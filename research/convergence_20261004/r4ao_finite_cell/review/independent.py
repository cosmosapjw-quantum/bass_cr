"""Read-only R4AO review. Does not import producer/interval/native modules.
The Cartesian integral is a high-precision diagnostic, NOT a new enclosure.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,math,time
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'evidence/PILOT_v1'
checks=[]
def check(name,value):
    checks.append({'condition':name,'pass':bool(value)})
    if not value:raise AssertionError(name)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pair(d):return F(int(d['lower_numerator']),1<<int(d['denominator_power2'])),F(int(d['upper_numerator']),1<<int(d['denominator_power2']))
def main():
    start=time.monotonic();c=json.loads((ROOT/'contracts/PILOT_v1.json').read_text());r=json.loads((RUN/'RESULT.json').read_text());a=json.loads((RUN/'ANALYTIC_REMAINDER.json').read_text())
    check('contract identity',sha(ROOT/'contracts/PILOT_v1.json')==r['contract_sha256'])
    for name,h in c['source_input_pins'].items():check('input '+name,sha(ROOT/name)==h)
    for k in ('S_TP','H_TP','D_TP','K_TP'):
        mu=pair(a['complex_sup_u'][k])[1];mw=pair(a['complex_sup_w'][k])[1];err=pair(a['modulus_error'][k])[1]
        constant=F(64,15)/((F(2)-1)*F(2)**63)
        check('Gaussian tensor '+k,err>=F(1,2)*constant*(mu+mw))
        q=r['values'][k];rad=F(0)
        for part in ('real','imag'):
            num=pair(q['numeric'][part]);lo,hi=pair(q['enclosure'][part]);rad+=(hi-lo)/2
            check('expanded '+k+part,lo<=num[0]-err and hi>=num[1]+err)
        check('radius '+k,rad==F(q['radius_L1_upper']))
        check('target '+k,rad<=F(1,10**16))
    lines=(RUN/'STDOUT.txt').read_text().splitlines()
    check('native count',lines[0]=='R4AN_NUMERIC_V1 256 1024')
    for line in lines[1:]:
        k,rl,rh,il,ih=line.split();val=r['values'][k]['numeric']
        check('native endpoint '+k,[int(rl),int(rh),int(il),int(ih)]==[int(val['real']['lower_numerator']),int(val['real']['upper_numerator']),int(val['imag']['lower_numerator']),int(val['imag']['upper_numerator'])])
    check('one attempt',r['actual_candidate_native_calls']==1 and r['new_cell_count']==1 and r['new_channel_pair_count']==1)
    check('no expansion',r['full_K_calls']==0 and r['historical_replays']==0 and r['root_finder_calls']==0)
    for k in ('K_window_derivative_bound','physical_bridge_upper','precise_full_matrix_K_cubature_error'):check('unclaimed '+k,r[k] is None)
    check('native unchanged from R4AN',sha(ROOT/'native/weak_cell.cpp')=='8f871fccbbdb21168b732af948f43c248ced6b0e80843bd88722abb40e3285b0')
    check('pole u',pair(a['remote_denominator_u']['real'])[0]>0)
    check('pole w',pair(a['remote_denominator_w']['real'])[0]>0)
    with np.load(ROOT/'inputs/CANDIDATE.npz',allow_pickle=False) as data:
        edges=data['edges'].copy();end=data['shared_endpoint_values'].copy();bubble=data['bubble_coefficients'].copy()
    slope=(F(float(end[3,1]))-F(float(end[3,0]))+F(float(bubble[3,0,0])))/F(float(edges[1]))
    check('nonzero retained p slope',slope!=0)
    # Non-holomorphic Cartesian formulas are used ONLY on the real domain for
    # diagnostic values. No producer chart-polynomial or angular moment code.
    mp.mp.dps=70
    def cv(f):
        q=F(f);return mp.mpf(q.numerator)/q.denominator
    b,z,v,t=[cv(c['binding']['context'][k]) for k in ('b','z','v','t')]
    R=mp.sqrt(b*b+z*z);rad=cv(F(float(edges[1])));e=(b/R,mp.mpf(0),z/R);e1=(-z/R,mp.mpf(0),b/R);e2=(mp.mpf(0),mp.mpf(-1),mp.mpf(0));nu=v*v/2
    coeffs={}
    for mode,panel in ((4,28),(3,0)):
        lo,hi=[cv(F(float(x))) for x in edges[panel:panel+2]]
        L,U=[cv(F(float(x))) for x in end[mode,panel:panel+2]]
        qs=[cv(F(float(x))) for x in bubble[mode,panel]]
        coeffs[(mode,panel)]=(lo,hi-lo,L,U,qs)
    def field(mode,panel,m,r,x,cj=False):
        lo,dr,L,U,qs=coeffs[(mode,panel)];s=(r-lo)/dr
        qq=qs[0]+s*(qs[1]+s*qs[2]);qp=qs[1]+2*s*qs[2]
        u=(1-s)*L+s*U+s*(1-s)*qq
        du=(U-L+(1-2*s)*qq+s*(1-s)*qp)/dr
        cvec=(mp.sqrt(mp.mpf(3)/2) if m==-1 else -mp.sqrt(mp.mpf(3)/2),-1j*mp.sqrt(mp.mpf(3)/2),mp.mpf(0))
        if cj:cvec=tuple(mp.conj(a) for a in cvec)
        nh=tuple(a/r for a in x);cn=sum(cvec[i]*nh[i] for i in range(3))
        f=u/r*cn
        grad=tuple((du/r-u/r**2)*cn*nh[i]+u/r**2*(cvec[i]-cn*nh[i]) for i in range(3))
        return f,grad
    degree=20;angles=32
    gx,gw=mp.gauss_quadrature(degree,'legendre');out=[mp.mpc(0) for _ in range(4)]
    cos_sin=[(mp.cos(2*mp.pi*j/angles),mp.sin(2*mp.pi*j/angles)) for j in range(angles)]
    for i in range(degree):
        rr=rad*(gx[i]+1)/2
        for j in range(degree):
            eta=gx[j];other=R+rr*eta;aa=eta-rr*(1-eta*eta)/(2*R);trans=mp.sqrt(1-aa*aa)
            accum=[mp.mpc(0) for _ in range(4)]
            for cs,sn in cos_sin:
                nh=tuple(aa*e[k]+trans*(cs*e1[k]+sn*e2[k]) for k in range(3))
                xp=tuple(rr*a for a in nh);xt=tuple(R*e[k]+xp[k] for k in range(3))
                ft,gt=field(4,28,1,other,xt,True);fp,gp=field(3,0,-1,rr,xp)
                ph=mp.exp(1j*(v*xt[2]-nu*t));prod=ft*fp
                hh=sum(gt[k]*gp[k] for k in range(3))/2+1j*v*gt[2]*fp/2-prod*(1/rr+1/other)
                dd=ft*(-v*gp[2]-1j*nu*fp)
                vals=(prod,hh,dd,hh-1j*dd)
                for k in range(4):accum[k]+=vals[k]*ph
            weight=gw[i]*gw[j]/4*rad*other/R*rr**2
            for k in range(4):out[k]+=accum[k]/angles*weight
    diag={}
    for key,val in zip(('S_TP','H_TP','D_TP','K_TP'),out):
        q=r['values'][key];mid=mp.mpc(cv(q['midpoint_real']),cv(q['midpoint_imag']))
        lo,hi=pair(q['enclosure']['real']);il,ih=pair(q['enclosure']['imag'])
        contained=cv(lo)<=val.real<=cv(hi) and cv(il)<=val.imag<=cv(ih)
        check('Cartesian diagnostic inside '+key,contained)
        diag[key]={'real':mp.nstr(val.real,65),'imag':mp.nstr(val.imag,65),'abs_midpoint_difference':mp.nstr(abs(val-mid),12),'inside_certified_rectangle':contained}
    review={'status':'READ_ONLY_EXACT_ARITHMETIC_AND_CARTESIAN_DIAGNOSTIC_PASS','checks':checks,'condition_count':len(checks),'independent_agent_or_human':False,'producer_imported':False,'native_reexecuted':False,'p_origin_slope_exact':str(slope),'reference_diagnostic':{'precision_digits':70,'radial_Gauss_degree':20,'eta_Gauss_degree':20,'azimuth_trapezoid_nodes':32,'Cartesian_point_evaluations':20*20*32,'is_enclosure':False,'replaces_analytic_bound':False,'values':diag},'wall_seconds':time.monotonic()-start}
    target=ROOT/'evidence/INDEPENDENT_REVIEW.json'
    with target.open('x') as f:json.dump(review,f,indent=2);f.write('\n')
    print(json.dumps({k:review[k] for k in ('status','condition_count','wall_seconds')},indent=2));print(json.dumps(diag,indent=2))
if __name__=='__main__':main()
