# CR 외부 source 인터페이스 실행본

외부 photon/electron/baryon의 분포와 주입, scalar cascade/stopping 장부를 구분하는 타입·guard 및 기존 C23B/C23E 소비 adapter다. 실제 입력에 결속한 범위는 C23B의 세 z·ground PI channel과 C23E의 저장 conditional H/D PI/RR/CX moment다.

## 파일

- `contracts.py`: 이산 phase-space measure, proper source 정규화, constant exposure, isotope/domain 검사, event ledger, EOS derivative, cutoff flux 및 provider 증거 검사.
- `consume_saved.py`: 원 atom/point-result SHA256을 확인한 뒤 source·event를 SI로 결속. 과거 source generator나 solver를 import하지 않는다.
- `test_contracts.py`: 새 인터페이스를 위한 제조 controls. 실제 rate/분포 공급자의 물리 검증으로 해석하지 않는다.
- `run_checks.py`: 새 run ID, CPU/RAM admission, 시행별 measured 비용, source snapshot, 원본 로그를 보존하는 실행기.
- `THEORY_KO.md`, `SOURCE_MANIFEST.json`, `PROVIDER_REGISTRY.json`, `INTERFACE_CONTRACT.json`: 식–입력–구현–scope의 연결.
- `runs/external_interfaces_v1/`: 실제 26-control 및 저장 자료 adapter 실행 결과.

## 정확한 실행 명령

저장된 실행을 복구하려는 목적에서는 재실행하지 않고 source/receipt를 읽는다. 코드·입력이 변경되어 해당 검사가 다시 필요한 경우에만 별도 run ID로 아래 명령을 사용한다.

```bash
python3 research/cr_external_interfaces_20261025/run_checks.py --run-id CHANGED_INPUT_UNIQUE_RUN_ID
```

단위 누적 한도는 새 검증 CPU 30 s, 호출당 wall 60 s, address-space 512 MiB, native threads 1이다. 과거 실패를 포함한 이 단위 `runs/*/RECEIPT.json`의 CPU를 차감한다. NCP·외부 host 실행은 없다. 실제 첫 실행은 CPU 0.145485309 s였다. inherited PR105 CPU 39.097868524 s와 C23E 별도 계보 15.493261114 s, global remaining/currency `null`은 그대로 유지한다.

## 소비 경계

`number_weight_per_target_s`는 discrete atom의 질량이다. `dK`나 (4\pi\)를 추가로 곱하지 않는다. target density는 C23B에 한 번 적용하고, 이미 volumetric인 C23E에서는 다시 적용하지 않는다. epoch 보간·support 확장·frame 변환·finite mass·angular momentum law는 별도 명시된 공급 계약을 요구한다.

`caloric_partition`은 heating/assimilation을 반환하지 않는다. molecules를 포함한 thermal heat capacity는 EOS 공급자를 따르며 nuclear count와 구분한다. β, 일반 cascade 및 HE stopping export의 미결 상태는 `PROVIDER_REGISTRY.json`에 보존한다. 이 작업은 N6/N7 gate를 변경하지 않는다.

독립 review와 GitHub/backup/전체 DAG 갱신은 root의 최종 delivery 기록에 결속한다.

## 실행기 예산 이력 보완

최초 v1 source snapshot과 실제 실행 결과를 보존했다. 이후 run_checks.py의 과거 receipt 조회만 수정하여 미완료 run directory를 UNKNOWN_PRIOR_ATTEMPT_BUDGET으로 처리하고 negative/null/NaN/bool 비용을 거절한다. 별도 세 그룹·네 invalid variant의 기계적 검사 CPU는 0.001943521 s이며 과거 source·rate·ODE를 재평가하지 않았다. TARGETED_RUNNER_BUDGET_CHECK.json과 runs/runner_budget_guard_v1/RECEIPT.json을 참조한다. 두 새 검증의 측정 CPU 합은 0.147428830 s이고 과거 계보 예산과 구분한다. 독립 검토는 review/C9_EXTERNAL_INTERFACE.json에 기록한다.

최종 독립 검토는 review/C9_EXTERNAL_INTERFACE.json의 consumed-source 범위 PASS와 review/C9_RUNNER_BUDGET_SUPPLEMENT.json의 실행기 변경 검토 PASS로 구성된다. 최초 실행의 원 wrapper와 최종 budget-guard wrapper를 서로 다른 source identity로 보존했다.
