# FND TP1 Short-Window Metric Transport Design

Date: 2026-09-26

## Purpose

Validate time-dependent transport for the already validated finite 18-channel two-center FEM operator without opening a capture observable, full collision, b-grid, or production admission.

Canonical work unit: `FND_TP1_SHORT_WINDOW_METRIC_TRANSPORT_V1`.

Evolve

\[
i S(t)\dot c(t) = \bigl(H(t)-iD(t)\bigr)c(t)
\]

on a short fixed interval while independently checking metric consistency, weighted norm preservation, generator consistency, and time-step convergence.

## Frozen physical scope

- 100 keV/u, b = 2 a0.
- z: -12 -> -10 a0.
- Initial state: target-centered 1s.
- Same 18-channel FEM basis as the validated full-static step.
- No mode removal, reordering, energy fitting, Coulomb softening, tapering, or post-hoc matrix symmetrization.
- Upstream full-operator commit: `0e916c16a4da09f0122317b8c793f7e75cd1b118`.
- Capture observable remains forbidden.

## Operator evaluation

At every requested t, construct instantaneous S(t), H(t), D(t).

- TT/PP: each center's full support.
- TP/PT: validated support-intersection quadrature.
- Saved z=-12 cross matrices may not be reused at later times.
- Exact-time caching is allowed, interpolation is not.

## Two independent transport routes

### Reference

Direct generalized ODE:

\[
\dot c=-iS^{-1}Hc-S^{-1}Dc.
\]

Use a high-accuracy `solve_ivp` route and solve linear systems with S rather than relying on explicit inversion.

### Candidate

Metric-frame transport with

\[
S=R^\dagger R,\qquad y=Rc.
\]

Propagate in the metric-orthonormal frame with the connection implied by the actual S,H,D convention. The existing AOCC Cholesky pattern may be used as a reference pattern, but its formula must be re-derived for this basis convention rather than copied blindly.

## Required diagnostics

1. Operator validity at all requested nodes:
   - S,H Hermiticity relative defect <= 1e-11.
   - metric eigenvalue ratio >= 1e-8.

2. Metric derivative identity at z = -12,-11,-10:
   \[
   \dot S_{FD}\approx D+D^\dagger.
   \]
   Registered relative residual <= 1e-6.

3. Weighted norm:
   \[
   N=c^\dagger Sc.
   \]
   Maximum absolute drift <= 1e-8 for both reference and candidate.

4. Candidate/reference comparison:
   final global phase removed, then
   \[
   \|c_{cand}-c_{ref}\|_{S_f}\le10^{-6}.
   \]

5. Candidate fixed-step ladder:
   N = 8,16,32,64.
   Primary 32 -> 64 final physical-state distance <= 1e-6.

6. Candidate generator anti-Hermitian/unitarity defect is recorded using the derived metric-frame convention. No symmetrization is allowed to force the screen.

## Initial condition

Locate target 1s by channel metadata. Initialize that channel and normalize in the actual initial metric:

\[
c_0\leftarrow c_0/\sqrt{c_0^\dagger S(t_0)c_0}.
\]

## Execution policy

- Reference and candidate consume the same instantaneous operators.
- A finite-difference epsilon for Sdot is preregistered before the run and held fixed.
- First failure is preserved.
- No automatic retry.
- No tolerance changes after results.
- No interval shrinking after failure.
- No GPU run.
- No capture calculation.

## Explicit exclusions

TP1 does not claim or calculate:
- capture probability,
- all-bound probability,
- ionization probability,
- cross section,
- b integration,
- production rate,
- basis completeness,
- equivalence to historical GPU TDL,
- resolution of the historical ~3% discrepancy.

## Durable outputs

Fresh create-only output directory containing:
- `INTAKE.json`
- source/dependency identity receipt
- operator diagnostic rows
- reference ODE receipt
- candidate results for each step count
- norm diagnostics
- final-state comparison scalars
- `RETURN_REPORT.json`
- `MANIFEST.json`
- `<output>_RETURN.zip`

## Status semantics

Top-level statuses:
- `TP1_SHORT_TRANSPORT_PASS`
- `OPERATOR_TIME_NODE_FAILED`
- `METRIC_CONNECTION_FAILED`
- `REFERENCE_TRANSPORT_FAILED`
- `CANDIDATE_TRANSPORT_FAILED`
- `TEMPORAL_REFINEMENT_FAILED`
- `IDENTITY_OR_INPUT_BLOCKED`
- `ENVIRONMENT_BLOCKED`
- `INTERRUPTED`

Even on PASS:

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
```

## Next gate

Only after TP1 passes may a later design extend the interval. A capture observable requires a separate preregistered work unit.