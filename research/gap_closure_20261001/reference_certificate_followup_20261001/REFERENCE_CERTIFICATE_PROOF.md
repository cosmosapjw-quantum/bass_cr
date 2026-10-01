# A validated conforming reference and a 2.76856×10⁻¹⁴ selector map

The exact binary-rational interpretation of the archived B0 radial bank has now
been mapped to a precisely defined conforming reference and its invariant
isolated negative spectral projector. This is an actual static certificate,
not a proposal to obtain one later. It does not identify either reference with
the original dynamics or transfer the old temporal qualification.

The authoritative numerical values are rational endpoints in
`actual_certificate/REFERENCE_CERTIFICATE.json`. All decimal display fields are
conveniences; they are not outward-rounded endpoints. Simple outward rational
bounds, verified by exact comparison, are in `CERTIFICATE_SUMMARY.json`.

| Certified quantity | Convenient conservative bound |
|---|---:|
| Repaired one-center Gram lower bound | ≥ 0.99999999999999 |
| Negative selected block separation a | ≥ 0.12499999996 |
| Positive complementary block separation d | ≥ 0.0005525039691 |
| Isolated selected/complement residual r | ≤ 2.20011×10⁻¹⁵ |
| Original → conforming selected projector distance | ≤ 1.01622×10⁻¹⁴ |
| Conforming selected → negative spectral projector distance | ≤ 1.75235×10⁻¹⁴ |
| Original selected → negative reference projector distance | ≤ 2.76856×10⁻¹⁴ |

The reference has radius 64 a₀ and nine angular channels per center. Its negative
spectral subspace has rank five and its positive subspace rank four. The two
radial l=1 functions each retain their entire m=−1,0,1 multiplet. No angular
channel is removed and no reference has been adopted by a physical run.

## 1. Exact radial reference

The saved `BASIS.npz` contains degree-four coefficients pᵢⱼ(t), where
`t=(r−rⱼ)/(rⱼ₊₁−rⱼ)` and 0≤t≤1. Every saved binary64 value is interpreted as its
exact rational value, including all radial edges. Values at a finite collection
of cell endpoints do not affect the archived L² functions. The source evaluator
`foundation_rebuild/src/bass_foundations/radial_basis.py:FEMRadial.evaluate`
confirms this local polynomial convention and zero extension outside radius 64.

For each radial mode independently define common node traces

\[
\tau_0=\tau_N=0,\qquad
\tau_j=\frac{p_{j-1}(1)+p_j(0)}{2}\quad (0<j<N),
\]

and repair each cell by a linear lift:

\[
\widehat p_j(t)=p_j(t)
 -(p_j(0)-\tau_j)(1-t)-(p_j(1)-\tau_{j+1})t.
\]

Therefore adjacent cell values agree exactly and both external traces vanish
exactly. The repair is linear, preserves degree, and is idempotent. The repaired
radial functions belong to H¹₀(0,64). With normalized spherical harmonics,

\[
 \widehat\phi_{ilm}(\mathbf x)
 =\frac{\widehat u_{il}(r)}{r}Y_{lm}(\Omega)
\]

belongs to H¹₀ of the ball, extended by zero to ℝ³. At the origin the repaired
polynomials vanish linearly or faster; hence u/r and its angular-gradient energy
are square integrable, including l=1. Pointwise smoothness at the origin is not
being asserted or required for the Coulomb quadratic form. Values at r=0 can be
chosen arbitrarily without changing the Hilbert-space vector.

For a fixed (l,m), the exact mass and weak Coulomb Hamiltonian are

\[
 S_{ij}=\int_0^{64}\widehat u_i\widehat u_j\,dr,
\qquad
 H_{ij}=\frac12\int\widehat u_i'\widehat u_j'\,dr
 +\frac{l(l+1)}2\int\frac{\widehat u_i\widehat u_j}{r^2}\,dr
 -\int\frac{\widehat u_i\widehat u_j}{r}\,dr.
\]

Different (l,m) sectors are orthogonal. This defines a finite-dimensional
self-adjoint Galerkin operator on the repaired retained space. Its eigenvectors
are not claimed to be exact eigenfunctions of the full infinite-dimensional
Coulomb Hamiltonian. In particular, r below is a residual between blocks of the
finite weak-Galerkin compression. It is not an L² strong-operator residual:
cellwise derivatives and the zero extension can have derivative jumps, so the
repaired functions need not be in the strong Coulomb operator domain. The E
projector is the negative projector of this finite compression, not the
infinite-rank negative spectral projector of the full Coulomb Hamiltonian.
The full 9×9 one-center problem is an orthogonal direct sum
of a 3×3 l=0 block and three identical 2×2 l=1 blocks. A single 5×5 radial direct
sum therefore contains all distinct block information without losing any channel.

## 2. Certified rational integration and logarithms

L² masses and derivative products are integrated exactly as rational polynomial
integrals in local coordinates. The r⁻¹ and r⁻² products are expanded as exact
rational global polynomials on each cell. Every primitive is rational except
`log(b/a)`. Origin terms with nonzero singular coefficients are rejected;
conforming functions make these coefficients exactly zero.

For rational 1≤x≤2 set z=(x−1)/(x+1), so 0≤z≤1/3. For N=128,

\[
 L_N=2\sum_{k=0}^{N-1}\frac{z^{2k+1}}{2k+1},\qquad
 0\le\log x-L_N
 \le\frac{2z^{2N+1}}{(2N+1)(1-z^2)}.
\]

This follows by integrating the geometric series for 1/(1−z²), or from the
absolutely convergent atanh series and replacing every remaining denominator by
its smallest value. The right side is rational. An arbitrary positive rational
x is reduced to this interval by exact multiplication/division by powers of two;
`log x = log y + k log 2` is enclosed with the same interval arithmetic.

Nonzero-width interval endpoints are rounded outward to the dyadic grid 2⁻²⁵⁶.
For an endpoint q, lower rounding is floor(2²⁵⁶q)/2²⁵⁶ and upper rounding is
ceil(2²⁵⁶q)/2²⁵⁶. Addition, multiplication, division away from zero, and negation
use elementary interval inclusions. Exact point rationals are retained exactly.
No binary floating point, Decimal logarithm, precision agreement, or floating
linear algebra participates in a certified inequality. The sqrt enclosure uses
integer square root after rational scaling and verifies the exact floor relation.

The only NumPy operation is loading the archived non-object NPZ arrays. No
SciPy, eigensolver, native moment library, two-center operator evaluator, or
propagator is called.

## 3. Exact complementary coordinates and spectral inequalities

Let A index radial modes {0,1,3}, and B index {2,4}. Here these sets identify
the archived semantic selection; signs of stored energy labels are not used to
prove the new spectrum. Set

\[
 X=S_{AA}^{-1}S_{AB},\qquad
 Z=\begin{pmatrix}-X\\I_B\end{pmatrix},\qquad
 K=Z^\dagger S Z=S_{BB}-S_{BA}S_{AA}^{-1}S_{AB}.
\]

The inverse, X, and K are exact rational matrices. The selected and complementary
physical columns are S-orthogonal. The complementary and residual form matrices
are enclosed by

\[
 H_C=H_{BB}-X^\dagger H_{AB}-H_{BA}X+X^\dagger H_{AA}X,
 \qquad R_0=H_{BA}-X^\dagger H_{AA}.
\]

Gershgorin bounds, using diagonal interval endpoints and upper absolute off-diagonal
entries, give positive rational constants

\[
 s_-I\le S_{AA}\le s_+I,\quad
 k_-I\le K\le k_+I,\quad
 -H_{AA}\ge c_-I,\quad H_C\ge c_+I.
\]

The exact matrices are symmetric by their quadratic-form definition, and the
computed symmetric enclosures mirror both triangles. Positivity of SAA and K
also proves full Gram positivity by Schur complement. After orthonormalization,

\[
 A_0\le-aI,\quad D_0\ge dI,\quad
 \|R\|\le r,
\]

with the implemented conservative choices

\[
 a=c_-/s_+,\quad d=c_+/k_+,\quad
 \|R\|^2\le\frac{\sum_{ij}\max(|(R_0)_{ij}^{lo}|,|(R_0)_{ij}^{hi}|)^2}
 {s_-k_-}\le r_{\mathrm{upper}}^2.
\]

Here r = r_upper is the upper endpoint of the exact square-root enclosure.
Each l=1 block repeats independently for three m values. The full operator norm
is the maximum of sector norms, not the sum of repeated multiplicities. Using
the Frobenius bound on the single l=0⊕l=1 radial direct sum is therefore an upper
bound for the full 9-channel residual. The same observation applies to all Gram
and spectral sign bounds.

By min-max, the isolated reference F has exactly five negative eigenvalues with
λ₅≤−a and four positive eigenvalues with λ₆≥d. Let E be its exact negative
spectral projector, P the orthogonal projector onto repaired selected columns,
and U an orthonormal basis of ran P. If V complements U, then
`FU−UA₀=VR`. With F₊ the positive restriction,

\[
 F_+(I-E)U-(I-E)UA_0=(I-E)VR.
\]

The solution is the convergent Sylvester integral

\[
 (I-E)U=\int_0^\infty e^{-tF_+}(I-E)VR\,e^{tA_0}\,dt,
\]

so its norm is at most r/(a+d). Equal finite-rank orthogonal projectors have
`||P−E||=||(I−E)U||` by their principal-angle decomposition. Thus

\[
 \|P-E\|\le\min(1,r/(a+d)).
\]

This is a validated enclosure of a spectral projector distance without computing
approximate spectral vectors.

## 4. Original physical projector to repaired spectral projector

Let F₀ and F₁ synthesize the archived and repaired selected physical functions
in the same L²(ℝ³), and let Q₀,Q₁ be the orthogonal projectors onto their ranges.
Exact rational integration gives their difference Gram
`GΔ=(F₀−F₁)†(F₀−F₁)` and the original selected Gram lower bound s₀>0. Both
selected ranks are five. Since `(I−Q₁)F₁=0`,

\[
 \|Q_0-Q_1\|
 =\|(I-Q_1)F_0(F_0^\dagger F_0)^{-1/2}\|
 \le\frac{\|F_0-F_1\|}{\sqrt{s_0}}.
\]

For each orthogonal (l,m) block, its largest eigenvalue is at most its trace.
The maximum of the selected l=0 and l=1 radial trace bounds is therefore a valid
bound for `||F₀−F₁||²` in the full angular space. No factor of three is missing:
the l=1 block repeats orthogonally; it is not added to the same block.

Combining the two maps by the triangle inequality gives

\[
 \boxed{\|Q_0-E\|\le 2.76856\times10^{-14}.}
\]

The displayed upper bound is the exact rational 276856/10¹⁹. It is strictly above
the full certificate's rational bound. For any common physical state ψ with
squared norm N,

\[
 |\langle\psi,Q_0\psi\rangle-\langle\psi,E\psi\rangle|
 \le N\,2.76856\times10^{-14}.
\]

Common unitary translations, rotations, and ETF phase multiplications preserve
the bound. It compares observables on the same state; it does not compare a
saved archived state with a newly evolved reference state. A dynamics/state map
must supply its own error separately. In particular, tiny trace repair does not
by itself establish small Hamiltonian or trajectory error.

## 5. Identities and remaining boundary

- Exact archived basis identity:
  `f23267b7214a5e3918866dcece5cb61c79a891578f4dda69dee5a762eb02983a`.
- Exact repaired coefficient canonical JSON SHA256:
  `85166a5812f6c9bb09f7389e1eb73019b48ea530058e37e9abdd2f11b05da6ee`.
- Named negative reference selector definition SHA256:
  `2df8fd41703e3075c837e0e576ff34ec26d38f5b83d04066f1d9ec7b805e7150`.
- Actual archived inputs and all bounds are pinned in the certificate; these
  identities describe a mathematical reference and do not adopt it operationally.

The previous G04 reference-definition, conforming-function, validated isolated
sign/gap, and same-Hilbert-space selector-map subblockers are resolved for this
named reference. What remains is the finite bridge/tail and state/dynamics
comparison required by whichever asymptotic observable is ultimately selected.
The original fixed-J observable's ordinary asymptotic limit remains unproved;
this calculation cannot remove the prior eternal-oscillation counterexample.

`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`,
`original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`,
and `continuous_trajectory_error_bound=false` remain unchanged.

The focused test suite checks exact polynomial examples, singular/negative input
rejection, log and square-root rational inclusions, repair conformity/idempotence,
angular orthogonality, complementary Schur coordinates, and a sign-gap
obstruction. Nine tests passed. The initial missing-module red result and the
green log are retained. The saved-input certificate completed with zero native
calls, zero new two-center operator queries, and zero time propagations.
