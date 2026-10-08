import ctypes
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import numpy as np
import pytest
import preflight as p

def test_exact_r4o_reproduction(inputs):
    receipt = p.closeout(inputs)
    obs = receipt['observable']
    expected = [0.00965343237616185, 0.009653417329471998, 0.009653428615023815]
    for actual, oracle in zip(obs['probabilities'].values(), expected):
        assert abs(actual-oracle) <= 8*math.ulp(oracle)
    assert obs['order_roundoff_interval'][0] <= 2.0002049811596685 <= obs['order_roundoff_interval'][1]
    assert math.isclose(obs['absolute_difference'], 3.7611380347e-9, abs_tol=16*math.ulp(expected[0]), rel_tol=0)
    assert math.isclose(obs['relative_difference'], 3.8961665531e-7, abs_tol=16*math.ulp(expected[0])/expected[0], rel_tol=0)
    assert obs['status'] == 'FINITE_SPAN_SELECTED_OBSERVABLE_TEMPORALLY_ADMITTED'
    assert obs['claim_labels'] == ['NOT_ALL_BOUND','NOT_ASYMPTOTIC_CAPTURE','NOT_PRODUCTION_CAPTURE']
    assert obs['projector']['metric_idempotence_defect'] < 1e-12
    assert obs['projector']['gram_condition'] < 1.000000000001
    assert receipt['temporal']['gate'] == 'CLOSED_FOR_CURRENT_FIXED_BASIS_AND_WINDOW'
    assert abs(receipt['temporal']['p_ref']-2.000008800631878)<1e-11
    assert abs(receipt['temporal']['p_self']-2.000046457687837)<1e-11
    assert receipt['native_operator_calls'] == 0

def test_positive_pseudostates_excluded(inputs):
    basis=json.loads((inputs/'BASIS.json').read_text())
    rows=p.bind_bank(p.registry('B0'),basis['modes'])
    selected=[r['index'] for r in rows if r['center']==1 and r['kind']=='bound']
    assert selected==[9,10,12,13,14]
    assert [r['index'] for r in rows if r['center']==1 and r['kind']=='positive_pseudostate']==[11,15,16,17]
    with pytest.raises(ValueError,match='selector'):
        p.projector(np.eye(18),np.eye(18)[0],(9,10,11,12,13,14))

@pytest.mark.parametrize('name,count,bound,positive',[('B0',18,5,4),('B1',46,14,9),('B2',92,30,16),('B3',124,30,32)])
def test_registry_counts_order_symmetry(name,count,bound,positive):
    r=p.registry(name);rows=r['channels'];half=count//2
    assert len(rows)==count
    assert [row['index'] for row in rows]==list(range(count))
    assert rows[:half]==[{**row,'index':row['index']-half,'center':0} for row in rows[half:]]
    assert sum(c['kind']=='bound' for c in rows[:half])==bound
    assert sum(c['kind']=='positive_pseudostate' for c in rows[:half])==positive
    assert [(c['radial_mode'],c['m']) for c in rows[:half]]==sorted((c['radial_mode'],c['m']) for c in rows[:half])
    assert r==p.registry(name)
    assert r['inherits_B0_temporal_certificate'] is False
    assert r['radial_spec']['radius']==64 and r['radial_spec']['elements']==40
    assert r['radial_spec']['degree']==4 and r['radial_spec']['quad_order']==12 and r['radial_spec']['grading']==2

def test_nested_semantics_and_no_higher_l_backend_fallback():
    ladders=[p.registry(n) for n in ('B0','B1','B2','B3')]
    def sig(r):return {(c['center'],c['l'],c['m'],c['principal_n'],c['positive_rank']) for c in r['channels']}
    assert sig(ladders[0]) < sig(ladders[1]) < sig(ladders[2]) < sig(ladders[3])
    assert [r['original_five_channel_projectile_span'] for r in ladders]==[[9,10,12,13,14],[23,24,27,28,29],[46,47,51,52,53],[62,63,68,69,70]]
    assert all(r['frozen_native_backend_status']=='UNSUPPORTED_L_GT_1' for r in ladders[1:])
    assert all(r['full_two_center_gram_status']=='NOT_MEASURED' for r in ladders[1:])

@pytest.mark.parametrize('damage',['missing','positive_sign','unresolved_sign','order'])
def test_bank_rejects_hidden_deletion_and_bad_classification(inputs,damage):
    modes=json.loads((inputs/'BASIS.json').read_text())['modes']
    if damage=='missing':modes.pop()
    if damage=='positive_sign':modes[2]['energy']=-0.1
    if damage=='unresolved_sign':modes[0]['energy']=-1e-15
    if damage=='order':modes[0],modes[1]=modes[1],modes[0]
    with pytest.raises(ValueError):p.bind_bank(p.registry('B0'),modes)

def test_tail_exact_arithmetic_and_preregistered_window_plan():
    c=p.tail_contract();v=c['velocity_au'];points=c['samples']
    assert [p['z_a0'] for p in points]==[-16.,16.,-20.,20.,-24.,24.,-32.,32.]
    assert len({p['query_id'] for p in points})==8
    for row in points:
        z=row['z_a0'];assert row['R_a0']==math.sqrt(2.*2.+z*z)
        assert row['time_au']==z/v and row['time_hex']==float(z/v).hex()
        assert float.fromhex(row['z_hex'])==z
    assert c['operator_only'] and c['new_native_samples_authorized'] is False
    assert c['maximum_future_raw_attempts']==88 and len(c['qualification_ladder'])==11
    assert c['window_preregistration']['nstep']=='USER_APPROVAL_REQUIRED'
    assert c['window_preregistration']['automatic_execution'] is False
    assert c['tail_error_bound'] is None

@pytest.mark.parametrize('action',['native','N3072','full_window','new_basis','b_grid','capture','all_bound'])
def test_forbidden_launches(action):
    with pytest.raises(PermissionError,match='NATIVE_AUTHORIZATION_PENDING'):
        p.forbidden(action)

def test_corrupt_exact_bytes_stop(inputs,tmp_path):
    target=tmp_path/'input';shutil.copytree(inputs,target)
    with (target/'CANDIDATE_N1536.npz').open('ab') as f:f.write(b'corrupt')
    with pytest.raises(ValueError,match='identity'):p.closeout(target)

@pytest.mark.parametrize('metric',['NaN','indefinite','nonhermitian'])
def test_projector_rejects_invalid_metric(metric):
    S=np.eye(18,dtype=complex)
    if metric=='NaN':S[0,0]=np.nan
    if metric=='indefinite':S[0,0]=-1
    if metric=='nonhermitian':S[0,1]=1
    with pytest.raises(ValueError):p.projector(S,np.eye(18)[0])

def test_preparation_native_trap_and_no_nonce(inputs,tmp_path,monkeypatch):
    calls=[]
    def trap(*args,**kwargs):calls.append(args);raise AssertionError('native or process boundary crossed')
    monkeypatch.setattr(ctypes,'CDLL',trap);monkeypatch.setattr(subprocess,'Popen',trap)
    before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs.rglob('*') if f.is_file()}
    result=p.prepare(inputs,tmp_path/'out')
    assert result['native_operator_calls']==0 and result['authorization_nonce_consumed'] is False
    assert not calls
    assert before=={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs.rglob('*') if f.is_file()}
    for name in ['R4O_TEMPORAL_CLOSEOUT.json','FINITE_SPAN_OBSERVABLE.json','R4P0_TAIL_PREFLIGHT_CONTRACT.json','B0_B3_BASIS_REGISTRY_CONTRACT.json','FUTURE_NATIVE_TEMPLATES.json']:
        assert (tmp_path/'out'/name).is_file()
    t=json.loads((tmp_path/'out/FUTURE_NATIVE_TEMPLATES.json').read_text())
    assert t['operator_only']['status']=='USER_APPROVAL_REQUIRED'
    assert all(t['operator_only'][k] is None for k in ['authorization_id','cpus','deadline_unix','wall_seconds','cost_scope'])
    assert result['claim_ceiling']=={'capture':False,'production':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,'continuous_global_supremum_bound':False,'continuous_trajectory_error_bound':False}

def test_cli_native_trap(inputs,tmp_path,monkeypatch,capsys):
    import prepare_closeout as cli
    calls=[]
    def trap(*args,**kwargs):calls.append(args);raise AssertionError('execution boundary')
    monkeypatch.setattr(ctypes,'CDLL',trap);monkeypatch.setattr(subprocess,'Popen',trap)
    assert cli.main(['--inputs',str(inputs),'--out',str(tmp_path/'prepared')])==0
    assert not calls
    assert 'NATIVE_AUTHORIZATION_PENDING' in capsys.readouterr().out
    assert not list(tmp_path.rglob('*CONSUMED*'))

@pytest.mark.parametrize('flag',['--native','--nstep','--b-grid','--capture','--all-bound'])
def test_cli_rejects_science_flags(inputs,tmp_path,flag):
    import prepare_closeout as cli
    with pytest.raises(SystemExit) as error:
        cli.main(['--inputs',str(inputs),'--out',str(tmp_path/'prepared'),flag])
    assert error.value.code==2
    assert not (tmp_path/'prepared').exists()

@pytest.mark.parametrize('damage',['bytes','extra','traversal','duplicate'])
def test_portable_manifest_rejects_corruption(tmp_path,damage):
    import verify_preparation_package as verifier
    import zipfile
    payload={'file.txt':b'fixture'}
    manifest={'files':{'file.txt':{'bytes':7,'sha256':hashlib.sha256(b'fixture').hexdigest()}}}
    if damage=='bytes':payload['file.txt']=b'damaged'
    if damage=='extra':payload['unexpected.txt']=b'x'
    if damage=='traversal':payload['../escape']=b'x'
    path=tmp_path/'fixture.zip'
    with zipfile.ZipFile(path,'w') as z:
        for n,b in payload.items():z.writestr(n,b)
        z.writestr('MANIFEST.json',json.dumps(manifest))
        if damage=='duplicate':
            with pytest.warns(UserWarning):z.writestr('file.txt',b'fixture')
    with pytest.raises(ValueError):verifier.checked_payload(path)

def test_clean_commit_package_preserves_receipts(inputs,tmp_path,monkeypatch):
    import make_preparation_package as maker
    import verify_preparation_package as verifier
    root=tmp_path/'repo';root.mkdir()
    # A portable tree also has generated package payload and compile artifacts;
    # the clean source fixture must contain only source/contracts/receipts.
    source=root/'prep';shutil.copytree(p.HERE,source,ignore=shutil.ignore_patterns(
        '__pycache__','inputs','SOURCE_PINS.json','MANIFEST.json',
        'FUTURE_AUTHORIZATION_TEMPLATE.json','compile_*.pyc'))
    subprocess.run(['git','init','-q',str(root)],check=True)
    subprocess.run(['git','-C',str(root),'add','prep'],check=True)
    subprocess.run(['git','-C',str(root),'-c','user.name=Preparation Test','-c','user.email=preparation@example.invalid','commit','-qm','fixture'],check=True)
    monkeypatch.setattr(maker,'HERE',source)
    result=maker.make(inputs,tmp_path/'prepared.zip')
    manifest,payload=verifier.checked_payload(result['package'])
    assert result['preparation_commit']==manifest['preparation_commit']
    for name in ('FINITE_SPAN_OBSERVABLE.json','R4O_TEMPORAL_CLOSEOUT.json'):
        assert payload['receipts/'+name]==(p.HERE/'receipts'/name).read_bytes()
    template=json.loads(payload['FUTURE_AUTHORIZATION_TEMPLATE.json'])
    assert template['preparation_commit']==result['preparation_commit']
    assert template['source_pins_sha256']==hashlib.sha256(payload['SOURCE_PINS.json']).hexdigest()
    assert template['operator_only']['authorization_id'] is None

@pytest.mark.parametrize('damage',['tree','source_pin','contract_pin','approved_fields'])
def test_package_authority_corruption_rejected(tmp_path,damage):
    import verify_preparation_package as v
    manifest={'preparation_commit':'a'*40,'preparation_tree':'b'*40,'native_authorized':False}
    pins={**manifest,'source_files':{'preflight.py':hashlib.sha256(b'code').hexdigest()}}
    template={**manifest,'source_pins_sha256':'','contract_pins':{'contract.json':hashlib.sha256(b'contract').hexdigest()},
              'operator_only':{'status':'USER_APPROVAL_REQUIRED',**dict.fromkeys(['authorization_id','cpus','workers','worker_ram_bytes','total_ram_cap_bytes','deadline_unix','wall_seconds','termination_grace_seconds','cost_scope'])}}
    payload={'preflight.py':b'code','receipts/contract.json':b'contract','SOURCE_PINS.json':json.dumps(pins).encode()}
    template['source_pins_sha256']=hashlib.sha256(payload['SOURCE_PINS.json']).hexdigest()
    payload['FUTURE_AUTHORIZATION_TEMPLATE.json']=json.dumps(template).encode()
    v.check_authority(manifest,payload)
    if damage=='tree':template['preparation_tree']='c'*40
    if damage=='source_pin':template['source_pins_sha256']='0'*64
    if damage=='contract_pin':template['contract_pins']['contract.json']='0'*64
    if damage=='approved_fields':template['operator_only']['authorization_id']='UNAUTHORIZED'
    payload['FUTURE_AUTHORIZATION_TEMPLATE.json']=json.dumps(template).encode()
    with pytest.raises(ValueError):v.check_authority(manifest,payload)

def test_external_package_pin_rejected_before_replay(tmp_path):
    import verify_preparation_package as v
    package=tmp_path/'wrong.zip';package.write_bytes(b'not the approved bytes')
    with pytest.raises(ValueError,match='external package SHA'):v.verify(package,'0'*64)
