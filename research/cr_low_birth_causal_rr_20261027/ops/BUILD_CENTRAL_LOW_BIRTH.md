# Offline additive central builder

`build_central_low_birth.py` is a standard-library metadata helper. It imports no
scientific implementation, performs no new physical calculation, reads no ZIP,
creates no archive, invokes no Git command and makes no network request.
It adapts the retained prior-unit builder at
`8482ed83b14517b709ba6e801f6714cc333e720f`, Git blob
`8e94325515c72ad522cd225e72c5b5d8bb4cbfb1`; the prior file/state is unchanged.
This new source has only been authored and statically read, not executed.

## Exactly two candidate publication paths

The explicit `--output-dir` must not exist. Its only files are:

- `DAG.json`: the supplied current DAG plus one field
  `owner_return_low_birth_causal_rr_20261027` on the existing
  `CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE` node;
- `returns/CR_LOW_BIRTH_CAUSAL_RR_20261027.json`: exact bytes from the root's final
  `--owner-return` input, without normalization or invented findings.

The separate create-only `--proof-file` must be outside that candidate directory.
The candidate is a two-file patch, never a replacement central tree. The publisher
must freshly verify the central expected SHA and full base tree, require the new
return path to be absent, and apply only those two files with `force=false`.
The builder records that it did not verify the remote HEAD itself.

## Actual input requirements

The CLI requires `--dag`, `--owner-return`, `--central-head`,
`--central-count-baseline`, `--science-sha`, `--documents-sha`, `--source-r3`,
`--results`, `--output-dir`, `--proof-file`.
Git identities must be actual lowercase 40-hex SHA values; repeated-character
placeholders and mismatching S/D/current-parent fields are refused.
An unknown precommit `central_commit_M` is null and is supplied by a separate
postcommit delivery receipt later. There is no circular self-SHA placeholder.

### Current central count and preserved historical count

The current count comes from the required `--central-count-baseline` JSON input,
with schema `CR_LOW_BIRTH_CENTRAL_COUNT_BASELINE_V1`. The old27/88 is historical;
the helper no longer freezes it as the count for a future publication. No status
strings or status prefixes are counted. Required baseline fields are:

| Field | Required meaning |
|---|---|
| central_head | Exact actual `--central-head` |
| dag_sha256 | SHA256 of the actual supplied DAG bytes |
| original_DAG | Exact count object from the authoritative return |
| foreign_cause | `node_id` and `unit_id` of the existing scoped foreign cause |
| authoritative_return | `local_path`, `repo_path`, `revision`, `bytes`, `sha256`, `json_pointer` |
| historical_original_central_completed_total | `27/88`, retaining earlier stage/source history |
| unmerged_PR236_32_of_88_added | false |
| counts_inferred_from_status_strings | false |

The authoritative return is a pinned actual regular JSON file at that same
central revision. Its repository path, JSON pointer and selected value must
match the foreign node's current `status_observation` exactly. The return's
top-level `original_DAG`, selected observation's `original_DAG`, and baseline's
count object must all agree. Their explicit integer `before_completed`,
`completed`, `total`, `completion_count_effect` satisfy before+effect=completed,
with total88; `count_scope` remains explicit. This CR unit cannot be its own
foreign count cause. The authority input is included in the proof, collision
guards and unchanged-input recheck, without performing a remote query.

The observed central revision `74aff0740d1812c732466563a9c66108a3a4d8fd` declares
27→28/88 through the existing `B3h-native-finite-absorption` node and
`BASS_B3H_QSS_CHANNEL_COMPLETION_20261027` return. This is the foreign scoped
effect+1. The present CR link contributes0. The current28/88 is read from the
authority files rather than embedded as a fixed code value. Earlier stages1–15
and prior source units keep their27/88 records. Unmerged PR23632/88 remains
separate, and the global physical gates remain unchanged.

The source R3 input uses the actual common raw-reader envelope:
`archive={name,bytes,sha256,members,payloads}`,
`both_original_full_GET_and_all_members_PASS=true`,
`source_archive_rebuilt=false`, and two `providers` rows named Dropbox and Drive.
Each provider row must contain actual `id`, R3 tier, `raw_HTTP_method=GET`,
`HTTP_status=200`, `HEAD_or_Range_used=false`, `downloaded_original_file=true`,
`all_payload_sha256_and_CRC_PASS=true`, matching archive bytes/hash/member counts
and matching `manifest_sha256`. This validates saved receipt metadata and does
not pretend to perform a fresh download. Private signed-download URL/token
fields are refused.

The results input is a real metadata manifest with schema
`CR_LOW_BIRTH_CENTRAL_RESULTS_INPUT_V1`, `unit_id`, actual `science_commit_S`,
actual `documents_commit_D`, and explicit `files` descriptors. Required roles are
`primary`, `controls`, `independent`, `execution_ledger`, `execution_budget`,
`final_review`.
Every descriptor supplies:

| Field | Required meaning |
|---|---|
| role | Unique role, with the six required roles above present |
| local_path | Absolute actual regular JSON file to read |
| repo_path | Unique relative path under `research/cr_low_birth_causal_rr_20261027/` |
| revision | Actual S or D containing that evidence |
| bytes | Exact positive input byte length |
| sha256 | Exact SHA256 of the supplied bytes |

The final-review descriptor may include
`acceptance={verdict_pointer,blocking_count_pointer}` to name its actual JSON
fields. Defaults are `/verdict` and `/core_blocking_findings`. Its actual verdict
must begin `PASS_SCOPED`, its unit must match, and its blocker count must be zero
or its blocker list empty. This accommodates an actual review schema without
changing or inventing the review result.

The helper validates actual primary internal acceptance and four prefixes/bins,
control counts, independent PASS/check counts, explicit matching inventory/nb,
unchanged source JSON digest, and the separate failure-inclusive 40 CPU ledger.
It reads the canonical unique-attempt costs and preserves failed attempt IDs;
it neither recalculates source/response physics nor runs any test suite.

### Same-unit preparation costs

The `execution_budget` descriptor must pin the actual active
`research/cr_low_birth_causal_rr_20261027/EXECUTION_BUDGET.json` beside this helper's
unit, with status `FROZEN_C4_ADMITTED`, cap40 and both historical/parallel transfer
flags false. A preserved draft budget or another unit's allowance is refused.
The builder resolves the budget's `preparation_cost_manifest` within this exact
unit and verifies its bytes against `preparation_cost_manifest_sha256`.
The current active path is `evidence/C04_PREPARATION_LEDGER_V2.json`; the helper
does not hardcode its hash or incurred cost.

The manifest must name this unit and contain nonempty `records`. Every row has
`path`, positive `bytes`, `sha256` and nonnegative `charged_preparation_CPU_s`.
Each source must be a regular nonsymlink file inside this unit; absolute paths,
`..`, duplicate resolved paths and self-reference are refused. The actual receipt
JSON must name this unit, contain the same finite nonnegative preparation cost,
and carry no old or parallel transfer. Exact raw byte length and SHA bind every
row. Each actual cost must agree with its row declaration. Their Decimal sum must
agree with manifest `charged_total_CPU_s`, active budget
`spent_before_C4_admission` and execution ledger `baseline_preparation_cpu_s`,
using absolute tolerance1e-12 CPU s.
The ledger aggregate remains this verified baseline plus unique terminal attempt
debits; it is not reset to zero.

The existing four preparation receipts retain their 1.714435 CPU s history.
The actual C4v2 manifest additionally records the 0.22207 CPU s admission and
therefore pins a 1.936505 CPU s baseline. These observed numbers describe the
current receipts, not hardcoded acceptance values or a future worker total.
The manifest's explicit `all_resource_attempts_pass=false`, initial refusal and
receipt identities remain visible. An explicit failed `memory_gate` or nonempty
receipt `error`/`errors` cannot coexist with a resource blanket PASS. The validated
summary distinguishes worker-only acceptance from resource acceptance, and
`all_runtime_attempts_pass` requires both. The preparation input pins are included
in the proof, output-collision guards and final unchanged-input recheck.

## Required final owner-return bindings

The root's final return uses the normal unit/parent/repository/PR/S/D/current-base
fields, `unit_path=research/cr_low_birth_causal_rr_20261027`, and additionally:

- `source_R3_receipt_sha256` and `results_input_sha256` bind the two actual inputs.
- `central_count_baseline_sha256` binds the actual current central-count input.
- `original_DAG` fixes nodes88, integration_edges17,
  `declared_deliverable_count` equal to the current pinned count and new_count_effect0.
- `original_central_completed_total` equals the actual current count (currently
  `28/88`); `historical_original_central_completed_total="27/88"`,
  `unmerged_PR236_32_of_88_added=false`, `original_node_status_changed=false`.
  The last flag describes this CR candidate's changes against its supplied
  current base; it does not erase a foreign owner's earlier node completion.
- `scope_child` records exactly one completed child of one, with parent equal to
  the original external-source node and original_central_count_effect0.
- `workflow` records R10/10, C10/10, total20/20, twenty distinct actual published
  stage commits, twenty dual R2 stage receipts, and canonical source dual R3.
  Actual S belongs to that commit list and its final entry is actual D.
- `gates` retains N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4 false and explicit
  null global physical completion/error/budget remaining/currency.
- `review_decision` equals the actual final scoped review verdict.
- `verification` contains actual `new_controls_passed`,
  `independent_checks_passed`, `all_resource_attempts_pass` and
  `all_runtime_attempts_pass` matching the worker ledger and resource manifest.
- `execution` contains new_unit_cap_s40, exact charged_cpu_s, the actual ordered
  `preserved_failed_attempt_ids`, false old/parallel transfer, false automatic
  carry and false hard_preventive_aggregate_cap_proof. It also binds
  `baseline_preparation_cpu_s`, unit-local `preparation_cost_manifest`, its
  `preparation_cost_manifest_sha256`, and the actual ordered
  `preserved_failed_preparation_receipt_paths` from explicitly failed resource
  receipts. These are separate from scientific worker attempt IDs.
- `canonical_source_archive` binds actual science_commit_S, the same five archive
  identity fields, canonical_same_immutable_zip true and source_rebuilt_after_seal
  false. The actual ZIP name contains the actual S prefix.
- `source_evidence` contains exactly one matching path/revision/bytes/hash pin for
  every results-manifest descriptor.

`scientific_scope` is copied from the actual result's metadata, with these exact
keys: `source_record_sha256`, `selected_birth_tag`, `cumulative_prefixes`,
`disjoint_observation_bins`, `same_state_nb_m3`, `inventory_id`,
`rr_native25_scope`, `full_source_native25`, `source_parent_ion_chemistry`,
`physical_heating_completed`, `absolute_worldtube_totals`. Fixed values are the
accepted source SHA, direct_0p1_10, four/four, integrated_RR_event_only,
null/null/false/null; actual nb and inventory ID come from the saved primary.
Other narrative qualifications can be included outside this exact binding.

## Preservation proof

Input JSON numbers use `Decimal`; no binary64 float roundtrip rewrites old
scientific values. Sorted-key serialization changes formatting only. Removing
the one new link must restore exact canonical semantic identity of the entire
original DAG. The proof separately records all other 87 nodes, all 17 edges,
all non-node top metadata, the prior proper link, N5/HeIII link and entire current
B3h node. Original node order and status fields remain unchanged.
The proof records the current authoritative count and its scoped foreign cause
separately from historical27/88 and this CR unit's zero count effect.

All validation precedes output writes. Output creation is exclusive; byte
readback and JSON roundtrip preservation are checked, and all explicit input
files are rechecked for concurrent change. A partial I/O failure remains as
evidence and requires a new output path. No old candidate or receipt is replaced.
The final two-file candidate and proof require a different reviewer's inspection
before root publication. A static helper review is not candidate acceptance.
