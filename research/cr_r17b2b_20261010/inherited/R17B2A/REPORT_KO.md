# R17B2A: 임의 birth의 완전 결합 광자–가스 응답과 물리적 수지

연구일 2026-10-10 KST. 담당 bass_cr만. `FULL_COUPLED_NOMINAL_KERNEL_NUMERICALLY_VERIFIED__CONDITIONAL_REGULARITY_DERIVED__HOMOTOPY_CERTIFICATION_OPEN`.

## 1. 이번에 실제 진행한 물리

R17B1은 실제 source rule의 모멘트·Peano·jump 계수를 계산했지만 FT03 response 자체는 계산하지 않았다. 이번에는 동일 FT03에서 새 광자에 대한 gas–기존 photons의 결합 변분 방정식과 adjoint를 유도하고, nominal six-birth background에서 임의 birth의 광학·온도 response를 실제 적분했다. 기존 단일 7-cohort adjoint의 birth시각 보간을 쓰지 않았다. 별도 probe의 생존율과 직접 gas forcing을 임의 시각에서부터 적분했다.

핵심 결과: (i) 기존 photons의 absorption-delay memory를 빠뜨리면 선형 photon 수지가 닫히지 않는다. (ii) 검사한 b<T의 11개 시각 모두 추가 광자에 대한 최종 tau derivative는 양수, temperature derivative는 음수였다. (iii) 같은 물리적 injection energy의 배경 birth에서 K,K',K''의 jump가 상쇄되는 조건부 정리를 유도했다. 세 번째 derivative의 jump는 일반적으로 남는다. 이 결과는 새 source-error 구간 또는 source homotopy 전체의 부호 인증이 아니다.

## 2. 고정 입력과 계산 해석

Git parent eb692c19c7cef3e3721f1e044ca3d41151d9309d, branch research/cr-r17-recovery-r17b1-20261010. R17B1 ZIP SHA256 95b2cba70b84c3cb53df6f5747504d48a82105389acc464e0421f4711ee11374의 BIRTH_PLAN.json을 불변 사용했다. 읽기전용 REI BRIDGE13 ZIP SHA256 a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48에서 원 FT03 instantaneous RHS, 원 point/AD, 원 초기 state를 선택했다. 선택 파일11개의 원 bytes/hash는 SOURCE_BINDING.json에 있다. 소스 의미는 원 binary64 literal의 실수 해석이고 새 NumPy backend는 그 식의 point-level 근사다. 원 code를 수정하지 않았다.

FT03 HG Case-A H/He CI/RR/two-DR, prescribed FLRW H=f64(1e-14) s^-1, nH0=f64(1e-4) cm^-3, fHe=f64(.083), initial gas=(.9,.3,.6,13.620772387478219 eV/H), photons=.05/H, Eb=13.7eV. 시간창 [0,1.25e9] proper s, 원 여섯 birth 및 nominal weights. 이번 진단은 weight/초기energy family의 nominal 점이며 구간 family 전체가 아니다. HH/RCT/CR OFF. Grackle low-T IGM, CMB/free-free 등 다른 RHS를 추가하지 않았다. FT03의 CI/RR kinetic cooling, two DR cooling, gas expansion work를 유지했다.

실행 좌표 u=t/Tf, gas g=(h,y,z,w/W0), W0=13.620772387478219 eV/H, p_j=photons/H. donor는 p/P0를 사용하므로 독립 Jacobian 대조에서 행·열 scale을 모두 변환했다. 에너지는 E_j(t)=Eb_j exp[-H(t-b_j)], 밀도는 nH0 exp(-3Ht)다. 모든 active energy는 HI fit cutoff 위/HeI cutoff 아래다. 원 매끈한 식에 한정하며 밖의 값은 거절한다.

초기 native history를 rate stage로 재사용하지 않았다. 새로운 nominal nonlinear trajectory를 한 번 만든 후 모든 새 응답이 공유한다. 일곱 photon slot을 미리 할당하되 각 원 birth 전에는 해당 population과 tangent를0으로 둔다. original source birth는 p에만 더하고 gas/tau는 연속이다. coefficient 구간을 midpoint로 바꿔 certification에 쓰지 않는다. 이번은 point diagnostic이며 normalized clock의 binary64 rounding도 interval로 감싸지 않았다.

## 3. 전체 결합 tangent: 즉시 opacity 억제와 지연된 재흡수

이 절의 dot는 proper seconds다. N(g,t)는 원 FT03 nonphoto RHS를 normalized w로 쓴4벡터다. a_j=c_cgs nH sigma(E_j), kappa_j=a_j(1-h), v_j=(1,0,0,(E_j-chiHI)/W0)^T이면

    gdot=N(g,t)+sum_j kappa_j p_j v_j,
    pdot_j=-kappa_j p_j.

새 b에서 deltaM photons/H를 주입하고 deltaM=0의 derivative를 (u,q_j)로 둔다. 새 probe의 단위 생존율 P_b는 P_b(b)=1, Pdot_b=-kappa_b P_b다. 기존 photons의 q_j(b)=0이며 이후 원 birth에서 새로 들어오는 weight의 derivative도0이다. 정확한 tangent는

    udot=J_N u + sum_j v_j[-a_j p_j u_h + kappa_j q_j]
                    +1_(t>=b) kappa_b P_b v_b,
    qdot_j=a_j p_j u_h-kappa_j q_j.

여기에는 opacity가 u_h에 반응하는 즉시 항과 기존 photon population이 달라지는 delayed 항이 모두 있다. probe 자체의 opacity 변화는 deltaM*u에 곱해지는 이차항이므로 first variation에서 따로 더하지 않는다. 기존 background photons의 변화는 first order여서 반드시 남긴다.

동일 식을 적분하면

    q_j(t)=p_j(t) int_(max(b,b_j))^t a_j(s)u_h(s) ds.

즉 gas-only 표현으로 바꾸면 과거 u_h를 기억하는 Volterra 항이 생긴다. u_h가 해당 시간에 비음수라면 q_j도 비음수지만, full thermo-chemical 모형에서 그 부호를 가정으로 강제하지 않았다. full Jacobian은 단순한 양의 행렬이 아니므로 '광자를 더 주었으니 모든 물리변수가 증가'라는 일반 비교정리는 쓰지 않는다.

연속 source에서도 같은 식은 sum을 초기 photon과 p_mu(t,dbeta)의 적분으로 바꾸면 된다. mu_eta=(1-eta)mu_Q+eta mu_S 위의 g_eta와 survival를 실제로 구해야 한다. 이 식을 작성한 것이 eta 전 구간을 계산했다는 뜻은 아니다.

## 4. 기존 photon 수와 photoheat의 정확한 장부

모든 tangent는 단위 추가 photons/H당 값이다. 기존 photon의 누적 absorption 변화는

    deltaA_old=-sum_j q_j(Tf).

따라서 c_e=(1,fHe,2fHe,0)로 두면

    c_e.u(Tf) + P_b(Tf) + sum_j q_j(Tf)
       =1+int_b^Tf c_e.J_N u dt.

오른쪽의 nonphoto electron response도 남아 있다. 식을 h만의 보존식으로 잘못 쓰거나 He를 지우지 않았다.

Q_j(t)=E_j(t)-chiHI이면 Qdot_j=-H E_j이고 기존 photon의 integrated heat response는

    deltaQ_old = -sum_j Q_j(Tf)q_j(Tf)
                 -H int_b^Tf sum_j E_j(t)q_j(t) dt.

여기서 heat는 thermal eV/H이며 총 gas w 차이와는 다르다. 이 항에는 nonphoto cooling/expansion을 다시 더하지 않는다. 첫 항은 아직 흡수되지 않은 photon의 excess energy, 두 번째는 delay로 추가 발생한 redshift energy loss다. q>=0일 때 old-photoheat 변화가 비양수라는 조건부 물리 부호가 성립한다. 이 지연으로 photon number가 생성되는 것은 아니다.

## 5. adjoint와 임의 energy probe

누적 목표는 tau=CT int nH Xe dt, CT=c_SI*sigmaT_SI*1e6; c_SI=299792458m/s,sigmaT=f64(6.6524587e-29)m²,nH[cm^-3]. D=1이며 observer tail=null. lambda_g와 psi_j를 사용하면

    -lambda_g_dot=J_N^T lambda_g
      +sum_j p_j grad_g(kappa_j)(v_j.lambda_g-psi_j)+CT nH c_e,
    -psi_j_dot=kappa_j(v_j.lambda_g-psi_j),
    lambda_g(Tf)=0, psi_j(Tf)=0.

기존 photon feedback는 gas adjoint에도 남는다. 임의 b의 response는 original source node를 보간하지 않고

    K_mu(b)=int_b^Tf P_mu(t,b) kappa_mu(t,b) v(t,b).lambda_g,mu(t) dt

로 계산한다. 이것은 전체 결합 배경에서의 Fréchet tangent이다. numerical backend에서는 tau_scale=CT*nH0*Tf를 분리해 작은 광학 수치를 안정적으로 적분한 후 물리값으로 환산했다.

단일 nominal K_muQ를 int K d(muS-muQ)에 넣는 것만으로 유한 source 오차가 인증되지 않는다. 정확한 finite-source identity는 int_0^1 deta int K_mueta(b)d(muS-muQ)(b)이며, eta=0만 사용하는 경우 별도 remainder가 필요하다. 이번에는 그 적분/나머지/구간 인증을 하지 않았다.

## 6. 새 정칙성 결과: 같은-energy birth에서 0–2차 jump는0

가스 상태와 배경이 연속이고, cutoffs/thermal branches를 지나지 않으며, 비광이온화 RHS와 energy dependence가 필요한 만큼 매끄럽다고 하자. photon adjoint를 현재 physical energy 좌표의 psi(t,E)로 확장하면

    (partial_t-H E partial_E)psi=kappa(psi-v.lambda_g),
    K(b)=psi(b,Eb).

배경의 t=a에서 weight w_*가 동일 energy Eb로 들어온다. gas는 연속이고, adjoint도 additive jump의 transpose map(identity on old state)에 따라 연속이다. 그러므로 [K]=[K_b]=0이다. R=psi-v.lambda_g, k_g=grad_g kappa로 두면

    [gdot]=w_* kappa v,
    [lambda_g_dot]=w_* k_g R,
    [partial_t kappa]=w_* kappa(k_g.v).

또한 energy derivative의 필요한 trace가 연속이면

    [K_bb]=[kappa_t]R-kappa v.[lambda_g_dot]
          =w_*kappa(k_g.v)R-w_*kappa(v.k_g)R=0.

따라서 **현재 같은13.7eV source 채널의 알려진 여섯 impulse에서 K,K',K''는 연속**이다. 이 cancellation은 단순 frozen-medium approximation이 아니라 background photon의 변화와 adjoint 변화가 함께 들어가 생긴다. 다른 energy의 background birth와 probe이면 두 항의 커널/energy yield가 달라져 일반적으로 상쇄되지 않는다. 코드가 그 경우를 자동0으로 만들지 않도록 exact 반례 시험을 했다.

이 명제는 각 eta의 smooth coupled solution이 존재한다는 조건 아래 source homotopy에도 같은 형태로 적용된다. 그러나 그 조건을 새 interval backend로 증명하지 않았으며 모든 source/threshold event의 정칙성을 자동 승인하지 않는다. known same-channel event에서만 R17B1의 J0,J1,J2 필요항이0으로 정리된다. J3 및 regular fourth derivative는 여전히 외부 인증이 필요하다.

단순 HI toy xdot=-rho*x²+a(1-x)p, pdot=-a(1-x)p, goal_dot=c*x에서도 symbolic adjoint derivative의0,1,2차 jump는0이고 세 번째는 일반적으로 비영이다. exact local 값(x=.9,p=.05,lambda_x=.5,lambda_p=.25,a=2,rho=.1,c=1,w=.01)에서 -93/20000을 얻었다. 이는 국소 대수 반례이며 FT03의 실제 J3 값이나 같은 terminal adjoint의 수치해가 아니다. 과거 potential-event 계수를 물리 jump로 재명명하지 않는다.

끝점에서는 새로운 광자가 즉시 optical integral을 바꾸지 않는다. smooth positive kappa에서

    K(b)=0.5*CT*nH(Tf)*kappa(Tf,Eb)*(Tf-b)^2+O((Tf-b)^3).

따라서 Tf에서 K=K_b=0이고 충분히 늦은 birth의 leading response는 양수다. recombination과 기존-photon memory는 더 높은 시간차수에 들어간다. 이 국소 결론으로 모든 b의 양성을 증명하지는 않는다.

## 7. 실제 FT03 진단

새 nominal background를 DOP853으로 seven birth-free 구간에서 적분했다. 초기w와 particle density로 회수한 온도는50000K, 최종은49995.445413982765K이다. 생산 native가 아니라 source-authentic NumPy/complex-step point backend이며 원 donor의6개 실제 점에서 RHS66성분, Jacobian726성분을 separately implemented Decimal/AD와 대조했다. 최대 상대차는5.66423e-16(RHS),2.12326e-14(Jacobian)다. 이는 점/구현 대조이며 interval RHS 정확성 인증이 아니다.

12개 arbitrary birth query 중 b<T 11개에서 최종 optical derivative가 양수, 온도 derivative가 음수였다. b=Tf는 정확0. 원6개 birth를 포함하지만 new arbitrary query 0,.1Tf,.3540127993818848Tf,.5Tf,.8Tf 등도 포함한다.

| b/Tf | K_tau [tau/(photons/H)] | dT(Tf)/dM [K/(photons/H)] |
|---:|---:|---:|
|0|2.901833668679391e-12|-54.30936085364431|
|0.1|2.350559408445196e-12|-48.88434335210891|
|0.3540127993818848|1.211068846901555e-12|-35.09819197498|
|0.5|7.255728284584664e-13|-27.17112268835075|
|0.8|1.161026365179018e-13|-10.87239605860100|
|0.9824162146151559|8.97494555047066e-16|-0.9561004252569661|

이 표의 '단위 source'는 derivative의 정규화이며, 실제1 photon/H를 유한하게 주입한 linear-validity 보장이 아니다. 기존 총초기량 .05/H와 비교해 큰 유한 변화에는 그대로 적용하지 않는다.

예를 들어 b=442515999.227356s에서 단위 probe survival=.9984960812406785, background retained photons=5.651546980543308e-7, old-photoheat=-5.732423778432305e-8 eV, 추가 redshift energy=2.085288837133252e-11 eV다. 직접 probe heat는+1.52662957330216e-4 eV다. electron closure에는 nonphoto charge response -4.143266524225051e-8도 포함된다. 조건부 수지식의 최대 잔차는 모든 query에서2.87271e-16(count),1.66007e-21 eV(old heat)다.

온도 부호의 기초는 D=1+fHe+Xe, T=2w/(3kB_eV D)다. 직접 primary photo event만의 순간 변화는

    Tdot_photo = 2*Rph/(3*kB_eV*D)*[(E-chiHI)-1.5*kB_eV*T].

원 초기50000K에서1.5kBT=6.4629999466eV, excess=0.101565400298eV, ratio=.01571490038다. 따라서 열에너지는 증가해도 새 전자가 늘리는 particle count 때문에 온도는 내려갈 수 있다. 실제 terminal negative derivative에는 full CI/RR/DR 및 work feedback도 계산에 포함돼 있다. 일반적인 cosmic-ray heating 또는 Grackle reionization의 결론으로 확대하지 않는다.

전체 전방 tangent와 gas–photon adjoint+별도 arbitrary probe integral의 최대 상대차는4.15309e-14다. 두 경로는 같은 numerical background와 Jacobian을 공유하므로 독립 physical solver 두 개의 일치는 아니다. 별도 positive-dose1e-3,5e-4,2.5e-4/H를 b=.354...에서 주입한 nonlinear 진단의 optical derivative 상대차는5.01517e-6,2.50630e-6,1.25393e-6으로 감소했다. 이는 finite variation 검산이며 ε→0 오차 증명이나 새 source-error bound가 아니다.

local-opacity-only control은 qdot의 gas coupling을 제거하되 즉시 -a*p*u_h 항은 남긴 인위적 비교다. full K와 상대차는 b=0에서2.26175e-7로 작지만, 이 control은 photon 수지를 깨므로 certified fallback으로 사용할 수 없다. memory가 작다는 유한점 관측을 uniform smallness로 바꾸지 않는다.

late query의 K/(1-b/Tf)^2는 이론 endpoint 계수2.902748984287316e-12의0.999994455052배다. 유한 b에서의 asymptotic 검산일 뿐 regular fourth derivative 상계는 아니다.

## 8. 검증, 실행 횟수, 남은 조건

새 고유 unit tests18 PASS; 기존 photons의 response를0으로 누락하는 실제 assertion RED→GREEN1개/나머지17개 tests-after. 산출물 검사30개, point/AD independent 비교6점(66+726성분), exact jump/heat identities와 세 번째 derivative 반례를 수행했다. original6 birth의 gas continuity, local Kbb exact cancellation, original photon adjoint와 arbitrary probe integral의 대조도 포함된다.

최종 데이터셋은 nominal nonlinear base1개, positive-dose nonlinear3개, nonzero forward tangent11개와 artificial memory-off tangent11개, coupled backward adjoint1개, arbitrary probe integral11개다. endpoint zero는 적분 없이 계산한다. source homotopy η 전체는0회, 새 native0회, 원 root/기존 scientific suite0회다. 개발 출력/최종 telemetry 추가/새 폴더 재현의 실행을 별도 구분해 VERIFICATION.json에 기록한다. 이 새로운 경량 계산을 '새 IVP0회'라고 보고하지 않는다.

원 입력 상계·R17A source certification·R16B 시간 certification은 재실행/변경하지 않았다. 이번 full coupled nominal K 숫자는 η=0이고 parameter-family 및 continuous-emission source의 uniform derivative가 아니므로 새 source/전체 tau certified intervals는 null이다. 물리적 atom fit 정확성도 미인증이다. 독립 인간/에이전트 reviewer와 proof assistant는 수행하지 않았다.

다음 NCP는 이번 point/tangent 구성을 재구현하지 않고 interval화하고, 같은 source homotopy의 continuum photon population까지 포함해야 한다. 실제 common tube/regularity premise를 확보한 뒤 known same-energy impulse의 J0=J1=J2 cancellation을 적용하고, J3와 regular K''''를 감싸 R17B1 Peano에 전달한다. 그렇지 않으면 NO_CERTIFIED_SOURCE_SHARPENING이다. 물리적 convergence와 kernel arithmetic/point agreement를 분리한다.

CR_OFF_FASTEST, HH research ACTIVE, precision atomic PARKED, G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, physical/production HOLD. Grackle owner-input 및 G02 bank blocker, observer tail/owner ACK/global CRcounter=null 유지. 다른 repo mutation 없음.

## 문헌과 출처

FT03 실행식의 SSOT는 위 pinned donor source다. D.A. Verner et al., ApJ465,487(1996), DOI10.1086/177435, 저자원자료 https://www.pa.uky.edu/~verner/photo.html 는 단면적 fit의 문헌 배경이다. L.Hui & N.Y.Gnedin, MNRAS292,27(1997), arXiv:astro-ph/9612232는 photoionized IGM의 thermal equation과 원 H/He 계수의 배경이다. 이 문헌의 다른 업데이트나 물리모형을 원 code에 자동 교체하지 않았고, 본 새 memory/adjoint/정칙성 유도와 실제 수치는 본 구현·검산에서 나온 것이다. 문헌이 본 diagnostic을 인증하거나 세계최초 결과라고 주장하지 않는다.
