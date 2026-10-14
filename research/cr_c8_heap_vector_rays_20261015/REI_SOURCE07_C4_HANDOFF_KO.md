# BASS_CR C8 source-identity and SOURCE07 C4 owner handoff (2026-10-15 KST)

This is an **actual executed Python optimizer** committed in `bass_cr`; it is not a patch to `rei_bianchi`. Parent `bass_cr` PR66 `0a43dcbaf7691c04706800e3336c1fd5ceb056ce`. Read `REPORT_KO.md` and `NEXT_DAG.json` for scope.

## Implementation and tests
- Drop-in `HeapCompressedCohortTransport` returns exactly the same accepted compressed lists and `CompressionCertificate` as the original scan on recorded inputs, including error-budget HOLD. The batch Verner readout uses original coefficients with independent proper gas/time/redshift for each ray, not a new physical source. Same-science exact parity and numerical-difference controls: 92/92 tests PASS, plus relocated ZIP retest 92/92.
- `compress_bianchi_ray_lanes` groups by (ray ID, source birth epoch, current proper clock) and a fixed current normal-tetrad direction. It never merges different angular rays or different ages. Exact null photon four-momentum under scalar-energy merging holds **only within a single direction**. This is an interface validation, NOT an owner k_i/source Jacobian replacement.
- Source producer responsibility: `rei_bianchi` SOURCE07 `axbi_q_reference` and C3 `axbi_q_advance` own each characteristic energy, direction, time, and R*J weight **exactly once**. Transfer only `(Ephysical_eV,NperH)` plus separate immutable ray/age/clock key to the bass_cr module. This supplier has no direct Bianchi evolving-H or nonlinear coupled-gas rate certificate.
- Local first derivative Verner event/heat budget uses floating point with cushion, **not outward rounded**. Future source-versioned trials must validate within actual gas-chemistry occupancy; do not promote 50kK fixture rates to a new cosmic history.

## New speed measured at equal frozen-neutral component accuracy
Actual Ubuntu workstation Python3.12.3, 24 logical CPU visible, five-repeat medians:
- Heap vs full rescanning: 48→32 7.48×; 96→48 8.84×; 240→32 34.45×; 384→192 60.50×.
- NumPy ragged-ray Verner BE readout vs original scalar: 8 rays 3.13×; 64 rays 4.50×; 256 rays 4.88×.
- Optional per-ray `forkserver` processes: 8 rays one worker5.82ms, two35.09ms, four39.87ms; 64 rays one57.22ms, two62.26ms, four61.78ms. On these sizes parallelizing compression adds overhead. Its reproducible code stays optional. Do not transfer the above speedups to a full native Rust solver.

## Why not copy the owner's optimized code
Actual `rei_bianchi` PR117 head `0c9fd151b6e0aef9ee2414ed672364afa4a3dce1` already contains tested C3 threshold-aware Bianchi photon event transport, 1/2/4-thread native Rust and SoA. Its own Ryzen5900X native 24576-packet benchmark reports axisym four threads 2.71×, AoS→SoA readout 5.77×, for **different native matched physics**. C4 requires angular/age/source ownership and maximum 2GiB lane budget. Reimplementing its source Jacobian or claiming this Python module supersedes C3 would be incorrect.

## Remaining owner gates and next practical task
`REI_SOURCE07_C4_A_CAP_CHOICE` owner-controlled: compare actual q direction-preserving bounded cohorts and fixed-q grid with same source/IC/clock, per ray binding, event/heat absolute and relative errors, actual memory bytes and source IDs; improve static one-step bound with directed or second-derivative estimates as needed. Then source-map and variable opacity C4_B/C before full variable-geometry history. Historical 49-node checkpoints and prior AX08/AX11/AX12 evidence remain unchanged. This supplier is **READY_FOR_OWNER_SCOPED_CONSUMPTION**, not full C4 scientific PASS.

### Git run command
From new branch layered on PR66:
`PYTHONPATH=research/cr_c8_heap_vector_rays_20261015/src:research/cr_c5_budgeted_cohorts_20261015/src python -m pytest -q research/cr_c8_heap_vector_rays_20261015/tests`.
The existing parent tests can be run separately. Full standalone all-92 test ZIP is preferred for no-dependency relocation.

Proof/benchmark files and immutable standalone source: Drive `1MrM1aZTuEeqzLIq88cV5LJFNuENzYfXh`, Dropbox `id:BSpOijBcT10AAAAAAD7ftQ`, file `BASS_CR_OPTIMIZED_RAYS_20261015_SOURCE.zip`, SHA256 `b809de4fde0aec6766cc305b67686ebf615325fee2e183d34eee87edd515c4a1`, 142866 bytes, 27 SHA payloads. Both cloud ACK and size; local and Ubuntu full-archive byte/hash/tests verified. `native_subagent: NOT_RUN`; no local Codex or external repo mutations during this run.
