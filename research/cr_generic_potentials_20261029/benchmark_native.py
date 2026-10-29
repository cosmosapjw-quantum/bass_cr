"""Source-locked conditional K3 benchmark, with exact witnesses and audit receipts."""
from __future__ import annotations
import json,os,sys,time,resource,hashlib
from fractions import Fraction as F
from pathlib import Path
from native_budget import load_pr116_npz
from potentials_bridge import run_exact
folder=Path(__file__).parent
base=Path(sys.argv[1]); raw=(base/'ATTRIBUTION_ARRAYS.npz').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
atoms=load_pr116_npz(base/'ATTRIBUTION_ARRAYS.npz')
prior=json.loads((base/'native_actual.json').read_text())
cases=prior['frontier']
if len(sys.argv)>2: cases=[cases[int(sys.argv[2])]]
record=[]
for row in cases:
 c=F(row['c']); t=time.perf_counter()
 got=run_exact(atoms,F(3),c,timeout=90.0)
 elapsed=time.perf_counter()-t
 assert got['M']==F(row['M_budget']),('M_DIFFER',c,got['M'],row['M_budget'])
 assert got['d_max']==F(row['d_max'])
 assert got['gap']==0
 rec={k:str(got[k]) for k in ('M','C','d_max','lambda_dual','gap')}
 rec.update(c=str(c),seconds=elapsed,peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            cpp_stats=got['cpp_stats'],positive_edges=len(got['flow']),eligible_active=got['eligible_edges'],
            checked_original_edges=got['checked_edges'],atoms=len(atoms),status=got['state'])
 record.append(rec)
 print(json.dumps(rec,sort_keys=True),flush=True)
(folder/'benchmark_native_results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'results':record},indent=2)+'\n')