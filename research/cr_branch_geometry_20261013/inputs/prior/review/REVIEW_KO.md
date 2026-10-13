# BASS_CR kernel–cutoff 연구 루프 독립 심사

연구 단위: CR-THEORY-KERNEL-CUTOFF-20261013  
심사자: /root/feedback_literature_review  
판정: **PROMOTE_SCOPED / PASS — KC1–KC7**

실제 PHYS02C/PHYS02B kernel의 양의 사건 표현, 고정 inventory의 온도 의존 cutoff 해법, 공변 경계 source, 두 단계를 연결하는 조건부 feedback bound를 채택한다. 아래의 전제와 exact candidate snapshot이 이 판정의 범위를 정한다. 원자 kernel 전체의 시간 진화나 모든 branch를 통과하는 실제 coupled solver의 실행 결과를 이번 판정에 포함하지 않는다. 다음 구성 대상은 그 coupled solver와 기하학적 에너지 변화 이후의 kernel 재결속이다.

## 1. 심사 독립성과 근거 경계

심사자는 후보 유도·구현·검사 설계에 참여하지 않았다. Kernel 후보는 /root/feedback_event_construction, cutoff 후보는 /root/feedback_fixed_point, 공변 경계와 coupled bound는 /root가 작성했다. 심사자는 SciSpace와 Exa를 이용한 좁은 원전 비교를 먼저 수행한 뒤, 실제 후보 식·코드·입력·원 실행 출력을 읽고 독립적으로 대수, 미분, 부호, 단위와 branch 조건을 확인했다.

이번 심사에서 과학 프로그램이나 기존 suite를 다시 실행하지 않았다. 수행한 로컬 확인은 파일 읽기, JSON의 기록 대조, SHA256 및 Git blob identity 확인이다. 후보 저자의 수치 검사는 구현 연결의 근거로 읽었으며, 유한 표본을 일반 정리의 증명으로 사용하지 않았다.

승인된 FB1–FB7은 입력·전제·버전의 동일성을 확인해 재사용했다. inputs/PRIOR_REUSE.json의 19개 복사 기록은 모두 현재 bytes 및 SHA256과 맞는다. 이 중 이전 candidate manifest에 직접 결속된 과학 파일은 11개이고, 나머지는 provenance·후속 metadata 또는 이전에 승인된 nested 유도다. matches_frozen_science=false는 그 파일이 이전 25-file candidate 목록에 들어 있지 않다는 표시이며, 현재 bytes 불일치라는 뜻으로 사용하지 않는다.

## 2. 채택한 주장과 실제 적용 조건

| 주장 | 채택 결과 | 심사에 사용한 조건과 근거 |
|---|---|---|
| KC1 | 저장된 실제 energy grid와 HI/HeI BED, 선택된 CCC/stopping을 양의 공통 사건 열로 표현한다. 같은 parent와 target family의 sharing 분포도 capacity 적용 뒤 유지된다. | KA.5–18, KA.25–29; 실제 source의 projector·sharing·generator를 직접 대조했다. Saved grid gap이 binding 및 excitation cost보다 작아 parent 재투영이 생기지 않는다. |
| KC2 | 실제 target-count feedback와 thermal electron bath의 stopping derivative bound를 연결한다. | KA.13, KA.19–24, KA.28. 고정 parent energy, 양의 Coulomb log, 지정한 cold-target 모형, 초기 양의 target support를 사용한다. |
| KC3 | 고정 common inventory에서 연속 cutoff의 signed count/energy 이동, 유일 EOS root 및 잔차·자료 오차의 온도 증명서를 얻는다. | TCF.2–35. 양의 온도 bracket, 유한 spectral moments, 연속 또는 bounded piecewise-continuous density, bracket 부호와 C_eff≥m>0가 필요하다. h=0 및 시간 미분은 일관된 predictor와 명시된 정칙성에 따른다. |
| KC4 | 유한 원자 spectrum의 모든 branch를 열거하고, χ≥3/2에서 존재 scan과 inherited energy continuation을 유한하게 수행한다. | TCF.36–46. Thermal이 equality를 소유하며 base count와 energy가 양수다. 순수 energy continuation에서는 atom energies·weights 및 base count를 고정한다. |
| KC5 | 움직이는 경계의 수 source와 운동에너지 source를 공변 식으로 연결한다. | CV.1–10. 선언한 spectral balance, trace, endpoint flux 조건과 공행 전자 수 전류 closure를 사용한다. 여섯 xAct residual은 매끄러운 곱 법칙·수축의 실제 근거다. |
| KC6 | 실제 사건 moment imbalance에서 coupled temperature/density/ion-fraction gain과 inner/outer 잔차 bound를 얻는다. | CP.1–15. 동일 descriptor self-map, uniform root bracket, m>0, q<1. 연속 표현은 trial z에 독립인 고정 선형 재구성이며, 원자 표현은 하나의 admitted prefix branch에 머문다. |
| KC7 | 두 reference 구현과 실제 에너지 사건·연속 및 원자 예제가 위 식에 맞게 연결된다. | Kernel source 및 세 focused check source를 읽고, 실제 JSON output과 실행 identity를 대조했다. 구성한 시험 inventory와 저장된 과거 물리 spectrum은 구별한다. |

CONTRACT의 A1–A10, THERMAL_CUTOFF_ASSUMPTIONS의 TC-A1–TC-A10, 각 유도에 명시된 세부 조건을 함께 읽는다. 각 행이 다른 행의 적용 조건을 지우거나 자동 충족시키지는 않는다.

## 3. 실제 kernel과 보존 사건의 심사

### 3.1 Source identity와 coordinate 대응

inputs/KERNEL_SOURCE_BINDING.json의 11개 복원 source는 모두 기록된 길이·SHA256·Git blob SHA-1과 일치한다. 저장된 NPZ의 energy_eV field identity는 source-bound 실행이 확인했으며, 새 mesh나 전체 generator 생성은 수행하지 않았다. 심사자는 실제 causal_cascade.py의 project, _sharing, _generator, stopping_eV_s, excitation_sigma와 coherent_bed.py의 Ionization 정의를 읽었다.

원래 projector는 전자 count의 convex 분배를 active energy coordinate로 반환한다. KA.5–6은 이를 count coordinate로 정확히 옮긴다.

\[
\sum_i b_i+n_B=1,\qquad \sum_i W_i b_i+u_B=w.
\]

W≤W_b daughter는 실제 w를 absorber energy에 넣고, W_b와 첫 node 사이의 보간에는 W_b ghost fraction을 사용한다. 두 경우의 count/energy가 별도 출력에 남는다. source의 heat와 cutoff_energy는 물리 U_B에 한 번만 합치며, ion-stage chemical energy로 센 binding을 다시 더하지 않는다. Low-cross observers도 기존 energy의 겹치는 관측량으로 유지한다.

원래 u_j=E_j A_j/V coordinate에 사건 열을 되돌리면 각 parent의 -rate와 rate×projector/E_j, binding/radiation/heat observers가 _generator의 실제 조립식과 같다. 원래 저장 행렬의 T_END factor를 나눈 physical generator를 비교한다는 점도 맞다.

### 3.2 Positivity, paired daughters와 sharing 보존

두 daughter를 한 사건에 함께 넣으면 자유전자 increment는 1이고, kinetic·thermal·binding 합의 increment는 0이다. Excitation과 stopping은 자유전자 합의 increment가 0이다. 각 사건에서 nuclei·charge·energy row가 0이므로 같은 extent를 곱한 모든 후보 상태가 같은 invariant를 유지한다.

BED 양성성의 핵심 변형은

\[
y^2+r^2-\frac{y+r}{t+1}=(y-r)^2+yr>0
\]

이다. HI oscillator의 양성성과 He polynomial의 감소·양의 최솟값을 실제 source 상수와 대조했다. Total BED의 나머지 함수 H(t)는 H(1)=0 및 양의 H′(t)를 갖는다. 양의 quadrature weights를 정규화한 sharing probability와 원래 total rate의 곱은 채택한 source의 분포를 보존한다.

공통 capacity map의 donor load는 모든 사건을 함께 합친 c_i이다. 각 donor를 쓰는 사건의 분모에는 c_i/y_i^n가 포함되므로 총 순소모가 초기 stock을 넘지 않는다. 초기 zero donor와 inactive parent를 끄는 규칙도 코드에 반영됐다.

KA.29는 별도로 확인했다. 실제 최대 grid gap 0.6325633326908928 eV는 최소 binding 13.6057 eV보다 작다. 따라서 parent j의 ion daughters는 E_{j-1}보다 낮고, 모든 sharing 사건의 negative coordinates가 A_j와 해당 X_a의 각 1로 같다. 같은 parent–target family에서는 분모가 sharing index에 독립이어서

\[
\xi_{ja\ell}=p_{ja\ell}\Xi_{ja}
\]

가 성립한다. 실제 세 sharing samples의 identical donor columns·denominator·extent/probability ratio가 이를 구현에서 확인한다. 일반 결론은 grid inequality와 사건 열의 증명에서 얻으며, 세 sample 수만으로 전체 family를 추정하지 않는다.

### 3.3 Rate와 단위

Atomic proposal은 초기 parent count와 고정 donor mask에 trial neutral density를 곱한다. Excitation neutral은 effective closure에서 net increment가 0이므로 가상의 depletion을 capacity에 추가하지 않는다.

Stopping은 실제 bath density n_e=N_e,thermal/V를 사용한다. 두 Coulomb log의 n 의존성이 공통 -½ log n이어서, 고정 energy에서 최소 branch의 선택이 density에 따라 바뀌지 않는다. 따라서 b=αnL, b′=α(L-½), b″=-α/(2n) 및 endpoint derivative bound가 맞다. 여기서 b의 단위는 eV/s, λ=b/ΔE는 1/s다. 문서는 elementary charge e(C)와 energy conversion ε_eV(J/eV)를 구별한다. 코드가 재사용한 SI 상수의 수치 동일성을 단위 동일성으로 해석하지 않는다.

Fixed-energy rates의 직접적인 T derivative는 이 cold-target source에서 0이다. Thermal ownership이 변해서 n_e가 바뀌는 간접 의존성은 별도로 포함한다. χ≥3/2는 cutoff branch 존재 조건이며 cold-target 정확도의 대체 기준으로 사용하지 않는다.

## 4. 온도 의존 cutoff와 root certificate의 심사

### 4.1 고정 inventory와 정확한 유효 열용량

모든 inner 후보는 같은 C, E, μ_h에서 다시 계산한다. N=C-A_N(c), U=E-A_E(c)이므로 cutoff를 올리거나 내릴 때 수와 실제 에너지의 signed 적분이 함께 움직인다. 이전 후보의 transfer를 다음 후보에 누적하지 않는다. Retained atoms를 raw A_j와 thermal aggregate 양쪽에 중복 계산하지 않는 인터페이스가 명시돼 있다.

연속 branch에서 직접 미분하면

\[
N_T=\alpha\rho(c),\quad U_T=\alpha c\rho(c),\quad
F_T=c_vN+\alpha(c_vT-c)\rho(c)=C_{\rm eff}.
\]

χ≤3/2일 때의 충분한 양의 하한과 χ>3/2일 때 density bound가 필요한 이유가 이 식에서 바로 나온다. Bracket 부호와 C_eff≥m>0는 존재·유일성을 준다. Bounded piecewise-continuous spectrum에서는 F가 절대연속이고 derivative 하한을 거의 모든 점에서 사용한다.

Off-root Picard derivative와 root에만 유효한 축약식을 구별했다. q<1과 self-map은 전체 bracket에서 확인해야 한다. Exact fixture의 q=233/243과 별도 이분법 선택은 일관된다.

### 4.2 계산된 오차와 시간 미분

| 오차 종류 | 채택한 온도 bound |
|---|---|
| Exact endpoint의 algebraic residual | \(|F(\widehat T)|/m\) |
| Bracket만 사용할 때 | \(\max(\widehat T-a,b-\widehat T)\); 중점에서는 \((b-a)/2\) |
| Residual 평가오차 η_F | \((|\widehat F|+\eta_F)/m\) |
| 고정 inventory·tail 자료 오차 | \(\{c_vT_+(|\delta C|+\sup|\delta A_N|)+|\delta E|+\sup|\delta A_E|\}/m\) |

두 spectrum의 total moments가 같아도 cutoff-tail moments가 같다고 결론내리지 않는다. Exact Fraction fixture의 평가오차 0은 그 유리수 표현의 성질이다.

h=0 identity는 reference EOS와 초기 cutoff 일치에서 나온다. C¹ predictor는 올바른 첫 미분과 o(h)를 주며, O(h²)는 추가 정칙성을 요구한다. 양쪽 trace가 다르면 상대 흐름 부호와 선택 upwind trace가 고정된 branch에서 implicit coefficient를 읽도록 보충됐다. Comoving count에는 volume dilution을 중복하지 않고 thermal energy에는 -2θU/3 work를 유지한다.

### 4.3 실제 이분법 코드

Finite box 사이에서는 F_T가 affine이므로 density knots로 나눈 구간의 양 끝 one-sided 값을 확인하는 derivative_lower_bound가 유효하다. 겹치는 positive boxes는 density 합으로 다룬다. Immutable input에서 매 후보의 count와 energy를 재구성하고, 양의 bracket·base inventory·slope 및 endpoint signs를 검사한다.

Solver는 reference root를 먼저 확인하므로 h=0 identity를 보존한다. 최대 반복 후에는 현재 후보와 유효한 bracket/residual certificate를 MAX_ITERATIONS로 반환한다. 마지막 interval을 더 좁힐 수 있는 경우에도 반환한 기존 bracket이 계속 유효하므로 certificate는 보수적으로 유지된다.

## 5. 원자 branch의 심사

각 distinct-energy prefix의 유일 후보 온도는

\[
T_k=\frac{U_B+\sum_{j\le k}w_j n_j}
{c_v(N_B+\sum_{j\le k}n_j)}
\]

이며 admissibility는 w_k≤αT_k<w_{k+1}이다. 따라서 M+1개 prefix를 계산하면 전체 root set을 얻는다. Equality는 thermal에 배정한다.

χ≥3/2에서 next atom을 포함한 온도는 이전 T와 w/c_v의 양의 가중평균이다. 두 값 모두 w/α 이상이므로 새 lower-threshold 조건이 보존된다. Index가 유한하게 증가한다는 증명에는 온도의 단조증가가 필요하지 않다.

고정 spectrum·base count에서 base energy만 바꾸는 continuation은 heating에서는 높은 atom을 포함하고, cooling에서는 조건을 어긴 가장 높은 thermal atom을 제거한다. Cooling 제거식의 부호는 음수이며 U_B>0 덕분에 양의 에너지가 남는다. h=0에서는 inherited consistent index를 그대로 반환한다.

코드의 grouping, zero-weight omission, prefix sum, equality 조건, root enumeration과 continuation 경로가 이 증명과 맞는다. 실제 다중-root fixture에서 0,1,2 세 branch를 모두 반환하고, zero update는 k=0 existence policy로 바꾸지 않고 supplied branch를 유지한다. χ>3/2 crossing의 유한 온도 jump는 smooth C_eff 및 C¹ 시간 정리의 적용 경계를 정확히 드러낸다.

## 6. 공변 경계와 coupled bound의 심사

CV.1의 spectral balance에서 이동 상한을 미분하면 S_c=j_c^a∇_aE_c-ℱ_c이다. Lower energy moment의 부분적분은 bulk ∫ℱ dW와 경계 E_cS_c를 분리한다. Upper partition에서는 반대 부호가 생긴다. 무한 endpoint에서 Wℱ→0 조건을 추가해 높은 에너지 쪽 부분적분 끝항도 정당화했다.

Metric (-,+,+,+), J_e^a=cn_en^a를 사용하면 rest-mass tensor를 뺀 scalar contraction이 정확히 m_ec²∇_aJ_e^a를 뺀다. Boundary spatial momentum이 있어도 n·h=0이므로 rest-mass-subtracted thermal source는 E_cS_c다. 이 scalar closure를 임의의 tilted current에 확대하지 않는다.

CP.2의 연속 재구성은 trial z에 독립인 고정 선형 basis로 한정됐다. 고정 T에서 두 후보의 F 차를 구하고 한쪽 root에서 C_eff≥m을 적용하면, classical coefficient derivative 없이도

\[
|\mathcal T(z)-\mathcal T(w)|
\le \frac{\sum_r\sup_I|\nu_{U,r}-c_vT\nu_{N,r}|M_r}{m}
\|z-w\|_a
\]

가 나온다. 이 finite-difference proof는 Lipschitz-only 자료에도 적용된다.

Number descriptor에는 고정-T 사건 moment 차와 이동 상한의 αρ_max|δT|를 더한다. Ion fractions는 고정 nucleus denominator를 사용한다. 양의 고정 척도에서 q<1과 closed self-map이 함께 있으면 유일 endpoint와 Picard 수렴이 따른다. Inner temperature가 같은 admitted bracket에 있을 때 residual/m을 descriptor error로 옮기고, approximate-map residual에 더한 CP.15도 맞다.

이 판정은 CP의 계산 가능한 조건부 정리를 채택한다. 실제 9600-node 모든 반응으로 q<1·self-map을 구성하여 coupled endpoint를 계산하는 일은 다음 DAG의 CR_THEORY_COUPLED_BRANCH_SOLVER가 맡는다. 원자 threshold를 넘는 경로는 별도 branch 선택을 갖추어야 한다.

## 7. 실제 실행 근거의 집계

| 근거 | 실제 관측 | 채택 범위 |
|---|---|---|
| Kernel event checks | 17 event columns × 4 invariant rows, exact residual 0; 4 ionization·4 excitation·3 stopping component 기록 | Source-bound projection와 새로운 event wiring |
| Sparse capacity witness | 7 events, 모든 state 비음수, 4 invariant 변화 0; 최대 h c_i/y_i^n 약 3.06525×10⁷ | 큰 h의 positivity/보존; 시간 정확도 판단은 별도 |
| KA.29 dedicated check | 실제 HI 30.00977 eV의 3 sharing sample에서 동일 donor·분모·ξ/p | Grid-gap 일반 증명의 구현 연결 |
| Thermal driver | 2 check groups PASS; heating 37회, cooling 39회 이분; zero-step 0회; 유효 certificate ≤10⁻¹² | 무차원 τ=T/T_*의 finite-box 해법 및 atomic prefix 경로 |
| Wolfram scalar | 17 zero groups / 21 scalar zeros, 5 quantified inequalities True | 실제 기호 대수·fixture 부등식 |
| Wolfram+xAct | 6 zero groups / 6 scalar zeros | 선언한 abstract tensor 곱 법칙·수축 |
| Symbolic 합계 | **23 zero groups / 27 scalar zeros + 5 inequalities = 28 groups** | 이전 loop의 25-scalar 집계와 구별 |

온도 tolerance 10⁻¹²는 thermal fixture의 무차원 τ 오차다. Kelvin 오차는 T_*를 곱한다. Sparse kernel witness의 103.81591145887886 K는 구성한 큰-step inventory의 EOS이며 저장된 physical history 예측값으로 채택하지 않는다.

Kernel event layer는 저장된 float source 입력을 exact binary rational로 읽고 fast daughter·barycentric weights·sharing normalization을 exact하게 완성한다. 원래 floating projector와의 최대 scale-normalized 차이는 8.41719×10⁻¹⁴이며, 이 수치 비교와 exact invariant 증명은 별개의 근거다.

### 실행 관측의 처리

WolframContext의 MCP -32603 오류는 보조 context discovery에서 발생했다. 실제 Wolfram Language 계산과 xAct 로딩은 성공했다. xCore/xPerm/xTensor의 공식 package SHA256을 먼저 확인했으며, 지원되는 Wolfram backend를 선택한 $xpermQ=False 상태가 출력에 남는다.

첫 scalar attempt의 21 algebraic residual은 모두 0이었으나 inline D를 ForAll 안에 둔 두 inequality가 False였다. Diagnostic에서 precomputed derivative와 명시적 literal derivative는 True이고 endpoint 값도 정확했다. Derivative를 quantifier 밖에서 계산하도록 해당 구문만 수정한 canonical batch가 다섯 inequality를 모두 True로 반환했다. 이전 attempt와 diagnostic을 보존하며 이 관측을 이론의 반례로 분류하지 않는다.

Retained kernel main run의 정확한 UTC는 포착되지 않았다. KERNEL_ADAPTER_EXECUTION.json은 이를 null/unknown으로 표시하고 실제 exit 0, current source/result hashes, 기록 시 관측 runtime을 구별한다. Dedicated sharing 및 thermal checks는 자체 UTC와 source hashes를 기록한다. 심사에서 timestamp를 mtime으로 추정하지 않았다.

## 8. 수정 항목과 closure

| ID | 대상 → 관측 근거 | 영향 → 최소 교정 | 상태 |
|---|---|---|---|
| CV-R1 | CV §1의 F(∞)=0만으로는 upper first-moment endpoint를 제거할 수 없었다. | 에너지 부분적분에 필요한 lim W F(W)=0을 추가하거나 endpoint source를 유지하도록 수정했다. | CLOSED |
| CP-R1 | Atomic branch 설명에 존재하지 않는 TEMPERATURE_CUTOFF_KO.md가 쓰였다. | 실제 THERMAL_CUTOFF_FEEDBACK_KO.md로 참조를 교정했다. | CLOSED |
| CP-R2 | Continuous moment coefficients가 trial-independent이어야 CP.2 및 gain 분자가 고정된다. | 고정 선형 z-independent basis를 명시하고 adaptive basis의 추가 응답을 구별했다. | CLOSED |
| CP-R3 | Lipschitz-only 계수에 classical implicit derivative만 제시하면 설명이 부족했다. | 고정 T_w에서 root perturbation을 취하는 finite-difference 증명을 보충했다. | CLOSED |
| TC-R1 | 양쪽 trace가 다른 경우 implicit coefficient의 branch 선택이 필요했다. | Relative-flow sign과 upwind trace를 고정한 branch에서 읽도록 명시했다. | CLOSED |
| KA-R1 | 초안의 한국어 이중부정 및 U≥0에서 T>0라는 문장이 식과 맞지 않았다. | 비음수 표현으로 고치고 T>0에는 U>0를 요구했다. | CLOSED |
| KA-R2 | Elementary charge와 eV→J conversion의 같은 SI 수치가 동일 차원의 기호처럼 쓰였다. | e(C)와 ε_eV(J/eV)를 분리했다. | CLOSED |
| META-R1 | KC1 family 표현, KC7 section 참조, KC6의 continuous basis 전제를 metadata와 일치시킬 필요가 있었다. | Same parent–target family, KA §10, fixed linear basis 조건을 claim/contract에 결속한 최종 snapshot을 확인했다. | CLOSED |
| DAG-R1 | 초안의 최상위 prior DAG 보존 기록이 이전 thermal-stage identity를 가리켰다. | 현재 feedback-stage SHA 9fdeca1b…와 33→35 nodes, 60→65 edges, 31 unchanged nodes로 갱신하고 이전 묶음을 historical origin으로 보존한 것을 확인했다. | CLOSED |

과학적 수정은 해당 문단과 영향 있는 코드·원 출력만 재검토했다. 변경되지 않은 이전 scientific suite는 심사 중 재실행하지 않았다.

## 9. Overformalization watchdog

| 대상 | 관측 근거 | 과학적 영향과 최소 행동 |
|---|---|---|
| 사건 열 S와 공유 extent | 실제 9600 grid, paired BED daughters, source generator의 coordinate 변환, 17 exact columns에 연결된다. | 추상 표기만 남지 않는다. Kernel/source binding을 그대로 유지한다. |
| C_eff의 명칭 | 이전 MC35에 같은 계수가 있다. 이번에는 finite EOS의 실제 derivative, root certificate, coupled gain의 denominator로 쓰인다. | 재사용과 새 유도를 구별한다. 기존 경계 계수를 새 발견으로 중복 계상하지 않는다. |
| 공변 tensor 표기 | Ec S_c thermal source 및 rest-mass ledger로 내려오는 명시적 수축식과 실제 xAct 출력이 있다. | 현재 observer/current closure에 결속한다. 범위 밖 tilted tensor closure를 의무에 추가하지 않는다. |
| Positivity·moments와 물리 분포 | 동일 0차·1차 moments는 임의의 lower trace를 정하지 않는다. 실제 source absorber도 두 집계값만 보존한다. | 하향 경로에 retained inventory, 선택한 재구성, 또는 명시한 cutoff domain을 사용한다. |
| 문서와 검사 수 | 새 event adapter, finite root driver, 실제 symbolic 실행이 산출돼 있다. | 상태 파일의 수를 성과로 사용하지 않고 위 구성과 오차 bound를 결과로 채택한다. |
| 미완성 응용의 범위 | 실제 coupled self-map과 crossing policy, geometry 후 energy rebind가 다음 DAG에 구체적으로 있다. | 이미 완결된 조건부 정리를 유지하고 해당 새 입력·구성만 다음 단계로 진행한다. |

Lower-trace 경계는 독립적으로도 간단히 확인할 수 있다. 무차원 W∈[0,2]에서 p(W)=6W²−12W+4는 ∫p=∫Wp=0이지만 p(1)=−2다. 0<ε<1/4이면 ρ₀=1과 ρ₁=1+εp는 둘 다 양수이고 같은 count·energy를 갖지만 cutoff W=1의 trace가 다르다. 이것은 두 moments만으로 trace를 복원하는 입력이 부족함을 확인하는 작은 심사 예이며, 추가 closure나 retained atoms를 사용하는 구성 전체를 배제하는 새 no-go 성과로 계상하지 않는다.

## 10. NG1–NG7 screening

이번 candidate는 새 전역 불가능성·배제 정리를 주장하지 않는다. 아래 일곱 기준은 부정적 scope 문장을 과장하지 않았는지와 constructive 결과의 실제 내용을 확인하는 데 적용했다.

| 기준 | 실제 심사 결과 |
|---|---|
| NG1: 정확한 대상·조건·양화 | Atomic roots는 유한 positive measure와 prefix 부등식으로 정해진다. Trace 입력의 부족은 두 moments만 제공한 경우로 한정한다. 다른 kinetic closure 전체에 대한 배제 양화가 없다. |
| NG2: 완결된 증명 | 사건별 moments, root derivative와 monotonicity, atomic weighted-average/제거식, 공변 부분적분, coupled finite-difference bound를 각각 확인했다. |
| NG3: 비자명성·기초 모델 | 실제 pinned source와 별도의 positive continuous/atomic inventories가 있다. 조건을 정의만으로 반복하거나 숨긴 모순을 성공으로 처리하지 않는다. |
| NG4: 구체적인 장애 기작 | Atomic threshold jump는 유한 packet count가 EOS에 들어가는 식에서 나오고, lower-trace 비결정성은 moment 정보 소실에서 나온다. 실행환경 오류는 물리적 장애로 사용하지 않는다. |
| NG5: 과학적 귀결 | Continuous bracket solver, retained-atom branch solver, coupled fixed-prefix domain을 각각 선택하는 계산 경로가 구체적이다. |
| NG6: 원전 비교와 범위 | 네 가까운 primary sources의 실제 section을 읽었다. 양의 grid redistribution·두 daughter moments·thermal transfer와 비교하되 sharp Ec(T) 정리를 원전에서 가져왔다고 주장하지 않는다. 전역 novelty 판정은 하지 않는다. |
| NG7: 독립 검토 | 후보 비저자인 별도 심사자가 식·원 source·raw 출력과 적용 조건을 확인했다. 주장하지 않은 global sharpness나 필요충분조건을 추가 gate로 만들지 않는다. |

**새 strong no-go 채택 수: 0.** 원자 다중 roots와 discontinuous crossing은 구성의 branch 정보로 보존한다.

## 11. 원전과 새 유도의 관계

LITERATURE_KO.md와 SOURCES.json에는 검색 질문·검색일·read URL·실제로 읽은 식/절·원 응답 hashes가 있다. 네 원전의 역할은 다음과 같다.

| 원전 | 실제 비교한 내용 | 이번 후보와의 관계 |
|---|---|---|
| Le–Cambier, 2017, DOI 10.1063/1.4998242 | Electron-impact ionization의 두 daughter source와 별도 density/energy bin moments; III.3 및 V | Count와 energy를 함께 표현해야 하는 선행 문맥. Polynomial positivity나 그 linearized solver의 보편적 exact finite-step 정리를 가져오지 않는다. |
| Mijin 등, SOL-KiT, DOI 10.1016/j.cpc.2020.107600 | §3.6 두 moment constraints와 bracketing absorber weights | 양의 보존 grid redistribution의 가까운 비교. 논문의 lowest-cell secondary 근사는 현재 differential paired BED와 구별한다. |
| Ricketson 등, 2014, DOI 10.1016/j.jcp.2014.04.059 | §3–4 및 §6의 Maxwellian/kinetic split, entropy 기준, moment-matched thermal update | 보존 transfer와 분포 근사오차를 분리하는 문맥. Sharp temperature-dependent cutoff root theorem은 이번 직접 유도다. |
| Singleton–Brown, 2008, DOI 10.1088/0741-3335/50/12/124016 | §I 및 III의 thermalized-particle energy와 source solution | 열화된 입자의 잔여 thermal energy 소유권 비교. Prescribed common background T의 결과를 evolving EOS 증명으로 가져오지 않는다. |

## 12. 다음 소비자와 동결 규칙

다음 연구는 실제 kernel output의 atom weights·lower trace를 포함해 한 threshold-separated coupled domain의 self-map, q와 residual budget을 계산하고, 반응으로 spectrum이 바뀌는 crossing에서 branch 선택을 구성한다. 병렬 후속은 prescribed geometry 이후의 현재 parent/daughter energies와 rate domain을 다시 결속하는 것이다.

현재 source의 0.1 eV 이하 absorber를 역분류하려면 lower energy trace를 추가 보존하거나 cutoff domain을 제한한다. 전체 27 raw CCC tables의 production adapter와 finite-temperature·추가 HeII/recombination rates는 선택한 응용이 요구할 때 원 source를 별도로 결속한다. 실제 scenario·observable budget과 physical time error는 이 조건부 이론의 응용 입력이다.

동결 대상과 SHA256은 review/CANDIDATE_MANIFEST.json에 기록한다. Science·source·raw evidence는 exact bytes로 동결한다. CONTRACT/CLAIMS의 심사 당시 원문은 review/candidate_metadata에 보존하고, 최상위의 사후 수용 status 및 review_reference만 갱신할 수 있도록 normalized scientific-body hash를 별도로 둔다. 수식·가정·scope·evidence 목록의 변경은 이 허용에 포함되지 않는다. 보고서·PDF·DAG·출판 기록은 이 심사 결과를 소비하는 산출물이며 별도의 사후 binding으로 연결한다.
