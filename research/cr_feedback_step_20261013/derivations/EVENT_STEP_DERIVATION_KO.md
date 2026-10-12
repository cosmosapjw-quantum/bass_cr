# 공통 사건 증분을 사용하는 H/He–active–thermal 보존 step

단위: CR-THEORY-FEEDBACK-20261013. 이 문서는 채택된 TH1–TH7의 수·에너지 회계에서
온도·조성 피드백에 사용할 실제 반응 step을 구성한다. 근거 상태는 **직접 유도**다.
유한 에너지 채널의 reference implementation과 정확 유리수 검산은 별도 파일에 결속한다.

## 1. 현재 가정과 구성의 목표

이 반응 부분 step에서는 고유부피 $V_*>0$, active 에너지 격자, 이온화 문턱 및 사건별
출력 에너지를 고정한다. 시간은 고유시간 $t$, step 길이는 $h\ge0$다.
부피·운동량의 기하학적 변화는 별도의 주어진 배경 substep에서 처리한다.
원자핵과 thermal 전자는 비상대론적 단원자 이상기체로 같은 온도를 공유하며,
원자핵의 반동과 들뜬 원자의 에너지는 이 작은 ground-state family에서 생략한다.
이 조건은 아래 energy column의 물리적 정의에 포함된다.
순 운동량이 0인 원래 기준계를 유지할 때에는 각 active count를 같은 가중치의
$\pm\boldsymbol p$ 쌍으로 실현하고 daughter의 각도 재분배도 반전 대칭으로 선택한다.
에너지와 종별 수의 증명은 그 대칭 안의 개별 각도 선택에 의존하지 않는다.

상태는 공행 셀의 실제 입자수와 에너지다. active 에너지 bin의 가중 입자수도 허용하며,
그 경우 각 bin 에너지와 가중 입자수의 곱이 kinetic energy를 정의한다.
초기 상태는 비음수이며 총 원자핵 수가 양수다.
온도 피드백에 필요한 반응계수는 선언한 정칙 영역에서 유한·비음수이며 국소 Lipschitz다.

목표는 다음 세 성질을 같은 식에서 실현하는 것이다.

1. 같은 충돌의 active 변화, 이온화 단계 변화, thermal 전자수와 에너지 변화를 하나의 extent로 갱신한다.
2. 그 extent들이 공유하는 반응물·thermal energy의 총 소비량을 사용하여 각 재고의 양수성을 보존한다.
3. 계수에 들어가는 $T$, 조성, 전자밀도 등을 endpoint 후보 상태에서 평가할 수 있도록 명시적인 map을 만든다.

선택한 방법은 반응별 extent의 유리함수 갱신이다. 반응물의 질량작용 인자는 초기 상태에서
고정하고, 온도·조성에 의존하는 계수는 후보 상태에서 평가한다.
이 방법은 완성한 화학·에너지 보존 항등식과 일차 시간 정확도를 갖는다.

## 2. 상태와 보존 행

세 이온화 단계를 $r\in\{{\rm H},{\rm HeI},{\rm HeII}\}$로 쓰고,
각 이온화 에너지를 $I_{\rm H},I_{\rm HeI},I_{\rm HeII}>0$라 둔다.
상태 순서는

$$
y=(A_{\rm H},A_{\rm HeI},A_{\rm HeII},A_L,
H^0,H^+,{\rm He}^0,{\rm He}^+,{\rm He}^{++},
N_e,U,R)^T
\tag{ES.1}
$$

다. $A_j$는 active electron count, $N_e$는 thermal electron count,
$U$는 thermal kinetic energy, $R$는 이 부분 step까지 방출된 복사 에너지의 누적 장부다.
$R$는 방출 시각·기준계의 에너지 유출을 기록한다. 셀 안에 남아 있는 복사장의 동역학은
별도 photon 상태를 추가하여 같은 사건 column을 연결할 수 있다.

원자핵 수, 총 ionic charge에 대한 자유전자 차이, energy는

$$
N_{\rm H}=H^0+H^+,\qquad
N_{\rm He}={\rm He}^0+{\rm He}^++{\rm He}^{++},
\tag{ES.2}
$$

$$
Q/e=H^++{\rm He}^++2{\rm He}^{++}-N_e-\sum_jA_j,
\tag{ES.3}
$$

$$
\begin{aligned}
{\cal E}
={}&\sum_j E_j A_j+U+R\\
 &+I_{\rm H}H^+
 +I_{\rm HeI}{\rm He}^+
 +(I_{\rm HeI}+I_{\rm HeII}){\rm He}^{++}
\end{aligned}
\tag{ES.4}
$$

다. 중성 ground state를 chemical energy의 0으로 선택했다.
각 원자핵 수와 총 bound+free 전자수가 고정되므로 상수인 rest-energy 항은
이 kinetic–chemical ledger에서 생략할 수 있다.
(ES.3)은 전기적 중성이면 0이며, 증명은 임의의 보존된 $Q$에 대해 성립한다.

Thermal EOS에 들어가는 입자수는

$$
N_{\rm th}=N_{\rm H}+N_{\rm He}+N_e,\qquad
c_v=\frac32 k_B,\qquad T=\frac{U}{c_vN_{\rm th}}.
\tag{ES.5}
$$

각 원자핵은 이온화 단계와 관계없이 한 입자로 센다.
$N_{\rm H}+N_{\rm He}>0$이면 $N_{\rm th}$의 양의 하한이 즉시 확보된다.

## 3. 고정 에너지 열을 갖는 실제 H/He 사건 family

$E_c>0$를 고정 cutoff로 정하고

$$
E_L=2E_c,\qquad \epsilon_s=\frac12E_c,\qquad
E_{A,r}=E_L+I_r+\epsilon_s
\tag{ES.6}
$$

로 active bin을 구성한다. 이 예의 에너지 격자는 양의 daughter 에너지와 threshold를
정확히 동시에 만족하도록 만든다. 실제 BASS_CR 격자에 연결할 때에는 이미 정의된
양의 재분배 가중치가 같은 수·에너지 열을 만들면 그 열을 그대로 사용할 수 있다.

세 쌍 $(X_r^q,X_r^{q+1})$는
$(H^0,H^+)$, $({\rm He}^0,{\rm He}^+)$, $({\rm He}^+,{\rm He}^{++})$다.

### 3.1 Active impact ionization와 subcutoff secondary

$$
A_r+X_r^q\longrightarrow A_L+X_r^{q+1}+e_{\rm th},
\qquad \Delta U=\epsilon_s.
\tag{ES.7}
$$

전자 daughter는 active primary 하나와 $\epsilon_s<E_c$인 thermal secondary 하나다.
입사 kinetic energy와 출력은
$E_{A,r}=E_L+\epsilon_s+I_r$를 만족한다.
한 사건에서 자유전자수가 1 증가하고 ionic charge도 1 증가한다.
해당 active parent와 표적 원자 모두 동일한 extent만큼 감소한다.

이 채널은 실제 ionization kernel에서 특정 daughter 에너지 채널을 선택한 유한 모델이다.
계수는 그 채널의 비음수 cross-section weight와 입사속도를 포함한다.
다른 daughter 채널을 추가할 때에도 각 channel마다 같은 형태의 column을 추가한다.

### 3.2 끝단 thermalization

$$
A_L\longrightarrow e_{\rm th},
\qquad \Delta U=E_L.
\tag{ES.8}
$$

이 사건은 끝단 셀의 stopping heat와 최종 thermal 편입을 합한 전달을 나타낸다.
이 부분 step의 선택된 유한 closure에서는 양의 hazard $\nu_L$를 사용한다.
입자수 1과 실제 총 kinetic energy $E_L$가 같은 extent로 이동한다.
이동 cutoff에서의 drift와 jump 분해는 이전 TH1에 있으며,
그 출력이 동일한 총량을 주면 이 column에 직접 결속할 수 있다.

### 3.3 Thermal collisional ionization

$$
e_{\rm th}+X_r^q
\longrightarrow2e_{\rm th}+X_r^{q+1},
\qquad \Delta U=-I_r.
\tag{ES.9}
$$

사건 matrix의 thermal electron **순** 변화는 $+1$이다.
입사 thermal electron의 존재는 질량작용 인자 $N_eX_r^q/V_*$가 보장한다.
Threshold energy는 thermal kinetic reservoir에서 chemical energy로 이동한다.
Threshold 위의 전자 kinetic energy는 thermal pool 안에 남는다.

### 3.4 에너지별 radiative recombination

고정된 captured-electron kinetic energy node $\epsilon_{r\ell}>0$에서

$$
e_{\rm th}+X_r^{q+1}
\longrightarrow X_r^q+\gamma,
\quad
\Delta U=-\epsilon_{r\ell},
\quad
\Delta R=I_r+\epsilon_{r\ell}.
\tag{ES.10}
$$

를 둔다. Capture energy는 $T$에 따라 변하는 column 대신 고정 node로 분해했다.
이에 따라 평균 cooling energy의 온도 의존성을 비음수 계수들에 넣을 수 있다.

예를 들어 비상대론적 Maxwellian energy density

$$
F_E(\epsilon;T)=
\frac{2}{\sqrt\pi}
\frac{\sqrt{\epsilon}}{(k_BT)^{3/2}}
\exp\!\left(-\frac{\epsilon}{k_BT}\right)
$$

와 양의 quadrature weight $\omega_\ell$에 대해

$$
\alpha_{r\ell}(T)=
\omega_\ell F_E(\epsilon_{r\ell};T)
v(\epsilon_{r\ell})\sigma_r^{\rm rec}(\epsilon_{r\ell})
\ge0
\tag{ES.11}
$$

다. $\omega_\ell$의 차원은 J,
$v\sigma$의 차원은 m$^3$ s$^{-1}$이고,
$\alpha_{r\ell}$는 m$^3$ s$^{-1}$다.
총 recombination coefficient와 thermal cooling coefficient는 각각
$\sum_\ell\alpha_{r\ell}$, $\sum_\ell\epsilon_{r\ell}\alpha_{r\ell}$로 주어진다.
이 식은 양의 energy quadrature가 정의하는 유한 closure다.
Quadrature 오차는 독립적인 coefficient approximation으로 평가한다.
작은 machine-readable 예제는 각 이온화 단계마다 node 하나를 사용한다.

이 family의 모든 사건에서 (ES.2)–(ES.4)의 변화가 0임은 직접 대입으로 확인된다.
예를 들어 radiative recombination은
$-\epsilon_{r\ell}+(I_r+\epsilon_{r\ell})-I_r=0$이고,
thermal ionization은 $-I_r+I_r=0$이다.

## 4. 고정 column과 상태 의존 계수의 분리

사건 $r$의 상태 증분을 $s_r$, 모든 column을 모은 행렬을 $S$라 쓰자.
(ES.2)–(ES.4)의 보존 행을 $L$에 모으면

$$
LS=0.
\tag{ES.12}
$$

행렬 $S$는 종별 stoichiometry와 event energy ledger다.
쌍입자 반응의 물리적 propensity는 종 밀도의 곱으로 구성하며,
$S$를 단일 입자 Markov generator로 바꾸는 가정을 사용하지 않는다.

초기 상태를 $y^n$, endpoint 후보를 $z$라 두고

$$
f_r(z;y^n)=k_r\!\left(T(z),x_{\rm H}(z),x_{\rm He}(z),
n_e(z),\ldots\right)b_r(y^n,V_*)
\ge0
\tag{ES.13}
$$

로 proposal event rate를 정의한다.
예를 들어 impact에는 $b=A_r^nX_r^{q,n}/V_*$,
thermal ionization에는 $b=N_e^nX_r^{q,n}/V_*$,
recombination에는 $b=N_e^nX_r^{q+1,n}/V_*$를 사용한다.
끝단 thermalization은 $b=A_L^n$이고 계수의 단위가 s$^{-1}$다.
각 $f_r$의 단위는 사건수 s$^{-1}$다.

분율 $x$와 밀도 $n_e$가 계수에 나타나는 물리적 예는
전자 screening, Coulomb logarithm, 매질 조성에 따른 stopping 및 selected closure의 계수다.
기존 계수가 $T$에만 의존하면 그 제한된 의존성을 그대로 사용한다.
초기점에서는

$$
f_r(y^n;y^n)=\mathcal R_r(y^n),
$$

즉 선언한 유한 반응모형의 실제 propensity가 된다.
온도와 조성 feedback을 사용하는 비선형 종료 조건은 $z=\Phi_h(z;y^n)$다.
그 존재·유일성·반복 오차는 동반 피드백 유도에서 다룬다.

## 5. 공유 소비량에 의한 extent의 명시적 구성

음의 순 증분과 비음수 순 생산량을

$$
C_{ir}=\max(-S_{ir},0),\qquad P_{ir}=S_{ir}+C_{ir}\ge0
$$

로 둔다. $C$는 **재고를 감소시키는 순 소비량**이다.
촉매나 양쪽에 나타나는 입사 전자 등의 gross 반응물 조건은 (ES.13)의 질량작용 인자에 포함된다.

초기 재고가 0인 감소 행 $i$를 요구하는 사건은 이번 부분 step에서 비활성화하여
$f_r=0$으로 둔다. 이 규칙은 그 사건에만 적용한다.
다른 사건으로 생성된 새 종의 소비는 후속 step에서 반영한다.
이하 합에는 이 support 규칙을 적용한 rates를 사용한다.

공유 재고 $i$의 총 제안 소비율과 사건별 denominator는

$$
c_i(z)=\sum_r C_{ir}f_r(z;y^n),\qquad
d_r(z)=\sum_{i:C_{ir}>0}\frac{c_i(z)}{y_i^n}.
\tag{ES.14}
$$

$y_i^n>0$인 활성 감소 행에서만 나눗셈을 수행한다.
사건 extent와 갱신 map을

$$
\boxed{
\xi_r(z)=\frac{h f_r(z;y^n)}{1+h d_r(z)},\qquad
\Phi_h(z;y^n)=y^n+S\xi(z)
}
\tag{ES.15}
$$

로 정의한다. 비활성 사건의 extent는 0이다.
$C_{ir}$는 입자수 행에서는 particle/event,
에너지 행에서는 J/event이므로 $c_i/y_i^n$와 $d_r$는 s$^{-1}$다.
따라서 denominator는 무차원이며 $\xi_r$는 사건수다.
양의 대각 단위 변환 $y=D\bar y$, $S=D\bar S$를 적용하면
$c_i/y_i^n=\bar c_i/\bar y_i^n$이므로 모든 extent가 그대로 유지된다.
그 결과 (ES.15)는 입자수·에너지 행의 단위 선택과 가환한다.

여러 반응이 같은 중성 H, thermal electron 또는 thermal energy를 소비하면,
그 모든 rate가 같은 $c_i$에 들어간다.
그 뒤 하나의 $\xi_r$가 사건의 모든 출력 행을 갱신한다.

### 정리 ES-A: 비음성과 양의 재고 하한

유한한 비음수 proposals, $h\ge0$ 및 $y^n\ge0$ 아래에서

$$
\Phi_h(z;y^n)\ge0.
$$

더 구체적으로 초기 재고 $y_i^n>0$이면

$$
\boxed{
\Phi_{h,i}(z;y^n)\ge
\frac{y_i^n}{1+h c_i(z)/y_i^n}>0
}
\tag{ES.16}
$$

이다.

**증명.** $C_{ir}>0$인 사건에 대해
$d_r\ge c_i/y_i^n$이므로

$$
\sum_r C_{ir}\xi_r
\le
\frac{h\sum_rC_{ir}f_r}{1+h c_i/y_i^n}
=
\frac{h c_i}{1+h c_i/y_i^n}
=
y_i^n-\frac{y_i^n}{1+h c_i/y_i^n}.
$$

$P\xi\ge0$를 더하면 (ES.16)이 따른다.
$y_i^n=0$이면 감소 사건들은 비활성이고 생산항만 남는다. $\square$

이 증명은 시간간격의 상한을 사용하지 않는다.
정확도와 비선형 고정점 유일성에는 별도의 step 조건을 사용한다.

### 정리 ES-B: 핵수·전하·에너지의 정확한 동시 보존

$LS=0$이면 proposal을 평가한 후보 $z$와 관계없이

$$
\boxed{
L\Phi_h(z;y^n)=Ly^n
}
\tag{ES.17}
$$

이다. 따라서 고정점 반복의 각 image도 같은 보존량을 갖는다.

**증명.** (ES.15)에 왼쪽에서 $L$을 곱하면
$L\Phi_h=Ly^n+LS\xi=Ly^n$이다. $\square$

동결된 co-reactant는 propensity를 정하는 입력으로만 사용된다.
그 co-reactant의 **실제 갱신량**은 다른 출력과 똑같은 $\xi_r$에서 나오므로,
원 핵수·전하·에너지 불변량을 정확히 보존한다.
열적 energy를 별도로 사후 절단하거나 이온 fraction만 재정규화할 필요가 없다.

### 열적 상태와 all-free 표현의 연결

$N_{\rm H}+N_{\rm He}>0$ 및 $U^n>0$이면 (ES.16)–(ES.17)로
$U^{n+1}>0$, $N_{\rm th}^{n+1}\ge N_{\rm H}+N_{\rm He}>0$다.
따라서 EOS inversion은

$$
\boxed{
T^{n+1}=\frac{U^n+\sum_r S_{Ur}\xi_r}
{c_v\left(N_{\rm th}^n+\sum_r S_{er}\xi_r\right)}
}
\tag{ES.18}
$$

로 유일하게 정해진다. 단일 사건의 유한 증분에 대해서는

$$
T^{n+1}-T^n
=
\frac{\sum_r
\bigl(S_{Ur}-c_vT^nS_{er}\bigr)\xi_r}
{c_vN_{\rm th}^{n+1}}.
\tag{ES.19}
$$

여기서 $S_{er}$는 thermal electron count의 순 증분이다.
원자핵 수가 보존되므로 thermal count 변화와 같다.

최종 active count와 energy로
$N_{\rm all}=N_{\rm th}+\sum_jA_j$,
$U_{\rm ex}=\sum_jE_jA_j-c_vT\sum_jA_j$를 계산하면,
이전 TH2의 all-free 표현을 동일한 상태에서 얻는다.
Signed excess energy는 positivity 재고에 포함하지 않는다.

## 6. 정확도와 공유 반응물의 실제 예

물리적 유한 반응모형을

$$
\dot y=R(y):=S\mathcal R(y)
\tag{ES.20}
$$

로 둔다. 정칙한 해 영역에서 proposals와 그 후보 의존성은 국소 유계·Lipschitz이며,
고정점 branch가 $z_h=y^n+O(h)$를 만족한다고 하자.
(ES.13)의 초기점 일치성과 (ES.15)를 전개하면

$$
\xi_r(z_h)=h\mathcal R_r(y^n)+O(h^2),\qquad
z_h=y^n+hR(y^n)+O(h^2).
\tag{ES.21}
$$

즉 한 step의 local truncation error는 $O(h^2)$이고,
동반 안정성 조건 아래의 시간 정확도는 일차다.
Rate feedback을 종료하는 잔차의 크기도 이 정확도와 함께 정한다.

단일 쌍입자 반응 $A+B\to\cdots$에 초기 $(a,b)$,
상수 질량작용 계수 $\kappa$를 두면
$f=\kappa ab$, $d=\kappa(a+b)$이며

$$
\xi_h=\frac{h\kappa ab}{1+h\kappa(a+b)}.
\tag{ES.22}
$$

두 반응물의 감소량이 같은 $\xi_h$다.
$a=b=1$일 때 연속 반응식의 정확 extent는
$\xi_{\rm exact}=\kappa h/(1+\kappa h)$이고, 두 해의 차는

$$
\xi_{\rm exact}-\xi_h
=
\frac{\kappa^2h^2}
{(1+\kappa h)(1+2\kappa h)}.
\tag{ES.23}
$$

이다. 이 해석 사례는 event conservation과 유한 시간 정확도를 각각 판별한다.
큰 step에서 보존성과 비음성은 유지되며, 시간 정확도는 선택한 일차 적분법의
오차 조건에 따라 제어한다.

## 7. 구현과 검증 연결

- 실제 reference module: event_capacity_step.py.
- 고정 사건과 불변량: examples/H_HE_EVENT_FAMILY.json.
- 정확 유리수 판별 검산: checks/run_event_checks.py.
- 실제 실행 결과: results/EVENT_CHECKS.json.

Reference module은 입력 숫자를 Fraction으로 바꾸어 유한 산술 입력에 대한
사건 장부를 정확하게 계산한다. SI $k_B$는 정확한
$1.380649\times10^{-23}$ J K$^{-1}$를 사용한다.
상용 부동소수점 큰 격자 구현에서는 같은 물리적 map에 별도의 누적 오차 예산을 붙인다.

이 부분 결과는 고정 energy-channel 모델의 구성·보존·양수성·EOS 및 일차 정합성이다.
기존 BASS_CR 전체 atomic kernel과 연결할 때에는
각 기존 channel의 threshold, daughter energy와 number weight,
capture cooling quadrature 및 허용된 계수 domain을 같은 column 계약에 결속한다.
고정점 조건과 기하학적 substep을 합한 완전한 한 step은 동반 문서에서 완결한다.

### 실행한 판별 검산

작성자가 Python 3.12.14 표준 라이브러리의 정확한 유리수 산술로 9개 검산을 실행했고
9개 모두 통과했다. 10개 event column의 핵수·전하·energy 행 40개가 정확히 0이며,
모든 채널이 동시에 같은 donor와 thermal energy를 소비하는 큰 step에서도
양수성과 네 보존량이 유지된다. Captured energy가 초기 thermal 평균 energy와 같은
단일 recombination에서는 finite-step 온도가 정확히 유지된다.
쌍입자 반응의 연속 정확해와의 차는 (ES.23)과 세 step에서 정확히 일치한다.
원자 threshold의 수치 입력은 이 검산에서만 쓰는 무차원 유리수 fixture이며,
측정된 H/He 원자 자료와 구분한다. 실제 결과와 source identity는
results/EVENT_CHECKS.json에 기록했다. 새 ODE 적분이나 전체 atomic kernel 실행은 사용하지 않았다.

