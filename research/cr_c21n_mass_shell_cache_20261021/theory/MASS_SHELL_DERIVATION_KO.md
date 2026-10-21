# C21N: 원 mass-shell 합의 도함수와 초기 stress 상쇄의 해제

## 1. 이번 기여와 고정 범위

기존 C21M의 125개 저장 trajectory를 그대로 사용한다. 원 source는 REI PR147의
`3b85dedce84d37b3e165da00685a8a984950aafe`이며, non-tilted, collisionless LRS Bianchi I의
40상태계다. 이 문서의 신규 계산은 mass-shell 합의 해석적 도함수와 기존 상태에 대한
정적 평가다. 새 ODE 적분은 0회다. 원 tolerance, momentum/angular resolution,
species, Hamiltonian 또는 RHS를 바꾸지 않는다.

여기서 matter stress는 massive Vlasov 성분이 낸다. 함께 존재하는 dust는 source가
명시적으로 등방적으로 모델링하여 anisotropic stress가 0이다. 아래의 massive
에너지밀도 기호에는 dust를 넣지 않는다. 원 설정은 massive fraction `fm=0.1`,
`mass/Tref=30`, 24 radial cells × 12 angular cells × 각 방향 Gauss order 3이다.
실제로 존재하는 photon과 massless-neutrino stress를 각각 계산하여 radiation으로
더한다. UV·별·완전 결합 H/He history를 새로 넣지 않는다.

문헌의 mass-shell 표현을 재사용하고, 그 표현을 **이 source의 고정 packet 합에 대해
직접 미분**한다. 이 결과를 완전한 triaxial 계, continuum discretization 오차보증,
일반적인 장기 안정성 정리로 승격하지 않는다. `global_error_bound=null`이다.

## 2. 문헌에서 재사용한 것과 직접 유도한 것

Heinzle–Uggla의 [원 논문](https://doi.org/10.1088/0264-9381/23/10/016),
[저자 소속기관 원문](https://pure.mpg.de/rest/items/item_150627_1/component/file_150626/content),
[arXiv gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031)의 식 (2d–f)는 covariant
momentum으로 쓴 Bianchi I Vlasov 에너지밀도와 응력의 mass-shell 적분을 준다.
공간 병진 대칭에 따라 해당 momentum과 초기 분포를 보존하여 현재 metric만으로
moments를 계산하는 표현을 재사용한다. 이것이 원 `CanonicalMomentumFV`의 conserved
packet 구현과 맞닿는 부분이다. 논문의 전역 dynamical-system 정리와 compact-support
가정은 이번 FD 분포·양의 cosmological constant source에 그대로 이식하지 않는다.

문헌의 units는 `c=G=1`이다. 아래 SI 대응과 source별 normalization은 원 코드로
별도로 확인한다. [Rendall gr-qc/9505017](https://arxiv.org/abs/gr-qc/9505017)은
대응 논문의 초록과 서지정보를 확인한 보조 문헌이며, 이번 계산식의 독립적인 원문
검산 근거로 세지 않는다. Exa의 다섯 검색 결과에는 중복 URL이 포함되고 SciSpace의
열 항목에도 같은 논문의 여러 버전이 있다. 이를 서로 다른 다수의 독립 근거로
계산하지 않는다.

Exa는 원문 식의 확인, SciSpace는 같은 원 논문의 서지 교차 확인에 사용했다.
Wolfram LanguageEvaluator의 두 실제 성공 응답은 packet chain rule, 에너지 항등식,
SI 대응, 단일 shell의 초기 jet 대수를 확인한다. 먼저 호출한 Wolfram context 도구의
internal server error도 함께 보존한다. CAS의 성공은 ODE 적분이나 finite-window
remainder의 검증을 의미하지 않는다. 게시용 [evidence/](evidence/)에는 문헌 검색의
query·URL·서지·원 응답 hash를 담은 sanitized receipt와 CAS code/output만 넣는다.
긴 검색 본문이나 fetched 논문 전체는 게시하지 않고 원 tool 응답을 scratch에
보존한다. [EVIDENCE_MANIFEST.json](EVIDENCE_MANIFEST.json)이 게시 파일을 고정한다.
SciSpace의 중복 arXiv DOI 항목이 반환한 2022-03-17은 원 연구의 발표일로 사용하지
않는다. journal 원문 header의 2006-04-28 및 2005년 preprint/received 정보를 구분한다.

## 3. 부호, Frobenius norm, 시간 단위

source의 signed scalar를 다음처럼 쓴다.

\[
\sigma_{\hat i\hat j}=\operatorname{diag}(-s,-s,2s),\qquad
\pi^{(X)}_{\hat i\hat j}=\operatorname{diag}(-p_X,-p_X,2p_X),
\quad p_X=\frac{p_{\parallel,X}-p_{\perp,X}}3.
\]

그러므로 full Frobenius norm은 \(|\sigma|=\sqrt6|s|\),
\(|\pi_X|=\sqrt6|p_X|\)다. `Pi_*_J_m3`라는 source 변수명은 norm이 아니라 이
signed \(p_X\)다. 본 문서와 그림의 signed coordinates는

\[
S=\frac{\sqrt6s}{H_t},\qquad
P_X=\frac{\sqrt6 K_t p_X}{H_t^2},\qquad K_t=\frac{8\pi G}{c^2}.
\]

요청한 scalar norms는 \(\Sigma=|S|\), \(\Pi_X=|P_X|\)이다. source의
half-contraction norm보다 \(\sqrt2\)배 크다. 압력은 J/m³이고 \(H_t\)는 proper time의
s⁻¹이므로 \(K_t\)를 쓴다. 사용자가 정의한 energy-coupling
\(\kappa_E=8\pi G/c^4\), \(H_{\mathrm{geom}}=H_t/c\)로 쓰면
\(\kappa_E|\pi|/H_{\mathrm{geom}}^2=K_t|\pi|/H_t^2\)로 같다.

\(P_r=P_\gamma+P_\nu\), \(P_{\rm tot}=P_m+P_r\)는 부호를 보존한 덧셈이다.
\(\Pi_{\rm tot}=|P_m+P_r|\)를 \(\Pi_m+\Pi_r\)로 바꾸지 않는다. 절댓값은 0에서
미분 가능하지 않을 수 있으므로 이번 도함수와 jet은 모두 **signed coordinates**에
대해 계산한다.

## 4. conserved packet 합을 직접 미분

\(\eta=\ln(a/a_0)\), \(r=e^{-\eta}\), \(v=b'=s/H_t\)로 놓는다. 한 packet의
canonical magnitude \(q\)와 cosine \(\mu\)는 상수다. 원 source의 표현을 따라

\[
u=(rq)^2e^{2b}(1-\mu^2),\qquad
w=(rq)^2e^{-4b}\mu^2,\qquad E=\sqrt{M^2+u+w}
\]

를 정의한다. conserved packet population \(n_j\), 초기 에너지 정규화 \(N_E\)에 대해
\(W_j=r^3n_j/N_E\)라 쓰면

\[
\rho_m=\sum_j W_j E_j,\quad
p_{\perp,m}=\sum_jW_j\frac{u_j}{2E_j},\quad
p_{\parallel,m}=\sum_jW_j\frac{w_j}{E_j}.
\]

여기의 \(\rho_m\)와 pressures는 packet source 내부의 reference-normalized 값이다.
실제 SI matter stress는 원 source의 `_mass_pref`와 `rhocrit_j_m3`를 곱해 얻는다.

\[
u'=(-2+2v)u,\quad w'=(-2-4v)w,\quad
E'=\frac{u'+w'}{2E},\quad W_j'=-3W_j.
\]

따라서 구현한 derivative는

\[
\rho_m'=\sum_jW_j(-3E_j+E_j'),
\]
\[
p_{\perp,m}'=\sum_jW_j
\left[\frac{-3u_j+u_j'}{2E_j}-\frac{u_jE_j'}{2E_j^2}\right],
\]
\[
p_{\parallel,m}'=\sum_jW_j
\left[\frac{-3w_j+w_j'}{E_j}-\frac{w_jE_j'}{E_j^2}\right],\qquad
p_m'=\frac{p_{\parallel,m}'-p_{\perp,m}'}3.
\]

이는 arbitrary admissible \(b,\eta,v\)에서 mass-shell 합의 chain rule이다.
momentum array나 분포를 바꾸지 않는다. 미분 전 \(\rho,p_\perp,p_\parallel\)의
표현과 reduction 순서는 원 source 그대로 유지한다. derivative는 수학적 합의
미분이며 FP rounding 함수 자체의 도함수라는 주장은 하지 않는다.

이 식은 다음 energy conservation identity를 만족해야 한다.

\[
\rho_m'+3(\rho_m+\bar p_m)+6v p_m=0,
\qquad \bar p_m=\frac{2p_{\perp,m}+p_{\parallel,m}}3.
\]

마지막 항은 \(\sigma_{ab}\pi^{ab}/H_t=6vp_m\)이다. factor 3이나 norm의
\(\sqrt2\)를 임의로 끼워 넣지 않는다. collisionless number의 물리적 희석은
\(n'=-3n\)이고 canonical cell numbers는 변하지 않는다.

## 5. 초기 상쇄를 푸는 직접 mass-shell 항

정확히 \(v=0\)인 상태에서는 위 합을 정리하여

\[
p_m'+4p_m=R_m^{\rm packet},\qquad
R_m^{\rm packet}=-\sum_jW_j
\frac{M^2(w_j-u_j/2)}{3E_j^3}
\]

를 얻는다. 이 식은 \(p_m\)으로 나누지 않는다. 따라서 \(A=0\) 또는 극도로 작은
stress에서도 직접 평가할 수 있다. FP64에서는 두 separately reduced pressures의
차와 직접 packet sum의 residual이 남으므로 residual 자체를 보존한다.

초기 \(b_0=v_0=0\)이고 정확한 separable continuum 분포가
\(f_{\rm FD}(q)[1+A P_2(\mu)]\)이며 **\(A\ne0\)**이면 explanatory formula로

\[
p_{m,0}'=(-5+\beta_m)p_{m,0},\qquad
\beta_m=
\frac{\int_0^\infty q^6f_{\rm FD}(q)(M^2+q^2)^{-3/2}\,dq}
     {\int_0^\infty q^4f_{\rm FD}(q)(M^2+q^2)^{-1/2}\,dq},
\quad 0<\beta_m<1
\]

를 쓸 수 있다. \(\beta_m\)는 pressure weight로 평균한 speed squared다.
massless limit에서는 1로, 충분히 비상대론적인 limit에서는 0으로 접근한다.
단, 원 source의 admitted domain은 \(M\ge3\)이므로 \(M=0\)인 새 source 실행은
하지 않았다. 이 limit 설명은 대수적 해석이다.

\(A=0\)인 continuum에서는 anisotropic stress와 mass-release 항이 모두 0이다.
실제 FP64 source의 tiny pressure 차와 direct packet residual을 나누어 \(\beta_m\)를
추정하면 의미 없는 값이 나올 수 있다. 구현에서는 모든 \(A\)에서 위의 **직접 합**을
사용하고 이 비를 만들지 않는다. 실제 center의 residual도 0으로 덮어쓰지 않는다.

초기 shear가 정확히 0이면 원 collisionless radiation hierarchy의 initial angular
transport RHS는 0이다. 물리 pressure의 명시적 \(a^{-4}\)만 남아
\(p_{r,0}'=-4p_{r,0}\)이다. 이보다 일반적인 상태에서는 실제 photon/neutrino
hierarchy RHS의 \(E_2'\)를 사용한다.

## 6. Einstein shear jet: 이상 상쇄와 실제 offset

\(h=H_t'/H_t\)로 쓰면 원 source의 shear equation은

\[
S'=P_{\rm tot}-(3+h)S
\]

이다. \(H_t'\)는 source Hamiltonian을 직접 미분해서 얻는다. source의
\(H_t^2=H_0^2(\rho_{d,n}+\rho_{m,n}+\rho_{r,n}+\Omega_\Lambda)+s^2\)에서
dust derivative \(-3\rho_{d,n}\), 위 massive derivative, 실제 radiation hierarchy
derivative, \(2ss'\)를 모두 포함한다.

초기에 \(S_0=0\)이고 total stress도 **정확히** 상쇄되면

\[
P_{\rm tot,0}'=S_0''=\mathcal R_m,
\qquad
\mathcal R_m=\frac{\sqrt6K_t}{H_{t,0}^2}
\rho_{\rm crit}\,\texttt{mass\_pref}\,R_m^{\rm packet}.
\]

이상적인 separable continuum의 비영 \(A\)에 대해서는

\[
S_0''=-(1-\beta_m)P_{m,0},\qquad
S(\eta)=-\frac12(1-\beta_m)P_{m,0}\eta^2+O(\eta^3).
\]

양의 massive signed stress가 음의 radiation signed stress와 상쇄되면 massive
pressure가 더 빠르게 감소하여 처음 나타나는 total stress와 shear는 음의 방향이다.
반대 부호에서는 반대로 나타난다. 이는 국소 response 해석이며 장기 amplitude나
endpoint를 이 항 하나로 예측한다는 뜻이 아니다.

실제 \(\epsilon=P_{\rm tot,0}\ne0\)인 입력은 별도로

\[
P_{\rm tot,0}'=\mathcal R_m-(4+2h_0)\epsilon,\qquad
S_0''=\mathcal R_m-(7+3h_0)\epsilon
\]

를 갖는다. 원 코드가 Einstein forcing을 normalized stress부터 합하는 순서와
SI component부터 합하는 순서가 다르므로 이 등식에도 FP grouping residual을
명시적으로 남긴다. 실제 local curve에는 원 RHS로 구한 \(S_0'\)와 \(S_0''\)를
사용한다. requested total stress가 0이라는 이유로 \(\epsilon\)이나 \(S_0'\)를
제거하지 않는다.

\(S_0''\)의 일반식에는 \(-h'S_0\)도 포함된다. 현재 함수가 정확히 \(s_0=0\)인
slice에서만 second derivative를 반환하는 이유다. nonzero \(s_0\)에 threshold를
적용하여 이 항을 생략하지 않는다. 함수 `initial_cancellation_jet`는 정확한
`b0 == 0` 및 `s0 == 0`을 요구한다.

\(O(\eta^3)\)는 smooth local system의 형식적 Taylor 차수를 표시한다. 이번에는
3차 coefficient, 수치 remainder bound, 정확도가 보장되는 시간창을 계산하지
않았다. 기존 저장점과의 residual 측정은 [RESULTS_KO.md](RESULTS_KO.md)에 별도로
보고한다.

## 7. 구현·검산의 지위

[mass_shell_derivatives.py](../mass_shell_derivatives.py)는 생산 integrator의 교체품이
아니다. 원 source object를 얕게 복사하여 RHS의 `_nfev` counter 증가를 국소화하고,
FP64 state를 복사하여 읽는다. derivative를 평가하는 동안 momentum 배열을 변경하지
않는다. [test_mass_shell_derivatives.py](../test_mass_shell_derivatives.py)의 focused
receipt는 [mass_shell_derivatives_v1.json](../checks/mass_shell_derivatives_v1.json)이다.

검사는 원 moment bytes, 독립 complex-step chain-rule 평가, finite directional
difference, conservation identity 및 실제-offset jet에 제한한다. derivative의
테스트가 새 full trajectory의 source-vs-reuse bitwise 일치를 입증하는 것은 아니다.
기존 C21L의 세 full trajectory bitwise 검증은 그 역사적 범위를 그대로 유지한다.

기존 HH의 전 시간 shear-path attribution이나 radiation matrix transport reduction과
이 초기 mass-shell jet은 질문과 적용 범위가 다르다. 이번 결과의 전역 novelty를
주장하지 않는다. 문헌·다른 연구의 표현을 재사용하여 현재 frozen source의 해석과
검증 가능성을 높인 것이 이번 단위의 기여다.
