# F04L: 약한 shear 응답 차수와 각도 모멘트

## 판정과 범위

Task: BASS-CR-CHAT-F04L_WEAK_SHEAR_RESPONSE_AND_ANGULAR_MOMENTS.
Status: DERIVED_AND_ALGEBRA_CHECKED__FINITE_SHEAR_PHYSICAL_HOLD.

미해결 Bianchi–FLRW 연결에서 스칼라 응답이 선형인지 이차인지, 각도 격자가 그 차수를 왜곡하는지를 연구했다. 첫 macro의 F04K 가열량을 다시 계산하지 않았다. 새 결과는 선형항 소거 조건, 이차 Taylor 계수의 축약 변분계, 실제 각도 header의 모멘트 편향, 같은 이상적 노드의 양의 moment4 가중치와 보존적인 even-cusp 반례다. 실제 물리모형 Q2의 적분·finite-shear remainder·BI macro certificate는 이번에 계산하지 않았다.

bass 시작 및 게시 준비 HEAD=6735bf51d862d3878f5b830df9e74febda8d0a66, 동일 research/r4q-gap-closure-20261001 branch. Receiver=756e1d4f833a1eec454e660b340d3424f3e5d768, forward/rust-reion-kernels-20260922. 이전 a2bc41f 이후 변경은 BI-BLOCK 문서8개다. 새 README와 BLOCK_ERROR_CONTRACT를 읽었으며 owner는 actual BI 첫 transaction 미확보를 보고한다. Header를 복원했다고 그 transaction blocker가 닫힌 것은 아니다. Receiver source/runtime_returns/CODEX_SYNC는 수정하지 않았다.

## 소스 identity

- receiver BI-BLOCK README blob23679959c753d3e64da946d47dcb7edb3c01edc6, contract blob1bda81080bba8a3a458df55bca03970e81a23991.
- paired_runtime.rs blob70eed18b07b6dd4297d8ef8da6d7e1be8e44456e. qhat, source_weights와 fixed-grid transport를 읽었고 원 bytes를 패키지에 보관했다.
- T0_FLRW-header.jsonl: 실제 Dropbox 회수10147bytes, 고정 Git blob5afeefd1dc730e5058fd3759558b67608bd6a5f2와 일치.
- T0_BI-header.jsonl: 실제 Dropbox 회수10145bytes, 고정 Git blob9e2e704162d9cc2ce47d0a5359c960cdfcdcb090과 일치.
- 두 header의128방향과33energy nodes가 동일하다. 원 history/raw transaction 전체는 회수하거나 재실행하지 않았다.
- F04K archive SHA256 bf70472e4a244849d6039586ddec622c66e46adaafa0649fd9ac25c1ca25be51과 CRC를 확인하고 기존 이론·수치 결과는 계승했다.

## 가정과 정의

Signature(-,+,+,+), proper t, H_i=H(1+epsilon*a_i), H>0, sum a_i=0, dimensionless epsilon/a_i. 따라서 nH=nH0 exp(-3Ht)는 epsilon에 독립이다. H_i>0 및 해가 공통 smooth-domain에 머무는 조건을 유지한다. 원자식의 c,kB,eV 환산을 보존하며 hbar를1로 두지 않았다.

정확한 response 정리는 unit ray labels, 양의 고정 b_d(sum b=1), 초기광자 p_d(0)=b_d P(0), epsilon=0 emissivity의 같은 angular base b를 전제로 한다. Energy nodes·원자계수는 고정이고 opacity는 각도에 독립, gas는 총 photon P=sum p_d에만 의존한다. 이는 homogeneous scalar HHe source scope이며 tilted/polarized/angle-dependent opacity로 자동 확장하지 않는다.

    p_dot_d=h_d*K*p_d-D_kappa(G,t)*p_d+w_d*S(t)
    G_dot=f(G,P,t), P=sum_d p_d
    w_d=b_d*J_d/sum_e b_e*J_e, J_d=exp(-3Ht)/g_d^3
    g_d=exp(-Ht)*sqrt(sum_i q_di^2 exp(-2epsilon*H*a_i*t)).

K는 무차원 fixed-grid transport 행렬, kappa는s^-1, photons는per conserved H, S는photons/H/s다. Define tau=Ht, s_d=sum a_i*q_di^2, v_d=sum a_i^2*q_di^2, m1=<s>,m2=<s^2>,n2=<v>.

Taylor convention Y=Y0+epsilon*Y1+epsilon^2*Y2: Y2=Y''(0)/2다.

## 직접 유도: 기하·source와 선형 소거

    h_d/H=1+epsilon*s_d-2epsilon^2*tau*(v_d-s_d^2)+O(epsilon^3)
    w_d/b_d=1+3epsilon*tau*(s_d-m1)
      +epsilon^2*tau^2*[15/2*(s_d^2-m2)-3*(v_d-n2)-9m1*(s_d-m1)]+O(epsilon^3).

Source의 각 비영 차수 weighted sum은0이다. 정규화 분모를 미분하지 않으면 다른 source가 된다.

A0=H*K-D_kappa0에서 mean first variation은

    G1_dot=f_G*G1+f_P*P1
    P1_dot=A0*P1-D_kappa1*P0+H*m1*K*P0.

초기 G1=P1=0이고 m1=0이면 동차 변분계의 유일성에 따라 G1=P1=0이다. Fixed-node HI heat Qdot=c*nH*(1-xHII)*psi^T P, psi=(E-chiHI)*sigmaHI의 Q1도0이다. m1!=0은 선형 forcing을 허용하지만 모든 observable에서 반드시 비영 응답이라는 주장은 아니다.

모든 trace-free symmetric shear의 선형 angular forcing을 없애는 필요충분 angular condition은 sum b_d*q_d*q_d^T=I/3이다. trace(a)=0만으로 유한 구적의 이 조건이 성립하지 않는다.

a=(1,-1,0)이고 x/y 교환 ray permutation이 초기자료·b를 보존하면 epsilon→-epsilon은 그 permutation으로 방정식에 대응한다. 유일해의 scalar는 even이다. 추가 C4 smoothness 아래 Q=Q0+epsilon^2 Q2+O(epsilon^4). Q2가 비영이라는 보장은 없고 일반 shear의 m1=0만으로 모든 odd order가 사라지지도 않는다. 실제 Q2와 고차 remainder 없이 EPS_HALF의1/4 scaling을 승인하지 않는다.

## 이차 응답계

    p_d,1/b_d=P1+(s_d-m1)*Z
    Z_dot=A0*Z+H*K*P0+3tau*S, Z(0)=0
    P2_dot=A0*P2-D_kappa1*P1-D_kappa2*P0
      +H*K*[m1*P1+(m2-m1^2)*Z-2tau*(n2-m2)*P0]
    G2_dot=f_G*G2+f_P*P2+1/2*D2f[Y1,Y1].

kappa2는 opacity의 epsilon^2 계수다. 현재처럼 gas fractions에 affine이면 kappa2=kappa_G*G2. 일반 nonlinear opacity에는1/2*kappa_GG[G1,G1]도 필요하다.

m1=0에서는 mean-first=0이므로 gas Hessian forcing이 사라진다. HI heat의 second coefficient는

    Q2_dot=c*nH*[(1-x0)*psi^T*P2-x2*psi^T*P0].

일반 m1!=0에는 -x1*psi^T*P1도 들어간다. Gas4+active9 형식은 baseline13+Z9+second13=35변수, Q0/Q2까지37변수다. Mean-first13을 남기는 일반계는48변수다. 이는 정확한 Taylor-coefficient reduction이며 finite-epsilon 원1156D nonlinear source 전체를35D로 닫았다는 뜻은 아니다. 구현은 photon coefficient RHS와 moments/helper이고 실제 full gas/heat response integrator 실행은0이다.

## 현재 angular grid의 모멘트 결과

이상적 qhat는 mu_i=-1+(2i+1)/n_mu, phi=2pi(l+1/2)/n_phi다. n_phi>=8,4의 배수에서

    <mu^2>=1/3-1/(3n_mu^2)
    <mu^4>=1/5-2/(3n_mu^2)+7/(15n_mu^4)
    M=diag(1/3+1/(6n_mu^2),1/3+1/(6n_mu^2),1/3-1/(3n_mu^2))
    m1=-a_z/(2n_mu^2).

n_mu=8에서 같은 eigenvalues의 a=(1,-1,0)는 m1=0, a=(1,0,-1)는 m1=1/128이다. Source-defined xy shear의 소거를 회전 불변 구적으로 해석하면 안 된다.

xy shear의 m2=4/15+7/(30n_mu^4),n2=2/3+1/(3n_mu^2). n_mu8에서 m2의 continuum 대비 상대편향은0.0213623046875%, n2-m2는1.287841796875%다. 서로 다른 시간함수 Z/P0에 곱해지므로 이것을 실제 Q2 상대오차라고 부르지 않는다.

실제 저장 qhat의 normalized direction cosines를 exact Fraction으로 평가하면 uniform initial weight의 xy m1=-2.9137729268448255e-17, xz m1=0.007812499999999986(표시값). max|q·q-1|≈2.9110226622249826e-16다. 정확히0 또는unit으로 치환하지 않았다.

Raw q의 source 실수 해석은 epsilon0에서 J=||q||^-3이므로 emissivity base와 uniform initial base도 엄밀히 다르다. 90자리 진단의 weight L1 difference≈1.194035387558675e-16, source-weighted xy m1≈-2.392251827605146e-17이다. 이것은 outward interval이 아니다. 따라서 exact-unit/common-base theorem을 literal header의 완전한 대칭으로 적용하지 않는다. Raw-bit target에는 이 차이를 별도 forcing으로 유지해야 한다.

## 같은 이상적 노드의 양의 moment4 가중치 후보

mu=±1/8,±3/8,±5/8,±7/8 쌍의 총 질량 W에 sumW=1,sumW*mu²=1/3,sumW*mu4=1/5를 부과했다. 원 W0=(1/4,...,1/4)로부터 Euclidean 최소변경해는 C의 행(1,mu²,mu4)에 대해

    W=W0+C^T*(C*C^T)^(-1)*(target-C*W0).

정확한 양의 pair weights는 순서대로34447/126720,10057/42240,2989/14080,35201/126720다. 각±방향에절반,각azimuth16에균등배분한다. 이상적2차·4차sphere tensors가 정확해져 선형 forcing과 이차 coefficient의 tensor-level orientation bias를 제거한다.

현재 producer에 적용하지 않은 선택안이다. Physical quadrature b를 바꾸려면 initial photons와 normalized source를 함께 바꿔야 한다. Error comparison norm의 b만 바꾸는 것으로 physical quadrature error가 수정되지 않는다. Raw-f64 norm defect·고차 angular오차·finite-epsilon오차·기존 certificate 재사용은 승인하지 않았다.

## 보존적인 even-cusp 반례

세 energy nodes Eminus<Ec<Eplus에서 Ec±d의 두packet을 인접node에 선형분배하면

    [psi_h(Ec+d)+psi_h(Ec-d)]/2-psi_h(Ec)
      =|d|/2*[(psi_plus-psi_c)/(Eplus-Ec)-(psi_c-psi_minus)/(Ec-Eminus)].

이 함수는even이지만 일반적으로|d|다. psi=1과psi=E에서는정확0이라N/U보존으로검출되지않는다. 합성nodes(1,2,3),psi(0,0,1)에서는|epsilon|/2이고epsilon반감의응답비는1/2다. Actual T0 remap에cusp가발생했다는관측이나sourcebug판정이아니다. Smoothness 없는finite remap/adaptive map을continuous smooth-response theorem과혼동하지않기위한반례다.

## 실제 검증과 한계

새 focused18tests PASS(1 assertion RED→GREEN,17tests-after). 48합성coefficient사례에서full directional Taylor RHS와reduced P0/P1/P2/Z가exactly일치했다. 24geometry/source derivative와6trigonometric moments,총30개90자리비교의최대표시차≈1.23e-91. Symbolic/exact7조건과Python3파일syntax도PASS다. 정확유리수정본은results/final/RESULTS.json의hex분자/분모이며display숫자와구분한다.

Final verification3명령exit0,scientific/testsource SHA 고정. 재실행한진단의RESULTS bytes는최초것과동일하다. 새native/physicalIVP/syntheticIVP/root/history/old-suites/원자적분/receiver수정은0이다. 초기container서비스오류와directDNS실패는환경기록이며회복/Files회수로실행가능해졌다. 독립human/agentreview와proofassistant는없다.

이론식·positiveweights·cusp는derived,exact coefficient reference는algebraic implementation-verified,고정밀대조는numerically checked다. Actual Q2, finite epsilon remainder, BI macro certificate, native consumer import는미완료다. 새로운physicsPASS나mandatorygate가아니다.

## 정본·이중백업

BASS_CR_CHAT_F04L_20261005_v1.zip:71312bytes,40members/39payload size/SHA256 및CRC local검증.
SHA256=1cc345ca923364590d60a29c70b240e056b849c8c7c3dc8705369f2609573f05.

Drive success ACK 및metadata readback:id17SE-OyJxSRB2Qy2lnVKQ8J3D4SFm7Jdt,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size71312일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzbgA,size71312,modified2026-10-05T15:11:18Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04L_20261005_v1.zip.

동일immutablearchive를두provider에create-only저장했다. R1 UPLOAD_VERIFIED이며remotechecksum은응답에노출되지않았고새ZIP의fullrestore는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git은summary/provenance/backup pointer,code/tests/전체한국어유도/정확결과/로그의정본은ZIP이다. 실제publicationcommit/tree는detachedreceipt에남긴다.

## 종료와 다음 연결

현재약한shear이론단위는종료한다. 다음은owner가선택한정확한source/angularbase에서baseline과response coefficient를연결하는것이다. Raw-bit보존경로에는qnorm/sourcebase차이를forcing으로남긴다. Moment4새source선택은별도owner결정과새provenance가필요하다. Actual Q2와고차remainder 없이EPS_HALF결과를소급승인하지않는다. 기존F04K나이새18시험을단순동기화목적으로반복하지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capturefalse,all_boundOPEN,b_gridNO_GO,actualCRcounter=null유지. FullK/318patch/CR-on/원자실행승인재사용과receiverproductionmutation없음.

표준배경참고: NIST DLMF14.30(spherical harmonics orthogonality),3.5(polynomial quadrature exactness). Source-specificresponse식과고정-nodepositiveweights는REPORT_KO.md에서직접유도했으며문헌상최초결과라고주장하지않는다.
