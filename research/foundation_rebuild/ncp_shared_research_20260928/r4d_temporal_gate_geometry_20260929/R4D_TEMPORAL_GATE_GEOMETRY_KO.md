# R4D temporal-gate geometry research loop

상태: **R4D_GATE_GEOMETRY_CLOSED__N768_RECLASSIFIED_AS_BRIDGE_RUNG**

## 1. Frozen inputs

- execution code: `4c2c0be5171c74a52b4a6e96b04c33fa00c62481`
- execution tree: `2e1a3175a7d20cf9c0218fb15f07f72d4afcb425`
- current research parent: `60e69781dc2bf7614a2f6ad65ffc8c0880a80fc2`
- historical N=384 -> reference phase-aligned metric distance:
  `2.6345608772805691e-06`
- frozen candidate-to-reference screen: `1e-6`
- frozen consecutive-refinement screen: `1e-6`

The implementation defines

    d_S(a,b) = min_phi || a - exp(i phi) b ||_S,

and `assess_temporal_pair` evaluates both the candidate-reference and
previous-candidate distances with the same final overlap matrix `S_final`.

## 2. Geometry theorem

Because multiplication by a global phase is an isometry of the positive-definite
S-norm, the phase-quotiented distance obeys the triangle inequality. Therefore,
for A=N384, B=new candidate, R=reference,

    d(A,R) <= d(A,B) + d(B,R).

The frozen screens would require the right-hand side to be <= 2e-6. But

    d(A,R) = 2.6345608772805691e-06 > 2.0e-6.

Therefore **no N768 state, regardless of integrator order or actual numerical
value, can satisfy both frozen screens simultaneously**.

Equivalent bounds:

    min_B max[d(A,B), d(B,R)] >= d(A,R)/2
                              = 1.3172804386402845e-06.

Thus the best possible maximum of the two distances is already larger than
1e-6. If the N768 candidate passes the reference screen, then reverse triangle
inequality forces

    d(N384,N768) >= d(N384,R) - 1e-6
                 = 1.6345608772805691e-06,

which necessarily fails the refinement screen. The converse statement holds
with the two distances interchanged.

This conclusion is **derived**, not an extrapolation, and is independent of
second-order convergence assumptions.

## 3. Consequence for the execution DAG

N768 cannot be a temporal-gate-closing rung under the frozen screens.
It remains scientifically useful only as a **bridge rung** because the frozen
N1536 test uses the consecutive pair N768 -> N1536. Skipping N768 would either
remove the required previous state or silently change the gate definition.

Therefore the correct N768 terminal state is:

- bridge evidence valid + at least one frozen distance screen fails:
  `R4D_N768_BRIDGE_COMPLETE__TEMPORAL_CLOSURE_UNRESOLVED`;
- both distance screens somehow pass:
  `METRIC_OR_EVIDENCE_INCONSISTENCY`, because that contradicts the frozen
  N384-reference distance and triangle inequality;
- operator/environment/identity/nonfinite failures:
  the corresponding BLOCKED/FAILED class.

There is no automatic N1536 authorization after N768.

## 4. Extrapolation audit

The historical R4B diagnostic records separate latest observed orders

- reference-distance order: `2.000148765470919`
- refinement-distance order: `2.000748231204326`

but its `selected_span_diagnostic.py` sets `pstate=ref_orders[-1]` and uses the
same ratio for **both** future distance estimates. Therefore the historical
refinement extrapolation is internally inconsistent with its own recorded
`observed_order_refinement_distance_latest`.

This affects only a scheduling heuristic, not historical physical states or
the frozen gate.

Using each recorded order with its matching sequence gives:

- N768 reference-distance heuristic: `6.5857230623527754e-07`
- N768 refinement-distance heuristic: `1.9751677025877228e-06`
- N1536 reference-distance heuristic: `1.6462610003825063e-07`
- N1536 refinement-distance heuristic: `4.9353589459168162e-07`

The old R4B N768 refinement estimate was `1.975988590822597e-6`; the corrected
sequence-specific estimate is `1.9751677025877228e-06`. Both predict failure of
the 1e-6 refinement screen at N768. These are **heuristics only**.

## 5. Literature check

SciSpace searches identified literature that supports the broader numerical
interpretation but does not replace the project-specific gate:

1. Blanes, Casas, González & Thalhammer, *IMA Journal of Numerical Analysis*
   (2021), DOI `10.1093/IMANUM/DRZ058`: convergence/stability analysis for
   commutator-free quasi-Magnus exponential integrators for nonautonomous
   linear Schrödinger equations, with structural preservation and regularity
   assumptions.
2. Descombes & Thalhammer, *BIT Numerical Mathematics* (2010),
   DOI `10.1007/S10543-010-0282-4`: exact local-error representation for
   exponential splitting methods, emphasizing the conditions under which
   asymptotic order estimates are meaningful.
3. Ture & Jang, *J. Phys. Chem. A* (2023),
   DOI `10.1021/acs.jpca.3c07866`: unitarity-conserving Magnus propagators and
   higher-order time propagation for time-dependent Hamiltonians.
4. Joubert-Doriol, *J. Chem. Theory Comput.* (2022),
   DOI `10.1021/acs.jctc.2c00461`: finite-step propagation in a
   time-dependent nonorthogonal basis with semi-unitary construction.

These papers support treating near-second-order behavior and structural
preservation as numerical evidence. They do **not** certify this specific
moving-basis implementation, its operator provider, or the frozen 1e-6 gate.

## 6. Wolfram cross-check

Wolfram evaluation independently returned:

- `d384_ref - 2e-6 = 6.3456087727796e-7 > 0`,
- `d384_ref / 2 = 1.31728043863898e-6`,
- pure p=2 prediction:
  `d_ref(768) = 6.58640219319491e-7`,
  `d_self(384,768) = 1.97592065795847e-6`,
- simultaneous `<=1e-6` feasibility: `False`.

This agrees with the direct derivation. The exact gate impossibility does not
depend on the Richardson/Magnus heuristic.

## 7. Claim ceiling

Unchanged:

- `capture_execution_allowed = false`
- `production_admission = HOLD`
- `all_bound = OPEN`
- `b_grid = NO_GO`
- `original_capture_gap_resolved = false`
- `continuous_global_supremum_bound = false`
- `continuous_trajectory_error_bound = false`

No new native evaluation, DOP853 reference replay, historical rung replay,
capture calculation, or b-grid calculation was performed in this research loop.
