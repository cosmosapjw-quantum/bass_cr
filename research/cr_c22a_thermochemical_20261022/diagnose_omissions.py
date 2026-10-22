#!/usr/bin/env python3
"""Evaluate selected omitted processes on a saved C22A trajectory, with ODE0.

This is a source-bound trajectory diagnostic, not a self-consistent alternate
solution or a global error bound. Out-of-fit-domain rates remain unavailable;
neither extrapolation nor replacement of unavailable coefficients by zero is
performed. Integrals use only adjacent saved points with available rates.
"""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.constants import Boltzmann, Planck, c, electron_mass

HERE = Path(__file__).resolve().parent
C21O = HERE.parent / "cr_c21o_hheli_z2_20261021"
sys.path.insert(0, str(C21O))
from atomic_network import AtomicNetwork21, CHANNEL_NAMES
from rr_energy_moment import rr_energy_factor

EV_ERG = 1.602176634e-12
KB_CGS = Boltzmann * 1e7
KB_EV_K = KB_CGS / EV_ERG
ME_CGS = electron_mass * 1e3
C_CGS = c * 1e2
H_CGS = Planck * 1e7
SIGMA_T_CM2 = 6.6524587051e-25  # Same frozen constant as parent lrs_boltzmann.py.
RADIATION_A_CGS = 8*np.pi**5*KB_CGS**4/(15*H_CGS**3*C_CGS**3)
TCMB0_K = 2.7255  # Explicit diagnostic input, not fitted to this trajectory.

SOURCES = {
    "HG1997": {
        "citation": "Hui & Gnedin 1997, MNRAS292,27, AppendixA; Eq.(2)",
        "url": "https://arxiv.org/abs/astro-ph/9612232",
        "doi": "10.1093/mnras/292.1.27",
        "retrieval": "primary full text read through Exa 2026-10-22",
    },
    "Grackle_source_crosscheck": {
        "url": "https://github.com/grackle-project/grackle/blob/main/src/clib/rate_functions.c",
        "git_blob_sha": "dfbab661e7c45981eed750baebff140849917152",
        "scope": "official code inspected; HG formula is primary for H CI/excitation below",
    },
    "VF_RR": {
        "url": "https://www.pa.uky.edu/~verner/rec.html",
        "table_url": "https://www.pa.uky.edu/~verner/dima/rec/table1.dat",
        "provider_sha256": "74b2a8c30c62f4a50e7c5c4bcf92cb159549ffcb904a3e423a793169c2f2bb27",
        "energy_moment": "L_RR=k_B*T*alpha*(3/2+dln(alpha)/dln(T)); fit derivative accuracy not certified",
    },
    "Compton": {
        "url": "https://arxiv.org/abs/astro-ph/9612232",
        "location": "AppendixA nonrelativistic Compton heating/cooling",
        "formula": "Q_C=4*sigma_T*c*a_R*Tgamma^4*n_e*k_B*(Tgamma-T)/(m_e*c^2)",
        "adopted_CMB_temperature_K": "2.7255*(1+z)",
        "Thomson_constant_cm2": SIGMA_T_CM2,
        "constant_provenance": "same numeric sigma_T as frozen C21O donor lrs_boltzmann.py; scipy.constants for exact SI c,h,k and CODATA electron mass",
    },
}


def h_collisional_ionization_cm3_s(temperature_K):
    """HG1997 AppendixA fit to Lotz; quoted domain 1e4..1e9 K, 3% fit.

    CI=21.11 T^-1.5 exp(-lambda/2) lambda^-1.089
       /[1+(lambda/0.354)^0.874]^1.101, lambda=2*157807/T.
    The prefactor carries cm^3 s^-1 K^(3/2). NaN means unavailable.
    """
    t=np.asarray(temperature_K,dtype=float)
    valid=np.isfinite(t)&(t>=1e4)&(t<=1e9)
    result=np.full(t.shape,np.nan)
    tv=t[valid]; lam=2*157807./tv
    result[valid]=21.11*tv**(-1.5)*np.exp(-lam/2)*lam**(-1.089)/(1+(lam/.354)**.874)**1.101
    return result,valid


def h_excitation_cooling_erg_cm3_s(temperature_K):
    """HG1997 AppendixA Black/Cen H line cooling; 5e3..5e5 K, ~10% fit."""
    t=np.asarray(temperature_K,dtype=float)
    valid=np.isfinite(t)&(t>=5e3)&(t<=5e5)
    result=np.full(t.shape,np.nan)
    tv=t[valid]
    result[valid]=7.5e-19*np.exp(-.75*157807./tv)/(1+np.sqrt(tv/1e5))
    return result,valid


def _safe_ratio(numerator,denominator):
    result=np.full(np.shape(numerator),np.nan,dtype=float)
    valid=np.isfinite(numerator)&np.isfinite(denominator)&(denominator>0)
    np.divide(numerator,denominator,out=result,where=valid)
    return result


def _stats(values):
    values=np.asarray(values); values=values[np.isfinite(values)]
    return {"minimum":float(values.min()),"maximum":float(values.max()),
            "maximum_absolute":float(np.max(abs(values)))} if values.size else {
                "minimum":None,"maximum":None,"maximum_absolute":None}


def _valid_integral(t,y,valid):
    """No bridging of unavailable intervals; report integration coverage."""
    dt=np.diff(t)
    adjacent=valid[:-1]&valid[1:]&np.isfinite(y[:-1])&np.isfinite(y[1:])
    duration=float(np.sum(dt[adjacent]))
    total=float(t[-1]-t[0])
    value=float(np.sum(.5*(y[1:][adjacent]+y[:-1][adjacent])*dt[adjacent])) if np.any(adjacent) else None
    return {"value":value,"available_interval_duration_s":duration,
            "total_duration_s":total,"available_duration_fraction":duration/total,
            "available_adjacent_intervals":int(np.sum(adjacent)),
            "total_intervals":int(len(dt)),
            "availability":"AVAILABLE_FULL_SAVED_GRID" if np.all(adjacent) else "OPEN_PARTIAL_TEMPERATURE_COVERAGE" if np.any(adjacent) else "OPEN_NO_VALID_ADJACENT_INTERVALS",
            "quadrature":"trapezoid_on_saved_samples_only; no convergence_bound"}


def _normalized(value,denominator):
    return float(value/denominator) if value is not None and denominator>0 else None


def diagnose_history(history):
    """Return (JSON-safe report, numpy arrays) for the requested NPZ contract."""
    required=("eta","z","H","nH_ref_cm3","n_e_cm3","temperature_K",
              "atomic_abundance_per_Href","atomic_state_labels",
              "thermal_energy_eV_per_H","proper_elapsed_s")
    missing=[key for key in required if key not in history]
    if missing:
        raise ValueError("HISTORY_FIELDS_MISSING: "+",".join(missing))
    values={key:np.asarray(history[key]) for key in required}
    t=np.asarray(values["proper_elapsed_s"],dtype=float)
    if t.ndim!=1 or len(t)<2 or not np.isfinite(t).all() or not np.all(np.diff(t)>0):
        raise ValueError("PROPER_TIME_MUST_BE_FINITE_STRICTLY_INCREASING")
    size=len(t)
    for key in ("eta","z","H","nH_ref_cm3","n_e_cm3","temperature_K","thermal_energy_eV_per_H"):
        if values[key].shape!=(size,) or not np.isfinite(values[key]).all():
            raise ValueError("HISTORY_SHAPE_OR_FINITE: "+key)
    temp=np.asarray(values["temperature_K"],dtype=float)
    ne=np.asarray(values["n_e_cm3"],dtype=float)
    nref=np.asarray(values["nH_ref_cm3"],dtype=float)
    h=np.asarray(values["H"],dtype=float)
    uth=np.asarray(values["thermal_energy_eV_per_H"],dtype=float)
    if np.any(temp<=0) or np.any(ne<0) or np.any(nref<=0) or np.any(h<=0) or np.any(uth<=0):
        raise ValueError("NONPHYSICAL_HISTORY_FOR_OMISSION_DIAGNOSTIC")
    labels=[str(x) for x in values["atomic_state_labels"]]
    abundance=np.asarray(values["atomic_abundance_per_Href"],dtype=float)
    if abundance.shape!=(21,size) or len(labels)!=21 or len(set(labels))!=21 or not np.isfinite(abundance).all():
        raise ValueError("ATOMIC_HISTORY_SHAPE_OR_LABELS")
    net=AtomicNetwork21(electronic_isotope_equality=True)
    if set(labels)!=set(net.state_labels):
        raise ValueError("ATOMIC_STATE_IDENTITY_MISMATCH")
    ordered=abundance[[labels.index(label) for label in net.state_labels]]
    # Match the preregistered finite-numerical population gate. Keep all signed
    # raw values: replacing a tolerated negative residual by zero would change
    # the saved trajectory and hide this diagnostic's numerical limitation.
    scaled=ordered/net.scales[:,None]
    if np.any(scaled < -2e-9):
        raise ValueError("NEGATIVE_POPULATION_BELOW_CONTRACT_GATE; no clipping")
    population_residual={
        "minimum_abundance_per_Href":float(np.min(ordered)),
        "minimum_population_scaled":float(np.min(scaled)),
        "negative_population_samples":int(np.sum(ordered<0)),
        "accepted_scaled_lower_bound":-2e-9,
        "policy":"retain_signed_raw_values_no_clipping; negative_diagnostic_contributions_are_numerical_residuals_not_physical_negative_rates",
        "species_with_negative_residuals":[
            {"label":net.state_labels[i],"minimum_abundance_per_Href":float(np.min(ordered[i])),
             "minimum_population_scaled":float(np.min(scaled[i]))}
            for i in range(21) if np.any(ordered[i]<0)],
    }
    # Same electronic-isotope equality as selected model, explicitly retained.
    neutral_h=sum(ordered[net.blocks[name][0]] for name in ("H1","D","T"))
    rr=np.zeros(size)
    rrvalid=(temp>=3)&(temp<=1e9)
    rr[~rrvalid]=np.nan
    for lower,upper,ch in net.edges:
        pars=net.provider.rows[CHANNEL_NAMES[ch]]["RR"]
        alpha=np.asarray(net.provider.rr(CHANNEL_NAMES[ch],temp[rrvalid]))
        capture=KB_EV_K*temp[rrvalid]*rr_energy_factor(pars,temp[rrvalid])
        rr[rrvalid]+=ne[rrvalid]*ordered[upper,rrvalid]*alpha*capture
    cirate,civalid=h_collisional_ionization_cm3_s(temp)
    ci_events=cirate*ne*neutral_h  # events per Href per proper second.
    ci_loss=13.6*ci_events  # eV/Href/s; model threshold, not extra radiation loss.
    exc_coeff,excvalid=h_excitation_cooling_erg_cm3_s(temp)
    exc_loss=exc_coeff*ne*neutral_h/EV_ERG
    tgamma=TCMB0_K*(1+np.asarray(values["z"],dtype=float))
    if np.any(tgamma<=0):
        raise ValueError("NONPOSITIVE_DIAGNOSTIC_CMB_T")
    # Adopted applicability screen: kBT/(m_e c^2)<=0.01; this is a diagnostic
    # regime selector, not a certified error estimate for the omitted terms.
    rel=np.maximum(KB_CGS*temp,KB_CGS*tgamma)/(ME_CGS*C_CGS**2)
    compvalid=rel<=.01
    qcomp=4*SIGMA_T_CM2*C_CGS*RADIATION_A_CGS*tgamma**4*ne*KB_CGS*(tgamma-temp)/(ME_CGS*C_CGS**2)
    qcomp[~compvalid]=np.nan
    comp=qcomp/(nref*EV_ERG)
    comp[~compvalid]=np.nan
    shear=np.asarray(history["s"],dtype=float) if "s" in history else None
    geometry=("FLRW_shear_zero_saved_history" if shear is not None and shear.shape==(size,) and np.all(shear==0)
              else "LRS_or_unspecified; additional_imposed_isotropic_blackbody_diagnostic")
    if "energy_total_eV_per_H" in history:
        initial_energy=float(np.asarray(history["energy_total_eV_per_H"])[0])
        energy_denominator="energy_total_eV_per_H[0]"
    else:
        energy_keys=("thermal_energy_eV_per_H","ionization_energy_eV_per_H","UV_energy_eV_per_H")
        initial_energy=sum(float(np.asarray(history[key])[0]) for key in energy_keys) if all(key in history for key in energy_keys) else None
        energy_denominator="sum_initial_thermal_chemical_UV" if initial_energy is not None else "UNAVAILABLE; thermal_denominator_only"
    arrays={"eta":values["eta"],"z":values["z"],"proper_elapsed_s":t,
            "included_RR_cooling_eV_per_Href_s":rr,
            "H_CI_events_per_Href_s":ci_events,"H_CI_thermal_loss_eV_per_Href_s":ci_loss,
            "H_excitation_thermal_loss_eV_per_Href_s":exc_loss,
            "CMB_Compton_gas_heating_eV_per_Href_s":comp,
            "CMB_Compton_Q_erg_cm3_s":qcomp,
            "CMB_temperature_diagnostic_K":tgamma,
            "H_CI_valid_temperature":civalid,"H_excitation_valid_temperature":excvalid,
            "CMB_Compton_valid_nonrelativistic":compvalid}
    reports={}
    for name,rate,valid in (("H_collisional_ionization",ci_loss,civalid),
                            ("H_collisional_excitation",exc_loss,excvalid),
                            ("isotropic_CMB_Compton",comp,compvalid)):
        signed=_valid_integral(t,rate,valid)
        absolute=_valid_integral(t,abs(rate),valid)
        ratio_hu=_safe_ratio(rate,h*uth)
        ratio_rr=_safe_ratio(rate,rr)
        arrays[name+"_over_H_Uthermal"]=ratio_hu
        arrays[name+"_over_included_RR_cooling"]=ratio_rr
        reports[name]={
            "availability":signed["availability"],
            "valid_sample_count":int(np.sum(valid)),"total_sample_count":size,
            "rate_eV_per_Href_s":_stats(rate),
            "rate_over_H_Uthermal":_stats(ratio_hu),
            "rate_over_included_RR_cooling":_stats(ratio_rr),
            "integrated_signed_energy_eV_per_Href":signed,
            "integrated_absolute_energy_eV_per_Href":absolute,
            "integrated_absolute_over_initial_Uthermal":_normalized(absolute["value"],float(uth[0])),
            "integrated_absolute_over_initial_total_energy":_normalized(absolute["value"],initial_energy) if initial_energy is not None else None,
            "sign":"positive means gas heating" if name=="isotropic_CMB_Compton" else "positive magnitude of gas thermal sink",
        }
    reports["H_collisional_ionization"]["integrated_events_per_Href"]=_valid_integral(t,ci_events,civalid)
    reports["H_collisional_ionization"]["temperature_domain_K"]=[1e4,1e9]
    reports["H_collisional_ionization"]["threshold_eV"]=13.6
    reports["H_collisional_ionization"]["energy_destination"]="chemical ionization energy, not radiative cooling"
    reports["H_collisional_excitation"]["temperature_domain_K"]=[5e3,5e5]
    reports["H_collisional_excitation"]["energy_destination"]="escaping line radiation; low_density_escape_assumption"
    reports["isotropic_CMB_Compton"]["geometry_assumption"]=geometry
    reports["isotropic_CMB_Compton"]["maximum_kBT_over_mec2"]=float(np.max(rel))
    report={
        "schema":"C22A_OMITTED_PROCESS_DIAGNOSTICS_V1",
        "status":"COMPLETED_SCOPED_TRAJECTORY_DIAGNOSTIC",
        "new_ODE_runs":0,"old_C21O_ODE_runs":0,
        "interpretation":"evaluated_on_incomplete_original_trajectory; not_self_consistent_alternate_run; not_global_error_bound",
        "hydrogen_species":["H1_0","D_0","T_0"],
        "isotope_approximation":"same_H_electronic_rates_as_selected_C21O/C22A_model",
        "initial_thermal_energy_eV_per_Href":float(uth[0]),
        "initial_total_energy_eV_per_Href":initial_energy,
        "total_energy_denominator":energy_denominator,
        "coverage_policy":"outside_published_fit_domain=NaN_and_OPEN; no_zero_substitution_no_extrapolation; integral_uses_available_adjacent_saved_points_only",
        "population_numerical_residuals":population_residual,
        "diagnostics":reports,
        "included_RR_cooling_integral_eV_per_Href":_valid_integral(t,rr,rrvalid),
        "unassessed_omissions":["He/Li_collisional_ionization","He/Li_excitation","DR","charge_exchange","free_free","molecules","secondary_electron_ionization","RR_radiative_reabsorption","anisotropic_Compton_spectrum"],
        "sources":SOURCES,
        "global_error_bound":None,
    }
    return report,arrays


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True,help='new create-only directory')
    a=p.parse_args()
    raw=a.history.read_bytes()
    # Input identity refers to the exact bytes passed to the NPZ reader.
    import io
    with np.load(io.BytesIO(raw),allow_pickle=False) as history:
        report,arrays=diagnose_history(history)
    report["input"]={"path":str(a.history.resolve()),"size_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
    report["diagnostic_code_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.out.mkdir(parents=True,exist_ok=False)
    with (a.out/'OMISSIONS.json').open('x') as f:
        json.dump(report,f,indent=2,sort_keys=True,allow_nan=False); f.write('\n')
    with (a.out/'OMISSIONS.npz').open('xb') as f:
        np.savez_compressed(f,**arrays)
    print(json.dumps({"status":report["status"],"out":str(a.out.resolve()),
                      "new_ODE_runs":0,"global_error_bound":None},sort_keys=True))


if __name__=='__main__':
    main()
