"""Changed runtime seam and preserved resource guards; no science execution."""
import copy
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'runtime/r4ag/source'))
import resource_reader as reader
import runtime_contract as runtime
from common import ContractError


class RuntimePortTests(unittest.TestCase):
    def test_runtime_observes_actual_nonroot_process_not_fixed_mount_root(self):
        try:
            result=runtime.observe_environment()
        except ContractError as error:
            result=str(error)
        self.assertIsInstance(result,dict,'live v2 environment rejected by fixed-root reader')
        self.assertEqual(result['resource_hierarchy']['binding']['membership'],Path('/proc/self/cgroup').read_text().strip()[3:])
        self.assertTrue(result['resource_hierarchy']['raw_snapshot']['observation_after'])

    def test_changed_membership_namespace_or_mount_cannot_reuse_observation(self):
        original={'resource_hierarchy':{'binding':{'membership':'/jobs','namespaces':{'pid':'pid:[10]','cgroup':'cgroup:[20]','mnt':'mnt:[30]'},'mount':{'mount_id':'34','root':'/','mountpoint':'/cg'}}}}
        for part in ('membership','namespaces','mount'):
            changed=copy.deepcopy(original)
            if part=='membership':changed['resource_hierarchy']['binding'][part]='/other'
            elif part=='namespaces':changed['resource_hierarchy']['binding'][part]['cgroup']='cgroup:[99]'
            else:changed['resource_hierarchy']['binding'][part]['mountpoint']='/other'
            with self.subTest(part=part):
                with self.assertRaises(reader.ResourceError):reader.assert_same_hierarchy(original,changed)

    def test_changed_usage_and_timestamp_do_not_reuse_values(self):
        original={'resource_hierarchy':{'binding':{'membership':'/jobs'}}}
        changed=copy.deepcopy(original);changed['memory_available']=42;changed['observed_utc']='later'
        reader.assert_same_hierarchy(original,changed)

    def test_missing_binding_is_rejected(self):
        with self.assertRaises(reader.ResourceError):reader.assert_same_hierarchy({}, {})

    def test_three_worker_memory_and_coordinator_thresholds_unchanged(self):
        e={'affinity':[0,1,2,3],'quota':'4','memory_limit':3489660928,'memory_available':3489660928}
        p=runtime.choose_resources(e,3)
        self.assertEqual(p['memory_required'],3489660928)
        self.assertEqual(p['native_memory_bytes'],536870912)
        self.assertEqual(p['coordinator_and_reserve_bytes'],1879048192)
        self.assertEqual(p['coordinator_cpu_id'],3)
        self.assertEqual(p['parallel_nodes'],1)
        self.assertEqual(p['wall_seconds'],1800)
        for key,value in [('quota','399999/100000'),('affinity',[0,1,2]),('memory_available',3489660927)]:
            bad=copy.deepcopy(e);bad[key]=value
            with self.subTest(key=key):
                with self.assertRaises(ContractError):runtime.choose_resources(bad,3)
        e['affinity']=[0,1];e['quota']='2';e['memory_limit']=e['memory_available']=2415919104
        self.assertEqual(runtime.choose_resources(e,1)['memory_required'],2415919104)
        e['memory_available']-=1
        with self.assertRaises(ContractError):runtime.choose_resources(e,1)

if __name__=='__main__':unittest.main()
