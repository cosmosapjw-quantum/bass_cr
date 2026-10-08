"""Exact readout algebra; never evolves a producer state or certifies its inputs.

Responses may be signed. Scalar state admissibility is a producer obligation.
All interval endpoints are Fractions; native f64 inputs use binary64() explicitly.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from decimal import Decimal, localcontext
from typing import Iterable, Sequence
import json
import math

Interval = tuple[F, F]

class ContractError(ValueError):
    """Input identities, domains or readout semantics do not match."""


def binary64(value: str | float | int) -> F:
    if isinstance(value, bool):
        raise ContractError('BOOLEAN_IS_NOT_A_PHYSICAL_VALUE')
    x = float(value)
    if not math.isfinite(x):
        raise ContractError('NONFINITE_BINARY64')
    return F.from_float(x)


def checked_interval(x: Interval) -> Interval:
    if len(x) != 2 or not all(isinstance(v, F) for v in x) or x[0] > x[1]:
        raise ContractError('INVALID_EXACT_INTERVAL')
    return x


def electron_interval(h: Interval, y: Interval, z: Interval, f_he: F) -> Interval:
    """x_HII + fHe*(x_HeII + 2*x_HeIII), or its matched-state difference."""
    checked_interval(h); checked_interval(y); checked_interval(z)
    if not isinstance(f_he, F) or f_he < 0:
        raise ContractError('INVALID_HELIUM_RATIO')
    return (h[0] + f_he*(y[0] + 2*z[0]),
            h[1] + f_he*(y[1] + 2*z[1]))


def electrons(h: F, y: F, z: F, f_he: F) -> F:
    return electron_interval((h,h), (y,y), (z,z), f_he)[0]


def rct_fraction_increment(events_per_h: F, f_he: F) -> tuple[F,F,F]:
    """HeIII + HI -> HeII + HII + gamma; native event counts are per H."""
    if f_he <= 0 or events_per_h < 0:
        raise ContractError('RCT_COUNT_DOMAIN')
    return events_per_h, events_per_h/f_he, -events_per_h/f_he


def rct_opacity_increment(events_per_h: F, n_h: F, sigma_hi: F,
                          sigma_heii: F, c: F) -> F:
    """Fixed-state linear perturbation; no time integration or photon closure."""
    if any(x < 0 for x in (events_per_h,n_h,sigma_hi,sigma_heii,c)):
        raise ContractError('NEGATIVE_ABSORPTION_INPUT')
    return c*n_h*events_per_h*(sigma_heii-sigma_hi)


@dataclass(frozen=True)
class PairContract:
    model_family: str
    source_identity: str
    background_identity: str
    coordinate: str
    observable: str
    window: tuple[F,F]


def require_pair(a: PairContract, b: PairContract) -> None:
    if a != b:
        raise ContractError('UNMATCHED_MODEL_SOURCE_BACKGROUND_CLOCK_OR_READOUT')
    if a.coordinate not in ('proper_seconds', 'ln_a') or a.window[0] >= a.window[1]:
        raise ContractError('UNDECLARED_OR_EMPTY_CLOCK')


def trapezoid(nodes: Sequence[F], values: Sequence[F], *, signed: bool = False) -> F:
    """Exactly integrates the endpoint-linear surrogate, not the unknown IVP."""
    if len(nodes) != len(values) or len(nodes) < 2:
        raise ContractError('INCOMPLETE_ENDPOINT_SERIES')
    if any(nodes[i+1] <= nodes[i] for i in range(len(nodes)-1)):
        raise ContractError('NONINCREASING_CLOCK')
    if not signed and any(y < 0 for y in values):
        raise ContractError('NEGATIVE_ELECTRON_DENSITY')
    return sum(((b-a)*(x+y)/2 for a,b,x,y in zip(nodes,nodes[1:],values,values[1:])),F(0))


def paired_integral(a_key: PairContract, b_key: PairContract,
                    a_nodes: Sequence[F], b_nodes: Sequence[F],
                    a_values: Sequence[F], b_values: Sequence[F]) -> F:
    require_pair(a_key,b_key)
    if tuple(a_nodes) != tuple(b_nodes):
        raise ContractError('CLOCK_VALUES_NOT_IDENTICAL')
    if not a_nodes or (a_nodes[0],a_nodes[-1]) != a_key.window:
        raise ContractError('CLOCK_WINDOW_MISMATCH')
    if len(a_values) != len(b_values):
        raise ContractError('SERIES_LENGTH_MISMATCH')
    return trapezoid(a_nodes, [b-a for a,b in zip(a_values,b_values)], signed=True)


def fixed_energy_guard(energy: Sequence[Interval]) -> None:
    """Applies only to the received REI BOXJOIN contract, not all producers."""
    for box in energy:
        checked_interval(box)
        if box[0] != box[1]:
            raise ContractError('ENERGY_PARAMETER_BOX_UNSUPPORTED_BY_DONOR')


def hh_total_electron_bounds(signed: dict, predecessor: dict,
                             prefactor: F, f_he: F = F('0.083')) -> dict:
    """Conditional theorem from HH-TH05 + its hash-bound TH04, not a re-proof.

    TH05 supplies d_h(t)>=lambda*m/d*(1-exp(-d*t)), 0<lambda<=1.
    TH04 supplies componentwise |Delta He|<=lambda*B and common density bounds.
    Return all numbers per lambda; lambda=0 is exactly the common OFF solution.
    """
    if signed['scope']['time_s'] != predecessor['time_s']:
        raise ContractError('HH_TIME_MISMATCH')
    if signed['scope']['epsilon'] != predecessor['shear_range']:
        raise ContractError('HH_SHEAR_MISMATCH')
    if signed['scope']['lambda'] != predecessor['HH_strength_range']:
        raise ContractError('HH_STRENGTH_MISMATCH')
    if not signed['claims']['h_lambda_gt_h_OFF_for_t_gt0_lambda_gt0']:
        raise ContractError('HH_SIGNED_PREMISE_MISSING')
    times=[F(v) for v in predecessor['time_s']]
    if times[0] != 0 or times[1] <= 0 or prefactor <= 0:
        raise ContractError('HH_DOMAIN_MISMATCH')
    L=times[1]
    try:
        B=[F(x['upper']) for x in predecessor['uniform_error_bound']]
        if len(B)<3 or any(x<0 for x in B): raise ValueError()
    except (KeyError,ValueError,TypeError):
        raise ContractError('HH_HELIUM_BOUNDS_REQUIRED') from None
    m=F(signed['strict_positive_margin_per_s'])
    d=F(signed['damping_upper_per_s'])
    nlo=F(signed['density_lower_cm3']); nhi=F('0.0001')
    gl=F(signed['delta_h_endpoint_lower_function_interval']['lower'])
    gu=F(signed['delta_h_endpoint_lower_function_interval']['upper'])
    if not (0<m and 0<d and 0<nlo<=nhi and 0<gl<=gu<m*L):
        raise ContractError('HH_INCONSISTENT_POSITIVE_PREMISES')
    beta=f_he*(B[1]+2*B[2])
    lower_X=gl-beta
    upper_X=B[0]+beta
    # Integral g=(m*L-g(L))/d. Subtract upper endpoint for a lower integral.
    int_g_lower=(m*L-gu)/d
    int_g_upper=(m*L-gl)/d
    tau_lower=prefactor*(nlo*int_g_lower-nhi*beta*L)
    tau_upper=prefactor*nhi*upper_X*L
    if m<=d*beta:
        t_positive=None
    else:
        t_positive=beta/(m-d*beta) # sufficient, not the exact onset
    return dict(helium_penalty=beta, endpoint_Xe=(lower_X,upper_X),
        endpoint_ne_lower=nlo*lower_X if lower_X>=0 else nhi*lower_X,
        endpoint_ne_upper=nhi*upper_X, int_g=(int_g_lower,int_g_upper),
        delta_tau=(tau_lower,tau_upper), sufficient_positive_time_s=t_positive,
        all_outputs_per_lambda=True, HII_predecessor_reexecuted=False,
        physical_admission=False, observer_tail=None)


def fraction_record(x: F) -> dict:
    with localcontext() as ctx:
        ctx.prec=28
        display=str(Decimal(x.numerator)/Decimal(x.denominator))
    return {'numerator':str(x.numerator),'denominator':str(x.denominator),'display':display}


def exact_json(x):
    if isinstance(x,F): return fraction_record(x)
    if isinstance(x,dict): return {k:exact_json(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [exact_json(v) for v in x]
    return x


def strict_load(text: str):
    def pairs(xs):
        out={}
        for k,v in xs:
            if k in out: raise ContractError('DUPLICATE_JSON_KEY')
            out[k]=v
        return out
    def fail(x): raise ContractError('NONFINITE_JSON')
    return json.loads(text,object_pairs_hook=pairs,parse_constant=fail)
