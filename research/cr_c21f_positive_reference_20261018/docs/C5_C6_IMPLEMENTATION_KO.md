# C21F C5-C6 implementation

24/24 Python tests PASS (6.24s), shell syntax PASS. Original sibling C21E source/native bridge was not changed.

Actual behavioral RED/GREEN records: physical-opacity number-Radau negative photon failure -> positive optical-depth coordinate; absent-helium numerical Jacobian probing -> structurally remove absent variables; identical native point re-evaluation -> one-entry exact-input-byte memo; a rejected comparator aborting peers -> per-case failure and result persistence. No physical tolerances were weakened or invalid gas state clipped.

The reference still reuses the exact same opacity, clock, source impulses, gas EOS and microphysics provider. Arbitrary gas positivity/stiff nonlinear convergence is not asserted. The end-of-reference ledger validation is separate from the IVP solver's own success code. Gas/ledger atol=2e-13 retained; tau atol=1e-12 explicitly dimensionless.

Native compilation/actual PreparedAbsorption and original CI/RR/DR/thermal history NOT_RUN here (no rustc/cargo). The new run_ncp.sh calls the already authored immutable native build, while campaign.py substitutes only the optical-depth reference and preserves independent failed/completed lanes. The adapter's microphysics dependency is a pure point evaluator; reuse requires exact binary input identity.
