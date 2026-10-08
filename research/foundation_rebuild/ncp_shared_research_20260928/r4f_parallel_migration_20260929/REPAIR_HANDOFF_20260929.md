# R4F restore API repair after the stopped serial parent

The approved parent serial run `R4C-N768-BRIDGE-20260929-A1` was stopped by
SIGTERM at a verified PID/start time. Its recorded first failure was
`InterruptedError` from that planned signal. The parent partial archive is
preserved. The first R4F launcher call failed with shell exit 126 because the
shell file lacked an executable bit; it ran through `bash` without changing
source bytes. The R4F coordinator then exited before native parity with
`AttributeError: module 'continue_temporal' has no attribute
'restore_query_store'`. This error and its partial archive remain preserved
under `R4F-N768-MIGRATION-20260929-A1`.

This repair imports `restore_query_store` from the frozen
`qualified_provider` module, as the serial runner itself does, and checks
that all 1279 original archive pairs were restored. The frozen numerical
dependencies, native library, thresholds, context, and original archive are
unchanged. The old migration authorization has not been consumed before
native workers, but its attempted execution and first failure are retained;
it must not be reused to launch this changed code.

A non-native preflight using the actual stopped parent bytes verified the
complete frozen parent manifest, 1279 archive pairs, 1279 restored pairs,
two original required hits, 186 new parent midpoint pairs, 582 missing
required IDs, no orphans, and zero native calls. Focused tests: 28 passed.
No parity, pilot, parallel fill, or cache-only replay has yet run.

Any resumed migration requires explicit user approval of this new execution
commit/tree, a new authorization ID linked to both the original serial ID
and the failed R4F ID, the original cumulative deadline and cost envelope,
the same 22-raw-attempt parity cap, 8-query pilot, 8-worker/CPU 0-7/1 GiB
per-worker limits, and no automatic N1536 launch. The preserved parent is
read-only input; do not signal or restart the original serial run.
