# R3M19 제한된 성능 실험

이 결과는 현재 웹 실행환경의 Xeon Platinum 8272CL에서 얻었다. 사용자 workstation의
CPU·RAM은 아직 재확인하지 않았고 GPU 실행은 없었다. 최신 production receipt의 RTX3090
24GB와 예전 프로필의 Ryzen5900X/64GB를 같은 시점에 검증한 inventory로 합치지 않는다.

고정 `cr_repro` source는 변경하지 않았다. `BufferedSplitStep`은 동일한 `Vmid`,
`cap_half`, `kin`, complex128, midpoint와 actual dt를 사용하며 phase/work 배열 재사용과
kinetic 곱의 in-place 연산을 별도 sidecar로 구현한다. CPU 대안은 SciPy FFT의 명시적
`workers`를 사용한다. BLAS는 1 thread로 제한하지만 이 제한이 NumPy FFT를 병렬화하거나
제어한다고 주장하지 않는다. GPU 대안은 CuPy FFT를 그대로 사용한다. 새 fused kernel,
fast-math, float32, soft-core, renormalization은 없다.

64×64×96, 4 steps, 각 구현 warmup 2회 및 timed repeat 5회의 결과:

| 후보 | CPU FFT workers | 기준 중앙 시간(s) | 후보 중앙 시간(s) | 측정 비율 | 상대 state L2 차이 |
|---|---:|---:|---:|---:|---:|
| native FFT + buffer reuse | 해당 없음 | .472662 | .300503 | 1.57290 | 6.28e-16 |
| SciPy FFT + buffer reuse | 1 | .417315 | .212173 | 1.96686 | 1.03e-15 |
| SciPy FFT + buffer reuse | 4 | .430099 | .143159 | 3.00434 | 1.03e-15 |

이는 각 후보와 같은 실행에서 측정한 reference의 중앙값 비율이다. 서로 다른 실험의
기준 시간도 달랐다. 원 샘플·범위·환경·script hash는 각 `RESULT.json`과 `SUMMARY.json`에
남겼다. 본 결과의 오차는 frozen split-step 구현과의 차이이며 정확한 물리해에 대한 오차가
아니다. P1/P2/P3는 이 microbenchmark에서 계산하지 않았다. 따라서 전체 6,300만 점
collision이나 사용자 GPU의 속도·정확도를 의미하지 않는다.

준비·초기상태 copy/reset·배열 preallocation·결과 검산·host/device copy·projector·checkpoint
hash/write·backup은 step timing에서 제외한다. GPU는 warmup 뒤 CUDA events 및 end
synchronization으로 device 시간과 host enqueue/wall 시간을 구분한다. memory monitoring은
timed trajectory 전후에만 수행한다. 실제 GPU 검증은 미실행이다. fake CUDA event 시험은
계측 위치만 검증하며 GPU 성능 증거가 아니다.

R3M18에서 preparation 423.14156초와 29개 generation의 29.232GB state 보존은 확인된다.
충돌 전파/FFT/projector/checkpoint별 시간은 repo summary에 없어 실제 production 병목은
UNMEASURED다. 기존 chunk·receipt·generation·backup 정책을 속도 목적으로 바꾸지 않았다.

로컬 실행 프로토콜:

1. 기존 scientific interpreter로 `python -m scripts.r3m19_performance inventory --backend cupy`
   실행 후 실제 CPU affinity/physical topology/cgroup quota, available RAM, GPU 모델/free VRAM,
   Python/NumPy/CuPy/CUDA, FFT cache/pool을 기록한다. 환경 업그레이드는 하지 않는다.
2. CPU 후보는 동일 64×64×96 shape에서 native buffer 후보와 SciPy workers 1, 4를 순차
   측정한다. 4 workers는 실제 inventory cap이 허용할 때만 사용한다. 더 많은 workers를
   무조건 선택하지 않는다. BLAS=1은 scoped control이며 종료 후 복원된다.
3. GPU는 단독 프로세스로 아래 두 shape를 순차 측정한다. 각 run은 고유 output 디렉터리,
   stdout/stderr를 보존한다. 다른 대형 GPU job과 겹치지 않는다.

```bash
python -m scripts.r3m19_performance benchmark --backend cupy --candidate buffer_reuse \
  --shape 64,64,96 --steps 4 --repeats 5 --max-working-mib 512 --max-seconds 30 \
  --out /ABSOLUTE_NEW_PATH/gpu_medium
python -m scripts.r3m19_performance benchmark --backend cupy --candidate buffer_reuse \
  --shape 128,128,64 --steps 4 --repeats 5 --max-working-mib 512 --max-seconds 30 \
  --out /ABSOLUTE_NEW_PATH/gpu_larger_bounded
```

각 run은 2^20 points·8 steps·10 repeats·1GiB working budget·60초의 hard ceiling 아래여야
한다. 실제 요청은 이보다 작다. 명시적 working-memory model과 available RAM/VRAM 검사는
array allocation보다 먼저 수행한다. CuPy pool/cache 한도는 sidecar에만 적용하고 복원한다.
이 한도는 CUDA context/library를 포함한 실제 전체 peak VRAM의 증명이 아니다. OOM·timeout·
parity failure는 증거를 보존하고 CPU fallback이나 자동 재시도를 하지 않는다.

현재 acceptance는 미세 실험 범위의 구현 동등성이다. GPU speedup이나 더 큰 workload에
대한 승격은 해당 하드웨어 측정과 정확도 일치가 확인된 뒤 별도 scope에서 결정한다.
고정 production propagator를 이 후보로 자동 교체하지 않는다.
