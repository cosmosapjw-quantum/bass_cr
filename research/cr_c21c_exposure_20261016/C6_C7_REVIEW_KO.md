# C21C C6/C7 실제 샌드박스 검증 및 과학 판정

## 실행

`PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q tests -p no:cacheprovider`: 28/28 PASS. CPython/SciPy/NumPy versions in RUN_RECORD.json. Parent C21B original source blob `88002b133c659b8a42b806627796db3f13b8b6b2` matches the exact vendored source SHA256 `8cca6193747287c5fae84ce58f9249684ba258a8e38869e4626ff402336a29f4`.

실제 검사:
- 9개 exact pair / zero population / zero rate / equal stock / nearly equal stock / weak reaction, unaltered positivity 및 common event invariant.
- 4개 독립 SciPy Radau exact pair + absorber/photon exposure `∫A dt, ∫N dt` 대조.
- Very stiff depletion N0=10/H, A0=.01/H, k=1/s, dt=100 s: minority endpoint underflows 0; exposure `I_A>0`, finite `Gamma_exp` but `Gamma_BE` mathematically unrepresentable. Code returns `HOLD_ENDPOINT_RATE_UNREPRESENTABLE`. No epsilon rescue.
- N0=1/H, A0=.1/H, k=3/s, dt=2s에서 endpoint native photo-rate/exposure 평균 비는 40 이상. Two rates cannot be interchanged in the BE native Rust RHS.
- native per-absorber `Gamma, photoheat` ↔ total-H event ↔ proper cm^-3 s^-1 단위 변환 identity.
- original `q20↔qref` factor21, true Verner fit threshold at boundary, photon/thermal positivity and two birth-time source staging.
- zero-opacity two-age Radau number/energy ledgers and gas H/He nuclei conservation.
- parent C21B positive source-age `exact_pair`와 동일 conditional stock/event values; new exposure integral is extra observable.

## 독립 source-age physically timed Radau

제조한 9개 광자 stock: 기존 3개 E=(13.8,24.8,55.0)eV에서 N=(.014,.010,.008) per total H; 새 방출 시각 2개 × E_birth=(15.1,26.1,55.0)eV, 조건부 가중치 (.2,.3,.5), 각각 원본 MD14 at birth의 GL2 수/H. 실제 Verner owner 세 row, N_H0=1.8981984507140266e-7 cm^-3, Y=0.2454/[4(1-0.2454)], cosmological x=ln(a), source positive, proper density∝a^-3, fitted threshold moving cuts.

독립 Radau integrates photon counts + H,He nuclei + gas thermal W (+ gas adiabatic work) + species photoevents/heat + photon work + **real physical-time absorber exposures**. Threshold fit below/exact/above use one-sided interval RHS. This is a constructed three-energy positive source, **not** identical to native BB50K-48-cell source, native C21 Grackle or full cosmic history.

At Δln(a)=.025 and opacity_scale=.001 (controlled Verner amplitude multiplier), representative results from `evidence/REFERENCE_COMPARE.json`:

| Species | photoevent/H | Gamma exposure (s^-1) | Gamma BE endpoint (s^-1) | endpoint/exposure |
|---|---:|---:|---:|---:|
| HI | .028136850194 | 7.25749e-17 | 7.30964e-17 | 1.0071856 |
| HeI | .007549338308 | 2.39171e-16 | 2.49211e-16 | 1.0419782 |
| HeII | .000496740465 | 5.90298e-17 | 5.17499e-17 | **0.8766731** |

**실제 물리적 차이:** HeII absorber는 HeI→HeII 반응으로 단계 도중 생성되므로, `α_HeII(t)`는 단조 감소라고 볼 수 없다. 따라서 HI/HeI 같은 pure-depletion-bound `Gamma_BE/Gamma_exp≥1`을 HeII에 강요하면 물리적 오류다. 코드에 별도의 반례 회귀를 추가했다.

독립 reference photon ledger residual ~1.39e-17 photons/H; energy residual ~-1.85e-15 eV/H. Cloned original C21B Strang photo-only endpoint residual 2..128 nstep 최대 ~1.17e-16 photons/H, ~1.02e-14 eV/H. 이는 비선형 ODE 정확도와 분리된 discretized accounting validity이다.

## 실제 과학 claim gate

- Exact pair exposure R5: mathematical identity + symbolic/numerical checks scoped PASS.
- Dynamics with fixed manufactured spectra and photo-only evolving gas: independent Radau agreement + photon/binding/heat/work scoped PASS.
- Original Verner photo fit shape used with manufactured normalized amplitude; no original full native q-grid parity; this is not original C21 rust native or native Grackle.
- Importantly the exact reaction's exposure is local *single pair* time. For multiple packets with palindromic Strang composition, sum of separate pseudo-time exposures does **not** equal the real `∫α_j(t)dt`. The oracle independently integrates this exposure physically. Native BE endpoint and physical-time exposure rate are two distinct API contracts.
- Case-A RR/CI/DR, source-locked age-resolved native geometry, stiffness outside tested parameters, full EoR + Bianchi observational response: HOLD.

## Next

C8: parameter-matched time-grid refinement matrix against independently integrated Radau, report actual observed orders, no forced second-order if non-asymptotic. C10: publish source/evidence/versions/repair and provide copyable Codex prompt linking existing NCP C21 bridge and PR166 data.
