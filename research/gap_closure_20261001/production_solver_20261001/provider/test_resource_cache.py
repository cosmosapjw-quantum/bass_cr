"""Synthetic cgroup-cache admission cases; no native code or large allocation."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'hpc_optimization_20261001'))
import resource_profile as rp


def stat(**changes):
    row={'file':7000,'active_file':6000,'inactive_file':1000,'file_mapped':100,
         'file_dirty':200,'file_writeback':50,'shmem':30,'unevictable':20}
    row.update(changes);return row


class CacheMemoryTests(unittest.TestCase):
    def test_half_clean_credit_excludes_every_nonclean_category(self):
        self.assertEqual(rp.clean_file_credit(stat(),8000,0,0,0),3300)
        self.assertEqual(rp.clean_file_credit(stat(),8000,1000,300,0),2800)
        self.assertEqual(rp.clean_file_credit(stat(),2000,0,0,0),800)

    def test_missing_invalid_and_hierarchical_counters_get_no_credit(self):
        self.assertEqual(rp.clean_file_credit(stat(),8000,0,0,1),0)
        self.assertEqual(rp.clean_file_credit(stat(),8000,0,0,-1),0)
        for key in stat():
            row=stat();del row[key]
            self.assertEqual(rp.clean_file_credit(row,8000,0,0,0),0)
            self.assertEqual(rp.clean_file_credit(stat(**{key:-1}),8000,0,0,0),0)
        self.assertEqual(rp.clean_file_credit(stat(),8000,-1,0,0),0)

    def test_type_and_lru_totals_use_minimum_and_never_negative(self):
        self.assertEqual(rp.clean_file_credit(stat(active_file=1000,inactive_file=1000),8000,0,0,0),800)
        self.assertEqual(rp.clean_file_credit(stat(file_dirty=9000),8000,0,0,0),0)

    def write_cgroup(self,p,*,current='8000',missing=None,descendants=0):
        files={'memory.current':current,'memory.min':'0','memory.low':'0',
               'memory.stat':'\n'.join(f'{k} {v}' for k,v in stat().items()),
               'cgroup.stat':f'nr_descendants {descendants}\nnr_dying_descendants 0\n'}
        for name,value in files.items():
            if name!=missing:(p/name).write_text(value)

    def test_cgroup_raw_and_adjusted_headroom_are_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.write_cgroup(p)
            row=rp.cgroup_memory_headroom(p,9000)
            self.assertEqual(row['unreclaimed_headroom_bytes'],1000)
            self.assertEqual(row['clean_file_credit_bytes'],3300)
            self.assertEqual(row['estimated_available_bytes'],4300)

    def test_fallback_keeps_raw_cap_and_missing_usage_fails_closed(self):
        for missing in ('memory.stat','memory.min','memory.low','cgroup.stat'):
            with tempfile.TemporaryDirectory() as d:
                p=Path(d);self.write_cgroup(p,missing=missing)
                row=rp.cgroup_memory_headroom(p,9000)
                self.assertEqual(row['clean_file_credit_bytes'],0)
                self.assertEqual(row['estimated_available_bytes'],1000)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.write_cgroup(p,missing='memory.current')
            self.assertEqual(rp.cgroup_memory_headroom(p,9000)['estimated_available_bytes'],0)

    def test_racing_usage_uses_larger_charge_and_smaller_cache_base(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.write_cgroup(p)
            original=Path.read_text;reads=iter(['8000','2000'])
            def read(path,*args,**kwargs):
                return next(reads) if path.name=='memory.current' else original(path,*args,**kwargs)
            with patch.object(Path,'read_text',read):
                row=rp.cgroup_memory_headroom(p,9000)
            self.assertEqual(row['current_bytes'],8000)
            self.assertEqual(row['clean_file_credit_bytes'],800)
            self.assertEqual(row['estimated_available_bytes'],1800)

    def test_racing_cache_uses_smaller_of_two_observations(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.write_cgroup(p)
            original=Path.read_text
            reads=iter(['\n'.join(f'{k} {v}' for k,v in row.items())
                        for row in (stat(),stat(file_dirty=6000))])
            def read(path,*args,**kwargs):
                return next(reads) if path.name=='memory.stat' else original(path,*args,**kwargs)
            with patch.object(Path,'read_text',read):
                row=rp.cgroup_memory_headroom(p,9000)
            self.assertEqual(row['clean_file_credit_bytes'],400)
            self.assertEqual(row['estimated_available_bytes'],1400)

    def test_census_respects_tighter_ancestor_and_host_available(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);cg=root/'cg';leaf=cg/'job';leaf.mkdir(parents=True)
            proc=root/'proc';(proc/'self').mkdir(parents=True)
            (proc/'self/cgroup').write_text('0::/job\n')
            (proc/'cpuinfo').write_text('model name: synthetic\n')
            (proc/'meminfo').write_text('MemTotal: 67108864 kB\nMemAvailable: 33554432 kB\n')
            for directory,limit,current,children in ((cg,8,7,1),(leaf,16,15,0)):
                self.write_cgroup(directory,current=str(current*rp.GiB),descendants=children)
                (directory/'memory.max').write_text(str(limit*rp.GiB))
                (directory/'cpu.max').write_text('200000 100000')
            row=stat(file=10*rp.GiB,active_file=10*rp.GiB,inactive_file=0,
                     file_mapped=0,file_dirty=0,file_writeback=0,shmem=0,unevictable=0)
            (leaf/'memory.stat').write_text('\n'.join(f'{k} {v}' for k,v in row.items()))
            def route(value):
                value=str(value)
                if value=='/sys/fs/cgroup':return cg
                if value.startswith('/proc/'):return proc/value.removeprefix('/proc/')
                return Path(value)
            with patch.object(rp,'Path',side_effect=route), \
                 patch.object(rp.os,'sched_getaffinity',return_value={0,1}):
                info=rp.census()
                self.assertEqual(info['memory_limit_bytes'],8*rp.GiB)
                self.assertEqual(info['memory_available_bytes'],rp.GiB)
                (proc/'meminfo').write_text('MemTotal: 67108864 kB\nMemAvailable: 524288 kB\n')
                self.assertEqual(rp.census()['memory_available_bytes'],rp.GiB//2)

    def test_overlimit_usage_must_be_repaid_before_credit_is_available(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.write_cgroup(p,current='10000')
            self.assertEqual(rp.cgroup_memory_headroom(p,9000)['estimated_available_bytes'],2300)

if __name__=='__main__':unittest.main()
