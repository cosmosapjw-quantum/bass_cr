# R3M16 Coulomb/FFT h-dt representation 판정

**두 새 충돌 A1/B1과 target-only 진단은 완료됐고, 과학적 판정은
`TIME_REFINEMENT_STILL_OPEN`이다.** h=.20에서 requested dt를 .05에서 .025로
줄였을 때 P3가 1.8874437% 변해 real-time 배분 .10%를 충족하지 않았다. dt=.025의
h=.25/.20 P3 차이도 2.9527586%로 spatial 배분 .30%보다 크다. target-only
고정-horizon ladder는 단조·수치 해상도는 확보했지만 사전 등록한 clean second-order
범위에 들지 않았다. 그러므로 현 자료만으로 point-Coulomb/FFT representation 변경을
결론 내리거나 물리적 charge-transfer model의 실패로 해석하지 않는다.

## 고정된 계산과 provenance

R3M15 HEAD `65c456b61bab6a5665a0ab5d7ee63a00976ee03e`에서 전용 branch를 만들었다.
`cr_repro/*.py`는 바꾸지 않았고 numerical source digest는
`581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`로 유지했다.
A1/B1은 각각 h=.25/.20, E=100 keV/u, b=2 a0, requested dt=.025,
τ=.00625×4800, 같은 box/CAP/start/stop/projector를 사용했다. 실제 dt는 둘 다
0.02499784704477988, 1,793 step이다. 각 job은 새 preparation receipt를 만들었고
v2 witness가 collision 내부 초기상태와 saved initial bytes를 직접 결합했다.

Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0, CUDA runtime 12090,
driver API 13020, NVIDIA driver 595.84와 RTX 3090을 재사용했다. package upgrade나
CPU fallback은 없었다. A1/B1은 각각 15개 bounded chunk와 14회 sealed restart로
완료됐다. sampled GPU total-used peak는 A1 6,250 MiB, B1 11,403 MiB였다. 이는
실측 샘플이며 엄밀한 peak VRAM 상한이라고 부르지 않는다.

## target-only h-dt 진단

target-only step은 scientific runner와 같은 sampled target `-1/r` 및 FFT kinetic을
사용했으며 projectile potential과 CAP를 포함하지 않았다. 서로 다른 h의 state에 pair
theorem을 적용하지 않았다. 아래 ray distance는 capture probability error가 아니다.

| state | h | dt actual | one-step ray distance | norm drift | energy drift (Eh) |
|---|---:|---:|---:|---:|---:|
| A | .25 | .04996782581 | .003405900814 | 1.11e-16 | 6.3382040e-4 |
| A | .25 | .02498391290 | .0005426263621 | 1.11e-16 | 1.7395599e-5 |
| A | .25 | .01249195645 | .00008425421594 | 0 | 3.6839407e-7 |
| B | .20 | .04996782581 | .005826013659 | 0 | 2.3910167e-3 |
| B | .20 | .02498391290 | .001142213094 | 0 | 1.1351332e-4 |
| B | .20 | .01249195645 | .0001906330740 | 0 | 2.9055111e-6 |
| B refined | .20 | .04996782581 | .005778656966 | 0 | 2.3738326e-3 |
| B refined | .20 | .02498391290 | .001097266127 | 0 | 1.0919991e-4 |
| B refined | .20 | .01249195645 | .0001629096065 | 2.22e-16 | 2.4867251e-6 |

`d1(dt)=a_h dt+b_h dt^3`의 unconstrained 진단 적합은 A에서
`a_h=.0052205092, b_h=25.2240745`, B에서 `.0182386024, 39.4505241`, refined B에서
`.0160930451, 39.9311977`이다. coefficient를 양수로 강제하지 않았으며 certified law가
아니다. refined-B/A의 coarse one-step ray 비 1.6966604는 단순 h^-5/2 예상
1.74693과 가깝지만 증명이 아니다.

T_probe=1.0 t_a의 A는 D01=.003732331852, D12=.000597496083,
p_time=2.6430761이고 B는 .01426561416, .0009790506342, p_time=3.8650146이다.
두 ladder 모두 nonzero·monotone·resolved라 full collision을 중지할 구조적 사유는
없었다. 그러나 사전 등록 범위 1.5≤p≤2.5 밖이므로 dt=.025가 clean asymptotic regime에
있다는 근거로 쓰지 않았다.

## 2×2 collision matrix

| cell | h | requested dt | actual dt | P1 | P2 | P3 | P_region | norm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | .25 | .05 | .04996782581 | .005815498146 | .007272025974 | .007757383241 | .025905111996 | .978738989111 |
| B0 | .20 | .05 | .04996782581 | .005936876533 | .007416156281 | .007911255992 | .026216090737 | .971953800704 |
| A1 | .25 | .025 | .02499784704 | .005873247875 | .007336491990 | .007825354867 | .026017099817 | .978863461004 |
| B1 | .20 | .025 | .02499784704 | .006068282195 | .007562290857 | .008063449050 | .026422136895 | .978729910129 |

| observable | Δh(dt=.05) | Δh(dt=.025) | Δt(h=.25) | Δt(h=.20) | interaction I_ht |
|---|---:|---:|---:|---:|---:|
| P1 | 1.2137839e-4 (2.0445%) | 1.9503432e-4 (3.2140%) | 5.7749729e-5 (.9833%) | 1.3140566e-4 (2.1655%) | 7.3655933e-5 (1.2138%) |
| P2 | 1.4413031e-4 (1.9435%) | 2.2579887e-4 (2.9859%) | 6.4466016e-5 (.8787%) | 1.4613458e-4 (1.9324%) | 8.1668561e-5 (1.0799%) |
| P3 | 1.5387275e-4 (1.9450%) | 2.3809418e-4 (2.9528%) | 6.7971626e-5 (.8686%) | 1.5219306e-4 (1.8874%) | 8.4221431e-5 (1.0445%) |

Δh(dt=.05)의 상대 분모는 abs(B0), 나머지 fine-dt h 효과·h=.20 dt 효과·interaction은
abs(B1), h=.25 dt 효과는 abs(A1)이다. interaction이 P1/P2/P3에서 각각 B1의
1.214%/1.080%/1.044%이므로 h와 dt 오차를 독립 가산으로 가정하지 않는다.

## support와 claim ceiling

A1/B1 Gram condition은 1.0002123/1.0001926이고 모두 rank 14다. final state의
CAP-layer norm은 .0038706782/.0038601093이다. raw channel norms 및 channel별 CAP
fraction은 `results/R3M16/collisions/*_support.json`에 있다. rank loss나 고준위 support를
epsilon floor로 숨기지 않았다. finite selected-span complement는 continuum이 아니며
all-bound completion은 OPEN이다.

R3M15 historical result/state/seal bytes는 변경하지 않았다. global spatial convergence는
NO_GO, N1_TDL은 OPEN, b-grid는 NO_GO다. 100 keV/u cross section, 50/225 keV/u,
physical rate, 새 대형 AOCC trajectory, main merge, Nichols-code reproduction은 이
work unit의 결론이 아니다.

## 실패 보존, 시험과 다음 node

historical runner enrichment와 preparation-only control binding에서 발생한 첫 두
instrumentation 실패, 구현 전 test collection 실패를 `results/R3M16/FAILURE_LEDGER.json`
및 receipts에 보존했다. collision structural failure는 없었다. R3M16 신규 시험은
37 passed, 관련 R3M11–R3M16 범위는 122 passed다. 과거 85 PASS를 이번 수로 재사용하지
않았다. MLflow 39 trace는 outer command span만 기록하며 agent evaluation이나 scientific
admission이 아니다.

다음 canonical node는 정확히
`N1_TDL_B_DT0125_SINGLE_COLLISION_TEMPORAL_RESOLUTION`이다. 같은 h=.20 saved
preparation/config family에서 requested dt=.0125 충돌 하나만 사전 등록해 B1/B2
temporal contraction을 검사한다. 그 전에는 더 미세한 h를 실행하거나 representation을
교체하지 않는다.
