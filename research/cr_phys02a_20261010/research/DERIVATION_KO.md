# CR-PHYS02A — 직접 생성된 저에너지 전자의 인과적 Coulomb 침적

## 1. 문제와 증거 범위

기준은 `cosmosapjw-quantum/bass_cr`의 PHYS01 commit
`e41e18873af438ef989ff44f505fe2665118fdec`이다. 이 단계는 1–4 MeV 양성자의
H/He impact ionization을 FS10 terminal electron yields와 합성했으나, 그 표를
317년 turn-on의 실제 침적 이력으로 승인하지 않았다. 본 작업은 그 제한을
그대로 보존하며 CR-PHYS02-DELAY의 첫 물리 하위문제를 계산한다.

FS10 §2, §6.1은 전자의 최종 energy fractions와 순간 침적 가정을 구분한다.
특히 §4의 helium excitation photons는 원 모형 내부에서 재흡수된다. 따라서
표의 최종 counts/heat만으로 전자와 광자의 시간별 재고를 복원할 수 없다.
이 진술의 근거는 원문이며, 아래 인과적 응답식은 직접 유도이다.

본 계산은 **양성자 충돌에서 직접 태어난 0.1–10 eV 전자**만을 대상으로 한다.
10 eV 위 전자가 cascade 도중 이 구간에 진입하는 flux는 아직 계산하지 않았다.
이 선택은 전체 에너지 스펙트럼의 재정규화가 아니라 출처를 유지한 부분적분이다.

## 2. Terminal yield만으로 지연을 식별할 수 없는 이유 — derived

고정된 가스 상태에서 에너지 W인 전자가 탄생한 뒤 age a에 채널 c로 전달하는
평균 응답을 k_c(a,W)라고 하자. 에너지 채널이면 단위는 전자당 eV/s,
이온화 횟수 채널이면 전자당 1/s이다. 인과성은 a<0에서 k_c=0을 요구한다.

\[
Y_c(W)=\int_0^\infty k_c(a,W)\,da,
\qquad
P_c(t)=\int dW\int_0^t Q_e(W,t-a)k_c(a,W)\,da.
\]

FS10 표가 주는 것은 Y_c이다. 임의의 양수 λ에 대해

\[
k_{c,\lambda}(a,W)=\lambda k_c(\lambda a,W)
\]

는 같은 Y_c를 가지지만, 첫 시간 모멘트는 1/λ배가 된다. 그러므로 표의 에너지
보존이나 terminal convergence를 확인해도 지연은 결정되지 않는다. 실제 시간
정보를 얻으려면 absolute collision rates, energy drift, branching과 photon
propagation을 따로 제공해야 한다. 임의의 exponential lag를 붙이는 것은 이
식별 불가능성을 해소하지 못한다.

초기 source가 ramp인 Q_e(W,t)=A(W)t Θ(t)이고 k_c≥0라면

\[
P_c^{\rm term}(t)-P_c(t)
=\int dW\,A(W)\int_0^\infty\min(a,t)k_c(a,W)\,da\ge0.
\tag{1}
\]

첫 모멘트 M_c=∫a k_c da가 유한하면 절대 오차는 ∫A M_c dW 이하이다.
충분히 늦은 시간의 상대 오차는 source-weighted mean delay/t로 제한된다.
이 식은 시간 kernel이 실제로 주어졌을 때만 적용할 수 있으며, terminal 표만으로
M_c를 채울 수는 없다. 또한 식 (1)은 고정된 상태와 동일한 source normalization을
전제한다. 상태가 변하는 전체 IGM에 그대로 적용한 오차 보장은 아니다.

## 3. 실제 CR source의 초기 시간 의존성 — derived

PHYS01의 가스 밀도와 원 source를 유지한다.

\[
n_H=140\ {\rm m^{-3}},\qquad
n_{He}=n_H\frac{0.248}{4(1-0.248)},\qquad
n_e=0.01(n_H+n_{He})=1.5154255319\ {\rm m^{-3}}.
\]

source는 Leite17 momentum power law와 MD14 SFRD의 기존 결합이며,
10 keV–1 PeV 전체 구간에서 정규화한다. 국소 초기 전개에서

\[
\mathcal N_p(K,t)=t q_p(K)+O(Ht^2q_p),
\qquad
Q_e(W,t)=t A(W),
\]

\[
A(W)=\sum_{s=H,He}n_{s,0}\int_{1\,{\rm MeV}}^{4\,{\rm MeV}}
q_p(K)v_p(K)\frac{d\sigma_{p,s}}{dW}\,dK.
\tag{2}
\]

여기서 n_s,0는 각 neutral target density이다. 기존 Rudd SDCS에서 선택한
W≤10 eV는 모든 active proton node의 ejection endpoint보다 낮다. 따라서

\[
A(W)=\sum_s\frac{C_{1s}+C_{2s}W/I_s}{(1+W/I_s)^3}
\]

로 계수 적분을 분리할 수 있다. 분모의 shape나 전체 source normalization은
바꾸지 않았다. `DirectElectronSource`의 계수법을 원 SDCS의 독립 adaptive
적분과 비교한다. 양성자 생성 age와 전자 생성 age는 서로 다르다.

원 Bianchi-I에서 H=3.3×10^-17 s^-1, s=3.3×10^-18 s^-1이고 Δt=10^10 s이다.
HΔt=3.3×10^-7, max(2H_ray Δt)=7.92×10^-7이다. 현재 응답은 이 작은
팽창량의 leading local term이다. 기존 정확한 양성자 characteristic을 세 시점에서
읽어 계수 차이를 수치 비교하며, 이 표본 비교를 연속구간 인증으로 부르지 않는다.
전자 방향 분포나 signed adiabatic work를 열로 바꾸어 채우지 않는다.

## 4. 선택한 stopping closure와 유효범위 — literature-supported, conditional

에너지를 물리량 ℰ(J)로 쓰고, κ=e²/(4π ε₀), v=√(2ℰ/m_e)라 하자.
Khrapak (2020), Eq. (6)의 고전적 superthermal weak-collisionality stopping과
FS10 Eq. (5)의 에너지율 계수를 사용한다.

\[
\omega_p=\sqrt{\frac{n_e e^2}{\epsilon_0m_e}},\qquad
\rho_0=\frac{\kappa}{\mathcal E},\qquad
\mathcal L_{\rm cl}=\ln\frac{v}{\omega_p\rho_0},
\]
\[
-\frac{d\mathcal E}{dt}
=\frac{4\pi\kappa^2 n_e}{m_e v}\mathcal L_{\rm cl}>0.
\tag{3}
\]

ρ₀에는 동종 전자의 reduced mass m_e/2가 반영되어 있다. 원문 Eq. (11)의
momentum-drag 8π를 에너지율에 그대로 가져오지 않는다. 정지한 동종 target의
이체 산란에서는 ΔE=(v/2)Δp_parallel이므로 해당 계수는 에너지율에서 4π가 된다.

이 closure는 고정된 bath, 비상대론적 superthermal 전자, 큰 Coulomb log,
ν_neutral<ω_p, 약한 결합, 고전적 cutoff를 전제한다. 원 논문은 감속으로
induced force 자체가 바뀌는 효과를 생략한다. 이 조건을 실제 IGM의 모든
산란과 열화에 대한 정밀 오차 보장으로 승격하지 않는다.

특히 선택한 상단 10 eV에서 κ/(ℏv)≈1.17이므로 classical/quantum separation은
강하지 않다. 하단 0.1 eV에서 ℰ/(k_B T)≈11.6이며 near-thermal kinetic closure도
완결되지 않았다. 따라서 0.1 eV를 thermalization 완료점으로 부르지 않고,
통과한 입자 수와 남은 kinetic energy를 별도 cutoff reservoir에 보존한다.
electron-neutral elastic energy transfer, electron-ion exchange, energy diffusion,
magnetization, thermal bath의 실제 변화는 이 연구에서 제외된다.

FS10 Eq. (12)는 E>13.7 eV 조건이 명시되어 있으므로 본 구간에 외삽하지 않는다.
또한 FS10 arXiv v1의 compact ζ_e 줄은 밀도 제곱근이 빠져 explicit plasma-frequency
표현과 불일치한다. 본 연구는 그 축약 숫자를 사용하지 않는다. 이 인쇄상의 문제로
원 Monte Carlo나 저장된 FS10 표까지 오류라고 판정하지 않는다.

## 5. 감속 시계와 정확한 인과적 응답 — derived

χ=1 eV를 joule로 나타낸 상수, w=ℰ/χ를 코드의 eV 수치라고 하자. 식 (3)은

\[
-\dot w=b(w)=\mathcal A\frac{\ln(Bw^{3/2})}{\sqrt w},
\quad
\mathcal A=\frac{4\pi\kappa^2n_e}{\sqrt{2m_e}\,\chi^{3/2}},
\quad
B=\frac{\sqrt{2/m_e}\,\chi^{3/2}}{\kappa\omega_p}.
\]

로그의 인수는 무차원이고 b의 수치는 eV/s에 해당한다. w_c=0.1에서 시계를 0으로 잡으면

\[
T(w)=\int_{w_c}^w\frac{du}{b(u)}
=\frac{2}{3\mathcal A B}
\left[\operatorname{Ei}(\ln(Bw^{3/2}))
-\operatorname{Ei}(\ln(Bw_c^{3/2}))\right].
\tag{4}
\]

미분하면 T'=1/b이므로 차원은 시간이고 T는 증가한다. 초기 에너지 w₀인 전자의
cutoff 도달 시간은 τ₀=T(w₀), age a에서의 에너지는

\[
w(a;w_0)=T^{-1}(T(w_0)-a)\quad(0\le a<\tau_0)
\]

이며 그 이후에는 cutoff ledger에서 w_c를 보존한다. 이는 이미 열이 되었다는
뜻이 아니라 미완결 저에너지 영역으로 넘긴 에너지의 추적 규칙이다.

u_*=max(0,T(w₀)-t), w_*=T^-1(u_*)를 두자. source coefficient A(w₀)를
잠시 바깥에 두면, 현재 stopping power와 누적 stopping heat는

\[
\frac{P_{\rm stop}(t;w_0)}{A(w_0)}
=\int_{w_*}^{w_0}[t-T(w_0)+T(w)]\,dw,
\tag{5}
\]
\[
\frac{H_{\rm stop}(t;w_0)}{A(w_0)}
=\frac12\int_{w_*}^{w_0}[t-T(w_0)+T(w)]^2\,dw.
\tag{6}
\]

식 (5)는 ∫₀^min(t,τ₀)(t-a)b(w(a))da에서 b da=-dw를 적용한 것이다.
식 (6)은 source birth time을 한 번 더 적분한 결과이며, 시간 미분하면 식 (5)를
복원한다. 따라서 현재 power×t를 누적 heat로 사용하지 않는다.

cutoff 입자 수와 잔류 에너지는 각각

\[
N_c/A=\tfrac12(t-\tau_0)_+^2,\quad
U_c/A=w_c N_c/A,\quad
\dot U_c/A=w_c(t-\tau_0)_+.
\tag{7}
\]

선택된 source의 총 주입 에너지는 U_inj/A=w₀t²/2이다. 남은 active 전자의
에너지 U_act와 다음 식이 성립한다.

\[
U_{\rm inj}=H_{\rm stop}+U_{\rm act}+U_c.
\tag{8}
\]

전자당 식에 실제 A(W)를 곱하여 W=0.1–10 eV에서 적분하고 χ를 한 번 곱하면
SI의 J m^-3 또는 J m^-3 s^-1이 된다. source와 bath를 0부터 변화시키는 전체
coupled plasma solution을 계산한 것으로 해석하지 않는다.

## 6. 극한과 검증 계약

t=0 또는 source OFF이면 모든 selected observable이 정확히 0이다.
t≪τ₀에서는 P_stop/A≈b(w₀)t²/2, H_stop/A≈b(w₀)t³/6이므로 양성자 turn-on 후
terminal proxy의 P_term∝t와 초기 차수가 다르다. 모든 입자가 cutoff에 도달할
수 있는 늦은 시간에는 stopping yield가 w₀-w_c이며 남은 w_c는 여전히 cutoff
ledger의 몫이다. 이를 terminal total-heat yield w₀와 혼동하지 않는다.

실제 신규 검증은 Ei primitive 대 adaptive 에너지 적분, 직접 forward ODE 대
에너지좌표 응답, 원 SDCS 직접 적분 대 계수 분리, 64/96 quadrature 비교,
positive energy ledger, zero/OFF, domain rejection이다. 동일 source·closure를
공유하므로 독립 수치 경로의 일치는 물리 모형 자체의 외부 검증이 아니다.
정량 수치와 실행 identity는 `evidence/NUMERICAL_RESULT.json`이 기준이다.

## 7. 다음 물리 연결

완전한 PHYS02에는 W>10 eV 전자의 impact ionization/excitation·Coulomb
에너지 수송, 새 secondary-electron branching, 위 구간에서 본 저에너지 구간으로
들어오는 flux, helium excitation photon propagation과 near-thermal matching이
필요하다. 전자와 재흡수 전 광자에 저장된 에너지는 gas heat와 별도여야 한다.
또한 생성 즉시의 free charge와 thermal electron number는 같지 않으므로,
delayed receiver는 suprathermal electron number/energy를 thermal pressure에서
분리해야 한다. PHYS01의 한 점 terminal receiver를 이런 상태로 묵시적 일반화하지 않는다.

고정 상태의 안정한 transient generator G와 채널 출력 d_c가 구축되면
Y_c=d_c^T(-G)^-1s, M_c=d_c^T(-G)^-2s로 terminal yield와 첫 시간 모멘트를
같은 물리 연산자에서 계산할 수 있다. 이것이 표에 임의 lag를 붙이는 대신 실제
quasistatic criterion을 얻는 다음 계산이다. 이번에 해당 G나 전체 IGM 이력을
구현했다고 주장하지 않는다.

## 원문

1. Furlanetto & Stoever, *Secondary ionization and heating by fast electrons*,
   MNRAS 404, 1869–1878 (2010), arXiv:0910.4410v1, §§2–6, Eqs. (5), (8)–(12).
   https://arxiv.org/html/0910.4410v1
2. Khrapak, *Reduction of the Coulomb logarithm due to electron-neutral collisions*,
   arXiv:2006.00128v1 (2020), pp.1–3, especially Eq. (6), cutoff definition and conditions.
   https://arxiv.org/pdf/2006.00128
3. PHYS01 source and normalization are inherited from the exact source-pinned local
   modules listed in `inputs/PARENT_SOURCE_MANIFEST.json`; their completed validation
   is not repeated or promoted to a causal result.
