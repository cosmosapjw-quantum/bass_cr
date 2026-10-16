# C21C C8: independent original-Verner three-energy source-age conditional refinement

## Inputs and method

Original Verner fitting shapes, MD14 emission rate time dependence, H/He gas+photon coupling, two GL2 physical birth times, three per-birth positive manufactured energies, original FLRW background (H0, Ω matter/radiation/Λ), gas adiabatic work, and exact fit threshold-event partitions. The full 48-cell stellar source spectrum and native Rust Grackle point rates are **not** used: this is a conditional low-dimensional independent mathematical reference.

At each of six combinations Δln a∈{.0125,.025}, opacity_multiplier∈{1e-4,1e-3,3e-3}, compare inherited original C21B positive Strang exact pair at 4,8,16,32,64 substeps per birth interval against new source/threshold-aligned SciPy Radau time history. Full original C21B original source immutable git blob `88002b133c659b8a42b806627796db3f13b8b6b2`; tests use the same bytes as PR76. Numerical data are `evidence/SCOPED_MATRIX.json` and `REFERENCE_COMPARE.json`.

## Quantitative results

| Δln a | opacity scale | state ∞-error at n=64 | observed p(n32→64) |
|---:|---:|---:|---:|
| .0125 | 1e-4 | 6.7252e-9 | 1.99999 |
| .0125 | 1e-3 | 6.5593e-7 | 1.99993 |
| .0125 | 3e-3 | 3.9446e-6 | 1.99949 |
| .0250 | 1e-4 | 2.6550e-8 | 1.97545 |
| .0250 | 1e-3 | 1.9599e-6 | 1.98828 |
| .0250 | 3e-3 | 1.5002e-5 | 1.99431 |

At primary (.025,1e-3) n=2,4,8,16,32,64,128 errors `[7.95232896e-4,3.85695883e-4,1.13269443e-4,2.95129432e-5,7.77610377e-6,1.95987831e-6,4.93574094e-7]`. The adjacent observed orders are `[1.0439,1.7677,1.9403,1.9242,1.9883,1.9894]`. Non-asymptotic coarse n=2→4 is **not** second-order: the close-to-second-order statement is only at the finer tested conditional grids and does not certify a global bound.

Across six cases, observed all n=64 final state differences are positive and last 32→64 orders in `[1.975,2.000]`. The local number/energy ledgers remain small (~1e-16 photons/H, ~1e-14 eV/H respectively) but algebraic closure is **not** continuum accuracy.

## Physical/C8 boundaries

This establishes numerical agreement and asymptotic trend for a manufactured nine-packet original-Verner amplitude and timed-positive-source FLRW photo-only problem. It does not establish complete MD14/BB50K spectrum accuracy, native C21 Rust bridge parity, actual Grackle Case-A thermal chemistry, true source-age spectral convergence, signed Bianchi I, or astrophysical whole-history observables. The comparison deliberately does not equate pseudo-time pair exposure to real physical-time absorber exposure; the latter is an independent Radau output.

`C8_REAL_VERNER_CONDITIONAL_SCOPED=PASS`, `C8_FULL_NATIVE_GRACKLE_ORIGINAL=NOT_RUN`, `GLOBAL_REIONIZATION=HOLD`, `USER_NCP_CPU55_CURRENT_CAMPAIGN=UNTOUCHED`. Native subagents NOT_RUN due host capability.
