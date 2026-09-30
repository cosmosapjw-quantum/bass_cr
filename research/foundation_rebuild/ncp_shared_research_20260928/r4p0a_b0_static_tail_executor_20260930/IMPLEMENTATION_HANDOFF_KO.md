# B0 static tail runtime binding

Stop: R4P0_B0_OPERATOR_EXECUTOR_READY__EXPLICIT_NATIVE_AUTH_PENDING.

이 문서는 native 승인이 아니다. 이번 연결 작업의 new_native_operator_evaluations=0,
new_authorization_consumed=0이다. 새 source identity, live proposal bytes 및 명시적 승인 이후에만
B0 signed8 operator-only 실행을 허용한다. 기존 A3, 준비 f7b5eef, 연구432010f는 실행 identity가 아니다.

## 변경 범위

전달 projector_rate_probe.py와 tail_plan_adapter.py를 byte-preserving 재사용한다.
연구 CODEX_HANDOFF_KO.md도 원본 그대로 보존한다. static_tail.py/tail_worker.py는 기존
R4F initialize_worker/compute_query, ResolutionQualifiedProvider, AnalyticEvaluator,
GlobalBudget, validate_pair/publish_pair/dispatch_bounded에 연결하는 얇은 adapter다.
기존 numerical source/library/BUILD 및 모든 기존 파일은 변경하지 않는다.

R4P0_PLAN_ONLY ID는 사용할 수 없다. 전달 bind_runtime_plan이 생성한 별도 context/runtime IDs
8개만 dispatch한다. time_hex는 float.fromhex로 복원한다. +z/−z 복사, interpolation,
새 parity, FD, baseline rerun, warmup query 또는 tuning pilot이 없다.

BASIS.npz는 sealed verified A3 archive의 manifest에 고정된 bytes를 회수했다.
SHA256 및 size는 BINDING_INPUTS.json을 확인한다. load_bank는 저장된 coefficient를 읽기만 한다.
새 atomic_bank 생성, native rebuild, backend fallback은 없다. raw NPZ는 Git에 넣지 않는다.
검증된 runtime/fixture bytes는 portable package에 포함된다.

## 실행·권한

prepare_authority.py가 final clean HEAD/tree/source/input/native/query plan pins를 기계적으로
생성한다. source dependency closure는 DEPENDENCY_CLOSURE.json에 고정한다.
실제 live affinity/quota/RAM/peer pressure/own-group census를 저장하고,
4 worker·hard max8·thread1·wall3600s·grace60s를 미승인 제안으로 반환한다.
확장 pilot/자동 scaling은 없다. 자원 변경은 새 proposal과 사용자 결정이 필요하다.
비용은 별도의 새 scope로 최대 KRW10000(VAT포함)을 제안한다. A3 남은 예산을 상속하지 않는다.
이는 provider 가격이나 성능 보증이 아니다. monetary cap은 코드가 집행하지 않으며
사용자/provider가 승인한 외부 비용 통제가 필요하다.

AUTHORIZATION_PROPOSAL.json은 USER_APPROVAL_REQUIRED다. 이 원본 JSON SHA를 승인문에
포함하고, 승인 후 이를 수정/normalize/regen/substitute하지 않는다.
CLI는 외부 승인 token 및 exact approved proposal SHA를 동시에 요구한다.
모든 scope/source/bank/native/environment/resources 확인을 통과한 후에만
PROPOSAL_PIN.json과 EXECUTION_ADMISSION.json을 durable 기록하고 기존 account-wide
bass_r4c/authorizations의 create-only consume_authorization을 한 번 사용한다.
새 R4P0 ID만 허용하며 과거 A3 ID/nonce/wall/raw budget을 재사용하지 않는다.

native pool은 spawn이고 worker마다 pinned source와 exact bank/native/BUILD를 확인한 후
기존 initializer를 호출한다. GlobalBudget(parent_attempts=0, maximum=88)은 실제 raw 평가
시작 전에 원자적/durable reservation을 기록한다. 각 query 내부 11-resolution ladder와
first-passing adjacent pair 선택 순서가 그대로다. 내부 native contraction 수와 raw attempts는 다르다.

런처는 Git mode100644이며 future 승인 이후에만 bash로 호출한다:

```bash
export BASS_R4P0_PYTHON=/exact/prepared/python
export R4P0_PROPOSAL=/exact/sealed/AUTHORIZATION_PROPOSAL.json
export R4P0_SOURCE_PINS=/exact/sealed/SOURCE_PINS.json
export R4P0_INPUTS=/exact/sealed/runtime_inputs
export ANALYTIC_BUILD=/exact/sealed/native_build
export R4P0_APPROVED_PROPOSAL_SHA256=<exact explicitly approved proposal SHA>
export ALLOW_NEW_NATIVE_R4P0=YES_I_AUTHORIZE_EIGHT_B0_STATIC_SNAPSHOTS
bash "$SIDE/run_b0_tail_science.sh" "$OUT"
```

임의 chmod/direct execution은 필요 없다. 승인 없이는 launcher/supervisor가 child/native pool을
시작하지 않는다. -I Python 및 전용 start_new_session process group을 사용한다.
기존 supervisor의 group termination/partial packager를 재사용한다.
Future.cancel/shutdown(wait=False)는 종료 receipt가 아니다. 첫 실패 파일을 supervisor가 관측하면
정확한 자기 process group에만 SIGTERM→approved grace→필요시 SIGKILL을 적용하고 실제 종료를 확인한다.
Deadline은 min(승인 absolute deadline, 실제 시작+wall cap)이며 연장하지 않는다.

## 자원 정책

COOPERATIVE_SHARED_HOST: 외부 BASS peer와 broad affinity 교집합은 telemetry다.
그 PID/PGID/SID/state/redacted cmdline/affinity/cgroup/intersection/CPU-pressure를 보존한다.
허용 CPU affinity, finite quota, RAM, 자기 worker teardown, identity, budget, deadline는 hard gate다.
타 연구 job에 kill/stop/repin/renice/cgroup 변경을 수행하지 않는다.

## 결과 의미와 failure 보존

worker private task의 ordered raw payload/ledger/JSON+NPZ를 validate_pair로 확인한 뒤 create-only
canonical cache에 게시한다. Qualified matrices를 먼저 게시하고 snapshot_diagnostics로 해당 row의
실제 z/R/time metadata를 기록한다. Diagnostics 실패도 원 qualified pair를 잃지 않는다.
First failure와 orphan/partial task bytes는 supervisor return archive에 보존한다. 자동 retry가 없다.

rho는 Sdot=D+D† 가정의 local Galerkin diagnostic이다. 독립 derivative validation이 아니며
continuous tail bound 또는 finite-window certificate가 아니다. 새 tail에는 state가 없으므로
P_selected_at_this_tail_sample=null, Pdot_at_this_tail_sample=null이다.

실행 static screens는 raw_cross_relative_max=1e−9, operator_hermiticity_relative_max=1e−11,
metric_min_ratio=1e−8 세 개뿐이다. Derivative/temporal/trajectory norm 검사는 미수행으로 기록한다.
기존 denominator/tolerance/floor 및 qualification 조건은 수정하지 않는다.

정상 종료도 R4P0_B0_EIGHT_STATIC_SNAPSHOTS_COMPLETE__TAIL_GATE_UNRESOLVED다.
결과는 diagnostic snapshots이며 asymptotic/production capture 승인이 아니다.

## 비-native 검증/portable closure

전달25 tests와 변경된 연결 경계만 수행한다. 기존 preparation40 및 unchanged full suites는 재실행하지 않는다.
Synthetic evaluator로 unchanged worker/provider→global reservation→durable pair→local diagnostic을 검증한다.
승인 없음/소비 ID/잘못된 pin, unexpected time/ID, cap88, qualification failure, deadline, postprocessor failure,
cooperative peer/no mutation 및 own-pool leak를 검증한다. Native factory 및 CDLL trap은0이다.

verify_binding_package.py는 독립 package SHA/CRC/manifest/source/authority pins 확인 후 빈 디렉터리에
추출하여 py_compile과 전달·연결 suite를 수행한다. 외부 PYTHONPATH/source/bank/build 의존성을 제거한다.
실제 성공한 경우에만 SELF_CONTAINED_TEST_REPLAY_VERIFIED=true로 외부 receipt에 기록한다.
원 source/input paths의 실제 Git commit 비교는 별도 독립 review에서 확인한다.

No B1/B2/B3 runtime, no full transport, no N3072, no reference rerun,
no automatic retry, no capture/all-bound/b-grid promotion.

capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false; continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
