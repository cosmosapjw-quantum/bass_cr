**PASS — 고정 h=.20, 100 keV/u, b=2의 선택 span P1/P2/P3 시간오차 추정에 한정합니다. 이를 차단하는 BLOCKER/MAJOR는 발견하지 못했습니다.** Production **HOLD**, all-bound **OPEN**, b-grid **NO_GO**는 유지해야 합니다.

- 지정 HEAD `41ba35c6…`, 계약 SHA `d2ed93ef…`, config·수치 source·실행 helper hash가 일치했습니다. B0–B2 원자료에서 재구성한 forecast도 고정 payload와 정확히 일치했습니다.
- 외부 preparation **1회**, 첫 chunk의 내부 재준비·v2 witness **1회**, 전체 collision **1개**를 확인했습니다. `56×128+4=7172` steps, **57개 frontier**, **116개 명령 영수증**의 argv·성공 상태·seal·runtime 연결이 일치합니다. 약 **57.46GB** generation 파일을 직접 재해시했고 불일치는 없었습니다. [실행 감사](/home/cosmosapjw/Dropbox/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/results/R3M27/RUNTIME_AUDIT.json:1)
- coordinator의 기존 테스트 3개를 파일 생성 없이 실행해 통과했고, temporal·Decimal budget 평가도 저장 결과와 정확히 일치했습니다.

| 채널 | B3 관측값 | B2→B3 상대차 | U_time/B3 |
|---|---:|---:|---:|
| P1 | 0.006089329814 | 0.067142% | 0.062533% |
| P2 | 0.007586698170 | 0.062743% | 0.055982% |
| P3 | 0.008089219135 | 0.062169% | 0.054581% |

모두 같은 부호이며 fine 증분 수축비는 **0.2411–0.2425**입니다. 네 limit 모델과 세 사전 forecast로 `U_time=2 max(E_model,D_hold)`를 재계산했고 모두 **0.10% 이하**였습니다. 세 채널 모두 `D_hold`가 지배합니다. Held-out은 새 B3 **한 점**이며, LOO와 관측차수는 진단이지 독립 검증점 추가나 엄밀한 오차상한이 아닙니다. [고정 판정 규칙](/home/cosmosapjw/Dropbox/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/docs/r3m26/NUMERICAL_STRATEGY_KO.md:90)

**MINOR — 출처 메타데이터 수정 필요:** [ledger 143행](/home/cosmosapjw/Dropbox/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/results/R3M27/CURRENT_SELECTED_P3_LEDGER.json:143)의 `ERROR_BUDGET.json` SHA `85f93a7b…`는 구 `90d6cbad…` 버전입니다. 선언된 base `e32f6286…`의 SHA는 `d50e72cb87505f16e3245865cdb2cf84c0ad4bf85bf9cf1476b9c83d72677829`입니다. 최소 수정은 **참조 commit과 해당 SHA를 함께 명시**하는 것입니다. 출처 연결 오류이며, 확인된 temporal 수치의 실패나 재전파 사유는 아닙니다.

Ledger의 `FULL_COMPONENT`는 **고정 h·선택 span에서 전체 trajectory의 시간 성분**에만 타당합니다. 공간·`h_dt`는 raw difference로 미승인이고 준비·경계는 미측정이므로 총합 `null`, `NUMERICAL_BUDGET_OPEN`이 정확합니다. [ledger](/home/cosmosapjw/Dropbox/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/results/R3M27/CURRENT_SELECTED_P3_LEDGER.json:43)

이번 독립 재해시는 저장 바이트와 영수증의 연결을 확인했습니다. **Endpoint 전파나 Gram projection을 독립 재계산한 것은 아닙니다.** 파일 수정·새 전파·외부 검색은 수행하지 않았습니다.

