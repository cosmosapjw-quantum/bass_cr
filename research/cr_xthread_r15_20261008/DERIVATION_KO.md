# R15: fixed-birth first-macro 광학 functional

시간은 proper seconds, 밀도는 proper cm^-3, 광자수는 conserved H nucleus당,
기체 상태는 (h,y,z,w/w0), 광자는 각각 Pj/0.05이다. Native의 실제 variant=0
양끝 binary64를 정확한 실수로 읽어 각 cell에서 선형 재구성한다.
H,nH0,fHe는 donor의 binary64 상수다. 관측량은 무차원이며
CT = 299792458 × binary64(6.6524587e-29) × 10^6,
Xe = h+fHe(y+2z), nH(t)=nH0 exp(-3Ht)이다.

cell i에서 L=t1-t0는 f64 경계의 **정확한 실수차**다. s=(t-t0)/L,
alpha=3HL, d0=exp(-3Ht0), scale=CT nH0 L라 두면

    e(s)=ein - integral_0^s r(u)du + integral_0^s [F(u,zcont)-F(u,zhat)]du
    delta_tau_i = scale*d0*[W*Xe(ein) - sum_panels Xe(r_panel)*J_panel + feedback]
    W = integral_0^1 exp(-alpha*s)ds
    J_[a,b] = integral_a^b du integral_u^1 exp(-alpha*s)ds

따라서 incoming signed error를 0으로 바꾸면 첫 항 전체가 사라진다.
31개 후속 cell에는 donor의 이전 signed endpoint와 실제 native interface 차를
사용하고, exact birth source weight interval만 신규 광자에 추가한다. 이 값이
저장된 initial_error_scaled와 정확히 일치하는지 확인한다. endpoint proof와
Picard contraction을 새로 발급하지 않는다. 기존 tube와 stored residual
supremum을 사용해 광학 functional의 새 all-prefix majorant를 계산한다.

convex physical tube에서 N_ij=sup|dF_i/dz_j|, R_i=sup|r_i|를 사용한다.
augmented positive matrix [[N,R],[0,0]]의 exp-action과 directed tail로
모든 s의 |e|를 E로 감싼다. |F(zcont)-F(zhat)| <= N E이다. 새 residual은
각 cell의 실제 16개 전시간 interval panel에서 계산하며 R과 integral r가
기존 donor evidence와 byte 표현까지 일치한다. positive-series metadata도
기존 기록과 일치한다. feedback의 광학 upper는

    scale*d0_upper*J_[0,1]_upper*(NE_h+fHe*(NE_y+2*NE_z))

이다. per_cell_nonlinear_remainder는 이 **전체 nonlinear RHS difference**의
보수적 bound를 뜻한다. 선형 Jacobian feedback도 포함하며 Hessian만의
2차 remainder로 주장하지 않는다. incoming의 직접 signed optical contribution,
잔차 forcing, 이 feedback remainder를 각각 기록한다.

0<=alpha<=1에서 exp(-alpha*s)는 Taylor5 아래, Taylor6 위에 있다.
positive W/J weights의 적분은 Fraction exact rational로 수행한다. 부호 있는
residual/initial interval 곱은 네 endpoint의 최소/최대를 사용한다. native
tau는 양의 endpoint shape weights (1-s),s를 사용해 같은 Taylor enclosure로
감싼다. density d0는 donor의 outward Decimal exp로 감싼다. 첫 cell은 R14의
원 rational GOAL.json을 그대로 계승한다. 그 원 source_point와 BRIDGE13
variant=0 첫 point의 전체 필드가 정확히 일치함을 별도 byte audit로 확인했다.

tau는 여섯 birth에서 연속이며 누적량을 재설정하지 않는다. 전체 32-cell
interval은 각 cell interval의 합이다. positive endpoint Xe나 rate 부호로
결론을 추정하지 않았다. 실제 하한이 양수일 때만 signed positive로 기록한다.

독립 검산은 Taylor 다항식을 사용하지 않는 80자리 exponential antiderivative
구적 및 원 mpmath FT03 nonphoto 식에 별도 optical-error 누적 상태를 붙인
DOP853 32구간이다. certificate는 검산 후 포함 확인에만 사용된다. 이것은
독립 interval backend, proof assistant 또는 물리 원자율 검증이 아니다.
원 FT03 계수 source는 공유한다. donor repo 변경 및 BRIDGE14 실행은 0회다.

결론은 Decimal60 directed/outward exp-ln 및 donor Picard/Jacobian proof에
조건부다. continuous emission quadrature, observer tail, Bianchi,
physical atomic fit, full history/global operator, matched discrete-family tau는
이 인증에 포함되지 않는다. Grackle IGM equation과 결합하지 않는다.
