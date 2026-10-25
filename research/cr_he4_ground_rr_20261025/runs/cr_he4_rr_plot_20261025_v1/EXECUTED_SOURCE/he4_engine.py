"""Single HeI smooth-ground Milne channel competing on immutable H1 RR chains."""
import csv, hashlib, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
from scipy.linalg import solve_banded

class InputError(ValueError):
    pass

def need(ok,message):
    if not ok:raise InputError(message)

def writej(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def validate_config(c):
    expected={'I_He_eV':24.59,'d_He':4,'g_He_bound':1,'g_He_ion':2,
      'n_HeII_cm3':0.02,'I_eV':13.6,'n_HII_cm3':0.1,
      'electron_mass_kg':9.1093837015e-31,'eV_J':1.602176634e-19,
      'c_m_s':299792458.0,'PI_maximum_eV':50000.0,'T_K':10000.0,
      'finite_mass':False,'component':'ground_spontaneous_only',
      'operator_baseline':'EXACT_STORED_PR105_K_DIAG',
      'isotope_assignment':'CONDITIONAL_ELEMENTAL_HE_TO_HE4',
      'source_residual_state_resolution':'CONDITIONAL_SMOOTH_GROUND_CHANNEL_MODEL'}
    need(all(c.get(k)==v for k,v in expected.items()),'FROZEN_HE4_CONTRACT_MISMATCH')
    need(c['d_He']==2*c['g_He_ion']/c['g_He_bound'],'ELECTRONIC_WEIGHTS')

def verify(unit):
    c=json.loads((unit/'inputs/CONFIG.json').read_text())
    m=json.loads((unit/'inputs/INPUT_MANIFEST.json').read_text())
    for rel,key in [('FROZEN_CONTRACT.md','frozen_contract_sha256'),('inputs/CONFIG.json','config_sha256')]:
        need(hashlib.sha256((unit/rel).read_bytes()).hexdigest()==m[key],'FROZEN_IDENTITY:'+rel)
    for row in m['files']:
        b=(unit/row['path']).read_bytes()
        need(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'INPUT_IDENTITY:'+row['path'])
    validate_config(c)
    return c

def provider(unit):
    p=unit/'inputs/reused/c23b/spectral_photo_source.py'
    spec=importlib.util.spec_from_file_location('he4_exact_c23b',p)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    # Plain import and point calls only; no GL/source/thermal quadrature path.
    return mod.Verner96.from_table('HeI',p.parent/'data')

def coefficients(E,c,atom,density):
    need(not isinstance(density,bool) and isinstance(density,(int,float)) and math.isfinite(density) and density>=0,'FINITE_EXPLICIT_TARGET_DENSITY_REQUIRED')
    raw=np.asarray(E)
    need(raw.dtype.kind!='b','BOOLEAN_ENERGY_REJECTED')
    E=np.asarray(E,dtype=float)
    need(E.size>0 and E.ndim<=1 and np.all(np.isfinite(E)) and np.all(E>0),'POSITIVE_FINITE_KINETIC_ENERGY_REQUIRED')
    need(c['I_He_eV']==24.59 and c['d_He']==4 and atom.channel=='HeI' and atom.threshold_eV==24.59 and atom.maximum_eV==50000.0,'NATIVE_HEI_GROUND_SOURCE_IDENTITY')
    photon=E+c['I_He_eV']
    need(np.all(photon>=atom.threshold_eV) and np.all(photon<=atom.maximum_eV),'FINITE_PI_SUPPORT_REQUIRED')
    pi=np.array([atom.sigma_cm2(float(v)) for v in np.atleast_1d(photon)])
    mec2=c['electron_mass_kg']*c['c_m_s']**2/c['eV_J']
    sigma=pi*np.atleast_1d(photon)**2/(c['d_He']*mec2*np.atleast_1d(E))
    speed=100*np.sqrt(2*np.atleast_1d(E)*c['eV_J']/c['electron_mass_kg'])
    lam=density*speed*sigma
    need(np.all(np.isfinite(lam)) and np.all(np.isfinite(sigma)) and np.all(sigma>0),'NONFINITE_OR_INVALID_HE_RR')
    return dict(sigma_PI_He_cm2=pi,sigma_RR_He_cm2=sigma,v_cm_s=speed,lambda_He=lam)

def apply(d,l,u,x):
    y=d[:,None]*x if x.ndim==2 else d*x
    if x.ndim==2:y[1:]+=l[:,None]*x[:-1];y[:-1]+=u[:,None]*x[1:]
    else:y[1:]+=l*x[:-1];y[:-1]+=u*x[1:]
    return y

def solve(d,l,u,b):
    need(np.all(np.isfinite(d)) and np.all(d>0) and np.all(np.isfinite(l)) and np.all(l<=0) and np.all(np.isfinite(u)) and np.all(u<=0) and np.all(np.isfinite(b)),'VALID_KILLED_OPERATOR_REQUIRED')
    ab=np.zeros((3,len(d)));ab[0,1:]=u;ab[1]=d;ab[2,:-1]=l
    x=solve_banded((1,1),ab,b)
    need(np.all(np.isfinite(x)),'NONFINITE_SOLUTION')
    residual=abs(apply(d,l,u,x)-b);den=apply(abs(d),abs(l),abs(u),abs(x))+abs(b)
    need(np.all(residual[den==0]==0),'ZERO_RESIDUAL_SCALE')
    scaled=np.divide(residual,den,out=np.zeros_like(residual),where=den>0)
    return x,np.atleast_1d(scaled.max(axis=0)).tolist()

def atoms(unit,z):
    rows=list(csv.DictReader((unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open()))
    need(len(rows)==384,'EXACT_SAVED_384_ATOMS_REQUIRED')
    a={k:np.array([float(row[k]) for row in rows]) for k in rows[0] if k!='channel'}
    need(np.all((a['W_eV']>0)&(a['W_eV']<10)) and np.all(a['pulse_count_cm3']>0),'SAVED_SOURCE_DOMAIN')
    return a

def consume(base,h1,c,atom,count):
    for key in ['E_eV','K_lower','K_upper']:
        need(np.array_equal(base[key],h1[key]),'PARENT_IDENTITY:'+key)
    need(np.array_equal(base['K_diag'],h1['K0_diag']),'PR104_DIAGONAL_IDENTITY')
    need(np.array_equal(h1['lambda_RR'],h1['lambda_RR_s_inverse']),'H1_RATE_IDENTITY')
    E=base['E_eV'][1:];d0=h1['K_diag'];l=h1['K_lower'];u=h1['K_upper']
    coef=coefficients(E,c,atom,c['n_HeII_cm3']);lam=coef['lambda_He'];h=h1['lambda_RR']
    d=d0+lam
    rhs16=np.column_stack([base['rhs_first6'],h,h*E,lam,lam*E,base['rhs_bath6']])
    count(16);x,res=solve(d,l,u,rhs16)
    time_rhs=x[:,[0,1,6,8]];count(4);v,rv=solve(d,l,u,time_rhs)
    response_rhs=-lam[:,None]*np.column_stack([h1['u_s']+h1['u_p'],h1['t'],h1['p_RR']])
    count(3);response,rr=solve(d,l,u,response_rhs)
    count(1);w,rw=solve(d0,l,u,lam)
    eta=float(w.max());phe=x[:,8];lower=w/(1+eta)
    need(np.all(w>0) and np.all(phe>0),'STRICT_HE_RR_POSITIVITY')
    upper_v=float(np.maximum((phe-w)/w,0).max());lower_v=float(np.maximum((lower-phe)/lower,0).max())
    hph=x[:,7]+c['I_eV']*x[:,6];hi=-c['I_eV']*x[:,6]
    heph=x[:,9]+c['I_He_eV']*phe;hei=-c['I_He_eV']*phe
    partition=x[:,:3].sum(axis=1)+x[:,6]+phe;ce=x[:,0]+x[:,1];ce_in=x[:,4]+x[:,5]
    terms=np.column_stack([x[:,10:16],base['E_eV'][0]*x[:,2],ce_in-c['gap_eV']*ce,c['gap_eV']*ce,hph,hi,heph,hei])
    er=abs(terms.sum(axis=1)-E)/(abs(terms).sum(axis=1)+E)
    addition_loss=(d.astype(np.longdouble)-d0.astype(np.longdouble))-lam.astype(np.longdouble)
    ownscale=np.maximum(abs(heph)+abs(hei)+abs(x[:,9]),np.finfo(float).tiny)
    own_res=float((abs(heph+hei-x[:,9])/ownscale).max())
    metrics=dict(rhs_scaled_backward_residuals=res+rv+rr+rw,partition_maxabs=float(abs(partition-1).max()),energy_scaled_residual=float(er.max()),He_RR_own_energy_residual=own_res,probability_min=float(x[:,[0,1,2,6,8]].min()),probability_max=float(x[:,[0,1,2,6,8]].max()),eta=eta,rare_upper_relative_violation=upper_v,rare_lower_relative_violation=lower_v,delta_CE_max=float(response[:,0].max()),delta_time_max=float(response[:,1].max()),delta_H1_RR_max=float(response[:,2].max()),diagonal_addition_lost_rate_max_abs=float(abs(addition_loss).max()),diagonal_addition_loss_relative_to_He_rate_max=float((abs(addition_loss)/lam).max()),baseline='EXACT_STORED_PR105_K_DIAG',old_offdiagonal_exact_reuse=True,old_generator_replay=0,old_source_projection_replay=0)
    t=c['tolerances']
    passed=max(metrics['rhs_scaled_backward_residuals'])<=t['linear'] and metrics['partition_maxabs']<=t['partition'] and metrics['energy_scaled_residual']<=t['energy'] and own_res<=t['event_energy'] and metrics['probability_min']>=-t['probability'] and metrics['probability_max']<=1+t['probability'] and max(upper_v,lower_v)<=t['rare_bound'] and np.all(response<=0)
    new=dict(E_eV=base['E_eV'],K_H1_diag=d0,K_diag=d,K_lower=l,K_upper=u,lambda_H1=h,rhs_physical16=rhs16,rhs_conditional4=time_rhs,rhs_response3=response_rhs,rhs_w=lam,solution_physical16=x,solution_conditional4=v,solution_response3=response,w=w,p_H1=x[:,6],r_H1=x[:,7],v_H1=v[:,2],p_He=phe,r_He=x[:,9],v_He=v[:,3],u_s=x[:,0],u_p=x[:,1],u_entry=x[:,2],t=x[:,3],r_s=x[:,4],r_p=x[:,5],H=x[:,10:16],photon_H1=hph,internal_H1=hi,photon_He=heph,internal_He=hei,delta_CE=response[:,0],delta_time=response[:,1],delta_H1_RR=response[:,2],energy_terms=terms,**coef)
    return new,metrics,bool(passed)

def source_average(base,h1,new,src,z,c):
    p=base['source_'+z];mask=base['active_mask_'+z];W=src['W_eV'];m=src['pulse_count_cm3'];E=base['E_eV'];pop=p[1:]
    need(np.array_equal(mask,W>E[0]),'SOURCE_ACTIVE_MASK_IDENTITY')
    active=float(m[mask].sum());selected=float(m.sum())
    need(abs(float(p.sum())-active)/active<2e-12 and abs(float(p@E)-float(m[mask]@W[mask]))/float(m[mask]@W[mask])<2e-12,'SAVED_PROJECTION_IDENTITY')
    ph=float(pop@new['p_H1']);rh=float(pop@new['r_H1']);vh=float(pop@new['v_H1'])
    pe=float(pop@new['p_He']);re=float(pop@new['r_He']);ve=float(pop@new['v_He'])
    ce=float(pop@(new['u_s']+new['u_p']));inc=float(pop@(new['r_s']+new['r_p']));gains=pop@new['H']
    stop=float(pop@new['t']);dce=float(pop@new['delta_CE']);dt=float(pop@new['delta_time']);dh=float(pop@new['delta_H1_RR'])
    oldce=float(pop@(h1['u_s']+h1['u_p']));oldt=float(pop@h1['t']);oldh=float(pop@h1['p_RR']);sw=float(pop@new['w']);eta=float(new['w'].max())
    ledger=dict(bath_gain_eV_cm3={k:float(gains[i]) for i,k in enumerate(c['bath_labels'])},entry_energy_eV_cm3=float(E[0]*(float(pop@new['u_entry'])+p[0])),inactive_own_energy_eV_cm3=float(m[~mask]@W[~mask]),CE_outgoing_kinetic_eV_cm3=inc-c['gap_eV']*ce,CE_internal_eV_cm3=c['gap_eV']*ce,H1_RR_photon_retained_eV_cm3=rh+c['I_eV']*ph,H1_RR_atomic_internal_eV_cm3=-c['I_eV']*ph,He_RR_photon_retained_eV_cm3=re+c['I_He_eV']*pe,He_RR_atomic_internal_eV_cm3=-c['I_He_eV']*pe,initial_kinetic_eV_cm3=float(m@W))
    final_keys=['entry_energy_eV_cm3','inactive_own_energy_eV_cm3','CE_outgoing_kinetic_eV_cm3','CE_internal_eV_cm3','H1_RR_photon_retained_eV_cm3','H1_RR_atomic_internal_eV_cm3','He_RR_photon_retained_eV_cm3','He_RR_atomic_internal_eV_cm3']
    values=list(ledger['bath_gain_eV_cm3'].values())+[ledger[k] for k in final_keys]
    ledger['scaled_residual']=abs(math.fsum(values)-ledger['initial_kinetic_eV_cm3'])/(math.fsum(abs(v) for v in values)+ledger['initial_kinetic_eV_cm3'])
    return dict(P_He_RR_active=pe/active,P_He_RR_selected=pe/selected,conditional_He_RR_kinetic_eV=re/pe if pe>0 else None,conditional_He_RR_photon_eV=re/pe+c['I_He_eV'] if pe>0 else None,conditional_He_RR_time_s=ve/pe if pe>0 else None,He_RR_photon_eV_per_selected=(re+c['I_He_eV']*pe)/selected,He_RR_internal_eV_per_selected=-c['I_He_eV']*pe/selected,P_H1_RR_active=ph/active,conditional_H1_RR_photon_eV=rh/ph+c['I_eV'] if ph>0 else None,conditional_H1_RR_time_s=vh/ph if ph>0 else None,P_CE_active=ce/active,mean_stop_s_active=stop/active,delta_CE_active=dce/active,delta_time_s_active=dt/active,delta_H1_RR_active=dh/active,old_P_H1_RR_active=oldh/active,old_P_CE_active=oldce/active,old_mean_stop_s_active=oldt/active,subtraction_diagnostic_delta_H1=(ph-oldh)/active,source_bound_lower=sw/(1+eta)/active,source_bound_upper=sw/active,selected_count_cm3=selected,active_count_cm3=active,source_q_count_cm3=float(p[0]),expected_He_events_cm3=pe,expected_H1_events_cm3=ph,expected_population_delta_cm3={'fast_electron':-pe-ph,'HeII':-pe,'HeI':pe,'HII':-ph,'HI':ph,'photon':pe+ph},diagnostic_electron_removed_energy_eV_cm3=re+rh,ledger=ledger)
