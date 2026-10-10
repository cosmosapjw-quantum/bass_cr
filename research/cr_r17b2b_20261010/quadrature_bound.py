"""Independent additional midpoint-source quadrature bound for diagnostics.
The mathematical interval path continues to use S db exactly. This only bounds
a finite auxiliary population's exact IVP relative to the true continuum IVP;
point ODE integration error is NOT supplied by this quadrature bound.
"""
import sys,json,argparse
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from interval_backend import I,Jet
from interval_rhs import *
from homotopy import load_contract,compute

def auxiliary(n,eta):
 c=load_contract();p=c['plan'];S=F.from_float(5e-15);Tq=F(T);records=[]
 cells=sorted(set((F.from_float(row['left']),F.from_float(row['right'])) for row in p['same_source_weight_boxes'].values()))
 W1=F(0);clockerr=F(0);masserr=F(0)
 for l,r in cells:
  h=(r-l)/n
  W1+=S*n*h*h/(4*Tq) # global-u Lipschitz distance moment, exact rational.
  for j in range(n):
   bb=l+h*F(2*j+1,2);w=S*h;b64=float(bb);w64=float(w)
   clockerr+=w*abs(F.from_float(b64)-bb)/Tq;masserr+=abs(F.from_float(w64)-w)
   records.append(dict(birth_proper_s=b64,weight=w64,exact_birth=str(bb),exact_weight=str(w)))
 def ii(q):return I(q.numerator)/q.denominator
 r=compute();E=I(*r['energy_eV']);sig=sigma(Jet.variable(E)).derivatives();sigmax=sig[0].mag();sigprime=sig[1].mag()
 A=I(T)*C*I(NH)*I(sigmax);K=A*I('.11');kb=I(T)*C*I(NH)*I('.11')*I(sigprime)*I(H)*T*E
 qheat=(E-CHI[0])/W0;qb=I(H)*T*E/W0
 slope_x=K+kb
 slope_w=qheat*K+qb*K+qheat*kb+qheat*K*(K+kb)
 slope=I(max(slope_x.hi,slope_w.hi));force=I(max(K.hi,(qheat*K).hi))
 quad_forcing=slope*ii(W1+clockerr)+force*ii(masserr)
 q=I(*r['q_contraction'])+I(*r['mixed_g_source_gain'])*ii(masserr)
 for radius,margin in zip(r['gas_selfmap_radii'],r['initial_margins']):
  if (I(radius)+force*ii(masserr)).hi>=I(margin).lo:raise ValueError('AUXILIARY_TUBE_SELF_MAP')
 if q.hi>=1:raise ValueError('AUXILIARY_CONTRACTION')
 G=I(T)*I(299792458.)*I(6.6524587e-29)*I(10**6)*I(NH)*(I(1)+3*I(FHE))
 tau=G*quad_forcing/(1-q)
 return records,dict(auxiliary_midpoints_per_cell=n,eta=eta,source='same continuous Sdb represented only for diagnostics',
 exact_midpoint_W1_global_u=str(W1),clock_realification_error=str(clockerr),mass_realification_error=str(masserr),
 independent_quadrature_gas_forcing_bound=quad_forcing.data(),independent_tau_quadrature_radius=(I(eta)*tau).data(),
 point_ODE_integration_error='NOT_ENCLOSED; diagnostics cannot be promoted to interval truth',
 proof='Exact midpoint integral |b-bmid| and full-birth absorption/heat Lipschitz majorant; directed causal gas contraction',
 physical_source_plan_changed=False,auxiliary_mass_perturbation_contraction=q.data())
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();rows=[]
 for n in [16,32]:
  _,r=auxiliary(n,1);rows.append(r)
 with x.output.open('x') as f:f.write(json.dumps(rows,indent=2)+'\n')
 print(json.dumps(rows))
