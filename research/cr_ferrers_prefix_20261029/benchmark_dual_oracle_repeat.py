"""Fresh same-host exact 3-budget paired confirmations, not statistical power."""
from pathlib import Path
from fractions import Fraction as F
import json,time,resource,statistics
from native_budget import load_pr116_npz
from prefix_bridge import run_prefix
p=Path(__file__).parent
atoms=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz');base=json.loads((p/'native_actual.json').read_text());R=F(base['R']);qs=[F(0),R/2,R]
old=json.loads((p/'BENCHMARK_DUAL_ORACLE.json').read_text())
pairs=[{'explicit':old['modes']['explicit']['end_to_end_wall_s'],
        'prefix_exact':old['modes']['prefix_exact']['end_to_end_wall_s'],
        'order':['explicit','prefix_exact']}]
for order in [('prefix_exact','explicit'),('explicit','prefix_exact')]:
 rec={'order':list(order)}; results={}
 for mode in order:
  t=time.perf_counter();z=run_prefix(atoms,F(3),qs,dual_check=mode,timeout=120)
  rec[mode]=time.perf_counter()-t;results[mode]=z
 for a,b in zip(results['explicit'],results['prefix_exact']):
  for f in ('budget','M','C','d_max','lambda_dual','gap','prices','flow','checked_edges','cpp_stats'):
   assert a[f]==b[f], f
  assert a['gap']==0 and a['checked_edges']==102831
 pairs.append(rec)
old['pairs'] = pairs
old['n3_median_explicit_wall_s']=statistics.median(q['explicit'] for q in pairs)
old['n3_median_prefix_exact_wall_s']=statistics.median(q['prefix_exact'] for q in pairs)
old['n3_ratio_of_medians']=old['n3_median_explicit_wall_s']/old['n3_median_prefix_exact_wall_s']
old['n3_scope']='3 sequential paired 3201-atom 3-budget runs, alternating order; exact price, flow, objective equality and original-edge logical certification; no statistical significance'
(p/'BENCHMARK_DUAL_ORACLE.json').write_text(json.dumps(old,indent=2)+'\n')
print(json.dumps({'pairs':pairs,'ratio_of_medians':old['n3_ratio_of_medians'],'median_explicit_s':old['n3_median_explicit_wall_s'],'median_prefix_s':old['n3_median_prefix_exact_wall_s']},indent=2))
