# Coulomb-matched partition decision, 2026-10-14

Selected node: `NT_COULOMB_MATCHED_PARTITION_DECISION`, R5 constructive derivation and local checks. Parent PR58: `808d11c1869c6334572554edcb24370e35c69f44`. The adjacent `coulomb_partition.py` is the tested local Maxwell-bath reference, published at `7900d17dcf4f13c07cdd144b1abc85e53811e3e4`. It is not the nonlinear production collision operator.

## Decision

Preserve the original20kBT instantaneous model and finite-rate family as separate baselines. Do not calibrate the physical thermalization time from the tau=.001s numerical error budget. The next physical comparison uses **reversible kinetic/core flux, energy diffusion, angular scattering and a single opposite bath collision-energy moment**. Replace the original Coulomb component within that comparison lane; do not add a second stopping/thermalization heat for the same interaction.

This unit supplies local Maxwell-background coefficients, source-anchor diagnostics, exact moving-interface balances, a reversible finite-band reference and exact eliminated-core memory. A physical tau, nonlinear Landau/core closure and new full-source temperature/opacity intervals remain null. This is a completed scoped decision, not a declaration that the entire source has Maxwellized.

## Exact source and conventions

Signature(-,+,+,+), bath-rest proper seconds, W and theta=kBT/epsilon_eV in eV, epsilon_eV=1.602176634e-19J/eV. Keep c and kB. The local coefficients assume a nonrelativistic, nondegenerate, weakly coupled Maxwell electron background and a constant leading Coulomb logarithm unless the explicitly separate running-log extension is selected.

Actual SOURCE_RATES.npz SHA256 `3c63d0cd77c6fa03b19a2349f6a039cb9056d3594afd7dfcf50d192a5c066ae2`. Grid23 is offset0. Selected file fields are energy,target,alpha,L0,kappa,mass,grid_indices; this selected file has no energy-diffusion field. No all-repository absence claim.

From the exact stored values and scalar IC:

- W*=0.174250000000000016eV, DeltaW=.0030937500000000062eV.
- T0=101.10236413400510K, theta=.008712327653334758eV.
- nc=1/V0=.9940179640539353m^-3, Coulomb log27.00113613862255.
- b*=alpha23*nc*logLambda=4.968199677294018e-10eV/s.

Numbers below are high-precision POINT diagnostics, not directed physical uncertainty intervals. Original scalar CASE has an ancestral static-reference geometry label; it is not used to overwrite the moving parent's geometry.

## 1. An edge wait is not Maxwellization

An internal downward generator W->W-DeltaW at lambda=b/DeltaW gives mean dW/dt=-b and infinitesimal second-moment coefficient D_jump=b*DeltaW/2. The latter vanishes under grid refinement. It is not the finite-temperature Coulomb diffusion coefficient.

At an absorbing node23->bath edge the tagged active kinetic energy loses the whole W. Its heat moment is lambda*W, not lambda*DeltaW=b. Here W/DeltaW=56.3232323. This is the explicitly declared old coarse-graining closure, not an alleged upstream implementation bug.

## 2. Time/count Maxwell-bath coefficients

Let x=W/theta, F(x)=erf(sqrt(x))-2sqrt(x)exp(-x)/sqrt(pi), G(u)=F(u^2)/(2u^2), and b0(W)=b*sqrt(W*/W) for the frozen-log source anchor. Transform the original velocity-space coefficients of Jeffrey et al2014, AppendixA1-A4, into count per energy, not their path-length electron-flux spectrum:

    N(W)=4pi*epsilon_eV*v*f(v)/me,
    p_theta(W)=2sqrt(W)exp(-W/theta)/(sqrt(pi)*theta^(3/2)),
    D_W=theta*b0(W)*F(x),    Var(dW)=2D_W dt,
    j_C=-D_W[partial_W N+(1/theta-1/(2W))*N]
       =-D_W*p_theta*partial_W(N/p_theta),
    a_W=D_W'+D_W*(1/(2W)-1/theta)
       =b0(W)[4sqrt(x)exp(-x)/sqrt(pi)-erf(sqrt(x))],
    nu_Omega=b0(W)/(4W)*[erf(sqrt(x))-G(sqrt(x))].

The angular operator is nu_Omega*Delta_S2, so the local l-mode decay is l(l+1)nu_Omega. Electron-ion pitch-angle scattering/energy exchange are separate contributions. The velocity-flux equilibrium vN is proportional to Wexp(-W/theta), whereas count equilibrium is sqrt(W)exp(-W/theta).

With b0=C/sqrt(W), low-energy limits are D_W/W->4C/(3sqrt(pi theta)) and a_W->2C/sqrt(pi theta)>0. At high energy a_W->-b0 and D_W->theta*b0. Upward diffusion/heating are required for stationary Maxwell balance.

For the DECLARED equilibrium-preserving running-log extension L(W)=L*+1.5log(W/W*):

    D_run=D_W*L/L*,
    a_run=(L/L*)*a_W + D_run*1.5/(W*L).

This retains the derivative required by divergence form; it is not claimed to be an exact arbitrary-screening Rosenbluth model. Cold loss alone does not uniquely fix diffusion or angular scattering.

## 3. New numerical comparison

At the actual source anchor, W*/theta=20.00039564:

- D_W=4.32845829748e-12eV²/s, D_jump/D_W=.177550142514.
- Frozen-log cold-vs-warm mean-drag relative difference2.10480921e-8, despite nonzero diffusion.
- The running-log Ito correction at the anchor is .00277760592001*b*.
- Original edge waiting time6.22710478836e6s; local W*/b*=3.50730669696e8s.
- Local l2 angular decay2.39815720885e8s; DeltaW²/(2D)=1.10562334262e6s.
- Frozen-coefficient sqrt(2D*1e5s)=9.30425526034e-4eV, not a new integrated source variance.

For a fully activated1ms removal at this energy, W*/tau divided by b* is3.5073e11. This rate-scale comparison is not a claim that the initial gate is active; it is zero before contact. It does not calibrate tau.

A separate fixed-bath first-passage diagnostic uses absorbing3theta and reflecting40theta. The exact formula

    T(W)=integral_q^W dy/(D(y)*p(y))*integral_y^WR p(z)dz

solves a*T'+D*T''=-1 with T(q)=0,T'(WR)=0. Starting at node23 gives approximately2.31565946127e8s. This is not whole-source Maxwellization.

For an ALREADY Maxwellian distribution, number fraction above20theta is1.06550903343e-8 and energy fraction1.49336790005e-7. These tails do not prove that arbitrary nonthermal particles below20theta are Maxwellian.

## 4. Moving boundary and complete bath heat

Let F be cell count/eV/sr, g_W geometric energy drift, and positive flux point to increasing W. At partition q(t):

    Jrel=integral_Omega[j_C+g_W*F-qdot*F]_(W=q),
    IC=integral_tail j_C dW dOmega,
    Ntail'=+Jrel+SNtail;    Ncore'=-Jrel+SNcore,
    Utail'=q*Jrel+IC+Work_tail+SUtail,
    Ubath'=-q*Jrel-IC+Work_core+SUcore.

Thus the shared interface and bulk collision exchange cancel in total energy. Omitting -IC misses heat deposited before the electron crosses q; adding old b*N heat again double-counts it. Merely adding the opposite moment to a fixed-bath operator does not by itself prove finite-bath Maxwell shape, positivity or momentum closure.

A pure partition of the SAME distribution preserves total count/current/energy. Replacing the core by a Maxwell distribution is an extra approximation. In general retain momentum and spatial current too. Bianchi work remains -K_ab*Pi^ab and is not removed by instantaneous energy conservation.

For a disjoint Maxwell-shaped core below q,

    Nc=NM*P(3/2,q/theta),
    Ucore,e=NM*(3/2)*theta*P(5/2,q/theta).

The mean at20theta is1.49999979197745theta, not exactly1.5theta. Truncated-core potentials likewise differ from full-Maxwell potentials. Either evaluate the actual truncated distribution or explicitly use a full-background plus signed-correction representation. Do not count the Maxwell tail twice.

## 5. Executed reversible reference and memory

Five reflecting cells at(18.5,19.5,20.5,21.5,22.5)*theta use declared midpoint Maxwell masses pi and positive conductances c. Edge flux is c*(Ni/pi_i-Ni+1/pi_i+1). Hence Qpi=0, column sums0, off-diagonal rates>=0 and detailed balance. The discrete relative entropy decreases by the sum of negative edge products. This is a finite-band fixed-thermostat diagnostic, not a full-source physical calculation.

Eliminate two core cells exactly:

    Nc(t)=exp(Qcc*t)Nc0+integral_0^t exp(Qcc*(t-s))Qct Nt(s)ds,
    Nt'=Qtt Nt+Qtc exp(Qcc*t)Nc0
        +integral_0^t Qtc exp(Qcc*(t-s))Qct Nt(s)ds.

The two core eigenvalues in t/(theta/b*) units are-.139594726141 and-2.77505699373. The return-kernel log slope changes from-1.54750585682 on[0,1] to-.389754213129 on[1,2], so it is not one exponential. Direct matrix solution and memory reconstruction agree at1.86e-15(core state) and6.11e-16(tail RHS). Dropping core return leaves scaled RHS l1 error.1450. These are numerical checks of a derived exact identity, not a universal prohibition on reduced models.

A finite time-local memory error can instead use ||Nt'||<=LN and LN*integral_0^t s||M(s)||ds, retaining initial-core forcing and any truncated kernel tail separately.

## Physics boundary and successor

Initial nonthermal/core count ratio2 does not justify a dilute test-population assumption. Velocity-separated cross terms may still be bounded, but that must be demonstrated. A physical extension retains or bounds reciprocal/field-particle and tail-tail Landau terms, and electron-ion/neutral heat exchange if the nuclei share one T. The small fixed-bath reference does not settle them.

Next READY: `NT_REVERSIBLE_COULOMB_CORE_TAIL_PILOT`. Declare core/overlap ownership, use the tested reversible reference, and connect one bounded core-moment/collision comparison with partition/error control. Preserve the original20kBT and FR baselines and avoid replaying old atomic/history/HPC campaigns. Physical tau and new full-source T/tauT bounds remain null.

## Evidence, related sources and delivery

Actual Wolfram15.0.1:25 scalar literal zeros in19groups; actual xTensor1.3.0:6 tensor literal zeros. Official .m hashes match; formal-symbol/Limit warnings retained. New source/numerical validation70conditions and unit tests9pass. One manufactured drift-only Maxwell equilibrium RED->GREEN is preserved; remaining work is tests-after. Same author separate CAS/arithmetic, no external independent scientific reviewer or native subagent.

Read latest HE47 full R2_RESULT, HH64 detailed PR, REI116 metadata, and REI115 R8 full selection at39dce6702dcadbb516fc8e25e7ba5a6991f64c22. Reuse source/forcing/feedback and typed identity principles, not their foreign numeric rates/radii. Current source/native/global claims and CR/RCT/HH OFF unchanged.

Primary comparison: Jeffrey et al2014 arXiv1404.1962, doi10.1088/0004-637X/787/1/86; Ricketson et al2014 arXiv1301.5678, doi10.1016/j.jcp.2014.04.059. Parsed primary Appendix/entropy sections and SciSpace/Exa/web discovery were used. PDF screenshots failed cache retrieval; no visual-reading claim or redistributed papers/fonts. No novelty claim for standard Coulomb or entropy theory.

**Full executable archive:** BASS_CR_COULOMB_PARTITION_20261014_SOURCE.zip,1290755bytes,50members/49manifest payloads. SHA256 `eae5092cb0a7fb8a94a7bd8970c1e32b1f504ffa34c7107407794fccdfb35a34`.

[Full report, exact inputs, code, results, failures and DAG on Drive](https://drive.google.com/file/d/1y_9SELBlfUxMh1S6tkogA-JY2TdEMhby/view?usp=drivesdk), existing parent1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI. Upload plus ID/name/size/parent metadata matched.

Dropbox completed1290755bytes at `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_COULOMB_PARTITION_20261014_SOURCE.zip`, ID `id:BSpOijBcT10AAAAAAD5R1A`. The initial upload returned FETCH_FAILED; one retry completed. The failure is recorded in detached delivery, not retrospectively inserted into the immutable ZIP.

Local49payload hashes, parent56payloads, four nested archive CRCs and font absence were checked. Relocated verifier passed, modified-source control failed, restoration passed. Remote verification is R1 ACK/ID/name/size/parent, not full-byte restoration. No original overwritten, sharing change, main merge, force push, full source ODE, native receiver or HPC run.
