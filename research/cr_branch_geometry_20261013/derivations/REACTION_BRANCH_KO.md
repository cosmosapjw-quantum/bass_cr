# 반응으로 원자 가중치가 바뀌는 유한 cutoff branch 구성

## 결과와 범위

고정된 유한 에너지 support에서 반응이 원자 가중치, 기저 전자 수, 기저 열에너지와 이온 조성을 동시에 바꾸어도, 각 raw state의 cutoff branch를 **이전 branch에서 시작하는 유한 scan**으로 선택할 수 있다. 아래 정리는 $\chi\ge3/2$, 양의 기저 열용량과 비음수 raw 원자 가중치 아래 성립한다. 한 raw state에서 최대 원자 수만큼 이동하며, 선택한 열/비열 장부의 수와 에너지 합은 변하지 않는다. 반응 경로 전체의 유일한 EOS 해를 가정하지 않는다.

실제 PHYS02C HI kernel의 한 sharing contribution을 사용하여, 반응이 새로 만드는 첫 energy-grid 원자의 가중치가 증가하다가 cutoff에 편입되는 예제를 완성했다. 같은 반응 extent에서 두 consistent branch도 실제로 존재한다. 따라서 inherited branch는 반복 알고리즘의 편의값이 아니라 이 유한 표현의 **명시적인 선택 입력**이다.

이 절의 예제는 구성한 초기 재고와 하나의 source-pinned quadrature contribution에 대한 결과다. 선택한 contribution의 원래 확률은 rate coefficient 안에 유지하며, 선택 후 확률을 1로 재정규화하지 않는다. 시간 $h$는 accepted capacity map의 step parameter이며, nonlinear kinetic ODE의 정확한 경과 시간이나 cosmological history 정확도로 해석하지 않는다.

## 1. 변화하는 공통 raw inventory

서로 다른 고정 에너지 $0<w_1<\cdots<w_M$, raw 원자 가중치 $a_j(s)\ge0$, 기저 입자 수 $N_B(s)>0$, 기저 열에너지 $U_B(s)>0$를 둔다. 에너지는 J, 수는 같은 물리 cell의 count이며 $s$는 반응 extent이다. $k_B$는 SI 상수,

$$c_v=\frac32 k_B,\qquad \alpha=\chi k_B,\qquad E_c(T)=\alpha T.\tag{RB.1}$$

기저 수에는 모든 열적 nuclei와 unresolved thermal electrons가 들어간다. retained raw 원자는 소유가 thermal인지 active인지와 무관하게 $a_j$에 한 번 저장하고, $N_B,U_B$에서 그 수와 에너지를 다시 빼고 더하지 않는다. 원 source의 0.1 eV absorber/ghost에 포함된 전자는 이 예제에서 기저에 남는다. 모든 채택 cutoff가 그 absorber보다 높다는 조건을 아래에서 검증한다.

앞에서부터 $k$개를 thermal로 분류하면

$$N_k=N_B+\sum_{j\le k}a_j,\quad U_k=U_B+\sum_{j\le k}w_ja_j,\quad T_k=\frac{U_k}{c_vN_k}.\tag{RB.2}$$

$w_0=0,w_{M+1}=\infty$로 두었을 때 branch 일관성은

$$w_k\le\alpha T_k<w_{k+1}.\tag{RB.3}$$

등호는 thermal 소유다. Support에 가중치 0인 항을 유지해도 수/에너지는 변하지 않는다. 같은 에너지의 항은 먼저 하나로 합친다. 반응이 새로운 에너지를 만들면 현재 단계의 모든 사건 열이 만드는 support의 합집합을 먼저 고정한다. 에너지 자체의 geometry 이동은 별도 geometry map에서 처리한 후 이 단계의 support로 고정한다.

고정 $k$에서 $C^1$인 raw path의 미분은

$$\frac{dT_k}{ds}=\frac{U'_B+\sum_{j\le k}w_ja'_j-c_vT_k(N'_B+\sum_{j\le k}a'_j)}{c_vN_k}.\tag{RB.4}$$

따라서 기존의 $U_B$만 바뀌는 공식에 비해, 반응으로 변하는 **원자 가중치와 기저 수**가 모두 들어간다. 이 식은 cutoff를 미리 smooth하게 만든 유도가 아니며, 고정 prefix 내부의 정확한 미분이다.

## 2. 한 raw state의 유한 scan 정리

입력 inherited index를 $k$라 한다. 현재 $T_k$가 lower condition을 위반하면 가장 높은 thermal 원자를 제거한다. 그렇지 않고 upper condition을 위반하면 가장 낮은 active 원자를 추가한다. 일관성을 만족하면 종료한다.

### 추가 단계

다음 원자 $(w,a)$가 $w\le\alpha T_k$를 만족하면

$$\alpha T_{k+1}=\frac{N_k\alpha T_k+(\alpha/c_v)aw}{N_k+a}\ge w,\qquad\frac\alpha{c_v}=\frac{2\chi}3\ge1.\tag{RB.5}$$

이미 들어 있던 에너지는 모두 $w$ 이하이므로 lower consistency가 유지된다. 추가 후 온도가 감소하는 경우에도 이 부등식은 성립한다. 다음 upper violation에 대해서만 같은 단계를 반복하면 유한 $M$회 이내에 종료한다. 모든 원자를 넣었으면 upper bound는 $\infty$다.

### 제거 단계

가장 높은 thermal 원자가 $w>\alpha T_k$를 만족하면 $w>c_vT_k$이므로

$$T_{k-1}-T_k=\frac{a(c_vT_k-w)}{c_v(N_k-a)}\le0.\tag{RB.6}$$

분모는 최소 $N_B>0$이다. 제거한 원자는 새 cutoff 위에 있고, 앞서 제거한 더 높은 원자도 모두 위에 남는다. Lower violation이 없어질 때까지 제거하면 유한 $M$회 이내에 종료한다. $k=0$에서는 $T_0>0$이므로 lower condition을 만족한다.

따라서 한 raw state의 scan은 방향을 되돌릴 필요가 없고, 양의 EOS와 비음수 원자 수를 보존한다. 분류가 바뀔 때마다 동일한 실제 원자 에너지를 옮기므로

$$N_{\rm th}+N_{\rm act}=N_B+\sum_j a_j,\qquad U_{\rm th}+U_{\rm act}=U_B+\sum_jw_ja_j\tag{RB.7}$$

는 정확히 불변이다. 다른 chemical/excitation reservoir는 분류에 의해 변하지 않는다. 반응에 따른 물리 변화는 raw state를 만드는 공통 사건 열에서 이미 계산된다.

이는 한 endpoint의 유한 종료 정리다. 임의의 진동하는 $C^1$ parameter path 전체가 유한 횟수만 교차한다는 주장은 아니다. 전체 continuation을 유한 event sequence로 인증하려면 해당 경로의 교차 수, transversality와 event separation을 별도로 확인해야 한다.

## 3. 교차면과 온도 jump

Branch $k$의 상단에서

$$b_k(s)=\alpha U_k(s)-c_vw_{k+1}N_k(s)\tag{RB.8}$$

를 정의한다. $b_k<0$가 upper consistency다. $b_k(s_*)=0$, $b'_k(s_*)>0$, $a_{k+1}(s_*)>0$이면 increasing parameter 방향에서 inherited branch가 이 상단을 통과한다. 교차 시점의 추가는

$$\Delta T=\frac{a_{k+1}(w_{k+1}-c_vT_k)}{c_v(N_k+a_{k+1})}
=\frac{a_{k+1}w_{k+1}(1-c_v/\alpha)}{c_v(N_k+a_{k+1})}\ge0.\tag{RB.9}$$

$\chi>3/2$와 양의 crossing weight이면 엄밀히 양수다. 첫 추가가 그다음 경계도 넘으면 RB.5로 cascade를 끝까지 수행한다. $\chi=3/2$에서는 이 경계 jump가 0이다. 반대 방향 lower crossing의 제거 jump는 RB.6으로 정해진다. 양의 atom weight에서 나타나는 이 온도 jump는 **선택한 유한 sharp-cutoff EOS의 분류 변화**이며, 실제 물리 온도가 순간적으로 불연속이라는 증거가 아니다.

## 4. 실제 HI contribution에 결속한 구성

재사용한 kernel identity는 `inputs/prior/inputs/KERNEL_SOURCE_BINDING.json`에 고정되어 있다. Parent는 저장된 9600-grid의 Python index 4762,

$$W_p=30.00976971818039\ {\rm eV},\qquad B_H=13.6057\ {\rm eV}.\tag{RB.10}$$

원 sharing index 38의 느린 daughter는 $w_s=0.10194917280818$ eV, 빠른 daughter는 약 16.3021205453722 eV다. 원 quadrature 확률을 포함한 coefficient는 약 $\kappa=3.336923667758757\times10^{-18}$ m$^3$ s$^{-1}$다. 정확히 사용한 finite-binary rational은 결과 JSON에 보존한다.

느린 daughter가 source absorber $w_c=0.1$ eV와 첫 grid node $w_1=0.10309375$ eV 사이에 있으므로 원 projector는

$$g=\frac{w_1-w_s}{w_1-w_c},\qquad a=1-g=\frac{w_s-w_c}{w_1-w_c}\tag{RB.11}$$

의 ghost와 첫 node로 분해한다. 두 항의 합은 정확히 1이고 $g w_c+a w_1=w_s$다. $g$는 기저 thermal count, $g w_c$는 그 열에너지에 들어간다. 이 contribution에는 actual-subcut daughter가 없다. 빠른 daughter의 원 barycentric 두 node도 raw state에 유지한다.

별도 구성 초기 재고를 $V=1$ m$^3$, $N_{HI}=7$, $N_{HII}=2$, $N_{e,B}=1$, active parent count 1로 둔다. 따라서 nuclei는 9, $N_B^0=10$이며 ion charge 2와 자유전자 count 2가 일치한다. 초기 raw 첫 node와 빠른 daughter의 가중치는 0이다. $\chi=4$, $s_*=1/4$로 두고 SI로 변환한 $w_c,w_1$을 사용하여

$$U_B^0=\frac{c_v}{\alpha}w_1N_B^0-g\left(w_c-\frac{c_v}{\alpha}w_1\right)s_*\tag{RB.12}$$

로 초기 열에너지를 **구성한다**. 이 값은 양수이고 초기 cutoff는 $w_c$와 $w_1$ 사이에 있다.

동일한 ionization event 열 $S$를 하나의 extent $s$로 갱신하면

$$y(s)=y^0+sS,\quad N_B(s)=10+gs,\quad U_B(s)=U_B^0+gw_cs,\quad a_1(s)=as.\tag{RB.13}$$

또한 parent는 $1-s$, HI는 $7-s$, HII는 $2+s$, 빠른 daughter count는 $s$다. 기저/첫 node/빠른 daughter를 합친 자유전자 수는 반응 한 번당 1 증가한다. Chemical energy는 $B_Hs$만큼 증가한다. 실제 사건 열을 그대로 사용하므로 총 kinetic+chemical energy, H/He nuclei와 charge의 네 invariant residual은 모든 계산점에서 정확히 0이다.

Branch 0의 상단 함수는

$$b_0(s)=g(\alpha w_c-c_vw_1)(s-s_*),\qquad g(\alpha w_c-c_vw_1)>0.\tag{RB.14}$$

따라서 생성된 원자 가중치가 $a/4>0$인 상태에서 정확히 $s=1/4$에 첫 node가 편입된다. 그 뒤 첫 node까지 포함한 분자는 $U_B^0+w_ss$, 분모의 count는 $10+s$다.

## 5. 실제 조성 feedback 및 step parameter

초기 parent count 1과 초기 neutral count 7을 capacity denominator에 유지하고, trial neutral은 실제 endpoint $7-s$를 쓰면

$$f(s)=\kappa\frac{7-s}{V},\qquad \Psi_h(s)=\frac{hf(s)}{1+(8/7)hf(s)}.\tag{RB.15}$$

아래에서는 $V=1$ m$^3$의 count convention이다. 지정한 $0\le s<7/8$에 대해

$$h(s)=\frac{sV}{\kappa(7-s)[1-(8/7)s]}\tag{RB.16}$$

를 선택하면 $s=\Psi_{h(s)}(s)$가 정확히 성립한다. 이것은 frozen neutral의 단순 평가가 아니라 이 subfamily의 조성 feedback을 닫은 식이다. $h>0$에서 $\Psi_h$는 감소하고 $s$는 증가하므로 그 교점은 유일하다. $[0,1]$에 대한 $\Psi_h$의 image는 $[0,7/8)$ 안에 있어 존재한다. 이 유일성은 extent에 관한 것이며 cutoff branch의 유일성과 다르다.

$0\le s\le1/2$에 결속한 $h\le h(1/2)$에서는 $a_h=h\kappa/V\le7/39\simeq0.17949$이고

$$|\Psi'_h(s)|=\frac{a_h}{[1+(8/7)a_h(7-s)]^2}\le a_h<1\qquad(0\le s\le1).\tag{RB.17}$$

따라서 해당 domain에서 일반 fixed-point defect의 extent error는 $|\widehat s-\Psi_h(\widehat s)|/(1-a_h)$로 제한할 수 있다. 아래 예제는 RB.16의 정확 rational $h$를 써 defect 자체가 0이다.

## 6. 새 실행 결과와 판별

`python3 checks/check_reaction_branch.py`를 새로 실행했다. 0, 1/5, 1/4, 3/10, 1/2의 다섯 extent에서 같은 initial state와 source event로 raw state를 독립 구성했다. Fraction arithmetic은 **사용한 유한 source 숫자**에 대한 대수적 정확성을 인증한다. 원 cross section의 물리 정확도나 원 quadrature 오차를 0이라고 만들지 않는다.

| 새 판별량 | 실제 결과 |
|---|---:|
| 초기 온도 | 294.6991929990844 K |
| 교차 extent | 정확히 1/4 |
| 교차의 capacity step parameter | $1.5538818688854852\times10^{16}$ s |
| 교차 직전 branch 0 온도 | 299.0883225233885 K |
| 동일 raw state의 선택 branch 1 온도 | 306.7483350125956 K |
| 교차 뒤 cutoff | 0.10573410521646769 eV |
| 그 순간 편입되는 생성 원자 수 | 0.15750891379231236 |
| 네 invariant 및 extent 식 residual | 각 계산점에서 정확히 0 |

동일한 $s=1/5$에서 branch 0과 branch 1이 모두 RB.3을 만족한다. Branch 1의 lower consistency 시작점은

$$s_- =\frac{c_vw_1N_B^0-\alpha U_B^0}{\alpha w_s-c_vw_1}
\simeq0.08964254913065285 <\frac15<\frac14.\tag{RB.18}$$

이는 동일 extent의 root multiplicity를 직접 보여준다. 현재 선택은 inherited branch 0을 유지하다가 upper equality에서 branch 1로 넘어가는 continuation이다. 반대 경로를 물리적인 역이온화 계산으로 실행한 것은 아니다. 이 결과를 새 strong no-go로 채택하지 않으며, 실제로 완성한 유한 선택 규칙과 반응 예제로 보존한다.

## 7. 다음 의무

여러 실제 family의 rate가 cutoff branch별 $n_e,T$에 다시 의존하면 서로 다른 branch에서 extent 자체도 달라질 수 있다. 그 경우 branch별 coupled domain/error certificate와 crossing compatibility를 함께 구해야 한다. 이 루프의 별도 fixed-branch 구성은 그중 한 separated domain을 닫는다. 전체 multi-family crossing continuation의 전역 유일성, step refinement 및 유한 spectral representation을 연속 spectrum과 비교하는 오차는 다음 DAG 의무로 남긴다.

근거: `reaction_branch_continuation.py`, `checks/check_reaction_branch.py`, `results/REACTION_BRANCH_CHECKS.json`, accepted predecessor의 KA/TCF/CP 유도. 문헌과 현재 정리의 적용 범위 대응은 `LITERATURE_KO.md`에 모은다.
