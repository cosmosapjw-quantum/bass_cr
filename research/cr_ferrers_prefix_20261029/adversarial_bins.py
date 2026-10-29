from pathlib import Path
import json,time,resource
from fractions import Fraction as F
from native_budget import load_pr116_npz,Atom
from prefix_bridge import run_prefix
p=Path(__file__).parent
original=load_pr116_npz(p/'ATTRIBUTION_ARRAYS.npz')
# Fixed declared synthetic recoloring: the 3201 original energies/capacities are untouched.
a=tuple(Atom(x.key,x.energy,x.mass,(i*7+int(x.energy*10))%5) for i,x in enumerate(original))
R=F(json.loads((p/'native_actual.json').read_text())['R'])
qs=[F(0),R/2,R]
u=resource.getrusage(resource.RUSAGE_SELF);ch=resource.getrusage(resource.RUSAGE_CHILDREN)
start=time.perf_counter();z=run_prefix(a,F(3),qs,timeout=85);wall=time.perf_counter()-start
v=resource.getrusage(resource.RUSAGE_SELF);c=resource.getrusage(resource.RUSAGE_CHILDREN)
rows=[{'c':str(t['budget']),'M':str(t['M']),'C':str(t['C']),'d':str(t['d_max']),'gap':str(t['gap']),'lambda':str(t['lambda_dual']), 'checked_edges':t['checked_edges'],'positive_pairs':t['positive_pairs'],'stats':t['cpp_stats']} for t in z]
assert all(t['gap']==0 and t['checked_edges']==102831 for t in z)
out={'scope':'synthetic-bin-relabel-original-energy-mass-unchanged','bin_rule':'(7*i+int(E_i*10))%5','source_sha256':'1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47','wall':wall,'cpu':v.ru_utime-u.ru_utime+c.ru_utime-ch.ru_utime+v.ru_stime-u.ru_stime+c.ru_stime-ch.ru_stime,'child_rss_kb':c.ru_maxrss,'queries':rows}
(p/'ADVERSARIAL_BINS.json').write_text(json.dumps(out,indent=2)+'\n')
for x in rows:print(json.dumps(x))
print('WALL',wall,'CPU',out['cpu'],'RSS',c.ru_maxrss)
