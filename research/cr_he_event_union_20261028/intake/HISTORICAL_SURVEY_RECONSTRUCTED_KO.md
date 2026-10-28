# 이전 실제 전수조사 관찰의 복원

단위: `CR_PHYS02_HE_EVENT_UNION_V1`. 기록 유형은 `RECONSTRUCTED_FROM_ACTUAL_PRIOR_OBSERVATIONS`이다. 호스트 리셋으로 이전 scratch의 원 tool 응답과 중간 산출물이 사라졌다. 이 문서는 같은 대화에 남은 실제 관찰과 상위 에이전트의 인계를 복원한다. 아래 수치는 이전에 실제 수행한 조회의 범위이며, 현재 시각에 다시 전수 조회했다고 주장하지 않는다. 이 새 문서의 SHA는 새 파일의 identity에만 해당한다. 손실된 원 응답의 SHA나 원본 파일 identity를 꾸며내지 않는다.

## 1. 조사 범위와 종료 조건

이전 전체 목록의 기준 시각은 2026-10-28 06:32:38 KST 부근이며, owner별 후속 확인은 약 06:33:50 KST, REC 원 ZIP 확인은 약 06:36 KST에 이루어졌다. 항목 나열 완료와 모든 파일 본문 독해는 구분한다.

| 표면 | 실제 이전 범위 | 종료·제한 |
|---|---:|---|
| GitHub 접근 가능한 repo catalog | 51 repositories | 접근 가능한 목록에 한정; 개인의 모든 repo를 단정하지 않음 |
| CR 외 50개 repo branch | 2,184 refs | 각 목록 끝까지 페이지 조회 |
| `bass_cr` branch | 189 refs, 100+89 | 2 pages terminal |
| 합계 branch | 2,373 refs | 비동시 스냅샷; 현재 재전수조사 수치 아님 |
| `bass_cr` PR | 111 PR, 100+11 | 2 pages terminal |
| 관련 5 owner PR | 150 PR | selected owner inventory; 모든 본문 독해 아님 |
| Vigilode PR | 10 PR | 별도 조회 |
| Library recent inventory | 821 unique items, 5 pages | 2026-10-25T00:00Z 이후, `next_cursor=null` |
| Dropbox 정확한 parent 직계 목록 | 3,471 unique items, 6 pages | `/BASS_DERIVATION_DOSSIERS_20260912`, `has_more=false` |
| Dropbox CR subtree | 206 items | recursive terminal |
| Dropbox REI subtree | 346 items | recursive terminal |
| Dropbox REC subtree | 245 items | recursive terminal |
| Dropbox WU subtree | 602 items, 2 pages | recursive terminal |
| Dropbox BASS subtree | 304 items | recursive terminal |
| Drive CR / REI / BASS / WU | 188 / 330 / 132 / 635 items | 각 실제 응답의 범위; 전체 Drive inventory는 **PARTIAL** |

Drive는 같은 CR parent에 대해 search 9건과 folder listing 188건이 달랐다. tool 응답에 다음 토큰이 없다는 것만으로 전체 계정이나 모든 backup의 완전 탐색을 주장하지 않는다. 넓은 Dropbox 검색은 오래되거나 관계없는 결과가 섞여 전수조사의 증거로 쓰지 않았다. 관련 없는 비공개 항목명은 이 공개 연구 기록에 복제하지 않는다.

## 2. 개인 대화 접근과 내용 identity

Personal Context의 실제 반환은 “Personal context is unavailable for this conversation.”이었다. 개인 대화 전체를 열거·검색하는 기능은 제공되지 않았다. Pages의 `bass_cr` 검색은 무관한 안내 자료만 돌려주었다. 따라서 `personal_conversation_search=UNAVAILABLE`, `personal_conversation_inventory_complete=false`를 유지한다.

Library의 일부 `read_text` 결과 4개는 마지막 newline 때문에 원 byte size보다 1 byte 작았다. 읽힌 텍스트는 `CONTENT_IDENTITY`로만 취급한다. 원본 download나 complete GET 없이 `BYTE_IDENTITY` 또는 전체 SHA 검증을 주장하지 않는다. 이전 source/closeout의 dual-original-R3는 기존 실제 영수증의 범위대로 재사용하며, 다음 영수증을 삽입하려고 고정 ZIP을 재생성하지 않는다.

## 3. REC Git 단계와 실제 backup 단계의 차이

이전 조사에서 REC native branch의 실제 Git HEAD는 `a21a99cd676671421ff4437f926834ec5e65af07`로 C4 단계였다. 별도로 실제 original full GET으로 다음 C9 backup을 읽었다.

| 필드 | 실제 이전 관찰 |
|---|---|
| ZIP | `REC_H5_NATIVE_PATH_20261028_C9_c905f4c1a128.zip` |
| Dropbox id | `id:BSpOijBcT10AAAAAAEDInw` |
| 크기 | 1,221,320 bytes |
| members | 114, 전체 CRC PASS |
| SHA256 | `c905f4c1a128d05b923f8d87832e37f783670e83018f3dd51aaa7faf546f1940` |
| C9 decision | `PASS_SCOPED`, 19/20; C10 pending |
| source science commit | null |

파일명의 `c905f4c1a128`은 ZIP SHA prefix다. 이것을 Git commit으로 해석한 조회는 422였으며, Git identity로 사용하지 않는다. 원 ZIP은 그때 memory에서 읽었고, 추출된 일부 텍스트와 영수증의 scratch 사본은 리셋으로 손실됐다. 이 문서는 새 원본 GET 또는 새 CRC 검증의 영수증이 아니다.

그 C9 내부 기록은 native capture의 photon 4,680,625 values bitwise, target checks 1,257개 차이 0, 313 queries / 626 endpoints, 7,493 committed rows, controls 18 PASS를 보고했다. Independent review의 추출 SHA `196cadd852e3456e3194cf358fe800c0ccede59f6a0498b8560f464d3a189457`는 내부 decision의 값과 일치했다. 이는 representation/native-reference 계약의 scoped 검증이다. Physical coverage는 **0/313**, 9 physical fields는 null, H6/H7 open, L4 false, REI activation false를 유지한다. C5 및 Git publication 미완료와 C9 backup의 실제 진척을 동시에 기록한다.

REC의 기록된 6 runs는 16.06107697 CPU-s이고, `capture001=UNKNOWN_NOT_ZERO` 및 별도 60 CPU-s allocation charge가 보존된다. 해당 owner의 비용·미지값을 CR allowance에 더하거나 빼지 않는다.

## 4. 이전 과학·문헌·검토 관찰

리셋 전 이 새 CR 단위의 과학 runtime은 0이었다. 새로운 science evaluator를 돌렸다는 기록은 없다. 당시 SciSpace discovery 1회, Exa search 2회와 알려진 primary URL fetch 3회, web lookup 3회가 수행됐고 raw PDF original GET은 0이었다. 각 논문의 읽은 범위는 별도 `PRIMARY_SOURCE_MAP_KO.md`에 적는다. Tool 회수는 실제 당시 관찰의 기록이며 현재 응답의 수량으로 재해석하지 않는다.

Wolfram의 context 자동검색은 `Expand[S+2Pi[1]D] → S` 같은 무관한 결과를 노출했다. 이를 항등식 평가나 증명으로 채택하지 않았고, 해당 시점에서 evaluator 호출은 없었다.

리셋 전 유한 원자 측도 수학은 별도 에이전트 `/root/backup_survey_next`가 `PASS_DERIVED_SCOPED`로 독립 검토했다. 이는 **당시 관찰된 검토**이며 새 복원 파일이나 새 implementation에 대한 C9 합격을 뜻하지 않는다. 실제로 제기됐던 구현 쟁점은 다음과 같다.

- F01: 단순 총합 일치 대신 atomwise exact marginal equality를 검증할 것.
- F02: selected claim 집합을 완전히 검사할 것. 당시 static repair는 관찰됐지만 runtime 검증은 미완료였다.
- F03: 실제 pinned NPZ loader와 독립 fixture의 구별 및 결속이 필요하다.
- F04: 결론의 범위를 유한 원자 nonnegative measure family로 한정할 것. 임의의 연속 측도나 물리적 joint FDCS의 sharpness로 확장하지 않는다.

완결된 수학 내용은 `THEORY_KO.md`에 복원한다. 이 복원은 새 science calculation, 새 독립 review, runtime PASS, Git publication, backup receipt를 대신하지 않는다.

## 5. 재사용과 현재 확인의 경계

전체 2,373 refs를 재조회하는 대신, 이번 복원에서는 관련 7 owner의 최신 branch와 AGENTS·핵심 반환을 새로 조회했다. 새로운 실제 관찰은 `fresh/`에 별도로 보존하고 `CURRENT_OWNER_SUMMARY_KO.md`에서 현재 상태를 종합한다. 변경된 owner의 수학·조건부 model은 출처와 scope가 일치할 때만 재사용한다. 외부 owner의 bath, temperature, n_b, volume, history, rate, budget, completion은 이 CR 단위에 이식하지 않는다.

중앙 completed/total은 당시 28/88이며, 새 실제 확인도 28/88이다. 타 owner의 scoped product 완료나 작업 branch의 33/88을 중앙 수치에 더하지 않는다. `global_physical_completion`, `global_error`, `global_budget_remaining`, `global_currency`는 null이다.
