"""Tiny nonphysical fixtures only: no operator import or scientific pilot."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock
import zipfile

NCP=Path(__file__).resolve().parents[1]/'ncp'
sys.path.insert(0,str(NCP))
import qualify_parallel as q
import run_and_collect as collector


def resources(cpus=64,bounded=128*q.GIB,available=110*q.GIB,disk=32*q.GIB,quota=None):
    return dict(capacity_established=True,effective_allowed_cpus=list(range(cpus)),cpu_quota=quota,
                bounded_memory_bytes=bounded,available_before_reserve_bytes=available,free_disk_bytes=disk)


def fixture(root):
    """Fake reviewed payload, explicit byte pins, no numerical source imports."""
    def save(name,text):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        return path
    source={name:save(name,'fake nonphysical source\n') for name in q.REQUIRED_SOURCE}
    inputs={name:save(name,'fake nonphysical input\n') for name in q.REQUIRED_INPUT}
    extra='fixture/original_dependency.bin';save(extra,'original decimal bytes\n')
    save(q.F_DEP_REL,json.dumps(dict(path_basis='repository-root',files={extra:q.file_identity(root/extra)})))
    input_name=q.H_REL+'/inputs/INPUT_IDENTITIES.json'
    input_path=save(input_name,json.dumps(dict(path_basis='repository-root',files={name:q.file_identity(path) for name,path in inputs.items()})))
    execution_name=q.H_REL+'/ncp/EXECUTION_SOURCE_MANIFEST.json'
    execution_path=save(execution_name,json.dumps(dict(path_basis='repository-root',files={
        **{name:q.file_identity(path) for name,path in source.items()},input_name:q.file_identity(input_path)})))
    review_name=q.H_REL+'/review/INDEPENDENT_REVIEW.json'
    review_path=save(review_name,json.dumps(dict(status='PASS_SCOPED',independent_of_implementation=True,
            ncp_preparation_admitted=True,unit=q.UNIT,execution_manifest_sha256=q.sha(execution_path))))
    ready=dict(status='NCP_READY',execution_manifest=dict(path=execution_name,**q.file_identity(execution_path)),
         input_manifest=dict(path=input_name,**q.file_identity(input_path)),
         independent_review=dict(path=review_name,**q.file_identity(review_path)))
    save(q.READY_REL,json.dumps(ready))
    return ready


class NCPQualificationTests(unittest.TestCase):
    def assertHold(self,code,action):
        with self.assertRaises(q.Hold) as caught:action()
        self.assertEqual(caught.exception.code,code)

    def test_actual_resource_admission_amended_64_slots_and_memory(self):
        admitted=q.admission(resources())
        self.assertEqual(admitted['workers_per_model'],29)
        self.assertEqual(admitted['peak_process_count'],64)
        self.assertEqual(admitted['total_fixed_cpu_slots'],6)
        self.assertEqual(admitted['total_fixed_support_memory_bytes'],64*2**20)
        self.assertEqual(admitted['total_fixed_wrapper_memory_bytes'],64*2**20)
        self.assertEqual(admitted['paired_candidate_working_bytes'],33*q.GIB+128*2**20)
        admitted63=q.admission(resources(cpus=63))
        self.assertEqual(admitted63['workers_per_model'],28)
        self.assertEqual(admitted63['peak_process_count'],62)
        self.assertEqual(admitted['reserve_bytes'],16*q.GIB)
        self.assertEqual(q.admission(resources(cpus=64,quota=16))['workers_per_model'],5)
        self.assertEqual(q.admission(resources(bounded=64*q.GIB,available=42*q.GIB))['workers_per_model'],21)
        self.assertHold('RESOURCE_ADMISSION_HOLD',lambda:q.admission(resources(cpus=8)))
        self.assertHold('RESOURCE_ADMISSION_HOLD',lambda:q.admission(resources(available=39*q.GIB)))
        self.assertHold('RESOURCE_ADMISSION_HOLD',lambda:q.admission(resources(disk=15*q.GIB)))
        self.assertHold('RESOURCE_MAPPING_HOLD',lambda:q.admission(dict(capacity_established=False,reason='unresolved mapping')))

    def test_plan_is_source_and_resource_only(self):
        observed=resources()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/q.H_REL/'ncp').mkdir(parents=True)
            (root/q.CONTRACT_REL).write_text('fake');(root/q.AMENDMENT_REL).write_text('fake amendment')
            (root/q.WRAPPER_AMENDMENT_REL).write_text('fake wrapper amendment')
            with mock.patch.object(q,'contract',return_value=dict(unit=q.UNIT)), \
                 mock.patch.object(q,'load_ops',return_value=SimpleNamespace(probe=lambda p:observed)), \
                 mock.patch.object(q,'bound_sources',return_value={'fake':True}), \
                 mock.patch.object(q.platform,'python_version',return_value='3.12.3'), \
                 mock.patch.object(q.importlib.metadata,'version',side_effect=lambda n:{'numpy':'2.4.2','scipy':'1.17.0'}[n]), \
                 mock.patch.object(q,'load_builder',side_effect=AssertionError('NO_NUMERICAL_IMPORT_ALLOWED')):
                result=q.plan(root,root)
            self.assertTrue(result['ready_for_execute'])
            self.assertEqual(result['call_counts']['G'],0)
            self.assertEqual(result['execution_status'],'NOT_EXECUTED')
            self.assertNotIn('parallel_operator',sys.modules)
            self.assertNotIn('numpy',sys.modules)
            with mock.patch.object(q,'contract',return_value=dict(unit=q.UNIT)), \
                 mock.patch.object(q,'load_ops',return_value=SimpleNamespace(probe=lambda p:observed)), \
                 mock.patch.object(q,'bound_sources',return_value={'verified':True}), \
                 mock.patch.object(q.platform,'python_version',return_value='0.0.0'), \
                 mock.patch.object(q.importlib.metadata,'version',side_effect=lambda n:{'numpy':'2.4.2','scipy':'1.17.0'}[n]):
                held=q.plan(root,root)
            self.assertEqual(held['runtime_version_observation']['status'],'RUNTIME_HOLD')
            self.assertEqual(held['source_binding'],{'verified':True})
            self.assertIn('RUNTIME_HOLD',[row['code'] for row in held['holds']])

    def test_missing_forged_review_and_source_amendment_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.assertHold('NCP_READY_MISSING',lambda:q.bound_sources(root))
            ready=fixture(root)
            bound=q.bound_sources(root)
            self.assertEqual(bound['independent_review']['sha256'],ready['independent_review']['sha256'])
            review=root/ready['independent_review']['path']
            review.write_text('{}')
            self.assertHold('SOURCE_IDENTITY_MISMATCH',lambda:q.bound_sources(root))
            ready=fixture(root)
            review=root/ready['independent_review']['path'];data=json.loads(review.read_text())
            data['independent_of_implementation']=False;review.write_text(json.dumps(data))
            ready['independent_review'].update(q.file_identity(review));(root/q.READY_REL).write_text(json.dumps(ready))
            self.assertHold('INDEPENDENT_NCP_REVIEW_HOLD',lambda:q.bound_sources(root))
            ready=fixture(root)
            (root/q.AMENDMENT_REL).write_text('mutated amendment')
            self.assertHold('SOURCE_IDENTITY_MISMATCH',lambda:q.bound_sources(root))
            ready=fixture(root)
            (root/q.WRAPPER_AMENDMENT_REL).write_text('mutated wrapper accounting amendment')
            self.assertHold('SOURCE_IDENTITY_MISMATCH',lambda:q.bound_sources(root))

    def test_review_alternate_name_requires_pinned_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);ready=fixture(root)
            alt=root/'alternate/review.json';alt.parent.mkdir();alt.write_bytes((root/ready['independent_review']['path']).read_bytes())
            self.assertEqual(q.bound_sources(root,review_override='alternate/review.json')['independent_review']['sha256'],ready['independent_review']['sha256'])
            alt.write_text('{}')
            self.assertHold('SOURCE_IDENTITY_MISMATCH',lambda:q.bound_sources(root,review_override='alternate/review.json'))

    def test_shared_durable_budget_no_reset_or_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);budget=q.Budget(root)
            for index in range(8):budget.reserve('fake_'+str(index))
            self.assertEqual(sum(r['columns_reserved'] for r in q.Budget(root).rows()),76800)
            self.assertHold('CUMULATIVE_BUDGET_EXHAUSTED',lambda:q.Budget(root).reserve('fake_ninth'))
            self.assertHold('DUPLICATE_LOGICAL_BUILD',lambda:q.Budget(root).reserve('fake_0'))
            # A separate budget fixture discriminates column exhaustion before
            # the build count is exhausted.
            other=root/'other';other.mkdir();q.Budget(other,max_columns=9600).reserve('one')
            self.assertHold('CUMULATIVE_BUDGET_EXHAUSTED',lambda:q.Budget(other,max_columns=9600).reserve('two'))

    def test_injected_worker_failure_timeout_and_owned_group_cleanup(self):
        processes=[]
        try:
            sleeper=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
            failure=subprocess.Popen([sys.executable,'-c','raise SystemExit(7)'],start_new_session=True)
            processes=[sleeper,failure]
            self.assertHold('LANE_FIRST_FAILURE',lambda:q.wait_lanes(processes,time.monotonic()+5,lambda:None))
            q.cleanup_groups(processes)
            self.assertIsNotNone(sleeper.poll())
            timeout=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
            processes.append(timeout)
            self.assertHold('WHOLE_COMMAND_TIMEOUT',lambda:q.wait_lanes([timeout],time.monotonic()+.05,lambda:None))
            q.cleanup_groups([timeout]);self.assertIsNotNone(timeout.poll())
        finally:q.cleanup_groups(processes)

    def test_injected_eight_build_schedule_fresh_runs_and_accounting(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'fresh_run'
            (root/q.H_REL/'ncp').mkdir(parents=True)
            (root/q.CONTRACT_REL).write_text('fake contract');(root/q.AMENDMENT_REL).write_text('fake amendment')
            (root/q.WRAPPER_AMENDMENT_REL).write_text('fake wrapper amendment')
            commands=[]
            class FakeWorker:
                counter=200000
                def __init__(self,command,**kwargs):
                    commands.append(command);self.pid=FakeWorker.counter;FakeWorker.counter+=1;self.returncode=0
                    if '--lane' in command:
                        job=command[command.index('--job')+1];kind=command[command.index('--kind')+1]
                        directory=run/job;directory.mkdir()
                        q.write_new(directory/'DONE.json',dict(job=job,kind=kind,columns_completed=9600,
                            build_and_persist_wall_s=2 if kind=='serial' else 3))
                def poll(self):return self.returncode
                def wait(self,timeout=None):return self.returncode
            binding={'ready_path':q.READY_REL,'independent_review':{'path':'fake_review'}}
            with mock.patch.object(q,'contract',return_value={}), \
                 mock.patch.object(q,'bound_sources',return_value=binding), \
                 mock.patch.object(q,'require_wrapper',return_value=dict(parent_pid=None)), \
                 mock.patch.object(q,'load_ops',return_value=SimpleNamespace(probe=lambda p:resources())), \
                 mock.patch.object(q.platform,'python_version',return_value='3.12.3'), \
                 mock.patch.object(q.importlib.metadata,'version',side_effect=lambda n:{'numpy':'2.4.2','scipy':'1.17.0'}[n]), \
                 mock.patch.object(q.subprocess,'Popen',side_effect=FakeWorker), \
                 mock.patch.object(q,'historical_comparisons',return_value={'acceptance_gate':False}), \
                 mock.patch.object(q,'cleanup_groups'), \
                 mock.patch.object(q,'process_measurements',return_value=[]):
                result=q.execute(root,run)
            self.assertEqual(result['actual_exit'],0)
            self.assertEqual(result['counts']['logical_G_reserved'],8)
            self.assertEqual(result['counts']['columns_completed'],76800)
            self.assertEqual(result['performance']['legacy']['status'],'PERFORMANCE_NOT_IMPROVED')
            lanes=[c for c in commands if '--lane' in c]
            self.assertEqual([c[c.index('--kind')+1] for c in lanes],['serial','serial','candidate','candidate']*2)
            self.assertTrue(all(c[c.index('--workers')+1]=='29' for c in lanes))
            self.assertEqual(len([c for c in commands if '--compare' in c]),6)
            start=json.loads((run/'START.json').read_text())
            self.assertEqual(start['process_inventory']['maximum_reserved_slots'],64)
            self.assertEqual(start['process_inventory']['wrapper_watchdog'],1)
            self.assertHold('RUN_MUST_BE_FRESH_ABSOLUTE_OUTSIDE_SOURCE',lambda:q.execute(root,root/'bad'))

    def test_wrapper_child_environment_identifies_only_actual_watchdog_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'new_run';out=base/'return'
            captured={}
            class FakeQualifier:
                returncode=0;pid=250000
                def __init__(self,command,**kwargs):
                    captured.update(kwargs);run.mkdir()
                def poll(self):return 0
            with mock.patch.object(collector.subprocess,'Popen',side_effect=FakeQualifier), \
                 mock.patch.object(collector,'collect',return_value={'status':'FAKE_NONPHYSICAL_COLLECTION'}):
                result=collector.execute_and_collect(root,run,out)
            self.assertEqual(captured['env']['CR_PHYS02H_WRAPPER_PID'],str(os.getpid()))
            self.assertTrue(captured['start_new_session'])
            self.assertEqual(result['actual_exit'],0)

    def test_direct_execution_requires_verified_watchdog_route(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'new_run'
            with mock.patch.dict(os.environ,{},clear=True):
                self.assertHold('VERIFIED_WRAPPER_REQUIRED',lambda:q.require_wrapper(root,run))
            values=dict(CR_PHYS02H_WRAPPER_PID=str(os.getppid()),CR_PHYS02H_LAUNCH_NONCE='a'*32,
                        CR_PHYS02H_RUN_MARKER=str(run.resolve()))
            with mock.patch.dict(os.environ,values):
                self.assertHold('WRAPPER_PARENT_IDENTITY_HOLD',lambda:q.require_wrapper(root,run))

    def test_malformed_control_files_do_not_block_raw_collection(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            for scenario in ('START','READY','fallback_manifest'):
                root=base/scenario/'source';root.mkdir(parents=True)
                run=base/scenario/'run';run.mkdir();out=base/scenario/'return'
                (run/'data.npy').write_bytes(b'tiny_nonphysical_raw_values\x00\xff')
                ready=root/q.READY_REL;ready.parent.mkdir(parents=True)
                start=run/'START.json';start.write_text('{bad START' if scenario=='START' else '{}')
                if scenario=='READY':ready.write_text('{bad READY')
                elif scenario=='fallback_manifest':
                    bad=root/'inputs/malformed_manifest.json';bad.parent.mkdir();bad.write_text('{bad manifest')
                    ready.write_text(json.dumps(dict(input_manifest=dict(path='inputs/malformed_manifest.json',**q.file_identity(bad)))))
                else:ready.write_text('{}')
                returned=collector.collect(root,run,out)
                self.assertTrue(returned['collection_warnings'])
                with zipfile.ZipFile(returned['archive']) as bundle:
                    self.assertEqual(bundle.read('run/data.npy'),b'tiny_nonphysical_raw_values\x00\xff')
                    self.assertEqual(bundle.read('run/START.json'),start.read_bytes())
                    self.assertEqual(bundle.read('source/'+q.READY_REL),ready.read_bytes())
                    if scenario=='fallback_manifest':self.assertEqual(bundle.read('source/inputs/malformed_manifest.json'),bad.read_bytes())
                    manifest=json.loads(bundle.read('RETURN_MANIFEST.json'))
                    self.assertEqual(manifest['source_binding_status'],'COLLECTION_DOES_NOT_ATTEST_SOURCE_ADMISSION')

    def test_dead_qualifier_orphans_malformed_event_and_unregistered_comparator(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'new_run';out=base/'return'
            path=root/q.H_REL/'ncp/qualify_parallel.py';path.parent.mkdir(parents=True)
            # This is an injected nonphysical qualifier. Two sleep-only sessions
            # emulate a model lane and a comparator/event-append death race.
            script='''import json,os,pathlib,subprocess,sys,signal
run=pathlib.Path(sys.argv[sys.argv.index('--run')+1]);run.mkdir()
(run/'data.npy').write_bytes(b'NONPHYSICAL_RAW\\x00\\xff')
(run/'START.json').write_text('{malformed START')
children=[subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True) for _ in range(2)]
(run/'CHILDREN.json').write_text(json.dumps([p.pid for p in children]))
stat=pathlib.Path('/proc/self/stat').read_text();ticks=int(stat[stat.rfind(')')+2:].split()[19])
event={'process_group':children[0].pid,'ownership':{'qualifier_pid':os.getpid(),'qualifier_start_ticks':ticks,'uid':os.getuid(),'run_directory':str(run.resolve()),'launch_nonce':os.environ['CR_PHYS02H_LAUNCH_NONCE']}}
(run/'PROCESS_EVENTS.jsonl').write_text('{bad first line\\n'+json.dumps(event)+'\\n')
os.kill(os.getpid(),signal.SIGKILL)
'''
            path.write_text(script)
            ready=root/q.READY_REL;ready.write_text('{malformed READY')
            environment=os.environ.copy();environment.pop('CR_PHYS02H_LAUNCH_NONCE',None);environment.pop('CR_PHYS02H_RUN_MARKER',None)
            unrelated=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True,env=environment)
            try:
                returned=collector.execute_and_collect(root,run,out)
                self.assertEqual(returned['actual_exit'],-9)
                self.assertIsNone(unrelated.poll())
                children=json.loads((run/'CHILDREN.json').read_text())
                cleanup=json.loads(next(out.glob('LAUNCH_*/OWNED_GROUP_CLEANUP.json')).read_text())
                signaled={s['process_group'] for item in cleanup['records'] for s in item['signaled']}
                self.assertTrue(set(children).issubset(signaled))
                warnings=[w['code'] for item in cleanup['records'] for w in item['warnings']]
                self.assertIn('MALFORMED_PROCESS_EVENT_JSON',warnings)
                self.assertIn('OWNED_SESSION_DISCOVERED_WITHOUT_DURABLE_EVENT',warnings)
                for pid in children:
                    status=Path('/proc')/str(pid)/'status'
                    if status.exists():self.assertIn('Z',next(line for line in status.read_text().splitlines() if line.startswith('State:')))
                with zipfile.ZipFile(returned['return_bundle']['archive']) as bundle:
                    self.assertEqual(bundle.read('run/data.npy'),b'NONPHYSICAL_RAW\x00\xff')
                    self.assertEqual(bundle.read('run/PROCESS_EVENTS.jsonl'),(run/'PROCESS_EVENTS.jsonl').read_bytes())
            finally:q.cleanup_groups([unrelated])

    def test_watchdog_cancels_science_before_unresponsive_root_grace(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'new_run';out=base/'return'
            path=root/q.H_REL/'ncp/qualify_parallel.py';path.parent.mkdir(parents=True)
            path.write_text('''import json,os,pathlib,signal,subprocess,sys,time
signal.signal(signal.SIGTERM,signal.SIG_IGN)
run=pathlib.Path(sys.argv[sys.argv.index('--run')+1]);run.mkdir()
child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'],start_new_session=True)
(run/'CHILDREN.json').write_text(json.dumps([child.pid]))
(run/'data.npy').write_bytes(b'NONPHYSICAL_TIMEOUT_RAW')
time.sleep(30)
''')
            real_clock=time.monotonic;real_popen=subprocess.Popen;checked=[];launched=[]
            def clock():return real_clock()+(901 if (run/'CHILDREN.json').exists() else 0)
            def launch(command,**kwargs):
                process=real_popen(command,**kwargs);launched.append(process);original_wait=process.wait
                def wait(timeout=None):
                    if timeout==8:
                        pid=json.loads((run/'CHILDREN.json').read_text())[0]
                        status=Path('/proc')/str(pid)/'status';until=real_clock()+1
                        while status.exists() and real_clock()<until:
                            state=next(line for line in status.read_text().splitlines() if line.startswith('State:'))
                            if 'Z' in state:break
                            time.sleep(.01)
                        if status.exists():self.assertIn('Z',state)
                        checked.append('science_stopped_before_root_grace')
                        raise subprocess.TimeoutExpired(command,8)
                    return original_wait(timeout)
                process.wait=wait;return process
            try:
                with mock.patch.object(collector.time,'monotonic',side_effect=clock), \
                     mock.patch.object(collector.subprocess,'Popen',side_effect=launch):
                    returned=collector.execute_and_collect(root,run,out)
                self.assertTrue(returned['watchdog_timeout'])
                self.assertEqual(checked,['science_stopped_before_root_grace'])
                self.assertIsNotNone(launched[0].poll())
                self.assertEqual(returned['return_bundle']['raw_value_files'],1)
            finally:
                for process in launched:
                    if process.poll() is None:process.kill();process.wait(timeout=2)

    def test_all_new_sessions_receive_ownership_events(self):
        with tempfile.TemporaryDirectory() as temp:
            run=Path(temp);nonce='b'*32
            process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
            try:
                with mock.patch.dict(os.environ,dict(CR_PHYS02H_LAUNCH_NONCE=nonce)):
                    q.register_session(run,process,'compare_fake','nonphysical fixture command')
                event=json.loads((run/'PROCESS_EVENTS.jsonl').read_text())
                self.assertEqual(event['kernel_identity']['session_id'],process.pid)
                self.assertEqual(event['ownership']['qualifier_pid'],os.getpid())
                self.assertEqual(event['ownership']['launch_nonce'],nonce)
            finally:q.cleanup_groups([process])

    def test_historical_difference_informational_only(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'run';run.mkdir()
            source=root/'historical/source.json';source.parent.mkdir();source.write_text('original historical metadata')
            old=dict(raw_sha256='old_data_bytes',dtype='<f8',shape=[3])
            record=dict(label='original_F_reference_fullBED',model='fullBED',
                        source=dict(path='historical/source.json',**q.file_identity(source)),arrays=dict(data=old))
            path=root/q.HISTORICAL_REL;path.parent.mkdir(parents=True);path.write_text(json.dumps(dict(records=[record])))
            raw=run/'fullBED_rep1_serial/raw';raw.mkdir(parents=True)
            q.write_new(raw/'SIDECAR.json',dict(arrays=dict(data=dict(raw_sha256='different_fresh_bytes',dtype='<f8',shape=[3]))))
            comparisons=q.historical_comparisons(root,run)
            self.assertFalse(comparisons['acceptance_gate'])
            self.assertFalse(comparisons['original_pulse_or_source_approval_adopted'])
            self.assertFalse(comparisons['records'][0]['comparisons']['data']['exactly_equal'])
            self.assertEqual(comparisons['records'][0]['status'],'INFORMATIONAL_ONLY')
            self.assertEqual(comparisons['records'][1]['status'],'NO_COMPLETE_FRESH_SIDECAR')

    def test_cleanup_includes_orphaned_worker_grandchild(self):
        child=None;grandchild=None
        try:
            code='import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"]); print(p.pid,flush=True); raise SystemExit(7)'
            child=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,text=True,start_new_session=True)
            grandchild=int(child.stdout.readline().strip());child.wait(timeout=3)
            q.cleanup_groups([child])
            status=Path('/proc')/str(grandchild)/'status'
            until=time.monotonic()+1
            while status.exists() and time.monotonic()<until:
                state=next(line for line in status.read_text().splitlines() if line.startswith('State:'))
                if 'Z' in state:break
                time.sleep(.01)
            if status.exists():
                state=next(line for line in status.read_text().splitlines() if line.startswith('State:'))
                self.assertIn('Z',state)  # dead orphan waiting for host reaper
        finally:
            if child is not None:
                q.cleanup_groups([child])
                if child.stdout is not None:child.stdout.close()
            if grandchild is not None:
                try:os.kill(grandchild,9)
                except ProcessLookupError:pass

    def test_failed_partial_counts_and_collection_contains_values_after_deadline(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();run=base/'failed_run';run.mkdir();out=base/'return'
            fixture(root);binding=q.bound_sources(root)
            q.write_new(run/'START.json',dict(source_binding=binding,deadline_monotonic=time.monotonic()-900))
            q.Budget(run).reserve('fake_partial')
            tile=run/'fake_partial/tiles/tile_000';tile.mkdir(parents=True)
            # Nonphysical tiny binary value payload; collector must include its
            # actual bytes even without complete sidecar / terminal build record.
            values=b'FAKE-NPY-RAW-VALUES\x00\x01\xff';(tile/'data.npy').write_bytes(values)
            q.write_new(tile/'TILE_DONE.json',dict(columns_completed=[0,1,2]))
            q.write_new(run/'FIRST_FAILURE.json',dict(error='injected timeout'))
            counts=q.counts(run)
            self.assertEqual(counts['logical_G_completed'],0)
            self.assertEqual(counts['partial_builds'][0]['durably_completed_columns'],3)
            returned=collector.collect(root,run,out)
            self.assertEqual(returned['status'],'COMPLETE_OBSERVED_PAYLOAD')
            self.assertEqual(returned['raw_value_files'],1)
            with zipfile.ZipFile(returned['archive']) as bundle:
                self.assertEqual(bundle.read('run/fake_partial/tiles/tile_000/data.npy'),values)
                self.assertIn('source/fixture/original_dependency.bin',bundle.namelist())
                manifest=json.loads(bundle.read('RETURN_MANIFEST.json'))
                self.assertFalse(manifest['science_deadline_extended'])

    def test_resource_loss_detected(self):
        admitted=q.admission(resources())
        self.assertHold('RESOURCE_ADMISSION_LOST',lambda:q.monitor_check(resources(quota=32),admitted,set()))
        self.assertHold('RESOURCE_ADMISSION_LOST',lambda:q.monitor_check(resources(available=15*q.GIB),admitted,set()))


if __name__=='__main__':unittest.main(verbosity=2)
