# G12: derived and checked nonnative parity; physical parity remains open

`REPORT_GAP_12` started at `REPORTED_RECOMMENDATION_NOT_VALIDATED`.
It is now **RESOLVED_WITH_LIMITATION**. The whitening connection and a CF4
reference are derived and implementation-checked. No physical production
tolerance claim is closed.

Inspection found that the repository already has two method families in
`research/foundation_rebuild/tp1_short_transport_20260926/`:
`metric_transport.py` contains Cholesky-frame exponential midpoint, and
`reference_transport.py` contains direct generalized-ODE DOP853. This work
preserves those implementations, adds CF4, and runs a new analytic benchmark.
It does not claim to have invented the prior independent reference or rerun a
previously closed B0 temporal certificate.

The exact noncommuting synthetic trajectory uses a moving nonorthogonal metric.
The new strict whitening agrees with the existing generator to 1.12e-16 in
the sampled audit. Centered differences of the Cholesky factor show second-order
convergence to Rdot=XR. The connection-free generator demonstrably fails
anti-Hermiticity; incompatible Sdot and non-SPD inputs are rejected.

| Method | Steps | Metric state error | Selected population error |
|---|---:|---:|---:|
| Existing midpoint | 128 | 3.524923e-5 | 1.398123e-5 |
| New CF4 | 128 | 1.470249e-10 | 7.239503e-11 |
| Existing direct DOP853 | adaptive, 371 RHS evaluations | 2.926721e-14 | 4.135581e-15 |

On the 8,16,32,64,128 ladder, midpoint error ratios tend to 4 and CF4 ratios
tend to 16. CF4 norm drift stays below 1.56e-15; DOP853 sampled norm drift is
4.18e-13. DOP853 used rtol=5e-13 and atol=5e-15. These are errors against a
known synthetic solution, not rigorous float64 enclosures or selected physical
B0 production thresholds. Operator queries are recorded because CF4 requires
two Gauss-stage snapshots per step and cannot silently reuse midpoint snapshots.

TDD preserved an initial missing-module failure and a later 64-step threshold
failure: its 2.352867e-9 state error exceeded the predeclared synthetic 2e-9
check. The threshold was retained, the ladder extended to 128, and all six
tests then passed. This is a synthetic discretization refinement, not a native
resource authorization.

Commands from this directory:

```
python -m unittest discover -s . -p test_independent_propagator.py -v
python independent_propagator.py
```

The minimal physical contract requires a qualified operator provider at the
actual Gauss nodes and independently validated metric derivative inputs. The
currently cited static snapshots alone do not define an operator trajectory;
interpolating them would introduce an additional unverified method. A physical
parity budget must be declared before running and must cover operator and
temporal uncertainties. `PHYSICAL_PARITY_CONTRACT.json` explicitly records the
unbound requirements and forbids execution until they are bound. It is a
finished input/return contract, not a native-ready authorization object.

Next minimum action: bind the exact current B0 initial state and qualified
operator provider for the existing +/-12 a0 window; declare the method-parity
budget and initial stage-grid/resource proposal; then request fresh narrowly
scoped execution authority only if the parent workflow advances this branch.
No extended physical window, B1 basis, b-grid, or native query was executed.

New external calls=0; new native calls=0; historical authorization consumed=0.
Capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO and all continuous
physical-bound ceilings remain unchanged.

## Independent review correction: common initial value

The historical midpoint and DOP853 helpers normalize their input state, while the new CF4 preserves the supplied norm. The analytic benchmark starts at unit metric norm, so the reported synthetic comparisons are unchanged. A nonunit physical input would otherwise define different initial-value problems. PHYSICAL_PARITY_CONTRACT.json now requires an explicitly named common normalized IVP, per-method actual initial-state/norm receipts, and a predeclared initial-distance allowance included in the parity error chain. A null allowance blocks physical execution. No historical solver behavior was changed.
