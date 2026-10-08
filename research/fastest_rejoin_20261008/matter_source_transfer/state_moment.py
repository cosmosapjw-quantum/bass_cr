"""Exact photo-source finite differences for two matched matter states.

R11 remains immutable. This is readout algebra: no trajectory, rate provider or
physical-error certificate is constructed. Mixed state/moment evaluations are
counterfactual algebraic evaluations, not independently evolved solutions.
"""
from fractions import Fraction as F
from source_transfer import State, Moments, ContractError, project

BACKGROUND = ('n_h','n_he','hubble_s','kb_erg_k','ev_erg','c_thomson_cm3_s')


def matched_background(a: State, b: State) -> None:
    if any(getattr(a,k) != getattr(b,k) for k in BACKGROUND):
        raise ContractError('MATCHED_BACKGROUND_AND_CONSTANTS_REQUIRED')


def difference(a, b):
    if a.keys() != b.keys():
        raise ContractError('OUTPUT_KEYS_DIFFER')
    return {k:b[k]-a[k] for k in a}


def average(a, b):
    if a.keys() != b.keys():
        raise ContractError('OUTPUT_KEYS_DIFFER')
    return {k:(a[k]+b[k])/2 for k in a}


def split_source(sa: State, ma: Moments, sb: State, mb: Moments, chi):
    """Exact symmetric moment/state split, including nonlinear EOS factors.

    F(s,m)=A(s)m is linear only in m. No Taylor remainder is discarded.
    The two possible update orders are averaged; no unique causal claim.
    Background and atomic constants must match; caller also binds model/epoch.
    """
    matched_background(sa,sb)
    aa=project(sa,ma,chi); ab=project(sa,mb,chi)
    ba=project(sb,ma,chi); bb=project(sb,mb,chi)
    moment=average(difference(aa,ab),difference(ba,bb))
    state=average(difference(aa,ba),difference(ab,bb))
    total=difference(aa,bb)
    interaction={k:bb[k]-ba[k]-ab[k]+aa[k] for k in aa}
    if any(total[k] != moment[k]+state[k] for k in total):
        raise ArithmeticError('SPLIT_IDENTITY')
    return dict(total=total,moment=moment,state=state,interaction=interaction)


def temperature_secant(sa: State, ma: Moments, sb: State, mb: Moments, chi):
    """Exact product/quotient chain rule for Tdot, not a frozen-state Jacobian.

    r=1/D, v=w/D**2, Tdot=2/(3kb)*(r*heat-v*electron_rate).
    delta(r) and delta(v) are finite differences, not first-order derivatives.
    """
    matched_background(sa,sb)
    a=project(sa,ma,chi);b=project(sb,mb,chi)
    da,db=sa.particles,sb.particles
    ra,rb=1/da,1/db
    va,vb=sa.w_erg_h*ra**2,sb.w_erg_h*rb**2
    dh=b['heat_erg_h_s']-a['heat_erg_h_s']
    dc=b['electron_dt_per_h_s']-a['electron_dt_per_h_s']
    hbar=(a['heat_erg_h_s']+b['heat_erg_h_s'])/2
    cbar=(a['electron_dt_per_h_s']+b['electron_dt_per_h_s'])/2
    dr=-(db-da)/(da*db)
    dv=(ra**2+rb**2)/2*(sb.w_erg_h-sa.w_erg_h)+(sa.w_erg_h+sb.w_erg_h)/2*(ra+rb)*dr
    if dr != rb-ra or dv != vb-va:
        raise ArithmeticError('QUOTIENT_SECANT_IDENTITY')
    k=F(2,3)/sa.kb_erg_k
    terms=dict(heat_change=k*(ra+rb)/2*dh,
               particle_denominator_change=k*hbar*dr,
               electron_rate_change=-k*(va+vb)/2*dc,
               thermal_partition_change=-k*cbar*dv)
    total=b['temperature_dt_k_s']-a['temperature_dt_k_s']
    if sum(terms.values(),F(0)) != total:
        raise ArithmeticError('EOS_SECANT_IDENTITY')
    return dict(total=total,terms=terms,delta_D=db-da,delta_w=sb.w_erg_h-sa.w_erg_h)


def three_way(s2: State, s4: State, m22: Moments, m24: Moments,
              m42: Moments, m44: Moments, chi):
    """H2Q2 -> H4Q4 split into reader, spectral-history and matter response.

    H denotes a saved gas path; Q an endpoint spectral quadrature. First average
    the two H/Q update orders, then split each H update into state/moment parts.
    This nesting is an explicitly selected attribution convention.
    """
    matched_background(s2,s4)
    a=project(s2,m22,chi);b=project(s2,m24,chi)
    c=project(s4,m42,chi);d=project(s4,m44,chi)
    q2=split_source(s2,m22,s4,m42,chi)
    q4=split_source(s2,m24,s4,m44,chi)
    reader=average(difference(a,b),difference(c,d))
    spectral=average(q2['moment'],q4['moment'])
    matter=average(q2['state'],q4['state'])
    total=difference(a,d)
    if any(total[k] != reader[k]+spectral[k]+matter[k] for k in total):
        raise ArithmeticError('THREE_WAY_IDENTITY')
    return dict(total=total,reader=reader,spectral_history=spectral,
                matter_state=matter,history_at_Q2=q2,history_at_Q4=q4,
                HQ_interaction={k:d[k]-c[k]-b[k]+a[k] for k in a},
                temperature_secant=temperature_secant(s2,m22,s4,m44,chi))
