from pathlib import Path
from fractions import Fraction as F
import json,time,resource,hashlib
from native_budget import load_pr116_npz
from prefix_bridge import run_prefix
p=Path(__file__).parent
atoms=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz')
base=json.loads((p/'native_actual.json').read_text())
R=F(base['R']);qs=[F(0),R/2,R]
t0=time.perf_counter();u0=resource.getrusage(resource.RUSAGE_SELF);c0=resource.getrusage(resource.RUSAGE_CHILDREN)
z=run_prefix(atoms,F(3),qs,timeout=90)
w=time.perf_counter()-t0;u1=resource.getrusage(resource.RUSAGE_SELF);c1=resource.getrusage(resource.RUSAGE_CHILDREN)
for result,old in zip(z,[base['frontier'][0],base['frontier'][2],base['frontier'][1]]):
 assert result['M']==F(old['M_budget']) and result['d_max']==F(old['d_max'])
 assert result['gap']==0 and result['checked_edges']==102831
print('source 3201 original SHA',hashlib.sha256((p/'ATTRIBUTION_ARRAYS.npz').read_bytes()).hexdigest())
report={'wall_seconds':w,'cpu_user_seconds':u1.ru_utime-u0.ru_utime+c1.ru_utime-c0.ru_utime,'cpu_sys_seconds':u1.ru_stime-u0.ru_stime+c1.ru_stime-c0.ru_stime,'maxrss_self_kb':u1.ru_maxrss,'maxrss_children_kb':c1.ru_maxrss,'queries':[]}
for r in z:
 row={'c':str(r['budget']),'M':str(r['M']),'d_max':str(r['d_max']),'gap':str(r['gap']),'checked_edges':r['checked_edges'],'positive_pairs':r['positive_pairs'],'pruned_high':r['pruned_high'],'active_high':r['active_high'],'active_low':r['active_low'],'cpp_stats':r['cpp_stats']}
 report['queries'].append(row);print(json.dumps(row))
(p/'BENCHMARK_SOURCE.json').write_text(json.dumps(report,indent=2)+'\n')
print('WALL',round(w,5),'CPU',round(report['cpu_user_seconds']+report['cpu_sys_seconds'],5),'RSS_KB',report['maxrss_children_kb'])
