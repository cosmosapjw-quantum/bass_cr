# 독립 read-only 실행 반환 검토

검토 범위는 content `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`의 고정 offgrid4
와 attempt `20261021T131024Z_1428294_296968044871797`에 한정했다.

- 결과: `PASS_SCOPED`; 관측된 P0 없음.
- 네 사례 각각 COMPLETE 봉인, RESULT/history SHA, 고정 grid/source identity 일치.
- REI commit `3b85dedce84d37b3e165da00685a8a984950aafe`; grid SHA256
  `2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5`.
- source code SHA는 run `MANIFEST.json`에 포함되고 고정 content worktree와 대조했다.
- 네 좌표는 기존125 CSV의 좌표와 중복되지 않는다. raw 상태는 FP64 `40×101`, 유한하고
  eta가 단조다. 초기 target 및 결과 map은 준비 인증서와 일치한다.
- radiation 분할, `P_r=P_gamma+P_nu`, `P_tot=P_m+P_r`, full-Frobenius norm/half
  규약 잔차는 최대 `4.07e-20` 이하. 초기 cancellation은 약 1, z=4에는
  `0.38986365–0.38986642`다.
- 도함수 식 잔차 최대 `1.59e-18`; 이는 유한구간 error bound가 아니다.
- 전체 정확도·성능 향상은 검증하지 않았다. `global_error_bound=null`; general
  triaxial, full reionization, CMB는 HOLD.

이 검토는 raw를 수정하거나 ODE를 재실행하지 않았다.
