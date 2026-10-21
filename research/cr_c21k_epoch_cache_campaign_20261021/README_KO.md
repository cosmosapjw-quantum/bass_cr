# C21K — epoch 계수 재사용과 NCP bounded campaign

이 단위는 완료된 C21I 구현 및 C21J 원 native trace 분석 위에 추가된다. 부모는 C21J 문서 head `fee0d6a3f1b6460a24a1ae60f50ee84971227e5b`다. 원 H/I/G/F 실행 source, test, 원 native 반환과 역사 실패는 수정하지 않는다. 실행 content와 이후 문서 head는 최종 출판 영수증에서 구분한다.

## 실제 완료 범위

`epoch_adapter.py`는 원 reference와 C21I adapter의 고정 bytes를 private module에서 읽고, 두 호출 경로의 opacity binding에만 새 계수 재사용을 적용한다. 같은 cell·불변 fixture·고정 source·같은 binary64 epoch에서 성공한 `E,K`를 LRU16에 보관한다. 저장 배열은 불변 bytes를 바탕으로 하고 호출자에게는 독립 writable 배열을 돌려준다. Signed zero와 인접 binary64를 구분하며 float/np.float64 이외 타입은 거부한다. State-dependent hazard·population·전체 RHS를 epoch key로 캐시하지 않는다. 원 full-state exact cache와 live native guard는 별도로 유지된다.

Opacity miss에서는 원 왼쪽 결합 곱셈 순서를 유지하며 같은 scalar 중간값만 한 번 계산한다. M9의 exp 호출식은 miss당28→2, M81은244→2다. H는 원함수를 유지한다. 근사, 허용오차 완화, state/event 변경, clipping, fastmath 또는 재결합을 추가하지 않았다.

`run_epoch_pilot.py`와 `epoch_pilot_contract.py`는 원 H provider·예산·CPU55 보호·build 검사·cleanup에 새 K identity를 연결한다. K native 실행은 checkout 밖의 H/I/K 출판 영수증과 **detached K content**를 요구한다. H→I→K ancestry, 원 source bytes 및 K runtime exact3를 검사한다. 원 I의 fe6 전용 native gate를 다른 commit에 맞춰 고치지 않는다. FD 부모는 동일 K mode/source/publication과 원 H의 fixture/method/native/build/COMPLETE/raw 검사를 모두 통과해야 한다.

## 검증과 제한

| 항목 | 실제 결과 |
|---|---|
| Epoch focused | 최종 source에서13 tests PASS; 원 FIT 문턱값을 포함한126 입력 조합의 bit parity |
| 새 runner focused | 임시 Git 및 explicit doubles로22 tests PASS |
| 실제 plan 통합 | 고정 H/I/G/F/baseline34파일로 READY_EXECUTABLE_INPUTS_VERIFIED; doubles 없음 |
| 최종 saved callback replay | 3경우, 각472 replies/40432 binary64 값, FD nodes와 physical fields bitwise 일치 |
| 원 I vectorized 저장 trace | provider table823; opacity859요청/329miss/530hit |
| 원 I exact 저장 trace | provider table754; opacity790요청/329miss/461hit |
| 새 native chemistry / 새 IVP | 0 / 0 |
| 일관된 saved callback 가속 | NOT_ESTABLISHED |
| K live native / native performance / NCP64 scaling | NOT_RUN / NOT_EVALUATED / NOT_EVALUATED |
| 전역 오차 경계 | `global_error_bound=null` |

최종 source SHA는 `EXECUTION_MANIFEST.json` 및 `evidence/verification/epoch_replay_final/replay/REPLAY_REPORT.json`이 지정한다. 이전 두 timing 측정은 각 역사 source에만 연결된다. 초기 opacity+H cache의 paired median은0.9364664941, 후속 opacity CSE+cache/H 원함수 후보는1.0004085537이었다. 두 범위 모두1을 가로지른다. 이후 type/deadline guard가 추가된 최종 source의 timing 측정으로 이 결과를 옮기지 않는다. 이전 `epoch_final/`이라는 경로명은 당시 작업명일 뿐 최신 source라는 뜻이 아니다.

저장 accepted states를 소비한 replay는 새 trajectory 적분이 아니다. 기존 full-RHS cache가 제거한69회와 잔여 opacity hit를 중복 계산하지 않는다. 원 작은 native projection100hit는 다른 정책이며 이 단위가 구현하지 않는다. 과거 C21I 제조32+FD2와 C21J 검증을 다시 실행하지 않았다.

## NCP 실행 범위

`ncp/`의 campaign은 실제 affinity/effective cpuset·cgroup quota·현재 메모리·기존 배정을 먼저 확인한다. CPU55를 제외하고 coordinator CPU/RAM을 별도로 계상하며 각 scientific job은 single-thread다. 128GiB에서는16GiB, 그 외에는12.5%와 최소1GiB 중 큰 reserve를 유지한다. 64 CPU라는 명칭으로64개 physical core 또는64배 가속을 가정하지 않는다.

이전 명시적 잔여21개와 이번 요청에 따른 비교범위 확장28개를 구분한다. 원 완료3개가 현재 실행 identity에 맞는 경우 총52 logical scientific slots 중49개가 미실행이다. H7+G12+I14+K16이며, 이 중26개는 base/reference,23개는 matching base 또는 원 G 판정 뒤의 조건부 작업이다. 원 G는 독립 계약의 내부 single-worker campaign8+조건부4를 그대로 사용한다. 이 때문에 coordinator의 top-level node 수와 logical scientific job 수는 다르다. I baseline audit8개는 H control과 중복되어 기본 범위에서 제외한다.

이 행렬 확장은 과거 C21J의 one-job packet이 이미 전체 행렬을 승인했다는 뜻이 아니다. 이번 사용자의 전체 실행 준비 요청에 따른 새 operational decision이다. Matching 완료 근거는 재사용하고, 다른 source/native/build/fixture/method/control identity는 재사용으로 표시하지 않는다. 실행 실패 뒤 자동 retry, 원 output 덮어쓰기, 조건부 과학 HOLD의 임의 해제를 하지 않는다. 실제 DAG readiness와 자원 admission이 허용한 작업만 동시에 실행한다.

동시 campaign의 개별 wall time은 실행 처리량·진단 자료다. 이를 통제된 native speedup benchmark로 해석하지 않는다. 일관된 native 가속 주장을 하려면 해당 source/binary/fixture/control을 고정한 별도의 비교 설계와 실제 측정이 필요하다.

## 이론과 자료

`theory/C21K_EPOCH_CACHE_AND_DAG_THEORY_KO.md`에 의존성, binary64 재사용 조건, ordered CSE, 비용식, DAG work/critical-path 및 이상적 list scheduling 경계가 있다. SciSpace·Exa·Wolfram을 실제 사용했고 원전, 읽은 범위, 실패·제한, 우리 CAS query/result를 별도 ledger로 남겼다. 기존 memoization·scheduling 정리와 이 source에서의 구체적 적용을 구분했다. 새 strong no-go는 채택하지 않았다.

`intake/`는 연구 전 및 마감 전 관측 범위를 기록한다. 다른 대화 검색은 unavailable이었다. GitHub와 세 저장처에서 새 bass_cr C21 native return은 확인하지 못했다. 관련 REI의 새 profile/tiny native 결과와 HE/WU의 별도 연구는 source identity가 달라 이 단위의 완료 근거로 사용하지 않는다.

Full48, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle/full-driver parity 등 기존 과학 HOLD와 C21F의 게시 완료 상태를 보존한다. C21K 구현·검증 완료, Git 출판, 백업, 실제 NCP 실행의 상태는 각각 별도 영수증으로 판정한다.
