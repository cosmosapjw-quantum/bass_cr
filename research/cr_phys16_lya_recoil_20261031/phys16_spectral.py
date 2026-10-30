#!/usr/bin/env python3
"""Source-locked PHYS16 conditional Ly-alpha injection spectrum and one-scatter kernel.

NOT empirical differential electron cross sections, physical K, escaping flux or multi-scatter.
Birth and excitation rates owned by exact immutable PHYS15 (and nested PHYS14).
The added normalized plane-wave first Born angular closure is EXPLORATORY near threshold.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,io,json,math,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import quad,quad_vec
from scipy.special import wofz,ndtr

ROOT=Path(__file__).resolve().parent
PHYS15_SHA='48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316'
PHYS15_PREFIX='research/cr_phys15_lya_first_scatter_20261030/'
ME=9.1093837139e-31; MH=1.6735575e-27
EV=1.602176634e-19; H=6.62607015e-34; HBAR=H/(2*math.pi)
C=299792458.; KB=1.380649e-23; A0=5.29177210544e-11
E21=10.1988; T_K=100.; A21=6.2649e8
NU0=E21*EV/H; VTH=math.sqrt(2*KB*T_K/MH); DNU=NU0*VTH/C
A=A21/(4*math.pi*DNU); ETA_EM=H*NU0/(2*MH*C*VTH)
ETA_SC=2*ETA_EM
XGRID=np.linspace(-16.,16.,161)
M_N,M_W=32,12
MU,MW=np.polynomial.legendre.leggauss(M_N)
WU,WW=np.polynomial.legendre.leggauss(M_W)
# Emission E1 from first-Born 2p aligned along momentum transfer (q direction).
DIPOLE_W=WW*0.75*(1-WU**2)
ISO_W=WW*0.5
assert abs(sum(DIPOLE_W)-1)<1e-14


def sha(b): return hashlib.sha256(b).hexdigest()

def exact_recoil(e_ev, mu):
    """Stationary target H, electron e+H->e'+H(2p); exact nonrel 2-body kinematics."""
    pi=np.sqrt(2*ME*EV*e_ev)
    aa=1/ME+1/MH; bb=2*pi*np.asarray(mu)/MH
    cc=2*E21*EV+pi*pi/MH-pi*pi/ME
    discr=bb*bb-4*aa*cc
    if np.any(discr < 0):raise ValueError('INELASTIC_CLOSED')
    pf=(bb+np.sqrt(discr))/(2*aa)
    q2=np.maximum(0,pi*pi+pf*pf-2*pi*pf*np.asarray(mu))
    q=np.sqrt(q2)
    err=(e_ev-E21)*EV-pf*pf/(2*ME)-q2/(2*MH)
    return pf/pi, q/(MH*VTH), q2/(2*MH*EV), float(np.max(np.abs(err)/(e_ev*EV))),q*A0/HBAR


def born_angular(e_ev):
    """Model 1s->2p PWBA shape |F(q)|^2/q^4, normalized, not DCS data.
    Hydrogenic F squared = 72 z^2 / (z^2+9/4)^6, z=q a0 / hbar.
    """
    ratio,vrec,erec,err,z=exact_recoil(e_ev,MU)
    form2=72*z*z/(z*z+2.25)**6
    shape=ratio*form2/(z**4)
    weights=MW*shape
    weights=weights/np.sum(weights)
    return weights,vrec,erec,err


def emit_pdf(e_ev,x=XGRID,n_mu=M_N,n_w=M_W):
    """Three explicit closures, all exactly normalized over full real frequency axis.
    Thermal v_z/v_th Gaussian variance 1/2; finite A natural Voigt profile.
    """
    if n_mu==M_N and n_w==M_W:
        mu,mw,w,ww=MU,MW,WU,WW
        bm,vrec,erec,err=born_angular(e_ev)
    else:
        mu,mw=np.polynomial.legendre.leggauss(n_mu)
        w,ww=np.polynomial.legendre.leggauss(n_w)
        ratio,vrec,erec,err,z=exact_recoil(e_ev,mu)
        f2=72*z*z/(z*z+2.25)**6
        raw=mw*ratio*f2/z**4
        bm=raw/np.sum(raw)
    shape=np.real(wofz(np.asarray(x)[None,None,:]-vrec[:,None,None]*w[None,:,None]+ETA_EM+1j*A))/np.sqrt(np.pi)
    wd=ww*0.75*(1-w*w)
    bi=np.asarray(mw)*0.5
    return (
        np.einsum('i,j,ijk->k',bm,wd,shape,optimize=True),
        np.einsum('i,j,ijk->k',bi,wd,shape,optimize=True),
        np.einsum('i,j,ijk->k',bm,ww*0.5,shape,optimize=True),
        np.dot(bm,erec),np.dot(bm,vrec*vrec),np.dot(bi,erec),err)


def voigt_phi(x):return np.real(wofz(np.asarray(x)+1j*A))/np.sqrt(np.pi)

def hi_first_scatter_rate(x):
    qe=1.602176634e-19; eps0=8.8541878128e-12
    sigma_pref=qe**2/(4*eps0*ME*C)*0.41641/(math.sqrt(math.pi)*DNU)
    return C*138.6*sigma_pref*math.sqrt(math.pi)*voigt_phi(x)


def redistributed_moments(x_in):
    """Conditional Maxwellian HI 100K velocity given resonant absorption, R_II-like.
    Selection: p(u_parallel|x)~ exp(-u^2)*Lorentz(x-u), not unconditioned Maxwellian.
    Rayleigh phase p(mu)=3/8*(1+mu^2), coherent in rest frame; recoil O(hnu/Mc^2).
    Not exact fine-structure interference, spin exchange, detailed-balance corrected operator.
    """
    def fun(u,pow_):
        return u**pow_*math.exp(-u*u)/math.sqrt(math.pi)*A/(math.pi*((x_in-u)**2+A*A))
    def integrate(n):
        return quad(lambda u:fun(u,n),-10,10,epsabs=1e-12,epsrel=2e-10,points=[x_in] if -10<x_in<10 else None,limit=250)[0]
    d=integrate(0)
    m=integrate(1)/d; v=integrate(2)/d-m*m
    # E mu=0, E mu^2=2/5 for p(mu)=3/8*(1+mu^2).
    out_mean=x_in-m-ETA_SC
    out_var=1.4*v+0.4*(m+ETA_SC)**2+0.3
    return dict(x_in=float(x_in),absorption_profile=float(d),conditional_u_mean=float(m),conditional_u_variance=float(v),out_mean=float(out_mean),out_variance=float(out_var),mean_frequency_shift=float(out_mean-x_in))


def one_scatter_bin_masses(x_in, edges):
    """Conservative cell-integrated R(x_out|x_in), no point-sampling cusp artefact.
    For each Maxwellian transverse velocity, integrate outgoing Gaussian over
    each frequency cell analytically, then quadrature on resonant parallel velocity.
    Returns non-negative cell probabilities; finite-grid mass <= 1.
    """
    mu,mw=np.polynomial.legendre.leggauss(24)
    wm=mw*3/8*(1+mu**2)
    invsig=1/np.sqrt((1-mu**2)/2)
    ee=np.asarray(edges)[None,:]
    def integrand(u):
        mass=math.exp(-u*u)/math.sqrt(math.pi)*A/(math.pi*((x_in-u)**2+A*A))
        centre=x_in+(mu-1)*(u+ETA_SC)
        cdf=ndtr((ee-centre[:,None])*invsig[:,None])
        cell=np.diff(cdf,axis=1)
        return mass*np.einsum('i,ij->j',wm,cell)
    pts=[x_in] if -9<x_in<9 else None
    rr,_=quad_vec(integrand,-9,9,points=pts,epsabs=5e-9,epsrel=7e-6,limit=350)
    return rr/voigt_phi(x_in)


def load_source(source):
    raw=Path(source).read_bytes()
    if sha(raw)!=PHYS15_SHA:raise ValueError('IMMUTABLE_PHYS15_HASH_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        src=list(csv.DictReader(io.StringIO(z.read(PHYS15_PREFIX+'results/SOURCE_2P_LYA_ATOMS.csv').decode())))
        rows=list(csv.DictReader(io.StringIO(z.read(PHYS15_PREFIX+'results/FINAL_SOURCE_ATOM_LYA_SCATTER.csv').decode())))
        result=json.loads(z.read(PHYS15_PREFIX+'results/RESULT.json'))
        nested=z.read(PHYS15_PREFIX+'sources/PR139_ORIGINAL_SOURCE.zip')
        py=z.read(PHYS15_PREFIX+'phys15_lya.py')
    assert len(src)==6400 and len(rows)==12800
    assert sha(nested)=='55c5b97d8bb59fa2f56fb0e07deef9bf43a328feb820cb8ea0bf6fabf2f8aefa'
    return src,rows,result,py,nested


def calculate(source,output,with_first_scatter=True):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    src,rows,parent,py,nested=load_source(source)
    key=lambda x:(x['source'],int(x['source_atom_index']))
    by_policy={p:{key(r):float(r['measured_domain_H_2p_excitation_m3']) for r in rows if r['birth_policy']==p} for p in ('earliest','latest')}
    selected=[r for r in src if int(r['ionization_excitation_measured_overlap']) and float(r['primary_2p_first_event_rate_s'])>0]
    assert len(selected)==2066 and set(r['source'] for r in selected)=={'He'}
    totals={p:sum(by_policy[p].values()) for p in by_policy}
    for p in totals:
        assert abs(totals[p]/parent[p]['calculated_2p_excitations_m3']-1)<5e-13
    spectra={p:np.zeros((3,len(XGRID))) for p in by_policy}
    allrows=[];recoil_max=0.;source_max_centre_shift_x=0.
    # Remember per-event profile for exact weighted first-scatter convolution.
    emit_by_key={}
    emitted_profiles=[]
    for i,r in enumerate(selected):
        e=float(r['primary_electron_energy_eV'])
        p_b,p_u,p_i,erec,vrec2,eis,err=emit_pdf(e)
        recoil_max=max(recoil_max,err)
        source_max_centre_shift_x=max(source_max_centre_shift_x,float(exact_recoil(e,-1.)[1])+ETA_EM)
        weights={p:by_policy[p][key(r)] for p in by_policy}
        for p in by_policy:
            spectra[p]+=weights[p]*np.array([p_b,p_u,p_i])
        emit_by_key[key(r)]=p_b
        emitted_profiles.append(np.array([p_b,p_u,p_i]))
        allrows.append(dict(source=r['source'],source_atom_index=r['source_atom_index'],Ee_eV=e,
                            photon_energy_eV=r['photon_energy_eV'],excitation_earliest_m3=weights['earliest'],
                            excitation_latest_m3=weights['latest'],collision_recoil_mean_eV=erec,
                            collision_recoil_iso_impact_mean_eV=eis,
                            collision_recoil_centre_variance_x2=vrec2/5,
                            thermal_centre_variance_x2=0.5,
                            emission_photon_recoil_mean_x=-ETA_EM,
                            estimated_total_centre_variance_x2=0.5+vrec2/5,
                            collision_angular_closure='PWBA normalized NIST BE total, E1 dipole aligned',
                            max_energy_momentum_relative_residual=err))
    write_csv(output/'SOURCE_RECOIL_MODEL_CROSSWALK.csv',allrows)
    np.savez_compressed(output/'SOURCE_EMISSION_PROFILES.npz', profiles=np.asarray(emitted_profiles), x=XGRID, source_index=np.array([int(r['source_atom_index']) for r in selected]), source_type=np.array([r['source'] for r in selected]), Ee_eV=np.array([float(r['primary_electron_energy_eV']) for r in selected]))
    # Rigorous continuous distribution tail bound via triangle inequality:
    # X=centre_shift+thermal Gaussian+natural Lorentzian, |centre_shift|<=B.
    # P(|X|>L) <= P(|Voigt|>L-B). QUADPACK evaluates this positive tail.
    L=float(np.max(np.abs(XGRID)))
    assert source_max_centre_shift_x<L
    from scipy.integrate import quad as _quad
    rigorous_tail_bound=2*_quad(lambda z:float(voigt_phi(z)), L-source_max_centre_shift_x,np.inf,epsabs=1.e-12,epsrel=1.e-10)[0]+1.e-10
    labels=['BORN_DIPOLE','ISOTROPIC_IMPACT_DIPOLE','BORN_ISOTROPIC_EMISSION']
    qq=hi_first_scatter_rate(XGRID)
    srows=[];sums={}
    for p in by_policy:
        for j,name in enumerate(labels):
            curve=spectra[p][j]/totals[p]
            integralmass=float(np.trapezoid(curve,XGRID))
            haz=float(np.trapezoid(curve*qq,XGRID))
            sums[p+':'+name]=dict(mass_within_x16=integralmass,weighted_injection_hazard_s=haz,missing_spectral_mass_upper_estimate=1-integralmass,
                                 photon_number_m3=totals[p])
            for xi,n_x,norm in zip(XGRID,spectra[p][j],curve):
                srows.append(dict(birth_policy=p,angular_model=name,x_Doppler=float(xi),
                                  source_emission_spectral_number_per_Doppler_m3=float(n_x),
                                  source_emission_normalized_pdf_per_Doppler=float(norm),
                                  first_scatter_conditional_rate_s=float(hi_first_scatter_rate(xi))))
    write_csv(output/'SOURCE_EMISSION_FREQUENCY_ATLAS.csv',srows)
    # Conditional redistribution in a frozen static gas, *one* scattering, no iteration.
    mrows=[redistributed_moments(x) for x in [-10.,-5.,-3.,-1.,0.,1.,3.,5.,10.]]
    write_csv(output/'ONE_SCATTER_REDIS_MOMENTS.csv',mrows)
    rout=[];rchecks=[]
    edges=np.linspace(-20.,20.,401)
    xo=(edges[1:]+edges[:-1])/2
    dx=edges[1]-edges[0]
    for xi in (-3.,0.,3.):
        mass_by_cell=one_scatter_bin_masses(xi,edges)
        d=mass_by_cell/dx
        m=redistributed_moments(xi)
        qmass=float(np.sum(mass_by_cell))
        mean=float(np.dot(mass_by_cell,xo))
        rchecks.append(dict(xin=xi,finite_grid_mass=qmass,finite_grid_mean=mean,analytic_mean=m['out_mean']))
        for xxx,dd in zip(xo,d):rout.append(dict(xin_Doppler=xi,xout_Doppler=float(xxx),kernel_density_per_Doppler=float(dd)))
    write_csv(output/'ONE_SCATTER_REDIS_KERNEL_ATLAS.csv',rout)
    result=dict(unit='CR_PHYS16_CONDITIONAL_EMITTER_ANGULAR_SPECTRUM_AND_ONE_SCATTER_RII_LIKE',
                parent_ph15_sha256=PHYS15_SHA,source_photons=6400,source_2p_qualified=2066,
                parental_per_atom_parity=True,observed_s=1e10,temperature_K=T_K,
                total_2p_photons_m3=totals,emission_mean_photon_recoil_x=-ETA_EM,
                photon_scatter_recoil_x=ETA_SC,line_a=A,
                born_closure='MODEL_NOT_MEASURED_DCS_AND_NOT_CCC_DCS',
                maximum_source_centre_shift_x=source_max_centre_shift_x,
                rigorous_model_tail_probability_upper_x16=rigorous_tail_bound,
                spectral_mass_and_injection_hazard=sums,collision_energy_residual_max=recoil_max,
                redistribution=mrows,redistribution_grid_checks=rchecks,
                physical_K='UNBOUND',global_He_exclusive='UNBOUND',
                shared_gas_radiation_clock_geometry='UNBOUND',
                no_full_recoil_PDF='TRUE_WITHOUT_PRIMARY_DCS',
                multiple_scattering='NOT_RUN',source_owned_full_redistribution='NOT_BOUND',
                central_DAG='28/88 DELTA0',extension_DAG='0/3 DELTA0',
                auxiliary_scope='NEW_CONDITIONAL_RESEARCH_UNIT_UNDER_SAME_AUTHOR_REVIEW',
                R06_distinct_author='NOT_RUN',C09_distinct_author='NOT_RUN',native_subagent='NOT_RUN',
                native25='HOLD',L4='HOLD',production='HOLD',no_merge=True,no_force_push=True)
    if with_first_scatter:
        # Future full integration would require rebinding the correct time-ordered per-atom source r_2p.
        result['source_spectrally_integrated_first_scatter']='NOT_RUN_NO_CLAIM'
    (output/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    return result

def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'sources/PR140_PHYS15_SOURCE.zip');p.add_argument('--output',type=Path,default=ROOT/'results');args=p.parse_args()
    r=calculate(args.source,args.output)
    print(json.dumps({k:v for k,v in r.items() if k in ('source_photons','source_2p_qualified','spectral_mass_and_injection_hazard','redistribution_grid_checks','collision_energy_residual_max')},indent=2))
