# 해석적 축약과 물리적 pruning의 증명

## 1. 보존한 모형과 단위

두 점 Coulomb 핵과 비상대론적 한 전자, 고정 target 및 직선 projectile 궤적을 유지한다. 100 keV/u, b=2 a0, 기존 18-channel FEM radial coefficient payload를 사용한다. 내부 단위는 a0, Eh, ta=ħ/Eh이다. 차원 있는 식은

\[
\chi_A(\mathbf r,t)=e^{i m_e\mathbf v_A\cdot\mathbf r/\hbar-i m_ev_A^2t/(2\hbar)}f_A(\mathbf r-\mathbf R_A(t)),
\]
\[
S_{ab}=\langle\chi_a|\chi_b\rangle,\quad
H_{ab}=\frac{\hbar^2}{2m_e}\langle\nabla\chi_a|\nabla\chi_b\rangle+\langle\chi_a|V|\chi_b\rangle,
\quad D_{ab}=\langle\chi_a|\partial_t\chi_b\rangle
\]
이다. V=-e²[ZT/rT+ZP/rP]/(4πε0). H는 Eh, D는 ta^-1 단위의 수치 행렬이다. S는 무차원이다. U(L)=0인 유한 FEM 상태의 미분 jump 때문에 강한 Laplacian을 고유에너지로 치환하지 않는다. TT/PP는 자기 중심의 전체 support, TP/PT는 두 support의 교집합을 사용한다.

## 2. 최대 각도 차수를 먼저 줄인다

s+p 기저에서 무위상 함수는 f=A(r)L(x), A=u/r^(l+1)이며 L=q0+q·x이다. s에서 q=0, p에서 q0=0이다. B=A'(r)/r라 쓰면

\[
\nabla f=A\mathbf q+BL\mathbf x.
\]

두 중심축 eR에 대해 xT=a eR+ρ(c e1+s e2), xP=(a-R)eR+ρ(c e1+s e2), c=cosφ,s=sinφ이다. rT,rP가 고정된 ring에서는 A와 B는 φ에 무관하고

\[
\mathbf x_T\cdot\mathbf x_P=\frac{r_T^2+r_P^2-R^2}{2}
\]

는 상수다. 따라서

\[
\nabla f_T^*\cdot\nabla f_P=
A_TA_P\mathbf q_T^*\cdot\mathbf q_P
+A_TB_PL_P\mathbf q_T^*\cdot\mathbf x_P
+B_TA_PL_T^*\mathbf x_T\cdot\mathbf q_P
+B_TB_PL_T^*L_P\mathbf x_T\cdot\mathbf x_P.
\]

개별 gradient component를 곱하면 4차처럼 보이지만, 벡터 내적을 먼저 하면 각도 차수는 2이다. ETF를 포함한 gradient에는 i m_e v f/ħ가 추가되므로 H는 최대3차, 직접 D 역시 최대3차다. S와 unboosted kinetic은 최대2차다. Wolfram의 다항식 나머지 검사는 0, 차수 검사는 {2,2,3,3}을 반환했다. 기존 degree4의 9 ring samples는 정확성 문제를 만들지는 않았지만 불필요하게 비싼 상한이었다.

## 3. Ring을 아예 평가하지 않는다

k=m_e(vP-vT)/ħ라 하고 e1을 k의 중심축 수직 성분 방향으로 택한다. 각도 위상은 exp(iκ cosφ), κ=k_perp ρ이다. 필요한 여섯 적분은

\[
(M_0,M_c,M_{cc},M_{ss},M_{ccc},M_{css})=
\left(2\pi J_0,2\pi iJ_1,\pi(J_0-J_2),\pi(J_0+J_2),\frac{i\pi}{2}(3J_1-J_3),\frac{i\pi}{2}(J_1+J_3)\right).
\]

모든 홀수 sinφ 항은 0이다. 예를 들어 선형 L_T=t0+tc c+ts s, L_P=p0+pc c+ps s의 곱은

\[
\int e^{iκc}L_TL_Pdφ=M_0t_0p_0+M_c(t_0p_c+t_cp_0)+M_{cc}t_cp_c+M_{ss}t_sp_s.
\]

여기에 v·x라는 선형식이 하나 더 곱해져도 3차 moments 두 개만 추가하면 된다. native code는 이 bilinear/trilinear form을 직접 축약한다. 9개 φ 점에서 값을 만드는 방식, 3개의 gradient field, D field 및 큰 중간 배열이 사라진다. 두 거리 적분은 여전히 수치적으로 남으므로 '모든 두 중심 적분을 해석적으로 해결했다'고 표현하지 않는다.

J2=2J1/κ-J0, J3=4J2/κ-J1을 κ>=4에서 사용한다. 작은 κ에서는 J2,J3를 직접 평가해서 상쇄와 0 나눗셈을 피한다. J0,J1의 실수 인자 전용 함수와 원래 일반 jv의 결과를 비교했다. 이 선택은 exact identity에 근거한 계산 경로이며, 부동소수점 오차의 엄밀한 enclosure는 아니다.

## 4. raw H와 D의 의미를 보존한다

코드 내부 atomic units에서

\[
\nabla\chi=e^{i\Phi}(\nabla f+i\mathbf v f),\qquad
\partial_t\chi=e^{i\Phi}(-\mathbf v\cdot\nabla f-iv^2f/2).
\]

두 D 방향을 각각 이 식에서 계산한다. Target가 정확히 정지했을 때만 D_PT=0을 사용한다. 작다고 보이는 속도나 작은 행렬원소를 threshold로 제거하지 않는다.

S_PT=S_TP†, H_PT=H_TP†는 실수 Coulomb Hamiltonian의 약한 형태에 대한 정확한 항등식이다. 한 방향을 계산하고 다른 방향을 복원하되 두 값을 평균하지 않는다. 이 결과의 Hermiticity가 0이라는 것은 '독립 검증'이 아니라 구성 원리다. 따라서 과거의 독립 양방향 ring 계산과 여섯 raw block을 모두 비교했다.

## 5. Cartesian 표현과 정확한 18→14 pruning

각 p radial multiplet에서

\[
p_x=(Y_{1,-1}-Y_{1,+1})/\sqrt2,\quad
p_y=i(Y_{1,-1}+Y_{1,+1})/\sqrt2,\quad p_z=Y_{1,0}.
\]

이 변환은 unitary이고 radial function을 섞지 않는다. Cartesian solid harmonic coefficient는 실수이므로 native contraction의 불필요한 복소 곱도 제거할 수 있다. 일반 complex multiplet이 불완전하면 원래 complex 경로로 돌아가고, 부분 집합에 잘못된 unitary 회전을 적용하지 않는다.

현재 궤적의 핵 위치와 속도는 고정 xz 평면 안에 있다. 반사 P_y:y→-y는 H와 기저의 시간미분을 보존한다. 완전한 magnetic multiplet을 가진 유한 공간에서 S,H,D가 모두 even/odd block diagonal이다. 각 중심에 p radial 상태가2개이므로 odd p_y는 총4개다. Target1s는 even이다. S가 비특이인 동안 odd 계수의 homogeneous ODE에 초기값0을 주면 유일한 해는0이므로 14-dimensional even block은 원래18-dimensional 유한모형과 정확히 동등하다.

여기서 U는 lab Cartesian basis의 시간독립 변환이다. 적분용 중심축 frame만 움직일 뿐 상태 기저를 임의로 회전시키는 것이 아니다. 따라서 숨은 Udot connection을 빠뜨리지 않는다. 수치 검증에서 even embedding의 U†U-I는4.44e-16, S/H/D off-sector 상대 norm은 각각2.78e-17,4.63e-17,3.95e-17이었다. Odd initial state, y방향 속도, 불완전한 p multiplet에는 pruning을 거절한다. 비대칭 외부장, 다른 초기상태, spin coupling까지 이 결과를 확장하지 않는다.

## 6. 탐색하고 탈락시킨 좌표 변경

r=rT와 target polar θ를 쓰면 rP²=r²+R²-2rRcosθ, dV=r²sinθ drdθdφ이다. |∂θΦ|<=|k|r이므로 angular panel의 위상 변화를 제한할 수 있다. 모든 FEM shell 경계를 θ로 옮기고 phase budget8rad, q12/16/24/32의 네 규칙을 조사했다.

정확한 lens volume은 재현됐으나 z0의 raw 행렬 차이는 각각1.042e-5,6.527e-6,2.886e-6,4.578e-8이었다. 전부1e-9 기준을 위반했다. 위상 변화량만 제한하는 것으로 moving interface amplitude와 Jacobian을 포함한 완전한 integrand 오차가 보장되지 않는다. 이 경로를 채택하지 않았으며 더 높은 q로 사후 튜닝하지 않았다. 특정 탐색 범위에서의 실패이지 polar coordinates 자체의 불가능성 증명은 아니다.

## 7. 비용을 줄일 수 있어도 버리면 안 되는 항

- Ritz eigenvalue 관계 a(φ_h,v_h)=E_h m(φ_h,v_h)는 해당 FEM test space에서의 관계다. 다른 중심의 translated orbital이 그 공간에 속하지 않으므로 cross kinetic을 E*S로 치환할 수 없다. Interface/outer-wall weak residual을 무시하는 shortcut은 배제했다.
- Sdot=D+D†를 만족시키도록 D를 재구성하거나 G를 사후 반Hermitian으로 투영하지 않는다. 이는 오류를 숨긴다.
- Diffuse pseudostate를 작은 에너지/작은 점유 추정으로 삭제하지 않는다. 이번 pruning은 대칭으로 정확히 불변인 sector와 해석적으로 중복인 계산뿐이다.
- 같은 노드를 reference/candidate라는 이름으로 두 번 계산한 결과는 독립 증거가 아니다. Effective mesh/order/time/basis/engine/sector가 같은 요청만 canonical key로 합치고, alias 여부를 보고한다.

## 외부 근거와 직접 유도

Bessel moment 항등식의 출발점: NIST DLMF10.9 (https://dlmf.nist.gov/10.9), integer recurrence: DLMF10.6 (https://dlmf.nist.gov/10.6). Gaussian quadrature의 다항식 정확성: DLMF3.5 (https://dlmf.nist.gov/3.5). 이 문헌은 위 수치 결과나 속도 배수를 증명하지 않는다.

SciSpace로 two-center charge-transfer integral 문헌을 검색했다. Anderson–Antal(1975), DOI10.1088/0022-3700/8/9/017은 integral interpolation, Silverstone(2014), DOI10.1021/jp5070159는 Slater-type contour integration, Safouhi(2006), DOI10.1007/s00894-005-0020-z는 Bessel integral convergence transformation을 제안한다. 여기서는 abstract-level screening이며 본문 전체를 검증했다고 주장하지 않는다. Compact piecewise FEM과 moving metric에 적용하려면 추가 근거가 필요해 이번 대체법으로 채택하지 않았다.

Levin/Filon 계열은 진동 인자를 별도 ODE 또는 moment로 처리하는 후속 후보로 분류했다. 이번에는 해당 solver를 구현하거나 수렴성을 검증하지 않았다. Compact FEM의 각 piece와 끝점/축 근처의 Bessel-ODE 계수 처리가 추가로 필요하므로, 현재 검증된 경로를 대체하지 않는다. 확인하지 않은 논문 식별자나 성능 주장은 여기에 넣지 않는다.

외부 primary-source metadata/abstract도 https://arxiv.org/abs/2211.13400 및 https://arxiv.org/abs/1912.09698에서 확인했다. 전자는 adaptive Levin의 low-frequency/stationary-point 처리, 후자는 singularity separation을 다룬다. 이 두 결과가 현재 compact FEM two-centre problem에 그대로 적용된다고 주장하지 않으며 본문 정리의 전제까지 감사한 것은 아니다.
