# PHYS02D actual-return review

Decision: **HOLD**. The launcher exited 1 after the fullBED constructor returned and before pulse propagation. The guard at `ncp/launch_pulse.py:74` raised `STORED_SOURCE_GRID_FIELDS_MISMATCH`. There is one build reservation and no pulse reservation; legacy never started. Reservations are not completed-call counters. No usable physical pulse result is available.

The independent reviewer reproduced the grid expression by evaluating only the AST-isolated `energy_grid` function under the pinned NumPy environment. Both NPZ files pass the other compound-guard conditions. Each has 340 of 9,600 energy nodes differing from reconstruction, by at most one ULP (1.1368683772161603e-13 eV). The saved and rebuilt byte hashes match GRID_DIAGNOSTIC.json. This proves a strict-grid reproducibility failure; it does not identify SIMD/libm provenance as the cause or establish operator equivalence.

The scientific contract and four amendments retain the exact saved-grid requirement. Earlier independent PASS was preparation-only. All 11 direct input hashes and 74 prepared-review file bindings were independently verified. The first auto-collected ZIP has 369 manifest payload files and exactly 370 ZIP entries, with all bytes and hashes verified. Wrapper exit 0 reflects failure collection; the actual launcher exit remains 1.

A future bounded amendment must either introduce a reviewed saved-grid constructor path that supplies the pinned E before all grid-dependent calculations, or establish a runtime grid path that reproduces the saved nodes exactly. It must preflight the grid before spending another physical build, retain array_equal and every scientific tolerance, preserve source/ledger/atomic definitions, and receive targeted no-G verification plus independent review. Patching E after G construction or changing array_equal to allclose is unacceptable. This proposal authorizes no implementation change or additional physical call.

All seven inherited gates remain unchanged: PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO; all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING; CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED.

The reviewer used a fresh independent context and made no G build, pulse call, prior-suite rerun or frozen-study edit. Astra was requested; the underlying model backend was not independently verified. Exact source identities, evidence hashes, call accounting and proposed amendment scope are recorded in INDEPENDENT_ACTUAL_RETURN_DECISION.json.
