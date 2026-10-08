"""Read-only archived coefficient audit; no native/operator evaluator is called.

Piecewise polynomial products are exact rational expressions in the stored
binary64 coefficients. The only nonrational integrals use Decimal ln at 80
and 100 digits. This is a high-precision consistency audit, not directed
interval arithmetic or an exact eigenfunction assertion.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import comb
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from analytic_majorant import cancellation_rate


def dec(x):return Decimal(x.numerator)/Decimal(x.denominator)
def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c

def global_poly(local,a,h):
    out=[F(0)]*len(local)
    for k,c in enumerate(local):
        for j in range(k+1):out[j]+=F(float(c))*comb(k,j)*(-a)**(k-j)/h**k
    return out

def integrate(p,a,b,shift=0):
    result=Decimal(0)
    for k,c in enumerate(p):
        if not c:continue
        power=k+shift
        if power==-1:
            if a==0:raise ValueError('nonzero logarithmically singular origin term')
            result+=dec(c)*(dec(b)/dec(a)).ln()
        else:
            e=power+1
            if a==0 and e<0:raise ValueError('nonzero singular origin term')
            result+=dec(c*(b**e-a**e)/e)
    return result

def evaluate(coefficients,edges,ell,precision):
    with localcontext() as ctx:
        ctx.prec=precision
        ns=len(ell); S=[[Decimal(0) for _ in ell] for _ in ell];H=[[Decimal(0) for _ in ell] for _ in ell]
        for cell in range(len(edges)-1):
            a,b=map(lambda x:F(float(x)),edges[cell:cell+2]);h=b-a
            poly=[global_poly(coefficients[m,cell],a,h) for m in range(ns)]
            deriv=[[k*p[k] for k in range(1,len(p))] for p in poly]
            for i in range(ns):
                for j in range(i,ns):
                    if ell[i]!=ell[j]:continue
                    prod=mul(poly[i],poly[j]);kin=mul(deriv[i],deriv[j])
                    sij=integrate(prod,a,b)
                    hij=integrate(kin,a,b)/2-integrate(prod,a,b,-1)
                    if ell[i]:hij+=Decimal(ell[i]*(ell[i]+1))/2*integrate(prod,a,b,-2)
                    S[i][j]+=sij;H[i][j]+=hij
        for i in range(ns):
            for j in range(i):S[i][j]=S[j][i];H[i][j]=H[j][i]
        return S,H

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    meta=json.loads((args.inputs/'BASIS.json').read_text()); ar=np.load(args.inputs/'BASIS.npz',allow_pickle=False)
    modes=meta['modes'];ell=[m['l'] for m in modes]
    records=[];values=[]
    for precision in (80,100):
        S,H=evaluate(ar['coefficients'],ar['edges'],ell,precision);values.append((S,H))
        fS=np.array(S,float); fH=np.array(H,float)
        J=np.eye(5)[:,[0,1,3]]
        result=cancellation_rate(fS,fH,np.zeros((5,5)),J)
        with localcontext() as ctx:
            ctx.prec=precision
            det=S[0][0]*S[1][1]-S[0][1]*S[1][0]
            inv=((S[1][1]/det,-S[0][1]/det),(-S[1][0]/det,S[0][0]/det))
            schur=[]
            for j in (0,1):
                schur.append(H[2][j]-sum(S[2][k]*inv[k][l]*H[l][j] for k in (0,1) for l in (0,1)))
            schur.append(H[4][3]-S[4][3]*H[3][3]/S[3][3])
        records.append({'decimal_digits':precision,'isolated_invariance_schur_residual_decimal':[str(x) for x in schur],'isolated_selected_coupling_per_atomic_time_float64_svd':result['rho_offdiagonal'],
          'radial_mass_decimal':[[str(x) for x in row] for row in S],
          'radial_isolated_hamiltonian_decimal':[[str(x) for x in row] for row in H],
          'selected_mode_indices':[0,1,3], 'positive_mode_indices':[2,4]})
    with localcontext() as ctx:
        ctx.prec=110
        difference=max(abs(values[0][k][i][j]-values[1][k][i][j]) for k in range(2) for i in range(5) for j in range(5))
    # The radial 5x5 direct sum reproduces the spectral norm of the 9-channel
    # same-center coupling: l=1 block is repeated for m=-1,0,1.
    endpoint_defects=[]
    for m in range(5):
        jumps=[]
        for cell in range(39):
            jumps.append(sum(F(float(x)) for x in ar['coefficients'][m,cell])-F(float(ar['coefficients'][m,cell+1,0])))
        end=sum(F(float(x)) for x in ar['coefficients'][m,-1])
        endpoint_defects.append({'mode':m,'max_internal_piecewise_value_jump_float':float(max(map(abs,jumps))),
          'outer_boundary_trace_float':float(end), 'outer_boundary_trace_exact_binary_rational':str(end)})
    out={'schema':'BASS_G04_ARCHIVED_RADIAL_ALGEBRA_AUDIT_V1','status':'NUMERICALLY_CHECKED_NOT_INTERVAL_CERTIFIED',
      'method':'exact rational polynomial products; Decimal logarithms for r^-1 integrals; float64 final SVD',
      'basis_identity':meta['identity'],'support_radius_a0':float(ar['edges'][-1]),
      'input_pins':{n:{'sha256':hashlib.sha256((args.inputs/n).read_bytes()).hexdigest(),'bytes':(args.inputs/n).stat().st_size} for n in ('BASIS.json','BASIS.npz')},
      'precision_records':records,'max_absolute_matrix_difference_between_precisions':str(difference),
      'piecewise_endpoint_audit':endpoint_defects,
      'new_native_calls':0,'new_physical_operator_queries':0,
      'interpretation':'Nonzero isolated coupling is observed in the stored-binary polynomial interpretation; tiny continuity/boundary defects also prevent silently treating float polynomials as exact conforming FEM eigenfunctions. This does not invalidate finite-window evidence or quantify its error. No integrable infinite-tail certificate is issued.'}
    args.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'couplings':[x['isolated_selected_coupling_per_atomic_time_float64_svd'] for x in records],'precision_difference':str(difference),'endpoint_defects':endpoint_defects},indent=2))
if __name__=='__main__':main()
