# F1-R2 authorized NCP parallel admission run handoff

Role: **BASS_NCLOUD_F1_R2_EXECUTOR_AND_EVIDENCE_PUBLISHER**.

Run the frozen R2 implementation exactly once under the owner-approved 3600 s / 4000 KRW bound.
Publish PASS or FAIL evidence and stop. Do not begin F2/F3.

## Frozen implementation

- commit: `f1d69165c6d1e799d9474db23166cb665880576f`
- tree: `5842046d6bf9d4865566dad28a3fec5b22235f41`

Control branch:
`research/fnd-ncloud-f1-r2-parallel-admission-20260928`

Active authorization:
`research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/RUN_AUTHORIZATION_20260928_R2.json`

Host/storage approval:
`research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_HOST_STORAGE_APPROVAL.json`

Owner-approved bounds:
- max_wall_seconds = 3600
- spending_limit_krw = 4000
- configured vCPU = 64
- configured memory = 128 GB
- preferred workers = 60
- existing storage = CB1 100 GB `/dev/vda`, root partition `/dev/vda2` ext4

## 1. Preserve current source checkout

Do not switch/reset/clean/stash/rebase/merge the user's current checkout.

```bash
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" status --short
git -C "$REPO" rev-parse HEAD
git -C "$REPO" rev-parse 'HEAD^{tree}'
git -C "$REPO" branch --show-current || true
```

## 2. Fetch control branch and verify active authorization

```bash
CONTROL_BRANCH='research/fnd-ncloud-f1-r2-parallel-admission-20260928'
git -C "$REPO" fetch origin "refs/heads/$CONTROL_BRANCH:refs/remotes/origin/$CONTROL_BRANCH"
CONTROL_REF="refs/remotes/origin/$CONTROL_BRANCH"

BASE='research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928'
AUTH_PATH="$BASE/RUN_AUTHORIZATION_20260928_R2.json"
HOST_PATH="$BASE/R2_HOST_STORAGE_APPROVAL.json"

git -C "$REPO" show "$CONTROL_REF:$AUTH_PATH" | jq .
git -C "$REPO" show "$CONTROL_REF:$HOST_PATH" | jq .
```

Require exactly:

```text
schema = BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1
implementation_commit = f1d69165c6d1e799d9474db23166cb665880576f
implementation_tree = 5842046d6bf9d4865566dad28a3fec5b22235f41
native_admission_allowed = true
max_wall_seconds = 3600
spending_limit_krw = 4000
preferred_workers = 60
f2_f3_execution_allowed = false
```

Any drift => stop without running.

## 3. Host/resource preflight before scientific runner

Use the already-approved root storage. Do not create `/data` or a new volume.

```bash
ROOT=/root/.local/state/bass_f1_r2
mkdir -p "$ROOT"
test -w "$ROOT" || exit 3

python3 - <<'PY'
import json, os
mem={}
with open('/proc/meminfo') as f:
    for line in f:
        if line.startswith(('MemTotal:', 'MemAvailable:')):
            k,v=line.split(':',1); mem[k[:-1]]=int(v.strip().split()[0])*1024
row={'affinity_count':len(os.sched_getaffinity(0)), **mem}
print(json.dumps(row,indent=2))
assert row['affinity_count'] >= 64, row
assert row['MemTotal'] >= 120_000_000_000, row
assert row['MemAvailable'] >= 5_368_709_120, row
PY

findmnt -T "$ROOT"
df -hT "$ROOT"
AVAILABLE_KB="$(df -Pk "$ROOT" | awk 'NR==2 {print $4}')"
test "${AVAILABLE_KB:-0}" -ge 5242880 || { echo R2_WORKSPACE_FREE_SPACE_BELOW_5G; exit 3; }
```

Do not format `/dev/vda`; do not mount/create a new filesystem; do not use sudo or edit fstab.

## 4. Create exact frozen implementation worktree

```bash
IMPL='f1d69165c6d1e799d9474db23166cb665880576f'
IMPL_TREE='5842046d6bf9d4865566dad28a3fec5b22235f41'
git -C "$REPO" cat-file -e "$IMPL^{commit}"
test "$(git -C "$REPO" rev-parse "$IMPL^{tree}")" = "$IMPL_TREE" || exit 3

WORKTREE="$ROOT/code/r2_exec_${IMPL:0:12}"
if test -e "$WORKTREE"; then
  test "$(git -C "$WORKTREE" rev-parse HEAD)" = "$IMPL" || { echo R2_WORKTREE_IDENTITY_MISMATCH; exit 3; }
  test -z "$(git -C "$WORKTREE" status --porcelain)" || { echo R2_WORKTREE_NOT_CLEAN; exit 3; }
else
  mkdir -p "$(dirname "$WORKTREE")"
  git -C "$REPO" worktree add --detach "$WORKTREE" "$IMPL"
fi
```

Do not run the scientific runner from the later control/docs HEAD.

## 5. Materialize authorization externally

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
AUTH_DIR="$ROOT/authorization/$STAMP"
mkdir -p "$AUTH_DIR"
AUTH="$AUTH_DIR/RUN_AUTHORIZATION.json"
git -C "$REPO" show "$CONTROL_REF:$AUTH_PATH" > "$AUTH"

jq -e '
  .schema == "BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1" and
  .implementation_commit == "f1d69165c6d1e799d9474db23166cb665880576f" and
  .implementation_tree == "5842046d6bf9d4865566dad28a3fec5b22235f41" and
  .native_admission_allowed == true and
  .max_wall_seconds == 3600 and
  .spending_limit_krw == 4000 and
  .preferred_workers == 60
' "$AUTH" >/dev/null || exit 3
```

## 6. Exact numerical environment

Use an existing Python only if it is Python 3.12.3 with exact pins:
`numpy 2.3.5`, `scipy 1.17.0`, `pytest 9.0.2`, `mpmath 1.3.0`.

If no existing interpreter meets the pins, create one isolated venv and install exactly the pinned wheels.
No apt/system Python mutation, no fallback versions.

```bash
PY=python3
if ! "$PY" - <<'PY'
import sys, numpy, scipy, pytest, mpmath
assert sys.version_info[:3] == (3,12,3)
assert numpy.__version__ == '2.3.5'
assert scipy.__version__ == '1.17.0'
assert pytest.__version__ == '9.0.2'
assert mpmath.__version__ == '1.3.0'
PY
then
  ENV="$ROOT/env/r2_$STAMP"
  python3 -m venv "$ENV"
  PY="$ENV/bin/python"
  "$PY" -m pip install --only-binary=:all: -r "$WORKTREE/research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/requirements-tested.txt"
fi
```

Verify `g++` is available. Do not upgrade it automatically.

## 7. Fixed thread policy

Before launching the runner:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_DYNAMIC=FALSE
export MKL_DYNAMIC=FALSE
```

## 8. Historical archive identity

```bash
ARCHIVE="$WORKTREE/research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip"
printf '%s  %s\n' '630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35' "$ARCHIVE" | sha256sum -c -
```

## 9. Run exactly once and sample resource utilization

Do not use an external `timeout`; the R2 runner owns its 3600 s budget and durable interruption handling.

```bash
RUN_ID="$STAMP"
OUT="$ROOT/runs/r2_native_$RUN_ID"
RECEIPT_DIR="$ROOT/receipts/$RUN_ID"
mkdir -p "$ROOT/runs" "$RECEIPT_DIR"
LOG="$RECEIPT_DIR/R2_RUN.log"
RESOURCE_LOG="$RECEIPT_DIR/RESOURCE_SAMPLES.tsv"

RUNNER="$WORKTREE/research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/runtime_r2/run_f1_r2_parallel.py"

set +e
"$PY" "$RUNNER" --authorization "$AUTH" --archive "$ARCHIVE" --out "$OUT" > >(tee "$LOG") 2>&1 &
RUN_PID=$!

printf 'utc\tparent_pid\tchild_count\tchild_pcpu_sum\tchild_rss_kib_sum\tmem_available_kib\tprogress_tail\n' > "$RESOURCE_LOG"
while kill -0 "$RUN_PID" 2>/dev/null; do
  CHILD_ROWS="$(ps --no-headers --ppid "$RUN_PID" -o pcpu=,rss= 2>/dev/null || true)"
  CHILD_COUNT="$(printf '%s\n' "$CHILD_ROWS" | awk 'NF{n++} END{print n+0}')"
  CPU_SUM="$(printf '%s\n' "$CHILD_ROWS" | awk 'NF{s+=$1} END{printf "%.1f",s+0}')"
  RSS_SUM="$(printf '%s\n' "$CHILD_ROWS" | awk 'NF{s+=$2} END{print s+0}')"
  MEM_KB="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
  TAIL="$(tail -n 1 "$OUT/PROGRESS.jsonl" 2>/dev/null | tr '\t\n' '  ' || true)"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RUN_PID" "$CHILD_COUNT" "$CPU_SUM" "$RSS_SUM" "$MEM_KB" "$TAIL" >> "$RESOURCE_LOG"
  sleep 15
done

wait "$RUN_PID"
RC=$?
set -e
printf 'R2_EXIT=%s\nRUN_ID=%s\nOUT=%s\n' "$RC" "$RUN_ID" "$OUT"
```

Do not launch a second R2 run in this session.

## 10. Mandatory post-run inspection

Inspect without changing evidence:

```bash
test -f "$OUT/RETURN_REPORT.json" && jq . "$OUT/RETURN_REPORT.json"
test -f "$OUT/PARTIAL_TASK_SUMMARY.json" && jq . "$OUT/PARTIAL_TASK_SUMMARY.json"
test -f "$OUT/HOST_RESOURCE_RECEIPT.json" && jq . "$OUT/HOST_RESOURCE_RECEIPT.json"
tail -n 30 "$OUT/PROGRESS.jsonl" || true
tail -n 20 "$RESOURCE_LOG" || true
```

Healthy precompute evidence should include:
- affinity_count >=64
- workers =60 while enough tasks remain
- many child processes visible during precompute
- completed/persisted counts increasing
- MemAvailable above 5-GiB floor.

Do not infer PASS if RETURN_REPORT is absent.

## 11. Preserve resume cache

If `operator_tasks/` exists, preserve it regardless of PASS/FAIL.

Create a cache archive for publication/backup:

```bash
if test -d "$OUT/operator_tasks"; then
  CACHE_ZIP="$RECEIPT_DIR/OPERATOR_TASK_CACHE_${RUN_ID}.zip"
  "$PY" - <<PY
from pathlib import Path
import zipfile
out=Path(r'''$OUT''')
dest=Path(r'''$CACHE_ZIP''')
with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in ('TASK_CONTEXT.json','PARTIAL_TASK_SUMMARY.json','RETURN_REPORT.json'):
        p=out/name
        if p.is_file(): z.write(p,name)
    for p in sorted((out/'operator_tasks').glob('*')):
        if p.is_file(): z.write(p,'operator_tasks/'+p.name)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
PY
  sha256sum "$CACHE_ZIP" > "$CACHE_ZIP.sha256"
fi
```

Do not delete the uncompressed run directory.

## 12. Publish PASS or FAIL evidence

Use a fresh evidence worktree based on the latest remote R2 control branch after the run.
Do not commit from the frozen scientific worktree.

Destination:
`research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1_R2/<RUN_ID>/`

Publish when present:
- RETURN_REPORT.json
- PARTIAL_TASK_SUMMARY.json
- HOST_RESOURCE_RECEIPT.json
- ENVIRONMENT_RECEIPT.json
- ENGINE_BUILD.json
- ENGINE_IDENTITY.json
- ENGINE_ADMISSION.json
- REPRESENTATIVE_PARITY.json
- METRIC_CONNECTION_PARITY.json
- PROGRESS.jsonl
- FOCUSED_TESTS.log
- sanitized R2_RUN.log
- RESOURCE_SAMPLES.tsv
- OPERATOR_TASK_CACHE_<RUN_ID>.zip and .sha256 if present
- EVIDENCE_MANIFEST.json
- SANITIZATION.json.

Secret/network-ID sanitization follows the existing NCP evidence publication policy.
Never publish credentials or the raw authorization file; record only its SHA and approved bounds.

Commit:
`data(ncloud): publish F1-R2 parallel admission evidence <RUN_ID>`

Push non-force to:
`research/fnd-ncloud-f1-r2-parallel-admission-20260928`.

Verify remote ref/tree and evidence-only diff.

## 13. Stop boundary

After evidence publication stop.
No automatic retry, even if timed out.
No automatic `--resume-from` in this session.
No F2/F3.
No threshold, query-set, ladder or worker-count change.

Final output:

```text
F1_R2_NCP_RUN_PUBLISHED
branch = ...
head = ...
tree = ...
implementation_commit = f1d69165c6d1e799d9474db23166cb665880576f
implementation_tree = 5842046d6bf9d4865566dad28a3fec5b22235f41
run_id = ...
exit_code = ...
scientific_status = ...
wall_seconds = ...
authorization_wall_seconds = 3600
authorization_spending_limit_krw = 4000
affinity_count = ...
workers = ...
planned_tasks = ...
restored_tasks = ...
persisted_tasks = ...
min_mem_available_bytes = ...
resource_samples = ...
operator_cache_archive_sha256 = ...
return_report_sha256 = ...
evidence_manifest_sha256 = ...
remote_ref_verified = true
remote_tree_verified = true
```