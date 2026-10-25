"""Frozen H1 ground spontaneous Milne consumer of immutable saved PR104 chains."""
import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.linalg import solve_banded

class InputError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise InputError(message)

def writej(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')

def verify(unit):
    c = json.loads((unit/'inputs/CONFIG.json').read_text())
    m = json.loads((unit/'inputs/INPUT_MANIFEST.json').read_text())
    need(hashlib.sha256((unit/'FROZEN_CONTRACT.md').read_bytes()).hexdigest() == m['frozen_contract_sha256'], 'FROZEN_CONTRACT_CHANGED')
    for row in m['files']:
        b = (unit/row['path']).read_bytes()
        need(len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], 'INPUT_IDENTITY:'+row['path'])
    expected = {'I_eV':13.6,'g_H':2,'g_p':1,'d':1,'electron_mass_kg':9.1093837015e-31,'eV_J':1.602176634e-19,'c_m_s':299792458.0,'n_HII_cm3':0.1}
    need(all(c.get(k) == v for k,v in expected.items()), 'FROZEN_CONSTANT_MISMATCH')
    need(c.get('component') == 'ground_spontaneous_only', 'UNSUPPORTED_COMPONENT')
    return c

def provider(unit):
    path = unit/'inputs/reused/c23b/spectral_photo_source.py'
    spec = importlib.util.spec_from_file_location('rr_native_c23b', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    # Only this class and its point evaluator are consumed. No spectrum/GL path.
    return mod.Verner96.from_table('HI', path.parent/'data')

def rr_coefficients(E, c, atom, density=None):
    if density is None:
        density = c.get('n_HII_cm3')
    need(not isinstance(density,bool) and isinstance(density,(int,float)) and math.isfinite(density) and density >= 0, 'EXPLICIT_FINITE_HII_DENSITY_REQUIRED')
    E = np.asarray(E, dtype=float)
    need(E.size > 0 and np.all(np.isfinite(E)) and np.all(E > 0), 'POSITIVE_SUPPORTED_KINETIC_ENERGY_REQUIRED')
    need(c.get('I_eV') == 13.6 and c.get('d') == 1 and atom.channel == 'HI', 'H1_GROUND_WEIGHT_CONVENTION')
    photon = E+c['I_eV']
    need(np.all(photon >= atom.threshold_eV) and np.all(photon <= atom.maximum_eV), 'PI_SUPPORT_UNKNOWN_NOT_ZERO')
    pi = np.array([atom.sigma_cm2(float(v)) for v in photon])
    mec2 = c['electron_mass_kg']*c['c_m_s']**2/c['eV_J']
    sigma = pi*photon**2/(c['d']*mec2*E)
    speed = 100*np.sqrt(2*E*c['eV_J']/c['electron_mass_kg'])
    lam = density*speed*sigma
    need(np.all(np.isfinite(lam)) and np.all(sigma > 0), 'INVALID_RR_COEFFICIENT')
    return dict(sigma_PI_cm2=pi,sigma_RR_cm2=sigma,v_cm_s=speed,lambda_RR_s_inverse=lam)

def apply(d,l,u,x):
    y = d[:,None]*x if x.ndim == 2 else d*x
    if x.ndim == 2:
        y[1:] += l[:,None]*x[:-1]
        y[:-1] += u[:,None]*x[1:]
    else:
        y[1:] += l*x[:-1]
        y[:-1] += u*x[1:]
    return y

def solve(d,l,u,rhs):
    need(np.all(d>0) and np.all(l<=0) and np.all(u<=0) and np.all(np.isfinite(rhs)), 'INVALID_KILLED_OPERATOR')
    ab = np.zeros((3,len(d)))
    ab[0,1:] = u
    ab[1] = d
    ab[2,:-1] = l
    x = solve_banded((1,1),ab,rhs)
    need(np.all(np.isfinite(x)), 'NONFINITE_SOLUTION')
    residual = abs(apply(d,l,u,x)-rhs)
    den = apply(abs(d),abs(l),abs(u),abs(x))+abs(rhs)
    need(np.all(residual[den==0] == 0), 'ZERO_RESIDUAL_SCALE')
    scaled = np.divide(residual,den,out=np.zeros_like(residual),where=den>0)
    return x, np.atleast_1d(scaled.max(axis=0)).tolist()

def atoms(unit,z):
    rows = list(csv.DictReader((unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open()))
    need(len(rows)==384, 'EXACT_384_SOURCE_ATOMS_REQUIRED')
    a = {k:np.array([float(row[k]) for row in rows]) for k in rows[0] if k!='channel'}
    need(np.all((a['W_eV']>0)&(a['W_eV']<10)) and np.all(a['pulse_count_cm3']>0), 'SOURCE_DOMAIN')
    return a

def consume(old,c,atom,count):
    E = old['E_eV'][1:]
    d0,l,u = [old['K_'+k] for k in ['diag','lower','upper']]
    coef = rr_coefficients(E,c,atom)
    lam = coef['lambda_RR_s_inverse']
    d = d0+lam
    rhs14 = np.column_stack([old['rhs_first6'],lam,lam*E,old['rhs_bath6']])
    count(14)
    x,res = solve(d,l,u,rhs14)
    count(3)
    v,rv = solve(d,l,u,x[:,[0,1,6]])
    response_rhs = -lam[:,None]*np.column_stack([old['u_s']+old['u_p'],old['t']])
    count(2)
    response,rr = solve(d,l,u,response_rhs)
    count(1)
    w,rw = solve(d0,l,u,lam)
    eta = float(w.max())
    pr = x[:,6]
    lower = w/(1+eta)
    need(np.all(w>0) and np.all(pr>0), 'STRICT_RR_POSITIVITY')
    upper_violation = float(np.maximum((pr-w)/w,0).max())
    lower_violation = float(np.maximum((lower-pr)/lower,0).max())
    photon = x[:,7]+c['I_eV']*pr
    internal = -c['I_eV']*pr
    partition = x[:,:3].sum(axis=1)+pr
    # Final energy reservoirs: six baths, entry, CE outgoing/internal, RR photon/internal.
    ce = x[:,0]+x[:,1]
    ce_in = x[:,4]+x[:,5]
    terms = np.column_stack([x[:,8:14],old['E_eV'][0]*x[:,2],ce_in-c['gap_eV']*ce,c['gap_eV']*ce,photon,internal])
    er = abs(terms.sum(axis=1)-E)/(abs(terms).sum(axis=1)+E)
    loss = (d.astype(np.longdouble)-d0.astype(np.longdouble))-lam.astype(np.longdouble)
    metrics = dict(rhs_scaled_backward_residuals=res+rv+rr+rw,partition_maxabs=float(abs(partition-1).max()),energy_scaled_residual=float(er.max()),probability_min=float(x[:,[0,1,2,6]].min()),probability_max=float(x[:,[0,1,2,6]].max()),eta=eta,rare_upper_relative_violation=upper_violation,rare_lower_relative_violation=lower_violation,delta_CE_max=float(response[:,0].max()),delta_time_max=float(response[:,1].max()),diagonal_addition_lost_rate_max_abs=float(abs(loss).max()),diagonal_addition_loss_relative_to_lambda_max=float((abs(loss)/lam).max()),diagonal_addition_diagnostic_arithmetic='longdouble diagnostic only; independent Decimal70 forms unrounded K0+lambda',old_offdiagonal_exact_reuse=True,old_generator_exact_reuse=True,old_source_projection_exact_reuse=True)
    tol=c['tolerances']
    ok = max(metrics['rhs_scaled_backward_residuals'])<=tol['linear'] and metrics['partition_maxabs']<=tol['partition'] and metrics['energy_scaled_residual']<=tol['energy'] and metrics['probability_min']>=-tol['probability'] and metrics['probability_max']<=1+tol['probability'] and max(upper_violation,lower_violation)<=tol['rare_bound'] and metrics['delta_CE_max']<=0 and metrics['delta_time_max']<=0
    new = dict(E_eV=old['E_eV'],K0_diag=d0,K_diag=d,K_lower=l,K_upper=u,lambda_RR=lam,rhs_physical14=rhs14,rhs_conditional3=x[:,[0,1,6]],rhs_response2=response_rhs,rhs_w=lam,solution_physical14=x,solution_conditional3=v,solution_response2=response,w=w,p_RR=pr,r_RR=x[:,7],v_RR=v[:,2],u_s=x[:,0],u_p=x[:,1],u_entry=x[:,2],t=x[:,3],r_s=x[:,4],r_p=x[:,5],v_s=v[:,0],v_p=v[:,1],H=x[:,8:14],photon_RR=photon,internal_RR=internal,delta_CE=response[:,0],delta_time=response[:,1],energy_terms=terms,**coef)
    return new,metrics,bool(ok)

def source_average(old,new,src,z,c):
    p=old['source_'+z];mask=old['active_mask_'+z];W=src['W_eV'];m=src['pulse_count_cm3'];E=old['E_eV'];pop=p[1:]
    need(np.array_equal(mask,W>E[0]), 'SAVED_ACTIVE_MASK_CHANGED')
    active=float(m[mask].sum());selected=float(m.sum())
    need(abs(float(p.sum())-active)/active<2e-12 and abs(float(p@E)-float(m[mask]@W[mask]))/float(m[mask]@W[mask])<2e-12, 'SAVED_PROJECTION_IDENTITY')
    pr=float(pop@new['p_RR']);rr=float(pop@new['r_RR']);vr=float(pop@new['v_RR']);ce=float(pop@(new['u_s']+new['u_p']));inc=float(pop@(new['r_s']+new['r_p']));gains=pop@new['H'];eta=float(new['w'].max());sw=float(pop@new['w']);time=float(pop@new['t']);dce=float(pop@new['delta_CE']);dt=float(pop@new['delta_time'])
    oldce=float(pop@(old['u_s']+old['u_p']));oldt=float(pop@old['t']);photon=rr+c['I_eV']*pr;internal=-c['I_eV']*pr
    ledger=dict(bath_gain_eV_cm3={k:float(gains[i]) for i,k in enumerate(c['bath_labels'])},entry_energy_eV_cm3=float(E[0]*(float(pop@new['u_entry'])+p[0])),inactive_own_energy_eV_cm3=float(m[~mask]@W[~mask]),CE_outgoing_kinetic_eV_cm3=inc-c['gap_eV']*ce,CE_internal_eV_cm3=c['gap_eV']*ce,RR_photon_retained_eV_cm3=photon,RR_atomic_internal_eV_cm3=internal,initial_kinetic_eV_cm3=float(m@W))
    values=list(ledger['bath_gain_eV_cm3'].values())+[ledger[k] for k in ['entry_energy_eV_cm3','inactive_own_energy_eV_cm3','CE_outgoing_kinetic_eV_cm3','CE_internal_eV_cm3','RR_photon_retained_eV_cm3','RR_atomic_internal_eV_cm3']]
    ledger['scaled_residual']=abs(math.fsum(values)-ledger['initial_kinetic_eV_cm3'])/(math.fsum(abs(v) for v in values)+ledger['initial_kinetic_eV_cm3'])
    return dict(P_RR_active=pr/active,P_RR_selected=pr/selected,conditional_RR_kinetic_eV=rr/pr if pr>0 else None,conditional_RR_photon_eV=photon/pr if pr>0 else None,conditional_RR_time_s=vr/pr if pr>0 else None,RR_photon_eV_per_selected=photon/selected,RR_internal_eV_per_selected=internal/selected,P_CE_active=ce/active,mean_stop_s_active=time/active,delta_CE_active=dce/active,delta_time_s_active=dt/active,paired_CE_relative_to_old=dce/oldce,paired_time_relative_to_old=dt/oldt,old_P_CE_active=oldce/active,old_mean_stop_s_active=oldt/active,subtraction_diagnostic_CE=ce/active-oldce/active,subtraction_diagnostic_time_s=time/active-oldt/active,source_bound_lower=sw/(1+eta)/active,source_bound_upper=sw/active,source_q_count_cm3=float(p[0]),selected_count_cm3=selected,active_count_cm3=active,expected_reaction_events_cm3=pr,expected_population_delta_cm3={'electron':-pr,'HII':-pr,'HI':pr},diagnostic_electron_removed_energy_eV_cm3=rr,ledger=ledger)
