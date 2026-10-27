# C9 최종 독립 코드·반환 결과 검토

## 최종 판정

**PASS_SCOPED — 같은 1회 코드 검토에 실제 C6·C7·C8·C9 결과를 결속했다. Material finding 0건.**

대상은 `CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1`이다. 생산 코드 7개 및 독립 검증기 1개의 현재 bytes가 각 실행의 PRE_EXECUTION 및 EXECUTED_SOURCE와 일치한다. frozen THEORY·CONTRACT·ACCEPTANCE와 input manifest의 해시는 변하지 않았다. 로컬 기반 HEAD는 `b11b2e9255f2b10fb5582376412e045bd1e9151c`, AGENTS SHA256은 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`이다.

예비 검토의 pending 판정은 `C9_CODE_REVIEW_PRELIMINARY.json`, `REVIEW_PRELIMINARY_KO.md`에 원문 그대로 보존했다. 이번 후속 검토는 코드 재검토가 아니라 반환된 자료의 읽기·해시 결속·그림 확인이다.

## 실제 검증 결과

| 근거 | 실제 결과 | 허용치/범위 |
|---|---:|---|
| C6 controls | 36/36 PASS | 새 변경만; 과거 controls replay 0 |
| C7 primary | 8 case, 224 RHS, 24 source 행/exports | 18+5+4+1 열 구성 × 8 |
| 최대 RHS backward residual | 1.1263434346961322e-12 | 2e-12 |
| 최대 partition 잔차 | 8.4980689152303057e-11 | 2e-8 |
| 최대 scaled energy 잔차 | 3.7807871838044604e-11 | 2e-8 |
| 최대 rare-bound 위반 | 0.0 | 5e-10 |
| C8 ordinary grid | 120/120, 최대 1.143893625718921e-4 | 0.005 |
| C8 stable paired grid | 48/48, 최대 3.6363433333349046e-5 | 0.01 |
| C8 upper domain | 84/84, 최대 3.806794429081296e-11 | 1e-5 |
| C9 Decimal70 | 56 RHS/56 own-column 비교 PASS | 두 finest case, 실제 각 2479 nodes |
| C9 최대 열별 상대 차이 | 2.5830073808660872e-11 | 5e-10 |
| C9 coefficient | 10 지점 × 4량, 최대 2.0021283548882073e-15 | 5e-13 |
| C9 source | 6행, 최대 상대 차이 9.4490497178211566e-12 | 5e-10 |

C9 결과에는 실제 754개 scoped check가 모두 통과했고 failure는 0건이다. 생산 코드/provider import와 과거 generator/projection/quadrature/reward 재실행도 0이다. 2개 Decimal CSV 원자료의 크기와 SHA256을 직접 대조했다. 각 CSV는 28개 reference 열과 실제 2479개 행을 갖는다고 반환 자료에 명시되어 있다.

일부 node에서 새 hazard의 binary64 대각합 손실 비율이 1.0인 사실은 그대로 보존한다. 독립 검증은 `Decimal.from_float(K0_diag)+Decimal.from_float(lambda)`로 의도한 합을 구성하여 56개 열을 각각 자기 norm으로 비교했다. 이번 통과는 frozen 유한 사례의 수치 admission이며 연속체·전역 물리 오차 보증이 아니다.

## 그림과 출력의 직접 확인

C8 plot은 저장된 finest source 6행만 사용했고 solver/provider/ODE 호출이 0이었다. root의 실제 PNG 검토 영수증을 읽고 이 검토자도 동일 PNG를 `view_image`로 직접 확인했다. 네 패널과 단위·범례·source z가 보이며 잘린 label을 발견하지 않았다. stored-column response 및 conditional elemental mapping의 범위가 표시되어 있다. PNG·PDF·JSON·CSV의 해시를 검토 영수증과 대조했다.

source rows, integrated exports, C6 controls와 양의 nb event, input manifest, theory, frozen contract, 독립 checker, 두 reference CSV 및 모든 실행 source snapshot의 연결이 모두 일치한다. 전체 객체별 결과와 exact artifact hashes는 `C9_CODE_REVIEW.json`에 보존했다.

## 첫 C9 요청 차단과 비용

C9 v1은 terminal plot이 남긴 owned lease 때문에 **worker 시작 전에 차단**되었다. 실패 영수증의 `child_started=false`, worker CPU 0, coordinator CPU 0.081043861 s를 직접 확인했다. root는 terminal plot PASS/exit0와 정확한 lease hash를 확인한 뒤 해당 lease를 보존 경로로 옮기고 unique v2를 승인했다. 원래 stale 상태의 발생 원인은 확정하지 않았다. failed attempt·retained lease·recovery·authorization을 모두 보존했고 acceptance와 예산은 바꾸지 않았다.

| 비용 항목 | Worker CPU s | Coordinator CPU s |
|---|---:|---:|
| C6 | 0.427652 | 0.052623798 |
| C7 | 1.431108 | 0.123628466 |
| C8 plot | 3.055059 | 0.067896131 |
| C9 v1, preworker 차단 | 0 | 0.081043861 |
| C9 v2 | 1.470165 | 0.057253882 |

Preparation 0.221624387 s를 포함한 누적 비용은 **6.988054525 / 30 CPU-s**다. 영수증별 비용을 Decimal 메타데이터 합산하여 dispatcher 누적값과 nanosecond 표시 자릿수에서 일치함을 확인했다. 과거 허용량 이전은 0이며 원격 provider CPU는 unavailable 상태를 유지한다.

## 독립성과 물리 범위

검토자는 producer 및 Decimal 검증기 작성자와 다르다. 다만 R5 native25 event-map 구성과 C4 환경 조사에 참여했으므로 이 두 기여를 완전히 새로운 독립 유도로 재검증했다고 주장하지 않는다. 별도 R6 및 Decimal 검증을 실제 근거로 사용했다. 검토자가 수행한 과학 실행·테스트·생산 코드 수정·원격 변경은 0이며 재귀 검토와 추가 과학 재실행을 요구하지 않는다.

다음 frozen 범위 원문을 유지한다.

> Conditional elemental-He-to-He4 mapping; stationary heavy target, zero recoil,
nonrelativistic scalar, ground spontaneous only, frozen baths, closed box,
proper seconds. No new stimulated, total/excited, finite-mass or angular model.

> These finite grid/domain comparisons leave global physical error bound null.

> This is an integrated diagnostic return, not a finite coupled abundance update.

C8 범위 원문: `finite preselected grid/domain comparisons, not an interval or continuum error certificate`. C9 범위 원문: `two finest cases, all56 own-column references and six source rows`.

실제 source exports의 nb는 null이고, 양의 nb control만 per-baryon map을 검사한다. Retained photon은 별도 port이며 caloric partition·physical heating·thermal assimilation 완료를 승격하지 않는다. **중앙 DAG 27/88, edge 17; N4/N5 PARTIAL_OPEN; N6/N7 PREDECESSOR_GATED; global completion/error/budget remaining/currency null; L4=false를 유지한다.** 과거 UNKNOWN_NO_ACK와 각 예산은 보존한다.

## Coordinator에 반환할 판정

이 C9 노드의 frozen 수치·코드·시각 검토는 **PASS_SCOPED**로 종료한다. Exact-SHA 게시, source ZIP·이중 백업 및 changed authority readback, 중앙 owner-return 반영은 root 소유 후속 작업이며 본 검토가 이미 완료했다고 주장하지 않는다.
