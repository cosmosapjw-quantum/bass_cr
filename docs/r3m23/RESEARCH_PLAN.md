# R3M23 frozen two-window work-precision plan

Input authority: remote `cr/r3m22-inner-action-reference-20260923` exact HEAD `bd6cd9c183967e4319162c6023074162a3259d81`. Canonical node: `N1_TDL_PRODUCTION_H_B2_CLOSEST_OUTGOING_SHORT_WINDOW_WORK_PRECISION`. This is a new bounded continuation, not a second run of the R3M22 one-job contract.

The immutable R3M20 selection fixes `closest g001152` and `outgoing g002048`, each a 4-B2-dt horizon `0.04999569408955976` au from its actual checkpoint time. R3M23 `INPUT_GUARD.json` validates both generation manifests, seal/witness/receipt, source/config and state SHA before GPU. R3M22 strict 64/96-point dense-DOP853 CPU oracle 4/4 PASS and its first coarse-gate failure remain separate evidence. No other generation, full collision, preparation, finer h, representation/CAP/box/energy/b change, projection or checkpoint write is admitted.

Question: do the two remaining production-H short windows give a reproducible CF4-versus-frozen-Strang work/error comparison at each window's own Strang-error scale? This does not imply a production independent ODE oracle or a new self-scaled CF4 1% reference.

Fixed one-job sequence: allocation+three full-H matvec probe, then each selected window in closest→outgoing order. Each window uses frozen/buffer parity at one and four B2 steps, frozen Strang n4/8/16, a one-CF4-step n16 calibration at substeps 2/4 and tighter inner budget, then full-H CF4 n8/16 and n16 tightened inner budget. Optional full-window n8 substeps4 is run only when its 640-matvec worst case plus all still-required later-window work fits the frozen 4,000 cap. A missing optional repeat fails closed for the comparison gate. If the first window fails parity, calibration or comparison accuracy, stop before outgoing and record why. No automatic retry.

CF4 global exact-arithmetic inner budget is `1e−14`, tightened budget `1e−15`, max Arnoldi basis 10, same discrete H/CAP. One-step calibration must be below the pre-existing `2.103970853068276e−14` physical raw-L2 limit. For each window, the own Strang comparison scale is the minimum of raw S4/S8/S16 distances to CF4 n16. The CF4 n8→16, n16 tighter-inner and full-window n8 substep repeats must each be strictly below 1% of that scale; all endpoints finite and frozen/buffer parity PASS. This scale permits only a Strang-scale empirical comparison. The R3M22 new self-scaled CF4 1% gate remains unresolved regardless of this result.

Hard maxima: one GPU job, at most two four-dt windows, total FFT/kinetic matvecs ≤4,000 including probe and Strang, each window wall <1,800 s, total GPU job wall <7,200 s, GPU free ≥2 GiB and host available ≥8 GiB at checked stages. Required two-window worst case is 3,591 matvecs; optional repeats are dynamic and never displace required work. Forecast uses the measured R3M22 job rate and is labeled forecast, never measured R3M23 performance. Record synchronized propagation, host transfer, setup/upload, FFT counts, observed free memory separately. A full-collision speedup or equal-accuracy cross-method speedup requires a true common error target and is not inferred here.

Stop at first source/checkpoint/resource/parity/inner/NaN/budget failure; retain raw failure. Scientific `TIME_REFINEMENT_STILL_OPEN`, production `HOLD`, b-grid `NO_GO` persist. Independent review must assess numerical scope and actual budgets. Publish a dedicated branch, dual-backup only new small evidence, and return exactly one next canonical node.

Evidence log (append-only):

- E1: fetched and verified remote R3M22 `bd6cd9c…` exact HEAD; new branch created clean.
- E2: selected g001152/g002048 `validate_generation` and SHA guard PASS; no checkpoint mutation. `results/R3M23/INPUT_GUARD.json`.
- E3: new opt-in sidecar and focused tests; initial test failure was a floating literal equality in test assertion, preserved as `EXPECTED_RED.*`; corrected test PASS 3/3 in `TARGET_GREEN.*`. No numerical implementation tolerance changed.
