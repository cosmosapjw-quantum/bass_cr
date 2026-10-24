"""Independent C9: saved-array endpoint proof checks and closed-form identities.

This module does not import production scientific algorithms or any provider.
Only the old/current admission guard is imported for a synthetic negative witness.
No ODE, quadrature, source constructor, moments or rate provider is run.
"""
from __future__ import annotations

import bisect
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
from decimal import Decimal, localcontext


UNIT = Path(__file__).resolve().parents[1]
PRIMARY_ID = "n5_ce_envelope_primary_20261024t031906828z_v1"
PRIMARY = UNIT / "implementation/runs" / PRIMARY_ID
TOLERANCE = Decimal("5e-14")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def binary(value):
    if isinstance(value, float):
        return Decimal.from_float(value)
    return Decimal(value)


def relative(actual, reference):
    a = binary(actual)
    return abs(a - reference) / max(abs(a), abs(reference), Decimal("1e-300"))


def interpolation(xs, ys, point):
    if point == xs[-1]:
        return ys[-1]
    j = bisect.bisect_right(xs, point) - 1
    assert 0 <= j < len(xs) - 1
    # Independent Decimal barycentric evaluation, without production helpers.
    return (ys[j] * (xs[j + 1] - point) + ys[j + 1] * (point - xs[j])) / (xs[j + 1] - xs[j])


def endpoints_only(envelope, arrays, case):
    low, high = map(binary, envelope["full_pre_entry_domain_eV"])
    threshold = binary(arrays["threshold_eV"])
    channels = [arrays["channels"][name] for name in envelope["channels"]]
    converted = [(list(map(binary, c["energy_eV"])), list(map(binary, c["W_eV_cm2"]))) for c in channels]
    for xs, ys in converted:
        assert len(xs) == len(ys) and len(xs) >= 2
        assert all(x < y for x, y in zip(xs, xs[1:]))
        assert all(y >= 0 for y in ys)
        assert xs[0] == threshold and ys[0] == 0 and high <= xs[-1]
    # Nonnegative affine W(E)/sqrt(E) has no positive interior maximum.
    # Thus all union knots and clipped endpoints suffice, independently of
    # production stationary-candidate enumeration and slope/intercept arithmetic.
    points = {low, high}
    if low <= threshold <= high:
        points.add(threshold)
    for xs, _ in converted:
        points.update(x for x in xs if low <= x <= high)
    prefactor = binary(case["n_H1_1s_cm3"]) * Decimal(100) * (
        Decimal(2) * binary(case["eV_J"]) / binary(case["m_e_kg"])
    ).sqrt()
    values = []
    for e in sorted(points):
        value = Decimal(0) if e < threshold else prefactor * sum(interpolation(x, y, e) for x, y in converted) / e.sqrt()
        values.append((value, e))
    maximum, at = max(values)
    error = relative(envelope["hmax_per_proper_s"], maximum)
    assert error <= TOLERANCE
    assert at == binary(envelope["maximizing_energy_eV"])
    return {
        "chi": envelope["chi"], "selection": envelope["selection"],
        "decimal_from_float_hmax": str(maximum),
        "maximizing_energy_decimal_from_float_eV": str(at),
        "saved_hmax_per_s": envelope["hmax_per_proper_s"],
        "relative_error_exact_binary_inputs": str(error),
        "endpoint_count": len(values),
        "interior_search": "NOT_NEEDED_BY_NONNEGATIVE_AFFINE_ENDPOINT_LEMMA",
        "status": "PASS",
    }


def guard_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_guard_witness():
    old_path = UNIT / "implementation/repair_history/primary_executed_source/n5_semantics.py"
    new_path = UNIT / "implementation/n5_semantics.py"
    old = guard_module(old_path, "c9_old_guard_only")
    new = guard_module(new_path, "c9_new_guard_only")
    request = {
        "process": "CE", "nuclide": "H1", "charge": 0,
        "internal_state": "1s->2s", "quantity_kind": "maxwellian_coefficient",
        "frame": "bath_frame_rest_target", "clock": "proper_seconds",
        "unit": "cm^3/s", "interpolation": "exact_T_only",
        "isotope_mapping": "H1_only", "temperature_K": 10000.0,
    }
    provider = dict(request, owner_gate="NUMERICALLY_AVAILABLE_SCOPED",
                    value=1e-13, temperature_K_values=[10000.0])
    provider.pop("temperature_K")
    missing = {k: v for k, v in request.items() if k != "temperature_K"}
    before = old.admit_rate(missing, provider)
    after = new.admit_rate(missing, provider)
    positive = new.admit_rate(request, provider)
    assert before["admitted"] is True
    assert after["admitted"] is False and after["value"] is None
    assert "MISSING_SELECTOR:temperature_K" in after["reasons"]
    assert positive["admitted"] is True
    # Supported Decimal inputs at unrepresentably tiny magnitudes are outside
    # this JSON/binary64 campaign but expose a concrete nonblocking API caveat.
    tiny = new.product(Decimal("1e-1000"), 1.0)
    return {
        "missing_temperature_before": before,
        "missing_temperature_after": after,
        "valid_temperature_after": positive,
        "before_source_sha256": sha(old_path),
        "after_source_sha256": sha(new_path),
        "decimal_cast_underflow_witness": {
            "input": "product(Decimal('1e-1000'),1.0)", "returned": tiny,
            "classification": "NONBLOCKING_OUTSIDE_FROZEN_JSON_INPUTS",
        },
    }


def checks():
    manifest_path = UNIT / "inputs/INPUT_MANIFEST.json"
    manifest = read(manifest_path)
    for item in manifest["files"]:
        p = UNIT / item["path"]
        raw = p.read_bytes()
        assert len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"]
    pre = read(PRIMARY / "PRE_EXECUTION.json")
    assert sha(manifest_path) == pre["input_manifest_sha256"]
    for item in pre["source_pins"]:
        p = UNIT / "implementation/repair_history/primary_executed_source" / Path(item["path"]).name
        assert p.stat().st_size == item["bytes"] and sha(p) == item["sha256"]
    case = read(UNIT / "inputs/CASE.json")
    arrays = read(PRIMARY / "SOURCE_ARRAYS_REUSED.json")
    envelopes = read(PRIMARY / "CE_ENVELOPES.json")
    mfpt = read(UNIT / "inputs/reused/C23D_MFPT.json")
    mfpt_map = {(r["redshift"], r["chi"]): r["upper_boundaries_theta"]["80"] for r in mfpt}
    with localcontext() as context:
        context.prec = 80
        envelope_checks = [endpoints_only(e, arrays, case) for e in envelopes]
        identities = []
        for row in read(PRIMARY / "HCRIT.json"):
            source = mfpt_map[row["redshift"], row["chi"]]
            mean = source["active_weighted_mean_s"]
            assert row["active_mean_first_entry_proper_s"] == mean
            assert row["active_fraction"] == source["active_fraction"]
            ref = -(Decimal(1) - binary(row["epsilon_active"])).ln() / binary(mean)
            err = relative(row["hcrit_per_proper_s"], ref)
            assert err <= TOLERANCE
            identities.append({"kind": "hcrit", "redshift": row["redshift"], "chi": row["chi"], "epsilon": row["epsilon_active"], "relative_error": str(err)})
        for row in read(PRIMARY / "CE_FIRST_EVENT_ESTIMATES.json"):
            source = mfpt_map[row["redshift"], row["chi"]]
            assert row["active_mean_first_entry_proper_s"] == source["active_weighted_mean_s"]
            assert row["active_fraction"] == source["active_fraction"]
            match = [e for e in envelopes if e["chi"] == row["chi"] and e["selection"] == row["channel_selection"]]
            assert len(match) == 1 and row["hmax_per_proper_s"] == match[0]["hmax_per_proper_s"]
            exposure = binary(row["hmax_per_proper_s"]) * binary(source["active_weighted_mean_s"])
            active = Decimal(1) - (-exposure).exp()
            whole = binary(source["active_fraction"]) * active
            errors = [relative(row[k], v) for k, v in [
                ("hmax_times_active_mean", exposure),
                ("active_first_event_upper_estimate", active),
                ("whole_selected_first_event_upper_estimate", whole)]]
            assert max(errors) <= TOLERANCE
            assert row["physical_probability_certificate"] is None and row["global_error_bound"] is None
            identities.append({"kind": "CE_first_event", "redshift": row["redshift"], "chi": row["chi"], "selection": row["channel_selection"], "max_relative_error": str(max(errors))})
        with (UNIT / "inputs/reused/PHYS83_RATES.csv").open() as stream:
            saved = list(csv.DictReader(stream))
        assert len(saved) == 132
        thermal_checks = []
        for row in read(PRIMARY / "THERMAL_TARGET_COMPARISONS.json"):
            source = mfpt_map[row["redshift"], row["chi"]]
            assert row["active_mean_first_entry_proper_s"] == source["active_weighted_mean_s"]
            exact_rows = [s for s in saved if s["upper_level"] == row["upper_level"] and Decimal(s["temperature_K"]) == Decimal(10000)]
            assert len(exact_rows) == 1
            exact_text = exact_rows[0]["q_" + row["direction"] + "_cm3_s"]
            assert row["saved_q_cm3_s_text"] == exact_text
            assert row["saved_q_cm3_s"] == float(exact_text)
            q = binary(row["saved_q_cm3_s"])
            rate = binary(case["n_e_thermal_cm3"]) * q
            exposure = rate * binary(source["active_weighted_mean_s"])
            errors = [relative(row["lambda_per_frozen_target_per_proper_s"], rate), relative(row["lambda_target_times_ee_active_mean"], exposure)]
            assert max(errors) <= TOLERANCE
            for key in ["tagged_electron_event_probability", "evolved_atomic_event_count", "heat_rate"]:
                assert row[key] is None
            thermal_checks.append({"redshift": row["redshift"], "chi": row["chi"], "upper_level": row["upper_level"], "direction": row["direction"], "max_relative_error": str(max(errors))})
    coverage = read(UNIT / "intake/COVERAGE_MATRIX.json")
    assert len(coverage["population_rows"]) == 21
    assert all(len(row["channels"]) == 8 for row in coverage["population_rows"])
    assert all(ch["rate_value"] is None for row in coverage["population_rows"] for ch in row["channels"].values())
    for provider in coverage["providers"]:
        if "source_local_sha256" in provider:
            assert sha(UNIT / provider["source"]) == provider["source_local_sha256"]
    return {
        "status": "PASS", "precision_digits": 80,
        "input_identity": "Decimal.from_float of saved binary64 arrays, constants and scalar inputs",
        "comparison_tolerance": str(TOLERANCE),
        "interpretation": "independent numerical agreement; no directed rounding, empirical source accuracy or MFPT error certificate",
        "manifest_file_count": len(manifest["files"]),
        "primary_executed_source_pins_verified": len(pre["source_pins"]),
        "source_constructor_executions": 0, "provider_rate_evaluations": 0,
        "new_ODE": 0, "new_source_quadratures": 0, "old_science_replays": 0,
        "envelope_checks": envelope_checks, "closed_form_identity_checks": identities,
        "thermal_product_checks": thermal_checks,
        "coverage_rows": 21, "coverage_channels_each": 8,
        "coverage_rate_values_all_null": True,
        "synthetic_guard_witness": synthetic_guard_witness(),
        "global_error_bound": None, "global_completion_percent": None,
    }


def main():
    run_id = "n5_independent_c9_binary64_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_v1"
    run = UNIT / "review/runs" / run_id
    run.mkdir(parents=True, exist_ok=False)
    lease = UNIT / "implementation/.n5_local_lease"
    fd = None
    t0, c0 = time.monotonic(), time.process_time()
    status, error = "FAILED_RETAINED", None
    try:
        fd = os.open(lease, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, json.dumps({"run_id": run_id, "pid": os.getpid(), "mode": "independent_C9_saved_arrays"}).encode())
        os.close(fd)
        allowed = sorted(os.sched_getaffinity(0))
        assert 0 in allowed and 8 in allowed
        os.sched_setaffinity(0, {0})
        cg = Path("/sys/fs/cgroup")
        current, limit = int((cg / "memory.current").read_text()), int((cg / "memory.max").read_text())
        stat = dict(line.split() for line in (cg / "memory.stat").read_text().splitlines())
        clean_inactive = max(0, int(stat["inactive_file"]) - int(stat["file_dirty"]) - int(stat["file_writeback"]))
        assert limit - current + clean_inactive - 64 * 1024**2 >= 32 * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2, 128 * 1024**2))
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        signal.alarm(30)
        files = [Path(__file__).resolve(), UNIT / "FROZEN_CONTRACT.md", UNIT / "inputs/INPUT_MANIFEST.json", UNIT / "intake/COVERAGE_MATRIX.json", *sorted(PRIMARY.glob("*.json")), *sorted((UNIT / "implementation").glob("*.py"))]
        pins = [{"path": str(p.relative_to(UNIT)), "bytes": p.stat().st_size, "sha256": sha(p)} for p in files]
        write(run / "PRE_EXECUTION.json", {
            "run_id": run_id, "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "reviewer": "/root/provider_returns", "source_science_contribution": False,
            "primary_run_id": PRIMARY_ID, "file_pins": pins,
            "cpu_affinity": sorted(os.sched_getaffinity(0)), "coordinator_cpu_protected": 8,
            "cpu55": "UNAVAILABLE_ON_THIS_HOST_NOT_USED", "native_threads": 1,
            "thread_env": {k: os.environ.get(k) for k in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]},
            "memory_current": current, "memory_max": limit, "clean_inactive_file": clean_inactive,
            "address_space_limit_bytes": 128 * 1024**2, "cpu_limit_s": 5, "wall_limit_s": 30,
            "external_NCP_lease": "UNOBSERVED", "global_spend": None, "remaining": None,
        })
        result = checks()
        assert all(sha(UNIT / pin["path"]) == pin["sha256"] for pin in pins)
        write(run / "CHECK_RESULT.json", result)
        status = "PASS"
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        signal.alarm(0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        receipt = {
            "run_id": run_id, "status": status, "error": error,
            "process_cpu_s_at_receipt": time.process_time(),
            "bounded_body_cpu_s": time.process_time() - c0,
            "wall_s": time.monotonic() - t0, "peak_rss_kib": usage.ru_maxrss,
            "resource_accounting": "single stdlib process; separate from producer worker/coordinator ledger",
            "new_ODE": 0, "new_source_quadratures": 0, "provider_rate_evaluations": 0,
            "source_constructor_executions": 0, "old_science_replays": 0,
            "global_spend": None, "remaining": None,
            "EXECUTION": status, "PUBLICATION": "PARENT_OWNED_NOT_ATTEMPTED",
            "BACKUP": "PARENT_OWNED_PENDING", "DAG": "C9_SCOPED_REVIEW;N5_PARTIAL;N6_N7_OPEN",
        }
        write(run / "REVIEW_RECEIPT.json", receipt)
        if fd is not None:
            lease.unlink()
        print(json.dumps({"run_id": run_id, "run_directory": str(run), "status": status, "process_cpu_s_at_receipt": receipt["process_cpu_s_at_receipt"]}))


if __name__ == "__main__":
    main()
