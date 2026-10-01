# B0_RHO_INTEGRATION_THEOREM

Date: 2026-10-01. Database row: `REPORT_GAP_01` (working label `G01`).
Result: **CLOSED_DERIVED_AND_SYMBOLICALLY_VERIFIED**, conditional finite-model theorem.

The general proof below closes the missing mathematical implication from an
integrable local selected-population rate envelope to accumulated population
change. It does not establish an integrable envelope for the physical B0 tail.
In particular it does not certify physical `Sdot`, finite-window capture,
all-bound capture, or a continuous trajectory error bound.

## 1. Hypotheses and existence

Let I be a real interval and let n and k be finite integers with 1 <= k <= n.
Use complex coefficient vectors and the conjugate transpose dagger. Assume:

1. S belongs to AC_loc(I; Hermitian n-by-n matrices) and S(t) is positive
   definite at every t in I.
2. H,D belong to L1_loc(I; complex n-by-n matrices), H=H† almost everywhere,
   and Sdot=D+D† almost everywhere.
3. J is a time-independent n-by-k complex matrix of full column rank.
4. In atomic units, A=-i S^-1 H-S^-1 D and c is the solution of cdot=A c
   with specified finite initial vector c(t0). In general units replace H by
   H/hbar. No numerical discrete trajectory is silently identified with c.

These are sufficient low-regularity hypotheses for this proof, not a claim that
no weaker theorem is possible. Since S is continuous, its minimum eigenvalue
has a strictly positive minimum on every compact subinterval of I. Thus S^-1
is locally bounded, A is locally integrable, and the linear integral equation
for c has a unique AC_loc solution. The same argument applies to
G=J†SJ: on a compact K, lambda_min(G) >= min_K lambda_min(S) sigma_min(J)^2 > 0.
Inversion and multiplication preserve local absolute continuity here, so the
forms below are AC_loc where appropriate. All derivative identities are a.e.;
the integrated conclusions hold at every pair of times.

If S=B†B and D=B†Bdot for an AC_loc finite column family B into a Hilbert space,
with linearly independent columns at each time, the product rule gives the
assumed compatibility identity. This is a mathematical construction. A code
path which assigns Sdot=D+D† has not thereby independently validated the
derivative of its evaluated overlap matrix; that is G02.

No single positive lower bound for S over an infinite half-line is needed for
this conditional theorem. Such a bound may be needed to prove a usable tail
majorant. Rank loss at any finite time falls outside the hypotheses.

## 2. Projector and quadratic form

Define

\[
G=J^\dagger SJ,\quad
\Pi=JG^{-1}J^\dagger S,\quad
Q=S\Pi=SJG^{-1}J^\dagger S,\quad
P=c^\dagger Qc.
\]

G is Hermitian positive definite, so G^-1 is Hermitian. Direct multiplication gives

\[
\Pi^2=JG^{-1}(J^\dagger SJ)G^{-1}J^\dagger S=\Pi,
\qquad \Pi^\dagger S=S\Pi=Q=Q^\dagger.
\]

Pi has range ran(J), fixes Jv, and its residual satisfies J†S(c-Pi c)=0.
It is therefore the S-orthogonal **coefficient projector** onto ran(J).
Q is its **Hermitian quadratic-form matrix**, not in general an ordinary
idempotent projector. Its identity is Q S^-1 Q=Q. Further,

\[
P=\|\Pi c\|_S^2,\qquad
\|c\|_S^2=\|\Pi c\|_S^2+\|(I-\Pi)c\|_S^2,
\]

so 0 <= P <= c†Sc. Equivalently, S^-1/2 Q S^-1/2 is an ordinary orthogonal
projector. For normalized finite-model states P is a selected-span probability.
These statements do not identify that finite span with all physical bound states.

## 3. Metric norm conservation

Since H=H†, S=S†, and S^-1=(S^-1)†,

\[
SA=-iH-D,\qquad A^\dagger S=iH-D^\dagger.
\]

For the AC solution, the product rule therefore yields a.e.

\[
\frac{d}{dt}(c^\dagger Sc)
=c^\dagger(A^\dagger S+\dot S+SA)c
=c^\dagger(\dot S-D-D^\dagger)c=0.
\]

Absolute continuity implies N=c†Sc=c(t0)†S(t0)c(t0) is constant at all times.
If compatibility is absent, the displayed defect is exactly the missing norm
derivative. It cannot be discarded merely because H is Hermitian.

## 4. Rate form and instantaneous sharp inequality

For fixed J, Gdot=J†Sdot J and (G^-1)dot=-G^-1 Gdot G^-1. Therefore

\[
\begin{aligned}
\dot Q={}&\dot S JG^{-1}J^\dagger S
+SJG^{-1}J^\dagger\dot S\\
&-SJG^{-1}(J^\dagger\dot S J)G^{-1}J^\dagger S.
\end{aligned}
\]

Define W=Qdot+A†Q+QA. W is Hermitian a.e. and

\[
\dot P=c^\dagger Wc.
\]

At such a time, let y=S^1/2 c and C=S^-1/2 W S^-1/2. The Euclidean Hermitian
Rayleigh bound gives

\[
|\dot P|=|y^\dagger Cy|
\leq \|y\|_2^2\|C\|_2
=N\rho,\qquad \rho=\|C\|_2.
\]

This instantaneous bound is sharp over coefficient states of fixed norm: use
an eigenvector of C for an eigenvalue of largest absolute value and convert
back using S^-1/2. Such a maximizer need not follow the actual propagated
trajectory, so sharpness at a time does not establish tightness of an integral
along that trajectory (G06).

Because W is locally integrable and S^-1/2 locally bounded, rho is measurable
and L1_loc. The generalized Hermitian-definite eigenproblem W x=lambda S x
is equivalent to C u=lambda u under u=S^1/2 x. Thus all eigenvalues are real
and rho=max_j |lambda_j|. With S=L L†, an equivalent Hermitian matrix is
L^-1 W L^-†. Numerical implementation should use linear solves rather than
form inverses. Conditioning and floating-point certification are separate G07
questions; mathematical equivalence is not a floating-point error bound.

## 5. Finite-interval integration

For t1 <= t2 in I, P is absolutely continuous on [t1,t2], hence

\[
|P(t_2)-P(t_1)|
=\left|\int_{t_1}^{t_2}\dot P(t)\,dt\right|
\leq N\int_{t_1}^{t_2}\rho(t)\,dt.
\]

For N=1 this is the requested probability bound. For other normalizations the
factor N must remain. When N>0, the normalized population p=P/N obeys the
same factor-free inequality. When N=0, positive definiteness forces c=0 and
all statements are trivial. Since 0<=P<=N, the upper bound can also be capped
at N. None of these conclusions require rho to be smooth.

## 6. Infinite-tail existence and remainder

Suppose I contains [T0,infinity) and rho belongs to L1([T0,infinity)). For any
u>=v>=T>=T0,

\[
|P(u)-P(v)|\leq N\int_v^u\rho
\leq N\int_T^\infty\rho.
\]

The last quantity tends to zero as T tends to infinity. Thus P(t) is a Cauchy
family of real numbers at infinity, so it has a limit P_infinity in [0,N].
For any fixed T>=T0, taking u to infinity in the finite-interval inequality gives

\[
|P_\infty-P(T)|\leq N\int_T^\infty\rho(t)\,dt.
\]

For N=1 this is the requested one-sided tail certificate **conditional on a
valid integrable envelope over the entire half-line**. The same proof after
time reversal applies to an incoming half-line. Incoming and outgoing absolute
bounds must be kept separate; no cancellation is supplied by this theorem.

Integrability is a sufficient condition, not a necessary one. Its absence gives
no general convergence guarantee: S=I, D=0, H=sigma_x, J=e1, c(0)=e1 yields
rho=1 and P(t)=cos(t)^2, which has no limit. Conversely an exact eigenstate can
have constant P even where this state-independent envelope is not integrable.

## 7. Constant basis covariance

For a time-independent nonsingular matrix T, set B'=BT, c'=T^-1 c, and
J'=T^-1 J. Transform every represented quantity consistently:

\[
S'=T^\dagger ST,\quad H'=T^\dagger HT,\quad
D'=T^\dagger DT,\quad \dot S'=T^\dagger\dot ST.
\]

Then G'=G, A'=T^-1 A T, Pi'=T^-1 Pi T, Q'=T†QT, and Qdot'=T†Qdot T.
Consequently W'=T†WT. These follow by substitution and
(T†ST)^-1=T^-1 S^-1 T^-†. It follows immediately that

\[
c'^\dagger S'c'=c^\dagger Sc,\qquad
c'^\dagger Q'c'=c^\dagger Qc.
\]

Moreover W'-lambda S'=T†(W-lambda S)T, so its determinant differs by the
nonzero factor |det(T)|^2. The generalized eigenvalues, rho, and the integral
bound are invariant. Pi transforms by similarity; Q and W transform by
congruence. Treating all three as ordinary Euclidean projectors is incorrect.
After a basis change, keeping the old numerical selector J generally changes
the physical subspace. For time-dependent T, D and A acquire connection terms
and J' has a derivative; the fixed-J formula above must not be reused without
those additional terms. This theorem only claims the constant-T case.

## 8. Units and project scope

With normalized basis-state wavefunctions and dimensionless coefficients, S,
J, G, Pi, Q, N and P are dimensionless. H has energy units; H/hbar, D, A,
Sdot, Qdot, W and rho have inverse-time units. In atomic units hbar=1 and
rho is reported per atomic time. Thus integral rho dt is dimensionless. On a
straight trajectory z=vt with v>0, dt=dz/v; a per-a0 envelope is rho/v.

The proof applies to any finite model satisfying the assumptions, including
the stated 18-channel B0 model if its actual operators satisfy them. It does
not import the N1536 temporal certificate beyond the existing +/-12 a0 window.
No c(t) is supplied at static-tail points, and no old endpoint state is reused.
The eight qualified rho samples or a fitted R^-2 curve do not verify the
continuous-tail hypothesis. G02, G04, G05, G06, G07, G09 and physical gate
dependencies keep their separate requirements.

## 9. Computational checks and provenance

The exact original database row is recorded in CLAIM_UPDATE.json. The earlier
project formulation was inspected at source commit
432010f2afd5305ca63933056f50584c01e4e524, in
`research/foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_tail_rate_20260930/RESEARCH_AND_HANDOFF_KO.md`.
This document supplies the missing regularity, general proof, normalization,
Cauchy tail argument, projector distinction, units and precise limitations.
No external paper is used as a substitute for the direct proof.

The bounded Wolfram evaluation in `symbolic_checks.wls` checks 14 exact
parametric 2-by-2 identities with real t,h1,h2,r,s and r!=0; its full returned
output is preserved. This is a family of symbolic checks, not a proof for
arbitrary n. `symbolic_checks.py` independently replays 78 exact rational
assertions at six parameter substitutions with standard-library Fraction.
The 12 numerical unit tests include a complex 3-by-3 moving basis, independent
centered Q differences showing second-order convergence, an analytically known
physical-coordinate synthetic solution, instantaneous saturation with N=9,
finite/infinite analytic examples, nonunitary covariance, and rejected
compatibility/rank/Hermiticity failures. These tests verify the synthetic audit
kernel only. They are not B0 physical runs and are not outward-rounded numerical
certificates.

The missing-kernel test failed first, then all 12 tests passed after the focused
implementation. The exact commands, package versions, external-call counts and
outputs are preserved in VALIDATION.json and the TDD logs. A Wolfram context
lookup failed before the successful evaluator call and remains recorded.

Claim ceilings remain: capture=false; production=HOLD; all_bound=OPEN;
b_grid=NO_GO; original_capture_gap_resolved=false;
continuous_global_supremum_bound=false; continuous_trajectory_error_bound=false.
