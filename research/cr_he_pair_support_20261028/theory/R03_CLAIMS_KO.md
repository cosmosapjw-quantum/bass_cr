# R3 명제·전제와 단위

## 정의와 양화

유한 atom 집합 `A`를 서로소 bin `A_i`로 분할한다. 각 atom `a`는 고정 에너지 `E_a`와 비음수 coefficient `a_a`를 갖는다. 코드의 네 bin은 cutoff ghost, `(cutoff,1]`, `(1,3]`, `(3,10] eV`다. Ghost는 별도 원래 atom이며 새 support가 아니다. `a_i=sum_{a in A_i} a_a`, `A_tot=sum_i a_i`로 쓴다.

정리 자체는 유한 bin 수와 임의 비음수 실수 질량 `n_i`에 대해 성립한다. 실제 구현은 네 bin과 정확한 유리수 coefficient를 사용한다. History `q_a(t)=t*a_a`의 허용 proper window `[u,v]`에서 `W=(v²-u²)/2>0`이고 `n_i=W*a_i`다. Coefficient의 단위는 `m^-3 s^-2`, 적분 질량의 단위는 `m^-3`다. Graph는 해당 binding/window에서 시간에 따라 변하지 않는 명시적 조건부 입력이다. 동차성으로 `rho_G(W*a)=W*rho_G(a)`다. `C_coeff,d_coeff`와 적분한 `C=W*C_coeff,d=W*d_coeff`를 혼동하지 않는다.

`G`는 서로 다른 bin을 잇는 단순 무방향 graph다. 허용 edge `ij`는 **전체** `A_i × A_j` rectangle의 원자쌍을 허용한다. Graph에는 self-edge를 넣지 않는다. 대신 모든 atom의 single event와 동일 atom 두 leg를 갖는 diagonal double event를 조건부 구성에서 허용한다. Atom별 금지쌍, diagonal 금지, 각운동량/에너지 교환 제약, 실제 exclusive kernel의 추가 조건은 이 정리의 전제가 아니다. 그러한 조건이 주어지면 별도 feasible set이 필요하다.

`x_ij`는 unordered cross-double event 질량이다. 각 endpoint bin에서 `x_ij`만큼 electron leg를 소비하며, 전체로는 두 leg를 소비한다. `B`는 각 edge의 두 endpoint에 각각1을 갖는 incidence matrix다. 정리의 feasible polytope는 `x>=0, Bx<=n`이다. 남은 marginal은 single 또는 diagonal double로 채운다. Symmetric ordered measure로 쓰면 `D_ij=(pi_ij+pi_ij^T)/2`, 따라서 `mu=S+2*pi_1 D`다. Diagonal에는 이 식의 factor2가 그대로 적용된다.

## 새 대상 명제

| ID | 정확한 명제 | 상태·의존성 |
|---|---|---|
| T1 | `rho_G(n)=max 1·x=min n·y`, primal `x>=0,Bx<=n`, dual `y>=0,y_i+y_j>=1` | R5에서 finite max-flow construction으로 증명 |
| T2 | 대칭 이분 double-cover의 최대유량 `F`에 대해 `rho=F/2`; cut에서 `y_i∈{0,1/2,1}`인 최적 dual을 얻음 | N=0 별도 처리, N>0 cross-arc cap2N |
| T3 | attainable cross mass는 `[0,rho]`; fixed internal double mass `0<=d<=N/2`이면 `[0,min(d,rho)]` | residual diagonal doubles를 허용하는 명시적 전제 |
| T4 | 임의 feasible bin assignment를 원래 atom marginal을 정확히 보존하는 sparse event set으로 lift 가능 | full Cartesian rectangle과 unrestricted diagonal 전제 |
| T5 | 원래 event-union consumer와 연결하면 partition sum의 ion correction `(C,0,-C)`, charge `-2C`, chemical `-(I1+I2)C` | PR112 소비자 식 재사용; graph witness의 보존·binding은 새 검증 |
| T6 | Graph 추가/질량 증가에 대해 monotone, nonnegative scaling에 동차, 질량 perturbation에는 `|rho(n)-rho(m)|<=sum|n_i-m_i|` | dual을 `[0,1]`에 둘 수 있음 |

Actual physical graph, actual exclusive kernel, actual C/D와 selected-outside partner response는 확보하지 않았다. Constructed witness에서 outside event를 넣지 않았다는 사실은 실제 물리계의 outside mass가0이라는 측정이 아니다. 실제 EOS/T·donor work·full physical native25는 계속 null이다. 이번에는 불가능성 또는 strong no-go를 성과로 주장하지 않는다.

## 구현 수용 기준의 정확도

입력은 저장 binary64의 정확한 유리수 값이다. 핵심 primal feasibility, dual feasibility, objective equality, atomwise marginal, C/d, species/charge/chemical correction은 **정확한 등식과 부등식**으로 판정한다. tolerance를 느슨하게 하여 통과시키지 않는다. Binary64로 표시한 그림이나 표는 presentation이다. Source fit·실제 kernel·물리 모델 오차에 새 finite bound를 주장하지 않으며 해당 global physical error는 null이다.
