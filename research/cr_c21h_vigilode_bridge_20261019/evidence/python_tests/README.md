# Independent optical adapter callback tests

Status: PASS_SCOPED_12_UNIQUE_METHODS.

The initial run executed 12 unittest methods, with one error in a boundary subcase. Its original log/receipt are retained. The boundary (HeII, HeIII)=(0.8,0.2) passes the inherited summed-fraction domain check while left-associated 1-0.8-0.2 equals -5.551115123125783e-17; the inherited manufactured provider rejects a negative event rate. This was an incorrect expectation of success in the test fixture, not a new adapter fallback or a corrected scientific source.

The admissible-stencil test now uses the exact dyadic boundary (0.75,0.25). A separate expected-failure subcase preserves the (0.8,0.2) provider rejection. Only those two changed methods were rerun, and both passed. Ten unchanged methods reuse their successful initial evidence. Thus 12 unique methods have passing final evidence from 14 method executions. This is not a claim that one final fresh 12-method run occurred or that all tests were red-first.

The adapter remained SHA256 5a18ab7766cb0b1ecef8abe0c320ee55a1ff615267a4e44846fd05dee67ed1ed across both runs. The pinned C21G reference remains 714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0.

The actual source RHS is captured at its first solve_ivp boundary by an explicit exception before integration starts. Callback finite differences, passive columns, state reduction, time-clamp branches, scaling and private imports are checked. Conservative manufactured microphysics is explicit; a synthetic polynomial checks time derivatives. One mocked return trace checks scale/shape plumbing only. No ODE integration, Rust solver execution, native microphysics, old35 suite or old56 suite is represented by these receipts.

Exact commands, selected environment variables, source hashes, actual test counts/timing, local log hashes and numerical comparison diagnostics are in initial.json and corrected_boundary.json. initial_test_source.py was reconstructed by reversing the two known test edits and its SHA256 matches the hash recorded for the actual initial execution; the original initial log was not altered.
