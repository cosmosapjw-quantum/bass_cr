# BASS_CR R4Q gap closure, 2026-10-01

This dated research package reduces the 13 report gaps through proofs, saved-matrix audits, synthetic benchmarks and bounded executor implementations. `GAP_REGISTRY.json` is the current gap ledger; `CLAIM_EVIDENCE_MATRIX.json` distinguishes derivation, implementation evidence and remaining physical claims. Original literature and acquisition records remain unchanged in database v4; research updates use separate tables.

## Scope and use

The accepted B0 temporal result covers only the original 18-channel, 100 keV/u, b=2 a0, ±12 a0 problem. Its selected indices are `[9,10,12,13,14]`. The eight restored static-tail matrices provide no propagated tail states. No new physical operator evaluation or transport run was performed in this research session.

The delivered archive contains a selective, hash-verified source snapshot, not a complete Git checkout. Its `source/` and sibling `restored_static_A1/EXECUTION_PREPARATION/` directories must remain together for the saved-payload guard test. Native payloads and historical authorization records in that restored directory are evidence only. They are not permission to execute.

Run only the new non-native suites from the archive root:

```bash
python source/research/gap_closure_20261001/run_validation.py --out new_validation_output
```

The output directory must be new. The runner stops on the first failure or skipped test and records commands, logs, versions and source hashes. Validation uses Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. NumPy/SciPy match the historical native environment; its Python version was 3.13.5.

## Evidence map

| Directory | Main result |
|---|---|
| `rho_integration_theorem_20261001` | Conditional local-rate, accumulated-probability and integrable-tail theorem; projector algebra |
| `numerical_methods_20261001` | Generalized-eigenvalue conditioning and basis-covariance audits |
| `semantic_selection_20261001` | Semantic selection reproduces the B0 subspace and rejects duplicate physical identities |
| `static_validation_20261001` | Independent finite-difference design, static-qualification limits, two guarded executor families |
| `asymptotics_20261001` | Conditional multipoles, parity counterexample, frozen minimum held-out discriminator |
| `majorant_analytic_20261001` | Conditional compact-support tail, saved-radial obstruction and reference-selector repair theorem |
| `majorant_validated_20261001` | Rational finite-interval continuum certificate on synthetic inputs; physical cell enclosures still absent |
| `rank_policy_20261001` | Synthetic rank-loss policies and mandatory new-basis qualification |
| `independent_propagator_20261001` | Whitened CF4 algorithm and independent synthetic convergence benchmark |

Physical G04 remains Level 0: neither conditional analytic formulas nor the synthetic Level 2 demonstration certify actual B0 continuously. `TAIL_BOUND.json` therefore contains no issued physical infinite-tail bound. The error budget has unknown components and no certified total.

## Next bounded physical proposals

G02 needs 66 new static queries, six verified reused centers and a maximum of 726 raw attempts. G03 is a separate signed ±48 a0 proposal: two queries, maximum 22 raw attempts. Each requires a clean exact Git source pin, fresh gap-specific authorization and successful runtime/resource admission. See the executor README and immutable science/resource contracts. The proposals cannot borrow each other's scope or consume historical authorization. Neither launches automatically when tests run.

G04 additionally needs a certified interpretation of the exact isolated reference model and selector mapping, together with continuous finite-bridge operator/derivative enclosures. More point samples alone do not close that requirement. Stateful window and basis-expansion work remains downstream.

The final archive's `RESEARCH_LOOP_CLOSEOUT.json` supplies the published branch/HEAD/tree, test totals and checkpoint receipts. The separate delivery receipt binds the final ZIP hash to its dual-backup readbacks.

Claim ceilings remain `capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`, and `continuous_trajectory_error_bound=false`.
