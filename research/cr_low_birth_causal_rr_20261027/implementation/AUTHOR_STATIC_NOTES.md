# Prospective implementation and run interface

Unit `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`, frozen R1 contract SHA256
`0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210`.
This source-authoring pass performed **zero scientific executions, imports or
compilation**. Metadata reads, source edits, static cross-reading, JSON syntax
validation and SHA256 checks are not reported as numerical verification.
Root owns C4 admission, scientific invocation, stage publication and backups.

## Files and separation

`model.py` reads the exact saved low birth source and constructs new coefficients
using the common2022 constants and fixed100 K conditional inventory.
`uniformization.py` prepares positive Decimal80 Poisson weights and shares one
active-state power sweep between four phi2 states and four phi3 occupancies.
The weights are not renormalized and no negative output is clipped.
`ports.py` binds the source family, inventory, proper frame/history and finite
observation ownership. `primary.py` derives capture atoms, retained-photon atoms,
endpoint rates and separate source/cutoff/caloric/RR ledgers from those states.
Full source parent-ion chemistry remains absent, so full source native25 is null.

`controls.py` covers zero source, zero generator, one-state analytical capture,
common competing capture, zero-RR drift conservation, direct cutoff, finite-bin
prior survivors and adversarial state/ownership/support/normalization contracts.
It does not rerun any previous unit's accepted suite. The independently authored
`review/independent_reference.py` has no production imports.
`plot_saved.py` reads only a hash-pinned saved primary RESULT and writes one PNG
and one SVG; raw numerical files remain authoritative.

## Input bytes required before preparation

- Repo-relative source `research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json`,
  4394309 bytes, SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`.
- Unit-relative `inputs/reused/c23b/spectral_photo_source.py`,10712 bytes,
  SHA256 `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`.
- Unit-relative `inputs/reused/c23b/data/verner_photo.dat`,17760 bytes,
  SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.

The provider files are hashed but never imported. The explicit fit parameters
and equations retain their exact source qualification. New preparation creates
PREPARED.npz and PREPARATION.json once. Primary requires the latter's observed
SHA256 on its command line and checks each prepared array identity.

## Runner gate and prospective command sequence

Commands below are documentation only and have not been invoked. Working
directory is this unit. Root must first freeze EXECUTION_BUDGET.json with the
actual C4 host receipt and exact code-manifest hash. The code manifest must be
`{"unit": UNIT_ID, "files": [{"path": "implementation/model.py", "bytes": N,
"sha256": H}, ...]}` and cover every implementation/review `.py` file.
The resource proposal contains the required field names; its DRAFT status does
not authorize a worker. Named run allocations also fix the actual memory cap.

```text
python3 implementation/run_bounded.py --run-id prepare_v1 --cpu-reserve 3 -- python3 implementation/prepare.py --out runs/prepare_v1
python3 implementation/run_bounded.py --run-id controls_v1 --cpu-reserve 4 -- python3 implementation/controls.py --out runs/controls_v1
python3 implementation/run_bounded.py --run-id primary_v1 --cpu-reserve 10 -- python3 implementation/primary.py --prepared runs/prepare_v1 --preparation-sha256 ACTUAL_PREPARATION_SHA256 --out runs/primary_v1
python3 implementation/run_bounded.py --run-id independent_v1 --cpu-reserve 10 -- python3 review/independent_reference.py --primary runs/primary_v1 --out runs/independent_v1
python3 implementation/run_bounded.py --run-id plot_v1 --cpu-reserve 6 -- python3 implementation/plot_saved.py --result runs/primary_v1/RESULT.json --result-sha256 ACTUAL_PRIMARY_RESULT_SHA256 --out runs/plot_v1
```

The runner checks the same Python interpreter, frozen script path, exact named
CPU/memory reservation, owned output directory, C4 status/receipt/code hashes,
all existing immutable attempt debits and unresolved reservations. It supplies
CR_BOUNDED_UNIT, CR_BOUNDED_OUTDIR and CR_BOUNDED_ATTEMPT_ID to each worker.
Existing output directories are refused. Failed attempts require their own
preserved debit and an explicitly admitted unique successor, never overwrite.

## Static findings and prospective repairs

The runner adapts the exact PR109 implementation with SHA256
`724f816a9a90edbf8cfd9b582a0c12570aaf65cfecc80583e10f709cf1e5a56f` into a
separate40 CPU unit. It retains create-only preworker debit, maximum-per-attempt
reconciliation, UNKNOWN_NO_ACK blocking, cgroup clean-inactive memory estimate,
512 MiB upper limit and1 GiB reserve. Named allocation memory is now binding.
Aggregate descendant CPU polling is recorded as a non-atomic protective
estimate; the code does not claim a strict aggregate kernel CPU cap.

Static runner review identified and repaired newly adopted descendants appearing
after the last monitor poll, per-snapshot equality to the frozen manifest, and
binding the named memory allocation. Cleanup repeatedly discovers only this
coordinator's actual descendants, checks PID/start identity, terminates and
reaps them. The independent disposition is in `review/RUNNER_STATIC_REVIEW.json`;
runtime acceptance remains untested at this authoring stage.

Static production review identified that a positive Poisson tail subtotal and
the geometric bound on its unadded remainder were originally stored separately
while downstream bounds used only the subtotal. The bound fields now use their
sum, with the subtotal still retained for arithmetic identity diagnostics.
The correction is made before any execution and does not change the tolerances.
The exact-arithmetic truncation formula evaluated in ordinary floating point is
explicitly not an outward interval certificate.

Old independent_v1 preworker failure, old plot_v1 reservation failure and all
historical no-ack/lease records remain in their own immutable units. None of
their unused budget is carried. The new nominal proposal is 33 worker CPU seconds
plus 4 CPU seconds reserved for five coordinator invocations, leaving 3 of 40
for failure/repair accounting.
No measured new runtime or numerical PASS is asserted by this document.
