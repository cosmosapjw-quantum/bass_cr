"""Independent read-only pin verification and tiny exact-rational algebra.

No audited module is imported. No quadrature, source API, decay solver, ODE,
historical computation, or FS deposition function is executed.
"""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import hashlib
import json
import time

R=Path(__file__).resolve().parent
W=R.parents[1]
S=W/'nuclear_supply'
start=time.perf_counter()
manifest_bytes=(S/'MANIFEST.json').read_bytes()
manifest_sha=hashlib.sha256(manifest_bytes).hexdigest()
assert manifest_sha=='f4d667d23e567b1165193ce6a43c6374058fc0d54b41cae40fb5ea8e462c11db'
manifest=json.loads(manifest_bytes)
files=[]
for row in manifest['files']:
    raw=(S/row['path']).read_bytes()
    got=hashlib.sha256(raw).hexdigest()
    assert got==row['sha256'] and len(raw)==row['bytes'],row['path']
    files.append({'path':row['path'],'bytes':len(raw),'sha256':got,'status':'MATCH'})
assert len(files)==manifest['file_count']==29
assert sum(r['bytes'] for r in files)==manifest['total_bytes']==233841
run=S/'c23a_beta_fs2010_coverage_20261023_v1'
pins=json.loads((run/'INPUT_CODE_PINS.json').read_text())
for row in pins:
    raw=(S/row['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['bytes']
binding=json.loads((S/'source/EVALUATED_DECAY_BINDING.json').read_text())
prior=(S/'source/EVALUATED_DECAY_INPUTS.json').read_bytes()
git_blob=hashlib.sha1(b'blob '+str(len(prior)).encode()+b'\0'+prior).hexdigest()
assert git_blob==binding['git_blob']=='33fd920abce6cc28ff26a850b030bb7b4fd2462e'
prior_data=json.loads(prior)
assert not any('energy' in k or 'endpoint' in k for k in prior_data)
contract=json.loads((S/'source/EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json').read_text())
results=json.loads((run/'RESULT.json').read_text())
L=Fraction(contract['domain']['lower_eV']);U=Fraction(contract['domain']['upper_eV'])
checks=[]
for name,energy in contract['energy_inputs'].items():
    Q=Fraction(energy['decay_Q_eV']);m=Fraction(energy['electron_mean_kinetic_eV'])
    assert 0<L<U<Q and 0<m<Q
    # Derived separately from T*1_D <= U*(Q-T)/(Q-U).
    energy_upper=min(Fraction(1),(U/m)*((Q-m)/(Q-U)))
    number_upper=min(Fraction(1),m/L,(Q-m)/(Q-U))
    stored=results['results'][name]['conditional_moment_bounds']
    assert energy_upper==Fraction(stored['kinetic_energy_fraction_upper_exact'])
    assert number_upper==Fraction(stored['particle_upper_exact'])
    # Preserve nonuniqueness witness moments without executing the producer API.
    witness_checks=[]
    for witness in stored['same_mean_and_endpoint_counterexamples']:
        support=list(map(Fraction,witness['support_eV_exact']))
        weights=list(map(Fraction,witness['probability_exact']))
        assert all(w>=0 for w in weights) and sum(weights)==1
        assert sum(x*w for x,w in zip(support,weights))==m
        assert max(support)==Q and weights[support.index(Q)]>0
        pd=sum(w for x,w in zip(support,weights) if L<=x<=U)
        ed=sum(x*w for x,w in zip(support,weights) if L<=x<=U)
        witness_checks.append({'normalization_exact':True,'mean_exact':True,
            'endpoint_supported':True,'in_domain_number_exact':str(pd),
            'in_domain_energy_fraction_exact':str(ed/m)})
    checks.append({'source':name,'Q_eV_exact':str(Q),'mean_eV_exact':str(m),
        'conditional_number_upper_exact':str(number_upper),
        'conditional_energy_upper_exact':str(energy_upper),
        'conditional_energy_upper':float(energy_upper),
        'stored_bound_matches':True,'witnesses':witness_checks})
receipt={'schema':'C23A_NUCLEAR_C9_READ_ALGEBRA_V1','reviewer':'/root/igm_supply',
    'source_manifest_sha256':manifest_sha,'source_files':files,
    'source_file_count':len(files),'source_total_bytes':sum(r['bytes'] for r in files),
    'completed_run_code_pins_matched':len(pins),'existing_lifetime_git_blob':git_blob,
    'existing_lifetime_energy_fields':'ABSENT','tiny_independent_rational_checks':checks,
    'audited_module_imports':0,'producer_code_executions':0,'quadrature_reruns':0,
    'source_API_calls':0,'new_ODE':0,'historical_ODE_reruns':0,
    'resource_scope':'stdlib file reads/hashes and a few exact Fraction operations; no science worker dispatched',
    'wall_s':time.perf_counter()-start,'status':'PASS_SCOPED',
    'created_utc':datetime.now(timezone.utc).isoformat()}
with (R/'READ_AND_ALGEBRA.json').open('x') as f:
    json.dump(receipt,f,indent=2,allow_nan=False)
    f.write('\n')
print(json.dumps({'status':receipt['status'],'files_matched':len(files),
    'run_pins_matched':len(pins),'source_manifest_sha256':manifest_sha,
    'bound_checks':checks,'wall_s':receipt['wall_s']},indent=2))
