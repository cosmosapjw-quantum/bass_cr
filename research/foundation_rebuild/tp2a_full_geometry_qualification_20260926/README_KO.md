# TP2A derivative-aware full geometry qualification

기준 upstream: `research/fnd-tp2a-derivative-aware-20260926` at `fdb89175cb9cd34e08b040600f56589b4e6248c1`.

이 sidecar는 이미 승인된 z=-6 qualification 뒤의 남은 9개 geometry만 순서대로 검사한다.

```text
z/a0 = -4,-2,0,+2,+4,+6,+8,+10,+12
```

각 geometry에서 6개의 독립 계산을 병렬 실행한다.

- candidate: phase-aware panels, Gauss order24, phase budget 24 rad
- reference: original panels, Gauss order32
- 각각 z-epsilon, z, z+epsilon, epsilon_z=1e-4 a0
- same-center order20
- 동일 18-channel FEM basis, 동일 native ring evaluator

geometry 순서는 gate의 일부다. 한 geometry가 실패하면 뒤 geometry는 새로 제출하지 않는다. 같은 geometry 내부에서 이미 제출된 6개 task는 완료될 수 있다. order40 자동 승격, epsilon/threshold/basis 변경은 없다.

## durable execution

각 operator task는 완료 즉시 `tasks/<task_id>.npz`와 hash receipt로 원자적 create-only 저장된다. `--resume-from`은 기존 output을 수정하지 않고 새 output으로 exact context가 일치하는 task만 복사한다. source, basis, native binary, contract가 달라지면 reuse를 거절한다.

worker마다 BLAS/OpenMP thread는 1이다. process 수는 `--workers`로 지정하거나 실제 affinity/core/memory 한도에서 자동 선택한다.

## 실행

이전 TP2A 성능 benchmark에서 빌드한 native directory를 그대로 사용할 수 있다.

```bash
BASE=research/foundation_rebuild/tp2a_full_geometry_qualification_20260926
OUT_FULLG="runs/tp2a_full_geometry_qualification_$(date -u +%Y%m%dT%H%M%SZ)"

python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" \
  --workers 8 \
  --out "$OUT_FULLG" \
  --expected-commit "$(git rev-parse HEAD)"
```

다른 터미널에서 실제 output 경로의 `PROGRESS.jsonl`을 읽는다. 실행 중 `OUT_FULLG`를 새 date로 다시 만들지 않는다.

```bash
tail -f "$OUT_FULLG/PROGRESS.jsonl"
```

중단 후 명시적 resume는 새 폴더로만 수행한다.

```bash
OUT_RESUME="runs/tp2a_full_geometry_resume_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" --workers 8 \
  --resume-from "$OUT_FULLG" --out "$OUT_RESUME" \
  --expected-commit "$(git rev-parse HEAD)"
```

정상 최종 상태는 `TP2A_DERIVATIVE_AWARE_FULL_GEOMETRY_PASS`다. 이것은 9개의 이산 geometry qualification이지 연속 궤적 오차상한이 아니다.

항상 다음 claim ceiling을 유지한다.

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```
