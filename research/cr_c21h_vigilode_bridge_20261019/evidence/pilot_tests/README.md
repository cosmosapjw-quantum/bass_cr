# C21H pilot provenance / resource contract evidence

13 unique pilot unittest methods and 1 new optical short-cell regression passed.
The first receipt runs 10 pilot helper methods plus the optical method; the
second runs the remaining 3 pilot main methods. Both process exits were 0.
These are fresh targeted contracts. There is no all-red-first claim.

| Receipt | Actual methods | Exit | Wrapper wall time |
| --- | ---: | ---: | ---: |
| helpers_and_shortcell.json | 11 | 0 | 0.814615298 s |
| main_admission.json | 3 | 0 | 0.947904400 s |

## Scope and interpretation

No native process or ODE solver is executed. Synthetic temporary binary,
build, fixture, and receipt files test byte/identity binding and failure
propagation only. Main-level tests forbid subprocess.Popen, the Rust/ODE
entrypoint, and affinity mutation. Actual C21G/C21F inputs are read; 16 pinned
source and baseline files retain their original bytes. Tampering is performed
only on temporary copies.

The main plan test reads root's already completed evidence/wiring/plan_01,
compares its recorded inputs/source with the frozen contracts, then verifies
that trying to reuse its existing directory raises FileExistsError before any
write. It does not create another plan. Missing-bridge and native admission
tests inspect FAILED receipts and confirm nonexecution flags.

The new optical method captures the unchanged original RHS before the SciPy
integrator with a sentinel. Its manufactured dx=1e-7 first-cell interval has
width 2.113248687152236e-08; the original inset rounds to the cell endpoints.
The test verifies exact original-RHS equality at three points, zero endpoint
partial time derivatives, strictly interior time FD probes, and explicit
failure when too few represented interior nodes exist. This is callback
algebra and domain coverage, not integration/convergence evidence.

## Provenance and counting

Each run JSON preserves the command, cwd, single-thread environment, Python /
NumPy / SciPy versions, per-method wall times, full source hashes before/after,
log size/hash, and actual test/exit counts. The source bytes stayed unchanged
during each test invocation. Existing 35/56 or complete 12-method suites were
not rerun.

Only the not-yet-run main plan test was changed after the helper run, to reuse
the root plan rather than create another. The 10 helper methods were unchanged.
helpers_test_source.py reverses that exact change and was required to match
the helper receipt's recorded initial source SHA. Raw logs/receipts were not
rewritten. The final 13 pilot methods are covered across the two receipts; a
fresh all-13 run is not claimed.

A previous single mocked return-trace recheck is separately retained at
../python_tests/trace_after_transport_changes.json and is not counted in the
14 method executions summarized here. Older optical SUMMARY.json records its
historical 12-method coverage and remains unchanged.

Native execution, physical acceptance, reference convergence, and wall-time
performance are separate gates. Global error bound remains null.
