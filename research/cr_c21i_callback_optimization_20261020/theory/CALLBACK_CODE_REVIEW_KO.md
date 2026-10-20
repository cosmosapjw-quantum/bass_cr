# C21I optimized_adapter 독립 source 검토와 deadline 수정 확인

2026-10-20. 최종 검토 source는 optimized_adapter.py **20343 bytes**, SHA256 **bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e**다. 독립 검토에서 실제 budget defect 하나를 세 가지 경로로 재현했고, 담당자의 작은 수정 뒤 같은 probe로 모두 거절됨을 확인했다. 선언된 deterministic provider 범위 안에서 남은 callback 구현 blocker는 발견하지 못했다. Native admission을 수행하는 runner와 실제 같은-binary benchmark는 별도 통합 gate다.

## 1. 원 수학과 배열 순서

새 callback은 caller 전용 private C21H module을 읽고 CellCallbacks binding만 교체한다. C21H runtime 8개와 C21G manifest가 지정하는 원 C21F source 10개의 바이트를 시작/끝에 확인한다. 원 reference_tau.py의 event loop, reduced_rhs closure, birth 처리, exact Y=0 coordinate map, accepted state·tau·log-survivor·ledger 검사는 유지한다.

jacobian은 n×n reduced scratch를 한 번 소유하고 요청마다 모든 성분을 0으로 재설정한다. tau 열의 사진화학·열·photo ledger·photon work 행을 벡터로 채우며, gas 열의 원 gas_nodes/derivative_weights/실제 original RHS 3점 차분을 유지한다. 각 cohort의 heat는 원 contiguous 3-species reduction을 axis=1로 적용한다. He event 행은 원 event_fractions의 산술 순서, scale은 곱셈 다음 나눗셈 순서를 유지한다. 반환은 scratch의 독립 copy이므로 다음 Jacobian이 이전 반환값을 덮어쓰지 않는다.

생산자의 scoped callback 검사는 Y=0, Y>0, 실제 보존된 두 fixture 및 M=128의 제조 증대 입력에서 전체 행렬/RHS/time partial의 bit pattern과 FD nodes를 비교했다. underflow와 구조적 zero, gas 경계, 짧은 cell의 기존 오류도 포함한다. 이 검사는 native를 호출하지 않았고 ODE solver 앞에서 원 closure를 포착했다. floating reduction의 bitwise 관측을 모든 NumPy 버전·아키텍처에서의 보장으로 확장하지 않는다.

## 2. Cache의 실제 구현 범위

vectorized_exact는 한 cell마다 최대 16개 성공한 원 RHS 값을 LRU로 저장한다. key는 실제 t의 float64 bits와 전체 physical u의 float64 bytes다. passive ledger bits와 signed zero도 포함한다. 모든 cell에 독립 cache가 생성된다. fixed fixture 입력의 list를 scalar encoding을 보존한 tuple로 소유하고 scale/dynamic/active 배열은 별도 copy 후 읽기 전용으로 둔다. fun/fixture/reference/소유 배열/lo-hi 변경은 guard가 거절한다.

cache는 rhs뿐 아니라 gas/time FD에서 요청되는 성공한 original 값도 동일 full-bit 조건으로 재사용한다. 이것은 근사 Jacobian이나 tolerance cache가 아니다. 오류·nonfinite·shape-invalid 반환을 삽입하지 않으며 호출자가 반환 배열을 수정해도 cache 내부 copy는 변하지 않는다. 같은 state의 이미 성공한 원 RHS를 생략하는 경우 원 min_internal_tau 갱신은 idempotent다. actual calls는 실제 계산이 줄어든 만큼 감소하고 logical requests/hits와 구별된다.

자동 admission은 source-pinned exact ManufacturedMicro/ZeroMicro class와 빈 instance configuration으로 한정된다. generic callable은 vectorized 모드에서 여전히 매번 호출되고, exact 모드는 명시적 admission을 요구한다. 이 admission 사전 자체는 임의 callable의 순수성을 증명하지 않는다. Native runner는 실제 class/source/owner/binary/instance identity와 연결해 이를 생성해야 한다. pinned native EVAL 경로의 값 순수성은 REVIEW_PLAN_KO.md와 raw/owner_purity의 source 5개에 대한 별도 검토가 뒷받침한다.

## 3. 독립 검토에서 재현한 deadline 결함

수정 전 source SHA256은 **59a3affa03ab6171d14c6d098121ced4c7055320a0e0a77846ee8087df4e5c5d**, 19358 bytes였다. callback은 계산 전 guard만 수행하고, driver 최종 반환 뒤 guard가 없으며 source setup 후 새 deadline를 만들었다. 다음 세 fake-clock probe에서 예산 1초를 넘긴 clock=2초에서도 성공값을 반환했다.

| 같은 probe 논리 | 수정 전 | 최종 source |
|---|---|---|
| original RHS 계산이 deadline를 넘음 | 값을 반환하고 cache entry 1개 생성 | 예외, cache entry 0개 |
| driver 최종 반환이 deadline를 넘음 | 결과 반환 | RUST_JOB_WALL_BUDGET 예외 |
| source setup이 남은 예산을 소진함 | 뒤늦은 deadline로 callback 허용 | driver 시작 전 RUST_JOB_WALL_BUDGET 예외 |

probe_deadline_review.py는 실제 후보 source를 읽어 frozen C21H loader와 callback/driver 경로를 사용하되 계산·시간은 작은 tool stub으로 대체했다. Rust/native/ODE solver는 실행하지 않았다. 수정 전 source와 raw는 raw/deadline_review/에 남겼다. 최종 source는 raw/deadline_review_fixed/에 별도로 저장했다.

최종 independent replay는 probe의 **출력 경로와 snapshot/JSON 파일명만 변경**했다. 조건·값·검사 논리는 0개 변경이다. 세 경로 모두 예상 거절을 반환했고 source는 실행 전후 동일했다. REPLAY_EXECUTION_RECEIPT.json은 이 차이와 두 프로그램 hash를 기록한다. 이것은 세 deadline scenario의 scoped red→green 근거이며 전체 C21I 검사나 전체 과학 실행이 red-first였다는 뜻이 아니다.

## 4. 수정 내용의 검토

최종 구현은 wall_s를 먼저 확인하고 함수 진입 시점의 absolute deadline를 만든다. source/fixture setup이 그 시간에서 소비된다. 원 H driver에는 setup 뒤 실제 remaining만 넘긴다. original cache miss는 계산과 방어적 copy가 끝난 뒤 guard를 통과해야 cache에 들어간다. hit도 copy 뒤 guard를 통과해야 hit로 반환된다. rhs/partial_t/jacobian의 마지막 산술·복사 뒤에도 guard가 있다. driver 반환 후와 source identity readback 뒤에도 deadline를 확인한다.

이 수정은 물리값·Jacobian 산술·차분점·tolerance를 바꾸지 않는다. 원 실제 RHS/native 200000회 상한, native timeout=min(15초, 남은 예산), Rust 요청 상한을 완화하지 않는다. 원 provider deadline/closed/process 검사도 계속 실행된다. source나 provider 실패를 cache 값으로 감추지 않는다.

생산자는 변경 의존성에 대한 6개 focused 계약을 source 49558e49…에서 실행한 뒤, remaining 전달의 최종 작은 변경에 영향받은 wrapper deadline/원 event-loop wiring 2개를 최종 bb73bfa9…에서 다시 확인했다. 전체 18개 고유 계약은 scoped 근거로 관리하며 최종판 전체를 한 번에 새로 실행한 기록은 아니다. 독립 검토에서 해당 evidence index의 15개 파일 hash를 확인하고 관련 stdout/stderr/outcome을 읽었다. 원 경계 테스트의 초기 He simplex 기대값 오류와 그 교정도 보존되어 있으며 이를 optimizer의 과학 결함으로 바꾸어 기록하지 않는다.

## 5. 남은 runner·성능 통합 gate

아래 항목은 callback source의 새 결함이라는 뜻이 아니라, 이 라이브러리를 실제 실행할 runner가 구현해야 할 소유 계약이다.

1. Fresh process에서 H run_pilot을 NumPy/optimized_adapter보다 먼저 load하여 원 early-import guard와 worker=1 설정을 보존한다. NUMPY_ALREADY_IMPORTED flag를 덮어쓰지 않는다.
2. H context/verify_own_source를 실제 실행하고 C21I entrypoint/adapter/설정/기타 실행 runtime manifest의 before/after identity를 더한다. 실제 bridge build source와 새 standalone block companion의 build를 구별한다.
3. Native exact cache admission은 원 BudgetedNativeMicro, NativeMicro, process, owner/binary와 고정 max_calls/원 deadline에 묶는다. 예상대로 변하는 calls/timeout는 값 캐시 key로 사용하지 않는다. wrapper.native/process 교체나 구성 drift를 감지하는 O(1) guard를 둘 수 있다. binary/source hash는 기존 before/after gate에서 유지한다.
4. FD parent에는 C21I source, 최적화 옵션, fixture, method, scale, native/bridge/build/receipt/raw identity가 같아야 한다. 지정된 fd-half 변화만 허용하고 H의 옛 완료 receipt를 C21I parent로 자동 채택하지 않는다.
5. callback-only kernel/replay와 전체 제조 trajectory를 분리한다. 동일 새 binary로 현재 H baseline과 I를 비교하며 새 source hash에 timing을 묶는다. mode=baseline도 I subclass의 guard와 timing instrumentation을 포함하므로 이 내부 비교는 '공통 계측을 둔 원 callback 경로'라고 표시한다. 실제 untouched H 전체 실행과의 속도비는 그 실행을 별도로 사용한다.

이 library는 public native admission이나 NCP allocation을 직접 수행하지 않는다. 최신 PUBLISHED content commit guard, NCP read-only inventory/CPU 보호/locked compile/native 실행은 기존 handoff와 실제 runner에 남는다. 이 검토가 미게시를 게시로 바꾸거나 native NOT_RUN을 완료로 바꾸지 않는다.

## 6. 상태

| 실행 | 게시 | 백업 | DAG |
|---|---|---|---|
| 최종 callback source 독립 검토 완료; 재현한 deadline 3개 수정 확인; 새 native/Rust/ODE 실행 0 | 이 검토의 GitHub write 0 | 새 source snapshot·red/recheck·검토 파일의 parent 전달 | 값/guard/key 이론→callback 구현→focused·독립 recheck 완료; runner·동일 binary 성능·native 노드 별도 |

global_error_bound=null. Full48/source-age/spectral/angular/Case B/signed Bianchi/full EoR/standalone Grackle parity HOLD는 유지한다.
