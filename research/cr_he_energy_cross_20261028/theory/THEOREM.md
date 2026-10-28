# Exact cross-bin envelope with an atomwise energy cap

## Problem and result

For finite atoms i with exact nonnegative energy E_i and divisible coefficient mass w_i, partition b_i, and a nonnegative cap K, put an edge {i,j} precisely when b_i != b_j and E_i+E_j <= K. Let N=sum_i w_i. A cross event of mass x_ij consumes x_ij at both ends. Residual legs remain singles. The requested coefficient is C=sum_edges x_ij, with incidence(x)_i <= w_i.

For every independent vertex set I let Gamma(I) be its open neighborhood and let w(A)=sum_(i in A) w_i. Then

    Delta(K) = max_(I independent) [w(I)-w(Gamma(I))] >= 0,
    Cmax(K) = (N-Delta(K))/2.

The empty independent set is included. Both endpoints and every C in [0,Cmax] are attainable in this finite divisible-measure family. All conditions on an actual physical joint source remain separately input-gated.

## 1. General fractional matching identity

The primal maximizes sum x_ij under nonnegative edge masses and vertex capacities. Its finite LP dual minimizes sum w_i y_i with y_i>=0 and y_i+y_j>=1 for every edge. An optimum may be chosen in {0,1/2,1}: clip y at 1, take an extreme optimum in the resulting compact polytope, and examine tight-edge connected components among strictly fractional coordinates. On a bipartite such component, opposite signed small perturbations preserve every tight edge and remain feasible, contradicting extremality. A nonbipartite component contains an odd cycle and all its tight coordinates equal 1/2. Thus every fractional coordinate is 1/2.

Given any independent I, labels 0 on I, 1 on Gamma(I), 1/2 elsewhere form a feasible dual of cost [N-w(I)+w(Gamma(I))]/2. Conversely, take a half-integral optimum and I={y=0}. All neighbors of I have label 1. Any label-1 vertex outside Gamma(I) may be changed to 1/2 while preserving all edges; the nonnegative objective cannot increase. This yields the identity above by finite LP duality. Zero-weight vertices and the empty graph are included. This is an application of established fractional matching/vertex-cover theory, not a novelty claim about that general theory.

## 2. Two energy thresholds suffice for this graph

For any nonempty independent I choose an atom of globally minimum energy e and let its partition be r. If I has an atom outside r, let h be the minimum energy outside r; otherwise write h=infinity. Necessarily h>=e and e+h>K whenever h is finite. Consequently 2h>K.

Enlarge I to

    I*(r,e,h) = {i:b_i=r,E_i>=e} union {i:b_i!=r,E_i>=h}.

Its members in r do not share edges. Members outside r have pair sums at least 2h>K, and cross pairs with r have sums at least e+h>K. It remains independent. Furthermore

    Gamma(I*) = {i:b_i!=r,E_i<=K-e} union {i:b_i=r,E_i<=K-h}
              = Gamma(I).

The original minimum e attains the first neighborhood, and the original minimum h, when present, attains the second. Added vertices do not create new neighbors: their energies are higher than these minima. Hence w(I*)-w(Gamma(I*)) >= w(I)-w(Gamma(I)). No assumption of uniform weights is used.

Define inclusive tails T_r(z)=sum_(b_i=r,E_i>=z) w_i, inclusive prefixes P_r(z)=sum_(b_i=r,E_i<=z) w_i, and corresponding outside-partition functions. Then

    F_r(e) = T_r(e) - P_not_r(K-e),
    G_r(h) = T_not_r(h) - P_r(K-h),
    Delta = max(0, max_(r,e) { F_r(e) + max_(h>=e,h>K-e) G_r(h) }).

Here e ranges over complete energy levels present in partition r, h over complete energy levels outside r and infinity; G_r(infinity)=0. The h>=e inequality is inclusive while h>K-e is strict. Keeping complete tied-energy levels is essential.

Sort energies, precompute exact prefix sums and suffix maxima of G_r. A binary search for each e selects the admissible suffix using max(bisect_left(h,e),bisect_right(h,K-e)). For k partitions, this uses O(k n log n) comparisons/arithmetic operations and O(n) working storage per partition. Rational bit costs are not constant. Arbitrary forbidden bin-edge masks are outside this specialization.

## 3. Constructive attainment through a compressed flow

Create left and right copies of each atom, with source-to-left and right-to-sink capacities w_i. Include a left-to-right edge with a capacity exceeding N for every allowed original edge in each orientation. Every feasible original edge mass x induces both directed flows of size x, so maxflow F>=2 Cmax. Conversely any directed flow f gives x_ij=(f_ij+f_ji)/2. Its incidence at atom i is half of its outgoing plus incoming flows and is at most w_i. Thus C=F/2 and F<=2 Cmax. Equality follows constructively.

For each right partition sort atoms by energy and replace all eligible prefix connections by a descending prefix chain. Left i enters that chain at the last energy <=K-E_i; each chain node has its own atom capacity to the sink and an unlimited edge to the previous prefix node. A flow enters only an eligible prefix. Descending FIFO decomposition recovers its original left-to-right atomic pairs. This exactly represents the dense bipartite graph with O(k n) edges, without assuming constant maxflow runtime. Rational capacities are scaled to exact integers using their common denominator. A returned primal witness and the independently calculated dual must have equal exact objectives.

## 4. Intermediate values, limiting cases, and physical return

Scale every maximum cross-event mass by lambda=C/Cmax and replace unused atom legs with singles. If Cmax=0, use all singles directly. This constructs every C in the interval. Same-bin doubles can alter total internal d without changing C; this work does not compute the joint fixed-d feasible boundary.

Increasing K only adds edges, so Cmax is nondecreasing and changes only at cross-bin pair-energy sums. Diagonal thresholds 2E_i alone do not add a cross edge. At large K the complete multipartite graph is recovered: Delta=max(0,2 max_r N_r-N), and Cmax=min(N/2,N-max_r N_r), the PR112 envelope. A single populated partition gives Cmax=0. A three-partition unit-weight triangle has Cmax=3/2, attained by three half-mass events; an integer matching would be the wrong problem.

The source coefficient has units m^-3 s^-2. For q_i(t)=t A_i, multiply by W(a,b)=(b^2-a^2)/2 exactly once to obtain densities on the declared proper interval. Relative to separately summed birth-bin source returns, the union correction for He4I/He4II/He4III is W(C,0,-C), ionic charge correction is -2WC, and chemical-reference correction is -(24.59+54.42)WC eV m^-3. Electron count, selected kinetic energy, RR and retained-photon corrections are zero. Divide by explicit same-state nb=8750/47 m^-3 for native species correction. This conditional chemical correction is not a heating or projectile-debit measurement.

The native consumer retains its neutral-inventory, state, history, support, clock, frame, normalization and replay checks. Endpoint acceptance is checked on the actual declared source/window. Actual K, exclusive joint law, C and D, outside-partner response, donor work, EOS/T and full-source physical native25 remain null.
