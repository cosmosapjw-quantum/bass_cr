#!/usr/bin/env bash
# New explicit targets only; completed 125 targets are rejected before output.
# No package installs, old-grid generation or automatic replay is performed.
# bash ncp_run.sh plan|run|resume REPO_ABSOLUTE NEW_GRID_ABSOLUTE OUTPUT_ABSOLUTE
set -euo pipefail

task_action="${1:?Expected plan, run, or resume}"
task_repo="${2:?Expected repository absolute path}"
task_grid="${3:?Expected explicit NEW C21N grid absolute path}"
task_output="${4:?Expected create-only run output absolute path}"
: "${C21N_CONTENT_COMMIT:?Set the published tested C21N content commit from its authority receipt}"
case "$task_action" in
    plan|run|resume) ;;
    *) printf '%s\n' 'Expected plan, run, or resume' >&2; exit 2 ;;
esac
for task_path in "$task_repo" "$task_grid" "$task_output"; do
    [[ "$task_path" == /* ]] || { printf '%s\n' 'Absolute paths are required' >&2; exit 2; }
done
task_actual="$(git -C "$task_repo" rev-parse HEAD)"
if [[ "$task_actual" != "$C21N_CONTENT_COMMIT" ]]; then
    printf '%s\n' 'SOURCE_COMMIT_MISMATCH: use an isolated checkout of the tested content commit' >&2
    exit 2
fi

# Preserve both original M production dependencies and new N dependencies.
task_bound_paths=(
    research/cr_c21m_independent_stress_20261021/builder.py
    research/cr_c21m_independent_stress_20261021/shared_runner.py
    research/cr_c21m_independent_stress_20261021/shared_resources.py
    research/cr_c21m_independent_stress_20261021/requirements-science.txt
    research/cr_c21l_rei_pilot_20261021/adapter.py
    research/cr_c21l_rei_pilot_20261021/SOURCE_MANIFEST.json
    research/cr_c21l_rei_pilot_20261021/vendor/rei
    research/cr_c21n_mass_shell_cache_20261021/builder.py
    research/cr_c21n_mass_shell_cache_20261021/prepared_momentum.py
    research/cr_c21n_mass_shell_cache_20261021/shared_runner.py
    research/cr_c21n_mass_shell_cache_20261021/shared_resources.py
    research/cr_c21n_mass_shell_cache_20261021/storage_preflight.py
    research/cr_c21n_mass_shell_cache_20261021/completed_targets.json
    research/cr_c21n_mass_shell_cache_20261021/requirements-science.txt
    research/cr_c21n_mass_shell_cache_20261021/ncp_run.sh
)
git -C "$task_repo" diff --exit-code "$C21N_CONTENT_COMMIT" -- "${task_bound_paths[@]}"
if [[ -n "$(git -C "$task_repo" status --porcelain --untracked-files=all -- "${task_bound_paths[@]}")" ]]; then
    printf '%s\n' 'BOUND_SOURCE_NOT_CLEAN' >&2
    exit 2
fi

task_workers="${C21N_WORKERS:-62}"
if [[ ! "$task_workers" =~ ^[0-9]+$ ]] || (( 10#$task_workers < 1 || 10#$task_workers > 62 )); then
    printf '%s\n' 'C21N_WORKERS must be an integer in 1..62; admission further caps it' >&2
    exit 2
fi
task_python="${C21N_PYTHON:-python3}"
task_runner="$task_repo/research/cr_c21n_mass_shell_cache_20261021/shared_runner.py"
task_options=(--grid "$task_grid" --output "$task_output"
              --workers "$task_workers" --execution-site ncp
              --lease-dir "${C21N_LEASE_DIR:-/tmp/bass_cpu_leases}"
              --timeout-seconds "${C21N_TIMEOUT_SECONDS:-3600}"
              --active-grace-seconds "${C21N_ACTIVE_GRACE_SECONDS:-300}")
if [[ -n "${C21N_CPU_LIST:-}" ]]; then
    task_options+=(--cpu-list "$C21N_CPU_LIST")
fi
if [[ "$task_action" == resume ]]; then
    task_options+=(--resume)
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR="${C21N_TMPDIR:-${TMPDIR:-/tmp}}"
[[ -d "$TMPDIR" && -w "$TMPDIR" && -x "$TMPDIR" ]] || {
    printf '%s\n' 'Writable searchable C21N_TMPDIR/TMPDIR is required' >&2; exit 2;
}

# The runner creates a private temporary writable MPLCONFIGDIR and removes it.
# The plan has no persistent run metadata, output directory or CPU lease writes.
# statvfs available blocks + inodes must cover reserves, coordinator and tasks.
"$task_python" -B "$task_runner" "${task_options[@]}" --plan-only
if [[ "$task_action" == plan ]]; then
    exit 0
fi
# A second observed admission precedes output creation. Completed seals are
# verified on resume; started/failed/unsealed cases are never automatically run.
exec "$task_python" -B "$task_runner" "${task_options[@]}"
