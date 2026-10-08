from pathlib import Path
import json,zipfile
import numpy as np
import pytest
import qualification_runtime as qr
import verified_import as vi
from runtime import save_bank
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from cr_repro.observables import projectile_speed_au

@pytest.fixture
def previous(tmp_path):
    source=tmp_path/'old';source.mkdir()
    spec=dict(radius=4.,elements=4,degree=4,lmax=0,bound_nmax=1,positive_per_l=0)
    bank=atomic_bank(RadialSpec(**spec));basis=save_bank(source,bank)
    cfg={'energy_keV_per_u':100.,'b_a0':2.,'epsilon_z_a0':1e-4,'phase_budget_rad':24.,'phase_order':24,
         'reference_orders':[32,40,48,56,64],'same_center_order':20,'radial_spec':spec,
         'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9},'z_samples_a0':[-4.,-2.]}
    pins={'source_manifest_sha256':'manifest','dependency_pins_sha256':'dependencies'}
    context={'contract':cfg,'basis_identity':basis['identity'],'native_library_sha256':'native','source_pins':pins}
    cid=qr._digest(context);tid=qr.task_identity('phase24',-2.,0.,context)
    s=np.array([[1.,.1],[.1,1.]],complex);h=np.array([[-.5,.01],[.01,.3]],complex);d=np.array([[0.,.03j],[0.,.2j]],complex)
    arrays={'S':s,'H':h,'D':d}
    cross={k:arrays[k[0]][0:1,1:2].copy() if k.endswith('tp') else arrays[k[0]][1:2,0:1].copy() for k in qr.CROSS_KEYS}
    rec={'task_id':tid,'context_id':cid,'method':'phase24','reference_order':None,'z_center_a0':-2.,'dz_a0':0.,
         'time_ta':-2./projectile_speed_au(100.),'channel_count':2,'metadata':{'radial_order':24,'phase_budget_rad':24.},
         'diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':.8}}
    qr.save_task(source,rec,{'full':arrays,'cross':cross})
    qr._write_json(source/'INTAKE.json',{'context':context,'context_id':cid})
    qr._write_json(source/'RETURN_REPORT.json',{'execution_head':'test-commit','status':'NUMERICAL_SCREEN_FAILED'})
    archive=source.with_name(source.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x') as z:
        for p in source.rglob('*'):
            if p.is_file():z.write(p,str(p.relative_to(source)))
    grant={'execution_head':'test-commit','report_sha256':qr.sha(source/'RETURN_REPORT.json'),
        'archive_sha256':qr.sha(archive),'contract_digest':qr._digest(cfg),'source_pins':pins}
    return source,grant,cfg,tid


def test_verified_import_reuses_npz_bytes_without_changing_old_failure(previous,tmp_path):
    src,grant,cfg,oldtid=previous;oldreport=(src/'RETURN_REPORT.json').read_bytes()
    validated,bank,basis=vi.validate_previous_run(src,grant,'native',cfg)
    newcfg=dict(cfg,candidate_orders=[24,32,40])
    newctx={'contract':newcfg,'basis_identity':basis['identity'],'native_library_sha256':'native','source_pins':{'new':'pins'}}
    bridge=vi.import_tasks(validated,tmp_path/'new',newctx)
    assert bridge['count']==1 and bridge['new_scientific_evaluations']==0
    newtid=bridge['imported_tasks'][0]['new_task_id']
    assert newtid!=oldtid
    assert (src/'tasks'/f'{oldtid}.npz').read_bytes()==(tmp_path/'new/tasks'/f'{newtid}.npz').read_bytes()
    assert (src/'RETURN_REPORT.json').read_bytes()==oldreport
    rec,_=qr.load_task(tmp_path/'new',newtid,qr._digest(newctx))
    assert rec['provenance']['source_task_id']==oldtid
    assert bridge['old_failure_preserved'] is True


def test_import_rejects_wrong_native_binary(previous):
    src,grant,cfg,_=previous
    with pytest.raises(ValueError,match='native'):
        vi.validate_previous_run(src,grant,'different-library',cfg)


def test_import_rejects_changed_physics(previous):
    src,grant,cfg,_=previous
    with pytest.raises(ValueError,match='rule changed'):
        vi.validate_previous_run(src,grant,'native',dict(cfg,epsilon_z_a0=2e-4))


def test_archive_hash_and_directory_bytes_are_both_checked(previous):
    src,grant,cfg,_=previous
    (src/'BASIS.npz').write_bytes((src/'BASIS.npz').read_bytes()+b'x')
    with pytest.raises(ValueError,match='differs from authorized archive'):
        vi.validate_previous_run(src,grant,'native',cfg)


def test_import_rejects_unreported_archive(previous):
    src,grant,cfg,_=previous
    archive=src.with_name(src.name+'_RETURN.zip');archive.write_bytes(archive.read_bytes()+b'x')
    with pytest.raises(ValueError,match='archive SHA'):
        vi.validate_previous_run(src,grant,'native',cfg)


def test_import_refuses_overwrite(previous,tmp_path):
    src,grant,cfg,_=previous
    p,bank,basis=vi.validate_previous_run(src,grant,'native',cfg)
    ctx={'contract':cfg,'basis_identity':basis['identity'],'native_library_sha256':'native','source_pins':{}}
    vi.import_tasks(p,tmp_path/'new',ctx)
    with pytest.raises(FileExistsError):vi.import_tasks(p,tmp_path/'new',ctx)
