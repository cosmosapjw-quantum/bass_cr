"""Reconstructed v3 neutral operator; old preparation bytes were not recoverable."""
from base_helpers_v3 import *
import re

def parse_mtcs(path,sp):
    lines=Path(path).read_text().splitlines()
    starts=[i for i,line in enumerate(lines) if line.strip()=='ELASTIC']
    need(len(starts)==1,'ONE_ELASTIC_MTCS_BLOCK_REQUIRED')
    i=starts[0];need(lines[i+1].strip()==sp['target'],'MTCS_TARGET_MISMATCH')
    h='\n'.join(lines[i:i+12])
    need('MTCS' in h and 'COLUMNS: Energy (eV) | Cross section (m2)' in h,'MTCS_UNITS_OR_PROCESS')
    rows=[];inside=False
    for line in lines[i+2:]:
        if re.fullmatch(r'-{5,}',line.strip()):
            if inside:break
            inside=True;continue
        if inside:
            values=line.split();need(len(values)==2,'MTCS_ROW_FORMAT');rows.append([float(v) for v in values])
    a=np.asarray(rows)
    need(a.shape==(sp['row_count'],2),'MTCS_ROW_COUNT')
    need(np.all(np.isfinite(a)) and np.all(a>0) and np.all(np.diff(a[:,0])>0),'MTCS_POSITIVE_MONOTONE')
    need(list(a[[0,-1],0])==sp['support_eV'],'MTCS_SUPPORT_IDENTITY')
    return a[:,0],a[:,1]

def validate_case(c):
    need(c.get('units',{}).get('density')=='cm^-3' and c['units'].get('E')=='eV','UNIT_CONVENTION_MISMATCH')
    need(c.get('theta_eV',0)>0 and c.get('T_K',0)>0,'BATH_TEMPERATURE')
    need([s['label'] for s in c.get('neutral_species',[])]==['H1neutral','He4neutral'],'MISSING_NEUTRAL_SPECIES')
    for s in c['species']+c['neutral_species']:
        need(s.get('n_cm3') is not None and math.isfinite(s['n_cm3']) and s['n_cm3']>=0,'MISSING_OR_INVALID_DENSITY')
        need(s.get('r',0)>0,'INVALID_MASS')
        need(s['T_K']==c['T_K'] and s['theta_eV']==c['theta_eV'],'COMMON_WEIGHT_TEMPERATURE_MISMATCH')
    need(c.get('sub_q_neutral_coefficients') is None,'SUB_Q_OUT_OF_SCOPE')
    return c

def verify(unit):
    manifest=json.loads((unit/'inputs/INPUT_MANIFEST_V3.json').read_text())
    for row in manifest['files']:
        b=(unit/row['path']).read_bytes()
        need(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'INPUT_IDENTITY:'+row['path'])
    return validate_case(json.loads((unit/'inputs/CASE_V3.json').read_text()))

def interpolate(E,table):
    x,y=table;E=np.asarray(E,dtype=float)
    need(np.all(np.isfinite(E)) and np.all((E>=x[0])&(E<=x[-1])),'OUTSIDE_MTCS_SUPPORT')
    k=np.clip(np.searchsorted(x,E,side='right')-1,0,len(x)-2)
    slope=(y[k+1]-y[k])/(x[k+1]-x[k])
    return y[k]+slope*(E-x[k]),slope

def leading(E,sigma,slope,theta,n_cm3,r,c):
    E=np.asarray(E,dtype=float)
    need(np.all(E>0),'POSITIVE_ENERGY_REQUIRED')
    need(theta>=0 and n_cm3 is not None and n_cm3>=0 and r>0,'INVALID_NEUTRAL_PARAMETERS')
    nu=n_cm3*1e6*np.sqrt(2*E*c['eV_J']/c['electron_mass_kg'])*sigma
    D=2/r*theta*E*nu;mu=2/r*nu*(theta*(2+E*slope/sigma)-E)
    return mu,D,nu

def coefficient(E,c,sp,table,q):
    E=np.asarray(E,dtype=float)
    need(np.all(np.isfinite(E)) and np.all(E>0),'POSITIVE_ENERGY_REQUIRED')
    active=E>=q;mu=np.full(E.shape,np.nan);D=np.full(E.shape,np.nan);nu=np.full(E.shape,np.nan)
    if np.any(active):
        sigma,slope=interpolate(E[active],table)
        mu[active],D[active],nu[active]=leading(E[active],sigma,slope,sp['theta_eV'],sp['n_cm3'],sp['r'],c)
    return mu,D,nu

def combined_case(old,c,tables):
    E=old['E_eV'];pi=old['pi'];mid=(E[:-1]+E[1:])/2;th=c['theta_eV'];q=E[0]
    Dee=th*c['b_anchor_eV_s']*np.sqrt(th/mid)*gammainc(1.5,mid/th)
    gens={};conds={};checks={};raw={};diagnostics=[]
    for sp in c['neutral_species']:
        mu,D,nu=coefficient(mid,c,sp,tables[sp['label']],q)
        cond=old['conductance_EE']*D/Dee
        need(np.all(cond>0),'POSITIVE_NEUTRAL_CONDUCTANCE')
        g,ch=generator(cond,pi);gens[sp['label']]=g;conds[sp['label']]=cond;checks[sp['label']]=ch
        raw['D_mid_'+sp['label']]=D;raw['mu_mid_'+sp['label']]=mu;raw['conductance_'+sp['label']]=cond
        diagnostics.append(dict(species=sp['label'],max_theta_over_rE=float(th/(sp['r']*q)),active_q_eV=float(q),mass_ratio=sp['r']))
    neutral={k:sum(g[k] for g in gens.values()) for k in ['diag','lower','upper']}
    total={k:old['Q_total_'+k]+neutral[k] for k in neutral}
    checks['total']=generator_checks(total,pi)
    d=old['K_diag']-neutral['diag'][1:];l=old['K_lower']-neutral['upper'][1:];u=old['K_upper']-neutral['lower'][1:]
    rhs=old['rhs_first6'].copy();rhs[0,2]+=neutral['upper'][0]
    x,r0=solve(d,l,u,rhs);v,r1=solve(d,l,u,x[:,:2])
    bath=np.column_stack([old['rhs_bath4']]+[-electron_drift(E,gens[s['label']])[1:] for s in c['neutral_species']])
    H,r2=solve(d,l,u,bath)
    sol=dict(u_s=x[:,0],u_p=x[:,1],u_entry=x[:,2],t=x[:,3],r_s=x[:,4],r_p=x[:,5],v_s=v[:,0],v_p=v[:,1],H=H)
    uce=x[:,0]+x[:,1];incoming=x[:,4]+x[:,5];internal=c['gap_eV']*uce
    terms=np.column_stack([H,q*x[:,2],incoming-internal,internal])
    res=abs(terms.sum(axis=1)-E[1:]);scale=abs(terms).sum(axis=1)+E[1:]
    condtot=old['conductance_total']+sum(conds.values());T=mfpt(condtot,pi);T0=old['mfpt_total']
    delta=float(np.max(sum(conds.values())/old['conductance_total']))
    metrics=dict(linear_scaled_residual=max(r0,r1,r2),linear_rhs_residuals=[r0,r1,r2],partition_max_abs=float(abs(x[:,:3].sum(axis=1)-1).max()),probability_min=float(x[:,:3].min()),probability_max=float(x[:,:3].max()),energy_ledger_scaled_residual=float((res/scale).max()),mfpt_poisson_scaled_residual=scaled_residual(-total['diag'][1:],-total['upper'][1:],-total['lower'][1:],T[1:],np.ones(len(E)-1)),delta_max=delta,mfpt_bound_upper_relative_violation=float(np.maximum(T[1:]/T0[1:]-1,0).max()),mfpt_bound_lower_relative_violation=float(np.maximum(1-(1+delta)*T[1:]/T0[1:],0).max()),old_bath4_RHS_exact_reuse=bool(np.array_equal(bath[:,:4],old['rhs_bath4'])),old_CE_RHS_exact_reuse=bool(np.array_equal(rhs[:,[0,1,3,4,5]],old['rhs_first6'][:,[0,1,3,4,5]])))
    tol=c['tolerances']
    ok=all(max(v.values())<=tol['generator'] for v in checks.values())
    ok &= metrics['linear_scaled_residual']<=tol['linear'] and metrics['partition_max_abs']<=tol['partition'] and metrics['probability_min']>=-tol['probability'] and metrics['probability_max']<=1+tol['probability'] and metrics['energy_ledger_scaled_residual']<=tol['energy'] and metrics['mfpt_poisson_scaled_residual']<=tol['mfpt'] and max(metrics['mfpt_bound_upper_relative_violation'],metrics['mfpt_bound_lower_relative_violation'])<=tol['bound'] and metrics['old_bath4_RHS_exact_reuse'] and metrics['old_CE_RHS_exact_reuse']
    raw.update(E_eV=E,pi=pi,conductance_EE=old['conductance_EE'],conductance_total=condtot,Q_total_diag=total['diag'],Q_total_lower=total['lower'],Q_total_upper=total['upper'],K_diag=d,K_lower=l,K_upper=u,rhs_first6=rhs,rhs_time2=x[:,:2],rhs_bath6=bath,mfpt_old=T0,mfpt_total=T,energy_terms=terms,**sol)
    return raw,dict(generator=checks,checks=metrics,expansion_diagnostics=diagnostics,pass_scoped=bool(ok)),bool(ok)

def source_average(old,new,src,z,c):
    E=old['E_eV'];p=old['source_'+z];mask=old['active_mask_'+z];W=src['W_eV'];m=src['pulse_count_cm3'];pop=p[1:]
    active=float(m[mask].sum());selected=float(m.sum());q=E[0]
    need(np.array_equal(mask,W>q),'SAVED_ACTIVE_MASK_MISMATCH')
    need(relative(float(p.sum()),active)<2e-12 and relative(float(p@E),float(m[mask]@W[mask]))<2e-12,'SAVED_SOURCE_IDENTITY')
    def metrics(s):
        u=s['u_s']+s['u_p'];inc=s['r_s']+s['r_p'];v=s['v_s']+s['v_p'];ce=float(pop@u)
        return dict(P_CE_active=ce/active,P_CE_selected=ce/selected,mean_stop_s_active=float(pop@s['t'])/active,mean_stop_s_selected=float(pop@s['t'])/selected,conditional_CE_energy_eV=float(pop@inc)/ce,conditional_CE_time_s=float(pop@v)/ce,entry_P_active=(float(pop@s['u_entry'])+float(p[0]))/active,no_CE_MFPT_s_active=float(p@s['mfpt_total'])/active,no_CE_MFPT_s_selected=float(p@s['mfpt_total'])/selected)
    now=metrics(new);prior=metrics(old);gains=pop@new['H'];labels=['EE']+[s['label'] for s in c['species']+c['neutral_species']]
    heat={k:float(gains[i]/selected) for i,k in enumerate(labels)}
    now['bath_heat_eV_per_selected']=heat;now['neutral_heat_eV_per_selected']=heat['H1neutral']+heat['He4neutral'];now['ion_heat_eV_per_selected']=sum(heat[s['label']] for s in c['species'])
    now['neutral_induced_relative_CE_change']=now['P_CE_active']/prior['P_CE_active']-1
    ce=float(pop@(new['u_s']+new['u_p']));incoming=float(pop@(new['r_s']+new['r_p']));internal=c['gap_eV']*ce
    ledger=dict(bath_gain_eV_cm3={k:float(gains[i]) for i,k in enumerate(labels)},entry_energy_eV_cm3=q*(float(pop@new['u_entry'])+float(p[0])),inactive_energy_eV_cm3=float(m[~mask]@W[~mask]),CE_post_kinetic_eV_cm3=incoming-internal,CE_internal_eV_cm3=internal,initial_selected_eV_cm3=float(m@W))
    values=list(ledger['bath_gain_eV_cm3'].values())+[ledger[k] for k in ['entry_energy_eV_cm3','inactive_energy_eV_cm3','CE_post_kinetic_eV_cm3','CE_internal_eV_cm3']]
    ledger['scaled_residual']=abs(sum(values)-ledger['initial_selected_eV_cm3'])/(sum(abs(v) for v in values)+abs(ledger['initial_selected_eV_cm3']))
    return dict(new=now,old=prior,ledger=ledger,selected_count_cm3=selected,original_active_count_cm3=active,source_q_count_cm3=float(p[0]),inactive_own_energy_eV_cm3=ledger['inactive_energy_eV_cm3'])

