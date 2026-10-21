# C21K bounded all-pending campaign packet

## Status and scope

This packet is prepared code. Actual NCP host allocation has not been observed, and this packet has started **zero native scientific jobs**. Native performance is **NOT_EVALUATED**. The existing scientific HOLD and `global_error_bound=null` remain in force.

`BACKLOG_INVENTORY.json` is the exact V3 inventory. The fixed scientific grid has 52 logical slots: H8, I16, G12 and K16. Three immutable returned native results already completed H common_ic/VigilODE base and I common_ic/VigilODE/vectorized base plus fd_half. Nominal pending49 comprises historical pending21 and the current user's operational extension28.

| Lane | Historical complete | Nominal pending | Contract |
|---|---:|---:|---|
| H | 1 | 7 | Original two methods, two fixtures, base/FD |
| I | 2 | 14 | Original vectorized/vectorized_exact modes, two methods, two fixtures, base/FD |
| G | 0 | 12 | Original standalone campaign: eight references and four internally gated histories |
| K | 0 | 16 | Published vectorized/vectorized_exact epoch modes, two methods, two fixtures, base/FD |

The duplicate I baseline audit grid is excluded. No new physics slots, Full48 expansion, backend integration or tolerance changes are added. H/I and I/K comparison relations are soft evidence links; only the original same-lane, same-mode FD base is a hard dependency. A failed comparison lane does not stop an otherwise independent base. G remains independent and retains its own numerical gate.

One unchanged G process contains up to12 nested scientific jobs. Thus nominal pending49 corresponds to **38 top-level pending processes**, plus three external evidence nodes. G exit0 or `PARTIAL_OR_REFERENCE_HOLD` cannot be reported as completion of all12. Its eight references and four conditional histories remain separately reported; original source and receipts govern the numerical gate.

## Exclusive changed-dependency controls

The current authoritative scope is `DEPENDENCY_CONTROL_SCOPE_DECISION.json`. The earlier `FD_CONTEXT_REPAIR_ADDENDUM.json` described only the path branch. Its bytes were not recovered after workspace pruning; the exact recovered control decision is the current authority.

| Verified current inputs | Added controls | Maximum new attempts | Pending top-level processes |
|---|---:|---:|---:|
| Historical native/bridge bytes and matching H FD context | 0 | 49 | 38 |
| Same bytes; canonical H manifest/bridge/native absolute paths differ | 1 H base | 50 | 39 |
| Valid new native or bridge build under unchanged source/owner pins | 3: H base, I vectorized base, matching I vectorized FD | 52 | 41 |

The three-control branch includes the H repair, so it never adds a fourth control. Each control is identified before execution, has its own create-only output directory, and may be attempted once. It is a changed-input control, not a failure retry. Historical receipts and payloads are never rewritten. Different build bytes retain historical COMPLETE evidence without claiming matching current-build reuse. Source or owner pin changes fail admission.

Nominal conditional jobs are FD19 plus G histories4. The changed-build branch adds one FD control, giving FD20; the maximum attempt bound then becomes52. Canonical path resolution avoids controls caused solely by symlink, trailing slash or `..` spelling.

## Inputs and source binding

Use two detached checkouts:

- I execution checkout: `fe6bbaec2de5032b938aed0713623b9618ba70e6`. G and H run from the unchanged, manifest-verified G/H bytes inherited by this checkout. Their historical source-content provenance is distinct from the actual fe6 execution checkout.
- K execution checkout: the exact **content_commit** in the real external PUBLISHED K receipt. A later document head is not substituted for executable content.

The builder verifies detached HEADs; fixed H/I/G manifest hashes and full recorded runtime/baseline closure; committed K contract/coordinator blobs; the actual H→I→K publication chain; native identity and bridge build provenance. It records scheduler, builder, inventory and control decision hashes in `input_files`. Changing a prepared source or input causes admission failure.

Copy `SITE_BINDINGS.example.json` outside both checkouts and replace every placeholder with a real absolute path. All three publication receipts must be outside the execution checkouts. The receipt-named admission copies prepared below must remain complete: the original receipt SHA and its entire payload inventory are checked.

Prefer an existing verified native binary or a byte-identical restored PR82 artifact:

- Native SHA256: `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`.
- Returned bridge SHA256: `717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30`.

Do not assume either artifact or Rust is currently present. The original locked build procedure may supply a valid replacement. For a rebuilt native binary, add optional `native_build_dir` as a real absolute path containing `native_point`, `owner_commit.txt`, `build_exit.txt`, `input_sha256.txt` and `owner_source.tar`. Original G `verify_native_binary` admits the recorded pinned-owner build; no invented `NATIVE_BUILD_RECEIPT.json` is required. A bridge requires the original H build receipt matching its actual binary, all three pinned Rust source records, the fixed VigilODE commit and Diffsol version, and successful build exit.

Original build scripts and the project build/restore guide govern compilation and runtime dependencies. Compilation is a distinct preparation stage; it does not use scientific job leases or convert build success into scientific completion. The packet implements the full scheduler and controls here; it does not ask NCP to design a new backend.

Optional `g_reuse_directories` is a list of canonical absolute prior G campaign directories. Original G's own complete-payload, signature and input admission decide whether reuse is valid. A path-only claim or an exit code alone does not suffice.

## Prepare exact historical admission copies

The immutable original native tar contains one `runner_exit_code.txt` wrapper sidecar in each returned job directory. That sidecar is outside the original receipt's payload inventory. Direct extraction and the smaller replay-only materialization both fail the unchanged exact-payload gate.

Before binding the campaign, create a separate admission root with the included narrow helper:

```bash
python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/prepare_historical_evidence.py \
  --archive /absolute/restored/C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz \
  --out /absolute/new_historical_evidence_admission
```

Set `SITE_BINDINGS.json` → `native_return_evidence` to that new output root. It contains the three original job-directory names and one root `STAGING_RECEIPT.json`; staging metadata stays outside the per-job directories. Do not bind the direct tar extraction or replay-only directory.

The helper requires the original archive's 2,568,680 bytes and SHA256 `2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3`, the pinned backlog inventory and its exact three receipt pins. It rejects unsafe paths, duplicate archive members, links and special members. It verifies all113 receipt-named payloads before creating output, copies those bytes and the three receipt bytes verbatim, and invokes unchanged `scheduler.verify_external` on all three jobs. It rechecks the original archive hash afterward.

Only the known three wrapper sidecars are absent from these admission copies. They remain unchanged in the original tar and their identities are recorded in the staging receipt. The original tar, original receipt and native raw are never rewritten or deleted. This preparation does not make a relocated old base automatically satisfy the original FD context guard; controls0/1/3 still apply.

Actual focused validation: one successful preparation of three jobs/113 payloads/three receipts, followed by one separate call containing two negative tests (create-only rejection and one-byte archive tamper rejection). Scientific/native calls and old-suite reruns were zero. Public audit and exact raw tool outputs are in `validation/HISTORICAL_EVIDENCE_*`; private LIVE inventory contents are not printed there.

## Preparation and execution

The examples below use operator-defined absolute paths. The example allocation is deliberately invalid until actual ownership, resources and expiry are supplied. Preparing a manifest does not execute jobs.

```bash
python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/make_campaign.py \
  --bindings /absolute/outside/SITE_BINDINGS.json \
  --out /absolute/outside/CAMPAIGN.json

python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/scheduler.py \
  --manifest /absolute/outside/CAMPAIGN.json
```

The actual NCP host must be read before filling the allocation:

```bash
python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/scheduler.py \
  --inspect-resources
```

Fill `OWNER_ALLOCATION.example.json` outside the checkout with the current host fingerprint, explicitly granted CPU IDs, future expiry, positive measured or conservative worker/coordinator RSS budgets, and a lease directory shared by cooperating jobs. This record is an owner allocation; advertised64 CPU/128GB specifications and an online device listing are not substitutes.

```bash
python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/scheduler.py \
  --manifest /absolute/outside/CAMPAIGN.json \
  --allocation /absolute/outside/OWNER_ALLOCATION.json \
  --out /absolute/new_unique_campaign_output \
  --execute
```

Only an identical manifest may resume an existing output:

```bash
python -B /absolute/K_checkout/research/cr_c21k_epoch_cache_campaign_20261021/ncp/scheduler.py \
  --manifest /absolute/outside/CAMPAIGN.json \
  --allocation /absolute/outside/OWNER_ALLOCATION.json \
  --out /absolute/existing_campaign_output \
  --execute --resume
```

Successful attempts are reused only after exact signature, payload inventory and scientific receipt checks. Failed, interrupted, timed-out or incomplete reserved attempts are terminal and are not automatically retried. This resume is not permission to rerun historical completed jobs. Original G can separately reuse valid prior nested results through its unchanged contract.

Running the builder without `--bindings` produces an explicitly **UNBOUND_NOT_EXECUTABLE** template. It is useful for reviewing all commands and DAG relations; it cannot launch.

## Resource and bounded-process admission

The coordinator intersects the granted CPU IDs with current affinity and visible cgroup CPU masks, removes CPU55, and accounts for the visible CPU quota. One leased CPU is reserved for the coordinator. Every worker receives one separate CPU lease and affinity, and one-thread BLAS/OMP/NumExpr/Rayon settings. Current independent ready jobs determine useful width; a single coupled ODE is not split across64 cores.

Visible RAM constraints and current availability bound concurrency. Reserve is max(1GiB,12.5% of actual constrained memory), hence at least16GiB for128GiB. The coordinator has its own RSS budget. Full worker RSS budgets are reserved for every active process before children grow; sampled owned process-group RSS exceeding the worker budget terminates that attempt. This is conservative admission and monitoring, not an external kernel guarantee against unrelated host activity.

This implementation requires Linux cgroup v2, child-subreaper support and reliable same-user `/proc` ownership observation. Cgroup v1 fails explicitly. After a valid owner allocation and coordinator lease/pin, a bounded non-scientific child checks the actual marker reader **and production owned_processes/process_identity observer**, stable start ticks and valid live RSS. If that gate fails, no scientific job is launched. The capability child also excludes protected CPU55 because it inherits the admitted coordinator affinity.

Each job inherits a unique ownership token. Cleanup uses only the matching token and observed process start ticks, covers children that create new sessions, and never scans or prints environment contents into receipts. A child left after a successful leader exit makes that attempt fail. Tests explicitly preserve an unrelated subprocess. This does not authorize terminating other NCP work.

H/I/K coordinator deadlines are300s per attempt and retain original native call limits and remaining-time caps. G uses its unchanged per-job policy inside one3660s outer container. The outer campaign is bounded to21600s or allocation expiry, whichever occurs first. Original runners remain authoritative for fixtures, scales, tolerances, FD identity and native budget.

## Receipts, validation and limits

Every new attempt receives a durable reservation, stdout/stderr, original runner payload, coordinator receipt with source signature, CPU, wall time, exit/timeout status, payload hashes, cleanup outcome and observed RSS. The campaign return distinguishes independent statuses, scoped G HOLD, soft comparison availability, publication and backup. Execution does not publish or back up automatically.

`RECOVERY_RECEIPT_20261021.json` preserves the known history of early14 PASS, the23-test error/7 skips, the24-test two-failure run, and the later24 PASS. Their original full raw and `validation/VALIDATION_HISTORY.json` were not recovered. The subsequent33-test PASS and targeted1-test tool returns were recovered from the original tool messages in `validation/ATTEMPT_05_*` and `validation/TRACKER_GATE_FOCUSED_*`, with source identities in `validation/SOURCE_VALIDATION_SNAPSHOTS.json`. After review, a separate focused1-test call validated rejection when marker text is readable but the production ownership tracker cannot observe the child. These are separate actual calls; there is no claim that a34-test full suite was executed.

The sandbox denies child `/proc/environ` and has a virtualized process view. Local subprocess tests therefore use explicit ownership/start-time doubles while exercising actual subprocesses, CPU affinity, thread environment, signals, timeouts and setsid descendants. Matrix0/1/3 tests use preverified admission doubles. Actual NCP ownership observation, bound native preparation, new scientific execution and measured speedup remain unverified here. The production gate must pass on the real allocated host.

`NCP_CODE_MANIFEST.json` is a newly written RECOVERED_PACKET manifest of the currently present files, excluding itself. The original 34-payload manifest identity is recorded as historical NOT_RECOVERED; it is not claimed to match this new manifest. Core source3, tests3 and mandatory planning2 match their original hashes exactly. Publication, backup and research-DAG receipts are separate root closeout stages. Current exact scientific HOLD and `global_error_bound=null` are preserved.

