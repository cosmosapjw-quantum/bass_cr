# NCP local Codex 시작 지시 — CR-PHYS02E 저장 격자 펄스

이 파일이 든 완전 백업과 **별도로 발행되는 최종 시작 영수증**으로 이어서 수행한다. 외부 영수증의 실제 ZIP 이름·byte 수·SHA256·Drive/Dropbox ID·science commit/branch/tree·최종 공개 gate를 사용한다. 아직 발행되지 않은 ID를 이 내부 문서에서 추정하지 않는다. 추가 사용자 첨부를 요구하지 않는다.

---

`cosmosapjw-quantum/bass_cr`의 `research/cr_phys02e_20261011`에서 **`CR-PHYS02E-NCP-SAVED-GRID-PULSE`**를 수행하라. 초기 준비 단계는 `HOLD / NEW_INDEPENDENT_REVIEW_REQUIRED`였다. 최종 archive의 독립 `PASS_SCOPED`와 해당 task `READY`, 그리고 ZIP 밖 최종 영수증의 clean restore/publication gate를 함께 확인해야만 새 물리 호출이 가능하다. 구현·대상 시험은 이미 완료되었으므로 재구현이나 전체 suite 반복을 하지 않는다. 이 전달 작업에서 실제 pulse 결과는 아직 없다.

## A. 신뢰·복원·하네스

1. 기존에 연결된 Drive 또는 Dropbox에서 외부 영수증의 정확한 완전 ZIP을 확보한다. 동일 ZIP이 이미 로컬에 있으면 재다운로드하지 않는다. 로컬 byte 수/SHA256과 외부 identity를 대조하고 기존 dirty 작업을 보존한다. 새 고유 staging/checkout/worktree에만 안전하게 추출한다. 절대경로·`..`·중복 ZIP entry·symlink를 거부하며 archive-root `BUNDLE_MANIFEST.json`의 모든 entry byte/hash를 실제 검증한다. 복원/trust boundary에 대한 R3의 수행 범위를 기록한다.
2. 외부 영수증과 archive science receipt의 실제 commit/tree를 대조한다. 새 science branch에서 additive return branch/draft PR을 만든다. main merge, force push, 과거 run/branch/단위 덮어쓰기를 하지 않는다.
3. `handoff_harness/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip`와 `handoff_harness/physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip`의 외부 배포 digest를 검증하고 별도 staging에서 읽는다. 각 `START_HERE.md`, 연구 `PROJECT_INSTRUCTIONS.md`와 관련 integrated prompt, 코딩 `AGENTS.md`·`SCIENTIFIC_CONTRACT.md`·현재 validation 행을 적용한다. `docs/MODEL_ROUTING.md`/`MODEL_ROUTER.json`에 따라 실제 각 실행자의 host model metadata와 요청 backend를 구별한다. 패키지명으로 backend를 추정하지 않고 unsupported alias·모순은 미해결로 남긴다. 전역 harness/모델/개인 skill을 변경하지 않는다. 하네스 템플릿은 실행 증거가 아니다.
4. unit의 `REPORT_KO.md`, `ncp/README_KO.md`, SCI/NCP/validation/input/dependency/DAG/review 및 `research/context/{REMOTE_AGENTS,CHATGPT_CODEX_DIVISION_OF_LABOR_KO,HPC_ACCURACY_POLICY_KO,READBACK_POLICY,ASTRA_TIER_ROUTING_POLICY}.md`를 읽는다. 관련 계약·현재 실패 evidence만 확인하며 과거 전체 phase나 suite를 다시 실행하지 않는다.

## B. 새 계약과 과거 실패를 분리한다

이전 PHYS02D 실제 실행은 **103.797892739 s, exit 1, G 1회, pulse 0회**, constructor 직후 엄격한 격자 점검에서 실패했다. 이전 1 ULP 차이와 actual run·logs·진단을 보존한다. 이전 task 예산은 소비되었으며 새 코드로 재사용하지 않는다.

PHYS02E는 저장 NPZ의 정확한 immutable E를 모든 grid-dependent constructor 계산 전에 설치하는 **새 task**다. 새 승인 범위는 **fullBED 다음 legacy, (3200,6400) 격자/9600점, G 최대 2회, pulse 최대 2회, coordinator 전체 3600 s**다. 후속 pulse의 sampling/physics/tolerance는 D 그대로다. oldD 실행기, ramp, 이전 2400/4800/9600 suite, 새 격자·native 교체·64-rank sweep·추가 physical retry를 수행하지 않는다.

다음 identity를 확인한다.

| 파일 | SHA256 |
| --- | --- |
| SCI `state/SCIENTIFIC_CONTRACT.json` | `863d13aea1dfceba35709f43c6411bad50a8980a660698ad86510ad237dcf6a8` |
| NCP `ncp/NCP_EXECUTION_CONTRACT.json` | `ac5d177fba4b67d83db38260b820a0e6fc289345edc434a437490ae8bb6cdb21` |
| validation `state/VALIDATION_CONTRACT.json` | `8b98196569c12d277087a1cc90ae77eab42ad1430b8f09b9c37c05b77c6dede4` |
| input `inputs/INPUT_IDENTITIES.json` | `30bb5000dcade9a7818e14273f105ca5d5c658665462b6ef8984e846f24a1b96` |
| dependency `inputs/DEPENDENCY_PAYLOAD_MANIFEST.json` | `e04ea95cf8cfc7aef26292c9bd8ed9fb538980f9912d9c04cf97172d8496208e` |

새 FILE_MANIFEST, root BUNDLE_MANIFEST, 모든 pinned inputs와 repository-relative **409파일 dependency payload**를 검증한다. 독립 review는 frozen DAG의 실제 path/hash reference로 검증하고, SCI/NCP/input/dependency 및 `src/saved_grid.py`, `src/pulse_response.py`, `ncp/launch_pulse.py`, `ncp/collect_return.py`, `ncp/ops.py`, `ncp/run_and_collect.py` 여섯 파일을 묶어야 한다. 독립성·정확한 bytes/hash·PASS_SCOPED·READY 중 하나라도 없으면 typed HOLD를 반환한다. local Codex가 심사 파일이나 DAG를 임의로 READY로 고쳐 실행하지 않는다.

## C. 정확한 환경 → plan → 양쪽 NPZ preflight

실제 수치 preflight와 worker는 **Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0, FP64, 실제 BLAS/numerical pool 1 thread**를 요구한다. 기존 pinned venv를 우선 재사용한다. 없다면 현재 전달 지시가 허용한 새 isolated 환경에만 정확한 버전을 준비하며 install command/actual exit/version/경로를 기록한다. Python도 3.12.3이어야 한다. 전역 설치, 환경 gate 완화, CPU fallback, precision/tolerance/quadrature/누적 순서/thread 변경을 하지 않는다. 정확한 환경을 준비할 수 없으면 runtime HOLD다.

`PHYS02E_PYTHON`은 일치하는 venv의 Python 절대 경로로 정한다. source tree 밖에 고유 로그 디렉터리 `PHYS02E_LOG_DIR`를 만들고, source 밖의 **존재하지 않는** 고유 run 경로 `PHYS02E_RUN_DIR`, run 밖의 별도 return 경로 `PHYS02E_RETURN_DIR`를 정한다. run 폴더를 미리 만들지 않는다. 아래 command는 unit root에서 실행한다. stdout/stderr/command/cwd/UTC/exit를 보존한다.

```bash
"$PHYS02E_PYTHON" ncp/launch_pulse.py --plan > "$PHYS02E_LOG_DIR/plan.json" 2> "$PHYS02E_LOG_DIR/plan.stderr.log"
```

plan은 stdlib-only이며 G/pulse/수치 import가 없다. **HOLD여도 exit 0**이므로 JSON의 `admission_status == "READY"`와 `resource_probe.admitted == true`를 따로 확인한다. 독립 review와 root 최종 publication/restore gate도 충족해야 한다. ops가 실제 cgroup visible ancestors·affinity·quota·memory.current·disk를 확인한다. `max(12.5% bounded memory,1GiB)` reserve 후 작업 메모리 12GiB, free disk 8GiB, effective CPU1 이상이 필요하다. advertised NCP topology로 대체하지 않는다.

```bash
"$PHYS02E_PYTHON" ncp/launch_pulse.py --preflight > "$PHYS02E_LOG_DIR/preflight.json" 2> "$PHYS02E_LOG_DIR/preflight.stderr.log"
```

preflight는 exact runtime과 fullBED/legacy **양쪽** pinned NPZ 일곱 필드·grid raw digest/strict equality·shape/dtype/finite/bounds/split/time/tags/source heat/terminal/scale를 검증한다. atomics/Cascade/G/pulse/BUILD reservation은 없다. 실패하면 원래 exit·로그·도달한 진단을 보존하고 **STOP, execute 금지**다. grid를 재생성·보간·재투영하거나 equality를 allclose로 바꾸지 않는다. worker가 같은 preflight를 다시 반드시 수행한다.

## D. 한 번의 wrapper 실행과 완료/예약 구별

앞 gate를 통과했을 때만 아래를 **한 번** 실행한다.

```bash
"$PHYS02E_PYTHON" ncp/run_and_collect.py --run-dir "$PHYS02E_RUN_DIR" --out "$PHYS02E_RETURN_DIR" > "$PHYS02E_LOG_DIR/wrapper.stdout.log" 2> "$PHYS02E_LOG_DIR/wrapper.stderr.log"
```

wrapper가 execute를 최대 한 번 호출하고 finally에서 한 번 collect한다. 다음 별도 `--execute`를 호출하지 않는다. 직접 `--worker` 실행/예약 우회도 하지 않는다. fullBED는 coherent_bed.parent/AtomicData, legacy는 inherited causal_cascade/AtomicData를 사용한다. strict postconstructor array_equal guard를 유지하며 성공한 constructor와 guard 뒤의 `G_COMPLETION_n.json`은 CSC data/indices/indptr·E·method-binding identity를 기록한다. BUILD 예약은 완료 G가 아니며 operator hash는 old/new G parity나 물리 정확성을 증명하지 않는다.

source_vectors 전체 두 birth column·direct cutoff·counters·초기 heat0·time `[0,1e10]`를 보존한다. 후속 원천은 없고 17개 u=i/16을 한 호출에 전파한다. selected는 두 열의 합이다. pulse engine/ops 및 physics/source/bath/atomic/cutoff/FP64/quadrature/tolerance를 변경하지 않는다.

어떤 error/timeout도 최초 command·actual child exit·partial evidence·예약·완료를 보존한다. execute1+collect0은 nonzero이고 execute0+collect1도 nonzero다. 실패 후 physical 재시도나 old task 재사용을 하지 않는다. 새 physics/domain/tolerance/input/budget 또는 허용 repair 밖의 변경은 실제 최초 실패와 최소 필요한 판단을 Astra에게 반환하고 dependent 작업을 멈춘다.

## E. 완전한 return family를 자동으로 전달한다

return ZIP의 actual_run에는 도달한 raw result/failure, actual `ACTUAL_EXIT.json`, runtime/pools, resource probe, preflight, reservations, completed-G, stdout/stderr, 사용한 operational sidecar가 들어간다. source_unit 전체와 모든 409 dependency payload, 이전 실제 실패, pinned inputs 및 original manifest/restore metadata도 들어간다. `RETURN_MANIFEST.json`의 정확한 entry set와 모든 byte/SHA256을 검증한다.

`WRAPPER_EXECUTE_EXIT.json`은 ZIP에 있다. collect 이후 작성되는 **run의 `WRAPPER_COLLECTION_EXIT.json`과 `WRAPPER_ACTUAL_EXIT.json`은 ZIP 밖의 필수 sidecar**다. final wrapper receipt가 execute+collection 실제 exit와 archive path/bytes/SHA256을 묶는다. ZIP에 자신의 hash를 넣으려 재귀적으로 수정하지 않는다. 외부 plan/preflight/wrapper logs 및 isolated setup 기록도 고유 sidecar로 포함하고 각 파일의 byte/hash를 담은 local return-family manifest를 작성한다. collector 자체가 실패하면 ZIP이 없음을 명시하고 sidecar/실패 증거를 그대로 반환한다.

**ZIP + wrapper 두 sidecars + 외부 logs/diagnostics + return-family manifest**를 기존 인증을 이용해 아래 두 곳에 **새 object**로 백업한다. 동시에 새 science branch 기반 additive Git return draft PR로 exact source/actual evidence/receipt를 돌려준다. 사용자에게 다시 파일을 붙여 보내도록 요구하지 않는다.

- Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`

프로젝트 READBACK_POLICY의 실제 trigger/tier를 따른다. 정상 create-only upload와 non-force branch push는 R1/R2 metadata identity 절차를 쓰며 release/복구/trust boundary/불일치는 대상 범위에 R3를 기록한다. provider success·remote object ID/ref·size·available hash 및 exact branch commit을 보존한다. 다른 알고리즘 hash를 SHA256으로 오표기하거나 metadata를 raw readback으로 표시하지 않는다. legacy blanket-download script를 기본 호출하지 않는다. 인증·연결이 없으면 로컬 family를 보존하고 provider별 BLOCKED를 보고하며 게시 완료를 주장하지 않는다.

## F. 실제 반환 심사와 보고

최종 응답은 수행한 command/exit/wall, BUILD/PULSE 예약과 완료 수, runtime·자원·source/input identity, 실제 결과와 미도달 결과, ZIP/sidecar path·byte·SHA256, 두 백업 remote IDs/tier 및 additive Git PR을 구별한다. pulse CDF/kernel·uncapped frozen moments·saved ramp residual·장부/양성/CDF bound 결과는 실제 파일에 있는 범위만 보고한다. exit0을 scientific PASS로 쓰지 않는다. 실제 반환에 대한 **독립 Astra 과학 판정이 다음 필수 단계**다.

동일 operator의 saved ramp 비교는 대수 점검이고 independent physical validation이 아니다. frozen infinite moments는 고정 operator 연장에 조건부이며 cosmic history가 아니다. 이번 9600 pulse로 mesh convergence·production·NCP64 scaling을 선언하지 않는다.

유지 gate: **PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO; all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING; CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED.**
