# R17B2B: actual continuum homotopy, second variation, and C2 birth lemma

The recovered R17B2A remains a nominal point/tangent/adjoint calculation. It is
not renamed to a complete R17B2 interval certificate. All physical coefficients
are the original FT03 donor binary64 literals realified as constants. Gas is
(h,y,z,W/W0), photons are counts/H, u=t/T, T=1250000000 proper seconds. Original
initial gas and photons are identical on both source sides for each theta.
Initial photon energy ranges over its original box; all source atoms, continuous
births and arbitrary probes inject the SAME fixed13.7eV source channel. Initial
energy is a separately matched parameter, not a demand that its uncertain value
must equal the fixed source energy. No numerical source coefficient, temperature
floor, extra cooling process, Grackle input or CR effect is introduced.

## Actual continuum Volterra map and full feedback

For a prescribed gas path g, let a_b=T*c*nH*sigma(E_b), k_b=a_b*(1-h),
v_b=(1,0,0,(E_b-chi)/W0), E_b(u)=Eb*exp[-H*T*(u-b/T)]. The positive survivor
P_b(u)=exp[-int_(b/T)^u k_b(s)ds]. The gas-path map is

Phi(g,mu)(u)=g0+int_0^u N(g,s)ds
             +0.05*int_0^u k_0 P_0 v_0 ds
             +int_(b<=u*T) int_(b/T)^u k_b P_b v_b ds mu(db).

Here mu_eta=(1-eta)*sum_i wi delta_bi+eta*S db. The continuous photon population
is eta*S*P_b(u) db; it is not replaced by finite births in any interval result.
Continuum_integral performs outward range integration of this actual measure,
including every previous atom with physical right trace. The bound calculation
uses analytic whole-domain majorants of its integrated kernel, not sampled
integrands. The integrator alone remains conditional on a valid panel range.

Dg P_b[h]=P_b*int_b^u a_b*h_H ds. Thus existing photons' gas response and memory
are retained. The instantaneous block includes gas-photo derivative A, old
photon response C=-p grad(kappa), and D=-diag(kappa), in p/H coordinates. No
p/P0 scaling is borrowed silently from the donor. The full nonphoto Jacobian and
Hessian are interval differentiated. The original R17B2A optical adjoint and
separate arbitrary-birth forcing integral are reused for NEW diagnostics.

## Uniform solution and source-sensitivity tube

The closed rectangle [.89,.91] x [.29,.31] x [.59,.61] x [.99,1.01] encloses every
same initial-state solution for eta in[0,1] and all original weight boxes. A
whole-domain interval RHS bounds each integrated gas displacement strictly
inside the actual initial-to-rectangle margins. Positive source and opacity
imply survival in[0,1]. Photon mass is bounded by
P=0.05+max(S*T,sum upper original weights), using convexity rather than adding
both source masses. Temperature and energy remain strictly inside the original
thermal-fit and HI-only branch-free domains. He populations remain positive
with HeII+HeIII<1. These are calculated inequalities, not interval booleans.

Write A=sup a, K=sup k, V=max(1,sup|E-chi|/W0). With normalized state infinity
norm, let L_N=max_i sum_j |N_ij| and B_N=max_i sum_jk |N_ijk|, computed over the
WHOLE time/state rectangle using directed interval Hessians. Then

q = L_N+P*V*A*(1+K) <1,
B_gmu = V*A*(1+K),
B_gg = B_N+P*V*A^2*(2+K).

The first derivative photo term includes both current -a*h_H and memory
k*int a*h_H. The second derivative photo term is
P_b*v_b*(-a*h_H*I_l-a*l_H*I_h+k*I_h*I_l), I_h=int a*h_H.
This proves the stated second-variation majorant. Banach contraction supplies
the actual continuous-source gas path for all eta/theta. Smoothness of the
original analytic equations and the dominated Volterra map supplies its source
differentiability, including one-sided endpoint eta derivatives.

Let nu=mu_S-mu_Q, Dnu=S*T+sum wi (the continuous and atomic measures are mutually
singular). This total variation retains the mass mismatch; it does not normalize
weights or assume Gauss moment exactness. The uniform first and second eta
sensitivity bounds are

U1 = V*K*Dnu/(1-q),
U2 = (B_gg*U1^2+2*B_gmu*U1*Dnu)/(1-q).

For the actual Thomson goal use
G=T*c_SI*sigmaT_SI*1e6*sup nH*(1+3*fHe).
Then the exact eta-integrated finite-source response lies in[-G*U1,G*U1]. Its
radius is about9.9973754e-17. This is a valid WHOLE HOMOTOPY candidate, not a
nominal K sample or sign theorem. It is much wider than the documented causal
fallback2.125035e-18, hence NO_CERTIFIED_SOURCE_SHARPENING.

The independently reported finite-source nonlinearity remainder is
|tau(mu_S)-tau(mu_Q)-Dmu tau(mu_Q)[nu]| <=G*U2/2 <2.92584e-23.
This closes a genuine missing nominal-tangent remainder premise. It does NOT
make an unvalidated nominal source quadrature integral a certified interval.
No original R16B time interval is added here; the replacement/combination count
is zero and both distinct R17A derivations remain unchanged.

## Physical same-energy C2 lemma closed for this homotopy

On the proved rectangle, atomic rate functions, sigma and energy/redshift are
smooth: every fractional-power/log base and denominator is strictly positive;
thermal and HI/HeI cutoffs are excluded over the full macro. Between the six
source atoms, constant continuous injection and these functions are smooth.
The gas state is continuous at an additive photon birth. Full gas adjoints solve
bounded linear Volterra equations and are continuous; additive injection has
identity derivative on old state. The energy-extended photon adjoint is

(partial_u-H*T*E*partial_E)psi=kappa*(psi-v.lambda_g).

It has an integral representation along energy characteristics with smooth
energy coefficients on a compact domain. Differentiation under that integral
is dominated by bounded sigma/energy derivatives and the bounded adjoint flow.
Its energy derivatives have continuous time traces at the atoms. This is a
qualitative smoothness argument supported by actual branch/tube inequalities;
it is not a quantified mixed time/birth derivative tube.

For a source atom of weight m=(1-eta)*wi, let R=psi-v.lambda_g and
kg=grad_g kappa at the physical injection energy. Since the background atom and
probe use the SAME physical channel (source alias, not just equal interval
boxes),

[g_u]=m*kappa*v,
[lambda_g,u]=m*kg*R,
[kappa_u]=m*kappa*(kg.v),
[K_bb]=[kappa_u]*R-kappa*v.[lambda_g,u]=0.

All energy-trace terms are continuous. Hence J0=J1=J2=EXACT0 at all six known
atoms for every eta and original weight. Initial energy uncertainty does not
alter this equality of the source and probe channels. An independent energy
alias or changed injection energy is rejected. At eta=1 no source atoms remain.
Different energy channels or a branch/cutoff event would not satisfy this lemma.

The known physical regularity partition is[0,*six original birth clocks,T].
Source-cell/output/proof boundaries away from these atoms are artificial cuts
of smooth physical equations, so they carry exactly zero physical jumps through
order3. PARTITION.json includes the supplied such cuts and the exact reason.
This qualitative partition does NOT provide numerical J3 or K4 bounds.
K_bbb jumps at the source atoms remain unknown. No toy -93/20000 is adopted.
Regular K_bbbb and anchor K1..3 remain quantitatively unproved. R17B1's local
x derivative convention requires(h/T)^r times global-u derivatives; its
moment/hinge coefficients already contain factorials. The99.7754% first-cell
share is a coefficient budget, not an error share. No Peano coefficients or old
CDF calculations are recomputed in this task.

## Auxiliary quadrature and diagnostic limits

NEW eta=.5,1 point experiments use16/32 auxiliary midpoint births per original
source cell with an independent additional quadrature budget. This is not an
adopted physical source plan. For a prescribed gas path, birth absorption and
heat response slopes are bounded respectively by
K+Kb and Q*K+Qb*K+Q*Kb+Q*K*(K+Kb),
where Kb is the fixed-gas global-b derivative bound and Q=(E-chi)/W0.
Exact rational midpoint distance moments give
W1=S*sum_cells(width^2)/(4*n*T), with realification clock and mass errors added.
The gas-map contraction turns this into an exact-IVP optical quadrature radius
at eta=1 of about4.31001e-19(n16),2.15501e-19(n32). The tiny auxiliary mass
rounding correction is included in the comparison tube/self-map/contraction.
These bounds compare exact auxiliary and exact continuum IVPs. They do NOT
bound the NumPy point solver's integration error; diagnostic values remain
DIAGNOSTIC_ONLY. Finite sampling does not certify a whole-b/eta sign.

The unchanged R17B2A baseline supplies four NEW surrogate backgrounds, twelve
full forward probes and independent backward+forcing paths, three positive
finite-dose runs, and one memory-off negative control. The control breaks the
photon conservation identity and is never a physical fallback. Heating,
ionization, temperature and instantaneous/terminal derivatives are distinguished.
No R17B2A eta=0 suite, old donor root, R16B/R17A/B1 science or other repository
lane is run. Direct donor RHS evaluations used in independent checking are
read-only equation evaluations, not old suites.

## Verification scope and final gate

A separately written Decimal60 donor RHS is compared to the new interval
transcription over a whole time/state panel, with p/P0 row/column and short-clock
normalization explicitly transformed. Independent MP110 equations check4 values,
16 gradients and64 Hessians;8 point corners satisfy interval inclusion. This is
an independent RHS evaluation, not the R16B shared-AD panel check. Separate
MPFR256 arithmetic recomputes the entire homotopy/second-variation majorants;
it explicitly shares the new physical RHS expression. Such numerical checks
support the directed-rounding implementation; the whole-domain inequalities,
not sampling, establish the bound. No proof assistant or external review occurs.

Current claim: continuum homotopy value/sensitivity/nonlinearity bound and the
physical same-channel C2 lemma are closed, source sharpening is not. J3/K4/anchor
quantitative Peano certification remains OPEN. peano_transfer fails closed.
Protected: CR_OFF_FASTEST,precision atomic PARKED,physical/production HOLD,
G02 UNRESOLVED,b_grid NO_GO,Grackle/G02 owner-input lanes unchanged.
