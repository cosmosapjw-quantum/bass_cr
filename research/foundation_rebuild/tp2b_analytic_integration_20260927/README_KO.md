# TP2B analytic backend × resolution policy integration

기준 branch는 `research/fnd-tp2a-analytic-pruning-20260926`이다. 이 sidecar는 이미 검증된 analytic s+p angular contraction을 기존 TP2A resolution-qualified geometry policy에 연결한다.

## 고정 범위

- geometry: `z/a0 = -4,-2,0,+2,+4,+6,+8,+10,+12`
- physical basis: 기존 18-channel FEM 그대로
- qualification sector: **full18 only**
- reference/candidate resolution ladders와 모든 numerical screens: 기존 `tp2a_reference_qualified_20260926`와 동일
- angular backend: `EXACT_SP_MOMENTS_CXX_V1`
- same-center weak operator: 기존 order20
- even14 pruning: 이번 operator qualification에는 사용하지 않음. 향후 planar/even initial-state transport에만 admissible
- legacy ring task import: 금지. backend identity가 다르므로 새 analytic context에서 다시 계산

## canonical task aliasing

candidate/reference 역할 이름은 numerical identity에 포함하지 않는다. 다음이 모두 같을 때에만 하나의 계산 결과를 공유한다.

- exact time
- Gauss order
- 실제 effective integration edges
- full/even sector
- basis/physics contract
- analytic source 및 native library identity

따라서 `z=0`처럼 longitudinal phase splitting이 실제 mesh를 바꾸지 않는 경우 같은 `(q, subdivisions)` candidate/reference 요청은 한 번만 계산할 수 있다. 이 공유는 `ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK`로 기록하며 독립 수렴 증거로 세지 않는다. Reference 자체는 인접한 서로 다른 resolution의 기존 독립 qualification을 먼저 통과해야 한다.

## 로컬 실행

```bash
EXPECTED_SHA=<push 후 제공되는 commit>
EXPECTED_TREE=<push 후 제공되는 tree>

git fetch origin refs/heads/research/fnd-tp2b-analytic-integration-20260927
test "$(git rev-parse FETCH_HEAD)" = "$EXPECTED_SHA" || exit 1
git switch --detach "$EXPECTED_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_TREE" || exit 1

ROOT="$(git rev-parse --show-toplevel)"
export BASS_ANALYTIC_SOURCE_ROOT="$ROOT"
ANALYTIC="research/foundation_rebuild/tp2a_analytic_pruning_20260926"
BASE="research/foundation_rebuild/tp2b_analytic_integration_20260927"

ABUILD="runs/tp2b_analytic_build_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$ANALYTIC/code/build.py" --out "$ABUILD"

OUT="runs/tp2b_analytic_geometry_$(date -u +%Y%m%dT%H%M%SZ)"
echo "OUT=$OUT"
python3 "$BASE/run_analytic_geometry_qualification.py" \
  --analytic-build "$ABUILD" \
  --workers 8 \
  --out "$OUT" \
  --expected-commit "$EXPECTED_SHA"

echo "EXIT=$?"
```

진행상황:

```bash
tail -f "$OUT/PROGRESS.jsonl"
```

중단 후에는 같은 analytic contract의 output만 새 directory로 resume한다.

```bash
OLD="$OUT"
OUT2="runs/tp2b_analytic_geometry_resume_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_analytic_geometry_qualification.py" \
  --analytic-build "$ABUILD" --workers 8 \
  --resume-from "$OLD" --out "$OUT2" \
  --expected-commit "$EXPECTED_SHA"
```

기존 ring-backend run에 대한 `--import-from`은 제공하지 않는다.

전체 성공 상태는 `TP2B_ANALYTIC_FULL18_GEOMETRY_PASS`다. 성공하더라도 이는 9개 이산 geometry의 full18 operator qualification이며 continuous trajectory bound나 capture admission이 아니다.

항상 `capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, original capture gap unresolved를 유지한다.
