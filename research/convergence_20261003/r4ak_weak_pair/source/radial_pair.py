"""Exact finite-candidate tail bounds, no new two-center integral evaluations."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import numpy as np
from weak_pair import rat, sqrt_bounds, ContractError

def tail_mass(edges, endpoints, bubbles, cutoff):
    e=[rat(x) for x in edges]; u=[rat(x) for x in endpoints]
    q=[[rat(x) for x in row] for row in bubbles]; c0=rat(cutoff)
    if len(e)<2 or len(u)!=len(e) or len(q)!=len(e)-1 or any(len(row)!=3 for row in q):
        raise ContractError('inconsistent radial panel shapes')
    if e[0]!=0 or c0<0 or any(b<=a for a,b in zip(e,e[1:])):
        raise ContractError('nonnegative cutoff and increasing edges from zero required')
    value=F(0)
    for a,b,left,right,(q0,q1,q2) in zip(e,e[1:],u,u[1:],q):
        if b<=c0: continue
        lo=max(F(0),(c0-a)/(b-a))
        c=[left,right-left+q0,q1-q0,q2-q1,-q2]
        value+=(b-a)*sum(c[i]*c[j]*(1-lo**(i+j+1))/F(i+j+1) for i in range(5) for j in range(5))
    if value<0: raise ContractError('negative squared tail mass')
    return value

def uniform_pair_bound(candidate_npz, candidate_json, exact_moments, *, speed, min_abs_z=12, split_radius=6, impact_b=2):
    """For |z|>=12 and b=2, use |<T1s|P1s>|<=2 sqrt(g*tail(6)).

    This statement holds for any ETF with unit modulus. It is not a bound on
    the full 18-channel Gram, on a cross derivative, or on a physical gap.
    The norm and radial kinetic moment are reused from the exact R4AB oracle.
    """
    meta=json.loads(Path(candidate_json).read_text()); gram=json.loads(Path(exact_moments).read_text())
    if meta['identity']!=gram['candidate']: raise ContractError('candidate/moment identity mismatch')
    m=[i for i,x in enumerate(meta['modes']) if x['l']==0 and x['principal_n']==1]
    if len(m)!=1: raise ContractError('one s-wave ground label required')
    j=m[0]; a=rat(split_radius); z=rat(min_abs_z); b=rat(impact_b); v=rat(speed)
    if a<=0 or z<2*a or b<0 or v<=0: raise ContractError('invalid nonoverlap split or kinematics')
    with np.load(candidate_npz,allow_pickle=False) as data:
        edges=data['edges']; u=data['shared_endpoint_values'][j]; q=data['bubble_coefficients'][j]
        if float(u[0])!=0 or float(u[-1])!=0: raise ContractError('zero endpoints required for H1 extension')
        tail=tail_mass(edges,u,q,a)
    g=rat(gram['matrices_exact']['G'][j][j]); kinetic=rat(gram['matrices_exact']['T'][j][j])
    if not 0<=tail<=g or g<=0 or kinetic<0: raise ContractError('invalid inherited exact radial moments')
    cross=2*sqrt_bounds(g*tail)[1]; lower=g-cross; upper=g+cross
    if lower<=0: raise ContractError('pair conditioning is not certified by this split')
    l2_trace=2*g
    gradient_trace=2*kinetic+v*v*g
    H_bound=gradient_trace/2+4*sqrt_bounds(gradient_trace*l2_trace)[1]
    Fdot_sq=v*v*kinetic/3+v**4*g/4
    D_bound=sqrt_bounds(l2_trace*Fdot_sq)[1]
    out={'schema':'R4AK_FINITE_CANDIDATE_UNIFORM_PAIR_V1', 'candidate':meta['identity'],
         'domain':{'min_abs_z_a0':str(z),'b_a0':str(b),'speed_a0_per_ta':str(v),
                   'split_radius_a0':str(a),'same_normalized_Y00':True,'ETF_unit_modulus':True},
         'ground_mode':j,'ground_norm_square':str(g),'radial_kinetic_integral_a0_m2':str(kinetic),
         'tail_mass_exact':str(tail),'overlap_modulus_upper':str(cross),
         'pair_Gram_lower':str(lower),'pair_Gram_upper':str(upper),
         'pair_condition_number_upper':str(upper/lower),
         'weak_pair_H_upper_Eh':str(H_bound),'pair_D_upper_per_ta':str(D_bound),
         'weak_pair_K_upper_Eh':str(H_bound+D_bound),
         'full18_Gram_lower':None,'physical_bridge_gap_Eh':None,'physical_bridge_upper':None,
         'all_bound_or_capture_promoted':False,'new_cross_integrals':0,
         'old_G_and_T_recomputed':False,'new_tail_integral_count':1,
         'method':'exact finite polynomial tail and Cauchy-Schwarz; weak Hardy form and H1 translation',
         'input_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest()
                         for p in (candidate_npz,candidate_json,exact_moments)}}
    return out
