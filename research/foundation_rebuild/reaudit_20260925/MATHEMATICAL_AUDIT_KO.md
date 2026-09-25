# BASS_CR D5A 재감사: 수학적 모형, 적분, 반례와 수정

기준: commit `8b7fef411ebca8dcdbfb45de542690c821fd7826`, tree `e17782911caad0af599715f37ac497639bf9e312`. 이 문서의 새 계산은 탐색적 연구 결과이며 과거 D1–D5A 사전등록 결과를 대체하지 않는다. 원문 소스는 `source/`, 새 구현은 `repair/`, 새 수치 증거는 `analysis/`에 분리되어 있다.

## 1. 물리 문제와 단위

고정된 두 핵 궤적에서 단일 전자의 비상대론적 Hamiltonian은

\[
H(t)=-\frac{\hbar^2}{2m_e}\nabla^2
-\frac{Z_T e^2}{4\pi\epsilon_0|\mathbf r-\mathbf R_T(t)|}
-\frac{Z_P e^2}{4\pi\epsilon_0|\mathbf r-\mathbf R_P(t)|}.
\]

프로젝트는 내부적으로 \(a_0,E_h,t_a=\hbar/E_h\) 단위를 사용한다. 그 수치 표현에서 \(m_e=\hbar=e^2/(4\pi\epsilon_0)=1\)이다. 이번 비교는 100 keV/u, b=2 a0, z=-12 a0, v=2.00798106651023 a0/ta, ZT=ZP=1에 한정된다. 직선 궤적, 고정 표적, 유한한 선택 basis라는 원래 가정을 바꾸지 않았다. 핵 반동, 상대론, 단면적 b 적분, all-bound 완비성은 이번 정적 적분 수렴과 별도의 층이다.

이동기저 \(\chi_j\)에서
\[
S_{ij}=\langle\chi_i,\chi_j\rangle,\quad
H_{ij}=\frac{\hbar^2}{2m_e}\langle\nabla\chi_i,\nabla\chi_j\rangle+\langle\chi_i,V\chi_j\rangle,\quad
D_{ij}=\langle\chi_i,\partial_t\chi_j\rangle,
\]
\[
i\hbar S\dot c=(H-i\hbar D)c.
\]
S는 무차원, H는 에너지, D는 시간의 역수다. 따라서 S/H/D의 절대 Frobenius 오차를 서로 같은 단위의 하나의 수로 더하지 않는다. 원자단위 수치에서 \(K=H-iD\)도 별도로 검사했지만 이것만으로 \(S^{-1}K\)의 전파오차 또는 포획오차가 정해지지는 않는다.

## 2. FEM zero extension은 잘못된 물리인가

현재 \(u(r)=rR_l(r)\)는 [0,L]에서 연속인 piecewise polynomial이고 u(0)=u(L)=0이다. L 밖에서 0으로 확장하면 \(u_L=u\Theta(L-r)\)이다. 분포론적으로
\[
u_L'=u'\Theta(L-r)-u(L)\delta(r-L)=u'\Theta(L-r),
\]
\[
u_L''=u''\Theta(L-r)-u'(L^-)\delta(r-L)
\]
이며 내부 knot에서도 u' jump에 대응하는 두 번째 미분의 delta가 존재한다. 따라서 **첫 미분을 쓰는 D에 임의의 경계 delta를 추가해서는 안 된다.** 반대로 강한 미분 Hamiltonian을 아무 경계항 없이 고립 원자 고유값으로 치환하는 것도 정당하지 않다.

3차원 확장 함수는 해당 유한요소 공간에서 H1/form-domain 조건을 충족한다. Coulomb의 weak kinetic form은 유효하다. 강한 H2 regularity가 부족하다는 사실은 FEM 자체가 부적합하다는 결론이 아니다. 문제는 전역 smooth quadrature에 derivative discontinuity와 compact-support 경계를 숨겼다는 데 있다.

원본과 같은 bank를 재구성해 얻은 u 연속성 오차는 최대 약 1e-14, 1D mass norm 오차는 약 3e-15였다. 양에너지 s/p mode의 L=64에서 왼쪽 미분은 각각 -0.0388032607451, -0.0491408926902 (원자단위 radial normalization)였다. bound 1s/2s/2p의 해당 경계 미분은 약 1e-21, 1e-11 수준이다. 이는 bound-only control이 diffuse pseudostate의 경계 민감성을 충분히 검사하지 못하는 이유다. 내부 knot의 u' jump도 존재하며, S보다 H,D 적분의 regularity가 낮다. 수치와 모든 mode별 값은 `analysis/REANALYSIS.json`에 있다.

## 3. 서로 다른 support를 분리해야 한다

유한 radial support의 두 중심 basis에 대해
\[
\operatorname{supp}(\chi_T^*\chi_P)\subseteq B_T(L)\cap B_P(L),
\]
그러나
\[
\operatorname{supp}(\chi_T^*\chi_T)\subseteq B_T(L),\qquad
\operatorname{supp}(\chi_P^*\chi_P)\subseteq B_P(L).
\]
D3은 모든 행렬을 두 구의 교집합에서 적분했다. 이것은 TT/PP에 잘못된 다른 중심 cutoff를 추가한 것이다. D4A에서 z=-12의 D3 큰 차이가 거의 전부 same-center pseudostate block에 있다는 것은 이 구현 오류를 지지한다. 이는 pseudostate의 물리적 부적합이나 원래 GPU 계산 실패의 증거가 아니다.

새 `cross_blocks()`는 TP/PT만 계산한다. same-center block을 0으로 채워 full matrix인 것처럼 반환하지 않는다. disjoint support에서는 cross block의 정확한 0을 반환한다. 같은 중심 구에 대한 별도 적분은 후속 full-matrix 구현에서 필요하다.

## 4. 왜 eta FAIL이 ETF 원인 확정은 아닌가

분리벡터가 (b,0,z), 속도가 lab z 방향이면 상대 ETF 공간위상은 좌표에 무관한 상수를 제외하고
\[
\Phi=\frac{v}{2}\left[z\mu\eta+b\sqrt{\mu^2-1}\sqrt{1-\eta^2}\cos\phi\right],
\quad \mu=1+2\rho/R.
\]
실제 최대 선형 eta 계수 q=126.76226068324343은 큰 수다. 그러나
\[
\int_{-1}^{1}e^{iq\eta}\,d\eta=2\sin(q)/q
\]
라는 독립 정확해에 대해 Gauss–Legendre 96점 적분의 절대오차는 1.18e-15였다. D5A가 사용한 192/256점은 순수 선형위상 하나를 분해하기에 부족하지 않았다.

따라서 **eta direction에서 수렴하지 않는다는 관찰을 pure longitudinal phase underresolution이라는 원인으로 등치한 이전 설명을 철회한다.** 위상과 비매끄러운 진폭의 곱, element/cutoff 경계, radial coordinate와의 결합, 상쇄의 영향은 여전히 존재한다. 이 반례는 모든 ETF 효과가 없다는 증명이 아니다.

## 5. 기하에 맞춘 거리 좌표 적분

\(r_T,r_P\)를 두 초점까지의 거리, \(R>0\)를 핵간 거리라 하면
\[
|r_T-r_P|\le R\le r_T+r_P,
\qquad d^3r=\frac{r_T r_P}{R}\,dr_Tdr_Pd\phi.
\]
수치식의 Jacobian 차원은 L이고 두 radial 미분과 곱하면 L3다. cross support에서는 두 거리 모두 [0,L]이다. 외부 rT partition은
\[
\{e_i\}\cup\{|R-e_j|\}\cup\{R+e_j\}
\]
와 양 끝점으로 분할한다. 내부 rP 구간은 [|R-rT|,min(R+rT,L)]을 각 FEM knot에서 분할한다. 기존 D4C의 이 기하적 구분은 타당했으며, 그것만으로 order 6/8/10이 모든 diffuse integrand를 정확하게 적분한다는 보장은 없었다.

transverse radius를 차가 큰 두 제곱의 차로 구하는 대신
\[
r_\perp^2=\frac{(r_T+r_P+R)(r_T+r_P-R)(R+r_T-r_P)(R-r_T+r_P)}{4R^2}
\]
를 써서 축 근처 cancellation을 줄였다. negative roundoff와 실제 triangle violation을 구분한다. 부피 oracle은
\[
V_\cap=\frac{\pi(2L-R)^2(4L+R)}{12},\quad 0\le R\le2L
\]
이다. **부피가 맞는다는 것은 integrand 1에 대한 검사이며 H,D의 정밀도 보증이 아니다.**

## 6. 정확한 azimuthal ETF 적분

각 고정 거리 쌍의 ring에서 radial amplitude는 phi와 무관하다. solid harmonic의 값은 phi에 대한 차수 l의 유한 삼각다항식이고 gradient는 차수 l+1 이하이다. 따라서 S/H/D의 ETF를 제거한 진폭은 차수
\[
M\le l_i+l_j+2\le2l_{\max}+2
\]
의 유한 Fourier 다항식이다. 현재 s+p basis에서는 안전한 M=4를 사용한다.

\[
\int_0^{2\pi}e^{i\kappa\cos(\phi-\phi_0)}e^{im\phi}d\phi
=2\pi i^m J_m(\kappa)e^{im\phi_0}
\]
로 ETF는 해석적으로 적분한다. Jacobi–Anger expansion의 직접 귀결이다. 진폭에 대해서만 2M+1=9개 ring sample로 Fourier coefficient를 복원한다. 이는 고주파 ETF를 9개 점으로 샘플링하는 방식이 아니다. 수치 가중치는 복소수이며 확률 quadrature로 해석해서는 안 된다.

공간 위상을 제거한 함수와 gradient를 원래 basis evaluator로 계산한 뒤
\[
\nabla\chi=e^{i\Phi}(\nabla\phi+i m_e\mathbf v\phi/\hbar),\qquad
\partial_t\chi=e^{i\Phi}[-\mathbf v\cdot\nabla\phi-i m_ev^2\phi/(2\hbar)]
\]
를 그대로 복원한다. TP/PT는 독립적으로 누적하고 사후 Hermitian symmetrization으로 결함을 숨기지 않는다.

근거: NIST DLMF §10.12, https://dlmf.nist.gov/10.12 . 별도 충분한 uniform-phi 적분과 작은 실제 FEM bank에서 비교했고, 원래 큰 bank의 동일 order10에서 보존된 D4C G3와 약 8e-13 상대차로 일치했다.

## 7. 변경 전후의 통제된 비교

basis: 같은 18 channels, L=64, 40 elements, degree4, lmax1, bound_nmax2, positive_per_l1, 동일한 직접 time derivative와 weak kinetic. 새 p10/p16/p20/p24 계산의 channel identities는 서로 byte-identical이다. 과거 로컬 호스트와 이번 호스트의 regenerated eigenvectors는 byte-identical이라고 주장하지 않는다. Python/SciPy 환경이 다르지만 old/new order10 행렬 parity가 그 차이의 영향이 이번 gate보다 훨씬 작음을 보인다.

| 비교 | S TP 상대 Fro | H TP 상대 Fro | D TP 상대 Fro |
|---|---:|---:|---:|
| 새 order10 vs 보존된 D4C G3 | 7.52e-13 | 7.50e-13 | 7.91e-13 |
| 새 order16→20 | 3.22645e-7 | 1.69449e-7 | 6.47989e-7 |
| 새 order20→24 | 1.21104e-11 | 6.65655e-12 | 2.38841e-11 |

order24의 bound-only subblock은 과거 B G3와 S/H/D 약 4.5e-13–7.2e-13로 일치한다. 따라서 이 개선은 pseudostate를 삭제하거나 기준을 느슨하게 하거나 desired energy를 fitting한 결과가 아니다. **정확히 같은 유한 basis의 적분 문제가 해결 가능한 형태였음을 확인했다.**

그러나 유한한 refinement 비교는 엄밀한 outward-rounded error enclosure가 아니다. 새 oracle도 모든 geometry/상자크기/고에너지 mode/고차 l에서 보편적으로 검증된 것은 아니다. p24 reference 대비 과거 D5A 최종행렬의 상대차는 S 5.885e-4, H 2.554e-3, D 4.787e-3다. D5A의 S는 eta 마지막 쌍 비교를 통과했어도 전체 적분오차가 그 수치보다 컸다는 점이 중요하다. 이는 마지막 한 축 차분을 joint convergence나 capture-error bound로 쓰면 안 된다는 실측 예다.

## 8. 후속 full-matrix 경로에서의 정확한 cancellation

동일 중심의 ETF가 동일하면 Scc의 phase는 상쇄된다. \(A_{ab}=\langle\phi_a,\nabla\phi_b\rangle\)라 두면
\[
H_{cc}=H_{0,c}-i\hbar\mathbf v_c\cdot A+	frac12m_ev_c^2 S_{cc}+V_{{\rm other},cc},
\]
\[
D_{cc}=-\mathbf v_c\cdot A-i m_ev_c^2S_{cc}/(2\hbar).
\]
따라서 \(H_{cc}-i\hbar D_{cc}=H_{0,c}+V_{{\rm other},cc}\). 이는 후속 통합 시 검사할 구조적 항등식이다. 이번 코드에 full same-center assembly나 collision propagation을 구현했다는 뜻은 아니다. H와 D 각각의 상대차 외에도 실제 생성자에서 큰 항 cancellation이 정확한지 검사해야 한다.

## 결론

확인된 수치 문제는 '양에너지 상태라는 물리 가정의 실패'가 아니라, 유효한 compact C0 FEM 기저의 piecewise/oscillatory cross integral을 smooth global tensor rule 또는 너무 낮은 local order로 처리한 데 있다. D3에는 그와 별도로 support 구현 오류가 있었다. 각 원인의 오차 기여율을 독립적으로 모두 분해한 것은 아니지만, **동일 기저에서 원 실패 계산의 일치 재현과 개선된 수렴을 동시에 얻는 통제된 수정**을 완성했다. 원래 GPU capture의 3% 공간 pair 문제는 별개로 남는다.
