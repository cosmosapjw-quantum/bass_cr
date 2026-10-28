# R9 Exact code and acceptance contract

## API and domains

The pure core accepts a finite sequence of uniquely keyed Atom records `(key, energy_eV, coefficient, partition)` and explicit nonnegative `K_eV`. Energy, coefficient, K and optional target d must be exact `int` or `fractions.Fraction`, excluding bool, float, strings, NaN and infinity. Zero weights and an empty sequence are valid. Native atoms remain a separate byte-attested source bundle with the prior support and four birth partitions. No synthetic fixture can acquire native source authority by relabeling itself.

`solve(atoms,K_eV,target_d=None)` returns an exact immutable solution containing a maximum primal witness, a feasible explicit dual, a selected-target witness, atom digest, total masses, threshold/deficit data and conditional labels. `verify(atoms,solution)` recomputes the input digest, every atom marginal, every positive event coefficient, every pair sum including loop multiplicity, selected target d and the maximum primal/dual objective equality. It never accepts a solver flag as a proof. Feasibility of the three-valued dual can be checked by the minimum energy in each value group: any group pair whose dual sum is below1 must have its minimum energy sum strictly aboveK, including a group's own minimum loop.

The constructor sorts high atoms descending and low atoms ascending, uses a linear nested-neighborhood sweep, then low diagonals and residual high singles. It keeps complete tied high levels in the deficit computation. At zero optimum it does not divide. General exact arithmetic has no floating tolerance; O(nlogn) sorting and O(n) arithmetic do not assert bounded bit complexity. Maximum witnesses have at most n_positive events, and arbitrary target witnesses at most2n_positive.

## Byte-pinned same-state consumer

Before importing the predecessor consumer, check its complete source SHA256 `6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d`. Its loader checks the retained attribution NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. Reuse the exact stored binary64 atoms by exact rational lifting, without source fitting, quadrature, projection, transport, source normalization or RR replay.

Bind a cap to source identity, attribution identity, exact atom digest, eV units, exact K and a nonempty explicit conditional assumption description. Check that binding on every native plan/consume call. The native adapter consumes all four partition claims once through the original source-bound `consume_event_union`, preserving state, proper window, nb, provenance, inventory and replay checks. Full selected support has p=0. Selected kinetic energy is pairing-independent. Apply W only in the original consumer; its species21 division uses `nb=8750/47 m^-3` once. Retained photons and saved RR remain separate once-only ports.

Native admission retains `W*(N-d)<=Hneutral`. Report the recipient interval separately and reject an empty interval; never change the inventory to make a witness pass. Actual K/kernel/C/D/outside response/donor work/EOS/T/absolute volume/full-source physical native25 stay null. C is the constructed witness's cross duplicate, not an optimized energy-support max-C.

## Predetermined executed checks

Primary: exact hand-solvable fixtures; finite zero/empty/tied/nonbinary mass cases; d=0, intermediate and optimum; independent certificates; exact cutoff caps `1/5` and `2*Fraction.from_float(.1)`; native sampled conditional K including0 and20eV; monotonic sampled envelope; all3201 original atom marginals; proper-window/nb/species/chemical/kinetic identities; sparse size.

Negative controls: malformed exact scalar, negative K/energy/mass, duplicate keys, out-of-range target, missing event, wrong pair, wrong or forged dual, changed atom digest, tampered cap/source/state/window/nb, provenance substitution, inventory violation and overlapping replay. Test rejection rather than merely documenting it.

Independent: a separately authored generic graph oracle enumerates dual values `{0,1/2,1}` on small explicit allowed-pair/loop graphs, without importing production code or its tail recurrence. A separate evaluator validates saved native atoms/events/duals through energy ordering and eligible-prefix minima. Compare every oracle fixture against the production optimum and selected targets.

Runtime: all scientific preparation/imports/tests/native evaluation/plotting execute only through the new measured40CPU-s runner. Single native thread, bounded memory and wall time; failed attempts and tails retained. No preventive aggregate hard-cap proof is claimed. Remote Wolfram one8-second constrained batch is independently reported with CPU null. Metadata/provider/publication costs remain unmeasured/null.

Plot saved exact results only; show conditional cap samples and parent envelope with explicit interpretation, plus certificate residual checks. Root must inspect the rendered image. C9 independently reviews actual executed code, tests and saved results; unresolved substantive issues block scoped acceptance.
