# C22D: H1 유한 CI, 공통 에너지 기준, 저밀도 채택 계약

작성일: 2026-10-22 UTC. 연구 규약 **physmath-research-loop 1.0.0 / approval 0.2**. 이 문서는 독립 이론·원자료 하위 작업의 결과다. **새 ODE 0, 기존 완료 ODE 재실행 0, 기존 동결 파일 변경 0**. 새 CI scalar 계산과 기존 저장 상태에서 바뀌는 의존성만 읽었다. C22D 전체 실행·게시·백업 authority는 부모 작업의 실제 영수증으로 확정해야 한다.

## 1. 구현에 전달한 결정

새 C22D 모델은 H1 바닥상태 CI의 **CCC 원자료 유한 기여**를 추가한다. 모델 에너지 기준은 CCC TICS의 13.6058 eV와 맞춘다. 기존 전자율 동일성 근사를 유지하는 H1/D/T 공통 HI family의 binding increment, PI support와 PI heat, RR export를 같은 기준으로 바꾸고, CI의 thermal loss에도 같은 수치를 쓴다. 이 선택은 **서로 다른 원자료의 근사를 명시적으로 결합한 새 모델 계약**이다. 실제 H1의 정밀 이온화 에너지로 개선했다는 주장이 아니다.

기본 CI 단면적은 실제 87개 점 사이의 양성 piecewise linear(PL) 모형이다. 첫 0.0342 eV 구간만 문턱 지수 1.127로 바꾼 모형은 별도 sensitivity다. 온도는 수학적으로 T>0, float64 공급자에서는 1–10⁸ K, 부모의 공통 RR·여기 closure가 활성화되는 C22D에서는 **3–20,000 K**로 구분한다. 이 하위 작업은 등록된 새 C22D trajectory를 만들지 않았다.

추가 반응은 H1에만 적용한다. H1/D/T의 population을 명시적으로 유지하며, H1-only CI를 H+D+T 총량에 적용하지 않는다. CI 사건 counter 하나를 독립 적분하여 전하 ledger에 추가한다. (U=(3/2)k_BNT)의 U를 적분하는 기존 구조를 유지하면 (-TN'/N)은 자동으로 포함되므로 별도 온도 보정 항을 중복 추가하지 않는다.

## 2. 실제 원자료와 가까운 1차 문헌

### 2.1 CCC 선택 bytes

[Curtin CCC 저자 목록](https://atom.curtin.edu.au/CCC-WWW/index.html)을 이번에도 직접 조회했다. H I 항목은 August 2026 자료와 [원 archive](https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/e-H_XSEC_LS.zip)를 연결한다. archive 전체는 다시 내려받거나 원 계산을 재실행하지 않았다. 이미 검증되어 보존된 선택 TICS bytes를 읽고 SHA를 확인하여 새 provider에 결속했다.

| 항목 | 확인한 실제 값 |
|---|---|
| 선택 파일 | `sources/CCC_TICS_1S.txt` |
| 크기 / SHA256 | 5,754 bytes / `7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae` |
| 행 수 | 87 |
| 문턱 행 | E=13.6058000 eV, σ=0 |
| 첫 비영점 | E=13.6400 eV, σ=0.002420 a₀² |
| 마지막 행 | E=968.61 eV, σ=0.4017 a₀² |
| tabulated 최대 σ | 2.167 a₀²; 표 밖 상한으로 사용하지 않음 |
| 표 단위 | 입사 전자 에너지 eV, total ionization cross section a₀² |
| 추가 multiplicity | π 또는 두 outgoing electron의 2를 추가하지 않음 |

원 README는 TICS를 양의 에너지 최종 상태들의 cross section 합으로 설명한다. `asym` 열은 이 스핀 평균 total rate에 사용하지 않는다. 전자 두 개가 나오는 화학양론과 두 번의 사건을 세는 것은 다르다. 각 CI 사건은 H1 원자 하나를 이온화하며 자유전자 순증가는 하나다. archive bytes와 선택 member의 이전 CRC 검증 범위는 C22C source receipt를 재사용하고, 이것을 전체 archive 물리 감사로 확대하지 않는다.

### 2.2 Wannier, CCC near-threshold, SW91의 역할

이번에 Exa와 SciSpace를 실제 호출했다. Exa는 Wannier 및 독립 near-threshold 논문을, SciSpace는 **Bray, Bray, Fursa & Kadyrov (2018), PRL 121, 203401**을 회수했다. [2018 APS 원전 초록](https://link.aps.org/doi/10.1103/PhysRevLett.121.203401)을 직접 열어 확인했다. 이 논문은 양자 CCC 계산의 전자 충돌 문턱 거동이 excess energy의 1.127 power와 양립함을 다룬다. 이 결과를 유한 표 전체에 동일한 power law를 적용할 근거로 사용하지 않는다.

[Wannier (1953), Phys. Rev. 90, 817](https://link.aps.org/doi/10.1103/PhysRev.90.817)의 원전 초록은 원자 문턱의 1.127 지수와 유도의 ergodicity 가정을 명시한다. 원전 전문은 읽지 못했으므로 전문의 완전한 증명을 재현했다고 주장하지 않는다. [Bartlett & Stelbovics (2004), PRL 93, 233201](https://link.aps.org/doi/10.1103/PhysRevLett.93.233201)의 원전 초록은 full Schrödinger equation 계산으로 지수 1.122±0.015를 제시한다. 별도의 collinear/Temkin–Poet 부분모형 결과와 이 full problem 결과를 합치지 않는다. 두 APS 초록은 Exa fetch로 수식까지 읽었다.

[Scholz & Walters (1991), ApJ 380, 302–306, DOI10.1086/170587](https://articles.adsabs.harvard.edu/pdf/1991ApJ...380..302S)은 기존에 확보한 원문 PDF와 p303·p304 이미지에서 직접 다시 필요한 CI 부분을 판독했다. 새 HTTP open 실패는 기존 실제 bytes 접근 실패와 같지 않다. p303 Eq5는

\[
\sigma_{\rm SW,gap}(E)=1.179\,(E/{\rm Ry}-1)^{1.127}\pi a_0^2,
\qquad 1\le E/{\rm Ry}\le1.073.
\]

이는 Shah et al.의 가장 낮은 실험점 1.073 Ry 아래에서 사용한 독립 문턱 모형이다. **CCC 표의 a₀²와 SW91의 πa₀²를 실제로 구별**했다. p304 Table2의 CI 계수 7개를 읽었고 Eq6·Eq9·Eq10의 Boltzmann factor와 (y=\ln(T/{\rm K}))를 적용했다. Table3 excitation 계수나 Table4 total cooling 계수와 섞지 않았다. CI 전체 fit은 원문 범위 **2,000–10⁸ K**에서만 비교했다. 그 아래 온도에는 Eq5의 명시된 유한 에너지 적분만 비교하며 전체 fit을 외삽하지 않는다.

SW91의 1 Ry를 eV로 표시하기 위해 [NIST CODATA 2022 Rydberg energy](https://physics.nist.gov/cuu/Constants/)의 13.605693122990 eV를 명시적으로 사용했다. 이 수치는 원 논문이 적지 않은 자릿수까지 그 논문의 역사적 상수라고 주장하는 것이 아니다. CCC 13.6058 eV를 몰래 SW91 문턱에 복사하지 않았으므로 극저온 비교에는 이 작은 문턱 차이의 Boltzmann 효과도 들어 있다.

## 3. 유한 CI 적분과 차원·양성성

Maxwell 전자 분포, 원자료의 입사 전자 질량 convention, 비상대론적 전자를 가정한다. 전자 에너지를 eV로 쓴 E, θ=kBT[eV], 단면적의 a₀² 단위 수치를 s(E)라 하면

\[
q_{\rm core}(T)=K\theta^{-3/2}
\int_{13.6058}^{968.61}s_{\rm PL}(E)E e^{-E/\theta}\,dE,
\quad K=10^6a_0^2\sqrt{\frac{8e_{\rm J}}{\pi m_e}}.
\]

SI 식 (\sqrt{8/(\pi m_e)}(k_BT)^{-3/2}\int\sigma(E_J)E_Je^{-E_J/k_BT}dE_J)에서 단위 변환을 독립적으로 계산했다. 최종 q의 단위는 cm³/s다. Maxwell 정규화의 π는 원자료 단면적 단위의 π와 별개다.

구간 (E=L+dt), (0\le t\le1), (y=d/\theta)에서 이미 C22C가 검증한 양성 endpoint identity를 재사용한다.

\[
J_n(y)=\int_0^1t^n e^{-yt}dt,
\quad w_L=L(J_0-J_1)+d(J_1-J_2),
\quad w_R=LJ_1+dJ_2,
\]
\[
S(\theta)=\sum_i d_i e^{-(L_i-\chi)/\theta}
(s_iw_{L,i}+s_{i+1}w_{R,i}),
\quad \ln q=\ln K-\tfrac32\ln\theta-\chi/\theta+\ln S.
\]

두 weight는 각각 양의 함수 ((1-t)(L+dt)e^{-yt}), (t(L+dt)e^{-yt})의 적분이다. 따라서 음이 아닌 source endpoint에 대한 모든 구간 기여가 음이 아니며, 유한 T>0에서 총 선택 core는 양수다. 기울기와 절편의 큰 상쇄를 피하고, 저온에서는 문턱 Boltzmann factor를 로그 밖으로 분리한다. float64 `q=0`은 `float64_underflow=True`와 유한 `log10_q_cm3_s`로 기록한다. 이를 자료 미확보 또는 물리적 0으로 바꾸지 않는다.

소스의 **86개 구간에 대한 닫힌 모멘트 합**은 ODE RHS 안의 에너지 quadrature를 제거하는 물리에 근거한 계산 단순화다. 이것만으로 측정 speedup을 주장하지 않는다. 새로운 성능 수치는 부모의 실제 고정 입력 benchmark 영수증이 있어야 한다.

### 첫 gap의 별도 문턱 모형

첫 폭 (h=0.0342\) eV, (s_1=0.00242), ε=E−χ에 대해

\[
s_p(E)=s_1(\epsilon/h)^p,
\quad
S_{\rm gap,p}=\frac{s_1}{h^p}
\left[\chi\theta^{p+1}\gamma(p+1,h/\theta)
+\theta^{p+2}\gamma(p+2,h/\theta)\right].
\]

첫 구간만 이것으로 바꾸고 나머지 실제 표는 그대로 둔다. p=1은 PL gap과 정확히 같고, p=1.127은 문턱 지수에 따른 별도 모형이다. (\theta\ll h,\chi)에서 두 gap의 비는 대략 (\Gamma(p+1)(\theta/h)^{p-1})이다. 따라서 낮은 온도에서 PL에 대한 상대 편차가 커질 수 있다. 이는 finite source core의 sensitivity이며 실제 단면적 interpolation error bound는 아니다.

## 4. 실제 새 scalar 수치와 판별 검증

새 `ci_finite.py`와 [수치 영수증](scalar_checks_v1/CI_THEORY_DELTA_NUMERICS.json), [CSV](scalar_checks_v1/CI_RATE_COMPARISON.csv)를 만들었다. 기존 C22C 여기 공급자의 검증은 반복하지 않았다. 바뀐 CI source에 대해 SI 단위로 직접 작성한 Gauss–Legendre 에너지 적분과 비교했다. 독립 적분은 원래 구간마다 (u=(E-L)/\theta)로 바꾸어 적분했고, (u>80)의 선택 PL 유한 구간 기여를 생략한 수학적 상한은 별도 기록했다. 이것은 **원자료 밖 physical tail**과 다르다.

| T[K] | log₁₀(qcore/[cm³/s]) | p1.127 gap / 기본 PL 전체율 | CCC core / SW91 전체 fit |
|---:|---:|---:|---:|
| 1 | −68580.9900457280 | 0.4960110 | 범위 밖 |
| 3 | −22867.2754514067 | 0.5702778 | 범위 밖 |
| 100 | −695.4756680683 | 0.8877981 | 범위 밖 |
| 300 | −238.0645652015 | 0.9726451 | 범위 밖 |
| 1,000 | −77.6855375296 | 0.9972729 | 범위 밖 |
| 2,000 | −43.1420195122 | 0.9994199 | 0.7752998 |
| 5,000 | −22.2560378651 | 0.9999251 | 0.8785638 |
| 10,000 | −15.1863770790 | 0.9999835 | 0.9369024 |
| 20,000 | −11.5615930381 | 0.9999962 | 0.9720104 |

300 K의 q는 8.6185617678×10⁻²³⁹, 10,000 K에서는 6.5106285899×10⁻¹⁶, 20,000 K에서는 2.7441444074×10⁻¹² cm³/s다. 첫 gap의 PL 기여 비중은 100 K에서 90.19%, 300 K에서 34.80%, 2,000 K에서 0.9319%, 20,000 K에서 0.006263%였다. 첫 gap만 바꾸는 지수 sensitivity가 작아져도 나머지 continuum 원자료 차이가 사라지는 것은 아니다. 예를 들어 SW91과의 2,000 K 차이는 첫 gap만 바꾼 결과보다 훨씬 크다.

1–10⁸ K의 11개 온도에서 독립 적분과의 최대 log₁₀ 차이는 **5.6843418861×10⁻¹⁴**, scaled integral 최대 상대 차이는 **3.3306690739×10⁻¹⁶**이다. 온도 bool·0·NaN·infinity·정의역 밖, D 요청, full physical rate 요청, 잘못된 flag 및 gap 지수의 **10개 fail-closed** 요청이 모두 거절되었다. 10⁸ K는 수치 범위 점검일 뿐 활성 물리 범위가 아니다. 그 온도에서 CCC 유한 core/SW91 전체 fit≈0.06859인 사실은 finite cutoff를 전체 hot rate로 취급하면 안 된다는 점과도 맞는다.

## 5. 문턱·binding·PI·RR의 일관된 새 registry

| 기준 | 값 또는 convention | C22D에서의 역할 |
|---|---|---|
| 상속 C21O HI | 13.6 eV | 동결 부모의 원래 PH1 support·chemical increment |
| CCC TICS | 13.6058 eV | 새 유한 CI source와 새 공통 HI chemical increment |
| SW91 | 1 Ry | 독립 비교 원전 convention; 현대 eV 변환을 별도로 명시 |
| NIST 실제 H1 handbook | 13.598433 eV | 모형 선택과 실제 isotope energy를 구별하는 참고 |

[NIST H1 원자료 페이지](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable1.htm)는 실제 H1 에너지에 관한 값과 isotope 범위를 명시한다. 따라서 CCC13.6058로 맞추는 것은 **source-consistency 변경**이며 reduced-mass isotope shifts나 실제 spectral accuracy를 완성한 것이 아니다.

원 PI provider의 HI PH2 모양 계수는 보존한다. 새 adapter는

\[
\sigma_{\rm PI,new}(E)=\mathbf1_{E\ge13.6058}\,\sigma_{\rm PI,old}(E)
\]

로 support만 명시적으로 제한한다. CCC E축을 평행이동하거나 보상 reservoir를 새로 만들지 않는다. 같은 Δχ=0.0058 eV를 H1/D/T binding 증가량, PI당 heat (E_\gamma-\chi), RR당 export (\chi+\langle E_{\rm cap}\rangle)에 모두 적용한다. RR α(T)와 fit-derived capture energy는 기존 근사로 보존한다. **독립 PI fit과 all-level Case-A RR fit의 Milne detailed balance 또는 LTE 완성은 주장하지 않는다.** fit의 값 정확도가 derivative로 얻는 thermal moment의 정확도를 보증하지 않는 기존 한계도 남는다.

support 구간 [13.6,13.6058) eV에서는 기존 PI율이 새로 0이 되므로 해당 국소율의 상대 변화는 100%다. 문턱 숫자의 상대 변화 0.042647%를 rate 전체의 상대 오차라고 쓰지 않는다. 실제 예: 13.6029 eV에서 기존 σ=6.3426617220×10⁻¹⁸ cm², 새 σ=0이다. 새 문턱에서 σ=6.3390298681×10⁻¹⁸ cm²로 다시 활성화되며, 그 위의 PH2 모양은 같다.

redshifting photon cohort의 crossing은

\[
\eta_{\rm new}=\eta_{\rm old}-\ln(13.6058/13.6),
\quad\Delta\eta=0.000426379675500811
\]

만큼 앞당겨진다. 해당 segment boundary, actual A-level events/RHS, binding 및 initial energy를 함께 갱신해야 한다. 겉 wrapper의 `thresholds` 속성만 바꿔도 아래 base가 원 registry를 읽으면 불일치가 남는다.

기존 C22C 저장 accepted data를 읽은 의존성 점검에서 20/40/60 eV cohort의 옛 HI 문턱 crossing에 기록된 광자 abundance는 |G|≤4.53×10⁻³²였다. 작은 음수도 그대로 보존했다. 이 결과는 **옛 저장 sample의 dependency evidence**이며 새 trajectory나 연속시간 upper bound가 아니다. PI support만의 영향과 CI 자체 영향을 구별하려면 같은 새 registry의 CI-off와 CI-on을 새 입력으로 비교한다. 같은 absorption당 gas heat는 −0.0058 eV, 같은 H-family RR당 export는 +0.0058 eV 변한다.

## 6. 반응·입자수·온도·에너지 보존

H1 ground CI의 순 화학양론은

\[
H^0+e\longrightarrow H^++2e,
\quad\nu=(-1,+1,+1)_{(H^0,H^+,e)}.
\]

핵종 row (1,1,0)과 전하 row (0,1,−1)은 각각 ν와 내적이 0이다. 총 particle row (1,1,1)의 내적은 +1이다. per-Href proper-time 사건률 (r=n_eX_{H1,0}q\,[\mathrm{s^{-1}/Href}])에 대해

\[
\dot X_{H1,0}=-r,\quad\dot X_{H1,+}=r,\quad\dot X_e=r,
\quad\dot C_{\rm CI}=r,
\]
\[
\dot U|_{\rm CI}=-\chi r,\quad\dot B|_{\rm CI}=+\chi r,
\quad(\dot U+\dot B)|_{\rm CI}=0.
\]

에너지는 ionization binding으로 옮겨 가며 CI만으로 escaping photon을 만들지 않는다. primary electron의 초과 kinetic energy와 secondary electron의 kinetic energy는 단일 Maxwell gas에 즉시 재분배한다는 closure다. 총 단면적만으로 전자별 energy-sharing spectrum이나 secondary ionization yield를 결정하지 않는다.

\[
U=\tfrac32 k_BNT,\qquad\dot N|_{\rm CI}=r
\quad\Longrightarrow\quad
\dot T|_{\rm CI}=-\left(\frac{2\chi}{3k_B}+T\right)\frac rN.
\]

Wolfram evaluator의 수정된 실제 호출은 이 식, charge0/nuclei0/particles+1, energy0 및 p=1 gap identity를 반환했다. Context 호출은 internal error였고 첫 evaluator 코드의 자기 참조 오류는 recursion failure로 기록했다. 수정 호출의 성공으로 앞선 실패를 삭제하지 않는다. 상세는 `THEORY_PROVENANCE_AND_COVERAGE.json`에 연결한다.

새 electron balance의 독립 gate는

\[
X_e+C_{\rm RR}-C_{\rm PI}-C_{\rm CI}-X_e(0)=0
\]

이다. (C_{\rm CI}=X_e+C_{\rm RR}-C_{\rm PI}-X_e(0))를 사후 정의해서 같은 식을 검증하면 항등식이므로 독립 보존 검사가 되지 않는다. 독립 CI counter를 쓰는 이유다. photon ledger는 CI로 변하지 않는다. 미모형 n/T 핵반응은 기존 선언한 정확한 zero inventory를 유지하며 nonzero 입력을 지우지 않고 거절한다.

## 7. isotope quotient가 성립하는 조건과 이번 변화

상속 PI/RR block은 공통 T와 ne에서 H1/D/T에 동일한 2-state 전자 generator Q₀를 쓴다. H1과 D의 초기 ion fraction도 모두 2×10⁻⁴다. 따라서 CI가 없으면 (X_H=A_Hv,\ X_D=A_Dv)인 비례 부분공간은 보존된다. H1-only excitation은 population을 바꾸지 않으므로, 이 비례 조건을 명시적으로 유지한다면 H1 heat를 (A_H/(A_H+A_D)\)로 aggregate에서 재구성하는 제한된 quotient는 가능하다. 이것은 D의 excitation rate를 H1과 같다고 선언하는 것과 다르다.

H1-only CI를 추가하면 aggregate (Z=X_H+X_D)의 식은

\[
Z'=Q_0Z+Q_{\rm CI}X_H
\]

가 된다. 같은 Z와 같은 isotope totals 안에서도 neutral abundance를 H와 D 사이에서 조금 바꾸면 (Q_{\rm CI}X_H)가 바뀐다. CI가 활성이고 neutral H가 있으면 기존 상수비례면도 깨진다. 따라서 Z만으로 이 항을 재구성하는 **기존 상수 weight quotient는 닫히지 않는다**. H1 상태를 별도로 유지한다는 구현 결정은 이 국소적인 정보 의존성에 근거한다. 임의의 모든 isotope reduction을 배제하는 새로운 strong no-go 주장은 아니다. 다른 공통 block의 축약이나 보조 좌표를 둔 축약은 별도 조건으로 연구할 수 있다.

## 8. 역반응, 밀도, Maxwell closure의 admission

### 8.1 명시된 ground-state inverse 진단

비퇴화 Maxwell gas, ground H 통계중량2·proton1·electron spin2의 convention이면

\[
S_1(T)=\left(\frac{2\pi m_ek_BT}{h^2}\right)^{3/2}10^{-6}
 e^{-\chi/k_BT}\quad[\mathrm{cm^{-3}}].
\]

같은 선택 ground CI 모형의 역반응을 mass action (R_3=K_3n_e^2n_p)로 정의할 경우 (K_3=q_{\rm CI}/S_1\,[\mathrm{cm^6/s}])가 detailed-balance equilibrium을 준다. coefficient에 identical-electron convention을 포함한 이 rate 정의에 추가 1/2를 덧붙이지 않는다. q와 S가 둘 다 underflow할 때 0/0을 계산하지 않고 두 Boltzmann 인자를 대수적으로 소거하여 K₃를 계산했다.

하지만 이는 **선택한 finite-source ground 모델의 조건부 inverse**다. 실제 all-level three-body capture, high-n bottleneck과 cascade를 원자료로 확보한 것이 아니다. 현재 C22D RHS에 reverse provider를 공급하지 않았으며, 이 수치를 모든 reverse process의 upper bound로 사용하지 않는다.

| T[K] | K₃ ground finite model[cm⁶/s] | nₑ=0.01에서 K₃nₑ/αRR |
|---:|---:|---:|
| 3 | 2.31216×10⁻²⁷ | 3.36950×10⁻¹⁹ |
| 300 | 2.53672×10⁻²⁹ | 5.85138×10⁻²⁰ |
| 2,000 | 6.43698×10⁻³⁰ | 5.06916×10⁻²⁰ |
| 10,000 | 1.93992×10⁻³⁰ | 4.62732×10⁻²⁰ |
| 20,000 | 1.07774×10⁻³⁰ | 4.27286×10⁻²⁰ |

실제 부모 C22C 저장 상태 3case에서 (n_{\rm Href}\)는 5.15125×10⁻⁶–1.76688×10⁻³ cm⁻³였다. 새 pilot의 (n_{\rm Href}\le0.01\) cm⁻³ guard 안에 있다. 같은 저장 sample의 조건부 ground inverse/RR 최대는 2.07326×10⁻²¹이다. 이 범위의 상태별 지표는 C22D의 새 accepted data에서도 다시 계산해야 한다. **density guard 하나만으로 모든 T·ionization 상태에서 all-level three-body omission이 입증되는 것은 아니다.**

### 8.2 thermal collision scale과 남는 조건

[NRL Plasma Formulary 2019](https://www.nrl.navy.mil/Portals/38/PDF%20Files/NRL_Formulary_2019.pdf)의 electron collision scale (\nu_e=2.91\times10^{-6}n_e\ln\Lambda\,T_{eV}^{-3/2}\,\mathrm{s^{-1}}\)를 공식 출처의 검색 색인으로 확인했다. PDF 직접 fetch는403/timeout으로 실패했으며 전문을 읽었다고 주장하지 않는다. ℓnΛ=10은 이 진단에서 **가정한 값**이다. 기존 저장 sample의 최소 νe/H≈2.07466×10⁷, T=20,000 K의 qCI/(νe/ne)≈2.13363×10⁻⁷이다.

이는 열적 전자 간 Coulomb 이완 scale에 대한 조건부 지표다. 저이온화 gas의 energetic photoelectron이 전자와 열화하기 전에 중성 원자를 여기·이온화하는 경쟁, ion/neutral와 electron의 온도 equilibration, 분포의 고에너지 tail까지 검증하지 않는다. 새 C22D는 single-T Maxwell 재열평형을 **부과한 closure**로 채택한다. 물리적 admission을 확장하려면 실제 electron-neutral energy-transfer, differential CI energy sharing/secondary yield, photon injection 및 Coulomb log를 결속해 τthermal≪τinjection,τinelastic,τexpansion 조건을 각각 확인해야 한다.

## 9. 실제 coverage와 다음 line-energy 의무

| process | C22D 단위의 상태 | 다음 필요한 근거 |
|---|---|---|
| H1 ground CI | CCC finite PL core와 보존 adapter 후보; source-domain/scalar PASS_SCOPED | continuum interpolation, 표 밖 tail, 새 trajectory admission |
| HI family PI/Case-A RR | source PH2 support와 공통 binding 기준을 새 계약으로 정렬 | Milne-consistent multilevel/photo/RR 통합을 완료했다고 쓰지 않음 |
| H1 n=2 excitation | 동결 C22C의 source와 즉시 귀환·완전 탈출 재사용 | 실제 lifetime, escape, 재흡수, mixing |
| D/T·He/Li CI·excitation | 미확보 source는 UNAVAILABLE | 종별 rate/threshold/energy·isotope adapter |
| 역 three-body | 선택 ground inverse의 진단만 존재 | all-level capture/cascade source와 density/T 조건 |
| DR/CX/free-free/분자 | 완료되지 않음 | 실제 thermal moment, final states, photon spectrum, 유효 온도 |
| secondary electrons | Maxwell thermalization closure로 제거 | energy-sharing spectrum, competing yields와 T분리 |
| full thermal/radiative/UV/stars | OPEN | energy source·transport·생산 network |

다음 최소 line 계약은 2p Lyα의 line photon 하나와 2s two-photon continuum을 구별해야 한다. 매질 column·geometry·line profile, absorption source 및 collisional de-excitation/2s↔2p mixing이 실제 필요하다. two-photon spectrum은 photon수 적분2와 energy 적분ΔE를 동시에 만족해야 한다. CCC README가 same-n LS-degenerate 전이에 경고한 형식적 발산을 finite physical mixing rate로 복사하지 않는다.

isotropic resident-radiation reservoir를 추가하는 조건부 다음 모형은 per-Href R에 (R'=-R+(Q_{emit}-Q_{abs}-Q_{esc})/H\), (W_R'=R\), (L_{esc}'=Q_{esc}/H\)를 두고 gas 항과 상쇄시킬 수 있다. 실제 opacity와 escape 규칙은 별도 원자료가 있어야 한다. 이미 탈출한 cumulative export에는 다시 redshift 항을 붙이지 않는다. higher-n을 추가하면 각 cascade의 photon energy 합이 level ΔE와 일치하고 photon multiplicity가 branch와 일치해야 한다.

atomic gas는 isotropic stress closure다. nonbaryonic Vlasov의 anisotropic stress를 gas heating으로 옮기지 않는다. non-tilted LRS, full Frobenius norm, signed amplitudes를 먼저 합한 뒤 norm을 취하는 `Pi_r=abs(Pgamma+Pnu)`, `Pi_tot=abs(Pm+Pr)`를 유지한다. full nuclear high-energy 및 general tilted/triaxial/polarized CMB는 HOLD다. 회수하지 못한 원 핵반응 PNG를 읽은 근거는 없고, 접근 못한 과거 대화는 UNAVAILABLE로 취급한다.

## 10. tail·오차·NG 및 4축

물리적 total CI를 말할 때 (q_{phys}=q_{core,PL}+\delta_{interpolation}+q_{tail}\)로 구분한다. 두 미지 항은 OPEN이다. 모든 E>Emax에서 실제 σ/a₀²≤scap이라는 추가 가정이 있으면 (q_{tail}\le K s_{cap}\theta^{-1/2}(E_{max}+\theta)e^{-E_{max}/\theta}\)다. 채택한 physical cap은 null이다. 20,000 K의 cap당 계수 log₁₀는 −249.9374748156이지만 그 작은 수가 cap의 증명은 아니다. `global_error_bound=null`을 유지한다.

**새 strong no-go: NONE. NG1–NG7 각각 NOT_APPLICABLE_WITH_REASON.** 대상 전체의 불가능성·배제 정리, 그 sharpness 또는 문헌 신규성을 성과로 채택하지 않았다. 위 isotope 사례는 현재 닫힘의 조건과 필요한 추가 정보에 대한 구성적 국소 진단이다. positivity와 energy cancellation은 새 source adapter의 구성적 증명, 수치 비교는 finite model 구현 검증이다.

| 단계 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|
| source/이론 R1–R5 | 실제 문헌 조회·기존 선택 bytes 판독·차원/보존 유도 완료; ODE0 | 로컬 source-bound 이론 작성 | 부모 운송 영수증 대기 | finite CI 후보와 registry 결정 |
| scalar 구현 C1–C6/R6 | 11T 독립 적분·10 refusal PASS_SCOPED, 기존 결과 변경0 | 공급자와 CSV/JSON reviewable | 이 하위 작업에서 외부 완료 주장 없음 | 부모 adapter·새 입력으로 연결 |
| 전체 C22D R7–R9 | 부모의 신규 run/분석 영수증으로 확정 | 실제 Git/PR receipt로 확정 | 실제 provider ID·readback으로 확정 | 이 문서만으로 COMPLETE 주장 안 함 |
| 다음 R10 | 새 완료 계산 복원 재실행 불필요 | 다음 source 계약 공개 | 원 bytes 보존 연결 | line escape/secondary/omitted process OPEN; nuclear/general CMB HOLD |

공개 묶음에는 이 보고서, `ci_finite.py`, 선택 TICS bytes, scalar CSV/JSON, source hash와 조회 범위를 포함한다. `retrieval_raw/`의 검색 원문·긴 초록과 기존 SW91 PDF·이미지 전체는 중간 판독 자료로 두며 공개 package에 자동 복제하지 않는다. 원문 URL과 hash·판독 위치가 근거의 연결을 제공한다.
