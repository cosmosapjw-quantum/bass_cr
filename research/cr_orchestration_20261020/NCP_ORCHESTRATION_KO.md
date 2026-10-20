# bass_cr G/H/I 통합 NCP 실행 계약 — 2026-10-20

목표는 **이미 구현·검증·복원·게시한 코드를 취득하여, 아직 완료하지 않은 bounded native 계산만 실행하는 것**이다. 사용자가 파일 다운로드·복원·변수 입력을 따로 할 필요가 없도록 실행자가 GitHub와 연결된 백업에서 직접 읽는다. 새 large feature 구현, 과거 패치 재적용, 완료 matching suite/trajectory 재실행을 하지 않는다. 이 계약은 이전 H/I ZIP의 게시 중단 상태 이후에 작성된 현재 orchestration이다. 이전 게시 거절은 역사 기록으로 남기고 현재의 실제 publication receipt를 읽는다.

먼저 `AGENTS.md`, `docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `docs/HPC_ACCURACY_POLICY_KO.md`, `.codex/readback-policy.json`, [INTAKE_AND_THEORY_KO.md](INTAKE_AND_THEORY_KO.md)를 읽는다. ChatGPT 쪽이 코드·교정·검증·패키징을 담당했고 NCP local Codex는 실제환경 확인, 필요한 작은 호환 수정, locked compile, 실제 실행과 근거 반환을 담당한다. 이 repo에는 별도의 모델 tier 강제 규칙이 없다.

## 0. 최신 결과를 확인하고 job inventory를 확정

현재 작업 경로에서 repo/remote/branch/HEAD/dirty/worktree를 읽기 전용으로 확인한다. `cosmosapjw-quantum/bass_cr`와 native owner `rei_bianchi`의 이 문서 이후 PR·branch·receipt, 현재 NCP의 실행중 process/watcher/checkpoint/terminal receipt, Drive/Dropbox의 새 결과를 읽는다. 조회 범위·시각·페이지 종료·오류를 기록한다. 과거 NOT_RUN은 현시점 증거가 아니다. native process가 진행중이면 새 복제job을 제출하지 않는다.

다음 job key를 source manifest, fixture canonical SHA, method, variant, optimization, native/bridge build+binary identity, controls 및 원 context에 결속한다. COMPLETE payload가 검증되면 REUSED로 표시한다. failed/partial 원본은 보존한다. F의 기존 baseline, full-native8/16/32/48worker,10000/12h, 원 전체 suite와 C21F n8/16/32/64는 재계산하지 않는다.

| lane | 최대 미완료 작업 | 사전 조건 |
|---|---|---|
| G | reference8개, conditionalhistory4개 | 고정 C21F baseline 및 native |
| H | base4개, 각complete base에 FD1개 | locked bridge, 현재 1CPU admission |
| I | 우선 common_ic/VigilODE/vectorized1개 | 동등 H base, H/I 실제 게시, 동일 bridge/native |

현재64core/128GiB 전체가 이 작업에 자유롭다고 가정하지 않는다. 실제 CPU/RAM/디스크/다른 campaign 할당을 조사하여 **CPU 하나**, 동시 job1개를 배정한다. 보호CPU55는 사용하지 않는다. affinity가 곧 독점배정은 아니다. 기존 dirty checkout을 reset/clean/stash/rebase하지 않고 다른 watcher/checkpoint/job을 중단하지 않는다.

## 1. 최신 문서 receipt와 실제 실행 content를 분리

알려진 metadata branches는 다음과 같다.

- H: `research/cr-c21h-vigilode-bridge-20261019`, unit `research/cr_c21h_vigilode_bridge_20261019`
- I: `research/cr-c21i-callback-optimization-20261020`, unit `research/cr_c21i_callback_optimization_20261020`
- G: `research/cr-c21g-reference-refinement-20261019`, unit `research/cr_c21g_reference_refinement_20261019`

이번 복원 게시에서 실제로 생성한 H content commit은 `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`, I content commit은 `fe6bbaec2de5032b938aed0713623b9618ba70e6`이다. I의 부모는 H다. 이는 source content pin이며 이후 receipt/document commit과 구별한다. 실행 시에는 아래 최신 remote receipt가 이 content 또는 후속으로 독립 검증한 content를 가리키는지 확인한다. 아래 frozen manifest와 다른 후속 source를 자동 혼합하지 않는다.

아래 shell은 실제 bass_cr checkout에서 시작한다. 이미 같은 clean content worktree가 있고 원 context 결과를 재사용해야 하면 그 worktree를 사용하고 새것을 무조건 만들지 않는다. `TASK_PARENT`는 실행자가 확인한 writable parent를 택한다.

```bash
set -euo pipefail
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" remote -v
git -C "$REPO" status --porcelain=v1
git -C "$REPO" worktree list --porcelain
TASK_PARENT="$(dirname -- "$REPO")"
TASK_ROOT="$(mktemp -d -- "$TASK_PARENT/bass-cr-ghi-XXXXXXXX")"
CONTROL="$TASK_ROOT/control"
RESULTS="$TASK_ROOT/results"
mkdir -- "$CONTROL" "$RESULTS"
H_REL='research/cr_c21h_vigilode_bridge_20261019'
I_REL='research/cr_c21i_callback_optimization_20261020'
git -C "$REPO" fetch --no-tags origin research/cr-c21h-vigilode-bridge-20261019
H_DOC="$(git -C "$REPO" rev-parse FETCH_HEAD)"
git -C "$REPO" show "$H_DOC:$H_REL/PUBLICATION_RECEIPT.json" > "$CONTROL/H_PUBLICATION.json"
git -C "$REPO" fetch --no-tags origin research/cr-c21i-callback-optimization-20261020
I_DOC="$(git -C "$REPO" rev-parse FETCH_HEAD)"
git -C "$REPO" show "$I_DOC:$I_REL/PUBLICATION_RECEIPT.json" > "$CONTROL/I_PUBLICATION.json"
python3 - "$CONTROL" <<'PY'
import json,re,sys
from pathlib import Path
p=Path(sys.argv[1])
expected={
 'H':('research/cr_c21h_vigilode_bridge_20261019','7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb'),
 'I':('research/cr_c21i_callback_optimization_20261020','f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec')}
for tag,(unit,digest) in expected.items():
 r=json.loads((p/(tag+'_PUBLICATION.json')).read_text())
 assert r.get('status')=='PUBLISHED', (tag,'current publication not confirmed')
 assert r.get('repository')=='cosmosapjw-quantum/bass_cr'
 assert r.get('unit','').rstrip('/')==unit
 assert re.fullmatch('[0-9a-f]{40}',r.get('content_commit',''))
 assert r.get('branch') and r.get('execution_manifest_sha256')==digest
 print(tag,r['content_commit'],r['branch'])
PY
H_CONTENT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["content_commit"])' "$CONTROL/H_PUBLICATION.json")"
I_CONTENT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["content_commit"])' "$CONTROL/I_PUBLICATION.json")"
git -C "$REPO" cat-file -e "${H_CONTENT}^{commit}"
git -C "$REPO" cat-file -e "${I_CONTENT}^{commit}"
git -C "$REPO" merge-base --is-ancestor "$H_CONTENT" "$I_CONTENT"
WORKTREE="$TASK_ROOT/worktree"
git -C "$REPO" worktree add --detach "$WORKTREE" "$I_CONTENT"
```

위 guard가 실패하면 receipt를 수정하여 통과시키지 않는다. 최신 remote ACK/문서 head를 더 조회하고 실제 blocker를 기록한다. I runner는 두 unit의 committed manifest/runtime bytes, H ancestor I, **같은 checkout**, **detached HEAD=I content commit**을 실제로 검사한다. 따라서 receipt는 content checkout 밖 CONTROL에 둔다. 문서-only head를 실행 content로 오인하지 않는다. current receipt가 없어도 임의 SHA·PR번호를 만들어 사용자에게 채우라고 하지 않는다.

## 2. 입력과 예산

```bash
H="$WORKTREE/$H_REL"
I="$WORKTREE/$I_REL"
G="$WORKTREE/research/cr_c21g_reference_refinement_20261019"
SOURCE="$WORKTREE/research/cr_c21e_event_native_20261018"
BASELINE="$SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
```

`CPU`, `NATIVE`, `NATIVE_BUILD_DIR`, `BRIDGE`, `BRIDGE_RECEIPT`는 실행자가 inventory에서 찾은 실제 값에 연결한다. 사용자의 수동입력 단계로 바꾸지 않는다. 원 native owner는 `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`, 재사용 binary SHA256는 `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`이다. 해당 native binary가 실제로 있고 현재 host에서 사용 가능하면 reuse한다. 없을 때만 `SOURCE/build_native.sh`의 pinned build를 사용하고 실제 build receipt를 연결한다.

```bash
NATIVE_ARGS=(--native "$NATIVE")
if [[ -n "${NATIVE_BUILD_DIR:-}" ]]; then
  NATIVE_ARGS+=(--build-dir "$NATIVE_BUILD_DIR")
fi
```

job당 wall300s, 원 RHS/native calls200000, native call timeout=min(15s,remaining)을 지킨다. cleanup의 약2s native/0.5s Rust는 실행과 구별해 기록한다. H/I controls는 rtol2e-11, atol multiplier2e-14, max-step divisor8이다. FP64/단위/합산순서/tolerance/norm/event 정의를 바꾸지 않는다. floor/clipping/silentfallback/fastmath로 실패를 PASS로 바꾸지 않는다. 동일 source/context의 완료 suite는 반복하지 않는다.

G manifestSHA=`7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`, H=`7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb`, I=`f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`이다. G/H/I plan은 source/fixture를 검증하지만 native 계산을 수행하지 않는다. 현재 context의 matching plan이 없을 때 한 번 만든다.

```bash
python3 "$G/run_campaign.py" plan --source-dir "$SOURCE" \
  --baseline-dir "$BASELINE" --out "$RESULTS/g_plan"
python3 "$H/run_pilot.py" plan --source-dir "$SOURCE" --c21g-unit "$G" \
  --baseline-dir "$BASELINE" --out "$RESULTS/h_plan"
python3 "$I/run_optimized_pilot.py" plan --optimization vectorized \
  --source-dir "$SOURCE" --c21g-unit "$G" --baseline-dir "$BASELINE" \
  --out "$RESULTS/i_plan"
```

## 3. 필요한 경우에만 locked Rust bridge compile

동일 source/toolchain/현재 binary의 성공 receipt가 있으면 reuse한다. 새 build가 필요하면 설치된 Rust1.94.1의 cargo/rustc를 실제로 찾는다. rustup이 없으면 실제 toolchain 경로를 사용한다. Cargo.lock은 재생성하지 않는다. VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, Diffsol은 `=0.17.1`이다. 뒤의 더 새로운 upstream patch를 자동 도입하지 않는다.

```bash
CARGO="$(rustup which --toolchain 1.94.1 cargo)"
RUSTC="$(rustup which --toolchain 1.94.1 rustc)"
BRIDGE_BUILD="$RESULTS/bridge_build"
taskset -c "$CPU" bash "$H/rust_bridge/build_bridge.sh" \
  --cargo "$CARGO" --rustc "$RUSTC" --target-dir "$BRIDGE_BUILD"
BRIDGE_RECEIPT="$BRIDGE_BUILD/BUILD_RECEIPT.json"
BRIDGE="$(python3 -c 'import json,sys;r=json.load(open(sys.argv[1]));assert r["exit_code"]==0 and r["source_files_unchanged"];print(r["binary"])' "$BRIDGE_RECEIPT")"
```

helper는 locked/release/jobs1을 사용한다. `--offline`은 locked dependency가 모두 cache에 있을 때만 추가한다. 과거 sandbox의 rust-lld executable mode 문제와 `RUSTFLAGS='-C linker-features=-lld'` 교정은 역사적 환경 증거다. NCP에 같은 실제 문제가 관측되지 않으면 그 workaround를 자동 적용하지 않는다. 작은 실제 환경/API 수정이 필요하면 원실패를 보존하고 새 source/build identity 및 영향 검사만 남긴다. 큰 solver/physics 개발은 여기서 시작하지 않는다.

## 4. G lane — 독립 reference ladder

현재 inventory에서 미완료 G가 남으면 원 runner로 순차 실행한다. L0와 n8/16/32/64는 재사용한다. 모든8reference가 operational COMPLETE이고 native_source pilot sensitivity가 READY일 때만4history를 연다. 각 receipt와 source/fixture/control 서명으로 판단하며 성공 stdout만으로 완료를 추정하지 않는다.

```bash
G_ARGS=()
if [[ -n "${VERIFIED_G_PREVIOUS_OUT:-}" ]]; then
  G_ARGS+=(--reuse "$VERIFIED_G_PREVIOUS_OUT")
fi
python3 "$G/run_campaign.py" run --source-dir "$SOURCE" \
  --baseline-dir "$BASELINE" "${NATIVE_ARGS[@]}" --cpu "$CPU" \
  "${G_ARGS[@]}" --out "$RESULTS/g_campaign"
```

기존partial을 in-place resume하지 않는다. `--reuse`는 원출력 payload를 검증하여 completedmatchingjob만 재사용하는 원기능이다. L3와 L3M의 실제 grid가 같으면 `MESH_CAP_INACTIVE`; 차이0을 정확한 IVP error0으로 해석하지 않는다. empiricalradius와 certifiedbound를 구별한다.

## 5. H lane — 원 adapter의 실제 native base와 derivative sensitivity

두fixture=`common_ic`,`native_source`, 두method=`vigilode-rodas5p`,`diffsol-bdf`의4행을 READY/REUSED/COMPLETE/FAILED/BLOCKED로 먼저 채운다. 아직 안 된 한 행의 실제 `FIXTURE`,`METHOD`를 고르고 create-only 출력에 실행한다. 무조건8개를 제출하는 shellloop를 만들지 않는다.

```bash
H_BASE="$RESULTS/h_${FIXTURE}_${METHOD}_base"
python3 "$H/run_pilot.py" native --source-dir "$SOURCE" --c21g-unit "$G" \
  --baseline-dir "$BASELINE" --bridge "$BRIDGE" \
  --bridge-build-receipt "$BRIDGE_RECEIPT" "${NATIVE_ARGS[@]}" --cpu "$CPU" \
  --fixture "$FIXTURE" --method "$METHOD" --variant base --out "$H_BASE"
```

동일 source/input/fixture/bridge/native/context의 base가 COMPLETE이고 모든 payload가 확인된 경우에만 matching fd_half를 실행한다. H_BASE가 기존완료 결과라면 원context 경로를 유지한다. source identity에는 경로도 포함될 수 있으므로 다른host/path의 receipt를 편집해 binding을 맞추지 않는다. 원context를 복원할 수 없어 followup을 잇지 못하면 그 사유를 BLOCKED로 기록하고 base를 자동재실행하지 않는다.

```bash
python3 "$H/run_pilot.py" native --source-dir "$SOURCE" --c21g-unit "$G" \
  --baseline-dir "$BASELINE" --bridge "$BRIDGE" \
  --bridge-build-receipt "$BRIDGE_RECEIPT" "${NATIVE_ARGS[@]}" --cpu "$CPU" \
  --fixture "$FIXTURE" --method "$METHOD" --variant fd_half \
  --base-job "$H_BASE" --out "$RESULTS/h_${FIXTURE}_${METHOD}_fd_half"
```

H 결과를 G reference ladder 완료로 대체하지 않는다. H/I solver차이,FD민감도, acceptedgrid, 물리수지, runtime은 서로 다른 관측량이다.

## 6. I lane — 가장 작은 native 최적화 비교부터

먼저 같은fixture/source/native/bridge/hardware의 **H원본 common_ic/VigilODE base**를 확보하거나 기존완료 근거를 재사용한다. I baseline모드는 guard계측이 들어간 I구현이며 원 H성능baseline과 구별한다. 새 Inative는 `common_ic/vigilode-rodas5p/vectorized/base` 한 행부터 한다. 동일 입력의 진짜성능 차이와 original RHS/native call 감소·guard비용·end-to-end시간을 읽고 필요한 다음행만 연다. `baseline/vectorized/vectorized_exact`×전체matrix를 자동 제출하지 않는다.

```bash
I_BASE="$RESULTS/i_common_ic_vigilode_vectorized_base"
python3 "$I/run_optimized_pilot.py" native --optimization vectorized \
  --publication-receipt "$CONTROL/I_PUBLICATION.json" \
  --c21h-publication-receipt "$CONTROL/H_PUBLICATION.json" \
  --source-dir "$SOURCE" --c21g-unit "$G" --baseline-dir "$BASELINE" \
  --bridge "$BRIDGE" --bridge-build-receipt "$BRIDGE_RECEIPT" \
  "${NATIVE_ARGS[@]}" --cpu "$CPU" --fixture common_ic \
  --method vigilode-rodas5p --variant base --out "$I_BASE"
```

이 Ibase가 COMPLETE일 때만 동일optimization/source/context의 FDfollowup을 연결한다. Hbase나 다른Imode를 FD부모로 쓰지 않는다.

```bash
python3 "$I/run_optimized_pilot.py" native --optimization vectorized \
  --publication-receipt "$CONTROL/I_PUBLICATION.json" \
  --c21h-publication-receipt "$CONTROL/H_PUBLICATION.json" \
  --source-dir "$SOURCE" --c21g-unit "$G" --baseline-dir "$BASELINE" \
  --bridge "$BRIDGE" --bridge-build-receipt "$BRIDGE_RECEIPT" \
  "${NATIVE_ARGS[@]}" --cpu "$CPU" --fixture common_ic \
  --method vigilode-rodas5p --variant fd_half --base-job "$I_BASE" \
  --out "$RESULTS/i_common_ic_vigilode_vectorized_fd_half"
```

`vectorized_exact`는 실제cacheguard/hitrate 측정이 다음불확실성을 해결할 때에만 같은context에서 별도create-only base로 연다. native_source/Diffsol확장은 완료firstrow와 동일성·budget을 검토한 뒤 해당 질문이 남을 때 수행한다. 제조32ODE·standaloneSchur·threadpoolcomponent는 반복하지 않는다. Schur/JVP production backend 연결은 이번NCP범위가 아니다.

## 7. 수용 조건, 중단 조건, 보존할 결과

각 job의 terminalJOB_RECEIPT/workerreceipt, source/input/build/binary/fixture/rawSHA, actualcontrols, acceptedgrid/FDnodes/RPC/nativepoints, counters, wall/RSS/stdout/stderr, cleanup를 보존한다. 원deadline을 늘리거나 재시도시 같은출력을 덮어쓰지 않는다. domain/nonfinite/timeout/receiptmismatch는 명시적실패로 남긴다. 다른campaign의quota/CPU를 가져오거나 process를 죽이지 않는다.

판정은 최소6축이다: (1)실행완료/제한도달, (2)바이트identity, (3)독립 photon/energy/source/escape/work수지, (4)L0/Grefinement/FD/solver간차이, (5)동일문제runtime성능, (6)게시·백업의 actualACK. `COMPARE_TO_PINNED_L0.json`, `INDEPENDENT_BALANCES.json`, 완료시 `COMPARE_FD_HALF_TO_BASE.json`과 원ledger를 함께 읽는다. 성공exit는 물리수렴승인이 아니며 동일값은 전역오차0이 아니다.

`global_error_bound=null`을 유지하고 Full48/source-age/spectral/angular/CaseB/signedBianchi/fullEoR/standaloneGrackle-driver-parity의 독립HOLD를 자동승격하지 않는다. 고정H/He non-photo donor에 새17-ion물리나 rate table을 임의혼합하지 않는다. publicationAPI거절이나 CI실패를 native과학gate실패로 기록하지 않는다.

## 8. 단계별 게시·백업·DAG와 반환

각intake/build/job/assessment단계에서 `execution`, `science`, `publication`, `backup`, `DAG`를 따로 기록한다. 새결과만 create-onlyGitHub branch/PR에 게시하고 forcepush/자동merge를 하지 않는다. 공개tree에는 secrets/credential/임시URL/비공개raw를 넣지 않는다. 필요한비공개raw는 접근권한이확인된 Drive/Dropbox에 보존하고 공개manifest는 SHA/size/객체ID·범위만 기록한다. oldraw/실패/checkpoint를 수정하지 않는다.

Drive/Dropbox/Library의 기존bass_cr폴더를 현재조회하여 새묶음으로백업한다. R1selectivepolicy가 기본이며 recovery/trusttrigger의R3는 실제수행범위를기록한다. providerACK/metadata를 rawreadback으로부르지않고 SHA가없는것만으로 무조건전체다운로드하지않는다. archiveCRC/payloadmanifest/localSHA와 실제providerID·bytes/checksum을남긴다. sourcecontentcommit/documenthead와receiptcommit이 다르면 각각기록한다.

최종반환은 사용자에게 파일다운로드를 요청하지 않고 아래표와 정확한링크를 본문에 제공한다.

| 단계/행 | 실행·재사용 | 과학 판정 | GitHub actualcommit | Drive/Dropbox/Library actualID·검증수준 | DAG다음node |
|---|---|---|---|---|---|
| 최신intake/자원 | actual상태 | 해당없음 | 조회head | 조회coverage | READY/BLOCKED |
| bridgebuild | COMPLETE/REUSED/FAILED | wiring범위 | build/sourceidentity | actualreceipt | H/Iadmission |
| G8reference/4conditionalhistory | 각각기록 | sensitivity/order별도 | actualreceipt | actualbackup | 해당conditionalgate |
| H4base/4conditionalFD | 각각기록 | balance/FD별도 | actualreceipt | actualbackup | I/assessment |
| I선택pilot | 각각기록 | equality/nativeperformance별도 | actualreceipt | actualbackup | 필요한다음행 |

실제 NCP경로·실행commit·최종documenthead·source변경여부·완료/실패/재사용목록·각jobbudget/counters·자원보존·현재HOLD를 연구스레드에 반환한다. 값이없으면UNKNOWN/NOT_RUN/NOT_EVALUATED를 그대로 쓰며, 임의PASS나전역완료로 채우지 않는다.
