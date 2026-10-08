# R4Y: 충돌 중심의 공간 적분 진단과 횡위상 패널

2026-10-02 KST. 이 문서는 기존 R4X 원자료 읽기, 구현식의 직접 유도, 적분점 기하의 계산만 수행한 결과다. 새로운 물리 연산자·시간 전파·capture 호출은 0회다. G02=UNRESOLVED, production=HOLD, capture=false를 유지한다. 아래 정리는 연속 후보의 특정 대칭 원소에만 적용하며 전체 미분 검증을 대신하지 않는다.

## 1. 정의와 구현 경로

정지 target의 위치를 원점, projectile의 위치를 \(\mathbf R=(b,0,z)\), 속도를 \(\mathbf v=(0,0,v)\), \(z=vt\)로 둔다. R4X 입력은 \(b=2a_0\), \(v=2.00798106651023a_0/t_a\), 지지 반경 \(L=64a_0\)다. \(t_a=\hbar/E_h\)이며 실제 위상 파수는 \(\mathbf k=m_e\mathbf v/\hbar\)다. 아래 구현 수치는 길이 \(a_0\), 시간 \(t_a\) 단위이므로 속도의 수치가 파수의 수치와 같다. D의 단위는 \(t_a^{-1}\)다.

두 초점 거리 \(r_0,r_1\), 핵간 거리 \(R=|\mathbf R|\), target 기준 축좌표 \(a\), 횡반경 \(\rho\)는

\[
a=\frac{r_0^2-r_1^2+R^2}{2R},\qquad
\rho^2=r_0^2-a^2,
\qquad d^3r=\frac{r_0r_1}{R}\,dr_0dr_1d\phi.
\]

삼각 영역 \(|r_0-r_1|\le R\le r_0+r_1\) 안에서 \(0\le r_0,r_1\le L\)다. `geometry_pairs`는 기존 FEM 셀 경계뿐 아니라 삼각 경계와 inner FEM 경계의 모든 교차점을 outer 구간 경계에 넣는다. 따라서 이번 문제를 단순히 누락된 FEM 불연속 경계로 설명할 근거는 없다.

`continuous_exact_cross.cross`의 ETF 공간 위상은

\[
\Phi=k_\parallel a+k_\perp\rho\cos\phi+\Phi_0,
\quad k_\parallel=\frac{m_ev}{\hbar}\frac zR,
\quad k_\perp=\frac{m_ev}{\hbar}\frac bR.
\]

코드는 s+p 각도 진폭의 여섯 ring moments를 \(J_0,J_1,J_2,J_3\)로 계산한다. \(\phi\) 격자 aliasing은 이 구현의 문제가 아니지만 \(\kappa=k_\perp\rho\)에 따른 Bessel 진동은 남은 두 거리 적분이 해상해야 한다. Bessel 부동소수 평가 자체가 수학적으로 정확하다는 뜻은 아니다. `phase_split_edges`는 \(|k_\parallel|\Delta(r^2)/(2R)\)만 사용하므로 \(z=0\)에서는 양의 budget을 넣어도 원래 경계를 그대로 반환한다.

## 2. 기존 원자료와 기하만으로 확인한 결과

동일 입력에서 구현식을 계산하면 다음과 같다.

| 위치 | R/a₀ | k∥ a₀ | k⊥ a₀ | 지지 교집합의 max κ |
|---|---:|---:|---:|---:|
| z=−32a₀ | 32.06243908 | −2.004070681 | 0.1252544176 | 7.760721664 |
| z=0 | 2 | 0 | 2.007981067 | 128.4950999 |

여기서 \(\rho_{\max}=\sqrt{L^2-R^2/4}\)다. 중앙에서는 Bessel argument 범위가 약 20.45개의 \(2\pi\) 간격에 해당한다. 이는 국소 적분 오차의 증명이 아니라 진동 해상도의 기하학적 진단이다.

더 직접적으로 order40의 실제 outer Gauss 노드만 생성해 inner FEM 패널의 \(\kappa\) 범위를 계산했다. 중앙에서 \(r_0=63.99897787163213a_0\)일 때 하나의 inner 패널 \([61.99897787163213,64]a_0\)가 \(\kappa=0\)부터 128.494056834까지 덮는다. far z=−32의 최대 inner 패널 변화는 2.360331589뿐이다. 따라서 동일한 Gauss 차수의 난도가 크게 다르다.

R4X의 원본과 연속 후보는 중앙에서 거의 동일한 order32→40 차이를 보인다. 후보의 최대 S 차이 \(1.7496204929\times10^{-4}\)와 D 차이 \(3.4897684264\times10^{-4}t_a^{-1}\)는 모두 cross [2,2]이며 양의 에너지 s 모드의 동일 모드 쌍이다. 해당 원소는 넓은 지지 구간을 사용하는 상태다. 경계 표현을 바꾼 효과가 \(10^{-14}\) 수준인 반면 이 차이는 훨씬 크므로 R4W의 미세 경계 불연속만으로 중앙 실패를 설명할 수 없다.

**근거 상태:** 횡위상 해상도 부족은 강한 기하·소스 근거가 있는 원인 가설이다. 실제 패널 개입 후 잔차가 감소하는지 확인하기 전에는 완전히 입증된 원인이라고 부르지 않는다. 아래 정리는 [2,2]의 절대 오차 자체를 별도로 확정한다.

## 3. 동일한 실수 s 모드의 중앙 D=0 정리

각 원자 중심에 같은 실수 s 함수 \(f(\mathbf r)=u(|\mathbf r|)/(\sqrt{4\pi}|\mathbf r|)\)를 놓는다. 연속 후보의 \(u\)는 원점 및 외곽에서 0이고, 유한 개 다항식 조각으로 연속이며, 원점에서 \(u(r)/r\)의 유한 극한이 존재한다. 따라서 0으로 연장한 \(f\)는 \(H^1(\mathbb R^3)\)에 속한다. 셀 내부 도함수의 jump는 허용되지만 함수 자체의 jump는 허용하지 않는다. 원본의 불연속 저장 표현에 이 전제를 자동 적용하지 않는다.

target의 ETF는 1이며 projectile ETF는

\[
\exp\left[\frac{i m_e}{\hbar}\left(\mathbf v\cdot\mathbf r-\frac{v^2t}{2}\right)\right].
\]

중점 좌표 \(\mathbf x=\mathbf r-\mathbf R/2\)를 쓰면 \(\mathbf v\cdot\mathbf R=v^2t\)이므로 시간 carrier가 정확히 소거된다. 동일 모드 overlap은

\[
S(z)=\int_{\mathbb R^3}
 f(\mathbf x+\mathbf R/2)f(\mathbf x-\mathbf R/2)
 e^{ikx_z}\,d^3x.
\]

1. \(A_{\mathbf R}(\mathbf x)=f(\mathbf x+\mathbf R/2)f(\mathbf x-\mathbf R/2)\)는 \(\mathbf x\mapsto-\mathbf x\)에 대해 짝함수다. 따라서 sine 적분이 사라지고 \(S(z)\)는 실수다.
2. \(z\mapsto-z\)와 \(x_z\mapsto-x_z\)를 함께 적용하면 radial 곱은 같고 ETF는 복소켤레가 된다. 따라서 \(S(-z)=S(z)^*=S(z)\)다.
3. \(H^1\) 함수의 translation은 \(L^2\)에서 미분 가능하고 그 도함수는 translation된 weak gradient다. 유계 ETF와의 내적에 적용하면 \(S\)는 \(C^1\)이다. 따라서 \(dS/dt|_{z=0}=v\,dS/dz|_0=0\)이다.
4. 정의 \(D_{ab}=\langle\chi_a|\dot\chi_b\rangle\)로부터 \(\dot S_{TP}=D_{TP}+D_{PT}^\dagger\)다. target ket은 시간 독립이므로 \(D_{PT}=0\). 결국 **동일 s 모드에 대해 \(D_{TP,ii}(0)=0\)** 이다.

정규화 상수나 에너지 부호는 이 정리에 영향을 주지 않는다. 그러므로 현재 3개 s 모드 i=0,1,2에 모두 적용된다. 서로 다른 radial 모드, 일반적인 p 자기양자수 쌍, z≠0의 모든 D 원소로 확장하지 않는다.

후보의 수정하지 않은 R4X raw 값을 이 정리와 비교하면 다음과 같다. 모든 실수부는 0이며 표에는 허수부를 적었다.

| cross diagonal | Im D32 [ta⁻¹] | Im D40 [ta⁻¹] | 정확 값 |
|---|---:|---:|---:|
| [0,0], 1s | +8.9856764e−17 | −6.2769494e−17 | 0 |
| [1,1], 2s | +1.4120919e−14 | −6.5866290e−16 | 0 |
| [2,2], 양의 에너지 s | +5.1056919558e−4 | +1.6159235294e−4 | 0 |

따라서 [2,2]에서는 두 차수 차이뿐 아니라 각 계산의 **정확한 대칭 기준에 대한 절대 잔차**를 얻는다. 위 정리를 raw D를 0으로 덮어쓰는 절차로 사용하면 안 된다. 독립 진단값으로 저장하고 기존 절대 허용오차와 비교한다. 이 정리는 전 행렬·전 구간 미분 검증이 아니다.

## 4. 횡위상을 직접 제한하는 inner 패널

outer Gauss 노드 \(r_0>0\)를 고정하고

\[
a=r_0\cos\theta,\qquad \rho=r_0\sin\theta,\quad0\le\theta\le\pi,
\quad r_1^2=r_0^2+R^2-2Rr_0\cos\theta
\]

로 둔다. 각 \(\phi\)에서

\[
\left|\frac{d\Phi}{d\theta}\right|
=r_0|-k_\parallel\sin\theta+k_\perp\cos\theta\cos\phi|
\le r_0|\mathbf k|.
\]

따라서 \(\Delta\theta\le\beta/(|\mathbf k|r_0)\)인 패널 안에서는 모든 방위각의 위상 변화가 \(\beta\) 이하다. 이 명제는 직접 미분과 Cauchy–Schwarz에서 얻은 **위상 변화 상계**다. Gauss 적분 오차 상계는 아니다.

구현 후보는 기존 각 inner FEM 패널 [l,h]를 θ 구간으로 변환하고

\[
n=\max\{1,\lceil |\mathbf k|r_0(\theta_h-\theta_l)/\beta\rceil\}
\]

개의 θ 간격으로 나눈 뒤 내부 경계만 r₁로 되돌린다. 원래 l,h bytes는 그대로 보존한다. 내부 경계는 상쇄를 줄이는 동치식

\[
r_1(\theta)=\sqrt{(r_0-R)^2+4Rr_0\sin^2(\theta/2)}
\]

을 사용할 수 있다. 새 각 subpanel 안에서 기존 r₁ Gauss 규칙과 Jacobian \(r_0r_1/R\), 기존 native contraction을 그대로 적용한다. 기저 FEM mesh·계수·FP64·raw D를 바꾸지 않으며 의도적인 quadrature 변경으로 별도 context를 부여해야 한다. 새로운 점 집합은 원래 계산과 bitwise 동일하지 않으므로 기존 quadrature context로 재사용하면 안 된다.

θ 자체를 Gauss 변수로 바꾸면 Jacobian은 \(r_0^2\sin\theta\)가 되지만 이는 별도의 알고리즘 선택이다. 이번 endpoint 분할 설계에는 필요하지 않다. inner 위상 제한만으로 outer 적분 오차까지 제한되지는 않는다. 독립 order·outer 분할 검증이 여전히 필요하다.

## 5. 단순 p/h 증가와 비교

기존 코드는 Gauss 차수 2…64와 균일 subdivision 1,2,4를 허용한다. 차수 증가 자체는 가장 작은 소스 변경이지만 p32/40의 일치 여부만으로 정확도를 추정하지 않는다. 단순 균일 h 분할은 삼각 endpoint 근처의 비선형 \(\rho(r_1)\) 변화를 고르게 제한하지 못한다.

중앙 order40에서 실제 operator를 계산하지 않고 점 개수와 최대 inner κ 범위만 계산한 결과:

| 규칙 | radial pair 점 수 | 최대 inner κ 범위 |
|---|---:|---:|
| 기존 subdivision1 | 720,000 | 128.4941 |
| 기존 subdivision2 | 2,505,600 | 122.9271 |
| 기존 subdivision4 | 9,409,600 | 100.7366 |
| inner θ budget24, 기존 outer | 1,541,560 | 위상 변화 ≤24의 설계값 |
| inner θ budget12, 기존 outer | 2,563,720 | 위상 변화 ≤12의 설계값 |

마지막 두 행은 phase budget의 정확 실수 설계와 FP64 기하에 따른 예상 node count다. 시간·정확도·production 성능 측정이 아니다. ceil 경계 및 극미세 panel 처리는 구현에 따라 정확한 count가 달라질 수 있으므로 실행 전 구현의 count를 다시 고정해야 한다. 기존 subdivision을 4로 늘려도 최대 κ 폭은 100 이상 남는 반면 θ 패널은 실제 어려운 inner 방향을 직접 제어한다.

사전 고정한 유한한 p ladder를 먼저 평가하고, 남는 실패에 대해 β=24와12 및 독립 p 비교를 적용하는 경로가 타당하다. 세 개 동일 s–s 중앙 exactzero 진단을 함께 사용한다. 전체 operator delta, volume, 유한성, identity, 자원 한도 검증은 보존한다. 정확한 지지 교집합 volume 적분은 weight·기하 screen이며 진동하는 integrand의 정확도 증거가 아니다.

이 설계는 새로운 문헌의 외삽 없이 현재 소스에서 직접 유도했다. 입력·소스·8개 R4X raw SHA와 기계 판독 결과는 `THEORY.json`에 있다. 실제 패널 구현, 새 계산 결과, 독립 검토 판정은 별도 실행 근거로 기록해야 한다.
