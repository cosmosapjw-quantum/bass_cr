"""Changed-dependency checks for C22D. No cosmological ODE is integrated."""
from __future__ import annotations
import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import model as new
from run_pilot import json_create, lease_snapshot, resource_control, utc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    resources = resource_control.observe_resources()
    reserved, leases = lease_snapshot(set(os.sched_getaffinity(0)))
    json_create(args.output / "RESOURCE.json", {"resource": resources, "leases": leases,
                "affinity": sorted(os.sched_getaffinity(0)), "threads": 1})
    if reserved & set(os.sched_getaffinity(0)):
        raise RuntimeError("KNOWN_LEASE_INTERSECTS_CHECK_CPU")
    cases = json.loads((new.HERE / "inputs/NOMINAL_CASES.json").read_text())["cases"]
    factory = new.ThermochemicalFactory()
    off, on = factory.build(cases[0]), factory.build(cases[1])
    checks, details = [], []

    def check(name, condition, **evidence):
        checks.append({"name": name, "pass": bool(condition), **evidence})

    check("state_and_declared_invariant_map", on.size == 78 and on.solver_size == 75
          and len(on.invariant_indices) == 3)
    check("same_registry_matched_initial_state", on.initial_state().tobytes() == off.initial_state().tobytes())
    for species in ("H1", "D", "T"):
        lo, hi = on.atomic.blocks[species]
        check("aligned_binding_" + species, on.binding[hi]-on.binding[lo] == new.CHI_EV)
    e = np.array([13.59, 13.6, np.nextafter(new.CHI_EV, -np.inf), new.CHI_EV, 20.])
    p = on.atomic.provider
    adopted, original = p.sigma("HI", e), p.source.sigma("HI", e)
    check("PI_support_refined_not_energy_shift", np.all(adopted[:3] == 0.)
          and np.array_equal(adopted[3:], original[3:]) and original[1] > 0.)
    check("RR_number_fit_unchanged", all(p.rr("HI", t) == p.source.rr("HI", t)
                                        for t in (300., 1e4, 2e4)))
    transitions = np.array(on.transition_times())
    check("new_PI_threshold_segment_registered", np.min(abs(transitions-np.log(20./new.CHI_EV))) < 1e-15)
    check("old_H_threshold_not_registered", np.min(abs(transitions-np.log(20./13.6))) > 1e-8)
    check("layer_initial_energy_recomputed", all(
        layer.initial_energy == layer.energy(0., layer.initial_state())
        for layer in (on, on.base, on.base.base, on.base.base.base)))

    for ionized, temperature, eta in ((.0002, 300., 0.), (.05, 1e4, 0.),
                                     (.05, 2e4, .5), (.5, 8e3, 1.2)):
        y = on.initial_state()
        y[on.ax.start+on.h1_ground] = 1.-ionized
        y[on.ax.start+on.h1_ion] = ionized
        abundance = on.atomic.physical_abundances(y[on.ax])
        particles = float(np.sum(abundance) + on.atomic.q @ abundance)
        y[on.iu] = 1.5*new._ci.KB_EV_K*particles*temperature
        q = on.fields(eta, y)
        don, doff = on.rhs(eta, y), off.rhs(eta, y)
        old_prefix = off.base.rhs(eta, y[:off.base.size])
        check(f"aligned_off_prefix_bitwise_T{temperature:g}", doff[:off.base.size].tobytes() == old_prefix.tobytes())
        rate = on.ci_events(eta, y, q)
        expected = np.zeros(on.size)
        expected[on.ax.start+on.h1_ground] = -rate/on.atomic.scales[on.h1_ground]
        expected[on.ax.start+on.h1_ion] = rate/on.atomic.scales[on.h1_ion]
        expected[on.iu] = -new.CHI_EV*rate
        expected[on.ici] = rate
        # Subtracting two large complete RHS values can lose tiny CI increments.
        # The tolerance here is relative to the full operation scale, while the
        # nonzero warm CI increment is checked separately below.
        difference = don-doff
        scale = np.maximum.reduce([abs(don), abs(doff), abs(expected), np.full(on.size, 1e-300)])
        check(f"CI_only_expected_stoichiometric_coordinates_T{temperature:g}",
              np.max(abs(difference-expected)/scale) < 2e-14,
              normalized_error=float(np.max(abs(difference-expected)/scale)))
        if temperature >= 8000.:
            check(f"warm_CI_increment_resolved_T{temperature:g}",
                  np.max(abs(difference-expected))/np.max(abs(expected)) < 5e-12)
        de = on.rhs_energy_residual(eta, y)
        energy_terms = abs(don[on.iu])+float(abs(on.binding) @ abs(on.atomic.scales*don[on.ax]))
        energy_terms += sum(abs(don[i]) for i in (on.iesc,on.iwg,on.iwr,on.ibath))
        check(f"event_total_energy_T{temperature:g}", abs(de)/max(energy_terms,1e-300) < 2e-14)
        dparticles = float(np.sum(on.atomic.scales*expected[on.ax])
                           + on.atomic.q @ (on.atomic.scales*expected[on.ax]))
        tprime = expected[on.iu]/(1.5*new._ci.KB_EV_K*particles)-temperature*dparticles/particles
        formula = -(2*new.CHI_EV/(3*new._ci.KB_EV_K)+temperature)*rate/particles
        check(f"particle_temperature_chain_rule_T{temperature:g}",
              abs(tprime-formula) <= 5e-15*max(abs(formula),1e-300))
        details.append({"T_K":temperature,"eta":eta,"CI_events_per_H_per_eta":rate,
                        "nHref_cm3":q["nH_ref_cm3"],"particles_per_H":particles,
                        "CI_Tprime_K":tprime,"energy_rhs_residual":de})
    invalid = []
    for description, call in (
        ("unsupported_CI_species",lambda: on.ci_provider.evaluate(1e4,species="D")),
        ("unsupported_physical_total",lambda: on.ci_provider.evaluate(1e4,full_physical_rate=True)),
        ("boolean_temperature",lambda: on.ci_provider.evaluate(True)),
        ("registry_mismatch",lambda: factory.build(dict(cases[1],energy_registry="old13.6"))),
        ("required_CI_disabled",lambda: factory.build(dict(cases[0],required_processes=[new.PROCESS])))):
        try: call()
        except ValueError as exc: invalid.append({"case":description,"exception":str(exc),"pass":True})
        else: invalid.append({"case":description,"pass":False})
    y = on.initial_state(); y[on.invariant_indices[0]] = 1e-20
    try: on.project(y)
    except ValueError: check("declared_n_not_silently_erased",True)
    else: check("declared_n_not_silently_erased",False)
    # Verify that view construction never changed the frozen/shared provider.
    original_model = factory.base_factory.build({k:v for k,v in cases[1].items()
                                                if k not in ("energy_registry","h1_ci_enabled")})
    check("fresh_original_factory_still_13p6", original_model.thresholds[0] == 13.6
          and original_model.atomic.provider.sigma("HI",np.array([13.6]))[0] > 0.)
    all_pass = all(x["pass"] for x in checks+invalid)
    report = {"schema":"C22D_CHANGED_MODEL_CHECKS_V1","utc":utc(),
              "status":"PASS_SCOPED" if all_pass else "FAIL_PRESERVED",
              "checks":checks,"invalid_inputs":invalid,"point_details":details,
              "new_ODE":0,"old_ODE":0,"global_error_bound":None,
              "source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (new.HERE/"model.py",new.HERE/"ci_finite.py",new.HERE/"optimized_kernel.py")}}
    json_create(args.output/"RESULT.json",report)
    print(json.dumps({"status":report["status"],"checks":len(checks)+len(invalid),
                      "failures":[x for x in checks+invalid if not x["pass"]],"new_ODE":0}))
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
