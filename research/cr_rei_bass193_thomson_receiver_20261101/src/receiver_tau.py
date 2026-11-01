#!/usr/bin/env python3
"""REI consumer science: BASS193 source-owned H/He/21-charge electron tau/visibility.

This is a finite z=20..2 FLRW proxy receiver, not REI fully coupled IVP or Bianchi
line-of-sight transfer. All original rate histories remain read-only.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

C_M_S = 299792458.0
SIGMA_T_M2 = 6.6524587321e-29  # locked Thomson SI cross-section
SOURCE_NAME = 'REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip'
SOURCE_SHA = '4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52'
SOURCE_GIT_BLOB_ARRIVAL = '61ef864bac685be02560cde84e24837a3e5b2914'
SHA = {
 'inputs/PR302_THERMAL_192.csv': '292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6',
 'inputs/PR303_SPECIES_192.csv': 'dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09',
 'inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv': '50a9a7a2728f08ac4534f0e92071cdd4fb3b7ddc9a3e9f8175458d398ad06b0f',
}

def git_blob_sha(raw: bytes) -> str:
 return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def load(path: Path):
 raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
  raise ValueError('SOURCE_FULL_ZIP_SHA256_MISMATCH')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if z.testzip() is not None:
   raise ValueError('ORIGINAL_ZIP_CRC_FAIL')
  for name,expected in SHA.items():
   if hashlib.sha256(z.read(name)).hexdigest()!=expected:
    raise ValueError('SOURCE_MEMBER_HASH_MISMATCH '+name)
  arr_raw=z.read('results/CCC_FIRST_COLLISION_ARRIVAL_192.csv')
  if git_blob_sha(arr_raw)!=SOURCE_GIT_BLOB_ARRIVAL:
   raise ValueError('CCC_192_ORIGINAL_GIT_BLOB_DRIFT')
  thermal=pd.read_csv(io.BytesIO(z.read('inputs/PR302_THERMAL_192.csv')))
  species=pd.read_csv(io.BytesIO(z.read('inputs/PR303_SPECIES_192.csv')))
  plasma=pd.read_csv(io.BytesIO(z.read('inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv')))
  arrival=pd.read_csv(io.BytesIO(arr_raw))
 if (len(plasma),len(thermal),len(species),len(arrival))!=(193,192,192,192):
  raise ValueError('ORIGINAL_SOURCE_GRID_LENGTH_DRIFT')
 if not np.array_equal(plasma.epoch,np.arange(193)):
  raise ValueError('ORIGINAL_EPOCH_INDEX_DRIFT')
 if not np.array_equal(arrival.arrival_interval,np.arange(192)):
  raise ValueError('ORIGINAL_ARRIVAL_INDEX_DRIFT')
 return plasma,thermal,species,arrival

def _tau_visibility(ne: np.ndarray, dt: np.ndarray):
 # Use 193 source endpoints and 192 exact source-owned proper-time intervals.
 delta=C_M_S*SIGMA_T_M2*.5*(ne[:-1]+ne[1:])*dt
 tau=np.cumsum(delta[::-1])[::-1]
 tau_next=np.r_[tau[1:],0.0]
 visibility=np.exp(-tau_next)*(-np.expm1(-delta))
 return delta,tau,visibility

def calculate(source: Path, out: Path):
 plasma,thermal,species,arrival=load(source)
 z=plasma.z.to_numpy(dtype=float);a=plasma.x.to_numpy(dtype=float)
 nb=plasma.nb_m3.to_numpy(dtype=float)
 dt=thermal.proper_interval_s.to_numpy(dtype=float)
 if not ((dt>0).all() and (nb>0).all() and (np.diff(z)<0).all()):
  raise ValueError('INVALID_CLOCK_OR_BACKGROUND_STATE')
 if np.max(np.abs(z[1:]-arrival.z_low.to_numpy()))>=1e-11:
  raise ValueError('Z_ENDPOINT_PARENT_MISMATCH')
 if np.max(np.abs(z[:-1]-arrival.z_high.to_numpy()))>=1e-11:
  raise ValueError('Z_START_PARENT_MISMATCH')
 if np.max(np.abs(nb[1:]-arrival.nb_m3.to_numpy()))>=1e-10:
  raise ValueError('ORIGINAL_BARYON_DENSITY_MISMATCH')
 if np.max(np.abs(dt-arrival.proper_interval_s.to_numpy()))>=1e-1:
  raise ValueError('SOURCE_PROPER_TIME_MISMATCH')
 full_saved=nb*plasma.xe_saved.to_numpy(dtype=float)
 full_star=nb*plasma.xe_star.to_numpy(dtype=float)
 # Source-owned H/He chemistry, not a substitute for the full 21-charge electron bath.
 Y=float(species.helium_per_H_ref.iloc[0]);fH=float(thermal.nHref_over_nb.iloc[0]);
 if np.max(np.abs(species.helium_per_H_ref.to_numpy()-Y))>=1e-10:
  raise ValueError('HE_ABUNDANCE_DRIFT')
 if np.max(np.abs(thermal.nHref_over_nb.to_numpy()-fH))>=1e-10:
  raise ValueError('H_REF_NORMALIZATION_DRIFT')
 hII=np.r_[species.xHII_start.iloc[0],species.xHII_end.to_numpy()]
 heII=np.r_[species.xHeII_start.iloc[0],species.xHeII_end.to_numpy()]
 heIII=np.r_[species.xHeIII_start.iloc[0],species.xHeIII_end.to_numpy()]
 hhe=nb*fH*(hII+Y*(heII+2*heIII))
 direct_hhe=arrival.ne_HHe_cm3.to_numpy()*1e6
 if np.max(np.abs(hhe[1:]-direct_hhe)/np.maximum(1e-30,direct_hhe))>=2e-12:
  raise ValueError('HHE_CHARGE_PROJECTION_MISMATCH')
 deltaS,tauS,visS=_tau_visibility(full_saved,dt)
 deltaE,tauE,visE=_tau_visibility(full_star,dt)
 deltaH,tauH,visH=_tau_visibility(hhe,dt)
 rightS=C_M_S*SIGMA_T_M2*full_saved[1:]*dt
 rightE=C_M_S*SIGMA_T_M2*full_star[1:]*dt
 rightH=C_M_S*SIGMA_T_M2*hhe[1:]*dt
 interval=np.arange(192)
 dz=np.log1p(z[:-1])-np.log1p(z[1:])
 if not (dz>0).all():
  raise ValueError('REDSHIFT_LOG_BIN_INVERSION')
 data=pd.DataFrame(dict(interval=interval,z_high=z[:-1],z_low=z[1:],proper_dt_s=dt,
  nb_start_m3=nb[:-1],nb_end_m3=nb[1:],xe_saved_start=plasma.xe_saved.to_numpy()[:-1],
  xe_saved_end=plasma.xe_saved.to_numpy()[1:],xe_star_start=plasma.xe_star.to_numpy()[:-1],
  xe_star_end=plasma.xe_star.to_numpy()[1:],ne_full21_saved_start_m3=full_saved[:-1],
  ne_full21_saved_end_m3=full_saved[1:],ne_static_star_start_m3=full_star[:-1],
  ne_static_star_end_m3=full_star[1:],ne_HHe_start_m3=hhe[:-1],ne_HHe_end_m3=hhe[1:],
  dtau_full_saved_trap=deltaS,dtau_static_star_trap=deltaE,dtau_HHe_trap=deltaH,
  dtau_full_saved_right=rightS,dtau_static_star_right=rightE,dtau_HHe_right=rightH,
  tau_full_saved_from_high_to_z2=tauS,tau_static_star_from_high_to_z2=tauE,
  tau_HHe_from_high_to_z2=tauH,finite_window_bin_visibility_saved=visS,
  finite_window_bin_visibility_star=visE,finite_window_bin_visibility_HHe=visH,
  delta_visibility_static_minus_saved=visE-visS,
  probability_density_per_log1pz_saved=visS/dz,
  probability_density_per_log1pz_star=visE/dz))
 out.mkdir(parents=True,exist_ok=True)
 data.to_csv(out/'BASS193_HHE_THOMSON_RECEIVER_192.csv',index=False,float_format='%.17g')
 sums={}
 for name,ds,vs,right in [('full21_saved',deltaS,visS,rightS),('instant_static_star',deltaE,visE,rightE),('HHe_component',deltaH,visH,rightH)]:
  tau=float(ds.sum());total=float(np.sum(vs));normal=-math.expm1(-tau)
  sums[name]={"tau_trapezoid":tau,"tau_right_endpoint":float(right.sum()),"trapezoid_minus_right":tau-float(right.sum()),
   "finite_window_scattering_probability":total,"finite_window_transmission":float(math.exp(-tau)),
   "visibility_telescoping_abs_error":abs(total-normal),"conditional_visibility_mean_z":float(np.dot(vs,.5*(z[:-1]+z[1:]))/total),
   "largest_visibility_bin":int(np.argmax(vs))}
 # A same-clock source/closure comparison, not a statistical uncertainty band.
 stats=dict(schema='REI_BASS193_SOURCE_BOUND_HHE_THOMSON_RECEIVER_V1',
  status='SOURCE_SUPPORTED_FINITE_Z_WINDOW_FLRW_DIAGNOSTIC_NOT_REI_COUPLED_DAG',
  source={'private_zip_name':SOURCE_NAME,'private_zip_sha256':SOURCE_SHA,
          'CCC_192_public_git_blob_sha1':SOURCE_GIT_BLOB_ARRIVAL,'parent_REI_PR':311,
          'original_BASS_epochs':193,'proper_intervals':192,'source_file_sha256':SHA},
  physical={'c_m_s':C_M_S,'sigma_T_m2':SIGMA_T_M2,'redshift_window':[2,20],
   'unit':'dimensionless tau; n_e in m^-3, proper dt in seconds',
   'full21_saved_vs_static_star':'alternate source-owned static-response closure, not observational confidence interval',
   'HHe_component':'H/He ions only; not an independently sourced total 21-species electron bath'},
  totals=sums,
  diagnostics={'max_rel_HHe_projection_vs_arrival':float(np.max(np.abs(hhe[1:]-direct_hhe)/np.maximum(direct_hhe,1e-30))),
   'max_rel_HHe_vs_full21_saved_end':float(np.max(np.abs(hhe[1:]-full_saved[1:])/np.maximum(full_saved[1:],1e-30))),
   'tau_star_minus_saved_trapezoid':sums['instant_static_star']['tau_trapezoid']-sums['full21_saved']['tau_trapezoid'],
   'tau_star_fractional_increase':sums['instant_static_star']['tau_trapezoid']/sums['full21_saved']['tau_trapezoid']-1,
   'tau_HHe_minus_full21_saved':sums['HHe_component']['tau_trapezoid']-sums['full21_saved']['tau_trapezoid'],
   'dt_source_sum_s':float(dt.sum()),
   'max_abs_xe_star_minus_saved':float(np.max(np.abs(plasma.xe_star-plasma.xe_saved))),
   'max_abs_unnormalized_visibility_delta':float(np.max(np.abs(visE-visS))),
   'density_positive':bool((full_saved>=0).all() and (full_star>=0).all() and (hhe>=0).all())},
  admission={'central_dag':'28/88_REPORTED_DELTA0','working_dag':'33/88_REPORTED_DELTA0','extension_dag':'0/3_REPORTED_DELTA0',
   'REI_coupled_first_interval':'NOT_IMPLEMENTED','Bianchi_directional_tau':'NOT_COMPUTED','fully_recombined_cmb_tau':'NOT_COMPUTED',
   'CR_effect':'OFF_NOT_TESTED','independent_author_review':'NOT_RUN','production':'HOLD','no_merge':True,'no_force_push':True})
 (out/'RESULT.json').write_text(json.dumps(stats,sort_keys=True,indent=2)+'\n')
 return stats,data

def plot(resultdir:Path,figdir:Path):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 d=pd.read_csv(resultdir/'BASS193_HHE_THOMSON_RECEIVER_192.csv')
 figdir.mkdir(exist_ok=True,parents=True)
 z=d.z_low.to_numpy();zh=d.z_high.to_numpy()
 settings=[
  ('FIG1_electron_fraction_history.png','xe history of frozen BASS193 (not REI integrated)',
   ['xe_saved_end','xe_star_end'],'electron per baryon'),
  ('FIG2_cumulative_tau.png','H/He and full21 finite-window Thomson optical depth',
   ['tau_full_saved_from_high_to_z2','tau_static_star_from_high_to_z2','tau_HHe_from_high_to_z2'],'tau from redshift z to 2'),
  ('FIG3_visibility_log_redshift.png','Finite-window Thomson scattering probability per log(1+z)',
   ['probability_density_per_log1pz_saved','probability_density_per_log1pz_star'],'dP / d ln(1+z)')]
 for fn,title,keys,ylabel in settings:
  fig,ax=plt.subplots(figsize=(7.6,4.4));
  xaxis=zh if fn=='FIG2_cumulative_tau.png' else (.5*(z+zh) if fn=='FIG3_visibility_log_redshift.png' else z)
  for k in keys:ax.plot(xaxis,d[k],lw=1.8,label=k)
  ax.set(xlabel='redshift z',ylabel=ylabel,title=title);ax.grid(alpha=.25);ax.legend(fontsize=7)
  fig.tight_layout();fig.savefig(figdir/fn,dpi=135);plt.close(fig)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results');p.add_argument('--figures',type=Path,default=Path(__file__).resolve().parents[1]/'figures');p.add_argument('--no-plot',action='store_true')
 a=p.parse_args();r,d=calculate(a.source,a.out)
 if not a.no_plot:plot(a.out,a.figures)
 print(json.dumps({'rows':len(d),'saved_tau':r['totals']['full21_saved']['tau_trapezoid'],'star_tau':r['totals']['instant_static_star']['tau_trapezoid'],'hhe_tau':r['totals']['HHe_component']['tau_trapezoid']},sort_keys=True))
