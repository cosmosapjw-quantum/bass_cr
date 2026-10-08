"""Adversarial scope/evidence/accounting tests; synthetic passes are not science."""
import copy
import importlib.util
import json
import math
from pathlib import Path
from fractions import Fraction

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r3m26_budget", ROOT / "scripts/r3m26_budget.py")
budget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(budget)


def synthetic(profile="SELECTED_SPANS_SINGLE_B", evidence="VALIDATED_ESTIMATE"):
    """Entirely fictional estimates for evaluator behavior, never real admission."""
    quantity = dict(model_id="SYNTHETIC_TEST_MODEL", observable_id="SYNTHETIC_TEST_OBSERVABLE",
                    observable_scope="SELECTED_SPANS" if profile.startswith("SELECTED") else "ALL_BOUND",
                    energy_keV_per_u=100., domain={"kind": "SINGLE_B", "b_a0": 2.},
                    units="dimensionless", reference_value=.01)
    if profile == "ALL_BOUND_CROSS_SECTION":
        quantity.update(domain={"kind": "B_INTEGRATED_FROM_ZERO_TO_INFINITY"}, units="a0^2")
    def row(error):
        return dict(quantity=copy.deepcopy(quantity), absolute_error=error,
                    evidence_class=evidence, evidence_refs=["SYNTHETIC_FIXTURE_NOT_REAL_EVIDENCE"],
                    support_scope="FULL_COMPONENT_FOR_DECLARED_QUANTITY",
                    validation=dict(preregistered=True, held_out_checked=True, conservative_envelope_checked=True),
                    certification=dict(proof_checked=True, roundoff_controlled=True))
    components = {name: row(float(budget.ALLOCATIONS[name]) * .01 / 2)
                  for name in budget.PROFILE_COMPONENTS[profile]}
    coupling = row(1e-7)
    coupling.update(accounting="SEPARATE_ADDITIVE",
                    accounting_evidence_refs=["SYNTHETIC_CROSS_EFFECT_ACCOUNTING"])
    return dict(schema=budget.SCHEMA, profile=profile, quantity=quantity, components=components,
                couplings={"h_dt": coupling}, synthetic_fixture=True,
                external_validation={"status": "NOT_EVALUATED"})


def test_empirical_route_can_close_only_declared_numerical_scope():
    result = budget.evaluate_ledger(synthetic())
    assert result["status"] == "NUMERICAL_BUDGET_SATISFIED_MODEL_CONDITIONAL"
    assert result["certified_total_bound"] is None
    assert result["production_admitted"] is False
    assert result["required_relative_total"] == .007
    assert result["external_validation"]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("profile,total", [("SELECTED_SPANS_SINGLE_B", .007),
    ("ALL_BOUND_SINGLE_B", .0085), ("ALL_BOUND_CROSS_SECTION", .01)])
def test_profile_budgets_keep_seven_frozen_allocations(profile, total):
    result = budget.evaluate_ledger(synthetic(profile))
    source = json.loads((ROOT / "docs/roadmap/ERROR_BUDGET.json").read_text())
    assert {key: float(value) for key, value in budget.ALLOCATIONS.items()} == source["allocation_relative"]
    assert result["required_relative_total"] == total


def test_raw_pair_local_only_single_fit_and_missing_do_not_close():
    for field in ("RAW_PAIR_DIFFERENCE", "SINGLE_POWER_FIT", "LOCAL_DIAGNOSTIC_ONLY"):
        ledger = synthetic()
        ledger["components"]["real_time"]["evidence_class"] = field
        result = budget.evaluate_ledger(ledger)
        assert result["status"] == "NUMERICAL_BUDGET_OPEN"
        assert result["additive_total_absolute_error"] is None
    ledger = synthetic()
    del ledger["components"]["preparation"]
    assert budget.evaluate_ledger(ledger)["status"] == "NUMERICAL_BUDGET_OPEN"
    ledger["components"]["spatial"] = None
    assert budget.evaluate_ledger(ledger)["additive_total_absolute_error"] is None
    ledger = synthetic()
    ledger["components"]["real_time"]["support_scope"] = "LOCAL_ONLY"
    assert budget.evaluate_ledger(ledger)["status"] == "NUMERICAL_BUDGET_OPEN"
    ledger = synthetic()
    ledger["components"]["real_time"]["validation"]["held_out_checked"] = False
    assert budget.evaluate_ledger(ledger)["status"] == "NUMERICAL_BUDGET_OPEN"


@pytest.mark.parametrize("replacement", [True, -1., math.nan, math.inf, "0.0"])
def test_invalid_error_numbers_cannot_hide_as_zero(replacement):
    ledger = synthetic()
    ledger["components"]["preparation"]["absolute_error"] = replacement
    with pytest.raises(ValueError):
        budget.evaluate_ledger(ledger)


def test_identity_and_completeness_mismatches_rejected():
    for field, value in [("model_id", "OTHER_MODEL"), ("observable_id", "P_DIFFERENT"),
                         ("energy_keV_per_u", 225), ("units", "a0^2"),
                         ("reference_value", .02), ("domain", {"kind": "SINGLE_B", "b_a0": 3.})]:
        ledger = synthetic()
        ledger["components"]["preparation"]["quantity"][field] = value
        with pytest.raises(ValueError):
            budget.evaluate_ledger(ledger)
    ledger = synthetic()
    ledger["profile"] = "ALL_BOUND_SINGLE_B"
    with pytest.raises(ValueError, match="scope"):
        budget.evaluate_ledger(ledger)
    ledger = synthetic()
    ledger["quantity"]["reference_value"] = 0
    with pytest.raises(ValueError, match="reference"):
        budget.evaluate_ledger(ledger)


def test_h_dt_required_and_accounted_exactly_once():
    separate = synthetic()
    separate_result = budget.evaluate_ledger(separate)
    missing = copy.deepcopy(separate)
    del missing["couplings"]["h_dt"]
    assert budget.evaluate_ledger(missing)["status"] == "NUMERICAL_BUDGET_OPEN"
    included = copy.deepcopy(separate)
    included["couplings"]["h_dt"]["accounting"] = "INCLUDED_IN_SPATIAL"
    included["components"]["spatial"]["includes_couplings"] = ["h_dt"]
    included_result = budget.evaluate_ledger(included)
    assert separate_result["additive_total_absolute_error"] - included_result["additive_total_absolute_error"] == pytest.approx(1e-7)
    included["components"]["spatial"]["absolute_error"] = 1e-8
    with pytest.raises(ValueError, match="spatial.*coupling"):
        budget.evaluate_ledger(included)
    separate["components"]["spatial"]["includes_couplings"] = ["h_dt"]
    with pytest.raises(ValueError, match="account"):
        budget.evaluate_ledger(separate)


def test_l1_total_and_component_caps_both_required_without_rss():
    ledger = synthetic()
    for name, component in ledger["components"].items():
        component["absolute_error"] = float(budget.ALLOCATIONS[name]) * .01
    result = budget.evaluate_ledger(ledger)
    assert result["status"] == "NUMERICAL_BUDGET_EXCEEDED"
    assert result["total_within_budget"] is False  # Separate coupling consumes the residual headroom.
    ledger = synthetic()
    ledger["components"]["real_time"]["absolute_error"] = .0000101
    result = budget.evaluate_ledger(ledger)
    assert result["status"] == "NUMERICAL_BUDGET_EXCEEDED"
    assert result["total_within_budget"] is True


def test_certification_needs_every_component_and_coupling_and_exact_sum():
    ledger = synthetic(evidence="CERTIFIED_BOUND")
    result = budget.evaluate_ledger(ledger)
    assert result["certified_total_bound"] is not None
    assert isinstance(result["certified_total_bound"]["numerator"], int)
    assert isinstance(result["certified_total_bound"]["denominator"], int)
    ledger["couplings"]["h_dt"]["evidence_class"] = "VALIDATED_ESTIMATE"
    assert budget.evaluate_ledger(ledger)["certified_total_bound"] is None
    ledger = synthetic(evidence="CERTIFIED_BOUND")
    ledger["components"]["real_time"]["certification"]["roundoff_controlled"] = False
    assert budget.evaluate_ledger(ledger)["status"] == "NUMERICAL_BUDGET_OPEN"


def test_json_decimal_boundary_preserved_before_fraction_conversion(tmp_path):
    ledger = synthetic(evidence="CERTIFIED_BOUND")
    ledger["components"]["real_time"]["absolute_error"] = .00001
    raw = json.dumps(ledger).replace('"absolute_error": 1e-05',
                                    '"absolute_error": 0.00001000000000000000001')
    assert raw != json.dumps(ledger)
    path = tmp_path / "strict_decimal.json"
    path.write_text(raw)
    result = budget.evaluate_ledger(budget.load_json(path))
    assert result["status"] == "NUMERICAL_BUDGET_EXCEEDED"
    assert result["components"]["real_time"]["reported_value_exceeds_allocation"] is True
    exact = result["components"]["real_time"]["absolute_error_exact"]
    assert Fraction(exact["numerator"], exact["denominator"]) == Fraction("0.00001000000000000000001")
    bound = result["certified_total_bound"]
    assert Fraction(bound["numerator"], bound["denominator"]) == Fraction(401, 10000000) + Fraction("1e-23")
    json.dumps(result, allow_nan=False)  # exact input must still produce valid JSON evidence


def test_projection_bound_is_sharp_and_stable_relative_inverse():
    p, delta = .01, .002
    error = (math.sqrt(p) + delta)**2 - p
    assert budget.projection_probability_error(p, delta) == pytest.approx(error)
    assert budget.projection_probability_error(0., delta) == delta**2
    for goal in (0., 1e-16, .001, 1.):
        d = budget.sufficient_state_error(p, goal)
        assert budget.projection_probability_error(p, d) == pytest.approx(p * goal, rel=2e-15, abs=0.)
    with pytest.raises(ValueError, match="relative"):
        budget.sufficient_state_error(0., .01)
    with pytest.raises(ValueError):
        budget.projection_probability_error(True, .1)
