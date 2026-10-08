# BASS foundation rebuild: implementation and test-only return

This sidecar contains the CP3 CPU foundations and a new bounded R2 two-center operator implementation. It does not alter `cr_repro`, the original Coulomb model, or historical run evidence. Production HOLD, all-bound OPEN, b-grid NO_GO.

## Local Codex: execute, do not redesign

Read `LOCAL_CODEX_HANDOFF_KO.md`. From the repository root, using the published commit SHA:

```sh
python3 research/foundation_rebuild/run_validation.py --profile local --expected-commit EXACT_PUBLISHED_SHA
```

The runner checks source identity, records environment, runs the new tests and fixed operator cases, then runs the original repository tests in a separate subprocess. It emits durable step receipts, JUnit counts with explicit skips, matrix NPZ files, a return report, a manifest and a ZIP. It does not install packages, start a local model, change thresholds, rerun failed stages, or launch a full collision. `EXACT_PUBLISHED_SHA` must be replaced by the SHA in the delivery prompt, not by a guessed current branch head.

`--profile package` tests only this sidecar. This was the environment available during integration: the container could not resolve github.com for a direct clone. GitHub connector writes preserve the complete base tree, but package test counts do not establish the legacy full suite. The pull-request workflow also runs the local profile in a fresh public-repo checkout when GitHub Actions is available.

Dependencies: NumPy, SciPy (with `sph_harm_y`), mpmath, pytest. `requirements-validation.txt` pins the environment used for the workflow, including threadpoolctl required by legacy tests. No CuPy dependency is added to this CPU sidecar. A CPU workflow can explicitly skip legacy GPU tests; it does not validate a GPU backend.

## New implemented interfaces

- `radial_basis.py`: analytic hydrogen references; finite-domain radial FEM eigenstates; declared negative and positive pseudostates, with no silent omission.
- `two_center.py`: complex solid harmonics through l=3 with all m; both centers with electron translation factors; all-space prolate quadrature; direct ket time derivative; weak kinetic and point Coulomb S/H/D; Gram selected-span population.
- `validation_cases.py`: fixed analytic overlap/Hamiltonian checks, a quadrature ladder, and an l=0..3 radial spectrum/pseudostate bank.
- `run_validation.py`: test-only orchestration with timeout/interruption handling and preserved first failures.

The implementation is bounded. General FEM cross-center convergence, continuum completeness, asymptotic extraction, and the original 3% capture discrepancy remain open. This release does not implement an admitted capture cross section or deploy a huge Fourier embedding on a GPU. The next common-capture pilot remains a separate, non-automatic research run.

`REPORT_KO.md` and `docs/*FOUNDATIONS*`/`*ARCHITECTURE*` preserve the prior research text. See `docs/R2_IMPLEMENTATION_KO.md` for what this integration newly implements. Imported files and archive identities are in `provenance/CP3_IMPORT.json`; executable/test identities are in `SOURCE_MANIFEST.json`.
