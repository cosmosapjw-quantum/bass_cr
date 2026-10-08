# F1-R2 parallel admission implementation plan

## Goal

Preserve every F1 scientific definition while replacing the serial expensive operator-evaluation
orchestration with a 60-process exact-task precompute on the existing 64-vCPU / 128-GB NCP host.

The previous F1 run is classified as:
`ORCHESTRATION_SERIALISM_NOT_SCIENTIFIC_FAILURE`.

No threshold, representative point, resolution ladder, metric sentinel, native source, basis,
or historical evidence is changed.

## Architecture

The existing F1 reducer remains authoritative:

- `engine_admission.admit_query`
- `engine_admission.metric_sentinels`

R2 does not rewrite their scientific logic. Instead it precomputes all exact
`(time_hex, order, subdivisions)` operator evaluations in a process pool, persists them,
and supplies a read-only cache evaluator to the unchanged reducer.

Pipeline:

```text
identity / authorization firewall
        ↓
engine build + exact basis
        ↓
exact R2 task plan
        ↓
spawn process pool (60 workers on 64-vCPU host)
        ↓
parent-only durable task store
        ↓
cache-only evaluator
        ↓
existing F1 admission reducer
        ↓
same parity / metric gates
```

## Task 1 — exact task planner

Proposed:
`runtime_r2/task_plan.py`

Representative tasks:
15 queries × 11 frozen resolutions = 165 task specifications.

Metric tasks:
derive the same 5 z sentinels and centered ±epsilon times used by the old
`metric_sentinels`. Precompute the full 11-resolution ladder for those 15 exact times.
This is at most 165 additional specifications.

Deduplicate by exact scientific task identity:

```text
engine_identity_sha256
historical_archive_sha256
time_hex
order
subdivisions
sector=full
```

Roles such as representative/sentinel must not enter the numerical identity.

No rounded/fuzzy/nearest time reuse.

Tests:
- exact representative count 165.
- metric-time hexadecimal identity matches old formula bit-for-bit.
- task deduplication preserves all consumer references.
- randomized input ordering produces identical ordered task plan.
- changed engine/archive/time/q/h changes task ID.
- role label does not change task ID.

## Task 2 — process worker

Proposed:
`runtime_r2/worker.py`

Use `multiprocessing.get_context("spawn")` / `ProcessPoolExecutor`.

Initializer per process:
- set/verify BLAS/OpenMP threads = 1;
- load exact basis once;
- load exact new engine once;
- construct trajectory/channels/evaluator once.

Each worker handles multiple tasks during its lifetime.

Task:
`(time_hex, order, subdivisions)` → raw/full arrays + lightweight diagnostics.

No worker writes scientific task-store files.
Only the parent writes, so concurrent filesystem races cannot redefine completion.

Tests:
- initializer occurs once per process in a synthetic seam.
- task time uses `float.fromhex(time_hex)`.
- exceptions return typed failure and cannot become PASS.
- nonfinite output rejected.
- worker result is serializable.
- thread environment is 1 before native evaluator initialization.

## Task 3 — durable task store

Proposed:
`runtime_r2/task_store.py`

For each completed exact task, parent writes:

```text
operator_tasks/<task_id>.npz
operator_tasks/<task_id>.json
```

Receipt contains:
- exact task identity/context;
- payload SHA-256;
- selected engine/archive identities;
- array shapes/dtypes;
- completion timestamp/order only as operational metadata.

Completion means **persisted + fsync + receipt written**, not just future returned.

Restore:
- only exact same R2 context.
- payload SHA and identity must match.
- copy/import into a fresh output directory.
- never mutate an old run directory.
- no restoration from scientific-failure outputs with changed contract.

Tests:
- payload tamper.
- JSON tamper.
- context drift.
- missing pair member.
- interrupted partial task ignored or rejected.
- fresh-output resume reuses valid tasks and recomputes only missing tasks.

## Task 4 — cached evaluator and unchanged reducer

Proposed:
`runtime_r2/cache_evaluator.py`

API:
`evaluator(t, q, h) -> (raw, full)`

It computes the exact `float(t).hex()` task identity and reads the task store.

If the task does not exist:
`R2_CACHE_MISS_NO_FALLBACK`.

It must never call native assembly itself.

Then invoke the old, pinned:

```python
run_admission(evidence, cached_evaluator, speed, F1_contract, engine_identity, ...)
```

This guarantees that:
- selection logic is inherited;
- historical attempt checks are inherited;
- raw/full parity thresholds are inherited;
- metric sentinel residual logic is inherited.

Tests:
- serial synthetic evaluator and precomputed-cache reducer produce byte-equivalent normalized result.
- out-of-order worker completion cannot change reducer output.
- missing one task causes hard cache miss rather than compute fallback.
- parity failure/status from old reducer is preserved exactly.

## Task 5 — resource admission

Proposed:
`runtime_r2/resources.py`

Known host contract:
- configured vCPU = 64
- configured memory = 128 GB

Runtime require:
- `len(os.sched_getaffinity(0)) >= 64`
- total memory >= 120,000,000,000 bytes
- selected worker count:
  `min(60, affinity_count - 4, remaining_tasks)`

Do not spawn 64 workers. Reserve 4 vCPUs for parent, kernel and I/O.

Capture:
- affinity count
- `/proc/meminfo` MemTotal/MemAvailable
- worker count
- parent RSS
- periodic MemAvailable
- completed/in-flight task counts

If memory becomes critically low, stop scheduling new tasks and fail closed.
Do not silently reduce precision or contract.

## Task 6 — R2 runner

Proposed:
`runtime_r2/run_f1_r2_parallel.py`

Stages:
1. authorization and exact implementation identity
2. F0 durable evidence
3. historical timeout evidence
4. source/contract/archive/basis
5. R2-new tests
6. engine build
7. task plan
8. valid resume import if explicitly requested
9. parallel precompute
10. cache completeness gate
11. unchanged admission reducer
12. result packaging

Progress must include:
- plan task count
- restored count
- submitted/running/completed/persisted/failed counts
- every 10 completions
- elapsed
- worker count
- MemAvailable

On timeout/interrupt:
- persist `PARTIAL_TASK_SUMMARY.json`
- persist valid task receipts already completed
- create `RETURN_REPORT.json`
- never lose all progress as the old hard timeout did.

## Task 7 — authorization firewall

R2 is a new executable implementation identity.

The old authorization tied to
`8236887... / d114060...`
MUST NOT authorize R2.

R2 runner requires a new external:
`BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1`

with exact R2 implementation commit/tree, positive wall budget and cost/prepaid gate.

Implementation session does not create an active authorization.

## Task 8 — focused validation

Only R2-new tests.

Do not rerun:
- TP2D 18 tests
- TP2E 32 tests
- old F1 48 tests

Their source semantics are pinned and unchanged.

R2 tests must cover:
- task planner
- worker seam
- task store
- resume
- serial-vs-parallel reducer equivalence
- resource selection
- authorization firewall
- timeout/interrupt partial evidence
- create-only output collision
- CLI --help

Implementation completion:
- R2-new tests failures/errors/skips = 0
- py_compile PASS
- CLI --help PASS
- existing scientific source modified = 0
- no scientific R2 run
- source manifest closed
- non-force push and R1 ref/tree verification

Allowed implementation statuses:
- `F1_R2_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN`
- `F1_R2_IMPLEMENTATION_BLOCKED`

Do not claim `F1_ENGINE_ADMISSION_PASS`.

## Execution expectation

The previous run paid for 64 vCPUs but used one expensive Python process.
R2 is designed to keep up to 60 independent native evaluations in flight.

No wall-time promise is made until measured.
The expected improvement is an orchestration speedup, not a change in numerical method.

After implementation closure, a **new owner run authorization** is required before execution.

## Claim ceiling

Unchanged:

```text
capture=false
production=HOLD
all_bound=OPEN
b_grid=NO_GO
original_capture_gap_resolved=false
continuous_global_supremum_bound=false
```
