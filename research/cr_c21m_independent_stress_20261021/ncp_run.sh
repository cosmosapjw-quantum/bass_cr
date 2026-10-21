#!/usr/bin/env bash
# Run on the observed NCP host, from a separately checked out tested content commit.
# Required binding: export C21M_CONTENT_COMMIT=<published tested content SHA>
# bash ncp_run.sh plan|run|resume REPO_ABSOLUTE GRID_ABSOLUTE OUTPUT_ABSOLUTE
set -euo pipefail

task_action="${1:?Expected plan, run, or resume}"
task_repo="${2:?Expected repository absolute path}"
task_grid="${3:?Expected explicit NEW C21M grid absolute path}"
task_output="${4:?Expected create-only run output absolute path}"
: "${C21M_CONTENT_COMMIT:?Set the published tested content commit, supplied by the closeout receipt}"
task_actual="$(git -C "$task_repo" rev-parse HEAD)"
if [[ "$task_actual" != "$C21M_CONTENT_COMMIT" ]]; then
    printf '%s\n' 'SOURCE_COMMIT_MISMATCH: use an isolated checkout of the tested content commit' >&2
    exit 2
fi
git -C "$task_repo" diff --exit-code "$C21M_CONTENT_COMMIT" -- \
    research/cr_c21m_independent_stress_20261021/builder.py \
    research/cr_c21m_independent_stress_20261021/shared_runner.py \
    research/cr_c21m_independent_stress_20261021/shared_resources.py \
    research/cr_c21l_rei_pilot_20261021/adapter.py \
    research/cr_c21l_rei_pilot_20261021/SOURCE_MANIFEST.json \
    research/cr_c21l_rei_pilot_20261021/vendor/rei
case "$task_action" in
    plan|run|resume) ;;
    *) printf '%s\n' 'Expected plan, run, or resume' >&2; exit 2 ;;
esac

task_python="${C21M_PYTHON:-python3}"
task_runner="$task_repo/research/cr_c21m_independent_stress_20261021/shared_runner.py"
task_options=(--grid "$task_grid" --output "$task_output"
              --workers "${C21M_WORKERS:-64}" --execution-site ncp
              --lease-dir "${C21M_LEASE_DIR:-/tmp/bass_cpu_leases}"
              --timeout-seconds "${C21M_TIMEOUT_SECONDS:-3600}"
              --active-grace-seconds "${C21M_ACTIVE_GRACE_SECONDS:-300}")
if [[ -n "${C21M_CPU_LIST:-}" ]]; then
    task_options+=(--cpu-list "$C21M_CPU_LIST")
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 PYTHONDONTWRITEBYTECODE=1

# Read-only source/grid/resource assessment. This does not create output/leases.
"$task_python" -B "$task_runner" "${task_options[@]}" --plan-only
if [[ "$task_action" == plan ]]; then
    exit 0
fi
if [[ "$task_action" == resume ]]; then
    task_options+=(--resume)
fi
# Existing completed cases are hash-verified and not repeated. Started but
# unfinished cases retain INTERRUPTED_NO_AUTORETRY and require a separate decision.
exec "$task_python" -B "$task_runner" "${task_options[@]}"
