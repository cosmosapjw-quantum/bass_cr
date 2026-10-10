"""Exact finite-source moment defects and jump-aware Peano transfer.

Local coordinate x=(birth-a)/(b-a). The signed measure is CONTINUOUS minus
DISCRETE. Intervals enclose all supplied weights, not a statistical distribution.
This module certifies algebra given external kernel premises, never the FT03
kernel, a homotopy, or an ODE solution. All arithmetic is Fraction.
"""
from fractions import Fraction as F
from math import comb, factorial

class ContractError(ValueError):
    pass
class MissingPremise(ContractError):
    pass


def box(x):
    if len(x)!=2 or any(not isinstance(v,F) for v in x) or x[0]>x[1]:
        raise ContractError('EXACT_ORDERED_INTERVAL_REQUIRED')
    return tuple(x)

def plus(a,b):
    return a[0]+b[0],a[1]+b[1]

def neg(a):
    return -a[1],-a[0]

def times(a,b):
    v=[x*y for x in a for y in b]
    return min(v),max(v)

def scale(a,s):
    if not isinstance(s,F): raise ContractError('EXACT_FRACTION_REQUIRED')
    return times(a,(s,s))

def mag(a):
    return max(abs(a[0]),abs(a[1]))

def check_rule(mass,nodes,weights):
    if not isinstance(mass,F) or mass<0: raise ContractError('EXACT_NONNEGATIVE_MASS_REQUIRED')
    if len(nodes)!=len(weights): raise ContractError('WEIGHT_NODE_COUNT')
    if any(not isinstance(x,F) or not 0<x<1 for x in nodes):
        raise ContractError('EXACT_INTERIOR_NODE_REQUIRED')
    if any(a>=b for a,b in zip(nodes,nodes[1:])): raise ContractError('NODE_ORDER')
    for w in weights:
        if box(w)[0]<0: raise ContractError('NEGATIVE_WEIGHT')

def moment_defects(mass,nodes,weights):
    """Integral x^k/k! dnu, k=0..3. Never impose ideal Gaussian exactness."""
    check_rule(mass,nodes,weights)
    out=[]
    for k in range(4):
        c=mass/F(factorial(k+1)); v=(c,c)
        for x,w in zip(nodes,weights): v=plus(v,neg(scale(w,x**k/F(factorial(k)))))
        out.append(v)
    return out

def hinge_coefficient(mass,nodes,weights,xi,order,*,trace='right'):
    """Integral (x-xi)_+^r/r! dnu; r=0 uses the specified value at an atom."""
    check_rule(mass,nodes,weights)
    if not isinstance(xi,F) or not 0<=xi<=1: raise ContractError('EXACT_EVENT_POSITION_REQUIRED')
    if isinstance(order,bool) or not isinstance(order,int) or not 0<=order<=3:
        raise ContractError('JUMP_ORDER')
    if trace not in ('left','right'): raise ContractError('ATOM_TRACE_REQUIRED')
    c=mass*(1-xi)**(order+1)/F(factorial(order+1)); v=(c,c)
    for x,w in zip(nodes,weights):
        if x>xi or (x==xi and order==0 and trace=='right'):
            v=plus(v,neg(scale(w,(x-xi)**order/F(factorial(order)))))
    return v

def kernel_polynomial(mass,nodes,weights,active_after):
    """Interval power coefficients of P4(t)=int (x-t)_+^3/6 dnu."""
    p=[(mass*F((-1)**j*comb(4,j),24),)*2 for j in range(5)]
    for x,w in zip(nodes,weights):
        if x>active_after:
            for j in range(4):
                p[j]=plus(p[j],neg(scale(w,F((-1)**j*comb(3,j),6)*x**(3-j))))
    return p

def bernstein(p,a,b):
    """Exact interval power-to-Bernstein transform on [a,b]."""
    n=len(p)-1; local=[]
    for j in range(n+1):
        v=(F(0),F(0))
        for i in range(j,n+1):
            v=plus(v,scale(p[i],F(comb(i,j))*a**(i-j)*(b-a)**j))
        local.append(v)
    result=[]
    for k in range(n+1):
        v=(F(0),F(0))
        for j in range(k+1): v=plus(v,scale(local[j],F(comb(k,j),comb(n,j))))
        result.append(v)
    return result

def peano_l1(mass,nodes,weights,*,subdivisions=16):
    """Enclose integral |P4| for EVERY fixed admissible weight choice.

    Bernstein convexity proves a bound over whole subintervals. Nonnegative
    coefficients permit exact signed integration. Mixed signs use triangle
    inequality under positive Bernstein basis, not sampled extrema.
    """
    check_rule(mass,nodes,weights)
    if isinstance(subdivisions,bool) or not isinstance(subdivisions,int) or subdivisions<1:
        raise ContractError('POSITIVE_SUBDIVISIONS_REQUIRED')
    cuts=[F(0),*nodes,F(1)]; lo=hi=F(0); nsub=mixed=0
    signed=moment_k4=mass/F(120)
    signed_box=(signed,signed)
    for x,w in zip(nodes,weights): signed_box=plus(signed_box,neg(scale(w,x**4/F(24))))
    for a,b in zip(cuts,cuts[1:]):
        p=kernel_polynomial(mass,nodes,weights,(a+b)/2)
        for j in range(subdivisions):
            l=a+(b-a)*F(j,subdivisions); r=a+(b-a)*F(j+1,subdivisions)
            beta=bernstein(p,l,r); avg=(F(0),F(0))
            for v in beta: avg=plus(avg,scale(v,(r-l)/len(beta)))
            if all(v[0]>=0 for v in beta): ll,hh=avg
            elif all(v[1]<=0 for v in beta): ll,hh=-avg[1],-avg[0]
            else:
                ll=max(F(0),avg[0],-avg[1])
                hh=(r-l)*sum((mag(v) for v in beta),F(0))/len(beta); mixed+=1
            lo+=ll;hi+=hh;nsub+=1
    return {'l1':(lo,hi),'signed_integral':signed_box,'whole_subintervals':nsub,'mixed_sign_subintervals':mixed}

def certify_kernel_error(mass,nodes,weights,*,anchor_derivatives=None,
                         fourth_bound=None,jumps=None,partition_complete=False,
                         homotopy_uniform=False,subdivisions=16):
    """Conditional full-coupled homotopy kernel quadrature enclosure.

    anchor_derivatives[k] encloses K^(k)(0+) with LOCAL x derivatives.
    jumps consists of (xi,r,J_box,trace). Its completeness and a uniform K''''
    bound on each smooth piece are caller proof obligations. Empty jumps must
    be explicitly supplied and justified, not inferred from missing data.
    """
    if anchor_derivatives is None or fourth_bound is None or jumps is None:
        raise MissingPremise('KERNEL_DERIVATIVES_JUMPS_AND_REGULAR_BOUND_REQUIRED')
    if not partition_complete or not homotopy_uniform:
        raise MissingPremise('COMPLETE_PARTITION_AND_FULL_HOMOTOPY_PROOF_REQUIRED')
    if len(anchor_derivatives)!=4: raise ContractError('FOUR_ANCHOR_DERIVATIVES')
    if not isinstance(fourth_bound,F) or fourth_bound<0: raise ContractError('EXACT_REGULAR_BOUND_REQUIRED')
    ds=moment_defects(mass,nodes,weights); center=(F(0),F(0))
    for d,v in zip(ds,anchor_derivatives): center=plus(center,times(d,box(v)))
    for xi,r,j,trace in jumps:
        if not 0<xi<1: raise ContractError('INTERIOR_JUMP_REQUIRED')
        center=plus(center,times(box(j),hinge_coefficient(mass,nodes,weights,xi,r,trace=trace)))
    remainder=fourth_bound*peano_l1(mass,nodes,weights,subdivisions=subdivisions)['l1'][1]
    return {'interval':(center[0]-remainder,center[1]+remainder),
            'anchor_and_jump':center,'regular_radius':remainder,
            'classification':'CONDITIONAL_ON_EXTERNALLY_PROVED_KERNEL_PREMISES'}
