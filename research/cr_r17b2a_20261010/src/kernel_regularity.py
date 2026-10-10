"""Exact jump algebra for an additive background birth and a test channel.

Input entries are Fractions in one consistent time/thermal normalization.
This computes the local jump expression; continuity/smoothness and common
homotopy tube assumptions are external physical premises, not inferred here.
"""
from fractions import Fraction as F

def dot(a,b):
    if len(a)!=len(b):raise ValueError('VECTOR_DIMENSION_MISMATCH')
    return sum((x*y for x,y in zip(a,b)),F(0))

def second_jump(*,weight,kappa_background,grad_background,yield_background,psi_background,
                kappa_probe,grad_probe,yield_probe,psi_probe,lambda_g):
    vectors=[grad_background,yield_background,grad_probe,yield_probe,lambda_g]
    if not vectors[0] or len({len(x) for x in vectors})!=1:raise ValueError('VECTOR_DIMENSION_MISMATCH')
    vals=[weight,kappa_background,kappa_probe,psi_background,psi_probe]+[x for v in vectors for x in v]
    if not all(isinstance(v,F) for v in vals):raise TypeError('EXACT_FRACTIONS_REQUIRED')
    if weight<0 or kappa_background<0 or kappa_probe<0:raise ValueError('NEGATIVE_BIRTH_OR_OPACITY')
    Rb=psi_background-dot(yield_background,lambda_g)
    Rp=psi_probe-dot(yield_probe,lambda_g)
    dk=weight*kappa_background*dot(grad_probe,yield_background)
    dl=[weight*a*Rb for a in grad_background]
    direct=dk*Rp
    dual=-kappa_probe*dot(yield_probe,dl)
    return {'opacity_time_jump':dk,'adjoint_time_jump':dl,'opacity_term':direct,'adjoint_term':dual,'kernel_second_jump':direct+dual}
