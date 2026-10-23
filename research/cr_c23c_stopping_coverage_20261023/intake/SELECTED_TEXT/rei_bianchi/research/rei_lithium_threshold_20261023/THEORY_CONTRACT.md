# ANGTHERM02 — lithium threshold integration on a retained thermal history

Authority: Astra controller, physmath-research-loop intrinsic 1.0.0 / approved
v0.2. Date: 2026-10-23. Base REI PR221 commit
`6daf382ee698835e7a141378c232d1d97c1c5cf1`; PR222 is a separate unchanged branch.
This is a new bounded research unit. ANGTHERM01's completed budget is closed.

## R1–R4: question, retained evidence, and chosen representation

Resolve the numerical origin of the remaining Li angular differences and
construct a more accurate, inexpensive conditional Li response. Retain the
ANGTHERM01 prescribed grid044 geometry, atomic fits, initial composition and
completed M4/M8/M16/mean histories. Do not rerun those full gas/photon IVPs.

The question here concerns a late trace response on an explicitly prescribed
thermal/electron bath, not a replacement full coupled angular-continuum run.
The previous 2e-7 angular accuracy target remains an open full-model target.
The same value is a discrimination threshold for this conditional experiment.

Saved evidence: the 10 eV cohort has max optical depth 5.617874831337621e-9 in
M16. At saved report index11, eta*=0.10702505819804223, the summed initial
20–150 eV cohorts are about1.31e-317/Href. Their logs, rather than underflowed
counts, define the tail bound. The source count is finite and has no new births.
The remaining photoionizing cohort can ionize LiI only. All earlier expensive
gas dynamics are reused; the new chemistry has four Li charge fractions.

Alternatives considered: (i) another whole-system fixed-node refinement,
(ii) moving rays with reconstructed attenuation, (iii) support-resolved rate
quadrature with a separately bounded optically thin approximation. Choose(iii)
because the surviving cohort is extremely optically thin. Moving quadrature
nodes evaluate an integral; they never acquire invented photon histories.

## R5: geometry, measure, and support

Use signature(-,+,+,+), eta=ln(a/a_initial), c=29979245800cm/s, energies in eV,
cross sections in cm², and counts per reference H nucleus. Reuse the exact
ANGTHERM01 characteristics on the saved Hermite b and PCHIP logH background:

    E(eta,mu)=E0 exp(-eta) sqrt(A+(B-A)mu²), A=exp(2b), B=exp(-4b).

The fixed covariant direction mu is in[0,1] after reflection/azimuth symmetry.
The density of the initial10eV cohort is G0=0.05 per Href per dmu. Do not insert
another physical-angle Jacobian. For b>0 partial support is[0,mu_c], where

    mu_c²=[(chi/E0)² exp(2eta)-A]/(B-A), chi=5.392eV.

For b<0 partial support is[mu_c,1]; b=0 has a common all-or-none threshold.
Classify empty/full support by endpoint energies before solving for mu_c.
Use expm1/log1p where cancellation matters. The adopted grid044 rays all
redshift monotonically, so E<=10eV and the support eventually becomes empty.
Find first/last endpoint crossings with brentq and include them as time splits.

Define k=(c nHref/H)sigma_LiI(E). Then

    Lambda0 = G0 integral_active k dmu,
    LambdaE = G0 integral_active E k dmu.

For interval[l,u], use positive GL weights(u-l)w_j at l+(u-l)x_j. Retain the
physical support width; do not normalize it to one. Independently compute
selected angular integrals with scipy.integrate.quad on the exact same support.
Its error output is an estimate, not a certified enclosure.

## Bath and initial-value definition

Read the saved accepted_eta/accepted_Y of grid044_M16_tight. Obtain T and v
from the original equations. The PRIMARY bath is CubicHermiteSpline of logT
and logv, with slopes from the original Reduced.rhs at the saved states:

    (logT)'=U'/U-v'/(N_nuc+v), (logv)'=v'/v.

At any original support boundary use the physical source fit for the slope;
the Li contribution is retained. This interpolation is an explicit new input
model, not an interval-error certificate for the unknown exact bath. Record
the derivatives and driver arrays. A secondary log-PCHIP bath on the same
accepted data is an independent reconstruction sensitivity control. Retain
all raw fractions: no floor, clipping, rescaling or renormalization.

All late cases start at report index11 with the identical saved M16 LiI–LiIV
fractions, end at log7, and report on the union of existing report nodes after
eta*, both support endpoint times, and401 uniform points in[0.44,0.74]. Retain
each accepted state too. Direct saved comparisons use exactly matching report
times; no interpolation of the saved fractions into a new alleged reference.

## Four-state trace equations and event ledger

Let f0..f3 denote LiI..LiIV, and r_q=(nHref/H)v alpha_q(T), q=1,2,3, from the
same source RR rows. With only the surviving10eV photons,

    f0'=-Lambda f0+r1 f1
    f1'= Lambda f0-r1 f1+r2 f2
    f2'=-r2 f2+r3 f3
    f3'=-r3 f3.

The generator has nonnegative off-diagonal entries and zero column sums.
Evolve all four components directly. The proof may use cLi=1-f2-f3 and
f0'=r1 cLi-(r1+Lambda)f0; do not subtract nearly equal fractions in outputs.

Add five ledgers per Li nucleus, initialized to zero at eta*:

    CA'=Lambda f0; CR'=sum_q r_q f_q
    Qgas'=(LambdaE-chi1 Lambda)f0-sum_q K_q r_q f_q
    Eesc'=sum_q(chi_q+K_q)r_q f_q
    Eabs'=LambdaE f0.

K_q is the already adopted conditional capture-energy closure. With ionization
potential I=sum_q B_q f_q and charge Z=sum_q q f_q, verify

    Z-Z*=CA-CR,
    I-I*+Qgas+Eesc-Eabs=0.

This is an event energy-transfer identity for the prescribed bath. Qgas is a
diagnostic transfer to/from the bath; T is not updated. The corrected trace
is not pasted into old photon/gas ledgers. Full photon count, pressure and
shear-work conservation belong to the unmodified ANGTHERM01 calculation.

## Controlled attenuation omission: derived comparison and numerical test

The continuous reference has g=G0 exp(-tau), tau'=YLi k f0,
YLi=5.0001e-10. Fix delta=2e-8 before execution. For0<=tau<=delta,

    exp(-delta)Lambda0 <= Lambda <= Lambda0.

Late exact and thin solutions share the bath, initial fractions and upper
states. Writing d=f_exact,0-f_thin,0 gives

    d'=-(r1+Lambda)d+(Lambda0-Lambda)f_thin,0.

Since0<=f_thin,0<=1 and Lambda0-Lambda<=(exp(delta)-1)Lambda, variation of
constants gives0<=d<=expm1(delta), uniformly in the large photoionization rate.
LiII has the opposite difference; upper fractions coincide. This is a derived
conditional result, not a deduction from observing a small nodal tau.

Close the optical-depth assumption with a full-time comparison from eta0:

    F'=r1(1-F)-exp(-delta)Lambda0 F, F(0)=0,
    B'=YLi sigma_max(c nHref/H)F, B(0)=0, until eta_last.

The original LiI has only nonnegative additional photoionization sinks and
fLiII<=1-fLiI, hence fLiI<=F as long as tau<=delta. Check the seeded late
fLiI(eta*)<=F(eta*) explicitly. Any initial angular profile satisfying
0<=tau(eta*,mu)<=B(eta*) is covered. B(eta_last)<delta closes a first-crossing
bootstrap for that family, without assigning an optical history to new nodes.

For the adopted LiI fit on[5.392,10]eV, sigma_max=1.66e-18cm². Its analytic
stationarity polynomial in u=sqrt[E/(3.107*15.01)] is

    -7*15.01*u³+(4.895-7)*15.01*u²+11u+(11-4.895)=0.

One coefficient sign change gives one positive stationary root. Its E is
6.70826323365278eV, sigma1.65892479072499Mb; endpoints are lower. The chosen
1.66Mb includes a rounding margin. Verify the row and this bound separately.

Compute B twice at the two time tolerances. The numerical bootstrap check is
max(B1,B2)+1e-10<delta, with |B1-B2|<1e-11 and positive fractions. The1e-10
allowance is a declared numerical robustness margin, not interval arithmetic.
Report both the analytic implication and the actual numerical check distinctly.

The remaining higher-bin photon number Ntail from saved log counts bounds
future extra absorption events by Ntail per Href, or Ntail/YLi per Li nucleus.
Evaluate this ratio in log space before exponentiating, preserving a possible
subnormal raw count. No continued emission or additional photon births exist.

## C1–C8: implementation and finite execution contract

Allowed implementation paths: only this new unit. Old source/data remain
unchanged. Import the prior sibling unit's source fits and background helper;
package the needed sibling bytes for clean reproduction. No Rust installation,
new clone/worktree, dependency installation or whole-project CI changes.

Requested implementation worker:gpt-6.1-sol/high per AGENTS. Record requested
and observed identities separately. Controller owns scientific decisions;
fresh Astra reviewer reads math, actual code, raw results and plots.

Use scipy Radau with the exact linear-state Jacobian; its finite-ray attenuation
control includes dLambda/dtau and tau'=YLi k f0. Standard rtol2e-9, atol fractions
2e-12, other ledgers2e-11; optical depths2e-14. Tight uses rtol2e-11 and atols/100.
For the bootstrap B use atol1e-14 standard and1e-16 tight. Retain signed numerical
roundoff, solver status, counts, accepted states and errors. No retries without
identified cause; no completed case reruns for packaging.

Execute these TEN small cases once, after local algebra/input checks pass:

| ID | Case | Purpose |
|---|---|---|
| 1 | fixedM16_attenuated, primary, tight | Reconstruct late saved M16 with16 evolved optical depths and exact saved initial depths |
| 2 | fixedM4_thin, primary, tight | Discrete support control, same bath/seed |
| 3 | fixedM8_thin, primary, tight | Discrete support control |
| 4 | fixedM16_thin, primary, tight | Separate attenuation omission from support quadrature |
| 5 | splitGL8_thin, primary, tight | Low-order support-resolved candidate |
| 6 | splitGL16_thin, primary, tight | Selected candidate |
| 7 | splitGL32_thin, primary, tight | Angular refinement control |
| 8 | splitGL16_thin, secondary PCHIP, tight | Bath reconstruction sensitivity |
| 9 | bootstrapGL32, primary, standard | Global opacity envelope, eta0..last crossing |
| 10 | bootstrapGL32, primary, tight | Numerical envelope sensitivity |

These are four chemistry states plus five ledgers (case1 also16depths), or two
bootstrap states. They are not ten new coupled gas/photon trajectories. Optional
repair must have a concrete diagnosis; maximum12 attempts total. Total new
solver/check/analysis CPU allowance120s and wall180s, memory1GiB, one BLAS thread.
Per invocation CPU60s/wall90s. Initial saved-only diagnostic1.286CPU/1.172wall
is counted separately as source inspection, not hidden inside the new IVPs.
Prepare/package wall cost is reported separately. Failure preserves raw/partial
states and stops that batch; no silent tolerance or claim changes.

Independent coefficient checks: endpoint support roots; b=0 and opposite-sign
support; normalization for constant integrand; nonnegative angular weights;
GL8/16/32 vs an independent scalar quad energy integrand at at most121 specified
etas including points very near each endpoint. Quadrature gate for Lambda is
abs difference<=1e-10*max(1,abs(Lambda_quad)); energy coefficient analogous with
scale1eV. At least one deliberately unsplit low-order rule must expose the
support defect. Verify generator sums, Jacobian, charge/energy derivatives and
constant-coefficient matrix-exponential solution independently; do not mirror
the same implementation as both oracle and candidate.

Acceptance: mass residual<=2e-10, minimum raw fraction>=-2e-12; event energy
residual<=2e-9eV per Li and charge residual<=2e-10. Case1 vs saved M16<=2e-7 on
matching late reports; selected split16/32 fraction difference<=2e-8;8/16 is
reported separately. The fixed16 thin/attenuated difference must be consistent
with expm1(delta) plus a2e-9 numerical allowance. Primary/secondary bath difference
is reported and must be<=2e-7 for claiming the threshold improvement transfers
to the saved trajectory at that target. If a gate fails, keep its actual result
and determine the smallest diagnosed repair or narrower admission.

Save per-case NPZ/JSON, common comparisons and cost receipts. Plot and directly
inspect: (1) rate/support curves and Li fractions across the crossing interval,
(2) signed fraction errors vs split32, and (3) bootstrap/ledger residuals. Label
all variables, units, native Li-fraction normalization, and conditional bath.
Do not present successive GL differences as certified asymptotic order.

## R6–R10 / C9–C10: review, decision, publication and resumption

Independent source/math intake is in intake_angtherm02_20261023. Freeze this
contract then implement; reuse earlier invariant proofs when inputs match.
New no-go claim: none; NG1–NG7 admission is not invoked. The scope is constructive.

Checkpoint groups: prepared theory+inputs; implemented+observed; final reviewed
decision+handoff. Every R/C stage links its evidence and checkpoint in DAG.json.
Publish additive UTF8 text to the existing PR221 branch with expected-head lease;
put all binary source/results/figures in complete checkpoint ZIPs on the existing
Drive folder and Dropbox backup path. Preserve PR222 and the original unit.
No merge/force push. Record actual provider/commit receipts; no remote download
claim unless performed. Next task follows the remaining error or coupling
dependency, based on measured results, rather than a predetermined larger sweep.
