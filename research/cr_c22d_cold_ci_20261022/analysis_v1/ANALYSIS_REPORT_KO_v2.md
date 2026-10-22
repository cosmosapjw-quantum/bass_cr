# C22D 분석 완료 보고서: 유한 H1 충돌 이온화, 공통 에너지 기준, 저장 경로 검증

## 판정과 범위

**C22D의 새 4개 해에 대한 분석은 `COMPLETE_SCOPED / PASS_SCOPED`다.** 4개 실행의 저장 격자와 solver accepted 격자, 총 8개 감사가 모두 사전 계약을 통과했고, CI LRS의 BDF와 더 엄격한 Radau 사이의 정확히 9개 필드 비교도 통과했다. 수치 gate를 완화하지 않았다. 이 판정은 주어진 초기값, 유한 원자자료 모형, 실제 반환된 유한 격자에 국한된다. `global_error_bound = null`이며 전체 thermochemical/radiative energy closure는 계속 OPEN이다. [E1–E3]

관측된 CI 변화와 공통 에너지 기준 변경을 분리했다. 새 기준에서 CI ON−OFF의 최종 온도 차이는 −0.001745967 K, 최종 전자밀도 차이는 −4.524365e−12 cm⁻³, Thomson optical depth 차이는 +3.142114e−8이다. 한편 새 기준의 CI OFF−이전 C22C 저장 해의 최종 온도 차이는 −0.011719964 K다. 두 비교를 합쳐 CI 효과라고 부르지 않는다. **CI에 의한 전단 변화는 이번 자료의 BDF/Radau 차이보다 작아 수치적으로 분해되지 않았다.** [E3–E4]

수치 분석 과정에서 새 ODE 0, RHS 호출 0, 이전 C22C 요약 재계산 0이었다. 이번 새 해의 accepted 경로 요약 4개와 새 CI 진단을 한 번 만들었다. 이후 그림의 시간축 자동 여백 문제만 고쳤으며, 그 단계에는 provider 평가와 accepted 요약 재계산도 모두 0이었다. 원 분석 JSON·NPZ·CSV와 원본 그림은 보존했다. [E2, E5–E7]

## 1. 입력과 증거 결속

새 과학 실행 source identity는 `2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72`이고, 이전 C22C source identity는 `e27e8506473833c6265343406b378bb2e8e260c2e8df6b5ab8537c5d7dfa904d`다. `CONTRACT.json` SHA256은 `4022fc0c2e72d9cf18d9064f42170b524050f0eebe35b7b8db6d080880e9be4b`다. [E1–E2]

새 nominal run은 `c22d_h1_ci_bdf_20261022_v1`이며 BDF `rtol=3e-11`, `atol=3e-13`을 사용했다. 세 case는 `registry_control_lrs`, `ci_lrs`, `ci_flrw`다. 별도 reference run `c22d_h1_ci_radau_20261022_v1`의 `ci_lrs`는 Radau `rtol=3e-12`, `atol=3e-14`다. 모두 ellmax=8, 출력 상태 78개, 적분 상태 75개, 저장 시각 201개다. 21개 원자 population은 출력에서 유지했다. 선언한 초기 영 inventory인 n, T0, T1의 불변 좌표만 적분 상태에서 제외했다. [E1–E2]

`read_run`은 COMPLETE, SOURCE, INPUT, RECEIPT, MODEL과 원 history의 SHA256·크기를 연결한다. hash를 계산한 바로 그 메모리 bytes를 `BytesIO`로 NPZ에 전달하여 검증과 사용 사이의 파일 교체를 피했다. `verify_old_baseline`은 단순 case 이름이나 코드 hash를 넘어, 이전 CONTRACT의 solver 설정과 입력을 확인하고 공통 물리 입력을 정규화해서 대조한다. 이름, 새 registry 키, CI 스위치를 제외한 초기값은 같고, 누락된 ellmax의 기본값 8도 명시적으로 처리했다. ON/OFF에는 같은 새 에너지 기준이 적용되며 CI 스위치만 다르다. 비교는 동일 eta 격자에서 수행했고 보간하지 않았다. [E2, E8]

기존 C22C 비교는 `c22c_h1_excitation_bdf_20261022_v1/cases/finite_uv_excitation_lrs/history.npz`의 완료된 저장 배열만 읽었다. 이전 trajectory 복원 재적분이나 이전 provider/RHS 재평가는 하지 않았다. [E2]

## 2. 이번 유한 모형이 의미하는 물리

반응은 `H1(1s)+e → H1+ + 2e`다. Href당 eta 단위 사건률을 r로 두면 H1 바닥상태 −r, H1 이온 +r, 전자 +r, 핵종수 변화 0, 전체 기체 입자수 변화 +r다. 새 CI 사건 누적값 1개를 추가했으며, 기존 77개 상태 prefix를 유지했다. [E1, E9]

채택한 유한 source는 CCC의 87행 H1 total ionization cross section이다. incident energy 13.6058–968.61 eV 안에서 σ(E)를 piecewise linear로 정의하고 Maxwell 적분한다. q의 부동소수점 값과 log10 q를 함께 보존한다. 첫 양의 자료점은 13.64 eV이므로 첫 0.0342 eV 구간의 보간 형태는 별도로 점검할 수 있다. 968.61 eV 위의 물리 tail은 UNAVAILABLE이며 0으로 안다고 주장하지 않는다. 선택된 유한 적분의 지원 밖에서 기여를 제외한 계산 정의와, 실제 물리 단면적의 미지 tail은 구분한다. 수치 provider 범위 1–1e8 K와 다른 원자자료까지 함께 적용할 수 있는 활성 범위 `3<T≤20000 K`도 구분한다. [E1]

H-family의 공통 electronic energy increment를 13.6에서 13.6058 eV로 맞추고 PI 지원역, 열 유입, binding, RR export, 초기 에너지를 함께 정렬했다. 이는 **CCC 표의 에너지 관례에 맞춘 근사 모형의 일관성 변경**이다. 물리 H1 precision threshold의 교정이라고 부르지 않으며, reduced-mass isotope shift나 Milne/LTE 일관성을 해결한 것도 아니다. D/T에도 같은 electronic energy를 쓰는 기존 isotope 근사는 남아 있다. [E1]

CI의 에너지 전달은

\[
U'_{\rm CI}=-\chi r,\qquad B'_{\rm CI}=+\chi r,\qquad E'_{\rm escaped,CI}=0.
\]

기체 입자수 N에 대해 `T=2U/(3k_B N)`이므로

\[
T'_{\rm CI}=-\frac{2\chi/(3k_B)+T}{N}\,r.
\]

열에너지 감소와 새 전자에 따른 입자수 증가가 이 식에 한 번씩 포함된다. 온도에 별도 보정항을 더하지 않는다. `model.py:H1IonizationModel.rhs`는 종과 thermal energy와 사건 누적값을 갱신하고, `summarize`는 CI binding transfer와 charge counter를 제공한다. 분석의 `additional_diagnostics`는 위 온도 기여와 조건부 역반응, 고정 경로 보간 민감도를 계산한다. `mesh_audit`의 온도 재구성은 U,N,T의 **대수적 일관성 검사**이며 새로운 독립 동역학 증명은 아니다. [E1, E8–E9]

전체 추적 에너지 합은 thermal + binding + resident UV + escaped RR + gas work + UV work + Compton bath + escaped H1 n2다. CI binding 전달을 escape 저장고에 다시 넣지 않았다. 전하 장부는 `ne/Href + C_RR − C_PI − C_CI − ne_initial = 0`이다. atomic gas의 응력은 isotropic이며, 별도 nonbaryonic Vlasov의 matter anisotropic stress와 섞지 않는다. Non-tilted LRS에서 signed amplitudes를 먼저 합한 뒤 full Frobenius norm을 취한다. 따라서 `Pi_r=abs(Pgamma+Pnu)`와 `Pi_tot=abs(Pm+Pr)`의 cancellation을 각 성분 norm의 합으로 바꾸지 않았다. [E1–E2, E9]

## 3. 저장·accepted 격자의 사전 gate

| 실행·case | 저장 점수 | accepted 점수 | accepted 에너지 최대 상대 잔차 | 저장 / accepted |
|---|---:|---:|---:|---|
| nominal:ci_flrw | 201 | 1616 | 1.445904333e-11 | PASS / PASS |
| nominal:ci_lrs | 201 | 1618 | 1.269734018e-11 | PASS / PASS |
| nominal:registry_control_lrs | 201 | 1618 | 1.269593232e-11 | PASS / PASS |
| reference:ci_lrs | 201 | 3195 | 2.033576719e-15 | PASS / PASS |

저장 점수는 총 804개, accepted 점수는 총 8047개다. 아래 값은 완료된 8개 감사의 extrema를 모은 것이다. 연속 시간 전체에서의 엄밀한 extrema나 내부 모든 solver trial 상태의 보증을 뜻하지 않는다. [E2]

| 항목 | 고정 gate | 실제 최대 또는 최소 | 판정 |
|---|---:|---:|---|
| 에너지 상대 잔차 최대 절댓값 | ≤1e−8 | 1.445904333e−11 | PASS |
| 핵종 보존 상대 잔차 | ≤1e−10 | 2.220446049e−14 | PASS |
| 전하 정규화 잔차 | ≤1e−10 | 2.406603562e−15 | PASS |
| photon number 정규화 잔차 | ≤1e−10 | 1.665334537e−15 | PASS |
| scaled population 최소 | ≥−2e−9 | 0 | PASS |
| UV count 최소/Href | ≥−2e−11 | −1.487386817e−14 | PASS |
| event count 최소/Href | ≥−2e−11 | −8.928706867e−100 | PASS |
| 온도 | 3<T≤20000 K | 29.76520014–9906.281636 K | PASS |
| nHref | ≤0.01 cm⁻³ | 최대 0.001766880378 | PASS |
| 선언한 n/T inventory | 정확한 0 | 정확한 0 | PASS |

작은 음수 UV/event 값과 사건 증가량 최소 −8.6736173799e−19/Href를 원값대로 유지했다. clipping이나 사후 0 대체를 하지 않았다. 관측 ne의 최대값은 0.0004476431546 cm⁻³이고 역반응 진단에는 이 실제 경로의 ne를 사용했다. nHref 상한만으로 ne 상한이 자동 보장된다고 가정하지 않았다. [E2]

## 4. 정확히 9개 필드의 BDF/Radau 비교

같은 201개 eta에서 CI LRS BDF와 더 엄격한 Radau를 비교했다. T, ne, tau, Sigma_F, Pi_r_F, H1 ionized fraction에는 `max(abs(reference), 1e−8 × reference_peak, 1e−30)`을 사용했다. 누적 bath energy, n2 escaped energy, CI events의 3개 필드는 `max(reference_peak,1e−30)`인 균일 scale을 썼다. 모든 필드의 고정 gate는 2e−7이다. [E1, E3]

| 필드 | scaled 최대 차이 | 물리 단위 최대 절대 차이 | gate |
|---|---:|---:|---|
| temperature_K | 9.430629324e-09 | 6.838966328e-06 | PASS |
| n_e_cm3 | 6.151598183e-09 | 2.774205561e-13 | PASS |
| tau_T | 1.791129433e-09 | 1.471912869e-11 | PASS |
| Sigma_F | 8.787874572e-09 | 1.653454526e-10 | PASS |
| Pi_r_F | 3.351942107e-09 | 5.629413494e-14 | PASS |
| H1_ionized_fraction | 6.150738800e-09 | 1.570062969e-10 | PASS |
| bath_energy_received_eV_per_H | 3.983089681e-10 | 4.478218907e-10 | PASS |
| excitation_escaped_energy_eV_per_H | 2.921815111e-08 | 1.163085073e-09 | PASS |
| H1_CI_events_per_H | 6.356984508e-08 | 4.691289920e-13 | PASS |

가장 큰 scaled 차이는 CI events의 6.356984508e−8이다. 이는 정해진 필드와 시각에서 다른 방법·더 엄격한 tolerance를 사용한 유한 비교의 통과다. 실제 물리 단면적 오차, 모든 미분해 반응의 오차, 또는 전 구간의 엄밀한 global error certificate를 주지는 않는다. CI OFF와 FLRW에는 별도 Radau reference를 추가하지 않았으므로 ON reference의 차이를 그 두 해의 보증 오차로 전용하지 않는다. [E3]

## 5. 같은 에너지 기준에서 CI ON−OFF

다음 표의 최종값은 z=2이며 차이 부호는 ON−OFF다. 단위는 T가 K, ne가 cm⁻³, 두 energy가 eV/Href이고 나머지는 무차원이다. 경로 최대 절댓값은 같은 저장 eta 배열에서의 차이다. [E4]

| 필드 | OFF 최종 | ON 최종 | 최종 차이 | 경로 최대 절대 차이 |
|---|---:|---:|---:|---:|
| temperature_K | 29.8985991406 | 29.8968531736 | -1.745967022e-03 | 4.801197611e-01 |
| n_e_cm3 | 1.44565813247e-07 | 1.44561288882e-07 | -4.524365021e-12 | 1.115951371e-08 |
| tau_T | 0.0223412071329 | 0.022341238554 | 3.142114349e-08 | 1.946818035e-07 |
| Sigma_F | 0.0156321990978 | 0.0156321990844 | -1.337416636e-11 | 1.831261531e-11 |
| Pi_r_F | 0.000136723157511 | 0.000136723170015 | 1.250354380e-11 | 5.025414915e-11 |
| H1_ionized_fraction | 0.0278874599328 | 0.0278865921463 | -8.677865088e-07 | 6.638699265e-06 |
| bath_energy_received_eV_per_H | 1.12435872574 | 1.12430782777 | -5.089796996e-05 | 5.089796996e-05 |
| excitation_escaped_energy_eV_per_H | 0.0398252310876 | 0.0398069348889 | -1.829619866e-05 | 1.829619866e-05 |

CI는 순간 반응에서 전자를 추가하지만, 결합된 열·이온화 경로의 최종 전자 수는 더 작다. 독립 검토의 저장 counter 비교에서 ΔC_PI=1.931788063e−14/Href, C_CI=7.379740530e−6/Href, ΔC_RR=8.258044039e−6/Href였다. 따라서

\[
\Delta X_e=\Delta C_{PI}+C_{CI}-\Delta C_{RR}
=-8.78303490052\times10^{-7}.
\]

이는 저장 ne/nHref의 직접 차이 −8.78303490055e−7과 3.45e−18 안에서 일치한다. 증가한 누적 재결합이 CI 사건 증가보다 큰 두 coupled 해의 장부로 최종 ne 감소를 설명할 수 있다. 이 차이만으로 RR의 개별 인과효과를 독립 분리했다거나 CI 반응 자체가 전자를 제거한다고 말하지 않는다. [E10]

CI ON−OFF의 Sigma_F 경로 최대 차이 1.831261531e−11은 ON 해의 BDF−Radau 최대 차이 1.653454526e−10보다 작다. **이번 결과로 CI 전단 효과를 분해했다고 주장할 수 없다.** 반면 온도·전자밀도·optical depth·Pi_r의 관측 차이는 해당 ON reference 차이보다 크지만, OFF의 독립 reference가 없으므로 이 크기 비교도 엄밀한 효과 오차막대가 아니다. [E3–E4]

LRS 누적 CI 사건은 7.379740529664e−6/Href, FLRW는 7.388740147703e−6/Href이며 OFF는 정확한 0이다. CI가 H1에만 있으므로 H1와 D의 ionized fraction quotient를 강제할 수 없다. LRS accepted 경로에서 두 fraction 차이의 최대는 7.091486749e−6, FLRW는 7.099825811e−6이다. OFF에서 관측된 차이는 약 5.55e−17이다. 이 H1-only source를 유지한 채 isotope quotient로 상태를 더 줄이면 물리 모형이 바뀐다. [E2]

## 6. 에너지 기준 변경과 CI를 분리

다음 차이는 새 registry의 CI OFF−이전 C22C LRS 저장 해다. 초기조건과 공통 model 입력을 확인한 뒤 저장된 배열만 비교했다. [E2, E4]

| 필드 | 최종 차이 | 경로 최대 절대 차이 |
|---|---:|---:|
| temperature_K | -1.171996447e-02 | 8.445364493e+00 |
| n_e_cm3 | -3.503874588e-11 | 2.323579677e-08 |
| tau_T | -3.061257333e-06 | 3.061257333e-06 |
| Sigma_F | -3.983723074e-12 | 4.631810213e-11 |
| Pi_r_F | 2.127753336e-11 | 1.624275078e-10 |
| H1_ionized_fraction | -6.762131409e-06 | 2.425395961e-05 |
| bath_energy_received_eV_per_H | -7.764926474e-04 | 7.764926474e-04 |
| excitation_escaped_energy_eV_per_H | -3.759048629e-04 | 3.759048629e-04 |

기준 변경만으로 경로 온도 차이의 최대는 8.445364493 K이며, CI ON−OFF의 0.480119761 K보다 크다. n2 escaped energy의 최종 변화율도 기준 변경에서 약 −0.9351%, 같은 기준 CI에서 약 −0.04594%다. 따라서 이전 C22C와 새 CI ON의 전체 차이를 새 CI 반응에 귀속하면 기준 변경을 함께 셈하게 된다. 이 분리는 수치 source 정렬 효과의 분리이며, 새 에너지 기준이 자연의 임계값을 더 정확히 맞춘다는 물리 검증을 뜻하지 않는다. [E1, E4]

## 7. 저온 CI, 조건부 역반응과 첫 구간 형태 진단

### 7.1 Underflow와 미지원 반응의 구별

LRS accepted 경로에서 유한-source `log10(q/cm³ s⁻¹)`는 약 −15.2540에서 −2303.5976까지 변했다. 1618개 중 252개에서 q의 float64 값은 underflow였고, 같은 201개 저장 경로에서는 51개였다. 로그와 명시적 underflow mask를 함께 남겼다. 유한 지원 source의 양의 적분이 부동소수점 0이 된 경우이며 absent species나 UNAVAILABLE rate를 0으로 채운 경우가 아니다. FLRW의 최소 로그값은 −2313.7431이다. [E2]

### 7.2 조건부 ground-state three-body/RR

선택한 finite ground CI와 Saha degeneracy convention `g_H1=2, g_p=1, electron spin=2`, 즉 d=1을 가정하면 S(T)=n_e n_p/n_H0에 대해 K3=q/S다. 역반응 사건률은 `R3=K3 ne² np`이고 추가 1/2를 넣지 않았다. low-T Boltzmann factor를 대수적으로 소거한 log K3를 사용하므로 underflow한 q를 직접 나눠 0/0을 만들지 않는다. 실제 경로에서 비교한 값은 `ne K3/alpha_RR`다. [E1–E2, E8]

이 비의 최대는 LRS 2.0734400e−21, FLRW 2.0734414e−21이다. 이는 선택한 유한 ground source의 조건부 inverse와 채택 RR fit 사이의 작은 비율이다. all-level three-body recombination, cascade, 실제 omitted-process 합의 상한으로 확대하지 않는다. 그런 전체 inverse closure는 OPEN이다. [E2]

### 7.3 첫 0.0342 eV 보간 형태: 고정 경로 기능량

첫 구간에서 PL의 power 1을 1.127로 바꾼 별도 형태 모형을 비교했다. 0<epsilon/h<1이고 p>1이므로 이 구간 단면적과 동일 T의 유한 rate는 PL 이하가 된다. 로그/threshold-scaled 적분의 비를 써서 low-T underflow 0/0을 피했다. 관측 LRS 경로의 rate ratio 최소는 약 0.76367이지만, 그 저온 영역에서는 CI 사건률 자체가 지수적으로 억제된다. [E1–E2]

| accepted 경로 | ODE 누적 CI/Href | PL 사다리꼴−ODE counter 상대 차이 | p1.127 사다리꼴/PL−1 |
|---|---:|---:|---:|
| nominal:ci_lrs | 7.379740529664e-06 | 1.153459167e-04 | -1.924669552e-05 |
| reference:ci_lrs | 7.379740998792e-06 | 1.742075253e-05 | -1.924690294e-05 |
| nominal:ci_flrw | 7.388740147703e-06 | 1.152949875e-04 | -1.924687664e-05 |

LRS nominal accepted 경로의 PL 사다리꼴 적분은 7.3805917526e−6, p1.127은 7.3804497006e−6/Href다. 이 두 사다리꼴의 상대 차이 약 −1.92467e−5는 **같은 mesh·같은 경로·같은 구적 방식에서 정의한 기능량 민감도**다. nominal PL 사다리꼴과 ODE counter의 상대 차이 1.15346e−4보다 작다. Radau accepted 경로의 해당 구적 불일치도 1.74208e−5다. 201개 저장점만 사용하면 nominal LRS PL 사다리꼴−ODE counter 차이는 약 2.23%까지 커진다. [E2]

따라서 사다리꼴을 ODE의 사건 누적값으로 대체하지 않는다. 위 민감도를 실제 새 trajectory의 counter 변화, thermal/ionization feedback 변화, 보간 오차 상한, 또는 ODE 해오차로 부르지 않는다. ODE에 포함해 함께 적분한 원 counter가 일차 결과다. 서로 다른 accepted mesh에서 유사한 기능량 비율이 나왔더라도 새로운 구적 오차 증명이 생긴 것은 아니다. 새로운 sensitivity ODE는 수행하지 않았다. [E2]

## 8. 그림의 실제 판독과 표시 문제 보존

원 v1 PNG를 실제 판독하자 symlog 축에 Matplotlib 자동 여백이 음수 시간/eta tick과 겹친 레이블을 만드는 표시결함이 있었다. 수치 데이터가 아니라 축 범위 문제였다. 원본 4 PNG·4 PDF와 `FIGURE_V1_VISUAL_FINDING.json`을 보존했다. 원 수치 분석 source도 `analyzer_executed_v1.py`로 그대로 보존했다. [E5, E8]

그림만 만드는 별도 모드는 완료된 JSON/NPZ와 원 저장 배열의 hash를 확인한 뒤 physical x-limit을 0부터 최대 plotted time/eta까지 설정했다. 새 위치 `figures_v2/`를 create-only로 사용했다. 수치 요약, provider 평가, ODE를 다시 실행하지 않았다. 교정 후 4개 PNG를 모두 실제 판독해 축·단위·범례·부호·cancellation·scope 표시가 읽히는 것을 확인했다. PDF는 동일 figure의 export이며 hash/size를 확인했다. PDF를 별도로 raster화해 읽었다고 기록하지 않는다. [E6–E7]

![CI와 기준 변경 비교](figures_v2/MATCHED_EFFECTS_AND_REGISTRY.png)

**그림 1.** 절대 T/ne/tau 경로와 CI ON−OFF, registry OFF−old C의 별도 차이 패널. 거의 겹치는 절대 경로만으로 작은 효과를 과장하지 않도록 차이를 별도로 보였다.

![에너지와 응력 및 보존](figures_v2/ENERGY_STRESS_AND_CONSERVATION.png)

**그림 2.** signed stress와 Frobenius norm을 분리하고 cancellation을 남겼다. 에너지 8항, 사건 누적값과 보존 잔차를 표시했다.

![고정 9필드 reference](figures_v2/STRICT_NINE_FIELD_REFERENCE.png)

**그림 3.** 사전등록한 9개 필드, 같은 201 eta, fixed 2e−7 gate. 이 그림의 통과와 작은 CI 전단 변화의 물리적 분해 여부는 별개다.

![CI source 및 조건부 진단](figures_v2/CI_SOURCE_AND_CONDITIONAL_DIAGNOSTICS.png)

**그림 4.** finite log rate, 사건률, 첫 구간 형태, 조건부 ground inverse, fixed-path 누적 구적과 입자수 효과를 한 번 포함한 CI 온도 기여. 민감도와 역반응의 제한을 제목에 명시했다.

## 9. 계산 비용, source hash와 실패 기록

수치 분석은 CPU3, native thread 1개에서 wall 106.696117 s, CPU 104.808135 s였다. 시작 자원 관측은 affinity 0–8, quota 8 CPU, memory limit 8 GiB였고, parent가 CPU3를 배정했다. thread 관련 환경변수 6개는 모두 1이었다. 관측된 cooperative lease JSON 목록은 비어 있었으며, 이 관측을 다른 coordinator의 무제한 자원 허가로 해석하지 않았다. figure-only 수정은 같은 CPU3에서 wall 40.247134 s, CPU 39.913496 s였다. 모두 완료되어 CPU3를 반환한다. 시간은 이 실행의 실제 비용이며 안정적 speedup 주장이 아니다. [E2, E6]

| 코드·증거 | bytes | SHA256 | 역할 |
|---|---:|---|---|
| analyzer_executed_v1.py | 45148 | 3391cfd378e76c31c4f3509c395f80ded2b8a6eef7b0487bb7591facffadde5e | 수치 결과를 실제 생성한 분석 코드 |
| ../analyze.py | 50569 | 9f0373658c0c19eed825ab47b2074bda6c7fbc82430f1696ec7900b7f5b7fb4a | 그림 범위 수정·완료 배열 재사용 모드를 포함한 현재 코드 |
| SUMMARY.json | 47553 | 4e440447ccc3224d57bb85d24ced72d626029ed91efac5db391ebfcc9d9f4472 | 변경하지 않은 수치 결과 authority |
| ARTIFACT_MANIFEST.json | 8727 | d0fa0a87398188147f08690938eaaaf2a1816edb0bdafa1a46813106e6a561cf | 원 수치 및 v1 그림 파일 pin |

원 `SUMMARY.json`의 `failure_scope.all_gate_failures_preserved=false`는 구현에서 `not passed`를 저장한 모호한 명칭이다. **이번 분석의 gate failure count는 0**이며, 이 false를 과거 실패를 지웠다는 뜻으로 해석하면 안 된다. 원 JSON은 수정하지 않고 이 보고서와 `FINAL_COMPLETION_v2.json`으로 의미를 명료화한다. 모든 관측된 이전 실패는 별도로 보존한다. C22D lightcheck의 두 잘못된 상대 predicate 실패와 그 후의 correctly-rounded-addition 검토, 외부 최초 127 raw의 JSON 실패·재적분 이력, VigilODE P02 C6 FAIL, 미완료 campaign의 기존 상태, 이번 v1 그림 표시결함을 지우지 않았다. [E1–E2, E5]

접근할 수 없는 대화는 UNAVAILABLE이다. 회수되지 않은 원 nuclear-network PNG는 NOT_RECOVERED_NOT_READ다. 기존 C21O/NCP 51개와 과거 외부 raw의 재실행 또는 전체 재감사를 이번 분석 결과로 주장하지 않는다. [E1–E2]

## 10. 4축 상태와 다음 DAG

| 축 | 이 분석 담당 범위의 완료 상태 | 다음 의존 작업 |
|---|---|---|
| EXECUTION | 새 4개 완료 해의 분석·8 mesh 감사·9field reference·그림 실제 판독 COMPLETE_SCOPED; 분석 ODE/RHS 0; 원 raw 불변 | 이 결과를 고정된 유한 모형의 증거로 사용 |
| PUBLICATION | 재현 코드, CSV3, NPZ9, 수치 JSON, 교정 그림4쌍과 보고서를 로컬 준비 | parent가 저장소 게시와 실제 ref/ACK를 별도로 기록 |
| BACKUP | 이 담당 작업은 원격 백업을 수행하지 않음; 완료된 로컬 결과를 parent package에 제공 | provider별 ACK/byte 검증을 확인; Drive 보존 OPEN을 임의로 닫지 않음 |
| DAG | C22D finite H1 CI scoped 결과 완료 | 실제 atomic-rate coverage와 full thermal/radiative closure는 계속 OPEN; 다음 소스 계약이 선행 |

이번 값은 finite H1 excitation+CI, 채택 PI/RR, thermal/UV/Compton 장부의 제한된 새 단계다. higher-n 및 D/T/He/Li excitation/CI, physical tails와 보간 오차, all-level inverse, DR energy/cascade, charge exchange, free-free, nonthermal secondary electrons, line trapping/reabsorption와 2s mixing, stellar/nuclear emissivity, trace thermal/radiative Einstein feedback이 남아 있다. 관측된 omitted trace H² fraction 최대 약 7.14e−10은 따로 추적한 진단이며 omitted feedback의 global error bound가 아니다. [E1–E2]

새 반응을 추가하기 전에 source coverage·단위·유효 온도·핵종/전하/에너지 보존·dominant omitted processes·isotope quotient 조건을 다시 계약해야 한다. 그 뒤 새 입력과 새 run ID로 가벼운 delta 검증→실제 자원/lease 확인→계산→분석→게시/백업을 진행한다. 이미 완료된 이번 네 해를 복원 목적으로 재실행할 필요는 없다. Full nuclear high-energy와 general triaxial/tilted/polarized CMB는 HOLD다. strong no-go나 완전한 물리 network 완료를 주장하지 않는다. [E1]

## 증거 위치

- [E1] `../CONTRACT.json`: source 범위, 에너지 기준, preregistered gates, omission 및 HOLD 계약.
- [E2] `SUMMARY.json`과 네 `*_AUDIT.json`: 실제 mesh 수, 자원, 원본 불변, gate·진단 결과.
- [E3] `STRICT_REFERENCE.json`, `STRICT_REFERENCE.csv`, `STRICT_REFERENCE_ARRAYS.npz`: 동일 eta 9field 비교.
- [E4] `MATCHED_EFFECTS.json`, `HISTORY.csv`, `ENDPOINTS.csv`: 같은 registry CI 효과와 이전 C registry 효과의 분리.
- [E5] `FIGURE_V1_VISUAL_FINDING.json`: 원본 표시결함을 보존한 기록.
- [E6] `figures_v2/RENDER_COMPLETE.json`: 완료 수치 배열의 hash 재사용과 science 재계산 0.
- [E7] `figures_v2/FIGURE_VISUAL_REVIEW.json`: 실제 PNG 4개 판독 및 범위.
- [E8] `analyzer_executed_v1.py`, `../analyze.py`: 실제 수치 분석 코드와 그림만 수정 가능한 현재 코드. CI 수식·source/input binding은 별도 담당자의 one-pass 검토 PASS_SCOPED.
- [E9] `../model.py`, `../ci_finite.py`, `../optimized_kernel.py`: 동결된 실행 source에 속한 구현. 이번 분석은 source를 바꾸지 않았다.
- [E10] `/workspace/scratch/30d955d9ea43/c22d_20261022/review_final/FINAL_CHARGE_DIFFERENCE.json`: 독립 검토의 저장 counter 장부; `FINAL_COMPLETION_v2.json`에 hash pin과 값이 포함된다.

## 문서 교정 이력

v2는 증거 [E9]의 파일명 오기 `ci.py`를 실제 동결 파일 `ci_finite.py`로 고쳤다. 최초 보고서·완료 JSON·manifest는 그대로 보존했으며 수치·그림·분석 코드 변경은 없다. 현재 문서 authority는 `ANALYSIS_REPORT_KO_v2.md`, `FINAL_COMPLETION_v2.json`, `FINAL_ARTIFACT_MANIFEST_v2.json`이다.
