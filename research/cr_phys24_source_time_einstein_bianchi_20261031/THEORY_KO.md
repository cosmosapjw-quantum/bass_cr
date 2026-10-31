# PHYS24: PHYS15 source-clock to conditional Einstein–Bianchi I polarized Lyα transport

Date: 2026-10-31, signature `(-,+,+,+)`, SI units, `c`, `G`, `h`, `k_B` retained. Scientific status: **derived mathematical background + numerically checked conditional radiative calculation**, not source-compatible Einstein–Boltzmann closure.

## Original atom-source and deliberately conditional angular/time closure

From the unchanged PHYS15 27-row original `TIME_LYA_2P_RADIATION_LEDGER.csv`, choose the two locked source birth policies (earliest, latest) and extract cumulative `N_b(t_j)` for 9 source proper-clock epochs `t_j=j×1.25×10^9 s`, `j=0,...,8`. Define `ΔN_{b,j}=N_b(t_{j+1})−N_b(t_j)>=0`, `j=0,...,7`. The PHYS15 emitted Lyα lower bound and new-photon upper bound coincide to tabulated precision, with residual 2p occupation at the final time bounded by ~2.21×10^-49 m^-3 for earliest birth, so a first-emission-in-bin approximation can carry the locked source count. **This is not a reconstructed actual per-photon emission-time distribution.** In particular the source's internal event ages and individual photon direction vectors remain absent.

Each PHYS15 interval inherits the original PHYS22 10 source-integrated conditional E1 source coherencies, five angular scenarios × two Bray anchors, with `χ_{b,scenario,anchor}(t)` provisionally **constant across bins** at the exact source-weighted PHYS22 aggregate value; this independence of time and angular structure is NOT source-proven. Use three explicit `within-bin emission time` closures `t_em=t_j`, `(t_j+t_{j+1})/2`, `t_{j+1}`. The final-bin `end` closure injects at observation time and produces zero absorption on that bin, an intentionally extreme boundary witness, **not a posterior estimate**.

## Conditional dynamical geometry: exact Einstein dust solution

For a homogeneous diagonal Bianchi-I line element

\[
 ds^2=-c^2dt^2+\sum_{i=1}^3 a_i^2(t)(dx^i)^2,\quad
 a_i(t)=V^{1/3}(t)e^{\beta_i(t)},\quad \sum_i \beta_i=0,\quad V=\prod_i a_i,
\]

assume geodesic comoving pressureless homogeneous dust, no cosmological constant, isotropic dust stress `T^μ_ν=diag(-ρc²,0,0,0)` in the comoving orthonormal frame. Define the observer-reference dust density `ρ_o=m_H×138.6 m^-3` (a **conditional cosmological identification**, not a provenance assertion that the original 100 K HI static gas is the true total source of curvature), `V(t_o)=1`, `β_i(t_o)=0`, `t_o=10^10 s`, `dot β_i=C_i/V`, `∑C_i=0`. The Einstein 00 constraint and dust conservation give

\[
3\bar H^2=8\pi G\rho+\tfrac12\sum_i(\dot\beta_i)^2,\quad
 \rho=\rho_o/V,\quad
 \dot V^{\,2}=AV+B,\quad A=24\pi G\rho_o,\quad B=\tfrac32\sum_i C_i^2.
\]

The positive-expansion branch is exactly

\[
V(t)=1+\sqrt{A+B}(t-t_o)+\tfrac A4(t-t_o)^2,\qquad
\beta_i(t)=-C_i\int_{t}^{t_o}{du\over V(u)}.
\]

Differentiating this expression gives `dot V²=AV+B`, `ddot V=A/2`, `dot β_i=C_i/V`, and all three independent pressureless spatial Einstein equations. The background uses declared shear constants (s^-1): `flrw_dust=(0,0,0)`, `axisymmetric_dust=(2,2,-4)×10^-16`, `triaxial_dust=(3,-3,0)×10^-16`. The dust test background is an exact independent Einstein IVP, but the PHYS15 emitted-photon source is an **externally prescribed test emissivity**, not self-consistent Einstein matter/radiation or an original CR source-compatible metric. Local tests include the full 00 constraint and pressurefree spatial equations, not merely fitted `Δβ`.

## Geodesic, normalized angular Jacobian and Stokes

The conserved spatial covariant null momenta satisfy `p_i=(hν/c) a_i n_i`, with observation scale factors `a_i(t_o)=1`. For a final observed unit direction `n_o`, define `z(t,n_o)=√Σ_i[n_{o,i}/a_i(t)]²` and `r(t_e,n_o)=ν_o/ν_e=1/z(t_e,n_o)`. Then

\[
n_{e,i}={n_{o,i}\over a_i(t_e)z(t_e,n_o)},\qquad
{d\Omega_e\over d\Omega_o}={r^3\over V(t_e)}=r_s^3,
\quad r_s=r/V(t_e)^{1/3}.
\]

The `V^{-1}` factor in the angular Jacobian is crucial when mean expansion is not suppressed. The source photon count is measured per **fixed reference comoving volume** normalized to its observation volume `V(t_o)=1`, not physical number density at the emission epoch. Thus `∫dΩ_o I_o^{(bin)}=ΔN_bin` for collisionless source counts; no extra artificial `V^{-1}` density factor should be added to that reference count. The polarimetric source tensor is the PHYS22 positive semidefinite orbital matrix `ρ_3=(1−χ)I_3/3+χ aa^T`. Project it onto the emission screen, transport each transverse basis by the Levi-Civita equation in the comoving orthonormal frame, and rotate the coherency:

\[
\dot n_i=(\sum_jH_j n_j^2-H_i)n_i,\qquad
\dot f_i=n_i\sum_j H_j n_j f_j,\qquad
J_o^{(bin)}=r_s^3 R J_e^{(bin)}R^T.
\]

With `H_i=dot a_i/a_i` and `f⋅n=0`, the transport preserves transverse norm and positivity. The source Stokes `V=0` stays zero in collisionless transport and an isotropic unpolarized source stays Q=U=V=0 even though the sky intensity can become anisotropic by shear focusing. These expressions are the Bianchi-I specialization consistent with Pontzen–Challinor photon/screen transfer. **Do not insert external BASS KM2N/KM2O photon arrays.**

## Spectral transfer and first HI interaction (no redistribution)

Use the original PHYS15/NIST atomic inputs `E21=10.1988 eV`, `A21=6.2649×10^8 s^-1`, `f=0.41641`, `T_HI=100 K`. Define `ν0=E21/h`, `Δν_D=ν0√(2 k_B T_HI/m_H)/c`, `a=A21/(4πΔν_D)` and normalized source Voigt `Φ(x)=Re[w(x+ia)]/√π` on x∈R. For each interval and ray,

\[
x_e={x_o-(r-1)\nu_0/\Delta\nu_D\over r},\quad
S_o(x_o)=\sum_j S^{(j)}_{o,\rm integrated}{\Phi(x_e)\over r}.
\]

This spectral profile is a **100 K recoil-free conditional line-source closure**, not the original PHYS16 recoil spectrum. The first-interaction Lyα optical depth at a fixed observed frequency (gas comoving in the conditional dust background) is

\[
\tau_j(x_o,n_o)=c\int_{t_{em,j}}^{t_o}{138.6\,dt\over V(t)}\;\sigma_{Ly\alpha}\big[x_t\big],\quad
x_t=\big[z(t,n_o)-1\big]{\nu_0\over\Delta\nu_D}+z(t,n_o)x_o,
\]

\[
\sigma_{Ly\alpha}(x)={e^2 f\over4\varepsilon_0m_ec\sqrt\pi\Delta\nu_D}\operatorname{Re}w(x+ia),\quad
S_{\rm unscattered}(x_o)=\sum_j S_{o}^{(j)}(x_o)e^{-\tau_j(x_o,n_o)}.
\]

The difference `S_free−S_unscattered` is **photons removed from the unscattered beam by a first HI interaction**, not emitted or redistributed photons, not escaped Lyα flux, and not a physical RII Stokes source. The angle/frequency-dependent resonant redistribution matrix and its detailed balance remain open (Hummer 1962). For optical depth, the 20-node Gauss–Legendre result is explicitly compared with independent 64-node quadrature.

## Scope, limits and provenance

- Original 2066 He-origin source events preserved by Git blob `d7034188ca5a02dc37db24aaf8f7d550624567bd`; no source event, rate, E1 conditional prior or archive bytes changed.
- PHYS15 original ZIP SHA-256 `48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316` and PHYS23 ZIP SHA-256 `22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111` restored/readback during this run; PHYS15/22 input CSV/JSON byte locked in `phys24.py`.
- The χ(t) conditional independence, within-bin timing, emitter Voigt/recoil exclusion, 100K HI gas and Einstein dust source material identity are **not** established by the original source. The dust geometry does not prove global He exclusivity, physical K, dynamically coupled Einstein–Boltzmann, RII, observational Lyα posterior or source uniqueness.
- Original-source FLRW branch includes nontrivial mean expansion, so it is not literally the PHYS23 **fixed mean-a** zero-shear regression except in the formal `Gρ_o→0` limit. For same `ρ_o` it is the correct zero-shear Einstein dust control.

Literature: Pontzen & Challinor, MNRAS 380, 1387 (2007), DOI 10.1111/j.1365-2966.2007.12221.x; Khalatnikov & Kamenshchik, Phys Lett B 553, 119 (2003), arXiv:gr-qc/0301022; Wiese & Fuhr, JPCRD 38, 565 (2009), DOI 10.1063/1.3077727; Hummer, MNRAS 125, 21 (1962), DOI 10.1093/mnras/125.1.21.
