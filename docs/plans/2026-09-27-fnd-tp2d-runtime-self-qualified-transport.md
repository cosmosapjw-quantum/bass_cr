# FND TP2D Runtime Self-Qualified Full-Window Transport Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a bounded `z/a0=-12..+12` transport qualifier whose every actual operator query independently passes finite analytic resolution convergence before use.

**Architecture:** Reuse TP2A analytic assembly and TP1 transport, replacing the old fixed-order operator provider with an exact-time durable self-qualifying provider. Preserve TP2C as immutable predecessor evidence and keep all capture/production claims closed.

**Tech Stack:** Python, NumPy, SciPy DOP853/expm, existing C++ analytic moment library, pytest, Git/GitHub.

## Global Constraints

No operator interpolation. No phase-budget q24 candidate semantics in runtime snapshots. No old-suite rerun. No capture observable, all-bound extraction, b-grid, GPU run, or production admission. Finite ladders and frozen screens only. Create-only outputs and exact-context query-cache resume.

---

### Task 1: Self-qualified operator provider
- [x] Add focused red tests for adjacent-resolution selection, ladder exhaustion, operator screens, exact-time cache, resume cache, audit summary, and progress callbacks.
- [x] Implement `qualified_provider.py` with durable per-query JSON/NPZ receipts and finite query budget.
- [x] Verify focused tests pass.

### Task 2: Transport and analytic policy seams
- [x] Add red tests for temporal pair qualification, direct metric derivative sentinel, and analytic adapter semantics.
- [x] Implement `transport_policy.py` and `analytic_adapter.py`.
- [x] Verify focused tests pass.

### Task 3: Runner, provenance, and claim gate
- [x] Add runner contract/predecessor/success/failure tests.
- [x] Implement TP2C byte-verifying preflight, source/dependency pins, full-window DOP853 reference, bounded candidate ladder, resume cache, create-only return package, and explicit failure classes.
- [x] Preserve `continuous_global_supremum_bound=false` and all capture/production HOLD fields.
- [x] Run complete TP2D-new test suite and syntax checks before publication.

### Task 4: Publish and local confirmatory execution
- [x] Publish exact source bytes on `research/fnd-tp2d-runtime-self-qualified-transport-20260927` and verify remote manifest/blob identity in the commit containing this plan.
- [ ] Run the heavy full-window confirmatory job on the user's local 5900X environment using the already qualified analytic build and exact TP2C return bytes.
- [ ] Classify the local return without relaxing any frozen screen or finite ladder.
