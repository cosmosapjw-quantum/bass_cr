"""Synthetic R4Y scheduling/identity tests; no archived physical operator calls."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import runner as r

def info():
    return {'usable_cpu_budget':8,'affinity_cpus':list(range(8)),
            'memory_limit_bytes':8*r.GiB,'memory_available_bytes':8*r.GiB}

def task(q=40,**extra):
    return {'order':q,'subdivisions':1,'moment_backend':'fortran','radial_backend':'fortran',**extra}

def fixture(n=4):
    tasks=r.validate_tasks([task(q=q) for q in (40,48,56,64)[:n]])
    c={'context_id':'context','resources':r.admit_resources(3,info()),'input_pins':{},'source_pins':{},
       'timeout_seconds_per_attempt':1800,'screens':r.SCREENS}
    m={'context_id':'context','manifest_id':'manifest','tasks':tasks}
    return c,m

class RunnerTests(unittest.TestCase):
    def test_exact_resolution_task_domain_and_unique_semantics(self):
        self.assertEqual(r.validate_tasks([task()])[0]['inner_phase_budget'],None)
        for bad in (task(q=True),task(q=24),task(subdivisions=3),task(moment_backend='auto'),
                    task(inner_phase_budget=7),task(subdivisions=2,inner_phase_budget=6)):
            with self.assertRaises(ValueError):r.validate_tasks([bad])
        with self.assertRaises(ValueError):r.validate_tasks([task(),task(inner_phase_budget=None)])
        tasks=r.validate_tasks([task(),task(inner_phase_budget=6)])
        self.assertNotEqual(tasks[0]['task_id'],tasks[1]['task_id'])

    def test_resource_cpu_disjointness_and_headroom(self):
        a=r.admit_resources(3,info())
        self.assertEqual(a['worker_cpu_sets'],[[0,1],[2,3],[4,5]])
        self.assertEqual(a['coordinator_cpu_id'],6)
        for workers,census in ((4,info()),(3,{**info(),'usable_cpu_budget':6}),
                              (3,{**info(),'memory_available_bytes':4*r.GiB})):
            with self.assertRaises(ValueError):r.admit_resources(workers,census)

    def test_duplicate_json_atomic_create_only_and_safe_batch_name(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.json';p.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError):r.read_json(p)
            with self.assertRaises(FileExistsError):r.write_json(p,{'safe':True})
            self.assertEqual(p.read_text(),'{"x":1,"x":2}')
            for name in ('../outside','a/b','', 'a'*65):
                with self.assertRaises(ValueError):r.batch_path(Path(d),name)

    def test_raw_metric_uses_both_norms_and_all_six_blocks(self):
        a={k:np.ones((2,2),complex) for k in r.RAW_KEYS}
        b={k:np.ones((2,2),complex) for k in r.RAW_KEYS};b['D_pt']*=2
        maximum,detail=r._raw_difference(a,b)
        self.assertEqual(maximum,.5);self.assertEqual(detail['D_pt'],.5)
        self.assertEqual(len(detail),6)

    def test_central_control_observes_without_projection(self):
        d=np.zeros((9,9),complex);d[1,1]=2e-12j;before=d.copy()
        control=r.central_s_control({'D_tp':d})
        self.assertFalse(control['pass']);self.assertEqual(control['maximum_absolute'],2e-12)
        self.assertTrue(np.array_equal(d,before))

    def test_counting_wrappers_preserve_calls_and_results(self):
        class K:
            backend_identity='fixture';receipt={};threads=2;backend='fortran'
            def accumulate(self,*args,**kw): return args[0]
        a=np.ones((5,4));k=r.CountingMoment(K())
        self.assertIs(k.accumulate(a,real_coefficients=True),a)
        self.assertEqual(k.evidence()['radial_pairs'],5)
        self.assertFalse(k.evidence()['actual_openmp_team_observed'])
        class N:
            last_observed_threads=1
            def evaluate(self,*args):return args[2],args[3]
        n=r.CountingRadial(N());cells=np.zeros(5,int);s=np.ones(5);h=np.ones(5)
        result=n.evaluate(None,cells,s,h,1)
        self.assertIs(result[0],s);self.assertIs(result[1],h)
        self.assertEqual(n.evidence()['observed_openmp_team_sizes'],[1])

    def test_durable_global_budget_rejects_gaps_and_duplicate_tasks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c,m=fixture()
            rec={'context_id':c['context_id'],'global_attempt':1,'task':m['tasks'][0]}
            r.write_json(p/'reservations'/'001.json',rec)
            self.assertEqual(len(r.reservations(p,c)),1)
            r.write_json(p/'reservations'/'003.json',{**rec,'global_attempt':3})
            with self.assertRaises(ValueError):r.reservations(p,c)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for i in (1,2):r.write_json(p/'reservations'/f'{i:03}.json',{**rec,'global_attempt':i})
            with self.assertRaises(ValueError):r.reservations(p,c)

    def run_fixture(self,d,c,m,starter,**extra):
        dest=Path(d)/'batches'/'fixture';dest.mkdir(parents=True)
        with patch.object(r,'load_context',return_value=(Path(d),c)), \
             patch.object(r,'load_batch',return_value=(dest,m)), \
             patch.object(r,'census',return_value=info()), \
             patch.object(r.os,'sched_getaffinity',return_value={7}), \
             patch.object(r.os,'sched_setaffinity'), \
             patch.object(r.subprocess,'Popen',side_effect=starter), \
             patch.object(r.os,'killpg') as kill:
            with self.assertRaises(extra.get('error',RuntimeError)):
                r.execute(d,'context_sha','fixture','manifest_sha')
        return dest,kill

    def test_popen_failure_consumes_global_reservation_closes_log(self):
        c,m=fixture();logs=[]
        with tempfile.TemporaryDirectory() as d:
            def start(*args,**kw):
                logs.append(kw['stdout'])
                self.assertTrue((Path(d)/'reservations'/'001.json').exists())
                raise OSError('simulated launch failure')
            dest,kill=self.run_fixture(d,c,m,start,error=OSError)
            rec=r.read_json(dest/'FAILED.json')
            self.assertEqual(rec['global_reserved_attempts'],1)
            self.assertEqual(rec['reserved_attempts_this_batch'],1)
            self.assertTrue(logs[0].closed);kill.assert_not_called()

    def test_worker_failure_cancels_and_reaps_owned_peers_no_retry(self):
        c,m=fixture();procs=[]
        class Proc:
            def __init__(self,index):self.pid=90000+index;self.code=1 if index==0 else None
            def poll(self):return self.code
            def wait(self,timeout):self.code=-15;return self.code
        with tempfile.TemporaryDirectory() as d:
            def start(argv,**kw):
                proc=Proc(int(argv[argv.index('--index')+1]));procs.append(proc);return proc
            dest,kill=self.run_fixture(d,c,m,start)
            self.assertEqual(len(procs),3);self.assertEqual(kill.call_count,2)
            self.assertTrue(all(x.poll() is not None for x in procs))
            rec=r.read_json(dest/'FAILED.json')
            self.assertEqual(rec['global_reserved_attempts'],3);self.assertTrue(rec['no_retry'])

    def test_timeout_cancels_all_launched_workers(self):
        c,m=fixture();c['timeout_seconds_per_attempt']=-1;procs=[]
        class Proc:
            def __init__(self):self.pid=91000+len(procs);self.code=None
            def poll(self):return self.code
            def wait(self,timeout):self.code=-15;return self.code
        with tempfile.TemporaryDirectory() as d:
            def start(*args,**kw):proc=Proc();procs.append(proc);return proc
            dest,kill=self.run_fixture(d,c,m,start,error=TimeoutError)
            self.assertEqual(kill.call_count,3)
            self.assertTrue(all(x.poll() is not None for x in procs))
            self.assertEqual(r.read_json(dest/'FAILED.json')['exception'],'TimeoutError')

    def test_previous_batch_consumption_blocks_retry_before_new_calls(self):
        c,m=fixture(1)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dest=root/'batches'/'again';dest.mkdir(parents=True)
            r.write_json(root/'reservations'/'001.json',{'context_id':'context','global_attempt':1,'task':m['tasks'][0]})
            with patch.object(r,'load_context',return_value=(root,c)), \
                 patch.object(r,'load_batch',return_value=(dest,m)), \
                 patch.object(r.os,'sched_setaffinity'), \
                 patch.object(r.subprocess,'Popen') as start:
                with self.assertRaisesRegex(ValueError,'already reserved'):r.execute(root,'sha','again','sha')
            start.assert_not_called();self.assertFalse((dest/'STARTED.json').exists())

    def test_twenty_four_global_reservations_block_fresh_task(self):
        c,m=fixture(1)
        historical=[]
        for q,s in r.GRID:
            for mb,rb in (('reference','python'),('reference','fortran'),('fortran','python')):
                historical.append(task(q=q,subdivisions=s,moment_backend=mb,radial_backend=rb))
        historical=r.validate_tasks(historical[:24])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dest=root/'batches'/'overflow';dest.mkdir(parents=True)
            for i,t in enumerate(historical,1):
                r.write_json(root/'reservations'/f'{i:03}.json',{'context_id':'context','global_attempt':i,'task':t})
            with patch.object(r,'load_context',return_value=(root,c)), \
                 patch.object(r,'load_batch',return_value=(dest,m)), \
                 patch.object(r.os,'sched_setaffinity'), \
                 patch.object(r.subprocess,'Popen') as start:
                with self.assertRaisesRegex(ValueError,'cap would be exceeded'):r.execute(root,'sha','overflow','sha')
            start.assert_not_called();self.assertFalse((dest/'STARTED.json').exists())

if __name__=='__main__':unittest.main()
