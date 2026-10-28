# Exact energy-constrained cross-event envelope

cross_envelope.upper_bound(atoms,K) evaluates the two-threshold deficiency
formula and returns a complete half-integral dual certificate. verify_bound
checks input identity, exact scalar domains, every allowed edge through
partition/dual-group minima, independent neighborhoods, threshold metadata
and objective. It does not rerun the threshold search.

cross_flow.solve(atoms,K) constructs a primal maximum using an exact integer
capacity bipartite double cover compressed into energy-prefix chains.
verify_primal checks every explicit atom marginal, support, objective and
both supplied duals. Rational weights are divisible masses, not integer
particle counts.

For complete native cross support, complete_support_witness checks all
partition maximum-energy sums against K and reuses the byte-pinned PR112
half-shift, discards same-bin pairs and reconstructs residual singles. Its
flow/min-cut fields are null. Explicit primal and formula-dual equality
certify optimality.

## Data and consumer

Always load the source with native_module().load_pinned_source(npz_path).
The original loader attests the 3,201 binary64-derived exact atom values.
The native adapter requires that actual attested source.
consume_native requires a nonempty explicit conditional K assumption and
exact same-state nb=8750/47. It calls the original
binding -> claims_by_partition -> consume_event_union path and preserves
state, history, volume, clock, inventory and replay guards. nb=None is refused.

The source coefficient is m^-3 s^-2. The consumer applies W=(b^2-a^2)/2 once
and divides by nb once. Union correction is W(C,0,-C), chemical correction
-(24.59+54.42)WC eV m^-3 and ionic-charge correction -2WC.
Electron/kinetic/RR/retained-photon corrections are zero.
Actual K, exclusive joint law, C/D, donor work, EOS/T and full-source physical
native25 remain null.

## Validation and reproducibility

Do not reopen the closed ledger. An independent rerun needs a fresh run area
and separately approved resource ledger. Actual COMMAND.json, executed
SOURCE_SNAPSHOT, SHA256 manifest and receipts are preserved per attempt.

- small_v1:116 independent exact cases and20 rejection controls.
- targeted_v1:8 targeted controls after static certificate/nb review.
- native_v1:failed during K20 generic flow. Eight complete checkpoint cases
  are retained and separately revalidated.
- recover_v1:preserved syntax failure before science.
- recover_v2:reuses those eight cases and adds only K20 direct attainment.
- independent_v1:reads the original NPZ itself; checks nine duals, three
  explicit primals and three main consumer results.
- plot_v1:uses saved results only; root visual QA is a separate receipt.

reference_oracle.py uses generic explicit graph enumeration. The native
independent evaluator imports neither production solver nor source loader
and checks all eligible neighbors by sorted prefix minima.
Six native caps have upper certificates and the proved sharpness theorem;
three have separately checked explicit primal attainment.

## Cost and scope

The dual sweep takes O(k n log n) rational operations/comparisons. Bit
complexity is separate. The compact flow has O(k n) edges but its runtime is
not linear: long prefix chains caused the preserved K20 cost failure.
This study optimizes C, not the joint fixed-d region or an arbitrary extra
bin-edge mask. Native inventory depends on d, not C in general. The actual
retained source passes even the all-single inventory endpoint.
