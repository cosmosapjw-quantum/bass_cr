# R4Z central derivative validation

Current status: **CENTRAL_DERIVATIVE_NUMERICAL_CHECK_PASS** with independent review **PASS_LOCAL_CENTRAL_CANDIDATE_DERIVATIVE_ONLY**. `FINAL_STATE.json` is the authoritative post-run scientific state; `RUN_STATE.json` records the pre-interruption checkpoint and is retained unchanged. Git and cloud delivery identities are recorded separately in the delivery receipt.

This additive stage checks the separately identified R4X continuous radial candidate at `z=0`, `b=2 a0`, `100 keV/u`, and 18 channels. Every shifted overlap sample is spatially qualified under the original six-raw-block criterion. The derivative construction takes only S matrices and the velocity; the unchanged central raw D is used afterward for comparison.

- `TASK_CONTRACT.json`: fixed numerical conditions, thresholds, and claim ceiling.
- `DERIVATION_KO.md` / `THEORY.json`: assumptions, units, ETF derivative, exact fixed weights, and regularity limits.
- `runner.py` / `RUNNER_API.md`: original create-only bounded staged execution.
- `derivative_analyzer.py`: original hash-bound S-only analysis and unchanged raw R2 comparator.
- `test_runner.py` / `test_derivative_analyzer.py`: the 23 targeted tests passed before the runtime interruption.
- `recovery_adapter.py` / `test_recovery_adapter.py`: additive two-context collection and reporting; 8 new recovery tests passed without rerunning the original 23.
- `REPORT_KO.md`: final Korean scientific report including failed coarse R8 and unchanged raw R2 results.
- `build_database.py`: additive DBv12 builder preserving all 46 DBv11 tables and 3309 historical rows, including `sqlite_sequence`.
- `package_delivery.py`: create-only reproducibility package builder.

Original completed and interrupted evidence remains immutable. Recovery work must use a separately identified context and retain actual reservation and completion counts. A missing batch completion record cannot supply a full batch wall time. File modification timestamps from different runtime clocks are not benchmark data.

The run produced **40 completed full operator payloads from 43 reserved/started attempts**. The original 25 completed payloads were hash-validated and reused; recovery supplied 15 missing results. Three interrupted attempts remain recorded with unknown internal progress. Automatic retries and duplicate completed-task executions were zero. All 13 shifted geometries passed both spatial comparisons; the shifted C++/Python versus Fortran/Fortran raw/full arrays were bitwise equal. All six accepted R8 estimates passed, with maximum spectral/Frobenius/element residuals `1.9744554126403304e-14`, `3.103189167802793e-14`, and `8.98425127414762e-15` in atomic-time inverse units. All three coarse H=0.4 R8 windows failed the absolute threshold and remain in the result. Both original R2 ladders failed for all three rules.

For the two-context completed evidence, use `recovery_adapter.py analyze`, not the single-context analyzer CLI. Bind `runs_r4z/RECOVERY_BINDING.json` SHA256 `c06a35352afefe374eb646dd808aac662caf2a4cdcec9ba8419d7ac4cc0915d0`, recovery root `runs_r4z/central_recovery_v1`, context SHA256 `b26ff8ee6915b551aea66af0bb4e71a3c697534b6dc4cd101a9b314c140cedf3`, batch `recovery`, and manifest SHA256 `9c4ad8197a4ba815f106d009e3a444e23888a536bc6b0553c08fafe68207a982`. The output is create-only. Original absolute execution paths and provenance are preserved; moving the archive does not silently authorize remapping contexts or rebinding source digests.

DBv12 preserves all 46 historical DBv11 tables and 3309 rows and adds seven evidence rows plus one local-only G02 status overlay. Integrity and foreign-key checks passed; non-G02 effective statuses are unchanged. Next priority is one offcentral pilot at z=-32a0 with a shell-contact-aware S stencil and explicit roundoff sensitivity, before expanding to the original eight centers.

The scope is `CENTRAL_CANDIDATE_DERIVATIVE_NUMERICAL_CHECK_ONLY`. The R8 label denotes fixed polynomial moment cancellation, not a proof of C9 regularity or a certified eighth-order physical error bound. Original R2 and offcentral eight-center failures remain separately recorded. Same-center quadrature order20 is fixed and not independently refined. G02 remains `UNRESOLVED`, production `HOLD`, capture `false`, all_bound `OPEN`, b_grid `NO_GO`. No MPI execution, NCP64 scaling, full-trajectory certificate, or production basis adoption is claimed.
