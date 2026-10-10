# First failure retained

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cr_phys02b_delay_20261010/validate.py`
exited 1. The unmodified original result is `evidence/VALIDATION.json`; no
repair-closeout run or extended grid sweep was performed.

Only the frozen grid acceptance failed: maximum channel differences per initial
energy were 0.02401240495356627 for 128→256 and 0.027487108516121878 for 256→512.
The contract requires the fine difference <=0.02 and decreasing.

Saved-data localization identifies the same case at both refinement pairs:
20 eV impulse, t=1e11 proper seconds, active electron kinetic energy. The values
are 3.779738079958318, 3.2994899808869924, and 2.749747810564555 eV. At the last
pair, cutoff energy changes from 6.475354768578228 to 6.847225143522853 eV.
This locates the issue in transient active/cutoff partition accuracy. It does
not yet distinguish donor-cell numerical diffusion from other discretization
effects; no causal explanation has been established by the existing evidence.

Time refinement, independent sparse/dense exponential comparison, daughter
quadrature refinement, conservation, positivity, t=0 and OFF checks passed.
The result is `GRID_CONVERGENCE_NOT_ESTABLISHED`, not an upstream physical-source
failure. Do not relax the tolerance or promote the sidecar to a provider.

Minimum follow-up: one targeted numerical-method investigation of the 20 eV
impulse crossing the 10 eV cutoff at t=1e11s, with the same physical rates and
conservative ledgers. Freeze a new bounded repair contract before changing the
scheme. No broad IGM/history integration follows from this failure.

## Characteristic repair: first targeted-test failures

The first captured repair regression run exited 1; its complete output is
`evidence/REPAIR_TESTS.log`. Seven of nine tests passed. The new tiny-time heat
slope differed from the raw drag by 1.04097e-5 because subtracting two large
cooling ages lost relative precision. The exact inert-cutoff test also failed:
the sparse exponential perturbed an unchanged state by 1.9984e-15.

The targeted corrections integrate the local flight segment directly when
inverting a characteristic, and return an exactly stationary cutoff-only input
unchanged. Neither correction changes a rate, cutoff, tolerance, acceptance
row, physical reservoir, or population clipping policy. These are implementation
debugging inside the one authorized repair; the full repair-closeout has not
yet been executed at the time of this entry. One earlier test process finished before its tool handle was
retained; its output/exit are unavailable, and it is not counted as a PASS.

The corrected focused run subsequently exited 0 (9 tests, 2.994 s wall reported
by unittest); its raw log is `evidence/REPAIR_TESTS_CORRECTED.log`. The one full
repair-closeout then exited 0 and passed every frozen acceptance row plus the
arrival oracle. Its result is `evidence/REPAIR_VALIDATION.json`; no second full
repair run or tolerance change was performed.
