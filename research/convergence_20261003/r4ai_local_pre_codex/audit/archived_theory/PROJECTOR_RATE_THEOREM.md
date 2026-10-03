# Cancellation-preserving selected-projector rate and angle budget

R4T, 2026-10-01. Status: **DERIVED**, with exact finite-dimensional replay and
synthetic FP64 implementation checks. This is a conditional finite-model
theorem. It supplies an exact factorization of the G01 rate, a cancellation
route for G04/G05, and a sharper conditional G06 population-change envelope.
It does not supply a B0 trajectory, physical overlap derivative, continuous
majorant or propagation-error certificate.

## 1. Definitions and assumptions

Let \(S(t)\) be a positive definite \(n\times n\) Hermitian matrix, locally
absolutely continuous on an interval. Let \(H=H^\dagger\) and \(D\) be locally
integrable, with
\[
\dot S=D+D^\dagger,\qquad
\dot c=A c,\qquad
A=-S^{-1}(D+iH/\hbar),\qquad \hbar>0.
\]
Here \(H\) has energy units, whereas \(D,\dot S,A\) have inverse-time units.
The basis coefficients and overlaps use the same conventions as G01. There is
no replacement of an independently evaluated \(\dot S\) by a defining identity.
That distinction remains essential for physical G02.

Let \(J(t)\) be locally absolutely continuous, \(n\times k\), full column rank
at every time, with \(1\le k\le n\). The project already uses a fixed selector;
allowing \(\dot J\) here states the connection term required by a moving change
of coordinates. Define
\[
G=J^\dagger S J,\quad
\Pi=J G^{-1}J^\dagger S,\quad
Q=S\Pi,\quad N=c^\dagger S c,\quad P=c^\dagger Qc.
\]
Thus \(\Pi^2=\Pi\), \(\Pi^\dagger S=S\Pi\), \(0\le P\le N\), and \(N\) is
constant. G01 proves existence and these identities for fixed \(J\); local
absolute continuity and inversion of the positive definite \(G\) extend the
same statements to this moving selector. All differential statements below
hold almost everywhere; the integrated inequalities hold at all endpoints.

Use
\[
W=\dot Q+A^\dagger Q+QA,\qquad
\rho=\|S^{-1/2}W S^{-1/2}\|_2.
\]
For fixed \(J\), this is exactly the G01 \(W,\rho\), including its sign
convention. \(Q\) is a quadratic-form matrix, not an ordinary projector.

## 2. Exact off-diagonal factorization

Choose matrices \(X\) and \(Y\) whose columns span the selected subspace and
its \(S\)-orthogonal complement, normalized so that
\[
X^\dagger SX=I_k,\quad Y^\dagger SY=I_{n-k},\quad X^\dagger SY=0.
\]
Write \(G=L_G L_G^\dagger\), with \(L_G\) lower triangular, and choose
\(X=J L_G^{-\dagger}\). At each time define
\[
\boxed{\;
E=Y^\dagger\big[(D+iH/\hbar)J+S\dot J\big]L_G^{-\dagger}.
\;}
\tag{1}
\]
Then
\[
\boxed{\quad
[X,Y]^\dagger W[X,Y]
=\begin{pmatrix}0&E^\dagger\\E&0\end{pmatrix},
\qquad \rho=\|E\|_2.
\quad}
\tag{2}
\]
There is **no factor of two** in the equality for \(\rho\).

To prove it without differentiating any matrix square root, introduce
\(\mathcal L=\dot\Pi+[\Pi,A]\). Metric compatibility gives
\[
W=S\mathcal L:
\quad
\dot S\Pi+S\dot\Pi+A^\dagger S\Pi+S\Pi A
=S(\dot\Pi-A\Pi+\Pi A).
\]
Differentiating \(\Pi^2=\Pi\) shows
\(\Pi\dot\Pi\Pi=0\) and
\((I-\Pi)\dot\Pi(I-\Pi)=0\). The commutator with \(\Pi\) has the same
zero diagonal blocks. Hence \(\mathcal L\), and therefore \(W\) in an
\(S\)-orthonormal selected/complement frame, has zero diagonal blocks.
Differentiating \(\Pi J=J\) gives
\[
\dot\Pi J=(I-\Pi)\dot J,\qquad
\mathcal L J=(I-\Pi)(\dot J-AJ).
\]
Multiplication by \(Y^\dagger S\), followed by the selected normalization,
gives (1). Hermiticity of \(W\) supplies its upper block \(E^\dagger\).

Finally \(U=S^{1/2}[X,Y]\) is unitary. The matrix in (2) is unitarily
equivalent to \(S^{-1/2}WS^{-1/2}\). Its square is
\(\operatorname{diag}(E^\dagger E,EE^\dagger)\); its nonzero eigenvalues
are the pairs \(\pm\sigma_j(E)\), with any remaining eigenvalues zero.
This proves the asserted norm equality. If \(k=n\), the complement and \(E\)
are empty, \(P=N\), and \(\rho=0\).

For a fixed selector this simplifies to
\[
E=Y^\dagger(D+iH/\hbar)X.
\tag{3}
\]
The Hamiltonian and connection terms must be combined **before taking their
norm**. Bounding them independently generally discards a physical
cancellation. Adding a scalar energy \(\lambda(t)S\) to \(H\) changes (3)
by \(i\lambda Y^\dagger SX/\hbar=0\). A common scalar phase connection likewise
drops out. More generally, the rate is zero exactly when
\[
(D+iH/\hbar)J+S\dot J\ \in\ \operatorname{ran}(SJ),
\]
equivalently \((I-\Pi)(\dot J-AJ)=0\): the selected subspace is transported
invariantly by the finite-model dynamics.

## 3. Schur-complement computational form

Choose any \(n\times(n-k)\) completion \(K\) for which \([J,K]\) is nonsingular.
Set
\[
B=J^\dagger SK,\quad C=K^\dagger SK,\quad
U_K=K-JG^{-1}B,\quad
M=C-B^\dagger G^{-1}B=U_K^\dagger S U_K>0.
\]
With \(M=L_M L_M^\dagger\), put \(Y=U_K L_M^{-\dagger}\). If
\(\mathcal F=(D+iH/\hbar)J+S\dot J\), then
\[
\boxed{\quad
\mathcal R=K^\dagger\mathcal F
 -B^\dagger G^{-1}J^\dagger\mathcal F,\qquad
E=L_M^{-1}\mathcal R L_G^{-\dagger}.
\quad}
\tag{4}
\]
The small matrices \(G,M\) are positive definite by the hypotheses. The
reference implementation uses Cholesky and triangular/positive-definite solves,
never explicit inverses, pseudoinverses, diagonal shifts or metric repairs.
It evaluates \(M\) as \(U_K^\dagger S U_K\), avoiding another subtraction of
two large positive matrices. The selected-span subtraction in \(\mathcal R\)
is performed before whitening or taking norms.

Equation (4) retains two distinct cancellations: between \(D\) and \(iH/\hbar\),
and between the raw complement block and its selected-span projection. For
example, with
\[
S=\begin{pmatrix}4&2\\2&5\end{pmatrix},\quad
J=e_1,\quad K=e_2,\quad
B_{\rm phys}=\begin{pmatrix}2&1\\0&2\end{pmatrix},\quad
H=B_{\rm phys}^\dagger
\begin{pmatrix}a&g\\g&b\end{pmatrix}B_{\rm phys},\quad D=0,
\]
one obtains \(G=M=4\) and \(E=ig/\hbar\), independently of the arbitrarily
large isolated energies \(a,b\). A bound built from \(\|H\|\) loses this fact.

Algebraic cancellation is not itself a floating-point error certificate.
Ill-conditioned \(S,G,M\), or cancellation of nearly equal rounded inputs,
can amplify input/roundoff errors. The FP64 helper reports a computed
factorization, not a rigorous enclosure. In particular it cannot recover a
small coupling already lost when a large-energy input matrix was rounded.

If an input violates \(\dot S=D+D^\dagger\), (2) is not generally valid.
For fixed \(J\), defining \(\Xi=\dot S-D-D^\dagger\), the transformed \(W\)
contains a selected diagonal block \(X^\dagger\Xi X\) and cross-block
corrections \(Y^\dagger\Xi X\). The code rejects a defect above its fixed
input-validation tolerance; it does not discard that defect as physics.

## 4. State-aware sharp instantaneous rate

Let \(a=X^\dagger Sc\) and \(b=Y^\dagger Sc\). Then
\[
\|a\|^2=P,\quad \|b\|^2=N-P,\quad
\dot P=2\operatorname{Re}(b^\dagger E a).
\]
Consequently
\[
\boxed{\quad
|\dot P|\le 2\sqrt{P(N-P)}\,\rho\le N\rho.
\quad}
\tag{5}
\]
The factor two belongs here. For fixed \(P,N\), choose \(a,b\) proportional
to a right/left top singular-vector pair of \(E\), with phases aligned.
The first inequality is attained. Its maximum over \(P\in[0,N]\) occurs at
\(P=N/2\) and is \(N\rho\), explaining why (2) has no extra two.
At \(P=0\) or \(P=N\), the derivative vanishes instantaneously. This does not
freeze the state; quadratic departure from an endpoint is possible.

The helper computes \(N-P\) from the complement norm rather than subtraction,
avoiding a gratuitous loss of significance near a pure selected state.
No B0 coefficient vector is supplied by this theorem or implementation.

## 5. Integrated angle theorem, including endpoints

For \(N>0\), let
\[
p=P/N,\qquad \theta=\arcsin\sqrt p\in[0,\pi/2],\qquad
\Theta=\int_{t_0}^{t_1}\rho(t)\,dt,\quad t_1\ge t_0.
\]
Then
\[
\boxed{\quad |\theta(t_1)-\theta(t_0)|\le\Theta.\quad}
\tag{6}
\]
The proof does not divide by zero at \(p=0,1\). For \(\varepsilon>0\) define
\[
\theta_\varepsilon
=\arcsin\sqrt{\frac{p+\varepsilon}{1+2\varepsilon}}.
\]
On compact time intervals it is absolutely continuous and, almost everywhere,
\[
|\dot\theta_\varepsilon|
=\frac{|\dot p|}
 {2\sqrt{(p+\varepsilon)(1+\varepsilon-p)}}
\le\rho,
\]
since \(|\dot p|\le2\rho\sqrt{p(1-p)}\) and
\[
(p+\varepsilon)(1+\varepsilon-p)
=p(1-p)+\varepsilon+\varepsilon^2\ge p(1-p).
\]
Integrate, then let \(\varepsilon\downarrow0\). Uniform continuity of
\(\arcsin\sqrt{\cdot}\) on \([0,1]\) gives uniform convergence to \(\theta\).
This proves (6) at all endpoints. The resulting interval estimate by the
integrable \(\rho\) also establishes \(\theta\in AC_{\rm loc}\).
For \(N=0\), \(c=0\) and all population statements are trivial.

Thus the exact clipped population interval is
\[
\boxed{\quad
\sin^2\!\big(\max\{0,\theta_0-\Theta\}\big)
\le p(t_1)\le
\sin^2\!\big(\min\{\pi/2,\theta_0+\Theta\}\big).
\quad}
\tag{7}
\]
In particular \(p_0=0\) gives
\(p_1\le\sin^2(\min\{\Theta,\pi/2\})\), a quadratic small-budget bound.
There is no assumption that a known population at one coordinate can be used
as the initial population at another coordinate.

Optimizing over the unknown initial population gives
\[
\boxed{\quad
|p(t_1)-p(t_0)|\le
\sin\!\big(\min\{\Theta,\pi/2\}\big).
\quad}
\tag{8}
\]
Indeed, for \(\delta=|\theta_1-\theta_0|\),
\[
|\sin^2\theta_1-\sin^2\theta_0|
=\sin\delta\,|\sin(\theta_1+\theta_0)|
\le\sin\delta,
\]
and \(0\le\delta\le\min\{\Theta,\pi/2\}\). This improves the G01
\(\min\{\Theta,1\}\) estimate while retaining the same exact rate \(\rho\).
For nonunit normalization multiply (7)-(8) by \(N\).

The bounds are optimal for the supplied rate budget. In the two-level model
\[
S=I,\quad D=0,\quad J=e_1,\quad
H=\hbar\begin{pmatrix}0&ig(t)\\-ig(t)&0\end{pmatrix},\quad
c=\begin{pmatrix}\sin\theta\\\cos\theta\end{pmatrix},
\]
the equation of motion is \(\dot\theta=g\), \(E=g\), and \(\rho=|g|\).
For \(0\le\Theta\le\pi/2\), choose the endpoints
\(\theta_0=\pi/4-\Theta/2\),
\(\theta_1=\pi/4+\Theta/2\), with \(g\ge0\). Then
\(|\Delta p|=\sin\Theta\). Full transfer saturates the cap one; if a larger
exact integrated cost is required, a forward/back excursion adds arbitrary
cost without changing the final population. This is a synthetic sharpness
example, not a statement that the archived B0 trajectory is extremal.

If a half-line admits an integrable \(\rho\), the angle has a limit and (7)
also applies with \(t_1=\infty\) and the actual tail integral. Producing that
continuous physical integral remains an independent obligation.

## 6. Coordinate covariance and physical interpretation

For a nonsingular time-dependent \(T(t)\), the same physical basis and state
are represented by
\[
S'=T^\dagger ST,\quad H'=T^\dagger HT,\quad
D'=T^\dagger DT+T^\dagger S\dot T,\quad
c'=T^{-1}c,\quad J'=T^{-1}J,
\]
\[
\dot J'=T^{-1}\dot J-T^{-1}\dot T\,T^{-1}J.
\]
The crucial cancellation is
\[
(D'+iH'/\hbar)J'+S'\dot J'
=T^\dagger[(D+iH/\hbar)J+S\dot J].
\]
Therefore \(W'=T^\dagger WT\), while normalized choices of \(X,Y\) can differ
only by unitary rotations within the two subspaces. The singular values of
\(E\), \(\rho\), population and angle bounds are invariant. Dropping
\(\dot J'\) after a moving coordinate change generally changes the answer.
This extends G01's constant-coordinate covariance with its required terms.

If the columns of a Hilbert-space basis \(\mathcal B(t)\) realize
\(S=\mathcal B^\dagger\mathcal B\),
\(D=\mathcal B^\dagger\dot{\mathcal B}\), and
\(H=\mathcal B^\dagger\widehat H\mathcal B\), then \(E\) is the projection of
the selected-frame residual
\[
\frac{d}{dt}(\mathcal B J L_G^{-\dagger})
 +\frac{i}{\hbar}\widehat H\,\mathcal B J L_G^{-\dagger}
\]
onto \(\mathcal B Y\). The derivative of the within-selected normalization
drops out by orthogonality. This is a complement **within the finite model**;
the theorem does not bound a residual outside its full basis span or turn a
Galerkin state into the exact infinite-dimensional physical state.

This displayed Hilbert-space residual requires the selected columns to lie in
the strong operator domain of \(\widehat H\), so that
\(\widehat H\mathcal B J L_G^{-\dagger}\) is an actual Hilbert-space vector.
Conforming \(H^1\) columns alone do not imply that condition. For such weak-form
columns, only the finite test-function pairings are asserted; use the sibling
Galilean weak-residual theorem rather than interpreting this expression as an
unproved \(L^2\) residual norm.

## 7. Implementation, verification and scope

The new small-matrix reference is projector_rate.py; hbar is an explicit
argument. It returns \(X,Y,G,M,\mathcal R,E,\rho,Q,W\), with optional
\(\dot J\), plus the state-aware rate when a coefficient vector is actually
provided. At these dimensions Python orchestrates vetted BLAS/LAPACK solves;
the project HPC policy does not justify parallel overhead for an 18-by-18
matrix. No new native kernel, operator evaluation or propagation is run.

Eleven targeted tests passed with zero skips. They compare fixed-J results
against G01's independently assembled \(W\), verify the paired singular-value
spectrum, exact large-energy cancellation, state-bound saturation, arbitrary
completion invariance, moving-coordinate covariance, and second-order
convergence of an independently centered \(Q\) difference. Full-span and
invalid-input cases are included. The separate Fraction replay checks 33 exact
identities across six real-connection and four Hamiltonian families, including
isolated energies of size \(2^{80}\). These finite families support the
implementation; the arbitrary-dimension and endpoint proofs are given above.

One failed synthetic fixture was preserved: amplifying a rounded \(B^\dagger hB\)
by \(2^{30}\), then declaring \(D=-iH,\dot S=0\), exposed its amplified
Hermiticity/compatibility defect. The fixture was replaced by directly
specified exactly Hermitian integer data. Neither input tolerance nor the
compatibility gate was relaxed.

Claim ceilings remain capture=false, production=HOLD, all_bound=OPEN,
b_grid=NO_GO, original_capture_gap_resolved=false,
continuous_global_supremum_bound=false, continuous_trajectory_error_bound=false.
In particular, no endpoint population from the old +/-12 a0 window is assigned
at 32 a0, and no synthetic or saved-matrix comparison supplies that missing
physical state or interval certificate.
