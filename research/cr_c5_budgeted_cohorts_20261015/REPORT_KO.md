# BASS_CR: 반응률 인지형 유한 메모리 photon cohort 압축 구현

**2026-10-15 KST · C5 신규 연구 단위**. 실제 upstream `bass_cr` PR65 head `438a36a4529ead5192896941cfcac196301b36cc`를 기준으로 구현한다. 기존 `rei_bianchi` CR/RCT/HH-OFF 계산·source ID·코드 및 실행 중 Codex 원본은 바꾸지 않는다.

## 1. 물리/수치 계약

원 source `MD14_Z002_FESC_BB50K_13P6_100_V1`: 50,000 K, [13.6,24.59,54.42,100] eV. 실험상 neutral proper number densities `(1e-3,8e-5,2e-5) cm^-3`와 frozen-neutral absorption `dt=1e9 s`는 **새로 선언한 toy fixture**이며 실제 cosmic history에서 읽은 상태가 아니다. `c=2.99792458e10 cm/s`, energy eV, count per H, proper seconds, signature `(-,+,+,+)`.

실제 photon은 `(E_i,n_i)`라는 물리적 energy centroid/packet로 보존하며, 기존의 매 step fixed energy node projection을 반복하지 않는다. 우선 `CohortTransport` 부모를 그대로 사용하고, 압축 단계에서 `(E1,n1),(E2,n2)`를

\[
 n=n_1+n_2,\qquad \bar E=\frac{n_1E_1+n_2E_2}{n}
\]

로 합쳐 count·first energy moment를 보존한다. 이 자체만으로 반응률을 보존하지 않으므로 **상대 적색편이의 예고구간** `[r_min,1]` 전체에서 H I/He I/He II 문턱을 가로지르는 병합을 금지한다. 현재 예고구간에서는 하단 에너지 support 13.6 eV도 보존한다. 환경이 바뀌거나 예고구간이 초과되면 이전 증명서를 사용할 수 없다.

## 2. Verner 도함수 상계와 implicit 사건 함수

Verner 단면적에 대해 $x=E/E_0-y_0$, $y=\sqrt{x^2+y_1^2}$, $A=(x-1)^2+y_w^2$, $z=\sqrt{y/y_a}$이며

\[
\sigma=10^{-18}\sigma_0 A y^{p/2-11/2}(1+z)^{-p}
\]

이고 매끄러운 한 threshold-side 구간에서는

\[
 \frac{\sigma'}\sigma=\frac{2(x-1)}{E_0 A}+\left(\frac p2-\frac{11}2\right)\frac{x}{E_0y^2}-\frac{pxz}{2E_0y^2(1+z)}.
\]

고정 흡수자에서 $p_k(E)=\Delta t\,c\,n_k\sigma_k(E)$, 한 단계 implicit photon 사건확률 $G_k=p_k/(1+\sum p_j)$라면

\[
|G_k'|\le |p_k'|+\sum_j|p_j'|=L_k^{(N)}, \qquad
\left|[ (E-\chi_k)G_k]'\right|\le 1+(E_\max-\chi_k)L_k^{(N)}
\]

(활성 구간의 나머지 종에 대해 정해진 $p_j'$, 비활성 종의 $G_k=0$). `src/compressed_cohorts.py`의 `one_step_pair_bounds`는 **전체 `[r_min E_1,E_2]`를 포함**하는 $\sigma'_k$ 충분 상계를 endpoint extrema로 계산한다. `n_1|E_1-\bar E|+n_2|E_2-\bar E|`에 곱하여 각 종 사건량/초과열량의 *one-step frozen-neutral* 상한을 합산한다. 어떤 threshold 또는 13.6 eV support를 가로지르면 그 쌍은 병합 불가다. 예산 부족이면 `CompressionHold`이며 기존 상태는 그대로다. 계산은 float64와 1e-10 수준 padding을 쓰므로 **위 식은 exact-real sufficient bound이고, 산술적으로 인증된 outward interval은 아니다**.

## 3. 실제 C5/C6/C7 결과

`src/compressed_cohorts.py`에는 guarded transactional `compress()` 및 `inject_and_compress()`가 구현되어 있다. 기존 `src/threshold_rt.py`를 재현본으로 함께 보존한다. `src/compression_benchmark.py`는 비압축 source-cohort 기준과 동일한 source·neutral·timestep에서 실행한다.

고정 source n16은 48개 cohort. `max_cohorts=32`, `r_min=.99`, 종별 event budget `.01 count`, heat budget `1 eV`를 선택하면 **48→32** (16 merges). 네 적색편이 값 `r=1,.999,.995,.99`에서 실제 각 종 BE 사건/열량 차이는 모두 선언한 local upper bound 아래였다.

| Observable | 증명서의 모델식 상계 | 실제 최대 사례 r=.99 부근 |
|---|---:|---:|
| HI 사건량 (count/H) | 3.367779e-4 | 3.8733e-6 |
| HeI 사건량 (count/H) | 3.270197e-4 | 7.2003e-7 |
| HeII 사건량 (count/H) | 1.716599e-4 | 5.3518e-9 |
| HI 가열량 (eV/H) | 2.326529e-2 | 1.8834e-6 |
| HeI 가열량 (eV/H) | 1.927163e-2 | 1.7777e-5 |
| HeII 가열량 (eV/H) | 7.177844e-3 | 1.4775e-7 |

별도의 four-step 연속 운반 실험에서는 매 step `.997` 적색편이, `dt=1e9 s` 고정흡수, *initial source의 0.1 count를 매번 추가*한다. 원 reference는 **48→96→144→192→240 packets**, 압축 실험은 최종 32개를 유지한다. 여기의 compression budgets는 event .05, heat10; 매 step 그때그때 **새 국소 오차 예산**을 적용한다. 표는 실제 진화 차이이며 네 step에 대한 rigorous total-error bound가 아니다.

| step | raw→compressed cohort 수 | HI event 차이 [count/H] | HeI 차이 | HeII 차이 |
|---:|---:|---:|---:|---:|
|1|96→32|−9.110830e−8|−5.616568e−8|−1.581160e−8|
|2|144→32|−5.406751e−7|−1.618161e−7|−1.716714e−8|
|3|192→32|−1.486723e−6|−3.302753e−7|−1.850382e−8|
|4|240→32|−2.722524e−6|−3.803406e−7|−1.982448e−8|

Count·energy/source redshift/photochemistry ledgers within floating tolerance. **압축 패킷을 계속 진화시키므로 각 국소 certificate는 미래 비선형 history에 대해 자동 합성되지 않으며, redshift/absorb 뒤 현재 certificate는 무효화한다.** `max_cohorts=16`, `r_min=.98`, budget `.01,1`에 대해서는 명시적인 `HOLD`가 반환되고 상태가 변경되지 않는다. 이는 안전하게 멈추는 처리이지 동일 정확도로 항상 16개 표현을 제공한다는 주장이 아니다.

## 4. 기존 repo와 충돌 방지

비압축 `CohortTransport`는 앞선 PR65의 실증 reference다. HE, HH의 atomic rates 및 REI 다른 source는 수입하지 않는다. 새 구현은 `bass_cr` C5 코딩 연구이고 **production `rei_bianchi`를 수정·재실행하지 않는다**. REI의 기존 signed-run, AX11·AX12, source identity, CR/RCT/HH OFF 상태와 독립이다. Owner가 고려할 경우에는 새 source/solver version ID를 붙여 별도 matched comparison을 수행해야 한다.

현재 `rei_bianchi` Codex 작업트리에는 진행 중인 변경이 있었으므로, branch owner 파일을 고치거나 프로그램을 종료하지 않았다. `bass_cr`로만 Git 변경을 적용한다.

## 5. 검증·재현·근거

- `PYTHONPATH=src pytest -q tests`: 총 **58 tests passed** (부모의 35개 포함, 신규 23개). 이론식 도함수 경계·threshold crossing/HOLD/transactionality·입력오류·energy moments·4-step smoke 포함.
- `PYTHONPATH=src python src/compression_benchmark.py`: 실제 n16 source와 위 조건으로 실행, `results/COMPRESSION_BENCHMARK.json` 보존.
- Wolfram Language 15.0.1에서 Verner 로그도함수와 first moment 항등식 각각 residual0, 실제 xAct/xTensor1.3.0에서 5개 텐서 residual0 (동일 작성자 경로; 외부 독립 심사 아님).
- 사용 문헌: Mirocha et al., ApJ 756 (2012)94, https://arxiv.org/abs/1204.1944 (ionization+heating spectral fidelity); Baumschlager, Shen, Wadsley, A&A (2024), https://www.aanda.org/articles/aa/pdf/2024/11/aa48164-23.pdf (piecewise ionization-edge spectral reconstruction). 이들 접근이 최초이며 본 작업의 측정값은 별개다.
- 전역 full nonlinear REI ODE/history, transport error proof, moving angular Bianchi, physical electron collision calibration, QCD/atomic provider update, external independent scientific review, native subagent: NOT_RUN.

**다음 실행:** 같은 source ID의 별도 시험에서 일련의 absorption coefficient·He ionization fronts와 고정-grid transport 비교, 실제 한 단계 유한율 spectrum error estimator의 directed-rounding 검증, 필요하면 적응형 horizon revalidation. 실제 owner AX11/12 gate는 달라지지 않는다.

## 6. v2: 실제 SOURCE07 C3 q-reference 입력과의 접속

기존 구현 v1은 `frozen_source()`의 최대100 eV로 packet energy support를 함께 묶어두어 **새로운** `rei_bianchi` SOURCE07 C3의 움직이는 방향 photon ray에 필요한 **432.2293723204678 eV**를 다루지 못했다. 원 Codex `research/source07_c2_q_reference_20261015/NEXT_C3.json`를 **2026-10-15 01:09 KST 실제 working tree**에서 읽어 발견한 결함이다. Source07 C2는 각도8, source-cell48, 384 ray packet, 원 source injection에 Bianchi `R*J`를 정확히 한번 적용, collisionless k_i 운반 및 proper neutral frozen absorption reference를 이미 제공한다. 기존 implementation 또는 그 테스트를 반복·복제하지 않고, 이 압축기는 그 packet producer가 출력한 **(현재 physical energy, normalized count)** tuple만 소비한다.

v2에서는 Verner 공식 적용범위 **50 keV**까지의 cohort energy와 frozen-neutral error-estimator 및 `redshift`를 허용했다. 내부 source identity는 여전히 13.6–100 eV의 기존 50,000K source이며, **별도 q-ray 소스가 입력될 때는 source_model_id, source clock, angular Jacobian, per-ray geometry가 owner 소유**다. 이 코드가 자동으로 q-ray energies/weights를 계산하지 않는다. 새 테스트 3개에서 실제 432.2293723204678eV 경계의 packet이 보존적으로 redshift하고, 400–432eV 보간 후보가 local event+heat bound 안에 있음을 확인했다. 50keV 초과의 입력/적색편이는 명시적 ValueError와 transactionality로 처리한다.

이로써 SOUR​​CE07 C3의 **고에너지 에너지 support에 대한 인터페이스 blocker를 컴포넌트 단계에서 해소**했다. 그러나 Bianchi 각도/생성시각 source와 실시간 chemistry connection을 구현한 것 또는 AXBI의 완료된 새로운 DAG gate는 아니다. 원 AX08 signed history와 AX11/AX12 실행은 owner가 계속한다. Tests v2: **61 passed**.
