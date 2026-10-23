# C23B: isotropic decay electrons in the gas frame

## Result and scope

For an unpolarized parent with isotropic single-electron emission in its rest
frame, a fixed rest kinetic energy maps to a uniform interval of kinetic energy
in the gas frame. The resulting positive kernel admits analytic particle,
kinetic-energy, total-energy and parallel-momentum integrals in every finite
energy bin. Superposition extends the result to any finite positive spectral
measure. This is a local source operator, before propagation or deposition.

The input is a **per-decay spectral measure**, with its initial atomic/molecular
and charge-state meaning supplied separately. The C23A evaluated means and Q
ceilings do not specify that measure. C23A's illustrative Fermi-one shape is
still illustrative. The derivation below does not adopt it as an evaluated
spectrum or complete a beta-to-IGM heating model.

Use metric (-,+,+,+). The parent rest frame is S*, the gas frame is S, and the
parent moves along the chosen positive parallel direction in S. All displayed
energies use the same unit (eV in the code). Keep c explicitly through
M=m_e c^2 and q=p_*c. No electromagnetic stress closure is changed.

## 1. Exact map and a stable endpoint

For K>=0, define E=K+M, q=sqrt[K(K+2M)], gamma>=1 and
G=sqrt[(gamma-1)(gamma+1)]=gamma*beta. At fixed K, the isotropic angular measure
is dmu/2 times dphi/(2*pi), where mu is the rest-frame cosine from the boost axis.
The Lorentz transform is

\[
 k=K_{\rm gas}=A+B\mu,\quad
 A=\gamma K+(\gamma-1)M,\quad B=Gq,
\]
\[
 E_{\rm gas}=k+M=\gamma E+Gq\mu,\qquad
 p_\parallel c=\gamma q\mu+GE,
\quad p_\perp c=q\sqrt{1-\mu^2}.
\]

These follow directly from the standard boost [PDG2025 Eq49.1; Agashe2015 Eq4].
The latter source explicitly states the scalar/unpolarized-parent condition
for a uniform rest cosine. For a continuous multi-body spectrum, the same
single-electron relation holds conditionally at each K when the marginal is
isotropic. Spin correlations between outgoing particles need not vanish; their
single-electron marginal must meet the stated assumption.

For B>0, the support is [k_-,k_+]=[A-B,A+B], and the density is 1/(2B).
For B=0 the measure is a Dirac mass at A. This includes gamma=1 and K=0;
the latter gives a moving electron with k=(gamma-1)M, not zero kinetic energy.

The lower endpoint can lose accuracy if formed by subtracting A and B.
Let y=asinh(q/M) and eta=acosh(gamma). Then

\[
 k_-=2M\sinh^2[(y-\eta)/2],\qquad
 k_+=2M\sinh^2[(y+\eta)/2],\quad k_+-k_-=2B.
\]

An independent on-shell identity is

\[
 k_-={ (\gamma q-GE)^2 \over \gamma E-Gq+M}.
\]

Its denominator is E_minus+M, never E_plus+M. The rapidity form gives a
nonnegative lower endpoint without clipping a negative floating result. A
producer may form the upper endpoint as k_-+2B to retain the analytic interval
width, while checking bin totals against the direct moment A. Extreme floating
inputs that overflow intermediate quantities require an explicit supported
domain or rejection; they do not justify silently renormalizing the result.

## 2. Exact bin particle and energy integrals

For a gas-energy bin [L,U), intersect [L,U) with [k_-,k_+] and call its endpoints
l,u. If u<=l, its continuous-kernel mass is zero. Otherwise, for B>0,

\[
 N_D={u-l\over2B},\qquad
 K_D=N_D{l+u\over2},\qquad
 E_D=K_D+MN_D,
\]
\[
 K_D^{(2)}=N_D\left[\left({l+u\over2}\right)^2+{(u-l)^2\over12}\right].
\]

These are unnormalized bin moments per input electron. Factors of a spectral
atom's multiplicity multiply all four moments together. The half-open
convention matters only for Dirac atoms: an atom at a shared boundary belongs
to exactly one bin. The final unbounded tail includes its lower endpoint.

An independent angular construction is useful for verification. Put
mu_l=max(-1,(L-A)/B), mu_u=min(1,(U-A)/B). Let
d=(mu_u-mu_l)/2 and m=(mu_u+mu_l)/2 for a nonempty interval. Then
N_D=d, K_D=d(A+Bm), and K_D^(2)=d[(A+Bm)^2+B^2*d^2/3].
High precision direct integration in mu supplies an independent numerical
reference to an implementation that uses the energy-interval representation.

The full-range identities are N=1, K=A, E=gamma*E_rest and
K^(2)=A^2+B^2/3. A three-way partition below/inside/above a transport table
must preserve these moments. An unavailable low or high deposition response
retains its count and kinetic energy explicitly.

## 3. Parallel momentum and angular closure

The signed parallel momentum moment (in energy units) is

\[
 P_D^c=\int_D p_\parallel c\,d\nu
       =d\{GE+\gamma qm\}.
\]

Equivalently, for G>0,
P_D^c=[gamma*E_D-E*N_D]/G. The angular expression avoids dividing a small
G and may be preferable numerically. For the full range it is GE. For gamma=1,
every nonempty fixed-energy atom bin contains the full isotropic angular shell,
so its net parallel momentum is zero; for K=0 it is GM.

For a finite positive measure nu(dK), write N_*=integral dnu and
E_*=integral(K+M)dnu. Then the complete per-event electron four-vector moment
in energy units is (gamma*E_*, G*E_* along the boost axis), and its kinetic
moment is gamma*E_*-M*N_*. The spectrum's first rest energy moment suffices for
these full moments. Energy-bin moments still depend on the spectrum.

Equal source populations with opposite parent directions cancel the signed
parallel first moment at every energy bin. They generally retain an even
stress anisotropy. Therefore they may provide a non-tilted LRS source candidate
with a separate stress owner, but do not establish isotropic atomic-gas stress.
An isotropic distribution of parent directions yields rotationally invariant
electron injection in the gas frame; that directional average admits a scalar
source. Isotropic injection by itself does not establish instantaneous stopping
or thermalization.

For future stress consumers, the relevant on-shell integrands are
(p_parallel*c)^2/E_gas and p_perp^2*c^2/(2E_gas). Their integrals describe
injection moments, not the accumulated stress after transport. At G>0 the first
has a closed primitive in w=E_gas:

\[
 {1\over2BG^2}\left({\gamma^2w^2\over2}-2\gamma Ew+E^2\log w\right).
\]

The stress trace primitive is [w^2/2-M^2 log w]/(2B). Half the trace-minus-
parallel contribution gives either transverse component. Degenerate G=0 or
B=0 cases require their direct limits. These optional stress formulas are
derived here; they are outside the initial source operator's adopted API.

## 4. Lifetime, volume and source-clock normalization

Let lambda=1/tau be the proper decay rate, where tau is the mean lifetime,
not the half-life. If a half-life is supplied, lambda=ln(2)/t_half. For mono-
energetic parents with gas-frame density n_b and Lorentz factor gamma,

\[
 R_{\rm event}={\lambda n_b\over\gamma}.
\]

PDG2025 Eq49.14 gives the survival factor exp[-lambda*t/gamma]. A mono-stream
proper density is n_*=n_b/gamma, so the same event rate is lambda*n_*.
The event count per proper spacetime volume is scalar; the number-density
transformation and lifetime dilation cancel as required. For a bath-frame
parent distribution f(P) normalized by integral f d^3P=n_b,
R_event=lambda*integral f(P)/gamma(P) d^3P. Spectral averaging and event-rate
weighting must use the same parent distribution.

For the mono-stream spectrum moments above,

\[
 \dot n_e={\lambda n_b N_*\over\gamma},\quad
 \dot u_{e,\mathrm{total}}=\lambda n_b E_*,\quad
 \dot u_{e,\mathrm{kin}}=\lambda n_b\left(E_*-{MN_*\over\gamma}\right),
\]
\[
 c\dot p_{e,\parallel}=\lambda n_b\beta E_*.
\]

The total-energy source's explicit gamma cancels for fixed bath parent density.
This cancellation concerns per-time emission from a prescribed population,
not a rule for boosting a per-event spectrum. For a finite time step at fixed
gamma and no replenishment, the actual decays are n_b[1-exp(-lambda*dt/gamma)];
the safe evaluation is -n_b*expm1(-lambda*dt/gamma). Updating gamma or density
during that step requires the corresponding time-dependent evolution.

In homogeneous LRS, let V=a_parallel*a_perp^2 be the local volume scale.
Comoving rates are V times proper-volume rates, and comoving parent density is
V*n_b. For a reference inventory n_ref per physical volume and an integration
coordinate eta with declared dt/deta>0,

\[
 q_{\eta,\mathrm{per\ ref}}={dt\over d\eta}{R_{\rm event}\over n_{\rm ref}}.
\]

Physical and comoving density ratios agree when both use the same V. No factor
of a^3 is inserted twice. If eta=ln(a) with a=V^(1/3), dt/deta=1/H where
H=dot(V)/(3V); other clocks need their own Jacobian. A redshift coordinate has
negative dt/dz for expanding histories and needs a declared traversal/sign
convention. The operator accepts a positive source clock explicitly instead
of guessing these conventions.

## 5. Complete energy and charge ownership

For an event, parent four-momentum is the sum of daughter, electron, neutrino
and emitted electromagnetic four-momenta, with any medium exchange included.
Apply one Lorentz transformation to all channels. An electron's increased
gas-frame kinetic energy is not an independent extra energy release: the
parent's removed momentum/kinetic energy and the other products balance it.
For isolated free particles, sum(K_out)-K_parent equals the rest-mass defect
Q when all final rest masses are included, in any frame. Channel-specific
electron kinetic support and partition are nevertheless frame dependent.

Atomic/molecular Q values require their matching initial/final masses,
ionization states and excitation/rearrangement ledger. A neutral-atom Q
cannot be inserted unchanged into a fully stripped-ion event contract.
For n->p+e-+antineutrino, nuclei/baryon and charge incidence must be linked to
the same event count as this kinetic source; recoil and antineutrino energy
have distinct owners. None is automatically deposited as electron heat.

## Verification and research status

Wolfram's final symbolic evaluation verified the on-shell lower-endpoint
identity, uniform-bin moments0..2 and the equivalent momentum expression.
The initial malformed query and a subsequent incorrectly transcribed
denominator test are preserved in SYMBOLIC_CHECKS.json; the final query
corrected them and returned zero differences. These were query-level failures,
not silent edits to a scientific producer result. A source-code reviewer uses
high-precision mu-space integration after the producer API is fixed.

EXECUTION: new derivation and symbolic checks complete; producer review pending.
PUBLICATION: parent-owned pending. BACKUP: parent-owned pending.
DAG: C23A rest-frame domain evidence reused -> exact source-frame operator
derived -> new implementation/review -> physical spectrum/state/transport
admission. global_error_bound=null. No previous ODE or coverage run was rerun.

Sources and exact scope are recorded in PRIMARY_SOURCES.json. The novelty claim
is the project-specific source/ledger implementation, not a new Lorentz theorem.
