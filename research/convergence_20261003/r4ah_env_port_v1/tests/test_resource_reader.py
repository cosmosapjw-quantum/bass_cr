"""Behavioral resource admission regressions, using observations only as tests.

Production defects: fixed-root reads, omitted ancestor limits, hidden hierarchy
acceptance, missing-current defaults, and malformed/ambiguous mapping acceptance.
No fixture is passed to a production prepare or authorization command.
"""
import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1]/'runtime/r4ag/source/resource_reader.py'
spec = importlib.util.spec_from_file_location('resource_reader', SOURCE)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
GiB = 1024**3


def sample(member='/user/jobs', mountpoint='/sys/fs/cgroup', mountroot='/'):
    ns = {'pid':'pid:[10]', 'cgroup':'cgroup:[20]', 'mnt':'mnt:[30]'}
    s = {
        'membership':'0::'+member+'\n',
        'mountinfo':f'34 25 0:29 {mountroot} {mountpoint} rw shared:9 - cgroup2 cgroup2 rw\n',
        'meminfo':'MemTotal: 16777216 kB\nMemAvailable: 12582912 kB\n',
        'affinity':list(range(8)),
        'namespaces':{'self':dict(ns), '1':dict(ns), '2':dict(ns)},
        'kernel2_comm':'kthreadd\n',
        'kernel2_status':'Name:\tkthreadd\nPid:\t2\nPPid:\t0\nNSpid:\t2\nKthread:\t1\n',
        'kernel2_membership':'0::/\n',
        'observed_utc':'2026-10-03T00:00:00Z',
        'files':{},
    }
    # These are literal public proc/cgroup file observations, not reader output.
    root = Path(mountpoint.replace('\\040',' '))
    s['files'][str(root/'cgroup.controllers')] = 'cpu memory pids\n'
    leaf = root/member.lstrip('/')
    for d in (leaf, *leaf.parents):
        if not d.is_relative_to(root) or d == root:
            break
        for name, text in [('cpu.max','max 100000\n'), ('memory.max','max\n'), ('memory.current',str(GiB)+'\n')]:
            s['files'][str(d/name)] = text
    return s


class ResourceReaderTests(unittest.TestCase):
    def test_actual_nonroot_with_root_limit_files_absent_is_observable(self):
        try:
            value = reader.evaluate_snapshot(sample())
        except reader.ResourceError as error:
            value = str(error)
        self.assertIsInstance(value, dict, 'valid non-root v2 hierarchy was rejected')
        self.assertEqual(value['memory_available'], 12*GiB)
        self.assertEqual(value['quota'], 'unlimited')

    def test_parent_quota_and_paired_parent_usage_restrict_leaf(self):
        s = sample()
        s['files']['/sys/fs/cgroup/user/jobs/cpu.max'] = '600000 100000\n'
        s['files']['/sys/fs/cgroup/user/cpu.max'] = '250000 100000\n'
        s['files']['/sys/fs/cgroup/user/jobs/memory.max'] = str(10*GiB)
        s['files']['/sys/fs/cgroup/user/jobs/memory.current'] = str(GiB)
        s['files']['/sys/fs/cgroup/user/memory.max'] = str(4*GiB)
        s['files']['/sys/fs/cgroup/user/memory.current'] = str(3*GiB)
        result = reader.evaluate_snapshot(s)
        self.assertEqual(result['quota'], '5/2')
        self.assertEqual(result['memory_limit'], 4*GiB)
        self.assertEqual(result['memory_available'], GiB)
        self.assertEqual(result['effective_cpu_capacity'], '5/2')

    def test_host_available_and_affinity_remain_upper_limits(self):
        s = sample()
        s['affinity'] = [0,2]
        s['files']['/sys/fs/cgroup/user/cpu.max'] = '600000 100000'
        s['meminfo'] = 'MemTotal: 16777216 kB\nMemAvailable: 1048576 kB\n'
        result = reader.evaluate_snapshot(s)
        self.assertEqual(result['effective_cpu_capacity'], '2')
        self.assertEqual(result['memory_available'], GiB)

    def test_alternate_mountpoint(self):
        s = sample(mountpoint='/accounting')
        result = reader.evaluate_snapshot(s)
        self.assertEqual(result['resource_hierarchy']['leaf'], '/accounting/user/jobs')
        self.assertEqual(result['memory_available'], 12*GiB)

    def test_escaped_mountpoint(self):
        s = sample(mountpoint='/accounting\\040space')
        self.assertEqual(reader.evaluate_snapshot(s)['resource_hierarchy']['leaf'], '/accounting space/user/jobs')

    def test_proven_global_root_has_documented_root_exemption(self):
        s = sample(member='/')
        result = reader.evaluate_snapshot(s)
        self.assertEqual(result['memory_available'], 12*GiB)
        self.assertEqual(result['resource_hierarchy']['ancestors'][0]['accounting'], 'GLOBAL_ROOT_CONTROLLER_EXEMPTION')

    def test_finite_parent_fully_used_has_no_available_memory(self):
        s = sample()
        s['files']['/sys/fs/cgroup/user/memory.max'] = str(GiB)
        s['files']['/sys/fs/cgroup/user/memory.current'] = str(2*GiB)
        self.assertEqual(reader.evaluate_snapshot(s)['memory_available'], 0)

    def test_missing_current_is_rejected_even_with_explicit_max(self):
        s = sample()
        del s['files']['/sys/fs/cgroup/user/jobs/memory.current']
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_unreadable_limit_is_not_unlimited(self):
        s = sample()
        s['files']['/sys/fs/cgroup/user/cpu.max'] = {'error':'PermissionError'}
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_missing_parent_limit_is_not_skipped(self):
        s = sample()
        del s['files']['/sys/fs/cgroup/user/memory.max']
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_namespace_hidden_ancestors_are_not_admitted(self):
        s = sample()
        s['namespaces']['self']['cgroup'] = 'cgroup:[99]'
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_pid_namespace_visibility_insufficient_is_rejected(self):
        s = sample()
        s['namespaces']['self']['pid'] = 'pid:[99]'
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_truncated_mount_root_is_rejected(self):
        s = sample(mountroot='/user')
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_namespace_relative_membership_does_not_guess_hidden_root(self):
        s = sample(member='/jobs', mountroot='/delegated')
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_kernel_thread_identity_is_required_for_root_visibility(self):
        s = sample()
        s['kernel2_status'] = s['kernel2_status'].replace('Kthread:\t1','Kthread:\t0')
        with self.assertRaises(reader.ResourceError):
            reader.evaluate_snapshot(s)

    def test_v1_hybrid_and_duplicate_memberships_rejected(self):
        for text in ('2:cpu:/user\n', '0::/user\n2:memory:/user\n', '0::/user\n0::/other\n'):
            with self.subTest(text=text):
                s = sample();s['membership'] = text
                with self.assertRaises(reader.ResourceError):reader.evaluate_snapshot(s)

    def test_ambiguous_and_hybrid_mounts_rejected(self):
        for extra in ('35 25 0:29 / /other rw - cgroup2 cgroup2 rw\n', '35 25 0:31 / /legacy rw - cgroup cgroup rw\n'):
            with self.subTest(extra=extra):
                s = sample();s['mountinfo'] += extra
                with self.assertRaises(reader.ResourceError):reader.evaluate_snapshot(s)

    def test_path_traversal_or_malformed_membership_rejected(self):
        for member in ('/user/../other','relative','/user/./jobs','/user//jobs','/user (deleted)'):
            with self.subTest(member=member):
                s=sample();s['membership']='0::'+member+'\n'
                with self.assertRaises(reader.ResourceError):reader.evaluate_snapshot(s)

    def test_malformed_cpu_and_memory_values_rejected(self):
        for name,value in [('cpu.max','max 0'),('cpu.max','0 100000'),('cpu.max','-1 100000'),('cpu.max','100 0'),('cpu.max','max'),('cpu.max','max 100000 extra'),('memory.max','-1'),('memory.current','max'),('memory.current','-1'),('memory.max','bogus')]:
            with self.subTest(name=name,value=value):
                s=sample();s['files']['/sys/fs/cgroup/user/jobs/'+name]=value
                with self.assertRaises(reader.ResourceError):reader.evaluate_snapshot(s)

    def test_missing_controllers_and_partial_global_root_rejected(self):
        for key,value in [('/sys/fs/cgroup/cgroup.controllers','cpu'),('/sys/fs/cgroup/memory.current','0')]:
            with self.subTest(key=key):
                s=sample();s['files'][key]=value
                with self.assertRaises(reader.ResourceError):reader.evaluate_snapshot(s)


if __name__ == '__main__':
    unittest.main()
