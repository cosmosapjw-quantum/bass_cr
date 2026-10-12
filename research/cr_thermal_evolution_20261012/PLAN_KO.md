# BASS_CR 이론 연구계획: 열적 진화와 충돌 시계의 연결

현재 단위는 **CR-THEORY-THERMAL-EVOLUTION-20261012**다. 사용자가 명시한 이론 연구 요청에 따라 고정 배경의 A2 cutoff 편입 결과에서 출발해, 움직이는 분할면·all-free 회계·진화 배경에서의 연산자 재사용을 구성했다. 통합 채택 상태는 **PROMOTE_SCOPED**다. 독립 판정 review/DECISION.json에서 TH1–TH7을 명시된 가정 아래 승인했으며, 다음 이론 노드는 READY로 갱신했다.

## 이번에 구성한 결과

| 결과 | 실제 유도·구현과 근거 |
|---|---|
| 움직이는 cutoff | derivations/MOVING_CUTOFF_KO.md: MC13의 일반 모멘트식, MC20의 내부 이관 상쇄, daughter 실제 에너지, Bianchi stress work, source ghost 대응 |
| thermal–all-free 회계의 동치 | derivations/THERMAL_EXCESS_KO.md: T.7–T.11의 active 기준에너지·stress와 열용량 결합, primary birth·secondary ionization 회계 |
| 정확한 충돌 시계와 Coulomb 보정 | derivations/COLLISION_CLOCK_KO.md: CC1–CC2의 부피·시간 변환, 식 3.5의 고정 행렬 보정, 실제 PHYS02 계수의 정의역 |
| residual에서 온도까지의 상계 | CC3–CC5의 양의 에너지·Duhamel 상계와 T.17–T.22의 누적 침적 → 팽창 후 thermal energy/count → temperature 사상 |
| 가벼운 receiver 구현 | receiver_interface.py: transfer·total moment·comoving packet EOS·temperature error의 네 함수, 정확한 Fraction 연산 지원 |
| 판별 검산 | results/THEORY_CHECKS.json: **15/15 PASS**. 해석 예제, 기존 함수에서 추출한 stopping 계수, 한 개의 무차원 비가환 cascade를 사용한 실제 실행 |

계산은 0.0168초였고 새 full generator나 원격 과학 실행은 0회다. 검산은 birth만 있는 경우의 온도 보존, 입자 편입과 역이관, 단열 팽창, energy/count 오차 상계, 전단 일, 실제 Coulomb 밀도항, 비가환 residual 전달을 구별한다. 두 단계 cascade의 후보 저자 Wolfram 기호 검산도 21/21 PASS다. 독립 검토자는 각 유도문과 실제 결과를 읽고 별도 해석으로 심사했으며 검산 재실행은 0회다.

## 바로 다음 이론 작업: T·조성 피드백을 포함한 양의 보존 step

다음 노드는 **CR_THEORY_SELF_CONSISTENT_FEEDBACK**이다. 이번에 분리한 고정 event 행렬과 시간 변화 계수를 사용하여, 온도와 H/He 조성이 충돌률을 바꾸는 구간의 한 step을 실제 구성한다.

1. **동일 사건으로 수·에너지를 갱신하는 상태를 정한다.** Active energy vector, thermal count·energy, H/He 종별 population을 함께 두고, 각 사건의 고정 행렬과 계수로 generator를 쓴다. 같은 사건의 전자 생성·원자 내부에너지·열·cutoff 이관을 한 번씩 배정한다.
2. **계수를 고정한 한 step의 양성과 보존을 증명한다.** 비음이 아닌 반응률의 정의역에서 선택한 전파법이 population과 에너지를 보존하고 양의 상태를 유지하는 조건을 유도한다. Comoving thermal energy/count를 갱신한 뒤 EOS를 역으로 푼다.
3. **T·조성 갱신과 계수 평가를 닫는다.** 해당 step의 implicit 또는 반복 갱신을 구성하고, 반응률의 국소 변화율로 존재·수렴·양성 조건을 얻는다. 현재 coefficient residual과 온도 오차 사상을 이용해 step 길이 또는 반복 종료 기준을 정한다.

완료 산출물은 한 개의 명시적 보존 step, 그 조건을 갖춘 증명, 입력·출력과 판별 예제를 담은 구현 계약이다. 먼저 주어진 배경과 분할면에서 구성하고, 온도에 의존하는 cutoff에는 이번 implicit boundary 식을 연결한다.

## 실제 scenario에 적용하는 경로

실제 적용은 기존 **CR_SCENARIO_SOURCE_BINDING → CR_THERMAL_NONTHERMAL_ACCOUNTING → M1_CONSUMER_ERROR_BUDGET → M1_REI_SOURCE_ADOPTION** 경로에 둔다. 그 경로에서는 source와 시간 원점·초기 stock·배경, thermal/active 정의, 관측량과 허용오차를 실제 선택 자료에 연결한다. 이번 명시적 이론 요청은 일반 유도와 구성의 실행 근거이며, scenario의 수치 예산은 해당 적용 단계에서 사용한다.

## 보존한 근거와 DAG

NEXT_DAG.json은 이전 **22개 local node 객체**와 원 global overlay의 **19개 node를 포함한 전체 객체**를 그대로 보존하고, 새 이론·검산·후속 작업 8개 노드를 추가한다. Local graph는 30개 노드·53개 의존 간선이며 순환이 없다. 기존 node의 경로는 이전 과학 commit 아래의 원 연구 단위를 기준으로 해석하도록 명시했다.

이전 source ZIP의 확인된 SHA-256은 `632995c3926a738878e4268ec1993817e40062fe84161d39200e21155957f301`, 과학 commit은 `5fc11143679fe1950133b1e268ac3dd248f6429b`다. 복구 기록은 inputs/RECOVERY.json, 원 local DAG는 inputs/prior/NEXT_DAG.json, 원 global overlay 전체는 새 DAG의 global_overlay_snapshot에 있다. 각각의 원문 hash와 node 객체의 보존 확인은 NEXT_DAG.json의 preservation에 기록했다.
