"""Exact radial trace obstructions and finite-metric transfer helpers.

No native operator evaluation, basis solve or time propagation. Fraction algebra
and optional reading of the already pinned BASIS.npz are the only computations.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,json

def value(p,t):return sum(x*F(t)**k for k,x in enumerate(p))
def slope(p,t,h):return sum(k*x*F(t)**(k-1) for k,x in enumerate(p) if k)/h

def squared_integral(p):
    return sum(x*y/F(i+j+1) for i,x in enumerate(p) for j,y in enumerate(p))

def mode_traces(polynomials,edges):
    p=[list(map(F,row)) for row in polynomials];e=list(map(F,edges))
    if len(e)!=len(p)+1 or e[0]!=0 or any(a>=b for a,b in zip(e,e[1:])):raise ValueError('invalid radial partition')
    jumps=[]
    for j in range(1,len(p)):
        jumps.append({'radius':e[j], 'value_jump':p[j][0]-value(p[j-1],1),
                      'derivative_jump':slope(p[j],0,e[j+1]-e[j])-slope(p[j-1],1,e[j]-e[j-1]), 'kind':'INTERNAL'})
    jumps.append({'radius':e[-1], 'value_jump':-value(p[-1],1),
                  'derivative_jump':-slope(p[-1],1,e[-1]-e[-2]),'kind':'ZERO_EXTENSION'})
    return {'origin_value':p[0][0],'origin_slope':slope(p[0],0,e[1]-e[0]), 'shells':jumps,
            'nonzero_value_jumps':sum(x['value_jump']!=0 for x in jumps),
            'nonzero_derivative_jumps':sum(x['derivative_jump']!=0 for x in jumps),
            'max_abs_value_jump':max(abs(x['value_jump']) for x in jumps),
            'max_abs_derivative_jump':max(abs(x['derivative_jump']) for x in jumps)}

def broken_difference_squared(a,b,edges):
    mass=F(0);grad=F(0)
    for pa,pb,l,r in zip(a,b,edges,edges[1:]):
        h=F(r)-F(l);p=[F(x)-F(y) for x,y in zip(pa,pb)]
        mass+=h*squared_integral(p)
        grad+=squared_integral([k*p[k] for k in range(1,len(p))])/h
    return {'L2_radial_squared':mass,'cellwise_radial_derivative_squared':grad,
            'sum_is_BROKEN_radial_H1_only':mass+grad}

def matmul(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def transpose(a):return list(map(list,zip(*a)))
def add(a,b):return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def sub(a,b):return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def finite_residual(L1,T,L0,Tdot):return sub(sub(matmul(L1,T),matmul(T,L0)),Tdot)
def real_metric_defect(S,Sdot,L):return add(Sdot,add(matmul(transpose(L),S),matmul(S,L)))
def frobenius_squared(a):return sum(x*x for row in a for x in row)

def encode(x):
    if isinstance(x,F):return {'rational':str(x),'display_float':float(x)}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def analyze(repaired_path,certificate_path,original_npz):
    d=json.loads(Path(repaired_path).read_text());cert=json.loads(Path(certificate_path).read_text())
    canonical=hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if canonical!=cert['reference_coefficients_sha256']:raise ValueError('repaired coefficient identity mismatch')
    if sha(original_npz)!=cert['input_pins']['BASIS.npz']['sha256']:raise ValueError('archived coefficient identity mismatch')
    import numpy as np
    with np.load(original_npz,allow_pickle=False) as ar:
        original=[[[F(float(x)) for x in p] for p in m] for m in ar['coefficients']]
        edges=[F(float(x)) for x in ar['edges']]
    if edges!=list(map(F,d['edges'])):raise ValueError('edge identity mismatch')
    repaired=[[list(map(F,p)) for p in m] for m in d['coefficients']]
    modes=[]
    for i,(old,new,ell) in enumerate(zip(original,repaired,d['l'])):
        rt=mode_traces(new,edges);ot=mode_traces(old,edges)
        if rt['origin_value'] or rt['nonzero_value_jumps']:raise ValueError('reference is not conforming')
        modes.append({'mode':i,'ell':ell,'archived_traces':ot,'repaired_traces':rt,
                      'repair_difference':broken_difference_squared(old,new,edges),
                      'strong_L2_operator_obstruction':rt['nonzero_derivative_jumps']>0,
                      'additional_origin_centrifugal_obstruction':ell>0 and rt['origin_slope']!=0})
    return {'schema':'BASS_R4T_EXACT_REGULARITY_OBSTRUCTION_V1',
            'status':'EXACT_TRACE_AND_DOMAIN_OBSTRUCTIONS_VERIFIED',
            'input_pins':{'repaired_file_sha256':sha(repaired_path),'reference_certificate_sha256':sha(certificate_path),
                          'original_npz_sha256':sha(original_npz),'repaired_canonical_coefficients_sha256':canonical},
            'units':'archived atomic units; displayed floats are not interval endpoints',
            'modes':modes,'native_operator_queries':0,'physical_time_propagations':0,
            'dynamics_comparison_bound_instantiated':False,
            'claim_scope':'Domain obstruction and finite-metric transfer theorem; not a physical trajectory certificate.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repaired',type=Path,required=True);p.add_argument('--certificate',type=Path,required=True)
    p.add_argument('--original-npz',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=encode(analyze(a.repaired,a.certificate,a.original_npz))
    with a.output.open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
if __name__=='__main__':main()
