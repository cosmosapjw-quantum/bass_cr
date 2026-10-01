# G04: cancellation-aware analytic majorant, and the exact remaining obstruction

**Result:** an exact fixed-selector leakage formula and an integrable far-tail
majorant have been derived. The majorant is conditional on an exact conforming
finite-FEM model with an invariant isolated selected subspace. It is **not yet a
certificate for the archived B0 numerical operators**. G04 remains unresolved;
G05 gains a conditional closed-form integral only. No native query, transport,
or new physical run was made.

The authoritative database rows are `REPORT_GAP_04` and `REPORT_GAP_05`, both
originally `REPORTED_RECOMMENDATION_NOT_VALIDATED`. This work preserves those IDs.
The recorded physical operator-execution source is commit
`01ec2ba7e71aefdccab1896acfe5d92c15c6b776`; the research/derivation context is
`432010f2afd5305ca63933056f50584c01e4e524`.
Read files and SHA256 identities are listed in `ROUTE_A_STATUS.json`.

## 1. Assumptions and the basic matrix bound

Use atomic units, with time measured in atomic time. Let S be positive definite,
H Hermitian, J fixed and full column rank, Sdot=D+D†, and
A=−S⁻¹(iH+D). All identities hold almost everywhere under the local absolute
continuity/integrability assumptions of G01. Pi=J(J†SJ)⁻¹J†S is the S-orthogonal
projector and Q=S Pi. Write S≥s0 I with s0>0. Then

\[
\rho=\|S^{-1/2}WS^{-1/2}\|_2\le {\|W\|_2\over\lambda_{\min}(S)}
\le {\|W\|_2\over s_0}.
\]

This follows from submultiplicativity and
||S⁻¹/²||²=1/lambda_min(S). Bounding every summand of Qdot+A†Q+QA separately is
usually unsuitable: isolated energies and the Coulomb monopole are order one
and order R⁻¹ terms that cancel in the selected rate. A triangle bound made
before cancellation loses this structure and need not be integrable.

## 2. Exact cancellation: one off-diagonal block, no factor two

Metric compatibility gives Sdot+A†S+SA=0. Set

\[
\mathcal T=\dot\Pi+[\Pi,A],\qquad W=S\mathcal T.
\]

Differentiate Pi²=Pi to see that T has zero diagonal blocks in the
selected/complement decomposition. Moreover Pi J=J and fixed J imply
Pidot J=0, hence Pidot Pi=0. Therefore

\[
(I-\Pi)\mathcal T\Pi=-(I-\Pi)A\Pi.
\]

After metric whitening the projector becomes an ordinary orthogonal projector,
and S⁻¹/²WS⁻¹/² is Hermitian with the block form

\[
\begin{pmatrix}0&X^\dagger\\X&0\end{pmatrix}.
\]

Its eigenvalues are ± the singular values of X (plus possible zeros), so its
norm equals ||X||, rather than the generally looser 2||X||. Consequently

\[
\boxed{\rho=\|S^{1/2}(I-\Pi)A\Pi S^{-1/2}\|_2.}
\]

Equivalently, with

\[
 F=(I-\Pi^\dagger)(iH+D)\Pi,
 \qquad W=F+F^\dagger,
 \qquad
 \boxed{\rho=\|S^{-1/2}FS^{-1/2}\|_2\le\|F\|_2/s_0.}
\]

A reference generator A0 can be removed before estimating anything if
(I−Pi)A0 Pi=0. Then the first boxed formula contains A−A0. In particular a
metric-normalized estimate on the leakage of an integrable perturbation is
sufficient; separate bounds on all of H, D, Qdot are not necessary.

The formula requires **fixed J in the declared coefficient representation**.
Changing the selected physical subspace or using a time-dependent coordinate
change without transforming Jdot introduces additional terms. The formula does
not authorize either operation. `analytic_majorant.py` evaluates this identity
with solves and Cholesky factors, for research checks only. It does not replace
the production rate postprocessor or impose an exact Sdot identity on measured
data.

## 3. Actual B0 representation: compact FEM support

The registry and restored `BASIS.npz` both give radial radius a=64 a0, degree 4,
40 elements, lmax=1. `FEMRadial.evaluate` extends u and its element derivative by
zero for r≥a. Thus exact conforming basis functions on the two centers have
disjoint supports for R>2a=128 a0. S, H and D cross-center weak integrals vanish
there. This is a finite-support statement, not a Slater exponential-tail
approximation and not a statement about the exact physical atom.

`full_operator.py:same_center_blocks` computes the isolated weak Hamiltonian
H0, the full-sphere other-center Coulomb potential V, and the translation matrix
vA. Direct substitution in that source yields

\[
H-iD=H_0+V+\tfrac i2[(vA)^\dagger+vA].
\]

For exact conforming, zero-boundary weak functions, integration by parts makes
vA skew Hermitian and the last term vanishes. The same-center Gram S0 is
constant. If the selected negative-energy isolated eigenspace is **exactly**
invariant under S0⁻¹H0, then isolated evolution contributes no selected leakage.
For the selected projectile span the target block is also irrelevant once the
supports are disjoint. Only the selected-to-complement part of V remains:

\[
\rho={1\over\hbar}\|(I-P)\widehat V P\|_2,
\]

where P is the ordinary projector in orthonormal physical-span coordinates.
Here hbar is restored for units; the project uses hbar=1.

## 4. A universal integrable majorant without fitted coefficients

Within the projectile support ball, the attractive target Coulomb potential
satisfies

\[
-{Z_T\over R-a}\le V(x)\le-{Z_T\over R+a} \quad(R>a).
\]

Its midpoint is a scalar and therefore has no off-diagonal selected coupling.
The spectral norm of the centered multiplication operator is at most half its
range. Compression to a finite subspace cannot increase that norm. It follows
that, under the preceding exact assumptions, for every direction and R>2a,

\[
\boxed{\rho(z)\le g_A(z)
 ={Z_T a\over\hbar\,[R(z)^2-a^2]}
 ={Z_T a\over\hbar\,[z^2+b^2-a^2]}.}
\]

This bound uses support and charge only; it needs **no regression coefficient**,
no fitted exponent and no high-precision radial moment. It is conservative but
integrable. For a chosen Rstar>2a it also implies

\[
 g_A(z)\le {C_2\over R(z)^2},\qquad
 C_2={Z_T a\over\hbar(1-a^2/R_*^2)}
 \quad(R\ge R_*).
\]

A tighter optional path uses the actual B0 angular projection. Since lmax=1,
V has projected multipoles L=0,1,2 for R>a. The scalar L=0 term is −Z_T S0/R
and cancels exactly; selected/complement dipole and quadrupole norms give
C2/R²+C3/R³. The rough bounds C2≤Z_T a/hbar and C3≤Z_T a²/hbar follow from
|P_L|≤1 and multiplication-operator compression. Sharper C2,C3 require certified
radial moments and angular matrices; none has been manufactured from the four
observed radii. The potential-range bound above is already a simpler sufficient
majorant, provided its exact-model assumptions are certified.

## 5. Conditional G05 integral and units

Let z=vt, v>0. Incoming and outgoing intervals must be bounded separately. For
an outgoing Z with sqrt(Z²+b²)>2a,

\[
\epsilon_{A,+}(Z)={Z_T a\over\hbar v}
 \int_Z^\infty{dz\over z^2+b^2-a^2}.
\]

If b<a, let k=sqrt(a²−b²); the integral is atanh(k/Z)/k. If b>a, let
k=sqrt(b²−a²); it is atan(k/Z)/k. If b=a it is 1/Z. These are stable formulas
for the far region and tend continuously to 1/Z as k→0. The incoming bound has
the analogous expression using its own cutoff and certified constants; equal
formulae here come from the direction-independent ideal support estimate, not
from assuming empirical signed samples are symmetric.

For a separately certified g=C/R² the stable result is

\[
\int_Z^\infty{C\,dz\over v(b^2+z^2)}
 ={C\over vb}\arctan(b/Z),
\]

with b=0 limit C/(vZ). This avoids cancellation in pi/2−atan(Z/b).
C has dimensions length²/time, g has 1/time, dt=dz/v has time, and the final
bound is dimensionless probability for a normalized state. The root error-budget
record now predeclares a research target of 1e-5 total probability, split 5e-6
per side, before new physical tail evidence; see `../ERROR_BUDGET_CURRENT_B0.json`.
These mathematical integrals do not close G05 because a project-valid all-z
majorant has not been supplied or shown to satisfy that target.

## 6. The stored-binary coefficient obstruction was measured

`audit_saved_radial.py` reads only the restored B0 coefficients; it calls no
static/native operator evaluator. The stored binary64 numbers are interpreted
as exact rational coefficients. Piecewise mass and kinetic products are
integrated as rational polynomials; Coulomb/centrifugal terms use exact
antiderivatives with Decimal logarithms at 80 and 100 digits. The two resulting
matrices agree to about 2.96e−73 in absolute value. Final norm evaluation uses
ordinary float64 SVD and is not interval certified.

The isolated selected/complement coupling is approximately
**1.9112521548222583e−15 per atomic time** in this literal coefficient
interpretation. High-precision Schur residuals, which test isolated invariance
before the final SVD, are approximately −6.7276e−16, −1.7889e−15, and
+5.8566e−16. Also, exact binary-rational evaluation detects piecewise value
jumps up to 1.59e−14 and positive-mode outer-boundary traces near 1.01e−15 and
1.36e−15. Full identities, coefficient pins and values are preserved in
`ARCHIVED_RADIAL_AUDIT.json`.

These small numbers are compatible with floating representation error. They
are **not** a new finite-window failure or an error estimate for the accepted
N1536 result. They matter because an infinite-time theorem cannot discard an
arbitrarily small constant. The literal piecewise-polynomial functions are not
exactly conforming zero-boundary FEM eigenfunctions. Treating the mathematical
reference as conforming interpolants/eigenspaces is possible, but requires an
explicit model definition and a validated mapping; replacing stored modes or
J silently would change the object under certification.

Even if metric compatibility is granted to an exact coefficient model, an
isolated leakage delta0>0 yields a nondecaying norm limit. If the remaining
Coulomb leakage tends to zero, the reverse triangle inequality gives
rho(z)≥delta0−o(1). Thus rho is not L1 on an infinite tail. Appending a constant
roundoff allowance to C/R² produces a divergent majorant. A very small measured
residual cannot certify exact zero. This is why a purely numerical plateau
check cannot finish the analytic remainder.

## 7. Exact remaining work and status

1. Define and pin the exact reference model to which the continuous theorem
   applies. Establish conforming zero-boundary functions, the ETF integration-
   by-parts identity, and an exactly invariant isolated selected subspace.
   For a newly defined spectral selector/basis, obey G09/G10 identity and
   requalification rules. Do not relabel the accepted B0 artifact silently.
2. Certify the archived-to-reference interpretation/rounding treatment. The
   high-precision audit is not directed interval arithmetic and proves no
   rigorous numerical tolerance for this mapping.
3. Supply a continuous finite-interval certificate from the chosen tail cutoff
   (for example 32 a0) to Zstar with sqrt(Zstar²+b²)>128 a0. The support majorant
   supplies no bound in the overlapping-support region by itself. Route B's
   derivative/interval construction addresses this finite segment.
4. Validate metric positivity and operator errors on those finite cells, with
   G02/G07 and source identities bound to the same model. Four or more node
   samples and successful fits are insufficient.
5. Only then integrate the finite and infinite pieces and compare separate
   incoming/outgoing totals to a predeclared epsilon_tail.

The universal far bound eliminates the need to first discover empirical tail
constants. It does not eliminate the exact invariant-model assumption or the
finite bridge. The present blocking classes are **NUMERICAL_METHOD_BLOCKER**
(exact-versus-rounded reference/cancellation and validated enclosure method)
and **IMPLEMENTATION_BLOCKER** (no certified finite bridge/physical interval
inputs). There is no new native authorization to consume for the mathematical
work. The first next action is reference-model reconciliation plus validated
constant/finite-cell design, not a maximal static radius grid.

Evidence status: DERIVED and NUMERICALLY_CHECKED. The helper implementation's
stated synthetic identities and integral formulas pass nine focused tests;
it is not a physical certification backend. Physical continuous-majorant level
remains 0 (empirical node evidence); no level 2 or 3 is achieved. G04 and G05
remain open, and all scientific claim ceilings are unchanged.

A bounded follow-up repair is derived in `REFERENCE_SELECTOR_REPAIR.md`: a
validated isolated spectral residual/gap can bound the distance to an invariant
reference selector, yielding uniform observable discrepancy without integrating
a constant defect. This changes the named target observable only if explicitly
adopted under a new identity; it does not assert a limit for the old fixed J.
