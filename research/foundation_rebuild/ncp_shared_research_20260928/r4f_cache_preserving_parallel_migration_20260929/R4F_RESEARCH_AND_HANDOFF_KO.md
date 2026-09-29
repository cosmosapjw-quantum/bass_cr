# R4F: running N768의 cache-preserving parallel migration

Status: DESIGN_READY__LIVE_CENSUS_AND_PRODUCTION_IMPLEMENTATION_PENDING.
사용자는 serial N768이 이미 실행 중이라고 보고했다. 이번 ChatGPT 연구에서 원격 PID/진척은 관측하지 않았고 process 중단, 새 native operator evaluation 또는 production parallel runner 구현은 수행하지 않았다.

## Authoritative identities

BASE_SERIAL_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481
BASE_SERIAL_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425
ORIGINAL_ARCHIVE_SHA256=630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35
ORIGINAL_ARCHIVE_BYTES=31849212
CONTEXT_ID=bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda
Research parent=7f225ec838018c46c7fac4e896792d5adee8d673

## Source-derived findings and fresh arithmetic probe

AnalyticEvaluator(t,order,subdivisions) does not consume the propagated state. Each query's ordered resolution ladder is independent of other times. Parallelize time queries, not the chronological state updates or each query's reduction/qualification order.

ResolutionQualifiedProvider commits NPZ first and JSON receipt second using atomic create-only writes. Reuse only complete hash/identity/qualification-valid pairs. A completed raw-call log is NOT a committed qualified query. The in-progress query's resolution payloads may exist only in memory.

continue_temporal.py writes CANDIDATE_N768 only after run_candidate returns. A generic intermediate-state resume is not implemented. Preserve expensive operator preparation; replay only the small chronological state propagation from the original initial state with a strict cache-only reader.

The original runner requires the original exact archive, original source status and exactly1279 queries. Do not replace that archive with an interrupted OUT or edit its status/pins. Implement an additive extra-cache importer/orchestrator with separate lineage.

Fresh read-only probe checked the locked archive and1279 query payload hashes. Original traversal arithmetic is:

    dt=(tf-t0)/768
    ta=t0+j*dt
    tb=ta+dt
    tm=0.5*(ta+tb)

Replacing this by t0+(j+0.5)*dt changes607 of768 binary64 time_hex values; max difference8.881784197001252e-16 atomic time. Keep exact expression order and actual step width tb-ta. Required query set=770; base exact hits=2; initially new midpoints=768; complete base union=2047. Seven synthetic completed-prefix set checks passed; no real worker/native parity or performance was measured.

Required-plan canonical JSON digest=93512ebead8c0374bcc93a6cd2075f8f18ba3f4bdf8b5d8d806d7c4be1d867d0.

## Decision rule

M=|required_ids-(valid_original_ids union valid_live_ids)|. Do not infer M from raw-call count or unfiltered file count.

T_keep approximately M*tau.
T_switch approximately H+M*tau/(P*eta).
Switch is useful only when H < M*tau*(1-1/(P*eta)), with P*eta>1.
H includes remaining implementation/review, bounded native parity, stop/freeze/import/start, replay and tail overhead. Re-read live M when implementation is ready. Do not count already elapsed development twice.

Historical proxy tau=31.8531s/query. Under explicitly hypothetical P16, eta0.5, H1h requires at least130 remaining queries; H2h requires at least259. These are not measured speedups or current-host forecasts. Nearly completed serial runs should finish unchanged.

## Codex live-window handoff

1. Read-only census first. Identify actual Python PID/start-time/cmdline/cwd and timeout supervisor/PGID, active OUT, code/input/native/env identity, consumed authorization, deadline/cost scope, current committed required IDs and pending raw attempts. Whitelist relevant environment fields; do not dump secrets. Check other BASS_HE/WU088_HH jobs, live CPU/RAM/cgroup/lease. Historical quota proposals are not current grants. If N768 is already complete, verify and preserve it, do not rerun.

2. Keep the original run/worktree untouched while preparing a separate clean-worktree adapter and focused synthetic tests. No hot-patching, debugger injection, indefinite SIGSTOP, shared-output writes, or large native pool beside the serial run. No new VM/resize.

3. Implement exact planner, frozen-parent extra-cache importer, bounded spawn process pool, coordinator global budget/cancellation, and strict CacheOnlyProvider. Worker-local native initialization after frozen source/library/BUILD checks; OMP/OPENBLAS/MKL/NUMEXPR remain1 per worker. One query per worker assignment, original ordered qualification ladder unchanged. Private worker ledgers/task directories; coordinator validates before canonical create-only commit. Conflicting same-ID payloads block, never silently overwrite.

4. Do NOT multiply8470 by worker count. Use atomic coordinator-wide raw-attempt reservation/accounting including old serial attempts and new validation/compute attempts. Bound in-flight tasks<=P. Future.cancel/shutdown(wait=False) does not stop running workers. Enforce a deadline on the whole dedicated process group/cgroup and verify descendants actually exit. Initial P<=8 within explicit current lease; larger16/32 only inside an approved CPU/RAM envelope after a small useful-work pilot. No blind worker sweep.

5. Focused non-native acceptance: exact time_hex and step widths against original traversal; partial/full/non-prefix cache sets; duplicate/conflict/orphan/nonfinite/context/hash failures; cache-only miss makes zero evaluator calls; shuffled synthetic completion preserves coverage and ordered replay; shared budget cannot overshoot; worker failure/cancel stops new dispatch; original source/OUT/nonce unchanged. These tests do not replace native parity. Plan a bounded parity comparison on about2 existing frozen query IDs and record the maximum raw-query budget in the authorization.

6. Before stopping, recheck M and break-even. Present one MIGRATION_READY request with actual parent run/auth IDs, new prepared execution commit/tree, unchanged numerical dependency manifest, CPU list/worker/RAM cap, bounded parity scope, global raw cap and remaining original wall/cost. Ask once for controlled stop plus one missing-only native migration. Do not treat this research prompt or standing backup permissions as permission to reuse the consumed nonce. Do not automatically reset the budget to10h/50000KRW. Bind new migration authorization to the parent; retain the old consumed record. After explicit approval, execute within that scope without repeatedly requesting the same approval at each step.

7. Controlled stop only after approval. No cooperative query-boundary hook exists in the original process: watching a new JSON then signaling can still interrupt the next query. SIGTERM first to the verified target; preserve its first failure and enforce only the approved grace/termination scope. Never broad pkill/killall, kill the Codex window, or terminate other sessions. Verify actual child/descendant exit, not just supervisor exit. Preserve original R4C_BLOCKED/InterruptedError and explain planned migration in an external sidecar. A prior real scientific qualification failure remains a separate blocker.

8. After exit freeze existing bytes with manifest: source/native/env/admission/nonce/process/exit/logs, completed JSON+NPZ hashes, orphan/partial inventory. Revalidate schema/context/time/query-ID, payload hash, shape/finiteness and ordered adjacent-pair qualification from payloads. Copy only admitted pairs, byte-preserving; keep quarantine evidence separately. No final ZIP does not justify inventing a completed return. Keep the original archive intact and record extra-cache IMPORT_BRIDGE lineage.

9. Under the new approved migration, run the bounded parity first, then4-8 missing query useful-work pilot whose results are retained. Parallelize ONLY remaining required IDs; no successful expensive query re-computation except separately bounded validation. Once canonical coverage770/770 is frozen, replay unchanged run_candidate(768) from original initial state using a reader with NO native evaluator and immediate CACHE_MISS failure. Do not call unchanged fallback-capable provider and assume it is cache-only.

10. Return HOST_CENSUS, MIGRATION_DECISION, STOP_RECEIPT, FROZEN_PARENT_MANIFEST, IMPORT_BRIDGE, exact required/missing plan, new code/admission/parent-auth linkage, combined raw-attempt ledger, worker/resource/parity receipts, query pairs, CACHE_ONLY_REPLAY_AUDIT(native_calls=0), CANDIDATE_N768, TEMPORAL_PAIR, PROVIDER_AUDIT, RETURN_REPORT, MANIFEST and actual portable ZIP. Preserve first failure/partials on timeout. No automatic retry/new nonce/N1536.

Frozen ceilings: capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO; original_capture_gap_resolved=false; continuous_global_supremum_bound=false. N768 dual PASS contradicts the frozen R4D triangle condition and must be investigated, not admitted.

Small evidence/code can be non-force published on a separate branch; no automatic merge. Native NPZ files go in create-only dual-provider artifacts, not duplicated in Git. Lack of credentials requires returning actual ZIP bytes, not merely a /root path. Do not stop/delete/resize the shared VM; process timeout is not a billing stop.

## Complete research package

Filename: BASS_CR_R4F_CACHE_PRESERVING_PARALLEL_MIGRATION_20260929_v1.zip
Bytes:68191
SHA256:a3e975447b53f280d0424f503afa039981de81c7bc0e1ad7d00f8dc0c18c6206
Contents: full Korean research design, detailed live-window handoff, read-only probe_plan.py, arithmetic evidence,770-entry required plan, status and manifest. This is NOT an implemented production runner.
Google Drive object:1uYKrXk75z4kRaB2kOFYmNKIkLdsvyKXM
Backup acknowledgement is recorded separately; no restore claim is inferred from upload.

Sources: pinned metric_transport.py, qualified_provider.py, analytic_adapter.py, continue_temporal.py, execution_admission.py and frozen archive; Python3.12 official multiprocessing/signal/concurrent.futures documentation; GNU timeout manual; NCP official FAQ223. Python signals can interrupt after C returns, and terminate can corrupt shared IPC; these motivate private durable task records and explicit process ownership.
