# G07: generalized-rate eigensolver and conditioning

The finite-matrix eigensolver audit is closed **with a conditioning domain**.
Eight recovered B0 static matrices are well conditioned and reproduce their
archived rho values exactly in the historical implementation. Generalized
`scipy.linalg.eigh` and explicit Cholesky congruence agree within 4.45e-15 relative
on those matrices. This does not establish reliable full rate-matrix assembly
near rank loss, a certified forward-error enclosure, or physical tail control.

## Authority and implementation

Database row `REPORT_GAP_07` (report line 1169) initially says
`REPORTED_RECOMMENDATION_NOT_VALIDATED`; its request is a conditioning sweep,
backward-error and value-error assessment. This report addresses that request.

The historical `projector_rate_probe.py` is unchanged, from returned execution
commit `01ec2ba7e71aefdccab1896acfe5d92c15c6b776`, SHA256
`022cade99f705493043ef98ec86bb5fb9aefb22f079ca5471874d23a05c1fb27`.
The recovered preparation contains byte-identical probe code. The audit uses
Python 3.12.14, NumPy 2.3.5 and **SciPy 1.17.0**, matching the project's pinned
execution versions. Archived documentation `SciPy_1_17_0_eigh` is the versioned
reference; the archive's current SciPy 1.18 documentation does not establish
behavior of this runtime. LAPACK `LAPACK_zhegvd` supplies the underlying
Hermitian-definite driver reference.

The new code is an audit helper. It does not change production evaluator
behavior. No dependency was installed. Because mpmath/SymPy are absent, a
standard-library Decimal analytic lane supplies an independent 100-digit
reference for complex Hermitian 2x2 pencils.

## Mathematical and computational form

For Hermitian W and positive-definite S, set S=LL† and y=L†x. Then

\[
 Wx=\lambda Sx\quad\Longleftrightarrow\quad
 (L^{-1}WL^{-\dagger})y=\lambda y.
\]

Consequently rho is the maximum absolute eigenvalue in either formulation.
The Cholesky-whitened matrix is unitarily similar to the symmetric-square-root
whitening, so their Hermitian spectral norms agree. Explicit inverses are not
formed: both congruence sides and eigenvector recovery use triangular solves.

* Path A: `eigh(W,S,type=1,driver='gvd')`, full Hermitian-definite pencil.
* Path B: Cholesky, two triangular solves, `eigh(C,driver='evr')`, recover
  generalized eigenvectors with `solve_triangular(L†,y)`.
* Path C: solve `det(W-lambda S)=0` in 100-digit Decimal arithmetic for 2x2.
  Decimal.from_float binds the reference to the **actual rounded input pencil**.
  The quadratic roots use a cancellation-avoiding product/root formulation.

A and B share LAPACK infrastructure and Cholesky-based mathematics; their
agreement is a cross-path check, not fully independent numerical certification.
C has different arithmetic and algorithmic structure. It is high precision,
not directed-rounding interval validation.

For each eigenpair, with r=Wx-lambda Sx, the reported normwise residual/backward
measure is

\[
 \eta=\frac{\|r\|_2}{(\|W\|_2+|\lambda|\|S\|_2)\|x\|_2}.
\]

It measures an unstructured normwise perturbation scale. It is not a structured
Hermitian-definite backward-error theorem or a relative eigenvalue certificate.
Absolute residuals, W-scaled residuals, S-orthogonality defects and the dominant
rho eigenpair residual are also retained. Small normwise residuals do not imply
small relative forward error when S has a small eigenvalue. Perturbations to the
metric are magnified by normalization; eps*cond(S) is recorded as a conditioning
indicator, not asserted to be an error bound.

## Synthetic results

The six-dimensional complex sweep uses the same fixed W and a unitary rotated
S with geometric eigenvalue ladder. Intended conditions are 1, 1e4, 1e8, 1e12;
the actual represented conditions are recorded in JSON.

| Intended cond(S) | A/B rho discrepancy | Max backward measure A | Max backward measure B | Decimal 2x2 forward error A |
|---:|---:|---:|---:|---:|
| 1 | 1.43e-16 | 4.84e-16 | 1.43e-15 | 1.60e-16 |
| 1e4 | 5.85e-16 | 1.39e-15 | 3.81e-14 | 9.77e-14 |
| 1e8 | 2.03e-15 | 9.57e-13 | 4.61e-11 | 3.22e-10 |
| 1e12 | 5.36e-15 | 3.50e-10 | 1.21e-7 | 2.78e-6 |

The dominant eigenpair backward measures stay below 2.74e-16 for A and
2.36e-16 for B in this sweep. Other eigenpairs deteriorate substantially. Most
importantly, both paths share a 2.78e-6 forward error at approximately 1e12 in the
independent Decimal lane despite near-machine-precision A/B agreement. Agreement
between related solvers alone is therefore an inadequate conditioning test.

The full historical `rate_matrices` accepts the synthetic metrics at 1 and 1e4.
At 1e4 its W relative Hermiticity defect is 4.99e-13; it rejects the 1e8 and 1e12
cases with `ValueError: W: non-Hermitian input`. These are **preserved failures**,
not silently corrected. They arise in constructing W, before the eigensolver.
The full-probe verification domain is therefore narrower than the direct
pencil stress sweep.

For `S=[[1,1],[1,1+delta]]`, represented deltas 1e-8, 1e-12 and 1e-15 pass
Cholesky. Requested delta <=1e-16 rounds to zero on this float64 platform and is
rejected. Singular and indefinite metrics are rejected without mutation. This
is a representation-dependent boundary, not a universal rank threshold. Any
rank reduction/new basis must be decided under G09, with new qualification.

## Recovered physical matrices

The eight existing B0 tail queries at z=±16, ±20, ±24, ±32 a0 were recovered by
the root agent from `R4P0-B0-STATIC-TAIL-20260930-A1` and verified by member size
and SHA256. This audit independently checked each consumed NPZ and diagnostic
against its science manifest before extracting selected S,H,D.
`PHYSICAL_MATRIX_FIXTURES.json` preserves the exact float64 values as real/imag
JSON pairs, original NPZ hashes, byte counts and diagnostic hashes. It permits
the test to run without a remote restore or native evaluation.

All eight have cond(S) between **1.0042690153 and 1.0089766800**. The historical
rho replay matches its archive exactly. Maximum A/B relative discrepancy is
**4.44273e-15**, and maximum eigenpair backward measure over both paths is
**2.43718e-15**. This supports current B0 finite-matrix postprocessing at these
stored points. A high-precision 18x18 lane was not necessary to diagnose this
well-conditioned case; physical assembly error and independently checking
Sdot remain different gaps.

Full spectra have an approximately ±lambda dominant pair. The next absolute
eigenvalue pair is separated from the dominant pair by approximately
1.07189e-3, 7.49418e-4, 5.35517e-4 and 3.00541e-4 at |z|16,20,24,32 respectively.
These are pointwise spectra, not continuous branch-tracking certificates.
No state is attached to the tail matrices; P and Pdot remain unavailable there.

## Admission and limits

The helper explicitly checks finite square inputs and relative Hermiticity
before factorization, with default admission threshold 500 machine eps. Any
accepted Hermitian-part adjustment is recorded as half the input anti-Hermitian
defect. For historical assembled W, the separate postprocessing audit explicitly
uses `(W+W†)/2` and retains the raw W defect. This matches the historical probe's
declared roundoff treatment; it does not discard the rejected high-condition
cases or relax their production checks. No diagonal shifts, clipping or rank
truncation occur.

The verified domain consists of the eight stored B0 pencils and the documented
synthetic families. A conservative **operational screening recommendation** is
cond(S)<=1e4, residual/orthogonality/Hermiticity checks, and a high-precision
audit when the requested tolerance competes with eps*cond(S). This is not a
proof that every pencil below that condition number meets a requested forward
tolerance. Near-singular full-probe accuracy remains a G09/numerical-method
issue and cannot inherit the B0 result.

## Tests, failure evidence and closure

`TDD_RED.log` records initial missing-helper import failures before implementation.
An intermediate overstrong condition-independent backward-error threshold failed
at 1e8/1e12; the data above preserve that finding. The regression now distinguishes
dominant-pair residual checks from conditioning-scaled whole-spectrum stress
checks; it does not relabel poor forward conditioning as success. This change and
the explicit historical W projection are recorded in `TDD_DECISIONS.json`.

Command from repository root:

```sh
python -m unittest discover -s research/gap_closure_20261001/numerical_methods_20261001 -p 'test_*.py' -v
python research/gap_closure_20261001/numerical_methods_20261001/numerical_audit.py
```

The shared G07/G08 suite has 11 passing tests. Evidence status is
NUMERICALLY_CHECKED and IMPLEMENTATION_VERIFIED for this exact scope.
Candidate update: `G07=CLOSED_IMPLEMENTATION_VERIFIED_WITH_CONDITIONING_DOMAIN`
(registry category `RESOLVED_WITH_LIMITATION`). No new native/external run or
authorization was consumed. No physical capture, tail or basis gate changes.
