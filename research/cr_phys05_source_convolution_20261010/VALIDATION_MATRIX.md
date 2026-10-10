# Validation matrix

| Gate | Status | Evidence |
| --- | --- | --- |
| Source byte identity | PASS | SOURCE_MANIFEST.json; runtime checked imports |
| Focused software tests | PASS, 8 tests | evidence/TESTS.json |
| SDCS source and source partitions | PASS | evidence/VALIDATION.json |
| Original global birth quadrature | FAIL preserved | evidence/VALIDATION.json |
| Repaired panel birth quadrature | PASS_SCOPED | evidence/REPAIR_VALIDATION.json |
| Source64/96 and grid128/256/512 | PASS_SCOPED | evidence/REPAIR_VALIDATION.json |
| Number/energy ledger, positivity, causality | PASS | evidence/REPAIR_VALIDATION.json |
| Zero time and OFF | PASS | tests and unchanged first validation rows |
| Kernel time-method accuracy | REUSED_SCOPED | P02B REPAIR_VALIDATION.json; identical kernel SHA |
| Independent review | PENDING | parent-owned next step |
| Production modification | NONE | only new sidecar directory |
| Full CR/IGM history | HOLD | domain, feedback and model uncertainty remain open |
