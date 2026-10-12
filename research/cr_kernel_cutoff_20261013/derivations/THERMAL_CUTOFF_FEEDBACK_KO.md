# 온도에 의존하는 cutoff의 보존적 유한 분할과 implicit 열적 응답

연구 단위: CR-THEORY-KERNEL-CUTOFF-20261013  
선택한 열린 구성: CR_THEORY_THERMAL_CUTOFF_FEEDBACK  
상태: 명시한 spectrum·EOS·branch 가정 아래 유도한 조건부 구성. 실제 원자 kernel의 채택 또는 새 물리 scenario의 검증을 뜻하지 않는다.

## 0. 이번에 닫은 구성과 재사용 근거

기존 이동 경계 결과 MC1–MC37은 주어진 cutoff의 양쪽 입자수·운동에너지 ledger가 정확히 상쇄함을 보였다. 기존 thermal excess 결과는 thermal count와 all-free count 표현 사이의 정확한 변환과 EOS 오차식을 제공했다. 이번에는 cutoff 자체를 온도로 정하여
\[
c(T):=E_c(T)=\chi k_BT,\qquad \chi>0,\qquad c_v=\frac32k_B
\tag{TCF.1}
\]
로 놓고, 공통 inventory에서 한 번의 endpoint 분할을 실제로 정의한다. 연속 밀도에서는 양의 근의 존재·유일성과 오차 한계를 얻고, 실제 에너지 격자의 원자 measure에서는 유한 branch 열거 및 continuation scan을 구성한다.

여기서 \(c(T)\)는 cutoff energy의 약기호이며 광속을 뜻하지 않는다. 공변 유도에서 사용하는 광속 \(c_{\rm light}\)와 구별한다. 모든 \(N,U,\rho\)는 한 comoving cell의 **입자수·운동에너지·에너지당 입자수**다. proper-volume 밀도와 섞지 않는다. 초기 reference와 최종 candidate를 구별하기 위해 predictor가 제공한 데이터에는 아래첨자 \(h\), 이전 시간의 물리 상태에는 \(n\)을 쓴다.

재사용한 원 근거는 다음과 같다.

- ../inputs/prior/inputs/prior/derivations/MOVING_CUTOFF_KO.md: MC19의 양방향 trace, MC34–MC37의 implicit coefficient와 signed finite moments.
- ../inputs/prior/inputs/prior/derivations/THERMAL_EXCESS_KO.md: all-free/thermal inventory와 이상기체 EOS 오차.
- ../inputs/prior/derivations/FEEDBACK_THEOREMS_KO.md: 양의 공통 사건 endpoint와 물리 ODE 오차의 구별.
- ../inputs/prior/derivations/EVENT_STEP_DERIVATION_KO.md: 실제 parent/daughter energy에 결속된 사건 열과 보존 row.

이전 과학 실행을 다시 돌리지 않는다. 아래 정리는 위 근거의 새로운 구성적 연장이며, 실제 새 symbolic 실행의 결과와 구현 실행의 결과는 각각 해당 results 파일에 따로 기록한다.

## 1. 먼저 고정하는 common all-free 상태

한 cutoff closure solve를 시작할 때 predictor가 다음 자료를 제공한다고 하자.

\[
\mathscr C_h=N_{\rm nuc}+N_{\rm e,all},\qquad
\mathscr E_h=U_{\rm th}+U_{\rm active},\qquad
\mu_h\ge0,\qquad c_0=\chi k_BT_n>0 .
\tag{TCF.2}
\]

\(\mathscr C_h\)는 nuclei와 모든 자유전자를 합한 count, \(\mathscr E_h\)는 두 자유 운동 집단의 kinetic energy다. Bound-state potential, excitation, radiation의 별도 ledger는 cutoff를 옮기는 동안 바꾸지 않는다. 따라서 사건 step이 보존하는 전체 에너지에 cutoff의 재분할을 합성해도 그 보존 row는 유지된다. Ionization 등의 외부 predictor는 \(\mathscr C_h\)나 \(\mathscr E_h\)를 바꿀 수 있으나, **하나의 cutoff 근을 구하는 동안 이 두 수와 \(\mu_h,c_0\)를 고정한다.**

\(\mu_h\)는 endpoint에서 추적하는 전자 measure다. 반드시 active tail만을 뜻하지 않는다. 아래로 cutoff를 내릴 수 있는 구간에는 이전에 thermal 쪽으로 배정한 resolved electron inventory도 남겨 둔다. 전체 \(\mu_h\)의 0차와 1차 에너지 모멘트가 유한하며, 나머지 unresolved reservoir를
\[
N_{B,h}=\mathscr C_h-\int d\mu_h\ge N_{\rm nuc}>0,\qquad
U_{B,h}=\mathscr E_h-\int W\,d\mu_h\ge0
\tag{TCF.3}
\]
로 정의한다. \(\mu_h\)의 support는 \(W\ge0\)에 있다.

(TCF.3)은 간단히 확인할 수 있는 충분한 positivity 조건이다. \(N_B\)에는 nuclei와 명시적으로 분해하지 않은 thermal electrons가 들어갈 수 있다. \(U_B\)는 그 고정 reference reservoir의 kinetic inventory다. 이는 최종 nuclei가 고정된 별도 온도를 갖는다는 뜻이 아니다. 최종 thermal closure는 합쳐진 \(U,N\) 전체를 공통 \(T\)로 다시 표현한다. 선택한 \(\mu_h\)가 Maxwellian이거나 실제 저에너지 분포와 같다고 이 모멘트 조건만으로 주장하지 않는다.

열적 상태를 오직 \(U_{\rm th},N_{\rm th}\) 두 모멘트로 저장한 이전 모델에는 임의의 하향 cutoff trace가 들어 있지 않다. 이때는 양의 lower-band reconstruction을 추가 자료로 지정하거나, 실제 원자 node와 ownership을 보존하거나, 현재 이용 가능한 단방향 경로로 범위를 제한한다. 두 모멘트가 같은 양의 분포들도 경계에서 서로 다른 값을 가질 수 있으므로 \(U,N\)만으로 그 trace를 계산하지 않는다.

## 2. TC1 — signed 유한 분할, positivity, 정확한 보존

경계의 원자 질량은 thermal 쪽이 소유한다는 규약을 택한다. 따라서 active tail은
\[
A_N(c)=\mu_h((c,\infty)),\qquad
A_E(c)=\int_{(c,\infty)}W\,d\mu_h .
\tag{TCF.4}
\]
이고 candidate \(T\)에서
\[
N_h(T)=\mathscr C_h-A_N(c(T))
      =N_{B,h}+\mu_h([0,c(T)]),
\]
\[
U_h(T)=\mathscr E_h-A_E(c(T))
      =U_{B,h}+\int_{[0,c(T)]}W\,d\mu_h
\tag{TCF.5}
\]
로 놓는다. (TCF.3)에 의해 모든 candidate에서
\[
N_h(T)\ge N_{B,h}\ge N_{\rm nuc}>0,\quad U_h(T)\ge U_{B,h}\ge0,
\quad A_N,A_E\ge0 .
\tag{TCF.6}
\]
즉, positivity를 얻기 위해 음의 상태를 잘라 내거나 이후에 에너지를 보정하지 않는다.

경계 interval에 원자가 없고 \(\mu_h=\rho_h(W)dW\)라고 하자. \(c_0\)에서의 고정 reference를
\[
\bar N_h=\mathscr C_h-A_N(c_0),\qquad
\bar U_h=\mathscr E_h-A_E(c_0)
\tag{TCF.7}
\]
로 정의하면
\[
\Delta N_h(T)=\int_{c_0}^{c(T)}\rho_h(W)dW,\qquad
\Delta U_h(T)=\int_{c_0}^{c(T)}W\rho_h(W)dW,
\tag{TCF.8}
\]
\[
N_h(T)=\bar N_h+\Delta N_h(T),\qquad
U_h(T)=\bar U_h+\Delta U_h(T).
\tag{TCF.9}
\]
적분은 방향을 가진다. \(c(T)<c_0\)이면 \(\Delta N,\Delta U\le0\)이며 active inventory에 같은 크기가 더해진다. 유한 이동에서 일반적으로 \(\Delta U\ne c(T)\Delta N\)다. 에너지는 실제 이관 band의 1차 모멘트를 사용한다.

모든 candidate에서
\[
N_h(T)+A_N(c(T))=\mathscr C_h,\qquad
U_h(T)+A_E(c(T))=\mathscr E_h
\tag{TCF.10}
\]
이므로 입자수·운동에너지가 정확히 보존된다. 자유전자 수의 active/thermal 배정만 바뀌고 ion charge가 같으므로 기존 charge row도 보존된다. 유한 measure에서는 (TCF.4)–(TCF.5)를 직접 사용하면 equality 소유권과 원자 질량까지 같은 증명이 성립한다.

**구현상 고정점.** 각 반복에서 (TCF.5) 또는 고정된 (TCF.7)–(TCF.9)를 다시 평가한다. 직전 반복의 \(N,U\)에 처음 \(c_0\)부터 계산한 \(\Delta N,\Delta U\)를 다시 더하지 않는다. 반복은 같은 endpoint를 찾기 위한 계산이며 물리 시간이 흐르는 일련의 재열화가 아니다.

## 3. TC2 — 연속 spectrum의 implicit EOS와 shape derivative

\(\alpha=\chi k_B\), \(I=[T_-,T_+]\subset(0,\infty)\)를 고정한다. \(\rho_h\ge0\)가 cutoff bracket \(\alpha I\)에 연속이고 유한하다고 먼저 가정한다. EOS를
\[
F_h(T)=c_vT\,N_h(T)-U_h(T)=0,\qquad
\Phi_h(T)=\frac{U_h(T)}{c_vN_h(T)}
\tag{TCF.11}
\]
로 쓴다. 움직이는 상한 적분을 미분하면
\[
N_T=\alpha\rho_h(c),\qquad
U_T=\alpha c\,\rho_h(c),
\tag{TCF.12}
\]
\[
\boxed{\quad
F_T=C_{\rm eff}=c_vN+\alpha(c_vT-c)\rho_h(c).
\quad}
\tag{TCF.13}
\]
따라서 EOS 자체의 \(c_vN\)와 달리 implicit boundary를 포함한 미분계수는 \(C_{\rm eff}\)다.

상수 \(\rho_{\max},N_{\min}>0\)를
\[
0\le\rho_h\le\rho_{\max},\qquad N_h\ge N_{\min}
\tag{TCF.14}
\]
로 선택한다. \(\chi\le3/2\)이면 \(F_T\ge c_vN_{\min}\). \(\chi>3/2\)이면
\[
F_T\ge m:=
c_vN_{\min}
-\chi(\chi-\tfrac32)k_B^2T_+\rho_{\max}.
\tag{TCF.15}
\]
양의 \(m\)과
\[
F_h(T_-)\le0\le F_h(T_+)
\tag{TCF.16}
\]
를 함께 확인하면 \(I\) 안에 정확히 하나의 근이 존재한다. 증명은 다음과 같이 직접적이다. (TCF.16)과 연속성으로 근이 적어도 하나 있다. 임의의 \(T_1<T_2\)에서
\[
F_h(T_2)-F_h(T_1)=\int_{T_1}^{T_2}F_T(s)ds\ge m(T_2-T_1)>0
\tag{TCF.17}
\]
이므로 두 개의 근은 없다. 이 증명은 \(\rho\)가 bounded piecewise continuous여서 \(F\)가 절대연속이고 같은 derivative bound가 거의 모든 점에서 성립할 때도 그대로 적용된다. 그 경우 density jump에서 고전적인 양측 shape derivative가 있다고 주장하지 않는다.

(TCF.15)는 계산하기 쉬운 충분조건이며 실제 \(F_T\)의 interval 최소값을 구하면 더 넓은 domain을 사용할 수 있다. \(N_{\rm nuc}>0\)만으로 \(\chi>3/2\)일 때의 \(C_{\rm eff}>0\)가 따라오지는 않는다. 미분계수의 양성은 cutoff density와 EOS를 함께 묶는 독립 조건이다.

Picard map의 일반 derivative와 root에서의 derivative는 각각
\[
\Phi_T(T)=
\frac{\alpha\rho_h(c)\{c-c_v\Phi_h(T)\}}{c_vN_h(T)},
\]
\[
\Phi_T(T^\star)=
\frac{\alpha\rho_h(c^\star)(c^\star-c_vT^\star)}
{c_vN_h(T^\star)}
=\left(\frac{2\chi}{3}-1\right)
 \frac{c^\star\rho_h(c^\star)}{N_h(T^\star)} .
\tag{TCF.18}
\]
\(U/N\)가 off-root에서 \(c_vT\)와 다르므로 마지막 식을 전체 interval의 derivative bound로 사용하지 않는다.

Picard convergence를 쓰려면 \(\Phi_h(I)\subseteq I\)와
\(\sup_I|\Phi_T|\le q<1\)를 확인한다. 예를 들어 \(0\le U\le U_{\max}\), \(N\ge N_{\min}\), \(c\le\alpha T_+\)이면
\[
|\Phi_T|\le
\frac{\alpha\rho_{\max}}{c_vN_{\min}}
\left(\alpha T_++\frac{U_{\max}}{N_{\min}}\right)
\tag{TCF.19}
\]
가 계산 가능한 보수적 bound다. 실제 부호와 모멘트를 쓰면 훨씬 줄어들 수 있다. \(\Phi\)의 interval image는 endpoint·piecewise stationary point 등 선택한 spectrum 표현에 맞게 확인한다. 이 두 조건 아래
\[
|T_j-T^\star|\le\frac{|\Phi_h(T_j)-T_j|}{1-q}
\tag{TCF.20}
\]
이며 반복 차이가 기하급수적으로 줄어든다. 유일근의 존재는 (TCF.15)–(TCF.16)만으로도 성립하므로 Picard가 충분히 수축하지 않을 때는 bracket을 보존하는 이분법을 사용한다.

## 4. TC3 — residual과 입력 모멘트 오차를 온도 한계로 전달

\(F_T\ge m>0\)인 위 interval에서 평균값 적분을 적용하면
\[
\boxed{\quad |T-T^\star|\le \frac{|F_h(T)|}{m}.\quad}
\tag{TCF.21}
\]
이분법의 현재 bracket \([a,b]\)와 \(T\in[a,b]\)에는 독립적으로
\[
|T-T^\star|\le\max(T-a,b-T)
\tag{TCF.22}
\]
가 성립한다. 중점에서는 우변이 \((b-a)/2\)다. 두 값의 최솟값을 certificate로 사용한다. \(F\) 평가오차가 \(|\widehat F-F|\le\eta_F\)로 따로 증명된 부동소수점 구현이라면 (TCF.21)의 분자를 \(|\widehat F|+\eta_F\)로 바꾼다. 이번 reference는 유리수 box density와 유리수 입력을 정확한 Fraction 연산으로 평가하므로 수식 평가에 관한 \(\eta_F=0\)이다. 실제 연속 물리 spectrum과의 reconstruction 차이가 0이라는 뜻은 아니다.

두 입력 데이터 \(D,\widehat D\)가 같은 bracket에서 각각 근 \(T^\star,\widehat T^\star\)를 갖고 원 데이터 \(F_D\)가 \(F'_D\ge m>0\)이면
\[
|T^\star-\widehat T^\star|
\le\frac{\sup_{T\in I}|F_D(T)-F_{\widehat D}(T)|}{m}.
\tag{TCF.23}
\]
공통 count/energy와 active-tail 모멘트 차이에 대해
\[
\sup_I|\delta F|
\le c_vT_+\bigl(|\delta\mathscr C|+\sup_I|\delta A_N|\bigr)
+|\delta\mathscr E|+\sup_I|\delta A_E|.
\tag{TCF.24}
\]
이는 \(\delta F=c_vT(\delta\mathscr C-\delta A_N)-\delta\mathscr E+\delta A_E\)를 전개하고 삼각부등식을 쓰면 얻는다. 최종 온도 오차는 근 찾기 certificate와 이 데이터 오차 bound를 더해서 전달할 수 있다. \(\mu\)를 바꾼 경우 zeroth·first total moments만 같다고 tail 오차가 자동으로 작아지지는 않는다. 실제 cutoff bracket의 tail bound가 필요하다.

이 certificate는 선택한 이산 endpoint closure의 오차다. 물리 ODE의 시간 절단오차, 누락 반응, 선택한 atomic cross-section의 불확실성까지 포함하지 않는다. 그런 오차는 이전 FEEDBACK_ERROR_MAP의 physical defect 경로 또는 별도 spectrum/predictor bound로 결속한다.

## 5. TC4 — \(h=0\) identity와 연속 moving-cutoff 식에 대한 일치

시간 폭이 0일 때 predictor가 초기 공통 inventory와 spectrum을 그대로 반환하고
\[
c_0=\alpha T_n,\qquad
\bar U_0=c_vT_n\bar N_0
\tag{TCF.25}
\]
라고 하자. (TCF.8)의 두 signed integral은 \(T=T_n\)에서 정확히 0이므로 \(F_0(T_n)=0\). \(T_n\in I\)이고 유일성 조건이 성립하면 cutoff solver의 결과는 \(T_n\)이며 count·energy·active-tail 모두 처음과 같다. 구현에서는 이 정확한 초기 근을 먼저 확인하여 불필요한 반복 없이 identity를 반환한다.

작은 \(h\)에 대해 \(\bar N_h,\bar U_h,\rho_h\)가 필요한 모멘트 의미에서 \(C^1\)이고, 초기 \(C_{\rm eff,0}>0\)라고 하자. implicit 미분 또는 (TCF.11)을 직접 미분하면
\[
T'(0)=
\frac{\bar U'_0-c_vT_n\bar N'_0}{C_{\rm eff,0}} .
\tag{TCF.26}
\]
여기서 \(\partial_h\int_{c_0}^{\alpha T_n}\rho_h\,dW=0\)이고 에너지 적분도 같으므로 초기 reference의 \(h\) 미분만 분자에 남는다. 또한
\[
N'(0)=\bar N'_0+\alpha\rho_0(c_0)T'(0),
\]
\[
U'(0)=\bar U'_0+c_0\alpha\rho_0(c_0)T'(0).
\tag{TCF.27}
\]
따라서 고정-cutoff predictor가 실제 수송의 고정 경계 미분을 제공할 때, 이 closure는 움직이는 경계의 count·energy 미분을 복원한다. \(C^1\)만으로는 \(o(h)\) remainder를 얻으며, bounded \(O(h^2)\) local remainder를 주장하려면 predictor와 implicit 자료의 국소 Lipschitz 1차 미분 또는 \(C^2\) 정칙성을 추가한다.

연속 에너지 drift의 경계값을 \(b_c=dW/dt|_{W=c}\), comoving spectral trace를 \(\rho_c\)라 하자. 하나의 연속 spectrum이면 경계의 signed thermal count source는
\[
S_c=(\alpha\dot T-b_c)\rho_c
\tag{TCF.28}
\]
다. 양쪽 표현이 다른 경우에는 기존 MC19의 상대 흐름에 따른 upwind trace를 양쪽 ledger에 공통으로 쓴다. 이때 implicit coefficient는 그 상대 흐름의 부호와 선택한 upwind trace가 고정된 branch에서 읽으며, 부호 전환에서는 trace 선택도 다시 결속한다. 다음 식은 scalar \(b_c\)가 있거나 방향을 이미 적절히 적분한 경우다. anisotropic drift에서는 \(b_c\rho_c\)를 \(\int b_c(\Omega)\rho_c(\Omega)d\Omega\)로, \(\rho_c\)를 방향 적분으로 해석한다.

Thermal regular source를 \(S_{\rm reg},Q_{\rm reg}\), prescribed expansion을 \(\theta=\dot V/V\)라 하면
\[
\dot N=S_{\rm reg}+(\alpha\dot T-b_c)\rho_c,
\]
\[
\dot U=Q_{\rm reg}+c(\alpha\dot T-b_c)\rho_c
-\frac23\theta U.
\tag{TCF.29}
\]
Comoving count이므로 별도의 \(-\theta N\) 희석항은 없다. Thermal ideal-gas pressure work는 \(-2\theta U/3\)로 남는다. \(U=c_vNT\)를 미분하고 \(\dot T\) 항을 모으면
\[
\boxed{\quad
C_{\rm eff}\dot T=
Q_{\rm reg}-c_vTS_{\rm reg}
-(c-c_vT)b_c\rho_c-\frac23\theta U .
\quad}
\tag{TCF.30}
\]
이는 기존 MC35의 implicit coefficient와 동일하다. Jump collision에서 처음부터 경계 아래로 생긴 daughter는 regular ledger에 실제 daughter energy로 들어간다. 그 daughter energy를 \(c(T)\)로 바꾸지 않는다. Drift·geometric work·source의 새 값을 매번 Picard candidate에 누적하는 것으로 (TCF.30)을 구현하지 않는다. 먼저 일관된 predictor를 만들고 같은 reference closure를 풀거나, 별도로 정의한 coupled map의 모든 data 의존성을 명시한다.

## 6. TC5 — 연속 spectrum의 정확한 가열·냉각 사례

상수 \(E_*=k_BT_*\), \(\epsilon=W/E_*\), \(\tau=T/T_*\)를 사용한다. 이 절의 \(k_B=1\) 표기는 계산에서 \(E_*/T_*\)로 무차원화한 값이다. 물리 Boltzmann 상수를 없애는 가정이 아니다. 다음 양의 고정 spectrum을 택한다.
\[
\chi=4,\qquad
\frac{dN}{d\epsilon}=\frac14\,\mathbf1_{[3,6]}(\epsilon),\qquad
c_0/E_*=4,
\]
\[
\bar N_0=2,\quad \bar U_0/E_*=3,\qquad
\mathscr C=\frac52,\quad
\mathscr E/E_*=\frac{11}{2}+\delta .
\tag{TCF.31}
\]
\(\delta E_*\)는 predictor가 unresolved base에 넣은 외부 에너지다. 그 값은 cutoff 적분으로 얻은 에너지와 따로 기록한다. 전체 spectrum count는 \(3/4\), energy는 \(27E_*/8\)이므로
\[
N_B=\frac74,\qquad U_B/E_*=\frac{17}{8}+\delta>0 .
\tag{TCF.32}
\]
예를 들어 \(N_{\rm nuc}=1\)을 선택하면 (TCF.3)을 만족한다.

\(I=[3/4,5/4]\)에서
\[
N(\tau)=1+\tau,\qquad u(\tau)=U/E_*=1+\delta+2\tau^2,
\]
\[
f(\tau)=F/E_*=
\frac32\tau-\frac12\tau^2-1-\delta,\qquad
f'(\tau)=\frac32-\tau\ge\frac14.
\tag{TCF.33}
\]
두 끝점 값은
\[
f(3/4)=-\frac5{32}-\delta,\qquad
f(5/4)=\frac3{32}-\delta .
\tag{TCF.34}
\]
따라서 \(-5/32\le\delta\le3/32\)이면 양의 유일근과 정확한 slope certificate가 있다. Picard 식도
\[
\phi(\tau)=\frac{1+\delta+2\tau^2}{(3/2)(1+\tau)},\qquad
\phi'(\tau)=\frac43-\frac{2(3+\delta)}{3(1+\tau)^2}
\tag{TCF.35}
\]
로 닫힌다. 이 직사각형에서 \(0<\phi'\le233/243<1\). endpoint 부호와 단조성이 \(\phi(I)\subseteq I\)를 주므로 이 사례는 Picard도 수축한다. 실제 exact reference 구현은 큰 rational numerator/denominator를 피하기 위해 중점 이분법을 사용한다.

| predictor energy \(\delta\) | \(\tau^\star\) | \(N^\star\) | \(U^\star/E_*\) | signed \(\Delta N\) | signed cutoff \(\Delta U/E_*\) |
|---|---:|---:|---:|---:|---:|
| \(2/25\) | \(6/5\) | \(11/5\) | \(99/25\) | \(1/5\) | \(22/25\) |
| \(-3/25\) | \(4/5\) | \(9/5\) | \(54/25\) | \(-1/5\) | \(-18/25\) |
| \(0\) | \(1\) | \(2\) | \(3\) | \(0\) | \(0\) |

가열과 냉각의 transfer 크기는 같지 않다. 에너지 band가 서로 다르기 때문이다. 각 행에서 thermal과 active를 합하면 동일 predictor의 \(\mathscr C,\mathscr E\)로 정확히 돌아간다. 냉각 행은 \(c_0\) 아래의 \([3,4]\) band를 실제로 보존했기 때문에 정의된다.

## 7. TC6 — 원자 measure의 유한 root 구성과 실제 격자 연결

실제 kernel이 에너지 node별 packet count를 제공하면
\[
\mu=\sum_{j=1}^{M}n_j\delta_{w_j},\qquad
0\le w_1<\cdots<w_M,\quad n_j>0
\tag{TCF.36}
\]
로 직접 사용한다. 같은 에너지 node는 먼저 묶는다. \(N_B\ge N_{\rm nuc}>0,\ U_B>0\)라 하자. 첫 \(k\)개 node가 thermal인 branch의 수·에너지·온도는
\[
N_k=N_B+\sum_{j\le k}n_j,\qquad
U_k=U_B+\sum_{j\le k}w_jn_j,\qquad
T_k=\frac{U_k}{c_vN_k}.
\tag{TCF.37}
\]
이 branch는 정확히
\[
w_k\le\alpha T_k<w_{k+1}
\tag{TCF.38}
\]
일 때 consistent하다. \(k=0\)에는 아래쪽 조건이 없고, \(k=M\)에는 위쪽 조건이 없다. equality는 thermal 소유라는 (TCF.4)의 규약과 같다.

**직접 구성 1.** \(M+1\)개의 (TCF.37)을 계산하고 (TCF.38)을 검사하면 모든 consistent scalar root를 유한하게 얻는다. 총 count와 energy가 양수인 것만으로 임의의 \(\chi>0\)에 대해 branch의 유일성을 선언하지 않는다. 결과가 여러 개이면 root set과 선택한 continuation index를 별도로 반환한다.

**직접 구성 2.** \(\alpha\ge c_v\), 즉 \(\chi\ge3/2\)이면 양의 branch의 존재를 더 직접적으로 보일 수 있다. \(k=0,\ T_0=U_B/(c_vN_B)>0\)에서 시작한다. 다음 node가 \(w_{k+1}\le\alpha T_k\)이면 포함하고 \(k\)를 1 증가시킨다. 포함 뒤
\[
T_{k+1}
=\frac{N_kT_k+n_{k+1}w_{k+1}/c_v}{N_k+n_{k+1}}
\tag{TCF.39}
\]
는 \(T_k\)와 \(w_{k+1}/c_v\)의 양의 가중평균이다. 두 값 모두 \(w_{k+1}/\alpha\) 이상이므로 \(\alpha T_{k+1}\ge w_{k+1}\). 따라서 새 node와 모든 낮은 node가 계속 thermal 조건을 만족한다. 다음 node가 cutoff 위에 있거나 \(k=M\)이면 멈추며 (TCF.38)이 완성된다. index가 한 번에 1씩 증가하므로 최대 \(M\)번 만에 종료한다. **온도 자체의 단조증가는 이 증명에 필요하지 않다.**

이 구성이 실제 finite energy grid에 바로 적용되는 이유는 packet을 연속 밀도로 바꾸지 않고 그 count와 실제 energy를 그대로 (TCF.37)에 쓰기 때문이다. 사건 adapter가 보존한 binding/radiation/charge ledger에 대해 cutoff 단계는 다음 변환만 수행한다.
\[
(A_j,N_{\rm th},U_{\rm th})
\longmapsto
(A_j-\xi,\ N_{\rm th}+\xi,\ U_{\rm th}+w_j\xi)
\tag{TCF.40}
\]
또는 그 역변환. 실제 common inventory에서 packet 소유권을 바꾸므로 \(\xi\)는 해당 resolved packet count를 넘지 않는다. \(w_j\)가 실제 node energy라는 점이 보존을 만든다.

활성 node를 thermal로 편입하면서 underlying \((w_j,n_j)\)와 ownership 정보를 모두 삭제했다면 역변환을 재구성할 수 없다. 실제 adapter의 downward 경로에는 lower packet inventory를 retained closure state로 남기는 계약이 필요하다. 새로운 충돌이 packet weights나 energies를 바꾼 arbitrary endpoint에는 (TCF.37)–(TCF.38)을 다시 적용하고, 이전 branch와의 선택 정책을 별도로 결속한다. 다음 절의 monotone energy continuation 정리를 임의의 spectrum 변경에도 그대로 적용하지 않는다.

## 8. TC7 — 원자 branch의 가열·냉각 continuation과 \(h=0\) identity

초기 원자 measure·\(N_B\)·\(\alpha\ge c_v\)를 고정하고, consistent index \(k_n\)가 주어졌다고 하자. predictor가 base energy만
\[
U_B^+=U_B+\Delta U_B>0
\tag{TCF.41}
\]
로 바꾸는 경로를 고려한다. 각 candidate는 **같은 \(U_B^+\)와 고정 prefix moments**로 다시 계산한다.

가열 \(\Delta U_B\ge0\)에서는 \(k=k_n\)에서 시작하여, 다음 node가 \(w_{k+1}\le\alpha T_k^+\)인 동안 포함한다. 첫 candidate 온도는 초기보다 크거나 같아서 원래 thermal prefix의 아래쪽 조건이 유지된다. 이후에는 (TCF.39)의 가중평균 증명으로 새 prefix의 아래쪽 조건이 유지된다. 멈추면 위쪽 조건도 만족하므로 consistent branch다. 최대 \(M-k_n\)번의 편입으로 끝난다.

냉각 \(\Delta U_B<0\)에서는 \(k=k_n\)에서 시작하여, 가장 높은 thermal node가 \(w_k>\alpha T_k^+\)인 동안 제거한다. \(\alpha\ge c_v\) 때문에 \(w_k>c_vT_k^+\). 제거 뒤
\[
T_{k-1}^+-T_k^+
=\frac{n_k(c_vT_k^+-w_k)}{c_v(N_k-n_k)}<0 .
\tag{TCF.42}
\]
\(N_k-n_k\ge N_B>0\)이며 \(U_{k-1}^+=U_B^++\sum_{j<k}w_jn_j>0\)이므로 positivity도 유지된다. 기존 active node와 방금 제거한 node는 낮아진 cutoff보다 위에 남는다. 아래쪽 조건이 다시 만족되면 멈추고, 최대 \(k_n\)번 제거로 consistent branch를 얻는다.

\(\Delta U_B=0\)이면 최초 consistent prefix에서 어떤 node도 옮기지 않는다. 따라서 atomic map도 \(h=0\)에서 identity다. 초기 stored ownership이 equality 규약을 어기지 않아야 한다. 한 node를 threshold에서 두 집단에 중복 배정하지 않는다.

이 절은 명시된 branch continuation의 finite 존재·positivity·보존·종료를 증명한다. 그 결과가 모든 algebraic branch 중 유일하다는 주장은 아니다. \(\chi>3/2\)이면 원자를 포함하는 순간 유한한 온도 점프가 생길 수도 있다. \(T_-=w/\alpha\)에서 count \(n\)를 편입할 때
\[
T_+-T_-=
\frac{nw}{N+n}\left(\frac1{c_v}-\frac1\alpha\right)>0
\tag{TCF.43}
\]
이므로 이 crossing에 연속 spectrum의 classical \(C_{\rm eff}\)나 시간 \(C^1\) 정리를 적용하지 않는다. \(\chi=3/2\)에서는 이 특정 threshold jump가 0이지만, branch 변경은 여전히 별도로 처리한다. 이전 branch를 유지하는 정책과 단순 \(k=0\) 존재 scan은 서로 다른 정책이며, arbitrary endpoint가 여러 root를 가질 때 자동으로 같은 root를 고르는 것으로 취급하지 않는다.

### 실제 finite scan을 확인할 작은 exact inventory

\(k_B=1\)로 무차원화하고 \(c_v=3/2,\chi=4\)를 둔다.
\[
N_B=10,\quad U_B=15,\quad
(w_j,n_j)=(5,1),(9,1),(30,1),\quad k_n=0 .
\tag{TCF.44}
\]
초기 \(T=1,\ c=4\)로 모든 node가 active다. \(\Delta U_B=135\)이면 같은 fixed prefix에서
\[
k:0\to1\to2\to3,\qquad
T:10\to\frac{310}{33}\to\frac{82}{9}\to\frac{388}{39}.
\tag{TCF.45}
\]
앞의 두 편입에서 온도가 내려가도 다음 node와의 threshold 조건 및 termination은 유지된다. 최종 \(N=13,\ U=194,\ c=1552/39>30\)이다. 이 inventory에서 다시 \(-135\)만큼 base energy를 줄이면
\[
k:3\to2\to1\to0,\qquad
T:\frac{118}{39}\to\frac{29}{18}\to\frac{40}{33}\to1 .
\tag{TCF.46}
\]
최종 thermal \(N=10,U=15\), active count \(3\), active energy \(44\)로 돌아간다. 각 candidate는 그 가열 또는 냉각 단계의 고정 common total을 정확히 보존한다. 특정 이 사례의 복귀가 일반 branch hysteresis의 부재를 뜻하지는 않는다.

## 9. 구현, 검증 범위와 다음 결속

thermal_cutoff_solver.py는 다음 좁은 reference를 제공한다.

1. 비음성 rational box spectrum의 exact zeroth·first tail moments와 고정 common-inventory EOS.
2. 각 box 경계로 bracket을 나눈 뒤 piecewise-affine \(F_T\)의 끝점 값을 정확 계산하여 \(m>0\)를 확인하는 bounded bisection. 공급한 값이 맞다고 가정하는 일반 slope oracle이 아니라, 이 finite box 표현 자체에서 계산한 bound다.
3. 고정 원자 inventory의 모든 threshold branch 열거와 pure base-energy update의 finite continuation scan.

이분법은 최대 반복 수, 현재 bracket, signed EOS residual과 온도 certificate를 반환한다. 최대 반복 수를 소진하면 미수렴 상태를 그대로 기록한다. 음수 clipping, projection, epsilon 온도 치환은 사용하지 않는다. 원자 scan은 정렬된 prefix를 한 번 만들고 finite index를 움직여 원래 reference에서 candidate를 평가한다.

새 checks/run_thermal_cutoff_checks.py는 위 두 대표 구성의 **구현 연결**만 검사한다. 연속 exact heating/cooling 및 \(h=0\), 미수렴 반환, 기록한 모든 근 찾기 candidate의 보존과 certificate를 확인하고, 원자 가열·냉각 및 branch 분류·고정 prefix 보존을 확인한다. 소스 SHA256·입력·runtime·실제 결과를 results/THERMAL_CUTOFF_CHECKS.json에 기록한다. 이 검사는 물리 ODE 적분, cross-section qualification, NCP 실행 또는 이미 완료한 이전 suite의 재실행을 포함하지 않는다.

이전 event-capacity 피드백과 합성할 때 raw endpoint는 매번 같은 \(y_0\)에서 \(y(z)=y_0+S\xi(z)\)로 만든다. 초기 donor와 active mask는 \(E_c^n\)의 초기 support에 고정하고, lower-band atoms는 역경계에 사용할 retained inventory로 둔다. 현재 에너지 node \(w_j\)와 원자 prefix \(k\)가 고정된 branch에서 사건별 thermal 모멘트 열은
\[
\nu_{N,r}=s_{N_B,r}+\sum_{j\le k}s_{A_j,r},\qquad
\nu_{U,r}=s_{U_B,r}+\sum_{j\le k}w_js_{A_j,r}
\tag{TCF.47}
\]
다. \(\partial_z\)를 선택한 scalar parameter 또는 정규화된 한 방향의 미분으로 읽고, \(|\partial_z\xi_r|\le M_r\), \(C_{\rm eff}\ge m>0\)이면 implicit 미분으로
\[
|\partial_zT|\le
\frac{\sum_r\sup_I|\nu_{U,r}-c_vT\nu_{N,r}|\,M_r}{m}.
\tag{TCF.48}
\]
이 식은 fixed initial reference를 사용하는 outer map의 온도 sensitivity에 연결한다. 연속 spectrum에서는 candidate에 따른 spectral shape의 미분도 같은 분자에 포함해야 하고, 원자 branch를 넘을 때는 (TCF.48)을 그대로 연장하지 않는다. Coupled event map의 rate-domain·미분상수·self-map 조건은 그 outer map에 따로 결속한다. 이 문서의 scalar cutoff 해가 모든 coupled reaction-temperature 문제의 전역 유일성을 보장하는 것으로 해석하지 않는다.

최종 응용에는 실제 kernel endpoint spectrum과 그 retained lower inventory, predictor의 physical defect bound, cutoff parameter \(\chi\), domain 또는 선택 branch, 관측량 오차 예산을 결속해야 한다. 연속 reconstruction을 채택하면 root residual과 별도로 (TCF.24)의 tail representation error를 관리한다. 원자 표현을 유지하면 실제 packet energy와 ownership을 보존하고 crossing을 branch event로 기록한다.

