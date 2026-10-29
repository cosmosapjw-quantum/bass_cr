# CR_PHYS02_RR_IONIZING_PHOTON_V1 | source-bound 물리 이론

**Source authority:** BASS-CR PR110 science `2eed7ef835c55ee17e4ce96e0eda7fe8d82dc47c`, documents `616b166fa0108ca35defece3f8c9d99fc79895cb`, SOURCE ZIP SHA256 `5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58`. **New add-only child base:** PR124 `a6b49b352fed31587955d55b1cad30c0b55a81eb`. Actual PR110 atomwise `ARRAYS.npz` SHA256 `2c3624e4ca6d087436f79360497e75b0c84fb2c8ea6b83bb855a9a0cd0005c1d`, `RESULT.json` SHA256 `ae8452f25958c47349d313926ef14e7ab7d78691ba6bb3b8395dc399aa49b0ce`. PHYS02 original-source JSON SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf` and distinct original fullBED NPZ *lineage* SHA256 `7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc` are **different objects**.

## 1. Question and frozen scope

What time- and photon-energy-resolved **emission source** is implied by the genuine saved low-born PHYS02 H1/He4 100 K Coulomb/ground radiative recombination calculation? What photon counts *can energetically* ionize H I / He I? What is the formal signed, RR-only Thomson-column response? Unlike previous Ferrers matching auxiliaries, this product retains a physical source/target model and computes source-derived physical observable data. It is **not new original RR physics**, not an experimental measurement, not photons transported/absorbed, not cosmological CMB optical depth, and not an exclusive correlated He double-ionization kernel.

Preserve gas-rest scalar nonrelativistic isotropic ensemble, fixed proper volume densities, T_bath=100 K, H1/He4 only, direct low-born `direct_0p1_10` support 0.1–10 eV, four quarter bins on 0≤t≤10^10 proper seconds. Source injection q_a(t)=t A_a, and previously calculated 3200 electron energy atoms E_a and channel RR event measure w_{c,j,a}≥0 per disjoint time bin j. Capture transitions HII→HI(1s), HeII(1s)→HeI(1s² singlet), spontaneous ground only. Verner/Milne conditional source fit with threshold energies I_H=13.60 eV, I_He=24.59 eV, stationary heavy target and zero recoil. n_H=140m⁻³, n_He=1085/94m⁻³, n_e=2849/1880m⁻³, n_b=8750/47m⁻³. This is a **prescribed model**, not a coupled evolving chemistry/thermal solution.

## 2. Source transformation (derived from actual stored event measure)

For each channel c∈{H,He} and disjoint proper-time bin j, define the emitted **number measure** in photon energy ε (eV):

  dN_{γ,c,j}(ε)/dV = Σ_{a=1}^{3200} w_{c,j,a} δ(ε-[E_a+I_c]) dε.

Its mean source (emissivity in photon number per volume, time and eV) for Δt_j>0 is

  q_{γ,c,j}(ε) = Σ_a (w_{c,j,a}/Δt_j) δ(ε-[E_a+I_c]).

Photon frequency ν(ε) = ε·eV_J/h and spectral density dN/dν=(h/eV_J) dN/dε. Integrated photon count and retained radiation energy are

  N_{c,j}=Σ_a w_{c,j,a},
  U_{γ,c,j}=eV_J Σ_a(E_a+I_c)w_{c,j,a}.

Original event ledger identity:

  U_{γ,c,j}^{(eV)} = K_{c,j}^{(eV)} + I_c N_{c,j},
  ΔU_fast = -K, ΔU_binding=-I_cN, ΔU_photon=K+I_c N.

Every original ground RR event yields **one model photon**. For ionization threshold I_s, `G_s=Σ_{c,j,a}w_{c,j,a} 1(E_a+I_c>=I_s)` counts only photons energetically eligible for direct photoionization. It is **not an actual absorption count, net ionizations or transported flux**. In this low-electron-energy domain, all photons are above HI threshold, only He channel photons exceed HeI threshold, none exceed HeII threshold.

A 0.5 eV histogram (13.0 to 36.0 eV, 46 bins) with an explicit four-quarter time axis is a *lossy presentation* of the authoritative 3200×4×2 atomwise event measure; full atomwise arrays remain in output. Time-bin means are ΔN/Δt, **not instantaneous endpoint rates**.

## 3. Formal proper-time Thomson-column response (derived conditional diagnostic)

Let C(t)=Σ_c C_c(t) be the cumulative RR capture density since t=0. As a **linearized RR-only stoichiometric response around the frozen inventory**, δn_e(t)=-C(t), ignoring ion-target depletion, secondary injection, ionization and expansion. This does not turn the prescribed frozen background into a self-consistent plasma history. For proper slab length from time 0 to T:

  δτ_T = c σ_T ∫_0^T δn_e(t) dt = -c σ_T ∫_0^T C(t) dt.

Since stored captures are nonnegative, C(t) is nondecreasing and for j=1,..,4, Δt_j=t_j-t_{j-1}>0,

  -cσ_T Σ_j Δt_j C(t_j) ≤ δτ_T ≤ -cσ_T Σ_j Δt_j C(t_{j-1}).

No assumption of linear C(t) between endpoints is required. This mathematical enclosure assumes the underlying exact frozen discrete model and endpoints; binary64 rounding is not interval-certified. NIST CODATA2022 σ_T=6.6524587051×10^-29m², c=299792458m/s. The baseline homogeneous slab τ0=cσ_T n_e T is a **different object** from cosmological ionization optical depth τ(z) and should not be inserted into CMB likelihood or L4. In this source, |δn_e| is far below binary64 ulp at n_e≈1.5/m³, so calculate δτ directly from cumulative captures without subtracting two nearly equal n_e values.

## 4. Limits, admitted claims, and literature

- **derived / numerically checked / implementation-verified scoped:** frequency/energy/time emission source, energetic ionization threshold classes, original event-energy identity, finite monotone slab bounds.
- **original source, not new:** original PR110 positive finite 3200-atom Coulomb+ground RR event arrays and conditionally source-qualified 100 K physical model; rerunning prior RR ODE was unnecessary and not performed.
- **held:** actual ionizing absorption probability, Case A/B radiation feedback, photon propagation/escape, dynamic ion abundance and temperature, inclusive/full-electron source, absolute worldtube volume, full-coupled native25, real exclusive He double event kernel/physical K, L4, production, observational claims.

Related literature: Nebrin, *Case A or Case B?*, RNAAS 7 (2023), DOI 10.3847/2515-5172/acd37a, emphasizes optical-thickness/transport dependence of ground RR photon absorption; NIST CODATA 2022 values https://physics.nist.gov/cuu/pdf/wall_2022.pdf. Ciappina et al. PRA 77 062706 (2008), DOI 10.1103/PhysRevA.77.062706, describes **6 MeV proton** helium double-ionization correlations, not a 1–4 MeV tabulated source-qualified exclusive event kernel for this PHYS02 model. Existing Verner PI / Milne fit source details and validity are inherited from pinned PR110, not requalified by citing an unrelated article.

**Scientific DAG:** canonical 28/88 unchanged; this adds a scoped source-emission child 1/1 pending distinct-author R6/C9. Central advancement requires an actual owner-qualified acceptance of a named original node, not adding auxiliary nodes by arithmetic.
