# Conditional repair: certify a nearby invariant observable without integrating a constant defect

**Derived outcome.** A validated residual plus a separated spectral gap can
bound the distance from the current selected subspace to an exactly invariant
isolated spectral subspace. That distance gives a **uniform observable error**.
It need not be integrated over infinite time. This provides a precise possible
repair of the analytic-reference blocker. It does not establish convergence of
the original fixed-J observable, change J, or close any physical gate.

The mathematical argument below is proved directly in the project notation;
no literature theorem is being used as a substitute for a proof. The actual
operator-execution source pin is `01ec2ba7e71aefdccab1896acfe5d92c15c6b776`;
`432010f2afd5305ca63933056f50584c01e4e524` is the research/derivation context.
Individual files retain the SHA256 pins in `ROUTE_A_STATUS.json`.

## 1. Objects that must be fixed before computing a bound

Choose a well-defined exact isolated reference finite space with SPD Gram S0
and self-adjoint H0. Both objects must include a specified mathematical
interpretation of the archived radial coefficients, not merely a floating
matrix printed to a file. Let

\[
 F=S_0^{-1/2}H_0S_0^{-1/2},\quad
 U=S_0^{1/2}J(J^\dagger S_0J)^{-1/2},\quad P=UU^\dagger.
\]

Then U†U=I. Complete U to a unitary [U,V], and write

\[
 [U,V]^\dagger F[U,V]
 =\begin{pmatrix}A&R^\dagger\\R&D\end{pmatrix},
 \quad A=U^\dagger FU,\quad D=V^\dagger FV,\quad R=V^\dagger FU.
\]

This note's D is a **complementary isolated Hamiltonian block**, not the moving-
basis derivative matrix D in the main project equations. The certificate schema
calls it `H_complement_block` to avoid that ambiguity.

Suppose a validated enclosure establishes

\[
 A\le-aI,\qquad D\ge dI,\qquad \|R\|_2\le r,
 \qquad a>0,\ d>0.
\]

These are matrix inequalities for the exact reference. Saved energy labels,
ordinary residuals, and agreement of high-precision runs are not by themselves
validated enclosures. Other negative unselected modes would invalidate D≥dI;
therefore apply this construction to the **projectile isolated retained span**,
not the full two-center block containing target bound states. For current B0 the
semantic split has five projectile negative and four positive retained channels.
Its complete angular multiplets must be preserved.

## 2. Residual/gap projector theorem and proof

Let m=rank(P). By the min-max principle applied to the m-dimensional U space,
lambda_m(F)≤−a. Applied to the complementary space it gives
lambda_(m+1)(F)≥d. Thus F has exactly m negative eigenvalues and its negative
spectral projector E has the same rank as P; the spectral gap is at least a+d.
Equivalently, these signs also follow by the Schur complement because D>0 and
A−R†D⁻¹R<0.

Let X=(I−E)U and let Fplus be F restricted to ran(I−E). The exact residual
identity FU−UA=VR gives the Sylvester equation

\[
 F_+X-XA=(I-E)VR=Y.
\]

Since Fplus≥dI and A≤−aI, its unique solution is

\[
 X=\int_0^\infty e^{-tF_+}\,Y\,e^{tA}\,dt.
\]

Differentiate the integrand and integrate its decaying endpoints to verify the
equation. The operator-norm bound follows immediately:

\[
 \|X\|_2\le\|Y\|_2\int_0^\infty e^{-(a+d)t}dt
 \le{r\over a+d}.
\]

For equal-rank orthogonal projectors, their difference has eigenvalues ±sin
(theta_j) on each principal-angle plane. The same sine values are the singular
values of (I−E)U; intersections contribute zeros. Hence

\[
 \boxed{\|P-E\|_2\le\delta:=\min\{1,r/(a+d)\}.}
\]

This is a residual/gap bound with an explicit separation assumption. It does
not infer the gap from a small residual. The exact-rational helper
`projector_distance_enclosure` only performs the last bound arithmetic; it
neither computes E nor validates the input matrix inequalities.

If a rigorously enclosed approximate block representation has spectral-norm
error at most eta, Weyl/variational inequalities allow conservative
`a=a_nominal−eta`, `d=d_nominal−eta`, `r=r_nominal+eta`, provided both resulting
a,d stay positive and nominal bounds themselves are enclosing. A perturbation
in S0 requires its own validated whitening/subspace enclosure; it cannot be
silently included as an H-only residual.

## 3. Uniform observable error, and what it implies at infinity

For any common state psi of squared norm N,

\[
 \boxed{|\langle\psi,P\psi\rangle-
             \langle\psi,E\psi\rangle|\le N\delta.}
\]

This is simply the quadratic-form spectral bound. It holds at every time
without integrating r, and is unchanged when both projectors are transported
by the same unitary translation/ETF convention. If the original archived
physical projector P_original differs from the current-projector representation
P in the reference space by an independently certified eta_P, replace delta by
`delta_total=min(1,eta_P+delta)`. This extra term is required if conforming
reference functions differ from literal stored polynomial functions.

Suppose the E-observable has a separately certified integrable rate envelope,
with e_E(T)=integral_T^infinity rho_E dt, and norm N is conserved. Then P_E has
a limit P_E,infinity, and

\[
 |P_{original}(T)-P_{E,\infty}|
 \le N(\delta_{total}+e_E(T)).
\]

For any two finite t2≥t1≥T,

\[
 |P_{original}(t_2)-P_{original}(t_1)|
 \le N\{2\delta_{total}+\int_{t_1}^{t_2}\rho_E dt\}.
\]

Therefore the repaired certificate targets a **named reference asymptotic
observable**, with a bounded mapping discrepancy. It does not prove that
P_original itself has a limit; its limiting oscillation diameter is at most
2N delta_total if the reference limit exists. Do not write
P_original,infinity unless its separate existence has been established.

These comparisons use the same physical state. If the archived numerical
state and the reference dynamical state differ, their difference needs a
separate bound. For normalized states its probability contribution is at most
2||psi_numerical−psi_reference||; more generally it is bounded by the sum of
state norms times their distance. Static selector repair is not a dynamics
error certificate and does not transfer the old temporal gate to a new model.

## 4. Explicit two-state obstruction

Take

\[
 F=\begin{pmatrix}-a&r\\r&d\end{pmatrix},\quad
 P=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad r>0,
 \quad\Omega=\sqrt{(a+d)^2+4r^2}.
\]

For initial state (1,0), unitary isolated evolution gives

\[
 P_J(t)=1-{4r^2\over\Omega^2}\sin^2(\Omega t/2).
\]

It oscillates forever and has no limit. In contrast, the exact negative
spectral projector E commutes with F, so its population is constant. Their
projector distance is

\[
 \|P-E\|_2=
 \sqrt{\tfrac12[1-(a+d)/\Omega]}\le r/(a+d).
\]

The four focused regression tests verify this example, the uniform observable
inequality (including a state attaining its projector-norm bound), positivity
conditions, and exact rational residual/gap arithmetic. This is a mathematical
counterexample, not a statement that a B0 trajectory has observable oscillations
of the displayed size.

## 5. Minimal certificate and identity boundary

`REFERENCE_SELECTOR_CERTIFICATE_CONTRACT.json` specifies the conditional return
schema. Required new evidence is limited to:

1. The exact reference definition and same physical Hilbert-space embedding.
2. A validated S0 lower bound plus self-adjointness and exact unitary connection
   assumptions relevant to the intended tail theorem.
3. Validated projectile negative/positive block bounds a,d and residual r, with
   the five-versus-four semantic rank checked independently.
4. Any physical-projector mapping bound eta_P and its provenance.
5. A new reference selector identity/hash and its observable definition.
6. A validated finite bridge and analytic remainder for that selector.

No new basis, selector, or projector has been installed. Any adopted reference
selector gets a new identity; changes of basis/model require new operator and
temporal qualification under G09/G10. Prior B0 indices and certificates remain
historical authorities for their original observable. A static projected-
observable mapping certificate must not be reported as a replaced physical run.

The root error budget now predeclares a **research target** of 1e−5 total tail
probability, split 5e−6 per side, in `../ERROR_BUDGET_CURRENT_B0.json`. This
follow-up does not enlarge it or choose a value after new physical evidence.
Any selector mapping allowance must fit the existing target or a separately
predeclared named observable-mapping component; it cannot be omitted or silently
charged twice. No physical value for delta or eta_P is certified here.

Status: conditional theorem DERIVED; four synthetic tests NUMERICALLY_CHECKED.
G04/G05 stay UNRESOLVED. The exact-reference blocker now has a bounded repair
contract, and no claim of the original fixed-J asymptotic limit is introduced.
