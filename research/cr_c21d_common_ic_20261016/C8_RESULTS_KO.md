# C21D C8 independent Radau comparison: three mathematical photo-only lanes

Compared source-locked 9-cohort FLRW photo-only C21C continuous SciPy Radau with mathematical *endpoint BE*, *frozen-end exponential*, and new positive self-consistent *MIDEXP* time-centered absorber exposure. All share the same source ages, photon q20, H(a) proper clock, gas total-H density, Verner 13.60/24.59/54.42 eV cutoff, distinct physical binding thresholds, three spectral energy nodes and frozen opacity scale. Crossings and GL2 impulses aligned. **No original Rust native owner was compiled/run.**

Primary `x0=ln(1/12),dx=.025,opacity_scale=.001`. Infinity state error (9 photon+5 gas+1 thermal):

| subdivisions per birth segment | BE error | End-EXP error | MIDEXP error |
|---:|---:|---:|---:|
|2|7.23988796e-3|5.11279548e-4|6.29796e-6|
|4|5.04873907e-3|3.37740533e-4|5.996037e-6|
|8|3.09935359e-3|1.93415414e-4|2.36238e-6|
|16|1.56646236e-3|9.89883640e-5|6.34612e-7|
|32|8.08236179e-4|5.12731796e-5|1.76632e-7|
|64|4.13547677e-4|2.59722417e-5|4.54570e-8|
|128|2.08474680e-4|1.30878028e-5|1.1558e-8|

Late orders n64→128 approximately BE 0.9882, end-EXP 0.9887, MIDEXP 1.9756. At n2→4 MIDEXP error decreases very little due to coarse threshold/source crossover; no global clean second-order claim on arbitrary grid. All number ledger absolute residuals across 7 cases <=2.1e-17/H and energy residuals <=1.6e-15 eV/H, while state error remains finite. Source-fraction tests and total-H gates are in code.

Five additional (dx,opacity) settings with n=16/32/64 provide last-pair orders:

| dx | opacity multiplier | BE order | end-EXP order | MIDEXP order |
|---:|---:|---:|---:|---:|
| .0125 | .0003 | .9958 | 1.0030 | 1.9999 |
| .0125 | .001 | .9989 | .9970 | 1.9998 |
| .025 | .0003 | .9655 | .9865 | 1.9923 |
| .025 | .001 | .9667 | .9812 | 1.9582 |
| .025 | .003 | .9721 | .9727 | 1.9904 |

The five matrix cases use a **manufactured** opacity multiplier and three-energy shape; the observed order is per-scoped case, NOT original PR150 source-on production accuracy. The original parameter and exact JSON arrays remain in evidence. An independent derivative calculation with Wolfram verifies local O(dt³) smooth hazard approximation; explicit HeII replenishment tests cover positivity and zero inactive support.

Actual targeted pytest after MIDEXP implementation: 42/42 PASS, exit0. First inactive HeII optimizer failure and source author IDs remain preserved. New run_scope_matrix import failure was a research CLI invocation mismatch and repaired with a relative-module fallback; the physical algorithm/source was unchanged. No acceptance criterion was relaxed.
