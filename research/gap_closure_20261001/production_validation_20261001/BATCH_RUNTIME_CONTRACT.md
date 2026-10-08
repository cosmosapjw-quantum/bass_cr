# R4V bounded local full-operator batch

`batch_runtime.py` adds a local process supervisor around the unchanged R4U
`precompute_cli.make_manifest`, `validate_manifest`, and `run_manifest` APIs.
It makes no numerical-kernel/provider edit, interpolation, floating reduction,
tolerance change, or MPI launch. Planning makes zero physical calls. The current
user's implementation-and-run continuation authorizes the bounded new work;
exact manifest hashes are content bindings, not signatures or old approvals.

## Fixed work and global budget

The input is an ordered JSON list of finite times (prefer exact Python hexadecimal
floats). Up to 72 unique queries are split into at most four contiguous nonempty
partitions; collection restores the original order. Every query retains the full
unchanged first-passing 11-level ladder and each lane uses the same exact physical
and numerical context. There is no retry, cap transfer, or fallback lane. Output
and plan paths are create-only; failure consumes any created paths.

For the 72-query, four-lane design, each lane owns 18 queries and at most 198 raw
attempts. The **single batch coordinator** preallocates disjoint global reservation
blocks `[1,198]`, `[199,396]`, `[397,594]`, `[595,792]`. Before any subprocess launch,
it durably writes `GLOBAL_RESERVATION_BLOCKS.json`, including exact lane-plan
digests and ranges. R4U then durably reserves each lane's local attempt ID before
the corresponding native call. The global ID is `block_start + local_id - 1`.
The lane file's historical field `global_attempt` means the R4U lane-local ID in
this enclosing batch. Unused IDs are never returned/reissued. Thus the sum of
independent lane caps is bounded by 792, and **no lane receives a copy of 792**.

## CPU, memory, and identity admission

The target local configuration is four serial lanes × two Fortran/OpenMP threads,
with eight distinct admitted CPU IDs. Every lane supervisor explicitly binds to
its own CPU pair before it enters the existing R4U supervisor; native workers
independently recheck and apply that pair. The batch coordinator runs within the
same eight-CPU affinity. Supervisors share those CPUs; no uncounted compute rank
or separate coordinator core is claimed. A physical-core plan also rejects
sibling logical CPUs across lanes. No root-guard override or MPI fallback exists.

At planning and immediately before run, aggregate admission checks the actual
Linux affinity, topology, cgroup quota, current memory estimate, and **sum** of
lane RSS estimates. Reserve is at least 1 GiB or one eighth of currently available
memory; execution preserves the larger frozen reserve. Each R4U worker also
performs its unchanged immediate admission. The default 0.5 GiB per lane gives
about six times the earlier approximately 85 MiB observed child high-water mark;
four lanes therefore request 2 GiB plus the aggregate reserve. This is a declared
engineering estimate including room for wrappers and buffers, **not** an enforced
RSS limit, an allocation guarantee, or simultaneous-peak measurement. Future
operator difficulty/allocations can differ. The conservative R4U cgroup cache
accounting policy is unchanged.

The parent freezes its own source, R4U CLI/resource sources, Python executable,
runtime versions, exact host boot, and exact bytes of every lane plan. Each lane
plan additionally pins every R4U provider/input/native/source identity. Every lane
plan is fully validated before **any** subprocess launch, and all contexts must
match. New source identity never migrates an old checkpoint or cached context.

## Fail-fast cancellation and deadlines

Every owned `_lane` wrapper installs `SIGTERM -> KeyboardInterrupt`, binds its
CPU pair, and calls the existing R4U `run_manifest`. The parent polls at 50 ms.
The first observed nonzero lane exit, launch error, parent interruption, or overall
deadline sends SIGTERM to all still-running owned wrappers. R4U's existing
`supervise` catches that interrupt, kills its physical process group and recorded
admitted workers, waits, and records its failure. No further work is scheduled
after cancellation reaches a wrapper. A call already in flight may have consumed
a durable reservation; it is not retried. Cancellation has a 15-second grace;
after it, fallback cleanup kills only snapshotted descendant identities matching
PID, start time, signal PID, and PID namespace (parent PID may change on orphaning).
Completed lanes and first-failure evidence are retained.

Independent review reproduced a defect in the first implementation: a wrapper
could exit immediately after spawning a new-session child, before the first
descendant snapshot. That pre-run source was rejected and its plan invalidated.
The repaired supervisor enables Linux `PR_SET_CHILD_SUBREAPER` before any launch,
then restores the previous process-local setting after cleanup. Orphaned
grandchildren are adopted by this supervisor even across the immediate exit race.
Existing descendant subtrees are excluded, exact owned identities are retained,
and available R4U supervisor/admission receipts are checked against lane execution
digests and direct wrapper PID/start/namespace ancestry. An unbound receipt
authorizes no signal. Terminal cleanup runs even when no wrapper remains active,
kills any exact live owned descendant, and reaps adopted zombies. A wrapper exit
code of zero with a still-live owned descendant is a batch failure. Recorded live
survivors also explicitly prevent success. Killing the batch owner itself remains
outside this process-local protection; an external scheduler is required for that
separate failure class.

The external overall deadline is at least the per-lane hard deadline plus 30
seconds for launch/admission overhead. Each lane retains its original external
hard watchdog. As with R4U, an OS kill of the supervising process itself is not
an external scheduler lease; surviving scheduler infrastructure is assumed.
The batch reads all available lane admission/results/watchdog/queue receipts,
checks recorded cap usage, and writes a final `BATCH_RESULT.json`. Its success is
only finite-query operational completion. Failed/incomplete outputs cannot be
treated as a completed cache.

## CLI

All output/manifest parents must already exist outside the repository:

```sh
python -I batch_runtime.py plan \
  --inputs /absolute/inputs --build /absolute/build \
  --times-json /absolute/TIMES.json \
  --manifest /absolute/BATCH.json --output /absolute/new_batch \
  --cpus 0,1,2,3,4,5,6,7 --lanes 4 --threads 2 \
  --per-lane-gib 0.5 --max-attempts 792 --timeout-seconds 1800
python -I batch_runtime.py run \
  --manifest /absolute/BATCH.json --execution-sha256 PRINTED_EXACT_BYTE_DIGEST
```

Lane plans are `/absolute/BATCH.json.lane00.json` through `lane03.json`;
outputs are `/absolute/new_batch.lane00` through `.lane03`. Batch aggregation
receipts/logs are in `/absolute/new_batch`. `--logical-cpus` explicitly changes
CPU accounting units; it must not be used to evade the actual quota.

## Evidence and ceilings

Focused tests use mocked planning contexts and real nonphysical sleeping/failed
subprocesses. They check exact-byte tamper rejection, CPU overlap, aggregate CPU
and memory overcommit, cap/range tampering, fresh memory admission, different
contexts/source hashes, create-only paths, real first-failure cancellation of an
existing R4U watchdog and its long child, and an overall timeout. These tests
provide no scientific accuracy or MPI/NCP speedup evidence.

Additional regression tests cover immediate wrapper exit 7, wrapper SIGKILL, and
wrapper exit 0 after spawning an independent-session long child. In all three
cases the batch fails, the child is killed/reaped, no live descendant remains,
and the previous subreaper setting is restored. A mismatched receipt is rejected
without yielding any authorized process identity. The repaired suite has 13
test methods; no physical evaluator or operator call is made.

`production_admission=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture=false`,
and no continuous trajectory error bound remain fixed. Model-routing capability
was unavailable; no inference about another model's judgment was made. NCP64
and MPI physical execution are not claimed by this local batch.
