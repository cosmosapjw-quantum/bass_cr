#!/usr/bin/env python3
"""Source-locked 100 K H/He ground-RR cumulative first-absorption envelopes.

This is a conditional fixed-gas local photon/primary-photoelectron data product;
it is not a cosmological opacity or coupled transfer/chemistry calculation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
PARENT_DIR = HERE.parent / 'cr_phys02_rr_boundfree_20261030'
sys.path.insert(0, str(PARENT_DIR))
import rr_boundfree as parent  # source-locked PR127 implementation; explicit oracle unchanged

C = 299792458.0  # exact SI m / s
EV_J = 1.602176634e-19 # exact SI J / eV
SOURCE_MODULE_SHA256 = '2db17652571465cd2e5f5fde51f60be01fd6d3ae2b11b193addc98dd047f9594'  # replaced during locked intake
OBS_TIMES_S = np.arange(9, dtype=np.float64) * 1.25e9
KINETIC_EDGES_EV = np.arange(23, dtype=np.float64)  # 22 [k,k+1) eV bins
CHANNELS = ('H', 'He')
TARGETS = ('HI', 'HeI')


def _sum(values):
    return math.fsum(float(x) for x in np.ravel(values))


def _check_parent():
    actual=hashlib.sha256((PARENT_DIR/'rr_boundfree.py').read_bytes()).hexdigest()
    if actual != SOURCE_MODULE_SHA256:
        raise ValueError(f'PR127_PARENT_MODULE_SHA256_MISMATCH:{actual}')


def first_absorption_probability(alpha_target: np.ndarray, alpha: np.ndarray,
                                 birth: float, observe: float) -> np.ndarray:
    if observe < 0 or birth < 0 or not np.isfinite(observe) or not np.isfinite(birth):
        raise ValueError('NONNEGATIVE_FINITE_TIME_REQUIRED')
    dt=max(0., observe-birth)
    if np.any(alpha <= 0) or np.any(alpha_target < 0) or np.any(alpha_target > alpha*(1.+1e-14)):
        raise ValueError('INVALID_OPACITY_OR_PARTITION')
    return (alpha_target / alpha) * (-np.expm1(-alpha*C*dt))


def survival_bounds(alpha:np.ndarray, t0:float, t1:float, observe:float):
    """Tight pointwise survivor extrema for arbitrary unknown emission time in [t0,t1]."""
    zeros=np.zeros_like(alpha)
    if observe < t0:
        return zeros,zeros
    if observe < t1:  # an emission can be after T, or exactly at T
        return zeros,np.ones_like(alpha)
    return np.exp(-alpha*C*(observe-t0)),np.exp(-alpha*C*(observe-t1))


def compute(arrays, density, params, observation_times=OBS_TIMES_S):
    ts=np.asarray(observation_times,dtype=np.float64)
    if ts.ndim != 1 or not len(ts) or np.any(~np.isfinite(ts)) or np.any(ts<0) or np.any(np.diff(ts)<=0):
        raise ValueError('OBSERVATION_TIMES_MUST_INCREASE')
    edges=arrays['time_edges_s']
    rows=[]; hist_rows=[]; total_rows=[]
    sigma={ch:{a:parent.verner_sigma(arrays[f'photon_{ch}_eV'], params[a]) for a in TARGETS} for ch in CHANNELS}
    ledger={ch:{a:density[a]*sigma[ch][a] for a in TARGETS} for ch in CHANNELS}
    full_opacity={ch:ledger[ch]['HI']+ledger[ch]['HeI'] for ch in CHANNELS}
    for ch in CHANNELS:
        if not np.all(full_opacity[ch]>0):
            raise ValueError('NONPOSITIVE_SOURCE_OPACITY')
    total_birth=_sum([_sum(arrays[f'capture_{ch}_bins_m3']) for ch in CHANNELS])
    energy_input=_sum([_sum(arrays[f'capture_{ch}_bins_m3'][j] * arrays[f'photon_{ch}_eV'])
                       for ch in CHANNELS for j in range(4)])*EV_J
    for T in ts:
        accumulated={'absorbed_lo_m3':0.,'absorbed_hi_m3':0.,'photon_energy_lo_J_m3':0.,'photon_energy_hi_J_m3':0.,
          'threshold_lo_J_m3':0.,'threshold_hi_J_m3':0.,'electron_excess_lo_J_m3':0.,'electron_excess_hi_J_m3':0.}
        emitted_lo=0.; emitted_hi=0.; survive_lo=0.; survive_hi=0.
        for ch in CHANNELS:
            E=arrays[f'photon_{ch}_eV']
            W=arrays[f'capture_{ch}_bins_m3']
            alpha=full_opacity[ch]
            for j in range(4):
                w=W[j]; l=float(edges[j]);r=float(edges[j+1]); born=_sum(w)
                if r<=T: emitted_lo+=born
                if l<=T: emitted_hi+=born
                surv_min,surv_max=survival_bounds(alpha,l,r,float(T))
                survive_lo+=_sum(w*surv_min)
                survive_hi+=_sum(w*surv_max)
            for a in TARGETS:
                alpha_a=ledger[ch][a]
                s_lo=0.;s_hi=0.; u_lo=0.;u_hi=0.; threshold_lo=0.;threshold_hi=0.; ex_lo=0.;ex_hi=0.
                excess=E-params[a][0]
                # On support of this target alpha_a>0 implies electron excess>=0.
                if np.any((alpha_a>0)&(excess<0)):
                    raise ValueError('BELOW_THRESHOLD_ABSORPTION')
                excess=np.maximum(excess,0.)
                hist_lo=np.zeros(len(KINETIC_EDGES_EV)-1,dtype=np.float64)
                hist_hi=np.zeros(len(KINETIC_EDGES_EV)-1,dtype=np.float64)
                if np.max(excess[alpha_a>0],initial=0)>=KINETIC_EDGES_EV[-1]:
                    raise ValueError('ELECTRON_SPECTRUM_NOT_COVERED')
                for j in range(4):
                    w=W[j]
                    p_lo=first_absorption_probability(alpha_a,alpha,float(edges[j+1]),float(T))
                    p_hi=first_absorption_probability(alpha_a,alpha,float(edges[j]),float(T))
                    nlo=w*p_lo; nhi=w*p_hi
                    s_lo+=_sum(nlo);s_hi+=_sum(nhi)
                    u_lo+=_sum(nlo*E)*EV_J;u_hi+=_sum(nhi*E)*EV_J
                    ex_lo+=_sum(nlo*excess)*EV_J;ex_hi+=_sum(nhi*excess)*EV_J
                    hist_lo+=np.histogram(excess,bins=KINETIC_EDGES_EV,weights=nlo)[0]
                    hist_hi+=np.histogram(excess,bins=KINETIC_EDGES_EV,weights=nhi)[0]
                threshold_lo=params[a][0]*EV_J*s_lo
                threshold_hi=params[a][0]*EV_J*s_hi
                # Three energy accounts refer to incident photons absorbed. Only the last is a primary electron kinetic energy budget.
                if not (0 <= s_lo <= s_hi <= total_birth*(1+1e-12)):
                    raise AssertionError('ABSORPTION_ENVELOPE_INVALID')
                if not np.isclose(u_lo,threshold_lo+ex_lo,rtol=3e-13,atol=1e-80):
                    raise AssertionError('ENERGY_LEDGER_LO')
                if not np.isclose(u_hi,threshold_hi+ex_hi,rtol=3e-13,atol=1e-80):
                    raise AssertionError('ENERGY_LEDGER_HI')
                if not np.isclose(hist_lo.sum(),s_lo,rtol=3e-13,atol=1e-90) or not np.isclose(hist_hi.sum(),s_hi,rtol=3e-13,atol=1e-90):
                    raise AssertionError('SPECTRUM_NUMBER_LEDGER')
                data={'T_s':float(T),'photon_channel':ch,'absorber':a,
                      'absorbed_lo_m3':s_lo,'absorbed_hi_m3':s_hi,
                      'photon_energy_lo_J_m3':u_lo,'photon_energy_hi_J_m3':u_hi,
                      'threshold_lo_J_m3':threshold_lo,'threshold_hi_J_m3':threshold_hi,
                      'electron_excess_lo_J_m3':ex_lo,'electron_excess_hi_J_m3':ex_hi}
                rows.append(data)
                for m in range(len(hist_lo)):
                    hist_rows.append({'T_s':float(T),'photon_channel':ch,'absorber':a,
                        'Ekin_left_eV':float(KINETIC_EDGES_EV[m]),'Ekin_right_eV':float(KINETIC_EDGES_EV[m+1]),
                        'electron_count_lo_m3':float(hist_lo[m]),'electron_count_hi_m3':float(hist_hi[m])})
                for k in accumulated:
                    accumulated[k]+=data[k]
        total_rows.append({'T_s':float(T),'source_total_photons_m3':total_birth,
          'emitted_lo_m3':emitted_lo,'emitted_hi_m3':emitted_hi,
          'survive_lo_m3':survive_lo,'survive_hi_m3':survive_hi,**accumulated})
        v=total_rows[-1]
        if v['absorbed_lo_m3'] < -1e-90 or v['absorbed_hi_m3'] > v['emitted_hi_m3']*(1+3e-13):
            raise AssertionError('CAUSALITY_OR_PHOTON_COUNT_FAIL')
        if not (0<=v['survive_lo_m3']<=v['survive_hi_m3']<=v['emitted_hi_m3']*(1+3e-13)):
            raise AssertionError('SURVIVOR_BOUNDS_FAIL')
        if v['emitted_lo_m3']>v['emitted_hi_m3']:
            raise AssertionError('EMISSION_TIME_BOUNDS_FAIL')
        # At the final horizon all the emission has occurred, so survivor/absorber complementary bounds are exact.
        if T >= edges[-1]:
            if not np.isclose(v['survive_lo_m3']+v['absorbed_hi_m3'],total_birth,rtol=3e-13):
                raise AssertionError('FINAL_SURVIVAL_DUAL_FAIL_LO')
            if not np.isclose(v['survive_hi_m3']+v['absorbed_lo_m3'],total_birth,rtol=3e-13):
                raise AssertionError('FINAL_SURVIVAL_DUAL_FAIL_HI')
    # Componentwise monotonicity of cumulative first ionizations.
    for key in ('absorbed_lo_m3','absorbed_hi_m3','electron_excess_lo_J_m3','electron_excess_hi_J_m3'):
        seq=np.array([r[key] for r in total_rows])
        if np.any(np.diff(seq)<-1e-14*max(1e-90,seq[-1])):
            raise AssertionError(f'CUMULATIVE_MONOTONICITY_{key}')
    return {
      'schema':'CR_PHYS03_RR_TEMPORAL_FIRST_ABSORPTION_V1',
      'source':'PR125 original byte-locked ground RR; PR127 source-locked Verner photoionization',
      'source_sha256':parent.PR125_SOURCE_SHA,
      'source_photon_npz_sha256':parent.PR125_NPZ_SHA,
      'pr127_parent_module_sha256':SOURCE_MODULE_SHA256,
      'density_m3':density,
      'source_total_photons_m3':total_birth,
      'source_total_photon_energy_J_m3':energy_input,
      'time_observe_s':list(map(float,ts)),
      'spectral_energy_bins_eV':list(map(float,KINETIC_EDGES_EV)),
      'atomic_photon_energies_per_channel':3200,
      'source_time_bins':4,
      'assumptions':['frozen homogeneous 100 K gas','constant ground-state H I and He I densities',
        'straight photon at physical c','no scattering, reemission, redshift, gas feedback or secondary electrons',
        'first photoionization only','arbitrary unknown birth times within four original proper-time bins'],
      'interpretation':'exact pointwise interval for original source under specified frozen medium; not a unique history, cosmological tau, rate, electron heating or an IVP',
      'pr127_reproduction':'final 1e10 s absorption endpoint must match parent PR127 result',
      'central_dag':'28/88','extension_dag':'0/3','scoped_new_aux':'1/1_REVIEW_HOLD',
      'distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN',
      'physical_K':None,'exclusive_He_kernel':None,'native25':False,'L4':False,'production':False
    },rows,total_rows,hist_rows


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def run(source_zip:Path,outdir:Path):
    _check_parent()
    params,table_sha=parent.load_verner()
    _,arrays,density=parent.read_source(source_zip)
    meta,channels,totals,hist=compute(arrays,density,params)
    # Same source+physics baseline at PR127 horizon (recomputed from pristine source).
    prior,_,_,_=parent.evaluate(arrays,density,params)
    final=totals[-1]
    if final['T_s']==1.e10:
        for k,oldkey in [('absorbed_lo_m3','absorbed_lower_m3'),('absorbed_hi_m3','absorbed_upper_m3')]:
            if not math.isclose(final[k],prior[oldkey],rel_tol=3e-14,abs_tol=1e-90):
                raise AssertionError('PARENT_PR127_ENDPOINT_MISMATCH')
        meta['final_endpoint_verified_against_PR127']={k:final[k] for k in ('absorbed_lo_m3','absorbed_hi_m3')}
    meta['verner_table_sha256']=table_sha
    meta['result_row_counts']={'channels':len(channels),'total_times':len(totals),'electron_spectral_bins':len(hist)}
    outdir.mkdir(parents=True,exist_ok=True)
    write_csv(outdir/'TIME_CHANNEL_TARGET.csv',channels)
    write_csv(outdir/'TIME_TOTAL.csv',totals)
    write_csv(outdir/'TIME_ELECTRON_SPECTRUM.csv',hist)
    (outdir/'RESULT.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return meta,channels,totals,hist


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-zip',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(args.source_zip,args.output)

if __name__=='__main__':main()
