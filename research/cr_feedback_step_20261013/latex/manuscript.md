# 이번 연구에서 완성한 것

이번 연구는 직전 DAG의 **온도·H/He 조성 피드백을 포함하는 양의 보존적 한 step**을 구성했다. 사건마다 하나의 공통 extent를 사용하고, 같은 저장고를 소비하는 모든 사건의 부하를 분모에 공유한다. 이 map의 각 반복 단계에서 비음성과 핵수·전하·총 에너지가 유지된다. 여기에 온도와 조성에 따라 변하는 반응 계수를 넣고, 정의역의 보존·고정점 존재·수렴·온도 오차까지 유도했다.

연구 단위는 **CR-THEORY-FEEDBACK-20261013**이다. 날짜는 2026년 10월 13일 KST이며, 실제 작업 기록의 UTC 날짜는 2026년 10월 12일이다. 요청한 SciSpace와 Exa를 사용해 가까운 원전 네 편을 비교했고, Wolfram Language와 xAct로 공변 텐서 식 및 정확한 유리수 사례를 실제 계산했다.

이 결과의 대상은 현재 사건 열과 각 열의 실제 에너지가 고정된 유한 collision stage이다. 반응 계수의 온도·조성 의존성은 그 stage의 endpoint와 자기일관적으로 갱신된다. 주어진 Bianchi I geometry와의 합성에는 동일한 packet 상태를 만드는 angular lift와 에너지 장부를 명시했다. 가정은 다음 절과 CONTRACT.json에 모았다.

## 결과 지도

| 결과 | 완성한 내용 | 본문의 근거 |
|---|---|---|
| FB1 | 공통 사건 extent의 양수성·보존량과 양의 재고 하한 | ES-A/ES-B, FP1 |
| FB2 | 12개 상태·10개 사건의 H/He family와 유한 EOS | 사건 구성의 H/He 표 |
| FB3 | 양의 온도 정의역, 존재, 계산 가능한 수축 조건 | FP2–FP3 |
| FB4 | 반복·계수 근사·실제 시간 오차의 온도 전달 | FP4, FP6 |
| FB5 | 실제 반응 ODE에 대한 일차 일관성과 나머지 상계 | FP5 |
| FB6 | 공변 투영, Bianchi momentum/thermal map과 Lie step | CG.1–CG.11 |
| FB7 | 중성 비선형 사례의 정확한 endpoint와 실행 가능한 반복 | FP7, driver 검산 |

핵심 계산식은 다음과 같다. $S_{ir}$는 사건 하나가 상태 $i$에 주는 증분, $f_r(z;y^n)$는 초기 donor와 trial endpoint 계수로 평가한 비음 반응률이다.

$$
C_{ir}=(-S_{ir})_+,\qquad
c_i(z)=\sum_r C_{ir}f_r(z),\qquad
d_r(z)=\sum_{i:C_{ir}>0}\frac{c_i(z)}{y_i^n},
$$

$$
\boxed{
\xi_r(z)=\frac{h f_r(z)}{1+h d_r(z)},\qquad
\Phi_h(z)=y^n+S\xi(z).
}
$$

초기에 0인 저장고를 소비하는 사건은 그 step에서 비활성화한다. 활성 사건은 각 소비 저장고의 총 부하를 공유하므로

$$
\sum_r C_{ir}\xi_r
\le\frac{h c_i}{1+h c_i/y_i^n},\qquad
[\Phi_h(z)]_i\ge\frac{y_i^n}{1+h c_i/y_i^n}>0
$$

를 만족한다. 임의의 보존 행 $\ell^TS=0$에는 $\ell^T\Phi_h=\ell^Ty^n$이 성립한다. 따라서 수렴 전 iterate도 동일한 물리 장부 안에 머문다.

# 현재 가정과 재사용한 근거

## 물리적 상태와 closure

공행 셀의 수 상태는 active 전자, H/He 원자·이온, thermal 전자를 구분한다. 에너지 상태는 thermal kinetic energy $U$, 현재 active packet의 실제 kinetic energy, 원자의 누적 ionization energy, 방출 복사 에너지를 함께 센다. Thermal EOS는

$$
T=\frac{U}{c_v(N_H+N_{He}+N_{e,\mathrm{th}})},\qquad
c_v=\frac32k_B
$$

다. 열적 원자핵 수 $N_H+N_{He}>0$는 이 EOS의 양의 분모 하한이다. Active 전자는 자신의 에너지와 입자수 상태에 유지한다.

이번 H/He 예시는 ground-state family와 무거운 원자핵의 반동 에너지 생략을 사용한다. Recombination은 양의 고정 captured-energy node로 분해하고 그 rate weight에 온도 의존성을 넣는다. 이 표현 덕분에 동일 사건 열이 kinetic, chemical, radiation 장부를 정확히 연결한다. 표의 무차원 유리수 검산 입력은 이 구조를 판별하기 위한 것이다.

계수에 저온 특이성이 있으면 양의 초기 열에너지 $U^n$에서 온도 하한을 구성한다. Coulomb-log 형태를 사용하는 경우에는 지정한 $0<n_{\rm lo}\le n\le n_{\rm hi}<C^2$의 양의 구간과 실제 count functional, 부피, 미분 상계를 함께 결속한다. 이 조건은 정칙한 일반 계수에 필요한 가정과 구별해 본문에 기록했다.

Geometry에는 metric $(-,+,+,+)$, 주어진 양의 diagonal scale factor, 초 단위 고유시간을 사용한다. Thermal sector는 유지된 등방 단원자 ideal-fluid closure로 운반하고, active sector는 실제 비등방 응력과 운동량을 운반한다. $c$와 $k_B$는 계산식에 남겨 두었다. 현재 collision의 angular chart는 초기 packet 상태를 그대로 표현하고, 연속 collision field와 이산 map에 동일하게 사용한다.

## 직전 루프에서 유지한 결과

직전의 과학 commit은 \texttt{2495662e86a69ed822ec192685c3e9e0e68e1255}이며, 확인한 branch head는 \texttt{3bac8c6d00da0ae2eabc3cb7ba16acd64ec1c54e}다. 그 단계의 proof·코드·결과 중 이번 유도에 필요한 8개 과학 파일의 SHA-256을 원 근거와 대조해 재사용했다.

| 재사용한 결과 | 이번 사용 |
|---|---|
| 이동 cutoff의 signed number·energy moment | Geometry 후 실제 packet energy의 thermal 편입 |
| Thermal/all-free 표현의 정확한 동치 | Active와 thermal count의 EOS 소유권 |
| 유한 입자 편입의 EOS | Impact·재결합·terminalization의 온도 갱신 |
| 상태·에너지·입자수 오차의 온도 전달 | FP4와 FP6의 온도 certificate |
| 실제 Coulomb 밀도 변화의 분해 | 양의 density domain과 rate perturbation 연결 |
| 충돌 시계 및 prescribed expansion | 현재 고유시간 반응률과 geometry의 연결 |

현재 결과는 위 증명을 다시 실행하지 않고 새로운 nonlinear 연결을 유도한 것이다. 동일 identity를 가진 이전 과학 검산의 재실행은 0회다. 전체 이력과 정확한 파일 대응은 inputs/PRIOR_REUSE.json 및 원 단위의 HANDOFF.json에 있다.

# 피드백을 닫는 계산 절차

입력은 현재의 사건 열 $S$, 보존 행, 초기 상태, 부피와 고유시간 step, 계수 evaluator 및 유효 정의역이다. 이 자료에서 각 계수의 상계와 미분 상계를 구한 뒤 다음 순서로 계산한다.

1. 보존된 핵수·전하·에너지로 상태와 thermal count의 유한 상계를 구한다.
2. $T_{\rm floor}=U^n/(2c_vN_{\max})$와 $T_{\rm ceil}=E_{\rm tot}/(c_vN_{\min})$로 coefficient domain을 구성한다.
3. $h\overline c_U\le U^n$를 만족시켜 thermal energy가 $U^n/2$ 이상 남게 한다.
4. EOS, fraction, density의 변화에서 rate Lipschitz 상계를 계산하고 본문의 $q<1$ 조건으로 step을 정한다.
5. 초기 상태에서 $\Phi_h$를 반복하고, 실제 반환 상태의 residual을 새로 평가해 온도 허용오차를 확인한다.
6. 실제 ODE의 endpoint defect도 평가할 경우, FP6의 재구성 적분으로 시간 이산화까지 포함한 온도 오차를 얻는다.

$z$에서 측정한 residual을 $\rho=\|\Phi_h(z)-z\|_{\infty,a}$라 하면 이산 endpoint까지의 오차는

$$
\|y^\star-z\|_{\infty,a}\le\frac{\rho}{1-q}
$$

다. 실제 연속 반응계의 endpoint에는 별도로

$$
D_{\rm end}
=\left\|\frac{z-y^n}{h}-G(z,t_n+h)\right\|_{\infty,a}
$$

를 사용한다. FP6은 $D_{\rm end}$와 상태·시간 Lipschitz 상계에서 실제 한 step 오차를 직접 구성한다. 두 식은 구현의 서로 다른 출력 필드에 대응한다.

# 정확한 비선형 사례와 해석

전하 중성인 hydrogen 사례에서 active 전자 하나의 kinetic energy를 $4E_0$, ionization threshold를 $E_0$로 둔다. 사건과 초기 상태는

$$
A(4E_0)+H^0\longrightarrow H^++2e_{\rm th},
\qquad \Delta U=3E_0,
$$

$$
(A,H^0,H^+,N_e,U/E_0)^n=(1,1,1,0,1)
$$

다. Extent $x$에 대해 $\vartheta=c_vT/E_0=(1+3x)/(2+2x)$이고, 온도와 ion fraction에 의존하는 계수를 선택하면 proposal이 $f/\kappa_0=(3+5x)/2$로 단순해진다. $\eta=h\kappa_0=4/17$에서

$$
\boxed{
x^\star=\frac14,\qquad
\frac{c_vT^\star}{E_0}=\frac7{10},\qquad
q=\frac{170}{841}.
}
$$

최종 상태는 $(3/4,3/4,5/4,1/2,7/4)$다. 전체 에너지는 처음과 같은 $6E_0$, 전하는 0이다. 실제 연속 질량작용률을 같은 endpoint에서 평가하면 extent defect는 $-17\kappa_0/128$이다. 이 값은 이산 고정점의 정확한 해를 구한 뒤에도 시간 이산화의 잔차를 정량적으로 계산할 수 있음을 보여 준다.

![정확한 feedback map과 같은 extent가 연결하는 energy 장부. 점은 x=1/4의 정확한 고정점이다.](../figures/feedback_construction.pdf)

Reference driver는 이 사례를 SI $k_B$를 유지한 $E_0=(3/2)k_B(1\,\mathrm K)$로 실행했다. 15회의 accepted update, 16회의 map 평가 후 다음 결과를 얻었다.

| 항목 | 실제 결과 |
|---|---:|
| 정확한 해에 대한 온도 오차 | $6.290324474015892\times10^{-14}\,\mathrm K$ |
| 반환한 온도 오차 상계 | $2.31157671764639\times10^{-13}\,\mathrm K$ |
| 종료 허용오차 | $10^{-12}\,\mathrm K$ |
| 검사한 방문·인증 상태 | 17개 |
| 각 상태의 핵수·전하·에너지 잔차 | 정확히 0 |

Fraction 계산으로 위 상계를 유리수 그대로 보존했다. 별도 제한 종료 사례에서는 한 번의 update만 허용해, 양의 상태와 보존량을 유지하면서 \texttt{MAX\_ITERATIONS}와 실제 오차 상계를 반환했다.

# 전체 유도

다음 세 장은 공통 사건 구성, nonlinear feedback의 정리, 공변 geometry 연결의 전체 유도다. 정리의 조건·계산식·유효범위와 구현 대응을 포함한다.


\clearpage

# 공통 사건 증분을 사용하는 H/He–active–thermal 보존 step

단위: CR-THEORY-FEEDBACK-20261013. 이 문서는 채택된 TH1–TH7의 수·에너지 회계에서
온도·조성 피드백에 사용할 실제 반응 step을 구성한다. 근거 상태는 **직접 유도**다.
유한 에너지 채널의 reference implementation과 정확 유리수 검산은 별도 파일에 결속한다.

## 현재 가정과 구성의 목표

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

## 상태와 보존 행

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

## 고정 에너지 열을 갖는 실제 H/He 사건 family

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

## 고정 column과 상태 의존 계수의 분리

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

## 공유 소비량에 의한 extent의 명시적 구성

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

## 정확도와 공유 반응물의 실제 예

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

## 구현과 검증 연결

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



# 온도·H/He 조성 피드백의 유한 사건 step: 존재, 수렴, 온도 오차

연구 단위: CR-THEORY-FEEDBACK-20261013. 직접 유도 담당: /root/feedback_fixed_point.

근거 상태: 이 문서의 FP1–FP7은 명시된 유한 반응 모형에 대한 직접 유도다. 실행 검산과 독립 심사 상태는 별도 결과 파일에 기록한다. 기존 CR-THEORY-THERMAL-EVOLUTION-20261012의 thermal/all-free 항등식 T.7–T.11, 유한 열적 편입 T.14 및 EOS 오차식 T.18을 재사용한다.

## 상태, 반응, 실제 연속 방정식

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

## 하나의 사건 extent로 모든 저장고를 갱신

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

## 특이한 온도 계수까지 포함하는 계산 가능한 정의역

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

## 계수로부터 고정점 수렴상수를 계산

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

## 반복 중단 오차와 계수 근사 오차를 온도로 전달

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

## 실제 연속 반응계의 상수도 coefficient 자료로 계산

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

## Frozen donor와 capacity factor의 시간 일관성

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

## 실제 endpoint defect에서 물리적 온도 오차로 가는 증명

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

## Prescribed expansion과의 연결

이 문서의 finite step은 고정 사건 열을 사용하는 collision substep이다. 동일한 prescribed 부피 이력의 순수 열적 geometric substep에는 기존 T.15에서

$$
U^+=\gamma U^-,\qquad N^+=N^-,\qquad
\gamma=\left[\frac{V^+}{V^-}\right]^{-2/3}>0
\tag{FP.43}
$$

를 쓴다. 따라서 두 collision endpoint 사이의 온도 오차는 이 후속 substep에서 정확히 $\gamma$배가 된다. 이 단계의 thermal pressure work는 $U^--U^+$로 동일 장부에 넣는다.

실제 collision–geometry 결합의 시간 이산화에는 선택한 splitting 또는 전체 재구성의 residual을 사용한다. (FP.41)을 전체 bounded finite vector field에 적용할 경우에는 geometric 항과 그 시간 의존성을 $G,L_G,L_{G,t}$에 함께 넣는다. Active 전자의 비등방 압력 일은 기존 모멘트 계약을 따르며 thermal scalar 식으로 치환하지 않는다.

## FP7: 전하 중성인 정확한 비선형 feedback 구성 사례

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

## 계산 계약과 다음 연결

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



# 공변 에너지·입자수 투영에서 Bianchi I 기하 substep까지

단위: CR-THEORY-FEEDBACK-20261013. 이 문서는 앞선 TH1–TH7의 모멘트 회계와
이번 공통 사건 extent를 주어진 Bianchi I 배경의 실제 시간 step으로 연결한다.
아래 항등식과 유한 map의 근거 상태는 **직접 유도**다.
공변 tensor identity의 xAct 실행과 판정은 root가 작성하는 검산 기록에 따로 결속한다.

## 가정, 시간, tensor의 차원

Metric signature는 $(-,+,+,+)$다. 미래 방향 단위 시간꼴 벡터를 $n^a$라 두고

$$
n^an_a=-1,\qquad
h^{ab}=g^{ab}+n^an^b,\qquad h^a{}_bn^b=0
$$

를 사용한다. 에너지 밀도와 압력은 모두 J m$^{-3}$다.
공행 기준계에서 energy flux가 0인 물질 tensor를

$$
T^{ab}=\rho n^an^b+p h^{ab}+\pi^{ab}
=(\rho+p)n^an^b+p g^{ab}+\pi^{ab}
$$

로 분해한다. $\pi^{ab}$는 대칭이고 $n_a\pi^{ab}=0$,
$g_{ab}\pi^{ab}=0$이다. Active 분포는 운동량 반전 대칭으로 구현하며,
그 짝대칭 안에서 방향 비등방성과 shear stress를 유지한다.

길이 차원의 방향 미분과 팽창을
$D_n=n^a\nabla_a$, $\Theta=\nabla_an^a$로 정의한다.
물리적 고유시간 미분은 $\dot F=cD_nF$이며,
$\theta=c\Theta$는 s$^{-1}$다. 일반적으로 $n^a$가 좌표기저에서
무차원 성분만 갖는다고 가정하지 않고 $n^an_a=-1$의 tensor 정의를 사용한다.
아래 Bianchi 좌표에서는 $t$를 초 단위 고유시간으로 선택한다.

배경은 주어진 양의 $C^1$ 함수 $a_i(t)$의 diagonal Bianchi I다.
기하 부분 step 동안 electromagnetic force, collision, 외부 source 및 공간 비균질 flux를
생략한다. Thermal sector에는 매 시각 등방인 비상대론적 단원자 이상유체 closure,
즉 $\pi_{\rm th}^{ab}=0$를 적용한다.
그 closure는 자유 비행하는 thermal 분포 대신 thermal bath를 진화시키는 정의다.

## 에너지 투영을 직접 전개하기

곱의 미분과 $n_bn^b=-1$을 사용하면

$$
\begin{aligned}
-n_b\nabla_a[(\rho+p)n^an^b]
={}&D_n(\rho+p)+(\rho+p)\Theta\\
 &-(\rho+p)n^an_b\nabla_an^b.
\end{aligned}
$$

정규화의 미분으로 $n_b\nabla_an^b=0$이므로 마지막 항은 0이다.
Metric compatibility에서

$$
-n_b\nabla_a(p g^{ab})=-D_np.
$$

또한 $n_b\pi^{ab}=0$을 미분하면

$$
-n_b\nabla_a\pi^{ab}
=\pi^{ab}\nabla_an_b.
$$

세 식을 합하여

$$
\boxed{
-n_b\nabla_aT^{ab}
=D_n\rho+(\rho+p)\Theta+\pi^{ab}\nabla_an_b
}
\tag{CG.1}
$$

을 얻는다. 이 항등식은 energy flux가 0인 위 tensor 분해와 정규화만 사용한다.

가속도 $a_b=n^c\nabla_cn_b$,
projected symmetric trace-free derivative $\bar\sigma_{ab}$와
projected antisymmetric derivative $\bar\omega_{ab}$를 사용하면

$$
\nabla_an_b=-n_aa_b+\frac13\Theta h_{ab}
+\bar\sigma_{ab}+\bar\omega_{ab}.
$$

$\pi^{ab}$의 공간성·무흔적성·대칭성 때문에

$$
\pi^{ab}\nabla_an_b=\pi^{ab}\bar\sigma_{ab}.
$$

물리적인 shear를 $\sigma_{ab}=c\bar\sigma_{ab}$,
four-force/source density를 $F^b=\nabla_aT^{ab}$,
고유시간당 energy source를 $Q=-c n_bF^b$로 정의한다.
그러면 $c$를 복원한 energy balance는

$$
\boxed{
\dot\rho+(\rho+p)\theta+\sigma_{ab}\pi^{ab}=Q.
}
\tag{CG.2}
$$

모든 항의 차원은 J m$^{-3}$ s$^{-1}$다.
$c$는 $D_n$, $\Theta$, $\bar\sigma$의 길이 차원에서 물리적 시간 차원으로
변환하는 곳에 각각 한 번 들어간다. 따라서 이미 고유시간으로 정의한
$\theta,\sigma_{ab}$나 반응률에는 추가적인 $1/c$를 넣지 않는다.

## 공행 입자수 current와 부피

종 $s$의 proper number density를 $n_s$라 하고,
물리적 particle current를 $J_s^a=c n_s n^a$로 둔다.
그 발산은

$$
\nabla_aJ_s^a
=cD_nn_s+c n_s\Theta
=\dot n_s+\theta n_s.
$$

고유시간·고유부피당 source를 $S_s$로 정의하면

$$
\boxed{
\dot n_s+\theta n_s=S_s,\qquad
\frac{dN_s}{dt}=V S_s,\qquad N_s=Vn_s,\quad \frac{\dot V}{V}=\theta.
}
\tag{CG.3}
$$

이는 단위벡터 current $\widehat J_s^a=n_s n^a$를 사용할 때의
$c\nabla_a\widehat J_s^a=S_s$와 동치다.
에너지와 입자수 source의 time adapter가 같은 고유시간을 참조한다.

균질 셀에서는 서로 마주 보는 면을 통한 공간 flux가 상쇄된다.
기하 부분 step의 $S_s=0$이면 각 공행 입자수 $N_s$가 보존된다.
종별 ionization과 active–thermal 교환은 별도 collision 사건에서
같은 extent로 처리한다.

## Diagonal Bianchi I의 실제 tetrad와 보존 운동량

좌표 metric을

$$
ds^2=-c^2dt^2+\sum_{i=1}^3a_i(t)^2(dx^i)^2,\qquad a_i(t)>0
\tag{CG.4}
$$

로 쓰고

$$
n=\frac1c\partial_t,\qquad
e_{\hat i}=\frac1{a_i}\partial_i
$$

를 선택한다. 이 공행 congruence는 측지선이며 vorticity가 0이다.
고정 좌표 셀 부피 $V_c$에 대해

$$
V(t)=V_c a_1a_2a_3,\qquad
H_i=\frac{\dot a_i}{a_i},\qquad
\theta=\sum_iH_i,\qquad H=\frac13\theta,
$$

$$
K_{\hat i\hat j}=H_i\delta_{ij},\qquad
\sigma_{\hat i\hat j}=(H_i-H)\delta_{ij}.
$$

여기서 $K$와 $\sigma$의 단위는 s$^{-1}$이며,
고유시간 tensor shear와 (CG.2)의 정의가 일치한다.
정의에 $H^{-1}$이나 $\theta^{-1}$가 들어가지 않는다.

각 $\partial_i$는 Killing vector다.
전자 four-momentum의 covariant spatial component를 $P_i$라 하면,
측지선 방정식과 Killing identity로

$$
P^a\nabla_a(P_b\zeta_{(i)}^b)
=\zeta_{(i)}^bP^a\nabla_aP_b
+P^aP^b\nabla_{(a}(\zeta_{(i)})_{b)}=0,
\qquad \zeta_{(i)}=\partial_i
$$

이다. 미래 방향 궤적의 $t$는 단조이므로

$$
\frac{dP_i}{dt}=0.
$$

동일한 결과는 좌표 Hamiltonian

$$
\mathcal H(t,\boldsymbol P)
=\sqrt{m_e^2c^4+c^2\sum_i\frac{P_i^2}{a_i(t)^2}}
$$

에서 $\dot P_i=-\partial\mathcal H/\partial x^i=0$으로도 얻는다.
물리적 직교기저 운동량은 $p_{\hat i}=P_i/a_i$이므로

$$
\boxed{
p_{\hat i}^{+}
=\frac{a_i(t_n)}{a_i(t_{n+1})}p_{\hat i}^{n},
\qquad
\dot p_{\hat i}=-H_i p_{\hat i}.
}
\tag{CG.5}
$$

이다. 이 유한 map은 주어진 $a_i$의 양의 endpoint 값만으로 평가된다.

## 상대론적 active energy와 pressure work

전자 kinetic energy, total energy 및 물리적 3-velocity는

$$
W(\boldsymbol p)
=\sqrt{m_e^2c^4+c^2|\boldsymbol p|^2}-m_ec^2,\qquad
\mathcal E_p=W+m_ec^2,\qquad
v_{\hat i}=\frac{c^2p_{\hat i}}{\mathcal E_p}.
$$

따라서 $\partial W/\partial p_{\hat i}=v_{\hat i}$이고, (CG.5)에서

$$
\boxed{
\dot W
=-\sum_iH_i p_{\hat i}v_{\hat i}
=-K_{\hat i\hat j}p_{\hat i}v_{\hat j}.
}
\tag{CG.6}
$$

이때 압력 일을 정하는 양은 $p_iv_j$다.
상대론적 active energy를 일률적으로 $2W/3$의 등방압력으로 바꾸지 않고,
운동량과 velocity에서 실제 tensor를 계산한다.
작은 운동량에서의 계산에는 동치인 양의 식

$$
W=\frac{c^2|\boldsymbol p|^2}
{\sqrt{m_e^2c^4+c^2|\boldsymbol p|^2}+m_ec^2}
$$

을 사용하면 두 큰 에너지의 차감을 피할 수 있다.

Active packet들의 공행 가중 입자수를 $w_j\ge0$라 하면

$$
N_A=\sum_jw_j,\quad
U_A=\sum_jw_j W_j,\quad
\Pi_{A,\hat i\hat j}
=\frac1V\sum_jw_jp_{\hat i,j}v_{\hat j,j}.
$$

기하 흐름에서 $w_j$는 변하지 않는다.
$\boldsymbol p\mapsto-\boldsymbol p$ 쌍대칭은 (CG.5)로 유지되며,
$\Pi_A$는 양의 준정부호 symmetric tensor다.
$p_i v_j=(c^2/\mathcal E_p)p_i p_j$이고 $\mathcal E_p>0$이므로 이 성질은 각 packet에서 성립한다.
(CG.6)을 합하면

$$
\boxed{
\dot U_A=-V K:\Pi_A,\qquad
\dot u_A+\theta u_A+K:\Pi_A=0,\qquad u_A=U_A/V.
}
\tag{CG.7}
$$

가 된다. 이 식은 공변 투영과도 일치한다.
실제 active energy density는 $\rho_A=m_ec^2n_A+u_A$이고,
$p_A=\mathrm{tr}\Pi_A/3$, $\pi_A=\Pi_A-p_AI$다.
(CG.3)의 $\dot n_A+\theta n_A=0$으로 rest-energy 부분을 소거하면,
(CG.2)의 나머지는
$\dot u_A+\theta u_A+\theta p_A+\sigma:\pi_A=0$다.
$\theta p_A+\sigma:\pi_A=K:\Pi_A$이므로 (CG.7)이 회복된다.

이 유도는 유한 packet과 연속 분포의 적분에 똑같이 적용된다.
연속형에서는 packet 합을 운동량 모멘트 적분으로 바꾼다.

## Thermal 이상유체의 정확한 기하 subflow

같은 공행 셀의 thermal 원자핵·전자 수 $N_{\rm th}$가 고정되고,
등방 단원자 closure를 유지하면

$$
U_{\rm th}=c_vN_{\rm th}T,\qquad
p_{\rm th}=\frac{2U_{\rm th}}{3V},\qquad c_v=\frac32k_B.
$$

(CG.2)를 적용하고 상수인 공행 rest/chemical energy를 소거하면

$$
\dot U_{\rm th}+p_{\rm th}\dot V=0,
\qquad
\dot U_{\rm th}=-\frac23\theta U_{\rm th}.
$$

이에 따라

$$
\boxed{
U_{\rm th}^{+}
=U_{\rm th}^{n}
\left(\frac{V^{+}}{V^n}\right)^{-2/3},
\qquad
T^{+}=T^n
\left(\frac{V^{+}}{V^n}\right)^{-2/3},
\qquad N_{\rm th}^{+}=N_{\rm th}^{n}.
}
\tag{CG.8}
$$

은 이 이상유체 closure의 정확한 부분 해다.
부피가 양수이므로 $U_{\rm th}\ge0$와 $T\ge0$를 유지한다.
등방팽창에서는 익숙한 $T\propto a^{-2}$를 회복한다.
$\theta=0$인 구간에서는 thermal energy가 그대로 유지되며,
active sector의 $\sigma:\Pi_A$ 일은 계속 (CG.7)에 포함된다.

기하만으로 자유 비행하는 분포는 shear에 의해 비등방성을 만들 수 있다.
여기서는 thermal sector를 등방 bath로 유지하는 원래 closure를 사용하고,
active sector의 비등방 tensor를 별도로 정확히 운반한다.

## Signed 기하학적 일 장부의 endpoint 구성

Species counts가 변하지 않는 기하 부분 step에서 chemical energy는 일정하다.
Rest-energy를 상수로 생략한 material energy를

$$
\mathcal E_{\rm mat}=U_A+U_{\rm th}+U_{\rm chem}
$$

로 두자. 물질에서 기하학적 stress work로 이동한 에너지의 부호를 양으로 선택하여

$$
\boxed{
\Delta\mathcal W_{\rm geom}
=\mathcal E_{\rm mat}^{n}-\mathcal E_{\rm mat}^{+}
=U_A^n+U_{\rm th}^n-U_A^+-U_{\rm th}^+
}
\tag{CG.9}
$$

로 기록한다. 연속식 (CG.7)–(CG.8)에 의해 이는

$$
\Delta\mathcal W_{\rm geom}
=\int_{t_n}^{t_{n+1}}
V\left(K:\Pi_A+\theta p_{\rm th}\right)\,dt
$$

와 정확히 같다. 따라서 주어진 geometry에서 별도의 work quadrature 없이
물리적 endpoint energy 차이로 동일한 장부를 만들 수 있다.

$\Delta\mathcal W_{\rm geom}$은 정의상 signed다.
예를 들어 일부 축이 수축할 때 그 방향 운동량의 energy가 증가할 수 있다.
이 work ledger는 물질의 비음수 재고 $y$와 구분하여 보관한다.
고정 셀·공행 기준계에 대해 다음 합은 각 discrete substep에서 유지된다.

$$
\mathcal E_{\rm mat}+R+\mathcal W_{\rm geom}=\text{initial value}.
$$

Collision에서는 event columns가 $\mathcal E_{\rm mat}+R$를 보존하고,
geometry에서는 (CG.9)가 $\mathcal E_{\rm mat}+\mathcal W_{\rm geom}$을 보존한다.
핵수와 전하도 두 substep 각각에서 유지된다.

## 주어진 cutoff의 endpoint 편입

선택한 고정 cutoff $E_c>0$ 아래로 옮긴 active packet이 있으면,
endpoint의 실제 kinetic energy를 사용해

$$
\Delta N_{\rm join}=\sum_{j\in\mathcal L}w_j,\qquad
\Delta U_{\rm join}=\sum_{j\in\mathcal L}w_j W_j^+
$$

를 계산한다. 해당 packet을 active에서 제거하고,
$N_e\mapsto N_e+\Delta N_{\rm join}$,
$U_{\rm th}\mapsto U_{\rm th}+\Delta U_{\rm join}$로 갱신한다.
이 대수적 편입은 핵수·전하·energy와 비음성을 보존한다.
최종 온도는

$$
T_{\rm joined}
=\frac{U_{\rm th}^{+}+\Delta U_{\rm join}}
{c_v(N_{\rm th}^{+}+\Delta N_{\rm join})}
$$

다. Cutoff energy에 입자수를 곱하는 대신 각 실제 $W_j^+$를 사용한다.

이 편입의 수·energy 보존은 endpoint 항등식이다.
연속 시간의 경계 유량은 이전 TH1의 상대 경계속도와 실제 daughter moment에 연결한다.
아래의 시간 정확도 정리는 cutoff/channel support가 정칙한 소구간에 적용한다.
Crossing을 포함하는 interval에서는 TH1에 따라 crossing 시점에서 나눈 substep이나
검증된 경계 flux 적분을 사용하여 그 시간 정확도 의무를 연결한다.

## 닫힌 collision–geometry 한 step과 정확도

현재 격자와 volume에서 공통 extent의 collision map을
$\mathcal C_h$라고 하고, 주어진 $a_i(t)$의 geometry map을
$\mathcal G_{t_n\to t_{n+1}}$라고 쓰자.
두 map을 같은 packet 상태 공간에 놓기 위해, 현재 collision의 각 에너지 bin $j$에
고정 단위방향 $\boldsymbol\omega_{j\alpha}$와
$\beta_{j\alpha}\ge0$, $\sum_\alpha\beta_{j\alpha}=1$을 지정한다.
그 bin count $A_j$의 angular lift $\mathcal L_n$를

$$
\boldsymbol p_{j\alpha\pm}
=\pm\frac{\sqrt{W_j(W_j+2m_ec^2)}}{c}\boldsymbol\omega_{j\alpha},
\qquad
w_{j\alpha\pm}=\frac12A_j\beta_{j\alpha},
\qquad |\boldsymbol\omega_{j\alpha}|=1
\tag{CG.L1}
$$

로 정의하고, $\mathcal L_n$는 thermal·species·장부 성분에는 항등으로 작용한다. 이 식은
$\sum_{\alpha,\pm}w_{j\alpha\pm}=A_j$,
$\sum_{\alpha,\pm}w_{j\alpha\pm}W_j=A_jW_j$,
$\sum_{\alpha,\pm}w_{j\alpha\pm}\boldsymbol p_{j\alpha\pm}=0$을 직접 준다.
동일 packet 표현이 갖는 stress는
$\Pi_{A,j}=A_jV^{-1}[W_j(W_j+2m_ec^2)/(W_j+m_ec^2)]
\sum_\alpha\beta_{j\alpha}\boldsymbol\omega_{j\alpha}\boldsymbol\omega_{j\alpha}^{T}$다.

현재 입력도 정확히 같은 $\mathcal L_n$으로 표현되어 있다고 가정하고,
collision과 연속 collision vector field에 동일한 angular redistribution rule을 적용한다.
그러면 packet 위의 collision은
$\widetilde{\mathcal C}_h=\mathcal L_n\mathcal C_h\mathcal L_n^{-1}$이고,
$\mathcal L_n^{-1}$는 같은 bin의 packet count를 합한다.
입력 chart 위에서 $\widetilde{\mathcal C}_0=\mathrm{id}$이며,
입력의 pressure tensor도 그대로 유지된다.
주어진 유한 even packet 상태는 각 $\pm\boldsymbol p$ 쌍을 개별 $j$로 두고
$\beta=1$을 사용하여 이 chart에 포함할 수 있다.
또는 처음부터 사건 column을 이 packet index별로 정의해 같은 map을 얻는다.
아래의 $\mathcal C_h$는 이 공통 packet 공간의 map을 뜻하며,
$\mathcal G$는 바로 그 packet 운동량에 (CG.5)를 적용한다.
먼저 collision endpoint $y^\dagger=\mathcal C_h(y^n)$의 coefficient feedback을
해결한 뒤, 그 상태를 geometry로 운반한다.

$$
\boxed{
y^{n+1}
=\mathcal G_{t_n\to t_{n+1}}\!\left(\mathcal C_h(y^n)\right).
}
\tag{CG.10}
$$

Collision의 $T(z)$는 geometry를 적용하기 전의 collision endpoint다.
이 합성에서는 (CG.8)–(CG.9)의 기하 입력 상태를 $n$ 대신 $\dagger$로 읽는다.
특히 기하 work는 $U_A^\dagger+U_{\rm th}^\dagger-U_A^{n+1}-U_{\rm th}^{n+1}$이다.
최종 물리 온도는 그 뒤 (CG.8)과 필요한 편입의 EOS로 얻는다.
이 순서는 현재의 nonlinear coefficient closure와 정확한 prescribed geometry를
한 번씩 연결한 구체적인 Lie step이다.

사건 threshold/channel support가 일정한 정칙 영역에서,
collision vector field $\mathcal R(t,y)$가 시간과 상태에 대해 국소 Lipschitz라고 하자.
기하학적 시간 전개에는 각 $H_i(t)$의 국소 Lipschitz 연속성을 추가로 가정한다.
예를 들어 선택된 유한 구간에서 양의 $a_i\in C^2$이면 이 조건이 성립한다.
앞 절들의 정확한 유한 momentum map과 순간 work identity에는 $a_i\in C^1$이면 충분하며,
여기의 추가 조건은 $O(h^2)$ 시간 정확도 결론에 사용한다.
동반 event와 feedback 정리에 따라

$$
\mathcal C_h(y)=y+h\mathcal R(t_n,y)+O(h^2)
$$

이고, 정확 geometry flow의 전개는

$$
\mathcal G_{t_n\to t_{n+1}}(y)
=y+h\mathcal B(t_n,y)+O(h^2)
$$

다. 첫 식을 둘째에 대입하고 $\mathcal B$의 국소 Lipschitz 성질을 사용하면

$$
\mathcal G\mathcal C_h(y)
=y+h[\mathcal R(t_n,y)+\mathcal B(t_n,y)]+O(h^2).
\tag{CG.11}
$$

따라서 full split vector field에 대해 local error $O(h^2)$,
동반 안정성 조건 아래 global time order 1을 갖는다.
위 계산은 두 vector field의 가환성을 사용하지 않는다.
고정점 미종료 잔차는 동반 feedback certificate에 따라 이 정확도 예산에 더한다.

각 substep이 nonnegative material state를 보존하므로 그 합성도 그렇다.
Thermal count가 양의 핵수 하한을 갖고 thermal energy가 양수이면 최종 EOS도 유일하다.
사건 matrix의 핵수·전하·energy 보존과 (CG.9)의 기하학적 일이 결합하여,
한 step의 동일한 증분과 endpoint를 사용하는 전체 장부가 닫힌다.

## 다음 collision에 전달할 정확한 상태

(CG.5)는 실제 physical momentum을 바꾸므로, 다음 collision에는
$\boldsymbol p_j^{n+1}$와 $W_j^{n+1}$를 전달한다.
현재 예시 event family의 관계
$E_{A,r}=E_L+I_r+\epsilon_s$는 현재 collision에서 구성한 energy column의 정의다.
다음 collision에서는 변경된 실제 parent energy에 맞추어 daughter와 energy ledger를
다시 구성하거나, 양의 보존 remap으로 현재 solver 격자에 연결한다.
Angular chart도 기하 흐름 뒤의 실제 방향과 packet weights를 입력으로 다시 지정한다.
기존 angular rule로 되돌리는 추가 투영을 수행하지 않고 현재 even packet 상태를
그대로 담는 chart를 선택한다. 연속 collision field에도 그 단계의 동일한 angular closure를 사용한다.
각 collision의 고정 column이 현재 energy 행에 대해 $L_{\rm current}S=0$을 만족하면
동일한 보존·양수성 증명이 적용된다.

이번에 닫은 결과는 다음 항목이다.

1. 에너지·입자수의 공변 투영과 고유시간 $c$ adapter.
2. Active packet의 정확한 diagonal Bianchi I momentum/energy map.
3. Thermal 이상유체 closure의 정확한 양의 adiabatic map.
4. 실제 energy 차이로 평가하는 signed work ledger.
5. 정칙 branch에서 이 map과 coefficient-feedback collision의 일차 Lie 결합.

기존 전체 atomic kernel의 움직인 에너지 격자에 대한 보존 remap과,
$T$에 의존하는 cutoff의 implicit 경계 응답은 다음 adapter 작업으로 남긴다.
현재 부분 결과에서 사용하는 grid/channel energy, fixed cutoff, 이상유체 closure와
prescribed metric은 모두 명시적인 입력이다.




# 새 검산과 독립 검토

## 실제 실행 결과

| 실행 | 검사 수 | 결과와 대상 |
|---|---:|---|
| 사건 reference, Python Fraction | 9 | 양수성, 공유 energy capacity, 40개 invariant column residual, EOS, local-order 사례 |
| 피드백 driver, Python Fraction | 2 | 정확한 해에 대한 종료 certificate, 제한 종료의 실제 상태 |
| Wolfram, feedback 대수·적분 | 14 | 정확한 endpoint, 수축 상계, 물리적 defect, Grönwall 적분과 극한 |
| Wolfram+xAct | 4 | 공간 응력 직교성·무흔적성, 에너지 투영, 입자수 current |
| Wolfram, prescribed geometry | 5 | 운동량·상대론적 energy·thermal work·응력 분해·장부 |

Wolfram의 23개 named check는 모두 0 residual을 반환했다. Momentum check의 세 성분을 세면 scalar residual은 25개다. Python의 새 연결 검산은 합계 11개다. 이 숫자는 각 실행 파일에서 정한 검사 그룹 수이며, 문서나 검색 건수는 포함하지 않는다.

Wolfram kernel은 15.0.1 for Linux x86 (64-bit), xTensor는 1.3.0, xPerm은 1.2.4다. 공식 xAct 사이트의 xCore/xPerm/xTensor 파일을 내려받아 SHA-256을 확인한 뒤 불러왔다. $xpermQ=False$인 지원 Wolfram Language backend로 tensor canonicalization을 실행했다.

xAct에 입력한 응력은 임의의 대칭 $S^{ab}$를 공간 projector로 투영한 뒤 trace를 뺀 구성이다. 최종 energy identity를 simplification rule로 삽입하지 않았다. 입력 규칙은 metric compatibility, unit timelike normalization, 그 미분 및 응력의 정의다.

초기 external permutation 경로에서는 metric의 covariant derivative 정의가 끝나지 않는 오류가 발생했다. 같은 공식 소스의 지원 backend를 바꾸어 문제를 해결했고, canonical 원출력에는 정상 버전·hash와 네 개의 0 residual을 기록했다. Scalar 극한 계산 중 발생한 \texttt{Power::infy}/\texttt{Infinity::indet} 메시지도 원출력에 보존했다. 최종 극한값과 독립적인 해석 전개가 FP.40의 연속 정의와 일치한다.

## 독립 검토와 반영

후보를 작성하지 않은 검토자가 사건 구성, feedback proof, geometry, 코드와 실제 원출력을 읽고 독립적인 논증으로 검토했다. 검토 중 발견한 참조 경로 한 건, 시간 정확도에 필요한 Lipschitz 조건, bin-to-packet angular lift의 연결을 원문과 계약에 반영했다. 최종 판정은 PROMOTE_SCOPED / PASS이며, FB1–FB7과 두 reference 구현을 승인했다. 열린 차단 지적은 0개다. 각 지적의 해결 상태와 채택 범위는 review/DECISION.json 및 review/REVIEW_KO.md에 결속했다.

사건 소비량의 양수성은 실제 전체 donor load를 사용한 상계로 검토했고, FP6은 선형 경로의 residual을 직접 적분해 확인했다. Geometry에서는 $c$의 위치, 상대론적 pressure work, signed work ledger 및 $h=0$에서 항등인 angular chart를 확인했다. 기존 과학 실행을 독립 검토자가 반복한 횟수는 0회다.

# 구현과 재현

작은 유한 입력의 exact reference는 Python 표준 라이브러리만 사용한다. 핵심 함수는 \texttt{capacity\_step}와 \texttt{solve\_feedback}이다. 전자는 공통 사건 extent, 새 상태, 총 donor load와 잔여 하한을 반환한다. 후자는 주어진 $q$ 및 domain 근거에 따라 반복하고, 반환 상태와 그 상태의 residual을 측정한 다음 map image를 각각 보관한다.

Driver의 계약은 입력된 수축 상계와 domain이 별도로 검증되었다는 것이다. 방문 상태가 domain 안에 있는지와 수치 범위는 실행 중 확인한다. 계수 표나 부동소수점 evaluator를 사용할 때에는 그 평가 오차 상계를 함께 제공한다. 실제 continuous rate evaluator를 전달하면 physical endpoint defect가 추가로 반환된다.

재현 자료에는 다음이 포함된다.

- 전체 Markdown 유도, 계약, 가정과 error map.
- H/He event family, exact reference code와 두 실행 파일.
- 실제 Wolfram/xAct 코드, package SHA-256, 원출력과 정규화한 결과.
- 독립 검토, 이전 근거의 identity, 새 DAG와 계획.
- LaTeX 전체 원고, PDF, figure와 사용 폰트 정보.

Python 검산은 제공한 \texttt{checks/run\_event\_checks.py} 및 \texttt{checks/run\_feedback\_checks.py}로 재현한다. 이론을 읽거나 다음 연구를 재개할 때에는 유지된 결과와 identity를 먼저 재사용한다. Wolfram 코드는 stateless kernel에서 각 파일을 독립적으로 평가하도록 작성했다. xAct bootstrap에는 공식 다운로드 URL와 hash가 들어 있다.

# 다음 연구 지점

완료한 feedback node 다음에는 두 이론 연결을 병행할 수 있다.

첫째는 **현재 실제 에너지 격자와 atomic daughter 자료를 사건 열에 결속하는 adapter**다. 현재 식 $L_{\rm current}S=0$을 유지하는 양의 분해와 interpolation의 미분 상계를 구성하면, FP3의 step 조건과 FP4의 rate-table 오차를 실제 kernel 입력으로 평가할 수 있다. 기존 원자 계산을 다시 실행하는 작업에 앞서 이 연결을 수행한다.

둘째는 **온도 의존 cutoff의 implicit 경계 응답**이다. 이전 moving-boundary moment와 이번 EOS map을 이용해, cutoff의 변화가 thermal count와 energy에 주는 미분을 구성하고 self-map 조건에 포함한다. 현재의 고정 cutoff와 정칙 channel branch는 그 계산의 출발점이다.

선택된 물리 scenario에 적용하는 경로에는 source, 초기 상태, 관측량과 허용오차를 결속한다. 이 입력을 요구하는 기존 application node는 그 의미를 유지한다. 이번 단계에서 일반 조건부 유도와 유한 예제, reference 구현, 공변 검산을 완성했다.

# 문헌과 원전 비교


\begingroup
\small

연구 단위: CR-THEORY-FEEDBACK-20261013. 확인일: 2026-10-13 KST / 2026-10-12 UTC.

## 문헌 대조의 결론

반응별로 공통 증분을 사용해 화학양론을 보존하는 방법과, 입자수 변화를 포함한 열적 온도식은 선행연구에서 확인된다. 이번 후보의 수용 여부는 그 위에 구성한 BASS_CR active/thermal/H–He 사건 장부, 양수성 보존 갱신, 온도·조성 피드백 사상의 직접 증명으로 판정한다. 아래 문헌은 수식과 방법의 대응 근거이며, 후보의 일반 정리는 별도의 독립 심사에서 확인한다.

SciSpace의 자연어 검색 한 차례와 Exa의 네 검색(요청 결과 합계 26개)을 사용했다. 중복과 개요만 있는 결과를 제거하고 아래 네 원전의 필요한 절을 읽었다. 검색의 목적은 이번 구성에 가까운 선행 방법과 적용 조건의 확인이다.

## L1. 반응별 공통 가중치와 에너지의 반응 참여

Jianhua Pan, Yu-Yen Chen, Liang-Shih Fan, *Second-order unconditional positive preserving schemes for non-equilibrium reactive flows with mass and mole balance*, Journal of Computational Physics **441**, 110477 (2021). DOI: [10.1016/j.jcp.2021.110477](https://doi.org/10.1016/j.jcp.2021.110477). 읽은 원문: [arXiv:2006.08549](https://ar5iv.labs.arxiv.org/html/2006.08549), §§2–5.

논문은 반응 r에 참여하는 모든 종에 동일한 Patankar 가중치 χ_r를 곱한다. 반응률과 화학양론 계수의 곱을 유지하므로 사건별 원소·질량 장부가 보존된다. §§2–3은 반응물 농도비의 곱으로 χ_r를 구성하고 2차 정확도 조건을 전개한다. §5는 흡열 사건에서 내부에너지를 소비하는 성분으로, 발열 사건에서는 생성되는 성분으로 다루어 열적 양수성을 결합한다.

증명의 적용 조건을 분리했다. §4의 일반 다중 반응물 암시계에 대한 양의 해 존재·유일성은 **Conjecture 1**이다. Theorem 1은 각 반응에 반응물이 하나인 경우, Theorem 2는 다중 반응물·무생성 반응 하나와 선형 단일 반응물 반응들이 있는 경우를 다룬다. 일반 경우의 근거는 해당 논문의 표본 계산이다. 따라서 이번에는 **반응별 공통 가중치와 에너지 참여라는 구성 비교**를 채택하며, 후보의 일반 존재·유일성은 직접 증명으로 심사한다.

## L2. 양의 선형 암시계와 보존량

Stefan Kopecz, Andreas Meister, *On Order Conditions for modified Patankar–Runge–Kutta schemes*, [arXiv:1702.04589](https://arxiv.org/abs/1702.04589). 읽은 원문: [PDF](https://arxiv.org/pdf/1702.04589), Definition 2.1, Lemmas 2.6–2.7, Theorems 3.3–3.4.

논문이 다루는 생산–소멸계는 비음수의 쌍별 전달률 p_ij,d_ij와 p_ij=d_ji를 갖는다. 비음수 Runge–Kutta 계수 및 양의 Patankar 분모를 사용하며, 분모는 해당 단계에서 구할 미지수와 독립이다. Lemma 2.6은 같은 전달을 생성·소멸 양쪽에 배정해 합의 보존을 증명한다. Lemma 2.7은 시스템 행렬의 전치가 엄격한 대각우세 M-matrix임을 사용해 역행렬의 비음성과 단계별 양수성을 증명한다. 정확도는 별도 분모 조건으로 다룬다.

이번 연구와의 대응은 **고정한 계수에서의 양의 선형 갱신과 보존 출력**이다. 다중 반응물을 하나의 수·에너지 사건으로 묶을 때에는 그 사건의 화학양론과 필요한 모든 보존 선형형식을 후보에서 직접 확인한다. L1의 비선형 공통 가중치와 L2의 선형 M-matrix 조건은 서로 다른 증명 구조로 기록한다.

## L3. H/He 화학 변화에 따른 온도식

U. Ziegler, *A chemical reaction network solver for the astrophysics code NIRVANA*, Astronomy & Astrophysics **586**, A82 (2016). DOI: [10.1051/0004-6361/201527262](https://doi.org/10.1051/0004-6361/201527262). 읽은 원문: [공식 HTML](https://www.aanda.org/articles/aa/full_html/2016/02/aa27262-15/aa27262-15.html), §§2.1–2.2, §3, 식 (3)–(13).

원문은 종별 수밀도와 열적 에너지의 반응 부분을 함께 다루고, 전자수는 전하 보존에서 결정한다. 고정 γ의 이상기체와 고정 부피의 source 부분에서 $n_{\rm tot}=\sum_s n_s+n_e$ 및 $\dot n_e=\sum_s q_s R_s$를 사용해 식 (12)를 얻는다:

$$
\dot T=\frac{\gamma-1}{k_Bn_{\mathrm{tot}}}S_e-
\frac{T}{n_{\mathrm{tot}}}\sum_s(1+q_s)R_s.
$$

식 (13)은 반응별 열적 source가 종별 반응과 같은 농도곱을 공유하도록 구성한다. 이 결과는 현재 열적 EOS에서 수 변화 항의 부호·단위와 사건별 열 연결을 대조하는 근거다. BASS_CR의 active 전자와 thermal 전자의 분할, cutoff 이관, 초과에너지 상태는 직전 채택 유도에서 가져와 이번 장부에 연결한다. NIRVANA의 source 적분기는 GRK4(3)T이며, 이번 후보의 양수성·수축 조건은 후보 자체의 증명으로 판정한다.

## L4. 자기일관적 화학–열 결합의 암시적 구성

Daniel R. Reynolds, John C. Hayes, Pascal Paschos, Michael L. Norman, *Self-Consistent Solution of Cosmological Radiation-Hydrodynamics and Chemical Ionization* (2009). DOI: [10.1016/j.jcp.2009.06.006](https://doi.org/10.1016/j.jcp.2009.06.006). 읽은 원문: [arXiv:0901.1110v3 PDF](https://arxiv.org/pdf/0901.1110), §§2.1, 3.2–3.2.4, 식 (19)–(43).

논문은 우주론적 화학종, 가스 에너지 보정, 복사 에너지를 하나의 암시적 비선형 잔차로 묶고, 선탐색을 갖춘 inexact Newton 방법으로 푼다. 미시물리 결합이 공간적으로 국소라는 점을 이용해 Schur complement에서 셀별 블록을 소거한다. 물리량 규모가 다른 변수에는 별도의 단위 정규화를 적용하고, 적응 시간 간격에는 정확도 판별량을 사용한다.

이번에는 **화학·열의 동시 피드백과 물리량별 정규화**를 방법론적 근거로 채택한다. 현재 BASS_CR 한 셀의 사상은 자신의 상태공간·정칙성·불변집합·수축 상수 아래에서 증명한다. 논문의 복사 확산 closure와 수치 허용오차는 이번 이론 가정에 추가하지 않는다.

## 근거와 실행 상태

- **literature-supported:** 위 원전에서 확인한 식과 해당 조건의 증명 또는 구성.
- **derived:** 현재 후보의 사건 장부·피드백·오차식은 후보 원문과 독립 심사에서 별도로 판정.
- SciSpace와 Exa 호출은 성공했다. Pan의 arXiv 직접 URL은 Exa가 처음에 서지 레코드만 반환하여, Exa의 ar5iv 원문으로 §§2–5를 읽었다. Kopecz–Meister와 Reynolds는 Exa가 PDF 본문을 반환했고, Ziegler는 공식 HTML 본문을 반환했다.
- 일반 웹 도구에는 일부 URL의 403·503·DisabledError 및 한 차례 무관한 검색 결과가 있었다. 이를 과학적 실패로 분류하지 않았으며, 해당 결과는 문헌 근거에서 제외했다. 채택한 네 원전의 필요한 본문은 Exa로 확인했다.

후속 후보 독립 심사는 이 문헌 대조와 별도 기록이다. 이 파일 작성자는 후보 생성과 작성자 검산 설계에 참여하지 않았다.


\endgroup


## xAct 실행 근거

xAct의 공식 [xTensor](https://www.xact.es/xTensor/)와 [xPerm](https://www.xact.es/xPerm/) 자료, [설치 안내](https://www.xact.es/download/install)를 확인했다. xPerm의 tensor canonicalization 배경은 J. M. Martín-García, “xPerm: fast index canonicalization for tensor computer algebra,” Computer Physics Communications 179 (2008) 597–603, [arXiv:0803.0862](https://arxiv.org/abs/0803.0862)에 있다.


