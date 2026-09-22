"""R3M15 reporting semantics; does not change any numerical propagator or tolerance."""
import math

RELATIVE_SCREEN = .01
ABSOLUTE_FLOOR = 1e-8
ABSOLUTE_SCREEN = 1e-10

def _probability(value):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('probability must be finite in [0,1]')
    return value

def evaluate_pair(p_ref, p_new, d, reference_identity, new_identity):
    """Apply only to a verified common grid/K/Q/source pair with bound initials.

    This function consumes verified identities; it does not itself establish
    contraction, projector orthogonality or provenance from scalar inputs.
    Historical R3M14's missing reference binding must NOT call this as a certificate.
    """
    for key in ('grid', 'K', 'Q', 'source'):
        if not reference_identity.get(key) or reference_identity[key] != new_identity.get(key):
            raise ValueError(f'pair identity mismatch: {key}')
    if any(x.get('binding_verified') is not True for x in (reference_identity,new_identity)):
        raise ValueError('both initial-state bindings must be verified')
    _probability(p_ref); _probability(p_new)
    if not math.isfinite(d) or not 0 <= d <= math.sqrt(2):
        raise ValueError('invalid normalized phase-aligned distance')
    if p_ref == 0:
        return dict(a_priori_pair_certificate='UNDEFINED_RELATIVE_REFERENCE_ZERO',
                    measured_capture_test='UNDEFINED_RELATIVE_REFERENCE_ZERO',
                    relative_measured_change=None, absolute_measured_change=abs(p_new-p_ref), d_star=None)
    d_star = math.sqrt(p_ref)*RELATIVE_SCREEN/(math.sqrt(1+RELATIVE_SCREEN)+1)
    change = abs(p_new-p_ref)/p_ref
    return dict(a_priori_pair_certificate='SUFFICIENT_PAIR_ONLY' if d <= d_star else 'INCONCLUSIVE',
                measured_capture_test='PASS_PAIR_ONLY' if change <= RELATIVE_SCREEN else 'FAIL_OBSERVABLE_PAIR',
                relative_measured_change=change, absolute_measured_change=abs(p_new-p_ref),
                d_star=d_star, roundoff_certified=False, global_convergence_admitted=False)

def observable_change(candidate, reference):
    """New spatial metric: |fine - coarse| / |fine|; tiny fine uses absolute screen."""
    _probability(candidate); _probability(reference)
    delta = abs(candidate-reference)
    relative = delta/abs(candidate) if abs(candidate)>ABSOLUTE_FLOOR else None
    passed = relative <= RELATIVE_SCREEN if relative is not None else delta <= ABSOLUTE_SCREEN
    return dict(mode='RELATIVE_FINE_DENOMINATOR' if relative is not None else 'ABSOLUTE',
                absolute_change=delta, relative_change=relative,
                status='PASS_PAIR_ONLY' if passed else 'FAIL_PAIR_ONLY',
                relative_screen=RELATIVE_SCREEN, absolute_screen=ABSOLUTE_SCREEN,
                small_observable_floor=ABSOLUTE_FLOOR)

def spatial_order(coarse, middle, fine, *, comparable=True):
    """Equal h ratio 1.25; empirical single-power diagnostic, never a certificate."""
    out = dict(observed_order=None, extrapolated=None, certified=False)
    if not comparable or not all(math.isfinite(x) for x in (coarse,middle,fine)):
        return dict(out,status='NOT_COMPARABLE')
    d1,d2=coarse-middle,middle-fine
    if min(abs(d1),abs(d2)) <= ABSOLUTE_SCREEN or d1*d2 <= 0:
        return dict(out,status='UNRESOLVED_OR_NONMONOTONE')
    order=math.log(abs(d1/d2))/math.log(1.25)
    if order <= 0:
        return dict(out,status='NONCONTRACTING_DIFFERENCES')
    return dict(observed_order=order,extrapolated=fine+(fine-middle)/(1.25**order-1),
                certified=False,status='EMPIRICAL_SINGLE_POWER_ONLY')

def minimum_relative_change_over_interval(reference, lower, upper):
    """Min |candidate-reference|/candidate on a positive probability interval.

    The interval's provenance/theorem is external. This is scalar comparison,
    not a theorem about initial states on different grids.
    """
    for value in (reference,lower,upper):_probability(value)
    if lower>upper:raise ValueError('reversed probability interval')
    if lower==0:return None  # Undefined denominator is never an automatic PASS.
    if reference<lower:return (lower-reference)/lower
    if reference>upper:return (reference-upper)/upper
    return 0.
