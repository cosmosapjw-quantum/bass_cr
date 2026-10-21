"""Small coordinator tests use artificial subprocesses; no ODE/native code."""
import copy
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess
from unittest.mock import patch
from types import SimpleNamespace

import scheduler as s


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.snap = {"host_fingerprint_sha256": "synthetic-host", "affinity_cpu_ids": list(range(64)),
            "cpu_quota": 64, "memory_limit_bytes": 128*s.GIB, "memory_available_bytes": 128*s.GIB}
        self.alloc = {"schema": "C21K_OWNER_ALLOCATION_V1", "owner_allocation_id": "test-only",
            "host_fingerprint_sha256": "synthetic-host", "cpu_ids": list(range(64)),
            "expires_at_utc": "2100-01-01T00:00:00Z", "per_job_rss_budget_bytes": 2*s.GIB,
            "coordinator_rss_budget_bytes": s.GIB}

    def test_protected_cpu_coordinator_and_reserve(self):
        c = s.admitted_capacity(self.snap, self.alloc)
        self.assertNotIn(55, c["cpu_ids"])
        self.assertEqual(c["memory_reserve_bytes"], 16*s.GIB)
        self.assertEqual(c["maximum_cpu_jobs"], 62)
        self.assertEqual(c["maximum_concurrent_jobs"], 55)

    def test_quota_counts_coordinator(self):
        self.snap["cpu_quota"] = 3.9
        self.assertEqual(s.admitted_capacity(self.snap,self.alloc)["maximum_concurrent_jobs"],2)
        self.snap["cpu_quota"] = 1.9
        with self.assertRaises(s.AdmissionError): s.admitted_capacity(self.snap,self.alloc)

    def test_low_memory_fails(self):
        self.snap.update(memory_limit_bytes=8*s.GIB,memory_available_bytes=s.GIB)
        with self.assertRaises(s.AdmissionError): s.admitted_capacity(self.snap,self.alloc)

    def test_stale_or_wrong_host_allocation_fails(self):
        self.alloc["expires_at_utc"] = "2000-01-01T00:00:00Z"
        with self.assertRaises(s.AdmissionError): s.admitted_capacity(self.snap,self.alloc)
        self.alloc["expires_at_utc"] = "2100-01-01T00:00:00Z"
        self.alloc["host_fingerprint_sha256"] = "different"
        with self.assertRaises(s.AdmissionError): s.admitted_capacity(self.snap,self.alloc)

    def test_cpu_ranges(self):
        self.assertEqual(s.cpu_set("0-2,5,8-9"),{0,1,2,5,8,9})

    def test_reused_pid_start_ticks_are_not_signalled(self):
        process=SimpleNamespace(pid=123,poll=lambda:0,wait=lambda timeout:0)
        task={'process':process,'token':'test-token','owned':{456:{'start_ticks':1,'state':'S'}}}
        with patch.object(s,'owned_processes',return_value={}), \
             patch.object(s,'process_identity',return_value={'start_ticks':2,'state':'S'}), \
             patch.object(s.os,'kill') as kill:
            result=s.stop_owned(task)
        self.assertEqual(result['forced_process_count'],0)
        kill.assert_not_called()


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cpus = sorted(os.sched_getaffinity(0) - {55})[:2]
        if len(self.cpus)<2: self.skipTest("bounded test requires two allowed CPU IDs")
        self.snapshot = {"observed_at_utc":s.utc(), "host_fingerprint_sha256":"synthetic-host",
            "affinity_cpu_ids":self.cpus,"cpu_quota":2,"memory_limit_bytes":8*s.GIB,
            "memory_available_bytes":8*s.GIB,"cgroup_observations":[]}
        self.allocation = {"schema":"C21K_OWNER_ALLOCATION_V1","owner_allocation_id":"test-only",
            "host_fingerprint_sha256":"synthetic-host","cpu_ids":self.cpus,
            "expires_at_utc":(datetime.now(timezone.utc)+timedelta(minutes=1)).isoformat(),
            "per_job_rss_budget_bytes":64*1024**2,"coordinator_rss_budget_bytes":64*1024**2,
            "lease_directory":str(self.root/'leases')}

    def tearDown(self): self.tmp.cleanup()

    def job(self,key="a",code=None):
        code = code or "import pathlib,json,sys,os; p=pathlib.Path(sys.argv[1]); p.mkdir(); (p/'result.json').write_text(json.dumps({'execution':'COMPLETE','threads':os.environ['OMP_NUM_THREADS'],'affinity':list(os.sched_getaffinity(0))}))"
        return {"job_id":key,"command":[sys.executable,"-c",code,"${job_out}"],
            "dependencies":[],"timeout_seconds":3,"result_receipt":"result.json",
            "success":[{"path":"execution","equals":"COMPLETE"}]}

    def manifest(self,jobs):
        return {"schema":"C21K_BOUNDED_CAMPAIGN_V1","binding_status":"BOUND",
            "source_identity":{"test":"synthetic-process-only"},"input_files":[],"jobs":jobs,
            "campaign_timeout_seconds":15,"maximum_raw_attempt_units":len(jobs)}

    def run_it(self,m,**kwargs):
        # This sandbox denies /proc/<child>/environ. Inject only the ownership
        # observer with test-created PIDs; subprocesses, signals and setsid are
        # real. Production admission must observe its own marker or refuse.
        original=s.subprocess.Popen; children={};gone=set()
        def create(*args,**kw):
            process=original(*args,**kw)
            token=kw.get('env',{}).get('BASS_C21K_ATTEMPT_TOKEN')
            if token:children[token]=(process,Path(args[0][-1]))
            return process
        def identity(pid):
            # The sandbox's /proc view is virtualized as well as environ-
            # restricted. Test-owned PID tokens stand in for kernel starttime;
            # the production /proc observer is a separate admission obligation.
            if pid in gone:raise FileNotFoundError(pid)
            direct=next((p for p,_ in children.values() if p.pid==pid),None)
            if direct is not None:
                if direct.poll() is not None:raise FileNotFoundError(pid)
            else:
                try:
                    reaped,_=os.waitpid(pid,os.WNOHANG)
                    if reaped:
                        gone.add(pid);raise FileNotFoundError(pid)
                except ChildProcessError:pass
                os.kill(pid,0)
            return {'start_ticks':pid*10,'state':'S','rss_bytes':1024*1024}
        def observe(token):
            if token not in children:return {}
            process,payload=children[token];result={}
            ids=[process.pid]
            child_file=payload/'child_pid'
            if child_file.is_file():ids.append(int(child_file.read_text()))
            for pid in ids:
                if pid==process.pid and process.poll() is not None:continue
                try:result[pid]=identity(pid)
                except (FileNotFoundError,ProcessLookupError):pass
            return result
        with patch.object(s,"resource_snapshot",return_value=self.snapshot), \
             patch.object(s,"verify_process_observation"), \
             patch.object(s,"process_identity",side_effect=identity), \
             patch.object(s,"owned_processes",side_effect=observe), \
             patch.object(s.subprocess,"Popen",side_effect=create):
            return s.run_campaign(m,self.allocation,self.root/'output',**kwargs)

    def test_complete_single_thread_affinity_and_resume(self):
        m=self.manifest([self.job()]); self.assertEqual(self.run_it(m),{'a':'COMPLETE'})
        p=self.root/'output/jobs/a/payload/result.json'; before=p.read_bytes()
        result=json.loads(before); self.assertEqual(result['threads'],'1')
        self.assertEqual(len(result['affinity']),1)
        self.assertEqual(self.run_it(m,resume=True),{'a':'COMPLETE'})
        self.assertEqual(p.read_bytes(),before)

    def test_failure_blocks_dependent_without_launch(self):
        a=self.job(code="raise SystemExit(7)"); b=self.job('b'); b['dependencies']=['a']
        self.assertEqual(self.run_it(self.manifest([a,b])),{'a':'FAILED','b':'BLOCKED'})
        self.assertFalse((self.root/'output/jobs/b').exists())

    def test_exit_zero_without_scientific_receipt_fails(self):
        self.assertEqual(self.run_it(self.manifest([self.job(code='pass')])),{'a':'FAILED'})

    def test_timeout_is_terminal_and_not_retried(self):
        a=self.job(code="import time; time.sleep(3)"); a['timeout_seconds']=.1
        m=self.manifest([a]); self.assertEqual(self.run_it(m),{'a':'TIMED_OUT'})
        self.assertEqual(self.run_it(m,resume=True),{'a':'TIMED_OUT'})

    def test_resume_payload_tamper_fails(self):
        m=self.manifest([self.job()]); self.run_it(m)
        (self.root/'output/jobs/a/payload/result.json').write_text('{}')
        with self.assertRaises(s.AdmissionError): self.run_it(m,resume=True)

    def test_create_only_and_manifest_change(self):
        m=self.manifest([self.job()]); self.run_it(m)
        with self.assertRaises(FileExistsError): self.run_it(m)
        m['source_identity']={'test':'changed'}
        with self.assertRaises(s.AdmissionError): self.run_it(m,resume=True)

    def test_interrupted_reservation_not_restarted(self):
        m=self.manifest([self.job()]); output=self.root/'output'; (output/'jobs/a').mkdir(parents=True)
        s.write_new(output/'CAMPAIGN_IDENTITY.json',{'manifest_sha256':s.digest(m)})
        self.assertEqual(self.run_it(m,resume=True),{'a':'INTERRUPTED'})

    def test_unbound_and_cycle_rejected(self):
        m=self.manifest([self.job()]); m['binding_status']='UNBOUND_NOT_EXECUTABLE'
        with self.assertRaises(s.AdmissionError): self.run_it(m)
        m['binding_status']='BOUND';m['jobs'][0]['dependencies']=['a']
        with self.assertRaises(s.AdmissionError):s.validate_manifest(m)

    def test_marker_capability_denial_is_not_native_admission(self):
        with patch.object(Path,'read_bytes',side_effect=PermissionError('synthetic deny')):
            with self.assertRaisesRegex(s.AdmissionError,'OBSERVATION_UNAVAILABLE'):
                s.verify_process_observation()

    def test_capability_runs_after_pin_and_failure_restores_affinity(self):
        before=os.sched_getaffinity(0)
        def denied():
            self.assertEqual(os.sched_getaffinity(0),{self.cpus[0]})
            raise s.AdmissionError('OWNED_PROCESS_OBSERVATION_UNAVAILABLE')
        with patch.object(s,'resource_snapshot',return_value=self.snapshot), \
             patch.object(s,'verify_process_observation',side_effect=denied):
            with self.assertRaises(s.AdmissionError):
                s.run_campaign(self.manifest([self.job()]),self.allocation,self.root/'output')
        self.assertEqual(os.sched_getaffinity(0),before)
        report=s.read_json(next((self.root/'output').glob('CAMPAIGN_RETURN_*.json')))
        self.assertEqual(report['statuses'],{'a':'NOT_RUN'})
        self.assertIn('OWNED_PROCESS_OBSERVATION_UNAVAILABLE',report['failure'])
        self.assertFalse((self.root/'output/jobs/a').exists())

    def test_readable_marker_without_production_tracker_is_rejected(self):
        marker=b'BASS_C21K_ATTEMPT_TOKEN=fixed-capability-test\0'
        with patch.object(s.secrets,'token_hex',return_value='fixed-capability-test'), \
             patch.object(Path,'read_bytes',return_value=marker), \
             patch.object(s,'process_identity',return_value={'start_ticks':1,'state':'S','rss_bytes':4096}), \
             patch.object(s,'owned_processes',return_value={}):
            with self.assertRaisesRegex(s.AdmissionError,'TRACKER_NOT_VERIFIED'):
                s.verify_process_observation()

    def test_changed_source_input_rejects_before_job_spawn(self):
        source=self.root/'source.py';source.write_text('original')
        m=self.manifest([self.job()])
        m['input_files']=[{'path':str(source),'record':s.file_record(source)}]
        source.write_text('changed')
        with self.assertRaisesRegex(s.AdmissionError,'INPUT_IDENTITY_CHANGED'):
            self.run_it(m)
        self.assertFalse((self.root/'output').exists())

    def test_g_hold_does_not_mean_twelve_complete(self):
        result={'status':'PARTIAL_OR_REFERENCE_HOLD','jobs':[{'status':'COMPLETE'}]*8,
                'refinement_execution':'NOT_RUN','reference_status':{'native_source':'HOLD'}}
        code="import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.mkdir(); (p/'result.json').write_text("+repr(json.dumps(result))+")"
        job=self.job(code=code);job['kind']='standalone_g_campaign'
        job['success']=[{'path':'status','one_of':['PARTIAL_OR_REFERENCE_HOLD','COMPLETED_BOUNDED_PILOT']}]
        self.assertEqual(self.run_it(self.manifest([job])),{'a':'SCOPED_HOLD'})
        receipt=s.read_json(self.root/'output/jobs/a/COORDINATOR_RECEIPT.json')
        self.assertEqual(receipt['scientific_summary']['conditional_history_jobs_not_run'],4)

    def test_setsid_grandchild_after_leader_exit_is_cleaned(self):
        unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)'])
        try:
            code="import pathlib,json,sys,subprocess; p=pathlib.Path(sys.argv[1]); p.mkdir(); c=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True); (p/'child_pid').write_text(str(c.pid)); (p/'result.json').write_text(json.dumps({'execution':'COMPLETE'}))"
            status=self.run_it(self.manifest([self.job(code=code)]))
            self.assertEqual(status,{'a':'FAILED'})
            pid=int((self.root/'output/jobs/a/payload/child_pid').read_text())
            self.assertFalse(Path('/proc',str(pid)).exists())
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate(); unrelated.wait()

    def test_timeout_cleans_setsid_grandchild(self):
        code="import pathlib,sys,subprocess,time; p=pathlib.Path(sys.argv[1]); p.mkdir(); c=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True); (p/'child_pid').write_text(str(c.pid)); time.sleep(10)"
        job=self.job(code=code);job['timeout_seconds']=.15
        self.assertEqual(self.run_it(self.manifest([job])),{'a':'TIMED_OUT'})
        pid=int((self.root/'output/jobs/a/payload/child_pid').read_text())
        self.assertFalse(Path('/proc',str(pid)).exists())

    def test_group_rss_budget_aborts(self):
        self.allocation['per_job_rss_budget_bytes']=1
        job=self.job(code='import time; time.sleep(10)')
        self.assertEqual(self.run_it(self.manifest([job])),{'a':'FAILED'})
        r=s.read_json(self.root/'output/jobs/a/COORDINATOR_RECEIPT.json')
        self.assertEqual(r['result_error'],'GROUP_RSS_BUDGET_EXCEEDED')

    def test_memory_reserved_before_children_grow(self):
        cpus=sorted(os.sched_getaffinity(0)-{55})[:4]
        if len(cpus)<4:self.skipTest('four allowed CPU IDs needed')
        self.snapshot.update(affinity_cpu_ids=cpus,cpu_quota=4,memory_limit_bytes=4*s.GIB,memory_available_bytes=4*s.GIB)
        self.allocation.update(cpu_ids=cpus,per_job_rss_budget_bytes=s.GIB)
        original=s.subprocess.Popen; observed=[];processes=[]
        def record(*args,**kwargs):
            p=original(*args,**kwargs);processes.append(p)
            observed.append(sum(x.poll() is None for x in processes));return p
        code="import pathlib,json,sys,time; time.sleep(.15); p=pathlib.Path(sys.argv[1]); p.mkdir(); (p/'result.json').write_text(json.dumps({'execution':'COMPLETE'}))"
        with patch.object(s.subprocess,'Popen',side_effect=record):
            result=self.run_it(self.manifest([self.job(str(i),code=code) for i in range(4)]))
        self.assertTrue(all(v=='COMPLETE' for v in result.values()))
        self.assertLessEqual(max(observed),2)


if __name__=='__main__': unittest.main(verbosity=2)
