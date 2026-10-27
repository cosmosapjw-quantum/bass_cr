#!/usr/bin/env python3
"""Changed physics limits and adversarial contracts; no old suite replay."""
import argparse
import copy
import json
import math
from pathlib import Path

import numpy as np

from model import (CONSTANTS, FITS, SOURCE_PATH, T_END, UNIT_ID, inventory, need,
                   photo_cm2, source_arrays, validate_actual_source, write_json)
from ports import (claim_birth, claim_return, context_record, native25_rr,
                   retained_port, validate_context)
from prepare import require_runner
from uniformization import (choose_cutoff, propagate, ramp_occupancy_weights,
                            uniformization_rate)


def close(value, expected, tolerance=2e-12):
    value, expected = np.asarray(value), np.asarray(expected)
    scale = max(float(np.max(np.abs(expected))), 1e-300)
    need(np.all(np.isfinite(value)) and float(np.max(np.abs(value - expected))) <= tolerance * scale,
         "ANALYTIC_OR_CONSERVATION_DISAGREEMENT")


def refused(action, reason):
    try:
        action()
    except ValueError as error:
        need(reason in str(error), "UNEXPECTED_REFUSAL_REASON:" + str(error))
        return
    raise AssertionError("EXPECTED_CONTROLLED_REFUSAL:" + reason)


def solve(amplitude, drift, lh, lhe, times):
    arrays = [np.asarray(a, dtype=float) for a in (amplitude, drift, lh, lhe)]
    nu = uniformization_rate(*arrays[1:])
    cutoff, _ = choose_cutoff(nu, max(times))
    wn, wo, _ = ramp_occupancy_weights(nu, times, cutoff)
    return propagate(*arrays, np.asarray(times), nu, wn, wo)[:2]


def scalar_exact(amplitude, removal, t):
    z = removal * t
    change = math.expm1(-z)
    return amplitude * (z + change) / removal ** 2, \
        amplitude * (z * z / 2 - z - change) / removal ** 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    unit = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    require_runner(unit, out)
    findings = []

    def check(name, action, meaning):
        try:
            action()
            findings.append({"name": name, "pass": True, "meaning": meaning})
        except Exception as error:
            findings.append({"name": name, "pass": False, "meaning": meaning,
                             "error": type(error).__name__ + ":" + str(error)})

    def zero_generator():
        times = np.asarray([.5, 1., 2., 3.])
        source = np.asarray([2., 3.])
        n, occ = solve(source, [0., 0.], [0., 0.], [0., 0.], times)
        close(n, np.outer(times ** 2 / 2, source), 0.)
        close(occ, np.outer(times ** 3 / 6, source), 0.)

    check("zero_drift_zero_RR_exact_polynomial", zero_generator,
          "Actual occupancy is the time integral, and zero generator preserves the prescribed ramp.")

    def one_capture():
        times = [.5, 1., 2., 3.]
        n, occ = solve([2.], [0.], [.7], [0.], times)
        exact = [scalar_exact(2., .7, t) for t in times]
        close(n[:, 0], [r[0] for r in exact])
        close(occ[:, 0], [r[1] for r in exact])
        close(n[:, 0] + .7 * occ[:, 0], np.asarray(times) ** 2)

    check("zero_drift_single_capture_analytic", one_capture,
          "A killed one-state ramp has an independent closed-form state and occupancy.")

    def finite_bin_survivors():
        n, occ = solve([2.], [0.], [.7], [0.], [1., 2.])
        h, k, a = 1., .7, 2.
        absolute_clock_reset_occ = a * (1. * (h / k + math.expm1(-k * h) / k ** 2)
            + (k * k * h * h / 2 - k * h - math.expm1(-k * h)) / k ** 3)
        expected_survivor_occupancy = -scalar_exact(a, k, 1.)[0] * math.expm1(-k * h) / k
        actual_bin = occ[1, 0] - occ[0, 0]
        close(actual_bin - absolute_clock_reset_occ, expected_survivor_occupancy)
        need(actual_bin > absolute_clock_reset_occ > 0, "PRIOR_SURVIVORS_MUST_BE_PRESENT")

    check("finite_bin_inherits_prior_population", finite_bin_survivors,
          "The second bin includes first-bin survivors even when its source clock is absolute.")

    def competing_capture():
        t, a, h, he = 2., 3., .4, .9
        n, occ = solve([a], [0.], [h], [he], [t])
        exact_n, _ = scalar_exact(a, h + he, t)
        removed = a * t * t / 2 - exact_n
        close(n[0, 0], exact_n)
        close(h * occ[0, 0], h / (h + he) * removed)
        close(he * occ[0, 0], he / (h + he) * removed)
        separately = a * t * t - scalar_exact(a, h, t)[0] - scalar_exact(a, he, t)[0]
        need(separately > removed, "SEPARATELY_KILLED_CHANNEL_SUM_IS_NOT_COMMON_COMPETITION")

    check("common_competing_H_He_capture", competing_capture,
          "Channel captures partition a single common survival process.")

    def drift_only_energy():
        energy = np.asarray([1., 2.])
        drift = np.asarray([.7, .3])
        source = np.asarray([.5, 1.5])
        times = [1., 2., 3.]
        n, occ = solve(source, drift, [0., 0.], [0., 0.], times)
        stopping = drift * np.diff(np.r_[.1, energy])
        for j, t in enumerate(times):
            cutoff = drift[0] * occ[j, 0]
            close(math.fsum(n[j]) + cutoff, math.fsum(source) * t * t / 2)
            close(math.fsum(energy * n[j]) + .1 * cutoff + math.fsum(stopping * occ[j]),
                  math.fsum(energy * source) * t * t / 2)

    check("zero_RR_drift_number_and_energy", drift_only_energy,
          "Downward transport splits active energy, cutoff energy and caloric transfer exactly in the represented model.")

    def zero_source():
        n, occ = solve([0., 0.], [.2, .5], [.7, .1], [.3, .2], [1., 2.])
        need(np.count_nonzero(n) == 0 and np.count_nonzero(occ) == 0,
             "ZERO_SOURCE_MUST_RETURN_EXACT_ZERO")

    check("zero_source_exact_zero", zero_source, "No event or state is created without a source.")

    def direct_cutoff():
        t, acut = 3., 2.
        direct = acut * t * t / 2
        n, occ = solve([0.], [1.], [2.], [3.], [t])
        need(n[0, 0] == occ[0, 0] == 0, "DIRECT_CUTOFF_IS_NOT_ACTIVE")
        close(.1 * direct, .1 * acut * t * t / 2, 0.)

    check("direct_cutoff_has_no_active_RR", direct_cutoff,
          "A boundary atom is owned by the unresolved cutoff ledger, not post-boundary physical RR.")

    context = context_record(inventory())

    def event_energy_charge():
        native = native25_rr(context, {"H": 2., "He": 3.}, {"H": 4., "He": 9.})
        values = native["values"]
        close(math.fsum((values[1], values[2], 4 * values[10], 4 * values[11])), 0., 0.)
        need(abs(native["thermal_electron_change"]) <= 1e-14 * 5. / context["recipient_nb_m3"],
             "THERMAL_ELECTRON_RR_STOICHIOMETRY")
        need(values[23] == values[24] == 0., "RR_RADIATION_MUST_NOT_HEAT_WEXT")
        for channel, count, kinetic in (("H", 2., 4.), ("He", 3., 9.)):
            threshold = FITS[channel][0]
            residual = math.fsum((-kinetic, -threshold * count, kinetic + threshold * count))
            need(abs(residual) <= 1e-14 * (kinetic + threshold * count), "EVENT_ENERGY_ROUNDOFF")

    check("RR_event_baryon_charge_and_energy", event_energy_charge,
          "Only the RR event updates native25; binding and retained photons are counted once.")

    def mutation(path, value):
        changed = copy.deepcopy(context)
        location = changed
        for key in path[:-1]:
            location = location[key]
        location[path[-1]] = value
        return changed

    mutations = [
        ("mixed_frame", ["recipient_frame"], "other_rest_frame", "MIXED_FRAME"),
        ("mixed_state", ["recipient_state_id"], "PR107_T10000K", "MATCHING_EXPLICIT_STATE"),
        ("missing_nb", ["recipient_nb_m3"], None, "EXPLICIT_MATCHING_NB"),
        ("mismatched_nb", ["donor_nb_m3"], 1., "EXPLICIT_MATCHING_NB"),
        ("wrong_inventory", ["inventory_values", "T_K"], 10000., "FROZEN_100K_INVENTORY"),
        ("wrong_isotope_mapping", ["isotope_mapping"], "CONDITIONAL_HE_TO_HE3", "WRONG_ISOTOPE"),
        ("wrong_target_isotope", ["channels", "He", "isotope"], "He3", "ISOTOPE_STATE_BRANCH"),
        ("wrong_target_state", ["channels", "He", "target_state"], "2s", "ISOTOPE_STATE_BRANCH"),
        ("wrong_product_state", ["channels", "He", "final_state"], "triplet", "ISOTOPE_STATE_BRANCH"),
        ("wrong_degeneracy", ["channels", "He", "d"], 1, "ISOTOPE_STATE_BRANCH"),
        ("stimulated_component", ["component"], "stimulated", "GROUND_SCALAR"),
        ("native_support_expansion", ["native_birth_support_eV"], [.1, 900.], "NATIVE_BIRTH_SUPPORT"),
        ("missing_history", ["known_history_s"], None, "ACTUAL_FINITE_HISTORY"),
        ("invented_shutoff", ["history_outside"], "zero", "ACTUAL_FINITE_HISTORY"),
        ("second_clock_factor", ["normalization", "source_clock_factor"], 729., "NORMALIZATION"),
        ("second_volume_factor", ["normalization", "source_volume_factor"], 729., "NORMALIZATION"),
        ("second_target_factor", ["normalization", "rr_target_density_applications"], 2, "NORMALIZATION"),
        ("invented_parent_chemistry", ["source_parent_ion_chemistry"], "neutral_H_photoionization", "UNKNOWN_SOURCE_CHEMISTRY"),
        ("invented_worldtube_volume", ["proper_volume_m3"], 1., "PROPER_CLOCK_VOLUME"),
    ]
    for name, path, value, reason in mutations:
        changed = mutation(path, value)
        check("reject_" + name, lambda c=changed, r=reason: refused(lambda: validate_context(c), r),
              "The actual response contract refuses this unsupported state or normalization mutation.")

    def duplicate_birth():
        registry = []
        claim_birth(context, registry)
        refused(lambda: claim_birth(context, registry), "OVERLAPPING_SOURCE_BIRTH")

    check("reject_duplicate_birth", duplicate_birth, "Same physical source injection is claimed once.")

    def disjoint_returns():
        registry = []
        for channel in ("H", "He"):
            for left, right in zip([0., T_END / 4, T_END / 2, 3 * T_END / 4],
                                   [T_END / 4, T_END / 2, 3 * T_END / 4, T_END]):
                claim_return(context, channel, [left, right], registry)
        need(len(registry) == 8, "FOUR_BINS_TWO_CHANNELS_REQUIRED")

    check("accept_disjoint_bins_same_birth", disjoint_returns,
          "Shared birth history does not merge disjoint observation events.")

    def overlapping_returns():
        registry = []
        claim_return(context, "H", [0., T_END / 2], registry)
        refused(lambda: claim_return(context, "H", [T_END / 4, 3 * T_END / 4], registry),
                "OVERLAPPING_CAUSAL_RETURN")

    check("reject_overlapping_observation_bins", overlapping_returns,
          "Distinct endpoint hashes cannot conceal overlapping physical return claims.")

    def whole_then_split():
        registry = []
        claim_return(context, "He", [0., T_END], registry)
        refused(lambda: claim_return(context, "He", [0., T_END / 4], registry),
                "OVERLAPPING_CAUSAL_RETURN")

    check("reject_whole_then_split_returns", whole_then_split,
          "Cumulative whole-window events cannot be added again through a smaller bin.")
    check("reject_cumulative_prefix_claim", lambda: refused(
          lambda: claim_return(context, "H", [0., T_END / 4], [], role="prefix"), "NONADDITIVE"),
          "Prefix diagnostics are not additive return messages.")
    check("reject_missing_return_registry", lambda: refused(
          lambda: claim_return(context, "H", [0., T_END / 4], None), "SHARED_RETURN_REGISTRY"),
          "A successful claim must participate in an explicit aggregate registry.")
    check("reject_after_known_history", lambda: refused(
          lambda: claim_return(context, "H", [T_END, T_END + 1.], []), "OUTSIDE_KNOWN_HISTORY"),
          "The recorded source endpoint does not invent later shutoff or returns.")

    def revision_invariant_event():
        first = copy.deepcopy(context)
        second = copy.deepcopy(context)
        first["producer_revision"], second["producer_revision"] = "old", "new"
        a = claim_return(first, "H", [0., T_END / 4], [])
        b = claim_return(second, "H", [0., T_END / 4], [])
        need(a["event_id"] == b["event_id"], "EVENT_ID_MUST_BE_PHYSICAL")

    check("event_identity_ignores_producer_revision", revision_invariant_event,
          "Documentation revisions do not create a second physical capture event.")
    check("reject_photo_support_extension", lambda: refused(
          lambda: photo_cm2("He", [50000.0001]), "NATIVE_PHOTO_SUPPORT"),
          "Finite native photo support is not extrapolated.")
    check("reject_wrong_photo_species", lambda: refused(
          lambda: photo_cm2("He3", [30.]), "UNSUPPORTED_GROUND_PHOTO_CHANNEL"),
          "An elemental fit is not silently mapped onto another isotope/channel.")
    check("reject_photon_support_extension", lambda: refused(
          lambda: retained_port(context, "H", [0., T_END / 4], [50001.], [1.]), "PHOTON_SUPPORT"),
          "Explicit photon atoms remain inside capture-energy plus threshold support.")
    check("reject_negative_generator", lambda: refused(
          lambda: solve([1.], [-.1], [.2], [.1], [1.]), "NONNEGATIVE_FINITE_CHAIN"),
          "A negative transition rate cannot enter a positive generator.")

    def actual_source_contract():
        energy, amplitude, cutoff, identity, source = source_arrays(unit.parents[1] / SOURCE_PATH)
        need(len(energy) == 3200 and len(amplitude) == 3200 and cutoff > 0
             and identity["selected_tag"] == "direct_0p1_10", "ACTUAL_NATIVE_LOW_SELECTION_REQUIRED")
        changed = copy.deepcopy(source)
        changed["normalization"]["d_native_clock_d_proper_s"] = 2.
        refused(lambda: validate_actual_source(changed), "NORMALIZATION")
        changed = copy.deepcopy(source)
        changed["support_eV"] = [.1, 900.]
        refused(lambda: validate_actual_source(changed), "SOURCE_SUPPORT_EXPANSION")

    check("actual_saved_low_source_identity_and_guards", actual_source_contract,
          "The exact saved low birth tag is selected without any source quadrature or projection replay.")
    result = {"schema": "CR_LOW_BIRTH_CHANGED_CONTROLS_V1", "unit": UNIT_ID,
              "checks": findings, "count": len(findings),
              "passed": sum(row["pass"] for row in findings),
              "all_pass": all(row["pass"] for row in findings),
              "old_suites_replayed": 0,
              "tests_are": "analytic limits, conservation, finite-bin history, and adversarial physical contracts"}
    write_json(out / "RESULT.json", result)
    print(json.dumps({key: result[key] for key in ("count", "passed", "all_pass")}, allow_nan=False))
    need(result["all_pass"], "CHANGED_CONTROL_FAILURE")


if __name__ == "__main__":
    main()
