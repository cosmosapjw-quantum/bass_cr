# PHYS02 부모 사건과 조건부 native25 — 수동 유도 초안

## 0. 신분, 고정 계약, 읽기 범위

단위는 **CR_PHYS02_PARENT_EVENT_NATIVE25_V1**이다. R1 실제 게시 commit은 fbc039ff5c357571cbbf2ff61d96fde8b3ce8594이고 draft PR111에 속한다.
고정 CONTRACT.json의 SHA256은 **01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162**,
CONDITIONING_DEFINITION.json의 SHA256은 **90f0b4e049ab289fbf0a7dd205f4dbc720dbf32547f99f3444a3d3a83b4059bc**이다.
이 문서는 그 파일을 변경하지 않는 R4 표현·R5 구성적 증명·R9 구현계약용 초안이다. root의 해당 단계 preflight나 게시가 완료됐다고 선언하지 않는다.

작성자는 이론/입력 식별 제안자이며 이전 PR110 theory/reference 저자다. 현재 문서를 독립심사라고 부르지 않는다.
수식은 수동으로 유도했다. 새 물리 runtime, CAS, scientific import, compile, test, 기존 source/proton quadrature/G/RR 실행은 모두0이다.
실제 코드로 DirectElectronSource, Rudd port, source_vectors, number-linear project와 PR110 saved-result schema를 읽었다.
필요한 원문·바이트·source pin은 `inputs/SOURCE_LINEAGE_MANIFEST.json`과 `inputs/INPUT_MANIFEST.json`에, primary 문헌 대조는 `literature/LITERATURE_MAP_KO.md`에 결속돼 있다.

선행 response identity는 S2eed7ef835c55ee17e4ce96e0eda7fe8d82dc47c, D616b166fa0108ca35defece3f8c9d99fc79895cb,
M42cc3a909688d670200ba09c500e2ca83a94fa10이다. 원 canonical source JSON SHA8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf를 바꾸지 않는다.

## 1. 변수와 물리 범위

모든 N은 proper m^-3, U·Q·K는 별도 표시가 없으면 eV proper m^-3, t는 proper second이다.
source spectrum은 q_s(t,W)=t A_s(W), A_s의 단위는 m^-3 s^-2 eV^-1이다.
알려진 이력은 0≤t≤T=1e10 s이고 처음 선택 cohort는0이다. 이력 밖 continuation/shutoff는 unknown이다.
Frame은 prescribed gas-rest nonrelativistic scalar, volume은 fixed proper-volume density convention이다.
절대 V 또는 worldtube 총수는 주어지지 않았다.

source에서 nH=140과 nHe=140·0.248/[4(1−0.248)]는 전체 핵 수 밀도다.
neutral target 인자는 각각0.99이며 이미 원 A에 들어 있다.
원 q_p의 comoving→proper729, angle integration, proton velocity, neutral density 역시 A의 생성단계에 들어 있다.
새 귀속 또는 native25 사상에서 이를 다시 곱하지 않는다.

새로 명시된 동일상태 conditional H1/He4 inventory는
n_H=140, n_He=1085/94, n_e,0=2849/1880, n_b=8750/47 m^-3, T0=100 K,
x_HII=x_HeII=.01,x_HeIII=0이다.
이 정확한 의미의 inventory와 원 source의 literal binary64 density recipe를 구분하고 원 source를 재정규화하지 않는다.
예전 PR109의 nb=null을 소급 수정하지 않는다.

선택 birth support는 실제 tag direct_0p1_10의 W∈[.1,10] eV다.
current E≤10 필터로 high-born 경계 atom을 섞지 않는다.
공통 source계수 식별에 쓰는 W∈[0,1000]은 원 source의 정보 범위이며, 이번 transport/consumer birth support를 늘리는 것이 아니다.
보존된 source coverage의 모든 proton node에 대한 최소 endpoint2154.927725029828 eV가 이 식별 범위를 덮는다.
원 proton collision window1–4MeV, source H/He elemental→H1/He4 조건, zero recoil 모델 범위를 유지한다.
이 모델은 charge exchange·전하변환된 projectile·nuclear reaction 또는 state-resolved physical accuracy를 새로 제공하지 않는다.

## 2. source를 세 개 고정 basis로 쓰는 이유

원 소스 코드는 각 표적에 대해

\[
A_s(W)=\frac{c_{1s}+c_{2s}W/I_s}{(1+W/I_s)^3}
\tag{1}
\]

를 사용한다. H threshold는 원 source의 \(I_H^{src}=13.605693122994\) eV,
He threshold는 \(I_1^{src}=24.59\) eV다.
H Williams-limit는 각 proton node에서 \(F_{1H}=7/(3v^2),F_{2H}=1/v^2\)이므로 실수식에서
\(c_{1H}=(7/3)c_{2H}\)이다.
\(f_0(I,W)=(1+W/I)^{-3}, f_1(I,W)=(W/I)(1+W/I)^{-3}\)로 놓으면

\[
\begin{split}
g_H(W)&=(7/3)f_0(I_H,W)+f_1(I_H,W),\\
g_{He0}(W)&=f_0(I_1,W),\qquad g_{He1}(W)=f_1(I_1,W),\\
A(W)&=\theta_H g_H(W)+\theta_{He0}g_{He0}(W)+\theta_{He1}g_{He1}(W).
\end{split}
\tag{2}
\]

이 본문의 수학기호는 0-based He basis를 사용한다. 고정 계약·코드의 coefficient order는 `(theta_H, theta_He1, theta_He2)`이며, 명시적 대응은 `theta_He0_theory = theta_He1_contract` 및 `theta_He1_theory = theta_He2_contract`이다. 따라서 두 문서의 접미사만으로 열을 정렬하지 않고 이 대응표로 결속한다. 계수는 세 개이며 물리적 의미나 frozen CONTRACT를 변경하지 않는다.

모든 theta의 단위는 A와 같다. 이미 적분된 원 proton source/target normalization이 이 세 scalar 안에 포함된다.
원 64-point proton quadrature의 node나 flux를 다시 평가할 필요가 없다.

**함수 수준의 독립성.** H basis의 유리함수 표현은
\(I_H^2[W+(7/3)I_H]/(W+I_H)^3\)이다.
\(W=-I_H\)에서 분자는 \((4/3)I_H^3\ne0\)이고 두 He basis는 이 점에서 regular하다.
따라서 열린 W 구간에서 세 basis의 선형결합이0이면 유리함수 항등식의 H pole 계수가0이어야 한다.
남은 He numerator는 \(bI_1^3+cI_1^2W\)이므로 b=c=0이다.
이는 함수 식별 가능성을 보인다. 선택한 세 finite band의 moment matrix conditioning까지 자동 증명하지는 않는다.

원 H c1,c2가 별도 binary64 dot product로 조립됐다는 점도 남는다.
정확한 실수 관계와 실제 저장 binary64 source 사이의 작은 차이는 frozen unused-moment/atom 검증 대상이다.
세 계수 fit가 실패해도 네 계수로 바꾸거나 원 source를 새로 계산하지 않는다.

## 3. moment primitive: 차분 상쇄를 피하는 구성

I>0,0≤a≤b를 놓고 다음 네 적분을 정의한다.

\[
N_0(I;a,b)=\int_a^b f_0\,dW,\quad N_1(I;a,b)=\int_a^b f_1\,dW,
\]
\[
E_0(I;a,b)=\int_a^b Wf_0\,dW,\quad E_1(I;a,b)=\int_a^b Wf_1\,dW.
\tag{3}
\]

원시함수의 단순 차분도 수학적으로 맞지만, a=0,b=.1에서 E1은 작은 양을 얻기 위해 더 큰 로그·유리항을 뺀다.
다음 표현은 모든 coefficient가 비음수여서 그 상쇄를 피한다.

\[
K=I+a,\qquad h=(b-a)/K,\qquad z=h/(1+h)=\frac{b-a}{I+b}\in[0,1).
\tag{4}
\]

W=a+Ku로 바꾸고
\(F_r=\int_0^h u^r/(1+u)^3\,du\)로 놓으면

\[
F_0=z(1-z/2),\qquad F_1=z^2/2,
\]
\[
F_2=\log(1+h)-z-z^2/2
    =-\log(1-z)-z-z^2/2
    =\sum_{k=3}^{\infty}\frac{z^k}{k}.
\tag{5}
\]

마지막 식은 v=u/(1+u) 치환으로
\(\int_0^z v^2/(1-v)\,dv\)를 얻어 증명된다.
따라서

\[
\begin{array}{ll}
N_0=\dfrac{I^3}{K^2}F_0,&
N_1=\dfrac{I^2}{K^2}(aF_0+KF_1),\\[4pt]
E_0=I N_1,&
E_1=\dfrac{I^2}{K^2}(a^2F_0+2aKF_1+K^2F_2).
\end{array}
\tag{6}
\]

모든 항이 양수이며 a=b일 때는 네 적분을 정확히0으로 반환한다.
f1이 아닌 f0의 H 조합에는 N_H=(7/3)N0_H+N1_H, E_H=(7/3)E0_H+E1_H를 사용한다.

### 3.1 구현 가능한 안정된 F2 평가

작은 z에는 positive series를 사용한다. m≥3까지 더했다면

\[
0\le F_2-\sum_{k=3}^{m}z^k/k
\le \frac{z^{m+1}}{(m+1)(1-z)}.
\tag{7}
\]

예를 들어 z≤1/2에서는 이 잔여 상계가 부분합의1e-70 이하가 될 때 종료하는 fixed highprecision 방식을 사용할 수 있다.
이는 작은 3×3 moment 평가의 내부 산술 정확도 목표이며 R1 허용치를 바꾸지 않는다.
z>1/2에서는 80digits 이상의 Decimal log 표현
\(\log[(I+b)/(I+a)]-z-z^2/2\)를 사용할 수 있다.
그 영역에서 \(F_2\ge z^3/3>1/24\)여서 작은-z의 심한 cancellation이 없다.
이 ordinary highprecision 계산을 outward interval arithmetic 인증이라고 부르지는 않는다.

독립 reference는 Eq6을 그대로 복사하지 않아도 된다.
예컨대 x=W/I에 대한 별도 원시함수
\[
\int f_0\,dW=-I/[2(1+x)^2],
\]
\[
\int f_1\,dW=I[-(1+x)^{-1}+\tfrac12(1+x)^{-2}],
\]
\[
\int W f_1\,dW=I^2[\log(1+x)+2/(1+x)-\tfrac12(1+x)^{-2}]
\tag{8}
\]
의80digits 이상 차분으로 작은 band를 검증할 수 있다.
\(E_0=I N_1\)는 차원과 derivative 검사의 독립 단서다.

### 3.2 literal과 binary64의 역할

원 JSON moment, 원 grid, 원 source atom의 binary64 bit pattern은 authoritative다.
새 고정밀 numerical fit는 기존 binary64로 round-trip되는 입력을 정확히 고정밀로 올리는 방식(예: Decimal.from_float)을 명시해야 한다.
기존 source 상수/경계의 원 binary64 표현을 사용하면 그 사실을 manifest에 기록한다.
에너지 convention sidecar에서는 선언된 decimal lexeme13.605693122994,13.60을 별도로 보존한다.
표현의 tiny roundoff를 새로운 threshold 물리로 해석하거나 원 atom에 반영하지 않는다.

## 4. scaled recovery, 민감도, 양수성

recovery bands는 [0,.1],[3,10],[100,1000]이고 b_i는 실제 저장된 band energy coefficient다.
\(M_{ij}=\int_{a_i}^{b_i} Wg_j(W)dW\)를 Eq6으로 계산한다.
holdout [.1,1],[1,3],[10,100]은 coefficient fit에 사용하지 않는다.

고정 CONDITIONING_DEFINITION대로
\[
R=\operatorname{diag}(1/b_i),\quad
c_j=1/\max_i |(RM)_{ij}|,\quad
B=RM\operatorname{diag}(c_j)
\tag{9}
\]
로 두면
\[
Bz=\mathbf1,\qquad \theta=\operatorname{diag}(c_j)z.
\tag{10}
\]

b_i>0이고 column scale이 finite positive임을 먼저 검사한다.
수치해는 작은3×3 pivoted solve 또는 고정밀 inverse로 얻고 residual을 별도 기록한다.
동일 inverse에서
\[
\operatorname{rcond}_{\infty}(B)
=\frac1{\|B\|_\infty\|B^{-1}\|_\infty}\ge10^{-6}
\tag{11}
\]
를 요구한다.

행렬 M을 고정하고 실제 moment perturbation을
\(|\delta b_i|\le\eta b_i,\eta=2\times10^{-12}\)로 제한하면,
row scaling을 nominal b로 고정한 식에서
\(B\delta z=R\delta b\)이고

\[
|\delta z|\le d_z:=\eta |B^{-1}|\mathbf1.
\tag{12}
\]

따라서 모든 j에 대해 \(d_{z,j}/|z_j|\le10^{-8}\), \(z_j-d_{z,j}>0\)를 요구한다.
이는 선언된 numerical consistency envelope의 선형 perturbation 결과다.
행렬 primitive/solve의 ordinary arithmetic error 및 원 source의 model accuracy를 자동 인증하지 않는다.
행렬 오차는 독립 primitive/solve 검증에 포함한다.

원 식의 exact pole 독립성, finite-band matrix의 conditioning, 저장 데이터 consistency, 물리적 모델의 정확도는 서로 다른 판정이다.
조건을 못 맞추면 MODEL_IDENTIFICATION_UNRESOLVED다.
theta 출력의 의미는 MODEL_IDENTIFIED_FROM_PINNED_MOMENTS이고 ORIGINAL_SAVED_COEFFICIENT_BYTES가 아니다.

## 5. 원 8점 cell projection을 basis마다 적용

원 low grid는 저장된 \(e_0=.1<e_1<\cdots<e_{3200}=10\)을 사용한다.
e0는 absorber ghost이고 e1…e3200만 active다.
원 코드가 사용하는 각 cell [e_(j−1),e_j]의 Gauss8 abscissa ξ_l,weight w_l에 대해

\[
W_{jl}=(e_{j-1}+e_j)/2+(e_j-e_{j-1})\xi_l/2,\qquad
\omega_{jl}=(e_j-e_{j-1})w_l/2,
\tag{13}
\]
\[
\alpha_{jl}=(W_{jl}-e_{j-1})/(e_j-e_{j-1})
\tag{14}
\]
이다.

원 source_vectors는 각 cell에서 source A를 평가하고, 원 selected_A_energy로 나눈 뒤
project로 number를 \(\alpha\)와 \(1-\alpha\)에 나눈 다음 active 좌표에 E를 곱한다.
새 귀속은 전체 Cascade를 생성하지 않고 이 작은 source projection 정의만 재현한다.
기존 generator/_sharing/_generator/evolve/terminal_yields를 호출하지 않는다.

각 basis g_r에 대해 number-coordinate projection kernel을
\[
K_{jr}^{up}=\sum_l\omega_{jl}g_r(W_{jl})\alpha_{jl},\quad
K_{j-1,r}^{down}=\sum_l\omega_{jl}g_r(W_{jl})(1-\alpha_{jl})
\tag{15}
\]
로 누적한다.
j=1의 down은 active로 보내지 않고 cutoff ghost0에 둔다.
그러면 \(a_{Hj}=\theta_HK_{jH}\),
\(a_{Hej}=\theta_{He0}K_{j,He0}+\theta_{He1}K_{j,He1}\)이다.
이 a의 단위는 proper m^-3 s^-2이다.

원 normalized energy coordinate b_j와 실제 canonical number A_j의 관계는 실수식에서
\[
A_j=(U_*/T^2)\,b_j/e_j,\quad U_*/T^2=A^{selected}_{energy},
\tag{16}
\]
이다. 따라서 normalization이 취소돼 Eq15와 같아진다.
cutoff-number ledger에는 b_cutN을 사용하고 E로 다시 나누지 않는다.
이 관계는 기존 byte를 검증하기 위한 표현 일치다. 원 U*·source column·A를 새 값으로 바꾸지 않는다.

**보존 증명.** 한 quadrature weight p의 number는
\(p\alpha+p(1-\alpha)=p\)이고 energy는
\(p[\alpha e_j+(1-\alpha)e_{j-1}]=pW\)이다.
따라서 ghost를 포함한 projection은 quadrature에 대해 count와 kinetic energy를 보존한다.
\(\theta\)가 positive이고 Gauss weights·barycentric factors가 positive이므로 각 target atom도 positive이다.
Gauss8의 연속 적분 정확도와 floating accumulation 오차는 별도 consistency 검사다.

**금지되는 shortcut.**
\(A_j^{canon}A_s(e_j)/A(e_j)\)는 일반적으로 \(P_j[A_s]\)와 같지 않다.
cell 평균과 target fraction이 교환되지 않기 때문이다.
또한 재구성 a_H+a_He가 canonical에 조금 다르다고 각 atom을 강제로 renormalize하거나 차이를 한 target에 밀어 넣지 않는다.

새 coefficient의 projected atoms는 canonical atoms 자신의 scale에서2e-11,
analytic low moments와 target별 projected N/E, total canonical N/E는 계약에 지정된 기준으로 비교한다.
source atoms의 exactzero는 absolutezero 규칙을 쓴다.
원 canonical actual source는 이후 consumer에서도 authoritative로 남는다.

## 6. 유한 clock과 네 prefix/네 observation bin

시간점은 t_k=kT/4,k=1…4이다. prefix P_k=[0,t_k]는 nonadditive diagnostic이다.
네 bin B_k=(t_(k−1),t_k]는 누적 결과의 차이로 정의하며, 연속율의 끝점 차이는 measure0이다.

새 target source의 number/energy coefficients를
\[
A_{sN}^{disc}=\sum_{j=0}^{3200}a_{sj},\quad
A_{sU}^{disc}=\sum_{j=0}^{3200}e_j a_{sj}
\tag{17}
\]
로 두면 source birth extent는
\[
J_s[a,b]=\tfrac12(b-a)(b+a)A_{sN}^{disc},\quad
U_s[a,b]=\tfrac12(b-a)(b+a)A_{sU}^{disc}.
\tag{18}
\]
source endpoint rates는 tA_sN,tA_sU다. T에서는 known-history left limit이다.
a=b는 정확히0이고 [0,T] 밖 query는 거절한다.
\((b-a)(b+a)/2\)는 가까운 두 큰 제곱의 차를 피한다.
proper clock factor를 한 번 썼으므로 다시 exposure,1/H,volume factor를 곱하지 않는다.

이와 별도로 **PR110의 actual selected response**를 읽는다.
prefix에는 N_active,U_active; bin에는 active_number_change,active_energy_change가 있다.
각 bin의 N_cut,Q_C,C_H,C_He,K_H,K_He,retained photon은 saved bin 그대로 쓴다.
이 RR는 이전 bin에 태어난 전자의 생존분을 포함한다.
각 bin을 빈 초기상태로 다시 시작하거나 conditional mean time을 exposure로 쓰지 않는다.

표기의 혼동을 피하기 위해 다음 saved identity를 사용한다.
\[
N_{inj}^{save}=\Delta N_A+N_C+C_H+C_{He},
\]
\[
U_{inj}^{save}=\Delta U_A+U_C+Q_C+K_H+K_{He}.
\tag{19}
\]
prefix에서 ΔN_A=N_A,ΔU_A=U_A이고, bin에서는 endpoint 차이다.
N_C는 direct+drift cutoff, U_C는 그 saved energy다.
number/energy right-hand sides는 기존 floating residual을 가질 수 있으며 바이트를 고치지 않는다.

새 split의
\[
\epsilon_N=J_H+N_{He}-N_{inj}^{save},\quad
\epsilon_U=U_H+U_{He}-U_{inj}^{save}
\tag{20}
\]
는 attribution consistency residual이다.
이를 physical free electron이나 heat로 해석하지 않는다.
별도 기록·허용치 검사하고 canonical source와 saved response를 renormalize하지 않는다.

## 7. He marginal의 실제 사건 의미와 일반 family

[Rudd1992 §II](https://doi.org/10.1103/RevModPhys.64.441)의 SDCS는 electron-production marginal이다.
원 source는 target label을 합산했지만 exclusive He ion charge state와 electron pair를 저장하지 않았다.
source basis 식별은 H/He 전자 기원을 복원하는 작업이며, 이 잃어버린 joint-event 정보를 추가로 만들어내지 않는다.

직접 자유전자 방출이라는 원 channel 모델 안에서 selected window와 교차하는 He 사건의 누적 수를 s,p,d로 둔다.

| 종류 | selected e | outside partner e | He 잔류 charge |
|---|---:|---:|---:|
| s: single ionization |1|0|1|
| p: double, 한 전자만 선택 |1|1|2|
| d: double, 두 전자 선택 |2|0|2|

그러므로
\[
s+p+2d=N_{He},\quad p\ge0,\ d\ge0,\ p+2d\le N_{He},
\tag{21}
\]
\[
\Delta n_{HeI}=-(N_{He}-d),\quad
\Delta n_{HeII}=N_{He}-p-2d,\quad
\Delta n_{HeIII}=p+d.
\tag{22}
\]

이 domain은 selected marginal이 주는 **필요한 affine 제약**이다.
전체 source support에 걸친 실제 joint kernel의 모든 제약을 만족하는 충분조건이라고 하지 않는다.
예컨대 mixed event는 선택 밖 marginal에도 partner 한 개를 사용해야 한다.
원 all-W He scalar는 low parent count로 직접 대입할 수 없으며, 전체 branch/state 복구를 대신하지 않는다.

nonidentifiability는 '새 physical channel 불가능'이라는 strong no-go가 아니다.
동일한 selected marginal에서 p=0,d=0과 적절히 paired한 p=0,d>0의 conditional family가 서로 다른 He species inventory를 만든다.
mixed partner의 허용된 작은 변화도 같은 selected marginal을 유지하면서 총 electron charge를 바꿀 수 있다.
이 예들은 실제 branch point가 아니라 필요한 추가 자료가 어떤 것인지를 보여주는 constructive family다.

p=0 또는 d=0을 실제 기본값으로 채우지 않는다.
s,p,d actual값과 energy-resolved pair/history는 null이다.
He+ residual excitation 역시 inclusive source에서 제공되지 않는다.
새 state-resolved 자료가 오면 별도 hidden atomic port를 묶어야 한다.
source ionization operator에 없는 transfer/capture 또는 projectile state 변화도 이 family로 해결했다고 주장하지 않는다.

## 8. source 부모와 saved RR를 합성한 species/charge 장부

H는 원 atomic-H direct channel과 conditional H1 mapping에서 선택 전자 하나당 parent H1I→H1II 하나이다.
저장 RR target과 그 전자의 source parent target은 구별한다.
H에서 태어난 전자가 He에 잡힐 수도 있으므로 둘을 동일 label로 묶지 않는다.

같은 observation interval의 source births J_H,N_He와 saved selected RR C_H,C_He를 합성하면
\[
\begin{array}{ll}
\Delta n_{H1I}=-J_H+C_H,&\Delta n_{H1II}=J_H-C_H,\\
\Delta n_{He4I}=-N_{He}+d+C_{He},&
\Delta n_{He4II}=N_{He}-p-2d-C_{He},\\
\Delta n_{He4III}=p+d.&
\end{array}
\tag{23}
\]

각 원소의 핵 수와 nb는 보존된다. projectile는 이 selected direct event의 양쪽에 남는다.
이는 전체 외부 proton injection의 baryon history가 닫혔다는 뜻이 아니다.
후속 partner의 RR/escape/thermal response는 Eq23에 없고 unknown addendum이다.

native 순서는 기존 실제 code의21species 뒤 ζ21,w_nt22,w_ext23,logT24이다.
H1I/II index1/2,He4I/II/III index10/11/12다.
Eq23을 nb로 **한 번** 나눈다.
p,d의 단위가 proper m^-3일 때 affine coefficient vectors의 nonzero entries는

\[
v_p:\quad (HeII,HeIII)=(-1,+1)/n_b,
\]
\[
v_d:\quad (HeI,HeII,HeIII)=(+1,-2,+1)/n_b.
\tag{24}
\]

v0는 p=d=0에서의 algebraic intercept일 뿐 실제 branch point가 아니다.
actual parameter values는 null로 둔다.

native total free-electron charge 변화는
\[
n_b\,q\cdot\Delta Y=J_H+N_{He}+p-C_H-C_{He}.
\tag{25}
\]
ζ가 selected electrons만 세면 unresolved partner p가 \(g=q\cdot Y-\zeta\)에 잘못 들어간다.
partner가 어떤 pool에 있고 어떤 반응을 했는지 입력받지 않고 이 차이를 thermal electron으로 채우면 안 된다.

default cutoff-retention convention에서 selected
\[
n_b\Delta\zeta_{\rm ret}=\Delta N_A+N_C,\quad
n_b\Delta w_{nt,\rm ret}=(\Delta U_A+U_C)eV_J.
\tag{26}
\]
instant assimilation fixture에서는
\[
n_b\Delta\zeta_{\rm assm}=\Delta N_A,\quad
n_b\Delta w_{nt,\rm assm}=\Delta U_A\,eV_J.
\tag{27}
\]

Eq19가 exact이고 split이 일치할 때 charge-minus-selected-fast는 retention에서 p,
assimilation에서 p+N_C다.
실제 numerical output에는 Eq20의 εN 및 기존 saved count residual이 추가되므로 그 잔차를 별도로 보고한다.
εN을 thermalization이라고 부르거나 보정용 species/ζ increment로 넣지 않는다.
partner의 pool·native response가 없으면 **actual full physical native25=null**이다.

## 9. kinetic, photon, chemical convention 및 missing work를 분리

저장된 RR photon은 각 capture energy atom에서
\[
E_{\gamma,H}=E+I_H^{RR},\quad E_{\gamma,He}=E+I_{He}^{RR},
\]
\[
U_\gamma=K_H+K_{He}+I_H^{RR}C_H+I_{He}^{RR}C_{He}.
\tag{28}
\]
여기서 \(I_H^{RR}=13.60,I_{He}^{RR}=24.59\) eV이다.
실제 saved arrays의 capture atoms를 재사용하며 N/E moments로 새로운 spectrum이나 history를 만들지 않는다.
retained photons는 transport/absorption/escape를 수행하지 않은 별도 port다.

### 9.1 식별 가능한 electron-equivalent source functional

원 CRIPTIC primary [Eq23](https://arxiv.org/pdf/2207.13838)은 \(\int(W+I)d\sigma\) 형태다.
새 귀속의 source functional은
\[
L_0=U_{inj}^{save}+I_H^{src}J_H+I_1^{src}N_{He}.
\tag{29}
\]
kinetic 부분은 canonical saved source를 유지하고 binding 부분은 새 model-identified target split을 쓴다.
별도로 analytic/projected U_H+U_He와의 εU를 출력한다.
Eq29는 실제 exclusive-He projectile depletion/history가 아니라 원 모형의 selected kinetic-plus-binding functional이다.

recipient chemical potential을 HII:\(I_H^*\),HeII:\(I_1^*\),HeIII:\(I_1^*+I_2^*\)로 두면
\[
\Delta B^*
=I_H^*(J_H-C_H)+I_1^*(N_{He}-C_{He})
 +I_2^*p+(I_2^*-I_1^*)d.
\tag{30}
\]
현재 native code의 H13.6,HeI24.59,HeII54.42는 **recipient representation**의 실제 pin이다.
I2src를 이 값으로 자동 대입해 실제 double-ionization donor data를 만들지 않는다.

### 9.2 literal convention residual

다음을 정의한다.
\[
R_{\rm const}=
(I_H^{src}-I_H^*)J_H+(I_1^{src}-I_1^*)N_{He}
 +(I_H^*-I_H^{RR})C_H+(I_1^*-I_{He}^{RR})C_{He},
\tag{31}
\]
\[
B_{\rm branch}^*=I_2^*p+(I_2^*-I_1^*)d.
\tag{32}
\]

saved kinetic identity가 exact라면
\[
L_0-[\Delta U_A+Q_C+U_C+U_\gamma+\Delta B^*]
=R_{\rm const}-B_{\rm branch}^*.
\tag{33}
\]
실제 검사는 기존 saved energy residual도 그대로 포함해 양변 차를 기록한다.
p=d=0의 명시적 closed one-electron fixture에서는 우변이 Rconst뿐이다.
IH*=IHRR=13.60이면 source H 차이의 coefficient는 정확한 선언 lexeme로0.005693122994 eV다.

Rconst는 literal convention sidecar다.
Bbranch는 미제공 exclusive branch의 추가 chemical storage이지 literal rounding 또는 heat가 아니다.
둘을 한 scalar 'heating correction'으로 합치지 않는다.

### 9.3 필요한 실제 branch work와 partner

source의 독점 double binding I2src, partner kinetic energy U_partner, residual excitation X를 실제로 제공받으면
zero-recoil 조건 아래 필요한 donor work는
\[
L_{\rm req}=L_0+U_{\rm partner}
 +I_2^{src}p+(I_2^{src}-I_1^{src})d+X.
\tag{34}
\]
원 모델 밖 recoil/projectile-state energy가 있다면 별도 항과 계약이 필요하다.
Lreq를 실제 proton history의 측정/계산 debit라고 부르려면 donor가 그 동일 사건·시간·volume에서 실제로 제공해야 한다.

선택한 source/recipient convention 사이의 branch-only 차이는
\[
R_{\rm branch}
=(I_2^{src}-I_2^*)p
+\{(I_2^{src}-I_1^{src})-(I_2^*-I_1^*)\}d.
\tag{35}
\]
전체 balance를 구성할 때 U_partner와 X를 각각 자신의 port로 보존하고 Rconst,Rbranch를 분리한다.
partner의 이후 흐름은 별도 response 입력 없이 추정하지 않는다.

actual external work/proton debit는 null이다.
고정 계약의 scoped_projected_w_ext=0은 지금 다루는 retained-port projection의 기여0이라는 의미다.
retained photon w_ext contribution도0이다.
이 두0을 실제 전체 external reservoir나 전체 donor work가0이라는 주장으로 바꾸지 않는다.
actual full physical native25 point는 계속 null이다.

## 10. default retention과 선택적 finite-caloric closure

### 10.1 기본값

N_C,U_C는 unresolved retained electron reservoir다.
Eq26에 따라 선택된 비열적 subset 안에 보관한다고 명시할 수 있으나, 아래 cutoff에서 energy spectrum이나 thermal distribution을 새로 만들지 않는다.
actual temperature update는 partner/branch/EOS closure가 없으면 null이다.
기존 PR110 Q_C는 prescribed caloric stopping ledger였다는 원 판정을 바꾸지 않는다.

### 10.2 명시적인 conditional fixture

새 consumer가 다음을 모두 명시한 경우에만 finite caloric 값을 평가한다.

- translational ideal-gas EOS \(U_{th}=c_v n_{part}T,c_v=3k_B/2\);
- retained-cutoff 또는 instant-assimilation 중 선택한 closure;
- partner의 thermal count/energy 및 native response closure(예: p=0을 실제값이 아닌 fixture로 명시);
- hidden excitation의 별도 보관 및 thermal energy 미전입;
- source/model work가 actual donor debit는 아니라는 표시;
- native species baseline+delta nonnegative, nb>0,thermal count>0,T>0.

assimilation에서는 \(Q=(Q_C+U_C)eV_J,\Delta n_{th}=N_C\)이다.
retention의 명시적 EOS fixture라면 \(Q=Q_C eV_J,\Delta n_{th}=0\)이며 U_C는 비열 reservoir에 남는다.
실제 partner가 있으면 그 입력된 thermal/energy response를 더해야 한다. unknown을0으로 두지 않는다.

초기 \(n_{part,0}=n_H+n_{He}+n_{e,0}\)와 T0=100 K에서
\[
T_1=\frac{n_{part,0}T_0+Q/c_v}{n_{part,0}+\Delta n_{th}},
\]
\[
\delta:=\frac{T_1-T_0}{T_0}
=\frac{Q/(c_vT_0)-\Delta n_{th}}
       {n_{part,0}+\Delta n_{th}},\qquad
\Delta\log T=\log1p(\delta).
\tag{36}
\]

새 열전자가 들어오면 입자 수가 증가하므로 Q>0만으로 ΔT>0가 항상 성립하지는 않는다.
부호는 \(Q-c_vT_0\Delta n_{th}\)가 정한다.
직접 T1−T0 또는 log(T1)−log(T0)를 binary64로 계산해 tiny 값을 잃지 않는다.

### 10.3 bin의 baseline은 앞 bin의 conditional endpoint다

네 prefix와 네 bin을 모두 처음100K에서 독립 적용해 합산하면 finite EOS와 맞지 않는다.
누적 thermal energy \(U_a=U_{th,0}+Q[0,a]\)와 particle density
\(D_a=n_{part,0}+\Delta n_{th}[0,a]\)를 two-part/highprecision로 보관한다.
bin의 q=Q[a,b],n=Δn_th[a,b]에 대해
\[
\frac{T_b}{T_a}=\frac{(U_a+q)D_a}{U_a(D_a+n)},
\]
\[
\delta_{ab}=\frac{qD_a-U_a n}{U_a(D_a+n)},\qquad
\log T_b-\log T_a=\log1p(\delta_{ab}).
\tag{37}
\]

이 식은 energy/particle increments만 사용하므로 baseline의 tiny 변화가 사라져도 increment를 보존할 수 있다.
모든 prefix는 같은 초기 conditional baseline을 기준으로, 각 bin은 그 앞 endpoint를 기준으로 설명한다.
합친 네 bin의 energy/particle counts는 마지막 prefix와 같아야 하고,
log increments의 합은 해당 prefix의 stable log ratio와 허용치 안에서 맞아야 한다.

이것은 frozen100K response를 사용한 명시적 EOS postprocessing이다.
새 T에 맞춰 stopping/hazards/source를 갱신하지 않았으며 coupled thermal history를 푼 결과가 아니다.
physical_heating_complete=false와 global null은 그대로다.

## 11. baseline+delta 표현

baseline species는 exact conditional inventory/nb에서 만들며 원 source rounding을 그 baseline에 억지로 맞추지 않는다.
21species order,charge,mass-number vector를 실제 native identity와 결속한다.
출력의 authoritative 부분은 baseline와 delta 및 He의 affine coefficient다.
baseline+delta를 binary64 하나로 더한 rounded endpoint는 diagnostic이다.
round-trip할 때 delta를 rounded endpoint−baseline로 복구하지 않는다.

baseline+delta에 더해 **event-term ledger**도 보존한다. 예를 들어 J_H−C_H의 합성 delta와 별개로 J_H와 C_H를 원 precision/identity로 각각 저장한다.
source count와 rare RR count의 scale 차이 때문에 C_H를 J_H−(합성 delta)로 역추출하면 own-RR-scale 오차가 커질 수 있다.
새 parent 귀속의 오차를 기존 RR 항의 오차로 잘못 판정하지 않는다. capture number·kinetic·binding·retained photon의 각 원 항을 그대로 결속한다.
RR own-scale 검사는 독립된 원 항/byte identity로 하고, 큰 source-minus-return 차의 역산으로 하지 않는다.
합성 species/energy delta의 평가에는 고정밀 또는 compensated sum을 쓸 수 있지만 원 개별 항은 버리지 않는다.

수치 원장을 검증할 때 거대한 baseline을 denominator로 삼아 tiny source 오류를 숨기지 않는다.
species delta,charge/baryon residual,energy increment는 각각 해당 실제 incremental terms의 scale로 검사한다.
exactzero인 symbolic baryon coefficient는 exact/rational 검사를 먼저 한다.
signed bin active changes는 물리적으로 음수일 수 있으므로 무조건 clipping하지 않는다.
비음수 의무는 source births,capture/retention count,누적 population과 admissible recipient state에 적용한다.

## 12. once-only 소유권과 실제 null

source family,birth partition,source revision alias,proper birth interval을 묶어 birth를 한 번 소비한다.
response observation bin은 source birth interval과 별도 의미다.
새 aggregate return은 기존 RR-only component를 포함한다는 lineage를 기록하고,
같은 recipient에서 두 return이 동시에 적용되면 중복으로 거절한다.
p,d branch/partner는 실제 joint event identity가 오기 전에는 symbolic port다.
synthetic fixture의 event label을 실제 family claim에 등록하지 않는다.

prefix는 diagnostic이라 additive adoption에 사용하지 않는다.
기본 actual adoption 대상은 네 disjoint bins이며 parent birth와 saved response를 각각 한 번 포함한다.
mixed-frame,wrong isotope/charge state,다른 nb/T/ion fraction,source support 확장,다른 proper clock을 거절한다.
한 번 적용할 요소는 source preparation density/729/angle integration,
finite source t²/2,per-baryon1/nb,eV→J뿐이며 각 요소의 owner를 output에 적는다.
절대 V가 없으면 density를1m³ packet으로 암묵 변환하지 않는다.

actual null은 actual s/p/d,He+ residual state,partner energy/history/response,
actual external work/proton depletion,actual full low-source physical native25,
full9600/global native25,absolute worldtube totals와 global completion/error/budget/currency다.
scoped projected w_ext0,retained-photon contribution0,conditional fixture values는 이 null과 다른 필드다.
정보가 없는 항목을0으로 채우는 기본값을 두지 않는다.

## 13. 검증 의무와 결과의 명칭

R1의 rcond1e-6,sensitivity1e-8,holdout2e-12,atom/aggregate2e-11,target-independent1e-9,
native incremental ledger1e-11을 그대로 사용한다.
새 숫자가 나오기 전 'recovery PASS'를 쓰지 않는다.
old517/112/46은 기존 response를 신뢰하는 범위에만 재사용하고 새 attribution/consumer 검사 수에 더하지 않는다.

새 검토자는 다음 연결을 직접 확인할 수 있어야 한다.

1. 고정 input hash→Eq2의3basis→Eq6의positive moments→Eq9–12의identified coefficients.
2. 미사용 moments와 원 Q8/projector→canonical atoms own-scale consistency.
3. finite q=tA→target N/E 및 source residual→saved four-prefix/four-bin response.
4. inclusive He→Eq21–24 affine family→partner guard→null actual point.
5. saved kinetic/RR photon→Eq29–35의별도 literal/branch/partner energy 장부.
6. explicit closure가 있을 때만 Eq36–37 및 two-part native projection.
7. source·return 중복,clock/volume/density double factor와 mixed state를 거절하는 구현.

예산은 새40 CPU-s이며 preparation·worker·coordinator·실패·tails를 포함한다. 이전 잔여 이월0이다.
이 초안은 이후 root의 단계 preflight/게시, 독립 R6, bounded R7 CAS, C4 admission과 실제 C6–C9 결과를 대체하지 않는다.

