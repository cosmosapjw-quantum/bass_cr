# R3M20 N1: production h 짧은 GPU 기준해와 work–precision

## 범위와 입력

입력 원격 branch `cr/r3m19-fullh-diagnostics-20260923`는 fetch 후 exact HEAD `83dc465443f8b4fdf7c720304118207cc5267dfc`로 확인했고, 별도 branch `cr/r3m19-n1-gpu-short-window-20260923`에서 실행했다. R3M18 과학 기준은 `3d033eb08a0efd99257470f0fa27214f569b427a`, numerical source digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`이다. 같은 h/box/CAP/energy/b와 보존된 B2 상태만 사용했다. 새 full collision, preparation, finer h, representation 변경, projection 및 checkpoint write는 모두 0회다.

B2의 작은 원본 13개, 16,672 bytes를 `results/R3M20_N1/intake/`에 원문 그대로 보관하고 양쪽 SHA를 검증했다. 원본 `result.json`은 6,029 bytes, SHA-256 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`로 계약과 일치했다. 유일하게 실행한 incoming `g000384` checkpoint는 기존 guard로 seal/config/frontier/state SHA를 검증했다. 이 검증은 local checkpoint 검증이며 원격 restore 검증은 아니다. 나머지 두 checkpoint는 선택만 고정하고 읽거나 전파하지 않았다.

## 장비와 구현 동등성

실측 장비는 Ryzen 9 5900X(affinity 안 물리 12코어), RAM 총 101,140,516,864 bytes, RTX 3090(25,290,604,544 bytes)이다. 첫 inventory의 RAM available은 84,539,527,168 bytes, GPU free는 24,895,881,216 bytes였다. Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0을 사용했다. 기존 설치 `threadpoolctl`과 CUDA 12 cuFFT/cuBLAS 라이브러리 경로만 노출했으며 과학 패키지를 업그레이드하지 않았다. 첫 모듈/라이브러리 실패 원문과 재시도는 `results/R3M20_N1/performance/`에 보존했다.

동일한 4-step/5-repeat microtrajectory의 기준/후보 median wall 비율과 상태 상대 L2는 다음과 같다. 비율 1보다 크면 해당 측정에서 후보가 빨랐다는 뜻이다. setup, reset, 검산, projector, checkpoint 시간은 이 비교 밖이다.

| 장치와 shape | 후보 | 기준/후보 wall | 상대 L2 |
|---|---|---:|---:|
| GPU 64×64×96 | buffer reuse | 1.02495 | 7.81e−16 |
| GPU 128×128×64 | buffer reuse | 0.99965 | 7.85e−16 |
| CPU 64×64×96 | native buffer | 1.09037 | 6.44e−16 |
| CPU 64×64×96 | SciPy FFT, 1 worker | 1.56182 | 6.44e−16 |
| CPU 64×64×96 | SciPy FFT, 4 workers | 2.09368 | 6.44e−16 |

등록된 state≤5e−13, norm≤2e−13 동등성 기준은 모두 통과했다. 실제 GPU 시험은 20 passed, 0 skipped였다. 이는 두 작은 GPU shape와 한 CPU shape의 결과다. production 63M점과 전체 collision의 속도 개선은 이 microbenchmark에서 측정하지 않았다.

## full-H action과 독립 작은 기준해

새 opt-in `scripts/r3m20_matrix_free.py`는 원래 FFT 주기 경계의 `A(t)ψ=−i[T_hψ+(V_T+V_P(t))ψ]−Wψ`를 matrix-free로 계산한다. CAP `W=−log(mask)/dt_ref`를 포함한 비Hermitian Arnoldi에 두 번의 재직교화를 쓰며, CF4의 각 exponential은 전체 generator action이다. Arnoldi residual은 경험적 inner indicator일 뿐 global state/observable certificate가 아니다. 원래 `cr_repro/` numerical core는 변경하지 않았다.

64점 CAP off/on과 속도 부호 ±, 96점 직사각형 CAP on의 네 사례에서 독립 DOP853의 `max_step` repeat와 inner-tolerance repeat를 실행했다. 최종 `MATRIX_FREE_TINY_v3.json`의 네 사례 모두 두 repeat 차이가 최소 비교 CF4 오차의 1% 미만이었다. 고정 horizon에서 timestep refinement도 별도로 수행했다. 초기 tiny receipt의 1% 미해결은 남겨 두었고 inner tolerance를 강화한 새 receipt로 해결했다. R3M19 refined h=.20 CF4 oracle FAIL은 바꾸지 않았다. 작은 격자의 검증은 continuum이나 production-grid 전역 오차 인증이 아니다.

## 선택과 production 격자 1구간

계산 전 `SELECTION.json`에 incoming `g000384`(z=−20.3625), closest `g001152`(z=−1.08756), outgoing `g002048`(z=21.3999)를 실제 z와 state/manifest SHA로 고정했다. 각 구간의 최대 horizon은 B2 dt `0.01249892352238994`의 4배다. 할당 probe는 production 63M complex128 배열과 basis/temporary를 실제 할당했고, FFT matvec 후 GPU free 2,689,138,688 bytes, host reserve≥8 GiB를 확인했다. 최초 창 비용은 median matvec 0.101826초에서 325.84초로 **예측**했으며, 실측이라고 취급하지 않는다.

허용된 GPU 전파 job **1개**에서 incoming 창만 계산했다. 창 wall 430.0339초, preflight 포함 전체 FFT matvec 1,893회로 30분/2시간/4,000회 상한 안이다. 같은 상태의 frozen Strang과 buffer 후보는 1-step 상대 L2 `2.72e−16`, 4-step `1.06e−15`로 동등했다. 참조로 둔 CF4 dt/2 endpoint에 대한 raw 상태거리는 다음과 같다.

| 방법 | propagation wall, 초 | FFT matvec | CF4 dt/2까지 raw 거리 |
|---|---:|---:|---:|
| frozen Strang dt, 4 steps | 0.3967 | 별도 FFT 계수 미기록 | 2.767862e−4 |
| Strang dt/2, 8 steps | 0.7954 | 별도 FFT 계수 미기록 | 6.853402e−5 |
| Strang dt/4, 16 steps | 1.5667 | 별도 FFT 계수 미기록 | 1.709404e−5 |
| full-H midpoint, 4 steps | 52.9102 | 224 | 3.597126e−10 |
| full-H average, 4 steps | 53.4450 | 224 | 1.837849e−10 |
| full-H CF4, 4 steps | 85.1884 | 384 | 2.103971e−12 |
| full-H CF4, 8 steps | 131.7961 | 640 | 기준값 자체 |

CF4 4-step inner tolerance `1e−12→1e−13` repeat는 같은 endpoint와 basis를 주었다. 이것만으로 true error가 0이라고 주장하지 않는다. CF4 dt→dt/2 차이는 `2.103971e−12`이며, production grid에서 독립 ODE 또는 dt/4가 없어 dt/2 자체가 해결된 oracle인지는 **미확인**이다. raw vector Gram 분해의 squared closure residual은 `3.97e−23`; 이는 항등식/계산 내부 검산이며 참조 정확도 증명이 아니다. setup/upload 약 0.714초와 endpoint별 host transfer 약 0.13~0.15초를 propagation wall과 분리 기록했다. 관측 GPU free 최저 약 4.97 GiB였다.

서로 같은 상태오차에 도달한 두 방법의 wall 표본이 없으므로 **정확도 맞춤 speedup은 산출하지 않는다**. 위 표는 조건부 기준점에 대한 work–error 위치만 나타낸다. 특히 Strang의 빠른 wall을 CF4의 더 작은 오차와 같은 성능점으로 비교할 수 없다. 전체 B2 collision timing도 없고 full collision 속도는 미실측이다. closest/outgoing 창은 전파하지 않았다.

## 시험, 검토, 판정

직접 GPU를 포함한 대상 테스트는 통과했다. 저장소 루트의 `pytest -q`는 과거 보관 테스트를 중복 수집하여 exit 2였고 원문을 보존했다. `pytest tests`의 첫 경로 설정은 subprocess import 1건에서 실패했고 이 원문도 보존했다. 올바른 Python 지원 경로에서 `python -B -m pytest -q -p no:cacheprovider tests`는 **354 passed, 0 failed, 0 skipped**였다. 이 결과를 무조건적인 저장소 루트 명령 성공으로 바꾸어 말하지 않는다. 독립 검토는 source와 receipt를 읽는 정적 검토였으며 production 계산 재실행은 아니었다. 검토 시점의 untracked source 결함은 전용 branch commit과 원격 exact HEAD 확인으로 해소한다.

과학 판정은 여전히 `TIME_REFINEMENT_STILL_OPEN`, production admission `HOLD`, b-grid `NO_GO`다. 시간 gate는 production CF4 외부 기준의 독립 resolution이 없어 열려 있다. 공간, CAP, preparation, all-bound, b 적분 및 physical rate gate도 이 창으로 닫지 않는다. 다음 canonical node는 정확히 하나: `N1_TDL_PRODUCTION_H_CF4_OUTER_REFERENCE_RESOLUTION_AT_INCOMING_CHECKPOINT`. 별도 미래 계약에서 같은 incoming checkpoint의 CF4 dt/4 또는 독립 기준을 자원상한과 함께 설계·검증해야 한다. 이번 node의 사용한 GPU 전파 job을 확장하거나 새 collision을 승인하는 뜻은 아니다.
