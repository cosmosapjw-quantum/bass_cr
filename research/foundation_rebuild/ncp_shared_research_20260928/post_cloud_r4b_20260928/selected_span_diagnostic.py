from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np

SELECTED = np.array([9, 10, 12, 13, 14], dtype=int)
TARGET_NEG = np.array([0, 1, 3, 4, 5], dtype=int)
FINAL_QUERY_ID = "9a30b3744896b21ce0f75284f264165d9bb4ab42f50e92cac926c6329f974ede"

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def metric_probability(S: np.ndarray, c: np.ndarray, idx: np.ndarray):
    G = S[np.ix_(idx, idx)]
    v = (S @ c)[idx]
    x = np.linalg.solve(G, v)
    p = np.vdot(v, x)
    return p, G

def metric_norm(S, c):
    return np.vdot(c, S @ c)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    a=ap.parse_args()
    root=Path(a.input); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    refs=np.load(root/'REFERENCE_STATES.npz',allow_pickle=False)
    op=np.load(root/'FINAL_OPERATOR.npz',allow_pickle=False)
    S=np.asarray(op['selected__S'],complex)
    cref=np.asarray(refs['final_state'],complex)
    if S.shape!=(18,18) or cref.shape!=(18,): raise ValueError('unexpected final shapes')
    if not np.array_equal(refs['states'][-1],cref): raise ValueError('final state mismatch')
    c0=np.asarray(refs['initial_state'],complex)
    if abs(c0[0]-1)>1e-14 or np.max(np.abs(c0[1:]))>1e-14: raise ValueError('initial target-1s vector mismatch')
    herm=float(np.max(np.abs(S-S.conj().T)))
    sev=np.linalg.eigvalsh(S)
    if herm>1e-12 or sev[0]<=0: raise ValueError('invalid final overlap metric')
    p_ref,G=metric_probability(S,cref,SELECTED)
    p_targ,Gt=metric_probability(S,cref,TARGET_NEG)
    if abs(p_ref.imag)>1e-12: raise ValueError('selected probability not real')
    pref=float(p_ref.real); norm_ref=metric_norm(S,cref)
    if pref < -1e-12 or pref > norm_ref.real+1e-12: raise ValueError('selected probability outside metric norm')

    J=np.zeros((18,len(SELECTED)),complex); J[SELECTED,np.arange(len(SELECTED))]=1
    Q=S@J@np.linalg.solve(G,J.conj().T@S)
    qherm=float(np.max(np.abs(Q-Q.conj().T)))
    idemp=float(np.linalg.norm(Q@np.linalg.solve(S,Q)-Q,2))
    qmineig=float(np.min(np.linalg.eigvalsh((Q+Q.conj().T)/2)))
    sqmineig=float(np.min(np.linalg.eigvalsh(((S-Q)+(S-Q).conj().T)/2)))

    rows=[]
    for N in (24,48,96,192,384):
        d=np.load(root/'candidates'/f'CANDIDATE_N{N}.npz',allow_pickle=False)
        c=np.asarray(d['final_state'],complex)
        p,_=metric_probability(S,c,SELECTED)
        rows.append({
            'nstep':N,
            'selected_span_probability':float(p.real),
            'abs_error_to_reference':abs(float(p.real)-pref),
            'relative_error_to_reference':abs(float(p.real)-pref)/pref,
            'metric_norm_real':float(metric_norm(S,c).real)
        })
    prob_orders=[]
    for x,y in zip(rows[:-1],rows[1:]):
        if x['abs_error_to_reference']>0 and y['abs_error_to_reference']>0:
            prob_orders.append({
              'nstep_pair':[x['nstep'],y['nstep']],
              'observed_order':math.log(x['abs_error_to_reference']/y['abs_error_to_reference'],2.0)
            })

    temporal=[]
    for aN,bN in ((24,48),(48,96),(96,192),(192,384)):
        d=json.loads((root/'candidates'/f'TEMPORAL_PAIR_N{aN}_N{bN}.json').read_text())
        temporal.append(d)
    ref_orders=[]; refine_orders=[]
    for x,y in zip(temporal[:-1],temporal[1:]):
        ref_orders.append(math.log(x['candidate_reference_metric_distance']/y['candidate_reference_metric_distance'],2.0))
        refine_orders.append(math.log(x['candidate_refinement_metric_distance']/y['candidate_refinement_metric_distance'],2.0))
    last=temporal[-1]; pstate=ref_orders[-1]; ratio=2.0**pstate
    extrap={
      'basis':'latest observed state-distance order; extrapolation only, not certificate',
      'observed_order_reference_distance_latest':pstate,
      'observed_order_refinement_distance_latest':refine_orders[-1],
      'N768_reference_distance_estimate':last['candidate_reference_metric_distance']/ratio,
      'N768_refinement_distance_estimate':last['candidate_refinement_metric_distance']/ratio,
      'N1536_reference_distance_estimate':last['candidate_reference_metric_distance']/(ratio**2),
      'N1536_refinement_distance_estimate':last['candidate_refinement_metric_distance']/(ratio**2),
      'frozen_limit':1e-6
    }

    payload={
      'schema':'BASS_R4B_REFERENCE_PATH_FINITE_SPAN_DIAGNOSTIC_V1',
      'status':'REFERENCE_PATH_FINITE_SPAN_DIAGNOSTIC_COMPLETE__TRANSPORT_GATE_OPEN',
      'authority':{
        'reference_states_sha256':sha256(root/'REFERENCE_STATES.npz'),
        'final_operator_npz_sha256':sha256(root/'FINAL_OPERATOR.npz'),
        'final_query_id':FINAL_QUERY_ID,
        'selected_indices':SELECTED.tolist(),
        'positive_projectile_pseudostates_excluded':[11,15,16,17],
        'initial_target_1s_index':0,
        'basis_phase_convention':'historical two_center basis_values: exp(i v.r - i v^2 t/2) on moving-center channel; pinned source commit c954d68fdc86527453765a563b3a025351163ed9'
      },
      'reference_result':{
        'P_projectile_negative_energy_finite_span':pref,
        'P_target_negative_energy_finite_span_nonexclusive':float(p_targ.real),
        'metric_norm_real':float(norm_ref.real),
        'metric_norm_imag':float(norm_ref.imag),
        'selected_gram_condition_number_2':float(np.linalg.cond(G)),
        'selected_gram_eigenvalues':np.linalg.eigvalsh(G).tolist(),
        'final_S_condition_number_2':float(np.linalg.cond(S)),
        'final_S_min_eigenvalue':float(sev[0]),
        'final_S_max_eigenvalue':float(sev[-1])
      },
      'projector_checks':{
        'Q_hermiticity_max_abs':qherm,
        'Q_Sinv_Q_minus_Q_spectral_norm':idemp,
        'min_eigenvalue_Q_symmetrized':qmineig,
        'min_eigenvalue_S_minus_Q_symmetrized':sqmineig,
        'pass_numerical_tolerance_1e-12':bool(max(qherm,idemp,max(0,-qmineig),max(0,-sqmineig))<1e-12)
      },
      'candidate_observable_convergence_diagnostic':rows,
      'candidate_observable_error_orders':prob_orders,
      'historical_state_metric_temporal_pairs':temporal,
      'state_metric_observed_orders':{
        'reference_distance':ref_orders,
        'refinement_distance':refine_orders
      },
      'future_temporal_extrapolation':extrap,
      'claim_policy':{
        'this_is_capture_execution':False,
        'this_is_production_result':False,
        'reference_path_is_temporally_admitted_by_frozen_TP2D_gate':False,
        'reason':'historical TP2D return status is TEMPORAL_REFINEMENT_UNRESOLVED; diagnostic uses archived reference final c and exact matching final S only',
        'capture_execution_allowed':False,
        'production_admission':'HOLD',
        'all_bound':'OPEN',
        'b_grid':'NO_GO',
        'original_capture_gap_resolved':False,
        'continuous_global_supremum_bound':False
      }
    }
    out.write_text(json.dumps(payload,indent=2)+'\n')

if __name__=='__main__': main()
