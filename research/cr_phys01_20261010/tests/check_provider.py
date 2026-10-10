"""Independent quadrature route for the assembled finite component.

Shares published coefficients and selected table interpolation; independent
integration algorithm, not an independent physical calibration.
"""
import sys, json, hashlib, math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from provider import build_packet, convolve_secondary, response_vector, CHANNELS, canonical_hash
from fs10 import FS10Table,IONIZATION_EV
import rudd

table=FS10Table(); records=[]
for K in [1e6,2e6,4e6]:
    for target in ['H','He']:
        vector=convolve_secondary(np.array([K]),target,table)[0]
        endpoint=float(rudd.secondary_max_eV(K,target))
        points=np.unique(np.r_[table.energy_eV,10.2,IONIZATION_EV])
        points=points[(points>0)&(points<endpoint)]
        for c in [0,2,5,6,7]:
            def integrand(W):
                return float(rudd.dsigma_dW_m2_per_eV(K,W,target))*float(response_vector(table,W)[c])
            ref,error=quad(integrand,0,endpoint,points=points,epsabs=1e-45,epsrel=2e-9,limit=600)
            relative=abs(vector[c]-ref)/max(abs(ref),1e-80)
            records.append({'K_eV':K,'target':target,'channel':CHANNELS[c],
                            'analytic':float(vector[c]),'adaptive_quad':ref,'relative_error':relative})
            assert relative<2e-8,(K,target,c,relative)
base,_,_=build_packet(48,8,8); fine,_,_=build_packet(64,12,12)
comparisons={}
for k in ['primary_rate_m3_s','secondary_rate_m3_s','heat_power_j_m3_s',
          'excitation_escape_power_j_m3_s','modelled_ionization_loss_power_j_m3_s']:
    a,b=np.array(base[k]),np.array(fine[k]); r=float(np.max(abs(a-b)/np.maximum(abs(b),1e-90)))
    comparisons[k]=r
    assert r<2e-6,(k,r)
assert all(x>0 for x in base['primary_rate_m3_s']+base['secondary_rate_m3_s'])
assert base['heat_power_j_m3_s']>0 and base['excitation_escape_power_j_m3_s']>0
assert abs(math.fsum([base['heat_power_j_m3_s'],base['ionization_power_j_m3_s'],
                     base['excitation_escape_power_j_m3_s'],-base['modelled_ionization_loss_power_j_m3_s']])) < 128*np.finfo(float).eps*base['modelled_ionization_loss_power_j_m3_s']
payload=base.copy(); claimed=payload.pop('packet_sha256'); assert claimed==canonical_hash(payload)
for K in [0,999999,4000001,np.nan]:
    try: convolve_secondary(np.array([K]),'H',table)
    except ValueError: pass
    else: raise AssertionError(('domain',K))
out={'status':'PASS','quadrature_comparisons':records,'max_quadrature_relative_error':max(x['relative_error'] for x in records),
     'resolution_48_8_8_vs_64_12_12':comparisons,'admission':'finite instantaneous component only; terminal-delay and full-history not evaluated',
     'thresholds':{'independent_quadrature':2e-8,'resolution_relative':2e-6,'ledger':'128*f64EPS'},
     'physical_oracle_independent':False,'numerical_integration_independent':True}
(ROOT/'evidence'/'PROVIDER_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'max_quadrature_relative_error':out['max_quadrature_relative_error'],'resolution':comparisons}))
