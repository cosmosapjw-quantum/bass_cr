# BASS-CR PHYS12 | 실제 H(1s) 전자충돌 미시 계수와 유한시간 2차 사건 상한

## 원본과 식 (derived / numerically checked)

Original PHYS11 source 7,135,159 B SHA256 `afedf6ac708e17e847d086625af47c0cf0a902b8ec2f1c168daf16b198ef050a`, PR136 HEAD `d7de61661b718f9968acd4e696510603968e18e7`. Original H/He RR photon atoms 6400 and four birth bins, original proper s 0–1e10, H/He fixed neutral 138.6/11.427127659574467 m^-3, T_gas=100 K. Original source He->HI primary electron E_e=E_gamma−13.60 eV, max 20.99 eV. No foreign BASS193, Li, HD, electron transport source spliced.

Atomic H electron-impact fit: Yong-Ki Kim (1992) Eq.(2), Table 1, DOI 10.6028/jres.097.032, a *fit to* experimental Shah, Elliott & Gilbody (1987) DOI 10.1088/0022-3700/20/14/022, not raw experimental points. Let x=E_e/(13.61 eV), and use C=+5.867. For x>1

σ_H(E_e)=10^-20 m² /x · [0.7576 ln x + (-5.521 ln x +5.867 (x−1))/(x+2.948)], otherwise σ=0.

n_H=138.6 m^-3, v=sqrt(2 E_e e_J/m_e), ν0=n_H σ_H v. At E_e=20.99 eV, σ=3.268196090913e-21 m², ν0=1.230844678544e-12 s^-1, λ=71.54480730394357 pc. This is a *microscopic stationary-target collision coefficient*, not the electron trajectory or the program physical energy cap K.

Given first He-origin photon with first HI hazard k_gammaH, total competing photon hazard k_gamma, and proper birth time s, the model-conditioned two-event upper is

P2^upper(T|s,E_gamma)=∫_0^(T−s) k_gammaH exp(−k_gamma u)[1−exp(−ν0(E_e)(T−s−u))] du.

Proof: if the primary electron has non-increasing kinetic energy and no external acceleration, with the stationary-gas microscopic model ν(E(t))≤ν(E0) in the relevant interval, then the conditional survival exp(−∫ν dt)≥exp(−ν0 Δt). Integrating over source-owned first photon absorption time gives the expression. No assumptions about a specific stopping trajectory are used. However, the assumptions are not the full 100 K thermal target velocity distribution; the global physical event rate is not certified.

### Source-derived physical numerical results

Actual CSV rows **13,173**: atom 12,800, time-channel 108, time-total 27, original energy bins 184, uniform neutral gradient 54. Parent first-absorption count at 1e10 s earliest matches exactly 1.7193913666048540e-26 m^-3 and original PHYS11 kinematic H capacity 1.2886312586089971e-28 m^-3. New finite-horizon upper 1.3345858733024866e-31 m^-3, ratio to energy capacity 1.035661570668e-03; latest 3.9701495974077453e-32 m^-3, ratio 8.363116410385e-04. Mean-free-path diagnostic at max energy λ=71.54 pc, not measured transport distance.

### Authority and adversarial constraints

- Physical threshold in PHYS11 source is 13.60 eV; empirical fit uses 13.61 eV. Original 2,389 kinematically eligible He-origin energy atoms; 2,386 with strictly positive Kim fit. **The three zero-fit atoms are NOT physically forbidden.**
- Shah1987 measured cross sections start at 14.6 eV. Of 2,386 Kim positive atom energies, 320 are below 14.6 eV, so the Kim model is an empirical extrapolation there.
- Bray et al. (2018), Phys Rev Lett 121 203401 DOI 10.1103/PhysRevLett.121.203401 discusses the neutral-atom Wannier near-threshold exponent ≈1.127. Kim's fit is linear asymptotically at its own threshold; neither source establishes a universal uncertainty envelope for the 320 extrapolated atoms.
- A 100 K neutral population may have thermal velocities, and accelerated primary electrons, electron-neutral scattering, diffusion, stopping and secondary energy sharing are not provided. The result is conditional, not actual event counts or a universal upper bound for arbitrary trajectories.
- R06/C09 different-author NOT_RUN; same-author blind-style scalar QUADPACK vs independently coded formula max relative difference 3.891e-16 over 32 cases, finite density log gradient max relative FD difference 2.614e-08.

### Scientific admission

Current Central 28/88 Δ0; Extension 0/3 Δ0; PHYS12 scoped auxiliary **1/1 CONDITIONAL REVIEW_HOLD**. Physical `K[eV]`, globally exclusive He kernel, common evolving neutral+radiation+clock+geometry, actual particle trajectories/stopping, native25, L4 and production remain UNBOUND/HOLD. No new central node promoted. No merge/force push/main modifications.
