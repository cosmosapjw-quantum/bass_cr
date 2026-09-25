# FND TP1 short-window metric transport

이 sidecar는 검증된 full finite-FEM S/H/D를 `z=-12 -> -10 a0` 짧은 구간에서 시간전파만 검증한다. capture observable, GPU, full collision, b-grid는 열지 않는다.

두 경로를 독립적으로 비교한다.

1. direct generalized ODE: `dc/dt = S^{-1}(-iH-D)c`, SciPy DOP853, rtol=1e-10, atol=1e-12.
2. Cholesky metric-frame candidate: `S=R†R`, `y=Rc`, raw `G=X-Dt-iHt`, fixed midpoint exponential with 8/16/32/64 steps.

`Sdot = D + D†`는 z=-12,-11,-10에서 centered finite difference (`epsilon_z=1e-4 a0`)로 별도 검사한다. `D`를 이 identity에서 재구성하지 않는다.

성공해도 다음 상태를 유지한다.

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```

실행은 create-only다. source manifest와 dependency pins를 확인한 뒤 신규 TP1 tests를 실행하고, 모든 gate가 통과한 경우에만 `TP1_SHORT_TRANSPORT_PASS`를 반환한다. 실패 시 첫 failure를 보존하고 자동 재시도하지 않는다.

## 구현단계 exploratory smoke

정식 18-channel confirmatory run 전에 동일 실행 경로를 2-channel 작은 FEM basis로 한 번 실행했다. 이것은 confirmatory evidence가 아니다. 이 smoke에서는 204개의 고유 operator evaluation이 발생했고, direct DOP853 reference의 `nfev=83`, metric-connection residual은 최대 약 `9.63e-8`, candidate64/reference 최종 metric distance는 약 `2.96e-9`, candidate32/64 차이는 약 `8.28e-9`였다. 정확한 값은 `EXPLORATORY_SMOKE.json`에 보존한다.

이 결과는 runner와 두 transport 경로의 integration smoke일 뿐이며, 18-channel basis나 capture physics를 승인하지 않는다.
