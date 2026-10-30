#!/usr/bin/env python3
"""Source-locked H(1s)->2p vs H ionization first-inelastic competition.

The parent PHYS13 full-source archive is immutable and includes user-provided
Shah1987 measured H impact cross sections, original 6400 BASS-CR H/He RR photons
and source birth bins. NEW NIST data are BE-scaled model, not experimental rates.
This is a restricted two-channel, uniform frozen-gas, no-stopping conditional model.
NOT an actual cosmological K, full stopping law, or Ly-alpha escaped background.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PARENT_SHA='fdae18068eb51ae7bdd0785efa371229aa15d33b6f040e0640e0bd65cc66d3a7'
PARENT_HEAD='9647b3e6a27ec5711c2ba4bfc33acf57a97f1f27'
NIST_CSV_SHA='bb5d4b1a883bd71575a139858d82b39cad43f70b8d6ee0260e06898b2173468a'
EV_J=1.602176634e-19
E_LYA=10.1988 # eV, NIST current H 1s->2p database; Stone2002 paper lists 10.204eV, distinguish
ME=9.1093837139e-31
NIST_SIGMA_UNIT=1e-20 # 10^-16 cm² = 10^-20 m²
TIMES=np.arange(9,dtype=float)*1.25e9
POLICIES=('earliest','midpoint','latest')
TARGETS=('HI','HeI')
_GL_X,_GL_W=np.polynomial.legendre.leggauss(24)
_GL_Q=0.5*(_GL_X+1.)
_GL_WEIGHT=0.5*_GL_W
ENERGY_BINS=list(zip(np.arange(13.,36.,1.),np.arange(14.,37.,1.)))

def sha(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()
def fs(arr) -> float: return math.fsum(float(a) for a in np.asarray(arr).ravel())

def load_parent(source_zip: Path):
    raw=source_zip.read_bytes()
    if sha(raw)!=PARENT_SHA: raise ValueError('PR138_PARENT_SHA_MISMATCH')
    with zipfile.ZipFile(source_zip) as z:
        if z.testzip():raise ValueError('PR138_PARENT_CRC_BAD')
        mf=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
        if len(mf)!=46:raise ValueError('PR138_MANIFEST_COUNT_BAD')
        pref='research/cr_phys13_shah1987_experiment_20261030/'
        for e in mf:
            data=z.read(pref+e['path'])
            if len(data)!=e['size'] or sha(data)!=e['sha256']:raise ValueError('PR138_MEMBER_IDENTITY:'+e['path'])
        code=z.read(pref+'phys13_shah.py')
        src=z.read(pref+'sources/PR137_ORIGINAL_SOURCE.zip')
        measured=z.read(pref+'data_shah1987.csv')
        result=json.loads(z.read(pref+'results/RESULT.json'))
    with tempfile.TemporaryDirectory(prefix='phys14_owner_') as tmp:
        d=Path(tmp)
        (d/'phys13_shah.py').write_bytes(code)
        (d/'PR137_ORIGINAL_SOURCE.zip').write_bytes(src)
        (d/'data_shah1987.csv').write_bytes(measured)
        spec=importlib.util.spec_from_file_location('cr_phys13_locked',d/'phys13_shah.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        p12,owner=module.load_original(d/'PR137_ORIGINAL_SOURCE.zip')
        shah=module.load_shah(d/'data_shah1987.csv')
    _,edges,prep,params,dens=owner
    if sum(len(pp['energy']) for pp in prep)!=6400:raise AssertionError('PARENT_SOURCE_ATOM_DRIFT')
    return module,owner,shah,result

def load_nist(path:Path):
    raw=path.read_bytes()
    if sha(raw)!=NIST_CSV_SHA:raise ValueError('NIST_SOURCE_TRANSCRIPTION_SHA_MISMATCH')
    with path.open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    E=np.array([float(x['incident_electron_eV']) for x in rows])
    be=np.array([float(x['BE_scaled_1e_minus16_cm2']) for x in rows])
    if not (len(rows)==12 and E[0]==11 and E[-1]==21 and np.all(np.diff(E)>0) and np.all(be>0)):
        raise ValueError('NIST_CROSS_SECTION_GRID_BAD')
    return rows,E,be

def second_first_event(kh,k,ni,nx,dt):
    """Convolution over first H photoabsorption and one subsequent 2-channel event.

    Returned pair is (P_H_secondary_ion,P_H_1s2p_excitation) on same original ray.
    ni,nx in s^-1; if either is unavailable it MUST be set to 0 only for an
    explicitly isolated, labelled channel scenario, never as a physical zero.
    """
    kh=np.asarray(kh,float);k=np.asarray(k,float);ni=np.asarray(ni,float);nx=np.asarray(nx,float)
    if dt<=0:return np.zeros_like(kh),np.zeros_like(kh)
    nu=ni+nx
    u=dt*_GL_Q[:,None]
    re=dt-u
    anyprob=dt*np.einsum('i,ij->j',_GL_WEIGHT,kh[None,:]*np.exp(-k[None,:]*u)*(-np.expm1(-nu[None,:]*re)))
    return np.divide(anyprob*ni,nu,out=np.zeros_like(nu),where=nu>0),np.divide(anyprob*nx,nu,out=np.zeros_like(nu),where=nu>0)

def velocity(ee):return np.sqrt(2*EV_J*np.maximum(np.asarray(ee,float),0.)/ME)
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def generate(source_zip:Path,nist_csv:Path,out:Path):
    p13,orig,shah,parent_result=load_parent(source_zip)
    _,edges,prep,params,dens=orig
    _,Esh,Ssh,Err=shah
    nist,En,BE=load_nist(nist_csv)
    nH=float(dens['HI']); I_H=float(params['HI'][0]);out.mkdir(parents=True,exist_ok=True)
    if not(abs(nH-138.6)<1e-8 and abs(I_H-13.60)<1e-8):raise AssertionError('FROZEN_BASE_DRIFT')
    micro=[]; info=[]; classes={n:0 for n in ['uncovered_below11','excitation_only_below_ion_threshold','ionization_gap_unmeasured','measured_overlap','outside_H_source']}
    for pp in prep:
        E=np.asarray(pp['energy'],float);ee=E-I_H
        kh=np.asarray(pp['k'])*np.asarray(pp['frac'])[0];khe=np.asarray(pp['k'])*np.asarray(pp['frac'])[1]
        nistcovered=(ee>=En[0])&(ee<=En[-1])
        sigma_2p=np.where(nistcovered,np.interp(ee,En,BE)*NIST_SIGMA_UNIT,0.)
        shcovered=(ee>=Esh[0])&(ee<=Esh[-1])
        sigma_ion=np.where(shcovered,np.interp(ee,Esh,Ssh)*p13.SIGMA_UNIT,0.)
        v=velocity(ee);nx=nH*v*sigma_2p;ni=nH*v*sigma_ion
        low=nistcovered & (ee<I_H)
        gap=nistcovered & (ee>=I_H) & (~shcovered)
        overlap=nistcovered & shcovered
        double_2p=ee>=2*E_LYA
        info.append(dict(pp=pp,ee=ee,E=E,kh=kh,k=kh+khe,nx=nx,ni=ni,v=v,
                         nistcovered=nistcovered,shcovered=shcovered,low=low,gap=gap,overlap=overlap,db=double_2p))
        for i in range(len(ee)):
            cls='measured_overlap' if overlap[i] else 'excitation_only_below_ion_threshold' if low[i] else 'ionization_gap_unmeasured' if gap[i] else 'uncovered_below11' if ee[i]<11 else 'outside_H_source'
            classes[cls]+=1
            micro.append(dict(source=pp['source'],source_atom_index=i,photon_energy_eV=float(E[i]),
                first_H_photoelectron_eV=float(ee[i]),source_H_absorber_hazard_per_s=float(kh[i]),
                NIST_2p_table_covered=int(nistcovered[i]),Shah_H_impact_measured=int(shcovered[i]),channel_class=cls,
                second_2p_energetically_possible=int(double_2p[i]),
                sigma_NIST_BE_2p_m2=float(sigma_2p[i]) if nistcovered[i] else '',
                sigma_Shah_ion_m2=float(sigma_ion[i]) if shcovered[i] else '',
                v_e_m_s=float(v[i]),nu_exc_per_s=float(nx[i]) if nistcovered[i] else '',
                nu_ion_per_s=float(ni[i]) if shcovered[i] else '',
                excitation_over_ion_hazard=float(nx[i]/ni[i]) if overlap[i] and ni[i]>0 else ''))
    write_csv(out/'SOURCE_ATOM_NIST_SHAH_CROSSWALK.csv',micro)
    time_rows=[];chan_rows=[];bins=[]
    def calc_case(info,T,policy):
        pp=info['pp'];first=np.zeros(len(info['ee']))
        ion=np.zeros(len(first));exc=np.zeros(len(first));iononly=np.zeros(len(first))
        sub=np.zeros(len(first));gapub=np.zeros(len(first));exc_only=np.zeros(len(first))
        for j in range(4):
            birth=orig[0].bin_birth(float(edges[j]),float(edges[j+1]),policy)
            dt=float(T-birth)
            w=np.asarray(pp['weights'][j],float)
            first+=w*orig[0].first_probability(info['kh'],info['k']-info['kh'],dt,0)
            a,b=second_first_event(info['kh'],info['k'],info['ni'],info['nx'],dt)
            _,b0=second_first_event(info['kh'],info['k'],np.zeros_like(info['ni']),info['nx'],dt)
            c,_=second_first_event(info['kh'],info['k'],info['ni'],np.zeros_like(info['nx']),dt)
            ion+=w*a*info['overlap'];exc+=w*b*info['overlap'];iononly+=w*c*info['overlap']
            exc_only+=w*b0*info['nistcovered']
            sub+=w*b0*info['low'];gapub+=w*b0*info['gap']
        return dict(first=first,ion=ion,exc=exc,iononly=iononly,sub=sub,gapub=gapub,exc_only=exc_only)
    for T in TIMES:
        for policy in POLICIES:
            sums=dict.fromkeys(['first','ion','exc','iononly','sub','gapub','exc_only','binding','lyalpha','ionresid','excresid'],0.)
            for x in info:
                y=calc_case(x,T,policy);ee=x['ee']
                m={k:fs(v) for k,v in y.items()}
                m.update(binding=fs(y['ion']*I_H)*EV_J,lyalpha=fs(y['exc']*E_LYA)*EV_J,
                         ionresid=fs(y['ion']*(ee-I_H))*EV_J,
                         excresid=fs(y['exc']*(ee-E_LYA))*EV_J)
                for k in sums:sums[k]+=m[k]
                chan_rows.append(dict(observation_s=float(T),birth_policy=policy,source=x['pp']['source'],
                    first_H_photoabsorption_m3=m['first'],
                    Shah_ion_with_NIST_2p_competition_m3=m['ion'],
                    NIST_2p_excitation_with_Shah_ion_competition_m3=m['exc'],
                    Shah_ion_no_excitation_m3=m['iononly'],
                    NIST_2p_only_model_all_covered_m3=m['exc_only'],
                    NIST_2p_only_model_ion_forbidden_m3=m['sub'],
                    NIST_2p_only_model_unmeasured_ion_gap_UPPER_m3=m['gapub'],
                    H_binding_from_secondary_ion_J_m3=m['binding'],
                    potential_Lyalpha_2p_energy_J_m3=m['lyalpha']))
            if not sums['ion']<=sums['iononly']*(1+1e-12)+1e-70: raise ValueError('ION_SINK_COMPETITION_MONOTONICITY_FAIL')
            time_rows.append(dict(observation_s=float(T),birth_policy=policy,
                first_H_photoabsorption_m3=sums['first'],
                H_ion_first_inelastic_measured_overlap_m3=sums['ion'],
                H_2p_first_inelastic_measured_overlap_m3=sums['exc'],
                H_ion_no_exc_measured_overlap_m3=sums['iononly'],
                H_ion_suppression_due_to_2p_m3=sums['iononly']-sums['ion'],
                H_ion_suppression_relative=(1-sums['ion']/sums['iononly']) if sums['iononly'] else '',
                H_2p_only_nist_all_m3=sums['exc_only'],
                H_2p_only_ion_forbidden_m3=sums['sub'],
                H_2p_only_unknown_ion_13_6_to_14_6_upper_m3=sums['gapub'],
                Lya_2p_first_event_candidate_energy_J_m3=sums['lyalpha'],
                secondary_H_binding_energy_J_m3=sums['binding'],
                ionization_postcollision_electron_kinetic_J_m3=sums['ionresid'],
                two_p_excitation_postcollision_electron_kinetic_J_m3=sums['excresid']))
    write_csv(out/'TIME_CHANNEL_COMPETITION.csv',chan_rows)
    write_csv(out/'TIME_TOTAL_COMPETITION.csv',time_rows)
    T=float(TIMES[-1])
    for x in info:
        for policy in ('earliest','latest'):
            y=calc_case(x,T,policy)
            for lo,hi in ENERGY_BINS:
                mask=(x['E']>=lo)&(x['E']<hi)
                bins.append(dict(source=x['pp']['source'],policy=policy,photon_E_lo_eV=float(lo),photon_E_hi_eV=float(hi),
                        H_first_absorptions_m3=fs(y['first'][mask]),
                        H_ion_competition_m3=fs(y['ion'][mask]),
                        H_2p_competition_m3=fs(y['exc'][mask]),
                        H_2p_subthreshold_m3=fs(y['sub'][mask]),
                        H_2p_unknown_ion_gap_upper_m3=fs(y['gapub'][mask])))
    write_csv(out/'FINAL_SOURCE_ENERGY_BIN_COMPETITION.csv',bins)
    nist_out=[];ccc=[]
    for row in nist:
        e=float(row['incident_electron_eV']);v=float(row['BE_scaled_1e_minus16_cm2']);cc=row['CCC_1e_minus16_cm2']
        nist_out.append(dict(Ee_eV=e,sigma_BE_scaled_2p_m2=v*NIST_SIGMA_UNIT,sigma_CCC_2p_m2=float(cc)*NIST_SIGMA_UNIT if cc else '',source='NIST_ElectronImpact_H1s_to_2p'))
        if cc:ccc.append(dict(Ee_eV=e,sigma_BE_m2=v*NIST_SIGMA_UNIT,sigma_CCC_m2=float(cc)*NIST_SIGMA_UNIT,BE_div_CCC=v/float(cc),method_not_uncertainty=True))
    write_csv(out/'NIST_2P_REFERENCE.csv',nist_out)
    write_csv(out/'NIST_BE_VS_CCC_CROSSCHECK.csv',ccc)
    support=[dict(classification=k,source_atom_count=v) for k,v in classes.items()]
    support.append(dict(classification='double_2p_energetically_eligible',source_atom_count=sum(int(x['db'].sum()) for x in info)))
    write_csv(out/'SUPPORT_CENSUS.csv',support)
    count=dict(micro=6400,by_source=len(chan_rows),time_total=len(time_rows),energy_spectrum=len(bins),nist_reference=len(nist_out),ccc_comparison=len(ccc),support_census=len(support))
    if count != dict(micro=6400,by_source=54,time_total=27,energy_spectrum=92,nist_reference=12,ccc_comparison=4,support_census=6):raise ValueError('ROWS_MISMATCH:'+str(count))
    first=next(x for x in time_rows if x['observation_s']==T and x['birth_policy']=='earliest')
    last=next(x for x in time_rows if x['observation_s']==T and x['birth_policy']=='latest')
    result=dict(unit='CR_PHYS14_NIST_H_1S2P_COMPETING_INELASTIC_FIRST_EVENT',parent_PR=138,
        parent_HEAD=PARENT_HEAD,parent_source_sha256=PARENT_SHA, source_atoms=6400,
        target='H(1s)',source_NIST='https://physics.nist.gov/cgi-bin/Ionization/excit_data.php?final=2p&id=HI&initial=1s&ision=E',
        source_Shah='user-provided original Table1 inherited from frozen PHYS13',
        nist_method='Stone2002 BE-scaled Born, 12 published sample points; NOT experimental',
        sigma_units='m^2',natural_constants={'EV_J':EV_J,'m_e_kg':ME},
        excitation_threshold_eV=E_LYA,h_first_ion_threshold_eV=I_H,
        max_primary_e_eV=max(float(x['ee'].max()) for x in info),
        physical_scope='uniform frozen gas, source-born photon first absorption, then two-channel first-inelastic e-H(1s) ion vs 2p excitation; no microscopic electron trajectory, elastic/2s/3p/scattering cascade/temperature, no escaped Lyalpha photon',
        results=first,final_latest=last,counts=count,total_rows=sum(count.values()),source_census=classes,
        double_2p_energy_atoms=sum(int(x['db'].sum()) for x in info),
        central_DAG='28/88 DELTA0',extension_DAG='0/3 DELTA0',scoped_auxiliary='1/1 CONDITIONAL_REVIEW_HOLD',
        physical_K='UNBOUND',electron_stopping='UNBOUND',He_exclusive='UNBOUND',
        common_evolving_gas_rad_clock_geometry='UNBOUND',L4='HOLD',native25='HOLD',production='HOLD',
        distinct_author_R06='NOT_RUN',distinct_author_C09='NOT_RUN',native_subagent='NOT_RUN',no_merge=True,auto_next=False)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'count':count,'total_rows':sum(count.values()),'maxE':result['max_primary_e_eV'],'double2p':result['double_2p_energy_atoms'],'earliest':first,'latest':last},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'sources/PR138_ORIGINAL_SOURCE.zip');p.add_argument('--nist',type=Path,default=ROOT/'nist_h_2p_cross_sections.csv');p.add_argument('--out',type=Path,default=ROOT/'results');x=p.parse_args();generate(x.source,x.nist,x.out)
