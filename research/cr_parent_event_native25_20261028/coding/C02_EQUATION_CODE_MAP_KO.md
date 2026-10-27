# C2 수식–입력–코드 사상

새 기능은 준비 단계의 식별·투영과, 저장 응답을 소비하는 primary 단계로 나뉜다. root는 실제 생산 함수와 제어 코드, 출력 serializer를 정적으로 읽고 다음 대응을 확인했다. 이 기록은 실행·compile·수치 PASS를 주장하지 않는다.

| 수식 또는 계약 | 실제 함수 | 자료와 단위 / 적용 횟수 |
|---|---|---|
| 고정 source·17개 입력 | load_retained_inputs, validate_actual_source | 실제 bytes/SHA, birth tag·grid index·ghost·frame·history·state 검증. 원 source 모듈을 import하지 않는다. |
| 안정한 N0,N1,E0,E1 | positive_moments, basis_moments | 80자리 Decimal; 원 binary64 상수·edge를 정확히 lift. 작은 z는 양의 급수, 큰 z는 log 비율. |
| Mtheta=b 및 scaled Bz=1 | identify_coefficients, inverse3, recovery_metrics | 세 recovery band만 fit. 세 holdout을 별도 검사하며 rcond·sensitivity·양의 envelope 기준 고정. |
| 원 linear Q8 projector P | q8_project_basis, project_identified_source | 저장 grid에서 기저를 각각 투영. 원 total atom 바이트는 보존하며 새 attribution 잔차를 별도 출력한다. |
| q(t)=tA의 유한 proper-time 적분 | finite_source_factor, consume_selected_parent_event_window | ((b−a)(b+a)/2)A 한 번. N:m^-3, E:eV m^-3. bin에는 이전 cohort survivor의 저장 응답을 사용한다. |
| 명시적 same-state nb | validate_binding, baseline_inventory | total-nuclei H1/He4 inventory, nb=8750/47. 다른 T·nb·ion fraction·frame·isotope·clock·source factor는 거절한다. |
| 부모 사건 + 별도 RR target | native_affine, evaluate_family | ΔY intercept와 p,d coefficients를 nb로 한 번 나눔. 실제 s,p,d와 partner 응답은 null. |
| selected ζ,w_nt | selected_nonthermal | 원 active change와 cutoff의 signed incremental bookkeeping. nb와 eV→J 변환을 각각 한 번 적용. |
| literal/branch/saved energy 분리 | energy_sidecars | source H13.605693122994, recipient/RR H13.6; 실제 I2src/work는 null. 원 RR 항은 별도 scalar/hex를 보존한다. |
| 조건부 EOS와 작은 log 증분 | finite_caloric, decimal_log1p, caloric_for_saved_row | p=d=0·명시 EOS에서만 계산. observation bin은 직전 prefix의 두 부분 baseline을 사용한다. |
| retained photon port | retained_photon_descriptor | 원 saved ARRAY의 H/He count 및 photon-energy member SHA, row와 port를 그대로 참조한다. |
| 동일 사건 중복 방지 | claim_components, claim_saved_rr_component | 실제 family·recipient·birth support·proper interval·component의 교차 검사. prefix와 conditional fixture의 additive claim 및 aggregate/RR 중복 거절. |
| preparation과 primary의 분리 | run_prepare, load_preparation, run_primary | 준비 산출물의 실제 성공 receipt·producer SHA·NPZ hash 확인 후 byte copy. primary에서 fit·projector 재실행 없음. |
| 별도 numeric reference | independent_reference.py | 90자리 직접 원시함수와 raw M solve, analytic target N/E, 직접 EOS 비율. production import·계수 oracle 사용 없음. |

## 입력 identity와 결측

원 record의 `source_revision`과 `retained_revision`은 서로 다른 provenance 항목이다. 구현은 record의 ec463db0c7e5c7fb5070796071c926caa4db6445와 실제 retained provider 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b를 각각 보존한다. canonical record의 최종 SHA는 8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf다. 이 구분으로 PR107의 10000 K bath를 현재 100 K source에 옮기지 않는다.

실제 history가 없으면 rate·exposure·유한 event·native25를 null로 반환한다. 같은 상태의 explicit nb가 없으면 per-baryon 및 native25를 null로 두고, 별도 proper history가 이미 있던 density N/E만 보존한다. 잘못된 값과 결측은 서로 다른 경로다. 원 immutable record를 변조한 fixture는 SHA 단계에서 거절하며, missing-input 제어는 별도 generic binding fixture를 사용한다.

## 수치 표현과 독립성

새 authoritative scalar는 고정밀 Decimal 문자열이고, 원 RR scalar는 원 JSON number·float hex·source SHA·JSON pointer를 보존한다. baseline+delta와 individual event terms가 authoritative하며 반올림된 endpoint는 진단이다. `OUTPUT_SCHEMA.md`와 production/reference 작성자의 직렬화 key 대조가 이 인터페이스를 결속한다. 실제 NPZ 검증과 비교 결과는 C5–C8에 남긴다.

정적 확인에서 고정 physics 또는 tolerance를 바꾸어야 할 오류는 발견하지 않았다. 실제 환경·CPU/RAM·serialization·실수치 수용은 아직 미수행이므로 C4 이후 별도 결과로 판정한다. C4 helper의 실행 전 실패 경로 교정은 과학식 변경과 분리한다.

현재 단위만 진행하며 중앙 **28/88**, 이번 효과 0이다. 정확한 코드 SHA는 `C02_CODE_SOURCE_PINS.json`, 실제 게시·이중 백업은 생성 후 `publication/C02_RECEIPT.json`을 따른다.
