# R3M26 성능·메모리·실행 순서 검토

2026-09-24 UTC. 결론은 **현재 환경과 scientific path를 고정한 B3 한 회의 시간 수렴 검증을 우선한다**는 것이다. R3M20 실측에서 GPU 버퍼 재사용은 약1배였고 작은 CPU FFT의 최선은 2.09배였다. 과거 웹 조사에서 제시한 약3배 기대치를 실제 GPU 가속 실적으로 사용하지 않는다. 63M production 격자의 전체 가속은 측정되지 않았다.

성능 목표는 승인된 관측량 오차에 도달하는 총 시간(time-to-accuracy)이다. GPU 사용률을 100%에 가깝게 만드는 것, FFT 하나의 최고 처리량, norm 보존만으로 실행 방법을 선택하지 않는다. 이 검토에서는 새 GPU 작업이나 전파 코드를 실행·변경하지 않았다.

## 실제 하드웨어와 고정 환경

자료는 [R3M20 inventory](../../results/R3M20_N1/performance/hardware.json), [R3M25 attempt2 preflight](../../results/R3M25/ATTEMPT_2/PREFLIGHT.json), [CONTRACT_2](../../results/R3M25/CONTRACT_2.json)다. 현재 장비를 새로 probe한 값으로 표시하지 않는다.

| 항목 | 기록된 값 | 실행에 적용할 의미 |
|---|---|---|
| CPU | Ryzen 9 5900X, 물리12 cores, affinity logical24 | 24개의 과학 작업 동시 실행 근거가 아님. quota 값은 null이므로 무제한 quota로 해석하지 않음 |
| RAM | 101,140,516,864 bytes = 94.1944 GiB | 약96 GiB급 장비이며 64 GiB가 아님 |
| R3M25 시작 시 available RAM | 80,505,634,816 bytes = 74.9767 GiB | 총 RAM과 작업이 당장 사용할 수 있는 RAM을 구분 |
| GPU | RTX3090, device0, 25,290,604,544 bytes = 23.5537 GiB | 24 GB급 단일 GPU. 시작 시 free24,864,358,400 bytes |
| CUDA | runtime12090, driver API13020 | 각각12.9/13.2로 기록. CUDA toolkit·driver package 전체 버전과 혼동하지 않음 |
| 과학 환경 | Python3.12.3, NumPy2.5.3, SciPy1.18.1, cupy-cuda12x14.2.0 | 동일 interpreter·환경·공유 라이브러리 경로를 유지 |
| FFT cache/pool 초기값 | plan0, cache0 bytes, 최대16plans, cache byte limit−1; pool limit0 | 측정 시 캐시가 비어 있었음. 무제한 메모리 가용성을 뜻하지 않음 |

B2의 `350×300×600`은63,000,000 points다. `complex128` 상태 하나의 payload는1,008,000,000 bytes(0.9388 GiB)다. host와 GPU의 복제 수, FFT workspace, CAP/potential 배열, pool 잔류분을 함께 계상해야 한다.

고정 scientific source digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`다. `threadpoolctl3.6.0`의 기존 Python module 재사용과 기존 `libcufft.so.11` 검색 경로 보완은 이미 기록된 지원 조치이며 과학 라이브러리 upgrade가 아니다. B3 직전에 NumPy/SciPy/CuPy/CUDA, reduction backend, FFT backend, dtype, fast-math 설정을 바꾸지 않는다. 환경의 재현 여부를 확인할 수 없으면 멈추고 차이를 기록한다.

## 실제 microbenchmark

[SUMMARY.json](../../results/R3M20_N1/performance/SUMMARY.json)은 동일 microtrajectory의4steps×5repeats다. setup/reset/validation/projector/checkpoint를 제외한다. 아래 비율은 reference wall/candidate wall의 중앙값이다.

| 장치·후보 | shape | reference ms | candidate ms | 속도비 |
|---|---|---:|---:|---:|
| GPU buffer reuse | 64×64×96 | 2.29409 | 2.23825 | 1.02495 |
| GPU buffer reuse | 128×128×64 | 5.46535 | 5.46727 | 0.99965 |
| CPU native buffer reuse, workers1 | 64×64×96 | 102.22290 | 93.75101 | 1.09037 |
| CPU SciPy FFT, workers1 | 64×64×96 | 101.70988 | 65.12250 | 1.56182 |
| CPU SciPy FFT, workers4 | 64×64×96 | 99.72195 | 47.63006 | 2.09368 |

GPU device-event 비율도 각각1.02522/0.99965다. 같은 discrete-state parity의 상대L2는GPU 약7.8e−16, CPU 약6.4e−16이며 기록된 실제 GPU 시험은20passed/0skipped다. 이는 microbenchmark의 검증 기록이며 이번 문서에서 재실행한 시험이 아니다. 특히 CPU2.09배를 GPU와의 속도비, 63M 전체 경로 가속, 물리적 정확도 개선으로 해석하지 않는다. `production_63M_speed=NOT_MEASURED`를 유지한다.

## R3M25 residency 수리의 의미

[실행 코드](../../scripts/r3m25_event_window.py), [residency closeout](../../results/R3M25/RESIDENCY_REVIEW_CLOSEOUT.json), [R3M25 보고서](../r3m25/REPORT_KO.md)를 대조했다. closeout의 중간 `NOT_YET_RUN`과 이후 attempt2 성공을 시간 순서로 구분한다.

최초 시도는1kinetic matvec 뒤 GPU free1,143,472,128 bytes가2GiB reserve 아래로 내려가 중단됐다. 수치 판정 실패와 별도의 자원 실패다. 독립 full-H/CAP 표현을 만든 후 더 이상 쓰지 않는 split runner의 `kin`, `mask`, `cap_half`를 해제해 payload2,016,000,000 bytes(1.8775GiB)를 회수했다. 사용 중인 Hamiltonian을 단순화한 것이 아니다. pool 반환은 이 생명주기 경계에서 수행하며 매 time step마다 수행하지 않는다.

수리 후에는 probe runner를 폐기한 다음 fresh runner에서 고정 checkpoint를 다시 읽고42step warmup을 한다. warmup 결과는 파생 상태이며 역사적 checkpoint로 부르지 않는다. Strang parity에 필요한6개 host transfer 모두 전후 reserve를 검사한다. host 전송 직전에는 상태 payload를 추가로 고려한다. CF4 endpoint 전송도 동기화·전후 검사 후 hash를 만든다. `cp.asnumpy`의 기존 동기 전송을 사용한다.

최종 attempt2는 physical t=0을 지나는4B2step 국소 구간에서 총2523kinetic matvecs/5046FFTs, wall585.053s를 기록했다. sampled minimum free는GPU3,158,835,200 bytes(2.9419GiB), host70,871,818,240 bytes(66.0045GiB)였다. 연속 시간의 완전한 peak-memory 인증은 아니다. 이 국소 CF4 검사를 full trajectory의 비용·시간오차 인증으로 외삽하지 않는다. 당시 whole-process watchdog3600s, kill grace10s, matvec cap4000과 basis cap10은 **해당 국소 계약**이다. B3의 별도 전체 충돌 시간 계약으로 자동 복사하지 않는다.

## CPU·RAM·GPU 작업 순서

다음은 기존 실행 경로를 보존하는 후속 일정이다. 실제 B3 실행 승인·결과를 뜻하지 않는다.

| 단계 | CPU 및 host RAM | GPU 및 동시 작업 | 완료/중단 기준 |
|---|---|---|---|
| 1. 계약·환경·입력 확인 | 단일 coordinator, JSON/hash의 bounded 읽기. 작은 검사에만 명시한 thread 수 사용 | 전파0개. 장비·환경·state/manifest/source identity 확인 | 시작 전 실제 free값을 다시 확인. 다른 과학 작업을 종료한 단일 GPU 확보 |
| 2. 필요한 resource preflight | host reserve8GiB; 예상 host 복사 bytes를 사전에 차감. 큰 상태의 불필요한 복제 금지 | GPU reserve2GiB; workspace/cache/pool과 살아 있는 배열을 함께 계상 | pre/post-transfer 검사. OOM·reserve 미달이면 기록하고 정지, 63M CPU fallback 없음 |
| 3. B3 한 회 | 기존 synchronous checkpoint/관측량 경로 유지. 별도 대규모 CPU FFT·압축·원격 전송 병행0개 | GPU propagation1개. B2와 같은 h/box/CAP/preparation/projector, actual dt의 절반,7172steps | 새로운 계약에 입력·runtime·wall/memory cap을 고정. frozen Strang 경로를 변경하지 않음 |
| 4. 진단·축소·배송 | 전파 종료 후 순차 hash·작은 결과 분석·archive 전송. 검증된 streaming 방식으로 RAM 제한 | 전파0개, 다른 충돌 시작0개 | B3 held-out 판정과 budget 계산 후 다음 연구 단계 결정 |
| 5. 독립 CPU/성능 실험 | 별도 시점의 작은 shape에서 workers1/4 비교. BLAS thread1을 명시하는 새 실험 계약으로 중첩 병렬 방지 | production 전파와 겹치지 않음 | 과거 실행의 thread 설정이1이었다고 소급 주장하지 않음. 모든 logical core 사용을 기본값으로 삼지 않음 |

단계3 전에 float32/complex64, Coulomb smoothing 변경, h 변경, FFT representation 교체, CAP·projector 수정, CF4 전면 대체를 넣지 않는다. 현재 frozen Strang의 B3 refinement가 선택한 이산 Hamiltonian에서 시간 오차를 판별하도록 한다. 이후 개선은 별도 parity/오차/자원 계약으로 비교할 수 있다. GPU가 사용할 수 없으면 자원 제약으로 중단하며 `backend=numpy`로63M 궤적을 몰래 재실행하지 않는다.

## 정확히 맞는 API 조사와 적용 한계

- [CuPy14.2.0 memory](https://docs.cupy.dev/en/v14.2.0/user_guide/memory.html): device/pinned pool은 재할당 비용을 줄이며 미사용 block을 보유할 수 있다. pool limit은 context·일부 library 할당까지 모두 제한하지 않는다. 따라서 pool used만으로 여유를 판단하지 않고 device free, reserved, FFT workspace, host available을 같이 기록한다. `free_all_blocks()`는 살아 있는 배열을 해제하지 않는다.
- [CuPy14.2.0 FFT](https://docs.cupy.dev/en/v14.2.0/user_guide/fft.html): plan cache는 device/thread별이며 plan workspace가 추가 메모리를 차지한다. 고정 shape/axes/dtype로 cache를 재사용하되 cache hit, plan 수·bytes, 실제 peak를 기록한다. 별도 `get_fft_plan`은 experimental이며 B3에 새로 도입하지 않는다. plan cache를 무조건 지우거나 키우는 것을 가속으로 가정하지 않는다.
- [CuPy14.2.0 benchmark](https://docs.cupy.dev/en/v14.2.0/user_guide/performance.html): `cupyx.profiler.benchmark`는 warmup과 CUDA event/end-event synchronization을 사용한다. CPU enqueue 시간만으로 GPU 완료 시간을 측정하지 않는다. kernel timing과 초기화·JIT·전송·checkpoint를 포함한 전체 wall을 분리해서 모두 보고한다.
- [CuPy14.2.0 asnumpy](https://docs.cupy.dev/en/v14.2.0/reference/generated/cupy.asnumpy.html): `blocking=True`가 기본이다. `blocking=False`에서는 호출자가 stream 순서를 책임진다. 단순히 옵션만 바꾸면 host hash/writer가 완료 전 buffer를 읽을 수 있다.
- [SciPy1.18.1 FFT source](https://raw.githubusercontent.com/scipy/scipy/v1.18.1/scipy/fft/_basic.py): `workers`는 병렬 worker 상한이며 음수는 CPU 수에 상대적으로 해석된다. CPU workers4의 실측은 작은 shape에서만 확인됐다. `plan` 인자는 해당 SciPy 구현에서 예약 인자이므로 cuFFT plan을 여기로 전달하는 최적화를 제안하지 않는다.
- [SciPy1.18.1 expm_multiply source](https://raw.githubusercontent.com/scipy/scipy/v1.18.1/scipy/sparse/linalg/_expm_multiply.py): 전체 exp(A)를 만들지 않고 action을 계산한다. `LinearOperator`에서 `traceA`를 생략하면 추정이 필요하며 source는 trace 제공을 권한다. 고정A action이 정확하더라도 moving H의 시간 적분 차수는 별도다. public API에 임의 tolerance를 있다고 가정하지 않으며 작은 독립 action 검산에 사용한다. matrix-free여도 full-size 작업 벡터와 반복 matvec 비용이 남으므로63M CPU fallback의 근거가 아니다.

SciPy 문서의1.18.1 version URL은 열람되지 않아 공식 저장소의 **v1.18.1 tag source**를 읽었다. 다른 버전 문서를 현재 설치 API의 증거로 대체하지 않았다.

## 아직 구현하지 않은 최적화와 승인 척도

비동기 checkpoint는 미래 설계 후보이며 이번 구현·검증·B3에 포함하지 않는다. 도입하려면 pinned host buffer 소유권, GPU event 완료 후 hash/write, 제한된 queue와 backpressure, double buffer의 추가 RAM, 임시 파일의 durable write 및 hash/manifest 일치, crash injection과 restore, 기존 scientific output의 byte/수치 동등성을 검증해야 한다. 이 조건을 충족하지 않은 `blocking=False` 전환을 속도 개선으로 승인하지 않는다.

후속 최적화 비교는 같은 input/config/source와 관측량 오차 목표에서 setup→propagation→projection→checkpoint→검증까지의 wall, 준비비용, FFT/matvec 수, 최고 RAM/GPU 사용량, 성공/중단/재시도 비용을 함께 낸다. cold/warm 결과와 반복 분산을 구분하고 P1/P2/P3, state/projector 및 cross-effect 검사로 정확도를 묶는다. 사용률은 병목 진단 자료다. 오차 배분을 만족하는 결과를 가장 적은 총 자원으로 얻는 방법을 채택한다.

현재 판정: scoped 성능·residency 증거는 재사용 가능하다. 전역 시간 오차와 다른 numerical budget은 여전히 열려 있으므로 production은 HOLD다. 다음 canonical node는 `N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT`다.
