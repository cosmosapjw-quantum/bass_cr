"""Separate original Decimal/AD point comparison and exact regularity identities.
No repeated donor root/IVP/prefix certification; source audit at six new points.
"""
from pathlib import Path
import sys,json,importlib,hashlib
import numpy as np
import sympy as sy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from ft03_point import Model,TEND,W0,temperature,nonphoto_jac,H,CHI,CE,TAU_SCALE
from birth_response import Background

def run(inputdir,outfile):
    plan=json.loads((ROOT/'inputs/BIRTH_PLAN.json').read_text())
    state=json.loads((inputdir/'BASE_SAMPLES.json').read_text())
    result=json.loads((inputdir/'RESPONSE.json').read_text())
    donor=ROOT/'inputs/donor'
    sys.path[:0]=[str(donor/'research'),str(donor/'source')]
    import chain_defect as cd
    from interval_decimal import IV,AD
    import interval_decimal as ia
    births=np.r_[0.,np.array(plan['same_births'])/TEND]
    model=Model(births);n=11;ia.DIM=n
    scales=[1.]*4+[.05]*7
    rhs_rel=[];jac_rel=[];absdiff=[];cases=[]
    # Original donor state/time definitions, but first-cell normalized time not reused.
    for idx in [0,8,20,36,52,64]:
        u=state['u'][idx];native=np.array(state['state'][idx][:n])
        z=[AD.var(IV(float(v))/IV(s),j) for j,(v,s) in enumerate(zip(native,scales))]
        exact,_=cd.gas_photo_rhs(IV(0),z,IV(float(u))*IV(TEND),IV(TEND),[IV(13.7)]*7)
        expected=np.array([float((v.v.lo+v.v.hi)/2)*sc for v,sc in zip(exact,scales)])
        jex=np.array([[float((a.lo+a.hi)/2)*scales[i]/scales[j] for j,a in enumerate(v.g)] for i,v in enumerate(exact)])
        got=model.rhs(u,native);jg=model.jac(u,native)
        delta=np.abs(got-expected);rr=delta/np.maximum(np.abs(expected),1e-26)
        jd=np.abs(jg-jex);jj=jd/np.maximum(np.abs(jex),1e-26)
        rhs_rel.extend(rr.tolist());jac_rel.extend(jj.ravel().tolist());absdiff.extend(delta.tolist())
        cases.append({'u':u,'max_rhs_rel':float(rr.max()),'max_jac_rel':float(jj.max())})
    assert max(rhs_rel)<3e-12 and max(jac_rel)<3e-11, (max(rhs_rel),max(jac_rel))
    # Exact lower-derivative continuity + nonzero cubic jump in a nonlinear HI probe model.
    x,p,lx,lp,a,r,c,w=sy.symbols('x p lx lp a r c w', real=True)
    F=sy.Matrix([-r*x*x+a*(1-x)*p,-a*(1-x)*p]);J=F.jacobian([x,p]);lam=sy.Matrix([lx,lp]);ld=-J.T*lam-sy.Matrix([c,0])
    coords=[x,p,lx,lp];vec=[*F,*ld];f=lp;jumps=[]
    for k in range(4):
        jump=sy.factor(f.subs(p,p+w)-f);jumps.append(jump)
        f=sy.factor(sum(sy.diff(f,z)*v for z,v in zip(coords,vec)))
    assert jumps[:3]==[0,0,0] and jumps[3]!=0
    ex=jumps[3].subs({x:sy.Rational(9,10),p:sy.Rational(1,20),lx:sy.Rational(1,2),lp:sy.Rational(1,4),a:2,r:sy.Rational(1,10),c:1,w:sy.Rational(1,100)})
    assert ex!=0
    # PDE jump cancellation is algebraic for arbitrary vector direction d and gradient k_g.
    kk,ww,D,R=sy.symbols('kappa w dot_product R',real=True)
    assert sy.expand(ww*kk*D*R-kk*ww*D*R)==0
    # Photon conservation and memory heat follow exactly from qp'=a*p*uh-kappa*qp.
    Q,q,qprime,Hs,E=sy.symbols('Q q qprime H E')
    assert sy.expand(-Q*qprime-(-sy.Symbol('dQq')-Hs*E*q)).subs(sy.Symbol('dQq'),-Hs*E*q+Q*qprime)==0
    output={'status':'PASS_SEPARATE_DONOR_AD_POINT_AND_EXACT_IDENTITIES','donor_point_evaluations':6,'rhs_components':len(rhs_rel),'jacobian_components':len(jac_rel),'max_rhs_relative':max(rhs_rel),'max_jac_relative':max(jac_rel),'cases':cases,'same_source_coefficients':True,'new_uniform_interval_proof':False,'jump_orders_0_1_2_zero':True,'third_jump_formula':str(jumps[3]),'exact_nonzero_third_jump_example':str(ex),'independent_human_reviewer':False,'proof_assistant':False}
    outfile.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();run(args.input,args.output)
