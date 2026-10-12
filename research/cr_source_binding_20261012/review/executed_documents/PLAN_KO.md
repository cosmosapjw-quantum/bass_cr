# 실제 source-bound 열·cutoff 원장을 잇는 다음 계획

**BASS_CR의 고정 bath \(\xi=.01\) source binding은 실행 완료다. 다음 과학 작업은 이미 계산한 열·이온화·cutoff 원장을 실제 선택한 scenario에 연결하고, 열적·비열적 입자수와 관측량 허용오차를 정하는 일이다.** REI의 실제 source 채택은 별도 대기 상태이며 전역 RUX 실행 상태는 바꾸지 않는다.

## 1. 완료된 계산과 현재 후보

[실제 결과](results/SOURCE_BOUND_RESPONSE.json)는 \(Q_e(W,t)=tA(W)\), \(t\in[0,T]\), 초기 비열적 stock 0에서
\[
A_E=\int_{0.1\,{\rm eV}}^{900\,{\rm eV}} W A(W)\,dW,\qquad
q_\star=T A_E\,{\rm eV}_{J},
\]
\[
P_{\rm heat}(T)=q_\starH_0R,\qquad
E_{\rm heat}(T)=\frac{q_\starT H_0S}{2}
\]
를 실제 source scale과 결속했다. 기존 fullBED/legacy의 selected_record 및 두 birth tag를 재사용했으며 transport·pulse·source quadrature를 새로 실행하지 않았다.

고정 조건은 \(T=10^{10}\) s, gas 100 K, \(n_H=140\) m⁻³, \(Y_{\rm He}=0.248\), \(\xi=.01\)이다. electron birth 구간은 0.1–10 및 10–900 eV이고, 원 proton collision 구간은 1–4 MeV다. 다음 표는 fullBED/selected_record의 저장값을 표시 자릿수만 줄인 것이다.

| 결과 | 값 |
| --- | ---: |
| \(q_\star\), J m⁻³ s⁻¹ | 1.8012625784277353e−42 |
| endpoint heat power, J m⁻³ s⁻¹ | 3.4427310257273833e−44 |
| cumulative heat, J m⁻³ | 1.1921620918578547e−34 |
| heat만의 고정-\(C_V\) calorimetric \(\Delta T\), K | 3.7610126365996764e−14 |

최신 실행은 **37개 저장 기록의 산술·정규화 비교 PASS**이며 최대 상대차는 약 \(4.50\times10^{-14}\)다. 비교 기준 \(10^{-12}\)는 단위변환 후 기존 수치 기록의 일치 기준이다. source·원자 모형·격자·coupled-history의 물리 오차 예산으로 옮기지 않는다. 최초 zero-source 검사에서 무차원 비율까지 합산한 오류와 수정은 [보존 기록](evidence/attempt01/FAILURE_AND_REPAIR.json)에 남아 있다.

**열적 중요도와 cutoff thermal join은 CANDIDATE_UNDER_REVIEW다.** 같은 결과 JSON의 rows[*].cutoff_thermal_join에 실제 후보 산술이 있으며, 독립 결정은 root가 담당한다. 제안된 경계는
\[
P_{\rm th}=P_{\rm heat}+P_{\rm cut},\qquad
S_{\rm thermal}=S_{\rm cut}
\]
이다. cutoff energy와 number를 열적 bath로 함께 넘기면서 active nonthermal stock을 별도로 남긴다. 이 후보의 frozen-coefficient 산술을 coupled 온도 이력이나 기존 one-temperature receiver의 자동 대체 항으로 부르지 않는다.

## 2. 다음 실행 순서

| 순서 / 노드 | 기존 입력으로 할 일 | 닫을 산출물 |
| --- | --- | --- |
| 1. CR_SCENARIO_SOURCE_BINDING | 계산된 source를 사용할 실제 scenario를 선택한다. proton/electron 범위, amplitude와 이력, clock, 초기 stock, bath, source/process owner가 현재 계산과 같은지 대조한다. | future/SELECTED_CR_SCENARIO_SOURCE.json: 실제 선택과 호환 범위 또는 구체적인 부족 범위 |
| 2. CR_THERMAL_NONTHERMAL_ACCOUNTING | 동일 paired 원장에서 heat·binding·excitation·active stock·cutoff energy/number를 가져와 total/thermal/nonthermal 전자수와 EOS의 소유를 정한다. | future/THERMAL_PARTICLE_ACCOUNTING.json: 아래 입자수 계약 |
| 3. M1_CONSUMER_ERROR_BUDGET | 선택한 관측량·단위와 절대 tolerance, 필요한 상대 tolerance 및 양의 분모를 결속한다. | future/CR_OBSERVABLE_BUDGET.json: 실제 값 또는 해당 소유자가 아직 공급하지 않은 null |
| 조건부. M2_PHYSICAL_CLOSURE_DECISION | 같은 source/bath면 이미 있는 exact response를 사용한다. 다른 이력에는 별도로 유효한 residual/curvature bound를 붙여 선택된 예산과 비교한다. | future/CR_CLOSURE_DECISION.json |
| downstream. M1_REI_SOURCE_ADOPTION | 선택된 source·입자수 계약·예산을 실제 REI call-site/시나리오에 채택한 identity를 receiver 소유자가 기록한다. | future/REI_CR_SOURCE_ADOPTION.json |

검토 중인 cutoff 후보는 1번 scenario 결속과 병행할 수 있다. 후보를 실제 thermal closure로 선택할 때에는 독립 범위 판정을 요구한다. REI의 후속 실제 채택은 BASS_CR의 독립 fixed-bath 연구를 막는 선행조건이 아니다.

### 입자수 계약의 필수 내용

- \(n_{e,\mathrm{total}}\)은 이온화로 생긴 총 전자수이며, \(n_{e,\mathrm{thermal}}\)과 같은 변수로 두지 않는다. 선택 source의 number ledger에서 두 수 사이에 남는 \(N_{\rm active}\)를 명시한다.
- cutoff join을 선택하면 thermal 전자 유입은 \(S_{\rm cut}\), 누적 증가는 \(N_{\rm cut}\)이다. 여전히 active인 전자를 thermal heat capacity에 즉시 포함하지 않는다.
- primary proton birth ionization, 주입된 비열적 전자수, degradation의 secondary ionization을 구분한다. paired energy·ion·cutoff 원장의 동일 source·birth 범위를 사용하고 추가 유출입이 있으면 따로 적는다.
- cutoff의 잔여 에너지를 heat에도 더하고 unresolved stock에도 중복 잔류시키지 않는다. 총 ionization rate를 곧바로 thermal particle source로 대입하지 않는다.
- 고정-\(C_V\) calorimetric 값, cutoff join의 prescribed/frozen-coefficient 온도 응답, 실제 coupled 온도 이력 중 어느 관측량을 쓰는지 선택한 뒤 그 정의에 맞는 tolerance를 정한다.

## 3. 재사용 경계와 보존 gate

[최신 consumer intake](inputs/consumer_intake/INTAKE_KO.md)의 REI PR110 head는 17f8d0daa72e0f76a49cde01b110f650a6688c42로 이전과 같다. 실제 native receiver는 \(\xi=.01,.1\)의 고정 FS10 terminal packet이며, 새 causal source가 자동으로 그 API에 채택된 것은 아니다. 실제 CR-on 관측량·절대/상대 tolerance·분모는 결과 JSON과 DAG 모두 null을 유지한다. 고정 100 K reference thermal energy의 작은 비율만으로 CR OFF나 모든 scenario에서의 무관성을 선택하지 않는다.

M1_ELECTRON_SOURCE_BINDING의 완료 범위는 **BASS_CR executed fixed-bath source**이며, M1_REI_SOURCE_ADOPTION은 **PENDING_DOWNSTREAM_ACTUAL_ADOPTION**이다. [전역 overlay](REI_ATOMIC_REUSE_DAG_CR_OVERLAY_20261012.json)의 모든 RUX 노드는 기존 실행 상태를 유지한다. RUX13_BIND의 소비자 채택·예산 부분도 여전히 열려 있다.

새 H/F/generator/transport/pulse/NCP 실행과 old suite 재실행은 모두 0이다. 이미 수신한 paired energy·ion·cutoff 원장을 재사용한다. M3 국소 OFF는 추가 patch가 필요 없고, 실제 선택 이력의 OFF receipt는 receiver 소유자의 별도 범위다. F operator binding HOLD, G BLOCKED, PHYS02_DELAY OPEN, production history HOLD, atomic G02 UNRESOLVED, all_bound OPEN, b_grid NO_GO를 보존한다. 실제 선택 범위의 부족이 확인될 때만 그 부족을 겨냥한 별도 최소 계약을 만든다.

현재 local DAG는 [NEXT_DAG.json](NEXT_DAG.json)이다. 결과 수치는 source JSON의 원 정밀도를 유지하며, 독립 결정·보고서·루트 entrypoint 갱신은 root가 담당한다.
