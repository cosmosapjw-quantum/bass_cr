# 현재 연구 상태 — CR-PHYS02D

## 물리 질문과 현재 근거

완료된 ramp의 현재 열률과 누적 열에서 무엇을 알 수 있는지 분리했다. \(R=E[X],S=E[X^2]\), \(X=(1-\tau/T)_+\)를 유도하고 clipped moments, 현재 열의 원천 주입 나이, pulse CDF의 유한시간 경계를 얻었다. Uncapped mean은 두 endpoint만으로 식별되지 않는다.

실제 저장값 분석은 한 번 수행했다. 여섯 selected-total 모멘트 행 및 18개 birth-tag 나이 행은 `evidence/endpoint/RESULT.json`이다. 첫 process exit1은 CSV export 단계에서 발생했으며 계산 결과는 이미 보존되어 있었다. 저장값에서만 export를 복구했고 이후 이산 CDF 그림도 수정했다. 원래 실패와 수정 영수증이 모두 남아 있다.

실제 기준 base는 PR31 `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31`이다. PR30의 두 9,600점 ramp 수송은 실제 exit0으로 이미 완료되었다. 그 과거 계산을 이번 실행으로 재표기하지 않는다.

## 다음 작업

`CR-PHYS02D-NCP-PULSE-RESPONSE`: 같은 `(3200,6400)` 격자, fullBED 다음 legacy, 두 source birth 열 동시 전파, 17개 시간, 최대 새 G2/pulse2, 전체 wall3600s. 작은 해석·운영 검사는 수행되었으며 실제 물리 실행은 **NOT_EXECUTED**다.

최종 독립 과학 판정은 `../review/INDEPENDENT_DECISION.json`, 그 판정에 따른 실행 가능 상태는 `NEXT_DAG.json`을 따른다. 이 문서는 owner의 자기 승격 판정이 아니다.

## 보존한 경계

`PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`, `CCC SOURCE_IDENTITY_UNRESOLVED`.

이번 모멘트는 고정 모델의 에너지 열 방출 지연에 관한 것이다. 입자 수명, 실제 우주론 장기 이력, 전체 원자 완전성 또는 NCP64 scaling으로 확대하지 않는다. 격자 전환과 numerical runtime 전환은 구분해 보고한다.
