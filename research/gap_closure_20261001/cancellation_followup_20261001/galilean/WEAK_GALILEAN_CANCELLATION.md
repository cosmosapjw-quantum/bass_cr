# Exact Galilean cancellation and the finite weak residual that remains

The kinetic ETF terms and the moving-basis connection cancel **before taking
norms**, for all matrix rows including cross-center rows. In an overlapping
two-center finite basis, the exact selected rate reduces to two objects:

1. the isolated **weak Galerkin residual**, tested against the other center;
2. the off-diagonal action of the other-center Coulomb potential.

The first is generally nonzero even when the isolated matrix eigenproblem is
solved exactly. The second is bounded directly in physical L2 and does not need
an inverse-Gram amplification factor. These facts give a source-bound reference
rate estimate rho≤8409/800=10.51125 and a raw integrated-rate bound
25227/50=504.54 on each bridge from |z|=32 to128. This improves the previous raw
bound55408/11≈5037.09. **Both corresponding probability-difference bounds remain
one after the trivial cap.** Neither certifies the target5×10^-6; no practical
probability gate is closed by this improvement.

All statements concern the already named exact conforming reference and its
invariant isolated negative projectile selector. No archived basis, selector,
operator, trajectory, threshold, or native approval is changed. Units below are
atomic, hbar=1. This folder performs only small exact algebra and imports saved
exact certificates; it contains no new quadrature or HPC hot loop.

## 1. Source conventions and the weak cancellation theorem

The inspected source `two_center.py:basis_values` uses, for center b with
constant velocity v_b,

\[
\chi_b(x,t)=e^{i v_b\cdot x-i|v_b|^2t/2}\,
\phi_b(x-R_b(t)),\qquad R_b(t)=R_b(0)+v_bt,
\]

\[
\dot\chi_b=U_b[-v_b\cdot\nabla\phi_b-i|v_b|^2\phi_b/2],
\quad D_{ab}=\langle\chi_a,\dot\chi_b\rangle,
\quad K=H-iD.
\]

U_b denotes the full unitary translation/ETF map on physical functions. Assume
the unboosted functions are compactly supported H1 functions, and use the exact
weak Coulomb form for H. Let

\[
h_b(\eta,f)=\frac12\langle\nabla\eta,\nabla f\rangle
-Z_b\langle\eta,|x|^{-1}f\rangle.
\]

For every H1 test function eta, the distributional Galilean identity is

\[
\boxed{(H_{\rm lab}-i\partial_t)U_b f
=U_b[h_b^{\rm dist}f+V_{{\rm other},b}f].}
\tag{1}
\]

Here h_b^dist maps H1 into H^-1; it is not asserted to be an L2 operator action.
For smooth functions, expansion of the Laplacian gives

\[
-\tfrac12\Delta(U_bf)
=U_b[-\tfrac12\Delta f-i v_b\cdot\nabla f+|v_b|^2f/2],
\]

while i dot(U_bf)=U_b[-i v_b·grad f+|v_b|²f/2]. Subtraction cancels both
velocity terms exactly. Multiplication by either Coulomb potential is compatible
with the translation/phase. Approximation in H1 extends this distributional
identity to the reference functions; Hardy's inequality makes the Coulomb forms
continuous on H1.

Equivalently, with eta_ab=U_b†chi_a in the column-center frame,

\[
\boxed{K_{ab}=h_b(\eta_{ab},\phi_b)
+\langle\chi_a,V_{{\rm other},b}\chi_b\rangle.}
\tag{2}
\]

This holds even when v_a differs from v_b and the supports overlap. It does not
replace a cross weak integral by a stored isolated eigenvalue.

An independent one-dimensional algebra check makes the cross-row boundary
term explicit. Omitting the common phase exp(i(v_b−v_a)x), expansion of H_kin−iD
minus the column-centered weak kinetic form gives

\[
\frac{i v_b}{2}(\overline{a'}b+\overline a b')
-\frac{v_b(v_b-v_a)}2\overline a b.
\]

With its phase restored, this is exactly
(i v_b/2) d_x[exp(i(v_b−v_a)x)conj(a)b]. Its integral vanishes for compact H1
functions. Value-continuity matters: nonzero FEM trace jumps would produce
additional interface terms. Derivative jumps are retained within h_b^dist;
they do not spoil this first-derivative weak cancellation.

The same-center source identity
H−iD=H0+V_other+(i/2)(vA†+vA) is a special case. For exact conforming functions,
A is skew Hermitian by integration by parts, so the last term vanishes.
Finite quadrature arrays need not satisfy this identity exactly; their defects
cannot be silently repaired or declared zero by the continuum theorem.

## 2. Isolated matrix action and the residual against foreign tests

Let Phi_b map the retained one-center coefficients to unboosted physical
functions, let M_b=Phi_b†Phi_b, and define the exact isolated Galerkin operator

\[
F_b=M_b^{-1}H_b,\qquad (H_b)_{ij}=h_b(\phi_i,\phi_j).
\]

For f=Phi_b c define its weak residual functional

\[
r_{b,c}(\eta)=h_b(\eta,\Phi_bc)
-\langle\eta,\Phi_bF_bc\rangle.
\tag{3}
\]

By construction r_{b,c}(eta)=0 for every eta in the retained **same-center**
span. No assertion follows for translated/phase-shifted functions from another
center. Equation(2) yields the full coefficient identity

\[
\boxed{K=S F_{\rm block}+R+V^{\rm column},}
\tag{4}
\]

where R_ab=r_{b,e_b}(U_b†chi_a), and the potential in each column is the nucleus
other than that column's center. The residual's own-center row blocks vanish;
cross-center row blocks generally do not.

This residual is not the tiny residual of a finite matrix eigensolver. An exact
C0 piecewise-polynomial function typically has jumps in its normal derivative.
Its distributional Laplacian then contains shell delta distributions. The
strong residual need not belong to L2, despite the well-defined H^-1 functional
and exact Galerkin annihilation. The sibling regularity track gives additional
source-specific shell and origin evidence; this theorem does not assume H2.

An exact elementary discriminator uses f(x)=1−|x| on[-1,1], extended by zero,
and h=−(1/2)d²/dx². Its one-function Galerkin eigenvalue is
lambda=(1/2)∫|f'|²/∫|f|²=3/2, so r(f)=0 exactly. For the H1 test
eta(x)=1−x² on the same interval, h(eta,f)=1 and <eta,f>=5/6, hence

\[
r(\eta)=1-\frac32\frac56=-\frac14.
\]

The distributional kinetic action is delta_0−(delta_-1+delta_1)/2, not an L2
function. This counterexample rules out replacing(3) by zero or by an L2
eigenvector residual norm merely because the matrix eigenproblem closes.

## 3. Selected Schur residual after the exact cancellation

Use a fixed coefficient selector J spanning an invariant isolated projectile
subspace: F_P J_P=J_P Lambda. For the intended candidate this is the exact
negative spectral subspace, not the original unrepaired fixed index selector.
Choose complementary coefficient columns and order selected columns first:

\[
S=\begin{pmatrix}G&B^\dagger\\B&C\end{pmatrix},\qquad
T=C-BG^{-1}B^\dagger\succ0.
\]

Here B has complement rows and selected columns. The sibling projector report
uses the adjoint orientation for its B; the two formulas are equivalent.
Equation(4), the same-center residual annihilation, and isolated invariance give

\[
K_{ss}=G\Lambda+V_{ss},\qquad
K_{cs}=B\Lambda+R_{cs}+V_{cs},\qquad R_{ss}=0.
\]

Thus the exact off-diagonal selected-rate factor is, up to the irrelevant
unit-modulus factor i,

\[
\boxed{\rho=
\left\|T^{-1/2}
\left[R_{cs}+V_{cs}-BG^{-1}V_{ss}\right]G^{-1/2}\right\|.}
\tag{5}
\]

The same formula may use Cholesky-whitened factors, which differ only by
unitaries. Isolated energies disappear as B Lambda−BG^-1G Lambda=0.
Any scalar potential shift V→V−cI disappears as cB−BG^-1cG=0. The selected
population rate has one such off-diagonal norm, not twice the norm. Its general
fixed-selector derivation and factorization are proved in the sibling projector
folder; here the new content is the weak Galilean reduction of its numerator.

R_cs has target rows only: residual tests against all retained projectile
functions, including its unselected positive subspace, vanish. After exact
disjoint support R>128, the cross weak integrals also vanish, so R_cs=0.
No small constant isolated eigensolver residual needs to be integrated in this
reference formulation. This statement uses the exactly invariant selector and
does not establish an asymptotic limit for the original fixed-J observable.

## 4. Potential leakage is a physical projection, with no Gram penalty

Let U_s be an isometry onto the selected physical span, P_s=U_sU_s†, and let
P_tot project onto the complete finite two-center span. Orthogonalizing the
complement columns gives the isometry Q_c whose coefficient factor is T^-1/2.
The potential part of(5) is exactly

\[
Q_c^\dagger V U_s,
\qquad
\|Q_c^\dagger V U_s\|
=\|(P_{\rm tot}-P_s)VU_s\|.
\]

Since ran(P_s) is contained in ran(P_tot), their difference is an orthogonal
projector. Consequently

\[
\boxed{\rho_V\le\|(I-P_s)VU_s\|
\le\inf_{c\in\mathbb R}\|(V-c)U_s\|.}
\tag{6}
\]

There is no factor s0^-1/2 or s0^-1 in this physical bound. The apparent inverse
metric in the coefficient expression is cancelled by normalization of the
physical test subspace. This conclusion applies because Coulomb multiplication
of the selected H1 functions belongs to L2; it does not justify replacing the
weak isolated residual in(3) by a global L2 vector.

For unit remote charge, translated Hardy gives
||V f||=||f/|x-a|||≤2||grad f||. The common ETF phase has modulus one, so this
can be applied directly to the unboosted selected function. If its gradient
operator norm is bounded by L, then rho_V≤2L uniformly, including when the
other nucleus lies inside the support. No false pointwise Coulomb supremum is
used. Outside support overlap, more useful centered-potential bounds remain
available and recover the earlier dipole-scale far-tail analysis.

## 5. A finite-test H1 residual bound using saved exact certificates

Use separately orthonormalized one-center coordinates and the exact spectral
rotation within the projectile span. Then G=I, and the previous ETF certificate
gives S≥s0I with s0=33/100. Minimizing the Gram quadratic form over selected
coefficients proves T≥s0I. Hence

\[
\rho_R\le s_0^{-1/2}\|R_T\|,
\tag{7}
\]

where R_T comprises only the target-test rows of the weak residual. This is a
finite test-space bound, not a global norm for h_b^dist f.

For a normalized target coefficient vector and selected projectile vector,
write the target test in the projectile frame as
eta=exp(−iv z_lab)f_T, up to translation and a scalar phase. The derivative
term in(3) obeys

\[
\tfrac12|\langle\nabla\eta,\nabla f_P\rangle|
\le\tfrac12 L^2+\tfrac12vL_z.
\]

The first term pairs unboosted gradients; the second pairs a normalized target
function with the directional derivative of the selected projectile function.
The own-center Coulomb term is at most2L by Hardy. If the physical isolated
Galerkin operator has norm at most M, its subtraction term is at most M.
These are uniform bilinear bounds in both normalized coefficient vectors, so
no factor equal to the number of target channels is required:

\[
\boxed{\|R_T\|\le L^2/2+vL_z/2+2L+M.}
\tag{8}
\]

The following conservative rational constants are independently checked against
the already saved exact certificate endpoints:

\[
L\le6/5,\qquad L_z\le67/100,\qquad 2\le v\le3,\qquad
M\le51/100,\qquad s_0\ge33/100,\qquad s_0^{-1/2}\le7/4.
\]

The first two come from the full retained-bank gradient certificates; restriction
to the selected spectral subspace cannot increase their norms. The M bound uses
the exact interval row-norm upper bound of the saved isolated weak H matrix
divided by the saved positive mass lower bound. Angular multiplet replication
does not change the operator norm. No physical matrix is freshly assembled.

Equations(6)–(8) now give exact arithmetic:

\[
\|R_T\|\le927/200,\quad
\rho_R\le6489/800,\quad \rho_V\le12/5,
\quad
\boxed{\rho\le8409/800=10.51125.}
\]

For a96-a0 signed bridge and v≥2,

\[
\boxed{\int\rho\,dt\le\frac{96}{2}\frac{8409}{800}
=\frac{25227}{50}=504.54.}
\]

This improves the raw integrated-rate majorant. However, the old and new
probability bounds both reduce to1 after applying the elementary population
range. The comparison supplies **no newly useful certified probability accuracy**
at the5×10^-6 target. The remaining mathematical task is a much sharper estimate
of the foreign-test weak residual and centered selected potential coupling,
preserving their cancellations. Neither a native eigensolver residual nor a
fit to point rates can replace those continuum estimates.

## 6. Validation, first rejection, and unchanged boundaries

The tests were written first; the captured red run failed because the new
implementation module did not exist. Five targeted exact tests then passed:
cross-velocity weak boost boundary identity and missing-phase discriminator;
isolated/scalar Schur cancellation; absence of a potential metric penalty;
the nonzero foreign-test weak residual despite exact one-function Galerkin
closure; and the rational reference-bound arithmetic and guard.

The first certificate build also rejected a real provenance ambiguity: the
older reference certificate used a canonical compact-JSON coefficient hash,
whereas older bridge/ETF certificates used the exact pretty-file hash under
the same field name. The additive new certificate rechecks both identities
from the same saved reference file and records them separately. Canonical hash
85166a… and file hash9471aa… agree with their respective documented serializers;
there was no coefficient change. `FIRST_ADMISSION_FAILURE.json` preserves the
rejection. No historical certificate was edited.

The implementation uses Fraction for a few small matrices and exact certificate
comparisons. Per the HPC policy these operations remain small exact algebra;
no artificial MPI work distribution or new Python quadrature loop is introduced.
There are zero new native calls, physical operator queries, and physical
propagations. The candidate reference has not been adopted, and the old temporal
gate has not been transferred. All existing physical claim ceilings remain.
