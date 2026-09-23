# R3M22: incoming B2 full-H inner action 오차 제어와 CF4 기준해 재시험

입력은 별도 후속 branch에 게시된 R3M21 exact HEAD `d87c2924b659394885d16796fd8fe9a34f45d39f`이다. 이번 branch는 `cr/r3m22-inner-action-reference-20260923`이다. R3M20에서 고정한 B2 incoming `g000384` 상태 1,008,000,128 bytes의 SHA-256 `eaad0a24ae65edec6a6609abf7fbdb5f690cdb77b820d1b8a65426ddd12ebf55`와 B2 설정/선택/직전 실패 결과를 다시 검증했다. 동일한 6,300만 점 production h/box/CAP/energy/b, 동일한 4 B2-dt horizon `0.04999569408955976` au다. 새 full collision, preparation, finer h, representation 변경, 다른 checkpoint 창, projection, checkpoint write는 모두 0회다.

직전 R3M21의 최초 실패는 그대로 남아 있다. 그 결과는 CF4 16→32 raw 차이 `4.2760932402361476e−11`과 8-step action-substep 차이 `2.0653821525023145e−12`로 1% 기준해 gate를 통과하지 못했다. 이번에는 frozen `cr_repro`를 변경하지 않고 opt-in `scripts/r3m22_inner_action.py`를 추가했다. 두 번 재직교화한 비Hermitian Arnoldi action에 비팽창 semigroup의 정확산술 오차상한을 물리 L2 단위로 누적하고, 유한정밀도/FFT 잔차는 별도의 tolerance·substep repeat로 검사했다. 이는 부동소수점 전역 인증서가 아니다. Jawecki–Auzinger–Koch Theorem 1의 적용 조건과 이 구현의 dissipativity 조건은 `LITERATURE.md`에 기록했다.

생산 격자 전의 CPU 원본 `CPU_ORACLE.json`은 CAP on/off, 속도 부호, 64/96점 직사각형의 네 독립 dense-DOP853 사례에서 PASS를 기록했으나, **handoff가 요구한 최소 비교 오차가 아니라 거친 4→8 차이의 1%를 분모로 사용한 최초 gate 오류**가 있었다. Astra xhigh 독립 reviewer가 이 오류를 찾고 원래 n32 설정의 강화 inner/substep repeat가 올바른 최소-error 한계를 4.50–8.58배 넘는 것을 재현했다. 이 실패와 당시 잘못된 GPU 진입 판단은 보존한다. GPU 재실행 없이 수행한 사전 고정 CPU-only closeout은 같은 네 사례의 n32에서 global inner budget `1e−14`, tighter `1e−15`, substeps 4↔8을 비교했다. 각 사례의 n4/8/16/32 중 **최소 독립 DOP853 오차의 1%**를 한계로 하여 네 사례 모두 PASS였다. 예컨대 CAP-off에서 한계 `6.147e−13`에 대해 n32 tighter 차이 `1.724e−15`, substep 차이 `7.459e−15`이다. 이것은 후속 보완 검증이지 GPU 당시 선행 gate가 처음부터 유효했다는 소급 주장이 아니다. 새 action의 dense `expm` 회귀 4개가 통과했고, CodeRabbit가 지적한 수렴 전 큰 벡터 조립 비용을 고친 뒤 전체 테스트는 **361 passed, 0 skipped**였다. CodeRabbit 실제 committed-diff 검토는 major issue 1건이었고 수정했다. 독립 모델 검토는 별도 기록한다.

GPU는 RTX 3090 24 GiB, Ryzen 9 5900X affinity 12 physical cores, host RAM 약 101.14 GB에서 단일 job으로 실행했다. input guard, allocation 및 3회 matvec preflight가 PASS였다. 계획 상한 3,843 FFT matvec와 직전 job 기반 801.11초 예측은 실행 전 비용 추정이며 실측 성능이 아니다. 실제 job은 **2,827 FFT matvec, 650.404초**였고, 전파 창 wall은 **648.279초**였다. preflight 중 최소 GPU 여유 2,689,138,688 bytes, 전파 중 기록한 최소 여유 3,190,358,016 bytes로 모두 2 GiB 하한 위였다. preflight 시 host available은 81,241,849,856 bytes로 8 GiB 하한 위였다. 4,000 matvec/1,800초 창/7,200초 job 상한을 **실측으로는** 넘지 않았다. 독립 reviewer는 clock check가 matvec 시작 전에만 있고 마지막 matvec 후 terminal check가 없음을 지적했다. 그러므로 이 구현이 모든 가능한 실행에서 hard wall cap을 강제한다고 주장하지 않는다. 이번 기록의 650.404/648.279초는 충분히 상한 안이다. 최초 실패 파일은 생성되지 않았고 자동 재시도도 없었다.

기존 R3M20의 고정된 4→8 raw 신호 `2.103970853068276e−12`의 1%인 `2.103970853068276e−14`를 비교 한계로 **실행 전에 고정**했다. n32 한-step calibration의 substep2↔4 차이 `5.289e−16`, tighter-inner repeat 0은 한계보다 작았다. 따라서 같은 job 안에서 전체 incoming 짧은 창의 CF4 외부 사다리를 실행했다.

| CF4 외부 step | action substeps | FFT matvec | 전파 wall 초 | 정확산술 inner bound 합 |
|---|---:|---:|---:|---:|
| 4 | 2 | 160 | 41.065 | 2.868e−16 |
| 8 | 2 | 256 | 59.219 | 3.013e−15 |
| 16 | 2 | 448 | 97.998 | 2.980e−15 |
| 32 | 2 | 896 | 196.291 | 4.656e−17 |
| 16, tighter inner | 2 | 512 | 118.937 | 2.354e−17 |
| 8, substep repeat | 4 | 448 | 98.125 | 2.980e−15 |

같은 시작 상태와 종료 시각에서 raw 4→8/8→16/16→32 차이는 각각 `4.0106508177109755e−13`, `2.2854099499661647e−14`, `4.457098127159628e−15`이며 8→16 대 16→32 비는 `5.128`이다. n16 inner 강화 차이 `2.375e−15`, n8 substep2↔4 차이 `4.367e−15`도 사전 한계보다 작다. 그러므로 **`REFERENCE_RESOLVED_AT_PRIOR_4_TO_8_SCALE`**이다. 단, 이번 새 4→8 신호 자체의 1%는 `4.011e−15`로 16→32 차이 `4.457e−15`보다 조금 작다. 새로 얻은 더 좁은 scale까지 해결했다고 주장하지 않는다. production 독립 ODE/continuum 기준해도 없으므로 더 강한 전역 오차나 observable 정확도를 주장하지 않는다.

이번 후보의 n16과 tighter n16은 같은 사전 오차 한계 안에서 각각 97.998초와 118.937초였다. 이 wall은 개별 전파 측정이며 host transfer 약 0.115초는 별도다. 직전 R3M21의 오차 조건이 달라 두 job 간 speedup으로 나누지 않는다. Strang과도 같은 상태오차에서 비교 가능한 생산 격자 쌍이 아직 없다. 따라서 정확도 맞춤 방식 간 speedup과 전체 collision wall은 `NOT_MEASURED`다.

R3M19 refined h=.20 CF4 oracle FAIL, R3M21 첫 1% FAIL을 그대로 보존한다. 이번 결과는 incoming 한 짧은 창의 시간 기준을 **직전 신호의 1% scale에서만** 경험적으로 해상했고, tiny 최소-error gate는 CPU-only 후속 closeout에서 통과했다. 전체 `TIME_REFINEMENT_STILL_OPEN`, production `HOLD`, b-grid `NO_GO`는 유지한다. 공간/CAP/preparation/all-bound/b 적분/physical-rate gate는 열려 있다. R3M20에서 선택만 고정한 closest/outgoing B2 창은 이번 계약상 실행하지 않았다. 다음 canonical node는 정확히 하나: `N1_TDL_PRODUCTION_H_B2_CLOSEST_OUTGOING_SHORT_WINDOW_WORK_PRECISION`. 그 node는 새 자원 계약에서 두 남은 보존 checkpoint의 identity/독립 inner gate를 먼저 확인하고, 각각 최대 4 B2 dt만 비교해야 한다.
