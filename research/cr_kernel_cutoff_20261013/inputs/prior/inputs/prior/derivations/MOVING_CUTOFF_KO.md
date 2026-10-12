# 시간에 따라 움직이는 전자 cutoff의 입자수·운동에너지 보존

## 결과와 사용 범위

전자 kinetic energy의 분할면을 임의의 양의 C¹ 함수 \(W_c(t)\)로 정하면, active 전자에서 아래쪽 집단으로 향하는 연속 수송의 signed number flux는

\[
S_{c,d}=\int_{S^2}[\dot W_c-b(W_c,\boldsymbol n,t)]g_c\,d\Omega
\tag{MC1}
\]

이고 같은 경계의 kinetic-energy flux는 \(P_{c,d}=W_cS_{c,d}\)다. 여기서 \(b=dW/dt\)는 실제 입자의 연속 에너지 변화율이다. 충돌에서 cutoff 아래로 태어난 daughter들의 이관량은 따로 계산한 \((J_{c,N},J_{c,E})\)이며, 이때 에너지는 각 daughter의 실제 \(W\)다. 전체 이관은

\[
S_c=S_{c,d}+J_{c,N},\qquad
P_c=W_cS_{c,d}+J_{c,E}.
\tag{MC2}
\]

아래에서 Bianchi I의 팽창·전단에 의한 일, 연속 충돌 손실, branching collision을 포함해 두 집단의 모든 경계항이 정확히 상쇄함을 증명한다. 기존의 고정 cutoff 열적 편입식은 \(\dot W_c=0\), 고정 배경에서의 특수형으로 얻는다.

이 유도의 첫 부분은 같은 kinetic distribution을 두 영역으로 나누는 정확한 모멘트 항등식이다. 마지막 부분은 아래쪽 전자를 공통 온도의 비상대론적 열적 집단으로 편입하는 명시적 closure에 대한 온도 방정식을 구성한다. 해당 closure를 사용하는 조건과 추가 입력은 §8에 모았다.

## 1. 정의와 전제

1. 계량 부호는 \((-+++ )\), 시간 \(t\)는 Bianchi I의 수직 관측자의 proper time이다. 먼저 \(ds^2=-c^2dt^2+\sum_i a_i^2(t)(dx^i)^2\)를 사용한다. 직교 정규틀의 팽창 텐서는 \(K_{ij}=H_i\delta_{ij}\), \(H_i=\dot a_i/a_i\), \(\theta=\mathrm{tr}K\), \(\sigma_{ij}=K_{ij}-\theta\delta_{ij}/3\)다. 이 \(K\)는 팽창률 부호를 사용한다.
2. \(\boldsymbol p\)는 해당 틀에서 측정한 물리적 3-momentum이다. 전자 질량을 \(m_e\)라 하면
   \[
   \mathcal E=\sqrt{m_e^2c^4+c^2p^2},\quad W=\mathcal E-m_ec^2,\quad
   \boldsymbol v=\nabla_pW=\frac{c^2\boldsymbol p}{\mathcal E}.
   \tag{MC3}
   \]
3. \(f(t,\boldsymbol p)\,d^3p\)는 proper volume당 전자 수다. \(f\ge0\)이며 필요한 0차·1차 에너지·momentum 모멘트가 유한하다. 경계의 trace가 존재하고 무한대 flux가 사라지는 고전해를 먼저 다룬다. 적분형 항등식은 같은 trace와 적분 가능성을 갖춘 약해에도 적용한다.
4. 연속 운동량 변화는 \(\dot{\boldsymbol p}=-K\boldsymbol p+\boldsymbol F_c\)다. \(\boldsymbol F_c\)는 연속 충돌 drag 등의 운동량 변화율이며, \(b_c=\boldsymbol v\cdot\boldsymbol F_c\), \(b_g=-K_{ij}p_i v_j\), \(b=b_g+b_c\)로 쓴다. jump 충돌은 별도 collision operator \(\mathcal C\)에 둔다.
5. cutoff는 각도와 무관한 \(W_c(t)>0\)다. \(A(t)=\{W>W_c(t)\}\), \(B(t)=\{0\le W<W_c(t)\}\)로 정하고, 경계에 유한 질량의 delta가 없는 경우를 본문에서 쓴다. 원자적 분포의 threshold crossing은 대응 적분식의 signed transfer로 정의한다.
6. 주입원 \(q\)는 proper volume·proper time당 생성률이다. 기존 \(Q_e(W,t)=tA(W)\)는 방향 적분을 이미 끝낸 source다. 등방 birth를 선택하면 \(q_g=Q_e/(4\pi)\)로 각도 공간에 넣는다. 이 확장은 source의 총 정규화를 유지한다.
7. 열적 편입식 §6에서는 nuclei 수가 팽창으로 희석되고, 열적 nuclei·전자 집단은 공통 \(T\)의 비상대론적 이상기체라고 정한다. active 분포와 source·충돌이 \(\boldsymbol p\mapsto-\boldsymbol p\)에 대해 짝이면 평균 momentum은 0이면서 비등방 stress는 남을 수 있다. 이 조건은 geodesic gas rest frame의 scalar 온도 closure와 양립한다.

단위는 본문에서 \(W,W_c\)에 joule, \(t\)에 second, 길이에 metre를 쓴다. eV 표를 사용할 때 \(W_J=\epsilon_{\rm eV}W_{\rm eV}\), \(g_J=g_{\rm eV}/\epsilon_{\rm eV}\)로 변환한다. \(\epsilon_{\rm eV}=1.602176634\times10^{-19}\,\mathrm{J/eV}\).

## 2. Bianchi I 운동량과 연속 수송식

공간 병진 대칭으로 보존되는 covariant momentum을 \(P_i\)라 하면 물리적 성분은 \(p_i=P_i/a_i\)다. 따라서 자유 전자는

\[
\dot p_i=-H_i p_i,\qquad
\dot W\big|_g=-\sum_iH_ip_iv_i
=-\frac{\theta}{3}p v-\sigma_{ij}p_iv_j.
\tag{MC4}
\]

직교틀에서의 proper-volume 밀도는 다음 보존형 수송식을 만족한다.

\[
\partial_t f+\theta f+
\nabla_p\cdot[(-K\boldsymbol p+\boldsymbol F_c)f]
=q+\mathcal C[f].
\tag{MC5}
\]

자유 수송에서는 \(\nabla_p\cdot(-K\boldsymbol p)=-\theta\)이므로 (MC5)는 궤적을 따른 \(df/dt=0\)와 같다. \(\theta f\)는 proper volume의 변화와 운동량 공간의 수축을 동시에 올바르게 반영한다.

\(\boldsymbol n=\boldsymbol p/p\), \(v=dW/dp\)를 쓰면

\[
g(W,\boldsymbol n,t)=\frac{p^2}{v}f(t,p\boldsymbol n),\qquad
d^3p=\frac{p^2}{v}dW\,d\Omega.
\tag{MC6}
\]

이에 따라 (MC5)는

\[
\partial_tg+\theta g+\partial_W(bg)+
\nabla_{\!\Omega}\cdot(\dot{\boldsymbol n}\,g)
=q_g+\mathcal C_g,
\tag{MC7}
\]

\[
\dot{\boldsymbol n}\big|_g=-K\boldsymbol n+
(\boldsymbol n\cdot K\boldsymbol n)\boldsymbol n
\tag{MC8}
\]

가 된다. 구면에서의 angular divergence는 0차와 에너지 모멘트를 적분할 때 상쇄한다. 비등방성은 에너지 drift의 \(\sigma_{ij}p_iv_j\)와 stress에 유지된다.

물리적 pressure tensor를

\[
\Pi_{A,ij}=\int_Ap_iv_jf\,d^3p,
\quad P_A=\frac13\mathrm{tr}\Pi_A,
\quad\pi_{A,ij}=\Pi_{A,ij}-P_A\delta_{ij}
\tag{MC9}
\]

로 정의하면

\[
\int_A b_g f\,d^3p=-K:\Pi_A=-\theta P_A-\sigma:\pi_A.
\tag{MC10}
\]

이 식은 전자 각도분포의 등방성을 요구하지 않는다. \(pv=W(W+2m_ec^2)/(W+m_ec^2)\)이므로 비상대론적 극한에서 \(\mathrm{tr}\Pi_A\to2U_A\), 초상대론적 극한에서는 \(\mathrm{tr}\Pi_A\to U_A\)를 얻는다.

## 3. 움직이는 cutoff의 일반 모멘트 정리

\(M_{\psi,A}=\int_A\psi(t,\boldsymbol p)f\,d^3p\)라 하자. cutoff sphere의 반지름은

\[
p_c=\frac{\sqrt{W_c(W_c+2m_ec^2)}}c,
\qquad\dot p_c=\frac{\dot W_c}{v_c}.
\tag{MC11}
\]

active 영역의 안쪽 경계 외향 법선은 \(-\boldsymbol n\)이다. 경계에 대한 상대 flux는

\[
[\dot{\boldsymbol p}-\dot p_c\boldsymbol n]\cdot(-\boldsymbol n)
\,f_c p_c^2d\Omega
=[\dot W_c-b_c^{\rm tot}]g_c\,d\Omega,
\tag{MC12}
\]

여기서 \(b_c^{\rm tot}=b(W_c,\boldsymbol n,t)\)다. 혼동을 피하려고 연속 충돌 drift 자체의 기호 \(b_c\)와 경계에서 평가한 전체 drift를 구별했다.

Reynolds 적분 미분식과 (MC5)를 적용하면

\[
\begin{split}
\dot M_{\psi,A}+\theta M_{\psi,A}
={}&\int_A\psi(q+\mathcal C)\,d^3p
+\int_A[\partial_t\psi+
(-K\boldsymbol p+\boldsymbol F_c)\cdot\nabla_p\psi]f\,d^3p\\
&-\int_{S^2}\psi(W_c,\boldsymbol n)
[\dot W_c-b(W_c,\boldsymbol n)]g_c\,d\Omega.
\end{split}
\tag{MC13}
\]

증명은 두 단계다. 첫째, 움직이는 안쪽 경계의 영역 감소가 \(-\int\psi\dot p_cf_cp_c^2d\Omega\)를 준다. 둘째, 수송식의 momentum divergence를 부분적분하면 경계의 실제 수송 \(+\int\psi(\dot{\boldsymbol p}\cdot\boldsymbol n)f_cp_c^2d\Omega\)와 내부의 \(\dot{\boldsymbol p}\cdot\nabla_p\psi\)가 남는다. 두 경계항을 합치고 \(g_c=p_c^2f_c/v_c\)를 사용하면 (MC13)이다.

\(\psi=1,W,p_i\)를 택하고

\[
n_A=\int_A f\,d^3p,\quad U_A=\int_AWf\,d^3p,\quad
M_{A,i}=\int_Ap_if\,d^3p,\quad
P_{h,d}=-\int_A b_c f\,d^3p
\tag{MC14}
\]

로 두면

\[
\dot n_A+\theta n_A=\int_A(q+\mathcal C)d^3p-S_{c,d},
\tag{MC15}
\]

\[
\dot U_A+\theta U_A+K:\Pi_A
=\int_AW(q+\mathcal C)d^3p-P_{h,d}-W_cS_{c,d},
\tag{MC16}
\]

\[
\dot M_{A,i}+\theta M_{A,i}+K_{ij}M_{A,j}
=\int_Ap_i(q+\mathcal C)d^3p
+\int_AF_{c,i}f\,d^3p-M_{c,d,i},
\tag{MC17}
\]

\[
M_{c,d,i}=p_c\int_{S^2}n_i
[\dot W_c-b(W_c,\boldsymbol n)]g_c\,d\Omega
\tag{MC18}
\]

를 얻는다. 운동량 이관은 에너지와 함께 별도의 벡터량으로 유지된다. 짝분포에서는 (MC18)이 0이고, (MC10)의 전단 일은 남는다.

### 경계 trace와 signed transfer

상대 에너지 속도를 \(a=b-\dot W_c\)라 하자. 하나의 연속 분포를 나눌 때 양쪽 trace가 같다. 서로 다른 active·하부 표현을 붙일 때는 \(a<0\)에서 active 쪽 trace, \(a>0\)에서 하부 쪽 trace를 사용하는 동일한 upwind flux를 두 ledger에 반대 부호로 넣는다. 따라서

\[
S_{c,d}=-\int a\,g_{\rm upwind}\,d\Omega.
\tag{MC19}
\]

\(S_{c,d}>0\)는 아래쪽 이관, \(S_{c,d}<0\)는 active 영역으로의 이관을 뜻한다. cutoff가 내려가거나 수축 방향의 geodesic blue shift가 우세하면 아래쪽 분포의 trace가 실제 입력이 된다.

## 4. 두 kinetic 영역에서의 정확한 상쇄

하부 영역 \(B\)에 같은 계산을 적용하면 (MC13)의 경계항이 양의 부호로 들어간다. 따라서 수·에너지·momentum 각각에서

\[
(-S_{c,d})+(+S_{c,d})=0,
\quad(-W_cS_{c,d})+(+W_cS_{c,d})=0,
\quad(-\boldsymbol M_{c,d})+(+\boldsymbol M_{c,d})=0.
\tag{MC20}
\]

이 상쇄는 \(\dot W_c\)의 부호·크기와 \(f\)의 angular anisotropy에 무관하다. 완전한 kinetic partition의 \(n_A+n_B\), \(U_A+U_B\), \(\boldsymbol M_A+\boldsymbol M_B\)는 분할면 선택에 독립적이다. energy work 역시 \(K:\Pi_A+K:\Pi_B=K:(\Pi_A+\Pi_B)\)로 합쳐진다.

여기서 분할에 독립적인 양은 동일한 \(f\)의 두 적분을 더한 총 모멘트다. §6에서는 하부 분포를 선택한 열적 방정식으로 표현하며, 그 표현에서 얻는 온도와 stress는 하부 closure 및 interface trace에 따라 정해진다.

## 5. Branching collision의 daughter ledger

active parent의 상태 \(x\)에서 충돌 outcome \(\chi\)가 발생하는 event-rate measure를 \(d\Gamma(x,\chi)\)라 하자. outcome은 daughter 전자들 \(\{\boldsymbol p_j\}_{j=1}^{\nu}\)와 매질에 남은 에너지를 정한다. 각 event에서

\[
\ell_E=W_x-\sum_{j=1}^{\nu}W_j,
\qquad\ell_{N}=\nu-1,
\qquad\boldsymbol\ell_p=\boldsymbol p_x-\sum_j\boldsymbol p_j.
\tag{MC21}
\]

\(\ell_E\)는 채택한 충돌 모형에 따라 열, 원자 binding·excitation, recoil 등의 ledger로 배분한다. \(L_E=\int\ell_Ed\Gamma=P_{h,j}+L_{\rm at}\)처럼 나누고, \(\mathcal R_{\rm sec}=\int(\nu-1)d\Gamma\)라 쓰자. cutoff 아래의 daughter 수와 에너지는

\[
J_{c,N}=\int\sum_j\mathbf1_{W_j<W_c}\,d\Gamma,
\quad
J_{c,E}=\int\sum_jW_j\mathbf1_{W_j<W_c}\,d\Gamma,
\tag{MC22}
\]

\[
\boldsymbol J_{c,p}=\int\sum_j\boldsymbol p_j\mathbf1_{W_j<W_c}\,d\Gamma.
\tag{MC23}
\]

충돌 operator의 active 모멘트는 event마다 daughter gain에서 parent loss를 빼서

\[
\int_A\mathcal C\,d^3p=\mathcal R_{\rm sec}-J_{c,N},
\quad
\int_AW\mathcal C\,d^3p=-P_{h,j}-L_{\rm at}-J_{c,E}
\tag{MC24}
\]

가 된다. 이는 단순한 두 전자 이온화뿐 아니라 유한한 daughter 수·에너지 모멘트를 갖는 branching에도 성립한다. momentum 역시 \(-\int\boldsymbol\ell_pd\Gamma-\boldsymbol J_{c,p}\)다.

이제 \(P_h=P_{h,d}+P_{h,j}\), source 모멘트를 \(Q_{A,N},Q_{A,E}\)로 쓰면

\[
\boxed{\dot n_A+\theta n_A=Q_{A,N}+\mathcal R_{\rm sec}-S_c},
\tag{MC25}
\]

\[
\boxed{\dot U_A+\theta U_A+K:\Pi_A
=Q_{A,E}-P_h-L_{\rm at}-P_c}.
\tag{MC26}
\]

이 식에서 \(\mathcal R_{\rm sec}\)는 active와 하부 daughter를 모두 포함한 새 전자의 생성 수다. 하부 daughter의 편입 수는 이미 \(J_{c,N}\)에 들어 있다.

위 branching 표현은 기존 cascade와 같은 active-parent 충돌에 적용한다. 하부 입자를 active로 올리는 collision을 추가할 때에는 그 event에서 제거하는 하부 수·에너지와 생성하는 active 수·에너지를 동일한 signed interface ledger에 넣는다. 완전한 양쪽 collision operator를 사용하는 경우에는 (MC13)의 \(\mathcal C\) 모멘트식이 그대로 출발식이다.

### Daughter 에너지의 판별 예

이온화 문턱을 \(I\), 두 daughter 에너지를 \(6.36\,\mathrm{eV}\)와 \(0.04\,\mathrm{eV}\)로 정한 한 event를 보자. parent 에너지는 \(I+6.40\,\mathrm{eV}\), cutoff는 \(0.10\,\mathrm{eV}\)다. 추가 전자는 하나이고 active daughter도 하나이므로 active 수 변화는 0이다. active 에너지 변화는 \(-I-0.04\,\mathrm{eV}\), 원자 ledger는 \(+I\), 하부 ledger는 \(+0.04\,\mathrm{eV}\)로 정확히 합이 0이다. 이 event의 \(J_{c,E}/J_{c,N}\)는 \(0.04\,\mathrm{eV}\)다. 이 대수 예는 daughter 에너지와 경계의 연속 수송 에너지를 구별하는 판별식이다.

## 6. 열적 편입 closure와 팽창 중의 온도 방정식

하부 전자를 nuclei와 공통 온도 \(T\)의 비상대론적 이상기체에 편입한다고 정하자. \(n_g=n_{\rm nuc}+n_{e,\rm th}\),

\[
u_{\rm th}=\frac32k_BTn_g,\quad
P_{\rm th}=k_BTn_g,\quad
C_V=\frac32k_Bn_g,\quad\bar e_{\rm th}=\frac32k_BT.
\tag{MC27}
\]

source 자체가 현재 cutoff 아래에서 birth를 만드는 경우 그 수·에너지를 \(Q_{B,N},Q_{B,E}\)로 기록한다. 아래 두 방정식에 같은 \((S_c,P_c)\)를 넣는다.

\[
\dot n_{e,\rm th}+\theta n_{e,\rm th}=Q_{B,N}+S_c,
\tag{MC28}
\]

\[
\dot u_{\rm th}+\theta(u_{\rm th}+P_{\rm th})
=Q_{B,E}+P_h+P_c+Q_{\rm other}.
\tag{MC29}
\]

\(\dot n_{\rm nuc}+\theta n_{\rm nuc}=0\)과 (MC27)를 대입하면

\[
\boxed{C_V\dot T+P_{\rm th}\theta
=P_h+P_c+Q_{B,E}+Q_{\rm other}
-\bar e_{\rm th}(S_c+Q_{B,N})}.
\tag{MC30}
\]

source 이외에 열적 입자 수를 바꾸는 반응을 넣으면 (MC28)의 해당 순생성률과 (MC30)의 \(-\bar e_{\rm th}\) 항을 함께 추가한다. 식 (MC30)의 cutoff 기여를 풀면

\[
P_c-\bar e_{\rm th}S_c
=(W_c-\bar e_{\rm th})S_{c,d}
+\int\sum_{W_j<W_c}(W_j-\bar e_{\rm th})\,d\Gamma.
\tag{MC31}
\]

새로 편입한 전자의 에너지가 열적 집단의 입자당 에너지보다 작거나 큰 경우를 이 식이 모두 처리한다. 분할·편입 수와 에너지의 대응을 유지하면 별도의 임의 온도 보정이 필요하지 않다.

### 전체 에너지·입자수의 닫힘

원자 저장 에너지 \(u_{\rm at}\)가 \(\dot u_{\rm at}+\theta u_{\rm at}=L_{\rm at}\)를 만족하는 convention을 사용하면 (MC26)+(MC29)의 합은

\[
\frac d{dt}(U_A+u_{\rm th}+u_{\rm at})
+\theta(U_A+u_{\rm th}+u_{\rm at})
+K:\Pi_A+\theta P_{\rm th}
=Q_{A,E}+Q_{B,E}+Q_{\rm other}.
\tag{MC32}
\]

전자 수는

\[
\frac d{dt}(n_A+n_{e,\rm th})
+\theta(n_A+n_{e,\rm th})
=Q_{A,N}+Q_{B,N}+\mathcal R_{\rm sec}.
\tag{MC33}
\]

결과적으로 연속·jump 열, cutoff number, cutoff energy는 각 ledger 사이의 내부 이관으로 정확히 닫힌다. 원자 저장 에너지의 상태 정의와 방출 채널이 달라질 경우 해당 외부 source·sink를 양쪽에 동일하게 포함한다.

### 온도에 따라 정한 cutoff

\(W_c=\chi k_BT\)이고 \(\chi\)가 일정하다고 정하자. \(\rho_c=\int g_{\rm upwind}(W_c,\Omega)d\Omega\), \(B_c=\int b(W_c,\Omega)g_{\rm upwind}d\Omega\)이면

\[
S_{c,d}=\chi k_B\rho_c\dot T-B_c.
\tag{MC34}
\]

해당 upwind branch가 정해진 순간에서 (MC30)은

\[
\begin{split}
\big[C_V-\chi k_B(W_c-\bar e_{\rm th})\rho_c\big]\dot T
+P_{\rm th}\theta
={}&P_h+Q_{B,E}+Q_{\rm other}-\bar e_{\rm th}Q_{B,N}\\
&-(W_c-\bar e_{\rm th})B_c
+J_{c,E}-\bar e_{\rm th}J_{c,N}.
\end{split}
\tag{MC35}
\]

이 식은 cutoff가 \(T\)의 함수일 때 경계 이동과 온도 갱신을 같은 implicit residual에서 풀 수 있게 한다. 분포 trace와 upwind 선택도 같은 상대 속도 \(b-\dot W_c\)를 사용한다. 해당 branch의 bracket 계수가 0이 아닌 구간에서 \(\dot T\)에 대해 대수적으로 풀 수 있다.

## 7. 유한 cutoff 변경을 위한 정확한 재분배

한 순간의 분포를 고정하고 cutoff를 \(w_0\)에서 \(w_1\)로 옮기면, active에서 하부로 넘기는 signed 양은

\[
\Delta N_c=\int_{w_0}^{w_1}\bar g(W)dW,\quad
\Delta U_c=\int_{w_0}^{w_1}W\bar g(W)dW,
\quad
\Delta\boldsymbol M_c=\int_{w_0}^{w_1}\!\int p(W)\boldsymbol n g\,d\Omega\,dW.
\tag{MC36}
\]

여기서 \(\bar g=\int gd\Omega\)다. active ledger에는 이 양을 빼고 하부 ledger에는 더한다. 각 bin의 일부만 cutoff를 통과한 경우에도 적분 구간만으로 바로 적용된다. (MC36)을 infinitesimal cutoff 이동에 적용하면 \(dU_c=W_c\,dN_c\)가 되어 (MC1)–(MC2)의 경계 이동 부분을 재현한다.

예를 들어 \(\bar g=g_0\)가 일정하고 cutoff가 \(0.1\)에서 \(0.2\,\mathrm{eV}\)로 이동하면 \(\Delta N_c=0.1g_0\), \(\Delta U_c=0.015g_0\,\mathrm{eV}\)다. 이관된 집단의 평균 에너지는 양 끝점의 평균 \(0.15\,\mathrm{eV}\)로 정해진다.

## 8. 기존 BASS_CR 결과와의 연결 및 다음 입력

기존 A2 ledger는 고정 \(W_c=0.1\,\mathrm{eV}\), 고정 배경에서 저장한 \(S_c,P_c\)를 사용한다. 이론식의 대응은 다음과 같다.

| 기존 항목 | 이번 식의 의미 | 진화 배경에 필요한 추가 정보 |
|---|---|---|
| active stock | \(n_A,U_A\) | stress \(\Pi_A\), cutoff trace \(g_c\) |
| continuous heat | \(P_h\)의 연속 충돌 부분 | local 배경을 사용한 \(b_c\) |
| cutoff number | \(S_c=S_{c,d}+J_{c,N}\) | 경계 이동률 및 방향별 상대 flux |
| cutoff energy | \(P_c=W_cS_{c,d}+J_{c,E}\) | 연속·jump 분리, daughter 실제 에너지 |
| thermal join | (MC28)–(MC30) | \(n_g,T,\theta\), 하부 재구성의 조건 |
| linear source | \(Q_e=tA\)의 두 영역 적분 | source의 proper-time·proper-volume 변환 |

### 저장된 source ghost의 정확한 대응

복원한 원문 DERIVATION_KO.md §6.1과 causal_cascade.py의 project(), summarize()를 확인했다. 원 project()는 실제 \(W\le0.1\,\mathrm{eV}\) daughter에 \((N,W N)\)을 더하고, 첫 active node와 ghost 사이의 양의 projection weight에도 \((N,0.1\,\mathrm{eV}\,N)\)을 더한다. source에도 같은 projection이 적용되어 저장된 cutoff derivative에는 source ghost가 포함된다.

본문에서 분리한 하부 source \(Q_{B,N},Q_{B,E}\)에 그 source projection 성분을 포함하면 기존 총량의 대응은

\[
S_{\mathrm{cut,stored}}=S_c+Q_{B,N},\qquad
P_{\mathrm{cut,stored}}=P_c+Q_{B,E}.
\tag{MC37}
\]

따라서 기존 저장 총량을 바로 사용하는 interface는 (MC30)의 \(P_c+Q_{B,E}\)를 \(P_{\mathrm{cut,stored}}\), \(S_c+Q_{B,N}\)를 \(S_{\mathrm{cut,stored}}\)로 한 번씩 대체한다. 세분화한 interface는 먼저 source 부분을 분리하여 본문의 \((S_c,P_c,Q_B)\)를 각각 입력한다. 이 대응은 기존 A2의 \(P_h+P_{\mathrm{cut,stored}}\), \(S_{\mathrm{cut,stored}}\) 사용을 보존한다.

현재 선택한 source 창과 정규화는 유지한다. 새 배경에서 source가 \(tA(W)\) 형태를 유지하도록 정할 경우에는 \(t\)의 원점과 \(A\)의 시간 의존성을 명시한다. 고정 배경의 저장된 scalar cutoff 총량을 재사용하는 범위는 그 고정 cutoff 응답이며, 진화하는 interface의 계산은 위 표의 trace·stress·event moment를 입력으로 한다.

열적 closure의 구성 단계는 (i) 단방향 capture라면 active trace에서 flux 계산, (ii) 양방향 이관이라면 하부 trace를 재구성하여 하나의 upwind flux 공유, (iii) source와 daughter 에너지를 각각 적분, (iv) scalar 온도식과 active stress work를 동시에 갱신하는 순서다. 하부 표현을 Maxwellian 등으로 정하는 물리 선택은 그 표현의 normalization과 momentum·energy moments를 함께 지정한다.

이번 결과의 새 기여는 기존 고정 cutoff의 \((S_c,P_c)\)를 움직이는 분할면·Bianchi stress work·jump daughter·thermal particle count가 함께 닫히는 하나의 interface로 연결한 데 있다. 기존 수송 실행이나 source 진폭 계산은 반복하지 않았다.

## 9. 검토용 판별 지점

- 고정 cutoff, \(b<0\): \(S_{c,d}=-\int bg_c>0\)이고 active 수가 감소한다.
- 순수 분할면 상승, \(b=0\): \(S_{c,d}=\dot W_c\bar g_c>0\)이며 하부 영역 증가량과 같다.
- 공이동 분할면, 모든 방향에서 \(b(W_c)=\dot W_c\): 연속 boundary transfer가 0이다.
- 각도 비등방 분포: \(K:\Pi_A=\theta P_A+\sigma:\pi_A\)가 남는다.
- source·collision·팽창이 없는 유한 재분배: (MC36)에서 active+하부 수·에너지·momentum이 각각 보존된다.
- branching event: (MC21)–(MC24)의 합으로 daughter 수와 에너지가 모두 닫힌다.
- \(\theta=0,\dot W_c=0,Q_B=0\): (MC30)은 기존 \(C_V\dot T=P_h+P_c-(3/2)k_BT S_c\)를 재현한다.

이 판별식들은 위 증명의 부호·차원·분할 대응을 직접 확인한다. 독립 검토자는 (MC13)의 inner normal 부호, (MC24)의 daughter multiplicity, (MC30)의 열적 입자수 항, (MC35)의 implicit coefficient를 우선 검토할 수 있다.

## 10. 원전과 근거 상태

1. Ho Lee and Ernesto Nungesser, *Bianchi I solutions of the Einstein–Boltzmann system with a positive cosmological constant*, arXiv:1705.07009, DOI:10.1063/1.4985935. 원문 PDF https://arxiv.org/pdf/1705.07009 를 2026-10-12 열람했다. §1.1의 orthonormal/covariant momentum 대응, §3의 kinetic energy-momentum tensor와 covariant momentum에서의 homogeneous Boltzmann 식을 확인했다. 본문의 물리 momentum·명시적 c·움직이는 kinetic-energy cutoff 식은 여기서 직접 유도했다.
2. P. Lidström, *Moving regions in Euclidean space and Reynolds’ transport theorem*, Mathematics and Mechanics of Solids 16(4), 366–380 (2011), DOI:10.1177/1081286510393805. https://journals.sagepub.com/doi/10.1177/1081286510393805 에서 서지와 abstract를 2026-10-12 확인했다. 본문의 움직이는 경계 공식은 §3에서 적분 미분과 부분적분으로 직접 증명했다.
3. 복원한 BASS_CR source-binding 단위의 DERIVATION_KO.md §6과 inputs/source_lineage/sources/research/cr_phys02b_20261010/src/causal_cascade.py의 project(), functionals(), summarize()를 직접 읽어 fixed-cutoff·daughter·source ghost 의미를 확인했다. 읽은 파일의 SHA-256은 이 분과의 SOURCE_BINDING.json에 기록한다. 본 분과는 source-binding 수치 자체를 새 실행하지 않았다.

근거 상태: (MC1)–(MC37)은 §1의 조건 아래 직접 유도한 항등식·closure 구성과 기존 코드에 대한 입력 대응이다. 원전의 배경 geometry·moment 정의를 확인했고, 독립 논증 검토는 통합 루프 검토자에게 인계한다. 새로운 불가능성 정리는 제안하지 않았다.
