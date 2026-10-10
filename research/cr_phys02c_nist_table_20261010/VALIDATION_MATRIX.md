# Validation matrix

| Check | Result | Evidence / claim boundary |
|---|---|---|
| Exact primary PDF and literal table | PASS | SOURCE_MANIFEST.json; local hashes verified |
| Syntax of three Python files | PASS | FIRST_RUN.log |
| Eight table entries, six linear midpoints | PASS | 9 focused tests; independent decimal fixtures |
| cm2 conversion and channel/energy identity | PASS | test_units_and_explicit_channel_energies |
| Inclusive endpoints, outside/nonfinite errors | PASS | tests; no clipping or extrapolation |
| Positive, convex linear interpolation | PASS | checked points and positive-endpoint convexity |
| Existing tracked providers/evidence unchanged | PASS | empty before/after git diff in receipt |
| Physical cross-section/model-error bound | HOLD | not measured; table parity is not a bound |
| Kernel/history convergence and gas feedback | NOT_EXECUTED | solver intervals 0 |
| Independent review | PENDING_PARENT | not claimed by implementation worker |
| Publication and recovery package | PENDING_PARENT | no commit/push |

The 1e-14 comparison tolerance qualifies floating arithmetic only, not physical
uncertainty, table rounding, interpolation error or a continuous atomic model.
