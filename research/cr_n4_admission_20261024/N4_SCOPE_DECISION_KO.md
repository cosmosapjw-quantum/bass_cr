# CR_N4_C23B_CUTOFF_BINDING — 기존 완료 결과의 수신과 소비자 범위

## 이번 결정

사용자가 지정한 2026-10-23 고정 인계의 N4 connector는 이후 C23C에서 구현·검증·게시되었다. 현재 PR98의 실제 HEAD는 `910a9a92e4bf5a9d77b6ff60365d94559f54cbbd`다. 이번 단위는 이 결과를 원 인계의 입력·정리 가정·출력·소비자 gate에 대응시키고 중앙 DAG의 해당 wrapper를 갱신한다. 기존 source quadrature, KC 정리 검산, C23C 18-case sweep과 독립 C9를 다시 실행하지 않는다. stopping 물리는 `CR_N4_STOPPING_KERNEL`의 별도 노드로 유지한다.

- Frozen handoff: rei_bianchi `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, `research/orchestration_longterm_20261023/assembly/HANDOFF_bass_cr_KO.md`.
- 원 저자 계약: `atomic/LONGTERM_CONTRACTS.json`, `/nodes/bass_cr/0`. 원문의 OPEN/NOT_RUN과 budget null은 당시 snapshot으로 보존한다.
- C23C science C: `54c2ff11e8308d45c545679301059bc1fcf268eb`.
- C23C documents D: `6c760dc1f0ce5820263b276fa7263e87c1285bd2`.
- C23C terminal E: `910a9a92e4bf5a9d77b6ff60365d94559f54cbbd`.
- C23C path: `research/cr_c23c_stopping_coverage_20261023/`.
- 이번 요청의 실행 규약: 사용자가 첨부한 physmath-research-loop 내장 1.0.0. 기존 C23C의 1.3.0 실행 provenance는 그대로 남긴다.

## 식에서 실제 소비자까지의 대응

고정 source는 `inputs/photoelectron_atoms.csv`의 32,592개 저장 quadrature atoms다. 크기는 1,681,578 bytes, SHA256은 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`이다. 각 source channel HI/HeI/HeII의 q_ij는 absorbing target 하나당 proper second의 양의 가중치, K_ij는 bath-frame eV다. 이 CSV는 같은 이름의 임의 source를 허용하는 template가 아니라 byte-pinned 공급자다. Source 실행 identity `277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955`와 이후 guarded source identity를 구분한다.

\[
Q_e(dK)=\sum_i n_i\sum_j q_{ij}\delta_{K_{ij}}(dK),\qquad
\mu_s(dK)=V\Delta\tau\,Q_e(dK),\qquad
n_{ij}=N_i\Delta\tau q_{ij}.
\]

Q_e는 proper volume당 proper time당 전자수 측도다. 소비자가 넘기는 \(\mu_s\)는 유한 기대 전자수 측도다. V와 proper exposure는 각각 한 번만 곱한다. Density 또는 fixed-reference abundance 입력을 하나만 사용하고 두 표현을 동시에 제공하면 거절한다. 이미 bath frame인 source에 boost나 parent lifetime factor를 추가하지 않는다.

실제 API는 `implementation/source_cutoff_binding.py::SavedSupplier`와 `bind`다. Named consumer는 `C23C_FROZEN_FIVE_LABEL_CALORIC_V1`이며, HI/HII/HeI/HeII/HeIII를 모두 명시한 frozen-target source predictor와 caloric partition이다. 실제 실행 entrypoint는 `implementation/run_binding.py`, 완료 run은 `runs/c23c_source_cutoff_binding_20261023_v1`이다. N6 coupled RHS, IGM thermal history, full21 rate provider를 이 이름으로 대신하지 않는다.

## 기존 KC4 가정의 충족

기존 KC source는 bass_cr `a5c29ad4070acb931d92d2bec42a927a57f479ca`다. `implementation/vendor/thermal_cutoff_solver.py`는 원 KC reference의 17,393 bytes를 재사용하며 SHA256은 `427ccb65c8f11d5cbe2035415f2f45abeaca6b23aa818027a09152b2cbfe67f0`이다.

정규화된 초기 population이 비음수이고 총 핵수 \(N_{\rm nuc}>0\)이면,

\[
N_{e,0}=N_{\rm HII}+N_{\rm HeII}+2N_{\rm HeIII}\ge0,
\quad N_B=N_{\rm nuc}+N_{e,0}\ge N_{\rm nuc}>0.
\]

T0>0과 정확한 양의 k_B를 사용해 \(U_B=(3/2)k_BT_0N_B>0\)를 구성한다. 저장된 source는 유한 지지와 유한 양의 가중치를 갖고 V>0, \(\Delta\tau\ge0\)이므로 새 count measure도 유한·비음수다. \(\chi\ge3/2\)는 API에서 검사한다. 이 조건에서 KC4의 fresh-inventory forward construction을 재사용한다. KC3 연속 C_eff certificate, KC6 contraction/uniqueness 또는 source가 달라진 상태에서의 고정-spectrum branch continuation은 이 소비자의 승인 근거가 아니다.

초기 자유전자는 charge-neutral thermal reservoir, 초기 resolved nonthermal measure는 0으로 명시한다. 처음 존재한 target만 source에 쓰며 같은 노출에서 생성된 daughter는 다시 처리하지 않는다. 점유된 target의 \(\Delta\tau\Gamma_i\le1\) 및 최종 population 비음성을 검사한다. 이 검사는 source-time discretization error bound를 제공하지 않는다.

## Atomic endpoint와 에너지 소유권

원 인계의 \(\int_{K_c}^{\infty}\) 표기는 유한 원자 측도에서 endpoint 소유권을 지정해야 한다. 기존 C23C B12와 실제 코드는 다음을 사용한다.

\[
\mu_{\rm th}=\mu|_{[0,K_c]},\qquad
\mu_{\rm active}=\mu|_{(K_c,\infty)},\qquad K_c=\chi k_BT_{\rm cal}.
\]

따라서 원 인계의 Nth와 Uth는

\[
N_{\rm th}=N_{\rm nuc}+N_{e,\rm all}-\mu((K_c,\infty)),
\qquad
U_{\rm th}=U_{\rm all,kin}-\int_{(K_c,\infty)}K\,\mu(dK)
\]

에 대응한다. 여기서 \(U_{\rm all,kin}=U_B+\int K\mu_s(dK)\)는 병진 kinetic inventory다. Binding·radiation·escape energy를 이 항에 섞지 않는다. 동일 event count가 ion charge +1, free electron +1, source threshold에 따른 binding 공급을 결정한다. 새 source를 resolved measure와 base thermal inventory에 중복 합산하지 않는다.

원 인계의 미분 EOS

\[
dT=\frac{2\,dU_{\rm th}}{3k_BN_{\rm th}}-\frac{T\,dN_{\rm th}}{N_{\rm th}}
\]

는 EOS의 smooth variation에 대한 항등식이다. 이번 atomic 소비자의 실제 계산은 저장된 atoms를 유지한 유한 분할과

\[
\Delta T_{\rm cal}=\frac{L_E-\frac32 k_BT_0L_N}{\frac32 k_B(N_B+L_N)}
\]

이다. Atomic crossing의 전역 smooth density derivative를 새로 계산한 것으로 취급하지 않는다. FS 10 eV 하한 및 9,937.21 eV 상한은 source-table 지원 구간이며 Kc와 독립적으로 분류한다. 분류의 count/energy 보존은 physical deposition의 승인이 아니다.

## 조건부 API 정의역과 실제 수치 승인 집합

API의 조건부 정의역은 세 epoch z=2.316/2.479/2.649 각각, 양의 T0, chi>=3/2, 위 명시적 bath와 source 가정이다. 다른 epoch 보간, 기존 resolved nonthermal inventory, 임의 전자 charge reservoir는 이 API에 포함되지 않는다. 입력 누락은 BLOCKED_MISSING_BATH_OR_SOURCE_CONTRACT로 반환하며 unknown top-level field는 현재 guarded source에서 거절한다.

실제 수치 승인 집합은 저장된 **18개 요청**으로 고정한다: 세 z × T0=(100,10000,50000) K × chi=(3/2,3), V=1 cm^3, proper duration=10^10 s, density=(0.9,0.1,0.07,0.02,0.01) cm^-3 순서 HI/HII/HeI/HeII/HeIII. API의 모든 연속 입력에 대한 수치 campaign 완료로 확대하지 않는다.

18개 요청의 13개 exact rational residual, 독립 raw-CSV Decimal80 audit의 977개 비교와 최대 상대차 1.2507493130458459e-78, 기준 1e-40, 기존 equality/normalization/input guard 근거를 그대로 재사용한다. Main 실행 source identity는 `c6174a7a78247a1ee89dfeb152444ba49e2094004926bfe0597eb613e30b7faf`다. 현재 guarded binding SHA256 `acedb6e893f08dc1207c6fc40a63af0f4d21480cbf226e0266b6d8f81b883401`와 과거 실행 v1을 구분하며, guard 교정의 5개 targeted 검사와 old18-unaffected 판정을 연결한다. 이번 연구 결과의 수치를 새로 계산하지 않는다.

## 판정과 다음 실행

N4 wrapper는 COMPLETE_SCOPED로 갱신할 수 있다. Gate trajectory의 DERIVED_SCOPED, IMPLEMENTATION_VERIFIED, NUMERICALLY_CHECKED_SCOPED는 기존 C23C 근거를 재사용한다. CONSUMER_ADMITTED의 대상은 위 named consumer와 저장된 18개 입력이다. 구조 검사나 해시 일치를 과학적 수용의 대체 근거로 쓰지 않는다. 새로운 독립 검토는 이 수신 대응과 중앙 wrapper diff의 범위에 한정한다.

원 atomic 계약 40개와 authority 7개, integration edge 17개, 나머지 wrapper를 유지한다. 중앙 assemble.py 전체 재생성은 기존 HE-X1 완료 상태를 되돌릴 수 있으므로 사용하지 않는다. N4 wrapper의 observed_completion과 scoped consumer admission만 추가한다. 고정 handoff에는 별도 현재 수신 section을 추가할 수 있으며 원 계약 본문은 유지한다.

PASS 뒤의 다음 물리 실행은 **별도** CR_N4_STOPPING_KERNEL: finite-T collision/thermal-exchange supplier, 유효 T/E 및 composition, count/energy 공통 boundary flux, escape와 t_stop/t_evolution의 계약을 먼저 구성한다. CR_N5_ATOMIC_ISOTOPE_COVERAGE는 actual rate/energy-moment/isotope domain을 확보하는 병렬 OPEN 노드다. N6 coupling/N7 new parcel은 해당 선행 gate를 따른다. 이번 단위에서 stopping implementation·rate·새 ODE를 실행하지 않는다.

## 예산·보존·범위

기존 C23C의 9개 distinct run/source snapshot과 실제 비용을 그대로 이어받고 과학·검토·그림/전송 비용을 구분한다. 확인된 부분 비용은 합계의 범위를 표시하며, 전체 inherited spend/remaining/currency의 null을 0으로 바꾸지 않는다. 이번 새 scientific execution, source quadrature, empirical rate evaluation, ODE, historical replay는 모두0이다.

Main316 payload, documents17 payload, terminal bytes를 실제 Library 사본에서 해시·크기·ZIP CRC/member identity로 복원했다. 기존 Dropbox R3는 producer evidence를 재사용하고 현재 main metadata를 확인했다. 기존 Drive main은 이번 exact-name/folder 조회도0건이므로 UNKNOWN_NO_ACK를 유지한다. 이번 새 수신 패키지는 별도 create-only object로 백업하며 각 provider의 실제 응답과 달성 tier를 기록한다.

Non-tilted LRS/full Frobenius, signed stress와 norm/cancellation 구분, isotropic atomic gas와 별도 nonbaryonic Vlasov 범위를 유지한다. physical_heating, stopping_time, global_error_bound, 전체 목표 완료율은 null이다. Full nuclear high-energy/general triaxial·tilted·polarized CMB는 HOLD다. 원 nuclear-network PNG는 NOT_RECOVERED_NOT_READ다. 다른 대화 전체는 UNAVAILABLE이며 외부 runtime process/lease는 UNOBSERVED다.
