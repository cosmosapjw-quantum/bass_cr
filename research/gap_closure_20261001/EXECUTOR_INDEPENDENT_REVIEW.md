# Independent G02/G03 executor review

**Accepted within the admission, resource, return and saved-matrix
postprocessing scope. No actionable defect remains in that scope.** This is
not a native-run approval or closure of G02/G03 scientific claims.

The reviewer implemented G07/G08/G09 but did not implement these executors.
Review began after the execution author declared the relevant modules stable;
final source identities are recorded in `EXECUTOR_INDEPENDENT_REVIEW.json`.
Historical admission, numerical worker, resource census and process-group
supervisor helpers were inspected as the unchanged baseline.

| Boundary | G02 | G03 |
|---|---|---|
| New qualified queries | 66 | 2, exactly z=−48,+48 a0 |
| Existing snapshots reused | 6 | 0 |
| Raw attempt ceiling | 726 | 22 |
| Maximum workers | 8 | 2 |
| RAM per worker | 1 GiB | 4 GiB |
| Wall limit | Explicit fresh proposal and absolute deadline | At most 900 s and absolute deadline |
| Threads | 1 | 1 |
| Authorization namespace | G02-FD | G03-STATIC48 |

Both require separate gap-specific approval environment values and the exact
proposal digest. A matching digest with the historical or other-gap environment
does not reach the native factory or launch a child. The fresh nonce namespace
cannot inherit an R4P0 or other-gap approval; exclusive durable consumption uses
the established OS-account-wide authorization store. A consumed nonce fails.
Preflight returns before consumption or native pool construction.

Exact source closure, a clean pinned commit/tree, immutable plan/resource
digests, exact executable path, stored B0 bank/input bytes and native
source/library/build hashes are checked before native construction. The worker
rechecks source/input identities and admits only the frozen query IDs/times.
NumPy 2.3.5, SciPy 1.17.0 and numerical thread environment values are required;
Python must satisfy the declared executable and version admission. The current
local test runtime is Python 3.12.14, not the historical native Python 3.13.5.

Live census checks CPU affinity/quota and workers×RAM plus 4 GiB headroom.
Worker initialization applies affinity and the address-space limit. Global
reservations occur before evaluator attempts, including failures. No automatic
worker scaling, retry, transport, G03-to-FD expansion or next-batch execution
is introduced. Monetary caps remain external controls, as explicitly reported
by the code.

Return publication is create-only. Qualified JSON/NPZ pairs are published before
postprocessing, so a diagnostic error preserves the qualified matrices. Failure
records cancel remaining dispatch. The supervisor starts a new isolated child
session, terminates only that owned process group on failure/deadline, records
teardown outcomes and packages partial evidence. This teardown preservation was
source-reviewed; no real native process group or kill exercise was launched.

The new G03 postprocessor checks payload identity, qualifying adjacent order and
selected-full/raw-cross agreement before diagnostics. It reconstructs each raw
cross resolution using the fixed order-20 same-center blocks, retains full
generalized spectra/eigenvectors, residuals and the dominant absolute-eigenvalue
cluster's S-orthogonal projector. It records both rho paths and adjacent rho
discrepancy. Qualified matrices remain available if a later rate calculation
fails. The final producer prefixes diagnostic paths with `diagnostics/` relative
to the return root. No state, P or Pdot is invented at the new tail points.
Sdot=D+D† remains explicitly assumed here, and adjacent agreement is labelled
internal consistency rather than a certified operator bound.

Independent execution comprised **24 targeted negative discriminators**: ten
for G02 and fourteen for G03. They reject old/cross-gap authorization, consumed
nonces, wrong query/raw/FD counts, thread/RAM/worker drift, expired deadlines and
G03 wall expansion. A G03 synthetic first failure invoked one fake compute,
reserved zero raw attempts and preserved both failure and cancellation receipts.
Additional source-closure checks passed for both modules and rejected a tampered
source hash while a native-loader trap remained unused. Native factory calls,
child launches, dlopen calls, native evaluations and authorization consumptions
in this independent review were all **zero**. No full suite was rerun.

The execution author subsequently reported the finalized combined suite as
**17/17 passing**: 10 G02, 4 G03 producer and 3 G03 rate tests, with no skips.
That includes the full synthetic collectors and create-only returns. This count
is author test evidence; root's final portable integration run is a separate
verification step. Changes after the independent negative checks were comments,
G03 schema/status labels and the diagnostic relative-path correction; the
final affected code was inspected before this review was frozen.

Live-host proposal preparation, fresh authority, host resource admission and
actual native execution remain unperformed. G02 derivative validation, G03 model
identification, continuous tail control and all capture/production ceilings
remain at their own gates.

The separate G12 normalization follow-up was also inspected. Its physical
contract now declares a common normalized IVP, exact shared state/S0 identities,
per-method actual initial-state/norm/distance receipts and a predeclared
initial-distance allowance. A null allowance blocks launch. This resolves the
documented contract mismatch; future runtime enforcement is still required.
The existing unit-norm synthetic benchmark was not rerun or changed.
