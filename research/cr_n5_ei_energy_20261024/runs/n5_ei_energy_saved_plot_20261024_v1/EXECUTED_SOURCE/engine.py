"""Selected EI energy exchange; stored native grids and immutable EE arrays only."""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.special import gammainc
from scipy.linalg import solve_banded

class InputError(ValueError): pass
def need(ok,msg):
    if not ok: raise InputError(msg)
def writej(path,obj):
    with Path(path).open('x') as f: json.dump(obj,f,indent=2,allow_nan=False); f.write('\n')
def positive(value,label,zero=False):
    need(value is not None and isinstance(value,(int,float)) and math.isfinite(value) and (value>=0 if zero else value>0),'INVALID_'+label)
def validate_case(c):
    for k in ['theta_eV','b_anchor_eV_s','anchor_energy_eV','T_K','ne_cm3','lnLambda_ee','pulse_exposure_s','gap_eV']: positive(c.get(k),k)
    expected_units={'E':'eV','theta':'eV','mu':'eV/s','D':'eV^2/s','density':'cm^-3','time':'proper s','source_rate':'cm^-3 s^-1','pulse_heat':'eV cm^-3'}
    need(c.get('units')==expected_units,'UNIT_CONVENTION_MISMATCH')
    need(c.get('frame')=='stationary isotropic bath frame' and c.get('clock')=='proper seconds','FRAME_CLOCK_CONVENTION_MISMATCH')
    for sp in c['species']:
        for k in ['n_cm3','Z']: positive(sp.get(k),k,True)
        for k in ['r','T_K','theta_eV','lnLambda']: positive(sp.get(k),k)
        need(sp['T_K']==c['T_K'] and sp['theta_eV']==c['theta_eV'],'COMMON_WEIGHT_TEMPERATURE_MISMATCH')
    need(abs(sum(s['n_cm3']*s['Z'] for s in c['species'])-c['ne_cm3'])<=c['tolerances']['charge'],'CHARGE_SUM')
    return c
def verify(unit):
    m=json.loads((unit/'inputs/INPUT_MANIFEST.json').read_text())
    for row in m['files']:
        p=unit/row['path']; d=p.read_bytes();need(len(d)==row['bytes'] and hashlib.sha256(d).hexdigest()==row['sha256'],'INPUT_IDENTITY:'+row['path'])
    need('inputs/CASE.json' in {r['path'] for r in m['files']},'CASE_NOT_PINNED')
    return validate_case(json.loads((unit/'inputs/CASE.json').read_text()))
def coefficient(E,c,sp):
    E=np.asarray(E,dtype=float);need(np.all(np.isfinite(E)) and np.all(E>0),'POSITIVE_ENERGY_REQUIRED')
    for k in ['n_cm3','Z']:positive(sp.get(k),k,True)
    for k in ['r','theta_eV','lnLambda']:positive(sp.get(k),k)
    eta=sp['n_cm3']*sp['Z']**2/c['ne_cm3']*sp['lnLambda']/c['lnLambda_ee']
    b=c['b_anchor_eV_s']*np.sqrt(c['anchor_energy_eV']/E)*eta
    x=sp['r']*E/sp['theta_eV'];A=gammainc(1.5,x);Ap=2*np.sqrt(x)*np.exp(-x)/math.sqrt(math.pi)
    return b*(Ap-A/sp['r']),sp['theta_eV']*b*A/sp['r']
def eta(c,sp):return sp['n_cm3']*sp['Z']**2/c['ne_cm3']*sp['lnLambda']/c['lnLambda_ee']
def apply(d,l,u,x):
    if x.ndim==1:
        y=d*x;y[1:]+=l*x[:-1];y[:-1]+=u*x[1:]
    else:
        y=d[:,None]*x;y[1:]+=l[:,None]*x[:-1];y[:-1]+=u[:,None]*x[1:]
    return y
def scaled_residual(d,l,u,x,rhs):
    res=abs(apply(d,l,u,x)-rhs); den=apply(abs(d),abs(l),abs(u),abs(x))+abs(rhs)
    need(np.all(res[den==0]==0),'ZERO_SCALE_RESIDUAL')
    return float(np.divide(res,den,out=np.zeros_like(res),where=den>0).max())
def solve(d,l,u,rhs):
    need(np.all(d>0) and np.all(l<=0) and np.all(u<=0) and np.all(np.isfinite(rhs)),'INVALID_OPERATOR_OR_RHS')
    ab=np.zeros((3,len(d)));ab[0,1:]=u;ab[1]=d;ab[2,:-1]=l
    x=solve_banded((1,1),ab,rhs);need(np.all(np.isfinite(x)),'NONFINITE_SOLUTION')
    return x,scaled_residual(d,l,u,x,rhs)
def generator_checks(g,pi):
    d=g['diag'];lo=g['lower'];up=g['upper']
    need(np.all(np.isfinite(d)) and np.all(np.isfinite(lo)) and np.all(np.isfinite(up)) and np.all(lo>0) and np.all(up>0) and np.all(d<=0),'GENERATOR_DOMAIN')
    sums=d.copy();sums[:-1]+=lo;sums[1:]+=up
    scale=abs(d);scale[:-1]+=lo;scale[1:]+=up
    left=lo*pi[:-1];right=up*pi[1:]
    return dict(column_scaled_defect=float(np.max(abs(sums)/scale)),detailed_balance_edge_defect=float(np.max(abs(left-right)/(abs(left)+abs(right)))))
def generator(c,pi):
    lo=c/pi[:-1];up=c/pi[1:];d=np.zeros(len(pi));d[:-1]-=lo;d[1:]-=up
    g={'diag':d,'lower':lo,'upper':up}
    return g,generator_checks(g,pi)
def electron_drift(E,g):
    """Q.T E from edge increments, including the q edge."""
    de=np.diff(E);v=np.zeros(len(E));v[:-1]+=g['lower']*de;v[1:]-=g['upper']*de
    return v
def mfpt(c,pi):return np.r_[0.,np.cumsum(np.cumsum(pi[:0:-1])[::-1]/c)]
def relative(a,b):
    scale=max(abs(a),abs(b));return abs(a-b)/scale if scale else 0.
def atoms(unit,z):
    with (unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open(newline='') as f:r=list(csv.DictReader(f))
    out={k:np.array([float(row[k]) for row in r]) for k in r[0] if k!='channel'}
    need(len(r)==384 and np.all((out['W_eV']>0)&(out['W_eV']<10)),'SOURCE_DOMAIN')
    need(all(np.all(np.isfinite(a)) for a in out.values()),'NONFINITE_SOURCE')
    return out

def combined_case(old,c):
    E=old['E_eV'];pi=old['pi'];cee=old['conductance'];mid=(E[:-1]+E[1:])/2;th=c['theta_eV']
    conductances={'EE':cee};generators={'EE':dict(diag=old['Q_diag'],lower=old['Q_lower'],upper=old['Q_upper'])};checks={}
    for sp in c['species']:
        cb=cee*eta(c,sp)/sp['r']*gammainc(1.5,sp['r']*mid/th)/gammainc(1.5,mid/th)
        conductances[sp['label']]=cb;generators[sp['label']],checks[sp['label']]=generator(cb,pi)
    # Preserve inherited off-diagonal EE entries and sum new ion edge rates.
    lo=old['Q_lower'].copy();up=old['Q_upper'].copy()
    for sp in c['species']:lo+=generators[sp['label']]['lower'];up+=generators[sp['label']]['upper']
    diag=np.zeros(len(E));diag[:-1]-=lo;diag[1:]-=up
    total=dict(diag=diag,lower=lo,upper=up);ct=sum(conductances.values())
    checks['EE']=generator_checks(generators['EE'],pi);checks['total']=generator_checks(total,pi)
    literal=sum(g['diag'] for g in generators.values());checks['diagonal_sum_rounding_max_eV_independent_s_inv']=float(abs(diag-literal).max())
    checks['inherited_EE_edge_rate_max_relative_difference']=max(float(np.max(abs(old['Q_lower']-cee/pi[:-1])/(cee/pi[:-1]))),float(np.max(abs(old['Q_upper']-cee/pi[1:])/(cee/pi[1:]))))
    hs=old['hazard_2S_s_inv'];hp=old['hazard_2P_s_inv'];h=hs+hp
    d=h-diag[1:];l=-up[1:];u=-lo[1:];a=np.zeros(len(h));a[0]=up[0]
    rhs=np.column_stack([hs,hp,a,np.ones(len(h)),E[1:]*hs,E[1:]*hp])
    x,r0=solve(d,l,u,rhs);v,r1=solve(d,l,u,x[:,:2])
    bath_rhs=np.column_stack([-electron_drift(E,g)[1:] for g in generators.values()]);H,r2=solve(d,l,u,bath_rhs)
    sol=dict(u_s=x[:,0],u_p=x[:,1],u_entry=x[:,2],t=x[:,3],r_s=x[:,4],r_p=x[:,5],v_s=v[:,0],v_p=v[:,1],H=H)
    uce=x[:,0]+x[:,1]; incoming=x[:,4]+x[:,5];post=incoming-c['gap_eV']*uce;internal=c['gap_eV']*uce
    terms=np.column_stack([H,E[0]*x[:,2],post,internal]);res=abs(terms.sum(axis=1)-E[1:]);scale=abs(terms).sum(axis=1)+E[1:]
    Tee=mfpt(cee,pi);Ttot=mfpt(ct,pi)
    # Retain flux-form roundoff as a diagnostic; the frozen backward residual gates.
    def poisson(T,cond):
        flux=cond*np.diff(T);net=flux.copy();net[:-1]-=flux[1:]
        target=pi[1:];return float(np.max(abs(net-target)/(abs(flux)+np.r_[abs(flux[1:]),0]+target)))
    chi=E[0]/th;delta=sum(eta(c,s)/s['r'] for s in c['species'])/gammainc(1.5,chi)
    edge_ratio=ct/cee-1
    metrics=dict(linear_scaled_residual=max(r0,r1,r2),linear_rhs_residuals=[r0,r1,r2],partition_max_abs=float(abs(x[:,:3].sum(axis=1)-1).max()),probability_min=float(x[:,:3].min()),probability_max=float(x[:,:3].max()),energy_ledger_scaled_residual=float((res/scale).max()),mfpt_poisson_scaled_residual=max(scaled_residual(-old['Q_diag'][1:],-old['Q_upper'][1:],-old['Q_lower'][1:],Tee[1:],np.ones(len(E)-1)),scaled_residual(-diag[1:],-up[1:],-lo[1:],Ttot[1:],np.ones(len(E)-1))),mfpt_flux_diagnostic_scaled_residual=max(poisson(Tee,cee),poisson(Ttot,ct)),delta_max=float(delta),actual_max_edge_ratio=float(edge_ratio.max()),mfpt_bound_upper_relative_violation=float(np.maximum(Ttot[1:]/Tee[1:]-1,0).max()),mfpt_bound_lower_relative_violation=float(np.maximum(1-(1+delta)*Ttot[1:]/Tee[1:],0).max()),edge_bound_relative_violation=float(max(0,edge_ratio.max()-delta)))
    tol=c['tolerances'];ok=all(r['column_scaled_defect']<=tol['generator'] and r['detailed_balance_edge_defect']<=tol['generator'] for r in [checks[k] for k in generators]+[checks['total']])
    ok &= metrics['linear_scaled_residual']<=tol['linear'] and metrics['partition_max_abs']<=tol['partition'] and metrics['probability_min']>=-tol['probability'] and metrics['probability_max']<=1+tol['probability'] and metrics['energy_ledger_scaled_residual']<=tol['energy'] and metrics['mfpt_poisson_scaled_residual']<=tol['mfpt'] and max(metrics[k] for k in ['mfpt_bound_upper_relative_violation','mfpt_bound_lower_relative_violation','edge_bound_relative_violation'])<=tol['bound']
    raw={'E_eV':E,'pi':pi,'conductance_EE':cee,'conductance_total':ct,'Q_total_diag':diag,'Q_total_lower':lo,'Q_total_upper':up,'K_diag':d,'K_lower':l,'K_upper':u,'rhs_first6':rhs,'rhs_time2':x[:,:2],'rhs_bath4':bath_rhs,'mfpt_EE':Tee,'mfpt_total':Ttot,'energy_terms':terms,**sol}
    for label,cond in conductances.items():
        key=label.replace('+','p');raw['conductance_'+key]=cond;raw['electron_drift_'+key]=electron_drift(E,generators[label])
    return raw,dict(generator=checks,checks=metrics,pass_scoped=bool(ok)),bool(ok)

def source_average(old,new,src,z,c):
    E=old['E_eV'];p=old['source_'+z];mask=old['active_mask_'+z];W=src['W_eV'];m=src['pulse_count_cm3'];pop=p[1:];active=float(m[mask].sum());selected=float(m.sum());inactive=float(m[~mask]@W[~mask]);q=E[0]
    need(np.array_equal(mask,W>q),'SAVED_ACTIVE_MASK_MISMATCH')
    need(relative(float(p.sum()),active)<=2e-12 and relative(float(p@E),float(m[mask]@W[mask]))<=2e-12,'SAVED_SOURCE_IDENTITY')
    def metrics(sol,entry):
        u=sol['u_s']+sol['u_p'];r=sol['r_s']+sol['r_p'];v=sol['v_s']+sol['v_p'];n=float(pop@u)
        return dict(P_CE_active=n/active,P_CE_selected=n/selected,mean_stop_s_active=float(pop@sol['t'])/active,mean_stop_s_selected=float(pop@sol['t'])/selected,conditional_CE_energy_eV=float(pop@r)/n if n>0 else None,conditional_CE_time_s=float(pop@v)/n if n>0 else None,entry_P_active=(float(pop@sol[entry])+float(p[0]))/active)
    now=metrics(new,'u_entry');prior=metrics(old,'u_abs');H=pop@new['H'];heat={k:float(H[i]/selected) for i,k in enumerate(['EE']+[s['label'] for s in c['species']])}
    now['bath_heat_eV_per_selected']=heat;now['ion_heat_eV_per_selected']=sum(v for k,v in heat.items() if k!='EE')
    now['no_CE_MFPT_s_active']=float(p@new['mfpt_total'])/active;now['no_CE_MFPT_s_selected']=float(p@new['mfpt_total'])/selected
    prior['no_CE_MFPT_s_active']=float(p@new['mfpt_EE'])/active;prior['no_CE_MFPT_s_selected']=float(p@new['mfpt_EE'])/selected
    now['EI_induced_relative_CE_change']=now['P_CE_active']/prior['P_CE_active']-1
    ce_prob=float(pop@(new['u_s']+new['u_p']));ce_incoming=float(pop@(new['r_s']+new['r_p']));internal=c['gap_eV']*ce_prob
    ledger=dict(bath_gain_eV_cm3={k:float(H[i]) for i,k in enumerate(heat)},entry_energy_eV_cm3=q*(float(pop@new['u_entry'])+float(p[0])),inactive_energy_eV_cm3=inactive,CE_post_kinetic_eV_cm3=ce_incoming-internal,CE_internal_eV_cm3=internal,initial_selected_eV_cm3=float(m@W))
    vals=list(ledger['bath_gain_eV_cm3'].values())+[ledger[k] for k in ['entry_energy_eV_cm3','inactive_energy_eV_cm3','CE_post_kinetic_eV_cm3','CE_internal_eV_cm3']]
    ledger['scaled_residual']=abs(sum(vals)-ledger['initial_selected_eV_cm3'])/(sum(abs(v) for v in vals)+abs(ledger['initial_selected_eV_cm3']))
    return dict(new=now,old=prior,ledger=ledger,selected_count_cm3=selected,original_active_count_cm3=active,source_q_count_cm3=float(p[0]),inactive_own_energy_eV_cm3=inactive)
