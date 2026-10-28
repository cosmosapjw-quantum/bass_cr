# Exact conditional atomwise energy-sum implementation

`energy_sum.py` is the new general core and a thin same-state adapter to the
byte-pinned PR112 event-union consumer. It does not import a source fit,
quadrature, transport, RR or retained-photon implementation.

## Public core API

`Atom(key, energy_eV, coefficient, partition=0)` and
`Event(key, electrons, coefficient)` are frozen records. Core scalars accept
only Python `int` or `Fraction`; `bool`, floating point and strings are refused.
Atom keys are unique nonempty strings, partitions are nonnegative integers,
and energies/masses are nonnegative. The finite input is a tuple or list;
the empty declaration is valid. Native atoms are a separately restricted domain.

`solve(atoms, K_eV, target_d=None)` returns a frozen `Solution`. Its complete
maximum witness and dual certify `dmax`. Its second witness has the requested
double mass, or `dmax` when no target is given. `Solution` holds immutable
tuples/Fractions and an exact atom-content digest. The requested target must
lie in `[0,dmax]`; the all-single construction handles `dmax=0` without division.
Zero-weight events are omitted. All marginal legs, including two identical legs
in a diagonal event, are accounted for individually.

`verify(atoms, solution)` independently checks the supplied marginal, each
represented pair's energy sum, the maximum and chosen double sums, complete
dual domain, primal-dual exact equality, the threshold-deficit witness,
record bounds, and the recomputed atom digest/mass counters. It does not call
the greedy solver or trust a solver status. The independent small-graph oracle
is a different implementation, outside this production module.

For dual feasibility, group atoms by dual value `0, 1/2, 1`. For any two groups
whose dual sum is below one, an allowed violating pair exists exactly when the
sum of the groups' minimum energies is at most `K`. Within one group, the same
minimum atom is allowed to be used twice: this tests the diagonal too. This is
a complete check of all pair and loop constraints, including zero-mass atoms,
in linear time plus at most six group comparisons. It is not a sampled edge
check. Maximum-witness marginal equality and equal primal/dual objectives
certify optimality independently of the tail sweep.

Sorting costs `O(n log n)` comparisons; the two sorted sweeps, construction and
certificate check use `O(n)` rational arithmetic operations. These are not
constant-bit-cost claims. The maximum witness has at most `n_positive` records;
an arbitrary target has at most `2*n_positive`. The witness's `cross_C` is its
own cross-partition double mass and is **not** an optimized energy-support C.

`serial(value)` produces stable JSON-compatible rational strings and recursively
serializes the records. `content_id(value)` hashes canonical compact sorted-key
JSON. This serializer is not an input parser; callers must explicitly reconstruct
Fractions when loading serialized scientific data.

## Native API and provenance

`load_native(npz_path, predecessor_path=None)` checks the predecessor module's
SHA256 before its first import, then calls its original byte-verified NPZ
loader. Only that loader attests the retained 3,200 active atoms and distinct
cutoff ghost. `bind_cap(source,K_eV,assumption)` requires this attested complete
source and a nonempty explicit conditional assumption. It binds the cap in eV,
the canonical source SHA, attribution SHA, atom digest, same-state identity,
predecessor-module SHA and actual-physical-K null into a content digest.
`validate_cap` reconstructs and compares the complete binding, rejecting stale
source metadata, missing/extra fields and modified digests.

`native_plan(source,cap,target_d=None)` binds the general solution to that exact
cap digest. `consume_native(source,cap,solution,window,nb_m3=NB,
previous_windows=(),bound=None)` checks the solution/cap/source relationship,
then uses all four original partition claims and invokes the original consumer
once. An explicitly supplied old binding is validated and must match `window`.
The consumer preserves the exact proper-time factor `(b*b-a*a)/2`, known
`[0,1e10]` second history, source/state/clock/frame/support, explicit
`nb=8750/47 m^-3`, replay refusal and neutral inventory guard.

The native adapter requires the actual attested retained marginal; a general
fixture cannot acquire that provenance by copying labels. The inventory
interval returned after successful consumption is
`[max(0,N-H_neutral/W), dmax]`, where `H_neutral=(1085/94)*(99/100)`.
The existing consumer rejects a selected target outside the inventory bound;
the diagnostic does not weaken it. All four partitions are selected, so `p=0`.
The underlying PR112 API retains its more general partial-selection formula.

Returned output explicitly labels the cap/return as conditional, carries
`physical_activation=false`, and keeps actual K, exclusive He kernel, actual C
and D, outside response, donor work, EOS/T, absolute volume, full-source
physical native25, global physical error/budget/currency null. Saved RR and
retained photon ports remain separate and once-only.

## Authoring status

This implementation and README were authored without executing/importing the
scientific module, loading NPZ arrays, running tests or calling CAS. Root owns
the bounded execution ledger and the later acceptance decision. Source edits
alone are not test or science completion evidence.
