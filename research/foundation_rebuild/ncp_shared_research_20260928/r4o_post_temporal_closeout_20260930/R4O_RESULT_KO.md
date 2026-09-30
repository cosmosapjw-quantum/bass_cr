# R4O — N1536 temporal closeout and next-error-budget decision

상태:
`R4O_TEMPORAL_DISCRETIZATION_CLOSED__FINITE_SPAN_SELECTED_OBSERVABLE_TEMPORALLY_ADMITTED__ASYMPTOTIC_AND_BASIS_GATES_OPEN`

## A3 authority

- execution commit: `b310a5f782f2739deb886218ef354281ed614611`
- tree: `ae02da10ac9a6145f0ddddb98c63257bd64f6338`
- return ZIP SHA256: `7ee0f704ac76d25bab9b83e094cef357cfb3c98594b9ab59df8b51bc8d242b79`
- status: `N1536_TEMPORAL_GATE_CLOSED`
- d_ref(1536): `1.6465482261011564e-7`
- d(768,1536): `4.939684855805989e-7`
- coverage: 1538/1538
- union: 3583
- lifetime raw: 5046/16896
- cache-only replay native calls: 0

## Temporal convergence

Wolfram cross-check:
- p_ref(768->1536) = `2.000008800631878`
- p_self = `2.0000464576878373`

The current frozen temporal gate is closed. No N3072 is required for this gate.

## Finite-span selected projectile observable

Using the exact final metric and the R4A-pinned projectile negative-energy selector
`[9,10,12,13,14]` with the Gram projector:

- P_sel(reference) = `0.00965343237616185`
- P_sel(N768) = `0.009653417329471998`
- P_sel(N1536) = `0.009653428615023815`
- abs N1536-reference difference = `3.7611380347e-9`
- relative difference = `3.8961665531e-7`
- observable order = `2.0002049811596685`

Projector checks remain at ~1e-16 and the metric is well conditioned.

This quantity is temporally admitted **only for the current finite basis and finite
window**. It is not all-bound capture and not an asymptotic production probability.

## Next dominant error axes

At the current terminal z=12 a0, b=2 a0, the final qualified operator has:

- ||S_TP||_2 = `0.00493086088605`
- ||H_TP||_2 = `0.00797960265766`
- ||D_TP||_2 = `0.00620259250946`
- ||[S^-1(H-iD)]_TP||_2 = `0.00755719628920`
- cross/full generator ratio = `0.0129770`

These are diagnostics, not tail bounds, but they show the current endpoint is not
numerically decoupled at the already tiny temporal-error scale.

Next DAG:
1. R4P0 operator-only asymptotic-tail preflight at larger separations;
2. R4P1 finite-window convergence at fixed B0 basis;
3. R4Q nested basis/pseudostate convergence;
4. only then all-bound classification and b-grid.

Prepared nested channel counts:
- B0 18
- B1 46
- B2 92
- B3 124

Claim ceiling remains:
`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`.

No native work was performed in R4O.
