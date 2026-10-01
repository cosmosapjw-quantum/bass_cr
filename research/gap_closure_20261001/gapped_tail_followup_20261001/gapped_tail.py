"""Exact rational arithmetic for a CONDITIONAL gapped far-tail theorem.

This module does not certify a reference Hamiltonian, gap, support, embedding,
or dynamics. Inputs must describe one exact finite-dimensional model. No
native query, numerical propagation, fitted data, or selector replacement.
"""
from fractions import Fraction


def _rational(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise TypeError(f'{name}: exact int, decimal/rational string or Fraction required')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f'{name}: finite rational required') from error


def tail_bound(*, Z, b, radius, charge, gap, norm2=1):
    """Return rational support-only bound for one signed tail |z| >= Z.

    gap is an independently established lower/upper H0 cluster separation.
    This is not a sign-cut definition of the perturbed cluster: retain its
    rank using a fixed separator in the certified gap. Preconditions Z>a,
    R(Z)>2a and 2*epsilon(Z)<gap are enforced exactly. Bound is independent
    of positive constant speed and hbar because it follows a commuting
    instantaneous spectral projector along the SAME exact state.
    """
    Z,b,a,q,delta,N=[_rational(x,n) for x,n in
                    [(Z,'Z'),(b,'b'),(radius,'radius'),(charge,'charge'),
                     (gap,'gap'),(norm2,'norm2')]]
    if a<=0 or Z<=a or b<0 or q<0 or delta<=0 or N<0:
        raise ValueError('a>0, Z>a, b>=0, charge>=0, gap>0, norm2>=0 required')
    if Z*Z+b*b<=4*a*a:
        raise ValueError('disjoint support R(Z)>2a required')
    epsilon=q*a/(Z*Z+b*b-a*a)
    g=delta-2*epsilon
    if g<=0:
        raise ValueError('strict spectral gap 2*epsilon(Z)<gap required')
    distance=epsilon/(delta-epsilon)
    derivative_integral=q*a/(Z-a)**2
    variation=derivative_integral/g
    uncapped=N*(distance+variation)
    return dict(epsilon=epsilon,instantaneous_gap_lower=g,
                projector_distance=distance,
                derivative_mod_scalar_integral=derivative_integral,
                variation_integral=variation,
                uncapped_probability_bound=uncapped,
                probability_bound=min(N,uncapped))


def first_integer_cutoff(*, target, b, radius, charge, gap, norm2=1):
    """Smallest positive integer Z passing this formula; not a run proposal."""
    target=_rational(target,'target')
    if target<=0:
        raise ValueError('positive target required')
    args={n:_rational(x,n) for n,x in
          dict(b=b,radius=radius,charge=charge,gap=gap,norm2=norm2).items()}
    if (args['b']<0 or args['radius']<=0 or args['charge']<0
            or args['gap']<=0 or args['norm2']<0):
        raise ValueError('invalid bound parameters')
    def passes(z):
        try:
            return tail_bound(Z=z,**args)['probability_bound']<=target
        except ValueError:
            return False
    low,high=0,1
    for _ in range(1024):
        if passes(high):
            break
        low,high=high,2*high
    else:
        raise OverflowError('cutoff exceeds bounded search range')
    while high-low>1:
        middle=(low+high)//2
        if passes(middle):
            high=middle
        else:
            low=middle
    return high
