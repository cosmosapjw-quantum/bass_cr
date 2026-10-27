# Proper-time injection/return: 채택 유도와 계산식

검토자: /root/theory_review. 조회일: 2026-10-27.
범위: 이론 유도, 원문 대조, 한정 Wolfram 대수. 기존 source/solver 과학 재실행 0.
독립 유도를 root가 원 source 코드·배열 의미와 대조하여 R5에 채택했다. 후속 R6는 별도 검토자가 적용 범위와 핵심 식을 검사한다.

## 1. Source measure와 한 번의 변환

공통 recipient-frame에서 native number measure를
dN_s = q_s^nat(t_n, ξ) dt_n dV_n dξ
로 정의한다. 시간, 부피, 에너지 변환이 분리되는 동일 worldtube에 대해서만
j_s(E,τ) = q_s^nat(t_n(τ),ξ(E)) |dt_n/dτ| (dV_n/dV_p) |dξ/dE|
이며 j_s 단위는 number/(proper m³ proper s energy-unit)이다.
이는 dN 동일성으로 직접 유도된다. Clock·volume·energy-coordinate 인자를 이미 포함한 source에 다시 적용하지 않는다.

Source가 hazard per target이면 target density는 그 source를 volumetric source로 만드는 한 곳에서만 곱한다.
Source가 이미 volume-rate이면 추가 target density가 없다.
Surface flux는 volume source가 아니다. 면적·방향·입사 cosine·수송 geometry 없이는 바꿀 수 없다.
각도 적분된 rate에 4π를 다시 붙이지 않는다.

다른 frame 간 변환은 위 scalar factors만으로 수행할 수 없다. Metric(-,+,+,+),
u·u=-c²일 때 E_total=-p·u, massive particle E_kin=E_total-mc²이다.
Energy-angle distribution와 같은 worldtube의 Lorentz/geometry 변환이 따로 있어야 한다.
현재 bounded adapter는 동일 frame identity만 수용하고 mixed-frame 입력을 거절한다.

조건부 단위 예:
proper seconds+comoving m³ rate -> a^-3;
conformal time+comoving m³ rate -> a^-4;
proper seconds+proper m³ rate -> 1.
이는 source에 해당하는 clock/volume definitions가 있을 때만 쓰는 변수변환이다.

## 2. Finite source history와 적분량

고정 proper V에서
N_s[a,b] = ∫_a^b dτ ∫_support j_s(E,τ)dE,
U_s[a,b] = ∫_a^b dτ ∫_support E j_s(E,τ)dE.
E가 eV이면 U를 J로 내보낼 때만 eV_J=1.602176634e-19 J/eV를 한 번 곱한다.
Source가 이미 J 단위 moment를 공급하면 다시 곱하지 않는다.

시간 가변 V인 worldtube에는 absolute count ∫V(τ)j_N(τ)dτ를 사용한 뒤
명시된 reference/final V로 나눈다. ∫j_Ndτ를 final density로 부르는 것은 일반적으로 틀리다.
현재 PHYS02와 PR107 frozen boxes를 서로 합성하는 volume history는 공급되지 않았다.

Source snapshot의 두 moments N,U는 energy distribution이나 time history를 정하지 않는다.
Time history가 원 구현에 별도로 정의된 경우에만 그 법칙을 이용한 적분/미분이 가능하다.
t=b 이후 continuation 또는 shutoff가 정의되지 않았으면 둘 다 추정하지 않는다.

## 3. 실제 선택된 PHYS02 원문과의 대조

원 source revision은 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b.
D=ec463db0c7e5c7fb5070796071c926caa4db6445에서 읽는 retained lineage:
- research/cr_phys01_20261010/src/injection.py:
  q_proper_m3_s_eV는 angle-integrated number/(proper m³ s eV).
  z_snapshot=8의 comoving->proper729는 이미 q_p에 포함.
- research/cr_phys02a_20261010/src/causal_subthreshold.py:
  prescribed-source local ramp Q_e(W,t)=t A(W), T_END=1e10 s,
  초기 proton stock0의 leading-local 근사.
- research/cr_phys02b_20261010/src/causal_cascade.py:
  selected direct electron support0.1..900eV, split10eV.
  target HI=.99*140m^-3, HeI=.99*[140*.248/(4*(1-.248))]m^-3가 A에 이미 포함.
  energy_scale_eV_m3 = T_END² * selected_A_energy.
  selected final injected energy = .5 * energy_scale_eV_m3 * eV_J.
  두 birth source columns는 같은 selected-total energy denominator로 정규화된다.

A(W)=Σ_target n_target ∫_[1MeV,4MeV] q_p(K)v_p(K)(dσ_target/dW)dK.
단위: [A]=m^-3 s^-2 eV^-1, [Q_e]=m^-3 s^-1 eV^-1.
따라서 같은 저장 source와 실제 local-ramp 법칙에서
N[a,b]=N_T (b²-a²)/T², U[a,b]=U_T (b²-a²)/T²,
j_N(t)=2N_T t/T², j_U(t)=2U_T t/T².
여기서 N_T,U_T는 저장된 T 시점 source-injected moments이다.
이는 알려진 time law를 사용한 재표현이고 moments에서 history를 만들어낸 것이 아니다.

원 기록의 fullBED/legacy 두 operator realization은 동일 source를 사용한다.
두 source로 합산하지 않는다. 직접 low/high birth tags를 서로 다른 물리 source event로
중복 선언해서도 안 된다. 이는 한 source-event family의 disjoint support partitions다.

저장 source_vectors 같은 실제 원 배열을 취득하면 기존 source-grid measure로 재사용할 수 있다.
정확한 energy grid, ghost/ledger rows, common energy denominator, units와 hash를 결속해야 한다.
새 spectrum을 moments에서 복원하거나 같은 source를 재투영/재정규화하지 않는다.
Raw vectors에서 physical injection을 얻으려면 source code의 실제 dimensional scale을 사용한다.

## 4. Finite injection window와 RR return clock은 서로 다른 대상

Backward transient operator K=-Q이고 reward r가 proper-time hazard일 때
f_infty = K^-1 r,
f_h = ∫_0^h exp(-K a) r da = K^-1[I-exp(-K h)]r.
주입 density column j(s)에 대해
state n'(τ)=-K^T n(τ)+j(τ), n(0)=0,
finite-window return C(T)=∫_0^T j(s)^T f_(T-s) ds.
주입 구간[0,T]의 cohorts가 이후 모두 처리될 때의 eventual return은
C_eventual=∫_0^T j(s)^T f_infty ds.
두 식을 혼동하지 않는다. finite history 확보만으로 f_infty가 finite-time return이 되지 않는다.
K orientation은 실제 stored solver의 row/column convention과 대조해야 한다.

판별 가능한 scalar 예 n'=-kn+j, k>0:
n(T)=j(1-exp(-kT))/k,
C(T)=j[T-(1-exp(-kT))/k],
C_eventual=jT, C_eventual-C(T)=n(T).
T->0에서 C(T)=jkT²/2+O(T³), eventual=jT.
이 예는 arbitrary mean stopping time을 exposure로 대입하는 오류를 판별한다.
conditional mean time은 분포의 1차 moment이며 injection duration/observation horizon이 아니다.

실제 PHYS02 bath100K와 PR107 bath10000K 및 target densities는 다르다.
PHYS02 source를 PR107 operator에 직접 공급하는 물리 transfer/state contract는 현재 미공급.
실제 source moment/spectrum port는 자체 state로 보존하고 PR107 RR gate는
GATED_SOURCE_RECIPIENT_STATE_MISMATCH로 유지하는 것이 물리적으로 일관된다.
병렬 PR108의 finite-age RR 연구도 별도 input/clock/budget 범위로 보존한다.

## 5. Same-state baryon normalization와 baryon injection

n_b가 명시된 같은 donor/recipient state이고 baryon-conserving RR event이면
a=N_cap/n_b,
ΔY_He4II=+a, ΔY_He4III=-a, Δζ=-a,
Δw_nt=-U_e/n_b, Δw_ext=0, ΔlogT=0.
Native index와 energy units는 실제 authoritative native25 contract에서 연결한다.
어떤 donor의 T 또는 n_b를 다른 bath에 대입하지 않는다.

실제 baryon injection이 있으면 n_b 자체가 변한다.
dn_i/dτ+θn_i=R_i,
dn_b/dτ+θn_b=R_B,
Y_i=n_i/n_b -> dY_i/dτ=(R_i-Y_i R_B)/n_b.
Finite same-volume addition:
ΔY_i=(Δn_i-Y_i Δn_b)/(n_b+Δn_b).
따라서 고정 nb의 Δn_i/nb는 baryon-conserving event나 명시적 reference-normalized diagnostic의 식이다.
입사 baryons를 실제 composition evolution으로 바꾸려면 denominator/charge/internal/rest-energy ownership을 함께 제공해야 한다.
현재 actual PHYS02에는 explicit same-state nb가 없으므로 nb/native25는 null로 유지한다.

## 6. Retained photon과 event ownership

He4III+e_fast->He4II(1s)+γ 의 zero-recoil spontaneous ground event:
Δu_fast=-E,
Δu_internal=-I,
Δu_retained_gamma=E+I, I=54.42eV.
합은0. Photon count/energy는 별도 retained port에 둔다.
u_fast removal diagnostic을 total stopped-energy 합에 두 번째로 더하지 않는다.
Photon energy moment E_gamma/N_gamma는 monoenergetic spectrum을 뜻하지 않는다.

External electron/baryon source도 source-event family와 recipient transfer ID를 명시한다.
Donor impact/ionization에서 이미 처리한 binding/recoil/particle changes를 recipient가 다시 event로 세지 않는다.
PHYS02 direct electrons의 kinetic birth port와 donor atomic/proton ledgers는 이 경계를 통해 연결한다.
입사 massive particle rest energy와 kinetic/binding/thermal energy는 별도 quantity다.
Missing retained-photon output은 null; physical zero evidence가 없으면 0으로 채우지 않는다.

## 7. 구현의 필수 판별항

- 같은 immutable source revision/hash/scope와 올바른 state/isotope tags.
- 시간 finite, ordered, domain[0,T] 안; claimed interval 밖 extension 거절.
- raw source가 이미 proper/angle-integrated/target-weighted일 때729,4π,n_target 재적용 거절.
- same event family 중복 fullBED+legacy 및 overlapping support claims 거절.
- source_vectors ledger/ghost rows와 energy scale를 올바르게 분리; reprojection 금지.
- moment-only input에서 spectrum synthesis 거절.
- same-state nb 없으면 native25 null.
- baryon-number-changing event에 fixed-nb physical-update mapping 거절.
- finite source interval과 eventual/finite RR output의 horizon tag를 구분.
- mixed frame, isotope/state remap, support extrapolation 거절.
- retained photon을 w_ext 또는 heating으로 이동 거절.
- 기존 source quadrature/solvers와 병렬 PR108을 재실행하지 않는다.

## 8. 문헌 대조의 사용 범위

SciSpace discovery 이후 Exa에서 원 논문을 확인했다.
Slatyer2013(arXiv1211.0283), §III.2 Eq(4)는 injection-redshift/energy에 대한 history convolution,
§III.3은 delayed deposition을 다룬다.
Slatyer2016(arXiv1506.03812)은 ionization/heating/low-energy photons를 구별하는 transfer outputs를 제공한다.
Liu,Ridgway,Slatyer2019(arXiv1904.09296), §II 및 §III A는 injection과 deposition의 시간 차이,
propagating photons를 다음 timestep에 넘기는 별도 category를 명시한다.
이 문헌들의 cosmology, density, spectrum support, numeric transfer functions는 CR unit에 수입하지 않았다.
우리의 clock/volume/abundance formulas는 위 number measure와 quotient rule로 직접 유도했다.

Exa ar5iv extraction의 Slatyer2013 Eq(5) 설명에서 dV redshift exponent 부호가
후속 식과 일치하지 않는 표현이 보인다. 해당 한 줄은 채택하지 않았다.
고정 comoving cell의 proper volume V_p=a³ V_c에서 Jacobian을 직접 유도하였다.
SciSpace의 원문 duplication과 잘못된 apparent2022 publication dates도 채택하지 않았다.
검색결과의 unrelated TRSM/finite-duration energy relation은 전부 미채택이다.

## 9. Wolfram과 실패 보존

WOLFRAM_CHECK_V1.json: timeConstraint20s, provider CPU unavailable(null).
state ODE, count balance, finite capture formula, event energy, clock-volume count invariance의
다섯 exact residual이0이었다. Baryon quotient residual expression에는
replacement precedence 문제(/.s->0-...)가 있어 의도한 검사를 수행하지 못했다.
이 출력을 물리적 반례로 해석하지 않았다.

WOLFRAM_CHECK_V2_REPAIR.json: timeConstraint5s, provider CPU unavailable(null).
괄호를 교정하여 quotient residual0 및 finite ΔY formula residual0을 얻었다.
첫 호출과 실패 원인·두번째 호출을 모두 보존한다.
이 대수 검산은 actual source numerical validation이나 global physical error certificate가 아니다.

## 10. 상태

derived: source measure conversion, finite moment integration, response-horizon distinction,
same-state abundance mapping, baryon-source denominator correction, RR event energy.
literature-supported: delayed deposition와 propagating photon 별도 category.
symbolically checked: 위 Wolfram의 exact residual7개(첫5+수정2).
unresolved/input-gated: 실제 PHYS02->PR107 same-state transport, explicit nb, finite RR 소비.
global physical completion/error/budget remaining/currency null, L4 false를 유지한다.
Strong no-go의 새로운 성과를 주장하지 않는다.


## 11. 채택한 계산식과 source ledger

원 stored energy source column b_i는 number column이 아니다. S=U*/T_end²로 두면 A_Ni=S*b_i/E_i이고 A_Ei=S*b_i다. cutoff energy와 number는 각각9605/9608행이다. high-born low_cross9609/9610은 existing active projection을 기록한 diagnostics이므로 source 합에서 제외한다. 기존 ionization-counter rows9606/9607은 source에서0임을 실행에서 확인한다. source로 새 chemical event를 추가하지 않는다.

M(a,b)=(b-a)(b+a)/2를 사용하여 N=M*S*(sum b/E+cutoff_N), U_eV=M*S*(sum b+cutoff_E)를 계산한다. 단위는 각각m^-3와eV m^-3이며U_J=eV_J*U_eV다. 여러 segment는 각 proper 시작점의 elapsed time을 사용한다. 일반 degree≤2 polynomial에서 proper rate coefficient는 native c_k*(dt_native/dtau)^(k+1)*(dV_native/dVproper)*n_target(if needed)이다. Timestamp endpoints themselves are explicitly supplied in proper seconds; the Jacobian applies to the polynomial argument and rate measure, not a second time to those endpoints.

유한 시간 window는[0,T],[0,T/2],[T/2,T],[T/3,2T/3],[T(1-10^-6),T],[T,T]로 고정한다. 두 birth tags와total에 대해18개 finite outputs를 만든다. Zero-width intervals have zero integrated count/energy and a qualified left endpoint rate; their instantaneous rates are not obtained by dividing by zero exposure. No mean capture time enters this contract.

RR interface는 적분 source와 state/source/projection/frame/isotope/support/horizon identity가 맞는 공급자 output만 채택한다. Actual PHYS02→PR107은state mismatch라RR와retained port=null이다. Same-state mock RR만 event energy/stoichiometry control에 쓰며 실제 scientific source로 승격하지 않는다. Pure electron kinetic injection alone does not replay the donor's proton/atomic ionization ledger.
