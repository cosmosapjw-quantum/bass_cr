# 공변 에너지·입자수 투영에서 Bianchi I 기하 substep까지

단위: CR-THEORY-FEEDBACK-20261013. 이 문서는 앞선 TH1–TH7의 모멘트 회계와
이번 공통 사건 extent를 주어진 Bianchi I 배경의 실제 시간 step으로 연결한다.
아래 항등식과 유한 map의 근거 상태는 **직접 유도**다.
공변 tensor identity의 xAct 실행과 판정은 root가 작성하는 검산 기록에 따로 결속한다.

## 1. 가정, 시간, tensor의 차원

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

## 2. 에너지 투영을 직접 전개하기

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

## 3. 공행 입자수 current와 부피

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

## 4. Diagonal Bianchi I의 실제 tetrad와 보존 운동량

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

## 5. 상대론적 active energy와 pressure work

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

## 6. Thermal 이상유체의 정확한 기하 subflow

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

## 7. Signed 기하학적 일 장부의 endpoint 구성

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

## 8. 주어진 cutoff의 endpoint 편입

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

## 9. 닫힌 collision–geometry 한 step과 정확도

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

## 10. 다음 collision에 전달할 정확한 상태

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

