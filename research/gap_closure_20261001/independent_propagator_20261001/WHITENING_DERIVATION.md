# Cholesky derivative and a fourth-order independent-family reference

## Exact metric connection

Let S(t) be Hermitian positive definite and differentiable; the same derivative
statements hold almost everywhere for locally absolutely continuous S with
compact-interval coercivity. Take its unique upper Cholesky factor R with positive
real diagonal, S=R†R. Define y=Rc for cdot=A c. Then

\[
\dot y=\mathcal B y,\qquad
\mathcal B=\dot R R^{-1}+RAR^{-1}.
\]

The Cholesky factor is differentiable on the open positive-definite cone. To
compute its derivative, multiply the differentiated factorization by R^-† and
R^-1:

\[
E=R^{-\dagger}\dot S R^{-1}=X^\dagger+X,
\qquad X=\dot R R^{-1}.
\]

X is upper triangular, and X_ii=Rdot_ii/R_ii is real because the diagonal of R
is real and positive. Hence this equation has the unique solution

\[
X_{ij}=\begin{cases}E_{ij}&i<j,\\ E_{ii}/2&i=j,\\0&i>j.\end{cases}
\qquad\dot R=XR.
\]

With Ht=R^-† H R^-1 and Dt=R^-† D R^-1, and hbar=1,

\[
RAR^{-1}=-iH_t-D_t,\qquad
\mathcal B=X-D_t-iH_t.
\]

If H=H† and Sdot=D+D†, then Ht is Hermitian and E=Dt+Dt†, giving

\[
\mathcal B+\mathcal B^\dagger
=E-D_t-D_t^\dagger=0.
\]

Thus exact metric transport becomes Euclidean unitary transport. Omitting X
generally makes the generator non-anti-Hermitian and changes the ODE; simply
antisymmetrizing that incorrect generator also changes the ODE. More generally,
without compatibility,

\[
\mathcal B+\mathcal B^\dagger
=R^{-\dagger}(\dot S-D-D^\dagger)R^{-1}
\]

for Hermitian H. This exposes the defect rather than repairing it. The reference
implementation uses two triangular solves per transformed matrix; it neither
forms an inverse nor diagonal-shifts S. It rejects non-SPD S, non-Hermitian
S/H/Sdot, or a compatibility defect beyond the declared float64 input check.
This tolerance is not a validated numerical bound.

The existing `metric_transport.metric_frame_generator` already implements the
same Cholesky connection using E=Dt+Dt†. Its formula is retained unchanged.
The new audit accepts Sdot explicitly to test this identity against a separate
synthetic derivative. Such a synthetic test does not close physical G02.

## CF4 construction and order

For ydot=B(t)y, on a step of length h take the two Gauss nodes
c1=1/2-sqrt(3)/6, c2=1/2+sqrt(3)/6 and B_j=B(t+c_j h). Put
a1=(3-2sqrt(3))/12 and a2=(3+2sqrt(3))/12. The step is

\[
y(t+h)\approx
e^{h(a_1B_1+a_2B_2)}
e^{h(a_2B_1+a_1B_2)}y(t).
\]

The rightmost exponential acts first. Real coefficients preserve
anti-Hermiticity of each exponent; the negative a1 is not a hidden clipping or
modification. Exact exponentials are unitary. Floating-point norm drift is
measured separately.

To derive the order, expand at the step midpoint with B0=B(tm), B1d=B'(tm),
B2d=B''(tm). The late-weighted and early-weighted exponents are

\[
X=\tfrac h2B_0+\tfrac{h^2}{6}B_{1d}
+\tfrac{h^3}{48}B_{2d}+O(h^4),\qquad
Y=\tfrac h2B_0-\tfrac{h^2}{6}B_{1d}
+\tfrac{h^3}{48}B_{2d}+O(h^4).
\]

The BCH logarithm through degree three is

\[
X+Y+\tfrac12[X,Y]
=hB_0+\tfrac{h^3}{24}B_{2d}
-\tfrac{h^3}{12}[B_0,B_{1d}]+O(h^5).
\]

The omitted nested-commutator terms of total degree four cancel between X and Y.
The composition is time symmetric: reversing the interval reverses node order
and negates both exponents, producing the inverse map. Thus its midpoint
logarithm contains no even powers. The displayed expression equals the Magnus
logarithm through degree three. For a sufficiently smooth bounded generator
(e.g. C4 on the compact test interval), the one-step defect is O(h^5), and a
stable finite-interval propagation has global error O(h^4). This is a local
asymptotic order derivation, not a numerical error constant or physical global
certificate. The analytic synthetic trajectory is smooth and avoids the
commuting-generator degeneracy; observed halving ratios independently test the
stage order and coefficients.

The prior candidate is exponential midpoint (order two). The prior reference
is adaptive direct-coefficient DOP853. DOP853 and CF4 have different error
structures, coordinate representations and time sampling; CF4 and midpoint
share matrix-exponential machinery. Therefore the independence claim rests on
comparison with the direct DOP853 lane and the analytic solution, not merely on
renaming an exponential midpoint update.

## Exact synthetic benchmark

Write the moving basis as F(t)=V(t)R(t), with nonconstant upper-triangular R,
positive real diagonal, and V=exp(-i gamma(t) sigma_y). The physical exact
unitary is U=exp(-i phi(t) sigma_z) exp(-i theta(t) sigma_x). Its Hermitian
Hamiltonian is

\[
h=\phi'\sigma_z+\theta'e^{-i\phi\sigma_z}
\sigma_x e^{i\phi\sigma_z}.
\]

Set S=F†F, D=F†Fdot, H=F†hF, and independently evaluate
Sdot=Rdot†R+R†Rdot. For the fixed normalized vector v, c_exact=F^-1 Uv.
Differentiation proves cdot=-S^-1(iH+D)c, so all three numerical methods and
the analytic solution solve the same ODE. The trigonometric coefficient
functions, initial vector and interval [0,3] are explicit in the script.
The selected synthetic span uses J=e1 and the same metric quadratic-form
observable as G01. It is not the physical 18-channel B0 span.

Synthetic norm and convergence evidence says nothing by itself about native
operator interpolation, physical state identity, production tolerances, or
finite-window capture. Those remain prerequisites for a physical comparison.
