import unittest
from resource_profile import plan,GiB,verify_rank_allocation
class ResourceTests(unittest.TestCase):
    def info(self,physical=64,logical=64,quota=64,memory=128):return {'physical_cores':physical,'logical_cpus':logical,'affinity_cpus':list(range(logical)),'usable_cpu_budget':quota,'memory_limit_bytes':memory*GiB,'memory_available_bytes':memory*GiB}
    def test_64core_hybrid_and_reserve(self):
        p=plan(self.info(),16,4,3);self.assertEqual(p['memory_budget_bytes'],112*GiB);self.assertEqual(p['worker_ranks'],15);self.assertEqual(p['environment']['OPENBLAS_NUM_THREADS'],'1');self.assertIn('slot:PE=4',p['argv'])
    def test_smt_must_be_explicit(self):
        with self.assertRaises(ValueError):plan(self.info(32,64),64,1,1)
        p=plan(self.info(32,64),64,1,1,logical=True);self.assertIn('--use-hwthread-cpus',p['argv']);self.assertEqual(p['environment']['OMP_PLACES'],'threads')
    def test_affinity_quota_and_memory(self):
        with self.assertRaises(ValueError):plan(self.info(quota=8),16,1,1)
        with self.assertRaises(ValueError):plan(self.info(memory=8),8,1,1)
        with self.assertRaises(ValueError):plan(self.info(),64,2,1)
        self.assertEqual(plan(self.info(quota=8,memory=8),4,2,1)['total_bound_slots'],8)
    def test_invalid_budget(self):
        for x in [float('nan'),float('inf'),0,-1]:
            with self.assertRaises(ValueError):plan(self.info(),2,1,x)
    def test_actual_rank_ids_checked_before_native(self):
        env={'BASS_HPC_ADMITTED_CPUS':'2,3,6,7','BASS_HPC_CPU_UNIT':'physical_core'}
        actual={'affinity_cpus':[2,3],'physical_cores':2,'logical_cpus':2}
        self.assertEqual(verify_rank_allocation(2,actual=actual,environ=env)['slots'],2)
        with self.assertRaises(ValueError):verify_rank_allocation(1,actual=actual,environ=env)
        actual['affinity_cpus']=[0,1]
        with self.assertRaises(ValueError):verify_rank_allocation(2,actual=actual,environ=env)
if __name__=='__main__':unittest.main()
