"""R16 *diagnostic* signed midpoint-Jacobian adjoint on true 32 donor cells.

Never labels midpoint Jacobian or propagated numerical dual as certified.
The energy birth family and source closure remain inherited, and no donor root
or Picard interval proof is re-run. All source arrays are read from an exact
R15 archive extraction and its nested, pinned REI BRIDGE13 donor.
"""
from __future__ import annotations
from pathlib import Path
from decimal import Decimal as D
from fractions import Fraction as Fraction
import hashlib
import json
import sys
import time
import numpy as np
from scipy.interpolate import CubicSpline
from adjoint_linear import Cell,Link,forward_error,backward_dual

PIN_R15='0fe656016c1de11fa2d4d1e5dd0227bdd79d0b2e53ee1ad253b49290725ac5aa'
PIN_REI='a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for piece in iter(lambda:f.read(1024*1024),b''):h.update(piece)
    return h.hexdigest()

def asfloat(iv):return (float(iv.lo)+float(iv.hi))*.5

def build_cells(donor:str|Path, jacobian_s:float=.5, residual_nodes:int=17):
    if not (0 <= jacobian_s <=1) or residual_nodes<9 or residual_nodes>129:
        raise ValueError("INVALID_DIAGNOSTIC_SAMPLING")
    root=Path(donor)
    sys.path[:0]=[str(root/'source'),str(root/'research')]
    import chain_defect as ch
    assert ch.ENTRIES.keys()>={'root','point','after'}
    CT=float(299792458*float(6.6524587e-29)*1e6)
    H=float(ch.H.lo);NH=float(ch.NH0.lo);fHe=float(ch.FHE.lo)
    weights=[1.,fHe,2*fHe]
    pieces=[];links=[];diagnostics=[]
    for i in range(32):
        r=ch.ENTRIES['root'][i];pt=ch.ENTRIES['point'][i]
        if pt['variant']!=0:raise ValueError('NONCANONICAL_NATIVE_VARIANT')
        n=4+len(pt['p0']);ch.ia.DIM=n
        scales=ch.SCALE_G+[ch.P0]*len(pt['p0'])
        z0=[ch.IV(v)/sc for v,sc in zip(pt['old']+pt['p0'],scales)]
        z1=[ch.IV(v)/sc for v,sc in zip(pt['gas']+pt['p1'],scales)]
        midpoint=[a+ch.IV(str(jacobian_s))*(b-a) for a,b in zip(z0,z1)]
        t0=ch.IV(r['t0']);h=ch.IV(r['t1'])-t0
        a,_=ch.gas_photo_rhs(ch.IV(str(jacobian_s)),[ch.AD.var(v,j) for j,v in enumerate(midpoint)],t0,h,ch.EB[:n-4])
        mat=np.array([[asfloat(d) for d in v.g] for v in a],dtype=float)
        if mat.shape!=(n,n) or not np.isfinite(mat).all():raise RuntimeError('NONFINITE_MIDPOINT_JACOBIAN')
        length=float(Fraction.from_float(r['t1'])-Fraction.from_float(r['t0']))
        time0=float(r['t0']);birthn=len(pt['p0'])
        def raw_residual(s,z0=z0,z1=z1,t0=t0,h=h,birthn=birthn,n=n):
            ch.ia.DIM=n
            ss=ch.IV(str(float(s)))
            dz=[b-a for a,b in zip(z0,z1)]
            zs=[a+ss*d for a,d in zip(z0,dz)]
            fn,_=ch.gas_photo_rhs(ss,zs,t0,h,ch.EB[:birthn])
            return np.array([asfloat(d-v) for d,v in zip(dz,fn)],dtype=float)
        sample_s=np.linspace(0.,1.,residual_nodes)
        sample_r=np.array([raw_residual(s) for s in sample_s])
        residual_spline=CubicSpline(sample_s,sample_r,axis=0,bc_type='natural')
        def residual(s,residual_spline=residual_spline):return np.array(residual_spline(s),dtype=float)
        heldout_s=[.113,.267,.619,.907]
        heldout_error=[]
        for t in heldout_s:
            exact=raw_residual(t);approx=residual(t)
            heldout_error.extend(np.abs(exact-approx).tolist())
        vec=np.zeros(n);vec[:3]=weights
        def goal(s,vec=vec,time0=time0,length=length):
            return (CT*NH*length*np.exp(-3*H*(time0+length*s)))*vec
        pieces.append(Cell(A=mat,r=residual,g=goal))
        diagnostics.append({'cell':i,'n':n,'clock_s':[r['t0'],r['t1']],
                            'signed_offdiag_positive':int(((mat>0)&(~np.eye(n,dtype=bool))).sum()),
                            'signed_offdiag_negative':int(((mat<0)&(~np.eye(n,dtype=bool))).sum()),
                            'fhe':fHe,'jacobian_diag':np.diag(mat).tolist(),
                            'dt_s':length,'A_s_approx':mat.tolist(),
                            'jacobian_sampling_s':jacobian_s,
                            'point_residual_mid':raw_residual(.5).tolist(),
                            'residual_interpolation_maxabs_heldout':max(heldout_error),
                            'residual_interpolation_nodes':len(sample_s),
                            'residual_interpolation_is_diagnostic_not_certified':True})
        if i:
            last=ch.ENTRIES['point'][i-1];prev_n=4+len(last['p1'])
            if n not in (prev_n,prev_n+1):raise ValueError('UNEXPECTED_BIRTH_DIMENSION')
            B=np.zeros((n,prev_n));B[:prev_n,:prev_n]=np.eye(prev_n)
            prev=last['gas']+last['p1'];curr=pt['old']+pt['p0'][:len(last['p1'])]
            delta=np.zeros(n)
            for j,(a,b) in enumerate(zip(prev,curr)):
                x=Fraction.from_float(a)-Fraction.from_float(b)
                delta[j]=float(x/Fraction(str(scales[j].lo)))
            if n==prev_n+1:
                # Point parameter chooses true birth weight = native birth weight.
                if not r['birth_box'][0] <= pt['p0'][-1]<=r['birth_box'][1]:
                    raise ValueError('BIRTH_WEIGHT_MISMATCH')
                delta[-1]=0.
            if any(delta[:prev_n]):raise RuntimeError('EXPECTED_BIT_EXACT_NATIVE_INTERFACE')
            links.append(Link(B=B,delta=delta))
        print('point jacobian',i,'/' ,31,'N',n,flush=True)
    if len(links)!=31 or sum(1 for v in links if v.B.shape[0]>v.B.shape[1])!=6:
        raise ValueError('BIRTH_COUNT_MISMATCH')
    return pieces,links,diagnostics

def run(donor,output,jacobian_s=.5,residual_nodes=17):
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    cells,links,diags=build_cells(donor,jacobian_s,residual_nodes)
    n0=len(cells[0].A);e0=np.zeros(n0)
    print('solve forward error ...',flush=True)
    forward=forward_error(cells,links,e0,rtol=4e-11)
    print('solve backward signed adjoint ...',flush=True)
    dual=backward_dual(cells,links,e0,rtol=4e-11)
    p1=forward['goal'];p2=dual['goal']
    old_lo=1.84951686695075324e-17;old_hi=2.10105887626794078e-17
    old_ref=1.9731045074324378e-17
    result={'schema':'bass-cr.r16.midpoint-jacobian-adjoint-diagnostic.v1',
            'status':'NUMERICAL_LINEARIZED_DIAGNOSTIC_NOT_CERTIFIED_INTERVAL',
            'model':'read-only FT03 32-cell fixed-six-birth donor, HHe, prescribed FLRW',
            'method':'signed frozen A sampled per cell; diagnostic cubic-spline interpolated RHS residual; proper-density goal, DOP853 dual and independent forward solves',
            'jacobian_sampling_s':jacobian_s,'residual_interpolation_nodes_per_cell':residual_nodes,
            'forward_delta_tau':p1,'dual_delta_tau':p2,
            'absolute_primal_dual_gap':abs(p1-p2),
            'relative_gap':abs(p1-p2)/max(abs(p1),abs(p2)),
            'R15_interval':[old_lo,old_hi],
            'linearization_inside_R15':old_lo<=p1<=old_hi and old_lo<=p2<=old_hi,
            'archived_R15_nonlinear_IVP_delta':old_ref,
            'diagnostic_linearization_difference':p2-old_ref,
            'residual_terms':dual['residual_contributions'],
            'interface_terms':dual['interface_contributions'],
            'initial_term':dual['initial_contribution'],
            'signed_offdiag_counts':{'negative':sum(v['signed_offdiag_negative'] for v in diags),'positive':sum(v['signed_offdiag_positive'] for v in diags)},
            'cohort_births':6,'cells':32,'exact_native_interface_gas_and_carried_photons':True,
            'not_certified':['interval bounds on signed A','average Jacobian and nonlinear remainder','donor independent proof reissue','full continuous source quadrature','physical fit'],
            'original_R15_not_rerun':True,'elapsed_s':time.monotonic()-started}
    output.write_text(json.dumps(result,indent=2)+'\n')
    (output.parent/('JACOBIAN_'+output.stem+'.json')).write_text(json.dumps(diags,indent=2)+'\n')
    print('ADJOINT_DIAGNOSTIC',json.dumps({k:result[k] for k in ['forward_delta_tau','dual_delta_tau','relative_gap','R15_interval','linearization_inside_R15','archived_R15_nonlinear_IVP_delta','diagnostic_linearization_difference','elapsed_s']},indent=2))
    return result

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--donor',required=True);a.add_argument('--output',required=True);a.add_argument('--jacobian-s',type=float,default=.5);a.add_argument('--residual-nodes',type=int,default=17)
    v=a.parse_args();run(v.donor,v.output,v.jacobian_s,v.residual_nodes)
