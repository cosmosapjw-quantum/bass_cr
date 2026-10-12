# 실제 전자 birth source와 M0 응답의 정규화 결속

작성 역할: **후보 수학 유도 및 원문·코드 계보 분석자**. 이 문서는 최종 decision review가 아니다. GPT-6 Astra v4.0.0 research core를 읽고 적용했다. 원문 기준 commit은 `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`다. 저장된 scalar의 정확 분수 산술 1회 외에 source quadrature, generator, transport, pulse, resolvent, F/H, 과거 suite는 실행하지 않았다. 모든 인용 식별자의 Git 경로·blob SHA1·SHA256·읽은 범위는 `SOURCE_INVENTORY.json`에 있다.

## 1. 이번에 닫힌 연결

**기존 M0 응답은 실제로 저장된 PHYS02의 `Q_e(W,t)=t A(W)`에 물리 단위로 연결할 수 있다.** 대응하는 스칼라 source는 양성자 주입률 자체나 PHYS01의 FS10 terminal heat가 아니다. `0.1≤W≤900 eV`에서 직접 태어난 전자의 에너지 주입률이다. 실제 9600 실행에서 저장된 공통 진폭은

\[
T_0=10^{10}\ {\rm s},\qquad
U_*=T_0^2 A_{E,\rm sel}
=1.1242596728743301\times10^{-13}\ {\rm eV\,m^{-3}},
\]

\[
q_*=\frac{\epsilon_{\rm eV}U_*}{T_0}
=1.8012625784277353\times10^{-42}\ {\rm J\,m^{-3}\,s^{-1}},
\qquad \epsilon_{\rm eV}=1.602176634\times10^{-19}\ {\rm J/eV}.
\]

M0의 원래 정규화를 유지하면 해당 source의 관측 시각 가열률과 누적 열은

\[
\boxed{\mathcal P_h(T_0)=q_*H_0R},\qquad
\boxed{\mathcal E_h(T_0)=\frac{q_*T_0}{2}H_0S}.
\tag{1}
\]

새로운 kernel을 실행할 필요가 없다. 이 SI 변환은 원래 E 실행의 `SI_J1`, `SI_J2` 변환과 일치한다. M0의 기록된 소수들을 정확한 분수로 취급한 값과 옛 FP64 출력 사이의 마지막 자리 차이는 표현과 반올림의 차이이며 물리 오차 상계가 아니다. [B, ELAUNCH, E_FULL, E_LEGACY, CACH]

성립 범위는 동일한 직접 전자 source, 고정 bath, `xi=0.01`, 선택 birth 에너지 창, 같은 두 birth 열과 같은 유한 cascade 모형이다. PHYS01의 정확 Bianchi 수송을 거친 최종 proton population, FS10 terminal closure, native receiver의 `xi=0.1` knot 및 전체 우주론 이력을 이 결과와 동일시하지 않는다. 이 제한은 사용할 수 있는 응답을 막는 결손이 아니라 이번에 실제로 결속한 물리 문제의 정의다.

## 2. 양성자 주입에서 A(W)까지

### 2.1 단위와 원래 정규화

양성자 주입률을

\[
q_p(K)=\frac{dN_p}{dV_{\rm proper}\,dt\,dK}
\quad[\mathrm{m^{-3}s^{-1}eV^{-1}}]
\]

로 쓴다. `InjectionModel.q_proper_m3_s_eV`는 이미 각도 적분된 source다. 등방 birth의 각도 측도 `dμ/2`는 별도로 사용되므로 여기에 `4π`를 추가하지 않는다. 스펙트럼은

\[
q_p(K)=\mathcal N\,\beta(K)^{-1}
\left[\frac{p(K)}{p(K_0)}\right]^{-\alpha},\qquad
K_0=1\ {\rm GeV},\quad\alpha=2.2,
\]

이며 `10 keV–1 PeV` 전체 source 에너지 적분으로 정규화한다. `1–4 MeV`는 이후 충돌 계산에서 사용하는 부분 창이다. 그 창을 전체 CR power로 다시 정규화하면 원 source가 바뀐다. `(1+z)^3`의 comoving-to-proper 변환도 source 안에서 이미 수행된다. [INJ]

실제 실행 코드에 결속된 constructor는 `z_snapshot=8`, 초신성 에너지 `10^44 J`, CR 효율 `0.1`, escape fraction `1`, `k_CC=0.0068/Msun`, 전체 source 정규화 quadrature order `128`을 사용한다. 실제 9600 영수증에 모든 인수가 별도 JSON으로 출력된 것은 아니다. 영수증이 핀한 launcher → 실행 API → `ElectronSource()` → `DirectElectronSource()` → `InjectionModel(enabled=True)`의 코드 호출 연결이 기본 인수 사용의 근거다. [INJ, C9600LAUNCH, CRUN, C9600RESULT]

### 2.2 직접 전자 source

초기 proton population이 0이고 source·배경이 고정된 leading local 문제에서

\[
N_p(K,t)=tq_p(K),
\]

\[
A(W)=\sum_{s=\mathrm{H,He}}n_{s,0}
\int_{1\,\mathrm{MeV}}^{4\,\mathrm{MeV}}
q_p(K)v_p(K)\frac{d\sigma_{p,s}}{dW}(K,W)\,dK,
\qquad Q_e(W,t)=tA(W).
\tag{2}
\]

여기서 Rudd SDCS는 `m²/eV`, 따라서 `A(W)`는 `m⁻³ s⁻² eV⁻¹`, `Q_e`는 `m⁻³ s⁻¹ eV⁻¹`다. `Q_e`는 **전자 birth rate**이며 이미 존재하는 전자 stock이 아니다. 열화가 없을 때만 birth 누적수는 `t²A(W)/2`가 된다. 원 source 생성기에서 proton log-K 적분 order는 `64`다. [A, ADER, RUDD]

고정 bath는

\[
n_H=140\ {\rm m^{-3}},\quad Y_{\rm He}=0.248,\quad
n_{\rm He}=\frac{Y_{\rm He}}{4(1-Y_{\rm He})}n_H,
\]

\[
x_{\rm HII}=x_{\rm HeII}=0.01,\quad x_{\rm HeIII}=0,
\quad n_e=0.01(n_H+n_{\rm He}),\quad T_g=100\ {\rm K}.
\]

source의 중성 표적 밀도는 `0.99n_H`, `0.99n_He`다. C의 fullBED 교체는 전자 충돌의 atomic representation을 바꾸며, 양성자 source와 외부 birth 스펙트럼을 바꾸지 않는다. [A, B, C, CCON]

`DirectElectronSource`는 `W/I_s=w`에 대해

\[
A(W)=\sum_s\frac{c_{1s}+c_{2s}w}{(1+w)^3}
\]

의 계수를 저장한다. 다만 이 저에너지 형태를 무한 W로 연장해서 전체 에너지를 적분하면 안 된다. 전체 source 적분은 각 proton K의 실제 ejection endpoint를 포함한 Rudd `cross_section_moments`로 계산한다. 저장된 최소 표본 endpoint는 `2154.927725029828 eV`이므로 선택 창 `W≤900 eV`에서 같은 계수를 사용하는 근거가 있다. [A, B, CR001]

PHYS01의 `transport_population`은 age별 희석 및 redshift를 포함한 최종 proton population을 사용한다. 식 (2)는 이 정확 수송 문제를 silent replacement한 결과가 아니라 PHYS02가 명시적으로 선택한 leading local source다. 저장된 몇 시각의 비교가 있어도 그것은 연속 시간의 오차 인증이 아니다. [P01, ADER, ARES]

## 3. 실제 실행과 cache의 계보

다음은 연구 계획의 추정 연결이 아니라 읽은 원문과 저장 영수증의 연결이다.

| 연결 | 확인한 내용 |
|---|---|
| 9600 launcher → source | 실제 adapter의 worker가 `source=api.cc.ElectronSource()`를 만들고 fullBED·legacy에 같은 객체를 전달한다. |
| C 실행 API → B | `tests/run_targeted.py`의 `cc=bed.parent`; C는 B의 `Cascade`, `ElectronSource`를 그대로 연결한다. |
| B → A → PHYS01 injection | 부모 manifest로 소스 바이트를 확인하며 동일 source model·Rudd 자료로 `A(W)`를 만든다. |
| 9600 NPZ | `source_vectors`, `physical_energy_scale_eV_m3`, `birth_tags`, 원 energy grid를 함께 보존한다. |
| E saved-grid pulse | 저장된 source 열을 재생성하지 않고 `pulse_response`에 전달한다. 물리 scale도 NPZ에서 그대로 읽는다. |
| E → F | F의 `INPUT_IDENTITIES`가 E 실제 `RESULT_fullBED/legacy`를 핀하며 `H0,cdf[-1],R,S`를 읽는다. |
| F → M0 → RUX | `F_CACHED_NUMERICAL_ARTIFACT`의 기록값을 정확 분수로 후처리한다. `selected_record`, `birth_defined`를 합치지 않는다. |

두 9600 NPZ는 source 배열의 raw C-order SHA256이 모두

`07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609`

이며 shape은 `(9611,2)`다. energy 배열 shape은 `(9600,)`, raw SHA256은

`6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`

다. source가 같은 두 원자 모형의 응답 비교라는 사실을 여기서 확인한다. 해시 일치 자체를 물리 정확도나 과거에 소실된 raw CSC의 복구로 해석하지 않는다. [C9600RESULT, ESAVED, EINPUT, FINPUT]

## 4. normalized impulse의 정확한 의미

선택 birth 구간을 `B=[0.1,900] eV`, 두 disjoint tag를 `B_1=[0.1,10]`, `B_2=(10,900]`으로 둔다. 끝점은 연속 source 적분에 영향을 주지 않지만 실제 grid와 ghost 경계는 원 코드 그대로 유지한다.

\[
A_{E,\rm sel}=\int_B WA(W)\,dW,
\qquad \phi(W)=\frac{A(W)}{A_{E,\rm sel}},
\qquad \int_B W\phi(W)\,dW=1.
\tag{3}
\]

`φ`는 number-normalized probability density가 아니다. 에너지로 정규화한 birth shape다. 따라서 `∫φdW`는 일반적으로 1이 아니며, `H0`에 다시 평균 electron energy를 곱하면 이중 변환이 된다.

B의 `source_vectors`는 각 에너지 cell에서 `A(W)/selected_A_energy`를 적분하고 count/energy preserving projection을 적용해 `b_1,b_2`를 만든다. 두 열의 분모는 **각 밴드의 에너지**가 아니라 동일한 전체 선택 `A_E,sel`이다. active 좌표는 전자 에너지이며, cutoff energy·number와 기타 ledger가 따로 붙는다. source의 heat ledger는 정확히 0이다. [B: source_vectors, project, functionals]

`u=t/T0`와 dimensionless generator `G`를 사용한 원 ramp 방정식은

\[
\frac{dz}{du}=Gz+u b,\qquad z(0)=0,\qquad b=b_1+b_2.
\tag{4}
\]

물리적 에너지 밀도 좌표는 `ε_eV U_* z`다. 따라서 식 (4)의 source는

\[
\frac{\epsilon_{\rm eV}U_*}{T_0}u b=q_*\frac{t}{T_0}b
\]

이고 M0의 스칼라 source에 필요한 대응은

\[
\boxed{q(t)=q_*\frac{t}{T_0}=\epsilon_{\rm eV}A_{E,\rm sel}t}.
\tag{5}
\]

이 `q`는 proper volume당 에너지 주입률이다. total power가 필요하면 고정 proper volume을 곱하고, 질량당 값을 원하면 명시한 질량 밀도로 나눈다. 이미 proper인 값에 다시 `(1+z)^3`를 곱하지 않는다.

active block을 `L_u=G[:n,:n]`, dimensionless heat row를 `h_u`라 하면 물리 지연 kernel은

\[
K_b(\tau)=\frac1{T_0}h_u^T
\exp\!\left(L_u\frac{\tau}{T_0}\right)b_{\rm active},
\quad [K_b]=\mathrm{s^{-1}},
\]

\[
H_0=\int_0^\infty K_b(\tau)\,d\tau
=h_u^T(-L_u)^{-1}b_{\rm active},\qquad
dF=\frac{K_b(\tau)}{H_0}\,d\tau.
\tag{6}
\]

`H0`는 이 에너지 정규화와 b에 따른 무차원 eventual heat yield다. 그 적분은 같은 고정 유한 연산자를 계속 유지했을 때의 수학적 continuation이다. 긴 시간 동안 실제 bath가 일정하다는 인증은 아니다. source quadrature와 FP64 projection 때문에 저장 b의 정확한 에너지 합이 명목 1과 마지막 자리에서 다를 수 있으므로, 저장된 전역 scale와 원 b를 함께 유지한다. separately rounded `injected_energy`를 이용해 b를 다시 rescale하지 않는다. 필요하면 개별 b의 실제 에너지 가중치 `η_j=e^T b_j`를 따로 보고하며 `H0_j/η_j`만 자기 birth 에너지에 대한 수율이다.

## 5. power와 cumulative heat의 유도 및 값

zero prehistory와 독립 initial nonthermal stock 0에서

\[
\mathcal P_h(T)=\int_0^T K_b(\tau)q(T-\tau)\,d\tau.
\]

식 (5)를 넣으면 `P_h=q_*∫(1-τ/T0)K_b dτ=q_*H0R`이다. 누적 열에는 한 번 더 적분한다.

\[
\begin{aligned}
\mathcal E_h(T_0)
&=\int_0^{T_0}dt\int_0^tK_b(\tau)q(t-\tau)\,d\tau\\
&=\frac{q_*}{2T_0}\int_0^{T_0}(T_0-\tau)^2K_b(\tau)\,d\tau
=\frac{q_*T_0}{2}H_0S.
\end{aligned}
\tag{7}
\]

E pulse 코드의 `J1=H0 R`, `J2=H0 S/2`와 SI 변환은 이 식을 직접 구현한다. `p=F([0,T0])`는 pulse가 T0까지 내놓은 eventual heat의 비율이다. 선형 birth rate의 endpoint에 p를 곱하는 식은 맞지 않는다. 또한 지금 필요한 누적식은 **선형 source의 누적 열**이다. 이차 source의 누적 열에는 세제곱 truncated moment가 더 필요하므로 이 식으로 대신하지 않는다. [EPULSE, ELAUNCH, CACH, QUAD]

다음은 저장 scalar에 대한 정확 분수 후처리를 유효 숫자로 줄인 값이다.

| 모형 | representation | P_h(T0) [J m⁻³ s⁻¹] | E_h(T0) [J m⁻³] |
|---|---|---:|---:|
| fullBED | selected_record | 3.4427310257273833e−44 | 1.1921620918578547e−34 |
| fullBED | birth_defined | 3.4427310257273836e−44 | 1.1921620918578547e−34 |
| legacy | selected_record | 3.4418410735804500e−44 | 1.1919309813417637e−34 |
| legacy | birth_defined | 3.4418410735804502e−44 | 1.1919309813417638e−34 |

fullBED selected 기록에서 `H0 R=0.01911287708387543`, `H0 S=0.013236960631230734`다. 즉 current birth energy power에 대한 열 power의 비율은 약 1.9113%, 누적 선택 birth energy에 대한 누적 열의 비율은 약 1.3237%다. 같은 kernel의 즉시 eventual-yield 근사에 대한 비율은 각각 `R≈0.03418586`, `S≈0.02367602`다. 이 서로 다른 분모를 바꾸어 쓰지 않는다.

**원 응답만을 이용한 calorimetric 진단.** 고정 조성·부피의 이상 단원자 기체 열용량을

\[
C_{V,0}=\frac32k_B(n_H+n_{\rm He}+n_{e,0})
=3.1697901789973404\times10^{-21}\ {\rm J\,m^{-3}\,K^{-1}}
\]

로 정의하면 fullBED의 `E_h/CV0=3.7610126365996764e−14 K`다. 이것은 열량계적 에너지 환산이다. electron number 변화, expansion, cooling, chemistry 또는 coupling을 포함한 실제 receiver의 `ΔT`나 `Tdot`이 아니다. `PHYSICAL_SCALING_CANDIDATE.json`과 `ARITHMETIC_RECEIPT.json`은 이 단계의 정확 산술과 source identity를 보존한다.

## 6. cutoff에서 thermal bath에 합류시키는 명시적 후보 closure

### 6.1 무엇을 새로 정하는가

원 cascade는 `0.1 eV` cutoff에 도달한 전자의 에너지와 수를 `cutoff_energy`, `cutoff_number`로 **보존하며 열로 넣지 않는다**. 새 후보는 이 두 양을 thermal bath로 동시에 이관한다고 명시한다. 이것은 해석 가능한 추가 closure이며 subcutoff 물리 또는 cutoff 독립성을 새로 검증한 결과는 아니다. 원 기록과 과거의 unresolved-cutoff 상태를 덮어쓰지 않는다.

`cutoff_energy`에는 drift로 경계를 통과한 전자뿐 아니라 실제 에너지가 cutoff 아래인 ionization daughter의 에너지도 들어간다. 따라서

\[
E_c\ne(0.1\ {\rm eV})N_c
\]

가 일반적이다. 에너지와 수는 반드시 저장된 각 ledger를 읽는다. cutoff power에는 source projection의 ghost-cutoff 기여도 이미 포함되며, 저장된 `Gz+u b`가 이를 처리한다. [B: project, summarize; C9600RESULT]

### 6.2 수 보존

B의 number functional은

\[
\mathcal N(z)=\sum_{i\in\rm active}\frac{z_i}{E_i}
+N_c-N_{\rm ion,H}-N_{\rm ion,He}
\]

다. ionization 한 번은 active/cutoff를 합쳐 전자를 하나 더 만들고 ionization counter도 하나 늘리므로 이 조합이 보존된다. stopping과 excitation은 전자수를 바꾸지 않는다. 외부 birth source를 포함하면

\[
\boxed{N_{\rm birth}+N_{\rm sec}=N_{\rm active}+N_c},
\quad N_{\rm sec}=N_{\rm ion,H}+N_{\rm ion,He}.
\tag{8}
\]

paired9600 fullBED의 저장값은 `N_birth=1.6887914953102317e−15`, `N_active=1.5113757640471567e−15`, `N_c=1.8382904526169294e−16 m⁻³`, `N_sec=6.181443264058178e−18+2.318707345589628e−19 m⁻³`다. 원 저장 number-ledger relative residual은 `4.619349761163593e−16`이다. 이 finite model에서 식 (8)을 확인하는 근거가 이미 있다. [C9600RESULT]

### 6.3 열역학식

thermal particle 수와 active nonthermal particle 수를 구분한다. nuclei의 원자·이온 stage가 바뀌어도 thermal heavy-particle 총수 `n_H+n_He`는 이 모형에서 변하지 않는다. cutoff 합류만 thermal electron 수를 늘린다고 정하면

\[
\dot n_{\rm th}=S_c,\qquad
P_{\rm th}=P_h+P_c,\qquad
u_{\rm th}=\frac32 k_B n_{\rm th}T_g.
\]

따라서 고정 부피 에너지 항등식은

\[
\boxed{C_V\dot T_g=P_h+P_c-\frac32k_BT_g S_c}.
\tag{9}
\]

주어진 frozen transport 출력에 대해 `T0=100 K`, `CV0`를 유지한 국소 진단은

\[
\dot T_{\rm frozen}(T_0)=
\frac{P_h(T_0)+P_c(T_0)-\frac32 k_BT_{g,0}S_c(T_0)}{C_{V,0}},
\]

\[
\delta T_{\rm frozen}=\frac{E_h+E_c-\frac32 k_BT_{g,0}N_c}{C_{V,0}}.
\tag{10}
\]

온도 피드백으로 kernel을 바꾸지 않고 주어진 누적 에너지·수만으로 정확 고정체적 열역학 대수를 계산하면

\[
\boxed{\Delta T_{\rm prescribed}
=\frac{E_h+E_c-\frac32k_BT_{g,0}N_c}
{C_{V,0}+\frac32 k_BN_c}}.
\tag{11}
\]

식 (10)은 식 (11)의 frozen-coefficient/일차 표현이다. 식 (11)의 대수가 정확하다는 사실은 frozen cascade가 변경된 기체 조건에서도 정확하다는 뜻이 아니다.

owner가 작성한 A2 후보의 저장값은 `δT_frozen=3.8418834731514848e−14 K`, 국소 `Tdot_frozen=1.1074696107648691e−23 K/s`다. 이 문서는 식 (8)–(11)의 수학과 그에 필요한 원 ledger 의미를 제시한다. A2 코드 실행·전체 확인 결과의 최종 decision은 별도 검토자가 맡는다.

기존 receiver의 `x_e`가 모든 자유전자를 센다면 그 전자수 증가에는 active도 포함된다. 반면 식 (9)의 thermal electron 수에는 cutoff 합류만 들어간다. 두 수의 차이를 active nonthermal ledger에 남겨야 한다. 따라서 이 후보를 한 온도·한 electron count만 가진 receiver에 곧바로 대입할 수 있다고 주장하지 않는다.

### 6.4 all-free event projection은 조건부 대안이다

모든 자유전자를 즉시 동일 thermal temperature의 particle count에 넣는 다른 closure라면 secondary 추가분에 대해 `S_e^sec=S_HI+S_HeI`를 쓰는

\[
C_{V,0}\dot T^{\rm sec}_{\rm frozen}
=P_h-\frac32 k_BT_{g,0}(S_{\rm HI}+S_{\rm HeI})
\]

형태를 만들 수 있다. 그러나 그것은 thermal 합류와 ionization event를 같게 놓는 별도 counting convention이다. 대부분의 새 전자가 아직 active일 수 있는 현재 cascade에는 cutoff 합류 closure가 더 직접적이다. primary proton birth-ionization은 `N_sec`와 별개이며 실제 전체 receiver source에는 추가로 결속해야 한다. heat의 `p/R/S`를 ionization ledger에 그대로 적용하지 않는다.

## 7. 전체 secondary birth energy와 W 밖의 보수적 envelope

같은 source constructor가 전자 mesh loop에 들어가기 **전에** 저장한 coverage는

\[
A_{E,\rm all}=1.5285042578786697\times10^{-33}
\ {\rm eV\,m^{-3}\,s^{-2}},
\]

\[
\frac{A_{E,\rm sel}}{A_{E,\rm all}}=0.7355293039449105
\quad\text{(저장 비율)}.
\]

이 분모는 동일한 `1–4 MeV` proton 충돌이 직접 낳은 **모든 secondary kinetic energy**다. `10 keV–1 PeV` 전체 CR 주입 에너지, primary ionization binding 비용, 핵반응 또는 다른 proton 에너지 창의 기여가 아니다. [CR001, CRUN, A, B]

coverage는 2400/4800 실행의 기록이지만, source 객체·proton order·부모 source 코드가 실제 9600과 같고 `source_energy_coefficient`가 electron mesh를 인수로 받지 않는다. 이를 같은 source의 적분값으로 재사용하며 새 9600 coverage 계산으로 표시하지 않는다. `W>900`의 전체 적분은 저-W rational 식을 무한대로 연장한 값이 아니라 Rudd의 finite endpoint를 가진 원 moment 적분이다.

저장된 값을 쓰면

\[
E_{\rm in,sel}=\frac12\epsilon_{\rm eV}T_0^2A_{E,\rm sel}
=9.0063128921386765\times10^{-33}\ {\rm J\,m^{-3}},
\]

\[
E_{\rm in,all}=1.2244669034713575\times10^{-32}\ {\rm J\,m^{-3}},
\qquad
E_{\rm out}=3.2383561425748985\times10^{-33}\ {\rm J\,m^{-3}}.
\tag{12}
\]

W 밖의 초기 stock이 없고 해당 cohort의 kinetic energy 외에 열에너지를 가져오지 않는다면, 열분율이나 열화시간을 몰라도 `0≤E_h,out(T0)≤E_out`라는 누적 에너지 상계가 있다. 선택 모형의 heat를 고정한 calorimetric envelope는

\[
E_h\le E_{h,\rm sel+out}\le E_h+E_{\rm out}.
\]

fullBED의 `(E_h+E_out)/CV0=1.0592411996249992e−12 K`다. cutoff energy도 thermal bath에 넣는 A2 closure의 더 보수적인 **에너지 전용** 상계는

\[
\boxed{\Delta T\le
\frac{E_h+E_c+E_{\rm out}}{C_{V,0}}
=1.060170012180312\times10^{-12}\ {\rm K}}
\tag{13}
\]

이다. 식 (13)은 새 thermal particle이 요구하는 에너지와 증가한 heat capacity를 무시하므로 양의 초기 온도에서 위쪽으로 보수적이다. cutoff thermalization의 정확 대수를 함께 쓰면 알려진 `N_c`를 numerator와 denominator에 반영해 더 낮은 상계를 만들 수 있다. W 밖에서 새로 들어오는 thermal particle 수가 알려지지 않았다면, 위의 calorimetric 하한을 실제 온도 변화의 하한으로 승격하지 않는다.

선택 모형의 열화까지 신뢰하지 않고 해당 모든 secondary kinetic energy를 열로 허용하는 가장 넓은 같은-source calorimetric 상계는 `E_in,all/CV0=3.8629273053608791e−12 K`다. 이 값들도 기록된 source coefficient와 에너지 회계에 조건부이며 source 물리·quadrature·mesh 오차의 인증구간은 아니다.

**누적 상계와 순간 power 상계는 다르다.** 시간에 무관한 비음 causal kernel, eventual heat yield≤1, 같은 단조 증가 ramp를 추가로 가정하면 `P_out(T0)≤ε_eV T0 A_E,out`도 성립한다. 임의의 시간 변화 과정이 과거 stock을 짧게 방출할 수 있도록 허용하면, 총 에너지 예산만으로 순간 power의 상한을 만들 수 없다. 따라서 식 (12)–(13)의 누적 envelope는 그 추가 stationary 가정 없이 제시하고, 별도 power 상계에는 해당 가정을 명시한다.

## 8. source 모양이 달라질 때의 재사용 가능한 대안

### 8.1 두 저장 birth 열을 그대로 쓰는 경우

현재 두 열은 각기 원래 source의 low/high birth 에너지를 이미 가중한 열이다. 같은 bath에서 새 source가

\[
A_{\rm new}(W)=\lambda_1 A(W)1_{B_1}
+\lambda_2 A(W)1_{B_2},\quad\lambda_j\ge0,
\]

처럼 각 밴드 내부 모양은 유지하고 세기만 바뀐다면 새 generator나 pulse 없이

\[
P_{h,\rm new}(T_0)=q_*\sum_j\lambda_jH_{0j}R_j,
\qquad
E_{h,\rm new}(T_0)=\frac{q_*T_0}{2}
\sum_j\lambda_jH_{0j}S_j
\tag{14}
\]

를 쓴다. 여기의 q*는 원래 전체 선택 source scale다. b_j가 이미 energy weighting을 포함하므로 다시 band fraction을 곱하지 않는다. `H0_j`는 자체 birth 에너지로 정규화한 열수율과 다르다.

반대로 band 자기 에너지로 정규화한 응답을 정의하려면 `f_j=A_E,j/A_E,sel` 또는 명시한 이산 에너지 가중치 `η_j`로 b_j와 H0_j를 나누고, 물리적 band input power에도 같은 정의를 사용해야 한다. source energy 가중치와 heat-delay mixture 가중치를 구분한다. 총 normalized delay moment는

\[
M_{\rm new}=\frac{\sum_j\lambda_jH_{0j}M_j}
{\sum_j\lambda_jH_{0j}},\qquad M_j\in\{p_j,R_j,S_j\},
\]

이므로 **heat yield**로 가중한다. [FCACHE, FANALYSIS, CACHECODE]

### 8.2 밴드 내부 모양이 달라지는 경우

두 적분된 열만으로 임의의 에너지별 Green function을 복원할 수 없다. 예를 들어 exact Bianchi 수송이 proton 스펙트럼 모양을 바꾸거나 source spectral index가 바뀌면 일반적으로 단일 q(t)나 두 band amplitude만으로 정확하지 않다.

생산적인 대안은 현재 source를 저장된 두 모양의 비음 조합으로 근사하고 잔차를 별도로 두는 것이다.

\[
A_{\rm new}(W)=\sum_j\lambda_j A(W)1_{B_j}+\delta A(W).
\]

같은 stationary positive energy-conserving response에서

\[
|\Delta P_h(T_0)|\le\epsilon_{\rm eV}T_0
\int W|\delta A(W)|\,dW,
\]

\[
|\Delta E_h(T_0)|\le\frac12\epsilon_{\rm eV}T_0^2
\int W|\delta A(W)|\,dW.
\tag{15}
\]

이는 개별 source 에너지가 내놓을 수 있는 heat가 그 energy를 넘지 않는다는 선형 양성 응답의 bound다. amplitude-only 변경에는 잔차가 0이며 기성 응답을 즉시 쓴다. 잔차가 명시한 관측량 예산에 작으면 새로운 kernel 없이 충분할 수 있다. 잔차 예산이 크거나 bath 자체가 바뀌면 필요한 energy-channel response만 추가하는 문제가 된다. 현재 두 b의 기록을 충분하지 않은 더 큰 source family에 억지로 맞추지 않는다.

특히 `xi=.01→.1`에서 중성 H/He source가 공통 비율로 줄어 source 모양이 같더라도, Coulomb electron density와 neutral collision rates가 바뀌므로 kernel은 같지 않다. source 모양의 일치만으로 bath 변경을 허용하지 않는다.

## 9. 후보가 주장하는 것과 남은 판정

| 주장 | 이번 근거 상태와 범위 |
|---|---|
| `Qe=tA`와 M0의 q 및 b 정의 | 원문·코드로 결속; 직접 유도 |
| actual9600의 공통 b·물리 scale | 실제 저장 NPZ·영수증의 source identity 확인 |
| SI endpoint heat·cumulative heat | 기록된 scalar의 정확 산술 완료; 기존 SI 결과와 표현 차이를 보존 |
| heat/CV0 | 명시한 고정 조성 calorimetric 진단 |
| cutoff energy+number thermal join | 새로 명시한 후보 closure의 열역학·보존식 유도; 구현 후보 A2는 owner가 별도 생성 |
| W 밖 secondary energy envelope | 같은 active proton source와 저장 full energy coefficient에 조건부인 누적 회계 상계 |
| native receiver·cosmic history·확정 physical error | 이번 산출물로 승격하지 않음 |

이 source 결속은 `CONSUMER_REQUEST`에 남아 있던 무단위 M0 amplitude의 의미를 **특정 기록된 CR source에 대해서** 구체화한다. 다음 단계는 새 solver를 만드는 것이 아니라 이 source/closure 범위를 가진 고정 후보와 실제 사용자의 observable budget을 독립 decision reviewer에게 전달하는 일이다. 최종 PROMOTE/HOLD 판정은 이 후보 생성자가 하지 않는다.

## 주요 원문과 산출물

- [A] `research/cr_phys02a_20261010/src/causal_subthreshold.py`
- [B] `research/cr_phys02b_20261010/src/causal_cascade.py`
- [C] `research/cr_phys02c_20261011/src/coherent_bed.py`
- [INJ] `research/cr_phys01_20261010/src/injection.py`
- [CRUN] `research/cr_phys02c_20261011/tests/run_targeted.py`
- [CR001] `research/cr_phys02c_20261011/evidence/runs/R001/NUMERICAL_RESULT.json`
- [C9600LAUNCH] `research/cr_phys02c_paired_9600_closeout_20261011/raw/ncp_operational_adapter_20261011/launch_refinement.py`
- [C9600RESULT] `research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01/NUMERICAL_RESULT.json`
- [ESAVED, EPULSE, ELAUNCH] `research/cr_phys02e_20261011/{src/saved_grid.py,src/pulse_response.py,ncp/launch_pulse.py}`
- [E_FULL, E_LEGACY] `research/cr_phys02e_ncp_return_20261011/actual_run/RESULT_{fullBED,legacy}.json`
- [FINPUT, FANALYSIS] `research/cr_phys02f_20261011/{inputs/INPUT_IDENTITIES.json,src/tail_analysis.py}`
- [FCACHE, CACHECODE] `research/cr_plan_reset_20261012/{inputs/F_CACHED_NUMERICAL_ARTIFACT.json,evaluate_cached_response.py}`
- [CACH, QUAD] `research/cr_rux_m1_m3_20261012/inputs/{CACHED_RESPONSE.json,QUADRATIC_RESPONSE.json}`
- `SOURCE_INVENTORY.json`: 위 식별자 및 보조 원문 40개의 바이트 identity·읽기 범위.
- `qe_lineage/SOURCE_FINDINGS_KO.md`: 독립적으로 나눈 source 호출 계보 분석. 최종 decision review로 세지 않음.
- `PHYSICAL_SCALING_CANDIDATE.json`, `derive_physical_scaling.py`, `ARITHMETIC_RECEIPT.json`: heat-only calorimetric 및 outside energy 후보 산술의 원 결과와 재현 코드. root의 A2 cutoff thermal join 후보와 서로 다른 역할로 보존.
