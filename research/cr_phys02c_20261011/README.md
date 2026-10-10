# CR-PHYS02C — coherent full BED atomic consistency

This additive research unit compares a source-defined full BED ionization representation with the saved PHYS02B BEQ-total / normalized-BED-shape representation. The source, prescribed bath, parent cascade, Coulomb closure, and 27 native CCC excitation tables and effective costs remain fixed.

The actual targeted R001 execution passed 15 scoped checks on the matched 2400/4800-node grids. This numerical result does not admit production history or experimental cross-section accuracy. Scientific admission is owned by the distinct reviewer in `review/FINAL_DECISION.json`; live task admission is owned by `state/NEXT_DAG.json`.

## Read first

- `REPORT_KO.md`: results, paired model deltas, interpretation, and limits.
- `DERIVATION_KO.md`: frozen atomic equations, domain, and event conservation.
- `state/SCIENTIFIC_CONTRACT.json`: exact inputs, tolerances, grids, and limits.
- `state/CLAIM_GATE.json`, `state/EVIDENCE_LEDGER.md`, `state/NEGATIVE_RESULTS.md`: admitted scope, evidence, and remaining unknowns.
- `research/ionization_sources/`: primary-source audit, independent 50-digit source calculation, and retained first failure.
- `research/excitation_sources/`: unchanged bounded supplemental CCC source audit; target-energy identity remains unresolved.
- `evidence/runs/A001/` and `evidence/runs/R001/`: actual numerical outputs and process receipts.
- `START_NCP_CODEX_KO.md`, `ncp/README_KO.md`: prepared next bounded task and execution gates.

## Reproduce only the targeted candidate work

Run from a complete repository-layout extraction, with restored parent studies alongside this unit. The full handoff includes all required parent code, raw inputs, saved legacy comparison, and reference test code. Install `requirements.txt` in an isolated environment if necessary.

```sh
OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_MAX_ACTIVE_LEVELS=1 python tests/run_targeted.py --atomic-only --run-dir evidence/runs/A_NEW
```

The local transport CLI additionally runs exactly the two frozen grids. Preserve existing run directories; do not rerun historical parent suites. Local reruns require a newly bounded task and resource admission rather than interpreting this README as authorization for unlimited repeats.

The NCP third-grid task is prepared, not executed on NCP. It permits sequential full BED and legacy calculations at (3200,6400), two calls maximum, only after the exact frozen manifest, scientific contract, independent review, and READY DAG checks pass. No automatic global-gate promotion is authorized.

## Unchanged gates and model provenance

PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO; all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING.

The requested implementation route was gpt-6.1-sol; observed child host identity remained GPT-6 Astra Pro. `evidence/WORKER_MODEL_PROVENANCE_CLARIFICATION.json` records actual_runtime_model=UNVERIFIED_CONFLICTING_METADATA. No model-performance measurement is claimed.

Source/code and payload identities are recorded in the unit manifests. Git/backup publication receipts are written after actual completion. An upload hash establishes file identity, not scientific validity.
