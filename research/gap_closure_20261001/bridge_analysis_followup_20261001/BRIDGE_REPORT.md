# Finite bridge: a constructive continuum bound and its quantitative failure

The finite bridge no longer has an existence-only obstruction: exact polynomial
algebra and support geometry prove a uniform positive metric on every separation
R≥32, without a native operator query. For the separately named conforming
reference, a Hardy-form argument also supplies a continuous constant rate
majorant on each signed bridge [32,128]. Its probability bound is about
6.27×10^57 per side, against the predeclared 5×10^-6 target. This method therefore
**does not meet the research accuracy target**. The result proves that a finite
continuum enclosure exists constructively; useful cancellation-preserving
enclosures remain necessary.

This note does not replace the archived B0 model, selector, numerical state or
temporal gate. In particular, a rigorous statement about the exact physical L2
Gram is not an error certificate for the native quadrature matrices. All results
below use atomic units and squared state norm N=1 unless N is written explicitly.

## 1. Source inspection and the actual regularity boundary

`full_operator.py:same_center_blocks` forms the weak isolated Hamiltonian,
other-center Coulomb multiplication form, and translation connection directly.
Its angular projection includes L=0,1,2 for B0; its radial integral is split at
the nuclear distance R. The point Coulomb singularity can lie inside a support
ball for R<64. Consequently, a uniform pointwise bound on the full Coulomb
potential is false on part of the requested bridge. That obstruction must be
handled by a form bound rather than by replacing the singular potential with a
finite supremum.

`radial_basis.py:FEMRadial.evaluate` zero-extends the stored polynomial pieces.
Literal archived binary coefficients have small nonzero internal and exterior
traces, as the preceding Route A audit established. Such discontinuities do not
prevent L2 mass integration, but they do prevent silently treating the functions
as H1 conforming. Translation of a nonzero jump satisfies a squared L2 increment
of order |h| near its jump surface; its L2 derivative need not exist. Thus the
bulk derivative used by the native formula cannot silently be identified with
the exact weak derivative of that literal discontinuous function.

The new reference artifact `EXACT_REPAIRED_REFERENCE.json` makes endpoint traces
agree exactly and vanish at the two exterior radial endpoints. Its construction
and old-to-reference mapping are owned by the sibling reference certificate.
Here it is independently read and its exact traces are checked. The finite
bridge theorem is applied to the weak H1 Galerkin model of that **named candidate**,
with exact moving-basis connection. No adoption or trajectory comparison follows
from this analysis.

## 2. Exclusive caps prove a whole-continuum positive metric

Place the two centers at separation R≥32; the common support radius is a=64.
At each center take the radial shell 48≤r≤64 and the outward angular cap
mu≥1/2, where outward means away from the other center. Every such point lies
strictly outside the other support ball, because

\[
|x-R_{\rm other}|^2=r^2+R^2+2rR\mu
\ge48^2+32^2+48\cdot32=4864>64^2.
\]

The squared-distance margin is exactly 768. The two caps are disjoint. Their
orientation can change with z; only their pointwise support property is used,
and no cap derivative appears in the argument.

Use normalized spherical harmonics through l=1, with a real p basis for writing
the following matrix. On mu≥c the l=0 and longitudinal l=1 angular block is

\[
A_c=\begin{pmatrix}
(1-c)/2&\sqrt3(1-c^2)/4\\
\sqrt3(1-c^2)/4&(1-c^3)/2
\end{pmatrix},
\quad
\det A_c={(1-c)^4\over16}.
\]

Each transverse p component has cap norm (2−3c+c^3)/4. At c=1/2,
det A=1/256 and tr A=11/16, hence

\[
\lambda_{\min}(A)\ge{\det A\over\operatorname{tr}A}
={1\over176},\qquad {2-3c+c^3\over4}={5\over32}>{1\over176}.
\]

Therefore angular cap restriction is bounded below by gamma=1/176 on the
entire s/p angular span. This remains valid in the complex harmonic basis and
for every cap direction because the complete l=1 multiplet transforms unitarily.
Incomplete magnetic multiplets would require a separate angular calculation.

For each l define the exact radial shell Gram and full radial mass Gram

\[
T_l{}_{ij}=\int_{48}^{64}u_i(r)u_j(r)\,dr,\qquad
M_l{}_{ij}=\int_0^{64}u_i(r)u_j(r)\,dr.
\]

The coefficients and edges are rational (literal binary values for the old bank,
explicit rational values for the reference). These integrals are exactly
rational even when 48 cuts a mesh cell. Positive exact LDL pivots prove each
T_l positive. If n_l is its dimension,

\[
t_l={\det T_l\over(\operatorname{tr}T_l)^{n_l-1}}
\le\lambda_{\min}(T_l).
\]

Indeed every other positive eigenvalue is bounded above by tr T_l. This bound is
very pessimistic when the radial modes have very different tail masses.

On a target-exclusive cap the projectile sum is zero, and conversely. The ETF
phase has unit modulus within either center. Integrating the squared total
wavefunction over the two exclusive caps therefore gives, for raw coefficients,

\[
\boxed{c^\dagger S(R)c\ge\gamma\min_l(t_l)\,\|c\|^2
\quad\hbox{for every }R\ge32.}
\tag{1}
\]

After separately orthonormalizing each center, let m_upper bound both center
mass matrices. Then the dimensionless combined Gram obeys

\[
\boxed{S_{\rm cc}(R)\succeq s_0I,\qquad
s_0={\gamma\min_l(t_l)\over m_{\rm upper}}.}
\tag{2}
\]

The exact certificates, including radial matrices, LDL pivots, rational lower
endpoints and input hashes, are in the two JSON files next to this report.
Their decimal displays are not the authoritative endpoints:

| Object | Proven all-R≥32 bound in center-normalized coordinates |
|---|---:|
| Literal archived L2 span | S≥2.22035337611597388×10^-55 I |
| Named conforming reference | S≥2.22035337611605217×10^-55 I |

These tiny lower bounds do not show that the real Gram is poorly conditioned.
They show that this particular exclusive-tail argument is extremely conservative.
For comparison with an alternative route, center-normalized blocks have the form
[[I,C],[C†,I]], so their minimum eigenvalue is 1−||C||. A useful certified bound
on the angle between the two center spans could be much stronger. Pointwise
small overlaps alone do not prove a uniform bound in between those points.

## 3. Coulomb form bounds, with no false potential supremum

For f in H1(R3), the translated Hardy inequality is

\[
\int {|f(x)|^2\over|x-a|^2}\,dx\le4\int|\nabla f(x)|^2dx.
\tag{3}
\]

A direct proof for smooth compact functions, after translating a to zero,
expands 0≤||grad f+(x/2r²)f||². Integration by parts uses div(x/r²)=1/r²
and gives ||grad f||²−(1/4)||f/r||²≥0. Approximation extends this to H1.
Cauchy–Schwarz then gives

\[
\int {|f|^2\over|x-a|}\le2\|f\|\,\|\nabla f\|.
\tag{4}
\]

Suppose the gradient operator restricted to the total normalized finite span
has norm at most sqrt(K). With charge sum Zsum, the compressed self-adjoint
weak Hamiltonian therefore satisfies

\[
\|\widehat H\|\le K/2+2Z_{\rm sum}\sqrt K.
\tag{5}
\]

This is a norm bound obtained from all normalized quadratic forms; Coulomb
singularities inside the support are allowed. No regularized potential is used.

The helper proves the unboosted one-center gradient bound kappa from exact
diagonal kinetic integrals and a Gershgorin lower bound on the one-center mass.
For the angular term l(l+1)∫u²/r², it integrates the first cell exactly after
factoring u(0)=0; later cells use r^-2≤r_left^-2. Positivity of the gradient Gram
allows its trace to bound its norm. The resulting certified value is
kappa≤1.34527189809663382.

For stationary target and projectile speed v≤vmax, define

\[
L_T=\sqrt\kappa,\quad L_P=\sqrt\kappa+v_{\max},\quad
K={L_T^2+L_P^2\over s_0},\quad
B=v_{\max}\sqrt\kappa+v_{\max}^2/2.
\]

L_T and L_P bound the individual boosted gradient maps. Their sum satisfies the
Cauchy–Schwarz bound sqrt(L_T²+L_P²) on combined center coefficients; (2)
then gives K. The source ETF convention is
chi=exp(i v·x−i v²t/2)phi(x−vt), so
dot chi=phase[−v·grad phi−i v²phi/2], yielding B.

Let X map center-normalized coefficients to physical wavefunctions. Since
S=X†X, X S^-1/2 is an isometry, and D=X†dot X gives

\[
\|S^{-1/2}DS^{-1/2}\|\le B/\sqrt{s_0}.
\]

For fixed full-rank selector J, the preceding exact leakage identity is
rho=||S^1/2(I−Pi)A Pi S^-1/2|| with A=−S^-1(iH+D). Both whitened projectors
are contractions. Consequently a sufficient **constant continuum majorant** is

\[
\boxed{\rho(z)\le G:=K/2+2Z_{\rm sum}\sqrt K+B/\sqrt{s_0}.}
\tag{6}
\]

H1 translation supplies the L2 derivative and Sdot=D+D†. Weak-form H and D are
continuous on the finite bridge, and (2) bounds S^-1. Thus the underlying finite
ODE and the existing fixed-J rate identity are well defined. Derivative bounds
on H, W, or the Coulomb potential are not needed for this coarse construction.
In particular this route avoids demanding second derivatives of a C0 FEM basis.

`certify_reference_bridge.py` uses integer upper square-root bounds and exact
rational arithmetic throughout. It scopes v to [1,3] atomic units, stationary
target, unit charges, b=2, and a=64. The broader rational velocity interval
contains the declared B0 100 keV/u speed; it is an explicit model hypothesis,
not a new velocity fit. At |z|=128 the actual separation sqrt(128²+4) is already
strictly greater than 128, so this bridge can join a disjoint-support tail.

The actual reference certificate gives

\[
G\le6.53049201806069730\times10^{55},\qquad
\int_{32}^{128}\rho\,{dz\over v}
\le6.26927233733826940\times10^{57}.
\]

The accepted calculation remains unchanged. This huge upper bound is not a
prediction of a huge probability: probability differences can separately be
capped by N. Neither bound certifies the 5×10^-6 target. A sharp method must keep
the isolated/translation/monopole cancellation before norm estimation and
certify the resulting selected-to-complement coupling over the finite bridge.

## 4. Independent check of the gapped-tail proposal

The sibling gapped-tail theorem was read independently. Its ordered lower versus
upper projectile cluster, not arbitrary interlaced eigenvalues, makes the
semigroup Sylvester operator-norm constants valid. The instantaneous projector
derivative has off-diagonal Hermitian blocks and therefore incurs no extra
factor two. Its population commutes with the instantaneous Hamiltonian, so the
velocity cancels between dot E=v E_z and dt=dz/v; there is no 1/v or hbar factor
in that population-variation bound.

The required gap concerns the isolated projectile block after exact disjoint
support. The full two-center isolated Hamiltonian contains target/projectile
degeneracies; its rank-five projectile selector is not an isolated global energy
cluster. Extending the projectile projector by zero is legitimate only because
the disjoint-support dynamics is a direct sum.

The Coulomb derivative estimate uses the full Cartesian field A(y)=y/|y|³,
whose Jacobian norm is 2/|y|³. Hence the off-diagonal potential derivative is
bounded by 2qa/(R−a)³. Scalar subtraction may differ between the amplitude bound
and the derivative bound because scalars have zero off-diagonal coupling. This
correctly accounts for the changing direction of (b,0,z). No defect was found
in these proof steps.

There is a sharp countercondition: gap plus ||V||=O(t^-2) alone does not imply
an O(t^-2) population remainder. Set hbar=1 and

\[
H_0={\Delta\over2}\sigma_z,\qquad
V(t)=t^{-2}e^{-iH_0t}\sigma_xe^{iH_0t}.
\]

For sufficiently large t the gap stays positive. In the interaction picture
the Hamiltonian is exactly sigma_x/t², and
x(t)=exp(i sigma_x/t)x_infinity. For x_infinity=(1,i)/sqrt(2), the upper-energy
population is [1−sin(2/t)]/2. Its deviation from its limiting value 1/2 is
O(t^-1). Here V' has a resonant O(t^-2) term. The sibling theorem's controlled
projector variation (supplied by its Coulomb derivative estimate) excludes this
example; merely saying “gapped” would not. This discriminator was sent to the
theorem author for inclusion in its own focused tests.

The root's `ASYMPTOTIC_OBSERVABLE_THEOREM.md` was also read independently. Its L1
interaction-state argument, exact grouping of equal Bohr frequencies, ordinary
limit criterion, retained degenerate coherences, and Cesàro limit are correct
under the stated finite-reference assumptions. Treating the old physical
projector as a compressed contraction on the reference span is necessary and is
done explicitly. A nonzero commutator alone does not prove nonconvergence for
every specific state; the note correctly distinguishes that statement.

## 5. What remains, and what is now smaller

There are now exact input-only continuum metric certificates for the literal L2
span and the named repaired reference. There is also a rigorous finite constant
majorant for that reference, with a quantified failure to meet the target.
These replace an unspecified existence issue with a precise accuracy issue.
No whole-cell native data are required merely to prove existence.

The practical unresolved seam is a sharp bound for the cancellation-preserving
off-diagonal generator in the overlap region, together with an accepted
old-state to reference-state comparison if the reference is adopted. The
existing Route B interval derivative method is one option; direct weak-form
interval enclosures of the cancelled block are another. Neither dense sampling
nor finite differences alone provide such a certificate.

This folder has four focused algebra/helper tests, all passing. No old suite,
new native library, new physical operator query or propagated state was run.
The two proof reviews are read-only and did not rerun sibling test suites.
Existing ceilings remain capture=false, production=HOLD, all_bound=OPEN,
b_grid=NO_GO, original_capture_gap_resolved=false,
continuous_global_supremum_bound=false, continuous_trajectory_error_bound=false.


## 6. Later bounded follow-up: the ETF phase supplies a strong metric bound

The exact ETF integration-by-parts argument in `ETF_METRIC_THEOREM.md` now proves
33/100 I <= S_cc <= 167/100 I for the named conforming reference, at every center
displacement, using the frozen relative speed v=2.00798106651023. Parity separates
the directional derivative l=0/l=1 blocks; s-wave isotropy supplies the factor
1/3, yielding L_z<=67/100 and cross-Gram norm<=67/100. The earlier exclusive-cap
certificates remain unchanged and valid, but this new certificate provides the
useful metric bound.

Keeping the same conservative Hardy estimate gives a per-side bridge bound
55408/11 (about5037.09), which still does not meet5e-6. The remaining sharpness
problem lies in the cancellation-preserving rate enclosure, not uniform metric
positivity. `ETF_METRIC_CERTIFICATE.json` binds all exact inputs and the actual
velocity source. Two new focused tests pass; the previous four were not rerun.
No native call, model adoption or archived trajectory transfer occurred.
