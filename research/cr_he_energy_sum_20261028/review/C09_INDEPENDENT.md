# C9 독립 검토 최종 보고서

## 최종 판정

**PASS_SCOPED_ENERGY_SUM — 열린 scoped blocker 0.**

Unit은 CR_PHYS02_HE_ENERGY_SUM_V1, 경로는 research/cr_he_energy_sum_20261028이다. Exact finite atomwise support \(E_a+E_b\le K\)에서 total internal-double/parent envelope와 sparse witness, original same-state once-only consumer로의 반환을 채택한다. 실제 C6/C7/C8 결과, source snapshots, root의 PNG 시각 QA, 닫힌 own-budget 기록을 읽은 뒤 내린 판정이다. 추가 과학 실행이나 수정은 필요하지 않다.

실행 이력에는 primary_v1 실패가 남는다. 최종 corrected scope의 PASS와 all_runtime_attempts_pass=false는 함께 유지된다. 중앙 DAG 전체의 물리 완료나 게시·백업의 전체 완료는 이 C9 판정 대상이 아니다.

## 1. 검토자의 독립성 경계

검토자는 production core, primary worker, controls worker, bounded runner의 작성자가 아니다. 별도로 exact generic reference, saved-certificate independent worker, saved-result plot worker를 작성했다. Reference와 independent worker를 동결한 뒤 처음 production 원문을 읽었으며, 이후 알고리즘을 production에 맞추어 바꾸지 않았다.

Independent reference SHA는 58ede1228866a8ca29cce838b7fbfb473c872ea9ef20ec0faf69066df276983b로 유지되었다. Production core SHA는 6cacfa7ba046ea21740beb91b9fd20797f8c06fa43ea525f0c9a555e933d981a이다. Production은 reference에서48개 fixed fixture inputs만 받아 사용하고, reference oracle/verifier를 호출하지 않는다. Independent execution은 production imports0, NPZ loads0이다.

이 독립성은 production 구현에 대한 것이다. 검토자가 작성한 reference·plot 자체에 대한 외부 독립 audit라고 주장하지 않는다. 실제 PNG 시각 검토는 plot 작성자와 다른 /root가 수행했고, 본 C9는 그 실제 파일·hash·QA 기록을 읽었다.

C9 중에는 과학 module import, solver/oracle/plot 재실행, NPZ load, CAS 호출을 하지 않았다. 수행 방법은 정적 source 읽기, saved JSON 읽기, 원본 file hash, source snapshot과 manifest 비교, 실제 세 줄 patch 비교이다. Metadata CPU는 unmeasured/null이다.

## 2. 실제 실행 결과

| Run | 결과 | 확인한 내용 | Charge CPU-s |
|---|---|---|---:|
| probe_v1 | PASS | 실제 runtime probe | 0.170454 |
| primary_v1 | FAIL | fixture ID guard에서 첫 case 전에 종료 | 0.138040 |
| primary_v2 | PASS |123/123 logical checks;48 general fixtures,9 native caps,5 old-consumer windows | 5.847505 |
| controls_v1 | PASS |80/80 controls:75 exact-reason rejection,5 acceptance | 3.840236 |
| independent_v1 | PASS |223/223 groups:192 fresh,31 exact-argument reuse; failed0/not_run0 | 1.922077 |
| plot_v1 | PASS |saved-input validation, exact evidence checks, PNG/SVG creation3/3 | 1.943221 |

모든 run의 source manifest와 final manifest가 일치했다. 각 run의 EXECUTED_SOURCE 안7개 파일의 실제 bytes/SHA를 manifest와 비교하여 mismatch0을 확인했다. 성공한 run의 exit code는0이며, primary_v1은 exit1과 missing RESULT 상태 그대로 보존된다. 실제 receipt 경로와 hash는 동반 JSON에 연결했다.

Primary의 solve 호출 기록은 small optimum48, distinct selected target25, native optimum9, native half target1이다. Original consumer를 통한 scientific-return checks는 full window의 K0/K3/K20과 K3의 인접 half windows 두 개, 총5개다. 이 수치는 logical checks123과 구분한다.

Independent의223 groups는 global4 + small48×4 + native9×3이다.31 reused groups는 인자·event payload·target이 maximum check와 완전히 같은 경우에만 기존 exact certificate를 연결한 것이다.192 fresh groups와 합하여223이 되며, 내부 require 문 개수를 과장해 보고하지 않는다.

## 3. Exact envelope와 certificate 결과

General fixtures에는 empty/zero cases, equal energies, all-low/all-high, exact pair/loop thresholds, stored binary64 cutoff와 decimal cap, rational energies/weights, isolated vertices, imbalanced tails, nonfinal maximum deficit와 입력 순열이 포함된다.48개 모두 독립 full-graph half-integral dual oracle의 optimum과 production dmax가 정확히 일치했다.

Native source는3200 active atoms와 별도 cutoff ghost, 총3201 atoms이고 이번 저장 자료에서는 양의 질량 atom도3201개다. 다음9개 conditional caps의 maximum certificate가 모두 exact marginal residual0과 primal-dual gap0을 가졌다.

| K(eV) | 저장된 exact dmax/N |
|---|---|
|0 |0 |
|1/5 |0 |
|3602879701896397/18014398509481984 |9526254920466972/77906149556394634457 |
|1 |4708232022473114592/77906149556394634457 |
|2 |10064227018025968630/77906149556394634457 |
|3 |14911794880822982546/77906149556394634457 |
|6 |26904538155960258376/77906149556394634457 |
|10 |38702850710117320981/77906149556394634457 |
|20 |1/2 |

Native checker의 sorted-prefix minimum 방식은 explicit dual의 모든 허용 graph constraints를 검사한다. K0와 decimal1/5에는 허용 pair/loop가0개, exact stored-cutoff equality에는1개다. K20에서는5,124,801개 unordered pair/loop 제약을3201개 prefix checks로 논리적으로 모두 검증했다. 이는 sampled pair 검사가 아니다.

K3의 선택된 witness는 dmax/2이다. 따라서 maximum의 dual upper bound와 선택된 witness 사이 gap은
\[
\frac{7455897440411491273}
{49039857307708443467467104868809893875799651909875269632}>0
\]
이고, saved result는 그 target의 optimality_certified=false를 정확히 기록한다. Target marginal residual은0이다. Maximum certificate의 zero gap과 이 중간 target의 upper-bound gap을 구별했다.

Actual C와 D는 null이며 witness_C는 각 행에서 CHOSEN_WITNESS_ONLY_NOT_MAX_C로 표시된다. 이 sample 결과는 total d envelope를 제공한다.

## 4. R6 findings의 실제 종료 근거

| 항목 | 실제 근거와 영향 | 최소 교정의 적용 상태 |
|---|---|---|
| F01 inventory |5개 실제 returns에서 원래 neutral gate 유지; 이 source/window의 반환 interval lower endpoint는0. 별도 labelled algebraic fixture는 정확히 CONDITIONAL_NEUTRAL_INVENTORY_EXHAUSTED로 거부됨 | 닫힘: algebraic interval과 recipient intersection을 분리 |
| F02 p=0 |모든 full four-partition native returns의 p=0; species/charge/chemical checks 통과 | 닫힘: full-support 식과 original partial-selection API의 범위 구별 |
| F03 exact cutoff |decimal1/5에서 dmax0, exact2Eghost에서 ghost coefficient/2. Independent allowed-constraint count0과1 구별 | 닫힘: float tolerance 없이 Fraction equality 사용 |
| F04 C와 d |각 native row가 witness-specific C라고 명시; actual C/D null | 닫힘: max-d를 max-C로 승격하지 않음 |
| F05 general/native domain |empty/zero general cases 통과; algebraic fixture의 attested native adapter 진입은 정확한 이유로 거부 | 닫힘: 원3201 source support 유지 |
| F06 zero optimum |zero cases에서 invalid event·0/0 없음; zero event coefficient negative control은 거부 | 닫힘: direct branch·zero-event 생략 적용 |

구체적인 scalar controls는 bool/float/string/NaN/Inf, 음수 cap·energy·mass, invalid atom/partition/target를 거부했다. Certificate controls는 삭제된 maximum/selected event, forbidden high diagonal, forged dual loop, 변경된 atom digest·mass counters·objective·target, mutable/untyped records, duplicate IDs 등을 거부했다.

Native controls는 변경된 cap/source/state/digest/unit/energy unit/actual-physical-K claim, 다른 cap의 solution, un-attested fixture, window/support/frame/clock/volume/nb 변경, 알려진 history 밖, overlapping replay를 각각 기대한 ValueError reason으로 거부했다. Adjacent windows는 양의 control로 수용했다.75개 rejection과5개 acceptance의 실제 예외 이유를 읽었으며 결과는80/80이다.

## 5. Proper history와 물리 반환 범위

보존된 coefficient history는 \(q_j(t)=tA_j\), proper time \([0,10^{10}]\)초이다. Full window의 factor는50,000,000,000,000,000,000 s², 두 half windows는 각각12,500,000,000,000,000,000과37,500,000,000,000,000,000 s²이다. Primary는 scalar·species·normalized birth additivity와 인접 window replay ledger를 실제 검사했다.

모든5개 반환에서 source_normalization_reapplied=false와 new_source_normalization_applied=false를 확인했다. 원래 consumer가 W를 한 번 적용하고, explicit same-state nb=8750/47로 한 번 정규화한다. RR_correction과 retained_photon_correction은0이며 별도 once-only ports를 유지한다. 전체 window와 두 half-window 반환은 동일 source exposure를 나타내는 대안이므로 함께 중복 합산하지 않는다.

원래 고정 proper-volume density와 absolute volume null이 유지된다. Actual physical K, exclusive He joint kernel, actual C/D, outside partner response, projectile donor work, EOS/T, full-source physical native25, global physical error/budget remaining/currency는 null이다. Physical activation은 false이다. 같은-state conditional source-return 수용을 전체 coupled state 또는 물리 완료로 사용하지 않는다.

## 6. 실제 실패와 최소 repair

primary_v1 stderr는 EXACT_48_FIXTURE_ORDER_REQUIRED를 기록한다. 최초 primary guard는 bare F001..F048을 기대했으나 frozen reference는 F001_empty_zero 같은 descriptive IDs를 사용했다. 이 guard는 첫 case solver 앞에 있어 실제 첫 case 계산에 도달하지 않았다. RESULT는 생성되지 않았고 receipt가 exit1·missing result를 그대로 기록했다.

Source snapshots의 실제 diff를 비교한 결과 변경은 정확히3개 파일의 각1줄이다.

1. primary.py: full canonical IDs는 그대로 두고 numbered prefix만 guard에서 비교.
2. independent.py: 기본 saved input 경로 primary_v1 → primary_v2.
3. plot.py: 기본 summary 경로 primary_v1 → primary_v2.

Core, reference, runner, cases, 정확도·tolerance는 변경되지 않았다. 실패한 source snapshot과 C05 manifest를 보존하고 create-only primary_v2에서 다시 실행했다. 이후 primary·controls·independent·plot의 결과가 PASS이다. 실패 charge0.13804를 삭제하거나 성공으로 재분류하지 않았다.

## 7. Saved plot과 root 시각 QA

Plot worker는 saved SUMMARY와 independent RESULT만 읽었고 NPZ/source/production/oracle를 재실행하지 않았다. 출력은2720×1160 PNG와 SVG이다. 세 panel은9개 conditional cap samples의 markers, normalized parent intervals, near-equal cutoff caps의 별도 categorical 표시다.

Root는 실제 PNG를 view_image로 열고 readable axes/labels, clipping·collision 없음, marker-only 표시, cutoff 구별, parent interval과 inventory의 구별, cutoff normalization, exact cap gap, conditional-K·unknown-kernel 안내, source counts와 actual certificate annotation을 확인하여 PASS_VISUAL_QA를 기록했다.

Plot RESULT의 visual_QA=PENDING_ROOT_PNG_INSPECTION은 worker 생성 시점의 상태로 보존한다. 후속 root QA가 별도 원본 파일로 완료를 증명한다. 검토자가 이를 덮어쓰거나 자신의 시각 QA로 바꾸지 않았다.

PNG는253,510 bytes, SHA256 2984353ee34751a43e018801a4397812b168345bac77e86f4d4c8782f6eb56d2이다. Root QA SHA는534bf0aa99968c9f2a79cdee23b04577b034b77b9d75c35b3bdd4806eaa2de67이다.

## 8. 닫힌 예산

실제 BUDGET.json과 BUDGET_CLOSEOUT.json은 각각7178 bytes이며 SHA256은 동일한
d5d18237161a1c998d5fab388f105ec4c85264b03c16dc8e5e6148e574465ce2이다.

- Cap:40 CPU-s.
- Charge:13.861533 CPU-s.
- Measured coordinator+worker:13.561532000000001 CPU-s.
- Explicit tails와 rounding tails:0.30000099999999974 CPU-s.
- 잔여:26.138467 CPU-s, NONTRANSFERABLE.
- science_closed=true, additional_science_allowance_cpu_s=0.
- automatic_next_node=false, old_or_foreign_budget_transfer_cpu_s=0.
- further_science_runs_selected=0.
- all_runtime_attempts_pass=false.

이는 이 단위의 측정된 local coordinator/worker 비용과 보존된 tails이다. Metadata/provider/publication/CAS CPU는 unmeasured/null로 유지되며, remote까지 측정했다고 해석하지 않는다. Preventive aggregate hard-cap proof는 false라는 원래 기록을 보존했다.

## 9. 주요 evidence pins

| 산출물 | Bytes | SHA256 |
|---|---:|---|
| primary_v2/PRIMARY_CERTIFICATES.json |15,160,355 |4f3cad59cb65f901b72674ce99749878efe6ca84ff3e0e337e38540b0c06540e |
| primary_v2/RESULT.json |24,900 |61a4022de2f3edfe7cde2174528579c3bc82473a9e1e6f86f348ed51eb107d5f |
| primary_v2/SUMMARY.json |102,700 |8107b20143e7e9f0baed96895de1c855d2525e9dd2be6a97613ffe63c0e08deb |
| controls_v1/RESULT.json |32,351 |7fcc5f3c75c4512f5f7adb09e6dfd7c12e0f5c43307ac56cadb14c63573080c5 |
| independent_v1/RESULT.json |270,070 |d4bce8426f521c924f9bc8b0b726f0dedae5887a178c455a0beb4df854894bea |
| plot_v1/RESULT.json |7,063 |59c379f801e543818cb1ab8b15a00f0414e8a234ce87925999140a74d34eb3dd |

표의 run artifacts는 runs/ 아래에 있다. Receipts, manifests, source identities, 원본 실패·repair·R6·budget pins는 동반 JSON에 포함했다.

검토 중 read-only JSON-shape helper가 scalar count에 len()을 적용해 TypeError가 한 차례 발생했다. Schema별 추출로 교정했고 source·result 파일 수정이나 과학 실행은 없었다. 이 metadata 사건은 scientific attempt와 별도로 기록했다.

현재 scope는 채택 가능하며 추가 scientific repair나 test는 요구하지 않는다. Root는 이 C9를 scoped child 종료와 science summary의 근거로 사용하고, 이미 승인된 publication·backup·handoff를 마무리한다. 닫힌 science allowance를 다시 열거나 후속 node를 자동 실행하지 않는다.

