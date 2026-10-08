# R4P0A → B0-only signed tail execution handoff

ROLE=R4P0_B0_STATIC_TAIL_RUNTIME_BINDING_AND_AUTH_PROPOSAL
REPO=cosmosapjw-quantum/bass_cr

## 상태와 금지

R4P0 preparation은 검토·재현 완료다. 이전 gate를 다시 열거나 기존 A3/N1536을
재실행하지 않는다. 이 인계는 새 native 승인문이 아니다. native 호출/nonce 소비는
이번 binding 단계에서 모두0이어야 한다. 새 고유 one-shot 승인 이후에만 operator8점을
실행할 수 있다. B1–B3 higher-l 또는 full transport는 범위 밖이다.

INPUT_COMMIT=f7b5eef95895f299327562859ce0b278ffa8679c
INPUT_TREE=a48f84aa757da786304171c51458002707f72c6a
INPUT_BRANCH=codex/r4p0-tail-basis-preflight-20260930
INPUT_PACKAGE_BYTES=75053
INPUT_PACKAGE_SHA256=60ed70b65c8fd37fee8a6d7d83602ef20a0de4d745e68655502d9a45f5af5528

완료된 A3 science SHA는 원 R4P0 CONTRACT.json에서 읽는다. 사람이 해시를 다시
옮겨 적지 말고 실제 manifest로 source/input/native/plan pins를 생성한다.

## 전달 코드 재사용

이번 연구 패키지의 다음 파일은 이미 구현·비-native 검증되었다.

- projector_rate_probe.py: Q,Qdot,A,W와 generalized rho; 저장 endpoint postprocessing
- tail_plan_adapter.py: B0 signed8점 PLAN_ONLY→runtime ID binding 및 per-sample 진단
- BOUND_B0_TAIL_QUERY_PLAN.json: 실제8개 t/z/R과 runtime ID
- NEXT_SCOPE_CONTRACT.json: 범위 및 남은 runtime binding 분류
- tests/test_rate_probe.py, tests/test_tail_plan_adapter.py: 총25 passed
- fixtures/R4P0: 원본 prep source/정확한 입력의 재현 fixture

프로젝트의 source/권한 규칙을 먼저 읽는다. 전달된 구현을 다시 설계하지 말고
검증된 기존 scientific worker/provider/supervisor에 최소 연결한다.
Research commit 자체가 실행 commit은 아니다. 실제 연결이 끝난 source로 새 execution
commit/tree를 고정하고, 그때까지 NATIVE_READY라고 하지 않는다.

## 1. 고정 scientific scope

basis=B0, channels=18
energy=100 keV/u
b=2 a0
z_a0=[-16,+16,-20,+20,-24,+24,-32,+32]
new_unique_operator_queries=8
max_raw_operator_evaluations=88

8×11은 raw operator evaluation 상한이다. 내부 Coulomb/native contraction call 수와
구분한다. 새 parity, derivative finite-difference sample, warmup scientific query는
이88 안에 암묵적으로 추가하지 않는다. baseline z=12는 기존 저장값만 읽는다.

EXACT_SP_MOMENTS_CXX_V1, 원 B0 radial bank/coefficient identity,
same_center_order20, frame/ETF/trajectory, source/library/BUILD를 그대로 사용한다.
B1–B3는 registry만 존재하며 higher-l native 지원과 actual Gram을 미검증 상태로 유지한다.

11-resolution ladder와 기존 static screens를 유지한다:
raw_cross_relative_max=1e-9
operator_hermiticity_relative_max=1e-11
metric_min_ratio=1e-8

static provider는 metric_derivative_relative_max를 독립 검사하지 않는다.
해당 키가 과거 transport contract에 있다는 이유로 derivative PASS를 기록하지 말라.
Temporal/norm-trajectory/asymptotic gate 역시 이 operator-only job으로 닫히지 않는다.

## 2. 최소 native-runtime binding

기존 다음 primitives를 exact source에서 재사용한다:
- tp2d .../qualified_provider.py::ResolutionQualifiedProvider
- tp2d .../analytic_adapter.py::AnalyticEvaluator
- r4f_parallel_migration .../worker_runtime.py 의 pinned bank/native initialization
- r4f .../parallel_bridge.py 의 GlobalBudget, validate_pair 및 create-only publication
- 현재 cooperative resource census와 검증된 process-group supervisor

그들의 numerical implementation을 수정하지 않는다. 프리플라이트 입력에 실제
BASIS.npz/bank가 필요하면 verified A3 source에서 exact bytes만 가져온다. R4P0의
작은 postprocessing ZIP에 없는 native-runtime fixture를 존재한다고 가정하지 않는다.
Bank 재생성이나 .so rebuild/fallback은 승인 범위 밖이다.

새 bounded runner가 구현해야 하는 얇은 연결:
1. source/preparation/native/bank/plan identity와 아직 미소비된 승인 객체 검증;
2. tail_plan_adapter.bind_runtime_plan으로 기계적으로 재생성한 plan과 승인 plan SHA 비교;
3. 각 row의 time_hex를 float.fromhex로 읽고 기존 provider를 그 시간에 호출;
4. 새 tail context_id와 runtime_query_id를 사용. PLAN_ONLY ID를 cache ID로 쓰지 않음;
5. 전역 raw reservation을 각 실제 평가 시작 전 atomic/durable하게 수행;
6. qualified JSON+NPZ pair를 검증 후 create-only publish;
7. snapshot_diagnostics(S,H,D,row)로 실제 해당 row의 z/R/time을 기록;
8. 성공8/8 또는 실패/timeout partial manifest와 최초 실패를 보존하고 stop.

원 R4P0 preflight.operator_diagnostics는 z12 baseline용이다. 새 샘플에 그대로
호출하여 z/R를12로 찍지 말라. 전달된 per-sample adapter는 이를 이미 분리했다.

+z와-z를 한쪽 계산의 복사/켤레/대칭 가정으로 대체하지 않는다.
Interpolation, 같은 ID 덮어쓰기, 저해상도 fallback, 실패한 상대 screen의 자동
완화/분모 floor 조정은 금지한다. 필요하면 다음 연구로 실패를 정확히 반환한다.

## 3. 선택적 새 진단: W와 rho

일반 단위:
A=-(i/hbar) solve(S,H)-solve(S,D)
Q=SJ solve(J†SJ,J†S)
W=Qdot+A†Q+QA
rho=max(abs(generalized_eigenvalues(W,S)))

저장된 atomic-unit 행렬에 대해서만 hbar=1이다. J=[e9,e10,e12,e13,e14]를 사용한다.
Qdot는 제공 함수에서 Sdot=D+D† identity로 계산한다. 이것은 독립적인 실제
Sdot finite-difference validation이 아니라 exact Galerkin 가정 기반 local diagnostic이다.

새 tail point에는 state c(t)가 없으므로 rho는 계산 가능하지만 Pdot=c†Wc는 unavailable이다.
N1536 final c를 다른 시간에 붙여서 미래 Pdot나 P를 만들지 말라.

이번 stored z12 값은:
Pdot=+1.6382726202381236e-4 / atomic time
rho=6.2271258107070085e-3 / atomic time

이는 exact expected gate 값이 아닌 비교용 diagnostic이다. rho 추가를 위해 새로운
native query가 필요하지 않으며 raw qualification/gate/threshold를 바꾸지 않는다.
진단 코드에서 오류가 나면 원 qualified matrices를 먼저 보존한다.

||K_TP||, cross/full ratio 또는 소수표본 rho를 tail error certificate로 부르지 않는다.
원 R4O의 raw block 크기와 무차원 probability error를 직접 비교한 해석은 채택하지 않는다.

## 4. 자원과 권한

4 workers, 최대8 workers, one numerical thread/worker는 제안이다.
작업은8개뿐이므로32-worker tuning/pilot을 반복하지 않는다.
COOPERATIVE_SHARED_HOST 유지:
외부 BASS peer 존재·broad affinity 교집합은 telemetry일 뿐 hard blocker가 아니다.
다른 작업을 kill/stop/repin/renice/cgroup 변경하지 않는다.
Allowed affinity/quota/RAM/own worker teardown/identity/global budget/deadline는 계속 hard gate다.

새 CPU list, worker/RAM limits, wall/deadline/grace, cost scope, one-shot ID는 live census와
명시적 사용자 승인이 필요하다. wall3600s, grace60s는 미승인 제안이며 성능 보증이 아니다.
A3의 남은 raw 예산·과거 deadline·소비된 ID는 사용할 수 없다.

실행 도구의 세션 종료가 background job을 정리하는 문제를 피하려면 기존에 실제로
검증된 durable supervisor/session 방식을 그대로 사용한다. nohup만으로 생존을 보장한다고
가정하거나 조용한 자동 재시도/새 nonce를 만들지 않는다.

## 5. targeted acceptance 및 한 번의 반환

원본40 tests는 이번에 그대로 재현되었다. 원본 미변경 파일을 감사 목적으로 반복하지 말라.
전달 코드25 tests와 바뀐 binding 경계만 준비 환경에서 실행한다.

binding 최소 테스트:
- 승인 없음/소비된ID/잘못된pin이면 native factory 호출0;
- exact8 time만 가능하고 signed row/runtime query IDs가 plan과 일치;
- synthetic evaluator로 기존 ordered qualification→JSON/NPZ→diagnostics 경로 통과;
- 전역 max88 및 실패/timeout 시 extra dispatch 없음;
- cooperative external peer 통과, 자기 worker leak는 별도 hard fail;
- restore package에서 필요한 source/input fixture가 실제 있으며 native trap smoke0.

실제 native 결과가 아니면 그렇게 표시한다. 정상8점 표본이나 sparse empirical fitting으로
B0 full-window asymptotic gate를 닫지 않는다. 후속 window 비교는 endpoint 정의 및 초기
target1s 위치를 고정하고 time-step accuracy를 별도로 다뤄야 한다. B0의N1536 step count를
큰 window나 B1–B3에 그대로 certificate로 승계하지 않는다.

새 정확한 실행 commit/tree, 새 plan/source/native/bank pins, targeted tests,
portable package와 미승인 approval JSON을 한 번에 반환한다. 값들은 manifest에서 생성한다.
Report와 작은 코드만 non-force push; raw scientific NPZ는 Git에 중복 저장하지 않는다.
실패와 기존 과학 결과를 보존하고 main merge를 하지 않는다.
Backup은 원 project selective-readback policy를 따른다. R1/R2/R3와 실제 여부를 구분한다.

STOP_STATE=R4P0_B0_OPERATOR_EXECUTOR_READY__EXPLICIT_NATIVE_AUTH_PENDING

No new native execution in this binding task.
No B1/B2/B3 runtime, no full transport, no N3072, no reference rerun,
no capture/all-bound/b-grid promotion, no automatic retries.

capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false; continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
