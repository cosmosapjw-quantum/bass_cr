from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Snap:
    S: np.ndarray
    H: np.ndarray
    D: np.ndarray


class ConstantProvider:
    def __init__(self,H): self.H=np.asarray(H,complex)
    def at(self,t):
        n=len(self.H)
        return Snap(np.eye(n,dtype=complex),self.H,np.zeros((n,n),complex))


class ScalarMetricProvider:
    def at(self,t):
        s=1.+0.2*t
        return Snap(np.array([[s]],complex),np.zeros((1,1),complex),np.array([[0.1]],complex))


class WrongDScalarProvider:
    def at(self,t):
        s=1.+0.2*t
        return Snap(np.array([[s]],complex),np.zeros((1,1),complex),np.zeros((1,1),complex))


def test_metric_generator_satisfies_raw_connection_identity_without_projection():
    from metric_transport import metric_frame_generator
    p=ScalarMetricProvider();g=metric_frame_generator(p.at(0.3))
    assert np.linalg.norm(g.X+g.X.conj().T-g.W)<1e-14
    assert g.antihermitian_defect<1e-14
    assert np.allclose(g.G,np.zeros((1,1)),atol=1e-14)


def test_midpoint_step_matches_constant_generator_exactly():
    from metric_transport import run_candidate
    H=np.array([[0.4,0.1],[0.1,-0.2]],complex)
    p=ConstantProvider(H)
    c0=np.array([1.,0.],complex)
    out=run_candidate(p,c0,0.,0.75,3)
    from scipy.linalg import expm
    exact=expm(-1j*H*0.75)@c0
    assert np.allclose(out.final_state,exact,atol=2e-14,rtol=0)
    assert out.max_norm_drift<2e-14


def test_time_dependent_metric_candidate_agrees_with_direct_reference_under_refinement():
    from metric_transport import run_candidate, phase_aligned_metric_distance
    from reference_transport import run_reference
    p=ScalarMetricProvider();c0=np.array([1.+0j])
    ref=run_reference(p,[object()],0.,1.,c0=c0,rtol=1e-12,atol=1e-14)
    c8=run_candidate(p,c0,0.,1.,8)
    c64=run_candidate(p,c0,0.,1.,64)
    Sf=p.at(1.).S
    assert phase_aligned_metric_distance(c64.final_state,ref.final_state,Sf)<1e-11
    assert phase_aligned_metric_distance(c8.final_state,c64.final_state,Sf)<1e-11
    assert c64.max_norm_drift<1e-13


def test_phase_alignment_removes_only_global_phase():
    from metric_transport import phase_aligned_metric_distance
    S=np.array([[2.,0.2],[0.2,1.]],complex)
    a=np.array([1.,2j])
    b=np.exp(0.73j)*a
    assert phase_aligned_metric_distance(a,b,S)<1e-14
    c=b+np.array([0.05,0.])
    assert phase_aligned_metric_distance(a,c,S)>1e-3


def test_wrong_D_is_visible_not_repaired():
    from metric_transport import metric_frame_generator
    g=metric_frame_generator(WrongDScalarProvider().at(0.4))
    # Missing D makes the candidate generator look trivially skew at a single node,
    # so the independent metric-derivative identity remains the required detector.
    # Crucially, this function must not invent a D correction.
    assert np.allclose(g.Dt,0.)
    assert np.allclose(g.X,0.)


def test_candidate_result_has_no_capture_observable():
    from metric_transport import CandidateResult
    assert not any('capture' in x.lower() for x in CandidateResult.__dataclass_fields__)
