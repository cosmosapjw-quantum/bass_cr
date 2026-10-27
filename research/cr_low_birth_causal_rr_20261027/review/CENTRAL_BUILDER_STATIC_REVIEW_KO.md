# Central additive builder 정적 검토

**PASS_SCOPED_STATIC_METADATA_HELPER.** 두 항목을 수정한 현재 source를 다시 읽었고 열린 finding은 없다. Helper는 실행·import·compile하지 않았으며 candidate, source ZIP 또는 중앙 변경을 생성하지 않았다. 실제 최종 candidate의 PASS와 구분한다.

검토 대상은 `ops/build_central_low_birth.py` SHA `8281046ca19a619dd00b2fdd5e53c94b10afc88b11d6ed45c27442952a4a6d4b` 및 schema 문서 SHA `47f4e869cf3485939d9c9b68f295622102b3ecb7439e03507492fe4d527d7b24`다. 이 reviewer는 현재 helper/production/reference 작성자가 아니다. 다만 현재 helper가 재사용한 prior proper-unit metadata builder를 작성한 이력이 있으므로 blind review라고 하지 않는다.

## 수정 사항과 실제 비용 보존

첫째, 기존 `baseline_preparation_cpu_s==0` 조건은 이번 단위에서 실제로 발생한 C4 비용을 거절하므로 제거해야 했다. 수정된 경로는 실제 active `EXECUTION_BUDGET.json` → SHA-pinned `C04_PREPARATION_LEDGER_V2.json` → 각 actual receipt의 bytes/SHA/unit/비용 → runtime ledger baseline으로 이어진다. Unit외 경로, duplicate/self-reference, 외부 allowance 전용과 음수·비유한 비용을 거절하고 Decimal 합은 manifest/budget/ledger와1e−12CPU s 안에서 같아야 한다.

로컬 실제 receipt를 읽어 기존1.714435 subtotal을 구성한4개 record와 v2 admission0.22207 기록이 새 manifest에 존재함을 확인했다. 현재 manifest/budget가 선언한 baseline은1.936505다. 이 값은 새 worker 결과를 추정한 값이나 코드의 hardcoded acceptance 값이 아니다. C4v1 `memory_gate=FAIL`과 container reclaim의 read-only-file-system error도 원문에 남는다.

둘째, worker가 모두 성공했더라도 resource 거절 이력을 숨기지 않도록 `all_worker_attempts_pass`, `all_resource_attempts_pass`, `all_runtime_attempts_pass`를 구분했다. 마지막 값은 resource AND worker다. Owner return은 실패한 preparation receipt paths와 worker attempt IDs를 별도로 보존해야 하며 baseline·manifest identity도 실제 값과 같아야 한다. 이로써 resource 실패와 이후 control 실패를 blanket PASS로 바꿀 수 없다.

## 중앙 변경 범위

추가할 파일은 `DAG.json`과 `returns/CR_LOW_BIRTH_CAUSAL_RR_20261027.json` 두 개다. Root가 준 owner return의 bytes를 그대로 사용하고, 기존 external-source target에 scoped link 하나만 더한다. 그 link를 제거한 뒤 전체 DAG canonical semantic identity가 원본과 같아야 한다. Decimal parser/encoder로 기존 scientific 숫자의 binary64 roundtrip을 피하며, 기존87개 node·17edges·top metadata·target contract/status를 보존한다. Prior proper link, N5/HeIII link와 현재 B3h node도 별도로 대조하도록 작성되어 있다.

27/88, 효과0, L4false, global null, 별도PR23632/88 미합산과 no-budget-carry를 요구한다. `hard_preventive_aggregate_cap_proof=false`도 유지한다. 현재 관찰 central152b82…를 final HEAD로 고정하지 않으며, publisher가 실제 최신 parent/tree를 다시 확인하고 두 파일만 expected-SHA/nonforce로 적용해야 한다. 기존 return 전체 tree를 두-file candidate로 대체하면 안 된다.

Source R3 receipt는 양쪽 original fullGET/200, SHA/CRC와 member/manifest identity가 맞는 실제 기록을 요구한다. Helper 자체의 download는 없다. 새 execution_budget role을 포함한6개 actual result/review role과 sourceS/documentD, 실제20stage publication/ACK를 root가 공급해야 한다. 최종 과학 결과·C9 또는 source identity를 helper가 미리 만들지 않는다.

## 남은 실제 검토

Root가 관찰한 `/proc` descendant count와 aggregate peak가 worker_started=true에서도0인 문제는 유효한 aggregate monitor 증거가 아니다. Direct worker RLIMIT_CPU/AS, terminal wait4/RUSAGE 비용과 구분해 이후 C9에서 actual receipts로 평가한다. 본 정적 검토는 해당 runtime 항목을 PASS로 만들지 않는다.

실제 C6–C8 결과, 실패를 포함한 최종 ledger, C9 판정, source dualR3 및 C10 identity가 생긴 뒤 fresh central base의 two-file candidate/proof를 다시 독립 검토해야 한다. 이번 기록에는 미래 CPU 합계나 numerical PASS 수를 넣지 않았다.
