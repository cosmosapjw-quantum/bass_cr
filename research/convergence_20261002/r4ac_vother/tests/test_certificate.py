from fractions import Fraction as F
from dyadic_interval import Interval as I
from vother_certificate import radial_certificate

def test_interior_uniform_density_monopole_and_multipoles():
    # u=1 on [0,2], R=1. Deliberately nonphysical fixture for exact moments.
    k=radial_certificate([0.,2.],[[1.,1.]],[[[0.,0.,0.]]],I.point(1))
    lo,hi=k[0][0][0].fractions()
    assert F(169,100) < lo <= hi < F(17,10)
    assert k[1][0][0].contains(1)
    assert k[2][0][0].contains(F(17,24))
    assert hi-lo<F(1,10**75)

def test_far_field_polynomial_moments():
    # u(r)=r on [0,1], R=2, hence K_L=1/(2^(L+1)*(L+3)).
    k=radial_certificate([0.,1.],[[0.,1.]],[[[0.,0.,0.]]],I.point(2))
    for ell in range(3):assert k[ell][0][0].contains(F(1,2**(ell+1)*(ell+3)))

def test_split_at_exact_mesh_edge_and_refusal():
    import pytest
    a=radial_certificate([0.,1.,2.],[[1.,1.,1.]],[[[0.,0.,0.],[0.,0.,0.]]],I.point(1))
    assert a[1][0][0].contains(1)
    with pytest.raises(ValueError):radial_certificate([0.,1.],[[0.,1.]],[[[0.,0.,0.]]],I.point(0))
    with pytest.raises(ValueError):radial_certificate([0.,1.,2.],[[0.,1.,0.]],[[[0.,0.,0.],[0.,0.,0.]]],I.bounds(F(99,100),F(101,100)))

def test_angular_sign_and_parity_no_projection():
    from vother_certificate import projected_matrix,geometry_interval
    lm=[(0,0),(1,-1),(1,0),(1,1)];ix=[0,0,0,0]
    radial=[[[I.point(1)]] for _ in range(3)]
    R,n=geometry_interval([0.,0.,2.]);v=projected_matrix(radial,lm,ix,n)
    assert v[0][0].contains(-1)
    assert v[2][2].contains(F(-7,5))
    assert v[1][1].contains(F(-4,5))
    _,n2=geometry_interval([0.,0.,-2.]);w=projected_matrix(radial,lm,ix,n2)
    assert (v[0][2]+w[0][2]).contains(0)
    import pytest
    with pytest.raises(ValueError):geometry_interval([1.,1.,1.])
