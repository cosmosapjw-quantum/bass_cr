# BASS_CR D5A 재감사 및 static cross repair

기준 source: `8b7fef411ebca8dcdbfb45de542690c821fd7826`

이 디렉터리는 기존 production source를 교체하지 않는 독립 재감사/repair sidecar다.

## 확인된 범위

- D3 same-center support 오류를 보존된 증거에서 확인.
- D5A의 eta 미수렴을 순수 longitudinal ETF under-resolution로 단정할 수 없음을 반례로 확인.
- 기존 18-channel FEM basis를 유지한 채 interface-aligned two-distance quadrature와 phase-exact azimuthal Bessel moments를 사용.
- z=-12 a0 static TP/PT에서 order 20 -> 24 relative Frobenius change:
  - S: 1.211037740302443e-11
  - H: 6.656547226773848e-12
  - D: 2.3884148807880013e-11
- smooth infinite-support Laguerre L2 radial basis를 비-FEM atomic comparator로 별도 구현.
- capture propagation, full S/H/D integration, production admission은 수행하지 않음.

현재 claim ceiling:
`production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture_execution_allowed=false`.

## 로컬 소형 검증

repo root에서:

```bash
PYTHONPATH="$PWD/research/foundation_rebuild/reaudit_20260925/repair:$PWD/research/foundation_rebuild/src:$PWD" \
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  research/foundation_rebuild/reaudit_20260925/tests/test_repair.py
```

기대 범위는 `34 passed`다. 이것은 GPU/full collision/production PASS가 아니다.

## opt-in static reproduction

이미 저장된 수치를 다른 호스트에서 재현할 필요가 있을 때만:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
python3 research/foundation_rebuild/reaudit_20260925/repair/run_cross_probe.py \
  --order 24 \
  --out runs/reaudit_cross_order24_local
```

출력 폴더는 create-only이며 기존 경로가 있으면 실패한다. GPU를 사용하지 않는다.

## GPU

이 repair는 기존 TDL GPU forward operator를 수정하지 않는다. 따라서 이 branch를 확인하기 위해 과거 B3 full GPU collision을 처음부터 다시 실행하지 않는다.

GPU/driver/CUDA 환경 자체가 바뀐 경우에는 먼저 `nvidia-smi`와 기존 작은 GPU runtime tests만 시행한다. 실제 Hamiltonian/grid/CAP/initial state 또는 propagation source가 변경될 때에만 새 identity의 forward run을 검토한다.

## 다음 canonical work unit

`FND_FULL_OPERATOR_INTEGRATION_FROM_VALIDATED_CROSS_V1`

검증된 TP/PT cross kernel을 올바른 full-support TT/PP와 결합하고 full metric 및 direct D를 검증하는 단계다. 그 전에는 capture pilot을 자동 실행하지 않는다.
