from pathlib import Path
from fractions import Fraction as F
import json,pytest
import pilot

def base(tmp_path):
    return {'schema':'R4AO_FINITE_CANDIDATE_SINGLE_CELL_V1','source_root':str(pilot.ROOT),'method':dict(pilot.METHOD),'caps':dict(pilot.CAPS),'resources':dict(pilot.RESOURCES),'units':{'S':'1','H':'Eh','D':'ta^-1','K':'Eh','ta':'hbar/Eh'}}

@pytest.mark.parametrize('group,key,value',[
('method','degree',64),('method','rho','3'),('method','subdivisions',1),('method','complex_L1_target','1e-12'),('method','precision_fractional_bits',128),
('caps','cells',2),('caps','channel_pairs',2),('caps','native_attempts',2),('caps','candidate_geometries',2),('caps','full_matrix_calls',1),('caps','root_finder_calls',1),('caps','native_nodes',2048),('caps','historical_replays',1),('caps','complex_majorant_calls',3),
('resources','native_memory_limit_bytes',1),('resources','native_wall_seconds',240),('resources','total_wall_seconds',840),('units','K','eV')])
def test_policy_change_rejected_before_native(tmp_path,monkeypatch,group,key,value):
    c=base(tmp_path);c[group][key]=value
    f=tmp_path/'contract.json';f.write_text(json.dumps(c))
    def forbidden(*args,**kwargs):pytest.fail('native boundary reached')
    monkeypatch.setattr(pilot.subprocess,'run',forbidden)
    with pytest.raises(ValueError):pilot.run(f,pilot.sha(f))
    assert not (tmp_path/'RESERVATION.json').exists()

def test_contract_hash_rejected_first(tmp_path):
    f=tmp_path/'c.json';f.write_text('{}')
    with pytest.raises(ValueError,match='contract hash'):pilot.validate({},f,'0'*64)

@pytest.mark.parametrize('available,cpu,fixture',[(0,'4',False),(2**34,'0',False),(2**34,'4',True)])
def test_no_fake_or_insufficient_resource_admission(available,cpu,fixture):
    d={'fixture':fixture,'profile':'OBSERVED_LOCAL_SESSION_VISIBLE_CGROUP_PLUS_NATIVE_RLIMIT','visible_available_bytes':available,'cpu_capacity':cpu}
    with pytest.raises((ValueError,RuntimeError)):pilot.admit(d)

def test_saved_rule_reuse_has_no_finder(monkeypatch):
    import quadrature
    monkeypatch.setattr(quadrature,'certified_rule',lambda n:pytest.fail('root finder must not run'))
    samples=pilot.rule()
    assert len(samples)==1024
    s=sum((x[2] for x in samples),pilot.ZERO)
    assert s.contains(1)
    assert all(0<u.lo<=u.hi<pilot.SCALE and 0<w.lo<=w.hi<pilot.SCALE for u,w,_ in samples)

def test_actual_candidate_and_anchor_locked():
    c,cell,ctx=pilot.model()
    assert c.profile=='FINITE_CANDIDATE' and c.ells==(0,0,0,1,1)
    assert c.identity==pilot.CANDIDATE and cell.dump()=={'kind':'origin_P','i':28,'j':0,'triangle':None}
    assert ctx.b==2 and ctx.z==-32
    assert ctx.t != ctx.z/ctx.v  # no silent epoch substitution

def test_completed_production_contract_cannot_be_replayed(monkeypatch):
    path=pilot.ROOT/'contracts/PILOT_v1.json'
    if not path.exists():pytest.skip('post-execution guard check')
    c=json.loads(path.read_text())
    if not Path(c['output']).exists():pytest.skip('post-execution guard check')
    monkeypatch.setattr(pilot.subprocess,'run',lambda *a,**k:pytest.fail('native reached on replay'))
    with pytest.raises(ValueError,match='consumed'):
        pilot.validate(c,path,pilot.sha(path))
