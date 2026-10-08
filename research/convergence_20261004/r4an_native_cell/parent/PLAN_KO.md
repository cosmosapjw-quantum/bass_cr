# R4AM bounded implementation plan

Scope: atomic producer only. Finish a reference validated weak-K cross integrand and integration-remainder provider before any actual candidate quadrature. No R4AH prepare, old suites, central S/M9/R8 or old radial integrals.

1. Recover R4AL inputs and exact Gaussian interval primitives. Freeze provenance, sources and assumptions.
2. Derive azimuthal moments up to degree four; include weak gradient, Coulomb and time/ETF terms without enforcing numerical Hermiticity.
3. Replace the two first-panel origin regions by exact radial-difference charts. Keep regular shell triangles, prove coverage and complex pole checks.
4. Write focused tests before implementation for new key behaviors; then independent Cartesian/angular and manufactured-integral fixtures, failure and scope tests.
5. Implement a pure Python outward-interval reference integrator, explicit Gaussian remainder, finite evaluation budget and fail-closed output. Actual source integration cap zero here.
6. Check actual candidate chart/topology bounds only, no matrix elements; update scoped state and DB without global promotions.
7. Package source, new tests, input identities, evidence, next runtime contract, read-only verifier and publication patch. Publish/dual-backup if exposed tools permit, record exact coverage.

Done means theory and fixture-checked reference software, not a sharp actual K error, not native production speed, and not full physical bridge closure.
