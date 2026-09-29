# R4F N768 cache preserving migration adapter

Status: implementation prepared; parent serial run remains active. This code is
not an authorization to stop it or launch native workers.

`parallel_bridge.py` plans the exact `run_candidate` time queries, validates
ordered qualified JSON/NPZ pairs, imports only complete extra parent cache, and
provides a strict cache-only reader. `worker_runtime.py` initializes one frozen
native kernel per spawned worker after checking source, library, BUILD receipt,
architecture, and four single-thread settings. `GlobalBudget` reserves each raw
attempt in one fsynced, process-shared ledger before the native evaluator call.

After a single linked migration approval, `controlled_stop.py` reidentifies the
original Python child by PID, start ticks, command, cwd, Git identity, parent
supervisor and process group. It signals only that child and writes a separate
stop/loss receipt. The original output and consumed R4C authorization stay intact.

The approved `run_r4f_science.sh` then launches `supervise.py`, which owns a
dedicated process group and applies the remaining original deadline and approved
termination grace. `run_parallel_bridge.py` validates the exact original archive
and frozen parent, performs at most two endpoint native parity queries, runs a
useful 8-query pilot, fills only missing required IDs, and replays unchanged
`run_candidate(768)` from the original initial state with zero native calls.
No N1536 path exists here.

Numerical dependencies and `PINNED_DEPENDENCIES.json` are unchanged. The
parity allowance is at most 22 raw attempts (two queries times the frozen
11-rule ladder), included in the original global 8470 cap. Parity compares
every saved operator payload and the selected adjacent resolution. Passing
synthetic tests is not native parity evidence.

The runner requires a new approval bound to the parent authorization ID,
new execution commit/tree, original archive SHA256, actual remaining deadline,
CPU list, worker/RAM caps, grace, and cost scope. It does not measure provider
billing. A failure may leave only partial task files; the supervisor packages
existing bytes and never fabricates a candidate or return report.
