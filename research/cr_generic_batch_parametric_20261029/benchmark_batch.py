"""Original pinned 3201 atom actual batch run; exact compare without physical promotion."""
from pathlib import Path
from native_budget import load_pr116_npz
from batch_bridge import run_batch
from fractions import Fraction as F
import hashlib, time, json, resource
p=Path(__file__).parent
raw=(p/'ATTRIBUTION_ARRAYS.npz').read_bytes()
sha=hashlib.sha256(raw).hexdigest()
if sha!='1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47': raise RuntimeError('ORIGINAL_NPZ_SHA_MISMATCH')
atoms=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz')
prior=json.loads((p/'native_actual.json').read_text());cs=[F(row['c']) for row in prior['frontier']]
t0=time.perf_counter();cpu=time.process_time();zs=run_batch(atoms,F(3),cs,timeout=120)
res=[]
for idx,(want,z) in enumerate(zip(prior['frontier'],zs)):
 if z['M']!=F(want['M_budget']) or z['d_max']!=F(want['d_max']) or z['gap']!=0: raise RuntimeError('EXACT_PARENT_DISAGREEMENT')
 if z['checked_edges']!=102831: raise RuntimeError('ELIGIBLE_GRAPH_MISMATCH')
 res.append({'case':idx,'budget':str(cs[idx]),'M':str(z['M']),'d_max':str(z['d_max']),
             'cost':str(z['C']),'dual_gap':str(z['gap']),'lambda':str(z['lambda_dual']),
             'state':z['state'],'checked_edges':z['checked_edges'],
             'positive_pairs':z['positive_pairs'],'cumulative_cpp_stats':z['cpp_stats']})
rec={'original_npz_sha256':sha,'atoms':len(atoms),'budget_count':len(cs),
     'wall_seconds':time.perf_counter()-t0,'python_cpu_seconds':time.process_time()-cpu,
     'child_peak_rss_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'results':res}
(p/'BENCHMARK_ORIGINAL.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec,indent=2))
