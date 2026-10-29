"""Matched source-independent end-to-end benchmark of batch vs PR122 repeated solver.
No claimed physical source or production speedup. Process and Python verification included.
"""
from native_budget import Atom
from batch_bridge import run_batch
from potentials_bridge import run_exact
from fractions import Fraction as F
import random, time, statistics, json, resource
from pathlib import Path
rng=random.Random(20261029)
atoms=tuple(Atom.parse('S'+str(i),F(rng.randrange(0,21),2),F(rng.randrange(1,9),8),rng.randrange(5)) for i in range(120))
K=F(10);budgets=[F(0),F(1,3),F(1),F(5,2),F(5),F(9),F(15),F(30)]
measurements=[]
for trial in range(3):
    t=time.perf_counter();a=run_batch(atoms,K,budgets);tbatch=time.perf_counter()-t
    t=time.perf_counter();b=[run_exact(atoms,K,c,executable=Path(__file__).parent/'potentials_ssp') for c in budgets];tsingle=time.perf_counter()-t
    for x,y in zip(a,b):
        if (x['M'],x['d_max'],x['C'],x['lambda_dual'])!=(y['M'],y['d_max'],y['C'],y['lambda_dual']):
            raise RuntimeError('MATCHED_OUTPUT_MISMATCH')
        if x['gap']!=y['gap'] or x['checked_edges']!=y['checked_edges']:
            raise RuntimeError('CERTIFICATE_MISMATCH')
    measurements.append({'trial':trial,'batch_s':tbatch,'repeated_s':tsingle,'ratio':tsingle/tbatch,
                         'batch_augmentations':a[-1]['cpp_stats'][0],
                         'sum_repeated_augmentations':sum(x['cpp_stats'][0] for x in b),
                         'dual_edges_per_budget':a[0]['checked_edges']})
record={'contract':'same 120 synthetic atoms, 5 bins, 8 budgets, exact Python certificates, i128 C++ O2, same host','seed':20261029,
        'measurements':measurements,'median_batch_s':statistics.median(x['batch_s'] for x in measurements),
        'median_repeated_s':statistics.median(x['repeated_s'] for x in measurements),
        'ratio_of_medians':statistics.median(x['repeated_s'] for x in measurements)/statistics.median(x['batch_s'] for x in measurements),
        'peak_rss_child_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
Path(__file__).with_name('BENCHMARK_MATCHED_SYNTHETIC.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
