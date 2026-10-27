# PHYS02 low-born causal RR: 같은 bath의 baryon 정규화와 유한 시간 source–response

Unit: **CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1**. 이론은 frozen R1 `CONTRACT.md` SHA256 `0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210`에 결속한다. Root가 정한 별도40CPU-s 단위와 네 prefix/네 observation bin을 적용한다. 작성자 `/root/theory_review`는 이 이론과 독립 sparse-exponential reference의 작성자이며 production 비작성자다. 독립 R6 검토자는 `/root/source_qualification`이며 그 역할과 primary-literature 조사 이력은 별도로 기록한다. 이 문서 작성 시점의 scientific worker, 원 source quadrature, 과거 transport/ODE·suite 재실행은 모두0이고, symbolic requests는 준비됐으나 미실행이다.

## 1. 고정된 실제 source와 새 recipient scope

같은 PHYS02 100 K 상태의 저장된 H/He 수밀도로 **조건부 H1/He4-only recipient inventory와 명시적 `n_b`를 새로 구성**할 수 있다. 이 구성은 다른 프로젝트의 bath를 가져오지 않는다. 저장된 source와 같은 상태의 응답으로 **직접 태어난 0.1–10 eV electron cohort의 Coulomb drift + HII/HeII ground RR + cutoff 응답**을 구성한다. 저장된 3200개 low-energy grid와 실제 source column을 그대로 사용하고, 새로 추가한 RR 및 유한 관측창에 필요한 변경만 계산한다.

Root는 이 low-born slice를 다음 대상으로 선택했다. Source 선택은 실제 `direct_0p1_10` birth-tag column으로 한다. **Total source를 `E<=10`으로 잘라 만드는 선택은 사용하지 않는다.** High-born source가 grid의 E=10 경계로 project한 성분이 그 필터에 섞이기 때문이다. 별도40CPU-s inclusive budget과 수용 기준은 R1에 고정됐으며, 개별 worker allocation과 실제 resource admission은 C4에서 확인한다.

고정된 root 계약은 `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`, 별도40CPU-s inclusive preparation/worker/coordinator, actual prefixes `T/4,T/2,3T/4,T` 및 네 disjoint observation bins다. Verner thresholds는 `I_H=13.60eV`, `I_He=24.59eV`, inherited Milne degeneracy parameters는 `d_H=1,d_He=4`, native photon support는 `<=50000eV`로 고정됐다. 하나의 CODATA2022 constants revision을 쓴다. 이 degeneracy d와 isotope mass number A는 별개의 quantity다. Exact provider/source identities와 실제 resource admission은 root R1/C4 기록이 최종 권위를 가진다.

이 선택의 과학적 기여는 actual finite proper-time injection을 source cohort별 finite-age capture와 photon count/energy, native25 RR event return까지 연결하는 것이다. 같은 bath의 `n_b`가 명시되므로 이전의 per-baryon 의존성 하나를 실제로 닫을 수 있다. 기존 10000 K PR107/108 응답을 100 K bath에 붙이지 않는다. 정확한 RR source revision, native support, isotope/state/threshold는 `intake/RR_SOURCE_BINDINGS.json`과 R1에, 실제 source payload는 `inputs/INPUT_MANIFEST.json`에 고정한다.

조사에서 full 100 K G의 실제 raw CSC가 회수되지 않았다는 code-agent 관찰을 유지한다. 저장된 endpoint와 pulse 자료는 그 자료가 실제 제공하는 observable와 시간에서 재사용한다. Fingerprint-only 기록을 복원된 G로 표시하지 않는다.

## 2. 실제 수밀도 근거와 새로운 명시적 inventory

직접 읽은 보존 자료:

1. `research/cr_source_binding_20261012/PHYSICAL_SCALING_CANDIDATE.json`: `fixed_scope`에 같은 100 K 상태의 `n_h=140`, `n_he=1085/94`, `n_e=2849/1880`, `Y_He=31/125`, `xi=1/100`을 정확한 유리수 산술 입력으로 기록한다. 이 파일 자체는 당시 candidate/scalar-arithmetic 근거라는 지위를 유지한다.
2. 같은 unit의 `inputs/source_lineage/sources/research/cr_phys02b_20261010/src/causal_cascade.py`: `N_H=140.`, `N_HE=N_H*.248/(4*(1-.248))`, `N_E=.01*(N_H+N_HE)`, neutral targets `.99*N_H`와 `.99*N_HE`를 정의한다.
3. 보존된 PHYS02A `causal_subthreshold.py`: Coulomb clock의 T=100 K, 같은 electron density, E=0.1–10 eV domain과 `Q_e(W,t)=t A(W)`를 고정한다.
4. 앞 unit `research/cr_proper_injection_20261027/CONTRACT.md`, `THEORY_KO.md`, `implementation/ports.py`: source proper measure, donor/recipient equality, exact native25 quotient, photon 별도 port를 제공한다.

H/He-only 물질 inventory에서 모든 hydrogen nucleus를 H1, 모든 helium nucleus를 He4로 사상한다고 새로 명시한다. 그 inventory의 baryon number density는

\[
n_b=\sum_i A_i n_i=n_{\rm H}+4n_{\rm He}
=140+4\frac{1085}{94}=\frac{8750}{47}\;{\rm m}^{-3}.
\]

따라서 원 source의 표현으로는 `n_b=n_H/(1-Y_He)`이다. H/He ionization stage는 mass number A를 바꾸지 않으므로 같은 원자핵 inventory를 쓴 모든 stage에서 이 합은 같다. Electron과 photon은 이 baryon 합에 들어가지 않는다. 여기서 A는 baryon 수이고, atomic mass를 proton mass로 나눈 근삿값을 넣는 정의가 아니다.

같은 inventory의 ionic targets는

\[
n_{\rm HII}=0.01n_{\rm H}=\frac75\;{\rm m}^{-3},\qquad
n_{\rm HeII}=0.01n_{\rm He}=\frac{217}{1880}\;{\rm m}^{-3},\qquad
n_{\rm HeIII}=0.
\]

`n_e=n_HII+n_HeII=2849/1880 m^-3`와 일치한다. H1/He4 이외의 실제 우주 baryon inventory가 배제됐다는 관측 주장을 만들지 않는다. 이번 recipient의 명시적 model inventory로 한정한다. 원 source가 `n_b`를 직접 제공했다는 주장도 하지 않는다. **PR109의 actual `nb=null` 결과는 원 당시 계약 그대로 보존**하고, 새 inventory manifest와 새 donor/recipient context를 추가한다.

보존 코드의 target density는 binary64 표현식으로 계산됐고 위 기록은 exact decimal/rational semantics를 쓴다. 두 표현을 manifest에서 구분한다. 새 numerical recipient의 실제 density recipe를 고정하고, precision 차이를 맞추려고 retained A/B/source scale을 재정규화하지 않는다. `n_b`는 정규화 분모이며, RR target density는 해당 ion의 수밀도다. 둘을 대체해서는 안 된다.

## 3. proper clock와 density 변수

현재 후보는 prescribed gas-rest scalar frame, 고정 proper volume/density, 고정 bath T와 조성에서 다룬다. `q_i(t)`는 `proper m^-3 proper s^-1`의 number injection이고, `x_i`는 active number density다. `q_i(t)=t A_i`이면 `A_i`의 단위는 `m^-3 s^-2`이다.

원 저장 source는 energy coordinates를 쓴다. 저장한 `B_i`, 원 energy `E_i`, 원 global scale `U_*`와 `T=1e10 s`에 대해

\[
A_i=\frac{U_*}{T^2}\frac{B_i}{E_i},\qquad
A_{\rm cut}=\frac{U_*}{T^2}B_{\rm cutoff\_number}.
\]

Energy source는 같은 scale의 `B_i`와 `B_cutoff_energy`에서 얻는다. Count source와 energy source를 별도로 normalize하지 않는다. 저장 source에 이미 포함된 proper-volume factor, angle integral, target density, source clock을 다시 적용하지 않는다.

원 generator가 dimensionless `u=t/T`에서 `G`이면 physical generator는 `L=G/T`다. 이미 physical `s^-1`로 새 low-chain을 작성했다면 다시 T로 나누지 않는다. `sigma[cm^2]`와 `n[cm^-3]` 같은 provider units는 둘 중 선택한 한 단위계에 한 번만 변환하고 `n_target v sigma`를 구성한다.

Primary electron birth의 neutral-target density와 recipient RR의 ionic-target density는 서로 다른 사건의 인자다. 전자는 이미 A에 들어 있으므로 유지하고, 후자는 새 `lambda=n_ion v sigma`에 한 번 넣는다. 그 구분을 없애서 target density를 두 번 적용하거나, source에 target density가 있었다는 이유로 recipient RR의 실제 target density를 생략해서는 안 된다. 같은 `n_b`로 source를 미리 나눈 뒤 이미 per-baryon인 return을 다시 나누는 중복 정규화도 피한다.

다른 proper volume history를 다루는 확장은 `N_i=V(t)n_i`와 `Q_i=V(t)q_i`의 extensive equation으로 작성할 수 있다. Density equation을 쓰면 volume dilution 항을 명시해야 한다. 이번 고정 bath slice에 새로운 volume history를 암묵적으로 붙일 이유는 없다. 실제 volume 크기가 주어지지 않으면 worldtube 총수·총에너지는 여전히 null이고, proper-volume density 결과는 정의된다.

## 4. causal semigroup 및 관측창 return

행렬의 dimension과 좌표를 다음과 같이 구분한다. `L_act`는3200 active count states의 downward/absorption generator, `A_act`는 그 source vector이며 그 semigroup는 substochastic이다. 이 절에서 n과 실제 active occupancy O에 적용하는 L은 `L_act`다. `L_count`는 cutoff/H-RR/He-RR count absorbers를 더한 column-conservative extension이고, `A_count`에는 active source 및 direct-cutoff source가 들어간다. Uniformization의 stochastic P는 `I+L_count/nu`이고 실제 active-only sweep에는 그 active block `P_act`를 쓴다. Generic semigroup/phi identities는 행렬과 source의 dimension을 맞추면 어느 representation에도 성립하지만, 식(4a),(4c)의 실제 active occupancy에는 active projection을 취한다. Absorber의 누적 occupancy나 mixed-unit energy reward rows를 active n 또는 probability state로 해석하지 않는다.

유한 차원 fixed generator L, integrable source q, 초기 상태 `x(t0)=x0`를 가정하면 variation of constants로

\[
x(t)=e^{L(t-t_0)}x_0+\int_{t_0}^{t}e^{L(t-s)}q(s)\,ds.
\tag{1}
\]

L이 Metzler이고 `x0,q>=0`이면 양의 semigroup가 모든 state의 비음성을 보존한다. Prescribed time-dependent L(t)에서는 `e^{L(t-s)}` 대신 `partial_t U(t,s)=L(t)U(t,s)`, `U(s,s)=I`를 만족하는 ordered propagator U(t,s)를 사용한다. 두 경우 모두 causal dependency는 `s<=t`이다.

Channel c의 event rate를 `j_c(t)=r_c(t)^T x(t)+d_c(t)^T q(t)`라고 쓰자. 직접 absorber injection을 d 항으로 나타낼 수 있다. 초기 상태 0에서 관측창 `[t0,t1]`의 count/energy return은

\[
Y_c[t_0,t_1]
=\int_{s\in H,\,s\le t_1}\left[
\int_{\max(t_0,s)}^{t_1}r_c(t)^T U(t,s)\,dt\right]q(s)\,ds
+\int_{H\cap[t_0,t_1]}d_c(s)^Tq(s)\,ds,
\tag{2}
\]

여기서 H는 실제 기록된 source history domain이다. `max(t0,s)>t1`인 적분은 0이다. 이 식은 주입창과 관측창이 다른 경우의 유효한 Volterra contract다. History 밖 source 값이 unknown이면, 그 부분에 의존하는 전체 physical return도 unknown으로 남는다. `[a,b]`라는 **선택된 birth cohort의 return**은 `[a,b]` 밖 source를 0이라고 선언하지 않고도 정의할 수 있다.

같은 계산을 absorbing ledger `z_c'=j_c`로 구현하면 그 cohort의 관측창 return은 `z_c(t1)-z_c(t0)`다. Active inventory `x(t1)-x(t0)`는 발생한 event count와 같지 않다. 지속 주입 중 cutoff와 RR로 active population이 감소하거나 증가하기 때문이다.

고정 L과 `q(s)=A s`에 대해 전체 `[0,t]` ramp의 state는

\[
x(t)=t^2\varphi_2(tL)A,
\qquad
\varphi_k(Z)=\sum_{m=0}^{\infty}\frac{Z^m}{(m+k)!}.
\tag{3}
\]

선택된 birth window `[a,b]`의 state를 시간 t에서 관찰하자. `m=min(b,t)`, `d=max(m-a,0)`라 두면, `t>=a`에서

\[
x_{[a,b]}(t)=e^{L(t-m)}
\{a d\varphi_1(dL)+d^2\varphi_2(dL)\}A.
\tag{4}
\]

`t<a`이면 0이다. 증명은 (1)에서 `s=a+v`로 바꾸고 상수항과 v항을 각각 적분하면 된다. 식 (4)의 `a d phi1` 항이 source absolute proper-time origin을 보존한다. 각 창 시작에서 `q=A(t-a)`로 source clock을 초기화하면 다른 주입 이력이 된다.

`phi1(0)=1`, `phi2(0)=1/2`이므로 zero-rate와 absorbing zero eigenvalue도 정의된다. Full ledger matrix는 singular일 수 있으므로 `L^-1`이나 `L^-2` 식을 정의 자체로 삼지 않는다. Scalar numerical implementation에서는 small argument의 cancellation을 `expm1`/entire-series 등으로 처리해야 한다. 이 intake에서는 함수를 실행하지 않았다.

### 실제 finite occupancy와 endpoint channel rate

실제 source history와 propagator가 정해졌으므로 integrated occupancy는

\[
O_j(t)=\int_0^t n_j(s)ds,
\qquad O(t)=t^3\varphi_3(tL)A,
\qquad [O_j]={\rm m}^{-3}{\rm s}.
\tag{4a}
\]

Active-state entries를 선택해서 반환한다. Constant channel rates에 대해

\[
C_c(t)=\sum_j\lambda_{c,j}O_j(t),\qquad
\dot C_c(t)=\sum_j\lambda_{c,j}n_j(t).
\tag{4b}
\]

이 exposure는 실제 finite history에서 얻은 population-time integral이며 conditional mean lifetime을 대입한 값이 아니다. Per-baryon occupancy가 필요하면 같은 고정 `n_b`로 나눈다. `lambda`에 target density가 이미 들어 있으므로 event conversion에서 target density를 다시 곱하지 않는다.

Per-state H capture `C_H,j=lambda_H,j O_j`가 실제로 저장되고 `lambda_H,j>0`이면 `O_j=C_H,j/lambda_H,j`도 같은 식이다. **집계된 C_H 전체를 한 bin의 lambda_H,j로 나누는 식은 성립하지 않는다.** Direct positive occupancy reward가 이 division을 피한다.

Observation bin `[a,a+h]`는 이전 active state `n(a)`를 유지하여

\[
O_{[a,a+h]}=h\varphi_1(hL)n(a)
+a h^2\varphi_2(hL)A+h^3\varphi_3(hL)A
\tag{4c}
\]

로 쓸 수 있다. `O(a+h)-O(a)`와 같지만 first-half-born population과 absolute source clock을 직접 드러낸다. Zero-rate limit에서는 `O(t)=A t^3/6`이다. Endpoint rates는 해당 prefix의 actual active state에서 평가하고, cumulative return을 단순히 elapsed time으로 나눈 평균을 endpoint rate라고 표시하지 않는다.

## 5. 새 low-born Coulomb + RR chain의 구체식

보존 low grid를 `E_1<...<E_3200=10eV`, cutoff를 `E_0=0.1eV`라 한다. 원 Coulomb stopping law를 `b_j=b_C(E_j)>0` eV/s라 두고,

\[
d_j=\frac{b_j}{E_j-E_{j-1}},\quad
\lambda_{{\rm H},j}=n_{\rm HII}v_j\sigma_{{\rm H},1s}(E_j),\quad
\lambda_{{\rm He},j}=n_{\rm HeII}v_j\sigma_{{\rm He},g}(E_j)
\tag{5}
\]

로 정의한다. Ground state의 provider label, native thresholds `I_H=13.60eV,I_He=24.59eV`, cross-section revision과 recoil/angular convention은 R1 및 `intake/RR_SOURCE_BINDINGS.json`에 pin했다. H1/He4 mapping을 승인된 mapping으로 검사한다. 현 bath에서는 `n_HeIII=0`이므로 HeIII ground RR hazard는 0이다.

Count-coordinate active equation은

\[
\dot n_j=-(d_j+\lambda_{{\rm H},j}+\lambda_{{\rm He},j})n_j
+d_{j+1}n_{j+1}+t A_j,
\tag{6}
\]

상단 `j=3200`에서는 influx term을 생략한다. 원 source projection의 직접 cutoff atom은 그대로 cutoff port에 들어가고, absorbing cutoff policy하에서는 그 atom에 active RR hazard를 부여하지 않는다. 이 정책은 cutoff 아래 에너지의 RR가 전체 물리에서 사라진다는 주장과 구분한다.

필요한 nonnegative ledgers는

\[
\begin{aligned}
\dot N_{\rm cut}&=d_1n_1+tA_{\rm cut},\\
\dot U_{\rm cut}&=E_0d_1n_1+tA_{\rm cut,E},\\
\dot Q_C&=\sum_j b_jn_j,\\
\dot N_c&=\sum_j\lambda_{c,j}n_j,\\
\dot K_c&=\sum_j E_j\lambda_{c,j}n_j,\\
\dot U_{\gamma,c}&=\dot K_c+I_c\dot N_c.
\end{aligned}
\tag{7}
\]

원 saved direct-cutoff energy를 사용하며, 저장된 energy/count가 서로 다른 representation이면 임의로 `E0*N`으로 바꾸지 않는다. 위 `E0` 배수는 grid의 실제 `E1->E0` drift event에만 적용했다.

`b_C`는 보존 PHYS02B `stopping_eV_s(E,quantum_constant=0)`의 정확한 prescription을 pin한다. 이 코드는 classical/quantum Coulomb-log 중 작은 값을 선택한다. 온도나 coefficient를 비슷한 다른 donor 모델에서 다시 고르지 않는다.

새 recipient가 CODATA2022 constants를 명시적으로 쓰는 것과 historical G의 floating coefficients가 bitwise 동일하다는 주장은 구분한다. Historical scipy.constants revision이 다르거나 확인되지 않으면, 새 recipient를 같은 stopping law와 새로 고정한 constants의 조합으로 기록한다. Retained B/U*는 그대로 유지하고, 그 changed dependency를 무시한 old-endpoint parity를 요구하지 않는다.

초기 active/ledger가 0일 때 source cohort별로

\[
N_{\rm inj}=N_{\rm active}+N_{\rm cut}+N_{\rm H}+N_{\rm He},
\tag{8}
\]

\[
U_{\rm inj}=U_{\rm active}+Q_C+U_{\rm cut}+K_{\rm H}+K_{\rm He}
\tag{9}
\]

가 성립한다. (8)은 (6)의 합에서 adjacent drift terms가 telescope되어 나오고, (9)는 (6)에 `E_j`를 곱한 합에서 `d_j(E_j-E_{j-1})=b_j`를 쓰면 나온다. Chemical binding-energy change는

\[
\Delta U_{\rm ion}=-I_{\rm H}N_{\rm H}-I_{\rm He}N_{\rm He}.
\]

따라서 photon을 포함한 동일 event energy identity는

\[
U_{\rm inj}=U_{\rm active}+Q_C+U_{\rm cut}
+U_{\gamma,\rm H}+U_{\gamma,\rm He}+\Delta U_{\rm ion}.
\tag{10}
\]

`K_c`와 `U_gamma,c`는 같은 event의 서로 다른 accounting projection이다. 두 값을 독립 에너지 sink로 더하면 중복 집계가 된다. `Q_C`, cutoff energy와 retained-photon energy도 각각의 port 소유권을 유지한다.

## 6. native25와 retained photon return

새 explicit inventory의 `n_b`가 donor와 recipient에서 같은 physical state/frame에 속하고, 각 return이 같은 source/cohort/history/support에서 나온 경우에만 per-baryon projection을 수행한다. RR event return의 stoichiometry는

\[
\Delta n_{\rm HI}=N_{\rm H},\quad \Delta n_{\rm HII}=-N_{\rm H},\quad
\Delta n_{\rm HeI}=N_{\rm He},\quad\Delta n_{\rm HeII}=-N_{\rm He},
\]

\[
\Delta n_{\rm fast}=-(N_{\rm H}+N_{\rm He}),\quad
\Delta w_{\rm nt}=-(K_{\rm H}+K_{\rm He})\,eV_J/n_b,
\quad\Delta w_{\rm ext}=0.
\tag{11}
\]

Heavy species와 fast-electron count는 각 density delta를 `n_b`로 나눈다. 원 native species order에서 H1I/H1II/He4I/He4II의 indices를 authoritative contract와 대조한다. `Delta logT=0`은 frozen-T diagnostic convention이며 coupled thermal response의 완료를 뜻하지 않는다. 이 return은 source injection 및 cutoff transfer와 별도이다.

Source+transport의 net active inventory를 별도로 표시한다면 `zeta_active=N_active/n_b`, `w_nt_active=U_active*eV_J/n_b`이다. Total injected number를 현 active number로 쓰지 않는다. RR return delta만 initial fast stock 0에 적용해서 음의 population을 만들면 source/response ordering이 잘못된 것이다. Port는 통합 ledger와 cohort ownership을 제공하며 실제 coupled state update는 recipient가 전체 source/cutoff/return을 함께 적용하는 계약을 요구한다.

### Charge-derived electron abundance와 thermal subset

Legacy native25에서는 species charge vector를 q라 할 때 전체 free-electron abundance가 `x_e=q^T Y`이고, `zeta`는 그 안의 nonthermal subset이다. 따라서 thermal subset은

\[
x_{e,\rm th}=q^TY-\zeta.
\tag{11a}
\]

새 conditional H1/He4 inventory의 nominal initial charge abundance는 `x_e=407/50000`이다. 이것은 위 같은-state `n_e/n_b`와 같다. Charge state별 누락 성분을 임의로 0으로 채워서 다른 source의 초기 상태를 만드는 규칙이 아니다.

RR count `Ncap=N_H+N_He`에 대해

\[
q^T\Delta Y=-N_{\rm cap}/n_b,\qquad
\Delta\zeta=-N_{\rm cap}/n_b,\qquad
\Delta x_{e,\rm th}=0.
\tag{11b}
\]

즉 fast electron이 이온에 붙는 이번 RR event는 thermal-electron population을 제거하지 않는다. Ion이 neutral로 바뀌어도 heavy-particle translational count는 하나로 유지된다. Zero-recoil/spontaneous photon bookkeeping에서는 captured kinetic/binding energy가 photon port로 가며 thermal heating 항이 생기지 않는다.

Cutoff transition은 별도이다. **Cutoff에 도달한 electron이 thermal bath에 편입된다는 명시적 closure**를 선택한 경우,

\[
\Delta Y=0,\qquad \Delta\zeta=-N_{\rm cut}/n_b,\qquad
\Delta x_{e,\rm th}=N_{\rm cut}/n_b.
\tag{11c}
\]

Source injection은 parent-ion chemistry가 미제공이면 전체 native25 chemical vector가 결정되지 않는다. 예를 들어 `DeltaY=0`을 임의로 놓고 `Delta zeta=+Ninj/nb`만 적용하면 식(11a)가 `Delta x_e,th=−Ninj/nb`를 강제한다. 이는 실제 외부 electron source의 charge balance를 나타내지 않는다. 최소 추가 정보는 charge/parent-ion source 또는 명시적인 boundary-current/charged-state closure이고, 완전한 native21 vector에는 species별 daughter ledger가 필요하다.

따라서 이번 단위가 반환하는 **RR-only native25 event delta**와 `Nactive/nb`, `Uactive/nb` **net nonthermal diagnostics**를 구분한다. 후자는 원 source의 parent chemistry를 보충한 닫힌 native25 source state가 아니다. Source-native25 chemistry가 미제공이면 해당 전체 source projection을 null로 유지하고, 실제 finite count/energy diagnostics는 그대로 제공할 수 있다.

### Cutoff thermal bookkeeping의 조건부 식

이미 charge-consistent recipient가 주어지고, 고정 volume의 monatomic translational bath, 공통 T, 실제 cutoff energy의 thermal 편입을 선택했다고 가정하자. Initial thermal heat capacity를 `Cv0=(3/2)k_B(n_heavy,0+n_e,th,0)`로 두면 source와 RR를 포함한 전체 gas history를 새로 만들어내지 않고도 cutoff/Coulomb contribution에 대한 local energy relation을 쓸 수 있다:

\[
[C_{V0}+\tfrac32 k_BN_{\rm cut}]T_{\rm new}
=C_{V0}T_0+Q_C+U_{\rm cut},
\]

\[
\Delta T_{\rm join}
=\frac{Q_C+U_{\rm cut}-\tfrac32k_BT_0N_{\rm cut}}
{C_{V0}+\tfrac32 k_BN_{\rm cut}}.
\tag{11d}
\]

여기서 energy는 J 단위로 변환한다. Corresponding differential identity는

\[
C_V(t)\dot T=P_C+P_{\rm cut}-\tfrac32 k_BT\dot N_{\rm cut}.
\tag{11e}
\]

추가 thermal particle의 heat-capacity term을 생략한 `Q/Cv`와 식(11d)는 다르다. 이번 frozen-coefficient source-response 계산은 이 식에 들어갈 caloric/cutoff port를 제공할 수 있다. 실제 aggregate source의 전체 parent chemistry 및 receiver state가 없으면 coupled temperature history는 null이고 native return의 `Delta logT=0` diagnostic을 물리적 thermal completion으로 바꾸지 않는다. 과거 source-binding의 cutoff-join candidate 식은 같은 조건에서 재사용한다.

원 source_vectors는 HI/HeI primary birth species가 합쳐진 electron input이다. 그것만으로 primary proton event의 ion-daughter 분할을 만들지 않는다. 위 RR chemical return은 새 recipient의 실제 RR channel count로 결정된다. 저장 cascade의 secondary-ionization counters가 따로 존재하면 해당 recipient 이벤트에만 사용할 수 있고, primary birth의 chemical ledger로 바꾸지 않는다.

Baryon-changing injection을 확장할 때는 단순 나눗셈 대신 이미 유도된 exact finite quotient

\[
\Delta y_i=\frac{\Delta n_i-y_i\Delta n_b}{n_b+\Delta n_b}
\tag{12}
\]

를 쓴다. 정의역은 `nb>0`, `nb+Delta nb>0`이며, 실제 removal을 적용한 최종 species/count densities도 비음성이어야 한다. 이번 electron injection/RR는 `Delta nb=0`이다.

식(12)의 y는 number density 또는 energy density를 nb로 나눈 좌표다. Energy coordinate이면 같은 식의 n을 해당 energy density로 읽는다. `logT`는 별도 intensive coordinate이며 nb로 나누지 않고 frozen-temperature convention을 따로 적용한다.

Photon count와 energy는 `N_gamma,c=N_c`, `U_gamma,c=K_c+I_cN_c`인 별도 retained-radiation port다. 이 모델의 retention convention을 명시하며 photon absorption/escape 또는 receiver heating을 실행한 것으로 표시하지 않는다. 실제 per-energy RR event measure를 계산·반환한다면 `E_gamma=E_j+I_c`의 discrete emission atoms는 그 event model에서 직접 나온다. Moment-only 결과에서 spectrum이나 time history를 역으로 만들어서는 안 된다.

## 7. RR-only frozen-energy 대안의 의미와 정량 의무

Drift를 생략하고 한 energy에 constant RR rate `lambda>=0`만 둔 모델은 정확히 풀 수 있다. `q(t)=At`, zero initial state에서

\[
n(T)=AT^2\varphi_2(-\lambda T),\qquad
N_{\rm RR}(T)=AT^2[1/2-\varphi_2(-\lambda T)].
\tag{13}
\]

`lambda=0`이면 `n=AT^2/2`, capture=0이다. 이 해는 **frozen-energy RR-only model의 정확한 결과**로 사용할 수 있다. 실제 low-energy Coulomb drift가 존재하는 PHYS02 transport와의 오차를 결정하려면 omitted operator의 크기나 적합한 검증 근거가 필요하다.

구체적으로 full candidate operator가 `L=L0+DeltaL`이고, 선택한 같은 norm에서 두 propagator가 contraction이며 bounded `DeltaL`를 알면

\[
e^{Lt}-e^{L_0t}=\int_0^te^{L(t-s)}\Delta L e^{L_0s}\,ds,
\quad
\|x(T)-x_0(T)\|\le\|\Delta L\|\int_0^T(T-s)\|q(s)\|ds.
\tag{14}
\]

Ramp `q=sA`이면 우변은 `||DeltaL|| ||A|| T^3/6`이다. 이 bound는 적합한 norm/contractivity와 omitted-rate bound를 실제로 확인했을 때만 수치 error budget에 쓴다. RR-only result 자체는 그 정보를 제공하지 않는다. Omitted energy loss가 RR cross-section을 바꿀 수 있어 blanket upper/lower-bound 방향도 가정 없이 결정하지 않는다.

권고하는 drift+RR slice는 이 frozen-energy 누락을 직접 해소한다. 다만 neutral elastic transfer, photon reabsorption/escape, bath depletion/thermal feedback, stimulated/excited-state channels, cutoff 아래 response 등은 정해진 frozen model 밖에 남는다. 원 Coulomb leading-log closure의 physical error 지위를 재사용하며 새 arithmetic/solver residual을 그 오차로 바꾸지 않는다.

## 8. response evidence가 허용하는 사용 범위

| 실제 공급된 근거 | 바로 정의되는 quantity | 추가 입력이 필요한 quantity |
|---|---|---|
| Source A/B와 finite proper history | finite injected N/E와 source rates | recipient return |
| 동일 source의 실제 saved ramp endpoint | 그 정확한 source/time의 state·ledger | 임의 window/새 history의 전체 response |
| 실제 saved pulse response at specified ages | 저장된 ages에서의 해당 pulse observable | ages 사이 continuous interpolation의 오차 |
| Same-state full G 또는 qualified propagator | fixed model의 causal convolution | model 밖 bath/energy/isotope extension |
| Eventual yield 또는 conditional mean lag | 그 정의의 integrated/asymptotic moment | finite-window RR event history |
| Finite RR count/kinetic moments | native RR stoichiometry와 photon moments | photon spectrum/time history가 미제공이면 null |

이 표는 필요한 다음 입력을 고르는 데 사용한다. 비가용 자료를 일반적인 불가능성 주장으로 확대하지 않는다. 저장된 100 K endpoint로 normalization/selected ledger adapter를 만드는 slice도 가능하지만, low-born drift+RR 후보가 허용되면 actual finite return을 추가하는 더 직접적인 다음 단위다.

## 9. 최소 changed verification 제안

R1/C3가 고정하는 항목은 low-born source tag·history·observation windows, exact grid/source/code hashes, donor/recipient inventory, RR cross-section revision/native support, approximation conventions, units와 scalar tolerances, coordinator를 포함한 별도 CPU/RAM budget이다.

필요한 검증은 다음 changed dependency에 집중할 수 있다.

- 원 source A/B/cutoff atom 및 common scale 재사용 identity; high-born low-cross diagnostic의 source 중복 거절.
- Zero RR / zero source / zero-width / zero-age limits와 positive off-diagonal structure.
- Source absolute-time origin을 보존한 full vs split birth-window additivity.
- 독립 small-chain analytic/Volterra reference와 finite-window return 비교.
- Count identity (8), kinetic identity (9), photon+binding identity (10), baryon sum 및 RR channel stoichiometry.
- Native25 exact quotient·same-state inventory·event-family ownership과 retained photons의 별도 port.
- 실제 saved low-born result를 쓰는 경우 그 endpoint에만 oracle 범위를 고정; 기존 전체 generator/quadrature/ODE를 다시 실행하지 않는다.

수치 허용치는 아래와 R1에 고정한다. 실제 runtime success와 독립 R6 verdict는 각 실행·검토 영수증에 기록한다. `SYMBOLIC_REQUESTS.json`의 최대3개·각8s 제한 요청은 changed algebra만 대상으로 하며 root가 R7에서 dispatch한다. 작성 시점의 Wolfram execution은0이다.

### 추가 구체화: positive uniformization

Implementation agent가 제안한 count-coordinate chain에서는 active states와 cutoff/H-RR/He-RR count absorbers를 함께 두어 column-conservative L을 만든다. `nu>=max_j(d_j+lambda_Hj+lambda_Hej)`이면 `P=I+L/nu`는 nonnegative column-stochastic matrix다. `x=nu*T`에 대해 ramp source의 최종 상태는

\[
y(T)=T^2\sum_{k\ge0}w_k(x)P^kA,\qquad
w_k(x)=\int_0^1(1-v)e^{-xv}\frac{(xv)^k}{k!}\,dv
=x^{-2}\sum_{n\ge k+2}(n-k-1)p_n(x),
\tag{15}
\]

`p_n(x)=exp(-x)x^n/n!`이다. Poisson series를 `n<=M`에서 끊은 positive weights를 `w_k^(M)`이라 쓰면

식(15)의 series identity는 `exp(-xv)=exp(-x)sum_l[x(1-v)]^l/l!`를 integrand에 넣어 직접 얻는다. 모든 항이 nonnegative여서 합과 적분을 교환할 수 있다. Beta integral `integral_0^1 v^k(1-v)^(l+1)dv=k!(l+1)!/(k+l+2)!`를 쓰고 `n=k+l+2`로 바꾸면 정확히 `x^-2 sum_{n>=k+2}(n-k-1)p_n(x)`가 된다. 수렴이나 positivity를 새로운 물리 가정으로 추가하지 않는다.

\[
\sum_{k=0}^{M-2}w_k^{(M)}(x)
=\frac1{x^2}\sum_{n=2}^{M}\frac{n(n-1)}2 p_n(x)
=\tfrac12\Pr\{\mathrm{Pois}(x)\le M-2\}.
\tag{16}
\]

따라서 `N_inj=(T^2/2)sum A`인 count-state의 missing mass는 `N_inj*Pr{Pois(x)>=M-1}`다. 각 particle의 total kinetic reward가 `Emax` 이하, RR photon reward가 `Emax+Ic` 이하인 해당 모델에서는 같은 missing particle mass로 observable별 absolute tail bound를 얻는다. Exact weights의 k만 잘라내는 방식과, 이 식처럼 Poisson n series도 truncate한 방식은 구분해야 한다. Total output을 다시 normalize하면 이 truncation accounting이 바뀌므로 그대로 보존한다.

식 (15)–(16)은 새 numerical campaign 없이 직접 대조한 해석적 식이다. 실제 coefficient/stiffness, 선택 M, float summation error, Poisson-tail 계산의 rounding 및 CPU는 새 admission에서 검증한다. 수학적인 positive truncation bound를 binary64 outward interval certificate로 자동 승격하지 않는다. `x=0`은 별도 exact ramp limit으로 처리한다.

이 P의 column-stochastic 성질은 active+count absorber state에 대한 것이다. Energy-reward rows까지 붙인 augmented matrix는 같은 probability column sum을 갖지 않아도 된다. 그 energy bound는 underlying count chain의 각 path에서 누적 kinetic reward가 Emax 이하이고, 한 electron의 capture는 한 channel에서 한 번이라는 사실로 따로 얻는다.

### Occupancy와 tiny RR에 맞춘 positive tail

Occupancy에는 다음 positive weights를 쓸 수 있다:

\[
O(t)=t^3\sum_{k\ge0}v_k(x)P^k A,\qquad
v_k(x)=x^{-3}\sum_{n\ge k+3}\binom{n-k-1}{2}p_n(x),
\quad x=\nu t.
\tag{16a}
\]

이는 `phi3`의 integral representation `1/2 integral_0^1 (1-v)^2 exp(xv(P-I))dv`를 식(15)와 같은 nonnegative series/Beta integral로 전개한 결과다. Finite-n truncation `n<=M`이면

\[
\sum_{k=0}^{M-3}v_k^{(M)}
=\tfrac16\Pr\{\mathrm{Pois}(x)\le M-3\},\qquad
\sum_{k=l+1}^{M-2}w_k^{(M)}=xv_l^{(M)}.
\tag{16b}
\]

두 번째 식은 coefficients의 finite triangular sum에서 나온다. 따라서 같은 M을 쓰면 count absorber로 얻은 truncated capture와 `lambda`를 occupancy에 곱한 capture가 exact arithmetic에서 서로 일치한다. Occupancy weights는 ramp weights의 추가 backward cumulative sum으로도 얻을 수 있다.

Active source coefficient의 scalar 합을 `S_A=sum_j A_j`, `N_inj,act=S_A*t^2/2`라고 두자. 벡터 `A_act`와 이 scalar 합을 구분한다. Direct cutoff birth는 RR에 기여하지 않는다. Channel c의 최대 active hazard를 `lambda_c,max`라 하면 `k`개의 uniformization step 안에서 해당 channel로 capture될 확률은 `min(1,k lambda_c,max/nu)` 이하이다. 따라서 missing channel count는

\[
\epsilon_c\le\min\left\{
N_{\rm inj,act}\Pr[N\ge M-1],\quad
\frac{S_A\lambda_{c,\max}t^3}{6}\Pr[N\ge M-2]
\right\},\quad N\sim\mathrm{Pois}(\nu t).
\tag{16c}
\]

두 번째 항의 지수는 다음 합으로 독립 대조했다:

\[
\sum_{k=0}^{n-2}k(n-k-1)=\frac{n(n-1)(n-2)}6,
\qquad n(n-1)(n-2)p_n(x)=x^3p_{n-3}(x).
\]

Omitted n은 `n>=M+1`이므로 shift 후 tail은 `Pr[N>=M-2]`이다. Count bound의 `M-1`과 한 단계 차이 난다. 이 bound는 active source, zero initial RR absorbers, irreversible capture, column-conservative underlying P라는 이번 chain의 조건에서 성립한다. Equivalent occupancy bound는 `sum_active DeltaO_j <= S_A*t^3/6*Pr[N>=M-2]`다.

Capture kinetic-energy error에는 `Emax*epsilon_c`, photon-energy error에는 `(Emax+I_c)*epsilon_c`를 사용할 수 있다. Endpoint rate의 absolute tail은 `lambda_c,max`에 해당 active count-tail bound를 곱해 얻는다. Positive exact-arithmetic partial capture `C_c^(M)>0`를 기준으로 `epsilon_c<=eta*C_c^(M)`이면 full capture에 대한 truncation relative error도 eta 이하이다. 실제 floating result를 certificate lower bound라고 부르려면 rounding bound가 별도로 필요하다. `lambda_c,max=0`은 exact-zero channel이며, computed capture0인데 nonzero tail이 남는 경우에는 absolute enclosure로 보고한다.

Root가 정한 새 acceptance 방향은 relative count/energy closure `1e-11`, positive capture/reference `1e-9`, source/photon ledger consistency `1e-11`이다. Analytical truncation allocation은 channel capture의 `1e-12` 이하, injection count/energy의 `1e-13` 이하이며 ordinary FP roundoff는 별도이다. Energy tail allocation은 `Emax*missing_count`를 실제 injected energy와 비교하여 확인한다. Count tail ratio만 energy ratio라고 이름 붙이지 않는다. 네 observation bins에는 식(17)로 두 endpoint tail을 전파한다.

문헌의 normalized truncated Poisson weights를 사용할 때는 주의가 필요하다. 식(16)은 **정규화하지 않은 실제 p_n**의 finite-n truncation이다. Centered/scaled weights를 계산한 뒤 truncated sum으로 다시 정규화하면 원 Poisson mass와 달라진다. Scaled anchor나 normalization의 오차를 따로 bound하거나, 계산한 weights를 실제 p_n normalization으로 되돌리는 근거가 필요하다. Source-qualification agent의 Fox–Glynn/Al-Mohy–Higham primary 조사는 이 구현 의무에 연결된다.

Finite emission-bin 결과를 endpoint prefixes의 차로 계산할 때도 tail을 전파한다. `R_i`가 nonnegative cumulative count 또는 energy reward이고 `Rhat_i<=R_i<=Rhat_i+eps_i`라면

\[
R_1-R_0\in
[\widehat R_1-\widehat R_0-\epsilon_0,
 \widehat R_1-\widehat R_0+\epsilon_1].
\tag{17}
\]

Physical nonnegative bin과 교집합을 취할 수 있다. 두 prefix를 빼면 positive lower approximation이라는 성질이 자동 보존되지 않는다. Floating-point subtraction/summation error는 여기에 별도로 포함한다. Very thin observation bins를 택하면 cancellation이 실제 판별 위험이 되므로 해당 창의 acceptance는 직접 bin formulation 또는 전파된 absolute bound로 정한다.

### 추가 구체화: birth 창과 emission 창의 event ownership

입력 source claim은 family와 native birth support/time에 결속하고 한 번만 소유한다. 유한 RR return의 claim에는 그 birth cohort와 별도로 **observation/emission time bin**이 필요하다. 같은 `[0,T]` source에서 나온 `[0,T/2)`와 `[T/2,T]` emission returns는 서로 다른 event sets이므로 합할 수 있다. 반대로 cumulative prefixes `R(T/2)`와 `R(T)`는 겹치므로 diagnostic/nonadditive로 표시한다.

일반 registry의 overlap 판단은 같은 family/channel에서 native birth partition, birth-time partition, emission-time bin이 모두 겹치는지를 본다. 이번 slice가 전체 birth history 하나를 고정하면 birth-time field는 고정된 identity로 유지하면 된다. `R(T)-R(T/2)`에는 first-half-born surviving electrons의 second-half capture도 들어가므로 midpoint에서 빈 상태로 재시작하는 식으로 계산하면 안 된다. Drift 이후 current energy 또는 photon emission energy를 native birth support로 대체하지 않는다. Source history 밖의 주입을 가정하지 않으면서 이미 고정한 source cohort의 지연 return을 나타낼 수 있다.

## 10. SciSpace·Exa·primary 대조

2026-10-27에 SciSpace와 Exa로 primary literature를 새로 조사했고, 원 arXiv records를 직접 읽었다. 전체 입력·응답은 `LITERATURE_RAW.json`에 보존했다.

- Furlanetto–Stoever, *Secondary ionization and heating by fast electrons*, arXiv:0910.4410; MNRAS 404 (2010), 1869–1878, DOI10.1111/j.1365-2966.2010.16401.x. 원 abstract는 electron-electron heating, H/He ionization 및 excitation/secondary photons를 구별하고 energy/ionization-state dependence를 명시한다. 이 literature는 channel 구분의 배경으로 사용한다. 해당 연구의 E>10eV 또는 terminal deposition convention을 이번 0.1–10eV finite-time model에 들여오지 않는다. https://arxiv.org/abs/0910.4410
- Liu–Ridgway–Slatyer, *DarkHistory*, arXiv:1904.09296; Phys.Rev.D101,023530(2020). 원 abstract는 source cooling과 thermal/ionization history의 backreaction을 함께 다루는 framework를 명시한다. 이번 fixed-bath response와 coupled-history response를 구별하는 conceptual reference로 재사용한다. 그 cosmological density, temperature, spectrum, transfer tables는 입력하지 않는다. https://arxiv.org/abs/1904.09296

SciSpace는 같은 FS10 preprint를 2022 repository entry로도 반환했다. 원 arXiv submission은2009-10-23이고 journal publication은2010이므로 그 실제 서지를 채택했다. Primary journal URL의 직접 fetch는 inaccessible redirect 오류였고, 해당 실패를 보존했으며 직접 읽은 arXiv 원문 record로 abstract claims를 대조했다. 새 scattering values나 measured rates를 이 검색에서 채택하지 않았다.

## 11. 운영·근거 기록

요청된 main skill `skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop`의 1.0.0 본문을 읽었다. 해당 user URI에서 세 reference의 direct read가 실패하여, 같은1.0.0 설치본 `e1/skill-6aa0657100b08191b7d67482d1f97c1d`의 RESEARCH_POLICY, THEORY_LOOP, EVIDENCE_AND_HANDOFF를 읽어 적용했다. 이 접근 문제는 연구 중단이나 추가 승인 요구로 사용하지 않았다.

Old proper-injection20/20, scoped1/1, central27/88 effect0, old C9/lease/failure, 새 proper-unit10.238419/20 및 두 runtime failures의 기록을 그대로 유지한다. 다음 unit의 budget은 별도이고 잔여를 이월하지 않는다. Source/code/provider current HEAD survey는 root와 해당 담당 agent가 수행하며 이 문서는 새로운 provider 완료 수나 physical closure를 선포하지 않는다. 개인 대화 전체 검색 unavailable, Drive partial inventory 한계도 유지한다.


## 12. 최종 코드 인계와 원전 연결

구현 계약은 `THEORY_TO_CODE_KO.md`, 제한 symbolic 입력은 `SYMBOLIC_REQUESTS.json`, 독립 reference는 `review/independent_reference.py`에 둔다. 이론 작성자가 reference도 작성했음을 유지하고 production modules를 import하지 않는다. Actual source는 PR109 `ACTUAL_SOURCE_RECORDS.json` SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`의 `direct_0p1_10` record다. Total-source energy filter는 사용하지 않는다.

Algorithm-primary qualification은 source-qualification reviewer의 unit-relative `literature/LITERATURE_SUPPORT_KO.md`와 `literature/PRIMARY_READMAP.json`을 따른다. Al-Mohy–Higham2011, DOI10.1137/100788860, §2 Theorem2.1의 polynomial-forcing/augmented exponential identity를 적용한다. Fox–Glynn1988, DOI10.1145/42404.42409, Prop1의 normalized truncated expectation bound와 이번 absolute Poisson-mass truncation을 구분한다. 식(15)–(16c)는 위에 제시한 직접 유도이며 그 논문에 동일식이 실렸다고 주장하지 않는다. 두 원전의 floating-point 분석도 이번 코드의 자동 outward enclosure가 아니다.
