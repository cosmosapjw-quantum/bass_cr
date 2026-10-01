"""Validated rational reference certificate from archived polynomial coefficients.

No native library, time propagation, or two-center operator query is used.
Every certified numerical bound is a Fraction endpoint. Floats are read only
as their exact binary values, or printed as explicitly non-authoritative display.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import comb, isqrt
from pathlib import Path
import argparse
import hashlib
import json
import platform
import time

BITS=256
GRID=1<<BITS

def down(x):
    x=F(x); return F((x.numerator*GRID)//x.denominator,GRID)

def up(x):
    x=F(x); return F(-((-x.numerator*GRID)//x.denominator),GRID)

@dataclass(frozen=True)
class I:
    lo:F
    hi:F
    def __init__(self,lo,hi=None):
        lo=F(lo); hi=lo if hi is None else F(hi)
        if lo>hi: raise ValueError('reversed interval')
        # Exact point rationals stay exact. Nonzero-width enclosures are rounded
        # outward to control denominator growth, preserving set inclusion.
        object.__setattr__(self,'lo',lo if lo==hi else down(lo))
        object.__setattr__(self,'hi',hi if lo==hi else up(hi))
    def contains(self,x):return self.lo<=F(x)<=self.hi
    def __add__(self,other):
        b=interval(other); return I(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,other):return self+-interval(other)
    def __rsub__(self,other):return interval(other)+-self
    def __mul__(self,other):
        b=interval(other); p=(self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi)
        return I(min(p),max(p))
    __rmul__=__mul__
    def __truediv__(self,other):
        b=interval(other)
        if b.lo<=0<=b.hi:raise ValueError('division by interval containing zero')
        return self*I(1/b.hi,1/b.lo)
    def __rtruediv__(self,other):return interval(other)/self
    def abs_upper(self):return max(abs(self.lo),abs(self.hi))

def interval(x):return x if isinstance(x,I) else I(x)

@lru_cache(maxsize=256)
def _unit_log(x):
    """x in [1,2]; 128-term positive atanh series plus proven tail."""
    x=F(x)
    if not 1<=x<=2:raise ValueError('log reduction interval')
    z=(x-1)/(x+1); z2=z*z; term=z; s=F(0); n=128
    for k in range(n):s+=2*term/(2*k+1); term*=z2
    rem=2*term/((2*n+1)*(1-z2))
    return I(s,s+rem)

@lru_cache(maxsize=256)
def log_enclosure(x):
    """Rigorous log(x) for positive rational x, via powers of two."""
    x=F(x)
    if x<=0:raise ValueError('log argument must be positive')
    k=0
    while x>2:x/=2;k+=1
    while x<1:x*=2;k-=1
    return _unit_log(x)+k*_unit_log(F(2))

def sqrt_enclosure(x):
    x=F(x)
    if x<0:raise ValueError('negative square root')
    p=isqrt(x.numerator);q=isqrt(x.denominator)
    if p*p==x.numerator and q*q==x.denominator:return I(F(p,q))
    k=isqrt((x.numerator*GRID*GRID)//x.denominator)
    return I(F(k,GRID),F(k+1,GRID))

def mul(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out

def local_value(p,t):return sum(c*F(t)**k for k,c in enumerate(p))

def repair_coefficients(coefficients):
    """C0 average traces internally, zero exterior traces, linear lift repair."""
    result=[]
    for mode in coefficients:
        traces=[F(0)]+[(local_value(mode[i-1],1)+mode[i][0])/2 for i in range(1,len(mode))]+[F(0)]
        repaired=[]
        for i,p0 in enumerate(mode):
            p=list(map(F,p0))
            if len(p)<2:p+=[F(0)]*(2-len(p))
            left=p[0]-traces[i];right=local_value(p,1)-traces[i+1]
            p[0]-=left;p[1]+=left-right
            repaired.append(p)
        result.append(repaired)
    return result

def global_poly(p,a,h):
    out=[F(0)]*len(p)
    for k,c in enumerate(p):
        for j in range(k+1):out[j]+=c*comb(k,j)*(-a)**(k-j)/h**k
    return out

def rational_integral(p,a,b,shift=0):
    ans=F(0)
    for k,c in enumerate(p):
        if not c:continue
        e=k+shift+1
        if e==0:raise ValueError('log integral requires enclosing routine')
        if a==0 and e<0:raise ValueError('singular origin integral')
        ans+=c*(b**e-a**e)/e
    return ans

def enclosed_integral(p,a,b,shift=0):
    exact=F(0); logcoefficient=F(0)
    for k,c in enumerate(p):
        if not c:continue
        e=k+shift+1
        if e==0:
            if a==0:raise ValueError('logarithmically singular origin integral')
            logcoefficient+=c
        else:
            if a==0 and e<0:raise ValueError('singular origin integral')
            exact+=c*(b**e-a**e)/e
    if not logcoefficient:return I(exact)
    return I(exact)+logcoefficient*log_enclosure(b/a)

def gram_matrix(coefficients,edges,ell):
    n=len(ell); out=[[F(0) for _ in range(n)] for _ in range(n)]
    # L2 mass is best integrated in the local t coordinate, avoiding cancellation.
    for cell,(a,b) in enumerate(zip(edges,edges[1:])):
        h=b-a
        for i in range(n):
            for j in range(i,n):
                if ell[i]!=ell[j]:continue
                out[i][j]+=h*rational_integral(mul(coefficients[i][cell],coefficients[j][cell]),F(0),F(1))
    for i in range(n):
        for j in range(i):out[i][j]=out[j][i]
    return out

def isolated_matrices(coefficients,edges,ell):
    n=len(ell); S=gram_matrix(coefficients,edges,ell);H=[[I(0) for _ in range(n)] for _ in range(n)]
    for cell,(a,b) in enumerate(zip(edges,edges[1:])):
        h=b-a; pol=[global_poly(coefficients[i][cell],a,h) for i in range(n)]
        for i in range(n):
            for j in range(i,n):
                if ell[i]!=ell[j]:continue
                # Kinetic integral in local coordinate is rational and stable.
                dp=[k*coefficients[i][cell][k] for k in range(1,len(coefficients[i][cell]))]
                dq=[k*coefficients[j][cell][k] for k in range(1,len(coefficients[j][cell]))]
                kinetic=rational_integral(mul(dp,dq),F(0),F(1))/(2*h)
                prod=mul(pol[i],pol[j]); value=I(kinetic)-enclosed_integral(prod,a,b,-1)
                if ell[i]:value+=F(ell[i]*(ell[i]+1),2)*enclosed_integral(prod,a,b,-2)
                H[i][j]+=value
    for i in range(n):
        for j in range(i):H[i][j]=H[j][i]
    return S,H

def transpose(A):return [list(row) for row in zip(*A)]
def matmul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def subtract(A,B):return [[a-b for a,b in zip(ar,br)] for ar,br in zip(A,B)]
def plus(A,B):return [[a+b for a,b in zip(ar,br)] for ar,br in zip(A,B)]
def block(A,rows,cols):return [[A[i][j] for j in cols] for i in rows]

def inverse(A):
    n=len(A); a=[[F(x) for x in row]+[F(i==j) for j in range(n)] for i,row in enumerate(A)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:raise ValueError('singular rational matrix')
        a[k],a[pivot]=a[pivot],a[k];d=a[k][k];a[k]=[x/d for x in a[k]]
        for i in range(n):
            if i!=k:
                v=a[i][k];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
    return [row[n:] for row in a]

def spectral_bounds(A):
    bounds=[]
    for i,row in enumerate(A):
        center=interval(row[i]);radius=sum(interval(v).abs_upper() for j,v in enumerate(row) if j!=i)
        bounds.append((center.lo-radius,center.hi+radius))
    return min(x[0] for x in bounds),max(x[1] for x in bounds)

def block_certificate(S,H,selected,complement):
    if sorted(selected+complement)!=list(range(len(S))) or set(selected)&set(complement):raise ValueError('not a partition')
    SA=block(S,selected,selected);SB=block(S,selected,complement); SC=block(S,complement,complement)
    X=matmul(inverse(SA),SB);XT=transpose(X)
    K=subtract(SC,matmul(transpose(SB),X))
    HA=block(H,selected,selected);HAB=block(H,selected,complement);HB=transpose(HAB);HC=block(H,complement,complement)
    HX=matmul(HA,X)
    HCorth=plus(subtract(subtract(HC,matmul(XT,HAB)),matmul(HB,X)),matmul(XT,HX))
    R=subtract(HB,matmul(XT,HA))
    sa_min,sa_max=spectral_bounds(SA);k_min,k_max=spectral_bounds(K)
    neg_min,_=spectral_bounds([[-v for v in row] for row in HA]);hcomp_min,_=spectral_bounds(HCorth)
    if min(sa_min,k_min,neg_min,hcomp_min)<=0:raise ValueError('failed positive Gram / negative-positive spectral separation')
    a=neg_min/sa_max;d=hcomp_min/k_max
    r2=sum(interval(v).abs_upper()**2 for row in R for v in row)/(sa_min*k_min)
    r=sqrt_enclosure(r2).hi;delta=min(F(1),r/(a+d))
    return {'a_lower':a,'d_lower':d,'r_upper':r,'delta_selector_upper':delta,
       'S_selected_lower':sa_min,'S_complement_lower':k_min,'S_selected_upper':sa_max,'S_complement_upper':k_max,
       'S_orthogonal_complement_coordinates':X,'S_complement_gram':K,'H_complement_interval':HCorth,
       'H_selected_interval':HA,'H_residual_interval':R,
       'negative_rank_radial':len(selected),'positive_rank_radial':len(complement)}

def projector_bridge(original,repaired,edges,ell,selected):
    S0=gram_matrix(original,edges,ell);smin,_=spectral_bounds(block(S0,selected,selected))
    if smin<=0:raise ValueError('original selected Gram not certified positive')
    difference=[[[x-y for x,y in zip(p,q)] for p,q in zip(m,n)] for m,n in zip(original,repaired)]
    G=gram_matrix(difference,edges,ell)
    # Full angular space is orthogonal direct sum over (l,m). The same radial
    # block repeats, so maximum block trace bounds its operator norm squared.
    block_traces={l:sum(G[i][i] for i in selected if ell[i]==l) for l in set(ell[i] for i in selected)}
    e2=max(block_traces.values()); eta=min(F(1),sqrt_enclosure(e2/smin).hi)
    return {'eta_projector_upper':eta,'original_selected_gram_lower':smin,
        'repair_operator_norm_squared_upper':e2,'repair_gram_exact':G,'original_gram_exact':S0,
        'selected_l_block_trace_exact':block_traces}

def encode(x):
    if isinstance(x,F):return {'rational':str(x),'display_float':float(x)}
    if isinstance(x,I):return {'lower':str(x.lo),'upper':str(x.hi),'display_lower':float(x.lo),'display_upper':float(x.hi)}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def exact_data(coefficients,edges,ell):
    return {'edges':list(map(str,edges)),'l':ell,'coefficients':[[list(map(str,p)) for p in m] for m in coefficients]}

def certify_reference(inputs):
    import numpy as np
    meta=json.loads((inputs/'BASIS.json').read_text())
    with np.load(inputs/'BASIS.npz',allow_pickle=False) as ar:
        coefficients=[[[F(float(x)) for x in p] for p in m] for m in ar['coefficients']]
        edges=[F(float(x)) for x in ar['edges']]
    ell=[m['l'] for m in meta['modes']]
    if ell!=[0,0,0,1,1] or len(edges)!=41 or edges[0]!=0 or edges[-1]!=64:raise ValueError('unexpected B0 bank shape')
    if any(a>=b for a,b in zip(edges,edges[1:])):raise ValueError('nonincreasing edges')
    selected=[0,1,3];complement=[2,4]
    if [i for i,m in enumerate(meta['modes']) if m['energy']<0]!=selected:raise ValueError('semantic labels disagree')
    repaired=repair_coefficients(coefficients)
    assert all(m[0][0]==0 and local_value(m[-1],1)==0 for m in repaired)
    assert all(local_value(m[j],1)==m[j+1][0] for m in repaired for j in range(len(m)-1))
    S,H=isolated_matrices(repaired,edges,ell)
    spectral=block_certificate(S,H,selected,complement)
    bridge=projector_bridge(coefficients,repaired,edges,ell,selected)
    total=min(F(1),bridge['eta_projector_upper']+spectral['delta_selector_upper'])
    refdata=exact_data(repaired,edges,ell);refsha=hashlib.sha256(json.dumps(refdata,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    selector_definition={'schema':'BASS_R4R_REFERENCE_SPECTRAL_SELECTOR_V1','reference_coefficients_sha256':refsha,
       'operator':'Coulomb Z=1 weak Galerkin Hamiltonian on repaired 9-channel isolated projectile retained span',
       'selector':'exact negative spectral projector','full_angular_multiplets':True,'negative_rank':5,'positive_rank':4}
    selector_sha=hashlib.sha256(json.dumps(selector_definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'schema':'BASS_R4R_EXACT_REFERENCE_CERTIFICATE_V1','status':'STATIC_REFERENCE_AND_SELECTOR_MAPPING_VALIDATED',
       'method':'exact rational polynomial repair/mass; 256-bit outward dyadic intervals; proved rational log remainder; exact Schur coordinates',
       'input_pins':{name:{'sha256':hashlib.sha256((inputs/name).read_bytes()).hexdigest(),'bytes':(inputs/name).stat().st_size} for name in ('BASIS.json','BASIS.npz')},
       'archived_basis_identity':meta['identity'],'reference_coefficients_sha256':refsha,'selector_definition':selector_definition,'selector_identity_sha256':selector_sha,
       'support_radius_a0':F(64),'selected_radial_modes':selected,'positive_radial_modes':complement,
       'selected_angular_rank':sum(2*ell[i]+1 for i in selected),'positive_angular_rank':sum(2*ell[i]+1 for i in complement),
       'reference_gram_exact':S,'reference_isolated_H_interval':H,'reference_gram_spectral_bounds':spectral_bounds(S),
       'reference_block_certificate':spectral,'same_hilbert_space_projector_mapping':bridge,
       'original_to_negative_reference_projector_upper':total,
       'observable_error_for_unit_norm_common_state_upper':total,
       'same_state_comparison_only':True,'new_reference_adopted':False,'native_calls':0,'new_two_center_operator_queries':0,'time_propagations':0,
       'claim_limits':['No original fixed-selector asymptotic-limit existence proof','No finite bridge or dynamical state-map certificate','No old temporal gate transfer','No tail/global-continuum bound for archived B0'],
       'claim_ceilings':{'capture':False,'production':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,'continuous_global_supremum_bound':False,'continuous_trajectory_error_bound':False}}
    return result,refdata

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    if args.out.exists():raise SystemExit('create-only output directory already exists')
    args.out.mkdir(parents=True);t=time.perf_counter();result,reference=certify_reference(args.inputs)
    (args.out/'REFERENCE_CERTIFICATE.json').write_text(json.dumps(encode(result),indent=2,allow_nan=False)+'\n')
    (args.out/'EXACT_REPAIRED_REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n')
    receipt={'schema':'BASS_R4R_REFERENCE_EXECUTION_V1','status':'PASS','wall_seconds':time.perf_counter()-t,'python':platform.python_version(),
       'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_pins':result['input_pins'],'native_calls':0,'new_two_center_operator_queries':0,'time_propagations':0}
    (args.out/'EXECUTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(encode({k:result[k] for k in ('status','reference_coefficients_sha256','selector_identity_sha256','original_to_negative_reference_projector_upper')}),indent=2))
    print(json.dumps(encode({k:result['reference_block_certificate'][k] for k in ('a_lower','d_lower','r_upper','delta_selector_upper')}),indent=2))
if __name__=='__main__':main()
