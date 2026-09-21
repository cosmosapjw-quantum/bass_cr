from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',required=True);p.add_argument('--step',type=float,default=.4);p.add_argument('--bmax',type=float,default=14.);a=p.parse_args()
base=json.loads(Path(a.base).read_text());out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
n=int(round(a.bmax/a.step))
for i in range(n+1):
 b=i*a.step;c=json.loads(json.dumps(base));c['b']=b
 (out/f'b{i:03d}_{b:.6f}.json').write_text(json.dumps(c,indent=2))
print(json.dumps({'count':n+1,'step':a.step,'bmax':a.bmax,'out':str(out)},indent=2))
