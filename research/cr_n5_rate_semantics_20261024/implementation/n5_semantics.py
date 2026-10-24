"""Scoped rate admission and algebraic diagnostics. No work runs on import.

No thermal-rate evaluation, quadrature, ODE or PHYS84 source callback is owned
by this module. Missing numerical inputs remain None.
"""
from __future__ import annotations

import bisect
import hashlib
import importlib.util
import json
import math
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


class InputError(ValueError):
    """Explicit semantic, numerical or provenance rejection."""


def real(value, name, *, minimum=0.0, strictly_positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise InputError(f"{name}:REAL_NONBOOL_REQUIRED")
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise InputError(f"{name}:FINITE_REQUIRED") from exc
    if result == 0.0 and value != 0:
        raise InputError(f"{name}:NONZERO_COERCION_UNDERFLOW")
    if not math.isfinite(result) or result < minimum or (strictly_positive and result <= 0):
        raise InputError(f"{name}:DOMAIN_OR_FINITE_FAILURE")
    return result


def exact_decimal(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise InputError(f"{name}:EXACT_DECIMAL_REQUIRED")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise InputError(f"{name}:DECIMAL_PARSE_FAILURE") from exc
    if not result.is_finite():
        raise InputError(f"{name}:FINITE_REQUIRED")
    return result


def product(*values):
    """Reject overflow and a positive product silently underflowing to zero."""
    result = 1.0
    for index, value in enumerate(values):
        value = real(value, f"factor{index}")
        old = result
        result *= value
        if not math.isfinite(result):
            raise InputError("PRODUCT_OVERFLOW")
        if old > 0 and value > 0 and result == 0:
            raise InputError("PRODUCT_UNDERFLOW")
    return result


def hazard_limit(epsilon, mean_s):
    epsilon = real(epsilon, "epsilon")
    mean_s = real(mean_s, "active_mean_s", strictly_positive=True)
    if epsilon >= 1:
        raise InputError("epsilon:MUST_BE_LESS_THAN_ONE")
    result = -math.log1p(-epsilon) / mean_s
    if not math.isfinite(result):
        raise InputError("HAZARD_LIMIT_OVERFLOW")
    if epsilon > 0 and result == 0:
        raise InputError("HAZARD_LIMIT_UNDERFLOW")
    return result


def first_event_estimate(hmax_per_s, mean_s, active_fraction=1.0):
    hmax = real(hmax_per_s, "hmax_per_s")
    mean = real(mean_s, "active_mean_s", strictly_positive=True)
    fraction = real(active_fraction, "active_fraction")
    if fraction > 1:
        raise InputError("active_fraction:ABOVE_ONE")
    exposure = product(hmax, mean)
    active = -math.expm1(-exposure)
    whole = product(fraction, active)
    return {"hmax_times_active_mean": exposure,
            "active_first_event_upper_estimate": active,
            "whole_selected_first_event_upper_estimate": whole}


def domain_coverage(requested, supplied, *, threshold=None):
    """Exact decimal interval containment, with an explicitly stated zero region.

    A source lower bound is not a physical threshold. A genuine gap between the
    threshold and the first source knot remains uncovered.
    """
    if requested is None or supplied is None:
        return {"covered": False, "value": None, "reason": "MISSING_DOMAIN"}
    if len(requested) != 2 or len(supplied) != 2:
        raise InputError("INTERVAL_SHAPE")
    lo, hi = (exact_decimal(x) for x in requested)
    sl, sh = (exact_decimal(x) for x in supplied)
    th = None if threshold is None else exact_decimal(threshold)
    if lo < 0 or hi < lo or sl < 0 or sh < sl or (th is not None and (th < 0 or th > sl)):
        raise InputError("INTERVAL_ORDER")
    if th is not None and hi < th:
        return {"covered": True, "value": 0.0, "reason": "OWNER_THRESHOLD_ZERO"}
    if lo >= sl and hi <= sh:
        return {"covered": True, "value": None, "reason": "SOURCE_INTERVAL_COVERED"}
    if th is not None and sl == th and lo < th and hi <= sh:
        return {"covered": True, "value": None, "reason": "THRESHOLD_ZERO_PLUS_SOURCE_INTERVAL"}
    return {"covered": False, "value": None, "reason": "UNRESOLVED_OUTSIDE_SOURCE_INTERVAL"}


ADMITTED_OWNER_GATES = frozenset({"NUMERICALLY_CHECKED_SCOPED", "NUMERICALLY_AVAILABLE_SCOPED",
                                 "CONDITIONAL_SOURCE_MODEL_ADMITTED"})
IDENTITY_KEYS = ("process", "nuclide", "charge", "internal_state", "quantity_kind",
                 "frame", "clock", "unit", "interpolation", "isotope_mapping")


def admit_rate(request, provider):
    """Admit a supplied scalar only at its exact declared semantics and domain."""
    reasons = []
    if provider is None:
        return {"admitted": False, "value": None, "reasons": ["MISSING_PROVIDER"]}
    if provider.get("owner_gate") not in ADMITTED_OWNER_GATES:
        reasons.append("PROVIDER_GATE_NOT_ADMITTED")
    for item in (request, provider):
        charge = item.get("charge")
        if isinstance(charge, bool) or not isinstance(charge, int) or charge < 0:
            reasons.append("INVALID_TARGET_CHARGE")
    for key in IDENTITY_KEYS:
        if key not in request or key not in provider or request[key] is None or provider[key] is None:
            reasons.append(f"MISSING_IDENTITY:{key}")
        elif request[key] != provider[key]:
            reasons.append(f"IDENTITY_MISMATCH:{key}")
    kind = str(request.get("quantity_kind", "")).lower()
    thermal = "thermal" in kind or "maxwell" in kind
    tagged = "tagged" in kind
    if tagged and request.get("energy_domain_eV") is None and request.get("incident_energy_eV") is None:
        reasons.append("MISSING_SELECTOR:tagged_electron_energy")
    for key in ("temperature_K", "incident_energy_eV"):
        required = key + "_values" in provider or (key == "temperature_K" and thermal)
        if (required or key in request) and request.get(key) is None:
            reasons.append(f"MISSING_SELECTOR:{key}")
            continue
        if key in request:
            allowed = provider.get(key + "_values")
            try:
                wanted = exact_decimal(request[key], key)
                if wanted < 0 or (key == "temperature_K" and wanted == 0):
                    raise InputError("NONPOSITIVE_T_OR_NEGATIVE_ENERGY")
                matches = allowed is not None and wanted in {exact_decimal(x, key) for x in allowed}
            except InputError:
                matches = False
            if not matches:
                reasons.append(f"EXACT_VALUE_UNAVAILABLE:{key}")
    for key in ("energy_domain_eV", "outgoing_energy_domain_eV", "angle_domain_deg"):
        if (key in provider or key in request) and request.get(key) is None:
            reasons.append(f"MISSING_SELECTOR:{key}")
            continue
        if key in request:
            threshold = provider.get("threshold_eV") if key == "energy_domain_eV" else None
            coverage = domain_coverage(request[key], provider.get(key), threshold=threshold)
            if not coverage["covered"]:
                reasons.append(f"DOMAIN_UNAVAILABLE:{key}")
    value = provider.get("value")
    if value is None:
        reasons.append("MISSING_NUMERICAL_VALUE")
    else:
        try:
            value = real(value, "provider_value")
        except InputError:
            reasons.append("INVALID_NUMERICAL_VALUE")
        if value == 0 and provider.get("zero_basis") not in {"owner_physical_threshold", "explicit_owner_exact_zero"}:
            reasons.append("UNQUALIFIED_ZERO")
    return {"admitted": not reasons, "value": value if not reasons else None,
            "reasons": reasons, "scope": provider.get("scope"),
            "source_identity": provider.get("source_identity")}


def exact_temperature_rows(rows, temperature):
    wanted = exact_decimal(temperature, "requested_T")
    if wanted <= 0:
        raise InputError("POSITIVE_TEMPERATURE_REQUIRED")
    selected = [row for row in rows if exact_decimal(row["temperature_K"]) == wanted]
    if not selected:
        raise InputError("EXACT_TEMPERATURE_ROWS_UNAVAILABLE")
    return selected


def contained_path(base, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise InputError("UNSAFE_RELATIVE_INPUT_PATH")
    base = Path(base).resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base):
        raise InputError("INPUT_ESCAPES_UNIT")
    return path


def verify_manifest(base, relative="inputs/INPUT_MANIFEST.json"):
    manifest_path = contained_path(base, relative)
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    seen = set()
    for row in manifest["files"]:
        rel = row["path"]
        if rel in seen:
            raise InputError("DUPLICATE_MANIFEST_PATH")
        seen.add(rel)
        data = contained_path(base, rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise InputError(f"INPUT_SHA256_MISMATCH:{rel}")
        if "bytes" in row and len(data) != row["bytes"]:
            raise InputError(f"INPUT_SIZE_MISMATCH:{rel}")
    return {"manifest_sha256": hashlib.sha256(raw).hexdigest(), "verified_files": len(seen),
            "paths": sorted(seen)}


def import_pinned(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise InputError("PINNED_IMPORT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_channel(energy, flux, threshold):
    if len(energy) != len(flux) or len(energy) < 2:
        raise InputError("CHANNEL_SHAPE")
    x = tuple(real(v, "source_energy", strictly_positive=True) for v in energy)
    y = tuple(real(v, "source_W") for v in flux)
    if any(a >= b for a, b in zip(x, x[1:])):
        raise InputError("CHANNEL_ENERGY_NOT_STRICT")
    if x[0] != threshold or y[0] != 0:
        raise InputError("CHANNEL_THRESHOLD_NOT_OWNER_ZERO")
    return x, y


def interpolate_nonnegative(energy, flux, point):
    if point == energy[-1]:
        return flux[-1]
    index = bisect.bisect_right(energy, point) - 1
    if index < 0 or index >= len(energy) - 1:
        raise InputError("INTERPOLATION_OUTSIDE_SOURCE")
    if point == energy[index]:
        return flux[index]
    t = (point - energy[index]) / (energy[index + 1] - energy[index])
    if not 0 <= t <= 1:
        raise InputError("INTERPOLATION_WEIGHT")
    return (1 - t) * flux[index] + t * flux[index + 1]


def ce_envelope(channels, domain_eV, *, threshold_eV, n_1s_cm3, eV_J, m_e_kg):
    """Analytic panel candidates for the declared W-PL source-model supremum.

    The root b/a is included even though a positive affine W permits only an
    interior minimum. Endpoints are evaluated by nonnegative interpolation.
    """
    threshold = real(threshold_eV, "threshold", strictly_positive=True)
    low, high = (real(x, "path_energy", strictly_positive=True) for x in domain_eV)
    if low >= high or not channels:
        raise InputError("ENVELOPE_DOMAIN_OR_CHANNELS")
    checked = {name: validate_channel(*values, threshold) for name, values in channels.items()}
    if any(high > x[-1] for x, _ in checked.values()):
        raise InputError("FULL_PATH_NOT_SOURCE_COVERED")
    density = real(n_1s_cm3, "n_1s_cm3")
    ev = real(eV_J, "eV_J", strictly_positive=True)
    mass = real(m_e_kg, "m_e_kg", strictly_positive=True)
    prefactor = product(density, 100.0, math.sqrt(2.0 * ev / mass))
    points = {low, high}
    if low < threshold < high:
        points.add(threshold)
    for x, _ in checked.values():
        points.update(e for e in x if low < e < high)
    points = sorted(points)
    best = None
    endpoint_samples = {}
    candidate_count = 0
    stationary_candidates = 0
    for left, right in zip(points, points[1:]):
        if right <= threshold:
            wl = wr = 0.0
            individual_left = individual_right = {name: 0.0 for name in checked}
        else:
            individual_left = {name: interpolate_nonnegative(x, y, left) for name, (x, y) in checked.items()}
            individual_right = {name: interpolate_nonnegative(x, y, right) for name, (x, y) in checked.items()}
            wl = math.fsum(individual_left.values())
            wr = math.fsum(individual_right.values())
        a = (wr - wl) / (right - left)
        b = wl - a * left
        candidates = [(left, "left_endpoint"), (right, "right_endpoint")]
        if a != 0:
            critical = b / a
            if math.isfinite(critical) and left < critical < right:
                candidates.append((critical, "stationary_b_over_a"))
                stationary_candidates += 1
        for energy, candidate_type in candidates:
            fraction = (energy - left) / (right - left)
            w = wl if energy == left else wr if energy == right else (1 - fraction) * wl + fraction * wr
            hazard = product(prefactor, w / math.sqrt(energy))
            candidate_count += 1
            if candidate_type in {"left_endpoint", "right_endpoint"}:
                individual = individual_left if energy == left else individual_right
                endpoint_samples[energy] = {"energy_eV": energy, "h_total_per_proper_s": hazard,
                                            "channel_hazards_per_proper_s": {
                                                name: product(prefactor, val / math.sqrt(energy))
                                                for name, val in individual.items()}}
            if best is None or hazard > best["hmax_per_proper_s"]:
                best = {"hmax_per_proper_s": hazard, "maximizing_energy_eV": energy,
                        "candidate_type": candidate_type, "panel_eV": [left, right],
                        "panel_W_endpoints_eV_cm2": [wl, wr],
                        "panel_a_cm2": a, "panel_b_eV_cm2": b}
    if best is None:
        raise InputError("NO_ENVELOPE_CANDIDATES")
    return {**best, "channels": list(channels), "full_pre_entry_domain_eV": [low, high],
            "threshold_eV": threshold, "ground_H1_target_density_cm3": density,
            "candidate_count": candidate_count, "stationary_candidate_count": stationary_candidates,
            "union_panel_count": len(points) - 1, "prefactor_cm_per_s_per_sqrt_eV_times_cm3_inv": prefactor,
            "endpoint_samples": [endpoint_samples[key] for key in sorted(endpoint_samples)],
            "quantity_kind": "uniform_tagged_electron_CE_event_hazard_envelope",
            "source_model": "stationary_heavy_target_unpolarized_H1_ground_W_PL",
            "empirical_source_uncertainty": None, "continuum_error_certificate": None,
            "physical_model_probability_certificate": None}
