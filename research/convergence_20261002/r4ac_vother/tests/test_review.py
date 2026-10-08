import mpmath as mp
from independent_review import local_radial,direct_angular

def test_independent_recurrence_known_moments():
    with mp.workdps(120):
        r=local_radial([0.,2.],[[1.,1.]],[[[0.,0.,0.]]],[0.,0.,1.])
        truth=(1+mp.log(2),mp.mpf(1),mp.mpf(17)/24)
        for ell in range(3):assert abs(r[ell][0][0]-truth[ell])<mp.mpf('1e-110')

def test_independent_angular_axis_rule():
    with mp.workdps(120):
        a=direct_angular([0.,0.,2.])
        assert abs(a[1][0][2]-1/mp.sqrt(3))<mp.mpf('1e-110')
        assert abs(a[2][2][2]-mp.mpf(2)/5)<mp.mpf('1e-110')
        assert abs(a[0][1][1]-1)<mp.mpf('1e-110')
