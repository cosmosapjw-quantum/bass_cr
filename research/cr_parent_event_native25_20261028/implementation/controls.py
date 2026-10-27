#!/usr/bin/env python3
"""Meaningful new synthetic controls; no old source/RR replay.

This file is prospective until the separate new-unit C4 admits its worker.
Each selected action records its own outcome. A unique recovery run may select
one named changed control with --only; completed unchanged controls need not be
rerun. No control count or PASS is asserted before the worker actually runs.
"""
import argparse
import copy
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import math
import os
from pathlib import Path


UNIT = Path(__file__).resolve().parents[1]
UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"


def ensure(condition, reason="CONTROL_ASSERTION_FAILED"):
    if not condition:
        raise AssertionError(reason)


def rejects(action, reason):
    try:
        action()
    except (ValueError, ArithmeticError) as error:
        ensure(reason in str(error), "WRONG_REFUSAL:"+str(error))
        return
    raise AssertionError("EXPECTED_REFUSAL:"+reason)


def admitted_out(value):
    out = Path(value).resolve()
    ensure(UNIT.name == "cr_parent_event_native25_20261028" and UNIT.parent.name == "research",
           "EXACT_NEW_UNIT_REQUIRED")
    ensure(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID
           and os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "BOUNDED_ENV_REQUIRED")
    ensure(out.parent == UNIT / "runs" and out.is_dir(), "RUNNER_CREATED_OUTPUT_REQUIRED")
    reservation = json.loads((out / "RESERVATION.json").read_bytes())
    ensure(reservation.get("unit") == UNIT_ID and reservation.get("run_id") == out.name
           and reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID"),
           "ACTUAL_RESERVATION_REQUIRED")
    ensure(reservation.get("native_threads") == 1
           and reservation.get("selected_worker_memory_limit_bytes") == 268435456,
           "EXACT_RESOURCE_ADMISSION_REQUIRED")
    return out


def build_controls(p, prepared):
    controls = []
    def case(name):
        def decorate(action):
            controls.append((name, action))
            return action
        return decorate

    def altered_binding(**changes):
        context = p.actual_binding_context()
        context.update(changes)
        return context

    @case("missing_history_keeps_rate_exposure_and_native_null")
    def missing_history():
        result = p.validate_binding(altered_binding(history_s=None))
        ensure(result["status"] == "UNBOUND_HISTORY_NO_INFERENCE")
        ensure(all(result[key] is None for key in ("derived_rate", "exposure", "finite_event_N_E", "native25")))

    @case("missing_nb_keeps_per_baryon_null_with_separate_density_history")
    def missing_nb():
        result = p.validate_binding(altered_binding(donor_nb_m3=None, recipient_nb_m3=None))
        ensure(result["status"] == "UNBOUND_SAME_STATE_NB")
        ensure(result["native25"] is None and result["per_baryon_values"] is None
               and result["proper_density_history_bound"] is True)

    @case("missing_recipient_state_does_not_adopt_same_temperature")
    def missing_recipient():
        result = p.validate_binding(altered_binding(recipient_state_id=None))
        ensure(result["status"] == "UNBOUND_SAME_STATE_NB" and result["native25"] is None)

    mismatch_cases = (
        ("same_T_wrong_total_nuclei_rejected", "nH_m3", "138.6"),
        ("neutral_vs_total_semantics_rejected", "nH_semantics", "neutral_HI"),
        ("same_T_wrong_ion_fraction_rejected", "xHeII", "0.1"),
        ("wrong_10000K_bath_rejected", "temperature_K", "10000"),
        ("wrong_isotope_mapping_rejected", "isotope_mapping", "CONDITIONAL_ELEMENTAL_HE_TO_HE3"),
        ("mixed_frame_rejected", "recipient_frame", "unrelated_comoving_frame"),
        ("wrong_proper_clock_rejected", "proper_clock", "conditional_mean_time"),
        ("second_proper729_factor_rejected", "additional_source_multiplier", 729.),
        ("second_nb_division_rejected", "per_baryon_already_applied", True),
        ("second_eV_conversion_rejected", "energy_unit_conversion_already_applied", True),
        ("source_hash_mismatch_rejected", "source_record_sha256", "0"*64),
        ("source_revision_mismatch_rejected", "source_revision", "0"*40),
        ("selected_birth_tag_not_current_energy_filter", "birth_tag", "selected_total"),
        ("birth_support_extension_rejected", "native_birth_support_eV", [.1, 900.]),
        ("unprovided_absolute_volume_not_assumed_one", "proper_volume_m3", 1.),
    )
    for name, key, value in mismatch_cases:
        @case(name)
        def binding_mismatch(key=key, value=value):
            rejects(lambda: p.validate_binding(altered_binding(**{key: value})), "WRONG_OR_MIXED_BINDING:"+key)

    @case("foreign_explicit_nb_rejected")
    def wrong_nb():
        rejects(lambda: p.validate_binding(altered_binding(recipient_nb_m3="187")), "WRONG_OR_FOREIGN_BARYON_DENSITY")

    @case("history_continuation_not_inferred")
    def wrong_history():
        rejects(lambda: p.validate_binding(altered_binding(history_s=[0., 2e10])), "WRONG_PROPER_HISTORY_OR_CLOCK")

    @case("zero_width_moments_exact_zero")
    def zero_moments():
        ensure(p.positive_moments("13.605693122994", "0.1", "0.1") == (Decimal(0),)*4)

    @case("nonpositive_I_and_invalid_bands_refused")
    def invalid_moments():
        for args in ((0, 0, 1), (-1, 0, 1), (13, -1, 1), (13, 2, 1), (13, 0, 1001)):
            rejects(lambda args=args: p.positive_moments(*args), "MOMENT_DOMAIN")
        rejects(lambda: p.positive_moments(float("nan"), 0, 1), "NONFINITE_SCALAR")

    @case("positive_primitives_independent_antiderivative")
    def primitive_oracle():
        def anti(I, W):
            u = 1+W/I
            n0 = -I/(2*u*u)
            n1 = I*(-1/u+1/(2*u*u))
            e0 = I*n1
            e1 = I*I*(u.ln()+2/u-1/(2*u*u))
            return n0, n1, e0, e1
        for I, a, b in (("13.605693122994", "0", "0.1"), ("24.59", "3", "10"),
                        ("13.605693122994", "100", "1000"), ("24.59", "0", "0.000001")):
            I, a, b = map(Decimal, (I, a, b))
            low, high = anti(I, a), anti(I, b)
            expected = [right-left for left, right in zip(low, high)]
            actual = p.positive_moments(I, a, b)
            ensure(all(value > 0 for value in actual))
            ensure(all(abs(value-reference) <= Decimal("1e-45")*abs(reference)
                       for value, reference in zip(actual, expected)), "INDEPENDENT_PRIMITIVE_MISMATCH")

    @case("zero_width_finite_window_and_outside_history")
    def finite_window():
        ensure(p.finite_source_factor(3, 3) == 0)
        rejects(lambda: p.finite_source_factor(-1, 1), "QUERY_OUTSIDE_KNOWN_PROPER_HISTORY")
        rejects(lambda: p.finite_source_factor(1e10, 1e10+1), "QUERY_OUTSIDE_KNOWN_PROPER_HISTORY")

    @case("absolute_source_clock_not_bin_local_reset")
    def absolute_clock():
        ensure(p.finite_source_factor(2, 3) == Decimal("2.5"))
        ensure(p.finite_source_factor(2, 3) == 5*p.finite_source_factor(0, 1))

    @case("conditioning_gate_rejects_singular_scale_without_fallback")
    def condition_gate():
        B = [[p.D(1), p.D(0), p.D(0)], [p.D(0), p.D(1), p.D(0)], [p.D(0), p.D(0), p.D("1e-12")]]
        inv = [[p.D(1), p.D(0), p.D(0)], [p.D(0), p.D(1), p.D(0)], [p.D(0), p.D(0), p.D("1e12")]]
        _rc, _s, _lower, checks = p.recovery_metrics(B, inv, [p.D(1), p.D(1), p.D("1e12")])
        ensure(checks[0]["pass"] is False)
        rejects(lambda: p.inverse3([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), "SINGULAR_THREE_BASIS_MATRIX")

    @case("nonpositive_envelope_and_excess_sensitivity_refused")
    def envelope_gates():
        identity = [[p.D(int(i == j)) for j in range(3)] for i in range(3)]
        negative = p.recovery_metrics(identity, identity, [p.D(1), p.D(1), p.D(-1)])[3]
        sensitive = p.recovery_metrics(identity, identity, [p.D(1), p.D(1), p.D("1e-7")])[3]
        ensure(negative[2]["pass"] is False and sensitive[1]["pass"] is False)

    @case("holdouts_remain_unused_and_three_coefficient_only")
    def holdout_scope():
        fit = prepared["coefficient_identification"]
        ensure(fit["theta_order"] == ["theta_H", "theta_He1", "theta_He2"])
        ensure(len(fit["theta_decimal"]) == 3 and fit["fourth_coefficient_fit"] is False)
        ensure(all(row["used_for_fit"] is False for row in fit["holdout_results"]))
        ensure([tuple(row["interval_eV"]) for row in fit["holdout_results"]] == list(p.HOLDOUT))

    @case("canonical_exact_zero_is_not_a_relative_floor")
    def zero_atom():
        ensure(p.own_scale_error(0, 0) == 0)
        rejects(lambda: p.own_scale_error("1e-99", 0), "NONZERO_PREDICTION_ON_EXACT_ZERO_REFERENCE")

    @case("original_Q8_projector_count_energy_and_separate_ghost")
    def projector_identity():
        import numpy as np
        energy = np.asarray([.1, .35, 1.7, 10.])
        K, _x, _w, qn, qe = p.q8_project_basis(energy)
        for i in range(3):
            number = math.fsum(map(float, K[:, i]))
            kinetic = math.fsum(float(e)*float(v) for e, v in zip(energy, K[:, i]))
            ensure(abs(number-qn[i]) <= 1e-11*abs(qn[i]))
            ensure(abs(kinetic-qe[i]) <= 1e-11*abs(qe[i]))
            ensure(K[0, i] > 0 and math.fsum(map(float, K[1:, i])) < qn[i])

    @case("pointwise_target_fraction_is_not_projected_target")
    def noncommuting_fraction():
        import numpy as np
        energy = np.asarray([.1, .35, 1.7, 10.])
        K, _x, _w, _qn, _qe = p.q8_project_basis(energy)
        H, He = .7*K[:, 0], .9*K[:, 1]+.2*K[:, 2]
        xh, xe = energy/13.605693122994, energy/24.59
        point_H = .7*((7./3)+xh)/(1+xh)**3
        point_He = (.9+.2*xe)/(1+xe)**3
        wrong = (H+He)*point_H/(point_H+point_He)
        ensure(float(np.max(np.abs(wrong-H)/H)) > 1e-6, "SHORTCUT_WITNESS_NOT_DISTINCT")

    @case("actual_preparation_keeps_original_grid_and_atoms_readonly")
    def preparation_scope():
        artifact = prepared["artifacts"]["ATTRIBUTION_ARRAYS.npz"]
        ensure(artifact["arrays"]["energy_eV_with_cutoff"]["shape"] == [3201])
        ensure(artifact["arrays"]["canonical_A_m3_s2"]["shape"] == [3201])
        ensure(prepared["projection_validation"]["canonical_source_replaced"] is False)
        ensure(prepared["projection_validation"]["residual_reassigned"] is False)
        ensure(prepared["projection_validation"]["new_source_normalization_factors"] == [])

    @case("actual_He_parameters_remain_null_not_intercept_default")
    def He_null():
        family = p.native_affine(6, 4, 1, .5)
        ensure(family["actual_parameters"] == {"s": None, "p": None, "d": None})
        ensure(family["intercept_is_actual_branch"] is False)
        rejects(lambda: p.evaluate_family(family, None, None), "NO_DEFAULT_ACTUAL_HE_BRANCH")

    @case("negative_or_excess_He_branch_parameters_refused")
    def He_domain():
        family = p.native_affine(6, 4, 1, .5)
        for v in ((-1, 0), (0, -1), (3, 1), (0, 3)):
            rejects(lambda v=v: p.evaluate_family(family, *v), "HE_SELECTED_MARGINAL_DOMAIN_REFUSED")
        # A strictly positive excess must not disappear in an 80-digit sum.
        rejects(lambda: p.evaluate_family(family, Decimal("1e-100"), Decimal(2)),
                "HE_SELECTED_MARGINAL_DOMAIN_REFUSED")

    @case("exact_He_half_quarter_boundary_and_prior_extent")
    def exact_He_boundary():
        coefficient = p.D(prepared["projection_validation"]["target_totals"]["He"]["number_coefficient_m3_s2"])
        previous = Decimal(0)
        for index, endpoint in enumerate(p.TIMES):
            prefix_marginal = p.finite_source_factor(0, endpoint)*coefficient
            beginning = 0 if index == 0 else p.TIMES[index-1]
            bin_marginal = p.finite_source_factor(beginning, endpoint)*coefficient
            # Real saved-attribution extents, plus the prior-prefix boundary
            # used by bin fixtures; no coefficient fit/projection is repeated.
            for marginal in (prefix_marginal, bin_marginal, previous):
                family = p.native_affine(0, marginal, 0, 0)
                for fraction in (Fraction(1, 4), Fraction(1, 2)):
                    expected_d = Fraction(marginal)*fraction
                    d = p.exact_terminating_decimal(expected_d)
                    s = p.exact_terminating_decimal(Fraction(marginal)-2*Fraction(d))
                    ensure(Fraction(d) == expected_d)
                    ensure(Fraction(s)+2*Fraction(d) == Fraction(marginal) and s >= 0)
                    if fraction == Fraction(1, 2):
                        ensure(s == 0)
                    p.evaluate_family(family, 0, d)
            previous = prefix_marginal
        rejects(lambda: p.exact_terminating_decimal(Fraction(1, 3)), "NONTERMINATING_DECIMAL_REFUSED")

    @case("mixed_partner_He_baryon_and_charge_ledger")
    def He_partner():
        family = p.native_affine(6, 4, 1, .5)
        values = p.evaluate_family(family, 1, Decimal("0.5"))
        nb = p.D("8750/47")
        density = [value*nb for value in values]
        expected = {1: Decimal(-5), 2: Decimal(5), 10: Decimal(-3),
                    11: Decimal("1.5"), 12: Decimal("1.5")}
        ensure(all(abs(density[i]-value) < Decimal("1e-65") for i, value in expected.items()))
        ensure(abs(sum(p.D(a)*v for a, v in zip(p.MASSES, density))) < Decimal("1e-65"))
        ensure(abs(sum(p.D(q)*v for q, v in zip(p.CHARGES, density))-Decimal("9.5")) < Decimal("1e-65"))

    @case("valid_marginal_domain_does_not_close_partner_response")
    def no_activation():
        family = p.native_affine(6, 4, 1, .5)
        p.evaluate_family(family, 1, .5)
        rejects(lambda: p.refuse_unclosed_activation(family, exclusive_branch={"p": 1, "d": .5}),
                "FULL_ACTIVATION_REQUIRES_EXCLUSIVE_BRANCH_AND_PARTNER_RESPONSE")
        rejects(lambda: p.refuse_unclosed_activation(family, exclusive_branch={}, partner_response={}),
                "ACTUAL_FULL_CONSUMER_ACTIVATION_NOT_ADMITTED")

    @case("two_part_species_domain_preserves_tiny_negative_increment")
    def negative_species():
        family = p.native_affine(0, 0, Decimal("1e-60"), 0)
        base = [p.D(value) for value in p.baseline_inventory()["Y_decimal"]]
        base[2] = Decimal(0)
        rejects(lambda: p.evaluate_family(family, 0, 0, baseline_Y=base),
                "NEGATIVE_TWO_PART_RECIPIENT_SPECIES_REFUSED")

    @case("rare_RR_scalar_survives_separate_serialization")
    def rare_scalar():
        rare = 4.6363591070009445e-27
        family = p.native_affine(1, 1, rare, 1e-28)
        packet = {"source": "1", "C_H": rare, "C_H_hex": rare.hex(), "native_affine_Y": family}
        decoded = json.loads(json.dumps(packet, allow_nan=False))
        ensure(decoded["C_H"].hex() == rare.hex() == decoded["C_H_hex"])
        ensure(decoded["native_affine_Y"]["intercept_decimal"] == family["intercept_decimal"])
        ensure(float(1-rare) == 1., "SYNTHETIC_CANCELLATION_WITNESS")

    @case("signed_bin_active_changes_not_clipped")
    def signed_active():
        result = p.selected_nonthermal(-3, -2, 1, .1)
        ensure(p.D(result["retention"]["delta_zeta"]) < 0)
        ensure(p.D(result["assimilation_fixture"]["delta_zeta"]) < 0)
        ensure(p.D(result["retention"]["delta_w_nt_J_per_baryon"]) < 0)
        ensure(result["actual_full_nonthermal_state"] is None)

    def energy_fixture():
        return {"role": "nonadditive_cumulative_prefix", "active_energy_eV_m3": 10.,
            "injected_energy_eV_m3": 40., "cutoff_energy_eV_m3": .4, "coulomb_energy_eV_m3": 20.,
            "kinetic_energy_residual_eV_m3": 0., "total_energy_residual_eV_m3": 0.,
            "channels": {"H": {"capture_number_m3": 2., "retained_photon_energy_eV_m3": 33.2},
                         "He": {"capture_number_m3": 1., "retained_photon_energy_eV_m3": 28.19}}}

    @case("literal_threshold_bridge_separate_from_branch_work_and_heat")
    def energy_bridge():
        result = p.energy_sidecars(8, 4, energy_fixture())
        ensure(p.D(result["literal_H_difference_eV"]) == Decimal("0.005693122994"))
        ensure(p.D(result["literal_convention_residual_eV_m3"]) == Decimal("0.005693122994")*8)
        ensure(p.D(result["branch_lift"]["coefficient_p_eV"]) == Decimal("54.42"))
        ensure(p.D(result["branch_lift"]["coefficient_d_eV"]) == Decimal("29.83"))
        ensure(result["actual_I2_source_eV"] is None and result["actual_external_work"] is None)
        ensure(result["literal_or_branch_residual_deposited_as_heat"] is False)
        ensure(abs(p.D(result["balance_residual_after_saved_eV_m3"])) < Decimal("1e-65"))

    @case("caloric_requires_explicit_EOS_and_partner_closure")
    def caloric_closure():
        rejects(lambda: p.finite_caloric("1e-20", 1, prior_Q_J_m3=0, prior_n_thermal_m3=0, closure=None),
                "EXPLICIT_PARTNER_EOS_CLOSURE_REQUIRED")

    @case("positive_energy_can_cool_when_new_thermal_particles_enter")
    def caloric_sign():
        cvT = Decimal("1.380649e-23")*Decimal(150)
        result = p.finite_caloric(cvT/2, 1, prior_Q_J_m3=0, prior_n_thermal_m3=0, closure=p.closed_caloric_fixture())
        ensure(p.D(result["delta_T_ratio"]) < 0 and p.D(result["delta_logT"]) < 0)
        ensure(result["physical_heating_complete"] is False)

    @case("stable_log_increment_survives_rounded_temperature_endpoint")
    def tiny_caloric():
        n0 = p.D(p.baseline_inventory()["n_part0_m3_decimal"])
        U0 = Decimal("1.380649e-23")*Decimal(150)*n0
        result = p.finite_caloric(U0*Decimal("1e-25"), 0, prior_Q_J_m3=0, prior_n_thermal_m3=0,
                                  closure=p.closed_caloric_fixture())
        ensure(p.D(result["delta_logT"]) > 0 and result["delta_logT_float64"] > 0)
        ensure(100.*(1.+float(result["delta_T_ratio"])) == 100.)

    @case("caloric_bins_use_prior_endpoint_and_telescope")
    def prior_caloric():
        n0 = p.D(p.baseline_inventory()["n_part0_m3_decimal"])
        U0 = Decimal("1.380649e-23")*Decimal(150)*n0
        q1, q2, n1, n2 = U0/2, U0/7, Decimal(3), Decimal(1)
        closure = p.closed_caloric_fixture()
        first = p.finite_caloric(q1, n1, prior_Q_J_m3=0, prior_n_thermal_m3=0, closure=closure)
        second = p.finite_caloric(q2, n2, prior_Q_J_m3=q1, prior_n_thermal_m3=n1, closure=closure)
        total = p.finite_caloric(q1+q2, n1+n2, prior_Q_J_m3=0, prior_n_thermal_m3=0, closure=closure)
        wrong = p.finite_caloric(q2, n2, prior_Q_J_m3=0, prior_n_thermal_m3=0, closure=closure)
        ensure(abs(p.D(first["delta_logT"])+p.D(second["delta_logT"])-p.D(total["delta_logT"])) < Decimal("1e-60"))
        ensure(abs(p.D(second["delta_logT"])-p.D(wrong["delta_logT"])) > Decimal("1e-6"))

    def claim_packet(a=0., b=2., support=(.1, 10.)):
        return {"role": "disjoint_observation_bin", "interval_s": [a, b],
            "claim_identity": {"family_id": p.FAMILY, "recipient_identity": p.STATE,
                               "native_birth_support_eV": list(support), "selected_response_sha256": p.RR_RESULT_SHA}}

    @case("same_event_alias_and_overlapping_interval_rejected")
    def same_event():
        registry = []
        packet = claim_packet()
        p.claim_components(packet, registry)
        alias = copy.deepcopy(packet)
        alias["producer_revision"] = "f"*40
        rejects(lambda: p.claim_components(alias, registry), "SAME_EVENT_OVERLAP")
        rejects(lambda: p.claim_components(claim_packet(1., 3.), registry), "SAME_EVENT_OVERLAP")

    @case("touching_time_or_birth_support_edges_not_double_counted")
    def disjoint_claims():
        registry = []
        p.claim_components(claim_packet(0., 2.), registry)
        p.claim_components(claim_packet(2., 3.), registry)
        separate = []
        p.claim_components(claim_packet(0., 2., (.1, 5.)), separate)
        p.claim_components(claim_packet(0., 2., (5., 10.)), separate)
        ensure(len(registry) == 8 and len(separate) == 8)

    @case("nonadditive_prefix_and_conditional_fixture_claim_refused")
    def forbidden_claim():
        prefix = claim_packet()
        prefix["role"] = "nonadditive_cumulative_prefix"
        rejects(lambda: p.claim_components(prefix, []), "CUMULATIVE_PREFIX_IS_NOT_ADDITIVE")
        fixture = claim_packet()
        fixture["conditional_fixture"] = True
        rejects(lambda: p.claim_components(fixture, []), "CONDITIONAL_FIXTURE_IS_NOT_ACTUAL_FAMILY_CLAIM")

    @case("aggregate_and_prior_RR_duplicate_rejected_in_both_orders")
    def duplicate_RR():
        rr = {"family_id": p.FAMILY, "channel": "H", "native_birth_support_eV": [.1, 10.],
              "observation_bin_s": [0., 2.], "horizon": "finite_known_history_observation_bin"}
        aggregate_first = []
        p.claim_components(claim_packet(), aggregate_first)
        rejects(lambda: p.claim_saved_rr_component(rr, aggregate_first), "AGGREGATE_PRIOR_RR_DUPLICATION")
        rr_first = []
        p.claim_saved_rr_component(rr, rr_first)
        before = copy.deepcopy(rr_first)
        rejects(lambda: p.claim_components(claim_packet(), rr_first), "AGGREGATE_PRIOR_RR_DUPLICATION")
        ensure(rr_first == before, "FAILED_BATCH_MUST_NOT_PARTIALLY_REGISTER_BIRTH")

    @case("ownership_support_extension_refused")
    def claim_support():
        rejects(lambda: p.claim_components(claim_packet(support=(.1, 900.)), []), "CLAIM_SUPPORT_EXTENSION_REFUSED")

    @case("retained_photon_reference_keeps_original_atoms_and_null_transport")
    def photon_reference():
        retained = p.load_retained_inputs()
        row = retained["saved"]["observation_bins"][0]
        descriptor = p.retained_photon_descriptor(retained, row, 0)
        for channel in ("H", "He"):
            item = descriptor[channel]
            ensure(item["arrays_file"]["sha256"] == p.RR_ARRAYS_SHA)
            ensure(item["count_member"] == "capture_"+channel+"_bins_m3")
            ensure(item["energy_member"] == "photon_"+channel+"_energy_eV")
            ensure(item["saved_port"] == row["retained_photon_ports"][channel])
            ensure(item["source_moments_inverted"] is False and item["continuous_time_spectrum"] is None)
            ensure(item["escape_or_absorption"] is None and item["actual_physical_heating"] is None)
            ensure(item["retained_photon_w_ext_contribution"] == 0)

    return controls


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--only", action="append", help="exact named changed control; repeat to select more than one")
    args = parser.parse_args(argv)
    out = admitted_out(args.out)
    # Only the new production module is imported, after actual runner binding.
    import parent_event as p
    with localcontext() as context:
        context.prec = p.PRECISION
        prepared, _arrays, prepared_identity = p.load_preparation(args.prepared)
        cases = build_controls(p, prepared)
        names = [name for name, _action in cases]
        ensure(len(names) == len(set(names)), "CONTROL_NAMES_MUST_BE_UNIQUE")
        selected = names if args.only is None else args.only
        ensure(len(selected) == len(set(selected)) and set(selected) <= set(names), "UNKNOWN_OR_DUPLICATE_CONTROL_SELECTION")
        outcomes = []
        for name, action in cases:
            if name not in selected:
                continue
            try:
                action()
                outcomes.append({"name": name, "pass": True})
            except Exception as error:
                outcomes.append({"name": name, "pass": False, "exception_type": type(error).__name__, "reason": str(error)})
        passed = all(row["pass"] for row in outcomes)
        p.write_json_new(out / "RESULT.json", {"schema": "CR_PARENT_EVENT_CONTROLS_V1", "unit": UNIT_ID,
            "status": "PASS" if passed else "FAILED", "checks": outcomes,
            "passed_checks": sum(row["pass"] for row in outcomes), "total_checks": len(outcomes),
            "selection": "all_current_controls" if args.only is None else "explicit_changed_controls_only",
            "selected_names": selected, "unselected_controls_rerun": False,
            "preparation": prepared_identity, "old_science_replay": 0,
            "conditional_fixtures_are_actual_branch_data": False,
            "global_physical_completion": None, "physical_heating_complete": False})
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
