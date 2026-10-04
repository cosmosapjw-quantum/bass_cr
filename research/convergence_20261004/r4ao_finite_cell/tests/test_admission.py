from pathlib import Path
from fractions import Fraction as F
import json,pytest
from weak_kernel import Candidate,Context,Cell,cover
from finite_adapter import serialize
from dyadic import I
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def model():
    c=Candidate.load(ROOT/'inputs/CANDIDATE.npz',ROOT/'inputs/CANDIDATE.json')
    g=json.loads((ROOT/'inputs/ANCHOR_GEOMETRY.json').read_text())['geometry']
    ctx=Context(F(2),F(float(g['actual_z_a0'])),F(float(g['speed_a0_per_ta'])),F(float(g['time_ta'])))
    cells,_=cover(c,ctx.R);cell=next(x for x in cells if x.kind=='origin_P')
    entry=(4,3,1,-1)
    binding={'candidate':c.identity,'profile':'FINITE_CANDIDATE','cell':cell.dump(),'entry':list(entry),'context':{k:str(getattr(ctx,k)) for k in ('b','z','v','t')},'node_limit':1024}
    return c,cell,ctx,entry,binding

def test_finite_candidate_one_cell_serialize_allowed_only_with_binding(model):
    c,cell,ctx,e,b=model
    text=serialize(c,cell,ctx,e,[(I(F(1,2)),I(F(1,2)),I(1))],b)
    assert text.startswith('R4AN_CELL_V1 256\n2\n')

@pytest.mark.parametrize('key,value',[
 ('candidate','different'),('profile','SYNTHETIC_FIXTURE'),
 ('cell',{'kind':'regular','i':28,'j':0,'triangle':None}),
 ('entry',[4,3,1,1]),('node_limit',2048),('context',{'b':'2','z':'-32','v':'2','t':'-16'})])
def test_serialization_rejects_unbound_candidate_cell_or_epoch(model,key,value):
    c,cell,ctx,e,b=model;b=dict(b);b[key]=value
    with pytest.raises(ValueError):serialize(c,cell,ctx,e,[(I(F(1,2)),I(F(1,2)),I(1))],b)

@pytest.mark.parametrize('u,w,weight',[(F(-1,10),F(1,2),1),(F(1,2),F(11,10),1),(F(1,2),F(1,2),-1)])
def test_outside_reference_domain_or_negative_weight_rejected(model,u,w,weight):
    c,cell,ctx,e,b=model
    with pytest.raises(ValueError):serialize(c,cell,ctx,e,[(I(u),I(w),I(weight))],b)

def test_more_than_1024_nodes_rejected(model):
    c,cell,ctx,e,b=model
    with pytest.raises(ValueError):serialize(c,cell,ctx,e,[(I(0),I(0),I(1))]*1025,b)

def test_original_r4an_guard_is_not_relaxed(model):
    from native_adapter import serialize as original
    c,cell,ctx,e,b=model
    with pytest.raises(ValueError,match='fixture-only'):original(c,cell,ctx,e,[(I(0),I(0),I(1))])

def test_same_identity_wrong_cell_is_not_accepted(model):
    c,cell,ctx,e,b=model;wrong=Cell('origin_P',27,0)
    b=dict(b,cell=wrong.dump())
    with pytest.raises(ValueError,match='registered pilot'):serialize(c,wrong,ctx,e,[(I(0),I(0),I(1))],b)
