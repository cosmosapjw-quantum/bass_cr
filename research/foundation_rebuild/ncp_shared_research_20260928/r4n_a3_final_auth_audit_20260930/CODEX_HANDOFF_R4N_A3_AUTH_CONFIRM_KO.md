# Codex handoff — R4N exact A3 proposal confirmation

Role: `N1536_A3_EXACT_AUTHORIZATION_CONFIRMATION`.

Do not start native science. Do not consume the A3 nonce. Do not modify source code.

Exact execution:
- commit `b310a5f782f2739deb886218ef354281ed614611`
- tree `ae02da10ac9a6145f0ddddb98c63257bd64f6338`

Final package:
`N1536_A3_PREP_b310a5f_15fa2b923d4b_20260930.zip`
SHA256:
`15fa2b923d4b98aa4aeafe64150b388cc3882a2f20874e749375a676ca0f1765`

Saved live census:
`/root/.local/state/bass_r4m/packages/A3_LIVE_CENSUS_20260930T0435Z.json`

Saved authorization proposal:
`/root/.local/state/bass_r4m/packages/A3_AUTHORIZATION_PROPOSAL_20260930T0435Z.json`

Final package pins:

SOURCE_PINS_SHA256=
`7688fe42f9988ca5ddff13e95f1d866a2194c5db81f6137f91a990a04f46a26d`

QUERY_PLAN_SHA256=
`212e492f677867e75434584d6d29cb31dabe130dab9ef00f07ea86b54093da0b`

USEFUL_PILOT_PLAN_SHA256=
`a6ae00971235e6b4955603eb081969376479324abe84413b37ba7c24e309e349`

A2_CUMULATIVE_SALVAGE_MANIFEST_SHA256=
`2567c2aa5334ebdc9561bc21c804b13ab0a5aaa124ceb7961a87faf8d8f422d1`

N1536_REMAINING_FILL_PLAN_SHA256=
`8e2fa7af8b05688b38c1f4ddc3d3093f66e7530b4c89483a05da1716b75d5bb7`

A2_SELECTED_STAGE_EVIDENCE_SHA256=
`8a5aedf220e231bd90b5227913dd9f81bc7ea09446d1f259b3a6d8611a0fafa1`

RESOURCE_POLICY_SHA256=
`52eb02ba0d0da6f17fb5125d363a86e8435adafdd640c83e43a6d84ab7921850`

Fixed A3 semantics:
- authorization candidate `R4G-N1536-ADAPTIVE-SHARED-RESUME-20260930-A3`
- resource policy `COOPERATIVE_SHARED_HOST`
- CPUs candidate ordered 0..31
- selected workers 32
- pilot reexecution NONE
- prior raw 368
- lifetime raw cap 16896
- remaining midpoint IDs 1424
- worker RAM 1073741824
- total worker RAM cap 34359738368
- parity NONE

Read-only confirmation:

1. Print the COMPLETE saved authorization proposal JSON.
2. Recompute the exact package authority-file SHA256 values and compare every proposal pin.
3. Recheck HEAD/tree/clean worktree, affinity, finite CPU quota if any, live RAM, own stale A2 worker/process-group state and peer telemetry.
4. Confirm the A3 authorization ID remains unused.
5. Do not silently change the saved absolute deadline.

Return one of:
- `A3_NATIVE_AUTHORIZATION_READY`
- `A3_AUTHORIZATION_PIN_MISMATCH`
- `A3_LIVE_RESOURCE_HARD_BLOCKED`
- `A3_AUTHORIZATION_IDENTITY_BLOCKED`

Then print:
ACTUAL_HEAD
ACTUAL_TREE
ACTUAL_SOURCE_PINS_SHA256
ACTUAL_QUERY_PLAN_SHA256
ACTUAL_USEFUL_PILOT_PLAN_SHA256
ACTUAL_SALVAGE_MANIFEST_SHA256
ACTUAL_FILL_PLAN_SHA256
ACTUAL_SELECTED_STAGE_SHA256
ACTUAL_RESOURCE_POLICY_SHA256
FRESH_AUTH_UNUSED
LIVE_CPU_AFFINITY_OK
LIVE_CPU_QUOTA_OK
LIVE_RAM_OK
OWN_POOL_TEARDOWN_OK
EXTERNAL_BASS_PEERS
NATIVE_SCIENCE_STARTED=NO

Finally print the complete mechanically generated approval block including exact ID, CPU list, absolute deadline/deadline_unix, max wall, grace, cumulative A1+A2+A3 cost scope, cooperative shared-host policy, prior raw=368 and lifetime cap=16896.

Then wait for explicit user approval.
