# 장기 연구 PR 계획

이 문서는 동결된 저장소별 계획의 기계적 조립본이다. 계획을 실행 완료·물리적 승인으로 해석하지 않는다. 각 작업은 원 저자 계약, 소스, 적용 영역, 예산 및 보류 조건을 그대로 따른다. 기존 소유자 브랜치에 합치거나 중복 계산을 시작하지 않는다.

## WU088_HH

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| WU_CE83_OWNER_COMPLETION | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/0` |
| WU_LI_SOURCE_UNCERTAINTY | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/1` |
| WU_HE_LI_CX_STATE_ENERGY | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/2` |
| WU_D_PI_RR_MATCHED | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/3` |
| WU_NUCLEAR_PARTICLE_OWNERSHIP | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/4` |
| WU_SPECTRAL_GEOMETRY_COUPLING | PROPOSED | WU_CE83_OWNER_COMPLETION, WU_HE_LI_CX_STATE_ENERGY, WU_D_PI_RR_MATCHED, WU_NUCLEAR_PARTICLE_OWNERSHIP; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/5` |

## bass_cr

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| CR_N4_C23B_CUTOFF_BINDING | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/0` |
| CR_N4_STOPPING_KERNEL | PROPOSED | CR_N4_C23B_CUTOFF_BINDING; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/1` |
| CR_N5_ATOMIC_ISOTOPE_COVERAGE | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/2` |
| CR_N6_CONSERVATIVE_COUPLING | PROPOSED | CR_N4_STOPPING_KERNEL, CR_N5_ATOMIC_ISOTOPE_COVERAGE; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/3` |
| CR_N7_NEW_PARCEL | PROPOSED | CR_N6_CONSERVATIVE_COUPLING; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/4` |
| CR_BETA_FULL_OWNER | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/5` |

## cosmosapjw-quantum/rec_bianchi

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| REC-LINE02 | OWNER_DELIVERY_PENDING | 내부 없음; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/0` |
| REC-HISTORY | PROPOSED | REC-LINE02; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/1` |
| REC-C3 | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/2` |
| REC-LI | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/3` |
| REC-FIELD | PROPOSED | REC-LINE02; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/4` |
| REC-COUPLED | PROPOSED | REC-LI, REC-FIELD, REC-HISTORY; 외부: []; 조건부: [] | `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/5` |

## cosmosapjw-quantum/BASS_HE

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| HE-X1 | COMPLETE_SCOPED | 내부 없음; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/0` |
| HE-ANG | PROPOSED | HE-X1; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/1` |
| HE-EXCHANGE | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/2` |
| HE-RESERVOIR | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/3` |
| HE-CLOSURE | PROPOSED | HE-ANG, HE-EXCHANGE, HE-RESERVOIR; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/4` |
| HE-FEEDBACK | PROPOSED | HE-CLOSURE; 외부: []; 조건부: [] | `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/5` |

## cosmosapjw-quantum/bass

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| B1-G1B-recover | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `numerics/BASS_CONTRACTS.json/nodes/0` |
| B2-G1B-curved | PROPOSED | B1-G1B-recover; 외부: []; 조건부: [] | `numerics/BASS_CONTRACTS.json/nodes/1` |
| B3-fourforce-owner | PROPOSED | B2-G1B-curved; 외부: []; 조건부: [] | `numerics/BASS_CONTRACTS.json/nodes/2` |
| B4-production-restart | PROPOSED | B3-fourforce-owner; 외부: []; 조건부: [] | `numerics/BASS_CONTRACTS.json/nodes/3` |
| B5-domain-validation | PROPOSED | B2-G1B-curved, B3-fourforce-owner, B4-production-restart; 외부: []; 조건부: [] | `numerics/BASS_CONTRACTS.json/nodes/4` |

## cosmosapjw-quantum/vigilode

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| V1-affine-native | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `numerics/VIGILODE_CONTRACTS.json/nodes/0` |
| V2-session-fatal | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `numerics/VIGILODE_CONTRACTS.json/nodes/1` |
| V3-affine-quotient | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `numerics/VIGILODE_CONTRACTS.json/nodes/2` |
| V4-causal-polynomial | PROPOSED | 내부 없음; 외부: []; 조건부: [] | `numerics/VIGILODE_CONTRACTS.json/nodes/3` |
| V5-sphere-production | PROPOSED | V1-affine-native, V2-session-fatal, V4-causal-polynomial; 외부: []; 조건부: [] | `numerics/VIGILODE_CONTRACTS.json/nodes/4` |

## cosmosapjw-quantum/rei_bianchi

| 노드 | 계획 상태 | 선행 노드 | 계약 |
|---|---|---|---|
| REI-L0 | PROPOSED | 내부 없음; 외부: ["external:ANGTHERM01@6daf382ee698835e7a141378c232d1d97c1c5cf1", "external:X1_HE38_ANGULAR_PSD_REVIEW"]; 조건부: [] | `rei/CONTRACTS.json/nodes/0` |
| REI-L1 | PROPOSED | REI-L0; 외부: ["external:BASS_CR_C23B_PHYSICAL_SOURCE", "external:WU088_HH_SOURCE_MOMENTS", "external:REC_SELECTED_LINE_OR_COMPTON_PROVIDER"]; 조건부: [] | `rei/CONTRACTS.json/nodes/1` |
| REI-L2 | PROPOSED | 내부 없음; 외부: ["external:C3_ZERO_TINY_SOURCE", "external:LOCALFLOW@9620e1fcc4bdda76e0311206f614234926600381", "external:PHYSICAL_BETA_DAUGHTER_AND_STOPPING_PROVIDER"]; 조건부: [] | `rei/CONTRACTS.json/nodes/2` |
| REI-L3 | PROPOSED | 내부 없음; 외부: ["external:BASS_HE_FINITE_MASS_TRANSPORT", "external:X1_HE38_ANGULAR_PSD_REVIEW", "external:BASS_MASSIVE_COMPONENT_MAP"]; 조건부: [] | `rei/CONTRACTS.json/nodes/3` |
| REI-L4 | PROPOSED | REI-L0, REI-L1; 외부: ["external:BASS_GEOMETRY_FEEDBACK", "external:VIGILODE_NUMERICAL_HOOKS"]; 조건부: [{"condition": "nonzero_n_or_T", "dependency": "REI-L2", "external": false}, {"condition": "anisotropic_baryons", "dependency": "REI-L3", "external": false}, {"condition": "ANGTHERM02_accuracy_claim", "dependency": "external:ANGTHERM02_OWNER_ADMISSION", "external": true}] | `rei/CONTRACTS.json/nodes/4` |
| REI-L5 | PROPOSED | REI-L4; 외부: []; 조건부: [] | `rei/CONTRACTS.json/nodes/5` |

## 저장소 간 조건부 연결

이 표는 채널 선택에 따른 선행 조건이다. 모든 공급자를 동시에 요구하는 AND 조건으로 해석하지 않는다.

| 공급 노드 | 소비 노드 | 적용 조건 | 주장 한계 |
|---|---|---|---|
| HE-X1 | REI-L0 | using angular-moment injection | Necessary PSD/moment-cone gate only; does not supply angular distribution or physical cross section |
| HE-ANG | REI-L3 | selecting anisotropic baryonic scattering transport | Source-qualified angular moments needed; event frequency is not l2 transport |
| HE-EXCHANGE | REI-L3 | selecting finite-mass baryonic pressure exchange | Momentum/energy and pair symmetry from supported physical model |
| HE-CLOSURE | REI-L4 | selecting nonzero baryonic anisotropic stress | Isotropic pi_b=0 minimal pilot does not require this extension |
| CR_N4_STOPPING_KERNEL | REI-L1 | claiming thermalization of supplied fast photoelectrons | Without provider, energy remains explicitly nonthermal; no instant heat |
| CR_N6_CONSERVATIVE_COUPLING | REI-L4 | selecting CR coupled radiation/deposition pathway | Source and gas use same event measure and valid domain |
| WU_D_PI_RR_MATCHED | REI-L1 | claiming isotope-specific D PI/RR number and energy moments | Equal-electronic isotope approximation remains distinct smaller model |
| WU_NUCLEAR_PARTICLE_OWNERSHIP | REI-L2 | activating nuclear daughters/fast products | Branch normalization, charge and energy carriers explicit |
| CR_BETA_FULL_OWNER | REI-L2 | activating source-qualified beta partition and stopping | One beta owner; total Q not all heat |
| REC-LINE02 | REI-L1 | selecting native line source | Consume completed owner result only; active owner reservation remains |
| REC-LINE02 | WU_SPECTRAL_GEOMETRY_COUPLING | selecting native line in WU spectral coupling | One native line owner; no detached/native double counting |
| REC-FIELD | REI-L1 | selecting actual spectral radiation/Compton exchange | Planck and actual-monopole baths remain distinct |
| B3-fourforce-owner | REI-L4 | selecting BASS four-force geometry feedback adapter | Closed sum of sectors in matching frame/clock; signed stresses retained |
| B2-G1B-curved | REI-L5 | claiming curved Bianchi smooth-source domain | Not a prerequisite to all LRS selected flat pilots |
| V1-affine-native | REI-L4 | using native reduced30/full33 affine adaptive client | Actual full physical norm and inherited scales; other validated solvers remain available |
| V2-session-fatal | REI-L4 | using switching/restart driver | Accepted-state transactional semantics and all costs preserved |
| V5-sphere-production | REI-L5 | claiming its physical spherical transport scheme | Joint number/energy remap and source-appropriate stability; not all selected-model pilots |

```json
{
  "rule": "Requirements are AND within the selected model, not AND over every physical provider or numerical option.",
  "REI_L1": "Choose and bind exactly the channels the model activates. Original external donor list is a provider menu; each source is required only if its channel/domain claim is selected.",
  "REI_L4": "Always L0+one completed selected L1 pair+compatible validated geometry/solver. L2/L3/Li owner are conditional extensions. No requirement to complete all7 repositories before bounded safe algebra."
}
```
