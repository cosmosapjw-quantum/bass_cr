# G02: independent metric-derivative implementation audit

**Result:** `BLOCKED_RESOURCE_POLICY_BLOCKER` for the physical G02 claim. The source audit, strict saved-data postprocessor, reuse validator, plan generator, bounded fresh-scope native executor and synthetic FD regression are complete. No physical operator or native library was invoked. `REPORT_GAP_02` remains the database identity; its original row is a recommendation, not a validated claim.

## What the current implementation computes

Exact file SHA256 pins are in `SOURCE_PINS.json`; the fetched execution source head is `01ec2ba7e71aefdccab1896acfe5d92c15c6b776`. The theory branch anchor is `432010f2afd5305ca63933056f50584c01e4e524`.

| Source/function | Relevant operation | Independence and limitation |
|---|---|---|
| `tp2a_analytic_pruning_20260926/code/moment_kernel.cpp`, both `bass_moment_accumulate_*_v1` | `sv=at*ap*f`; `dTP` uses `bp`, spatial angular derivatives and `-.5*i*vp2*sv`; `dPTconj` uses target velocity terms | Direct overlap and analytic time-derivative expressions are distinct. Neither computes D from an FD of S. They share quadrature, radial input, phase and native contraction. |
| `.../code/exact_cross.py`, `_radials`, `cross` | evaluates radial values and derivatives; returns `S_tp=S`, `S_pt=S†`, both direct D directions | An FD made from re-evaluated overlaps tests an independent **derivative path**. Shared quadrature/model errors remain possible. Reverse S/H conjugacy is imposed analytically, not independently measured. |
| `full_operator_20260926/full_operator.py`, `same_center_blocks` | S from radial overlap; D=`-vA-.5*i*v²*S`, A from direct spatial derivatives | Fixed same-center order20. S is constant analytically under own-center translation; the numerical radial rule splits at R, which can expose quadrature defects. D skewness and FD constancy are useful tests, not independent basis/model validation. |
| `.../full_operator.py`, `assemble_full` | joins independently computed same-center blocks and identity-bound cross blocks | Checks dimensions/identity/Hermiticity/metric. No Sdot forcing occurs. |
| `tp2d_runtime_self_qualified_transport_20260927/transport_policy.py`, `metric_derivative_residual` | existing three-query central FD at a single epsilon | A useful old diagnostic, insufficient by itself for the requested h-convergence evidence; this audit does not change it. |

Thus **a genuinely different differentiation procedure is available**, but it has not yet been run at the requested signed tail points and shrinking h ladder. The stronger statement that S and D have fully independent numerical or physical errors is false.

## Derived diagnostic and units

With z=vt and positive `v=2.00798106651023 a0/atomic_time`,

\[
F_h(z)=v\frac{S(z+h)-S(z-h)}{2h},\qquad E_h=F_h-(D+D^\dagger).
\]

S is dimensionless and F, D, E have units `atomic_time^-1`. If S is three times differentiable on the stencil, central FD has O(h²) truncation. For a uniform bound `||S'''||≤M3`, `||F_h-vS'||≤v h²M3/6`. This is conditional mathematical analysis, not a bound already established for the physical FEM quadrature.

Saved-operator uncertainty is amplified by differentiation. If true error bounds were available, their contribution would be at most `v(εS+ + εS-)/(2h)+2εD`. Adjacent-resolution differences do not supply those ε bounds. The residual is reported in spectral and Frobenius relative norms and a maximum normalized component norm, alongside absolute residuals. A documented absolute component floor prevents division by zero entries.

The default acceptance requires two consecutive observed spectral-error orders in [1.5,2.5] and finest-ladder spectral/Frobenius/component residuals below **1e-6 relative or 1e-12 atomic_time^-1 absolute**. The 1e-6 relative target preserves the existing metric-derivative screen; none of the production qualification screens are relaxed. Failure to show order, including exactness or roundoff plateau, is `ORDER_NOT_RESOLVED`, never an automatic pass. If h=.05 is still pre-asymptotic, a new narrower stencil contract is required; no automatic point expansion occurs.

## Actual available evidence

Six center operators at ±16, ±24, ±32 were read from the hash-verified A1 science return. Each JSON/NPZ pair is independently checked for record and payload hashes, exact time hex, source context, matching native/basis/physics identity, shape, finiteness, metric and qualification status. Their original bytes are retained in `reused_snapshots/` with `REUSE_MANIFEST.json`.

The restored preparation contains a +12 NPZ without the paired provider JSON. That is insufficient to establish original query qualification and binding; it is **not reused**. The -12 pair is also unavailable. No state vector is used anywhere in this diagnostic.

The exact plan has 72 distinct operator coordinates: eight center D values and 64 shifted S values. Six center queries are verified reusable, leaving **66 new qualified queries**. The actual provider ladder contains 11 rules, so the worst-case ceiling is **726 raw operator evaluations**, not 132. Two raw attempts per new query would be 132 if every first adjacent pair passes; that is an estimate, not the cap. See `E_SDOT_FD_EXECUTION_CONTRACT.json` for every coordinate/time and the unchanged ladder/screens.

## Implemented and tested

`static_validation.py` has no import or call to the native evaluator. Its public commands generate a plan and postprocess a supplied saved-query manifest. Manifest inputs include explicit units and identity binding, original provider record hash and paired NPZ; unknown contexts, duplicate coordinates, mismatched time/basis/source/units, invalid qualification, bad matrices and hash failures stop processing. The binding itself must be checked against the source/preparation provenance by the execution reviewer; a self-authored sidecar is not independent proof of its truth.

`python -m unittest discover -s research/gap_closure_20261001/static_validation_20261001 -p test_static_validation.py -v` passed **8 tests** on Python3.12.14 / NumPy2.3.5 / SciPy1.17.0. The initial red run failed with the new module absent; green runs exercise the implemented APIs. `build_evidence.py` additionally validated the six actual physical saved pairs and returned all missing coordinates. No old suite was rerun.

For the analytic synthetic `S=diag(2+.1sin z,3+.2cos z)`, exact D shows approximately second-order residual decay; a 10% derivative defect plateaus and fails. The synthetic demonstration uses an explicit 1e-3 residual target so the four prescribed h values demonstrate order without pretending to achieve the physical target. It does **not** change the physical 1e-6 contract. Exact numeric rows are in `SYNTHETIC_FD_CONVERGENCE.csv` and `E_SDOT_FD_RESULTS.json`.

## Minimal next execution and stopping point

The source-independent consumer and complete bounded producer are ready. `executor/fd_executor.py`, `fd_worker.py`, `prepare_fd_authority.py`, `run_fd.py` and `supervise_fd.py` implement fresh G02-specific admission,66-query whitelist,726-raw atomic budget, unchanged numerical worker, exact source/native/bank verification, live CPU/RAM/thread checks, unique authorization consumption, isolated process group, deadline/teardown and create-only return. The consumed A1 authorization and its eight-point whitelist are never reused. `executor/README.md` gives the executable preparation/run handoff; `NATIVE_RETURN_CONTRACT.md` specifies the return boundary. External execution still requires the new live proposal's exact approval. The restored native bytes and bank are available; missing environment is no longer asserted as the primary blocker.

No tail-rho extension, interpolation, sign symmetry reuse, propagation, N768/N1536 rerun or ±48 expansion is authorized by this plan. G02 physical closure remains open until returned independent FD convergence and source binding are reviewed. Capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO and both continuous-bound fields remain unchanged.
