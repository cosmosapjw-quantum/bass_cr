# NCP local Codex 시작 프롬프트 — CR-PHYS02D

아래 지시문과 이 파일이 포함된 완전 백업으로 진행한다. 추가 사용자 전달 파일을 요구하지 않는다. Archive-root `publication/SCIENCE_COMMIT_RECEIPT.json` 및 외부 시작 파일은 실제 commit과 ZIP identity를 제공한다.

---

`cosmosapjw-quantum/bass_cr`의 `CR-PHYS02D-NCP-PULSE-RESPONSE`를 이어서 수행하라. 주 연구 단위는 `research/cr_phys02d_20261011`이다. 과거 9,600점 ramp 계산은 이미 완료되어 있으므로 새 작업은 동일 격자의 pulse 진단이다.

## 정확한 입력과 복구

1. 이번 PHYS02D 완전 ZIP을 기존에 연결된 Drive 또는 Dropbox 백업에서 확보한다. 외부 시작 파일에 고정된 ZIP 이름·byte 수·SHA256과 대조한다. 기존 인증·동기화 경로를 재사용하고 자격증명을 출력하지 않는다. ZIP이 이미 있으면 다시 받지 않는다.
2. 기존 작업을 보존하고 비어 있는 새 디렉터리에 안전하게 추출한다. 절대경로·`..`·중복 entry·symlink를 거부하고 archive-root `BUNDLE_MANIFEST.json`의 모든 파일 크기·SHA256을 확인한다. Git을 사용할 때는 실제 science receipt의 commit을 별도 checkout/worktree에서 확인한다. `main`에 병합하지 않는다.
3. 두 Astra v4.0.0 harness ZIP은 `handoff_harness/`에 있다. 관련 `START_HERE.md`, 프로젝트 instruction을 읽고, 프로젝트의 `research/context/REMOTE_AGENTS.md`, `CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `HPC_ACCURACY_POLICY_KO.md`, `READBACK_POLICY.md`를 따른다. 현재 사용 모델은 실제 host metadata로 기록한다.
4. `REPORT_KO.md`, `state/SCIENTIFIC_CONTRACT.json`, `ncp/NCP_EXECUTION_CONTRACT.json`, 모든 `state/IMPLEMENTATION_AMENDMENT_*.json`, `inputs/INPUT_IDENTITIES.json`, `inputs/DEPENDENCY_PAYLOAD_MANIFEST.json`, `review/INDEPENDENT_DECISION.json`, `state/NEXT_DAG.json`, `ncp/README_KO.md`를 읽는다. 새 unit과 259개 inherited payload가 모두 준비되어 있으므로 부모 suite를 재실행하거나 데이터를 다시 만들어서는 안 된다.

고정 scientific contract SHA256:

`bc05614e9812f616c4a4bb45805e4c0359a171813f7329794b0c10c3bf37dde2`

고정 NCP contract SHA256:

`9dd8b098d828fcad5ddd5138afd29e9dce4805e26fbac897bd4c9a07779e8ff9`

직접 base는 PR #31의 `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31`이고, 이 전달본의 실제 새 science commit은 receipt를 따른다. 이전 PHYS02C 후기 영수증 `eecb9bd…`는 별도 provenance다. 이전 code·source hash나 frozen acceptance를 새 이름으로 바꿔 통과시키지 않는다.

## 먼저 admission

일치하는 기존 Python 환경을 선택한다. 실제 물리 실행에는 Python **3.12.3**, NumPy **2.4.2**, SciPy **1.17.0**, 실제 수치 threadpool **1 thread**가 필요하다. 전역 환경을 변경하지 않는다. 현 host, affinity, cgroup의 보이는 모든 제한 및 부모 제한, 사용 중인 메모리, reserve, disk, 동시 작업을 실제로 읽는다. NCP64 성능을 가정하지 않는다.

선택한 단위 디렉터리에서 한 번 실행한다.

```bash
python ncp/launch_pulse.py --plan
```

`admission_status=READY`, 정확한 독립 review binding, 모든 payload identity와 resource admission을 확인한다. 이 명령의 exit 0 자체는 실행 허가가 아니다. Runtime pin은 worker가 수치 import 후에도 확인한다. 입력·환경·자원이 맞지 않으면 실제 원인을 남긴 typed HOLD를 반환하며 물리 호출을 시작하지 않는다.

## 허가된 새 물리 작업

새 run directory를 한 개 선택해 **한 번만** 실행한다. 아래 식별자는 실제 UTC와 고유값으로 바꾼다.

```bash
python ncp/launch_pulse.py --execute --run-dir evidence/runs/PULSE_UTC_UNIQUE
```

fullBED 다음 legacy 순서, 같은 `(3200,6400)` 격자만 허가된다. 최대 물리 G 생성 2회, 새 pulse 전파 2회, 전체 wall 3600 s다. 두 birth column은 한 호출에 함께 전파하고 selected_total은 합으로 구한다. 기존 ramp, 2,400/4,800/9,600점 suite 반복, 네 번째 격자, 64-rank sweep을 수행하지 않는다.

이 프로그램은 matching 9,600점 NPZ의 원래 source_vectors 전체를 pulse 초기조건으로 사용한다. 직접 cutoff 및 counter를 보존하고 초기 heat는 0으로 둔다. 이후 원천은 없다. source/bath, 원자모형, CCC native markers/energy axis, cutoff, Coulomb prescription, precision, quadrature를 변경하지 않는다. 전체 ledger 행렬을 역산하지 않는다.

새 결과는 17개 시간의 pulse 열 CDF와 kernel, active resolvent의 frozen terminal yield·평균·분산, 두 적분상태와 기존 ramp 열률/누적 열의 비교, 장부·양성·모멘트 및 CDF 경계 검사를 포함해야 한다. 무한 모멘트는 고정 연산자 연장에 조건부이며 우주론적 장기 이력으로 승격하지 않는다.

## 실패 처리 및 반환

예약은 coordinator가 child/build/pulse 전에 기록한다. 첫 실패, 실제 command/cwd/UTC/exit, runtime 및 threadpool, resource probe, code/input hash, 도달한 raw 산출물을 보존한다. 실패한 run directory를 덮어쓰지 않고 자동으로 물리 실행을 다시 시작하지 않는다. 코드·입력·허용값·예산 변경이 필요하면 구체적인 원인과 bounded amendment 요청을 남긴다. Local Codex가 독립 Astra의 과학 판정을 대신 발행하지 않는다.

실제 실행에 사용한 동일 run directory를 지정하여 반환 묶음을 만든다.

```bash
python ncp/launch_pulse.py --collect --run-dir evidence/runs/PULSE_UTC_UNIQUE --out evidence/returns
```

Return ZIP의 `RETURN_MANIFEST.json`을 검증하고 새 코드, actual run, 모든 실패 및 사용한 operational adapter, pinned transitive dependencies가 포함되는지 확인한다. 추가 손전달 파일이 필요하지 않게 actual return과 짧은 실행 요약을 기존 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` 및 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`에 **새 파일로** 백업한다. 기존 파일을 덮어쓰거나 임의의 다른 수신자에게 보내지 않는다. Git 변경은 additive draft PR/새 branch로 전달하고 non-force ancestry를 보존한다. 실제 remote identity와 수행한 readback 범위를 영수증에 기록한다.

최종 응답은 실제 수행한 것, 실제 exit와 벽시계 시간, 두 모형의 CDF/모멘트/참조 잔차, 미해결 항목, return ZIP의 정확한 경로·크기·SHA256·두 백업 식별자를 분리해 보고하라. 실제 수치 반환에 대한 다음 독립 Astra 심사는 아직 필요하다.

`PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`, `CCC SOURCE_IDENTITY_UNRESOLVED`를 유지한다.
