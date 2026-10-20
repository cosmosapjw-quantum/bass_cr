"""Read-only audit and report of the retained callback component run.

No callback, native chemistry or ODE is evaluated by this analyzer.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics


HERE = Path(__file__).resolve().parents[1]


def record(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def load(path):
    return json.loads(Path(path).read_text())


def lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def med(values):
    return statistics.median(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE / "evidence/component_benchmark_01")
    parser.add_argument("--output", type=Path, default=HERE / "evidence/component_analysis_01")
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = load(source / "PAYLOAD_MANIFEST.json")
    for name, expected in manifest["files"].items():
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts, "INPUT_MANIFEST_PATH")
        require(record(source / relative) == expected, "INPUT_PAYLOAD_MISMATCH " + name)
    require(manifest["payload_count"] == len(manifest["files"]), "PAYLOAD_COUNT")
    before, after = load(source / "SOURCE_BEFORE.json"), load(source / "SOURCE_AFTER.json")
    require(before == after, "DEPENDENCY_SOURCE_BEFORE_AFTER")
    require(record(HERE / "benchmarks/callback_components.py") == before["benchmark"], "BENCHMARK_SOURCE_NOW_DIFFERS")
    require(record(HERE / "optimized_adapter.py") == before["optimized_adapter"], "ADAPTER_SOURCE_NOW_DIFFERS")
    receipt = load(source / "EXECUTION_RECEIPT.json")
    operations = lines(source / "operation_repeats.jsonl")
    batches = lines(source / "batch_repeats.jsonl")
    tasks = lines(source / "task_repeats.jsonl")
    reference = load(source / "REFERENCE_OUTPUT_INDEX.json")
    reference_map = {(row["case"], row["point"], row["operation"]): row for row in reference}
    require(len(reference_map) == 54, "CANONICAL_REFERENCE_COUNT")
    require(len(operations) == 3888 and len(batches) == 216 and len(tasks) == 432, "MEASURED_ROW_COUNTS")
    require(len({row["batch"] for row in batches}) == len(batches), "DUPLICATE_BATCH_ID")
    require(len({(row["batch"], row["worker"], row["cycle"], row["operation"]) for row in operations}) == len(operations), "DUPLICATE_OPERATION_ROW")
    require(len({(row["batch"], row["worker"]) for row in tasks}) == len(tasks), "DUPLICATE_TASK_ROW")
    batch_map = {row["batch"]: row for row in batches}
    by_task = defaultdict(list)
    for row in operations:
        baseline = reference_map[(row["case"], row["point"], row["operation"])]
        require(row["bitwise_equal_original"] is True and row["shape"] == baseline["shape"] and
                row["float64_bytes_sha256"] == baseline["float64_bytes_sha256"], "OUTPUT_IDENTITY " + row["batch"])
        require(isinstance(row["elapsed_ns"], int) and row["elapsed_ns"] > 0, "TIMING_DOMAIN")
        by_task[(row["batch"], row["worker"])].append(row)
    actual_calls = 0
    fd_sequences = {}
    task_tallies = []
    for task in tasks:
        batch = batch_map[task["batch"]]
        group = by_task[(task["batch"], task["worker"])]
        require(len(group) == 9, "TASK_OPERATION_COUNT")
        gas = int(batch["case"].split("_g")[1])
        original_per_triplet = 2*gas+5
        expected_calls = 3*original_per_triplet
        if batch["mode"] == "vectorized_exact":
            expected_calls = 3*(original_per_triplet-2) if batch["regime"] == "cold_sequence" else 0
        actual = task["actual_rhs_after"]-task["actual_rhs_before"]
        require(actual == expected_calls == task["count_deltas"]["original_rhs_evaluations"], "ACTUAL_RHS_COUNTS")
        for name in ("rhs_requests", "jacobian_requests", "partial_t_requests"):
            require(task["count_deltas"][name] == 3, "LOGICAL_CALLBACK_COUNTS")
        require(task["thread_affinity"] == [0, 1], "OBSERVED_WORKER_AFFINITY")
        actual_calls += task["actual_rhs_after"]
        key = (batch["case"], batch["regime"])
        if key in fd_sequences:
            require(task["fd_nodes"] == fd_sequences[key], "FD_NODE_OR_ORDER_DIFFERENCE")
        else:
            fd_sequences[key] = task["fd_nodes"]
        if batch["mode"] != "original":
            require(task["count_deltas"]["original_rhs_requests"] == 3*original_per_triplet, "LOGICAL_ORIGINAL_RHS_REQUESTS")
            require(task["count_deltas"]["avoided_full_matrix_allocations"] == 3, "REDUCED_JACOBIAN_ALLOCATION_COUNT")
            require(task["count_deltas"]["jacobian_return_allocations"] == 3, "JACOBIAN_OUTPUT_OWNERSHIP_COUNT")
            require(task["counts_after"]["rhs_cache_peak_entries"] <= 16, "BOUNDED_CACHE_CAPACITY")
        task_tallies.append({"batch": task["batch"], "worker": task["worker"],
                             "actual_rhs": actual, "expected_actual_rhs": expected_calls})
    reference_calls = sum(load(path)["reference_actual_rhs_calls"] for path in sorted((source / "inputs").glob("*.json")))
    require(actual_calls + reference_calls == 13878 == receipt["actual_original_rhs_calls_including_reference_and_warmup"], "TOTAL_ORIGINAL_RHS_CALLS")
    for batch in batches:
        actual = sum(task["actual_rhs_after"]-task["actual_rhs_before"] for task in tasks if task["batch"] == batch["batch"])
        require(actual == batch["measured_actual_rhs_calls"], "BATCH_ORIGINAL_RHS_COUNT")
    summary = load(source / "SUMMARY.json")
    by_key = {(row["repeat"], row["case"], row["regime"], row["mode"], row["schedule"]): row for row in batches}
    cases = sorted({row["case"] for row in batches}, key=lambda value: (int(value.split("_")[0][1:]), value))
    cold_comparison = []
    warm_comparison = []
    for case in cases:
        for regime, target in (("cold_sequence", cold_comparison), ("warm_identical_point", warm_comparison)):
            row = {"case": case}
            for mode in ("original", "vectorized", "vectorized_exact"):
                serial = [by_key[(r, case, regime, mode, "serial_two_callbacks")]["elapsed_ns"] for r in range(3)]
                parallel = [by_key[(r, case, regime, mode, "two_thread_batch")]["elapsed_ns"] for r in range(3)]
                reference_serial = [by_key[(r, case, regime, "original", "serial_two_callbacks")]["elapsed_ns"] for r in range(3)]
                row[mode] = {"serial_batch_median_ms": med(serial)/1e6,
                             "serial_speedup_paired_raw": [old/new for old, new in zip(reference_serial, serial)],
                             "serial_speedup_paired_median": med([old/new for old, new in zip(reference_serial, serial)]),
                             "thread_speedup_paired_raw": [s/p for s, p in zip(serial, parallel)],
                             "thread_speedup_paired_median": med([s/p for s, p in zip(serial, parallel)])}
            target.append(row)
    operation_groups = defaultdict(list)
    for row in operations:
        if row["regime"] == "cold_sequence" and row["schedule"] == "serial_two_callbacks":
            operation_groups[(row["case"], row["operation"], row["mode"])].append(row["elapsed_ns"])
    component_medians = [{"case": case, "operation": operation,
                         **{mode+"_median_us": med(operation_groups[(case, operation, mode)])/1e3
                            for mode in ("original", "vectorized", "vectorized_exact")}}
                        for case in cases for operation in ("jacobian", "rhs", "partial_t")]
    thread_batches = [row for row in batches if row["schedule"] == "two_thread_batch"]
    thread_id_counts = Counter(len(set(row["thread_ids"])) for row in thread_batches)
    thread_comparisons = [row for row in summary["paired_comparisons"] if row["comparison"].startswith("same two")]
    audit = {"schema": "C21I_CALLBACK_COMPONENT_RAW_AUDIT_V1", "status": "PASS_SCOPED",
             "analyzer": record(__file__), "input_payload_manifest": record(source / "PAYLOAD_MANIFEST.json"),
             "payload_files_verified": len(manifest["files"]), "source_before_after": "PASS",
             "operations": len(operations), "bitwise_output_hashes": "PASS_ALL_MEASURED",
             "tasks": len(tasks), "actual_rhs_and_cache_count_model": "PASS_ALL_TASKS",
             "fd_node_sequence_identity": "PASS_ALL_MODES_REPEATS_SCHEDULES",
             "reference_actual_rhs_calls": reference_calls, "other_actual_rhs_calls": actual_calls,
             "total_actual_rhs_calls": actual_calls+reference_calls,
             "threadpool_max_workers": 2, "observed_distinct_worker_ids_per_batch": dict(thread_id_counts),
             "thread_comparisons_with_median_speedup_below_one": sum(row["ratio"]["median"] < 1 for row in thread_comparisons),
             "thread_comparison_groups": len(thread_comparisons),
             "cold_serial_comparisons": cold_comparison, "warm_serial_comparisons": warm_comparison,
             "cold_serial_component_medians": component_medians,
             "task_count_checks": task_tallies, "callback_reruns_by_analyzer": 0,
             "native_calls": 0, "ode_integrations": 0, "global_error_bound": None}
    write(output / "RAW_AUDIT.json", audit)
    report = ["# C21I 실제 원 RHS callback 성분 측정", "",
        "실제 C21H callback에 연결된 원 `reference_tau.py` RHS closure를 재사용해, "
        "벡터화와 성공한 동일 입력 RHS 재사용의 비용을 측정했다. 216개 batch의 432개 독립 callback이 반환한 "
        "3,888개 측정 출력은 같은 입력의 원 callback 출력과 binary64 바이트가 모두 같았다. "
        "이는 제조 microphysics의 callback 성분 검사이며 ODE·native chemistry·Rust 실행은 각각 0이다.", "",
        "## 실행·게시·백업·DAG", "",
        "| 축 | 이 산출물의 상태 |", "|---|---|",
        "| 실행 | `COMPLETE_SCOPED`; 6.776초, 3 repeats, 54개 원 reference 출력·3,888개 timed 출력 |",
        "| 게시 | root가 처리하는 실제 GitHub 영수증을 따른다. 이 harness는 GitHub를 변경하지 않았다. |",
        "| 백업 | 원 raw는 create-only `component_benchmark_01`, 새 분석은 `component_analysis_01`에 보존했다. 원격 저장 ACK는 root 최종 영수증을 따른다. |",
        "| DAG | callback component 비교는 `PASS_SCOPED`; 실제 solver trajectory·native·전역오차 결론은 열어 둔다. |", "",
        "## 무엇을 실제로 실행했는가", "",
        "검증된 C21H private module의 원 event driver가 첫 event cell의 `reduced_rhs` closure를 생성한 직후 "
        "`solve_ivp` sentinel에서 멈췄다. 이후 그 closure만 원/벡터/정확 cache callback에 넘겼다. "
        "RHS 산식을 별도로 복제하지 않았다. source 전후 대조는 C21H runtime 8개, C21G runtime 4개, "
        "상속 C21F source 10개 및 실제 실행한 `optimized_adapter.py`·harness를 대상으로 통과했다. "
        "최적화 source는 `bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e`이다.", "",
        "M=9는 원 `make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003)`를 사용했다. M=64/128은 같은 "
        "9개의 q·birth cohort를 반복하고 각 원 amount를 그 cohort의 복제 수로 나눴다. fixture JSON에 "
        "원 amount와 복제 합의 `math.fsum`을 남겼다. 큰 M은 제조 확장이다. "
        "각 경우 Y=0은 gas unknown 2개, 원 Y_HE는 4개이며 passive ledger 15개를 모두 유지한다.", "",
        "각 task는 독립 provider·private RHS closure·callback·cache를 갖는다. `cold_sequence`는 새 빈 cache에서 "
        "서로 다른 세 state/time 쌍에 `jacobian → rhs → partial_t`를 호출한다. `warm_identical_point`는 "
        "한 triplet으로 cache를 준비한 뒤 같은 점을 세 번 더 요청한다. 이 요청 순서는 실험 설계이며 "
        "실제 ODE trajectory에서 관측한 순서나 cache hit율이 아니다. cold는 CPU cache flush를 뜻하지 않는다.", "",
        "Linux local process의 최초 허용 CPU는 0–8이었으며 이 실행은 0/1만 사용했다. CPU 55는 사용하지 않았다. "
        "BLAS/OMP/MKL/NumExpr/Rayon/vecLib worker 환경을 NumPy import 전에 1로 설정했고, 로드된 NumPy·SciPy "
        "OpenBLAS도 `threadpoolctl`에서 각각 1로 관측했다. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0이었다. "
        "cgroup CPU quota는 8 CPU분, RAM 상한은 8 GiB였으며 독점 CPU 할당은 확인하지 않았다. NCP 자원 자료가 아니다.", "",
        "## 빈 cache에서 서로 다른 세 점", "",
        "각 batch는 같은 양의 두 task를 수행한다. 아래 시간은 serial batch의 3회 중앙값, 배속은 "
        "각 repeat의 `원 batch / 후보 batch` 비율 3개의 중앙값이다. 작은 표본·비독점 환경의 관측값이다. "
        "배속 1 미만인 결과도 그대로 유지한다.", "",
        "| M / gas | 원 batch ms | 벡터화 ms | 벡터 배속 | 정확 재사용 ms | 정확 재사용 배속 |",
        "|---|---:|---:|---:|---:|---:|"]
    for row in cold_comparison:
        report.append(f"| {row['case']} | {row['original']['serial_batch_median_ms']:.3f} | {row['vectorized']['serial_batch_median_ms']:.3f} | {row['vectorized']['serial_speedup_paired_median']:.3f} | {row['vectorized_exact']['serial_batch_median_ms']:.3f} | {row['vectorized_exact']['serial_speedup_paired_median']:.3f} |")
    report += ["", "M=9/G4의 벡터화만 사용한 batch는 이 표본에서 느렸다. M=64/128의 cold serial 전체 callback "
        "batch는 벡터화로 약 1.13–1.22배, 정확 재사용까지 포함하면 약 1.25–1.49배였다. "
        "M=9의 동작을 자동으로 병렬화하거나 벡터 경로의 보편적인 가속을 선언할 근거는 아니다.", "",
        "### 성분별 시간", "",
        "다음은 cold serial 개별 callback 18개(3 repeats × 2 tasks × 3 points)의 중앙값이다. "
        "실행 순서상 정확 재사용의 RHS는 직전 Jacobian의 base RHS를 재사용하고, 시간 편미분도 그 base를 재사용한다. "
        "각 Jacobian의 gas 차분은 원래의 실제 표현 가능한 동일 노드를 사용한다.", "",
        "| M / gas | 성분 | 원 μs | 벡터 μs | 정확 재사용 μs |", "|---|---|---:|---:|---:|"]
    for row in component_medians:
        report.append(f"| {row['case']} | {row['operation']} | {row['original_median_us']:.1f} | {row['vectorized_median_us']:.1f} | {row['vectorized_exact_median_us']:.1f} |")
    report += ["", "## 실제 원 RHS 호출과 warm 범위", "",
        "원 closure 내부의 `calls` cell을 직접 읽었으며 callback의 `original_rhs_evaluations` 차이와 "
        "모든 432개 task에서 일치했다. 원 기준 triplet은 gas 차원 G에 대해 `2G+5`회이다. "
        "빈 cache의 정확 재사용은 같은 base의 중복 2회를 없애므로 `2G+3`회이다. "
        "한 batch(2 tasks × 3 points)는 G2에서 54→42회, G4에서 78→66회였다. "
        "벡터화만으로는 원 RHS 호출 수를 줄이지 않는다.", "",
        "warm 동일점은 gas·time 차분점까지 cache에 모두 들어가며, timed 3 triplet 동안 실제 원 RHS는 0회였다. "
        "각 캐시 hit에서도 domain·소유권·실행 deadline guard 및 결과 복사는 실행된다. "
        "이 최선 조건에서 cold 표와 같은 기준의 serial 배속은 아래와 같았다.", "",
        "| M / gas | warm 정확 재사용 배속 | timed 실제 원 RHS / batch |", "|---|---:|---:|"]
    for row in warm_comparison:
        report.append(f"| {row['case']} | {row['vectorized_exact']['serial_speedup_paired_median']:.3f} | 0 |")
    report += ["", "4.82–11.19배의 warm 수치는 의도적으로 반복한 동일점에만 해당한다. "
        "설정·warmup은 별도 raw 시간/호출 수로 남겼으며 `including_setup_and_warmup_ns`에서 합산했다. "
        "원 reference 생성과 warmup을 포함한 실제 원 RHS 총수는 13,878회다. "
        "Native chemistry 요청 수, 전체 ODE 가속이나 다른 solver controller의 결과로 옮기지 않는다.", "",
        "## 두 task의 thread batch", "",
        "`ThreadPoolExecutor(max_workers=2)` 생성, 제출, join, shutdown을 batch 시간에 포함했다. "
        f"실제 worker thread ID는 {thread_id_counts[2]}/108 batch에서 2개였다. 나머지 {thread_id_counts[1]}개는 "
        "짧은 작업의 lazy scheduling 때문에 한 worker가 둘 다 처리했다. 모든 task의 실제 thread ID와 affinity를 "
        "raw에 남겼으며 전체 108개를 동시 두-thread 실행으로 부르지 않는다. 고정된 최대 worker 2 정책의 "
        "현실적인 실행 비용 비교이다.", "",
        f"case·regime·mode의 36개 묶음 중 {audit['thread_comparisons_with_median_speedup_below_one']}개는 "
        "serial/thread wall 비율의 중앙값이 1 미만이었다. warm cache가 계산을 더 짧게 만들 때 thread의 고정 비용도 "
        "상대적으로 커졌다. 이 범위에서 job/thread 수를 자동으로 늘리는 기본 정책은 채택하지 않는다. "
        "독립된 큰 native 작업이나 supplied JVP/stage 병렬의 성능은 이 실험에서 측정하지 않았다.", "",
        "## 보존된 근거와 다음 연결", "",
        "`component_benchmark_01/contract.json`은 측정 전에 저장한 범위·예산이며 `operation_repeats.jsonl`, "
        "`task_repeats.jsonl`, `batch_repeats.jsonl`에 모든 반복값이 있다. `reference_outputs/*.npy`에는 "
        "54개의 원 출력 배열, `inputs/*.json`에는 실제 fixture·D·dynamic map·binary64 state가 있다. "
        "전후 source 목록과 runtime inventory를 함께 보존했다. 현재 분석은 원 70개 payload의 SHA256을 다시 "
        "대조하고 모든 출력 hash·실제 호출·차분 노드 순서를 읽어서 검사했으며 callback을 재실행하지 않았다.", "",
        "후속 runner는 동일 새 bridge binary, 같은 fixture·rtol·alpha·worker 수에서 실제 callback 요청 순서와 "
        "accepted state·전체 수지를 비교해야 한다. 그 결과에서 cache의 실제 hit율, RPC bytes, 전체 wall과 실패·거절·fallback "
        "비용을 평가한다. 여기의 성분 배속은 그 실행의 결론을 대신하지 않는다. `global_error_bound=null`을 유지한다.", ""]
    with (output / "CALLBACK_COMPONENTS_REPORT_KO.md").open("x") as stream:
        stream.write("\n".join(report))
    write(output / "ANALYSIS_RECEIPT.json", {"status": "COMPLETE_SCOPED", "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "analyzer": record(__file__), "source_payload_manifest": record(source / "PAYLOAD_MANIFEST.json"),
        "raw_audit": record(output / "RAW_AUDIT.json"), "report": record(output / "CALLBACK_COMPONENTS_REPORT_KO.md"),
        "callback_reruns": 0, "native_calls": 0, "ode_integrations": 0})
    payload = {path.name: record(path) for path in sorted(output.iterdir()) if path.is_file()}
    write(output / "PAYLOAD_MANIFEST.json", {"files": payload, "payload_count": len(payload),
        "payload_bytes": sum(item["bytes"] for item in payload.values()), "self_included": False})
    print(json.dumps({"status": "PASS_SCOPED", "operations": len(operations), "tasks": len(tasks),
                      "verified_payloads": len(manifest["files"]), "thread_workers_observed": dict(thread_id_counts),
                      "report": str(output / "CALLBACK_COMPONENTS_REPORT_KO.md")}, sort_keys=True))


if __name__ == "__main__":
    main()
