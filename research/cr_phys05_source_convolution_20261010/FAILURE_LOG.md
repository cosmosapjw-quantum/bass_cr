# First qualification failure

Command: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/cr_phys05_source_convolution_20261010/validate.py`.
Exit 1, 120 cohorts, wall 75.529032 s, CPU 75.443266 s.

The unsplit birth-time GL16→32 maximum observable relative difference was
0.011067010826446212 (cutoff energy), exceeding the frozen 3e-6 threshold.
Cutoff count changed by 0.009256745389852184. Source, grid, number/energy
ledger, positivity, causal age, zero and OFF checks passed. The original
`evidence/VALIDATION.json` remains immutable.

Finite-grid characteristic nodes enter the cutoff at exact ages tau(E).
Observables therefore have jumps at birth times T-tau(E). Global Gaussian
quadrature has no panel boundary at those known discontinuities. This is a
quadrature failure, not a change in the source or gas closure.

One parent-authorized repair splits only at those existing characteristic
arrival times, preserving the source, kernel, gas, orders and tolerances.
The repair contract is frozen before new results.
