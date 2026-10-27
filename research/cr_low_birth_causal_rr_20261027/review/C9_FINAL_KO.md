# C9 독립 saved-output 통합 검토

## 판정

**PASS_SCOPED_FINITE_CAUSAL_RR**, open blocking finding **0**. 이 판정은 고정된 실제 low-birth source와 새 조건부 100 K H1/He4-only recipient의 유한 시간 discrete Coulomb+ground RR 응답을 수용한다. 전체 물리 완료, 모든 실행 성공, source ZIP R3 또는 최종 게시 완료를 선언하지 않는다.

검토자는 `/root/source_qualification`이며 주 이론 유도, production math/runner, independent numerical reference의 작성자가 아니다. Source/literature qualification, R6 및 사전 정적 검토 참여는 공개한다. 원 보고서의 두 범위·시점 문구를 교정하고 실제 C9 판정·C8 게시 상태 문단을 추가했다. 편집 전 보고서를 그대로 보존했다. 과학 실행·import·compile·수치 재계산은 **0**이다. Exact byte/JSON/NPY header/CRC 대조와 저장 receipt의 비용 산술은 메타데이터 검증으로 수행했다.

## 실제 근거

| 구분 | 확인한 실제 근거 | 해석 |
|---|---|---|
| Source | 4,394,309-byte record SHA `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf` | 유일한 `direct_0p1_10`; 3200 active atoms + direct cutoff; old source replay0 |
| 시간·상태 | `q=tA`, proper `[0,1e10] s`, fixed proper volume, 100 K | 구간 밖 unknown; volume 크기 null |
| 새 inventory | H1/He4-only conditional, `nb=8750/47 m^-3` | 같은 donor/recipient에 명시; 이전 PR109 null을 소급 변경하지 않음 |
| Controls |46 unique 채택 =45 saved PASS 재사용+1 selected repair |47 actual evaluations 중1 failed 원기록·비용 보존 |
| Primary |4 cumulative prefixes+4 observation bins,112 internal flags PASS | Prefix는 nonadditive, additive RR return8개 |
| 독립 reference |517/517 unique comparisons PASS | 별도 SI/log-form coefficient +6402-state sparse augmented exponential; production imports0 |
| 배열·실행 identity | Primary18개 NPY payload SHA/형식/CRC, independent NPZ whole SHA/CRC,7 attempts×9 snapshots | Byte 무결성 대조; 새 numerical solution 아님 |
| 그림 | 실제 plot_v2 PNG/SVG 해시 일치, PNG 육안 확인 | Saved results만 표현; 원 plot_v1 failure 보존 |

Frozen contract와 theory hash는 R6의 범위와 일치한다. Production model/prepare/uniformization/ports/primary의 hash는 사전 정적 검토한 수식과 일치하며 새 과학 수정이 없다. Independent source는 원 source bytes와 동일 frozen literals를 별도로 읽고 계수·n/O를 독립적으로 계산했다. 실제 RESULT는 primary JSON/NPZ의 exact digest에 결속되어 있다. 수·kinetic·retained photon의 작은 RR quantity를 각각 자신의 크기로 비교한 `1e-9` 기준, conservation `1e-11`, coefficient L1 `1e-11`, zero-reference의 exact zero 규칙을 유지했다. Array componentwise maximum은 diagnostic이며 frozen gate를 소급 바꾸지 않는다.

## 수용 범위와 물리적 경계

Actual occupancy와 finite-window RR, 기록된 proper-history endpoint rate, 해당 capture에서 생성한 discrete retained-photon atoms, 같은-state RR-only native25를 수용한다. Source의 angle/target/729/proper clock 인자는 이미 저장된 A에 포함되어 있고 다시 적용하지 않는다. 새 RR ion target density는 hazard에 한 번만 들어간다. Direct cutoff source atom은 active RR state로 들어가지 않으며 downstream drift cutoff와 분리된다.

Native25 수용은 RR event의 `Delta nb=0` 투영이다. H/He의 neutral 증가·ion 감소와 nonthermal electron 감소가 charge-derived thermal electron 변화0을 만들고, captured kinetic energy는 nonthermal energy 감소로 기록한다. Photon binding energy는 별도 retained port에 남는다. `w_ext=0`과 frozen `Delta logT=0`은 물리적 heating 완료가 아니다. Full source parent chemistry/native25, coupled thermal bath, photon absorption/escape/deposition, continuous emission history, 구간 밖 source, absolute worldtube totals와 전체 물리 오차는 null 또는 미완료다.

첫 두 prefix의 ordinary binary64 tail0은 양수 Decimal80 값의 underflow다. 원 Decimal 문자열, omitted-summation remainder, 공통 horizon의 비영 Chernoff/design reserve를 보존한다. Exact-arithmetic Poisson tail 이론과 실제 ordinary-FP 평가를 구분하며 outward interval certificate를 주장하지 않는다. 연속 energy 오차나 생략된 충돌 과정의 오차로 승격하지 않는다.

## 실제 실패와 비용

| 비용 범주 | 실제 값 `[CPU-s]` |
|---|---:|
| Saved receipts까지 측정된 preparation+worker+coordinator |14.616973 |
| 별도 conservative receipt tails |10.075038000000001 |
| **실패 포함 charge / 이 단위 cap** |**24.692011 /40** |
| 미사용 산술 잔여 |15.307989, NONTRANSFERABLE |

기계가 읽는 [BUDGET_CLOSEOUT](../evidence/BUDGET_CLOSEOUT.json)을 원5개 preparation receipt의 실제 measured field,7개 worker attempt 및 같은 attempt의 maximum cumulative debit에 대조했다. Preparation의 measured1.686505와 charged1.936505 사이 tail0.25를 분리했다. 따라서 legacy ledger의 `measured_worker_plus_coordinator_cpu_s=14.866973`을 순수 측정값으로 인용하지 않는다. Provider/kernel background/metadata discovery·authoring·publication CPU는 측정되지 않은 값을0으로 만들지 않는다.

`controls_v1`의 한 energy oracle failure는 exact-zero active-state 실패가 아니라 binary64 곱셈 재결합의 zero-tolerance oracle 문제였다. 실제 selected `controls_v2` 하나가 통과했고45개는 기존 evidence를 재사용했다. 원 failed result·receipt·charge는 남는다.

`plot_v1`은 coordinator guard로 중단되어 완성된 이미지가 없었다. 원 receipt3.106334, amendment1, authoritative amendment2를 모두 보존하고 마지막 cumulative10.145070을 한 번만 charge했다. 같은 코드·saved result의 unique `plot_v2`를 별도 prospective worker6+coordinator10(tail5 포함)으로 승인한 뒤 실제 성공했으며 charge7.717970이다. 이를 과거 실패의 소급 PASS로 표시하지 않는다.

모든 terminal receipts의 observed owned processes0과 실제 nonzero RUSAGE_CHILDREN worker CPU는 동시에 남아 있다. `/proc` descendant monitor가 이 host에서 검증됐다고 볼 수 없다. Per-process RLIMIT, final inclusive debit, admission estimate와 preventive aggregate hard proof를 구분한다. **all_resource_attempts_pass=false, all_worker_attempts_pass=false, all_runtime_attempts_pass=false, aggregate hard preventive proof=false**다. Actual7 workers는5 completed·2 failed이고 원 resource refusal/reclaim failure도 보존된다. 추가 승인 science runs0이며 옛20/30/병렬60 예산이나 이번 잔여를 다른 단위로 이월하지 않는다.

## 게시 및 중앙 관찰

C9 직전 actual C08 receipt는 commit `fbe0dd5acd4664471c9dc9de49117daefe5451e2`, checkpoint5,148,630 bytes/366 members, SHA `fdf01b07f406a8e5f159101d6d98bbe09d2e5726d964fe100afce4fd61e3e358`에 Dropbox/Drive R2 ACK를 기록한다. **게시·이중 R2는18/20**이다. Raw archive readback은 false이므로 이를 R3로 부르지 않는다. C09 preflight UTC `2026-10-27T14:05:41.512387+00:00`의 local/remote CR HEAD, 정책·source pin·직전 backup receipt를 읽었다. REC AGENTS404와 대화 전체 검색 unavailable, Drive partial inventory는 보존한다.

현재 canonical 중앙은 `74aff0740d1812c732466563a9c66108a3a4d8fd`에서 **28/88**,88 nodes/17 edges이다. 다른 owner의 기존 B3h 완료가+1을 만들었고 이 CR 효과는0이다. 과거27/88 stage receipts와 별도 PR23632/88 제외를 유지한다. N4/N5 partial, N6/N7 gated, L4false, global physical completion/error/budget/currency null이다.

C9 과학 수용은 실제 C9/C10 게시, immutable source ZIP, dual full-GET R3, 문서 D, 독립 검토한 additive central candidate·실제 M 및 handoff의 후속 delivery gate를 대신하지 않는다. 각 작업의 완료 여부는 이후 실제 receipt로 정한다. 이 검토는 미래 PASS 수·CPU·S/D/M 또는 source R3를 미리 만들지 않는다.

전체 reviewed-file pins와 resolved/retained-limit findings는 [C9_FINAL.json](C9_FINAL.json)에 있다.
