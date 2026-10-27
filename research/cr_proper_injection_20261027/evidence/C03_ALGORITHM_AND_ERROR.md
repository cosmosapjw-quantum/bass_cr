# C3 bounded algorithms and separated errors

## Native measure and finite history

The adapter validates exact revision/hash, state/isotope/frame/support, the stored event family and a finite declared history. It converts native elapsed-clock polynomial coefficients once with c_k * clockJacobian^(k+1) * volumeJacobian * targetFactor. Proper time endpoints already belong to the chosen clock and are not multiplied again. Reapplying normalization tokens is rejected. The bounded implementation admits fixed proper volume, constant positive Jacobians and nonnegative degree0–2 segment coefficients. More general moving cells or nonlinear coordinate changes require a new contract.

For a segment polynomial, integrate each coefficient analytically. Linear finite moments use (b-a)(b+a)/2 rather than subtracting two large squares. Zero-width windows return zero integral while a known left endpoint rate remains distinct. Missing history returns null fields; unknown gaps or extrapolation are refused. Atomic bins are already integrated measures, not differential samples. Moment-only inputs never acquire an invented spectrum.

## Actual stored source

The active energy coordinates B are converted to number through B_i/E_i using the original positive energy nodes. Preserve a single U*/T² scale for all source birth tags. Cutoff energy/count are once-only; duplicate diagnostic low_cross counters are excluded. fullBED and legacy encode one source family. Low/high native birth supports can be disjoint even when projected atoms meet at10eV; native birth/time overlap controls event ownership.

## Independent arithmetic and acceptance

Production uses binary64 inputs and math.fsum. Independent reference reopens the original pinned NPZ, uses Decimal80.from_float for exact represented inputs, independently divides energy coordinates by energy and analytically integrates the six represented windows. It does not import production modules. Compare90 fields across18rows, six original stored moments and source/tag/half-window additivity. Decimal80 is a check of implementation arithmetic, not an improvement to the original source model.

Frozen tolerances: original source moments2e-12 relative; independent fields2e-13; finite integration/additivity2e-14; energy unit/event conservation2e-14 scaled. Exact-zero quantities use exact zero checks; there is no artificial unit-scale absolute error floor. Errors are separated: source quadrature/projection physics inherited and not newly estimated; binary64 adapter error independently measured; proper-history model domain finite; actual RR/state and nb gates unresolved. Global physical error remains null.

## Minimal execution

Single bounded controls attempt, one actual source-adapter attempt, independent-reference attempt and optional saved-output plot. Unique create-only run IDs, executed code snapshots, worker/coordinator/failure costs and shared unit-budget lock. No optimizer, new quadrature, old RHS, operator solve or source-model replay. Final C9 reviews raw results and code after these new calculations, including earlier static findings and unexecuted reference correction.
