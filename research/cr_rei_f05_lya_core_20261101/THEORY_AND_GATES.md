# R1–R10: REI F05 original H/He-state Ly-alpha line-centre / Thomson opacity coefficient witness

Date 2026-11-01 KST. Repo `cosmosapjw-quantum/bass_cr`; isolated branch `research/cr-rei-f05-native-lya-core-opacity-20261101`.
Parent PR #158 HEAD `2ad9c6e1959afb92b876ecb82293040a579b0e81`, immutable. REI F05 original native 26-event owner PR #352 source state, V2 shadow PR #354, original accepted tick160/131072. No REI owner or original source mutation.

## R1 question / physical observable
For the **actual REI native 46,080-cell H/He material state** (accepted tick160, followed only by nonauthoritative tick161 preview), what is the source-conditioned *maximum possible* Ly-alpha line-centre scattering coefficient relative to the same material cell's Thomson coefficient, under the explicitly declared neutral-ground-state saturation model? This is an input to future BASS-CR resonant-photon transport, not a Ly-alpha light curve, scattering history, nor an actual photon-source coupling. New source-scoped physical quantity, not another BASS193/A7 rate fit.

## R2 primary inputs and literature provenance
REI PR352 original 46,080-node H/He and thermal preview artifact `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz`. Local private read-only source in `/home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101/primary/`. SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`, independently byte-identical in three original auditor lanes. Original 26-event TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted tick160 arrays SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`, reported by REI PR354, NOT reopened here. Source 27 columns: positive *cell-integrated* H nuclei `N_H`, He nuclei, HII fraction bracket and common gas T bracket at tick160 and candidate161, electron-number brackets, 46,080 cells. The source does **not** provide geometric cell volumes, a Ly-alpha occupation number or complete polarized resonant transfer. No private original state/archive republished.

Primary radiative-transfer formulas: Dijkstra, PASA 2014, arXiv:1406.7292, Ly-alpha basics f12=0.4162, λ=1215.67 Å, σ_α,Gaussian(10^4 K)=5.88e-14 cm²; explicit Voigt formula in ART2 MNRAS 424 884 (2012), https://academic.oup.com/mnras/article/424/2/884/1004516 and Smith et al. MNRAS 541 179 (2025), https://academic.oup.com/mnras/article/541/1/179/8160349. The literature formula is independent of the incomplete HK1980 p+H charged-particle collision operator. The original REI photon owner is four ionizing groups, **not** a measured 10.2-eV Ly-alpha photon field.

## R3 conventions and domains
Use nonrelativistic single-temperature gas `T_gas` for *neutral thermal Doppler width* (model assumption; no neutral-ion temperature split). H I(1s) fraction is unknown; define neutral ground-state fraction `0<=g_1<=1`, where `g_1=1` is explicitly a saturation model, not an REI-measured level population. Neglect extra turbulent broadening; thermally Maxwellian H I velocity profile. Physical constants in cgs: c=2.99792458e10 cm/s, kB=1.380649e-16 erg/K, mH=1.6735575e-24 g, me=9.1093837139e-28 g, elementary charge (Gaussian esu) e=4.80320471257e-10 statC, A21=6.265e8 s^-1, f12=0.4162, λα=1.2156701e-5 cm, sigmaT=6.6524587051e-25 cm². Do not mix SI and Gaussian electron-charge formulas. H I source nuclear count already includes both ground and excited populations; conditional maximal ground-state scattering at exact line centre only.

## R4/R5 constructive derivation and exact volume cancellation
ν_α=c/λ_α; v_th=sqrt(2kB T/mH), Δν_D=ν_α v_th/c, a=A21/(4πΔν_D).
`H(a,x)=(a/π)∫ e^(-y²)/[(x-y)²+a²]dy`, `H(a,0)=exp(a²)erfc(a)`.
Normalized Voigt profile `φ_ν(ν) = H(a,x)/(sqrt(π) Δν_D)`, `∫φ_ν dν=1`, x=(ν-ν_α)/Δν_D.
`σ_α,0(T)=π e² f12/(me c) × H(a,0)/(sqrt(π) Δν_D)` = `sqrt(π) e² f12/(me c Δν_D) exp(a²)erfc(a)`.
At T=10^4 K, CAS numerical check σ0≈5.89491753788e-14 cm², a≈0.000471835514368; small discrepancy to 5.88e-14 literature rounding is physically negligible, not a fit.
Let N_H>0 and N_e>0 be *same-cell* original nucleus and electron counts and x_HII the source ionic fraction. Cell opacity coefficients: `κ_α,0=N_H(1-x_HII) g_1 σ_α,0 / V`, `κ_T=N_e σ_T/V`. Thus
`κ_α,0/κ_T = g_1 [(N_H/N_e)(1-x_HII)] [σ_α,0(T)/σ_T]`.
**V cancels identically**, so source nuclear/electron *counts*, without density or geometric path, suffice for the local line-centre ratio. Since 0<=g_1<=1, `0<=κ_α,0/κ_T<=R_max(T,x,N_H,N_e)`, with equality only when all source H I is in the neutral ground state and the stated thermal line profile applies. This is NOT an upper bound if true neutral temperature can be colder than source Tgas or if the assumed profile fails.

For any source-population bounds `N_H∈[N_H^-,N_H^+], N_e∈[N_e^-,N_e^+], x∈[x^-,x^+], T∈[T^-,T^+]`:
`R_saturation^-=(N_H^-/N_e^+)(1-x^+) σ0(T^+)/σT`,
`R_saturation^+=(N_H^+/N_e^-)(1-x^-) σ0(T^-)/σT`.
These are interval inclusion bounds on the **ground-state saturated model**. The physically unknown true ratio is only `[0,R_saturation^+]`; the conditional lower bound is not physical unconditional. Source condition `N_H,N_e>0, 0<x<1` checked for all actual cells.
To justify monotonic sigma0(T): with a∝T^-1/2, `σ0(T)∝aH(a,0)=∫[a²/(a²+y²)]e^(-y²)dy/π`, strictly increasing in a and hence strictly decreasing with T. This gives rigorous endpoint-bracket inclusion, no assumption of an interpolated temperature field.

For source-matched candidate tick161, compute only a **shadow** ratio and `Δln R_saturated` interval from the tick161/tick160 brackets, NEVER advance original accepted history. No interval sum over cells, no volume-weighted mean without original physical volumes.

## R6/R7 checks and hostile counterexamples
Check positivity of all inputs, cell numbering, finite values, every 1-x from original HII bounds, exact 3-lane source bytes, source+paper constants, temperature monotonicity, `R_lower<=R_mid<=R_upper`, invariance under common N_H and N_e scaling (volume and unit cancellation), G1=0 limit gives zero actual opacity, tick161 status HOLD preserved, and no raw source columns or ZIP in public Git. Independent Decimal50 multiplication crosswalk on selected high, low and median cells, numerical σ0 vs Wolfram at 10^4 K; finite-limits T→∞ σ0→0 and x_HII→1 upper ratio→0. Do not confuse ratio with **integrated τ**, actual line photons, escaping flux, rate, true CG polarization, HI neutral excitation population, large-scale Bianchi geometry, or a new original F05 owner admission. Nonzero line-centre opacity is not proof of resonance photons in the *four source ionizing groups*; recombination cascade line emissivity needs a separate real source owner.

## R8/R9/R10 admission and minimal computational handoff
Generate exactly one source-matched **46,080-node paired-input** per-cell record table with tick160 conditional bracket, tick161 unapproved-preview bracket, elementary source-density-free opacity ratio and optional interval `ΔlnR` bracket; model assumptions in headers and summary. Source is the original 46k F05 owner, not BASS193 PR311 and not HK1980 charge exchange. One actual research unit; R1–R10 checkpoint plus C stages as needed. Observe user-scoped drift: if calculations cannot be scientifically interpreted, do not promote anything; stop before another atomic/sky atlas. REI canonical **28/88 REPORTED**, working **33/88 REPORTED**, BASS-CR extension **0/3**, change zero until authoritative source-owner admission. CR-OFF unaffected, PRODUCTION HOLD, NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH. Native child delegation NOT_RUN (user asks no subagent); one same-author hostile review, no fabricated independent-author certificate.
