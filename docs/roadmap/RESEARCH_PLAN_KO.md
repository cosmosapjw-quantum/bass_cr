# 독립 H+ + H(1s) bound capture 연구계획

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
