# Independent bounded review: G09 and G12

Review scope: the new rank-policy and independent-propagator work only. G01/G07/G08/G10 were deliberately not reviewed again. Historical production implementations were inspected where needed to establish method and initial-state semantics. Their full suites and the new full suites were not rerun by this reviewer. One focused nonunit-state discriminator was executed.

## Outcome

**G09 synthetic policy/reference: ACCEPT WITH STATED LIMITATIONS.** The retained transforms, diagnostics, new identities and no-certificate-inheritance claims agree with the code and saved 20-decision table. No physical enlarged-basis decision is made.

**G12 theorem/reference/synthetic benchmark: ACCEPT WITH STATED LIMITATIONS.** The Cholesky derivative, triangular solves, CF4 coefficients and order of exponentials match the derivation. The saved convergence data support the stated synthetic order. Physical production parity remains open.

**Resolved P2 finding G12-NORMALIZATION-01:** the unbound physical comparison contract must explicitly bind a common initial-state normalization policy. `propagate_cf4` preserves the supplied norm, while historical `run_candidate` and `run_reference` normalize even a supplied c0. The current benchmark starts from a normalized exact vector, so its reported results remain valid. A later physical comparison using arbitrary imported c0 could otherwise compare different initial-value problems.

The finding was repaired in `PHYSICAL_PARITY_CONTRACT.common_initial_value_contract`: it now binds initialization state/norm/hash/factor receipts, an explicit common normalized IVP, a predeclared discrepancy allowance and its propagated contribution to the parity budget. A null allowance blocks execution. This reviewer read the amended contract and report directly; no historical solver or synthetic code changed, so no suite rerun was warranted. Physical admission implementation remains part of the existing open G12 physical scope. The original discriminator is retained.

## G12 derivation and implementation checks

1. With upper Cholesky S=R†R, X=Rdot R^-1 is upper triangular with real diagonal. Differentiating gives E=R^-† Sdot R^-1=X†+X, uniquely fixing X_ij=E_ij above the diagonal and X_ii=E_ii/2. The implementation uses this orientation correctly.
2. `_congruence_inverse` first solves R† L=M and then X R=L via a transpose solve. This computes R^-† M R^-1; it does not accidentally conjugate the right factor or form an explicit inverse.
3. The whitened generator is X−Dt−iHt. Its Hermitian part equals the transformed metric-compatibility defect when H is Hermitian. The code rejects defects beyond a declared tolerance and records residual anti-Hermiticity; it does not silently antisymmetrize the generator. SPD/regularity and smoothness hypotheses are explicit in the derivation. No validated floating-point enclosure is claimed.
4. The Gauss nodes are 1/2±sqrt(3)/6. With a1=(3−2sqrt(3))/12, a2=(3+2sqrt(3))/12, the early-weighted exponential acts first and the late-weighted one acts last. Expanding around the midpoint yields the required negative h³[B,B']/12 Magnus commutator term. Reversing the step gives the inverse composition, so even powers of the midpoint logarithm vanish. The stated C4 compact-interval assumption is sufficient for the claimed local O(h⁵), global O(h⁴) asymptotic order; no error constant is supplied.
5. The benchmark's physical exact Hamiltonian follows by differentiating U=exp(−i phi sigma_z)exp(−i theta sigma_x). For F=VR, the independently constructed Sdot from Rdot and D from Fdot are consistent with that exact trajectory. This is a genuine same-ODE synthetic comparison with the legacy direct-coefficient DOP853 lane. It is not merely an exponential-method self-comparison and does not prove physical G02.
6. Saved counts are consistent: five midpoint rows use n+2 provider calls; five CF4 rows use 2n+2; direct DOP853 uses 371 RHS calls plus one initial metric query and 25 norm-history queries =397. Six G12 unit tests are recorded in the original green log. This reviewer read that result rather than claiming a rerun.
7. The reported order ratios (midpoint approximately4; CF4 approximately16), norm drift, final error and no-native flags agree with the saved JSON. All three methods have an exact normalized benchmark initial state; their normalization differences are irrelevant there to more than roundoff.

## Focused normalization discriminator

A constant synthetic S=I, H=diag(0.3,−0.2), D=Sdot=0, c0=(2,0), t∈[0,1] was passed to the three existing/new entrypoints. Only this focused review experiment was run.

| Lane | Input norm | Effective initial norm | Final norm |
|---|---:|---:|---:|
| New CF4 | 4 | 4 | 4 |
| Legacy exponential midpoint | 4 | 1 | 1 |
| Legacy direct DOP853 | 4 | 1 | 0.9999999999999978 |

`INDEPENDENT_NUMERICAL_REVIEW_DISCRIMINATOR.json` preserves the result. The correction belongs in physical comparison admission/provenance, not an unrequested rewrite of the historical solvers. Require a predeclared common normalization transform or fail on a mismatch; retain original state/hash, transformed state/hash, original metric norm and applied factor. All lanes must then receive the same declared physical initial state, and any legacy internal normalization must be accounted for or rejected by the admission check. No normalization correction may hide propagation norm drift.

## G09 mathematical and policy checks

Canonical truncation retains lambda>tau*lambda_max and returns T=U_keep lambda_keep^-1/2. Pivoted Cholesky updates residual diagonals from selected columns and orthonormalizes the chosen submatrix explicitly. These are distinct rules, correctly reported as such; shared numerical scales do not imply equal ranks or subspaces in general.

The Hermitian-part adjustment and tiny-negative PSD uncertainty are disclosed. No diagonal metric shift is applied. Residual-diagonal clipping is recorded separately from the original metric, and the final residual spectral norm/minimum eigenvalue remain visible. Exact-PSD residual trace reasoning is not mislabeled as a floating-point certificate.

`new_basis_identity` binds parent metric bytes, cutoff, algorithm, complete transform digest, pivot list and retained rank. It requires new operator qualification and temporal certification, marks selection semantics unresolved, forbids old index inheritance and authorizes no physical execution. Degenerate eigenvector choices may produce a different transform hash; the implementation does not pretend that a method label alone uniquely fixes a basis.

Synthetic physical-space diagnostics use B T and reconstruct an orthonormal physical span. Both regular and weak states are projected without renormalization, so discarded norm is visible. The selected span's projection is explicitly AUDIT_ONLY; it is not a hidden replacement for the original physical channel definition. SVD rank filtering within the audit span is accompanied by its resulting selected rank; all saved examples retain selected rank2.

The 20 saved rows equal two cases × five predeclared cutoffs × two algorithms. All rows include a new identity and no physical authorization. The rank4 plateau at cutoffs1e−8 and1e−6 coexists with about42% rho change from the full near-SPD model and almost complete loss of the weak state. The report correctly uses this as a counterexample to plateau-implies-completeness, not as validation of a universal cutoff.

The report explicitly freezes a time-independent transform and gives the additional T†S Tdot term for a time-dependent transform. Principal angles are supplemented by rank and retained-projector distance, so lost dimensions are not concealed. The need to retain the actual transform, not only its hash, is also explicit. The existing B1–B3 unsupported/backend/coefficient/Gram prerequisites remain blockers.

The original green log records eight G09 tests. This reviewer verified its count and relation to the code, without rerunning the suite. No actionable G09 defect was found within this synthetic-reference scope.

## Remaining limitations

This is a source/derivation/record consistency review with one targeted synthetic discriminator. It is not a second full validation campaign, native execution, interval certification, or physical production acceptance. Existing claim ceilings remain unchanged. Exact reviewed file hashes and repair disposition are in `INDEPENDENT_NUMERICAL_REVIEW.json`.

## Finding resolution

The common normalized-IVP contract correction was independently inspected by the G07/G08 reviewer. Exact common state/S0 identities, per-method actual initial-state/norm/factor/distance receipts and a predeclared initial-distance allowance are now required; null allowance blocks launch. The correction resolves the missing-contract finding. Future physical runtime enforcement remains unimplemented and G12 physical parity remains open. Synthetic unit-norm results and existing solver behavior are unchanged. No full suite or native calculation was repeated for this document-only fix.
