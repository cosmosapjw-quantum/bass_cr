# EVIDENCE_LEDGER

| ID | Claim | Evidence status | Actual evidence | Independence and limit |
|---|---|---|---|---|
| E01 | Adopted parent is PHYS02A final58c8e1c | IDENTITY_CHECKED | inputs/PARENT_SOURCE_MANIFEST.json; source runtime hash checks | Byte identity, not physics |
| E02 | Neutral electron impact rates and sharing have explicit primary representations | LITERATURE_SUPPORTED_WITH_LIMITS | inputs/NIST_IONIZATION.json; DERIVATION §§3–4; source audits | Printed primary coefficients, NIST formulas/parameters; CGI unavailable, He hybrid not single-source calibrated |
| E03 | CCC units, selected channels and raw bytes are fixed | SOURCE_DATA_CHECKED | CCC_USED_CHANNELS.json; research/literature/CCC_*; inputs/ccc | 27 selected channels; effective energy costs, He unpublished README status |
| E04 | Source extension is valid within tested selected domain | NUMERICALLY_CHECKED | R002 SOURCE_HIGH_W_AND_COVERAGE | Direct SDCS vs coefficient path share physical parent; bound900eV and source endpoints explicit |
| E05 | Branching conserves energy and adds one electron per ionization | DERIVED_AND_NUMERICALLY_CHECKED | DERIVATION §§3,7,8; R002 generator identities and independent functionals | Independent left-functionals and exact toy; does not calibrate atomic energy costs |
| E06 | Time integration is causal and accurate for supplied generator | IMPLEMENTATION_VERIFIED | R002 exact toy, DOP853, positivity and OFF checks | Toy independently constructed; DOP853 shares generator/source and isolates time propagation |
| E07 | Low-energy limit approaches parent continuum | NUMERICALLY_CHECKED | R002 INHERITED_LOW_CONTINUUM_LIMIT | Parent independent Ei analytic function; only needed new comparison called, prior suite rerun0 |
| E08 | Adopted observable mesh tolerances are met | NUMERICALLY_CHECKED | R001 FAIL retained; R002 mesh and sharing quadrature | No tolerance change; empirical refinement, not proof of physical accuracy |
| E09 | Finite-time storage/heat differs from same-operator terminal proxy | DERIVED_AND_NUMERICALLY_CHECKED | R002 final,time_series,same_operator_terminal | Same conditional frozen operator; no FS10 or universal clock claim |
| E10 | Current quantum-log prescription variation is small at this point | NUMERICALLY_CHECKED_MODEL_SENSITIVITY | R002 coulomb_sensitivity | One preselected offset, not a physical uncertainty bound |
| E11 | Exact NIST CGI numerical reproduction | NOT_EVALUATED_EXTERNAL_FAILURE | SOURCE_COMPLETION_ADDENDUM; R002 unexecuted_external_checks | Cannot be inferred from equivalent formula integration |
| E12 | Coherent atomic calibration and full histories | UNRESOLVED | Known Q/cost discrepancies and explicit exclusions | No numerical success or manifest promotes these claims |
| E13 | Independent final admission | PROMOTE_SCOPED | review/FINAL_DECISION.json,2026-10-10T12:30:02Z | Independent reviewer; conditional research operator only, no physical/production admission |
| E14 | Explicit1thread canonical reproduction | RUNTIME_REPRODUCIBILITY_CHECKED | evidence/thread_control: actualexit0, all final observables identical; failed resource preflight retained | Original R002 threads NOT_RECORDED; one endpoint rerun, not original suite or performance claim |

Actual process receipts in each run record the tool session, final output chunk and
exit code. Execution/source manifests bind the code, inputs, tests and outputs. A
reproduction instruction is not an additional execution. Remote publication and
backup acknowledgments are operational evidence and belong in publication/, not in
the scientific validation count. UPLOAD_VERIFIED is distinct from RESTORE_VERIFIED.
