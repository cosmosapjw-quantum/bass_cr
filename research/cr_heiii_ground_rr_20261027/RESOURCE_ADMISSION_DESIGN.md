# C4 launch admission

The actual read-only probe is `intake/ENVIRONMENT.json`. Affinity/cpuset0–8 and cpu.max800000/100000 admit distinct coordinator8, worker0, reviewer2 roles. Only one scientific worker is launched at a time. These are allowed masks, not exclusive host reservations. No NCP/MPI/scaling result follows.

The observed8GiB cgroup included substantial clean file cache. Raw headroom alone was426.20MiB, which cannot support the512MiB worker allowance plus1GiB reserve. Each actual dispatch therefore rereads current values and uses the inherited conservative estimator, rather than reusing that static probe as an admission.

Let M=memory.max, C=memory.current, I=inactive_file, A=active_file, and X=file_dirty+file_writeback+shmem+unevictable. The implementation computes CI=max(0,I−X), CA=max(0,A−max(0,X−I)), then

`available = max(0,M−C) + CI + floor(CA/2) − 1GiB`.

Excluded pages are charged to the higher-credit inactive pool first. Full clean inactive and half clean active credit is an estimate of reclaimability, not current free RAM or a dedicated reservation. A single new worker is admitted only if available≥512MiB. Current C already contains the running coordinator and other live processes; the1GiB reserve remains for growth and shared-host variation. Coordinator RSS/virtual size and the sequential-worker rule are recorded with launch metadata. No unrelated process is terminated to make the inequality hold.

The child receives RLIMIT_AS512MiB, an integer CPU hard limit no larger than its remaining fixed subcap, wall60s, distinct affinity and native libraries1thread before scientific import. The C6 runtime control reads the effective worker affinity/AS/native threadpool values. OMP dynamic/nesting is disabled. AS is virtual address space, not a claim that actual RSS reaches512MiB.

One create-only task lease and unique run directory identify each attempt. Previous worker and coordinator costs, including failures, are summed with preparation cost. Missing/boolean/negative/nonfinite cost or missing receipt is UNKNOWN_PRIOR_ATTEMPT_BUDGET and blocks a launch. New reservations remain controls5, primary8, review10, plot5, misc2 with aggregate30CPU-s. Historical H1/HeI/C23E/REC allowances remain distinct. The dispatcher only terminates its owned child group on a concrete wall/CPU failure and preserves completed output and terminal receipt.

C4 adopts this guarded local path conditionally. It does not label an unstarted worker PASS. Fresh launch receipts, actual peak RSS, exit and measured CPU in C6–C9 decide runtime acceptance.
