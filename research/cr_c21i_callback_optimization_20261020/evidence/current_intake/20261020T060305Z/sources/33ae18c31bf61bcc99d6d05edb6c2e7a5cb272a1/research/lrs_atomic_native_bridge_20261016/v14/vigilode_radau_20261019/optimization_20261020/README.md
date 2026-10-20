# Bounded native evaluation optimization

This research adapter adds opt-in `--native-eval cell-cache` and optional `--profile` to the existing case executable. The default is `legacy`. The solver, tolerance, quadrature, node summation order, physical inputs, GL2 births and ledger calculations are preserved.

Prepare normally with the adjacent `prepare_and_run.py --offline --prepare-only`, then build with the pinned/offline Cargo setup. The complete portable workflow accepts `prepare_and_run.py --all --native-eval cell-cache --output-root FRESH_OUTPUT` together with the same immutable input/cache/toolchain arguments as before; it restores source, builds, executes the focused tests and forwards cache selection to all nineteen histories. Optional `--profile` is forwarded as well. The preparation script copies the complete `src/` tree, including `src/bin/lrs_batch.rs`, and the additive native module/hook.

```
cargo build --offline --locked --release --manifest-path PREPARED/adapter/Cargo.toml
PREPARED/adapter/target/release/rei-vigilode-radau-research result.json fixed radau 16 --native-eval cell-cache
PREPARED/adapter/target/release/rei-vigilode-radau-research profile.json fixed radau 16 --native-eval cell-cache --profile
```

The cache lasts one finite-difference Jacobian. It reconstructs all base cells once; gas perturbations reuse them all; photon perturbations reconstruct only their own cell. It replays nodes in original order into unchanged native rate arithmetic. It rejects stale other-cell state/support. No global cache or rate approximation is used. Profile-off code does not execute fine-grained timer calls.

## Independent-history batch

`lrs_batch CASE_BINARY FRESH_OUTPUT WORKERS CPU_LIST` reuses the pinned VigilODE `ParallelExecution::rayon` / `map_ordered` pool. Workers must be 1–4 and CPUs distinct. It runs fixed/birth/disabled Radau N16, one transport thread per child, cell-cache mode, with taskset affinity and timeout 30s (2s kill grace). Wrap the complete batch in a 90s timeout. Children report their actual exit/IO failure; raw output paths are distinct. `/usr/bin/time` peak RSS is optional and becomes null if unavailable. Three jobs can occupy at most three workers, including when width=4.

## Evidence runners

`experiment.py`, `batch_experiment.py` and `memory_probe.py` preserve commands, raw JSON, stdout/stderr, exit and observed timing. They do not issue scientific admission. Set `LRS_OPT_WORKSPACE` to a workspace with the documented task layout (`baseline/adapter`, `rust_prefix`, `cargo_home`, shared `target_baseline`, `immutable_baseline`), and `LRS_REFERENCE_RECEIPTS` to the immutable original matrix receipt directory. Optional `LRS_OPT_EVIDENCE` selects a fresh output directory. The memory probe compiles the included small C helper with cc; that helper performs fork/exec/wait4 without inheriting a large Python parent's pre-exec RSS. It has no third-party dependency. Earlier Python-fork memory measurements are not admitted because parent RSS can contaminate ru_maxrss. Warm-up, profile attribution, correctness matrix, measured pairs and memory observations have separate names. Existing successful outputs are reused; retain failed outputs when choosing a new attempt name.

The finite-aware recursive comparator checks every original field except `wall_s`; new `native_evaluation` metadata is compared separately through work counts. Any scientific mismatch stops execution. It never widens a tolerance. Matrix fixed Radau N4 uses its actual historical receipt name `final_source_n4`.

The 2026-10-20 observations are finite same-setting equivalence and cost evidence. They do not extend the completed history count or earlier held scientific claims. Root/Astra owns admission.
