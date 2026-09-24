"""CPU tests of real intake/coordinator/gates; no claim of a GPU execution."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest


def module(name):
    try:
        return importlib.import_module('scripts.r3m24_' + name)
    except ModuleNotFoundError as exc:
        pytest.fail(f'corrective module not implemented: {exc.name}')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, sort_keys=True, separators=(',', ':')))


def generation(tmp, label='closest', done=4):
    root = tmp / f'g{done:06d}'
    root.mkdir()
    np.save(root / 'state.npy', np.arange(8).reshape(2, 2, 2).astype(np.complex128))
    meta = dict(config_hash='c'*64, done=done, nstep=32, backend='cupy', norm=1.)
    write(root / 'state.json', meta)
    write(root / 'r3m11_checkpoint_seal.json', dict(schema='R3M11_CHECKPOINT_SEAL_V1',
          source_digest='s'*64, files={'state.npy': digest(root/'state.npy'),
                                     'state.json': digest(root/'state.json')}))
    write(root / 'r3m14_initial_binding.json', dict(status='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED'))
    write(root / 'r3m14_witness_run_receipt.json', dict(done=done, nstep=32))
    files = {p.name: dict(sha256=digest(p), size=p.stat().st_size) for p in root.iterdir()}
    manifest = dict(schema='BASS_CR_R3M17_CHECKPOINT_GENERATION_V1',
                    status='PUBLISHED_VERIFIED_LOCAL', files=files, done=done,
                    nstep=32, config_hash='c'*64, source_digest='s'*64)
    write(root / 'r3m17_generation_manifest.json', manifest)
    spec = dict(label=label, done=done, nstep=32, config_hash='c'*64, source_digest='s'*64,
                backend='cupy', shape=[2, 2, 2], dtype=np.dtype('complex128').str,
                generation_directory=str(root), manifest_sha256=digest(root/'r3m17_generation_manifest.json'),
                expected_state_npy_sha256=digest(root/'state.npy'),
                expected_state_npy_bytes=(root/'state.npy').stat().st_size,
                actual_start_time_au=-1.+done*.125, initial_time_au=-1.,
                actual_dt_au=.125, horizon_au=.5)
    return spec


def plan(tmp):
    a = generation(tmp, 'closest', 4)
    b = generation(tmp, 'outgoing', 12)
    return dict(schema='BASS_CR_R3M24_SAFE_RESTART_V1', computation_key='k'*64,
                windows=[a,b], probe=a, reuse={}, sources={}, root=str(tmp),
                limits=dict(kinetic_matvecs=5000, total_seconds=7200, window_seconds=1800),
                scope='REFERENCE_FOR_STRANG', production_admission=False)


class FakeBackend:
    """Coordinator test double, explicitly not a numerical/GPU oracle."""
    def __init__(self, fail=None):
        self.calls=[]; self.count=0; self.fail=fail
    def probe(self, state):
        state.assert_current(); self.calls.append('probe'); self.count+=3
        return dict(status='PASS', kinetic_matvecs=3)
    def window(self, spec, state):
        state.assert_current(); self.calls.append(spec['label']); self.count+=7
        if spec['label']==self.fail:
            raise RuntimeError('injected second-window failure')
        return dict(label=spec['label'], status='STRANG_SCALE_REFERENCE_CONSISTENT',
                    production_admission=False, checkpoint_sha256=spec['expected_state_npy_sha256'],
                    fft_matvecs=7, evidence='COORDINATOR_TEST_DOUBLE')
    def snapshot(self):
        return dict(kinetic_matvecs=self.count, fft_transforms=2*self.count,
                    wall_seconds=0., backend='CPU_TEST_DOUBLE')
    def close(self): pass


def test_intake_pins_readonly_exact_array(tmp_path):
    g=module('guard'); spec=generation(tmp_path)
    with g.bind_generation(spec) as bound:
        assert np.array_equal(bound.array, np.arange(8).reshape(2,2,2))
        assert not bound.array.flags.writeable
        assert bound.receipt['state_sha256']==spec['expected_state_npy_sha256']
        bound.assert_current()


@pytest.mark.parametrize('target', ['state.npy','state.json','r3m14_initial_binding.json'])
def test_same_size_mutation_rejected(tmp_path, target):
    g=module('guard'); spec=generation(tmp_path)
    p=Path(spec['generation_directory'])/target
    raw=bytearray(p.read_bytes()); raw[-2]^=1; p.write_bytes(raw)
    with pytest.raises(ValueError):
        with g.bind_generation(spec): pass


@pytest.mark.parametrize('change',['replace','in_place','metadata','symlink'])
def test_pinned_input_rechecks_consumption_boundary(tmp_path, change):
    g=module('guard'); spec=generation(tmp_path)
    root=Path(spec['generation_directory'])
    with g.bind_generation(spec) as bound:
        p=root/'state.npy'
        if change=='replace':
            replacement=root/'replacement.npy'; replacement.write_bytes(p.read_bytes()); replacement.replace(p)
        elif change=='in_place':
            with p.open('r+b') as f: f.seek(-1,2); f.write(b'\xff')
        elif change=='metadata':
            (root/'state.json').write_text('{}')
        else:
            p.rename(root/'real.npy'); p.symlink_to(root/'real.npy')
        with pytest.raises(ValueError): bound.assert_current()


def test_manifest_wrong_done_and_config_rejected(tmp_path):
    g=module('guard'); spec=generation(tmp_path)
    for key,value in [('done',8),('config_hash','d'*64),('shape',[2,2,3]),('actual_start_time_au',.4)]:
        bad=dict(spec, **{key:value})
        with pytest.raises(ValueError):
            with g.bind_generation(bad): pass


def test_atomic_json_never_overwrites(tmp_path):
    g=module('guard'); p=tmp_path/'out.json'
    g.publish_json(p,{'value':1}); raw=p.read_bytes()
    with pytest.raises(FileExistsError): g.publish_json(p,{'value':2})
    assert p.read_bytes()==raw


def test_atomic_json_nonfinite_not_published(tmp_path):
    g=module('guard'); p=tmp_path/'out.json'
    with pytest.raises(ValueError): g.publish_json(p, {'bad':float('nan')})
    assert not p.exists()


def test_existing_output_blocks_factory(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'; out.mkdir()
    called=[]
    with pytest.raises(FileExistsError): e.execute(p,out,lambda _:called.append(1))
    assert called==[]


def test_bad_input_blocks_factory(tmp_path):
    e=module('execution'); p=plan(tmp_path); called=[]
    path=Path(p['windows'][1]['generation_directory'])/'state.npy'
    raw=bytearray(path.read_bytes()); raw[-1]^=1; path.write_bytes(raw)
    with pytest.raises(ValueError): e.execute(p,tmp_path/'out',lambda _:called.append(1))
    assert called==[]


def test_second_window_failure_preserves_first(tmp_path):
    e=module('execution'); p=plan(tmp_path); backend=FakeBackend('outgoing'); out=tmp_path/'out'
    with pytest.raises(RuntimeError, match='injected'):
        e.execute(p,out,lambda _:backend)
    first=e.read_window(out/'windows'/'closest',p,p['windows'][0])
    assert first['result']['label']=='closest'
    failure=json.loads((out/'FIRST_FAILURE.json').read_text())
    assert failure['stage']=='WINDOW_outgoing'
    assert len(failure['completed_windows'])==1
    assert failure['work']['kinetic_matvecs']==17
    assert not (out/'COMPLETED.json').exists()


def test_explicit_reuse_avoids_completed_window_work(tmp_path):
    e=module('execution'); p=plan(tmp_path); old=tmp_path/'old'
    with pytest.raises(RuntimeError): e.execute(p,old,lambda _:FakeBackend('outgoing'))
    q=copy.deepcopy(p)
    q['reuse']={'closest':dict(directory=str(old/'windows'/'closest'),
                             manifest_sha256=digest(old/'windows'/'closest'/'MANIFEST.json'))}
    backend=FakeBackend(); result=e.execute(q,tmp_path/'new',lambda _:backend)
    assert backend.calls==['probe','outgoing']
    assert result['reused_labels']==['closest']
    assert result['work']['kinetic_matvecs']==10
    assert result['production_admission'] is False


def test_complete_replay_has_zero_factory_calls(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'
    first=e.execute(p,out,lambda _:FakeBackend()); called=[]
    again=e.execute(p,out,lambda _:called.append(1))
    assert again==first and called==[]


def test_corrupt_completed_result_not_replayed(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'
    e.execute(p,out,lambda _:FakeBackend())
    (out/'windows'/'closest'/'RESULT.json').write_text('{}'); called=[]
    with pytest.raises(ValueError): e.execute(p,out,lambda _:called.append(1))
    assert not called


def test_different_contract_not_replayed(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'
    e.execute(p,out,lambda _:FakeBackend())
    q=copy.deepcopy(p); q['computation_key']='q'*64
    with pytest.raises(ValueError): e.execute(q,out,lambda _:FakeBackend())


def test_all_reused_needs_no_original_arrays_or_backend(tmp_path):
    e=module('execution'); p=plan(tmp_path); old=tmp_path/'old'
    e.execute(p,old,lambda _:FakeBackend())
    q=copy.deepcopy(p)
    q['reuse']={w['label']:dict(directory=str(old/'windows'/w['label']),
                              manifest_sha256=digest(old/'windows'/w['label']/'MANIFEST.json')) for w in q['windows']}
    for w in q['windows']: (Path(w['generation_directory'])/'state.npy').unlink()
    called=[]; result=e.execute(q,tmp_path/'reused',lambda _:called.append(1))
    assert not called and result['work']['kinetic_matvecs']==0


def test_import_execution_never_imports_cupy():
    before=set(sys.modules); module('execution'); module('metrics')
    assert 'cupy' not in set(sys.modules)-before


def trace(n=8, substeps=2, m=8):
    return dict(input_sha256='a'*64, source_key='b'*64, t0=-.5,horizon=.05,
                n=n, action_substeps=substeps, backend='cupy', dtype='<c16',
                basis_dimensions=[m]*(2*n*substeps), matvecs=2*n*substeps*m,
                endpoint_sha256='c'*64)


def test_unchanged_tolerance_is_not_independent():
    m=module('metrics'); a=trace(); b=dict(a, requested_budget=1e-15)
    assert m.repeat_kind(a,b)=='UNCHANGED_WORK_NOT_INDEPENDENT'
    b['endpoint_sha256']='d'*64
    assert m.repeat_kind(a,b)=='SAME_WORK_DIFFERENT_OUTPUT'


def test_changed_substeps_is_independent_work():
    m=module('metrics'); assert m.repeat_kind(trace(),trace(substeps=4))=='CHANGED_WORK'


def test_other_initial_state_is_not_a_repeat():
    m=module('metrics'); b=dict(trace(),input_sha256='d'*64)
    with pytest.raises(ValueError): m.repeat_kind(trace(),b)


def test_incomplete_work_trace_is_not_independent():
    m=module('metrics'); b=trace(); b['basis_dimensions']=[]
    with pytest.raises(ValueError): m.repeat_kind(trace(),b)


def test_known_unchanged_tightening_skips_work():
    m=module('metrics'); actions=[dict(physical_upper_bound=1e-18)]*32
    assert m.tightening_is_unchanged(actions,1e-15) is True
    assert m.tightening_is_unchanged(actions,1e-18) is False


@pytest.mark.parametrize('q,delta',[(0.,1e-8),(.008,8e-6),(1.,1e-25)])
def test_probability_budget_is_stable(q,delta):
    m=module('metrics'); eps=m.state_budget(q,delta)
    assert eps>0
    assert 2*np.sqrt(q)*eps+eps**2==pytest.approx(delta,rel=2e-15,abs=1e-40)


@pytest.mark.parametrize('q,delta',[(-1.,.1),(.1,0.),(.1,float('nan')),(float('inf'),.1)])
def test_bad_probability_budget_rejected(q,delta):
    m=module('metrics')
    with pytest.raises(ValueError): m.state_budget(q,delta)


def test_local_reference_never_closes_global_gate():
    m=module('metrics'); gate=m.strang_gate(1e-5,1e-9,1e-15,'CHANGED_WORK')
    assert gate['status']=='PASS_STRANG_SCALE_ONLY'
    assert gate['GLOBAL_TIME_ERROR']=='NOT_EVALUATED'
    assert gate['production_admission'] is False
    assert m.strang_gate(1e-5,1e-9,0.,'UNCHANGED_WORK_NOT_INDEPENDENT')['status']=='UNRESOLVED_INDEPENDENT_ACTION'


def test_discriminator_is_design_only_and_brackets_zero():
    m=module('metrics'); dt=.01249892352238994
    design=m.discriminator_design(dt,3586,-30.,60.,1152)
    assert design['execution_admission']=='DESIGN_ONLY'
    assert design['B3']['nstep']==7172
    assert design['B3']['actual_dt_au']==dt/2
    assert design['event_window']['t0']<0<design['event_window']['t1']
    assert design['B3']['prediction_is_acceptance_target'] is False
    assert design['event_window']['warmup_steps']>0


def test_source_mutation_rejected_before_backend(tmp_path):
    e=module('execution'); p=plan(tmp_path)
    code=tmp_path/'source.py'; code.write_text('original')
    p['sources']={'source.py':digest(code)}; code.write_text('modified')
    called=[]
    with pytest.raises(ValueError): e.execute(p,tmp_path/'out',lambda _:called.append(1))
    assert not called


def test_required_repeats_are_in_frozen_worst_case():
    gpu=module('gpu')
    assert gpu.required_matvecs(2)==4871
    assert gpu.required_matvecs(1)==2437
    assert gpu.required_matvecs(0)==0


def test_no_gpu_import_when_importing_adapter():
    before=set(sys.modules); module('gpu'); module('cross_window')
    assert 'cupy' not in set(sys.modules)-before


def test_budget_counts_transforms_and_rejects_before_overspend():
    gpu=module('gpu'); b=gpu.Budget(dict(kinetic_matvecs=2,total_seconds=10.,window_seconds=10.))
    b.tick(); b.tick()
    with pytest.raises(TimeoutError): b.tick()
    assert b.count==2 and b.snapshot()['fft_transforms']==4


def test_clock_check_at_terminal_boundary():
    gpu=module('gpu'); now=[0.]
    b=gpu.Budget(dict(kinetic_matvecs=4,total_seconds=10.,window_seconds=2.),clock=lambda:now[0])
    b.begin_window(); b.tick(); now[0]=2.01
    with pytest.raises(TimeoutError): b.end_window()


def test_actual_action_trace_is_preserved():
    gpu=module('gpu')
    infos=[dict(actions=[dict(basis_dimension=3,matvec_count=3,physical_upper_bound=1e-20)]*4,
                total_fft_matvec=12)]*2
    r=gpu.work_trace(dict(label='x',expected_state_npy_sha256='a'*64,
        actual_start_time_au=-.5,horizon_au=.05),'b'*64,2,2,infos,'c'*64,'numpy')
    assert r['basis_dimensions']==[3]*8
    assert r['matvecs']==24
    assert module('metrics').repeat_kind(r,r)=='UNCHANGED_WORK_NOT_INDEPENDENT'


def test_resource_cap_cannot_drop_required_repeat(tmp_path):
    gpu=module('gpu'); p=plan(tmp_path); p['limits']['kinetic_matvecs']=4000
    with pytest.raises(ValueError,match='required'):
        gpu.validate_work_capacity(p,2)


def test_nonpositive_basis_trace_rejected():
    m=module('metrics'); b=trace(); b['basis_dimensions'][0]=0
    with pytest.raises(ValueError): m.repeat_kind(trace(),b)


def test_factory_not_called_when_reuse_manifest_is_corrupt(tmp_path):
    e=module('execution'); p=plan(tmp_path); old=tmp_path/'old'
    e.execute(p,old,lambda _:FakeBackend())
    q=copy.deepcopy(p); q['reuse']={'closest':dict(directory=str(old/'windows'/'closest'),manifest_sha256='0'*64)}
    called=[]
    with pytest.raises(ValueError): e.execute(q,tmp_path/'new',lambda _:called.append(1))
    assert not called


def contract_fixture(tmp_path, monkeypatch):
    m=module('cross_window'); monkeypatch.setattr(m,'ROOT',tmp_path)
    cfg=dict(backend='cupy',dt=.125,energy_keV_per_u=100.,b=2.,z_start=-1.,z_stop=3.,
             grid=dict(dx=.2,xlim=[-1,1],ylim=[-1,1],zlim=[-1,1]))
    selection=dict(actual_dt_au=.125,nstep=32,B2_config_sha256=None,windows=[])
    for label,done in [('incoming',0),('closest',4),('outgoing',12)]:
        selection['windows'].append(dict(label=label,done=done,generation_directory=str(tmp_path/f'g{done:06d}'),
            actual_start_time_au=-1+done*.125,horizon_au=.5,manifest_sha256='1'*64,
            expected_state_npy_sha256='2'*64,expected_state_npy_bytes=16128))
    for path,data in [(m.CONFIG,cfg),(m.SELECTION,selection)]:
        target=tmp_path/path; target.parent.mkdir(parents=True,exist_ok=True); write(target,data)
    selection['B2_config_sha256']=digest(tmp_path/m.CONFIG); write(tmp_path/m.SELECTION,selection)
    strict=tmp_path/m.STRICT; strict.parent.mkdir(parents=True,exist_ok=True); write(strict,dict(all_oracle_resolved=True))
    source={p:digest(tmp_path/p) for p in (m.CONFIG,m.SELECTION,m.STRICT)}
    monkeypatch.setattr(m,'source_snapshot',lambda:source)
    specs=m.canonical_specs(cfg,selection)
    p=dict(schema='BASS_CR_R3M24_SAFE_RESTART_V1',root=str(tmp_path),base_commit=m.BASE,
           config=cfg,sources=source,runtime_identity=m.runtime_identity(),probe=specs[0],windows=specs[1:],reuse={},
           scope='REFERENCE_FOR_STRANG',production_admission=False,
           limits=dict(kinetic_matvecs=5000,total_seconds=7200,window_seconds=1800),
           scientific_settings=m.SCIENTIFIC_SETTINGS.copy(),
           execution_policy='EXPLICIT_CONTRACT_SHA_ONLY_NO_AUTOMATIC_DISPATCH')
    p['computation_key']=m.computation_key(p)
    return m,p


def test_valid_canonical_contract_is_accepted(tmp_path,monkeypatch):
    m,p=contract_fixture(tmp_path,monkeypatch); m.validate_contract(p)


@pytest.mark.parametrize('change',['config','time','probe','settings','cap','key','scope','base'])
def test_mutated_contract_cannot_describe_different_work(tmp_path,monkeypatch,change):
    m,p=contract_fixture(tmp_path,monkeypatch)
    if change=='config': p['config']=dict(p['config'],dt=.01)
    elif change=='time': p['windows'][0]['actual_start_time_au']+=1.
    elif change=='probe': p['probe']['done']=1
    elif change=='settings': p['scientific_settings']['inner_budget']=1e-8
    elif change=='cap': p['limits']['kinetic_matvecs']=999999
    elif change=='key': p['computation_key']='0'*64
    elif change=='scope': p['scope']='GLOBAL_TIME_ERROR'
    else: p['base_commit']='0'*40
    with pytest.raises(ValueError): m.validate_contract(p)


def test_backend_cleanup_failure_not_marked_complete(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'
    class BadClose(FakeBackend):
        def close(self): raise RuntimeError('injected cleanup failure')
    with pytest.raises(RuntimeError,match='cleanup'): e.execute(p,out,lambda _:BadClose())
    assert not (out/'COMPLETED.json').exists()
    assert (out/'FIRST_FAILURE.json').exists()


def test_backend_cleanup_never_masks_first_error(tmp_path):
    e=module('execution'); p=plan(tmp_path); out=tmp_path/'out'
    class BadClose(FakeBackend):
        def close(self): raise RuntimeError('cleanup should not mask')
    with pytest.raises(RuntimeError,match='injected second-window'):
        e.execute(p,out,lambda _:BadClose('outgoing'))
    assert json.loads((out/'FIRST_FAILURE.json').read_text())['message']=='injected second-window failure'


def test_retained_array_view_cannot_become_dangling_after_context(tmp_path):
    import subprocess
    spec=generation(tmp_path)
    script=('import json; from scripts.r3m24_guard import bind_generation\n'
            f'spec=json.loads({json.dumps(json.dumps(spec))})\n'
            'with bind_generation(spec) as pinned:\n    retained=pinned.array\n'
            'assert retained[0,0,0] == 0\nprint(repr(retained.shape))\n')
    proc=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True)
    assert proc.returncode==0, f'mmap lifetime subprocess exited {proc.returncode}: {proc.stderr}'


def test_contract_runtime_change_rejected(tmp_path,monkeypatch):
    m,p=contract_fixture(tmp_path,monkeypatch)
    p['runtime_identity']=dict(m.runtime_identity(),numpy='different-version')
    with pytest.raises(ValueError): m.validate_contract(p)


def test_runtime_identity_participates_in_reuse_key(tmp_path,monkeypatch):
    m,p=contract_fixture(tmp_path,monkeypatch)
    old=m.computation_key(p)
    p['runtime_identity']=dict(p['runtime_identity'],numpy='another-version')
    assert m.computation_key(p)!=old
