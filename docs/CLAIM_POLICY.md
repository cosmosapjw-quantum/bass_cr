# Claim policy

1. Never label these results "Nichols code reproduction". The current claim is "independent numerical implementation of the declared semiclassical one-electron Coulomb model". Papers support definitions and comparisons; matching private raw data or digitized curves is not a production prerequisite.
2. TDL primary capture observable is explicit bound-state projection. `P_region` is a comparator.
3. `P_bound_truncated_nmax` is not total all-bound capture unless an independently justified high-n completion is added and separately labelled.
4. AOCC W1R code is reused only for analytic Gaussian/ETF primitives. Its two-electron spin/H-minus source physics is not imported.
5. No source spread becomes a covariance. No source voting selects a production central.
6. A 100 keV/u single-b calculation cannot by itself arbitrate an integrated cross section.
7. R3M26 prospectively separates model definition, code verification, numerical solution validation, optional formal error certification, and real-world validation. A model-conditional numerical release may use preregistered, held-out-checked conservative estimates with cross-effect checks. Such estimates are not certified bounds or probabilistic confidence intervals. See `r3m26/SCIENTIFIC_CONTRACT.md` and `roadmap/ERROR_BUDGET.json`.
8. Keep the original all-bound 50/100/225 keV/u objective. A finite selected-channel release is an explicitly narrower intermediate product. CAP, finite box/start/stop, finite grid and channel truncation remain numerical approximations requiring convergence; they cannot be renamed physical assumptions to erase their errors.
9. A full AOCC trajectory is an optional independent comparison lane. Independent operator/propagator/projector evidence is required; implementing every alternative solver is not. Known physical contradictions must be investigated, and unavailable experimental validation is labelled `NOT_EVALUATED`.
10. Local-reference passes, source hashes, norm preservation and test counts do not establish global observable accuracy. Historical decisions are immutable; R3M26's user-authorized prospective policy does not retroactively pass R3M18 or R3M25.
