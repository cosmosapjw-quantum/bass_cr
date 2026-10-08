# Local test-operation contract

For a validation handoff, execute run_validation.py and return its evidence. Do not implement more physics, rewrite source/tests, relax tolerances, start new collision jobs, or make a local model a dependency. Preserve the first failure, source identity, and explicit skipped-test counts. Do not turn a passing static/operator test into production admission.

New development requires a new explicit development request. This rule does not forbid development that the owner explicitly requests; it prevents a test-only session from silently becoming another research/implementation loop.
