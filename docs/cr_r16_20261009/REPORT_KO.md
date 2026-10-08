# bass_cr R16: 전역 광학 functional, signed adjoint, 연속 방출원 조건부 결합

**연구일:** 2026-10-09 KST  
**판정:** `R16A_CONDITIONAL_CONTINUOUS_SOURCE_TAU_SIGN_CLOSE__R16B_SIGNED_ADJOINT_DIAGNOSTIC_ONLY`  
**과학적 권한:** FT03 첫 macro (0–1.25×10⁹ proper s), prescribed FLRW, HI/He physical fit의 선언된 Toy 동역학, HH/RCT/CR OFF. Grackle 기반 R13은 다른 모형이다.

## 1. 고정된 실제 입력과 신규성

- 원 `bass_cr` R15: `research/ncp-r15-20261008`, science `3a6b141973f0141443396e8e425d9acd637fc393`, delivery HEAD `e42b93d1d249c674f2e5994381a087ed2284c38c`. 봉인 ZIP `BASS_CR_NCP_R15_20261008_v1.zip` SHA256 `0fe656016c1de11fa2d4d1e5dd0227bdd79d0b2e53ee1ad253b49290725ac5aa`; 6,070,096 bytes, 95 payloads. 이 archive의 R15 연속 six-birth shadow−native linear optical 구간은 그대로 계승했다.
- 읽기 전용 REI BRIDGE13는 R15 내부 ZIP `a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48`. BRIDGE14는 추가로 직접 원격 회수하여 `REI_XTHREAD_BRIDGE14_20261008.zip` SHA256 `5fc3b77d9a17553f7cd34f61711983776edbb992ba9ebd294420b9813a818515`, 517,269 bytes로 검증했다. BRIDGE14의 부모 REI13 해시가 R15의 외부 donor와 일치한다.
- 후행 BRIDGE15는 compiled native 증명과는 분리된 **조건부 IEEE 누적 장부 한정**이다. 본 연구의 tau 인증·birth/clock에는 사용하지 않았다.
- 기존 R15의 32 root/전시간 defect·R13 Grackle native source·REI의 B14/B15 interval 과학 suite는 반복하지 않았다. 신규 계산은 정확 유리수 전역 Fubini 재구성, REI14 source-only optical 상계 전달, midpoint-AD signed adjoint 및 독립 forward linearized check, 20 focused tests다.

## 2. 전역 optical Fubini: 재배치만으로 폭을 줄일 수 없다

Native 32-cell `[t_i,t_{i+1}]`의 `variant=0` gas endpoint와 carried photon stock을 직접 대조했다. **31 gas/old photon 인터페이스의 값이 exact f64 bit로 동일**했고 birth index는 `[4,8,12,16,20,24]`였다. 따라서 gas state의 nominal jump가 없고 optical tau jump도 0이다. Photon birth weight와 photon error는 동역학 ΔF를 통해 반영된다.

`r(t)=ŷ'(t)-F(t,ŷ(t))`, `e=y−ŷ`, `g(t)=C_T n_H(t) c_e`, `c_e=(1,f_He,2f_He,0,… )`, `W(t)=∫_t^T exp(-3Hs)ds`라 두면

\[
\Delta\tau=-C_Tn_{H0}\int_0^T W(t)c_e^\top r(t)dt+C_Tn_{H0}\int_0^T W(t)c_e^\top [F(y)-F(\hat y)]dt.
\]

해당 정상화에 맞춰 R15의 기존 560 full-time residual panel을 다시 독립적인 **전역 양의 커널**로 합성했다. 내부 Fubini 원리와 동일한 donor absolute-Jacobian `N·E` 상계를 사용하면 결과는

`[1.8495168669507532,2.1010588762679408]×10^-17`

이며 이전 R15 구간과 표시 정확도에서 완전히 같다. 정확 유리수 endpoint 차는 하단 `−3.09322×10^-57`, 상단 `−7.40883×10^-76`뿐이다. 새로운 폭 축소라고 주장하지 않는다. 이 재배치가 유리하지 않은 이유는 주로 cell 경계 e-box 및 절댓값 비교행렬의 signed correlation 소실이다. 향후 NCP는 unsigned `N`의 단순한 재조합에 시간을 쓰지 않아야 한다.

## 3. 실제 5→11D signed adjoint 계산, 진단만

각 cell `s∈[0,1]`에서 `A_i=∂F_s/∂z (s=1/2, ŷ(1/2))`를 원 소스의 interval-AD로 평가한 뒤, actual 17/33 point residual을 cubic spline으로 *수치 보간*했다. 

Piecewise frozen linear model은 `e'=A_i e-r_i`이고 optical sensitivity는 `g_i(s)=C_TnH0 L_i exp[-3H(t_i+L_i s)] c_e`이다. 후방 \(−\lambda'=A_i^\top\lambda+g\), `lambda(T)=0`, birth에서 `lambda^- = B^T lambda^+`로 연결했다. Same θ, nominal birth weight를 선택한 진단의 직접 event δ=0, 그러나 파라미터 상관을 인증한 것은 아니다.

- midpoint A, **33개 residual interpolation nodes/cell**: forward `1.9731044416400455e-17`; backward dual `1.97310444167335e-17`; 상대 dual gap `1.6879e-11`.
- midpoint A, 17 nodes: forward `1.9731044472169032e-17`, backward `1.97310444716053e-17`. Archived R15 nonlinear IVP diagnostic `1.9731045074324378e-17`; midpoint33 adjoint와 차는 `−6.57591e-25`.
- A sample s=.25/.75, 17 nodes: backward `1.97310437790160e-17` / `1.97310451641945e-17`. 이 sample dependence는 수치 approximation sensitivity이며 certified error bar가 아니다.
- Jacobian signed offdiagonal entries: 양수 612, 음수 192 (32 sampled matrices). Absolute Jacobian majorant만으로는 cancellation을 복원하지 못한다.

사용한 원본 source는 REI BRIDGE13의 변경하지 않은 `chain_defect.gas_photo_rhs`; 새로운 whole-data numerical forward/backward *linearized diagnostic*이며 새 native/IVP 원 donor scientific campaign 또는 물리적 source 변경이 아니다. 한 번의 45초 실행 제한은 plain source를 수치적분기의 모든 RHS call마다 재평가해 발생했다. 안전한 별도 17/33-node cubic residual **진단 interpolation**으로 바꾸어 7–13초 내 계산했다. 수치 보간은 진정한 잔차 interval 증명이 아니므로 R16B는 `NUMERICAL_DIAGNOSTIC_ONLY`다.

이 단계의 정확한 목표항등식은 nominal Jacobian `Ahat(t)`를 쓰는 경우

\[
\Delta\tau=\lambda(0)^T e(0)-\int_0^T\lambda(t)^T r(t)dt
+\sum_{j}\lambda(t_j^+)^T\delta_j
+\int_0^T\lambda(t)^T\big[F(y)-F(\hat y)-A_{\rm hat}e\big]dt.
\]

여기서 `δ_j`는 native interface·birth weight의 *오차*이며, 무조건 0이라고 둘 수 없다. 동역학의 Jacobian이 실제로 시간의존이고 e에도 의존하므로 본 numeric frozen A 점추정을 조건부 인증의 구간으로 대체할 수 없다. 다음에는 signed interval A 또는 Hessian second-order remainder, matrix exponential/backward adjoint enclosure와 θ 상관을 실제로 검증해야 한다.

## 4. 신규 조건부 결론: continuous **constant-S** source까지 허용한 τ 양의 부호

BRIDGE14의 `SOURCE_MEASURE_CERTIFICATE.json`는 같은 FT03/FLRW `(0..1.25e9)s` 동안 연속 양의 constant emission `S=f64(5e-15)`와 같은 source mass의 six finite Gauss births의 **source-only** Thomson 부분 τ 차에

`|τ_cont,S − τ_cont,6birth| ≤ 1.021772255776130141…e-17`

을 인증했다(같은 초기 gas/source energy θ, cutoff 미횡단, Picard gas tube). 실제 계약과 public 안전 외측 표시를 보수적으로 선택해 `B_S=1.021773e-17`로 고정했다. 원래 source는 `σ_T=f64(6.6524587e-25) cm²`, R15는 `σ_T=f64(6.6524587e-29) m²`; 정확 Fraction 검사에서 R15 CT / REI CT `=1−9.976…×10^-18`로 1보다 작아 이 기존 source 상계를 줄이지 않고 재사용할 수 있었다.

실수 삼각부등식에 따라

\[
\boxed{\begin{aligned}
\tau_{\rm cont,S}-\tau_{\rm native}
&= (\tau_{\rm cont,S}-\tau_{\rm cont,6b})
 +(\tau_{\rm cont,6b}-\tau_{\rm native})\\
&\in [8.277438669507532\times10^{-18},\;3.122831876267941\times10^{-17}].
\end{aligned}}
\]

**하한이 엄격히 양수인 새로운 조건부 source+time optical 결론**이다. 정본 분자·분모와 허용 source-only 상계는 `results/COMBINED_TAU.json`에 있다. Absolute first-macro continuous-emission tau는 `[2.554130524611589,2.554130547562469]×10^-9`(source/native recurrence 모두 이번 선언모형)이다. 서로 다른 source의 정밀한 상관성을 가정하지 않고 구간합으로 넓혔다. 이는 REI BRIDGE14 소스 certification을 *새로 만들거나 고친* 것이 아니라 기존 donor 근거를 검증 가능한 같은-observable consumer로 **새로 결합한** 결과다.

## 5. 테스트·실패·입증범위

- 새 focused test 20개 PASS: adjoint synthetic forward/backward, 비정방 birth embedding transpose, nominal state interface, 음의 잔차 sign, 실제 32-cell 560-panel Fubini/clock/6 birth, source bound 누락·가상 큰 source bound의 부호 거절, 실제 R15+BRIDGE14 input 계약.
- Combined-bound 구현은 의도적 잘못된 (0,0) 기능에 대해 **세 assertion RED(1)→GREEN(0)**을 기록했다. Adjoint는 첫 파일 미구현 ImportError RED여서 assertion RED라고 주장하지 않는다. 이외 시험은 구현 후 추가했다.
- 실제 signed A sampling 32회에서 원 FT03 source AD를 사용; forward linearized와 backward dual은 별도 DOP853 적분 경로. 네 가지 sampled design과 residual held-out error 자료를 저장했다. 원 소스가 창 내부에서 cutoff를 지나지 않는 donor 증명을 계승한다.
- 실패 로그: 잘못된 R15/REI14 schema 가정으로 소비기가 두 차례 실패했지만, 실제 ZIP을 직접 읽어 고쳤다. 첫 signed source의 scale IV→float 변환 실패, plain IVP 45초 timeout도 수정 전 로그를 보존했다. 이 오류를 과학적 부호 반전으로 분류하지 않는다.
- 독립 human/agent review, 다른 entire interval RHS backend, formal proof assistant는 미실행이다. `CR_OFF_FASTEST`, precision atomic PARKED, HH research ACTIVE, G02 UNRESOLVED, all_bound OPEN, b_grid NO_GO, capture=false, physical/production HOLD, owner_ACK/global_CR/observer_tail `null` 유지.

## 6. 다음 최소 단위

NCP의 새 코드는 `R16B_CERTIFIED_SIGNED_ADJOINT_WITH_BIRTHS`다. 실제 시간의존 signed interval Jacobian 또는 Hessian nonlinear remainder를 완전히 제한해 *validated* backward dual optical goal 범위를 만들어라. R15/R16A의 정확 기준 및 donor source identity를 사용하고 원래 32-cell root와 생존 원자물리계를 재실행하지 마라. 유효구간이 R15보다 좁아지지 않으면 FAIL이 아니라 `NO_CERTIFIED_SHARPENING`으로 종료하고 원 R16A 결론을 유지하라. 그 밖에 Grackle R13는 동일 owner stage가 없으면 BLOCKED_OWNER_INPUT, G02 bank는 BLOCKED_INPUT이다. 별도 REI BRIDGE15의 조건부 IEEE 누적 energy ledger를 optical certified result로 가져오지 마라.

## 재현

`python -B reproduce.py --verify-only` (오프라인 manifest/ZIP 확인)

`python -B reproduce.py --output NEW_EMPTY_DIR` (20 시험, exact global/source interval, 새 32-cell signed-adjoint diagnostic 실행). 원 donor interval/root/native 과학 suite 재실행은 없다.
