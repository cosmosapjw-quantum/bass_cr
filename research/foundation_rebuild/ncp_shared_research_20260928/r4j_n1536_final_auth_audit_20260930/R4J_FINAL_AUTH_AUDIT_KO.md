# R4J N1536 final authorization audit

Status: **N1536_ADAPTIVE_IMPLEMENTATION_READY__LIVE_CENSUS_AND_USER_AUTHORIZATION_REQUIRED**

Reviewed executable:
- commit `830b2849741f70078ac7bc779ee40c3f249c3fab`
- tree `922c976e5bb3aa8f6a87d96d482ea5b28e82eaf0`
- completed predecessor ZIP SHA256 `dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3`

Final preparation package:
- `N1536_ADAPTIVE_830b284_dc2ac87334a8_20260930.zip`
- bytes 31883158
- SHA256 `dc2ac87334a8748ae0fca732fc50acf906f66d541165dd95b7b20ce89528457b`
- ZIP CRC PASS; 60 manifest data members; 0 hash/size mismatches.

This audit independently materialized both the Google Drive and Dropbox copies. Their
bytes are identical and have the SHA256 above, so the final preparation package is
dual-provider RESTORE_VERIFIED.

Final authority pins:
- SOURCE_PINS `98569325f8c56ce176159a6bd01c712fd1d33b3d50ab7672f3b9392dcc46fcfb`
- QUERY_PLAN `ec893eb20a376affaf5742f256b82b83529de29dac812025cc899dd6cc04a5c8`
- USEFUL_PILOT_PLAN `a6ae00971235e6b4955603eb081969376479324abe84413b37ba7c24e309e349`
- FUTURE_AUTHORIZATION_TEMPLATE `f37c46734c2cd3d33335dbef13989a85d0f2a89d1c91686395d81e79d0d49e9b`

The stale authority field is closed. Admission/template now distinguish:
- worker_stages [8,16,32]
- pilot_query_counts [16,32,64]
- pilot_query_total 112
- post_pilot_remaining 1424.

Target NCP reports 62 passed, 0 failed, 0 skipped and a successful fresh extracted-package
self-contained replay with native calls 0 and nonce unconsumed. In this ChatGPT container
the 60 non-supervisor tests pass; the two supervisor timing tests are environment-limited
under Python 3.13.5 with unrelated artifact_tool startup instrumentation, whereas the
target BASS Python is pinned at 3.12.3.

Scientific contract is unchanged:
active required 1538, exact hits 2, new midpoints 1536, eventual union 3583,
useful raw cap 16896, no automatic parity/N3072/capture/all-bound/b-grid.

Wolfram rechecked p_ref=2.0000370430, p_self=2.0001860166,
d_ref(1536) forecast 1.646516e-7, d_self forecast 4.939207e-7, and the sufficient
actual reference-distance condition 3.413766918823635e-7. Forecasts are not gates.

Next action is read-only live census only. Exact ordered 32-CPU list, fresh authorization
ID, absolute deadline and cost scope remain user-controlled and unapproved. Proposal:
8/16/32 stages; 1 GiB/worker; 32 GiB worker-pool cap; >=36 GiB live available including
coordinator reserve; raw cap 16896; wall 28800 s; grace 60 s; operational cost ceiling
KRW 40000 including VAT on one existing High CPU-g3 host, no resize/new VM.

No N1536 native work was run by R4J.
