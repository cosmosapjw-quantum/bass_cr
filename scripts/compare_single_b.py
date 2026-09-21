from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('results',nargs='+');a=p.parse_args()
rows=[]
for x in a.results:
 d=json.loads(Path(x).read_text());
 if 'analysis' in d: val=d['analysis']['P_bound_truncated_nmax']; kind='TDL'
 else: val=d['P_projectile_bound']; kind='AOCC'
 rows.append({'path':x,'kind':kind,'value':float(val)})
ref=rows[0]['value']
for r in rows: r['relative_to_first']=abs(r['value']-ref)/max(abs(r['value']),1e-300)
print(json.dumps(rows,indent=2))
