# 외부 분포·주입과 사건 장부의 소비 계약

단위: `CR_EXTERNAL_INTERFACES_20261025_V1`. 현재 가정은 bath frame의 등방적인 이산 에너지 측도, proper volume/proper time, 원자료에 지정된 조건부 동위원소 대응이다. 새 기여는 기존 C23B/C23E 결과를 한 번의 정규화와 공통 사건 extent로 소비하는 실행 가능한 인터페이스다. 새 cross section, rate, 적분 또는 trajectory를 계산하지 않는다.

## 1. 분포와 주입 측도

에너지 좌표 $K$에 대한 유한 분포와 source를 각각

\[
 F_s(dK)=\sum_j N_{sj}\delta_{K_{sj}}(dK),\qquad
 Q_s(dK)=\sum_j q_{sj}\delta_{K_{sj}}(dK)
\]

로 정의한다. $N_{sj}$의 단위는 proper $\mathrm{m}^{-3}$, $q_{sj}$의 단위는 proper $\mathrm{m}^{-3}$ proper $\mathrm{s}^{-1}$이다. 두 객체의 차원과 API가 다르다. 원 CSV의 `number_weight_per_target_s`는 quadrature atom에 이미 적분된 질량이다. 이를 $dK$의 밀도 표본으로 취급해 bin width를 다시 곱하지 않는다. 따라서

\[
 \dot n_s=\sum_j q_{sj},\qquad
 \dot U_{s,\mathrm{kin}}=\epsilon_{\rm eV}\sum_j K_{sj}q_{sj},
 \quad \epsilon_{\rm eV}=1.602176634\times10^{-19}\mathrm{J/eV}.
\]

광자는 total photon energy, 전자·baryon은 kinetic energy와 명시적 rest energy를 사용한다. 대입된 rest energy로 total-energy moment를 별도 계산한다. 이 total-energy moment는 진단값이다. 현재 kinetic/binding 사건 ledger에 rest energy를 다시 더하거나 heating으로 사용하지 않는다. `d^3p`, `dlnK`, invariant phase-space measure, occupation 또는 degeneracy를 암묵적으로 변환하지 않는다. 이 입력에는 해당 Jacobian과 정규화 공급자가 필요하다. 일반적인 외부 분포를 지원하는 타입과, 현재 수치적으로 결속된 C23B scalar source의 범위를 구분한다.

## 2. 정규화는 한 번 적용한다

$dV_p=J_VdV_c$, $d\tau=J_t d\eta$일 때 invariant count를 양쪽 표현으로 쓰면

\[
 Q_p=\frac{Q_c}{J_VJ_t},\qquad
 Q_p=\frac{n_{\rm ref}}{J_t}Q_{\rm ref},\qquad
 Q_p=n_{\rm target}q_{\rm per\ target}.
\]

`Scaling`은 필요한 인수 집합과 실제 인수 집합의 정확한 일치를 요구한다. 이미 volumetric인 source에 target density를 추가하면 거절한다. `normalize`의 반환형은 `ProperSource`이고 이를 다시 정규화할 수 없다. `IntegratedSource`는 constant proper exposure $t$를 곱한 $N_j=tq_j$이며 다시 exposure를 적용하는 API를 제공하지 않는다. 직접 생성자도 배열 길이·유한성·부호·한 번의 scaling과 exposure 동등성을 확인한다. 시간 이력을 입력하지 않은 source에서 임의의 이력 적분은 생성하지 않는다.

## 3. 원자료와 실제 결속

C23B의 source-native ground threshold는 HI/HeI/HeII에 대해 13.60/24.59/54.42 eV이며 photon support는 각 threshold부터 50 keV다. 원 source는

\[
 q_i(K)=\frac{S(K+I_i)\sigma_i(K+I_i)}{
 \epsilon_{\rm eV,erg}(K+I_i)^2},\quad
 S(E)=4\pi\nu J_\nu
\]

를 이미 계산했다. 현재 소비자는 저장된 32,592개 atom을 읽어 3개 $z=2.316,2.479,2.649$와 3개 channel의 SI source로 옮긴다. 새 source quadrature는 0이다. 저장된 per-target count/kinetic moments와의 차이는 새 SI adapter의 검증값이며 원 공급자 전체를 재실행한 수치 인증으로 세지 않는다. 바깥 redshift와 energy support, 유한질량·anisotropic 변환은 별도 admission 대상이다. 조건부 H1/He4 대응은 기존 PR105의 선언된 모형을 사용하며 empirical isotope resolution으로 바꾸지 않는다.

C23E는 18개 저장 point의 90개 signed PI/RR/CX event를 소비한다. 그 source에는 target density와 thermal-electron density가 이미 적용됐다. 따라서 이 경로는 $\mathrm{cm}^{-3}\to\mathrm{m}^{-3}$, $\mathrm{eV}\to\mathrm{J}$ 변환과 사건 표현만 적용한다. 기존 D43K threshold-gated H-equality 및 shared H/D RR moment를 유지한다. C23E의 Case-A photon escape는 PR105의 retained photon reservoir와 다른 owner 계약으로 보존된다. C23E current owner HEAD `8623d7b2035677fc231976d85fea309f48afd57c`의 `FROZEN_CONTRACT.md`와 `POINT_SOURCES.json`은 이번 expansion에 상속된 파일과 byte-identical임을 직접 확인했다.

출처: [C23B source contract](../cr_c23b_source_frame_20261023/source_providers/CONTRACT.json), [C23B 보고서](../cr_c23b_source_frame_20261023/REPORT_KO.md), [C23E frozen contract](../cr_c23e_d43_source_binding_20261024/FROZEN_CONTRACT.md), [C23E 고정 current owner](https://github.com/cosmosapjw-quantum/bass_cr/tree/8623d7b2035677fc231976d85fea309f48afd57c/research/cr_c23e_d43_source_binding_20261024). 개별 입력 SHA256은 `SOURCE_MANIFEST.json`에 둔다.

## 4. 단일 사건 extent와 에너지 소유권

사건 $r$의 비음수 extent를 $\xi_r\,[\mathrm{m}^{-3}\mathrm{s}^{-1}]$, 입자 변화량을 $\nu_{sr}$, signed energy reward를 $u_{ar}$라 하자. 각 핵종·전하 행 $A$에 대해

\[
 A\nu_r=0,\qquad \sum_a u_{ar}=0,\qquad
 \dot n_s=\sum_r\nu_{sr}\xi_r,\quad
 \dot U_a=\sum_r u_{ar}\xi_r.
\]

소비자는 number와 energy에 같은 extent를 사용한다. C23E의 signed net CX는 실제 부호에 맞는 방향의 양수 extent로 표현하고 원 에너지·입자 변화를 그대로 보존한다. `EventBook`은 같은 book 안에서 같은 event ID의 두 번째 추가, 중복 reservoir, mixed frame, 전하·핵종·energy closure 위반을 거절한다. 소비자는 원 event ID를 보존해야 한다. 같은 물리 사건에 새 alias ID를 붙이거나 서로 다른 book에 반복 입력한 것을 이 국소 자료구조가 판별하지는 않는다. 상대 closure 기준은 원 C23E의 $2\times10^{-13}$을 유지한다. 작은 signed 합은 구성 항들의 절댓값 합으로 정규화한다.

직접 PI 사건의 입력 photon energy가 $E_\gamma=I+K$이면

\[
 (\Delta U_\gamma,\Delta U_{\rm bind},\Delta U_{\rm fast},
 \Delta U_{\rm thermal})=(-I-K,+I,+K,0).
\]

이 `0`은 이 stage에서 생성된 전자를 fast pool에 배치한다는 정의다. 물리 heating 완료값을 뜻하는 결과 필드는 `null`이다. photon debit을 늘려 에너지 합만 억지로 맞추더라도 primary 단계에서 full fast kinetic과 full heat를 동시에 소유하면 거절한다. 후속 electron cascade는 이미 생성된 electron budget을 입력으로 가지며 같은 원 photon을 다시 흡수하지 않는다.

RR는 kinetic·binding의 감소와 retained/escaped photon을 별도 처리한다. 태그 전자의 RR hazard에는 capturing ion density를 사용하고, 기존 C23E thermal RR에는 이미 thermal-electron density가 포함돼 있다. 두 rate의 의미를 교환하지 않는다. 이는 각각 [PR105 theory](../cr_n5_rr_milne_20261025/THEORY_KO.md)와 C23E frozen contract의 재사용이다.

## 5. 열용량·입자수·결합·비열적 에너지

열적 상태식 $U_{\rm th}(T,\{n_s\})$에는

\[
 \dot T=\frac{\dot U_{\rm th}-\sum_s
 (\partial U_{\rm th}/\partial n_s)_T\dot n_s}{C_V},
 \qquad C_V=(\partial U_{\rm th}/\partial T)_{n_s}
\]

를 적용한다. `CaloricDerivative`는 $C_V$, 모든 thermal particle-number derivative 및 EOS 출처를 요구한다. binding energy와 fast energy는 이 입력에 포함시키지 않는다. 고전적 monatomic translational energy에 한해서 $U_{\rm th}=3n_{\rm tr}k_BT/2$로 두면

\[
 \dot T=\frac{2\dot U_{\rm th}}{3k_Bn_{\rm tr}}
          -T\frac{\dot n_{\rm tr}}{n_{\rm tr}}.
\]

제조 검산은 이 식의 particle-number 항을 검사한다. 분자·rotational/vibrational·내부 준위가 포함된 전체 heat capacity에는 별도 EOS/준위 공급자가 필요하다. `Species.nuclei`는 핵종 보존을 위한 구성이고 translational particle count를 대신하지 않는다.

`caloric_partition`은 $K\le K_c$와 $K>K_c$의 count/energy만 분리한다. thermal particle transfer와 heating은 `null`, irreversible assimilation은 `false`로 반환한다. 실제 stopping 공급자의 경계 flux를 받는 경우에도 동일 signed $J_c$에

\[
 \dot n_{\rm th}|_c=J_c,\quad \dot U_{\rm th}|_c=K_cJ_c,
 \quad \dot n_{\rm fast}|_c=-J_c,\quad
 \dot U_{\rm fast}|_c=-K_cJ_c
\]

를 적용한다. 경계 역류가 가능하므로 이 항만으로 irreversible assimilation을 판정하지 않는다. [기존 cutoff 유도](../cr_kernel_cutoff_20261013/latex/manuscript.md)와 [thermal evolution](../cr_thermal_evolution_20261012/REPORT_KO.md)을 재사용한다.

## 6. β·cascade·stopping·운동량 의존성

평가된 β 공급에는 isotope/isomer/charge, spectrum, Q, branching, mass convention, parent proper lifetime과 daughter/electron/neutrino/recoil owner가 모두 필요하다. 기존 C23B의 Lorentz/clock 구성은 재사용 가능하지만 mean-line 제조 witness를 실제 spectrum으로 채택하지 않는다. `require_physical_provider`는 공급자의 원파일 및 독립 admission-review pin의 실제 바이트와 범위만 검증한다. 과학적 admission 자체는 그 검토의 선행 결과이며 함수 호출로 만들어지지 않는다. 이번 registry의 미결 β·cascade·stopping 입력은 명시적으로 거절된다.

현재 atom source와 energy ledger의 각도 범위는 isotropic ensemble이다. 개별 photon/capture 사건의 운동량 법칙은 제공하지 않는다. `SCALAR_ENSEMBLE_ONLY`의 energy/charge 검사와 full angular momentum transfer 검증을 분리한다. 임의의 beam·moving target·finite-recoil 입력에는 각도/상대속도/질량 공급자가 필요하다. HE101의 C8 export 및 원 예산 상태를 상속하여 일반적인 stopping/anisotropic kernel 완료로 승격하지 않는다.

## 7. 실제 검증과 남은 의무

`runs/external_interfaces_v1/`의 결과는 다음과 같다.

- 새 인터페이스 제조 controls 26개: PASS.
- 원 C23B atom 32,592개, 9개 source case의 SI 변환·공통 사건 ledger: PASS.
- 원 C23E point 18개, signed event 90개의 SI/owner 변환: PASS. 구성 energy-scale 기준 최대 상대차 $2.1471732382525837\times10^{-16}<2\times10^{-13}$.
- source/rate quadrature, old rate evaluation, ODE, old finite-chain solve: 각각 0.
- 새 bounded 검증 CPU 0.145485309 s, wall 0.145567049 s, peak RSS 25,780 KiB. 과거 PR105/C23E 계보 CPU와 합산하지 않은 별도 unit 비용이다.

확보 상태는 `derived`와 `implementation-verified`이고 새 microphysical validity/전체 열화/전체 heating 검증은 해당 공급자·N6 결합에 남아 있다. N4/N5 `PARTIAL_OPEN`, N6/N7 `PREDECESSOR_GATED`, global completion/error bound `null`을 유지한다. 새로운 no-go 정리나 문헌 신규성 주장은 없다.

## 실행기 예산 이력 보완

최초 v1 source snapshot과 실제 실행 결과를 보존했다. 이후 run_checks.py의 과거 receipt 조회만 수정하여 미완료 run directory를 UNKNOWN_PRIOR_ATTEMPT_BUDGET으로 처리하고 negative/null/NaN/bool 비용을 거절한다. 별도 세 그룹·네 invalid variant의 기계적 검사 CPU는 0.001943521 s이며 과거 source·rate·ODE를 재평가하지 않았다. TARGETED_RUNNER_BUDGET_CHECK.json과 runs/runner_budget_guard_v1/RECEIPT.json을 참조한다. 두 새 검증의 측정 CPU 합은 0.147428830 s이고 과거 계보 예산과 구분한다. 독립 검토는 review/C9_EXTERNAL_INTERFACE.json에 기록한다.

최종 독립 검토는 review/C9_EXTERNAL_INTERFACE.json의 consumed-source 범위 PASS와 review/C9_RUNNER_BUDGET_SUPPLEMENT.json의 실행기 변경 검토 PASS로 구성된다. 최초 실행의 원 wrapper와 최종 budget-guard wrapper를 서로 다른 source identity로 보존했다.
