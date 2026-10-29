from pathlib import Path
import json,time,resource
from fractions import Fraction as F
from native_budget import load_pr116_npz
from batch_bridge import run_batch
p=Path(__file__).parent
atoms=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz')
old=json.loads((p/'native_actual.json').read_text());r=F(old['R'])
start=time.perf_counter();u=resource.getrusage(resource.RUSAGE_SELF);c=resource.getrusage(resource.RUSAGE_CHILDREN)
z=run_batch(atoms,F(3),[F(0),r/2,r],executable=p/'potentials_batch',timeout=90)
end=time.perf_counter();u1=resource.getrusage(resource.RUSAGE_SELF);c1=resource.getrusage(resource.RUSAGE_CHILDREN)
for v,ref in zip(z,[old['frontier'][0],old['frontier'][2],old['frontier'][1]]):
 assert v['M']==F(ref['M_budget']) and v['d_max']==F(ref['d_max']) and v['checked_edges']==102831 and v['gap']==0
 print('budget',v['budget'],'M',v['M'],'C',v['C'],'STATS',v['cpp_stats'])
w=end-start;secs=u1.ru_utime-u.ru_utime+c1.ru_utime-c.ru_utime+u1.ru_stime-u.ru_stime+c1.ru_stime-c.ru_stime
print('PARENT_WALL',w,'PARENT_CPU',secs,'PARENT_CHILD_RSS_KB',c1.ru_maxrss)
(p/'BENCHMARK_PARENT_MATCHED.json').write_text(json.dumps({'wall_seconds':w,'cpu_seconds':secs,'children_rss_kb':c1.ru_maxrss,'stats':[v['cpp_stats'] for v in z]},indent=2)+'\n')
