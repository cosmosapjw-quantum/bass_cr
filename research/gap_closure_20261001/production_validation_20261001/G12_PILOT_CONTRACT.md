# R4V bounded independent-family physical pilot

This is an additive cache-only analyzer and exact query planner. No code in this
module calls the physical evaluator or starts the operator producer. The root
workflow must review the G02/G03 return and bind fresh qualified query execution
before supplying caches. Model routing is unavailable and is not inferred.

## Frozen scientific scope

- Archived 18-channel B0, 100 keV/u, b=2 a0, charges1/1.
- z=32 to32.02 a0, z=v t with the existing speed conversion.
- Initial e0 normalized exactly once using the shared qualified initial S.
  This is a numerical test state, not an incoming collision/tail state.
- Exact unmodified qualification ladder/screens, same-center order20, FP64.
- Direct coefficient equation cdot=solve(S,(-iH-D)c), DOP853 rtol5e-13,
  atol5e-15, one accepted step, first_step=max_step=tf-t0.
- Unchanged `candidate_step` Cholesky midpoint recurrence with1,2,4steps.
- Selected span indices9,10,12,13,14; its population is only a finite-span
  diagnostic and is not reported as capture.

The plan has18 exact unique times and13 expected DOP853 RHS evaluations;12 of
those RHS times are unique. Thus the unchanged11-level qualification policy has
198 raw attempts as an upper bound (36 if every first pair qualifies). Query
producer resources and hard timeout are recorded in its separate fresh manifest.
The root may partition complete query ladders using the existing resource-aware
batch producer. It must not split or reorder a single qualification ladder.

## APIs and invocation

`make_plan(inputs,build,backend="fortran",threads=2)` performs only reads,
source/native/input hashing, and exact-time planning. It calls `hp.prepare_context`
and binds the complete physical operator context, the dependency source hashes,
NumPy/Python versions, SciPy1.17.0, all DOP853 tableau arrays, and exact stage-node
array bytes. It does not load a native library. It writes no files by itself.

`ExactUnionCache(directories,plan)` first rebuilds the plan under current source
identities. Each time must resolve to exactly one complete source pair across
all supplied directories. `validate_pair` and `validate_cached_cross_binding`
verify qualification, raw/full binding and source context. Cache hits rehash the
record and payload; a missing or changed pair fails before propagation.

`analyze(plan,cache_directories,out)` is create-only and stores the plan, cache
manifest, common initial vector, final states, numerical comparisons, and first
failure. It returns exit status2 for a completed comparison that fails the local
screens. Exceptions preserve FIRST_FAILURE.json. No result silently expands the
query list, creates native calls, retries a rejected DOP853 step or relaxes
precision/tolerance.

Example (paths are supplied by the root manifest; no execution is implied here):

```bash
python -I g12_pilot.py plan --inputs INPUTS --build BUILD --out PLAN.json --threads 2
python -I g12_pilot.py analyze --plan PLAN.json --plan-sha256 FILE_SHA256 --cache CACHE_LANE_0 --cache CACHE_LANE_1 --out NEW_RESULT_DIRECTORY
```

`--plan-sha256` is the complete plan file byte SHA, distinct from the internal
canonical `plan_sha256`. Exact source identity, runtime and fresh operator-context
admission remain required even when a former context used identical matrix values.

## Local comparison screens

| Quantity | Maximum |
|---|---:|
| Midpoint4 versus DOP853 unaligned final metric-state distance |1e-8|
| Final selected-span population difference |1e-10|
| DOP853 initial/final metric-norm drift |1e-9|
| Midpoint discrete whitened-norm drift |1e-12|
| Method actual initial-state distance to the common state |1e-14|

These are predeclared **local engineering screens**, not mathematically certified
error bounds or replacements for the original production budget. There is no
claim that the state screen entails the stricter population screen; both are
measured separately. For a common metric-orthogonal projector, the population
difference is bounded by the metric state difference times the sum of the two
state norms, but that observation does not certify either method's absolute error.
No threshold is adjusted after inspecting physical output.

Both unaligned and phase-aligned distances are reported; only the unaligned one
is used in the local gate. Midpoint successive differences and their empirical
order are recorded. A100-epsilon floating floor marks order as unresolved when
appropriate rather than promoting roundoff/exactness to a convergence proof.
DOP853's embedded local controller is not a rigorous global error enclosure,
and no dense output is used. Norm sampling for DOP853 is only at both endpoints.

## Derivative and IVP limitations

For S=R†R and y=Rc, the correct whitened generator is
`B=Rdot R^-1-R^-†D R^-1-iR^-†H R^-1`. The frozen midpoint implementation uses
`X=triu(E,1)+diag(real(diag(E))/2)` with E=R^-†(D+D†)R^-1. This agrees with
Rdot R^-1 only when Sdot=D+D†. Its whitened norm conservation is therefore not
independent physical derivative validation. Direct DOP853 integrates the
coefficient ODE without this substitution. A disagreement can reveal time error,
quadrature effects or the derivative mismatch; this pilot alone does not identify
which. Preserve the separate G02 evidence and its limits.

The supplied common initial state is normalized once. The DOP853 actual initial
state must have the same bytes; midpoint maps it to y and reports the inverse-map
roundoff distance. No normalization occurs during either trajectory. Norm drift
must not be removed by rescaling the result.

The original G12 physical contract concerns the authentic incoming state and the
[-12,+12] window. It remains open even when this new local pilot passes. Production
HOLD, all_bound OPEN, b_grid NO_GO and capture false are permanent claim ceilings
of this pilot; no NCP64 or MPI physical-run claim is made.

## Focused tests and primary API source

`test_g12_pilot.py` exercises the exact18-query grid; a known analytic noncommuting
unitary trajectory in a changing nonorthogonal metric; nonunit input normalization;
midpoint refinement; direct DOP853 accuracy; a missing exact cache time; rejection
of an attempted adaptive replacement step; plan/context tampering; duplicate and
absent cache records. These are nonnative tests. No physical query was executed
as part of implementation.

The public complex-valued DOP853 API, `first_step`, `max_step`, `step`, `status`,
`t`, `y` and `nfev` were checked against the official versioned documentation:
https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.DOP853.html
(accessed2026-10-01). Exact stage ordering and byte identity use installed source
and coefficient hashes rather than an assumed documentation-level stage count.
