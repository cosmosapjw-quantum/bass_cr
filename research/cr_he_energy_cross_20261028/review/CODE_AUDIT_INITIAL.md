# Independent static code audit: energy-constrained cross envelope

Reviewer: `/root/source_handoff`  
Method: source reading and direct mathematical/code-path reasoning  
Reviewer scientific execution, NPZ loads, test runs, numerical experiments, compilation, source edits, and owner-branch edits: **none**

## Decision at the reviewed snapshot

**Core mathematics and constructive flow path: NO_BLOCKING_STATIC_FINDING.** The suffix formula, complete-edge dual verification, compact prefix-chain network, iterative residual flow, exact flow disaggregation, symmetrization, and original event-union invocation agree with the declared problem.

Two narrow contract/certificate findings should be resolved or explicitly scoped before final admission:

1. `verify_primal` does not validate the exposed `solution.mincut_dual`; forged auxiliary min-cut dual metadata can pass that verifier. Its accepted maximum is nevertheless mathematically certified by the separately verified formula dual and primal event witness. If the exposed min-cut dual is claimed as an accepted certificate, independently check its keys, exact domain, all allowed edge inequalities, and weighted objective.
2. `consume_native(nb_m3=None)` currently reaches the original consumer's intentionally supported density-only/null-native path. The new unit contract freezes explicit `nb=8750/47` for its native endpoint, so the wrapper should require exact equality to `NB` before the call, or explicitly expose a differently named density-only path. Do not weaken or modify the original consumer.

These are code-reading findings. No failing runtime was created by this reviewer, and no claim is made that an already recorded default native call is wrong.

## 1. Reviewed identities and boundaries

Root: `/workspace/scratch/41a5b08c0439/bass_cr`.

| File | SHA-256 read during this review |
|---|---|
| `research/cr_he_energy_cross_20261028/implementation/cross_envelope.py` | `3660ca157ab35062a1b24ffdd7ac07f79ffb39c85bd773d8f76672c9729385b9` |
| `research/cr_he_energy_cross_20261028/implementation/cross_flow.py` | `3bac2933c6b0b2c3de5fe28c05472ac5ad3e02afca57fb30566e27f051f7585f` |
| `research/cr_he_event_union_20261028/implementation/event_union.py` | `6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d` |

The new `CONTRACT.json` was also read. It fixes every different-partition pair satisfying `Ei+Ej<=K`, exact divisible rational masses, explicit same-state `nb=8750/47`, maximum cross objective, sparse primal attainment, and the unchanged source/consumer pins. Arbitrary bin-mask graphs and fixed-`d` Pareto claims are excluded.

The root's previously identified `claims_for` name mismatch has already been corrected in the reviewed source to the actual `claims_by_partition` function. The reviewer found the corrected call in place; no scientific execution was used to discover or verify that correction.

## 2. Formula and exact input path

`cross_flow.validate_atoms` normalizes a finite list/tuple to base `Atom` records, rejects duplicate/empty keys, requires nonnegative integer partitions, and accepts only plain `int` or `Fraction` nonnegative numeric inputs. `bool`, float, nonfinite float, and string values cannot enter the exact core.

`cross_envelope.upper_bound` validates atoms and the exact nonnegative cap, then constructs inclusive prefix/tail sums. `_Cumulative.below_equal` uses `bisect_right`; `above_equal` uses `bisect_left`. Complete duplicate energy levels are retained through `levels=sorted(set(energy))` while their entire mass contributes to the prefix and tail.

For each candidate own-bin energy `e`, the code uses

`max(bisect_left(h,e), bisect_right(h,K-e))`.

This is exactly the required conjunction `h>=e` and `h>K-e`, with the correct difference between inclusive and strict boundaries. The suffix array's terminal `(0,None)` is the infinity/outside-empty candidate. Equal-score ties select an already valid later suffix candidate and do not alter the maximum.

The chosen independent set is reconstructed from the selected complete tails. Its exact open neighborhood is computed from minimum energy in each independent-set bin rather than trusted from the deficit scalar. The returned dual is 0 on the set, 1 on its neighborhood, and 1/2 elsewhere. Empty or zero-deficit cases use the empty independent set and all-half dual.

`verify_bound` checks the atom digest, exact mass/objective values, unique dual keys, labels in `{0,1/2,1}`, full independent/neighborhood identities, canonical labels, and the exact objective `(N-deficit)/2`. For every pair of different partitions and dual-value groups whose label sum is below 1, it checks that the two minimum energies sum above `K`. An allowed edge exists between those groups exactly when that minimum-energy sum is at most `K`; hence this covers every allowed cross edge, including zero-mass vertices, without sampling.

The `partition/e_threshold/h_threshold` fields are construction metadata rather than inputs to `verify_bound`'s proof. Their alteration would not invalidate the checked independent-set/dual proof, but would leave inaccurate threshold metadata. If these threshold fields are themselves advertised as checked certificates, add a cheap reconstruction comparison; the verifier need not rerun the maximizing sweep.

## 3. Compact network is equivalent to the full double cover

The flow solver creates source and sink, one `L_i` and one `R_i` per atom. Every source-to-left and right-to-sink capacity is the atom mass, after exact common-denominator integer scaling. The integer denominator is the LCM of the input rational denominators. This is exact scaling, with no rounding or constant-bit-cost claim.

For every right partition, atoms are ordered by `(energy,key)`. A chain points from each higher position to the previous lower position. A left atom connects to the highest energy-qualified right position in each *other* partition, determined by `bisect_right(K-E_i)-1`.

Following that entry arc and zero or more downward chain arcs reaches precisely the allowed right prefix. It reaches no higher-energy right atom and no right atom in the left atom's own partition. Therefore the compressed paths represent exactly the allowed full double-cover arcs.

All entry/chain capacities are `total_capacity+1`. Since the source-cut capacity is `total_capacity`, no minimum cut can cut one of these arcs. Equivalently, the total flow can never saturate such an arc. Thus the compression imposes no spurious finite bottleneck and preserves min-cut equivalence.

The network has `2n+2` vertices and

\[
2n+(n-k)+m_{\rm entry},\qquad m_{\rm entry}\le(k-1)n,
\]

forward edges for `k` nonempty partitions. This is `O(kn)` storage and specializes to linear-in-`n` storage for four bins. The implementation properly makes no linear-time claim for the iterative Dinic solver.

## 4. Residual solver and min-cut reasoning

The `_Edge.reverse` indices match the opposite adjacency entry. A forward edge records both original capacity and residual capacity; its net flow is their difference, checked to remain in `[0,initial]`.

`_levels` performs BFS on positive residual capacity. `_augment_one` follows only successive BFS levels, records its path iteratively, and updates both forward and reverse residual capacities on augmentation. Cursor reuse skips saturated/dead edges. Marking a dead level-graph vertex `-1` is valid within that phase: augmentation only creates reverse residual arcs pointing backward in the original level graph, so it cannot create a new admissible forward continuation from a previously exhausted vertex. A new BFS is performed for the next phase.

The flow loop stops either when no augmenting path remains or when the source-capacity upper bound is reached. Residual reachability is then recomputed, sink non-reachability is required, and cut capacity is summed from every original forward arc crossing the cut. The code checks flow equals cut, total source flow, and total sink flow.

For an allowed atomic pair `(i,j)`, if `L_i` is reachable then its entry vertex and the complete eligible chain prefix, including `R_j`, are reachable because those large-capacity arcs cannot be saturated. Thus

\[
a_i+b_j\ge1,\quad a_j+b_i\ge1,
\qquad
a_i=1_{L_i\notin S},\ b_i=1_{R_i\in S}.
\]

The solver's min-cut dual `y_i=(a_i+b_i)/2` is therefore feasible on every allowed cross edge. Since no large-capacity arc crosses the minimum cut, its objective is half the source/sink cut capacity, equal to the cross optimum. The implementation checks this weighted objective. The missing *external verifier* check of the exposed dual is finding C01 below; it does not invalidate this internal mathematical derivation.

## 5. Flow disaggregation and symmetric atom witness

The underlying original forward network is acyclic: source, left vertices, right partition chains descending in energy, sink. Residual routing can change net original-edge flows, but their final net values remain nonnegative and satisfy conservation.

For each destination partition the code processes right atoms in descending energy. It inserts all incoming left-entry net flows at their entry point into a FIFO queue, consumes exactly the local sink flow, and carries the remaining queue down the chain. An entry flow starts at a left atom's highest eligible right position; every subsequently visited lower destination is also eligible. No origin can acquire a forbidden higher-energy destination during disaggregation.

`pending` equals incoming-plus-carried mass before sink consumption. After consumption it is checked against the actual net downward chain flow. At the bottom the queue and pending mass must both vanish. The code also directly checks the bin distinction and energy cap of each emitted directed atom pair, plus the total directed mass against the network flow.

The directed flows are symmetrized as

\[
x_{ij}=\frac{f_{ij}+f_{ji}}2.
\]

The dictionary numerator accumulator stores both orientations in one unordered key and uses denominator `2*capacity_denominator`. At atom `i`, the consumed leg mass is half of its directed outgoing plus incoming mass, no greater than `w_i`. The residual single formula `2*capacity_i-used_numerator_i` is therefore exactly the remaining leg mass. Negative residuals are rejected.

Every directed queue allocation exhausts an entry block or a right-atom sink demand. Therefore the number of positive directed allocations is bounded by entry blocks plus right demands, `O(kn)`. Symmetrization merges keys and cannot increase that count. Singles add at most `n` records. The returned witness is sparse in the declared fixed-four-bin setting.

## 6. Main primal verification

`verify_primal` independently checks every pair's positive exact coefficient, two distinct atom keys, cross-bin relation, closed energy cap, and uniqueness as an unordered edge. It checks positive exact residual singles, one record per single key, and every complete atom marginal. It then requires the primal cross objective to equal both the formula bound and `solution.cross_C`.

Together with `verify_bound`, these checks prove the exact mathematical maximum independently of the flow solver's success status. The equalities `flow_value=mincut_capacity=2C` are also checked, but presently their exposed scalars and the auxiliary min-cut dual are not independently typed/verified as a separate certificate.

The verifier does not claim to solve a fixed-total-double problem. Its accepted pairs are all cross-bin doubles, so for this witness `d=C`. Residual singles preserve the marginal. There are no same-bin or diagonal doubles hidden in the decomposition.

## 7. Native source binding and original consumer path

The adapter's `native_module` hashes the original `event_union.py` before dynamic import and requires the retained SHA. Its `native_atoms` calls that module's `validate_source` and requires actual pinned-source provenance.

The original validator checks:

- exact source bundle type;
- every atom and its original cutoff/energy-bin domain;
- exact atom-content digest;
- fixed attribution NPZ and canonical-source SHA labels;
- process-local attestation created only by the pinned loader.

The pinned loader itself enforces the NPZ byte SHA, exactly 3201 atoms, float64 storage, ordered finite energies, nonnegative finite weights, fixed endpoint energies, 3200 active atoms plus the separate cutoff ghost, then lifts each stored binary64 value exactly to `Fraction`.

Consequently source objects for this adapter should be obtained through

`cross_envelope.native_module().load_pinned_source(...)`.

An object created from a different dynamic import of the same consumer file has a different `AtomBundle` class and separate process-local attestation. It is correctly rejected by the original strict validator; identical source bytes do not justify bypassing that check.

The wrapper then:

1. verifies the maximum witness against the native atoms and the bound's atom digest;
2. assigns unique stable event IDs to the explicit cross pairs and residual singles;
3. calls the actual `previous.binding(window,source)`;
4. calls `previous.claims_by_partition(events,source,binding)`;
5. invokes `previous.consume_event_union(claims,source,nb_m3=...,previous_windows=...)` with the original named parameters.

The original consumer validates every claim binding and every same-event repetition, requires every selected incidence to appear, checks exact selected-source marginals, rejects overlapping-time replay, and applies `W=(b*b-a*a)/2` once. It then enforces

\[
 W(N-d)\le\frac{1085}{94}\frac{99}{100}.
\]

Here the new witness has `d=C`. The wrapper neither catches nor bypasses inventory failure. The original per-baryon conversion checks `nb=8750/47` whenever a non-null `nb` is provided. The wrapper-level null-`nb` contract issue is C02 below.

The adapter adds only conditional cap/assumption metadata and its digest. It keeps actual physical `K`, actual `C`, and actual `D` null; the inherited full-physical activation remains false. `total_double_scope` explicitly says `CROSS_ONLY_ATTAINING_WITNESS_NOT_FIXED_D_PARETO`, and `cross_interval_scope` keeps recipient inventory separate. RR and retained photons remain original zero-correction once-only ports; no source re-normalization, transport, projection, or RR recomputation is imported.

## 8. Findings

| ID | Severity/scope | Observation and effect | Minimal resolution |
|---|---|---|---|
| C01 | Certificate-integrity finding; not a defect in the accepted maximum | `verify_primal` ignores `solution.mincut_dual`. Its current PASS proves optimum through the formula dual and primal, but does not verify all displayed auxiliary flow certificate fields. | Validate the min-cut dual keys/exact labels/all cross edges/objective, or mark that field as unchecked diagnostic and avoid claiming it was independently admitted. |
| C02 | Native endpoint contract finding | `consume_native(...,nb_m3=None)` passes through the original density-only path although the new contract fixes explicit same-state `nb`. | Require `exact(nb_m3)==NB` in the new wrapper before native consumption; leave the original consumer unchanged. |
| C03 | Reporting precision | Bound threshold fields and flow diagnostic counts are not used by the proof verifiers. | Describe exactly which certificate fields are checked; optionally validate threshold-to-set reconstruction without redoing optimization. |

No blocker was found in the mathematical suffix optimum, actual compressed-flow construction, disaggregation, symmetrized marginals, original inventory gate, once-only history, or physical-null separation.

## 9. What this review does and does not establish

This review establishes static equation-to-code coherence for the identities above and identifies specific missing adapter/certificate checks. It does not supply a fresh execution PASS, benchmark, complete replay, final C09 decision, or new source-byte recovery claim.

The root-owned bounded runs and independently authored saved-certificate evaluator remain the execution evidence. They should preserve source identities and any real failed attempt, and should add only targeted checks required by a concrete finding. No rerun of unchanged source fitting, RR, PR113, or PR114 science is recommended by this audit.
