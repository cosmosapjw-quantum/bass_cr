# Conservative composition of the current B0 error budget

Use one common observable, basis, physical model, trajectory and time endpoint before composing errors. Introduce a telescoping chain of exact intermediate problems. For example a finite-basis infinite-time exact observable, the same finite-basis problem at the accepted window, the exact evolution using perturbed static operators, its exact time-discrete approximation, and its floating-point evaluation. Each bound must identify the two adjacent objects it connects.

If `|P_i-P_{i+1}|≤ε_i` holds simultaneously and deterministically, then `|P_0-P_m|≤sum ε_i` by the triangle inequality. **Statistical independence is not needed**; correlation does not invalidate this deterministic statement. The actual hazards are unproved error estimates, inconsistent intermediate objects, incompatible units, double-counting, and probabilistic coverage statements that were never made simultaneous. Root-sum-square is not justified without a stochastic model and its covariance/coverage assumptions. Individually valid probabilistic intervals require joint coverage treatment, such as a justified union bound.

For matched whitened variables, let exact `y'=B y` have anti-Hermitian B and approximate trajectory `yhat'=Bhat yhat`. Duhamel gives

\[
\|y(T)-\widehat y(T)\|\le \|y(0)-\widehat y(0)\|
 +\int_0^T\|B-\widehat B\|\,\|\widehat y\|\,dt.
\]

For an orthogonal selected projector E, and an approximate projector Ehat in the **same Euclidean frame**,

\[
|y^\dagger Ey-\widehat y^\dagger\widehat E\widehat y|
\le(\|y\|+\|\widehat y\|)\|y-\widehat y\|
 +\|E-\widehat E\|\|\widehat y\|^2.
\]

The first term assumes `||E||≤1`. This derivation converts genuine generator/projector error bounds into probability units. Before applying it to approximate S,H,D, one must bound metric-factor and inverse sensitivity, establish a common whitening frame and control its derivative. Raw cross-matrix adjacent differences are not a substitute. If exact B is not anti-Hermitian under the chosen approximation/model, a growth-factor bound must replace unitarity.

The eight requested components should therefore be recorded separately: temporal, static_operator, floating_point, window, tail, basis, b_quadrature and model. Keep their classes (`RIGOROUS_BOUND`, `VALIDATED_NUMERICAL_BOUND`, `EMPIRICAL_CONVERGENCE_ESTIMATE`, `SYSTEMATIC_MODEL_UNCERTAINTY`, `UNKNOWN`) and target domains attached. An empirical temporal pair difference is not a certified absolute error even though its existing operational temporal gate remains closed. Static operator uncertainty currently remains UNKNOWN as an absolute bound. Basis/model uncertainty must not disappear into a finite-B0 numerical budget. b-quadrature is not applicable to the single b=2 result and remains unopened for integrated cross sections.

For window closure, a certified tail bound from the accepted Z directly bounds its endpoint-to-infinity difference. A direct nested-window increment is useful evidence, but counting that increment **and** an already enclosing tail bound from the same starting endpoint double-counts the same bridge. Alternatively use the increment to connect Z1 to Z2 plus a certified residual tail from Z2, with independently bounded numerical endpoint errors and matched initial-state conventions. Incoming and outgoing absolute tails must be added without cancellation.

Current B0 has no finite certified total: unknown operator error and unresolved continuous tails prevent it. Conditional formulas and numerical convergence estimates should be reported, but no scalar certified total or relaxed gate follows from the present audit.
