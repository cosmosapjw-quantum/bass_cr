# CR PHYS17 — 1976 원전 미분 단면적에 기초한 H 2p recoil emission과 causal HI 최초 산란

## 산출물: 실제 원전 입력과 scientific computation

원래 **6,400개 H/He recombination photon atoms**, 4개 birth bins를 변경하지 않고 기존 2,066개 He-origin RR photon → H photoionization → electron H(1s→2p) first-inelastic event의 **원본 NIST BE-scaled total rate**를 보존했다. 원본 SOURCE archive SHA256 `3b316c595fc1b40109f39d91af92873ba5a215281040d70bcb177dd1ab74a7dc` (`PHYS16 PR #141 HEAD 30020355677b66930856a385cf5cd4e9c3c3a24c`). 100 K static HI `nHI=138.6 m^-3`, 관측 proper-time `1e10 s` 동일. parent PHYS16 PWBA `SOURCE_EMISSION_PROFILES.npz`의 한 모델을 identity anchor로 재사용.

새 수치 연구는 **4,190 structured numerical rows**: Kingston 2p+2s UBorn DCS 90 (published θ×energy), Kingston theoretical totals 6, Williams experimental n2 DCS 48, Williams↔Kingston angle matching 48, original-source recoil crosswalk 2,066, original-source emission spectra 966, time-ordered first scatter spectra 966. 별도로 2,066×3×161 source emission-PDF NPZ와 새로운 science PNG 세 점을 생성. 원래 저작권 PDF 자체는 배포하지 않고 SHA/DOI로 reference한다.

### 1. 물리 해석에 결정적인 원전 구분

Kingston–Fon–Burke 1976 printed p613 **Table 5는 pure 2p DCS이지만 'unitarized Born'**이다. 3-state close coupling curve from p615 Fig8은 다른 계산이며, 아래 소스에서는 Table5만 수치 입력으로 사용했다. Williams 1976 printed p1526 **Table1은 측정된 n=2 inclusive (2s+2p), 각도별 2p 분리 불가능**하다. Williams 수치를 유일한 pure 2p source라고 쓰는 오류를 피했다.

Kingston 2p Table5 angle integral / Table7 independently published UBorn total relative discrepancy ≤0.00532; 2s Table4 / Table6 ≤0.0132. 이는 전사/단위 consistency에 대한 검사다.

측정 비교에서는 Williams 13.87, 16.46, 19.58eV 각 16개 θ에서 `(KFB_UB2p+UB2s − Williams_n2)/quoted_angular_uncertainty` RMS 각각 **3.6294, 4.1238, 4.5335**. 19.58eV에서 KFB UB 2p-only DCS가 Williams n2 total 중심값보다 큰 점 6/16 (1σ upper보다 큰 점 5/16). angular covariance/systematic correlations unknown; 이 residual은 **통계적 chi-squared가 아닌 독립 source-data discriminator**다.

### 2. Source-specific kinetic/recoil operator

2p UBorn DCS의 원문 anchor (13.6,19.6,30.6 eV)에서 positive log-linear energy/positive log-PCHIP cosine-angle interpolation, 분포를 적분 정규화하고 source의 NIST BE-scaled 2p 충돌률은 그대로 유지한다. 증명 가능한 비상대론적 두 입자 에너지·운동량을 따르는 `p_f(μ,E), q(μ,E)`를 계산한다. excited H magnetic-sublevel density matrix가 없기 때문에 `p_E1(w)=3(1-w²)/4` dipole along transfer `q` **assumed closure**, uniform `p(w)=1/2` alternative, and original PWBA E1 baseline 세 모델을 따로 계산한다. 발광 시간지연은 PHYS16의 상계, first-scatter에서는 prompt limit.

### 3. 새로운 물리적 계산값

`x∈[-16,16]`, `T=1e10 s`:

| Birth | KFB UB2p/E1 N_first [m^-3] | KFB UB2p/isotropic photon N_first | PHYS16 PWBA/E1 N_first |
|---|---:|---:|---:|
| earliest | 3.310737424176e-31 | 3.310008771517e-31 | 3.310870378565e-31 |
| latest | 9.838125432988e-32 | 9.835501564401e-32 | 9.838602545397e-32 |

Earliest KFB/PWBA first-scatter difference = **-0.0040157%**, while frequency-weighted instantaneous scatter opacity/hazard is KFB `1.656006381525e-06 s^-1`, PWBA `1.659917818123e-06 s^-1`, difference **-0.235640%**. First-scatter probability saturates under original enormous horizon, so these are different observables.

All new first scatter values use **original time order** `r2p_i(u)*[1-exp(-cn_HI σ(x)(T-u))]`. Zero-source or no excitation source has no new Lyα; no artificial photon source reweighting. Frequency-tail envelope is inherited *numerically evaluated* ≤0.0002147518828; this does not certify the interior frequency integration with directed-rounding intervals. Original x=0 per-atom N first parity max ≤3.86e-16 under same parent physics.

### 4. 상태와 scope

- **established/literature-supported**: 1976 paper numeric points and measured vs model distinction, after manually reading page tables.
- **derived**: positive normalized angle probability, exact nonrel recoil kinematics and causal time-ordered source operator.
- **numerically checked**: full source 2066×3×161 profiles; 4,190 scientific CSV records, 35 focused tests (same-author), graph reproduction and checksum verification reported separately.
- **conjectural**: exact 2p orientation alignment (`q`-E1) and interpolation between sparse energies; low-energy UBorn model is not measured 2p angular DCS or CCC.
- **unresolved**: physical unique emitter recoil PDF including 2p state density matrix; detailed balance / multi-scatter / escape; actual electron stopping and physical K; global He exclusive; common evolving gas/radiation/proper clock/Bianchi geometry.

**DAG: 28/88 (+0), extension 0/3 (+0), PHYS17 auxiliary `1/1 CONDITIONAL_REVIEW_HOLD` (source-owned low-energy original DCS intake).** Real distinct-author R06/C09 NOT_RUN, native subagent NOT_RUN, NATIVE25/L4/PRODUCTION HOLD; NO_MERGE, NO_FORCE_PUSH, AUTO_NEXT_NODE=false.

### 5. Figure and data inventory

`figures/PHYS17_WILLIAMS_N2_VS_KFB_UB.png` compares measured 48 points and predicted UBorn n2; `PHYS17_SOURCE_EMISSION_UB2P.png` gives original-source recoil emission x-PDF; `PHYS17_FIRST_SCATTER_UB2P.png` gives causal first-scattered source spectrum. All data original tables and actual source-conditioned outputs are in `results/`, with full per-source NPZ; `primary_tables.py` is manual exact-value transcription with source coordinates. `REPRODUCE.sh` verifies clean independent replay.
