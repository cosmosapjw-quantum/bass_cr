#!/usr/bin/env python3
"""Source-locked conditional Ly-alpha 2p radiative emission and first resonant HI scatter.

Authority: immutable complete BASS-CR PHYS14 source archive (not Git-only checkout).
Physics: same 6400 RR photon atoms and 4 source birth bins; frozen uniform HI at 100 K;
first H photoabsorption followed by first modeled electron inelastic H 1s->2p
excitation competing with Shah H impact ionization on MEASURED overlap only;
then spontaneous 2p->1s E1 photon and, at externally specified frequency offset,
one first resonant scattering on HI. No source emission frequency distribution,
recoil, redistribution, multi-scattering, spatial boundary, chemistry IVP or K.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
from scipy.special import exprel,wofz

ROOT=Path(__file__).resolve().parent
PARENT_SHA='55c5b97d8bb59fa2f56fb0e07deef9bf43a328feb820cb8ea0bf6fabf2f8aefa'
PARENT_HEAD='ae9aacd7ce93c28008d4e23c587cb2878e9adb45'
EV_J=1.602176634e-19
C=299792458.0
H=6.62607015e-34
KB=1.380649e-23
ME=9.1093837139e-31
MH=1.6735575e-27
QE=1.602176634e-19
EPS0=8.8541878128e-12
TEMP_K=100.
A21=6.2649e8 # H I 2p->1s 2P_{1/2}, NIST; 2P_{3/2} is 6.2648e8 s^-1
F_LYA=0.41641 # NIST dipole oscillator strength
E_LYA=10.1988 # parent NIST 1s->2p model excitation energy eV; common source convention
H_DENSITY_M3=138.6
TIMES=np.arange(9,dtype=float)*1.25e9
POLICIES=('earliest','midpoint','latest')
X_OFFSETS=(-100.,-50.,-20.,-10.,-8.,-5.,-4.,-3.,-2.,-1.,0.,1.,2.,3.,4.,5.,8.,10.,20.,50.,100.)
BINS=list(zip(np.arange(13.,36.,1.),np.arange(14.,37.,1.)))
_GLX,_GLW=np.polynomial.legendre.leggauss(64)
GL_T=(_GLX+1)/2
GL_W=_GLW/2
_GL150_X,_GL150_W=np.polynomial.legendre.leggauss(160)
GL150_T=(_GL150_X+1)/2
GL150_W=_GL150_W/2
_LAG_N,_LAG_W=np.polynomial.laguerre.laggauss(64)

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fsum(a)->float:return math.fsum(float(x) for x in np.asarray(a).ravel())

def load_parent(archive:Path):
    raw=archive.read_bytes()
    if sha(raw)!=PARENT_SHA:raise ValueError('PHYS14_ORIGINAL_SOURCE_SHA256_MISMATCH')
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError('PHYS14_ZIP_CRC_FAIL')
        mm=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
        if len(mm)!=50:raise ValueError('PHYS14_MANIFEST_COUNT_MISMATCH')
        prefix='research/cr_phys14_nist_2p_20261030/'
        for x in mm:
            b=z.read(prefix+x['path'])
            if len(b)!=x['size'] or sha(b)!=x['sha256']:raise ValueError('PHYS14_MEMBER_IDENTITY:'+x['path'])
        code=z.read(prefix+'phys14_compete.py')
        base=z.read(prefix+'sources/PR138_ORIGINAL_SOURCE.zip')
        nist=z.read(prefix+'nist_h_2p_cross_sections.csv')
        time_rows=list(csv.DictReader(z.read(prefix+'results/TIME_TOTAL_COMPETITION.csv').decode('utf8').splitlines()))
    with tempfile.TemporaryDirectory(prefix='cr_phys15_owner_') as d:
        p=Path(d);(p/'phys14_compete.py').write_bytes(code);(p/'PR138_ORIGINAL_SOURCE.zip').write_bytes(base);(p/'nist.csv').write_bytes(nist)
        spec=importlib.util.spec_from_file_location('cr_phys14_original_owner',p/'phys14_compete.py')
        p14=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p14;spec.loader.exec_module(p14)
        _,orig,shah,_=p14.load_parent(p/'PR138_ORIGINAL_SOURCE.zip')
        _,En,BE=p14.load_nist(p/'nist.csv')
    _,edges,prep,params,dens=orig
    if sum(len(z['energy']) for z in prep)!=6400:raise ValueError('ORIGINAL_ATOMS_CHANGED')
    if abs(float(dens['HI'])-H_DENSITY_M3)>1e-9 or abs(params['HI'][0]-13.60)>1e-9:raise ValueError('ORIGINAL_NEUTRAL_CHANGED')
    return p14,orig,shah,En,BE,time_rows

def line_properties(temp_K=TEMP_K):
    nu0=E_LYA*EV_J/H
    vth=math.sqrt(2*KB*temp_K/MH)
    dnu=nu0*vth/C
    a=A21/(4*math.pi*dnu)
    sigma_pref=QE**2/(4*EPS0*ME*C)*F_LYA/(math.sqrt(math.pi)*dnu)
    return dict(nu0_Hz=nu0,vacuum_wavelength_m=C/nu0,doppler_width_Hz=dnu,v_th_m_s=vth,
                damping_a=a,sigma0_pref_m2=sigma_pref,A21_s=A21,lifetime_s=1/A21,
                Lyalpha_E_eV=E_LYA,lyalpha_E_J=E_LYA*EV_J,oscillator_strength=F_LYA)

LINE=line_properties()

def scatter_sigma(x:float)->float:
    return float(LINE['sigma0_pref_m2']*wofz(float(x)+1j*LINE['damping_a']).real)

def scatter_rate(x:float)->float:
    return H_DENSITY_M3*C*scatter_sigma(x)

def per_atom_excitation_density(kh,k,ni,nx,age):
    """Source-owned 2p excitation rate density per unit photon weight, s^-1.
    k=kh+kHe, nu=ni+nx, age after original source photon birth.
    Both collision channels are known only within measured-overlap classification.
    """
    age=np.asarray(age,float)
    return kh*nx*age*np.exp(-k*age)*exprel((k-(ni+nx))*age)

def integrate_case(info,T,policy,p14,orig,xlist=X_OFFSETS,with_atoms=False):
    """Causal first-2p event then prompt first Ly-alpha scattering response.
    The fast 2p lifetime is separately bounded, NOT numerically confused with
    near-instant response on 1e9 s source observation grid.
    """
    _,edges,_,_,_=orig
    q=np.array([scatter_rate(x) for x in xlist])
    agg=np.zeros(len(q));event_sum=0.;by_source={}
    excitation_per_atom=[];scatter_core_per_atom=[]
    # A continuous two-event source is integrated on exact physical birth subintervals.
    for p in info:
        pp=p['pp'];n=len(p['ee']);exc=np.zeros(n)
        for j in range(4):
            s=orig[0].bin_birth(float(edges[j]),float(edges[j+1]),policy)
            dt=float(T-s)
            if dt<=0:continue
            w=np.asarray(pp['weights'][j],float)
            ages=dt*GL_T
            ee_d=per_atom_excitation_density(p['kh'][None,:],p['k'][None,:],p['ni'][None,:],p['nx'][None,:],ages[:,None])
            ee_d*=w[None,:]
            integrated=dt*np.einsum('t,tn->n',GL_W,ee_d)
            exc+=integrated
            # Non-negative integration of the time-ordered three-step event.
            # The source is fixed, line frequency is a CONDITION, not an inferred
            # emission-frequency distribution.
            # When q*dt >> 1, a narrow causal boundary layer remains near
            # observation. Plain GL64 over [s,T] misses those unscattered photons.
            # Use positive 160-pt quadrature for q*dt <=200, and an independent
            # Laguerre quadrature of the non-scattered endpoint layer for q*dt >200.
            qdt=q*dt
            age160=dt*GL150_T
            rate160=per_atom_excitation_density(p['kh'][None,:],p['k'][None,:],p['ni'][None,:],p['nx'][None,:],age160[:,None])
            rate160*=w[None,:]
            summed160=np.sum(rate160,axis=1)
            for ix,qr in enumerate(q):
                if qdt[ix]<=200:
                    photon=dt*float(np.dot(GL150_W,summed160*(-np.expm1(-qr*(dt-age160)))))
                    if with_atoms and xlist[ix]==0.:
                        core=dt*np.einsum('t,tn,t->n',GL150_W,rate160,-np.expm1(-qr*(dt-age160)))
                else:
                    age=dt-_LAG_N/qr
                    keep=age>=0
                    rates=np.zeros((len(age),n))
                    if np.any(keep):
                        r=per_atom_excitation_density(p['kh'][None,:],p['k'][None,:],p['ni'][None,:],p['nx'][None,:],age[keep,None])
                        rates[keep]=r*w[None,:]
                    unsc=(1/qr)*np.einsum('t,tn->n',_LAG_W,rates)
                    scatter=integrated-unsc
                    if np.any(scatter<-1e-90):raise AssertionError('NEGATIVE_FIRST_SCATTER_LAGUERRE')
                    photon=fsum(np.maximum(scatter,0.))
                    if with_atoms and xlist[ix]==0.:core=np.maximum(scatter,0.)
                agg[ix]+=photon
                if with_atoms and xlist[ix]==0.:
                    if j==0:core_atom=np.zeros(n)
                    core_atom+=core
        event_sum+=fsum(exc)
        by_source[pp['source']]=by_source.get(pp['source'],0.)+fsum(exc)
        if with_atoms:
            excitation_per_atom.append((pp,exc,p,core_atom))
    return event_sum,agg,by_source,excitation_per_atom

def build_info(p14,orig,shah,En,BE):
    _,_,prep,params,dens=orig
    _,Esh,Ssh,_=shah
    out=[]
    for pp in prep:
        photon=np.asarray(pp['energy'],float)
        ee=photon-float(params['HI'][0])
        kh=np.asarray(pp['k'],float)*np.asarray(pp['frac'])[0]
        k=np.asarray(pp['k'],float)
        overlap=(ee>=En[0])&(ee<=En[-1])&(ee>=Esh[0])&(ee<=Esh[-1])
        v=p14.velocity(ee)
        nx=np.where(overlap,H_DENSITY_M3*v*np.interp(ee,En,BE)*p14.NIST_SIGMA_UNIT,0.)
        ni=np.where(overlap,H_DENSITY_M3*v*np.interp(ee,Esh,Ssh)*1e-21,0.)
        out.append(dict(pp=pp,E=photon,ee=ee,kh=kh,k=k,nx=nx,ni=ni,overlap=overlap))
    return out

def write_csv(path:Path,records:list[dict]):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)

def generate(parent_source:Path,output:Path):
    p14,orig,shah,En,BE,parent_rows=load_parent(parent_source)
    info=build_info(p14,orig,shah,En,BE);output.mkdir(parents=True,exist_ok=True)
    old={(float(r['observation_s']),r['birth_policy']):float(r['H_2p_first_inelastic_measured_overlap_m3']) for r in parent_rows}
    support_rows=[];time_rows=[];by_source_rows=[];freq_rows=[];bin_rows=[];line_rows=[];max_parity=0.
    for p in info:
        for j,E in enumerate(p['E']):
            support_rows.append(dict(source=p['pp']['source'],source_atom_index=j,photon_energy_eV=float(E),
                  primary_electron_energy_eV=float(p['ee'][j]),first_H_photoabsorber_rate_s=float(p['kh'][j]),
                  ionization_excitation_measured_overlap=int(p['overlap'][j]),
                  primary_2p_first_event_rate_s=float(p['nx'][j]),
                  primary_H_secondary_ion_first_event_rate_s=float(p['ni'][j]),
                  conditional_Lya_transition_energy_eV=E_LYA if p['overlap'][j] else '',
                  conditional_Lya_transition_A_s=A21 if p['overlap'][j] else '',
                  post_2p_excitation_primary_electron_eV=float(p['ee'][j]-E_LYA) if p['overlap'][j] else ''))
    for x in X_OFFSETS:
        sig=scatter_sigma(x);lam=1/(H_DENSITY_M3*sig);q=scatter_rate(x)
        line_rows.append(dict(x_Doppler=float(x),sigma_first_Lya_HI_scatter_m2=sig,
                first_scatter_rate_s=q,mean_first_scatter_time_s=1/q,mean_free_path_m=lam,
                time_horizon_optical_depth=q*float(TIMES[-1]),A_2p_to_1s_s=A21,energy_eV=E_LYA,
                mean_first_scatter_delay_upper_correction_fraction=q/(A21-q)))
    for T in TIMES:
        for policy in POLICIES:
            do_atom=(T==TIMES[-1] and policy in ('earliest','latest'))
            number,sc,by_source,atomlist=integrate_case(info,T,policy,p14,orig,with_atoms=do_atom)
            p_val=old[(float(T),policy)]
            rel=abs(number-p_val)/max(abs(number),abs(p_val),1e-95)
            max_parity=max(max_parity,rel)
            if rel>1e-9:raise AssertionError(f'PARENT_PHYS14_EXCITATION_PARITY_FAIL:{T},{policy},{rel}')
            core_idx=X_OFFSETS.index(0.);wing_idx=X_OFFSETS.index(10.);far_idx=X_OFFSETS.index(100.)
            core=sc[core_idx];wing=sc[wing_idx];far=sc[far_idx]
            if np.any(sc<-1e-70) or np.any(sc>number*(1+2e-10)+1e-65):raise AssertionError('SCATTER_PROBABILITY_BOUNDS')
            if not(0<=far<=wing<=core<=number*(1+1e-9)+1e-65):raise AssertionError('SCATTER_FREQUENCY_MONOTONE')
            # Provable upper on radiatively excited but not yet emitted H 2p number:
            # excite_rate(age) <= kh*nx*age, and ∫ exp(-A w) dw <= 1/A.
            pop_upper=0.
            for p in info:
                for j in range(4):
                    birth=orig[0].bin_birth(float(orig[1][j]),float(orig[1][j+1]),policy)
                    dt=max(0.,T-birth)
                    pop_upper+=fsum(np.asarray(p['pp']['weights'][j])*p['kh']*p['nx']*dt)/A21
            time_rows.append(dict(observation_s=float(T),birth_policy=policy,
                original_parent_H_2p_first_inelastic_m3=p_val,
                calculated_2p_excitations_m3=number,
                conditional_new_Lya_photons_upper_m3=number,
                conditional_unemitted_2p_upper_m3=pop_upper,
                conditional_emitted_Lya_lower_m3=max(0.,number-pop_upper),
                radiative_energy_reservoir_J_m3=number*EV_J*E_LYA,
                first_scatter_line_centre_prompt_m3=core,
                first_scatter_x10_prompt_m3=wing,
                first_scatter_x100_prompt_m3=far,
                escaped_Lya_photons='UNRESOLVED_NOT_MODELED',
                radiative_population_decay_lifetime_s=1/A21))
            for name,exc in sorted(by_source.items()):
                by_source_rows.append(dict(observation_s=float(T),birth_policy=policy,source=name,
                        H_2p_first_inelastic_m3=exc,conditional_Lya_energy_J_m3=exc*E_LYA*EV_J))
            for idx,x in enumerate(X_OFFSETS):
                q=scatter_rate(x);n=float(sc[idx]);loss=q/(A21-q)*number
                freq_rows.append(dict(observation_s=float(T),birth_policy=policy,x_Doppler=float(x),
                  N_Lya_initial_emission_upper_m3=number,
                  N_Lya_first_scatter_instant_decay_m3=n,
                  P_first_scatter_given_excitation=n/number if number>0 else '',
                  N_first_scatter_finite_A_lower_m3=max(0.,n-loss),
                  N_first_scatter_finite_A_upper_m3=n,
                  max_finite_A_delay_correction_m3=loss,
                  sigma_Lya_HI_m2=scatter_sigma(x),
                  H_density_m3=H_DENSITY_M3,proper_horizon_s=float(T),
                  photon_energy_J=E_LYA*EV_J,
                  first_scattered_photon_energy_J_m3=n*E_LYA*EV_J))
            if do_atom:
                for pp,ex,p,core_atom in atomlist:
                    for j,E in enumerate(p['E']):
                        if not p['overlap'][j] and (ex[j]!=0 or core_atom[j]!=0):raise AssertionError('UNSUPPORTED_SOURCE_NONZERO')
                        bin_rows.append(dict(source=pp['source'],birth_policy=policy,
                            source_atom_index=j,photon_energy_eV=float(E),
                            measured_domain_H_2p_excitation_m3=float(ex[j]),
                            potential_Lya_emitted_photons_upper_m3=float(ex[j]),
                            Lyalpha_first_resonant_scatter_x0_m3=float(core_atom[j]),
                            residual_primary_e_energy_eV=float(p['ee'][j]-E_LYA) if p['overlap'][j] else ''))
    write_csv(output/'SOURCE_2P_LYA_ATOMS.csv',support_rows)
    write_csv(output/'TIME_LYA_2P_RADIATION_LEDGER.csv',time_rows)
    write_csv(output/'TIME_SOURCE_LYA_LEDGER.csv',by_source_rows)
    write_csv(output/'FREQUENCY_FIRST_SCATTER_ATLAS.csv',freq_rows)
    write_csv(output/'FINAL_SOURCE_ATOM_LYA_SCATTER.csv',bin_rows)
    write_csv(output/'LINE_MICROPHYSICS.csv',line_rows)
    rows=dict(micro=len(support_rows),time=len(time_rows),by_source=len(by_source_rows),frequency=len(freq_rows),final_per_atom=len(bin_rows),line=len(line_rows))
    if rows!=dict(micro=6400,time=27,by_source=54,frequency=567,final_per_atom=12800,line=21):raise AssertionError('ROW_COUNT_INCONSISTENT'+str(rows))
    earliest=next(x for x in time_rows if x['observation_s']==float(TIMES[-1]) and x['birth_policy']=='earliest')
    latest=next(x for x in time_rows if x['observation_s']==float(TIMES[-1]) and x['birth_policy']=='latest')
    result=dict(unit='CR_PHYS15_LYA_SOURCE_AND_FIRST_RESONANT_SCATTER',parent_PR=139,parent_HEAD=PARENT_HEAD,
       parent_SHA256=PARENT_SHA,source_photon_atoms=6400,source_birth_bins=4,
       original_nHI_m3=H_DENSITY_M3,original_temperature_K=TEMP_K,
       line=LINE,original_energy_convention='PHYS14 E_LYA=10.1988eV',
       Lyalpha_time_lag='2p E1 decay A=6.2649e8 s^-1 finite lifetime bound; prompt approximation in first-scatter atlas',
       frequency='x=(nu-nu0)/delta_nu_D externally conditioned, NOT source-emission frequency PDF',
       radiation_scope='source-derived 2p excitations -> conditional spontaneous Lyalpha injection -> first HI resonance scatter only',
       excluded='source recoil spectrum, multiple scattering, redistribution, finite geometry escape, thermal/chemical feedback, electron stopping, 2s and other channels',
       rows=rows,total_rows=sum(rows.values()),earliest=earliest,latest=latest,source_parity_max_relative=max_parity,
       central_DAG='28/88 DELTA0',extension_DAG='0/3 DELTA0',auxiliary='1/1 CONDITIONAL_REVIEW_HOLD',
       physical_K='UNBOUND',global_He_exclusive='UNBOUND',common_evolving_gas_radiation_geometry='UNBOUND',
       source_qualified_first_Lya_scatter='CONDITIONAL_ONLY',native25='HOLD',L4='HOLD',production='HOLD',
       R06_distinct_author='NOT_RUN',C09_distinct_author='NOT_RUN',native_subagent='NOT_RUN',
       no_merge=True,no_force_push=True,auto_next=False)
    (output/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'rows':rows,'total_rows':sum(rows.values()),'parent_parity_relative_max':max_parity,
          'earliest':earliest,'latest':latest,'line':LINE},indent=2,ensure_ascii=False))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent-source',type=Path,default=ROOT/'sources/PR139_ORIGINAL_SOURCE.zip');p.add_argument('--out',type=Path,default=ROOT/'results');v=p.parse_args();generate(v.parent_source,v.out)
