# R3M17 — production 사용을 위한 연구·검증 코드 보완

기준 정본은 R3M16 `7844bc0d8122070b267ee77c75cb2c9447435155`이다. 이번 작업은
외부 원전·코드 조사, 재현 가능한 결함 수정, 독립 시간전파 기준해, 후속 GPU 실행계약을
완성한다. **과학적 판정은 TIME_REFINEMENT_STILL_OPEN, production admission은 HOLD**다.
새 production full collision은 0회이며 B2는 NOT_RUN이다. 작은 64점 격자의 검증 예제를
100 keV/u, b=2 생산 계산으로 세지 않는다.

## 1. 연구 결과: 단순한 dt 축소 이상의 문제가 있다

현재 계산은 atomic units로 고정된 비상대론적 전자 TDSE,
`i dψ/dt=[-Δ/2-1/r-1/|r-R(t)|-iW]ψ`, `R=(b,0,vt)`를 푼다.
`a0`, `Eh`, `ta=ħ/Eh`, `v_au=a0/ta`이며 핵은 정해진 직선운동을 한다.
생산 목표의 1%는 이 모델 안의 **numerical** 목표다. 핵 궤도 근사·유한질량·상대론 등
model discrepancy가 자동으로 1% 안에 들어온다는 주장은 별도다.

| 판단 | 근거 상태 | 결론의 범위 |
|---|---|---|
| R3M16의 dt 변화는 무시할 수 없다 | 기존 실행 결과, 정본 직접 확인 | B0→B1 P3 1.8874%; R3M16 판정 유지 |
| h와 dt 효과의 독립 가산은 정당화되지 않는다 | 기존 matrix 직접 검산 | P3 interaction/B1=1.0445%; 차원별 합성에 교차검사가 필요 |
| Coulomb splitting의 공간·시간 극한은 비균일할 수 있다 | literature-supported | 수소 원전은 메커니즘 근거; 현재 충돌의 오차 정리는 아님 |
| C와 A/B는 핵의 transverse mesh phase가 다르다 | derived/configuration-verified | C/A/B 하나의 순수 h power law는 추가 가정 |
| 현재 코드의 기본 Strang/midpoint 구현은 작은 격자에서 2차다 | implementation-verified, numerically checked | 동일 H_h 시간 구현 검증; continuum 정확도는 미검증 |
| production 정확도 | unresolved | 준비·공간·시간·CAP/경계·채널·b 적분이 남음 |

### 원전이 기존 설명에 가하는 제한

[Burgarth et al. 2024, PRR 6,043155](https://arxiv.org/pdf/2312.08044), Fig.6/8은
수소 1s에서 공간 truncation이 커질수록 형식적 시간 2차 영역의 진입점이 이동하는 사례를
직접 제시한다. 단순히 Strang을 고차 Suzuki 조합으로 바꾸면 문제가 해결된다고 볼 수 없다.
[Fang–Wu v2, 2026-08-24](https://arxiv.org/html/2604.07704v2)의 Thm.1은 더 일반적인
Coulomb 초기상태에 대한 upper bound를 주지만, Remark39는 **고정 최종시간의 many-step
quarter-order lower bound는 아직 증명하지 않았다**고 제한한다. 이 정리는 autonomous,
Hermitian, kinetic-outer 조건이고 현재 코드는 moving-potential, CAP, potential-outer다.
현재 P3에 그 지수를 그대로 적용하지 않는다.

기존 `||[V,[T,V]]ψ1s||~a^(-5/2)` 유도는 원점 밖의 formal cutoff norm이다.
FFT 이산 미분은 연속 Leibniz 항등식을 그대로 만족하지 않으며 다른 commutator,
원점의 distribution/domain, 시간의존성, 관측량 방향성과 CAP는 포함되지 않았다.
A/B scaling 비율의 유사성은 **conjectural 설명**으로 남기고 설계 규칙으로 쓰지 않는다.
세부 원전·열람범위·대안은 `LITERATURE_REVIEW_KO.md`에 기록했다.

### 독립 시간 기준해가 필요한 이유

같은 이산 Hamiltonian H_h, 정규화 ψ, E=<H_h>, r=(H_h-E)ψ에 대해
`||exp(-itH_h)ψ-exp(-itE)ψ|| <= |t| ||r||`이다. 따라서 split state와 **초기 ray**를
비교하면 정확 evolution의 preparation drift까지 섞인다. 새 기준량은
`d(S_h(dt)ψ, exp(-itH_h)ψ)`다. 잔차와 splitting은 벡터이므로 스칼라 norm을
`a dt+b dt^3`로 적합한 계수는 두 물리 기여의 직접 분해가 아니다.

고정 이산화에서 초기 ray distance의 제곱은 `σ_H² dt²+c4 dt⁴+...` 형태로 전개할 수
있지만, 이것도 맞춘 계수만으로 원인을 결정하지 않는다. 새 oracle은 dense DFT로 full
H_h를 독립 구성하여 eigendecomposition을 쓰며, 이동 두 중심에서는 full-H ODE를
DOP853로 풀고 tolerance를 다시 줄여 기준해의 안정성을 확인한다.

### 정지 target 검사가 놓치는 축

`v dt/h`는 이동 핵의 grid crossing 시간표본화다. h=.20에서 B0/B1/B2 계획값은
각각 .501672/.250976/.125488 cell/step이다. 동시에 FFT 최대 kinetic phase는
18.4936/9.25196/4.62598 rad이다. 이 수치는 **resolution indicator**이고 unitary
splitter의 CFL 불안정성 기준은 아니다. 실제 고주파 점유와 관측량 영향이 필요하다.

A/B의 projectile 최소 transverse 거리/h는 .707107이지만 C는 .509902이다.
`b=2`, x-origin과 h의 비가 바뀌어 나타나는 정확한 grid-phase 차이다. C의 결과를
폐기하지 않고 h+mesh-phase를 함께 바꾼 관측으로 유지한다. spatial 설계에는 앞으로
고정 h의 subcell translation 검사를 포함해야 한다.

## 2. 실제로 수정한 코드와 확인한 결함

과거 재현성을 위해 R3M16 instrumentation과 `cr_repro/*.py`는 동결하고, 향후 실행이
사용할 corrective successor를 `scripts/r3m17_*.py`로 구현했다. 기존 함수의 결함을
새 도구로 우회하여 다음 실행에서 사용하지 않게 하는 명시적 전환이며, 과거 결과를 다시
쓰거나 소급 PASS로 바꾸지 않는다.

| 파일 | 수정 내용 | 검증 기준 |
|---|---|---|
| `r3m17_reference.py` | 직접 phase-aligned 차분, norm을 포함한 거리, full-H 시간 oracle | 1e-10 ray 분해능, global phase, CAP norm loss 분리, exact eigenstate, 이동 두 중심 ODE |
| `r3m17_temporal.py` | 실제 config/source/backend/channel/시간/binding 검사 후 B0/B1/B2 분석 | 잘못된 에너지·h·dt·source·checkpoint·rank 거절, 실제 dt의 signed 차수, zero/nonmonotone 처리 |
| `r3m17_preflight.py` | B2 한 개의 정확 config·자원·sampling·chunk 계획 | B1의 dt만 변경, nstep=3586, 29 chunks, 마지막 2 step, singular grid 경로 거절 |
| `r3m17_checkpoint_guard.py` | 이전 sealed generation 보존 및 fresh 경로 복구 | state/metadata 갱신 사이 중단 주입 후 이전 generation 복원 |
| `r3m17_aocc_metric.py` | 독립 dot(O), dot(R) 차분과 D·generator 비교 | 구조적으로 만들어진 anti-Hermiticity와 실제 moving-basis 항등식을 분리 |

기존 ray 식 `sqrt(2-2*sqrt(fidelity))`는 1e-8 이하에서 0으로 상쇄됐다. 기존 analyzer는
복제한 B1의 status/h/E/dt/source를 바꿔도 completed B1으로 수용했다. 실제 R3M16
입력이 틀렸다는 증거는 없고, 현재 결과보다 작은 오차에서 또는 다음 입력에서 결함이
작동할 수 있음을 재현했다. 원 재현과 최초 실패는 `results/R3M17/audit/` 및 각 receipts에 있다.

기존 checkpoint는 array→metadata→seal 순서로 교체되어 그 사이 중단하면 이전 sealed
array가 사라졌다. 해시 검사는 이를 정상적으로 거절하지만 복구본은 남지 않는다.
새 generation guard는 **완료된 chunk 뒤**, 다음 쓰기 전에 array의 hardlink와 작은
metadata 사본을 보존한다. atomic replace로 새 array inode가 쓰이므로 이전 generation은
남는다. 다른 filesystem에는 묵시적 대용량 copy fallback을 하지 않는다. 기존 손상 경로는
보존하고 별도 fresh 경로만 복원한다. 모든 chunk를 보존하면 B2 array 29개에 약 29.232 GB
(27.225 GiB)가 유지되므로 시작 전에 디스크 여유를 확보한다. 이것은 VRAM 상한이 아니다.

## 3. 실제 경량 실험

`results/R3M17/reference/tiny_temporal_oracle_v2.json`은 4×4×4 주기 격자, h=.7,
T=.4의 **검증 예제**다. 실제 실행 환경은 Python3.12.14 / NumPy2.3.5 / SciPy1.17.0
CPU이며 production Python3.12.3/CuPy14.2.0 환경과 다르다. production 환경은 변경하지 않았다.

| 기준 문제 | dt=.05의 오차 | dt=.025의 오차 | dt=.0125의 오차 | 두 observed orders |
|---|---:|---:|---:|---|
| discrete Coulomb eigenstate → full-H dense oracle | 3.85136e-4 | 9.61947e-5 | 2.40431e-5 | 2.00134, 2.00033 |
| moving physical two-center → full-H DOP853 | 1.13857e-3 | 2.85154e-4 | 7.13205e-5 | 1.99742, 1.99935 |

Smooth periodic control의 차수는 2.00028, 2.00007이다. DOP853 두 tolerance 결과의
위상 정렬 전 차이는 1.32702e-11로 finest split error 7.13205e-5보다 충분히 작다.
이 결과는 부호·kinetic factor·midpoint·시간차수 구현의 독립 검사다. **동일 H_h를 공유하므로
공간 표현의 정확성, 큰 격자의 asymptotic onset, 실제 P1/P2/P3의 수렴을 보장하지 않는다.**
CuPy path와 production array oracle는 실행하지 않았다.

AOCC는 18개 basis의 smoke 설정에서 incoming/closest/outgoing 세 시각과
ε=.004/.002/.001/.0005의 matrix만 평가했다. Finest metric relative residual 최대는
1.98624e-7, 독립 raw generator defect는5.10655e-8이다. 최종 두 ε의 진단 기준을
만족해 PASS_LOCAL_METRIC_IDENTITY_ONLY를 얻었다. Coarse ε에서의 기준 초과도
원 결과에 그대로 남겼다. 기존 constructed generator defect가 약1e-15인 것은
그 자체로 물리적 D 항의 정확성을 검증하지 않는다. D 부호를 뒤집는 시험에서는
독립 검사가 실패한다. 이 국소 PASS는 basis 수렴·d channels·capture 정확도가 아니다.


## 4. 외부 방법 선택

| 후보 | 지금 채택할 부분 | 바로 production 교체하지 않는 이유 |
|---|---|---|
| 현 H_h + full-H exponential/CFET | 시간전파 독립 기준과 후속 비용 비교 | 큰 격자의 vector memory, exponential action과 time-ordering 오차를 별도 제어해야 함 |
| tRecX FE-DVR, off-center Coulomb | 실제 API가 있는 독립 공간 reference 설계 | stationary off-center 예제가 moving two-center capture를 구현한 것은 아님 |
| Coulomb asymptotic correspondence / hybrid CN | cusp-aware spatial stencil 후보 | stencil 원전 접근 범위·weighted inner product·임의 b의 3D 확장이 남음 |
| Coulomb-wave DVR / Qprop | one-center spectrum, hydrogen propagation reference | 이동 projectile bound packet과 전체 capture 채널에 추가 확장 필요 |
| 현재 AOCC 확장 / TC-BGM·SC-CCC 비교 | 가장 가까운 독립 공간 lane | s+p aggregate는 TDL n≤3 아님; d basis, radial/pseudostate/metric convergence가 필요 |

BDSCx 원전 Eq.17은 r<.2a0에서 Coulomb를 cap한다. volume integral 보정은 Hamiltonian
동일성이 아니므로 현재 -1/r의 무심한 대체로 사용하지 않는다. 반면 TC-BGM의 regularized
potential은 **basis generator**이며 physical Hamiltonian을 cap하는 것과 다르다.
TC-BGM 2019는 1–300keV를 다루지만, 원문은 특정 H(2p) 고에너지 n=6 capture의 수치문제도
보고한다. energy 범위가 맞는다고 모든 채널의 1% 기준해가 되는 것은 아니다.
외부 solver build/run이나 코드 reproduction은 이번 작업에서 주장하지 않는다.

## 5. 다음 계산이 결정할 것

canonical node는 그대로 `N1_TDL_B_DT0125_SINGLE_COLLISION_TEMPORAL_RESOLUTION`이다.
B2는 h=.20, requested dt=.0125, 실제 dt=.01249892352238994, 3586 step이며 다른
물리/config/preparation 규칙을 바꾸지 않는다. **새 full collision 정확히 1개**다.

B0/B1/B2의 동일 방향 차분에서 실제 dt를 사용하여

`(dt0^p-dt1^p)/(dt1^p-dt2^p)=(P1-P0)/(P2-P1)`

를 푼다. fine correction은 `(P2-P1)/[(dt1/dt2)^p-1]`이다. 이것은 single-power
가정의 **conditional empirical estimate**다. sign reversal, unresolved 차분,
비수축, zero relative denominator는 별도 상태로 반환하며 어떤 경우도 certified PASS가 아니다.
P1/P2/P3 모두 보며 norm/CAP drift를 따로 기록한다. target-only 차수를 여기에 대입하지 않는다.

정확히 2차라는 **가정하의 forecast**에서도 B2의 P3 pair 변화는 .47034%, fine remainder는
.15678%다. .10% 목표에 자동으로 닿을 것이라고 기대하면 안 된다. 이 예측은 실제 B2값이
아니며 다음 실행 횟수 확대를 승인하지 않는다. `SECOND_ORDER_COST_FORECAST.json`에 분리했다.

B2 후에도 A2가 없으므로 dt=.0125의 spatial gap은 미측정이다. B2−A1을 순수 h 효과로
쓰지 않는다. 모든 temporal 수치가 좋아도 먼저 empirical candidate로 두고 A쪽 시간검사,
이동 원자·CAP/finite-time cross-check와 동일-dt h 비교를 통해 다음 구체 노드를 고른다.
B2가 비수렴하면 원인을 분리한 full-H/이동 핵 진단 또는 시간전파 설계를 선택한다.
B3, finer h, soft core, 대형 AOCC, b-grid를 자동 추가하지 않는다.

## 6. production까지의 남은 조건

기존 N0–N5와 오차예산은 보존했다. N1_TDL에서 temporal estimate, mesh phase/spatial,
preparation, box/CAP/start–stop가 각각 닫혀야 한다. AOCC는 독립 metric identity를 먼저
검사하고 final C/O와 양 중심 공통 channel readout을 저장한다. 고 n tail은 n=3 increment로
추정하지 않으며 N2에서 support/rank와 근거 있는 truncation estimate를 요구한다.
N3에서는 `σ=2π∫ bP(b)db`와 함께 `|δσ|≤2π∫b εP(b)db`의 입력오차 전파를 기록하고
quadrature/tail을 분리한다. 50/100/225 세 점은 연속 rate kernel이 아니다.

**이번 산출물은 production으로 진행할 검증 기반이며 production dataset 자체가 아니다.**
최종 시험·독립 판정·게시 identity는 `FINAL_DECISION.json`, `DELIVERY_RECEIPT.json`,
`results/R3M17/INDEPENDENT_REVIEW.json`에 기록한다. 전체 local 실행계약은
`LOCAL_CODEX_HANDOFF.md`다.
