# C23D — 저장 source와 기존 유한온도 EE 연산자의 결속

이 단위는 고정 C23B photoelectron source의 low-10 eV pulse를 기존 Maxwellian EE provider에 결속한다. 과학적 수용 범위와 현재 판정은 `CLAIM_GATE.json`, 계산 결과는 `REPORT_KO.md`, 실행·보존 상태는 `HANDOFF_KO.md`를 따른다. 기존 provider나 source quadrature를 다시 구현·실행하지 않는다.

Git subtree는 `research/cr_c23d_finiteT_source_bridge_20261024/`이다. 기본 경로에서 adapter는 같은 repository의 다음 기존 파일을 찾는다.

- `research/cr_coulomb_partition_20261014/coulomb_partition.py` — 3984 bytes, SHA256 `0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86`.
- `research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv` — 1681578 bytes, SHA256 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`.
- 이 단위의 `inputs/CASE.json`.

위 기존 source/provider는 새 Git subtree에 중복하지 않는다. Canonical recovery ZIP에는 두 파일의 정확한 bytes를 원 repository-relative 위치로 함께 보존한다.

## 실제 실행과 재사용

완료된 primary run은 `runs/c23d_source_ee_20261023T220714Z_v1/`이다. Frozen convergence의 세 trajectory, applicability, signed coefficients, MFPT, SAME-current ledger, guard 및 runtime 측정값을 포함한다. `RESULT_CLARIFICATION.json`은 원 `new_ODE:0` 표현과 실제 신규 선형 EE population evolution을 구분한다. 원 실행 script는 `implementation/history/primary_20261023T220714Z/`에 exact hash로 보존했다.

별도 `runs/c23d_source_ee_supplement_20261023T220810Z_v1/`는 root의 세 trajectory 의도 명확화가 도착하기 직전에 끝난 추가 observation이다. 필수 계약과 admission basis에 포함하지 않으며 실제 비용과 결과를 보존한다. 기존 C23B quadrature, C23C18, KC/2048 Landau 검증을 재실행하지 않았다.

## 새 실행 명령 — 복구 명령과 별도

아래 명령은 실제 새 과학 실행을 시작한다. 이미 완료한 결과를 읽거나 복구할 때 실행하지 않는다. Frozen 입력·scope·실행 예산이 여전히 승인된 별도 새 단위를 실행할 때만 사용한다. Repository root에서:

```bash
python research/cr_c23d_finiteT_source_bridge_20261024/implementation/dispatch.py
```

Dispatcher는 runtime/runs 부모를 만들고, 고유한 create-only run과 exclusive local lease를 생성한다. CPU0 worker, CPU8 coordinator, native threads1, CPU120s/wall180s/RSS512MiB를 적용한다. CPU0/8이 없는 다른 호스트에는 현재 resource contract를 임의로 대입하지 않는다.

다른 materialization 위치에서는 runner가 명시적 경로도 받는다. 이미 만들어진 새 empty run directory를 넘기며, 다음은 명령 형식이다.

```bash
python research/cr_c23d_finiteT_source_bridge_20261024/implementation/run_bridge.py NEW_EMPTY_RUN_DIR \
  --provider /absolute/path/to/coulomb_partition.py \
  --source-csv /absolute/path/to/photoelectron_atoms.csv \
  --inputs /absolute/path/to/CASE.json
```

직접 runner 호출은 dispatcher의 wall/RSS 감시·lease 관리와 별도이므로, 현재 실행 계약에서 dispatcher를 기본으로 사용한다. 경로 override는 파일 위치만 바꾸며 exact source/provider hash 검사는 유지한다. NumPy/SciPy 및 그림용 Matplotlib은 기존 환경을 사용했고 설치/bootstrap은 수행하지 않았다.

## 계산하지 않고 읽기·복구하기

1. JSON/CSV/그림과 `REPORT_KO.md`를 읽는다. `.py`를 import하거나 실행할 필요가 없다.
2. Canonical ZIP을 받을 때 외부 artifact metadata의 전체 size/SHA256을 먼저 비교한다.
3. ZIP의 `MANIFEST.json`에서 payload size/SHA256과 typed source/commit roles를 확인한다.
4. 검증·복원만 하려면 package의 `mechanical/restore_c23d.py`를 ZIP 밖에 복사해 아래 형식으로 실행한다. 이 스크립트는 ZIP 전체를 memory에서 읽고 CRC/모든 manifest member를 검증한 다음, 존재하지 않는 목적지에 bytes만 쓴다. 과학 코드를 import하거나 실행하지 않는다.

```bash
python restore_c23d.py CANONICAL_ZIP NEW_NONEXISTENT_DESTINATION
```

복원 후 `NEW_NONEXISTENT_DESTINATION/repository/research/cr_c23d_finiteT_source_bridge_20261024/`에 새 단위가 있다. 기존 두 파일도 `repository/research/...`의 원 경로에 복원된다. 기존 디렉터리 위에 merge/overwrite하지 않는다.

최종 ZIP은 science publication S와 실제 PR receipt를 받은 뒤 생성한다. ZIP 생성·검증은 저장 bytes의 보존 작업이며 과학 검증이나 새 실행을 대신하지 않는다. 자체 containing commit과 backup provider ACK를 추측하지 않는다.
