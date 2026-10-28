# C2 — Formula, data and code mapping

| Mathematical object | Input / representation | Executable responsibility |
|---|---|---|
| a_i,E_i,b_i and source identity | Original NPZ; cf.Atom exact Fraction fields; original consumer's attested AtomBundle | Byte-pin every dependency before import; use cross_envelope.native_module() once, then its load_pinned_source→binding→claims→consume path |
| Effective low/high sets and domain | Positive a_i, exact2E_i<=K | New joint_region domain report; return the actual lowest-energy forbidden same-bin HL pair if one exists |
| L,N and D | Exact sums; saved PR114 dmax/max_events for native; energy_sum.solve for fresh small general fixtures | Convert the separate PR114 Atom/Event classes explicitly; do not invoke its distinct native loader |
| M=2D-L and B=(D,M) | HL+diagonal saved maximum events | Verify support/marginal/d/C with the new full-event verifier; no PR114 optimization replay on native data |
| X and cross G | Saved PR115 bound; saved K20 witness; new K6 primal | Reuse exact bound identity; cross_flow prefix graph plus new integer backend only for missing native primal |
| F=(D,X) | Theorem common-optimum construction | Exploit verified X=M, X=D or M=0 where applicable; use exact residual augmentation for other general inputs |
| Arbitrary(d,C) | Rational target and complete O/A/B/F/G measures | The theorem's guarded convex interpolation; merge unordered legs and retain exact singleton residuals |
| Native returns | Verified event measure and one original consumer instance | Create original Event IDs once; same event object/ID appears in each incident partition; apply W and nb through original consume_event_union |

The new full-event verifier must accept same-bin doubles and diagonals when energy permits, count every diagonal twice, and compare all atom marginals. The old cross_envelope.verify_primal is useful only for a cross-optimal pair/single witness. The old energy_sum.verify also imposes its particular solver's sparse-record bounds, which need not hold for convex mixtures; that incidental representation constraint is not inherited by the new joint verifier.

The existing cross_flow._Network API constructs exact integer capacities after clearing the mass denominators. Its max_flow(source,sink,bound) is the sole backend seam. A new bounded C++ solver can consume the forward-edge network, return exact forward flows, and restore residual capacities in the Python object. Existing reachable/cut checks, prefix FIFO decomposition, symmetrization, marginal reconstruction and exposed dual remain available unchanged. The scientific change is the max-flow execution backend and the new joint construction; there is no float capacity conversion.

Native adapters keep the consumer's tuple-array atom digest distinct from PR115's dataclass/dictionary bound digest. Both are checked in their own schemas, with atom field equality when crossing representations. Saved JSON fraction strings are parsed as Fraction; core callers accept only exact int/Fraction and reject float/bool. Source guards must fail before a constructor uses a mismatched payload.

Data flow is NPZ→one attested source bundle→exact atom conversion→domain guard→saved scalar/primal reuse or new K6 primal→joint vertices/interior→new atomwise verification→original consumer→exact serialized certificate/summary. Independent validation rereads the NPZ and certificate without importing the joint constructor. Plots read the saved summary only.

Only the new unit's code, results and root current-unit header may change. Four pinned reused computational dependencies are packaged with the new unit: event_union.py, cross_flow.py, cross_envelope.py and energy_sum.py. The source/normalization and unrelated old driver/test files are not modified. Failure categories are separated: input/domain/identity rejection, mathematical certificate failure, backend numeric-range/flow failure, runtime resource failure and provider publication failure.
