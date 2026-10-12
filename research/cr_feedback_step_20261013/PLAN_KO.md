# BASS_CR: feedback 이론 이후의 연구계획

연구 단위: CR-THEORY-FEEDBACK-20261013. 기준일: 2026-10-13 Asia/Seoul.

이번 루프에서 공통 사건 extent에 의한 H/He·active 전자·thermal gas의 유한 보존 step, 온도·조성 계수의 자기일관 갱신, 반복 및 물리 endpoint 오차의 온도 전달을 구성했다. 공변 모멘트와 주어진 Bianchi I 팽창의 연결도 같은 수·에너지 장부로 닫았다. 다음 연구는 이 식들을 실제 kernel 및 온도 의존 cutoff에 연결하는 두 유도로 진행한다.

## 완료된 연결

- 사건별 핵수·전하·에너지 열과 하나의 extent를 사용해 모든 소비 재고의 비음성을 보존한다.
- 보존된 핵수에서 thermal count 하한을 얻고, 온도·전자밀도 domain과 step 조건을 계산해 비선형 계수를 평가한다.
- 계수·EOS의 상계로 수렴상수 q를 구성한다. 공급된 q와 domain을 사용하는 bounded Picard driver는 실제 residual과 온도 certificate를 반환한다.
- 실제 연속 반응식에 대한 endpoint rate defect는 이산 fixed-point residual과 별도로 평가한다.
- 주어진 Bianchi I 기하에서 momentum, thermal energy와 pressure work를 일관되게 이동시킨다.

기존 가정과 적용범위는 derivations/FEEDBACK_ASSUMPTIONS.json, 오차 전달은 derivations/FEEDBACK_ERROR_MAP.json, 최종 판정의 식별자는 NEXT_DAG.json의 acceptance_update에 결속한다.

## 바로 시작할 이론 연구

| 우선순위 | 다음 노드 | 첫 구성과 완료 기준 |
|---|---|---|
| 1 | CR_THEORY_KERNEL_EVENT_ADAPTER | 실제로 고정된 electron energy-grid 행과 daughter kernel을 선택한다. 부모·daughter·threshold·heat·number 모멘트를 맞추는 비음 사건 가중치를 구성하고, thermal/composition domain의 rate 미분 상계를 계산해 현재 capacity map과 driver에 연결한다. |
| 2 — 병행 가능 | CR_THEORY_THERMAL_CUTOFF_FEEDBACK | E_c(T)=chi k_B T를 retained moving-cutoff flux에 넣고 경계 이동의 shape derivative를 전개한다. 실제 경계 수·에너지 전달과 EOS를 함께 사용하는 정칙 implicit thermal update 및 그 국소 수렴 조건을 구성한다. |

두 노드는 명시된 가정 아래에서 실제 유도부터 시작할 수 있다. 첫 노드에서는 새 물리 kernel을 대량 계산하기에 앞서 기존 kernel의 사건 분해와 선택된 자료의 단위·모멘트를 연결한다. 두 번째에서는 cutoff 경계값과 전달 방향을 고정하고 온도 미분항을 직접 계산한다.

## 선택된 물리 이력에 적용하는 단계

CR_FEEDBACK_SELECTED_APPLICATION은 다음 네 의존성을 사용한다.

1. 완료된 CR_THEORY_SELF_CONSISTENT_FEEDBACK.
2. 실제 kernel에 연결된 CR_THEORY_KERNEL_EVENT_ADAPTER.
3. CR_SCENARIO_SOURCE_BINDING의 실제 source·시간 이력·배경·초기상태와 식별자.
4. M1_CONSUMER_ERROR_BUDGET의 관측량·단위·허용오차와 유효한 상대오차 분모.

실제 source/history와 관측량 budget이 선택되면 사건 계수 domain, 시간 step 및 iteration tolerance를 해당 값에 맞춰 계산한다. 현재 소비자 budget의 비어 있는 필드와 원래의 물리 실행 gate는 기존 기록을 유지한다.

## 재개에 필요한 파일

- NEXT_DAG.json: 선택 노드의 완료와 새 의존성.
- derivations/EVENT_STEP_DERIVATION_KO.md: 실제 kernel이 맞춰야 할 사건·에너지·수 계약.
- derivations/FEEDBACK_THEOREMS_KO.md: domain, 수렴, 일차 일관성, endpoint 온도 certificate.
- derivations/COVARIANT_GEOMETRY_KO.md: 공변 모멘트와 기하 substep의 정의·정확도 조건.
- event_capacity_step.py, feedback_solver.py: 지금 완성된 참조 구현.
- inputs/prior/derivations/MOVING_CUTOFF_KO.md: 온도 의존 cutoff를 시작할 경계 수지.

원래 source 단위의 22개 노드와 직전 thermal-evolution 단위의 7개 완료 노드는 각 원 commit의 상대경로로 읽는다. 현재 완료한 feedback 노드와 새 3개 노드의 경로는 이번 단위에 속한다. 원래 READY 객체와 이전 preservation 기록은 inputs/prior/NEXT_DAG.json 및 현재 DAG의 historical 필드에 보존한다.
