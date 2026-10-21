# C21N mass-shell 도함수와 초기 상쇄 해제의 독립 물리 검토

**판정: `PASS_SCOPED`.** 고정 PR147 source의 유한 packet 합을 미분한 식, matter/radiation 구분, SI 단위, signed shear의 초기 2차 계수는 검토 범위에서 일관된다. 물리적 게시를 막는 결함은 발견하지 않았다. 다만 국소 jet을 전체 시간 구간의 응답 근사나 대체 solver로 승인하지 않는다.

검토자: 독립 협업 agent `/root/external_results`. 이번 검토는 소스·대수·기존 영수증·출력 파일의 결속을 읽어 확인한 것이다. focused 수치 test나 125개 정적 분석을 반복하지 않았고, 신규 ODE·벤치마크도 실행하지 않았다. 전체 입력 hash와 판단은 [INDEPENDENT_PHYSICS_REVIEW.json](INDEPENDENT_PHYSICS_REVIEW.json)에 있다.

## 1. 검토 대상과 source 결속

| 대상 | SHA256 |
|---|---|
| `mass_shell_derivatives.py` | `db108994e96f268e074778a3e763dddc8ca72799541b670aca11bbc728d6ef7c` |
| `analyze_mass_shell_jets.py` | `104d0100a85255a6a419666875c33ce636b737b6e67b60a12aed85aedbf75043` |
| `test_mass_shell_derivatives.py` | `37b07e8cf73a97c61ab00f28bdfa40fdf4714fcdaaa657f12227a068a96b0180` |
| `theory/MASS_SHELL_DERIVATION_KO.md` | `10651fb7c71bad650f1ed3ca004fed2d0181b81f5960e37df76dd534107b8128` |
| `theory/RESULTS_KO.md` | `c0d402bacd9a8cfd9cfc972597717916fc33e2b523088ece6090d1788e88ed8e` |

원 물리 source는 `3b85dedce84d37b3e165da00685a8a984950aafe`다. 원 FV constructor/moments/fields/RHS와 photon/neutrino `SpeciesHierarchy`를 직접 대조했다. 분석은 원 C21M builder를 명시적 file alias로 불러오며 `optimized=False`를 쓴다. C21N 준비 factory로 기존 실행의 provenance를 바꾸지 않는다.

재구성할 (A_m,k_\gamma,k_\nu,\Sigma_{\rm ref},\mathrm{orientation})은 sealed 원 receipt에서 읽는다. 중심은 원 C21L mapping과 (A=0)을 그대로 쓴다. target을 역변환해서 새 source parameter로 덮어쓰지 않는다. 분석 영수증은 125개 초기 state 및 결합 파일의 `eta/Y`가 원 raw와 byte 일치하고, source signed 성분 2,250개의 최대 수치차가 0임을 기록한다. 뒤의 2,250개 비교는 numeric equality이며 byte 검사로 확대하지 않는다.

## 2. 독립 대수 검토

LRS tensor가 (\sigma=\mathrm{diag}(-s,-s,2s)\), (\pi_X=\mathrm{diag}(-p_X,-p_X,2p_X)\)이면 full Frobenius 좌표는

\[
S=\frac{\sqrt6s}{H_t},\qquad
P_X=\frac{\sqrt6K_t p_X}{H_t^2},\qquad
K_t=\frac{8\pi G}{c^2},\qquad p_X=\frac{p_{\parallel,X}-p_{\perp,X}}3.
\]

(K_t\,[\mathrm{J/m^3}])의 차원은 (mathrm{s^{-2}})이므로 proper-time (H_t)를 쓴 좌표는 무차원이다. (\kappa_E=8\pi G/c^4)로 표시하면 (H_{\rm geom}=H_t/c)를 함께 사용한다. scalar norms는 (|S|,|P_X|)이며 source의 half-contraction norm과는 (\sqrt2)배 차이가 난다. 총 stress는 부호를 유지하여 더한 뒤 norm을 취한다.

한 packet에서 (v=b'=s/H_t), (u=p_\perp^2), (w=p_\parallel^2), (E=\sqrt{M^2+u+w}), (W=e^{-3\eta}n/N_E)라 놓으면

\[
u'=(-2+2v)u,\quad w'=(-2-4v)w,\quad
E'=\frac{u'+w'}{2E},\quad W'=-3W.
\]

이를 (\rho=\sum WE), (p_\perp=\sum Wu/(2E)), (p_\parallel=\sum Ww/E)에 적용한 product/quotient rule이 구현의 모든 derivative와 일치한다. 따라서

\[
\rho'+3(\rho+\bar p)+6vp_s=0
\]

가 된다. (6vp_s)는 정확히 (\sigma_{ab}\pi^{ab}/H_t)이며, source에서 사용하는 signed pressure difference의 (1/3)이나 Frobenius 정규화가 빠지지 않았다. canonical packet number는 일정하고 물리 number는 (n'=-3n)으로 희석된다.

정확히 (v=0)일 때

\[
p_s'+4p_s=R_m^{\rm packet}
=-\sum_j W_j\frac{M^2(w_j-u_j/2)}{3E_j^3}
\]

를 얻는다. 직접 합이므로 (A)나 작은 stress로 나눌 필요가 없다. 배열의 `mass_release_at_zero_shear`라는 이름도 이 제한을 보존한다. 비영 shear의 일반 상태에서 이 항을 전체 (p_s')로 쓰면 안 되며, 구현은 별도의 전체 chain rule을 사용한다.

초기 (b_0=v_0=0), separable (f(q)[1+A P_2(\mu)]), **(A\ne0)** 조건에서는

\[
p_{s,0}'=(-5+\beta_m)p_{s,0},\qquad
\beta_m=\frac{\int q^6f(q)E^{-3}\,dq}{\int q^4f(q)E^{-1}\,dq},
\quad 0<\beta_m<1.
\]

따라서 (\mathcal R_m/P_{m,0}=-(1-\beta_m))다. 문서의 부호 설명은 이 형태로 명확히 고쳐졌다. 구현은 이 continuum 비율을 계산식으로 쓰지 않고 fixed-quadrature 합을 직접 미분한다. (A=0) 또는 roundoff-scale center stress를 분모로 (\beta_m)를 추정하지 않는다. massless·비상대론적 극한의 설명도 대수적 해석이며, admitted domain 밖의 질량으로 새 source를 실행했다는 뜻이 아니다.

## 3. Einstein 초기 jet과 실제 offset

Hamiltonian의 미분에는 dust의 (-3\rho_d), massive packet의 (\rho_m'), 실제 radiation hierarchy의 (E_0')와 (a^{-4}) 희석, 전단의 (2ss')가 모두 포함된다. 각 sector의 (P_X')에는 (H_t^{-2}) 미분에서 오는 (-2(H_t'/H_t)P_X)도 들어 있다.

(h=H_t'/H_t)라 쓰면 원 RHS는

\[
S'=P_{\rm tot}-(3+h)S
\]

를 준다. 정확한 (S_0=b_0=0) slice에서 (\epsilon=P_{{\rm tot},0})을 보존하면

\[
P_{{\rm tot},0}'=\mathcal R_m-(4+2h_0)\epsilon,\qquad
S_0''=\mathcal R_m-(7+3h_0)\epsilon.
\]

이때 (S_0=0)이므로 일반식의 (-h'S_0)가 사라진다. 함수는 nonzero shear를 임의 threshold로 0 취급하지 않고, 정확한 `b0 == 0`, `y0[2] == 0`을 요구한다. 이상적인 정확한 상쇄에서만 (S_0''=\mathcal R_m)와 (S\simeq\mathcal R_m\eta^2/2)를 쓸 수 있다.

실제 local curve에는 원 RHS의 (S'_0,S''_0)를 사용한다. source-normalized forcing과 SI component 합 사이의 grouping 차이를 따로 보존하며, requested total stress가 0이라고 실제 offset을 제거하지 않는다. scalar norm의 0에서의 derivative는 계산하지 않는다.

재사용 중심의 (P_{m,0}\simeq-2.11115\times10^{-19}), (P_{r,0}\simeq+2.11115\times10^{-19}) 및 tiny derivative는 보존된다. 중심에서 separately reduced pressure derivative와 직접 mass-release 합의 상대 차이가 커질 수 있지만, 두 값은 모두 roundoff scale이다. 이를 유효 (\beta_m)나 물리적 불안정성으로 해석하지 않는 현재 제한이 맞다.

## 4. 기존 검증과 출력에 대한 수용 범위

focused 영수증은 12개 packet 상태에서 원 moment bytes와 독립 complex-step derivative를 비교하고, 3개 초기상태에서 source 방향도함수, 7개 무전단 입력에서 actual/ideal jet을 검사한다. 관측 최대 절대차는 각각 (4.44\times10^{-16}), (8.74\times10^{-14}), second-derivative 방향 검사 (5.72\times10^{-15})다. 이 수치를 새 trajectory 오차의 상계로 사용하지 않는다.

기존 125개 적용은 packet 상태 12,625개, 원 source RHS 상태 375개, 무전단 초기 jet 25개, 비영 opposing stress 4개에 한정된다. 실제 artifact manifest의 9개 파일 크기·SHA256이 모두 일치함을 별도로 확인했다. CSV 행 수 125·25·375·32도 확인했다. 검토자가 과학 계산을 다시 수행한 것은 아니다.

32개 local-comparison 행을 읽어 summary와 대조한 결과:

| 저장점 | 네 opposing case의 최대 상대 residual |
|---|---:|
| 첫 양의 점, (\eta=0.014350845252893228) | 2.1223365948877245% |
| 마지막 표시 점, (\eta=0.10045591677025259) | 15.837430650182002% |

마지막 점의 최대 절대 residual은 (1.3359691882247187\times10^{-7})다. relative residual은 ((S_{\rm saved}-S_{\rm jet})/S_{\rm saved})이며 비교에는 그 절댓값을 쓴다. (\eta=0)의 ratio 셀이 비어 있음을 확인했고, 작은 분모 floor는 없다.

**이 관측은 1% 정확도나 전체 시간창의 대체 근사로 승격할 근거가 없음을 분명히 한다.** 네 case의 선택된 저장점에서 측정한 차이이며, 연속 시간창의 오차 상계도 아니다. 현재 결과는 초기 응답의 부호와 leading coefficient를 설명하는 데 쓰는 것이 적절하다.

## 5. 제한과 상태

| 축 | 독립 검토 종료 상태 |
|---|---|
| `EXECUTION` | 소스·대수·artifact 감사 `PASS_SCOPED`; 신규 ODE 0, benchmark 0, focused/full-static campaign 재실행 0 |
| `PUBLICATION` | 검토 파일 준비 완료; 검토자는 push하지 않음 |
| `BACKUP` | 검토자는 provider 업로드를 수행하지 않음 |
| `DAG` | mass-shell chain rule과 초기 signed jet 검토 완료; full-window replacement 승인 없음 |

이 검토에서 PNG/PDF를 다시 시각 검사하지 않았다. coordinator의 visual receipt는 별도 근거다. 문헌과 CAS 도구 응답은 theory author가 수집한 자료이고, 이 검토가 별도 문헌 획득을 반복했다고 세지 않는다.

미분 대상은 고정된 유한 packet 합이다. continuum discretization 오차, 다른 source family, triaxial/full reionization/CMB 확장으로 일반화하지 않는다. `third_order_coefficient=null`, `finite_window_remainder_bound=null`, `global_error_bound=null`을 유지한다.
