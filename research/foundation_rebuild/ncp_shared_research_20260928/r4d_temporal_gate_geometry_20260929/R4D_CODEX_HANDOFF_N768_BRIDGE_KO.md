# Codex handoff: N768 bridge-rung execution after R4D gate-geometry audit

Role: `CLOUD_REVIEW_REPAIR_EXECUTOR`.

## Authoritative identities

Repository: `cosmosapjw-quantum/bass_cr`

Execute **only**:

- `EXECUTION_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481`
- `EXECUTION_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425`

Do not execute a moving research/documentation branch HEAD.

R4C/R4D directory:

`research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation`

Frozen historical archive:

- bytes: `31849212`
- SHA256: `630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
- context: `bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda`

## New R4D mathematical fact that changes interpretation

The N384-reference phase-aligned metric distance is

`2.6345608772805691e-06`.

Both frozen N768 distance screens are `1e-6`. The same positive-definite
`S_final` is used in both distances and the distance is the U(1)-phase
quotient of the S-norm. Hence triangle inequality gives

`d(N384,ref) <= d(N384,N768) + d(N768,ref)`.

Since `2.6345608772805691e-06 > 2e-6`, **N768 cannot pass both frozen screens under
any possible numerical outcome**.

Therefore N768 is authorized, when separately approved by the user, only as a
**bridge/diagnostic rung** needed to construct the subsequent N768->N1536
consecutive-refinement comparison. Do not describe N768 as capable of closing
the temporal gate.

If the run reports both distance screens PASS, stop and return
`METRIC_OR_EVIDENCE_INCONSISTENCY`; do not continue.

## Review before execution

1. Use a separate clean worktree at the exact execution commit/tree.
2. Read `AGENTS.md`, the R4C hostile-audit handoff, `continue_temporal.py`,
   `run_r4c_science.sh`, frozen contracts, and this R4D result.
3. Independently check that `phase_aligned_metric_distance` and
   `assess_temporal_pair` still use the same `S_final` and no code drift changes
   the metric argument.
4. Verify frozen `.so` source/library/BUILD hashes and architecture before
   dlopen. No rebuild or fallback.
5. Verify Python >=3.11, NumPy 2.3.5, SciPy 1.17.0 and thread limits.
6. Run only the focused non-native tests/preflight required by the repaired
   handoff. Do not repeat F0/F1/R2, DOP853 reference, N<=384 science, or long
   unchanged suites.

## Fresh user authorization requirement

The GitHub/Drive/Dropbox standing permissions are **not** native-science
authorization.

Before N768, require a fresh explicit authorization containing:

- exact `EXECUTION_COMMIT` and archive SHA256 above,
- `N384 -> N768` exactly one attempt,
- a unique `R4C_AUTHORIZATION_ID`,
- explicit `R4C_MAX_WALL_SECONDS`,
- termination grace,
- cost scope / external cost control as applicable.

Do not invent these values and do not reuse the consumed R2 3600s/4000 KRW
one-shot.

## Execution scope

Run the repaired `run_r4c_science.sh` exactly once. Do not bypass it with a
direct Python invocation. The calculation is a fresh N=768 propagation over
the same full finite window, not 768 steps appended to N=384.

Frozen scope:

- same 18-channel basis,
- 100 keV/u,
- b = 2 a0,
- z = -12 ... +12 a0,
- same frame/ETF conventions,
- same qualification ladder and thresholds,
- no capture/all-bound/b-grid/cross section.

No N1536 automatic continuation.

## Required post-run analysis

Record at minimum:

- actual `d_ref = d(N768,reference)`,
- actual `d_self = d(N384,N768)`,
- both norm drifts,
- operator qualification audit,
- cache hits / new unique query times / raw attempts,
- exact environment and code/input identities,
- wall time and exit status.

Check the geometric invariant

`2.6345608772805691e-06 <= d_self + d_ref + numerical_tolerance`.

Also report

`p_ref = log2(2.6345608772805691e-06 / d_ref)`

and, using the historical N192->N384 refinement distance
`7.9047694323699088e-06`,

`p_self = log2(7.9047694323699088e-06 / d_self)`,

when all inputs are finite and positive. These are diagnostics, not automatic
admission criteria.

Expected classification when execution is otherwise healthy:

`R4D_N768_BRIDGE_COMPLETE__TEMPORAL_CLOSURE_UNRESOLVED`.

Do not call this a failure merely because one frozen distance screen fails;
dual PASS is mathematically impossible at N768.

## Stop conditions

Stop after this one rung for every outcome:

- healthy bridge result,
- unresolved temporal screen,
- qualification failure,
- timeout/runtime interruption,
- identity/environment blocker,
- geometric inconsistency.

Preserve first failure and partial artifacts. Do not delete the one-shot nonce,
generate a new authorization ID, retry automatically, loosen thresholds, or
launch N1536.

Small evidence may be non-force pushed to a dedicated evidence branch.
Portable output must be create-only backed up to Google Drive + Dropbox when
credentials exist; distinguish provider acknowledgement from full restore
verification.

Claim ceiling remains:
capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false;
continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
