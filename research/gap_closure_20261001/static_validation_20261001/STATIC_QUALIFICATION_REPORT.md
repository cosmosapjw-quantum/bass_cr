# What the current static qualification establishes

**Derived and implementation-checked conclusion:** `STATIC_QUALIFICATION_VALID_FOR_INTERNAL_RESOLUTION_CONSISTENCY`, but **not a rigorous operator truncation-error bound**. The existing provider and its screens are preserved.

`ResolutionQualifiedProvider.at` walks the finite ordered11-rule ladder and chooses the higher member of the first passing adjacent pair. `_raw_difference` takes the maximum of six relative **Frobenius** cross-block differences. Both full operators must also pass S/H Hermiticity and metric ratio screens. The acceptance criteria are therefore explicit, useful and local to two numerical resolutions.

They do not demonstrate convergence to the exact integral. The reverse S/H cross blocks are formed by conjugacy, so their agreement/Hermiticity is not an independent reverse integration check. Same-center quadrature remains at order20 while the cross ladder changes; it is outside this cross-resolution comparison. The broad label `INDEPENDENT_NUMERICAL_RESOLUTION_COMPARISON` means separate resolution evaluations, not independent algorithmic/systematic errors.

## Counterexamples, now executable

1. **Correlated error:** let the true scalar operator be1 and computed levels be `5+C h²`. Every observed order can be exactly2, with small adjacent differences, while the limiting error is4. A shared bias survives a Richardson diagnostic.
2. **Plateau:** `[5,5,5]` agrees exactly with zero adjacent difference but may be a biased plateau, a roundoff floor, or the exact answer. Agreement alone cannot distinguish them.
3. **Pre-asymptotic false agreement:** `[1,1+1e-12,2]` passes a 1e-9 first-pair screen and fails the next-level consistency check.
4. **Nonmonotone convergence:** alternating errors can contract in magnitude with negative difference alignment. A scalar ratio inferred from norms alone would hide this sign/direction change.
5. **Roundoff floor:** changes of order machine epsilon cannot establish an asymptotic truncation order.

`STATIC_QUALIFICATION_RESULTS.json` stores these examples; the tests verify their different failure modes. Scalar examples embed as a diagonal block of any matrix and therefore refute the matrix implication as well.

## A cheap additional diagnostic

`three_level` reports two differences, their relative magnitudes, direction alignment and contraction ratio. It reports an order and a conditional Richardson fine-error estimate only if a genuine uniform refinement parameter is supplied. It never changes the old qualification outcome or declares a rigorous bound. The estimate `||d2|| r/(1-r)` presumes a single asymptotic error term with stable direction and contraction r; compatibility with that model is evidence, not a proof of the premise or absence of shared bias.

The project's `(q,subdivisions)` ladder mixes Gaussian order and panel subdivision. It is **not** a uniform h ladder, so one must pass `resolutions=None` for its ordinary adjacent triples. Reporting `p=log2(||d1||/||d2||)` for those mixed rules would be unjustified.

The saved A1 queries contain only q32/h1 and q40/h1. A three-level physical diagnostic is unavailable without one more saved level. A future separately admitted diagnostic can add q48/h1 at a sentinel where the first pair passes, check both successive raw-block differences and report the result as internal consistency. This costs one additional raw cross evaluation at that sentinel; it must remain inside that run's exact query/resolution budget. The current G02 plan does not silently force such extra evaluations after first-pair acceptance.

Residual/a-posteriori certification would need an enclosure for the quadrature remainder, an independent integration identity with known stability constants, or validated interval integration. No such bound is supplied by the current qualification code. A dense grid or another agreeing pair can improve empirical confidence, but cannot close continuous majorant or global operator error claims.

New native calls:0. Existing screens unchanged. Existing 8/8 A1 qualification retained with its precise internal-consistency meaning.
