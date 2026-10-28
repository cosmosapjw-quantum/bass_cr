# R4 — Representation and discriminating constructions

## Why the joint projection is needed

Independent intervals 0<=d<=D and 0<=C<=X discard two couplings. Every cross event is a double, so C<=d. If m is the high-low event mass and r the low-low event mass, d=m+r; under the domain assumption m<=C. The low-leg use is m+2r=2d-m and cannot exceed L. The resulting candidate extra facet is 2d-C<=L. Its sharpness and sufficiency remain R5 obligations.

Use the two-dimensional projection rather than a family of unrelated fixed-d optimizations. The candidate boundary has vertices O=(0,0), A=(L/2,0), B=(D,M), F=(D,X), G=(X,X), retaining coincident vertices by label until the construction handles degeneracies. This representation uses the PR114/115 optima directly and exposes the single missing common-optimum witness F.

## Actual small construction

Take K=3, three distinct bins A,B,H, energies (1/2,1,2), and masses (3,1,1). Low mass L=4. All low-high edges are cross-bin and permitted. High capacity is1, so M=1 and D=5/2. Every cross edge uses at least one leg from B or H, whose total mass is2, so X<=2; edges A-B of mass1 and A-H of mass1 attain X=2.

The five candidate vertices have explicit measures:

| Vertex | Nonzero doubles | Remaining singles |
|---|---|---|
| O=(0,0) | none | A:3, B:1, H:1 |
| A=(2,0) | A-A:3/2, B-B:1/2 | H:1 |
| B=(5/2,1) | A-H:1, A-A:1, B-B:1/2 | none |
| F=(5/2,2) | A-H:1, A-B:1, A-A:1/2 | none |
| G=(2,2) | A-H:1, A-B:1 | A:1 |

Every row has the original atom marginals. Energy support and all masses can be checked directly. The midpoint of any two rows preserves the complete marginal, rather than merely the scalar totals. This is an actual finite construction, not a numerical execution or a proof for all inputs.

## Chosen general route

1. Prove the four facets by leg accounting and the two existing maxima.
2. Select a cross-optimal measure which maximizes its high-low mass lexicographically.
3. If that mass is below M, a residual high-low augmenting path ends at a low atom with unused capacity relative to high-low edges. Split its available mass into singles and low-low cross occupancy.
4. A single endpoint would increase C; replacing a low-low cross edge would preserve C but increase high-low mass. Either contradicts the lexicographic choice.
5. Complete residual low marginals by diagonals and obtain F. Complete the other named vertices directly, then mix vertex measures with exact coefficients.

Compactness justifies the lexicographic maximizer. For rational input, a scaled finite integral-capacity flow formulation gives finite constructive residual augmentation; irrational generality is unnecessary for this contract.

## Alternatives and scope discrimination

A black-box LP for each d would obscure the common-attainment argument and require a numerical acceptance policy. The selected route yields an exact finite certificate and an interpolation algorithm. A generic Python prefix-chain native rerun is also inappropriate after PR115's measured failure; coding will use saved witnesses and a bounded faster backend only where a new explicit primal is missing.

For the same K=2, energies (2/5,7/5), masses (1,1), but equal bins, a high-low double of mass1 has (d,C)=(1,0) and L=1. It violates the candidate facet 2d-C<=L. This is a concrete witness that the unrestricted extension is false, and a future domain-rejection fixture. It is a local scope counterexample, not a new scientific strong no-go.

R5 must close the common-optimum proof, rational finite construction and all degenerate interpolation branches. R7 will independently check the three-atom polygon and this excluded fixture with exact symbolic arithmetic. No new solver or source science has run at R4.
