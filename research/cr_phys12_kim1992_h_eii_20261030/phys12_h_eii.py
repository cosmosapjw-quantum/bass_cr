#!/usr/bin/env python3
"""PHYS12: H(1s) e-impact microscopic coefficients and finite-horizon two-event envelope.

Input is exact, immutable PHYS11 source-inclusive ZIP. Kim 1992 Table 1 fit is
empirically fitted to Shah et al. 1987, NOT the raw measured cross-section table.
All two-event numbers are upper *fit-model* envelopes conditioned on a frozen 100 K
H/He source, static neutral densities, no field acceleration, non-increasing electron
kinetic energy and a Markov local n*sigma*v hazard. No trajectory or stopping is
asserted. K energy cap and cosmological evolution remain unbound.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, sys, tempfile, zipfile
from pathlib import Path
import numpy as np

PHYS11_SHA256='afedf6ac708e17e847d086625af47c0cf0a902b8ec2f1c168daf16b198ef050a'
PHYS11_HEAD='d7de61661b718f9968acd4e696510603968e18e7'
PHYS10_SHA256='faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033'
PARENT_ROOT='research/cr_phys11_secondary_capacity_20261030/'
SOURCE_REF='Y.-K. Kim 1992 J Res NIST 97, 689-692 DOI:10.6028/jres.097.032 Table 1 Eq (2); H fit to Shah et al 1987'
EV_J=1.602176634e-19
ME_KG=9.1093837139e-31
KM_I_EV=13.61
KM_A=0.7576
KM_B=-5.521
KM_C=5.867
KM_D=2.948
SIGMA_SCALE_M2=1e-20  # 10^-16 cm² = 10^-20 m²
TIMES=np.arange(9,dtype=float)*1.25e9
POLICIES=('earliest','midpoint','latest')
TARGETS=('HI','HeI')
ENERGY_BINS=list(zip(np.arange(13.0,36.0,1.),np.arange(14.0,37.0,1.)))
_GL_X,_GL_W=np.polynomial.legendre.leggauss(24)
_GL_Q=0.5*(_GL_X+1.0)
_GL_WEIGHT=0.5*_GL_W

def sha(b):return hashlib.sha256(b).hexdigest()
def fs(x):return math.fsum(float(t) for t in np.asarray(x).ravel())

def load_owner(fullzip):
    b=Path(fullzip).read_bytes()
    if sha(b)!=PHYS11_SHA256:raise ValueError('PHYS11_SOURCE_SHA256_MISMATCH')
    with zipfile.ZipFile(fullzip) as z:
        if z.testzip():raise ValueError('PHYS11_CRC_FAIL')
        entries=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
        if len(entries)!=48:raise ValueError('PHYS11_MANIFEST_COUNT_DRIFT')
        for e in entries:
            raw=z.read(PARENT_ROOT+e['path'])
            if len(raw)!=e['size'] or sha(raw)!=e['sha256']:raise ValueError('PHYS11_MEMBER_HASH_MISMATCH:'+e['path'])
        code=z.read(PARENT_ROOT+'phys11_capacity.py')
        inner=z.read(PARENT_ROOT+'sources/PR135_ORIGINAL_SOURCE.zip')
    if sha(inner)!=PHYS10_SHA256:raise ValueError('PHYS10_SOURCE_NESTING_ERROR')
    with tempfile.TemporaryDirectory(prefix='cr_phys12_lock_') as td:
        d=Path(td);(d/'phys11_capacity.py').write_bytes(code);(d/'PHYS10.zip').write_bytes(inner)
        spec=importlib.util.spec_from_file_location('cr_phys11_exact_owner_for_phys12',d/'phys11_capacity.py')
        owner=importlib.util.module_from_spec(spec);sys.modules[spec.name]=owner;spec.loader.exec_module(owner)
        result=owner.load_source(d/'PHYS10.zip')
    mod,edges,prep,params,dens=result
    if sum(len(pp['energy']) for pp in prep)!=6400:raise ValueError('ATOM_COUNT_DRIFT')
    if abs(float(dens['HI'])-138.6)>1e-12:raise ValueError('NEUTRAL_DENSITY_DRIFT')
    return result

def kim_sigma_m2(incident_E_eV):
    E=np.asarray(incident_E_eV,dtype=float)
    x=E/KM_I_EV
    x_safe=np.maximum(x,1.0)
    # log1p is exact to first order close to the published 13.61 eV threshold.
    L=np.log1p(x_safe-1.0)
    val=(KM_A*L+(KM_B*L+KM_C*(x_safe-1.0))/(x_safe+KM_D))/x_safe
    return np.where(E>KM_I_EV,SIGMA_SCALE_M2*val,0.0)

def velocity_m_s(E_eV):
    return np.sqrt(2*EV_J*np.maximum(np.asarray(E_eV,dtype=float),0.)/ME_KG)

def eii_micro(E_eV,nH_m3):
    s=kim_sigma_m2(E_eV)
    v=velocity_m_s(E_eV)
    return s,v,s*v,float(nH_m3)*s,float(nH_m3)*s*v

def first_probability(mod,ka,kb,dt,target):
    return mod.first_probability(ka,kb,dt,target)

def bound_probability(ka,k_all,nu,dt):
    """Capped two-event probability; first photon H photoabsorbs before secondary H EII.

    Valid as an upper envelope when the collision rate along the electron history
    cannot exceed its original energy-specific nu and H density stays frozen.
    Positive Gauss-Legendre integration avoids cancellation of two small hazards.
    """
    a=np.asarray(ka,dtype=float)
    k=np.asarray(k_all,dtype=float)
    nu=np.asarray(nu,dtype=float)
    if dt<=0:return np.zeros_like(a)
    u=dt*_GL_Q[:,None]
    remain=dt-u
    integrand=a[None,:]*np.exp(-u*k[None,:])*(-np.expm1(-remain*nu[None,:]))
    return dt*np.einsum('i,ij->j',_GL_WEIGHT,integrand)

def bound_gradient_uniform(ka,khe,nu,dt,which):
    """d bound_probability / d ln n_which, both photon hazard and electron hazard."""
    a=np.asarray(ka,dtype=float)
    h=np.asarray(khe,dtype=float)
    nu=np.asarray(nu,dtype=float)
    if dt<=0:return np.zeros_like(a)
    u=dt*_GL_Q[:,None]; remain=dt-u
    ee=np.exp(-(a+h)[None,:]*u)
    ee_nu=np.exp(-nu[None,:]*remain)
    gain=-np.expm1(-nu[None,:]*remain)
    if which=='HI':
        term=(1-a[None,:]*u)*gain+nu[None,:]*remain*ee_nu
    elif which=='HeI':
        term=-h[None,:]*u*gain
    else:raise ValueError('INVALID_NEUTRAL_PARAMETER')
    return dt*np.einsum('i,ij->j',_GL_WEIGHT,a[None,:]*ee*term)

def write_csv(path,items):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]),lineterminator='\n')
        w.writeheader();w.writerows(items)

def generate(source_zip,out):
    mod,edges,prep,params,dens=load_owner(source_zip)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    hi=float(params['HI'][0]);hei=float(params['HeI'][0]);nH=float(dens['HI'])
    atom=[];channels=[];totals=[];spectrum=[];gradients=[]
    prepared=[]
    for pp in prep:
        src=pp['source'];E=np.asarray(pp['energy'],dtype=float)
        kh=np.asarray(pp['k']*pp['frac'][0],dtype=float)
        khe=np.asarray(pp['k']*pp['frac'][1],dtype=float)
        for a,target in enumerate(TARGETS):
            eps=np.maximum(E-float(params[target][0]),0.)
            sigma,v,sv,kap,nu=eii_micro(eps,nH)
            # Even if an electron has sufficient energy, secondary-He impact is not
            # included; only first-photoabsorber H produces a candidate in source.
            if a!=0:sigma=np.zeros_like(sigma);sv=np.zeros_like(sigma);kap=np.zeros_like(sigma);nu=np.zeros_like(sigma)
            cond=(a==0)&(eps>=hi)
            prepared.append(dict(pp=pp,source=src,absorber=a,E=E,eps=eps,ka=kh if a==0 else khe,kh=kh,khe=khe,nu=nu,sv=sv,sigma=sigma,kap=kap,cond=cond))
            for i in range(len(E)):
                atom.append(dict(source=src,source_energy_index=i,first_absorber=target,photon_E_eV=float(E[i]),
                   initial_electron_eV=float(eps[i]),PHYS11_H_eligible=int(cond[i]),
                   Kim1992_fit_sigma_m2=float(sigma[i]),electron_speed_m_s=float(v[i]),
                   Kim1992_sigma_v_m3_s=float(sv[i]),frozen_H_opacity_m_inv=float(kap[i]),
                   frozen_H_collision_rate_s_inv=float(nu[i]),
                   frozen_H_mean_free_path_pc=(1/kap[i]/3.085677581491367e16 if kap[i]>0 else ''),
                   photon_first_H_hazard_s_inv=float(kh[i]),photon_first_He_hazard_s_inv=float(khe[i])))
    for T in TIMES:
        for policy in POLICIES:
            T=float(T);totalFirst=[];totalEligible=[];totalMicro=[];totalBound=[];totalKinetic=[];source_by={}
            for q in prepared:
                pp=q['pp'];src=q['source'];a=q['absorber'];target=TARGETS[a]
                E=q['E'];eps=q['eps'];kh=q['kh'];khe=q['khe'];kt=kh+khe
                first_parts=[];eligible_parts=[];micro_parts=[];bound_parts=[];kin_parts=[]
                for j in range(4):
                    birth=mod.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                    dt=T-birth;raw=np.asarray(pp['weights'][j])
                    first=first_probability(mod,kh,khe,dt,a)
                    cap=first*(q['cond'].astype(float))
                    bp=bound_probability(kh,kt,q['nu'],dt)
                    first_parts.append(fs(raw*first));eligible_parts.append(fs(raw*cap))
                    micro_parts.append(fs(raw*first*q['sv']))
                    bound_parts.append(fs(raw*bp));kin_parts.append(fs(raw*bp*hi*EV_J))
                n,eligible,micro,bound,kin=(math.fsum(x) for x in [first_parts,eligible_parts,micro_parts,bound_parts,kin_parts])
                channels.append(dict(observation_s=T,birth_policy=policy,source=src,first_absorber=target,
                   first_photoabsorptions_m3=n,source_kinematic_capacity_m3=eligible,
                   first_population_weighted_sigma_v_s_inv=micro,
                   finite_horizon_upper_H_second_m3=bound,
                   fraction_upper_H_second_over_first=(bound/n if n else ''),
                   H_second_binding_upper_J_m3=kin))
                totalFirst.append(n);totalEligible.append(eligible);totalMicro.append(micro);totalBound.append(bound);totalKinetic.append(kin)
            n,cap,micro,bound,kin=map(math.fsum,[totalFirst,totalEligible,totalMicro,totalBound,totalKinetic])
            totals.append(dict(observation_s=T,birth_policy=policy,
                   first_photoabsorptions_m3=n,PHYS11_energy_eligible_capacity_m3=cap,
                   first_population_weighted_sigma_v_s_inv=micro,
                   finite_horizon_upper_H_second_m3=bound,
                   fraction_upper_H_second_over_first=bound/n if n else '',
                   fraction_upper_over_energy_capacity=bound/cap if cap else '',
                   H_second_binding_upper_J_m3=kin))
    # Integrate finite-horizon bound by original source energy bin and birth policy.
    tf=float(TIMES[-1])
    for q in prepared:
        pp=q['pp'];src=q['source'];a=q['absorber'];target=TARGETS[a]
        for policy in ('earliest','latest'):
            wfirst=np.zeros(len(q['E']));wbound=np.zeros(len(q['E']))
            for j in range(4):
                dt=tf-mod.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                raw=np.asarray(pp['weights'][j]);wfirst+=raw*mod.first_probability(q['kh'],q['khe'],dt,a)
                wbound+=raw*bound_probability(q['kh'],q['kh']+q['khe'],q['nu'],dt)
            for low,high in ENERGY_BINS:
                mask=(q['E']>=low)&(q['E']<high)
                spectrum.append(dict(source=src,birth_policy=policy,first_absorber=target,E_lo_eV=float(low),E_hi_eV=float(high),
                  first_m3=fs(wfirst[mask]),energy_capacity_m3=fs(wfirst[mask]*q['cond'][mask]),
                  finite_horizon_second_upper_m3=fs(wbound[mask]),
                  average_fit_sigma_v_conditioned_m3_s=(fs(wfirst[mask]*q['sv'][mask])/fs(wfirst[mask]) if fs(wfirst[mask])>0 else '')))
    # Uniform perturbation of frozen H or He for the final 3 birth witnesses and
    # every 9 observation epoch (same source, not time-local perturbation).
    for T in TIMES:
        T=float(T)
        for policy in POLICIES:
            for neutral in TARGETS:
                contributions=[]
                for q in prepared:
                    pp=q['pp']
                    for j in range(4):
                        birth=mod.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                        gp=bound_gradient_uniform(q['kh'],q['khe'],q['nu'],T-birth,neutral)
                        contributions.append(fs(np.asarray(pp['weights'][j])*gp))
                dcount=math.fsum(contributions)
                gradients.append(dict(observation_s=T,birth_policy=policy,neutral_parameter=neutral,
                  d_H_second_upper_dln_neutral_m3=dcount,
                  d_H_second_binding_upper_J_m3=dcount*hi*EV_J))
    sizes={'atom':len(atom),'time_channels':len(channels),'time_totals':len(totals),'energy_bins':len(spectrum),'uniform_gradients':len(gradients)}
    if sizes!={'atom':12800,'time_channels':108,'time_totals':27,'energy_bins':184,'uniform_gradients':54}:raise AssertionError('EXPECTED_COUNTS_DRIFT:'+str(sizes))
    if any(row['finite_horizon_upper_H_second_m3']>row['source_kinematic_capacity_m3']*(1+1e-13) for row in channels):raise AssertionError('TWO_EVENT_BOUND_OVER_CAP')
    if any(row['finite_horizon_upper_H_second_m3']<0 for row in channels):raise AssertionError('NEGATIVE_BOUND')
    for row in channels:
        if row['source']!='He' or row['first_absorber']!='HI':
            if row['finite_horizon_upper_H_second_m3']!=0:raise AssertionError('UNSUPPORTED_PHYSICAL_CHANNEL')
    for name,rows in [('MICROSCOPIC_SOURCE_ATOMS.csv',atom),('TIME_CHANNEL_TWO_EVENT.csv',channels),('TIME_TOTAL_TWO_EVENT.csv',totals),('FINAL_ENERGY_BIN_TWO_EVENT.csv',spectrum),('UNIFORM_NEUTRAL_RESPONSE.csv',gradients)]:write_csv(out/name,rows)
    pick=lambda policy:next(x for x in totals if x['observation_s']==tf and x['birth_policy']==policy)
    result={'unit':'CR_PHYS12_KIM1992_H_EII_FINITE_HORIZON', 'origin':'PHYS11 immutable original H/He 6400 RR photon energy atoms, 4 original birth bins, original 100 K and frozen neutral density','source_parent_SHA256':PHYS11_SHA256,'parent_git_head':PHYS11_HEAD,'external_empirical_fit':{'source':SOURCE_REF,'formula':'sigma=1e-20 m²/x*[A ln(x)+(B ln(x)+C(x-1))/(x+D)]; x=Ee/13.61 eV; sigma=0 for Ee<=13.61','I_fit_eV':KM_I_EV,'A':KM_A,'B':KM_B,'C':KM_C,'D':KM_D,'is_raw_shah_measurements':False},'source_H_threshold_eV':hi,'source_He_threshold_eV':hei,'frozen_n_HI_m3':nH,'source_atoms':6400,'PHYS11_kinematic_H_eligible_atom_rows':sum(int(z['PHYS11_H_eligible']) for z in atom),'Kim_fit_positive_atom_rows':sum(z['Kim1992_fit_sigma_m2']>0 for z in atom),'Kim_fit_extrapolation_atom_rows_below_Shah1987_14_6eV':sum((z['Kim1992_fit_sigma_m2']>0 and z['initial_electron_eV']<14.6) for z in atom),'rows':sizes,'total_rows':sum(sizes.values()),'final_earliest':pick('earliest'),'final_midpoint':pick('midpoint'),'final_latest':pick('latest'),'sigma_v_at_20_99eV_m3_s':float(eii_micro(np.array([20.99]),nH)[2][0]),'mean_free_path_at_20_99eV_pc':float(1/eii_micro(np.array([20.99]),nH)[3][0]/3.085677581491367e16),'max_kinetic_electron_energy_eV':20.99,'event_upper_conditional':'No external electron acceleration, no kinetic-energy gain, source-frozen n_HI/n_HeI in proper time, nonrel EII, local first-hit Markov hazard with Kim1992 total atomic H fit; no stopping assumed','not_extracted':'Shah1987 original raw data table, electron trajectories, stopping, diffusion, actual realized event rate, full physical K, global He kernel, evolving gas/radiation, observation/thermal deposition','new_scoped_auxiliary':'1/1 CONDITIONAL REVIEW_HOLD','central_DAG':'28/88 delta0','extension_DAG':'0/3 delta0','R06_distinct_author':'NOT_RUN','C09_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN','production':'HOLD','merge_ready':False,'auto_next':False}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'rows':sizes,'full':result['final_earliest'],'latest':result['final_latest'],'lmax_pc':result['mean_free_path_at_20_99eV_pc']},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-zip',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args();generate(a.source_zip,a.out)
