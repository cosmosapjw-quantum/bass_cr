# NCP 선택 실행 패킷: C21I native exact 한 행

작성 기준: 2026-10-20 13:39:37 UTC. **이번 패킷은 준비 문서와 얇은 실행 래퍼다. 여기서 native process, chemistry, ODE 또는 bridge를 실행하지 않았다.** 현재 NCP 자원·실행 파일의 존재는 이번 작업에서 관측하지 않았다. `actual_exact_native_execution=NOT_RUN`, `actual_exact_native_performance=NOT_EVALUATED`, `global_error_bound=null`이다.

다음 한 행은 고정 C21I 구현의 `common_ic / vigilode-rodas5p / vectorized_exact / base`다. 원 H base, I vectorized base, I vectorized FDhalf의 새 실제 반환은 이미 COMPLETE로 확인됐으므로 재사용한다. G reference lane은 독립 계약으로 남긴다. 같은 identity의 더 새 exact 완료 또는 진행 결과가 있는지 실행 직전에 먼저 확인하고, 있으면 재사용하거나 진행 중인 작업을 기다린다.

## 1. 실행 source와 새 보고서의 게시 pin

| 역할 | 실제 고정 값 | 적용 |
|---|---|---|
| H 실행 content | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | I의 실제 부모 |
| **I 실행 content** | **`fe6bbaec2de5032b938aed0713623b9618ba70e6`** | 같은 repo의 detached checkout `HEAD` |
| H 문서 head | `0ec4c55102766c40c554ffc6141eb08fba741c79` | PR85 게시 근거 |
| I 문서 head | `26ab505dac2bfcb0cfd3d049f22bc408f4c86241` | PR86 게시 근거 |
| 새 native evidence content | `0f2d195aee3c08b372d020bcd6caba87db64a83c` | PR87의 이미 반환된 세 native 행 |
| 마지막 확인한 native evidence 문서 head | `d3eaf596e46be4f994723fb742237a7399c290ed` | 2026-10-20 13:09:05 UTC 실제 ref 재조회 |
| 이번 C21J 분석·보고·패킷의 새 게시 commit | `null`, `PENDING_ROOT_PUBLICATION` | root의 실제 push/readback 영수증으로 결속할 필드 |

C21J의 아직 생기지 않은 commit을 만들어 쓰지 않는다. 그 필드는 분석·보고서 게시용이며 **이번 native job의 실행 source를 바꾸지 않는다**. NCP는 현재 branch/PR/receipt를 다시 읽고 문서 변경과 source 변경을 구분한다. 새 source가 발견되면 fe6과 자동 혼합하지 않는다.

실행 전에 repo의 `AGENTS.md`, `docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `docs/HPC_ACCURACY_POLICY_KO.md`, `.codex/readback-policy.json`을 읽는다. 원 권위 문서는 `NCP_C21HI_FINAL_PROMPT_KO_20261020.md`와 [26ab의 NCP_ORCHESTRATION_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/26ab505dac2bfcb0cfd3d049f22bc408f4c86241/research/cr_orchestration_20261020/NCP_ORCHESTRATION_KO.md)다. 파일 SHA와 runtime manifest는 [PILOT_CONTRACT.json](PILOT_CONTRACT.json)에 있다.

## 2. 이 한 행으로 확인할 불확실성

반환된 H base와 I vectorized base는 최종 **전체 28개 state와 모든 ledger**, 저장된 segment 결과와 accepted physical points가 동일했다. 독립 저장 trace 분석에서 원 RHS 요청은 823개이며, full physical `(t,u)`의 binary64 key에 대해 **cell별 16-entry LRU의 재사용 기회는 69개**였다. 이 저장 요청열에 조건부로 적용하면 miss는 754개다. native `EVAL` 문자열 중복 100개는 tau·ledger가 다른 요청까지 합치므로 full RHS hit로 사용하지 않는다.

이 숫자는 이미 저장된 요청열의 분석이다. 새 native exact 실행의 실제 counter가 아니다. 실제 exact 경로는 source-defined provider, process, deadline, fixture/context와 file lease를 callback마다 검사한다. Admission 및 종료 시 전체 SHA도 확인한다. 따라서 saved native reply를 사용한 replay 시간으로 실제 native exact 성능을 판정할 수 없다. 이번 한 행은 **실제 admission/live guard를 포함한 cache hit, 실제 native 호출, 결과 동일성 및 시간 비용**을 확인한다. 기존 제조 입력의 전체 시간 가속도 `NOT_ESTABLISHED`이며, 한 번의 새 시간 관측만으로 일반적 가속을 확정하지 않는다.

## 3. 현재 NCP 자원 admission과 기존 작업 보존

실행자가 실제 접근한 NCP에서 다음을 읽고 시각·범위·오류를 남긴다. 경로나 CPU 값을 사용자에게 채우라고 되묻는 단계가 아니다.

1. 현재 repo/remote/HEAD/dirty/worktree, 다른 관련 branch/PR/receipt와 세 저장처의 새 결과를 확인한다. 동일 source manifest, canonical fixture SHA, method, variant, optimization, native/bridge/build identity 및 controls의 COMPLETE payload를 검증하면 `REUSED`로 처리한다. 진행 중인 matching job도 복제 제출하지 않는다.
2. 실제 CPU affinity, CPU/RAM/cgroup/디스크 제한과 남은 여유, campaign별 현재 배정, process tree, watcher와 checkpoint를 읽는다. **CPU55를 제외한 실제 배정 CPU 하나**를 확보한다. Affinity에 포함됐다는 사실은 독점 배정 증거가 아니다. 과거 CPU62 또는 서버 전체 64core/128GiB를 현재 가용 자원으로 옮겨 쓰지 않는다.
3. 동시 native job은 1개다. BLAS/OpenMP/MKL/NumExpr/Rayon worker는 모두 1이며, 각 job은 NumPy가 먼저 import되지 않은 새 Python process로 시작한다. 기존 dirty checkout의 reset/clean/stash/rebase, watcher 중단, checkpoint 덮어쓰기를 하지 않는다.
4. `LIVE_INVENTORY.json`과 상세 process/context raw는 비공개 보존 대상이다. 공개 tree에는 허용된 요약과 SHA를 기록한다. 자원 또는 artifact에 접근할 수 없으면 실제 관측된 `RESOURCE_NOT_ADMITTED`, `ARTIFACT_MISSING`, `ACCESS_UNAVAILABLE` 등의 구체 사유를 기록한다. 과거 scratch의 Rust 부재를 현재 NCP의 부재로 추정하지 않는다.

이번 패킷은 이 현재 자원 확인을 수행했다고 표시하지 않는다. `PILOT_CONTRACT.json`의 현재 CPU·메모리·경로 필드가 `null`인 이유는 **아직 관측하지 않았기 때문**이다. 기존 NCP 권위 계약의 실제 inventory 절차를 이어서 이 필드를 별도 새 admission 기록으로 결속한다.

## 4. artifact 복원과 build 재사용

| 필요한 artifact | 취득·복원 위치 | 적용 조건 |
|---|---|---|
| 실행 tree | GitHub의 I content `fe6bbaec…` | 독립 detached checkout. H/I가 같은 root에 있고 `H ancestor I` 확인 |
| F/G/H/I runtime 및 baseline | 같은 fe6 tree | F runtime 10개, G runtime 4개, H runtime 8개, I runtime 3개 및 각 manifest. G 입력 검사는 두 fixture의 `fixture.json`, `radau.json`, `SUMMARY.json` 총 6개를 요구한다. common_ic 한 행이어도 native_source의 baseline 파일을 빼지 않는다 |
| 외부 H/I PUBLISHED controls | 현재 H/I 문서 receipt를 content checkout 밖의 새 control 디렉터리에 보존. 아래 반환 archive에도 `control/H_PUBLICATION.json`, `control/I_PUBLICATION.json`이 있다 | 정확한 repo/unit/content/manifest 및 최신 metadata 대조. 역사적인 content 내부 pending receipt를 편집하지 않는다 |
| 성공 bridge 및 build receipt | 아래 반환 archive의 `binary/bass-cr-c21h-rust-bridge`, `build_success/BUILD_RECEIPT.json` | 실제 binary SHA, 성공 receipt와 source-files identity 확인. 현재 host architecture/ELF loader·공유 library·실행 권한을 확인하면 **Rust 설치 없이 재사용 가능** |
| native executable | 현재 실제 matching 파일을 먼저 찾고, 없으면 원 PR82의 검증된 binary/build artifact를 현재 receipt에서 찾아 복원 | 이번 선택 행은 아래 **known SHA 일치 binary만** 사용. 새 반환 archive에는 native executable이 없다 |

검증된 새 반환 archive는 `C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz`, 2,568,680 bytes, SHA256 `2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3`다. Drive ID `1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u`, Dropbox ID `id:BSpOijBcT10AAAAAAD_T4A`, rev `65e43db2185370af03d47`이다. 이번 intake는 Drive raw 전체 SHA와 archive payload 155개를 확인했고, Dropbox는 metadata 확인 수준이다. 실제 존재를 확인하지 않은 Library ID나 PR82 binary archive ID를 만들어 넣지 않는다.

bridge SHA는 `717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30`이고 성공 build receipt SHA는 `c846c35621dd9a0aa3c5bbfb90e94da0f022e934cf2ea1342270d61eda4b5190`이다. 복원된 binary의 현재 경로를 `--bridge`로 주고 원 receipt를 `--bridge-build-receipt`로 준다. 영수증 내부의 과거 build 경로를 현재 경로로 편집하지 않는다. 현재 host의 loader/dependency 확인은 읽기 전용 정보로 먼저 해결하며, 과거 protocol/smoke/native suite를 자동 반복하지 않는다.

### bridge를 재사용할 수 없을 때만 locked build

원 helper의 실제 인자는 다음뿐이다. `CARGO`와 `RUSTC`는 현재 설치에서 찾은 실행 파일이며, `BRIDGE_BUILD`는 새 절대 경로다. 현재 toolchain/dependency가 없으면 그 상태부터 기록한다.

```bash
taskset -c "$CPU" bash "$H/rust_bridge/build_bridge.sh" \
  --cargo "$CARGO" --rustc "$RUSTC" --target-dir "$BRIDGE_BUILD"
```

helper는 `cargo build --locked --release --jobs 1`을 실행한다. Vigilode pin `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, Diffsol `0.17.1`, 게시된 Cargo.lock SHA `d30f7f6437b7704f845ba85f8206c94810fbd4ec1a48db9cba06b7b77604c892`를 유지한다. `--offline`은 필요한 locked dependency가 실제 cache에 있을 때만 추가한다. 과거 sandbox의 linker workaround를 자동 복사하지 않는다. 반환의 실패 build와 성공 build를 보존한다. **300초는 계산 job의 예산이며 cold compile 전체에 무조건 적용하는 시간이 아니다.** Build는 별도 자원·시간 기록을 가진 준비 단계다.

### native identity와 이번 행의 제한

Native owner는 `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`다. 이번 행은 5,003,448-byte binary의 SHA256 **`1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`**를 요구한다. 과거 `/root/C21F_NATIVE_RUN_20261018T1358Z/build/native_point`는 탐색을 도울 역사적 위치일 뿐, 현재 존재를 보장하지 않는다.

원 G authority에는 `RECORDED_PINNED_OWNER_BUILD`를 검사하는 일반 경로도 구현되어 있다. 이 경로는 `build/native_point`, `owner_commit.txt`, `build_exit.txt`, `input_sha256.txt`, `owner_source.tar`, 고정 `native_point.rs`를 대조한다. 그러나 **이번 선택 행은 다른 SHA로 새로 만든 native artifact를 자동 admit하지 않는다**. Known binary를 복원하지 못하면 구체적인 artifact 상태를 반환한다. 별도 새 build가 필요해지면 그 실제 source/build identity와 영향 검증을 독립적으로 다룬다.

원 `build_native.sh NEW_BUILD_DIRECTORY [EXISTING_OWNER_GIT_REPOSITORY]`는 locked/offline owner build를 사용하지만 내부 `CARGO_BUILD_JOBS=2`다. 한 CPU의 `taskset`으로 제한된 두 compiler child와 native job의 worker1을 혼동하지 않는다. 이 build recipe를 이번 exact 한 행의 필수 준비 단계나 자동 실행 단계로 추가하지 않는다. Frozen helper를 바꿔 jobs1이라고 표시하지 않는다.

## 5. 실제 single-run 명령

`WORKTREE`, `CONTROL`, `CPU`, `NATIVE`, `BRIDGE`, `BRIDGE_RECEIPT`, `PYTHON`, `NEW_EXACT_JOB`은 NCP 실행자가 위 현재 inventory와 복원 결과에서 얻은 실제 값이다. `NEW_EXACT_JOB`은 아직 없는 절대 경로다. 기존 H/I base를 만들거나 FD parent를 넘기지 않는다.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
I="$WORKTREE/research/cr_c21i_callback_optimization_20261020"
G="$WORKTREE/research/cr_c21g_reference_refinement_20261019"
SOURCE="$WORKTREE/research/cr_c21e_event_native_20261018"
BASELINE="$SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"

"$PYTHON" "$I/run_optimized_pilot.py" native --optimization vectorized_exact \
  --publication-receipt "$CONTROL/I_PUBLICATION.json" \
  --c21h-publication-receipt "$CONTROL/H_PUBLICATION.json" \
  --source-dir "$SOURCE" --c21g-unit "$G" --baseline-dir "$BASELINE" \
  --bridge "$BRIDGE" --bridge-build-receipt "$BRIDGE_RECEIPT" \
  --native "$NATIVE" --cpu "$CPU" --fixture common_ic \
  --method vigilode-rodas5p --variant base --out "$NEW_EXACT_JOB"
```

이 명령과 같은 인자로 stdout/stderr/exit/time을 runner 출력 밖에 보존하는 얇은 [run_exact_once.sh](run_exact_once.sh)를 제공한다. NCP 실행자는 현재 값으로 `C21J_WORKTREE`, `C21J_CONTROL_DIR`, `C21J_NATIVE_BINARY`, `C21J_BRIDGE_BINARY`, `C21J_BRIDGE_BUILD_RECEIPT`, `C21J_PYTHON`, `C21J_ALLOCATED_CPU`, `C21J_RUN_ROOT`를 결속하고 `bash run_exact_once.sh`를 **한 번만** 호출한다. `C21J_RUN_ROOT`는 아직 없는 새 절대 디렉터리이고 원 runner가 그 아래 `job/`을 create-only로 만든다. 필요하면 현재 확인한 GNU time 실행 파일의 절대 경로를 `C21J_TIME_BINARY`에 결속한다. 이 값이 없으면 GNU time/RSS 계측은 없는 것으로 표시하며 job 자체 receipt의 시간은 보존한다.

래퍼는 known native SHA와 frozen I runner SHA를 prelaunch에서 확인하고 동일 명령을 한 번 호출한다. 별도 compiler, test suite, native probe, ODE, 자동 retry, mode sweep 또는 FD follow-up을 실행하지 않는다. 래퍼의 단순 affinity 확인은 앞 절의 실제 독점 자원 배정을 대신하지 않는다. 현재 source/publication/native/fixture/build 및 exact purity admission은 **고정 원 runner가 계속 검사한다**.

### runner가 실제 강제하는 값

| 항목 | 기존 구현의 값·동작 |
|---|---|
| 실행 checkout | detached `HEAD=fe6bbaec…`; H/I 같은 repository; committed manifests/runtime bytes와 두 외부 PUBLISHED receipt 대조 |
| common_ic | canonical SHA `befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65`; 9 cohorts, 28-state; `FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT` |
| 허용오차·cell step | rtol `2e-11`, fixed-scale atol multiplier `2e-14`, max-step divisor `8` |
| 계산 제한 | 원 H deadline `300 s`, 원 RHS evaluations와 native actual calls 각각 최대 `200000` |
| 개별 native 요청 | `timeout=min(15 s, 남은 원 job 예산)`; exact setup/guard도 같은 예산 소비; 종료 후 deadline 검사 |
| exact cache | cell별 capacity16, full physical `(t,u)` binary64 byte key, signed zero 보존, 성공 RHS 값만 저장, 반환 copy, cell마다 reset |
| native admission | 정확한 원 `NativeMicro`/`BudgetedNativeMicro` class·code·binding, owner/build identity, actual process/stream/protocol receipt, 불변 fixture/source/context/deadline 및 monotone native count |
| live guard | hit에도 실행; admission과 terminal full SHA; callback에서는 immutable metadata/path lease와 live process/configuration/budget/context 검사 |

`--wall-s`, `--max-calls`, `--rtol`, `--workers` 같은 인자는 이 CLI에 없다. 새 flag를 만들어 상한을 적용했다고 표시하지 않는다. 허용오차·floor/clipping·fastmath·norm·state/event 정의를 바꾸지 않는다. Failed admission을 replay stub, 일반 purity 선언, pending receipt 수정으로 우회하지 않는다. Calls가 cap에 도달했을 때 이미 성공한 exact hit는 허용되며 실제 N+1 miss는 원 provider가 거부한다.

## 6. 이번 결과를 읽는 순서와 반환

실행 결과가 생기면 `JOB_RECEIPT.json`, `C21I_PUBLICATION_IDENTITY.json`, `INPUT_IDENTITY.json`, H/I source identity, native identity/process receipt, fixture, build receipt, 원 result 및 모든 payload hash를 먼저 확인한다. Terminal receipt가 없으면 성공 exit 문구만으로 COMPLETE를 만들지 않는다. Wrapper 로그는 원 `job/` 밖에 있으므로 원 runner의 payload inventory를 사후 변경하지 않는다. 실패·partial·timeout raw도 그대로 보존한다.

비교는 다음과 같이 각각 판정한다.

- **실행과 동일성:** actual source/native/bridge/build/fixture/mode/controls와 현재 hardware·환경·자원 context를 반환한다. Source 또는 binary가 바뀌었으면 옛 H/I의 같은 성능 실험으로 표시하지 않는다. H/I는 재계산 없이 이미 완료된 raw를 비교 기준으로 사용한다.
- **해와 수지:** 최종 전체 state, 모든 ledger, accepted trace, independent balances와 pinned L0 비교를 함께 읽는다. Endpoint 일부만 같다는 이유로 전체 state equality를 선언하지 않는다. 차이는 최대 fixed-scaled 차이와 실제 성분·단위를 보존한다.
- **실제 비용:** 원 RHS requests/evaluations, exact hits/misses/evictions, native actual calls, RHS/Jacobian/partial-t RPC, accepted/rejected/LU/fallback 및 phase timing을 보존한다. 69 hits/754 misses는 저장 요청열에 대한 예측값이므로 새 actual counter와 구별한다. 차이가 있으면 새 raw 요청열·guard admission·solver trace로 원인을 확인한다.
- **시간 해석:** end-to-end process, job, reference, segment, instrumented RHS/key/hit와 native logged interval을 이름 그대로 기록한다. 중첩된 시간을 더하거나 native logged interval을 순수 chemistry 시간으로 표시하지 않는다. 별도 guard timer가 없으면 잔여 시간을 순수 guard 비용으로 계산하지 않는다. 현재 자원·시각이 다른 한 번의 실행으로 일반적 speedup을 확정하지 않는다.
- **조건부 다음 행:** 새로운 FD 불확실성이 실제로 남을 때만 matching COMPLETE **exact-mode base**를 부모로 별도 FDhalf를 검토한다. 기존 I vectorized base/FDhalf나 H base를 exact FD parent로 재지정하지 않는다. G8/conditional4, 다른 H fixture/backend, 전체 I matrix 또는 Schur/JVP production 연결을 자동 제출하지 않는다.

| 상태 축 | 이 패킷 작성 시점 | 실행 이후의 갱신 근거 |
|---|---|---|
| 패킷 준비 | `PREPARED_CONTRACT_ONLY` | 실제 파일·정적 확인 |
| NCP exact native 실행 | `NOT_RUN` | 해당 새 job의 actual terminal receipt와 raw |
| 과학 | 기존 `HOLD`, `global_error_bound=null` | 별도 수지·FD·refinement 평가 |
| exact native 성능 | `NOT_EVALUATED`; 일반 가속 `NOT_ESTABLISHED` | 실제 guard가 동작한 새 job의 시간·counter와 비교 한계 |
| C21J 게시 | `PENDING_ROOT_PUBLICATION` | 실제 content/document commit와 ref/PR readback |
| 백업 | `PENDING_ROOT_CLOSEOUT` | create-only archive 및 각 provider ACK·검증 수준 |
| DAG | `C21J_SELECTIVE_NATIVE_EXACT_BASE: PREPARED_CONTRACT_ONLY` | 위 실행/과학/게시/백업의 각각 실제 상태 |

새 결과만 create-only branch/draft PR 및 Drive·Dropbox·Library 묶음으로 보존한다. 원 실패·raw·역사 `NOT_PUBLISHED`, C21F 게시 완료, G 독립 계약, 보호 CPU55를 유지한다. Full48/source-age/spectral/angular/Case B/signed Bianchi/full EoR/standalone Grackle driver parity의 과학 HOLD를 자동 승격하지 않는다. 공개 결과에 private `LIVE_INVENTORY` 원문을 포함하지 않는다.

## 근거

구체적인 CLI와 예산은 [고정 I runner](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/run_optimized_pilot.py), [H runner](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21h_vigilode_bridge_20261019/run_pilot.py)에서 읽었다. Purity/live guard는 [native_cache_contract.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/native_cache_contract.py), input/native build 검증은 [G campaign_contract.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21g_reference_refinement_20261019/campaign_contract.py)의 실제 구현에 따른다. 기존 NCP 권위 계약, 반환 archive의 성공 build/세 job raw 및 현재 C21J의 읽기 전용 trace 분석을 재사용했다. 이 패킷은 새 native 실행의 영수증이 아니다.
