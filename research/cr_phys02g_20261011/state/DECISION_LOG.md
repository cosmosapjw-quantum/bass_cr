# PHYS02G 후속 결정 기록

작성 시각: 2026-10-11T07:01:02.114170+00:00

## 판정 바인딩

독립 판정 `review/INDEPENDENT_DECISION.json`의 `PASS_SCOPED`를 root가 고정된 범위에서 채택했다. 실제 SHA-256은 `9dd9c623fdd881667b6692ea8c3c9fbac08d545ba821fe33f66c2dbd38322002`이다. 과학 계약 SHA-256은 `517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832`이며 계약, 구현, 테스트 기준과 원래 결과는 변경하지 않았다.

이 기록과 `NEXT_DAG.json`, `RESEARCH_STATE.json`은 독립 판정 후 허용된 상태 바인딩이다. 이 세 파일 자체가 독립 심사를 받았다고 주장하지 않는다. 게시와 최종 P01 판단은 root의 업무다.

## 채택 범위

채택 범위는 `DERIVED` 수학 부등식, 저장된 FP64 moment 및 envelope의 `NUMERICALLY_CHECKED` 평가, 그리고 `PREPARED_NOT_EXECUTED` frontier 준비다. exact Fraction 후보 toy는 1회, 저장된 두 모델 분석은 1회, 독립 검토자의 저장 결과 산술 비교는 1회 수행되었다. 세 실행은 실제 exit 0이며 원시 로그와 영수증을 보존한다. 새로운 G 생성, linear solve, pulse, expm은 모두 0회다. 실제 frontier 실행과 예약도 0회다.

저장 분석의 Decimal80 확인은 모델별 2,077개이며, 검토자는 producer 모듈을 import하거나 분석을 재실행하지 않고 3,936개 curve 값과 10개 끝점 구간을 독립 비교했다. 산술 일치는 입력 물리 오차, fixed-bath 유효성, 연속 극한이나 directed-rounding 인증을 뜻하지 않는다.

## G-R01: 끝점 산술의 주장 제한

원래 저장된 horizon 구간 10개 모두에서 작업 FP64 끝점 조건은 성립한다. 검토자는 소스의 십진 토큰과 표시된 fraction을 exact Fraction으로 계산했을 때 8개 구간에서 적어도 하나의 끝점 부등호가 반대로 나타남을 확인했다. 해당 확률 여유는 약 `1e-17`이다. 근거는 `review/REVIEW_SAVED_ARITHMETIC_RESULT.json`이며 SHA-256은 `339a0dc525235dc4f2b83692e53aecb0bae6de37aeeb849bdddccdc7cd3ab12e`이다.

원시 끝점 쌍은 exact-decimal 또는 exact-input 수치 포괄 구간으로 인증하지 않는다. directed rounding을 수행하지 않았고 forward-error 구간이나 물리 불확실성 구간도 아니다. 이 차이에서 물리 모델 차이를 추론하지 않는다. 원래 결과와 허용오차를 유지하며 새로운 분석 실행이나 값 보정을 하지 않는다. 판정은 고정된 FP64 확인 범위의 `PASS_SCOPED`다.

## 실패 및 수정 이력

저장 분석의 첫 targeted run은 합성 second moment의 잘못된 기대값 때문에 exit 1이었다. 계약식의 값은 `(24 - 8 + 0.95) / 0.8 = 21.1875`인데 테스트가 `20.5625`를 기대했다. 승인된 한 번의 수정에서 테스트 기대값만 고쳤고 고정 허용오차를 유지했다. 이후 7개 테스트가 exit 0으로 통과했다. 실제 저장 분석은 수정 이후 정확히 1회 수행했으며 재실행하지 않았다. 첫 stdout, stderr와 영수증을 남겼다.

NCP 준비의 conformance 명령은 ops 4개가 통과했으나 frontier 4개는 source 경로 등록 전 import 때문에 평가되지 않아 exit 1이었다. 승인된 import 순서 수정 이후 영향받은 frontier 4개만 exit 0으로 통과했다. ops는 다시 실행하지 않았다. 원래 준비 증거, 수정 전 snapshot, 최초 실패와 수정 영수증을 보존한다. 합성 자식 실패 및 deadline 증거는 실제 F 또는 G frontier 실행 실패로 집계하지 않는다.

## 다음 DAG와 실행 권한

`CR-PHYS02G-NCP-FRONTIER-ENVELOPE`는 `WAITING_FOR_F_ACTUAL_RETURN`이다. 준비 판정은 `PASS_SCOPED`, `consumed`는 `false`, 최대 postprocess 실행은 1회, wall 한도는 90초이며 G, linear solve, pulse, expm 허용 호출은 모두 0회다. 실제 review 경로와 해시는 DAG에 바인딩한다.

현재 관측 소스와 조회한 백업에서 실제 F 반환은 발견되지 않았다. 조회 범위는 최신 PR 10개, branch 101개, 잘리지 않은 tree 6,346개 항목 및 기록된 백업 폴더 검색이다. 관측 범위의 부재는 다른 호스트에서 미게시 실행이 없다는 증명이 아니다. F의 전역 예약, 실행 및 현재 예산 소모 상태는 `UNKNOWN`이다. 게시된 이전 F `READY`와 `consumed=false`는 당시 준비 기록이다. G는 새 F 실행 또는 재시도 예산을 만들지 않는다.

다음 작업은 실제 NCP 호스트의 기존 F 예약, 실행, 완료와 반환을 확인하는 것이다. 이미 실행 중이면 기존 실행을 기다린다. 완료되었으면 기존 family를 사용한다. 실패 또는 소모된 실행을 새로운 허가 없이 재시도하지 않는다. 실제 F family admission과 9,600-state G runtime은 아직 수행하거나 측정하지 않았다. 실제 F와 실제 G 출력에는 새로운 범위의 독립 심사가 필요하다.

P01은 `PENDING_FINAL_PUBLICATION_GATE`다. 실제 G 과학 커밋과 최종 ZIP 생성 후 전체 외부 엔트리 및 해시 검증, 새 디렉터리 복원과 표준 라이브러리 missing-F plan을 수행해야 한다. 예상 결과는 `WAITING_FOR_F_ACTUAL_RETURN`이며 준비 소스 admission은 `PREPARED_SOURCE_ADMITTED`여야 한다. 이 기록 시점에는 freeze, prepare-git, bundle, 복원 또는 plan을 실행하지 않았다.

## 소스, 하네스와 모델 메타데이터

기준 repository는 `cosmosapjw-quantum/bass_cr`이며 기준 commit은 `b21009893b93ed9b7e4af22ac4f480fe4b8e5c4b`, tree는 `63cd76b80393f3d9c506dec7c80eda8925df39e3`다. 현재 소스 기록은 draft PR36과 publication-only 후속 소스를 관측한 범위에 한정된다. 바이트 해시는 의미의 동등성, 과학적 정확성 또는 전역 실행 부재를 증명하지 않는다.

기존 canonical Astra v4.0.0 프로젝트 흐름을 유지한다. 연구 하네스 SHA-256은 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`, 코딩 하네스 SHA-256은 `dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a`다. developer 관측 label은 `GPT-6 Astra Pro`이지만 정확한 router alias는 `MODEL_UNRESOLVED`다. Pro 접미사를 새 alias로 만들지 않는다. 하위 구현 요청 backend는 `gpt-6.1-sol`이며 독립 backend 확인은 없다. `source-bound research/context/ASTRA_TIER_ROUTING_POLICY.md; lower implementation, independent Astra review`에 따라 이론, 계약, 판정은 Astra 역할이며 고정 계약 구현과 상태 조립은 하위 역할이다. 비용 또는 성능 주장은 하지 않는다.

## 상속 gate

| Gate | 유지 상태 |
|---|---|
| PHYS02_DELAY | OPEN |
| production_history | HOLD |
| atomic_G02 | UNRESOLVED |
| b_grid | NO_GO |
| all_bound | OPEN |
| R17B2B | NO_CERTIFIED_SOURCE_SHARPENING |
| CCC_2026_exporter_identity | SOURCE_IDENTITY_UNRESOLVED |

위 gate를 종료하거나 완화하지 않는다. fixed finite operator continuation은 조건부이며 장시간 fixed bath 유효성은 미해결이다. envelope 중첩으로 두 underlying kernel이 같다고 판단하지 않는다.
