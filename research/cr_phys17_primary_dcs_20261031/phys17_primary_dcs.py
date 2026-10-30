#!/usr/bin/env python3
"""PHYS17. Quantitative KFB76 *unitarized Born 2p* table -> original source recoil model.
  Positive, angular-normalized model interpolation, parent NIST 2p total rate fixed.
  Williams76 original MEASURED n=2 2s+2p only used as independent diagnostic.
  NO 2p-resolved measured DCS, no 2p sublevel density matrix, no physical K.
"""
import csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import wofz
import primary_tables as tab
import phys16_spectral as old

ROOT=Path(__file__).resolve().parent
PARENT_SHA='3b316c595fc1b40109f39d91af92873ba5a215281040d70bcb177dd1ab74a7dc'
PWBA_PDF_SHA='ccd609d3cc951ab1507c90423466de278816dffddb260f7c4e4648a468d18db2'
PR140_PHYS15_SHA=old.PHYS15_SHA
PDF_KINGSTON_SHA='d7767365440f840e5638eec38a46223bfbbf3a27a4c0296ecc1d35b6ec1b1c78'
PDF_WILLIAMS_SHA='09d3cb9c950f74624e7cd35d75d6d8a154d22102f19d75ee42493ff9d4c586ed'
K_EV=np.array([13.6,19.6,30.6])  # Kingston printed p616; avoid false unrounded precision.
ANGLE_GL=48
G_MU,G_MW=np.polynomial.legendre.leggauss(ANGLE_GL)
EM_W=old.WU
EM_DIP_W=old.DIPOLE_W
EM_ISO_W=old.ISO_W
LABELS=('KFB_UB2P_E1','KFB_UB2P_ISOTROPIC_EMISSION','PWBA_E1_PARENT')

def sha(b):return hashlib.sha256(b).hexdigest()

def dcs_at_mu(e_eV,mu,channel='2p'):
    """log-linear interpolation between *published* energy nodes; log PCHIP in cos(theta).
    This is an explicit model interpolation, not source-measured values at arbitrary energy.
    """
    e=float(e_eV)
    if not (K_EV[0]<=e<=K_EV[-1]):raise ValueError('DCS_ENERGY_OUTSIDE_PUBLISHED_NODES')
    vals=tab.K2P if channel=='2p' else tab.K2S
    vals_en=np.array([np.interp(e,K_EV,np.log(vals[i,:])) for i in range(len(tab.K_TH))])
    xx=np.cos(np.deg2rad(tab.K_TH))
    y=PchipInterpolator(xx[::-1],vals_en[::-1],extrapolate=False)(np.asarray(mu))
    if np.any(~np.isfinite(y)):raise ValueError('DCS_ANGLE_OUTSIDE_RANGE')
    return np.exp(y)

def normalized_angular(e_eV,channel='2p',nodes=G_MU,weights=G_MW):
    v=dcs_at_mu(e_eV,nodes,channel)
    z=np.sum(weights*v)
    if z<=0: raise ValueError('NONPOSITIVE_CROSS_SECTION')
    return weights*v/z, 2*np.pi*z  # dσ/dΩ = a0²/sr, sigma = a0²

def emitted_kfb(e_eV):
    p,sig=normalized_angular(e_eV)
    _ratio,vrec,erec,recoil_err,_z=old.exact_recoil(e_eV,G_MU)
    shape=np.real(wofz(old.XGRID[None,None,:]-vrec[:,None,None]*EM_W[None,:,None]+old.ETA_EM+1j*old.A))/np.sqrt(np.pi)
    p_e1=np.einsum('i,j,ijk->k',p,EM_DIP_W,shape,optimize=True)
    p_iso=np.einsum('i,j,ijk->k',p,EM_ISO_W,shape,optimize=True)
    return p_e1,p_iso,float(np.dot(p,erec)),float(np.dot(p,vrec*vrec)),sig,recoil_err

def measured_diagnostics():
    rows=[]
    for j,e in enumerate(tab.W_ENERGIES):
        if not (K_EV[0]<=e<=K_EV[-1]):raise AssertionError('MEASURED_ENERGY_OOB')
        for i,t in enumerate(tab.W_TH):
            mu=np.cos(np.deg2rad(t))
            a=float(dcs_at_mu(e,mu,'2p'))
            b=float(dcs_at_mu(e,mu,'2s'))
            m=float(tab.W_N2[i,j]);err=float(tab.W_ERR[i,j]);v=a+b
            rows.append(dict(energy_eV=float(e),angle_deg=int(t),measured_N2_DCS_a0_sq_sr=m,measured_uncertainty_a0_sq_sr=err,KFB_UB2P_model_DCS_a0_sq_sr=a,KFB_UB2S_model_DCS_a0_sq_sr=b,KFB_UB_N2_sum_model_DCS_a0_sq_sr=v,KFB_UB_2p_model_fraction=a/(a+b),signed_residual_in_reported_error_units=(v-m)/err,model_2p_exceeds_measured_total=bool(a>m)))
    return rows

def read_parent_crosswalk():
    p=ROOT/'sources'/'PHYS16_SOURCE_RECOIL_MODEL_CROSSWALK.csv'
    return list(csv.DictReader(p.open()))

def calculate(parent_zip, out):
    parent_zip=Path(parent_zip);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if sha(parent_zip.read_bytes())!=PARENT_SHA:raise ValueError('PARENT_PHYS16_SHA256_MISMATCH')
    if sha((ROOT/'sources/PHYS16_SOURCE_EMISSION_PROFILES.npz').read_bytes())!=PWBA_PDF_SHA:raise ValueError('PARENT_PWBA_PROFILE_SHA256_MISMATCH')
    source=(ROOT/'sources'/'PR140_PHYS15_SOURCE.zip')
    if sha(source.read_bytes())!=PR140_PHYS15_SHA:raise ValueError('PARENT_PHYS15_SHA256_MISMATCH')
    ref=np.load(ROOT/'sources/PHYS16_SOURCE_EMISSION_PROFILES.npz',allow_pickle=False)
    if ref['profiles'].shape!=(2066,3,len(old.XGRID)):raise ValueError('PARENT_PROFILE_SHAPE_CHANGED')
    src=read_parent_crosswalk()
    if len(src)!=2066:raise ValueError('SOURCE_ROWS_CHANGED')
    if not np.array_equal(np.asarray([int(r['source_atom_index']) for r in src]),ref['source_index']):raise ValueError('PARENT_SOURCE_ORDER_CHANGED')
    if np.max(np.abs(np.asarray([float(r['Ee_eV']) for r in src])-ref['Ee_eV']))>1e-13:raise ValueError('PARENT_ENERGY_CHANGED')
    profiles=np.zeros((2066,3,len(old.XGRID)),dtype=np.float64)
    source_moments=[]
    for i,r in enumerate(src):
        e=float(r['Ee_eV']);e1,iso,erecoil,vrec2,dcs_total,err=emitted_kfb(e)
        profiles[i,0]=e1;profiles[i,1]=iso;profiles[i,2]=ref['profiles'][i,0]
        _p,old_recoil,*_=old.born_angular(e)
        source_moments.append(dict(source='He',source_atom_index=int(r['source_atom_index']),Ee_eV=e,source_photon_energy_eV=float(r['photon_energy_eV']),excitation_earliest_m3=float(r['excitation_earliest_m3']),excitation_latest_m3=float(r['excitation_latest_m3']),KFB_UB2P_interpolated_total_DCS_a0_sq=dcs_total,KFB_UB2P_model_recoil_mean_eV=erecoil,PWBA_model_recoil_mean_eV=float(r['collision_recoil_mean_eV']),KFB_UB2P_model_centre_variance_x2=0.5+vrec2/5,relative_kinetic_energy_residual=err,closure='KFB1976_TABLE5_UB2P_ANGULAR_PLUS_ASSUMED_E1_Q_AXIS_WITH_ORIGINAL_NIST_TOTAL'))
    tab.write_csv(out/'SOURCE_UB2P_RECOIL_CROSSWALK.csv',source_moments)
    np.savez_compressed(out/'SOURCE_EMISSION_PROFILES.npz', profiles=profiles, x=old.XGRID, source_index=ref['source_index'],source_type=ref['source_type'],Ee_eV=ref['Ee_eV'])
    comparison=measured_diagnostics()
    tab.write_csv(out/'WILLIAMS_MEASURED_N2_VS_KFB_UB_N2.csv',comparison)
    spectral=[];scoped={}
    for policy in ('earliest','latest'):
        weights=np.array([float(r['excitation_'+policy+'_m3']) for r in src]);total=float(sum(weights))
        for j,label in enumerate(LABELS):
            curve=weights@profiles[:,j,:]/total
            mass=float(np.trapezoid(curve,old.XGRID))
            hazard=float(np.trapezoid(curve*old.hi_first_scatter_rate(old.XGRID),old.XGRID))
            scoped[policy+':'+label]=dict(parent_N2p_m3=total,inside_x16_mass=mass,source_weighted_initial_scatter_hazard_s=hazard)
            for k,x in enumerate(old.XGRID):
                spectral.append(dict(policy=policy,model=label,x_Doppler=float(x),source_weighted_emission_pdf=curve[k],emission_source_number_density_per_x_m3=float(total*curve[k]),hi_first_scatter_rate_s=float(old.hi_first_scatter_rate(x))))
    tab.write_csv(out/'SOURCE_UB2P_EMISSION_SPECTRA.csv',spectral)
    # Independent source-qualified model variations constrained by authentic DCS data.
    baseline_total={p:scoped[p+':'+LABELS[0]]['parent_N2p_m3'] for p in ('earliest','latest')}
    residuals={str(float(e)):{'RMS_reported_error_standardized':float(np.sqrt(np.mean([r['signed_residual_in_reported_error_units']**2 for r in comparison if r['energy_eV']==e]))),'max_reported_error_standardized':float(max(abs(r['signed_residual_in_reported_error_units']) for r in comparison if r['energy_eV']==e)),'model_2p_exceeds_measured_total_count':sum(r['model_2p_exceeds_measured_total'] for r in comparison if r['energy_eV']==e)} for e in tab.W_ENERGIES}
    from scipy.integrate import quad
    from scipy.interpolate import PchipInterpolator
    mu=np.cos(np.deg2rad(tab.K_TH))
    integral_checks=[]
    for j,k in enumerate(tab.K2):
        for state,arr,printed in [('2p',tab.K2P,tab.K2P_UB_TOTAL_PI),('2s',tab.K2S,tab.K2S_UB_TOTAL_PI)]:
            f=PchipInterpolator(mu[::-1],np.log(arr[::-1,j]))
            got=float(2*quad(lambda m:np.exp(f(m)),-1,1,epsabs=1e-11)[0]);expected=float(printed[j]);integral_checks.append(dict(k2_Ryd=float(k),channel=state,table6or7_UB_total_pi_a0_sq=expected,quadrature_total_pi_a0_sq=got,relative_difference=(got-expected)/expected))
    result=dict(unit='CR_PHYS17_PRIMARY_1976_UB_2P_DCS_SOURCE_RECOIL',parent_PR=141,parent_HEAD='30020355677b66930856a385cf5cd4e9c3c3a24c',source_photon_atoms=6400,source_qualified_2p_atoms=2066,temperature_K=100,neutral_density_HI_m3=138.6,source_ownership='UNCHANGED_NIST_BE_TOTAL_SHAH_MEASURED_EII',actual_pdfs_used={'Kingston1976':PDF_KINGSTON_SHA,'Williams1976':PDF_WILLIAMS_SHA},DCS_k2_2p='KINGSTON_1976_TABLE5_UNITARIZED_BORN_NOT_CLOSE_COUPLING',measured_comparison_semantics='WILLIAMS_1976_TABLE1_N2_2S_PLUS_2P_UNRESOLVED',calculation='MODEL_CONDITIONAL_WITH_KFB_UB2P_SHAPE_AND_ASSUMED_E1_ALIGNMENT',primary_table_rows=90+48+6,matched_experiment_rows=48,source_emission_profiles=2066*3*len(old.XGRID),source_weighted_spectra_rows=len(spectral),source_crosswalk_rows=len(source_moments),spectrum=scoped,measured_comparison=residuals,angular_table_integral_checks=integral_checks,max_abs_table_angular_integral_relative_diff=float(max(abs(x['relative_difference']) for x in integral_checks)),full_radial_kinetics_K='UNBOUND',true_2p_density_matrix='UNBOUND',full_RII_detailed_balance='UNBOUND',global_He_exclusive='UNBOUND',geometry_thermal_clock_radiation='UNBOUND',central_DAG='28/88 DELTA0',extension_DAG='0/3 DELTA0',production='HOLD',native25='HOLD',L4='HOLD',R06_distinct_author='NOT_RUN',C09_distinct_author='NOT_RUN',auto_next=False,no_merge=True,no_force_push=True,rigorous_model_tail_probability_upper_x16=0.00021475188281429132)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    import argparse
    ar=argparse.ArgumentParser();ar.add_argument('--parent',default=str(ROOT/'sources/PR141_PHYS16_SOURCE.zip'));ar.add_argument('--output',default=str(ROOT/'results'));a=ar.parse_args()
    r=calculate(a.parent,a.output)
    print(json.dumps({k:r[k] for k in ['source_emission_profiles','source_weighted_spectra_rows','matched_experiment_rows','max_abs_table_angular_integral_relative_diff','measured_comparison']},indent=2))
