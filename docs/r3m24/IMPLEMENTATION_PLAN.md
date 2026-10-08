# R3M24 bounded corrective implementation

Goal: implement the R3M23 audit's P0/P1 repairs without changing any historical
source, contract, result, checkpoint, numerical Hamiltonian, or tolerance.
Base: cosmosapjw-quantum/bass_cr @ 381b00e800bf1e7e2a78b5c0e9a56cbed5db56a5.
No git worktree, full collision, preparation, production GPU, main merge or force push.

Selected design: an opt-in successor using the frozen numerical kernels and new
CPU-only intake/coordinator/gate modules. Do not patch the historical runner in
place or monkeypatch its global numpy/GPU functions. All mutations are new files.

1. First reproduce missing protections with tests: same-size input mutation,
   metadata/path replacement, existing output before backend construction,
   partial-window failure, identical-work refinement, and scope escalation.
2. Implement pinned same-file-descriptor input intake, all manifest members,
   before/after consumption identity checks, and durable exclusive publication.
3. Implement fresh-output coordinator and explicit sealed-window reuse. A failed
   attempt is immutable: reuse completed windows only under a new frozen contract,
   never auto-retry a failed GPU job or overwrite it.
4. Implement actual-work fingerprints, reference-for-Strang gate, stable
   observable error-budget conversion, and physical-event/B3 design-only plans.
5. Wire a real CuPy adapter to historical Strang/CF4 kernels. Repeats required by
   the gate are required in the cost bound; unchanged tightening is not rerun or
   claimed as independent evidence. Execution requires explicit contract SHA.
6. Run new CPU and integration regressions, compile all new sources, preserve RED
   and failed attempts, document GPU/full historical-suite limits, and publish
   tested file blobs as an additive commit on a dedicated repair branch.

Review focus: TOCTOU at upload; corrupt/partial output; different input reused as
same state; incomplete action trace; cost/reservation failure before CUDA; source
or module identity mismatch; local reference incorrectly promoted to production.
