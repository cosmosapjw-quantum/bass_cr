# F1-R2 bounded first parallel execution plan

Status: **READY_FOR_OWNER_AUTHORIZATION, NOT AUTHORIZED**

Frozen implementation:

```text
commit = f1d69165c6d1e799d9474db23166cb665880576f
tree   = 5842046d6bf9d4865566dad28a3fec5b22235f41
```

## Why this run is different

The prior F1 run used one expensive Python process and timed out at 7200 s.
R2 precomputes exact operator tasks with up to 60 spawned processes, persists every completed task,
then feeds a cache-only evaluator into the unchanged F1 scientific reducer.

The first real R2 run serves two purposes simultaneously:

1. scientific F1 admission;
2. confirmation that the 64-vCPU NCP host actually sustains the designed 60-process execution.

## Recommended first-run bound

```text
max_wall_seconds = 3600
spending_limit_krw = 4000
```

Rationale:
- previous 7200-s serial run is no longer a useful runtime baseline after changing orchestration;
- R2 can keep up to 60 independent native tasks in flight;
- completed tasks are durable and exact-context resumable, so a bounded timeout no longer destroys the whole investment;
- 3600 s is deliberately conservative enough to reveal process/NUMA/memory behavior while capping another runaway serial-style run.

This is a recommendation, not an active authorization.

## Healthy-run expectations

During `precompute_started/precompute_progress`:

- `HOST_RESOURCE_RECEIPT.workers == 60`;
- affinity_count >=64;
- MemTotal >=120,000,000,000;
- htop should show many active worker processes/vCPUs, typically dozens rather than one;
- PROGRESS should advance every 10 completed tasks;
- persisted count should rise throughout the run;
- MemAvailable should stay above the fail-closed 5-GiB floor.

If htop again shows one active CPU while `running` is large, classify as orchestration/runtime regression.
Do not wait an hour hoping it fixes itself.

## Early-stop conditions

Stop/fail closed without changing the contract if:

- workers !=60 on the approved 64-affinity host;
- affinity <64;
- MemTotal below gate;
- MemAvailable trends toward 5 GiB floor;
- worker startup repeatedly fails;
- task-store identity/tamper error;
- source/environment/authorization identity drift;
- scientific parity or policy selection failure.

No automatic threshold relaxation or worker-count reinterpretation.

## Resume policy

If timeout/interrupt occurs after valid task persistence:

- preserve the run directory;
- publish evidence;
- inspect PARTIAL_TASK_SUMMARY;
- a later separately authorized run may use `--resume-from` into a fresh output directory;
- only exact-context hash-valid tasks may be imported.

Do not rerun from zero unless evidence shows the stored cache is invalid.

## After run

PASS or FAIL:
- publish execution evidence to the F1-R2 evidence branch/path;
- report actual workers, task counts, persisted/restored, wall, MemAvailable, scientific status;
- stop before F2/F3.

Claim ceiling remains unchanged.
