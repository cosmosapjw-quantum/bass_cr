# C2 식–코드–입출력 연결

이 문서는 현재 코드의 정적 연결표다. Source/implementation import, array sum, science worker 또는 control 실행은 하지 않았다. 아래 control ID는 실제 `implementation/controls.py`에서 읽은 예정 검증 항목이며 PASS 결과가 아니다. 실행·수용과 최신 C1/C2 preflight·게시는 root가 소유한다.

## 고정한 파일과 source

이론 `THEORY_KO.md` SHA256 `591396d2d49c549f4f67de590ffc8365ae0b12c95581c5cfb3c1d94e501da6ad`와 R6의 두 CLOSED finding을 사용한다. 이전 source snapshot은 `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`, 실제 consumer `REV`는 D=`ec463db0c7e5c7fb5070796071c926caa4db6445`다. 원 Git 경로 세 code files의 두 revision·retained bytes 일치는 R6에 보존했다. 최초 source 생성/원 실행 commit을4ca5라고 단정하지 않는다.

| 읽은 현재 파일 | SHA256 |
|---|---|
| `implementation/ports.py` | `717308252ab86bb4583377eb1a34608339e3fa79576ff397a59f1d57ff6c8a67` |
| `implementation/controls.py` | `bbbc89cccda00194a50a370fb45d80773f90ca94b9b1725935e2a91ff037e779` |
| `implementation/consume_phys02.py` | `f7626cc1dbca38b7592909b01ddd692ec1b00d8314b702f63441890f74cb5336` |
| `implementation/run_bounded.py` | `bbebe14b69c8d2b9afbc5d54ea6a14a4953d0d33e6c70fb2346e10f640c07d8e` |

변경된 의존성은 새 hash와 해당 연결만 갱신한다. 기존 source science를 다시 실행하는 근거로 쓰지 않는다.

## 식과 함수 대응

| 이론 / 계산식 | 현재 함수·producer | 입력 → 출력 field | 코드에서 확인한 control / 후속 확인 |
|---|---|---|---|
| §1 immutable source·species·frame·support | `validate_source`, `verify_payload`, `validate_source_event` | `source.revision/payload_sha256/evidence_kind`, `particle`, `medium`, `support_eV`, `source_event` | `unfrozen_revision`, `electron_isotope`, `no_frame`, `support_extension`, `bin_support_extension`; actual consumer의 NPZ/array hash assertions |
| §1/§11 `j=q_nat*c_tau*c_V*n_target`, `c'_k=c_k*c_tau^(k+1)*c_V*n_target` | `normalize_to_proper`, `_validate_proper` | normalization의 두 Jacobian·target mode → `applied_tokens`, `raw_input`, `raw_source_digest` | `clock_argument_and_rate_each_once`, `clock_energy_same_factor`, `repeat_normalization`, `changed_proper_coefficients`, `duplicate_clock`, `duplicate_volume`, `duplicate_target_density`, `forged_applied_token` |
| §3/§11 `S=Ustar/T²`, `A_Ni=S*b_i/E_i`, `A_Ei=S*b_i` | `consume_phys02.main` | NPZ `energy_eV,source_vectors,physical_energy_scale_eV_m3,time_s,birth_tags` → `source_checks.A_number_m3_s2/A_energy_eV_m3_s2`; history `[0,AN]`, `[0,AE]` | C6/C9의 saved-source moment recovery≤2e−12와 independent reference≤2e−13; 이 문서는 finite sums를 실행하지 않음 |
| §11 cutoff와 low_cross 분리 | `consume_phys02.main`의 `cutoffN/cutoffE`, `atoms` | cutoff_N=9608, cutoff_E=9605; zero source ledgers → `diagnostic_low_cross_excluded=[weights[9609],weights[9610]]` | 원0.1eV ghost 관계 assertion; energy/count를 원 별도 row에서 읽음. 새 projection·energy bin width 없음 |
| §2/§11 finite polynomial integral; `M=(b-a)*(b+a)/2` | `_poly_integral`, `_poly_value`, `integrate_history` | history segment start/stop, `window_s` → `number_m3`, `coordinate_energy_eV_m3/J_m3`, endpoint rates | `quadratic_exact_integral`, `subwindow_exact_integral`, 각 particle-kind의 `*_linear_N/E/proper_rate`; actual6windows×3tags=18 rows 예정 |
| §2 known finite history, missing history, unknown gaps | `_validate_history`, `integrate_history` | `history`, `history_boundary`, `history_gap_policy` → `exposure_s`, `supported_duration_s`, `known_zero_gap_duration_s`, `endpoint_rate_side=left` | `missing_history_nulls`, `no_mean_time_exposure`, `unknown_history_gap`, `point_inside_unknown_gap`, `post_history_not_zero_extended`, `overlapping_history`, `explicit_zero_gap`, `explicit_zero_segment`, `left_rate_at_history_start_unknown` |
| §2 fixed proper volume의 density→worldtube | `integrate_history` | `medium.proper_volume_mode=fixed`, `proper_volume_m3` → `worldtube_count`, `worldtube_coordinate_energy_J` | `*_worldtube_count`, `variable_volume`; actual volume size=null이므로 actual worldtube totals=null |
| §2 spectrum과 moments 구별 | `_validate_history`, `integrate_history`, `consume_phys02.main` | `representation`, stored atom coefficients → `spectrum` 또는 `spectrum_payload` | `*_no_reconstructed_spectrum`, `atomic_weights_not_samples`, `bin_support_extension`; actual stored measure 재사용, photon moments의 inversion 없음 |
| §3/§6 source family·birth/time partition 소유 | `build_source_event`, `claim_injection` | physical-definition/energy-array/source-array digests, native birth support, clock origin → `family_id`, immutable partition/time claim | `producer_variant_same_family`, `fullBED_legacy_same_injection`, `selected_total_low_overlap`, `low_high_disjoint_claims`, `disjoint_time_claims`, `unbound_clock_origin`; actual low+high claim 뒤 total 추가 거절 |
| §4 finite convolution과 eventual reward 구별 | `rr_compatibility`, `attach_rr_return` | `return_horizon`, `proper_time_window_s`, `method`, raw/history digests, full-source-distribution qualification → typed compatibility verdict | `RR_refusal_method_MEAN_TIME_IS_NOT_EXPOSURE`, `RR_refusal_method_EVENTUAL_RESOLVENT_NOT_FINITE_RETURN`, `RR_refusal_proper_time_window_s_FINITE_RETURN_WINDOW_MISMATCH`, `eventual_does_not_become_finite` |
| §4 actual source–recipient state | `rr_compatibility`, actual producer의 `RR_link_attempt` | state/T/frame/isotope/source/history/support/provenance → refusal reasons | `RR_refusal_state_id_DONOR_RECIPIENT_STATE_MISMATCH`, `RR_refusal_frame_MIXED_FRAME`, source/history/support refusal; actual100K/HeIII0→PR10710000K/.01cm⁻³는 gated |
| §5 exact finite quotient | `project_native25` | density delta, `nb_context`, `initial_native25` → `nb_initial_m3`, `nb_final_m3`, `delta` | `baryon_denominator_species/electron/energy`, `changing_nb_no_state`, `borrowed_nb`, `native25_RR_stoichiometry`; positive denominator·baryon ledger·known final population guards는 C9 별도 검토 |
| §6 He4III→He4II(1s), `-E-I+(E+I)=0` | `attach_rr_return`, `project_native25` | I54.42eV/photon≤50000eV, zero recoil/scalar spontaneous ground → signed energy ledger, density delta, retained-photon port | `RR_retained_photon`, `RR_external_ledger_zero`, `RR_heat_null`, `native25_RR_external_zero`; C9 wrong isotope/state/angular/stimulated/mapping 및 approved-He4 controls |
| §6 같은 RR 사건·total/partition 중복 | `canonical_event_id`, `_candidate_return_claim`, `attach_rr_return` | shared `return_registry`, family/channel/time/native birth support, optional `seen_event_ids` → one return claim | `RR_shared_registry_required`, `same_event_duplicate`, `same_event_new_representation`, `RR_variant_same_event`, `RR_total_low_overlap`, `RR_whole_split_time_overlap`, `failed_RR_claim_does_not_mutate_registry`, disjoint-return controls |
| 별도 실행 예산과 실패 보존 | `run_bounded.main` | `EXECUTION_BUDGET.json` → create-only run dir, `RESERVATION.json`, source manifest, `RECEIPT.json`, execution ledger | root의 C4 실제 admission 후 실행; worker+coordinator+receipt-tail reserve와 실패 기록. 이 정적 작업에서는 wrapper 실행 없음 |

## 입력·출력의 정확한 의미

`normalize_to_proper`의 coefficient 공식은 각 segment에서 native elapsed time `s=c_tau*(tau-start)`이고 `c_tau>0`, volume/필요한 target 인자가 상수일 때 적용한다. Timestamp는 이미 proper seconds다. Actual PHYS02의 clock/volume Jacobian은 각각1이고 target은 이미 A에 들어 있다. 729·4π·neutral density나 energy bin width를 다시 곱하지 않는다.

`_poly_integral`은 차분의 거듭제곱을 인수분해해 작은 window의 cancellation을 줄인다. Endpoint rate는 요청 끝점의 왼쪽 극한이다. 기록 시작점의 왼쪽 history가 없으면 그 rate는 null이며, zero-width integral은0이다. 실제 source는0≤τ≤10¹⁰ s에서 알려져 있어 이 구간 안의 exposure와 proper rate를 정의한다. 누락 history나 기록 밖 continuation/shutoff를 만들지 않는다.

`rr_compatibility`와 `attach_rr_return`은 이미 qualified된 return moments를 연결한다. 이 코드에는 K의 생성·역행렬·finite propagator 계산이 없다. 이론의 finite response convolution과 eventual `K^-1 r` 구별은 공급자가 제출한 horizon/method/source qualification에 대한 계약으로 연결된다. 실제 PHYS02–기존 RR bath mismatch는 typed refusal로 반환되고 actual RR·retained port는 null이다.

`project_native25`는 native21+fast count+두 energy ratios+logT의25좌표를 반환하며 energy unit은 J/baryon이다. Baryon-changing 입력은 같은 state/frame의 explicit positive nb와 초기 native25를 요구하고 `(Delta X-x*Delta nb)/(nb+Delta nb)`를 쓴다. `delta logT=0`은 frozen-temperature diagnostic이며 state update를 적용하지 않는다. Actual nb가 없으므로 실제 native25는 null이다.

`attach_rr_return`의 retained photon은 별도 count/energy port다. 그 port의 spectrum/time_history와 instantaneous RR rate는 새로 만들지 않는다. Photon energy를 `w_ext`나 physical heating에 더하지 않으며 source kinetic removal 또는 donor atomic ledger를 두 번 세지 않는다.

## Birth support와 projected support 확인

두 support는 개념적으로 구별한다. 이 frozen grid에서는 원 `energy_grid`가 low linspace의 끝점10eV를 포함하고 high geomspace의 시작10을 제외한 점들을 붙인다. `source_vectors`는 각 source interval의 `lo>=10`일 때 high tag를 부여하며 `project`는 그 점의 인접 lower/upper grid nodes에만 분배한다. 따라서 high-born source는10eV 경계까지 내려갈 수 있지만10미만으로 가지 않는다. R6에서 읽은 실제 metadata도 E[3199]=10, E[3200]=10.007033424904009다.

`low_cross`는 E<=10 mask이므로 source high-tag의10eV 경계 질량을 중복 기록한다. 현재 `[10,900]` atom support 검사는 이 source에 타당하고 support 확대가 필요하지 않다. 향후 다른 projection이 partition 경계를 넘으면 native birth support를 event ownership에 유지하고 projected measure support를 별도로 source/projection identity와 함께 qualify해야 한다. 이 문서는 그런 projection을 생성하거나 허용하지 않는다.

## Actual producer와 예정 산출물

`consume_phys02.main`은 fullBED NPZ를 선택하고 `ACTUAL_SOURCE_RECORDS.json`에 low/high/selected_total 3개 표현을 만든다. `RESULT.json`은6개 finite windows의18개 결과를 저장하도록 작성돼 있다. selected_total은 두 band의 같은 source 합 표현이므로 low+high에 다시 더할 donor가 아니다. Legacy는 같은 source를 가진 대안 transport realization이다.

예정 결과 fields는 `source_records_sha256`, `physical_definition_sha256`, `source_checks`, `source_partition_duplicate_refused`, `rows`, `actual_rows`다. `spectrum_payload`는 기존 atomic measure의 시간 적분 identity와 source record 연결을 보존한다. 이 문서는 해당 파일이 생성됐거나 수치검사가 PASS했다고 주장하지 않는다.

## 고정 수용 기준과 남은 실행

| 항목 | 수용 기준 | 이 문서 상태 |
|---|---|---|
| Source/code/input hash | exact | Source qualification·R6 byte evidence 참조; runtime input binding 별도 |
| Saved source N/E 복원 | relative≤2e−12 | 새 실행 필요 |
| Finite integration·additivity | relative≤2e−14 | 새 실행 필요 |
| Energy units·event conservation | scaled≤2e−14 | 새 실행 필요 |
| Independent reference | relative≤2e−13 | 별도 reference·독립 검토 필요 |
| Input·duplicate·state/frame/isotope/support guards | 명시된 invalid inputs 모두 거절 | Control text 연결만 수행 |
| 전역 물리 오차·완료 | null 유지 | 원 source model/quadrature/projection error를0으로 바꾸지 않음 |

정확한 input hashes·저장 reference literals·physical state·입력 공백과 중앙 owner-return 제안 경로는 `INPUT_QUALIFICATION.json`에 있다. 중앙 원27/88 효과0, N4/N5 partial·N6/N7 predecessor gate, L4=false와 과거 실패·UNKNOWN_NO_ACK·프로젝트별 예산을 보존한다.

