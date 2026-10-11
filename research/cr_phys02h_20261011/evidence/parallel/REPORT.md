# CR-PHYS02H parallel operator local implementation evidence

## Result

All 16 small complete and 8 selected-column logical builds completed, actual exit 0, external wall 66.285 s. Each candidate is byte-exact to its same-input reference in raw CSC data/indices/indptr, energy and rates; normalization diagnostic sequence is exact. Both repetitions pass. No complete 9600 operator was built here.

The pilot executed 52 generator invocations: 4 unmodified original small-grid generators, 4 original-arithmetic serial restricted generators, and 44 fresh spawned partial-worker generators. Logical builds and actual calls are separate. Each requested column is evaluated exactly once per candidate; selected probes cover only the 16 frozen columns.

Four targeted tests passed (actual exit 0, 2.039 s): missing/duplicate/out-of-order partition rejection; AST-restoration proof and byte-exact two-model storage/rates/diagnostics; NPY round-trip and modified-file rejection; failed-child cleanup; forbidden complete9600 local-host rejection. The injected failure is an expected test outcome, not a failed scientific pilot. Its canceled sibling generator-entry count is unobserved (0 or 1), and is excluded from the exact pilot counts. No implementation repair was used.

## Source and assembly argument

The cloned generator differs structurally only in its function name, added columns argument, and sole top-level outer column iterator. Replacing these three elements with originals reproduces the pinned parent AST exactly. Compilation uses the original module globals. Every tile creates a fresh shell with immutable identical E, n/size/ix, actual checked atomic data, sharing order4, quantum constant0, original mesh and empty normalization diagnostics. The original column body and precomputation remain intact.

Columns depend on immutable E and atomic rates and mutate only their local dense col and append-only diagnostic list. Tile column lists form contiguous sections of the sorted requested column list; selected tiles need not be consecutive physical indices. Gather copies exact CSC column slices in global column order, concatenates raw arrays, and constructs integer indptr. No sparse addition, FP reduction or duplicate coalescing occurs. Diagnostic lists concatenate in that same column order. Signed stored values are preserved.

This is a new implementation identity, not inherited SavedGridCascade approval. The reference and candidate intentionally share original arithmetic and physical inputs. These checks qualify restriction and assembly, not an independent physics oracle or prior E/F checkpoint/operator adoption. Atomic source dependency checks remain real and fail closed.

## Local timings

End-to-end seconds include each serial API call or spawned candidate construction and gather. Serial generator-only wall is also retained in raw telemetry. Process spawning and fresh imports are included in candidate timings. No local speedup is established for these small workloads.

| Scope | Model | Mode/workers | Repeat 1 s | Repeat 2 s | Mean s |
|---|---|---|---:|---:|---:|
| small | legacy | serial/0 | 1.179756 | 1.792038 | 1.485897 |
| small | legacy | parallel/1 | 2.234048 | 3.371505 | 2.802777 |
| small | legacy | parallel/2 | 2.984457 | 4.196851 | 3.590654 |
| small | legacy | parallel/4 | 3.464447 | 3.362953 | 3.413700 |
| small | fullBED | serial/0 | 1.062765 | 1.067514 | 1.065140 |
| small | fullBED | parallel/1 | 2.338167 | 2.535497 | 2.436832 |
| small | fullBED | parallel/2 | 2.855366 | 4.119600 | 3.487483 |
| small | fullBED | parallel/4 | 2.950851 | 3.146369 | 3.048610 |
| selected | legacy | serial/0 | 0.612377 | 0.471159 | 0.541768 |
| selected | legacy | parallel/4 | 4.619298 | 5.311898 | 4.965598 |
| selected | fullBED | serial/0 | 0.471370 | 0.582572 | 0.526971 |
| selected | fullBED | parallel/4 | 4.410170 | 5.208556 | 4.809363 |

## Resource scope

Actual cgroup quota is 8 CPUs and memory.max is 8 GiB; affinity inventory is separately retained. Candidates use at most4 workers plus their coordinator, all BLAS/NumExpr/OpenMP environments fixed to1. Admission includes coordinator, observed cgroup current use, 512 MiB per new process estimate and at least2 GiB reserve. Largest observed fresh-worker lifetime peakRSS was 125.941 MiB; largest coordinator lifetime peakRSS was 125.941 MiB. Worker RSS is resource.getrusage(RUSAGE_SELF).ru_maxrss from each fresh process; coordinator RSS is a cumulative lifetime peak, not per-build delta. Simultaneous total RSS is not inferred by summing nonconcurrent peaks. The spawn runtime may also start a multiprocessing resource_tracker support process; it performs no column calculation, and its RSS is not included in worker/coordinator telemetry. The local 8-CPU quota leaves capacity beyond4 computation workers and coordinator. NCP aggregate admission must account explicitly for root/lane coordinators and support processes.

No MPI execution, NCP64 scaling or full9600 resource qualification is claimed. Complete full-grid serial and parallel builder APIs are prepared but the small-memory host refuses their execution; NCP execution requires its separate frozen source/input/resource contract and aggregate lane/root admission.

## Persistence

Every one of the24 payloads retains data.npy, indices.npy, indptr.npy, energy.npy and each model rate array, plus SIDECAR.json with dtype, shape, raw-byte SHA256, file SHA256/size, matrix shape, evaluated columns, complete ordered diagnostics, source pins and runtime/assembly identity. Both payloads are persisted before candidate parity comparison, so a future parity failure would retain values. PILOT_PLAN.json predates execution; create-only reservation files prevent replay of the same pilot output directory. Raw stdout/stderr, actual exit/wall and completed progress remain available.

Inherited scientific HOLD/OPEN/NO_GO gates remain unchanged.
