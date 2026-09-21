import json,csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def resources(out):
 d={};p=out/'resource.txt'
 if p.exists():
  m=re.search(r'Maximum resident set size \(kbytes\): (\d+)',p.read_text());d['peak_host_rss_KiB']=int(m[1]) if m else None
 p=out/'gpu_memory_samples.jsonl';values=[]
 if p.exists():
  for line in p.read_text().splitlines():
   for item in json.loads(line).get('owned',[]):values.append(item['MiB'])
 d['peak_gpu_MiB_sampled']=max(values) if values else None
 return d

def row(name,lane):
 out=ROOT/'runs'/name
 if name=='tdl_baseline' and (ROOT/'runs/tdl_baseline_retry/result.json').exists():
  out=ROOT/'runs/tdl_baseline_retry';name='tdl_baseline_retry'
 r={'run':name,'status':'NOT_RUN','lane':lane}
 if not (out/'receipt.json').exists():return r
 q=json.loads((out/'receipt.json').read_text());r.update(status=q['status'],wall_seconds=q.get('wall_seconds'),config_sha256=q['config_sha256'],code_digest=q['code_digest'],**resources(out))
 if not (out/'result.json').exists():
  if (out/'progress.json').exists():r['progress']=json.loads((out/'progress.json').read_text())
  if (out/'state.json').exists():r['progress']=json.loads((out/'state.json').read_text())
  return r
 d=json.loads((out/'result.json').read_text());c=d.get('config',{})
 if lane=='TDL':
  a=d['analysis'];r.update(probability=a['P_bound_truncated_nmax'],P_region=a['P_region'],nmax=a['project_nmax'],initial_Eh=d['initial']['energy_Eh'],norm=a['wavefunction_norm'],dt_actual=d['dt_actual'],dx=c['grid']['dx'],capture_plane=c['capture_plane'],z_stop=c['z_stop'],state_amplitudes=a['state_amplitudes'],finite_grid_state_norms=a['finite_grid_state_norms'])
  if (out/'n1_diagnostics.json').exists():r['n1_diagnostics']=json.loads((out/'n1_diagnostics.json').read_text())
 else:r.update(probability=d['P_projectile_bound'],norm=d['norm'],nbasis=d['nbasis'],dt_actual=d['dt_actual'],negative_atomic_energies_Eh=d['negative_atomic_energies_Eh'],max_antihermitian_defect=d['max_antihermitian_defect'])
 return r

tdl=[row('tdl_'+n,'TDL') for n in ['baseline','dt025','dx03125','plane25','z75','boxwide']]
aocc=[row('aocc_'+n,'AOCC') for n in ['baseline','basis_large']]
for rows in [tdl,aocc]:
 b=rows[0].get('probability')
 for r in rows:r['relative_change_to_baseline']=abs(r['probability']-b)/abs(b) if b and 'probability'in r else None
for name,rows in [('tdl_convergence',tdl),('aocc_basis_convergence',aocc)]:
 (ROOT/'report'/f'{name}.json').write_text(json.dumps(rows,indent=2))
 keys=sorted(set(k for r in rows for k,v in r.items() if not isinstance(v,(dict,list))))
 with (ROOT/'report'/f'{name}.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
print(json.dumps({'tdl':[{k:r.get(k) for k in ['run','status','probability','relative_change_to_baseline','wall_seconds']} for r in tdl],'aocc':[{k:r.get(k) for k in ['run','status','probability','relative_change_to_baseline','wall_seconds']} for r in aocc]},indent=2))
