# CR_GENERIC_POTENTIALS_EXACT_V1: 단일 budget의 exact primal–dual construction

**Authority**: `bass_cr` PR121, immutable original `ATTRIBUTION_ARRAYS.npz` SHA-256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. This is a conditional finite event LP, **not** a measured physical helium kernel. Central DAG 28/88 and extension 0/3 remain unchanged.

## 1. Definition and reduction

For exact nonnegative rational masses \(w_h,w_l\), exact energies in eV, and a *conditional* K in eV, define eligible \(\mathcal A=\{(h,l):E_h+E_l\le K,\;2E_h>K,\;2E_l\le K\}\). Let \(\chi_{hl}\in\{0,1\}\) indicate different bins. The primal is
\[
M(c)=\max_{x\ge0}\left\{\sum_{(h,l)\in\mathcal A}x_{hl}:\sum_lx_{hl}\le w_h,\;\sum_hx_{hl}\le w_l,\;\sum_{hl}\chi_{hl}x_{hl}\le c\right\}.
\]
All masses and \(c\) have the stored `m^-3 s^-2` units. \(C_{\min}(m)\) is the minimal cross mass at fixed high-low mass \(m\). The parent theory gives \(M(c)=\max\{m:C_{\min}(m)\le c\}\) and \(d_{\max}(c)=(L+M(c))/2\), with unused low marginals completed as diagonal low-low pairs. This conclusion concerns the **inequality** \(C\le c\), not the exact fixed-\(C\) joint feasible region.

## 2. Exact integer scaling

Choose \(Q=\operatorname{lcm}(\{\mathrm{den}(w_i)\},\mathrm{den}(c))\). Then all scaled capacities \(W_i=Qw_i\) and budget \(B=Qc\) are nonnegative integers. Integer-cost SSP operates on \(s\to H\to L\to t\), with capacities \(W_h,W_l\) on vertex arcs, effectively unlimited \(H\to L\) admissible arcs (larger than the total possible flow) and costs \(\chi_{hl}\in\{0,1\}\). Reverse residual arcs have costs \(-\chi_{hl}\). The maximal input scale is bounded by explicit i128-safe guards; not all rational inputs have such a feasible integer scaling. Original binary64 capacities are dyadic and the pinned NPZ has \(Q=2^{185}\), scaled individual mass <=56 bits, total <=67 bits. The actual code recomputes the lcm for each budget and checks overflow before invoking C++.

## 3. Reduced-cost potentials

Maintain integer node potentials \(\pi\) with reduced residual costs
\[
\bar c_{uv}=c_{uv}+\pi_u-\pi_v\ge0.
\]
Initially all forward costs are nonnegative and \(\pi=0\). For every augmenting iteration, run Dijkstra on positive-capacity residual arcs with reduced costs, obtain \(d_v\), and update \(\pi_v\leftarrow\pi_v+d_v\) for reachable nodes. Then \(\bar c'_{uv}=\bar c_{uv}+d_u-d_v\ge0\) for every positive-capacity residual edge leaving a reachable node. After augmentation, newly activated reverse arcs lie on zero-reduced-cost path edges, so the same potential invariant is retained. The original path cost \(k=\pi_t-\pi_s\) is an integer and nondecreasing; it is a valid right slope of the convex finite \(C_{\min}(m)\) curve.

For budget \(B\), if the next positive-cost augmentation with path cost \(k>0\) and integer bottleneck \(\Delta\) would exceed \(B\), stop at the previous integer flow \((m_0,C_0)\) and add **exactly** \(\delta=(B-C_0)/k\) along that residual path. This may be a non-integer in the scaled units. Store each resulting edge flow as numerator/denominator rather than rounding. The budgeted optimum has \(m=m_0+\delta\) and \(C=B\). At the maximum-flow terminus, unused budget is permitted and \(C\le B\) can be strict.

## 4. Constructive original-graph dual certificate

The LP dual in the scaled coordinates is
\[
\min_{p_h,p_l,\lambda\ge0}\left(\sum_hW_hp_h+\sum_lW_lp_l+B\lambda\right),\qquad p_h+p_l+\lambda\chi_{hl}\ge1 \quad\forall(h,l)\in\mathcal A.
\]
At an open segment with positive integer marginal cost \(k\), take the cost-optimal integer flow \(x_0\) at its left endpoint. Since \(k\in\partial C_{\min}(m_0)\), adding an unbounded-capacity return arc \(t\to s\) of cost \(-k\) creates no negative-cost residual circulation. Find integer shortest-distance potentials \(d_u\) from a super source connected at zero cost to every vertex, so every positive residual arc obeys \(c_{uv}+d_u-d_v\ge0\). Then the unbounded forward return arc gives \(d_t-d_s\ge k\); each never-saturated admissible HL arc gives \(d_l-d_h\le\chi_{hl}\). Define
\[
q_h=\max(0,d_h-d_s),\quad q_l=\max(0,d_t-d_l),\quad p_h=q_h/k,\quad p_l=q_l/k,\quad\lambda=1/k.
\]
Consequently \(q_h+q_l+\chi_{hl}\ge k\) for **every** admissible edge and dual feasibility follows. Equality of the exact scaled primal and dual objectives is verified directly in C++ and independently from Python, not inferred from a floating tolerance. In the maximum-flow saturated case, use the reachable-set minimum cut \(p_h=1\) for unreachable highs and \(p_l=1\) for reachable lows, with \(\lambda=0\). Any zero-mass source atom omitted from the active graph receives price 1 at zero objective cost; all original admissible edges are then checked by the external verifier. The Python consumer verifies capacities, every edge, total objective, and the exact zero duality gap.

**Applicability**: the proof assumes nonnegative exact masses, fixed admissible HL graph, unlimited HL edge capacities, finite instance, exact integer scaling, nonnegative initial forward costs and exact arithmetic. It does not transfer to independent physical donor energy budgets, nonlinear rates, kinetic time evolution, or fixed-C joint regions.

## 5. Complexity and stop conditions

The implemented potentials-SSP work is \(O(A(E+V)\log V)\) for \(A\) augmentations, plus a residual dual shortest-distance certificate pass and an \(O(E)\) original-edge verification. This is **augmentation-sensitive**, not strongly polynomial and not a claim of a general cost-scaling implementation. Each large query currently restarts from zero and computes one witness; batched multi-budget re-use and cost-scaling would improve throughput. The source-specific K3 two-cover solver is already faster for its narrow Ferrers property; preserve it as a specialized baseline.

The code's checked integer guard is intentionally conservative: reject source scaling when \(\mathrm{bitlength}(\max\{B,\sum_i W_i+1,\max W_i\})>105\), so bounded potential multiplications and sums fit signed 128-bit capacity arithmetic. The CLI also rejects total capacity >=\(2^{106}\). No unproved silent big-integer fallback.

## 6. Fixed-C counterexample and physics boundary

With **only two low atoms** of mass 1, different bins, and an admissible mixed low-low pair, the exact fixed all-event cross mass \(C=1\) is attainable using the mixed event even though the high-low objective \(M(c)\equiv0\). This disproves any identification of the entire fixed-C joint region with the high-low budget upper frontier alone. The latter remains correct for maximizing the number of doubles subject to an inequality budget, using zero-cross diagonal completion. The He line-transfer and HD/nuclear photodisintegration donor branches do not furnish an exclusive paired He kernel by analogy.

## 7. Literature comparison

- Király & Kovács (2012), *Efficient implementations of minimum-cost flow algorithms*, arXiv:1207.6381. Standard reduced-cost SSP, scaling, network simplex and empirical performance comparison. No new general algorithm novelty is claimed here.
- Ahuja, Magnanti & Orlin (1993), *Network Flows: Theory, Algorithms, and Applications*: classical residual optimality and primal-dual lineage.
- Switzer & Hirata, *Primordial helium recombination I*, PRD 77, 083006: a non-substitutable photon line-transfer/feedback physical authority, not a default binary collision event kernel for the present finite LP.