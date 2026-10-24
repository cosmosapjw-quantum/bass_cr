"""New recovery-v2 source. Frozen physical providers; no old source-byte claim."""
import csv,hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from scipy.linalg import solve_banded

INPUT_ID='n5_ce_resolvent_recovery_input_20261024_v2'
RUN_ID='n5_ce_resolvent_recovery_primary_20261024_v2'
class InputError(ValueError):pass
def need(ok,msg):
    if not ok:raise InputError(msg)
def writej(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def expected_case():
    return {'schema':'N5_CE_RESOLVENT_RECOVERY_CASE_V2','physical_input_id':INPUT_ID,'primary_run_id':RUN_ID,'consumer':'N5_C23D_HI_CE_RESOLVENT_V1','observable':'channel-resolved first-CE-before-entry probability; event energy/time rewards; integrated hazard','prior_observable':'PR101 uniform-hazard/saved-MFPT estimate, descriptive comparator only','mark_multiplier':1.,'grid_N':[512,1024,2048],'chi':[1.5,3.],'R':[40,80],'primary_R':80,'source_z':['2.316','2.479','2.649'],'T_K':10000,'thermal_ne_cm3':.14,'lnLambda':20.,'n1s_cm3':.9,'n2s_cm3':None,'n2p_cm3':None,'clock':'proper seconds','frame':'bath frame; stationary heavy unpolarized H1 target','closed_box':True,'initial_support_eV':[0.,10.],'initial_endpoints':'open; initial selection only','pulse_exposure_s':10000,'theta_eV':.8617333262145178,'loss_anchor_eV_s':2.3306698113646996e-05,'gap_eV':10.20435,'missing_other_competing_hazards':None,'old_science_replay':0,'new_ODE':0,'source_quadrature':0,'thermal_rate_quadrature':0}
def validate_case(case,run_id):
    need(case==expected_case(),'FROZEN_CASE_MISMATCH');need(run_id==case['primary_run_id'],'RUN_ID_MISMATCH');return case

def verify_inputs(unit):
    m=json.loads((unit/'inputs/INPUT_MANIFEST_V2.json').read_text())
    for row in m['files']:
        data=(unit/row['path']).read_bytes();need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'INPUT_IDENTITY:'+row['path'])
    need('inputs/CASE_RECOVERY_V2.json' in {x['path'] for x in m['files']},'CASE_NOT_PINNED');return m

def providers(unit):
    ee=load_module(unit/'inputs/reused/pr59/coulomb_partition.py','_recovery_pr59')
    ce=load_module(unit/'inputs/reused/phys83/source/matched_ce.py','_recovery_phys83')
    calls={};prior=sys.getprofile();filename=str(unit/'inputs/reused/phys83/source/matched_ce.py')
    def guard(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==filename:
            name=frame.f_code.co_name;calls[name]=calls.get(name,0)+1;need(name not in ('moments','evaluate'),'FORBIDDEN_PROVIDER_RATE_EXECUTION')
    sys.setprofile(guard)
    try:channels={ch:ce.MatchedCEChannel(ch,unit/'inputs/reused/phys83/source_data') for ch in ('2S','2P')}
    finally:sys.setprofile(prior)
    return ee,ce,channels,calls

def hazard(E,channel,ce,density):
    need(density is not None and math.isfinite(density) and density>=0,'MISSING_OR_NEGATIVE_DENSITY');E=np.asarray(E)
    need(np.all(np.isfinite(E)) and np.all(E>0) and E.max()<=ce.INCIDENT_MAX_EV,'CE_DOMAIN')
    W=np.interp(E,channel.energy_eV,channel.W_eV_cm2,left=0.)
    h=density*100*math.sqrt(2*ce.EV_J/ce.ME_KG)*W/np.sqrt(E)
    need(np.all(np.isfinite(h)) and np.all(h>=0),'INVALID_HAZARD');need(np.all(h[E<=ce.GAP_EV]==0),'THRESHOLD_NONZERO');return h

def grid(theta,chi,N,gap):
    q=chi*theta;U=80*theta;return np.unique(np.r_[np.geomspace(q,U,N+1),q,10.,40*theta,U,gap])
def apply(d,l,u,x):
    if x.ndim==1:
        y=d*x;y[1:]+=l*x[:-1];y[:-1]+=u*x[1:]
    else:
        y=d[:,None]*x;y[1:]+=l[:,None]*x[:-1];y[:-1]+=u[:,None]*x[1:]
    return y

def positive_solve(d,l,u,rhs):
    need(np.all(np.isfinite(d)) and np.all(d>0) and np.all(l<=0) and np.all(u<=0),'INVALID_Z_OPERATOR')
    rhs=np.asarray(rhs,dtype=float);need(np.all(np.isfinite(rhs)) and np.all(rhs>=0),'MISSING_OR_NEGATIVE_RHS')
    ab=np.zeros((3,len(d)));ab[0,1:]=u;ab[1]=d;ab[2,:-1]=l
    x=solve_banded((1,1),ab,rhs);need(np.all(np.isfinite(x)),'NONFINITE_SOLUTION')
    residual=np.abs(apply(d,l,u,x)-rhs);den=apply(abs(d),abs(l),abs(u),abs(x))+abs(rhs)
    need(np.all(residual[den==0]==0),'ZERO_DENOMINATOR_RESIDUAL')
    ratios=np.divide(residual,den,out=np.zeros_like(residual),where=den>0)
    return x,float(ratios.max())

def matrix(E,ee,anchor):
    model=ee.MaxwellianCoulomb(anchor['theta_eV'],anchor['loss_anchor_eV_s'],anchor['theta_eV'],20.,False)
    Q,pi,c=ee.reversible_generator(E,model)
    d=Q.diagonal().copy();lo=Q.diagonal(-1).copy();up=Q.diagonal(1).copy()
    need(np.all(lo>0) and np.all(up>0) and np.all(d<=0),'GENERATOR_SIGN')
    sums=Q.sum(axis=0);den=abs(Q).sum(axis=0);need(np.all(sums[den==0]==0),'GENERATOR_ZERO_DENOMINATOR')
    ratio=np.divide(abs(sums),den,out=np.zeros_like(den),where=den>0);err=float(ratio.max());need(err<=2e-13,'GENERATOR_CONSERVATION')
    del Q
    a=np.zeros(len(E)-1);a[0]=up[0]
    return {'Q_diag':d,'Q_lower':lo,'Q_upper':up,'pi':pi,'conductance':c,'G_diag':d[1:],'G_lower':up[1:],'G_upper':lo[1:],'absorption':a,'generator_scaled_defect':err}

def solve_case(b,E,hs,hp):
    for h in (hs,hp):need(h is not None and len(h)==len(E)-1 and np.all(np.isfinite(h)) and np.all(h>=0),'MISSING_OR_NEGATIVE_HAZARD')
    h=hs+hp;d=h-b['G_diag'];l=-b['G_lower'];u=-b['G_upper']
    rhs=np.column_stack((hs,hp,b['absorption'],np.ones(len(h)),E[1:]*hs,E[1:]*hp))
    x,r1=positive_solve(d,l,u,rhs);v,r2=positive_solve(d,l,u,x[:,:2]);w,r3=positive_solve(-b['G_diag'],l,u,h)
    metrics={'linear_scaled_residual':max(r1,r2,r3),'partition_max_abs':float(abs(x[:,0]+x[:,1]+x[:,2]-1).max()),'probability_min':float(x[:,:3].min()),'probability_max':float(x[:,:3].max()),'uCE_minus_w_max':float((x[:,0]+x[:,1]-w).max())}
    ok=metrics['linear_scaled_residual']<=2e-12 and metrics['partition_max_abs']<=2e-8 and metrics['probability_min']>=-2e-10 and metrics['probability_max']<=1+2e-10 and metrics['uCE_minus_w_max']<=2e-10
    return {'K_diag':d,'K_lower':l,'K_upper':u,'rhs':rhs,'u_s':x[:,0],'u_p':x[:,1],'u_abs':x[:,2],'t':x[:,3],'r_s':x[:,4],'r_p':x[:,5],'v_s':v[:,0],'v_p':v[:,1],'w':w,'hazard_sum':h},metrics,bool(ok)

def atoms(unit,z):
    with (unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    W=np.array([float(r['W_eV']) for r in rows]);m=np.array([float(r['pulse_count_cm3']) for r in rows]);need(len(rows)==384 and np.all((W>0)&(W<10)) and np.all(np.isfinite(m)) and np.all(m>=0),'INVALID_SOURCE');return W,m

def project(E,W,m,gap):
    mask=W>E[0];w=W[mask];active=m[mask];need(len(w)>0 and np.all(w<=E[-1]),'ACTIVE_DOMAIN')
    right=np.minimum(np.searchsorted(E,w,side='right'),len(E)-1);left=right-1;t=(w-E[left])/(E[right]-E[left]);need(np.all((t>=0)&(t<=1)),'PROJECTION_SIGN')
    p=np.zeros(len(E));np.add.at(p,left,active*(1-t));np.add.at(p,right,active*t)
    den=float(active.sum());energy=float(active@w)
    info={'selected_count_cm3':float(m.sum()),'original_active_count_cm3':den,'active_fraction':den/float(m.sum()),'boundary_active_fraction':float(p[0]/den),'count_relative_error':abs(float(p.sum())-den)/den,'energy_relative_error':abs(float(p@E)-energy)/energy,'mass_above_10eV':float(p[E>10].sum()),'mass_on_CE_active_nodes':float(p[E>gap].sum())}
    need(info['mass_above_10eV']==0 and info['mass_on_CE_active_nodes']==0,'INITIAL_CE_ACTIVE_SOURCE')
    return p,mask,info

def averages(p,info,sol,E,gap):
    active=info['original_active_count_cm3'];selected=info['selected_count_cm3'];pop=p[1:];out={}
    for ch,probkey,rkey,vkey in [('2S','u_s','r_s','v_s'),('2P','u_p','r_p','v_p'),('sum',None,None,None)]:
        u=sol[probkey] if probkey else sol['u_s']+sol['u_p'];r=sol[rkey] if rkey else sol['r_s']+sol['r_p'];v=sol[vkey] if vkey else sol['v_s']+sol['v_p']
        prob=float(pop@u);energy=float(pop@r);tim=float(pop@v)
        out[ch]={'P_active':prob/active,'P_selected':prob/selected,'conditional_incoming_eV':energy/prob if prob>0 else None,'conditional_event_time_s':tim/prob if prob>0 else None,'conditional_postevent_kinetic_eV':energy/prob-gap if prob>0 else None,'internal_excitation_eV_per_selected':gap*prob/selected}
    absprob=float(pop@sol['u_abs'])+float(p[0]);out['absorption_P_active']=absprob/active;out['absorption_P_selected']=(absprob+selected-active)/selected
    for name,key in [('mean_stop_s','t'),('unmarked_integrated_hazard','w')]:out[name+'_active']=float(pop@sol[key])/active;out[name+'_selected']=float(pop@sol[key])/selected
    h=sol['hazard_sum'];incoming=E[1:]*h;post=(E[1:]-gap)*h;internal=gap*h;den=abs(incoming)+abs(post)+abs(internal);res=abs(incoming-post-internal)
    need(np.all(res[den==0]==0),'EVENT_ZERO_DENOMINATOR');out['event_energy_relative_residual']=float(np.divide(res,den,out=np.zeros_like(res),where=den>0).max());return out

def metadata(name,chi,R,N,E,b,metrics,passed,projection):
    return {'case':name,'chi':chi,'R':R,'N':N,'nodes':len(E),'generator_scaled_defect':b['generator_scaled_defect'],'checks':metrics,'pass':passed,'projection':projection}
