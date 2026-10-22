# C22A: 유한 UV와 동적 온도를 결합한 조건부 열화학 에너지 회계

## 1. 이번 단계의 판정

**C22A는 21개 원자 population, 유한 초기 UV, 동적 gas temperature를 묶은 74-state pilot의 보존식 유도·구현·nominal 3건 실행·저장 자료 검토를 완료했다.** Nominal 3건은 사전등록된 저장 201점 및 accepted mesh의 상태 검사를 모두 통과했다. 더 엄격한 Radau reference는 적분 후 초기 neutron 재고의 정확한 0 조건에서 실패했으며, 원 실패 상태를 유지한다. 그 보존 배열에서 다시 구한 여섯 관측량은 nominal과 정해 둔 수치 비교 기준 안에서 일치했다. 이 결과의 채택 범위는 **조건부 사건 회계와 유한 표본 수치 결과**다. Full thermochemical/radiative energy closure는 **OPEN**이다. [E1–E4]

새로 얻은 물리적 판단은 누락 과정의 우선순위다. 현재 UV 궤적에서 평가한 등방 CMB Compton 에너지 교환과 H excitation 냉각은 초기 에너지 또는 팽창 냉각률과 비교해 작지 않다. 따라서 현재 온도·전자밀도 이력을 완성된 물리 해로 승격하지 않는다. 이 보고서는 누락 항을 결합한 대안 해를 계산하지 않았으며, `global_error_bound=null`을 유지한다. [E5]

| 기록 축 | 이 보고서 작성 시점의 상태 |
|---|---|
| EXECUTION | 새 nominal 3건 `PASS_SCOPED`; Radau 1건 `FAILED_PRESERVED`; 독립 검토·누락 진단·분석의 추가 ODE 0; 기존 C21O/NCP 재실행 0 |
| PUBLICATION | **OPEN / LOCAL_COMMIT_ONLY_UNPUBLISHED** — content commit `7c796130af14616ab367e734842e941df5dd55f5`와 R을 prerequisite로 하는 Git bundle 보존. GitHub 쓰기 ACK 없음, Git push는 HTTPS 인증 부재로 실패. 원격 게시는 완료하지 못했다. [E8] |
| BACKUP | 이 보고서는 ZIP 봉인 전 snapshot이다. 새 배송본의 실제 SHA·provider ACK·재다운로드 검사는 별도 `C22A_FINAL_AUTHORITY_20261022.json`을 따른다. 역사적 C21O Drive 보존은 계속 OPEN이다. |
| DAG | 조건부 pilot 결과 확보; strict-zero reference 실패 유지; full closure 및 추가 atomic coverage OPEN |

선택한 연구 절차는 요청한 `physmath-research-loop`의 제공된 1.0.0 패키지다. R1–R10/C1–C10 기록은 `STAGE_RECORDS.json`에 분리되어 있다. 이 보고서는 strong no-go 정리를 주장하지 않는다. [E1]

## 2. 권위·외부 결과·복원 자료의 재사용

출발점은 `bass_cr`의 `research/cr-c21o-hheli-z2-sandbox-20261021`와 Draft PR96이다. Science C는 `6b6db06e8148e6826a2d5bf7dbc53d362126ca62`, historical D는 `f7ca6905729f7d8d36ca0605f7b1dd7ad5595819`, recovery R은 `a5e12c5f3e6d323e211d65fefad34060ec07eff0`이다. 기존 C21O의 45 stress grid와 6 controls, 201 saved times는 완료 증거로 재사용했다. 복원 목적으로 이를 재적분하지 않았다. 과거 복원 327개 연구 파일 및 원 analysis_v2와 byte-identical한 15개 결과물이라는 권위 기록도 새 계산의 성과와 구분한다. [E1, E6–E7]

이번 intake는 7개 저장소의 advertised heads 1,255개를 조사했다. 직전 2026-10-21 21:15:26 UTC snapshot 대비 추가 0, 변경 4, 삭제 0이며, 변경 4개 중 하나는 이미 알려진 C21O D→R 게시다. 실제 새 외부 변경은 HE85, REI219, VigilODE 세 곳이다. 선택 text 31개는 Git blob identity를 검증했지만 외부 raw array의 재감사는 수행하지 않았다. [E6]

HE85에는 외부 소유자가 394개 결과를 잃은 뒤 재실행해 보존한 완료 보고가 추가되었다. REI219에는 all-bare, 즉시 열화, passive 핵반응 민감도라는 별도 조건의 후속 결과가 추가되었다. 두 campaign의 과거 미완료 snapshot을 지우지 않는다. VigilODE의 원 P02 C6FAIL도 그대로 보존하며 P02b/P03/P04 후속 보고와 구분한다. P04의 사건별 에너지 회계는 검토 근거로 사용했지만, 그 viscous-gas closure를 우리의 nonbaryonic Vlasov stress에 대입하지 않았다. REI220/BASS180 compact33 mirror의 과거 대표 raw 2쌍 비교는 여전히 `PASS_SCOPED`이며 전체 127raw 재감사 또는 측정 speedup을 뜻하지 않는다. [E6]

대화 connector는 실제로 접근 불가를 반환했으므로 `UNAVAILABLE`이다. 원 핵반응 네트워크 PNG는 회수되지 않았고 읽지 않았다. 복원 ZIP의 Library byte identity와 Dropbox ID·크기 metadata를 재사용했으며, Dropbox byte 재다운로드는 `NOT_RUN`이다. Drive에서는 제한된 검색·폴더 listing으로 C21O 항목이 반환되지 않았지만 이것을 전역 부재로 해석하지 않았다. 원 main `UNKNOWN_NO_ACK`, 원 document `NOT_RUN`, recovery ZIP `NOT_ATTEMPTED`를 유지한다. 삼중 백업 완료 주장은 하지 않는다. [E6–E7]

## 3. 실제로 정의한 물리계

기하학은 non-tilted LRS다. Signed amplitudes를 더한 뒤 full Frobenius norm을 취하여

\[
P_r=P_\gamma+P_\nu,\quad P_{\rm tot}=P_m+P_r,\qquad
\Pi_r=|P_r|,\quad\Pi_{\rm tot}=|P_{\rm tot}|
\]

로 계산한다. Scalar norm의 합과 signed cancellation을 혼동하지 않는다. Atomic gas는 isotropic stress closure를 가지며, matter anisotropic stress는 별도의 nonbaryonic Vlasov 부문에 속한다. 추가 UV도 imposed isotropic cohort closure다. [E1, E4]

재고는 n, H1/D/T의 0·1 전하 상태, He3/He4의 0·1·2, Li6/Li7의 0·1·2·3으로 총 21 populations다. 전자 전이 edge는 H 계열 3개, He 계열 4개, Li 계열 6개인 13개이며 독립 electronic coefficient row는 6개다. 초기 n/T=0은 선언한 재고다. 미지원 종을 0으로 대신한 것이 아니며 양의 n/T 입력에는 beta/nuclear energy 계약이 필요하다. [E1, E4]

상태 74개는 inherited LRS kinetic 40개, atomic 21개, UV count 6개, thermal/export/work/event-count/optical-depth 7개다. 초기 온도는 300 K이고 UV cohort 에너지는 `[10,20,40,60,100,150] eV`, Href당 초기 count는 `[0.05,0.25,0.003,0.0002,0.00001,0.000001]`이다. 외부 emissivity는 이번 IVP에서 명시적으로 0이다. 각 cohort 에너지는 평균 팽창에 따라 감소하며, 기존 prescribed UV/T 모델과 달리 photon inventory와 thermal energy가 반응으로 변한다. [E1–E2]

공통 Maxwellian 온도, 이상 단원자 gas, photoelectron의 즉시 열화, ground-state charge inventory를 가정한다. Thermal·chemical·UV trace energy는 Einstein source에 추가하지 않았고 그 비율만 진단했다. 따라서 전체 열·복사·중력 backreaction을 완성한 모델이 아니다. [E1, E4]

## 4. 입자수와 사건별 에너지 보존의 구성

시간 변수는 \(\eta=\ln(a/a_i)\), \(H\)의 단위는 s⁻¹이다. \(N_i\)와 \(G_g\)는 보존되는 Href 핵당 원자·광자 수, 에너지는 eV/Href다. 전자 수는 charge neutrality로 \(N_e=\sum_iq_iN_i\)로 구한다. Thermal energy를

\[
U=\frac32k_BT\,(N_{\rm nuc}+N_e)
\]

로 정의하면, 온도 식에는 팽창뿐 아니라 반응에 따른 입자수 항이 생긴다.

\[
T'=-2T-T\frac{N_{\rm part}'}{N_{\rm part}}
+\frac{Q_\eta}{(3/2)k_BN_{\rm part}}.
\]

여기서 \(Q_\eta\)는 eV/Href/η의 반응 가열률이다. U를 직접 적분하는 구현은 이 입자수 효과를 포함한다. 원전의 temperature equation과도 대조했다. [W1, E3–E4]

Lower→upper edge e와 cohort g의 동일 사건 flux를

\[
\mathcal P_{eg}=\frac{c\,n_{\rm Href}N_l\sigma_e(E_g)G_g}{H},\qquad
\mathcal R_e=\frac{n_eN_u\alpha_e(T)}{H}
\]

로 두었다. Threshold \(\chi_e\), RR 포획 electron의 평균 kinetic energy \(\epsilon_e\), chemical binding inventory \(B\), UV energy \(V=\sum_gE_gG_g\)에 대해

\[
\begin{aligned}
U'&=-2U+\sum_{eg}(E_g-\chi_e)\mathcal P_{eg}-\sum_e\epsilon_e\mathcal R_e,\\
B'&=\sum_e\chi_e\left(\sum_g\mathcal P_{eg}-\mathcal R_e\right),\\
V'&=-V-\sum_{eg}E_g\mathcal P_{eg},\\
E_{\rm esc}'&=\sum_e(\chi_e+\epsilon_e)\mathcal R_e,\\
W_g'&=2U,\qquad W_{\rm UV}'=V.
\end{aligned}
\]

따라서 \(U+B+V+E_{\rm esc}+W_g+W_{\rm UV}\)가 보존된다. \(E_{\rm esc}\)는 **경계를 통해 유출된 누적 에너지**이며 방출 이후 우주에 남아 redshift하는 복사 저장고의 현재 에너지가 아니다. 별도의 propagated reservoir를 택하면 그 redshift와 work를 함께 바꾸어야 한다. 이번 구현은 두 정의를 섞지 않는다. 원자핵별 수, \(N_e+N_{\rm RR}-N_{\rm abs}\), \(\sum_gG_g+N_{\rm abs}\)도 같은 사건 flux로 보존된다. [E1, E3–E4]

RR의 kinetic moment는 온도에 직접 의존하지 않는 microscopic cross section과 Maxwellian 평균 아래

\[
\Lambda_{\rm RR}=k_BT\left(\frac32\alpha+T\alpha'\right),\qquad
\epsilon_{\rm RR}=\Lambda_{\rm RR}/\alpha
\]

로 유도했다. Verner–Ferland fit \(\alpha=A/[s_0(1+s_0)^{1-b}(1+s_1)^{1+b}]\), \(s_i=\sqrt{T/T_i}\)에 적용하면 안정적인 표현은

\[
\frac{\epsilon_{\rm RR}}{k_BT}
=\frac{1-b}{2(1+s_0)}+\frac{1+b}{2(1+s_1)}.
\]

실제 6개 row의 양의 A,T₀,T₁ 및 −1<b<1에서 이 factor는 0과 1 사이에 있다. Wolfram 대수 잔차는 0이었고, 각 row의 10,001점 derivative 검사는 최대 절대차 \(7.05\times10^{-11}\)를 주었다. 독립 75-digit 미분 비교 36점은 최대 상대차 \(2.94\times10^{-16}\)이었다. 이는 **선택한 fit가 함의하는 moment의 구현 검사**다. Number-rate fit의 정확도를 그 미분이나 실제 에너지 moment의 정확도로 옮기지 않는다. [W2–W3, E3–E4]

## 5. Atomic-rate coverage와 적용 조건

| 과정 | 현재 계약 | 한계 또는 다음 필요 자료 |
|---|---|---|
| Ground valence photoionization | 6 electronic rows 활성; Li I는 2s만 | core/Auger, secondary ionization, 비열적 electron 미포함 |
| Case-A RR number | 고정 Verner–Ferland 6 rows, 채택 fit domain 3–10⁹ K | 이 온도 범위 전체의 gas/누락 과정 유효성을 보증하지 않음 |
| RR kinetic energy | 위 fit의 analytic derivative moment 활성 | He/Li 독립 energy data OPEN; HeIII reference normalization 미해결 |
| H collisional ionization | 진단만; 10⁴–10⁹ K | domain 밖 NaN/OPEN, 외삽·0 대체 없음 |
| H excitation cooling | 진단만; 5,000–500,000 K | low-density line escape 가정, 일부 온도 구간만 가능 |
| CMB Compton energy | 진단만; 비상대론적 isotropic blackbody | 활성화 시 반대 부호 radiation energy 계정과 LRS 조건 필요 |
| DR, He/Li CI·excitation, free-free, charge exchange, molecules | OPEN_NOT_IMPLEMENTED | 실제 rate·온도·energy destination·우세성 계약 필요 |
| RR 재흡수, stellar UV, angular/spectral transport | OPEN_NOT_IMPLEMENTED | source·transport·multilevel/cascade closure 필요 |

이 표는 실제 provider와 실행된 항을 구분한 `RATE_COVERAGE.json`의 요약이다. 원전 PH1/PH2를 독립 전사한 116점 검사는 threshold 양쪽과 Li I branch switch를 포함해 최대 상대차 \(3.42\times10^{-16}\)이었다. Compiled Fortran 비교나 모든 실수 에너지의 동일성 증명은 아니다. H RR cooling의 다른 문헌 fit와의 비교는 유한 격자 진단으로 남겼으며, HeIII의 약 4배 normalization 차이를 임의로 보정하지 않았다. [E3–E4, W1–W4]

Isotope quotient의 정확성은 활성 electronic operator, threshold, energy moment, 공통 T/ne/UV가 같을 때만 성립한다. 개별 charge fraction의 유일한 복원에는 초기 벡터의 비례 조건도 필요하다. Isotope-specific charge exchange·energy shift·beta/nuclear 항을 추가하면 이 조건을 다시 확인해야 한다. 특히 H/D charge exchange의 실측·이론 rate는 별도 primary-source 검토 대상이다. [E1, E3–E4, W5]

## 6. 실제 새 실행과 nominal 결과

Nominal run ID는 `c22a_finite_uv_bdf_20261022_v1`이며 BDF rtol \(3\times10^{-11}\), atol \(3\times10^{-13}\)이다. z20→2를 각 18개 threshold segment로 적분하고 201점을 저장했다. Accepted mesh는 사례별 611/1,369/1,382점이다. 실행 source identity는 `f5f0f30b1358d79a361045823ec68daeca72c10da3675e7882ccb5775c3053cd`이며 28개 의존 파일을 묶는다. 관측 자원·lease에 따라 nominal worker2와 reference worker1을 사용했고, worker당 thread1, 별도 coordinator, CPU55 보호, create-only 출력을 지켰다. [E1–E2, E4]

| 사례 | 초기 (signed Σ, Pm, Pr) | accepted 최고 T [K] | z2 T [K] | z2 H1 ionized fraction | 최종 τT | z2 전자밀도 [cm⁻³] |
|---|---|---:|---:|---:|---:|---:|
| dark_expansion | (0,0,0), UV 0 | 300 | 6.122458 | 0.0001961683 | 0.00003729286 | 1.010541×10⁻⁹ |
| finite_uv_flrw | (0,0,0) | 9,921.234966 | 216.621450 | 0.06972445 | 0.02932886 | 3.613350×10⁻⁷ |
| finite_uv_lrs | (0.3,0.0002,0.0008) | 9,921.221054 | 216.613919 | 0.06979577 | 0.02926598 | 3.617050×10⁻⁷ |

z20에서 z2까지 proper elapsed time은 dark/FLRW 약 3,092.616 Myr, LRS 약 3,091.339 Myr다. Dark control에도 잔류 초기 이온화와 RR이 있어서 순수 무반응 \(T\propto a^{-2}\)의 exact oracle로 부르지 않는다. 모든 nominal n/T 성분은 저장점과 accepted mesh에서 정확히 0이었다. [E2, E4]

| 사례 | 최대 에너지 상대잔차: saved / accepted | 최대 핵종 상대잔차: accepted | 최대 charge-photon 잔차: accepted | 최대 photon-count 잔차: accepted |
|---|---:|---:|---:|---:|
| dark_expansion | 7.764×10⁻¹⁶ / 9.317×10⁻¹⁶ | 1.776×10⁻¹⁵ | 2.711×10⁻¹⁹ | 1.362×10⁻³⁵ |
| finite_uv_flrw | 1.977×10⁻¹¹ / 1.987×10⁻¹¹ | 2.442×10⁻¹⁵ | 4.631×10⁻¹⁶ | 5.551×10⁻¹⁶ |
| finite_uv_lrs | 1.423×10⁻¹¹ / 1.433×10⁻¹¹ | 1.554×10⁻¹⁵ | 1.018×10⁻¹⁵ | 9.992×10⁻¹⁶ |

사전 기준은 에너지 \(2\times10^{-8}\), 핵종·charge·photon count 각각 \(2\times10^{-9}\)다. Population/UV의 작은 음수는 원값을 보존하여 각 계약 하한과 비교했다. 예를 들어 dark accepted 최소 scaled population은 \(-2.7813\times10^{-28}\), UV 사례의 최소 cohort count는 약 \(-1.44\times10^{-14}\)다. Clipping, temperature floor 또는 0 대체는 하지 않았다. Retained thermal+chemical+UV energy의 H² source-scale 비율은 최대 약 \(7.14\times10^{-10}\)였으나, 이는 누락된 에너지 교환이 온도에 미치는 영향의 상한이 아니다. [E1, E4]

## 7. 엄격한 reference 실패와 재적분 없는 비교

`c22a_finite_uv_radau_20261022_v1`은 같은 물리 입력·source로 Radau rtol \(3\times10^{-12}\), atol \(3\times10^{-14}\)를 사용했다. 18개 구간은 모두 solver success를 반환했지만, 후처리의 `ZERO_INITIAL_INVENTORY_CHANGED` 예외로 전체 실행 상태는 `FAILED_PRESERVED`가 되었다. 보존 자료의 neutron 최대 절댓값은 \(8.674087365096036\times10^{-36}\)/Href다. 이 값이 작아도 사전등록한 “정확히 0” 조건은 실패다. T₀/T₁는 정확히 0이며 나머지 상태 gate는 저장 201점에서 통과했다. 정확한 부동소수점 발생 기전은 규명하지 않았고, 확인한 n RHS=0와 작은 수치 누출이 양립한다는 범위로 판정했다. [E4]

원 `FAILED_ACCEPTED_SOLUTION.npz`의 이름과 달리 현재 보존 내용은 201개 dense saved states다. Reference accepted mesh는 **UNAVAILABLE**이다. 독립 검토는 같은 hashed memory bytes를 읽고 원 neutron 값을 유지한 채 파생 진단을 만들었다. 새 ODE·RHS 호출은 0이며, 성공 run history로 재명명하지 않았다. [E4]

| 같은 201점의 관측량 | max abs(nominal−reference) / reference peak |
|---|---:|
| T | 5.088679×10⁻¹⁰ |
| ne | 6.171244×10⁻¹⁰ |
| τT | 1.579237×10⁻¹⁰ |
| full-Frobenius Σ | 4.534787×10⁻¹⁰ |
| full-Frobenius Πr | 1.118045×10⁻¹⁰ |
| H1 ionized fraction | 6.211090×10⁻¹⁰ |

여섯 값은 비교 기준 \(2\times10^{-7}\)보다 작아서 `PASS_SCOPED_DIAGNOSTIC_ONLY`다. Reference 자체의 공식 판정은 `FAIL_EXACT_ZERO_GATE_RETAINED`다. 이 두 판정은 함께 유지한다. [E4]

## 8. 누락 과정의 정량 진단과 유한 격자 한계

원 nominal 궤적의 saved201 및 accepted mesh에서 H CI, H excitation, 등방 CMB Compton을 평가했다. Compton 가정은 \(T_\gamma=2.7255(1+z)\) K 및

\[
Q_C=\frac{4\sigma_Tc\,a_RT_\gamma^4n_ek_B(T_\gamma-T)}{m_ec^2}
\]

이다. \(Q_C>0\)이면 gas heating이다. LRS에는 이 등방 bath가 추가 근사이며 anisotropic spectral CMB energy exchange를 푼 것이 아니다. 수치적으로 완벽한 shear 0이 아닌 FLRW control도 자동 진단 metadata는 보수적인 분류를 유지한다. [W1, E5]

| accepted mesh | ∫abs(Compton)dt [eV/Href] | 초기 총 에너지 대비 | max abs(QC)/(H U) | H excitation 부분적분 [eV/Href] | 초기 총 에너지 대비 |
|---|---:|---:|---:|---:|---:|
| dark_expansion | 0.0000578754 | 0.129513% | 0.00666448 | UNAVAILABLE | UNAVAILABLE |
| finite_uv_flrw | 2.54133136 | 44.7588% | 8.40592 | 0.25438259 | 4.48027% |
| finite_uv_lrs | 2.53120424 | 44.5804% | 8.34264 | 0.25261757 | 4.44919% |

표의 rate 비는 밀도 단위에서 |Q_C|/(H u_th)이며, Href당 단위에서는 |Q_C/n_Href|/(H U)로 같은 값이다. eV와 erg의 변환은 진단 코드에서 수행한다. UV 두 사례의 Compton signed 적분은 음수이며 원 궤적에서 냉각 방향이다. LRS의 H excitation 순간 최대 \(Q/(HU)=3.84957\)이고, 유효 온도 구간 부분적분은 초기 thermal U의 6.01945배다. Compton 절댓값은 초기 thermal U의 60.3143배다. 초기 U가 0.0419669 eV/Href인 반면 UV 가열을 받는 이력이라는 점이 이 비율의 맥락이다. 이는 결합 계산 없이 실제 온도 수정량으로 바꿀 수 없는 진단이다. [E5]

H CI fit의 하한은 10,000 K인데 모든 nominal 표본의 최고 T가 그보다 낮다. 따라서 CI rate와 적분 사건수는 **UNAVAILABLE/null**이다. 이를 0으로 해석하지 않는다. H excitation은 5,000 K 이상 구간만 평가되며, LRS accepted mesh의 유효 proper-time 비율은 4.08921%다. 나머지 구간을 외삽하거나 이어서 적분하지 않았다. He/Li CI·excitation, DR, charge exchange, free-free 등의 우세성은 아직 정량 평가되지 않았다. [W1, E5]

LRS에서 saved201 사다리꼴 적분은 accepted mesh 결과보다 Compton **0.166143%**, 부분 excitation **1.438209%**, 포함 RR kinetic cooling **0.121278%** 높았다. Excitation의 saved201 유효 시간은 3.93317%이므로 격자 차이와 적용 구간 차이가 함께 섞인다. Accepted mesh도 정확한 적분 참값이 아니고 solver tolerance는 이 사후 quadrature의 오차를 보증하지 않는다. 이 비교는 `global_error_bound`를 제공하지 않는다. [E5]

## 9. 분석 자료와 다음 DAG

권위 분석 자료는 `analysis_v3/`의 CSV, SUMMARY 및 PNG/PDF다. v1에는 secondary-redshift 축 의미 문제가 있었고 v2에는 제목·offset text의 겹침이 있어 표시를 보정했다. 또한 v1 HISTORY CSV는 현재 443개 data rows·252,036 bytes로, 당시 ARTIFACTS manifest의 348,309 bytes 및 SHA256과 다르다. 이 후속 byte mismatch의 원인은 `UNRESOLVED_AFTER_MANIFEST`이며 추정하지 않는다. v1은 축 문제와 불완전한 history export 두 사유로 최종 권위에서 제외한다. v2/v3 HISTORY는 각각 사례당 201점인 603 rows이며 HISTORY·ENDPOINTS CSV가 두 버전에서 byte-identical이다. Raw ODE를 다시 계산하지 않았다. 원 3개 history의 bytes와 출처는 COMPLETE receipt로 결속한다. 그림은 적분된 proper time에서 시작점 0을 유지하는 symlog 축과 각 사례 redshift 위치를 사용한다. [E2]

다음 단계는 이번 결과의 실패 이력과 물리적 범위를 유지하면서 진행한다.

1. **새 C22A 결과 게시·배송:** source, contract, 실패 원본, 독립 검토, v3 분석, omission 진단과 publishable Git bundle을 배송본으로 보존한다. 현재 GitHub 쓰기 접근 문제로 게시가 OPEN이며, 인증이 복구된 뒤 기존 S를 포함한 bundle HEAD를 재적분 없이 게시한다. 새 백업의 실제 receipt는 별도 최종 authority를 따른다. 역사적 C21O Drive 확인은 별도 OPEN 노드다.
2. **Strict-zero 표현 계약:** 이번 reference를 재분류하지 않고, 이후 모델에서 선언된 invariant component를 구조적으로 제외할지 또는 다른 명시적 수치 계약을 택할지 결정한다. 선택 변경은 새 source·input·run ID를 요구한다.
3. **Compton과 excitation의 보존적 활성화:** gas sink와 radiation/source 계정의 반대 항, 적합한 LRS angular/spectral 가정, 낮은 온도까지의 실제 coefficient coverage, line escape 조건을 먼저 고정한다. 이번 진단은 이 노드의 우선순위를 지지한다.
4. **Atomic coverage 확장:** DR, He/Li 충돌, free-free, charge exchange, molecules, secondary electrons, RR 재흡수, stellar emissivity의 rate·유효 온도·dominant omissions를 확인한다. 반응마다 전하·핵종·에너지 보존과 isotope quotient 조건을 재검토한다.
5. **새 구현과 검증:** 가벼운 보존·한계 검사 후 실제 resource/lease를 다시 확인하고 새 IVP만 실행한다. 누락 항 활성화에 따른 self-consistent 변화와 유한 격자 차이를 분석한 뒤 결과를 게시·보존한다.

Full nuclear high-energy 및 general triaxial/tilted/polarized CMB는 HOLD다. 전체 thermal/UV/stars/nuclear network 완료 주장은 여전히 하지 않는다. [E1, E5–E7]

## 근거 경로와 원전

상대 경로는 이 `cr_c22a_thermochemical_20261022` directory 기준이다. 독립 검토 원본을 `evidence/independent_review/`로 byte-identical하게 복사하여 실행·분석과 함께 제공한다.

- **E1 — 사전 계약과 단계:** `CONTRACT.json`, `RATE_COVERAGE.json`, `evidence/SOURCE_FREEZE.json`, `STAGE_RECORDS.json`.
- **E2 — 실행·분석 원본:** `runs/c22a_finite_uv_bdf_20261022_v1/{INPUT,RESOURCE,SOURCE_IDENTITY,SUMMARY}.json`, 각 case의 `COMPLETE.json`, `RECEIPT.json`, `history.npz`; `analysis_v3/{SUMMARY.json,HISTORY.csv,ENDPOINTS.csv,ARTIFACTS.json}`. 표시 버전 비교는 해당 CSV bytes를 직접 읽었다.
- **E3 — 유도·계수 검사:** `theory/THERMOCHEMICAL_ENERGY_CONTRACT.md`, `theory/RR_ENERGY_CHECKS.json`, `theory/TOOL_RECEIPTS.json`; `evidence/FOCUSED_TESTS_v2.json`.
- **E4 — 독립 검토:** `evidence/independent_review/C22A_REVIEW.md`, `evidence/independent_review/INDEPENDENT_CHECKS_v2.json`, `evidence/independent_review/saved_review_v1/SAVED_DATA_REVIEW.json`, `evidence/independent_review/saved_review_v1/REFERENCE_DIAGNOSTICS.npz`; 원 실패는 `runs/c22a_finite_uv_radau_20261022_v1/cases/finite_uv_lrs/{FAILURE.json,FAILED_SEGMENTS.json,FAILED_ACCEPTED_SOLUTION.npz}`. 저장 검토는 2026-10-22 02:03:14 UTC snapshot이며 reviewer ODE/RHS 호출 0이다. 최종 그림 검토는 같은 `saved_review_v1/FINAL_FIGURE_REVIEW.json`과 `evidence/ROOT_FIGURE_REVIEW.json`이다.
- **E5 — 누락 진단:** `runs/c22a_finite_uv_bdf_20261022_v1/omission_mesh_comparison_v1/{MESH_COMPARISON.json,RESOURCE.json,REPORT_KO.md}`; 각 case `omissions_saved/OMISSIONS.json`, `omissions_accepted/diagnostics/OMISSIONS.json`. 진단 코드 SHA256 `8dc5b1653554b10fdd0745311eef80714e54d155d136201ea9eaf0ad6adf26e9`.
- **E6 — 외부 intake:** `evidence/intake_refs/EXTERNAL_INTAKE_20261022.json`, `LIVE_REFS.json`, `TEXT_SOURCE_BINDINGS.json`, `PR_METADATA.json`; 관측 2026-10-22 01:32:46 UTC.
- **E7 — 복원·백업 intake:** `evidence/intake_backup/BACKUP_INTAKE_20261022.json`, `conversation_unavailable_receipt.json`; ZIP `BASS_CR_C21O_RECOVERY_20261022T065344KST.zip`, 29,568,718 bytes, SHA256 `06bc8b02dd38f729005abb52608346715479f8cc8f88e63ce7586e4ed25696ef`.
- **E8 — 실제 게시 시도:** `evidence/publication_attempts/FINAL_PUBLICATION_STATUS.json`, `INLINE_TREE_ATTEMPT_RECEIPT.json`, `FINAL_PUBLICATION_READBACK.json`; 로컬 content commit S와 별도 delivery manifest의 bundle head는 원격 게시 receipt가 아니다. 첫 blob 쓰기는 768초 동안 ACK가 없었고 이후 expected blob GET은 404였다. 대안 inline tree 쓰기도 44.001초 동안 ACK가 없었다. Connector commit/ref mutation은 0이며 Git push는 `could not read Username for 'https://github.com'`으로 실패했다.
- **W1 — Hui & Gnedin (1997), MNRAS 292,27**, Eq.(2), Appendix A: [primary paper](https://arxiv.org/abs/astro-ph/9612232), DOI [10.1093/mnras/292.1.27](https://doi.org/10.1093/mnras/292.1.27). Temperature particle-count term, H CI/excitation fit 및 isotropic nonrelativistic Compton의 원전.
- **W2 — Verner & Ferland (1996), ApJS 103,467**, [저자 recombination 자료](https://www.pa.uky.edu/~verner/rec.html), [table1.dat](https://www.pa.uky.edu/~verner/dima/rec/table1.dat). 이번 provider SHA256 `74b2a8c30c62f4a50e7c5c4bcf92cb159549ffcb904a3e423a793169c2f2bb27`.
- **W3 — Mao, Kaastra & Badnell (2017), A&A 599,A10**, [논문](https://doi.org/10.1051/0004-6361/201629708). RR energy loss와 number recombination rate의 구분 및 독립 energy-data 필요성을 확인한 원전; 이번 코드에 해당 data를 활성화한 것은 아니다.
- **W4 — Grackle official implementation**, [rate_functions.c](https://github.com/grackle-project/grackle/blob/main/src/clib/rate_functions.c), 실제 확인 Git blob `dfbab661e7c45981eed750baebff140849917152`. 움직이는 main URL과 고정된 열람 blob을 구분한다. Photo fit의 실제 frozen 원전은 inherited vendor의 `phfit2.f` 및 C22A source manifest에 결속되어 있다.
- **W5 — Savin (2002), H/D charge transfer**, [primary paper](https://arxiv.org/abs/astro-ph/0109356). Isotope-specific exchange를 추가할 때 quotient 가정을 재검토해야 하는 근거이며 이번 활성 rate에는 포함되지 않는다.
