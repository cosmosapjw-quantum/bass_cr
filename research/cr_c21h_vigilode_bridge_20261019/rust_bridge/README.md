# C21H Rust solver bridge

This process integrates one frozen segment. The Python parent owns the original
C21F optical-depth RHS, the fixed state scaling, fixture, finite-difference
Jacobian and time derivative, native subprocess, and scientific acceptance.
No chemistry formula or birth schedule is ported into this executable.

## Pinned reused packages

- `rodas5p-core` and `rodas5p-integrators` from
  `cosmosapjw-quantum/vigilode@8a8bd409b1d96c7b7421f496d229e119fd3d284e`.
  This is the measured Run2 Rust commit. Fresh GitHub comparison with PR71's
  `0bab431e1031f86eb3ddb44371240bce49ae2376` found no changed Rust crate files.
  The default `main` branch is a different, older baseline. This bridge calls
  `integrate_rodas5p_fast_observed` with its default transformed dense RODAS5P
  driver, explicit Jacobian and explicit nonautonomous partial derivative.
- `diffsol = 0.17.1`, default features disabled, `faer` enabled: an independent
  BDF implementation with faer linear algebra. Existing VigilODE A07 source
  informed the builder/JVP integration pattern; its 0.16.1 Robertson results
  retain their historical problem, accuracy and timing status.
- `serde_json` enables `float_roundtrip`. All solver state arithmetic is f64.

Upstream VigilODE is MIT licensed. Its generic solver validation retains its
original scope; packet, polynomial and certified global-error claims are not
used by this bridge. Diffsol callbacks have no `Result` return: the process is
built with `panic=unwind` and catches a private `CallbackAbort` around the complete
BDF operation. A failed RPC aborts before a callback returns, and the executable
emits a failed result and exits nonzero. No dummy derivative/state is supplied.
Other panics are a separately labelled execution failure with retained stderr.

## Wire protocol

All records are newline-terminated UTF-8 JSON, flushed synchronously. The child
first emits a `type=hello` record with protocol `C21H_V1`, the exact VigilODE
commit, Diffsol version, and both method names. The parent sends exactly one
configuration:

```json
{"protocol":"C21H_V1","dimension":2,"t0":0.0,"t1":1.0,"y0":[1.0,1.0],"rtol":1e-8,"atol":1e-11,"h0":0.0001,"h_min":1e-15,"h_max":0.1,"max_steps":10000,"method":"vigilode-rodas5p"}
```

`method` may also be `diffsol-bdf`. The optional `output_times` array must be
strictly increasing and include the exact two span endpoints; omitting it uses
only those endpoints. Unknown configuration fields are rejected. The transport
dimension cap is 256 and the incoming configuration/response line cap is 4 MiB;
these are executable capacity limits. The complete accepted-path result can be
larger, and the parent enforces its own output byte budget. The parent supplies
already scaled variables and scalar tolerances.

Each callback emits `{"type":"request","id":1,"op":"rhs","t":0.0,"y":[...]}`.
Operations are `rhs`, `jacobian`, and `partial_t`. The parent returns
`{"id":1,"ok":true,"value":[...]}` or
`{"id":1,"ok":false,"error":"..."}`. Jacobians are nested row-major arrays.
IDs, dimensions, finiteness and exact segment membership are checked. Any
transport/provider/shape/domain error is terminal. The last pending request,
original callback error and attempted/validated callback counters are preserved
in the result. The parent enforces wall-clock, native-call and process limits.

## Outputs and accepted states

The final `type=result` record separates `ok` (a solver record was returned),
`success`, `complete_output`, requested `times/states`, actual
`accepted_times/accepted_states`, work counters and step counts. Exit zero
requires exact complete requested output and successful integration. Shape
checks compare full row counts; no zip truncation is used. The parent must also
require `accepted_grid_complete=true` before adopting an accepted-grid check.

The pinned VigilODE fast API exposes requested samples and its accepted-step
count. Its explicit Jacobian callback is invoked at every fresh accepted base
state; rejection retries may repeat that identical base. The bridge observes
these callback inputs, requires strict progression or bit-identical duplicate
states at the same represented time, and appends the successful final endpoint.
The complete observed path must contain exactly `internal_steps + 1` rows. This
observer changes no callback value, controller, solver state or requested grid.
Its source conditions are `Workspace::attempt`'s `fresh` Jacobian call and
`integrate_fast`'s accepted-state assignment/reset at the pinned commit.
An incomplete run exposes only an observed accepted prefix and marks its grid
incomplete; the missing last accepted point is never invented.

Diffsol's accepted path is read directly after each successful `step()`.
Its initial state is created with the public
`BdfState::new_without_initialise` followed by `bdf_solver`: for this identity-mass
ODE, the initial state and its exact RHS already provide a consistent derivative.
This uses the supplied `h0` directly. The convenience `bdf()` API estimates a new
initial step and makes an Euler probe that can leave a short frozen segment,
even when `.h0` is small. A manufactured test observed that domain failure;
the explicit-state construction fixes it without widening the callback domain.
Diffsol has no absolute maximum-step configuration field at this version, so
the bridge sets an explicit rolling stop `min(t + h_max, t1)` before each step,
rounds a representably oversized stop downward, and checks every actual step
against the cap. This is independent of the output grid. Requested interior
outputs use BDF interpolation. VigilODE lands on requested output times.

At nonzero time origins Diffsol can report a stop as reached while its represented
state time remains one ULP before that stop. Reissuing the stop then returns the
typed `StopTimeAtCurrentTime` error. The bridge handles only that precise error
for a strictly later represented stop: it checks the remaining step against
`h_min/h_max`, sets the public mutable state's step size to the remaining
interval, and calls the solver for a genuine additional step. The public API
restarts BDF history at order one, so each such restart records its time, target,
old/new step size, order and cause in `roundoff_step_restarts`. Accepted times and
states still come directly from actual solver steps. No state is relabelled as
having reached another time.

`max_steps` bounds VigilODE adaptive attempts; it bounds Diffsol outer successful
step calls, with retries remaining in solver/RPC counters. These work axes are
labelled separately. Diffsol obtains a full parent Jacobian and computes JVPs
locally. Its cache key is the exact bit sequence of `(t,y)` within this one
immutable segment; JVPs, matrix requests and cache hits are counted separately.

The scalar-atol transformation is defined by the parent. VigilODE uses its
old/new maximum state scale, whereas Diffsol 0.17.1/faer uses its current-state
RMS error scale. Equal tolerance inputs therefore do not establish equal
achieved error, cost, or a reference bound.

## Build and validation

Use the delivered lockfile and Rust 1.94.1. The wrapper requires explicit actual
Cargo/rustc paths and a new absolute target directory:

```bash
bash build_bridge.sh --cargo "$C21H_CARGO" --rustc "$C21H_RUSTC" \
  --target-dir "$C21H_NEW_BUILD_DIR"
```

Add `--offline` only when those pinned dependencies are already available.
The wrapper uses one build job, retains stdout/stderr, and writes a build receipt
with source, lockfile and binary hashes. It writes `SOURCE_BEFORE.json` before
Cargo starts and compares the same files afterward. Source drift, a missing
binary, or Cargo failure produces a nonzero exit and no successful binary hash.
The `source_files` object binds exactly `rust_bridge/Cargo.toml`,
`rust_bridge/Cargo.lock`, and `rust_bridge/src/main.rs`, each with `bytes` and
`sha256`, as required by the parent runner. Compilation and manufactured bridge
tests are separate from native chemistry and the pending NCP campaign.

Run the real-binary manufactured and failure-path checks with a new evidence
directory:

```bash
python3 test_bridge_protocol.py --binary "$C21H_NEW_BUILD_DIR/release/bass-cr-c21h-rust-bridge" \
  --output-dir "$C21H_NEW_PROTOCOL_EVIDENCE"
```

`test_build_receipt.py --output-dir NEW_DIRECTORY` separately checks the receipt
contract using clearly labelled isolated Cargo/rustc stubs. Those tests do not
establish compilation or solver execution.

Ten source unit tests cover invalid controls, output-grid identity, RPC IDs,
matrix shapes, persistent callback failures, domain rejection, output
completeness, typed Diffsol abort, f64 serialization, and the accepted observer.
Their actual execution status is recorded in the enclosing C21H evidence.

### Observed sandbox validation on 2026-10-19

| Check | Result | Evidence scope |
|---|---|---|
| Canonical Git-pinned lock generation | PASS, Cargo exit 0 | Delivered canonical lock retained |
| Actual Rust check | PASS, exit 0 | Both solver packages and this bridge typechecked |
| Final Rust unit tests | 10/10 PASS, exit 0 | Same final bridge source as the binary |
| Real-binary protocol checks | 16/16 PASS, exit 0 | Four analytic IVPs and four failure/partial cases for each backend |
| Build receipt contract | 3/3 PASS | Tool stubs only; source drift and Cargo failure rejected |
| Native chemistry through this new bridge | NOT_RUN | Requires the independent native execution gate |

The first protocol run recorded 11/12 PASS and the Diffsol initial-probe failure.
`blackbox_01` retains that raw failure; `blackbox_02` records the corrected run.
The subsequent same-RHS wiring smoke exposed the one-ULP endpoint problem.
`blackbox_epoch_red_01` records both new epoch regressions failing under Diffsol;
`blackbox_03` records all 16 cases passing after the explicit closing-step fix.
The original unit tests were written with the implementation. The two defects
have recorded failing executions followed by their fixes; this does not make
the complete test collection a red-first suite.

Sandbox resource limits required a local Cargo source override for the three
VigilODE crates. All 476 selected upstream source/fixture files were verified
against the pinned Git blobs; the actual local lock differs from the delivered
canonical lock only by the three Git source-location fields. Registry package
versions and checksums are identical. The mode is explicitly recorded as
`LOCAL_PATH_OVERRIDE_OF_VERIFIED_IDENTICAL_GIT_SOURCE`. The published Cargo files
retain direct Git dependencies. Builds used Rust 1.94.1, one job, no incremental
compilation, and unoptimized code with debug information disabled. These runs
provide no speed ranking or native physical-reference accuracy bound.

The actual final binary SHA256 is
`a11d3ab01474f9d1a88df51c9cd6d7910ca59b3443814fd39699ed959cb64048`.
Raw logs, accepted states, RPC records, source binding, and receipts are in
`../evidence/rust_bridge_20261019/`.

Official API sources read for this implementation:

- https://docs.rs/diffsol/0.17.1/diffsol/ode_solver/builder/struct.OdeBuilder.html
- https://docs.rs/diffsol/0.17.1/diffsol/ode_solver/method/trait.OdeSolverMethod.html
- https://docs.rs/diffsol/0.17.1/diffsol/ode_solver/config/struct.BdfConfig.html
- https://docs.rs/diffsol/0.17.1/diffsol/ode_solver/state/struct.StateRef.html
- https://docs.rs/diffsol/0.17.1/diffsol/ode_solver/state/trait.OdeSolverState.html
- https://docs.rs/crate/diffsol/0.17.1/source/src/ode_solver/state.rs
- https://docs.rs/crate/diffsol/0.17.1/source/src/ode_solver/problem.rs
- https://docs.rs/crate/diffsol/0.17.1/source/src/ode_solver/bdf.rs
- https://docs.rs/diffsol-la/0.2.0/src/diffsol_la/vector/faer_serial.rs.html
