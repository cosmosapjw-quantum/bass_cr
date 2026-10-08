# TP2C analytic negative-tail qualification + full13 static closure

TP2B local run은 analytic s+p backend로 `z/a0=-4,-2,0,2,4,6,8,10,12`의 9개 full18 geometry를 모두 통과했다. 그러나 전체 13-point trajectory의 앞쪽 `-12,-10,-8,-6`은 동일 analytic backend와 동일 resolution policy로 아직 닫히지 않았다. TP2C는 바로 그 네 점만 새로 계산한다.

이 노드는 과거 29-test TP2B suite를 다시 실행하지 않는다. 대신 사용자가 반환한 TP2B `RETURN_REPORT.json`과 `_RETURN.zip`의 exact SHA-256을 먼저 검증하고, TP2C에 새로 추가된 tests만 실행한다. 이전 ring/native task는 import하지 않는다.

성공 조건은 다음과 같다.

- predecessor TP2B report/archive bytes가 계약의 SHA-256과 일치한다.
- predecessor status/head/tree, 29/0/0/0 test count, 9개 geometry와 claim ceiling이 일치한다.
- analytic build source/library SHA-256이 TP2B에서 사용한 exact build와 일치한다.
- `z=-12,-10,-8,-6` 각각에서 기존 TP2B와 동일한 finite reference/candidate ladder 및 screens를 통과한다.
- 네 점 모두 통과하면 predecessor 9점과 합쳐 `TP2C_ANALYTIC_FULL13_STATIC_GEOMETRY_PASS`를 반환한다.

이 PASS는 13개의 **이산 static geometry**를 동일 analytic backend로 닫는 것이며, 연속 궤적에 대한 interpolation/operator error bound가 아니다. 따라서 capture는 여전히 금지한다.

```text
continuous_trajectory_error_bound = false
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```

## 로컬 실행

TP2B에서 검증한 기존 analytic build를 그대로 사용한다.

```bash
EXPECTED_SHA=<TP2C branch exact commit>
EXPECTED_TREE=<TP2C branch exact tree>

git fetch origin refs/heads/research/fnd-tp2c-analytic-negative-tail-20260927
test "$(git rev-parse FETCH_HEAD)" = "$EXPECTED_SHA" || exit 1
git switch --detach "$EXPECTED_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_TREE" || exit 1

ROOT="$(git rev-parse --show-toplevel)"
export BASS_ANALYTIC_SOURCE_ROOT="$ROOT"
BASE="research/foundation_rebuild/tp2c_analytic_negative_tail_20260927"
ABUILD="runs/tp2b_analytic_build_20260926T233647Z"
PREV="runs/tp2b_analytic_geometry_20260927T000504Z"
PREV_ZIP="runs/tp2b_analytic_geometry_20260927T000504Z_RETURN.zip"
OUT="runs/tp2c_analytic_negative_tail_$(date -u +%Y%m%dT%H%M%SZ)"

python3 "$BASE/run_negative_tail_qualification.py" \
  --analytic-build "$ABUILD" \
  --predecessor-report "$PREV/RETURN_REPORT.json" \
  --predecessor-archive "$PREV_ZIP" \
  --workers 8 \
  --out "$OUT" \
  --expected-commit "$EXPECTED_SHA"

echo "EXIT=$?"
```

진행상황은 `tail -f "$OUT/PROGRESS.jsonl"`로 본다. 중단되면 같은 TP2C context에 한해서 새 output directory로 `--resume-from`을 사용할 수 있다. 실패한 이전 scientific run을 PASS로 바꾸는 import 경로는 없다.
