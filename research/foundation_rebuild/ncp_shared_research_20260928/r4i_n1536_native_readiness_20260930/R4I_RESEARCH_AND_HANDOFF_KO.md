# R4I: N1536 adaptive successor final pre-authorization audit

Status: **N1536_ADAPTIVE_IMPLEMENTATION_NEAR_READY__ONE_EVIDENCE_SCHEMA_FIX_BEFORE_NATIVE_AUTH**

Exact implementation under review:
- commit `5304df8bf696484671fe3db79500726ad608caf3`
- tree `2673055168818ce5ab8d2b6db213ed4ba6ff973a`
- completed predecessor archive SHA256 `dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3`

Independent portable verification:
- package `N1536_ADAPTIVE_5304df8_9a42219414ca_20260930.zip`
- bytes 31881249
- SHA256 `9a42219414ca120f9e4ef904fc759768eb123772bf9c6b9f705077978dccccc4`
- ZIP CRC PASS
- manifest verified files 60
- fresh extracted-package replay: 61 passed, 0 failed, 0 skipped
- external PYTHONPATH false
- native operator calls 0
- authorization nonce consumed false
- 13 R4G package source/test Git blobs independently matched the exact remote tree.

Adaptive pilot is now 8/16/32 workers with 16/32/64 useful queries, total112 and post-pilot remainder1424. Historical nearest-N768 attempt means for those three samples are 3.375, 3.25, 3.28125 versus overall 3.2838541667; max relative deviation about2.78%. The two-wave pilot therefore closes the earlier one-wave metrology concern well enough for execution planning, while remaining a scheduling measurement rather than scientific evidence.

Fresh finding: `successor.py::admission_scope` still emits `"pilot_queries": [8,16,32]`. These are worker stages after the hardening, not the actual pilot query counts [16,32,64]. Execution planning is already correct and hash-pinned, so this is not a physics/numerics defect. It is a P2 provenance/authority-schema inconsistency and should be corrected before native authorization.

Required final non-native repair:
- record `worker_stages=[8,16,32]`;
- record `pilot_query_counts=[16,32,64]`;
- record `pilot_query_total=112`;
- record `post_pilot_remaining=1424`;
- add the same explicit values to the future authorization template;
- add focused consistency assertions against ADAPTIVE_WORKER_POLICY and USEFUL_PILOT_PLAN;
- rerun final focused suite and self-contained extracted-package replay;
- regenerate exact commit/tree, source pins, query/pilot/template hashes and package.

Current exact pins:
- SOURCE_PINS SHA256 `cb3d85b6feaa8e7edf555cb8ff7cb2a4e0af351d74424129512fb7faccb668a8`
- query plan SHA256 `5dca79a2ebd9e81e0c16aa357ffff5f00bdbdcc838e2dcd73da6552cc133e0cf`
- useful pilot plan SHA256 `a6ae00971235e6b4955603eb081969376479324abe84413b37ba7c24e309e349`
- future authorization template SHA256 `69f925538317fb34a26d9dee5bed18a0a36ce82b2642262638a82c659e0b94e4`

Science/resource contract remains:
- active required1538; inherited hits2; new midpoints1536; union3583;
- useful raw strict cap16896; no automatic parity;
- workers8/16/32, hard max32, one numerical thread per worker;
- worker RAM1GiB, pool cap32GiB; live stage32 requires at least36GiB including coordinator reserve;
- no N3072/retry/reference rerun/capture/all-bound/b-grid.

Wolfram re-check:
- p_ref=2.0000370430
- p_self=2.0001860166
- predicted d_ref1536≈1.646516e-7
- predicted d_self1536≈4.939207e-7
- sufficient actual d_ref1536 for both distance screens: 3.413766918823635e-7
- same-8-worker whole-run projection≈3.731h

Literature context from SciSpace: strong-scaling/task-runtime work such as Merzky et al. IEEE TPDS 2022 (10.1109/TPDS.2021.3105994), Gillissen et al. 2023 (10.1007/978-3-031-22698-4_5), Grubel et al. 2015 (10.1109/CLUSTER.2015.119), and SciLance 2023 (10.1109/cluster52292.2023.00012) supports runtime profiling, explicit scheduler/startup overhead accounting and resource-aware adaptation for heterogeneous task workloads. It does not certify BASS physics.

No N1536 native computation was performed in this audit.

Detailed local handoff artifact:
`BASS_CR_R4I_N1536_NATIVE_READINESS_20260930_v1.zip`
SHA256 `249016f8bfe8cdba6d104265ff7499f81361f640d872684525bedf558e45873b`.
