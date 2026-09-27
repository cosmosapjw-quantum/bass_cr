# TP2D runtime self-qualified full-window transport

TP2C는 동일한 analytic s+p backend로 `z/a0=-12,-10,...,+12`의 13개 이산 full18 geometry를 닫았다. TP2D는 그 정적 결과를 단순 보간하지 않는다. 대신 full-window transport가 실제로 요청하는 각 고유 시간 `t`에서 finite reference-resolution ladder를 직접 올리고, 서로 다른 인접 resolution 두 개가 operator screen과 raw cross convergence를 동시에 통과한 경우에만 높은 resolution의 `S,H,D` snapshot을 반환한다.

따라서 TP2D 성공의 의미는 다음 두 문장으로 제한한다.

```text
all_runtime_operator_queries_qualified = true
full_window_transport_qualified = true
```

이는 모든 실수 시간에 대한 global supremum certificate가 아니다.

```text
continuous_trajectory_error_bound = false
continuous_global_supremum_bound = false
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```

## Operator policy

- basis: 기존 18-channel full FEM
- angular backend: `EXACT_SP_MOMENTS_CXX_V1`
- interpolation: 사용하지 않음
- phase-budget candidate q24 semantics: 사용하지 않음
- runtime reference ladder: `(32,1),(40,1),(48,1),(56,1),(64,1),(48,2),(56,2),(64,2),(48,4),(56,4),(64,4)`
- 선택 규칙: ordered ladder에서 서로 다른 인접 resolution 두 개가 각각 Hermiticity/metric screen을 통과하고 raw cross relative difference `<=1e-9`이면 높은 resolution을 선택
- exact-time cache: 같은 binary64 time은 같은 qualified snapshot을 재사용
- maximum unique runtime queries: 2048
- 각 새 qualified query는 `runtime_queries/<query_id>.json/.npz`로 즉시 create-only 저장

## Transport policy

Reference는 generalized ODE

`i S dc/dt = (H - iD)c`

를 DOP853 (`rtol=1e-10`, `atol=1e-12`)으로 `z=-12 -> +12 a0` 전 구간에서 적분한다. Reference sample은 13개 기존 static node에 저장되지만 solver 내부의 모든 adaptive RHS time도 동일 self-qualification을 통과해야 한다.

Candidate는 TP1에서 검증한 Cholesky metric-frame midpoint exponential을 재사용한다. step ladder는 `24,48,96,192,384`이며, 인접 두 candidate의 final metric distance, 높은 candidate와 DOP853 reference의 final metric distance, 두 candidate의 weighted norm drift가 모두 frozen screen을 통과한 최초 높은 step count에서 멈춘다. Ladder가 끝나도 통과하지 못하면 `TEMPORAL_REFINEMENT_UNRESOLVED`다.

`Sdot=D+D†`는 `z/a0=-12,-6,0,6,12` sentinel에서 `epsilon_z=1e-4 a0` centered difference로 별도 검사한다. 이 sentinel 검사는 전 구간 supremum bound로 승격하지 않는다.

## Local execution

전달 메시지의 exact TP2D commit/tree로 checkout한 뒤 TP2B에서 이미 검증한 analytic build와 TP2C return bytes를 그대로 사용한다.

```bash
ROOT="$(git rev-parse --show-toplevel)"
export BASS_ANALYTIC_SOURCE_ROOT="$ROOT"
BASE="research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927"
ABUILD="runs/tp2b_analytic_build_20260926T233647Z"
PREV="runs/tp2c_analytic_negative_tail_20260927T021110Z"
PREV_ZIP="runs/tp2c_analytic_negative_tail_20260927T021110Z_RETURN.zip"
OUT="runs/tp2d_runtime_self_qualified_$(date -u +%Y%m%dT%H%M%SZ)"

python3 "$BASE/run_tp2d.py" \
  --analytic-build "$ABUILD" \
  --predecessor-report "$PREV/RETURN_REPORT.json" \
  --predecessor-archive "$PREV_ZIP" \
  --out "$OUT" \
  --expected-commit "$EXPECTED_SHA"

echo "EXIT=$?"
```

진행은 `tail -f "$OUT/PROGRESS.jsonl"`로 확인한다. 새 tests만 실행하며 TP1/TP2B/TP2C의 이미 통과한 suite는 재실행하지 않는다.

## Resume semantics

중단된 동일 TP2D context에 대해서만 새 output directory로 `--resume-from`을 허용한다. Basis bytes와 `SCIENCE_CONTEXT.json`이 정확히 일치해야 하며, hash-valid runtime query cache만 복사한다. ODE state 자체를 이어 적분하는 것이 아니라 deterministic rerun에서 동일 exact time query가 다시 발생할 때 저장된 qualified operator를 재사용하는 방식이다. Scientific FAIL을 resume로 PASS로 바꾸지 않는다.
