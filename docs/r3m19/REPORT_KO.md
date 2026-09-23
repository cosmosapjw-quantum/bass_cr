# R3M19 — 시간 오차의 분리와 정확도를 유지하는 성능 개선

과학적 최종 판정은 **TIME_REFINEMENT_STILL_OPEN**이다. R3M18의 B2를 재실행하지 않았다. 이번에는 고정된 공간 이산화에서 full-H 시간 기준해를 만들고 오차 성분을 분리했으며, 실행 검증 결함을 수정하고 성능 후보를 실제 CPU에서 측정했다. 이 결과는 제한된 진단 도구의 승격 근거이며 production 물리 정확도 인증은 아니다.

입력은 R3M18 exact HEAD `3d033eb08a0efd99257470f0fa27214f569b427a`다. `cr_repro/*.py` digest `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`를 유지했다. GPT-6 연구/코딩 v4 하네스의 계약·반례·독립검토 방식을 적용했으며 모델 성능은 평가하지 않았다. 시험 및 검토의 최종 수치는 `FINAL_DECISION.json`과 `results/R3M19/VALIDATION.json`에 있다.

## 1. 문제를 네 층으로 분리한 판정

| 층 | 확인한 사실 | 현재 판단과 해결 방향 |
|---|---|---|
| 물리모델 | 동일 h·초기상태·두 중심 Coulomb·CAP에서 dt만 바꿔 P가 변한다 | 시간 차이를 물리모델 실패로 설명할 근거가 없다. 직선 핵 궤적, 유한 핵질량, 최종시각, 채널 완전성의 물리 불확실성은 별도로 남는다. |
| 수학/시간 알고리즘 | split 오차, 퍼텐셜 시간 구적, 비가환 시간 순서 오차가 서로 다르다 | 정확 Coulomb 시간 평균만으로 해결되지 않는다. 같은 H_h의 full-H midpoint/평균/CF4와 독립 ODE를 비교하는 코드로 분리했다. |
| 수치 정확도 | B1→B2 P3 변화 .25656% > .10%; 세 점의 p≈2.878 | 수렴은 수축하지만 등록한 pair/order screen 미충족. p>2.5가 발산이나 알고리즘 오류를 증명하지 않는다. 생산 h/상태의 짧은 구간 기준해가 다음 근거다. |
| 구현/실행/성능 | outer coordinator가 supplied config와 plan의 상호일치만 검사하던 경로; production 세부 timing 부재 | canonical config/argv/path/env 검사를 추가했다. 실제 B2 오실행의 증거는 없다. buffer reuse 및 FFT worker 후보와 GPU 계측을 별도 구현했다. |

고정 B 격자의 projectile 최소 횡거리 sqrt(.1²+.1²)=.141421 a0이므로 그 격자에서 움직이는 퍼텐셜은 유한하고 매끄럽다. 이는 h→0 극한의 Coulomb regularity나 공간 오차를 해결했다는 뜻이 아니다. 이전 h×dt interaction 1.0445%도 보존하며 공간·시간 오차의 독립 가산을 가정하지 않는다.

## 2. B0/B1/B2 재분석: 세 점으로 잔여오차를 인증할 수 없다

`scripts/r3m19_temporal_models.py`는 고정 R3M18 요약 SHA를 확인하고 actual dt로 재계산한다. raw P1/P2/P3와 norm은 변경하지 않았다.

| P3의 조건부 모형 | B2 잔여오차 상대 추정 | 의미 |
|---|---:|---|
| 세 점 single-power fitted p | .040395% | R3M18의 경험적 진단 재현 |
| P∞+c2 dt²+c4 dt⁴ | .066406% | 같은 세 점에 맞는 다른 매끄러운 모형 |
| finest pair에서 p=2 가정 | .085521% | 2차 지배를 따로 확인해야 쓸 수 있는 추정 |

세 값은 모두 인증 상한이 아니다. u=(dt/dt_ref)²에 대해 λ∏(u−u_j)를 더하면 세 자료점을 그대로 유지하면서 dt=0 값을 바꿀 수 있다. dt²+dt⁴ fit의 P3 계수는 모두 음수이고 coarsest에서 dt⁴/dt² 기여비는 약 1.239다. 따라서 높은 apparent order의 설명 후보로 고차항에서 저차항으로의 전환이 가능하지만 실제 원인으로 확정하지 않았다.

P2−P1 및 P3−P2의 차수는 약 2.456, 2.472로 cumulative P1의 2.957과 다르다. 관측량별 선도계수 차이를 봐야 한다. B1→B2 norm 상대 변화는 −.0037157%로 P3의 .25656%보다 훨씬 작다. P3/norm의 차수가 약 2.208이라는 사실은 생존 조건부 관측량의 진단일 뿐이다. 이를 raw capture 확률로 바꾸거나 사후 정규화하지 않는다. 총 norm 손실로 특정 채널의 CAP 편향을 알아낼 수도 없다.

## 3. 실제 full-H 실험

`scripts/r3m19_fullh_diagnostic.py`는 같은 주기적 DFT kinetic, point-Coulomb, 고정 rate CAP에 대해 다음을 비교한다. dense 기준 도구의 상한은 512점이며 생산 격자를 CPU로 대체하는 도구가 아니다.

- S_mid: frozen `ControlledTDLRunner.step`.
- E_mid: midpoint의 **전체 H** exponential; splitting만 제거.
- E_avg: 정확 projectile 시간 평균을 사용한 **전체 H** exponential; 시간 순서 commutator는 남음.
- CF4_fullH: Gauss 두 시점과 두 full-H exponential의 4차 후보.
- 독립 DOP853: 비자율 복소 ODE, CAP loss 보조 적분, 더 엄격한 repeat 비교.

원래 복소 벡터에서 `S−U=(S−E_mid)+(E_mid−E_avg)+(E_avg−U)`를 검사하고 Gram 교차항을 저장한다. 각 성분의 norm을 독립 오차처럼 더하지 않는다. 정확 평균은 작은 이동에서 상쇄를 피하는 atanh(x)/x 형태와 v=0 극한을 구현했다. CF4의 음의 한 계수에도 불구하고 정적 W의 각 exponential 합계는 −W/2이므로 이 구성 자체에 음의 CAP 시간이 들어가지는 않는다. 이것을 임의 음의 시간 splitting의 안정성 보장으로 확대하지 않는다.

정본 `fullh_64pt_suite_v2.json`: 4³점, h=.7, horizon=.2, incoming/closest/outgoing × CAP on/off 6건. 모두 reference-repeat 차이가 finest method error의 1% 미만이라는 **경험적** 해상도 조건을 충족했다. closest/CAP-on, dt=.0125 결과:

| 방법 | raw state distance |
|---|---:|
| frozen Strang | 4.19216e−5 |
| full-H midpoint | 1.81479e−5 |
| full-H 정확 평균 | 1.99468e−5 |
| full-H CF4 | 2.40697e−9 |

split/시간구적/시간순서 성분 norm은 각각 약 3.34210e−5, 3.10249e−6, 1.99468e−5이다. 음의 교차항 때문에 정확 평균이 midpoint보다 약간 나빠지는 실제 사례가 나왔다. Strang 차수는 약 2, CF4는 약 4.06→4.015다. 기준해 repeat 차이 약 5.45e−13, CAP loss ledger residual 약 −2.22e−16을 확인했다. CAP ledger 통과는 boundary bias 인증이 아니다.

추가 4×4×8, h=.20 stiffness probe도 실행했다. 작은 box·다른 초기상태이므로 production geometry를 대표한다고 주장하지 않는다. coarse ladder에서 apparent order가 높은 현상이 나타났고 refinement에서 Strang은 2.013→2.003으로 접근했다. CF4는 4.12→4.03으로 접근하지만 **refined 6건 모두 finest CF4 error 대비 1% reference-resolution gate 미충족**이다. 원문 결과를 보존하고 잠정 진단으로만 쓴다. 이 경고를 숨기거나 허용오차를 완화하지 않았다.

## 4. 코드 수정과 CPU/RAM/GPU 활용

`scripts/r3m18_b2_execute.py`의 launch 이전 검증을 강화했다. frozen B2 config 검증 후 canonical plan을 재생성해 interpreter, argv, 경로, cwd, 환경, prerequisites, retention, instrumentation identity를 대조한다. 임의 명령이나 다른 b가 통과하던 반례를 재현했고 신규 14건과 기존 coordinator 4건을 통과했다. 과거 B2의 결과·배열·수치 소스는 그대로다.

`scripts/r3m19_performance.py`에는 inventory, 사전 자원계획, 정확도 동반 benchmark를 추가했다. complex128 work/phase buffer 재사용과 kinetic in-place 곱을 구현했다. CPU용 SciPy FFT는 workers를 명시하고 BLAS 중첩 병렬은 제한한다. GPU 후보는 기존 CuPy FFT를 사용한다. 새로운 수치법이나 정밀도 하향을 속도 개선으로 섞지 않았다.

현재 웹 CPU Xeon 8272CL, 64×64×96, 4 steps, 2 warmups/5 repeats의 측정:

| 후보 | 기준→후보 중앙시간 | 측정 속도비 | 상대 state 차이 |
|---|---:|---:|---:|
| native FFT + buffer reuse | .47266→.30050 s | 1.57× | 6.28e−16 |
| SciPy FFT workers=1 + reuse | .41732→.21217 s | 1.97× | 1.03e−15 |
| SciPy FFT workers=4 + reuse | .43010→.14316 s | 3.00× | 1.03e−15 |

각 행은 같은 실험에서 따로 측정한 기준과의 비율이다. 이 정확도는 frozen 구현과의 동등성이며 물리해 오차가 아니다. setup, initial copy, projection, checkpoint, backup은 step timing 밖이다. 작은 CPU 수치를 6,300만 점 또는 사용자 GPU 속도로 외삽하지 않는다. RSS는 process lifetime peak여서 후보별 RAM 절감량도 아직 실측하지 않았다.

현재 환경에는 CuPy/GPU가 없어 실제 GPU 검증은 미실행이다. 최신 사용자 production evidence는 RTX3090 24GB다. 예전 Ryzen5900X/64GB 기록은 로컬 inventory로 재확인한다. CUDA event/wall timing, warmup, synchronization을 구현했고 검토 중 발견한 timed loop 내부 memory probe를 바깥으로 옮겼다. 해당 계측 위치는 회귀시험으로 검증했다.

활용 원칙은 모든 장치를 무조건 100% 점유하는 것이 아니라 **오차 기준을 만족하는 wall time 최소화**다. GPU에는 전파와 큰 벡터를 유지하고 CPU에는 작은 분석·문서·검증을 배정한다. 동시 FFT worker/BLAS/process 과다 사용을 막는다. checkpoint hash/write와 GPU 계산 중첩은 immutable staging과 기존 generation 보존을 먼저 입증해야 하며 이번에는 바꾸지 않았다. 준비 423.14초는 알려졌지만 propagation/FFT/projector/checkpoint phase별 production 시간은 미측정이다.

6,300만 complex128 상태 하나는 약 .939 GiB다. Arnoldi basis m개만으로 m×.939 GiB가 필요하므로 고차 exponential action을 이름만 보고 채택하지 않는다. matrix-free H·CAP matvec, inner action error, Krylov/Taylor 저장량, FFT workspace까지 함께 설계하고 같은 정확도에서 Strang과 작업량을 비교해야 한다. dense CF4를 생산 격자로 확대하는 것은 불가능하다.

## 5. 다른 스레드와 백업에서 가져온 것

`CROSS_THREAD_REVIEW_KO.md`에 C17, HH CONT2B, CR snapshot R5/R3M8 receipt, Atomic A7/T5, HOST4 H19의 실제 작은 보고서 5건과 receipt 9건의 identity·범위를 기록했다. 현재 시간/공간/all-bound gate를 닫는 외부 결과는 찾지 못했다. 반영한 내용은 수치수렴과 입력모형 오차 분리, evaluator precision과 차분 step 분리, source/host binding, 1s/total 및 tagged population 의미 구분이다. CX 사건의 free-electron source는 0이며 P1/P2/P3를 total gas ionization rate로 바꾸지 않는다.

R3M18 Dropbox archive의 현재 metadata와 Drive의 28 ordered parts manifest를 확인했다. 작은 manifest의 실제 bytes SHA는 `b56e11556f16011cd98a148d6ae0459c575ebdf00bff77afa3146b2494584393`로 기존 receipt와 일치한다. 938MB archive/배열의 raw readback이나 restore는 하지 않았다. `RESTORE_NOT_TESTED`를 유지한다.

Git에는 B2 분석 요약과 해시가 있지만 original 작은 result/witness/seal/receipt가 없다. 따라서 이번 재분석을 raw state reprojection 검증이라고 하지 않는다. 다음 로컬 실행의 첫 작업은 기존 작은 원문을 byte-identical하게 게시하는 것이며, 이를 위해 collision이나 preparation을 재실행하지 않는다.

## 6. 다음 한 canonical node

**N1_TDL_PRODUCTION_H_SHORT_WINDOW_GPU_REFERENCE_AND_WORK_PRECISION**.

로컬 실제 하드웨어에서 bounded GPU parity를 측정하고, 독립 tiny oracle로 검증한 matrix-free 비Hermitian full-H action이 메모리·inner-error 기준을 충족할 때만 보존된 B2 checkpoint의 최대 세 짧은 구간을 비교한다. production과 같은 h/box/CAP/실제 초기 배열에서 시간 샘플링·splitting 원인과 work-precision을 확인하는 것이 목적이다. 자세한 예산과 중지 기준은 `LOCAL_CODEX_HANDOFF.md`에 있다.

이는 새 full collision이나 B3, A2, 더 미세한 h, representation 변경을 자동 허가하지 않는다. N1_TDL 및 all-bound는 OPEN, b-grid는 NO_GO, production은 HOLD다. oracle나 메모리 조건이 불충족하면 정확한 blocker와 다음 최소 실험 하나를 반환한다.

문헌·공식 코드의 URL, 수식 위치, 버전 및 적용 한계는 `LITERATURE_AND_DERIVATION_KO.md`와 `results/R3M19/performance/PRIMARY_SOURCES.json`을 참조한다.
