# Joint He event-region implementation

This unit implements the exact conditional region documented in ../theory/THEOREM.md. Inputs are finite exact int/Fraction atom masses and energies, a nonnegative cap and birth-bin labels. Every allowed positive low-high pair must be cross-bin. Singles and allowed two-leg diagonals are part of the measure.

`joint_region.Atom` aliases the pinned cross_flow Atom. A measure is a dictionary mapping a canonical one-key or sorted two-key tuple to a positive Fraction. `solve(atoms,K,cpp_executable=...)` obtains fresh general exact optima and a Region. `assemble(atoms,K,D,X,B_events,G_events=None,cpp_executable=...)` instead consumes independently certified scalar optima and saved native witnesses; callers must validate those certificate bindings. `mix_at(region,d,C)` constructs a complete rational witness and `metrics(atoms,K,measure)` verifies it directly. `domain_report` returns a concrete forbidden pair for a well-formed input outside the theorem domain.

Native source attestation stays in worker.py using one original consumer module. No new source normalization, physical K/kernel inference, RR computation, transport calculation or EOS closure is supplied. Scalars in the certificate are exact fraction strings; decimal display fields are presentation only.

Use the unique-run bounded commands in ../coding/C04_EXECUTION.md. The C++ executable is built locally by the compile mode; no toolchain installation is needed in the observed environment. It supports integer-scaled capacities below2^126 and refuses larger values. The exact native input, four reused dependencies and source snapshots are in the release archive. The full large certificates and binary are archive payloads; Git carries implementation, manifests and compact results.

Every verification stage records an actual run receipt. Build success alone is not a scientific acceptance. C6 uses the independent full-incidence oracle; C7 uses the native source and a separate raw-NPZ checker; C8 plots only accepted saved results. A completed unit closes its budget and does not automatically authorize another run.
