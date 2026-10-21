# C21L: non-tilted Bianchi I의 물리적 Σ–Π pilot과 정확한 재사용

작성일: 2026-10-21. 이 문서의 직접 기여는 PR147의 고정 Einstein–Boltzmann–Vlasov 계산을 실제 초기 텐서 노름 격자에 연결하고, 같은 계산을 반복하는 비용을 줄이는 것이다. 일반 삼축 계와 완전한 재이온화 피드백의 과학 채택은 기존 상태를 유지한다.

## 1. 실제 연구 위치와 새 결과의 적용 범위

최근 branch·다른 대화·반환물 조사는 별도 INTAKE 기록에 있다. bass_cr C21K의 exact opacity 재사용과 실행기는 이미 완료됐다. WU PHYS73 raw 반환의 검증, REC U4B의 실제 32 accepted step, HE의 완료된 canary와 빈 queue, BASS S12 새 반환 ZIP, VigilODE의 N01–N08 source 변경을 각각 확인했다. 이들은 서로 다른 물리적 입력과 source를 가진다. 이번 pilot의 실제 경로는 REI PR147의 collisionless LRS 계이며, 새 source를 적용하려면 그 계와의 대응이 필요하다. 완료된 원자·화학·ODE suite를 반복하지 않는다.

선택한 원본은 `rei_bianchi@3b85dedce84d37b3e165da00685a8a984950aafe`의 `CanonicalFVSpecies`이다. 이 선택은 최신 문서 시각으로 과학 모델을 바꾸지 않고, 이미 실행 가능한 자기중력·전단·복사·massive Vlasov 결합을 유지한다. 원본 source 파일과 초기 cosmology lock의 byte identity를 기록한다. 외부 문헌은 물리적 식과 수치 설계의 근거로 쓰고, 현재 모델을 새 모형으로 대체하는 근거로 쓰지 않는다.

## 2. 텐서, 부호, 단위

계량 부호는 (-,+,+,+)이며 proper time t를 사용한다. LRS Bianchi I에서

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
\quad H=\dot a/a,\quad s=\dot b.
\]

공간 정규직교 기저에서

\[
\sigma^i{}_j=\mathrm{diag}(-s,-s,2s),\qquad
\pi^i{}_j=\mathrm{diag}(-p,-p,2p),\quad
p=(P_\parallel-P_\perp)/3.
\]

따라서 직접 수축하면

\[
\sigma_{ab}\sigma^{ab}=6s^2,\quad
\pi_{ab}\pi^{ab}=6p^2,\quad
\sigma_{ab}\pi^{ab}=6sp.
\]

Wolfram Language에서 두 trace가 0이고 위 세 수축이 각각 6s², 6p², 6sp임을 확인했다. 이 검산은 대수적 정규화만 확인하며, 수치 적분이나 연속 오차 정리를 대신하지 않는다.

이번 산점도/격자에서 막대는 Frobenius norm으로 명시한다:

\[
S=\sqrt6\,s/H,\quad\Sigma_F=|S|,
\qquad P=\frac{8\pi G}{c^2}\frac{\sqrt6\,p}{H^2},\quad\Pi_F=|P|.
\]

H는 s⁻¹, p는 J m⁻³이다. κ₄=8πG/c⁴를 쓰면 같은 식은
Π_F=κ₄|π_ab|/(H/c)²이다. 시간 기준 H²에 κ₄만 곱해 c²를 빠뜨리지 않는다.
기존 REI `Sigma`는 sqrt(σ_ab σ^ab/2)/H이므로 Σ_F=√2 Σ_REI이다. 양쪽 관례의 열을 모두 보존한다. 스트레스에도 동일한 half-contraction convention을 사용할 경우 Π_half=Π_F/√2이다.

PR147의 `Pi_gamma_J_m3`, `Pi_nu_J_m3`, `Pi_matter_J_m3`는 각 성분의 **p=ΔP/3**다. 총 p를 먼저 합산하고 그 절댓값을 취한다. 성분별 norm의 합은 서로 상쇄되는 물리적 응력을 과대평가한다. older coupled branch의 `Pi=ΔP`와 이 필드를 혼용하면 3배 오차가 생긴다.

Σ,Π의 비음수 값 둘만으로 텐서의 상대 부호와 모든 형태를 결정할 수 없다. 이 pilot은 LRS 형태를 고정하고 sign(S₀), sign(P₀)의 네 branch를 따로 저장·그린다. 영점에서 부호는 0으로 보존하며 같은 영점 case를 여러 패널에서 표시할 때도 새 계산으로 세지 않는다.

## 3. Einstein 제약과 초기 격자의 구성

원본의 Hamiltonian constraint는 에너지 밀도 ε에 대해

\[
H^2=\frac{8\pi G}{3c^2}\epsilon+\frac{\Lambda c^2}{3}+s^2.
\]

따라서 Ω_m+Ω_r+Ω_Λ+Σ_F²/6=1이며, 양의 총 에너지와 Λ≥0의 expanding branch에서 Σ_F<√6이다. 이는 모든 물질모형의 Π를 자유롭게 지정해도 된다는 뜻은 아니다. 이번 Π 축은 실제 비음수 분포의 초기 quadrupole로 생성한다.

원본의 q=s_ref/H_FLRW,ref와 목표 S₀는

\[
S_0=\frac{\sqrt6q}{\sqrt{1+q^2}},\qquad
q=\frac{S_0}{\sqrt{6-S_0^2}}.
\]

source constructor에 Sigma_ref=|S₀|/√2, orientation=sign(S₀)를 넣고 원래 initial_state()를 호출한다. 이후 실제 fields()의 H₀를 사용해 다시 확인한다. 이론식만으로 실제 초기장 검사를 생략하지 않는다.

복사 성분의 초기 분포는 공통 k에 대해 W(μ)=1+kP₂(μ), gamma와 neutrino가 같은 k를 가지며 |k|≤0.5이다. massive 분포는 A=0, 질량/T_ref=30, 비바리온 물질 비율 f_m=0.1로 고정한다. 주어진 S₀에서 H₀와 총 에너지는 k에 의존하지 않고, 원본 초기 E₂=k/5이므로

\[
p_{r,0}=\rho_{\mathrm{crit},0}\frac{\Omega_r k}{15a_{ref}^4},
\qquad
P_0(k)=P_0(0)+B(S_0)k,
\]

\[
B(S_0)=\frac{\sqrt6\,H_{\mathrm{today}}^2\,\Omega_r}
{5a_{ref}^4 H_{ref,actual}^2}.
\]

여기서 표기의 혼동을 피하려고 코드에서는 source.h0(오늘 Hubble 상수)와 fields['H'](초기 실제 H)를 구별한다. 초기 massive quadrature의 작은 잔차도 같은 원본 fields에서 얻어 P₀(0)에 포함한다. 구현은 k=0과 k=0.5의 실제 초기 fields를 이용해

\[
k=\frac{P_{target}-P_0(0)}{2[P_0(0.5)-P_0(0)]}
\]

로 역변환한다. 추가 ODE나 root search가 필요 없다. 입력 domain, 기울기 유한성, |k|≤0.5, 실제 S/P와 목표의 일치를 확인하고 solver 결과를 목표 값으로 덮어쓰지 않는다.

고정 cosmology는 H_today=2.1842852410855026e-18 s⁻¹, Ω_m=0.315, Ω_r=9.2e-5, Ω_Λ=0.6849080000000001, a_ref=1/21, a_end=0.2다. 실제 초기장 조회에서 S₀=0, k=0.5의 P₀는 약 0.001492847087284673이다. 따라서 이번 |P₀|≤0.001, |S₀|≤0.04 격자는 source의 보수적 |k|≤0.5 범위 안에 들어간다. 각 case의 실제 mapping 검사로 이를 다시 확인한다.

## 4. 재사용할 물리 구조와 계산량

균질한 Bianchi I의 collisionless Vlasov 계에서는 공간 Killing 대칭으로 공변 운동량 q_i가 보존된다. 문헌의 f(t,p^i)=f₀(p_i)는 이 보존 변수를 사용하는 정확한 특성 표현이다. 원본 canonical finite-volume 구현은 양의 cell 수 N_cell을 고정하고 현재 metric으로 물리 운동량과 에너지를 계산한다:

\[
p_\perp/T_{ref}=q_\perp e^{-\eta+b},\quad
p_\parallel/T_{ref}=q_\parallel e^{-\eta-2b},\quad
E/T_{ref}=\sqrt{m_*^2+p_*^2}.
\]

\[
\rho\propto e^{-3\eta}\sum wE,\quad
P_\perp\propto e^{-3\eta}\sum w\frac{p_\perp^2}{2E},\quad
P_\parallel\propto e^{-3\eta}\sum w\frac{p_\parallel^2}{E}.
\]

이미 채택된 Gauss rule과 cell 합산 순서를 유지한다. 이 표현은 collisionless transport의 자유도를 없애지만 momentum quadrature의 이산화 오차까지 없애지는 않는다. scattering이나 finite collision이 추가되면 N_cell 불변성은 다시 검토해야 한다.

이번 grid에서는 source, L=8, canonical cell 해상도 24×12, Gauss3, 질량과 A=0가 모든 case에서 같다. 따라서 2개의 9×9 Legendre operator, Thomson 대각계수, 2,592개 quadrature packet과 cell population을 worker마다 한 번 만들 수 있다. case마다 다른 값은 S₀·k와 시간에 따라 적분하는 상태다.

K개 case와 W개 실제 worker에 대해 constructor의 operator 생성은 2K회에서 최대 2W회로, 같은 canonical grid 생성은 K회에서 최대 W회로 줄어든다. 이는 코드 구조에서 얻는 작업 수 감소이며 wall-time speedup 측정값이 아니다. 각 case는 독립적인 40성분 상태와 DOP853의 같은 rtol=3e-11, atol=3e-13을 사용한다.

hot moment 식의 동일한 `(r*q)**2` 두 번 계산은 한 번으로 공통화할 수 있다. `1-mu²`와 immutable cell population의 최솟값도 고정이다. `(r*q)**2`를 `r²*q²`로 바꾸거나 합산 순서를 바꾸지 않으므로 새 재결합 근사를 도입하지 않는다. 실제 bitwise parity로 구현을 확인한다.

동일 k와 collisionless gamma/nu에서는 같은 초기 normalized hierarchy가 같은 미분방정식을 따른다. 이를 이용한 상태 차원 축소는 별도의 후보로 남긴다. 상태 수를 줄이면 adaptive solver의 오차 norm도 변할 수 있어, 이번의 source-preserving 최적화에는 포함하지 않는다. 큰 Schur/backend 통합, JAX/Numba 신규 compilation, 기기별 fastmath도 오늘 pilot의 선행 조건이 아니다.

## 5. 병렬화와 가용 자원

독립 case를 process pool에 배분하므로 case 사이에 floating-point reduction을 추가하지 않는다. 각 worker의 NumPy·BLAS·OpenMP thread는 1이다. persistent worker는 원본 template를 재사용하고 case별 즉시 결과를 저장한다. 집계는 case ID 순서대로 수행한다.

자원 상한은 현재 affinity, cgroup quota, visible ancestor memory, MemAvailable, 공동 lease와 짧은 CPU 사용 관측으로 정한다. CPU55를 제외하고 coordinator를 포함한다. memory reserve는 max(1GiB, effective limit의12.5%), conservative worker 예산512MiB, coordinator256MiB다. 광고된 64코어/128GiB를 실제 할당이라고 가정하지 않는다. 다른 세션은 전역 중지 사유가 아니며 가용 부분에서 진행한다. 같은 lease 디렉터리를 쓰지 않는 작업까지 lease가 통제한다고 주장하지 않는다.

외부 작업이 도중에 자원을 더 소비할 수 있으므로 관측은 시점에 묶인다. timeout·실패·중단과 성공 결과를 보존하고, 완료된 case는 같은 source/input identity에서 재사용한다. 실패 case는 자동으로 다시 실행하지 않는다. NCP 자원은 이번 read-only 접속 조회가 응답하지 않아 아직 관측되지 않았다. 샌드박스 실행과 NCP 실행은 별도로 보고한다.

## 6. 판정 기준과 남는 오차

필수 검증은 텐서 정규화·응력 상쇄·입력 mapping, template의 case 독립성, 기존과 재사용 moment의 bitwise 비교, 대표 세 trajectory의 같은 source/solver 조건 비교, CPU55·quota·memory·lease 및 incremental 결과 동작이다. 새 81-case sweep은 이 물리적 초기조건 격자의 실제 preliminary 계산이며 benchmark가 아니다.

Hamiltonian constraint가 fields에서 대수적으로 구성된다는 사실을 고려한다. 작은 constraint residual은 구현의 내부 일치 확인이지 독립적인 전역 정확도 증명이 아니다. particle number와 cell positivity, 유한 출력, solver 성공 등도 각 검사의 범위대로 기록한다. angular truncation, momentum quadrature, ODE global error, 적용하지 않은 H/He·UV feedback의 오차를 한꺼번에 인증하지 않는다. `global_error_bound=null`, full production 및 기존 과학 HOLD를 유지한다.

## 7. 읽은 외부 근거

- J. M. Heinzle & C. Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG23(2006)3463, DOI10.1088/0264-9381/23/10/016; arXiv:gr-qc/0512031. Section2 Eqs.(2d–f),(3),(6–13): covariant momentum, stress moments, expansion normalization. 문헌은 자체 가정의 Vlasov 계를 다루며 이번 다성분·Λ·finite hierarchy의 모든 과학 주장을 자동 보증하지 않는다. SciSpace에서 정확한 제목/DOI를 확인하고 Exa로 MPG 원문 Section2를 읽었다.
- NumPy 공식 broadcasting 문서: C 레벨 array 연산과 불필요한 copy 회피, 큰 broadcast temporary의 메모리 비용. https://numpy.org/doc/stable/user/basics.broadcasting.html
- SciPy 공식 solve_ivp 문서: DOP853 고차 explicit 적분과 1-D state, vectorized 옵션의 의미. https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- Python 공식 concurrent.futures 문서: 독립 process 실행, initializer와 task dispatch. https://docs.python.org/3/library/concurrent.futures.html

새 외부 physics code를 무분별하게 가져오지 않고 현재 소유자의 source와 이미 사용하는 NumPy/SciPy를 재사용한다. SciSpace 첫 두 질의는 관련성이 낮은 논문도 반환했으므로 정확한 제목·저자·DOI 질의로 보완했다. WolframContext는 internal error였지만 실제 Wolfram Language 수축·변환 검산은 결과를 반환했다. 이들 도구의 검색/대수 확인과 실제 Python IVP 증거를 구분한다.
