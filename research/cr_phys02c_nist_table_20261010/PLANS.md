# CR-PHYS02C-NIST-TABLE01

Frozen unit: a separate, source-backed two-transition cross-section table. This
is not adoption of an atomic model in the existing causal kernel.

1. Freeze contract and preserve base c471d455 / clean tracked state. DONE.
2. Acquire exactly the hash-pinned NIST PDF; transcribe its eight entries. DONE.
3. Implement a stdlib-only scalar provider with explicit transitions, source
   energies, linear interpolation, cm2 conversion and domain errors. DONE.
4. Run one bounded syntax/focused validation campaign. PASS_SCOPED, 9 tests.
5. Preserve any first failure; allow at most one targeted repair. NOT_USED.
6. Hand off an independent review and publication to the parent. PENDING.

Alternatives: extending the old formula violates the requested source-domain
boundary; importing upstream `new` adds unpinned HDF5 inputs and a broader model.
The eight-entry sidecar is sufficient and leaves both alternatives unadopted.

Only this new directory may change. Rollback is non-adoption of this sidecar;
existing tracked providers and evidence are untouched. No solver, science
history, cloud publication or old-suite replay is part of this unit.
