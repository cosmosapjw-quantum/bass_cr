# C21M 초기응력 사상 — 독립 물리·수학 검토

검토일: 2026-10-21 KST. 범위: REI PR147 source 3b85dedce84d37b3e165da00685a8a984950aafe를 C21L에서 고정한 non-tilted collisionless LRS Bianchi I, \(\eta_0=b_0=0\), \(f_m=0.1\), \(m/T_{\rm ref}=30\), \(\ell_{\max}=8\), canonical FV \(24\times12\), Gauss3. 이 문서는 이론 유도, 원 source 읽기, Wolfram 대수 검산, 초기장 수치 검산을 수행했다. 물리 ODE 재실행은 0회다. 새로운 문헌 신규성/no-go 주장을 하지 않는다.

## 1. source와 성분 의미

실제 읽은 source는 canonical_fv.py SHA256 91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5, species_hierarchy.py SHA256 ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5, C21L adapter.py와 SOURCE_MANIFEST.json이다. 실행 시 nine-entry source manifest를 실제 bytes에 대해 확인했다.

Pi_gamma_J_m3, Pi_nu_J_m3, Pi_matter_J_m3는 Frobenius norm이 아니라 signed \(p_X=\Delta p_X/3\)다. matter는 이 source에서 cold dust 및 nonbaryonic massive Vlasov의 합이고, cold dust의 stress는 source 가정으로 정확히 0이다. massive Vlasov가 실제 matter stress를 담당한다. photon과 massless neutrino는 모두 존재한다. 다른 species의 부재는 수치 0으로 추가하지 않는다.

## 2. 텐서·단위

직교기저에서
\[
 \sigma_{\hat i\hat j}=\operatorname{diag}(-s,-s,2s),\qquad
 \pi^{(X)}_{\hat i\hat j}
 =\operatorname{diag}(-\Delta p_X/3,-\Delta p_X/3,2\Delta p_X/3).
\]
따라서
\[
 |\sigma|_F=\sqrt6\,|s|,\qquad
 |\pi_X|_F=\sqrt{2/3}\,|\Delta p_X|=\sqrt6\,|p_X|,
 \quad \pi_m:\pi_r=\frac23\Delta p_m\Delta p_r.
\]
half-contraction norm은 각각 full Frobenius의 \(1/\sqrt2\)이다.

signed coordinates와 norm을 구분한다:
\[
 {\cal S}=\sqrt6\,s/H_t,\qquad
 {\cal P}_X=\frac{8\pi G}{c^2}\frac{\sqrt6\,p_X}{H_t^2},
 \qquad \Sigma_F=|{\cal S}|,\quad\Pi_{X,F}=|{\cal P}_X|.
\]
source \(H_t\)는 s\(^{-1}\), \(p_X\)는 J m\(^{-3}\)다. \(\kappa_4=8\pi G/c^4\)로 사용자의 식을 쓸 때에는
\[
 \Pi_{X,F}=\frac{\kappa_4|\pi_X|_F}{H_g^2}
 =\frac{\kappa_4c^2|\pi_X|_F}{H_t^2},\quad H_g=H_t/c.
\]
기존 C21L THEORY_KO.md에 이미 이 대응이 정확히 있으며 그대로 재사용한다. \(H_t\)와 \(\kappa_4\)를 조합하면서 \(c^2\)를 생략해서는 안 된다.

## 3. 원 분포에서 얻은 초기 matter moments

이 절의 rho_m은 massive Vlasov sector만의 에너지밀도다. Dust를 포함한 전체 matter 밀도와 구별하며, 아래 초기 밀도식의 f_m=0.1이 이 sector의 비율을 나타낸다. Dust의 anisotropic stress는 source 가정상 0이다.

source canonical weight는
\[
 f_{m,0}(q,\mu)\ \propto\ f_{\rm FD}(q)[1+A P_2(\mu)],
 \quad f_{\rm FD}(q)=\frac{1}{e^q+1},\quad P_2=(3\mu^2-1)/2.
\]
여기서 \(q=pc/(k_BT_{\rm ref})\), \(M=mc^2/(k_BT_{\rm ref})\)라는 dimensionless energy convention으로 해석한다. source는 이 dimensionless ratio를 mass_over_Tref로 보존한다. 초기 metric chart \(b=0\)에서 \(E_*=\sqrt{M^2+q^2}\)가 \(\mu\)와 독립이다.

정규화된 각도 평균 \(\langle g\rangle=\frac12\int_{-1}^1g\,d\mu\)에 대해
\[
 \langle P_2\rangle=0,\quad \langle P_2^2\rangle=1/5,\quad
 \langle\mu^2(1+AP_2)\rangle=1/3+2A/15,\quad
 \langle(1-\mu^2)(1+AP_2)/2\rangle=1/3-A/15.
\]
따라서
\[
 I_\rho(M)=\int_0^\infty q^2 f_{\rm FD}(q)\sqrt{M^2+q^2}\,dq,\qquad
 I_p(M)=\int_0^\infty\frac{q^4 f_{\rm FD}(q)}{\sqrt{M^2+q^2}}\,dq
\]
라고 두면
\[
 \frac{p_{\parallel,m}}{\rho_m}
 =\frac{I_p}{I_\rho}\left(\frac13+\frac{2A}{15}\right),\qquad
 \frac{p_{\perp,m}}{\rho_m}
 =\frac{I_p}{I_\rho}\left(\frac13-\frac{A}{15}\right),
\]
\[
 \frac{\Delta p_m}{\rho_m}=\frac{A}{5}\frac{I_p}{I_\rho},
 \qquad \frac{p_m}{\rho_m}=\frac{A}{15}\frac{I_p}{I_\rho}.
\]
평균 pressure와 총 number/energy normalization은 초기 \(A\)에 독립이다. 비음성은 \(P_2\in[-1/2,1]\)에서 정확히 \(-1\le A\le2\)이다. 경계에서는 연속 분포에 영점이 있고, FD tail의 부동소수점 underflow는 nonnegative zero packet으로 구별한다.

원 코드는 packets, cell_mass, reference_energy_norm, _number_sum을 \(A\)를 사용해 생성한다. 새 \(A\)마다 이를 일관되게 재생성해야 한다. 객체의 amplitude scalar만 바꾸면 moments()가 사용하는 분포는 바뀌지 않는다. 고정 grid 재사용 시에도 새 weights/normalization이 원 constructor와 동등한지 검산해야 한다.

## 4. radiation moments와 독립 초기 사상

초기 photon/neutrino는 각각 \(1+k_XP_2\)이고 source initial state에서 \(E_{X,0}=N_{X,0}=1,\ E_{X,2}=N_{X,2}=k_X/5\). 따라서
\[
 p_X=\frac{\rho_Xk_X}{15},\quad
 \Delta p_X=\frac{\rho_Xk_X}{5}\qquad(X=\gamma,\nu).
\]
수학적 positivity domain \([-1,2]\)보다 좁은 source constructor의 \(|k_X|\le0.5\)를 이번 구현에서 그대로 보존한다. common \(k_\gamma=k_\nu=k\)이면 \(p_r=\rho_rk/15\). photon와 neutrino의 각 tensor/압력은 출력에서 별도 보존한다.

고정 \(a_{\rm ref},f_m\)에서
\[
 \rho_{m,0}=\rho_{\rm crit,0}\frac{f_m\Omega_m}{a_{\rm ref}^3},
 \quad \rho_{r,0}=\rho_{\rm crit,0}\frac{\Omega_r}{a_{\rm ref}^4}.
\]
초기 Hamiltonian constraint는
\[
 H_t^2=H_{\rm FLRW,ref}^2+s^2,\qquad
 q_s=\frac{s}{H_{\rm FLRW,ref}}
 =\frac{{\cal S}_0}{\sqrt{6-{\cal S}_0^2}},
\]
즉 \(|{\cal S}_0|<\sqrt6\). source 인수는 \(\mathrm{Sigma\_ref}=|{\cal S}_0|/\sqrt2\)와 orientation=sign이다. \(A,k\)에 대해 초기 energy normalization이 유지되므로 실제 \(H_0\)는 두 angular amplitudes와 독립이고,
\[
 {\cal P}_{m,0}=B_m({\cal S}_0)A,\quad
 B_m=\frac{\sqrt6H_{\rm today}^2 f_m\Omega_m}
 {5a_{\rm ref}^3H_0^2}\frac{I_p}{I_\rho},
\]
\[
 {\cal P}_{r,0}=B_r({\cal S}_0)k,\quad
 B_r=\frac{\sqrt6H_{\rm today}^2\Omega_r}
 {5a_{\rm ref}^4H_0^2}.
\]
실제 implementation은 고정 quadrature의 아주 작은 \(A=0\) offset을 보존하고, 원 constructor/fields에서 측정한 intercept와 slope를 역변환에 쓴다. 목표값으로 실제 field를 덮어쓰지 않고 재생성된 field와 대조한다. continuum integral는 물리 독립검산용이고 discrete source mapping을 대체하지 않는다.

## 5. 응력 상쇄와 해석

coaxial LRS에서는
\[
 {\cal P}_{\rm tot}={\cal P}_m+{\cal P}_r,\quad
 \Pi_{\rm tot}=|{\cal P}_m+{\cal P}_r|\le\Pi_m+\Pi_r.
\]
signed amplitudes와 tensors를 저장하면 상대 부호가 보존된다. cancellation fraction은
\[
 C=1-\frac{|\Delta p_m+\Delta p_r|}{|\Delta p_m|+|\Delta p_r|}
\]
이며 분모가 양수일 때 정의된다. 분모=0에서는 undefined mask를 별도로 보존한다. 이를 0 또는 1의 물리적 값으로 암묵 치환하지 않는다.

초기 상쇄 \({\cal P}_{m,0}=-{\cal P}_{r,0}\)는 일반적으로 이후의 상쇄를 보장하지 않는다. massive의 momentum speed factor \(I_p/I_\rho\)와 redshift response가 radiation과 다르기 때문이다. 독립 \(({\cal P}_{m,0},{\cal P}_{r,0})\) 입력은 총 initial stress가 같은 경우에도 후속 shear/각분포를 달리 할 수 있는 자유도를 보존한다. 이는 source 방정식 구조의 유도이며 새 run의 정량 결론은 별도로 측정해야 한다.

## 6. 실제 검산과 한계

wolfram_evaluation.json은 Wolfram Language 실제 결과를 보존한다. \(P_2\) 평균, 제곱 평균, 두 압력 모멘트, positivity domain, tensor contractions가 모두 위 식을 반환했다. 도구는 자유기호 S가 정의되지 않았다는 lint 경고를 함께 반환했으나 요청한 symbolic expression 자체는 정확한 식으로 출력했다.

check_initial_moments.py / initial_moments_checks.json은 SciPy 독립 1D radial quadrature와 실제 고정 source 초기 fields를 비교했다. \(M=30\)에서 \(I_p/I_\rho=0.014042977688245462\). \(A=-1,-0.5,0,0.5,1,2\)의 source 초기 \(\Delta p/\rho\)와 continuum 식의 최대 차이는 \(3.4196022749566346\times10^{-12}\). five selected \(({\cal S},A,k)\) 초기장 중 \(|{\cal P}_m-{\cal P}_{m,\mathrm{continuum}}|\le8.321056517435199\times10^{-13}\), radiation formula 차이 \(\le2.168404344971009\times10^{-19}\), shear initial-map 차이 \(\le1.3877787807814457\times10^{-17}\)이다. 실제 tolerance/solver는 receipt에 있다. 이 차이는 별도 continuum/discrete 비교이며 global bound로 사용하지 않는다. ODE 적분과 새 sweep는 이 agent에서 수행하지 않았다.

source initial isotropic matter의 signed residual은 약 \(-2.11\times10^{-19}\) (normalized stress)이다. 구조적 isotropy를 numeric clipping으로 덮지 않고 roundoff-scale residual로 기록한다. 과학 해석의 zero 판정과 저장된 raw sign은 구별한다.

## 7. 1차 문헌의 재사용 범위

1. J. M. Heinzle & C. Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG 23 (2006) 3463–3490, DOI 10.1088/0264-9381/23/10/016, arXiv:gr-qc/0512031. [MPG author manuscript](https://pure.mpg.de/rest/items/item_150627_1/component/file_150626/content), Section 2, Eqs. (2d–f),(3),(4),(8),(12): canonical covariant momentum is conserved; stress components are explicit distribution moments; parity enforces zero momentum density; Hubble normalization includes shear in the Hamiltonian constraint. 원문은 equal-mass Vlasov 및 특정 대칭/regularity 가정으로 서술한다. source FD tail의 지수감쇠는 moment convergence를 직접 보장하며 compact support theorem 전체를 자동 수용하지 않는다.

2. A. D. Rendall & C. Uggla, *Dynamics of spatially homogeneous locally rotationally symmetric solutions of the Einstein–Vlasov equations*, arXiv:gr-qc/0005116. [원문](https://ar5iv.labs.arxiv.org/html/gr-qc/0005116). Massive LRS Einstein–Vlasov의 early massless/late dust asymptotic 연결이 source의 massive stress 희석 해석에 맥락을 제공한다. 이번 finite-redshift 다성분+Lambda 결과에 해당 asymptotic 정리를 직접 적용하지 않는다.

3. S. Calogero & J. M. Heinzle, *Dynamics of Bianchi type I solutions of the Einstein equations with anisotropic matter*, arXiv:0809.1008. [원문](https://arxiv.org/html/0809.1008), Section 2의 Hamiltonian/momentum constraints 및 metric-dependent stress 표현을 읽었다. 뒤의 고정 \(w\) 분류를 massive mixture에 동일하게 적용하지 않는다.

Exa로 1차 원문을 회수하여 읽었다. SciSpace 첫 자연어 질의는 anisotropic dark-energy 논문 등 인접 오탐을 다수 반환했으므로 해당 결과를 새 physics source로 채택하지 않았다. 검색·회수 전체 응답은 현재 회수 작업 폴더에 보존했고, 게시본은 아래 1차 문헌 식별자와 채택 범위 및 직접 검산 결과를 보존한다. 원문 전체를 재배포하지 않는다. 이 작업은 기존 source를 더 넓은 모형으로 교체하지 않고 직접 대응하는 moments와 conservation structure를 재사용한다.

