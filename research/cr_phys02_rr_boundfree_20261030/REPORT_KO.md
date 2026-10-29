# BASS-CR | CR_PHYS02_RR_BOUNDFREE_ENVELOPE_V1 | 물리 데이터 연구 보고서

2026-10-30 KST · PR125의 frozen physical H/He ground RR photon source를 그대로 사용하는 조건부 연구 결과. 소스에 실제 존재하지 않는 시간 내 출생시각, 우주론적 전파 경로, heating/deposition, 물리 He double-event kernel을 만들어내지 않는다.

## 1. Frozen inputs와 근거

- GitHub PR125 원 HEAD: `acf34ccb4229c002d9ad80a06a6d88cefb66d2fd` (Draft). Source ZIP 5,856,755 B SHA256 `8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e`.
- 봉인된 `PHOTON_ATOMWISE.npz` SHA256 `e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f`; 4 time bins × 3200 low-born H/He photon energy atoms. Source source summary JSON SHA256 `4a8cafd27bb78086842fc213fec6cc1f61dae0e62d3939c23be6df00fe32a538`.
- Source-in-source immutable PR110 ZIP SHA256 `5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58`. Inventory read from same source: n_HI=138.6 m^-3, n_HeI=11.427127659574467 m^-3 (100 K frozen proper gas-rest bath).
- Verner, Ferland, Korista & Yakovlev (1996), ApJ 465 487 DOI 10.1086/177435; author original `photo.dat` H I (Z1,N1) and He I (Z2,N2) lines, exact printed parameters in `source/VERNER1996_HI_HEI_TABLE1.dat`, SHA256 `a9ae2f7e7393de6f9ad89376cf5dd4be84da60cb3dadde3be37a4d3bd5989492`. Formula verified against arXiv astro-ph/9601009 v2 p4 Eq.(1).
- Verner σ is a fitted atomic cross-section, not a new measurement by this work. Conversion 1 Mb=10^-22 m². At 20 eV σ_HI=2.21110298403921×10^-22 m², σ_HeI=0; at 30 eV σ_HI=7.03485586735790×10^-23 m², σ_HeI=5.36119879909405×10^-22 m² (Wolfram).

## 2. Theory R1–R10

α_a(E)=n_aσ_a(E), α=Σ_aα_a [m^-1]. In a *prescribed, homogeneous and time-independent neutral gas* with straight-line photons at c, first absorption by target a, conditional on emission at t and observation T=10^10 s, is P_a(E,t) = α_a/α · [1−exp(−αc(T−t))], or zero if α=0. The original source supplies only bin-integrated birth weights w_{qji}≥0 for t_j≤t≤t_{j+1}; without choosing an unsupported birth-time distribution, monotonicity gives source-sharp bounds

A^-_{qja}=Σ_i w_{qji} P_a(E_{qi},t_{j+1}) ≤ A_{qja} ≤ A^+_{qja}=Σ_i w_{qji}P_a(E_{qi},t_j).

Derivative dP_a/dt=−cα_a exp[−αc(T−t)]≤0. Original count, target branching, energy thresholds/units, positivity, survival and algebraic U_abs=U_ion+U_excess preserved, with U_excess the **available initial photoelectron energy**, not deposited heat. No source birth time within bin was inferred. Two output tiers: local source-conditional α(E), and extra-assumption finite-horizon ballistic absorption bounds.

## 3. Physical-data results (fresh from this run)

| Quantity | Lower | Upper | Unit |
|---|---:|---:|---|
| Source emitted photons (fixed) | 2.729441124610644e-25 | same | m^-3 |
| First absorption, all target channels | 6.536559924836170e-27 | 1.719391366604854e-26 | m^-3 |
| Absorbed fraction of source emission | 0.023948345563850965 | 0.06299426469036315 | 1 |
| H RR photon → H I | 6.329531465952673e-27 | 1.6643607970697675e-26 | m^-3 |
| H RR photon → He I | 0 | 0 | m^-3 |
| He RR photon → H I | 1.3302203758498104e-28 | 3.533782756159203e-28 | m^-3 |
| He RR photon → He I | 7.400642129851678e-29 | 1.9692741973494655e-28 | m^-3 |
| Absorbed photon energy | 1.6701889106530617e-44 | 4.4048352888507276e-44 | J m^-3 |
| Threshold ionization energy | 1.4373213990014618e-44 | 3.7811602191980576e-44 | J m^-3 |
| Available photoelectron initial kinetic energy | 2.3286751165159964e-45 | 6.236750696526702e-45 | J m^-3 |

Machine-readable outputs: `results/BOUND_FREE_ATOMWISE.npz` (including original 4×3200 atom counts/energies), `BOUND_FREE_TIME_CHANNEL_TARGET.csv` 16 target-by-time-channel records, `BOUND_FREE_OPACITY_SAMPLES.csv`, `results/BOUND_FREE_RESULT.json`, independently checked `results/INDEPENDENT_MPMATH65.json`, two physics PNGs. This is a **conditional finite-time transfer surrogate only**, not observed or cosmological tau, actual heating, photoionization evolution or recombination history.

## 4. Coding R/C verification and failure classification

- Fresh executable Python 3 + NumPy source-driven generation and exact source-ZIP nested-byte/CRC locks PASS; ordinary and `python -O` unittest **12/12 each** PASS; `compileall` PASS, no compiled C++ path needed.
- Independent `mpmath` 65-digit point controls **256**; maximum relative difference σ 2.70396×10^-15, absorption probability 2.82878×10^-15. Separate Wolfram Language expression sample, analytic time-derivative sign and energy ledger PASS.
- Two actual physics plots produced and visually read. Original negative input test expected the wrong error category; repaired the test and added entry-point source-array guard before final rerun. This was **test-contract defect**, not empirical physics evidence of failure.
- R6 mathematical distinct-author and C9 code distinct-author **NOT_RUN**. Native subagent tool not exposed this session, no delegated reviewer receipt. No direct full physical transport or owner integration.
- PR125 and PR126 held; PR118 historical CPU resource FAIL and aggregate CPU cap NOT_CERTIFIED preserved. No native25/L4/production, physical exclusive He event kernel/K, coupling and stopping inherited.

## 5. DAG judgement and preservation

Canonical `CENTRAL=28/88 (+0)`, `EXTENSION=0/3 (+0)`; new scoped physical-data auxiliary `1/1 (REVIEW_HOLD)` only; retrospective new R/C workflow `18/20` (R6 and C9 NOT_RUN), not 18 scientific IVPs. Original PR125/126 branch and main MUST NOT be mutated; publish isolated Draft child only if remote ACK/readback succeeds. Stage records and cloud backups are distinct identity tiers. Next physical owner step (not automatically executed): decide correct time-dependent radiation transfer and actual ionization/thermal coupling before any promotion of this conditional opacity result.
