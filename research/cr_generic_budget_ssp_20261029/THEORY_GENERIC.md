# CR_GENERIC_BUDGET_SSP_V1: exact finite cross-bin budget frontier

**Authority / scope.** This is a finite, fractional event-allocation theorem and a small-instance exact algorithm. No physical exclusive He event kernel, measured energy cap, source-to-rate normalization, photon feedback, donor energy or stopping law is inferred. Parent is `cosmosapjw-quantum/bass_cr` PR120, HEAD `5a8e4ac85a19151a3f9625c91d8e87b38f7a32e7`. Parent source-specific K=3 eV result remains unchanged.

## Definitions

Fix a nonnegative energy cutoff K in eV. For each atom i specify an exact rational energy E_i>=0 in eV, marginal mass w_i>=0 in m^-3 s^-2 and birth-bin b_i. Low atoms satisfy 2E_i<=K and high atoms 2E_i>K. Let G=(H,L,A) be the bipartite graph with admissible edges A={(h,l):E_h+E_l<=K}. For each edge define chi_hl=1 if b_h != b_l, otherwise 0. Marginal constraints are sum_l x_hl<=w_h, sum_h x_hl<=w_l and x>=0. Define m=sum_A x_hl, C=sum_A chi_hl x_hl and M(c)=max m subject to C<=c, c>=0. All m,C,c,w have units m^-3 s^-2. Low-low diagonal loops consume twice their event mass, are always admissible, and incur zero cross-bin budget.

## Theorem 1: exact reduction to a parametric min-cost flow

For 0<=m<=M_infty, define C_min(m)=min{sum_A chi_hl x_hl : x>=0, vertex capacities, sum_A x_hl=m}. Then

M(c)=max{m in [0,M_infty] : C_min(m)<=c},

d_max(c)=(L_total+M(c))/2, with L_total=sum_l w_l.

**Proof.** The first equality follows by projection of the feasible high-low flow polytope. For the second, if y_ll' denotes low-low event mass, low marginal conservation gives m+2 sum y<=L_total, so d=m+sum y<=(L_total+m)/2. Given any maximizing high-low x, allocate every remaining low marginal r_l to a diagonal event y_ll=r_l/2. All original marginals are preserved, cross-bin budget is unchanged and the bound is attained. High residual marginals remain singles. QED.

The fixed-m minimum cost problem is a standard min-cost flow on s->H->L->t with source/high capacities w_h, high/low capacities min(w_h,w_l), low/sink capacities w_l, and integer costs chi on high-low arcs (all other forward costs 0). Reverse residual arcs have negative integer costs. Rational capacities imply exact rational flows.

## Theorem 2: convexity, slopes, primal and dual certificates

C_min(m) is continuous, nondecreasing, convex and piecewise linear on [0,M_infty]. Convexity follows from taking convex combinations of feasible flows with fixed values m1,m2; continuity follows from the finite LP and fractional feasibility. Nondecreasing follows from scaling a feasible higher-m flow down to any lower m. The exact successive-shortest-augmenting-path algorithm starts at m=0 and maintains a minimum-cost flow at each attained m. Its residual shortest s-t path cost k is the right derivative of C_min, and successive k values are nondecreasing. Because all arc costs are integers in {0,+1,-1}, every k is an integer >=0. Each augmentation of rational bottleneck delta yields a linear segment of slope k; convex interpolation of its two endpoint flows supplies a rational witness at any intermediate m. Therefore M(c) is continuous, nondecreasing, concave and piecewise linear with positive-segment slopes 1/k for positive integers k. The c=0 value may already be positive due to zero-cost same-bin flow.

For every c the exact LP dual is

min_{p_h,p_l,lambda>=0} [sum_h w_h p_h + sum_l w_l p_l + c lambda]
subject to p_h+p_l+lambda chi_hl>=1 for every admissible high-low edge, **including zero-mass atoms**. Equality of the dual objective with the constructed M(c) certifies the entire budgeted primal optimum. On an open frontier segment of slope 1/k, lambda=1/k is a supporting dual multiplier; the vertex prices depend on the actual instance. The finite SymPy dual in `generic_budget_flow.py` is a separate mathematical formulation from the SSP primal, though both use Python; independent Wolfram LP and all-event LP controls are retained.

## Sharpness of the old outer bound

For any x, write m=m_same+m_cross. Then m_same<=S, m_cross<=C<=c, and m<=M_infty, giving the necessary bound M(c)<=min(S+c,M_infty). Equality is **not** generic. The 4-atom example in PR119 has M(c)=1+c/2 for 0<=c<=2. The present 10-atom fixture at K=10 has high (energy,mass,bin) entries (19/2,1/2,1), (7,2,0), (9,2,1), (13/2,5/2,2), (6,1/2,1), and low entries (0,1,0), (7/2,1,1), (3/2,5/2,2), (0,5/2,0), (3/2,1/2,2). Exact SSP and independent Wolfram 18-edge LP give

M(c)=5+c for 0<=c<=3/2;
M(c)=13/2+(c-3/2)/2 for 3/2<=c<=5/2;
M(c)=7+(c-5/2)/3 for 5/2<=c<=4;
M(c)=15/2 for c>=4.

The slopes are 1,1/2,1/3,0. At c=5/2 the outer bound is 15/2 while exact M=7, a strict gap 1/2; the corresponding d_max gap is 1/4. This is a finite synthetic counterexample, **not** a measured He event distribution. Wolfram exact rational LP verified c={0,1,3/2,2,5/2,3,4} and values {5,6,13/2,27/4,7,43/6,15/2}. The independent full-event LP including low-low pairs and diagonals matches at c=2,3. Another independent Wolfram six-edge LP verified six points on the PR119 four-atom example.

## Complexity and scope

The current exact reference uses Bellman-Ford on the residual graph, O(A*V*E) arithmetic operations for A augmentations, and retains every endpoint flow snapshot. It caps input to 14 atoms and 100 high-low edges. Its dual uses exact SymPy simplex. The number of parametric breakpoints/augmentations can be large; this is not a claim of polynomial-time scaling in the numerical input size or a native 3201-atom replacement. The **source-specific** K3 native `native_budget.py` has already been run against the original PR116 NPZ separately and is preserved as the fast certified special case. A production generic engine requires a scalable cost-scaling/potentials implementation, original-atom certificates, performance profiling and a separate physical source binding.

## Literature lineage

- Kapoor & Sarwat, *The Budgeted Transportation Problem* (2013), https://arxiv.org/abs/1302.5871 : related LP/primal-dual optimization; its sink-budget constraints are not identical to our one global cross-bin budget.
- Joachims, Klimm & Warode, *Approximate Parametric Computation of Minimum-Cost Flows with Convex Costs* (2022), https://arxiv.org/abs/2203.13146 : background on parametric flow; the present discrete linear-cost SSP is simpler.
- Switzer & Hirata, *Primordial helium recombination I* (2008), https://doi.org/10.1103/PhysRevD.77.083006 : physical line transfer/feedback that cannot be inferred from matching capacities.

No novelty claim is made for general LP duality, SSP or classical min-cost flow. The source-specific application and explicit examples are the new project construction.