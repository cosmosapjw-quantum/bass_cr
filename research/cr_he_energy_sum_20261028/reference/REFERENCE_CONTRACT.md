# Independent reference contract

## Purpose and status

The independent reference file is generic_dual.py in this directory, authored by /root/energy_theory_audit for CR_PHYS02_HE_ENERGY_SUM_V1. Its author read the frozen unit CONTRACT.json, the actual theory/THEOREM.md and the prior substantive R6 findings. The actual R5 theorem incorporates the independently derived inventory intersection, full-support p=0 scope, C/d distinction, zero-optimum handling and native/general-domain separation.

The reference author did **not** read or import production energy_sum.py, execute scientific Python, load NPZ arrays, compile/test this reference, invoke CAS, or run any fixture. AUTHORING_STATE remains NOT_EXECUTED_BY_AUTHOR. Root's measured C6/C7 runner owns execution, CPU charges and actual result records. This document is a code contract, not a claim of test success.

Only generic_dual.py and this REFERENCE_CONTRACT.md were written during reference authoring. The earlier R06_INDEPENDENT.md/.json are preserved unchanged.

## Inputs and exactness

All scalar inputs accept only plain int, str or fractions.Fraction. bool, float and nonfinite strings are refused. Input sequences are list or tuple. Fractions are never converted to float. K, energies and weights must be nonnegative.

The reference operates on the general mathematical finite-atom domain E>=0. This includes empty atom lists and E=K=0 fixtures. The retained native PHYS02 adapter has its own narrower support, fixed 4-partition and provenance contract; this reference does not expand that adapter.

The full-support certificate is a coefficient measure. No proper-window W, new source normalization, nb division, NPZ authentication, state evolution or physical closure occurs here. The measured integration runner must separately retain original source hashes, the old consumer, W once, explicit nb8750/47, neutral inventory and physical null fields.

## API1: dual_oracle(energies, weights, K)

The oracle accepts n<=7, including n=0, and constructs every allowed unordered pair (i,j), i<=j, directly from E_i+E_j<=K. It enumerates every z in {0,1,2}^n, sets y=z/2 and tests z_i+z_j>=2 for every allowed pair. A loop is therefore checked as 2z_i>=2, or 2y_i>=1.

No low/high classification, tail deficit, matching recurrence or production helper is used. A common exact denominator converts the weighted objective to an integer objective before enumeration. Lexicographic enumeration gives a deterministic first minimizer among ties.

Returned fields include exact dmax, explicit dual coordinates in original atom order, full allowed pairs, N, parent_min=N-dmax, atom/loop counts, assignments_examined and feasible_assignments. The bound is 3^7=2187 candidates per fixture. These counters are filled only by actual future execution.

Returned Fractions remain Fractions. The caller should serialize each using str(value); floats would lose the intended exactness.

### Why half-integral enumeration is complete

The fractional packing primal has one variable for every allowed pair and has atom capacities w_i, with a diagonal using two units of its atom. Its dual has y_i>=0 and y_i+y_j>=1 for every allowed pair, including 2y_i>=1 for a loop.

For nonnegative weights, clipping every coordinate above1 to1 preserves feasibility and does not increase objective. The resulting bounded polytope attains an optimum at a vertex. In the graph of tight edge equalities, y_i+y_j=1 propagates values. A component anchored to a bound0 or1 propagates integer values. A component with an odd cycle or a loop is fixed at1/2. An unanchored bipartite component with no loop can be perturbed in opposite directions on its two color classes, so it cannot define a vertex. Consequently some optimum has all coordinates in {0,1/2,1}.

The primal is feasible via all singles and bounded by total capacity. Finite-dimensional LP duality identifies the minimum dual value with maximum double mass. This is a generic graph result; enumeration does not depend on the energy-support theorem's deficit formula.

## API2: deterministic_fixtures()

This function returns48 fresh fixture dictionaries and solves none. Each dictionary has:

- id: stable F001–F048 identifier.
- energies, weights, K: exact Fraction input values.
- tags: coverage labels.
- analytic_anchor_dmax: an optional manually transparent one-atom, all-low, all-high or zero-mass value.
- atoms: plain dictionaries with key, energy_eV and coefficient.

The cases cover empty input, zero cap/energy/mass, all-low and all-high, repeated energies, exact pair/diagonal equality, below/above equality, stored binary64 cutoff versus decimal cap, nonbinary rational energies/weights, isolated vertices and disconnected graphs, nested eligibility, heavy high/low masses, a maximum tail deficit away from the final level, input permutation, and seven-atom cases.

The stored cutoff is written directly as 3602879701896397/36028797018963968. F010 uses decimal cap1/5; F011 uses exact doubled stored cutoff3602879701896397/18014398509481984. Their oracle outputs must differ, with anchor0 and1 for atom mass2.

Small graph disconnection here includes isolated vertices. No claim that an energy-threshold graph admits arbitrary unrelated nontrivial components is needed.

Malformed scalars and forged certificates are not valid oracle fixtures. The measured runner should construct negative mutations and assert the appropriate ReferenceValidationError or production rejection separately.

## API3: verify_certificate(...)

Signature:

    verify_certificate(
        atom_records, K, event_records, dual_by_key,
        *,
        expected_dmax=None,
        target_d=None,
        require_optimal=True,
    )

Input atom records contain key, energy_eV and coefficient. Optional partition metadata must be supplied for every atom if present at all and must use integers0..3. It enables an independent cross-C calculation but does not validate the native energy-to-partition assignment; that belongs to the retained native adapter.

Each event contains a unique nonempty key, electrons with one or two known atom keys, and a positive exact coefficient. A repeated electron key is a diagonal. The evaluator directly accumulates every leg into its atom marginal, checks energy support for every actual double, and checks every marginal against the explicit atom weights. It also recomputes total singles, doubles, diagonal mass, parents and kinetic coefficient.

dual_by_key must have exactly the full atom key set. Every coordinate is parsed independently and must be nonnegative. The evaluator verifies the entire allowed graph by the method below, computes sum_iw_iy_i, and checks the primal-dual gap.

With require_optimal=True, a zero gap certifies sharpness independently of the production solver. With require_optimal=False, a target witness and its dual upper bound are checked. A positive-gap target alone does not certify that its upper bound is attained; use a separately certified maximum witness for that claim. expected_dmax, if supplied, must equal the checked dual objective; target_d must equal the actual double coefficient.

Outputs include exact marginal residual, graph-constraint coverage, objective/gap, optimality_certified, all event statistics and full-support p=0 ion/charge/chemical coefficient values. It also reports witness-specific cross_duplicate_coefficient when partition data is complete. Cross-C is not optimized here.

### Complete native dual verification without an all-pairs allocation

At n<=7, every allowed pair and loop is individually checked. At larger n, sort the explicit atoms by energy. For any atom i, its entire allowed neighbor set is the closed energy prefix E_j<=K-E_i. Prefix minima of the explicit y_j then give

    min_j allowed (y_i+y_j) = y_i + prefix_min_y(K-E_i).

Checking this single minimum for each nonempty prefix is equivalent to checking every graph constraint. bisect_right preserves the closed equality. A self-neighbor is included exactly when2E_i<=K, so diagonal constraints are included automatically.

This check works for arbitrary explicit dual coordinates; it does not assume they are0,1/2,1 or follow a high-tail template. It uses no deficit or greedy code. Sorting plus binary-search queries uses O(nlogn) comparisons and O(n) storage; exact rational arithmetic bit costs are separate.

The exact number of unordered pair/loop constraints is recovered from ordered neighbor counts: (ordered_edges + loops)/2. Output field pair_constraints_covered_exactly denotes this logical full-graph coverage. constraint_checks counts actual explicit checks for small graphs or nonempty prefix minima for large graphs; it does not falsely claim an individually scanned O(n^2) loop.

Certificate resource bounds are4096 atoms and8192 events, covering the original3201 atoms and the theorem's at-most2n_positive target-event construction. The oracle's n<=7 limit is separate.

## Planned measured integration

The root runner should:

1. Call deterministic_fixtures and dual_oracle, compare production dmax exactly, and verify any present manual anchor.
2. Convert production saved atoms/events/dual to the plain reference record contract without importing production internals into the reference module.
3. Verify each maximum witness with require_optimal=True and intermediate targets with require_optimal=False, keeping the independently certified maximum evidence.
4. Exercise missing event, forbidden pair, forged dual, malformed exact scalar, duplicate key and target mismatch mutations.
5. For saved native output, pass all3201 exact atom records and the explicit sparse events/dual to verify_certificate. The large-mode prefix check covers all allowed constraints; selecting two documented K values may limit execution count, while each selected certificate is checked in full.
6. Keep original source/provenance/time/state/nb/replay checks and neutral inventory acceptance in the retained consumer. The reference does not assign actual K, actual kernel/C/D, donor work, outside response, EOS/T or physical native25.

Code authoring and static readback do not discharge these execution obligations. All actual resource use belongs to the new unit's measured allowance; no closed-node or PR113 budget is transferred.

