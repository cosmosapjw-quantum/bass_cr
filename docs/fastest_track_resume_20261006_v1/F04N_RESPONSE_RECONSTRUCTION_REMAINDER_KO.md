# F04N: 응답 재구성의 가열 잔차와 유한 shear 입력 나머지

## 판정과 이번에 닫은 범위

Task=BASS-CR-CHAT-F04N_RESPONSE_RECONSTRUCTION_AND_REMAINDER.
Status=ANGULAR_LIFT_AND_PARAMETER_DEFECT_DERIVED__GOAL_RECONSTRUCTION_RESIDUAL_ENCLOSED__STATE_ERROR_OPEN.

F04M의 raw-q 실수 모형과 저장된 21개 계수해 표본을 계승했다. 새 IVP 없이 방향별 이차 계수의 충분한 복원식, 기하·정규화 source의 균일 삼차 나머지, photon/heat의 정확한 polynomial defect를 유도했다. 같은 표본에 새 cubic Hermite 재구성을 만들고 가열 계수 방정식의 잔차를 전체20개 시간구간에서 감쌌다. Q2의 이 goal-equation residual 적분 상계는 약2.6140897145e-21 eV/H다.

이 숫자는 가스·광자 계수해의 오차를 포함하지 않는다. Q2 전체 적분오차·엄밀한 부호·유한 shear 해의 Taylor remainder는 여전히 미완료다. 이미 수행한 두 수치 적분의 일치를 엄밀한 오차 상계로 바꾸지 않았다. Geometry input remainder, polynomial heat insertion remainder, 실제 해의 remainder도 별개다.

## 입력·최신 상태와 변경 경계

bass_cr 시작/게시 직전 HEAD=f2fd576426f11f18d407dc0f42a5306cea5e1094, tree=120af521762468fcf95ab1e22ce227e75c33f647, branch=research/r4q-gap-closure-20261001. 동일 branch에 새 문서만 추가한다. Receiver HEAD=06c16abde5df6b48da1382a6a5c56706d8d0ce3d, branch=forward/rust-reion-kernels-20260922. Receiver의 새 SPEC02 nonautonomous spectral/feedback 결과는 별도 연구로 수신했으며 그 모형·결과를 F04M 응답계에 가져오거나 재실행하지 않았다. Actual BI 원 transaction-dependent 인증과 consumer import는 별도 열린 문제다.

정본 입력 BASS_CR_CHAT_F04M_20261006_v1.zip은167905bytes, SHA256=9b32e24368637c46d6257c5c119de3f5d9cef6be846341d1fc3a66bd03f63dfe다. Archive identity와 필요한14개 선택 payload를 확인해 원 bytes로 보존했다. inputs/SELECTED_INPUTS.json이 경로/크기/SHA를 고정한다. 원 header128방향,33노드, active16..24와 가스4변수, 초기 alpha=1/128, 방출 beta=norm(q)^(-3)/sum norm(q)^(-3)를 유지한다. 작지만 비영인 raw 모멘트·초기/source base 차이를0으로 만들지 않는다.

저장된 scaled 표본과 scale을 각각 정확 binary64 실수로 읽어 곱했다. 과거 state_unscaled의 중간 반올림값과 같다고 강제하지 않았다. 같은 donor RHS를21개 표본에서 새로 평가해 float slope를 만들고 그 slope를 정확 수로 고정했다. 이는 새 재구성의 정의이며 원 solver의 dense output을 회수한 것이 아니다. IVP 재적분0, 새 coefficient RHS 평가21이다. 코드·모형·raw input·production source·허용오차·물리 quadrature는 변경하지 않았다.

## 1. 방향별 이차 복원식

H_i=H(1+epsilon*a_i), sum a_i=0, H>0, tau=Ht, r_d=sum q_di^2, s_d=sum a_i*q_di^2/r_d, v_d=sum a_i^2*q_di^2/r_d다. Signature(-,+,+,+), t는proper s다. 기존 A0=HK-D_kappa0에서 영차 p_d0=alpha_d U+beta_d V, U+V=P0를 계승한다.

평균 계수 P0/P1/P2만으로 finite-epsilon 전체 방향계 잔차를 계산할 수는 없다. 예를 들어 p2=(1,-1), s=(1,-1)이면 sum p2=0이지만 sum s*p2=2다. 이후 삼차 transport forcing에는 이 모드가 보인다.

충분한 방향별 복원은 다음14개의 energy-vector mode로 표현된다.

    p_d0 = alpha_d U + beta_d V
    p_d1 = alpha_d(a0+s_d a1) + beta_d(b0+s_d b1)
    p_d2 = alpha_d(c0+s_d c1+s_d^2 c2+v_d cv)
           +beta_d(d0+s_d d1+s_d^2 d2+v_d dv).

각 모드의 ODE는 REPORT_KO.md와 src/lift.py에 있다. Source의 정규화 분모 미분을 유지한다. m=<s>beta,m2=<s^2>beta,n2=<v>beta이며, source2의 constant/s/s²/v 계수는 tau²(3n2-15m2/2+9m²), -9tau²m, (15/2)tau², -3tau²다. Uinitial=Pinitial, 나머지mode initial0이다.

가스 coefficient3개까지14n+3g=138변수, Q0/Q1/Q2 포함141변수의 충분한 lift다. 최소차원 정리가 아니며 이번141변수 계를 적분하지 않았다. src/lift.py는 공급된 opacity jets의 photon lifting RHS를 구현한다. 기존57변수 mean coefficient reduction의 유효성도 취소하지 않는다. 정확 합성64사례에서 직접 방향별 RHS 및 cubic/quartic tail과3840개 항등식을 검사했다.

## 2. 기하와 정규화 source의 균일 삼차 나머지

A=max|a_i|, |epsilon|<=rho, rho*A<1을 둔다. Positive H_i와 기존 fixed-node/smooth-domain 범위다. F_d(z)=sum(q_di²/r_d) exp(-2a_i z), z=epsilon*tau를 정의하고 tilted mean mu를 사용하면 mu'=-2Var(a), mu''=4 central_moment3(a)다. Var<=A²와 |central_moment3|<=2A³로

    |h_d/H-[1+epsilon*s_d-2epsilon²*tau*(v_d-s_d²)]|
       <=4*A³*|epsilon|³*tau².

정규화 source weights w_d=beta_d exp(f_d)/sum beta exp(f), f_d=-(3/2)ln F_d에 대해 직접 분모까지 미분했다. |f'|<=3A, -6A²<=f''<=0, |f'''|<=24A³를 사용하면 sum|w'''(z)|<=615A³다. 따라서

    ||w-w_[2]||1 <= (205/2)*A³*|epsilon*tau|³.

상수 nonnegative source S에서는0..T의 cumulative source redistribution bound가

    (205/8)*S*A³*|epsilon|³*H³*T⁴

다. 이것은 source 입력의 Taylor remainder이며 가열/가스 해의 remainder가 아니다. Raw alpha/beta equality나 exact epsilon-sign symmetry가 필요하지 않다.

분석용 rho=1/100, A=1, 기존 H=1e-14/s,T=1.25e9s,S=5e-15photons/H/s literal의 exact-real 값에 대입한 표시값:

- h/H remainder upper:6.25e-16
- h remainder upper:6.25e-30/s
- source weight L1 remainder upper:2.001953125e-19
- cumulative source redistribution upper:3.1280517578125e-25photons/H.

이 rho를 owner가 승인한 새 물리 domain으로 표현하지 않는다. epsilon=.01이 실제 BI의 각각 반올림된 H_i와 비트상 일치한다는 주장도 아니다. 정확 유리수 끝점은 results/final/CERTIFICATE.json에 있다.

## 3. Photon과 가열의 정확한 polynomial defect

현재 affine opacity에서 kappa(G_[2])=kappa0+epsilon*kappa1+epsilon²*kappa2다. d_d=v_d-s_d²로 쓰면 quadratic state를 대입한 photon RHS의 추가 polynomial 항은

    T3_d=H*s_d*K*p_d2-2H*tau*d_d*K*p_d1-kappa1*p_d2-kappa2*p_d1
    T4_d=-2H*tau*d_d*K*p_d2-kappa2*p_d2.

따라서 전체 photon 재구성 잔차는 r0+epsilon*r1+epsilon²*r2에서 epsilon³T3+epsilon⁴T4+r_h*K*p_[2]+r_w*S를 뺀 것이다. r_h,r_w는 위 입력 나머지다. Nonlinear thermal RR/CI/DR의 gas defect를 이것으로 대체하지 않는다.

Heat는 a(t)=c*nH(t), Wk=psi^T*Pk, psi_j=(Ej-chiHI)*sigmaHI_j로 놓으면 a(1-x)W다. Quadratic state insertion의 계수는

    q0=a*(1-x0)*W0
    q1=a*((1-x0)*W1-x1*W0)
    q2=a*((1-x0)*W2-x1*W1-x2*W0)
    q3=-a*(x1*W2+x2*W1)
    q4=-a*x2*W2.

위 degree4 전개는 정확하다. q3/q4는 quadratic 재구성을 가열식에 넣어서 생긴 항이지 실제 해의 완전한 Q3/Q4가 아니다. 참해의 x3,P3 등의 영향은 state remainder에 남는다. Parameter second coefficient는 여전히 Y''/2다.

## 4. 실제 저장 표본의 전 시간구간 goal 잔차

원 첫 macro0..1.25e9s의21개 표본으로 affine 및 cubic Hermite 곡선을 정의했다. 새 RHS21회는 Hermite slope 정의에만 사용했다. 각20개 시간cell의 local coordinate u∈[0,1]에서 state polynomial은1차 또는3차이고 q_k는 exp(-gamma-alpha*u)와 최대6차 다항식의 곱이다.

Signed integral은 exact alternating exponential moments의20/21차 bracket으로 계산했다. Uniform residual은 exp(-alpha*u)를12차 polynomial+명시적 tail로 대체한 뒤 Q polynomial의 미분과 coefficient 단계에서 뺐다. Power coefficient a_i를 Bernstein coefficient b_k=sum_(i<=k) binom(k,i)/binom(n,i)*a_i로 변환하고 convex-hull 범위를 사용했다. 구간 끝점 몇 개만 검사한 결과가 아니라 각 cell 전체를 감싼 결과다.

    B_quad,k >= integral_0^T |hatQ_k'(t)-q_k(t,hatY0,hatY1,hatY2)|dt.

새 polynomial/moment/Bernstein 연산은 Fraction으로 정확 수행했다. Sigma는 같은 analytic-real Verner 식의 변경하지 않은 donor Decimal60 interval primitive에 의존한다. Float slope가 정확미분이라는 전제는 필요 없으며 임의의 고정 재구성 slope여도 잔차를 계산할 수 있다. Primitive 자체의 formal verification은 없다.

다음 표의 소수는 표시용이며 단위는eV/H다.

|가열 계수 residual budget|Affine|Cubic Hermite|
|---|---:|---:|
|B_quad,0|1.5191899526127329e-9|3.025568003485535e-18|
|B_quad,1|1.42410332868766e-26|3.54623386062397e-35|
|B_quad,2|1.1410360807628496e-15|2.614089714503771e-21|

Hermite q2 적분은 표시값 -1.4995918921856968e-14 eV/H다. 저장 Q2 increment와 이 적분 사이 signed defect는 약 -1.2030263098787902e-25 eV/H다. Signed integral의 상쇄와 integral absolute residual budget은 다른 값이다. 두 값 모두 상태계수해가 정확하다는 보증은 아니다.

rho=.01에서 Hermite quadratic state를 heat식에 대입한 직접 cubic/quartic 항의 integral absolute bound는7.197962439801705e-37eV/H 이하의 표시값, 느슨하게7.1980e-37eV/H 미만이다. 실제 유한-shear 가열해의 나머지가 이 숫자보다 작다고 주장하지 않는다.

## 5. 전체 coefficient 및 finite-epsilon 인증에 남는 항

공통 coefficient tube에서 정확한 state-error b0,b1,b2와 q2의 block Lipschitz columns L20,L21,L22가 검증되면

    |Q2_true(T)-hatQ2(T)|
      <=initial_goal_error+B_quad,2
        +integral(L20*b0+L21*b1+L22*b2)dt.

현재 계산한 것은 B_quad,2다. b0/b1/b2는 미인증이며 이를0으로 대체하지 않는다. Baseline error가 first/second response를 구동하고 tiny moment의 midpoint/interval 차이도 forcing으로 들어간다. REPORT에는 triangular block comparison과 각 goal gradient를 적었다. 같은 donor endpoint/root width를 continuous coefficient error로 바꾸지 않는다.

Finite epsilon에서 방향별 quadratic reconstruction의 defect와 공통 scaled convex tube가 있으면 b_epsilon'=M_epsilon*b_epsilon+|d_epsilon|와 additive goal comparison을 적용할 수 있다. Thermal nonlinear defect, actual lift data, full tube/majorant와 boundary jump는 추가로 필요하다. 이번에는141D lift integration이나 full-state interval certificate를 실행하지 않았다.

DeltaQ=epsilon*Q1+epsilon²*Q2+R에서 coefficient errors E1,E2가 있으면 중앙값 epsilon*hatQ1+epsilon²*hatQ2의 radius는 |epsilon|E1+epsilon²E2+Rbound다. 새 contrast_interval API는 E1/E2/R 중 하나라도 없으면 MissingPremise를 발생시킨다. 제공된 값의 수학적 정당성까지 자동 인증하는 API는 아니다.

    DeltaQ(epsilon/2)-DeltaQ(epsilon)/4
       =epsilon*Q1/4+R(epsilon/2)-R(epsilon)/4.

Raw source의 작은 비영 Q1을 삭제하지 않는다. 기존 Q1/Q2의 표시 crossover |Q1/Q2|≈1.9014107211e-11은 수치 기준값일 뿐이다. Exact evenness와 O(epsilon4), EPS_HALF scaling을 승인하지 않았다.

## 검증·실패·실행 수

최종 새 focused32tests PASS, 그중2개 assertion RED→GREEN,30개 tests-after다. Exact lift64사례/3840항등식과128개 normalized-source 합 검사가 통과했다. 독립120자리 경로에서 sigma9개 포함, integral10개(총40 panels×16 Gauss nodes), pointwise residual600개, raw geometry8개를 확인했다. Pointwise 검사는 implementation 대조이며 whole-cell 증명은 Bernstein+tail이다. 120자리 물리정확성을 주장하지 않는다.

새 Python10파일 syntax PASS, final artifact conditions27 PASS. logs/08_FINAL_TESTS 및09_FINAL_ARTIFACT의 명령은 모두exit0이고 VERIFICATION.json이 시험 당시 code hashes를 고정한다. 최초 계산 results/budget01을 byte-identical하게 final로 봉인했으며 동일 science run을 다시 실행하지 않았다.

개발 중 test expected outer list와 선언된 tuple 반환이 달라 한 시험이 실패했다. 실제 모든 계수값은 정확히0이었고 test의 기대 container type만 수정했다. 실패로그와 수정 전 시험을 보존했다. Scientific code/수식/허용오차는 이 수정을 위해 변경하지 않았다. 이를 production 또는 수학적 실패로 분류하지 않는다.

새 native/IVP/root/history/old science suites/원자 적분/receiver mutation은0이다. 새 F04M coefficient RHS evaluation21회는 실제 수행했다. Independent human/agent review 및 proof assistant는 미수행이다. Rust 환경 스크립트/toolchain은 실행하지 않았다.

## 정본·실제 이중백업

File=BASS_CR_CHAT_F04N_20261006_v1.zip.
bytes=1230070.
SHA256=7f1c4fa11d1790248baeb0358264770ebabc0e7a3ec5d69b60f896f544cc2d6a.
ZIP75members/74payload의size/SHA256/CRC와 포장 시 tested code hashes를 확인했다.

Drive upload success 및metadata readback:id1QKDXTdBUnvk1o4fudBIhC7KHIjOe882s,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size1230070일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzg2g,size1230070,modified2026-10-06T03:47:01Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04N_20261006_v1.zip.

동일 immutable ZIP을 두 provider에 create-only로 저장했다. R1 UPLOAD_VERIFIED이며 remote checksum은 응답에 노출되지 않았다. 새ZIP fullrestore/independent remote bytehash는 미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git은summary/provenance/backup pointer, 실제 full code/tests/REPORT/exact JSON/logs는ZIP이다. 실제 publication commit/tree와 provider ACK는 ZIP밖 detached DELIVERY_RECEIPT에 기록한다.

## 다음 최소 이론 작업

다음은 같은 Hermite coefficient curve에 대한 gas/photon state residual과 검증된 공통 coefficient tube·triangular majorant를 구성해 b0/b1/b2를 얻는 것이다. 그 후 이번 B_quad와 결합해야 Q2의 interval error/sign을 말할 수 있다. 동시에 원 finite-epsilon family의 thermal defect와 directional lift를 채워야 전체 Taylor remainder를 승인할 수 있다. 같은32시험·기존IVP·firstmacro를 동기화만을 위해 반복하지 않는다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcounter=null 유지. Owner import ACK/raw native heat=null이며 actual BI transaction-dependent 인증도 별도다. FullK/318patch/CR-on/소비된 원자 승인 재사용, 새 mandatory gate, producer mutation은 없다.

산술 신뢰 기반은 Python 공식 fractions/decimal 문서이며 sensitivity의 일반 배경은 SUNDIALS CVODES FSA 문서를 확인했다. Source-specific lift와 residual/remainder는 정본 REPORT에서 직접 유도했으며 문헌 최초 결과라고 주장하지 않는다.
