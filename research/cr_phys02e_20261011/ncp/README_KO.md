# CR-PHYS02E NCP 저장 격자 펄스 실행 절차

대상은 `research/cr_phys02e_20261011`의 **새 과제 `CR-PHYS02E-NCP-SAVED-GRID-PULSE`**다. 이 문서의 초기 준비 단계 DAG는 `HOLD / NEW_INDEPENDENT_REVIEW_REQUIRED`이며 실제 펄스를 실행하지 않았다. 최종 archive의 독립 심사 `PASS_SCOPED`와 해당 DAG의 `READY`, ZIP 밖 root 최종 영수증의 공개·복원 gate가 모두 충족된 뒤 아래 절차를 수행한다. 문서나 `--plan`의 exit 0만으로 실행 승인을 만들지 않는다.

이전 PHYS02D 실제 시도는 **103.797892739초, exit 1, G 예약/생성 1회, pulse 0회**로 끝났다. 그 실패와 1 ULP 격자 차이는 원래 evidence로 보존되어 있다. 이전 예약은 이미 소비되었으며 재사용하지 않는다. PHYS02E는 저장된 에너지 격자를 모든 격자 의존 계산 전에 설치하는 별도의 코드·심사·예산이다. 이번 새 예산은 **G 최대 2회, pulse 최대 2회, coordinator 전체 3600초**, 순서는 **fullBED → legacy**, 격자는 **(3200, 6400), 9600점**뿐이다.

## 1. 외부 영수증으로 시작하고 원본 작업을 보존한다

최종 별도 시작 영수증에서 실제 archive 이름·byte 수·SHA256, Drive/Dropbox object identity, science commit·branch·tree 및 공개 gate 결과를 확인한다. 이 내부 파일에는 아직 발행되지 않은 archive ID나 commit을 임의로 넣지 않는다. 이미 보유한 동일 ZIP은 다시 받지 않는다. 실제 내려받기·복원은 신뢰 경계를 넘으므로 `research/context/READBACK_POLICY.md`의 R3를 기록하고 원시 byte/hash를 검증한다.

기존 dirty 작업, 실패 run, 과거 B/C/D/actual-return 단위를 보존한다. 비어 있는 새 staging 디렉터리 또는 고유 checkout/worktree를 선택한다. ZIP의 절대 경로, `..`, 중복 entry, symlink를 거부하고 root `BUNDLE_MANIFEST.json`의 **모든 entry** 크기와 SHA256을 검증한다. archive에 포함된 실제 science receipt와 외부 영수증의 commit/tree를 대조한다. Git 변경은 새 과학 branch를 기반으로 한 additive branch/draft PR에만 넣으며 `main` 병합·force push·기존 branch/run 덮어쓰기를 하지 않는다.

완전 ZIP의 `handoff_harness/`에 있는 두 패키지를 별도 staging에서 확인한다.

- `physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip`: `START_HERE.md`, `PROJECT_INSTRUCTIONS.md`, 현재 phase에 필요한 `prompts/00_integrated_work_run.md`.
- `physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip`: `START_HERE.md`, `AGENTS.md`, `SCIENTIFIC_CONTRACT.md` 및 현재 계약과 관련 validation 행.

각 패키지의 `docs/MODEL_ROUTING.md`와 `MODEL_ROUTER.json`을 따른다. 연구와 구현의 실제 실행 모델 metadata를 각각 기록한다. 요청된 backend와 관측된 host metadata가 다르면 차이를 그대로 보존한다. 패키지명으로 실제 모델을 추정하거나 가격·성능 절감 주장을 만들지 않는다. 실행 모델이 미해결이면 router의 상태를 보존하며 전역 harness나 모델 설정을 변경하지 않는다. 포함된 state 템플릿은 연구 결과가 아니다.

프로젝트의 `research/context/REMOTE_AGENTS.md`, `CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `HPC_ACCURACY_POLICY_KO.md`, `READBACK_POLICY.md`, `ASTRA_TIER_ROUTING_POLICY.md`와 이 단위의 SCI/NCP/input/dependency/validation/DAG/review를 읽는다. 완료된 구현과 시험을 재작성하거나 이전 suite를 반복하지 않는다.

## 2. 고정 source·입력·심사를 확인한다

| 대상 | 고정 SHA256 |
| --- | --- |
| `state/SCIENTIFIC_CONTRACT.json` | `863d13aea1dfceba35709f43c6411bad50a8980a660698ad86510ad237dcf6a8` |
| `ncp/NCP_EXECUTION_CONTRACT.json` | `ac5d177fba4b67d83db38260b820a0e6fc289345edc434a437490ae8bb6cdb21` |
| `state/VALIDATION_CONTRACT.json` | `8b98196569c12d277087a1cc90ae77eab42ad1430b8f09b9c37c05b77c6dede4` |
| `inputs/INPUT_IDENTITIES.json` | `30bb5000dcade9a7818e14273f105ca5d5c658665462b6ef8984e846f24a1b96` |
| `inputs/DEPENDENCY_PAYLOAD_MANIFEST.json` | `e04ea95cf8cfc7aef26292c9bd8ed9fb538980f9912d9c04cf97172d8496208e` |

새 단위 `FILE_MANIFEST.json`, archive-root `BUNDLE_MANIFEST.json`, input의 모든 byte/hash 및 저장소 root 기준 dependency manifest를 검증한다. dependency payload는 **409개 파일 = 이전 259개 + PHYS02D 101개 + 이전 실제 실패 단위 49개**다. 부모 source나 저장 NPZ를 재생성하지 않는다. review 해시는 최종 frozen `NEXT_DAG.json`의 해당 task reference를 따른다. review는 SCI/NCP/input/dependency identity와 여섯 파일(`saved_grid`, pulse engine, launcher, collector, ops, wrapper)을 모두 정확하게 묶어야 한다. 독립 reviewer가 구현자·후보 설계자와 다르고 `PASS_SCOPED`인지 확인한다. 어떤 mismatch도 typed HOLD이며 자신이 READY를 만들어 실행하지 않는다.

## 3. 정확한 환경과 plan을 확인한다

실제 수치 preflight와 worker에는 **Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0**, FP64 및 실제 numerical threadpool **1 thread**가 필요하다. 먼저 이미 존재하는 pinned venv를 재사용한다. 없다면 현재 전달 지시에서 허용한 **고유 isolated 환경** 안에서만 정확한 버전을 준비하고 install command·actual exit·version·환경 경로를 기록한다. Python 자체도 정확히 3.12.3이어야 한다. 전역 설치, 버전 gate 완화, 다른 precision/tolerance/격자/누적 순서, thread 증대, CPU fallback 또는 과거 native 승인 재사용을 하지 않는다. 환경을 정확히 만들 수 없으면 `RUNTIME_ENVIRONMENT / HOLD`로 끝낸다.

launcher/ops가 thread environment를 1로 설정하고 worker가 실제 pool을 재확인한다. 매 G 전에 ops가 cgroup의 보이는 모든 ancestor·affinity·quota·사용 중 메모리와 disk를 점검한다. 가장 제한적인 bounded memory에서 `max(12.5%, 1 GiB)`를 reserve한 후 작업 가능 메모리 **12 GiB 이상**, 여유 disk **8 GiB 이상**, 유효 CPU **1 이상**이 필요하다. 광고된 NCP64·128GB 수치를 admission으로 대신하지 않는다.

아래 예시는 단위 root에서 실행한다. `PHYS02E_PYTHON`은 정확한 venv의 Python 절대 경로이고, `PHYS02E_LOG_DIR`는 source 밖에 먼저 만든 고유 로그 디렉터리다. 실제 command/cwd/UTC/exit를 함께 기록한다.

```bash
"$PHYS02E_PYTHON" ncp/launch_pulse.py --plan > "$PHYS02E_LOG_DIR/plan.json" 2> "$PHYS02E_LOG_DIR/plan.stderr.log"
```

`--plan`은 stdlib만 사용하고 수치 import/G/pulse를 하지 않는다. **HOLD여도 exit 0을 반환한다.** JSON의 `admission_status == "READY"`와 `resource_probe.admitted == true`를 각각 확인하고 frozen 심사·공개 gate도 확인한다. 하나라도 충족하지 않으면 실행하지 않는다.

그 뒤 numerical-only preflight를 한다.

```bash
"$PHYS02E_PYTHON" ncp/launch_pulse.py --preflight > "$PHYS02E_LOG_DIR/preflight.json" 2> "$PHYS02E_LOG_DIR/preflight.stderr.log"
```

이 명령은 정확한 환경·전체 input identity·양쪽 NPZ의 일곱 필드·저장 격자 raw digest/strict equality·source heat/time/tags/shape/scale 등을 검증한다. **G 생성·pulse·BUILD 예약은 0회**다. 실패하면 해당 command/exit/stdout/stderr와 도달한 진단을 반환하고 **STOP, no execute**로 둔다. source를 보간·재투영·재생성하거나 `allclose`로 바꾸지 않는다. 실제 worker도 같은 preflight를 다시 반드시 수행한다.

## 4. wrapper를 한 번만 실행한다

source tree 밖의 **아직 존재하지 않는 고유 run 경로**와 그 run 밖의 별도 return 디렉터리를 정한다. 로그를 redirect하려면 run 안에 미리 폴더를 만들지 말고 위 외부 로그 경로를 사용한다. 다음 명령을 **단 한 번** 수행한다.

```bash
"$PHYS02E_PYTHON" ncp/run_and_collect.py --run-dir "$PHYS02E_RUN_DIR" --out "$PHYS02E_RETURN_DIR" > "$PHYS02E_LOG_DIR/wrapper.stdout.log" 2> "$PHYS02E_LOG_DIR/wrapper.stderr.log"
```

wrapper가 launcher `--execute`를 한 번 호출하고 `finally`에서 한 번 collect한다. wrapper 다음에 별도 `--execute`, oldD 실행기, ramp, 부모 suite, 추가 grid 또는 물리 retry를 호출하지 않는다. private pipe를 가진 coordinator만 child를 시작하며 직접 `--worker`로 우회하지 않는다. coordinator deadline은 admission을 포함한 3600초이고 own children만 종료한다.

fullBED는 inherited `coherent_bed.parent`와 `AtomicData()`, legacy는 inherited causal-cascade와 `AtomicData()`를 쓴다. immutable 저장 E를 상속된 generator **이전**에 설치하고 constructor 뒤에도 exact `np.array_equal`를 확인한다. 성공한 constructor+guard마다 `G_COMPLETION_n.json`에 existing CSC data/indices/indptr·E·method-binding identity를 남긴다. raw G를 저장하지 않으며 이 identity는 이전 G의 byte parity나 물리 정확성의 인증이 아니다. BUILD/PULSE 예약 수와 완료 G 수를 구별한다.

각 모델의 완전한 저장 `source_vectors` 두 birth column을 보존한다. direct cutoff와 counters를 유지하고 초기 heat는 정확히 0, 후속 주입은 없다. u=i/16의 17개 시각을 한 pulse 호출로 계산하며 selected는 두 열의 합이다. inherited pulse engine, physical equations, atomic source, FP64, quadrature, 허용값, source/bath, cutoff 및 T0=1e10 s는 그대로다.

## 5. 실제 exit·첫 실패·완전 return family를 보존한다

wrapper exit가 0이어도 numerical scientific PASS는 아니다. execute1+collect0은 nonzero, execute0+collect1도 nonzero다. 실패/timeout/부분 결과를 삭제하거나 성공 파일로 바꾸지 않는다. 새 입력·physics/tolerance/domain/budget 판단, 추가 물리 실행 또는 허용 repair 밖의 수정은 최초 실패와 최소 근거를 Astra에게 반환한 뒤 dependent 작업을 중단한다. 이미 소비된 D 또는 E 예약을 새 코드로 재사용하지 않는다.

실제 run에는 도달한 `PLAN_AND_ADMISSION`, reservation, runtime/pools, `INPUT_PREFLIGHT_RECEIPT`, resource probes, BUILD/PULSE reservations, completed-G identities, stdout/stderr, NPZ·RESULT 및 `ACTUAL_EXIT.json`이 남는다. 성공한 경우에만 전체 `NUMERICAL_RESULT.json`이 있다. wrapper의 `WRAPPER_EXECUTE_EXIT.json`은 archive에 포함된다. collect 후 작성되는 **`WRAPPER_COLLECTION_EXIT.json`과 `WRAPPER_ACTUAL_EXIT.json`은 ZIP 밖의 필수 sidecar**다. final sidecar가 execute/collect exit 및 archive path/bytes/SHA256을 연결한다. 자기 자신의 SHA를 ZIP 안에 넣으려 ZIP을 재귀적으로 수정하지 않는다.

return ZIP은 `actual_run/`, `source_unit/`, 모든 `dependency_payload/`, pinned input copies, original frozen manifest, restore metadata를 포함한다. `RETURN_MANIFEST.json`은 자신을 제외한 모든 entry의 byte/SHA256을 기록한다. entry set가 정확히 `manifest files + RETURN_MANIFEST.json`인지, 모든 byte/hash가 일치하는지 확인한다. 복원은 새 위치에서 dependency payload를 repository root에, source unit을 `research/cr_phys02e_20261011`에 overlay하고 actual run은 별도 보존한다. 외부 plan/preflight/wrapper stdout/stderr와 환경 setup 기록도 return family의 고유 sidecar로 보존한다.

**ZIP + 필수 wrapper sidecars + 외부 진단/로그 + 로컬 return-family manifest**를 기존 인증으로 다음 두 위치에 create-only 백업하고, 새 science branch 기반 additive Git return draft PR로 전달한다.

- Drive folder: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912`

사용자에게 추가 파일이나 첨부를 요구하지 않는다. 기존 연결·remote를 재사용하며 비밀값을 출력하지 않는다. 정상 create-only 업로드/branch push에는 프로젝트 R1/R2 metadata 절차를 적용하고 실제 tier·provider success·remote ID/ref·크기·available hash·exact commit을 기록한다. release/복구/trust-boundary 또는 metadata mismatch는 해당 대상에 R3를 적용한다. DropboxHash/MD5를 SHA256으로 표시하지 않는다. 기본 경로로 legacy raw-readback script를 호출하지 않는다. 인증·연결이 없으면 local ZIP/sidecar를 유지하고 provider별 `BLOCKED`를 보고한다. 미수행 업로드를 완료라고 쓰지 않는다.

## 6. 반환 해석의 상한

실제 command/exit/wall, 예약과 completed-G/pulse 도달 수, runtime·자원·입력·source identity, 모형별 CDF/kernel/모멘트/저장 ramp residual, archive family byte/hash와 remote receipt를 구별하여 보고한다. 다음 **독립 Astra 실제 반환 심사**가 과학 판단을 내린다. 저장 ramp와 J1/J2 일치는 같은 연산자의 대수적 점검이며 독립 물리 검증이 아니다. frozen infinite moments는 고정 연산자 연장에 조건부이며 우주론적 장기 이력이 아니다. 9600점 pulse만으로 mesh convergence나 NCP64 scaling을 주장하지 않는다.

유지할 gate: `PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`, `CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED`.
