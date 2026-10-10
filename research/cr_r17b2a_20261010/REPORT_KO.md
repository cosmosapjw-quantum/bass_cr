# R17B2A: 임의 birth의 완전 결합 광자–가스 응답

2026-10-10 KST. 상태: FULL_COUPLED_NOMINAL_KERNEL_NUMERICALLY_VERIFIED__CONDITIONAL_REGULARITY_DERIVED__HOMOTOPY_CERTIFICATION_OPEN.

이 파일은 게시용 요약이다. 전체 유도·원 입력·시험·결과·실패 기록과 재현기는 봉인 ZIP에 있다. Git의 4개 core만으로 원 입력이 포함된 완전한 checkout이라고 주장하지 않는다.

## 실제 신규 물리

기존 R17B1은 source 모멘트/Peano/jump 계수까지만 계산했다. 이번에는 동일 FT03 nominal six-birth 배경의 nonlinear IVP를 새로 적분하고, 임의 birth의 probe survival과 gas–기존 photon tangent 및 adjoint를 실제 계산했다. 기존 7개 photon adjoint를 임의 birth에 보간하지 않았다.

원 모형: FT03 HG Case-A HHe CI/RR kinetic cooling/two DR/gas expansion, prescribed FLRW H=f64(1e-14)/s, nH0=f64(1e-4)/cm3, fHe=.083, initial fractions=(.9,.3,.6), initial w=W0=13.620772387478219 eV/H, initial photon=.05/H, Eb=13.7eV. 처음 1.25e9 proper seconds. HH/RCT/CR OFF. Grackle/CMB/free-free를 추가하지 않았다. 이 계산은 weight/energy family의 nominal 점이며 전체 parameter interval이 아니다.

원 R17B1 archive 95b2cba70b84c3cb53df6f5747504d48a82105389acc464e0421f4711ee11374와 REI BRIDGE13 archive a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48의 선택11개 source/input bytes를 고정했다. 원 소스는 수정하지 않았다.

## 완전 결합 변분과 수지

g=(h,y,z,w/W0), a_j=c nH sigma(E_j), kappa_j=a_j(1-h), v_j=(1,0,0,(E_j-chiHI)/W0). dot는 proper seconds다.

    gdot=N(g,t)+sum kappa_j p_j v_j; pdot_j=-kappa_j p_j.
    udot=JN u+sum v_j*(-a_j p_j u_h+kappa_j q_j)+kappa_b P_b v_b.
    qdot_j=a_j p_j u_h-kappa_j q_j; Pdot_b=-kappa_b P_b; P_b(b)=1.

probe가 gas opacity를 바꾸는 자기항은 probe mass와 gas tangent의 곱이므로 first variation에 없다. 반면 기존 photons의 opacity/stock 변화는 first order다. q_j(t)=p_j(t)*integral_(max(b,bj))^t a_j u_h ds이며 gas-only 식에는 Volterra memory가 생긴다. 이를 지우는 비교는 인위적이고 photon conserving 대체모형이 아니다.

ce=(1,fHe,2fHe,0)일 때

    ce.u(T)+P_b(T)+sum q_j(T)=1+integral ce.JN u dt.
    deltaA_old=-sum q_j(T).
    deltaQ_old=-sum (E_j(T)-chiHI)q_j(T)-H*integral sum E_j q_j dt.

마지막 식의 두 항은 아직 흡수되지 않은 초과에너지와 지연에 따른 추가 redshift 손실이다. q>=0이면 기존 photons의 deposited photoheat 변화는 비양수다. 총 gas thermal energy와 혼동하지 않는다.

## Adjoint와 정칙성

CT=c_SI*sigmaT_SI*1e6, tau=CT*integral nH Xe dt, Xe=h+fHe(y+2z).

    -lambda_g_dot=JN^T lambda_g+sum p_j grad(kappa_j)*(v_j.lambda_g-psi_j)+CT*nH*ce.
    -psi_j_dot=kappa_j*(v_j.lambda_g-psi_j).
    K_mu(b)=integral_b^T P_mu(t,b)*kappa_mu(t,b)*v(t,b).lambda_g,mu(t)dt.

terminal lambda=psi=0. 모든 배경 cohort의 변분이 포함된다. mu_eta=(1-eta)mu_Q+eta*mu_S 전체를 적분하거나 finite-source remainder를 감싸야 실제 source 오차가 된다. 이번은 eta=0의 numerical K다.

새 조건부 정리: gas와 energy coefficient가 매끄럽고 cutoff/다른 branch가 없으며 additive background birth가 probe와 같은 Eb이면 K,K',K''가 그 birth에서 연속이다. 현재 energy의 adjoint psi에 대해 (partial_t-H E partial_E)psi=kappa*(psi-v.lambda_g). R=psi-v.lambda_g, kg=grad_g(kappa)라 두면 [gdot]=w*kappa*v, [lambda_g_dot]=w*kg*R, [kappa_t]=w*kappa*(kg.v). 따라서 [Kbb]=[kappa_t]*R-kappa*v.[lambda_g_dot]=0. 필요한 energy trace의 매끄러움은 외부 전제이며 전체 homotopy에서 새 interval 증명을 수행한 것은 아니다.

K'''는 일반적으로 jump가 남는다. 작은 HI local symbolic 반례에서 -93/20000을 얻었지만 이는 FT03의 J3 값이 아니다. 다른 energy의 birth에서는 K'' 상쇄도 일반적으로 성립하지 않는다. 늦은 birth에는 K(b)=0.5*CT*nH(T)*kappa(T,Eb)*(T-b)^2+O((T-b)^3). 전 구간 양성정리로 확대하지 않는다.

## 실제 수치

새 nominal background 최종 T=49995.445413982765K. b<T의11개 query에서 K_tau>0, final temperature derivative<0; b=T는 정확0이다. 아래 값은 단위 photons/H당 derivative이며 실제1/H 유한 주입 예측이 아니다.

| b/T | K_tau | dTfinal/dM [K/(photons/H)] |
|---:|---:|---:|
|0|2.9018336686793906e-12|-54.309360853644314|
|.3540127993818848|1.211068846901555e-12|-35.09819197498|
|.5|7.255728284584664e-13|-27.171122688350753|
|.8|1.1610263651790176e-13|-10.872396058601003|
|.9824162146151559|8.97494555047066e-16|-0.9561004252569661|

b=.354...에서 probe survival=.9984960812406785, existing retained photon=5.651546980543308e-7, old photoheat=-5.732423778432305e-8 eV, extra old redshift=2.0852888371332522e-11 eV이다. ce 수지에는 nonphoto charge response도 남는다.

D=1+fHe+Xe이고 직접 photo Tdot=2 Rph/(3 kB_eV D)*[(E-chiHI)-1.5 kB_eV T]. 초기 T50000K에서1.5kBT=6.4629999466eV, E-chiHI=.101565400298eV다. 그러므로 열에너지 증가는 온도 증가와 다르다. 표의 최종 derivative에는 full nonphoto feedback도 포함되지만 selected nominal samples이지 전체 birth/source-family 부호 인증은 아니다.

## 검증·실행 횟수

18개 고유 unit tests, 실제 assertion RED→GREEN1/17tests-after, 30개 산출물 조건, Python10파일 syntax PASS. 원 donor point/AD6점에서 RHS66/Jacobian726성분의 최대 상대차5.66423e-16/2.12326e-14다. 별도 구현의 point 대조이지 independent interval RHS backend가 아니다.

전방 tangent와 후방 adjoint+probe integral 최대 relative gap4.15309e-14. photon/charge 수지 최대잔차2.87271e-16, old heat identity1.66007e-21eV. Positive finite doses .001,.0005,.00025/H에서 optical derivative 상대차5.01517e-6,2.50630e-6,1.25393e-6. 오차상계 인증이 아니다.

고유 nonlinear trajectories4개(배경1+positive dose3), full tangent11, artificial memory-off controls11, background adjoint1, probe integrals11. 개발/최종telemetry/새폴더재현3회로 실제 nonlinear runs12회이며 독립 데이터셋으로 합산하지 않는다. source homotopy0, native0, old suites0, 타repo mutation0. fresh reproduction exit0,5science JSON byte-identical,7.65s/161564KiB. 외부심사/proofassistant 미실행.

## 정본과 배포

새 core4개는 science commit18948fcbdb51f8a26bb2f0aa6b4ffcff05e27be0에 게시했다. Parent eb692c19c7cef3e3721f1e044ca3d41151d9309d. Blob metadata가 시험한 bytes와 일치한다.

전체 ZIP BASS_CR_R17B2A_20261010_v1.zip:143722bytes,SHA256 e46cb3d29c67abbe776324a19f22add884fd6bcedb0e58947cbf5b7d54d5cc89,56entries/55payloads CRC/SHA 검증. Drive1LbC2uPEXzHLNZjwidCKC9IsOi9NyDgjj와 Dropbox id:BSpOijBcT10AAAAAAD3uMw는 실제 ACK/name/size/parent-path 일치. R1_DUAL_PROVIDER_UPLOAD_VERIFIED, remote checksum 미제공/full restore 미실행. 봉인본의 PENDING는 당시 상태이며 이 후속반환이 배포상태를 기록한다.

다음 R17B2B는 tested core를 재구현하지 않고 interval화하여 전체 source homotopy/continuum photon population의 common tube를 증명하고 J3와 regular fourth derivative를 R17B1에 전달한다. 새source certificate는 아직null, 이전 R17A/R16B 불변. CR_OFF_FASTEST,precisionatomicPARKED,HH ACTIVE,G02UNRESOLVED,b_gridNO_GO,all_boundOPEN,physical/productionHOLD,observer tail/ownerACK/globalCR=null을 유지한다.
