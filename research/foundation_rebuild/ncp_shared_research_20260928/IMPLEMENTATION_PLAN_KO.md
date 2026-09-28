# R3 cache reuse and metric audit implementation plan

**Goal:** Implement the approved NEXT_CODEX_PROMPT_KO.md in this ChatGPT runtime, not delegate unfinished features to cloud Codex.
**Architecture:** Read pinned artifacts without importing F1/R2/native modules. Preserve original task receipt/payload bytes; create an additive read-only import bridge. Use triangular solves for stored-sample metric diagnostics. The historical finalized result is evidence reuse, not resuming an interrupted R2 run.
**Spec:** NEXT_CODEX_PROMPT_KO.md at 6f4be73104d791011137659fe08c71b6e354aaf3.
**Tech stack:** Python >=3.11, NumPy 2.3.5, SciPy 1.17.0, stdlib ZIP/hash/file I/O. No native BASS callback, rebuild, RPC or process pool.

## Constraints and review focus
Original code, arrays, thresholds and historical results remain immutable. Completion here is implementation-verified/cache-only, not production promotion. Cloud Codex reviews the delivered change, repairs demonstrated defects, and executes only the cache-only command; no rewrite, new physics or consumed authorization reuse.
Focus: reject malformed ZIP/JSON/NPY before allocation; bind imported context to model/basis/generator/policy; do not alias near-time tasks; verify lower/upper Cholesky direction on complex matrices; preserve failures and create-only output.

## Tasks
- [x] Reproduce output-path-dependent historical engine identity as an assertion failure with a fake compiler only.
- [x] Add integrity.py: bounded ZIP/JSON readers, exact hashes, safe create-only writes.
- [x] Add cache_bridge.py: source closure+evidence pins; original IDs and bytes preserved; strictly scoped numerical identity; exact lookup without fallback; fresh output import.
- [x] Add metric_diagnostics.py: independent FD residual, H Hermiticity, congruence whitening, inherited gate reconstruction and finite-sampling limitations.
- [x] Add run_cache_audit.py: one bounded cache-only command, receipts/partial failure preservation, no native imports or build.
- [x] Run only new focused tests and real archived-array audit; add next physics contract draft, small remote validation script, role policy, and implementation manifest.
- [ ] Publish tested bytes to a new implementation branch; verify remote ref/tree; package and back up create-only using existing targets.

## Test boundary
The old 18/32/48/30/16 suites are not rerun. New tests may read the 297-task archive, but do not run its historical scientific generator. Expected root RED is an actual numeric-identity comparison failure, not missing import/setup. Focused tamper tests exercise ZIP/context/payload/metadata and source drift separately.
