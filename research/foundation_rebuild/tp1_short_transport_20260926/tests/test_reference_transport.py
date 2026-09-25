from dataclasses import dataclass
import numpy as np
import pytest

from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import symmetric_channels


@dataclass(frozen=True)
class Snap:
    S: np.ndarray
    H: np.ndarray
    D: np.ndarray


class ScalarMetricProvider:
    def at(self,t):
        s=1.0+0.2*t
        sd=0.2
        return Snap(np.array([[s]],complex),np.zeros((1,1),complex),np.array([[0.5*sd]],complex))


class BlockedProvider:
    def at(self,t):
        raise ArithmeticError('metric positivity/rank screen failed')


def test_find_target_1s_uses_metadata_not_position():
    from reference_transport import find_target_1s
    spec=RadialSpec(radius=12.,elements=6,degree=2,lmax=0,bound_nmax=1,
                    positive_per_l=0,quad_order=6)
    ch=list(symmetric_channels(atomic_bank(spec)))
    ch=list(reversed(ch))
    idx=find_target_1s(ch)
    assert ch[idx].center==0
    assert ch[idx].radial.principal_n==1
    assert ch[idx].radial.l==0 and ch[idx].m==0


def test_metric_normalization_and_rhs_match_direct_solve():
    from reference_transport import normalize_metric_state, generalized_rhs
    p=ScalarMetricProvider();s=p.at(0.4)
    c=normalize_metric_state(np.array([2.+1j]),s.S)
    assert abs(np.vdot(c,s.S@c)-1)<1e-14
    got=generalized_rhs(0.4,c,p)
    want=np.linalg.solve(s.S,(-1j*s.H-s.D)@c)
    assert np.allclose(got,want,rtol=0,atol=1e-14)


def test_reference_preserves_weighted_norm_for_metric_compatible_scalar_problem():
    from reference_transport import run_reference
    p=ScalarMetricProvider()
    out=run_reference(p,[object()],0.0,1.0,c0=np.array([1.+0j]),rtol=1e-11,atol=1e-13)
    assert out.success
    assert out.max_norm_drift < 2e-10
    exact=np.sqrt(1.0/1.2)
    assert abs(out.final_state[0]-exact)<2e-10
    assert not any('capture' in x.lower() for x in out.__dataclass_fields__)


def test_reference_propagates_provider_metric_failure_without_regularization():
    from reference_transport import run_reference
    with pytest.raises(ArithmeticError,match='metric positivity'):
        run_reference(BlockedProvider(),[object()],0.,1.,c0=np.array([1.+0j]))
