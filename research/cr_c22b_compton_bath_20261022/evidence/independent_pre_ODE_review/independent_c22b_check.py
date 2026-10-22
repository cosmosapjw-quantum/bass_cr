"""Independent finite C22B review; no integrator imports or calls.

The old saved arrays are only input states for changed-dependency RHS checks.
They are neither repaired nor integrated again. Outputs are create-only.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    unit = args.project.resolve()
    repo = unit.parent.parent
    oldunit = unit.parent / "cr_c22a_thermochemical_20261022"
    oldfreeze = json.loads((oldunit / "evidence/SOURCE_FREEZE.json").read_text())
    source_before = {name: digest(unit / name) for name in ("model.py", "compton.py", "CONTRACT.json")}
    oldsource = []
    for row in oldfreeze["files"]:
        path = repo / row["path"]
        observed = digest(path)
        oldsource.append({"path": row["path"], "sha256": observed,
                          "matches_C22A_freeze": observed == row["sha256"]})
    assert all(r["matches_C22A_freeze"] for r in oldsource)
    sys.path.insert(0, str(unit))
    import numpy as np
    from scipy.constants import Boltzmann, c, electron_mass, Stefan_Boltzmann
    from model import ThermochemicalFactory, K_B_EV_K
    import compton

    # An independent radiation-constant route: a_R=4 sigma_SB/c in SI.
    a_si = 4 * Stefan_Boltzmann / c
    ar_relative = abs(compton.A_R_CGS / (a_si * 10) - 1)
    assert ar_relative < 1e-9  # Published sigma_SB constant may be rounded.
    scalar_rows = []
    for t, tg, xe in ((10., 57.2355, .3), (57.2355, 57.2355, .2),
                      (1e4, 30., 1.15), (1e4, 30., 0.)):
        # W per reference particle divided by eV in joules.
        expected = (4 * compton.SIGMA_T_CM2 * 1e-4 * a_si * tg**4
                    * Boltzmann * xe * (tg-t) / (electron_mass*c) / 1.602176634e-19)
        actual = compton.gas_exchange_eV_per_H_s(t, tg, xe)
        relative = abs(actual-expected)/max(abs(expected), 1e-300)
        assert relative < 1e-9
        assert actual*(1/t-1/tg) >= 0
        scalar_rows.append({"T_K": t, "Tgamma_K": tg, "electrons_per_H": xe,
                            "expected_eV_per_H_s": expected, "actual": actual,
                            "relative_difference": relative})

    factory = ThermochemicalFactory()
    histories = []
    finite_rows = []
    for case_name in ("dark_expansion", "finite_uv_flrw", "finite_uv_lrs"):
        case_dir = oldunit / "runs/c22a_finite_uv_bdf_20261022_v1/cases" / case_name
        raw = (case_dir / "history.npz").read_bytes()
        history = np.load(io.BytesIO(raw), allow_pickle=False)
        case = json.loads((case_dir / "MODEL.json").read_text())["case"]
        case.update(compton_enabled=True, Tcmb0_K=2.7255)
        model = factory.build(case)
        assert (model.size, model.solver_size) == (75, 72)
        labels = model.metadata()["invariant_labels"]
        assert labels == ["n", "T_0", "T_1"]
        histories.append({"path": str(case_dir / "history.npz"), "size_bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
        for index in (0, 1, 30, 100, 150, 200):
            eta = float(history["eta"][index])
            full = np.r_[history["Y"][:, index], 0.]
            assert np.array_equal(model.lift(model.project(full)), full)
            derivative = model.rhs(eta, full)
            base = model.base.rhs(eta, full[:-1])
            assert np.array_equal(model.lift(model.solver_rhs(eta, model.project(full))), derivative)
            assert np.all(derivative[model.invariant_indices] == 0)
            unaffected = np.setdiff1d(np.arange(74), [model.iu])
            assert np.array_equal(derivative[unaffected], base[unaffected])
            q = model.fields(eta, full)
            abundance = model.atomic.physical_abundances(full[model.ax])
            ne = float(model.atomic.q @ abundance)
            npart = float((1 + model.atomic.q) @ abundance)
            tg = 2.7255 / q["a"]
            rate = (4 * compton.SIGMA_T_CM2 * 1e-4 * a_si * tg**4 * Boltzmann
                    * ne * (tg-q["temperature_K"]) / (electron_mass*c) / 1.602176634e-19)
            flux = rate/q["H"]
            flux_relative = abs(-derivative[model.ibath]-flux)/max(abs(flux), 1e-300)
            assert flux_relative < 1e-9
            terms = [derivative[model.iu], model.binding@(model.atomic.scales*derivative[model.ax]),
                     model.photon_energies(eta)@derivative[model.gx],
                     -model.photon_energies(eta)@full[model.gx], derivative[model.iesc],
                     derivative[model.iwg], derivative[model.iwr], derivative[model.ibath]]
            normalized = abs(math.fsum(terms))/max(math.fsum(abs(x) for x in terms), 1e-300)
            assert normalized < 2e-14
            # EOS chain rule has N' and therefore the ionization particle term.
            npart_prime = float((1+model.atomic.q)@(model.atomic.scales*derivative[model.ax]))
            tprime = derivative[model.iu]/(1.5*K_B_EV_K*npart) - q["temperature_K"]*npart_prime/npart
            hstep = 2e-5/max(1., abs(derivative[model.iu]/full[model.iu]), abs(npart_prime/npart))
            numerical = (model.temperature(full+hstep*derivative)-model.temperature(full-hstep*derivative))/(2*hstep)
            directional_relative = abs(numerical-tprime)/max(abs(tprime), 1e-30)
            assert directional_relative < 1e-7
            shifted = full.copy(); shifted[model.ibath] = 13.5
            assert np.array_equal(model.rhs(eta, shifted), derivative)
            assert model.fields(eta, shifted)["H"] == q["H"]
            finite_rows.append({"case": case_name, "saved_index": index, "eta": eta,
                "T_K": q["temperature_K"], "Tgamma_K": tg,
                "energy_terms_normalized_residual": normalized,
                "Compton_flux_relative_vs_SI": flux_relative,
                "EOS_directional_relative": directional_relative,
                "kinetic_and_number_RHS_exact_base_parity": True,
                "declared_zero_RHS_exact": True, "bath_shift_RHS_and_H_invariant": True})

    off = factory.build({"name": "off_high_T_review", "temperature_K": 1e8, "compton_enabled": False})
    full = off.initial_state()
    old = off.base.rhs(0., full[:-1]); new = off.rhs(0., full)
    assert np.array_equal(new[:-1], old) and new[-1] == 0.
    rejected = []
    for coordinate in off.invariant_indices:
        for sign in (-1., 1.):
            invalid = full.copy(); invalid[coordinate] = sign*1e-100
            try:
                off.project(invalid)
            except ValueError as exc:
                assert "NONZERO_DECLARED_INVARIANT" in str(exc)
                rejected.append({"coordinate": int(coordinate), "value": sign*1e-100, "error": str(exc)})
            else:
                raise AssertionError("NONZERO_INVENTORY_ACCEPTED")
    source_after = {name: digest(unit / name) for name in source_before}
    assert source_after == source_before
    result = {"schema": "C22B_INDEPENDENT_FINITE_REVIEW_V1", "status": "PASS_SCOPED",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "execution": {"ODE_calls": 0, "saved_states_used_as_finite_RHS_inputs": len(finite_rows),
                      "old_state_mutations": 0, "old_ODE_replays": 0},
        "source_sha256": source_before, "source_unchanged_during_checks": True,
        "immutable_C22A_source_files": oldsource, "saved_inputs": histories,
        "radiation_constant_relative_to_4sigmaSB_over_c": ar_relative,
        "scalar_cases": scalar_rows, "finite_RHS_cases": finite_rows,
        "off_mode_high_T_parent_domain_parity": {"T_K": 1e8, "first_74_exact": True, "bath_derivative": 0.},
        "nonzero_declared_inventory_rejections": rejected,
        "invariant_projection": {"full": 75, "active": 72, "removed": [40,45,46], "labels": labels},
        "primary_formula_source": "https://adsabs.harvard.edu/pdf/1997MNRAS.292...27H Appendix A p42 and Eq2 p29",
        "limitations": ["finite input checks only; no new integration", "external bath ledger is not resident CMB energy",
                        "prescribed isotropic bath does not close the inherited CMB spectrum",
                        "global model validity, omitted atomic rates, and full energy feedback remain open"],
        "global_error_bound": None}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as output:
        json.dump(result, output, indent=2, allow_nan=False); output.write("\n")
    print(json.dumps({"status": result["status"], "output": str(args.out),
        "finite_RHS_states": len(finite_rows), "source_sha256": source_before,
        "max_normalized_ledger": max(r["energy_terms_normalized_residual"] for r in finite_rows),
        "max_EOS_directional_relative": max(r["EOS_directional_relative"] for r in finite_rows)}))


if __name__ == "__main__":
    main()
