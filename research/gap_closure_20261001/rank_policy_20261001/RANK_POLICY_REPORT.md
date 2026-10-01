# G09: explicit rank decisions and synthetic validation

The rank-loss policy and a bounded reference implementation are complete for
synthetic finite matrices. Adoption of any real B1/B2/B3 reduced basis remains
unresolved: the actual enlarged-basis Gram matrices and radial identities have
not been qualified, and the frozen native backend does not support l>1.
The appropriate overall gap status is **RESOLVED_WITH_LIMITATION**.

## Authority and actual project basis state

The original database row `REPORT_GAP_09`, report line 1171, is
`REPORTED_RECOMMENDATION_NOT_VALIDATED`. It calls for canonical versus pivoted
Cholesky comparison, storing every rank decision as a new basis identity, and
observable/subspace stability over a nontrivial cutoff range.

The existing `B0_B3_BASIS_REGISTRY_CONTRACT.json` has SHA256
`0b0e2b95dd9535cec17c5d8ab333e0d6efffb58843b4caf2fe6586a3af0abf04`.
It declares B0/B1/B2/B3 channel counts 18/46/92/124. For all enlarged bases it
records `UNSUPPORTED_L_GT_1`, `NOT_MEASURED` full two-center Gram matrices and
`FUTURE_CONSTRUCTION_AND_QUALIFICATION_REQUIRED` radial coefficient identities.
Hidden channel deletion and inherited B0 temporal certification are false.
The current radial implementation itself states that a missing requested state
raises instead of silently reducing the basis.

Source `Lehtola2019:available` is the acquired authoritative preprint
arXiv:1911.10372v2 (DOI anchor 10.1063/1.5139948). PDF page 2, equations (2)–(3),
describes canonical spectral orthogonalization and removal of small-overlap
directions. The same page describes pivot selection, a residual-trace stopping
criterion and orthogonalization of the pivot submatrix. These motivate the two
reference algorithms; neither that electronic-structure result nor our synthetic
test supplies a BASS_CR dynamical cutoff or physical error certificate.

## Policy

1. Preserve the declared parent basis, channel/radial identities, normalization
   convention, metric/operator source bytes and reference geometry. There is
   **no universal physical cutoff** selected here. A relative overlap cutoff
   is coordinate-dependent: `S=I` and `T=diag(1,1e-5)` describe the same full
   span, but an eigenvalue cutoff 1e-8 retains two and one directions respectively.
   Input scaling must therefore be frozen in the basis identity.
2. Reject materially indefinite or non-Hermitian metrics. Eigenvalues within
   the declared floating-point PSD uncertainty are explicitly marked uncertain;
   this is not certified positivity. Use a higher-precision sign audit if that
   sign matters. Never add an arbitrary diagonal shift.
3. Predeclare several cutoffs and compare canonical truncation, pivoted
   Cholesky, SVD and (when original basis columns are available) pivoted QR.
   A rank plateau is necessary diagnostic evidence, not sufficient physical
   validation. Record retained rank, condition, orthonormality defect, principal
   angles, projector distance, rho, state norm loss, selected observables and
   semantic channel changes. Principal angles alone can hide lost dimensions;
   dimension and projector-distance changes must be included.
4. Every decision receives `NEW_BASIS_IDENTITY` and `NEW_HASH` binding the exact
   parent metric, cutoff, method, retained dimension, pivot list and complete
   transform hash. The reference output demands new operator qualification and
   temporal certification and disallows inherited selected indices. Retain
   the actual transform when executing a future physical model; a hash alone
   is a provenance identifier, not sufficient executable basis data.
5. Canonical retained columns are linear combinations of channels. A normalized
   pivot subset may also mix channel identities. Define the selected physical
   subspace anew under G10; no old numerical index list is inherited. Even an
   unnormalized pure pivot subset can delete desired physical channels, so its
   retained labels do not prove selected-span completeness.
6. Freeze a constant transform over the declared run and test its conditioning
   throughout that domain. Recomputing a truncation independently at each time
   is not a harmless numerical repair. For Bnew=B T(t),
   `Dnew=T† D T+T† S Tdot`; omitting the second term changes the dynamics.
   Rank jumps or discontinuous eigenspace choices require a different model
   contract and cannot inherit this constant-transform policy.
7. For a real reduced basis, predeclare physical observable/rho/subspace
   tolerances and a numerical-conditioning budget before interpreting a sweep.
   Require model-specific operator, temporal and window validation. This
   reference implementation authorizes no B1/B2/B3 or b-grid execution.

## Algorithms and exact-arithmetic meaning

Canonical spectral truncation diagonalizes `S=U diag(lambda) U†`, retains
`lambda > tau*lambda_max`, and sets `T=U_keep diag(lambda_keep^-1/2)`.
In exact arithmetic `T† S T=I`, and the discarded Gram remainder has spectral
norm at most `tau*lambda_max`. A small Gram remainder does not bound error in
the physical span, rho or a normalized state: coefficients in a weak direction
may be large enough to represent a unit physical state.

Pivoted Cholesky greedily selects the largest remaining residual diagonal,
builds `S≈LL†`, and stops when its residual diagonal trace is at most
`tau*lambda_max`. The chosen coordinate columns are then explicitly
orthonormalized using their Gram eigendecomposition. In exact PSD arithmetic,
the residual is PSD, so its norm is at most its trace. In floating point we
record the actual residual, its smallest eigenvalue and any tiny negative
residual-diagonal clipping. This clipping affects the recursion's rounding
diagnostic, not S; no metric shift occurs. It is not a validated residual bound.

The two stopping rules have different meanings despite sharing a scale.
They need not select the same rank or subspace. SVD of S audits eigenvalue
threshold ranks; pivoted QR of the actual synthetic basis B uses a square-root
threshold on R diagonals as a separate rank heuristic. QR diagonal thresholds
are not asserted to be singular-value theorems. Identical ranks in these cases
do not establish general equivalence.

The PSD screen tolerance is `64*n*eps*||S||2`. A tiny negative eigenvalue inside
that region yields `NUMERICAL_PSD_SCREEN_ONLY_NOT_CERTIFIED`, with a sign-audit
requirement if material. Material negative modes raise. Cutoffs below that
screen's uncertainty are flagged even when the reference algorithms can return
a useful numerical result.

## Synthetic experiment and observations

The cutoff ladder was recorded in code before execution:
`[1e-14,1e-12,1e-10,1e-8,1e-6]`. Two complex six-channel cases use seed 909:
one has intended spectrum `[1,.2,.01,3e-5,3e-9,3e-12]`, the other has an exact
zero last physical basis direction before rounded Gram assembly. All 20
method/cutoff decisions, identities and diagnostics are saved.

The synthetic physical basis is known explicitly as B, permitting subspace
comparisons in the physical Euclidean space instead of misleading coefficient
angles. A fixed Hermitian Hamiltonian and two-column selected physical span
define each audit observable. For each reduced model we project that selected
span into its retained physical space, reconstruct its projector and recompute
the rate matrix `W=i[h,Q]`. This projection is labelled **AUDIT_ONLY** and is
not an authorized semantic selection recipe for BASS_CR channels.

The ordinary state is a normalized state formed from bounded coefficients. A
second state occupies the weakest physical direction. Both are projected into
the retained space **without renormalizing away norm loss**. No physical B0
state is used or copied.

| Near-SPD cutoff | Canonical/pivot ranks | Canonical rho | Pivot rho | Canonical ordinary P drift | Canonical weak-state norm loss |
|---:|---:|---:|---:|---:|---:|
| 1e-14 | 6/6 | 2.2374256250 | 2.2374256250 | 2.22e-16 | 2.22e-16 |
| 1e-12 | 6/6 | 2.2374256250 | 2.2374256250 | 2.22e-16 | 2.22e-16 |
| 1e-10 | 5/5 | 1.6049054458 | 1.6260151665 | 1.46e-11 | 1.0 |
| 1e-8 | 4/4 | 1.3070497125 | 1.3087567783 | 2.82e-9 | 1.0 |
| 1e-6 | 4/4 | 1.3070497125 | 1.3087567783 | 2.82e-9 | 1.0 |

The 1e-8–1e-6 interval is a stable rank/observable plateau for each method.
Nevertheless canonical rho differs from the full model by 0.93038 (about 42%),
and the weak state is completely lost. This is a concrete counterexample to
using a cutoff plateau or one ordinary selected population as sufficient
evidence of physical completeness. At rank five, the canonical-versus-pivot
retained-projector distance is about 0.02779; at rank four it is about 0.01053.
Equal ranks do not mean identical subspaces.

The PSD case retains ranks 5,5,5,4,4 for both methods; SVD/QR agree on these
tested ranks. Removing the exact null direction is numerically distinct from
removing a weak but nonzero physical direction. For true redundant physical
columns, H,D and other forms must respect the common null space before an
equivalent quotient model is asserted. The reference does not assume arbitrary
operator matrices satisfy that compatibility.

Full-rank orthogonalization of the most ill-conditioned near-SPD case gives
`cond(T†ST)` close to one but an orthonormality defect up to **1.63e-5**. Thus a
good reported condition number after whitening can conceal normalization error;
the explicit orthonormality check remains necessary. At the rank-four plateau,
defects are around 1e-12 or smaller in the tested cases. These are measured
floating-point errors, not formal enclosures.

## Implementation status and exact remaining blocker

`rank_policy.py` is a new research reference; historical project code and basis
registries are unchanged. Initial tests failed because the helper did not yet
exist (`TDD_RED.log`). The final eight tests pass (`TDD_GREEN.log`): diagonal
rank decisions, indefinite/non-Hermitian/zero rejection, rank/observable plateau,
SVD audit, weak-state loss, new identity and no certificate/index inheritance,
coordinate dependence, tiny-negative uncertainty, trace residual and dimension
loss diagnostics. Runtime: NumPy 2.3.5 and SciPy 1.17.0.

From repository root:

```sh
python -m unittest discover -s research/gap_closure_20261001/rank_policy_20261001 -p 'test_*.py' -v
python research/gap_closure_20261001/rank_policy_20261001/rank_policy.py
```

The policy/reference-implementation subclaim is DERIVED, LITERATURE_SUPPORTED,
NUMERICALLY_CHECKED and IMPLEMENTATION_VERIFIED. No physical B1 cutoff or
reduced basis is approved. Remaining failing claim: a real enlarged basis has
a stable, semantically acceptable and dynamically qualified reduction.
First blocking artifact: the existing B1/B2/B3 registry fields above.
Blocker class: **IMPLEMENTATION_BLOCKER**. Minimum repair: support and pin the
actual enlarged basis/radial identities, obtain independently qualified Gram
data after the prerequisite tail/window gates permit it, then execute this
predeclared cutoff study with physical tolerances and a new semantic selector.
No new native/external execution or authorization was consumed.
