"""Exact scalar/finite-matrix bridge tools, not a physical atomic certificate.

Units are explicit in BoundInputs. Saved binary64 entries may be interpreted as
exact rational numbers only for an explicitly named stored-matrix model.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import isfinite, isqrt
from typing import Any
import hashlib
import json

class ContractError(ValueError):
    """A precondition or evidence boundary is not satisfied."""

def rational(x: Any) -> F:
    if isinstance(x,bool):
        raise ContractError('boolean is not a numerical bound')
    if isinstance(x,float) and not isfinite(x):
        raise ContractError('nonfinite input')
    try:
        return F(x)
    except (ValueError,TypeError,OverflowError,ZeroDivisionError) as e:
        raise ContractError('invalid rational') from e

def _matrix(x):
    rows=[[rational(v) for v in r] for r in x]
    n=len(rows)
    if n<2 or any(len(r)!=n for r in rows):
        raise ContractError('real square matrix of dimension at least two required')
    if any(rows[i][j]!=rows[j][i] for i in range(n) for j in range(n)):
        raise ContractError('exact symmetry required; no symmetrization is performed')
    return rows

def gershgorin_lower(x):
    return min(x[i][i]-sum(abs(x[i][j]) for j in range(len(x)) if j!=i) for i in range(len(x)))

def sqrt_upper(x, bits=160):
    x=rational(x)
    if x<0 or not isinstance(bits,int) or isinstance(bits,bool) or bits<8 or bits>4096:
        raise ContractError('nonnegative radicand and 8..4096 bits required')
    if not x:return F(0)
    q=1<<bits
    k=isqrt((x.numerator*q*q)//x.denominator)
    if k*k*x.denominator<x.numerator*q*q:k+=1
    return F(k,q)

def _matrix_hash(S,H):
    data=json.dumps({'S':[[str(v) for v in r] for r in S],
                     'H':[[str(v) for v in r] for r in H]},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(data).hexdigest()

def stored_ground_gap(S,H,alpha,beta):
    """Min-max certificate for a real rational pair (H,S), with trial e_0.

    lambda_1 <= alpha follows from the trial Rayleigh quotient. lambda_2 >=
    beta follows from positivity of H_c-beta*S_c on x_0=0. This is NOT a
    certificate of the continuous candidate quadrature or a two-center gap.
    """
    S,H=_matrix(S),_matrix(H)
    if len(S)!=len(H):raise ContractError('shape mismatch')
    alpha,beta=rational(alpha),rational(beta)
    if beta<=alpha:raise ContractError('ordered positive gap required')
    smin=gershgorin_lower(S)
    if smin<=0:raise ContractError('Gershgorin SPD certificate failed')
    trial=H[0][0]/S[0][0]
    if trial>alpha:raise ContractError('trial energy does not certify alpha')
    comp=[[H[i][j]-beta*S[i][j] for j in range(1,len(S))] for i in range(1,len(S))]
    margin=gershgorin_lower(comp)
    if margin<0:raise ContractError('complement Loewner bound not certified')
    y=[H[i][0]-trial*S[i][0] for i in range(len(S))]
    residual_sq=sum(v*v for v in y)/(S[0][0]*smin)
    residual_upper=sqrt_upper(residual_sq)
    mapping_upper=min(F(1),residual_upper/(beta-trial))
    return {
        'schema':'R4AJ_STORED_MATRIX_MINMAX_V1', 'verified':True,
        'bound_type':'EXACT_STORED_BINARY_MATRIX_PAIR',
        'matrix_pair_sha256':_matrix_hash(S,H),'dimension':len(S),
        'lambda1_upper':str(alpha),'lambda2_lower':str(beta),
        'gap_lower':str(beta-alpha),'energy_unit':'Eh',
        'S_gershgorin_lower':str(smin),'trial_rayleigh':str(trial),
        'complement_psd_margin':str(margin),
        'residual_norm_square_upper':str(residual_sq),
        'residual_norm_upper':str(residual_upper),
        'raw_trial_to_stored_ground_projector_upper':str(mapping_upper),
        'physical_candidate_operator_error_included':False,
        'physical_or_continuous_bridge_admission':False,
    }

def exact_projector_rank_distance(rank_a,rank_b,dimension):
    """Norm is 1 for unequal finite ranks. Equal rank is not determined."""
    if any(not isinstance(k,int) or isinstance(k,bool) for k in (rank_a,rank_b,dimension)):
        raise ContractError('integer ranks required')
    if dimension<1 or not 0<=rank_a<=dimension or not 0<=rank_b<=dimension:
        raise ContractError('invalid rank/dimension')
    return F(1) if rank_a!=rank_b else None

def doubled_reference_discriminator(certificate):
    """Two identical isolated operator copies, in their internal-energy gauge.

    The repeated ground eigenvalue implies that keeping only projectile 1s
    cannot yield a nonzero spectral separation from its target partner.
    This states a structural obstruction in the declared reference, not
    exact resonance of the interacting Hamiltonian at finite separation.
    """
    if not certificate.get('verified') or certificate.get('bound_type')!='EXACT_STORED_BINARY_MATRIX_PAIR':
        raise ContractError('stored-matrix certificate required')
    gap=rational(certificate['gap_lower'])
    if gap<=0:raise ContractError('invalid input gap')
    return {'reference':'two identical isolated copies',
            'single_copy_sha256':certificate['matrix_pair_sha256'],
            'measurement_rank':1,'lowest_pair_rank':2,
            'single_measurement_to_full_complement_gap':'0',
            'pair_to_rest_gap_lower':str(gap),'energy_unit':'Eh',
            'finite_separation_gap_lower':None,
            'decision':'RETAIN_TARGET_AND_PROJECTILE_1S_IN_DYNAMIC_CLUSTER',
            'measurement_changed_to_cluster_population':False}

def select_channels(metadata, registry):
    """Bind semantic labels; never infer principal_n from array position."""
    if metadata.get('identity')!=registry.get('candidate'):
        raise ContractError('candidate identity mismatch')
    modes=metadata['modes']; ordered=registry['channel_order']
    seen=set();ground=[];negative=[]
    for i,c in enumerate(ordered):
        if len(c)!=3:raise ContractError('channel triple required')
        rad,l,m=c
        if any(not isinstance(t,int) or isinstance(t,bool) for t in c):raise ContractError('integer channel triple required')
        if not 0<=rad<len(modes) or l!=modes[rad]['l'] or l not in (0,1) or abs(m)>l:
            raise ContractError('unsupported or inconsistent channel')
        key=(modes[rad]['identity'],l,m)
        if key in seen:raise ContractError('duplicate physical channel')
        seen.add(key)
        if l==0 and m==0 and modes[rad]['principal_n']==1:ground.append(i)
        if rational(modes[rad]['energy'])<0:negative.append(i)
    if len(ground)!=1:raise ContractError('unique labeled 1s required')
    n=len(ordered);g=ground[0]
    return {'candidate':metadata['identity'],'center_channel_count':n,
            'measurement_projectile_1s':[n+g],
            'historical_projectile_negative_labels':[n+i for i in negative],
            'dynamic_target_projectile_1s':[g,n+g],
            'energy_labels_are_spectral_enclosures':False,
            'production_selector_installed':False}

@dataclass(frozen=True)
class BlockBounds:
    """Continuous upper bounds for the fixed-frame Hermitian block model.

    The caller must establish the continuous claims; exact arithmetic does
    not establish their premises. Energy is Eh, time ta, hbar Eh*ta.
    """
    gap: Any
    coupling: Any
    coupling_derivative: Any
    diagonal_derivative_sum: Any
    duration: Any
    hbar: Any
    evidence_id: str
    bound_type: str='CONDITIONAL_CONTINUOUS_INPUTS'
    frame_connection_included: bool=True
    energy_unit: str='Eh'
    time_unit: str='ta'


def clustered_action_bound(p: BlockBounds):
    if (p.energy_unit,p.time_unit)!=('Eh','ta'):
        raise ContractError('explicit atomic energy/time units required; convert before use')
    if p.bound_type not in ('CONDITIONAL_CONTINUOUS_INPUTS','VALIDATED_CONTINUOUS_INPUTS'):
        raise ContractError('point diagnostics and empirical differences are not continuous bounds')
    if not p.frame_connection_included:raise ContractError('moving-frame connection omitted')
    if not isinstance(p.evidence_id,str) or not p.evidence_id.strip():raise ContractError('missing premise/evidence identity')
    gamma,B,Bp,L,T,hbar=map(rational,(p.gap,p.coupling,p.coupling_derivative,p.diagonal_derivative_sum,p.duration,p.hbar))
    if gamma<=0 or hbar<=0:raise ContractError('positive ordered gap and hbar required')
    if min(B,Bp,L,T)<0:raise ContractError('negative upper bound or duration')
    x=B/gamma
    xp=Bp/gamma+L*B/(gamma*gamma)
    primitive=F(0) if T==0 else 2*x+T*xp
    norm_integral=T*B/hbar
    # Either ordinary Duhamel or primitive integration-by-parts is valid.
    e_raw=min(norm_integral,primitive*(1+norm_integral))
    e=min(F(2),e_raw)
    return {'schema':'R4AJ_CONDITIONAL_CLUSTER_ACTION_V1',
            'premise_identity':p.evidence_id,'premise_status':p.bound_type,
            'sylvester_solution_upper':str(x),'sylvester_derivative_upper_per_ta':str(xp),
            'primitive_upper':str(primitive),'coupling_time_integral':str(norm_integral),
            'state_distance_upper':str(e),
            'same_normalized_state_projector_error_upper':str(min(F(1),2*e)),
            'resonant_internal_transfer_included_in_error':False,
            'whole_physical_bridge_upper':None,
            'scientific_gate_promoted':False}

def reference_transfer_upper(coupling_in_measurement_basis,duration,hbar):
    """Two-state fixed measurement population variation <= integral |k|/hbar.

    This is valid for any normalized state; no P(t0)=0 is presumed. The frame
    connection must already be included in the effective off-diagonal k.
    """
    k,T,hbar=map(rational,(coupling_in_measurement_basis,duration,hbar))
    if k<0 or T<0 or hbar<=0:raise ContractError('invalid transfer inputs')
    return min(F(1),k*T/hbar)

def probability_bridge_total(reference_transfer,state_comparison,selector_map,other):
    """Same observable chain on normalized states, explicit missing inputs."""
    vals=(reference_transfer,state_comparison,selector_map,other)
    checked=[None if v is None else rational(v) for v in vals]
    if any(v is not None and v<0 for v in checked):raise ContractError('negative comparison bound')
    if any(v is None for v in checked):return {'status':'MISSING_PHYSICAL_BOUNDS','upper':None}
    total=checked[0]+2*checked[1]+checked[2]+checked[3]
    return {'status':'CONDITIONAL_CHAIN_EVALUATED','uncapped_upper':str(total),'upper':str(min(F(1),total))}
