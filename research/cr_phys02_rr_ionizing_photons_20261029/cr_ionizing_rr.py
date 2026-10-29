#!/usr/bin/env python3
"""Source-locked finite H/He ground-RR photon emission product, never photon transport.

Reads immutable PR110 actual atomwise four-bin captures; no solver re-runs, no source
inference from moments. Physics domain: frozen 100 K H1/He4 model, 0.1-10 eV direct
low-born electron cohort, proper 0..10^10 s, fixed proper-volume density.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile
import numpy as np

SOURCE_ZIP_SHA256 = '5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58'
SOURCE_ARRAYS_SHA256 = '2c3624e4ca6d087436f79360497e75b0c84fb2c8ea6b83bb855a9a0cd0005c1d'
SOURCE_RESULT_SHA256 = 'ae8452f25958c47349d313926ef14e7ab7d78691ba6bb3b8395dc399aa49b0ce'
STORED_SOURCE_RECORD_SHA256 = '8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf'
ORIGINAL_PHYS02_NPZ_SHA256 = '7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc'
BASE = 'research/cr_low_birth_causal_rr_20261027/runs/primary_v1/'
EV_J = 1.602176634e-19
PLANCK_J_S = 6.62607015e-34
C_M_S = 299792458.
SIGMA_THOMSON_M2 = 6.6524587051e-29  # NIST CODATA 2022; not exact
BOUND_IONIZATION_EV = {'HI': 13.60, 'HeI': 24.59, 'HeII': 54.42}
CHANNELS = {'H': {'threshold_eV': 13.60, 'label': 'HII_to_HI_ground'},
            'He': {'threshold_eV': 24.59, 'label': 'HeII_to_HeI_ground'}}
TIMES_S = np.array([2.5e9,5e9,7.5e9,1.0e10], dtype=np.float64)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_pinned(zip_path: str | Path):
    raw = Path(zip_path).read_bytes()
    if sha256(raw) != SOURCE_ZIP_SHA256:
        raise ValueError('locked PR110 SOURCE ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError('source ZIP CRC mismatch')
        ar = z.read(BASE + 'ARRAYS.npz')
        re = z.read(BASE + 'RESULT.json')
        original_source_record = z.read('research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json')
    if sha256(ar) != SOURCE_ARRAYS_SHA256 or sha256(re) != SOURCE_RESULT_SHA256:
        raise ValueError('original atomwise array or outcome SHA256 mismatch')
    result=json.loads(re)
    if result.get('unit') != 'CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1':
        raise ValueError('wrong source model')
    if sha256(original_source_record) != STORED_SOURCE_RECORD_SHA256 or result['input']['sha256'] != STORED_SOURCE_RECORD_SHA256:
        raise ValueError('wrong PHYS02 actual source JSON identity')
    if result['input']['source_payload_sha256'] != ORIGINAL_PHYS02_NPZ_SHA256:
        raise ValueError('wrong PHYS02 original fullBED NPZ lineage identity')
    if result['input']['selected_tag'] != 'direct_0p1_10':
        raise ValueError('wrong cohort; high-born 10eV projection is not direct low')
    if result['context']['history_outside'] not in ('UNKNOWN','unknown',None):
        raise ValueError('unqualified history extension')
    if result['scope'].find('fixed100K') < 0:
        raise ValueError('wrong thermal model')
    with np.load(io.BytesIO(ar), allow_pickle=False) as n:
        data={k:n[k].copy() for k in n.files}
    if not np.array_equal(data['times_s'],TIMES_S):
        raise ValueError('different observation clock')
    return result,data

def validate_finite_nonnegative(name, a):
    if not np.all(np.isfinite(a)) or not np.all(a>=0):
        raise ValueError(f'{name}: invalid nonfinite or negative physical event measure')

def generate(result, data, energy_step_eV=0.5):
    if energy_step_eV <= 0 or not math.isfinite(energy_step_eV):
        raise ValueError('positive finite spectral-bin width required')
    if abs(energy_step_eV - 0.5) > 1e-12:
        raise ValueError('frozen 0.5 eV spectral grid, do not silently widen')
    T = data['times_s']
    if T.shape!=(4,) or not np.array_equal(T,TIMES_S):
        raise ValueError('frozen four-endpoint proper-time grid mismatch')
    if result.get('input',{}).get('selected_tag')!='direct_0p1_10' or 'fixed100K' not in result.get('scope',''):
        raise ValueError('source partition or prescribed bath differs')
    ed=np.concatenate(([0.],T))
    dt=np.diff(ed)
    n_b = result['inventory']['values']['n_b_m3']
    n_e = result['inventory']['values']['n_e_m3']
    if n_b <= 0 or n_e <= 0:
        raise ValueError('baryon/electron densities must be positive')
    e = data['E_eV']
    validate_finite_nonnegative('born electron energy', e)
    if len(e)!=3200 or e.min() <= 0.1 or e.max()>10.0:
        raise ValueError('unexpected discrete low cohort')
    edges=np.arange(13.,36.+1e-9,energy_step_eV, dtype=np.float64)
    if not (edges[0]<13.6 and edges[-1]>34.59):
        raise AssertionError('frozen photon edge coverage')
    csv_rows=[]
    raw_weights=[]
    counts={}
    energies={}
    photon_evs={}
    for label, metadata in CHANNELS.items():
        eg=data[f'photon_{label}_energy_eV']
        capture=data[f'capture_{label}_bins_m3']
        cum=data[f'capture_{label}_prefix_m3']
        validate_finite_nonnegative(f'{label} photon energy',eg)
        validate_finite_nonnegative(f'{label} photon capture',capture)
        validate_finite_nonnegative(f'{label} photon cumulative',cum)
        if eg.shape !=(3200,) or capture.shape!=(4,3200) or cum.shape!=(4,3200):
            raise ValueError('wrong original result shape')
        if np.max(np.abs(eg-(e+metadata['threshold_eV'])))>2e-12:
            raise ValueError('event photon E+threshold law violated')
        if not np.allclose(np.cumsum(capture,axis=0),cum,rtol=2e-12,atol=0):
            raise ValueError('nonadditive or overlapping photon claims')
        for j,p in enumerate(result['observation_bins']):
            c=p['channels'][label]
            if abs(math.fsum(capture[j])-c['capture_number_m3'])>max(1e-290,3e-12*c['capture_number_m3']):
                raise ValueError('raw atom counts disagree with source summary')
            E=np.dot(eg,capture[j]); ref=c['retained_photon_energy_eV_m3']
            if abs(E-ref)>max(1e-290,3e-12*ref):
                raise ValueError('raw atomic photon energy disagrees with source summary')
            if c['retained_photon_number_m3']!=c['capture_number_m3']:
                raise ValueError('one photon per event identity invalid')
            if not (abs(c['capture_kinetic_eV_m3'] - c['binding_energy_change_eV_m3'] - ref)
                     <= max(1e-290,3e-12*ref)):
                raise ValueError('event energy ledger not closed')
        for j in range(4):
            hist_N=np.histogram(eg,bins=edges,weights=capture[j])[0]
            hist_U=np.histogram(eg,bins=edges,weights=capture[j]*eg*EV_J)[0]
            if abs(math.fsum(hist_N)-math.fsum(capture[j]))>max(1e-290,2e-12*math.fsum(capture[j])):
                raise ValueError('photon histogram loses events')
            if abs(math.fsum(hist_U)-math.fsum(capture[j]*eg*EV_J))>max(1e-290,2e-12*math.fsum(capture[j]*eg*EV_J)):
                raise ValueError('photon histogram loses radiation energy')
            for k in range(len(hist_N)):
                csv_rows.append(dict(channel=label, time_bin=j+1,
                    t_start_s=float(ed[j]),t_end_s=float(ed[j+1]),
                    E_low_eV=float(edges[k]), E_high_eV=float(edges[k+1]),
                    N_ph_m3=float(hist_N[k]), U_ph_J_m3=float(hist_U[k]),
                    mean_rate_m3_s=float(hist_N[k]/dt[j]),
                    bin_density_m3_eV=float(hist_N[k]/energy_step_eV),
                    nu_low_Hz=float(edges[k]*EV_J/PLANCK_J_S),
                    nu_high_Hz=float(edges[k+1]*EV_J/PLANCK_J_S),
                    bin_density_m3_Hz=float(hist_N[k]*PLANCK_J_S/(energy_step_eV*EV_J))))
        photon_evs[label]=eg
        raw_weights.append(capture)
        counts[label]=capture.sum(axis=1)
        energies[label]=(capture*eg[None,:]).sum(axis=1)*EV_J
    total=np.zeros(4)
    for v in counts.values():total+=v
    # In the frozen model, cumulative capture C(t) is monotone, so the electron-column
    # perturbation (from capture only) is bounded by the four endpoint Riemann sums.
    prefix=np.cumsum(total)
    lower_counts=np.concatenate(([0.],prefix[:-1]))
    beta=SIGMA_THOMSON_M2*C_M_S
    left=math.fsum(dt*lower_counts)
    right=math.fsum(dt*prefix)
    column_signed_tau=(-beta*right,-beta*left)
    assert column_signed_tau[0] <= column_signed_tau[1] <=0
    direct_tau0=beta*n_e*T[-1]
    # DO NOT compute ne+delta_ne: delta_ne is below binary64 ulp of frozen ne.
    ionization_threshold_counts={ion: {c:float(np.sum(w[:,photon_evs[c]>=thr]))
                               for c,w,thr in [(c,raw_weights[list(CHANNELS).index(c)],v) for c in CHANNELS]}
                               for ion,v in BOUND_IONIZATION_EV.items()}
    rows=[]
    for j in range(4):
        for ch in CHANNELS:
            rows.append({'time_bin':j+1,'channel':ch, 'interval_s':[float(ed[j]),float(ed[j+1])],
            'N_ph_m3':float(counts[ch][j]),'U_ph_J_m3':float(energies[ch][j]),
            'mean_rate_m3_s':float(counts[ch][j]/dt[j]),
            'N_ph_per_baryon':float(counts[ch][j]/n_b),
            'U_ph_J_per_baryon':float(energies[ch][j]/n_b)})
    summary={
       'schema':'BASS_CR_RR_PHYSICAL_PHOTON_SOURCE_V1',
       'authority':{'source_project':'cosmosapjw-quantum/bass_cr','source_PR':110,
         'source_HEAD':'616b166fa0108ca35defece3f8c9d99fc79895cb',
         'source_ZIP_SHA256':SOURCE_ZIP_SHA256,'source_arrays_SHA256':SOURCE_ARRAYS_SHA256,
         'source_RESULT_SHA256':SOURCE_RESULT_SHA256,
         'retained_PHYS02_source_record_SHA256':STORED_SOURCE_RECORD_SHA256,
         'retained_fullBED_NPZ_SHA256_lineage_only':ORIGINAL_PHYS02_NPZ_SHA256},
       'scope':{'physical_data':True,'conditional_frozen_100K_model':True,
        'gas_rest_frame':True,'proper_seconds_0_to_T':True,'fixed_proper_volume_density':True,
        'birth_tag':'direct_0p1_10','ground_RR_only':True,'photon_transport':False,
        'this_is_derived_from_PR110_photon_event_atoms':True,
        'observed_sky':False,'full_exclusive_He_double_event_kernel':False,
        'isotropic_ground_state_zero_recoil':True,'absolute_volume_m3':None},
       'constants':{'eV_J':EV_J,'h_J_s':PLANCK_J_S,'c_m_s':C_M_S,
        'sigma_T_m2_CODATA2022':SIGMA_THOMSON_M2,'n_e_m3':n_e,'n_b_m3':n_b},
       'time_grid_s':ed.tolist(), 'energy_bin_edges_eV':edges.tolist(),
       'photon_rows':rows,
       'ionizing_energy_gate_counts_m3':ionization_threshold_counts,
       'totals':{'N_H_m3':float(sum(counts['H'])),'N_He_m3':float(sum(counts['He'])),
         'N_all_m3':float(sum(total)), 'U_H_J_m3':float(sum(energies['H'])),
         'U_He_J_m3':float(sum(energies['He'])),
         'U_all_J_m3':float(sum(energies['H']+energies['He'])),
         'HeI_capable_fraction_of_emitted':float(sum(counts['He'])/sum(total)),
         'source_diagnostics':{'total_ionizing_HI_potential_m3':float(sum(total)),
          'HeI_potential_m3':float(sum(counts['He'])),
          'HeII_potential_m3':0.0}},
       'thomson_signed_RR_only':{'frozen_baseline_tau0':direct_tau0,
           'integral_capture_column_bracket_m3_s':[left,right],
           'delta_tau_bracket':list(column_signed_tau),
           'meaning':'fixed-proper-volume, fixed-ne baseline, first-order RR capture response ONLY; not cosmological tau or transported photons; endpoint monotonicity bracket'},
       'scientific_gates':{'full_parent_ion_chemistry':False, 'case_A_B_transport':False,
           'intervening_absorption':False,'photon_escapes':None,
           'real_He_exclusive_joint_kernel':None,'actual_exclusive_He_K':None,
           'physical_full_native25':False, 'L4':False, 'production':False}
    }
    arrays={'photon_H_eV':photon_evs['H'],'photon_He_eV':photon_evs['He'],
       'photon_H_freq_Hz':photon_evs['H']*EV_J/PLANCK_J_S,
       'photon_He_freq_Hz':photon_evs['He']*EV_J/PLANCK_J_S,
       'capture_H_bins_m3':raw_weights[0],'capture_He_bins_m3':raw_weights[1],
       'time_edges_s':ed, 'hist_edges_eV':edges}
    return summary,csv_rows,arrays

def save(summary,rows,arrays,out: Path):
    out.mkdir(parents=True,exist_ok=True)
    (out/'PHOTON_RESULT.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    with (out/'PHOTON_SPECTRUM.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    np.savez_compressed(out/'PHOTON_ATOMWISE.npz',**arrays)

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--source',required=True,help='original immutable PR110 SOURCE zip')
    cli.add_argument('--out',required=True)
    a=cli.parse_args()
    result,arr=read_pinned(a.source)
    summ,rows,raw=generate(result,arr)
    save(summ,rows,raw,Path(a.out))
    print(json.dumps({'status':'PASS_SCOPED','N_ph_m3':summ['totals']['N_all_m3'],
       'U_ph_J_m3':summ['totals']['U_all_J_m3'], 'HeI_capable_fraction':summ['totals']['HeI_capable_fraction_of_emitted'],
       'signed_tau_bracket':summ['thomson_signed_RR_only']['delta_tau_bracket'],
       'rows':len(rows)}))
