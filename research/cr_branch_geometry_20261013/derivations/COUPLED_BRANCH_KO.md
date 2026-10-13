# 실제 HI 사건과 stopping을 결합한 고정 atomic branch의 endpoint

연구 단위: `CR-THEORY-BRANCH-GEOMETRY-20261013`  
노드: `CR_THEORY_COUPLED_BRANCH_SOLVER`  
현재 기준 Git: `c450b00108dc05885a25d0d9c042cdcfe41bd659`  
재사용 근거: KC1–KC7의 실제 saved-grid/kernel 결속, paired event columns, 공통 capacity map, cutoff branch 및 EOS 인터페이스.

## 1. 이번 구성의 문제와 입력

이번에는 실제 source coefficient가 있는 두 사건을 골라, 조성과 thermal electron density가 바뀐 뒤 같은 반응률에 되돌아가는 **하나의 finite-step endpoint**를 계산한다. 두 사건은 HI full BED sharing의 한 실제 quadrature subchannel과, 별도 active donor의 한 실제 stopping edge다. 초기 재고는 아래에 명시한 **CONSTRUCTION**이며 historical spectrum을 대신하지 않는다. 선택한 subfamily의 endpoint 존재·유일성·장부·계산오차가 이번 결과다.

원자료는 `inputs/prior/kernel_event_adapter.py`와 그 아래 source-bound files에서 읽었다. 저장된 9600-node `energy_eV` raw digest는 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`이다. 전체 generator나 이전 physics suite를 재실행하지 않고, 아래 실제 사건과 필요한 stopping coefficient를 결속했다. 입력과 각 source file의 identity는 `examples/COUPLED_BRANCH_INPUT.json`에 있다.

| 항목 | 실제 채택값 |
|---|---:|
| HI parent node | \(j=4762\), \(W_I=30.00976971818039\) eV |
| HI sharing index | \(\ell=38\), 원래 15,620개 quadrature points 중 한 점 |
| 실제 sharing probability | \(p_{I}=0.00019359060355166532\) |
| 실제 subchannel coefficient | \(\kappa_I=v_I\sigma_H(W_I)p_I=3.336923667758757\times10^{-18}\ {\rm m^3s^{-1}}\) |
| Slow daughter | \(w=0.10194917280817987\) eV |
| Fast daughter | \(W_I-B_H-w=16.30212054537221\) eV |
| HI binding | \(B_H=13.6057\) eV |
| Stopping parent node | \(j=290\), \(W_S=1.00028125\) eV |
| Stopping daughter node | \(j=289\), \(W_D=0.9971875\) eV |
| Stopping heat | \(\delta=W_S-W_D=0.0030937500000000062\) eV |

이 표의 decimal은 사람이 읽는 표시이고, 구현의 source finite inputs와 event columns는 원래 binary rationals로 보존했다. SI energy conversion은 \(\epsilon_{\rm eV}=1.602176634\times10^{-19}\ {\rm J/eV}\), \(k_B=1.380649\times10^{-23}\ {\rm J/K}\), \(c_v=3k_B/2\)다. 원래 비상대론적 source velocity·cold-target stopping prescription을 유지한다.

## 2. 두 사건의 실제 raw output

Source lower absorber는 \(W_b=0.1\) eV이고 첫 active grid node는 \(W_0=0.10309375000000001\) eV다. 선택한 slow daughter는 이 둘 사이에 있다. 따라서 기존 projector는

\[
 \alpha={w-W_b\over W_0-W_b}=0.6300356551692494\ldots,\qquad
 g=1-\alpha=0.3699643448307506\ldots
 \tag{CB.1}
\]

를 사용한다. \(\alpha\) count는 raw node \(A_0\)에, \(g\) count와 \(\epsilon_{\rm eV}W_bg\) energy는 base thermal bath에 들어간다. 이 ghost 분해는 KC의 source projector 자체이며, 그 두 기여의 합은 정확히 한 electron과 \(\epsilon_{\rm eV}w\)다.

Fast daughter는 실제 nodes 3894와 3895, 즉 16.301160463877856 eV와 16.312625762674944 eV 사이에 투영된다. 그 upper barycentric weight를 \(\beta\)라 하자. HI 사건과 stopping 사건의 increments는 다음과 같다.

| 상태 | HI 사건 \(S_I\) | Stopping 사건 \(S_S\) |
|---|---:|---:|
| \(A_{4762}\) | \(-1\) | 0 |
| \(A_{3894},A_{3895}\) | \(1-\beta,\ \beta\) | 0 |
| \(A_0\) | \(\alpha\) | 0 |
| \(X_{HI},X_{HII}\) | \(-1,+1\) | 0 |
| base thermal electrons \(N_{e,B}\) | \(g\) | 0 |
| base thermal energy \(U_B\) | \(\epsilon_{\rm eV}W_bg\) | \(\epsilon_{\rm eV}\delta\) |
| \(A_{290},A_{289}\) | 0 | \(-1,+1\) |

같은 사건의 모든 coordinate에 하나의 extent를 곱한다. 두 columns는 초기 raw reference에 고정되어 있고, trial temperature나 density에 따라 daughter weights·source energies·초기 donor mask를 변경하지 않는다. Source의 excitation reservoir는 이 subfamily에서 그대로다. HI binding은 \(\epsilon_{\rm eV}B_HX_{HII}\)라는 chemical energy로 한 번 계산한다.

## 3. 양의 neutral 초기 재고

Physical volume과 step을

\[
 V_*=1\ {\rm m^3},\qquad h=10^{14}\ {\rm s}
 \tag{CB.2}
\]

로 고정한다. 두 parent counts는 각각 1이고, 나머지 raw nodes의 초기 count는 0이다. Gas 재고는

\[
 \begin{aligned}
 X_0:=X_{HI}^n&=138.6,\\
 X_{HeI}^n&=11.427127659574467,\qquad X_{HeII}^n=0,\\
 N_{e,B}^n=:n_0&=1.5154255319148937,\\
 X_{HII}^n&=n_0+2.
 \end{aligned}\tag{CB.3}
\]

이다. \(V_*=1\ {\rm m^3}\)이므로 electron count와 수밀도의 수치가 같다. 처음 thermal bath의 전체 particle count는

\[
 N_0=X_0+X_{HII}^n+X_{HeI}^n+N_{e,B}^n
      =155.05797872340426\ldots .
 \tag{CB.4}
\]

초기 \(T_0=100\) K와 \(U_B^n=c_vN_0T_0>0\)를 둔다. 초기 전하는 \(X_{HII}^n-N_{e,B}^n-A_{4762}^n-A_{290}^n=0\)이다. HI 및 thermal electron baseline densities는 원래 source bath의 수치에 맞췄고, 두 active electrons를 포함한 neutrality는 이번 construction에서 별도로 맞췄다. 따라서 전체 nuclei inventory는 historical source 초기조건이라는 주장이 아니다.

큰 \(h\)는 두 피드백과 capacity denominator가 실제로 작동하는 finite-map endpoint를 구성하기 위해 선택했다. 이후의 매우 작은 residual certificate는 이 map의 nonlinear solve 오차에 관한 것이며, \(h\)의 시간 이산화 오차나 전체 물리모형의 정확도에 관한 수치가 아니다.

## 4. Extent와 thermal branch의 정확한 축약

HI extent를 \(x\), stopping extent를 \(s\)라 쓰면 raw endpoint는

\[
 y(x,s)=y^n+xS_I+sS_S.
 \tag{CB.5}
\]

Cutoff closure를 \(E_c=\chi k_BT\), \(\chi=20\)으로 둔다. 고정할 actual grid branch는

\[
 W_{22}=0.17115625\ {\rm eV}
 <{E_c\over\epsilon_{\rm eV}}
 <W_{23}=0.17425000000000002\ {\rm eV}.
 \tag{CB.6}
\]

이 branch에서 raw \(A_0\)는 thermal-owned retained trace이고 다른 occupied raw nodes는 active다. 처음 active donor 둘은 모두 초기 cutoff 위에 있다. 처음 비어 있던 thermal trace를 이후 trial의 새 active donor로 세지 않는다.

\(A_0\)를 base에 중복 합산하지 않고 ownership에 따라 더하면

\[
 \begin{aligned}
 N_{e,th}(x,s)&=n_0+gx+\alpha x=n_0+x,\\
 N_{th}(x,s)&=N_0+x,\\
 U_{th}(x,s)&=c_vN_0T_0+
             \epsilon_{\rm eV}\{(W_bg+W_0\alpha)x+\delta s\}\\
 &=c_vN_0T_0+\epsilon_{\rm eV}(wx+\delta s),\\
 T(x,s)&={c_vN_0T_0+\epsilon_{\rm eV}(wx+\delta s)
                    \over c_v(N_0+x)}.
 \end{aligned}\tag{CB.7}
\]

따라서 반응으로 실제 raw atoms가 생기고 사라지는 동안, 조성·electron bath·thermal count·energy·cutoff가 두 extent에 의해 함께 결정된다. \(N_{e,th}\)는 EOS의 \(N_{th}\)와 구별한다. Density feedback에는 전자를 포함한 전체 active count를 더하지 않는다.

## 5. 실제 rate와 두 차원 endpoint map

초기 parent stocks와 positive co-reactant support를 고정하고 trial composition을 rate에 넣으면

\[
 f_I(x)=\kappa_I{X_0-x\over V_*},\qquad
 f_S(x)=\lambda(n_0+x).
 \tag{CB.8}
\]

Stopping source의 \(\alpha_S\)와 baseline Coulomb log를 exact finite inputs로 읽어

\[
 \begin{aligned}
 \lambda(n)&=A_S n L(n),\qquad A_S={\alpha_S\over\delta},\\
 L(n)&=L_0-\tfrac12\log(n/n_0),\\
 A_S&=2.497254955828195\times10^{-9}\ {\rm m^3s^{-1}},\\
 L_0&=29.4116061589828,\qquad
 \lambda(n_0)=1.1130539763458147\times10^{-7}\ {\rm s^{-1}}
 \end{aligned}\tag{CB.9}
\]

로 사용한다. 이는 KC의 thermal bath density continuation이다. Source의 \(\alpha_S,L_0\)를 binary rational로 해석하고 \(\delta\)를 exact grid energy difference로 계산한 baseline rate와 원래 float evaluation의 상대 차이는 \(1.19\times10^{-16}\)이다. 이 rounding 차이는 입력 기록에 명시했다.

두 사건의 negative donors는 각각 \(\{A_{4762},X_{HI}\}\)와 \(\{A_{290}\}\)이고 서로 다른 active parent를 쓴다. 이전 shared-capacity map을 이 두 columns에 적용하면, 새로운 수치기법을 도입하지 않고 정확히

\[
 \Phi_I(x)={a(X_0-x)\over1+b\,a(X_0-x)},\qquad
 \Phi_S(x)={h\lambda(n_0+x)\over1+h\lambda(n_0+x)},
 \tag{CB.10}
\]

\[
 a={h\kappa_I\over V_*}=0.0003336923667758757\ldots,
 \qquad b=1+{1\over X_0},\qquad
 \Phi(x,s)=(\Phi_I(x),\Phi_S(x))
 \tag{CB.11}
\]

을 얻는다. Desired endpoint는 \((x_*,s_*)=\Phi(x_*,s_*)\)다. HI depletion이 첫 rate에, 그 사건이 만드는 thermal electron이 둘째 rate에 실제로 되먹임된다. 이 source의 fixed-energy coefficients에는 직접 \(T\) 인자가 없으므로 temperature는 EOS와 branch 부등식으로 닫힌다. 일반적인 temperature-dependent atomic rate를 인위적으로 추가하지 않았다.

또한 \(z=y^n\)에서 (CB.8)은 원래 source의 해당 selected subchannel 및 stopping rate다. \(h\to0\)이면 \(\Phi_I=h f_I+O(h^2)\), \(\Phi_S=h f_S+O(h^2)\)이고, KC의 fixed-branch first-order consistency가 유지된다.

## 6. 숫자가 있는 닫힌 self-map

다음 직사각형을 택한다.

\[
 \mathcal D=[0,1/20]\times[0,1],\qquad
 \|(u,v)\|_* =\max(20|u|,|v|).
 \tag{CB.12}
\]

첫 map은 \(x\)에 대해 감소하므로 양 끝만 보면

\[
 0.04417595
 \le\Phi_I(x)\le
 0.04419119
 <0.05.
 \tag{CB.13}
\]

둘째 map의 정의역은 \(n\in[n_0,n_0+0.05]\)다. \(\log(1+r)\le r\)로부터

\[
 L(n)\ge L_0-{0.05\over2n_0}
       =29.395109142485783\ldots>\tfrac12.
 \tag{CB.14}
\]

따라서 \(\lambda>0\), \(\lambda'>0\), \(0<\Phi_S<1\)이다. (CB.13)–(CB.14)는 모두 exact rational inequalities로 확인했으므로 \(\Phi(\mathcal D)\subset\mathcal D\)다.

Thermal closure도 이 domain 전체에서 같은 branch에 남는다. 직접 미분하면

\[
 T_x={N_0(\epsilon_{\rm eV}w-c_vT_0)
                  -\epsilon_{\rm eV}\delta s\over c_v(N_0+x)^2}>0,
 \qquad
 T_s={\epsilon_{\rm eV}\delta\over c_v(N_0+x)}>0.
 \tag{CB.15}
\]

첫 분자의 최소값도 양수다. 따라서

\[
 100\le T(x,s)\le100.376319<100.4\ {\rm K},
 \tag{CB.16}
\]

\[
 0.17234666
 \le {E_c\over\epsilon_{\rm eV}}
 \le0.17299524\quad {\rm eV}.
 \tag{CB.17}
\]

이다. 실제 grid branch의 아래·위 경계까지 균일한 여유는 각각 적어도 **0.00119041 eV**, **0.00125476 eV**다. 그러므로 이 self-map의 모든 trial과 endpoint에서 thermal ownership이 유지된다. Source의 lower absorber보다 cutoff가 높으므로 이 구성에는 0.1 eV 아래 trace의 역분류가 요구되지 않는다.

온도 box \([100,100.4]\) K에서 가장 낮은 occupied active node에 대해서도 \(\mathcal W/(k_BT)>115.25\)이다. Positive Coulomb log와 함께 이번 cold-target continuation의 명시된 domain을 확인한다.

## 7. 수축률의 실제 상계

식 (CB.10)의 미분은

\[
 \Phi_I'(x)=-{a\over[1+b\,a(X_0-x)]^2},\qquad
 \Phi_S'(x)={h\lambda'(n_0+x)\over[1+h\lambda(n_0+x)]^2},
 \tag{CB.18}
\]

이고 \(\lambda'(n)=A_S(L(n)-1/2)\), \(\lambda''(n)=-A_S/(2n)<0\)이다. 따라서 \(\lambda\)는 증가하고 \(\lambda'\)는 감소한다. Domain 전체에서

\[
 \begin{aligned}
 q_I&={a\over[1+b\,a(X_0-1/20)]^2}
        =0.0003046579321861247\ldots,\\
 M_S&={h A_S(L_0-1/2)\over[1+h A_S n_0L_0]^2},\\
 q_S&={M_S\over20}=2.9138861430824442\times10^{-9}.
 \end{aligned}\tag{CB.19}
\]

Jacobian의 두 번째 column은 0이다. 그러므로 (CB.12)의 weighted maximum norm에서

\[
 \|\Phi(z)-\Phi(\widetilde z)\|_*
 \le\max(q_I,q_S)\|z-\widetilde z\|_*
 <\bar q\|z-\widetilde z\|_*,\qquad
 \bar q={31\over100000}=0.00031<1.
 \tag{CB.20}
\]

닫힌 완비 self-map에 수축정리를 적용하면 \(\mathcal D\) 안의 endpoint는 존재하고 유일하다. 이 결론은 서로 독립적인 \(T,n_e,X\) 값을 임의로 허용한 box가 아니라, 같은 사건 장부가 정의하는 physical extent domain에서 얻었다. \(T,n_e,X\)는 (CB.5)–(CB.7)의 같은 endpoint에서 함께 복원된다.

## 8. Endpoint의 실제 계산과 exact residual certificate

Ion equation은 두 차원 문제에서 먼저 제거할 수 있다. 식 \(x=\Phi_I(x)\)는

\[
 ba x^2-(1+a+baX_0)x+aX_0=0.
 \tag{CB.21}
\]

\(C=1+a(X_0+2)\)라 하면 양의 작은 root를 안정적인 형태로

\[
 x_*={2aX_0\over C+\sqrt{C^2-4a^2(X_0+1)}},\qquad
 C^2-4a^2(X_0+1)=1+2a(X_0+2)+a^2X_0^2>0
 \tag{CB.22}
\]

로 쓸 수 있다. 구현은 \(x=0\)에서 7회의 exact rational scalar update를 수행한 뒤 30 decimal places의 rational \(\widehat x\)를 선택했다. 그 지점에서 stopping log를 아래의 exact enclosure로 계산하고 rational \(\widehat s\)를 선택했다. 이 두 계산 경로는 fixed-point residual로 다시 검증한다.

\(t=x/(2n_0+x)\in[0,1)\)에 대해

\[
 \log\left({n_0+x\over n_0}\right)
 =2\sum_{j=0}^{K-1}{t^{2j+1}\over2j+1}+R_K,
 \quad
 0\le R_K\le{2t^{2K+1}\over(2K+1)(1-t^2)}.
 \tag{CB.23}
\]

이 positive atanh series의 tail bound는 분모를 \(2K+1\)로 낮추고 geometric series를 합해 얻는다. \(K=8\)에서 모든 항과 bound를 Fraction arithmetic으로 계산했다. 따라서 elementary-function floating accuracy에 기대지 않고 \(\Phi_S(\widehat x)\)의 엄밀한 rational interval을 얻는다.

실제 계산한 endpoint 표시는

\[
 \begin{aligned}
 x_*&\simeq0.04417772517583427,\\
 s_*&\simeq0.9999999126593523,\\
 n_{e,*}&\simeq1.559603257090728\ {\rm m^{-3}},\\
 T_*&\simeq100.35047955672445\ {\rm K},\\
 E_{c,*}/\epsilon_{\rm eV}&\simeq0.17295070507127627\ {\rm eV}.
 \end{aligned}\tag{CB.24}
\]

정확한 저장값은 `examples/COUPLED_BRANCH_ENDPOINT.json`에 있다. \(\widehat z=(\widehat x,\widehat s)\)의 residual과 endpoint bound는

\[
 \eta\ge\|\Phi(\widehat z)-\widehat z\|_*,\qquad
 \|z_*-\widehat z\|_*\le{\eta\over1-\bar q}.
 \tag{CB.25}
\]

실제 exact rational upper bounds는 다음과 같다.

| Quantity | 검증된 upper bound |
|---|---:|
| Weighted residual \(\eta\) | \(2.153\times10^{-25}\) |
| Endpoint weighted radius | \(2.154\times10^{-25}\) |
| \(x_*\) error | \(1.077\times10^{-26}\) |
| \(T_*\) error | \(8.107\times10^{-26}\) K |

Temperature estimate에는

\[
 L_T\le {\frac1{20}(\epsilon_{\rm eV}w-c_vT_0)
                 +\epsilon_{\rm eV}\delta\over c_vN_0}
      =0.3764399606128681\ldots\ {\rm K}
 \tag{CB.26}
\]

를 썼다. 이는 (CB.15)의 각 partial derivative 최대값을 weighted norm에 맞춰 합한 것이다. \(|T_*-T(\widehat z)|\le L_T\eta/(1-\bar q)\)이고 cutoff error에는 \(\chi k_B/\epsilon_{\rm eV}\)를 더 곱한다.

표의 decimal은 위로 여유를 둔 가독성 표기와 JSON의 exact Fraction certificate를 함께 참조한다. 중요한 정확도는 selected finite-input map의 algebraic solve 정확도다. 원자 자료·source rounding·cold-target closure·시간 적분의 모델 오차는 이 숫자에 포함하지 않는다. Source rounding 비교는 별도 입력 항목으로 남겼다.

## 9. 실제 raw endpoint와 보존

저장된 rational approximate endpoint도 \(y^n+\widehat xS_I+\widehat sS_S\)로 조립하므로 invariant는 정확히 유지된다. Endpoint raw inventory는 다음과 같다.

| Raw node | Energy (eV) | Count | Endpoint ownership |
|---|---:|---:|---|
| \(A_0\) | 0.10309375000000001 | 0.02783354202504379 | thermal retained trace |
| \(A_{289}\) | 0.9971875 | 0.9999999126593523 | active |
| \(A_{290}\) | 1.00028125 | \(8.7340647674\times10^{-8}\) | active |
| \(A_{3894}\) | 16.301160463877856 | 0.0404783696549195 | active |
| \(A_{3895}\) | 16.312625762674944 | 0.003699355520914768 | active |
| \(A_{4762}\) | 30.00976971818039 | 0.9558222748241657 | active |

Thermal endpoint는 \(N_{th,*}=155.10215644858008\ldots\), \(U_{th,*}=3.2233823978908755\times10^{-19}\) J다. Raw \(A_0\)와 base ghost contribution을 함께 읽어 한 thermal electron per ionization을 회복했다. \(U_B\)와 \(U_{th}\)의 차이를 유지하므로 thermal trace energy를 중복해 더하지 않는다.

보존 rows는 H nuclei, He nuclei, total charge,

\[
 E_{tot}=\epsilon_{\rm eV}\sum_jW_jA_j+U_B
          +\epsilon_{\rm eV}B_HX_{HII}
          +\epsilon_{\rm eV}B_{He}X_{HeII}+E_{exc,H}+E_{exc,He}
 \tag{CB.27}
\]

다. 각각의 두 source event column residual, 실제 endpoint 변화, unchanged capacity map이 만든 state의 변화가 모두 Fraction arithmetic에서 **정확히 0**이다. 모든 endpoint counts와 energy는 비음수이며 \(U_{th}>0\), \(N_{th}>0\)여서 \(T>0\)이다.

## 10. 새 실행과 독립 확인의 범위

`checks/check_coupled_branch.py`는 이번 endpoint에 필요한 새 검사만 수행했다. 실제 실행은 `results/COUPLED_BRANCH_CHECKS.json`에 UTC, runtime, 당시 input/source hashes와 함께 저장되어 있다.

검사는 먼저 현재 copied source bytes가 결속된 identity와 같은지 확인하고, scalar reduction을 **변경 없는 이전 `capacity_step`**에 두 source columns와 trial rates를 직접 넣은 결과와 비교했다. Ion extent는 exact equality이며 stopping extent는 (CB.23)의 rigorous enclosure 안에 있다. 이어 (CB.21)의 polynomial이 certified \(x\)-interval 양 끝에서 각각 비음수와 비양수이고 그 안에서 strictly decreasing임을 확인했다. 이는 수축 estimate와 별도의 exact algebraic enclosure다.

Domain corners와 endpoint의 raw inventory를 직접 분류하여 (CB.7)의 count·energy 응답을 확인했다. 증명에서 쓰인 self-map, branch margin, positive log와 \(\bar q<1\) 부등식은 모두 rational comparisons로 계산했다. 이전 full generator·ODE·NCP 또는 기존 suite는 호출하지 않았다.

Root가 수행한 새 Wolfram scalar 검산에서도 ion-map derivative, fixed-point quadratic, stable small root·discriminant, \(T_x,T_s\), stopping의 1·2차 미분과 map derivative, atanh log-ratio 미분이 exact zero residual로 확인되었다. 그 실행 근거는 root의 `checks/wolfram_branch_geometry_scalar.wl` 및 `results/WOLFRAM_SCALAR_RAW.json`에 결속된다. `examples/COUPLED_BRANCH_WOLFRAM_INPUT.json`은 숫자 결속용 보조 자료이며, 실제 Wolfram 실행 입력은 `checks/wolfram_branch_geometry_scalar.wl`의 일반기호식과 전제다. 실제 실행 범위는 일반기호식 24개와 부등식 4개이며, 이 JSON의 숫자를 Wolfram에 주입하지 않았다.

실행 이후 채택 근거 라벨의 `KC1-KC8` 오기를 `KC1-KC7`로 교정했다. 과학 식·수치 입력·결과는 바뀌지 않았고, 당시 실행 identity는 CHECKS 파일에 그대로 남겼다. 현재 metadata가 달라진 의미와 변경 전후 hashes는 `results/COUPLED_BRANCH_METADATA_PATCH.json`에 별도로 기록한다. 이 label 교정을 위해 science를 다시 실행하지 않았다.

## 11. 닫힌 결과와 다음 연결

이번 분과에서 실제 source-bound selected subfamily에 대해 다음 연결을 완성했다: 초기 positive neutral stock → 고정 source columns → trial HI density와 thermal electron density → common capacity extents → reaction-changed raw atoms → 같은 atomic branch의 thermal EOS → unique endpoint와 residual certificate.

Root의 reaction-driven crossing construction은 같은 HI source event에 다른 \(\chi\)와 초기 재고를 둔 별도 문제다. 여기의 \(\chi=20\) self-map에서는 명시한 양의 margins 때문에 crossing이 일어나지 않는다. 이 조건을 제거해 branch를 이동시키는 문제는 root의 conservative crossing 결과와 연결한다. Geometry 뒤 actual parent energy가 변하는 경우에는 다른 분과의 off-grid source rebinding이 새 immutable columns를 제공한다. 그 다음에 동일한 domain·ownership·rate-bound 계약을 다시 평가하면 된다.

Full HI sharing family, 나머지 물리 channels, 온도 의존적인 finite-temperature rate closure 및 실제 time-accuracy budget은 이 두 사건의 algebraic endpoint certificate와 구별한 후속 범위다. 현재 결과는 그 후속 계산에 재사용할 수 있는 구체적인 positive conservative coupled endpoint와 수치가 있는 self-map/error contract다.
