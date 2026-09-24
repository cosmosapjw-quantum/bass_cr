# R3M25 실제 t=0 국소 기준해 결과

## 판정과 범위

보존된 B2 `closest/g001152`에서 42개 B2 Strang step을 진행한 파생 상태로 시작해, 실제 t=0을 가로지르는 4-step 창 `[-0.016665231363186095, 0.033330462726373966]` au를 비교했다. 두 번째 fresh 시도에서 **국소 CF4 4차 호환성, 사전 고정한 self-scaled 기준, Strang 비교 척도가 PASS**였다. 이것은 `FOUR_B2_STEP_PHYSICAL_T0_LOCAL_ONLY` 결과다. 파생 warmup 상태는 historical checkpoint가 아니다.

**Production GO는 아니다.** `GLOBAL_TIME_ERROR=NOT_EVALUATED`, `production_admission=HOLD`, `b-grid=NO_GO`다. R3M18 B1→B2 P1/P2/P3 변화 0.2786926%/0.2591311%/0.2565637%는 0.10% pair screen을 초과했다. h=.25/.20의 P3 차이 약 2.9527586%, h-dt interaction 약 1.0445%도 미해결이다. 이 국소 결과는 B3 full collision, spatial convergence, preparation, CAP/box/final-time, all-bound completeness, target-Q reference를 대신하지 않는다.

## 입력·실행·검증

- 구현 commit: `4836e680c13e6abdfde1be44921b6d836c3aea11`.
- 원본 B2 state SHA-256: `539afab21049668e2c165e1700c907d760159cf0fbc6321f9b28032ce428f3c1`; generation manifest SHA-256: `2f7cd54c0801526ba5816f38058e70128140930d555a09e554d38137aeb68d01`.
- 두 번째 contract SHA-256: `64b3dba878c6bab2dfbf82cdedd78da6eedd2daacd854c5b66f3567d65ffb4d2`; 별도 fresh 경로 `results/R3M25/ATTEMPT_2`.
- warmup 42 matvec, 파생 endpoint SHA-256 `eb4353aa4f4f599831ef670f0fb63b4425789a6e526d0734b46b0da03d94037c`.
- 실제 총 2,523 kinetic matvec, 5,046 FFT transform, wall 585.053 s. 이 중 event 2,478 matvec, 578.883 s. 상한은 4,000 matvec, 전체 7,200 s, event 3,600 s이고 whole-process 3,600 s watchdog을 적용했다. 측정된 최소 GPU free 3,158,835,200 bytes, host available 70,871,818,240 bytes로 각각 2 GiB/8 GiB reserve를 지켰다.
- GPU는 RTX 3090, CuPy 14.2.0, CUDA runtime 12090, driver API 13020, complex128이었다. preflight 3 matvec과 Strang 1-step/4-step parity가 통과했다.
- 원본 GPU 첫 시도는 preflight 1 matvec 뒤 GPU free 1,143,472,128 bytes로 reserve를 잃어 중단했다. `ATTEMPT/FIRST_FAILURE.json`과 원본 contract는 수정하지 않았다. 이는 자원 실패이며 수치 비수렴이 아니다. 독립 source review가 발견한 6개 host transfer reserve gap은 후속 guarded helper와 CPU regression으로 수정한 뒤에만 두 번째 시도를 실행했다. 자동 retry는 0회다.

## 국소 수치 결과

동일 파생 입력과 물리 창의 raw-L2 distance는 `d4,8=1.528013292750591e-7`, `d8,16=8.302194020466426e-9`, `d16,32=5.026593394148416e-10`이었다. 관측 차수는 4.20202063593422, 4.045839749892995로 사전 등록 구간 `[3,5]` 안에 있다. 독립 action-substep 2→4 반복 차이는 `1.6629014671327192e-15`; 실제 work fingerprint가 달랐다. n16 tighter-inner는 같은 stopping work여서 `SKIPPED_UNCHANGED_WORK`이며 독립 반복으로 세지 않았다.

Self-scaled 1% 한계는 `1.528013292750591e-9`; `d16,32`와 독립 반복 차이가 그 아래다. order 신호 하한 `1.6629014671327193e-13`보다 세 ladder distance가 모두 크다. Strang-to-CF4 비교 척도는 `1.840747102771996e-5`; 이것은 self-scaled 분모로 대체하지 않았다. inner calibration의 독립 substep 차이는 `4.736954712682333e-16 < 2.103970853068276e-14`였다. Exact-arithmetic inner bounds는 부동소수점 roundoff certificate가 아니다.

## 회귀 및 무결성

최종 수정 후 R3M25 전용 시험 14 PASS, 전체 `tests` 436 PASS, compileall/CLI PASS, CUDA import/runtime PASS였다. `HOST_VALIDATION_2.json`에서 exit/contract/result/manifest seal, 입력·warmup binding, geometry, 작업량, reserve, 실제 독립성, 국소 수학 gate와 production hold 등 25개 독립 read-only check가 모두 PASS다. `ATTEMPT_2/RESULT.json`, `MANIFEST.json`, `COMPLETED.json`의 create-only 봉인을 확인했고 실패 영수증은 없다. 원본 첫 실패 영수증은 별도로 남아 있다.

## 다음 canonical node

`N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT` 하나다. B3는 이번 작업에서 실행하지 않았다. 같은 h/box/CAP/target/projector/preparation bytes에서 B2 actual dt의 절반과 7,172 step을 쓰는 새 계약을 먼저 고정해야 한다. B2→B3 channel pair, 4-point temporal model, leave-one-out 일치성 및 독립 reference/defect evidence를 함께 평가한다. 예측 P1/P2/P3 `0.0060884835814/0.0075857897381/0.0080882888941`은 acceptance target이 아니다.
