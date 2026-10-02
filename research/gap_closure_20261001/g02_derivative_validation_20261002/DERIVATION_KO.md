# R4Z: 중앙점의 독립적인 overlap 미분 검산

2026-10-02 KST. 이 문서의 항등식은 **derived**, 유리수 가중치 검사는 **exact arithmetic**, 이미 저장된 R4X/Y 자료에 관한 관측은 **numerically checked**다. R4Z의 새 물리 계산 결과는 이 문서가 아니라 실행·분석 결과에 기록한다. 문서 작성 과정의 물리 연산자 호출은 0회다.

이번 계약은 별도 identity의 연속 후보에 대해 중앙점의 미분을 독립적으로 수치 검산한다. 고정된 S-only stencil, 두 미세 window의 일치, 세 공간 적분 규칙의 일치, 수정하지 않은 D와의 일치를 함께 요구한다. 원래 8개 offcentral 지점의 원시 2차 차분 판정과 production HOLD는 변경하지 않는다.

## 1. 정의, 단위와 고정된 조건

원본 `bass_foundations/two_center.py::basis_values`가 사용하는 electron translation factor(ETF)를 물리 단위로 쓰면

\[
\chi_{Ca}(\mathbf r,t)=e^{i\vartheta_C(\mathbf r,t)}
 \phi_{Ca}(\mathbf r-\mathbf A_C-\mathbf v_Ct),\qquad
\vartheta_C=\frac{m_e}{\hbar}\left(\mathbf v_C\cdot\mathbf r-
\frac{v_C^2t}{2}\right),
\]

\[
\phi_{Ca}(\mathbf x)=\frac{u_{Ca}(r)}rY_{\ell_a m_a}(\hat{\mathbf x}),
\qquad S_{ab}=\langle\chi_a|\chi_b\rangle,
\qquad D_{ab}=\langle\chi_a|\partial_t\chi_b\rangle.
\]

위상의 질량은 전자 질량이다. 핵의 속도를 사용하는 ETF이며 핵 질량을 지수에 넣지 않는다. 속도와 radial 계수는 시간에 무관하고 궤도는 직선이다. 공간 내적은 전 공간에서 계산하며, compact support 밖으로 원자 함수를 0으로 연장한다. 구면조화함수는 소스의 complex Condon–Shortley convention을 유지한다.

내부 단위는 a₀, Eₕ, tₐ=ℏ/Eₕ이고 속도 단위는 a₀/tₐ다. S는 무차원, D와 Ṡ는 tₐ⁻¹, Aⱼ=⟨φₐ|∂ⱼφᵦ⟩는 a₀⁻¹이다. φ의 단위는 길이⁻³ᐟ², u는 길이⁻¹ᐟ²다. 아래에서 속도와 파수는 구별한다:

\[
\mathbf w=\mathbf v_P-\mathbf v_T,\qquad
\mathbf k=\frac{m_e}{\hbar}\mathbf w.
\]

원자단위 수치에서 w와 k의 숫자가 같다는 이유로 물리 단위의 식에서 서로 바꾸면 안 된다.

실제 계약은 b=2a₀, 100keV/u, v=2.00798106651023a₀/tₐ, v_T=0, v_P=v e_z, 두 charge=1, 18채널이다. 중심 좌표는 R_T=0, R_P=(b,0,z), z=vt다. R4X 연속 후보 identity는 `17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef`다. 원본 불연속 monomial 표현과 동일한 함수라고 간주하지 않는다.

## 2. 미분 항등식과 경계 가정

고정 lab 점에서 직접 미분하면

\[
\partial_t\chi_{Cb}=e^{i\vartheta_C}
\left[-\mathbf v_C\cdot\nabla\phi_{Cb}
-\frac{i m_ev_C^2}{2\hbar}\phi_{Cb}\right].
\]

공간이동 미분의 부호는 음수다. 두 항은 각각 속도×공간미분과 에너지/ℏ이므로 모두 시간⁻¹×φ 단위를 갖는다. 이 식에서 D를 독립적으로 적분한 뒤, 내적의 곱 미분을 적용하면

\[
\boxed{\dot S_{ab}=\langle\dot\chi_a|\chi_b\rangle+
\langle\chi_a|\dot\chi_b\rangle=(D^\dagger+D)_{ab}.}
\]

필요한 전제는 각 시간의 기저가 L²에서 강미분 가능하다는 것이다. 본 후보의 radial 함수는 유한 개 polynomial 조각으로 연속이고 u(0)=u(L)=0이며, 0으로 연장한 φ는 H¹(R³)에 속한다. 구면 성분에서 충분한 유한성 검사는

\[
\int_0^L\left(|u'|^2+\ell(\ell+1)|u/r|^2\right)dr<\infty
\]

이다. u(0)=0이고 첫 구간이 polynomial이므로 u/r는 원점 근방에서 유계다. 함수값 trace가 연속이므로 이동 interface에서 추가 delta 미분은 없다. 도함수의 shell jump는 허용되며 이것이 H² 또는 strong Coulomb action의 존재를 보장한다는 뜻은 아니다. H¹ 함수의 translation은 L²에서 약한 공간 gradient를 도함수로 가지므로 위 항등식은 성립한다.

같은 중심에서는 ETF가 내적에서 소거되고 공통 translation을 적분 변수로 제거할 수 있어 S_CC(t)는 상수다. H¹와 zero outer trace 아래 integration by parts로 Aⱼ+Aⱼ†=0이므로 D_CC+D_CC†=0이다. 이론상 영값은 원시 D를 반대칭화하거나 수치 원소를 0으로 덮어쓰는 처방이 아니다. 본 계약은 그러한 투영을 금지한다.

## 3. 독립적인 geometric derivative와 ETF 위상 검산

M=(R_P+R_T)/2, R=R_P−R_T, x=r−M라 두면

\[
S^{TP}_{ab}=e^{i\theta_0}\int e^{i\mathbf k\cdot\mathbf x}
 \phi_{Ta}^*(\mathbf x+\mathbf R/2)
 \phi_{Pb}(\mathbf x-\mathbf R/2)d^3x,
\]

\[
\theta(t)=\frac{m_e}{\hbar}
\left[\mathbf w\cdot\mathbf M(t)-\frac{v_P^2-v_T^2}{2}t\right]
=\frac{m_e}{\hbar}\mathbf w\cdot\frac{\mathbf A_P+\mathbf A_T}{2}
=\theta_0.
\]

Ṁ=(v_P+v_T)/2이고 w·Ṁ=(v_P²−v_T²)/2이므로 carrier가 정확히 상쇄된다. 이번 b⊥v 기하에서는 θ₀=0이다. lab 식의 −m_ev²t/(2ℏ)만 임의로 제거하는 demodulation은 이 상쇄를 깨므로 독립 미분을 자동으로 개선하지 않는다.

중점 표현을 직접 미분하면

\[
\boxed{\dot S^{TP}_{ab}=\frac{e^{i\theta_0}}2
\int e^{i\mathbf k\cdot\mathbf x}\,
\mathbf w\cdot\left[(\nabla\phi_{Ta}^*)\phi_{Pb}
-\phi_{Ta}^*(\nabla\phi_{Pb})\right]d^3x.}
\]

gradient에 곱하는 것은 파수 k가 아니라 상대 속도 w다. 이 식은 H¹만으로 정의되는 geometric derivative의 computational form이다. 원래 lab D+D†의 공통 속도 V=(v_P+v_T)/2 항은 −V·∇(φ_T*φ_P)이고, integration by parts 뒤 +iV·k S가 된다. 이것은 ETF carrier의 −i m_e(v_P²−v_T²)S/(2ℏ)와 상쇄되어 위 식을 재현한다.

정지 target에서는 D_PT=0이므로 교차 블록에서 Ṡ_TP=D_TP다. 동일 실수 s 모드의 양 중심 overlap은 중점 반전에 의해 실수이고 z에 대해 짝함수이므로 중앙의 해당 D_TP 대각은 정확히 0이다. 이는 R4Y에서 사용한 제한된 독립 대칭 진단이며, 일반적인 offdiagonal·p 원소의 미분을 0이라고 주장하지 않는다.

이 geometric 식의 별도 수축 구현은 이번 R4Z 계약에 포함하지 않았다. 기존 native D의 재조합을 독립 oracle이라고 부르지 않는다. 실제 구현 검증 경로는 다음 S-only 표본 미분이다.

## 4. S-only stencil의 유리수 구성

공간 간격 h의 원시 중앙차분을

\[
F(h)=v\frac{S(h)-S(-h)}{2h}
\]

로 정의한다. v는 z 미분을 t 미분으로 바꾸므로 결과 단위는 tₐ⁻¹이다. 시간 샘플은 t=±h/v이고, h와 시간을 혼동하지 않는다. 각 window는 h_j=H/2^j, j=0,1,2,3의 네 간격으로 구성한다.

가중치 w_j는 D를 사용하지 않고 다음 유리수 선형계로 고정한다:

\[
\sum_{j=0}^{3}w_j=1,\qquad
\sum_{j=0}^{3}w_j4^{-jk}=0\quad(k=1,2,3).
\]

Vandermonde 점 1,1/4,1/16,1/64가 서로 다르므로 해는 유일하며

\[
(w_0,w_1,w_2,w_3)=\left(-\frac1{2835},\frac4{135},
-\frac{64}{135},\frac{4096}{2835}\right),\qquad
R_8(H)=\sum_{j=0}^{3}w_jF(H/2^j).
\]

따라서 이 조합은 z에 대한 행렬값 다항식의 차수 8까지 중앙 미분을 정확하게 재현한다. 이는 polynomial moment cancellation에 관한 대수 명제이며 실제 물리 S가 8차 다항식이라는 뜻이 아니다. 유리수 직접 합으로 k=0…4의 moment를 계산하면 (1,0,0,0,−1/4096)을 얻는다.

추가로 S가 충분히 매끄럽고 9차 도함수의 Taylor remainder를 제어할 수 있다면 조건부로

\[
R_8(H)=vS'(0)-\frac{vH^8}{4096\,9!}S^{(9)}(0)+o(H^8)
\]

를 얻는다. **본 후보의 H¹ 성질만으로 이 전제를 얻을 수 없다.** 따라서 R₈은 가중치 조합의 이름이며 이번 계산에 대한 인증된 8차 수렴 또는 연속 오차 상계가 아니다. 기존 `richardson_diagnostic.build_table`의 재귀 `(4^k*b−a)/(4^k−1)`가 이 유리수 조합과 같은 식을 구현한다. 계수 적합, 차수 선택, scalar correction에 D를 사용하지 않는다.

세 window는 H=0.4,0.2,0.1a₀이고 각각 마지막 h는 0.05,0.025,0.0125a₀다. 첫 window도 보존하지만 계약의 판정은 두 미세 window를 모두 사용한다. 같은 결과가 나오는 window 하나만 사후 선택하지 않는다.

## 5. 차분 오차 민감도와 공간 오차의 구별

각 저장 overlap 표본에 norm error가 ε_{j,±}라면, 선형성으로 주어진 어떤 일관된 행렬 norm에서도

\[
\|\delta R_8\|\le\sum_j\frac{v|w_j|}{2h_j}
(\epsilon_{j,+}+\epsilon_{j,-}).
\]

모든 ε_{j,±}≤δ인 경우 계수 합은

\[
\sum_j|w_j|=\frac{1105}{567},\qquad
\sum_j\frac{v|w_j|}{h_j}=\frac{473v}{35H}.
\]

이번 세 H에서 마지막 값은 각각 67.8410746042,135.6821492085,271.364298417tₐ⁻¹이다. 이들은 S 표본 오차를 미분 오차로 전달하는 **조건부 sensitivity 계수**다. 실제 δ가 확보되지 않았으므로 machine epsilon×표본 norm을 대입한 숫자는 heuristic surrogate이며 quadrature·누적·basis·D 오차의 엄밀한 상계가 아니다.

공간 적분 q40,β24 대 q48,β24와 독립 q48,β12 비교는 각 13개 기하에서 모두 수행한다. 원래 여섯 raw block 상대 차이≤10⁻⁹, full S/H Hermiticity≤10⁻¹¹, metric λ_min/λ_max≥10⁻⁸를 유지한다. 이 상대 기준 통과만으로 작은 차분의 절대 오차≤10⁻¹²가 보장되지 않으므로, 세 규칙으로 구성한 미분 자체의 일치도 별도로 요구한다. 같은 기하·기저·moment 구현을 일부 공유하므로 이를 완전한 독립 error bound로 부르지 않는다.

또한 same-center S_CC는 이론상 상수지만 현재 assembly는 다른 핵의 거리 R에서 S 적분 panel도 분할한다. 저장된 R4X 후보 q40의 z=−32와 z=0을 비교하면 S_TT의 일부 대각이 1.1102230246251565×10⁻¹⁶만큼 다르다. 이는 시간 의존 floating-point bytes의 관측이며 모든 가까운 표본 오차에 대한 상계는 아니다. R4Z는 기존 same-center order20과 원시 값을 그대로 사용한다. 고정 FEM partition으로 S/A/H0를 계산하고 V_other만 R에서 분할하는 별도 개선은 이번에 시행하지 않는다.

## 6. 원래 gate와 이번 국소 판정

원래 `static_validation.compare_ladder`의 E_h=F(h)−(D+D†)를 그대로 계산한다. spectral, Frobenius 각각은 절대≤10⁻¹² **또는** 상대≤10⁻⁶이고, elementwise는 전체 최대 절대≤10⁻¹² **또는** 전체 최대 normalized≤10⁻⁶이다. 성분별 denominator는 max(|F_ij|,|D+D†|_ij,10⁻¹²,eps×spectral scale)이다. 관측차수 1.5…2.5인 두 연속 구간도 필요하다. 이 논리를 원소별 혼합 abs/rel 판정으로 바꾸지 않는다.

이번에도 처음 네 h와 전체 여섯 h의 원시 R₂ 결과를 각각 보존한다. 중앙점의 새 R₈ check가 통과하더라도 원래 offcentral 8개 지점의 실패를 PASS로 바꾸지 않는다. 기존 h-independent same-center cancellation 잔차를 원시 D 투영으로 제거하지 않는다.

새 계약의 국소 수치 검산은 세 공간 규칙 각각에서 두 미세 R₈ window와 raw D(0)+D(0)† 사이의 spectral, Frobenius, 최대 성분 절대 잔차가 모두 10⁻¹²tₐ⁻¹ 이하여야 한다. 두 window의 상호 차이와 공간 규칙 사이 미분의 차이도 동일한 절대 기준을 만족해야 한다. 모든 표본의 공간 qualification 및 fresh backend bitwise parity가 전제다. 실패는 보존하고 임계값을 조정하지 않는다.

이 판정의 범위는 **CENTRAL_CANDIDATE_DERIVATIVE_NUMERICAL_CHECK_ONLY**다. 기저의 전역 채택, 연속 trajectory certificate, NCP64 scaling, capture 또는 original G02 전체 closure가 아니다.

## 7. 극한, regularity와 다음 실험의 경계

두 속도가 같으면 w=k=0이고 상대 위치가 고정되므로 cross Ṡ=0이다. 지지가 분리되면 교차 S와 D는 0이다. 같은 중심 overlap의 미분은 항상 0이다. 이 극한들은 ETF 위상과 미분 부호에 일관된다. 가속, radial 계수의 시간 의존성, 별도 중심 phase, 비영 외곽 trace가 있으면 추가 항이 필요하며 본 증명의 조건 밖이다.

중앙 R=2a₀는 현재 FEM shell의 접촉 거리 |e_i−e_j| 또는 e_i+e_j와 실제로 일치한다. 실제 FP64 edges를 정확한 유리수로 읽었을 때 2보다 큰 다음 접촉 거리는 9187343239835813/4503599627370496a₀(표시값 2.04a₀)이고, 가장 먼 stencil의 R=2.039607805437114a₀는 그보다 작다. 즉 이 stencil 안에서는 중앙 접촉을 제외한 새로운 접촉 거리를 건너지 않는다. 이 사실만으로 중앙에서의 regularity가 증명되지는 않는다. 따라서 interface 기하가 바뀌지 않는 매끄러운 구간의 Taylor 논증을 중앙에 무조건 적용하지 않는다. 동일 s 모드의 짝대칭만으로도 해당 중앙 도함수는 정의되지만, 일반 행렬의 9차 시간 미분까지 따라오지 않는다.

후속 offcentral 설계를 위한 읽기 전용 기하 진단에서 z=−32a₀의 R=32.0624390837628a₀는 가장 가까운 shell 접촉 거리 32.08a₀와 0.0175609162372a₀ 떨어져 있다. 아주 작은 h ladder는 그 접촉점을 건너지 않을 수 있으나, 동시에 1/h roundoff 증폭을 겪는다. 이 관측은 차기 설계의 근거일 뿐 이번 중앙 계약을 넓히거나 offcentral 검증을 실행했다는 뜻이 아니다.

이 문서의 유도는 실제 로컬 소스와 고정 입력에 근거한다. 새 문헌 정리를 차용하거나 미확인 인용을 추가하지 않았다. 입력·소스 hash와 대수 검산값은 `THEORY.json`에 보존한다. 실제 R4Z 계산 결과, 독립 검토와 배포 완료 여부는 각각의 별도 evidence에서 확인한다.
