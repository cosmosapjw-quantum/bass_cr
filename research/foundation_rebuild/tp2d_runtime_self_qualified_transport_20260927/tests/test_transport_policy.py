from types import SimpleNamespace
import numpy as np
import pytest
from transport_policy import assess_temporal_pair,metric_derivative_residual


def dist(a,b,S):
    d=np.asarray(a)-np.asarray(b)
    return float(np.sqrt(np.vdot(d,S@d).real))


def test_temporal_pair_requires_reference_refinement_and_norm_passes():
    prev=SimpleNamespace(nstep=48,final_state=np.array([0.0]),max_norm_drift=1e-10)
    curr=SimpleNamespace(nstep=96,final_state=np.array([2e-7]),max_norm_drift=2e-10)
    rec=assess_temporal_pair(prev,curr,np.array([1e-7]),np.eye(1),dist,{
        'candidate_norm_drift_max':1e-8,
        'candidate_reference_metric_distance_max':1e-6,
        'candidate_refinement_metric_distance_max':1e-6,
    })
    assert rec['qualified'] is True
    assert rec['selected_nstep']==96
    assert rec['evidence_relation']=='INDEPENDENT_TEMPORAL_DISCRETIZATION_COMPARISON'


def test_temporal_pair_fails_if_only_reference_distance_passes():
    prev=SimpleNamespace(nstep=48,final_state=np.array([2e-3]),max_norm_drift=1e-10)
    curr=SimpleNamespace(nstep=96,final_state=np.array([2e-7]),max_norm_drift=1e-10)
    rec=assess_temporal_pair(prev,curr,np.array([1e-7]),np.eye(1),dist,{
        'candidate_norm_drift_max':1e-8,
        'candidate_reference_metric_distance_max':1e-6,
        'candidate_refinement_metric_distance_max':1e-6,
    })
    assert rec['reference_pass'] is True
    assert rec['refinement_pass'] is False
    assert rec['qualified'] is False


class LinearMetricProvider:
    identity='linear-metric'
    def at(self,t):
        A=np.diag([0.2,-0.1]).astype(complex)
        S=np.eye(2,dtype=complex)+float(t)*A
        D=0.5*A
        return SimpleNamespace(S=S,D=D)


def test_metric_derivative_sentinel_uses_direct_D_identity():
    row=metric_derivative_residual(LinearMetricProvider(),0.25,1e-4)
    assert row['relative_residual'] < 1e-10
    assert row['provider_identity']=='linear-metric'


def test_metric_derivative_rejects_nonpositive_epsilon():
    with pytest.raises(ValueError):
        metric_derivative_residual(LinearMetricProvider(),0.0,0.0)
