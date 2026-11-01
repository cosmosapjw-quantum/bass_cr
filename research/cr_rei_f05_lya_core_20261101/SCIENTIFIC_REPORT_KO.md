# BASS-CR → REI F05 | original 46,080-cell Lyα line-centre scattering capacity

2026-11-01, one bounded source-native H/He collision-physics result. THIS IS NOT A COMPLETED BIANCHI LYα TRANSFER, LYα PHOTON EMISSIVITY, OR A NEW REI CANONICAL NODE.

## Original data, exact source identity and limitations

Original owner: `cosmosapjw-quantum/rei_bianchi` PR352 tick161 **nonaccepted preview**, PR354 V2 shadow gate; original accepted tick160/131072. Frozen source-generated 27-column 46,080-cell `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz` SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d` byte-exact across 3 original shape lanes, which contain ONE physical dataset. Original native 26-event source TAR `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b` and accepted tick160 arrays `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01` are REI PR354 **reported historical hashes**, not separately reopened in this BASS-CR run. Parent BASS-CR PR158 HEAD `2ad9c6e1959afb92b876ecb82293040a579b0e81` immutable; theory Git checkpoint `f329db67e28b31b466b71747d7ab80042b212500`.

The source contains ORIGINAL cell-integrated positive nuclei/electron counts, original tick160 HII fraction/temperature brackets and preview tick161 same-state model H/He/T/electron brackets. It does NOT contain exact cell volume, Lyα photon line source, spectral occupation, level-resolved H I(1s), relative ion-neutral velocities, or Bianchi line-of-sight rays. No original private source archive, raw 27-field source CSV or unapproved candidate state arrays are committed.

## Physics, units and interpretation

For source H I neutral fraction `1-xHII`, unknown 1s fraction `g1`, thermal Doppler profile at `T_HI=Tgas`, and line centre `ν=ν_α` in the local rest frame:

`σ_α(ν_α,T)=sqrt(π) e² f12/(me c Δν_D) exp(a²)erfc(a)`, `a=A21/(4πΔν_D)`, `Δν_D=ν_α sqrt(2kBT/mH)/c`.

`κ_α,0/κ_T=g1 (N_H/N_e) (1-xHII) σ_α,0(T)/σ_T`. `N_H` and `N_e` are native **numbers per the same cell**, and the unknown same cell volume cancels exactly. `g1=1` is a conditional *ground-state saturation* model. If 0<=g1<=1, the actual locally evaluated line-centre coefficient under the same neutral temperature/profile assumptions is in [0, R_saturated_upper]. This is not a universal physical upper bound under colder neutral temperatures.

At 10^4 K, `σ_α,0=5.894917537882223e-14 cm²`, `a≈4.718355e-4`; photon E_α=`10.198835887565243 eV`. Positive oscillator strength `f12=0.4162`, A21=6.265e8 s^-1. This standard atomic result agrees with the literature Doppler-core 5.88e-14 cm² to <0.4% due constants and exact Voigt correction. Sources: Dijkstra arXiv:1406.7292 (PASA Lyα review), ART2 MNRAS 424, 884, https://academic.oup.com/mnras/article/424/2/884/1004516 ; Smith et al. 2025 MNRAS 541 179, https://academic.oup.com/mnras/article/541/1/179/8160349. No published full p+H joint charged-particle elastic/CX kernel is imported into this unrelated H(1s) optical line process.

## New source-owned science (ACTUAL native 46,080 physical cells)

**Accepted original tick160, as represented in SHA-locked REI PR352 source artifact:**
- Source H I neutral atom count sum [`6.796615232177277e62`, `6.798828287919838e62`], midpoint `6.797721760048558e62`. The uncertainties are original independent interval widths, not statistical error bars.
- Source-saturated sum of per-atom line-centre cross-sectional areas `A_Lya=ΣN_HI σ0(T)` [`3.333105629290552e49`, `3.334066635117788e49`] cm²; midpoint `3.3335861311854503e49` cm².
- All-free-electron Thomson area `A_T=ΣN_eσ_T` [`3.9650704222569966e42`, `3.965070654578892e42`] cm².
- **Total-summed scattering AREA diagnostic ratio, NOT integrated LoS opacity**, `A_Lya/A_T=[8,406,169.573400812,8,408,593.745026024]`; midpoint `8,407,381.656608673`. Distinct from the unweighted cell median saturation ratio `4,950,301.050520077`; original cells are NOT equal-volume sky realizations.
- Local source-conditional saturated ratio spans interval lower minimum `1.419543614485768e5` to interval upper maximum `8.729566675195652e8` across heterogeneous native cells. These are per-cell coefficients, not per-ray extinctions.

**Only the UNAPPROVED F05 tick161 candidate, not an accepted cosmic epoch:**
- H I neutral atom count midpoint `6.81145158742975e62`; source-bracket [`6.8103381319604735e62`,`6.8125650428990025e62`].
- Combined saturated area ratio [`8,422,089.172354363`, `8,424,533.054448722`], midpoint `8,423,311.109632183`. Comparing independent source-envelope bounds permits a **conditional** ratio increase between +0.16049565% and +0.21845242% on the unapproved native candidate.
- Of the same 46,080 matched physical cells, conditional saturation interval `Δln R` definitely increases in 41,220; decreases in 72; overlaps zero in 4,788. A preview is not actual accepted source-time propagation. The unknown g1(t) could reverse any inferred actual physical Lyα opacity evolution.

## Executed validation and adversarial physics findings

Python 3.12 run: **15/15 normal**, **15/15 Python -O** unit tests PASS locally: input SHA, 46,080 ordered source records, exact 3-lane source byte identity, original 46k H+He electron stoichiometric overlap, positivity, Voigt sigma T monotonicity, mathematically valid bracket, volume/common-count scaling invariance, g1=0 limit, tampered-source failure, 46,080 public derived rows, no raw input leak, deterministic exact byte clean replay, accepted-vs-candidate label preservation. Source H+He electron charge-count midpoint residual max 4.440892098500626e-16. Separate full-source SciPy `scipy.special.wofz` independent numerical implementation gives accepted and shadow summed line scattering areas within **1.1102230246251565e-16 relative** of the primary `exp(a²)erfc(a)` implementation. Wolfram at 10^4 K evaluates σ0=5.894917537882223e-14 cm² and Voigt a=0.000471835514368.

**Hostile findings:** R>10^6 is NOT optical depth, photon number, actual resonant-event frequency or a prediction of trapping. The original ionizing 4-group photon source is NOT the missing Lyα 10.20 eV emission/occupation owner. Original photoionization thresholds ~13.598,24.587,54.418 eV do not supply a distinct bound-bound Lyα source. A recombination/cascade line source could be generated in future, but is NOT derived here; no strong universal no-go is claimed. No path length, velocity gradient, non-LTE 1s fraction, turbulent Doppler width, line redistribution, radiative transfer, CMB polarization or Einstein self-consistency is asserted. The 3 shape lanes share a source and are not independent observations. Independent author blind review NOT_RUN; same-author targeted adversarial checking only; no GitHub CI PASS without workflow evidence.

## Result, DAG and drift watchdog

This is actual derived **original-source H I neutral inventory and Lyα line-centre vs Thomson collision-area budget**, strongly localized to F05 accepted tick160, not another BASS193 A7 surrogate and not an imported REI timestep. It defines a reusable atomic consumer for later source-owned Lyα photon injection. It does NOT authorize BASS-CR CR-ON or a new required central REI node; the decisive next physics is original REI owner F05 [160,161] acceptance plus real Lyα line photon emission and geometry at a common source. Do NOT start another optional nuclear/angle/sky atlas before that.

DAG stage R1-R10 end **REI CENTRAL 28/88 REPORTED, REI working 33/88, CR EXTENSION 0/3, all Δ0**. Stage C1-C10 same. CR-OFF baseline preserved, original source and main unchanged, NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH, PRODUCTION HOLD, AUTO_NEXT_OPTIONAL=false. GitHub Draft PR and local source-free backup are separate from source-owner admission and source-inclusive backup.

### Final live central dependency snapshot
At final cross-repo GitHub readback, REI original F05 theory Draft PR #355 HEAD `98a940ed7d506a55e3089a4de50d024e8d251e5e` was published on immutable PR354 HEAD `6574db945a1b96fa5e0b55923e36781b5db0b03b`. The reported PR355 scope is four ionizing photon groups, three shared H/He absorber moments, and a conditional continuum Volterra remainder; the observed published progress is **R1 theory checkpoint, R2–R10 pending**, not a new accepted full coupled F05 step. REI original tick160/131072 remains the accepted last tick. This optional BASS-CR material-line science must not be used to change REI source admission or to assume a Lyα photon radiation owner.

Further REI live readback: PR355 progressed to R9 original four-group/three-shared-moment continuous residual computation, commit 1a9ce263d73c32d884689d174ac7c5e860e74c97. This does not change F05 tick161 acceptance or BASS-CR physics; re-query REI live before using a latest status claim.
