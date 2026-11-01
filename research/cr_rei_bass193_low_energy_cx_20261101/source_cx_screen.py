#!/usr/bin/env python3
"""BASS-CR -> REI IGM: source-locked H+ + H(1s) resonant-CX event-rate screen.

Uses BASS193 source snapshots already archived by rei_bianchi PR311 and
published Titova et al. 2025 Appendix A4 total resonant-exchange fit to
Schultz et al. 2016 cross sections. No new REI IVP, no CR chemistry source,
no Bianchi drag without angular scattering and separate fluid velocity.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import quad

SOURCE_SHA256='4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52'
SOURCE_MEMBERS={
 'PR302_ARRIVAL_192.csv':'155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df',
 'PR302_THERMAL_192.csv':'292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6',
 'PR303_SPECIES_192.csv':'dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09',
 'PR_BASS193_ELECTRON_FEEDBACK_193.csv':'50a9a7a2728f08ac4534f0e92071cdd4fb3b7ddc9a3e9f8175458d398ad06b0f',
}
# Titova, Izmodenov & Korolkov (2025), PASA, Appendix A, eq. (A4):
# sigma_tot,cx(g)=(A-B ln[g/(cm/s)])^2. A and B have dimensions cm.
FIT_URL=('https://www.cambridge.org/core/journals/publications-of-the-astronomical-society-of-australia/'
         'article/effects-of-angular-scattering-and-hp-hh-collisions-on-the-properties-of-'
         'interstellar-atoms-in-the-heliosphere/295E867AC1038B5648D5780349B5E6E5')
FIT_A_CM=1.87618291e-7
FIT_B_CM=8.28949260e-9
MP_G=1.67262192595e-24
MH_G=1.6735575e-24
MU_G=MP_G*MH_G/(MP_G+MH_G)
KB_ERG_K=1.380649e-16
EV_ERG=1.602176634e-12
V_MIN_CM_S=3e5    # distinguishable-particle approach supported > ~3 km/s
V_MAX_CM_S=2e7   # 200 km/s; Maxwell tail beyond this is negligible for T<=12000 K
EXPECTED_ROWS=192


def sha256_bytes(b): return hashlib.sha256(b).hexdigest()

def file_sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def sigma_cx_cm2(v_cm_s):
    if not math.isfinite(v_cm_s) or v_cm_s<=0:raise ValueError('nonpositive relative speed')
    return (FIT_A_CM-FIT_B_CM*math.log(v_cm_s))**2


def thermal_speed_cm_s(T):
    if not math.isfinite(T) or T<=0:raise ValueError('nonpositive temperature')
    return math.sqrt(2*KB_ERG_K*T/MU_G)


def rate_fit_all_analytic(T):
    """Exact Maxwell integral for the *unbounded algebraic fit*, NOT source admission.

    Flux-weighted x^2=(v/vth)^2 has Gamma(shape=2, scale=1) law.
    Mean ln(x)=psi(2)/2; Var ln(x)=psi1(2)/4.
    """
    vth=thermal_speed_cm_s(T)
    psi2=1-np.euler_gamma
    tri2=math.pi**2/6-1
    centered=FIT_A_CM-FIT_B_CM*(math.log(vth)+0.5*psi2)
    return 2*vth/math.sqrt(math.pi)*(centered**2+0.25*FIT_B_CM**2*tri2)


def rate_quadrature(T, low=V_MIN_CM_S,high=V_MAX_CM_S):
    """Model contribution ONLY from named speed window; cm^3/s.

    epsabs is nondefault because the integral is ~1e-9 and default quad
    absolute tolerance (~1e-8) would incorrectly report a 'converged' result.
    """
    vth=thermal_speed_cm_s(T)
    if not(0<=low<high<=float('inf')):raise ValueError('bad speed bounds')
    lo,hi=low/vth,high/vth
    def fun(x):
        if x==0:return 0.0
        v=x*vth
        return (4/math.sqrt(math.pi))*x**3*math.exp(-x*x)*vth*sigma_cx_cm2(v)
    v,err=quad(fun,lo,hi,epsabs=1e-25,epsrel=2e-11,limit=200)
    if not math.isfinite(v) or v<0 or err>max(1e-19,1e-8*v):
        raise FloatingPointError('rate quadrature failed physical error target')
    return v


def source_rows(zip_path):
    zpath=Path(zip_path)
    if file_sha(zpath)!=SOURCE_SHA256:raise ValueError('SOURCE_ZIP_SHA_MISMATCH')
    with zipfile.ZipFile(zpath) as z:
        if z.testzip() is not None:raise ValueError('SOURCE_ZIP_CRC')
        files={}
        for name,digest in SOURCE_MEMBERS.items():
            b=z.read('inputs/'+name)
            if sha256_bytes(b)!=digest:raise ValueError('SOURCE_MEMBER_SHA_MISMATCH_'+name)
            files[name]=list(csv.DictReader(io.StringIO(b.decode('utf-8'))))
    if [len(files[k]) for k in SOURCE_MEMBERS] != [192,192,192,193]:
        raise ValueError('incorrect original row counts')
    return files


def compute(zip_path):
    inputs=source_rows(zip_path)
    arr=inputs['PR302_ARRIVAL_192.csv'];th=inputs['PR302_THERMAL_192.csv']
    chem=inputs['PR303_SPECIES_192.csv'];plasma=inputs['PR_BASS193_ELECTRON_FEEDBACK_193.csv']
    rows=[]
    for j,(a,t,c,p) in enumerate(zip(arr,th,chem,plasma[1:])):
        if any(int(x['arrival_interval'])!=j for x in (a,t)) or int(p['epoch'])!=j+1:
            raise ValueError('original source clock index mismatch')
        zh=float(a['z_high']);zl=float(a['z_low']);dt=float(t['proper_interval_s'])
        if not (zh>zl>0 and dt>0): raise ValueError('nonphysical source proper-time interval')
        if abs(zh-float(t['z_high']))>1e-11 or abs(zl-float(t['z_low']))>1e-11 or abs(zl-float(c['z_end']))>1e-11 or abs(zl-float(p['z']))>1e-11:
            raise ValueError('mixed source redshift clock')
        nH=float(p['nb_m3'])*1e-6*float(t['nHref_over_nb'])
        xHII=float(c['xHII_end']);T=float(t['T_BASS_saved_K'])
        if not(0<=xHII<=1 and nH>0 and 0<T<=12000.1):raise ValueError('nonphysical source state')
        k_valid=rate_quadrature(T)
        k_analytic=rate_fit_all_analytic(T)
        if not(0<=k_valid<=k_analytic*(1+2e-11)):
            raise ValueError('window rate larger than entire fit rate')
        frac=k_valid/k_analytic
        nHI=nH*(1-xHII);np_=nH*xHII
        event_rate_perH=nH*xHII*(1-xHII)*k_valid
        H_eff=math.log((1+zh)/(1+zl))/dt
        rows.append(dict(interval=j,z_high=zh,z_low=zl,proper_interval_s=dt,
            H_effective_per_s=H_eff,T_saved_K=T,nH_cm3=nH,x_HII_end=xHII,x_HI_end=1-xHII,
            nHII_cm3=np_,nHI_cm3=nHI,
            vth_relative_cm_s=thermal_speed_cm_s(T),Erel_vth_eV=KB_ERG_K*T/EV_ERG,
            sigma_at_vth_cm2=sigma_cx_cm2(thermal_speed_cm_s(T)),
            kcx_fit_window_cm3_s=k_valid,kcx_full_fit_extrapolated_cm3_s=k_analytic,
            fit_window_rate_fraction=frac,sub_3km_model_rate_fraction=1-frac,
            nu_neutral_s=np_*k_valid,nu_ion_s=nHI*k_valid,
            events_per_H_per_s_frozen_end=event_rate_perH,
            events_per_H_frozen_end_exposure=event_rate_perH*dt,
            nu_neutral_over_H_eff=np_*k_valid/H_eff,
            direct_H_ionization_source_s=0.0,direct_electron_source_s=0.0,
            direct_binding_energy_source_erg_per_H_s=0.0,
            supported_speed_floor_km_s=3.0,
            source_coverage='PARTIAL_LOW_SPEED_DOMINANT' if frac<0.5 else 'PARTIAL_LOW_SPEED_NONNEGLIGIBLE' if frac<0.95 else 'PARTIAL_SPEED_WINDOW_GE95PCT_MODEL'
        ))
    return rows


def summarize(rows):
    arr=lambda name:np.asarray([r[name] for r in rows],dtype=float)
    ind=int(np.argmax(arr('events_per_H_frozen_end_exposure')))
    by_cov={t:sum(r['source_coverage']==t for r in rows) for t in sorted(set(r['source_coverage'] for r in rows))}
    return {'schema':'BASS_CR_REI_BASS193_H_HPLUS_LOW_E_CX_RATE_SCREEN_V1',
      'units':'cgs and eV as column suffix','source_origin':'REI PR311 frozen BASS193 state',
      'source_zip_sha256':SOURCE_SHA256,'source_member_sha256':SOURCE_MEMBERS,
      'cross_section_author':'Titova Izmodenov Korolkov 2025 Eq A4, fit to Schultz et al 2016 quantum DCS/TCS',
      'cross_section_url':FIT_URL,'cross_section_range_note':'distinguishable charge transfer vs elastic separation more reliable g>3 km/s; numerical 3-200 km/s window is model convention',
      'reactants':'H+(proton) + H(1s) --> H(1s) + H+(proton), resonant identical isotope',
      'thermal_closure':'ion and neutral Maxwellian at same saved scalar T, zero common drift, relative reduced mass; not measured velocities or finite tilt',
      'direct_chemistry_ionization_electron_binding_sources':'EXACT_ZERO_FOR_RESONANT_LABEL_EXCHANGE',
      'momentum_drag':'NOT_COMPUTED_REQUIRES_ANGULAR_CROSS_SECTION_AND_SEPARATE_FLUID_F',
      'time_integrated_collision_count':'NOT_COMPUTED_FROZEN_ENDPOINT_EXPOSURE_ONLY',
      'validity':'source-conditioned low-energy rate capacity only, not native REI IVP, source-compatible Bianchi geometry or production',
      'rows':len(rows),'temperature_min_K':min(arr('T_saved_K')),'temperature_max_K':max(arr('T_saved_K')),
      'max_frozen_end_exposure':float(rows[ind]['events_per_H_frozen_end_exposure']),
      'max_frozen_end_exposure_interval':ind,'max_frozen_end_exposure_z':float(rows[ind]['z_low']),
      'max_nu_neutral_over_H_eff':float(np.max(arr('nu_neutral_over_H_eff'))),
      'number_window_rate_fraction_ge_0p95':int(np.sum(arr('fit_window_rate_fraction')>=.95)),
      'source_coverage_counts':by_cov,'sum_of_frozen_endpoint_exposures_NOT_integrated':float(np.sum(arr('events_per_H_frozen_end_exposure'))),
      'source_domain_limitation':'early cold T 100K has large extrapolated low-speed portion; do not promote full Maxwell fit as source-verified',
      'original_CR_R3M10_100keV_per_u':'NO_GO_NONTRANSFERABLE_TO_IGM_ELECTRONVOLT_REGIME',
      'central_DAG':'28/88_REPORTED','working_DAG':'33/88_REPORTED','bass_cr_extension_DAG':'0/3_REPORTED',
      'canonical_delta':0,'production':'HOLD','no_merge':True,'no_force_push':True,'auto_next_node':False}


def save(rows,outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    f=outdir/'BASS193_H_HPLUS_CX_SOURCE_CONDITIONAL_192.csv'
    with f.open('w',newline='',encoding='utf-8') as o:
        w=csv.DictWriter(o,fieldnames=list(rows[0]));w.writeheader()
        for row in rows:w.writerow({k:(format(float(v),'.17g') if type(v) is float else v) for k,v in row.items()})
    data=summarize(rows);data['science_csv_sha256']=file_sha(f)
    js=outdir/'RESULT.json';js.write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    return f,js


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    o=ap.parse_args();rows=compute(o.source);f,j=save(rows,o.out)
    print('CR_IGM_PHYSICAL_RESULT',json.dumps({'rows':len(rows),'csv_sha':file_sha(f),
          'max_exposure':max(r['events_per_H_frozen_end_exposure'] for r in rows),
          'coverage_counts':summarize(rows)['source_coverage_counts'],
          'central_DAG':'28/88_REPORTED','canonical_delta':0},sort_keys=True))
if __name__=='__main__':main()
