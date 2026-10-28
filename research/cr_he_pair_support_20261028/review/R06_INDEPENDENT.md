# R6 independent mathematical review

**Decision: PASS_SCOPED_THEOREM_REVIEW. One concrete scope clarification, R6-F1, is CLOSED; open mathematical blockers: 0.**

Unit: `CR_PHYS02_HE_PAIR_SUPPORT_V1`. Reviewer task: `/root/repo_census`. Review completed against the file identities recorded in `R06_INDEPENDENT.json` on 2026-10-28 UTC. The reviewer derived the flow correspondence, cut dual and fixed-double construction from the frozen contract before reading the author's theorem, then compared the derivation with `theory/THEOREM.md`, R03–R05 and the unchanged PR112 consumer. No production solver, scientific script, CAS or foreign scientific code was executed in this review.

## 1. Result and precise feasible class

The claims hold for a finite simple undirected graph on bins with nonnegative finite masses, where every allowed cross-bin edge permits the full Cartesian rectangle of atom pairs. Singles and same-atom diagonal doubles are allowed. The atom marginal is an electron-leg measure. An unordered double event consumes one leg at each endpoint, or two legs at its repeated endpoint.

With incidence matrix `B`, the sharp cross-event mass is

\[
\rho_G(n)=\max_{x\ge0,\,Bx\le n}\sum_e x_e
          =\min_{y\ge0,\,y_i+y_j\ge1}\sum_i n_i y_i.
\]

The attained cross masses form `[0,rho_G(n)]`. When total selected-internal double-event mass is prescribed as `d` with `0 <= d <= N/2`, they form `[0,min(d,rho_G(n))]`. These are mathematical event-measure statements. Consumer admission also imposes source and physical-state binding gates, including the inventory condition discussed in §7 below.

The real-valued theorem is compatible with exact rational implementation: rational input masses and rational requested `C,d` admit rational witnesses. Half-integral **dual coordinates** do not assert that arbitrary rational primal event masses are half-integers.

## 2. Independent flow and dual derivation

Put source capacity `n_i` on `s -> L_i`, sink capacity `n_i` on `R_i -> t`, and both arcs `L_i -> R_j`, `L_j -> R_i` on every undirected edge. For `N>0`, middle capacity `2N` is sufficient.

Given a graph assignment `x`, place `x_ij` on both directed counterpart arcs. The outgoing mass at `L_i` and incoming mass at `R_i` both equal `(Bx)_i`, so the assignment is a feasible flow of value `2 sum_e x_e`.

Conversely, for any feasible flow define `x_ij=(f_ij+f_ji)/2`. Its incidence at `i` is half of the outgoing mass at `L_i` plus incoming mass at `R_i`. Both terms are at most `n_i`. Thus `Bx <= n`, and the graph objective is exactly half the flow value. This establishes both inequalities and hence `F_max=2 rho` without an assumption that the returned maximum flow is itself symmetric.

A source-only cut has capacity `N`. Since `2N>N`, a minimum cut cannot contain a middle arc. Write `l_i=1{L_i is on the source side}` and `r_i=1{R_i is on the source side}`. Absence of cut middle arcs gives `l_i<=r_j` and `l_j<=r_i` for every edge. Therefore

\[
y_i=\frac{1-l_i+r_i}{2}\in\{0,\tfrac12,1\},\qquad
y_i+y_j=1+\frac{r_i+r_j-l_i-l_j}{2}\ge1.
\]

The cut capacity is `sum_i n_i(1-l_i+r_i)=2 n dot y`. The finite maximum-flow/minimum-cut equality therefore provides a dual objective exactly equal to the graph objective. Independently, summing `(y_i+y_j)x_ij >= x_ij` gives weak duality `sum_e x_e <= n dot y`. A returned feasible primal/dual pair with equal objectives certifies optimality independently of an algorithm's status label.

The author's explicit `N=0` branch avoids the invalid strict inequality `2N>N` at zero: `x=0`, `y_i=1/2` is feasible with equal zero objectives. Empty graphs admit `y=0`. Isolated or zero-capacity bins are retained and need no division. These branches close the relevant degeneracies.

## 3. Attainable interval and fixed internal double mass

Compactness of the finite feasible polytope supplies an optimum `x*`. For `rho>0`, `(C/rho)x*` realizes every `C` between zero and `rho`. For `rho=0`, only `C=0` is possible and the zero assignment suffices. Remaining electron-leg mass is `N-2C`, which can be assigned to singles.

If total internal double mass is `d`, necessity is `C<=d`, `C<=rho` and `2d<=N`. For sufficiency, after constructing cross mass `C`, allocate `2(d-C)` residual legs to atomic diagonal doubles and use the remaining `N-2d` legs as singles. The required residual-capacity inequality is

\[
2(d-C)\le N-2C \iff 2d\le N.
\]

Thus no additional positive lower bound on `C` arises in this mathematical feasible class. This conclusion uses the explicit permission for diagonal events. The graph does not need a self-edge because diagonal completion is a separate part of the contract.

Boundary cases follow directly. For `d=0`, every event is single and `C=0`. For `d=N/2`, all legs are paired, with the portion `d-C` supplied by diagonals. An empty graph or mass confined to isolated bins has `C=0` but permits every such `d`. A triangle with masses `(1,1,1)` realizes `rho=3/2` using weight `1/2` on each edge and dual `(1/2,1/2,1/2)`; an integral-matching result of 1 would solve a different feasible problem.

## 4. Atomwise sparse realization and the factor of two

Fix any feasible bin assignment. Before handling an edge, the residual capacity in each incident bin is at least the total demand of its unprocessed incident edges: previous withdrawals have subtracted only previously processed edge demands. A submeasure of the required edge mass can therefore always be withdrawn from each endpoint bin.

Greedy coupling of the two equal-mass finite submeasures pairs their first positive residual atoms, emits the smaller remaining amount, and advances exhausted entries. Full Cartesian support makes every emitted pair legal. Each positive step either exhausts an original residual atom or finishes the current edge; a coarse bound of `A_+ + E_+` cross records is enough to establish sparsity. Diagonal completion and singles each require at most one record per remaining atom. This argument does not depend on constructing a dense pair matrix.

For a cross record `(a,b)` with event weight `w`, use the symmetric ordered measure

\[
D_{ab}=\frac w2(\delta_{(a,b)}+\delta_{(b,a)}).
\]

Then `2 pi_1 D_ab` contributes `w` at each distinct endpoint. If `a=b`, the same formula equals `w delta_(a,a)` and contributes **`2w`** at that atom. Adding singles produces exactly `mu=S+2 pi_1 D`. The unchanged event-list consumer implements the same convention by iterating both electron entries, including a repeated key.

Consequently the construction preserves every atom's weight, energy, key and bin; it does not move or duplicate the cutoff ghost or extend the stored support. Verification of the instantiated 3,201 marginals belongs to the forthcoming coding run, not to this nonexecuting review.

## 5. Complete graph and sensitivity checks

The complete-graph formula can also be checked directly using the established half-integral dual result. A feasible half-integral cover with no zero coordinate costs at least `N/2`. If it has a zero coordinate at bin `i`, every other coordinate must be one, so its cost is at least `N-n_i >= N-n_max`. The all-half vector and the vector zero at a largest bin/one elsewhere attain the corresponding costs. Therefore

\[
\rho_{K}(n)=\min(N/2,N-n_{\max}),
\]

with the zero and one-bin cases handled directly. This independently agrees with the author's star and half-circle constructions and the predecessor bound.

Adding graph edges or increasing capacities enlarges the primal feasible set. Scaling all capacities by a nonnegative factor scales the optimum by the same factor, including scale zero. An optimal dual can be clipped to `[0,1]` without harming edge coverage. Applying the clipped optimal dual for `m` to capacities `n`, then reversing the roles, proves `|rho(n)-rho(m)|<=sum_i|n_i-m_i|`. This is sensitivity within the supplied finite model; it adds no estimate of physical model error.

## 6. Source, time, units and consumer signs

The source retains coefficient history `q_a(t)=t a_a` on the fixed proper-time domain. On an allowed window `[u,v]`, `W=(v^2-u^2)/2` is positive and carries units `s^2`. Coefficients have units `m^-3 s^-2`; integrated event and electron densities have units `m^-3`. Thus `C_window=W C_coeff`, `d_window=W d_coeff`, and the homogeneous graph optimum scales once by `W`.

The inherited source loader preserves the exact stored binary64 values. In particular, the numerical cutoff used by the code is the exact rational lift of stored binary64 `0.1`; replacing it by exact decimal `1/10` would change that source convention. R03 and the theorem retain atom identity and delegate source binding to the byte-reused consumer.

For a cross double appearing once in each of two partition claims, the naive species change is `(-2,0,+2)` while the event union contributes `(-1,0,+1)`. Their difference is `(1,0,-1)` per event. Therefore the integrated correction is `(C,0,-C)`, ionic charge correction `-2C`, and chemical correction `-(24.59+54.42)C`. Electron and selected kinetic energy corrections vanish because the same two legs and their energies are counted once in either partition sum. Baryon number is unchanged.

The actual source/state/frame/proper-window binding, exact `nb=8750/47`, allowed support, once-only time admission and independent RR/photon ports remain inherited obligations. These formulas describe a conditional partial source contribution. Actual physical graph/kernel/C/D, selected-outside response, donor work, EOS/T, absolute volume and full physical native25 remain null under the frozen contract.

## 7. Finding R6-F1 — CLOSED after patch verification

**Object:** The connection between mathematical feasibility and same-state consumer admission in the initial theorem §6.

**Evidence:** The unchanged PR112 `consume_event_union` additionally requires integrated parent count to be at most `Hcap=(1085/94)(99/100)`. The initial theorem's summary of consumer gates omitted this concrete bound. A feasible graph and exact atom marginal alone do not imply it for arbitrary formal capacities and windows.

**Consequence:** For the constructed witnesses, which contain no selected-outside double events, parent coefficient is `A_tot-d_coeff`. Admission requires

\[
W(A_{\rm tot}-d_{\rm coeff})\le H_{\rm cap}.
\]

When `d_coeff` is fixed, the mathematical `C_coeff` interval survives this inventory gate only if that inequality holds; otherwise that consumer family is rejected. When `d` is omitted and the contract chooses `d_coeff=C_coeff`, this particular family further requires

\[
C_{\rm coeff}\ge\max(0,A_{\rm tot}-H_{\rm cap}/W),
\]

in addition to `C_coeff<=rho_G(a)`. If the lower endpoint exceeds the upper endpoint, the family has no consumer-admitted member for that window. This derived gate is distinct from mathematical attainability and does not change its proof.

**Minimal correction and verification:** The author added the exact inventory inequality as theorem §6 Eq.(8), explicitly distinguished formal feasibility from consumer admission, and recorded the correction in `R05_DERIVATION_KO.md`. The reviewer read the patched paragraph and R05 and recorded their latest SHA256 identities in the companion JSON. R6-F1 is CLOSED. Actual retained-source witness admission remains a C-stage execution obligation; no scientific rerun was requested or performed for this textual correction.

## 8. Review disposition and remaining stage obligations

T1–T6 are accepted under the stated assumptions. Twelve manually identified review obligations are recorded in the companion JSON as passed. One finding was raised and corrected; no open mathematical blocker remains. There is no global novelty or physical-kernel claim.

This R6 result does not stand in for production execution or C9 code/result review. The implementation must still return and verify exact primal/dual certificates, compare with the independent finite dual oracle, verify the original atom marginals and selected consumer cases, and preserve the scoped nulls and once-only guards. No unchanged predecessor scientific calculation was repeated.

`skill_context_used`: `next_work/policy/RESEARCH_POLICY.md` (1.0.0), `THEORY_LOOP.md` (R6), and `SUBAGENT_MODE.md` (finite independent review, no recursive delegation). Local scientific execution count: **0**. Metadata/provider/publication CPU: **null/unmeasured**. Central snapshot remains qualified **28/88**, 88 nodes/17 edges; this review has central count effect 0.
