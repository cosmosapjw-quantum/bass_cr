"""Typed, model-conditional numerical error ledger; never a production runner.

Numbers and evidence declarations are checked, not independently proved by this
utility. A VALIDATED_ESTIMATE must declare preregistration, a held-out check and
a conservative envelope for the complete component of the stated quantity.
Raw pairs, a single fit and local-only diagnostics remain unadmitted. A declared
CERTIFIED_BOUND additionally requires proof/roundoff checks. Evidence references
remain inspectable authority inputs; a JSON label alone cannot establish them.

The seven fixed allocations are inherited from docs/roadmap/ERROR_BUDGET.json.
Profiles are different products, not aliases. Required errors combine by L1;
no independence/RSS assumption or automatic paper/AOCC prerequisite is added.
The required h-dt coupling is included once, either additively or within the
spatial estimate. Missing error components are never silently assigned zero.

JSON decimals are parsed as Decimal before any binary-float conversion. Budget
arithmetic uses exact rationals of those input values (or decimal repr values
for a caller supplying Python floats). A certified
sum is returned as a numerator/denominator pair, not a rounded-down float. This
does not make empirical inputs, Python helper calculations, or declarations into
formal certificates. Floating display totals are explicitly noncertified.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from fractions import Fraction
import json
import math
from pathlib import Path

SCHEMA = "BASS_CR_R3M26_TYPED_ERROR_LEDGER_V1"
ALLOCATIONS = {
    "preparation": Fraction("0.0015"),
    "spatial": Fraction("0.003"),
    "real_time": Fraction("0.001"),
    "box_CAP_finite_time": Fraction("0.0015"),
    "bound_channel_truncation": Fraction("0.0015"),
    "b_quadrature": Fraction("0.001"),
    "b_tail": Fraction("0.0005"),
}
PROFILE_COMPONENTS = {
    "SELECTED_SPANS_SINGLE_B": tuple(ALLOCATIONS)[:4],
    "ALL_BOUND_SINGLE_B": tuple(ALLOCATIONS)[:5],
    "ALL_BOUND_CROSS_SECTION": tuple(ALLOCATIONS),
}
QUANTITY_KEYS = {"model_id", "observable_id", "observable_scope", "energy_keV_per_u",
                 "domain", "units", "reference_value"}
ADMITTED_CLASSES = {"VALIDATED_ESTIMATE", "CERTIFIED_BOUND"}


def _number(value, name, *, positive=False):
    if (type(value) not in (int, float, Decimal)
            or (type(value) is float and not math.isfinite(value))
            or (type(value) is Decimal and not value.is_finite())):
        raise ValueError(f"{name} must be a finite number, not bool/string")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return Fraction(str(value))


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _refs(value):
    return isinstance(value, list) and bool(value) and all(_nonempty(item) for item in value)


def _quantity(value, profile):
    if not isinstance(value, dict) or set(value) != QUANTITY_KEYS:
        raise ValueError("explicit complete quantity identity required")
    for key in ("model_id", "observable_id", "observable_scope", "units"):
        if not _nonempty(value[key]):
            raise ValueError(f"invalid quantity {key}")
    expected_scope = "SELECTED_SPANS" if profile == "SELECTED_SPANS_SINGLE_B" else "ALL_BOUND"
    if value["observable_scope"] != expected_scope:
        raise ValueError("observable completeness scope does not match profile")
    normalized = dict(value)
    normalized["energy_keV_per_u"] = _number(value["energy_keV_per_u"], "energy", positive=True)
    normalized["reference_value"] = _number(value["reference_value"], "reference_value", positive=True)
    domain = value["domain"]
    if profile == "ALL_BOUND_CROSS_SECTION":
        if domain != {"kind": "B_INTEGRATED_FROM_ZERO_TO_INFINITY"} or value["units"] != "a0^2":
            raise ValueError("cross-section domain/units require all-b integral in a0^2")
    else:
        if not isinstance(domain, dict) or set(domain) != {"kind", "b_a0"} or domain["kind"] != "SINGLE_B":
            raise ValueError("single-b domain required")
        if value["units"] != "dimensionless":
            raise ValueError("single-b probability units must be dimensionless")
        normalized["domain"] = {"kind": "SINGLE_B", "b_a0": _number(domain["b_a0"], "impact parameter")}
    return normalized


def _exact(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def _display(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("combined error cannot be displayed as finite floating value")
    return result


def _display_tree(value):
    """JSON-safe display numbers; exact numeric identities are returned separately."""
    if type(value) is Decimal:
        return _display(Fraction(value))
    if isinstance(value, dict):
        return {key: _display_tree(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_display_tree(item) for item in value]
    return value


def _identity_exact_tree(value):
    if isinstance(value, Fraction):
        return _exact(value)
    if isinstance(value, dict):
        return {key: _identity_exact_tree(item) for key, item in value.items()}
    return value


def _row(name, row, quantity, profile, allocation=None):
    if row is None:
        return dict(status="MISSING", admitted=False, absolute_error=None,
                    evidence_class=None, evidence_refs=[], reasons=["MISSING_COMPONENT"]), None
    if not isinstance(row, dict):
        raise ValueError(f"{name} must be a component object")
    if _quantity(row.get("quantity"), profile) != quantity:
        raise ValueError(f"{name} quantity identity mismatch")
    absolute = row.get("absolute_error")
    error = None if absolute is None else _number(absolute, f"{name}.absolute_error")
    reasons = []
    evidence_class = row.get("evidence_class")
    if not isinstance(evidence_class, str) or evidence_class not in ADMITTED_CLASSES:
        reasons.append("EVIDENCE_CLASS_NOT_ADMISSIBLE")
    if error is None:
        reasons.append("MISSING_ERROR_ESTIMATE")
    if not _refs(row.get("evidence_refs")):
        reasons.append("MISSING_EVIDENCE_REFERENCES")
    if row.get("support_scope") != "FULL_COMPONENT_FOR_DECLARED_QUANTITY":
        reasons.append("LOCAL_OR_UNDECLARED_SUPPORT_SCOPE")
    if evidence_class == "VALIDATED_ESTIMATE":
        validation = row.get("validation")
        for key in ("preregistered", "held_out_checked", "conservative_envelope_checked"):
            if not isinstance(validation, dict) or validation.get(key) is not True:
                reasons.append(f"VALIDATED_ESTIMATE_REQUIRES_{key.upper()}")
    if evidence_class == "CERTIFIED_BOUND":
        certification = row.get("certification")
        for key in ("proof_checked", "roundoff_controlled"):
            if not isinstance(certification, dict) or certification.get(key) is not True:
                reasons.append(f"CERTIFICATION_REQUIRES_{key.upper()}")
    limit = None if allocation is None else allocation * quantity["reference_value"]
    exceeds = None if error is None or limit is None else error > limit
    admitted = not reasons
    return dict(status="ADMITTED_WITHIN_ALLOCATION" if admitted and not exceeds else
                       "ADMITTED_EXCEEDS_ALLOCATION" if admitted else "UNADMITTED",
                admitted=admitted, absolute_error=None if error is None else _display(error),
                absolute_error_exact=None if error is None else _exact(error),
                evidence_class=evidence_class, evidence_refs=row.get("evidence_refs", []),
                allocation_relative=None if allocation is None else _display(allocation),
                allocation_absolute=None if limit is None else _display(limit),
                reported_value_exceeds_allocation=exceeds,
                reasons=reasons), error


def evaluate_ledger(ledger):
    """Return arithmetic/evidence-type admission without changing any old gate."""
    if not isinstance(ledger, dict) or ledger.get("schema") != SCHEMA:
        raise ValueError("invalid ledger schema")
    profile = ledger.get("profile")
    if not isinstance(profile, str) or profile not in PROFILE_COMPONENTS:
        raise ValueError("unknown completeness profile")
    quantity = _quantity(ledger.get("quantity"), profile)
    components, couplings = ledger.get("components"), ledger.get("couplings")
    if not isinstance(components, dict) or not isinstance(couplings, dict):
        raise ValueError("explicit component and coupling objects required")
    required = PROFILE_COMPONENTS[profile]
    if set(components) - set(required):
        raise ValueError("component outside declared completeness profile")
    if set(couplings) - {"h_dt"}:
        raise ValueError("unsupported/unaccounted coupling")
    rows, exact_errors = {}, {}
    for name in required:
        rows[name], exact_errors[name] = _row(name, components.get(name), quantity, profile, ALLOCATIONS[name])
        included = (components.get(name) or {}).get("includes_couplings", [])
        if included not in ([], ["h_dt"]) or (included and name != "spatial"):
            raise ValueError("invalid or duplicate coupling accounting")
    coupling_input = couplings.get("h_dt")
    coupling, coupling_error = _row("h_dt", coupling_input, quantity, profile)
    accounting = None if coupling_input is None else coupling_input.get("accounting")
    spatial_includes = (components.get("spatial") or {}).get("includes_couplings", [])
    if coupling_input is not None:
        if accounting not in ("SEPARATE_ADDITIVE", "INCLUDED_IN_SPATIAL"):
            raise ValueError("explicit h_dt accounting required")
        if not _refs(coupling_input.get("accounting_evidence_refs")):
            coupling["admitted"] = False
            coupling["status"] = "UNADMITTED"
            coupling["reasons"].append("MISSING_COUPLING_ACCOUNTING_EVIDENCE")
        if accounting == "INCLUDED_IN_SPATIAL":
            if spatial_includes != ["h_dt"]:
                raise ValueError("spatial inclusion accounting must explicitly name h_dt")
            spatial_error = exact_errors["spatial"]
            if spatial_error is not None and coupling_error is not None and spatial_error < coupling_error:
                raise ValueError("spatial error smaller than included h_dt coupling")
        elif spatial_includes:
            raise ValueError("h_dt double accounting: separate plus included")
    elif spatial_includes:
        # The spatial claim names a coupling but the required measured/estimated
        # coupling row is absent. Preserve OPEN, never accept implied zero.
        coupling["reasons"].append("SPATIAL_INCLUSION_HAS_NO_COUPLING_ROW")
    all_admitted = all(row["admitted"] for row in rows.values()) and coupling["admitted"]
    relative_target = sum((ALLOCATIONS[name] for name in required), Fraction(0))
    absolute_target = relative_target * quantity["reference_value"]
    total = None
    if all_admitted:
        total = sum(exact_errors.values(), Fraction(0))
        if accounting == "SEPARATE_ADDITIVE":
            total += coupling_error
    exceeded_components = [name for name, row in rows.items()
                           if row["admitted"] and row["reported_value_exceeds_allocation"]]
    total_within = None if total is None else total <= absolute_target
    status = ("NUMERICAL_BUDGET_EXCEEDED" if exceeded_components or total_within is False else
              "NUMERICAL_BUDGET_SATISFIED_MODEL_CONDITIONAL" if all_admitted else "NUMERICAL_BUDGET_OPEN")
    all_certified = all_admitted and all(row["evidence_class"] == "CERTIFIED_BOUND"
                                        for row in [*rows.values(), coupling])
    certified = None if not all_certified else dict(**_exact(total), units=ledger["quantity"]["units"],
        scope="EXACT_SUM_OF_DECLARED_CERTIFIED_INPUT_BOUNDS_EVIDENCE_NOT_REPROVED_BY_LEDGER")
    return dict(schema="BASS_CR_R3M26_BUDGET_EVALUATION_V1", profile=profile,
                quantity=_display_tree(ledger["quantity"]), quantity_numeric_identity_exact=_identity_exact_tree(quantity),
                status=status, required_components=list(required),
                required_relative_total=_display(relative_target), required_absolute_total=_display(absolute_target),
                required_absolute_total_exact=_exact(absolute_target), components=rows,
                h_dt=dict(**coupling, accounting=accounting), all_required_evidence_admitted=all_admitted,
                exceeded_components=exceeded_components, total_within_budget=total_within,
                additive_total_absolute_error=None if total is None else _display(total),
                additive_total_exact=None if total is None else _exact(total),
                float_display_total_is_certified=False, certified_total_bound=certified,
                combination="CONSERVATIVE_L1_NO_RSS_OR_INDEPENDENCE_ASSUMPTION",
                external_validation=_display_tree(ledger.get("external_validation", {"status": "NOT_EVALUATED"})),
                synthetic_fixture=ledger.get("synthetic_fixture", False),
                production_admitted=False, historical_decisions_changed=False,
                scope="DECLARED_QUANTITY_NUMERICAL_LEDGER_ONLY_NOT_WHOLE_PRODUCTION_OR_EXPERIMENTAL_VALIDATION")


def projection_probability_error(p_num, delta):
    """Floating evaluation of |p-p_num| <= 2 sqrt(p_num) delta + delta**2.

    delta bounds ||psi-psi_num|| in the SAME Hilbert space and Q is an
    orthogonal projector. This floating helper does not certify delta or rounding.
    p_num=0 still has a meaningful absolute bound delta**2.
    """
    p = float(_number(p_num, "p_num"))
    d = float(_number(delta, "delta"))
    result = 2 * math.sqrt(p) * d + d * d
    if not math.isfinite(result):
        raise ValueError("probability-error formula overflows; no finite bound returned")
    return result


def sufficient_state_error(p_num, relative_goal):
    """Stable floating inverse, relative to p_num>0; never define 0/0 as PASS."""
    p = float(_number(p_num, "p_num for relative error", positive=True))
    goal = float(_number(relative_goal, "relative_goal"))
    result = math.sqrt(p) * (goal / (math.sqrt(1 + goal) + 1))
    if not math.isfinite(result):
        raise ValueError("state-error inverse overflows")
    return result


def load_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj
    def nonfinite(value):
        raise ValueError(f"nonfinite JSON token: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_float=Decimal, parse_constant=nonfinite)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate_ledger(load_json(args.ledger))
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
