# R7/C8 changed-dependency refinement: native CE knots, v3

## Observed reason, not an assumed asymptotic order

Recovery-v2 executed the complete12-case experiment with108RHS and36source rows. All matrix-local, projection/energy and R40/R80 checks passed. Eighteen chi1.5 probability grid comparisons failed the frozen0.5% criterion; observed changes1.00615–1.53976%. Mean event energy/time criteria passed. The original result remains FAILED_RETAINED; its actual raw is now backed up at Library `libfile_515e40e48564819188cabb0cd189939f` and Dropbox `id:BSpOijBcT10AAAAAAD_9TA`, R1 checkpoint, not scientific admission.

Independent exact-binary64 Decimal80 reference has maximum relative error8.644925e-14 versus target5e-10 for all finest R80 source/chi/channel probabilities. This supports finite-chain arithmetic only. The convergence failure cannot be relabeled arithmetic PASS. Apparent point-grid orders for chi1.5 are not2; chi3 differences reverse sign. No h^2 asymptotic extrapolation is admitted.

The native first positive CCC energy is Delta+0.0000385eV; the first positive chi1.5 N2048 node is Delta+0.0176815479eV, about459times farther away. q-node projection fractions also change with grid, so the threshold spacing is a diagnostic observation, not a proven sole cause. The next change resolves source knots explicitly while leaving the below-threshold grid and original active denominator untouched.

## One new numerical representation, same physics

New input `n5_ce_resolvent_native_knot_input_20261024_v3`; run `n5_ce_resolvent_native_knot_primary_20261024_v3`; grid family `GEOMETRIC_PLUS_NATIVE_CE_KNOTS_V1`.

Reuse unchanged recovery-v2 `engine.py` and all14 immutable scientific input files. Do not edit the v2 executed code, CASE, raw results, or original frozen contract. A new driver and new explicit CASE/manifest own this variant. At each chi∈{1.5,3}, N∈{1024,2048}, form the original R80 common geometric grid with exact q/10eV/Delta/40theta/80theta, then union both PHYS83 constructor energy-knot arrays strictly within[q,80theta]. Deduplicate exact equal binary64 node values with np.unique; do not merge nearby distinct source knots. R40 is the same-prefix restriction. Physical h(E), W-linear interpolation, source-native Delta and constants, bath, target, source atoms, projection and event ledger remain unchanged. No native knot outside the finite path domain or source upper limit is extrapolated.

Eight new matrices,72positive RHS,24source rows are planned. N512 is not repeated. Compare N2048 toN1024 in this new family for all six source/chi cases and all channels, and compare the two upper boundaries atN2048. Also report point-grid versus native-knot values as a representation comparison, without claiming that one difference alone is a certified physical error.

## Gates and bounded execution

All original numerical thresholds remain: probability grid0.5%, conditional energy/time1%, R40/R80 relative1e-5, componentwise residual2e-12 with exact zero-scale convention, partition2e-8, probability range±2e-10, generator conservation2e-13, projection2e-12, event energy2e-14. No clipping or gate relaxation. Small native spacings may expose binary64 conditioning; the independent exact-binary64 reference target remains relative5e-10. Independent C9 must inspect the new finest rows. A failed gate remains OPEN; no further automatic representation/refinement cycle is authorized by this file.

Before launch publish the new driver, CASE and input manifest. One new targeted control verifies native-knot inclusion, unchanged below10eV grid/source support, q/upper endpoints and unchanged v2 dependency identities; it is charged as test work and is not a physical primary. Do not rerun the unchanged11 controls. Then one create-only8-case primary is allowed within30CPU s/60wall/AS512MiB, native1, actual workerCPU0/coordinatorCPU8 after fresh resource/lease check. Independent reference including the previous0.688471CPU s stays within the original10CPU s review allocation; record actual use. No ODE, source/rate quadrature, old campaign replay or NCP.

Known bounded worker subtotal after v2 tests/primary is20.694009114s; independent reference1 adds0.688471s. Root's saved-output read diagnostic CPU0.054974463s is separate analysis cost, not silently lost or double-counted. V1 failed-run raw remains NOT_RECOVERED; observed v1 counts/cost remain charged. If this eight-case run completes, cumulative current physical work will be22Q builds,21complete cases,189RHS including v1; these are planned until observed. The final selected-family admission is independent of the earlier failed family.

EXECUTION: one evidence-motivated changed-grid comparison authorized; not yet run.

PUBLICATION: S1 recovery code/input already R1 PASS; v3 pre-execution snapshot required.

BACKUP: S0 and v2 raw R1 checkpoints ACK; final canonical R3 pending; historical Drive unknown unchanged.

DAG: finite-chain CE child in progress; full N4/N5 PARTIAL/OPEN; N6/N7 gated; global_error_bound=null and global_completion_percent=null.
