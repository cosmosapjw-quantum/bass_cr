# 이번 루프의 결과

실제 저장된 9600개 에너지 격자와 HI·HeI collision kernel을, 입자수·전하·에너지를 함께 보존하는 양의 사건 분해에 연결했다. 이어 $E_c(T)=\chi k_BT$로 움직이는 cutoff를 같은 원시 입자 inventory에서 재분류하는 유한 map을 구성하고, 온도 방정식의 해·오차·feedback 조건을 도출했다. 원자 격자에는 유한 branch 알고리즘을, 연속 spectrum에는 검증 가능한 root certificate를 제공한다.

이번 연구 단위는 **CR-THEORY-KERNEL-CUTOFF-20261013**이다. 직전 승인된 FB1–FB7과 그 DAG에서 열려 있던 실제 kernel 사건 adapter 및 온도 의존 cutoff 두 노드를 수행했다. 이전의 공통 사건량, 양의 재고 제한식, thermal/all-free 변환과 이동 경계 장부는 근거 identity를 유지하여 재사용했다. 이번에 새로 계산한 대상과 실행 결과는 아래에 한 번에 정리했다.

## 핵심 결론

1. **실제 daughter 분배를 보존하는 사건 step.** 같은 parent와 target species에 속한 모든 sharing 사건의 donor가 같음을 실제 격자 간격과 문턱 에너지로 증명했다. 이에 따라 양수성을 보장하는 capacity 제한은 같은 family의 전체 사건량을 조정하며 원래 daughter sharing probability를 유지한다.
2. **온도에 따라 움직이는 cutoff의 유한 해.** 전체 count와 kinetic energy를 고정하고 실제 이동 band의 0차·1차 모멘트를 다시 평가한다. 이 map에서 EOS를 풀면 연속 분포의 유효 열용량, 양의 유일근 조건, 잔차로부터의 온도 오차 한계가 함께 나온다.
3. **저장된 원자 격자에 맞는 구성.** Node별 입자수를 그대로 유지하면서 열적 prefix의 가능한 해를 유한하게 열거한다. $\chi\ge3/2$에서는 양의 base에서 해를 유한 단계로 구성할 수 있고, 고정 spectrum에 대한 가열·냉각 continuation은 기존 branch를 이어 간다.
4. **공변 경계식과 coupled feedback.** 수 전류와 총 4-momentum source의 rest-mass subtraction을 연결했다. 사건의 에너지·열적 입자수 증분으로 전체 온도·밀도·조성 map의 수축상계와 inner/outer 오차식을 얻었다.

독립 판정: **<!-- REVIEW_STATUS -->**. 주장 KC1–KC7의 정확한 범위와 근거는 `CLAIMS.json`, 전제는 `CONTRACT.json`, 독립 검토의 동결 대상은 `review/CANDIDATE_MANIFEST.json`에 있다. 이 보고서의 “완료”는 그 전제 아래의 이론 구성과 reference 구현에 관한 판정이다.

## 현재 가정과 근거

| 대상 | 이번에 고정한 내용 | 근거와 역할 |
|---|---|---|
| 기하와 단위 | $(-,+,+,+)$; $c,k_B,\hbar$ 유지; 상태 에너지 J, 원자 입력 eV; proper time | CV.1–10, KA.1–4 |
| 실제 입력 | PHYS02C full BED HI·HeI, PHYS02B projection·stopping·CCC; 저장된 9600 nodes | 기준 commit의 11개 원본 파일과 실제 NPZ bytes |
| 사건과 재고 | 한 사건의 모든 증분에 같은 extent; 초기 active mask와 초기 donor support 고정 | KA.12–29 및 기존 FP.7–24 |
| Coulomb bath | $n_e=N_{e,\mathrm{th}}/V$; 양의 Coulomb log와 cold-target 범위 | KA.19–24 |
| 열적 EOS | $U=c_vNT$, $c_v=3k_B/2$; $N$은 핵종과 thermal electrons의 합 | TCF.2–13 |
| 유한 분할 | 하나의 root solve에서 전체 count·energy·spectrum을 고정; lower trace 보존 | TCF.2–10 |
| 연속 root | root bracket과 $C_{\rm eff}\ge m>0$ | TCF.13–24 |
| 원자 root | equality는 thermal 소유; finite branch 열거; 존재 scan에는 $\chi\ge3/2$ | TCF.36–46 |
| 결합 feedback | descriptor self-map, uniform bracket, $q<1$; 연속 표현의 기저는 trial과 독립 | CP.1–15 |

원본 격자의 첫 node는 0.10309375000000001 eV, 중간 연결 node는 10 eV, 마지막 node는 900 eV다. Source lower absorber는 0.1 eV다. 실제 NPZ와 그 안의 energy array를 읽었으며, grid raw SHA256은 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`이다. 기존 spectrum을 다시 계산하거나 전체 generator를 새로 만들지 않았다.

# 실제 kernel을 보존 사건으로 연결한 결과

## 두 딸을 하나의 사건으로 묶는 이유

Parent energy $E_j$, ionization threshold $B_a$, 실제 sharing point $w_\ell$에 대해 두 daughter energy는

$$
w_1=w_\ell,\qquad w_2=E_j-B_a-w_\ell
$$

이다. 각 daughter를 양의 barycentric weights로 grid와 lower absorber에 투영한다. 한 daughter의 active weights $b_i$, 흡수 count $n_B$, 실제 흡수 energy $u_B$는

$$
\sum_i b_i+n_B=1,\qquad \sum_iE_i b_i+u_B=w
$$

를 만족한다. 두 daughter를 더하고 parent 하나를 빼면 자유전자 수는 1 증가한다. 같은 사건에서 neutral 하나가 ion 하나로 바뀌므로 전하가 보존되고, threshold를 chemical energy로 넣으면 총 에너지도 보존된다. 실제 subcut absorption과 첫 grid cell의 ghost fraction은 별도 출력으로 남긴다.

원래 에너지 좌표의 discrete generator와 이 count-coordinate 사건 합의 대응도 직접 확인했다. `heat`, `cutoff_energy`, `binding`, excitation energy 및 겹치는 observer를 각각 물리 장부와 대응시켜 같은 에너지를 두 번 더하지 않도록 했다. 전체 과정은 KA.5–18에 있다.

## 같은 family의 daughter 분포를 유지하는 강화 결과

실제 저장 격자의 최대 간격은 0.6325633326908928 eV이고, 최소 ion binding 13.6057 eV와 최소 adopted excitation cost 10.20435 eV보다 작다. 따라서 ion daughter나 excitation daughter의 투영은 parent node로 되돌아오지 않는다.

같은 $(j,a)$에 속한 ionization 사건은 모두 동일한 donor $\{A_j,X_a\}$를 가지며 소비 계수도 1이다. 공유 재고로 만든 분모 $1+h d_{ja}$는 sharing index $\ell$에 독립이어서

$$
\boxed{\xi_{ja\ell}=p_{ja\ell}\,\Xi_{ja},\qquad
\Xi_{ja}=\frac{h\,m_j^nA_j^nv_j\sigma_a(E_j)X_a(z)/V}{1+h d_{ja}}.}
$$

이 성립한다. 같은 family 안에서 원래 $p_{ja\ell}$가 유지되는 결과다. 서로 다른 target species나 parent의 총 사건량은 각자의 경쟁하는 재고를 반영하여 달라질 수 있다. 이 일반성은 KA.29의 격자 간격 증명에 있고, 실제 세 sharing points의 exact ratio는 구현 연결을 확인한다.

## 실제 rate feedback의 위치

Fixed-energy atomic coefficient에는 직접적인 온도 인자가 없다. Trial neutral count가 atomic rate에 선형으로 들어가고, stopping은 thermal electron density를 통해 변한다. 기존 stopping prescription을 같은 에너지에서 이어 쓰면

$$
L_j(n)=L_j(n_0)-\frac12\log\frac n{n_0},\qquad b_j(n)=\alpha_jnL_j(n),
$$

$$
b_j'(n)=\alpha_j\left(L_j(n)-\frac12\right),\qquad
b_j''(n)=-\frac{\alpha_j}{2n}.
$$

양의 밀도 구간 양끝에서 $|b_j'|$ 상계를 계산할 수 있다. Cutoff가 thermal ownership을 바꾸면 $N_{e,\rm th}$가 바뀌므로 이 식이 온도와 stopping의 간접 feedback을 연결한다. EOS에 넣는 총 thermal count에는 핵종도 포함되지만, screening 밀도에는 thermal electrons만 넣는다.

# 온도 의존 cutoff를 유한 단계로 닫은 결과

## 같은 전체 inventory에서 candidate를 계산한다

한 solve 동안 전체 count $\mathscr C$, kinetic energy $\mathscr E$, retained electron measure $\mu$를 고정한다. 아직 분해하지 않은 thermal base는

$$
N_B=\mathscr C-\int d\mu\ge N_{\rm nuc}>0,\qquad
U_B=\mathscr E-\int W\,d\mu\ge0
$$

를 만족한다. 경계 equality를 thermal 쪽에 배정하면

$$
\boxed{N(T)=\mathscr C-\mu((E_c(T),\infty)),\qquad
U(T)=\mathscr E-\int_{(E_c(T),\infty)}W\,d\mu.}
$$

이 계산은 모든 candidate에서 count와 kinetic energy를 정확히 보존한다. 낮은 에너지 전자를 이미 thermal로 합쳤더라도 그 원자 inventory를 retained measure에 남기면 cutoff를 낮출 때 회수할 수 있다. 이때 기존 thermal 총량에서 retained lower atoms를 먼저 빼서 $N_B,U_B$를 정의한다.

유한 이동의 에너지는 이동한 band의 1차 모멘트다. 따라서 일반적으로 $\Delta U\ne E_c(T)\Delta N$이다. 각 수치 반복은 같은 reference에서 새 candidate를 계산하며, 이전 반복에 다시 같은 이동량을 더하지 않는다.

## 유효 열용량과 온도 오차

연속 밀도 $d\mu=\rho(W)dW$에서

$$
F(T)=c_vTN(T)-U(T),\qquad E_c(T)=\chi k_BT
$$

를 미분하면

$$
\boxed{C_{\rm eff}=F_T=c_vN-\chi k_B(E_c-c_vT)\rho(E_c).}
$$

이 계수 자체는 기존 이동 경계 결과와 일치한다. 이번에는 유한 EOS map의 실제 미분으로 회복하고, root와 오차의 계산에 사용했다. $\chi>3/2$이면 경계의 편입 효과가 이 계수를 낮출 수 있다. 양의 $N$만으로 $C_{\rm eff}>0$를 대신할 수는 없다.

구간 $I=[T_-,T_+]$에서 $F(T_-)\le0\le F(T_+)$와 $C_{\rm eff}\ge m>0$를 확인하면 양의 유일근이 존재하며

$$
\boxed{|T-T^\star|\le\frac{|F(T)|}{m}}
$$

을 얻는다. 이번 finite box reference는 density knot 사이의 slope를 정확히 계산하여 $m$을 검증한다. 이분법의 bracket 오차와 이 잔차 bound 중 더 작은 값을 certificate로 반환한다. 물리 spectrum과 재구성 spectrum이 다르면 cutoff bracket의 tail count·energy 오차를 TCF.23–24로 추가한다.

## 정확한 가열·냉각 사례

$\tau=T/T_*$, $\epsilon=W/(k_BT_*)$로 정규화하고, $\chi=4$, $dN/d\epsilon=\tfrac14\mathbf1_{[3,6]}$를 택했다. 같은 전체 inventory에서 얻는 식은

$$
N(\tau)=1+\tau,\quad u(\tau)=1+\delta+2\tau^2,\quad
f(\tau)=\frac32\tau-\frac12\tau^2-1-\delta.
$$

$[3/4,5/4]$에서 $f'\ge1/4$이고, $-5/32\le\delta\le3/32$이면 root가 존재한다. Picard map도 이 구간을 보존하며 그 미분은 $233/243$ 이하이다.

| 외부 predictor energy $\delta$ | 정확한 $T/T_*$ | thermal $N$ | $U/(k_BT_*)$ | cutoff가 옮긴 $\Delta N$ | cutoff가 옮긴 $\Delta U/(k_BT_*)$ |
|---|---:|---:|---:|---:|---:|
| $2/25$ | $6/5$ | $11/5$ | $99/25$ | $1/5$ | $22/25$ |
| $-3/25$ | $4/5$ | $9/5$ | $54/25$ | $-1/5$ | $-18/25$ |
| $0$ | $1$ | $2$ | $3$ | $0$ | $0$ |

가열·냉각의 cutoff transfer가 대칭일 필요는 없다. 서로 다른 에너지 band를 옮기기 때문이다. 외부 predictor가 넣거나 뺀 에너지와 cutoff가 재분류한 에너지를 구별하면 각 행에서 전체 장부가 정확히 닫힌다.

![연속 cutoff의 정확한 EOS 근과 원자 branch의 유한 편입. 오른쪽 가로축은 한 endpoint 안의 분류 후보 순서이며 물리 시간 단계가 아니다.](../figures/cutoff_construction.pdf)

## 실제 격자의 원자 branch

$\mu=\sum_jn_j\delta_{w_j}$에는 미분 가능한 cutoff density를 가정하지 않고 prefix를 직접 사용한다. 첫 $k$개 node를 thermal로 둔 candidate는

$$
T_k=\frac{U_B+\sum_{j\le k}w_jn_j}{c_v(N_B+\sum_{j\le k}n_j)}
$$

이며 $w_k\le\chi k_BT_k<w_{k+1}$를 만족하면 consistent하다. $M+1$개 prefix를 검사하면 모든 해를 얻는다. $\chi\ge3/2$에서는 가장 낮은 에너지부터 조건에 맞는 원자를 편입하는 scan이 최대 $M$번에 끝남을 증명했다.

기존 branch에서 base energy만 변화시키면 가열은 위쪽 node의 편입, 냉각은 가장 높은 thermal node의 회수로 이어 간다. 양의 base를 유지하는 이 경로는 $h=0$에서 identity다. 새 원자를 편입한 직후 온도가 내려가더라도 그 원자가 여전히 cutoff 아래에 있다는 부등식이 유지되므로 scan은 성립한다.

Constructed example에서 $N_B=10,U_B=15$, 원자 에너지 $(5,9,30)$, 각 count 1, $\chi=4$를 사용했다. Base energy에 135를 더하면 $k:0\to1\to2\to3$으로 끝나고, 다시 135를 빼면 $3\to2\to1\to0$으로 복귀한다. 일반적인 원자 spectrum에는 여러 branch가 존재할 수 있으므로 inherited branch와 모든 algebraic roots를 별도 출력한다.

# 공변 경계와 전체 feedback

Spectral number current가 $\nabla_aj^a+\partial_W\mathcal F=\mathcal C$를 만족하면, 움직이는 cutoff가 만드는 수 source는

$$
\boxed{S_c=j_c^a\nabla_aE_c-\mathcal F_c.}
$$

낮은 에너지 영역에는 $S_c,E_cS_c$, 높은 영역에는 그 반대 부호가 들어간다. 경계 4-momentum의 시간 투영에서 rest mass를 빼면 운동에너지 전달 $E_cS_c$를 얻는다. $j_c^a=c\rho_cn^a$인 균질 경우에는 $S_c=\chi k_B\rho_c\dot T-B_c$로 기존 Bianchi 식과 연결된다.

Actual event extents $\xi_r(z)$로 raw inventory를 만든 뒤 cutoff EOS를 풀 때, 고정 cutoff의 thermal count·energy 증분을 $\nu_{N,r},\nu_{U,r}$로 쓰면

$$
\boxed{D_z\mathcal T=
\frac{\sum_r(\nu_{U,r}-c_v\mathcal T\nu_{N,r})D_z\xi_r}{C_{\rm eff}}.}
$$

이 식은 에너지 입력과 추가 열적 입자수의 효과를 함께 반영한다. $C_{\rm eff}$가 작아지면 같은 사건 오차에 대한 온도 응답과 density feedback이 커진다. CP.8–12는 이 식을 기존 사건량 Lipschitz bound와 합쳐 계산 가능한 수축상수 $q$로 만든다. $q<1$인 self-map에서는 inner EOS residual과 outer descriptor residual을 합친 오차를 $1/(1-q)$로 제어한다.

원자 표현에서는 prefix가 고정된 branch에 이 미분식과 수축 정리를 적용한다. Threshold crossing에는 유한 branch algorithm을 사용한다. 연속 표현을 쓰면 trial과 독립인 고정 선형 기저 또는 그보다 일반적인 표현의 추가 응답을 명시해야 한다.

# 실제 검증, 독립 검토와 해석 범위

## 이번에 실행한 검산

| 검산 대상 | 실제 결과 | 근거 |
|---|---|---|
| 9600-grid 및 source identity | 실제 energy array digest 일치; 11개 원본 파일 결속 | `KERNEL_SOURCE_BINDING` |
| 실제 사건 열 | 17개 열 × 4개 invariant residual 모두 exact zero | `KERNEL_ADAPTER_CHECKS` |
| 원래 floating projector와 exact layer | 최대 scale-normalized 차이 $8.42\times10^{-14}$ | 같은 기록 |
| 같은 family sharing 유지 | 실제 세 sharing points의 $\xi_\ell/p_\ell$ exact equality | `SHARING_CAPACITY_CHECKS` |
| 연속 cutoff reference | 가열 37회, 냉각 39회 이분; 각각 오차 $7.28\times10^{-13}$, $1.82\times10^{-13}$ in $T/T_*$ | `THERMAL_CUTOFF_CHECKS` |
| 원자 branch reference | 가열·냉각, equality, 복수 branch, $h=0$ 통과 | 같은 기록 |
| Wolfram scalar | 17개 zero group, 21개 scalar residual=0; 부등식 5개 참 | `WOLFRAM_SCALAR_RAW` |
| Wolfram 안의 xAct | 새 tensor residual 6개 모두 0 | `WOLFRAM_XACT_RAW` |

Wolfram kernel은 15.0.1, xTensor는 1.3.0, xPerm은 1.2.4였다. 공식 package bytes의 SHA256을 확인하고 pure Wolfram Language permutation 경로를 사용했다. xAct는 실제로 정의한 4차원 계량, 공변미분, 단위 시간벡터와 수 전류를 대상으로 selector product, partition cancellation, stress product, rest-mass energy subtraction, temperature cutoff current를 계산했다. 약한 분포 극한과 고정점 정리의 증명은 본문의 수학적 전제와 논증에 있다.

계산 도중 WolframContext의 내부 서비스 오류 1건이 있었으며 evaluator와 xAct 실행은 이어서 성공했다. 첫 scalar harness에서 `ForAll` 내부의 inline derivative 평가가 두 부등식에 잘못된 결과를 내어, 미분을 먼저 계산한 표현과 literal derivative를 대조했다. 그 진단에 따라 해당 두 구문을 고치고 새 canonical batch를 한 번 재실행했다. 최초 출력, 진단, 최종 출력을 모두 보존했다.

Actual-kernel의 큰-step 사례는 정확한 유한 장부와 양수성의 stress witness다. 여기서 나온 100 K→103.815911 K는 해당 구성 상태의 EOS 값이다. 그 step의 물리 시간 정확도나 새로운 우주론적 온도 예측을 뜻하지 않는다. 이전 unit의 과학 suite는 재실행하지 않았고, 전체 generator·새 물리 ODE·NCP job도 이번에 실행하지 않았다.

## 독립 검토가 보완한 전제

KC1–KC7은 명시된 가정 범위에서 모두 `PROMOTE_SCOPED / PASS`를 받았다. 심사에서 지적한 9개 항목은 모두 닫혔으며, 72개 근거 파일의 정확한 bytes를 동결했다. 최상위 주장·전제 기록의 판정 metadata 갱신은 과학 본문 hash와 별도로 결속했다.

독립 검토자는 유도·원본 함수·실행 code·actual raw output을 직접 대조했다. 높은 에너지 영역의 부분적분에는 $W\mathcal F(W)\to0$ 조건을 추가했고, CP의 연속 event reconstruction은 trial과 독립인 고정 선형 기저라는 전제를 명시했다. 문서의 비음성 표현과 $U\ge0\Rightarrow T\ge0$를 정밀화했다. Lipschitz 계수에 대한 CP bound는 고정 trial temperature의 root perturbation으로 직접 증명했다. 각 교정은 해당 범위를 유지하는 최소 보완이다.

## 물리 적용에 전달할 조건

Source는 HI·HeI cold-target full BED와 adopted excitation closure를 제공한다. HeII의 추가 이온화·재결합, finite-temperature diffusion, 모든 27개 여기 table에 대한 새 전체 generation은 각각 필요한 모형에서 추가하는 별도 입력이다. $\chi\ge3/2$는 원자 cutoff 해의 구성 조건이고, cold-target 정확도를 정량적으로 보장하는 조건은 아니다.

Source의 0.1 eV absorber 아래로 cutoff를 내려야 한다면 그 band의 실제 energy trace를 유지하거나 양의 reconstruction을 별도 결속해야 한다. Thermal 총 count·energy 두 값만으로 임의의 lower trace를 복원할 수는 없다. 이번 구현은 retained 원자 inventory를 명시적으로 유지하는 경로를 제공한다.

실제 적용에서 필요한 입력은 선택 source/history, $\chi$와 cutoff domain, thermal ownership, rate domain 및 이름·단위가 정해진 관측량 오차 예산이다. 현재 일반 이론의 성립 여부와 그 선택 응용의 물리 정확도는 각자의 근거로 판정한다.

# 다음 연구계획

기존 DAG의 `CR_THEORY_KERNEL_EVENT_ADAPTER`와 `CR_THEORY_THERMAL_CUTOFF_FEEDBACK`를 이번 결과에 연결했다. 다음 순서는 다음과 같다.

| 다음 노드 | 바로 수행할 첫 구성 | 완료 기준 |
|---|---|---|
| Coupled branch solver | 실제 HI·HeI subfamily, retained atoms, CP.3 모멘트로 한 branch의 온도·전자밀도·조성 endpoint를 함께 구성 | 실제 domain과 self-map, 잔차 예산, 한 threshold crossing의 보존·branch 선택 |
| Geometry 이후 kernel 재결속 | prescribed Bianchi redshift로 바뀐 actual parent energy에 daughter projector와 rate domain을 다시 결속 | geometry work와 cutoff source의 단일 장부, 현재 energy identity 및 representation error |
| 선택 응용 | 실제 source/history와 관측량의 허용오차를 앞의 결과에 연결 | 해당 source와 receiver 범위의 물리·수치 오차 근거 |

이론의 다음 두 구성은 일반 입력으로 시작할 수 있다. 선택 응용은 기존 DAG에 남아 있는 source/scenario 및 observable budget의 의존성을 사용한다. 다음 세션에서는 `HANDOFF.json`과 `NEXT_DAG.json`을 읽고 현재 동결 근거를 재사용한다.

## 연구 루프 수행 기록

R1 계약과 두 열린 노드 선택, R2 원본·이전 근거 재사용, R3 주장·전제 분리, R4 연속·원자 표현의 비교, R5 실제 구성과 증명, R6 독립 검토, R7 판별 계산, R8 범위별 판정, R9 reference 구현·정식 보고서, R10 DAG·source·인계본을 연결했다. C1–C10은 같은 식·입력에서 유도된 작은 구현, exact reference, source identity 및 독립 코드 검토로 이어진다. 단계별 근거 위치는 `policy/LOOP_RECORD.json`에 있다.

# 전체 유도

다음 세 장은 실제 원자 source에서 시작하는 KA, 온도 의존 finite cutoff의 TCF, 공변 경계와 전체 결합 bound의 CV·CP를 수록한다. 첫머리의 결과 설명과 같은 수식·범위를 사용한다.

<!-- DERIVATIONS -->

\clearpage

# 가까운 1차 문헌과의 비교

<!-- LITERATURE -->

# 재현 자료 안내

전체 source 묶음은 LaTeX 원문·도표·실행 코드·원본 입력 identity·새 실행 결과·Wolfram/xAct 원출력·독립 검토·DAG를 포함한다. `build_report.py`는 기존 결과로 그림과 보고서만 다시 만들며 과학 suite를 실행하지 않는다. Reference 실행은 각 `checks` 파일로 개별 구분되어 있다. 유지된 과학 근거의 사용에는 재실행이 필요하지 않다.

Source 재현 순서는 `CONTRACT.json`의 단위·범위를 확인하고, `inputs/KERNEL_SOURCE_BINDING.json`의 실제 입력을 유지한 뒤 필요한 변경 의존성만 실행하는 것이다. 원자 kernel의 전체 qualification 또는 선택된 외부 역사에는 해당 별도 node의 계약을 적용한다. 출판 commit과 PDF/source archive의 실제 identity는 최종 `PUBLICATION.json`, `DELIVERY.json`, `HANDOFF.json`에 기록한다.

외부 논문의 조회 원문 cache 11개는 로컬 심사의 동결 근거로 유지하고 배포 묶음에서는 제외했다. `EXTERNAL_REFERENCE_INDEX.json`은 해당 자료의 URL·조회 조건·크기·SHA256을 기록한다. 문헌 비교와 출처 목록, 자체 유도 및 실제 Wolfram/xAct 출력은 묶음에 포함한다. 이 배포 구분은 `review/CANDIDATE_MANIFEST.json`의 심사 당시 파일 identity를 바꾸지 않는다.
