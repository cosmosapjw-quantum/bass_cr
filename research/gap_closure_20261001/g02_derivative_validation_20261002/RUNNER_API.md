# R4Z shifted spatial operator runner

`runner.py` extends the create-only R4Y lifecycle into the frozen 13-point
central derivative stencil. It evaluates static raw/full S/H/D snapshots of the
separate R4X candidate. The separate analyzer constructs the S-only derivative;
this runner performs no propagation and does not promote G02 or production gates.

All commands require this environment before importing Python/NumPy:

```bash
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=2 OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 OMP_PROC_BIND=FALSE python PATH/runner.py ...
```

The API retains R4Y's command structure:

1. `init --inputs recovered_r4u/runtime_inputs --candidate runs_r4x/candidate_v1 --build recovered_r4u/native_build_portable --radial-manifest runs_r4x/native_v1/NATIVE_BUILD.json --contract PATH/TASK_CONTRACT.json --out runs_r4z/derivative_v1 --workers 3` freezes input, candidate, native, source, contract and resource identities. No physical operators are evaluated.
2. `prepare --out ROOT --context-sha256 HASH --plan PLAN.json --batch NAME` freezes an explicit batch with no physical calls.
3. `run --out ROOT --context-sha256 HASH --batch NAME --manifest-sha256 HASH` executes only that batch. No automatic continuation or retry occurs.

Every input task requires exactly these keys:

```json
{"tasks":[
  {"z_a0":0.4,"order":40,"subdivisions":1,"moment_backend":"reference","radial_backend":"python","inner_phase_budget":24},
  {"z_a0":0.4,"order":40,"subdivisions":1,"moment_backend":"fortran","radial_backend":"fortran","inner_phase_budget":24}
]}
```

The frozen domain is z in
`[-0.4,-0.2,-0.1,-0.05,-0.025,-0.0125,0,0.0125,0.025,0.05,0.1,0.2,0.4]` a0,
order40/48/56/64, subdivisions1, and inner phase budget24/12/6.
Only reference/Python and Fortran/Fortran backend pairs are admitted. No legacy
unpartitioned quadrature tasks are admitted. Fallback resolutions require a new
explicit plan within the same global budget, never an automatic retry.

Integer/float phase budgets have identical normalized identity; integer zero,
positive zero and negative zero become the same float zero. A normalized task
also contains `z_hex`, `time_hex`, `index` and `task_id`. The time is computed as
`t = requested_z / projectile_speed_au(100)` in FP64. Both operators receive this
time while retaining original laboratory origins `(0,0,0)` and `(2,0,0)` and
velocities `(0,0,0)` and `(0,0,v)`. Origins are never translated to simulate a
snapshot at time zero. `geometry_identity` in raw metadata and the completion
record contains requested z, exact hexadecimal requested z/time, actual
trajectory centers, actual z and its hexadecimal form, speed and the trajectory
record. Actual `v*t` can differ from requested z by rounding; both are preserved.

The source manifest includes this stage, R4Y's unchanged phase rule, R4X
candidate/operator sources, the original foundations and HPC kernels. The local
`bootstrap.py` is loaded under a distinct module identity; the archived analytic
`bootstrap` is imported and checked by its file path before runtime use.

The runtime reserves three disjoint two-CPU workers plus one coordinator CPU
within the eight-CPU quota, with at least1 GiB memory reserve. BLAS uses one
thread. The moment kernel is configured for two OpenMP threads; its ABI does not
observe actual team size, and receipts state this. The radial evaluator is
configured for one thread and records observed team sizes. This is local process
parallelism, not MPI execution or NCP64 scaling evidence.

A global exclusive lock protects all batches. Atomic create-only reservations
are written before each launch. The total cap is64 attempted calls, including
failed launches. Repeating a normalized task across batches is forbidden.
Launch failure closes logs; worker failure, timeout and coordinator SIGTERM
cancel and reap owned peers. Forced coordinator SIGKILL cannot guarantee Python
cleanup. A started batch is never resumed in place.

The outputs retain R4Y's paths and payload keys:

- `ROOT/CONTEXT.json`: `BASS_R4Z_DERIVATIVE_CONTEXT_V1`.
- `ROOT/batches/NAME/MANIFEST.json`: `BASS_R4Z_BATCH_MANIFEST_V1`.
- `ROOT/batches/NAME/attempts/INDEX/`: `RAW.npz`, `RAW.json`, `FULL.npz`, and `COMPLETED.json` or `FAILED.json`. `INDEX` has three decimal digits.
- Completion hashes: `raw_sha256`, `raw_metadata_sha256`, `full_sha256`.
- Raw metadata: `r4z_context_id`, `manifest_id`, `geometry_identity`, candidate and backend identities.
- Batch `SUMMARY.json`: `BASS_R4Z_BATCH_SUMMARY_V1`, with same-geometry comparisons only.

`load_context`, `load_batch` and `load_payload` expose the same read APIs as R4Y;
`load_payload` also recomputes geometry and verifies both copies. Raw/full cross
block equality, sizes and finiteness are checked. The central identical-s
exact-zero control applies only at z=0; nonzero points record `NOT_APPLICABLE`
with `pass:null`. No raw array is projected.

The original six-block relative metric and full matrix screens are unchanged.
Comparisons across different geometries are intentionally absent from the spatial
summary. The read-only derivative analyzer separately consumes all qualified
stencil points. Worker receipts keep G02 UNRESOLVED, production HOLD and capture
false irrespective of observed local agreement.

`python PATH/test_runner.py` runs13 synthetic tests without physical calls.
The modified tests cover the new exact z/time domain and canonical identities,
original-origin trajectory construction, conditional central control, and the
64-call ledger. Existing meaningful lifecycle checks cover resource admission,
create-only writes, transparent counters, launch failure, peer cancellation,
timeout and retry rejection.
