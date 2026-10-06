# F04M: 서로 다른 초기·방출 각도 가중치를 보존한 약한 shear 응답

## 판정과 이번 진전

Task=BASS-CR-CHAT-F04M_TWO_BASE_RAW_RESPONSE.
Status=DERIVED_TWO_BASE_RESPONSE__NUMERICAL_Q2_REFERENCE__FINITE_SHEAR_HOLD.

F04L의 exact-unit/common-angular-base 제한을 제거한 2차 Taylor 계수계를 직접 유도했다. 원 저장 ray 값의 norm과 초기/방출 가중치 차이를 0으로 바꾸지 않았다. 가스4+활성 photon9에서는 57변수로 계수계가 닫히고, 누적 HI photoheat의 Q0,Q1,Q2를 포함하면60변수다. 이 식을 실제 첫 macro [0,1.25e9]s에서 두 numerical integrator로 적분했다. Q2 reference는 약 -1.4995918922e-14 eV/H, Q1은 약2.8513401011e-25 eV/H다.

두-base 축약은 derived, 64개 합성 방향계 대조는 exact algebraic implementation verification, raw-ray moment 구간은 exact-rational enclosure, 실제 Q 계수는 numerically checked다. Q2의 엄밀한 ODE오차/부호 인증 및 finite-epsilon remainder는 미완료다. 전체 nonlinear BI history나 owner actual transaction을 재현한 결과가 아니다.

## Source와 범위

bass_cr 시작과 게시 직전 HEAD=0b57bd5a29728cfe5ce94af28c0f4733d2e6a44d, branch=research/r4q-gap-closure-20261001. 동일 branch의 새 날짜 폴더에 문서만 추가한다. Receiver=cosmosapjw-quantum/rei_bianchi@87b5aebd442a0e06fe9f9036886a41a8b37e8d98, branch=forward/rust-reion-kernels-20260922. 직전756e1d4 뒤의 변경은 SPEC01 문서8개이며 production source 변경은 없다. Receiver의 frozen-bath spectral 연구를 수신했지만 그 결과를 이번 coupled 응답의 입력으로 쓰거나 재실행하지 않았다. Actual BI 첫 accepted transaction 미확보 상태도 별개로 유지한다.

선택 원문과 Git blob:
- paired_runtime.rs:70eed18b07b6dd4297d8ef8da6d7e1be8e44456e
- ft03_rates.rs:b8a85ff37de160ecc576a168e4259ed23920a499
- T0_FLRW-header.jsonl:5afeefd1dc730e5058fd3759558b67608bd6a5f2
- T0_BI-header.jsonl:9e2e704162d9cc2ce47d0a5359c960cdfcdcb090

선택 bytes를 계승하고 blob을 대조했다. 두 header의128방향과33energy nodes는 동일하다. F04L archive SHA256=1cc345ca923364590d60a29c70b240e056b849c8c7c3dc8705369f2609573f05, slab archive SHA256=0930677e58a01488538bea048a98f872f19c0628875d3fe88ed7c85778b93f86의 전체 archive identity/CRC와 선택 payload hashes를 확인했다. 모든 old 내부 manifest나 과거 science suite를 재검증했다고 주장하지 않는다. 새 SOURCE_BINDING.json이 선택 입력과 실행 소스를 고정한다.

목표는 source-preserving raw-q real-analytic family다. 저장 binary64 q를 정확 실수로 읽되 geometry/rates는 실수 함수로 해석한다. 이는 literal f64 프로그램의 미분이 아니며, epsilon=.01에서 원 BI의 각각 반올림된 H_i 비트까지 같은 family라고 주장하지 않는다. Native producer/원자표/격자/허용오차/물리 angular weight는 변경하지 않았다. Owner runtime import ACK도 미관측이다.

## 두 angular base와 정확 영차 분해

Signature(-,+,+,+), proper t, H_i=H(1+epsilon*a_i), H>0, sum a_i=0. epsilon,a_i는 무차원이다. 근방에서 H_i>0과 공통 smooth solution domain, 고정 energy nodes, 방향 독립 opacity 및 총 photon P에만 의존하는 homogeneous gas를 전제한다. nH=nH0*exp(-3Ht)는epsilon에 무관하다. 수치 예제는 a=(1,-1,0)이다.

r_d=sum q_di^2, s_d=sum a_i*q_di^2/r_d, v_d=sum a_i^2*q_di^2/r_d, tau=Ht로 정의한다. 원 q를 정규화해 덮어쓴 것이 아니라 기하 도함수의 비율이다. Source의 J=exp(-3Ht)/g^3는epsilon0에서r_d^(-3/2)이므로

    alpha_d=1/Nray,
    beta_d=r_d^(-3/2)/sum_e r_e^(-3/2).

alpha는 초기 광자, beta는 영차 방출 가중치다. 이론은 임의 양의 정규화 alpha,beta에도 성립한다. 각각의 s,s^2,v-s^2 모멘트를 m_alpha,m2_alpha,d2_alpha 및 m_beta,m2_beta,d2_beta라 부른다. Delta m=m_alpha-m_beta 등은 정확 구간에서 먼저 빼고 수치계에 전달한다. 큰 모멘트를 각각 float로 반올림한 뒤 tiny difference를 다시 만들지 않는다.

기하와 source Taylor 전개:

    h_d/H=1+epsilon*s_d-2epsilon^2*tau*(v_d-s_d^2)+O(epsilon^3)
    w_d/beta_d=1+3epsilon*tau*(s_d-m_beta)
      +epsilon^2*tau^2*[(15/2)*(s_d^2-m2_beta)
        -3*(v_d-n2_beta)-9*m_beta*(s_d-m_beta)]+O(epsilon^3).

비영 차수의 source 합은0이다. Source 정규화 분모의 미분을 생략하거나 beta를alpha로 대체하면 다른 source다.

Y=Y0+epsilon*Y1+epsilon^2*Y2, Y2=Y''(0)/2를 사용한다. A0=H*K-D_kappa0, P0'=A0*P0+S, U'=A0*U, U(0)=P_initial로 놓으면

    p_d0=alpha_d*U+beta_d*(P0-U).

양변이 같은 선형 방정식과 초기조건을 만족하므로 정확하다. U는 영차 가스 배경에서 최초 광자에 기원한 성분이며, P0-U는 방출에 기원한 성분이다. 가스 feedback는 A0(G0,t)에 남는다.

    S0=sum s_d*p_d0=m_beta*P0+Delta m*U
    T0=sum s_d^2*p_d0=m2_beta*P0+Delta m2*U
    D0=sum (v_d-s_d^2)*p_d0=d2_beta*P0+Delta d2*U.

예를 들어 m_alpha=1/2,m_beta=-1/4,U=2,P0-U=1이면 실제S0=3/4이고 동일base로 잘못 대체한S0=-3/4다. 작은 raw-bit 차이에만 의존하는 주장이 아닌 정확한 부정 대조다.

## 57변수 계수계

T1=sum s_d*p_d1의 가중 첫 변분을 추가한다.

    P1'=A0*P1-D_kappa1*P0+H*K*S0
    G1'=f_G*G1+f_P*P1
    T1'=A0*T1-D_kappa1*S0+H*K*T0+3*tau*(m2_beta-m_beta^2)*S
    P2'=A0*P2-D_kappa1*P1-D_kappa2*P0+H*K*(T1-2*tau*D0)
    G2'=f_G*G2+f_P*P2+(1/2)*D2f[(G1,P1),(G1,P1)].

평균 source2는0이지만 source1의 효과는T1을 통해 전달된다. 현재 opacity는 가스분율에 affine이므로 kappa2=kappa_G*G2다. 일반 nonlinear opacity에서는 추가(1/2)*kappa_GG[G1,G1]가 필요하다.

차원은 baseline13+U9+mean-first13+weighted-first9+mean-second13=57이다. alpha=beta면 기존48변수, 추가m_beta=0이면35변수로 환원한다. 이는 충분한 계수 축약이며 최소차원 정리도, finite-epsilon1156변수 nonlinear state의 physical closure도 아니다.

psi_j=(E_j-chiHI)*sigmaHI_j일 때

    Q0'=c*nH*(1-x0)*psi^T*P0
    Q1'=c*nH*[(1-x0)*psi^T*P1-x1*psi^T*P0]
    Q2'=c*nH*[(1-x0)*psi^T*P2-x1*psi^T*P1-x2*psi^T*P0].

가열까지 포함해60변수다. P는photons/H, Q는eV/H, c=29979245800cm/s이며 EOS/rate에서kB와eV환산도 유지한다. hbar를1로 둔 것이 아니다. Q2는 second derivative 그 자체가 아니라 그 절반이다.

## 원 header의 정확 moment enclosure

정수 isqrt를 이용한 sqrt(1/r_d^3) Fraction 상·하계로 beta를 감쌌다. Native sqrt/pow/normalization 반올림 실행을 감싼 것은 아니다. 소수는 표시이고 정본 끝점은 results/response01/MOMENT_INTERVALS.json이다.

    m_alpha=-2.9137729268448255e-17 (정확 유리수 표시)
    m_beta≈-2.3922518276051458e-17, interval width≈8.78e-81
    m_alpha-m_beta≈-5.2152109923968e-18
    ||alpha-beta||1≈1.194035387558675e-16, width≈2.00e-80.

원 norm/source-base 차이를0으로 버리지 않아도 응답계를 계산할 수 있다. 양의 U,V=P0-U에 대해 ||S0||1<=max(|m_alpha|,|m_beta|)*||P0||1이지만, 이 조건 하나로 전체 가스/가열 선형응답을 인증하지 않는다.

## 실제 first-macro 계수 적분

동일 slab 모형: t0=0,tend=1.25e9s,H=1e-14/s,nH0=1e-4cm^-3,fHe=.083, 초기분율(.9,.3,.6),w0=13.620772387478219eV/H. 초기 .05photons/H at13.7eV와 continuous source5e-15photons/H/s를 유지했다. Active nodes16..24, physical chiHI와 fitcutoff13.6eV를 구분한다. HHe RR/CI/2DR와 gas work를 포함하고 photoabsorption만HI다. 아래 passive photons는 feedback하지 않는 sector이며 가열로 세지 않는다.

새 scalar Jet가 epsilon계수0/1/2를 전파한다. 1차 상태계수1e-16,2차1e-6 등의 명시적 numerical scale로 작은 응답이 absolute tolerance에 묻히지 않도록 했다. 이 과정은 physical angular reweighting이 아니다. 실제 원 순간값의 정확구간 midpoint와 float rate 평가로 수치 적분했으므로 IVP 결과는 interval certificate가 아니다.

|양|DOP853|Radau|
|---|---:|---:|
|Q0[eV/H]|1.1811319285348094e-5|1.181131928534806e-5|
|Q1[eV/H]|2.8513401010788304e-25|2.851340101078821e-25|
|Q2[eV/H]|-1.4995918921977272e-14|-1.499591892196691e-14|
|T0[K]|49995.445413818234|49995.44541381822|
|T2[K]|-3.2254009217213906e-11|-3.2254009216472694e-11|
|xHII2|-9.607847281451016e-16|-9.607847281747687e-16|

DOP853(rtol2e-12,atol2e-14):21steps/317RHS calls. Radau(rtol2e-11,atol2e-13):175steps/1233RHS calls. 각1회 실행했고 전체 새 coefficient IVP는2회다. 영차 배경도 이 두 새계 안에서 적분했으므로 모든IVP0이라고 주장하지 않는다.

Q0/Q1/Q2의 최대 상대 방법차는6.910197971126985e-13이다. 두 방법은 같은 RHS를 공유하므로 이것은 일관성 진단이지 적분오차 상계나 Q2의 엄밀한 부호 인증이 아니다. 짧은firstmacro의 계수를 전체 F08 history의 BI-FLRW 신호로 확대하지 않는다. Finite epsilon의1/4 scaling이나 O(epsilon4)를 승인하지 않았다.

## 검증과 미수행 사항

최종32focused tests PASS,64exact-rational directional coefficient cases PASS,10Python files syntax PASS. 1assertion RED→GREEN,31tests-after다. 별도 mpmath90 scalar derivative99개 최대상대차2.846127179344245e-15, 실제sourceweight128개 정확구간포함, untouched donor point RHS39성분 최대상대차1.9561591299211335e-15를 확인했다. 검산 정밀도를 물리 정확성 자릿수라고 부르지 않는다.

최종명령/exit는 logs/FINAL_COMMANDS.json과07_VERIFIED_TESTS,08_VERIFIED_CHECKS,09_SYNTAX에 보존했다. VERIFICATION.json은 시험 당시10개 source/test SHA를 고정하며 포장에서 불변을 확인했다. 정본 결과는 results/response01과results/FINAL_INDEPENDENT_CHECKS.json이다. 의도적RED 이외 추가 scientific test failure는 없다. Shell의TERM 환경 메시지는 과학 subprocess exit0와 별개다.

새 coefficient IVP2회를 제외한 native, nonlinear finite-shear history, BI raw extractor, 원자 적분, 과거F04L/F04K/receiver suite 및 receiver production mutation은0이다. 독립human/agent reviewer와proof-assistant 검증은 수행하지 않았다.

## 정본과 실제 이중백업

File=BASS_CR_CHAT_F04M_20261006_v1.zip
bytes=167905
SHA256=9b32e24368637c46d6257c5c119de3f5d9cef6be846341d1fc3a66bd03f63dfe
ZIP68members/67payload size/SHA256/CRC를local에서 확인했다. 포장 후 tested code hashes도 일치한다.

Google Drive upload success와metadata readback:id1dwwWb0OdfBENj_h0vK11UGeWRbDOEwwh,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size167905일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzg1Q,size167905,modified2026-10-06T02:02:13Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04M_20261006_v1.zip.

같은immutableZIP을두provider에create-only로저장했다. R1 UPLOAD_VERIFIED(ID/name/size/parent 또는path)이며remotechecksum은응답에노출되지않았다. 새ZIP fullrestore/independent remotebytehash는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git은summary/provenance/backup pointer이고 full code/tests/REPORT/결과의정본은ZIP이다. 실제publicationcommit/tree는detached DELIVERY_RECEIPT에기록한다.

## 다음 남은 이론

이제 동일 raw-target에서 Q1/Q2 적분오차와 유한epsilon Taylor remainder를 제한해야 한다. Raw header에는 exact epsilon-sign symmetry를 가정하지 않으므로 일반 C3 remainder부터 취급한다. Ideal symmetry/C4를 적용하는 target은 별도 정의와 provenance가 필요하다. 새 source나 physical quadrature 선택 없이 유도한 두-base 계수계 자체는 이번에 종료한다. 같은두IVP/32시험을 동기화목적으로 반복하지 않는다.

Actual BI transaction/time-slab certificate는 별도 열린 문제다. Owner import ACK/raw native heat/actualCRcounter는null을유지한다. CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capturefalse,all_boundOPEN,b_gridNO_GO. FullK/318patch/CR-on/소비된원자실행승인재사용과새mandatorygate는없다.

일반 sensitivity 배경은SUNDIALS CVODES공식FSA문서, 수치solver인터페이스는SciPy공식solve_ivp문서를확인했다. 두-base특수축약과수치는본직접유도/계산이며문헌최초결과라고주장하지않는다. 전체문헌URL과입력/출력계약은ZIP에있다.
