#!/usr/bin/env python3
"""One bounded exact-rational derivation oracle; no physical import or expm.

The four-state matrix is a constructed analytic toy, not bass_cr's operator.
The separate atom example tests general-measure identities, including an atom
at the finite-window boundary. It is not a new physical source model.
"""
from fractions import Fraction as F
import json
import math


checks = []


def eq(name, left, right):
    assert left == right, (name, left, right)
    checks.append({"name": name, "status": "PASS", "exact": True})


def true(name, value):
    assert value, name
    checks.append({"name": name, "status": "PASS", "exact": True})


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def mv(a, b):
    return [dot(row, b) for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def solve(a, b):
    """Exact Gauss-Jordan arithmetic, independent of SciPy triangular solver."""
    n = len(a)
    rows = [[F(x) for x in row] + [F(y)] for row, y in zip(a, b)]
    for k in range(n):
        p = next(i for i in range(k, n) if rows[i][k])
        rows[k], rows[p] = rows[p], rows[k]
        d = rows[k][k]
        rows[k] = [x/d for x in rows[k]]
        for i in range(n):
            if i != k:
                factor = rows[i][k]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[k])]
    return [row[-1] for row in rows]


def add(a, b):
    return [x+y for x, y in zip(a, b)]


def subtract(a, b):
    return [x-y for x, y in zip(a, b)]


def poly_add(a, b):
    n = max(len(a), len(b))
    return [((a[i] if i < len(a) else F(0)) +
             (b[i] if i < len(b) else F(0))) for i in range(n)]


def poly_scale(a, b):
    return [x*b for x in a]


def poly_eq(name, a, b):
    n = max(len(a), len(b))
    eq(name, a + [F(0)]*(n-len(a)), b + [F(0)]*(n-len(b)))


# Physical convention in this toy: A_s in s^-1, h_s in s^-1.
A = [
    [F(1), F(-1, 2), F(0), F(0)],
    [F(0), F(2), F(0), F(0)],
    [F(0), F(0), F(3), F(-1)],
    [F(0), F(0), F(0), F(4)],
]
h = [F(1, 2), F(1, 4), F(3, 2), F(1)]
births = [[F(1), F(0), F(0), F(0)], [F(0), F(0), F(0), F(2)]]
b = add(*births)
q0 = solve(transpose(A), h)
q1 = solve(transpose(A), q0)
q2 = solve(transpose(A), q1)
eq("adjoint_q0_equation", mv(transpose(A), q0), h)
eq("adjoint_q1_equation", mv(transpose(A), q1), q0)
eq("adjoint_q2_equation", mv(transpose(A), q2), q1)
true("metzler_hurwitz_energy_loss_toy", all(A[i][i] > 0 for i in range(4)) and
     all(A[i][j] <= 0 for i in range(4) for j in range(4) if i != j) and
     all(sum(A[i][j] for i in range(4))-h[j] >= 0 for j in range(4)))
true("nonnegative_heat_adjoint_bounded_by_one", all(0 <= x <= 1 for x in q0))

# Analytic kernels: K_low=.5 exp(-t), K_high=3 exp(-3t)-exp(-4t).
# For integer n, integral_0^infty t^n exp(-lambda*t) dt=n!/lambda^(n+1).
kernel_terms = [[(F(1, 2), 1)], [(F(3), 3), (F(-1), 4)]]
H = []
for j, bj in enumerate(births):
    w0 = solve(A, bj)
    w1 = solve(A, w0)
    w2 = solve(A, w1)
    direct = [sum((c*F(math.factorial(n), rate**(n+1)) for c, rate in kernel_terms[j]), F(0)) for n in range(3)]
    forward = [dot(h, w0), dot(h, w1), 2*dot(h, w2)]
    adjoint = [dot(q0, bj), dot(q1, bj), 2*dot(q2, bj)]
    eq(f"birth_{j}_direct_kernel_vs_forward_moments", direct, forward)
    eq(f"birth_{j}_direct_kernel_vs_adjoint_moments", direct, adjoint)
    eq(f"birth_{j}_mean_occupation", sum((x*y for x, y in zip(q0, w0)), F(0)), direct[1])
    eq(f"birth_{j}_second_moment_future_reward_occupation", 2*dot(q1, w0), direct[2])
    H.append(direct)

# At the symbolic horizon T=ln(2) seconds, all exp(-integer*T) are rational.
# Direct analytic propagator columns: source0 -> e^-T; source3 ->
# x2=2(e^-3T-e^-4T), x3=2e^-4T. No expm is executed.
xT_births = [[F(1, 2), F(0), F(0), F(0)], [F(0), F(0), F(1, 8), F(1, 8)]]
xT = add(*xT_births)
w = solve(A, b)
wT = solve(A, xT)
tail0 = dot(q0, xT)
tail1 = dot(q1, xT)
tail2 = 2*dot(q2, xT)
direct_tail = []
all_terms = kernel_terms[0]+kernel_terms[1]
for n in range(3):
    coeffs = [F(0)]*(n+1)
    for c, rate in all_terms:
        for power in range(n+1):
            coeffs[power] += c*F(1, 2**rate)*F(math.factorial(n), math.factorial(power)*rate**(n-power+1))
    direct_tail.append(coeffs)
poly_eq("tail_mass_direct_integral_vs_saved_state", direct_tail[0], [tail0])
poly_eq("tail_first_direct_integral_vs_saved_state", direct_tail[1], [tail1, tail0])
poly_eq("tail_second_direct_integral_vs_saved_state", direct_tail[2], [tail2, 2*tail1, tail0])
eq("tail_residual_first_future_occupation", dot(q0, wT), tail1)
eq("tail_residual_second_future_occupation", 2*dot(q1, wT), tail2)
eq("clipped_first_occupation_plus_residual", dot(q0, subtract(w, wT)) + tail1, dot(q1, b))
frontier = [x*y for x, y in zip(q1, xT)]
future_occupation = [x*y for x, y in zip(q0, wT)]
true("frontier_and_future_residence_bins_differ", frontier != future_occupation)
eq("frontier_and_future_residence_totals_agree", sum(frontier), sum(future_occupation))
true("all_occupation_contributions_nonnegative", all(x*y >= 0 for x, y in zip(q0, w)) and all(x*y >= 0 for x, y in zip(q0, wT)))

# Independent exact finite-window measure oracle. This tests an atom at T,
# which the actual continuous heat kernel does not have.
T = F(4)
atoms = [
    [(F(1), F(1, 4)), (F(2), F(1, 2)), (F(6), F(1, 4))],
    [(F(2), F(1, 4)), (F(4), F(1, 4)), (F(12), F(1, 2))],
]
mix = [F(2, 5), F(3, 5)]
combined = [(t, mix[j]*weight) for j, group in enumerate(atoms) for t, weight in group]
rows = []
for name, group in [("low", atoms[0]), ("high", atoms[1]), ("selected", combined)]:
    eq(name+"_probability_normalization", sum(weight for _, weight in group), F(1))
    p = sum((weight for t, weight in group if t <= T), F(0))
    R = sum((weight*max(F(0), 1-t/T) for t, weight in group), F(0))
    S = sum((weight*max(F(0), 1-t/T)**2 for t, weight in group), F(0))
    mu = sum(t*weight for t, weight in group)
    m2 = sum(t*t*weight for t, weight in group)
    e1 = sum((t*weight for t, weight in group if t <= T), F(0))
    e2 = sum((t*t*weight for t, weight in group if t <= T), F(0))
    l1 = sum((t*weight for t, weight in group if t > T), F(0))
    l2 = sum((t*t*weight for t, weight in group if t > T), F(0))
    r1 = sum((weight*max(F(0), t-T) for t, weight in group), F(0))
    r2 = sum((weight*max(F(0), t-T)**2 for t, weight in group), F(0))
    eq(name+"_early_first", e1, T*(p-R))
    eq(name+"_early_second", e2, T*T*(p-2*R+S))
    eq(name+"_late_first", l1, mu-T*(p-R))
    eq(name+"_late_second", l2, m2-T*T*(p-2*R+S))
    eq(name+"_residual_first", r1, mu-T*(1-R))
    eq(name+"_residual_second", r2, m2-2*T*mu+T*T*(1-S))
    eq(name+"_early_variance_compact", e2/p-(e1/p)**2, T*T*(p*S-R*R)/(p*p))
    eq(name+"_late_residual_variance_shift", l2/(1-p)-(l1/(1-p))**2, r2/(1-p)-(r1/(1-p))**2)
    true(name+"_early_support_moment_positivity", 0 <= R <= p <= 1 and R*R <= p*S and S <= R)
    true(name+"_tail_support_moment_positivity", r1 >= 0 and r2 >= 0 and r1*r1 <= (1-p)*r2)
    rows.append({"p": p, "R": R, "S": S, "mu": mu, "m2": m2, "var": m2-mu*mu,
                 "mu_early": e1/p, "var_early": e2/p-(e1/p)**2,
                 "mu_late": l1/(1-p), "var_late": l2/(1-p)-(l1/(1-p))**2,
                 "rho_late": r1/(1-p)})
total = rows[-1]
eq("birth_mixture_mean", sum(mix[j]*rows[j]["mu"] for j in range(2)), total["mu"])
eq("birth_mixture_total_variance", sum(mix[j]*(rows[j]["var"]+(rows[j]["mu"]-total["mu"])**2) for j in range(2)), total["var"])
for condition, suffix in [("early", "p"), ("late", "one_minus_p")]:
    weights = [mix[j]*(rows[j]["p"] if condition == "early" else 1-rows[j]["p"])/(total["p"] if condition == "early" else 1-total["p"]) for j in range(2)]
    eq(condition+"_posterior_normalization", sum(weights), F(1))
    eq(condition+"_posterior_mean", sum(weights[j]*rows[j]["mu_"+condition] for j in range(2)), total["mu_"+condition])
    eq(condition+"_posterior_total_variance", sum(weights[j]*(rows[j]["var_"+condition]+(rows[j]["mu_"+condition]-total["mu_"+condition])**2) for j in range(2)), total["var_"+condition])

print(json.dumps({"schema": "cr-phys02f-candidate-exact-toy.v1", "status": "PASS",
    "max_active_states": 4, "physical_G_builds": 0, "physical_transport_calls": 0,
    "expm_calls": 0, "new_input_endpoint_analysis_runs": 0,
    "identities": len(checks), "checks": checks,
    "four_state_H0_H1_H2_by_birth": [[str(x) for x in row] for row in H],
    "four_state_q0": [str(x) for x in q0],
    "four_state_tail_residual_moments": [str(tail0), str(tail1), str(tail2)],
    "frontier_lag_contributions": [str(x) for x in frontier],
    "future_residence_lag_contributions": [str(x) for x in future_occupation],
    "finite_window_atom_selected": {k: str(v) for k, v in total.items()},
    "claim_scope": "Exact derivation toy only; no physical operator, runtime admission, or acceptance decision."
}, indent=2))
