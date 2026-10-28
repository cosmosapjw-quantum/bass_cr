# C1 — Static code and saved-input baseline

## Disposition and scope

This note identifies the reusable code and stored evidence for `CR_PHYS02_HE_JOINT_REGION_V1`. The governing result and acceptance boundary are `theory/THEOREM.md`, `theory/R09_OBSERVABLES_AND_CODE.md`, `theory/R10_HANDOFF.md`, and `CONTRACT.json`. The inherited local source is the closed PR115 final `b457bb58d74cc9b64f7c760ffc690eda7a51ef9a`; the completed R10 remote checkpoint is `0db1d72042d39aec6fe77430e4ab0bbbe2d488f3`. These identities are distinct, as recorded in `coding/C01_GOAL_AND_BASELINE.md`.

The review consisted of source-text reads, selected stored-JSON field reads and byte SHA256 checks. No scientific module was imported; no solver, source loader, consumer, test, compiler or scientific benchmark was executed. No predecessor code was changed. The only authored artifact in this subtask is this note. Detailed formula mapping, new algorithm/backend design and resource allocation belong to C2–C4; implementation begins only after their actual checkpoints.

## Byte identities

Paths below are relative to the repository root. All eight SHA256 values were independently read from current local bytes during C1 and agree with the existing identity/selection receipts.

| Dependency | Bytes | SHA256 |
|---|---:|---|
| `research/cr_he_event_union_20261028/implementation/event_union.py` | 18,732 | `6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d` |
| `research/cr_he_energy_sum_20261028/implementation/energy_sum.py` | 17,424 | `6cacfa7ba046ea21740beb91b9fd20797f8c06fa43ea525f0c9a555e933d981a` |
| `research/cr_he_energy_cross_20261028/implementation/cross_flow.py` | 16,193 | `3bac2933c6b0b2c3de5fe28c05472ac5ad3e02afca57fb30566e27f051f7585f` |
| `research/cr_he_energy_cross_20261028/implementation/cross_envelope.py` | 13,962 | `653a3011bbcf6af115c4f55ebb4035a46020d72c3e8e5d43fcb3f95fd4e028d3` |
| `research/cr_he_joint_region_20261028/inputs/ATTRIBUTION_ARRAYS.npz` | 233,050 | `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47` |
| `research/cr_he_joint_region_20261028/inputs/PR114_SELECTED_WITNESSES.json` | 5,661,778 | `ae09b3183cbf7f16bb89983fa5f649a65e284b2d4a4042f9d424d0fe5566f8e5` |
| `research/cr_he_joint_region_20261028/inputs/PR115_SAVED_BOUNDS.json` | 2,642,706 | `9c9359a570de873ff6a7ad172ae2a95a1b3d3c2552bbbb80e7239c474fbeba01` |
| `research/cr_he_joint_region_20261028/inputs/PR115_K20_WITNESS.json` | 1,624,834 | `0cc7d56e82ef3fcab3913f24ed7b69e4e87a123da3727f54afdce960e457c775` |

The canonical source-record SHA is `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`. The saved original-consumer atom digest is `2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690`. They identify different objects from the NPZ file SHA.

The PR114 full certificate was recovered before C1 from the original published SOURCE archive: whole archive SHA `caad35c48f0ebe0b756e00429627210e20fc9ded65ec7a14d72a578930993076`, original member `research/cr_he_energy_sum_20261028/runs/primary_v2/PRIMARY_CERTIFICATES.json`, 15,160,355 bytes, member SHA `4f3cad59cb65f901b72674ce99749878efe6ca84ff3e0e337e38540b0c06540e`. `intake/RECOVERY_RECEIPT.json` records the original GET, whole SHA, 284 payload SHA/byte checks and CRC. The PR115 selection source certificate SHA is `c93fc0b692c1cc1597165cacf540db2d836dc86dbb8bc0d99e86cb30637f3a11`. The three selected JSON files copy saved evidence; their creation was not a scientific replay.

## Reusable exact interfaces

### General cross matching: `cross_flow.py`

`Atom(key, energy_eV, coefficient, partition=0)` and `validate_atoms(atoms)` define the finite general input. The validator accepts a list or tuple, enforces nonempty unique string keys, nonnegative exact `int`/`Fraction` energy and mass, and nonnegative integer partitions; `bool`, float and scalar strings are rejected. Empty and all-zero general inputs are permitted. Normalized atoms preserve input order.

`Event(electrons, coefficient)` has no event ID. Its `electrons` is a one-key single or unordered two-key cross pair. `solve(atoms, K_eV)` returns `Solution` with:

- Scientific fields: `cross_C`, `pairs`, `singles`, `flow_value`, `mincut_capacity`, `mincut_dual`.
- Certificate/network fields: `reachable_nodes`, `source_side_atom_keys`, `target_side_atom_keys`, `atom_count`, `partition_count`, `network_nodes`, `network_edges`, `capacity_denominator`, `dinic_phases`, `augmentations`.

The existing implementation uses a bipartite double cover, per-partition right prefix chains, LCM-scaled integer capacities and iterative Dinic. Its returned directed flow is twice the cross objective. Directed flow is decomposed into actual atom pairs and symmetrized; residual marginals become singles. Positive output records are stably sorted by atom keys. The existing certificate conventions and integer-flow/decomposition identities are reusable references. This C1 reading makes no new runtime assertion for a native call.

### Cross bound and original-consumer adapter: `cross_envelope.py`

`Atom` aliases `cross_flow.Atom`. `Bound` contains `atom_digest`, `K_eV`, `total`, `deficit`, `cmax`, `independent`, `neighbors`, `dual`, `partition`, `e_threshold`, `h_threshold`. `upper_bound(atoms,K_eV)` performs the prior two-threshold optimization; its native results are already saved and are not scheduled for replay.

`verify_bound(atoms,bound)` checks the exact source digest, dual labels, all allowed cross-edge constraints through partition/dual-group energy minima, deficiency and dual objective, and threshold-set identity. It does not rerun the threshold optimization. It is a reusable bound-certificate check.

`verify_primal(atoms,bound,solution)` verifies positive cross-only pairs, residual singles, all atom marginals and exact equality with `bound.cmax`. For a flow solution it also verifies the exposed cut dual and `flow_value = mincut_capacity = 2*cross_C`. For a direct `ConstructedWitness`, the method must be `PR112_HALF_SHIFT_FILTERED_CROSS` and flow/cut fields are `None`. This verifier certifies a cross maximum; it does not accept an arbitrary joint-region event measure containing same-bin doubles or a cross value below the maximum.

`maximum_cross` invokes both old optimization paths and is not a saved-evidence loader. `complete_support_witness` invokes the original half-shift construction after an all-cross-support check; the accepted K20 output is already saved. `native_module`, `native_atoms`, and `consume_native` document the original consumer binding. The old `consume_native` is specifically a cross-maximum adapter; a general joint witness needs its own verified adapter boundary.

### Total-double baseline: `energy_sum.py`

This module has its own `Atom`, `Event(key,electrons,coefficient)` and `Solution` classes. `validate_atoms` enforces exact general data. `solve(atoms,K_eV,target_d=None)` performs the existing high–low threshold/greedy construction and retains both maximum and requested witnesses. Its `Solution` fields are `K_eV`, `atom_content_sha256`, `N`, `low_mass`, `high_mass`, `delta`, `dmax`, `target_d`, `threshold_h_eV`, `dual`, `max_events`, `events`, `cap_digest`.

`_check_events` computes `double`, `single`, `cross_C`, `event_records`, and an exact marginal residual, checking permitted loops and pairs. `verify` checks source identity, masses, threshold deficiency, dual pair/loop constraints, both witnesses, exact objectives and predecessor-specific sparse-record limits. Its return explicitly labels cross mass `CHOSEN_WITNESS_ONLY_NOT_MAX_C`. This is a total-double certificate and never supplies the joint bound by itself.

`load_native`, `_native_atoms`, `bind_cap`, `validate_cap` and `consume_native` show how the original source is loaded, a conditional K is bound to source/state identity, and the original consumer is called. `native_plan` calls the old solver; it is not used to recover the saved native D or witnesses. The saved selections are not complete serialized `Solution` objects: their per-case keys are `id`, `K_eV`, `dmax`, `target_d`, `dual_by_key`, `max_events`. In particular, reconstructing a `Solution` merely by unpacking a selected case would be invalid.

## Original source loader and consumer

`event_union.load_pinned_source(path)` is the authoritative native loader. It first checks the exact NPZ SHA, then reads only `energy_eV_with_cutoff` and `identified_A_He_m3_s2`, requiring 3201 finite binary64 entries, the prescribed endpoints, strictly increasing energy and nonnegative weights. Each stored float is lifted by `Fraction.from_float`, preserving its exact stored binary value. The first record is `cutoff_ghost`; the remaining 3200 records are `active_0001` through `active_3200`.

The consumer's native partitions are the cutoff ghost, `(cutoff,1]`, `(1,3]`, `(3,10]`. Its `AtomBundle` contains `atoms`, `provenance_kind`, `atom_content_sha256`, `attribution_npz_sha256`, `canonical_source_sha256`. `validate_source` requires both exact `AtomBundle` type and the process-local loader attestation for a stored actual source. Copying the source SHA or constructing a bundle from the selected JSON does not create that attestation.

An integration detail follows directly from this code: `energy_sum._native_module()` and `cross_envelope.native_module()` dynamically import separate consumer module instances under different module names. Their classes and `_ATTESTED_ACTUAL_DIGESTS` sets are distinct. The new native adapter must use one pinned consumer instance consistently for `load_pinned_source`, `validate_source`, `Event`, `binding`, `claims_by_partition`, and `consume_event_union`. A bundle attested in one instance must not be passed to the other instance.

`event_union.Event(key,electrons,coefficient,provenance='CONDITIONAL_MARGINAL_LIFT')` requires positive exact coefficients, unique IDs within a kernel, and one or two valid electron keys. A loop repeats its key and therefore contributes two legs to the atom marginal. `claims_by_partition(events,source,binding)` repeats the same complete event object and ID across every incident partition. `consume_event_union` unions those IDs, rejects conflicting or incomplete claims, checks the selected marginals, guards overlapping history windows and neutral-parent inventory, and applies the proper-time factor once.

The principal returned fields are `union`, `partition_returns`, `source_ion_density_delta21`, `correction_to_sum_of_partition_ion_density21`, `cross_duplicate_parent_density`, `chemical_correction_eV_m3`, `ionic_charge_correction_m3`, `native_source_species21`, `native_species_correction21`, `selected_birth_zeta`, `selected_birth_wnt_J_per_baryon`, and `accepted_windows`. Physical activation and unprovided physical channels retain their original null/false values.

For full selection, the already-admitted mapping is `union.parents=W*(N-d)`, `union.ion_density_delta=W*(-N+d,N-2*d,d)`, and `cross_duplicate_parent_density=W*C`; chemical partition correction is `-(I1+I2)*W*C`. The source coefficients have units m^-3 s^-2, energies and K are in eV, and `W=(b*b-a*a)/2` has units s^2. `NB=8750/47` is applied once to convert density returns to abundances. The original allowed window is `0<=a<b<=10^10` proper seconds. It does not accept a zero-length window, even though the theory separately states a formal W=0 limit. No source-fit, transport, RR or photon code is imported by this consumer.

## Saved native evidence actually available

| Selection | Contents and permitted reuse |
|---|---|
| `PR114_SELECTED_WITNESSES.json` | Native atom records and source pins; cases N001/N002/N003/N005/N007/N009 at K=0, 1/5, twice the stored binary cutoff, 2, 6, 20; each contains exact D, dual-by-key and the maximum event measure including residual singles. Use `max_events`. |
| `PR115_SAVED_BOUNDS.json` | Nine `cases` with `label` and complete `bound`; K=0, 1/5, twice the binary cutoff, 1, 2, 3, 6, 10, 20. These provide saved X and dual evidence. A bound's presence does not assert that the new joint-domain predicate passes. |
| `PR115_K20_WITNESS.json` | Stored native atom records and one `case` containing bound, cross-only witness, previous consumer result and `TARGETED_DIRECT_CONSTRUCTION_RECOVERY` provenance. The witness contains cross pairs and singles, with direct-method metadata and null flow/cut fields. |

Fraction-valued JSON fields are strings; tuples are JSON arrays. A typed reconstruction must parse fractions exactly and restore the expected tuple/event classes. None of the original scientific APIs accepts a serialized dictionary as a substitute for its required record type.

The original-consumer/PR114 atom-content digest uses a sequence of atom-field tuples. PR115's `Bound.atom_digest` uses serialized atom dataclass dictionaries and is saved as `b1e67d1f39f4f9ab08ded516f291041db8a0c4bf8e74b5becdf274a31eab7412`. These two digests have different schemas; compare each with its own canonicalizer and compare the underlying atom fields exactly. Do not demand equality between their digest strings.

Native K6 has saved equal scalar optima D=X, but PR115 did not execute its explicit cross primal. That witness remains new C5–C7 work. Native K20 already has a saved cross witness; the theorem permits completing its residual low marginal with diagonals. Native K2's saved total maximum and the saved cross bound are the intended reuse inputs. These are R9 obligations, not fresh C1 numerical results.

## Completion boundary and next stage

The exact acceptance contract remains unchanged: actual domain verification, marginal-preserving positive/support-valid vertex and interior witnesses, exact `(d,C)`, an independent small full-event oracle, and agreement with the unchanged native consumer. The old cross verifier cannot replace the new general event verifier, and the old total solver's particular sparse-record bounds must not be imposed on arbitrary convex mixtures without a separate justification.

All four reviewed computational modules use the standard library for their exact core; NumPy is imported only inside the pinned NPZ loader. No SciPy, NetworkX or external LP solver is required by these baseline interfaces. `C01_BASELINE_IDENTITY.json` records the root's metadata-only environment observation: Python 3.12.14, g++ 13.3.0, NumPy 2.3.5 and Matplotlib 3.10.8. C1 does not establish a C++ build or performance result.

The predecessor budget remains closed at 28.653943/40 CPU-s, including `native_v1` exit -9 and `recover_v1` exit 1; its unused allowance is nontransferable. This is evidence from `research/cr_he_energy_cross_20261028/BUDGET_CLOSEOUT.json`, not a current-runtime failure. The current unit's independent 40 CPU-s contract includes compilation, validation, failures and plotting. No new scientific budget was allocated or consumed by this static subtask; metadata CPU is unmeasured.

C1 has an identified input, code, source, return-shape and exact acceptance baseline. C2 can now map the admitted region and witness obligations to these pinned dependencies. New backend details and any source execution remain for the subsequent authorized stages.
