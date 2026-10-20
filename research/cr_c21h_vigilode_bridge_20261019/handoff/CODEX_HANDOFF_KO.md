# C21H NCP 실행 인계 — 현재 영수증을 읽고 이어서 실행

> 현재 게시 중단: 새 명시적 push 지시 후의 create_tree594개 재시도도 user rejected MCP tool call을 반환했고 tree SHA가 없었다. commit·branch·PR 생성은 실행하지 않았다. 최신 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원래 8개 runtime source는 변경하지 않았다. 현재 환경의 locked 실제 재컴파일과 복원 근거는 새 영수증에 보존하며 native chemistry/NCP는 NOT_RUN이다.

> 역사 기록 — 재지시 이전의 2026-10-20 게시 요청: 새 create_tree도 `user rejected MCP tool call`을 반환했다. 원격 tree SHA·commit·branch·PR은 확인되지 않았고 현재 게시 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원 과학 source·검증은 유지되며 최신 실행/복구 증거는 별도 create-only 백업에 보존한다.
> 역사 기록 — 2026-10-20 이전 이관: 다른 대화로 이관하기 위해 C21H 게시 요청이 중단됐다. 마지막 create_tree 응답은 aborted by user였고 SHA가 없으며, 실제 branch/commit/PR 생성은 확인되지 않았다. 프로그램과 검증 raw는 세 저장처에 보존된 원 과학 ZIP에서 바이트 동일하게 복원했다. 현재 영수증을 읽고 게시를 재개한다. Native chemistry/NCP는 NOT_RUN이다.

## 게시 당시 확정된 검증 범위

두 solver의 제조 wiring base 및 fd_half 4건이 source manifest 02에서 모두
PASS했다. 이는 원 C21G RHS와 Rust bridge 연결을 실제 실행한 제조 검증이며,
C21H의 native chemistry campaign 결과는 아니다. 최종 source freeze에 대응하는
plan 02와 영향을 받는 선택 검사도 PASS 기록을 보유한다. 이미 완료된 제조 검증이나
기존 전체 suite를 NCP에서 반복할 필요는 없다. 더 새로운 결과는 실행 전에 확인한다.

| 제조 wiring 증거 디렉터리 | 결과 | 기록된 실행시간 |
| --- | --- | ---: |
| evidence/wiring/smoke_vigilode_base_03 | PASS, exit 0 | 1.418304674 s |
| evidence/wiring/smoke_diffsol_base_02 | PASS, exit 0 | 1.218285762 s |
| evidence/wiring/smoke_vigilode_fd_half_01 | PASS, exit 0 | 1.418343376 s |
| evidence/wiring/smoke_diffsol_fd_half_01 | PASS, exit 0 | 1.519834591 s |

- 실행 manifest SHA256: `7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb`.
- 이 제조 검증에 사용한 Rust bridge binary SHA256: `a11d3ab01474f9d1a88df51c9cd6d7910ca59b3443814fd39699ed959cb64048`.
- Branch: `research/cr-c21h-vigilode-bridge-20261019`.
- Unit: `research/cr_c21h_vigilode_bridge_20261019/`.
- 부모 C21G: PR84, head `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`.

초기 Diffsol roundoff/typed-stop 실패와 그 당시 raw는 역사 기록으로 보존한다.
위 4개는 교정 후 실제 완료한 결과다. 이 실행시간만으로 solver의 native 성능 우열을
판정하지 않는다. NCP에서 새로 빌드한 bridge의 바이트가 달라지면 그 실제 build/source
receipt로 검증하며, 위 binary SHA만으로 재현 가능한 toolchain 전체를 주장하지 않는다.

현재 PR URL, content commit 및 세 저장처 백업 ID는 이 unit의
`PUBLICATION_RECEIPT.json`과 `BACKUP_RECEIPT.json`에서 읽는다. 아래 명령은
실제 receipt 값을 직접 연결하므로 사용자가 번호나 commit을 채우기 위해 멈출 필요가 없다.

## 복사할 실행 지시

```text
ROLE=C21H_BOUNDED_NATIVE_EXECUTOR
REPOSITORY=cosmosapjw-quantum/bass_cr
BRANCH=research/cr-c21h-vigilode-bridge-20261019
UNIT=research/cr_c21h_vigilode_bridge_20261019
PUBLICATION_IDENTITY=PUBLICATION_RECEIPT.json
BACKUP_IDENTITY=BACKUP_RECEIPT.json
NATIVE_OWNER=cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4
REUSED_NATIVE_SHA256=1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40
C21G_MANIFEST_SHA256=7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed
RUST_TOOLCHAIN=1.94.1
VIGILODE_PIN=8a8bd409b1d96c7b7421f496d229e119fd3d284e
DIFFSOL_PIN=0.17.1
MAX_CONCURRENT_JOBS=1
ALLOCATED_CPUS=ONE_ACTUALLY_ADMITTED_CPU
PROTECTED_CPU=55
MANUFACTURED_WIRING=PASS_BOTH_SOLVERS_BASE_AND_FD_HALF
NATIVE_SCIENCE_STATUS=NOT_RUN_AT_PUBLICATION_RECHECK_LATEST_RESULTS
GLOBAL_ERROR_BOUND=null

목표는 이미 전달된 C21H 코드를 현재 NCP 환경에서 검증하고, 필요한 locked
compile와 최소 호환 수정 후 아직 완료되지 않은 bounded native job을 실행하는 것이다.
새 solver/physics 기능을 처음부터 구현하지 않는다. C21F 구현·복구·게시·과거
APPLY_C21F_FULL.py 적용을 반복하지 않으며, 중간 branch와 최종본을 자동 merge하지 않는다.
각 완료 단계에서 실행, 게시, 세 저장처 백업, DAG 상태를 별도로 보고한다.
```

## 0. 연구·compile 전에 최신 결과를 먼저 확인

실제 GitHub의 현재 head, 관련 열린/닫힌 PR, branch 및 새 receipt/evidence를 읽는다.
대상은 bass_cr C21F/C21G/C21H, native owner rei_bianchi, VigilODE의 관련 결과다.
Drive·Dropbox·ChatGPT Library의 관련 백업 목록도 다음 페이지가 없을 때까지 확인하고,
가능한 현재 NCP의 기존 결과 디렉터리와 checkpoint를 읽기 전용으로 대조한다.
저장처별 조회 시각·범위·페이지 종료·접근 오류를 기록한다. 접근 오류를 결과 없음이나
과거 백업 삭제로 해석하지 않는다. 과거 ZIP의 NOT_PUBLISHED 문구는 당시 기록이다.
현재 publication receipt가 게시 상태의 기준이다.

최신 C21H PUBLICATION_RECEIPT.json, BACKUP_RECEIPT.json, EXECUTION_MANIFEST.json, 최종 검증 보고,
현재 DAG 및 이 인계문을 읽어 실제 branch/실행 commit/unit 경로를 정한다.
C21G의 PUBLICATION_RECEIPT.json, EXECUTION_MANIFEST.json과 실행 인계도 함께 읽는다.
현재 GitHub 문서 head와 실제 실행 코드를 고정한 commit을 구별한다. 원 baseline의
f8359232df8d0dd4fe91fcdabeb6701eb06089ba를 새 C21H 실행 commit으로 적지 않는다.

새 결과가 있으면 source/fixture/native·bridge binary/설정/receipt/raw SHA를 먼저
검증하고 완료 job을 재사용한다. 완료한 matching job, 기존 35/56개 suite, 기존
광학 전체 검사, C21F 기존 native 행렬을 관성적으로 다시 실행하지 않는다.
필요한 코드는 GitHub에서 직접 읽고 사용자에게 다운로드나 수동 복원을 요구하지 않는다.
프로그램 복원이 실제로 필요할 때만 현재 Files에서 조회한 실제 file ID를 사용한다.

## 1. NCP 자원과 기존 작업을 보존하고 격리 checkout 확보

현재 repository 경로를 먼저 확인한다. 이미 발견한 checkout 안에서 다음을 사용한다.
다른 위치를 임의로 실제 NCP 경로라고 가정하지 않는다.

```bash
set -euo pipefail
C21H_REPO="$(git rev-parse --show-toplevel)"
git -C "$C21H_REPO" rev-parse HEAD
git -C "$C21H_REPO" status --porcelain=v1
git -C "$C21H_REPO" remote -v
git -C "$C21H_REPO" worktree list --porcelain
```

origin이 실제 cosmosapjw-quantum/bass_cr인지 확인한다. dirty files, watcher,
checkpoint, 실행 중인 job, process tree, CPU affinity, RAM·디스크, campaign별
자원 할당과 현재 remote 실행 가능 상태를 읽기 전용으로 남긴다. 과거 remote quota
기록을 현재 상태로 대체하지 않는다. 다른 campaign이나 보호 CPU 55를 사용하지 않는다.
Affinity에 들어 있다는 사실만으로 독점 가용성을 가정하지 않는다. 현재 자원 배정에서
허용된 CPU ID 하나를 명시적으로 확인한다. 이는 CPU 번호 1을 고정하라는 뜻이 아니다.

현재 checkout을 reset/clean/stash/rebase하지 않는다. watcher를 중단하거나 기존
checkpoint를 수정하지 않는다. 다음은 현재 게시 branch를 fetch한 뒤 같은 unit의
실제 publication/backup receipt를 읽는 명령이다. JSON을 shell code로 eval하지 않는다.
content commit과 문서 receipt head는 별도로 유지한다. receipt를 추가한 문서 commit이
content commit 이후에 생길 수 있으므로 receipt는 먼저 최신 문서 head에서 읽는다.

```bash
C21H_UNIT_REL='research/cr_c21h_vigilode_bridge_20261019'
C21H_METADATA_BRANCH='research/cr-c21h-vigilode-bridge-20261019'
git -C "$C21H_REPO" fetch --no-tags origin "$C21H_METADATA_BRANCH"
C21H_DOCUMENT_HEAD="$(git -C "$C21H_REPO" rev-parse FETCH_HEAD)"
C21H_PUBLICATION_JSON="$(git -C "$C21H_REPO" show "$C21H_DOCUMENT_HEAD:$C21H_UNIT_REL/PUBLICATION_RECEIPT.json")"
C21H_BACKUP_JSON="$(git -C "$C21H_REPO" show "$C21H_DOCUMENT_HEAD:$C21H_UNIT_REL/BACKUP_RECEIPT.json")"
export C21H_PUBLICATION_JSON C21H_BACKUP_JSON
python3 - <<'C21H_READ_RECEIPTS'
import json, os, re
publication=json.loads(os.environ['C21H_PUBLICATION_JSON'])
if publication.get('status')!='PUBLISHED':
    raise SystemExit('C21H_PUBLICATION_NOT_CONFIRMED_READ_BLOCKER_RECEIPT')
if publication['repository']!='cosmosapjw-quantum/bass_cr':
    raise SystemExit('C21H_PUBLICATION_REPOSITORY_MISMATCH')
if not re.fullmatch(r'[0-9a-f]{40}',publication['content_commit']):
    raise SystemExit('C21H_CONTENT_COMMIT_DOMAIN')
if not isinstance(publication['branch'],str) or not publication['branch']:
    raise SystemExit('C21H_PUBLICATION_BRANCH_MISSING')
print(json.dumps({key:publication[key] for key in
                 ('repository','branch','content_commit','pull_request')},indent=2))
print(json.dumps(json.loads(os.environ['C21H_BACKUP_JSON']),indent=2))
C21H_READ_RECEIPTS
C21H_EXECUTION_COMMIT="$(python3 -c 'import json,os; print(json.loads(os.environ["C21H_PUBLICATION_JSON"])["content_commit"])')"
C21H_PUBLISHED_BRANCH="$(python3 -c 'import json,os; print(json.loads(os.environ["C21H_PUBLICATION_JSON"])["branch"])')"
C21H_PR_URL="$(python3 -c 'import json,os; print(json.loads(os.environ["C21H_PUBLICATION_JSON"])["pull_request"]["url"])')"
git -C "$C21H_REPO" cat-file -e "${C21H_EXECUTION_COMMIT}^{commit}"
git -C "$C21H_REPO" merge-base --is-ancestor "$C21H_EXECUTION_COMMIT" "$C21H_DOCUMENT_HEAD"
```

receipt 파일을 읽지 못하면 실제 오류와 마지막 확인 head를 기록하고 현재 GitHub 및
백업 receipt를 더 조회한다. 임의 PR 번호·content commit·backup ID로 대체하거나
사용자에게 그 값을 채우도록 요청하지 않는다. 원본 checkout의 부모 디렉터리를 실제로
확인하고 가용한 writable 공간이면 다음과 같이 충돌 없는 작업 root를 만든다.
부모 공간이 부적합하면 현재 NCP에서 확인한 writable 작업 parent를 실행자가 선택한다.

```bash
C21H_WORK_PARENT="${C21H_WORK_PARENT:-$(dirname -- "$C21H_REPO")}"
C21H_TASK_ROOT="$(mktemp -d -- "$C21H_WORK_PARENT/c21h-ncp-XXXXXXXX")"
C21H_WORKTREE="$C21H_TASK_ROOT/worktree"
C21H_RUN_ROOT="$C21H_TASK_ROOT/results"
mkdir -- "$C21H_RUN_ROOT"
git -C "$C21H_REPO" worktree add --detach "$C21H_WORKTREE" "$C21H_EXECUTION_COMMIT"
git -C "$C21H_WORKTREE" rev-parse HEAD
git -C "$C21H_WORKTREE" status --porcelain=v1
```

기존에 동일 content commit의 깨끗한 격리 worktree가 있고 완료 job을 그 context에서
재사용해야 한다면 그 실제 경로를 재사용한다. 새 worktree를 무조건 추가하지 않는다.
위 단계에서 읽은 두 receipt의 원문과 문서 head는 새 intake 증거로 보존한다.


단계 표시: `INTAKE=COMPLETE/PARTIAL`, `RESOURCE_ADMISSION=READY/BLOCKED`,
`SOURCE_PIN=VERIFIED/FAILED`, `PUBLICATION=기존 최종 receipt`, `BACKUP=실제 확인 수준`.

## 2. 실행 경로와 기존 native binary를 실제 파일에 연결

아래 source 경로는 검증한 worktree에서 정한다. C21H_NATIVE와 C21H_CPU는 0–1단계에서
읽은 실제 native receipt/파일과 현재 campaign 할당 결과에 실행자가 직접 연결한다.
사용자에게 변수 채우기나 추가 승인을 요청하는 단계로 바꾸지 않는다. 현재 자원 배정이
없거나 확인할 수 없으면 그 실제 자원 상태를 BLOCKED로 보고하고 완료된 작업을 보존한다.

```bash
C21H_UNIT="$C21H_WORKTREE/$C21H_UNIT_REL"
C21H_SOURCE="$C21H_WORKTREE/research/cr_c21e_event_native_20261018"
C21H_C21G_UNIT="$C21H_WORKTREE/research/cr_c21g_reference_refinement_20261019"
C21H_BASELINE="$C21H_SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export RAYON_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
```

기존 receipt가 가리키는 native 파일의 SHA가 위 REUSED_NATIVE_SHA256와 같고 현재
환경에서 사용할 수 있으면 재사용한다. native binary가 없거나 사용할 수 없을 때만
현재 C21F source의 build_native.sh로 pinned owner를 빌드한다. 새 빌드는 owner,
input SHA, binary SHA, owner archive, 실제 build exit와 stdout/stderr를 보존한다.
새 binary에는 실제 검증 build directory를 `--build-dir`로 전달한다. 이미 검증한
binary를 다시 감사하거나 C21F 과거 패치를 적용하지 않는다.

다음 배열의 경로도 실제 검증값이어야 한다. 원래 pinned binary를 재사용하면
추가 build directory가 필요 없을 수 있다.

```bash
C21H_NATIVE_ARGS=(--native "$C21H_NATIVE")
if [[ -n "${C21H_NATIVE_BUILD_DIR:-}" ]]; then
  C21H_NATIVE_ARGS+=(--build-dir "$C21H_NATIVE_BUILD_DIR")
fi
```

## 3. 현재 source 검증과 Rust 1.94.1 locked bridge build

기존에 동일 runtime/source/binary와 toolchain에 대해 완료한 검증·build receipt가
있으면 먼저 재사용 가능성을 평가한다. 새 build가 필요하면 실제 설치된 Rust 1.94.1의
cargo/rustc 경로를 확인한다. rustup이 있는 환경에서는 다음으로 정확한 toolchain을
선택할 수 있다. 없다면 실제 제공된 1.94.1 도구 경로를 바인딩한다.

```bash
C21H_RUSTC="$(rustup which --toolchain 1.94.1 rustc)"
C21H_CARGO="$(rustup which --toolchain 1.94.1 cargo)"
"$C21H_RUSTC" --version --verbose
"$C21H_CARGO" --version
```

새 NCP context에 대응하는 완료 plan이 아직 없으면 create-only plan을 한 번 만든다.
현재 입력·소스 manifest의 byte identity를 검증하는 단계이며 native/ODE는 실행하지 않는다.
완료된 matching plan이 있으면 receipt를 재사용한다.

```bash
C21H_PLAN_OUT="$C21H_RUN_ROOT/plan"
python3 "$C21H_UNIT/run_pilot.py" plan \
  --source-dir "$C21H_SOURCE" --c21g-unit "$C21H_C21G_UNIT" \
  --baseline-dir "$C21H_BASELINE" --out "$C21H_PLAN_OUT"
```

bridge의 실제 build helper 경로는 `rust_bridge/build_bridge.sh`이다. 새 target directory를
사용한다. 스크립트는 `cargo build --locked --release --jobs 1`을 실행하고 빌드 전후
Cargo.toml/Cargo.lock/src/main.rs/build helper identity를 보존한다. Cargo.lock을
다시 생성하거나 dependencies를 임의로 최신화하지 않는다. `--offline`은 필요한 모든
locked source가 실제 cache에 있는 경우에만 붙인다. taskset 사용 가능성과 CPU 배정을
확인한 Linux NCP에서 다음을 사용한다.

```bash
C21H_BRIDGE_TARGET="$C21H_RUN_ROOT/bridge_build"
taskset -c "$C21H_CPU" bash "$C21H_UNIT/rust_bridge/build_bridge.sh" \
  --cargo "$C21H_CARGO" --rustc "$C21H_RUSTC" \
  --target-dir "$C21H_BRIDGE_TARGET"
```

실제 BUILD_RECEIPT.json의 exit_code, cargo_exit_code, source_files_unchanged,
toolchain, dependency pin, source_files와 실제 binary SHA를 대조한다. 성공 receipt에
기록된 실제 binary 경로와 해당 receipt를 다음처럼 연결한다. 이미 검증한 matching
build를 재사용하는 경우에는 그 실제 receipt 경로를 사용한다. 디렉터리 이름만 보고
성공을 추정하지 않는다.

```bash
C21H_BRIDGE_RECEIPT="$C21H_BRIDGE_TARGET/BUILD_RECEIPT.json"
C21H_BRIDGE="$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["exit_code"]==0 and r["source_files_unchanged"]; print(r["binary"])' "$C21H_BRIDGE_RECEIPT")"
```

게시된 두 solver의 제조 wiring은 위 4건으로 PASS다. 새로운 NCP 실행에서 실패가
발생하면 그 구체적인 환경·입력·실행 원인을 구별한다. typed-stop/endpoint 실패를
clipping, 보간, floor, silent fallback, 임의 tolerance 완화로 PASS 처리하지 않는다. 최소 호환 수정이 필요하면 별도 source
변경 및 그 영향을 기록하고 관련 검사만 수행한 다음 새로운 실행 identity로 게시한다.

단계 표시: `BRIDGE_BUILD=COMPLETE/FAILED/REUSED`, `SOLVER_WIRING=solver별 실제 상태`,
`NATIVE_EXECUTION=아직 시작하지 않은 상태`, `PUBLICATION/BACKUP/DAG=각각 실제 진행`.

## 4. C21H native 4 base와 성공별 fd_half를 순차 실행

| Fixture | Method | Base | FD followup |
| --- | --- | --- | --- |
| common_ic | vigilode-rodas5p | 독립 1 job | 같은 context의 완료 base 검증 후 1 job |
| native_source | vigilode-rodas5p | 독립 1 job | 같은 context의 완료 base 검증 후 1 job |
| common_ic | diffsol-bdf | 독립 1 job | 같은 context의 완료 base 검증 후 1 job |
| native_source | diffsol-bdf | 독립 1 job | 같은 context의 완료 base 검증 후 1 job |

먼저 목록을 최신 결과와 대조하여 각 행을 READY/COMPLETE/FAILED/BLOCKED로 표시한다.
동시에 하나의 job만 허용한다. 각 base 성공 직후 그 base의 fd_half를 처리하는 순서가
가능하며, 마지막 결과는 base 최대 4개 + 조건부 fd_half 최대 4개다. 이미 완료된
matching job을 다시 실행하지 않는다. 실행마다 fresh Python process를 사용한다.

한 base에 대한 실제 CLI는 다음과 같다. C21H_FIXTURE와 C21H_METHOD는 위 표의 아직
실행할 행으로 정하고, 출력은 항상 새 경로다. shell loop로 8개를 무조건 제출하지 않는다.

```bash
C21H_BASE_OUT="$C21H_RUN_ROOT/${C21H_FIXTURE}_${C21H_METHOD}_base"
python3 "$C21H_UNIT/run_pilot.py" native \
  --source-dir "$C21H_SOURCE" --c21g-unit "$C21H_C21G_UNIT" \
  --baseline-dir "$C21H_BASELINE" \
  --bridge "$C21H_BRIDGE" --bridge-build-receipt "$C21H_BRIDGE_RECEIPT" \
  "${C21H_NATIVE_ARGS[@]}" --cpu "$C21H_CPU" \
  --fixture "$C21H_FIXTURE" --method "$C21H_METHOD" \
  --variant base --out "$C21H_BASE_OUT"
```

완료 여부는 terminal JOB_RECEIPT.json과 실제 payload SHA로 판단한다. stdout에 경로가
출력됐다는 사실은 성공 판정이 아니다. 실행·native 호출 여부·물리 수지·수치 비교를
분리한다. 해당 base가 COMPLETE이고 command=native, fixture/method/source/input/
bridge/native identity와 모든 payload가 일치할 때만 다음을 실행한다.
C21H_VERIFIED_BASE_OUT에는 방금 검증한 실제 완료 디렉터리를 연결한다. 이전 receipt를
재사용하는 경우도 그 실제 경로를 유지한다. fixture/method는 해당 base와 동일해야 한다.

```bash
C21H_FD_OUT="$C21H_RUN_ROOT/${C21H_FIXTURE}_${C21H_METHOD}_fd_half"
python3 "$C21H_UNIT/run_pilot.py" native \
  --source-dir "$C21H_SOURCE" --c21g-unit "$C21H_C21G_UNIT" \
  --baseline-dir "$C21H_BASELINE" \
  --bridge "$C21H_BRIDGE" --bridge-build-receipt "$C21H_BRIDGE_RECEIPT" \
  "${C21H_NATIVE_ARGS[@]}" --cpu "$C21H_CPU" \
  --fixture "$C21H_FIXTURE" --method "$C21H_METHOD" \
  --variant fd_half --base-job "$C21H_VERIFIED_BASE_OUT" --out "$C21H_FD_OUT"
```

fd_half는 gas FD와 explicit partial-time FD의 probe scale을 모두 절반으로 한다.
현재 runner는 base를 실행 전후 모두 검증하며 source/input/binary identity에는
기록된 경로도 포함된다. 다른 host나 다른 build path의 receipt를 편집해서 binding을
맞추지 않는다. 기존 matching 결과는 보존하고, 원래 context가 유지되지 않아 followup을
연결할 수 없으면 그 사유를 BLOCKED로 반환한다. 완료 base를 자동으로 다시 만들지 않는다.

예산은 job당 wall 300초, 원 RHS/native 최대 200000회, 단일 native 호출은
`min(15초, 남은 job 시간)`이다. rtol=2e-11, 고정 dimensional scale에 대한
atol multiplier=2e-14, event cell max-step divisor=8을 유지한다. underflow와
log-survivor를 보존한다. 실패·timeout·domain 오류는 새 raw와 함께 기록하고
기존 디렉터리에서 resume하거나 실패 출력을 덮어쓰지 않는다.

## 5. C21G READY와 과학 판정을 독립 유지

C21G의 기존 reference 8개(common_ic/native_source × L1/L2/L3/L3M) 및 조건부
native_source history 4개(FULLMID/MIDPHOTO_ENDMICRO × n128/n256)는 별도 DAG다.
최신 완료 receipt가 발견되면 검증해 재사용하고, 그렇지 않으면 원래 READY 조건을
유지한다. C21H 완료를 C21G ladder 완료로 대체하지 않고, 이 인계에서 C21G 12개를
자동으로 추가 제출하지 않는다. 기존 L0 및 n8/16/32/64를 재사용한다.

판정은 다음 항목을 나누어 작성한다.

1. **실행:** exit/status, native launch/calls/exit, 제한 도달, source/binary drift 여부.
2. **동일성:** 실행 commit, source manifest, fixture 본문·canonical SHA, baseline/raw SHA,
   native owner/build/binary, bridge source/build/binary, toolchain과 실제 controls.
3. **물리 수지:** INDEPENDENT_BALANCES.json과 원 ledger, photon/energy/source/escape/
   work 항목 및 underflow/log-survivor. 과정 완료만으로 물리 수지 PASS를 주지 않는다.
4. **수치:** COMPARE_TO_PINNED_L0.json, 완료된 독립 C21G tier가 있을 때의 추가 비교,
   COMPARE_FD_HALF_TO_BASE.json, accepted grid·solver counters·FD nodes. local tolerance,
   FD 민감도, solver 간 차이와 전역 IVP 오차를 구별한다.
5. **성능:** 같은 fixture/source/hardware/resource 조건과 실제 raw가 있는 범위만 보고한다.
   제조 wiring이나 VigilODE 외부 benchmark만으로 bass_cr native 가속을 주장하지 않는다.

global_error_bound=null을 유지한다. 차이가 0이라고 IVP 오차 0으로 선언하지 않는다.
Full48, source-age, spectral, angular, Case B, signed Bianchi, full EoR,
standalone Grackle driver parity는 각각의 독립 검증 전까지 HOLD다.

## 6. 새 결과의 게시·세 저장처 백업·DAG와 반환

새 job마다 terminal receipt, input/source/native/build identity, fixture 본문,
PLAN/LIVE_INVENTORY, result/ledger/comparison, accepted grid, derivative nodes,
RPC/native raw, stdout/stderr, 실패·cleanup 증거를 실제 파일 목록으로 보존한다.
폴더 전체 payload manifest를 만들어 상대경로·bytes·SHA256를 기록한다. 루트 terminal
receipt의 자기참조만 피하고 하위 JOB_RECEIPT.json을 누락하지 않는다.

새 데이터만 create-only로 GitHub에 게시한다. 기존 PR81 복구본, PR84 결과,
중간 branch, checkpoint와 원 raw는 그대로 보존한다. commit·실행 source·최종 문서
head가 다르면 각각을 기록하고 doc-only 변경을 표시한다. 작은 수정이 있었으면
바뀐 코드·이유·영향 검사와 새 실행 identity를 분리해서 게시한다. force push나 자동 merge를 하지 않는다.

Drive, Dropbox, ChatGPT Library는 각각 현재 실제 존재하는 bass_cr 백업 폴더를
조회해서 대상과 provider ID를 확정한다. 과거 인계의 경로나 ID를 현재 확인 없이
재사용하지 않는다. /BASS_DERIVATION_DOSSIERS_20260912/bass_cr는 기존 기록을
찾는 단서이며, 각 provider의 실제 현재 폴더 존재 여부를 확인한다. 새 결과 묶음만
새 이름으로 저장하고, archive SHA256·bytes·payload 수·CRC와 실시한 readback 범위를
기록한다. 저장 성공, metadata 확인, 다운로드 후 전체 SHA/CRC/payload 검증을 구별한다.
실패한 저장처가 있으면 그 상태를 명시하고 다른 완료분을 지우지 않는다.

최종 반환 본문에는 최소한 다음 표를 포함한다.

| 단계 | 실행·검증 상태 | GitHub 게시 | Drive | Dropbox | Library | DAG / 다음 단계 |
| --- | --- | --- | --- | --- | --- | --- |
| 최신 결과 intake / 자원 | 실제 완료·오류·조회 범위 | 실제 head/receipt | 조회 범위 | 조회 범위 | 조회 범위 | 현재 READY/BLOCKED |
| bridge compile | 실제 exit / reused / failed | 실제 commit | 실제 ID/검증 수준 | 실제 ID/검증 수준 | 실제 ID/검증 수준 | native admission |
| base 각 4행 | 각각 COMPLETE/FAILED/REUSED/BLOCKED | 실제 receipt | 실제 ID/검증 수준 | 실제 ID/검증 수준 | 실제 ID/검증 수준 | 해당 FD READY/HOLD |
| fd_half 각 4행 | 각각 완료/실패/조건 미충족 | 실제 receipt | 실제 ID/검증 수준 | 실제 ID/검증 수준 | 실제 ID/검증 수준 | 수치 평가 |
| 수지·수렴·성능 평가 | 각각 관측·미평가 | 실제 평가 문서 | 실제 ID | 실제 ID | 실제 ID | 기존 HOLD 유지/독립 판정 |

실제 repo/branch/실행 commit/문서 head, source·fixture·raw SHA, binary/build identity,
runtime/controls/counters, 완료·실패·재사용 목록, 자원 보존 여부, 세 저장처의 실제
backup receipt와 현재 DAG를 연구 스레드로 반환한다. 빈 값이나 미실행 항목을
임의 PASS/COMPLETE로 채우지 않는다.
