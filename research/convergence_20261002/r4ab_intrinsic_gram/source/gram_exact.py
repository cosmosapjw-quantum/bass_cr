"""Exact arithmetic for the immutable R4X real, degree-four radial candidate.

Stored FP64 endpoints, bubbles and edges are interpreted as exact rationals.
No eigenvalue reconstruction, normalization, orthogonalization or source mutation.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math
import numpy as np

SCHEMA='BASS_R4X_CONTINUOUS_ENDPOINT_BASIS_V1'
ALGORITHM='u=(1-s)*left+s*right+s*(1-s)*q(s); degree=4; no renormalization'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def array_digest(a):return digest({'shape':list(a.shape),'dtype':a.dtype.str,'bytes_sha256':hashlib.sha256(a.tobytes(order='C')).hexdigest()})
def frozen(a):
    a=np.ascontiguousarray(a)
    return np.frombuffer(a.tobytes(),dtype=a.dtype).reshape(a.shape)
def rational(x):
    if isinstance(x,F):return x
    if isinstance(x,(bool,complex,np.complexfloating)):raise ValueError('finite real coefficient required')
    v=float(x)
    if not math.isfinite(v):raise ValueError('finite real coefficient required')
    return F(v)
def panel_coefficients(left,right,bubble):
    if len(bubble)!=3:raise ValueError('degree-four endpoint/bubble representation required')
    l,r=rational(left),rational(right);q0,q1,q2=map(rational,bubble)
    return (l,r-l+q0,q1-q0,q2-q1,-q2)
def product_integral(a,b):
    return sum((x*y/F(i+j+1) for i,x in enumerate(a) for j,y in enumerate(b)),F(0))
def differentiate(c):return tuple(i*c[i] for i in range(1,len(c)))

def validate_arrays(edges,endpoints,bubbles):
    arrays=[np.asarray(x) for x in (edges,endpoints,bubbles)]
    e,p,q=arrays
    if any(x.dtype!=np.dtype('float64') or not np.isfinite(x).all() for x in arrays):raise ValueError('finite FP64 arrays required')
    if e.ndim!=1 or len(e)<2 or e[0]!=0 or np.any(np.diff(e)<=0):raise ValueError('increasing mesh from zero required')
    if p.ndim!=2 or not 1<=len(p)<=32 or p.shape[1]!=len(e) or q.shape!=(len(p),len(e)-1,3):raise ValueError('bank shape mismatch')
    if np.any(p[:,0]!=0) or np.any(p[:,-1]!=0):raise ValueError('Dirichlet traces required')
    return e,p,q

@dataclass(frozen=True)
class Bank:
    edges:np.ndarray
    endpoints:np.ndarray
    bubbles:np.ndarray
    identity:str
    modes:tuple
    channel_records:tuple
    input_pins:tuple

    @property
    def channel_modes(self):return tuple(i for i,m in enumerate(self.modes) for _ in range(2*m['l']+1))
    @property
    def channel_lm(self):return tuple((r['l'],r['m']) for r in self.channel_records)

def load_bank(directory,contract,original_source):
    directory=Path(directory);original_source=Path(original_source)
    for name,key in [('CANDIDATE.json','candidate_metadata_sha256'),('CANDIDATE.npz','candidate_npz_sha256')]:
        if sha(directory/name)!=contract[key]:raise ValueError('candidate SHA mismatch: '+name)
    meta=json.loads((directory/'CANDIDATE.json').read_text());payload=dict(meta);identity=payload.pop('identity',None)
    if identity!=contract['parent_candidate'] or digest(payload)!=identity or meta['schema']!=SCHEMA or meta['algorithm']!=ALGORITHM:raise ValueError('candidate metadata identity mismatch')
    if any(meta[k] is not False for k in ['production_adopted','legacy_native_compatible','original_nodal_data_recovered']):raise ValueError('candidate scope mismatch')
    for n,h in meta['source_hashes'].items():
        if sha(original_source/n)!=h:raise ValueError('historical definition source mismatch')
    with np.load(directory/'CANDIDATE.npz',allow_pickle=False) as z:
        if set(z.files)!=set(meta['array_digests']):raise ValueError('unexpected payload keys')
        a={k:np.array(z[k],copy=True) for k in z.files}
    if {k:array_digest(v) for k,v in a.items()}!=meta['array_digests']:raise ValueError('typed array digest mismatch')
    e,p,q=validate_arrays(a['edges'],a['shared_endpoint_values'],a['bubble_coefficients'])
    if len(meta['modes'])!=len(p) or any(m['l'] not in (0,1) for m in meta['modes']):raise ValueError('this additive intrinsic angular implementation admits s+p only')
    records=[]
    for k,m in enumerate(meta['modes']):
        arr={'edges':e,'shared_endpoint_values':p[k],'bubble_coefficients':q[k],'reconstructed_nodal_values':a['reconstructed_nodal_values'][k]}
        rid=digest({'schema':SCHEMA,'algorithm':ALGORITHM,'original_mode':m,'arrays':{n:array_digest(v) for n,v in arr.items()}})
        for mm in range(-m['l'],m['l']+1):records.append({'center':0,'radial':rid,'l':m['l'],'m':mm,'energy':m['energy']})
    return Bank(frozen(e),frozen(p),frozen(q),identity,tuple(meta['modes']),tuple(records),tuple((n,sha(directory/n)) for n in ['CANDIDATE.json','CANDIDATE.npz']))

def exact_moments(edges,endpoints,bubbles):
    e,p,q=validate_arrays(edges,endpoints,bubbles);nm=len(p);ne=len(e)-1
    c=[[panel_coefficients(p[a,k],p[a,k+1],q[a,k]) for k in range(ne)] for a in range(nm)]
    matrices={name:[[F(0) for _ in range(nm)] for _ in range(nm)] for name in ('G','J','T')}
    for a in range(nm):
        for b in range(nm):
            for k in range(ne):
                h=rational(e[k+1])-rational(e[k]);ca,cb=c[a][k],c[b][k]
                matrices['G'][a][b]+=h*product_integral(ca,cb)
                matrices['J'][a][b]+=product_integral(ca,differentiate(cb))
                matrices['T'][a][b]+=product_integral(differentiate(ca),differentiate(cb))/h
    return matrices,c

def mp_inverse_moments(edges,coefficients,dps=90):
    """Evaluate exact rational/log panel expressions, not interval enclosures."""
    import mpmath as mp
    if not isinstance(dps,int) or dps<50:raise ValueError('at least 50 digits required')
    with mp.workdps(dps):
        mf=lambda x:mp.mpf(x.numerator)/x.denominator
        nm=len(coefficients);ne=len(edges)-1
        one=[[mp.mpf(0) for _ in range(nm)] for _ in range(nm)]
        two=[[mp.mpf(0) for _ in range(nm)] for _ in range(nm)]
        for k in range(ne):
            aa=rational(edges[k]);hh=rational(edges[k+1])-aa;a,h=mf(aa),mf(hh)
            if k:
                j=[mp.log1p(h/a)/h];v=[1/(a*(a+h))]
                for n in range(1,9):
                    j.append((mp.mpf(1)/n-a*j[-1])/h)
                    v.append((j[n-1]-a*v[-1])/h)
            for ia in range(nm):
                for ib in range(nm):
                    ca,cb=coefficients[ia][k],coefficients[ib][k]
                    poly=[sum((ca[i]*cb[n-i] for i in range(5) if 0<=n-i<5),F(0)) for n in range(9)]
                    if k==0:
                        if poly[0]!=0 or poly[1]!=0:raise ValueError('uncancelled origin singularity')
                        one[ia][ib]+=sum((mf(poly[n])/n for n in range(2,9)),mp.mpf(0))
                        two[ia][ib]+=sum((mf(poly[n])/(h*(n-1)) for n in range(2,9)),mp.mpf(0))
                    else:
                        one[ia][ib]+=h*sum((mf(poly[n])*j[n] for n in range(9)),mp.mpf(0))
                        two[ia][ib]+=h*sum((mf(poly[n])*v[n] for n in range(9)),mp.mpf(0))
        return {'R1':np.array([[float(x) for x in row] for row in one]),'R2':np.array([[float(x) for x in row] for row in two]),'decimal':{'R1':[[mp.nstr(x,dps) for x in row] for row in one],'R2':[[mp.nstr(x,dps) for x in row] for row in two]},'dps':dps,'certified_interval':False}
