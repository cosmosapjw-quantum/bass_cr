# CR-PHYS02H NCP 준비 독립 후속 심사

## 판정

**PASS_SCOPED — 동결된 v2 실행 source에 대한 NCP 준비만 승인한다.**

- Unit: `CR-PHYS02H-NCP-FULL9600-COLUMN-PARALLEL-QUALIFICATION`
- Execution manifest: `ncp/EXECUTION_SOURCE_MANIFEST.json`, 4745 bytes
- SHA-256: `14f9ad1319146c72d13b1e30583dc27d3b9272c8d23913e63467782fa57b35ec`
- `independent_of_implementation=true`
- `ncp_preparation_admitted=true`

초기 manifest의 HOLD 근거였던 H01–H05와 그 교정 과정에서 확인한 PID namespace 매핑 오류는 이 준비 범위에서 해소되었다. 검토자는 후보 선택·허용조건 설계·구현에 참여하지 않았고 생산 source를 수정하지 않았다. 최초 심사의 자체 비물리 재현을 보존했으며, 이번 후속 심사에는 새 fixture·기존 검사·물리 생성·NCP 실행을 추가하지 않았다.

이 판정은 실제 NCP의 전체9600 생성·원시 배열 동등성·속도 개선을 승인하지 않는다. 실제 실행은 아래 source binding과 현장 runtime/resource admission을 통과해야 하며, 반환 값에 대한 별도의 독립 심사가 필요하다. 기존 F 및 다른 물리 gate는 유지한다.

## 1. 심사 범위와 독립성

처음 심사한 manifest는 `0a0281dccbbae4f53a167bdb0af421c2cf760f0ca0926c9be08f716887aab280`이다. 그 판정은 `initial_manifest_hold/INDEPENDENT_NCP_DECISION.json`의 **HOLD**이며 변경하지 않았다. 원본 qualifier·wrapper·tests·manifest는 `initial_manifest_hold/`와 `evidence/ncp_validation/pre_cleanup_correction/`에 byte-identical하게 남아 있다.

이번에는 원본과 v2의 전체 diff, 교정본과 실패한 중간본의 namespace 관련 diff, 해당 검사 코드·실제 stderr·receipt·진단 기록을 읽었다. 추가 stdlib 작업은 파일 읽기, SHA-256, JSON pin 비교와 AST 구조 비교뿐이다. 생산 모듈 import나 실행은 없었다. 기존 scalar와 local parallel 판정은 별도 범위로 결속하고 재검사하지 않았다.

Canonical Astra v4.0.0의 독립 판정 절차를 적용했다. 실제 backend alias를 증명하는 별도 자료가 없으므로 정확한 runtime 모델명은 `MODEL_UNRESOLVED`로 남긴다. 앞서 명시적 모델 라우팅 시도가 실행 전에 거절된 기록은 routing/runtime 증거이며 물리 실패나 이 심사의 실행 증거가 아니다.

## 2. Source와 입력 결속

독립 읽기에서 v2 manifest의 **19개 직접 pin 모두 bytes·SHA-256이 일치**했다. 초기 manifest와 비교해 바뀐 직접 실행 파일은 다음 두 개뿐이다. 나머지 17개 직접 pin과 scientific contract·입력 manifest·두 자원 amendment는 그대로다.

| 파일 | Bytes | SHA-256 |
|---|---:|---|
| `ncp/qualify_parallel.py` | 46532 | `d9c393190a4930ca2749cc3bde9a6b75767481ee57cf727e03f05a3a212fb8b7` |
| `ncp/run_and_collect.py` | 19018 | `c5d7ecd7c68082062a4ecf02092911c085c96d618347502725fc548dd6a80a06` |
| `tests/test_ncp_qualification.py` | 31796 | `fe710252588b5cc13516ee3a8e3bfd260617bcf602c8248b4343f4f9d74e66f2` |

H input manifest는 549개 파일을 선언하며 SHA-256은 `f5af93b53159fe189d2a0d0b78670b07c707f298927029ccfb5e39c25598bc2d`다. F dependency manifest는 538개 파일을 선언하며 SHA-256은 `248ad97e6417c3ba88bcbbfcb662f6fe65464e63eba6183421770ba06d41a341`이다. 두 manifest 자체의 content identity가 v2에 결속된다. H는 F manifest 자체와 F의 538개 content pin을 모두 포함하며, 그 538개 bytes·SHA-256이 F의 선언과 일치한다.

이는 이번에 549개 전체 payload를 다시 해시했다는 뜻은 아니다. 직접 19개 실제 파일과 두 manifest의 입력 연결을 읽어 확인했다. 실제 NCP admission에서 전체 H 및 F dependency payload를 검사하는 `bound_sources`·`verify_manifest` 경로는 초기 심사 이후 바뀌지 않았다.

읽기 보조 코드의 첫 metadata 비교에서는 F record의 추가 `git_blob_sha` 필드까지 H record와 같다고 가정해 AssertionError가 발생했다. 직접 19개 content pin은 그 전에 이미 일치했다. 최초 오류는 receipt 기록 전 발생했고 source·fixture·물리 실행에 영향이 없었다. 문서화된 content identity인 bytes·SHA-256으로 비교 범위를 바로잡았으며 Git 부가 metadata는 별도로 보존했다. 이 경과는 `V2_DIRECT_PIN_READ_RECEIPT.json`에 남겼다.

AST 비교에서는 qualifier의 기존 정의 중 `execute`, `monitor_check`, `process_measurements`만 바뀌었고, namespace·소유 session·wrapper 확인을 위한 정의가 추가되었다. `Budget`, `admission`, `bound_sources`, `runtime_preflight`, `candidate_build`, `tile_worker`, `lane`, `compare_lanes`, `counts`, `historical_comparisons` 등 기존 계산·허용·비교 정의는 동일하다. Wrapper는 소유 session 취소·손상 metadata 처리와 호출 순서를 교정했다. 이 구조 확인 자체를 새로운 수치 검증으로 해석하지 않는다.

## 3. 초기 다섯 HOLD 항목의 후속 판정

| 항목 | v2에서 확인한 변화 | 결론과 근거 범위 |
|---|---|---|
| H01 — qualifier 선행 사망 후 orphan 누락 | Wrapper의 `finally`가 qualifier의 생존 여부와 무관하게 소유 session 취소를 실행하며 수집 전에 다시 확인한다. | 해결. 실제 비물리 fixture에서 qualifier exit −9 뒤 두 live orphan이 GONE으로 관측됐고, 관련 없는 session은 살아 있음을 검사했다. |
| H02 — 손상된 START·READY·manifest가 수집 중단 | `control_json`은 파싱/읽기 오류를 경고로 남긴다. 원문 파일과 raw payload를 포함하고, 해석할 수 없는 source binding을 admission으로 채택하지 않는다. | 해결. 교정 첫 batch의 malformed-control fixture는 통과했고 이후 namespace diff는 이 수집 경로를 바꾸지 않았다. START·READY·fallback manifest와 raw bytes의 보존 검사를 읽었다. |
| H03 — 손상 event 한 줄이 뒤의 정리·수집 차단 | 실제 소유 session에 대한 첫 취소 신호를 metadata 해석보다 먼저 보낸다. Event는 줄별 경고를 기록하며 유효한 다음 줄을 계속 읽는다. | 해결. 최종 orphan fixture에서 손상 첫 줄과 유효한 소유 event를 함께 보존하면서 정리·수집이 완료됐다. |
| H04 — comparator session 기록 누락 | Lane과 comparator 모두 같은 `register_session` 경로로 소유권 event를 durable append한다. Nonce/run marker 기반 발견이 spawn과 event append 사이의 사망 경계도 보완한다. | 해결. Comparator 등록 경로를 정적으로 확인했다. 최종 fixture는 등록 event의 session identity와 event 없는 두 번째 소유 session의 정리를 검사했다. |
| H05 — 900초 후 root의 8초 유예 중 계산 지속 | Wrapper가 science group에 먼저 SIGTERM을 보내고 짧은 취소 단계 뒤 남은 science group에 SIGKILL을 보낸다. 그 다음 qualifier만의 종료·증거 유예를 처리한다. | 해결. 시계를 주입한 비물리 watchdog fixture에서 live child가 root의 8초 wait에 들어가기 전에 ZOMBIE가 됐다. 실제 900초 대기나 과학 실행을 수행한 증거는 아니다. |

수집 manifest의 `COLLECTION_DOES_NOT_ATTEST_SOURCE_ADMISSION`은 적절하다. 손상 파일을 원문으로 수집했다는 사실과 source admission은 분리되어야 한다. 경고·누락·identity mismatch가 있으면 `PARTIAL_OR_MISMATCHED_EVIDENCE_PRESERVED`로 기록한다. `COMPLETE_OBSERVED_PAYLOAD`도 관측한 수집 대상의 완전성을 뜻하며 과학 성공을 뜻하지 않는다.

## 4. PID namespace 진단과 직접 영향

실패한 첫 교정은 current syscall PID를 `/proc`의 조상 namespace PID와 같은 숫자라고 취급했다. 보존된 진단의 한 관측에서는 current PID가 5인데 `/proc/self`가 `/proc/196252`로 해석되고 `NSpid=[196252,5]`였다. 그 상태에서 숫자 경로를 그대로 사용하면 identity 조회와 group 신호의 대상을 잘못 해석할 수 있다.

v2의 `proc_namespace_identity`는 먼저 활성 PID namespace inode가 자신의 것과 같은지 확인한다. 그 뒤 `NSpid`, `NSpgid`, `NSsid`의 마지막 원소를 current-namespace syscall ID로 사용한다. 원래 proc 경로·조상 PID/PGID/SID·start ticks·namespace vector는 별도의 evidence 필드로 남긴다. 숫자 경로만으로 identity가 맞는다고 간주하지 않고, 필요한 current PID가 살아 있으나 유일한 매핑을 얻지 못하면 typed HOLD로 처리한다.

소유 session 취소는 같은 UID·검증한 namespace와 함께 이번 launch의 nonce·정확한 run marker가 live session member에 일치하는지 확인한다. Event의 임의 PID만으로 다른 작업을 종료하지 않는다. Zombie는 실행 중인 작업과 구분하며, 과거 정확한 proc 경로/start tick을 이용한 zombie 관측 보완은 신호 권한을 부여하지 않는다. 매핑 또는 소유권을 확인할 수 없는 경우의 경고는 실제 반환에서 계속 평가해야 한다.

Wrapper의 실제 parent route, session 등록, 종료 대상 발견, process RSS 조회에 같은 namespace 해석을 적용했다. RSS는 현재 sample의 byte 값이고 lifetime peak들의 합이 아니다. 새 측정 경로가 이전 작은 파일럿의 불완전한 RSS 관측 범위를 소급하여 바꾸지 않는다. 실제 NCP의 지속적인 aggregate sample과 가시적 cgroup 관측은 아직 없다.

## 5. 저장된 검증 증거와 실패 보존

| 증거 | 실제 관측 | 판정에서의 역할 |
|---|---|---|
| 최초 독립 비물리 재현 | 1회, 6 case, wall 0.054009059초, exit0 | 초기 HOLD의 실패 경계 재현. 새 OS child와 물리 호출은 0. |
| 첫 cleanup 교정 batch | 8 tests 중 6 PASS·1 FAIL·1 ERROR, wall 1.946292326초, actual exit1 | 실패와 source를 보존한다. Orphan signaled-child 누락과 session identity 부재가 실제 실패였다. |
| namespace 교정 영향 batch | 6 PASS, wall 1.725660511초, actual exit0 | 현재 qualifier·wrapper·tests SHA와 일치한다. 기존 과학 suite 전체를 다시 실행한 것이 아니다. |
| 이번 독립 후속 심사 | 읽기·hash·JSON·AST 비교만 수행 | 새 fixture 0, 기존 test 재실행 0, physical G/column/pulse 0, NCP 실행 0. |

최종 batch의 실제 stderr는 6 tests의 `OK`를 기록한다. Fixture runner 전체 wall과 unittest 내부 wall은 다른 범위이며 더하지 않는다. 두 orphan은 각각 LIVE→GONE, watchdog child는 LIVE→ZOMBIE로 관측됐다. 첫 실패 순간의 child state는 **NOT_OBSERVED**로 유지한다. 이후의 관측으로 최초 실패를 zombie였다고 재해석하지 않는다.

검사에는 실제 수치 생성 대신 sleep-only process, 주입된 시계, 작은 비물리 raw bytes와 mocked admission을 사용했다. 최종 fixture의 Python은 3.12.14이며, 이는 NCP 수치 실행 계약의 Python 3.12.3을 검증한 결과가 아니다. 이전 첫 검사·ResourceWarning·wrapper accounting 교정 기록도 별도 보존된다.

## 6. 보존된 실행 계약

초기 심사에서 읽은 실행 계약과 두 amendment는 그대로 유지되며, v2 diff가 아래 의무를 바꾸지 않았다.

- 전체 science command의 900초 한도와 첫 실패 종료. 모델·반복별 시간 초기화가 없으며 source 복구·전송과 실패 후 수집은 별도 overhead다.
- 두 모델·두 반복의 serial4 + candidate4, 총8 논리 전체 생성과 76800열 상한. Durable reservation은 launch보다 앞서며 새 폴더를 자동 재시도 허가로 취급하지 않는다. 이전 H run 여부 확인은 handoff의 실행 전 의무다.
- 실제 CPU capacity 최대64에서 wrapper1 + qualifier1 + lane2 + spawn support2 + worker58 =64 슬롯, 모델당29 workers 상한. 실제 자원에 따라 감소하며 최소2/model이 불가능하면 HOLD한다.
- 메모리 reserve는 실제 한도의 max(16GiB,1/8), paired reference 작업 여유는24GiB다. Candidate는 parents4GiB + workers×512MiB + support64MiB + wrapper64MiB를 합산하고 출력용 최소16GiB disk를 요구한다. 128GB와128GiB를 같은 수치로 두지 않는다.
- 실제 Python3.12.3·NumPy2.4.2·SciPy1.17.0, 환경 thread1과 실제 threadpool1을 신선한 child에서 확인한다. 경로·library identity·dispatch 관측을 기록하고 과거 metadata를 현재 인증으로 채택하지 않는다.
- 원래 저장9600 에너지와 물리 source, 열 내부 연산 순서, disjoint column partition, 원시 partial/full 값 저장과 정확한 비교를 유지한다. tolerance 완화·clipping·grid 재생성·부동소수 reduction은 추가되지 않았다.
- 네 개 same-runtime candidate/reference 비교와 두 개 reference 반복 비교를 수행하도록 유지한다. Historical fingerprint 차이는 정보이며 과거 CSC 복구나 F binding 해소를 뜻하지 않는다.
- 두 반복의 같은 입력 build-and-persist 시간으로 median ratio를 보고한다. Correctness와 performance를 분리하고 느리면 `PERFORMANCE_NOT_IMPROVED`를 남긴다. 추가 scaling sweep이나 자동 최적화 반복은 없다.
- Pulse·expm·resolvent·선형계·F retry·G frontier는0이다. 손상된 실패 evidence와 이미 저장된 partial 값을 수집하며 immutable source와 실제 종료 기록을 보존한다.

## 7. 별도 판정 결속과 남아 있는 gate

| 기존 독립 판정 | 유지 상태 | SHA-256 |
|---|---|---|
| Exact scalar | `PASS_SCOPED` | `51d7f9c85c590b75de9d110110108f2ba66f189a34c2b665dde656b62a827392` |
| Local parallel | `PASS_SCOPED` | `6781c218148f586351e0978ae1133de4923eceb2930d4a8f7ca8bd866744c84d` |
| 최초 NCP preparation | 원래 manifest에 대한 `HOLD` 보존 | `5df1eacb0b69d3ce63e9011ca5cdb6008426ff009e4533242646c66a13cb10f4` |

Scalar의 정확 십진 모멘트 인증과 local payload의 exact parity는 각자의 범위에서 유지한다. 두 recorded representation을 합치거나 작은 행렬의 parity를 물리 oracle로 바꾸지 않는다. 이번 준비 판정과 실제 NCP 결과도 그 범위들과 구분한다.

| Gate | 유지 상태 |
|---|---|
| F | `HOLD_OPERATOR_BINDING_UNRESOLVED` |
| G frontier | `BLOCKED_BY_F_OPERATOR_BINDING_HOLD` |
| PHYS02_DELAY | `OPEN` |
| production_history | `HOLD` |
| atomic_G02 | `UNRESOLVED` |
| b_grid | `NO_GO` |
| all_bound | `OPEN` |
| R17B2B | `NO_CERTIFIED_SOURCE_SHARPENING` |
| CCC_2026_exporter_identity | `SOURCE_IDENTITY_UNRESOLVED` |

## 8. 검토 밖의 작업과 다음 admission

읽은 시점의 `REPORT_KO.md`와 `START_NCP_CODEX_KO.md`의 NCP 약속은 새 manifest, 검증한 wrapper 경유 실행, 900초/8회/76800열, 실패 수집, 준비·실제 결과의 구분과 일치한다. 실제 생성된 `RETURN_MANIFEST.json` 및 외부 collection receipt와 로그를 보존하라는 지침도 코드의 출력 구조와 맞는다.

Publication·백업 업로드/복구·restore helper 구현과 실행·외부 START의 실제 위치/ID·Git commit/tree·이 판정 이후 root가 작성할 READY 및 metadata는 이 심사의 승인 대상이 아니다. 문서의 그러한 지침을 읽었다는 사실을 실행·복구 성공의 증거로 사용하지 않는다.

Root는 이 판정의 실제 content identity와 v2 manifest 및 H input manifest를 READY에 결속할 수 있다. 해당 bytes 또는 실행 계약이 바뀌면 이 준비 승인을 이동해서 사용하지 않는다. NCP에서는 검증한 interpreter와 실제 filesystem에서 계획을 확인하고, 같은 계획이 이미 정확히 수행된 경우 반복하지 않는다. 실행은 신선한 최초 H run에 한 번만 수행하며 결과·예약·부분 raw 값·실패·자원/시간을 보존한 후 별도의 실제 결과 독립 심사로 넘긴다.

## 주요 증거 파일

- `review/ncp/V2_DIRECT_PIN_READ_RECEIPT.json`: 직접19개 pin, H549/F538 선언 연결, 증거 identity와 metadata 비교 보정 경과.
- `review/ncp/V2_STATIC_DELTA_RECEIPT.json`: 변경/동일 AST 정의, 최종 fixture source identity, 초기·중간 실패본의 보존 확인.
- `review/ncp/initial_manifest_hold/`: 초기 HOLD, 독립 재현, 원본 source.
- `evidence/ncp_validation/CLEANUP_CORRECTION_TEST_RECEIPT.json` 및 stderr: 첫 교정의 실제 실패.
- `evidence/ncp_validation/pre_namespace_mapping_correction/DIAGNOSIS_AND_PRESERVED_IDENTITIES.json`: namespace 진단과 실패본 identity.
- `evidence/ncp_validation/NAMESPACE_REPAIR_TEST_RECEIPT.json`, runner 및 stderr: 최종 직접 영향6개와 실제 lifecycle 관측.
- `review/exact/INDEPENDENT_EXACT_DECISION.json`, `review/parallel/INDEPENDENT_PARALLEL_DECISION.json`: 기존 별도 PASS 범위.
