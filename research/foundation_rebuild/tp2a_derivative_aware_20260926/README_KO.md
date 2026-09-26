# TP2A derivative-aware z=-6 qualification

이 sidecar는 `perf/fnd-tp2a-20260926`의 원본 order24 실패를 보존하면서, 진단 루프에서 독립적으로 수렴한 두 후보를 같은 새 basis에서 비교한다.

- candidate: 기존 Gauss order24 + longitudinal phase panel subdivision (`phase_budget_rad=24`)
- reference: 기존 panel + Gauss order32
- geometry: z=-6 a0, epsilon_z=1e-4 a0
- same-center order20, 동일 18-channel FEM basis
- direct D, weak H, Bessel azimuthal moments 유지

PASS는 z=-6의 derivative-aware integration qualification만 뜻한다. 전체 13-point trajectory, capture, production, all-bound, b-grid는 승인하지 않는다.

## 검증 상태

진단 패키지의 저장 증거 replay는 217개 파일 identity를 확인한 뒤 다음을 재계산했다.

- historical order24 residual: 2.401921967602956e-4
- order32 residual: 1.852590545006579e-9
- order40 residual: 1.83748171480019e-9
- phase-split order24 residual: 1.842157175109227e-9
- phase-split order24 vs order40 raw TP 최대 상대차: 4.490049543571318e-15

repo-integrated sidecar 신규 시험은 10 passed. 이 assistant 컨테이너에서는 18-channel qualification runner가 실행시간 제한에 걸려 완주 증거가 없으므로, 최종 end-to-end는 사용자 로컬에서 수행한다.

## 실행

기존 perf branch에서 만든 native build 경로를 재사용할 수 있다.

```bash
BASE=research/foundation_rebuild/tp2a_derivative_aware_20260926
OUT_Z6="runs/tp2a_zminus6_qualification_$(date -u +%Y%m%dT%H%M%SZ)"

python3 "$BASE/run_zminus6_qualification.py" \
  --native-build "$BUILD_TP2A" \
  --workers 6 \
  --out "$OUT_Z6" \
  --expected-commit "$EXPECTED_SHA"
```

정상 상태는 `ZMINUS6_DERIVATIVE_AWARE_QUALIFICATION_PASS`다. 결과에 phase24/reference32 connection residual과 raw cross relative differences가 기록된다.
