# bass_cr 전체 브랜치 72시간 조회 보완

조회시각: 2026-10-20T10:23:11Z. 기준시각: 2026-10-17T09:55:50Z.

REST 목록의 1·2·3페이지(100·63·0행)를 확인해 현재 **163개 브랜치, 160개 고유 head**를 확보했다. 160개 commit metadata를 모두 읽었으며 실패는0개다. 기준시각 이후 head는 **8개**이며, **기존6개 + 이번 대화의 복원본 게시2개**로 구분된다. 시각은 commit의 committer date이며 브랜치 생성/이동 시각은 아니다. 모든 과거 commit·파일 본문을 감사했다는 의미로 확대하지 않는다.

| 구분 | head | 의미 |
|---|---|---|
| 기존 PR80 | 82c71000 | C21E transaction/native bridge 준비 |
| 기존 sibling branch | 7905762c | C21F positive optical-depth reference,24 Python tests |
| 기존 PR81 | 249d9b29 | recovered C21F source/release |
| 기존 PR82 | c4a502e0 | C21F 실제 NCP 실행근거 |
| 기존 PR83 | d780c2c5 | C21F 독립 분석 |
| 기존 PR84 | bf7f7abb | C21G refinement 코드 |
| 이번 대화 PR85 | 51385b92 | 백업에서 복원한 C21H 게시, 새 native 실행0 |
| 이번 대화 PR86 | 1f5eb96d | 백업에서 복원한 C21I 게시, 새 native 실행0 |

추가로 읽은 sibling branch `research/cr-c21f-optical-depth-reference-20261018@7905762c63dcdd40f107ff33e3d19ca26c33bca1`은 PR81과 공통 부모82c71000에서 갈라진 이력이다(compare: ahead3/behind2). 이 branch의 당시 DAG·유도·구현기록·실제 TEST_C5_C6.log를 읽어 **24/24 Python tests,6.24초**를 확인했다. 내용은 photon-number Radau의 내부 음수 iterate 실패를 optical-depth 좌표로 해결하고, 없는 He 변수를 제거하며, 정확한 입력 바이트의 point-evaluator memo와 case별 실패 격리를 구현한 것이다. 당시 Rust/native 실행은 명시적으로 NOT_RUN이다.

이 sibling 기록은 기존 통합표에서 명시되지 않았던 **이전 경량 구현·실패 근거**를 보충한다. 더 새로운 native 계산 결과는 발견하지 않았다. PR81의 후속 복원본·PR82 실제 실행·PR83 분석과 경쟁하는 새 실행으로 집계하지 않으며, C21G/H/I의 남은 native gate를 변경하지 않는다.

전체 공개 metadata와 근거 URL은 BRANCH_INVENTORY_72H.json에 보존했다. 작성자·email·서명 URL은 제외했다. 이 보완 작업에서 외부 수정과 과학 실행은 모두0회다.

