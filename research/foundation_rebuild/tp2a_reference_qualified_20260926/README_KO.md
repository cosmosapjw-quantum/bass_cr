# TP2A reference-qualified full geometry qualification

기준 upstream: `research/fnd-tp2a-full-geometry-qualification-20260926` at `f88199d639341036c12d82c8289cb93b5e9410d8`.

이 sidecar는 `z=-4 a0`에서 드러난 **미수렴 reference32를 candidate 실패로 오분류하는 문제**를 수정한다. 기존 실패 run과 branch는 변경하지 않는다.

## 고정 정책

남은 geometry:

```text
z/a0 = -4,-2,0,+2,+4,+6,+8,+10,+12
```

candidate는 그대로 유지한다.

```text
phase-aware panels
Gauss order = 24
phase budget = 24 rad
epsilon_z = 1e-4 a0
same-center order = 20
```

reference는 더 이상 `q32`라는 이름만으로 정확하다고 간주하지 않는다. geometry마다 다음 ladder를 순서대로 계산한다.

```text
q = 32, 40, 48, 56, 64
```

더 높은 order `q_i`를 qualified reference로 채택하려면 다음을 모두 만족해야 한다.

1. `q_{i-1}`와 `q_i`가 각각 자신의 `Sdot = D + D†` connection screen `<=1e-6`를 통과한다.
2. 두 order 모두 S/H Hermiticity `<=1e-11`, metric ratio `>=1e-8`를 통과한다.
3. 세 stencil node의 raw `S_tp,S_pt,H_tp,H_pt,D_tp,D_pt`에서 `q_{i-1}->q_i` 최대 상대차가 `<=1e-9`다.

reference가 qualified 된 **후에만** candidate phase24를 계산하고 candidate 자체 connection/operator screens와 qualified reference에 대한 raw-cross `<=1e-9`를 검사한다.

ladder `64`까지 소진해도 reference가 qualified 되지 않으면:

```text
REFERENCE_CONVERGENCE_UNRESOLVED
```

으로 중단한다. 이것은 candidate numerical FAIL이 아니다. 자동 q>64, epsilon 변경, threshold 완화, basis 변경은 없다.

## z=-4에서 정책을 바꾼 근거

보존된 실패 run:

```text
plain q32 connection     = 5.286887e-4  FAIL
phase24 connection      = 1.626094e-9  PASS
phase24 / q32 raw diff  = 4.991643e-5  FAIL comparison
```

별도 reference audit에서는:

```text
plain q40 connection           = 5.300614e-9
plain q48 connection           = 1.628330e-9
q40 / q48 raw max difference   = 3.262381e-10
phase24 / q48 raw max diff     = 3.587532e-15
phase-budget12 / q48 raw diff  = 4.206492e-15
```

따라서 candidate를 수정하지 않고 reference 자체를 먼저 수렴검증한다.

## 실행

이전 성능 단계에서 만든 동일 native build를 사용한다.

```bash
BASE=research/foundation_rebuild/tp2a_reference_qualified_20260926
OUT_REFQ="runs/tp2a_reference_qualified_$(date -u +%Y%m%dT%H%M%SZ)"
echo "OUT_REFQ=$OUT_REFQ"

python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" \
  --workers 8 \
  --out "$OUT_REFQ" \
  --expected-commit "$(git rev-parse HEAD)"
```

runner는 한 geometry에서 q32+q40의 6개 reference task를 첫 batch로 병렬 실행한다. 아직 수렴하지 않으면 q48/q56/q64를 각각 3개씩 필요한 만큼만 추가한다. reference가 qualified 되기 전에는 candidate task를 제출하지 않는다. geometry가 PASS하면 다음 geometry로 진행한다.

진행상황:

```bash
tail -f "$OUT_REFQ/PROGRESS.jsonl"
```

중단 후 resume은 동일 run을 덮어쓰지 않고 새 output으로만 수행한다.

```bash
OUT_RESUME="runs/tp2a_reference_qualified_resume_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" --workers 8 \
  --resume-from "$OUT_REFQ" --out "$OUT_RESUME" \
  --expected-commit "$(git rev-parse HEAD)"
```

context가 바뀐 옛 f88199 run의 task를 자동 import하지 않는다. 그 실패와 receipts는 immutable evidence로 보존한다.

정상 전체 상태:

```text
TP2A_REFERENCE_QUALIFIED_FULL_GEOMETRY_PASS
```

하지만 이것은 9개 이산 geometry의 operator/connection qualification이다. 연속 궤적 오차상한, capture, production admission이 아니다.

항상:

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```
