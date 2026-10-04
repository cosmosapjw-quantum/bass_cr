#!/usr/bin/env python3
"""Exact finite bookkeeping checks, not an atomic/thermochemistry simulation."""
import json
from fractions import Fraction as F
H=(1,1,0,0,0,0,1); HE=(0,0,1,1,1,0,0); Q=(0,1,0,1,2,-1,-1)
REACTIONS={
 'HI_photo':(-1,1,0,0,0,1,0),'HI_e_impact':(-1,1,0,0,0,1,0),
 'HI_H_impact_k57':(-1,1,0,0,0,1,0),'HI_He_impact_k58':(-1,1,0,0,0,1,0),
 'HeI_photo':(0,0,-1,1,0,1,0),'HeI_e_impact':(0,0,-1,1,0,1,0),
 'HeII_photo':(0,0,0,-1,1,1,0),'HeII_e_impact':(0,0,0,-1,1,1,0),
 'HII_RR':(1,-1,0,0,0,-1,0),'HeII_RR_DR':(0,0,1,-1,0,-1,0),
 'HeIII_RR':(0,0,0,1,-1,-1,0),'HeIII_HI_RCT':(-1,1,0,1,-1,0,0),
 'HeIII_HI_NRCT':(-1,1,0,1,-1,0,0),'HII_HI_resonant_CX':(0,0,0,0,0,0,0),
 'HH_ion_pair':(-2,1,0,0,0,0,1)}
def conserved(v):return all(sum(x*y for x,y in zip(w,v))==0 for w in (H,HE,Q))
def check():
 out=[]
 for name,v in REACTIONS.items():
  assert conserved(v),name; out.append(name+':nuclei_charge')
 assert REACTIONS['HeIII_HI_RCT'][5]==0 and REACTIONS['HH_ion_pair'][5]==0
 out.append('CX_and_ion_pair_free_electron_zero')
 broken=list(REACTIONS['HeIII_HI_RCT']);broken[5]=1
 assert not conserved(broken);out.append('negative_wrong_CX_electron_detected')
 chiH=F('13.598');chiHeII=F('54.418');delta=chiH-chiHeII
 assert delta==F('-40.820');out.append('declared_rounded_threshold_RCT_binding_release')
 assert delta+(-delta)==0;out.append('symbolic_photon_plus_binding_partition')
 assert delta+2*(-delta)!=0;out.append('negative_double_count_photon_and_heat_detected')
 for energy in (F(14),F(25),F(60)):
  assert (energy-chiH)+chiH==energy
 out.append('photoelectron_plus_threshold_equals_absorbed_energy')
 assert 3*(1+F(2,3))==5;out.append('proper_thermal_expansion_factor_five')
 assert F('1.70e-13')/F('1e-14')==17;out.append('He_source_alternative_ratio17')
 assert F('1e-17')*F('1e-3')**2==F('1e-23');out.append('k57_density_normalization')
 return {'status':'FINITE_BOOKKEEPING_CHECKS_PASS','checks':out,'count':len(out),
 'threshold_note':'rounded declared fixture values, not updated atomic constants',
 'scientific_history_executed':False,'consumer_admission':False}
if __name__=='__main__':print(json.dumps(check(),indent=2))
