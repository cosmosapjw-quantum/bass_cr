# FND TP1 Short-Window Metric Transport Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a capture-free short-window time-dependent transport layer for the validated 18-channel finite-FEM full \(S,H,D\) operator on \(z=-12\to-10\,a_0\).

**Architecture:** The implementation adds a new sidecar under `research/foundation_rebuild/tp1_short_transport_20260926/` without modifying the validated full-operator or cross-integration sources. A shared instantaneous-operator provider feeds two independent transport routes: a direct generalized ODE reference and a Cholesky metric-frame fixed-step candidate. Development tests use small FEM bases; the expensive 18-channel confirmatory run is executed only by the create-only TP1 runner.

**Tech Stack:** Python 3, NumPy, SciPy (`solve_ivp`, dense linear algebra, `expm`), pytest, existing `bass_foundations`, validated `full_operator_20260926`, and `reaudit_20260925/repair/aligned_cross.py`.

## Global Constraints

- Canonical work unit: `FND_TP1_SHORT_WINDOW_METRIC_TRANSPORT_V1`.
- Physical scope: nonrelativistic fixed-target one-electron proton–hydrogen model, 100 keV/u, \(b=2a_0\), \(z=-12\to-10a_0\).
- Basis: the same 18-channel FEM basis used by the accepted full-static operator:
  radius 64, 40 elements, degree 4, \(l_{\max}=1\), bound \(n_{\max}=2\), one positive pseudostate per \(l\), positive-energy ceiling 2 Eh, radial FEM quadrature order 12, grading 2.
- Initial state: target-centered 1s identified from channel metadata and normalized in the actual initial metric.
- Upstream full-operator authority: commit `0e916c16a4da09f0122317b8c793f7e75cd1b118`.
- TT/PP use each center's full support; TP/PT use the validated support-intersection quadrature.
- A saved \(z=-12\) cross matrix may not be reused at later times.
- No operator interpolation in TP1.
- No mode removal, basis reordering, energy fitting, Coulomb softening, tapering, or post-hoc matrix symmetrization.
- Reference route: direct generalized ODE \(\dot c=-iS^{-1}Hc-S^{-1}Dc\).
- Candidate route: Cholesky metric-frame transport derived from the same \(S,H,D\), not copied blindly from AOCC.
- Candidate fixed-step ladder: 8, 16, 32, 64 steps.
- Diagnostic geometry: \(z=-12,-11,-10a_0\).
- Frozen metric finite-difference displacement: \(\epsilon_z=10^{-4}a_0\), converted to \(\epsilon_t=\epsilon_z/v\). This is fixed before the confirmatory run; no epsilon tuning is allowed within TP1.
- Reference solver recommendation, frozen for the implementation plan: SciPy `solve_ivp(method="DOP853", rtol=1e-10, atol=1e-12)`. These are solver controls, not physics error budgets.
- Confirmatory cross quadrature order: 24 with the existing Bessel angular integration.
- Same-center quadrature order: 20.
- Registered TP1 screens:
  - \(S,H\) Hermiticity relative defect \(\le10^{-11}\).
  - metric min/max eigenvalue ratio \(\ge10^{-8}\).
  - relative \(\|\dot S_{\rm FD}-(D+D^\dagger)\|/\max(\|\dot S_{\rm FD}\|,\|D+D^\dagger\|,10^{-300})\le10^{-6}\).
  - reference weighted-norm maximum drift \(\le10^{-8}\).
  - candidate weighted-norm maximum drift \(\le10^{-8}\).
  - phase-aligned candidate/reference final \(S_f\)-distance \(\le10^{-6}\).
  - phase-aligned 32→64 candidate final \(S_f\)-distance \(\le10^{-6}\).
- First failure is preserved. No automatic retry, no tolerance change, no interval shrinking.
- No capture observable, GPU run, full collision, b-grid, all-bound claim, production admission, or historical ~3% discrepancy claim.
- Even on success: `capture_execution_allowed=false`, `production_admission=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `original_capture_gap_resolved=false`.
- Existing successful static cross ladders and historical suites are not rerun unless a changed dependency invalidates their identity.

---

### Task 1: Instantaneous operator provider and metric-connection diagnostics

**Files:**
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/CONTRACT.json`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/operator_provider.py`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/tests/test_operator_provider.py`
- Consume unchanged: `research/foundation_rebuild/full_operator_20260926/full_operator.py`
- Consume unchanged: `research/foundation_rebuild/reaudit_20260925/repair/aligned_cross.py`

**Interfaces:**
- Consumes: `assemble_full(trajectory, channels, t, same_order=20, cross_order=24)`, `compute_cross_snapshot(...)`, `Trajectory`, ordered channel records.
- Produces:
  - `OperatorProvider(trajectory, channels, *, same_order=20, cross_order=24)`
  - `OperatorSnapshot(t, S, H, D, diagnostics, identity)`
  - `OperatorProvider.at(t) -> OperatorSnapshot`
  - `metric_derivative_residual(provider, t, epsilon_t) -> dict`
  - exact-time in-memory cache keyed by binary float time plus frozen provider identity.

- [ ] **Step 1: Add the focused failing tests**

Create small-basis tests that require:
1. repeated `provider.at(t)` returns matrices equal to the first evaluation and increments no second physical operator evaluation;
2. two distinct times do not alias in the cache;
3. each snapshot exposes raw, unsymmetrized `S,H,D`, passes shape/finiteness checks, and carries ordered channel identities;
4. `metric_derivative_residual` evaluates \(S(t\pm\epsilon_t)\) independently and checks `Sdot_fd` against `D+D†`;
5. source identity mismatch or channel reorder is rejected rather than silently rebound;
6. no API exposes capture probabilities.

- [ ] **Step 2: Verify the relevant RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  research/foundation_rebuild/tp1_short_transport_20260926/tests/test_operator_provider.py
```

Expected: collection/import failure for missing `operator_provider`, proving the behavior is not yet implemented.

- [ ] **Step 3: Implement the minimum provider**

Implementation rules:
- instantiate no GPU objects;
- call the existing full-operator APIs without modifying upstream files;
- compute fresh cross blocks for each new time;
- never reuse the saved \(z=-12\) cross archive for \(t\ne t_i\);
- cache only exact repeated `float(t)` values;
- calculate and store raw Hermiticity defects and metric eigenvalue ratio;
- reject a node immediately if the registered static operator screens fail;
- `metric_derivative_residual` must use the frozen \(\epsilon_z=10^{-4}a_0\) converted by the existing projectile speed.

- [ ] **Step 4: Verify the focused GREEN**

Run the identical focused command.

Expected: all provider tests pass with no skips.

- [ ] **Step 5: Run the affected integration check**

Run provider tests together with the existing full-operator package tests:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  research/foundation_rebuild/tp1_short_transport_20260926/tests/test_operator_provider.py \
  research/foundation_rebuild/full_operator_20260926/tests
```

Expected: all selected tests pass; no historical suite is invoked.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add research/foundation_rebuild/tp1_short_transport_20260926/CONTRACT.json \
        research/foundation_rebuild/tp1_short_transport_20260926/operator_provider.py \
        research/foundation_rebuild/tp1_short_transport_20260926/tests/test_operator_provider.py
git commit -m "feat(fnd-tp1): add instantaneous operator provider"
```

---

### Task 2: Independent direct generalized-ODE reference

**Files:**
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/reference_transport.py`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/tests/test_reference_transport.py`
- Consume: `research/foundation_rebuild/tp1_short_transport_20260926/operator_provider.py`

**Interfaces:**
- Produces:
  - `find_target_1s(channels) -> int`
  - `normalize_metric_state(c, S) -> ndarray`
  - `generalized_rhs(t, c, provider) -> ndarray`
  - `run_reference(provider, channels, t0, tf, *, rtol=1e-10, atol=1e-12) -> ReferenceResult`
- `ReferenceResult` records solver method, tolerances, nfev, requested sample states, initial/final states, weighted-norm history, and maximum norm drift.

- [ ] **Step 1: Add the focused failing tests**

Use a toy moving nonorthogonal two-state system with analytic or independently high-precision evolution to require:
1. target-1s identification uses metadata rather than a hard-coded index;
2. metric normalization gives \(c^\dagger Sc=1\);
3. `generalized_rhs` matches a direct `np.linalg.solve(S, -1j*H@c-D@c)` calculation;
4. the reference route preserves weighted norm for an exactly metric-compatible toy problem;
5. a singular/non-positive metric from the provider is refused upstream rather than regularized;
6. the reference result contains no capture/survival observable.

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  research/foundation_rebuild/tp1_short_transport_20260926/tests/test_reference_transport.py
```

Expected: missing module/interface failure.

- [ ] **Step 3: Implement the minimum reference solver**

- Use `solve_ivp(method="DOP853", rtol=1e-10, atol=1e-12)`.
- Solve `S x = (-1j*H-D)c` with `scipy.linalg.solve(..., assume_a="her")` only after the provider has passed the metric/Hermiticity screens; do not explicitly form `S^{-1}`.
- Request a deterministic norm-audit output grid containing at least the endpoints and the three diagnostic geometries.
- Treat solver failure or nonfinite state as `REFERENCE_TRANSPORT_FAILED`.
- Do not automatically retry with another solver or relaxed tolerances.

- [ ] **Step 4: Verify GREEN**

Run the identical focused command.

Expected: all reference tests pass with no skips.

- [ ] **Step 5: Run affected integration checks**

Run Task 1 + Task 2 tests.

Expected: all pass; exact-time provider cache is exercised by the ODE tests.

- [ ] **Step 6: Commit**

```bash
git add research/foundation_rebuild/tp1_short_transport_20260926/reference_transport.py \
        research/foundation_rebuild/tp1_short_transport_20260926/tests/test_reference_transport.py
git commit -m "feat(fnd-tp1): add generalized ODE reference"
```

---

### Task 3: Cholesky metric-frame candidate and temporal refinement

**Files:**
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/metric_transport.py`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/tests/test_metric_transport.py`
- Consume: Task 1 provider and Task 2 normalization/comparison helpers.

**Interfaces:**
- Produces:
  - `metric_frame_generator(snapshot) -> MetricGenerator`
  - `candidate_step(provider, y, ta, tb) -> ndarray`
  - `run_candidate(provider, c0, t0, tf, nstep) -> CandidateResult`
  - `phase_aligned_metric_distance(a, b, S) -> float`
- `MetricGenerator` records `R`, transformed `Ht`, `Dt`, `W=Dt+Dt†`, upper-triangular `X`, raw `G=X-Dt-1j*Ht`, and the raw skew-Hermitian defect.

**Derivation to implement:**

For `S = R† R`, `y = R c`,

\[
\dot y = G y,\qquad
G=X-\widetilde D-i\widetilde H,
\]

with

\[
\widetilde H=R^{-\dagger}HR^{-1},\qquad
\widetilde D=R^{-\dagger}DR^{-1},
\]

and

\[
W=\widetilde D+\widetilde D^\dagger.
\]

For the upper-triangular Cholesky derivative convention,

\[
X_{ij}=
\begin{cases}
W_{ij},&i<j,\\
\frac12\operatorname{Re}W_{ii},&i=j,\\
0,&i>j.
\end{cases}
\]

Then \(X+X^\dagger=W\), so exact compatible inputs make \(G+G^\dagger=0\).

- [ ] **Step 1: Add focused failing tests**

Tests must require:
1. `X+X†` reproduces `W` on compatible toy data;
2. raw `G+G†` is tiny without projecting/symmetrizing `G`;
3. midpoint `expm(dt*G_mid)` reproduces an exactly solvable constant-generator system;
4. a time-dependent analytic metric toy problem agrees with the direct generalized reference under step refinement;
5. phase alignment removes only a single global phase and uses the final `S` metric;
6. deliberate omission/sign reversal of `D` fails the reference comparison or metric identity;
7. candidate outputs contain no capture observable.

- [ ] **Step 2: Verify RED**

Run the focused metric transport test file.

Expected: missing implementation failure.

- [ ] **Step 3: Implement minimum candidate**

- At every fixed step use the midpoint operator.
- Construct the raw `G` above.
- Record its skew-Hermitian defect before propagation.
- Propagate with `scipy.linalg.expm(dt*G)`; do not project `G` onto its skew-Hermitian part.
- Convert `c0` to `y0=R(t0)c0`.
- At final time recover `c=R(tf)^{-1}y`.
- Run only preregistered step counts 8,16,32,64.
- Record weighted-norm history and consecutive phase-aligned final-state distances.

- [ ] **Step 4: Verify GREEN**

Run the identical focused command.

Expected: all candidate tests pass.

- [ ] **Step 5: Run the complete new TP1 unit-test set**

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -p no:cacheprovider \
  research/foundation_rebuild/tp1_short_transport_20260926/tests
```

Expected: all new TP1 tests pass with zero skips.

- [ ] **Step 6: Commit**

```bash
git add research/foundation_rebuild/tp1_short_transport_20260926/metric_transport.py \
        research/foundation_rebuild/tp1_short_transport_20260926/tests/test_metric_transport.py
git commit -m "feat(fnd-tp1): add metric-frame transport candidate"
```

---

### Task 4: Confirmatory TP1 runner, claim gates, and durable return

**Files:**
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/run_tp1.py`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/tests/test_runner_contract.py`
- Create: `research/foundation_rebuild/tp1_short_transport_20260926/README_KO.md`
- Create after successful local execution: `research/foundation_rebuild/tp1_short_transport_20260926/VALIDATION_EVIDENCE.json`
- Reference approved design: `docs/specs/2026-09-26-fnd-tp1-short-window-metric-transport-design.md`

**Interfaces:**
- CLI:
  - `--out <fresh-directory>` required.
  - `--expected-commit <sha>` optional but used in canonical local confirmation.
  - no flag may enable capture, change the interval, alter tolerances, alter the step ladder, or enable GPU.
- Produces the durable output set defined by the approved design.

- [ ] **Step 1: Add runner contract tests**

Test:
1. an existing output path is rejected without overwrite;
2. wrong repository HEAD is `IDENTITY_OR_INPUT_BLOCKED`;
3. source/dependency hash mismatch blocks before scientific execution;
4. all fixed physics/numerical parameters in `CONTRACT.json` are reflected in `INTAKE.json`;
5. first failure produces a return report and ZIP with the correct failure phase;
6. success cannot set `capture_execution_allowed=true`;
7. no CLI option exists for capture/GPU/tolerance relaxation;
8. a mocked confirmatory sequence proves status precedence for operator, metric, reference, candidate, and refinement failures.

- [ ] **Step 2: Verify RED**

Run the focused runner-contract test.

Expected: missing runner failure.

- [ ] **Step 3: Implement runner and documentation**

Execution order:
1. source and commit identity;
2. create-only intake;
3. new TP1 unit tests;
4. operator diagnostics at z=-12,-11,-10;
5. metric derivative diagnostics with fixed \(\epsilon_z=10^{-4}a_0\);
6. direct reference run;
7. candidate runs 8,16,32,64;
8. evaluate preregistered screens;
9. write `RETURN_REPORT.json`, `MANIFEST.json`, and return ZIP;
10. stop with no capture action.

The runner must emit progress records because full cross evaluations are expensive, but progress output cannot alter the computation.

- [ ] **Step 4: Verify runner contract GREEN and full new test suite**

Run runner-contract test and then all TP1 tests.

Expected: all pass with zero skips.

- [ ] **Step 5: Execute exactly one 18-channel confirmatory TP1 run locally**

Canonical command:

```bash
BASE="research/foundation_rebuild/tp1_short_transport_20260926"
OUT_TP1="runs/fnd_tp1_short_transport_$(date -u +%Y%m%dT%H%M%SZ)"

OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 "$BASE/run_tp1.py" \
  --out "$OUT_TP1" \
  --expected-commit "$(git rev-parse HEAD)"
```

Expected success status:

`TP1_SHORT_TRANSPORT_PASS`

On any other status, preserve the first failure and stop. Do not immediately add a new numerical fix in the same confirmatory run.

- [ ] **Step 6: Verify and commit only supported evidence**

If and only if the confirmatory run passes:
- copy a bounded summary, not the full run directory, into `VALIDATION_EVIDENCE.json`;
- include exact return-report SHA256, environment versions, operator evaluation count, solver `nfev`, norm drifts, metric-connection residuals, candidate/reference distance, 32→64 distance, and explicit unchanged HOLD/OPEN/NO_GO claims.

Commit:

```bash
git add research/foundation_rebuild/tp1_short_transport_20260926 \
        docs/specs/2026-09-26-fnd-tp1-short-window-metric-transport-design.md
git commit -m "research(fnd-tp1): validate short-window metric transport"
```

If the confirmatory run fails, commit the implementation/tests and a failure receipt only if preserving the failure is desired; do not write a PASS evidence file.

## Externally Observable Decisions

All externally observable decisions required for implementation are fixed by the approved design and this plan:
- create-only outputs;
- no retry;
- no capture or GPU path;
- fixed interval and basis;
- fixed reference solver and tolerances;
- fixed finite-difference displacement;
- fixed candidate step ladder;
- fixed success screens and status names;
- failure artifacts are preserved;
- success still leaves `HOLD / OPEN / NO_GO`.

There are no unresolved product decisions required to begin implementation.