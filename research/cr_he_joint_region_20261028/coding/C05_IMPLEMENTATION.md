# C5 — Completed implementation and actual build

The joint constructor, exact C++ backend, native adapter, bounded runner, independent small oracle and independent raw-NPZ checker are implemented. cpp_backend uses the original pinned cross_flow instance and replaces only its max_flow method. Its C++ solver is iterative128-bit integer Dinic; returned flows are checked for range, every vertex balance and residual mincut before restoring the original network. joint_region implements exact domain detection, all five complete vertex measures, finite residual HL exchange and every interpolation degeneracy. worker binds the original source consumer through a single module instance and checkpoints native cases. No predecessor computational file was changed.

The independent exact_oracle builds and enumerates the full incidence polytope for n<=4. independent_native reconstructs the original binary64 NPZ directly and checks support, all atom marginals and source-return fields without importing the constructor. These checkers were authored in C5; their scientific execution belongs to C6/C7 and is not claimed yet.

## Actual failed attempt and correction

build_v1 was stopped by AGGREGATE_CPU_WATCHDOG before the compile completed. Its measured0.079626CPU-s and charged0.179626CPU-s, exit-9 and source snapshot are retained. This is a controller/environment failure, not evidence against the mathematical region or C++ algorithm.

The environment exposes a procfs mount from a different PID namespace. In the actual diagnostic, Python's PID5 had procfs PID519721; looking up numeric namespace PID6 in procfs can select an unrelated host process. The kernel also lacks task/<tid>/children. The initial metadata probe's missing-path error and successful follow-up observations are retained in C05_PID_NAMESPACE_DIAGNOSIS and C05_PROCFS_DIAGNOSIS.

The runner now locates its actual direct child via procfs parent identity and NSpid, then samples the inherited process group. It retains serial reservations, per-process CPU/address-space limits, wall/RSS checks, exact final rusage and0.10CPU-s tail. The sample is not an atomic aggregate hard-cap proof. Three short controller metadata probes receive a conservative total0.30CPU-s preparation charge; that is explicitly not an observed exact measurement.

build_v2 succeeded with exit0: measured0.956505CPU-s, charged1.056505CPU-s, peak sampled process-group RSS104624128bytes. Sampled descendant CPU0.83s is consistent with measured waited-descendant CPU0.849698s. Source, inputs and all four reused dependency hashes stayed unchanged. The actual g++ command and executable hash are in runs/build_v2/BUILD_COMMAND.json and RESULT.json. Python syntax compilation covered all six Python modules.

Current charged local budget is1.536131/40CPU-s, including the failed attempt and conservative diagnostic charge. Native implementation controls, source witnesses and plotting are still unexecuted. The separate R7 remote CAS call retains unknown CPU. The next step is C6's bounded exact implementation controls after this actual C5 checkpoint.
