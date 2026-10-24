# BASS_CR N5 CE child — central intake patch proposal

Status: read-only intake and local proposal. No GitHub mutation has been performed by this task. The new child result identities, measured values, review decision and delivery receipts must come from the parent's completed return; the accompanying draft is not an admission record.

## Observed central state

- Repository: `cosmosapjw-quantum/rei_bianchi`.
- Branch: `research/orchestration-sandbox-20261022`.
- HEAD, independently re-read at `2026-10-24 03:22:28 UTC`: `3fba7cd91f84b4687cf6356f87400056ca32e37e`.
- HEAD tree: `2c3e73ed14ee0e8682b25cf5897cef47066e7e26`.
- Root `AGENTS.md` was read. `research/AGENTS.md` returned 404; listings of `research/orchestration_longterm_20261023`, `assembly`, and `assembly/returns` contain no nearer `AGENTS.md`.
- DAG contains 40 node wrappers, 40 embedded original contracts, 7 embedded authorities and 17 integration edges. The separate `authorities.json` contains the source manifest and must not be conflated with the seven embedded authority objects.
- `CR_N5_ATOMIC_ISOTOPE_COVERAGE` is node index 8 in this snapshot; its `plan_status` is `PARTIAL`. Its original contract still records `OPEN` / `NOT_RUN` as an immutable planning snapshot.
- N5 `observed_progress` records the completed C23E D43K source-binding child and its actual science commit `8e4e06361d714939513a11f64a27f02822bde2fa`, Draft PR100, results, budget and scoped review. It has no `additional_children` field.
- HE-ANG is node index 19, remains `SOURCE_INPUT_PENDING`, and already contains the PR94 measured DDCS window subunit. Existing HE authority, return and backup observations are outside this patch's ownership.
- `HANDOFF_bass_cr_KO.md` currently has a C23D overlay, the original contract list and a terminal C23E section. C23E is also recorded in the DAG and its return JSON. Append the new child after the existing C23E section without rewriting those records.

Exact retrieved file bytes, Git blob IDs and SHA256 values are listed in `SOURCE_INDEX.json`; all six local files reproduce the source Git blob IDs. `raw/dag.json` is an input snapshot, not a proposed replacement.

Local source materialization correction: an initial write of `raw/handoff.md` contained only the first 12000 characters (13146 bytes). The final input check detected this mismatch against the 16602-byte source, and the omitted exact suffix was appended from the already retrieved full tool response. The restored payload matches the original Git blob. An intermediate statement that the handoff lacked C23E was consequently withdrawn; the central source never had that omission.

## Smallest central change: three paths

| Path below `research/orchestration_longterm_20261023/assembly/` | Smallest change | Ownership |
| --- | --- | --- |
| `returns/CR_N5_PROVIDER_RATE_SEMANTICS_AND_CE_ENVELOPE_20261024.json` | Create one actual reviewed child return. Resolve the accompanying draft's pending identities and measured values from the parent's artifacts. | New BASS_CR N5 scoped child only |
| `DAG.json` | Find node by exact `id`; append one child reference inside `observed_progress.additional_children`. The field does not exist in the observed base and can be added as a one-element array. | One additive N5 observed-progress field |
| `HANDOFF_bass_cr_KO.md` | Append one dated section describing the new child, its actual evidence and the remaining gates; cite the already completed C23E return. Preserve existing bytes as the prefix. | Additive BASS_CR handoff text |

No fourth path is necessary. In particular, do not update `authorities.json`, original contracts, integration edges, source-owner returns, global schema/as_of/scope, or other wrappers. Do not add a 41st top-level DAG node. Do not rerun `assemble.py`: rebuilding would risk replacing additive observations and owner updates.

The child ID is `CR_N5_PROVIDER_RATE_SEMANTICS_AND_CE_ENVELOPE`; its parent stays `CR_N5_ATOMIC_ISOTOPE_COVERAGE` with `PARTIAL` / full coverage OPEN. The existing C23E object remains in place. A new nested list is preferable to converting the original object into a different schema or replacing its `child` field, because it preserves all existing consumers of that original return.

## Target field and parallel change handling

At this exact base the new field is `/nodes/8/observed_progress/additional_children`. This numeric pointer is a snapshot aid only: resolve the node by exact ID again on the then-current HEAD. `PATCH_PROPOSAL.json` records the semantic selector and the base-specific test conditions.

Before any central publication, re-read branch HEAD. If it has advanced, obtain the current DAG and handoff and add only the owned child entry and appended section. Preserve any new `additional_children` entries already there; deduplicate the exact child ID and compare an existing same-child identity rather than replacing it. Never overwrite a concurrent N5, HE or other owner observation with this snapshot. Re-read the applicable AGENTS if their blob identity has changed.

Publish against the then-current expected SHA with the normal non-force compare-and-swap procedure used by the project. If the expected SHA changes, repeat the narrow merge; do not force the old DAG into the branch. This proposal does not itself authorize or perform publication.

## Required payload semantics

The new return must distinguish (a) thermal Maxwellian rate coefficients and their target-owned event rates, (b) tagged-electron CE hazards, and (c) an EE-only first-entry clock. It must identify the fixed additional ground-state closure `n_H(1s)=0.9 cm^-3`, while unsupplied 2s/2p populations and missing other processes stay null.

The existing C23D `0<W<10 eV` describes initial selection, not the entire EE trajectory. The CE maximum used with the `80 kBT` MFPT must cover the full admitted path interval, up to approximately 68.94 eV at 10000 K. Source-subthreshold CE closure therefore does not imply zero CE throughout the stopping path. Reuse existing C23D MFPT values; record the result as a conditional finite-band numerical first-event diagnostic, not an irreversible assimilation, energy deposition fraction, or certified full-process stopping result.

The positive finite W-PL PHYS83 model permits a finite endpoint maximum over union knots and clipped domain endpoints. The return must report the actual computed maximum, location/domain, numeric evaluation allowance, units, input identity and assumptions. Source interpolation/model error is not certified by float-versus-Decimal checks. The conditional bound is `P_active <= 1 - exp(-h_max * mean_tau_active)`; apply the active fraction only for a selected-population statement. A CE-only bound does not bound the sum of missing non-EE channels, so the total non-EE bound is null.

PHYS84 remains numerical-admission WAIT; HE-ANG full law remains SOURCE_INPUT_PENDING despite the admitted measured window subunit. Reuse C23E's completed conditional source binding without rerunning or crediting it as new work. Preserve N4 full-stopping PARTIAL/OPEN, N5 PARTIAL/OPEN, and N6/N7 predecessor gates.

## Lightweight preservation checks after actual edit

1. Exactly the three owned paths changed. The new return is internally consistent with the parent's actual run, science/document identities, result, review and receipts; no draft markers or invented metrics remain.
2. Match DAG nodes by ID: all 40 original `contract` objects are semantically identical, all 39 other full wrappers are identical, and all 7 embedded authorities plus the complete integration object (including 17 edges) are identical to the current publication base.
3. For the N5 wrapper, remove only the newly added child entry/field from the edited version and compare to the current base. This preserves the original C23E `observed_progress`, N5 `plan_status`, dependencies, authority and original contract.
4. HE-ANG full wrapper, existing C23D/C23E return files and all HE return/backup files remain unchanged. No previously unknown Drive acknowledgement is promoted.
5. Handoff bytes before the appended section match the current base, and the new section states the actual four axes: EXECUTION | PUBLICATION | BACKUP | DAG.

`PRESERVATION_BASELINE.json` records semantic fingerprints for the observed snapshot so the parent can recognize the preservation boundaries. These are provenance aids for the narrow patch, not additional scientific gates. If HEAD moves, compare against the new base instead of demanding the old fingerprints.

## Four axes of this intake task

EXECUTION: read-only metadata and source inspection plus local proposal creation; no scientific ODE, quadrature, provider evaluation or replay. PUBLICATION: not attempted. BACKUP: parent-managed delivery; no new backup upload in this subtask. DAG: proposal only; observed N5 remains PARTIAL and no gate was changed.
