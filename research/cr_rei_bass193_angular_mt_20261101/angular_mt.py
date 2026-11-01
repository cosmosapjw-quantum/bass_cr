#!/usr/bin/env python3
"""BASS193 optional p-H+ charge-labelled linear drag: 2025 published angular-moment fit.

NOT a reconstruction of Schultz et al. (2016) original DCS data.
No new REI evolution, Bianchi finite-tilt source, or elastic channel.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path
from scipy.integrate import quad
import numpy as np

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'cr_rei_bass193_low_energy_cx_20261101'
sys.path.insert(0, str(PRIOR))
import source_cx_screen as old

SOURCE_SHA = old.SOURCE_SHA256
PARENT_CSV_SHA = 'afb5cb0fab472421026254e66e35c37fb01e86af97286e756845f9035908eb99'
LO, HI, SPLIT = old.V_MIN_CM_S, old.V_MAX_CM_S, 16e5

# Titova, Izmodenov & Korolkov (2025), Appendix A7, explicitly Model 6:
# the expression is for sigma_mt,CX/2, fitted to Schultz (2016) angular moments.
# Despite the paper's "sigma_tot,Hp" label at A7, section A.1 describes CX.
# g in cm/s; all a coefficients exactly as published (rounded fit coefficients).
A7_LOW = (7.16911227e-8, 4.27710011e-8, 8.90798298e-1, 3.01412164e-1)
A7_HIGH = (1.10302752e-4, 9.04905679e-6, 1.04605847, 8.06905161e-1)
BASIS = "outgoing_charged_particle_cm_scattering_angle"
FITS_URL = old.FIT_URL

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()

def sigma_cx_mt_fit(g):
    """Published 2025 A7 fit to ANGULAR MOMENT; not the original DCS integration."""
    if not math.isfinite(g) or g <= 0: raise ValueError("speed must be positive")
    aa,bb,cc,dd = A7_LOW if g <= SPLIT else A7_HIGH
    damp = -math.expm1(-cc / g)
    return 2.0 * (aa-bb*math.log(g))**2 * damp**dd

def sigma_cx_mt_pi(g):
    """Charge-labelled CM theta=pi approximation: angular moment = 2 total."""
    return 2.0 * old.sigma_cx_cm2(g)

def rate_integral(T, kind):
    """Maxwellian zero-drift 3-200 km/s: event <sigma*g> or linear drag K.

    K = 2/(3a^2) <sigma_mt*g^3>, where
    f_rel(w;U) = pi^(-3/2) a^(-3) exp(-|w-U|^2/a^2).
    """
    a = old.thermal_speed_cm_s(T)
    if kind == 'mt_a7':
        f, weight, power = sigma_cx_mt_fit, 8*a/(3*math.sqrt(math.pi)), 5
    elif kind == 'mt_pi':
        f, weight, power = sigma_cx_mt_pi, 8*a/(3*math.sqrt(math.pi)), 5
    elif kind == 'event_a4':
        f, weight, power = old.sigma_cx_cm2, 4*a/math.sqrt(math.pi), 3
    else:
        raise ValueError(kind)
    def integrand(x):
        if x <= 0: return 0.
        return weight * (x**power) * math.exp(-x*x) * f(x*a)
    bounds = (LO, SPLIT, HI) if kind == 'mt_a7' else (LO, HI)
    total = 0.
    for low, high in zip(bounds[:-1], bounds[1:]):
        value, error = quad(integrand, low/a, high/a,
                            epsabs=1e-25, epsrel=3e-10, limit=300)
        if error > max(1e-19, 1e-8 * abs(value)):
            raise FloatingPointError(f"quadrature uncertainty {kind} {T} {error}")
        total += value
    return total

def geometric_maxwell_drag_support(T):
    """Constant-sigma g^3-weight measure, NOT a true cross-section coverage bound."""
    a = old.thermal_speed_cm_s(T)
    def survivor(g):
        z = (g/a)**2
        return math.exp(-z) * (1+z+0.5*z*z) if z < 700 else 0.
    return survivor(LO)-survivor(HI)

def charged_vs_nuclear_kernel(mu, sigma_el, sigma_cx_charge):
    """Illustrate charge-frame DCS vs nuclear-labelled angle for exchange.

    mu=cos(theta_charged); cos(theta_nuclear)=-mu for resonant CX.
    """
    return (1-mu)*(sigma_el(mu)+sigma_cx_charge(mu))

def original_input(source_zip):
    if sha(source_zip) != SOURCE_SHA:
        raise ValueError("REI source ZIP mismatch")
    rows = old.compute(source_zip)
    with tempfile.TemporaryDirectory() as td:
        f, _ = old.save(rows, td)
        if sha(f) != PARENT_CSV_SHA:
            raise ValueError("PR154 derived CSV content mismatch on original replay")
        if f.read_bytes() != (PRIOR/'results/BASS193_H_HPLUS_CX_SOURCE_CONDITIONAL_192.csv').read_bytes():
            raise ValueError("PR154 source CSV not byte-exact")
    return rows

def fit_diagnostics():
    v = np.geomspace(LO,HI,501)
    ratios = np.array([sigma_cx_mt_fit(float(x))/sigma_cx_mt_pi(float(x)) for x in v])
    jump = sigma_cx_mt_fit(SPLIT*(1+1e-8))/sigma_cx_mt_fit(SPLIT)-1
    return dict(violating_sample_count=int(np.sum(ratios > 1+1e-12)),
                sampled_points=len(v),
                ratio_max=float(np.max(ratios)),
                ratio_min=float(np.min(ratios)),
                first_violation_km_s=float(v[np.flatnonzero(ratios > 1+1e-12)[0]]/1e5) if np.any(ratios > 1+1e-12) else None,
                sixteen_km_s_jump_relative=float(jump),
                physical_bound="0 <= sigma_mt <= 2 sigma_total, exact DCS moment; A7/A4 separate rounded fits do NOT obey globally")

def calculate(source_zip):
    source = original_input(source_zip)
    records = []
    for r in source:
        t = r['T_saved_K']
        k1 = rate_integral(t,'mt_a7')
        kpi = rate_integral(t,'mt_pi')
        kevent = rate_integral(t,'event_a4')
        if abs(kevent/r['kcx_fit_window_cm3_s']-1) > 3e-9:
            raise ValueError("source event crosswalk mismatch")
        n_i, n_n = r['nHII_cm3'],r['nHI_cm3']
        mu, mp, mn = old.MU_G,old.MP_G,old.MH_G
        gamma = mu*n_i*n_n*k1
        nu_i = mu/mp*n_n*k1
        nu_n = mu/mn*n_i*k1
        nu_rel = nu_i+nu_n
        a = old.thermal_speed_cm_s(t)
        records.append({
          'interval':r['interval'],'z_low':r['z_low'],'proper_interval_s':r['proper_interval_s'],
          'T_saved_K':t,'nHII_cm3':n_i,'nHI_cm3':n_n,'x_HII_end':r['x_HII_end'],
          'H_effective_per_s':r['H_effective_per_s'],
          'E_cm_thermal_eV':old.KB_ERG_K*t/old.EV_ERG,
          'k_mt_CX_A7_window_cm3_s':k1,
          'k_mt_CX_piA4_window_cm3_s':kpi,
          'k_event_CX_A4_window_cm3_s':kevent,
          'k_mt_A7_over_piA4':k1/kpi,
          'k_mt_A7_over_eventA4':k1/kevent,
          'maxwell_drag_geom_window_fraction':geometric_maxwell_drag_support(t),
          'ion_neutral_drag_gamma_g_cm_minus3_s_minus1':gamma,
          'nu_ion_linear_drag_s_minus1':nu_i,
          'nu_neutral_linear_drag_s_minus1':nu_n,
          'nu_rel_linear_drag_s_minus1':nu_rel,
          'nu_rel_over_H_effective':nu_rel/r['H_effective_per_s'],
          'sigma_mt_at_vth_cm2':sigma_cx_mt_fit(a) if LO<=a<=HI else '',
          'chemistry_net_HI_s':0.,'chemistry_net_HII_s':0.,
          'chemistry_net_electron_s':0.,'direct_binding_energy_erg_per_H_s':0.,
          'frozen_not_evolved':True,
          'sigma_elastic_mt_status':'NOT_AVAILABLE_ORIGINAL_DCS'
        })
    return records

def summarize(rows):
    def a(k): return np.array([r[k] for r in rows],float)
    imax=int(np.argmax(a('nu_rel_over_H_effective')))
    dg=fit_diagnostics()
    return dict(schema='BASS_CR_REI_BASS193_CX_A7_LINEAR_DRAG_DIAGNOSTIC_V1',
        authority='SOURCE_MATCHED_EXPLORATORY_PUBLISHED_ANGULAR_MOMENT_FIT_NOT_ORIGINAL_DCS',
        source_zip_sha256=SOURCE_SHA,parent_csv_sha256=PARENT_CSV_SHA,
        paper='Titova Izmodenov Korolkov 2025 PASA Appendix A7 (CX momentum/2), A4 (CX total); underlying Schultz et al 2016',
        paper_url=FITS_URL,cm_angle_definition=BASIS,
        admitted_speed_km_s=[3,200],linear_drift_expansion='leading order O(U) with equal T_i=T_n=T_BASS; O(U^3) discarded',
        rows=len(rows),
        min_T_K=float(np.min(a('T_saved_K'))),max_T_K=float(np.max(a('T_saved_K'))),
        k_mt_A7_over_pi_min=float(np.min(a('k_mt_A7_over_piA4'))),
        k_mt_A7_over_pi_max=float(np.max(a('k_mt_A7_over_piA4'))),
        k_mt_A7_over_pi_median=float(np.median(a('k_mt_A7_over_piA4'))),
        max_nu_rel_over_H=float(np.max(a('nu_rel_over_H_effective'))),
        max_nu_rel_over_H_interval=imax,max_nu_rel_over_H_z=float(rows[imax]['z_low']),
        drag_geom_fraction_ge_0p95=int(np.sum(a('maxwell_drag_geom_window_fraction')>=0.95)),
        drag_geom_fraction_lt_0p5=int(np.sum(a('maxwell_drag_geom_window_fraction')<0.5)),
        original_dcs_retrieved=False,
        elastic_angle_data_retrieved=False,
        joint_cr_elastic_mt=False,fit_checks=dg,
        reactor_tilt_and_separate_species_velocity='NOT_SOURCE_VERIFIED',
        source_conditional_transport_only=True,
        source_driven_dynamical_IGM=False,chemistry_source='ZERO',
        physical_drag_to_REI_CROFF=False,
        central_dag='28/88_REPORTED_UNCHANGED',working_dag='33/88_REPORTED_UNCHANGED',
        bass_cr_extension_dag='0/3_UNCHANGED',
        production='HOLD',no_merge=True,no_force_push=True,auto_next_node=False)

def save(rows, outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    csvpath=outdir/'BASS193_CX_A7_LINEAR_DRAG_192.csv'
    with csvpath.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k:(format(v,'.17g') if type(v) is float else v) for k,v in r.items()})
    data=summarize(rows)
    data['csv_sha256']=sha(csvpath)
    result=outdir/'RESULT.json'
    result.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    return csvpath,result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--out',default=str(HERE/'results'),type=Path)
    args=ap.parse_args()
    rows=calculate(args.source)
    files=save(rows,args.out)
    print(json.dumps(summarize(rows),sort_keys=True))
    print("OUTPUT",[(str(p),sha(p)) for p in files])

if __name__=='__main__': main()
