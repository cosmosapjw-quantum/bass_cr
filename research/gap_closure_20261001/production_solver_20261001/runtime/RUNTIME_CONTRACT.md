# Identity-bound midpoint runtime

This implements the second phase of the production-solver integration: execute
the existing finite-model midpoint candidate from a complete qualified operator
cache, with durable step checkpoints and explicit restart. The first phase is
the sibling provider adapter's MPI/operator evaluation. This runtime imports no
native evaluator and has no cache-miss fallback.

## Source-based architecture finding

The previous physical G02/G03 paths construct the frozen C++ MomentKernel
through worker_runtime. The R4S Fortran kernel and MPI queue existed separately.
The old metric_transport.run_candidate executes an entire temporal rung:
normalize c0 once, form y0=R(t0)c0, apply midpoint exponentials, and recover
c(tf)=R(tf)^(-1)y. The previous continue_temporal runner restores an earlier
completed rung/cache and executes a larger rung; it does not restart a partially
completed trajectory.

The new code closes the missing cache-to-stateful-solver integration seam while
leaving the old numerical source unchanged. It does not switch to the separate
synthetic CF4 implementation. It does not change quadrature, spatial screens,
midpoint arithmetic, normalization or the selected-span definition.

## Provider interface

solver_plan.make_plan accepts t0, tf, nstep, a 64-hex context_id, and explicit
qualification_contract and selected_indices. The contract contains the existing
runtime_reference_resolutions and screens, including candidate_norm_drift_max.
The current model is exactly 18 channels because the inherited strong query-pair
validator binds 18-by-18 full and 9-by-9 cross matrices.

The returned plan contains initial/final endpoints and every midpoint, using
exactly the operations in the legacy loop:

    dt = (tf-t0)/nstep
    ta = t0+j*dt
    tb = ta+dt
    tm = 0.5*(ta+tb)

Times use float.hex identity and the existing context/time query hash. The
final endpoint remains the supplied tf, just as in the old algorithm; a
rounded final tb is not silently substituted for it. A regenerated plan must
match every field and its digest. Duplicate/collapsed queries are rejected.

The sibling provider must supply the existing complete qualified pairs:

    cache_dir/<query_id>.json
    cache_dir/<query_id>.npz

The payload contains selected__S/H/D plus every attempted raw cross block.
QualifiedCache calls the unchanged parallel_bridge.validate_pair for each
required query, including the ordered ladder and first passing adjacent pair.
It freezes record/payload hashes in plan order. Lookup outside the exact plan
raises. On first materialization the pair hashes are checked again; arrays
are read-only. No interpolation, extrapolation or operator re-evaluation occurs.
Extra cache entries do not become permitted query times.

## State and restart contract

checkpoint_solver.run_cached(plan, cache_dir, out, c0, resume_from=None,
stop_after_steps=None) requires a fresh output outside the source tree.
The 18-component c0 is explicit and finite. Its original canonical complex128
bytes are bound separately from the once-normalized initial state.

The numerical recurrence invokes the unchanged candidate_step. It stores the
whitened state y after every completed step. It never renormalizes intermediate
states. Step zero and every later step receive a create-only NPZ/JSON pair;
the JSON binds the payload hash, previous checkpoint hash, exact plan/cache/
source/environment identity, step/time and norm/generator diagnostics.
Payloads are fsynced before an atomic create-only install; a JSON record marks
a completed pair.

A restart must name a prior run explicitly and produces a NEW run directory.
It verifies the entire contiguous checkpoint prefix and imports its bytes
unchanged. It rejects orphan pairs, gaps, changed payloads, a different initial
vector, selector, plan, operator cache, source closure or environment identity.
The source run and its failure evidence remain unchanged. The resume receipt
also binds any previous FIRST_FAILURE and RESULT records without reclassifying
their meaning. There is no implicit retry and no reuse of a native allowance.

The state at the last completed step continues the same numerical recurrence.
No operator queries or previous midpoint exponentials are rerun. A partial run
reports only its completed prefix; it does not fabricate an endpoint state at
a time absent from the operator plan.

## Commands

All numerical thread limits must be set before Python starts:

    export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
    export MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

The isolated CLI supports:

    python -I solver_cli.py plan --t0 T0 --tf TF --nstep N \
      --context-id CONTEXT --qualification-contract CONTRACT.json \
      --selected-indices 9,10,12,13,14 --out PLAN.json
    python -I solver_cli.py verify-cache --plan PLAN.json --cache-dir QUERIES
    python -I solver_cli.py propagate --plan PLAN.json --cache-dir QUERIES \
      --initial-state INITIAL.npz --state-key initial_state --out NEW_RUN

For restart add --resume-from OLD_RUN. For an intentional checkpoint pause,
add --stop-after-steps K. This last option creates a partial candidate, not
evidence of a numerical failure.

The runtime code requires no compiler or MPI launcher: operator evaluation
belongs to the separately pinned HPC provider. Small 18-by-18 exponentials
remain serial, with single-thread BLAS, while independent expensive queries
are parallelized in phase one. Checkpoint I/O does not change accumulation
order or the mathematical discretization.

## Outputs and claim gates

RUN_CONTEXT.json and CACHE_MANIFEST.json bind the full execution.
INITIAL_STATE.npz preserves both input and normalized vectors.
checkpoints/ contains the append-only state chain. A completed run writes
CANDIDATE_RESULT.npz with initial/final states and norm_history, plus RESULT.json.

The selected observable is the finite selected-span quadratic form
P=c†SJ(J†SJ)^(-1)J†Sc, evaluated by a positive-definite solve. It is labelled
FINITE_SELECTED_SPAN_DIAGNOSTIC_NOT_CAPTURE. The discrete norm gate is reported
against the exact supplied screen. Temporal refinement and independent reference
gates remain NOT_EVALUATED unless a separate comparison actually supplies them.

Source and environment matching support a same-environment restart. They do not
prove cross-host bitwise reproducibility or a continuous trajectory error bound.
An operator qualification pass is a finite adjacent-resolution comparison, not
an outward-rounded spatial certificate. A state restart test is an operational
and implementation result, not a capture or asymptotic accuracy certificate.

The saved N1536 +/-12 a0 evidence is not transferred to another window or backend.
An explicit acceptance-test state is not relabelled as an archived collision
state. The result keeps capture=false, production=HOLD, all_bound=OPEN,
b_grid=NO_GO, original_capture_gap_resolved=false,
continuous_global_supremum_bound=false and
continuous_trajectory_error_bound=false.

## Targeted validation

The initial missing-implementation failure is retained in TDD_RED.log.
Five tests then passed with zero skips, using synthetic 18-channel matrices:

* Exact array equality to the frozen midpoint implementation's final state and
  norm history, and to a pause/restart execution.
* Rejection of exact-time cache misses and tampered payloads, with zero fallback.
* Rejection of changed initial state, plan/selector and checkpoint payload.
* Rejection of orphan checkpoint pairs and existing output overwrite.
* An actual isolated Python CLI execution of the same cache-only contract.

These tests run the new solver. They are not new B0 operator evaluations and
are not re-executions of the unchanged historical validation suites.
