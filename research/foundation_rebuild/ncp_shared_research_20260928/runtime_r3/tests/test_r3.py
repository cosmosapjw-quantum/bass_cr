"""New R3 tests only. Synthetic seams + the admitted archive, never native science."""
from __future__ import annotations
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
PREFIX = 'research.foundation_rebuild.ncp_shared_research_20260928.runtime_r3'


def api():
    from research.foundation_rebuild.ncp_shared_research_20260928.runtime_r3 import integrity, cache_bridge, metric_diagnostics, run_cache_audit
    return integrity, cache_bridge, metric_diagnostics, run_cache_audit


@pytest.fixture(scope='session')
def evidence():
    _, b, _, _ = api()
    inputs=b.load_inputs(ROOT)
    return inputs,b.CacheArchive.from_inputs(inputs)


def make_zip(members):
    with io.BytesIO() as stream:
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
            for n,b in members:z.writestr(n,b)
        return stream.getvalue()


def changed(cache, mutate):
    i,b,_,_=api()
    members=dict(cache.members)
    mutate(members)
    raw=make_zip(sorted(members.items()))
    return b.CacheArchive(raw,context=cache.context,numerical_identity=cache.numerical_identity,
                          sha256=i.sha(raw),byte_count=len(raw),pair_count=len(cache.records),
                          expected_shapes=cache.expected_shapes)


def edit_record(members, callback):
    i,_,_,_=api()
    n=next(n for n in sorted(members) if n.startswith('operator_tasks/') and n.endswith('.json'))
    r=i.strict_json(members[n]);callback(r);r.pop('receipt_sha256',None)
    r['receipt_sha256']=i.sha(i.canonical(r));members[n]=i.canonical(r)+b'\n'


def test_admitted_cache_is_complete(evidence):
    inp,c=evidence
    assert len(c.records)==297 and c.audit['array_count']==2673
    assert inp.documents['r2_report']['status']=='F1_ENGINE_ADMISSION_PASS'
    assert c.audit['invalid_tasks']==0


def test_native_callback_not_part_of_adapter(evidence):
    _,c=evidence
    assert not hasattr(c,'native_evaluator')
    r=next(iter(c.records.values()))
    arrays=c.evaluate(r['time_hex'],r['order'],r['subdivisions'])
    assert set(arrays)=={'raw','full'} and arrays['full']['S'].shape==(18,18)
    assert not arrays['full']['S'].flags.writeable


def test_two_fresh_directories_preserve_bytes_and_identity(evidence,tmp_path):
    _,c=evidence
    a=c.import_to(tmp_path/'a',expected_identity=c.numerical_identity)
    b=c.import_to(tmp_path/'b',expected_identity=c.numerical_identity)
    assert a.numerical_identity==b.numerical_identity
    for n,raw in c.members.items():
        assert (tmp_path/'a'/n).read_bytes()==raw==(tmp_path/'b'/n).read_bytes()
    r=next(iter(c.records.values()))
    assert a.evaluate(r['time_hex'],r['order'],r['subdivisions'])['full']['S'].tobytes()==b.evaluate(r['time_hex'],r['order'],r['subdivisions'])['full']['S'].tobytes()


@pytest.mark.parametrize('field',['basis','model','source_closure_sha256','engine','generation_environment','quadrature_policy','dtype'])
def test_identity_drift_is_blocked_before_destination_creation(evidence,tmp_path,field):
    i,_,_,_=api();_,c=evidence
    identity=copy.deepcopy(c.numerical_identity);identity[field]='changed'
    with pytest.raises(i.AuditError,match='R3_NUMERICAL_CONTEXT_MISMATCH'):
        c.import_to(tmp_path/'blocked',expected_identity=identity)
    assert not (tmp_path/'blocked').exists()


def test_numerical_descriptor_excludes_output_path_only(evidence):
    _,b,_,_=api();inp,_=evidence
    one=copy.deepcopy(inp.documents['engine_identity']);two=copy.deepcopy(one)
    two['argv'][-1]='/another/new/libmoments.so';two['identity_sha256']='different_legacy_digest'
    assert b.numerical_descriptor(inp,one)==b.numerical_descriptor(inp,two)
    two['library_sha256']='0'*64
    assert b.numerical_descriptor(inp,one)!=b.numerical_descriptor(inp,two)


def test_existing_output_is_unchanged(evidence,tmp_path):
    _,c=evidence
    out=tmp_path/'exists';out.mkdir();(out/'marker').write_bytes(b'keep')
    with pytest.raises(FileExistsError):c.import_to(out,expected_identity=c.numerical_identity)
    assert list(out.iterdir())==[out/'marker'] and (out/'marker').read_bytes()==b'keep'


@pytest.mark.parametrize('t,q,h',[('nan',40,1),('inf',40,1),('0.0',40,1),('0x0.0p+0',True,1),('0x0.0p+0',40.1,1),('0x0.0p+0',40,0)])
def test_bad_task_identity_rejected(evidence,t,q,h):
    i,_,_,_=api();_,c=evidence
    with pytest.raises(i.AuditError):c.evaluate(t,q,h)


def test_exact_time_cache_miss_has_no_fallback(evidence):
    i,_,_,_=api();_,c=evidence
    with pytest.raises(i.AuditError,match='R3_CACHE_MISS_NO_FALLBACK'):
        c.evaluate(float.fromhex('0x0.0000000000001p-1022').hex(),40,1)


def test_top_level_hash_mismatch(evidence):
    i,b,_,_=api();inp,c=evidence
    with pytest.raises(i.AuditError,match='SHA_SIZE'):
        b.CacheArchive(inp.payloads['cache_archive']+b'x',context=c.context,numerical_identity=c.numerical_identity,sha256=inp.pins['files']['cache_archive']['sha256'],byte_count=inp.pins['files']['cache_archive']['bytes'],expected_shapes=c.expected_shapes)


def test_missing_task_pair_member(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):m.pop(next(n for n in m if n.endswith('.npz')))
    with pytest.raises(i.AuditError,match='PAIR'):changed(c,mutate)


def test_receipt_payload_hash_mismatch(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):edit_record(m,lambda r:r.update(payload_sha256='0'*64))
    with pytest.raises(i.AuditError,match='PAYLOAD'):changed(c,mutate)


def test_context_drift_inside_receipt(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):edit_record(m,lambda r:r['context'].update(engine_identity_sha256='0'*64))
    with pytest.raises(i.AuditError,match='CONTEXT'):changed(c,mutate)


def test_rehashed_receipt_time_drift(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):edit_record(m,lambda r:r.update(time_hex='0x1.0p+30'))
    with pytest.raises(i.AuditError,match='TASK_ID'):changed(c,mutate)


def test_dtype_metadata_tamper(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):edit_record(m,lambda r:r['arrays']['full__S'].update(dtype='float64'))
    with pytest.raises(i.AuditError,match='ARRAY'):changed(c,mutate)


def test_receipt_digest_is_not_optional(evidence):
    i,_,_,_=api();_,c=evidence
    def mutate(m):
        n=next(n for n in m if n.startswith('operator_tasks/') and n.endswith('.json'))
        r=i.strict_json(m[n]);r.pop('receipt_sha256');m[n]=i.canonical(r)
    with pytest.raises(i.AuditError,match='RECEIPT'):changed(c,mutate)


@pytest.mark.parametrize('name',['../escape','/absolute','a//b','a/./b','C:/drive','a\\b'])
def test_unsafe_zip_path(name):
    i,_,_,_=api()
    with pytest.raises(i.AuditError,match='ZIP'):i.read_zip(make_zip([(name,b'x')]),max_bytes=100,max_members=10)


def test_duplicate_zip_entries():
    i,_,_,_=api()
    with pytest.warns(UserWarning):raw=make_zip([('x',b'a'),('x',b'b')])
    with pytest.raises(i.AuditError,match='DUPLICATE'):i.read_zip(raw,max_bytes=100,max_members=10)


def test_zip_memory_budget():
    i,_,_,_=api()
    with pytest.raises(i.AuditError,match='BUDGET'):i.read_zip(make_zip([('x',b'x'*1000)]),max_bytes=500,max_members=10)


@pytest.mark.parametrize('raw',[b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}'])
def test_strict_json_rejects_ambiguous_values(raw):
    i,_,_,_=api()
    with pytest.raises(i.AuditError):i.strict_json(raw)


def test_npy_shape_budget_checked_before_allocation():
    i,_,_,_=api();stream=io.BytesIO()
    np.lib.format.write_array_header_1_0(stream,{'descr':'<c16','fortran_order':False,'shape':(10**10,10**10)})
    with pytest.raises(i.AuditError,match='ARRAY'):i.read_npy(stream.getvalue(),shape=(18,18),dtype='<c16')


def test_imported_file_tamper(evidence,tmp_path):
    i,_,_,_=api();_,c=evidence
    imported=c.import_to(tmp_path/'fresh',expected_identity=c.numerical_identity)
    rec=next(iter(c.records.values()))
    p=tmp_path/'fresh'/'operator_tasks'/(rec['task_id']+'.npz');p.write_bytes(p.read_bytes()+b'x')
    with pytest.raises(i.AuditError,match='IMPORTED'):imported.evaluate(rec['time_hex'],rec['order'],rec['subdivisions'])


def test_inherited_metric_residuals_reconstructed(evidence):
    _,_,m,_=api();inp,c=evidence
    out=m.from_cache(c,inp.documents['sentinels'],inp.documents['f1_contract'])
    assert len(out['sentinels'])==5
    assert out['continuous_global_supremum_bound']=='NOT_CERTIFIED'
    for row,old in zip(out['sentinels'],inp.documents['sentinels']['sentinels']):
        assert row['relative_residual']==pytest.approx(old['relative_residual'],rel=1e-8,abs=1e-20)
        assert row['whitened_total_spectral_norm']>=0 and row['h_hermiticity_gate_pass']


def test_whitening_direction_noncommuting_complex_matrices():
    _,_,m,_=api()
    C=np.array([[1.3,.2+.4j],[0,2.1]],complex);S=C.conj().T@C
    R=np.array([[.2,.1-.3j],[.1+.3j,-.4]])
    W=m.whiten(S,R)
    ci=np.linalg.inv(C)
    np.testing.assert_allclose(W,ci.conj().T@R@ci,rtol=1e-13,atol=1e-14)
    wrong=ci@R@ci.conj().T
    assert np.linalg.norm(W-wrong)>1e-3


def test_nonhermitian_h_term_not_silently_dropped():
    _,_,m,_=api()
    S=np.eye(2,dtype=complex);D=np.zeros((2,2),complex);H=np.array([[0.,1.],[0.,0.]],complex)
    row=m.matrix_diagnostics(S,S,S,D,H,epsilon_t=.1,hbar_scaled=2.,hermiticity_gate=1e-11)
    assert not row['h_hermiticity_gate_pass']
    assert row['whitened_connection_spectral_norm']==0
    assert row['whitened_total_spectral_norm']==pytest.approx(.5)


@pytest.mark.parametrize('case',['indefinite','nonhermitian','nonfinite'])
def test_invalid_metric_matrix_rejected(case):
    i,_,m,_=api();S=np.eye(2,dtype=complex)
    if case=='indefinite':S[0,0]=-1
    if case=='nonhermitian':S[0,1]=1j
    if case=='nonfinite':S[0,0]=np.nan
    with pytest.raises(i.AuditError):m.whiten(S,np.eye(2))


def test_source_dependency_drift_rejected(evidence,tmp_path):
    i,b,_,_=api();inp,_=evidence
    # The production reader checks role file hashes before semantic admission.
    data=tmp_path/'repo'; data.mkdir()
    pin=inp.pins['files']['f1_contract'];p=data/pin['path'];p.parent.mkdir(parents=True);p.write_bytes(b'{}')
    with pytest.raises(i.AuditError):b.load_inputs(data)


def test_cli_help_is_import_safe():
    r=subprocess.run([sys.executable,'-m',PREFIX+'.run_cache_audit','--help'],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0 and '--out' in r.stdout and '--repo-root' in r.stdout


def test_cli_complete_no_legacy_native_import(evidence,tmp_path):
    _,_,_,runner=api()
    before=set(sys.modules)
    assert runner.main(['--repo-root',str(ROOT),'--out',str(tmp_path/'run')])==0
    report=json.loads((tmp_path/'run/R3_RETURN.json').read_text())
    assert report['status']=='R3_CACHE_REUSE_AND_METRIC_AUDIT_COMPLETE'
    assert report['new_native_evaluations']==0 and report['capture_execution_allowed'] is False
    assert report['cache']['task_pairs']==297
    new=set(sys.modules)-before
    assert not any('ncloud_f1_engine_admission' in n or 'runtime_r2.worker' in n for n in new)
    assert (tmp_path/'run/OUTPUT_MANIFEST.json').is_file()


def test_cli_failure_preserves_first_failure(tmp_path):
    _,_,_,runner=api()
    assert runner.main(['--repo-root',str(tmp_path/'missing'),'--out',str(tmp_path/'failure')])==3
    report=json.loads((tmp_path/'failure/R3_RETURN.json').read_text())
    assert report['status']=='R3_BLOCKED' and report['first_failure'] is not None
    assert report['new_native_evaluations']==0


def test_cli_existing_output_never_overwrites(tmp_path):
    _,_,_,runner=api();p=tmp_path/'out';p.mkdir();(p/'R3_RETURN.json').write_text('original')
    assert runner.main(['--repo-root',str(ROOT),'--out',str(p)])==3
    assert (p/'R3_RETURN.json').read_text()=='original'


def test_returned_snapshot_cannot_be_made_writable(evidence):
    _,c=evidence
    r=next(iter(c.records.values()))
    a=c.evaluate(r['time_hex'],r['order'],r['subdivisions'])['full']['S']
    with pytest.raises(ValueError):a.setflags(write=True)


def test_reader_version_drift_blocks_without_install(monkeypatch):
    i,_,_,runner=api()
    monkeypatch.setattr(np,'__version__','UNAPPROVED_VERSION')
    with pytest.raises(i.AuditError,match='R3_READER_ENVIRONMENT'):runner.reader_environment()


def test_zip_symlink_is_rejected():
    i,_,_,_=api()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        item=zipfile.ZipInfo('link');item.create_system=3;item.external_attr=0o120777 << 16
        z.writestr(item,b'/outside')
    with pytest.raises(i.AuditError,match='ZIP_TYPE'):i.read_zip(stream.getvalue(),max_bytes=1000,max_members=10)
