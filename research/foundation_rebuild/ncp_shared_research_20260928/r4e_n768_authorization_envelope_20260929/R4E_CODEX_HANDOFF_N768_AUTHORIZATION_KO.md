# Codex handoff — R4E N=768 bridge-rung authorization

Role: `CLOUD_REVIEW_REPAIR_EXECUTOR`.

## Exact executable identity

Repository: `cosmosapjw-quantum/bass_cr`

Use exactly:

`EXECUTION_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481`
`EXECUTION_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425`

Do not execute the moving research or documentation branch HEAD.

Historical source:

`RESUME_BYTES=31849212`
`EXPECTED_RESUME_SHA256=630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
`CONTEXT=bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda`

Frozen native hashes remain those in the repaired R4C handoff.

## Interpretation

N=768 is a **bridge rung**, not a gate-closing rung.
R4D proves dual PASS at N=768 is mathematically impossible under the two
frozen 1e-6 distance screens.

A healthy completion must stop after N=768 and normally return:

`R4E_N768_BRIDGE_COMPLETE__N1536_DECISION_PENDING`

or an equivalent unresolved bridge status.

If both distance screens PASS, return
`METRIC_OR_EVIDENCE_INCONSISTENCY` and stop.

## Fresh authorization

Standing GitHub/Drive/Dropbox permissions are not native-science approval.

Before execution require one explicit user approval containing all of:

- exact execution commit above;
- exact archive SHA256 above;
- exactly one `N384 -> N768` attempt;
- a new unique `R4C_AUTHORIZATION_ID`;
- `R4C_MAX_WALL_SECONDS=36000`;
- 60-second termination grace;
- provider/user cost scope for this single existing-host attempt.

Suggested authorization ID, if the user explicitly approves it:

`R4C-N768-BRIDGE-20260929-A1`

Do not reuse the consumed R2 authorization.
Do not infer or fabricate a KRW cap.

## Resource basis for the suggested 10 h wall cap

The exact historical archive records incremental rung times:

- N24: 818.455 s
- N48: 1650.007 s
- N96: 3161.049 s
- N192: 6138.470 s
- N384: 12231.598 s

The N384 rung used 1260 raw evaluations for 384 new query times.
Projection of its qualification-resolution pattern to the N768 midpoint grid
gives about 2520 raw evaluations and an empirical center near 24493 s
(6.80 h). The 36000 s cap gives ~47% headroom.

This is not a performance guarantee. If the cap expires, preserve partial
evidence and stop. Do not auto-retry with a new nonce.

## Before native execution

1. clean detached worktree at exact execution commit/tree;
2. verify archive SHA/size/CRC;
3. verify Python>=3.11, NumPy=2.3.5, SciPy=1.17.0;
4. verify all four numerical thread limits are 1;
5. verify frozen source/library/BUILD hashes and architecture before dlopen;
6. focused tests + archive preflight only;
7. no F0/F1/R2, DOP853, N<=384 science replay, benchmark, capture or b-grid.

## Execution

Use repaired `run_r4c_science.sh` exactly once.
Never bypass it with direct Python.

The command environment must include:

```bash
export EXPECTED_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481
export EXPECTED_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425
export EXPECTED_RESUME_SHA256=630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35
export PREVIOUS_NSTEP=384
export NEXT_NSTEP=768
export ALLOW_NEW_NATIVE_R4C=YES_I_AUTHORIZE_ONE_RUNG
export R4C_MAX_WALL_SECONDS=36000
# R4C_AUTHORIZATION_ID must be exactly the newly user-approved ID.
```

Also export the actually verified absolute `RESUME_ARCHIVE`,
`ANALYTIC_BUILD`, and `BASS_R4C_PYTHON`.

## Post-run mandatory analysis

Record actual:

- `d_ref=d(N768,reference)`
- `d_self=d(N384,N768)`
- previous/current/reference norm drifts
- provider qualification audit
- restored hits/new query times/raw attempts
- exact identities/environment
- wall time and exit code

Then calculate:

`p_ref = log2(2.634560877280569e-6 / d_ref)`

`p_self = log2(7.904769432369909e-6 / d_self)`

and diagnostic forecasts only:

`d_ref_pred_1536 = d_ref^2 / 2.634560877280569e-6`

`d_self_pred_1536 = d_self^2 / 7.904769432369909e-6`

Check the geometry:

`2.634560877280569e-6 <= d_ref + d_self + roundoff_allowance`.

Do not reinterpret extrapolation as certification.

## Stop

Stop after N=768 for PASS, UNRESOLVED, BLOCKED, timeout, operator
qualification failure, or any inconsistency.

No N1536 automatic launch.
No new nonce.
No threshold relaxation.
No source/basis/window/frame changes.

Preserve first failure and all partial artifacts, and create-only back up the
portable return to Google Drive + Dropbox when credentials are present.

Claim ceiling remains unchanged.
