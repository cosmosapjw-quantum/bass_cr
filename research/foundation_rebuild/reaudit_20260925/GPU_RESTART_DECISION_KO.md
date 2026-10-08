# GPU 재실행 판정

**현재 판정: 원래 A3/B3 GPU full run을 처음부터 다시 실행하지 않는다.** 이번 CPU FND 정적 행렬 적분 실패와 원래 GPU wavefunction trajectory는 서로 다른 numerical path다. 현재 감사에서 원래 `cr_repro` source digest는 변하지 않았으며, 신규 수정은 별도 `repair/`에 있다.

## 이미 존재하는 근거

원래 B3 coordinator는 `ControlledTDLRunner` 경로를 사용한다. 이 클래스는 absorber mask를 actual dt/reference dt에 맞춰 rate-fixed하게 만들고 potential/CAP 반 단계, kinetic, 반 단계로 전파한다. authoritative observable은 Gram-corrected finite selected span이다. 기본 `TDLRunner`의 historical raw overlap sum 또는 per-step CAP를 곧바로 실제 B3 경로라고 진단하면 오탐이다.

`source/results/R3M27/validation/FULL_CUDA_PATH.stdout`와 `FULL_FINAL_SOURCE.stdout`에 각각 484 passed 기록이 있다. 첫 실패는 libcufft 동적 라이브러리 경로 문제였고 실패 로그가 보존되어 있다. 이 증거는 과거 run의 환경에 대한 것이며 현재 사용 중인 GPU가 건강하다는 새 검사가 아니다. 이후 CPU-only validation에서 GPU test 3개가 skip된 사실과 모순되지 않는다.

B3의 원래 result, config, source digest, endpoint hash/witness 자료는 보존되지만 대형 state.npy bytes는 이번 source export에 없다. 원래 GPU endpoint를 이번에 독립 전파로 재계산하거나 복원했다고 주장하지 않는다.

## 재실행 범위를 정하는 표

| 실제 변경/질문 | 필요한 최소 조치 | full collision |
|---|---|---|
| FND TP/PT quadrature만 변경 | 새 CPU kernel의 지정 수치 시험과 full-matrix 통합 | 불필요 |
| 현 GPU/드라이버 환경이 바뀌었거나 실행 직전 health 확인 | 소형 CUDA library/FFT/operator parity 시험, 실제 backend 기록 | 아직 불필요 |
| 기존 endpoint의 projector/분석만 변경 | 해당 endpoint bytes를 복원·동일성 확인 후 post-processing | 보통 불필요 |
| 실제 전파 H, grid, CAP, initial state 변경 | 새 source/config/run identity의 forward trajectory | 해당 새 실험에 필요 |
| source/config/witness 무결성 불일치 | 복구·정확한 영향 범위 조사 | 불일치 영향이 해소되지 않을 때만 |
| 원래 state payload가 소실되어 꼭 필요한 분석을 할 수 없음 | 백업 payload 복원을 우선 시도 | 복구 불가능한 필요한 run만 |
| 새 FND collision 비교를 시작 | 작은 고정 basis/geometry/horizon의 finite-span run | 원래 대형 B3 재실행부터 시작하지 않음 |

## 현재 주장 한계

고정 h=.20 시간 추정은 기존 scoped noncertified evidence로 유지한다. 그 시간 PASS를 새 Hamiltonian·초기상태·FEM basis로 복사하지 않는다. A3/B3의 3%대 공간 pair mismatch와 total production budget은 여전히 열려 있다. 이번 수정의 성공은 별개인 static cross-block convergence다.

`backend.py`의 explicit cupy 요청에서 import는 성공하지만 device count가 0일 때 numpy fallback이 가능한 정적 edge case도 발견했다. 이것을 과거 GPU run이 실제로 CPU였다는 증거로 사용하지 않는다. 향후 GPU 실행 준비 시 작은 독립 fail-closed runtime patch로 다룰 문제이며, 현재 `cr_repro` digest를 불필요하게 바꾸고 기존 checkpoint 전체를 무효화할 이유는 아니다.

현재 host의 GPU 종류와 가용 VRAM은 이번 감사에서 측정하지 않았다. 원래 보고서의 RTX3090 기록을 사용자의 현재 장비로 간주하지 않는다. 새 GPU 실행이 필요해지는 시점에 해당 host를 실제 확인한다.
