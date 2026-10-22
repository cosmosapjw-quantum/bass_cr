#!/usr/bin/env python3
"""Independent C22A algebra/RHS checks only; no ODE integrator is invoked."""
from __future__ import annotations
import os, sys, json, math, hashlib, re, argparse
from pathlib import Path
from decimal import Decimal, localcontext
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args=parser.parse_args()
ROOT=args.research_root.resolve()
UNIT=ROOT/'cr_c22a_thermochemical_20261022'
sys.path.insert(0,str(UNIT))
import numpy as np
from model import ThermochemicalFactory,K_B_EV_K
from rr_energy_moment import rr_energy_factor
from coupled_model import component_fields

WATCH=[UNIT/'model.py',UNIT/'rr_energy_moment.py',ROOT/'cr_c21o_hheli_z2_20261021'/'atomic_network.py',ROOT/'cr_c21o_hheli_z2_20261021'/'coupled_model.py',ROOT/'cr_c21n_mass_shell_cache_20261021'/'builder.py']
def hashes(): return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in WATCH}
start=hashes()
factory=ThermochemicalFactory()
model=factory.build({'signed_sigma':0.3,'signed_pi_m':0.0003,'signed_pi_r':-0.0003,'temperature_K':300.0})
rng=np.random.default_rng(2026102201)
record={'execution':{'ODE_integrations':0,'solver_imported_indirectly':True,'solver_called':False,'new_finite_state_checks':True},'source_start':start,'checks':{}}

# An independent high-precision central derivative of the number-rate formula.
# This tests the energy-factor implementation rather than differentiating it.
rr_rows=[]
with localcontext() as ctx:
    ctx.prec=75
    D=lambda x:Decimal(str(x))
    for i,params in enumerate(model.parameters):
        a,b,t0,t1=map(D,params)
        def alpha(t):
            x=(t/t0).sqrt(); z=(t/t1).sqrt()
            return a/(x*((1-b)*(1+x).ln()).exp()*((1+b)*(1+z).ln()).exp())
        for t0num in (3.0,300.,1e4,2e4,1e6,1e9):
            t=D(t0num); dt=t*D('1e-14')
            ref=D('1.5')+t*(alpha(t+dt)-alpha(t-dt))/(2*dt*alpha(t))
            actual=float(rr_energy_factor(params,t0num))
            rr_rows.append({'channel':i,'T_K':t0num,'factor':actual,'decimal_fd_reference':float(ref),'relative_error':float(abs(D(actual)-ref)/abs(ref))})
rrerr=max(v['relative_error'] for v in rr_rows)
assert rrerr < 3e-14 and all(0<v['factor']<1 for v in rr_rows)
record['checks']['RR_energy_factor']={'states':len(rr_rows),'maximum_relative_error':rrerr,'all_positive_below_one':True,'rows':rr_rows}

# Parse primary-author DATA statements separately and evaluate the documented
# phfit2 branches using scalar math, not the provider's vectorized code.
fortran=ROOT/'cr_c21o_hheli_z2_20261021/vendor/atomic/phfit2.f'
text='\n'.join(line[6:] for line in fortran.read_text().splitlines() if line and line[0] not in '*cC')
def data(pattern):
    m=re.search(pattern+r'\s*/([^/]+)/',text,re.I)
    assert m is not None
    return [float(x) for x in m.group(1).replace('\n','').split(',')]
def author_sigma(Z,N,s,E):
    p1=data(rf'DATA\s*\(PH1\(I,\s*{Z},\s*{N},\s*{s}\),I=1,6\)')
    if E<p1[0]: return 0.0
    if Z==3 and N==3 and E>=64.39:
        exponent=-p1[4]; u=E/p1[1]
        return p1[2]*((u-1.0)**2+p1[5]**2)*u**(-0.5*exponent-5.5)*(math.sqrt(u/p1[3])+1.0)**exponent
    p2=data(rf'DATA\s*\(PH2\(I,\s*{Z},\s*{N}\),I=1,7\)')
    exponent=-p2[3]; x=E/p2[0]-p2[5]; u=math.sqrt(x*x+p2[6]*p2[6])
    return p2[1]*((x-1.0)**2+p2[4]**2)*u**(-0.5*exponent-5.5)*(1.0+math.sqrt(u/p2[2]))**exponent
sigma_rows=[]
for name,row in model.atomic.provider.rows.items():
    chi=row['chi_eV']
    values=[np.nextafter(chi,0.0),chi,np.nextafter(chi,np.inf)]
    values+=np.geomspace(chi,150.0,15).tolist()
    if name=='LiI': values += [np.nextafter(64.39,0.0),64.39,np.nextafter(64.39,np.inf),65.0,73.0,91.0,123.0,149.9]
    for E in values:
        ref=author_sigma(row['Z'],row['N'],row['shell'],float(E))
        actual=float(model.atomic.provider.sigma(name,np.array([E]))[0])
        rel=abs(actual-ref)/max(abs(ref),1e-300)
        sigma_rows.append({'channel':name,'E_eV':float(E),'reference_Mb':ref,'actual_Mb':actual,'relative_error':rel})
        assert rel<3e-14
        if E<chi: assert actual==0.0
record['checks']['author_photo_branch_parity']={'points':len(sigma_rows),'max_relative_error':max(x['relative_error'] for x in sigma_rows),'primary_source_sha256':hashlib.sha256(fortran.read_bytes()).hexdigest(),'rows':sigma_rows,'scope':'Independent scalar transcription of frozen author formula, not empirical fit accuracy or a Fortran binary comparison'}

# Finite-state energy, charge, photons, isotope and exact zero-parent identities.
rows=[]
times=[0.,.2,.7,1.3,model.eta_end]
for trial in range(10):
    y=model.initial_state()
    for name,ids in model.atomic.blocks.items():
        total=model.atomic.initial_nucleus_totals[name]
        if total>0:
            f=rng.dirichlet(np.ones(len(ids)))
            y[model.ax][list(ids)]=total*f/model.atomic.scales[list(ids)]
    y[model.gx]=10**rng.uniform(-7,0,6)
    abundance=model.atomic.physical_abundances(y[model.ax])
    T=10**rng.uniform(1,6)
    y[model.iu]=1.5*K_B_EV_K*T*(sum(abundance)+model.atomic.q@abundance)
    for eta in times:
        d=model.rhs(eta,y)
        E=model.photon_energies(eta)
        dn=model.atomic.scales*d[model.ax]
        terms=[float(d[model.iu]),float(model.binding@dn),float(E@d[model.gx]),float(-E@y[model.gx]),float(d[model.iesc]),float(d[model.iwg]),float(d[model.iwr])]
        residual=math.fsum(terms); scale=math.fsum(abs(v) for v in terms)
        normalized=abs(residual)/max(scale,1e-300)
        ionres=max(abs(sum(dn[list(ids)])) for ids in model.atomic.blocks.values())
        e_balance=float(model.atomic.q@dn+d[model.irr]-d[model.iabs])
        photon_balance=float(sum(d[model.gx])+d[model.iabs])
        fluxscale=max(float(sum(abs(dn)))+abs(d[model.irr])+abs(d[model.iabs]),1e-300)
        assert normalized<2e-15
        assert abs(e_balance)/fluxscale<2e-15
        assert abs(photon_balance)/fluxscale<2e-15
        assert ionres/fluxscale<2e-15
        assert np.all(d[model.ax][list(model.atomic.blocks['T'])]==0) and d[model.ax][model.atomic.blocks['n'][0]]==0
        # Same-state kinetic equations: no historic IVP is replayed.
        yp=model.parent.initial_state();yp[:model.nk]=y[:model.nk];yp[model.nk:-1]=y[model.ax]
        dp=model.parent.rhs(eta,yp)
        assert np.array_equal(d[:model.nk],dp[:model.nk])
        rows.append({'trial':trial,'eta':eta,'T_K':T,'energy_absolute_eV_per_H_per_eta':residual,'energy_term_scale':scale,'energy_term_normalized':normalized,'charge_normalized':abs(e_balance)/fluxscale,'photon_normalized':abs(photon_balance)/fluxscale,'isotope_normalized':ionres/fluxscale})
record['checks']['finite_state_ledgers']={'states':len(rows),'max_energy_abs':max(abs(x['energy_absolute_eV_per_H_per_eta']) for x in rows),'max_energy_term_normalized':max(x['energy_term_normalized'] for x in rows),'max_charge_normalized':max(x['charge_normalized'] for x in rows),'max_photon_normalized':max(x['photon_normalized'] for x in rows),'max_isotope_normalized':max(x['isotope_normalized'] for x in rows),'kinetic_first40_parent_array_equal_all':True,'rows':rows}

# Scalar norms are computed only after signed tensor addition.
y=model.initial_state();q=model.fields(0,y);c=component_fields(q)
p=q['Pi_matter_J_m3']+q['Pi_gamma_J_m3']+q['Pi_nu_J_m3']
norm=math.sqrt(6)*abs(p)
factor=c['Pi_tot_F']/norm if norm else None
assert abs(c['signed_Pi_m_F']+c['signed_Pi_r_F']-c['signed_Pi_tot_F'])<1e-18
assert c['Pi_tot_F']<1e-15
assert c['Pi_m_F']+c['Pi_r_F']>0.00059
record['checks']['signed_stress_cancellation']={'components':c,'direct_tensor_frobenius_J_m3':norm,'passed':True}

# Signed Newton perturbations are algebraic extensions, while T leaves the
# sourced rate domain by a typed refusal instead of clipping/flooring.
y=model.initial_state();y[model.ax][model.atomic.blocks['H1'][1]]=-1e-8
assert np.all(np.isfinite(model.rhs(0,y)))
refusals=[]
for temp in (2.9,1.00001e9,-1.):
    y=model.initial_state();n=model.atomic.physical_abundances(y[model.ax]);y[model.iu]=1.5*K_B_EV_K*temp*(sum(n)+model.atomic.q@n)
    try: model.rhs(0,y)
    except ValueError as e: refusals.append(str(e))
    else: raise AssertionError('out-of-domain trial was accepted')
record['checks']['trial_domain']={'signed_population_trial_finite':True,'temperature_refusals':refusals,'note':'Exceptions are not certified adaptive-step rejection; runner must preserve failed attempt if SciPy propagates one.'}
record['source_end']=hashes()
record['source_unchanged']=record['source_start']==record['source_end']
assert record['source_unchanged']
record['decision']='PASS_SCOPED_FINITE_ALGEBRA_RHS'
record['check_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out=args.out.resolve()
with out.open('x') as f: json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({'decision':record['decision'],'RR_factor_rel':rrerr,'photo_parity_rel':record['checks']['author_photo_branch_parity']['max_relative_error'],'RHS_energy_rel':record['checks']['finite_state_ledgers']['max_energy_term_normalized'],'RHS_energy_abs':record['checks']['finite_state_ledgers']['max_energy_abs'],'finite_states':len(rows),'ODE_integrations':0,'source_unchanged':record['source_unchanged']}))
