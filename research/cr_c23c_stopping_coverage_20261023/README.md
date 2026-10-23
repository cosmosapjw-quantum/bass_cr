# C23C: saved photoelectron source → caloric cutoff, atomic coverage contracts

이번 단원은 C23B의 완료된 photoelectron atoms를 기존 KC4/KC7 finite atomic cutoff에 결속한 **새 adapter**와, 21 populations를 위한 원자 반응·에너지·동위원소 축약 계약이다. C23B의 source quadrature, C21O의 ODE 및 기존 KC 검증을 복원 목적으로 재실행하지 않았다.

## 완료된 범위

- 새 frozen-target source/bath 입력 18개: 수·전하·핵종·에너지·EOS의 13개 정확 유리수 residual이 각 case에서 0.
- Independent Decimal80 raw-CSV audit: 18개 case, 977 scalar comparisons, 최대 상대차 `1.2507493130458459e-78` < 사전 기준 `1e-40`.
- N4 입력 guard 교정: 5개 targeted checks. 기존 18개 request에는 영향 없음. 실행 당시 source bytes를 `implementation/history/v1/`에 보존.
- N5 bookkeeping/coverage contract: 최초 155개 검사와 C9 변경 범위 6개 검사 PASS_SCOPED. 최초 155개 replay 0.
- 저장 결과만 사용한 최종 그림: `analysis/FINAL_FIGURE_RECEIPT.json`가 선택한 PDF 4개·PNG 4개. v2의 90 mm PDF 한 개는 생성 후 bytes 불일치가 발견되어 v3에서 저장 자료만으로 교정했고 v4에서 실제 PDF 렌더를 읽었다. 최초 표시·전송 결함과 source도 보존.
- 신규 ODE, 신규 source quadrature, empirical atomic-rate evaluation 및 historical science rerun: 모두 0.

이 결과는 열화 시간이나 실제 IGM 열 진화를 계산한 결과가 아니다. `physical_heating=null`, `stopping_time=null`, `global_error_bound=null`을 유지한다. 전체 목표의 분모가 고정되지 않았으므로 전체 완료율도 `null`이다.

## 읽는 순서

1. `reports/SCIENCE_RESULTS_KO.md`: 실제 유도, 입력, 결과와 물리적 해석.
2. `intake/INTAKE_REPORT_KO.md`: 7repo refs/PR inventory, 외부 완료와 미완료 구분, 접근 한계.
3. `theory/lowenergy/C23B_KC_BINDING_DERIVATION_KO.md`: 새 source normalization·charge·binding·EOS 결속.
4. `theory/atomic_coverage/ATOMIC_COVERAGE_THEORY_KO.md`와 `COVERAGE_CONTRACT.json`: 21 populations 및 실제 atomic-rate coverage 의무.
5. `review/C9_REVIEW_KO.md`, `review/n5_independent_review.md`: 한 차례 독립 C9의 발견·수정·종결 근거.
6. `reports/STAGE_LEDGER_KO.md`, `reports/DAG_STATUS.json`: 이번 R1–R10/C1–C10 단계와 열린 후속 노드.
7. `delivery/`: 게시·백업의 실제 receipt와 최종 authority. 단계 문서 작성 뒤의 상태는 이 폴더의 최종 receipt가 보완한다.

## 모델과 물리적 단순화

각 saved source atom은 정지 ground-state target의 bath frame에서 운동에너지 `K_ij` [eV]와 `q_ij` [target^-1 proper-second^-1]를 가진다. 이번 입력에서는

`N_ij = N_target_i * delta_tau * q_ij = n_target_i * V_proper * delta_tau * q_ij`.

Density 또는 fixed-reference abundance 중 하나만 사용한다. 이미 bath frame인 원 source에 boost를 다시 적용하지 않는다. HI/HII/HeI/HeII/HeIII를 모두 명시하며, 처음 존재하는 target만 source step에 사용한다. Daughter를 같은 step에서 다시 이온화하지 않는 frozen-target first-order predictor이다. `delta_tau * Gamma_i <= 1`을 점검하지만 이를 시간 적분 오차 상한으로 승격하지 않는다.

원 `N_B`와 `U_B`는 주입 전 열 bath의 입자 수와 병진 에너지다. 새 primary electrons는 먼저 resolved source inventory로만 추가한다. 같은 event count로 ion charge, total free electrons와 binding ledger를 갱신하고, cutoff에 들어간 전자를 EOS에 합칠 때 이중으로 세지 않는다. 기존 KC4 finite atomic branch를 새 inventory에서 forward-from-zero로 구성한다. 기존 spectrum의 branch continuation이나 일반 유일성 정리를 새로 주장하지 않는다.

`K_c = chi * k_B * T_cal`, `chi >= 3/2`의 cutoff와 FS table의 10 eV 하한은 서로 다른 경계다. Thermal/active와 FS below/inside/above의 6개 cell에서 수와 에너지를 보존한다. Cutoff 아래로 분류했다는 사실만으로 실제 Coulomb stopping 또는 atomic energy deposition이 완료되지 않는다.

`N5`의 free-electron ledger는 `n_e,total = n_e,thermal + n_e,fast`로 해석한다. 총 전하중성 전자수를 Coulomb Maxwell bath density로 그대로 넘기면 안 된다. Energy ledger의 owner는 `all_free_kinetic`이며 supplied recoil은 명시적인 0을 포함해 필수다. 실제 rate 밖의 값은 `null`; 선언된 물리 threshold 아래의 zero만 0이다.

## 이번 실행과 복원

완료 결과는 `runs/`의 immutable receipts를 읽는다. 복원은 배송 ZIP의 SHA256/size/CRC/member SHA를 검증하는 `delivery/restore_c23c.py`로 수행하며 science command를 호출하지 않는다. 이전 run ID의 output 디렉터리는 create-only이므로 덮어쓰지 않는다.

새로운 물리 입력·source·run ID를 승인한 후에만 다음 형식의 실행을 사용할 수 있다. 아래 `<new_run_id>`는 실제 새 식별자로 대체해야 하며 이번 완료 run을 복구하는 명령이 아니다.

```bash
python3 implementation/dispatch.py --run-id <new_run_id> --entry implementation/run_binding.py --timeout 90
```

Dispatcher는 실제 affinity, cgroup CPU/RAM, foreign cooperative lease를 관측한다. Coordinator와 worker CPU를 분리하고 worker당 native thread를 1로 고정한다. CPU55는 보호한다. Resource admission 실패 시 worker를 시작하지 않는다. 기존 NCP51 재실행은 필요하지 않다.

## 정체성과 출처

- Parent publication: `aa57be95b7459eb397d9881b686d9c7bc4444755`, BASS_CR PR96 open/draft/unmerged.
- C23B science: `54477b285e0c712610453bca1408a076af43521d`.
- KC source: `a5c29ad4070acb931d92d2bec42a927a57f479ca`.
- Saved atom CSV SHA256: `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`, 32,592 rows.
- Main C23C execution source identity: `c6174a7a78247a1ee89dfeb152444ba49e2094004926bfe0597eb613e30b7faf`.

각 run의 `SOURCE_IDENTITY.json`는 그 시점 source snapshot이다. 이후 guard/docs가 교정되었어도 과거 receipt를 현재 source로 재서명하지 않는다. `SCIENTIFIC_SOURCE_IDENTITY.json`와 각 `history/v1/`/`REVISION_MAP.json`이 이 관계를 기록한다.

## 고정된 범위와 후속 DAG

Non-tilted LRS와 full Frobenius norm을 유지한다. `Pi_r=abs(Pgamma+Pnu)`, `Pi_tot=abs(Pm+Pr)`에서 signed amplitudes, scalar norms, cancellation을 구별한다. Atomic gas는 isotropic stress이고 matter anisotropic stress는 별도 nonbaryonic Vlasov다. C23C의 five-label fixture를 21 isotope-resolved rate closure로 부르지 않는다.

다음 실제 leaf는 `CR_N4_STOPPING_KERNEL`의 collision/thermal-exchange owner 및 boundary-energy 계약이다. N5 실제 rate providers, 유효 T/E interval, isotope mapping, dominant omitted-process budget을 함께 결속한 뒤 N6 thermochemical/radiative RHS와 N7 새 parcel 실행으로 진행한다. Full nuclear high-energy 및 general triaxial/tilted/polarized CMB는 HOLD다. 원 nuclear network PNG는 회수되지 않아 읽지 않았다. 다른 대화 전체는 UNAVAILABLE이며 검색 단서는 대화 원문 authority가 아니다.
