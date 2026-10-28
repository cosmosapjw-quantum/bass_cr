# Exact joint event region in the declared low–high cross domain

## Result

For the finite rational event model of R03_CLAIMS, suppose every permitted positive-mass low–high pair has unequal birth-bin labels. Write L for total low mass, M for the maximum capacity-limited high–low matching mass, D=(L+M)/2, and X for the maximum cross-bin double mass. Then the exact projection of all marginal-preserving event measures onto (d,C) is

\[
\mathcal P=\{(d,C):0\le d\le D,\quad0\le C\le X,\quad C\le d,\quad2d-C\le L\}.
\]

In particular the individual maxima have a common witness (D,X). For every 0<=d<=D,

\[
C_{\min}(d)=\max(0,2d-L),\qquad C_{\max}(d)=\min(d,X).
\]

For every 0<=C<=X,

\[
d_{\min}(C)=C,\qquad d_{\max}(C)=\min\{D,(L+C)/2\}.
\]

Event coefficients in the real polytope statement are nonnegative real numbers; atom inputs remain rational. Every rational point in this region admits a finite rational event measure with the original atom marginals. If event coefficients are required to be rational, the exact projection is P intersect Q^2. The proof supplies an explicit convex construction; it does not merely assert scalar feasibility.

## Definitions and existence

An atom has mass a_i>=0, energy E_i>=0 and bin b_i. A low atom satisfies 2E_i<=K; a high atom satisfies 2E_i>K. Singles are always allowed. Every unordered pair i,j with E_i+E_j<=K is allowed, including i=j. A diagonal p_ii consumes 2p_ii of atom i. There are no additional edge masks. Zero-mass atoms can be deleted for the proof and reinstated with zero marginal.

There are finitely many event variables. Nonnegativity and the marginal equations bound each variable by the total input mass, so the feasible polytope is compact and nonempty (all singles). Its rational constraints imply that a nonempty optimal face has a rational vertex. Thus d, C and all lexicographic optimizers used below attain their optima. No limiting, closure or numerical-tolerance argument is needed.

No high–high pair is allowed: each energy exceeds K/2. Every low–low pair and low diagonal is allowed. A capacity-limited high–low matching f_hl has sum_l f_hl<=a_h and sum_h f_hl<=a_l. Its maximum total is M. This is a submatching problem, not a probability coupling obtained by normalizing the two sides separately.

## Lemma 1: total-double maximum

For any event measure let m be its high–low mass and r its low–low mass. Then d=m+r and the used low marginal is m+2r=2d-m<=L. Since its high–low part is a feasible submatching, m<=M. Therefore d<=(L+M)/2.

Conversely take a maximum high–low matching of mass M. At each low atom fill its remaining marginal with the allowed diagonal, coefficient equal to half the residual. Leave each residual high marginal single. This produces d=M+(L-M)/2=D. It is the same leg-counting result used by the identity-pinned PR114 witnesses. In particular M<=L and D<=L.

## Lemma 2: the joint necessary inequalities

Nonnegativity gives d,C>=0. The definitions of D and X give d<=D and C<=X. Every cross event is a double, hence C<=d. By the domain assumption, every high–low event is cross-bin, so m<=C. Consequently

\[
2d-C\le2d-m\le L.
\]

Also M<=X: any high–low maximum can be kept as cross doubles with all remaining atoms single. And X<=D: a cross-only maximum is itself an allowed event measure with d=X. Thus

\[
0\le M\le X\le D\le L.
\]

## Lemma 3: simultaneous attainment

Start with cross doubles and singles only; this loses no C optimum, since any same-bin double can be replaced by its two singles without changing C. Among all cross-only measures of maximum C=X, choose one whose high–low mass m is largest. This secondary maximum exists on a compact rational optimal face.

Suppose m<M. Regard its high–low edges as a bipartite capacity flow, with source-to-high capacity a_h, permitted high-to-low edges of capacity N (N=sum_i a_i suffices), and low-to-sink capacity a_l. A larger feasible high–low flow exists by the definition of M. Therefore the current residual graph has a source-to-sink augmenting path: if none existed, the source-reachable cut would certify maximality. Remove cycles to take a simple path. Its first high has unused high capacity; its last low l has unused capacity relative to high–low occupancy. Intermediate high and low vertices have unchanged total high–low occupancy after a path augmentation.

In the cross-only event measure, high atoms have no other kind of double, so the first high has available single mass. The last low's non-high–low marginal is a sum of single mass and low–low cross incidences. At least one summand is positive. Choose epsilon>0 no larger than every path residual and than one positive endpoint summand (and the source-high single mass). All quantities may be chosen rational.

* If the last low has positive single mass, augment the high–low path by epsilon and reduce the two endpoint single masses. The net high–low flow, and therefore the cross mass, increases by epsilon. Internal alternating edges are all cross-bin by the domain assumption. This contradicts C=X.
* Otherwise choose a positive low–low cross edge (l,q) incident to the last low. Remove epsilon from this edge; augment the high–low path by epsilon; reduce the source-high single by epsilon and add epsilon to the single at q. The last low exchanges one low–low leg for one high–low leg. The other endpoint q is distinct from l because a cross edge is not a diagonal. Even if q is an internal path vertex, its path occupancy has zero net change, so its freed leg is correctly represented by the added single. All marginals, nonnegativity and support remain valid. Cross mass is unchanged (plus epsilon high–low, minus epsilon low–low), while m increases by epsilon. This contradicts secondary optimality.

Both possibilities contradict m<M. Hence a cross-maximal measure exists with high–low mass M. Its low-leg use is M+2(X-M)=2X-M. Fill each remaining low marginal by its diagonal. The sum of the new diagonal coefficients is

\[
\frac{L-(2X-M)}2=D-X\ge0.
\]

The completed measure has d=X+(D-X)=D and C=X. This proves simultaneous attainment with all original atom marginals.

The residual-path argument is also a finite rational construction. Given any rational cross optimum, clear all denominators of its event masses and input capacities. Repeatedly augment as above by the minimum positive residual and endpoint summand in that integer scaling. A single-ending path cannot occur while C is optimal. Every remaining step increases m by at least one scaled unit and m<=M, so the process terminates finitely at M. This is an existence/termination guarantee; it is not a claim of a strong polynomial runtime bound for that lexicographic procedure.

## Lemma 4: explicit vertex witnesses

All five named witnesses below have the same original marginal vector, including their residual singles:

| Label | Coordinates | Construction |
|---|---|---|
| O | (0,0) | All atoms single |
| A | (L/2,0) | Every low atom diagonal; all high atoms single |
| B | (D,M) | Maximum high–low matching, remaining low legs diagonal, residual high legs single |
| F | (D,X) | Lemma3 cross optimum with high–low mass M, completed by low diagonals |
| G | (X,X) | The cross-only portion of F, replacing its added diagonals with singles |

These labels may coincide. In particular A=B if M=0, B=F if X=M, and F=G if X=D. Coincidence does not require distinct event representations to be identical; either representative is sufficient.

## Lemma 5: constructive sufficiency and degeneracies

If X=0, then M=0, C=0 and D=L/2. If D=0, O is the only point. Otherwise any requested d in [0,D] is the convex mixture (d/D)A+(1-d/D)O. All formulas are well-defined.

Now assume X>0 and choose 0<=C<=X. A lower-bound witness Q(C)=(C/X)G+(1-C/X)O has coordinates (C,C).

For the upper-bound witness U(C), use:

* If M>0 and C<=M: U=(C/M)B+(1-C/M)A, giving d_U=(L+C)/2.
* If C>M (necessarily X>M): U=((C-M)/(X-M))F+((X-C)/(X-M))B, giving d_U=D.
* If M=0: U=(C/X)F+(1-C/X)A, again giving d_U=D.

These branches cover C=M without dividing by X-M when X=M. In every case d_U=min(D,(L+C)/2). The necessary inequalities imply C<=d<=d_U. If d_U=C, take Q (the only possible d). Otherwise set

\[
\theta=(d-C)/(d_U-C),\qquad \mu=(1-\theta)Q+\theta U.
\]

Here 0<=theta<=1. Linear combination of the complete event measures, including singles, preserves every atom marginal, allowed support and positivity, and gives exactly the requested (d,C). Rational inputs and target coordinates yield rational coefficients. This proves sufficiency, not only the vertices, and completes the theorem.

## Scope, prior art and use

General fractional matching polytope theory and finite weighted Hall/Strassen equivalence are prior art (R2_LITERATURE_REVIEW). This proof explicitly handles our two-leg diagonal convention, the energy-threshold low/high structure, and the stated cross-bin domain. It is a project-specific constructive result; no exhaustive global-priority claim is made.

The equal-bin two-atom example in R04 shows that extending the facet 2d-C<=L beyond this domain is false. Domain rejection alone asserts no impossibility for other data. This is a scope counterexample and is not admitted as a strong scientific no-go.

The observable correspondence is R03_CLAIMS and its independent consumer review. A mathematical witness is a possible exclusive event measure under the contract. It does not determine the physical K, actual exclusive kernel or activate a coupled physical source. Native verification and performance are separate coding obligations.
