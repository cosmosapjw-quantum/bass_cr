#!/usr/bin/env python3
"""BASS-CR PHYS11: exact source-locked energy-eligible secondary H-ionization capacity.

No electron-impact cross section or secondary event-rate, no actual secondary
collisions, no gas heating and no chemistry/radiation IVP is inferred.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import sys
import tempfile
import zipfile
from pathlib import Path
import numpy as np

ORIGINAL_PARENT_SHA256 = 'faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033'
PARENT_COMMIT = '284e904bc5d46360c53d718abc78ec1303b447b8'
PR134_SOURCE_SHA256 = 'e77bb3b9f7a91f608841b39e0b9679703c7d1f4d50f929c7fb7f030dac175243'
SOURCE_ROOT = 'research/cr_phys10_energy_causal_20261030/'
EV_J = 1.602176634e-19
TARGETS = ('HI','HeI')
TIMES = np.arange(9,dtype=float)*1.25e9
BIRTH_POLICIES = ('earliest','midpoint','latest')
WINDOWS = list(zip(TIMES[:-1],TIMES[1:]))
BINS = list(zip(np.arange(13.0,36.0,1.0),np.arange(14.0,37.0,1.0)))
HE_II_IONIZATION_NIST_eV = 54.4177655282


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fsum(a):
    return math.fsum(float(x) for x in np.asarray(a).ravel())


def load_source(original_parent_zip:Path):
    parent_bytes=Path(original_parent_zip).read_bytes()
    if sha(parent_bytes)!=ORIGINAL_PARENT_SHA256:
        raise ValueError('PHYS10_ORIGINAL_FULL_SOURCE_SHA256_MISMATCH')
    with zipfile.ZipFile(original_parent_zip) as z:
        if z.testzip():
            raise ValueError('PHYS10_ZIP_CRC_ERROR')
        manifest=json.loads(z.read(SOURCE_ROOT+'SOURCE_MANIFEST.json'))
        items=manifest['members']
        if len(items)!=43:
            raise ValueError('PHYS10_MANIFEST_COUNT_DRIFT')
        for item in items:
            raw=z.read(SOURCE_ROOT+item['path'])
            if sha(raw)!=item['sha256'] or len(raw)!=item['size']:
                raise ValueError('PHYS10_SOURCE_MANIFEST_MISMATCH:'+item['path'])
        parent_code=z.read(SOURCE_ROOT+'phys10_energy.py')
        inner_zip=z.read(SOURCE_ROOT+'sources/PR134_ORIGINAL_SOURCE.zip')
    if sha(inner_zip)!=PR134_SOURCE_SHA256:
        raise ValueError('PHYS09_SOURCE_IDENTITY_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='phys11_immutable_') as td:
        parent_path=Path(td)/'phys10_energy.py'
        source_path=Path(td)/'PR134_ORIGINAL_SOURCE.zip'
        parent_path.write_bytes(parent_code)
        source_path.write_bytes(inner_zip)
        spec=importlib.util.spec_from_file_location('phys10_frozen_owner_for_phys11',parent_path)
        parent=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=parent
        spec.loader.exec_module(parent)
        mod,edges,prep,params,dens=parent.load_owner(source_path)
    return mod,edges,prep,params,dens


def physical_capabilities(E:np.ndarray, Ia:float, IH:float, IHe:float):
    """Necessary kinematic conditions on *initial* photoelectron only.

    Integer inequalities are exact for these threshold parameters and source
    energy grid. The positive capability is NOT a probability of secondary impact.
    """
    eps=np.maximum(np.asarray(E,dtype=float)-Ia,0.)
    eligible_H = eps >= IH
    eligible_He = eps >= IHe
    eligible_two_H = eps >= (2*IH)
    return eps,eligible_H,eligible_He,eligible_two_H


def aggregate(weights,epsilon,eligible_H, I_H):
    """Return first counts and conditional capacity moments (not realized impacts)."""
    weighted=np.asarray(weights,dtype=float)
    cap=weighted*eligible_H
    n=fsum(weighted)
    c=fsum(cap)
    Q=fsum(weighted*epsilon)
    Ckin=fsum(cap*epsilon)
    Cleft=fsum(cap*np.maximum(epsilon-I_H,0.))
    return n,c,Q,Ckin,Cleft


def write_csv(path,rows):
    with open(path,'w',encoding='utf-8',newline='') as f:
        d=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        d.writeheader(); d.writerows(rows)


def generate(original_parent_zip:Path, output_dir:Path):
    mod,edges,prep,params,dens=load_source(original_parent_zip)
    output_dir.mkdir(parents=True,exist_ok=True)
    ih=float(params['HI'][0]); ihe=float(params['HeI'][0])
    base=[]
    eligible_atom_count=0
    for pp in prep:
        e=np.asarray(pp['energy'],dtype=float)
        for a,target in enumerate(TARGETS):
            Ia=float(params[target][0]); eps,cap,he,two=physical_capabilities(e,Ia,ih,ihe)
            eligible_atom_count+=int(cap.sum())
            for i,v in enumerate(e):
                base.append(dict(source=pp['source'],original_energy_index=i,photon_E_eV=float(v),first_absorber=target,
                    k_first_absorb_s_inv=float(pp['k'][i]*pp['frac'][a][i]),
                    source_total_birth_weight_m3=fsum([w[i] for w in pp['weights']]),
                    primary_electron_eV=float(eps[i]),
                    H_secondary_kinematically_eligible=int(cap[i]),
                    He_secondary_kinematically_eligible=int(he[i]),
                    two_additional_H_kinematically_eligible=int(two[i]),
                    direct_He_double_photon_eligible=int(v >= ihe+HE_II_IONIZATION_NIST_eV)))
    supports={ (pp['source'],a):physical_capabilities(pp['energy'],params[TARGETS[a]][0],ih,ihe)
               for pp in prep for a in (0,1)}
    time_channels=[]; time_total=[]; causal=[]; spectra=[]
    max_energy_bound=0.
    max_cap_overflow=0.
    largest_photon=max(float(np.max(pp['energy'])) for pp in prep)
    for T in TIMES:
        T=float(T)
        for policy in BIRTH_POLICIES:
            total_n=[];total_cap=[]; total_Q=[];total_cap_kin=[];total_cap_left=[]
            for pp in prep:
                src=pp['source']; E=np.asarray(pp['energy']);kH=pp['k']*pp['frac'][0];kHe=pp['k']*pp['frac'][1]
                for a in range(2):
                    eps,cap,he,two=supports[(src,a)]
                    count=[[],[],[],[],[]]
                    for j in range(4):
                        s=mod.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                        pv=mod.first_probability(kH,kHe,T-s,a)
                        inp=np.asarray(pp['weights'][j])*pv
                        out=aggregate(inp,eps,cap,ih)
                        for q,v in zip(count,out):q.append(v)
                        for b in range(2):
                            for wi,(lo,hi) in enumerate(WINDOWS):
                                gp=mod.log_response(kH,kHe,s,T,float(lo),float(hi),a,b)
                                scalar=fsum(np.asarray(pp['weights'][j])*cap*gp)
                                # Each j contribution is added below per original photon birth bin.
                                causal.append(dict(observation_s=T,birth_policy=policy,source=src,
                                    first_absorber=TARGETS[a],neutral_parameter=TARGETS[b],
                                    window_index=wi,window_start_s=float(lo),window_end_s=float(hi),
                                    birth_bin_index=j,d_H_capacity_dln_neutral_m3=scalar,
                                    d_secondary_binding_capacity_J_m3=scalar*ih*EV_J))
                    v=tuple(math.fsum(c) for c in count)
                    n,c,q,ck,cl=v
                    max_cap_overflow=max(max_cap_overflow,max(0,c-n))
                    time_channels.append(dict(observation_s=T,birth_policy=policy,source=src,first_absorber=TARGETS[a],
                        n_first_m3=n,H_secondary_upper_events_m3=c,eligible_first_fraction=c/n if n else '',
                        primary_kinetic_J_m3=q*EV_J,
                        eligible_primary_kinetic_J_m3=ck*EV_J,
                        H_secondary_max_binding_J_m3=c*ih*EV_J,
                        leftover_if_every_eligible_H_secondary_J_m3=cl*EV_J,
                        two_H_secondary_upper_m3=0.0, He_secondary_upper_m3=0.0))
                    for arr,x in [(total_n,n),(total_cap,c),(total_Q,q),(total_cap_kin,ck),(total_cap_left,cl)]:arr.append(x)
            n,c,q,ck,cl=map(math.fsum,[total_n,total_cap,total_Q,total_cap_kin,total_cap_left])
            time_total.append(dict(observation_s=T,birth_policy=policy,
                total_first_m3=n,H_secondary_upper_events_m3=c,
                H_capacity_over_first_fraction=c/n if n else '',
                initial_primary_kinetic_J_m3=q*EV_J,
                eligible_primary_energy_J_m3=ck*EV_J,
                H_secondary_binding_capacity_J_m3=c*ih*EV_J,
                residual_eligible_electron_kinetic_if_H_secondary_J_m3=cl*EV_J,
                He_secondary_upper_m3=0.0,two_H_secondary_upper_m3=0.0,
                direct_He_double_photon_upper_m3=0.0))
    # Aggregate per original source and observable; keep explicit original birth policy.
    # Causal rows above have birth_bin_index and 4× the PHYS09 grid; sum per j for canonical 1,728 rows.
    grouped={}
    for item in causal:
        key=(item['observation_s'],item['birth_policy'],item['source'],item['first_absorber'],item['neutral_parameter'],item['window_index'])
        if key not in grouped:
            grouped[key] = dict(item)
            grouped[key].pop('birth_bin_index')
            grouped[key]['d_H_capacity_dln_neutral_m3']=0.0
            grouped[key]['d_secondary_binding_capacity_J_m3']=0.0
        grouped[key]['d_H_capacity_dln_neutral_m3']+=item['d_H_capacity_dln_neutral_m3']
        grouped[key]['d_secondary_binding_capacity_J_m3']+=item['d_secondary_binding_capacity_J_m3']
    causal_out=list(grouped.values())
    for pp in prep:
        src=pp['source'];E=pp['energy'];kH=pp['k']*pp['frac'][0];kHe=pp['k']*pp['frac'][1]
        for policy in ('earliest','latest'):
            for a in range(2):
                eps,cap,he,two=supports[(src,a)]
                for lo,hi in BINS:
                    accum=[[],[],[],[],[]]
                    mask=(E>=lo)&(E<hi)
                    for j in range(4):
                        birth=mod.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                        p=mod.first_probability(kH,kHe,float(TIMES[-1])-birth,a)
                        w=np.asarray(pp['weights'][j])*p*mask
                        values=aggregate(w,eps,cap,ih)
                        for l,x in zip(accum,values):l.append(x)
                    n,c,q,ck,cl=(math.fsum(x) for x in accum)
                    spectra.append(dict(source=src,birth_policy=policy,first_absorber=TARGETS[a],E_lo_eV=float(lo),E_hi_eV=float(hi),
                        first_absorption_m3=n,additional_H_secondary_capacity_m3=c,
                        max_secondary_binding_J_m3=c*ih*EV_J,
                        eligible_initial_kinetic_J_m3=ck*EV_J))
    sizes=dict(atom_support=len(base),time_channels=len(time_channels),time_total=len(time_total),causal=len(causal_out),spectra=len(spectra))
    expected=dict(atom_support=12800,time_channels=108,time_total=27,causal=1728,spectra=184)
    if sizes!=expected:raise AssertionError(('ROW_DRIFT',sizes,expected))
    if not (largest_photon<ihe+HE_II_IONIZATION_NIST_eV and
            max(float(np.max(pp['energy']))-ih for pp in prep)<ihe):
        raise AssertionError('HELUM_SECONDARY_SUPPORT_OPEN_UNEXPECTEDLY')
    if not all(x['He_secondary_kinematically_eligible']==0 and x['two_additional_H_kinematically_eligible']==0 and x['direct_He_double_photon_eligible']==0 for x in base):
        raise AssertionError('INVALID_FORBIDDEN_CHANNEL')
    # Positive H secondary only from a He-origin photon first absorbed by H I.
    for x in time_channels:
        if (x['source'],x['first_absorber'])!=('He','HI') and x['H_secondary_upper_events_m3']!=0:
            raise AssertionError('FORBIDDEN_ORIGIN_SECONDARY')
    for name,rows in [('SUPPORT_PER_SOURCE_ATOM.csv',base),('TIME_CHANNEL_CAPACITY.csv',time_channels),
                      ('TIME_TOTAL_CAPACITY.csv',time_total),('CAUSAL_H_SECONDARY_CAPACITY.csv',causal_out),
                      ('FINAL_CAPACITY_ENERGY_BINS.csv',spectra)]:
        write_csv(output_dir/name,rows)
    results = {
      'unit':'CR_PHYS11_SOURCE_LOCKED_SECONDARY_ELIGIBILITY','parent_commit':PARENT_COMMIT,
      'original_source_sha256':ORIGINAL_PARENT_SHA256,'source_atoms':6400,
      'source_H_Emax_eV':max(float(np.max(pp['energy'])) for pp in prep if pp['source']=='H'),
      'source_He_Emax_eV':max(float(np.max(pp['energy'])) for pp in prep if pp['source']=='He'),
      'HI_threshold_source_eV':ih,'HeI_threshold_source_eV':ihe,
      'HeII_threshold_NIST_eV':HE_II_IONIZATION_NIST_eV,
      'He_double_photon_threshold_NIST_plus_original_eV':ihe+HE_II_IONIZATION_NIST_eV,
      'max_initial_electron_kinetic_eV':max(float(np.max(pp['energy']))-ih for pp in prep),
      'atom_energy_absorber_rows':12800,
      'eligible_He_origin_HI_energy_atoms':int(np.sum([np.count_nonzero(pp['energy']>=2*ih) for pp in prep if pp['source']=='He'])),
      'rows':sizes,'total_rows':sum(sizes.values()),
      'final_earliest':next(x for x in time_total if x['observation_s']==float(TIMES[-1]) and x['birth_policy']=='earliest'),
      'final_midpoint':next(x for x in time_total if x['observation_s']==float(TIMES[-1]) and x['birth_policy']=='midpoint'),
      'final_latest':next(x for x in time_total if x['observation_s']==float(TIMES[-1]) and x['birth_policy']=='latest'),
      'proof':{'H_additional_max_per_primary':1,'He_additional_max_per_primary':0,'single_photon_He_direct_double_max':0,
               'H_secondary_positive_capability_event_origin':'He_RR_photon_first_absorbed_by_HI',
               'capability_is_not_actual_event_count':True},
      'physical_K':'UNBOUND_PHYSICAL_EVENT_RATE_AND_STOPPING',
      'He_exclusive_global':'UNBOUND_OUTSIDE_THIS_SOURCE_ENERGY_SUPPORT',
      'central_DAG':'28/88 DELTA0','extension_DAG':'0/3 DELTA0',
      'scoped_auxiliary':'PHYS11 1/1 (source-kinematic cap; HOLD)',
      'R06_distinct_author':'NOT_RUN','C09_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN',
      'production':'HOLD','merge':False}
    (output_dir/'RESULT.json').write_text(json.dumps(results,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:results[k] for k in ['unit','total_rows','rows','final_earliest','final_midpoint','final_latest']},indent=2))
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--parent-zip',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    generate(a.parent_zip,a.out)
