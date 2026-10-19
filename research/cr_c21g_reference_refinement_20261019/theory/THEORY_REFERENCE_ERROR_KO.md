# C21G: reference 오차와 상쇄 이후 정련의 판정 계약

작성: 2026-10-19 UTC. 독립 이론 검토. 새 native 실행을 수행하지 않았다.

## 1. 범위와 재사용 근거

이 작업은 PR83 `d780c2c53f869c914add1d5492312d0bc507f976`의 C21F 결과를 이어받는다. Root의 새 GitHub·백업 조사에서 확인 범위 안에 PR83 이후 native 결과가 없다는 intake를 받은 뒤 시작했다. 기존 native raw 분석, 56개 검증, point audit, C21F 복구·게시를 재실행하지 않았다.

모델은 기존의 고정 source birth, energy cohort, opacity, FLRW geometry, native non-photo kernel을 유지한다. 각 cohort의 birth amplitude A와 comoving energy q, helium abundance Y는 두 비교 해에서 동일하다. 이 계약의 오차는 이 고정 IVP 안에서의 수치 오차다. Source-age, spectrum, angle, Case B, Bianchi, full EoR의 모델 오차는 포함하지 않는다.

직접 읽은 실행 소스:

- [reference_tau.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/d780c2c53f869c914add1d5492312d0bc507f976/research/cr_c21e_event_native_20261018/src/reference_tau.py): tau 재구성, scalar tolerance 검증, Y=0 축소, event-cell endpoint 처리.
- [run_experiment.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/d780c2c53f869c914add1d5492312d0bc507f976/research/cr_c21e_event_native_20261018/src/run_experiment.py): fixture digest, 고정 breakpoint, reference dispatch, endpoint ledger, FULLMID/hybrid 실행.
- [event_coupler.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/d780c2c53f869c914add1d5492312d0bc507f976/research/cr_c21e_event_native_20261018/src/event_coupler.py): gas domain과 EOS.

## 2. Optical depth에서 photon observable로 가는 정확한 오차 관계

### 2.1 양의 활성 cohort

A>0이고 cohort가 이미 태어났다고 하자. 두 유한 optical depth tau와 tau_tilde에 대해

\[
N=Ae^{-\tau},\qquad \widetilde N=Ae^{-\widetilde\tau},\qquad
\delta\tau=\widetilde\tau-\tau
\]

이므로 실수 산술에서 정확히

\[
\log\widetilde N-\log N=-\delta\tau,\qquad
\widetilde N-N=N\operatorname{expm1}(-\delta\tau).
\tag{1}
\]

따라서 만일 별도의 검증으로 |delta tau|<=eta를 보장했다면

\[
\frac{|\widetilde N-N|}{N}\le\operatorname{expm1}(\eta),\qquad
|\widetilde N-N|\le N\operatorname{expm1}(\eta).
\tag{2}
\]

이 상계는 eta가 실제 coordinate 오차의 상계일 때의 조건부 정리다. Solver의 `atol_tau`를 eta로 치환할 근거는 없다. 희망 상대 오차 epsilon에서 `log1p(epsilon)`을 local tau scale의 출발값으로 쓰는 것은 설계 규칙이며 전역 오차 인증이 아니다.

양쪽 해를 대칭으로 비교할 때는

\[
|\widetilde N-N|=
\exp\{\max(\ell,\widetilde\ell)\}
\left[-\operatorname{expm1}(-|\delta\tau|)\right],
\quad \ell=\log A-\tau.
\tag{3}
\]

이 식은 작은 delta tau에서 두 매우 가까운 exp 값을 빼는 일을 피한다. 양의 차의 log는

\[
\log|\widetilde N-N|=
\max(\ell,\widetilde\ell)+
\log\left[-\operatorname{expm1}(-|\delta\tau|)\right].
\tag{4}
\]

delta tau=0인 경우에만 차는 정확히 0이고 log 차는 확장실수 -infinity다. JSON에는 이 수를 넣지 말고 `difference_zero: true`와 `log_abs_difference: null`처럼 의미를 함께 저장한다. 같은 A라면 delta log를 두 `log_survivor`의 뺄셈으로 만들기보다 저장된 두 tau의 차의 음수로 계산하는 편이 공통 log A의 상쇄를 명시한다.

### 2.2 0과 underflow의 구별

- 아직 활성화되지 않은 cohort는 모델상 N=0이다. 비교 시 양쪽 activation과 birth identity가 일치해야 한다.
- A=0이면 역시 구조적 0이다. 상대 오차와 log-survivor 오차는 정의하지 않는다. Tau가 존재하더라도 이 photon에 대한 상대 정확도 지표로 쓰지 않는다.
- A>0, active, finite tau이면 실수 N은 양수다. Floating reconstruction이 0을 반환하면 이것은 underflow 기록이며 구조적 0이 아니다. 유한 log-survivor와 (4)는 계속 보존한다.
- Normal, subnormal, rounded-to-zero는 실제 dtype의 값과 `finfo.tiny`, `nextafter(0,1)`를 관측하여 구별한다. 이 숫자를 stock floor로 넣지 않는다. 특정 하드코딩된 tau 값만으로 underflow 판정을 대신하지 않는다.

양쪽 재구성 값이 모두 0이어도 log-survivor가 다르면 상대적인 survivor 차가 존재한다. 그 쌍의 absolute difference를 floating 0만으로 완료 판정해서는 안 된다. `log_abs_difference <= log(positive_absolute_target)`를 별도로 검사하면 표현 범위 아래의 양도 비교할 수 있다. 매우 작은 photon을 상대 오차에서 조용히 제외하지 않는다. 절대량, log량, 표현 상태를 각각 보고한다.

여기서 (1)–(4)는 고정된 실수 A, tau에 대한 항등식이다. Float의 log A 및 tau 자체의 반올림 오차까지 자동 인증하는 정리는 아니다. 계산한 차를 정확한 IVP 오차라고 해석하는 데도 별도 reference 근거가 필요하다.

### 2.3 집계량

끝점의 E_i=q_i/a_end>0가 같으면

\[
|\delta N_{\rm total}|\le\sum_i|\delta N_i|,\qquad
|\delta U_\gamma|\le\sum_i E_i|\delta N_i|.
\tag{5}
\]

서로 다른 cohort의 부호 상쇄로 순 photon number 차가 작아지는 것을 확인하려면, signed sum과 우변의 absolute sum을 함께 저장해야 한다. (4)를 사용한 log-sum-exp 집계는 underflow를 숨기지 않는다. 이 끝점 관계는 누적 photo event나 gas heating 오차의 상계가 아니다. 그 양은 전체 경로와 gas 반응의 안정성에 의존한다.

## 3. Gas EOS의 정확한 오차 관계

실행 코드의 상태는 g=(x,y,z,w), Y=n_He/n_H이고

\[
D=1+Y+x+Y(y+2z),\quad K=\tfrac32 k_B,\quad T=\frac{w}{KD}.
\tag{6}
\]

기존 domain 0<=x<=1, y>=0, z>=0, y+z<=1, w>0, Y>=0에서

\[
1+Y\le D\le 2+3Y.
\tag{7}
\]

같은 Y의 두 물리 상태에 대해 delta D=delta x+Y delta y+2Y delta z이다. 정확히

\[
\widetilde T-T=
\frac{D\,\delta w-w\,\delta D}{K D(D+\delta D)}
=\frac{\delta w/K-T\,\delta D}{D+\delta D},
\tag{8}
\]

\[
\frac{\widetilde T-T}{T}=
\frac{\delta w/w-\delta D/D}{1+\delta D/D}.
\tag{9}
\]

따라서 thermal-energy 오차와 temperature 오차는 같은 지표가 아니다. 전자수의 차가 분모를 바꾸고 두 항의 상쇄도 가능하다. 코드에서는 직접 EOS로 얻은 delta T, (8)의 재계산, delta w와 delta D를 함께 저장하면 상쇄 위치를 확인할 수 있다.

만일 검증된 coordinate 오차 상계 epsilon_x, epsilon_y, epsilon_z, epsilon_w가 있고

\[
\epsilon_D=\epsilon_x+Y\epsilon_y+2Y\epsilon_z<D
\]

이면

\[
|\widetilde T-T|\le
\frac{\epsilon_w/K+T\epsilon_D}{D-\epsilon_D}.
\tag{10}
\]

두 상태가 물리 domain에 속한다는 것만으로 분모를 1+Y로 대체한 더 느슨한 상계도 성립한다. 오차 box 전체에서 epsilon_w<w와 epsilon_D<D이면

\[
\frac{w-\epsilon_w}{K(D+\epsilon_D)}\le\widetilde T\le
\frac{w+\epsilon_w}{K(D-\epsilon_D)}.
\tag{11}
\]

(10)–(11)의 epsilon이 단순한 두 numerical reference의 차라면 결과는 sensitivity envelope이며 보장된 true-temperature interval이 아니다. Y=0에서는 기존대로 y=z=0을 unknown에서 정확히 제거한다. Float perturbation으로 가짜 He 자유도를 만들지 않는다.

## 4. Local tolerance와 전역 오차를 연결하는 데 필요한 정보

SciPy v1.17.0의 Radau는 5차 Radau IIA 해를 3차 embedded estimator로 제어한다. 구현은 `atol+rtol*max(abs(y),abs(y_new))`로 나눈 local estimator의 RMS norm을 검사한다. 따라서 각 성분을 tolerance 이하로 제한하는 max-norm 검증도 아니고, endpoint 물리 오차의 인증도 아니다. D개 동적 unknown 중 하나만 오차를 지배하면 정규화된 그 성분은 sqrt(D)까지 가능하다. 또 너무 작은 rtol은 구현에서 100 machine epsilon까지 상향한다. 실제 version과 effective tolerance를 기록해야 한다. [공식 Radau 문서](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.Radau.html), [Radau 구현](https://github.com/scipy/scipy/blob/v1.17.0/scipy/integrate/_ivp/radau.py), [norm·validate_tol 구현](https://github.com/scipy/scipy/blob/v1.17.0/scipy/integrate/_ivp/common.py).

### 4.1 구성적 전역 오차 표현

각 smooth event cell에서 IVP를 u'=F(x,u), 근사 연속 경로를 v라 두고 e=v-u, residual r=v'-F(x,v)라 하자. F가 두 경로 사이의 tube에서 C1이면

\[
e'=\overline J(x)e+r,\quad
\overline J(x)=\int_0^1D_uF(x,u+\theta e)\,d\theta.
\tag{12}
\]

이것은 비선형 문제에 대한 정확한 항등식이다. 전이 행렬 Phi에 대해

\[
e(X)=\Phi(X,x_0)e(x_0)+\int_{x_0}^X\Phi(X,s)r(s)\,ds
\tag{13}
\]

이고 event restart에 실제 state jump 오차 eta_k가 있으면 Phi(X,x_k) eta_k도 더해야 한다. 현재 tau cohort birth는 활성화 변경이고 tau/g의 prescribed reset은 항등이므로 동일한 정확한 birth에서는 이 jump 오차가 0이다. Event 시간 또는 fixture가 달라지면 동일 계약이 아니며 그 오차를 생략할 수 없다.

예를 들어 선택한 norm의 logarithmic norm mu에 대해 tube 안에서 mu(Jbar)<=m(x)를 검증하고 residual도 상계했다면

\[
\|e(X)\|\le e^{\int_{x_0}^Xm}\|e(x_0)\|
+\int_{x_0}^X e^{\int_s^Xm}\|r(s)\|ds
+\sum_k e^{\int_{x_k}^Xm}\|\eta_k\|.
\tag{14}
\]

이를 (2), (10)에 넣으면 조건부 물리 오차 인증이 가능하다. 단순히 ||J||를 쓰면 stiff decay도 거대한 양의 증폭으로 셀 수 있으므로 전이 행렬이나 logarithmic norm의 방향성 정보가 더 적절할 수 있다. 여기서는 그 tube, residual enclosure, roundoff enclosure를 계산하지 않았으므로 native global certificate는 `NOT_ESTABLISHED`다.

스칼라 endpoint observable Q의 경우 평균 endpoint gradient l과 adjoint -p'=Jbar^T p, p(X)=l을 사용하면

\[
Q(v(X))-Q(u(X))=p(x_0)^Te(x_0)+\int p^Tr\,dx+\sum_kp(x_k)^T\eta_k.
\tag{15}
\]

Q가 nonlinear이면 l은 두 endpoint 사이에서 gradient를 적분한 값이다. 근사 경로의 Jacobian과 gradient를 쓰는 실용 adjoint estimator에는 선형화 잔여항과 adjoint 오차가 추가된다. 이 분해의 기존 근거는 Cao–Petzold의 residual/condition 기반 연구다. 그 논문을 현재 native 문제의 인증 완료로 인용하지 않는다. [저자 원문, SIAM J. Sci. Comput. 26(2), 2004, DOI 10.1137/S1064827503420969](https://people.cs.vt.edu/~ycao/publication/siam_42096.pdf).

### 4.2 이번 ladder의 한계가 구체적으로 생기는 지점

동일 kernel, source, event 처리의 공통 편향은 tolerance를 줄여도 비교 차에서 상쇄된다. 특히 현재 RHS는 cell 안의 평가 x를 `lo+1e-9*(hi-lo)`와 `hi-1e-9*(hi-lo)` 사이로 제한한다. 이는 기존 one-sided endpoint policy이며 tighter tolerance가 이 고정 perturbation을 제거하지 않는다. 이번 작업은 기존 모델 정체성을 유지하고 이 정책을 receipt에 적는다. Global certificate에는 그 효과까지 residual로 다루는 별도 검토가 필요하다.

Finite ladder에서 R_k=R_true+b+c_k, c_k가 작아지는 경우를 생각하면, R_{k+1}-R_k는 공통 b를 알려주지 않는다. 따라서 마지막 두 reference가 일치했다는 사실만으로 b=0이나 |R_k-R_true|<=|R_k-R_{k-1}|를 추론할 수 없다. 이것은 ladder를 버릴 이유가 아니라 그 판정명을 empirical로 제한하는 이유다.

## 5. 실행 가능한 tolerance ladder와 사전 판정

### 5.1 입력과 기록

기존 L0=`rtol=2e-10, scalar atol=2e-13, max_step=cell_width/8` 결과는 identity를 검증해 재사용한다. Root와 검토한 새 설계는 아래와 같다. 수치는 결과를 보기 전에 선언하는 진단 설계값이며 물리 상수가 아니다. 새 vector profile은 기존 scalar profile과 구별한다.

| Level | rtol | Vector atol multiplier alpha | max_step | 역할 |
|---|---:|---:|---|---|
| L0 | 2e-10 | scalar 2e-13 | cell_width/8 | 기존 native 결과 재사용 |
| L1 | 2e-11 | 2e-14 | cell_width/8 | 새 component reference |
| L2 | 2e-12 | 2e-15 | cell_width/8 | 새 stricter reference |
| L3 | 2e-13 | 2e-16 | cell_width/8 | 새 tight reference |
| L3M | 2e-13 | 2e-16 | cell_width/16 | 같은 tolerance의 step-cap 민감도 |

각 성분의 atol은 alpha*S_j다. S_tau=S_fraction=1(무차원), S_number=1(per H), S_thermal=w_birth(eV/H)로 둔다. Energy ledger에는

\[
S_E=w_{\rm birth}+b(Y)\cdot g_{\rm birth,frac}
+\sum_i A_iq_i\exp(-x_{{\rm birth},i})
\tag{23}
\]

를 권장한다. 마지막 합은 처음 광자와 미래의 고정 source birth의 에너지까지 포함한다. 모든 항은 고정 fixture에서 계산되며 물리 fixture에서 w_birth>0이므로 floor 없이 양수다. Output이나 현재 error에 따라 scale을 바꾸지 않는다. 구조적 zero ledger도 양의 명시된 tolerance를 받으며 state에 epsilon을 추가하지 않는다. Scalar API도 그대로 유지하되 같은 L0 profile이라고 자동 표기하지 않는다. 권장 API 구조는 다음과 같다.

```python
ToleranceSpec(
    label, rtol, atol_tau, atol_fraction,
    atol_thermal_eV_H, atol_number_H, atol_energy_eV_H,
    max_step_divisor, max_rhs_evaluations,
)
```

Full state 순서는 tau[M], gas fractions[3], gas thermal[1], photo[3], ci[3], rr[3], dr[1], escape/cmb/photon_work/gas_work/heat[5]다. `atol_full`을 이 순서로 만들고 `atol_full[dynamic]`를 reduced solve에 넘겨야 한다. 특히 Y=0에서 두 He fraction unknown을 뺀다. 입력 shape, finite, positive를 검사하고 SciPy rtol 조정 하한보다 작은 요청은 명시적으로 거부하거나 요청값/실효값을 둘 다 저장한다. 현행 `all(math.isfinite(v) ... for v in (rtol,atol))` 검증은 vector atol을 받지 못하므로 변경 지점이 명확하다.

각 run receipt는 source/fixture/raw SHA, dtype·Python·NumPy·SciPy, tolerance profile 전체, dynamic dimension, endpoint policy, max_step, nfev/njev/nlu 및 실제 RHS 호출수, provider budget, solver status, gas domain, underflow 정보를 기록한다. 실패도 create-only 보존한다. 성공 exit와 observable convergence를 별개 상태로 둔다.

### 5.2 물리 endpoint 비교

L0–L1, L1–L2, L2–L3, L3–L3M의 signed component difference를 모두 보존한다. Root와 검토한 사전 pilot agreement 목표는 다음과 같다.

| Observable difference | common_ic | native_source |
|---|---:|---|
| max(abs(delta fractions), abs(delta w)/w_birth) | 1e-14 | 1e-10 |
| max_i abs(delta N_i) | 1e-14 per H | 1e-12 per H |
| max active positive abs(delta log N_i) | 1e-10 | 1e-8 |

실제 채택값과 photon budget의 정확한 aggregate 정의는 실행 manifest에 버전 고정해야 한다. Common gas 1e-14는 기존 dominant common FULL64 오차 약 1e-12의 약 1%를 구별하기 위한 설계값이다. Native gas 1e-10는 기존 native FULL64 gas norm 약 7.7e-7보다 세 자릿수 이상 작은 비교 해상도다. 이를 아직 실행하지 않은 n256 오차의 선험 상계로 읽지 않는다. 두 fixture는 opacity/source 계약이 달라 별도의 해상도 목표를 가질 수 있다. Common 실패가 native_source의 완료를 막지 않도록 개별 판정한다.

Temperature의 직접 차와 (8), photon energy의 signed/absolute 집계는 별도로 보고한다. 필요하면 그 진단 예산도 실행 전에 고정한다. 어떤 숫자도 native 정확도 인증에 사용하지 않는다. 기존 보존 수지 기준은 변경하지 않고 원시 수지와 reference 간 수지 변화량을 각각 보고한다.

최소 판정은 (a) 입력 identity 일치, (b) solver/domain 통과, (c) 마지막 tier 차와 tight mesh 차가 선언된 목표 안에 있는지, (d) tier 차가 줄었는지, 또는 인접한 두 차 모두 이미 목표 아래인지의 조합이다. 각 observable을 따로 판정한다. 모든 delta=0이면 `AGREEMENT_AT_RECORDED_PRECISION`이고 인증된 0 오차가 아니다. Step cap을 바꿔도 실제 grid가 안 바뀌면 `MESH_CAP_INACTIVE`로 적어, 별개의 mesh 검증이 성립한 것처럼 과장하지 않는다. 비수축 또는 목표 초과이면 `REFERENCE_UNRESOLVED`; 소스나 threshold를 바꿔 PASS를 얻지 않는다. 추가 계산은 사전 예산과 새 독립 node를 필요로 한다.

마지막 차와 mesh 차의 최대 U_j=max(|R3_j-R2_j|, |R3M_j-R3_j|)는 empirical sensitivity indicator다. `global_error_bound`에는 null을 쓴다. U_j에 안전계수를 곱해도 엄밀한 상계가 되지 않는다. Native discretization error가 0.05^{-1} U_j보다 큰지 확인하는 5% reference-share 규칙은 차수 판정의 실용 해상도 조건으로 사용할 수 있다. 이는 true error가 그 범위에 있다는 인증이 아니다. 이 진단이 native n128/256 실행을 여는 경우 그 gate는 계산 예산을 배분하는 REF_READY 조건이며 이론적 수렴 PASS가 아니다.

## 6. 차수와 상쇄 이후의 정련

### 6.1 Reference의 불확실성이 차수에 주는 영향

어떤 성분의 stored error를 E_n=u_n-R, true reference 오차의 **검증된** 상계를 b라고 가정하면

\[
\max(0,|E_n|-b)\le |u_n-u_*|\le |E_n|+b.
\tag{16}
\]

|E_n|>b와 |E_2n|>b에서 true two-level order는 다음 interval 안에 있다.

\[
\log_2\frac{|E_n|-b}{|E_{2n}|+b}
\le p\le
\log_2\frac{|E_n|+b}{|E_{2n}|-b}.
\tag{17}
\]

b 대신 empirical U를 대입하면 이름도 `reference_sensitivity_order_interval`로 제한한다. 한 분모나 분자의 lower bound가 0이면 유한 차수 interval을 억지로 출력하지 않는다. Sign도 |E_n|>b일 때만 조건부로 확정할 수 있다. Max norm의 active component를 각 n에 저장하여 component 교체가 만든 차수를 식별한다.

### 6.2 새 native 작업의 최소 행렬

기존 native_source FULLMID/hybrid n=64를 그대로 보존하고 n=128,256만 추가한다. 한 방법의 세 연속 level로

\[
p_{\rm free}(n,2n,4n)=
\log_2\left|\frac{u_n-u_{2n}}{u_{2n}-u_{4n}}\right|
\tag{18}
\]

를 구하면 Radau reference에 의존하지 않는다. 그럼에도 작은 차의 roundoff, Newton 오차, 비점근 구간의 영향은 남는다. 차가 0이거나 수치 해상도 아래이면 `UNRESOLVED`로 두고 0/0을 차수로 바꾸지 않는다. 이 차수는 성분별로 먼저 계산한다.

기존 유도의 smooth fixed-cell 가정 아래

\[
u_H(n)=u_*+A/n+B_H/n^2+O(n^{-3}),\quad
u_F(n)=u_*+B_F/n^2+O(n^{-3})
\tag{19}
\]

라고 쓸 수 있는 점근 구간을 가정하면 d_n=u_H(n)-u_F(n)는

\[
d_n=A/n+(B_H-B_F)/n^2+O(n^{-3}).
\tag{20}
\]

따라서 d_64/d_128, d_128/d_256의 성분별 차수는 공통 reference 오차를 정확히 제거한다. Generic A가 0이 아닐 때 1차에 접근하는지 측정할 수 있다. A=0인 특수 경우, 비점근성, observable 상쇄를 가능성으로 남긴다.

추가 fitting 없이 두 level로 leading coefficient를 분리할 수 있다.

\[
\widehat A_n=n(4d_{2n}-d_n)=A+O(n^{-2}),\qquad
\widehat B_n=2n^2(d_n-2d_{2n})=(B_H-B_F)+O(n^{-1}).
\tag{21}
\]

새 n=128,256은 Ahat_64와 Ahat_128의 안정성까지 확인한다. FULLMID의 leading 2차 계수는 조건부로

\[
\widehat B_{F,n}=\tfrac43n^2(u_F(n)-u_F(2n))=B_F+O(n^{-1}).
\tag{22}
\]

이 값들은 (19)의 가정에 의존하는 진단량이다. Fit이 zero crossing을 예측한 것으로 읽지 않는다. 이전 hybrid thermal n=32/64의 실제 sign bracket 및 네 점 fit의 실패 기록을 그대로 보존하고, 새 참조에서 각 n의 signed error를 다시 읽는다. 새 n=128,256의 부호나 차수를 미리 단정하지 않는다.

## 7. 판정과 구현 연결

이번 이론 결과는 (1)–(11)의 coordinate/observable 항등식과 조건부 bound, (12)–(15)의 certificate에 필요한 residual·stability 분해, (16)–(22)의 reference sensitivity와 상쇄 이후 정련 진단이다. Native absolute error 인증이나 새 native convergence 측정은 아직 수행하지 않았다.

Root가 여기서 구현할 수 있는 bounded code는 명시적 reference tolerance/profile 전달, reduced vector atol, create-only 실행 영수증, log-domain photon 차, EOS 차 검증, observable별 ladder 판정, reference-free/component order 및 Ahat/Bhat 분석이다. Native kernel 자체를 재구현할 필요가 없다. NCP에는 같은 pin의 compile, 제한된 L1/L2/L3/L3M reference, 조건이 충족된 native_source FULLMID/hybrid n128/256, 원시 결과 보존만 남길 수 있다.

| DAG node | 이 파일의 상태 | 게시·백업 상태 |
|---|---|---|
| 새 결과 intake | Root의 현재 receipt 재사용 | Root delivery receipt 참조 |
| 좌표–물리 오차 유도 | COMPLETE_CONDITIONAL_MATH | 이 파일을 root가 새 checkpoint에 포함 |
| SciPy/전역 오차 문헌 교차 | COMPLETE_PRIMARY_SOURCE_CHECK | LITERATURE_INTAKE.json 동봉 |
| Scalar/vector tolerance 설계 | READY_FOR_IMPLEMENTATION | 후보 정책; 실제 채택값은 실행 manifest |
| 새 경량 코드 검증 | ROOT_WORK_IN_PROGRESS | 이 독립 검토는 실행 완료를 주장하지 않음 |
| 새 native reference/128/256 | NOT_RUN | NCP 실행 receipt 필요 |
| 엄밀한 native 전역 오차 인증 | HOLD_SEPARATE_VALIDATION | 안정성 tube·residual enclosure 없음 |
| Source/spectrum/angle/Case B/Bianchi/full EoR | HOLD | 기존 독립 검증 조건 유지 |

## 8. 문헌 확인 내역

Exa로 official SciPy 1.17.0 문서와 버전 고정 구현을 직접 읽었다. SciSpace의 자연어 질의는 stiff IVP에서 local tolerance와 endpoint global error의 관계, 추가 stability/adjoint 정보에 한정했다. SciSpace는 Cao–Petzold 항목을 2005로 반환했지만 저자 PDF 및 UC 원문은 2004를 명시한다. 인용에는 원문의 2004를 사용한다. 이 불일치와 실제 질의/URL은 LITERATURE_INTAKE.json에 보존한다. 광범위한 새 문헌 심사나 novelty/no-go 주장은 하지 않았다.
