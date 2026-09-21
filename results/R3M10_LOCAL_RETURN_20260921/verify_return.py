"""Host artifact-binding checks, distinct from numerical convergence admission."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

runs=['tdl_baseline_retry','tdl_dt025','tdl_dx03125','tdl_plane25','tdl_z75','tdl_boxwide','aocc_baseline','aocc_basis_large']
for name in runs:
 out=ROOT/'runs'/name;rec=json.loads((out/'receipt.json').read_text());res=json.loads((out/'result.json').read_text())
 assert rec['status']=='PASS' and res['status']=='completed',name
 assert json.loads((out/'config.json').read_text())==res['config'],name
 assert rec['config_sha256']==sha(out/'config.json'),name
 for relative,digest in rec['code_hashes'].items():assert sha(ROOT/'source'/relative)==digest,(name,relative)
 for relative,digest in rec['output_hashes'].items():assert sha(out/relative)==digest,(name,relative)
 if name.startswith('tdl'):
  state=json.loads((out/'state.json').read_text());assert state['done']==state['nstep']==res['nstep']
  a=res['analysis'];assert len(a['state_amplitudes'])==14
  assert abs(sum(x*x+y*y for x,y in a['state_amplitudes'].values())-a['P_bound_truncated_nmax'])<1e-14
  n1=json.loads((out/'n1_diagnostics.json').read_text());assert n1['inequality_satisfied']
 else:assert abs(res['norm']-1)<1e-10
assert '20 passed' in (ROOT/'runs/pytest_final/stdout.txt').read_text()
for name in ['tdl_smoke','aocc_smoke','aocc_smoke_batched']:
 assert json.loads((ROOT/'runs'/name/'receipt.json').read_text())['status']=='PASS'
gate=json.loads((ROOT/'report/DECISION.json').read_text());assert gate['decision']=='NO_GO' and not gate['bgrid_launched']
assert not (ROOT/'runs/tdl_baseline/result.json').exists()
print('PASS: eight completed single-b runs, immutable config/code/output bindings, 20 tests, both smoke paths, n1 bounds, failure preserved, NO_GO gate.')
