# BASS_CR 다음 연구계획: 실제 kernel과 온도 cutoff

현재 단위는 CR-THEORY-KERNEL-CUTOFF-20261013이다. 직전 DAG에서 READY였던 실제 kernel 사건 adapter와 temperature-dependent cutoff 두 노드의 구성을 완료했다. 범위별 최종 판정은 RESULTS.json과 review/DECISION.json을 따른다.

## 이번에 확보한 연결

실제 저장된 9600-grid와 PHYS02C/PHYS02B source를 양의 사건 열에 결속했다. 같은 parent와 target family의 daughter sharing은 shared-capacity denominator 아래에서 유지된다. Thermal cutoff에는 같은 fixed inventory의 유한 count·energy 분할을 사용하고, 연속 root 또는 retained atomic prefix로 실제 계산 경로를 제공했다. Covariant 경계식과 CP.1–15가 이를 온도·전자밀도·조성 feedback에 연결한다.

## 다음 두 이론 구성

1. **CR_THEORY_COUPLED_BRANCH_SOLVER.** 실제 source-pinned HI/HeI subfamily에서 raw reaction inventory와 cutoff root를 함께 갱신한다. 우선 threshold에서 떨어진 한 branch에 uniform root bracket, positive capacity, CP.12의 q 및 residual budget을 구성한다. 다음으로 reactions가 atom weights를 바꿀 때 한 crossing을 보존적으로 연결하고 root 선택 규칙을 명시한다. 큰 parameter sweep은 선행 조건이 아니다.
2. **CR_THEORY_GEOMETRY_KERNEL_REBIND.** 기존 prescribed Bianchi stage 뒤의 actual parent energies를 사용하여 daughter projection과 rate domain을 다시 결속한다. 한 energy trajectory와 한 source family부터 시작해 threshold, lower trace, geometry work와 cutoff source의 장부 및 representation error를 계산한다.

두 작업의 입력은 이번 derivations, reference 구현, 정확한 원본 source와 저장된 grid다. 같은 근거를 다시 찾거나 이전 suite를 반복하지 않는다. 새 energy/domain/representation을 사용할 때 바뀐 의존성을 검증한다.

## 선택 응용

CR_FEEDBACK_SELECTED_APPLICATION은 기존 source/scenario와 관측량 예산 의존성을 유지한다. 실제 source history, chi/cutoff domain, thermal ownership 및 관측량 단위·절대/상대 허용오차를 그 노드에서 결속한다. 일반 이론의 다음 구성을 이 미정 응용 입력 때문에 중단하지 않는다.

현재 standalone 결과는 물리적 전체 history, 추가 HeII/재결합 rate, finite-temperature stopping 또는 전체 27-table generation을 대신하지 않는다. 해당 대상이 선택되면 원래 input/domain 계약을 가진 별도 node로 진행한다.

## 재개 자료

먼저 HANDOFF.json, RESULTS.json, NEXT_DAG.json, CONTRACT.json, review/DECISION.json을 읽는다. 분기 구조의 기계 판독본은 NEXT_DAG.json이며 원래 consumer budget과 과학 gates를 보존한다. LaTeX/PDF에는 전체 유도와 실제 검산을 담았다.
