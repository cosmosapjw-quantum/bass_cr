# C02 — 식에서 실제 함수·데이터·species/native 반환까지

단위: `CR_PHYS02_HE_EVENT_UNION_V1`. 상태: 구현 대응표 고정, scientific runtime NOT_RUN. 실행 결과의 authority는 이후 저장되는 RESULT와 parent runner RECEIPT에 있다.

## 수학과 데이터 모델

저장 전자 coefficient measure를 mu = sum_j A_j delta(E-E_j)로 두고, single-event measure S와 대칭 double-event measure D를 사건 수로 정규화한다. mu = S + 2 pi_1 D이다. 코드의 unordered double event는 coefficient 한 개와 두 electron atom IDs를 가진다. 같은 atom ID 두 개도 두 leg로 세며, 이를 한 leg로 축약하지 않는다. 비대각 사건을 대칭 D로 옮기면 양 방향에 weight/2씩 배정한다.

선택 영역의 s는 single, p는 한 leg만 선택된 double, d는 두 leg가 선택된 double의 유한 proper-density이다. N=s+p+2d, parent count=s+p+d=N-d이고 source-parent ion increment는 (HeI,HeII,HeIII)=(-(s+p+d), s, p+d)이다. 전체 네 지원 partition의 union에서는 이 조건부 within-support witness들의 p가 0이다. 실제 outside-support partner를 이 값으로 대체하지 않는다.

| 식 또는 계약 | 실제 함수·데이터 | 반환 또는 검증 |
|---|---|---|
| 원래 NPZ bytes 고정 | `load_pinned_source(path)` | SHA/float64/shape/ordering 확인 후 `AtomBundle` |
| 저장 E_j, A_j의 exact lift | `lift_float`, `Atom` | `Fraction.from_float`, atom key·partition·coefficient |
| actual/fixture provenance 구분 | `fixture_source`, `atom_content_id`, `validate_source` | NPZ/source pins, content digest, loader attestation |
| same state/frame/clock/support | `binding`, `validate_binding` | conditional He4I, gas rest, proper s, fixed density, V=null |
| mu의 single lift | `single_lift` | atom당 1-leg event weight A_j |
| mu의 within-atom double lift | `diagonal_double_lift` | atom당 (j,j), weight A_j/2 |
| 최대 cross witness | `half_shift_lift` | partition-contiguous mass coordinate의 x 및 x+N/2 pairing |
| mu 복원 | `marginal` | 각 event의 모든 leg에 weight를 더한 atom별 exact 결과 |
| n_i와 sharp C envelope | `partition_masses`, `sharp_cross_bound` | Cmax=min(N/2, N-max_i n_i) |
| proper finite birth exposure | `known_window_factor((a,b))` | (b^2-a^2)/2, 0<=a<b<=10^10 필수 |
| partition의 사건 참여 선언 | `claims_by_partition` | 같은 사건 ID가 모든 incident partition에 나타남 |
| s,p,d·ion·energy 직접 합산 | `evaluate_event_set` | N, U, parent count, 3 ion components, charge, chemical energy |
| 명명된 once-only 소비자 | `consume_event_union` | ID union, claim completeness, marginal, 보존, 시간 중복 거절 |

finite coefficient A_j의 단위는 proper m^-3 s^-2이고, event coefficient에도 같은 시간 인자 (b^2-a^2)/2를 한 번만 적용한다. proper density와 absolute worldtube count를 혼합하지 않는다.

## 중복 parent correction

disjoint birth-energy partitions A_i에 대해 C=2 sum_(i<j) D(A_i,A_j)이다. 한 cross event가 두 partition return에서 parent 두 번으로 나타나지만 union에서는 한 번만 나타나므로, union minus separately summed partition return은 다음과 같다.

| 성분 | 보정 |
|---|---|
| He4I proper density | +C |
| He4II proper density | 0 |
| He4III proper density | -C |
| ionic charge density | -2C |
| recipient chemical storage | -(I1*+I2*) C = -79.01 C eV m^-3 |
| 선택 전자 수 / kinetic energy | 각각 0 |
| 새 RR / retained photon 보정 | 각각 0; 저장 port의 값 자체를 0으로 정하는 뜻이 아님 |

I1*=24.59 eV, I2*=54.42 eV는 계약의 recipient native binding literal이다. source threshold, donor work 또는 heating으로 바꾸지 않는다. C는 전체 double-event count d와 다르다. within-atom double witness는 d>0이어도 C=0이다.

## 실제 21-species 배열과 native 부분 map

0-based 순서는 코드 `SPECIES`에 고정되어 있다.

| index | species | 이번 source-ion union 성분 |
|---|---|---|
| 0 | n | 0 |
| 1,2 | H1I,H1II | 0: 이번 He-source-only 반환의 성분 |
| 3,4 | DI,DII | 0 |
| 5,6 | TI,TII | 0 |
| 7,8,9 | He3I,He3II,He3III | 0; He4 결과를 여기에 넣지 않음 |
| 10,11,12 | He4I,He4II,He4III | (-(s+p+d),s,p+d) |
| 13,14,15,16 | Li6I,Li6II,Li6III,Li6IV | 0 |
| 17,18,19,20 | Li7I,Li7II,Li7III,Li7IV | 0 |

`source_ion_density_delta21`은 density increment이고 `correction_to_sum_of_partition_ion_density21`에는 index 10의 +C와 index 12의 -C만 들어간다. 이 배열의 다른 0은 이번 scoped contribution의 0이며, 다른 owner의 실제 species 존재량을 0으로 결정하는 값이 아니다. `MASSES`를 통한 baryon increment 0과 He nucleus·ionic charge identity를 exact 검사한다.

명시적 same-state `nb_m3=8750/47`일 때만 다음 부분값을 만든다. `nb_m3=None`이면 density return만 내고 모든 per-baryon 필드는 null이다. 다른 nonnull nb는 거절한다.

| 출력 key | 값과 ownership |
|---|---|
| `native_source_species21` | density species21 / nb, 한 번만 나눔 |
| `native_species_correction21` | correction species21 / nb |
| `native_ionic_charge_correction` | -2C / nb |
| `selected_birth_zeta` | N_selected / nb; 누적 birth source 부분량 |
| `selected_birth_wnt_J_per_baryon` | U_selected[eV m^-3] × exact 1.602176634e-19 / nb |
| `actual_full_native25`, `actual_T`, `actual_donor_work` | null |
| `outside_partner_response`, `actual_exclusive_event_measure`, `global_physical_error` | null |
| `full_physical_consumer_activation` | false |

부분 fields를 누락된 native25 슬롯에 임의로 채워 완성 벡터로 조립하지 않는다. nonthermal birth energy는 RR 후 survival/occupation exposure와 같지 않으며, 실제 완결된 physical state update를 뜻하지 않는다. `composition_rule`은 union source 또는 corrected partition sum을 한 번만 적용하고, 저장 RR를 한 번 별도 결합하도록 명시한다.

근거: `../implementation/event_union.py`, `../implementation/primary.py`, `../CONTRACT.json`, `../theory/THEORY_KO.md`. 중앙 참고 baseline 28/88; 이 대응표의 중앙 집계 변화 0. 실제 stage 게시·백업 값은 해당 receipt를 따른다.
