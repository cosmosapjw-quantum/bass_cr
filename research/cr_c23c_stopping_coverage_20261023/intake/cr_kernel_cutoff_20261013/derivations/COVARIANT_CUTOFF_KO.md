# 움직이는 cutoff의 공변 경계식과 실제 사건 피드백의 연결

연구 단위: CR-THEORY-KERNEL-CUTOFF-20261013. 직접 유도: /root.

근거 상태: 아래 CV1–CV3 및 CP1은 명시한 전제에서의 직접 유도다. xAct는 CV1의 매끄러운 selector 곱 법칙, CV2의 tensor 수축과 CV3의 chain rule을 실제 검산했다. 약한 trace 극한과 고정점 정리는 본문 증명에 의존한다. 이전 MC34–MC36의 균질 경계항과 유효 열용량은 재사용하며 새 결과로 중복 계상하지 않는다.

## 1. Convention과 spectral balance

계량 부호는 $(-,+,+,+)$, 공행 단위 시간벡터는 $n^an_a=-1$, $h^{ab}=g^{ab}+n^an^b$, 고유시간 미분은 $\dot f=c n^a\nabla_af$다. $W\ge0$는 $n^a$가 측정한 전자의 운동에너지(J)이고, $E_c(x)=\chi k_BT(x)$, $\chi>0$다. $c$는 광속이며 cutoff 기호와 구별한다.

에너지 축에 대한 수 전류 밀도 $j^a(W,x)$와 에너지 좌표 방향의 수 flux $\mathcal F(W,x)$가 다음 보존식을 만족한다고 가정한다.

$$
\nabla_a j^a+\partial_W\mathcal F=\mathcal C.
\tag{CV.1}
$$

$j^a$의 단위는 $\mathrm{m^{-2}s^{-1}J^{-1}}$, $\mathcal F$는 $\mathrm{m^{-3}s^{-1}}$, $\mathcal C$는 $\mathrm{m^{-3}s^{-1}J^{-1}}$다. 이 식은 선택한 observer의 에너지 좌표에서 쓰는 보존형 kinetic 방정식이다. 기하학적 energy drift와 observer work는 $\mathcal F$에 포함하고 collision/source 내용은 $\mathcal C$에 결속한다. 일반 kinetic 방정식에서 (CV.1)로 가는 measure 선택은 기존 Bianchi transport 계약을 따른다.

필요 전제는 유한 0차·1차 에너지 moment, $W=E_c$ 양쪽의 적절한 trace, 적분과 미분 교환 또는 이에 대응하는 약한 정식화다. 아래에서는 $\mathcal F(0)=\mathcal F(\infty)=0$과 $\lim_{W\to\infty}W\mathcal F(W)=0$을 쓴다. 마지막 조건은 높은 에너지 영역의 1차 moment에서 부분적분 끝항을 없앤다. 실제 모형에 끝점 유입이 있으면 수 및 에너지 끝항을 별도 source로 유지한다.

## 2. CV1: 경계의 입자수와 운동에너지 전달

낮은 에너지 쪽의 전류를

$$
J_B^a=\int_0^{E_c}j^a\,dW,\qquad
K_B^a=\int_0^{E_c}Wj^a\,dW
\tag{CV.2}
$$

로 정의한다. $K_B^a$는 선택 observer에 대한 운동에너지 전류이며 stress tensor 자체와 동일시하지 않는다. 이동 상한을 미분하고 (CV.1)을 사용하면

$$
\boxed{S_c=j_c^a\nabla_aE_c-\mathcal F_c,}
\tag{CV.3}
$$

$$
\boxed{\nabla_aJ_B^a=\int_0^{E_c}\mathcal C\,dW+S_c,}
\tag{CV.4}
$$

$$
\boxed{\nabla_aK_B^a=\int_0^{E_c}(W\mathcal C+\mathcal F)\,dW+E_cS_c.}
\tag{CV.5}
$$

**유도.** 수 전류에는 이동 상한의 항 $j_c^a\nabla_aE_c$와 $-\int_0^{E_c}\partial_W\mathcal F\,dW=-\mathcal F_c$가 생긴다. 에너지 식에서는

$$
-\int_0^{E_c}W\partial_W\mathcal F\,dW
=-E_c\mathcal F_c+\int_0^{E_c}\mathcal F\,dW
$$

를 사용한다. 따라서 경계 에너지의 계수는 cutoff에 있는 전자의 실제 운동에너지 $E_c$다. 높은 에너지 쪽 $(E_c,\infty)$에는 각각 $-S_c$와 $-E_cS_c$가 생겨 두 영역의 합에서 정확히 소거된다. $\int\mathcal F\,dW$는 bulk energy drift이며 경계 source와 중복하지 않는다. $\square$

약한 정식화에서는 $H(E_c-W)$를 매끄러운 selector $H_\epsilon$로 대체한다. 곱 법칙의 추가 항은 $H_\epsilon'(E_c-W)(j^a\nabla_aE_c-\mathcal F)$이며, trace 및 적분가능 지배 조건 아래 $\epsilon\to0$에서 (CV.3)을 얻는다. 실제 xAct 계산은 매끄러운 selector의 곱 법칙과 두 partition의 소거를 확인한다. 분포 극한의 정당화는 위 가정이 제공한다.

## 3. CV2: rest mass를 뺀 열적 에너지 source

경계 전달의 총 전자 4-momentum source를

$$
F_c^b=\frac{E_c+m_ec^2}{c}S_c n^b+h^{ba}M_a
\tag{CV.6}
$$

로 분해한다. $M_a$는 경계의 공간 운동량 전달을 나타내며 비등방 분포에서도 허용한다. $n_bh^{ba}=0$이므로

$$
\boxed{-c n_bF_c^b-m_ec^2S_c=E_cS_c.}
\tag{CV.7}
$$

이는 상대론적 총 에너지에서 전자 rest mass를 빼면 사건 장부의 운동에너지가 남는다는 정확한 수축식이다. 공간 운동량 source를 0으로 가정해 얻은 식이 아니다.

공행 전자 수 전류가 $J_e^a=c n_e n^a$인 even/angular closure에서는

$$
K^{ab}=T_e^{ab}-m_ec^2 n_e n^an^b
$$

에 대해

$$
\boxed{-c n_b\nabla_aK^{ab}
=-c n_b\nabla_aT_e^{ab}-m_ec^2\nabla_aJ_e^a.}
\tag{CV.8}
$$

**증명.** $n_bn^b=-1$의 미분에서 $n_b\nabla_an^b=0$이다. 따라서 $n_b\nabla_a(n_en^an^b)=-\nabla_a(n_en^a)$이고, $J_e^a$ 정의를 대입하면 (CV.8)을 얻는다. $\square$ 이 scalar rest-mass subtraction은 명시한 공행 수 전류 closure에 적용한다. 비영 tilt 전류는 그 flux를 포함한 별도 tensor 분해를 요구한다.

## 4. CV3: 기존 Bianchi 경계항과의 일치

균질 공행 spectral current $j_c^a=c\rho_c n^a$이면

$$
S_c=\chi k_B\rho_c\dot T-\mathcal F_c.
\tag{CV.9}
$$

기존 Bianchi 에너지 drift flux $B_c=\int b\,g_c\,d\Omega$를 $\mathcal F_c$로 대입하면 이전 MC34와 정확히 같다. $b=dW/d\tau$는 signed drift다. 순수 감속 $b<0$과 정지 cutoff에서는 $S_c=-B_c>0$이어서 active 전자가 열적 영역으로 들어간다.

열적 EOS $U=c_vNT$, $c_v=3k_B/2$에서 cutoff 재분류가 $dU=E_c\,dN$를 만들므로

$$
\big[c_vN-\chi k_B(E_c-c_vT)\rho_c\big]\,dT
=dU_{\rm fixed}-c_vT\,dN_{\rm fixed}.
\tag{CV.10}
$$

셀 입자수 spectrum을 사용하면 $\rho_c$도 셀 입자수/J이고 (CV.10)의 대괄호는 J/K다. 부피당 spectrum에서는 $N,U$ 대신 number density, energy density를 써서 같은 항등식을 얻는다. 이 열용량 계수는 이전 MC35의 재사용 결과다. 이번 루프의 추가 내용은 이 계수가 유한 EOS root의 실제 미분임을 보이고, root 및 사건 피드백 오차를 계산 가능한 형태로 연결하는 것이다.

## 5. CP1: 사건 extent에서 cutoff–온도–조성 feedback까지

### 5.1 고정 raw inventory와 재분류

현재 step의 초기 상태, 입자 에너지 격자, 시간 및 active donor mask를 고정한다. 초기 active mask는 $W_j>E_c^n$이며 cutoff 아래에 보관한 dormant trace를 active collision donor에 더하지 않는다. 각 trial descriptor $z=(T,n_e,\boldsymbol\chi_{\rm ion})$에서 이전 FP.7–FP.8의 공통 사건 extent $\xi_r(z)\ge0$를 계산한다. 원자 kernel에서 생성된 두 딸, cutoff ghost, excitation energy에는 같은 extent를 곱한다.

$$
x_h(z)=x^n+\sum_rs_r\xi_r(z).
\tag{CP.1}
$$

이 $x_h$는 cutoff 재분류 전의 한 고정 raw inventory다. 각 inner EOS 반복은 $x_h(z)$를 처음부터 재분류한다. 직전 cutoff 반복의 열적 상태에 다시 같은 이동량을 누적하지 않는다. $n_e$는 이번 baseline에서 실제 Coulomb bath인 $N_{e,\rm th}/V$로 정의한다.

고정 trial cutoff $E_c(T)$에 대해 raw inventory의 선형 moment는

$$
N(T;z)=N^n(T)+\sum_r\nu_{N,r}(T)\xi_r(z),\qquad
U(T;z)=U^n(T)+\sum_r\nu_{U,r}(T)\xi_r(z).
\tag{CP.2}
$$

원자 measure에서 첫 $k$개 에너지 원자가 thermal이면 계수는 실제 사건 열에서 직접 계산된다.

$$
\nu_{N,r}(k)=s_{N_B,r}+\sum_{j\le k}s_{A_j,r},\qquad
\nu_{U,r}(k)=s_{U_B,r}+\sum_{j\le k}W_js_{A_j,r}.
\tag{CP.3}
$$

$N_B$는 핵수와 unresolved thermal electrons를 포함하고, $U_B$는 unresolved thermal energy다. 연속 spectrum을 선택한 경우에는 trial $z$에 독립인 고정 선형 기저로 양의 0차·1차 moment 보존 재구성을 정하고, 그 기저함수를 적분하여 같은 $\nu$를 만든다. 그러한 재구성의 실제 선택은 raw 원자 measure와 별도로 결속한다. 비선형·adaptive 기저가 $z$에 따라 변하면 그 추가 응답을 별도로 미분·제한해야 하며 (CP.2)의 고정 계수 공식을 그대로 적용하지 않는다.

### 5.2 유효 열용량이 feedback gain으로 들어가는 위치

고정 $z$에서

$$
F(T;z)=c_vT N(T;z)-U(T;z)=0
\tag{CP.4}
$$

의 선택된 root를 $\mathcal T(z)$라 하자. 연속 spectrum에서는 $I=[T_-,T_+]$에서 양의 inventory, root bracket 및

$$
F_T=C_{\rm eff}=c_vN-\chi k_B(E_c-c_vT)\rho_c\ge m>0
\tag{CP.5}
$$

를 모든 허용 $z$에 대해 확보한다. 이때 root가 유일하며 암묵 미분으로

$$
\boxed{D_z\mathcal T
=\frac{\sum_r[\nu_{U,r}(\mathcal T)-c_v\mathcal T\nu_{N,r}(\mathcal T)]D_z\xi_r}{C_{\rm eff}}.}
\tag{CP.6}
$$

이것은 사건의 실제 에너지와 그 사건이 추가하는 열적 입자수의 평균 에너지 차를 사용한다. $|\nu_U|+c_vT|\nu_N|$라는 더 거친 분리 상계도 가능하지만, (CP.6)은 보존에 따른 소거를 유지한다.

descriptor에 고정 양의 척도 $a_T$ (K), $a_n$ ($\mathrm{m^{-3}}$), $a_{\chi_i}$를 정해 $\|z\|_a=\max_i|z_i|/a_i$로 둔다. 이전 FP.23의 계산 가능한 extent bound를 재사용한다.

$$
|\xi_r(z)-\xi_r(w)|\le M_r\|z-w\|_a,\qquad
M_r=\frac{hL_r}{m_r}+\frac{h^2F_rD_r}{m_r^2}.
\tag{CP.7}
$$

$F_r,L_r,D_r,m_r$는 같은 고정 donor proposal 및 양의 coefficient domain에서 계산한다. 그러면

$$
G_T=\frac1m\sum_r\sup_{T\in I}|\nu_{U,r}(T)-c_vT\nu_{N,r}(T)|M_r
\tag{CP.8}
$$

가 $\mathcal T$의 Lipschitz 상계다. 계수가 Lipschitz이기만 한 경우에는 $T_w=\mathcal T(w)$를 고정하여 $|F(T_w;z)-F(T_w;w)|$를 (CP.2)와 (CP.7)로 바로 제한한다. 이어 $F_T\ge m$에 의한 $m|\mathcal T(z)-T_w|\le |F(T_w;z)|$를 적용하면 같은 (CP.8)이 나오므로 계수의 고전적 미분가능성을 더 요구하지 않는다. $m>0$은 이 상계에서 실제로 사용되며 작은 $m$이 온도 오차와 feedback을 증폭한다.

### 5.3 전체 descriptor map의 수축과 계산된 오차

EOS 뒤의 descriptor map을

$$
\mathcal H(z)=\left(\mathcal T(z),\frac{N(\mathcal T(z);z)-N_{\rm nuc}}V,
\boldsymbol\chi_{\rm ion}(x_h(z))\right)
\tag{CP.9}
$$

로 둔다. $\rho_c\le\rho_{\max}$, $\kappa=\chi k_B$일 때

$$
L_N^{(0)}=\sum_r\sup_I|\nu_{N,r}|M_r,\qquad
G_n=\frac{L_N^{(0)}+\kappa\rho_{\max}G_T}{V},
\tag{CP.10}
$$

$$
G_{\chi_i}=\frac1{N_{{\rm species}(i)}}\sum_r|s_{{\rm ion}(i),r}|M_r.
\tag{CP.11}
$$

0인 species는 해당 fraction과 함께 생략한다. 허용 descriptor box가 닫힌 self-map이고 root bracket 및 (CP.5)가 그 box 전체에서 유지되며

$$
\boxed{q=\max\left(\frac{G_T}{a_T},\frac{G_n}{a_n},
\max_i\frac{G_{\chi_i}}{a_{\chi_i}}\right)<1}
\tag{CP.12}
$$

이면 유일한 자기일관 descriptor endpoint가 존재하고 반복이 수렴한다. 이 self-map 전제는 rate domain, 원시 inventory의 비음성, $N_B>0$, root bracket 및 fraction bounds로 구성한다. 원래 FP2의 cutoff 고정 온도 bound만으로 새 bracket을 자동 채택하지 않는다.

**증명.** 고정 $T$에서 (CP.2)의 차를 취하면 $L_N^{(0)}$가 나온다. 이동 상한의 차는 $|\delta N|\le\kappa\rho_{\max}|\delta T|$이므로 (CP.10)을 얻는다. 원자핵 보존으로 species denominator가 고정되어 (CP.11)이 따른다. (CP.8), (CP.10), (CP.11)을 weighted maximum norm에 넣으면 (CP.12)다. 닫힌 self-map은 완비이며, 반복 거리의 기하급수 감소가 존재와 유일성을 준다. 각 raw 사건 step과 재분류가 같은 수·에너지 장부를 보존하므로 모든 반복에서 장부가 유지된다. $\square$

inner EOS에서 계산된 $\widehat T$의 잔차를 $r_F=|F(\widehat T;z)|$라 하면

$$
|\widehat T-\mathcal T(z)|\le r_F/m.
\tag{CP.13}
$$

이에 따른 descriptor 오차는

$$
\epsilon_{\rm inner}
\le \max\!\left(\frac1{a_T},\frac{\kappa\rho_{\max}}{Va_n}\right)\frac{r_F}{m}.
\tag{CP.14}
$$

따라서 실제 approximate map $\widehat{\mathcal H}$에 대해

$$
\boxed{\|z-z^\star\|_a\le
\frac{\|z-\widehat{\mathcal H}(z)\|_a+\epsilon_{\rm inner}}{1-q}.}
\tag{CP.15}
$$

온도 성분의 오차는 우변에 $a_T$를 곱하면 된다. 이산 반응 step의 물리 시간 오차는 이전 FP5–FP7의 endpoint defect 및 시간 정칙성 계약을 별도로 더한다.

### 5.4 실제 9600 원자 격자의 branch 적용

원자 measure의 cutoff 이동은 계단형이다. 일정 prefix $k$가 유지되는 열린 branch에서는 $\partial_TN=\partial_TU=0$, $C_{\rm eff}=c_vN>0$, $\rho_{\max}$에 의한 경계 Lipschitz 항은 0이다. (CP.3), (CP.6)–(CP.15)는 그 branch의 자기일관 threshold 부등식이 유지되는 domain에 적용한다.

threshold를 가로지르는 finite remap에는 THERMAL_CUTOFF_FEEDBACK_KO.md의 prefix continuation/branch 열거를 쓴다. $\chi\ge3/2$에서 그 알고리즘은 양의 fixed inventory를 유한하게 분류한다. 원자 경계의 유한 jump에는 위 매끄러운 contraction 전제를 자동 확장하지 않는다. 이는 계산 경로를 분기하는 조건이며 원자 inventory 자체를 버릴 이유가 아니다.

## 6. 실제 실행과 다음 소비자에 주는 계약

실제 xAct의 새 residual 이름은 `CurrentSelectorProduct`, `CurrentPartitionCancellation`, `StressSelectorProduct`, `BoundaryKineticEnergyAfterRestMass`, `RestMassCurrentSubtraction`, `TemperatureCutoffCurrent`다. 여섯 결과가 모두 정확히 0이었다. 실행 원문과 공식 package SHA256은 `results/WOLFRAM_XACT_RAW.json`, 실행 코드는 `checks/wolfram_xact_cutoff_checks.wl`에 있다.

실제 소비자는 (i) fixed raw spectrum 및 ghost inventory, (ii) 초기 active donor mask, (iii) thermal bath density 정의, (iv) atom branch 또는 검증된 연속 재구성, (v) root bracket과 Ceff 하한, (vi) extent rate/derivative bounds, (vii) inner/outer residual budget을 전달한다. 이 입력들이 주어지면 사건별 보존, cutoff 재분류, 온도 feedback의 계산식을 그대로 사용할 수 있다.
