from fractions import Fraction as F
from weak_kernel import Candidate,Context,Cell,kernel
from geometry import Triangle,Affine
from complex_box import C
from dyadic import I
import native_adapter

def fixture():
    edges=tuple(map(F,(0,1,2,4,8)))
    rows=tuple((lo,hi-lo,F(0),F(0),F(0)) for lo,hi in zip(edges,edges[1:]))
    c=Candidate(edges,(rows,rows),(0,1),'R4AN_MANUFACTURED_U_EQUALS_R')
    tri=Triangle(2,3,((Affine(F(2)),Affine(F(4))),(Affine(F(3)),Affine(F(4))),(Affine(F(3)),Affine(F(5)))),(F(1),F(0),F(0)))
    return c,Cell('regular',2,3,tri),Context(3,4,0,0)

def test_native_regular_ss_executes_real_kernel():
    c,cell,ctx=fixture()
    got=native_adapter.evaluate(c,cell,ctx,(0,0,0,0),[(I(F(1,3)),I(F(2,5)),I(1))])
    assert isinstance(got,dict), 'native single-cell weak evaluator is not implemented'
    ref=kernel(c,cell,ctx,F(1,3),F(2,5),0,0,0,0).value()
    for key in ref:
        assert got[key].re.contains_interval(ref[key].re) or ref[key].re.contains_interval(got[key].re)
        assert got[key].im.contains_interval(ref[key].im) or ref[key].im.contains_interval(got[key].im)

import pytest

@pytest.mark.parametrize('chart', ['regular','origin_T','origin_P'])
@pytest.mark.parametrize('left',[(0,0),(1,-1),(1,0),(1,1)])
@pytest.mark.parametrize('right',[(0,0),(1,-1),(1,0),(1,1)])
def test_nonzero_etf_all_sp_pairs(chart,left,right):
    c,cell,_=fixture()
    # Nonconstant smooth radial fixture; not the physical candidate.
    coeff=[]
    for lo,hi in zip(c.edges,c.edges[1:]):
        dd=hi-lo
        # u(r) = r + r^2/7 + r^3/13, coefficients in local s.
        coeff.append((lo+lo**2/7+lo**3/13,dd*(1+2*lo/7+3*lo**2/13),dd**2*(F(1,7)+3*lo/13),dd**3/13,F(0)))
    c=Candidate(c.edges,(tuple(coeff),tuple(coeff)),(0,1),'R4AN_NONLINEAR_FIXTURE')
    if chart=='origin_T':cell=Cell(chart,0,3)
    elif chart=='origin_P':cell=Cell(chart,3,0)
    ctx=Context(3,4,F(7,9),F(11,7))
    entry=(left[0],right[0],left[1],right[1]);u=I(F(2,7));w=I(F(3,8))
    got=native_adapter.evaluate(c,cell,ctx,entry,[(u,w,I(1))])
    ref=kernel(c,cell,ctx,C(u),C(w),*entry).value()
    for key in ref:
        for x,y in ((got[key].re,ref[key].re),(got[key].im,ref[key].im)):
            assert max(x.lo,y.lo)<=min(x.hi,y.hi),(chart,entry,key,x,y)
            assert abs(x.mid()-y.mid())<F(1,10**60)

@pytest.mark.parametrize('chart',['origin_T','origin_P'])
@pytest.mark.parametrize('m',[-1,0,1])
def test_zero_radius_scaled_gradient_is_finite(chart,m):
    c,_,ctx=fixture();cell=Cell(chart,0,3) if chart=='origin_T' else Cell(chart,3,0)
    vals=native_adapter.evaluate(c,cell,ctx,(1,1,m,m),[(I(0),I(F(1,2)),I(1))])
    for x in vals.values():assert x.re.contains(0) and x.im.contains(0)

@pytest.mark.parametrize('fragment,replacement',[
 ('R4AN_CELL_V1 256','R4AN_CELL_V1 128'),
 ('R4AN_CELL_V1','R4AN_BAD_SCHEMA'),
])
def test_native_schema_and_precision_fail_closed(fragment,replacement):
    c,cell,ctx=fixture();text=native_adapter.serialize(c,cell,ctx,(0,0,0,0),[(I(F(1,3)),I(F(2,5)),I(1))])
    with pytest.raises(RuntimeError):native_adapter.invoke(text.replace(fragment,replacement,1))

def test_native_truncated_and_extra_data_rejected():
    c,cell,ctx=fixture();s=native_adapter.serialize(c,cell,ctx,(0,0,0,0),[(I(F(1,3)),I(F(2,5)),I(1))])
    with pytest.raises(RuntimeError):native_adapter.invoke(s[:len(s)//2])
    with pytest.raises(RuntimeError):native_adapter.invoke(s+'EXTRA\n')

@pytest.mark.parametrize('samples',[[],[(I(-1),I(0),I(1))],[(I(0),I(2),I(1))],[(I(0),I(0),I(-1))]])
def test_adapter_bad_sample_rejected(samples):
    c,cell,ctx=fixture()
    with pytest.raises(ValueError):native_adapter.evaluate(c,cell,ctx,(0,0,0,0),samples)

@pytest.mark.parametrize('entry',[(0,0,1,0),(5,0,0,0),(0,1,0,2),(0,0,0.0,0)])
def test_entry_validation(entry):
    c,cell,ctx=fixture()
    with pytest.raises(ValueError):native_adapter.evaluate(c,cell,ctx,entry,[(I(0),I(0),I(1))])

def test_actual_atomic_candidate_requires_separate_execution_contract():
    c,cell,ctx=fixture();c=Candidate(c.edges,c.coeffs,c.ells,c.identity,profile='FINITE_CANDIDATE')
    with pytest.raises(ValueError,match='fixture-only'):
        native_adapter.evaluate(c,cell,ctx,(0,0,0,0),[(I(F(1,3)),I(F(2,5)),I(1))])
