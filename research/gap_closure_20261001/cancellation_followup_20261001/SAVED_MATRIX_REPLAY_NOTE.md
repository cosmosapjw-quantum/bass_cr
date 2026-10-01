# Saved-matrix parity audit

The new cancellation factorization was evaluated on six recovered, hash-verified
original-model static snapshots. This performed zero new physical operator queries
and zero physical propagations. Both comparison paths used the explicit Hermitian
parts of the saved S and H; each projection size is recorded in JSON. D was unchanged.
Sdot was set to D+D† solely for the algebraic comparison. This does not validate G02.

The independent original path forms Qdot+A†Q+QA and solves its generalized
Hermitian eigenproblem. The new path takes singular values of the 13-by-5
selected/complement residual. Maximum relative rho discrepancy is
7.221467647696728e-16. These FP64 matches validate formula implementation on saved inputs; they are
not outward numerical enclosures, a continuous bound, or a state-dependent test.
The original snapshots belong to the archived model, whereas the analytic 504.54
bridge majorant belongs to the separately defined repaired H1 reference.

The first wrapper call omitted the newly explicit keyword-only hbar parameter;
it failed before any matrix calculation. The failure is retained, the wrapper now
passes hbar=1.0, and the complete replay passed. No tolerance was relaxed.
