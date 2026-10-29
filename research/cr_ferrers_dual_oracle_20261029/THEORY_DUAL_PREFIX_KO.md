# BASS-CR | CR_FERRERS_DUAL_ORACLE_V1 | 원래 HL dual 부등식의 prefix-minimum 정확 인증

**Research branch**: immutable PR124 HEAD `a6b49b352fed31587955d55b1cad30c0b55a81eb`의 독립 child만 허용. **Original source**: `ATTRIBUTION_ARRAYS.npz`, SHA-256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. **Tier**: source-conditional finite fractional HL event allocation, *not* physical exclusive He collision law.

## Definition / dimensions

High set H: `2 E_h > K`; low set L: `2 E_l <= K`; `E_i`, `K` in eV. Birth bins `b_i` immutable. Each original edge `(h,l)` exists iff `E_h+E_l<=K`. Cross-bin cost `chi_hl = 1[b_h != b_l]`, else 0. Marginal capacities `w_i` and budget `c` have original source units m^-3 s^-2, and `p_i>=0, lambda>=0` are dimensionless dual multipliers. Zero-mass atoms are **not** erased from the original logical edge universe. The original budget LP is `M(c)=max Σ_hl x_hl` subject to source/target capacities and `Σchi x <= c`; original `dmax=(Ltot+M)/2` retains PR124's low-low completion premise. Its dual feasibility requires for *every* original admissible HL edge:

`p_h + p_l + lambda*chi_hl >= 1`.

## Theorem: exact prefix-minimum dual oracle (derived)

For each low birth-bin `b`, sort **all** low atoms by increasing original exact energy (including zeros) to get `(l_b1,...,l_bn_b)`. For each high `h` define `k_hb=#{j : E_l_bj <= K-E_h}`. The graph restriction `N(h)∩L_b` equals the entire prefix `j<=k_hb`. For each nonempty prefix define `P_b(k)=min_{1<=j<=k}p_l_bj` and retain one atomic witness `j_min`. Then the following are equivalent:

1. All `p_h+p_l+lambda*chi_hl>=1` for every original admissible HL edge (including zero-mass atoms).
2. For each `(h,b)` with `k_hb>0`, `p_h+P_b(k_hb)+lambda*1[b_h!=b]>=1`.

**Proof.** Fix `(h,b)`. The cost `chi_hl` is constant across that bin; the admissible set is exactly the prefix. Therefore the left-hand side of the entire block is minimized at any exact minimizer `j_min`. All original block inequalities hold iff the single inequality at `j_min` holds. Taking conjunction over every high and populated low bin proves both directions; the minimizing atom is an original-graph counterexample whenever the reduced inequality fails. All arithmetic is exact rational. This is a logical equivalence, not sampling or an approximate bound. QED.

**Complexity.** First precompute sorted low blocks and `k_hb` at cost `O(L log L + HB log L)` comparisons (`B` = number of populated birth bins). Record the total original-edge count exactly as `sum_hb k_hb` and the nonempty `(h,b)` count as `Q <= HB`. Per budget, compute low price prefix minima `O(L)` and verify `Q` inequalities `O(Q)` (plus exact integer/rational bit costs). Storage `O(L+Q)` excluding original atoms, prices and outputs. By contrast the literal enumerator requires `O(|E|)` arithmetic per budget and an explicitly stored list of |E| edge pairs in PR124. Worst case no speed advantage if `B` comparable to `L`, arithmetic bit costs dominate, or the optimizer/witness path dominates.

## What the lemma does not change

- The original C++20 SSP solve, energy relation, source capacities, exact original-node prices, primal atom-wise conservation and cost, `M(c)`, `dmax(c)`, lambda and the exact zero-gap criterion are unchanged. The full original witness remains available.
- `checked_edges=102831` in prefix mode means **logically certified original-edge inequalities**, not 102831 explicit pair iterations. New `dual_check_mode` and `grouped_dual_constraints` fields distinguish evidence paths.
- When costs vary **within** a bin, or neighborhoods cease to be nested energy prefixes, the theorem is inapplicable. No variable-cost shortcut or source reweighting is authorized.
- Fixed-`C` feasible joint region is distinct from `C<=c` upper frontier. This certificate applies to the latter budget dual, without claiming the former's exact structure.
- No physical kernel, K choice, clock, normalizer, energy ownership, stop law, native25, L4 or production promotion follows. The old PR118 resource FAIL and missing aggregate CPU cap certification remain.

## Independent checks / limits

- Wolfram Language evaluated 1000 deterministic exact rational finite-prefix test instances: 1000 equality-of-predicate outcomes, 0 discrepancies. Finite tests are secondary to the general proof.
- Python differential tests: 300 random exact rational multi-bin original-graph predicate comparisons, with zero mass, duplicate energy and failure-witness checks. 9/9 normal and `-O` integration+existing tests passed.
- Actual 3201 source 3-budget paired end-to-end 3x checks matched exact price, witness, C, M, dmax and gap. A genuine distinct-author R06 and C09 review remains **NOT_RUN**; this self-contained derivation is not an independent author acceptance.

## Literature / novelty boundary

Király & Kovács (2012), *Efficient implementations of minimum-cost flow algorithms*, https://arxiv.org/abs/1207.6381 establishes broad prior art for SSP, potentials and performance heuristics. This note does **not** assert invention of prefix minima, segment trees or generic min-cost flow; it derives and tests exact original-edge dual certificate reduction for this locked CR Ferrers-by-bin instance and its evidence constraints.
