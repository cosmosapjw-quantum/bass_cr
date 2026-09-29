# R4F2 authorization-lineage audit and Codex handoff

Status: **OBSERVED_FAILURE_ROOT_CAUSE_REPAIRED__FRESH_LINEAGE_BLOCKER_FOUND__NO_NATIVE_RESTART**

## Verified observed failure

Prep commit `2e6ffa4378005bbdc7218b2884b18c074bc74e9d` called
`serial.restore_query_store(source,out,context_id)`.
The frozen `continue_temporal.py` does not export that symbol; its serial path imports
`restore_query_store` locally from `qualified_provider`.
This predicts the observed
`AttributeError: module 'continue_temporal' has no attribute 'restore_query_store'`.

Repair commit `f021d563a47fb41d35e51c7944193980f9152d62`,
tree `2d9d479f9ecba59acd2ee9991b213c70b348ac4b`, directly imports
`qualified_provider.restore_query_store` and adds a focused regression assertion.
This is a narrow, mechanistically correct repair of the observed restore failure.

Stopped-parent state remains:
- parent serial auth: `R4C-N768-BRIDGE-20260929-A1`
- prior failed migration auth: `R4F-N768-MIGRATION-20260929-A1`
- K=186 complete new midpoint pairs
- M=582 missing required midpoint IDs
- parent raw attempt_started count=374
- prior R4F native calls=0
- non-native preflight after restore repair: original/restored 1279, K=186, M=582
- focused suite reported 28 passed

## Fresh P1 blocker

Do **not** authorize `f021d563...` for native restart as-is.

`controlled_stop.py` records the immutable stop receipt field
`migration_authorization_id=args.migration_auth_id`; for this stop that is the
prior failed ID `R4F-N768-MIGRATION-20260929-A1`.

The repaired runner calls
`_parent_receipt(..., migration_id=args.authorization_id,...)`
and currently requires
`stop_receipt["migration_authorization_id"] == migration_id`.

A correct repaired restart must use a **fresh new** authorization ID. Therefore
the current code cannot satisfy both the immutable stop-receipt lineage and the
fresh-ID policy. Reusing the old failed migration ID would erase the distinction
between the failed attempt and the repaired attempt.

## Required minimum repair

Represent three IDs explicitly:
1. parent serial authorization,
2. prior failed migration authorization,
3. fresh repaired migration authorization.

Recommended interface: add
`--prior-migration-authorization-id`.

Requirements:
- compare the stop receipt's `migration_authorization_id` with the prior ID;
- require the fresh new ID to differ from parent and prior IDs;
- record all three IDs in admission/lineage receipts;
- bind the new lineage to the immutable stop-receipt SHA256 and, when available,
  the preserved failed-migration admission/return/archive identity;
- never rewrite the stop receipt, stopped parent, prior failure or old authorization evidence.

Required RED/GREEN tests:
- prior=A1, new=A2 with immutable stop receipt A1 -> pass after fix;
- wrong prior -> reject;
- new==prior -> reject;
- new==parent -> reject;
- stop-receipt hash/parent lineage mismatch -> reject;
- no native worker/load/authorization-consumption boundary crossed;
- restore-API regression remains passing.

Then rerun the actual stopped-parent **non-native preflight only** and require:
1279 original pairs, 1279 restored, base required hits=2, K=186, M=582,
admitted orphans=0, native calls=0.

## Resource invariant

Global raw cap remains 8470.
Strict worst case after repair:
`374 + 22 + 582*11 = 6798`, margin 1672.

Wolfram verified:
- serial remaining proxy: 5.1495845 h
- 8-worker query wall proxy:
  eta=0.8 -> 0.80462 h,
  eta=0.6 -> 1.07283 h,
  eta=0.5 -> 1.28740 h,
  eta=0.4 -> 1.60925 h.
At 2026-09-29 04:28:20 UTC, the unchanged deadline
2026-09-29 12:25:08 UTC had 7.94667 h remaining.

The useful 8-query pilot is part of M=582, not extra throwaway work.
Parity remains separately bounded at <=22 raw attempts.
Do not reset or extend the cumulative KRW 50,000 scope automatically.

## Codex next node

Role: `R4F_AUTHORIZATION_LINEAGE_REPAIR`.

No parity, pilot, parallel fill, cache-only replay, N1536, capture or b-grid.
Repair only the lineage model, add the regression tests, run the full focused
non-native suite and real-parent non-native preflight, then commit/push a new
exact commit/tree and return one `MIGRATION_REPAIR_READY` handoff.

That handoff must include:
- new exact commit/tree and changed files;
- RED/GREEN proof and total focused-test result;
- real-parent non-native preflight counts;
- all three authorization IDs/roles;
- stop-receipt SHA and failed-migration evidence identity;
- unchanged numerical/native/archive hashes;
- K=186 / M=582;
- parent raw=374 / worst total=6798 / margin=1672;
- CPU 0-7, max 8 workers, 1 GiB/worker;
- parity cap 22 raw attempts, useful pilot 8;
- unchanged original deadline/cost scope.

Only then ask the user once for a fresh repaired-migration authorization.
No automatic retry/new nonce/N1536. Claim ceilings unchanged.
