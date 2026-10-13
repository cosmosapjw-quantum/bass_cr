# Prescribed Bianchi 수송 이후의 실제 kernel 재결속과 표현 오차

단위: `CR-THEORY-BRANCH-GEOMETRY-20261013`. 이 분과는 이동한 **현재 운동량과 kinetic energy**를 먼저 정한 다음, 실제 HI/HeI source kernel을 그 에너지에서 다시 평가한다. 이전 grid index의 sharing ratio를 이동 후에도 유지하지 않는다. 선택된 packet count, geometry work 장부, 재결속된 각 사건의 핵종·전하·에너지는 정확한 유한 산술로 보존된다. 물리 수송의 binary64 반올림, source quadrature, energy-grid 표현 및 angular closure는 별도 오차와 가정이다.

구현은 `geometry_kernel_rebind.py`, 새 실행은 `checks/check_geometry_rebind.py`, 원 결과는 `results/GEOMETRY_REBIND_CHECKS.json`, 사건 열은 `examples/GEOMETRY_REBIND_WITNESS.json`에 있다. 가정은 이 문서 §1, 소비자 오차 지도는 §5–6에 명시한다. 공변 에너지 법칙과 observer convention은 같은 단위의 `derivations/COVARIANT_GEOMETRY_KO.md`를 사용한다.

## 1. 원 근거와 상태의 범위

Frozen baseline은 `c450b00108dc05885a25d0d9c042cdcfe41bd659`이며 원 파일은 `inputs/prior/`에 보존했다. 새 loader는 `inputs/prior/kernel_event_adapter.py`를 **그 위치에서** 불러 원 adapter의 `ROOT` 해석을 유지한다. 해당 adapter는 `inputs/prior/inputs/KERNEL_SOURCE_BINDING.json`의 source SHA256을 다시 읽어 일치 여부를 검사하고, 저장된 9600-node `energy_eV` 배열을 사용한다. 이것은 이전 과학 suite의 재실행이 아니다.

직접 사용한 원 함수는 PHYS02B `causal_cascade.py`의 `Cascade._sharing`, PHYS02C `coherent_bed.py`의 HI/HeI `Ionization.total_m2`, `raw_bed_m2_eV`, 그리고 이전 exact count-coordinate projector다. `_sharing(ion, energy)`는 임의의 허용된 현재 energy를 받는다. 원 adapter의 `ion_event(index, species, quadrature_index)`는 grid index를 받으므로, 새 함수 `rebind_moved_ionization`을 따로 만들었다. 함수의 원본 파일·grid·binding hash는 실행 JSON에 남겼다. [원 재결속의 출발점: `inputs/prior/derivations/KERNEL_EVENT_ADAPTER_KO.md`, §3–§6, §13.]

다음 가정을 사용한다.

| ID | 가정 또는 입력 | 적용 범위 |
|---|---|---|
| GR-A1 | $m>0$, $c>0$, 양의 유한 $a_i^n,a_i^{n+1}$, 같은 comoving cell | prescribed homogeneous Bianchi I geometry substep |
| GR-A2 | 각 packet의 물리 직교기저 운동량 $\mathbf q_j$, 비음수 count $\omega_j$ | 에너지 spectrum만으로 방향을 추정하지 않음 |
| GR-A3 | source energy 범위 $0\le W\le900$ eV, 활성 cutoff는 원 $W_b=0.1$ eV 이상 | 상한 밖 외삽 및 미보존 lower trace 요청은 거절 |
| GR-A4 | 원 HI/HeI cold-target BED와 $v_{\rm nr}=\sqrt{2\epsilon_{\rm eV}W/m_e}$를 유지 | geometry의 massive law가 collision 모형을 상대론적으로 바꾸지 않음 |
| GR-A5 | geometry 종료 후의 energy·초기 donor mask·사건 열은 collision step 동안 고정 | trial temperature는 이 동일 reference의 rate·분류에만 연결 |
| GR-A6 | source로부터 실제 유한 sharing 배열과 양의 정규화가 반환됨 | 임계값 아래에서는 sharing 호출 없이 정확한 zero branch |
| GR-A7 | $\varphi$의 Lipschitz 또는 $C^2$ 상계가 관련 projection cell에 존재 | cutoff indicator, source threshold, 변화하는 quadrature topology에는 자동 적용하지 않음 |
| GR-A8 | EOS 오차를 요구하면 $N_{th},\widetilde N_{th}\ge N_{\min}>0$와 $T\le T_{\max}$ | 순수한 all-free count/energy 보존만으로 thermal EOS 오차 0을 추론하지 않음 |
| GR-A9 | 미분 상계의 frozen finite source constants는 정확한 실수로 해석 | 실제 transcendental FP64 평가 오차는 추가 입력 |
| GR-A10 | 반복 geometry에 필요한 daughter angle·미분해 bath closure는 별도 지정 | scalar SDCS에서 방향·응력·반동을 복원했다고 주장하지 않음 |

실제 state count는 밀도가 아니라 cell 안의 입자수다. 물리 밀도는 $n=N/V$이고, $V^{n+1}/V^n=\prod_i a_i^{n+1}/a_i^n$를 적용한다. 이 분과의 electron energy 장부는 kinetic energy이며, source의 ionization binding energy는 원 화학 장부 convention을 따른다. Active electron의 rest energy를 chemical energy에 새로 중복 추가하지 않는다.

## 2. Massive Bianchi I packet pushforward

Metric을

$$
 ds^2=-c^2dt^2+\sum_{i=1}^3 a_i(t)^2(dx^i)^2
\tag{GR.1}
$$

로 쓰고, $q_i$를 comoving observer의 **물리 직교기저** 운동량 성분으로 정한다. 공간 translation 대칭의 보존 운동량은 $a_iq_i$다. 따라서 collision이 없는 prescribed geometry 구간에는

$$
 q_i^{G}=r_iq_i^n,\qquad
 r_i=\frac{a_i^n}{a_i^{n+1}}>0,
\qquad
 E^G=\sqrt{m^2c^4+c^2\sum_i(q_i^G)^2},\qquad
 W^G=E^G-mc^2.
\tag{GR.2}
$$

이는 특정 시간 적분법이 아니라 두 끝점 scale factor를 사용하는 정확한 geodesic momentum map이다. $H_i=\dot a_i/a_i$라 하면

$$
 \dot W=-\sum_i H_i\frac{c^2q_i^2}{E}.
\tag{GR.3}
$$

모든 $H_i\ge0$이면 packet은 energy를 잃지만, anisotropic geometry에서 일부 축이 수축하면 work의 부호는 각 방향 운동량에 따라 달라진다. 같은 scalar $W$를 가진 $x$축 packet과 $z$축 packet은 $r_x\ne r_z$일 때 서로 다른 $W^G$를 얻는다. 따라서 scalar energy spectrum만으로 일반 Bianchi I pushforward를 닫을 수 없다. 이번 실제 witness는 방향을 입력한다. [공변 유도: `derivations/COVARIANT_GEOMETRY_KO.md`; 실제 새 symbolic 근거: `results/WOLFRAM_XACT_RAW.json`, `results/WOLFRAM_SCALAR_RAW.json`.]

### 안정적인 kinetic energy 계산

$R=mc^2$와 $p=c|\mathbf q|$를 같은 energy 단위로 두면

$$
 W=\frac{p^2}{\sqrt{R^2+p^2}+R}
   =\frac{p}{E}\frac{p}{1+R/E}.
\tag{GR.4}
$$

마지막 식은 $E-R$의 cancellation과 $E+R$의 불필요한 overflow를 피한다. 구현은 `math.hypot`로 norm을 만들고 (GR.4)를 계산한다. 양의 component가 0으로 underflow하거나 energy가 유한하게 표현되지 않으면 명시적으로 거절한다. 0 momentum 자체는 허용되며 정확히 $W=0$이다. 음수를 clip해 보정하지 않는다.

`momentum_from_kinetic_eV`는 witness 초기화에 $c|\mathbf q|=\sqrt W\sqrt{W+2mc^2}$와 지정한 unit direction을 사용한다. 이 역변환은 FP64 계산이므로, 원 saved $W_j$와 다시 평가한 $W(\mathbf q_j)$의 차이를 별도 기록한다. $a_i^{n+1}=a_i^n$이면 입력된 $\mathbf q_j$와 그로부터 계산하는 $W(\mathbf q_j)$에 대한 geometry identity가 성립한다. saved-grid energy에서 처음 생성한 momentum이 원 energy bytes를 정확하게 재현한다는 다른 주장은 하지 않는다.

### 원자 측도의 count와 geometry work

Comoving cell의 원자 측도를

$$
 \mu^n=\sum_j\omega_j\delta_{\mathbf q_j^n},\qquad
 \mu^G=\sum_j\omega_j\delta_{\mathbf q_j^G},\qquad\omega_j\ge0
\tag{GR.5}
$$

로 두면 total count는 그대로다. 물리 밀도만 $N/V$로 변한다. Geometry가 resolved packets에 한 work는

$$
 \Delta U_G=\sum_j\omega_j(W_j^G-W_j^n).
\tag{GR.6}
$$

별도 외부 work 장부 $\mathcal G$를

$$
 \mathcal G^G=\mathcal G^n-\Delta U_G
\tag{GR.7}
$$

로 갱신하면 $\sum_j\omega_jW_j+\mathcal G$가 보존된다. 이것은 geometry가 주어진 계의 work 회계다. Lost kinetic energy를 thermal heat에 넣는 collision 처방이 아니다. 미분해 bath의 팽창 work는 그 bath의 EOS·angular closure에 따라 별도로 합성한다. 미분해 bath에 $U_B\propto V^{-2/3}$를 적용하려면 비상대론적 등방 ideal-gas 가정을 따로 사용해야 한다.

이번 구현의 $\omega_j$는 Fraction으로 유지한다. 계산된 finite binary64 $W_j$를 Fraction으로 해석하면 (GR.6)–(GR.7)은 정확한 유한 산술의 항등식이다. 이 사실은 geodesic transport의 FP64 error를 0으로 만들지 않는다. Fixed $m,c$에서

$$
 \|\nabla_{\mathbf q}W\|=\frac{c^2|\mathbf q|}{E}\le c
\tag{GR.8}
$$

이므로, 전달받은 momentum error certificate $\|\widehat{\mathbf q}-\mathbf q\|\le\varepsilon_q$와 kinetic evaluator error $\varepsilon_{\rm eval}$가 있으면

$$
 |\widehat W-W|\le c\varepsilon_q+\varepsilon_{\rm eval}
\tag{GR.9}
$$

이다(SI J). Total work error는 각 초기·종료 energy error에 count를 곱해 더하면 된다. 이번 90-digit 비교는 관측된 반올림 진단이며 (GR.9)의 엄밀한 runtime 입력을 대신하지 않는다.

## 3. Lower trace와 cutoff의 고정 reference

현재 raw atoms를 $(W_j,\omega_j)$로 유지하고 $W_j\le W_c$를 thermal, $W_j>W_c$를 active로 정한다. Equality는 thermal이다. `classify_fixed_atoms`는 매번 같은 raw inventory에서 이 분할을 계산한다. Picard trial마다 이전 분할의 count·energy를 다시 누적하지 않는다.

각 raw atom이 실제로 보존되어 있으면 위·아래 cutoff 이동은 모두 분류할 수 있다. 이전 source의 $W\le W_b$ aggregate만 보존한 상태에서는 그 아래의 energy trace를 $U_B,N_{e,B}$만으로 복원할 수 없다. 따라서 inherited unresolved band를 입력한 경우 $W_c<W_b$는 거절한다. 이번 helper는 raw daughter energy 및 actual-subcut/ghost trace를 분리해 반환하지만, 이것은 과거에 사라진 원자들을 복원하는 동작이 아니다.

Aggregate 표현과 retained-atom 표현은 대체 표현이다. 새로 흡수된 trace $\{(w_\ell,n_\ell)\}$를 raw atom basis에 올릴 때에는

$$
 N_{e,B}^{\rm residual}=N_{e,B}^{\rm agg}-\sum_\ell n_\ell,\qquad
 U_B^{\rm residual}=U_B^{\rm agg}-\epsilon_{\rm eV}\sum_\ell w_\ell n_\ell
\tag{GR.10}
$$

와 같이 그 기여를 aggregate에서 한 번만 뺀다. 새 사건의 흡수 increment가 알려져 있으므로 이를 처음부터 residual base와 retained trace에 나누어 기록할 수 있다. Residual base의 비음수성은 별도로 유지한다. Code의 `absorbed_*` fields와 `actual_lower_atoms`/ghost lift를 상태 에너지 합에 동시에 넣지 않는다. 이 energy trace는 다음 thermal cutoff 분류에 충분하지만, 그 자체가 다음 anisotropic geometry에 필요한 daughter direction을 주지는 않는다.

## 4. 현재 parent에서 실제 HI/HeI 사건을 다시 구성

Geometry 종료 후 실제 finite $\widehat W$를 가진 parent stock을 `P:<label>`로 지정한다. 기존 $A:j$ stock은 저장된 $W_j$를 가진다. 두 energy row를 섞지 않는다. Active cutoff $W_c^G\ge W_b$를 정한 collision reference에서

$$
 \widehat W\le W_c^G\ \Longrightarrow\ \text{초기 donor 차단},
 \qquad
 W_c^G<\widehat W\le B_a\ \Longrightarrow\ \kappa_a=0.
\tag{GR.11}
$$

$\widehat W>B_a$이고 source support 안이면 원 `ion.total_m2(\widehat W)` 및 `original._sharing(ion, \widehat W)`를 실제로 호출한다. Sharing의 reflected knots와 Gauss nodes 역시 현재 available energy $\widehat W-B_a$에서 새로 만들어진다. 이전 grid node의 sharing arrays를 재사용하지 않는다. Source가 유한한 양의 normalization을 반환하지 않으면 사건을 만들어 진행하지 않는다.

원 float 확률 $p_\ell^{src}$를 exact binary rationals로 읽고

$$
 \widehat p_\ell=\frac{p_\ell^{src}}{\sum_kp_k^{src}},\qquad
 \widehat\kappa_a=v_{\rm nr}(\widehat W)\sigma_a(\widehat W),\qquad
 \widehat\kappa_{a\ell}=\widehat\kappa_a\widehat p_\ell
\tag{GR.12}
$$

로 둔다. $\sum_\ell\widehat p_\ell=1$은 정확하며, full family의 rate가 원 total rate에 결속된다. 실제 source total, normalization error diagnostic, sharing-node count를 결과에 남긴다. 정확한 정규화는 source quadrature의 물리 오차를 없애는 절차가 아니다.

원 slow daughter의 finite energy $w_\ell$에 대해 두 daughter를

$$
 w_{s,\ell}=w_\ell,\qquad
 w_{f,\ell}=\widehat W-B_a-w_\ell
\tag{GR.13}
$$

로 묶는다. $B_a$도 frozen source의 binary64 값으로 읽는다. Fast daughter를 exact complement로 만드는 것은 parent energy, binding 및 slow sample의 정확한 유한 장부를 정하는 선택이다. 원 float subtraction과의 energy 반올림 차이는 이 입력 해석에 포함되며 heat로 전환되지 않는다.

다음 절의 양의 projector $P$를 두 daughter에 적용하고, $a^+$를 HII 또는 HeII라 하면 사건 열은

$$
 s_{a\ell}=-e_{P}-e_a+e_{a^+}
   +P(w_{s,\ell})+P(w_{f,\ell}).
\tag{GR.14}
$$

여기서 $P$의 active 부분은 $A:j$ count이고, lower 부분은 $e_{th}$ count 및 $U_{th}$ energy다. State energy row는 $P$ stock에 $\epsilon_{\rm eV}\widehat W$, $A:j$에 $\epsilon_{\rm eV}W_j$, HII·HeII에 각각 원 binding, $U_{th}$에 1을 배정한다. 그러면 각 사건에서

$$
 \Delta N_H=\Delta N_{He}=0,\qquad
 \Delta Q=0,\qquad
 \Delta U_{\rm kinetic}+\Delta U_{\rm binding}=0.
\tag{GR.15}
$$

증명은 두 daughter의 count가 2이고 parent가 1 감소하여 자유전자가 1 증가하며, ion charge가 1 증가한다는 점과 (GR.13)의 energy 합이다. 모든 출력 계수는 비음수이고 negative donors는 실제 parent와 해당 neutral뿐이다. 따라서 이전 공통 사건 extent/capacity construction에 그대로 넣을 수 있다. 동일 parent의 H/He family는 같은 parent capacity를 공유해야 한다. Geometry 장부는 collision 동안 상수다. [원 finite-step 증명: `inputs/prior/inputs/prior/derivations/EVENT_STEP_DERIVATION_KO.md`, `FEEDBACK_THEOREMS_KO.md`.]

## 5. 양의 energy-grid projection과 weak-error 정리

원 saved grid와 source cutoff $W_b$를 사용한다. $x\le W_b$인 원자는 energy $x$ 그대로 retained lower atom에 둔다. $x>W_b$이고 $[\ell,u]$가 현재 bracketing cell이면

$$
 \beta=\frac{x-\ell}{u-\ell},\qquad
 P\delta_x=(1-\beta)\delta_\ell+\beta\delta_u.
\tag{GR.16}
$$

첫 active node 아래의 $\ell=W_b$ 항은 원 source의 cutoff ghost다. Exact grid node에서는 그 node 하나를 유지한다. $x>W_{\max}$는 외삽하지 않는다. $P$는 양의 선형 map이고

$$
 \langle1,P\mu\rangle=\langle1,\mu\rangle,\qquad
 \langle W,P\mu\rangle=\langle W,\mu\rangle.
\tag{GR.17}
$$

증명은 $(1-\beta)+\beta=1$과 $(1-\beta)\ell+\beta u=x$다. 여기서 lower/ghost contributions도 합에 포함한다. Source의 aggregate lower fields만으로 arbitrary nonlinear observable을 평가한 뒤 (GR.17)을 확대 적용하지 않는다. 이번 `ProjectionLift.represented_atoms`는 그 비교에 필요한 actual lower atoms와 ghost를 명시한다.

### Lipschitz 및 $C^2$의 계산 가능한 상계

$\varphi$가 cell에서 Lipschitz 상수 $L$을 가지면

$$
 \left|(1-\beta)\varphi(\ell)+\beta\varphi(u)-\varphi(x)\right|
 \le 2L\frac{(x-\ell)(u-x)}{u-\ell}
 \le\frac L2(u-\ell).
\tag{GR.18}
$$

첫 부등식은 각 endpoint와 $x$의 차이에 Lipschitz bound를 적용한 뒤 barycentric weight를 더해 얻는다. $|\varphi''|\le M_2$이면 선형 Taylor 항은 moment 보존으로 소거되고

$$
 \left|(1-\beta)\varphi(\ell)+\beta\varphi(u)-\varphi(x)\right|
 \le\frac{M_2}{2}(x-\ell)(u-x)
 \le\frac{M_2}{8}(u-\ell)^2.
\tag{GR.19}
$$

양의 원자 $\mu=\sum_j n_j\delta_{x_j}$에 대해

$$
 B_1=\sum_j2n_j\frac{(x_j-\ell_j)(u_j-x_j)}{u_j-\ell_j},\qquad
 B_2=\frac12\sum_jn_j(x_j-\ell_j)(u_j-x_j)
\tag{GR.20}
$$

를 계산하면 $|\langle\varphi,P\mu-\mu\rangle|\le LB_1$ 또는 $M_2B_2$다. Point cells와 그대로 유지한 lower atoms의 항은 0이다. 구현의 `lipschitz_geometry_eV`, `curvature_geometry_eV2`가 이 exact rational 값이다. $\varphi(W)=W^2$에는 error가 정확히 $2B_2$여서 비선형 witness가 상계를 포화한다. 실제 재결속한 HI/HeI 8개 사건에서 이를 확인했다.

기하 energy uncertainty $|\widehat W_j-W_j|\le\varepsilon_j$도 전달받았다면, scalar Lipschitz observable의 추가 항은 $L\sum_jn_j\varepsilon_j$다. 따라서 energy pushforward와 grid 표현을 합성한 bound는

$$
 |\delta\langle\varphi\rangle|
 \le LB_1+L\sum_jn_j\varepsilon_j
\tag{GR.21}
$$

이며, 첫 항을 $M_2B_2$로 바꿀 수 있는 곳에서는 바꾼다. Source quadrature, coefficient evaluation, consumer feedback amplification은 각각 자기 증명서로 더한다.

### Cutoff indicator와 thermal EOS에는 별도 식을 사용한다

$1_{W\le W_c}$는 경계에서 Lipschitz가 아니다. Projection cell이 cutoff를 가로지르면 total count와 energy가 정확해도 thermal count·energy가 바뀔 수 있다. 정확한 오차는

$$
 \delta N_{th}=\sum_jn_j\left[(1-\beta_j)1_{\ell_j\le W_c}
        +\beta_j1_{u_j\le W_c}-1_{x_j\le W_c}\right],
\tag{GR.22}
$$

$$
 \delta U_{th}=\epsilon_{\rm eV}\sum_jn_j\left[(1-\beta_j)\ell_j1_{\ell_j\le W_c}
        +\beta_ju_j1_{u_j\le W_c}-x_j1_{x_j\le W_c}\right].
\tag{GR.23}
$$

Crossing cells $\mathcal C=\{j:\ell_j\le W_c<u_j\}$ 밖의 항은 0이고,

$$
 |\delta N_{th}|\le\sum_{j\in\mathcal C}n_j,\qquad
 |\delta U_{th}|\le\epsilon_{\rm eV}\sum_{j\in\mathcal C}n_ju_j.
\tag{GR.24}
$$

두 daughter가 모두 같은 thermal branch 안에서 projection되면 thermal count·energy도 정확하다. 반대로 source $W_c=W_b$에서는 actual-subcut atom을 그대로 유지하므로 ghost가 전부 오차다: $\delta N_{th}=n_g$, $\delta U_{th}=\epsilon_{\rm eV}W_bn_g$. 새 결과에 $n_g$를 actual-subcut count와 분리해 보존했다.

$c_v=3k_B/2$, $T=U_{th}/(c_vN_{th})$이면

$$
 \widetilde T-T=
 \frac{\delta U_{th}-c_vT\delta N_{th}}{c_v\widetilde N_{th}},\qquad
 |\widetilde T-T|\le
 \frac{|\delta U_{th}|+c_vT_{\max}|\delta N_{th}|}{c_vN_{\min}}.
\tag{GR.25}
$$

이는 주어진 cutoff에서의 분류/표현 error map이다. $W_c=\chi k_BT$의 implicit feedback이나 threshold jump를 포함한 endpoint error는 현재 coupled/branch solver의 root·continuation 조건과 합성해야 한다. (GR.25)만으로 global implicit-root uniqueness를 주장하지 않는다.

### Momentum과 stress에 대한 정확성 범위

같은 방향에 projected energy nodes를 놓더라도 $|\mathbf q(W)|=\sqrt{W(W+2mc^2)}/c$는 affine하지 않다. 그러므로 (GR.17)은 일반적인 momentum·stress 보존을 뜻하지 않는다. 그 관측량의 energy 함수가 regular한 구간에는 (GR.18)–(GR.19)를 사용하고, energy 0 부근의 derivative 특이성이나 angular 재구성에는 별도 가정을 둔다. 이번 양의/음의 동일 packet 쌍은 대칭 때문에 net momentum 0을 유지하지만, 이를 임의의 distribution으로 일반화하지 않는다. 원 raw momenta를 유지하는 pushforward에는 이런 energy-grid projection을 먼저 적용할 필요가 없다.

## 6. 실제 HeI total coefficient의 rational derivative bound

실제 source의 HeI closed form을 사용하면 finite difference 없이 scalar rate coefficient의 계산 가능한 상계를 만들 수 있다. 여기서는 $\kappa(W)=v_{\rm nr}(W)\sigma_{HeI}(W)$만 다룬다. 움직이는 daughter nodes·sharing probabilities 및 전체 branching operator의 $W$-미분 상계는 이 scalar 결과에 포함되지 않는다.

Source의 frozen parameters에 대해

$$
 t=\frac WB>1,\quad a=1+\frac UB,\quad
 D(t)=\frac1N\sum_{k=2}^{6}\frac{c_k}{k}
       \left[1-\left(\frac2{t+1}\right)^k\right],
\tag{GR.26}
$$

$$
 \begin{aligned}
 f(t)&=1-\frac1t-\frac{\log t}{t+1},
 &b(t)&=D(t)\log t+Kf(t),\\
 g(t)&=\frac{\sqrt t}{t+a},
 &\kappa(W)&=C g(t)b(t),\\
 C&=S\sqrt{\frac{2B\epsilon_{\rm eV}}{m_e}}.
 \end{aligned}
\tag{GR.27}
$$

여기서 $(c_2,\ldots,c_6)=(0,8.24012,-10.4769,3.96496,-0.0445976)$이고, 구현에서는 decimal 인쇄값이 아니라 실제 source float의 정확한 rational 값을 읽는다. $B=24.587$ eV와 $U=39.51$ eV, $N=2$, $K=2-N_i/N$도 원 source 값이다. [실제 함수: `inputs/prior/inputs/kernel_sources/research/cr_phys02c_20261011/src/coherent_bed.py`, `Ionization.D`, `Ionization.total_m2`.]

$1<t_0\le t\le t_1$, $y_i=2/(t_i+1)$, $\Lambda=t_1-1\ge\log t$라 두자. 다음 값은 각각 $|D|,|D'|,|D''|$의 상계다.

$$
 d_0=\frac1N\sum_k\frac{|c_k|}{k}(1-y_1^k),\quad
 d_1=\frac{\sum_k|c_k|y_0^k}{N(t_0+1)},\quad
 d_2=\frac{\sum_k(k+1)|c_k|y_0^k}{N(t_0+1)^2}.
\tag{GR.28}
$$

이는 $D'=N^{-1}\sum_kc_ky^k/(t+1)$, $D''=-N^{-1}\sum_k(k+1)c_ky^k/(t+1)^2$에서 직접 나온다. 다음 양의 rational bounds를 쓴다.

$$
 f_0=1-t_1^{-1}+\frac{\Lambda}{t_0+1},\qquad
 f_1=\frac1{t_0^2(t_0+1)}+\frac{\Lambda}{(t_0+1)^2},
\tag{GR.29}
$$

$$
 f_2=\frac{3t_1+2}{t_0^3(t_0+1)^2}
       +\frac1{t_0(t_0+1)^2}+\frac{2\Lambda}{(t_0+1)^3}.
\tag{GR.30}
$$

실제로 $f'=1/[t^2(t+1)]+\log t/(t+1)^2$이며 그 미분에 절댓값을 취하면 (GR.30)을 얻는다. 따라서

$$
 b_0=d_0\Lambda+|K|f_0,\quad
 b_1=d_1\Lambda+d_0/t_0+|K|f_1,\quad
 b_2=d_2\Lambda+2d_1/t_0+d_0/t_0^2+|K|f_2
\tag{GR.31}
$$

가 $|b|,|b'|,|b''|$를 각각 제한한다. $s\ge\sqrt{t_1}$인 rational upper bound를 정하고 $t_0>1$을 사용하면

$$
 g_0=\frac{s}{t_0+a},\quad
 g_1=\frac1{2(t_0+a)}+\frac{s}{(t_0+a)^2},\quad
 g_2=\frac1{4t_0(t_0+a)}+\frac1{(t_0+a)^2}
        +\frac{2s}{(t_0+a)^3}
\tag{GR.32}
$$

가 $|g|,|g'|,|g''|$의 상계다. 정확한 $g''$는
$-1/[4t^{3/2}(t+a)]-1/[\sqrt t(t+a)^2]+2\sqrt t/(t+a)^3$이며 (GR.32)는 그 분모에 $\sqrt t\ge1$을 적용한 보수적 상계다.

$C_+\ge C$인 rational upper bound를 만들면

$$
 L_\kappa=\frac{C_+}{B}(g_1b_0+g_0b_1),\qquad
 M_{2,\kappa}=\frac{C_+}{B^2}(g_2b_0+2g_1b_1+g_0b_2)
\tag{GR.33}
$$

가 필요한 상계다. 구현은 exact rational radicand에 $10^{40}$ scale을 곱한 정수 ceiling과 `isqrt`를 사용하여 square-root upper bound를 만든다. $\log t$는 $t_1-1$로 이미 위에서 제한했으므로 상계 생성에 floating logarithm, derivative sampling 또는 finite difference를 쓰지 않는다.

이 상계는 frozen finite coefficients가 정의하는 ideal real formula에 엄밀하다. `total_m2`의 실제 FP64 log·expm1·연산 roundoff까지 자동 포함하지 않는다. 관측된 binary64 coefficient와 ideal formula의 차이가 $\eta(w)$ 이하라는 별도 certificate를 받으면, 원자 하나에 대해 representation error에

$$
 (1-\beta)\eta(\ell)+\beta\eta(u)+\eta(x)
\tag{GR.34}
$$

를 추가한다. 아래 90-digit 비교는 이 error의 세 점 diagnostic만 제공한다. 임계값을 포함하거나 source support를 벗어나는 interval은 함수가 거절한다. HI의 quadrature-defined $D(t)$, source excitation table knots, 또는 changing sharing topology에 이 HeI 식을 그대로 사용하지 않는다.

## 7. 실제 source witness와 새 실행

새 focused 실행은 2026-10-12 23:55 UTC(10-13 KST)에 **한 번**, 0.321257080999203 s 동안 수행되었다. 3개 묶음은 geometry/trace, actual moved HI/HeI event rebind, weak representation bound다. 이전 scientific suite, generator 조립, ODE, NCP 실행은 모두 0이다. Source·검사 프로그램의 SHA256은 실행 JSON에 결속했다.

실제 saved node $j=4762$의 $W_j=30.00976971818039$ eV와 direction $(2,1,2)/3$ 및 그 반대 방향을 사용했다. 각 count는 $1/2$이다. 초기 $a=(1,1,1)$, 종료 $a^G=(2,1,2/3)$로 두면 finite ratio는 $(1/2,1,3/2)$이고,

$$
 W^G=36.678368111778816\ {\rm eV},\qquad
 \Delta U_G=6.66859839359843\ {\rm eV}.
\tag{GR.35}
$$

정확한 rational $\mathcal G$ increment는 그 음수이고 보존 residual은 0이다. Actual $W^G$는 saved grid node가 아니다. 33 eV cutoff에서는 두 raw packet이 thermal에서 active로 바뀌며 동일 reference 재분류가 반복해도 동일한 결과를 준다. 동일 scale factors에서는 state identity이고, 0.05 eV cutoff는 inherited missing trace 때문에 거절되었다. Isotropic $a^G=(2,2,2)$로 이동한 $W^G=7.5026076524362795$ eV에서는 HI/HeI ionization이 0이다. 강한 수축 $a^G=(0.1,0.1,0.1)$은 $2992.303936182018$ eV로 원 support를 벗어나 rebind를 거절한다.

Stable energy의 90-digit reference와의 절대 차이는 $7.5119\times10^{-15}$ eV였다. 별도의 arithmetic-only $10^{-20}$ eV 초기화에서 subtractive formula는 0, stable formula는 양의 energy를 반환했다. 이 작은 energy 사례는 cold-target source domain에 대한 물리 witness가 아니다.

| 실제 재결속 family | 새 sharing nodes | $\kappa$ ($\mathrm{m^3\,s^{-1}}$) | 직접 점검한 quadrature indices |
|---|---:|---:|---|
| HI | 17,564 | $2.143100169002381\times10^{-14}$ | 0, 32, 8782, 17563 |
| HeI | 13,888 | $5.0171422373973835\times10^{-15}$ | 0, 52, 6944, 13887 |

각 family 전체의 확률 합은 Fraction으로 정확히 1이다. 선택한 8개 사건은 actual subcut, source ghost, 내부 sharing, near-half daughter를 포함한다. 모든 사건에서 두 핵종·전하·total energy residual은 정확히 0이고, 원 projector와 active/base count·energy가 정확히 일치한다. Raw daughter의 count와 first energy moment도 정확하다. 각 사건의 quadratic weak error가 $2B_2$와 같고, kink를 가진 1-Lipschitz observable의 error가 $B_1$ 이하임을 확인했다. Parent $1/2$, target 1에서 extent $1/4$를 적용한 새 단일 사건 endpoint도 비음수다. 전체 nonlinear timestep 승격을 이 단일-event positivity witness에서 추론하지 않는다.

예를 들어 HI의 index 32는 $(0.10021480476800296,\ 22.972453307010813)$ eV daughter를 만들고, source cutoff ghost count는 $0.9305681557970258$이다. 이것은 해당 **조건부 사건 1회**의 ghost count이며 total physical family rate 또는 전체 전자 population의 fraction이 아니다. 그 사건 probability와 coefficient를 결과에 함께 기록했다.

현재 parent의 HeI rate projection cell은

$$
 [\ell,u]=[36.66802549168974,\ 36.69381567205715]\ {\rm eV}
\tag{GR.36}
$$

로 threshold에서 떨어져 있다. (GR.33)은 $L_\kappa\simeq2.6047684754\times10^{-15}$ $\mathrm{m^3s^{-1}eV^{-1}}$, $M_{2,\kappa}\simeq3.0393801968\times10^{-16}$ $\mathrm{m^3s^{-1}eV^{-2}}$를 준다. 실제 source의 세 energy 평가를 비교하면

$$
 |\delta\kappa|_{\rm binary64}
 =2.5759954266\times10^{-22}\ {\rm m^3s^{-1}},\qquad
 M_{2,\kappa}B_2=2.4279822341\times10^{-20}\ {\rm m^3s^{-1}}.
\tag{GR.37}
$$

Ideal formula의 90-digit weak error는 $-2.5759954255\times10^{-22}$ $\mathrm{m^3s^{-1}}$였고, 세 점에서 관측된 최대 coefficient roundoff는 $9.3164\times10^{-31}$ $\mathrm{m^3s^{-1}}$였다. 이 세 점 결과는 runtime domain 전체의 floating error 상계가 아니다. Exact mathematical (GR.33), 실제 source diagnostic, 그리고 최종 consumer의 total error budget을 구별한다.

## 8. 이번에 닫은 연결과 다음 소비자의 입력

실제 kernel 연결은 다음 순서로 닫힌다: 주어진 $a_i$와 raw momenta로 geometry map을 적용하고, count와 외부 work를 기록하며, 허용된 energy/cutoff domain을 판정한 다음, 그 종료 energy에서 HI/HeI total과 paired daughter family를 다시 만든다. 새 parent key의 energy row와 공통 extent를 고정하여 collision을 진행하고, 같은 raw inventory에서 thermal cutoff를 분류한다. 각 finite submap에서 전자가 어디에 있는지와 energy가 어느 장부에 있는지가 정해진다.

Smooth time interval에서 $a_i(t+h)/a_i(t)=1+H_ih+O(h^2)$, 선택된 collision map이 자기 ODE에 일차 일관적이며 source/cutoff branch가 필요한 regularity를 가지면 geometry–collision Lie composition은 합성 vector field에 일차 일관적이다. Threshold crossing, changing quadrature topology, implicit thermal branch jump의 regularity를 이 조건 없이 추가하지 않는다. Geometry substep의 $h=0$ identity와 collision의 $h=0$ identity는 같은 canonical raw state에 결속해야 한다. Trial마다 geometry나 trace transfer를 누적하면 이 construction과 다른 map이 된다.

소비자는 다음을 별도로 전달한다: (i) raw/thermal residual base와 daughter angular closure, (ii) 현재 physical volume과 cold-target admissibility, (iii) source quadrature·numeric evaluation budget, (iv) 사용 observable의 regularity 또는 exact crossing error (GR.22)–(GR.25), (v) coupled fixed-point/root amplification 및 선택 scenario의 tolerance. 전역 REI 채택, 기존 capture/all-bound/G02/production/b-grid gates, full production kernel qualification, NCP 실행 또는 선택 source·소비자 예산은 이번 geometry 구성으로 승격하지 않는다.
