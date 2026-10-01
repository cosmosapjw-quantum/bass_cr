# R4X static operator diagnostic adapter

`continuous_full_operator.py` is an additive copy of the frozen original
`full_operator.py`. Only its finite-radial type guard is extended to accept the
identity-validated `basis_representation.ContinuousRadial`. All integration,
assembly, matrix checks, phase terms, and raw matrix arithmetic are unchanged.

`continuous_exact_cross.py` is an additive copy of the frozen `exact_cross.py`.
The former `fast_cross._validate` radial guard is replaced by its local extended
counterpart. The coefficient fingerprint guard now recognizes the separately
identified endpoint/bubble payload. Metadata identifies the representation.
Quadrature nodes, order, packet boundaries, native arguments, and accumulation
remain unchanged. `OPERATOR_SOURCE_PATCH.json` records exact upstream/adapted
hashes, unified diffs, and a structural numerical-body comparison.

The supported candidate API is `continuous_exact_cross.cross(..., kernel=...)`
followed by `continuous_full_operator._bind_cross` and
`continuous_full_operator.assemble_full(..., cross=snapshot)`.
Use the original `hpc_optimization_20261001.kernel.HPCMomentKernel`, with the
explicit `backend='reference', threads=1` settings used by this diagnostic.
The legacy `MomentKernel` class retained verbatim in the copied module is not an
adapter entrypoint; its original sibling-source requirement fails closed here.
Likewise candidate `assemble_full` without an explicitly bound cross snapshot
reaches the unchanged legacy aligned-cross guard and is not supported. Neither
branch silently treats endpoint/bubble values as monomial coefficients.

The runner creates its manifest without native loading or physical evaluation:

```bash
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 python recovered_r4u/source/research/gap_closure_20261001/g02_continuous_basis_20261002/run_static_comparison.py prepare --inputs recovered_r4u/runtime_inputs --candidate runs_r4x/candidate_v1 --build recovered_r4u/native_build_portable --out runs_r4x/static_v1 --workers 4
```

After inspecting the exact fresh manifest, execute the same runner with `run
--out runs_r4x/static_v1 --manifest-sha256 HASH_FROM_PREPARE`, under the same
environment. The caller owns authorization. The runner does not reuse any prior
raw-call approval. It freezes exactly eight calls: original/candidate, z=-32/0
at b=2, order 32/40, same-center order20. Both representations use the same strict
C++ moment backend; the candidate radial evaluator is Python FP64. Separate
Fortran evaluator benchmarks do not imply the static probes used Fortran.

The coordinator reserves one distinct CPU; up to four single-thread workers use
disjoint CPUs. CPU quota and memory headroom are checked again before launch.
Memory admission includes 1GiB per worker, 0.5GiB for the coordinator, plus the
larger of 1GiB or one eighth of current admitted memory. These are estimates.
There is no MPI execution or NCP64 scaling claim.

Each raw attempt is reserved durably before launch. Outputs are create-only.
`RAW.npz` is saved before full assembly, so a subsequent assembly failure cannot
erase the raw result. Worker failure/timeout stops the batch, terminates and
reaps owned peer process groups, and never retries a consumed reservation.
Re-executing a started output directory fails before new calls. The worker
command is an internal coordinator entrypoint and requires a matching durable
reservation. No helper launches descendant work.

`SUMMARY.json` reports full and six raw S/H/D differences, same-center derivative
defects and metric conditioning, plus order32-to40 differences. It applies only
the local screens frozen in `TASK_CONTRACT.json`. The resolution difference is
an observation, not a certified quadrature error. No FD gate, propagation,
capture, full scattering window or production qualification is performed.

Nine targeted tests cover rejection by legacy APIs, payload tampering, mixed
representations, exact original same-center parity, unchanged synthetic cross
native arguments/batches/results, resource admission, create-only receipts,
and cancellation without retries after a synthetic worker failure. A focused
process-creation failure test checks that a durable reservation remains counted
when the operating system does not start the worker. Together with ten basis
tests, the final stage has nineteen unique tests.

The eight actual static probes completed before this coordinator accounting
repair. Their exact executed runner is preserved in
`runs_r4x/source_at_run/run_static_comparison.py`; its hash matches the frozen
static manifest. `runs_r4x/POST_RUN_REPAIR_RECEIPT.json` binds the before/after
sources, the sole changed source pin, the unchanged static results, and the
actual final nine-test log. The repaired scheduler has no new physical runs.
