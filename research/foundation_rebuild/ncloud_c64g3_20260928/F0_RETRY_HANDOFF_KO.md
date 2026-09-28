# F0 retry handoff — repository-contained inputs

Role: **BASS_NCLOUD_F0_RETRY_EXECUTOR**.

The previous F0 attempt ended as `STOP_F0_BLOCKED` before science because the design ZIP,
full TP2D RETURN ZIP, and approved environment contract were not available. Preserve that blocked
run unchanged. This retry exists because all required F0 inputs are now published on the dedicated
GitHub branch.

## Frozen identities

Repository: `cosmosapjw-quantum/bass_cr`

Plan/data branch:
`research/fnd-ncloud-c64g3-codex-handoff-20260928`

Minimum commit that MUST be an ancestor of the fetched branch:
`634f6fd3a2ff9b8dec94b104f693136b84accdab`

Historical scientific source:
- commit `c954d68fdc86527453765a563b3a025351163ed9`
- tree `0e13583301e271e9a9e8aa0eae3c05eaf8580a1a`
- TP2D status `TEMPORAL_REFINEMENT_UNRESOLVED`

The operator may supply a newer exact branch HEAD. Do not require that the user's current worktree
be switched to this plan branch. Fetch the branch and use `git show` to materialize inputs.

## 0. Preserve the current checkout

Record:

```bash
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" status --short
git -C "$REPO" rev-parse HEAD
git -C "$REPO" rev-parse 'HEAD^{tree}'
git -C "$REPO" branch --show-current || true
ps -eo pid,ppid,etime,cmd | grep -E 'run_tp2|run_cached_m4|bass' | grep -v grep || true
```

Do not run `reset --hard`, `git clean`, automatic stash/rebase/merge, or delete untracked
`.codex/` files. Do not switch the user's active checkout merely to read the plan.

## 1. Fetch and verify the repository-contained F0 inputs

```bash
PLAN_BRANCH='research/fnd-ncloud-c64g3-codex-handoff-20260928'
git -C "$REPO" fetch origin "refs/heads/$PLAN_BRANCH:refs/remotes/origin/$PLAN_BRANCH"
PLAN_REF="refs/remotes/origin/$PLAN_BRANCH"

MIN_INPUT_COMMIT='634f6fd3a2ff9b8dec94b104f693136b84accdab'
git -C "$REPO" merge-base --is-ancestor "$MIN_INPUT_COMMIT" "$PLAN_REF" || {
  echo "PLAN_INPUT_COMMIT_NOT_PRESENT"
  exit 3
}

BASE='research/foundation_rebuild/ncloud_c64g3_20260928'
```

Read, in order:

```bash
git -C "$REPO" show "$PLAN_REF:AGENTS.md"
git -C "$REPO" show "$PLAN_REF:docs/READBACK_POLICY.md"
git -C "$REPO" show "$PLAN_REF:$BASE/AGENTS.md"
git -C "$REPO" show "$PLAN_REF:$BASE/ARTIFACTS.json"
git -C "$REPO" show "$PLAN_REF:$BASE/STATUS.json"
git -C "$REPO" show "$PLAN_REF:$BASE/F0_RETRY_HANDOFF_KO.md"
git -C "$REPO" show "$PLAN_REF:$BASE/RETURN_CONTRACT.json"
```

Do not search Downloads, Dropbox, or Google Drive for F0 inputs. The branch now contains them.

## 2. Select an isolated F0 workspace and materialize exact Git blobs

`/data/bass` is preferred on an already prepared NAVER Cloud host, but it is **not a scientific
prerequisite for F0**. F0 performs zero spatial operator evaluations and may run in an isolated
home-directory workspace when no approved data volume is mounted.

Workspace selection order:

1. If the operator explicitly set `BASS_F0_ROOT`, require that its parent is writable and use it.
2. Else, if `/data/bass` already exists, is writable, and `findmnt -T /data/bass` resolves it,
   use `/data/bass` with `WORKSPACE_CLASS=NAVERCLOUD_DATA_VOLUME`.
3. Else use `$HOME/.local/state/bass_f0` with `WORKSPACE_CLASS=LOCAL_HOME_FALLBACK`.

Do not format, mount, chmod/chown system paths, use sudo, or create `/data/bass` merely to satisfy
this handoff. A home fallback is expected and valid for cache-only F0. Before continuing, require
at least 1 GiB available on the selected filesystem. Record the selected path, filesystem, available
bytes and workspace class in the F0 handoff receipt.

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if test -n "${BASS_F0_ROOT:-}"; then
  ROOT="$BASS_F0_ROOT"
  WORKSPACE_CLASS="EXPLICIT_F0_ROOT"
elif test -d /data/bass && test -w /data/bass && findmnt -T /data/bass >/dev/null 2>&1; then
  ROOT=/data/bass
  WORKSPACE_CLASS="NAVERCLOUD_DATA_VOLUME"
else
  ROOT="$HOME/.local/state/bass_f0"
  WORKSPACE_CLASS="LOCAL_HOME_FALLBACK"
fi

mkdir -p "$ROOT"
test -w "$ROOT" || {
  echo "F0_WORKSPACE_NOT_WRITABLE: $ROOT"
  exit 3
}

AVAILABLE_KB="$(df -Pk "$ROOT" | awk 'NR==2 {print $4}')"
test "${AVAILABLE_KB:-0}" -ge 1048576 || {
  echo "F0_WORKSPACE_INSUFFICIENT_SPACE: $ROOT available_kb=$AVAILABLE_KB"
  exit 3
}

WORKSPACE_FS="$(findmnt -T "$ROOT" -no SOURCE,FSTYPE,TARGET 2>/dev/null || true)"
printf 'F0_ROOT=%s\nWORKSPACE_CLASS=%s\nWORKSPACE_FS=%s\nAVAILABLE_KB=%s\n' \
  "$ROOT" "$WORKSPACE_CLASS" "$WORKSPACE_FS" "$AVAILABLE_KB"

STAGE="$ROOT/inputs/f0_repo_$STAMP"
CODE="$ROOT/code/f0_repo_$STAMP"
ENV="$ROOT/env/tp2e_f0_$STAMP"
mkdir -p "$STAGE" "$CODE" "$ROOT/runs" "$ROOT/receipts"

git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip" >   "$STAGE/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip"
git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/BASS_NCLOUD_C64G3_REDESIGN_20260928.zip" >   "$STAGE/BASS_NCLOUD_C64G3_REDESIGN_20260928.zip"
git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/BASS_TP2E_RESEARCH_20260928.zip" >   "$STAGE/BASS_TP2E_RESEARCH_20260928.zip"
git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/requirements-tested.txt" >   "$STAGE/requirements-tested.txt"
git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/F0_ENVIRONMENT_CONTRACT.json" >   "$STAGE/F0_ENVIRONMENT_CONTRACT.json"
git -C "$REPO" show "$PLAN_REF:$BASE/artifacts/HISTORICAL_ANALYTIC_BUILD.json" >   "$STAGE/HISTORICAL_ANALYTIC_BUILD.json"
```

Verify exact input bytes:

```bash
cat > "$STAGE/INPUTS.sha256" <<'EOF'
630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35  tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip
2c0600f742490ab89b63ff7810f8655a7cd9f43631669db13d08abf4b2c6a1df  BASS_NCLOUD_C64G3_REDESIGN_20260928.zip
0f7af63b234b8ae527ac1c1ba42c28a9cf89b39f79da329d2b73d8aa2896c7b0  BASS_TP2E_RESEARCH_20260928.zip
555144ce0107590dfce4b77cc7d60b83d84816edcf7abd32e8b3d9cdc08e4467  requirements-tested.txt
EOF
(cd "$STAGE" && sha256sum -c INPUTS.sha256)
```

Any mismatch is `INPUT_IDENTITY_BLOCKED`; do not substitute another archive.

## 3. Create a clean F0 environment only if needed

The historical TP2D RETURN archive does not pin its Python minor. Therefore **do not block solely
because that minor is absent**. The F0 environment admission is defined by
`artifacts/F0_ENVIRONMENT_CONTRACT.json`:

- exact top-level pins from `requirements-tested.txt`;
- unchanged TP2E admission tests must pass with no failures/errors/skips;
- historical N384 replay metric-distance gate must pass (`<=1e-10`);
- no fallback/latest version substitution.

If the current isolated environment already has the exact pins, reuse it and record the interpreter
and `pip freeze`. Otherwise creation of one new isolated venv is authorized:

```bash
python3 -m venv "$ENV"
source "$ENV/bin/activate"
python -m pip install --only-binary=:all: -r "$STAGE/requirements-tested.txt"
```

If exact pins cannot be installed/imported, return `ENVIRONMENT_BLOCKED`. Do not change the
versions and do not mutate the system Python or apt packages.

Record:

```bash
python --version > "$ROOT/receipts/F0_PYTHON_$STAMP.txt"
python -m pip freeze > "$ROOT/receipts/F0_PIP_FREEZE_$STAMP.txt"
python - <<'PY' > "$ROOT/receipts/F0_NUMERIC_ENV_$STAMP.txt"
import sys, numpy, scipy, pytest, mpmath
print(sys.version)
print("numpy", numpy.__version__)
print("scipy", scipy.__version__)
print("pytest", pytest.__version__)
print("mpmath", mpmath.__version__)
try:
    numpy.show_config()
except Exception as e:
    print("numpy.show_config failed:", repr(e))
PY
```

## 4. Expand the two packages without overwriting existing code

```bash
unzip -q "$STAGE/BASS_NCLOUD_C64G3_REDESIGN_20260928.zip" -d "$CODE"
unzip -q "$STAGE/BASS_TP2E_RESEARCH_20260928.zip" -d "$CODE"

DESIGN="$CODE/BASS_NCLOUD_C64G3_REDESIGN_20260928"
PKG="$CODE/BASS_TP2E_RESEARCH_20260928"
SOURCE="$STAGE/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip"

sha256sum "$DESIGN/upstream/BASS_TP2E_RESEARCH_20260928.zip"
cmp "$DESIGN/upstream/BASS_TP2E_RESEARCH_20260928.zip"     "$STAGE/BASS_TP2E_RESEARCH_20260928.zip"
```

The two TP2E ZIP copies must be byte-identical.

## 5. Run preflight

```bash
HOSTREC="$ROOT/receipts/HOST_F0_$STAMP.json"

python "$DESIGN/cloud_preflight.py"   --tp2d-archive "$SOURCE"   --tp2e-package "$DESIGN/upstream/BASS_TP2E_RESEARCH_20260928.zip"   --out "$HOSTREC"

PRE_RC=$?
echo "PREFLIGHT_EXIT=$PRE_RC"
test "$PRE_RC" -eq 0 || exit "$PRE_RC"
```

A null `safe_worker_ceiling` caused only by unmeasured native-worker RSS does not block F0,
because F0 is worker=1 and performs zero spatial operator evaluations. It does block F1/F2/F3.

## 6. Run exactly one cache-only M4 comparison

Set the thread environment to one before the Python process. Do not run native probe or DOP853.

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_DYNAMIC=FALSE
export MKL_DYNAMIC=FALSE
export PYTHON_BIN="$(command -v python)"

OUT="$ROOT/runs/tp2e_cache_$STAMP"
echo "OUT=$OUT"

set +e
bash "$DESIGN/run_cache.sh" "$PKG" "$SOURCE" "$OUT"
RC=$?
set -e
echo "EXIT=$RC"
```

Do **not** rerun automatically for any nonzero status.

Expected factual constraints, not promised results:
- new spatial operator evaluations = 0
- reference reintegrated = false
- original TP2D status remains `TEMPORAL_REFINEMENT_UNRESOLVED`
- fresh TP2E admission tests run once in this environment
- M4 uses exact archived midpoint nodes only

## 7. Return evidence

If `RETURN_REPORT.json` exists:

```bash
jq '{
  status,
  original_tp2d_status,
  new_tests,
  source_audit,
  new_method_temporal_comparison_qualified,
  comparison:{
    selected_nstep:.comparison.selected_nstep,
    historical_replay:.comparison.historical_replay,
    candidates:.comparison.candidates,
    pairs:.comparison.pairs,
    new_operator_evaluations:.comparison.new_operator_evaluations,
    reference_reintegrated:.comparison.reference_reintegrated
  },
  capture_execution_allowed,
  production_admission,
  all_bound,
  b_grid,
  continuous_trajectory_error_bound,
  continuous_global_supremum_bound,
  first_failure,
  wall_seconds
}' "$OUT/RETURN_REPORT.json"

sha256sum "$OUT/RETURN_REPORT.json" "$OUT"_RETURN.zip "$HOSTREC"
```

Create `F0_RETURN_HANDOFF.json` following `RETURN_CONTRACT.json`. Include:
- selected `ROOT`, `WORKSPACE_CLASS`, filesystem identity and available-space check;
- actual fetched plan branch HEAD/tree and `634f6fd3a2ff9b8dec94b104f693136b84accdab` ancestry result;
- source worktree HEAD/tree without modifying that worktree;
- exact GitHub input SHA/size values;
- interpreter and numerical package versions;
- preflight exit, F0 exit, actual test count;
- actual RETURN_REPORT/RETURN ZIP SHA/size;
- completed work and first blocker;
- publication/backup receipts only if actually performed.

If F0 comparison qualifies: `STOP_F0_COMPLETE`.
If science remains unresolved: `STOP_F0_SCIENTIFIC_UNRESOLVED`.
If identity/environment/runtime blocks execution: `STOP_F0_BLOCKED`.

## 8. Stop boundary

After F0, stop. Do not:
- patch TP2E or the source repo;
- loosen thresholds or skip tests;
- run another F0 attempt automatically;
- compile/load a new native engine;
- run `probe_native.py`, CF4, DOP853, or new spatial evaluations;
- begin F1/F2/F3;
- merge to main, force push, clean/reset the worktree;
- create/delete/stop cloud resources;
- publish credentials.

F1-F3 remain separately gated by implementation review and explicit native wall/cost budget.

Claim ceiling remains:
`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`,
`original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`.
