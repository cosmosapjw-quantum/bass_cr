# C15: Bianchi-I 연속 photon source 및 H/He time-centering

## Authority / 단위

- bass_cr parent C14 commit bf1fa9c36511f27798d4081dd331e74fd33b678a.
- Read-only rei_bianchi owner commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
- C11 SHA-pinned owner Scenario/Spectrum/C8 source constants preserved.
- Signature (-,+,+,+); proper time s; photon energy eV; densities proper cm^-3; photon-number per original H.
- Controlled initial gas at a=.1: xHI=.9, xHeI=.85, xHeII=.15, xHeIII=0, Tg=4000 K. Interval a=.1..11.
- The owner SOURCE07 spatial ray/radiative intensity/Jacobian R J_Omega is NOT computed here. This is a spatially homogeneous source-age/chemistry numerical supplier.

## Time-integrated continuous photon source

At birth in an orthonormal Bianchi-I frame, photon has mu_birth and E_birth.
Exact geometry energy adapter:
  E(a)/E_birth=(a_birth/a)*sqrt[(1-mu²)exp(2 Delta b)+mu² exp(-4 Delta b)]
with Delta b=b(a,q)-b(a_birth,q).
q=0: E/E_birth=a_birth/a. No repeated expansion dilution of photon number/H.

The actual owner source count on the interval:
  Delta N/H=(Delta ln a)*Scenario.rate(a_mid)/H(a_mid,q).
For frozen midpoint gas n_j and photon E_k,
  lambda_kj=c*n_j*sigma_j(E_k),  tau_k=dt*sum_j lambda_kj,
  dot N_k = S_k - lambda_k N_k,
  N_end=N_start*exp(-tau)+S_k*dt*(1-exp(-tau))/tau.
At tau=0 continuous limit phi=1. For every packet,
  A_kj=(N_start*(1-exp(-tau))+Sdt*(1-phi))lambda_kj/lambda_k.
N_start+Sdt=N_end+sum_j A_kj, A>=0, N_end>=0.

Algorithm: redshift existing photons to a_mid, adiabatic gas half-step,
C14 self-consistent midpoint electron-density Case-A RR half-step;
evaluate both old photons and continuous newborn source at half dt as a
discarded gas midpoint predictor; integrate full dt exact Duhamel from
the ORIGINAL packet plus emission rate with midpoint gas opacity;
update H/He photoevents and species photoheating, remaining half RR,
adiabatic expansion and photon energy redshift to a_end. Ledger tracks
photon-number, physical photon energy, expansion work, photo binding/heat,
recombination escaping binding/thermal energy and charge/nuclei.

The local step is EXACT only for constant proper source, gas opacity
and photon energy. Full Bianchi-I redshift and proper gas temperature/
opacity vary between stages and are currently midpoint approximations.

## Independent validations

In zero opacity (all HII, all HeIII, recombination off),
independent QUADPACK against actual owner source:
 N_end=integral[Scenario.rate(a)/H(a,0) dln(a)].
 FLRW redshifted photon energy:
 U_end=<E_emitted>/a_end *
       integral[a*Scenario.rate(a)/H(a,0) dln(a)].
The emitted spectral mean energy comes from an independent SciPy QUADPACK
evaluation of owner Spectrum.phi(E). 16,32,64,128-step grid refinements
give approximately second-order photon number and radiation energy.

At q=0, nstep32, strong opacity:
 xHI=0.8021905024753476; Tg=6627.044382590808 K,
 surviving photons/H=6.670100319137988e-6;
 photon ledger residual ~4.16e-17 photon/H,
 local energy ledger residual ~4.44e-16 eV/H.
C13 point-midpoint birth survivor at same timestep is 9.2013e-14/H.
This difference is a model/discretization comparison, NOT an observational
claim or an independent EoR error estimate.

The weak source (<5500K throughout), strong source without recombination
and hot gas (>5500K throughout) yield successive-grid gas xHI orders
about 2.02..2.20. Strong source beginning at 4000K crosses the 5500K
owner H recombination coefficient branch and xHI order at finest grid
drops to about 0.90; this correlation does NOT alone prove that the
coefficient branch is the only cause.
Across all opacity-active cases, the final surviving photon stock retains
roughly 1st-order successive-grid convergence (order ~0.98..1.00).
Thus there is NO claim of uniform second-order source-radiation solver.

## Analytic endpoint extension, held from main RT path

For linearly varying source S(t)=S0+(S1-S0)t/dt at CONSTANT opacity,
Wolfram independently derives the exact newborn photon contribution:
 dt*[S0*(phi1-phi2)+S1*phi2],
 phi1=(1-exp(-tau))/tau, phi2=(tau-1+exp(-tau))/tau^2.
At tau=0: (S0+S1)dt/2. Positive implementation in linear_source.py
has SciPy QUADPACK scalar parity and species photon ledger tests.
It is NOT exact for varying ionization state, frequency redshift or
source-age direction. Future work should use this as an isolated oracle,
not silently insert as current SOURCE07 owner transport.

## Optimization scope

Born-spectrum template is cached once. Zero packet pruning removes only
EXACT floating-point zeros; no arbitrary photon count cutoff.
Matched n=128 local benchmarks: cached+pruned 0.373s;
uncached+pruned 0.408s; cached+unpruned 0.776s (3-run medians).
C15 packet arrays 255920 vs unpruned 983040 bytes.
3 independent q jobs via OS spawn: 1 process 1.074s, 2 1.168s,
3 0.816s (medians). No claim about production Rust runtime speed.
Native subagent NOT_RUN, local Codex NOT_USED.

## Scientific handoff and future gates

Actual owner SOURCE07 transported age-resolved photon/ray stocks and
R J_Omega mapping, full igm_thermal chemistry/cooling/OTS, source
variability inside a step, external frequency/angular quadrature error,
stiff independent full-physics reference and EoR xHI/HeII/HeIII/Tg
history remain unresolved. Production admission HOLD.

Primary methodological sources:
Mellema et al. C2-Ray, arXiv astro-ph/0508416.
Friedrich et al. (2012) MNRAS 421 2232, H/He multifrequency.
Norman et al. (2015) ApJS 216,16 coupling radiation and chemistry.
Southworth et al. (2024) IMEX RK JCP DOI 10.1016/j.jcp.2024.113339.
Zingale et al. (2021) Strang-split reacting flows arXiv:2103.13193.
