# Fresh full-operator execution contract

`precompute_cli.py` connects the exact pinned physical provider to the existing R4S whole-query queue. It provides planning and execution, including serial operation when MPI launch admission is unavailable. Planning loads no native library and makes no operator call. The execution SHA256 identifies the **exact bytes of a new manifest**; it is not a signature, a user-approval hash, or reuse of an archived approval. The current user's bounded implementation/acceptance request supplies the task authority. The manifest makes that run concrete and reviewable.

## Planning and consuming one run

Use an existing parent directory outside the repository for both manifest and output. `TIMES.json` is an ordered JSON list of finite numbers or exact Python hexadecimal float strings. The contract defaults to the unchanged `SCIENCE_CONTEXT.json` → `context.contract`; `--contract FILE` accepts only an exact copy of that archived contract in this pinned B0 adapter. A changed physical or numerical contract requires a separate adapter. A two-step solver query plan can supply its already computed unique endpoint/midpoint times without recomputation, rounding or interpolation.

```sh
python -I precompute_cli.py plan \
  --inputs /absolute/runtime_inputs --build /absolute/native_build \
  --times-json /absolute/TIMES.json --manifest /absolute/EXECUTION.json \
  --output /absolute/new_execution --backend fortran \
  --ranks 1 --threads 2 --cpus 0,1 --per-rank-gib 1 \
  --max-attempts 44 --timeout-seconds 900
python -I precompute_cli.py run \
  --manifest /absolute/EXECUTION.json --execution-sha256 PRINTED_BYTE_SHA256
```

Every plan freezes a new execution UUID, exact operator context and source/native/input hashes, ordered query IDs and complete ladders, global raw-attempt cap, hard and queue wall budgets, selected CPU IDs, rank/thread counts, memory estimate/reserve, environment, Python executable and Python/platform/NumPy/SciPy versions, host boot identity, and (for MPI) OpenMPI launcher binary/version. Each MPI rank, including coordinator zero, consumes its own CPU and memory allocation. Physical-core mode requires distinct selected cores; `--logical-cpus` makes logical-CPU accounting explicit. Memory remains an estimate, with the larger frozen reserve required at admission; it is not an OS RSS limit.

`run` rejects changed identities and atomically claims a new output directory before starting any worker. A failure consumes that output path; there is no resume, retry, automatic cap extension, or overwrite. A new execution needs a newly planned output/manifest. The supervisor retains the original manifest digest in receipts and separately checks the copied manifest's exact byte digest on worker entry.

## Admission and numerical behavior

An external supervisor starts a separate worker process group and enforces the manifest's hard deadline with `SIGKILL`. Ordinary queue failures also stop publication and preserve the queue's first-failure/reservation evidence. Each rank verifies that it descends from the live, identity-matched watchdog and that the hard deadline remains valid. On timeout or a nonzero worker exit, the watchdog kills the group and any admitted rank recorded under its exact PID, start time and PID namespace. This handles MPI ranks with separate process groups. Linux procfs may expose ancestor-namespace PIDs: the implementation distinguishes procfs PID from signal PID rather than assuming `os.getpid()` is a valid procfs path. As with an ordinary external timeout utility, this assumes the supervising OS process remains alive; it is not an external cluster scheduler lease.

All ranks verify the fresh source/context, communicator size, environment, current quota/topology/memory, and explicitly apply `bind_rank`. They then gather every admission status. Root durably writes `ADMISSION.json` and broadcasts success before the queue starts. Only a dispatched task lazily constructs `PinnedEvaluator`, after this common decision. An admission failure creates no native evaluator. The queue's generic `physical_admission: false` remains unchanged: generic scheduling grants no physical authority; the enclosing fresh execution/admission records supply the run-specific contract.

MPI uses the exact selected OpenMPI launcher, `--nooversubscribe`, and `--bind-to none` because the application applies and verifies the exact OS affinity of **every rank** before native load. The CLI supplies no root-allow override and has no launcher fallback. A blocked MPI launcher remains blocked. No MPI launch was attempted in CLI development validation; the available serial path does not establish MPI acceptance or 64-core NCP scaling.

The unchanged `qualified_task` runs each query's full first-passing resolution ladder. Root's durable global reservation precedes every raw operator call; workers do not copy the attempt cap. The queue returns results in plan order and uses no floating-point MPI reduction. Qualified final pairs are revalidated and copied into a create-only `cache/`. There is no interpolation, altered tolerance, altered quadrature, propagation, or capture calculation in this CLI.

## Evidence and claim limits

Outputs include the execution manifest, supervisor command/deadline, stdout/stderr, all-rank admission, queue plan/reservations/first failure/receipt, per-task attempt payloads and qualified pairs, the collected cache, and final success/failure receipts. A hard kill may leave a consumed reservation with no completed attempt payload; it must not be silently retried. A cache directory left incomplete is not a completed cache. `SUPERVISOR_RESULT.json` reports wall time, return code, user/system child CPU seconds, minor/major page faults, and Linux `RUSAGE_CHILDREN` maximum RSS in KiB. RSS is the supervisor lifetime's maximum waited-child high-water mark, **not the simultaneous sum of MPI rank peaks**. CPU/fault values are deltas across the supervised launch.

All receipts retain `capture: false` and `production_admission: HOLD`; the manifest also retains `all_bound: OPEN`, `b_grid: NO_GO` and no continuous trajectory bound. A successful cache proves only completion of the bound finite query qualification run. Historical capture states, continuous bounds, CF4/temporal acceptance, and production claims require their separate contracts.

Focused TDD began with a missing-module failure before implementation. Synthetic tests then exposed the host/namespace procfs PID mismatch, which was fixed and covered by a real supervised read-only subprocess. Tests exercise exact manifest byte binding, resource overcommit/CPU substitution, a real hard timeout, all-rank fail-closed admission, lazy evaluator sequencing with mocks, source-change rejection before binding, watchdog ancestry, and create-only output reuse. They construct no physical evaluator, launch no MPI job, and provide no physical accuracy or speedup evidence.

Validation: `python -m unittest discover -s research/gap_closure_20261001/production_solver_20261001/provider -p test_precompute_cli.py` with OMP/OpenBLAS/MKL/NumExpr each set to one: **8 tests passed, 0 skipped**. Isolated `python -I .../precompute_cli.py --help` also passed. These are implementation tests only.

Cgroup memory admission uses the minimum of host `MemAvailable`, all finite ancestor limits, and each cap's current headroom plus a conservative clean-file allowance. For a verified leaf cgroup only, allowance is half of `max(0, min(current, file, active_file + inactive_file) - file_mapped - file_dirty - file_writeback - shmem - unevictable - max(memory.min, memory.low))`. Overlapping exclusions deliberately reduce the estimate. Anonymous, swap and slab memory receive no credit; unknown counters or descendants disable credit. Two cache observations and bracketing usage reads retain the smaller credit and larger usage. Raw headroom, counters and admitted credit are recorded separately. This does not modify cgroups, force reclaim, relax the CPU quota, or reduce the existing memory reserve. It remains a launch-time estimate rather than an allocation guarantee. Counter meanings follow the [Linux cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-interface-files); the [procfs documentation](https://docs.kernel.org/filesystems/proc.html#meminfo) explains why available memory can include reclaimable cache. The one-half allowance is this project's conservative policy, not a kernel-specified cgroup MemAvailable formula.
