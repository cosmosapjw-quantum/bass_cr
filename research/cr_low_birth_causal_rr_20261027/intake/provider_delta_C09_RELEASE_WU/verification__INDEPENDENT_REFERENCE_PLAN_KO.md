# R7 C7 독립 수치 reference 계획

## 범위와 실행 상태

이 파일은 실행 전 고정 계획이다. 작성 시 과학 실행은 0이다. Root의 명시적 실행 지시 뒤 한 번의 신규 reference 진입점을 사용하며 CPU 한도는 60 s이다. 기존 R6/PHYS91의 잔여 예산 0을 전용하지 않는다. 새 입력과 생산 결과의 SHA256, 실행 명령, Python/NumPy/SciPy 버전, 시작·종료·CPU·벽시계 시간, 첫 실패와 원시 결과를 출력에 남긴다.

`reference_r7.py`는 R7 생산 core와 R6 core를 import하거나 실행하지 않는다. 기존 R6의 saved K/rho 자료는 primary가 같은 입력·clock·H·certificate identity로 결속한 경우 읽기 근거로만 재사용한다. 원 rate, Gibbs 계산, uniformization 또는 이전 scientific suite를 재실행하지 않는다.

검증은 일반 증명의 수치적 보강이다. binary64 SciPy 결과나 유한한 관측 시각이 interval 증명 또는 모든 입력의 물리적 closure를 대신하지 않는다. 합성 reaction coefficient와 native excitation generator는 GL2022 destruction 수치 또는 named physical consumer로 표시하지 않는다.

## 독립 행렬 reference

생산 출력의 각 B,g,H,rho,w0를 exact rational 문자열에서 읽는다. SciPy `expm`으로 3x3 augmented matrix `[[B,g],[0,0,0]]`의 exponential을 계산하여 `exp(BH)`와 forcing integral을 동시에 얻는다. B 역행렬은 사용하지 않는다. 생산 exponential upper, T upper, q upper와 endpoint upper가 각각 reference를 위에서 덮는지 검사한다. 이 비교의 부동소수점 허용 오차와 실제 최악 초과량을 따로 저장한다.

독립 analytic controls는 B=0, nilpotent B²=0, diagonal B(음수 d 포함), 그리고 coupled Metzler negative-d case다. 첫 세 경우는 닫힌 식도 계산하여 augmented exponential과 교차 비교한다. 각 출력 행렬은 비음수이며 causal endpoint의 첫 대각에서만 `(1-rho)`를 빼야 한다. d<0을 0으로 clip한 결과는 같은 문제로 허용하지 않는다.

## 비선형 HD fine/coarse reference

상태 순서는 fine `[u,v,w,x_1,...,x_m]`, coarse `[ubar,vbar,wbar,Xbar]`다. 독립 RHS는 사건 propensity를 직접 합한다:

`a_i^+=kf*alpha_i*u*v`, `a_i^-=d_i*w*x_i`,
`u'=v'=-sum_i(a_i^+-a_i^-)`, `w'=sum_i(a_i^+-a_i^-)`,
`x_i'=sum_j K_ij*x_j+a_i^+-a_i^-`.

coarse RHS는 `(-1,-1,1,1)*((kf+coarse_kf_offset)*ubar*vbar-(d·pi)*wbar*Xbar)`다. offset은 frozen input에 명시되어 있으며 같은-source 사례에서는 0, 별도 source-defect 사례에서는 1/10000이다. 해당 defect의 실제 값 `offset*ubar*vbar`를 공급된 상계와 비교한다. 생산 residual 식이나 생산 coefficient 함수를 RHS로 복사하지 않는다. 고정 positive pi, 명시적 simplex alpha, 비음수 d, column-conservative Metzler K와 동일 초기 H/D/charge를 exact input 단계에서 검사한다. coarse 초기값을 fine aggregate로 자동 대체하거나 pi/alpha를 자동 정규화하지 않는다.

`solve_ivp(method='DOP853', rtol=1e-11, atol=1e-13)`로 fine와 coarse를 각각 푼다. primary가 고정한 3 또는 4 blocks에서 block당 65 저장 시각을 평가한다. primary의 pointwise queries는 block당 5개(또는 33/65개)일 수 있다. 모든 65시각에서는 생산 constant whole-block upper 및 독립 expm으로 계산한 pointwise 비교해를 검사하고, primary가 저장한 공통 시각에서는 생산 pointwise upper도 직접 검사한다. solver의 adaptive internal steps는 이 고정 시각 출력용이며 tolerance/입력의 사후 튜닝을 하지 않는다.

각 시각의 `R=||x-pi*sum(x)||_1`, `E=|sum(x)-Xbar|`를 생산 whole-block upper와 비교하고, block 끝에서는 더 강한 endpoint upper도 별도로 비교한다. `||Px-ybar||_1=4E`, H 핵수 `2u+w+X`, D 핵수 `v+X`, 전하 `v+w`의 fine/coarse 보존, 비음수성, 선언한 whole-block density box 포함 여부를 확인한다. positive lower box를 사용하는 경우 그 근거가 입력에 있어야 하며 유한 sample 포함만으로 전체 구간 enclosure를 발급하지 않는다.

필수 사례는 새 2-state 수학 fixture다. 9-state native-K 사례는 primary가 R6 saved K/rho/clock/H를 실제로 재사용해 출력한 경우 한 개만 추가한다. 이때 destruction/formation/density는 명시적인 합성 조건이며 physical consumer admission은 false다.

## 인과적 forcing과 guard

대칭 2-state K의 마지막 epsilon 구간에 formation을 넣으면 endpoint 잔차의 정확한 값은 `J*(-expm1(-gamma*epsilon))/(gamma*epsilon)`다. 올바른 forcing upper J와 잘못된 `rho*J`를 비교하여 `rho=exp(-gamma*H)`를 늦은 forcing 전체에 붙일 때 위반함을 확인한다. 초기 잔차의 rho 적용과 생성 후 잔여 시간의 전파를 구별한다.

입력 domain 검사로 잘못된 초기 H/D/charge, pi의 0/음수, alpha 미제공·합 불일치, 음수 destruction, 비보존 K, clock/H 불일치를 거부한다. 생산 guard 결과가 있는 경우 실제 status를 읽어 조합하되 reference의 별도 input 검사 결과와 혼동하지 않는다.

## 저장 출력과 판단

출력에는 각 analytic/matrix case 결과, HD fixture와 solver diagnostics, 저장 clocks·fine/coarse 상태·R/E·상계, invariants와 density-box 진단, late-forcing 비교, 적용한 허용 오차 및 source/fixture scope를 담는다. 한 case가 실패하면 나머지 허용된 같은 실행의 진단은 저장하되 전체 status를 PASS로 바꾸지 않는다. 첫 결과를 덮어쓰는 자동 repair/run loop는 없다. 명시적 산출 파일 존재 시 기본적으로 덮어쓰지 않는다.

고정 primary 입력 SHA256은 `3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330`이다. 5 affine 및 4 HD case를 전부 검사한다. native 9-state에는 saved R6 `native_mu_256` H/rho와 K interval을 사용하며 source값은 재계산하지 않는다. 실행 전 최종 output schema를 맞추고 입력·코드 identity를 고정한 한 번의 reference 실행만 수행한다.
