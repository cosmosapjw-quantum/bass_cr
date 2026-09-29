# R4F3 native-readiness audit

Status: `R4F3_LINEAGE_REPAIR_REVIEW_PASS__NATIVE_MIGRATION_READY_PENDING_EXPLICIT_USER_APPROVAL`.

Reviewed exact implementation:

- commit: `11100b35f78ec26100ea732971bb4ce0f9925719`
- tree: `05976e386c0a39591247d69c32c8cb28fa3f2a97`
- branch: `codex/r4f-authorization-lineage-repair-20260929`

The previous R4F2 P1 blocker is closed in source: the parent serial authorization, the prior failed migration authorization, and the proposed fresh repaired-migration authorization are now distinct. The immutable STOP_RECEIPT is compared to the prior failed migration ID, while the fresh ID is recorded separately. The runner also binds STOP_RECEIPT, prior admission, prior return, and prior partial archive SHA256 identities.

Execution-reported non-native evidence supplied with this checkpoint:
- focused suite: 39 passed, 0 failed, 0 skipped;
- original/restored query pairs: 1279/1279;
- base required hits: 2;
- stopped-parent extra midpoint pairs: K=186;
- missing midpoint IDs: M=582;
- admitted orphans: 0;
- native calls during preflight: 0;
- parent raw attempts: 374;
- strict upper bound: 374 + 22 + 582*11 = 6798 <= 8470.

Independent source review found no new P1 lineage blocker. Two operational guards remain:

1. `run_r4f_science.sh` is still Git mode `100644`. Launch it explicitly through `bash`; do not execute it directly and do not chmod the approved tree.
2. The approval/launch must pin exactly: workers=8, CPUs=0-7, worker RAM=1073741824 bytes. Verify those exact values in `EXECUTION_ADMISSION.json`.

At 2026-09-29 14:24:18 KST the unchanged deadline 2026-09-29T12:25:08Z had about 7.01389 h remaining. Wolfram arithmetic gives a serial remaining proxy of 5.14958 h for M=582, while 8-worker operator-fill proxies range from about 0.805 h (eta=0.8) to 1.609 h (eta=0.4). Strict raw-cap margin is 1672.

Literature retrieval through SciSpace supports application/task-level checkpoint/restart and localized recovery for independent scientific tasks, including:
- DOI 10.1109/IPDPSW52791.2021.00089
- DOI 10.1109/PDP.2015.17
- DOI 10.1007/978-3-030-57675-2_26
- DOI 10.1145/3624062.3624256

No native parity, pilot, parallel fill, cache-only replay, N1536, capture, all-bound, or b-grid was executed in this audit.

Fresh authorization remains pending. Claim ceilings remain unchanged: capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO, original_capture_gap_resolved=false, continuous_global_supremum_bound=false, continuous_trajectory_error_bound=false.

Research package:
`BASS_CR_R4F3_NATIVE_READINESS_20260929_v1.zip`
SHA256: `7b0de4426204c3da105d12f0d687e6829323f5234f8c218f5675152fabafb4c4`.
