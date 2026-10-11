#!/usr/bin/env python3
"""One bounded Fraction check of analytic toy identities; not physical G."""
from fractions import Fraction as F
import json


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def frac(x):
    x = F(x)
    return {"numerator": x.numerator, "denominator": x.denominator}


def project(energy, count, nodes=(F(1), F(2)), cut=F(1, 10)):
    """Exact analytic projection, separate active energy/cut energy/cut count."""
    assert F(0) <= energy <= nodes[-1]
    assert count >= 0
    active = [F(0) for _ in nodes]
    cutoff_energy, cutoff_number = F(0), F(0)
    if energy <= cut:
        return active, count*energy, count
    for index, upper in enumerate(nodes):
        if energy <= upper:
            lower = nodes[index-1] if index else cut
            weight = (energy-lower)/(upper-lower)
            active[index] += upper*count*weight
            if index:
                active[index-1] += lower*count*(1-weight)
            else:
                cutoff_energy += lower*count*(1-weight)
                cutoff_number += count*(1-weight)
            return active, cutoff_energy, cutoff_number
    raise AssertionError("projection domain")


def projected_ledgers(energy, count, nodes=(F(1), F(2)), cut=F(1, 10)):
    active, cutoff_energy, cutoff_number = project(energy, count, nodes, cut)
    e = sum(active, F(0)) + cutoff_energy
    n = sum((u/E for u, E in zip(active, nodes)), F(0)) + cutoff_number
    assert e == count*energy
    assert n == count
    return e, n


def main():
    checks = []
    ell_e = [F(1), F(1), F(1)]
    ell_n = [F(1), F(1, 2), F(0)]
    old_column = [F(1, 2), F(-1), F(1, 2)]
    assert dot(ell_e, old_column) == 0
    assert dot(ell_n, old_column) == 0
    checks.append({"name": "baseline_drift_both_ledgers", "exact": True})
    for name, epsilon in (("one_binary64_ulp_at_2_eV", F(1, 2**51)),
                          ("finite_tenth_eV", F(1, 10))):
        patched_e2 = 2+epsilon
        patched_n = [F(1), 1/patched_e2, F(0)]
        number_residual = dot(patched_n, old_column)
        assert dot(ell_e, old_column) == 0
        assert number_residual == epsilon/(2*(2+epsilon)) > 0
        checks.append({"name": name, "epsilon_eV": frac(epsilon),
                       "energy_residual_s_inverse": frac(0),
                       "number_residual_eV_s_inverse": frac(number_residual),
                       "exact": True})
    assert dot([F(1), 1/(2+F(1, 2**51)), F(0)], old_column) == F(1, 9007199254740994)

    e2 = F(21, 10)
    fixed_stopping = F(1)
    d = fixed_stopping/(e2-1)
    consistent_column = [d/e2, -d, d*(e2-1)/e2]
    assert dot(ell_e, consistent_column) == 0
    assert dot([F(1), 1/e2, F(0)], consistent_column) == 0
    checks.append({"name": "consistent_reconstruction_keeps_stopping_fixed",
                   "column_s_inverse": [frac(x) for x in consistent_column], "exact": True})

    doubled = [2*x for x in old_column]
    assert doubled != old_column
    assert dot(ell_e, doubled) == dot(ell_n, doubled) == 0
    checks.append({"name": "same_E_and_conservation_do_not_imply_same_operator", "exact": True})

    for name, E, p, nodes in (
        ("interior_barycentric", F(5, 4), F(3, 7), (F(1), F(2))),
        ("cutoff_ghost", F(3, 20), F(5, 3), (F(1, 5), F(2))),
        ("below_cutoff_actual_energy", F(1, 20), F(5, 3), (F(1), F(2))),
        ("at_cutoff", F(1, 10), F(2, 3), (F(1), F(2))),
        ("at_top_node", F(2), F(2, 3), (F(1), F(2))),
        ("zero_energy", F(0), F(2, 3), (F(1), F(2))),
    ):
        energy, number = projected_ledgers(E, p, nodes)
        checks.append({"name": name, "energy_eV": frac(energy),
                       "count": frac(number), "exact": True})

    incoming, binding, slow = F(2), F(1, 2), F(1, 4)
    fast = incoming-binding-slow
    slow_e, slow_n = projected_ledgers(slow, F(1))
    fast_e, fast_n = projected_ledgers(fast, F(1))
    assert -incoming + slow_e + fast_e + binding == 0
    assert -1 + slow_n + fast_n - 1 == 0
    checks.append({"name": "ionization_energy_and_corrected_number", "exact": True})

    cost = F(3, 4)
    outgoing_e, outgoing_n = projected_ledgers(incoming-cost, F(1))
    assert -incoming + outgoing_e + cost == 0
    assert -1 + outgoing_n == 0
    checks.append({"name": "excitation_energy_and_number", "exact": True})
    print(json.dumps({"schema": "cr-phys02e-exact-analytic-toy.v1",
                      "role": "THEORY_CONTRIBUTOR",
                      "status": "EXACT_RATIONAL_TOY_IDENTITIES_CONFIRMED",
                      "method": "fractions.Fraction; analytic matrices and projection only",
                      "is_physical_operator": False,
                      "physical_G_builds": 0, "physical_pulse_calls": 0,
                      "scientific_module_imports": 0, "old_suite_reruns": 0,
                      "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
