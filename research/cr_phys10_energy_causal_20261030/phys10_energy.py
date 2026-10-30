#!/usr/bin/env python3
"""BASS-CR PHYS10: original-source first-photoelectron energy and neutral response.

Conditional photon-born first absorption at 100K frozen H I/He I. No heating,
secondary electrons, ionization IVP, redshift, path geometry or electron-impact K.
Requires byte-identical PHYS09 full SOURCE ZIP, not an incomplete PR133 checkout.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, sys, tempfile, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
PR134_SOURCE_SHA256='e77bb3b9f7a91f608841b39e0b9679703c7d1f4d50f929c7fb7f030dac175243'
PHYS09_HEAD='9a79c8b618fae288aee3a6bebdb2b8a5afba9c67'
EV_J=1.602176634e-19
TIMES=np.arange(9,dtype=float)*1.25e9
WINDOWS=list(zip(TIMES[:-1],TIMES[1:]))
BIRTH_POLICIES=('earliest','midpoint','latest')
TARGETS=('HI','HeI')
ENERGY_BINS=np.arange(13.,37.,1.)

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def fsum(a)->float:return math.fsum(float(x) for x in np.asarray(a).ravel())

def load_owner(source_zip:Path):
    raw=Path(source_zip).read_bytes()
    if sha(raw)!=PR134_SOURCE_SHA256:raise ValueError('PR134_ORIGINAL_SOURCE_SHA256_MISMATCH')
    with zipfile.ZipFile(source_zip) as z:
        if z.testzip():raise ValueError('PR134_ORIGINAL_SOURCE_CRC_FAIL')
        mf=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
        if len(mf)!=41:raise ValueError('PR134_SOURCE_MANIFEST_COUNT_MISMATCH')
        for f in mf:
            d=z.read(f['path'])
            if sha(d)!=f['sha256'] or len(d)!=f['size']:raise ValueError('PR134_SOURCE_MEMBER_MISMATCH:'+f['path'])
        prefix='research/cr_phys09_chemistry_neutral_response_20261030/'
        code=z.read(prefix+'neutral_response.py')
        parent=z.read(prefix+'sources/PR133_ORIGINAL_SOURCE.zip')
    # The original PHYS09 code owns ALL photon source and opacity definitions.
    with tempfile.TemporaryDirectory(prefix='cr_phys10_immutable_') as d:
        d=Path(d)
        (d/'neutral_response.py').write_bytes(code)
        (d/'PR133_ORIGINAL_SOURCE.zip').write_bytes(parent)
        spec=importlib.util.spec_from_file_location('cr_phys09_immutable',d/'neutral_response.py')
        mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
        edges,prep,params,dens,prev=mod.original_source(d/'PR133_ORIGINAL_SOURCE.zip')
        if sum(len(pp['energy']) for pp in prep)!=6400:raise AssertionError('SOURCE_ATOM_DRIFT')
        return mod,np.array(edges),prep,params,dens

def _birth(sourced,bin_index,policy,edges,mod):
    return mod.bin_birth(float(edges[bin_index]),float(edges[bin_index+1]),policy)

def target_energy(pp,target,params):
    E=np.asarray(pp['energy']);eps=np.maximum(0.,E-float(params[TARGETS[target]][0]))
    return eps

def per_source(prep,params,edges,mod,observation,policy,source,absorber,parameter=None,window=None,energy_range=None):
    """Return (count[m^-3], initial electron energy[eV m^-3],
    binding energy[eV m^-3], photon energy[eV m^-3]).
    When window/parameter present return corresponding density-log linear responses.
    """
    totals=[[],[],[],[]]
    for pp in prep:
        if source is not None and pp['source']!=source:continue
        E=np.asarray(pp['energy']);eps=target_energy(pp,absorber,params)
        ka=np.asarray(pp['k'])*np.asarray(pp['frac'])[0]
        kb=np.asarray(pp['k'])*np.asarray(pp['frac'])[1]
        mask=(np.ones(E.shape,dtype=float) if energy_range is None else
              ((E>=energy_range[0])&(E<energy_range[1])).astype(float))
        for j in range(4):
            s=_birth(pp,j,policy,edges,mod)
            if window is None:
                p=mod.first_probability(ka,kb,observation-s,absorber)
            else:
                p=mod.log_response(ka,kb,s,observation,*window,absorber,parameter)
            weights=np.asarray(pp['weights'][j])*mask*p
            totals[0].append(fsum(weights))
            totals[1].append(fsum(weights*eps))
            totals[2].append(fsum(weights*float(params[TARGETS[absorber]][0])))
            totals[3].append(fsum(weights*E))
    return tuple(math.fsum(x) for x in totals)

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)

def generate(out:Path,source_zip:Path):
    mod,edges,prep,params,dens=load_owner(source_zip)
    out.mkdir(parents=True,exist_ok=True)
    atom_rows=[];window_rows=[];time_rows=[];bin_rows=[]
    max_ledger_abs=0.;max_response_abs=0.
    for T in TIMES:
        for policy in BIRTH_POLICIES:
            by_target=np.zeros((2,4)); gradients=np.zeros((2,2,4))
            for pp in prep:
                for a in range(2):
                    n,q,b,ph=per_source(prep,params,edges,mod,float(T),policy,pp['source'],a)
                    atom_rows.append(dict(observation_s=float(T),birth_policy=policy,source=pp['source'],absorber=TARGETS[a],
                        n_first_m3=n,primary_electron_energy_eV_m3=q,primary_electron_energy_J_m3=q*EV_J,
                        binding_energy_J_m3=b*EV_J,absorbed_photon_energy_J_m3=ph*EV_J,
                        mean_primary_electron_energy_eV=q/n if n>0 else '',
                        energy_conservation_residual_J_m3=(ph-q-b)*EV_J))
                    by_target[a]+=np.array((n,q,b,ph))
                    for par in range(2):
                        for iw,window in enumerate(WINDOWS):
                            ng,qg,bg,phg=per_source(prep,params,edges,mod,float(T),policy,pp['source'],a,par,window)
                            window_rows.append(dict(observation_s=float(T),birth_policy=policy,source=pp['source'],absorber=TARGETS[a],
                                neutral_parameter=TARGETS[par],window_index=iw,window_start_s=float(window[0]),window_end_s=float(window[1]),
                                d_n_first_dln_neutral_m3=ng,d_primary_electron_eV_m3=qg,
                                d_primary_electron_J_m3=qg*EV_J,d_binding_J_m3=bg*EV_J,d_photon_J_m3=phg*EV_J))
                            gradients[a,par]+=np.array((ng,qg,bg,phg))
                            max_response_abs=max(max_response_abs,abs(phg-qg-bg)*EV_J)
                    max_ledger_abs=max(max_ledger_abs,abs(ph-q-b)*EV_J)
            rec=dict(observation_s=float(T),birth_policy=policy)
            for a in range(2):
                n,q,b,ph=by_target[a]; mu=q/n if n>0 else None
                rec.update({f'first_{TARGETS[a]}_m3':n,
                    f'primary_{TARGETS[a]}_J_m3':q*EV_J,
                    f'mean_primary_{TARGETS[a]}_eV':mu if mu is not None else '',
                    f'binding_{TARGETS[a]}_J_m3':b*EV_J,
                    f'absorbed_photon_{TARGETS[a]}_J_m3':ph*EV_J})
                for par in range(2):
                    gn,gq,gb,gph=gradients[a,par]
                    rec.update({f'grad_number_{TARGETS[a]}_ln_{TARGETS[par]}_m3':gn,
                        f'grad_primary_{TARGETS[a]}_ln_{TARGETS[par]}_J_m3':gq*EV_J,
                        f'grad_mean_{TARGETS[a]}_ln_{TARGETS[par]}_eV':(gq-mu*gn)/n if mu is not None else ''})
            rec.update(total_primary_J_m3=fsum(by_target[:,1])*EV_J,
                total_binding_J_m3=fsum(by_target[:,2])*EV_J,total_absorbed_photon_J_m3=fsum(by_target[:,3])*EV_J)
            time_rows.append(rec)
    Tf=float(TIMES[-1])
    for pp in prep:
        for policy in ('earliest','latest'):
            for a in range(2):
                for par in range(2):
                    for elo,ehi in zip(ENERGY_BINS[:-1],ENERGY_BINS[1:]):
                        n,q,b,ph=per_source(prep,params,edges,mod,Tf,policy,pp['source'],a,par,(0.,Tf),(float(elo),float(ehi)))
                        bin_rows.append(dict(source=pp['source'],birth_policy=policy,absorber=TARGETS[a],neutral_parameter=TARGETS[par],energy_lo_eV=float(elo),energy_hi_eV=float(ehi),
                            d_number_m3=n,d_primary_electron_J_m3=q*EV_J,d_binding_J_m3=b*EV_J,d_absorbed_photon_J_m3=ph*EV_J))
    if (len(atom_rows),len(window_rows),len(time_rows),len(bin_rows))!=(108,1728,27,368):
        raise AssertionError('ROW_COUNTS_DRIFT')
    for name,rows in [('TIME_CHANNEL_ENERGY.csv',atom_rows),('CAUSAL_ELECTRON_ENERGY.csv',window_rows),('TIME_ENERGY_LEDGER.csv',time_rows),('FINAL_ENERGY_RESPONSE.csv',bin_rows)]:write_csv(out/name,rows)
    earliest=next(x for x in time_rows if x['observation_s']==Tf and x['birth_policy']=='earliest')
    latest=next(x for x in time_rows if x['observation_s']==Tf and x['birth_policy']=='latest')
    result=dict(unit='CR_PHYS10_CAUSAL_PRIMARY_ELECTRON_ENERGY',parent_pr=134,parent_head=PHYS09_HEAD,
        source_original_sha256=PR134_SOURCE_SHA256,source_atoms=6400,temperature_K=100,
        original_neutrals_m3=dens,rows={"time_channels":108,"causal_energy":1728,"time_energy":27,"final_bins":368},
        total_rows=2231,pointwise_ledger_max_abs_J_m3=max_ledger_abs,pointwise_response_ledger_max_abs_J_m3=max_response_abs,
        final_earliest=earliest,final_latest=latest,
        eV_to_J=EV_J,physics='Source-owned first photoionization initial electron kinetic energy and causal response to frozen-base neutral opacity, not energy deposition',
        central={'done':28,'total':88,'delta':0},extension={'done':0,'total':3,'delta':0},scoped_auxiliary={'done':1,'total':1,'review':'HOLD'},
        independent_author_R06='NOT_RUN',independent_author_C09='NOT_RUN',
        physical_K='UNBOUND',exclusive_He_double_event='UNBOUND',shared_evolving_neutral='UNBOUND',shared_radiation_owner='UNBOUND',
        native25='HOLD',L4='HOLD',production='HOLD',merge_ready=False,auto_next=False)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'unit':result['unit'],'rows':result['rows'], 'final_earliest':{
        k:v for k,v in earliest.items() if k.startswith(('total_','mean_primary_'))},
        'final_latest':{k:v for k,v in latest.items() if k.startswith(('total_','mean_primary_'))},
        'max_energy_residual_J_m3':max_ledger_abs,'max_response_residual_J_m3':max_response_abs},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-zip',type=Path,default=ROOT/'sources/PR134_ORIGINAL_SOURCE.zip')
    parser.add_argument('--out',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    generate(args.out,args.source_zip)
