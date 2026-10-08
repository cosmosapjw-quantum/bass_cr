# Codex handoff: F1-R2 60-worker parallel admission implementation

Role: **BASS_NCLOUD_F1_R2_PARALLEL_IMPLEMENTER**.

이번 세션의 목표는 serial F1 admission의 expensive operator-evaluation phase만 병렬화하는 것이다.
과학 판정 semantics는 기존 F1 implementation을 그대로 재사용한다.

실제 NCP R2 scientific run은 실행하지 않는다.

## 0. Frozen parent evidence

Timeout evidence parent:
`477fef8ede26af74e0cf7a91762ea4ec54ae1527`

Historical timeout run:
- run_id = `20260928T064313Z`
- exit = 124
- wall = 7200 s
- last progress = `engine_loaded`
- scientific status = NOT_REPORTED
- RETURN_REPORT absent
- user observed approximately one active vCPU in htop
- configured server = 64 vCPU / 128 GB

Old executable implementation:
- commit `8236887dd8869de57522d5c87a48972f287969fe`
- tree `d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae`

Do not reinterpret the timeout as scientific FAIL.

## 1. Worktree

Repository:
`cosmosapjw-quantum/bass_cr`

Implementation branch:
`research/fnd-ncloud-f1-r2-parallel-admission-20260928`

Preserve the user's current checkout.

Fetch the branch and create a separate detached worktree from the exact remote branch head.
This R2 implementation session explicitly authorizes:
- one separate worktree;
- commits;
- non-force push to the R2 branch.

It does not authorize a scientific run.

No reset --hard, git clean, automatic stash/rebase/merge, main modification, or force push.

## 2. Read first

In order:

```text
AGENTS.md
docs/READBACK_POLICY.md
research/foundation_rebuild/ncloud_c64g3_20260928/F0_DURABLE_CLOSURE.json
research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1/20260928T064313Z/EVIDENCE_MANIFEST.json
research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1/20260928T064313Z/PROGRESS.jsonl
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_CONTRACT.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_REPRESENTATIVE_QUERIES.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/runtime/native/engine_admission.py
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/runtime/run_f1_engine_admission.py
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_TIMEOUT_ANALYSIS.json
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_CONTRACT.json
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_IMPLEMENTATION_PLAN_KO.md
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_RETURN_CONTRACT.json
```

R2_CONTRACT and F1 scientific contract are frozen. Do not change them to make tests pass.

## 3. New implementation location

Only add code under:

```text
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/runtime_r2/
```

Expected modules:

```text
task_plan.py
worker.py
task_store.py
cache_evaluator.py
resources.py
run_f1_r2_parallel.py

tests/test_task_plan.py
tests/test_worker.py
tests/test_task_store.py
tests/test_cache_evaluator.py
tests/test_resources.py
tests/test_parallel_equivalence.py
tests/test_runner_contract.py
```

Existing F1/TP2D scientific code must remain unchanged.

## 4. TDD

RED first for:

- 165 representative task specs.
- exact sentinel time_hex compatibility with old metric_sentinels formula.
- task identity changes on engine/archive/time/q/h and ignores consumer role.
- out-of-order completion produces deterministic reducer input.
- task-store payload/receipt tamper.
- exact-context resume to fresh output.
- missing cached task hard-fails; no evaluator fallback.
- serial synthetic evaluator vs R2 precompute+cache result equivalence.
- resource worker selection yields 60 on affinity=64.
- affinity <64 blocks the intended 64-vCPU R2 contract.
- total memory below contract gate blocks.
- worker environment has BLAS/OpenMP threads=1.
- timeout/KeyboardInterrupt leaves reusable persisted tasks and a partial summary.
- old authorization tied to 8236887... cannot authorize R2.
- output collision fails closed.

Import/setup errors are not accepted as RED.

## 5. Parallel task planner

Representative:
15 exact times × 11 frozen resolutions = 165 specs.

Metric:
derive exactly the same five sentinel z values and center±epsilon times as old F1.
Generate all 11 frozen resolutions for each exact metric time.

Deduplicate exact numerical task identity across all consumers.

Maximum before dedup = 330.

Task identity:

```text
engine_identity_sha256
archive_sha256
time_hex
order
subdivisions
sector=full
```

Do not include representative/sentinel role.

## 6. Worker pool

Use spawn ProcessPoolExecutor.

Host contract:
64 visible affinity CPUs, 128 GB configured memory.

Worker count:
`min(60, affinity_count - 4, remaining_tasks)`.

For the approved server this should be 60.
If affinity is less than 64, do not silently treat the host as equivalent.

Before spawning:
- OMP_NUM_THREADS=1
- OPENBLAS_NUM_THREADS=1
- MKL_NUM_THREADS=1
- NUMEXPR_NUM_THREADS=1
- OMP_DYNAMIC=FALSE
- MKL_DYNAMIC=FALSE

Each worker initializer loads exact basis/native engine/evaluator once.
Each worker then processes multiple exact tasks.

Workers do not write the durable task store.
Parent is the sole writer.

## 7. Durable task store

Parent persists each successful result immediately:

```text
operator_tasks/<task_id>.npz
operator_tasks/<task_id>.json
```

Use create-only/atomic behavior and fsync semantics.
Receipt pins payload SHA, exact context and array metadata.

A future resume uses a fresh output directory and imports only exact hash-valid matching-context tasks.
No threshold/policy migration.

## 8. Cache-only reducer

After task-store completeness:

- build a read-only cached evaluator;
- cached evaluator computes exact time_hex/q/h task ID;
- cached evaluator MUST NOT call native assembly on cache miss;
- invoke the existing pinned F1 `run_admission()`.

Thus the original:
- first-qualified resolution semantics,
- historical raw-attempt checks,
- selected S/H/D parity,
- metric residual,
- failure statuses
remain unchanged.

Normalize output only for deterministic tests; do not change public science JSON semantics without a contract.

## 9. Resource/progress evidence

Record at minimum:
- affinity count
- configured/observed memory
- workers selected
- task plan count
- deduplicated count
- restored
- submitted
- running
- completed
- persisted
- failed
- parent RSS
- MemAvailable
- elapsed

Emit progress every 10 task completions and phase boundaries.

Timeout/interrupt must still produce:
- PARTIAL_TASK_SUMMARY.json
- valid persisted task cache
- RETURN_REPORT.json

The old behavior of losing the science report after external hard timeout must not repeat.

## 10. Authorization firewall

R2 implementation requires a NEW authorization schema:
`BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1`.

It must pin exact later R2 implementation commit/tree.

The old active authorization for
`8236887... / d114060...`
must be rejected.

This implementation session MUST NOT create an active R2 authorization.

## 11. Tests

Run only R2-new tests.

Do not rerun:
- TP2D 18 tests
- TP2E 32 tests
- old F1 48 tests

Required:
- failures/errors/skips = 0
- py_compile PASS
- CLI --help PASS
- serial/parallel synthetic equivalence PASS
- resume/tamper/failure-injection PASS
- source manifest closed
- secret scan
- existing scientific source modified 0

No actual native BASS R2 science execution.

## 12. Commit/push

Use bounded commits such as:

```text
test(f1-r2): add exact parallel orchestration contracts
feat(f1-r2): add durable parallel operator precompute
feat(f1-r2): reuse frozen admission reducer from cache
test(f1-r2): close resume and resource failure cases
docs(f1-r2): close implementation handoff
```

Push non-force to:
`research/fnd-ncloud-f1-r2-parallel-admission-20260928`.

Remote verify:
- ref SHA
- tree SHA
- parent descendant
- changed paths limited to R2 sidecar
- no historical scientific source modifications.

## 13. Stop

Allowed final statuses:

```text
F1_R2_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN
F1_R2_IMPLEMENTATION_BLOCKED
```

Do not claim F1_ENGINE_ADMISSION_PASS.

Do not create RUN_AUTHORIZATION.
Do not execute R2 science.
Do not start F2/F3.

Claim ceiling remains unchanged.
