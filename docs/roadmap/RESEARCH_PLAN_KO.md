# 독립 H+ + H(1s) bound capture 연구계획

## R3M29 현재 frontier — 2026-09-24

R3M29는 새 충돌 없이 point-Coulomb 특이 cell의 점값과 독립적 체적평균, 실제 7172개 projectile subcell phase의 분포를 검사했다. 국소 점값 bias는 0.91–2.97%이고 두 격자 phase histogram의 총변동거리는 약 0.00056이다. 이는 R3M28 3% 최종 확률 차이의 원인이나 공간오차 상한을 증명하지 않는다. [R3M29 보고서](../r3m29/REPORT_KO.md)에 근거해 cell-averaged Coulomb을 짧은 동일-h 검증 후보로만 선택했다.

다음 canonical node는 `N1_TDL_PRODUCTION_H_CELL_AVERAGED_COULOMB_SAME_H_SHORT_WINDOW_VALIDATION` **하나**다. Frozen production source를 바꾸지 않는 opt-in 후보를 작은 독립 기준으로 검증하고, 보존 B3 state의 최대 한 짧은 창에서 accuracy-matched endpoint와 실측 비용을 비교한다. 새 full collision·preparation·finer h·B4를 자동 실행하지 않는다. 공간 0.30% budget은 OPEN, production HOLD, all-bound OPEN, b-grid NO_GO다.

## R3M28 당시 frontier — 2026-09-24

R3M27은 고정 h=.20 selected spans의 시간 추정을 검증했다. R3M28은 같은 실제 dt와 물리 horizon의 A3/B3 비교를 한 건 실행했다. 세 채널 raw 공간 pair 차이 3.03–3.29%가 사전 0.30% screen을 초과해 `SPATIAL_PAIR_SCREEN_NO_GO`다. 이는 continuum 공간오차 하한이나 전체 오차 추정이 아니다. 보고서와 typed ledger는 [R3M28 보고서](../r3m28/REPORT_KO.md) 및 `ERROR_BUDGET.json`에 있다.

다음 canonical node는 `N1_TDL_PRODUCTION_H_SPATIAL_DISCRETIZATION_DISCRIMINATOR` **하나**다. point-Coulomb 공간 이산화와 projectile subcell phase의 영향을 사전 등록한 소규모 독립 진단으로 구분하고 다음 한 가지 공간 전략을 선택한다. A3/B3 반복, 자동 finer h, 새 full collision, representation 변경은 이 계획 갱신에 포함되지 않는다. Production HOLD, all-bound OPEN, b-grid NO_GO이며 준비/경계/최종시간도 OPEN이다.

## R3M26 당시 실행 계획 — 2026-09-24

이 절은 당시의 등록·판정 기록으로 보존한다. 아래 R3M15–R3M27 절에 적힌 '다음 node'는 현재 실행 지시가 아니다. 당시 입력은 R3M25 exact `90d6cbad25e4bc49e9563f8721fdc408761b31c7`였다.

production 목표를 **명시한 원자 모형의 내적 일관성과 수치적 충실도**로 확정한다. 특정 논문의 private data·그림 값 일치를 필수 조건으로 삼지 않는다. 원래 50/100/225 keV/u all-bound 단면적 목표는 유지한다. n≤3 단일-b 검증은 중간 산출물이다. 이론 정초는 `../r3m26/MODEL_FOUNDATION_KO.md`, 수치 전략은 `../r3m26/NUMERICAL_STRATEGY_KO.md`에 있다.

엄밀한 전역 오차 인증과 검증된 보수적 경험 추정을 구분한다. 후자도 사전 등록·새 refinement에 대한 예측 확인·모형 민감도·교차효과 검사가 있으면 model-conditional numerical budget을 닫을 수 있다. 경험 추정을 certified bound라고 부르지 않는다. 기존 총1%, 시간.10%, 공간.30% 및 나머지 배분은 유지한다. `ERROR_BUDGET.json`과 `scripts/r3m26_budget.py`가 서로 다른 관측량·범위·단위와 누락 오차를 섞지 않도록 검사한다.

| 순서 | 실제 해결할 문제 | 종료 조건과 후속 분기 |
|---|---|---|
| 0 완료 | 모델/단위/ETF/Gram/CAP/출력 정의와 증거 유형 고정 | 이론 문서 및 독립 검토. 문헌을 계속 추가해야만 다음 단계가 되는 구조를 종료 |
| 1 다음 한 node | 기존 Strang B3, h=.20, requested dt=.00625 | B0–B3 actual-dt 평가. sign/contraction, pair≤.10%, 등록 `U_time=2 max(E_model,D_hold)`≤.10%를 P1/P2/P3 모두 만족하면 이 fixed-h 시간 차원을 닫음. p∈[1.5,2.5]는 진단. factor2는 사전 설계값이며 엄밀상한/신뢰확률 아님 |
| 2 | 지배적인 공간 오차와 h–dt 결합 | 시간검증 뒤 같은 시간정확도·종점·상태정의의 spatial ladder 및 subcell translation. 기존 A1/B1 차이와 interaction을 포함해 .30% envelope 확인. h 변화만으로 해결되는지 한 번 판별한 후 필요한 경우에만 Coulomb/FFT 표현 대안 선택 |
| 3 | preparation·finite-start/stop·CAP/box | atom τ/T residual과 실제 관측량 민감도, common endpoint, CAP/box 영향으로 각각 .15% 추정. boundary/high-n support 상호작용 포함. pass한 차원을 이유 없이 반복하지 않음 |
| 4 | all-bound completion | 지원되는 n-ladder와 새 shell/tail 검증 또는 정당한 대안 projector 중 하나를 완성, .15% 충족. n=3 complement를 continuum이라 부르지 않음. 전체 AOCC solver 완성은 선택 비교 lane |
| 5 | b 적분과 tail | N1/N2 통과 뒤 .10% quadrature와 .05% tail. 각 b의 절대 오차를 2π∫b εP db로 전파. b=2 증거를 전체 b에 일반화하지 않음 |
| 6 | 에너지 확장·원자 데이터 release | 100 keV/u에서 고정한 절차를 50/225에 적용해 에너지별 지원 범위 검증. 하나의 최종 독립 판정. 실제 HOST 소비는 별도 계약 |

정확히 하나의 다음 canonical node는 `N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT`다. R3M25 실제 t=0 국소 CF4 PASS를 재사용하며 같은 목적의 새 국소-reference node를 열지 않는다. B3 관측 전 frozen forecast를 고정했고, 새 데이터는 한 번의 full collision에서 얻는다. 통과하면 spatial 단계로 이동한다. 예측과 양립하는 근소한 실패면 후속 계약에서 최대 한 refinement를 검토하고, 부호/예측/모형 간 불일치면 맹목적인 B4 대신 원인 판별로 분기한다. B3 결과를 본 뒤 이번 임계값을 수정하지 않는다.

현재 웹 작업은 B3·preparation·finer h·representation 변경을 실행하지 않았다. 실제 GPU 실행은 `../r3m26/LOCAL_CODEX_HANDOFF.md`의 후속 계약에서 source/config/environment/initial identity와 자원 한도를 고정한 뒤 진행한다. 기존 R3M14 witness는 full config 일치를 요구하므로 B2 preparation 영수증을 dt만 바꾸어 재사용하지 않는다. 새 B3 preparation의 같은 초기 배열 SHA를 확인한다.

성능 목표는 정확도와 복구 가능성을 유지한 전체 wall time 감소다. 실제 Ryzen5900X/약96GiB RAM/RTX3090 자료를 사용한다. CPU4-worker 소규모 FFT는 실제 약2.09배였으나 GPU buffer reuse는 거의1배였고 63M-grid speed는 미측정이다. 이 때문에 B3 중 propagator·precision·FFT backend를 바꾸지 않는다. GPU 전파, 제한된 CPU 검증/해시, RAM host staging을 배치하며 메모리와 I/O 비용을 따로 기록한다. 자세한 근거는 `../r3m26/PERFORMANCE_AND_CODE_REVIEW_KO.md`다.

아래는 역사 기록이다.


목표는 50, 100, 225 keV/u의 독립적인 bound capture 계산이다. Nichols 원 코드의
byte/code reproduction을 주장하지 않는다. 이 계획의 작성은 과학 단계 완료가 아니다.
기준 반환 authority는 `8c7bbfce157f17b85dc9082c62c63c05fef3b294`, numerical source
digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`다.
실행 상태와 입출력·실패 분기는 `DAG.json`, 목표 배분은 `ERROR_BUDGET.json`에 있다.

## N0 — 관측량·판정·오차예산

P1/P2/P3는 projectile의 sampled analytic hydrogen n≤1/2/3 span에 대한 Gram
보정 orthogonal projection이다. P_region은 z>30 영역 비교량이다. finite-span
complement를 continuum이라 부르지 않는다. `(P3-P2)/P3`는 nested-span increment이며
n>3 tail bound가 아니다. 서로 다른 grid의 상태에는 같은-Hilbert-space 정리를 쓰지 않는다.

공통 contraction K와 projector Q, 정규화 초기상태의 phase-aligned 거리 d에 대해
`d <= sqrt(p_ref)*.01/(sqrt(1.01)+1)`은 1% 상대 변화의 충분조건이다.
역은 성립하지 않는다. `d>d_star`는 INCONCLUSIVE이며 직접 측정 FAIL과 구별한다.
p_ref=0은 상대 판정 미정의다. 역사적 R3M14 NO_GO와 old initial.npy의 binding 부재는
보존한다. 새 addendum은 과거 theorem certificate를 소급 PASS로 만들지 않는다.

초기 numerical total relative-error 목표 1%: preparation .15%, spatial .30%,
real-time .10%, box/CAP/finite-time .15%, bound-channel truncation .15%,
b-quadrature .10%, b-tail .05%. 이는 아직 달성하지 않은 계획 목표다. 인증 상한이
있을 때만 보수적 합을 적용한다. 경험적 차분/외삽과 엄밀한 상한은 별도 기록하고,
독립성이 없는 오차의 제곱합이나 여러 1% pair PASS를 총오차 1%로 바꾸지 않는다.

## N1 — 100 keV/u 단일-b의 두 lane 수렴

TDL은 preparation τ/T, 공간 h, real dt, box와 고정 rate CAP, start/stop separation을
분리한 ladder로 검증한다. 이번 R3M15는 b=2, τ=.00625×4800, h=.25/.20/.3125의
최대 세 충돌뿐이다. A를 먼저 과거 h=.25, τ=.0125와 비교한다. 각 preparation은
별도 저장하고 v2 witness가 충돌 내부 초기상태와 직접 binding한다. spatial matrix가
완료되어도 dt/boundary/preparation의 전체 목표는 닫히지 않는다.

세 h의 비는 1.25다. 같은 τ, dt, box, CAP의 같은 관측량에서 차분이 동일 부호이고
명확하게 감소할 때만 observed order와 3점 Richardson 값을 계산한다. 이 값은
경험적 single-power 가정의 진단이며 continuum 인증값이 아니다. 단조 수렴이
확인되지 않으면 실제 원인을 특정한 representation decision으로 이동한다.

R3M16은 A/B에서 target-only dt=.05/.025/.0125 고정-horizon 진단과 A1/B1
requested dt=.025 충돌을 완료했다. h=.20 P3 dt 효과 1.8874%, dt=.025 h 효과
2.9528%, interaction 1.0445%로 real-time .10%와 spatial .30% 배분을 모두 닫지
못했다. target-only p_time은 A 2.643, B 3.865로 단조·resolved이지만 사전 등록한
clean second-order 범위 밖이다. 따라서 `TIME_REFINEMENT_STILL_OPEN`이며 current
representation 유지나 변경을 아직 선택하지 않는다. 다음 node는 h=.20에서 같은
preparation/config family의 requested dt=.0125 full collision 하나로 temporal
contraction을 검사한다. 그 결과 전에는 더 미세한 h를 자동 실행하지 않는다.

현재 `cr_repro/aocc.py:OneElectronAOCC`는 s와 세 Cartesian p 방향 Gaussian basis를
두 중심에 대칭으로 사용하고 eps_max cutoff 이하 상태를 유지한다. run()은 음의
atomic eigenvalue를 가진 모든 s+p projectile 상태의 aggregate만 반환한다.
이는 TDL n≤3와 truncation이 다르며 현재 코드에는 final C/O의 durable 저장도 없다.

AOCC의 다음 구현 단위는 다음과 같다.

- final coefficients C, metric O, basis center/angular/radial index, atomic energies와
  eigenvectors, 실제 dt/시각/ETF convention을 저장한다. 임의 energy bin만으로 n을
  지정하지 않고 hydrogen 1s/2s/2p/3s/3p/3d와의 수렴된 overlap/identity mapping을 만든다.
- 공통 1s/n≤2/n≤3 readout은 finite metric projector
  `v† G^-1 v`, `v=B† O C`, `G=B† O B`로 설계한다. rank/condition/support를 노출하고
  rank loss를 floor로 숨기지 않는다. target/projectile span 및 channel identity를 기록한다.
- radial 크기(ns,np), exponent 최소/최대, positive-energy pseudostate cutoff,
  angular lmax, dt를 각각 독립 ladder로 만든다. 양 중심에서 동일 completeness 규칙을 쓴다.
- matrix(t)의 D와 finite-difference dot(O)를 독립 비교하여 `dot(O)=D+D†`를 검증한다.
  generator()의 기존 defect는 기록하되 unitary_step()이 Hermitian symmetrization을
  수행하기 **전** G+G† defect와 실제 metric derivative 오차를 각각 검사한다.
- d 및 그 이상 angular basis의 실제 analytic primitive/rotation/ETF 확장·시험 전에는
  n≤3 전체 channel validation을 금지한다. s+p aggregate는 그 대체물이 아니다.

이번 작업은 AOCC의 새 대형 trajectory를 실행하지 않는다.

## N2 — 같은 관측량 비교와 all-bound completion

두 lane의 내부 수렴 후 동일 1s/n≤2/n≤3 상태 정의·ETF·최종 separation을 맞춰 비교한다.
각 basis와 finite box의 support, Gram rank/condition, raw channel norm을 함께 본다.
고 n 진단은 두 중심 completeness와 box/CAP support가 충분할 때만 근거로 쓰며,
단일 n=4 increment를 all-bound tail 상한으로 사용하지 않는다. bound truncation 목표
.15%를 별도로 닫기 전에는 all-bound가 OPEN이다.

## N3 — 100 keV/u impact-parameter 적분

N2 exit 후 별도 승인된 adaptive b-grid, 국소 quadrature refinement와 b-tail extension을
수행한다. `sigma=2π∫b P_bound(b) db`의 단위는 a0²다. b quadrature와 tail의 오차를
분리한다. 현재 admission은 NO_GO이고 이 계획은 실행 허가가 아니다.

## N4 — 50 및 225 keV/u

100 keV/u 절차가 고정된 뒤 각 에너지의 독립 계산과 energy-specific 검사를 수행한다.
정해진 절차를 그대로 적용할 수 없는 경우 해당 수렴 차원을 명시적으로 다시 연다.
이번 work unit에서는 두 에너지 모두 NOT_RUN이다.

## N5 — atomic release·외부 비교·BASS scoped handback

atomic dataset, 원자 channel/energy support, 수치 오차 및 provenance를 함께 공개하고
고정 literature authority와 비교한다. HOST/P0 외부 gate는 atomic single-b 실행의
선행조건이 아니다. HOST consumer 인수는 source/channel/energy support와 state/host
contract가 일치할 때 별도 승인한다. 50/100/225 세 점은 HOST의 4–81 keV/u 연속
1s source가 아니다. 외부 비교나 업로드 성공은 source admission을 대신하지 않는다.

## 유한 실행 및 중지 규칙

NaN/Inf, projector 부적합, binding/source 불일치, checkpoint 손상, 메모리 예산 위반은
해당 job을 중지하고 증거를 보존한다. 수치 허용오차 초과나 차수 미정은 scientific
nonconvergence로 기록한다. tolerance/CAP/box/energy/b를 바꾸어 PASS를 만들지 않는다.
이번 세 collision 이후의 refinement, b-grid, physical rate, main merge는 실행하지 않는다.


## R3M17 보완 — 실제 production admission과 다음 한 계산

정본 R3M16 결과는 보존한다. 외부 원전 및 코드 검토와 작은 격자의 독립 full-H
reference를 완료했다. `docs/r3m17/REPORT_KO.md`와 `LOCAL_CODEX_HANDOFF.md`가
후속 진단 계약이다. 이것은 production 또는 N1 완료가 아니다.

- C(h=.3125)의 projectile transverse mesh phase가 A/B와 다르므로 이전 세 h의
  power-law 해석은 h 변화 외에 translation 오차를 포함한다. C를 버리지 않고 이 한계를
  기록하며, 차후 spatial protocol에 subcell translation 검사를 넣는다.
- 정지 target-only apparent order는 moving two-center 시간오차의 admission gate가 아니다.
  B0/B1/B2의 signed 차분과 실제 dt로 차수를 계산하며 Richardson는 conditional empirical
  estimate로만 쓴다. pair difference가 목표 안에 드는 것과 잔여오차가 제어된 것은 다르다.
- B2만 추가해도 dt=.0125의 A2/B2 h-gap은 미측정이다. B2-A1을 spatial gap이라 하지 않는다.
- 큰 FFT 격자의 full-H exponential/CFE reference는 memory/cost 사전 조사 뒤 별도 수행한다.
  현재 tiny dense oracle는 최대512점으로 제한되며 큰 GPU CPU fallback은 없다.
- 이번 AOCC 검사는 18-basis smoke의 독립 moving-metric identity만 검증했다.
  final C/O, d 채널과 radial/angular/pseudostate ladder는 미구현/미실행 상태로 유지한다.
- numerical 1% 목표와 물리모델 불확실성을 구분한다. 각 b의 오차를 단면적으로 전파할 때
  |δσ|≤2π∫b εP(b)db를 사용하고 rare channel에는 사전 등록된 absolute 기준이 필요하다.

다음 canonical node는 `N1_TDL_B_DT0125_SINGLE_COLLISION_TEMPORAL_RESOLUTION`
하나다. 새로운 full collision 예산은 B2 한 개이며 3586 step/29 chunks(마지막2)다.
chunk마다 다음 저장 전에 검증된 checkpoint generation을 보존한다. scientific dt
nonconvergence는 구조적 실패와 구분하며 그 이유만으로 run 수를 늘리지 않는다.
B2 후 해석과 다음 구체 노드를 반환하고 멈춘다. N1의 모든 차원·N2 고n 채널·N3 b적분·
N4 다른 에너지·N5 source admission은 기존 계약과 오차배분 그대로 남는다.

## R3M18 결과 — B2 완료와 다음 시간표현 진단

R3M18은 frozen h=.20 family에서 requested dt=.0125 B2 하나를 완료했다. 실제 dt는
0.01249892352238994이고 3586 steps를 29 chunks로 실행했다. fresh preparation 초기 배열은
B0/B1과 byte-identical이며 v2 witness가 실제 내부 initial을 binding했다. 각 chunk 뒤 다음
chunk 전에 immutable generation을 게시했고 첫 실패·retry·restore는 없었다.

B1→B2 상대 변화는 P1 0.27869%, P2 0.25913%, P3 0.25656%로 real-time .10%
pair screen을 모두 넘었다. 실제 dt를 쓴 관측차수는 2.878–2.957로 contraction은 있으나
사전 등록 clean second-order 범위 1.5–2.5 밖이다. single-power Richardson 조건부 fine
remainder는 0.0402–0.0412%이지만 세 점 자체가 모델 잔여를 독립 검증하지 못하므로
certified bound나 budget closure가 아니다. 판정은 `TIME_REFINEMENT_STILL_OPEN`이다.

A2가 없으므로 dt=.0125 spatial gap은 `NOT_MEASURED`다. 다음 canonical node는
`N1_TDL_MOVING_TWO_CENTER_FULL_H_TEMPORAL_REFERENCE_DIAGNOSTIC`이다. 작은 고정 grid의
동일한 움직이는 두 중심 discrete `H_h(t)-iW`에 대해 non-Hermitian-capable full-H
exponential-action reference를 독립 수렴시키고 현재 split propagation과 공통 horizon에서
비교한다. 이 진단이 시간표본화/splitting error를 분리하기 전에는 새 production collision,
finer h 또는 representation 변경을 승인하지 않는다.


## R3M19 — full-H 오차 분리와 성능 후보

R3M18의 작은 원본 요약과 actual dt를 재분석했고, 세 점 외삽이 잔여오차를
인증하지 못함을 수치/대수적으로 확인했다. 64점 moving two-center full-H
midpoint/정확 평균/CF4와 독립 DOP853 6사례는 등록 reference-repeat 기준을
충족했다. h=.20 직사각형 tiny stiffness probe의 refined CF4 6사례는 그
기준을 충족하지 못해 잠정 진단으로 보존한다. 생산 격자/초기상태의 기준해는
아직 없다. TIME_REFINEMENT_STILL_OPEN, all-bound OPEN, b-grid NO_GO다.

outer 실행 coordinator의 canonical config/argv/path 검증 결함을 수정했다.
수치 cr_repro 소스와 역사 결과 bytes는 유지했다. buffer reuse와 명시적
CPU FFT worker 후보가 웹 CPU microbenchmark에서 1.57/1.97/3.00배를
보였지만 사용자 CPU/GPU 또는 전체 collision 속도는 미측정이다.

현재 canonical node는 N1_TDL_PRODUCTION_H_SHORT_WINDOW_GPU_REFERENCE_AND_WORK_PRECISION
하나다. docs/r3m19/LOCAL_CODEX_HANDOFF.md의 로컬 hardware inventory, 작은
GPU parity, tiny oracle로 검증한 matrix-free 비Hermitian full-H action,
자원 preflight를 순서대로 수행한다. 통과할 때만 보존 B2 checkpoint 최대
세 구간, 각 4 B2-step 이하를 비교한다. 총 GPU 2시간/4000 FFT matvec
상한이다. 신규 full collision/preparation/finer h 예산은 0이다. 다음
production propagator 선택은 같은 정확도에서 측정한 비용을 근거로 하며
현재 성능 후보를 frozen production에 자동 적용하지 않는다.

## R3M27 — B3 실측 시간 추정 완료, 다음은 공간·h_dt

R3M26 사전 예측을 수정하지 않고 exact B3 preparation 1회와 witnessed 7172-step
full collision 1회를 실행했다. 57개 immutable generation을 모두 보존하고 해시로
재검증했다. B1→B2와 B2→B3의 fine increment는 P1–P3 모두 같은 부호로
수축한다. B3 중앙값 기준 pair와 경험적 `U_time=2 max(E_model,D_hold)`가
세 채널 모두 .10% 이내여서
`TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS`다. 이는
비인증 경험 추정이며 production PASS나 전체 N1 완료가 아니다.

다음 canonical node는 `N1_TDL_PRODUCTION_H_SPATIAL_H_DT_BUDGET` 하나다.
새 실험 전에 같은 물리적 horizon과 실제 dt에서 h=.25/.20 공간 차이를
어떻게 측정할지, projectile subcell translation 및 h-dt 상호작용을
어떻게 한 번만 계상할지 사전 등록한다. 기존 dt=.025 P3 h 차이 약
2.9528%와 h-dt interaction 약 1.0445%는 .30% 공간 배분을
닫지 못한다. 자원·판별력 계약 전에는 새 finer-h collision을 시작하지
않는다. 공간 다음에는 preparation, box/CAP/finite-time, all-bound,
b-quadrature/tail, 50/225 keV/u 순서로 동일 모형의 numerical budget을
닫는다. 현재 production HOLD, all-bound OPEN, b-grid NO_GO다.
