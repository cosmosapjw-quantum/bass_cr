# Independent static audit of the cross-bin energy-support formula

Reviewer: `/root/source_handoff`  
Method: independent mathematical derivation and read-only source comparison  
Scientific execution, NPZ loading, tests, numerical experiments, and owner-branch modifications: **none**

## Decision

**PASS_SCOPED_FORMULA**, under the assumptions stated below. The proposed independent-set reduction, two-threshold canonicalization, exact deficiency formula, and suffix-maximum evaluation are valid. No counterexample was found by the static derivation. The proof below establishes the mathematical optimum, not an unexecuted implementation result.

The proposed sweep supplies the optimum and an exact dual certificate. Constructing and verifying an explicit primal maximum event witness is a separate implementation obligation unless the new unit intentionally adopts a value-and-dual-only output contract. No primal witness is manufactured by the deficiency calculation alone.

This review is for a new read-only-snapshot-based unit. It does not change the state, budget, implementation, or admission of PR113 or PR114. The parent has fixed the new scope to complete cross-bin support intersected with the atomwise energy-sum cap; arbitrary bin graphs and the full joint `(d,C)` Pareto set are outside this formula.

## 1. Source comparison and retained boundaries

Read directly:

- `/tmp/bass_cr_pr113/research/cr_he_pair_support_20261028/theory/THEOREM.md`, especially Sections 1–3: finite fractional matching, symmetric bipartite double cover, exact primal/dual equality, and the explicit limitation of unconditional diagonal completion.
- `/tmp/bass_cr_pr113/research/cr_he_pair_support_20261028/CONTRACT.json`: bin graph edges permit full Cartesian rectangles; exact divisible capacities; fixed-`d` construction uses unrestricted diagonal doubles.
- `/workspace/scratch/41a5b08c0439/bass_cr/research/cr_he_energy_sum_20261028/theory/THEOREM.md`: total internal double mass `d` under `Ea+Eb<=K`, with allowed diagonal test `2Ea<=K`.
- `/workspace/scratch/41a5b08c0439/bass_cr/research/cr_he_energy_sum_20261028/theory/R03_DEFINITIONS.md` and `implementation/energy_sum.py`: existing `C` is witness-specific and explicitly not optimized; the native adapter retains source/state/window/nb/replay guards.

The PR114 checkout supplied for review is `c87c50208a7585ff1713bd54303e1a1e29c962cf`. PR113 was read from the separate temporary snapshot supplied by the parent; this review does not infer its remote-current commit or its final admission.

The new formula addresses a concrete gap between those sources: it optimizes cross-bin duplicate mass using every atom's energy, rather than replacing an allowed bin edge by its full Cartesian rectangle or optimizing total double mass only.

## 2. Exact finite problem

Let `V` be a finite atom set. Each atom has:

- a bin label `b(i)` in a finite set of `k` bins;
- finite nonnegative energy `E_i`;
- finite nonnegative divisible leg mass `w_i`.

Let `K>=0` be the declared conditional cap. The allowed simple undirected cross graph is

\[
 \mathcal E_K=\{\{i,j\}:i\ne j,\ b(i)\ne b(j),\ E_i+E_j\le K\}.
\]

There are no loops in this graph. A cross event uses one leg at each endpoint. Define

\[
 N=\sum_iw_i,\qquad
 \mathcal X_K=\{x\ge0:\sum_{j:\{i,j\}\in\mathcal E_K}x_{ij}\le w_i\},
\]

\[
 C_{\max}(K)=\max_{x\in\mathcal X_K}\sum_{\{i,j\}\in\mathcal E_K}x_{ij}.
\]

Residual legs may always be singles. Consequently the incidence inequalities are equivalent to an exact-marginal event construction with singles. Same-bin doubles, if separately permitted by the physical bookkeeping, are unnecessary to attain the cross objective and are not used to justify this formula.

The mathematical proof works with finite real nonnegative masses. An exact implementation should use rational masses and exact comparisons, as in the predecessor contracts. Integer indivisibility or event-count parity is not assumed.

## 3. General independent-set deficiency identity

For a vertex set `I`, let `N(I)` denote its open graph neighborhood. For independent `I`, the two sets are disjoint. Define

\[
 \Delta=\max\left(0,\max_{I\text{ independent}}[w(I)-w(N(I))]\right).
\]

Then

\[
 \boxed{C_{\max}=\frac{N-\Delta}{2}.}
\]

### Proof

The fractional matching dual is

\[
 \min_{y_i\ge0}\sum_iw_iy_i,
 \qquad y_i+y_j\ge1\quad(\{i,j\}\in\mathcal E_K).
\]

It has a half-integral optimum with values in `{0,1/2,1}`. A direct constructive justification is the symmetric bipartite double cover already proved in PR113: source and sink capacities are `w_i`, allowed cross arcs occur in both orientations with capacity `2N`, max-flow value is `2Cmax`, and a minimum cut yields `y_i=(a_i+b_i)/2`. For `N=0` the result is immediate. This argument applies to the finite atom graph, not just a graph on bins.

For an optimal half-integral `y`, put `I={i:y_i=0}`. It is independent. Every neighbor of `I` has label 1. Any label-1 vertex outside `N(I)` can be lowered to `1/2`: it has no label-0 neighbor, so all incident edge inequalities remain satisfied. Nonnegative weights make this modification nonincreasing in objective. Thus there is an optimal dual of canonical form

\[
 y_i=\begin{cases}
 0,&i\in I,\\
 1,&i\in N(I),\\
 1/2,&\text{otherwise}.
 \end{cases}
\]

Its objective is

\[
 w(N(I))+\frac{N-w(I)-w(N(I))}{2}
 =\frac{N-[w(I)-w(N(I))]}2.
\]

Conversely, this dual is feasible for every independent `I`: every edge touching `I` ends in `N(I)`, and every other edge has both labels at least `1/2`. The empty set supplies the all-`1/2` objective `N/2`. Minimizing the canonical dual proves the displayed identity. Compact primal feasibility and finite max-flow/min-cut give attainment; this is not merely a weak upper bound.

## 4. Two-threshold canonicalization

Take any nonempty independent set `I`. Choose an atom in `I` of globally minimum energy `e`, and let its bin be `r`. If `I` contains an atom outside `r`, let

\[
 h=\min\{E_i:i\in I,\ b(i)\ne r\}.
\]

Otherwise write `h=+infinity`. For finite `h`, necessarily

\[
 h\ge e,\qquad e+h>K.
\]

The second inequality is strict because the graph contains pairs at equality.

Define the expanded set

\[
 I^*(r,e,h)
 =\{i:b(i)=r,\ E_i\ge e\}
 \cup\{i:b(i)\ne r,\ E_i\ge h\}.
\]

The second set is empty for `h=+infinity`.

### 4.1 Independence

Vertices in the `r` tail share a bin, so no edge joins them. A pair between that tail and an outside tail has sum at least `e+h>K`. Any two outside-tail vertices in distinct bins have sum at least `2h>=e+h>K`; same-bin pairs have no graph edge anyway. Thus `I*` is independent.

### 4.2 Exact neighborhood, including all other outside bins

The atom `(r,e)` is adjacent to every outside-bin atom with energy at most `K-e`. Therefore

\[
 N(I)\cap\{b\ne r\}=\{i:b(i)\ne r,\ E_i\le K-e\}.
\]

The reverse inclusion follows because every member of `I` has energy at least `e`: no neighbor outside `r` can have energy greater than `K-e`.

For finite `h`, an outside atom at energy `h` is adjacent to every bin-`r` atom with energy at most `K-h`, and all other outside members of `I` have energy at least `h`. Hence

\[
 N(I)\cap\{b=r\}=\{i:b(i)=r,\ E_i\le K-h\}.
\]

When `h=+infinity`, no member of `I` is outside `r`, and this neighborhood part is empty.

These identities remain true after replacing `I` by `I*`, because the actual minimum-energy atoms `e` and, when finite, `h` remain present. Thus

\[
 \boxed{N(I^*)=N(I).}
\]

Also `I subset I*`, so `w(I*)>=w(I)` by nonnegative weights. The deficiency cannot decrease. Every maximum deficiency is therefore attained by one of these two-threshold sets or by the empty set.

This argument requires all energy-qualified cross-bin edges to exist. It does not automatically extend to arbitrary graph masks on bins: the minimum atom in bin `r` would then fail to generate every outside-bin prefix used above.

## 5. Exact separable formula

Use inclusive prefix and tail definitions:

\[
 T_r(e)=\sum_{b(i)=r,E_i\ge e}w_i,\quad
 T_{\bar r}(h)=\sum_{b(i)\ne r,E_i\ge h}w_i,
\]

\[
 P_r(z)=\sum_{b(i)=r,E_i\le z}w_i,\quad
 P_{\bar r}(z)=\sum_{b(i)\ne r,E_i\le z}w_i.
\]

Then

\[
 F_r(e)=T_r(e)-P_{\bar r}(K-e),
 \qquad G_r(h)=T_{\bar r}(h)-P_r(K-h).
\]

Set `G_r(+infinity)=0`. For each actual energy `e` in bin `r`, finite `h` candidates are the actual energy levels outside `r` that satisfy both `h>=e` and `h>K-e`. Then

\[
 \boxed{\Delta=
 \max\left(0,
 \max_{r,e}\left[
 F_r(e)+
 \max_{\substack{h\in E_{\bar r}\cup\{+\infty\}\\h\ge e,\ h>K-e}}
 G_r(h)
 \right]\right).}
\]

The infinity candidate ensures that the inner maximum is always defined and at least zero. Empty bins contribute no `e` candidates. Empty atom input gives `Delta=Cmax=0`.

### Algorithmic reading

For each bin, sort complete distinct outside energy levels and precompute the suffix maximum of `G_r(h)`, also comparing every suffix with the infinity value zero. For a candidate `e`, find the first outside level satisfying both inequalities. In ascending order its index is the maximum of:

- `lower_bound(e)`, for `h>=e`;
- `upper_bound(K-e)`, for `h>K-e`.

Use the corresponding suffix maximum. Compute prefix/tail masses by exact cumulative sums. The resulting bound of `O(k*n*log n)` comparisons/arithmetic operations is conservative and valid. Exact-rational bit costs must remain separately qualified. No `O(n^2)` atomic edge matrix is necessary to evaluate the formula.

Choose complete tied-energy levels; using a partial atom prefix at a tie would change the neighborhood calculation. Deterministic tie-breaking between equally optimal `(r,e,h)` values affects only the selected certificate, not the optimum.

## 6. Certificate and attainment obligations

The maximizing canonical set supplies the explicit feasible dual

\[
 y=0\text{ on }I^*,\qquad
 y=1\text{ on }N(I^*),\qquad
 y=1/2\text{ elsewhere}.
\]

The two sets are disjoint: `e+h>K` gives `e>K-h` and `h>K-e`. Its weighted objective is exactly `(N-Delta)/2`.

If the implementation returns a primal cross-event measure, an independent verifier should check every atom's incidence, allowed bin distinction, closed energy cap, all residual singles, and

\[
 \sum_e x_e=\sum_iw_iy_i=(N-\Delta)/2
\]

with exact rational equality. The mathematical existence of such a primal follows from the finite matching proof. The proposed suffix sweep itself does not output it.

One constructive route is the symmetric bipartite double-cover flow followed by `x_ij=(f_ij+f_ji)/2`. A dense graph is unnecessary in principle: every left atom's allowed right neighbors are energy prefixes in the other bins, permitting a prefix/segment representation. Such a representation requires its own exact disaggregation and marginal checks; its performance is not established by this review.

For a requested `C` below `Cmax`, scaling a valid maximum cross witness by `C/Cmax` and making all residual legs singles preserves every marginal. The zero optimum requires a direct singles branch. Choosing only cross doubles gives `d=C`; it does not characterize every feasible total `d` under the energy cap. In particular PR113's unrestricted-diagonal fixed-`d` interval must not be imported into this new energy-restricted problem.

## 7. Analytic boundary checks; no numerical execution

1. **One bin:** the graph is empty. Choosing the entire bin as `I` gives `Delta=N`, hence `Cmax=0`.
2. **Empty graph:** the full vertex set is independent, so `Delta=N` and `Cmax=0`.
3. **All cross pairs allowed:** independent sets lie in one bin. The formula reduces to `Delta=max(0,2*n_max-N)` and `Cmax=min(N/2,N-n_max)`, recovering the complete-bin predecessor result.
4. **Equal energies across bins:** finite `h=e` is admissible only when `2e>K`. If `2e=K`, these cross edges exist and that independent set is forbidden. This checks the strict inner inequality.
5. **Zero masses:** the proof and objective remain valid. Keeping zero-mass atoms simplifies full-graph dual verification. An implementation that removes them must explain how the dual is lifted back while preserving all zero-capacity-vertex edge constraints.
6. **Zero total mass:** `Cmax=0` without division, irrespective of graph edges.
7. **No outside atom:** only the infinity candidate is present.
8. **A bin with tied energy minima:** any minimizing atom chooses the same complete energy tail. Ties between bins can be assigned to any minimizing bin `r`; the outside minimum `h=e` is covered when the strict independence condition holds.
9. **Cap monotonicity:** enlarging `K` only adds cross edges, so `Cmax(K)` is nondecreasing. For finite atoms it changes only at cross-bin pair sums and is right-continuous because equality is admitted.

### Distinct cutoff behavior from PR114

The PR114 diagonal threshold `K=2Eghost` is not a cross edge. In the retained source, the ghost is in its own bin and the active atoms have energies strictly greater than the ghost energy. Hence both `K=1/5` and `K=2Eghost` have `Cmax=0`. The first possible positive cross threshold is a ghost/active cross-bin pair sum, not a same-atom diagonal sum. Reusing the old total-`d` cutoff jump as a new cross-`C` jump would be a scientific error.

## 8. Physical scope and reporting

The formula supplies a sharp conditional mathematical envelope for the exact supplied atom marginal and declared cap. It supplies no measured cap, exclusive He joint kernel, actual cross coefficient, outside response, donor work, EOS/T, absolute volume, or full physical native25.

For a concrete witness, the existing once-only consumer still applies the proper-window factor once and requires the original source/state/frame/clock/nb/replay and neutral-inventory conditions. A pure cross witness with residual singles has `d=C`; its parent coefficient is `N-C`. The partition-union correction is the already established `(C,0,-C)` in He I/II/III coefficient space, with chemical correction `-(I1+I2)C`. These identities do not determine the physical value of `C`.

The source snapshots can be reused by identity. No old source-fit, projection, RR, photon, PR113, or PR114 science replay is required to prove this new finite-graph statement.

## 9. Findings and open obligations

| ID | Finding | Disposition |
|---|---|---|
| A01 | General independent-set deficiency equality needs an attainment argument, not only a feasible dual | Supplied by the finite double-cover proof and canonical half-integral dual normalization |
| A02 | Canonical enlargement must preserve every outside-bin neighbor, including edges among outside bins | Proved exactly in Section 4.2 |
| A03 | `h>=e` and `h>K-e` have different inclusivity | Preserve `lower_bound` versus `upper_bound`; exact tie tests required |
| A04 | `h=+infinity` and empty input/bin cases | Explicit zero inner candidate and empty-set baseline required |
| A05 | Formula/dual sweep does not construct an explicit primal event witness | Separate implementation obligation if witness/native return is in scope |
| A06 | Fixed-`d` and diagonal completion from PR113 do not survive arbitrary energy exclusions | Keep scope to cross optimum/target; use singles for residual legs |
| A07 | PR114 ghost diagonal jump is not a cross event | New cross-threshold controls and plots must use cross-bin pair sums |
| A08 | Arbitrary bin graph masks change the canonical neighborhood structure | Excluded by the fixed complete-cross-bin scope |

The mathematical formula has no remaining proof gap under this scope. Implementation execution, independent finite checks, primal construction if required, visual QA, and native-return admission remain future evidence obligations owned by the parent unit's separately frozen budget.
