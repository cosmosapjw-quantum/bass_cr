# 독립 과학 판정 — 실제 source 결속과 cutoff thermal join

검토자: `/root/independent_review`. 적용 하네스: GPT-6 Astra v4.0.0 연구 및 코딩. 후보·구현은 `/root`, 유도·source 분석은 `/root/dag_audit`, consumer 조사·계획은 `/root/consumer_intake`가 맡았다. 검토자는 이 후보 생성과 owner 검증 설계에 참여하지 않았다. 별도 보조 검토자 `/root/independent_review/thermal_ledger_audit`는 에너지·입자 장부의 논리만 읽었으며 코드 실행이나 수정은 하지 않았다.

## 1. 판정과 정확한 승인 범위

**PROMOTE — 고정된 source와 bath에 대한 단위 결속, 저장 기록의 산술, 명시된 A2 cutoff thermal-join 후보 및 누적 에너지 회계 상계의 연구·보고 재사용에 한정한다.** 후보의 source 정의, 시간 인자, birth 가중치, cutoff 에너지·입자수의 소유에서 이 범위의 승격을 막는 오류는 발견되지 않았다.

최종 후보 manifest는 `28b63802e061e8141bb9d7668765c574472064a5cbbfe42c693563d5e984bc2c`이고 81개 등록 파일이 모두 일치했다. 과학 코드, 결과 및 계약의 SHA256은 다음과 같다.

| 대상 | SHA256 |
|---|---|
| `evaluate_source_binding.py` | `0c9e1454d162f8d4c744fa8a7b11265db4e671d2f8270a2b547bbb175d41c964` |
| `results/SOURCE_BOUND_RESPONSE.json` | `dd4ed10b5ecd3aea8a8710b5190c9d7da4085834713bc72ae2cc37915cc97f27` |
| `CONTRACT.json` | `55c7630675b9de175215413ba0273e4a2db3af3154d7dc307aa2f58016a324cc` |
| 최종 `DERIVATION_KO.md` | `9c85133521984c48c11ad13d62e96b4a741ce78139c73f5da65ea01746bf47a2` |

이 승격은 cutoff 아래 물리적 thermalization, cutoff 독립성, 원자 자료·source 모형의 정확도, 새 gas-feedback 이력 또는 실제 one-temperature REI receiver 채택의 승인이 아니다. 제6.4절의 all-free event 항은 미완결 분해로 남으며 승인하는 대안 receiver에 포함하지 않는다. 실제 consumer observable, absolute/relative tolerance와 reference denominator는 모두 null이다. 보고서와 PDF의 최종 조판도 이 과학 판정의 범위가 아니다.

## 2. 실제 source와 M0의 물리 단위

원 `InjectionModel.q_proper_m3_s_eV`는 이미 각도 적분된 proper-volume당 proton 주입률이다. 전체 10 keV–1 PeV에서 주입 에너지를 정규화하고, comoving-to-proper 인자를 내부에서 적용한다. `DirectElectronSource`는 이 source 중 1–4 MeV 충돌 창만 중성 H/He와 적분한다. 따라서 4π, 추가 `(1+z)^3`, 충돌 창 재정규화가 필요하지 않다. 이 사실은 원 코드의 정의·constructor·호출 연결에서 확인했으며, source 적분을 다시 실행하지 않았다. [SRC-INJ, SRC-A, SRC-B]

선택된 leading-local 문제에서는

\[
A(W)=\sum_s n_{s,0}\int q_p(K)v_p(K)
\frac{d\sigma_{p,s}}{dW}\,dK,
\qquad Q_e(W,t)=tA(W).
\]

`A(W)`의 단위는 m⁻³ s⁻² eV⁻¹이고 `Q_e`는 m⁻³ s⁻¹ eV⁻¹인 birth rate다. 기존 electron stock 또는 PHYS01 terminal heat packet과 같지 않다. 같은 기본 proton source라도 PHYS01의 정확 collisionless Bianchi population와 PHYS02의 local ramp는 시간 근사와 전자 응답이 다르다.

`A_E=∫_[0.1,900] W A(W)dW`, 관측시간 `T_obs=10^10 s`라 쓰면 원 실행의 공통 에너지 scale은 `U_*=T_obs² A_E`이고, 올바른 endpoint input power는

\[
q_*=\epsilon_{\rm eV}U_*/T_{\rm obs},\qquad
q(t)=q_*t/T_{\rm obs}.
\]

이 source에서 누적 주입 에너지는 `ε_eV U_*/2`다. 후보는 factor 1/2를 보존하고 `q_*`를 전체 proton injection power로 바꾸지 않는다. 실제 9600 launcher는 같은 `ElectronSource()` 객체를 두 원자 모형에 전달한다. C의 교체는 atomic representation이고 source/cascade alias는 B에서 유지된다. E의 saved-grid adapter와 launcher는 저장된 source 배열·에너지 scale을 그대로 pulse에 전달한다. [SRC-C, SRC-C9600LAUNCH, SRC-CRUN, SRC-ESAVED, SRC-ELAUNCH]

고정 heat kernel에 대해

\[
P_h(T_{\rm obs})=\int_0^{T_{\rm obs}}K(\tau)q(T_{\rm obs}-\tau)\,d\tau
=q_*H_0R,
\]

\[
E_h(T_{\rm obs})=\frac{q_*}{2T_{\rm obs}}
\int_0^{T_{\rm obs}}(T_{\rm obs}-\tau)^2K(\tau)\,d\tau
=\frac{q_*T_{\rm obs}}2H_0S.
\]

원 pulse 구현의 `J1=H0 R`, `J2=H0 S/2` 및 `SI_J1`, `SI_J2`가 이 변환을 직접 지지한다. `p`는 pulse의 eventual heat에 대한 창 안의 분율이고 ramp 응답 계수가 아니다. 또한 이 누적식은 선형 source의 결과이며 이차 source의 누적 열을 닫지 않는다. [SRC-EPULSE, SRC-ELAUNCH, SRC-E_FULL, SRC-E_LEGACY]

## 3. Birth 열의 가중치와 cache 표현

두 source 열은 각각 `A(W)/A_E,selected`를 적분해 만든다. 각 열이 이미 원 source의 band 에너지 가중을 포함하므로 물리 공통 scale에 다시 band fraction을 곱하면 이중 가중이다. `H0_j`는 전체 선택 에너지로 정규화된 기여이며, 해당 band 자체의 에너지당 수율과 구별된다. 후보는 heat를 계산할 때 공통 scale을 유지한다. 출력의 `H0_per_own_birth_energy`는 저장된 band energy 비율로 환산한 진단으로 읽으며 b를 재정규화하는 연산으로 쓰지 않는다. [SRC-B: `source_vectors`, candidate: birth loop]

band 내부 모양을 유지하는 비음의 amplitude 변경은 `Σ λ_j H0_j R_j`, `Σ λ_j H0_j S_j`로 재사용할 수 있다. delay law를 다시 정규화할 때의 혼합 가중치는 `λ_j H0_j`에 비례한다. 임의의 band 내부 source shape나 bath 변화는 이 두 열만으로 복원되지 않는다. 특히 xi=.01에서 .1로 바꾸면 source 모양이 비례하더라도 Coulomb 및 neutral rates가 변한다.

`selected_record`와 `birth_defined`는 각각 저장 소수를 정확 입력으로 읽은 별개 표현이다. 후보는 서로를 덮거나 두 law의 제약을 교차하지 않는다. 이번 reference의 원 `J1/J2` 합산과 두 표현의 마지막 자리 차이는 같은 역사적 계산을 통과한 기록의 표현 차이다. 독립 원자 자료 검증이나 새로운 입력 오차 확률분포가 아니다. [SRC-FINPUT, SRC-FANALYSIS, SRC-CACHECODE]

## 4. A2 thermal join의 수·에너지 항등식

원 cascade는 cutoff에 실제 전달된 energy와 number를 별도로 보존한다. subcutoff daughter의 실제 에너지는 threshold보다 낮을 수 있고 near-cutoff ghost projection도 별도로 있으므로, 일반적으로 `E_cut != 0.1 eV × N_cut`다. cutoff rate는 `Gz+u b`에서 나오며 source가 cutoff ledger로 직접 투영된 몫도 포함한다. 후보는 저장된 두 ledger를 읽고 임의의 threshold×count 또는 `N_cut/T_obs`로 대체하지 않는다. [SRC-B: `project`, `summarize`]

원 number functional은 `N_active + N_cut - N_ion,HI - N_ion,He`다. 영 초기 active stock 아래

\[
N_{\rm birth}+N_{\rm secondary}=N_{\rm active}+N_{\rm cut}
\]

가 성립한다. 모든 자유전자수와 thermal electron 수는 다르다. A2가 thermal bath에 넣는 전자수는 `N_cut`이며, primary birth나 secondary ionization 수를 이에 다시 더하지 않는다. 아직 active인 전자는 별도 nonthermal reservoir에 남는다. nuclei의 원자·이온 stage 변화는 이 모델의 thermal heavy-particle 총수 `n_H+n_He`를 바꾸지 않는다. [SRC-B: `functionals`, paired9600 `final.components.selected_total`]

이 closure를 **정의로 선택한** 고정부피 thermal 부분계에는

\[
P_{\rm th}=P_h+P_c,\qquad S_{\rm thermal}=S_c,
\qquad u_{\rm th}=\tfrac32k_B n_{\rm th}T_g
\]

를 쓴다. 따라서

\[
C_V\dot T_g=P_h+P_c-\tfrac32k_B T_g S_c.
\]

새 입자수 항의 음의 부호는 맞다. 같은 온도에 새 thermal 입자를 포함시키는 데 필요한 에너지를 반영한다. prescribed 누적 에너지와 수만으로 최종 온도를 대수적으로 구하면

\[
\Delta T=
\frac{E_h+E_c-\tfrac32k_B T_{g,0}N_c}
{C_{V,0}+\tfrac32k_B N_c}.
\]

후보의 `delta_T_prescribed_energy_algebra_K`는 이 식이고 `linearized_delta_T_frozen_coeff_K`는 `C_V,0`만 분모에 남긴 일차 값이다. 원 입력에서 둘의 차이가 극히 작더라도, 독립 toy에서는 입자수 증가를 크게 잡아 두 식을 구별했다. 양의 에너지 유입만으로 온도 증가의 양의 하한이 생기지는 않는다. 충분히 차가운 입자가 늘면 온도는 낮아질 수 있다.

이 열역학 대수가 닫혀도 원 cascade가 바뀐 기체 조건에서 유효하다는 뜻은 아니다. 원 0.1 eV cutoff 연구의 unresolved 상태를 소거하지 않으며, A2는 frozen transport 출력에 대한 명시적 추가 closure다. 실제 receiver는 total/thermal/nonthermal 전자수와 EOS·collision-rate 소유권을 함께 결속해야 한다.

## 5. 누적 outside-energy 상계의 범위

`A_E,all`의 분모는 **같은 1–4 MeV proton impact가 직접 낳은 전자의 kinetic energy**다. 전체 CR injection, primary binding, 다른 proton 창·핵반응·추가 이력은 포함하지 않는다. source coverage는 전자 mesh loop 전에 같은 source constructor로 계산된 기존 기록이다. 새로운 9600 source quadrature를 수행한 것으로 표시하지 않는다.

실제 evaluator 입력 `SOURCE_COVERAGE_RECORD.json`은 PHYS02B R002의 SHA `1f2ebaef…`인 기록이다. 유도에서 인용한 PHYS02C R001은 SHA `36ea4033…`인 별도 원문이다. 검토자는 두 `/coverage` subobject가 저장 소수까지 완전히 같음을 확인했다. 두 whole-file identity를 동일하다고 주장하지 않는다. 이 차이는 코드가 사용한 실제 입력을 밝히기 위한 provenance 사항이며 수치 충돌은 아니다.

영 초기 outside stock, 주어진 cohort kinetic energy 밖에서 에너지를 가져오지 않는 passive deposition 및 고정된 selected response 아래

\[
0\le E_{h,\rm out}\le E_{\rm out},\qquad
E_{\rm out}=\tfrac12\epsilon_{\rm eV}T_{\rm obs}^2
(A_{E,\rm all}-A_{E,\rm sel})
\]

가 성립한다. A2에 대한 에너지 전용 온도 상계는

\[
\Delta T\le (E_h+E_c+E_{\rm out})/C_{V,0}
\]

다. 비음의 초기 온도와 새 thermal 입자수 아래, 입자수 증가가 요구하는 에너지와 열용량 증가를 버리므로 위쪽으로 보수적이다. outside source가 bath를 바꾸어 selected transport까지 달라지는 새로운 coupled history에 이 좁은 상계를 그대로 옮길 수 없다. `E_h`의 양의 하한을 실제 온도 변화의 양의 하한으로 바꾸지도 않는다.

누적 에너지 예산만으로 임의의 순간 power 상계는 얻지 못한다. 과거 stock을 짧게 방출하는 과정이 가능하기 때문이다. 별도 power 상계와 signed source residual 상계에는 stationary, positive, passive response 및 같은 ramp 등의 추가 가정이 필요하다. 후보 유도는 이를 구분한다.

## 6. 실제로 수행한 독립 확인

검토자는 candidate evaluator 또는 역사적 solver를 실행하지 않았다. 원문 읽기와 identity 확인 외에, **새로 설계한 stdlib Fraction reference를 한 번** 실행했다. source와 fixture는 실행 전에 `REFERENCE_PLAN.json`에 해시와 기준을 고정했다.

| 항목 | 실제 결과 |
|---|---|
| 명령 | `python reference_source_binding.py` — 실제 절대 실행 경로는 `REFERENCE_ACTUAL_EXECUTION.json` |
| 독립 reference 실행 수 | 1 |
| 확인 수 | 30/30 PASS |
| 실제 종료 | exit 0, stderr 0 bytes |
| wall time | 0.03056660998845473 s |
| candidate import/실행 | 0 |
| 새 source quadrature / G / transport / pulse / old suite / NCP | 모두 0 |

양의 원자측도 toy에는 0, 2, 3, 10, 15초의 delay를 포함했다. 관측창은 10초이고 두 band의 이미 가중된 heat mass를 직접 사용했다. birth clock을 직접 적분한 결과는 power `49/40`, cumulative heat `2051/400`이며 `q_* H0 R`, `q_* T_obs H0 S/2`와 정확히 같았다. horizon atom은 pulse의 p에는 포함되지만 ramp endpoint/cumulative에 기여하지 않았다. p를 R 대신 쓰거나 band fraction을 다시 곱한 negative control은 다른 값을 주었다.

별도 thermal toy는 number ledger, 실제 cutoff energy, finite heat-capacity denominator와 에너지 항등식을 정확 분수로 확인했다. 열유입이 0인 cold-particle 추가의 온도 변화가 `-40/31 K`인 예를 포함하여 calorimetric 양의 하한의 오용도 구별했다.

실제 저장 기록의 검산은 후보 `H0R/S` 함수를 호출하는 대신 원 pulse의 두 birth `J1/J2`를 합하고 SI scale을 적용했다. 원 paired 기록과의 가장 큰 상대차는 약 `4.09182e-14`로 사전 기준 `1e-12` 안이다. 두 경로는 같은 역사적 원자·source 자료를 공유하므로, 독립성은 단위변환 구현·적분 표현 및 toy oracle에 있다. 물리 입력의 독립 검증으로 세지 않는다. owner의 37개 비교와 최대 `4.49552e-14` 역시 저장된 기록의 일치 기준이지 물리적 uncertainty 인증이 아니다.

owner의 첫 zero-source 검사는 무차원 response fraction까지 dimensional outputs와 합산한 오류였고 원 실패·수정이 보존되어 있다. 최종 A2는 해당 검사 수정과 열적 population 구분을 포함한다. 검토 과정에서 scope·표기 두 곳을 알렸으며 owner는 `T_g,0` 표기와 all-free 항의 미완결 설명만 수정했다. 최종 diff와 manifest를 확인했고 과학 코드·결과·계약은 그대로였다.

## 7. 승인된 결과값과 이후 열린 항목

fullBED/selected_record에서 source endpoint power는 `1.8012625784277353e-42 J m^-3 s^-1`, causal heat power는 `3.4427310257273833e-44 J m^-3 s^-1`, 누적 heat는 `1.1921620918578547e-34 J m^-3`다. heat-only calorimetric 값 `3.7610126365996764e-14 K`와 A2 frozen 값 `3.8418834731514848e-14 K`를 서로 구별한다. A2의 에너지 전용 outside 상계 `1.060170012180312e-12 K`는 위의 source·passivity·selected-response 전제 안에서만 쓴다.

그 값이 작은 것은 지정된 source 시나리오의 진단이다. actual consumer의 관측량·허용오차가 null인 상태에서 모든 scenario의 무관성, CR OFF 선택, full CR history의 완료를 결론내리지 않는다. 다음 단계는 선택한 scenario의 source와 thermal/nonthermal particle accounting, 해당 observable의 tolerance 결속이다. 동일 source·bath에서 추가 과학 실행 없이 재사용할 수 있는 결과는 이번 범위 판정에 따라 사용한다.

다음 gate는 유지한다: REI actual source adoption pending, physical/production history HOLD, PHYS02_DELAY OPEN, F operator binding HOLD, G frontier BLOCKED, atomic G02 UNRESOLVED, all_bound OPEN, b_grid NO_GO. 실제 compiler/CPU/G provenance의 과거 제한도 이 scalar 결속으로 해소되지 않는다.

## 근거 파일

검토자가 직접 읽은 원문·범위·SHA 및 위 SRC 식별자의 정확 경로는 `SOURCE_READ_INVENTORY.json`에 있다. 추가 Git 원문은 `SOURCE_READ_EXECUTIONS.json`의 실제 read-only 명령으로 회수해 `review/sources/`에 보존했다. 전체 NPZ, 모든 과거 raw 실행 및 source 원 논문의 물리 내용을 새로 감사했다고 주장하지 않는다. 배열 identity는 원 source intake와 과거 영수증의 근거를 계승한다.

판정의 기계 판독 정본은 `DECISION.json`, 독립 계산 결과는 `REFERENCE_RESULT.json`, 실제 명령·환경·입력 SHA·stdout/stderr는 `REFERENCE_ACTUAL_EXECUTION.json`이다. `CANDIDATE_IDENTITY_CHECK.json`과 `FINAL_CANDIDATE_IDENTITY_CHECK.json`은 검토 전·최종 후보를 구별한다. 이 identity 기록 자체가 과학적 타당성을 대신하지는 않는다.
