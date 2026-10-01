# G08: basis covariance and diagnostic semantics

The covariance claim is derived and implementation-verified for constant,
nonsingular coefficient transformations, with consistent selected-span maps.
Twelve seeded complex six-dimensional transformations have condition number 5;
all checked relative defects are below 3.46e-15. The raw coordinate block norm
is explicitly demonstrated to change under basis scaling.

## Authority and assumptions

Database row `REPORT_GAP_08` (line 1170), initially
`REPORTED_RECOMMENDATION_NOT_VALIDATED`, requests covariance tests for rho and
projectors while permitting raw K_TP to vary. The historical rate probe and
runtime pins are identical to those in `E_RHO_SOLVER_REPORT.md`.

Assume S is Hermitian positive definite, H Hermitian, J full column rank,
Sdot=D+D†, and T is a time-independent nonsingular complex matrix. This is
coordinate covariance of the same finite model and physical selected span.
It is not a comparison of different bases or a completeness assertion.

## Derivation in the project notation

Let B'=BT and c'=T^-1 c. Then

\[
 S'=T^\dagger ST,\quad H'=T^\dagger HT,\quad
 D'=T^\dagger DT,\quad J'=T^{-1}J.
\]

Since T is constant, Sdot'=T† Sdot T and
`A'=-i S'^{-1}H'-S'^{-1}D'=T^{-1}AT`. The selected Gram is unchanged:

\[
 G'=J'^\dagger S'J'=J^\dagger SJ=G.
\]

The two selected-span matrices consequently have **different** transformation
laws:

\[
 \Pi'=J'G^{-1}J'^\dagger S'=T^{-1}\Pi T,
 \qquad Q'=S'\Pi'=T^\dagger QT.
\]

Pi is a coefficient projector: Pi²=Pi and Pi†S=S Pi. Q is the Hermitian
quadratic-form matrix; it is generally not idempotent and must not be transformed
by similarity. Using constant T gives Qdot'=T† Qdot T, hence

\[
 W'=\dot Q'+A'^\dagger Q'+Q'A'=T^\dagger WT.
\]

Therefore `c'†S'c'=c†Sc` and `c'†Q'c'=c†Qc`. Also

\[
 Wx=\lambda Sx
 \iff W'(T^{-1}x)=\lambda S'(T^{-1}x),
\]

so the complete generalized spectrum, including multiplicities, and rho are
invariant. This proof avoids a false claim that the principal square root itself
transforms by simple congruence. The symmetrically whitened matrices have the
same Hermitian spectrum, which suffices for spectral-norm invariance.

Time-dependent T needs extra connection terms in D' and A' and generally
Jdot'≠0. The test and this closure deliberately concern the constant-T contract.
Copying the same numerical selector indices after a general basis change would
represent a different subspace and is not the transformation tested here.

## Explicit raw block counterexample

Take S=I, K=[[0,1],[1,0]] and T=diag(10,1). If K is a coefficient operator,

\[
 S'=\mathrm{diag}(100,1),\qquad
 K'=T^{-1}KT=\begin{pmatrix}0&0.1\\10&0\end{pmatrix}.
\]

The upper off-diagonal block norm changes from 1 to 0.1, while the represented
operator and subspaces are unchanged. Thus the raw Euclidean coordinate block
norm is a diagnostic of that chosen representation, not a coordinate-invariant
physical quantity. More generally for any nonzero off-diagonal coefficient
block, independent scaling of its source and destination coordinates changes
that norm. If a recorded matrix is a covariant bilinear-form matrix instead,
its law is congruence and block scaling also changes the raw norm; its role
must be declared before interpreting it.

## Separate metric diagnostic

A new optional helper is named `metric_projected_coupling_norm`. It does not
replace, rename or modify existing K_TP outputs. Given full-rank subspace maps
U,V, coefficient operator K and SPD metric S, it computes

\[
 \|P_U K|_{\operatorname{ran}V}\|_{S\to S}
 =\|L_U^{-1}U^\dagger S K V L_V^{-\dagger}\|_2,
 \quad U^\dagger SU=L_UL_U^\dagger,
 \quad V^\dagger SV=L_VL_V^\dagger.
\]

Indeed Ubar=U L_U^-† and Vbar=V L_V^-† are S-orthonormal, so the matrix on the
right represents the projected mapping in orthonormal subspace coordinates.
Under T, transform U,V by T^-1 and K by similarity; its Gram and cross form
remain unchanged, proving invariance. Under separate invertible changes within
U and V, the orthonormalized bases differ unitarily, preserving the spectral
norm. No mutual orthogonality of the two subspaces is required for this identity.

In the counterexample this metric norm is 1 before and after scaling. The tests
also check changes of coordinates inside each subspace and random global complex
T. This is an invariant norm of a projected coefficient operator. Taking K=A
does not automatically give a physical transfer rate: moving-basis/subspace
terms and the observable derivative remain relevant. No such interpretation is
claimed here.

## Numerical and implementation verification

For each of twelve seeds, tests construct SPD S with condition 12, random
Hermitian H, complex D, two-column J, an S-normalized state and a complex
constant T with condition 5. They invoke the **historical production-equivalent
rate probe** in both representations, then compare norm, P, Q, Qdot, Pi, A, W,
full generalized spectrum, rho and the separately named metric diagnostic.
Projector idempotence, S-self-adjointness and Hermiticity are also checked.
Maximum relative defect is **3.45358e-15**. Test vectors are synthetic states;
no tail state or new physical result is constructed.

Results are in `E_COVARIANCE_RESULTS.json`; the common 11-test suite and commands
are recorded in the G07 report and `TDD_GREEN.log`. Evidence statuses are
DERIVED, NUMERICALLY_CHECKED and IMPLEMENTATION_VERIFIED. Candidate update:
`G08=CLOSED_DERIVED_AND_IMPLEMENTATION_VERIFIED`. New native/external executions
and consumed authorizations: zero. Capture, production, all-bound, b-grid,
continuous-majorant and continuous-trajectory ceilings remain unchanged.
