#!/usr/bin/env python3
"""Audit saved C21F native requests/responses without importing or running a solver.

All physics acceptance tolerances are copied, with source attribution, from the
pinned NativeMicro/MicroRates bridge.  Hash checks use original bytes.  This
program writes only a newly created output directory; it cannot overwrite a
previous assessment or mutate the source snapshot.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import sys


OWNER = "6ea2b1b4b3875c9163cafc45efe720afded43fc4"
EVIDENCE_REF = "c4a502e0c931a201edfa3c7046f7a91230c2278f"
UNIT = Path("research/cr_c21e_event_native_20261018")
EVIDENCE = UNIT / "evidence/C21F_NATIVE_NCP_20261018T1358Z"
EV_ERG = 1.602176634e-12
KB_ERG_K = 1.380649e-16
BIND_EV = (13.598434599702, 24.587389011, 54.41776)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TOLERANCES = {
    "density": {"rtol": 4e-14, "atol": 0.0,
                "rule": "abs(observed-expected) <= atol+rtol*abs(expected)",
                "source": "src/native_micro.py NativeMicro.__call__"},
    "temperature_K": {"rtol": 4e-13, "atol": 1e-10,
                      "rule": "abs(observed-expected) <= atol+rtol*abs(expected)",
                      "source": "src/native_micro.py NativeMicro.__call__"},
    "fractions_per_s": {"rtol": 2e-11, "atol": 1e-28,
                        "rule": "abs(observed-expected) <= atol+rtol*abs(expected)",
                        "source": "src/event_coupler.py MicroRates.validate"},
    "binding_eV_H_s": {"rtol": 2e-11, "atol": 1e-28,
                       "rule": "math.isclose with rel_tol and abs_tol (max rule)",
                       "source": "src/event_coupler.py MicroRates.validate"},
    "energy_eV_H_s": {"rtol": 2e-11, "atol": 1e-28,
                      "rule": "abs(fsum(thermal,binding,escape,-cmb)) <= atol+rtol*fsum(abs(terms))",
                      "source": "src/event_coupler.py MicroRates.validate"},
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def strict_json(data: str | bytes):
    def reject_constant(value):
        raise ValueError(f"nonfinite JSON constant {value}")

    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError(f"duplicate JSON key {key}")
            out[key] = value
        return out

    return json.loads(data, parse_constant=reject_constant, object_pairs_hook=pairs)


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def scalar_close(observed: float, expected: float, name: str):
    t = TOLERANCES[name]
    defect = abs(observed - expected)
    if name == "binding_eV_H_s":
        budget = max(t["atol"], t["rtol"] * max(abs(observed), abs(expected)))
    else:
        budget = t["atol"] + t["rtol"] * abs(expected)
    return defect <= budget, defect, budget, (defect / budget if budget else (0.0 if defect == 0 else math.inf))


def max_entry(stats, name, defect, budget, ratio, where):
    stat = stats.setdefault(name, {"maximum_absolute_defect": 0.0,
                                   "maximum_budget_fraction": 0.0,
                                   "location_maximum_absolute_defect": None,
                                   "location_maximum_budget_fraction": None})
    if stat["location_maximum_absolute_defect"] is None or defect > stat["maximum_absolute_defect"]:
        stat["maximum_absolute_defect"] = defect
        stat["location_maximum_absolute_defect"] = where
    if stat["location_maximum_budget_fraction"] is None or ratio > stat["maximum_budget_fraction"]:
        stat["maximum_budget_fraction"] = ratio
        stat["location_maximum_budget_fraction"] = where
        stat["absolute_defect_at_maximum_budget_fraction"] = defect
        stat["budget_at_maximum_budget_fraction"] = budget


class Findings:
    def __init__(self):
        self.counts = {}
        self.examples = []

    def add(self, name, where, detail):
        self.counts[name] = self.counts.get(name, 0) + 1
        if len(self.examples) < 60:
            self.examples.append({"condition": name, "location": where, "detail": detail})

    @property
    def total(self):
        return sum(self.counts.values())

    def payload(self):
        return {"count": self.total, "by_condition": self.counts, "examples": self.examples,
                "examples_truncated": self.total > len(self.examples)}


def load_manifest(path: Path):
    entries = {}
    for line in path.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix("*").removeprefix("./")
        if not HEX64.fullmatch(digest) or name in entries or ".." in Path(name).parts or Path(name).is_absolute():
            raise ValueError(f"invalid/duplicate manifest line: {line!r}")
        entries[name] = digest
    return entries


def load_receipts(directory: Path):
    by_path = {}
    inventories = []
    for path in sorted(directory.glob("intake_receipts_*.json")):
        raw = path.read_bytes()
        records = strict_json(raw)
        if not isinstance(records, list):
            raise ValueError(f"not a receipt list: {path}")
        inventories.append({"file": str(path), "sha256": sha256(raw), "record_count": len(records)})
        for record in records:
            by_path.setdefault(record["path"], []).append(record)
    return by_path, inventories


def attest(path: Path, snapshot: Path, manifest, evidence_root: Path, receipts, findings, require_manifest=True):
    rel = path.relative_to(snapshot).as_posix()
    if not path.is_file():
        findings.add("missing_input", rel, "file absent")
        return {"path": rel, "status": "MISSING"}
    raw = path.read_bytes()
    digest = sha256(raw)
    blob = git_blob(raw)
    manifest_hash = None
    if path.is_relative_to(evidence_root):
        manifest_hash = manifest.get(path.relative_to(evidence_root).as_posix())
    if require_manifest and manifest_hash is None:
        findings.add("manifest_entry_missing", rel, "required exact-byte identity unavailable")
    if manifest_hash is not None and digest != manifest_hash:
        findings.add("manifest_sha256_mismatch", rel, {"computed": digest, "recorded": manifest_hash})
    records = receipts.get(rel, [])
    matches = [r for r in records if r.get("sha256") == digest and r.get("git_blob") == blob and r.get("bytes") == len(raw)]
    if not matches:
        findings.add("intake_receipt_mismatch_or_missing", rel,
                     {"computed_sha256": digest, "computed_git_blob": blob, "receipt_count": len(records)})
    if path.is_relative_to(evidence_root) and matches and not any(r.get("source_ref") == EVIDENCE_REF for r in matches):
        findings.add("evidence_source_ref_mismatch", rel, [r.get("source_ref") for r in matches])
    return {"path": rel, "bytes": len(raw), "sha256": digest, "git_blob": blob,
            "manifest_sha256": manifest_hash, "manifest_matches": manifest_hash == digest if manifest_hash else None,
            "intake_receipt_matches": bool(matches),
            "receipt_source_refs": sorted({r.get("source_ref", "MISSING") for r in matches})}


def audit_file(point_path, snapshot, evidence_root, manifest, receipts, findings):
    rel = point_path.relative_to(evidence_root).as_posix()
    lane = point_path.relative_to(evidence_root).parts[0]
    fixture_path = evidence_root / lane / "fixture.json"
    fixture = strict_json(fixture_path.read_bytes())
    y_fixture = fixture["Y"]
    nh0_fixture = fixture["nh0"]
    process_path = point_path.with_name("native_process.json")
    process = strict_json(process_path.read_bytes())
    is_reference = point_path.parent.name == "reference_process"
    result_path = (evidence_root / lane / "radau.json") if is_reference else point_path.parent.parent / "result.json"
    result = strict_json(result_path.read_bytes())
    expected_count_key = "rhs_evaluations" if is_reference else "rhs_calls"
    expected_count = result.get(expected_count_key)
    expected_kind = "NATIVE_ORIGINAL_NONPHOTO_RUST"
    if result.get("microphysics") != expected_kind:
        findings.add("result_provider_kind", rel, result.get("microphysics"))
    if process.get("owner") != OWNER:
        findings.add("native_owner_metadata", rel, process.get("owner"))
    binary_hash = process.get("binary_sha256")
    if not isinstance(binary_hash, str) or not HEX64.fullmatch(binary_hash):
        findings.add("binary_hash_record_invalid", rel, binary_hash)
    elif binary_hash != manifest.get("build/native_point"):
        findings.add("binary_record_disagrees_with_manifest", rel, binary_hash)
    if not isinstance(process.get("command"), list) or not process["command"]:
        findings.add("native_command_metadata", rel, process.get("command"))
    if not finite_number(process.get("timeout_s")) or process["timeout_s"] <= 0:
        findings.add("native_timeout_metadata", rel, process.get("timeout_s"))
    if not isinstance(process.get("max_calls"), int) or isinstance(process.get("max_calls"), bool) or process["max_calls"] < 1:
        findings.add("native_budget_metadata", rel, process.get("max_calls"))
    local_start_failures = findings.total
    identity = attest(point_path, snapshot, manifest, evidence_root, receipts, findings)
    dependencies = [attest(p, snapshot, manifest, evidence_root, receipts, findings)
                    for p in (process_path, result_path, fixture_path)]
    checks = {"valid_request": 0, "OK_23_finite_response": 0, "exact_zero_photo_and_expansion": 0,
              "nonnegative_ci_rr_dr_and_escape": 0, "no_error_response": 0,
              "fixture_density_exact": 0, "elapsed_metadata_valid": 0}
    stats = {}
    ranges = {}
    count = 0
    seconds_sum = 0.0

    def note_range(name, value):
        r = ranges.setdefault(name, {"min": value, "max": value})
        r["min"] = min(r["min"], value)
        r["max"] = max(r["max"], value)

    with point_path.open("r", encoding="utf-8") as stream:
        for row_number, line in enumerate(stream, 1):
            count += 1
            where = f"{rel}:{row_number}"
            try:
                row = strict_json(line)
                if not isinstance(row, dict):
                    raise ValueError("row is not an object")
                request = row["request"]
                fields = request.split("\t")
                if len(fields) != 8 or fields[0] != "EVAL":
                    raise ValueError("request must contain EVAL plus exactly seven tab-separated values")
                a, nh0, nhe0, x, y, z, w = [float(s) for s in fields[1:]]
                values = (a, nh0, nhe0, x, y, z, w)
                if not all(math.isfinite(v) for v in values):
                    raise ValueError("nonfinite request")
                if not (0 < a <= 1 and nh0 > 0 and nhe0 >= 0 and 0 <= x <= 1
                        and y >= 0 and z >= 0 and y + z <= 1 and w > 0
                        and (nhe0 > 0 or (y == 0 and z == 0))):
                    raise ValueError("original strict request domain violated")
                checks["valid_request"] += 1
                if nh0 == nh0_fixture and nhe0 == nh0_fixture * y_fixture:
                    checks["fixture_density_exact"] += 1
                else:
                    findings.add("request_fixture_density", where,
                                 {"request": [nh0, nhe0], "fixture": [nh0_fixture, nh0_fixture*y_fixture]})
                for name, val in zip(("a", "nH0_cm3", "nHe0_cm3", "xHII", "xHeII", "xHeIII", "thermal_eV_H"), values):
                    note_range(name, val)
                sec = row.get("seconds")
                if finite_number(sec) and sec >= 0:
                    checks["elapsed_metadata_valid"] += 1
                    seconds_sum += sec
                    note_range("recorded_call_wall_s", sec)
                else:
                    findings.add("elapsed_metadata", where, sec)
                if "error" in row:
                    findings.add("logged_error", where, row["error"])
                response = row.get("response")
                if not isinstance(response, str) or not response.startswith("OK\t"):
                    findings.add("non_OK_response", where, response)
                    continue
                checks["no_error_response"] += 1
                pieces = response.split("\t")
                v = [float(s) for s in pieces[1:]]
                if len(v) != 23 or not all(math.isfinite(f) for f in v):
                    findings.add("response_shape_or_finiteness", where, {"field_count": len(v)})
                    continue
                checks["OK_23_finite_response"] += 1
                if all(f == 0.0 for f in v[18:]):
                    checks["exact_zero_photo_and_expansion"] += 1
                else:
                    findings.add("double_photo_or_expansion_owner", where, v[18:])
                positive_events = [*v[11:18], v[9]]
                if min(positive_events) >= 0:
                    checks["nonnegative_ci_rr_dr_and_escape"] += 1
                else:
                    findings.add("negative_ci_rr_dr_or_escape", where, positive_events)
                nh, nhe = nh0 / a**3, nhe0 / a**3
                for index, expected in enumerate((a, nh, nhe)):
                    ok, defect, budget, ratio = scalar_close(v[index], expected, "density")
                    max_entry(stats, f"density_{index}", defect, budget, ratio, where)
                    if not ok:
                        findings.add("density_identity", where, {"index": index, "observed": v[index], "expected": expected})
                eos = w / (1.5*(KB_ERG_K/EV_ERG)*(1+y_fixture+x+y_fixture*(y+2*z)))
                note_range("temperature_K", v[3])
                ok, defect, budget, ratio = scalar_close(v[3], eos, "temperature_K")
                max_entry(stats, "temperature_K", defect, budget, ratio, where)
                if not ok:
                    findings.add("EOS_identity", where, {"observed": v[3], "expected": eos})
                net = [v[11]-v[14], v[12]-v[15]-v[17], v[13]-v[16]]
                if y_fixture == 0:
                    if net[1] != 0 or net[2] != 0:
                        findings.add("helium_events_without_helium", where, net)
                    expected_frac = [net[0], 0.0, 0.0]
                else:
                    expected_frac = [net[0], (net[1]-net[2])/y_fixture, net[2]/y_fixture]
                for index, expected in enumerate(expected_frac):
                    ok, defect, budget, ratio = scalar_close(v[4+index], expected, "fractions_per_s")
                    max_entry(stats, f"fractions_per_s_{index}", defect, budget, ratio, where)
                    if not ok:
                        findings.add("stoichiometry_identity", where, {"index": index, "observed": v[4+index], "expected": expected})
                weights = [BIND_EV[0], y_fixture*BIND_EV[1], y_fixture*(BIND_EV[1]+BIND_EV[2])]
                binding = math.fsum(weights[i] * v[4+i] for i in range(3))
                ok, defect, budget, ratio = scalar_close(v[8], binding, "binding_eV_H_s")
                max_entry(stats, "binding_eV_H_s", defect, budget, ratio, where)
                if not ok:
                    findings.add("binding_identity", where, {"observed": v[8], "expected": binding})
                terms = (v[7], v[8], v[9], -v[10])
                defect = abs(math.fsum(terms))
                budget = TOLERANCES["energy_eV_H_s"]["atol"] + TOLERANCES["energy_eV_H_s"]["rtol"]*math.fsum(abs(t) for t in terms)
                ratio = defect/budget
                max_entry(stats, "energy_eV_H_s", defect, budget, ratio, where)
                if defect > budget:
                    findings.add("thermal_binding_escape_CMB_identity", where, {"defect": defect, "budget": budget})
            except (KeyError, ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
                findings.add("unparseable_or_invalid_record", where, str(error))
    if count != expected_count:
        findings.add("point_count_vs_result", rel, {"actual": count, "expected": expected_count, "counter": expected_count_key})
    if isinstance(process.get("max_calls"), int) and count > process["max_calls"]:
        findings.add("point_count_exceeds_native_budget", rel, {"actual": count, "budget": process["max_calls"]})
    return {"path": rel, "lane": lane, "reference": is_reference, "records": count,
            "expected_records": expected_count, "result_counter": expected_count_key,
            "count_matches": count == expected_count, "checks": checks, "residuals": stats,
            "observed_ranges": ranges, "recorded_call_wall_s_sum": seconds_sum,
            "owner_metadata": process.get("owner"), "binary_sha256_recorded": binary_hash,
            "binary_bytes_verified": False, "native_command_recorded": process.get("command"),
            "identity": identity, "dependency_identities": dependencies,
            "findings_in_file_and_dependencies": findings.total-local_start_failures}


def render_ko(report):
    totals = report["totals"]
    out = ["# C21F 저장 native point 독립 감사", "",
           f"판정: **{report['status']}**. 저장된 {totals['files']}개 JSONL, {totals['records']:,}개 요청·응답을 원시 텍스트에서 다시 읽었다. Rust/Python solver 실행이나 원래 과학 suite 재실행은 수행하지 않았다.", "",
           "## 근거와 identity", "",
           f"- Evidence commit: `{EVIDENCE_REF}`.",
           f"- Native owner 기록: `{OWNER}`.",
           "- 각 point 파일의 바이트 SHA-256을 원 manifest와 비교하고, Git blob SHA-1을 길이 포함 원래 Git object 표현에서 계산하여 실제 intake 영수증과 대조했다.",
           "- 모든 판정 tolerance는 `src/native_micro.py`와 `src/event_coupler.py`의 기존 수치를 유지했다. `math.fsum`을 사용한 독립 합산의 실제 잔차와 허용 budget 비율을 JSON에 함께 남겼다.",
           "- Native binary SHA는 process metadata와 manifest 사이의 일치만 확인했다. 실행 파일 바이트를 받지 않았으므로 binary byte identity는 검증하지 않았다.", "",
           "## 확인 항목", "",
           "| 항목 | 통과 record / 전체 |", "|---|---:|"]
    for name, value in totals["checks"].items():
        out.append(f"| `{name}` | {value:,} / {totals['records']:,} |")
    out.extend(["", "각 record에서 원래 strict state domain, request/fixture 밀도, 세 density echo, EOS, 23개 유한 출력, CI/RR/DR·escape의 비음성, 5개 photo/expansion 출력의 정확한 0을 확인했다. CI−RR−DR로 재구성한 종별 변화율과 결합에너지 변화율, `thermal + binding + escape − CMB = 0`을 독립 계산했다.", "",
                "| Lane | 파일 | point records | result/reference count 일치 |", "|---|---:|---:|---:|"])
    for lane, data in totals["lanes"].items():
        out.append(f"| `{lane}` | {data['files']} | {data['records']:,} | {data['count_matches']} / {data['files']} |")
    out.extend(["", "## 실제 잔차", "",
                "| 항등식 | 최대 절대 잔차 | 원래 허용 budget 대비 최대 비율 |", "|---|---:|---:|"])
    for name, stat in report["maximum_residuals"].items():
        out.append(f"| `{name}` | {stat['maximum_absolute_defect']:.6e} | {stat['maximum_budget_fraction']:.6e} |")
    out.extend(["", "## 적용 범위", "",
                "이 결과는 저장된 C21F 두 fixture의 native 비광이온화 bridge 응답에 대한 사후 일관성 검사다. 원자 rate 함수의 외부 자료 정확성, native build의 현재 재현, 보존량 적분·시간 수렴, source-age/spectral/angular 수렴, Case B, Bianchi 또는 full EoR의 검증을 대신하지 않는다. 입력 Hubble 항과 photo 입력을 0으로 주는 것은 읽은 wrapper source에서 확인했고, 로그에서는 대응하는 다섯 출력이 정확히 0임을 검사했다.", "",
                "Native handshake 문자열은 별도 원시 handshake 기록으로 저장돼 있지 않다. owner 문자열은 `native_process.json`의 기록이며, 해당 파일은 wrapper가 handshake를 성공 확인한 다음 기록하도록 구현돼 있다.", "",
                f"발견된 위반 수: **{report['findings']['count']}**. 세부 위치·입력 hash·파일별 통계는 `POINT_AUDIT.json`에 있다.", ""])
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--receipts-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="New directory only; existing path is rejected")
    args = parser.parse_args()
    snapshot = args.snapshot.resolve()
    evidence_root = snapshot / EVIDENCE
    output = args.out.resolve()
    if output.exists():
        parser.error("--out must not exist (create-only assessment)")
    findings = Findings()
    manifest_path = evidence_root / "MANIFEST.sha256"
    manifest = load_manifest(manifest_path)
    receipts, receipt_inventory = load_receipts(args.receipts_dir.resolve())
    expected_rel = sorted(p for p in manifest if p.endswith("/native_points.jsonl"))
    expected_points = [evidence_root/p for p in expected_rel]
    actual_points = {p.relative_to(evidence_root).as_posix() for p in evidence_root.rglob("native_points.jsonl")}
    if len(expected_rel) != 26:
        findings.add("expected_point_file_universe", "MANIFEST.sha256", {"expected": 26, "manifest": len(expected_rel)})
    if set(expected_rel) != actual_points:
        findings.add("point_file_universe", "evidence", {"missing": sorted(set(expected_rel)-actual_points),
                                                        "unmanifested": sorted(actual_points-set(expected_rel))})
    sources = [attest(snapshot / UNIT / p, snapshot, manifest, evidence_root, receipts, findings, require_manifest=False)
               for p in ("src/native_micro.py", "src/event_coupler.py", "native/native_point.rs", "vendor/pr79/exposure_contract.py")]
    manifest_identity = attest(manifest_path, snapshot, manifest, evidence_root, receipts, findings, require_manifest=False)
    files = []
    for path in expected_points:
        if not path.is_file():
            findings.add("missing_point_file", path.relative_to(evidence_root).as_posix(), "not materialized")
            continue
        files.append(audit_file(path, snapshot, evidence_root, manifest, receipts, findings))
    totals = {"files": len(files), "manifest_point_files": len(expected_rel),
              "records": sum(f["records"] for f in files), "checks": {}, "lanes": {}}
    maximum = {}
    for f in files:
        lane = totals["lanes"].setdefault(f["lane"], {"files": 0, "records": 0, "count_matches": 0})
        lane["files"] += 1
        lane["records"] += f["records"]
        lane["count_matches"] += int(f["count_matches"])
        for name, value in f["checks"].items():
            totals["checks"][name] = totals["checks"].get(name, 0) + value
        for name, stat in f["residuals"].items():
            m = maximum.setdefault(name, dict(stat))
            if stat["maximum_absolute_defect"] > m["maximum_absolute_defect"]:
                m["maximum_absolute_defect"] = stat["maximum_absolute_defect"]
                m["location_maximum_absolute_defect"] = stat["location_maximum_absolute_defect"]
            if stat["maximum_budget_fraction"] > m["maximum_budget_fraction"]:
                for key in ("maximum_budget_fraction", "location_maximum_budget_fraction", "absolute_defect_at_maximum_budget_fraction", "budget_at_maximum_budget_fraction"):
                    m[key] = stat[key]
    report = {
        "schema": "C21F_SAVED_NATIVE_POINT_INDEPENDENT_AUDIT_V1",
        "status": "PASS_SCOPED_SAVED_NATIVE_POINT_AUDIT" if findings.total == 0 else "AUDIT_FINDINGS",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidence_ref": EVIDENCE_REF, "native_owner_recorded": OWNER,
        "auditor_file": str(Path(__file__).resolve()), "auditor_sha256": sha256(Path(__file__).read_bytes()),
        "independence": "Python standard library only; raw-text parsing and independently written identities; no solver imports or execution",
        "actions": {"native_executions": 0, "scientific_solver_executions": 0, "source_mutations": 0, "remote_mutations": 0},
        "tolerance_contract": TOLERANCES, "constants": {"EV_ERG": EV_ERG, "KB_ERG_K": KB_ERG_K, "BIND_EV": BIND_EV},
        "sources": sources, "manifest_identity": manifest_identity, "intake_receipts": receipt_inventory,
        "totals": totals, "maximum_residuals": maximum, "files": files, "findings": findings.payload(),
        "limitations": ["Binary hashes are metadata/manifest records, not independently verified executable bytes.",
                        "Stored pointwise invariants do not validate atomic rate data against external physical references.",
                        "No claim of source-age, spectral, angular, Case B, Bianchi, Full48, or full EoR convergence.",
                        "No independent raw handshake transcript is available; owner metadata is logged after wrapper handshake checks."],
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output/"POINT_AUDIT.json").open("x") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    with (output/"POINT_AUDIT_KO.md").open("x") as stream:
        stream.write(render_ko(report))
    print(json.dumps({"status": report["status"], "out": str(output), "totals": totals,
                      "findings": report["findings"], "maximum_residuals": maximum}, ensure_ascii=False, allow_nan=False))
    return 0 if findings.total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
