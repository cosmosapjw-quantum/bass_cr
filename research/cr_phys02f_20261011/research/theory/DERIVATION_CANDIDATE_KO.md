# CR-PHYS02F 후보 유도: 유한 창 밖의 heat 지연과 birth·체류 에너지 분해

작성 역할: `/root/phys02f_tail_theory`, 후보 유도 기여자. 이 문서는 acceptance 설계나 독립 decision review가 아니다. 최종 과학적 판단은 owner와 실제 독립 reviewer가 별도 수행한다.

근거 상태: 아래 항등식은 **derived**이며, 구성한 4상태 계와 유한 원자측도에 대한 63개 항등식을 정확 유리수 연산으로 1회 확인했다. 그 결과는 **numerically checked (exact rational toy)**이다. 실제 9600-bin 연산자의 새 계산은 하지 않았다. 기존 실제 반환 `RESULT_fullBED.json`, `RESULT_legacy.json`을 읽었으나 이 기여에서 새 endpoint 수치 분석을 실행하지 않았다. 반환 파일의 물리적 승인 여부는 독립 intake 판정에 따른다.

## 1. 범위, 상태, 단위

활성 상태를 (x(t)), 원래 source-electron birth 열을 $b_j\ge0$, 열들의 합을 $b=\sum_jb_j$라 한다. 각 활성 성분은 $U_i=E_iN_i$의 에너지 좌표다. 에너지를 공통 기준으로 나누어 정규화해도 아래 비율은 동일하다. 물리 시간 convention은

\[
\dot x=L_sx,\qquad x(0)=b,\qquad A_s=-L_s,\qquad K(t)=h_s^Tx(t).
\]

$L_s,A_s,h_s$의 rate 단위는 $\mathrm{s}^{-1}$이다. $K$는 에너지/시간, $b,x$는 에너지이며, 정규화 좌표에서는 공통 에너지 기준을 복구하면 된다. $L_s$는 Metzler이고 Hurwitz여야 한다. 전체 ledger generator는 영 고유값을 가지므로 역행렬 대상은 활성 block뿐이다. $b,h_s\ge0$, 직접 source heat 없음, absorbing ledger와 계수의 시간 불변성을 가정한다.

기존 코드의 $G$는 $u=t/T_0$, $T_0=10^{10}\,\mathrm{s}$에 대한 generator다. 따라서

\[
A=-G_{\rm active}=T_0 A_s,\qquad h=G_{{\rm heat},\,\rm active}=T_0h_s.
\]

활성 에너지 block에 대해 이 $A,h$를 쓰면 계산된 시간 moment에 $T_0,T_0^2$를 복구해야 한다. 에너지와 number ledger가 혼재한 전체 $G$의 모든 entry를 무차원이라고 부르면 안 된다. 아래는 주로 물리 시간의 $A_s,h_s$ convention을 쓴다.

총 eventual heat yield와 정규화 heat 지연 분포는

\[
H_0=\int_0^\infty K(t)dt=h_s^TA_s^{-1}b,
\quad f(t)=K(t)/H_0,
\quad F(T)=\int_0^T f(t)dt.
\]

$H_0>0$일 때 $f$는 비음의 정규화 밀도이며, 그 확률변수를 $\tau$라 쓴다. 이는 **eventual heat energy의 발생 지연**을 가중치로 갖는 분포다. 각 electron을 같은 가중치로 센 수명분포가 아니다. 시간 원점은 원래 birth electron의 주입 시점이며 daughter 생성 때 재설정되지 않는다.

실제 반환의 uncapped moment는 고정된 bath·원자계수·source·cutoff·연산자를 $t\to\infty$까지 수학적으로 유지한 값이다. 긴 지연 동안 그 배경이 실제로 고정되는지는 여기서 검사하지 않는다. 이 값을 우주론적 시간에 직접 대응시키거나 새로운 물리 history로 해석하지 않는다.

## 2. 유한 창에서 조기 heat의 raw moment를 정확히 복원

$T>0$, $p=F(T)$,

\[
R=\mathbb E[(1-\tau/T)_+],\qquad
S=\mathbb E[(1-\tau/T)_+^2]
\]

라고 하자. 이 정의의 $R,S$는 동일한 고정 연산자의 선형 ramp 응답으로 얻은 값이다. 선택한 조기 사건은 $E=\{\tau\le T\}$, 후기 사건은 $L=\{\tau>T\}$다. 실제 유한행렬의 연속 heat kernel은 $T>0$에 atom을 갖지 않으므로 endpoint 포함 여부가 값을 바꾸지 않는다. 일반 측도 검산에서는 이 convention을 고정한다.

\[
R=p-\frac{\mathbb E[\tau\mathbf1_E]}T,
\quad
S=p-\frac{2\mathbb E[\tau\mathbf1_E]}T+
\frac{\mathbb E[\tau^2\mathbf1_E]}{T^2}.
\]

따라서 조기 **비조건부 raw moment**는

\[
e_1=\mathbb E[\tau\mathbf1_E]=T(p-R),\qquad
e_2=\mathbb E[\tau^2\mathbf1_E]=T^2(p-2R+S).
\]

이 둘은 각각 $\mathrm{s}$, $\mathrm{s}^2$ 단위다. $p>0$일 때만 조기 조건부 moment를 정의한다.

\[
\mu_E=\frac{e_1}{p}=T\left(1-\frac Rp\right),\qquad
m_{2,E}=\frac{e_2}{p},\qquad
v_E=\frac{e_2}{p}-\mu_E^2
=T^2\frac{pS-R^2}{p^2}.
\]

여기서 $R\neq F(T)$다. $R$는 짧은 지연을 추가로 크게 가중한 heat fraction이다. $p$를 얻으면 앞선 $R,S$만으로 알 수 없었던 조기 conditional moments가 정해진다.

## 3. 후기 heat의 raw·conditional·잔여 시간 moment

uncapped moments를

\[
\mu=\mathbb E[\tau],\qquad m_2=\mathbb E[\tau^2],\qquad v=m_2-\mu^2
\]

로 쓴다. 후기 raw moment는 전체에서 조기를 뺀 값이다.

\[
\ell_1=\mu-T(p-R),\qquad
\ell_2=m_2-T^2(p-2R+S).
\]

$p_L=1-p>0$일 때

\[
\mu_L=\ell_1/p_L,\qquad
m_{2,L}=\ell_2/p_L,\qquad
v_L=m_{2,L}-\mu_L^2.
\]

다음 두 잔여 raw moments는 후기 조건부 moments와 구별해야 한다.

\[
r_1=\mathbb E[(\tau-T)_+]
=\mu-T(1-R),
\]

\[
r_2=\mathbb E[(\tau-T)_+^2]
=m_2-2T\mu+T^2(1-S).
\]

첫 식은 $\tau=\min(\tau,T)+(\tau-T)_+$에서 바로 나오고, 둘째 식은 후기 영역에서 $\tau^2-2T\tau+T^2$를 적분해 위의 $e_1,e_2$를 대입하면 얻는다. 후기 조건부 **앞으로의 잔여 평균**과 분산은

\[
\rho_L=\mathbb E[\tau-T\mid L]=\frac{r_1}{1-p}=\mu_L-T,
\]

\[
v_{\rho,L}=\frac{r_2}{1-p}-\rho_L^2=v_L.
\]

고정 $T$를 빼는 것은 조건부 분산을 바꾸지 않는다. clipped mean $\mu_{\rm clip}=T(1-R)$가 uncapped mean을 얼마나 누르는지는 $r_1=\mu-\mu_{\rm clip}$로 정확히 표현된다. $r_1/\mu$는 uncapped 평균 중 cutoff 뒤에 더 기다리는 시간이 기여하는 비율이며, $1-p$ 자체와 다른 양이다. $\ell_1/\mu$는 전체 지연 평균 중 후기 heat가 기여하는 비율이다. 분모가 영이면 해당 비율을 정의하지 않는다.

## 4. birth 혼합의 올바른 가중치

각 birth 열 $j$가 갖는 eventual heat yield를 $H_{0j}$, 분포를 $F_j$, moments를 $\mu_j,v_j$라 한다. 동일한 공통 정규화의 source 열을 먼저 합해야 한다. 임의로 각 source 열을 단위 에너지나 단위 수로 다시 정규화하면 물리 mixture가 바뀐다.

\[
\pi_j=\frac{H_{0j}}{\sum_kH_{0k}},\qquad
F(t)=\sum_j\pi_j F_j(t).
\]

$\pi_j$는 **eventual heat를 조건으로 본 원래 birth ancestry 비율**이다. 주입 energy 비율 또는 electron number 비율이 아니다. birth별 yield 차이가 가중치를 바꾼다. 특정 birth에 대한 $H_{0j}=0$이면 전체 혼합에서는 가중치 0으로 제외하고 그 열의 conditional moments는 `UNDEFINED_ZERO_HEAT_YIELD`로 둔다.

조기·후기 사건을 조건으로 취하면 Bayes 식으로

\[
\pi_{j\mid E}=\frac{\pi_j F_j(T)}{F(T)},\qquad
\pi_{j\mid L}=\frac{\pi_j[1-F_j(T)]}{1-F(T)}.
\]

전체 평균과 total variance는

\[
\mu=\sum_j\pi_j\mu_j,
\]

\[
v=\underbrace{\sum_j\pi_jv_j}_{W:\,\text{birth 내부 분산}}+
\underbrace{\sum_j\pi_j(\mu_j-\mu)^2}_{B:\,\text{birth 평균 차이}}.
\]

이는 $\tau-\mu=(\tau-\mu_j)+(\mu_j-\mu)$를 제곱하고 birth 조건부 기대값을 취하면 교차항이 사라지는 직접 유도다. 조기·후기 각각에도 같은 공식을 쓰되 가중치와 conditional moments를 함께 바꾼다. 예를 들어

\[
\mu_L=\sum_j\pi_{j\mid L}\mu_{Lj},\qquad
v_L=\sum_j\pi_{j\mid L}\{v_{Lj}+(\mu_{Lj}-\mu_L)^2\}.
\]

$\rho_L$도 $\pi_{j\mid L}$로 혼합된다. 원래 birth별 평균 기여율 $\pi_j\mu_j/\mu$, 2차 moment 기여율 $\pi_jm_{2j}/m_2$, cutoff 뒤 추가 대기 기여율 $\pi_j(1-F_j)\rho_{Lj}/r_1$은 비음이고 각각 합이 1이다. 분모가 양일 때만 사용한다.

현재 ramp heat의 birth posterior는 또 다르다.

\[
\pi_{j\mid\text{ramp power at }T}=\frac{H_{0j}R_j}{\sum_kH_{0k}R_k},\qquad
\pi_{j\mid\text{integrated ramp heat}}=\frac{H_{0j}S_j}{\sum_kH_{0k}S_k}.
\]

그래서 (T(1-S/R))인 **지금 발생하는 ramp heat의 source ancestry 평균**은 eventual pulse heat의 uncapped 평균이나 조기 pulse 평균과 다르다. 순간 pulse heat의 posterior는 $K_j(T)/\sum_kK_k(T)$다. 이 네 가지 conditioning을 하나의 birth 비율로 섞어 쓰면 안 된다.

## 5. adjoint resolvent의 단위와 직접 유도

Hurwitz $L_s$에 대해 $e^{-A_st}\to0$. 부분적분하면

\[
\int_0^\infty t^n e^{-A_st}dt=n!A_s^{-(n+1)},\qquad n=0,1,2.
\]

$n=0$은 $A_s\int e^{-A_st}dt=I$이고, $n\ge1$은 적분의 양 경계항이 사라져 $A_sJ_n=nJ_{n-1}$가 되는 recurrence다. 이로부터

\[
H_n=\int_0^\infty t^nK(t)dt=n!h_s^TA_s^{-(n+1)}b.
\]

이를 transpose solve로 구현한다.

\[
A_s^Tq_0=h_s,\qquad A_s^Tq_1=q_0,\qquad A_s^Tq_2=q_1.
\]

\[
H_0=q_0^Tb,\quad H_1=q_1^Tb,\quad H_2=2q_2^Tb,
\quad \mu=H_1/H_0,\quad m_2=H_2/H_0.
\]

$q_0,q_1,q_2$의 단위는 각각 $1,\mathrm{s},\mathrm{s}^2$다. $q_{0i}$는 단위 활성 energy를 bin $i$에 놓았을 때 생기는 eventual heat energy의 비율이다. loss를 포함한 energy conservation과 비음성까지 가정하면 $0\le q_{0i}\le1$이다. $q_{1i},2q_{2i}$는 그 단위 initial energy로부터 발생할 heat의 비조건부 first·second delay moments이며, 그 bin으로부터의 conditional moments는 $q_{1i}/q_{0i}$, $2q_{2i}/q_{0i}$다.

기존 dimensionless active $A=-G_{\rm active}$, $h=G_{\rm heat,active}$로 계산한 $a_0=A^{-T}h$, $a_1=A^{-T}a_0$, $a_2=A^{-T}a_1$과의 관계는

\[
q_0=a_0,\qquad q_1=T_0a_1,\qquad q_2=T_0^2a_2.
\]

수학적으로 inverse 표기를 써도 구현에서는 sparse triangular solve를 사용한다. 저장된 $G$가 없는 이상 이것은 연산자 재구성 후의 diagnostics 계획이다. 물리 $G$의 construction과 source/state identity의 일치는 별도 실행 gate에 속한다.

## 6. energy bin의 체류 기여와 source ancestry를 분리

활성 energy의 시간 적분을

\[
w=A_s^{-1}b=\int_0^\infty x(t)dt
\]

로 둔다. $w_i$의 단위는 energy×s이다. adjoint relation으로

\[
\sum_iq_{0i}w_i=q_0^TA_s^{-1}b=h_s^TA_s^{-2}b=H_1.
\]

따라서

\[
C_i=\frac{q_{0i}w_i}{H_0}\ge0,\qquad \sum_iC_i=\mu.
\]

이것이 평균 지연에 대한 energy-bin 체류 기여다. $q_0^Tx(t)=\int_t^\infty K(s)ds$이므로, eventual heat를 만들 energy가 시각 (t)에 각 활성 bin에 얼마나 놓여 있는지를 시간 적분한 것이다. 각 $C_i$의 단위는 s다. $C_i/\mu$는 해당 평균 기여율이다.

더 명시적으로, $q_{0i}>0$인 heat-reachable 상태에 제한하고 $D=\operatorname{diag}(q_0)$라 두면, column convention의 변환 $L_H=DL_sD^{-1}$, heat exit rate $(h_H)_i=(h_s)_i/q_{0i}$, initial distribution $Db/H_0$를 갖는 positive absorbing 표현을 구성할 수 있다. $\mathbf1^TL_H=-h_H^T$이고 initial sum이 1이므로 그 표현에서 $C_i$는 heat absorption을 조건으로 한 state occupation time이다. $q_{0i}=0$인 상태에 division을 적용하면 안 된다. 이 표현은 원래 에너지 전달 계의 해석을 돕는 수학적 변환이며 electron branching의 각 daughter를 하나의 입자 경로로 동일시하는 진술이 아니다.

source birth $j$를 유지하면 $w_j=A_s^{-1}b_j$, $C_{ij}=q_{0i}(w_j)_i/H_0$로 birth×residence-bin 표를 만들 수 있다. 합을 birth별로 취하면 $H_{0j}\mu_j/H_0$, bin별로 취하면 $C_i$다. **birth는 원래 injection의 ancestry이고 bin은 이후 지연이 누적된 에너지 상태**다. 고에너지 birth가 eventual heat를 지배해도 대기시간의 큰 몫이 낮은 에너지 bin에서 생길 수 있다. 실제 operator diagnostics 전에는 어느 쪽인지 결정하지 않는다.

실제로 heat가 발생한 bin의 누적 yield는 $h_{si}w_i$이며 $q_{0i}w_i$와 단위부터 다르다. 전자는 energy, 후자는 energy×time이다. 또한 $w_i/E_i$는 electron number occupation에 해당하지만 본 heat-delay 분해의 weight로 대체할 수 없다.

2차 raw moment도 $H_2=2\sum_iq_{1i}w_i$로 비음 분해할 수 있다. 다만 이는 그 bin에 있을 때의 앞으로의 delay reward를 사용한 분해다. $2\sum_iq_{0i}(A_s^{-2}b)_i$도 같은 총합을 갖지만 bin별 값은 다를 수 있다. moment 총합의 대수적 동치를 특정 bin attribution의 유일성으로 바꾸면 안 된다. $C_i$ 역시 parameter sensitivity나 개별 충돌채널의 독립 인과효과를 뜻하지 않는다.

## 7. 저장된 pulse state만으로 tail을 진단하는 식

새 장시간 transport를 수행하지 않고, 이미 저장된 active state $x_T=x(T)$와 동일한 활성 연산자를 쓴다. semigroup 성질로

\[
x(T+s)=e^{-A_ss}x_T.
\]

tail heat와 $T$ 이후 잔여 delay raw moment의 **비정규화 값**은

\[
Q_0=q_0^Tx_T=H_0(1-p),
\quad Q_1=q_1^Tx_T=H_0r_1,
\quad Q_2=2q_2^Tx_T=H_0r_2.
\]

따라서

\[
\ell_1=(TQ_0+Q_1)/H_0,\qquad
\ell_2=(T^2Q_0+2TQ_1+Q_2)/H_0,
\]

\[
\rho_L=Q_1/Q_0,\qquad
v_{\rho,L}=Q_2/Q_0-(Q_1/Q_0)^2.
\]

이 식들과 §2–3의 유한 창 subtraction 식은 같은 해를 다른 방식으로 계산하므로 cancellation 진단에 유용하다. 둘의 일치는 algebraic consistency이며 독립 물리 검증은 아니다. 그 계산에는 정확한 saved energy grid·source columns·pulse state·operator convention을 유지해야 한다.

tail을 bin으로 나누는 두 관점은 구별한다.

| 관측량 | bin별 기여 | 합 | 의미 |
|---|---|---|---|
| tail heat fraction | $q_{0i}x_{Ti}/H_0$ | $1-p$ | $T$에 bin $i$에 남은 energy가 나중에 만들 heat |
| tail 잔여 평균의 frontier 기여 | $q_{1i}x_{Ti}/H_0$ | $r_1$ | $T$에 bin $i$에 있는 energy의 앞으로 대기 기여 |
| tail 잔여 평균의 미래 체류 기여 | $q_{0i}(w_T)_i/H_0$, $w_T=A_s^{-1}x_T$ | $r_1$ | $T$ 이후 bin $i$에서 실제로 누적되는 대기 기여 |
| clipped mean의 체류 기여 | $q_{0i}(w_i-(w_T)_i)/H_0$ | (T(1-R)) | $0\le t\le T$에서 누적된, eventual heat 기준의 대기 |

`frontier`는 $T$ 시각에 남아 있는 상태의 에너지 분포를 뜻한다. 위 두 잔여 평균 분해의 합은 같고 일반적으로 bin별 값은 다르다. 조기 heat만의 $e_1$과 clipped mean도 다르다. clipped mean은 $T$ 뒤에야 발생할 heat가 $T$까지 기다린 시간까지 포함한다. 조건부 tail 기여가 필요하면 위 세 tail 행의 해당 합을 $1-p$로 나눈다. $1-p=0$이면 정의하지 않는다.

## 8. 실수 연산·퇴화 경우·판정의 한계

정확한 양의 kernel에서 필요한 관계는

\[
0\le R\le p\le1,\quad R^2\le pS,\quad S\le R,
\]

\[
0\le\mu_E\le T,\quad v_E\ge0,
\quad r_1,r_2\ge0,\quad r_1^2\le(1-p)r_2.
\]

후기 조건부 평균은 $\mu_L\ge T$, 잔여 평균은 $\rho_L\ge0$이다. 이 관계는 exact model의 necessary consistency다. float64 입력의 불확실성을 둘러싸는 오차한계가 아니며 이 유도 문서는 수치 acceptance tolerance를 새로 정하지 않는다.

- $H_0=0$: heat-normalized 분포와 모든 conditional moment가 미정의다. numerator가 0이라고 평균 0으로 치환하지 않는다.
- $p=0$: 조기 conditional moments가 미정의다. $R=S=0$ 및 early raw moments 0은 exact identity다.
- $p=1$: 후기 conditional moments가 미정의다. exact finite positive transient heat model에서 유한 $T$에 정확히 도달하는지는 별개의 구조적 문제이며 float64의 `1.0`을 물리적인 완전 종료로 단정하지 않는다.
- $q_{0i}=0$, $w_i=0$: bin의 비조건부 기여는 0일 수 있으나 그 bin의 conditional moments는 해당 분모가 양일 때만 정의한다.
- 음의 raw variance, 범위를 벗어난 raw CDF 또는 posterior는 원 값을 보존한다. 자동 clip·renormalization·NaN 대체를 하지 않는다. 분모가 0인 typed `UNDEFINED`와 근거가 모순된 `FAIL/CONCERN`을 구별한다.
- $1-p$, (p-R), (p-2R+S), $\mu-T(1-R)$, $m_2-2T\mu+T^2(1-S)$, 그리고 variance는 상쇄를 겪을 수 있다. source precision의 정보를 더 높은 precision arithmetic이 새로 복구하지 않는다.
- 작은 backward solve residual은 forward error나 물리 오차한계를 자동 보증하지 않는다. adjoint/forward 및 tail-state/subtraction crosscheck는 같은 frozen operator의 algebraic consistency 범위다.

생각해 볼 conditioning 지표는 subtraction의 절대 항 합을 결과 절댓값으로 나눈 값이다. 예를 들어 $r_1$에는 $[|\mu|+|T(1-R)|]/|r_1|$, $r_2$에는 $[|m_2|+2|T\mu|+|T^2(1-S)|]/|r_2|$를 사용할 수 있다. 결과 0인 exact 경우를 무한 conditioning과 섞어 오류로 판정하는 정책은 owner가 따로 정해야 한다.

## 9. 정확 toy가 확인한 범위

`exact_toy.py`는 표준 라이브러리 `Fraction`만 사용한다. 실제 명령은 `EXACT_TOY_RUN_RECEIPT.json`에 보존되어 있다.

1. 구성한 4상태 upper-triangular Metzler/Hurwitz 계에서 직접 쓴 kernel (지수의 $t$는 초 단위 시간 수치값) $K_0(t)=\tfrac12e^{-t}$, $K_1(t)=3e^{-3t}-e^{-4t}$의 적분 moments와 forward·adjoint solve를 비교했다. 개별 spectral coefficient의 음수는 전체 positive kernel의 음수를 뜻하지 않는다.
2. $T=\ln2\,\mathrm{s}$에 대한 analytic state는 유리수이고, tail raw moments는 $T$의 다항식 계수로 정확히 비교했다. `expm`이나 수치 quadrature를 실행하지 않았다.
3. 별도 유한 atom measure로 $T$에 있는 atom까지 포함하는 조기·후기 정의, raw·conditional moments, residual shift, birth posterior 및 total variance를 검산했다. 이 atom measure는 실제 물리 kernel의 새로운 후보가 아니다.
4. tail frontier와 미래 residence의 bin 벡터는 다르지만 합은 같다는 사실을 구체적 반례로 확인했다.

실제 1회 실행에서 63 identities `PASS`, exit 0, wall 0.036199664005835075 s였다. Python 3.12.14를 사용했으며 NCP runtime 인증이 아니다. physical G build 0, physical transport 0, `expm` 0, 새로운 실제 endpoint 분석 0이다. 재실행하지 않았다. 파일 identity는 `THEORY_FILE_IDENTITIES.json`을 참조한다.

## 10. 문헌의 제한된 보조 범위

Bladt, M. and Nielsen, B. F. (2009), *Moment Distributions of Phase Type*, DTU IMM-Technical Report-2009-12, §3, 인쇄 p.3 (PDF의 0-based page 3)의 matrix-exponential density·moment·CDF 공식을 원문으로 확인했다. 이 자료는 §5의 resolvent moment 형태를 보조 지지한다. source ancestry, 특정 energy bin의 체류 해석, bass_cr의 배경 가정이나 장시간 물리적 타당성을 검증하는 자료는 아니다. 이 문서의 유한 창·birth posterior·occupation·saved-tail 식은 위에 제시한 직접 유도에 의존한다.

원문 URL: https://backend.orbit.dtu.dk/ws/files/4616859/tr09_12.pdf

서지 URL: https://orbit.dtu.dk/en/publications/moment-distributions-of-phase-type-3/

도구 retrieval ref: `turn109view0` (parent가 최종 web citation에 쓰려면 직접 open/search 확인 필요). 원문 일부만 읽었으며 전체 논문의 theorem들을 이 프로젝트에 적용했다고 주장하지 않는다. 원문 PDF를 산출물에 재배포하지 않는다.
