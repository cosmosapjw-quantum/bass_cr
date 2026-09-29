# Codex handoff — N1536 successor with adaptive worker scaling

Role: `N1536_SUCCESSOR_PREPARATION_ADAPTIVE_WORKERS`.

Repository: `cosmosapjw-quantum/bass_cr`

This is a **non-native implementation/review handoff**. Do not start native parity,
pilot, missing-query fill, cache-only replay, N1536 propagation, N3072, capture,
all-bound, or b-grid during this preparation step.

## Fixed predecessor and research inputs

Completed N768 execution:
- commit `11100b35f78ec26100ea732971bb4ce0f9925719`
- tree `05976e386c0a39591247d69c32c8cb28fa3f2a97`
- authorization `R4F-N768-MIGRATION-REPAIR-20260929-A2`
- completed return SHA256 `dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3`

R4G research parent:
- commit `33a8982ac0578df35361474b6aa7a43afb2ae144`

Adaptive worker implementation branch:
- `impl/r4g-adaptive-workers-20260929`

Read first:
- `AGENTS.md`
- `research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/R4G_RESEARCH_AND_HANDOFF_KO.md`
- `.../ADAPTIVE_WORKER_POLICY.json`
- `.../adaptive_workers.py`
- `.../tests/test_adaptive_workers.py`

The exact N768 execution commit remains immutable. Do not back-port or amend it.

## Scientific scope remains unchanged

N1536 is one fresh full-window propagation with the same physics, basis, reference,
frame, thresholds and ordered operator-qualification ladder. It is not 1536 steps
appended to the N768 final state.

Exact temporal arithmetic remains:

```python
dt = (tf - t0) / 1536
for j in range(1536):
    ta = t0 + j * dt
    tb = ta + dt
    tm = 0.5 * (ta + tb)
    width = tb - ta
```

Do not replace this with `linspace` or `t0 + (j + 0.5) * dt`.

R4G query contract:
- active required queries = 1538
- inherited exact hits = 2
- new midpoint IDs = 1536
- eventual union store = 3583
- active query cap remains 2048

## Adaptive worker policy

The previous N768 migration intentionally capped the first production parallel run at
8 single-thread workers. That cap was a validation/safety envelope, not a physical or
NCP hardware limit.

For the N1536 successor, support worker scaling stages:

`8 -> 16 -> 32`

Hard maximum for this preparation is **32 workers**. Do not add or authorize a
64-worker stage.

Every worker remains single-threaded internally:

```text
OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
```

Per-worker RAM planning value remains 1 GiB unless a later exact authorization changes
it. The 32-worker stage therefore requires an approved worker-RAM envelope of at least
32 GiB plus independent confirmation that the shared host has sufficient free memory.

Never infer that the 64-vCPU host grants 32 CPUs to this run. Read the live affinity,
other active BASS jobs and memory before admitting the stage.

### Useful scaling pilot

Use `adaptive_workers.build_useful_pilot_plan` to allocate **disjoint scientific
missing queries**, not benchmark-only duplicates:

- 8-worker stage: 8 useful queries
- 16-worker stage: 16 useful queries
- 32-worker stage: 32 useful queries

Total useful pilot work = 56 queries. All successful pilot query pairs are committed to
the canonical cache and count toward the 1536 missing midpoint queries. After all three
pilot stages, 1480 missing midpoint queries remain.

Pilot IDs must be selected deterministically and stratified across the then-remaining
query-ID order, without replacement. Do not use the first 56 consecutive times and do
not randomize.

For every stage record at minimum:
- workers
- exact CPU scope / affinity
- useful query IDs
- completed and failed queries
- wall seconds for the stage including pool startup/shutdown
- queries/second
- speedup versus the first healthy stage
- parallel efficiency versus the first healthy stage
- peak worker/coordinator RSS when available
- raw attempts consumed
- filesystem/publish failures or contention evidence

Use `summarize_scaling` for the derived metrics.

The scheduling rule is deterministic:
- discard any stage with a failed query or resource-scope violation;
- among healthy stages choose the stage with maximum measured queries/second;
- exact throughput tie -> choose fewer workers;
- this selection does **not** enlarge the approved CPU/RAM/raw/wall/cost scope.

If a higher stage fails, preserve its failure and fall back only to the best lower
healthy stage inside the same pre-authorized envelope. If no stage is healthy, STOP.
Do not create a new nonce or silently alter the worker plan.

### Remaining fill

After the useful pilot, dispatch only the still-missing IDs with the selected worker
count. No successful query may be recomputed merely to benchmark another worker count.

A stage transition may create a new process pool, but all native workers must use the
same frozen source/library/BUILD identities and the same ordered resolution ladder.

## Budget semantics

Adaptive scaling does not increase the scientific missing-query count.
The deterministic useful raw upper bound remains:

`1536 * 11 = 16896`

If a new two-query parity check is explicitly required and authorized, add at most 22:

`incremental max = 16918`

The 56 useful pilot queries are already included in the 1536 and are not additional
raw/query budget.

Historical N768 lifetime raw usage 2528 remains history only. Do not reset or merge the
old authorization cap into the new rung silently.

## Implementation requirements

Implement the N1536 successor as a new path/entrypoint rather than weakening the frozen
N768 runner. Reuse stable worker/provider/supervisor primitives where possible.

The new admission must accept an exact worker-stage plan and hard cap, and must reject:
- non-increasing or duplicate stages;
- stages above 32;
- CPU scopes smaller than the maximum stage;
- duplicate/negative CPU IDs;
- worker RAM envelopes smaller than max_workers * per_worker_ram;
- an unavailable live affinity;
- any attempt to enable internal BLAS/OpenMP threading >1.

Persist the worker policy and actual selected stage in the execution admission and
return receipts.

The existing helper tests currently cover:
- 8/16/32 default useful plan;
- unique/disjoint 56-query pilot with 1480 remainder;
- deterministic stratified domain coverage;
- custom stage sizes;
- hard cap and monotonic-stage validation;
- CPU/RAM scope checks;
- observed scaling metrics;
- fastest healthy-stage selection and failed-stage exclusion.

Integrate these checks into the real successor runner and add focused tests for the
launcher -> parser -> admission -> stage planner -> bounded pool boundary with native
calls trapped.

No native science is required to close this implementation task.

## N1536 replay and gate

Only after future native authorization and 1538/1538 verified active coverage:
- replay unchanged `run_candidate(..., 1536)` from the original initial state;
- strict cache-only reader;
- native operator calls during replay = 0;
- cache miss is fatal.

Gate:
- `d1536_ref <= 1e-6`
- `d768_1536 <= 1e-6`
- previous/current/reference norm screens
- all required operator queries qualified

Do not copy the N768 `dual PASS => inconsistency` guard. Dual PASS is valid at N1536.

Preserve expensive candidate/state/metrics before final gate classification so an
UNRESOLVED scientific result is not lost.

## Verification before handoff

Run, without native operator calls:
1. adaptive policy unit tests;
2. N1536 exact query-plan tests;
3. successful A2 predecessor validation;
4. active 1538 vs union 3583 distinction;
5. 8/16/32 stage partition and resource-bound tests;
6. bounded-pool failure/cancellation tests;
7. cache-only miss zero-evaluator tests;
8. launcher/parser integration smoke with native traps;
9. backward-compatibility checks for the immutable N768 evidence path.

Report exact commands and counts. Do not call synthetic tests native parity or N1536
science evidence.

## Delivery

Create a fresh exact implementation commit/tree and non-force push it. Do not merge.
Create-only back up the implementation/test/handoff package to the existing Google
Drive and Dropbox destinations under the project selective-readback policy.

Generate the later native authorization template mechanically from verified manifests.
Do not hand-type hashes.

The preparation task must stop at:

`N1536_ADAPTIVE_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING`

The later authorization should expose, at minimum:
- exact execution commit/tree
- exact predecessor ZIP/source pins/query-plan hash
- worker stages `[8,16,32]`
- hard max workers `32`
- exact approved CPU list covering up to 32 workers
- per-worker RAM and total worker-RAM cap
- useful pilot plan hash
- incremental raw-attempt cap
- wall/deadline and cost scope
- optional parity scope if needed

No automatic N3072, retry/new nonce, threshold relaxation, reference rerun,
capture/all-bound/b-grid, shared-VM resize/stop or other-session mutation.

Claim ceilings remain unchanged:
`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`,
`original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`,
`continuous_trajectory_error_bound=false`.
