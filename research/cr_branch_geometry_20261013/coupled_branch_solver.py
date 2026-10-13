"""Source-bound fixed atomic-branch endpoint with rational error certificates.

The construction uses one actual HI sharing subchannel and one actual stopping
edge.  The initial stock is a declared CONSTRUCTION, not an archived spectrum.
No previous suite, full generator, ODE, or NCP is executed.
"""
from __future__ import annotations

from bisect import bisect_right
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT / "inputs/prior"
EV_J = Q("1.602176634e-19")
K_B = Q("1.380649e-23")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_identity(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def dot(row, state):
    return sum((Q(value)*Q(state.get(name, 0)) for name, value in row.items()), Q(0))


def as_strings(values):
    return {name: str(value) for name, value in values.items()}


def build_source_inputs():
    """Bind just the event and stopping edge needed by this new construction."""
    bound = load_module(PRIOR / "kernel_event_adapter.py", "cb_prior_bound_kernel")
    kernel = bound.BoundKernel()
    ion = kernel.ion_event(4762, "HI", 38)
    stopping_index = 290
    ne0 = Q(float(kernel.parent.N_E))
    stop = kernel.drift_event(stopping_index, float(ne0))
    stop_source = kernel.coulomb(stopping_index, float(ne0))
    x0 = Q(float(kernel.parent.DENSITIES["HI"]))
    he0 = Q(float(kernel.parent.DENSITIES["HeI"]))
    initial_hii = ne0+2
    n0 = x0+initial_hii+he0+ne0
    cv = Q(3, 2)*K_B
    chi = Q(20)
    t0 = Q(100)
    initial_ec_eV = chi*K_B*t0/EV_J
    prefix_last = bisect_right(kernel.Eq, initial_ec_eV)-1
    indices = sorted({int(key.split(":")[1]) for ev in (ion, stop)
                      for key in ev.column if key.startswith("A:")})
    rows = kernel.invariants(indices)
    state = {name: Q(0) for row in rows.values() for name in row}
    state.update({f"A:{ion.parent}": Q(1), f"A:{stop.parent}": Q(1),
                  "HI": x0, "HII": initial_hii, "HeI": he0,
                  "HeII": Q(0), "e_th": ne0, "U_th": cv*n0*t0})
    alpha = Q(float(stop_source["alpha"]))
    l0 = Q(float(stop_source["L"]))
    stop_a = alpha/stop.heat_eV
    exact_baseline = stop_a*ne0*l0
    baseline_rounding = abs(float(exact_baseline)-stop_source["lambda_per_s"])/stop_source["lambda_per_s"]
    source_records = [file_identity(PRIOR/rel) for rel in
        ("kernel_event_adapter.py", "inputs/KERNEL_SOURCE_BINDING.json",
         "inputs/kernel_sources/research/cr_phys02b_20261010/src/causal_cascade.py",
         "inputs/kernel_sources/research/cr_phys02c_20261011/src/coherent_bed.py",
         "inputs/kernel_sources/research/cr_phys02c_paired_9600_closeout_20261011/raw/"
         "THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_fullBED_9600.npz",
         "inputs/prior/event_capacity_step.py")]
    result = {
        "schema": "bass-cr-coupled-branch-input.v1",
        "unit_id": "CR-THEORY-BRANCH-GEOMETRY-20261013",
        "baseline_git_commit": "c450b00108dc05885a25d0d9c042cdcfe41bd659",
        "state_status": "CONSTRUCTION: neutral finite stock, not an archived physical evolution",
        "model_scope": "Actual selected HI quadrature subchannel plus separate actual stopping edge",
        "source_reuse": "KC1-KC7 accepted source/kernel evidence; only current construction parameters evaluated",
        "source_files": source_records,
        "saved_grid_raw_sha256": kernel.binding["grid"]["raw_sha256"],
        "parameters_exact": as_strings({
            "EV_J": EV_J, "k_B": K_B, "c_v": cv,
            "volume_m3": Q(1), "step_s": Q("1e14"), "chi": chi,
            "T0_K": t0, "N0_thermal": n0, "X0_HI": x0, "n_e0_m3": ne0,
            "x_max": Q(1, 20), "s_max": Q(1), "T_box_max_K": Q("100.4"),
            "k_ion_m3_s": ion.coefficient, "slow_daughter_eV": ion.daughters_eV[0],
            "stop_delta_eV": stop.heat_eV, "stop_L0": l0, "stop_alpha": alpha,
            "stop_A": stop_a, "stop_lambda0_exact_sinv": exact_baseline,
        }),
        "source_rate_rounding": {
            "semantics": "Finite source alpha and L0 interpreted as exact binary rationals; logarithm evaluated with rational enclosures",
            "source_stopping_lambda0_sinv": stop_source["lambda_per_s"],
            "rational_model_baseline_relative_difference": baseline_rounding,
        },
        "events": {"ion": bound.event_json(ion, kernel), "stop": bound.event_json(stop, kernel)},
        "initial_state_exact": as_strings(state),
        "invariant_rows_exact": {name: as_strings(row) for name, row in rows.items()},
        "raw_energies_eV_exact": {f"A:{j}": str(kernel.Eq[j]) for j in indices},
        "thermal_raw_keys": [f"A:{j}" for j in indices if j <= prefix_last],
        "branch": {"last_thermal_grid_index": prefix_last,
                   "lower_energy_eV_exact": str(kernel.Eq[prefix_last]),
                   "upper_energy_eV_exact": str(kernel.Eq[prefix_last+1]),
                   "initial_active_donor_keys": [f"A:{ion.parent}", f"A:{stop.parent}"],
                   "ownership_policy": "Fixed initial donor mask and fixed thermal prefix; classify the same immutable raw output"},
    }
    return result


def parameters(inputs):
    return {name: Q(value) for name, value in inputs["parameters_exact"].items()}


def ion_map(x, p):
    a = p["step_s"]*p["k_ion_m3_s"]/p["volume_m3"]
    b = 1+1/p["X0_HI"]
    proposal_h = a*(p["X0_HI"]-Q(x))
    return proposal_h/(1+b*proposal_h)


def log_ratio_bounds(x, n0, terms=8):
    """Exact lower/upper bounds for log((n0+x)/n0), x >= 0.

    log((1+t)/(1-t)) = 2 sum t^(2j+1)/(2j+1), t=x/(2 n0+x).
    The positive remainder is bounded by a geometric series.
    """
    x, n0 = Q(x), Q(n0)
    if x < 0 or n0 <= 0 or terms < 1:
        raise ValueError("Positive base density and nonnegative increment required")
    t = x/(2*n0+x)
    partial = 2*sum((t**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    tail = 2*t**(2*terms+1)/(Q(2*terms+1)*(1-t*t))
    return partial, partial+tail


def stopping_rate_bounds(x, p, terms=8):
    # V=1 m3 in this declared construction; x contributes one thermal electron.
    if p["volume_m3"] != 1:
        raise ValueError("This reduced two-variable construction fixes V=1 m3")
    log_lo, log_hi = log_ratio_bounds(x, p["n_e0_m3"], terms)
    n = p["n_e0_m3"]+Q(x)
    lo = p["stop_A"]*n*(p["stop_L0"]-log_hi/2)
    hi = p["stop_A"]*n*(p["stop_L0"]-log_lo/2)
    if lo <= 0:
        raise ValueError("Positive cold-target Coulomb logarithm required")
    return lo, hi


def stopping_map_bounds(x, p, terms=8):
    lo, hi = stopping_rate_bounds(x, p, terms)
    h = p["step_s"]
    return h*lo/(1+h*lo), h*hi/(1+h*hi)


def round_rational(value, decimal_places=30):
    """Choose an exact rational decimal near a nonnegative rational."""
    value = Q(value)
    if value < 0:
        raise ValueError("Nonnegative input required")
    scale = 10**decimal_places
    integer = (2*value.numerator*scale+value.denominator)//(2*value.denominator)
    return Q(integer, scale)


def thermal_temperature(x, s, p):
    cv, n0 = p["c_v"], p["N0_thermal"]
    return (cv*n0*p["T0_K"]+p["EV_J"]*(p["slow_daughter_eV"]*Q(x)
            +p["stop_delta_eV"]*Q(s)))/(cv*(n0+Q(x)))


def exact_state(inputs, x, s):
    state = {name: Q(value) for name, value in inputs["initial_state_exact"].items()}
    for kind, extent in (("ion", Q(x)), ("stop", Q(s))):
        for name, coefficient in inputs["events"][kind]["column_exact"].items():
            state[name] = state.get(name, Q(0))+Q(coefficient)*extent
    return state


def thermal_from_raw(inputs, state):
    p = parameters(inputs)
    thermal_keys = inputs["thermal_raw_keys"]
    ne_count = state["e_th"]+sum((state.get(key, Q(0)) for key in thermal_keys), Q(0))
    u = state["U_th"]+sum((p["EV_J"]*Q(inputs["raw_energies_eV_exact"][key])
                            *state.get(key, Q(0)) for key in thermal_keys), Q(0))
    nuclei = sum((state.get(key, Q(0)) for key in ("HI", "HII", "HeI", "HeII")), Q(0))
    total = nuclei+ne_count
    return {"thermal_electron_count": ne_count, "thermal_total_count": total,
            "thermal_U_J": u, "T_K": u/(p["c_v"]*total),
            "n_e_m3": ne_count/p["volume_m3"]}


def domain_certificate(inputs):
    p = parameters(inputs)
    xm = p["x_max"]
    a = p["step_s"]*p["k_ion_m3_s"]/p["volume_m3"]
    b = 1+1/p["X0_HI"]
    fi_min, fi_max = ion_map(xm, p), ion_map(Q(0), p)
    # log(1+x/n0) <= x/n0 gives a fully rational uniform lower bound.
    log_floor = p["stop_L0"]-xm/(2*p["n_e0_m3"])
    lambda0 = p["stop_A"]*p["n_e0_m3"]*p["stop_L0"]
    lambda_prime_max = p["stop_A"]*(p["stop_L0"]-Q(1, 2))
    q_i = a/(1+b*a*(p["X0_HI"]-xm))**2
    m_s = p["step_s"]*lambda_prime_max/(1+p["step_s"]*lambda0)**2
    q_s = xm*m_s
    q = max(q_i, q_s)
    q_report = Q("0.00031")
    tx_positive_numerator = p["N0_thermal"]*(p["EV_J"]*p["slow_daughter_eV"]
                            -p["c_v"]*p["T0_K"])-p["EV_J"]*p["stop_delta_eV"]
    t_min = thermal_temperature(Q(0), Q(0), p)
    t_max = thermal_temperature(xm, Q(1), p)
    ec_scale = p["chi"]*p["k_B"]/p["EV_J"]
    ec_min, ec_max = ec_scale*t_min, ec_scale*t_max
    lower = Q(inputs["branch"]["lower_energy_eV_exact"])
    upper = Q(inputs["branch"]["upper_energy_eV_exact"])
    l_t = (xm*(p["EV_J"]*p["slow_daughter_eV"]-p["c_v"]*p["T0_K"])
           +p["EV_J"]*p["stop_delta_eV"])/(p["c_v"]*p["N0_thermal"])
    assert 0 < fi_min <= fi_max < xm
    assert log_floor > Q(1, 2)
    assert 0 < q < q_report < 1
    assert tx_positive_numerator > 0
    assert t_min == 100 and t_max < p["T_box_max_K"]
    assert lower < ec_min <= ec_max < upper
    assert ec_scale*p["T_box_max_K"] < upper
    return {
        "x_min_image": fi_min, "x_max_image": fi_max,
        "s_min_inclusive": Q(0), "s_max_inclusive": Q(1),
        "Coulomb_log_uniform_lower_bound": log_floor,
        "q_ion": q_i, "q_stop_weighted": q_s, "q_exact_bound": q,
        "q_reported_bound": q_report, "T_min_K": t_min, "T_max_K": t_max,
        "cutoff_min_eV": ec_min, "cutoff_max_eV": ec_max,
        "lower_branch_margin_eV": ec_min-lower,
        "upper_branch_margin_eV": upper-ec_max,
        "T_lipschitz_K_per_weighted_norm": l_t,
        "cold_active_min_energy_over_kBT": min(Q(value) for key, value in
           inputs["raw_energies_eV_exact"].items() if key not in inputs["thermal_raw_keys"])
           *p["EV_J"]/(p["k_B"]*p["T_box_max_K"]),
    }


def solve(inputs, scalar_iterations=7, log_terms=8, decimal_places=30):
    p = parameters(inputs)
    domain = domain_certificate(inputs)
    x = Q(0)
    for _ in range(scalar_iterations):
        x = ion_map(x, p)
    x_hat = round_rational(x, decimal_places)
    s_lo, s_hi = stopping_map_bounds(x_hat, p, log_terms)
    s_hat = round_rational((s_lo+s_hi)/2, decimal_places)
    residual_x = abs(x_hat-ion_map(x_hat, p))
    residual_s = max(abs(s_hat-s_lo), abs(s_hat-s_hi))
    residual_norm = max(residual_x/p["x_max"], residual_s)
    radius = residual_norm/(1-domain["q_reported_bound"])
    state = exact_state(inputs, x_hat, s_hat)
    thermal = thermal_from_raw(inputs, state)
    assert thermal["T_K"] == thermal_temperature(x_hat, s_hat, p)
    assert thermal["n_e_m3"] == p["n_e0_m3"]+x_hat
    changes = {name: dot(row, state)-dot(row, inputs["initial_state_exact"])
               for name, row in inputs["invariant_rows_exact"].items()}
    assert all(value == 0 for value in changes.values())
    assert all(value >= 0 for value in state.values())
    return {
        "x": x_hat, "s": s_hat, "state": state, "thermal": thermal,
        "domain": domain, "invariant_changes": changes,
        "residual_x": residual_x, "residual_s_upper": residual_s,
        "residual_weighted_norm_upper": residual_norm,
        "fixed_point_weighted_radius_upper": radius,
        "x_error_upper": p["x_max"]*radius,
        "s_error_upper": radius,
        "T_error_K_upper": domain["T_lipschitz_K_per_weighted_norm"]*radius,
        "cutoff_error_eV_upper": p["chi"]*p["k_B"]/p["EV_J"]
                                 *domain["T_lipschitz_K_per_weighted_norm"]*radius,
        "s_map_enclosure": (s_lo, s_hi),
        "scalar_iterations": scalar_iterations, "log_terms": log_terms,
        "decimal_places": decimal_places,
    }
