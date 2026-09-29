# R4H N1536 adaptive successor review

Status: **R4H_IMPLEMENTATION_REVIEW_CAUTION__NON_NATIVE_HARDENING_RECOMMENDED_BEFORE_N1536_AUTH**

Reviewed exact candidate:
- commit `e09c9391cc0864283aafe08d8cfba65efc261068`
- tree `ca099b7f408b4e53906d141c9a43c586aa1e4bd2`
- predecessor A2 ZIP SHA256 `dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3`

Portable implementation package:
- `N1536_ADAPTIVE_e09c939_20260929_2750fb62.zip`
- bytes 278320
- SHA256 `2750fb623c47ada00c33b8633f1fc6eadb87ab2c8b3282d6ece657cd5159ba53`
- ZIP CRC PASS
- 26 manifest members checked, 0 size/SHA mismatches

Fresh independent checks:
- core successor/adaptive Python files compile
- packaged `test_adaptive_workers.py`: 9 passed
- representative package Git blobs match the exact remote tree
- no native operator calculation or N1536 propagation performed

## Finding 1: scaling pilot metrology

Current useful pilot is one query per worker: 8/16/32 useful queries.

Historical completed N768 midpoint qualification is heterogeneous:
attempt-count distribution = {2:416, 3:102, 4:72, 5:56, 6:60, 7:40, 8:22},
mean 3.2838541666666665, Wolfram sample std 1.7615773835723983, CV about 0.5364.

The current deterministic stratification itself is good. Mapping prepared N1536
pilot locations to nearest completed N768 midpoints gives mean attempt counts:
8-worker=3.25, 16-worker=3.375, 32-worker=3.25, maximum deviation from the
historical overall mean about 2.78%.

Residual problem: each stage is only one scheduling wave, so pool/native-worker
startup and shutdown are not amortized as they will be in the 1480-query fill.
This can bias selection against higher worker counts.

Recommended narrow hardening before native authorization:
- use two useful queries per worker;
- stage counts 16/32/64, total 112 useful queries;
- all results retained in canonical scientific cache;
- remaining fill 1424 queries;
- keep hard max 32 workers and one numerical thread per worker;
- record raw-attempt/query and selected-resolution histogram in stage telemetry.

Wolfram planning arithmetic gives nominal sampling standard errors based on the
historical attempt spread:
- one-wave 8/16/32 samples: 0.623 / 0.440 / 0.311 attempts
- two-wave 16/32/64 samples: 0.440 / 0.311 / 0.220 attempts
Two-wave pilot is 7.2917% of the 1536 useful midpoint workload and is not wasted work.

## Finding 2: portable package test replay

The cloud implementation reports 60 passed / 0 failed / 0 skipped from the full
worktree.

However, a fresh attempt to run the packaged successor test directory after
extracting the backed-up package failed during collection with:
`ModuleNotFoundError: No module named 'reference_transport'`.

The package includes `metric_transport.py` but not its direct dependency
`reference_transport.py`. This is a backup/test-replay closure issue, not
evidence that the full-repository implementation test failed.

Before native authorization, update `make_preparation_package.py` so the extracted
package can replay its advertised focused non-native tests without borrowing source
files from the original worktree. Record
`SELF_CONTAINED_TEST_REPLAY_VERIFIED=true` only after that fresh extraction test
passes.

## Science and budget invariants

Unchanged:
- active required N1536 queries 1538
- inherited exact hits 2
- new midpoint IDs 1536
- eventual union 3583
- useful raw strict cap 16896
- optional parity remains separate
- N1536 gate uses both frozen distance screens + norm/operator qualification
- dual distance PASS is valid at N1536
- no automatic N3072/capture/all-bound/b-grid

Observed N768 second-order evidence remains:
- p_ref 2.0000370430175645
- p_self 2.000186016578518
- N1536 reference sufficient threshold 3.413766918823635e-7
- scheduling forecasts 1.646515993373354e-7 and 4.939207039229666e-7

## Next node

Run one non-native hardening loop only:
1. two-wave adaptive useful pilot (16/32/64 queries);
2. stage difficulty/startup telemetry;
3. self-contained package replay closure;
4. regenerate pilot/source-pin/authorization-template/package hashes;
5. fresh affected suite;
6. stop at `N1536_ADAPTIVE_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING`.

No native authorization is conferred by this document.
