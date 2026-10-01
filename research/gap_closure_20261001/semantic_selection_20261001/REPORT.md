# Semantic finite selected subspace

G10 is closed for the implemented semantic selection contract. The selector requires an explicit projectile-center mapping, resolved negative energy, bound-family quantum numbers, and each radial state's SHA256 identity. It returns positions in the current ordering instead of copying saved numerical indices.

The actual B0 resolved registry reproduces `[9,10,12,13,14]`. All 18 resolved channel energy/radial-identity records agree with the independently restored, manifest-verified B0 coefficient-bank metadata. A permutation regression verifies the selected physical projector after mapping coordinates back; the semantic selection hash is ordering independent. Negative or zero-energy pseudostates, ambiguous state identity, duplicate channels and inconsistent quantum labels fail closed.

Nine tests passed using Python's unittest runner. The initial red run failed because the implementation module did not yet exist; the green run passed with no skipped tests. This is a new callable research utility, not a silent replacement of the historical production selection.

B1-B3 can use the same schema only after their actual coefficients, energies and center conventions are bound. Their symbolic channel counts do not meet that requirement. This closes the semantic-index gap; it does not establish completeness, asymptotic capture, or any production gate. No new operator, propagation or native call was made.

Independent review exposed one label-alias duplicate admission. The reproducer failed before the repair, then all nine tests passed with uniqueness keyed by physical coefficient identity `(center,l,m,radial_identity)` independently of quantum labels. Evidence is retained in REVIEW_REGRESSION_RED.txt and REVIEW_REGRESSION_GREEN.txt.
