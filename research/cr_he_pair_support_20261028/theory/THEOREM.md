# Exact conditional pair-support envelope and atomic realization

Unit: CR_PHYS02_HE_PAIR_SUPPORT_V1. Scope and conventions: CONTRACT.json and R03_CLAIMS_KO.md. This is a constructive application of established fractional-matching mathematics, with a source-bound atomic realization and unchanged event-union consumer. It is not a novelty claim for the general matching theorem or an identified physical helium kernel.

## 1. Finite primal and weak dual

Let G=(V,E) be a finite simple undirected graph, n_i>=0, N=sum_i n_i. Define

    P = {x in R^E: x_e>=0, sum_{e incident i} x_e<=n_i},
    rho_G(n) = max_{x in P} sum_e x_e.

The zero vector is feasible. Each x_ij is bounded by min(n_i,n_j), so P is compact, including E empty. An optimum exists. For every y_i>=0 with y_i+y_j>=1 on E,

    sum_e x_e <= sum_{ij in E}(y_i+y_j)x_ij
               = sum_i y_i (Bx)_i <= sum_i n_i y_i.       (1)

This is a directly checkable upper-bound certificate. We construct a matching lower certificate and thereby prove equality, without trusting a floating-point solver status.

## 2. Symmetric bipartite double cover

For N>0 build a directed network with source s, sink t, copies L_i and R_i of every vertex. Put capacities n_i on s->L_i and R_i->t. For each undirected ij in E put both L_i->R_j and L_j->R_i, each of capacity 2N. There are no other forward arcs.

Every x in P gives a flow f_ij=f_ji=x_ij between the copies, with source/terminal arcs equal to the corresponding degrees. Its value is 2 sum_e x_e. Conversely any feasible flow f gives

    x_ij = (f_ij+f_ji)/2.                                (2)

At vertex i its incidence sum is one half of the outgoing flow from L_i plus incoming flow into R_i, hence at most n_i. Also sum_e x_e=F/2, where F is flow value. Thus the maximum flow satisfies F_max=2rho_G(n).

The finite max-flow/min-cut theorem supplies a minimum s-t cut S of capacity F_max. A cut consisting only of s has capacity N. Since 2N>N, no 2N cross arc can cross any minimum cut. Write

    a_i = 1{L_i not in S}, b_i = 1{R_i in S},
    y_i = (a_i+b_i)/2.                                  (3)

For an edge ij, the absence of both crossing cross arcs implies a_i+b_j>=1 and a_j+b_i>=1. Their sum gives y_i+y_j>=1. Moreover

    sum_i n_i y_i = cut_capacity/2 = F_max/2 = rho_G(n).  (4)

Equations(1)-(4) prove primal/dual equality and exhibit an optimal y with coordinates in {0,1/2,1}. Residual reachability after a maximum flow gives S constructively. For N=0 choose x=0 and y_i=1/2; all edges remain dual feasible and both objectives are0. For E empty choose x empty and y=0. Zero-capacity vertices and disconnected components cause no division and need no limiting argument.

For rational input capacities, augmenting along a shortest residual path with exact rational arithmetic is a finite Edmonds–Karp implementation. Its combinatorial termination bound is independent of rational denominators. Returned primal and dual data alone certify the objective through (1), even without trusting this algorithm.

## 3. Exact attainable interval, including fixed internal double mass

Interpret x_ij as unordered cross-double event mass. The set P is convex and contains0. If rho>0, scale an optimal x* by C/rho for any 0<=C<=rho; if rho=0 only C=0 is allowed. The total consumed electron-leg mass is2C, so the residual mass is N-2C>=0. Realize it as singles. Therefore the exact attainable cross-event interval is [0,rho].

Now prescribe a total selected-internal double-event mass d with 0<=d<=N/2. Necessarily C<=d and C<=rho. Conversely take any C in [0,min(d,rho)] and the scaled graph assignment above. The required additional diagonal double mass is d-C; its two legs require2(d-C). The residual marginal has mass N-2C, and

    2(d-C) <= N-2C  iff  2d<=N.                          (5)

Allocate that amount of residual electron marginal to atomic diagonal doubles, each at half its consumed leg weight, and leave the rest as singles. This constructs every such C. No additional lower bound on C appears because diagonal doubles are explicitly allowed. If an application forbids diagonals or imposes atom-specific pair exclusions, (5) alone is insufficient and this theorem's feasible class must be changed.

## 4. Sparse atomic realization

Each bin i contains a finite fixed measure mu_i=sum_{a in A_i} w_a delta_a of mass n_i. Every edge ij allows its full Cartesian rectangle. For a chosen feasible x, keep an ordered residual queue of the atoms of each bin. In a fixed edge order, take a submeasure of mass x_ij from each endpoint's remaining queue. Feasibility Bx<=n ensures that these withdrawals always exist.

Couple the two equal-mass submeasures by matching their first remaining atoms, emitting pair mass equal to the smaller remaining weight, and advancing any exhausted atom. Continue until edge mass x_ij is emitted. All emitted weights are positive, only atoms in the two endpoint bins occur, and each side's marginal equals its withdrawn submeasure. Each matching step exhausts an atom or finishes an edge, so this remains sparse; no dense atom-pair matrix is constructed.

The unordered pair record (a,b) with weight w represents the symmetric ordered measure w(delta_(a,b)+delta_(b,a))/2. Its electron marginal 2*pi_1 D contributes w at each endpoint, including2w at one atom when a=b. Apply the residual diagonal allocation in §3 to individual residual atom weights: consume r legs with a diagonal event weight r/2, then emit any residual as singles. Every original atom therefore has exactly its original marginal. Atom energies, keys, bins and their number are unchanged. The cutoff ghost is kept as its own existing atom.

The queue construction works for arbitrary finite nonnegative real weights as a mathematical construction; the code uses exact rational weights. It proves sharpness for the stated full-rectangle graph class. It does not invent an actual physical joint distribution.

## 5. Complete graph reduction and sensitivity

For a complete graph with at least two bins, every x has sum x<=N/2. Also cross events cannot use more mass from the largest bin than is available outside it, and events wholly outside that bin consume two outside legs. Writing their masses C_touch and C_else gives C_touch+2C_else<=N-n_max, hence C<=N-n_max. Thus rho<=min(N/2,N-n_max).

If n_max>=N/2, pair every outside bin directly with the largest bin: rho=N-n_max. If n_max<=N/2, place the bins consecutively on a circle of circumference N. Pair mass coordinates u and u+N/2, with u in [0,N/2). A bin interval has length at most N/2, so the two coordinates lie in different bins except endpoints of zero measure. This realizes N/2 cross mass. Atomic splitting of endpoint intervals is allowed, so atoms of positive weight cause no obstruction. N=0 is immediate; one bin gives0 by the same formula. This recovers PR112's exact envelope.

Adding allowed edges or increasing capacities enlarges P. For alpha>=0, rho_G(alpha*n)=alpha*rho_G(n), including alpha0. A dual vector can always be clipped above at1 without losing feasibility or increasing its nonnegative objective. Given an optimal dual for m, (1) implies rho(n)<=rho(m)+sum_i|n_i-m_i|; exchanging m,n proves

    |rho_G(n)-rho_G(m)| <= ||n-m||_1.                   (6)

Equation(6) concerns perturbations of the supplied capacities within the same mathematical model. It is not an error bound for an unknown physical exclusive kernel or for atom/source-model identification.

## 6. Proper history, source binding and consumer consequences

Production reads the byte-pinned PHYS02 coefficient measure a_a and uses the pre-existing binding for window [u,v] within [0,10^10] proper seconds. Since W=(v^2-u^2)/2>0, multiplying the witness by W yields the integrated measure. The coefficient-level primal/dual construction commutes with this multiplication by homogeneity. Neither a second target factor nor a source refit is introduced.

An event supported in two different selected birth bins appears in both partition claims but only once in the union. A cross double therefore contributes naive ion change(-2,0,+2), union(-1,0,+1), and correction(+1,0,-1) per event. Scaling by integrated cross mass C gives

    delta_ion_correction = (C,0,-C),
    delta_charge_correction = -2C,
    delta_chemical_correction = -(I1+I2)C,
    delta_selected_electron = delta_selected_kinetic_energy = 0.  (7)

Here I1=24.59eV and I2=54.42eV are reused consumer conventions. Both sides contain exactly the same electron legs and energies. The underlying consumer further verifies baryon conservation, all selected atom marginals, matching source/state/frame/clock/window, explicit same-state nb=8750/47 for native conversion, and no overlapping-time replay. The wrapper adds graph provenance, graph support and feasible C/d checks before calling that unchanged consumer.

Matching feasibility and atomic realization alone do not guarantee admission by the physical-state consumer. The inherited consumer separately requires the constructed integrated parent mass to fit the conditional neutral inventory:

    W*(A_tot-d_coeff) <= (1085/94)*(99/100).              (8)

Here A_tot is the sum of coefficient marginal masses and d_coeff is total internal double-event coefficient. Source identity, allowed proper window and all other consumer gates remain necessary. The retained source will be checked against these gates in actual coding execution; the theorem does not assert admission for every arbitrary formal capacity/window pair. This explicit separation records independent-review finding R6-F1.

Equation(7) is a same-state partial source correction. Use source union OR corrected partition sum once. Saved RR and retained photons have separate once-only ports. This new conditional graph construction supplies no selected-outside partner response, donor work, actual EOS/T, absolute volume or full-source physical native25.

## Evidence classification

T1-T4 are proved constructively above; T5 maps the new witness to the byte-reused PR112 consumer identity; T6 follows from the supplied finite feasible model. R6 is a separate independent proof review. R7 uses a bounded CAS only for discriminating identities/examples, not as the sole proof. Coding acceptance requires actual exact certificates, atomwise checks, independent oracle comparisons and scoped C9 review. No strong no-go claim is proposed.
