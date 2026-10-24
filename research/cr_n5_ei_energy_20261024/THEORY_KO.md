# 선택 H1/He4 이온의 전자 에너지 교환

## 연구 위치와 실제 기여

PR102는 실제 C23D source와 EE 경로 위에서 ground-H CE 첫 사건을 계산했다. 이번 단위는 그 저장된 경로 표현에 빠져 있던 **이온별 Coulomb 에너지 drift와 diffusion**을 결속한다. 고전 Landau–Rosenbluth 계수, Maxwell 평형, 가역 birth–death MFPT, killed-chain reward는 선행 결과로 재사용한다. 새 산출물은 이 선택 조성의 계수와 source 가중 에너지 교환, EE와의 경쟁 및 보존적 finite-chain 소비자다.

원 elemental 수밀도는 C23D 고정 계약에서 읽었고 H1/He4의 질량 해석, Ti=Te=10000K, He+의 nucleus+electron inertia 근사는 이번 입력의 조건이다. NIST 2022 proton/alpha 질량비와 inherited EE anchor는 별도 provenance다. 원 EE anchor를 새 CODATA 수로 다시 계산하지 않는다. 전체 물리 조건과 수용 기준은 FROZEN_CONTRACT.md 한 곳에 고정한다.

## R2–R4: 후보와 원전 대응

질량 의존 EI, PI–RR Milne pair, 반복 CE jump를 비교했다. EI는 실제 수밀도와 기존 EE anchor가 공급되고 기존 PR59–64의 electron-only 계산을 중복하지 않으므로 선택했다. Milne pair는 state/degeneracy 및 same-source capture law가 더 필요하고, 반복 CE는 decay/재충돌/원자 population 소유권을 먼저 고정해야 한다.

원전은 Rosenbluth, MacDonald, Judd, *Physical Review*107,1(1957), DOI10.1103/PhysRev.107.1이다. SciSpace와 Exa로 원전 및 후속 후보를 조사하고 Exa의 원 논문 추출 text를 읽었다. APS 서지와 NIST constants table을 별도로 확인했다. PDF image는 조회 실패/네트워크 제한 때문에 읽지 못했으며 그 실패를 원 응답으로 보존한다. Factor 검증에는 아래 명시적 속도 moment–energy 변환, 독립 R6, 새 계수 controls를 사용한다.

## R5: 속도 moment에서 에너지 계수로

시험 전자의 질량을 m=m_e, field ion 질량을 M_b, 수밀도를 n_b라 두고,

    r_b=M_b/m, s_b²=2 epsilon_eV theta_b/M_b,
    x_b=v²/s_b²=r_b E/theta_b,
    A(x)=erf(sqrt(x))-2sqrt(x)exp(-x)/sqrt(pi)

로 정의한다. theta_b=kB Tb/epsilon_eV이고 E=m v²/(2epsilon_eV)다.

Maxwell field distribution의 Rosenbluth potential은 H_b=n_b erf(v/s_b)/v이고 g_b=integral f_b(v')|v-v'|d³v'다. 직접 미분과 구면 적분으로

    H_b'=-n_b A(x_b)/v²,
    tr Hess g_b=2H_b,
    g_b''=n_b s_b² A(x_b)/v³

를 얻는다. 밀도를 제외한 gamma_b=4pi Z_b²[e²/(4pi epsilon0)]²lnLambda_eb/m²를 사용하면

    <dv>/dt=gamma_b(1+1/r_b) grad H_b,
    Cov(dv)/dt=gamma_b Hess g_b.

Itô 변환에서 에너지 drift는 마찰과 covariance trace를 함께 포함한다.

    mu_b=gamma_b*m/epsilon_eV *[(1+1/r_b)v H_b'+H_b]
        =b_b[erf(sqrt(x_b))-(1+1/r_b)A(x_b)]
        =b_b[A'(x_b)-A(x_b)/r_b],
    D_b=m²v² gamma_b g_b''/(2epsilon_eV²)
        =theta_b b_b A(x_b)/r_b.

여기서 b_b=gamma_b n_b m/(epsilon_eV v)=b_ee eta_b이며 eta_b=(n_bZ_b²/ne)(lnLambda_eb/lnLambda_ee)다. 분산 convention은 Var(dE)=2Ddt다. 속도 마찰의(1+1/r_b)는 수직 확산의 Itô 가열과 일부 상쇄된다. 그 인자를 에너지 diffusion에 그대로 붙이는 구현은 이 변환과 다르다.

### 평형과 극한

b_b=C_b E^(-1/2)이므로

    D_b'+D_b(1/(2E)-1/theta_b)
      =b_b A'(x_b)-b_b A(x_b)/r_b=mu_b.

따라서 C_b F=partial_E{D_b[partial_EF+(1/theta_b-1/(2E))F]}이고 p_theta proportional sqrt(E)exp(-E/theta)는 zero-current 평형이다. 모든 bath가 같은 theta일 때 common weight를 유지하며 diffusion과 generator를 더할 수 있다.

r=1은 기존 PR59로 환원된다. 고정 E>0,T에서 r→infinity이면 A→1,A'→0이므로 mu,D→0이다. 각 산란은 이 극한에서도 남는다. 에너지 교환률과 각 산란률은 다른 물리량이다. 작은 x에서 A=4x^(3/2)/(3sqrt(pi))[1-3x/5+3x²/14-…]이고 양의 gamma 함수 평가를 사용한다. source의 저에너지 원자를 무조건 high-energy asymptote로 치환하지 않는다.

### Maxwell test population의 열 교환

온도 theta_t인 정규화 Maxwell energy density와 mu_b를 적분한다. lambda=theta_b/(r_b theta_t)>0이면

    integral_0^inf exp(-lambda*x) A'(x) dx=(1+lambda)^(-3/2),
    integral_0^inf exp(-lambda*x) A(x) dx=(1/lambda)(1+lambda)^(-3/2).

두 번째 식은 A(0)=0과 지수 감쇠에서의 부분 적분이다. 그러므로

    <mu_b>=2 C_b (theta_b-theta_t)
           /[sqrt(pi) r_b (theta_t+theta_b/r_b)^(3/2)].

같은 온도에서 net energy 교환은0이며 개별 입자의 signed drift는0일 필요가 없다. 이 표준 열 교환 극한은 새 mass factor의 판별 검사다.

## EI/EE 경쟁과 첫 진입의 정량 조건

같은 T이고 E≥q=chi theta일 때 A의 단조 증가와 A≤1에서

    0<=D_EI/D_ee<=delta_max,
    delta_max=[sum_b eta_b/r_b]/A(chi).

기존 MFPT의 양의 적분 T(E)=integral_q^E dz [D(z)p(z)]^(-1)integral_z^U p(u)du에 대입하면

    T_ee/(1+delta_max)<=T_ee+EI<=T_ee.

이는 같은 finite domain, q absorbing, U reflecting, 동일 common Maxwell weight의 비교다. continuum coefficient에 대한 이 analytic relative comparison은 finite-chain 수치 오차나 실제 screening/model error의 전체 경계가 아니다. 같은 pi_i의 가역 체인에서는 c_b/c_ee=D_b/D_ee를 edge에 적용하고 T_i=sum_(k<i)(tail pi_(k+1))/c_k를 사용해 같은 비교를 얻는다. 기존 EE/CE solver는 재실행하지 않는다. 저장된 EE conductance를 읽어 새 paired algebraic diagnostic을 계산한다.

CE first-event probability는 별도로 새 combined killed system을 푼다. MFPT의 단조성만으로 CE probability의 부호를 주장하지 않는다. q보다 작은 initial source에는 위 bound를 전체 stopping error로 전용하지 않는다. 그 원자들은 별도 per-atom 계수와 순간 exchange에 남는다.

## 종별 에너지 장부

각 bath의 full column generator Q_b에 q-state를 포함한다. d_b=(Q_b^T E_full)_active, G=sum Q_b[1:,1:]^T, a=rate to q, h=h_s+h_p, K=diag(h)-G라 두면

    K H_b=-d_b,
    K u_entry=a,
    K u_CE=h,
    K r_CE=E_active*h.

K E_active=E_active*h-d_total+a*q이므로

    sum H_b + q*u_entry + r_CE = E_active.

CE 후 electron kinetic을 terminal로 표현하려면 r_CE를 r_CE-Delta*u_CE와 원자 내부에너지 Delta*u_CE로 나눈다. 원래 사건은 e(E)+H1s→e(E-Delta)+H2l이며 charge/nuclei/electron count incidence는0이다. first mark에서 관측을 끝내는 것은 물리 입자를 없애는 반응이 아니다. Initial inactive W<=q는 자기 원래 W를 terminal로 갖고 reward0이다. q로 처음 들어간 에너지를 추가 bath heat로 다시 더하지 않는다.

## 이론–코드 연결과 검증 종료

계수는 새 engine의 mass-resolved function, common-weight ratio는 edge conductance builder, 보존 장부는 signed bath RHS, 확률·시간·reward는 banded solve에 각각 대응한다. 소스·그리드·CE hazard와 EE 원 행렬은 immutable 입력이다. 검증 기준과 실행 ID는 FROZEN_CONTRACT.md 및 inputs/CASE.json에 결속한다.

독립 R6와 C9는 중요한 식, 원자료, 새 matrix/RHS/출력, 소스 정규화 및 수용 기준을 검사한다. Wolfram 첫20s 묶음 검산은 시간 초과였다. 필요한 항등식으로 축소한 두 번째 검산은 equilibrium defect0, A derivative defect0과 양의 작은-x 전개를 반환했다. 무한질량 극한은 위 해석 유도이며 CAS 완료로 표시하지 않는다.

새 strong no-go는 없고 NG1–NG7 채택 대상이 없다. 기존 isotope quotient 조건은 재사용한다. 이번 입력의 조건부 H1/He4 질량 결속은 다른 isotope density와 rate의 공급을 대신하지 않는다. 전체 N4/N5, N6/N7, global error/completion 상태는 계약의 원 DAG를 유지한다.
