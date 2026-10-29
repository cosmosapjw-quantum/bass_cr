"""One exact same-host paired run, plus isolated original-dual certificate timing.

Scoped to the 3201-atom source and three fixed budgets. Not production timings.
"""
from pathlib import Path
from fractions import Fraction as F
from native_budget import load_pr116_npz
from prefix_bridge import run_prefix
from prefix_dual_oracle import DualPrefixOracle,explicit_original_dual_check
import json,time,resource,statistics,hashlib
p=Path(__file__).parent
atoms=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz')
base=json.loads((p/'native_actual.json').read_text())
R=F(base['R']); qs=[F(0),R/2,R]
records={}; outputs={}
for mode in ('explicit','prefix_exact'):
 t=time.perf_counter();c=time.process_time()
 u=run_prefix(atoms,F(3),qs,dual_check=mode,timeout=120)
 records[mode]={'end_to_end_wall_s':time.perf_counter()-t,'python_process_cpu_s':time.process_time()-c,
                'results':[{'budget':str(v['budget']),'M':str(v['M']),'C':str(v['C']),
                            'd_max':str(v['d_max']),'gap':str(v['gap']),'logical_edges':v['checked_edges'],
                            'prefix_constraints':v['grouped_dual_constraints'],'pairs':v['positive_pairs'],
                            'solver_stats':v['cpp_stats']} for v in u]}
 outputs[mode]=u
for a,b in zip(outputs['explicit'],outputs['prefix_exact']):
 for f in ('budget','M','C','d_max','lambda_dual','gap','prices','flow','checked_edges','cpp_stats'):
  assert a[f]==b[f],f
 assert b['gap']==0 and b['checked_edges']==102831
oracle=DualPrefixOracle(atoms,F(3))
for mode in ('explicit','prefix_exact'):
 timing=[]; counts=[]
 for x in outputs['explicit']:
  t=time.perf_counter()
  for i in range(3):
   if mode=='explicit': count=explicit_original_dual_check(atoms,F(3),x['prices'],x['lambda_dual'])
   else: count=oracle.verify(x['prices'],x['lambda_dual'])[0]
  timing.append((time.perf_counter()-t)/3)
  assert count==102831
  counts.append(count)
 records[mode]['certificate_only_wall_s_per_budget_3rep'] = timing
record={'source_original_npz_sha256':hashlib.sha256((p/'ATTRIBUTION_ARRAYS.npz').read_bytes()).hexdigest(),
       'atoms':len(atoms),'budgets':[str(z) for z in qs],
       'comparison_scope':'one same-host pair and three repeats of exact dual-only checks per budget; not significance nor production',
       'modes':records,'equivalence':'same original all-atom prices/flow/budgets/M/C/dmax/gap',
       'old_pr124_review_status':'R06_C09_NOT_RUN','physical_activation':False}
record['n1_end_to_end_speed_ratio_explicit_over_prefix']=records['explicit']['end_to_end_wall_s']/records['prefix_exact']['end_to_end_wall_s']
record['dual_certificate_time_ratio']=statistics.median(records['explicit']['certificate_only_wall_s_per_budget_3rep'])/statistics.median(records['prefix_exact']['certificate_only_wall_s_per_budget_3rep'])
(p/'BENCHMARK_DUAL_ORACLE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'baseline_wall_s':records['explicit']['end_to_end_wall_s'],
                  'fast_wall_s':records['prefix_exact']['end_to_end_wall_s'],
                  'speed_ratio_n1':record['n1_end_to_end_speed_ratio_explicit_over_prefix'],
                  'dual_cert_ratio':record['dual_certificate_time_ratio'],
                  'original_edges':102831,'group_checks':records['prefix_exact']['results'][0]['prefix_constraints']},indent=2))
