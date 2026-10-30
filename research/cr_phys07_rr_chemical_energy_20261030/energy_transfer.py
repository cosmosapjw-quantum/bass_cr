#!/usr/bin/env python3
"""Source-pinned H/He recombination photon chemical-potential/primary-electron ledger.

Physics is the original PHYS06 fixed 100 K, fixed opacity, first absorption.
No full thermal/chemistry IVP. All published results derive from the frozen source.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, importlib.util, json, math, tempfile, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'sources/PR131_ORIGINAL_SOURCE.zip'
SOURCE_SHA256='6e2fe94051845612d06cbd880eb8c876a0c6692efbe6ef1f8408cd7784b0b764'
ORIGINAL_PR130_SHA256='89fd528ede24929cb29b51b1edf55f27ad1ea1f7c0a61f976884ebe657e48cb3'
EV_J=1.602176634e-19
TIMES=np.arange(9,dtype=float)*1.25e9
SOURCES=('H','He')
TARGETS=('HI','HeI')
POLICIES=('earliest','latest','midpoint')
ENERGY_BINS=np.arange(13.,37.,1.)


def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def fs(x):return math.fsum(float(v) for v in np.asarray(x).ravel())


def load_source(source:Path=SOURCE):
    content=Path(source).read_bytes()
    if sha256(content)!=SOURCE_SHA256:raise ValueError('PHYS06_SOURCE_SHA_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        if z.testzip() is not None:raise ValueError('PHYS06_SOURCE_ZIP_CRC')
        manifest=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
        if len(manifest)!=45:raise ValueError('PHYS06_SOURCE_MANIFEST_LENGTH')
        for q in manifest:
            b=z.read(q['path'])
            if sha256(b)!=q['sha256'] or len(b)!=q['size']:raise ValueError('PHYS06_SOURCE_MEMBER_MISMATCH:'+q['path'])
        pre='research/cr_phys06_rr_photon_recycling_20261030/'
        program=z.read(pre+'recycling.py')
        ancestor=z.read(pre+'sources/PR130_ORIGINAL_SOURCE.zip')
        prev=json.loads(z.read(pre+'results/RESULT.json'))
    if sha256(ancestor)!=ORIGINAL_PR130_SHA256:raise ValueError('PR130_ORIGINAL_SOURCE_SHA_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='cr_ph07_owner_') as td:
        t=Path(td); (t/'recycling.py').write_bytes(program); (t/'PR130_ORIGINAL_SOURCE.zip').write_bytes(ancestor)
        spec=importlib.util.spec_from_file_location('source_owned_phys06',t/'recycling.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        arrays,dens,params,sigma,baseline,ref=mod.load_locked(t/'PR130_ORIGINAL_SOURCE.zip')
        edges,prep=mod.make_prepared(arrays,dens,params,sigma)
    if params['HI'][0]!=13.6 or params['HeI'][0]!=24.59:raise ValueError('THRESHOLD_SOURCE_UNBOUND')
    if dens['HI']!=138.6 or not np.isclose(dens['HeI'],11.427127659574467,rtol=0,atol=1e-14):raise ValueError('FROZEN_NEUTRAL_SOURCE_UNBOUND')
    return edges,prep,params,dens,prev


def branch_prob(k,dt):
    if dt<=0:return np.zeros_like(k)
    return -np.expm1(-k*dt)


def source_birth_time(a,b,policy):
    return {'earliest':a,'latest':b,'midpoint':(a+b)/2.}[policy]


def epoch_ledger(prep,edges,params,T,policy):
    if policy not in POLICIES:raise ValueError('BAD_POLICY')
    if T<0 or T>edges[-1]:raise ValueError('BAD_TIME')
    born=[0.,0.];surv=[0.,0.];absorber=[0.,0.];abs_m=np.zeros((2,2))
    bind_in=[];kin_before=[];survE=[];threshold_out=[];kin_after=[]
    channel_acc={ (s,t): dict(ions=[],incoming_kin=[],primary_kin=[],binding_delta=[],photon_energy=[]) for s in SOURCES for t in TARGETS }
    for i,p in enumerate(prep):
        name=p['source'];E=p['energy'];k=p['k'];f=p['frac'];W=p['weights']
        I_s=float(params['HI' if name=='H' else 'HeI'][0])
        epre=E-I_s
        if np.any(epre<0):raise AssertionError('ORIGINAL_PRE_RR_ELECTRON_KINETIC_NEGATIVE')
        for j in range(4):
            a,b=(float(z) for z in edges[j:j+2]);s=source_birth_time(a,b,policy)
            if s>T:continue
            w=W[j];born[i]+=fs(w)
            bind_in.append(fs(w)*I_s*EV_J);kin_before.append(fs(w*epre)*EV_J)
            survival=np.exp(-k*(T-s));frac_abs=branch_prob(k,T-s)
            surv[i]+=fs(w*survival);survE.append(fs(w*survival*E)*EV_J)
            for t,ta in enumerate(TARGETS):
                I_a=float(params[ta][0]);mass=w*frac_abs*f[t]
                if name=='H' and ta=='HeI' and fs(mass)!=0:raise AssertionError('H_TO_HE_PHOTON_BELOW_THRESHOLD')
                if np.any((E<I_a)&(mass>0)):raise AssertionError('BELOW_THRESHOLD_POSITIVE_ABSORPTION')
                ions=fs(mass);absorber[t]+=ions;abs_m[i,t]+=ions
                c=channel_acc[(name,ta)]
                c['ions'].append(ions)
                c['incoming_kin'].append(fs(mass*epre)*EV_J)
                c['primary_kin'].append(fs(mass*np.maximum(E-I_a,0))*EV_J)
                c['binding_delta'].append(ions*(I_s-I_a)*EV_J)
                c['photon_energy'].append(fs(mass*E)*EV_J)
                threshold_out.append(ions*I_a*EV_J)
                kin_after.append(fs(mass*np.maximum(E-I_a,0))*EV_J)
    source_binding=fs(bind_in);source_prekin=fs(kin_before);survivor_energy=fs(survE)
    target_binding=fs(threshold_out);target_kin=fs(kin_after)
    net_neutral_H=born[0]-absorber[0];net_neutral_He=born[1]-absorber[1]
    residual=math.fsum([source_binding,source_prekin,-survivor_energy,-target_binding,-target_kin])
    photon_total=math.fsum([source_binding,source_prekin]); tol=photon_total*1e-13+1e-85
    if abs(residual)>tol:raise AssertionError(f'BINDING_PHOTON_ENERGY_NOT_CONSERVED:{residual}')
    net_e=absorber[0]+absorber[1]-born[0]-born[1]
    if abs(net_e+sum(surv))>sum(born)*1e-13+1e-83:raise AssertionError('CHARGE_ELECTRON_COUNT')
    ch=[]
    for name,ta in channel_acc:
        c=channel_acc[(name,ta)];z={key:fs(vals) for key,vals in c.items()}
        check=math.fsum([z['primary_kin'],-z['incoming_kin'],-z['binding_delta']])
        if abs(check)>max(z['primary_kin'],z['incoming_kin'],abs(z['binding_delta']),1e-80)*5e-13:
            raise AssertionError('CHANNEL_KINETIC_BINDING_IDENTITY:'+name+'->'+ta)
        ch.append(dict(time_s=float(T),policy=policy,source=name,target=ta,
                       absorption_m3=z['ions'],absorbed_photon_energy_J_m3=z['photon_energy'],
                       incoming_recombining_electron_kinetic_of_absorbed_photons_J_m3=z['incoming_kin'],
                       primary_photoelectron_kinetic_J_m3=z['primary_kin'],
                       net_kinetic_transfer_from_binding_J_m3=z['binding_delta']))
    total=dict(time_s=float(T),policy=policy,source_H_births_m3=born[0],source_He_births_m3=born[1],
        net_neutral_HI_m3=net_neutral_H,net_neutral_HeI_m3=net_neutral_He,
        ion_HII_change_m3=-net_neutral_H,ion_HeII_change_m3=-net_neutral_He,
        net_free_electron_change_m3=net_e,surviving_photons_m3=sum(surv),
        He_origin_to_HI_m3=abs_m[1,0],
        source_recombination_binding_release_J_m3=source_binding,
        pre_recombination_selected_e_kinetic_J_m3=source_prekin,
        surviving_photon_energy_J_m3=survivor_energy,
        target_ionization_threshold_energy_J_m3=target_binding,
        primary_photoelectron_energy_J_m3=target_kin,
        net_atomic_binding_energy_released_J_m3=source_binding-target_binding,
        net_selected_electron_kinetic_change_J_m3=target_kin-source_prekin,
        He_to_H_primary_electron_kinetic_boost_J_m3=next(x['net_kinetic_transfer_from_binding_J_m3'] for x in ch if x['source']=='He' and x['target']=='HI'),
        total_photon_energy_conservation_residual_J_m3=residual)
    if abs(total['net_atomic_binding_energy_released_J_m3']-total['net_selected_electron_kinetic_change_J_m3']-survivor_energy)>tol:
        raise AssertionError('MATTER_RADIATION_ENERGY_LEDGER')
    return total,ch


def spectral_energy(prep,edges,params,T=1e10):
    records=[]
    for p in prep:
        E=p['energy'];k=p['k'];f=p['frac'];W=p['weights'];origin=p['source'];idx=np.searchsorted(ENERGY_BINS,E,side='right')-1
        I_s=float(params['HI' if origin=='H' else 'HeI'][0])
        for j in range(4):
            left,right=(float(z) for z in edges[j:j+2]);w=W[j]
            for t,ta in enumerate(TARGETS):
                I_a=float(params[ta][0])
                lo=w*f[t]*branch_prob(k,T-right)
                hi=w*f[t]*branch_prob(k,T-left)
                for g in range(len(ENERGY_BINS)-1):
                    m=idx==g;emin=float(ENERGY_BINS[g]);emax=float(ENERGY_BINS[g+1]);
                    rec=dict(source=origin,target=ta,birth_bin=j,source_time_start_s=left,source_time_end_s=right,
                    photon_energy_bin_lo_eV=emin,photon_energy_bin_hi_eV=emax,
                    first_absorbed_ions_lo_m3=fs(lo[m]),first_absorbed_ions_hi_m3=fs(hi[m]),
                    input_electron_kinetic_lo_J_m3=fs(lo[m]*(E[m]-I_s))*EV_J,
                    input_electron_kinetic_hi_J_m3=fs(hi[m]*(E[m]-I_s))*EV_J,
                    primary_electron_kinetic_lo_J_m3=fs(lo[m]*np.maximum(E[m]-I_a,0))*EV_J,
                    primary_electron_kinetic_hi_J_m3=fs(hi[m]*np.maximum(E[m]-I_a,0))*EV_J,
                    binding_energy_cross_transfer_lo_J_m3=fs(lo[m])*(I_s-I_a)*EV_J,
                    binding_energy_cross_transfer_hi_J_m3=fs(hi[m])*(I_s-I_a)*EV_J)
                    records.append(rec)
    return records


def save_csv(path,rows):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def run(src:Path=SOURCE,out:Path=ROOT/'results'):
    edges,prep,params,dens,prev=load_source(src)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    epochs=[];channels=[]
    for T in TIMES:
        for policy in POLICIES:
            e,c=epoch_ledger(prep,edges,params,float(T),policy)
            epochs.append(e);channels.extend(c)
    full=spectral_energy(prep,edges,params)
    at_final={r['policy']:r for r in epochs if r['time_s']==TIMES[-1]}
    last=at_final['latest'];early=at_final['earliest']
    if not math.isclose(last['He_origin_to_HI_m3'],prev['cross_He_to_H_abs_lower_m3'],rel_tol=2e-14):raise AssertionError('PARENT_HE_HI_LOW')
    if not math.isclose(early['He_origin_to_HI_m3'],prev['cross_He_to_H_abs_upper_m3'],rel_tol=2e-14):raise AssertionError('PARENT_HE_HI_HIGH')
    source_energy=early['source_recombination_binding_release_J_m3']+early['pre_recombination_selected_e_kinetic_J_m3']
    if not math.isclose(source_energy,7.591430348411315e-43,rel_tol=3e-14):raise AssertionError('PARENT_ORIGINAL_SOURCE_ENERGY')
    gain_lo=last['He_to_H_primary_electron_kinetic_boost_J_m3'];gain_hi=early['He_to_H_primary_electron_kinetic_boost_J_m3']
    if not gain_hi>gain_lo>0:raise AssertionError('CROSS_ENERGY_POSITIVITY')
    res=dict(unit='CR_PHYS07_RR_CHEMICAL_ENERGY_TRANSFER_V1',source_parent_pr=131,source_parent_head='c61857bd99dcc69d1224c8da4432569084f657ea',source_sha256=SOURCE_SHA256,
      original_gas_100K_frozen_neutral_m3=dens,original_ionization_threshold_eV={'H':params['HI'][0],'He':params['HeI'][0]},
      time_grid_s=[float(x) for x in TIMES],time_history_rows=len(epochs),channel_time_rows=len(channels),final_energy_spectral_rows=len(full),
      total_original_RR_photons_m3=prev['total_RR_m3'],total_born_photon_energy_J_m3=source_energy,
      cross_He_to_H_m3_bounds=[last['He_origin_to_HI_m3'],early['He_origin_to_HI_m3']],
      cross_He_to_H_binding_energy_to_primary_electron_J_m3_bounds=[gain_lo,gain_hi],
      cross_He_to_H_primary_electron_boost_eV_per_absorption= float(params['HeI'][0]-params['HI'][0]),
      final_global_witnesses={name:r for name,r in at_final.items()},
      note_potential='I_H and I_He are atomic ionization binding energies, not thermodynamic chemical potentials',scientific_limit='fixed neutral first-absorption conditional event energy transfer; no real plasma heating, coupled chemical evolution or expanding radiation transport',
      central_dag={'completed':28,'total':88,'delta':0},extension_dag={'completed':0,'total':3,'delta':0},
      new_auxiliary={'completed':1,'total':1,'admission':'SCOPED_REVIEW_HOLD'},different_author_R6='NOT_RUN',different_author_C9='NOT_RUN',native_subagent='NOT_RUN_TOOL_UNAVAILABLE',native25=False,L4=False,production=False,auto_next_node=False)
    save_csv(out/'TIME_ENERGY_LEDGER.csv',epochs)
    save_csv(out/'CHANNEL_ENERGY_TRANSFER.csv',channels)
    save_csv(out/'FINAL_BIN_TRANSFER.csv',full)
    (out/'RESULT.json').write_text(json.dumps(res,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return res

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source-zip',type=Path,default=SOURCE);a.add_argument('--out',type=Path,default=ROOT/'results');args=a.parse_args()
    print(json.dumps(run(args.source_zip,args.out),indent=2))
