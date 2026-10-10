# R17B2 continuum source response and proof boundary

All constants are the pinned binary64 literals interpreted as real numbers. Time
u=t/T and probe birth v=b/T are dimensionless inside the RHS. T=1250000000 proper
seconds. z=(x_HII,x_HeII,x_HeIII,W/W0). Source mass is per conserved H nucleus.
The same original initial gas, photon mass0.05, energy family, density, Hubble
rate, HI fit, CaseA CI/RR/twoDR and six source atoms are used. Optional HH/RCT/CR
remain OFF. Energy E(t,b)=Eb exp[-H(t-b)], density nH(t)=nH0 exp[-3Ht].

Let a_b(u)=T c nH(u) sigma(E(u,b)), k_b=a_b(1-x),
q_b=(E(u,b)-chi_HI)/W0, and p_b(u)=exp[-int_b^u k_b(s)ds].
The initial photon component is0.05 p_0. Previous source births are integrated
against mu_eta=(1-eta)mu_Q+eta*S db, with the original weight box. No source mass
is renormalized; the exact finite mass defect is retained. Current gas photo
terms are int k_b p_b dmu, in x, and int q_b k_b p_b dmu, in W/W0, plus initial
photons. nonphoto_rhs supplies the full four gas rows, with cooling and expansion.
The companion source measure is a distribution, not a seven-cohort interpolation.

For an extra unit source photon at arbitrary b, let v be the gas tangent and
r_d=-p_d int_d^u delta k_d ds the response of EVERY existing companion photon.
Since delta k_d=-a_d v_x, r_d=p_d int_d^u a_d v_x ds. The tangent photo rate is
k_b p_b + int[-a_d p_d v_x + k_d r_d] dmu_eta, with the corresponding q_d heat
weights; the initial photon term participates too. This is implemented by
probe, memory_response and tangent_functional. They are exact operators given
valid fields. integrate_previous provides a whole-panel directed range integral
of the actual continuous+atomic measure; physical left/right trace is explicit
at an observation-time atom. The PositiveSurvivalTube uses the proved positive
opacity and [0,1] survival; it does not supply high order derivative fields.

The full gas adjoint is -J_nonphoto^T lambda_g-goal, with extra x row
int a_d p_d(lambda_x+q_d lambda_w-lambda_d) dmu_eta including initial photons.
The backward photon equation is lambda_d'=k_d(lambda_d-lambda_x-q_d lambda_w).
Its zero-terminal solution evaluated at u=b/T is K_eta(b). These equations and
birth Taylor arithmetic through order4 are implemented. Jet stores f^(r)/r!;
derivatives restores r! once. source_peano already includes the factorial in
moments/hinges, so no second division is allowed. Physical derivatives with
respect to proper seconds and global u are distinguished; the Peano local
coordinate derivative is (h/T)^r times the global-u derivative.

If differentiability and integral exchange hold in the common tube,
tau(mu_S)-tau(mu_Q)=int_0^1 d_eta int K_eta(b)(mu_S-mu_Q)(db).
A tangent evaluated only at eta=0 is insufficient. No eta quadrature result in
this package is promoted to that exact finite-source identity.

## Whole-homotopy value tube proved by new interval computation

For prescribed continuous gas paths in the closed rectangle [.89,.91]x[.29,.31]x[.59,.61]x[.99,1.01], all
photons have positive opacity, survival in[0,1], HI-only energy support and valid
thermal fit domain. The He fractions remain positive with HeII+HeIII<1. The
entire positive photon mass is bounded by P=0.05+max(S*T,sum upper weights),
which is valid for every eta and weight, using convexity rather than adding both
source measures. run_bounds computes the entire-window interval nonphoto RHS,
its four-by-four state Jacobian, E and nH, and photo/heat bounds. Every integrated
gas row stays strictly inside its actual initial-to-boundary margin (approximately .01). Thus the gas-path map with
exact causal survival maps the cube to itself.

With A=sup a_b, k=sup k_b and L_np the infinity row norm of the normalized
nonphoto Jacobian, the Lipschitz constant of that path map is bounded by
L_np+max(P*A*(1+k), P*A*(1+k)*sup|E-chi|/W0).
The direct current-photon and opacity-memory feedback are both included.
The directed upper value is <0.001341<1. Banach contraction gives the common
solution for ALL eta and weights; no trajectory sampling establishes it.
This also supports the bounded first source-direction response. For an arbitrary
unit probe, the gas tangent sup norm is at most
sup k*max(1,sup|E-chi|/W0)/(1-q_contraction).
Integrating the actual Thomson goal gives a coarse signed K0 enclosure of about
[-7.99791e-12,7.99791e-12] for all b and eta. It is not a source-error bound or a
sharp derivative estimate. BOUNDS_CANONICAL.json is the exact directed result.
MPFR_BOUNDS.json recomputes these whole ranges in separate MPFR256 arithmetic;
independent_check.py separately reconstructs the nonphoto equations in MP110
precision and checks state derivatives, as well as interval primitives/jets.
Finite arithmetic checks supplement the library rounding contract; they do not
replace the whole-domain self-map/contraction inequalities.

## Exact blocker for high order Peano transfer

The common value tube and gas Jacobian do not enclose the mixed time/birth
resolvent jets at the moving lower limit u=b/T. No validated flow for these jets
or the companion adjoint distribution is supplied. Derivatives of
lambda_b(u)|u=b/T require both time and birth derivatives, not merely the partial
birth jet of the instantaneous photon RHS. The latter is implemented and
independently checked; substituting it would be wrong.

Consequently K1,K2,K3 at anchors, regular K4 over each open piece, and all
one-sided jumps through order3 are unknown. Known atoms, source boundaries and
output/proof boundaries are enumerated in PARTITION_INVENTORY.json as candidates;
no complete partition is certified. Actual Gauss atoms miss many output/proof
boundaries. Empty jump lists or zeros cannot be inferred from smooth-looking
samples, nor from an interval/partition boolean. require_proof always fails
closed until an actual validated proof producer is implemented. It is not yet
a general accepting certificate verifier.

The first source interval[0,885031998.4547119] remains the priority because its
share of the regular fourth-derivative COEFFICIENT is99.7754%, not the true source
error. C4=2.579987776092595e-10 multiplies a global-u K4 bound. The design target
7.4129479e-9 is NOT an achieved K4 bound; it leaves10% of the fallback budget for
anchors and every jump. Later source intervals remain covered by the unchanged
whole-macro causal fallback. No partial source interval replaces it here.

## Diagnostics and unchanged bounds

Diagnostic.py solves a base with Gauss8/16 companion births per source cell,
then constructs arbitrary-birth forward tangents (DOP853) and independent
backward goals (RK45), including all companion response states. eta=0,.5,1 and
five birth locations are sampled. These are finite-approximation diagnostics,
not the true continuous distribution or a uniform interval proof. They are not
used to enclose source error or to assert its sign. Full source quadrature
remainder is not enclosed, and the actual eta integral is not certified.

No new source interval is certified: NO_CERTIFIED_SOURCE_SHARPENING. The latest
causal R17 source radius and combined R16B interval are retained byte-for-byte
in inputs/CAUSAL_RESULT.json. The documented safe fallback is2.125035e-18; the
original exact rational radius is preserved too. There is ZERO new time/source
combination operation. The earlier Volterra/direct-electron derivation remains
separate and is not invalidated. No old CDF, coefficient, donor or R16B suite was
rerun. Physical/production HOLD, CR_OFF_FASTEST, G02_UNRESOLVED, b_grid_NO_GO and
Grackle owner-input blocker are unaffected.
