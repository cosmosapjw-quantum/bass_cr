# C23B photoelectron atoms와 KC atomic cutoff의 결속

## 결과와 범위

C23B의 저장된 양의 quadrature measure를 **고정 source predictor가 만든 electron count inventory**로 변환하면, KC4/TCF.36–40의 유한 atomic prefix 분할을 그대로 적용할 수 있다. 실제 cutoff는 \(K_c=\chi k_BT\), \(\chi\ge3/2\)이고, threshold equality는 thermal 쪽에 배정한다. 이 변환은 source의 수·운동에너지 모멘트와 원자 반응의 charge·nucleus·binding ledger를 보존한다.

이번 결과는 원 source bytes와 명시된 고정 source exposure, 이상기체 caloric closure에 대한 구성이다. 저장된 spectrum을 재구적하지 않는다. 저에너지 stopping rate, Maxwellianization 시간, secondary cascade와 실제 thermal heating의 승인에는 별도 충돌·열교환 근거가 필요하다. 이 보고서의 \(T_{\rm cal}\)은 분할과 EOS가 정의하는 caloric diagnostic이다. 원 C21O의 prescribed T를 소급하여 교정하는 값으로 쓰지 않는다.

**EXECUTION:** 새 결속 유도 및 Wolfram 항등식 7개 PASS; KC 및 C23B 완료 계산 재실행 0.  
**PUBLICATION:** 본 문서가 root의 C23C 배송본에 합류할 후보이며, 이 문서 자체에는 게시 ACK가 없다.  
**BACKUP:** root 배송 단계에 합류; provider 최종 상태는 root authority가 담당한다.  
**DAG:** CR_N4_C23B_CUTOFF_BINDING의 이론 계약; 물리 stopping 및 완전 thermal closure는 후속 의무.

## 1. 실제로 읽고 재사용한 원본

- KC science anchor: bass_cr commit **a5c29ad4070acb931d92d2bec42a927a57f479ca**.
- 원본: research/cr_kernel_cutoff_20261013/.
- 선택한 11개 파일, 148,122 bytes의 실제 Git blob SHA1/size를 모두 검사했다. 원본 byte identity는 reuse_kc/FETCH_MANIFEST_VERIFIED.json에 있다.
- 직접 사용할 엔진: thermal_cutoff_solver.py의 Atom, AtomicInventory, construct_atomic_root, enumerate_atomic_roots 및 명시적 fixed-spectrum energy continuation.
- C23B source: source_providers/runs/c23b_pw19_spectral_source_20261023_v1/photoelectron_atoms.csv. 생산 실행 identity 277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955.
- 저장 atom 표의 열은 redshift, channel, kinetic_eV, number_weight_per_target_s다. source_providers/spectral_photo_source.py와 THEORY_AND_RESULTS_KO.md에서 **bath frame stationary target, target 하나당 proper second**임을 확인했다.
- 3개 epoch z=2.316,2.479,2.649는 서로 다른 scenario다. 한 inventory에 서로 다른 epoch의 atoms를 합치지 않는다.
- fit-label source channel HI,HeI,HeII와 explicit five populations HI,HII,HeI,HeII,HeIII를 사용한다. 원 isotope-resolved 21 populations에 대한 mapping은 별도 OPEN이다.

| 기존 결과 | 이번 사용 |
|---|---|
| KC1 실제 PHYS02C event kernel | 원본 근거 보존. photoionization의 새로운 source column은 아래 직접 결속한다. |
| KC2 cold-target stopping 및 density derivative | 이번 source-only adapter에서는 사용하지 않는다. finite-T stopping의 공급자가 아니다. |
| KC3 continuous EOS certificate | finite atomic source에는 직접 적용하지 않는다. 원자 crossing에서 고전적 density derivative를 가정하지 않는다. |
| KC4 finite atomic branch | \(\chi\ge3/2\), 양의 base inventory, thermal equality 조건을 충족하여 직접 재사용한다. |
| KC5 공변 moving-boundary flux | 원본 근거 보존. 이번 proper-time finite source와 ledger의 convention을 맞춘다. 미분 수송 실행은 없다. |
| KC6 coupled contraction | descriptor self-map 및 q<1을 새로 입증하지 않았으므로 이번 coupling의 유일성 주장으로 사용하지 않는다. |
| KC7 exact reference | atomic reference code를 byte-pinned 재사용한다. 새 입력의 검증 결과는 C23C 실행에 귀속한다. |

## 2. rate measure에서 count measure로

각 source channel \(i\)의 C23B 저장 측도를

\[
dQ_i(K)=\sum_j q_{ij}\delta_{K_{ij}}(dK),
\qquad q_{ij}>0,\quad K_{ij}\ge0
\tag{B1}
\]

라 쓰자. \(q_{ij}\)는 target\(^{-1}\) proper s\(^{-1}\), \(K_{ij}\)는 eV다. 이는 저장된 양의 구적 측도이며, 실제 원자선 spectrum을 delta 함수들로 측정했다는 뜻은 아니다.

현재 stage의 proper volume \(V>0\), 명시적 target proper density \(n_i\ge0\), proper time exposure \(\Delta\tau\ge0\)를 고정한다. count \(N_i=Vn_i\)를 입력하는 동등한 API도 가능하다. 새 source packet count는

\[
n_{ij}=N_i\Delta\tau\,q_{ij}=Vn_i\Delta\tau\,q_{ij}.
\tag{B2}
\]

두 표현에서 volume을 한 번만 곱한다. coordinate/conformal time을 바로 넣는 경우 필요한 \(d\tau/d\eta\) 변환을 명시해야 한다. C23B source는 이미 bath frame이므로 추가 boost나 parent lifetime factor를 곱하지 않는다.

채널별 사건수와 새 electron number·kinetic energy는

\[
S_i=\sum_j n_{ij},\quad
S=\sum_iS_i,\quad
E_s=\sum_{ij}K_{ij}n_{ij}.
\tag{B3}
\]

이것은 고정 source를 이용한 1차 explicit predictor다. 모든 흡수 target inventory에 대해 \(\Delta\tau\Gamma_i\le1\), \(\Gamma_i=\sum_jq_{ij}\)를 확인하면 기존 target에서 요구한 사건수가 그 target 수를 넘지 않는다. 한 시간 단계 안에서 새로 생성된 HeII를 다시 HeIII source target으로 재사용하지 않는 frozen-target contract다. 이 구성이 큰 노출시간의 결합 helium kinetics에 대한 exact solution이라는 주장은 하지 않는다. 실제 허용오차와 물리 시간 절단오차는 후속 integration 계약이다.

## 3. charge·nucleus·binding 장부

B3의 동일 사건수를 모든 장부에 사용한다.

\[
\begin{array}{lll}
\Delta N_{\rm HI}=-S_{\rm HI},&
\Delta N_{\rm HII}=S_{\rm HI},\\
\Delta N_{\rm HeI}=-S_{\rm HeI},&
\Delta N_{\rm HeII}=S_{\rm HeI}-S_{\rm HeII},&
\Delta N_{\rm HeIII}=S_{\rm HeII}.
\end{array}
\tag{B4}
\]

수소·헬륨 nuclei 각각의 총수는 그대로이고, ion charge 증가는

\[
\Delta(N_{\rm HII}+N_{\rm HeII}+2N_{\rm HeIII})
=S_{\rm HI}+S_{\rm HeI}+S_{\rm HeII}=S.
\tag{B5}
\]

모든 새 electron은 initially resolved count measure에 들어간다. 양의 charge balance는 thermal과 active의 합을 사용한다.

채택 source fit threshold \(I_i=(13.60,24.59,54.42)\) eV를 사용하면

\[
\Delta E_{\rm bind}=\sum_i I_iS_i,\qquad
E_{\gamma,\rm abs}=\sum_{ij}(I_i+K_{ij})n_{ij}
=\Delta E_{\rm bind}+E_s .
\tag{B6}
\]

이 threshold는 C23B Verner fit convention이다. 다른 isotope의 정확한 ionization energy로 재해석하지 않는다. radiation은 외부 공급량을 기록하는 owner 또는 transported photon reservoir에서 차감하는 owner 중 하나만 갖는다. cutoff 재분할은 binding energy와 radiation 장부를 바꾸지 않는다.

## 4. 새 electron을 base에 중복으로 넣지 않는 공통 inventory

기존 unresolved thermal count를

\[
N_B=N_{\rm nuc}+N_{e,B}\ge N_{\rm nuc}>0,\qquad U_B>0
\tag{B7}
\]

로 둔다. charge-neutral 초기 five-population fixture에서는 \(N_{e,B}=N_{\rm HII}+N_{\rm HeII}+2N_{\rm HeIII}\)다. 별도 charged reservoir 또는 기존 resolved electrons가 있으면 그것의 소유권과 charge를 추가로 명시해야 한다.

초기 source-free fixture의 base energy는 \(U_B=(3/2)k_BTN_B\)로 만들 수 있다. 이미 resolved lower/upper atoms가 있는 상태에서는 base에서 그 atoms의 count·energy를 먼저 제외한다. 이번 단순 source-only coupling은 기존 resolved measure를 0으로 선언한 fixture 또는 명시적으로 공급한 기존 measure에서 시작한다.

기존 measure를 \(\mu_0\), source measure를 \(\mu_s=\sum n_{ij}\delta_{K_{ij}}\)라 하면,

\[
\mu^+=\mu_0+\mu_s,\qquad
{\cal C}^+={\cal C}^0+S,\qquad
{\cal E}_{\rm kin}^+={\cal E}_{\rm kin}^0+E_s.
\tag{B8}
\]

따라서

\[
{\cal C}^+-\mu^+_0=N_B,\qquad
{\cal E}_{\rm kin}^+-\mu^+_1=U_B.
\tag{B9}
\]

여기서 \(\mu_0,\mu_1\) 아래첨자는 문맥상 모멘트이며 초기 measure의 superscript와 구분한다. 새 source electron을 resolved measure에 넣으면서 \(N_B\)에도 더하면 총 electron count를 중복한다. 새 kinetic energy를 source atoms와 \(U_B\)에 동시에 넣는 경우도 같은 오류다.

## 5. threshold ownership과 caloric branch

에너지가 같은 atoms를 합친 뒤

\[
\mu^+=\sum_{j=1}^{M}n_j\delta_{K_j},\qquad
0\le K_1<\cdots<K_M
\tag{B10}
\]

로 정렬한다. 아래쪽 prefix \(j\le k\)가 thermal이면

\[
N_k=N_B+\sum_{j\le k}n_j,\qquad
U_k=U_B+\sum_{j\le k}K_jn_j,\qquad
T_k=\frac{2U_k}{3k_BN_k}.
\tag{B11}
\]

consistent branch의 조건은

\[
K_k\le \chi k_BT_k<K_{k+1}.
\tag{B12}
\]

끝쪽 부등식은 빈 prefix/full prefix에서 각각 생략한다. thermal이 equality를 소유하므로 active는 strict \(K>K_c\)다. KC4의 finite forward construction은 \(\chi\ge3/2\)에서 양의 consistent branch를 반환한다. 모든 consistent branches를 열거할 수도 있으나 uniqueness는 자동으로 성립하지 않는다. 새 source로 spectrum 자체가 바뀐 경우와 고정 spectrum의 pure base-energy continuation은 다른 계약이다.

어느 branch에서나

\[
N_{\rm th}+N_{\rm active}={\cal C}^+,\qquad
U_{\rm th}+E_{\rm active}={\cal E}_{\rm kin}^+
\tag{B13}
\]

다. thermal count에는 nuclei가 들어간다. electron-only ownership은 \(N_{e,\rm th}=N_{e,B}+\sum_{j\le k}n_j\)와 \(N_{e,\rm active}=\sum_{j>k}n_j\)로 따로 확인한다.

reference cutoff \(c_0\)와 새 cutoff \(c_1\)의 finite transfer는 해당 retained atoms의 signed difference다.

\[
\Delta N=\sum_jn_j
  \bigl({\bf1}_{K_j\le c_1}-{\bf1}_{K_j\le c_0}\bigr),\quad
\Delta U=\sum_jK_jn_j
  \bigl({\bf1}_{K_j\le c_1}-{\bf1}_{K_j\le c_0}\bigr).
\tag{B14}
\]

일반적으로 \(\Delta U\ne c_1\Delta N\)다. 아래로 돌아갈 경로가 있으면 thermal로 배정된 resolved atoms도 보존한다. 합계 두 모멘트만 보존하고 lower atoms를 삭제하면 역분할에 필요한 spectrum 정보가 사라진다.

## 6. kinetic assignment와 온도 반응

기존 base가 \(U_B=(3/2)k_BT_0N_B\)이고 thermal prefix 모멘트를 \(L_N,L_E\)라 하면, B11에서 직접

\[
T_{\rm cal}-T_0
=\frac{L_E-\frac32 k_BT_0L_N}
       {\frac32 k_B(N_B+L_N)}
\tag{B15}
\]

를 얻는다. \(L_E>0\) 자체로 \(T_{\rm cal}>T_0\)가 정해지지 않는다. 추가한 electron의 평균 운동에너지와 기존 입자당 thermal kinetic energy를 함께 비교해야 한다. 이 조건부 caloric 식은 새 electron number를 EOS에 포함하는 이유를 드러낸다.

C23B의 FS contraction lower edge 10 eV는 secondary deposition table의 지원 범위다. B12의 \(\chi k_BT\)와 별개다. cutoff below/above에 대한 count·energy partition이 계산되었다는 사실은 physical stopping/thermalization 또는 FS-domain extension을 승인하지 않는다. thermal_heating와 stopping_time은 별도 physical supplier가 결속되기 전까지 null이다.

## 7. exact arithmetic의 범위와 최소 검증

C23B CSV 문자열을 Fraction으로 읽으면 저장된 decimal representation의 유리수 측도에 대한 B2–B15가 exact하다. 이것은 원 spectrum·fit·구적의 물리적 오차가 0이라는 뜻이 아니다. 초기 eV 단위 그대로 구현할 때 \(k_B^{\rm eV/K}=k_B^{\rm J/K}/\epsilon_{\rm eV}^{\rm J/eV}\)를 명시한다. SI의 \(k_B=1.380649\times10^{-23}\) J/K와 \(\epsilon_{\rm eV}=1.602176634\times10^{-19}\) J/eV는 여기서 정확한 decimal constants로 표현할 수 있다. Joule 경로를 택하면 source energy에 \(\epsilon_{\rm eV}\)를 한 번 곱한다.

C23C의 독립 검증은 다음 구체적 위험을 다룬다.

1. 원 CSV SHA/size와 source epoch·channel·frame·단위 contract를 확인한다.
2. rate→count에서 target, volume, proper time이 각각 한 번만 반영되는지 확인한다.
3. 새 electron이 base와 resolved atoms에 중복 배정되지 않는지 B9 및 charge ledger로 확인한다.
4. raw decimal atoms의 직접 prefix sum과 구현 output의 count/energy를 대조한다.
5. equality, duplicate energy grouping, zero exposure, forbidden \(\chi<3/2\), 부족한 target inventory를 검증한다.
6. 선택 branch의 B12와 모든 branch의 B13을 확인한다. unique-root 또는 C_eff certificate를 암묵적으로 붙이지 않는다.
7. source가 없는 h=0 케이스에서는 주어진 consistent branch를 보존하는 경로를 사용한다. arbitrary source-change에서 old branch continuation의 조건을 자동 적용하지 않는다.
8. saved atomic source의 count/energy와 FS support의 overlapping classification을 보존하고, physical heating output은 null로 유지한다.

Wolfram 실행 evidence/check_new_binding.wl 및 WOLFRAM_BINDING_RESULT.json은 B5,B9,B13,B15에 해당하는 항등식 7개를 실제로 평가하여 모두 0을 반환했다. 이 실행은 C23C 새 결속의 scalar algebra 확인이며 과거 KC suite의 재실행이 아니다. source table나 코드의 실행 검증은 root의 별도 C23C run record에 귀속한다.

## 8. 다음 physical stopping 계약을 위한 문헌 인계

Exa 실제 호출은 402 credits limit으로 실패했다. 같은 호출을 반복하지 않았다. SciSpace 검색은 성공하여 finite-temperature Fokker–Planck thermalization 문헌 후보를 반환했다. 후보 중 Allred, Alaoui, Kowalski, Kerr (2020), DOI10.3847/1538-4357/abb239, arXiv2008.10671의 원 abstract와 저자 code solarFP/FP의 README·license metadata를 확인했다. FP는 momentum/pitch-angle diffusion을 포함하는 solar flare transport code이며 Apache-2.0로 표시된다. 이번 cutoff 계산에는 그 코드나 rate를 도입하지 않았다.

차기 stopping 구현에는 원 논문의 실제 finite-T coefficients, 코드 snapshot, 약결합 Coulomb log와 Maxwellian bath의 적용 조건, isotropic/energy-coordinate 변환, zero-flux equilibrium, thermal reservoir와의 반대 부호 energy exchange를 읽고 결속한다. 현재 조회한 abstract만으로 finite-T 또는 sub-eV atomic stopping coverage를 승인하지 않는다. neutral elastic/excitation, molecular/inelastic, escape, actual isotope composition의 coverage도 별도 공급자와 유효범위를 필요로 한다.

Primary pointers:

- https://arxiv.org/abs/2008.10671
- https://doi.org/10.3847/1538-4357/abb239
- https://github.com/solarFP/FP

검색·원 페이지 원 응답은 evidence/에 보존했다. numeric stopping rates, physical thermalization times와 global error bound는 아직 미정이다. **global_error_bound=null**.

