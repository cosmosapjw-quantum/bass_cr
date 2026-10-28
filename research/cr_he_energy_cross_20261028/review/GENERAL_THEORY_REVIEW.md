# Independent finite-graph basis for the energy-restricted cross-event maximum

Author: `/root/cross_bound_theory`. Date: 2026-10-28.
Status: **DERIVED; reference code AUTHORED_NOT_EXECUTED**.
No source fit, NPZ load, transport, RR, production import or scientific test was
performed by this author. Root owns execution and the new-unit CPU ledger.

## Independence and identity

The supplied baseline is PR114 commit
`c87c50208a7585ff1713bd54303e1a1e29c962cf`, with PR112's source/consumer scope.
Only predecessor definitions and the PR112 report were read. No new production
implementation was read. The task used a full-context child, so the parent's
earlier mathematical discussion was visible; this is **not a blinded review**.
The reference algorithm below is a generic graph enumeration and does not use
the parent's proposed energy-threshold optimization or flow implementation.

## 1. Exact mathematical problem

Let V be finite. Each vertex i has a nonnegative exact rational capacity w_i,
energy E_i >= 0 and partition label b_i. The cap K >= 0 is an explicit
conditional input. Define the loopless undirected graph

    G_K = (V, F_K),
    F_K = {{i,j}: i<j, b_i != b_j, E_i+E_j <= K}.

The cross-event mass is

    C = sum_{e in F_K} x_e,
    x_e >= 0, sum_{e incident to i} x_e <= w_i.

Residual capacity is assigned to single events. Therefore the permitted
same-bin doubles do not alter this maximum: removing those doubles releases
capacity without changing C, while a cross-only feasible x always extends to
a complete marginal by singles. A diagonal never contributes to C.

Write N=sum_i w_i. The feasible x set is a nonempty compact rational polytope
(empty edge set has the unique empty assignment), so its optimum is attained.
The dual is the fractional vertex-cover problem

    Cmax = min sum_i w_i*y_i,
    y_i >= 0, y_i+y_j >= 1 for every {i,j} in F_K.

All statements concern finite weighted electron-leg measures. This is not an
integer matching problem; x=1/2 on each edge of a unit triangle is permitted.

## 2. Constructive exact attainment through a doubled bipartite graph

Make vertices i_L and i_R for each i. Give arcs source->i_L and i_R->sink
capacity w_i. For each undirected permitted edge {i,j}, add both arcs
i_L->j_R and j_L->i_R with a capacity M>N. (If N=0 all flow is zero.)

For any feasible x, use f_ij=f_ji=x_{ij}. This is a feasible flow with value
2C. Conversely, for any feasible flow set x_{ij}=(f_ij+f_ji)/2. Then

    sum_j x_ij = (sum_j f_ij + sum_j f_ji)/2 <= w_i,
    sum_{i<j} x_ij = flow_value/2.

Thus **Cmax=Fmax/2**, and a maximum rational flow constructs an attaining
cross-only event measure. This also proves that the symmetrization factor is
exactly one half; no extra physical source factor enters the event convention.

A minimum cut has cost <=N and therefore cuts no M arc. Put a_i=1 if i_L is
on the sink side and b'_i=1 if i_R is on the source side, and define
y_i=(a_i+b'_i)/2. The two directed copies of each permitted edge imply
a_i+b'_j>=1 and a_j+b'_i>=1. Hence y_i+y_j>=1. Its cost is one half the
cut cost, equal to the attained C. The produced dual is half-integral:
y_i in {0,1/2,1}. This is an elementary proof of the exact primal/dual
certificate for the present finite problem, using max-flow/min-cut.

## 3. Exact independent-set deficiency formula

For an independent set I let N_G(I) be its full open neighborhood. Define

    Delta = max_{I independent} [w(I)-w(N_G(I))],

including I=empty, so Delta>=0. Then

    **Cmax = (N-Delta)/2.**

Proof: Given I, assign y=0 on I, y=1 on N_G(I), and y=1/2 elsewhere. This
is feasible, and its objective is (N-w(I)+w(N_G(I)))/2. Conversely take an
optimal half-integral dual from the doubled-graph cut. Its zero set I is
independent, and N_G(I) is contained in its set of ones. Every extra one
outside N_G(I) can be reduced to 1/2 without violating an edge constraint.
Nonnegative weights make this change non-increasing in cost. The resulting
optimal cover has the displayed form and attains the deficiency formula.
Zero weights therefore cause no exception to the formula.

The formula is a known weighted fractional matching/vertex-cover identity.
The contribution required for this CR continuation is its correct specialization
to the actual atomwise energy-and-partition support and certified consumption;
the general matching theorem is not claimed as a new result or a strong no-go.

## 4. Consequences and limits needed by the consumer

Every C in [0,Cmax] is attainable: scale all pairs of a maximizing cross-only
witness by lambda=C/Cmax and fill each remaining leg with singles. If Cmax=0,
only C=0 is possible and the all-single witness avoids division by zero.

Cmax(K) is nondecreasing and changes only at cross-bin pair sums. The closed
condition E_i+E_j<=K makes the finite step function right-continuous. Same-bin
pair sums and diagonal thresholds alone do not change this objective.

The global bounds 0<=Cmax<=min(N/2,N-max_bin_weight) are preserved. When K
admits every cross pair, the complete multipartite formula is recovered.
For fixed finite K, capacity isolated by energy can make the bound strictly
smaller. A one-bin input always has Cmax=0 even if total double mass dmax=N/2.

This theorem does not provide the full joint feasible set of (d,C). In the
cross-only attaining construction d=Cmax, but other admissible same-bin doubles
can alter d. The separate maximum of d need not occur at the same witness as
the maximum of C. Parent count N-d and absolute source chemical storage depend
on d, while the **partition-sum correction** depends on C alone.

For the latter correction the unchanged PR112 convention gives source species
(+C,0,-C), ionic charge -2C, and chemical-reference correction -(I1+I2)C.
On proper [a,b], multiply coefficient masses by W=(b*b-a*a)/2 exactly once.
The native correction divides by the explicit same-state nb only once.
These statements do not identify physical K, an exclusive He joint kernel,
outside-partner response, donor work, EOS/T or full-source physical native25.

## 5. Independent reference design and fixtures

`reference_oracle.py` has no production import. For n<=7 it explicitly forms
every unordered permitted edge, enumerates all 3^n covers coded by {0,1,2},
and independently enumerates all 2^n vertex subsets to check the deficiency
formula. It returns an exact rational optimum and both kinds of certificates.
The small-certificate verifier checks the supplied primal capacities, every
permitted dual edge and exact primal/dual/oracle equality. All scientific
functions require explicit calls; there is no import-time scientific execution.

Twenty named fixtures are authored but not run. Their analytical values use:
empty/isolated and same-bin graphs => 0; one edge => min(endpoint capacities);
complete multipartite graphs => min(N/2,N-largest partition); a star =>
min(center capacity,sum leaf capacities); two-bin energy fixture weights
(1,3,1,3), energies (0,4,0,4), partitions (0,0,1,1), K=4 => 2 because the
two low legs suffice for and limit the two cross events. A unit triangle
requires the fractional answer 3/2, which rejects accidental integer matching.

Recommended additional controls: exact equality at a cross-pair sum; cap
just below that sum; invalid floating or bool scalars; changed partition;
forged pair support; atom-capacity overflow; wrong factor two in flow
symmetrization; stale source/consumer identity; wrong proper-time factor;
wrong nb; negative dual; incomplete dual constraints; duplicate pair records;
using total d in place of cross C. Existing unchanged predecessor controls
should be reused where their dependency identities still apply.

## 6. Primary-source comparison (searched 2026-10-28)

1. G. L. Nemhauser and L. E. Trotter Jr., *Vertex packings: Structural
   properties and algorithms*, Mathematical Programming **8**, 232-248 (1975),
   DOI 10.1007/BF01580444.
   https://link.springer.com/article/10.1007/BF01580444
   The publisher's accessible abstract explicitly identifies half-integral
   basic solutions. Full paper access was not obtained from that page.

2. M. Chlebik and J. Chlebikova, *Crown reductions for the Minimum Weighted
   Vertex Cover problem*, Discrete Applied Mathematics **156**, 292-312 (2008),
   DOI 10.1016/j.dam.2007.03.026.
   Author manuscript:
   https://pure.port.ac.uk/ws/portalfiles/portal/82876/CN_JOURNAL_rev_final.pdf
   Publisher:
   https://www.sciencedirect.com/science/article/pii/S0166218X07001308
   Manuscript Theorem 2 (PDF page 12, printed page 12) gives the weighted
   independent-set deficiency identity. The manuscript states positive
   weights; the elementary proof above explicitly permits zero weights.
   The introduction also describes the bipartite/maximum-flow reduction.

3. M. Chlebik and J. Chlebikova, *Improvement of Nemhauser-Trotter Theorem
   and its applications in parametrized complexity*, author manuscript:
   https://pure.port.ac.uk/ws/files/15622011/Nemhauser_Trotter_Theorem_post_print.pdf
   Its nonnegative-weight formulation and Lemma 1 retain zero-weight vertices
   explicitly. This is corroboration, not a new calculation for the CR source.

Only primary publisher/author sources support the claims above. Search result
index dates were not treated as publication dates. The 2008 paper's recent
repository crawl/upload date does not make the mathematical result recent.

## Remaining obligations owned by root

Run the authored small exact reference under the separately recorded new-unit
budget; compare production outputs and explicit primal/dual certificates;
bind original source atoms and the same-state consumer; verify the actual
saved output and plot if claimed; record execution and publication separately.
The present author has made no runtime-PASS, native-data or completed-code claim.
