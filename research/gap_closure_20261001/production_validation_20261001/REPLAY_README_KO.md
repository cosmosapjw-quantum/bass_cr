# R4V 재개 및 증거 사용 안내

이 패키지는 R4U의 검증된 복구 원본과 R4V에서 실제 완료한 계산을 함께 보존한다. `MANIFEST.json`은 ZIP 안의 각 파일의 경로·크기·SHA256을 기록한다. 원본 R4U ZIP의 SHA256은 `f3ebd034b795751235c154f56c5e69bb75953fef8d3d94e34b7e96defa867a69`이다.

| 경로 | 내용 |
| --- | --- |
| `base/` | 이전 R4U ZIP: 원래 요구사항72개 감사,11개 SQLite 버전 조사,기존 solver·복구 증거 |
| `source/` | R4U 기반 선택적 소스와 R4V 구현·계약·검토 요약 |
| `runtime_inputs/`, `native_build_portable/` | 실제 계산에 사용한 입력과 엄격한 FP64 native binaries |
| `runs_r4v/` | G02/G03/G12 실행 계획,raw reservations,qualified arrays,종료 영수증,분석 결과 |
| `recovery_r4v/` | 복구 감사와 독립 구현·과학·실행 검토 |
| `reports/` | 한국어 보고서,진단 그림·CSV,DBv8와 DB 검증 |

`G02_BATCH_PLAN.json`과 최초 `G12_BATCH_PLAN.json`은 실행하지 않은 이전 계획이다. 실제 실행은 각각 `*_BATCH_PLAN_V2.json`이다. 변경 전 orphan 결함의 실패 증거도 보존되어 있다. 실패 기록이나 미사용 계획을 완료된 물리 계산으로 집계하지 않는다.

실행 계획에는 당시의 절대경로·소스·입력·native 파일·호스트 자원과 exact float time이 묶여 있다. 이동한 경로로 과거 계획을 고쳐서 승인이나 캐시 문맥이 유지된다고 취급하지 않는다. 다음 실행은 현재 파일 및 호스트 자원으로 새 계획을 만들고, 소비하지 않은 별도 예산과 출력 경로를 사용해야 한다. 현재 환경은8 CPU quota/8GiB이며64코어 NCP 실행 증거가 아니다. 보관된 native library를 다른 호스트에서 사용하기 전 호환성과 identity 검증이 필요하다.

완료한 수치 결과는 `runs_r4v/G02_RESULT.json`, `G02_RICHARDSON_RESULT.json`, `G03_ANALYSIS/G03_RESULT.json`, `G12_ANALYSIS/RESULT.json`에 있다. 새 물리 계산 없이 독립 검토와 결과 확인을 우선한다. 기존 R4U43 tests를 재실행한 것으로 집계하지 않는다.

DBv8에서는 과거38개 테이블과 행을 보존한다. 최신 연구 상태는 `current_research_gap_status` view에서 읽는다. 과거 `research_gap_status`의 내용은 이력이며 최신 상태로 덮어쓰지 않았다. 추가 증거의 파일 identity는 `continuation_evidence`, G02/G03/G12의 최신 해석은 `continuation_scientific_status`에 있다.

과학적 상태는 production HOLD, capture=false, all_bound OPEN, b-grid NO_GO이다. G02 raw FD 목표는 미달이며 Richardson 결과는 보조 관찰이다. G03의 경험적 외삽 적합성과 G12의 짧은 국소 비교는 연속 구간 오차 상계나 전체 산란 창의 정확성을 증명하지 않는다. 다음 단계와 남은 원래 연구 항목은 한국어 연구 보고서에 정리했다.
