# R3M21: incoming production-H CF4 외부 기준해 해상 시도

입력은 게시된 `cr/r3m19-n1-gpu-short-window-20260923` exact HEAD `7b731c85d663707b3657ae7c1b4b709f1a2558af`이다. 이번 별도 branch `cr/r3m21-cf4-reference-resolution-20260923`에서 `N1_TDL_PRODUCTION_H_CF4_OUTER_REFERENCE_RESOLUTION_AT_INCOMING_CHECKPOINT` 하나만 실행했다. B2 incoming `g000384`의 보존된 상태 SHA-256 `eaad0a24ae65edec6a6609abf7fbdb5f690cdb77b820d1b8a65426ddd12ebf55`를 다시 계산하여 일치함을 확인했다. 사용한 horizon은 기존과 같은 B2 dt 4배 `0.04999569408955976` au이며 같은 production h/box/CAP/energy/b와 frozen numerical source를 썼다. 원본 checkpoint는 읽기 전용이다. 새 full collision, preparation, finer h, 다른 checkpoint 창, representation 변경, projection, checkpoint write는 0회다.

기존 tiny dense/DOP853 독립 결과 `MATRIX_FREE_TINY_v3.json`의 네 사례는 1% oracle-resolution gate를 통과한 그대로 유지했다. 새 CPU 시험은 같은 외부 step에서 action 분할 수를 4/8로 바꾸는 차이와 inner tolerance 차이를 구분하며 2 passed였다. 전체 `tests/` 실행은 **356 passed, 0 skipped**였다. 이는 production grid의 독립 ODE 기준해가 아니다.

새 GPU 전파 job은 **1개**였다. 실행 전 B2 SHA guard와 production 63M점 allocation/matvec probe가 통과했고, 실측 GPU matvec median `0.101783`초에서 975.29초를 계획값으로 예측했다. 실제 job wall은 `774.429`초, 창 wall `772.264`초, preflight 포함 FFT matvec `3,715`회였다. 1,800초/7,200초/4,000회 상한 안이며 기록된 최소 GPU free는 `6,216,548,352` bytes였다. 예측과 실측은 별개다.

| CF4 설정 | matvec | 전파 wall 초 | 최대 basis | 최대 inner residual indicator |
|---|---:|---:|---:|---:|
| 4-step, 8 action substeps, tol 1e−12 | 384 | 84.743 | 6 | 5.85e−14 |
| 8-step, 8 substeps, tol 1e−12 | 640 | 131.681 | 5 | 1.79e−13 |
| 8-step, 4 substeps, tol 1e−12 | 384 | 85.199 | 6 | 5.85e−14 |
| 16-step, 4 substeps, tol 1e−12 | 640 | 131.981 | 5 | 1.79e−13 |
| 32-step, 4 substeps, tol 1e−12 | 1,024 | 195.619 | 4 | 1.87e−12 |
| 16-step, 4 substeps, tol 1e−13 | 640 | 132.252 | 5 | 1.79e−13 |

이전 4-step/8-step endpoint SHA는 같은 설정에서 **둘 다 byte-identical하게 재현**됐다. 따라서 직전 4→8 raw 거리 `2.103970853e−12`도 재현됐다. 그러나 이번 16→32 raw 거리는 `4.276093240e−11`로 커졌다. 같은 외부 8-step에서 action substeps만 8→4로 바꾼 차이도 `2.065382153e−12`였다. 16-step tol `1e−12→1e−13`의 두 endpoint는 동일했다. 등록된 1% 판정 한계는 측정된 4→32 거리 `4.274179310e−11`의 1%, 곧 `4.274179310e−13`이다. 16→32 차이와 8-step action-substep 차이가 이 한계를 각각 초과했으므로 **`REFERENCE_UNRESOLVED_ONE_PERCENT_GATE`**다. 기존 4→8 거리의 1%인 `2.104e−14`를 한계로 삼아도 실패한다.

이 패턴은 외부 timestep 변화와 inner action 근사/누적 효과가 아직 분리되지 않았음을 보여준다. 특히 32-step의 최대 경험적 Arnoldi indicator가 16-step보다 크고 action-substep 민감도가 이전 4→8 신호와 비슷하다. 이것만으로 특정 구현 결함 또는 참 외부 시간오차의 크기를 확정할 수 없다. 16-step tolerance repeat의 0 차이는 해당 두 계산이 같은 basis/endpoint를 선택했다는 관측이며 true inner error 0의 증명이 아니다. 32-step은 tighter-inner repeat가 없고 production 독립 ODE 기준해도 없다. 기존 R3M19 refined h=.20 CF4 oracle FAIL과 R3M20 조건부 결과를 소급 변경하지 않는다.

따라서 CF4 32-step을 새 기준해로 승격하지 않고 정확도 맞춤 GPU speedup도 주장하지 않는다. `TIME_REFINEMENT_STILL_OPEN`, production `HOLD`, b-grid `NO_GO`를 유지한다. 공간, CAP, preparation, all-bound, b 적분, physical rate의 gate도 열려 있다. 다음 canonical node는 정확히 하나: `N1_TDL_PRODUCTION_H_INNER_ACTION_ERROR_CONTROL_AND_CF4_REFERENCE_RETRY`. 그 node는 누적 inner error가 외부 시간차보다 충분히 작아지도록 tol/action-substep 선택을 먼저 검증한 뒤 새 자원 계약에서 한 번만 같은 incoming 창을 재시험해야 한다. 이번 job을 자동 재시도하지 않았다.

독립 검토는 이번 node에서 확보되지 않았다. 기존 reviewer의 새 작업 follow-up은 `CHILD_CONTINUATION_NOT_RESERVED`, 등록된 새 reviewer 실행은 `CLIENT_WORKTREE_MISMATCH`로 차단됐다. 이는 수치 실패가 아닌 reviewer 실행 경계다. Host가 source SHA, checkpoint/preflight/result 해시, 예산, raw 거리와 시험을 재검산한 `HOST_VALIDATION.json`은 독립 검토를 대체하지 않는다. 게시된 결과는 evidence-bound HOLD이며 독립 scientific admission 주장이 아니다.
