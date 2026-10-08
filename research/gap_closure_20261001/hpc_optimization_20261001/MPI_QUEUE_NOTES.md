# R4S OpenMPI task queue

`mpi_queue.py` is a new, additive scheduler. It does not edit, supersede or launch
the frozen G02/G03 executors. It has no B0 basis or native-kernel import. Its CLI
requires `--self-test` and performs bounded integer-only synthetic work.

## Public contract

All ranks in a dedicated communicator call:

```python
run_queue(comm, tasks, worker, max_attempts=cap,
          output_dir=fresh_output, timeout_seconds=300)
```

Only rank zero supplies `tasks` and receives an index-ordered result list. Other
ranks pass `None`. A task is finite JSON data containing a nonempty `levels`
list. `worker(task, reserve)` must call `reserve(0)`, `reserve(1)`, etc. **before**
the corresponding raw evaluation. Root accepts only an exact prefix, preserves
the whole ladder on one worker and allows an early successful prefix. Scientific
first-passing-pair qualification remains the worker/provider's responsibility.

The root alone holds the attempt cap. Workers never allocate a full cap of their
own. With an output directory the successful reservation reply follows an
append, flush and fsync. Failed or interrupted reserved attempts remain consumed;
there is no refund or automatic retry. `max_attempts=0` is useful for an empty
plan and rejects any actual reservation. An invalid next level fails the run.

The optional output directory must be new and its parent must exist. Each task
gets a private `reserve.task_dir`. A worker can put bulk payloads there and
return a finite JSON record with the relative path/hash. Only root publishes
canonical result records. Callback writes outside its assigned directory are
outside this API's contract; this is a cooperative scheduler, not an OS sandbox.

For communicator size greater than one, rank zero coordinates and `size-1`
ranks compute. Size one uses the same budget/order contract sequentially. An
N-rank queue therefore must not be represented as N compute workers in a host
resource proposal.

## Ordering, failure and memory

Completion may arrive out of order, but publication advances only over the
complete frozen-plan prefix. Active plus unpublished completed tasks never
exceed the number of workers. This bounds the reorder buffer without forcing
all tasks into memory; large payloads should remain in private task files.

No floating-point MPI reduction is used. The scheduler never distributes
levels within a task and never sums scientific results. Numerical output order
is stable; operational reservation order and task/rank assignment are allowed
to differ between schedules. Do not include operational token order in a claim
of bitwise-identical scientific payloads.

The first observed cooperative failure is recorded once. Root stops dispatch,
refuses every further reservation, drains already granted work, and sends stop
to each idle worker. Every rank receives the same terminal failure. Already
published canonical prefix files and task-local evidence are retained. A dead
rank, stuck callback or protocol failure cannot be cooperatively drained;
root records the failure and invokes nonzero `MPI.Abort` on timeout/protocol
failure. Unexpected MPI/I/O errors also abort rather than enter a collective
that may never finish. Size-one timeout checks are cooperative; a hung
size-one callback needs the external process supervisor.

This is not a restart protocol. An interrupted run's directory is immutable;
future recovery must inspect reserved attempts and exact task/native identity
under a fresh execution contract. A timeout limit is an operational watchdog,
not physical-run authorization or a cost-accounting proof.

## Integration boundary with the current project

The existing `r4f_parallel_migration_20260929/parallel_bridge.py` already provides
`PlannedQuery`, `validate_pair`, `publish_pair` and a shared `GlobalBudget` using
`flock`. `worker_runtime.compute_query` runs one complete ordered
`ResolutionQualifiedProvider` ladder per query. These semantic contracts remain
the physical integration reference. The new queue's root reservation service
replaces distributed access to that ledger for an MPI adapter; it must not be
layered as an additional independent allowance.

Current G02 is fixed at 66 new queries, cap 726, at most 8 single-thread workers;
G03 is fixed at two new queries, cap 22, at most 2 single-thread workers. Source
closure, C++ source/library identity, fresh authorization, actual CPU/RAM census,
create-only output and scientific claim ceilings are enforced separately.
Those limits have not been changed. Neither old approval nor a synthetic PASS
authorizes Fortran substitution or a 64-worker physical launch.

A future physical MPI/Fortran adapter needs a distinct exact source/native
identity and fresh approved query/resource proposal, while retaining the
existing scientific screen tolerances and first-passing resolution rule. It
must verify plan context, time-hex query IDs, basis and native hashes before
loading the library, validate worker pairs before root publication, bind each
rank to its allocated disjoint CPU set and account for rank-zero coordination.
Fortran `accumulate(...)` can enter through the existing kernel-object seam in
`exact_cross.cross`; it cannot masquerade as the frozen C++ library.

Query parallelism alone cannot occupy 64 cores for a two-query G03 workload.
OpenMP/SIMD inside a separately validated kernel is needed there. Parallelizing
independent channel pairs preserves each output's serial quadrature-node
accumulation order; parallelizing the node reduction changes that order and
requires its own accuracy analysis. The MPI queue makes no kernel-speed claim.

## Fresh validation

The initial targeted test failed because `mpi_queue` did not yet exist. After
implementation, the synthetic suite passed with OpenMPI 5.0.11 and mpi4py:

```bash
python -m unittest test_mpi_queue -v
```

The original six tests covered four serial contract tests and two real-MPI integration tests.
The latter execute seven bounded OpenMPI subprocesses: ordered 17-task plans at
1, 2 and 4 ranks; four-rank cap exhaustion at exactly seven globally reserved
attempts; invalid-level refusal; worker exception with cooperative drain; and
hard timeout with a nonzero exit and durable `QueueTimeout` receipt. Zero test
skips, physical queries, basis loads or floating-point MPI reductions.

The portable integration profile now uses `--nooversubscribe` and requires four
available MPI slots for the four-rank cases. It reads `mpiexec --version`, rejects
non-OpenMPI launchers and selects local shared-memory transport `self,vader` for
OpenMPI 4 or `self,sm` for OpenMPI 5 and newer, together with `--mca pml ob1`.
One additional unit test checks both version branches and rejection of MPICH.
This profile change awaits the root's combined validation; the initial result
above does not itself establish the changed launch command on a target host.

For this container's root user only, tests set the two OpenMPI root-confirmation
environment variables. These synthetic-test settings are not the NCP physical
launch resource contract. If `mpiexec` is absent, real-MPI tests explicitly skip
and execution is unverified. If a launcher exists but mpi4py/libmpi is missing or
broken, the subprocess tests fail visibly instead of hiding it with a skip.
