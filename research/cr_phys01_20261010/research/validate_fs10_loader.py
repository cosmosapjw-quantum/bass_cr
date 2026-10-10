"""Targeted source/adapter invariant checks; not an independent MC benchmark."""
from pathlib import Path
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fs10 import FS10Table, IONIZATION_EV, electron_loss_timescale_estimate

f=FS10Table()
E=np.r_[0,np.geomspace(.001,9937.21,2000),f.energy_eV,13.599,13.6,24.599,24.6,54.399,54.4]
r=f.evaluate(E)
assert np.max(abs(r['closed_energy_residual_eV'])) < 1e-10
for key,I in zip(['HI','HeI','HeII'],IONIZATION_EV):
    assert np.all(r['ionization_counts'][key][E<I] == 0)
for bad in [-1,9938,np.nan]:
    try: f.evaluate(bad)
    except ValueError: pass
    else: raise AssertionError('domain not rejected')
raw=f.raw; en=f.energy_eV
ev=np.c_[en,raw[:,1:4]*en[:,None],raw[:,5:8]*IONIZATION_EV,
         f._raw_defect,-f._raw_defect]
np.savetxt(ROOT/'research/FS10_COLUMN_ENERGY_LEDGER.csv',ev,delimiter=',',
 header='E_eV,raw_fion_energy_eV,raw_heat_energy_eV,raw_exc_energy_eV,HI_count_energy_eV,HeI_count_energy_eV,HeII_count_energy_eV,raw_event_defect_eV,heat_correction_eV',comments='')
result={'audit':f.audit,'scan_points':len(E),
 'max_closed_residual_eV':float(np.max(abs(r['closed_energy_residual_eV']))),
 'max_threshold_correction_eV':float(np.max(abs(r['threshold_interpolation_correction_eV']))),
 'column_ledger':'FS10_COLUMN_ENERGY_LEDGER.csv',
 'time_estimates':{str(e):{k:float(v) if isinstance(v,(np.number,int,float)) else v
   for k,v in electron_loss_timescale_estimate(e).items()} for e in [100,1000,9937.21]}}
(ROOT/'research/FS10_LOADER_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS_WITH_DECLARED_CONDITIONAL_SCOPE','scan_points':len(E),
 'max_closed_residual_eV':result['max_closed_residual_eV']}))
