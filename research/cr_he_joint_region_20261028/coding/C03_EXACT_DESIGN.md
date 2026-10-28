# C3 — Exact algorithm and error model

## Domain and scalar data

Normalize core atoms through the pinned cross_flow Atom validator. Ignore zero masses only when testing the graph predicate. Within each bin find the minimum-energy positive low and positive high atom. A permitted same-bin HL pair exists exactly when both exist and their energies sum to <=K; their minima give a concrete witness. This O(n) predicate after validation is equivalent to testing all same-bin pairs, without allocating a dense graph. Boundary equality is included. Compute L and N with Fraction.

For a fresh small general case use the pinned pure energy_sum.solve to obtain D and B, and exact cross optimum/dual construction for X and G. For native cases load the hash-pinned saved values/witnesses, verify their atom/cap correspondence and compare them to each newly constructed measure. Native optimization is not replayed merely to recover known scalar bounds. M=2D-L must match the HL mass of saved B in the accepted domain.

## Cross backend

The cross-flow double cover has two copies per atom, source/sink, source and sink capacities a_i, and directed cross-allowed pair support. Its maximum flow divided by2 is the cross optimum; symmetrization returns unordered event coefficients. Reuse the exact per-bin prefix-chain network and FIFO path decomposition in cross_flow.solve. Replace only _Network.max_flow with a C++ integer-capacity solver and restore every forward/reverse residual edge in Python.

All rational capacities are first multiplied by their exact common denominator in Python. Before a C++ process runs, verify nonnegative integer capacities, source/sink/node ranges and that the flow bound and every capacity are below2^126. C++ parses decimal digits with an overflow guard and uses signed128-bit arithmetic. No float,64-bit narrowing or compiler-specific saturation is allowed. Validate returned flow count, each edge's bounds, all vertex conservation, source/sink total and the reconstructed residual minimum cut. The unchanged Python solve additionally checks prefix-flow conservation, exact pair support, marginals and its dual objective. This catches a corrupted backend output rather than trusting a process exit code.

Use g++ -std=c++17 -O2 to build a single local executable. All source/build/run work is single-threaded. There is no unconditional speed or polynomial-time claim for arbitrary rational inputs; the observed cost belongs to the actual recorded jobs. Native K6 is the only new large cross primal required by this unit. Input capacity-range failures return an explicit error rather than rounded values.

## Common optimum and complete measures

Represent an event measure as a canonical unordered key tuple mapped to a positive Fraction. O is all singles; A replaces every positive low singleton by a half-mass diagonal. B is the existing maximum-HL-plus-diagonal measure. In the declared domain it has coordinates(D,M).

Use the following exact common-optimum paths after checking their scalar hypotheses:

* X=M: B is already F. Its cross-only submeasure, completed with singles, is G. This is the intended nativeK2 reuse path.
* X=D: any verified cross optimum has d=C=D, hence is already F=G. Low-leg accounting then forces m=M. This is the intended nativeK6 path.
* M=0: a verified cross G has no positive HL edges. Fill its remaining low marginals by diagonals to obtain F. This reuses nativeK20.
* Otherwise: apply the finite rational residual-HL augmentation of THEOREM Lemma3 to a cross optimum. A source high with residual capacity and an endpoint low with unused HL capacity determine an alternating path. The endpoint single case would contradict the verified cross optimum and is an error. Remove a positive incident LL-cross coefficient, augment HL by the minimum exact residual, and return the freed other low leg to its singleton. Track C invariant and strict growth of m until m=M, then add residual low diagonals.

The generic residual method may materialize HL adjacency for small/general inputs and has no claimed native performance bound. The native named cases avoid that expensive repair through proved equality branches; they do not approximate it. Empty inputs, all-zero masses and X=0 use the all-singles/low-diagonal branch.

For target(d,C), validate the four facets exactly and use THEOREM Lemma5. Convex mixing includes all singles. Combine duplicate unordered event tuples and omit zero coefficients; assign fresh unique original-consumer event IDs only after mixing. No arbitrary event-count limit from a different solver is imposed.

## Verification independence and numerical interpretation

The full-event verifier recomputes each atom marginal, d, C and low usage directly from events. The independent small oracle constructs singleton and allowed-double incidence columns from scratch and enumerates exact feasible basic solutions of A*x=a,x>=0. Its projected convex hull is compared with the region; it does not import the proposed bounds or cross backend. This is practical for the bounded n<=4 fixture suite and is not applied to native3201atoms.

The native independent checker rereads the original NPZ with numpy, lifts stored binary64 values exactly, and checks saved event and consumer returns without importing the joint constructor. Exact arithmetic has zero algorithmic rounding error for the stored rational problem. It does not remove the physical uncertainty of the input or provide a continuum-resolution/convergence claim. Binary cutoff versus decimal0.2 remains an intentional exact boundary test.

Only plotting converts accepted fractions to float. It must read saved results, label d/N and C/N, distinguish conditional caps, and never invoke the solver. Scientific resource and reproducibility receipts are produced by the bounded runner, including failed attempts and conservative tails.
