# BASS-CR optional REI-BASS193 resonant H+–H angular momentum transfer: conditional first-moment calculation

Status (2026-11-01): **SOURCE_MATCHED_EXPLORATORY_PUBLISHED_ANGULAR_MOMENT_FIT**. New 192-row source-conditioned linear-response **diagnostic**, not original quantum DCS reconstruction, not elastic+CX full operator, not REI native tilted Bianchi IVP. The data are astrophysical-source conditioned rather than new observations or source-evolved ion-neutral states.

## 1. Original authority and no-mutation boundary

- Owner: cosmosapjw-quantum/bass_cr. Immutable source-parent PR #154 HEAD 88b15fe3d6a0457d8bf63eba5b815da99d2e39b1 (draft). Its parent PR #153 HEAD ac2ed86c8b59fe7c7b5e78b0716c6c4d4677072e is an independent CR=OFF Thomson consumer.
- Original REI source PR #311 HEAD 63052797e382b438ef375e8389f539118a7e2a0c, private original ZIP size 1,234,543 bytes SHA256 4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52, 23 members CRC clean. Original ZIP never goes in Git or public archive.
- PR154 original derived 192-row CSV SHA256 afb5cb0fab472421026254e66e35c37fb01e86af97286e756845f9035908eb99, independently recomputed from exact source and byte-equal to PR154 file.
- REI central DAG 28/88 REPORTED, delta 0; working 33/88 REPORTED; BASS-CR extension 0/3, delta 0. REI unchanged, no merge, no production, no force push, no auto-next.

## 2. Publications and angular conventions

- Schultz et al. (2016) *J. Phys. B* 49, 084004, https://doi.org/10.1088/0953-4075/49/8/084004, original 1301 CM energies 10^-4–10^4 eV with integral and differential elastic/CX cross sections. Raw original DCS bytes **NOT RETRIEVED**.
- Krstic and Schultz (1999) *Phys. Rev. A* 60, 2118, https://doi.org/10.1103/PhysRevA.60.2118, nuclear indistinguishability and direct/exchange convention.
- Titova, Izmodenov & Korolkov (2025) PASA, https://www.cambridge.org/core/journals/publications-of-the-astronomical-society-of-australia/article/effects-of-angular-scattering-and-hp-hh-collisions-on-the-properties-of-interstellar-atoms-in-the-heliosphere/295E867AC1038B5648D5780349B5E6E5:
  - Their Eq. (A4) total CX event fit sigma_cx(g)=[A-B ln(g/(1 cm/s))]^2, A=1.87618291e-7 cm, B=8.28949260e-9 cm.
  - Appendix A, Eq. (A7), heading **Model 6 charge exchange**, states authors fit *one half of the CX momentum-transfer cross section*, calling this half a Model-6 proxy sigma_tot,Hp. Therefore sigma_mt,cx^A7(g)=2 F_A7(g) with F_A7(g)=[a-b ln(g/(1 cm/s))]^2 [1-exp(-c/(g/[cm/s]))]^d, separately parametrized at g<=16 km/s and >16 km/s. Coefficients in angular_mt.py are verbatim from A7. Crucially this is NOT the original measured/primary DCS.
- UGA 2023 updated elastic DCS listing https://sites.physast.uga.edu/amdbs/elastic/index-h%2B%2Bh-2023.html; original DCS download attempts timed out. Raw elastic and CX DCS **NOT ACQUIRED**. These are two separate fit sources and cannot automatically be combined into an exact channel kernel.

## 3. Constructive derivation

Nonrelativistic resonant H+(p)+H(1s) collision in original source local inertial frame, signature (-,+,+,+) when embedded in spacetime; retain physical m_p, m_H, k_B, and c externally. Ion and neutral are independent Maxwellians with same saved source T and small relative drift U=u_i-u_n, |U| << a, a^2=2 k_B T (1/m_p+1/m_H), mu=m_p m_H/(m_p+m_H). No finite tilt or differential species temperatures source verified.

Charge-labelled outgoing ion CM angle chi_ch defines sigma_mt,channel(g)=integral (1-cos chi_ch) d sigma_channel/dOmega_ch dOmega_ch. In resonant exchange the charged ion label follows previously neutral target nucleus; cos chi_ch=-cos chi_nuclear, so the nuclear-labelled CX weight is (1+cos chi_nuclear), unlike elastic (1-cos chi_nuclear). A blind use of elastic convention for CX is wrong. Exactly the original PR154 convention addendum.

Relative Gaussian f0(g)=pi^(-3/2) a^(-3) exp(-g^2/a^2), drift distribution f(g;U)=f0(g-U). Linearization in U gives force densities
R_i = -R_n = -mu n_i n_n K_mt(T) U + O(|U|^3)
K_mt(T) = 2/(3a^2) <sigma_mt(g) g^3>_0
        = 8a/(3 sqrt(pi)) integral_0^infty x^5 exp(-x^2) sigma_mt(a x) dx.
Restrict integral to g in [3,200] km/s; split A7 at 16 km/s. Units: sigma cm^2, K cm^3/s, gamma=mu n_i n_n K in g cm^-3 s^-1, nu_i=(mu/m_p)n_n K, nu_n=(mu/m_H)n_i K, nu_rel=nu_i+nu_n.
For constant sigma, analytic <sigma g>=2 sigma a/sqrt(pi), K=8 sigma a/(3 sqrt(pi)), K/<sigma g>=4/3, checked by Wolfram and independent tests. For isotropic DCS, sigma_mt=sigma_tot; for outgoing charge-angle delta chi=pi, sigma_mt,cx=2sigma_tot,cx. Synthetic angular quadrature confirms nuclear-to-charge relabel.

Direct H-ionization, HII, electron and atomic binding-energy reaction source are exactly zero under resonant label exchange. Frictional heating and detailed two-fluid internal energy redistribution are NOT computed. At exactly U=0 drag vector is zero although relaxation coefficient is nonzero.

## 4. Computed 192-row original-source-matched diagnostics

The output CSV has same 192 proper-time source intervals, z and saved T=100–12000 K, n_i/n_n reconstructed with source lock. New K_mt^A7, K_mt^pi/A4, source event k^A4, gamma, per-fluid nu, nu_rel/H_eff, zero direct chemical sources and geometric support flags.

- K_mt^A7 in [1.2254630043e-9, 2.2088780392e-8] cm^3/s.
- K_mt^A7/K_mt^pi,A4 in [0.6956458115, 0.9113510440], median 0.8555610842. A conditional estimate of angular-moment sensitivity **not primary DCS prediction**.
- Max frozen-end nu_rel/H_eff = 30821.6708 at interval 103, z=6.319103. No time-evolved ion/neutral IVP and no Bianchi-frame interpretation admitted.
- 114/192 have >=95% constant-sigma Maxwell-drag geometric speed weight in window and 60/192 have <50%. This is *not* actual sigma-weighted integral fraction, not a physical confidence interval.
- Published separate A7 and A4 fit consistency audit: at g approximately 69.0643 km/s sigma_mt^A7 > 2 sigma_cx^A4, 127/501 logarithmic speed samples violate, maximum violation 1.033% of this fit-bound; this **does not show exact quantum DCS violation**. At T=12000 K the above-threshold speed tail contributes 0.0440% of window A7 drag; integral excess relative to window A7 drag ~7.94e-7. The A7 piecewise join has a -2.92% jump immediately above 16 km/s. We report without clipping, renormalizing or pretending the fits were co-estimated.
- Source CSV SHA256 f47f1379503dba93f1583a8cb2b2cdb61fa856f9e0e485140d62fce329600f03; JSON SHA256 f7a3aad3548b836111da6e2a1488cbab9025627e5d1eafa08a83be681ad4db64.

## 5. Verification and drift watchdog

18/18 focused unittest regular plus 18/18 optimized Python tests pass on the authorized remote PC, including source SHA/192-row replay byte identity, independent Gauss-Legendre quadrature, constant-sigma 4/3 limit, charge/nuclear angular reversal, exact opposite forces, positive conditional gamma, chemistry invariants, tamper fails closed, reproducible CSV/JSON. Original PR154 derived CSV byte-exact original-source reproduction. Distinct-author blind R06/C09 **NOT_RUN**, but one local self-adversarial test pass was executed. Raw DCS physical verification and code CI are not claimed.

Watchdog: OBJECT = source-owned REI IGM evolving physics and observables; DEFECT = ongoing CR microphysics side screens risk consuming loops without source-evolved IGM progress; IMPACT = zero central DAG progress; MINIMAL REPAIR = generate one source-matched transport coefficient diagnostic, classify raw DCS missing accurately, publish as optional source-free BASS-CR draft, stop. No promotion of BASS-CR 0/3 or REI 28/88. No REI mutation. CR-OFF still works independently.

## 6. Scope boundary / next only

DONE within fit scope: a newly calculated 192-row momentum-drag susceptibility and explicit angular distinction. NOT DONE: primary DCS verified, elastic+CX combined angular kernel, low-energy identical-nucleus nuclear spin treatment, separately sourced species drift/temp, Bianchi finite tilt, actual REI coupled IVP/observables, central DAG milestone. Current correct status **HOLD**, do not auto-next.

Next candidate only: obtain and byte-verify original published charge-labelled CX and elastic DCS (UGA 2016/2023 or author), correct CM angle, nuclear-spin symmetry, integrated cross-section and transport moment; use them to build a joint channel kernel with source-matched ion-neutral f, finite Bianchi tilt/clock before an optional REI RUX13 CR-ON import. Actual core REI source IVP continues independently.
