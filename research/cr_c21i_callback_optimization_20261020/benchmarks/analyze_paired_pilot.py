"""Read-only C8 aggregation of an existing paired pilot; never execute a solver.

The input is immutable producer evidence. This program does not import an H/I
runtime module, compile Rust, invoke a native process, or rerun any experiment.
All new output is create-only and separate from the input evidence directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import struct
import time

UNIT = Path(__file__).resolve().parent.parent
PHYSICAL = ("gas", "photons", "temperature_K", "photon_number",
    "photon_energy_eV_H", "number_defect_H", "energy_defect_eV_H",
    "species_defect", "ledgers", "optical_depth", "log_survivor",
    "underflowed_positive_cohorts", "min_internal_optical_depth",
    "min_accepted_optical_depth", "photon_clipping", "tolerance_contract")
CLOCKS = ("process_wall_s", "job_wall_s", "reference_wall_s")
TIMERS = ("original_rhs_execution_ns", "rhs_cache_key_ns", "rhs_cache_hit_ns")
GAUGES = ("rhs_cache_capacity", "rhs_cache_payload_bytes",
          "rhs_cache_peak_entries", "jacobian_scratch_bytes")


def read(path):
    return json.loads(Path(path).read_text())


def record(path):
    value = Path(path).read_bytes()
    return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}


def new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2,
                  allow_nan=False)
        stream.write("\n")


def binary64(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NONFINITE_RECORDED_FLOAT")
        return {"binary64": struct.pack("<d", value).hex()}
    if isinstance(value, dict):
        return {key: binary64(v) for key, v in value.items()}
    if isinstance(value, list):
        return [binary64(v) for v in value]
    return value


def payload_snapshot(root):
    return {str(p.relative_to(root)): record(p) for p in sorted(root.rglob("*"))
            if p.is_file() and p != root / "PAYLOAD_MANIFEST.json"}


def audit_current_sources(before, first_receipt):
    sources = {}
    for tag, dirname in (("H", "cr_c21h_vigilode_bridge_20261019"),
                         ("I", "cr_c21i_callback_optimization_20261020")):
        root = UNIT.parent / dirname
        expected = before["units"][tag]
        sources[str(root / "EXECUTION_MANIFEST.json")] = expected["manifest"]
        for rel, rec in expected["runtime_files"].items():
            sources[str(root / rel)] = rec
    froot = UNIT.parent / "cr_c21e_event_native_20261018"
    groot = UNIT.parent / "cr_c21g_reference_refinement_20261019"
    for rel, rec in before["F_runtime"].items():
        sources[str(froot / rel)] = rec
    sources[str(groot / "EXECUTION_MANIFEST.json")] = before["G_manifest"]
    for rel, rec in first_receipt["input_identity"]["c21g_runtime_files"].items():
        sources[str(groot / rel)] = rec
    sources[str(UNIT / "benchmarks/paired_pilot.py")] = before["benchmark_source"]
    sources[first_receipt["bridge_identity"]["path"]] = before["bridge"]
    sources[first_receipt["bridge_build_receipt"]["path"]] = before["build_receipt"]
    checks = {path: record(path) == expected for path, expected in sources.items()}
    return sources, checks


def aggregate_job(root, name, obs):
    job = root / name
    receipt = read(job / "JOB_RECEIPT.json")
    result = read(job / "result.json")
    independent = read(job / "INDEPENDENT_BALANCES.json")
    payloads = {str(p.relative_to(job)): record(p) for p in sorted(job.rglob("*"))
                if p.is_file() and p != job / "JOB_RECEIPT.json"}
    callbacks, wire, rust = Counter(), Counter(), Counter()
    trace, fd, exits, raw_flags, gauges, segment_rust_counters = [], [], [], [], [], []
    segment_checks = []
    segment_wall = []
    accepted_states = 0
    for index, segment in enumerate(sorted((job / "segments").glob("segment_*"))):
        sr = read(segment / "receipt.json")
        raw = read(segment / "result.json")
        config = read(segment / "config.json")
        segment_exit = read(segment / "process_exit.json")
        segment_checks.append({
            "stored_raw_matches_embedded_result": binary64(raw) == binary64(result["rust_segments"][index]["raw_result"]),
            "config_matches_embedded_result": binary64(config) == binary64(result["rust_segments"][index]["config"]),
            "bridge_identity": read(segment / "binary.json") == receipt["bridge_identity"],
            "success_and_trace": raw["success"] is True and raw["ok"] is True
                and raw["accepted_grid_complete"] is True,
            "segment_exit": segment_exit["process_started"] is True
                and segment_exit["exit_code"] == 0,
            "rpc_log_bytes": sr["raw_bytes"] == (segment / "rpc.jsonl").stat().st_size,
        })
        callbacks.update(sr["callbacks"])
        gauges.append({key: sr["callbacks"].get(key) for key in GAUGES})
        rust.update(raw["counters"])
        segment_rust_counters.append(raw["counters"])
        fd.append(read(segment / "derivative_nodes.json"))
        exits.append(segment_exit)
        trace.append({"accepted_times": raw["accepted_times"],
                      "accepted_states": raw["accepted_states"], "config": config})
        accepted_states += len(raw["accepted_states"])
        segment_wall.append(sr["wall_s"])
        raw_flags.append({key: raw.get(key) for key in (
            "attempts", "internal_steps", "rejected_steps", "jacobian_reuses",
            "roundoff_step_restarts", "output_clipped_steps", "callback_failure",
            "pending_request")})
        wire["logged_bytes"] += (segment / "rpc.jsonl").stat().st_size
        for line in (segment / "rpc.jsonl").read_text().splitlines():
            row = json.loads(line)
            direction, msg = row["direction"], row["message"]
            wire[direction + "_messages"] += 1
            wire[direction + "_canonical_message_bytes"] += len(
                (json.dumps(msg, allow_nan=False) + "\n").encode())
            if msg.get("type") == "request":
                wire["rpc_" + msg["op"]] += 1
    physical = {key: result[key] for key in PHYSICAL}
    process = read(root / (name + ".PROCESS_RECEIPT.json"))
    derived_checks = {
        "job_payload_sha_bytes_and_cardinality": payloads == receipt["payload_files"],
        "outer_process_receipt": all(obs[key] == value for key, value in process.items()),
        "physical_bits_from_raw_result": binary64(physical) == obs["physical_bits"],
        "trace_bits_from_segment_raw": binary64(trace) == obs["trace_bits"],
        "fd_nodes_bits_from_raw": binary64(fd) == obs["fd_nodes_bits"],
        "independent_balances_bits_from_raw": binary64(independent) == obs["independent_balances_bits"],
        "callback_counters_from_raw": dict(callbacks) == obs["callbacks"],
        "rust_counters_from_raw": segment_rust_counters == obs["rust_counters"],
        "rpc_counts_and_sizes_from_raw": dict(wire) == obs["communication"],
        "rhs_evaluation_counter": result["rhs_evaluations"] == callbacks["original_rhs_evaluations"] == obs["rhs_evaluations"],
        "solver_diagnostics_from_raw": binary64(result["solver_diagnostics"]) == binary64(obs["solver"]),
        "job_and_reference_clocks": receipt["wall_s"] == obs["job_wall_s"] and result["wall_s"] == obs["reference_wall_s"],
        "process_exits_from_raw": exits == obs["process_exits"],
        "native_not_launched": all(receipt.get(key) is False for key in
            ("native_executed", "native_launch_attempted", "native_process_started")),
        "segments": all(all(check.values()) for check in segment_checks),
        "global_error_bound_null": receipt["global_error_bound"] is None and result["global_error_bound"] is None,
    }
    if "original_rhs_requests" in callbacks:
        derived_checks["logical_actual_hits"] = (callbacks["original_rhs_requests"]
            == callbacks["original_rhs_evaluations"] + callbacks["original_rhs_cache_hits"])
    row = {key: obs[key] for key in ("round", "method", "mode", *CLOCKS,
                                    "runner_process_wall_s", "execution", "exit_code")}
    row.update(name=name, job_payload_count=len(payloads), segments=len(segment_checks),
        accepted_state_rows_with_segment_initials=accepted_states,
        callbacks=dict(callbacks), communication=dict(wire), rust_counters=dict(rust),
        segment_gauges=gauges, segment_wall_raw_s=segment_wall,
        raw_flags=raw_flags, cleanup_wall_s=process["cleanup"]["wall_s"],
        cleanup_signals=len(process["cleanup"]["signals"]),
        observed_owned_processes=len(process["cleanup"]["observed_owned"]),
        checks=derived_checks, physical=physical, independent_balances=independent)
    return row, receipt


def ratio_summary(selected, lookup, reference_mode):
    later = [row for row in selected if row["round"] > 0]
    raw = {key: [lookup[(r["round"], r["method"], reference_mode)][key] / r[key]
                 for r in later] for key in CLOCKS}
    return {"raw": raw, "median": {key: statistics.median(v) for key, v in raw.items()}}


def make_report(data):
    plan, audit, groups = data["plan"], data["audit"], data["groups"]
    by_group = {(g["method"], g["mode"]): g for g in groups}
    fmt = lambda values, scale=1.: ", ".join(f"{v*scale:.6f}" for v in values)
    lines = [
        "# C21I: 같은 Rust 바이너리의 32개 제조 pilot 비교",
        "",
        "## 판정",
        "",
        "**실제 제조 ODE 32개가 모두 완료됐고, 각 backend의 같은 round에서 네 경로의 전체 accepted trace·물리 출력·FD node·Rust work counter가 binary64 수준에서 같았다.** exact 경로는 VigilODE의 원 RHS 실행을 423→372회(12.06%), Diffsol은 74→71회(4.05%)로 줄였다. 이 작은 입력에서 전체 프로세스 시간의 일관된 단축은 확인되지 않았다. 경량화의 일부 구조와 함수 실행 감소는 관측 사실이지만, NCP/native chemistry 가속 또는 일반적인 backend 속도 순위로 해석하지 않는다.",
        "",
        "이 문서는 기존 C8 실측의 read-only 집계다. 저장된 32개 observation과 각 job/segment 원시 파일을 다시 읽었으며, 새로운 ODE·native·콜백 benchmark·Rust 컴파일·과거 과학 테스트 실행은 모두 0이다. 하네스의 C9 검토와 발견된 failure-accounting 수정은 `../paired_pilot_review_01/REVIEW_CLOSE_KO.md`에서 이미 닫혔다.",
        "",
        "| 상태 축 | 이 분석에서 확인한 범위 |",
        "|---|---|",
        "| 실행 | 제조 pilot 32/32 COMPLETE, Rust segment 96개; native chemistry 0 |",
        "| 게시 | 이 분석은 GitHub 쓰기를 수행하지 않음. 현재 게시 상태는 별도 실제 publication receipt가 결정 |",
        "| 백업 | 원시 근거를 바꾸지 않고 새 분석 디렉터리에 create-only 저장. 외부 provider ACK는 이 영수증 범위 밖 |",
        "| DAG | 기존 C8 실측 분석 완료. NCP 실행·native 평가·전역 오차는 별도 미충족 노드 |",
        "",
        "## 1. 입력, 실행 범위와 근거",
        "",
        "원시 자료는 `../paired_pilot_final/`의 PLAN, SOURCE_BEFORE/AFTER, OBSERVATION 32개, JOB_RECEIPT 32개, segment raw 및 최종 SUMMARY/HARNESS_RECEIPT/PAYLOAD_MANIFEST다. `RAW_AUDIT.json`에는 각 observation을 원시 result/segment/RPC에서 다시 집계한 검사와 모든 반복값이 있다.",
        "",
        f"전체 manifest의 payload **{audit['payload_count']}개**, **{audit['payload_bytes']:,} bytes**를 SHA256·길이·파일 집합으로 확인했다. Job receipt에 선언된 payload는 합계 **{audit['job_payload_count']}개**이며, 원래 H 8개 job은 각 30개, I 24개 job은 각 31개다. JOB_RECEIPT 자체는 각 job의 자체 payload에서 제외되고 상위 manifest가 보존한다. 분석 전후 입력 payload와 manifest가 그대로였고, 측정 SOURCE_BEFORE/AFTER는 동일했다.",
        "",
        "| 항목 | 실제 설정 |",
        "|---|---|",
        "| 제조 입력 | 기존 H smoke, Y=0, M=9, Δx=10⁻⁷, 물리 full state 28 / integrated state 26 |",
        "| 비교 | VigilODE Rodas5P / Diffsol BDF × 원래 H / I baseline / vectorized / vectorized_exact |",
        "| 반복 | 최초 관측 1개 + 이후 fresh-process 3개; round별 mode 순서를 회전 |",
        "| 허용오차 | rtol=2×10⁻¹¹, α=2×10⁻¹⁴, fixed D, cell step divisor=8 |",
        f"| CPU/worker | child CPU {plan['cpu']}, monitor CPU {plan['monitor_cpu']}, 실제 허용 affinity {plan['affinity_before']}; 동시 job 1, BLAS/OpenMP/Rayon 1 |",
        "| 자원 경계 | affinity membership만 확인; 독점 CPU 배정은 확인하지 않음. 보호 CPU 55 미사용 |",
        "| Python 환경 | Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 |",
        "| timeout | H 300초 계산 예산 + 외부 하네스 30초 grace; 전체 실패 비용 보존 |",
        "",
        "바이너리는 사전에 실제 빌드된 하나를 모든 job에서 사용했다. SHA256 `202f4d93b94602f6649f427237afd6513b8fd933ae828cbd7a3cc1e90f7af934`, 4,660,352 bytes. BUILD_RECEIPT SHA256은 `800291c2e51424dd01afdef5f64672343fb167b9dd97a38f8c7b1210b0584c73`다. VigilODE 검증 pin `8a8bd409b1d96c7b7421f496d229e119fd3d284e` 및 Diffsol 0.17.1을 유지했다. 이 비교에 컴파일 시간은 들어가지 않는다. H runtime 8개, I runtime 3개와 F runtime 10개, G runtime 4개 및 각 manifest의 현재 바이트도 측정된 identity와 대조했다.",
        "",
        "최초 관측은 운영체제 cache를 비우지 않았고 바이너리는 이미 빌드·실행된 상태였다. 이후 관측도 새 Python 및 Rust 프로세스를 사용한다. 따라서 first/later를 통제된 cold/warm 성능으로 부르지 않는다. 제조 provider를 사용했으므로 native process와 native RPC는 없다. native exact admission helper의 파일 lease·owner/provenance 검사 비용도 이 제조 경로의 성능에 포함되지 않는다.",
        "",
        "## 2. 원래 H와 I baseline의 구분",
        "",
        "`c21h_original`은 수정하지 않은 H run_pilot/CellCallbacks를 사용한다. I `baseline`은 원래 Jacobian 산술을 유지하면서 private runner, 입력/source identity, guard 및 타이머 계측을 더한다. `vectorized`는 reduced Jacobian scratch와 tau 행의 NumPy 연산을 사용하고, `vectorized_exact`는 여기에 성공한 동일 (t,u) RHS 값의 cell별 재사용을 더한다. 그러므로 I baseline의 추가 비용을 0으로 놓거나 H의 타이머 미기록을 실행시간 0으로 처리하지 않았다.",
        "",
        "## 3. 프로세스 시간과 서로 다른 clock",
        "",
        "speedup은 같은 round의 **기준 시간 / 비교 시간**이다. 1보다 크면 해당 관측에서 단축됐다. 표의 중앙값은 세 개의 paired ratio의 중앙값이며, 서로 다른 표본의 중앙 시간끼리 나눈 값이 아니다.",
        "",
        "| Backend | 경로 | first process(s) | later process(s), 3개 | H/process 중앙 speedup | H/job 중앙 | H/reference 중앙 |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for g in groups:
        s = g["versus_h"]["median"]
        lines.append(f"| {g['method']} | {g['mode']} | {g['first_clocks']['process_wall_s']:.6f} | {fmt(g['later_clocks']['process_wall_s'])} | {s['process_wall_s']:.6f} | {s['job_wall_s']:.6f} | {s['reference_wall_s']:.6f} |")
    lines += ["", "I baseline을 기준으로 같은 세 round를 짝지은 값도 보존한다. 계측된 기준 안에서의 비교이며 원래 H 대비 수치를 대체하지 않는다.", "",
              "| Backend | 경로 | I baseline/process 중앙 speedup | I baseline/job 중앙 | I baseline/reference 중앙 |", "|---|---|---:|---:|---:|"]
    for g in groups:
        if g["mode"] not in ("vectorized", "vectorized_exact"):
            continue
        s = g["versus_i_baseline"]["median"]
        lines.append(f"| {g['method']} | {g['mode']} | {s['process_wall_s']:.6f} | {s['job_wall_s']:.6f} | {s['reference_wall_s']:.6f} |")
    lines += ["", "전체 32개 process wall 합은 **35.485946871초**, 하네스 자체 clock은 **36.156931410초**다. process wall에는 interpreter/import, identity/fixture 준비, 세 Rust process의 launch, 25ms ownership 관측 polling, 출력 및 cleanup이 포함된다. job wall과 reference wall은 더 안쪽의 서로 다른 구간이다. 콜백 타이머는 그 내부 일부를 재고, segment wall도 겹치는 구간을 포함하므로 이들을 더해서 전체 시간을 분해할 수 없다.", "",
        "VigilODE의 vectorized/exact process 중앙 speedup은 각각 0.845647/0.920985로 이 표본에서 느리다. Diffsol은 1.045230/0.985440로 방향이 갈린다. 특히 Diffsol exact의 reference 중앙 speedup 1.276193만 골라 전체 실행 가속으로 표시하면 process 결과를 누락하게 된다. 반복이 3개이고 독점 자원이 아니므로 신뢰구간·일반적인 우위·최적 정책을 추정하지 않는다.", "",
        "## 4. work counter와 RHS 재사용", "",
        "다음 값은 backend별 모든 round·mode에서 일정했다. RHS의 실제 실행 수만 exact 경로에서 달라진다.", "",
        "| Backend | accepted steps | RHS/Jacobian/∂t RPC 요청 | 원래 RHS 호출 | exact 실제/논리/hit | factorization/setup |", "|---|---:|---|---:|---|---:|",
        "| VigilODE | 27 | 216 / 27 / 27 | 423 | 372 / 423 / 51 | direct factorization 27 |",
        "| Diffsol | 53 | 59 / 3 / 0 | 74 | 71 / 74 / 3 | linear solver setup 11 |", "",
        "VigilODE는 gas FD 54열과 tau analytic 243열, ledger zero 405열을 평가했고 ∂t의 flat branch 3개를 유지했다. Diffsol은 gas FD 6열, tau analytic 27열, ledger zero 45열이다. exact의 논리 요청 수는 `actual + hit`와 맞는다. 반복 4개를 합하면 각 backend의 exact에서 204회/12회의 원 RHS 실행을 피했지만, native 호출 감소의 실측은 아니다.", "",
        "VigilODE의 rejected/fallback/linear-solve-failure/nonlinear-failure 카운터는 모두 0이며 direct solve는 216회다. Diffsol의 error-test-failure와 nonlinear-solver-fail은 0, nonlinear iteration은 56회다. Diffsol의 별도 rejected_steps 필드는 제공되지 않으므로 그 값을 임의로 만들어 넣지 않았다. 원래 H가 가진 마지막 ULP의 order-1 history restart는 세 segment 중 두 개에 실제로 남고, 네 모드에서 동일하다. 이 비용은 성공 실행의 clock에 이미 포함됐다.", "",
        "## 5. RPC와 타이머 범위", "",
        "| Backend | actual rpc.jsonl 로그 bytes/job | Python→Rust message 수 / canonical bytes | Rust→Python message 수 / canonical bytes |", "|---|---:|---|---|",
        "| VigilODE | 395,831 | 273 / 216,343 | 276 / 155,332 |",
        "| Diffsol | 106,869 | 65 / 38,545 | 68 / 62,472 |", "",
        "모든 round·mode에서 이 통신량은 같았다. exact는 Python 내부의 원 RHS를 재사용하므로 현재 JSONL RPC 개수와 메시지 내용을 줄이지 않는다. 실제 파일 길이는 direction wrapper를 포함한 로그 길이다. message bytes는 저장된 메시지를 Python json.dumps로 재직렬화한 수치이며, 특히 Rust가 원래 보낸 wire byte와 같다고 주장하지 않는다. 원시 log 합계는 8,043,200 bytes다.", "",
        "| Backend | I 경로 | first RHS timer(ms) | later RHS timer(ms), 3개 | later key timer(ms), 3개 | later hit timer(ms), 3개 |", "|---|---|---:|---|---|---|"]
    for g in groups:
        if g["mode"] == "c21h_original":
            continue
        t = g["timer_ns"]
        lines.append(f"| {g['method']} | {g['mode']} | {t[TIMERS[0]][0]/1e6:.6f} | {fmt(t[TIMERS[0]][1:],1e-6)} | {fmt(t[TIMERS[1]][1:],1e-6)} | {fmt(t[TIMERS[2]][1:],1e-6)} |")
    lines += ["", "`original_rhs_execution_ns`는 계측된 super().original 호출 내부의 wall nanoseconds다. key timer는 키 생성, hit timer는 성공 lookup과 result copy의 일부를 잰다. guard, cache miss lookup, 삽입/퇴출, 일부 복사, Jacobian 전체, JSON 변환, linear solve와 process 시작을 완전히 분리하지 않았다. 타이머 읽기 자체에도 비용이 있으므로 잔차 시간을 특정 연산 비용으로 귀속하지 않는다. H 원본에는 이 추가 timer가 없다.", "",
        "## 6. 경량화와 메모리 계측의 실제 범위", "",
        "vectorized/exact는 cell마다 26×26 binary64 scratch 1개(5,408 bytes)를 만들었다. 세 segment 합으로는 scratch allocation 3개/16,224 bytes지만 이는 세 cell의 누계이며 실제 peak RSS가 아니다. 반환 행렬은 owned copy로 유지해 scratch aliasing을 피한다. 결과 copy는 VigilODE 27개, Diffsol 3개다.", "",
        "새 계측은 VigilODE 27회, Diffsol 3회의 full 28×28 matrix allocation 회피를 기록했다. 원본 source의 해당 zero array 크기는 6,272 bytes이므로 그 한 종류의 누적 생성량은 각각 169,344/18,816 bytes에 대응한다. 원래 경로의 reduced indexing 및 scaling temporary와 새 경로의 보조 배열은 전체 allocator 계측이 아니므로 총 RAM 절감으로 환산하지 않는다. I baseline의 해당 counter 0은 원본이 할당을 하지 않았다는 뜻이 아니다.", "",
        "exact cache는 cell별 capacity 16, 관측 peak entry 16, 기록된 key/value payload 6,784 bytes다. job-level Counter가 더한 capacity48/peak48/payload20,352는 서로 다른 세 cell의 gauge 합이다. 동시에 48-entry cache를 썼다고 읽으면 안 된다. Python object/OrderedDict overhead는 이 bytes에 들어가지 않는다. VigilODE는 miss372/hit51/eviction324, result copy795회; Diffsol은 miss71/hit3/eviction23, result copy145회다. 캐시가 원 RHS 실행을 줄이는 대신 lookup·guard·소유 복사·저장 비용을 추가한 사실을 함께 보존한다.", "",
        "## 7. 물리 출력과 수지의 판정 경계", "",
        "모드 간 비교는 각 backend의 같은 round를 기준으로 했다. 24개 비자기 비교에서 fixture/input/bridge identity, 전체 물리 출력과 log-survivor/underflow 기록, accepted time/state/config, gas/time FD nodes, 독립 ledger 재합산, Rust counters, runtime이 모두 같았다. 원본 8개 자기 비교는 독립 검증 건수로 더하지 않는다. 원시 segment trace에는 initial row를 포함해 VigilODE job당30개, Diffsol job당56개의 accepted state row가 있으며 이 분석이 원시 파일에서 observation bits를 재구성해 확인했다.", "",
        "| Backend | result number defect(/H) | 독립 재합산 number defect(/H) | energy defect(eV/H), 양쪽 동일 |", "|---|---:|---:|---:|"]
    for method in plan["methods"]:
        g = by_group[(method, "c21h_original")]
        p, b = g["physical"], g["independent_balances"]
        lines.append(f"| {method} | {p['number_defect_H']:+.16e} | {b['computed']['number_defect_H']:+.16e} | {p['energy_defect_eV_H']:+.16e} |")
    lines += ["", "원 result와 독립 재합산의 number defect는 합산 순서에 따른 몇 ULP 차이를 이미 기록한다. VigilODE의 photon number 및 첫 species defect도 해당 reported_agreement가 false다. 이를 삭제하거나 두 산술이 bitwise 같다고 쓰지 않는다. 각각의 출력과 그 차이가 모드 간에는 그대로 같다. Photon clipping=false, positive-population underflow=0, accepted/internal tau minimum=0이며, 15개 ledger와 전체 물리 state/error norm을 유지했다.", "",
        "이 제조 입력의 ledger closure는 해당 수지 진단이다. 독립 참값과의 trajectory/global error bound 또는 native 수렴을 제공하지 않는다. `global_error_bound=null`을 유지한다. Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle parity는 이 결과로 해제하지 않는다.", "",
        "## 8. 실패 비용, 보존과 다음 판단", "",
        "32개 실행에서 timeout·nonzero exit·cleanup 잔류·native launch·accepted trace 누락은 관측되지 않았다. 하네스는 시작 전 ATTEMPT와 종료 PROCESS_RECEIPT를 남기고 실패한 시도도 process wall 합계에 포함하도록 수정됐지만, 이번 표본에서 실제 timeout 비용의 성능 분포를 측정한 것은 아니다. 이전 focused failure-contract의 실패 raw와 수정 전 source는 별도 디렉터리에 보존한다. 성공한 후보만 골라 시간 합계에서 실패를 제외하는 집계는 사용하지 않았다.", "",
        "이번 결과로 채택할 수 있는 것은 현재 Y0/M9 입력에서의 출력 동일성, matrix scratch 방식과 exact RHS 실행 감소다. 현재 기본 경로의 자동 병렬화·캐시 자동 활성화·더 빠른 backend 선택을 정당화하는 성능 증거는 부족하다. 큰 M/helium component 측정 및 독립 Schur/JVP prototype의 근거는 별도 실험 범위이며 여기에 합치지 않았다. Native/NCP의 현재 자원·locked compile·작은 호환 수정·실제 실행은 별도 후속 단계로 남는다. Parent가 수행하는 fd_half 두 실행도 이 32개에 합산하지 않는다.", "",
        "### 근거 파일", "",
        "- `../paired_pilot_final/{PLAN,SOURCE_BEFORE,SOURCE_AFTER,SUMMARY,HARNESS_RECEIPT,PAYLOAD_MANIFEST}.json`", "- `../paired_pilot_final/round*/{JOB_RECEIPT,result,INDEPENDENT_BALANCES}.json` 및 각 `segments/segment_*/`", "- `RAW_AUDIT.json`, `ANALYSIS_RECEIPT.json`, `PAYLOAD_MANIFEST.json`", "- `../../benchmarks/paired_pilot.py`, `../../benchmarks/analyze_paired_pilot.py`", "- `../paired_pilot_review_01/REVIEW_CLOSE_KO.md`", "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.input.resolve(), args.out.resolve()
    if root == out or root in out.parents:
        raise ValueError("OUTPUT_MUST_BE_SEPARATE_FROM_IMMUTABLE_INPUT")
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    source = record(__file__)
    with (out / "analyze_paired_pilot_source.py").open("xb") as stream:
        stream.write(Path(__file__).read_bytes())
    plan, summary = read(root / "PLAN.json"), read(root / "SUMMARY.json")
    before, after = read(root / "SOURCE_BEFORE.json"), read(root / "SOURCE_AFTER.json")
    manifest = read(root / "PAYLOAD_MANIFEST.json")
    raw_manifest_identity = record(root / "PAYLOAD_MANIFEST.json")
    input_before = payload_snapshot(root)
    obs_files = sorted(root.glob("*.OBSERVATION.json"))
    observations = [read(p) for p in obs_files]
    rows, receipts = [], []
    for path, obs in zip(obs_files, observations):
        row, receipt = aggregate_job(root, path.name.removesuffix(".OBSERVATION.json"), obs)
        rows.append(row); receipts.append(receipt)
    expected_keys = {(r, m, v) for r in range(plan["rounds"])
                     for m in plan["methods"] for v in plan["modes"]}
    keys = [(r["round"], r["method"], r["mode"]) for r in rows]
    lookup = {key: row for key, row in zip(keys, rows)}
    source_expected, current_source_checks = audit_current_sources(before, receipts[0])
    comparison_fields = ("fixture_sha256", "input_identity", "bridge_identity",
        "physical_bits", "trace_bits", "fd_nodes_bits", "independent_balances_bits",
        "rust_counters", "runtime")
    obs_lookup = {(r["round"], r["method"], r["mode"]): r for r in observations}
    comparisons = []
    for obs in observations:
        if obs["mode"] == "c21h_original":
            continue
        ref = obs_lookup[(obs["round"], obs["method"], "c21h_original")]
        comparisons.append({"round": obs["round"], "method": obs["method"], "mode": obs["mode"],
            "checks": {key: obs[key] == ref[key] for key in comparison_fields}})
    groups = []
    for method in plan["methods"]:
        for mode in plan["modes"]:
            selected = sorted((r for r in rows if r["method"] == method and r["mode"] == mode),
                              key=lambda row: row["round"])
            groups.append({"method": method, "mode": mode, "attempts": len(selected),
                "first_clocks": {k: selected[0][k] for k in CLOCKS},
                "later_clocks": {k: [r[k] for r in selected[1:]] for k in CLOCKS},
                "total_process_wall_s": sum(r["process_wall_s"] for r in selected),
                "versus_h": ratio_summary(selected, lookup, "c21h_original"),
                "versus_i_baseline": ratio_summary(selected, lookup, "baseline"),
                "timer_ns": {k: [r["callbacks"].get(k) for r in selected] for k in TIMERS},
                "callbacks_first": selected[0]["callbacks"], "communication_first": selected[0]["communication"],
                "rust_counters_first": selected[0]["rust_counters"],
                "physical": selected[0]["physical"], "independent_balances": selected[0]["independent_balances"]})
    estimates = {(g["method"],g["mode"]): g for g in summary["estimates"]}
    summary_checks = {str((g["method"],g["mode"])):
        g["versus_h"]["raw"] == estimates[(g["method"],g["mode"])]["later_paired_speedup_raw"]
        and g["versus_h"]["median"] == estimates[(g["method"],g["mode"])]["later_paired_speedup_median"]
        for g in groups}
    input_after = payload_snapshot(root)
    checks = {
        "payload_manifest_bytes_sha_and_set": input_before == manifest["files"]
            and len(input_before) == manifest["payload_count"],
        "payloads_unchanged_during_analysis": input_before == input_after
            and record(root / "PAYLOAD_MANIFEST.json") == raw_manifest_identity,
        "recorded_runtime_before_after_identical": before == after,
        "current_measured_runtime_source_match": all(current_source_checks.values()),
        "current_runtime_unchanged_during_analysis": all(record(p) == e for p,e in source_expected.items()),
        "source_unchanged_during_analysis": source == record(__file__),
        "planned_cardinality_and_uniqueness": len(keys) == len(set(keys)) and set(keys) == expected_keys,
        "all_job_raw_reaggregations": all(all(r["checks"].values()) for r in rows),
        "all_24_nonself_comparisons": len(comparisons) == 24 and all(all(c["checks"].values()) for c in comparisons),
        "all_timing_summary_ratios": all(summary_checks.values()),
        "all_jobs_complete_and_exits": all(r["execution"] == "COMPLETE" and r["exit_code"] == 0 for r in rows),
        "all_cleanup_complete_no_signals": all(o["cleanup"]["complete"] is True and not o["cleanup"]["signals"] for o in observations),
        "all_native_launch_flags_false": all(all(o.get(k) is False for k in ("native_executed", "native_process_started", "native_launch_attempted")) for o in observations),
        "no_timeouts": all(o["timed_out"] is False for o in observations),
    }
    audit = {"checks": checks, "accepted": all(checks.values()),
        "payload_count": len(input_before), "payload_bytes": sum(v["bytes"] for v in input_before.values()),
        "observation_count": len(rows), "job_payload_count": sum(r["job_payload_count"] for r in rows),
        "segment_count": sum(r["segments"] for r in rows),
        "accepted_state_rows_with_segment_initials": sum(r["accepted_state_rows_with_segment_initials"] for r in rows),
        "total_rpc_log_bytes": sum(r["communication"]["logged_bytes"] for r in rows),
        "total_process_wall_s": sum(r["process_wall_s"] for r in rows),
        "nonself_comparison_count": len(comparisons), "self_comparisons_not_counted": 8,
        "current_source_file_count": len(current_source_checks)}
    data = {"schema": "C21I_PAIRED_PILOT_READ_ONLY_ANALYSIS_V1", "plan": plan,
        "input_manifest_identity": raw_manifest_identity, "audit": audit,
        "source_checks": current_source_checks, "comparisons": comparisons,
        "summary_ratio_checks": summary_checks, "groups": groups, "rows": rows,
        "scope": "Existing C8 measurement analysis; no new scientific verification or solver execution"}
    new(out / "RAW_AUDIT.json", data)
    with (out / "PAIRED_PILOT_REPORT_KO.md").open("x") as stream:
        stream.write(make_report(data))
    new(out / "ANALYSIS_RECEIPT.json", {"schema": "C21I_PAIRED_PILOT_ANALYSIS_RECEIPT_V1",
        "at": datetime.now(timezone.utc).isoformat(), "analysis_wall_s": time.monotonic()-started,
        "analysis_source": source, "input_directory": str(root),
        "input_manifest": raw_manifest_identity, "checks": checks,
        "accepted": audit["accepted"], "python": platform.python_version(),
        "observations_read": len(rows), "job_payloads_sha_verified": audit["job_payload_count"],
        "raw_payloads_sha_verified": audit["payload_count"],
        "new_solver_runs": 0, "new_native_runs": 0, "new_callback_runs": 0,
        "new_compile_runs": 0, "old_science_suite_runs": 0,
        "global_error_bound": None, "publication_action": "NONE",
        "backup_action": "CREATE_ONLY_LOCAL_ANALYSIS_EXTERNAL_ACK_NOT_CLAIMED",
        "dag": "C8_EXISTING_MEASUREMENT_ANALYSIS_COMPLETE; NATIVE_NCP_SEPARATE",
        "skill_context_used": {"name": "physmath-research-loop", "version": "1.3.0",
            "stage": "C8 original measured-results analysis continuation",
            "binding": "Parent task after one completed C9/failure-accounting bounded repair; no additional review cycle or runtime rerun",
            "retroactive_relabeling_of_previous_evidence": False}})
    new(out / "PAYLOAD_MANIFEST.json", {"files": payload_snapshot(out),
                                       "payload_count": len(payload_snapshot(out))})
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    return 0 if audit["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
