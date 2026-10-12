"""Targeted checks of the new adapter; no full generator or old suite runs."""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kernel_event_adapter import BoundKernel, EV_J, K_B, dot, event_json


def load_capacity():
    path = ROOT / "inputs/prior/event_capacity_step.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "3683f0577263c2c7113593f6e3085b886b65b44101d438f6dd53f9762848e85c")
    spec = importlib.util.spec_from_file_location("accepted_capacity_kernel", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def active_indices(events):
    return sorted({int(name.split(":")[1]) for ev in events for name in ev.column
                   if name.startswith("A:")})


def projection_parity(kernel, event):
    # Independent exact-rational projection versus unchanged source projector.
    source = kernel.original.project([float(w) for w in event.daughters_eV], 1.)
    ref = np.zeros_like(source)
    for j, count in event.projection.active.items():
        ref[j] = float(kernel.Eq[j]*count)
    ref[kernel.original.ix["cutoff_number"]] = float(event.projection.absorbed_count)
    ref[kernel.original.ix["cutoff_energy"]] = float(event.projection.absorbed_energy_eV)
    scale = max(1., float(kernel.E[event.parent]))
    return float(np.max(np.abs(source-ref))/scale)


def main():
    k = BoundKernel()
    accepted = load_capacity()
    records = []
    events = []
    numerical = []
    mid = int(np.searchsorted(k.E, 30.))
    for sp, ion in k.ions.items():
        threshold = int(np.searchsorted(k.E, ion.B_eV, side="right"))
        for j in (threshold, mid):
            slow, p, p_exact = k.sharing(j, sp)
            fast = k.E[j]-ion.B_eV-slow
            raw = k.original.project(slow, p)+k.original.project(fast, p)
            count = np.sum(raw[:len(k.E)]/k.E)+raw[k.original.ix["cutoff_number"]]
            energy = np.sum(raw[:len(k.E)])+raw[k.original.ix["cutoff_energy"]]
            count_residual = float(count-2.)
            energy_relative = float((energy+ion.B_eV-k.E[j])/k.E[j])
            assert np.min(p) > 0 and abs(count_residual) < 1.e-12
            assert abs(energy_relative) < 1.e-12 and sum(p_exact, Q(0)) == 1
            ghost_target = .5*(float(k.cut)+k.E[0])
            selection = sorted({0, len(slow)-1,
                                int(np.argmin(np.abs(slow-ghost_target)))})
            local = [k.ion_event(j, sp, q) for q in selection]
            events.extend(local)
            coefficient = float(math.sqrt(2*k.E[j]*float(EV_J)/k.parent.m_e)
                                *ion.total_m2(float(k.E[j])))
            numerical.append({
                "kind": "ionization", "species": sp, "parent_index": j,
                "parent_energy_eV": float(k.E[j]), "sharing_nodes": len(slow),
                "min_probability": float(np.min(p)),
                "source_probability_sum": float(np.sum(p)),
                "exact_probability_sum": "1", "count_residual": count_residual,
                "energy_relative_residual": energy_relative,
                "coefficient_m3_per_s": coefficient,
                "selected_exact_event_count": len(local),
                "max_exact_vs_source_projection_relative": max(projection_parity(k, ev) for ev in local),
                "rational_probability_max_rounding_difference": max(
                    abs(float(pe)-float(pf)) for pe, pf in zip(p_exact, p)),
            })
            if j == threshold:
                # The selected actual near-threshold subfamily has thermal daughters.
                assert all(ev.projection.absorbed_count == 2 for ev in local)

    for relative, channel in k.channels.items():
        threshold = int(np.searchsorted(k.E, channel["adopted_effective_cost_eV"], side="right"))
        for j in (threshold, mid):
            ev = k.excitation_event(j, relative)
            events.append(ev)
            numerical.append({"kind": "excitation", "channel": relative,
                              "parent_index": j, "parent_energy_eV": float(k.E[j]),
                              "effective_cost_eV": float(channel["adopted_effective_cost_eV"]),
                              "coefficient_m3_per_s": float(ev.coefficient),
                              "max_exact_vs_source_projection_relative": projection_parity(k, ev)})

    for j in (0, 3199, mid):
        ev = k.drift_event(j, k.parent.N_E)
        events.append(ev)
        old_b = float(k.parent.stopping_eV_s(float(k.E[j])))
        new = k.coulomb(j, k.parent.N_E)
        relative = abs(new["b_eV_per_s"]-old_b)/old_b
        assert relative < 1.e-13
        lo, hi = .5*k.parent.N_E, 2*k.parent.N_E
        end_a, end_b = k.coulomb(j, lo), k.coulomb(j, hi)
        derivative_bound = max(abs(end_a["d_lambda_d_ne"]), abs(end_b["d_lambda_d_ne"]))
        assert end_a["L"] > 0 and end_b["L"] > 0
        numerical.append({"kind": "drift", "parent_index": j,
                          "parent_energy_eV": float(k.E[j]),
                          "baseline_b_eV_per_s": old_b, "baseline_relative_difference": relative,
                          "lambda_per_s": new["lambda_per_s"],
                          "density_interval_m3": [lo, hi],
                          "min_Coulomb_log": min(end_a["L"], end_b["L"]),
                          "lambda_density_derivative_bound": derivative_bound})

    indices = active_indices(events)
    rows = k.invariants(indices)
    invariant_residuals = {ev.name: {name: str(dot(row, ev.column)) for name, row in rows.items()}
                          for ev in events}
    assert all(x == "0" for values in invariant_residuals.values() for x in values.values())
    assert max(projection_parity(k, ev) for ev in events) < 1.e-12
    assert any(ev.projection.ghost_count > 0 for ev in events)
    assert any(ev.projection.actual_subcut_count > 0 for ev in events)
    gap = np.diff(np.r_[float(k.cut), k.E])
    max_gap = float(np.max(gap))
    assert max_gap < min(ion.B_eV for ion in k.ions.values())
    shared = [ev for ev in events if ev.kind == "ionization" and ev.species == "HI"
              and ev.parent == mid]
    shared_base = {f"A:{mid}": Q(1), "HI": Q(1)}
    shared_rates = {ev.name: k.proposal(ev, shared_base, Q(1)) for ev in shared}
    shared_result = accepted.capacity_step(shared_base,
        {ev.name: ev.column for ev in shared}, shared_rates, Q("1e20"))
    ratios = [shared_result.extents[ev.name]/ev.probability for ev in shared]
    assert all(value == ratios[0] for value in ratios)
    sharing_capacity = {"largest_saved_grid_gap_eV": max_gap,
                        "minimum_binding_eV": min(ion.B_eV for ion in k.ions.values()),
                        "no_ion_parent_reprojection": True,
                        "targeted_same_family_sharing_points": len(shared),
                        "all_extent_over_probability_ratios_exactly_equal": True,
                        "common_ratio_exact": str(ratios[0])}

    # A sparse actual-kernel subfamily exercises the unchanged shared capacity map.
    # It is a constructed state, not the archived spectrum or a full physical solve.
    selected = []
    for sp in ("HI", "HeI"):
        selected.append(next(ev for ev in events if ev.kind == "ionization" and ev.species == sp))
        selected.append(next(ev for ev in events if ev.kind == "ionization" and ev.species == sp
                             and ev.projection.ghost_count > 0))
        selected.append(next(ev for ev in events if ev.kind == "excitation" and ev.species == sp))
    selected.append(next(ev for ev in events if ev.kind == "drift" and ev.parent == 0))
    donor_indices = {ev.parent for ev in selected}
    state = {name: Q(0) for row in rows.values() for name in row}
    for j in donor_indices:
        state[f"A:{j}"] = Q(1)
    state.update(HI=Q(float(k.parent.DENSITIES["HI"])),
                 HeI=Q(float(k.parent.DENSITIES["HeI"])),
                 e_th=Q(float(k.parent.N_E)), HeII=Q(0))
    state["HII"] = state["e_th"]+len(donor_indices)
    n_thermal = sum(state[name] for name in ("HI", "HII", "HeI", "HeII", "e_th"))
    state["U_th"] = Q(3, 2)*K_B*n_thermal*100
    volume = Q(1)
    rates = {ev.name: k.proposal(ev, state, volume,
                               trial_thermal_electron_count=state["e_th"])
             for ev in selected}
    h = Q("1e14")
    result = accepted.capacity_step(state, {ev.name: ev.column for ev in selected}, rates, h)
    changed = {name: str(dot(row, result.state)-dot(row, state)) for name, row in rows.items()}
    assert all(value == "0" for value in changed.values())
    assert all(value >= 0 for value in result.state.values())
    assert accepted.temperature(result.state) > 0
    assert dot(rows["charge_over_e"], state) == 0
    disabled = k.proposal(selected[0], state, volume, initial_cutoff_eV=Q(20),
                          trial_thermal_electron_count=state["e_th"])
    assert disabled == 0
    half_targets = {sp: state[sp]/2 for sp in ("HI", "HeI")}
    trial_half = k.proposal(selected[0], state, volume, trial_species_counts=half_targets)
    assert trial_half == rates[selected[0].name]/2
    rec = {
        "state_kind": "constructed neutral sparse actual-kernel subfamily; not archived evolution",
        "event_count": len(selected), "step_seconds": float(h), "initial_T_K": 100.,
        "final_T_K": float(accepted.temperature(result.state)),
        "invariant_changes_exact": changed,
        "all_state_entries_nonnegative": True,
        "minimum_retained_fraction_of_positive_initial_stock": min(
            float(result.state[name]/value) for name, value in state.items() if value > 0),
        "max_raw_donor_load_times_step_over_stock": max(
            float(h*result.donor_loads[name]/value) for name, value in state.items() if value > 0),
        "initial_active_mask_20eV_disables_13eV_parent": disabled == 0,
        "trial_target_density_half_gives_exact_half_atomic_proposal": trial_half == rates[selected[0].name]/2,
        "capacity_code_sha256": hashlib.sha256((ROOT/"inputs/prior/event_capacity_step.py").read_bytes()).hexdigest(),
        "initial_state_exact": {name: str(value) for name, value in state.items()},
        "final_state_exact": {name: str(value) for name, value in result.state.items()},
        "extents_exact": {name: str(value) for name, value in result.extents.items()},
        "raw_output_active_nodes": [{"index": j, "W_eV": float(k.E[j]),
                                     "W_J": float(EV_J*k.Eq[j]),
                                     "A_count": float(result.state.get(f"A:{j}", 0)),
                                     "A_count_exact": str(result.state.get(f"A:{j}", Q(0)))}
                                    for j in indices if result.state.get(f"A:{j}", 0)],
        "base_thermal_electrons": float(result.state["e_th"]),
        "base_U_J": float(result.state["U_th"]),
    }
    output = {
        "schema": "bass-cr-kernel-adapter-checks.v1",
        "unit_id": "CR-THEORY-KERNEL-CUTOFF-20261013",
        "status": "pass",
        "saved_grid_identity_verified": True,
        "full_generator_built": False, "ODE_or_NCP_run": False,
        "source_definition_subset_executed": ["gauss", "checked_energy", "Ionization",
                                               "Cascade.project", "Cascade._sharing",
                                               "AtomicData.excitation_sigma", "stopping_eV_s"],
        "exact_event_count": len(events), "exact_invariant_rows": list(rows),
        "exact_column_residuals": invariant_residuals,
        "targeted_component_checks": numerical,
        "source_sharing_diagnostics": [list(row) for row in k.original.normalization_diagnostics],
        "sharing_distribution_capacity_preservation": sharing_capacity,
        "capacity_witness": rec,
        "scope": "finite source model and new event adapter; imported atomic derivation and original mesh validation are reused",
    }
    examples = {"schema": "bass-cr-actual-kernel-events.v1",
                "reference_cutoff_eV": float(k.cut),
                "energies_in_state": "SI joules; eV fields are labeled source coordinates",
                "exact_arithmetic_semantics": "saved floating inputs treated as binary rationals; fast daughter and barycentric coefficients completed exactly; p normalized exactly",
                "events": [event_json(ev, k) for ev in events],
                "capacity_witness": rec}
    for rel, data in (("results/KERNEL_ADAPTER_CHECKS.json", output),
                      ("examples/ACTUAL_KERNEL_EVENT_COLUMNS.json", examples)):
        path = ROOT/rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")
    summary = {"status": "pass", "exact_event_count": len(events),
               "exact_invariant_rows": 4, "ionization_component_count": 4,
               "excitation_component_count": 4, "drift_component_count": 3,
               "capacity_event_count": len(selected),
               "capacity_final_T_K": rec["final_T_K"],
               "capacity_max_raw_load": rec["max_raw_donor_load_times_step_over_stock"]}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
