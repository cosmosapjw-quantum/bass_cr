# SPDX-License-Identifier: GPL-3.0-only
"""Focused author checks for the new geometry/off-grid connection only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import geometry_kernel_rebind as gr


def dec(value):
    value = Q(value)
    return D(value.numerator) / D(value.denominator)


def qjson(value):
    value = Q(value)
    return {"rational": str(value), "float": float(value)}


def identity(path):
    path = Path(path)
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def expect_value_error(call):
    try:
        call()
    except ValueError:
        return True
    raise AssertionError("required explicit domain rejection was not returned")


def decimal_kinetic(momentum):
    with localcontext() as ctx:
        ctx.prec = 90
        c, mass, ev = dec(gr.C_SI), dec(gr.ELECTRON_MASS_SI), dec(gr.EV_J)
        rest = mass*c*c/ev
        psq = sum((dec(x)*c/ev)**2 for x in momentum)
        return +(psq / ((rest*rest+psq).sqrt()+rest))


def helium_ideal_rate(kernel, energy):
    """High-precision diagnostic, not an interval-arithmetic error certificate."""
    with localcontext() as ctx:
        ctx.prec = 90
        ion = kernel.ions["HeI"]
        w, b, u = dec(energy), dec(ion.B_eV), dec(ion.U_eV)
        n, k, s = dec(ion.N), dec(ion.K), dec(ion.S_m2)
        t = w/b
        y = D(2)/(t+1)
        integral = sum(dec(x)/D(j)*(1-y**j)
                       for j, x in enumerate(ion.coefficients, 2))/n
        bracket = integral*t.ln()+k*(1-1/t-t.ln()/(t+1))
        speed = (2*w*dec(gr.EV_J)/dec(gr.ELECTRON_MASS_SI)).sqrt()
        return +(speed*s/(t+u/b+1)*bracket)


def source_rate(kernel, species, energy):
    w = float(energy)
    return Q(math.sqrt(2*w*float(gr.EV_J)/gr.ELECTRON_MASS_SI)
             *float(kernel.ions[species].total_m2(w)))


def run():
    started = time.perf_counter()
    kernel = gr.load_bound_kernel()
    grid = gr.EnergyGrid(kernel.cut, kernel.Eq)
    parent_index = next(j for j, w in enumerate(kernel.Eq) if w >= 30)
    supplied_energy = kernel.Eq[parent_index]
    momentum = gr.momentum_from_kinetic_eV(supplied_energy, (2, 1, 2))
    packets = (gr.MomentumAtom("forward", Q(1, 2), momentum),
               gr.MomentumAtom("backward", Q(1, 2), tuple(-x for x in momentum)))
    transported = gr.bianchi_pushforward(packets, (1, 1, 1), (2, 1, 2/3))
    moved_energy = transported.atoms[0].energy_eV
    assert moved_energy not in grid.nodes
    assert transported.count == 1
    assert transported.particle_work_eV + transported.geometry_ledger_increment_eV == 0
    assert transported.particle_work_eV > 0
    assert transported.atoms[0].energy_eV == transported.atoms[1].energy_eV
    assert all(x == -y for x, y in zip(transported.atoms[0].momentum_si,
                                      transported.atoms[1].momentum_si))
    unchanged = gr.bianchi_pushforward(packets, (1, 1, 1), (1, 1, 1))
    assert unchanged.particle_work_eV == 0
    assert all(a.momentum_si == b.momentum_si for a, b in zip(unchanged.atoms, packets))
    volume_before = Q(7, 3)
    volume_after = volume_before * transported.volume_ratio
    density_after = transported.count / volume_after
    assert density_after * volume_after == transported.count
    reference = decimal_kinetic(transported.atoms[0].momentum_si)
    with localcontext() as ctx:
        ctx.prec = 90
        transport_error = abs(dec(moved_energy)-reference)
        relative_error = transport_error/reference
    assert relative_error < D("8e-15")
    tiny_target = Q("1e-20")
    tiny_q = gr.momentum_from_kinetic_eV(tiny_target, (1, 0, 0))
    tiny_stable = gr.stable_kinetic_eV(tiny_q)
    rest = gr.ELECTRON_MASS_SI * gr.C_SI**2 / float(gr.EV_J)
    tiny_pc = math.hypot(*(x*gr.C_SI/float(gr.EV_J) for x in tiny_q))
    tiny_subtracted = math.hypot(rest, tiny_pc)-rest
    assert tiny_stable > 0 and tiny_subtracted == 0
    assert abs(dec(tiny_stable)-decimal_kinetic(tiny_q))/decimal_kinetic(tiny_q) < D("8e-15")
    assert gr.stable_kinetic_eV((0, 0, 0)) == 0
    raw_before = tuple((a.label, a.before_eV, a.count) for a in transported.atoms)
    raw_after = tuple((a.label, a.energy_eV, a.count) for a in transported.atoms)
    initial_partition = gr.classify_fixed_atoms(raw_before, Q(33), unresolved_upper_eV=kernel.cut)
    moved_partition = gr.classify_fixed_atoms(raw_after, Q(33), unresolved_upper_eV=kernel.cut)
    assert initial_partition["thermal_count"] == 1 and moved_partition["thermal_count"] == 0
    equality = gr.classify_fixed_atoms(raw_after, moved_energy, unresolved_upper_eV=kernel.cut)
    assert equality["thermal_count"] == 1
    assert gr.classify_fixed_atoms(raw_after, Q(33), unresolved_upper_eV=kernel.cut) == moved_partition
    expect_value_error(lambda: gr.classify_fixed_atoms(raw_after, Q("0.05"),
                                                       unresolved_upper_eV=kernel.cut))
    expanded = gr.bianchi_pushforward(packets, (1, 1, 1), (2, 2, 2))
    compressed = gr.bianchi_pushforward(packets, (1, 1, 1), (.1, .1, .1))
    expect_value_error(lambda: gr.bianchi_pushforward(packets, (1, 1, 1), (0, 1, 1)))
    geometry = {
        "status": "PASS", "source_initial_grid_index": parent_index,
        "supplied_initial_energy_eV": qjson(supplied_energy),
        "represented_initial_energy_eV": qjson(transported.atoms[0].before_eV),
        "initialization_discrepancy_eV": qjson(transported.atoms[0].before_eV-supplied_energy),
        "scale_before": [1, 1, 1], "scale_after": [2, 1, 2/3],
        "momentum_ratios_binary64": list(transported.momentum_ratios),
        "volume_ratio_of_finite_scale_inputs": qjson(transported.volume_ratio),
        "packet_count_exact": str(transported.count),
        "moved_energy_eV": qjson(moved_energy),
        "particle_work_eV": qjson(transported.particle_work_eV),
        "external_geometry_ledger_increment_eV": qjson(transported.geometry_ledger_increment_eV),
        "work_ledger_residual_eV": "0", "identity_step_residual_eV": "0",
        "opposite_momenta_preserved": True, "thermal_heat_added_by_geometry": "0",
        "stable_energy_90_digit_diagnostic_abs_error_eV": str(transport_error),
        "stable_energy_90_digit_diagnostic_relative_error": str(relative_error),
        "diagnostic_is_roundoff_certificate": False,
        "tiny_energy_stable_eV": tiny_stable,
        "tiny_energy_subtractive_eV": tiny_subtracted,
        "cutoff_33eV_thermal_count_before_after": ["1", "0"],
        "equality_convention": "thermal", "fixed_reference_repeat_identical": True,
        "unretained_lower_trace_rejected": True,
        "expanded_energy_eV": qjson(expanded.atoms[0].energy_eV),
        "compressed_out_of_source_support_eV": qjson(compressed.atoms[0].energy_eV),
    }

    family_records, example_events = [], []
    for species in ("HI", "HeI"):
        family = gr.rebind_moved_ionization(kernel, "P:forward", moved_energy, species)
        assert family.status == "ACTIVE"
        assert sum(family.probabilities, Q(0)) == 1
        assert family.total_coefficient_m3_s == source_rate(kernel, species, moved_energy)
        selected = {0, len(family.slow_eV)//2, len(family.slow_eV)-1}
        ghost_index = next((j for j, w in enumerate(family.slow_eV)
                            if kernel.cut < w < kernel.Eq[0]), None)
        if ghost_index is not None:
            selected.add(ghost_index)
        event_records = []
        for j in sorted(selected):
            event = family.event(j)
            residuals = gr.event_invariant_residuals(event, kernel)
            assert all(value == 0 for value in residuals.values())
            assert event.projection.weak_error(grid, lambda w: Q(1)) == 0
            assert event.projection.weak_error(grid, lambda w: w) == 0
            quadratic = event.projection.weak_error(grid, lambda w: w*w)
            assert quadratic == 2*event.projection.curvature_geometry_eV2
            kink = event.daughters_eV[0]
            abs_error = abs(event.projection.weak_error(grid, lambda w: abs(w-kink)))
            assert abs_error <= event.projection.lipschitz_geometry_eV
            inherited_projection = kernel.project_exact(event.daughters_eV)
            assert event.projection.active == inherited_projection.active
            assert event.projection.absorbed_count == inherited_projection.absorbed_count
            assert event.projection.absorbed_energy_eV == inherited_projection.absorbed_energy_eV
            assert event.parent_key in event.column and event.column[event.parent_key] == -1
            assert sum(event.daughters_eV, Q(0)) + event.binding_eV == moved_energy
            initial = {event.parent_key: Q(1, 2), species: Q(1)}
            extent = Q(1, 4)
            endpoint = {key: initial.get(key, Q(0))+extent*event.column.get(key, Q(0))
                        for key in initial.keys() | event.column.keys()}
            assert all(value >= 0 for value in endpoint.values())
            record = {
                "quadrature_index": j,
                "probability": qjson(event.probability),
                "coefficient_m3_s": qjson(event.coefficient_m3_s),
                "daughters_eV": [qjson(w) for w in event.daughters_eV],
                "invariant_residuals": {k: str(v) for k, v in residuals.items()},
                "quadratic_weak_error_eV2": qjson(quadratic),
                "C2_geometry_factor_eV2": qjson(event.projection.curvature_geometry_eV2),
                "Lipschitz_geometry_factor_eV": qjson(event.projection.lipschitz_geometry_eV),
                "actual_lower_atoms": [[str(w), str(n)] for w, n in event.projection.actual_lower_atoms],
                "source_cutoff_ghost_count": qjson(event.projection.ghost_count),
                "old_source_projection_parity_exact": True,
                "positive_one_event_endpoint_extent": str(extent),
            }
            event_records.append(record)
            example_events.append({"name": event.name, "parent_key": event.parent_key,
                                   "parent_energy_eV": str(event.parent_energy_eV),
                                   "column": {k: str(v) for k, v in event.column.items()},
                                   "endpoint": {k: str(v) for k, v in endpoint.items()},
                                   **record})
        zero = gr.rebind_moved_ionization(kernel, "P:expanded", expanded.atoms[0].energy_eV, species)
        assert zero.status == "ZERO_AT_OR_BELOW_IONIZATION_THRESHOLD"
        threshold = gr.rebind_moved_ionization(kernel, "P:threshold", Q(float(kernel.ions[species].B_eV)), species)
        assert threshold.status == "ZERO_AT_OR_BELOW_IONIZATION_THRESHOLD"
        masked = gr.rebind_moved_ionization(kernel, "P:masked", moved_energy, species,
                                           initial_cutoff_eV=moved_energy)
        assert masked.status == "BLOCKED_INITIAL_CUTOFF"
        expect_value_error(lambda: gr.rebind_moved_ionization(
            kernel, "P:too_high", compressed.atoms[0].energy_eV, species))
        family_records.append({"species": species, "status": "PASS",
                               "moved_parent_energy_eV": qjson(moved_energy),
                               "threshold_eV": qjson(family.binding_eV),
                               "total_rate_coefficient_m3_s": qjson(family.total_coefficient_m3_s),
                               "sharing_node_count": len(family.slow_eV),
                               "probability_sum_exact": "1",
                               "source_quadrature_normalization_diagnostic": family.source_normalization_diagnostic,
                               "threshold_equality_and_expanded_zero": True,
                               "initial_mask_and_high_support_rejection": True,
                               "events": event_records})

    parent_projection = gr.barycentric_projection(((moved_energy, Q(1)),), grid)
    cell = parent_projection.cells[0]
    bounds = gr.helium_rate_derivative_bounds(kernel, cell.lower_eV, cell.upper_eV)
    assert cell.lower_eV > Q(float(kernel.ions["HeI"].B_eV))
    observed_source_error = abs(parent_projection.weak_error(
        grid, lambda w: source_rate(kernel, "HeI", w)))
    lip_bound = bounds["L_m3_s_per_eV"] * parent_projection.lipschitz_geometry_eV
    c2_bound = bounds["M2_m3_s_per_eV2"] * parent_projection.curvature_geometry_eV2
    assert observed_source_error <= lip_bound and observed_source_error <= c2_bound
    with localcontext() as ctx:
        ctx.prec = 90
        ideal_values = {w: helium_ideal_rate(kernel, w)
                        for w in (moved_energy, cell.lower_eV, cell.upper_eV)}
        ideal_delta = (dec(cell.lower_count)*ideal_values[cell.lower_eV]
                       +dec(cell.upper_count)*ideal_values[cell.upper_eV]
                       -ideal_values[moved_energy])
        max_sample_roundoff = max(abs(dec(source_rate(kernel, "HeI", w))-val)
                                  for w, val in ideal_values.items())
        assert abs(ideal_delta) <= dec(c2_bound)
    expect_value_error(lambda: gr.helium_rate_derivative_bounds(
        kernel, Q(float(kernel.ions["HeI"].B_eV)), cell.upper_eV))
    representation = {
        "status": "PASS", "observable": "retained HeI v_nr(W)*sigma_HeI(W)",
        "cell_eV": [qjson(cell.lower_eV), qjson(cell.upper_eV)],
        "L_m3_s_per_eV": qjson(bounds["L_m3_s_per_eV"]),
        "M2_m3_s_per_eV2": qjson(bounds["M2_m3_s_per_eV2"]),
        "Lipschitz_weak_bound_m3_s": qjson(lip_bound),
        "C2_weak_bound_m3_s": qjson(c2_bound),
        "observed_binary64_source_weak_error_m3_s": qjson(observed_source_error),
        "ideal_formula_90_digit_weak_error_m3_s": str(ideal_delta),
        "maximum_sampled_source_roundoff_m3_s": str(max_sample_roundoff),
        "bounds_interpretation": bounds["interpretation"],
        "numeric_diagnostic_is_roundoff_certificate": False,
        "threshold_crossing_C2_bound_rejected": True,
        "exact_quadratic_witnesses": len(example_events),
        "momentum_or_stress_conservation_claimed": False,
    }

    result = {
        "unit": "CR-THEORY-BRANCH-GEOMETRY-20261013", "status": "PASS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": time.perf_counter()-started,
        "python": sys.version, "platform": platform.platform(),
        "focused_new_check_groups": 3,
        "prior_scientific_suites_rerun": 0,
        "ODE_executions": 0, "generator_builds": 0, "NCP_dispatches": 0,
        "scientific_runtime_scope": "local selected packet/source connection only",
        "sources": [identity(ROOT/"geometry_kernel_rebind.py"), identity(Path(__file__)),
                    identity(ROOT/"inputs/prior/kernel_event_adapter.py"),
                    identity(ROOT/"inputs/prior/inputs/KERNEL_SOURCE_BINDING.json")],
        "kernel_source_records_reused": kernel.binding["files"],
        "geometry": geometry, "moved_HI_HeI": family_records,
        "representation": representation,
        "limitations": [
            "Exact count and ledger identities interpret computed binary64 energies as rational inputs.",
            "High-precision comparisons are diagnostics, not certified floating-point transport or source error bounds.",
            "The old 0.1–900 eV nonrelativistic cold-target collision source is retained.",
            "No daughter angle, target recoil, full stress closure, or unresolved-bath geometry update is inferred.",
            "A threshold-crossing source branch is reevaluated; smooth response bounds are local to admitted intervals.",
        ],
    }
    examples = {"unit": result["unit"], "geometry": geometry,
                "raw_moved_packets": [{"label": a.label, "count": str(a.count),
                                       "momentum_si": list(a.momentum_si),
                                       "energy_eV": str(a.energy_eV)} for a in transported.atoms],
                "moved_event_columns": example_events,
                "base_and_lower_trace_rule": "Use aggregate absorbed fields or their atom lift once, never both.",
                "source_identity": result["sources"]}
    return result, examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"results/GEOMETRY_REBIND_CHECKS.json")
    parser.add_argument("--examples", type=Path, default=ROOT/"examples/GEOMETRY_REBIND_WITNESS.json")
    args = parser.parse_args()
    results, examples = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.examples.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+"\n")
    args.examples.write_text(json.dumps(examples, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"status": results["status"], "new_check_groups": 3,
                      "runtime_seconds": results["runtime_seconds"],
                      "output": str(args.output), "examples": str(args.examples)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
