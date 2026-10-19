# physmath-research-loop 실행 기록

본 루프는 C21F 후속 연구다. 시작 시 최신 실행이 없는 것으로 가정하지 않고 실제 PR81·PR82 및 백업을 확인했다. 원래 구현·복구·56 tests·native 실행은 기존 근거로 재사용하고, 새 native 원자료의 판별 분석과 구성적 유도를 수행했다.

## 이론 연구 루프

| 단계 | 실제 작업과 결과 | 증거·완료 상태 |
|---|---|---|
| R1 연구 위치·계약 | PR81 실행 f8359232, 문서 249d9, PR82 c4a502e0, native owner 고정. 두 짧은 fixed fixtures만 평가 | README_KO §2–4, intake receipt; 완료 |
| R2 근거·재사용 | 17개 executable files와 새 raw text 167개의 identity 확인. 기존 Python 검사 56개·Rust 검사 3개·native histories 24개 실행 채택 | inputs/, intake 및 PR82 raw; 완료 |
| R3 주장·전제 정렬 | 실행 성공, 물리 수지, 시간 수렴, reference 정확도를 분리. Global EoR gates 유지 | README_KO §3–7; 완료 |
| R4 가설·표현 탐색 | Hybrid 높은 p의 원인을 signed thermal cancellation·active norm component 전환으로 검토. Radau를 소거하는 HYB−FULL 차분 선택 | results/thermal_cancellation.csv; 완료 |
| R5 구성적 유도 | Frozen cell에서 h²/2 DgM(Pg+M) local gas defect 유도. Photo feedback과 geometry/event 전제 명시 | INDEPENDENT_REVIEW_KO §6; derived 완료 |
| R6 독립 검증 | 별도 원시 SUMMARY/fixture/Radau 계산, 2,160개 step의 저장 residual normalization과 최대 budget raw point 5개 재검산 | INDEPENDENT_REVIEW_KO §9; 완료 |
| R7 판별 검증 | Signed errors, reference-free differences, n*d_n 안정화, 부호전환, 지배 성분 전환. 부적합 crossing fit 기각 | results/, figures/; numerically checked 완료 |
| R8 결과 판정 | FULLMID의 scoped 2차 경향 채택, hybrid comparator 유지. 절대오차 인증·특수 stiff 한계 확장 보류 | README_KO §5–7; 완료 |
| R9 정식 결과·코딩 연결 | 식·가정·정확한 raw 수치를 독립 analyzer와 연결. 다음 reference ladder/new levels 의무 명시 | 분석 코드, REPRODUCE.md, handoff; 완료 |
| R10 종료·재개 | 별도 additive draft PR와 create-only 새 평가 backup, DAG·handoff·영수증 연결 | 실제 외부 완료 상태는 PUBLICATION_RECEIPT.json/BACKUP_RECEIPT.json 기준 |

## 코딩 연구 루프

| 단계 | 실제 작업과 결과 | 증거·완료 상태 |
|---|---|---|
| C1 목표·baseline | 기존 C21F executable 그대로 저장 native 실행을 평가 | 17 source SHA; baseline 재사용 |
| C2 식–데이터–코드 | AST에서 binding·cutoff·tolerance 읽기. Fixture canonical/raw 분리, stock 및 ledger 식 독립 구현 | analyze_native_evidence.py; 완료 |
| C3 수치 설계 | Signed·absolute error, normalized gas norm, reference-free 차수; 가정적 fit와 실제 raw 분리 | results/, 독립 검토; 완료 |
| C4 실행 DAG·자원 | Python 실제 실행 가능. 현재 NCP inventory quota-blocked; 새 native job 없음. 기존 자원 로그는 역사적 증거 | DAG_C21F_ASSESSMENT.json; 후처리 완료, native 재개 준비 조건 별도 |
| C5 구현 | Stdlib terminal/step analyzer와 native-point auditor, exact-data plotting 구현 | 새 코드 3개; 완료 |
| C6 구현 검증 | 새 unittest 5개 PASS, v3 analyzer exit 0. 원래 Newton tolerance와 midpoint scale을 그대로 적용. 기존 56개 검사 재실행 없음 | validation/; implementation-verified |
| C7 과학 검증 | Photon·species stock·누적 energy 수지, 27,140개 point의 EOS·원자사건 회계, 2,160개 accepted step의 기록 범위 평가 | results/, native_point_audit/; 완료 |
| C8 수치·재현성 | 원시 SHA/Gitblob·canonical digest·source linkage, signed convergence, underflow/log-survivor, create-only output | 입력 영수증, 제품 hash, CSV; 완료 |
| C9 독립 검토 | 다른 검토자가 frozen v3 hash·원 gate·point maxima·local defect 및 fit 해석 확인 | INDEPENDENT_REVIEW_KO §9 PASS_SCOPED |
| C10 판정·인계 | 새 평가만 additive 게시·backup, 현재 READY/HOLD와 재사용 이력 인계 | 실제 commit/provider ack 영수증으로 완료 판정 |

## 연구 판정의 범위

새 실패를 찾기 위해 동일 matrix나 suite를 반복하지 않았다. 저장된 두 fixture만으로 시간 2차 경향과 hybrid의 1차 기여를 구별할 충분한 판별 자료가 있어 먼저 계산했다. 원자 rate의 외부 정확성, source-age·spectrum·angle, Case B, Bianchi, Full48, full EoR는 해당 독립 의무가 닫히기 전까지 HOLD다.

Reference의 residual numerical uncertainty는 남아 있다. 이것이 이미 존재하는 native completion이나 새 원시 일관성 검증을 무효화하지는 않는다. 다음 실행은 현재 자원 inventory를 확인한 뒤 같은 fixture의 더 엄격한 reference 또는 새로운 해상도만 추가한다.
