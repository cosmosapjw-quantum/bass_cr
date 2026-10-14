"""Separate guarded main script: forkserver cannot spawn from interactive stdin."""
import json
from time import perf_counter
from statistics import median
from ray_parallel import compress_rays
from threshold_rt import frozen_source


def main():
    nn=(1e-3,8e-5,2e-5)
    base=frozen_source(16)
    rows=[]
    for n in (8,64):
        cohorts=[[(e*(1+j*.000001),mass) for e,mass in base] for j in range(n)]
        old=None
        for workers in (1,2,4):
            durations=[]
            for _ in range(3):
                t=perf_counter()
                out=compress_rays(cohorts,[32]*n,[nn]*n,[1e9]*n,[.99]*n,.1,10.,workers=workers)
                durations.append(perf_counter()-t)
            if old is None:old=out
            else:assert out==old
            rows.append(dict(rays=n,workers=workers,median_s=median(durations),times_s=durations,
                             actual_count_end=sum(len(x[0]) for x in out),same_as_serial=True))
    print(json.dumps({'schema':'bass_cr.ray_parallel.matched_benchmark.v1',
                      'note':'Pool startup and IPC included in each call. Same ray source/IC and float result.',
                      'rows':rows},indent=2))
if __name__=='__main__':main()
