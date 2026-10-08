# R3M19 시간전파 원인분리: 문헌과 수학 유도

작성: 2026-09-23. 범위: 원전/공식 구현 조사, 기존 R3M18 숫자 재계산, 직접 수학 유도. 새 collision, GPU 실행, production numerical source 변경은 없음. R3M17의 문헌목록을 반복하지 않고 다음 canonical full-H diagnostic을 구체화한다. 아래 `DERIVED`는 이 연구에서 유도한 식이며 문헌의 정리로 표시하지 않는다.

## 1. 이번 데이터로 판정할 수 있는 것

`docs/r3m18/REPORT_KO.md`의 full-precision B0/B1/B2 입력을 사용했다. 세 P3는 0.007911255992446844 / 0.008063449050040342 / 0.008084190148156251, actual dt는 0.04996782580968821 / 0.02499784704477988 / 0.01249892352238994다.

| 직접 계산 | 값 | 해석 |
|---|---:|---|
| signed `(P1-P0)/(P2-P1)` | 7.337753128739204 | 같은 부호의 경험적 contraction |
| unequal-dt single-power observed p | 2.8780182899266467 | 사전 등록 clean-order 범위 밖 |
| fine-pair / B2 | 0.2565637093610342% | 사전 등록 0.10% screen 밖 |
| fitted-p conditional Richardson remainder / B2 | 0.0403948515634782% | single-power 가정에 조건부 |
| assumed-p=2 conditional remainder / B2 | 0.0855212364536781% | p=2 가정에 조건부 |
| dt²+dt⁴ model conditional remainder / B2 | 0.0664063329017287% | 아래 3-parameter model에 조건부 |

세 점은 `P(dt)=P∞+c2 dt²+c4 dt⁴`에도 정확히 맞는다: P∞=0.008089558562378444, c2=−0.031890887318075, c4=−15.829171949113071. 데이터 세 개와 자유도 세 개이므로 검증된 모형이 아니다. 이 반례는 p>2.5가 반드시 수학적 실패라는 주장을 반박하지만, 잔여오차를 인증하거나 p=2를 강제할 근거가 되지 않는다. 위의 세 조건부 잔여치는 모두 0.10% 아래인데도 어느 것도 gate를 닫지 않는다.

핵이 grid node를 지나지 않는 고정 finite grid에서는 행렬 원소가 시간에 매끄럽고 usual finite-dimensional asymptotic order를 시험할 수 있다. 그 onset이 현재 dt보다 작을 수 있으며, leading/higher error coefficient 혼합, 관측량의 방향 투영, 오차 상쇄가 관측 p를 바꿀 수 있다. 고정 h의 limit와 h→0에서 uniform한 Coulomb-domain estimate는 서로 다른 질문이다. R3M17의 autonomous continuum Coulomb 저차수 정리는 현재 moving-Coulomb+CAP 계산의 p>2.5를 금지하는 정리가 아니다. 따라서 상태는 `TIME_REFINEMENT_STILL_OPEN`, 과학적 해석은 `EMPIRICAL_CONTRACTION_ONLY`가 타당하다.

Norm의 signed 변화는 +0.006776109425150834와 −0.0000363657318714905로 부호가 반전된다. Norm에 positive single-power p를 fit하면 안 된다. Fine norm 변화가 작다는 사실도 P3 또는 CAP bias가 작다는 증거는 아니다.

## 2. 무엇을 같은 문제로 고정하는가

`A(t)=−i[T_h+V_h(t)]−W_h`, `W_h=−log(mask)/reference_dt≥0`로 정의한다. 실제 ControlledTDLRunner는 V-midpoint half step에 fixed-rate CAP half step을 곱하고 FFT kinetic step 다음에 같은 half step을 적용한다. 따라서 현재 runner에 대해 ‘매 step 같은 mask를 곱하므로 dt를 줄이면 다른 absorber가 된다’는 과거 일반론을 적용하면 안 된다. W가 동일하다는 binding을 직접 검사한다.

같은 grid, initial vector, t_start/t_stop, nucleus path, W, observable/projector를 모든 solver에 사용한다. Non-Hermitian full-H reference는 동일한 finite-grid CAP 문제의 시간해를 검증한다. 이것만으로 continuum Coulomb representation, CAP-free scattering, finite-time asymptotics, physical model을 검증하지 않는다.

## 3. 정확히 망원 합이 되는 세 원인분리 — DERIVED

한 step 또는 공통 horizon의 각 method 전체 product를 각각 다음처럼 정의한다.

- S_mid: 현재 midpoint Strang+CAP.
- E_mid: 각 interval에서 `exp(Δ A(t_mid))`를 full-H로 적용.
- E_avg: 각 interval에서 `exp(∫ A(t)dt)`를 full-H로 적용; moving diagonal potential integral은 아래 해석식.
- U_ref: full nonautonomous A(t)를 DOP853 및 독립 CF4 refinement로 교차 검증.

공통 initial ψ에 대해

`S_mid ψ − U_ref ψ = e_split + e_quad + e_order`,

`e_split=(S_mid−E_mid)ψ`, `e_quad=(E_mid−E_avg)ψ`, `e_order=(E_avg−U_ref)ψ`.

이는 선택한 비교 경로에 따른 정확한 vector identity다. e_split은 midpoint frozen operator splitting 차이, e_quad는 midpoint diagonal quadrature 차이, e_order는 time ordering 잔여와 reference 오차다. 유일한 물리적 원인분해나 독립 오차 budget이라는 주장은 하지 않는다. 각 term norm뿐 아니라 `2 Re<ei,ej>`를 기록하여 `||Σei||²=Σ||ei||²+2ΣRe<ei,ej>` 재구성을 검사한다. 전체 endpoint product 비교에서는 후속 전파와 상호작용까지 해당 차이에 포함된다.

각 term을 독립적으로 phase-align하면 identity가 깨진다. 이 분해에는 공통 raw phase gauge를 유지한다. 별도로 normalized ray distance, global-phase difference, raw L2, norm, projector expectation difference를 기록한다. 공통 scalar gauge subtraction을 한다면 모든 방법에 동일하게 적용하고 원 gauge 복원을 검증한다.

### Exact moving-potential integral — DERIVED

고정 grid point에서 `ρ²=(x−b)²+y²`, `q(t)=z−vt`, `Vp(t)=−[ρ²+q(t)²]^−1/2`일 때

`∫[t1,t2]Vp(t)dt = {asinh[q(t2)/ρ]−asinh[q(t1)/ρ]}/v`, ρ>0.

정지 target의 integral은 ΔVtarget다. v=0은 static limit로 처리한다. 실제 singular crossing을 임의 epsilon/soft core로 숨기면 다른 Hamiltonian이므로 fail closed 또는 정확히 정의한 별도 진단을 사용한다. 작은 interval의 asinh 차이 cancellation도 검증 대상이다.

`Vdot=−v q/r³`, `Vddot=v²(ρ²−2q²)/r⁵`.

Midpoint를 원점으로 둔 local Magnus expansion은

`Ω = Δ A0 + Δ³ A2/24 − Δ³[A0,A1]/12 + O(Δ⁵)`.

여기서 A1=−i Vdot, A2=−i Vddot, static W는 diagonal이므로 `[A0,A1]=−[T_h,Vdot]`다. E_avg는 leading quadrature correction을 포함하지만 time-ordering commutator를 없애지 않는다. Exact diagonal integral만으로 전체 method가 4차가 되는 것은 아니다. 핵 주변의 시간 scale은 ρ/v이므로 dt만이 아니라 v·dt/ρ_min, grid nuclear offset을 함께 기록한다.

고정-grid smooth/time-derivative 및 commutator 가정을 가진 exponential midpoint/Magnus 해석은 Hochbruck–Lubich의 Eq. (2.8), (2.9), (3.2), (3.4), Theorem 3.1을 참고한다 [S1]. Coulomb continuum에 smooth-potential uniform bounds를 그대로 적용하지 않는다. 큰 `dt*||T_h||`만으로 instability를 선언하지 않는다.

## 4. CF4 reference의 정확한 순서와 CAP — DERIVED extension of [S2]

두 Gauss node `c1=1/2−sqrt(3)/6`, `c2=1/2+sqrt(3)/6`, Aj=A(t+cjΔ),

`a=(3+2sqrt(3))/12≈0.5386751346`, `b=(3−2sqrt(3))/12≈−0.0386751346`.

[S2] Eq. (61)의 CF4를 matrix action으로 쓸 때

`U_CF4 = exp[Δ(b A1+a A2)] exp[Δ(a A1+b A2)]`.

오른쪽 early-weighted exponential을 먼저 적용한다. 순서를 뒤집으면 commutator 부호가 바뀐다. Full-H exponential/action을 사용해야 한다. 이를 내부 Strang으로 대체하면 검증하려던 splitting 오차가 다시 들어와 4차 기준해가 아니다.

현재 W는 static이고 a+b=1/2이므로 각 stage의 Hermitian dissipative part는 정확히 −W/2다. b<0이라는 이유만으로 이 CF4가 CAP를 역전시킨다고 주장하면 틀리다. 각 stage exponential은 contraction이고 product도 contraction이다. 시간 의존 W나 다른 고차 조합에는 이 결론을 재검사한다. W≠0일 때 Hamiltonian은 non-Hermitian이므로 `eigh` 또는 Hermitian Lanczos 가정을 사용하지 않는다. 작은 dense matrix에는 일반 `scipy.linalg.expm`, 확장에는 일반 exponential-action 알고리즘을 사용한다.

## 5. ‘독립 reference’의 최소 검증

공식 DOP853 [S3]은 complex 지원 explicit order-8 method다. `rtol/atol`은 local scale이며 전역 wavefunction/약한 capture probability의 인증치가 아니다. 공식 구현 [S4]은 scale=`atol+max(abs(y),abs(y_new))*rtol`로 만든 combined embedded-error norm으로 accept/reject한다. 모든 component별 절대 hard bound도 아니다. tail에서 atol가 우세하면 약한 capture channel에 부적합할 수 있다.

향후 생산 h/짧은 구간 기준해에서는 동일 grid에서 tolerance tightening, max_step halving, independently refined CF4와의 agreement를 기록한다. **현재 R3M19 tiny suite는 tolerance repeat를 실행했으며 별도 max_step halving은 미실행이다.** `max_step`을 infinity로 남겨 두면 빨리 움직이는 grid-near nuclear event를 adaptive estimator 하나에 맡긴다. 기하학적 ρ/v scale에 근거해 upper bound를 명시하고 줄여 검증한다. t_eval는 output time이지 실제 accepted step grid가 아니다. finaltime/status/nfev와 reference-to-reference raw/ray/norm/observable 차이를 기록한다. Reference residual이 비교하려는 smallest split error보다 충분히 작아야 한다. 이 허용비율을 결과 확인 전에 등록한다.

`expm_multiply(A,B,start=None,stop=None,num=None,endpoint=None,traceA=None)` [S5]에는 public `tol` 인수가 없다. `LinearOperator`를 쓰면 adjoint/transposable action과 traceA를 명시한다. 이 구현은 Al-Mohy–Higham 계열 exponential action이며 무조건 Krylov라 부르지 않는다. time-varying 문제의 full interval을 단일 expm_multiply(A(tmid),...)로 푸는 것은 독립 nonautonomous reference가 아니라 E_mid다. 실제 runtime SciPy version을 기록한다. 조사한 온라인 docs/source는 1.18.0; canonical GPU runtime 1.18.1과 동일 버전이라고 주장하지 않는다.

[S6]의 defect `D(τ)=S'(τ)−A(t0+τ)S(τ)` 및 Eq. (8)의 local-error integral은 작은 window의 오류 발생 시점을 찾는 데 유용하다. Eq. (6)의 `τ/(p+1) D(τ)`는 asymptotically correct estimator이며 finite-step certified bound가 아니다. 이번 노드에 자동 adaptive production 운영을 도입할 근거로 삼지 않는다.

## 6. 작은 dense 기준해와 향후 matrix-free 확장의 구별

이번 진단의 작은 dense full-H 행렬은 같은 finite grid의 시간전파를 독립적으로 비교하기 위한 기준해다. N complex128 grid points의 dense 행렬 하나만으로도 약 `16 N² bytes`가 필요하고, dense exponential 작업 공간은 별도다. 작은 grid의 정확도·차수 검증을 production 크기의 실행 가능성으로 해석하지 않는다.

향후 matrix-free 경로는 `A(t)ψ=−i[T_hψ+V_h(t)ψ]−W_hψ`를 FFT kinetic action과 diagonal multiplication으로 계산할 수 있다. W≠0에서는 일반 non-Hermitian exponential action이 필요하다. Arnoldi/Krylov를 선택할 경우 m개의 complex128 basis vector 저장량만 약 `16 m N bytes`이며, residual·FFT workspace·입출력 vector·재직교화·checkpoint 공간을 추가해야 한다. CPU와 GPU 사이의 배열 복사 비용도 별도다. 이는 feasibility estimate이며 production 구현 결과가 아니다.

여기서 CF4는 시간 step마다 full-H exponential action 두 번을 요구한다. 시간적 4차가 관측되려면 각 action의 inner approximation error가 time-discretization error보다 충분히 작아야 한다. Krylov 차원·restart·오차 추정 또는 다른 action 알고리즘의 정확도 설정을 refinement와 함께 검증해야 한다. `expm_multiply`는 위 [S5]의 별도 알고리즘이며 Krylov basis 메모리식을 그대로 적용하지 않는다. 이번 dense 검증은 matrix-free 구현, production GPU 메모리 한도, 속도, 장시간 안정성을 검증하거나 승인하지 않는다.

## 7. CAP 회계와 물리 경계오차를 구별한다 — DERIVED

정확한 finite-grid equation에서 `d||ψ||²/dt = −2<ψ,Wψ>`. 각 CAP half step은 amplitude에 `exp(−ΔW/2)`를 곱하므로 그 step의 probability loss는 `Σ [1−exp(−ΔW)] |ψ_beforehalf|² dv`다. 이를 합한 값과 initial minus final norm이 일치하는지 검사한다. 이 항등식은 absorber accounting/kinetic unitarity 점검이며 CAP reflection이나 capture bias의 인증이 아니다.

R3M18의 final CAP-layer norm 0.003861411089940187, sampled n≤3 maximal CAP fraction 0.0008739175405814191은 geometry/support diagnostic이다. 누적 손실, CAP가 없을 때 상태와의 차이, n>3 bound tail, continuum probability의 bound가 아니다. 특히 normalization으로 CAP 손실을 가려서는 안 된다. CAP-on/off 또는 W-scale 비교는 서로 다른 finite-grid Hamiltonian이므로 원인분리 control로 명확히 이름 붙인다.

[S7]은 CAP의 목표를 unabsorbed inner-region solution agreement로 명시하고 finite grid에서 low-momentum edge reflection이 남음을 보인다. 해당 SES-CAP 결과를 현재 multiplicative mask에 대한 quantitative guarantee나 CAP 교체 지시로 쓰지 않는다. 다음 production budget 단계에서는 CAP onset/width/strength, box, final time에 따른 channel 변화와 늦은 reflected/inward flux가 필요하다. 이번 tiny full-H 노드는 그 budget을 닫지 않는다.

## 8. 가설을 기각할 수 있는 bounded controls

| control (모두 작은 진단) | 예상 invariant/비교 | 무엇을 구분하는가 |
|---|---|---|
| T=0, moving diagonal V, static W | E_avg=U_ref within reference tolerance | exact integral/time ordering implementation |
| frozen V, 같은 W | E_mid=E_avg=U_ref | nonautonomous effect 제거, splitting만 남음 |
| W=0 및 W>0, 동일 나머지 조건 | noCAP unitary, CAP contractive; loss ledger | 비Hermitian 처리/흡수 상호작용 |
| noncommuting smooth 2×2 A(t) | CF4 order4, reversed product는 실패 | Gauss coefficient와 stage order |
| target-only discrete eigenvector | exact full-H의 ray distance≈0 | preparation drift와 real-time method 구별 |
| smooth periodic moving potential | Coulomb near-node와 error-profile 비교 | singular-potential hypothesis 반례/지지 |
| grid nuclear offset sweep (same h) | min distance, derivative scale와 local defect의 상관 | moving mesh-phase sensitivity |
| 동일 frozen discrete ψ의 짧은 common windows | vector decomposition와 Gram cross terms | 오류가 핵 근방인지 CAP contact인지 |

Grid-offset control은 physical Hamiltonian의 다른 discretization이고 CAP-off control은 다른 boundary model이다. 이를 같은 configuration 생산 데이터처럼 pool하지 않는다. Tiny-grid 결과를 production h=.20, full horizon, production prepared state에 자동 이전하지 않는다. 가능한 후속 replay는 원본 immutable checkpoint를 정확한 별도 진단 입력으로 쓰고 change window, resource, claim ceiling을 사전 등록한다. 이 메모는 production replay나 추가 collision을 승인하지 않는다.

## 9. 물리모델 부족과 수치 부족은 다른 판단

[S8] §2.1은 heavy nuclei를 classical straight lines로 다루는 조건을 제시하고, Eq. (5)는 cross section을 `T→∞` limit의 `2π∫b P_X(b)db`로 정의한다. 이 연구와 같은 구조의 전자 TDSE 모델은 있으나 해당 논문의 수치 representation/regularization과 published 5–80 keV 범위가 현재 100 keV/u 단일 b 문제를 직접 인증하지 않는다.

같은 frozen H_h(t)에서 dt 변화로 P3가 변하면 그 차이는 우선 시간수치 문제다. 단지 p가 2.5를 넘었다고 straight-line approximation, Coulomb physics, charge-transfer mechanism이 실패한 것은 아니다. 반대로 full-H 시간검증이 성공해도 nuclear recoil/deflection, infinite-nuclear-mass approximation, relativistic correction, cross-section impact-parameter quadrature, asymptotic state extraction 및 all-bound completion을 검증한 것은 아니다. 물리적 정확도 claim의 목표가 sub-percent라면 이 approximation들도 최종 목표에 맞는 별도 model discrepancy 연구가 필요하다. 여기서는 모델을 바꾸지 않는다.

## 원전 및 공식 코드: 재현 가능한 locator

아래 원전·공식 구현은 직접 열람했다. 구체적 진단과 분해식은 위에서 직접 유도로 구분했다.

- **[S1]** M. Hochbruck, C. Lubich, *On Magnus Integrators for Time-Dependent Schrödinger Equations*, SIAM J. Numer. Anal. 41 (2003), 945–963, DOI 10.1137/S0036142902403875. Author manuscript: https://ianm-mao.math.kit.edu/download/papers/magnus.pdf . Locator: Eq. (2.8),(2.9),(3.2),(3.4), Theorem 3.1. Evidence: read original manuscript; conditions, not a Coulomb+CAP certification.
- **[S2]** A. Alvermann, H. Fehske, *High-order commutator-free exponential time-propagation of driven quantum systems*, J. Comput. Phys. 230 (2011), 5930–5956. https://arxiv.org/pdf/1102.5071 . Locator Eq. (61), PDF p19. Evidence: original CF4 coefficients; current static-CAP contractivity is DERIVED.
- **[S3]** SciPy DOP853 official API: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.DOP853.html . Locator Parameters max_step, rtol, atol; Attributes nfev/status.
- **[S4]** SciPy v1.18.0 source: https://github.com/scipy/scipy/blob/v1.18.0/scipy/integrate/_ivp/rk.py . Locator RungeKutta._step_impl and DOP853._estimate_error_norm. Evidence: local error acceptance rule, not global goal error bound.
- **[S5]** SciPy expm_multiply official API: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.expm_multiply.html . Locator signature, A/traceA parameters, Notes/References.
- **[S6]** W. Auzinger, H. Hofstätter, O. Koch, M. Quell, *Adaptive Time Propagation for Time-dependent Schrödinger equations*, Int. J. Appl. Comput. Math. 7, 6 (2021), online 2020-12-19. https://link.springer.com/article/10.1007/s40819-020-00937-9 . Locator Eqs. (6)–(11); Section on defect-based estimators and Lanczos inner error. Evidence: asymptotic estimator, independent inner/external error control.
- **[S7]** O. Shemer, D. Brisker, N. Moiseyev, *Optimal reflection-free complex absorbing potentials for quantum propagation of wave packets*, Phys. Rev. A 71, 032716 (2005), DOI 10.1103/PhysRevA.71.032716. https://arxiv.org/pdf/quant-ph/0508084 . Locator Eq. (6), §4 Eqs. (20)–(21). Evidence: inner-region objective and finite-grid slow-wave reflection, not current mask quantitative bound.
- **[S8]** D. Tseliakhovich, C. M. Hirata, K. Heng, *Excitation and charge transfer in H–H+ collisions at 5–80 keV and application to astrophysical shocks* (2012), arXiv:1201.4778v2. https://arxiv.org/pdf/1201.4778 . Locator §2.1, Eq. (4)–(5), PDF p3. Evidence: model assumptions/cross-section definition only. PDF auto-header ‘Printed 6 November 2018’ is not paper year.

## 연구 범위

이 문서는 기존 데이터 재계산, 원전 조사, 수학 유도에 해당한다. 새 production collision 또는 production solver 변경의 결과를 제시하지 않는다.
