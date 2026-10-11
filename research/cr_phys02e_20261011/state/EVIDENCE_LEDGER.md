# 증거 장부

| 증거 | 관측 | 지위 |
| --- | --- | --- |
| `research/context/SOURCE_INTAKE.json` + 원본 PR33 반환 | exit1,1G,0pulse,340 one-ULP nodes | 실제 외부 반환, HOLD |
| `research/theory_contribution/DERIVATION_KO.md` | 공통 에너지 좌표와 두 장부 유도 | DERIVED, 부모 코드에 한정 |
| `research/theory_contribution/TOY_CHECK_RECEIPT.json` | Fraction13 identities,exit0,0.028147148s | 해석 예제 검산 |
| `evidence/saved_grid/RUN01.json` | SG01–05,7 tests,exit0,0.678532955s | 준비 구현 검증 |
| `evidence/saved_grid/INPUT_PREFLIGHT_RECEIPT.json` | 두 NPZ와14 배열 identity,무물리 import | 실제 저장 입력 읽기 |
| `evidence/ncp_validation/RUN01.json` | SG06–09,8 tests,exit0,1.139337197s | mock·isolated fixture 검증 |
| `review/INDEPENDENT_DECISION.json` | 최종 독립 판정과 검토 바이트 | 최종 작성 후만 유효 |
| `publication/LOCAL_RESTORE_SMOKE_RECEIPT.json` | 고정 ZIP clean restore + --plan | science freeze 이후 receipt gate |

최초 두 구현 배치에서 실패가 없었고 repair 예산도 사용하지 않았다. 물리 G 생성, pulse, 기존 전체 suite 재실행은 0회다. publication과 로컬 복구 확인은 수치 검증 횟수에 합산하지 않는다.
