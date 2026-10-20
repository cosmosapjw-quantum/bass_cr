# C21H: 원본 광학깊이 IVP의 Rust 적분기 연결

## 결과와 적용 범위

C21H는 C21F의 원본 연속방정식과 C21G의 고정 오차 척도를 유지하면서 VigilODE Rodas5P와 Diffsol BDF를 연결하는 단위다. 이 문서는 좌표 척도 변환, 광학깊이 Jacobian의 정확한 열, 수동 장부의 영 열, 사건 구간 안의 시간 편미분을 유도한다. 이 유도는 물리식의 동일성을 확인하는 계약이며, 새 native 실행의 수치 수렴 판정은 해당 실행 자료에 남긴다.

재사용한 소스는 `bass_cr@e742d44f605c51c06615451774ba90af8f41f622`의 `research/cr_c21e_event_native_20261018/src/reference_tau.py`와 같은 디렉터리의 `event_coupler.py`, `run_experiment.py`, 그리고 C21G `campaign_contract.py`다. 광학깊이 소스 SHA256은 `714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0`이다. Native owner는 `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`로 유지한다. VigilODE의 초기 읽기 head는 PR71의 `0bab431e1031f86eb3ddb44371240bce49ae2376`이고, bridge 실행 소스는 측정된 Run2 commit `8a8bd409b1d96c7b7421f496d229e119fd3d284e`에 고정한다. 이 문서가 사용하는 norms/problem/adaptive/fast 네 파일은 두 head의 Git blob·SHA256이 모두 같다. 실제 실행 revision에서 새로 읽은 `COMPILE_SOURCE_BINDING.json`이 이 대응을 확인한다.

이번 단위의 해석적 결과는 아래 식들이다. 최초 native 실행, 공통 달성 정확도에서의 성능 비교, 전역 오차 상계는 각각 별도 의무다. C21G의 기존 8개 reference와 조건부 4개 time-refinement 실행 계획을 C21H 완료로 대체하지 않는다. Full48, source-age/spectral/angular, Case B, Bianchi, full EoR의 기존 HOLD는 유지한다.

## 1. 고정 물리계와 상태

독립변수는 \(x=\ln a\)다. 광자 cohort 수를 \(M\), 가스 상태를 \(g=(X_{\rm HII},X_{\rm HeII},X_{\rm HeIII},w)\)로 쓴다. \(w\)는 전체 수소핵 한 개당 열에너지이며 단위는 eV/H다. \(Y=n_{\rm He}/n_{\rm H}\)는 고정한다. 전 상태의 순서는

\[
y=(\tau_1,\ldots,\tau_M,g,\ell),\qquad \dim y=M+19,
\]

이며 \(\ell\)은 photo/ci/rr 각 3개, dr 1개, escape/cmb/photon work/gas work/heat 각 1개의 총 15개 장부다. \(Y=0\)일 때 고정된 두 He 분율의 행·열·오차 척도만 정확히 제거하여 동적 가스 차원은 2가 된다. 수동 장부는 오차 제어에 계속 포함한다.

한 birth/cross-section 사건 구간 \([l,u]\)에서 cohort 활성 집합은 \(b_i\le l\)로 고정한다. 원본 코드의 epoch 샘플링은

\[
\Delta=u-l,\quad L=l+10^{-9}\Delta,\quad U=u-10^{-9}\Delta,
\qquad \chi(x)=\min\{\max\{x,L\},U\}
\]

이다. \(L,U\)는 원본과 같은 binary64 연산으로 생성한다. 허용 조건은 표현된 값에 대한 \(l\le L<U\le u\)다. 작은 \(10^{-9}\Delta\)가 해당 epoch의 ulp보다 작으면 \(L=l\) 또는 \(U=u\)가 될 수 있으므로 엄격한 끝점 inset을 요구하지 않는다. 이때도 원래 clamp 값과 정확한 corner의 0 편미분 convention을 유지하며, 내부 차분에 서로 다른 표현 가능한 노드가 없으면 명시적으로 실패한다.

가스 상태와 적분 시각은 원래 \(x\)를 유지하고 provider epoch, opacity, \(H\)만 \(\chi(x)\)를 사용한다. 새로운 어댑터가 이 clamp를 변경하면 C21G와 다른 RHS가 되므로 현재 연결에서는 이를 유지한다.

활성이고 \(A_i>0\)인 cohort에 대해

\[
N_i=A_i e^{-\tau_i},\qquad
\log N_i=\log A_i-\tau_i.
\]

비활성 cohort와 원래 \(A_i=0\)인 cohort는 구조적 0이다. binary64 복원에서 양의 cohort가 underflow하면 \(N_i=0\)과 유한한 log survivor를 함께 기록한다. 그 값을 양의 epsilon으로 대체하지 않는다. 원본에서 허용된 암묵적 내부 단계의 음의 \(\tau\)에 대한 해석적 연장도 유지한다. accepted state의 \(\tau\ge0\) 검사는 별도다.

흡수종 \(s=({\rm HI,HeI,HeII})\)에 대해

\[
\alpha(g)=(1-X_{\rm HII},\,Y(1-X_{\rm HeII}-X_{\rm HeIII}),\,YX_{\rm HeII}),
\]

\[
h_{is}=k_{is}(\chi)\alpha_s(g),\quad
r_{is}=N_i h_{is},\quad R_s=\sum_i r_{is},\quad
Q_i=\sum_s r_{is}(E_i(\chi)-B_s).
\]

여기서 \(h_{is}\)는 proper-second hazard이고 \(H\)도 proper-second 역수이므로 \(\tau_i'=\sum_s h_{is}/H\)는 무차원이다. 원본의 식은

\[
\tau_i'=\mathbf1_{\{b_i\le l\}}\frac{\sum_s h_{is}}{H},
\quad g_{\rm frac}'=\frac{\mathcal S_Y(R)+m_{\rm frac}}H,
\quad w'=\frac{\sum_iQ_i+m_w}H-2w,
\]

이다. \(\mathcal S_Y(R)=(R_H,(R_{HeI}-R_{HeII})/Y,R_{HeII}/Y)\)이고 \(Y=0\)에서는 He 사건이 정확히 0인 상태의 H 성분만 남긴다. \(m\)은 원래 non-photo native provider의 반환값이다. 흡수율, cross-section, 배경 \(H\), source births, 가스 상태 정의를 새 Rust 패키지의 관례에 맞춰 바꾸지 않는다.

## 2. 고정 대각 척도와 오차 노름

C21G가 fixture에서 정한 양의 대각 척도를 \(D=\operatorname{diag}(D_i)\)로 쓴다. \(\tau\), 가스 분율, 사건 수 장부의 척도는 1, 열에너지 척도는 \(w_0>0\), 다섯 에너지 장부의 척도는

\[
S_E=w_0+b(Y)\cdot g_{0,\rm frac}+\sum_i A_iq_i e^{-b_i},
\quad
b(Y)=(B_H,YB_{HeI},Y(B_{HeI}+B_{HeII})).
\]

즉 모든 고정 birth의 광자 에너지를 사용하는 초기 fixture 척도이며, 현재 state에 따라 갱신하는 floor가 아니다. \(y=Dz\)로 바꾸면

\[
z'=\widehat F(x,z)=D^{-1}F(x,Dz),\quad
J_z=D^{-1}J_yD,\quad
\widehat F_x=D^{-1}F_x.
\tag{1}
\]

\(D\)가 시간과 상태에 독립이므로 추가 \(D'\) 항은 없다. \(a_i=\alpha D_i\)이고 \(e_y=D e_z\)일 때

\[
\frac{(e_y)_i}{a_i+r\max(|y_i^{(0)}|,|y_i^{(1)}|)}
=
\frac{(e_z)_i}{\alpha+r\max(|z_i^{(0)}|,|z_i^{(1)}|)}.
\tag{2}
\]

따라서 같은 상태쌍·같은 오차벡터·같은 동적 좌표 집합에 대한 WRMS는 대수적으로 같다. \(Y=0\)의 두 고정 He unknown을 제거한 차원을 양쪽 평균의 분모에 사용해야 한다. 고정된 0 두 개를 남긴 큰 차원의 RMS는 다른 norm이다.

VigilODE의 고정 소스 `rodas5p-core/src/norms.rs`는 (2)의 old/new 최대값 분모와 성분 수로 나눈 RMS를 사용한다. Fast driver의 `AdaptiveStepConfig`는 scalar atol을 받으므로 (1)–(2)가 C21G vector atol을 연결하는 정확한 좌표 계약이 된다. 같은 control 숫자를 사용해도 서로 다른 알고리즘의 stage, embedded error, Newton 종료 기준, Jacobian 재사용, step controller는 다르다. 실수 연산의 동등성은 binary64에서 상태 변환·LU pivot 선택·roundoff까지 동일하다는 주장을 포함하지 않는다.

Diffsol 0.17.1은 `diffsol-la` 0.2.0을 요구한다. 해당 `FaerVec::squared_norm`의 실제 코드는 한 batch에서

\[
\frac1n\sum_i\left(\frac{e_i}{a_i+r|y_i|}\right)^2
\tag{3}
\]

를 계산한다. BDF `error_control`은 현재 `state.y`와 order별 error constant를 사용한다. 일반 trait 설명에서 생략된 \(1/n\)은 실제 faer 구현에서 확인했다. (3) 역시 고정 \(D\) 변환에서 보존되지만 VigilODE의 old/new 최대 분모와는 다른 backend 관례다. 이 차이를 없애기 위해 tolerance를 몰래 조정하지 않는다. 외부 비교는 공통 물리 상태·공통 출력 시각·공통 C21G 정규화에서 다시 계산한다. [Diffsol BDF 소스](https://docs.rs/diffsol/0.17.1/src/diffsol/ode_solver/bdf.rs.html), [Diffsol Cargo 의존성](https://docs.rs/crate/diffsol/0.17.1/source/Cargo.toml), [faer norm 구현](https://docs.rs/diffsol-la/0.2.0/src/diffsol_la/vector/faer_serial.rs.html).

## 3. Jacobian의 정확한 구조

고정된 \(x,g\)에서 \(\partial N_i/\partial\tau_j=-\delta_{ij}N_i\)다. \(k,\alpha,H\)는 \(\tau\)와 독립이므로 활성 cohort \(i\)의 열은 다음과 같다.

| 출력 행 | \(\partial F/\partial\tau_i\) |
|---|---|
| 모든 광학깊이 | 0 |
| 가스 분율 | \(-\mathcal S_Y(r_i)/H\) |
| 열에너지 | \(-Q_i/H\) |
| photo 사건 장부 | \(-r_i/H\) |
| ci, rr, dr, escape, cmb | 0 |
| photon work | \(-N_iE_i\) |
| gas work | 0 |
| photo heat | \(-Q_i/H\) |

비활성·구조적 0 cohort의 열은 0이다. Underflow된 복원값을 쓰는 경우 반환된 double 값의 열은 해당 0을 유지하며, log survivor 정보는 별도로 보존한다. 이 표는 가스 미시물리의 해석 미분을 필요로 하지 않는다.

어느 RHS도 수동 장부 \(\ell\)의 현재 값을 사용하지 않는다. 따라서 그 15개 Jacobian 열은 정확히 0이다. 가스 4개 열(\(Y=0\)에서는 2개)은 원본 RHS/provider를 물리 영역 안에서 차분한다. 이 열은 수치 미분으로 명시하고 전체 Jacobian을 analytic Jacobian이라고 부르지 않는다. 원본 provider는 음의 population, 분율 범위 위반, 비양의 \(w\)를 임의 투영하지 않으므로 FD 노드도 이 영역을 지켜야 한다.

상태 순서를 \((\tau,g,\ell)\)로 보면

\[
J=\begin{pmatrix}0&A&0\\B&C&0\\P&Q&0\end{pmatrix}.
\tag{4}
\]

이 구조는 provider 호출을 불필요한 passive/\(\tau\) 열에 쓰지 않는 근거다. 선택한 Rust solver가 요구하는 dense 행렬은 이 열들을 조합해 제공한다. 순수 JVP 경로는 이 같은 행렬의 곱을 사용할 수 있다. Diffsol의 자동 sparsity 추론은 NaN probe와 상태 의존 분기에서 별도 계약이 필요하므로 현재 dense faer 연결에 자동 coloring을 추가하지 않는다.

### 후속 최적화에 사용할 수 있는 Schur 소거

선형 solve \((I-cJ)k=b\)에 (4)를 넣으면

\[
(I_G-cC-c^2BA)k_g=b_g+cB b_\tau,
\]
\[
k_\tau=b_\tau+cAk_g,\qquad
k_\ell=b_\ell+cPk_\tau+cQk_g.
\tag{5}
\]

이는 행렬곱의 순서를 유지한 직접 소거다. \(I_G-cC-c^2BA\)가 가역일 때 (5)는 원래 전체 solve와 동등하다. \(G=4\) 또는 2이므로 전문 선형 solver를 추가할 때 유용한 정확한 연결식이다. 현재 dense bridge가 이 Schur solve를 구현하거나 속도 이득을 측정했다는 뜻은 아니다. 새 구현이 필요하면 독립 후속 단위에서 같은 물리식·선형 residual·실제 비용으로 평가한다. Wolfram의 비가환 블록 순서를 보존하는 7차원 유리수 예제는 residual 7개 모두 정확히 0을 반환했다.

## 4. 사건 경계와 비자율 시간 편미분

Rosenbrock–Wanner 단계는 일반적으로 \(h^2\gamma_iF_x\) 항을 포함한다. Steinebach의 Rodas5P 원전 식 (1.2)–(1.3)에 이 항과 \(F_y,F_x\)의 정의가 명시되어 있다. 따라서 가스 상태가 고정되어 있어도 \(a,n_H,E,H\)가 변하는 현재 IVP를 autonomous로 선언할 수 없다. [Steinebach 2023, BIT 63:27](https://link.springer.com/article/10.1007/s10543-023-00967-x).

고정 VigilODE `OdeProblem::eval_partial_t`는 callback이 없으면 \(\sqrt\epsilon\max(1,|x|)\)로 \(x\pm h\)를 샘플한다. 이 일반 중앙차분은 현재 event interval과 clamp의 구간 정의를 알지 못한다. C21H는 명시적 partial-time callback을 전달해 사건의 다른 쪽을 샘플하지 않는다.

중요한 점은 실제 미분 대상이 \(F_c(x,y)=F_0(\chi(x),y)\)라는 것이다. \(x<L\) 또는 \(x>U\)에서는 epoch가 상수이므로

\[
\partial_xF_c=0.
\tag{6}
\]

특히 interval 시작 \(x=l\)에서 \(L\) 너머의 forward node를 사용하면 underlying \(F_0\)의 기울기를 얻지만, 실제 clamped RHS의 시간 편미분 (6)과 다르다. \(L,U\)의 두 corner에서는 일반적으로 양측 미분이 존재하지 않으므로, 정확히 그 represented 값에서는 plateau 쪽의 0을 반환하는 branch convention을 기록한다. \(L<x<U\)에서만 모든 노드를 \([L,U]\) 안에 둔 차분을 수행한다. 기존 clamp가 만든 미분 불연속을 보존하므로, 전체 interval에서 다섯 번 미분 가능한 RHS에 대한 고전적 5차 정리를 그대로 적용하지 않는다. 실제 달성 정확도는 reference/mesh ladder로 판정한다.

가스 성분별 허용 차분 구간은 다음과 같다.

| 가스 성분 | 다른 성분을 고정한 허용 구간 |
|---|---|
| \(X_{\rm HII}\) | \([0,1]\) |
| \(X_{\rm HeII}\) | \([0,1-X_{\rm HeIII}]\) |
| \(X_{\rm HeIII}\) | \([0,1-X_{\rm HeII}]\) |
| \(w\) | \((0,\infty)\) |

예를 들어 simplex corner에서 한 성분의 허용 폭이 0이면 해당 열을 0으로 추정할 근거가 없다. 두 개의 구별되는 유효 차분 노드를 구성할 수 없으면 명시적인 미분 입력 실패를 반환한다. 내부 solver의 물리 영역 위반과 이를 구분해 기록한다.

### 실제 부동소수점 노드의 3점 차분

평가점 \(x_0\)와 실제 represented 노드 \(x_1,x_2\)를 사용하고 \(h_1=x_1-x_0\), \(h_2=x_2-x_0\)로 둔다. 세 값이 구별되고 \(h_1h_2(h_2-h_1)\ne0\)이면

\[
w_0=-\frac{h_1+h_2}{h_1h_2},\quad
w_1=\frac{h_2}{h_1(h_2-h_1)},\quad
w_2=-\frac{h_1}{h_2(h_2-h_1)}.
\tag{7}
\]

이 계수는 \(\sum_j w_j=0\), \(\sum_jw_jh_j=1\), \(\sum_jw_jh_j^2=0\)을 만족한다. 절대 좌표가 크고 간격이 작을 때에는 \(w_0F_0+w_1F_1+w_2F_2\)보다

\[
\frac{(h_2/h_1)(F_1-F_0)-(h_1/h_2)(F_2-F_0)}{h_2-h_1}
\tag{8}
\]

로 평가해 큰 공통 \(F_0\)의 상쇄를 줄일 수 있다. 중앙·전진·후진 스텐실에 같은 식을 사용한다. 요청한 간격이 아니라 실제 생성한 \(h_1,h_2\)로 계산한다.

현재 구현의 nominal gas 간격은 \(\epsilon^{1/3}\max(|u_j|,D_j)\), nominal 시간 간격은 \(10^{-4}(u-l)\)이다. 매번 중앙 스텐실을 먼저 시도하고, 물리 영역 안에 유효한 한쪽 스텐실이 있으면 그것을 사용한다. 최대 24개 halving level에서 실제 노드를 검사한다. 시간 노드는 열린 구간 \((L,U)\) 안에 둔다. 요청한 FD control과 사용한 actual node는 실행 증거에서 함께 읽는다.

노드 구간에서 \(F\in C^3\)이고 함수 평가 오차가 \(\delta F_j\)라면 성분별 오차는

\[
|\widehat F'-F'|\le\frac{|h_1h_2|}{6}\sup|F'''|+
\sum_j|w_j|\,|\delta F_j|
\tag{9}
\]

로 분해할 수 있다. 세 번째 moment가 \(-h_1h_2\)라는 계산에서 절단 오차가 나온다. 현재 native table/provider에 필요한 고계 도함수와 평가 오차 상계를 계산한 것은 아니므로, (9)의 식 자체와 이번 데이터의 실측 오차 상계는 구별한다. h와 h/2를 바꾼 경량 점검은 FD 민감도를 알려 주며 전역 오차 인증으로 승격하지 않는다.

## 5. Rust 패키지의 역할과 채택 이유

| 후보 | 실제 확인한 기능 | C21H에서의 역할과 판정 |
|---|---|---|
| VigilODE `rodas5p-integrators`, `rodas5p-core` @ `8a8bd409…` | Rodas5P fast, 명시 RHS/Jacobian/partial-time callback, step/callback counters, old/new WRMS; 초기 PR71 읽기와 필요한 source bytes 동일 | 사용자 저장소의 해당 core와 callback 경로를 직접 활용하는 주 backend. 현재 물리 IVP의 새 native 결과는 별도 실행으로 얻는다. |
| Diffsol `=0.17.1`, faer backend | BDF/NDF, implicit RHS/JVP closure, vector 또는 scalar atol, stop time, solver statistics | 다른 stiff 알고리즘의 비교 backend. 동일한 C21F callback과 고정 척도를 사용한다. BDF 재시작과 rolling stop 정책은 실행 계약에 기록한다. |
| faer `0.24.4` | dense/sparse LU 및 행렬 추상화 | VigilODE 고정 workspace가 사용하는 선형대수 구현. Diffsol 내부 resolved 버전은 실제 Cargo.lock으로 별도 확인한다. C21H의 크기에서 GPU/희소화 가속을 가정하지 않는다. |
| `ode_solvers` 공식 문서의 Dopri5/Dop853/RK4 | 명시적 Runge–Kutta 적분기 | 이번 stiff-native 주 비교에는 추가하지 않는다. 작은 비강성 제조 예제에 쓸 수 있으나 현재 요구에 맞는 implicit 비교는 Diffsol로 충족한다. |

Diffsol의 `DiffSL`/Enzyme 경로는 식 전체를 해당 DSL로 옮기거나 그 컴파일러의 미분 가능한 표현으로 제공해야 한다. 현재 원본 Rust native provider가 process callback을 통해 공급되므로 AD 패키지를 의존성에 넣는 것만으로 native 미시물리 Jacobian이 생기지 않는다. C21H는 광학깊이 열의 해석식과 원 provider에 대한 가스 차분을 실제로 구현할 수 있는 경로로 선택한다. [Diffsol 0.17.1 공식 문서](https://docs.rs/diffsol/0.17.1/diffsol/), [faer 0.24.4 공식 문서](https://docs.rs/faer/0.24.4/faer/), [ode_solvers 공식 문서](https://docs.rs/ode_solvers/latest/ode_solvers/).

과거 A07의 Diffsol 0.16.1 Robertson 실행은 동일 명목 tolerance의 accuracy gate가 FAIL인 별도 역사 자료다. 이는 0.17.1 또는 C21H fixture의 결과를 결정하지 않으며 그대로 보존한다. 같은 tolerance와 같은 process exit가 공통 달성 정확도를 뜻하지 않으므로 C21H는 실행 성공, 물리 수지, 수치 차이, 작업 비용을 별도 항목으로 반환한다.

## 6. 검증과 다음 판정

이번 유도는 Wolfram으로 (2)의 성분 비율 차이가 0, \(\partial_\tau(Ae^{-\tau})+Ae^{-\tau}=0\), (7)의 0/1/0 moment, 세 번째 moment \(-h_1h_2\)를 확인했다. 첫 symbolic 조회의 CAS 경고와 root의 별도 초기 syntax failure는 실제 상태로 보존한다. 7차원 유리수 Schur 예제의 전체 residual은 정확히 0이었다. 이러한 기호 검산의 범위는 `WOLFRAM_VERIFICATION.json`에 정리한다.

어댑터 검증은 원본 callback과 같은 fixture/state에서의 RHS 동등성, 광학깊이 열과 수동 열, Y=0 축소, domain 경계 FD, clamp plateau/corner, malformed result 및 callback 실패의 보존을 다룬다. 제조 예제의 wiring 성공과 실제 native 화학 실행은 별도 상태다. 속도 주장은 같은 admitted host에서 동일 출력 조건과 공통 달성 정확도가 확인된 뒤에 작성한다. 이 단위의 전역 오차 상계 필드는 `null`을 유지한다.

새 no-go 또는 새 stiff 적분법을 주장하지 않는다. 연구 기여는 기존 정확한 광자 좌표, 원 microphysics, 패키지의 실제 callback/norm 계약을 연결하고, 그 연결에서 필요한 Jacobian·시간 미분·검증 범위를 명시하여 실행 가능한 비교를 만드는 데 있다.
