#!/usr/bin/env python3
"""Source-locked PHYS09 original number-response parity independent of PHYS10 generation."""
import csv, hashlib, json, zipfile, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
z=zipfile.ZipFile(ROOT/'sources/PR134_ORIGINAL_SOURCE.zip')
PFX='research/cr_phys09_chemistry_neutral_response_20261030/results/'
def parent(name):return list(csv.DictReader(z.read(PFX+name).decode().splitlines()))
def mine(name):return list(csv.DictReader((ROOT/'results'/name).open()))
up=parent('CAUSAL_RESPONSE.csv');cur=mine('CAUSAL_ELECTRON_ENERGY.csv')
assert len(up)==len(cur)==1728
max_rel=0.;max_abs=0.; mismatch=[]
for i,(a,b) in enumerate(zip(up,cur)):
    for field in ('observation_s','birth_policy','source','absorber','neutral_parameter','window_start_s','window_end_s'):
        if a[field]!=b[field]: mismatch.append((i,field,a[field],b[field]))
    # Phys09 and Phys10 number derivative must be byte-identical written floating point.
    lhs=float(a['d_first_absorbed_dln_neutral_m3']);rhs=float(b['d_n_first_dln_neutral_m3'])
    max_abs=max(max_abs,abs(lhs-rhs));max_rel=max(max_rel,abs(lhs-rhs)/max(abs(lhs),abs(rhs),1e-40))
assert not mismatch,mismatch[:3]
assert max_rel<1e-14,(max_rel,max_abs)
base=parent('TIME_CHEMISTRY_JACOBIAN.csv');total=mine('TIME_ENERGY_LEDGER.csv')
assert len(base)==len(total)==27
for a,b in zip(base,total):
    for species in ('HI','HeI'):
        v=float(a['abs_'+species+'_m3']);w=float(b['first_'+species+'_m3']);assert math.isclose(v,w,rel_tol=1e-14,abs_tol=1e-46)
result={'parent_PHYS09_number_response_rows':1728,'parent_PHYS09_time_jacobian_rows':27,'number_response_max_rel':max_rel,'number_response_max_abs_m3':max_abs,'matches_keys':not mismatch,'time_matches_all':True}
(ROOT/'results'/'PARENT_PARITY.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,indent=2))
