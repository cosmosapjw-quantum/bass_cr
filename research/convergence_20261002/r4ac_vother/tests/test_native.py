import pytest,numpy as np
from fractions import Fraction as F
from native_vother import build,Native,angular_matrix
from vother_certificate import radial_certificate,geometry_interval,projected_matrix
from dyadic_interval import Interval as I,error_upper

@pytest.fixture(scope='module')
def native(tmp_path_factory):return Native(build(tmp_path_factory.mktemp('build')/'native'))

def test_native_uniform_and_polynomial(native):
    k=native.radial([0.,2.],[[1.,1.]],[[[0.,0.,0.]]],1.,32)
    assert abs(k[0,0,0]-(1+np.log(2)))<1e-14
    assert abs(k[1,0,0]-1)<1e-14
    assert abs(k[2,0,0]-17/24)<1e-14
    f=native.radial([0.,1.],[[0.,1.]],[[[0.,0.,0.]]],2.,32)
    assert np.allclose(f[:,0,0],[1/6,1/16,1/40],atol=1e-15,rtol=0)

def test_native_fixed_panel_error_and_angular(native):
    e=[0.,1.,2.];p=[[0.,.5,0.],[0.,1.,0.]];b=np.array([[[.1,.2,-.1],[.3,-.1,.1]],[[0.,0.,0.],[0.,0.,0.]]])
    delta=[.5,0.,1.25];rr=np.linalg.norm(delta)
    radial=native.radial(e,p,b,rr,32);R,n=geometry_interval(delta)
    cert=radial_certificate(e,p,b,R)
    lm=[(0,0),(1,0)];ix=[0,1];v=angular_matrix(radial,lm,ix,delta)
    truth=projected_matrix(cert,lm,ix,n)
    assert max(error_upper(v[i,j],truth[i][j]) for i in range(2) for j in range(2))<F(1,10**14)
    with pytest.raises(ValueError):native.radial(e,p,b,rr,True)
    with pytest.raises(ValueError):native.radial(e,p,b,-1.,32)
