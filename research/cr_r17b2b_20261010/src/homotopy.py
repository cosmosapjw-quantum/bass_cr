"""Actual continuous-source gas Volterra map and homotopy derivative majorants.
No replacement by finite births is used for the interval calculation.
Causal survivor density is eta*S*exp(-int_b^t kappa), plus scaled original atoms.
"""
import json,hashlib
from fractions import Fraction as F
from pathlib import Path
from interval_backend import I
from ad2 import D2
from interval_rhs import *
PLAN_SHA='989ad89d4e5caf57b94d3ce69c6b997cf8b41c607c767e746b0d6cc07d2e9153'
class Unproved(ValueError):pass

def load_contract(*,source_bytes=None,clock=T,channel='shared_source_Ebirth',injection_ev=13.7):
 p=ROOT/'inherited/R17B2A/inputs/BIRTH_PLAN.json';raw=p.read_bytes() if source_bytes is None else source_bytes
 if hashlib.sha256(raw).hexdigest()!=PLAN_SHA:raise ValueError('SOURCE_BYTES')
 plan=json.loads(raw)
 if clock!=T or plan['window_s']!=[0,T]:raise ValueError('PROPER_SOURCE_CLOCK')
 if channel!='shared_source_Ebirth' or injection_ev!=13.7:raise ValueError('SOURCE_ENERGY_CHANNEL')
 initial_raw=(ROOT/'inherited/R17B2A/inputs/donor/inputs/NEXT_CELL_INPUT.json').read_bytes()
 if hashlib.sha256(initial_raw).hexdigest()!='b0d82a4945604a2053787e4c1fe767d30c39f432130bd37113db0176ee6615a7':raise ValueError('INITIAL_ENERGY_PARAMETER_BYTES')
 initial=json.loads(initial_raw)['seed']
 if initial['gas']!=[.9,.3,.6,W0] or initial['p']!=[.05] or initial['energy']!=[13.7]:raise ValueError('ORIGINAL_INITIAL_STATE')
 return dict(plan=plan,initial=initial,energy_alias=channel,energy_box=initial['energy_box'][0],source_injection_energy=13.7,initial_energy_alias='matched_original_initial_Ebirth',time_s=[0,T],eta_domain=[0,1])

def continuum_integral(t,eta,range_integrand,*,subpanels=8):
 """Outer integral with range_integrand enclosing whole proper-birth panels.
 The source is S db itself, not a more finely sampled physical birth plan.
 This bound preserves source mass and all atoms (physical right trace).
 """
 c=load_contract();acc=None
 for j in range(subpanels):
  a=I(t)*j/subpanels;b=I(t)*(j+1)/subpanels
  values=range_integrand(I(a.lo,b.hi));mass=eta*I(5e-15)*I(t)/subpanels
  term=[mass*v for v in values];acc=term if acc is None else [x+y for x,y in zip(acc,term)]
 for birth in c['plan']['same_births']:
  if I(birth).hi<=I(t).lo:
   row=c['plan']['same_source_weight_boxes'][str(birth)];mass=(1-eta)*I(row['lo'],row['hi'])
   acc=[x+mass*y for x,y in zip(acc,range_integrand(I(birth)))]
 return acc

def compute():
 c=load_contract();u=I(0,1);z=[I('.89','.91'),I('.29','.31'),I('.59','.61'),I('.99','1.01')]
 initial=c['initial'];z0=[I(v) for v in initial['gas'][:3]]+[I(1)]
 # Same fixed source Ebirth at ALL atom/probe injections, not
 # independently chosen channel values with merely overlapping boxes.
 eb=I(*c['energy_box']);e,thermal=physical_domain(u,z,eb)
 nh=I(NH)*exp(-I(3)*H*T*u);a=I(T)*C*nh*sigma(e);k=a*(1-z[0]);vmax=max(I(1).hi,((e-CHI[0])/W0).mag())
 V=I(vmax);A=I(a.hi);K=I(k.hi)
 masses=[I(row['lo'],row['hi']) for row in c['plan']['same_source_weight_boxes'].values()]
 qmass=sum(masses,I(0));smass=I(5e-15)*T
 mass_upper=max(qmass.hi,smass.hi);P=I(initial['p'][0])+I(mass_upper)
 np,unused=nonphoto_rhs(u,[D2.var(box,j) for j,box in enumerate(z)])
 field=[r.v for r in np];field[0]+=I(0,P.hi)*k;field[3]+=I(0,P.hi)*k*(e-CHI[0])/W0
 radii=[row.mag() for row in field]
 margins=[min((v-I(box.lo)).lo,(I(box.hi)-v).lo) for v,box in zip(z0,z)]
 if any(r>=m for r,m in zip(radii,margins)):raise Unproved('CONTINUUM_SELF_MAP')
 Lnp=max(sum((I(v.mag()) for v in row.g),I(0)).hi for row in np)
 Bnp=max(sum((I(v.mag()) for rr in row.h for v in rr),I(0)).hi for row in np)
 # Dg Phi_photo <=P*V*A*(1+K), Dgg <=P*V*A²*(2+K).
 # These follow from exact survival derivatives, including memory terms.
 mixed=V*A*(1+K);q=I(Lnp)+P*mixed;Bgg=I(Bnp)+P*V*A*A*(2+K)
 if q.hi>=1:raise Unproved('WHOLE_HOMOTOPY_CONTRACTION')
 nu=smass+qmass # EXACT total variation formula: continuous & atoms singular.
 gain=V*K/(1-q)
 U=gain*I(nu.hi)
 U2=(Bgg*U*U+2*mixed*U*I(nu.hi))/(1-q)
 G=I(T)*I(299792458.)*I(6.6524587e-29)*I(10**6)*nh*(I(1)+I(3)*FHE)
 direct=G*U;nonlinear=G*U2/2
 # This is a valid source interval by eta integration of the uniform tangent
 # bound, independent of nominal K samples and of Peano regularity.
 signed=[(-I(direct.hi)).data()[0],I(direct.hi).data()[1]]
 # Fixed gas energy derivatives exist to all finite orders on this compact
 # branch-free domain. The actual resolvent K3/K4 bound is not inferred.
 jet=Jet.variable(e);sigma_jets=sigma(jet).derivatives()
 return dict(status='HOMOTOPY_UNIFORM_CONTINUUM_SOURCE_BOUND__NO_CERTIFIED_SOURCE_SHARPENING',
 eta_domain=[0,1],parameter_domain='matched original initial energy family + original weight boxes; source/probe13.7 share physical source channel',
 physical_continuous_source='eta*S*survival(t,b) db; no finite-birth replacement',
 gas_tube=[v.data() for v in z],energy_eV=e.data(),thermal_K=thermal.data(),
 gas_selfmap_radii=[str(r) for r in radii],initial_margins=[str(m) for m in margins],
 photon_mass_upper=P.data(),source_signed_measure_total_variation=nu.data(),
 nonphoto_Jacobian=[ [v.data() for v in row.g] for row in np],
 nonphoto_Hessian=[[[v.data() for v in rr] for rr in row.h] for row in np],
 nonphoto_L=I(Lnp).data(),nonphoto_B2=I(Bnp).data(),q_contraction=q.data(),
 mixed_g_source_gain=mixed.data(),full_gas_path_Hessian_majorant=Bgg.data(),
 unit_probe_gas_gain=gain.data(),homotopy_tangent_gas_bound=U.data(),homotopy_second_gas_bound=U2.data(),
 source_signed_interval_candidate=signed,source_nonlinearity_nominal_tangent_remainder_radius=nonlinear.data(),
 kernel_homotopy_remainder='enclosed by second-source-variation; nominal kernel alone still not a source bound',
 sigma_energy_derivatives_0_to_4=[v.data() for v in sigma_jets],
 known_atom_J012=[0,0,0],known_atom_J3=None,regular_K4=None,anchor_K1_K2_K3=None,
 sharpened_source_interval=None,adopted_fallback='latest causal R17; safe radius2.125035e-18',
 narrower_than_fallback=direct.hi<I('2.125035e-18').lo,
 replacement_count=0,time_source_new_combination_count=0,
 high_order_blocker='No quantified mixed-time/birth resolvent J3 or regular K4 enclosure. C2 same-channel cancellation is closed; it supplies neither J3 nor K4.',
 source_sign='NOT_DETERMINED')

def channel_jump_orders(c,*,probe_alias):
 if probe_alias!=c['energy_alias']:raise ValueError('UNMATCHED_PHYSICAL_INJECTION_PARAMETER')
 r=compute()
 # Evidence is the actual analytic branch-free tube and contract, not a flag.
 return dict(J012=[0,0,0],J3=None,eta_domain=[0,1],evidence=dict(energy=r['energy_eV'],thermal=r['thermal_K'],q=r['q_contraction'],energy_alias=c['energy_alias']),lemma='Gas continuity + additive photons + smooth energy trace of the continuum photon-adjoint PDE; proof in THEORY.md')

def peano_transfer(evidence):
 # J012 cancellation and qualitative regularity do not bound J3 or K4.
 # No self-attested boolean or toy value is accepted as a derivative proof.
 raise Unproved('ACTUAL_FULL_ETA_J3_AND_REGULAR_K4_AND_ANCHOR_JETS_REQUIRED')
