"""Exact-rational polynomial weak-metric envelopes for a retained rank-two span.

The input polynomial model is defined exactly. Uniform remainder inputs are
assumptions until separately admitted. No result here approves physical data.
K means H-i*hbar*D, including the complete moving-basis connection.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb, isfinite, isqrt
from typing import Any
import hashlib
import json

class ContractError(ValueError):
    pass

def rat(x: Any) -> F:
    if isinstance(x, bool):
        raise ContractError('booleans are not bounds')
    if isinstance(x, float) and not isfinite(x):
        raise ContractError('nonfinite input')
    try:
        return F(x)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ContractError('invalid rational') from exc

@dataclass(frozen=True)
class CQ:
    re: F = F(0)
    im: F = F(0)
    def __post_init__(self):
        object.__setattr__(self, 're', rat(self.re))
        object.__setattr__(self, 'im', rat(self.im))
    def __add__(self, b):
        b = cq(b); return CQ(self.re+b.re, self.im+b.im)
    __radd__ = __add__
    def __neg__(self): return CQ(-self.re, -self.im)
    def __sub__(self, b): return self + (-cq(b))
    def __rsub__(self, b): return cq(b) + (-self)
    def __mul__(self, b):
        b = cq(b)
        return CQ(self.re*b.re-self.im*b.im, self.re*b.im+self.im*b.re)
    __rmul__ = __mul__
    def __truediv__(self, b):
        b = cq(b); d = b.re*b.re+b.im*b.im
        if not d: raise ContractError('zero complex divisor')
        a = self*b.conj(); return CQ(a.re/d, a.im/d)
    def conj(self): return CQ(self.re, -self.im)
    def abs2(self): return self.re*self.re+self.im*self.im
    def __bool__(self): return bool(self.re or self.im)

def cq(x):
    if isinstance(x, CQ): return x
    if isinstance(x, complex): return CQ(rat(x.real), rat(x.imag))
    return CQ(rat(x))

@dataclass(frozen=True, init=False)
class P:
    """Power coefficients in physical time t measured in ta."""
    c: tuple[CQ, ...]
    def __init__(self, coeffs=0):
        if isinstance(coeffs, P): vals = coeffs.c
        elif isinstance(coeffs, (tuple, list)): vals = tuple(cq(x) for x in coeffs)
        else: vals = (cq(coeffs),)
        if not vals: vals = (CQ(),)
        while len(vals)>1 and not vals[-1]: vals = vals[:-1]
        object.__setattr__(self, 'c', vals)
    def __add__(self, b):
        b=P(b); n=max(len(self.c),len(b.c))
        return P([(self.c[k] if k<len(self.c) else CQ())+
                  (b.c[k] if k<len(b.c) else CQ()) for k in range(n)])
    __radd__ = __add__
    def __neg__(self): return P([-x for x in self.c])
    def __sub__(self,b): return self+(-P(b))
    def __rsub__(self,b): return P(b)+(-self)
    def __mul__(self,b):
        b=P(b); out=[CQ()]*(len(self.c)+len(b.c)-1)
        for i,a in enumerate(self.c):
            if a:
                for j,bb in enumerate(b.c):
                    if bb: out[i+j]=out[i+j]+a*bb
        return P(out)
    __rmul__ = __mul__
    def __truediv__(self,b):
        b=P(b)
        if len(b.c)!=1: raise ContractError('polynomial division is not scalar')
        return P([a/b.c[0] for a in self.c])
    def conj(self): return P([x.conj() for x in self.c])
    def deriv(self): return P([self.c[k]*k for k in range(1,len(self.c))])
    def value(self,t):
        t=cq(t); a=CQ()
        for c in reversed(self.c): a=a*t+c
        return a
    def __bool__(self): return any(bool(x) for x in self.c)
    def __eq__(self,b):
        try: return self.c==P(b).c
        except (ContractError, TypeError): return False
    def json(self): return [[str(x.re),str(x.im)] for x in self.c]

ZERO=P(0)
I=CQ(0,1)

def sqrt_bounds(x, bits=192):
    x=rat(x)
    if x<0 or not isinstance(bits,int) or isinstance(bits,bool) or not 16<=bits<=4096:
        raise ContractError('nonnegative radicand and 16..4096 bits required')
    q=1<<bits; k=isqrt(x.numerator*q*q//x.denominator)
    exact=k*k*x.denominator==x.numerator*q*q
    return F(k,q),F(k if exact else k+1,q)

def bernstein_coefficients(poly, interval):
    p=P(poly); a,b=map(rat,interval)
    if b<a: raise ContractError('reversed time interval')
    n=len(p.c)-1; d=b-a
    q=[sum((p.c[j]*comb(j,k)*a**(j-k)*d**k for j in range(k,n+1)),CQ())
       for k in range(n+1)]
    return tuple(sum((q[k]*F(comb(j,k),comb(n,k)) for k in range(j+1)),CQ())
                 for j in range(n+1))

def rectangle(p,interval):
    c=bernstein_coefficients(p,interval)
    return min(x.re for x in c),max(x.re for x in c),min(x.im for x in c),max(x.im for x in c)

def abs2_upper(p,interval):
    a,b,c,d=rectangle(p,interval)
    return max(abs(a),abs(b))**2+max(abs(c),abs(d))**2

def matrix(x):
    try: out=tuple(tuple(P(v) for v in row) for row in x)
    except (TypeError,ValueError) as exc: raise ContractError('invalid matrix') from exc
    if not out or not out[0] or any(len(r)!=len(out[0]) for r in out):
        raise ContractError('nonempty rectangular matrix required')
    return out

def dagger(A): return tuple(tuple(A[j][i].conj() for j in range(len(A))) for i in range(len(A[0])))
def madd(A,B):
    if (len(A),len(A[0]))!=(len(B),len(B[0])): raise ContractError('matrix shape mismatch')
    return tuple(tuple(x+y for x,y in zip(a,b)) for a,b in zip(A,B))
def mscale(A,c): return tuple(tuple(x*c for x in row) for row in A)
def msub(A,B): return madd(A,mscale(B,-1))
def mmul(A,B):
    if len(A[0])!=len(B): raise ContractError('matrix product shape mismatch')
    return tuple(tuple(sum((A[i][k]*B[k][j] for k in range(len(B))),ZERO)
                       for j in range(len(B[0]))) for i in range(len(A)))
def mderiv(A): return tuple(tuple(v.deriv() for v in row) for row in A)
def submatrix(A,rows,cols): return tuple(tuple(A[i][j] for j in cols) for i in rows)
def norm_upper(A,interval):
    return sqrt_bounds(sum(abs2_upper(v,interval) for row in A for v in row))[1]
def hermitian(A): return A==dagger(A)
def lower_metric(A,interval):
    if len(A)!=len(A[0]) or not hermitian(A): raise ContractError('exact Hermitian metric required')
    vals=[]
    for i,row in enumerate(A):
        lo,_,imlo,imhi=rectangle(row[i],interval)
        if imlo or imhi: raise ContractError('nonreal metric diagonal')
        vals.append(lo-sum(sqrt_bounds(abs2_upper(v,interval))[1] for j,v in enumerate(row) if j!=i))
    return min(vals)

def _check(S,K,retained,hbar,interval):
    S,K=matrix(S),matrix(K); n=len(S); hb=rat(hbar); a,b=map(rat,interval)
    if n<3 or len(S[0])!=n or len(K)!=n or len(K[0])!=n: raise ContractError('matching square n>=3 matrices required')
    if (len(retained)!=2 or len(set(retained))!=2 or
        any(not isinstance(i,int) or isinstance(i,bool) or not 0<=i<n for i in retained)):
        raise ContractError('two distinct retained coordinate indices required')
    if hb<=0 or b<a: raise ContractError('positive hbar and ordered interval required')
    if not hermitian(S): raise ContractError('no metric symmetrization allowed')
    return S,K,tuple(retained),hb,(a,b)

def residual_polynomials(S,K,retained=(0,1),hbar=1):
    """Return exact numerator N=det(G)KJ-SJ adj(G)K_R and metric defect."""
    S,K,R,hb,_=_check(S,K,retained,hbar,(0,0)); n=len(S)
    G=submatrix(S,R,R); KR=submatrix(K,R,R)
    adj=((G[1][1],-G[0][1]),(-G[1][0],G[0][0]))
    det=G[0][0]*G[1][1]-G[0][1]*G[1][0]
    N=msub(mscale(submatrix(K,range(n),R),det),
           mmul(mmul(submatrix(S,range(n),R),adj),KR))
    if any(bool(v) for row in submatrix(N,R,(0,1)) for v in row):
        raise ContractError('Galerkin numerator identity failed')
    Gamma=madd(mderiv(S),mscale(msub(dagger(K),K),I/hb))
    if not hermitian(Gamma): raise ContractError('metric defect algebra failed')
    return S,K,G,KR,adj,det,N,Gamma

@dataclass(frozen=True)
class Remainders:
    epsilon_S: Any
    epsilon_K: Any
    epsilon_Sdot: Any
    evidence_id: str
    bound_type: str='ASSUMED_UNIFORM_OPERATOR_REMAINDERS'
    energy_unit: str='Eh'
    time_unit: str='ta'
    def values(self):
        if self.bound_type!='ASSUMED_UNIFORM_OPERATOR_REMAINDERS':
            raise ContractError('point/refinement/fit errors are not uniform operator remainders')
        if (self.energy_unit,self.time_unit)!=('Eh','ta') or not isinstance(self.evidence_id,str) or not self.evidence_id.strip():
            raise ContractError('remainder identity and units required')
        vals=tuple(rat(x) for x in (self.epsilon_S,self.epsilon_K,self.epsilon_Sdot))
        if min(vals)<0: raise ContractError('negative remainder')
        return vals

def exact_pair_certificate(S,K,interval,retained=(0,1),hbar=1,remainders=None):
    """Enclose a complete polynomial time interval, not merely sampled values.

    Remainders refer to the same physical S,K,Sdot; no derivative of K or
    spectral gap is needed for this baseline weak-residual estimate.
    """
    S,K,R,hb,Z=_check(S,K,retained,hbar,interval)
    S,K,G,KR,adj,det,N,Gamma=residual_polynomials(S,K,R,hb)
    sp=lower_metric(S,Z); gp=lower_metric(G,Z)
    if min(sp,gp)<=0: raise ContractError('continuous metric positivity not certified')
    dl=rectangle(det,Z)[0]; dl=max(dl,gp*gp)
    np=norm_upper(N,Z); Bp=np/dl
    epsS=epsK=epsSd=F(0)
    if remainders is not None:
        if not isinstance(remainders,Remainders): raise ContractError('typed uniform remainder contract required')
        epsS,epsK,epsSd=remainders.values()
    sa,ga=sp-epsS,gp-epsS
    if min(sa,ga)<=0: raise ContractError('remainder consumes metric positivity')
    # Bound B_actual-B_polynomial with two inverse metrics, never assume
    # a fitted polynomial equals the unknown atomic operator.
    kr=norm_upper(KR,Z)+epsK
    sj=norm_upper(submatrix(S,range(len(S)),R),Z)
    Bdelta=epsK+epsS*kr/ga+sj*(epsS*kr/(ga*gp)+epsK/gp)
    rootlo=sqrt_bounds(sa*ga)[0]
    if rootlo<=0: raise ContractError('denominator precision insufficient')
    residual=(Bp+Bdelta)/(hb*rootlo)
    gamma=norm_upper(Gamma,Z)+epsSd+2*epsK/hb
    gammaR=norm_upper(submatrix(Gamma,R,R),Z)+epsSd+2*epsK/hb
    af=gamma/(2*sa); ar=gammaR/(2*ga)
    rate=None
    if remainders is None:
        # P1s measurement is the second retained physical column, not |d_1|^2.
        p=G[1][1]
        T=tuple(tuple(G[i][1]*G[1][j] for j in range(2)) for i in range(2))
        AN=mscale(mmul(adj,KR),-I/hb)
        RN=madd(mscale(msub(mscale(mderiv(T),p),mscale(T,p.deriv())),det),
                 mscale(madd(mmul(dagger(AN),T),mmul(T,AN)),p))
        pl=max(rectangle(p,Z)[0],gp)
        rate=norm_upper(RN,Z)/(dl*pl*pl*gp)
    data={'S':[[p.json() for p in r] for r in S], 'K':[[p.json() for p in r] for r in K],
          'retained':list(R),'hbar':str(hb)}
    return {'schema':'R4AK_POLYNOMIAL_WEAK_PAIR_TUBE_V1',
            'bound_type':'EXACT_POLYNOMIAL_REFERENCE' if remainders is None else 'CONDITIONAL_UNIFORM_OPERATOR_REMAINDERS',
            'model_sha256':hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'interval_ta':[str(x) for x in Z], 'retained':list(R),'hbar_Eh_ta':str(hb),
            'S_lower':str(sa),'G_lower':str(ga),'polynomial_detG_lower':str(dl),
            'polynomial_numerator_norm_upper':str(np),'polynomial_B_upper_Eh':str(Bp),
            'B_remainder_upper_Eh':str(Bdelta),'residual_upper_per_ta':str(residual),
            'metric_defect_upper_per_ta':str(gamma),'full_growth_upper_per_ta':str(af),
            'retained_growth_upper_per_ta':str(ar),
            'internal_measurement_rate_upper_per_ta':None if rate is None else str(rate),
            'spectral_gap_required':False,'K_derivative_required':False,
            'whitening_derivative_required':False,'frame_connection_required_in_K':True,
            'Galerkin_orthogonality_exact':True,'physical_admission':False,
            'physical_bridge_upper':None,
            'remainder_evidence':None if remainders is None else remainders.evidence_id}

def exp_upper(x):
    """Rational upper enclosure on exp(x), 0<=x<=32; explicit series tail."""
    x=rat(x)
    if not 0<=x<=32: raise ContractError('growth exceeds registered reference range [0,32]')
    if not x: return F(1)
    # Scaling avoids slow convergence and gives a positive ratio remainder.
    m=0; y=x
    while y>1: y/=2; m+=1
    term=total=F(1)
    for k in range(1,33): term*=y/k; total+=term
    tail=(term*y/33)/(1-y/34)
    return (total+tail)**(1<<m)

def propagate_certificates(certificates,initial_error=0,retained_norm=1):
    """Conditional finite-model state error with explicit contiguous slabs."""
    E,N=rat(initial_error),rat(retained_norm)
    if min(E,N)<0 or not certificates: raise ContractError('nonnegative initial bounds and nonempty slabs required')
    model=certificates[0]['model_sha256']; end=None; total_internal=F(0); internal_known=True
    for c in certificates:
        if c.get('schema')!='R4AK_POLYNOMIAL_WEAK_PAIR_TUBE_V1' or c.get('physical_admission') is not False:
            raise ContractError('unexpected certificate or unauthorized physical promotion')
        if c['model_sha256']!=model: raise ContractError('different polynomial models cannot be silently joined')
        a,b=map(rat,c['interval_ta'])
        if b<a or end is not None and a!=end: raise ContractError('missing/overlapping time slab')
        end=b; T=b-a
        r,af,ar=map(rat,(c['residual_upper_per_ta'],c['full_growth_upper_per_ta'],c['retained_growth_upper_per_ta']))
        if min(r,af,ar)<0: raise ContractError('invalid negative envelope')
        rate=c['internal_measurement_rate_upper_per_ta']
        if rate is None: internal_known=False
        else: total_internal+=rat(rate)*T*N*N*exp_upper(2*ar*T)
        E=exp_upper(af*T)*E+r*T*exp_upper(max(af,ar)*T)*N
        N=exp_upper(ar*T)*N
    return {'schema':'R4AK_FINITE_MODEL_PROPAGATION_V1','state_error_upper':str(E),
            'retained_norm_upper':str(N),'same_observable_error_upper':str(E*(2*N+E)),
            'internal_measurement_change_upper':str(total_internal) if internal_known else None,
            'physical_bridge_upper':None,'physical_admission':False}
