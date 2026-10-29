#!/usr/bin/env python3
"""Physical source-locked time-window first ionizations of original PR129 H/He RR photons.

All event envelopes are sharp *pointwise by window* under independent within-source-bin
birth times, not a common global emission history or actual evolving ionization ODE.
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import tempfile
from pathlib import Path
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'sources/PR129_ORIGINAL_SOURCE.zip'
SHA129 = '09b9c10bc50a3f00b6bba334e23565e867324f2112ee7906a543b3d2899bd64b'
SHA128 = 'a6062e5fa54c51983439e256ffd521f7b25d151952293e0fad7c2b3064ff4819'
PARENT = 'research/cr_phys04_rr_spectral_survival_20261030/'
EV_J = 1.602176634e-19
C = 299792458.0
SOURCES = ('H','He')
TARGETS = ('HI','HeI')
ENERGY_EDGES = np.arange(13.,37.,1.,dtype=float)
TIMES = np.arange(9, dtype=float)*1.25e9


def digest(b): return hashlib.sha256(b).hexdigest()
def summed(a): return math.fsum(np.ravel(np.asarray(a, dtype=np.float64)))


def load_sources(path=SOURCE):
    b=Path(path).read_bytes()
    if digest(b)!=SHA129: raise ValueError('LOCK_PR129_SHA256_FAIL')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError('LOCK_PR129_ZIP_CRC_FAIL')
        entries=json.loads(z.read('SOURCE_MANIFEST.json'))['payloads']
        if len(entries)!=40:raise ValueError('LOCK_PR129_MANIFEST_COUNT')
        for item in entries:
            raw=z.read(item['path'])
            if digest(raw)!=item['sha256'] or len(raw)!=item['size']:
                raise ValueError('LOCK_PR129_MANIFEST_MEMBER_FAIL:'+item['path'])
        old=z.read(PARENT+'sources/PR128_ORIGINAL_SOURCE.zip')
        code=z.read(PARENT+'spectral_survival.py')
        reference=json.loads(z.read(PARENT+'results/RESULT.json'))
    if digest(old)!=SHA128:raise ValueError('LOCK_PR128_NESTED_FAIL')
    with tempfile.TemporaryDirectory(prefix='cr_phys05_pr129_') as td:
        td=Path(td)
        (td/'spectral_survival.py').write_bytes(code)
        (td/'pr128.zip').write_bytes(old)
        sp=importlib.util.spec_from_file_location('source_locked_pr129',td/'spectral_survival.py')
        mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
        arrays,density,params,sigma,parent_total,parent_csv=mod.source_load(td/'pr128.zip')
    return arrays,density,params,sigma,reference


def event_kernel(s,k,t0,t1):
    """First-absorption probability in [t0,t1], without target branching factor."""
    s=np.asarray(s,dtype=float); k=np.asarray(k,dtype=float)
    if not (np.isfinite(t0) and np.isfinite(t1) and t1>t0):
        raise ValueError('INVALID_WINDOW')
    if np.any(k<0) or np.any(~np.isfinite(k)) or np.any(~np.isfinite(s)):
        raise ValueError('INVALID_K_OR_BIRTH')
    return np.where(s>t1,0.,np.where(s>t0,
             -np.expm1(-k*np.maximum(t1-s,0.)),
             np.exp(-k*np.maximum(t0-s,0.))*(-np.expm1(-k*(t1-t0)))))


def time_window_extrema(k,l,r,t0,t1):
    """Peak is birth at t0 clipped to birth range; lower is one of its endpoints."""
    if not (0<=l<=r): raise ValueError('INVALID_BIRTH_INTERVAL')
    s_peak=min(r,max(l,t0))
    vhi=event_kernel(s_peak,k,t0,t1)
    pl=event_kernel(l,k,t0,t1)
    pr=event_kernel(r,k,t0,t1)
    s_low=np.where(pl<=pr,l,r)
    vlo=np.minimum(pl,pr)
    if np.any(vhi+1e-14<vlo):raise AssertionError('PROBABILITY_EXTREMA_ORDER_FAIL')
    return vlo,vhi,s_low,s_peak


def numeric_rows(arrays,density,params,sigma,reference,times=TIMES):
    times=np.asarray(times,dtype=float)
    if len(times)<2 or not np.all(np.isfinite(times)) or times[0]<0 or np.any(np.diff(times)<=0):
        raise ValueError('INVALID_EPOCH_GRID')
    birth=np.asarray(arrays['time_edges_s'],dtype=float)
    if not np.array_equal(birth,[0.,2.5e9,5e9,7.5e9,1e10]):raise ValueError('INVALID_LOCKED_BIRTH_GRID')
    if times[-1]!=birth[-1]:raise ValueError('FINAL_TIME_MUST_MATCH_PARENT')
    source_photons=sum(summed(arrays[f'capture_{c}_bins_m3']) for c in SOURCES)
    if not np.isclose(source_photons,reference['source_photons_m3'],rtol=5e-15):
        raise ValueError('SOURCE_PHOTON_INVENTORY_DIFF')
    rows=[]; totals=[];witness=[]
    witness_policies=('earliest','latest','midpoint')
    witness_acc={policy:np.zeros((len(times)-1,2)) for policy in witness_policies}
    gamma_precomp=[]
    for src in SOURCES:
        E=np.asarray(arrays[f'photon_{src}_eV'],dtype=float)
        W=np.asarray(arrays[f'capture_{src}_bins_m3'],dtype=float)
        if W.shape!=(4,len(E)) or np.any(W<0) or np.any(E<ENERGY_EDGES[0]) or np.any(E>=ENERGY_EDGES[-1]):
            raise ValueError('SOURCE_SHAPE_WEIGHT_OR_GRID_BAD')
        a=np.stack([np.asarray(sigma[src][target],dtype=float)*density[target] for target in TARGETS])
        alpha=a.sum(axis=0);k=C*alpha
        if np.any(alpha<=0) or np.any(~np.isfinite(alpha)):
            raise ValueError('LOCKED_SOURCE_TOTAL_OPACITY')
        frac=a/alpha
        bins=np.searchsorted(ENERGY_EDGES,E,side='right')-1
        gamma_precomp.append((src,E,W,k,frac,bins))
    for t0,t1 in zip(times[:-1],times[1:]):
        dt=float(t1-t0)
        ion=np.zeros((2,2))
        photon_en=np.zeros((2,2));kin_en=np.zeros((2,2))
        for src,E,W,k,frac,bins in gamma_precomp:
            by_target=np.zeros((2,2,len(E)))
            for j in range(4):
                l,r=map(float,birth[j:j+2])
                vl,vh,sl,sh=time_window_extrema(k,l,r,float(t0),float(t1))
                for target_idx in range(2):
                    by_target[target_idx,0]+=W[j]*frac[target_idx]*vl
                    by_target[target_idx,1]+=W[j]*frac[target_idx]*vh
                for policy in witness_policies:
                    s= {'earliest':l,'latest':r,'midpoint':(l+r)/2}[policy]
                    p=event_kernel(s,k,float(t0),float(t1))
                    for target_idx in range(2):
                        witness_acc[policy][np.where(times[:-1]==t0)[0][0],target_idx]+=summed(W[j]*frac[target_idx]*p)
            for idx,ta in enumerate(TARGETS):
                I=float(params[ta][0]); kinetic=np.maximum(E-I,0)*EV_J
                for b in range(len(ENERGY_EDGES)-1):
                    mask=bins==b
                    nlo=summed(by_target[idx,0,mask]);nhi=summed(by_target[idx,1,mask])
                    elo=summed(by_target[idx,0,mask]*E[mask])*EV_J
                    ehi=summed(by_target[idx,1,mask]*E[mask])*EV_J
                    klo=summed(by_target[idx,0,mask]*kinetic[mask])
                    khi=summed(by_target[idx,1,mask]*kinetic[mask])
                    if klo<-1e-80 or khi<-1e-80:raise AssertionError('NEGATIVE_ELECTRON_EXCESS')
                    rows.append({'window_start_s':float(t0),'window_end_s':float(t1),
                      'source_photon':src,'target':ta,'energy_bin_lo_eV':float(ENERGY_EDGES[b]),
                      'energy_bin_hi_eV':float(ENERGY_EDGES[b+1]),'ions_lo_m3':nlo,'ions_hi_m3':nhi,
                      'electron_lo_m3':nlo,'electron_hi_m3':nhi,
                      'photon_energy_lo_J_m3':elo,'photon_energy_hi_J_m3':ehi,
                      'ionization_threshold_lo_J_m3':nlo*I*EV_J,
                      'ionization_threshold_hi_J_m3':nhi*I*EV_J,
                      'primary_electron_kinetic_lo_J_m3':klo,
                      'primary_electron_kinetic_hi_J_m3':khi,
                      'event_rate_lo_m3_s':nlo/dt,'event_rate_hi_m3_s':nhi/dt})
                ion[idx]+=np.array([summed(by_target[idx,0]),summed(by_target[idx,1])])
                photon_en[idx]+=np.array([summed(by_target[idx,0]*E)*EV_J,summed(by_target[idx,1]*E)*EV_J])
                kin_en[idx]+=np.array([summed(by_target[idx,0]*kinetic),summed(by_target[idx,1]*kinetic)])
        assert np.all(ion>=-1e-90)
        totals.append({'window_start_s':float(t0),'window_end_s':float(t1),'duration_s':dt,
           'HII_birth_lo_m3':ion[0,0],'HII_birth_hi_m3':ion[0,1],
           'HeII_birth_lo_m3':ion[1,0],'HeII_birth_hi_m3':ion[1,1],
           'electron_birth_lo_m3':ion[:,0].sum(),'electron_birth_hi_m3':ion[:,1].sum(),
           'electron_source_rate_lo_m3_s':ion[:,0].sum()/dt,'electron_source_rate_hi_m3_s':ion[:,1].sum()/dt,
           'primary_photoelectron_energy_lo_J_m3':kin_en[:,0].sum(),
           'primary_photoelectron_energy_hi_J_m3':kin_en[:,1].sum(),
           'photoabsorbed_energy_lo_J_m3':photon_en[:,0].sum(),
           'photoabsorbed_energy_hi_J_m3':photon_en[:,1].sum(),
           'charge_residual_lo_m3':ion[:,0].sum()-(ion[0,0]+ion[1,0]),
           'charge_residual_hi_m3':ion[:,1].sum()-(ion[0,1]+ion[1,1])})
    # Each joint birth-time witness generates a consistent interval history and endpoint.
    for policy in witness_policies:
        for j,(t0,t1) in enumerate(zip(times[:-1],times[1:])):
            ni=witness_acc[policy][j]
            witness.append({'policy':policy,'window_start_s':float(t0),'window_end_s':float(t1),
                            'ion_HII_m3':ni[0],'ion_HeII_m3':ni[1],'electron_m3':ni.sum(),
                            'charge_residual_m3':ni.sum()-(ni[0]+ni[1])})
    final=reference['final']
    assert np.isclose(witness_acc['earliest'].sum(),final['absorbed_hi_m3'],rtol=6e-14,atol=1e-85), 'EARLIEST_PARENT_FINAL_MISMATCH'
    assert np.isclose(witness_acc['latest'].sum(),final['absorbed_lo_m3'],rtol=6e-14,atol=1e-85), 'LATEST_PARENT_FINAL_MISMATCH'
    assert np.isclose(witness_acc['earliest'][:,0].sum(),final['absorbed_HI_hi_m3'],rtol=6e-14,atol=1e-85)
    assert np.isclose(witness_acc['latest'][:,1].sum(),final['absorbed_HeI_lo_m3'],rtol=6e-14,atol=1e-85)
    feedback={}
    for ta in TARGETS:
        feedback['max_fractional_depletion_'+ta]=source_photons/density[ta]
    feedback['max_relative_total_opacity_loss_uniform']=source_photons/min(density.values())
    feedback['max_survival_probability_absolute_drift_uniform']=feedback['max_relative_total_opacity_loss_uniform']/(math.e*(1-feedback['max_relative_total_opacity_loss_uniform']))
    feedback['conditional_on']='closed-box photoionization-only, no other chemistry; not a coupled REI/BASS state or actual deposition'
    out={'schema':'CR_PHYS05_RR_WINDOW_IONIZATION_V1','source_sha256':SHA129,
       'parent_pr':129,'parent_head':'76fac9178442ae5dc02b270d741b3ee1dcfa79b2',
       'source_photons_m3':source_photons,'density_m3':density,
       'window_rows':len(totals),'spectrum_rows':len(rows),'joint_history_witness_rows':len(witness),
       'first_ionization_product':'H I -> H II + e- or He I -> He II + e- only',
       'first_event_window_bounds':'sharp for independent unconstrained birth times within original PR125 bins',
       'clock':'proper s','source': 'frozen 100 K H/He PR125 atomwise RR photons, PR127 Verner photoionization',
       'parent_final_absorption_m3':final['absorbed_hi_m3'],
       'earliest_witness_window_sum_m3':float(witness_acc['earliest'].sum()),
       'latest_witness_window_sum_m3':float(witness_acc['latest'].sum()),
       'window_integrated_extrema_not_common_global_history':True,
       'max_photo_only_density_feedback':feedback,
       'central_dag':{'completed':28,'total':88,'delta':0},
       'extension_dag':{'completed':0,'total':3,'delta':0},
       'new_auxiliary_dag':{'completed':1,'total':1,'review':'HOLD'},
       'independent_author_R06':'NOT_RUN','independent_author_C09':'NOT_RUN',
       'native25':False,'L4':False,'production':False,'auto_next_node':False,
       'limitations':['birth-time distribution unknown','no evolving neutral fractions','no physical K or exclusive He event kernel','no cosmic redshift or transfer','no plasma thermal deposition','per-window extrema cannot be summed to infer an attainable global history']}
    return out, rows, totals, witness


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def run(source=SOURCE,out=ROOT/'results'):
    arrays,density,params,sigma,reference=load_sources(source)
    meta, spectra, totals, witness=numeric_rows(arrays,density,params,sigma,reference)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'RESULT.json').write_text(json.dumps(meta,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    write_csv(out/'WINDOW_IONIZATION_SPECTRA.csv',spectra)
    write_csv(out/'WINDOW_IONIZATION_TOTALS.csv',totals)
    write_csv(out/'JOINT_HISTORY_WITNESSES.csv',witness)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-zip',type=Path,default=SOURCE)
    p.add_argument('--out',type=Path,default=ROOT/'results')
    a=p.parse_args();print(json.dumps(run(a.source_zip,a.out),indent=2))
