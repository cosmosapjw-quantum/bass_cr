# C4 — Execution dependencies and bounded resources

The sequence is compile(C5) → independent exact small controls(C6) → native witnesses and raw-source independent check(C7) → saved-result plot/reproducibility(C8) → independent static review and admission(C9) → immutable release(C10). C5 authors all needed implementation and test/checker source; execution of each scientific verification stays at its declared later stage. Actual per-stage Git+dualR2 checkpoint is required before moving to the next stage.

Root owns worker/native orchestration, budget runner and final acceptance. cross_flow_code owns joint_region.py, cpp_backend.py and integer_flow.cpp. source_handoff will author an independent exact basic-solution oracle and raw-source checker in reference/, without importing the constructor into the oracle/checker. The R6 mathematical reviewer is reserved for C9 review. Agents do not launch science independently; root freezes source snapshots and runs each job serially.

The installed CPU environment has9 available affinity CPUs and an8GiB cgroup memory ceiling, but this unit binds each worker to one CPU and caps per-process address space at512MiB. It also samples descendant RSS and cumulative process-tree CPU. The wall limit is50s per job. Compiler and its waited descendants are charged through the same worker process. The runner accounts interpreter/preparation CPU and adds0.10 CPU-s per attempt for the final ledger/termination tail. It preserves every failed attempt and its stdout/stderr. Polling is not an atomic preventive aggregate hard-cap proof; that field remains false.

The new ledger cap is40 local CPU-s, with no predecessor transfer. Initial reservations are compile4, controls7, native18, independent6 and plot3 CPU-s, leaving2 CPU-s unreserved for measured adjustments. A reservation is a ceiling for starting the named job, not prepaid consumption. Later reservations may be changed within the actual remaining unit budget when evidence justifies it; source changes and failures must be recorded. No source run occurs in C4. The separate R7 remote CAS CPU remains unknown and is not included as zero in a total-CPU proof.

Each attempt gets a unique runs/<run_id>, exact source snapshot/hash, input manifest, actual argv, limits, output, final source hashes and resource receipt. The native worker checkpoints each completed cap so that a failure can be diagnosed and only unmet work resumed. Code/source changes during execution fail the attempt. No nested parallel scientific jobs or toolchain installation is allowed.

Expected commands after their source is authored are:

    python implementation/run_bounded.py compile --run-id build_v1 --reservation 4
    python implementation/run_bounded.py controls --run-id controls_v1 --reservation 7
    python implementation/run_bounded.py native --run-id native_v1 --reservation 18
    python implementation/run_bounded.py independent --run-id independent_v1 --reservation 6
    python implementation/run_bounded.py plot --run-id plot_v1 --reservation 3

Runtime metadata is C04_RUNTIME_METADATA.json. The unchanged source consumer, saved proofs and two old PR115 failures are provenance, not new charges. Actual compiler/backend success and numeric/runtime observations remain pending C5+ execution.
