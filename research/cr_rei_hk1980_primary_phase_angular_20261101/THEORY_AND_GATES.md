# R1–R10 | Primary HK1980 phase-authentic H+–H angular transport (2026-11-01)

## R1 Objective/authority
In `cosmosapjw-quantum/bass_cr`, rederive the **finite-original-partial-wave, charge-labelled** elastic and resonant CX scattering angular distribution for two *genuinely source-transcribed* Hunter–Kuriyan (1980) energies `E_cm=0.1,1.0 eV` from preserved WU088 P0 R12 source. Provide the actual full-angle DCS and physically conserved first two angular moments, not another A7 rate fit or 192-interval surrogate. User-scoped priority: the source remains an optional IGM kinetic-collision dependency, **not** a new REI central F05 state, CR-ON production operator, or cosmological observable.

Source archive: `/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip`, SHA256 `562aba864fa55119e8454f4484ae3b09433df990ab589a3b9725544a8b6a5913`. Source member `data/HK1980_FIRST_SLICE_PHASES.csv`, SHA256 `ae2b3159eaefc699ec8763f3153dddfd3a3ce2aca6151a9a1718ab67997ca6c2`. 674 transcribed phase rows = (147+190)×2 independent g/u molecular-symmetry phase values. Input manual transcription is archival-source-conditioned, *not* a newly authenticated publisher-provided machine-readable file. Original source ZIP/phase arrays/scan images remain PRIVATE; only computed derived moments/DCS are Git-published.

Parent history: protected BASS-CR PR #157 SHA `afd21458a023f40c6a5a0fb900742a5d90aaecd6`; original separate unfinished untracked local `bass-cr-hk1980-joint-20261101` worktree was read-only, and verified code/output bytes were transplanted into this new worktree. Original REI central 28/88, working 33/88, BASS-CR extension 0/3; no DAG promotion authorized.

## R2 Primary literature
Hunter & Kuriyan, *Scattering of protons by hydrogen atoms at low energies: Phase shifts and differential cross sections*, Atomic Data Nucl Data Tables **25**, 287–310 (1980), DOI `10.1016/0092-640X(80)90006-6`, published phase shifts to six decimals, 10^-4–10 eV in CM. Only the two archival energies below are read here.
Schultz et al., J Phys B **49**, 084004 (2016), DOI `10.1088/0953-4075/49/8/084004`, independent 1301-energy calculations and angular DCS, sampled at 1 eV by parent PR #156; original complete DCS is NOT_RETRIEVED.
Schultz et al., Atomic Data Nucl Data Tables **154**, 101601 (2023), DOI `10.1016/j.adt.2023.101601`, explicitly distinguishes physically indistinguishable proton scattering and distinguishable elastic/CX contributions, especially E_cm <~ 0.01 eV.
Glassgold, Krstić & Schultz, ApJ **621**, 808–816 (2005), DOI `10.1086/427686`, identical-proton joint low-E momentum transport; physical collision rate cannot be automatically inferred from the charge-labelled sum.
The authoritative UGA original machine tables exist in the portal but direct fetches timed out; no invented underlying source rows.

## R3 Conventions and units
Unpolarized nonrelativistic proton + neutral H(1s), CM kinetic energy fixed at original printed E in eV. `a_0=5.291772109e-9 cm` as rounded in the existing source module; source fixed wavenumbers `k=(2.597682,8.214591) a_0^-1` at E=(0.1,1.0) eV. Symmetry phase values `delta_l^g,delta_l^u` in radians, `S_l^{g,u}=exp(2i delta_l^{g,u})`.
`b_l^g=exp(i delta_l^g)sin(delta_l^g)`, analogously `b_l^u`; charge-labelled elastic/capture amplitudes `b_l^{el}=b_l^g+b_l^u`, `b_l^{CX}=b_l^g-b_l^u`. Nuclear-labelled outgoing-angle variable `x_N=cos(theta_N)`; outgoing **charged-particle** angle `x_charge=x_N` (elastic), `x_charge=-x_N` (CX). A source convention cannot be inferred from an empirical total event rate.

## R4/R5 Exact finite-L derivation
With `0<=l<L`, `f_c(x_N)=sum_l (2l+1)b_l^c P_l(x_N)/(2k)` and `d sigma_c/dOmega=|f_c|^2` in `a_0^2 sr^-1`. Define
`Q0=pi/k^2 sum_l(2l+1)|b_l|^2`.
`Q1=(2pi/k^2) sum_{l=0}^{L-2} (l+1) Re(b_l conj(b_{l+1}))`.
Define `C_j=j b_{j-1}+(j+1)b_{j+1}` with unavailable b outside [0,L) =0, `Q2=(pi/k^2)sum_{j=0}^{L} |C_j|^2/(2j+1)`.
Then `sigma_el_total=Q0_el`, `sigma_el_mt^charge=Q0_el-Q1_el`;
`sigma_CX_total=Q0_CX`, `sigma_CX_mt^charge=Q0_CX+Q1_CX`;
`sigma_viscosity=Q0-Q2` for either. These follow Legendre orthogonality and `xP_l=(l+1)P_{l+1}/(2l+1)+lP_{l-1}/(2l+1)`.
For each finite-L partial-wave solution, sample 768-point Gauss–Legendre nodes on x_N with weights w_j. `2pi |f_c(x_j)|^2 w_j` is the exact quadrature contribution to sigma_total, and `1-x_charge` and `1-x_charge^2` give transfer/viscosity moments. With max polynomial degree 2(L-1)<=378, 768 GL nodes integrate analytically formed finite-L observables exactly within floating rounding. This is an **independent** angular realization of the partial-wave sums (not independent atomic theory).

Charge-labelled elastic+CX momentum-loss sum `sigma_el_mt+sigma_CX_mt` is only a **diagnostic**; it must NOT be promoted as full physically spin-symmetrized indistinguishable-proton momentum-transfer cross section, especially below ~0.01 eV. Need nuclear spin populations and coherent/exchange interference conventions to do that.

## R6/R7 Mathematical and physics checks
Direct finite-L nonnegativity `0<=sigma_mt<=2sigma_total`, `0<=sigma_vis<=sigma_total`; total `Q0` is positive, incoming relative flux normalized. Channel identity `|b_el|^2+|b_CX|^2=2(|b_g|^2+|b_u|^2)` at every partial wave, confirming unitary channel decomposition at fixed l. CX outgoing charge angle has reversed `Q1`; wrong sign would produce the *wrong momentum-transfer operator* despite identical total cross section. The 2016 sparse original DCS comparison is labeled **DIFFERENT_SOURCE_NOT_PARITY**; it cannot certify physical source equivalence.
Wolfram analytic real l=0,1 check: `f=(b0+3b1 x)/(2k)`: (i) `sigma_total=pi(b0^2+3b1^2)/k^2`; (ii) `Q1=2pi b0 b1/k^2`; (iii) `sigma_vis=pi(2b0^2/3+6b1^2/5)/k^2`; residuals {0,0,0}. Later numeric 768 GL, independent 512/1024 GL, and direct sum checks require executed logs.
Hostile target: finite-L tail closure at L=147/190 is not proof of all higher-l original physical convergence; original printed six-decimal phases are not exact analytic amplitudes; low-E quantum interference and nuclear spin remain blocking physical full joint rate. No extrapolation to BASS193 100–12000 K, no 46k F05 synthetic tilt, no CR-ON claim.

## R8/R9/R10 Decision, coding contract and stop
One bounded primary-derived atomic science unit: four channel×energy integral moment rows, 6 sparse 2016 comparisons, plus 3072 *new* source-derived angular distribution records (2 E × 2 channels × 768 angles). For angular output include E_cm, finite L, channel, x_nuclear, x_charge, theta_nuclear_rad, theta_charge_rad, quadrature w, dSigma/dOmega a0^2 per sr, preweighted 2pi dSigma/dx a0^2, local total/mt/viscosity quadrature contribution; accept only if independent 768 GL moments match source sums at justified double precision and complete deterministic cold replay succeeds with original private ZIP. Report channel CX fraction of *charge-labelled* MT, not spin-averaged physical drag. REI central **28/88**, REI working **33/88**, BASS-CR optional **0/3**, changes 0. Production HOLD, no REI mutation, no merge, no force push, no silent extension beyond two original energies. Stop further optional work after this original-source phase result until REI source-owner F05 [160,161] admission and source-matched physical tilt/packet contract.
