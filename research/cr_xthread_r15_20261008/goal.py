"""Opt-in fixed-birth optical goal; exact rational integration kernels."""
from fractions import Fraction as Q
from math import factorial

class ContractError(ValueError):
    pass

def interval(v):
    if len(v)!=2: raise ContractError('INTERVAL_DIMENSION')
    a,b=map(Q,v)
    if a>b: raise ContractError('REVERSED_INTERVAL')
    return a,b

def mul(x,y):
    a,b=interval(x);c,d=interval(y)
    z=[a*c,a*d,b*c,b*d]
    return min(z),max(z)

def add(x,y): return x[0]+y[0],x[1]+y[1]

def xe(x,f):
    if len(x)!=3: raise ContractError('GAS_DIMENSION')
    x=[interval(v) for v in x]
    return x[0][0]+f*(x[1][0]+2*x[2][0]),x[0][1]+f*(x[1][1]+2*x[2][1])

def kernel(a,b,alpha,order):
    # Positive Fubini kernel: integral_a^b du integral_u^1 exp(-alpha*s) ds.
    return sum(((-alpha)**k/Q(factorial(k)*(k+1))*
                ((b-a)-(b**(k+2)-a**(k+2))/Q(k+2)) for k in range(order+1)),Q(0))

def moment(alpha,power,order):
    return sum(((-alpha)**k/Q(factorial(k)*(k+power+1)) for k in range(order+1)),Q(0))

def native_goal(initial, endpoint, alpha, density, scale, fhe):
    x0=xe([(v,v) for v in initial],fhe)[0]
    x1=xe([(v,v) for v in endpoint],fhe)[0]
    if min(x0,x1)<0 or not 0<=alpha<=1:raise ContractError('NATIVE_DOMAIN')
    # Positive endpoint shape weights (1-s), s avoid sign-dependent Taylor swaps.
    def partial(n):
        return sum(((-alpha)**k/Q(factorial(k))*(x0/Q((k+1)*(k+2))+x1/Q(k+2)) for k in range(n+1)),Q(0))
    return mul((scale*partial(5),scale*partial(6)),density)

def cell_goal(panels, incoming, coupling, alpha, density, scale, fhe):
    alpha,scale,fhe=map(Q,(alpha,scale,fhe));density=interval(density)
    if not 0<=alpha<=1 or scale<=0 or density[0]<=0 or not 0<=fhe<=1:
        raise ContractError('CLOCK_DENSITY_DOMAIN')
    if len(coupling)!=3 or any(Q(c)<0 for c in coupling):raise ContractError('COUPLING_DOMAIN')
    pos=Q(0);forcing=(Q(0),Q(0))
    for p in panels:
        a,b=interval(p['s'])
        if a!=pos or not a<b<=1: raise ContractError('PANELS_NOT_CONTIGUOUS')
        rlo,rhi=xe(p['residual'][:3],fhe)
        j=kernel(a,b,alpha,5),kernel(a,b,alpha,6)
        if j[0]<0 or j[0]>j[1]: raise ContractError('KERNEL_DOMAIN')
        forcing=add(forcing,mul((-rhi,-rlo),j));pos=b
    if pos!=1:raise ContractError('PANELS_DO_NOT_COVER_CELL')
    weight=moment(alpha,0,5),moment(alpha,0,6)
    initial=mul(xe(incoming,fhe),weight)
    rem=kernel(Q(0),Q(1),alpha,6)*sum((Q(c)*w for c,w in zip(coupling,[1,fhe,2*fhe])),Q(0))
    forcing=mul((scale*forcing[0],scale*forcing[1]),density)
    initial=mul((scale*initial[0],scale*initial[1]),density)
    rem*=scale*density[1]
    diff=add(add(initial,forcing),(-rem,rem))
    return {'forcing':forcing,'initial':initial,'remainder':rem,'difference':diff}

def encode(x):
    if isinstance(x,Q):return {'num':str(x.numerator),'den':str(x.denominator)}
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def decode(x):return Q(int(x['num']),int(x['den']))
