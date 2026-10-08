# R3M13: 초기상태 준비 오차와 충돌 확률의 조건부 분리

Parent: `02546302a3d6958ea9fa97488a670672e07be178`.
범위는 target-frame H+ + H(1s), 100 keV/u, b=2 a0의 기존 유한 격자 모델이다.
새 production 충돌 계산, b 적분, 단면적, 물리 rate는 수행하지 않았다.

## 1. source-derived 상태

R3M12의 동일 preparation(.025 x 1200), fixed CAP, real dt=.05에서
dx=.3125 -> .25의 P_span 변화는 2.289941%이다.
dx=.25의 P_span=.00775827737938, stationary residual=.021078203 Eh이다.
이 숫자는 원 저장소 반환값이며 이번 세션에서 재계산한 production 결과가 아니다.
R3M12가 지정한 다음 비교(.025 x 1200 vs .0125 x 2400)를 변경하지 않는다.

## 2. 유한 격자 Strang 준비의 고정점

공간격자 h를 고정하고, T_h,V_h를 유한차원 self-adjoint 행렬이라 하자.
imaginary step τ에서
S_τ = exp[-τ V_h/(2ℏ)] exp[-τ T_h/ℏ] exp[-τ V_h/(2ℏ)]
는 positive-definite Hermitian이다. 초기벡터가 dominant eigenspace와 겹치고
최대 고유값이 단순하면 정규화 반복은 S_τ의 dominant eigenvector로 수렴한다.
이 벡터는 H_h=T_h+V_h가 아니라
H_eff(τ)=-(ℏ/τ) log S_τ
의 최소 고유벡터이다. 고정된 유한 행렬에서 τ->0일 때
H_eff(τ)=H_h+O(τ²); 계수는 commutator와 격자에 의존한다.
Coulomb h->0에 균일한 상수나 production residual 오차율을 주장하지 않는다.

따라서 총 준비시간을 연장해도 H_h의 residual floor가 남을 수 있다.
반대로 H_h의 정확한 고유벡터도 유한 real-time Strang propagator의
고유벡터와 일반적으로 같지 않다. Hamiltonian residual과 target-only
real-time ray defect는 따로 기록해야 한다.

문헌 원천: Oppermann, Eicke & Lein, J. Phys. B 55, 19LT01 (2022),
DOI 10.1088/1361-6455/ac8bb9. 논문은 model-atom laser ionization의
propagator eigenstates를 다룬다. 여기 p-H 충돌의 직접 검증으로 전용하지 않는다.

## 3. 직접 유도: 초기상태 pair -> 동일 전파 뒤 확률

같은 weighted finite-grid Hilbert 공간에서 ||a||=||b||=1,
q=|<a,b>|, d=min_φ ||a-exp(iφ)b||=sqrt(2-2q)라 하자.
계산은 cancellation을 피하려고 phase-align한 배열의 차이를 직접 합산한다.

K는 두 상태에 공통인 선형 contraction, ||K||<=1이다.
기존 fixed-CAP Strang step은 real potential phase, unitary FFT kinetic,
0<M<=1 CAP 곱이므로 exact arithmetic에서 contraction이다.
real-time 중 상태 renormalization은 허용하지 않는다.
Q는 동일한 finite-span orthogonal projector이다. Gram 보정된 Q를 쓰며
raw nonorthogonal overlaps의 단순 합이나 서로 다른 grid의 Q를 쓰지 않는다.

p_a=||QKa||², p_b=||QKb||²에 대해 reverse triangle inequality와
contraction을 적용하면
|sqrt(p_b)-sqrt(p_a)|
 <= ||QK(b-exp(-iφ)a)|| <= d.
그러므로
max(0,sqrt(p_a)-d)² <= p_b <= min(1,(sqrt(p_a)+d)²).

또한 A=K†QK는 0<=A<=I인 effect이며
D(a,b)=(1/2)|| |a><a|-|b><b| ||_1=sqrt(1-q²)
      =d sqrt(1-d²/4).
따라서 |p_b-p_a|<=D. 코드는 두 interval의 교집합을 반환한다.

relative pair screen |p_b-p_a|<=s p_a의 충분조건은
d <= sqrt(p_a) (sqrt(1+s)-1)
  = sqrt(p_a) s/(sqrt(1+s)+1).
p_a=.00775827737938, s=.01의 계획용 threshold는
d_star=.00043930987793803503109988이다.
Wolfram에서 이 충분조건의 전칭 명제=True와 fidelity identity residual=0을 확인했다.

이 명제는 exact initial ground state로의 오차, 전체 spatial/time/absorber
오차, all-bound capture, 불확실성 공분산, b-grid GO를 인증하지 않는다.
참조 p_a와 initial-state bytes 및 같은 K/Q의 binding이 확인돼야 실용적
pair claim으로 사용 가능하다. 현재 CLI의 입력 scalar는 conditional scenario
anchor이며 `reference_anchor_verified=false`다. 수치 interval은 IEEE 연산의
평가이며 roundoff enclosure가 없으므로 `roundoff_certified=false`다.
floating_pair_screen=true라도 자동으로 collision run을 생략하거나 GO로 바꾸지 않는다.

## 4. 이번에 실행한 reduced-grid 검사

격자 [-6.4,6.4]^3, h=.4 a0, 32^3 points. target potential만의 준비이다.
총 imaginary time 30 t_a에서:
τ=.05: residual .013638113049666804 Eh; E=-.4722685355745903 Eh
τ=.025: residual .003484664337248429 Eh; E=-.4722772270377254 Eh
τ=.0125: residual .0008762234053475998 Eh; E=-.4722777878621499 Eh
residual 감소비는 약 3.914 및 3.977이다.
τ=.025에서 총시간60으로 늘리면 residual=.003484655813983709 Eh;
T30/T60 phase-aligned distance=2.4774628757402934e-6.
step 감소에 따른 약4배 residual 감소 및 총시간 연장의 plateau는 이
유한 격자에서 split-step fixed-point bias 해석을 지지한다.

T30, τ=.025/.0125 초기 pair의 d=.00018211061811878535이다.
production p_a를 숫자 예시로만 넣으면 conditional upper relative change는
.0041393422861이다. 이 0.414%는 production-grid bound가 아니며,
reduced-box 상태를 production 상태 대신 사용할 수 없다.

같은 reduced fixture의 target-only 한 real step(no CAP) ray defect는
.00129564595, .00082509667, .00070447311이다. H residual 감소가
real-time split stationary error를 자동 제거하지 않는다는 점을 보여준다.
여기에 사용한 real dt_actual=.04980126639032258 t_a는 reduced trajectory
window로부터 계산된 값이다. production dt_actual과 혼합하지 않는다.

## 5. 코드와 보존 경계

새 스크립트는 scripts/ 아래에만 있다. cr_repro/*.py 12개는 현재 parent와
Git blob identity가 같고 source_digest도
581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b
그대로다. 기존 seal을 무효화하지 않는다.

prepare: 기존 relaxed_initial만 호출; final target E/residual 재평가;
no-CAP target-only ray defect와 CAP 생존 norm; immutable initial.npy/receipt.
준비 도중 resume는 구현하지 않았으며 실패는 fresh directory에서 재시도한다.
compare: source/config/state hash, 동일 grid와 total prep time 검증 후
phase-aligned distance와 conditional interval. dynamics.run()은 호출하지 않는다.
full suite, GPU parity, production-size initial preparation 및 새로운
collision results는 이번 검증 범위 밖이다.

## 6. scoped sibling 및 백업

HOST4 H12 보고서를 읽었다. 그 보고서는 P0 R24 direct619 node를 import했으나
midpoint interpolation counterexample과 numeric envelope gate를 여전히 남긴다.
CR preparation 수치나 tolerance로 가져오지 않았다.
HOST4 H13은 검색 시 CP0만 관측했으며 final로 import하지 않았다.

R3M12 large archive의 Drive multipart manifest는 1/19만 검증된 상태다.
본 R3M13의 작은 checkpoint 이중백업과 이 과거 1.23GB archive의 복구를
구분한다. 새 작은 ZIP의 성공이 과거 archive 완료를 뜻하지 않는다.

## 7. 다음 최소 물리 실행

기존 R3M12 지정대로 production dx=.25에서 두 준비를 각각 저장하고
residual/ray difference를 비교한다. 이어 새 .0125 x 2400 상태의 기존
ControlledTDLRunner collision을 fresh run directory에서 실행한다.
real dt=.05, CAP, box, b=2, E=100, nmax=3를 바꾸지 않는다.
archive probability와의 pair 비교 및 source-equivalence 확인 후 추가 공간
정련을 결정한다. b-grid NO_GO 및 AOCC radial/exponent OPEN은 유지한다.
