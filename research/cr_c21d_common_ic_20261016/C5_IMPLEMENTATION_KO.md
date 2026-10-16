# C21D C5: Same-IC endpoint BE vs frozen-end EXP and continuous Radau

Implemented `src/c21d_trilane.py` with exact pinned predecessor C21C original `vendor/c21c/{radau_exposure_oracle.py,exposure_contract.py}`. Previous source is reused solely as a provenance-locked continuous RHS and source provider; original user NCP Rust PR78 and REI PR150/166 are unchanged.

C21D integrates three old photon cohorts and six actual GL2 birth-time cohorts in the same mathematical FLRW interval `x0=ln(1/12), Δx=0.025`. BB50K 48-cell full source is **not** used; the source's total MD14 emissivity history is original while energy distribution is deliberately three manufactured positive cells. All lanes share `q20=a_birth E_birth`, `nHtotal(a)`, `H(a)` and Verner `sigma_j(q20/a)`; all threshold `x=ln(q20/E_fit)` cuts are explicitly split.

At each frozen positive proper-time photo slab, endpoint gas with three nonnegative event fractions is solved by bounded nonlinear least squares; computed actual photon losses own gas changes, not optimizer's intermediate state. An observed early exact-inactive HeII slab produced spurious ~7e-10/H events and false gradient convergence when inactive channel was optimized. Fixed by analytically freezing each structurally unsupported photo species before optimization. No science tolerance was widened; failure threshold preserved. Both BE rational and EXP exponential survivor expressions have exact positive competing-risk species allocation.

For photo-only H/He gas, gas binding energy and thermal per-H are updated by actual photoevents; external FLRW gas and photon work are applied once. Reject any nonlinear root that fails physical residual and positivity; no epsilon neutral fraction clipping. Finite manufacturing normalizations are documented in R5, distinct from native production.

First executed `python src/c21d_trilane.py --out evidence/TRILANE.json --n 2 4 8 16 32 64 128`, Python environment with SciPy and NumPy. Independent Radau plus native-mathematical BE/EXP error trajectories stored in `evidence/TRILANE.json`. Later coding phase owns the full unit/regression checks and C8 interpretation, not C5 alone.

At n=128, max infinity norm state error vs independent Radau: BE `2.0847467997e-4`, EXP `1.3087802812e-5` under exactly matched source and IC. Both positive and ledger conservative within double precision. These are *mathematical endpoint photon models*, not verified original native Rust or production `PreparedAbsorption`.
