from pathlib import Path
import argparse,json,numpy as np,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cr_repro.observables import capture_cross_section_a0sq
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--field',default='P_projectile_bound');p.add_argument('--out',required=True);a=p.parse_args()
rows=[]
for f in Path(a.root).glob('b*/result.json'):
 d=json.loads(f.read_text()); b=float(d.get('config',{}).get('b',f.parent.name[1:].replace('p','.')))
 if 'analysis' in d: val=float(d['analysis'].get('P_bound_truncated_nmax'))
 else: val=float(d[a.field])
 rows.append((b,val,str(f)))
rows.sort(); b=np.array([x[0] for x in rows]);v=np.array([x[1] for x in rows]);sigma=capture_cross_section_a0sq(b,v)
out={'rows':[{'b':x,'P':y,'source':s} for x,y,s in rows],'sigma_a0sq':sigma,'field':a.field,'claim':'trapezoid over explicit completed b nodes; tail convergence is separate'}
Path(a.out).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
