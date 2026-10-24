# CR_N5: 공급자 rate 의미론, 원자 장부, EE first-entry 경쟁 판정

작성: `/root/n5_theory`, 2026-10-24 UTC. `physmath-research-loop` 내장 규약 1.0.0의 R3–R7에 한정한 이론 기여다. 부모 구현과 독립적으로 식·수용 조건을 구성했다. 이 문서는 코드 독립 C9, 새 atomic provider admission, 새 ODE 결과를 대신하지 않는다. 기존 C23D/PR59와 C23E/PHYS79의 정리·계산은 재사용한다. 새로운 strong no-go 또는 문헌상 우선권을 주장하지 않는다.

**결론.** PHYS83의 저장된 Maxwellian CE 계수는 고정 bath의 표적 원자 사건률에 바로 결속된다. 비열 전자 한 개의 충돌 hazard에는 에너지별 단면적과 충돌 상대의 밀도가 필요하다. C23D의 `W<10 eV`는 초기 source 선택이며, first-entry 경로의 상한은 반사 경계 `40 k_B T` 또는 `80 k_B T`다. 이 구별을 보존하면 기존 평균 first-entry 시간을 재적분하지 않고, 아직 미수신인 전자별 hazard의 허용 상한을 역산하는 유효한 조건부 진단을 만들 수 있다.

## 1. 읽은 근거와 현재 수신 범위

- C23D: `bass_cr@4a0bbc0ed618ab6eae1b7b2714e366d803186b86`, `research/cr_c23d_finiteT_source_bridge_20261024/FROZEN_CONTRACT.md`와 저장 `runs/c23d_source_ee_20261023T220714Z_v1/MFPT.json`. 원본 ZIP을 복원한 `baseline_c23d/repository/`의 파일을 읽었다. 기존 `MaxwellianCoulomb`/generator/MFPT 계산은 실행하지 않았다.
- C23E: `bass_cr@8e4e06361d714939513a11f64a27f02822bde2fa`, `research/cr_c23e_d43_source_binding_20261024/THEORY_KO.md`, Git blob `f03240a432662e09a026bbd74cffc2e9743ca447`. D43K PI/RR/CX 에너지 장부와 문턱 이동 모멘트는 재사용 근거다.
- PHYS83: `WU088_HH` PR140 science/return의 정확한 위치는 `provider_returns/SOURCE_INDEX.json`에 결속한다. 저장 `wu83_rates.csv`와 `wu83_contract_full.json`을 읽었다. H I 1s↔2s/2p, source-native gap `10.20435 eV`, heavy stationary-target Maxwellian, finite W-PL representation, 66개 정확한 온도/132개 rate 행이다.
- PHYS84: `wu84_return.md`, `wu84_contract.json`과 최신 `wu84new_wait.json`을 읽었다. instantaneous source adapter의 numerical application은 여전히 미수신이다.
- HE-ANG: `BASS_HE@d8bae9f7e24ad3494e399f7ab46c4167a5623d48`, `he_ang_ddcs20_window_20261024/CONTRACT.json`과 convention audit. 입사 20 eV, 출사 3–6 eV, 15–120°의 조건부 DDCS window 모멘트를 제공한다. 전체 event law, complete angular support, recoil owner는 이 window에서 따라 나오지 않는다.
- 외부 원전 확인: ADAS108의 neutral excitation 단면적/Maxwell averaging, ADAS302의 상대속도 평균, OPEN-ADAS ADF07/08 구분, CHIANTI v9 user guide §6.10. URL과 이번 검색 근거는 `SOURCE_NOTES.json`에 적었다. 원전 의미론 확인과 프로젝트 수치 admission을 분리한다.

## 2. 전자 분포와 사건률의 구분

모든 밀도는 같은 local normal bath frame의 proper volume당 수밀도, 시간은 그 frame의 proper time이다. 상대론적 수송에는 signature `(-,+,+,+)`를 유지하지만 아래 작은 원자 충돌 계산은 명시된 비상대론적, stationary-heavy-target 근사다. 에너지 `W`를 J로 쓸 때 `v(W)=sqrt(2W/m_e)`이며 eV 입력에서는 `W_J = epsilon_eV W_eV`를 먼저 적용한다.

표적 `s`에 대한 단면적을 `sigma_s(W)`라 하고, 정규화된 전자 에너지 확률밀도를 `f_E(W)`라 하자. 이중으로 열평균하지 않는 기본식은

\[
k_s[f_E]=\int_0^\infty f_E(W)\,\sigma_s(W)\sqrt{2W/m_e}\,dW,
\qquad \int f_E(W)dW=1.
\]

Maxwellian에서는

\[
f_M(W;T)=\frac{2\sqrt W}{\sqrt\pi(k_BT)^{3/2}}e^{-W/(k_BT)},\qquad
k_s(T)=\sqrt{\frac{8}{\pi m_e}}(k_BT)^{-3/2}
\int W\sigma_s(W)e^{-W/(k_BT)}dW .
\]

이는 Maxwellian **표적 사건률**

\[
\nu_{s,\mathrm{per\ target}}=n_{e,\mathrm{thermal}}k_s(T),\qquad
r_s=n_s n_{e,\mathrm{thermal}} k_s(T)
\]

를 준다. 각각 `[s^-1]`, `[cm^-3 s^-1]`다. 반면 지정된 에너지의 **tagged 전자**에는

\[
h_s(W)=n_s\,\sigma_s(W)\sqrt{2W/m_e}
\]

가 적용된다. 여기에 곱하는 것은 전자밀도가 아니라 충돌 상대인 `n_s`다. `k_s(T)` 하나 또는 온도별 유한 표를 임의의 `h_s(W)`로 직접 바꾸지 않는다. 분포가 실제 Maxwellian이고 필요한 평균 관측량만 계산하는 경우에는 그 평균을 사용할 수 있으나, 그 경우에도 표적당/전자당/부피당 rate를 구분해야 한다.

움직이는 표적의 속도분포 `g_s(u)`가 정규화되어 있으면 전자별 hazard는

\[
h_s(\mathbf v)=n_s\int g_s(\mathbf u)\,
\sigma_s(E_{\rm rel})\,|\mathbf v-\mathbf u|\,d^3u,
\quad E_{\rm rel}=\tfrac12\mu_{es}|\mathbf v-\mathbf u|^2.
\]

따라서 laboratory projectile energy인지 CM relative energy인지, `m_e`/reduced mass 중 어느 것을 쓰는지가 계약의 일부다. cold-target 문턱을 Maxwellian target에 그대로 적용해 전 경로의 exact zero를 선언하지 않는다. ADAS302의 두 분포 평균도 같은 상대속도 구조를 사용한다.

### 실제 PHYS83 적용

정확한 `T=10000 K` 저장 행은 다음과 같다. 이번 child는 이 값을 읽었고 다시 계산하지 않았다.

| H I channel | `k_up [cm^3 s^-1]` | `k_down [cm^3 s^-1]` |
|---|---:|---:|
| 1s↔2s | 8.512547823605277e-14 | 1.1825666233594462e-08 |
| 1s↔2p | 1.4643481898603336e-13 | 6.780928304072407e-09 |

`n_e=0.14 cm^-3`와 곱하면 각 초기 level의 thermal per-target rate다. 이를 저장된 EE 평균시간 `m`과 곱한 `n_e k(T)m`은 고정 bath/고정 표적 population을 유지한 비교 시간에 대한 **thermal target event exposure**다. 비열 source 전자 하나의 사건 확률로 해석할 수 없다. 전하·온도가 실제로 변하는 coupling에서는 해당 rates를 시간별 population과 함께 적분해야 한다.

`W<10 eV`인 초기 tagged 전자는 source-native ground-H excitation gap `10.20435 eV`보다 낮다. 이 말은 그 초기 energy support와 stationary-target convention에 대한 문턱 판정이다. thermal Maxwellian tail에는 gap 위 전자가 존재하고, excited H의 superelastic deexcitation은 별도 level population과 reverse kernel을 요구한다.

## 3. 초기 source support와 EE first-entry 경로 domain

C23D의 초기 선택은 `0<W<10 eV`이고 `q=chi k_B T`, `chi=1.5` 또는 `3`이다. first-entry 계산은 `W_R=40 k_B T`에 반사 경계를 둔 후, endpoint truncation 진단으로 `80 k_B T`를 썼다. 저장 MFPT는 **연속 finite-band 식의 numerical quadrature**다. 별도로 계산한 256/512-point 시간진화와 혼동하여 MFPT를 finite-grid ODE 결과라고 부르지 않는다.

`T=10000 K`에서 `40 k_B T≈34.4693 eV`, `80 k_B T≈68.9387 eV`다. 따라서 EE diffusion 경로는 초기 ceiling 10 eV 위로 갈 수 있다. 어떤 추가 반응을 first-entry 전 전체 시간에서 배제하거나 bound하려면 `q≤W≤W_R`의 도달가능 경로 전체를 검사한다.

- ground-H CE와 H CI는 초기 source에서 문턱 아래여도 경로 전체에서 자동 배제되지 않는다.
- H/He/Li CI의 source finite-window upper/lower limits와 physical chemical threshold는 서로 다른 필드다.
- `Li7 [6,15] eV`의 자료를 `q..80 k_B T` 전체 hazard로 확장하지 않는다. source 밖에 missing이 남으면 그 채널의 global `hmax`는 `null`이다.
- `He4 [24.6,60] eV` 역시 `80 k_B T` 경로 상단을 덮지 않는다. 원 numerical representation이 explicitly finite-support model로 채택되어도, 그 바깥 zero는 모형 정의의 범위이지 완전한 물리적 단면적 증거가 아니다.

`initial_support`, `reachable_path_domain`, `source_domain`, `chemical_threshold`, `source_native_threshold`를 하나의 `energy_range`로 압축하면 이 판정이 유실된다.

## 4. 기존 MFPT를 사용하는 첫 추가 사건 확률의 상한

### 정의와 전제

기존 frozen EE 과정을 `W_t`, 목표 core의 첫 진입 시각을

\[
\tau=\inf\{t\ge0:W_t\le q\}
\]

로 둔다. `W_0>q`인 source atoms에 조건부로 정규화한 초기법칙을 사용하며 `m_A=E[τ | active]<∞`라 하자. 추가 원자 사건의 비음성 predictable hazard를 `h(W_t,t)`라 하고, **첫 추가 사건까지** EE와 같은 경로를 따르며 경로에 조건부인 Poisson mark로 사건이 발생한다고 가정한다. 추가 사건 이후의 경로는 이 first-event 계산에 들어가지 않는다. 전 경로와 시간에서 `0≤h≤h_max<∞`가 공급되어야 한다.

경로별 누적 hazard는 `H_τ=∫_0^τ h(W_t,t)dt`다. 조건부 무사건 확률이 `exp(-H_τ)`이므로

\[
P_A=\Pr(T_{\rm event}<\tau\mid active)
=1-\mathbb E[e^{-H_\tau}\mid active].
\]

`H_τ≤h_max τ`와 `e^{-x}`의 convexity를 차례로 쓰면

\[
\mathbb E[e^{-H_\tau}]
\ge\mathbb E[e^{-h_{\max}\tau}]
\ge e^{-h_{\max}m_A},\qquad
\boxed{P_A\le 1-e^{-h_{\max}m_A}\le h_{\max}m_A.}
\]

목표 허용확률 `0<epsilon<1`에 대한 **충분조건**은

\[
\boxed{h_{\max}\le -\log(1-\epsilon)/m_A.}
\]

코드에서는 `-expm1(-h_max*m_A)`, `-log1p(-epsilon)/m_A`를 사용해 작은 수의 cancellation을 피한다. 우변은 `[s^-1]`다. bound에는 실제 `hmax` 공급이 필요하지만, 허용 ceiling 자체는 새 반응 단면적 없이 기존 mean과 선택 epsilon으로 계산할 수 있다. ceiling이 계산되었다는 사실은 실제 채널이 그 ceiling 아래라는 판정이 아니다.

### 선택 source 전체와 원 pulse의 구별

선택 source 중 active fraction을 `f_A`라 하고 처음부터 core에 있는 입자는 정의상 `τ=0`이면

\[
P_{\rm selected}\le f_A[1-e^{-h_{\max}m_A}].
\]

이는 `1-e^{-h_max f_A m_A}`를 사용하는 것보다 같거나 강한 상한이다. 선택되지 않은 `W≥10 eV` source가 포함된 원 pulse 전체에는 그 채널의 별도 정보가 필요하다. 선택 count fraction이 `f_sel`이면 아무 추가 정보가 없을 때 가능한 보수적 전체 상한은 `f_sel B_selected+(1-f_sel)`이며, `f_sel B_selected`만으로 전체 확률을 bound했다고 쓰지 않는다.

### 이 상한의 과학적 지위

위 부등식은 주어진 확률과정과 hazard 조건 아래 **derived**다. C23D 저장 `m_A`를 대입한 숫자는 기존 continuous finite-band 모델의 수치평가를 재사용한 **conditional numerical diagnostic**이다. quadrature estimate, upper-boundary sensitivity, physical unbounded-domain error가 certified upper error로 공급되지 않았으므로 continuum/우주론 전체의 certified probability bound로 승격하지 않는다. 엄밀한 수치 보증을 하려면 `m_A≤m_plus`의 검증된 upper enclosure를 넣으면 된다. 현재 `global_error_bound=null`을 유지한다.

`hmax=null`, density 누락, time/frame 불일치, source 밖 경로 존재, 잘못된 hazard type이면 `P_A=null`을 반환해야 한다. 원자료에 physical zero가 명시된 경우만 zero를 채택한다. 음의 energy drift를 hazard로 사용할 수 없다. EE energy drift, diffusion, pitch-angle relaxation, first-entry clock은 서로 다른 관측량이다.

### 독립적으로 확인 가능한 해석적 사례

`x=h m`에 대해 다음은 과거 science replay 없이 새 adapter의 계산식을 검사하는 작은 기준이다.

| Waiting law, constant hazard h | Exact first-event probability | 비교 |
|---|---|---|
| `τ=m` deterministic | `1-exp(-x)` | Jensen equality |
| Exponential `τ`, mean m | `x/(1+x)` | `≤1-exp(-x)` |
| `τ=0` or `2m`, each probability 1/2 | `(1-exp(-2x))/2` | 같은 mean, 더 작은 값 |
| `h=0` | `0` | zero-limit |
| initially core `τ=0` | `0` | first-entry observable 정의 |

부호·극한은 `P≥0`, `P≤1`, `h→0`에서 `P≤hm→0`, fixed m에서 monotone-in-h, scaling `h→h/a, m→a m` 불변이다. Mean만 고정하면 추가 분포 정보 없이 비자명한 양의 lower bound를 강제할 수 없다. 예를 들어 매우 작은 확률의 아주 긴 waiting time으로 mean을 보존하면 first-event probability는 임의로 작아질 수 있다. 이는 이 진단의 정보 한계를 보여주는 직접 예이며 새 strong no-go 성과로 채택하지 않는다.

### 기존 EE operator와의 후속 연결

기존 forward current convention `J=aF-∂_W(DF)`에서 backward generator는 `L=a∂_W+D∂_W²`다. time-independent h에 대해 core까지 무사건 확률 `u`는 `(L-h)u=0`, `u(q)=1`, `u'(W_R)=0`이고 `v=1-u`는 `(L-h)v=-h`, `v(q)=0`, `v'(W_R)=0`이다. 기존 mean의 식은 `Lm=-1`, `m(q)=0`, `m'(W_R)=0`이다. 이 대응은 나중에 실제 h를 수신할 때 쓰며, 이번 child에서는 어느 방정식도 새로 풀지 않았다.

## 5. 원자 사건 장부의 최소 조건

종·isotope·charge·internal level을 식별하는 population vector `n`과 stoichiometric matrix `S`에 대해 `dot n = S r`를 쓴다. 모든 purely atomic event column `a`는 각 isotope별 핵수와 전체 전하를 보존해야 한다. electron row에는 thermal/fast pool을 합한 자유전자를 사용하고 `n_e,all=n_e,thermal+n_e,fast`를 별도 검사한다.

| Process | Free-electron count | 핵종/charge bookkeeping | 필요한 energy owner |
|---|---:|---|---|
| PI | +1 | target charge +1 | absorbed photon = chemical increase + primary kinetic + recoil |
| CI | +1 | incident electron+target → two electrons+ion | incoming kinetic = outgoing kinetic sum + chemical increase + recoil |
| RR | −1 | ion charge −1 | captured kinetic + released binding → photon(s)+recoil |
| DR after stabilization | −1 | specified final bound ion | successful stabilization branch와 emitted photons; raw capture/autoionization 구별 |
| CX | 0 | donor/receiver charge 변화, 각 isotope 보존 | consistent chemical-potential difference와 상대운동 energy |
| CE/deexcitation | 0 | 같은 isotope/charge, internal level 이동 | kinetic↔internal energy; radiative decay의 별도 photon owner |
| neutral elastic/EI | 0 | populations unchanged | opposite electron/heavy-target kinetic transfer; angular moment owner |
| EE | 0 total | tagged/bath partition의 같은 current | tagged kinetic 변화의 반대 bath ledger; cutoff bookkeeping 중복 금지 |

부분단면적 window의 normalization을 total event rate로 확장하지 않는다. 특히 HE94의 one-electron DDCS window는 incident energy를 유지한 출사 부분 support다. 그 normalized window moments가 두 outgoing electrons의 joint law, 전체 ionization event count, finite-mass recoil 또는 full energy owner를 결정하지 않는다.

모든 활성 column은 하나의 shared internal energy descriptor `U_internal=Σ_i chi_i n_i`를 사용한다. kinetic/thermal/radiation/recoil/escape를 따로 합친 동일 event ledger에서

\[
\Delta U_{\rm th}+\Delta U_{\rm fast}+\Delta U_{\rm internal}
+\Delta U_{\rm recoil}+\Delta U_{\rm rad,escaped}
-E_{\rm incoming,external}=0
\]

를 확인한다. C23E PI/RR/CX의 선택된 모델에서는 그 기존 ledger를 그대로 매핑한다. source-native threshold와 chemical defect가 다른 자료를 쓸 때, 공급자가 선언한 convention을 보존하며 energy defect를 몰래 source knot로 대체하지 않는다. 같은 photoelectron kinetic source를 fast pool과 instantaneous thermal heat에 함께 넣으면 동일 사건의 energy를 중복 소유한다.

중성 elastic/EI의 **total collision cross section**만으로 stopping power를 정의하지 않는다. energy-transfer weight 또는 differential kernel, target mass/distribution이 필요하다. infinite-mass stationary target의 탄성 산란은 방향을 바꾸어도 그 근사 안에서 electron kinetic loss가 없을 수 있다. 따라서 event probability bound와 heat-deposition bound는 별도 관측량이다.

## 6. Isotope quotient: 기존 C23E 결과와의 정확한 연결

fine population을 `x`, isotope를 합치는 선형 map을 `P`, generator를 `Q`라 하면 모든 초기 상태에 대한 exact linear quotient 조건은

\[
P Q=\bar Q P.
\]

이는 각 coarse block으로 향하는 aggregate rate가 같은 block 안의 fine state 선택에 의존하지 않는다는 조건이다. 모든 원소별 generator가 완전히 같다는 것은 충분조건일 수 있지만 필요한 조건은 이 aggregate identity다. bilinear chemistry에서는 대응 조건 `P F(x)=bar F(Px)`를 적용한다.

H/D neutral/ion states를 elemental charge state로 묶고 PI를 켠 경우, 합친 neutral derivative에는 `-Gamma_H n_H0-Gamma_D n_D0`가 들어간다. arbitrary isotope split에 대해 `n_H0+n_D0`만으로 닫히려면 그 PI coefficients가 같아야 한다. C23E는 실제 source의 새 band를 사용하여 `Gamma_D=Gamma_H-G_l`을 이미 계산했다. 양의 band에서는 `G_l>0`이므로 이 모형의 PI quotient를 무조건 채택하지 않는다. CX만의 total charge incidence가 coarse map 아래 0일 수 있다는 사실과 PI closure를 구별한다.

population quotient와 energy observable quotient도 분리한다. energy weight `c^T x`가 coarse variables만으로 정확히 표현되려면 `c^T=bar c^T P`가 필요하다. C23E의 `chi_D-chi_H=43 k_B`에서는 D+의 독립 moment 또는 그에 동등한 chemical-energy correction을 유지한다. 이를 버린 순간적 binding error는 `|delta| n_D+`로 직접 추적할 수 있다. 이를 global temperature/observable error bound로 부르려면 dynamics와 목표 norm의 별도 안정성 근거가 필요하다.

C23E의 기존 moment identities를 사용하면 isotope source 근사의 local mismatch가 이미 분해된다:

\[
\Gamma_D-\Gamma_H=-G_l,\quad
K_D-K_H=-\delta\Gamma_H+B_l,\quad
A_D-A_H=-A_l.
\]

N5에는 이 같은 **count / primary kinetic / absorbed energy / binding** 차이와 단면적의 finite-mass/level/source uncertainty를 따로 결속한다. 목표 정확도, abundance, source/frame와 temperature가 없는 isotope transfer를 자동 승인하지 않는다. D/T/He3/Li6의 누락 source는 해당 isotopic coverage cell에 `null`로 유지한다.

## 7. 구현 계약과 최소 negative cases

각 provider row에는 최소한 다음 정보를 유지한다.

1. 실제 repository/commit/path/blob 및 byte SHA256, provider/owner, science/return gate.
2. process, projectile/target isotope·charge·level, final-state branch.
3. `rate_kind`: energy-resolved cross section, Maxwellian coefficient, per-target rate, tagged hazard, partial DDCS moment 등을 enum으로 분리.
4. 입력 energy coordinate와 units, source-native/chemical threshold, T/E/angular support와 interpolation/extrapolation policy.
5. particle distribution, relative-velocity/mass approximation, frame, proper time/volume convention.
6. target/electron density field와 population closure, missing value status.
7. event count normalization, outgoing-particle convention, energy-owner map, omitted channels.
8. source/fit/discretization/isotope/model uncertainty와 허용 observable; `initial_support` 및 `reachable_path_domain`을 별도 보존.

필수 negative tests는 다음과 같다.

- Maxwellian `k(T)`를 tagged-hazard 입력으로 제출하면 type error 또는 non-admission.
- per-target `n_e k`와 per-electron `n_s sigma v`의 density를 바꾸면 reject.
- `W_initial<10`만을 근거로 H excitation/ionization을 EE first-entry 전 경로에서 0으로 채택하면 reject.
- finite interval source의 바깥을 0으로 padding하거나 sample maximum을 certified global hmax로 취급하면 reject.
- PHYS83 T=10000 정확 행 재사용은 accept; 다른 T에 무단 nearest-neighbor 또는 domain 밖 extrapolation은 reject.
- excited state가 없는21-population register에서 superelastic rate를 ground population에 곱하면 reject; 해당 level population absent이면 null.
- source-native gap10.20435eV를 chemical H ionization energy 또는 PI13.6eV로 대체하면 mismatch.
- HE94 window normalization을 total/event cross section으로 바꾸거나 arbitrary factor2를 가산하면 reject.
- C23E unequal H/D PI source에 equal-rate quotient를 지정하면 reject; energy moment 보존 조건도 별도로 검사.
- h<0, nonfinite m/h, epsilon≤0 또는≥1은 reject. h 또는 required density가 null이면 actual probability는 null.
- mean의 active/all-selected normalization과 q, W_R, bath source identity가 다르면 reject.
- `first_event_probability`를 stopping-energy fraction, permanent assimilation 또는 Maxwellization probability로 rename하면 semantic mismatch.

### 채택 예정인 bounded CE source adapter: panel maximum의 구성

부모는 PHYS83의 기존 `MatchedCEChannel` constructor가 복원한 정확한 source-native `(E,W)` arrays를 재사용하는 경로를 선택했다. 기존 `evaluate/moments` 또는 Maxwellian rate 적분을 다시 실행하지 않는다. 여기서 `W_s(E)=E sigma_up,s(E)`이고 s=2s,2p는 서로 배타적인 두 final atomic channels다. 원 source에 포함된 degeneracy를 다시 곱하지 않는다. `n_1s=0.9 cm^-3`는 C23D total HI density에 **ground-state population assignment를 추가로 명시한** 새 frozen input이다. n2s/n2p는 여전히 unsupplied다.

E를 eV, W를 `eV cm^2`로 두면 선택된 두 CE channels의 event hazard는

\[
h_{\rm CE}(E)=C\frac{W_{2s}(E)+W_{2p}(E)}{\sqrt E},\qquad
C=n_{1s}\,100\sqrt{2\epsilon_{\rm eV}/m_e}.
\]

100은 m/s를 cm/s로 바꾸는 단위변환이다. source-native threshold 아래에서는 이 provider가 명시한 kinematic zero를 쓰며, 그 위의 EE path가 모두 source support에 포함되는지 확인한다. 출발 source의 `E<10`과 실제 reflected path 상한 `80 k_BT`를 분리한다.

두 positive W-PL channel의 knot union을 취하면 각 공통 panel에서 `W_total(E)=aE+b≥0`다. `E>0`에서

\[
h'(E)=\frac{C(aE-b)}{2E^{3/2}}.
\]

`a=0`이면 b≥0이므로 h는 감소하거나 0이다. `a>0,b≤0`이면 증가한다. `a<0,b≥0`이면 감소한다. 양의 interior stationary point `E_*=b/a`와 nonnegative W가 동시에 가능한 비자명한 경우는 a,b>0이며, 그 점에서 derivative가 음에서 양으로 바뀌어 **minimum**이다. a,b<0이면 모든 positive E에서 W<0이므로 admitted positive panel에 해당하지 않는다. 따라서 nonnegative W-PL representation의 h는 **각 panel의 endpoint에서 maximum을 갖는다**. 이는 finite set of knots와 truncated domain endpoints를 평가하는 계산식으로 곧바로 연결된다.

Generic stationary-candidate 평가를 별도 검산으로 남겨도 되지만 maximum search의 필수 집합은 union knots와 q/U endpoints뿐이다. cut endpoint가 source knot 내부에 있으면 기존 W-PL의 양의 보간값을 사용한다. q가 문턱 아래이면 해당 구간은 kinematic zero이며 문턱 자체도 union에 포함한다. U가 어느 channel의 유효 source support를 넘어가면 global hmax를 계산하지 않고 missing-domain 상태로 반환한다.

floating arithmetic에서는 `aE+b`의 cancellation 대신 `t=(E-E_l)/(E_r-E_l)`, `W=(1-t)W_l+tW_r`를 사용하고 `0≤t≤1`과 source positivity를 검사한다. source threshold의 exact zero는 source 값으로 보존하며, 임의의 negative clipping이나 extrapolation으로 양수성을 만든 것으로 인정하지 않는다. Panel slope/intercept는 증명 또는 independent stationary check용이고 positive endpoint interpolation이 수치 계산의 주 경로다.

독립 arithmetic 검산은 실제 binary64 knot/W/density/constants를 `Decimal.from_float`로 정확히 옮겨 square-root 및 finite maximum을 높은 정밀도로 계산하는 방식이 적절하다. 원 source decimal과 binary64 input을 섞어 차이를 evaluator rounding error라고 부르지 않는다. 임의의 admissible positive panels(증가·감소·interior minimum·zero endpoint)를 검사하고 특히 two-channel knot union과 clipped endpoint 사례를 포함한다. numerical grid maximum과 달리 여기서는 endpoint sufficiency의 해석적 증명이 있어 representation-wide maximum을 계산한다. FP evaluation error는 측정된 허용오차에 따로 결속하고 원전 단면적·finite-mass·omitted-level uncertainty는 별도로 open이다.

이 hmax로 얻은 수치는 **선택 ground-H 2s/2p CE-only marked clock along the frozen EE path**의 첫 사건에 대한 조건부 상한이다. 다른 neutral elastic/CI/RR/DR/CX/EI가 missing이면 total non-EE first-event bound는 계속 null이다. 알려지지 않은 사건으로 변형된 full coupled path의 총 CE 횟수나 deposition fraction은 이 bound의 관측량이 아니다. 첫 CE까지의 비교로 한정하면 다른 independent competing marks가 추가되어도 first CE before any-other/core 사건은 선택 CE-only first-event 사건의 부분집합이다.

이 child는 provider constructor, 새 hazard evaluator 또는 numerical maximum을 실행하지 않았다. 부모가 frozen v2 input과 신규 run ID 아래 수행하고 측정해야 한다.

## 8. 단계 기록과 남은 의무

| Stage | 이 child의 실제 산출물 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|---|
| R3 | rate/observable/domain 정렬 | derived + source read | parent integration pending | local artifact for parent | N5 scoped |
| R4 | thermal exposure와 tagged first-event bound 선택 | derived | parent integration pending | same local artifact | full-path hazard input open |
| R5 | survival/Jensen bound, quotient/energy mapping | derived | parent integration pending | same local artifact | old MFPT reused |
| R6 | 부호/단위/범위/analytic waiting laws/initial-vs-path countercheck | analytical consistency checked; no code audit | parent integration pending | same local artifact | C9 remains separate |
| R7 | exact test expectations 및 numeric execution contract | numerical execution NOT_RUN in this child | parent execution decides | same local artifact | no ODE/provider reexecution |

이론 child의 새 ODE, scientific provider rerun, full suite, quadrature, external dispatch는 모두 0이다. 새 runtime CPU 총량을 측정하지 않았으므로 이 child의 총비용은 unknown이며 0으로 보고하지 않는다. 부모가 수행할 새 diagnostic의 측정 비용과 inherited budgets를 따로 기록한다. global error 및 전체 completion percentage는 null을 유지한다.
