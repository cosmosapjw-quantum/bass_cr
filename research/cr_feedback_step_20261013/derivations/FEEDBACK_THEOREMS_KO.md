# 온도·H/He 조성 피드백의 유한 사건 step: 존재, 수렴, 온도 오차

연구 단위: CR-THEORY-FEEDBACK-20261013. 직접 유도 담당: /root/feedback_fixed_point.

근거 상태: 이 문서의 FP1–FP7은 명시된 유한 반응 모형에 대한 직접 유도다. 실행 검산과 독립 심사 상태는 별도 결과 파일에 기록한다. 기존 CR-THEORY-THERMAL-EVOLUTION-20261012의 thermal/all-free 항등식 T.7–T.11, 유한 열적 편입 T.14 및 EOS 오차식 T.18을 재사용한다.

## 1. 상태, 반응, 실제 연속 방정식

한 collision stage에서 공행 셀의 상태를

$$
y=(A_1,\ldots,A_m,H^0,H^+,He^0,He^+,He^{++},N_e,U,R_1,\ldots,R_\ell)^T
\tag{FP.1}
$$

로 둔다. $A_j,N_e$와 원자·이온 성분은 셀의 입자수, $U$는 열적 운동에너지, $R_a$는 중복되지 않는 누적 에너지 장부다. $A_j$의 전자당 에너지는 고정된 $W_j>0$이며 단위는 J다. 계수의 시간은 고유시간이고, 질량작용률에는 실제 부피 $V>0$를 사용한다. 이 collision stage의 에너지·입자수 교환은 고정 사건 열 $S=(s_1,\ldots,s_R)$로 표현한다.

$$
\dot y=G(y,t)=S\,\mathcal R(y,t),\qquad
\mathcal R_r(y,t)\ge0.
\tag{FP.2}
$$

$S_{ir}$의 단위는 상태 $i$의 단위/event이고, $\mathcal R_r$는 events/s다. 핵수, 전하 및 kinetic–chemical–radiative energy를 나타내는 행 $\ell_a^T$는 각각 $\ell_a^TS=0$을 만족한다. 사건 에너지와 charge 정의는 EVENT_STEP_DERIVATION_KO.md의 명세를 따른다.

열적 입자수와 온도는

$$
N(y)=N_{\rm nuc}+N_e,\qquad
N_{\rm nuc}=N_H+N_{He}>0,\qquad
T(y)=\frac{U}{c_vN(y)},\qquad c_v=\frac32k_B
\tag{FP.3}
$$

다. 열적 원자핵은 중성·이온화 상태에 관계없이 각각 한 입자로 세며 active 전자는 $N_e$에 포함하지 않는다. 전체 자유전자 수와 초과에너지를 쓰는 표현에는 기존 T.7–T.11의 정확한 변환을 적용한다.

### 실제 반응률과 frozen donor proposal

정수 차수의 질량작용 모형을

$$
\mathcal R_r(y,t)=
\kappa_r\bigl(T(y),\chi(y),n_e(y,t),t\bigr)
B_r(y,V(t)),
\qquad
B_r(y,V)=V^{1-p_r}\prod_j y_j^{\nu_{jr}},
\quad p_r=\sum_j\nu_{jr}
\tag{FP.4}
$$

로 쓴다. 실제 source·반응 모형에서 다른 비음의 donor factor를 사용하면 그 함수와 미분 상계를 대신 지정한다. $p_r=2$이면 $B_r=y_jy_k/V$이고, $p_r=1$이면 $B_r=y_j$다.

한 step의 초기 상태 $y^n$와 평가 시각 $t_*$를 고정하고, 후보 endpoint $z$에서

$$
f_r(z;y^n)=
\kappa_r\bigl(T(z),\chi(z),n_e(z,t_*),t_*\bigr)
B_r(y^n,V(t_*))
\tag{FP.5}
$$

를 평가한다. H/He fraction과 선택한 electron target density가 계수의 인수에 들어 있으므로, 해당 계수의 조성 의존성이 endpoint와 함께 갱신된다. 예를 들어 $\chi_H=H^+/N_H$, $\chi_{He,1}=He^+/N_{He}$, $\chi_{He,2}=He^{++}/N_{He}$ 및 $n_e=\ell_e^Tz/V(t_*)$를 쓸 수 있다. $N_H=0$ 또는 $N_{He}=0$인 성분군은 관련 fraction과 반응을 함께 생략한다.

다음 일치 조건이 연속 반응계와 이산 step을 연결한다.

$$
\boxed{f_r(y^n;y^n)=\mathcal R_r(y^n,t_*).}
\tag{FP.6}
$$

질량작용의 donor factors는 step 초기값이며, 비선형 계수는 trial endpoint에서 평가한다. 이 선택에 따른 시간 이산화 오차는 §7에서 직접 계산한다.

## 2. 하나의 사건 extent로 모든 저장고를 갱신

$C_{ir}=(-S_{ir})_+$를 사건의 순 소비량으로 정의한다. 초기값이 0인 성분을 순 소비하는 사건은 이 step에서 비활성화한다. 또한 frozen reactant factor가 0인 사건은 계수를 평가하기 전에 $f_r=0$으로 정의한다. 이 규칙은 비음 상태에서 실제 반응률이 존재하며 필요한 reactant가 없으면 그 반응률이 0이라는 조건과 결합한다.

활성 사건에 대해

$$
c_i(z)=\sum_r C_{ir}f_r(z),\qquad
d_r(z)=\sum_{i:C_{ir}>0}\frac{c_i(z)}{y_i^n},
\tag{FP.7}
$$

$$
\xi_r(z)=\frac{h f_r(z)}{1+h d_r(z)},\qquad
\boxed{\Phi_h(z)=y^n+S\xi(z)},\qquad h\ge0
\tag{FP.8}
$$

로 둔다. 비활성 사건의 $\xi_r$는 0이다. $c_i$는 상태 단위/s, $d_r$는 s$^{-1}$이고 $\xi_r$는 사건수다. $U$가 소비되는 사건도 동일한 식에 J/event의 $C_{Ur}$와 초기 에너지 $U^n$를 넣는다. 분모에는 $C_{ir}$의 부호나 단위를 섞는 별도 정규화가 필요하지 않다.

### FP1. 양수성과 선형 불변량

임의의 비음 proposal에 대해 $\Phi_h(z)\ge0$이고, $y_i^n>0$이면

$$
\boxed{
[\Phi_h(z)]_i
\ge
\frac{y_i^n}{1+h c_i(z)/y_i^n}>0.
}
\tag{FP.9}
$$

또한 모든 $\ell_a^TS=0$에 대해 $\ell_a^T\Phi_h(z)=\ell_a^Ty^n$이다.

**증명.** $C_{ir}>0$인 모든 사건은 $d_r\ge c_i/y_i^n$를 만족하므로

$$
\sum_r C_{ir}\xi_r
\le
\frac{h\sum_r C_{ir}f_r}{1+h c_i/y_i^n}
=
\frac{h c_i}{1+h c_i/y_i^n}.
$$

초기 저장량에서 이 소비량을 빼고 생산량을 비음으로 유지하면 (FP.9)를 얻는다. 초기값이 0인 성분에는 활성 사건의 음의 증분이 없으므로 결과는 비음이다. 불변량은 $\ell_a^T\Phi_h=\ell_a^Ty^n+\ell_a^TS\xi$에서 따른다. 따라서 모든 fixed-point iterate가 같은 핵수·전하·에너지 장부를 만족한다. $\square$

이 구조에서 서로 경쟁하는 사건들은 동일한 donor load를 공유한다. 사건 하나의 수·에너지·전하 증분에는 같은 $\xi_r$가 곱해진다.

## 3. 특이한 온도 계수까지 포함하는 계산 가능한 정의역

닫힌 collision stage의 비음 보존집합을

$$
K_0=\{y\ge0:\ell_a^Ty=\ell_a^Ty^n\ \text{for all }a\}
\tag{FP.10}
$$

로 둔다. 각 active 에너지 $W_j>0$, 비음 chemical energy 기준, 비음 radiation 장부 및 고정 핵수에서 $K_0$는 compact convex set이다. 새로운 자유 reservoir가 포함되면 해당 성분에 대한 유한 상계를 따로 넣는다.

초기 총 charge/e를 $Q_0$라 하면

$$
Q_0=H^++He^++2He^{++}-N_e-\sum_jA_j.
$$

따라서

$$
N_{\min}=N_{\rm nuc},\qquad
N_{\max}=N_{\rm nuc}+N_H+2N_{He}-Q_0
\tag{FP.11}
$$

는 열적 입자수의 하한과 상한이다. 유효한 비음 초기 상태에서는 $N_H+2N_{He}-Q_0\ge0$이다. 비음 에너지 기준에서 $0\le U\le E_{\rm tot}$를 쓸 수 있다.

$U^n>0$일 때 다음 고정 온도 구간을 선택한다.

$$
T_{\rm floor}=\frac{U^n}{2c_vN_{\max}}>0,\qquad
T_{\rm ceil}=\frac{E_{\rm tot}}{c_vN_{\min}},
\tag{FP.12}
$$

$$
K=K_0\cap\{c_vT_{\rm floor}N\le U
\le c_vT_{\rm ceil}N\}.
\tag{FP.13}
$$

$N$이 affine linear이므로 $K$도 compact convex이며 $y^n\in K$다. 이 집합에서 각 proposal의 유한 상계 $F_r=\sup_Kf_r$를 계산하고

$$
\overline c_i=\sum_r C_{ir}F_r
\tag{FP.14}
$$

로 둔다.

### FP2. 온도 정의역의 self-map 및 존재

계수들이 $K$에서 연속이고 비음이며

$$
\boxed{h\,\overline c_U\le U^n}
\tag{FP.15}
$$

이면 $\Phi_h(K)\subset K$이고, 적어도 하나의 fixed point $y^\star=\Phi_h(y^\star)$가 $K$에 존재한다. $\overline c_U=0$이면 (FP.15)는 step 크기에 제한을 주지 않는다.

**증명.** FP1과 보존식으로 $\Phi_h(K)\subset K_0$다. FP1에 의해 $U^+\ge U^n/(1+h\overline c_U/U^n)\ge U^n/2$이며, $N^+\le N_{\max}$이므로 $T^+\ge T_{\rm floor}$다. 에너지 상한과 $N^+\ge N_{\min}$은 $T^+\le T_{\rm ceil}$을 준다. 계수의 연속성과 양의 분모에서 $\Phi_h$는 연속이다. 구성한 compact convex $K$의 연속 self-map에 fixed-point 존재 정리를 적용한다. $\square$

보다 일반적인 지정 온도 하한 $T_{\rm low}<U^n/(c_vN_{\max})$에는

$$
h\frac{\overline c_U}{U^n}
\le
\frac{U^n}{c_vN_{\max}T_{\rm low}}-1
\tag{FP.16}
$$

을 사용한다. 이는 온도 domain을 먼저 정하고 그 domain에서 rate bounds를 구한 후 step을 선택하는 순서다.

예를 들어 $\alpha(T)=\alpha_0T^{-p}$, $p>0$에는

$$
\sup_K\alpha\le\alpha_0T_{\rm floor}^{-p},
\qquad
\sup_K|\alpha'|
\le p\alpha_0T_{\rm floor}^{-p-1}
\tag{FP.17}
$$

이라는 유한 상계를 직접 사용한다. $U^n=0$인 시작점에는 $T=0$에서 연속으로 정의된 regular rate family를 사용할 수 있다. 이 경우 $K_0$에서 연속인 모든 계수와 양의 $N_{\min}$에 대해 $\Phi_h:K_0\to K_0$가 성립하며 모든 유한 $h$에 대한 존재가 따른다.

전자밀도 logarithm 같은 추가 양의 정의역도 같은 방법으로 유지한다. 예를 들어 $N_e^n>0$에서 $h\overline c_e\le N_e^n$이면 $N_e^+\ge N_e^n/2$다. 고정 $V_*$에서 $n_e=N_e/V_*$인 경우 $n_e\ge N_e^n/(2V_*)$를 계수 domain에 넣는다. 더 일반적인 양의 electron-count functional에는 그 constituent stock 하한을 합한다.

$B(n)=K n\log(C/\sqrt n)$, $K,C>0$의 경우 $0<n_{\rm lo}\le n\le n_{\rm hi}<C^2$를 선택하면 밀도와 logarithm이 모두 양수다. 이 구간에서 $B'=K[\log(C/\sqrt n)-1/2]$의 끝점 값들로 미분 상계를 계산할 수 있다. $n=0$의 연속 확장과 양의 구간에서의 Lipschitz 상계는 각각 해당 조건에서 사용한다.

## 4. 계수로부터 고정점 수렴상수를 계산

혼합 단위의 상태에는 양의 고정 척도 $a_i$를 선택하고

$$
\|v\|_{\infty,a}=\max_i\frac{|v_i|}{a_i}
\tag{FP.18}
$$

를 사용한다. 입자수 성분의 $a_i$는 입자수, 에너지 성분의 $a_i$는 J다. $|N(z)-N(w)|\le a_N\|z-w\|_{\infty,a}$인 $a_N$를 정한다. 같은 핵수 보존집합에서는 $a_N=a_e$를 사용할 수 있다.

(FP.3)의 차를 직접 취하면

$$
|T(z)-T(w)|
\le L_T\|z-w\|_{\infty,a},\qquad
L_T=\frac{a_U}{c_vN_{\min}}
+\frac{T_{\rm ceil}a_N}{N_{\min}}.
\tag{FP.19}
$$

fraction 및 density의 예는

$$
L_{\chi_H}=\frac{a_{H^+}}{N_H},\qquad
L_{\chi_{He,1}}=\frac{a_{He^+}}{N_{He}},\qquad
L_{n_e}=\frac{\sum_i|\ell_{e,i}|a_i}{V_*}.
\tag{FP.20}
$$

$\partial_{\phi_\alpha}\kappa_r$의 절댓값 상계를 $K_{r\alpha}$, descriptor의 Lipschitz 상계를 $L_\alpha$, 초기 donor factor를 $b_r=B_r(y^n,V_*)$라 하면

$$
F_r=b_r\overline\kappa_r,\qquad
L_r=b_r\sum_\alpha K_{r\alpha}L_\alpha
\tag{FP.21}
$$

가 $f_r$의 supremum 및 Lipschitz 상계다. Piecewise differentiable 계수는 같은 구간에서의 Lipschitz 상계를 직접 제공해도 된다.

load와 denominator의 상계는

$$
L_{c_i}=\sum_r C_{ir}L_r,\qquad
D_r=\sum_{i:C_{ir}>0}\frac{L_{c_i}}{y_i^n}.
\tag{FP.22}
$$

초기 support는 이 fixed-point solve 동안 고정되어 있으므로, 0인 denominator를 평가하는 항은 없다. $m_r=1+h\inf_Kd_r\ge1$로 두면

$$
|\xi_r(z)-\xi_r(w)|
\le
M_r\|z-w\|_{\infty,a},
\qquad
M_r=\frac{hL_r}{m_r}
+\frac{h^2F_rD_r}{m_r^2}.
\tag{FP.23}
$$

**유도.** $h f(z)/(1+hd(z))-h f(w)/(1+hd(w))$에서 먼저 numerator 차를 떼고 다음에 inverse denominator 차를 뗀다. 첫 항은 $h|\delta f|/m_r$, 둘째는 $h^2F_r|\delta d|/m_r^2$ 이하이다.

### FP3. 유일한 자기일관 endpoint와 Picard 수렴

정의역 FP2의 조건과

$$
\boxed{
q=\max_i\frac1{a_i}\sum_r|S_{ir}|M_r<1
}
\tag{FP.24}
$$

을 만족하면, $K$의 fixed point는 유일하다. 임의의 $z_0\in K$에 대해 $z_{k+1}=\Phi_h(z_k)$는 이 점으로 수렴하고

$$
\|z_k-y^\star\|_{\infty,a}
\le q^k\|z_0-y^\star\|_{\infty,a}.
\tag{FP.25}
$$

**증명.** (FP.23)을 $S\xi$에 적용하면 $\|\Phi_h(z)-\Phi_h(w)\|_{\infty,a}\le q\|z-w\|_{\infty,a}$다. 반복 차이는 기하급수적으로 감소하므로 반복열은 완비 집합 $K$에서 Cauchy다. 연속성으로 극한은 fixed point이며, 두 fixed point 사이의 거리는 자기 자신의 $q$배 이하이므로 0이다. FP1은 모든 반복에서 물리 장부를 보존한다. $\square$

$m_r=1$의 간단한 상계로도 step을 사전에 고를 수 있다. 다음 상수들을 계산한다.

$$
A=\max_i a_i^{-1}\sum_r|S_{ir}|L_r,\qquad
B=\max_i a_i^{-1}\sum_r|S_{ir}|F_rD_r.
\tag{FP.26}
$$

그러면 $q\le hA+h^2B$다. 목표 $0<q_{\rm target}<1$에 대해 $B>0$이면

$$
\boxed{
h\le h_{\rm ctr}
=\frac{2q_{\rm target}}
{A+\sqrt{A^2+4Bq_{\rm target}}}
}
\tag{FP.27}
$$

가 충분하다. $B=0,A>0$이면 $h_{\rm ctr}=q_{\rm target}/A$, $A=B=0$이면 수렴 상수는 0이다. 실제 step은 (FP.15)의 domain 조건과 (FP.27)를 함께 만족하도록 선택한다. 양의 $m_r$를 이용하거나 독립적인 extent 좌표에서 미분하면 더 작은 $q$를 얻을 수 있다.

## 5. 반복 중단 오차와 계수 근사 오차를 온도로 전달

### FP4. 자기일관성 residual의 사후 상계

$z\in K$에서 같은 map의 residual을

$$
\rho(z)=\|\Phi_h(z)-z\|_{\infty,a}
$$

로 측정하면

$$
\boxed{
\|y^\star-z\|_{\infty,a}
\le\frac{\rho(z)}{1-q}.
}
\tag{FP.28}
$$

**증명.** $\|y^\star-z\|\le\|\Phi_h(y^\star)-\Phi_h(z)\|+\|\Phi_h(z)-z\|
\le q\|y^\star-z\|+\rho(z)$를 정리한다. $\square$

실제 iterate 차이 $d_k=\|z_{k+1}-z_k\|$를 쓸 때 $z_k$의 오차는 $d_k/(1-q)$, 새 상태 $z_{k+1}$의 오차는 $q\,d_k/(1-q)$ 이하이다. map 평가에 별도 상계 $\varepsilon_{\rm eval}$이 있으면 측정 residual에 이를 더한다.

기존 EOS 오차 항등식 T.18에 의해

$$
\boxed{
|T(y^\star)-T(z)|
\le
\left[
\frac{a_U}{c_vN_{\min}}
+\frac{T(z)a_N}{N_{\min}}
\right]
\frac{\rho(z)+\varepsilon_{\rm eval}}{1-q}.
}
\tag{FP.29}
$$

이 상계의 대상은 명시한 이산 fixed-point 문제의 정확한 endpoint이다.

### 계수 재사용을 포함한 map perturbation

같은 $y^n,S,h$와 support를 사용하는 두 proposal $f,\widehat f$가 $K$ 전체에서 $|f_r-\widehat f_r|\le e_r$를 만족한다고 하자. 두 proposal의 공통 상계 $F_r$와 공통 denominator 하한 $m_r$를 사용해

$$
e_{c_i}=\sum_rC_{ir}e_r,\qquad
e_{d_r}=\sum_{i:C_{ir}>0}\frac{e_{c_i}}{y_i^n},
$$

$$
e_{\xi_r}=\frac{h e_r}{m_r}
+\frac{h^2F_re_{d_r}}{m_r^2},\qquad
E_{\rm map}=\max_i a_i^{-1}\sum_r|S_{ir}|e_{\xi_r}
\tag{FP.30}
$$

로 둔다. 정확한 $\Phi_h$의 수렴 상수가 $q<1$이고 $z\in K$의 계산 residual이 $\widehat\rho=\|\widehat\Phi_h(z)-z\|$이면

$$
\|y^\star-z\|_{\infty,a}
\le\frac{\widehat\rho+E_{\rm map}+\varepsilon_{\rm eval}}{1-q}.
\tag{FP.31}
$$

증명은 (FP.23)의 분수 차 공식과 (FP.28)의 삼각부등식에 따른다. 이 값에 (FP.29)의 EOS 계수를 곱하면 approximate rate table·공통 충돌 계수 재사용의 온도 허용오차를 평가할 수 있다.

## 6. 실제 연속 반응계의 상수도 coefficient 자료로 계산

$0\le y_j\le M_j$와 $V\ge V_{\min}>0$인 domain에서 정수 질량작용 factor에는

$$
\overline B_r
=
V_{\min}^{1-p_r}\prod_j M_j^{\nu_{jr}}
\qquad (p_r\ge1),
$$

$$
L_{B_r}
\le
V_{\min}^{1-p_r}
\sum_{j:\nu_{jr}>0}
\nu_{jr}a_j M_j^{\nu_{jr}-1}
\prod_{k\ne j}M_k^{\nu_{kr}}
\tag{FP.32}
$$

를 사용할 수 있다. $\nu=1$의 미분은 경계 $y_j=0$에서도 유한하다. 따라서 실제 반응률의 상태 Lipschitz 상계는

$$
L_{\mathcal R_r}
\le
\overline B_r\sum_\alpha K_{r\alpha}L_\alpha
+\overline\kappa_r L_{B_r},
\qquad
L_G=\max_i a_i^{-1}\sum_r|S_{ir}|L_{\mathcal R_r}.
\tag{FP.33}
$$

속도 상계 $M_G=\max_i a_i^{-1}\sum_r|S_{ir}|\overline{\mathcal R}_r$도 같은 계수에서 구한다. prescribed $V(t)$의 시간 의존성은 $\partial_tB_r=(1-p_r)(\dot V/V)B_r$와 fixed-state descriptor의 시간 미분을 사용해 $|\partial_t\mathcal R_r|$ 및 $L_{G,t}$로 전달한다.

양의 온도 구간에서 실제 ODE 경로까지 같은 domain에 머무르게 하는 충분조건을 별도로 계산할 수 있다. $\overline c_U^{\rm phys}=\sum_r C_{Ur}\sup_K\mathcal R_r$에 대해

$$
\boxed{
h\,\overline c_U^{\rm phys}\le U^n/2
}
\tag{FP.34}
$$

이면, 첫 이탈 시각까지 $\dot U\ge-\overline c_U^{\rm phys}$를 적분하여 $U(t)\ge U^n/2$를 얻는다. 핵수와 에너지 불변량 및 quasipositivity를 함께 사용하면 실제 경로도 (FP.12)의 온도 domain에 남는다. 추가 density floor에는 해당 소비율의 같은 조건을 적용한다. 실제 반응률이 domain의 열린 근방에서 locally Lipschitz라는 조건 아래 이 argument는 유일한 연속 반응해의 해당 짧은 구간을 구성한다.

## 7. Frozen donor와 capacity factor의 시간 일관성

### FP5. 실제 반응 ODE에 대한 일차 일관성

유한 coefficient bounds, locally Lipschitz 실제 반응률, (FP.6)을 가정한다. $t_*=t_n+\vartheta h$, $0\le\vartheta\le1$이고, 초기 support 규칙이 $\mathcal R_r(y^n,t_*)=0$인 사건만 비활성화하면

$$
y^\star
=
y^n+hG(y^n,t_n)+O(h^2)
\tag{FP.35}
$$

다. 실제 ODE의 endpoint와 한 step 차이는 $O(h^2)$다.

**증명과 계산 가능한 나머지.** 다음 상수들을 두자.

$$
\overline d_r=\sum_{i:C_{ir}>0}\frac{\overline c_i}{y_i^n},\quad
M_f=\max_i a_i^{-1}\sum_r|S_{ir}|F_r,
$$

$$
L_f^S=\max_i a_i^{-1}\sum_r|S_{ir}|L_r,\qquad
C_{\rm cap}=\max_i a_i^{-1}\sum_r|S_{ir}|F_r\overline d_r .
$$

$\xi_r\le hF_r$이므로 $\|y^\star-y^n\|\le hM_f$다. 또한

$$
\left|
\frac{hf_r(y^\star)}{1+hd_r(y^\star)}
-hf_r(y^n)
\right|
\le
hL_r\|y^\star-y^n\|+h^2F_r\overline d_r.
$$

이를 $S$에 적용하고 (FP.6) 및 시간 Lipschitz 상계를 넣으면

$$
\|y^\star-y^n-hG(y^n,t_n)\|
\le
h^2\bigl(L_f^S M_f+C_{\rm cap}
+\vartheta L_{G,t}\bigr).
\tag{FP.36}
$$

한편 실제 경로에서는 $\|y(t_n+s)-y^n\|\le sM_G$이므로

$$
\|y(t_n+h)-y^n-hG(y^n,t_n)\|
\le
\frac{h^2}{2}(L_GM_G+L_{G,t}).
\tag{FP.37}
$$

두 나머지를 합하면 명시적인 한 step $O(h^2)$ 상계를 얻는다. $\square$

초기에 0인 donor가 다른 사건으로 $O(h)$만큼 생성되는 경우, 그 donor를 요구하는 반응률은 Lipschitz 조건에서 $O(h)$이고 해당 step의 실제 추가 extent는 $O(h^2)$다. 따라서 초기 support를 고정한 처리가 (FP.35)의 일차 일관성을 유지한다. 다음 step에서는 새 초기 상태로 support를 다시 구성한다.

고정 양의 donor를 중심으로 한 상수들은 $1/y_i^n$를 포함한다. 0인 donor에는 위의 별도 branch를 사용한다. 경계에 임의로 가까운 모든 초기 상태에 걸친 균일 시간 오차 상계를 사용하려면 physical donor factors에 의한 cancellation 또는 추가 양의 초기 하한을 계산한다.

## 8. 실제 endpoint defect에서 물리적 온도 오차로 가는 증명

(FP.28)은 반복 중단의 오차다. 실제 반응 ODE와의 차이에는 frozen factors, capacity denominator 및 시간 변화의 효과를 함께 넣어야 한다. 이를 실제 연속 vector field에 대한 endpoint defect 하나로 평가할 수 있다.

### FP6. 선형 경로 재구성의 endpoint certificate

$h>0$, $z\in K$를 계산된 endpoint라 하자. 같은 initial state에서

$$
\eta(s)=y^n+\frac{s}{h}(z-y^n),\qquad 0\le s\le h
\tag{FP.38}
$$

를 구성한다. $K$가 convex이므로 이 경로는 $K$ 안에 있다. 실제 ODE 경로도 $K$ 안에 있고 $G$의 상태·시간 Lipschitz 상계가 $L_G,L_{G,t}$라고 하자. 실제 endpoint defect를

$$
\boxed{
D_{\rm end}
=
\left\|
\frac{z-y^n}{h}-G(z,t_n+h)
\right\|_{\infty,a}
}
\tag{FP.39}
$$

로 정의한다. 다음 함수를 연속적으로 정의한다.

$$
A(L,h)=
\begin{cases}
(e^{Lh}-1)/L,&L>0,\\
h,&L=0,
\end{cases}
$$

$$
B(L,h)=
\begin{cases}
\bigl[(Lh-1)e^{Lh}+1\bigr]/L^2,&L>0,\\
h^2/2,&L=0 .
\end{cases}
\tag{FP.40}
$$

그러면

$$
\boxed{
\|y(t_n+h)-z\|_{\infty,a}
\le
A(L_G,h)D_{\rm end}
+
B(L_G,h)
\left(
L_G\frac{\|z-y^n\|_{\infty,a}}h+L_{G,t}
\right).
}
\tag{FP.41}
$$

초기 상태에도 오차 $e_0$가 있으면 우변에 $e^{L_Gh}e_0$를 더한다.

**증명.** 재구성 경로의 residual은 $d(s)=\dot\eta(s)-G(\eta(s),t_n+s)$다. (FP.39)에 endpoint와의 상태·시간 차를 더하면

$$
\|d(s)\|
\le D_{\rm end}
+(h-s)
\left[
L_G\frac{\|z-y^n\|}h+L_{G,t}
\right].
$$

실제 해와 재구성의 차이는
$\|e(h)\|\le e^{L_Gh}\|e(0)\|+\int_0^h e^{L_G(h-s)}\|d(s)\|ds$를 만족한다. 두 적분은 각각 $A(L_G,h)$와
$\int_0^h e^{L_G(h-s)}(h-s)ds=B(L_G,h)$다. $\square$

$B$의 안전한 단순 상계 $B(L,h)\le e^{Lh}h^2/2$도 쓸 수 있다. 작은 $Lh$의 계산에는 exponential의 작은 차를 안정적으로 평가하거나 $B=h^2[1/2+(Lh)/3+(Lh)^2/8+\cdots]$를 사용한다.

(FP.41)의 우변을 $E_{\rm phys}$라 하면

$$
\boxed{
|T_{\rm true}(t_n+h)-T(z)|
\le
\left[
\frac{a_U}{c_vN_{\min}}
+\frac{T(z)a_N}{N_{\min}}
\right]E_{\rm phys}.
}
\tag{FP.42}
$$

이 endpoint certificate에는 실제 vector field를 평가하는 한 계산 endpoint의 미완료 iteration과 시간 이산화가 모두 포함된다. 별도의 rate approximation이 실제 vector field 평가에 남으면 그 평가 오차를 (FP.39) 또는 경로 residual 상계에 더한다.

## 9. Prescribed expansion과의 연결

이 문서의 finite step은 고정 사건 열을 사용하는 collision substep이다. 동일한 prescribed 부피 이력의 순수 열적 geometric substep에는 기존 T.15에서

$$
U^+=\gamma U^-,\qquad N^+=N^-,\qquad
\gamma=\left[\frac{V^+}{V^-}\right]^{-2/3}>0
\tag{FP.43}
$$

를 쓴다. 따라서 두 collision endpoint 사이의 온도 오차는 이 후속 substep에서 정확히 $\gamma$배가 된다. 이 단계의 thermal pressure work는 $U^--U^+$로 동일 장부에 넣는다.

실제 collision–geometry 결합의 시간 이산화에는 선택한 splitting 또는 전체 재구성의 residual을 사용한다. (FP.41)을 전체 bounded finite vector field에 적용할 경우에는 geometric 항과 그 시간 의존성을 $G,L_G,L_{G,t}$에 함께 넣는다. Active 전자의 비등방 압력 일은 기존 모멘트 계약을 따르며 thermal scalar 식으로 치환하지 않는다.

## 10. FP7: 전하 중성인 정확한 비선형 feedback 구성 사례

단위 에너지 $E_0>0$와 rate scale $\kappa_0>0$를 선택한다. 사건

$$
A(4E_0)+H^0\longrightarrow H^++2e_{\rm th},
\qquad \Delta U=3E_0
\tag{FP.44}
$$

는 ionization energy $I_H=E_0$와 함께 에너지를 보존한다. 사건 열을 $(A,H^0,H^+,N_e,U/E_0)$ 좌표에서 $s=(-1,-1,1,2,3)^T$로 쓰고

$$
y^n=(1,1,1,0,1)^T
\tag{FP.45}
$$

에서 시작한다. 총 핵수는 2, charge/e는 0, 총 에너지는 $6E_0$다.

Extent $x$에 따라 $y(x)=(1-x,1-x,1+x,2x,1+3x)$이며

$$
\vartheta(x)\equiv\frac{c_vT}{E_0}
=\frac{1+3x}{2+2x},\qquad
\chi_H(x)=\frac{1+x}{2}.
\tag{FP.46}
$$

계수를 $\kappa=\kappa_0(1+\vartheta)\,2\chi_H$로 정하고 초기 donor factor를 1로 정규화하면

$$
\frac{f(x)}{\kappa_0}
=(1+\vartheta)(1+x)
=F(x)=\frac{3+5x}{2}.
\tag{FP.47}
$$

온도와 이온화 fraction이 모두 갱신되는 regular coefficient family다. 두 소비 donor의 초기량은 각각 1이므로 $d=2f$이고

$$
\psi_\eta(x)=\frac{\eta F(x)}{1+2\eta F(x)},
\qquad \eta=h\kappa_0 .
\tag{FP.48}
$$

$0\le x\le1$에서 $\psi_\eta(x)\in[0,1/2)$이며

$$
0\le\psi_\eta'(x)
\le
q(\eta)=\frac{5\eta/2}{(1+3\eta)^2}
\le \frac5{24}<1.
\tag{FP.49}
$$

마지막 최대는 $\eta=1/3$에서 얻는다. 따라서 모든 유한 $\eta\ge0$에서 이 scalar domain의 자기일관 endpoint는 유일하고 Picard 반복이 수렴한다.

$\eta=4/17$에서는

$$
\boxed{
x^\star=\frac14,\quad
\vartheta^\star=\frac7{10},\quad
y^\star=(3/4,3/4,5/4,1/2,7/4)^T,\quad
q=\frac{170}{841}.
}
\tag{FP.50}
$$

직접 대입으로 $\eta F(x^\star)=1/2$ 및 $\psi_\eta(x^\star)=1/4$를 확인한다. 최종 에너지는 $4(3/4)+(5/4)+(7/4)=6$ 단위 $E_0$, 전하는 $5/4-1/2-3/4=0$이다.

실제 donor factors를 갱신하는 연속 ODE의 extent rate는

$$
\mathcal R(x)=\kappa_0F(x)(1-x)^2 .
$$

같은 endpoint에서

$$
\boxed{
\frac{x^\star}{h}-\mathcal R(x^\star)
=
\frac{17}{16}\kappa_0-\frac{153}{128}\kappa_0
=
-\frac{17}{128}\kappa_0.
}
\tag{FP.51}
$$

따라서 이 예는 exact discrete self-consistency, 물리 장부, 실제 time-discretization residual을 각각 정확한 유리수로 판별한다. 온도 미분은 $\vartheta'(x)=1/(1+x)^2$이므로 $|\delta\vartheta|\le|\delta x|$이며 (FP.28)에서 직접 온도 반복 중단 기준을 얻는다.

## 11. 계산 계약과 다음 연결

이번 finite-step 구성의 계산 입력은 고정 $S$, 불변량 행, 비음 초기 state, 실제 부피와 고유시간 step, coefficient evaluator, 온도·밀도 domain, $F_r,L_r$ 또는 더 날카로운 직접 Jacobian 상계다. 출력은 하나의 common extent vector, 모든 저장고의 endpoint, capacity 하한, 반복 residual, 선택된 $q$ 및 온도 certificate다.

근거의 대상은 다음과 같이 대응한다.

| 입력 또는 검사 | 결론 |
|---|---|
| $\ell_a^TS=0$와 shared extents | 각 iterate의 핵수·전하·에너지 보존 |
| Capacity 식 FP.7–FP.9 | 각 iterate의 비음성과 양의 초기 donor 보유량 |
| Domain bounds FP.12–FP.16 | 온도 특이점을 피한 자기일관 coefficient 평가 |
| 계산된 $q<1$ | 선언한 domain의 유일한 이산 endpoint 및 Picard 수렴 |
| Map residual $\rho$ | 이산 자기일관 endpoint까지의 오차 |
| Endpoint physical defect $D_{\rm end}$ | 실제 연속 반응계 endpoint까지의 오차 |
| 기존 EOS 항등식 T.18 | 상태·수·에너지 오차의 온도 전달 |

실제 BASS_CR의 큰 전자 격자에는 이미 존재하는 사건 분해와 energy-resolved atomic data를 이 고정-column 계약에 연결할 수 있다. 이번 이론에서 다음으로 필요한 자료는 선택할 coefficient interpolation의 domain과 미분 상계, 보존 분해의 해당 사건 열, 그리고 실제 receiver의 온도 허용오차다. 이 자료의 수치 선택에 앞서 FP1–FP7의 유도와 구성은 위 가정 아래에서 완결된다.

