"""Only C9-affected C23C N5 checks; does not rerun the 155-check v1 suite."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import sys


def run_checks():
    path = Path(__file__).with_name("atomic_contract.py")
    spec = importlib.util.spec_from_file_location("c23c_atomic_repaired", path)
    c = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = c
    spec.loader.exec_module(c)
    checks = []

    def check(name, condition, evidence):
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "pass": True, "evidence": evidence})

    args = dict(chemical_defect_eV="6.5", incoming_electron_eV=20,
                outgoing_electrons_eV=(3, "10.5"))
    try:
        c.ionization_ledger(**args)
    except TypeError:
        check("omitted_recoil_rejected", True, "recoil_eV is a required keyword")
    else:
        raise AssertionError("omitted recoil was silently accepted")
    try:
        c.ionization_ledger(**args, recoil_eV=None)
    except c.ContractError:
        check("unknown_recoil_rejected", True, "None is not a supplied kinetic energy")
    else:
        raise AssertionError("unknown recoil was silently accepted")
    out = c.ionization_ledger(**args, recoil_eV=0)
    check("explicit_zero_recoil_preserves_numeric_ledger",
          {k: v for k, v in out.items() if k != "electron_pool"} == {
          "electron_kinetic_change_eV": F(-13, 2), "binding_change_eV": F(13, 2),
          "radiation_change_eV": F(0), "recoil_change_eV": F(0), "residual_eV": F(0)},
          "The formerly defaulted zero is now explicitly declared; numerical identity retained")
    check("all_free_kinetic_owner", out["electron_pool"] == "all_free_kinetic",
          "This output is not a thermal-heating provider")
    recoil = c.ionization_ledger(chemical_defect_eV="6.5", incoming_electron_eV=20,
                                 outgoing_electrons_eV=(3, 10), recoil_eV="0.5")
    check("supplied_nonzero_recoil", recoil["residual_eV"] == 0 and
          recoil["electron_kinetic_change_eV"] == -7 and recoil["recoil_change_eV"] == F(1, 2),
          "20=3+10+6.5+0.5; no missing energy inferred as recoil")
    G = ((0, 1, 0), (0, -2, 0), (0, 1, 0))
    q = c.isotope_quotient_at_state({"a": G, "b": G},
                                   {"a": (0, 13, 24), "b": (0, 14, 26)})
    check("directed_reducible_weak_connectivity_witness", q["joint_quotient"] and
          q["energy_source_rows"]["a"] == (F(0), F(-2), F(0)) and
          q["energy_source_rows"]["b"] == (F(0), F(-2), F(0)),
          "Nearest-neighbor G has rank1<2; binding offset(0,1,2) is nonconstant yet left-null")
    return {"schema": "C23C_ATOMIC_C9_TARGETED_REPAIR_V1", "status": "PASS_SCOPED",
            "checks": checks, "assertions": len(checks), "historical_155_replayed": 0,
            "empirical_rate_evaluations": 0, "new_ODE": 0,
            "findings_addressed": ["constant-offset lemma needs rank n-1/irreducibility",
                                    "free-electron kinetic ledger is not thermal heat",
                                    "recoil must be explicitly supplied"]}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_atomic_repair.py CREATE_ONLY_OUTPUT.json")
    result = run_checks()
    with open(sys.argv[1], "x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, ensure_ascii=False))
