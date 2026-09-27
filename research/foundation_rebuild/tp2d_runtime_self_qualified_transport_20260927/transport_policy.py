from __future__ import annotations
import numpy as np

class TemporalRefinementError(RuntimeError):
    pass


def assess_temporal_pair(previous,current,reference_final,S_final,distance_fn,screens):
    if int(current.nstep) <= int(previous.nstep):
        raise ValueError('temporal ladder must increase')
    dref=float(distance_fn(reference_final,current.final_state,S_final))
    dself=float(distance_fn(previous.final_state,current.final_state,S_final))
    if not np.isfinite([dref,dself,previous.max_norm_drift,current.max_norm_drift]).all():
        raise TemporalRefinementError('nonfinite temporal qualification evidence')
    norm_limit=float(screens['candidate_norm_drift_max'])
    ref_limit=float(screens['candidate_reference_metric_distance_max'])
    self_limit=float(screens['candidate_refinement_metric_distance_max'])
    prev_norm=previous.max_norm_drift<=norm_limit
    curr_norm=current.max_norm_drift<=norm_limit
    ref_pass=dref<=ref_limit
    refinement_pass=dself<=self_limit
    qualified=bool(prev_norm and curr_norm and ref_pass and refinement_pass)
    return {
        'previous_nstep':int(previous.nstep),'selected_nstep':int(current.nstep),
        'previous_norm_drift':float(previous.max_norm_drift),'selected_norm_drift':float(current.max_norm_drift),
        'previous_norm_pass':bool(prev_norm),'selected_norm_pass':bool(curr_norm),
        'candidate_reference_metric_distance':dref,'candidate_refinement_metric_distance':dself,
        'reference_pass':bool(ref_pass),'refinement_pass':bool(refinement_pass),'qualified':qualified,
        'evidence_relation':'INDEPENDENT_TEMPORAL_DISCRETIZATION_COMPARISON',
    }


def metric_derivative_residual(provider,t,epsilon_t):
    t=float(t);epsilon_t=float(epsilon_t)
    if not np.isfinite([t,epsilon_t]).all() or epsilon_t<=0:
        raise ValueError('finite time and positive finite epsilon required')
    m=provider.at(t-epsilon_t);c=provider.at(t);p=provider.at(t+epsilon_t)
    sdot=(np.asarray(p.S)-np.asarray(m.S))/(2*epsilon_t)
    direct=np.asarray(c.D)+np.asarray(c.D).conj().T
    den=max(float(np.linalg.norm(sdot)),float(np.linalg.norm(direct)),1e-300)
    return {'t':t,'epsilon_t':epsilon_t,'relative_residual':float(np.linalg.norm(sdot-direct)/den),
            'provider_identity':provider.identity}
