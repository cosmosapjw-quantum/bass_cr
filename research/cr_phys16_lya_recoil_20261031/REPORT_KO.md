# PHYS16 | source-conditioned Lyα recoil and static-HI one-scattering physics

## 실제 신규 과학 데이터

원본 PHYS15의 **6,400 원래 source 원자와 4개 birth bin** 중 실제 2p excitation measured/model 공통 유효 사건인 **2,066개 (모두 He-origin RR 광자에서 H 광흡수 후 생성된 전자)**를 사용했다. parent 값 `N_2p(T=1e10s)`는 earliest `3.3158906934521573e-31 m^-3`, latest `9.85567761064524e-32 m^-3`로 byte-locked source와 일치한다.

새 원본 source-conditioned 물리 데이터 총 **5,207개 CSV 행**: original per-event recoil/microphysics crosswalk 2,066; 2 birth clock×3 closure×161 emitted spectrum 966; 같은 조합의 time-ordered first-scatter atlas 966; 9 selected incoming frequency redistribution moments; 3 incoming frequencies×400 outgoing frequency bins의 static HI one-scatter R_II-like 1,200. 별도 2,066×3×161 원본 사건별 emission PDF NumPy NPZ, 실제 science PNG 3개가 생성됐다.

### 2p recoil physics

- parent line energy convention: `10.1988 eV`; H ground target `100 K`, `n_HI=138.6 m^-3` (자체 진화 없음).
- source e-H inelastic recoil energy conservation maximum relative residual `6.101432678e-16`; source-frequency angular-model maximum emitter centre shift `|x|≤1.977032481`. 이 bound는 Maxwellian Doppler + natural Lorentz로 broadened된 전체 spectrum의 support bound가 아니다.
- spontaneous Lyα photon recoil centre shift `-η_em=-0.0012677447247` Doppler widths; resonance-scatter recoil `η_sc=0.0025354894494` Doppler widths; Doppler damping `a=0.00471829643344`.
- x∈[-16,16]의 missing spectral mass ≈`1.88e-4`(natural Voigt tails); tail envelope with QUADPACK `P_tail <= 0.000214751882814` (학술적 엄밀 수치 보증 interval arithmetic는 아님).

### Time-ordered source-owned **conditional model** first scattering

`N_{1,MODEL}(T)=∑_i∫dx p_model(x|E_{e,i})∫_{s_i}^T r_{2p,i}(u)(1-e^{-c nHI σ(x)(T-u)})du`; 2p finite decay는 기존 PHYS15 경계로 제어. Integration clock `T=1e10s`. 단위 `[m^-3]`.

| Birth / angular model | finite grid (-16..16) model first-scatter m^-3 | grid + tail-only upper m^-3 | parent total excitations m^-3 |
|---|---:|---:|---:|
| `earliest:BORN_DIPOLE` | 3.31087037857e-31 | 3.31158247233e-31 | 3.31589069345e-31 |
| `earliest:ISOTROPIC_IMPACT_DIPOLE` | 3.30726458102e-31 | 3.30797667479e-31 | 3.31589069345e-31 |
| `earliest:BORN_ISOTROPIC_EMISSION` | 3.31029789617e-31 | 3.31100998994e-31 | 3.31589069345e-31 |
| `latest:BORN_DIPOLE` | 9.8386025454e-32 | 9.84071907072e-32 | 9.85567761065e-32 |
| `latest:ISOTROPIC_IMPACT_DIPOLE` | 9.82560650906e-32 | 9.82772303438e-32 | 9.85567761065e-32 |
| `latest:BORN_ISOTROPIC_EMISSION` | 9.83653568417e-32 | 9.83865220949e-32 | 9.85567761065e-32 |

**주의:** x-grid에서 trapezoid 대 Simpson 적분 상대 차이는 모델별 약 2.0e-8–2.0e-7 수준이었다. 이 값은 수렴성 진단이며 rigorous error bar는 아니다. 위 두번째 수치의 `lower`는 x-grid 양의 수치적분 값이라는 뜻이며 rigorous directed-rounding lower certificate가 아니다. `grid+tail-only upper`는 연속 모델의 x outside [-16,16] 꼬리만 제한하며, 내부 quadrature 정확도는 별도 수치 검증해야 한다. `first-scatter`는 escaped flux 혹은 다중산란 횟수가 아니다.

Model sensitivity: Born dipole vs isotropic-impact dipole earliest finite-window first-scatter difference `0.108908%`; conditional spectral-weighted initial opacity hazard difference `9.210644%`. 주파수별 time response가 달라 hazard 차이와 적분한 first-event 차이는 동일하지 않다.

### First-step redistribution R_II-like kernel, separately computed

- Absorption-selected atom parallel thermal velocity: `P(u|xin)∝exp(-u²) L_a(xin-u)` rather than unconditional Maxwellian.
- Rayleigh scattering `p(μ)=3(1+μ²)/8`, atom-frame coherence, first-order recoil; `x_out=x_in+(μ-1)(u+η_sc)+sqrt(1-μ²) v_⊥/v_th`.
- outgoing 400 bins integrated with positive Gaussian CDF, incoming `x=-3,0,+3`; mass residual ≤1.4e-12; analytic-vs-gridded first moment absolute error <5e-9 Doppler widths.
- `x_in=0` mean outgoing `-0.002535489449`; `x_in=-3` mean `-1.92358370284`; `x_in=+3` mean `+1.91851272394`. Asymmetry includes recoil; full detailed balance is not guaranteed.
- No multiple scattering iterations, no 2p fine structure/spin mixing, no global thermal feedback; therefore physical R_II, escaping flux and opacity feedback remain **UNBOUND**.

### Targeted blind referee (same author)

Two defects found in a prior pilot and repaired with actual tests: (i) assumed frequency redistribution variance symmetry under `x→-x` despite recoil; actual asymmetry `ΔVar=1.6 E[u|3] η_sc`; (ii) assumed exact oscillator f equality between hydrogenic 3/8-Hartree theory and parent 10.1988-eV convention/NIST f=0.41641; the distinct atomic inputs differ at ≈0.1%. A third numerical defect was grid-point probability-density integration yielding 1.001 rather than normalized measure; corrected with Gaussian-CDF outgoing **cell masses**. See `BLIND_REFEREE_EVIDENCE.json`.

The five CSV data tables and full per-source spectral NPZ are recorded with SHA-256 in `EXPECTED_OUTPUT_SHA256.json`. **Tests are same-author** and true distinct-author R06/C09 remains NOT_RUN. No production/integration scientific promotion.

### DAG & source status

CENTRAL `28/88 DELTA0`, EXTENSION `0/3 DELTA0`, PHYS15 old auxiliary `1/1 CONDITIONAL_REVIEW_HOLD` unchanged; new PHYS16 scoped auxiliary `1/1 CONDITIONAL_REVIEW_HOLD`. Subagent `NOT_RUN`, distinct-author R06/C09 `NOT_RUN`; physical_K, real DCS, common evolving gas/radiation/proper-clock/geometry, global He exclusive, multiple scatter `UNBOUND`; NATIVE25/L4/production `HOLD`. NO_MERGE, NO_FORCE_PUSH.
