# R4AK: 공진쌍의 균일 Gram과 gap-free weak bridge envelope

2026-10-03. 원자 데이터 생산 전용이다. Bianchi 배경·수송·재이온화 동역학은 rei_bianchi가 담당한다. 아래 유도는 저장된 유한 candidate 및 명시된 유한 행렬모델에 관한 것이며 실제 연속 18채널 산란 certificate와 구별한다. R4AJ의 rank/공진 판별과 과거 실패를 변경하지 않는다.

## 1. 두 종류의 결과와 단위

실제 candidate 결과는 저장 ground radial polynomial의 새로운 tail 적분 한 개를 이용한 두 중심 1s Gram의 연속 영역 상계다. 별도의 새 코드 결과는 정확히 정의한 polynomial S(t),K(t) 곡선 또는 그 곡선에 대한 명시적인 uniform operator remainder로부터 weak residual의 연속 상계를 반환하는 유한차원 provider다. 후자의 실제 BASS S,K 입력은 아직 없다.

좌표 단위는 a0, 에너지는 Eh, 시간은 ta=ħ/Eh이고 저장 v=2.00798106651023 a0/ta는 정확한 이진 유리수로 읽는다. 식에는 ħ를 유지하며 코드 인자 hbar는 Eh·ta 단위의 수치값을 갖는다. 내적은 첫 인수에 반선형이다. metric(-,+,+,+)는 국소 비상대론 전자 충돌 적분에서 사용되지 않는다.

## 2. 실제 finite candidate의 uniform pair Gram

동일 ground s orbital φ=u(r)Y00/r를 각 중심에 놓고 projectile에는 단위 절댓값의 ETF를 곱한다. R4AB의 exact rational Gram과 kinetic moment에서

g=∫0^64 |u|²dr, T=∫0^64 |u'|²dr

를 바이트 동일한 입력으로 재사용한다. 이를 새로 적분하지 않았다. 이번에는 a=6a0에 대해 τ(a)=∫a^64 |u|²dr만 exact rational로 새로 적분했다. 패널 표현은 u=(1-s)L+sR+s(1-s)(q0+q1s+q2s²)이고, s∈[0,1]. 부분 패널도 잘라 정확히 적분하며 tail을 버리거나 함수의 접합을 smoothing하지 않는다.

중심 거리 R≥2a이면 반경 a의 두 ball은 내부가 겹치지 않는다. target ball Ω와 그 여집합으로 overlap을 분할하면

|s_TP|≤||φ_T||Ω||φ_P||Ω+||φ_T||Ωc||φ_P||Ωc≤2√(gτ).

ETF는 절댓값이 1이므로 이 부등식에 추가 phase 가정은 없다. G_R=[[g,s_TP],[s_TP*,g]]의 두 고유값은 g±|s_TP|이므로

λmin(G_R)≥g−2√(gτ), λmax(G_R)≤g+2√(gτ).

b=2a0, |z|≥12a0에서는 R=√(b²+z²)≥12a0=2a이므로 같은 상계가 전체 영역에 성립한다. 이는 여러 z점의 fit이나 quadrature 차이에서 만든 상계가 아니다. 정수 제곱근으로 √(gτ)를 위쪽 유리수로 감쌌다.

관측된 표시값: τ(6)=0.0005222575618014674, g=0.9999999999999921, |s_TP|≤0.04570591041873964. 안전하게 바깥쪽으로 표시하면 λmin≥0.954294089581, λmax≤1.045705910419, cond2≤1.095789989518이다. 정본은 PAIR_UNIFORM_BOUND.json의 유리수다. 이는 pair의 physical-inner-product conditioning이지 full18 Gram positivity나 physical spectral gap이 아니다.

## 3. H1 weak form에서 얻은 거친 실제 pair operator 상계

s orbital의 연속 u와 0 및64a0의 zero endpoint는 zero extension의 H1 적합성을 준다. ∫|∇φ|²d³x=T이며 radial symmetry로 ∫|∂zφ|²=T/3이다. 이때 부분적분의 endpoint 항 [u²/r]은 0이다. 패널별 derivative jump는 존재해도 H1에 필요한 일차 약도함수 norm은 정의된다. strong Hφ∈L2를 가정하지 않는다.

원자 단위에서 ETF가 exp(iv xz−iv²t/2)이므로 합성사상 F=(χ_T,χ_P)의 Frobenius형 operator 상계는

||F||²≤2g, ||∇F||²≤2T+v²g=:Ggrad,
||Fdot||²≤v²T/3+v⁴g/4=:Gtime.

실수 radial 함수이므로 gradient·phase 항의 교차 실수부분은 0이다. SI에서는 ETF k=me vphys/ħ, 시간 phase ν=me vphys²/(2ħ)를 사용해 Ggrad=2T+k²g, Gtime=vphys²T/3+ν²g로 복원한다.

3차원 Hardy 부등식 ||ψ/r||≤2||∇ψ||는 ∇·(x/r²)=1/r²를 부분적분한 후 Cauchy–Schwarz를 적용해 얻는다: ∫|ψ|²/r²=−2 Re∫ψ* (x/r²)·∇ψ≤2||ψ/r||||∇ψ||. 매끄러운 compact 함수에서 유도한 뒤 H1으로 닫는다. 어느 중심으로 옮겨도 같은 부등식이다.

따라서 두 charge=1 Coulomb 핵의 weak 행렬은, 단위값 ħ²/(2me)=1/2와 e²/(4πε0)=1을 해당 a0/Eh 규약으로 사용하면

||H_R||≤Ggrad/2+4√(2g Ggrad),
||D_R||≤√(2g Gtime),
||K_R||≤||H_R||+ħ||D_R||, K=H−iħD.

SI potential 항은 2(|κ_T|+|κ_P|)||∇F||||F||이고 κ=e²Z/(4πε0)[energy·length]다. 계산된 거친 bound는 H_R≤16.909287852116Eh, D_R≤3.288838007067/ta, K_R≤20.198125859182Eh. 이는 정의가능성과 크기의 보수적 상계이지 목표5e−6를 만족하는 작은 bridge 오차가 아니다. pair-rest coupling·full metric이 빠졌으므로 physical_bridge_upper는 null이다.

## 4. Whitening 없이 공진쌍을 남긴 weak residual

정확한 유한 coefficient 모델 iħSċ=Kc, S=S†>0를 가정한다. S∈C1이고 K는 연속이며 모든 ETF와 움직이는 기저 연결항은 K=H−iħD에 포함한다. 수치 S/K를 강제 Hermitian화하지 않는다. 실제 기저가 움직이더라도 현재 채널 선택 injection J는 coefficient 좌표에서 상수다. J는 T1s/P1s 두 열을 선택하며 한 상태씩 따로 정규화한 projector를 더하지 않는다.

G=J†SJ, K_R=J†KJ, iħG d_dot=K_R d,
L=−iS^−1K/ħ, A=−iG^−1K_R/ħ.

approximation c_a=Jd의 잔차는

R=LJ−JA=−iS^−1 B/ħ,
B=KJ−SJ G^−1K_R, J†B=0.

J†B=0은 시험공간에 대한 Galerkin 직교성이다. B가 0이거나 물리적 leakage가 없다는 뜻은 아니다. operator norm으로

||R G^−1/2||_S=||S^−1/2 B G^−1/2||/ħ
≤||B||F/(ħ√(s_min g_min)).

이 상계에는 spectrum gap, Kdot 또는 whitening Mdot가 필요하지 않다. 따라서 1s partner를 제거하려고 가짜 gap을 도입할 이유가 없다. 공진쌍 내부 K_R의 전이는 그대로 남고, 외부공간을 제거하는 오차만 residual로 통제한다. gap이 실제로 증명되면 R4AJ의 oscillatory bound를 더 날카로운 선택지로 사용 가능하지만, 기본 타당성의 필수조건은 아니다.

J(t)를 바꾸면 추가 −Jdot가 residual에 들어가고 reduced weak generator도 J†KJ−iħJ†SJdot로 달라진다. 현재 provider는 constant coordinate selector만 지원한다. 시간가변 eigenvector selector를 고정 J인 것처럼 넣으면 안 된다.

## 5. Metric defect와 상태 오차

Γ=Sdot+(i/ħ)(K†−K), Γ_R=Gdot+(i/ħ)(K_R†−K_R)=J†ΓJ.

||c||²_S의 시간미분은 c†Γc이다. h의 Hermitian part만 취해 Γ를 숨기지 않는다. a_f≥||Γ||/(2s_min), a_r≥||Γ_R||/(2g_min), r≥||B||F/(ħ√(s_min g_min))가 같은 시간 slab에 성립하면 E=||c−Jd||S, N=||d||G에 대해

E_dot≤a_f E+rN, N_dot≤a_r N.

시간길이 Δ에서 직접 적분하여

E_out≤e^(a_fΔ)E_in+rΔ e^(max(a_f,a_r)Δ)N_in,
N_out≤e^(a_rΔ)N_in.

둘의 exponent가 같은 경우까지 연속인 보수적 상계다. exp_upper는 x∈[0,32]에서 양의 유리수 Taylor 급수와 기하급수 tail을 사용하고 큰 x를 나누어 계산한다. 해당 범위를 넘으면 overflow나 근사0이 아니라 명시적으로 거절한다. 동일한 S-직교 projector에 대한 quadratic observable 차이는 E(2N+E) 이하이고, projector 자체·초기상태·모델을 바꾸면 각 비교항을 더해야 한다.

이 식은 기존 R4AI의 norm transfer 아이디어를 구체적인 pair Galerkin residual provider에 연결한 것이다. 새로운 보편 theorem으로 포장하지 않는다.

## 6. 정확한 polynomial tube: 상쇄를 먼저 수행한다

입력 S(t),K(t)는 power coefficients가 정확한 복소 유리수인 다항식 모델이다. sampled fit이 참 원자 연산자와 같다고 가정하지 않는다. 두 상태 G에 대해 inverse 분모를 기호적으로 모으고

N_B=(detG)KJ−SJ adj(G)K_R

를 정확한 polynomial로 먼저 구성한다. J†N_B=0을 대수적으로 확인한 뒤 전체 slab의 Bernstein coefficient hull로 각 실수/허수 성분을 감싼다. Gershgorin으로 S,G의 연속 양의 하한을 확인하고 detG≥g_min²도 사용한다. 그 후에만 ||B||≤||N_B||/(detG)_min를 계산한다. KJ와 SJG^−1K_R를 따로 큰 범위로 평가해 이미 알려진 cancellation을 잃지 않는다.

Bernstein의 convex-hull 성질은 b_k C(n,k)x^k(1−x)^(n−k)의 basis가 [0,1]에서 비음수이고 합이1이라는 사실로 직접 따른다. 여러 표본의 최솟값을 사용하지 않는다. Γ와 측정률의 numerator도 같은 방식으로 symbolically cancel한다.

공통 실수 scalar c(t)S를 K에 더하면 N_B, Γ 및 observable rate에서 scalar gauge가 정확히 소거된다. 새로운 unitary 시간 frame을 적용하는 경우에는 connection을 먼저 포함해야 하며 scalar-cancellation만으로 일반 frame 불변성을 주장하지 않는다.

## 7. 실제 operator remainder를 붙이는 조건부 경로

정확 polynomial 모델을 S_p,K_p라 하고 같은 연속 실제 모델에 대해 ||S−S_p||≤εS, ||K−K_p||≤εK, ||Sdot−S_pdot||≤εSd가 전 slab에서 이미 정당화된 상계라고 가정한다. s=s_p−εS>0, g=g_p−εS>0이어야 한다. 두 inverse의 resolvent identity를 이용하면

δB≤εK+εS (||K_Rp||+εK)/g
 +||S_pJ||[εS (||K_Rp||+εK)/(g g_p)+εK/g_p].

이를 B_p 상계에 더해 실제 metric 하한으로 나눈다. Γ의 오차는 εSd+2εK/ħ 이하다. 이 경로는 ASSUMED_UNIFORM_OPERATOR_REMAINDERS로 표시한다. source hash가 있거나 caller가 asserted label을 붙였다는 이유만으로 실제 상계를 증명한 것이 아니다. 단일점·quadrature 차수차·fit RMS와 같은 입력은 거절한다. 실제 operator 측정률의 remainder는 이 provider에서 미구현이므로 null로 남긴다.

## 8. 측정은 여전히 projectile 1s

nonorthogonal pair의 두 번째 column이 P1s이면 reduced quadratic observable은 d†O d,

O=G[:,p]G[p,:]/Gpp

이다. 이것을 |d_p|² 또는 pair 총노름으로 바꾸지 않는다. exact polynomial 모델에서

Pdot=d†F_O d, F_O=Odot+A†O+OA.

p=Gpp, Tm=G[:,p]G[p,:], A_num=−i adjG K_R/ħ라 하면

N_O=(detG)(p Tm_dot−p_dot Tm)+p(A_num†Tm+Tm A_num),
F_O=N_O/[(detG)p²].

따라서 ||F_O||/g_min로 내부 실제 측정 변화율을 제한한다. 내부전이의 크기는 approximation error가 아니므로 두 수치를 분리해서 낸다. 시간0, decoupled invariant pair, pure scalar phase와 constant nonorthogonal metric 극한을 새 시험으로 확인했다.

## 9. 실제 실행 및 아직 열려 있는 항목

새 실제 candidate 연산은 τ(6)의 exact tail 한 개다. 원 G,T·중앙점·M9·기존 R8·D 원시배열·Vother·shifted 적분·과거 suite를 실행하지 않았다. 새 synthetic 3차원 모델은 M=I+(t/100)E20, h=[[0,1/4,0],[1/4,0,1/1000],[0,1/1000,2]], S=M†M, K=M†hM−iM†Mdot, t∈[0,1]이다. 네 slab에서 exact Γ=0이며 state bound≤0.016515177776, independent floating diagnostic max≈0.009777157947이다. reduced ODE norm drift≈1.94e−12로 사전1e−9 기준 안이다. 실제 atomic scattering trajectory가 아니다.

Actual bridge를 닫으려면 동일 candidate·시간영역의 full18 S,K,Sdot tube, full Gram 양의 하한, uniform operator remainders, 같은 endpoint의 초기상태·selector/embedding 오차와 목표 배분이 필요하다. Pair Gram 하한은 full18 하한을 대신하지 않는다. K_R의20.2Eh 거친 상계로5e−6 bridge 목표를 통과했다고 말하지 않는다. 실제 physical_bridge_upper 및 두 stencil total은 null이다.

## 10. 원전과 근거 구분

[PROJECT] R4AJ DERIVATION_KO.md, ATOMIC_ONLY_DAG, R4AB exact G/T, R4AG candidate bytes. 해당 source/input identity는 실행계약에 고정했다.
[PRIMARY_MOVING_BASIS] Artacho–O'Regan, arXiv:1608.05300v2, Phys.Rev.B95,115155(2017), https://arxiv.org/abs/1608.05300 . 이번 조회는 identity/abstract와 추가 connection의 일반 근거다.
[PRIMARY_ACTION] Burgarth et al., arXiv:2111.08961v2, Quantum6,737(2022), https://arxiv.org/abs/2111.08961 . integral-action 경로의 일반 근거이며 이번 gap-free residual을 논문의 미확인 특정 정리로 인용하지 않는다.
위 Hardy/Cauchy·잔차·Bernstein·remainder·측정률 식은 이 문서에 직접 유도했다. 정확 유리수 산술과 코드 시험은 proof-assistant 검증이나 실제 원자모델 오차의 해결과 다르다.
