# Validation matrix

| Check | Status | Evidence / ceiling |
|---|---|---|
| R3M11 package manifest | PASS | 90/90; receipts/package_verify.log |
| Input archive identity and manifest | PASS | source-owned SHA 5af567f4...; receipts/input_archive_manifest.log |
| Addition-only source import | PASS | 10 added paths, patch commit 0b0090bc... |
| Supplied targeted tests | PASS | 35/35; receipts/GIT_PATCH_PUBLICATION_tests.txt |
| Original TDL CPU/GPU parity | PASS | 1 test; receipts/gpu_parity.log |
| Controlled TDL CPU/GPU parity | PASS | controlled_parity/RECEIPT.json; max state difference 3.1646e-16 |
| Saved-state Gram source authority | PASS | postprocess/*_gram.json external SHA checks |
| Finite-span gap / monotonicity / probability | PASS | receipts/RESULT_VALIDATION.json; finite-grid only |
| New TDL completed checkpoint seals | PASS | 6 runs; receipts/RESULT_VALIDATION.json |
| Single-variable configuration differences | PASS | receipts/RESULT_VALIDATION.json |
| Fixed-CAP dt pair | PASS_PAIR_ONLY | 0.407404%; no order/asymptotic claim |
| Imaginary-time step/duration pairs on dx=.4 | PASS_PAIR_ONLY | 0.013703%, 0.007307%; stationary residual is not continuum error |
| Refined-preparation spatial pairs | FAIL_SCREEN | 10.411148%, 2.289941%; 1% unchanged |
| Host source review | COMPLETED | HOST_DIFF_REVIEW.md; not independent |
| Independent review | NOT_RUN | CLIENT_WORKTREE_MISMATCH before child start |
| Full suite | NOT_RUN | no substitution of targeted tests for full suite |
| b-grid / full support / tail | NO_GO / NOT_EVALUATED | never launched |
| Scientific admission / physical rate | NOT_ADMITTED / NOT_EVALUATED | no promotion |
| AOCC dt pair | PASS_PAIR_ONLY | 0.010804%; production basis fixed |
| AOCC radial / exponent pairs | FAIL_SCREEN | 4.732602% / 14.508513%; 1% unchanged |
