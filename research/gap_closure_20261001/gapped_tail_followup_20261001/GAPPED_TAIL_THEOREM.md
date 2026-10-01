# Gapped asymptotic population: an inverse-square tail bound

The conditional exact reference problem admits an **O(Z^-2) population
remainder**, even though integrating the fixed-selector absolute rate gives
only O(Z^-1). The additional structure is a separated isolated projectile
spectral cluster and a controlled perturbation derivative, supplied below by
the straight-line Coulomb geometry. The proof follows its instantaneous spectral projector,
whose population changes only when that projector changes. It does not assert
that the fixed-selector instantaneous rate itself decays as Z^-3.

This result concerns one exact, conforming finite reference model. No original
B0 selector, archived trajectory, numerical operator, or temporal gate is
replaced. All bounds below concern the **same exact reference state**. The
archived-to-reference observable and dynamical errors remain separate.

## 1. Finite-dimensional theorem with an ordered spectral gap

Let H0 be a self-adjoint operator on a fixed finite-dimensional Hilbert space.
For some 0 < m < n, suppose its first m eigenvalues lie at or below alpha, its
remaining eigenvalues lie at or above beta, and

\[
\Delta=\beta-\alpha>0,\qquad
E_0=\mathbf1_{(-\infty,\tau)}(H_0),\quad
\tau=(\alpha+\beta)/2.
\]

Consider a C1 self-adjoint reference Hamiltonian, in a fixed comoving frame,

\[
H(t)=H_0+c(t)I+W(z(t)),\qquad z(t)=vt,\quad v>0,
\]

with real scalar c, \(\|W(z)\|\le\epsilon(z)\), and a nonincreasing envelope
epsilon on z >= Z. Suppose epsilon tends to zero and 2 epsilon(Z) < Delta.
Set F(z)=H0+W(z) and define E(z) as its **lowest m-dimensional spectral
cluster**, equivalently its spectral projector below the fixed separator tau.
Weyl's eigenvalue bounds give

\[
\operatorname{spec}F_-\le\alpha+\epsilon(z)<\tau,
\qquad
\operatorname{spec}F_+\ge\beta-\epsilon(z)>\tau,
\qquad g(z)\ge\Delta-2\epsilon(z)>0.
\]

E(z) is C1 even when eigenvalues cross within either cluster. One way to see
this locally is the resolvent contour formula around the lower cluster; the
strict gap permits a fixed contour on a neighborhood and differentiation under
the finite-dimensional integral. The neighborhoods patch to the unique rank-m
projector. The scalar c does not change its eigenspaces or commutation with H.

**Do not use the negative-eigenvalue cut at zero for F.** If H0 has lower block
<= -a_minus I and upper block >= d_plus I, then Delta=a_minus+d_plus and
tau=(d_plus-a_minus)/2. The condition 2 epsilon < Delta preserves this cluster,
but can still permit upper-cluster eigenvalues to become negative when
epsilon > d_plus. For H itself the separating energy is tau+c(t).

### Projector distance

On the lower space of H0 let X=(I-E)E0. Commutation of E with F gives

\[
 F_+X-XH_{0,-}=(I-E)WE_0.
\]

The two ordered spectra are separated by at least Delta-epsilon. Subtract a
common scalar energy and solve this Sylvester equation by the convergent
semigroup integral. Its norm is at most RHS norm divided by that separation.
Equal-rank orthogonal projectors have
\(\|E-E_0\|=\|(I-E)E_0\|\), as follows from their principal-angle blocks.
Therefore

\[
\boxed{\|E(z)-E_0\|\le d(z):=
\frac{\epsilon(z)}{\Delta-\epsilon(z)}.}
\tag{1}
\]

This is a one-sided, ordered-cluster Sylvester estimate. A bound on pairwise
eigenvalue separation of arbitrarily interlaced clusters would not justify the
same operator-norm constant; that case is outside this theorem.

### Derivative without an extra factor two

Differentiating E squared = E shows E_z is off diagonal in the E/(I-E)
decomposition. With Y=(I-E)E_z E, differentiation of [F,E]=0 gives

\[
 F_+Y-YF_-=-(I-E)W_zE.
\]

The same semigroup argument yields

\[
\|E_z\|=\|Y\|
\le\frac{\|(I-E)W_zE\|}{\Delta-2\epsilon(z)}.
\tag{2}
\]

The equality is exact: the self-adjoint off-diagonal matrix with blocks Y and
Y dagger has norm ||Y||, not 2||Y||. Any real scalar derivative can be removed:
\((I-E)(W_z-s(z)I)E=(I-E)W_zE\). It is sufficient to supply

\[
\eta(z)\ge\inf_{s\in\mathbb R}\|W_z-sI\|,
\qquad
\int_Z^\infty\frac{\eta(z)}{\Delta-2\epsilon(z)}\,dz<\infty.
\]

An ordinary bound on ||W_z|| is also sufficient but may be unnecessarily large.

### Population limit and remainder

Let i hbar psi_dot = H psi, with conserved squared norm N. Since E commutes
with H,

\[
\frac{d}{dt}\langle\psi,E\psi\rangle
=\langle\psi,\dot E\psi\rangle,
\qquad
\left|\frac{d}{dt}\langle\psi,E\psi\rangle\right|
\le Nv\frac{\eta(z)}{\Delta-2\epsilon(z)}.
\]

The integrability hypothesis makes this population Cauchy at infinity. Because
d(z) tends to zero, the fixed E0 population has the **same limit** P_infinity.
For the same state at z=Z,

\[
\boxed{
|\langle\psi(Z),E_0\psi(Z)\rangle-P_\infty|
\le N\left[
 \frac{\epsilon(Z)}{\Delta-\epsilon(Z)}
 +\int_Z^\infty\frac{\eta(z)}{\Delta-2\epsilon(z)}\,dz
\right].}
\tag{3}
\]

Here psi(Z) denotes the trajectory evaluated at t=Z/v. The v from E_dot cancels
dt=dz/v. No hbar occurs in this bound because the commutator contribution is
exactly zero; neither cancellation assumes an adiabatically slow trajectory.
If the bracket exceeds one, the trivial population range N gives a smaller
valid bound. At a finite pair z2 > z1, add d(z1)+d(z2) and the intervening
variation integral. The incoming tail has the same argument with s=|z| and
reversed orientation, establishing the past limit separately. This does not
identify incoming and outgoing limits with each other.

## 2. Straight-line Coulomb potential with changing direction

Let the projectile reference functions have exact compact support |x| <= a,
and let r(z)=(b,0,z), R=sqrt(b squared + z squared). Within this ball the target
potential, with q >= 0, is V(z,x)=-q/|r(z)-x|. In atomic units q=Z_T; with units
restored it is the Coulomb coupling with dimensions energy times length.
For R>a its range is between -q/(R-a) and -q/(R+a). Subtract its midpoint

\[
c(z)=-\frac{qR}{R^2-a^2},\qquad
W=V-cI,\qquad
\boxed{\epsilon(z)=\frac{qa}{R^2-a^2}.}
\tag{4}
\]

Orthogonal compression into the exact finite reference span cannot increase
this multiplication-operator norm. A nonorthonormal basis must first be given
its exact physical inner product; applying (4) to an arbitrary coefficient
Euclidean norm is not justified.

Differentiate at fixed physical comoving x, not at fixed direction n=r/R:

\[
V_z=q\frac{z-x_z}{|r-x|^3},\qquad
\frac{d}{dz}(-q/R)=qz/R^3.
\]

In particular n_z derivative is nonzero:
\(n'= (e_z-n z/R)/R\), with norm b/R squared. To bound the complete derivative
define the Cartesian vector field A(y)=y/|y| cubed. Its Jacobian is

\[
DA(y)=\frac{I-3\widehat y\widehat y^{\mathsf T}}{|y|^3},
\qquad \|DA(y)\|=2/|y|^3.
\]

The segment r-sx, 0 <= s <= 1, remains at radius at least R-a. The mean-value
integral for A(r-x)-A(r) therefore gives, for every support point,

\[
|V_z-qz/R^3|\le\frac{2qa}{(R-a)^3}.
\]

Although (4) uses midpoint centering, its ordinary W_z norm need not obey this
last formula: the midpoint derivative differs from the monopole derivative.
The required **off-diagonal derivative does** obey it, because their difference
is scalar. Thus a valid choice in (2)-(3) is

\[
\boxed{\eta(z)=\frac{2qa}{(R(z)-a)^3}.}
\tag{5}
\]

This proof includes all direction changes on the straight line. No claim based
on differentiating R alone is used. The synthetic regression explicitly
exhibits a point where the fixed-direction derivative gives a wrong answer.

## 3. Stable rational support-only tail bound

Assume Z>a, R(Z)>2a, and 2 epsilon(Z)<Delta. The R>2a condition is needed for
exact disjoint support of the two-center finite model; R>a alone would suffice
for the single-sector potential estimates. On z >= Z, R>=z and epsilon is
nonincreasing, so

\[
\int_Z^\infty\eta(z)\,dz
\le\int_Z^\infty\frac{2qa}{(z-a)^3}\,dz
=\frac{qa}{(Z-a)^2}.
\]

Substitution in (3) yields the directly computable bound

\[
\boxed{
B(Z)=N\min\left\{1,
 \frac{\epsilon_Z}{\Delta-\epsilon_Z}
 +\frac{qa}{(\Delta-2\epsilon_Z)(Z-a)^2}
\right\},\quad
\epsilon_Z=\frac{qa}{Z^2+b^2-a^2}.}
\tag{6}
\]

Every operation in (6) is rational for rational inputs; there is no square root
or subtraction of nearly equal inverse-trigonometric values. The helper
`gapped_tail.py` uses Fraction throughout, checks the strict hypotheses, and
returns both components and their uncapped sum. Its cutoff search relies on
the monotonic decrease of both positive components and returns the first
integer Z satisfying its own stated formula. This exact final arithmetic does
not itself validate a gap, reference model, operator enclosure, or state.

For fixed a,b,q,Delta and N,

\[
B(Z)=\frac{2Nqa}{\Delta Z^2}\,[1+O(a/Z)+O(Z^{-2})].
\]

The old support-rate integral has leading term Nqa/(hbar v Z), so the leading
ratio is 2 hbar v/(Delta Z). The gain is a power of Z, not a fitted exponent
or a new native sample. The result does not remove the finite bridge from the
archived +/-12 window into the disjoint-support region, nor the cost of any
states that would be needed for a practical cutoff implementation.

### Why the derivative hypothesis is essential

The independent bridge review supplied the following exact discriminator.
With hbar=1, let H0=(Delta/2) sigma_z and

\[
 V(t)=t^{-2}e^{-iH_0t}\sigma_xe^{iH_0t},\qquad t>0.
\]

Its norm is t^-2 and H0+V has gap
\(2\sqrt{\Delta^2/4+t^{-4}}\ge\Delta\). In the interaction picture,
i phi_dot = sigma_x phi / t squared, whose solution with asymptotic state
phi_infinity=(1,i)/sqrt(2) is phi(t)=exp(i sigma_x/t) phi_infinity. The fixed
lower-energy population is therefore

\[
 P_0(t)=\frac12+\frac12\sin(2/t),
\]

and its remainder is O(t^-1), despite the nonclosing gap and O(t^-2)
perturbation amplitude. Here
\(\|V'\|=\sqrt{4t^{-6}+\Delta^2t^{-4}}=O(t^{-2})\), not O(t^-3).
The rotating resonant phase violates the stronger derivative bound used in
(5), so it is not a counterexample to (3) or (6). It rules out claiming the
inverse-square population gain from amplitude and gap alone.

## 4. Application boundary for B0

The reference application uses the isolated **projectile** span with five lower
and four upper channels. It cannot use a global negative/positive spectral gap
for the whole two-center Hamiltonian: target bound states can be degenerate
with projectile ones. For R>128 with a=64, exact disjoint conforming support
makes the two sectors invariant. Apply the theorem to the projectile block,
and extend its projector by zero on the target block. This extended projector
commutes with the block-diagonal full Hamiltonian even without a whole-system
spectral gap. The conserved sector norm N_projectile is at most total norm;
using N=1 is safe for a normalized full reference state.

The sibling exact reference construction supplies a source-pinned lower bound
Delta=a_lower+d_lower, approximately **0.1255525039332252 Hartree**. Its exact
rational value and certificate SHA256 are imported by `build_cutoff.py` and
recorded in `CONDITIONAL_CUTOFF.json`; they are not inferred from archived
energy labels. For a=64, b=2, q=1, N=1 and the already predeclared research
target 5e-6 per side, the smallest integer satisfying (6) is **Z=14312 a0**,
with B approximately **4.999662185996589e-6**. Adding the imported same-state
projector mapping bound 2.768556e-14 leaves that integer unchanged.

This is a **far-tail scale benchmark that spends the full one-side target**.
A nonzero finite bridge must also fit the target, generally requiring a more
distant cutoff or a sharper bound. It is not a certificate from the archived
window. At Z=14312 the old absolute-rate support integral is approximately
0.0022270151, about 445 times larger; its leading-order cutoff for 5e-6 is
approximately 6.3746 million a0. Those old-bound comparison numbers use ordinary
floating arithmetic and the supplied speed 2.00798, whereas (6) is exact
rational arithmetic and independent of speed. A hypothetical Delta=0.1 scenario
is retained separately for reproducibility of the initial exploratory example.
No new physical run or large-cutoff execution plan is adopted.

If a certified same-Hilbert-space projector discrepancy between the archived
observable and E0 is delta_map, then the archived observable on this SAME state
differs from the named reference limit by at most N delta_map+B(Z). If the
archived state and exact reference state differ by e at the cutoff, add
(||psi_arch||+||psi_ref||) e for the projector quadratic form (2e for normalized
states), plus any distinct finite-bridge accounting required by the chosen
comparison. This bound does not integrate delta_map over infinite time.
It does not prove the original fixed-J observable has a limit, nor transfer
the old temporal result to modified dynamics. A small nonzero isolated
commutator still permits the previous perpetual-oscillation counterexample.

Theorem status: **DERIVED, conditional finite-reference result**. Nine focused
synthetic tests verify exact arithmetic, strict rejections, cutoff minimality,
the inverse-square scaling, an analytic two-level projector and derivative,
the moving-direction Coulomb derivative, and a same-state finite-interval
population inequality under an independent DOP853 synthetic trajectory. They
also preserve the counterexample to an incorrect zero-energy cluster cut and
bind the computed cutoff to the exact sibling reference certificate hash.
The ninth test verifies the resonant counterexample and the missing derivative
condition, independently of the helper's formula.
No physical continuous majorant/tail certificate is issued by this folder.
