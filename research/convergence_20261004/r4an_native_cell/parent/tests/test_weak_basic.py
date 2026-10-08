from fractions import Fraction as F
import pytest
from dyadic import I
from weak_kernel import Candidate,origin_field,Context,Cell,kernel,cover
from moments import P,U,V
from complex_box import C

def candidate():
    # Two modes, compact C0 polynomial; remote panels are explicitly supplied.
    edges=(F(0),F(1,8),F(1),F(2),F(4),F(8))
    # F=u/r near r=0: a nonzero p slope, deliberately not smoothed.
    co=((F(0),F(1),F(1,3),F(-1,5),F(0)),)+( (F(1,10),F(-1,20),F(1,30),F(0),F(0)), )*4
    return Candidate(edges,(co,co),(0,1),'synthetic-origin')

def test_origin_scaled_gradient_preserves_nonzero_p_slope():
    c=candidate();n=[U,V,P(0)]
    val,rg=origin_field(c,1,F(0),n,0)
    # p_z has zero value on the equatorial ring, but nonzero tangent gradient.
    assert rg[2].evaluate(1,0).re.contains(8*I(3).sqrt().mid())
    assert rg[0].evaluate(1,0).re.contains(0)

@pytest.mark.parametrize('side',['origin_T','origin_P'])
@pytest.mark.parametrize('la',[0,1])
@pytest.mark.parametrize('lb',[0,1])
def test_origin_kernel_zero_radius_finite_zero(side,la,lb):
    c=candidate();ct=Context(F(1),F(3),F(2),F(3,2))
    cell=Cell(side,0 if side=='origin_T' else 3,3 if side=='origin_T' else 0)
    ks=kernel(c,cell,ct,F(0),F(2,5),la,lb,0,0).value()
    for x in ks.values():assert x.re.iszero() and x.im.iszero()

def test_bad_origin_trace_rejected():
    c=candidate();co=[list(x) for x in c.coeffs];row=list(co[0]);row[0]=(F(1),)+row[0][1:];co[0]=row
    b=Candidate(c.edges,tuple(tuple(x) for x in co),c.ells,'bad')
    with pytest.raises(ValueError,match='zero trace'):b.first_F(0,F(0))
