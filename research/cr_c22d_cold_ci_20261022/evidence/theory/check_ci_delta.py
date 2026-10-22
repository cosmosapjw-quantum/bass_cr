"""New C22D scalar checks only; no ODE or reconstruction of old calculations.

Run once with a fresh --out directory. Existing frozen model/source files read
only. All generated artifacts are create-only and all numerical threads are1.
"""
from __future__ import annotations
import os
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_var] = "1"
import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import gamma, gammainc
from ci_finite import CCCFiniteH1CI, THRESHOLD_EV, EMAX_EV, KB_EV_K, K_CM3_S, A0_M, EV_J, ME_KG, KB_J_K

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT / "resume_c22c_20261022/recovery/restored_c22b/repository"
C22C = REPO / "research/cr_c22c_h1_excitation_20261022"
C21O = REPO / "research/cr_c21o_hheli_z2_20261021"
sys.path.insert(0, str(C21O))
from atomic_network import AtomicNetwork21


def digest(path):
    b = path.read_bytes()
    return {"path": str(path), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def save_json(path, payload):
    with path.open("x") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def independent_scaled_gl(provider, temperature_K, n=80):
    """Direct SI velocity-weighted integral after u=(E-L)/theta per interval.

    Splits only the exponentially localized u integral; differs from analytic
    J_n endpoint-basis evaluation. The finite polynomial integral beyond u80
    is bounded below in the receipt; it is not a physical cross-section tail.
    """
    theta = KB_EV_K * temperature_K
    nodes, weights = leggauss(n)
    vals = []
    omitted_bound = 0.
    for left, width, sl, sr in zip(provider.left, provider.width, provider.sigma_l, provider.sigma_r):
        factor = math.exp(-(left-THRESHOLD_EV)/theta)
        if factor == 0:
            continue
        hi = width/theta
        bounds = [0.] + [v for v in (.25,1.,4.,16.,40.,80.) if v < hi] + [min(hi,80.)]
        bounds = sorted(set(bounds))
        total = 0.
        for lo, upper in zip(bounds[:-1],bounds[1:]):
            u = .5*(lo+upper)+.5*(upper-lo)*nodes
            e_j = (left+theta*u)*EV_J
            sig_m2 = (sl+(sr-sl)*theta*u/width)*A0_M**2
            integrand = sig_m2*e_j*np.exp(-u)*(theta*EV_J)
            total += .5*(upper-lo)*float(weights@integrand)
        # Transform the independently evaluated SI integral to the provider's
        # a0^2/eV scaled moment, so prefactors can also be compared separately.
        vals.append(factor*total/(A0_M**2*EV_J**2))
        if hi>80:
            # sigma_PL <= max(sl,sr), E<=EMAX for the remaining finite segment.
            omitted_bound += factor*max(sl,sr)*EMAX_EV*theta*math.exp(-80.)
    return math.fsum(vals), omitted_bound


def sw91_gap_logq(t, *, rydberg_eV=13.605693122990):
    """SW91 Eq5 alone over its source-supported interval1..1.073Ry.

    Original threshold is1Ry; modern conversion stated explicitly rather than
    pretending CCC13.6058 and SW91 thresholds are identical.
    """
    p, theta, h = 1.127, KB_EV_K*t, .073*rydberg_eV
    a = 1.179*math.pi/rydberg_eV**p  # sigma numerical a0^2, deltaE numerical eV
    value = a*(rydberg_eV*theta**(p+1)*gamma(p+1)*gammainc(p+1,h/theta)
               +theta**(p+2)*gamma(p+2)*gammainc(p+2,h/theta))
    return (math.log(K_CM3_S)-1.5*math.log(theta)-rydberg_eV/theta+math.log(value))/math.log(10.)


def sw91_fit_logq(t):
    if not 2000 <= t <= 1e8:
        return None
    # Actual p304 Table2; CI coefficients, NOT excitation Table3 or cooling4.
    c = [-96.1443,37.9523,-7.96885,.883922,-.0534513,.00166344,-.0000208888]
    logscaled = np.polynomial.polynomial.polyval(math.log(t), c)
    return (float(logscaled)-13.605693122990/(KB_EV_K*t))/math.log(10.)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started=time.perf_counter()
    provider=CCCFiniteH1CI()
    atomic=AtomicNetwork21(electronic_isotope_equality=True)
    temps=[1.,3.,10.,100.,300.,1000.,2000.,5000.,10000.,20000.,1e8]
    rows=[]
    for t in temps:
        q=provider.evaluate(t)
        alt=provider.evaluate(t,first_gap_power=1.127)
        oracle, omission=independent_scaled_gl(provider,t)
        actual=float(np.sum(provider.interval_scaled_integrals(t)))
        # Independent Maxwell prefactor in SI, not imported K_CM3_S.
        si_rate_log=(.5*math.log(8/(math.pi*ME_KG))-1.5*math.log(KB_J_K*t)
                     +math.log(oracle*A0_M**2*EV_J**2)-THRESHOLD_EV/(KB_EV_K*t)+math.log(1e6))/math.log(10.)
        swgap=sw91_gap_logq(t)
        swfit=sw91_fit_logq(t)
        rows.append({**asdict(q),
                     "first_gap_PL_fraction":float(provider.interval_scaled_integrals(t)[0]/actual),
                     "first_gap_power_1_127_ratio_to_PL":10**(alt.log10_q_cm3_s-q.log10_q_cm3_s),
                     "oracle_log10_q":si_rate_log,
                     "oracle_log10_difference":q.log10_q_cm3_s-si_rate_log,
                     "oracle_scaled_integral_relative_difference":actual/oracle-1,
                     "oracle_unintegrated_finite_u80_relative_bound":omission/oracle,
                     "SW91_1_to_1_073Ry_only_log10_q":swgap,
                     "SW91_1_to_1_073Ry_only_ratio_to_CCC_core":10**(swgap-q.log10_q_cm3_s),
                     "SW91_full_fit_log10_q":swfit,
                     "CCC_core_ratio_to_SW91_full_fit":None if swfit is None else 10**(q.log10_q_cm3_s-swfit),
                     "log10_conditional_tail_per_hypothetical_a0sq":provider.log10_conditional_tail_per_a0sq_cap(t)})
    with (args.out/"CI_RATE_COMPARISON.csv").open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # New CI input/coverage fail-closed contracts; no repeated C22C checks.
    refusals=[]
    queries=[("bool_T",(True,),{}),("T_zero",(0.,),{}),("T_nan",(float('nan'),),{}),
             ("T_inf",(float('inf'),),{}),("T_above_domain",(1e8+1.,),{}),
             ("species_D",(300.,),{"species":"D"}),("full_physical_rate",(300.,),{"full_physical_rate":True}),
             ("untyped_full_flag",(300.,),{"full_physical_rate":1}),
             ("bool_gap_power",(300.,),{"first_gap_power":True}),
             ("gap_zero",(300.,),{"first_gap_power":0.})]
    for label,a,k in queries:
        try:provider.evaluate(*a,**k)
        except (ValueError,TypeError) as e:refusals.append({"case":label,"refused":True,"error":str(e)})
        else:refusals.append({"case":label,"refused":False})
    # Conditional detailed-balance inverse:1s atomic degeneracy2, proton1,
    # electron spin2 gives d=1. Stable Boltzmann cancellation is algebraic.
    density=[]
    planck=6.62607015e-34
    for t in [3.,10.,100.,300.,1000.,2000.,5000.,10000.,20000.]:
        theta=KB_EV_K*t
        scaled=float(np.sum(provider.interval_scaled_integrals(t)))
        logD=1.5*math.log(2*math.pi*ME_KG*KB_J_K*t/planck**2)-math.log(1e6)
        logK3=math.log(K_CM3_S)-1.5*math.log(theta)+math.log(scaled)-logD
        k3=math.exp(logK3)
        alpha=float(atomic.provider.rr('HI',t))
        density.append({"temperature_K":t,"K3_ground_finite_model_cm6_s":k3,
                        "alpha_RR_cm3_s":alpha,"ne_cm3_equal_3body_RR":alpha/k3,
                        "ne_cm3_for_3body_RR_ratio_1e_6":1e-6*alpha/k3,
                        "conditional_3body_RR_ratio_at_ne_0_01":.01*k3/alpha,
                        "Coulomb_nu_per_ne_for_assumed_lnLambda10_cm3_s":2.91e-5/theta**1.5,
                        "ground_CI_over_Coulomb_per_ne_lnLambda10":provider.evaluate(t).q_cm3_s/(2.91e-5/theta**1.5)})
    # Saved C22C states only: inspect dependencies changed by the new registry;
    # no time integration or old closure re-validation.
    reuse=[]
    sourcepins=[]
    for name in ("nominal_dark_excitation","nominal_finite_uv_excitation_flrw","nominal_finite_uv_excitation_lrs"):
        path=C22C/"analysis_v2"/(name+"_ACCEPTED.npz")
        sourcepins.append(digest(path))
        with np.load(path,allow_pickle=False) as d:
            ne=d['n_e_cm3'];ts=d['temperature_K'];nh=d['nH_ref_cm3']
            logD=1.5*np.log(2*math.pi*ME_KG*KB_J_K*ts/planck**2)-math.log(1e6)
            logK3=np.array([math.log(K_CM3_S)-1.5*math.log(KB_EV_K*t)+math.log(float(np.sum(provider.interval_scaled_integrals(t)))) for t in ts])-logD
            alpha=atomic.provider.rr('HI',ts)
            nu=2.91e-5*ne/(KB_EV_K*ts)**1.5
            support=[]
            for j,e0 in enumerate(atomic.energies_eV):
                oldeta=math.log(e0/13.6);neweta=math.log(e0/THRESHOLD_EV)
                if 0<oldeta<d['eta'][-1]:
                    at=int(np.argmin(abs(d['eta']-oldeta)))
                    support.append({"cohort_initial_eV":float(e0),"old_crossing_eta":oldeta,
                        "new_crossing_eta":neweta,"nearest_old_saved_eta":float(d['eta'][at]),
                        "nearest_old_saved_photons_per_H":float(d['UV_photons_per_H'][at,j]),
                        "interpretation":"existing accepted sample only; not new trajectory or continuous support-change bound"})
            reuse.append({"source":name,"samples":len(ts),
                "nH_ref_min_max_cm3":[float(nh.min()),float(nh.max())],
                "ne_min_max_cm3":[float(ne.min()),float(ne.max())],
                "T_min_max_K":[float(ts.min()),float(ts.max())],
                "conditional_ground_3body_to_RR_max":float(np.max(ne*np.exp(logK3)/alpha)),
                "assumed_lnLambda10_nu_over_H_min":float(np.min(nu/d['H'])),
                "support_crossing_samples":support})
    energies=np.array([13.5999,13.6,13.6029,13.6058,13.606,20.,40.,60.,100.,150.])
    oldsig=atomic.provider.sigma('HI',energies)*1e-18
    newsig=np.where(energies>=THRESHOLD_EV,oldsig,0.)
    pi_delta={"old_chi_eV":13.6,"new_chi_eV":THRESHOLD_EV,
              "delta_chi_eV":THRESHOLD_EV-13.6,
              "fractional_delta_chi":THRESHOLD_EV/13.6-1,
              "each_moving_cohort_crossing_eta_advance":math.log(THRESHOLD_EV/13.6),
              "cross_section_samples":[{"photon_eV":float(e),"old_sigma_cm2":float(o),"new_sigma_cm2":float(n)} for e,o,n in zip(energies,oldsig,newsig)],
              "PI_heat_change_eV_per_same_H_family_absorption":13.6-THRESHOLD_EV,
              "RR_export_change_eV_per_same_H_family_recombination":THRESHOLD_EV-13.6,
              "source_shape_coefficients_changed":False,
              "source_support_changed":True,
              "uniform_small_relative_rate_bound":"NOT_ESTABLISHED:100percent local rate change in a narrow support interval",
              "matched_CI_off_on_new_registry_required":True}
    report={"schema":"C22D_CI_THEORY_DELTA_NUMERICS_V1",
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "workflow":"physmath-research-loop1.0.0/approval0.2",
            "coverage":provider.coverage(),"new_ODE_runs":0,"old_ODE_reruns":0,
            "resource":{"numerical_threads":1,"affinity_observed":sorted(os.sched_getaffinity(0)),
                        "runtime_seconds":time.perf_counter()-started},
            "rate_rows":rows,"fail_closed_cases":refusals,
            "numerical_gates":{"max_abs_log10_oracle_difference":max(abs(x['oracle_log10_difference']) for x in rows),
                               "max_abs_scaled_oracle_relative_difference":max(abs(x['oracle_scaled_integral_relative_difference']) for x in rows),
                               "all_fail_closed":all(x['refused'] for x in refusals),
                               "finite_positive_logs":all(math.isfinite(x['log10_q_cm3_s']) for x in rows)},
            "SW91":{"read_scope":"original PDFp303Eq5/6,p304Table2Eq9/10 read including actual page images",
                    "Ry_eV_conversion":13.605693122990,"conversion_source":"NIST CODATA2022 R_infinity hc/e; explicitly not measured H1 ionization energy",
                    "threshold_original":"1 Ry, preserved separately from CCC13.6058eV",
                    "threshold_shape_sigma_a0sq":"1.179*pi*(E/Ry-1)^1.127 for1<=E/Ry<=1.073",
                    "full_fit_T_K":[2000.,1e8],"full_fit_cold_extrapolation":False,
                    "CI_Table2_coefficients":[-96.1443,37.9523,-7.96885,.883922,-.0534513,.00166344,-.0000208888]},
            "density_inverse_rows":density,
            "inverse_qualification":"conditional ground-only Saha-inverse of chosen finite source model; not supplied physical all-level three-body recombination/cascade provider",
            "density_pilot_guard":{"nH_ref_max_cm3":.01,"all_level_3body_physical_omission_bound":None},
            "thermalization_qualification":"lnLambda10 is an explicit diagnostic assumption; thermal Coulomb timescale does not establish electron-neutral/ion equilibration or nonthermal secondary energy-sharing closure",
            "saved_state_dependency_reuse":reuse,"PI_registry_delta":pi_delta,
            "input_source_pins":sourcepins+[digest(HERE/'ci_finite.py'),digest(HERE/'sources/CCC_TICS_1S.txt'),digest(C21O/'atomic_network.py'),digest(C21O/'vendor/atomic/r9_li_thermal_rates.py'),digest(C21O/'vendor/atomic/rr_table.dat')],
            "global_error_bound":None,
            "four_axes":{"EXECUTION":"SCALAR_CI_DELTA_ONLY;newODE0;oldODErerun0",
                         "PUBLICATION":"LOCAL_REVIEWABLE_ARTIFACTS;parent_integration_pending",
                         "BACKUP":"parent_transport_receipt_required;not_completed_by_this_script",
                         "DAG":"CI_source_energy_contract_SCOPED;new_adapter_and_new_run_next;full_radiative_thermochemical_closure_OPEN"}}
    save_json(args.out/"CI_THEORY_DELTA_NUMERICS.json",report)
    print(json.dumps({"out":str(args.out),"gates":report['numerical_gates'],"density":density,
                      "saved_dependency_reuse":reuse,"pi_registry":pi_delta},indent=2))


if __name__=="__main__":
    main()
