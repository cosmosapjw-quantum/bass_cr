# 시간 변화 배경에서 열적 전자와 모든 자유전자의 회계를 연결하는 구성

단위: CR-THEORY-THERMAL-EVOLUTION-20261012. 이 문서는 R3–R5의 후보 유도다.
직전 CR-RUX-M1B-SOURCE-BINDING-20261012의 cutoff 편입 A2에서 출발하여,
그 DERIVATION_KO.md §6.4에 남은 all-free 기준에너지와 primary birth 회계를 닫는다.
이전 source/result는 inputs/RECOVERY.json 및 inputs/prior/에 결속했다.

## 1. 가정, 상태, 단위

- **T1 기하와 기준계.** 주어진 Bianchi I 배경의 comoving geodesic cell을 쓴다.
  고유시간은 $t$, 물리 부피는 $V(t)>0$, $\theta=\dot V/V$다.
  국소 직교기저의 팽창 텐서는 $K=H I+\sigma$, $\theta=3H$, $\mathrm{tr}\sigma=0$이다.
  공간 수송과 전자기장 일을 생략한 부분계다. 분포와 source의 운동량 반전 대칭으로 순 운동량은 0이며,
  방향 비등방성은 허용한다.
- **T2 열적 closure.** nuclei와 thermal electrons는 공통 온도 $T$의 비상대론적 단원자 이상기체다.
  각 nucleus는 ionization stage와 관계없이 한 입자로 센다.
  $n_{\rm th}=n_H+n_{\rm He}+n_{e,\rm th}>0$,
  $e(T)=c_vT$, $c_v=3k_B/2$, $u_{\rm th}=e(T)n_{\rm th}$,
  $p_{\rm th}=k_BTn_{\rm th}$다. 화학 결합·여기 에너지는 별도 장부에 둔다.
- **T3 비열적 상태.** $g(W,\Omega,t)$는 물리 부피·kinetic energy·solid angle당 전자수다.
  active 구간 $A=\{W>E_c(t)>0\}$에서
  $n_A=\int_Ag$, $u_A=\int_AWg$, $\Pi_{A,ij}=\int_Ap_iv_jg$다.
  여기서는 kinetic energy $W$에 SI joule를 사용한다.
  eV 자료에는 $\epsilon_{\rm eV}=1.602176634\times10^{-19}$ J/eV를 한 번 적용한다.
- **T4 교환 회계.** $J_N,J_E$는 active에서 thermal로 향할 때 양인 순 입자수·에너지 전달률이다.
  $P_h$는 active의 연속 stopping 및 채택한 jump의 직접 열 전달이 thermal bath에 주는 총 열이다.
  경계 drift, jump, subcutoff daughter를 각 실제 수·에너지로 센다.
  kinetic low partition의 정확한 항등식과 이를 T2의 bath로 편입하는 closure를 구분한다.
- **T5 외부 source.** $S_A,Q_A$는 active로 직접 들어오는 전자 birth의 수·kinetic energy source,
  $S_d,Q_d$는 thermal sector의 직접 source다.
  $S_{\rm sec}$는 active collision이 추가하는 총 자유전자수,
  $L\ge0$는 같은 collision에서 chemical/excitation/radiative ledger로 빠지는 kinetic energy다.
  재결합·추가 가열·냉각을 사용할 때는 수·에너지 항을 함께 명시한다.

밀도 $y$의 comoving balance 연산자는

$$
\mathcal D y=\dot y+\theta y=V^{-1}\frac{d(Vy)}{dt}.
\tag{T.1}
$$

이는 온도의 미분 $\dot T$와 구별된다.
$\Pi_A$는 J m$^{-3}$, $K:\Pi_A$, $J_E$, $P_h$는 J m$^{-3}$ s$^{-1}$,
$J_N$는 m$^{-3}$ s$^{-1}$이다.
일반 비균질 배경에서는 공간 flux divergence와 frame acceleration 항을 추가한다.
모멘트법의 배경은 Sarbach–Zannias (2013), Bianchi I의 momentum measure는
Lee–Nungesser (2017/2018)를 참조한다. 아래 식은 주어진 모멘트 방정식에서 직접 유도한다.

## 2. 두 부문의 입자수와 kinetic energy 방정식

active collision 한 사건의 parent 에너지를 $W$, 모든 전자 daughter의 에너지를 $W_r$라 두자.
$W-\sum_rW_r$는 매질로 향하는 총 energy debit이다. 이를 채택한 직접 jump heat와
chemical/excitation/radiative 항 $L$로 분배한다.
daughter 수에서 parent 수를 뺀 값은 secondary birth다.
subcutoff daughter를 thermal로 편입할 때 실제 $W_r$를 $J_E$에, 하나씩 $J_N$에 넣는다.
동일 사건을 중복 계상하지 않는 모멘트 회계는

$$
\begin{aligned}
\mathcal D n_A &= S_A+S_{\rm sec}-J_N,\\
\mathcal D n_{\rm th} &= S_d+J_N,\\
\mathcal D u_A+K:\Pi_A &= Q_A-L-P_h-J_E,\\
\mathcal D u_{\rm th}+\theta p_{\rm th} &= Q_d+P_h+J_E.
\end{aligned}
\tag{T.2}
$$

원 jump collision integral을 active 모멘트에 사용하는 구현에서는 $L,J_E,S_{\rm sec},J_N$가
그 integral의 항등적 분해다. 원 integral에 이 항들을 다시 더하지 않는다.
직접 subcutoff source는 $Q_d,S_d$에 넣거나 전체 source와 편입 장부에 넣는 한 가지 방법을 택한다.
직전 저장 cutoff derivative에는 source ghost가 이미 포함되어 있으므로 그 저장 총량을 사용할 때
같은 direct source를 추가하지 않는다.

$$
n_{\rm all}=n_{\rm th}+n_A,\qquad u_{\rm kin}=u_{\rm th}+u_A
\tag{T.3}
$$

로 두고 합하면 모든 내부 전달이 소거된다.

$$
\boxed{\mathcal D n_{\rm all}=S_{\rm all}:=S_A+S_d+S_{\rm sec}},
\tag{T.4}
$$

$$
\boxed{\mathcal D u_{\rm kin}
+K:(p_{\rm th}I+\Pi_A)=Q_{\rm kin}:=Q_A+Q_d-L}.
\tag{T.5}
$$

$Q_A$는 직전 PHYS02에서 전자로 직접 태어난 kinetic energy source다.
primary proton collision의 binding 비용은 해당 proton/chemical ledger에 연결한다.
이미 kinetic energy만 나타내는 $Q_A$에서 그 비용을 한 번 더 빼지 않는다.
secondary ionization의 $L$과 primary birth를 일으킨 외부 source의 화학 비용은 서로 다른 사건 장부다.
proton까지 포함한 전체 에너지 법칙에는 proton의 energy debit과 chemical reservoir를 합한다.

thermal 에너지식에 $u_{\rm th}=c_vn_{\rm th}T$와 수 방정식을 대입하면

$$
\boxed{c_vn_{\rm th}\dot T+k_Bn_{\rm th}T\theta
=Q_d+P_h+J_E-e(T)(S_d+J_N)}.
\tag{T.6}
$$

새 입자에 기존 온도의 평균 에너지 $e(T)$를 배정한 뒤의 에너지 차가 온도 변화에 기여한다.
입자수 source는 열 source와 함께 진화한다.

## 3. all-free 표현을 완결하는 상태변수

모든 자유전자를 세는 receiver에 다음 변수와 tensor를 둔다.

$$
\boxed{u_{\rm ex}:=u_A-e(T)n_A},\qquad
\boxed{\Pi_{\rm ex}:=\Pi_A-k_BTn_AI}.
\tag{T.7}
$$

$u_{\rm ex}$는 active kinetic energy에서 동일 전자수의 thermal 기준에너지를 뺀 값이다.
그 부호는 정의로 고정되지 않는다. passive energy norm은 $u_A$와 양의 에너지 장부에 적용한다.

### 정리 T-A: 열적 회계와 all-free 회계의 정확한 동치

T1–T5 아래에서 $n_{\rm th}=n_{\rm all}-n_A>0$일 때

$$
u_{\rm kin}=e(T)n_{\rm all}+u_{\rm ex},\qquad
\Pi_{\rm kin}=k_BTn_{\rm all}I+\Pi_{\rm ex}.
\tag{T.8}
$$

식 (T.4)–(T.5)는 다음 all-free 온도식과 동치다.

$$
\boxed{
c_vn_{\rm all}\dot T
=Q_{\rm kin}-\mathcal D u_{\rm ex}
-k_BTn_{\rm all}\theta-K:\Pi_{\rm ex}-e(T)S_{\rm all}.
}
\tag{T.9}
$$

**증명.** (T.7)을 (T.3)에 대입하면 (T.8)이 따른다.
곱의 미분으로 $\mathcal D[e(T)n_{\rm all}]
=c_vn_{\rm all}\dot T+e(T)S_{\rm all}$이다.
이를 총 kinetic energy 식 (T.5)에 대입하고 압력을 (T.8)로 바꾸면 (T.9)가 된다.
역대입하면 원 총에너지식이 회복된다. $\square$

이로써 직전 §6.4에 필요한 active 기준에너지와 primary birth 회계가 정해진다.
새 source를 thermal 기준의 총 입자수에 넣을 때 생기는 $-e(T)S_{\rm all}$과
active 기준에너지 변화가 같은 식에서 처리된다.

### 미분 결합과 유효 열용량

계산에 필요한 곱의 미분은

$$
\boxed{\mathcal D u_{\rm ex}
=\mathcal D u_A-e(T)\mathcal D n_A-c_vn_A\dot T.}
\tag{T.10}
$$

이를 (T.9)에 넣고
$S_{\rm all}-\mathcal Dn_A=S_d+J_N$ 및 (T.2)를 쓰면

$$
c_v(n_{\rm all}-n_A)\dot T
=Q_d+P_h+J_E-k_BTn_{\rm th}\theta-e(T)(S_d+J_N),
\tag{T.11}
$$

즉 (T.6)이 정확히 돌아온다.
$u_{\rm ex}$의 미분을 독립된 수로 고정하면 이 열용량 결합을 잃는다.
구현은 (T.6)을 직접 풀거나 (T.9)–(T.10)의 선형 결합을 풀어 같은 결과를 얻는다.
$u_{\rm ex}$를 별도 상태로 보관하더라도 (T.7)의 제약을 지킨다.
간결한 상태는 $(n_{\rm all},T,\text{active state})$이며 $n_A,u_A,u_{\rm ex}$를 여기서 평가한다.

## 4. pressure work와 cutoff의 의미

$M=m_ec^2$라 두면 상대론적 kinetic energy의 운동량·속도 곱은

$$
p(W)v(W)=\frac{W(W+2M)}{W+M}.
\tag{T.12}
$$

$\Pi_A=\int[pv]\Omega\Omega^Tg$이고,
$W\ll M$에서는 $pv\to2W$, $W\gg M$에서는 $pv\to W$다.
$K:\Pi_A=H\,\mathrm{tr}\Pi_A+\sigma:\Pi_A$로 비등방 압력 일을 보존한다.
등방·비상대론적 active 분포일 때 $\Pi_A=(2u_A/3)I$로 줄인다.

cutoff를 바꾸는 순수 kinetic repartition에서는 총 $n,u,\Pi$가 적분 항등식으로 보존된다.
low distribution을 T2의 기체로 교체하면 에너지와 수를 맞추는 closure가 추가되고,
새 $T$는 low energy와 count가 정한다.
Maxwellian 모양·압력 등방화·relaxation 속도는 해당 thermalization 모형의 조건이다.
주어진 $E_c(t)$의 상대 경계속도는 $\dot E_c-\dot W$,
drift 전달은 $J_{E,\rm drift}=E_cJ_{N,\rm drift}$다.
jump에는 각 $W_r<E_c$의 실제 에너지를 쓴다.
$E_c=\chi k_BT$는 $J_N$에도 $\dot T$를 넣어 경계밀도 결합을 만든다.
moving-cutoff 유도에서 이 추가 항을 전개한다.

## 5. 판별력이 있는 직접 구성

### 예 A: active birth만 있는 구간

고정 $V$에서 thermal gas $(n_{\rm th,0},T_0)$를 두고,
열 전달 없이 에너지 $W_b$의 전자를 active에 $S>0$의 속도로 만든다.
$S_A=S$, $Q_A=W_bS$, 다른 교환·source·loss는 0이다.
$\dot n_A=S$, $\dot u_A=W_bS$이고 (T.6)은 $\dot T=0$을 준다.
$n_{\rm all}$이 증가하는 all-free 식에서도

$$
c_v(n_{\rm all}-n_A)\dot T
=W_bS-(W_b-e)S-eS=0.
\tag{T.13}
$$

따라서 active 전자를 total count에 포함하면서 thermal $T$를 그대로 유지한다.
이 예는 source 수 항과 기준에너지 상태가 함께 필요함을 직접 판별한다.

### 예 B: 유한한 particle packet의 열적 편입

고정 $V$에서 thermal count $n_0$, $T_0$에 $N$ m$^{-3}$의 전자,
kinetic energy $\mathcal E_{\rm join}$ 및 heat $\mathcal E_h$가 들어오면 수·에너지 보존으로

$$
T_1=\frac{c_vn_0T_0+\mathcal E_{\rm join}+\mathcal E_h}{c_v(n_0+N)},
\qquad
\boxed{T_1-T_0=
\frac{\mathcal E_{\rm join}+\mathcal E_h-e(T_0)N}{c_v(n_0+N)}}.
\tag{T.14}
$$

$\mathcal E_{\rm join}=\sum W_r/V$다.
직전 A2 식 (11)은 이 식에 저장 cutoff energy와 $N_c$를 넣은 경우다.
직전 누적 energy 기호 $E_c$와 이번 threshold $E_c(t)$를 구별하기 위해 누적량을
$\mathcal E_{\rm join}$으로 표기한다.
저장된 $\Delta T=3.8418834731514848\times10^{-14}$ K를 재사용한다.

### 예 C: 팽창하는 thermal gas

thermal source와 교환이 0이면

$$
\dot T=-\frac23\theta T,\qquad
T(t)=T(0)\left[\frac{V(t)}{V(0)}\right]^{-2/3}.
\tag{T.15}
$$

active component에는 별도로 $\mathcal D u_A+K:\Pi_A=0$이 적용된다.

### 예 D: 지속적인 particle addition

고정 $V$, 일정한 $S_c\ge0$, 편입 에너지 $W_j$, heat $P_0$에 대해

$$
n_{\rm th}=n_0+S_ct,\qquad
T(t)=\frac{c_vn_0T_0+(P_0+W_jS_c)t}{c_v(n_0+S_ct)}.
\tag{T.16}
$$

$S_c>0$일 때 장시간 온도는 $[W_j+P_0/S_c]/c_v$로 접근한다.
새 particle energy와 thermal reference의 차를 보여주는 해석해다.

## 6. 계산 인터페이스

입력은 같은 시각의 $n_{\rm all},T,n_A,u_A,\Pi_A,\theta,K$와 source·transfer ledgers다.

1. **thermal transfer API:** $S_{\rm th}=S_d+J_N$,
   $Q_{\rm th}=Q_d+P_h+J_E$를 받아
   $\dot T=(Q_{\rm th}-eS_{\rm th}-\theta k_BTn_{\rm th})/(c_vn_{\rm th})$를 계산한다.
2. **total moment API:** $S_{\rm all},Q_{\rm kin},\mathcal Dn_A,\mathcal Du_A,K:\Pi_A$를 받아
   $S_{\rm th}=S_{\rm all}-\mathcal Dn_A$,
   $Q_{\rm th}=Q_{\rm kin}-\mathcal Du_A-K:\Pi_A$로 같은 식을 계산한다.

두 번째는 보존 회계 검사에 적합하다.
첫 번째는 큰 source와 active derivative의 차감이 작은 thermal source를 만드는 경우에도
직접 작은 교환항을 사용할 수 있다. $n_{\rm th}>0$은 양의 thermal heat capacity 조건이다.

유한 step에서는 $N_{\rm th}=Vn_{\rm th}$, $U_{\rm th}=Vu_{\rm th}$를 쓴다.
실제 적분량이 $\Delta N_{\rm th}$ 및

$$
\Delta U_{\rm th}
=\int_{t_n}^{t_{n+1}}V[Q_{\rm th}-\theta p_{\rm th}]\,dt
\tag{T.17}
$$

이면 보존량을 더한 뒤
$T_{\rm new}=U_{\rm th,new}/(c_vN_{\rm th,new})$로 inversion한다.
이 대수는 주어진 적분량에 대해 정확하다. 시간 quadrature 오차는 선택한 integrator의 수치 의무다.

collision-clock의 $X=Vx$, $\tau=\int a\,dt$로 얻은 heat/number/join ledgers를 위 API에 연결한다.
signed $u_{\rm ex}$를 passive energy norm에 넣지 않는다.
active energy·heat 오차와 number 오차를 별도로 EOS에 전달한다.

## 7. 온도 오차로 이어지는 상계

같은 시각의 thermal counts가 $N,\widehat N\ge N_{\min}>0$,
energies가 $U,\widehat U\ge0$이고
$T=U/(c_vN)$, $\widehat T=\widehat U/(c_v\widehat N)$이면

$$
\boxed{|T-\widehat T|
\le\frac{|U-\widehat U|}{c_vN_{\min}}
+\frac{\widehat T}{N_{\min}}|N-\widehat N|.}
\tag{T.18}
$$

**증명.**
$T-\widehat T=(U-\widehat U)/(c_vN)
+\widehat T(\widehat N-N)/N$에 삼각부등식을 적용한다. $\square$

이는 energy/number certificate를 observable temperature로 옮기는 map이다.
$\Delta U$는 같은 endpoint의 **thermal energy 오차**다.
누적 deposition 오차를 여기에 넣으려면 expansion work와 기타 cooling/source 차이가
누적된 항도 포함한다.
고정 부피·동일한 나머지 source에서는 deposition ledger 오차가 직접 $\Delta U$가 된다.
팽창하는 단원자 thermal gas에는 energy balance의 integrating factor $V^{2/3}$를 사용할 수 있다.

이 map과 collision-clock의 coefficient residual은 실제 허용오차가 주어지면
연산자 재사용을 결정하는 충분조건을 제공한다.
허용오차의 수치값과 무관하게 위 구성과 증명은 명시한 가정 아래에서 완결된다.


## 8. 팽창 중의 누적 deposition certificate를 온도로 전달하기

T2의 단원자 기체에서는 입자수가 변하더라도
$p_{\rm th}=2u_{\rm th}/3$이다.
$U=Vu_{\rm th}$, $N=Vn_{\rm th}$,
$Q_{\rm th}=Q_d+P_h+J_E$ 및

$$
\mu(t)=\left[\frac{V(t)}{V(0)}\right]^{2/3},\qquad
\mathcal H(t)=\int_0^t V(s)Q_{\rm th}(s)\,ds
\tag{T.19}
$$

로 두면 thermal energy 방정식은

$$
\dot U+\frac23\theta U=\dot{\mathcal H},\qquad
\boxed{U(t)=\mu(t)^{-1}
\left[U(0)+\int_0^t\mu(s)\,d\mathcal H(s)\right]}.
\tag{T.20}
$$

이 적분해는 같은 prescribed expansion history 아래에서 가열·편입 이력과 온도를 직접 연결한다.
수 방정식 $N(t)=N(0)+\int_0^t VS_{\rm th}ds$를 함께 사용해 $T=U/(c_vN)$를 얻는다.

### 정리 T-B: 누적 열 전달 오차의 endpoint thermal energy 상계

정확 이력과 재사용 이력의 차를 $\delta$로 쓰자.
두 이력이 같은 $V(t)$를 사용하고 모든 $s\le t$에서
$|\delta\mathcal H(s)|\le B_H(s)$를 만족하면

$$
\boxed{
|\delta U(t)|\le
\frac{|\delta U(0)|}{\mu(t)}
+B_H(t)+\frac1{\mu(t)}
\int_0^t|\dot\mu(s)|B_H(s)\,ds .
}
\tag{T.21}
$$

**증명.** $\delta\mathcal H(0)=0$이고
$\int_0^t\mu\,d(\delta\mathcal H)
=\mu(t)\delta\mathcal H(t)-\int_0^t\dot\mu\,\delta\mathcal H\,ds$다.
(T.20)에 대입하고 삼각부등식을 적용한다. $\square$

팽창만 있는 구간 $\theta\ge0$에서 $B_H$가 비감소이면

$$
|\delta U(t)|\le
\frac{|\delta U(0)|}{\mu(t)}
+\left(2-\frac1{\mu(t)}\right)B_H(t).
\tag{T.22}
$$

$\mu=1$에서는 그대로 $|\delta U(0)|+B_H(t)$다.
$B_H$는 같은 정의의 전체 thermal deposition ledger에 대한 bound여야 한다.
heat와 cutoff energy를 함께 편입하는 경우 두 출력의 합을 certificate의 출력으로 선택한다.
그 밖의 서로 다른 cooling/source가 있으면 그 누적 차의 bound를 합한다.
이 조건 아래에서 (T.21)과 (T.18)은 collision operator 잔차 → 누적 thermal deposition
→ 팽창 후 thermal energy → 온도의 완결된 오차 전달 경로다.
이는 prescribed background에서의 정리이며,
온도·조성 feedback의 계수 차이는 collision-clock의 $\Delta(t)$ 또는 별도 source 차에 포함한다.

