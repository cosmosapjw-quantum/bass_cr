"""Exact rational bound arithmetic, conditional on caller-validated matrix bounds.

This creates no spectral projector and changes no B0 basis or selector.
Accepting rational inputs does not certify their physical provenance.
"""
from fractions import Fraction


def projector_distance_enclosure(a_lower,d_lower,residual_upper):
    """For A<=-aI,D>=dI,||R||<=r, return min(1,r/(a+d)) exactly.

    F=[[A,R†],[R,D]] is self-adjoint and P selects the A block.
    The result bounds ||P-E_negative(F)|| if the supplied inequalities hold.
    """
    if not all(isinstance(x,Fraction) for x in (a_lower,d_lower,residual_upper)):
        raise TypeError('exact Fraction bounds required; no automatic float rounding')
    if min(a_lower,d_lower)<=0 or residual_upper<0:
        raise ValueError('positive separated diagonal gaps and nonnegative residual required')
    return min(Fraction(1),residual_upper/(a_lower+d_lower))
