# F1 NCP bounded native admission run handoff

Role: **BASS_NCLOUD_F1_NATIVE_EXECUTOR_AND_EVIDENCE_PUBLISHER**.

이번 세션은 이미 승인된 F1 native admission을 정확히 한 번 실행하고, 결과를 GitHub execution evidence로 게시한다.
F2/F3는 시작하지 않는다.

## Frozen implementation

implementation commit:
`8236887dd8869de57522d5c87a48972f287969fe`

implementation tree:
`d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae`

control/evidence branch:
`research/fnd-ncloud-f1-engine-admission-20260928`

active authorization file:
`research/foundation_rebuild/ncloud_f1_engine_admission_20260928/RUN_AUTHORIZATION_20260928.json`

storage approval:
`research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_STORAGE_APPROVAL.json`

Owner-approved bounds:
- max_wall_seconds = 7200
- spending_limit_krw = 8000
- native_admission_allowed = true
- F1 only

## 1. Preserve current checkout

Do not switch, reset, clean, stash, rebase or merge the user's current source checkout.

```bash
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" status --short
git -C "$REPO" rev-parse HEAD
git -C "$REPO" rev-parse 'HEAD^{tree}'
git -C "$REPO" branch --show-current || true
```

## 2. Fetch control branch and verify authorization

```bash
CONTROL_BRANCH='research/fnd-ncloud-f1-engine-admission-20260928'
git -C "$REPO" fetch origin "refs/heads/$CONTROL_BRANCH:refs/remotes/origin/$CONTROL_BRANCH"
CONTROL_REF="refs/remotes/origin/$CONTROL_BRANCH"

AUTH_PATH='research/foundation_rebuild/ncloud_f1_engine_admission_20260928/RUN_AUTHORIZATION_20260928.json'
STORAGE_PATH='research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_STORAGE_APPROVAL.json'

git -C "$REPO" show "$CONTROL_REF:$AUTH_PATH" | jq .
git -C "$REPO" show "$CONTROL_REF:$STORAGE_PATH" | jq .
```

Require exact authorization fields:

```text
schema = BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1
implementation_commit = 8236887dd8869de57522d5c87a48972f287969fe
implementation_tree = d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae
native_admission_allowed = true
max_wall_seconds = 7200
spending_limit_krw = 8000
f2_f3_execution_allowed = false
```

Mismatch => STOP_F1_BLOCKED_AUTHORIZATION_DRIFT. Do not repair values.

## 3. Use existing approved CB1 root storage

The owner explicitly approved the existing NCP default CB1 100 GB block storage `/dev/vda` for F1.
F0 host evidence observed `/dev/vda2` ext4 mounted at `/` with about 91.4 GB free.

Use:

```bash
ROOT=/root/.local/state/bass_f1
mkdir -p "$ROOT"
test -w "$ROOT" || exit 3
findmnt -T "$ROOT"
df -hT "$ROOT"
AVAILABLE_KB="$(df -Pk "$ROOT" | awk 'NR==2 {print $4}')"
test "${AVAILABLE_KB:-0}" -ge 5242880 || {
  echo 'F1_WORKSPACE_FREE_SPACE_BELOW_5G'
  exit 3
}
```

Do not format `/dev/vda`, do not create a new filesystem, do not mount a new volume, do not use sudo, and do not alter `/etc/fstab`.

## 4. Create exact implementation worktree

```bash
IMPL='8236887dd8869de57522d5c87a48972f287969fe'
IMPL_TREE='d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae'

git -C "$REPO" cat-file -e "$IMPL^{commit}"
test "$(git -C "$REPO" rev-parse "$IMPL^{tree}")" = "$IMPL_TREE" || exit 3

WORKTREE="$ROOT/code/f1_exec_${IMPL:0:12}"
if test -e "$WORKTREE"; then
  test "$(git -C "$WORKTREE" rev-parse HEAD)" = "$IMPL" || { echo WORKTREE_IDENTITY_MISMATCH; exit 3; }
  test -z "$(git -C "$WORKTREE" status --porcelain)" || { echo WORKTREE_NOT_CLEAN; exit 3; }
else
  mkdir -p "$(dirname "$WORKTREE")"
  git -C "$REPO" worktree add --detach "$WORKTREE" "$IMPL"
fi
```

Never run the scientific runner from the later control/docs HEAD. The runner must see HEAD/tree equal to the frozen implementation identity.

## 5. Materialize external authorization from control branch

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
AUTH_DIR="$ROOT/authorization/$STAMP"
mkdir -p "$AUTH_DIR"
AUTH="$AUTH_DIR/RUN_AUTHORIZATION.json"
git -C "$REPO" show "$CONTROL_REF:$AUTH_PATH" > "$AUTH"

jq -e '
  .schema == "BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1" and
  .implementation_commit == "8236887dd8869de57522d5c87a48972f287969fe" and
  .implementation_tree == "d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae" and
  .native_admission_allowed == true and
  .max_wall_seconds == 7200 and
  .spending_limit_krw == 8000
' "$AUTH" >/dev/null || exit 3
```

## 6. Reuse or create exact numerical environment

Prefer the already admitted F0 venv only if it still exists and exact pins match:

```bash
F0_ENV=/root/.local/state/bass_f0/env/tp2e_f0_20260928T045058Z
if test -x "$F0_ENV/bin/python"; then
  PY="$F0_ENV/bin/python"
else
  ENV="$ROOT/env/f1_$STAMP"
  python3 -m venv "$ENV"
  PY="$ENV/bin/python"
  "$PY" -m pip install --only-binary=:all: -r "$WORKTREE/research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/requirements-tested.txt"
fi

"$PY" - <<'PY'
import numpy, scipy, pytest, mpmath
assert numpy.__version__ == '2.3.5'
assert scipy.__version__ == '1.17.0'
assert pytest.__version__ == '9.0.2'
assert mpmath.__version__ == '1.3.0'
print('NUMERIC_ENV_OK')
PY

g++ --version | head -n 1
```

If exact pins or g++ are unavailable, stop with an environment/build blocker. Do not upgrade/fallback automatically.

## 7. Thread policy and input identity

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_DYNAMIC=FALSE
export MKL_DYNAMIC=FALSE

ARCHIVE="$WORKTREE/research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip"
printf '%s  %s\n' \
  '630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35' "$ARCHIVE" | sha256sum -c -
```

## 8. Run F1 exactly once

```bash
RUN_ID="$STAMP"
OUT="$ROOT/runs/f1_native_$RUN_ID"
LOG="$ROOT/receipts/F1_RUN_$RUN_ID.log"
mkdir -p "$ROOT/runs" "$ROOT/receipts"

set +e
"$PY" "$WORKTREE/research/foundation_rebuild/ncloud_f1_engine_admission_20260928/runtime/run_f1_engine_admission.py" \
  --authorization "$AUTH" \
  --archive "$ARCHIVE" \
  --out "$OUT" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e
printf 'F1_EXIT=%s\nOUT=%s\nRUN_ID=%s\n' "$RC" "$OUT" "$RUN_ID"
```

Do not automatically rerun for any nonzero exit or scientific failure.

## 9. Inspect result

```bash
test -f "$OUT/RETURN_REPORT.json" && jq . "$OUT/RETURN_REPORT.json"
find "$OUT" -maxdepth 2 -type f -printf '%P %s bytes\n' | sort
sha256sum "$OUT"/* 2>/dev/null || true
```

Success status is exactly `F1_ENGINE_ADMISSION_PASS`. Any other status is preserved as evidence.

## 10. Publish F1 execution evidence to GitHub

Whether PASS or FAIL, publish the completed run according to:
`research/foundation_rebuild/ncloud_c64g3_20260928/NCP_GITHUB_EVIDENCE_UPLOAD_KO.md`.

Destination:

```text
research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1/<RUN_ID>/
```

Publish allowlisted/sanitized:
- RETURN_REPORT.json
- ENGINE_BUILD.json if present
- ENGINE_IDENTITY.json if present
- ENGINE_ADMISSION.json if present
- REPRESENTATIVE_PARITY.json if present
- METRIC_CONNECTION_PARITY.json if present
- PROGRESS.jsonl if present
- FOCUSED_TESTS.log
- sanitized run/environment/storage receipts
- EVIDENCE_MANIFEST.json
- SANITIZATION.json

Use a fresh evidence worktree based on the latest remote control branch after the run. Do not commit from the frozen implementation worktree.

Commit:
`data(ncloud): publish F1 native admission evidence <RUN_ID>`

Push non-force to:
`research/fnd-ncloud-f1-engine-admission-20260928`.

Then verify remote ref/tree and intended evidence-only diff.

## 11. Stop boundary

After publishing F1 evidence, stop.

Do not start F2/F3, worker calibration, CF4, DOP853, capture, threshold changes, or a second F1 run.

Final output block:

```text
F1_NCP_RUN_PUBLISHED
branch = ...
head = ...
tree = ...
implementation_commit = 8236887dd8869de57522d5c87a48972f287969fe
implementation_tree = d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae
run_id = ...
exit_code = ...
scientific_status = ...
wall_seconds = ...
authorization_wall_seconds = 7200
authorization_spending_limit_krw = 8000
workspace = /root/.local/state/bass_f1
storage = CB1 100GB /dev/vda (root filesystem /dev/vda2)
evidence_manifest_sha256 = ...
return_report_sha256 = ...
remote_ref_verified = true
remote_tree_verified = true
```