# BASS-CR → original REI F05: full-source Cen92 versus Scholz–Walters91 cooling closure

Date 2026-11-02 KST. One bounded theory + coding research cycle, parent BASS-CR PR162 at immutable HEAD `7c6c0c4a9d025dc72a80de6bddf2865cb68690b4`. No original REI/source/worker/main mutation, no original physics tolerance relaxation or production/CR switch. Central REI 28/88; working 33/88; BASS-CR extension 0/3 (all delta zero).

## R1–R3 | Original question, physical sources and exact conventions

**Question:** How strongly does original REI F05's *existing* H I collisional-excitation energy loss depend on choice of optically thin atomic-H cooling model across its entire source-native 46,080-cell accepted tick160 material? Does the model difference justify altering an original [160,161] numerical acceptance decision? The deliverable is a quantitative F05 source-specific frozen-physics sensitivity, NOT an additional physical sink or new reionization trajectory.

Original REI source owner: PR356 HEAD `cc1929982948265f6d0b0f699353b3170ccd1792`; officially last accepted F05 tick 160/131072; candidate tick161 NONAUTHORITATIVE. Original 46,080-row private preview/source `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz` SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d` contains accepted tick160 N_H, N_He, x_HII, N_e, T_gas and separately NONAUTHORITATIVE preview increments. Source owner `reduced_interval_rhs.py` SHA256 `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36` contains Cen92/Black81 H excitation loss. Read-only original tensorized inputs and forcing supply exact original proper cell volumes V [cm³] and microtick dt [s]. Previous BASS-CR PR162 2p partial rate is distinct; no 2p+legacy additive cooling.

Original cooling formulas reproduced by Glover (2015), MNRAS 453, 2901, doi:10.1093/mnras/stv1781, Eqs. (34)–(36); original Scholz & Walters (1991) ApJ, doi:10.1086/170587, reports Maxwellian H collision rates and *optically thin hydrogen plasma total excitation cooling fit* 2×10³–10⁸ K. Both models apply to H I–electron collisions, with identical `n_e n_HI` density factors; no claim that their difference equals a resolved 2s or n>2 process. C92 is a phenomenological Ly-alpha-dominated cooling coefficient with multiple historical approximations; SW91 is an alternate atomic cooling fit, not a statistically calibrated uncertainty bar.

Take c explicit only for eventual transport (not used here); k_B=1.380649×10⁻¹⁶ erg K⁻¹; T in kelvin; photon/heat model assumes one locally equilibrated gas temperature T_e=T_gas. Counts N_H,N_He,N_e and proper volume V are original input. The native material thermal reservoir is U=(3/2)k_B T (N_H+N_He+N_e) erg for one ideal monatomic shared-temperature bath.

## R4–R5 | Constructed competing physical closures and algebra

Let `u = ln T` and
`P(u)=213.7913 - 113.9492u +25.06062u² -2.762755u³ +0.1515352u⁴ -0.003290382u⁵`.
`Lambda_C(T)=7.5e-19 exp(-118348/T)/(1+sqrt(T/1e5))` erg cm³ s⁻¹.
`Lambda_SW(T)=1e-20 exp(P(ln T)-118348/T)` erg cm³ s⁻¹.

At each original source cell `K_j=N_H,j(1-x_HII,j) N_e,j/V_j` [cm⁻³], and
`Q_C,j=K_j Lambda_C(T_j)`, `Q_SW,j=K_j Lambda_SW(T_j)` [erg s⁻¹].
`Delta_Q_j=Q_SW,j-Q_C,j` [erg s⁻¹] is a *replacement sensitivity*, not an additive REI RHS.
One-source frozen-time local logarithmic thermal response:
`delta_lnT_j = -dt Delta_Q_j/U_j` (first order with same frozen count, T, proper V and zero response of other source terms).
Time-integrated energy, recombination, cooling, photon trapping, feedback and actual [160,161] rerun are NOT computed. None of the original 14 ledgers is modified. No V1 numerical gate can be passed via physical closure variation.

For positive original source intervals, `Kmin=N_Hlo(1-xhi)N_elo/V`, `Kmax=N_Hhi(1-xlo)N_ehi/V` and `Umin,Umax` arise from positive count/T endpoint products. Since each Lambda is monotone increasing over 2000–67000 K (see R6), bound Q_C and Q_SW separately by Kmin*Lambda(Tlo), Kmax*Lambda(Thi). Signed Delta_Q interval is `[Q_SWlo-Q_Chi, Q_SWhi-Q_Clo]`. Propagate to `delta_lnT` via signed four-corner division by positive U intervals. Source interval bounds are measurement/solver-state envelopes, not atomic uncertainty bars. The SW/Cen spread is a *two-model comparison*, not statistical error.

## R6–R7 | Adversarial physical/numerical checks and first measured results

Proof of monotonic coefficients on 2000–67000 K: `d(ln Lambda_C)/d(ln T)=118348/T - (1/2)r/(1+r)`, `r=sqrt(T/1e5)`, so this exceeds 1.76−0.5>0. For SW, `q=d(ln Lambda_SW)/d(ln T)=P'(ln T)+118348/T`; `dq/d(ln T)=P''(ln T)-118348/T`. On `ln T∈[ln 2000,ln 67000]`, the cubic P'' extrema are at endpoints and critical roots of `P'''(u)=0`; its maximum <0.395. Since 118348/T >1.766, q decreases across the domain and `q(67000)>2`; therefore both coefficients grow throughout the native temperature support. Independent Wolfram evaluated q_SW(66267) ≈2.21097 and SW/Cen ratio at T=(2000,5000,10000,20000,66262) ≈(1.54629,1.08439,0.946407,0.968919,1.62572). Local signed Delta_Q changes sign and cannot be treated as a monotone positive extra sink.

Preliminary source-native Python run (before finalized code/test/repro contracts), 46,080 authentic tick160 cells:
`Sum Q_C =3.228248858135368e39 erg/s`;
`Sum Q_SW=3.4012753342571914e39 erg/s`;
`Q_SW/Q_C-1=0.053597626368174`;
`dt sum(Delta_Q)=8.429588212670994e47 erg`;
`max_j |delta_lnT_j|=7.306574024911232e-6` (frozen-source midpoint);
`0/46080` cells have this first-order model response >2e-4. This is NOT the original V1 discrete local-error estimator: original V1 `2.1245050576368385e-4 > 2e-4` remains historical FAIL; V2 `5.387144148931529e-6` is separate source-scoped discrete gate. Claiming the closure spread closes numerical acceptance would be a category error.

R6 blind-referee counterexamples: (a) at 10k SW<C, so assuming a uniform enhanced cooling gives false sign; (b) both fit descriptions concern Ly-alpha-dominated H excitation, so the PR162 positive phenomenological residual cannot be identified with specific additional atomic processes; (c) optical trapping and secondary cascading are not modeled, so Q is gas excitation energy removal, not observed 10.2-eV photon output; (d) interval positivity does not imply continuous-ODE error certification; (e) integer counts/physical cell volumes in original nonaccepted preview must not be treated as a new epoch.

## R8–R10 | Scientific admissibility and implementation contract

Promote only source-scoped result: `SOURCE_NUMERICALLY_CHECKED` after actual replay, physical model spread over 46k. Pending: true 26-event time-stage and 14-ledger parity, original versioned worker contract, and canonical t161 gate; no solver/operator mutation, no silent closure replacement or bias toward more optional atlases. This 46k full-domain comparison is one bounded diagnostic and must STOP optional H cooling model surveys afterward.

Code contract: source SHA and owner/legacy RHS code SHA locked; original `native_caseb_lya.native()` read-only geometry; original `tick160_*` only for physics, preview deltaln used *only* as labeled nonauthoritative contrast if needed. Public output derived per-source-cell power/model-response rows with no raw T, x, N, V, preview delta; result JSON with physical sums and finite interval diagnostics; real 46,080 source-native rows. Unit, sign, domain/clock guards, independent Wolfram and Decimal coefficient checks, cold deterministic output SHA readback, no original privacy leak, local source-free backup and Git Draft on separate branch stacked PR162. No CR-ON claim; central 28/88, working 33/88, BASS-CR extension 0/3 (all delta0). No native subagent available: serial same-author audit only.
