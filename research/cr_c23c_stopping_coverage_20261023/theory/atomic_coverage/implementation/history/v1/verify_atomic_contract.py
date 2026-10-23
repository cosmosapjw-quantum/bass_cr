"""New exact C23C contract witnesses, to run once through the root lease runner.

Expected values are hand-derived rational conservation/counterexample witnesses.
No historical source provider, ODE or prior campaign is invoked.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import sys


def _load():
    path = Path(__file__).with_name("atomic_contract.py")
    spec = importlib.util.spec_from_file_location("c23c_atomic_contract", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_checks():
    c = _load()
    checks = []

    def check(name, condition, evidence):
        checks.append({"name": name, "pass": bool(condition), "evidence": evidence})
        if not condition:
            raise AssertionError(name)

    def rejects(name, fn):
        try:
            fn()
        except c.ContractError as exc:
            checks.append({"name": name, "pass": True, "evidence": str(exc)})
        else:
            raise AssertionError(name)

    check("inventory_cardinality", len(c.POPULATIONS) == 21 and len(c.SPECIES) == 22,
          "1+3*2+2*3+2*4=21 atomic populations, plus one free-electron pool")
    expected = ("n:0", "H1:0", "H1:1", "D:0", "D:1", "T:0", "T:1",
                "He3:0", "He3:1", "He3:2", "He4:0", "He4:1", "He4:2",
                "Li6:0", "Li6:1", "Li6:2", "Li6:3", "Li7:0", "Li7:1", "Li7:2", "Li7:3")
    check("explicit_species_order", c.POPULATION_LABELS == expected, list(expected))
    counts = {"n": 0, "H1": 1, "D": 1, "T": 1, "He3": 2, "He4": 2, "Li6": 3, "Li7": 3}
    for kind, sign in (("CI", 1), ("PI", 1), ("RR", -1)):
        reactions = c.all_rungs(kind)
        check(f"{kind}_13_rungs", len(reactions) == 13,
              "Three H-isotope + four He-isotope + six Li-isotope charge transitions")
        for reaction in reactions:
            net = reaction.net()
            q = reaction.lower_charge
            lo = c.INDEX[f"{reaction.nuclide}:{q}"]
            hi = c.INDEX[f"{reaction.nuclide}:{q+1}"]
            ref = [0] * 22
            ref[lo], ref[hi], ref[-1] = -sign, sign, sign
            check(reaction.identifier + ":net", tuple(ref) == net,
                  {"lower": -sign, "upper": sign, "free_electron": sign, "other": 0})
            residuals = c.conservation_residuals(net)
            check(reaction.identifier + ":invariants", all(v == 0 for v in residuals.values()), residuals)
            check(reaction.identifier + ":particle_count", sum(net) == sign,
                  "The monatomic/free-electron particle count changes by one; isotope counts are fixed")
        check(f"{kind}_nuclide_counts",
              {n: sum(r.nuclide == n for r in reactions) for n in counts} == counts, counts)
    bad = list(c.rung("D", 0).net())
    bad[-1] = 0
    check("missing_electron_is_detected", c.conservation_residuals(bad)["charge"] == 1,
          "Ionization without its extra free electron leaves +1 electric charge")
    explicit = {s: 0 for s in expected}
    explicit["H1:0"] = "1"
    check("explicit_zero_inventory", sum(c.inventory(explicit)) == 1,
          "n and all T charge states are present explicitly with zero initial number")
    missing = dict(explicit)
    del missing["T:1"]
    rejects("missing_species_rejected", lambda: c.inventory(missing))
    rejects("bool_inventory_rejected", lambda: c.inventory(dict(explicit, **{"n:0": False})))
    rejects("unknown_nuclide_rejected", lambda: c.rung("H2", 0))
    rejects("neutron_atomic_rung_rejected", lambda: c.rung("n", 0))
    rejects("invalid_li_charge_rejected", lambda: c.rung("Li7", 3))

    support = c.SourceSupport("SYNTHETIC:H1:0", "CI", "synthetic:no_empirical_rate",
                              F(14), F(100), F(13))
    for energy, status in ((12, "PHYSICAL_THRESHOLD_ZERO"), (13, "UNCOVERED_UNKNOWN"),
                           ("13.5", "UNCOVERED_UNKNOWN"), (14, "SOURCE_COVERED_VALUE_NOT_EVALUATED"),
                           (100, "SOURCE_COVERED_VALUE_NOT_EVALUATED"), (101, "UNCOVERED_UNKNOWN")):
        out = support.classify(energy)
        check(f"support:{energy}", out.status == status, {"status": out.status, "value": None if out.known_value is None else str(out.known_value)})
    check("true_kinematic_zero", support.classify(12).require_physical_value() == 0,
          "An explicitly admitted threshold excludes subthreshold events")
    rejects("uncovered_cannot_be_zero_filled", lambda: support.classify("13.5").require_physical_value())
    rejects("covered_still_needs_provider_value", lambda: support.classify(15).require_physical_value())
    unknown_threshold = c.SourceSupport("SYNTHETIC:H1:0", "CI", "synthetic", F(14), F(100))
    check("unknown_threshold_stays_unknown", unknown_threshold.classify(0).known_value is None,
          "No threshold is inferred from the first table knot")
    rejects("nan_rejected", lambda: support.classify("NaN"))
    rejects("negative_energy_rejected", lambda: support.classify(-1))

    ci = c.ionization_ledger(chemical_defect_eV="6.5", incoming_electron_eV=20,
                            outgoing_electrons_eV=(3, "10.5"))
    check("CI_energy_owner", ci["residual_eV"] == 0 and ci["electron_kinetic_change_eV"] == F(-13, 2),
          "20 -> 3 + 10.5 kinetic + 6.5 binding; net electron thermal loss is 6.5, not 20")
    pi = c.ionization_ledger(chemical_defect_eV="6.5", incoming_electron_eV=0,
                            outgoing_electrons_eV=("13.5",), incoming_photon_eV=20)
    check("PI_energy_owner", pi["residual_eV"] == 0 and pi["electron_kinetic_change_eV"] == F(27, 2),
          "Photon energy 20 -> primary electron 13.5 + binding 6.5; no immediate-heat inference")
    mismatch = c.ionization_ledger(chemical_defect_eV="6.6", incoming_electron_eV=20,
                                  outgoing_electrons_eV=(3, "10.5"))
    check("mixed_threshold_detected", mismatch["residual_eV"] == F(1, 10),
          "Changing only the chemical defect produces a nonzero energy residual")
    rejects("missing_secondary_not_inferred", lambda: c.ionization_ledger(
        chemical_defect_eV=1, incoming_electron_eV=2, outgoing_electrons_eV=()))
    check("recoil_mass_dependence", c.recoil_momentum_transfer_factor(1, 3) == F(3, 8)
          and c.recoil_momentum_transfer_factor(1, 7) == F(7, 32),
          {"synthetic_masses_1_3": "3/8", "synthetic_masses_1_7": "7/32"})
    maxwell = c.relative_maxwell_parameters(projectile_mass=1, target_mass=3,
              projectile_temperature=8, target_temperature=4)
    check("finite_mass_relative_temperature", maxwell == {"reduced_mass": F(3, 4), "relative_temperature": F(7)},
          "(3/4)*(8+4/3)=7; stationary target and finite-T double-Maxwell are different contracts")

    G = ((-2, 1), (2, -1))
    equal = c.isotope_quotient_at_state({"a": G, "b": G}, {"a": (0, 13), "b": (5, 18)})
    check("constant_binding_offset_quotient", equal["joint_quotient"],
          "epsilon_b-epsilon_a=(5,5) is a conserved isotope-number offset")
    different_binding = c.isotope_quotient_at_state({"a": G, "b": G}, {"a": (0, 13), "b": (0, 14)})
    check("number_not_energy_quotient", different_binding["number_quotient"]
          and not different_binding["binding_source_quotient"]
          and different_binding["energy_row_differences"]["b"] == (F(2), F(-1)),
          {"a_energy_row": [26, -13], "b_energy_row": [28, -14]})
    different_rate = c.isotope_quotient_at_state({"a": G, "b": ((-3, 1), (3, -1))},
                                               {"a": (0, 13), "b": (0, 13)})
    check("unequal_rates_fail_number_quotient", not different_rate["number_quotient"],
          "Same total neutral population gives ionization derivative2 or3 depending on isotope allocation")
    rejects("nonconservative_generator_rejected", lambda: c.isotope_quotient_at_state(
        {"a": G, "b": ((-2, 1), (3, -1))}, {"a": (0, 13), "b": (0, 13)}))
    rejects("negative_transition_rejected", lambda: c.isotope_quotient_at_state(
        {"a": G, "b": ((1, 1), (-1, -1))}, {"a": (0, 13), "b": (0, 13)}))
    return {"schema": "C23C_ATOMIC_CONTRACT_CHECKS_V1", "status": "PASS_SCOPED",
            "checks": checks, "assertions": len(checks), "new_ODE": 0,
            "empirical_rate_evaluations": 0, "historical_science_replays": 0,
            "global_error_bound": None,
            "scope": "Exact declared stoichiometry and synthetic rational closure witnesses; physical rates/coverage remain source-bound"}


if __name__ == "__main__":
    result = run_checks()
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_atomic_contract.py CREATE_ONLY_OUTPUT.json")
    with open(sys.argv[1], "x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, ensure_ascii=False))
