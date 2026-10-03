# R4AI: Bianchi 재이온화 목적의 국소 이론·reference 구현

2026-10-03. 원자 산란의 새 물리 결과가 아니라, 현재 원자 source 이후의 계산과 검증에 필요한 분리된 이론/참조 구현이다. 원본 R4Z–R4AH의 계산·시험·승인·실패를 변경하지 않는다. 수식의 논리적 조건을 실제 입력값의 인증과 구분한다.

## 1. 오차를 갖는 이동 비직교 기저

내적은 첫 인수에 반선형이고 S=S†>0, S∈C¹이다. iℏS ċ=(H−iℏD)c, L=−iS⁻¹H/ℏ−S⁻¹D를 정의한다. 실제 이산 연산자는 exact metric compatibility를 자동 만족하지 않으므로

Γ=Ṡ+L†S+SL=Ṡ−D−D†+(i/ℏ)(H†−H)

를 남긴다. ||c||²_S=c†Sc를 미분하면 d||c||²_S/dt=c†Γc다. κ≥||S⁻¹/²ΓS⁻¹/²||₂이면 노름의 성장률은 κ/2로 제한된다.

근사 곡선 ĉ의 동일 coefficient model 잔차를 r=ċ̂−Lĉ라 두면 e=c−ĉ는 ė=Le−r이며

d||e||_S/dt ≤ κ||e||_S/2 + ||r||_S.

따라서 각 구간 길이 Δt에서 κ≤κ̄, ||r||_S≤ρ̄가 **구간 전체에** 성립하면

E_out ≤ exp(x) E_in + ρ̄ Δt (exp(x)−1)/x, x=κ̄Δt/2,

x=0에서는 E_out≤E_in+ρ̄Δt다. core.state_error_bound는 exp의 양의 Taylor 급수와 기하급수 tail을 유리수로 계산한다. 양의 projector P의 probability 오차는 정확한 공통 orthogonal projector인 경우 |P[c]−P[ĉ]|≤E(2||ĉ||_S+E)다. projector 자체가 바뀌면 그 차이에 의한 별도 link가 필요하다.

S≥s_min I 및 동일기저의 연속 operator 오류 ||ΔS||≤εS, ||ΔH||≤εH, ||ΔD||≤εD가 있으면,

||r||_S ≤ {εS||ċ̂|| + (εH/ℏ+εD)||ĉ|| + ||Ŝċ̂+(iĤ/ℏ+D̂)ĉ||}/√s_min.

core.coefficient_residual_upper가 이 조건부 입력 합성을 구현한다. 이것은 두 모델을 비교하는 기존 G11의 시간의존 T/embedding 정리를 대체하지 않는, 동일기저의 특수형이다. **기존 REGULARITY_AND_DYNAMICS_TRANSFER.md의 정리를 재사용한 구현이며 새로운 일반 정리라고 주장하지 않는다.** 상이한 기저에서는 −Ṫ와 물리 synthesis-map 오차를 유지해야 한다. metric.metric_defect는 Cholesky 좌표의 작은 행렬 진단일 뿐 time enclosure가 아니다.

점별 matrix residual이나 scipy ODE tolerance는 위 연속 입력 상계를 제공하지 않는다. strong Hφ∈L²가 성립하지 않는 패널 기저에 strong residual을 대입하지 않는다. ℏ[energy·time], H[energy], D[time⁻¹], κ[time⁻¹], ρ[norm/time]이며 E는 norm이다.

## 2. Bridge의 진동상쇄를 쓰려면 무엇이 필요한가

A(t)가 행렬 C¹ 함수, φ(t)가 실수 C²이고 전 구간에서 |φ′|≥ω>0일 때

∫ A e^(iφ)dt = [A e^(iφ)/(iφ′)] − ∫ e^(iφ){A′/(iφ′)−A φ″/(i(φ′)²)}dt.

삼각부등식으로

||∫ A e^(iφ)dt|| ≤ (||A(a)||+||A(b)||)/ω + Δt [sup||A′||/ω+sup||A||sup|φ″|/ω²].

closure.oscillatory_integral_bound는 이식을 정확 유리수로 계산하고 ω=0을 거절한다. stationary point, degenerate block, gap crossing을 무시하지 않는다. propagator 또는 projector가 amplitude에 들어 있다면 그 도함수도 A′에 포함한다. 이 식은 norm을 취하기 전에 상쇄를 유지하는 최소 판별식이며 실제 G04/G05의 A,φ,ω 및 연속 상계를 아직 생성하지 않았다. 과거 raw bridge≈504.54 및 target5×10⁻⁶은 바꾸지 않는다. 일반적인 integral-action 접근의 문헌 경로는 Burgarth et al. arXiv:2111.08961v2다. 여기에서는 위 부분적분식을 직접 유도했으며 논문의 일반 theorem을 새 candidate에 무조건 적용한 것은 아니다.

## 3. H5 radial 측도와 warm-target 축약

회수한 H5 보고서의 정의는 G(p)=∫p² f(p,Ω)dΩ=C p⁻²이며 ∫G(p)dp=n_CR다. 따라서 normalized projectile law는 G/n_CR이다. p² 또는 n_CR를 다시 곱하면 이중계수다. 원 state bytes를 복구한 것이 아니라 **보고서에서 확인한 의미론**이다. spectrum.powerlaw_p_minus2_weights는

w_i=(p_i⁻¹−p_(i+1)⁻¹)/(p_min⁻¹−p_max⁻¹)

를 exact 계산한다. w_i 합=1은 rate quadrature의 정확도를 의미하지 않는다.

국소 gas tetrad, proper time, NR 상대속도 g=|v−w|, E_CM=μg²/2를 쓴다. μ=m_p m_H/(m_p+m_H), s²=k_BT/m_H. 정지한 등방 Maxwell target에 대한 각도 적분으로, a=V/s, y=g/s에 대해

p(y|a)=y[exp(−(y−a)²/2)−exp(−(y+a)²/2)]/(√(2π)a), a>0,
p(y|0)=√(2/π)y² exp(−y²/2).

이는 ∫pdy=1, E[y²]=a²+3을 만족한다. 평균은

E[y]=√(2/π)exp(−a²/2)+(a+1/a)erf(a/√2),

a→0에서 2√(2/π)[1+a²/6−a⁴/120+a⁶/1680+…]다. kinetics는 expm1을 사용해 거의 같은 두 Gaussian을 뺄 때의 소실을 줄였다. 여섯 drift 값과 독립 원 속도-각도 적분으로 확인한 것은 floating 수치 검산이며 엄밀한 interval certificate가 아니다.

K(V,T)=s∫p(y|a)yσ(μs²y²/2)dy, R=n_CR n_HI K. K[m³/s], R[m⁻³/s]. source의 유효 에너지 범위에 해당하는 core만 적분한다. continuum.maxwellian_core는 명시된 piecewise-linear MODEL source를 energy-panel로 나누어 scipy quadrature로 계산한다. QUADPACK 반환 오차는 **추정치**로 표시하고 total_K_upper, low/high tail, source discrepancy는 null로 남긴다. 등방 target에서 scalar count만 축약되며, 비등방 target이나 outgoing angular cut에는 자동 적용하지 않는다.

누락된 scaled 상대속도 영역 |y−a|>L은 target 속도 q=|w|/s>L에 포함된다. σ≤σ_max가 누락 영역 전체에 성립할 때만

K_tail ≤ σ_max s[a P_L+√(2/π)(L²+2)exp(−L²/2)],
P_L=erfc(L/√2)+√(2/π)Lexp(−L²/2)

가 된다. 확률이 작다는 사실만으로 rate tail을 닫지 않는다. exp/erfc의 floating evaluation을 certified zero로 사용하지 않는다. 물리 source의 σ_max와 NR 고에너지 discrepancy는 별도 미확립이다.

## 4. 이산 count와 source 오차

provider는 명시적으로 정규화된 이산 속도분포 w_i, u_j와 비음수 source 모델 구간을 받는다. 각 속도쌍의 E_CM은 유리수로 계산하고 g의 제곱근만 정수 isqrt로 감싼다. 이산 MODEL 함수족에 한해

K∈Σ_ij w_i u_j g_ij [σ_−(E_ij),σ_+(E_ij)]

의 endpoint를 exact 방향으로 조립한다. 이 구간은 연속 Maxwell 적분이나 실제 source truth의 구간이 아니다. source profile은 MODEL만, 출력 capability는 formation_count_1s만 허용한다. 부적합 channel·frame·time·measure·단위·source hash·영역은 거절하며 입력 normalization을 몰래 고치지 않는다.

## 5. 보존식과 Bianchi-I 참조

반응 p_CR+H_g(1s)→H_CR(1s)+p_g의 species순서를 (p_CR,H_g,H_CR,p_g,e_free)로 두면 화학양론은 ν=(−1,−1,+1,+1,0)다. 전체 nuclei, charge, HI/HII와 자유전자 수 변화는 각각0이다. gas proton은 늘고 CR proton은 줄지만 포획 count를 photoionization·자유전자 생성·열원으로 바꾸지 않는다. cx_update는 허용 extent ξ≤min(n_pCR,n_Hg)에서 exact bookkeeping만 수행하며 ξ를 동역학적으로 계산하는 chemistry solver가 아니다.

Bianchi-I metric ds²=−c²dt²+Σ a_i²(dx^i)²에서 공간 Killing 대칭으로 collisionless covariant momenta p_i가 보존된다. orthonormal 성분은 p_hat_i∝a_i⁻¹, homogeneous 입자수 밀도는 n∝(a1a2a3)⁻¹다. bianchi_i_map은 이 참조 mapping과 FLRW 한계를 유리수로 검사한다. 일반 Bianchi·tilted gas·Thomson·radiation/thermal solver를 구현했다고 주장하지 않는다. 국소 원자 source에 임의 shear 계수를 곱하지 않는다.

## 6. 공통 오차 chain

같은 물리량·단위의 exact comparison objects O0→O1→…→On에 대해 |Oi−Oi+1|≤εi가 동시에 성립하면 |O0−On|≤Σεi다. 독립성은 필요하지 않으며 RSS는 사용하지 않는다. 같은 변화를 중복 포함하거나 비연속 비교대상·단위가 다른 σ와 P를 합하면 안 된다. closure.compose_chain은 이를 검사하지만 evidence hash가 실제 연속 증명을 담는지는 외부 admission이 필요하다. 하나의 upper가 null이면 total도 null이다.

## 7. 신뢰 경계

정확 산술은 입력 가정의 진실을 보증하지 않는다. MODEL 참조코드의 통과는 actual source/host·fullH/D·전궤도·basis·b 적분·physical rate의 승인과 다르다. 기존 coefficient-transfer 정리, H5 warm kernel과 Bianchi-I 운동학을 재사용·전문화한 부분과 이번 새 portable 구현을 구분한다. 학술적 개방 문제라는 이유로 중단한 것은 없으며, 남은 것은 구체적인 source/operator/host 입력 및 미구현 전역 검증 경로다.
