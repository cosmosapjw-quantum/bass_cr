# TP2A analytic angular contraction + exact reflection pruning

이 디렉터리는 `fa5903a54c57326c12d7f60cb2444c68a8eb2392` 위에 추가되는 **source-only integration sidecar**다.

채택된 코드는 다음 세 가지를 구현한다.

1. s+p 기저에서 방위각 ring sampling을 J0..J3의 정확한 moment contraction으로 대체한다.
2. 고정 xz 충돌평면과 even 초기상태에서 reflection-odd p_y 네 채널의 exact invariant sector를 분리한다.
3. 동일한 effective quadrature 요청은 candidate/reference 역할 이름과 무관하게 canonical numerical key로 한 번만 계산한다.

물리적 FEM basis, weak-form H, direct D, radial quadrature의 정확도 gate는 변경하지 않는다. odd 초기상태, 비평면 운동, 불완전한 p multiplet에는 pruning을 적용하지 않는다.

## 검증 provenance

전체 연구 패키지 `BASS_TP2A_ANALYTIC_PRUNING_20260926.zip`의 사용자 로컬 확인에서:

- stored evidence replay: PASS, 748 files verified
- z=0 six-node: `ANALYTIC_Z0_QUALIFICATION_PASS`
- connection residual q56/q64: 약 2.32537e-9
- independent stored ring 대비 raw max: 약 1.31e-14
- q56->q64 raw max: 약 1.38e-14
- unique operator evaluations / role requests: 6 / 9

이 GitHub sidecar에는 **소스·수학 증명·fixture-independent unit tests만** 포함한다. z=0 BASIS/NPZ와 rejected polar-shell 실험은 용량과 역할 분리를 위해 durable research ZIP에 유지한다. 따라서 이 branch 자체를 `ANALYTIC_Z0_QUALIFICATION_PASS`의 새로운 독립 실행 증거로 세지 않는다.

## source-only 검증

repo root를 dependency source로 명시한다.

```bash
BASE=research/foundation_rebuild/tp2a_analytic_pruning_20260926
export BASS_ANALYTIC_SOURCE_ROOT="$(git rev-parse --show-toplevel)"
BUILD="runs/analytic_moments_build_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/code/build.py" --out "$BUILD"

BASS_MOMENT_BUILD="$BUILD" \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  "$BASE/tests/test_analytic.py" \
  "$BASE/tests/test_task_plan.py"
```

assistant shipping environment의 fresh source-only proof는 g++ build PASS, `19 passed`, py_compile PASS였다. 사용자의 z=0 heavy validation은 위 durable package에서 별도로 PASS했다.

## 다음 통합 gate

이 branch는 기존 HP/full-geometry qualifier를 자동으로 교체하지 않는다. 다음 단계는 analytic backend를 기존 resolution-qualified geometry policy에 연결하는 별도 contract다. 그 전까지 기존 결과와 실패 receipts는 immutable evidence로 유지한다.

항상:

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```
