# Final independent static code review after targeted repairs

Reviewer: `/root/source_handoff`  
Scope: changed certificate checks, native `nb` gate, threshold metadata, and the complete-cross-support direct witness path  
Method: read-only source/receipt inspection and mathematical reasoning  
Reviewer scientific execution, NPZ loads, tests, numerical experiments, and owner-branch modifications: **0**

## Static decision

**PASS_SCOPED_STATIC_CODE_REVIEW.** Findings C01 and C02 from `CODE_AUDIT.md` are closed in the reviewed source. The optional threshold consistency issue C03 has also been corrected. The added complete-cross-support constructor preserves the exact graph, source marginal, maximum cross objective, and original native consumer gates.

This is the final *static* review of the source identities below. It is not a substitute for the parent-owned independent saved-certificate runtime result or final scientific admission. The earlier `CODE_AUDIT.md` remains unchanged as the record of the original findings and reviewed source.

## 1. Exact reviewed identities

Root: `/workspace/scratch/41a5b08c0439/bass_cr`.

| File | Reviewed SHA-256 |
|---|---|
| `research/cr_he_energy_cross_20261028/implementation/cross_envelope.py` | `653a3011bbcf6af115c4f55ebb4035a46020d72c3e8e5d43fcb3f95fd4e028d3` |
| `research/cr_he_energy_cross_20261028/implementation/cross_flow.py` | `3bac2933c6b0b2c3de5fe28c05472ac5ad3e02afca57fb30566e27f051f7585f` |
| `research/cr_he_event_union_20261028/implementation/event_union.py` | `6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d` |

The envelope and flow hashes match the actual `recover_v2/SOURCE_MANIFEST.json`. The flow solver and original event-union consumer hashes are unchanged from the preceding static review. Their earlier proof-to-code analysis is therefore reused; no broad re-audit or scientific replay is claimed.

## 2. Closed findings

### C01: exposed min-cut dual verification — CLOSED

The flow-backed branch of `verify_primal` now checks:

- number of min-cut dual entries;
- unique keys equal to the complete atom set;
- each label is an exact scalar in `{0,1/2,1}`;
- every allowed cross-edge inequality through partition/label-group minimum energies;
- exact weighted dual objective equal to the primal `C`;
- retained equality `flow_value=mincut_capacity=2C`.

For two different partition/label groups with dual labels summing below 1, an allowed edge exists if and only if their minimum energies sum at most `K`. Thus the added check covers all such edges, including zero-mass vertices, without sampling. Altered or infeasible auxiliary min-cut duals can no longer receive this proof path's PASS.

The existing formula dual and exact atomwise primal witness still provide the primary optimality proof. The auxiliary min-cut dual is now an actually checked additional certificate rather than unchecked displayed metadata.

### C02: explicit native baryon density — CLOSED

`consume_native` now requires

`exact(nb_m3) == NB`

before native source consumption. `None`, float, bool, and wrong exact values are rejected by this wrapper. The retained same-state value is `NB=8750/47`. The original consumer remains byte-identical and still performs its own `nb` verification and once-only conversion.

### C03: threshold metadata consistency — CLOSED for the scientific threshold fields

`verify_bound` now requires that a nonempty independent set's reported partition and minimum energy are actual atom levels, that finite `h` is an actual outside level satisfying `h>=e` and `h>K-e`, and that the two reported threshold tails reconstruct exactly the checked independent set. Empty independent sets require all three threshold metadata fields to be null.

This validates the construction metadata without rerunning the maximizing suffix sweep. Network diagnostic counts remain diagnostic rather than an independently re-executed network transcript; the static review does not describe them as additional scientific certificates.

## 3. Complete-support witness: conditions and construction

The new `complete_support_witness(source,bound)` is a specialized attaining-witness constructor. It does not change the suffix formula or the compact general flow solver.

### 3.1 Guard is sufficient for every cross pair

The function first uses the pinned native source validator and `verify_bound`. It computes the maximum energy in each occupied partition and requires

\[
 M_r+M_s\le K\qquad(r\ne s).
\]

For every atom pair in distinct bins, `E_i<=M_r` and `E_j<=M_s`, so this condition proves that every cross-bin pair is permitted. The test includes all atoms, including zero-mass ones; it is conservative and mathematically consistent with the declared full graph. The half-shift path is not invoked on a partially excluded cross graph.

### 3.2 Reuse is the actual pinned predecessor function

The constructor invokes `previous.half_shift_lift(source.atoms)` from the byte-pinned `event_union.py`. That function sorts the mass intervals into contiguous partition blocks and pairs mass coordinate `u` with `u+N/2`. It preserves the complete source marginal, including atoms that split across block boundaries.

On complete cross support, the cross mass of this construction is

\[
 \min(N/2,N-n_{\max}).
\]

If every partition mass is at most `N/2`, opposite points cannot both lie in the same partition except for null endpoints. If one partition is larger than `N/2`, every outside leg is paired with the large partition and contributes cross mass `N-n_max`; the remaining pairs lie within the large partition. This is the already established complete-bin result, applied only after the full-cross-support guard.

### 3.3 Filtering preserves the intended cross objective

The new function keeps only pairs whose endpoint partitions differ, combines repeated unordered atom keys, and computes each atom's used cross leg mass. It then emits its exact remaining marginal as a single.

Removing a same-bin double removes both of its legs from the double measure; restoring the two resulting leg masses as singles preserves the full marginal. No residual leg is silently treated as an allowed diagonal double. Thus the resulting witness has

\[
 d=C,\qquad s=N-2C,
\]

and no same-bin pairs. The direct path has the same cross-event objective and same conditional feasible graph as the original `K=20` request. Its particular atom pairing may differ from a flow witness, which is permitted because this unit specifies an envelope and an attaining conditional witness, not an identified exclusive kernel.

### 3.4 Existing exact verifier remains mandatory

The function finishes by calling `verify_primal` against the original bound. This checks every pair's distinct-bin and cap condition, every exact atom marginal, all residual singles, and exact primal equality to the separately checked formula dual. If filtering failed to attain the claimed bound, or overused any atom, the function would fail this verification.

The complete-support theorem therefore gives the construction rationale, while the explicit events and dual equality provide independently checkable finite evidence. No tolerance, source weight, cap, inventory, or physics assumption was relaxed.

## 4. Direct construction does not fabricate flow evidence

`ConstructedWitness` explicitly sets

- `method="PR112_HALF_SHIFT_FILTERED_CROSS"`;
- `flow_value=None`;
- `mincut_capacity=None`;
- `mincut_dual=None`.

The direct branch of `verify_primal` requires the exact record type, exact declared method, and all of those null flow/min-cut fields. It returns `flow_min_cut="NOT_PROVIDED_DIRECT_PRIMAL_CERTIFICATE"`.

This branch is entered only after atomwise marginal, support, and formula primal/dual equality have been checked. A missing flow certificate is therefore an accurate statement of the chosen proof method, not a waived optimum check. A flow-solver record with null fields cannot impersonate this direct record type.

The independent saved-certificate evaluator must use these explicit method/null fields to distinguish the two proof paths. Its actual execution/admission is a separate parent-owned obligation; this static review does not infer its outcome.

## 5. Native consumer and physical scope are retained

The changes leave the source validator, actual NPZ attestation, original atom content, cap identity, and original consumer module unchanged. The endpoint continues through

`binding -> claims_by_partition -> consume_event_union`

with the original named `nb_m3` and `previous_windows` arguments.

The original proper-window factor is applied once. The source-parent inventory condition

\[
 W(N-d)\le (1085/94)(99/100)
\]

remains enforced by the original consumer; the direct cross witness has `d=C`. Source/partition event identity, complete selected marginal, non-overlapping time history, original fixed-volume frame, and same-state baryon density remain independently checked.

The new result keeps actual physical `K`, actual `C`, actual `D`, full physical native25, donor work, EOS/T, and physical activation in their inherited null/false state. It explicitly states that the witness is cross-only and is not a fixed-total-`d` Pareto result. RR and retained photons remain separate once-only ports.

## 6. Recorded targeted and recovery evidence read

The following are existing parent-run records read by this reviewer, not new reviewer executions.

### Targeted finding checks

`runs/targeted_v1/RESULT.json` records eight expected rejections:

- missing, infeasible, wrong-objective, and float min-cut duals;
- null and incorrect native `nb`;
- false threshold partition and false threshold energy.

It also records a positive exact optimum of 2, and explicitly states that the unchanged 116 small cases were not replayed. Its receipt is PASS with charge `0.135582 CPU-s` and unchanged source.

### Preserved unsuccessful attempts

`runs/native_v1/RECEIPT.json` remains FAIL with `WORKER_EXIT_-9`, a 22 CPU-s reservation, measured `23.874731999999998 CPU-s`, and charged `23.924732 CPU-s`. The completed case checkpoints are distinct from the aborted job's final status. This receipt does not invalidate an already completed certificate by itself; reuse still requires the independent saved-data verification. It also does not become PASS merely because a specialized later constructor succeeds.

`runs/recover_v1/RECEIPT.json` and stderr preserve the worker syntax error `positional argument follows keyword argument`, with charged `0.069671 CPU-s`. This is an implementation/execution failure before the intended recovery result, and remains separately charged.

### Targeted recovery

`runs/recover_v2/RESULT.json` records `PASS_TARGETED_NATIVE_RECOVERY`, eight reused cases, one new case, and `previous_failure_preserved=true`. Its receipt is PASS with charge `1.414403 CPU-s`, unchanged source, and the exact current envelope/flow identities stated above. The new exact `K=20` cross coefficient is preserved as a Fraction string in that result rather than reconstructed by this review.

No generic-flow performance success at `K=20` is implied by the direct recovery. The accepted recovery claim concerns the specialized exact attaining witness and its verification under complete cross support.

## 7. Final finding state and remaining evidence

| Finding | Current state | Basis |
|---|---|---|
| C01 auxiliary min-cut dual unchecked | CLOSED | Static all-edge/domain/objective checks plus targeted rejection records |
| C02 nullable `nb` native endpoint | CLOSED | Wrapper exact equality plus targeted null/wrong rejection records |
| C03 threshold metadata not checked | CLOSED for threshold fields | Direct metadata-to-independent-set reconstruction plus targeted mutations |
| Complete-support direct construction | STATICALLY SUPPORTED | Full-cross guard, pinned half-shift construction, residual singles, explicit optimum certificate |
| Generic `K=20` flow performance | FAILED ATTEMPT PRESERVED | Original native receipt remains FAIL; no performance claim promoted |
| Full independent saved-certificate admission | SEPARATE RUNTIME OBLIGATION | Parent-owned evaluator/result and final reviewer decision must be read before scientific closeout |

There is no remaining blocking static finding in the reviewed production files. The parent should preserve the original failures, targeted evidence, current source identities, and independent saved-certificate outcome in final admission. This review authorizes no additional scientific replay and transfers no prior or foreign budget.
