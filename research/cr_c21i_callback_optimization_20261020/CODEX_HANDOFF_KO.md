# C21I NCP 실행 인계

## 현재 상태와 역할

이 단위의 실제 게시 여부는 `PUBLICATION_RECEIPT.json`, runtime identity는 `EXECUTION_MANIFEST.json`, 완료 검증은 `VALIDATION_SUMMARY.json`, 연구·native 의무는 `DAG_C21I.json`에서 읽는다. 최신 외부 delivery receipt가 제작 시점 ZIP의 pending 상태를 대체한다. **현재 C21H/PR85 content `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`, C21I/PR86 content `fe6bbaec2de5032b938aed0713623b9618ba70e6`가 실제 게시됐다.** 최신 두 publication receipt를 content checkout 밖에 보존해 기존 `status=PUBLISHED` guard와 함께 사용한다. 과거 `user rejected MCP tool call`은 역사 기록이며 실제 게시 성공의 근거로 해석하지 않는다. H/I native chemistry는 계속 `NOT_RUN`이다.

```text
ROLE=C21I_BOUNDED_NATIVE_EXECUTOR
REPOSITORY=cosmosapjw-quantum/bass_cr
C21H_BRANCH=research/cr-c21h-vigilode-bridge-20261019
C21I_BRANCH=research/cr-c21i-callback-optimization-20261020
C21I_UNIT=research/cr_c21i_callback_optimization_20261020
C21H_UNIT=research/cr_c21h_vigilode_bridge_20261019
NATIVE_OWNER=cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4
REUSED_NATIVE_SHA256=1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40
VIGILODE_PIN=8a8bd409b1d96c7b7421f496d229e119fd3d284e
DIFFSOL_PIN=0.17.1
C21H_EXECUTION_MANIFEST_SHA256=7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb
RTOL=2e-11
ALPHA=2e-14
MAX_STEP_DIVISOR=8
JOB_WALL_SECONDS=300
MAX_ACTUAL_ORIGINAL_RHS_AND_NATIVE_CALLS=200000
NATIVE_CALL_TIMEOUT=min(15, remaining_job_seconds)
MAX_CONCURRENT_JOBS=1
BLAS_OPENMP_RAYON_WORKERS=1
PROTECTED_CPU=55
GLOBAL_ERROR_BOUND=null
```

여기서 수행할 일은 현재 자원과 완료 결과의 읽기 전용 확인, published content의 격리 checkout, locked compile, 실제 발견한 작은 호환 수정, bounded native 실행이다. Callback 벡터화·exact cache·native admission·실행기는 이미 제공된다. `block_solver/`는 별도 제조 검증을 마친 prototype이고 현재 native 실행기의 dependency가 아니다. 이를 backend에 연결하는 큰 기능을 NCP에서 처음부터 구현하지 않는다.

## 1. 새 결과와 live 자원 확인

GitHub의 현재 C21G/H/I branch·PR·execution/publication/backup receipt와 세 저장처의 관련 새 파일을 확인한다. REI·VigilODE의 다른 fixture 결과는 해당 owner/source/입력 범위로 분류한다. 동일한 완료 source/fixture/mode/backend/native/bridge identity의 job은 재사용한다. C21F56·C21G35·옛 native 행렬·이 문서에 연결된 완료 제조 검증은 반복하지 않는다.

현재 실제 repo 경로, git status, worktree 목록, process tree, CPU affinity와 campaign별 할당, RAM/cgroup quota, 다른 작업, watcher·checkpoint를 읽기 전용으로 기록한다. 현재 checkout을 reset/clean/stash/rebase하지 않고 watcher·checkpoint를 변경하지 않는다. Affinity membership을 독점 CPU 배정으로 보지 않는다. 보호 CPU55를 사용하지 않는다. Remote Desktop의 과거 quota나 다른 REI NCP receipt를 현재 가용성으로 사용하지 않는다.

실행자는 현재 repo/할당/native receipt로 아래 task-specific 변수의 실제 값을 정한다. 사용자에게 경로나 CPU를 채워 달라고 멈추는 단계가 아니다. 실제 할당·채널이 없으면 그 자원 상태를 BLOCKED로 남기고 완료 산출물을 보존한다.

## 2. 최신 문서 receipt를 content checkout 밖에 보존

아래는 실행자가 실제 기존 repo 안에서 시작할 명령이다. 두 branch가 실제 게시돼 있어야 한다. 미게시라면 중단 이유를 그대로 보고한다. Force push/merge는 하지 않는다.

```bash
set -euo pipefail
set -C
C21I_REPO="$(git rev-parse --show-toplevel)"
C21I_H_BRANCH='research/cr-c21h-vigilode-bridge-20261019'
C21I_I_BRANCH='research/cr-c21i-callback-optimization-20261020'
C21I_H_REL='research/cr_c21h_vigilode_bridge_20261019'
C21I_I_REL='research/cr_c21i_callback_optimization_20261020'
git -C "$C21I_REPO" status --porcelain=v1
git -C "$C21I_REPO" worktree list --porcelain
git -C "$C21I_REPO" fetch --no-tags origin \
  "refs/heads/$C21I_H_BRANCH:refs/remotes/origin/$C21I_H_BRANCH" \
  "refs/heads/$C21I_I_BRANCH:refs/remotes/origin/$C21I_I_BRANCH"
C21I_CONTROL="$(mktemp -d "${TMPDIR:-/tmp}/bass_c21i_control.XXXXXX")"
git -C "$C21I_REPO" show "refs/remotes/origin/$C21I_H_BRANCH:$C21I_H_REL/PUBLICATION_RECEIPT.json" \
  > "$C21I_CONTROL/H_PUBLICATION.json"
git -C "$C21I_REPO" show "refs/remotes/origin/$C21I_I_BRANCH:$C21I_I_REL/PUBLICATION_RECEIPT.json" \
  > "$C21I_CONTROL/I_PUBLICATION.json"
python3 - "$C21I_CONTROL/H_PUBLICATION.json" "$C21I_CONTROL/I_PUBLICATION.json" <<'PY'
import json,re,sys
for path in sys.argv[1:]:
    r=json.load(open(path))
    assert r['status']=='PUBLISHED', 'PUBLICATION_NOT_CONFIRMED'
    assert r['repository']=='cosmosapjw-quantum/bass_cr'
    assert re.fullmatch(r'[0-9a-f]{40}',r['content_commit'])
    print(path,r['content_commit'],r.get('pull_request'))
PY
C21I_CONTENT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["content_commit"])' "$C21I_CONTROL/I_PUBLICATION.json")"
```

기존의 같은 content commit에 대응하는 깨끗한 격리 detached worktree가 있으면 그것을 재사용한다. 없다면 현재 할당된 task 저장 위치에 새 디렉터리를 만들어 `git worktree add --detach`를 실행한다. 현재 root checkout을 reset하지 않는다. 예를 들어 실행자가 실제 확보한 새 `C21I_TASK_ROOT` 아래에서 다음을 사용한다.

```bash
C21I_WORKTREE="$C21I_TASK_ROOT/worktree"
C21I_RESULTS="$C21I_TASK_ROOT/results"
mkdir -- "$C21I_RESULTS"
git -C "$C21I_REPO" worktree add --detach "$C21I_WORKTREE" "$C21I_CONTENT"
C21I_UNIT="$C21I_WORKTREE/$C21I_I_REL"
C21I_H_UNIT="$C21I_WORKTREE/$C21I_H_REL"
C21I_SOURCE="$C21I_WORKTREE/research/cr_c21e_event_native_20261018"
C21I_G_UNIT="$C21I_WORKTREE/research/cr_c21g_reference_refinement_20261019"
C21I_BASELINE="$C21I_SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
```

최신 문서 head와 content commit은 다르다. Content commit 내부의 제작 시점 pending receipt를 고치거나 guard를 지우지 않고, 위 외부 최신 receipt 두 개를 runner에 명시적으로 전달한다. Runner는 두 committed manifest/runtime bytes, H→I ancestor 관계, 실제 detached I HEAD를 확인한다.

## 3. Plan과 locked compile

현재 context의 matching plan이 없을 때만 새 output으로 실행한다.

```bash
python3 "$C21I_UNIT/run_optimized_pilot.py" plan \
  --optimization vectorized \
  --source-dir "$C21I_SOURCE" --c21g-unit "$C21I_G_UNIT" \
  --baseline-dir "$C21I_BASELINE" --out "$C21I_RESULTS/plan_vectorized"
```

현재 설치된 Rust/Cargo를 실제 조회하고 1.94.1 경로를 확인한다. C21H의 `rust_bridge/build_bridge.sh`를 재사용한다. `C21I_RUSTC`, `C21I_CARGO`, `C21I_CPU`는 실제 toolchain과 현재 할당에 연결한다. 같은 source/toolchain/binary의 유효한 완료 build가 있으면 먼저 재사용 가능성을 판단한다.

```bash
"$C21I_RUSTC" --version --verbose
"$C21I_CARGO" --version
C21I_BRIDGE_TARGET="$C21I_RESULTS/bridge_build"
taskset -c "$C21I_CPU" bash "$C21I_H_UNIT/rust_bridge/build_bridge.sh" \
  --cargo "$C21I_CARGO" --rustc "$C21I_RUSTC" \
  --target-dir "$C21I_BRIDGE_TARGET"
C21I_BUILD_RECEIPT="$C21I_BRIDGE_TARGET/BUILD_RECEIPT.json"
C21I_BRIDGE="$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["exit_code"]==0 and r["source_files_unchanged"]; print(r["binary"])' "$C21I_BUILD_RECEIPT")"
```

실제 helper는 locked release jobs1을 사용한다. `--offline`은 필요한 locked dependency가 현재 cache에 있을 때만 붙인다. Cargo.lock이나 VigilODE pin을 업데이트하지 않는다. 이번 샌드박스의 `RUSTFLAGS='-C linker-features=-lld'`는 실제 rust-lld mode 문제에 대한 환경 수정이었다. NCP에 같은 문제가 관측되지 않았다면 적용하지 않는다. Python code-object 호환의 현재 검증 환경은3.12.14다. NCP interpreter 차이로 구체적인 계약 실패가 생기면 해당 작은 호환 수정과 영향 검사만 새 source identity로 기록한다.

## 4. 순차 native pilot

기존 C21H 두 fixture×두 backend의 base4개와 각 성공에 따른 fd_half 최대4개는 H handoff의 독립 계약이다. 기존 G reference8개와 조건부 refinement4개도 그대로다. 완료 matching job을 먼저 재사용한다.

C21I는 `baseline`(I 계측·guard baseline), `vectorized`, `vectorized_exact` 모드를 제공한다. **원 H와의 속도 비교에는 원 H runner 결과를 사용한다.** I baseline은 원 H 전체 경로와 같다고 부르지 않는다. Native 성능을 아직 측정하지 않았으므로 세 모드×전체 fixture를 무조건 제출하는 행렬은 만들지 않는다. 먼저 완료한 H matching base가 있는 `common_ic`·VigilODE 한 행에서 vectorized 후보를 실행하고, exact mode의 별도 비용을 확인할 필요가 있으면 같은 한 행의 새 output으로 실행한다. 해당 실제 결과에 따라 나머지 I 행과 FD followup을 판정한다. 새 큰 기능 구현 없이 같은 CLI로 진행할 수 있다.

현재 검증한 native binary를 `C21I_NATIVE`에 연결한다. 새 native build가 필요한 경우에만 C21F의 기존 builder와 pinned owner를 재사용하고 실제 build provenance를 `C21I_NATIVE_BUILD_DIR`에 연결한다.

```bash
C21I_NATIVE_ARGS=(--native "$C21I_NATIVE")
if [[ -n "${C21I_NATIVE_BUILD_DIR:-}" ]]; then
  C21I_NATIVE_ARGS+=(--build-dir "$C21I_NATIVE_BUILD_DIR")
fi
C21I_MODE='vectorized'
C21I_FIXTURE='common_ic'
C21I_METHOD='vigilode-rodas5p'
C21I_BASE_OUT="$C21I_RESULTS/${C21I_FIXTURE}_${C21I_METHOD}_${C21I_MODE}_base"
python3 "$C21I_UNIT/run_optimized_pilot.py" native \
  --optimization "$C21I_MODE" \
  --publication-receipt "$C21I_CONTROL/I_PUBLICATION.json" \
  --c21h-publication-receipt "$C21I_CONTROL/H_PUBLICATION.json" \
  --source-dir "$C21I_SOURCE" --c21g-unit "$C21I_G_UNIT" \
  --baseline-dir "$C21I_BASELINE" \
  --bridge "$C21I_BRIDGE" --bridge-build-receipt "$C21I_BUILD_RECEIPT" \
  "${C21I_NATIVE_ARGS[@]}" --cpu "$C21I_CPU" \
  --fixture "$C21I_FIXTURE" --method "$C21I_METHOD" \
  --variant base --out "$C21I_BASE_OUT"
```

출력 JOB_RECEIPT에서 COMPLETE, 실제 native calls, source/fixture/bridge/native identity와 payload SHA를 확인한다. source identity의 mode까지 같아야 같은 FD 부모다. 해당 base가 유효한 경우에만 위와 같은 인자에서 다음 세 항목을 바꾼 새 job을 실행한다.

```bash
--variant fd_half --base-job "$C21I_BASE_OUT" \
--out "$C21I_RESULTS/${C21I_FIXTURE}_${C21I_METHOD}_${C21I_MODE}_fd_half"
```

두 explicit derivative probe만 절반으로 줄고 rtol/alpha는 유지된다. 원 H base나 다른 I mode의 base를 이 FD 부모로 전달하지 않는다.

## 5. 결과 반환과 상태 보고

실행 exit와 물리 수지, L0/C21G와의 수치 비교, 달성 정확도, 실제 비용을 각각 판정한다. accepted trace·원 RHS/실제 native/RPC·factorization/rejection/fallback·cache hits·배열 counter·wall time과 실패 raw를 보존한다. Exact cache의 native guard 비용은 실제 native fixture에서 포함해 측정한다. Underflow는 log-survivor와 함께 보존하고 global_error_bound는 null이다.

현재 stage마다 `EXECUTION / PUBLICATION / DRIVE / DROPBOX / LIBRARY / DAG`를 실제 ACK와 raw에 따라 표시한다. 새로운 native 결과와 최소 수정분만 create-only로 백업하고 actual content commit과 문서 receipt commit을 분리해 게시한다. 전체 옛 과학 ZIP·기존 test/raw를 다시 복제하거나 적용하지 않는다. 실행·source·binary·fixture가 바뀐 의존성만 검증한다.
