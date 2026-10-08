# R4Y staged central spatial diagnostic

`runner.py` operates only on the separately identified R4X candidate at the
fixed central geometry: z=0, b=2 a0, energy100 keV/u, 18 channels, same-center
order20. It preserves FP64, the original analytic moments and per-entry native
accumulation order, full sector, batch1024, and unmodified raw S/H/D. The new
optional `phase_pairs` rule changes quadrature panels only under an explicitly
declared task. It does not change or promote the radial bank.

All commands require this environment **before Python/NumPy import**:

```bash
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=2 OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 OMP_PROC_BIND=FALSE python PATH/runner.py ...
```

1. `init --inputs recovered_r4u/runtime_inputs --candidate runs_r4x/candidate_v1
   --build recovered_r4u/native_build_portable
   --radial-manifest runs_r4x/native_v1/NATIVE_BUILD.json
   --contract PATH/TASK_CONTRACT.json --out runs_r4y/central_v1 --workers 3`
   freezes original inputs, the exact R4X candidate, native libraries/build
   records, current numerical sources, caller contract, resource allocation and
   the global24-attempt cap. This performs no native load or physical evaluation.
2. Write an explicit plan with only the `tasks` key. Each task has `order`,
   `subdivisions`, `moment_backend` (`reference`/`fortran`), `radial_backend`
   (`python`/`fortran`) and optional `inner_phase_budget` (default null).
3. `prepare --out ROOT --context-sha256 HASH --plan PLAN.json --batch NAME`
   stores a create-only manifest; no physical calls occur.
4. `run --out ROOT --context-sha256 HASH --batch NAME --manifest-sha256 HASH`
   explicitly executes that exact batch. The caller reviews each stage before
   declaring/preparing the next one; there is no automatic continuation or retry.

Example first plan:

```json
{"tasks":[
  {"order":40,"subdivisions":1,"moment_backend":"reference","radial_backend":"python"},
  {"order":40,"subdivisions":1,"moment_backend":"fortran","radial_backend":"fortran"}
]}
```

The original rule permits exactly
`(32,1),(40,1),(48,1),(56,1),(64,1),(48,2),(56,2),(64,2),(48,4),(56,4),(64,4)`.
An explicitly separate inner-phase rule permits budgets24/12/6 at subdivisions1,
with orders32/40/48/56/64. The callback is
`partial(phase_pairs.phase_pairs, phase_budget=beta)`; the unchanged cross
operator receives `phase_budget=None` and the explicit `pair_rule` callback.
Task identity includes this numerical-rule choice; omitted/null budgets have
identical semantic identity. Repeated tasks across batches are forbidden.

One coordinator has a dedicated CPU. At most three workers each have disjoint
two-CPU affinity sets, totalling7 admitted CPUs. BLAS is single-threaded; radial
Fortran uses one OpenMP thread and reports the observed team size at every call.
The native moment wrapper restores its configured2 threads at each call and
records real/fallback call counts. The unchanged moment ABI does not expose the
actual team size; receipts therefore explicitly do **not** claim an observed
moment team. The C++ reference moment kernel is serial. Memory admission reserves
at least1 GiB plus a0.5 GiB coordinator estimate and1 GiB per worker; this is an
estimate, not enforced RSS. The runtime is local process parallelism, with no MPI
or NCP64 scaling claim.

A context-wide exclusive lock prevents concurrent batches from sharing the
24-attempt budget. Before each launch, an atomic create-only global reservation
is committed. Process-creation failure consumes its reservation and closes its
log. Failure, timeout or coordinator SIGTERM cancels and reaps owned peer process
groups. No numerical worker launches subprocess descendants. Forced SIGKILL of
the coordinator cannot be converted into a Python cleanup guarantee; a started
batch cannot be restarted in place and consumed reservations remain counted.

Each worker stores raw arrays before full assembly, then full arrays and source,
input, native identity, timing, RSS, affinity, call-count and screen evidence.
The independent central control observes `abs(D_tp[i,i]) <= 1e-12` for identical
real s indices0/1/2; it never projects or replaces raw D.

The batch summary imports the original qualifier's exact six-block metric:
`max ||A-B||_F/max(||A||_F,||B||_F,1e-300)`, threshold1e-9, full Hermiticity1e-11
and metric ratio1e-8. All batch pair observations are retained; selection of
successive resolution pairs and an independent subdivision comparison belongs
to the frozen research contract and its result analysis. Observed agreement is
not a certified error bound or a whole-trajectory derivative test. G02 remains
UNRESOLVED and production remains HOLD in these worker/batch receipts.

`test_runner.py` contains12 synthetic tests: exact task domain/semantic identity,
CPU/RAM admission, duplicate JSON and create-only writes, the original six-block
metric, the exact-zero control without projection, transparent wrappers, durable
ledger continuity, Popen failure, failed-worker peer cleanup, timeout cleanup,
cross-batch retry rejection, and global24-attempt exhaustion. They make no
archived physical operator calls.
