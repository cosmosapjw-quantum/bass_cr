# G04 Route B: a finite continuum certificate and its exact physical boundary

**Result:** the finite-interval construction is derived and implemented. A
nonconstant, noncommuting real-symmetric rational 2-by-2 family has a genuine
Level 2 continuum certificate on `[0,1]`. B0 remains Level 0 empirical evidence;
neither its finite interval nor its infinite tail is certified. G04 is only
partially resolved and G05's physical closure is blocked.

The original rows are `REPORT_GAP_04` (report line 1166, no continuous
majorant) and `REPORT_GAP_05` (line 1167, no quantified infinite-tail integral).
Both retain their original recommendation provenance. This directory does not
edit historical database rows or change the shared current registry.

## Exact theorem used by the envelope

On a finite interval I, assume S and W are Hermitian, locally absolutely
continuous, and the following bounds hold almost everywhere (the positive
metric bound holds everywhere by continuity):

\[
S(z)\succeq s_0I,\quad s_0>0,\qquad
\|S'(z)\|_2\le s_1,\quad
\|W(z)\|_2\le w_0,\quad
\|W'(z)\|_2\le w_1.
\]

Here prime is d/dz, **not** the time derivative used inside the construction
of W. For straight motion d/dt=v d/dz; inserting a time derivative bound in
place of a z derivative without the velocity conversion is invalid.

Set F=S^(-1/2), C=FWF, and rho=||C||2. The spectral functional calculus gives

\[
F=\frac1\pi\int_0^\infty t^{-1/2}(S+tI)^{-1}\,dt.
\]

This identity follows by diagonalization and the scalar integral: substituting
t=s u^2 reduces it to 2/(pi sqrt(s)) times the integral of 1/(1+u^2).
The locally uniform positive lower bound justifies differentiating in operator
norm, using the resolvent identity and its integrable norm dominator. Thus

\[
F'=-\frac1\pi\int_0^\infty t^{-1/2}
(S+tI)^{-1}S'(S+tI)^{-1}\,dt,
\qquad
\|F'\|_2\le\frac{s_1}{2s_0^{3/2}}.
\]

The scalar integral in the last step is pi/(2 s0^(3/2)), obtainable by
differentiating the preceding scalar integral in s. There is no assumption
that S and S' commute. The product rule and ||F||<=s0^(-1/2) give

\[
\boxed{\|C'(z)\|_2\le L:=\frac{w_1}{s_0}
+\frac{w_0s_1}{s_0^2}.}
\]

Absolute continuity and the reverse triangle inequality now imply

\[
|\rho(z)-\rho(z_i)|\le\|C(z)-C(z_i)\|_2
\le L|z-z_i|.
\]

Eigenvalue branches may cross, exchange the maximum, or change sign. No
derivative of rho or any chosen eigenvalue branch is assumed. If a verified
center enclosure supplies rho(zi)<=ui, then gi(z)=ui+L|z-zi| is a continuous
upper bound on that whole cell. Neighboring tents may have different heights at their shared boundary. The
assembler raises that boundary height to the larger adjacent height, retains
each center height ui, and linearly joins successive boundary/center vertices.
Each half-cell line is at least the original Lipschitz tent, so this creates a
literally continuous piecewise-linear majorant on the entire finite domain.
Before this optional upward join, a width h tent has integral

\[
\int_I g_i(z)\,dz=h u_i+\frac{Lh^2}{4}.
\]

For the continuous join, with raised left/right heights a,b, the exact cell
integral is h(a+b+2ui)/4; the certificate saves this larger bound and the
original tent sum separately. The corresponding probability-change bound divides this integral by a
strictly positive certified velocity. Units are rho: atomic_time^(-1), L:
atomic_time^(-1) a0^(-1), and integral dz/v: dimensionless.

## Exact spectral enclosure without a floating point eigensolver

At a center with exact rational real-symmetric S>0 and W, q is a strict upper
bound for rho exactly when both qS-W and qS+W are positive definite. Indeed,
congruence by S^(-1/2) gives qI-C and qI+C. Exact rational LDL pivot positivity
tests positive definiteness. Bisection therefore encloses rho between rational
numbers. Failed strict positivity means rho>=q; equality does not invalidate
the closed bracket. W=0 has the exact bracket [0,0]. No diagonal shift,
truncation, or numerical-rank repair is performed.

For uncertain physical matrix entries, exact tests on nominal float matrices
are insufficient. One must first enclose the actual S,W entry errors, then
prove qS±W positive definite for the whole interval family. A residual of one
approximate eigenpair only places one eigenvalue; it cannot certify the largest
absolute eigenvalue unless completeness and all relevant residual/roundoff
terms are covered. The present implementation deliberately does not advertise
that unsupported shortcut or complex interval arithmetic.

## Demonstrator actually certified

For 0<=z<=1, the fixed family is

\[
S=\begin{pmatrix}2&z/8\\z/8&1+z^2/16\end{pmatrix},\qquad
W=\frac1{(1+z)^2}
\begin{pmatrix}1&z/4\\z/4&-1/2\end{pmatrix}.
\]

These matrices do not commute in general. The implemented derivatives are

\[
S'=\begin{pmatrix}0&1/8\\1/8&z/8\end{pmatrix},\qquad
W'=\begin{pmatrix}-2/(1+z)^3&(1-z)/(4(1+z)^3)\\
(1-z)/(4(1+z)^3)&1/(1+z)^3\end{pmatrix}.
\]

Exact rational interval operations enclose each entry on each of four cells
of width 1/4. Gershgorin diagonal-minus-offdiagonal bounds certify metric
positivity throughout each cell; exact maximum row sums bound the spectral
norms of symmetric matrices. These bounds plus the exact center pencil
brackets produce `SYNTHETIC_CONTINUUM_CERTIFICATE.json`.

Every certificate number is an integer fraction. Arithmetic roundoff is zero
for these exact inputs. Dependence losses in interval arithmetic only enlarge
the bounds. Bisection uncertainty is retained by selecting the upper bracket;
the continuous piecewise-linear envelope integral is exact. The fixture is a mathematical matrix
family, not a propagated state, a B0 operator, or a physical scattering run.
Finite rational spot checks are additional regression diagnostics. The
continuum proof comes from interval extensions and the derivative theorem,
not those spot checks. A separate crossing example W=diag(z,1-z), S=I verifies
the envelope across a nondifferentiable maximum of eigenvalue branches.

## Implemented admission boundary

`CellBounds` and `assemble_envelope` require an explicit scope, contiguous
finite cells, positive metric lower bounds, nonnegative norm bounds, midpoint
centers, and identified center/derivative proof artifacts with SHA256 and
specific references. A `finite_difference` or sample-fit method is rejected.
Binary floating-point inputs are rejected rather than silently treated as
exact decimal measurements. Integer, fraction, and decimal-string inputs
represent exact values; their physical uncertainty remains the caller's duty.

Provenance metadata is **not a mathematical proof checker**. The generic
assembler is conditional on the cited certificates actually being valid and
correctly scoped. Only the fixed demonstrator's bounds are generated and
verified in this implementation. A forged method name/hash would not become
a certificate. Independent physical proof review remains required.

Levels are separated: 0 empirical nodes, 1 conservative dense numerical
envelope without certification, 2 validated finite intervals, 3 validated
finite intervals joined to a certified analytic infinity remainder. The
assembler emits Level 2 and `infinite_tail_certified=false` unconditionally;
there is no automatic Level 3 or physical gate promotion.

## Conditional G05 integral primitive

If and only if a separate argument proves rho(z)<=C/(b^2+z^2) for all z>=Z,
the one-sided time integral is C/(v b) atan(b/Z) for b>0,Z>0. This is the
cancellation-safe equivalent of C/(v b)[pi/2-atan(Z/b)]. At b=0 it is C/(vZ).
`tail_p2_enclosure` certifies that integral with an exact rational alternating
series enclosure of atan(b/Z), on 0<=b<=Z. It explicitly rejects unsupported
domains. The enclosure is valid even at b/Z=1, though convergence is slow.
This helper proves an integral evaluation, not the B0 majorant hypothesis.
Incoming and outgoing coefficients and bounds must remain separately scoped;
their absolute bounds add and cannot cancel. No epsilon_tail has been invented
or chosen post hoc, and no physical G05 certificate is issued.

## Missing inputs for actual B0 and smallest repair

The available B0 evidence is eight qualified point rates at signed radii
16,20,24,32, with no independently propagated tail states. Point qualification
does not enclose the true continuum operators or their derivatives. The eight raw physical operator payloads have now been recovered, verified,
and preserved as exact float64 fixtures by G07. They supply pointwise S,H,D
and reconstructed W at the existing nodes. They do not supply validated
entrywise operator error or whole-cell z-derivative bounds.

The first missing physical proof is a whole-cell lower metric bound and
whole-cell S',W' norm bounds accounting for operator and arithmetic error.
An FD ladder can diagnose derivative implementation but cannot furnish that
proof by itself. Minimal repair is: bind the recovered B0 basis/radial/native
pins and available point matrices to the exact reference model; obtain any
additional center inputs needed by an adaptive finite cover; supply analytic or interval-certified entries for
S,S',W,W' on a finite covering of each signed side; prove interval SPD and
center spectral bounds; join at a specified radius to Route A's independently
certified remainder. The finite FEM support radius 64 a0 makes an analytic
join beyond R>128 a0 a promising Route A target; compact support alone does
not supply finite-domain derivative certificates or all multipole constants.
The exact finite domain needed is [Z,Zstar] per signed side; its node set and
subdivision should be adaptive to these bounds, not a maximal sample grid.

The mathematical barrier is `NUMERICAL_METHOD_BLOCKER`: no validated physical
operator/derivative enclosure yet. The recovery of the eight correctly pinned
matrix payloads removes the point-data availability subtask, while the
whole-cell mathematical enclosure barrier remains. G04 and G05 remain scientifically open; no native calls,
external science runs, state reuse, or old authorization consumption occurred.

## Source use and exact scope of external support

Read the v3 database rows `REPORT_GAP_04`, `REPORT_GAP_05`, and the current
`works` row `Mathias1997`. The acquired publisher-formatted PDF
`v3/user_uploads/paper/mathias1997.pdf` was inspected at physical pages 1–3,
printed pages 861–863, especially Theorems 1–2 and the derivative expansion
on printed p.863. It supports the need to respect noncommutativity and the
difference between matrix square-root perturbation norms. It is **not cited
as proving this project's inverse-square-root derivative constant or B0
certificate**; the exact theorem above is derived here. The selected version
is `Mathias1997:user-upload-20261001`, DOI 10.1137/S5089547989529577.
No additional broad literature search was needed for these self-contained
derivations.

## Reproduction and claim update

From repository root:

```sh
python -m unittest discover -s research/gap_closure_20261001/majorant_validated_20261001 -p 'test_validated_majorant.py' -v
python research/gap_closure_20261001/majorant_validated_20261001/validated_majorant.py
```

The initial red test failed because the implementation module was absent.
The final focused suite contains 23 tests and passes. The detailed command,
exit code, and assertions are preserved in `TDD_GREEN.txt` and
`VALIDATION_RESULTS.json`. Evidence states: DERIVED for the Lipschitz and
integral theorems; IMPLEMENTATION_VERIFIED for exact-rational interval and
spectral helpers; NUMERICALLY_CHECKED for regression spot checks. There is
no PHYSICAL_RUN_VERIFIED claim in this directory.

Ceilings remain capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO,
original_capture_gap_resolved=false, continuous_global_supremum_bound=false,
and continuous_trajectory_error_bound=false.
