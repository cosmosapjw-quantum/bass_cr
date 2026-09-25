# BASS_CR external audit handoff — R3M10 through R3M29

## Audit purpose and requested outcome

Audit how the selected fixed-target one-electron H+ + H(1s) TDL/AOCC research repository developed from its R3M10 imported checkpoint through R3M29, preserving run provenance, first failures, scientific claim ceilings, and backup/readback distinctions.

An independent, evidence-linked assessment of implementation/run integrity, numerical gate history, preserved failures, claim scope, and remaining blockers, ending with one justified next action. The audit must not promote production from a local reference or pair screen alone.

The selected production model, numerical targets, and current claim ceilings are recorded in the machine-readable [execution report](EXECUTION_REPORT.json). This handoff requests review of recorded work; it does not authorize new runs.

## Repository identity

- Root commit: `9da0011f93147ad8dddf166d3825de9a1c683ca9`
- Inventory snapshot branch and HEAD: `cr/r3m29-spatial-discretization-discriminator-20260924` / `8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f`
- First-parent commits: 81; all reachable commits: 92
- Uncommitted or untracked material was present at inventory generation: True (the report files were being created in this snapshot).

## Recorded project history

Each milestone links to its authoritative report/decision and its run folder or result file. The JSON report also links every file under `results/`, every recognized canonical local run-result JSON, the first-parent chronology, and all commits reachable from local refs. Packaged/readback copies remain in the full results catalog and are not counted as fresh local runs.

### R3M10 — Repository intake
Imported manifest-verified independent physical-problem checkpoint; repository root commit.
- [results/R3M10_LOCAL_RETURN_20260921](../../../results/R3M10_LOCAL_RETURN_20260921)
Actual run results:
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_baseline/result.json) — SHA-256 `f5dc3453fdeeeeadd7731fa8b53dc18bc3e4ffb146ca29ce9b1652072ab57f53`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_basis_large/result.json) — SHA-256 `75acf57730b0d145e13056fd2b54b2bb0bcb0f15c63d6825f2ececbda6b8f2fd`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_smoke/result.json) — SHA-256 `973317fa3569bf62cda5e030384e544998f93b0c6db13d0ff3bc33c2b0b5e10f`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_smoke_batched/result.json) — SHA-256 `47cd193eab2ef83bc6afdc3ac8d5c9d1a3a3d30d56a481824f96103ab41930d3`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_baseline_retry/result.json) — SHA-256 `93d97949f2a42c12d2c96a696ed7db3b7896417dbcb1fb9291497dda06119154`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_boxwide/result.json) — SHA-256 `2b9bb15452ff596752129a5fa12c04d6a820bd6559249de397846c799e15dbad`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_dt025/result.json) — SHA-256 `9c86338b5ea9a6a0a80d40da160b5ff0fd050839a594e6ddf0908b542f39299e`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_dx03125/result.json) — SHA-256 `6de60819e0690cd30b572a9accfba0cc2768b5b7b2ef98aaebfd8df10c007bca`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_plane25/result.json) — SHA-256 `47d046a72bef4eced4cfe3cabe886cd3fa9a489252bfad8cfdd876203c6b6e37`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_smoke/result.json) — SHA-256 `b09f14c01f57552fb67edcec71ba752eae48bf5247da89e22dbf94eea08be668`
- [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_z75/result.json) — SHA-256 `27e40d2827c9dd129f81e895f9f8cfae646d16ea8d070776ca41d3bd3ab203d7`

### R3M11 — Single-b baseline and controlled variables
Recorded imported scientific NO_GO and separated fixed-CAP/finite-span controls.
- [REPORT_KO.md](../../../docs/r3m11/REPORT_KO.md)
- [STATUS.json](../../../docs/r3m11/STATUS.json)
Actual run results:
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_baseline/result.json) — SHA-256 `f5dc3453fdeeeeadd7731fa8b53dc18bc3e4ffb146ca29ce9b1652072ab57f53`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_basis_large/result.json) — SHA-256 `75acf57730b0d145e13056fd2b54b2bb0bcb0f15c63d6825f2ececbda6b8f2fd`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_smoke/result.json) — SHA-256 `973317fa3569bf62cda5e030384e544998f93b0c6db13d0ff3bc33c2b0b5e10f`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_smoke_batched/result.json) — SHA-256 `47cd193eab2ef83bc6afdc3ac8d5c9d1a3a3d30d56a481824f96103ab41930d3`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_baseline_retry/result.json) — SHA-256 `93d97949f2a42c12d2c96a696ed7db3b7896417dbcb1fb9291497dda06119154`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_boxwide/result.json) — SHA-256 `2b9bb15452ff596752129a5fa12c04d6a820bd6559249de397846c799e15dbad`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_dt025/result.json) — SHA-256 `9c86338b5ea9a6a0a80d40da160b5ff0fd050839a594e6ddf0908b542f39299e`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_dx03125/result.json) — SHA-256 `6de60819e0690cd30b572a9accfba0cc2768b5b7b2ef98aaebfd8df10c007bca`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_plane25/result.json) — SHA-256 `47d046a72bef4eced4cfe3cabe886cd3fa9a489252bfad8cfdd876203c6b6e37`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_smoke/result.json) — SHA-256 `b09f14c01f57552fb67edcec71ba752eae48bf5247da89e22dbf94eea08be668`
- [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_z75/result.json) — SHA-256 `27e40d2827c9dd129f81e895f9f8cfae646d16ea8d070776ca41d3bd3ab203d7`

### R3M12 — Controlled single-b return
Added controlled comparisons and preserved the NO_GO decision and publication failures/receipts.
- [README_KO.md](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/README_KO.md)
- [results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921)
Actual run results:
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/controlled_parity/cpu/result.json) — SHA-256 `044fbe38a881f15e7ca3bd802235e2a511ed746729164c7e12e7a75e4ec7e9f5`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/controlled_parity/gpu/result.json) — SHA-256 `3d2fa585f80a50fc9e681f60fb8e964e2c567f73575a60cc4cc41618c2399b21`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_base/result.json) — SHA-256 `48386c8ce7960d12d7141a8f4e34427d29c56eddcbb3521d3c26c9c612c11d0b`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_dt025/result.json) — SHA-256 `25a42afd925a89a0b3e2675b39c005f2e069d5c58f325bf94a2857acd566a76a`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_exponent_only/result.json) — SHA-256 `9dd3c0f7c41c5cbe1ea6b4c2d3f5694d849423419c170d2b67be2e1c415714f0`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_radial_only/result.json) — SHA-256 `f17b9983a7d4a0c4c07fea1b600632ff51fa8b81eba61595862cad37f8783625`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_cap_base/result.json) — SHA-256 `1340f76fa8925537a2f03c59ee69540230bd1f88a03ec0f8c709d4b393745643`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_dt025/result.json) — SHA-256 `55d9cfcda588797bfd8dda2f53797160e6c1f8c7f0449de9d1e1b92f88eebf80`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_imag025/result.json) — SHA-256 `b239a63dd6f9f6ee29eb726736221a4295784257b6642b2c64dcb248045e3cf6`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_imag025_long/result.json) — SHA-256 `278e638b7fa7b348790ff4786ed8bd3ee6084968197eb6e98a126a27a040fa45`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_refined_dx025/result.json) — SHA-256 `e431a605d268ec208bb2009418772b85aacbd33ff6444df4bd9a3cba6dacec9d`
- [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_refined_dx03125/result.json) — SHA-256 `82200788151d34692ef3c78bd84a4f21e9a8cf78c6f098504ed85eded2404b59`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/controlled_parity/cpu/result.json) — SHA-256 `044fbe38a881f15e7ca3bd802235e2a511ed746729164c7e12e7a75e4ec7e9f5`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/controlled_parity/gpu/result.json) — SHA-256 `3d2fa585f80a50fc9e681f60fb8e964e2c567f73575a60cc4cc41618c2399b21`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_base/result.json) — SHA-256 `48386c8ce7960d12d7141a8f4e34427d29c56eddcbb3521d3c26c9c612c11d0b`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_dt025/result.json) — SHA-256 `25a42afd925a89a0b3e2675b39c005f2e069d5c58f325bf94a2857acd566a76a`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_exponent_only/result.json) — SHA-256 `9dd3c0f7c41c5cbe1ea6b4c2d3f5694d849423419c170d2b67be2e1c415714f0`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_radial_only/result.json) — SHA-256 `f17b9983a7d4a0c4c07fea1b600632ff51fa8b81eba61595862cad37f8783625`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_cap_base/result.json) — SHA-256 `1340f76fa8925537a2f03c59ee69540230bd1f88a03ec0f8c709d4b393745643`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_dt025/result.json) — SHA-256 `55d9cfcda588797bfd8dda2f53797160e6c1f8c7f0449de9d1e1b92f88eebf80`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_imag025/result.json) — SHA-256 `b239a63dd6f9f6ee29eb726736221a4295784257b6642b2c64dcb248045e3cf6`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_imag025_long/result.json) — SHA-256 `278e638b7fa7b348790ff4786ed8bd3ee6084968197eb6e98a126a27a040fa45`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_refined_dx025/result.json) — SHA-256 `e431a605d268ec208bb2009418772b85aacbd33ff6444df4bd9a3cba6dacec9d`
- [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_refined_dx03125/result.json) — SHA-256 `82200788151d34692ef3c78bd84a4f21e9a8cf78c6f098504ed85eded2404b59`

### R3M13 — Preparation diagnostics
Added conditional preparation-pair diagnostics and transfer bounds; no new production collision or cross section.
- [REPORT_KO.md](../../../docs/r3m13/REPORT_KO.md)
- [STATUS.json](../../../docs/r3m13/STATUS.json)

### R3M14 — Preparation-pair gate and collision
Preparation-pair NO_GO; collision comparison passed only as a pair screen. Production remains NO_GO.
- [REPORT_KO.md](../../../docs/r3m14/production/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m14/production/FINAL_DECISION.json)
Actual run results:
- [result.json](../../../results/R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN/collision0125/result.json) — SHA-256 `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd`
- [result.json](/mnt/sn850x2t/bass_cr_r3m14_20260922/collision0125/result.json) — SHA-256 `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd`
- [result.json](/mnt/sn850x2t/bass_cr_r3m14_20260922/production_return/collision0125/result.json) — SHA-256 `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd`

### R3M15 — Controlled spatial matrix
Three A/B/C collisions and preparation controls recorded; scientific convergence NO_GO.
- [REPORT_KO.md](../../../docs/r3m15/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m15/FINAL_DECISION.json)
Actual run results:
- [result.json](../../../results/R3M15/A/collision/result.json) — SHA-256 `42a76cff7b9dad4354a0c9e059696108ebb37151f7554a0a5b5895849d4666ce`
- [result.json](../../../results/R3M15/B/collision/result.json) — SHA-256 `23da11c5b877d133db1ddaaeff4b52081c22f930e752aec608e13966d454a1d7`
- [result.json](../../../results/R3M15/C/collision/result.json) — SHA-256 `997061fd42a1819228c71dac23f19d55560f80dc6a19bf2430273077e417a94a`
- [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/A/collision/result.json) — SHA-256 `42a76cff7b9dad4354a0c9e059696108ebb37151f7554a0a5b5895849d4666ce`
- [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/B/collision/result.json) — SHA-256 `23da11c5b877d133db1ddaaeff4b52081c22f930e752aec608e13966d454a1d7`
- [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/C/collision/result.json) — SHA-256 `997061fd42a1819228c71dac23f19d55560f80dc6a19bf2430273077e417a94a`

### R3M16 — Coulomb/FFT h-dt study
Two A1/B1 collisions and target-only diagnostics; time refinement remained open.
- [REPORT_KO.md](../../../docs/r3m16/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m16/FINAL_DECISION.json)
Actual run results:
- [A1_result.json](../../../results/R3M16/collisions/A1_result.json) — SHA-256 `c2f19c93020f11e9e56e1045f733201de826043aaf6928a74a7871d154e0c775`
- [B1_result.json](../../../results/R3M16/collisions/B1_result.json) — SHA-256 `ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f`
- [result.json](/mnt/sn850x2t/bass_cr_r3m16_20260922/A1/collision/result.json) — SHA-256 `c2f19c93020f11e9e56e1045f733201de826043aaf6928a74a7871d154e0c775`
- [result.json](/mnt/sn850x2t/bass_cr_r3m16_20260922/B1/collision/result.json) — SHA-256 `ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f`

### R3M17 — Production validation infrastructure
Added independent time reference, immutable checkpoint handling and execution contracts; production HOLD.
- [REPORT_KO.md](../../../docs/r3m17/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m17/FINAL_DECISION.json)
Actual run results:
- [result.json](../../../results/R3M17/aocc/smoke_matrices/result.json) — SHA-256 `e61a2bca7428a4b4327dd3122500f0f1f6ced6d4defbfaed00cb04ae077aabe1`

### R3M18 — B2 temporal refinement
Recorded B2 and channel changes exceeding the 0.10% screen; temporal gate remained open.
- [REPORT_KO.md](../../../docs/r3m18/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m18/FINAL_DECISION.json)
Actual run results:
- [result.json](/mnt/sn850x2t/bass_cr_r3m18_20260923/B2/collision/result.json) — SHA-256 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`
- [result.json](/mnt/sn850x2t/bass_cr_r3m18_20260923/B2/generations/g003586/result.json) — SHA-256 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`

### R3M19 — Full-H diagnostics and work precision
Time refinement remained open; bounded full-H diagnostics and CPU performance candidates were recorded.
- [REPORT_KO.md](../../../docs/r3m19/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m19/FINAL_DECISION.json)
Actual run results:
- [RESULT.json](../../../results/R3M19/performance/cpu_native/RESULT.json) — SHA-256 `9fbd3dbd1a11f900e4a91232c3c59095c59c54faa2fe36a467ae453e3860561f`
- [RESULT.json](../../../results/R3M19/performance/cpu_scipy_w1/RESULT.json) — SHA-256 `9805c61f4eb391a6f9db5742c280f967fb95cb8722793715a68ef2e26464872b`
- [RESULT.json](../../../results/R3M19/performance/cpu_scipy_w4/RESULT.json) — SHA-256 `96f56c4b703902a532d7f67176f28bd20e3e99b1c400950454a0ac42b61cdd74`

### R3M20 — Short-window GPU reference/work precision
Ran bounded diagnostics on retained B2 checkpoints; scope remained local Strang reference, not production.
- [REPORT_KO.md](../../../docs/r3m20/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m20/FINAL_DECISION.json)
Actual run results:
- [result.json](../../../results/R3M20_N1/intake/collision/result.json) — SHA-256 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`
- [RESULT.json](../../../results/R3M20_N1/performance/cpu_native_retry1/RESULT.json) — SHA-256 `27483261619668259bf3f27e581b0b02d1a8bf1b268de24ef5735df6e2e1f00f`
- [RESULT.json](../../../results/R3M20_N1/performance/cpu_scipy_w1_retry1/RESULT.json) — SHA-256 `2ea0adf56261d794e7cd5f3fe74c4ae57022c0ec460d14a2046488bcfb66e5eb`
- [RESULT.json](../../../results/R3M20_N1/performance/cpu_scipy_w4_retry1/RESULT.json) — SHA-256 `ca913e97350ff5b42c5e8ef491eb516250bffd96d1637c4967728e1d7aed03ff`
- [RESULT.json](../../../results/R3M20_N1/performance/gpu_larger_retry2/RESULT.json) — SHA-256 `d8aa4a828c20867275eb889571dcdd764e44fa7049f9c13a9ec328d0a8b981ea`
- [RESULT.json](../../../results/R3M20_N1/performance/gpu_medium_retry2/RESULT.json) — SHA-256 `94ada5c69089b9be0d0ddff18c04ada2cb07c7f944570205d6bab3b4c7bf6266`

### R3M21 — Incoming CF4 reference resolution attempt
Incoming B2 CPU/GPU reference ladder did not satisfy its strict oracle gate; first failure retained.
- [REPORT_KO.md](../../../docs/r3m21/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m21/FINAL_DECISION.json)

### R3M22 — Incoming full-H inner action reference
Bounded GPU reference retry and strict CPU oracle evidence; unresolved historical failures retained.
- [REPORT_KO.md](../../../docs/r3m22/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m22/FINAL_DECISION.json)
Actual run results:
- [GPU_RESULT.json](../../../results/R3M22/GPU_RESULT.json) — SHA-256 `6adbe0495629f70e5da50f2c3ac1cfd2cb2d3ad2bdd116672df841bad1871cc4`

### R3M23 — Closest/outgoing B2 cross-window work precision
Two retained-window comparisons passed only for REFERENCE_FOR_STRANG; no global time or production promotion.
- [REPORT_KO.md](../../../docs/r3m23/REPORT_KO.md)
- [FINAL_DECISION.json](../../../results/R3M23/FINAL_DECISION.json)
Actual run results:
- [GPU_RESULT.json](../../../results/R3M23/GPU_RESULT.json) — SHA-256 `2a1a2a9a3d346570e75540bd167cb512c8ab75e62d657e03724312832ec92a5a`

### R3M24 — Local integration and bounded reference
Local integration suite and two B2 windows; typed result scope remained REFERENCE_FOR_STRANG.
- [LOCAL_INTEGRATION_REPORT_KO.md](../../../docs/r3m24/LOCAL_INTEGRATION_REPORT_KO.md)
- [results/R3M24_LOCAL_20260924T1532KST](../../../results/R3M24_LOCAL_20260924T1532KST)
Actual run results:
- [RESULT.json](../../../results/R3M24_LOCAL_20260924T1532KST/ATTEMPT/windows/closest/RESULT.json) — SHA-256 `e88dc5f7166a2f7ad38bb7985434bd85a5ec573594bffc408604bd8e040d69bf`
- [RESULT.json](../../../results/R3M24_LOCAL_20260924T1532KST/ATTEMPT/windows/outgoing/RESULT.json) — SHA-256 `6aea49967b129b35219fcdfe70e645033bdd2d3b7d91730be6898d554eebaa5a`

### R3M25 — Physical t=0 event window
Four-step local event window passed its local CF4/Strang-scale checks; no global time certificate.
- [REPORT_KO.md](../../../docs/r3m25/REPORT_KO.md)
- [RESULT.json](../../../results/R3M25/ATTEMPT_2/RESULT.json)
Actual run results:
- [RESULT.json](../../../results/R3M25/ATTEMPT_2/RESULT.json) — SHA-256 `a51828e724c6636c3522aee7c4ecdb02435d9031947bf39d9ccde1fe195239ff`

### R3M26 — Model foundation and prospective convergence strategy
Completed model/units/observable and prospective numerical criteria; production remains HOLD.
- [REPORT_KO.md](../../../docs/r3m26/REPORT_KO.md)
- [FINAL_DECISION.json](../../../docs/r3m26/FINAL_DECISION.json)
Actual run results:
- [RESULT.json](../../../results/R3M26/foundation/RESULT.json) — SHA-256 `e92a0bdf24418198e4565fce5c848248a14046e6104d545d763f63edc7e96f88`
- [RESULT_FINAL.json](../../../results/R3M26/foundation/RESULT_FINAL.json) — SHA-256 `71fc551d5800182d381f7576b3d3f6929b25fd0af2b04edeff4286b9d323bbc7`

### R3M27 — B3 full collision and frozen time estimate
One preparation and one witnessed 7172-step B3 collision; fixed-h selected-span temporal estimate validated, noncertified.
- [REPORT_KO.md](../../../docs/r3m27/REPORT_KO.md)
- [B3_TEMPORAL_EVALUATION.json](../../../results/R3M27/B3_TEMPORAL_EVALUATION.json)
Actual run results:
- [result.json](/mnt/sn850x2t/bass_cr_r3m27_20260924/B3/collision/result.json) — SHA-256 `7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce`
- [result.json](/mnt/sn850x2t/bass_cr_r3m27_20260924/B3/generations/g007172/result.json) — SHA-256 `7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce`

### R3M28 — A3 same-horizon spatial pair
One preparation and one witnessed 7172-step A3 collision; P1-P3 pair screen NO_GO at 3.03-3.29%; continuum spatial error remains open.
- [REPORT_KO.md](../../../docs/r3m28/REPORT_KO.md)
- [SPATIAL_EVALUATION.json](../../../results/R3M28/SPATIAL_EVALUATION.json)
Actual run results:
- [result.json](/mnt/sn850x2t/bass_cr_r3m28_20260924/A3/collision/result.json) — SHA-256 `e03295595ca64e90bd4c8c78ac208f4c4e1de5c59a77db930fa2d3ef68339c14`
- [result.json](/mnt/sn850x2t/bass_cr_r3m28_20260924/A3/generations/g007172/result.json) — SHA-256 `e03295595ca64e90bd4c8c78ac208f4c4e1de5c59a77db930fa2d3ef68339c14`

### R3M29 — Point-Coulomb cell and phase discriminator
Local singular-cell bias and production-order phase histogram prioritized cell-average as a short-window candidate; causality and production spatial budget remain open.
- [REPORT_KO.md](../../../docs/r3m29/REPORT_KO.md)
- [RESULT_V3.json](../../../results/R3M29/RESULT_V3.json)
Actual run results:
- [RESULT.json](../../../results/R3M29/RESULT.json) — SHA-256 `7a9fef9ad52faa07afd61f098b1a9b5e61d15d5c86a3f452e8a1ea7c39eec551`
- [RESULT_V2.json](../../../results/R3M29/RESULT_V2.json) — SHA-256 `2fed3bde2712a4b33b7c825d923739aefb06da0714fcc08ae389c8b4e59f5132`
- [RESULT_V3.json](../../../results/R3M29/RESULT_V3.json) — SHA-256 `3963fea9d7c33b76d3946ce533d159af09ad1a15d8adc28ca66cb337055626e9`

## Actual local run-result files

The following table lists recognized result JSONs in the repository and canonical local run roots. Explicit readback mirrors and packaged copies are excluded from this table; they remain indexed in the full results tree when stored in the repository. The complete evidence inventory, with size and SHA-256, is in the linked machine-readable report.

| Result file | SHA-256 |
|---|---|
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_baseline/result.json) | `f5dc3453fdeeeeadd7731fa8b53dc18bc3e4ffb146ca29ce9b1652072ab57f53` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_basis_large/result.json) | `75acf57730b0d145e13056fd2b54b2bb0bcb0f15c63d6825f2ececbda6b8f2fd` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_smoke/result.json) | `973317fa3569bf62cda5e030384e544998f93b0c6db13d0ff3bc33c2b0b5e10f` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/aocc_smoke_batched/result.json) | `47cd193eab2ef83bc6afdc3ac8d5c9d1a3a3d30d56a481824f96103ab41930d3` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_baseline_retry/result.json) | `93d97949f2a42c12d2c96a696ed7db3b7896417dbcb1fb9291497dda06119154` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_boxwide/result.json) | `2b9bb15452ff596752129a5fa12c04d6a820bd6559249de397846c799e15dbad` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_dt025/result.json) | `9c86338b5ea9a6a0a80d40da160b5ff0fd050839a594e6ddf0908b542f39299e` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_dx03125/result.json) | `6de60819e0690cd30b572a9accfba0cc2768b5b7b2ef98aaebfd8df10c007bca` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_plane25/result.json) | `47d046a72bef4eced4cfe3cabe886cd3fa9a489252bfad8cfdd876203c6b6e37` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_smoke/result.json) | `b09f14c01f57552fb67edcec71ba752eae48bf5247da89e22dbf94eea08be668` |
| [result.json](../../../results/R3M10_LOCAL_RETURN_20260921/runs/tdl_z75/result.json) | `27e40d2827c9dd129f81e895f9f8cfae646d16ea8d070776ca41d3bd3ab203d7` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/controlled_parity/cpu/result.json) | `044fbe38a881f15e7ca3bd802235e2a511ed746729164c7e12e7a75e4ec7e9f5` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/controlled_parity/gpu/result.json) | `3d2fa585f80a50fc9e681f60fb8e964e2c567f73575a60cc4cc41618c2399b21` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_base/result.json) | `48386c8ce7960d12d7141a8f4e34427d29c56eddcbb3521d3c26c9c612c11d0b` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_dt025/result.json) | `25a42afd925a89a0b3e2675b39c005f2e069d5c58f325bf94a2857acd566a76a` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_exponent_only/result.json) | `9dd3c0f7c41c5cbe1ea6b4c2d3f5694d849423419c170d2b67be2e1c415714f0` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/aocc_radial_only/result.json) | `f17b9983a7d4a0c4c07fea1b600632ff51fa8b81eba61595862cad37f8783625` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_cap_base/result.json) | `1340f76fa8925537a2f03c59ee69540230bd1f88a03ec0f8c709d4b393745643` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_dt025/result.json) | `55d9cfcda588797bfd8dda2f53797160e6c1f8c7f0449de9d1e1b92f88eebf80` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_imag025/result.json) | `b239a63dd6f9f6ee29eb726736221a4295784257b6642b2c64dcb248045e3cf6` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_imag025_long/result.json) | `278e638b7fa7b348790ff4786ed8bd3ee6084968197eb6e98a126a27a040fa45` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_refined_dx025/result.json) | `e431a605d268ec208bb2009418772b85aacbd33ff6444df4bd9a3cba6dacec9d` |
| [result.json](../../../results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/runs/tdl_refined_dx03125/result.json) | `82200788151d34692ef3c78bd84a4f21e9a8cf78c6f098504ed85eded2404b59` |
| [result.json](../../../results/R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN/collision0125/result.json) | `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd` |
| [result.json](../../../results/R3M15/A/collision/result.json) | `42a76cff7b9dad4354a0c9e059696108ebb37151f7554a0a5b5895849d4666ce` |
| [result.json](../../../results/R3M15/B/collision/result.json) | `23da11c5b877d133db1ddaaeff4b52081c22f930e752aec608e13966d454a1d7` |
| [result.json](../../../results/R3M15/C/collision/result.json) | `997061fd42a1819228c71dac23f19d55560f80dc6a19bf2430273077e417a94a` |
| [A1_result.json](../../../results/R3M16/collisions/A1_result.json) | `c2f19c93020f11e9e56e1045f733201de826043aaf6928a74a7871d154e0c775` |
| [B1_result.json](../../../results/R3M16/collisions/B1_result.json) | `ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f` |
| [result.json](../../../results/R3M17/aocc/smoke_matrices/result.json) | `e61a2bca7428a4b4327dd3122500f0f1f6ced6d4defbfaed00cb04ae077aabe1` |
| [RESULT.json](../../../results/R3M19/performance/cpu_native/RESULT.json) | `9fbd3dbd1a11f900e4a91232c3c59095c59c54faa2fe36a467ae453e3860561f` |
| [RESULT.json](../../../results/R3M19/performance/cpu_scipy_w1/RESULT.json) | `9805c61f4eb391a6f9db5742c280f967fb95cb8722793715a68ef2e26464872b` |
| [RESULT.json](../../../results/R3M19/performance/cpu_scipy_w4/RESULT.json) | `96f56c4b703902a532d7f67176f28bd20e3e99b1c400950454a0ac42b61cdd74` |
| [result.json](../../../results/R3M20_N1/intake/collision/result.json) | `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc` |
| [RESULT.json](../../../results/R3M20_N1/performance/cpu_native_retry1/RESULT.json) | `27483261619668259bf3f27e581b0b02d1a8bf1b268de24ef5735df6e2e1f00f` |
| [RESULT.json](../../../results/R3M20_N1/performance/cpu_scipy_w1_retry1/RESULT.json) | `2ea0adf56261d794e7cd5f3fe74c4ae57022c0ec460d14a2046488bcfb66e5eb` |
| [RESULT.json](../../../results/R3M20_N1/performance/cpu_scipy_w4_retry1/RESULT.json) | `ca913e97350ff5b42c5e8ef491eb516250bffd96d1637c4967728e1d7aed03ff` |
| [RESULT.json](../../../results/R3M20_N1/performance/gpu_larger_retry2/RESULT.json) | `d8aa4a828c20867275eb889571dcdd764e44fa7049f9c13a9ec328d0a8b981ea` |
| [RESULT.json](../../../results/R3M20_N1/performance/gpu_medium_retry2/RESULT.json) | `94ada5c69089b9be0d0ddff18c04ada2cb07c7f944570205d6bab3b4c7bf6266` |
| [GPU_RESULT.json](../../../results/R3M22/GPU_RESULT.json) | `6adbe0495629f70e5da50f2c3ac1cfd2cb2d3ad2bdd116672df841bad1871cc4` |
| [GPU_RESULT.json](../../../results/R3M23/GPU_RESULT.json) | `2a1a2a9a3d346570e75540bd167cb512c8ab75e62d657e03724312832ec92a5a` |
| [RESULT.json](../../../results/R3M24_LOCAL_20260924T1532KST/ATTEMPT/windows/closest/RESULT.json) | `e88dc5f7166a2f7ad38bb7985434bd85a5ec573594bffc408604bd8e040d69bf` |
| [RESULT.json](../../../results/R3M24_LOCAL_20260924T1532KST/ATTEMPT/windows/outgoing/RESULT.json) | `6aea49967b129b35219fcdfe70e645033bdd2d3b7d91730be6898d554eebaa5a` |
| [RESULT.json](../../../results/R3M25/ATTEMPT_2/RESULT.json) | `a51828e724c6636c3522aee7c4ecdb02435d9031947bf39d9ccde1fe195239ff` |
| [RESULT.json](../../../results/R3M26/foundation/RESULT.json) | `e92a0bdf24418198e4565fce5c848248a14046e6104d545d763f63edc7e96f88` |
| [RESULT_FINAL.json](../../../results/R3M26/foundation/RESULT_FINAL.json) | `71fc551d5800182d381f7576b3d3f6929b25fd0af2b04edeff4286b9d323bbc7` |
| [RESULT.json](../../../results/R3M29/RESULT.json) | `7a9fef9ad52faa07afd61f098b1a9b5e61d15d5c86a3f452e8a1ea7c39eec551` |
| [RESULT_V2.json](../../../results/R3M29/RESULT_V2.json) | `2fed3bde2712a4b33b7c825d923739aefb06da0714fcc08ae389c8b4e59f5132` |
| [RESULT_V3.json](../../../results/R3M29/RESULT_V3.json) | `3963fea9d7c33b76d3946ce533d159af09ad1a15d8adc28ca66cb337055626e9` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_baseline/result.json) | `f5dc3453fdeeeeadd7731fa8b53dc18bc3e4ffb146ca29ce9b1652072ab57f53` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_basis_large/result.json) | `75acf57730b0d145e13056fd2b54b2bb0bcb0f15c63d6825f2ececbda6b8f2fd` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_smoke/result.json) | `973317fa3569bf62cda5e030384e544998f93b0c6db13d0ff3bc33c2b0b5e10f` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/aocc_smoke_batched/result.json) | `47cd193eab2ef83bc6afdc3ac8d5c9d1a3a3d30d56a481824f96103ab41930d3` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_baseline_retry/result.json) | `93d97949f2a42c12d2c96a696ed7db3b7896417dbcb1fb9291497dda06119154` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_boxwide/result.json) | `2b9bb15452ff596752129a5fa12c04d6a820bd6559249de397846c799e15dbad` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_dt025/result.json) | `9c86338b5ea9a6a0a80d40da160b5ff0fd050839a594e6ddf0908b542f39299e` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_dx03125/result.json) | `6de60819e0690cd30b572a9accfba0cc2768b5b7b2ef98aaebfd8df10c007bca` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_plane25/result.json) | `47d046a72bef4eced4cfe3cabe886cd3fa9a489252bfad8cfdd876203c6b6e37` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_smoke/result.json) | `b09f14c01f57552fb67edcec71ba752eae48bf5247da89e22dbf94eea08be668` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m11_20260921/runs/tdl_z75/result.json) | `27e40d2827c9dd129f81e895f9f8cfae646d16ea8d070776ca41d3bd3ab203d7` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/controlled_parity/cpu/result.json) | `044fbe38a881f15e7ca3bd802235e2a511ed746729164c7e12e7a75e4ec7e9f5` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/controlled_parity/gpu/result.json) | `3d2fa585f80a50fc9e681f60fb8e964e2c567f73575a60cc4cc41618c2399b21` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_base/result.json) | `48386c8ce7960d12d7141a8f4e34427d29c56eddcbb3521d3c26c9c612c11d0b` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_dt025/result.json) | `25a42afd925a89a0b3e2675b39c005f2e069d5c58f325bf94a2857acd566a76a` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_exponent_only/result.json) | `9dd3c0f7c41c5cbe1ea6b4c2d3f5694d849423419c170d2b67be2e1c415714f0` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/aocc_radial_only/result.json) | `f17b9983a7d4a0c4c07fea1b600632ff51fa8b81eba61595862cad37f8783625` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_cap_base/result.json) | `1340f76fa8925537a2f03c59ee69540230bd1f88a03ec0f8c709d4b393745643` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_dt025/result.json) | `55d9cfcda588797bfd8dda2f53797160e6c1f8c7f0449de9d1e1b92f88eebf80` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_imag025/result.json) | `b239a63dd6f9f6ee29eb726736221a4295784257b6642b2c64dcb248045e3cf6` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_imag025_long/result.json) | `278e638b7fa7b348790ff4786ed8bd3ee6084968197eb6e98a126a27a040fa45` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_refined_dx025/result.json) | `e431a605d268ec208bb2009418772b85aacbd33ff6444df4bd9a3cba6dacec9d` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m12_20260921/return/runs/tdl_refined_dx03125/result.json) | `82200788151d34692ef3c78bd84a4f21e9a8cf78c6f098504ed85eded2404b59` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m14_20260922/collision0125/result.json) | `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m14_20260922/production_return/collision0125/result.json) | `83c674c3401cc5ab550ebb48c9b76e280a5b8565874d5a4822326fcdf50fffbd` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/A/collision/result.json) | `42a76cff7b9dad4354a0c9e059696108ebb37151f7554a0a5b5895849d4666ce` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/B/collision/result.json) | `23da11c5b877d133db1ddaaeff4b52081c22f930e752aec608e13966d454a1d7` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m15_20260922/C/collision/result.json) | `997061fd42a1819228c71dac23f19d55560f80dc6a19bf2430273077e417a94a` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m16_20260922/A1/collision/result.json) | `c2f19c93020f11e9e56e1045f733201de826043aaf6928a74a7871d154e0c775` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m16_20260922/B1/collision/result.json) | `ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m18_20260923/B2/collision/result.json) | `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m18_20260923/B2/generations/g003586/result.json) | `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m27_20260924/B3/collision/result.json) | `7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m27_20260924/B3/generations/g007172/result.json) | `7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m28_20260924/A3/collision/result.json) | `e03295595ca64e90bd4c8c78ac208f4c4e1de5c59a77db930fa2d3ef68339c14` |
| [result.json](/mnt/sn850x2t/bass_cr_r3m28_20260924/A3/generations/g007172/result.json) | `e03295595ca64e90bd4c8c78ac208f4c4e1de5c59a77db930fa2d3ef68339c14` |

## Local Dropbox backups

These links point to the backed-up files on this computer. Each file is linked individually so the reviewer can open it without extra context. Consult its linked in-repository receipt for backup tier and restore status.

- [BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1.zip) — 76059 bytes
- [BASS_CR_R3M11_CONTROLLED_REFINEMENT_PACKAGE_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M11_CONTROLLED_REFINEMENT_PACKAGE_20260921_v1.zip) — 82815 bytes
- [BASS_CR_R3M11_CP0_REPO_INTAKE_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M11_CP0_REPO_INTAKE_20260921_v1.zip) — 10329 bytes
- [BASS_CR_R3M11_CP1_CONTROLLED_KERNEL_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M11_CP1_CONTROLLED_KERNEL_20260921_v1.zip) — 50015 bytes
- [BASS_CR_R3M11_DUAL_BACKUP_AND_REPO_RECEIPT_20260921_v1.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M11_DUAL_BACKUP_AND_REPO_RECEIPT_20260921_v1.json) — 3678 bytes
- [BASS_CR_R3M11_REPO_REPAIR_AND_HANDOFF_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M11_REPO_REPAIR_AND_HANDOFF_20260921_v1.zip) — 2916241 bytes
- [BASS_CR_R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921_v1.tar.gz](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921_v1.tar.gz) — 1231876036 bytes
- [BASS_CR_R3M13_CP0_SOURCE_FREEZE_20260922_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M13_CP0_SOURCE_FREEZE_20260922_v1.zip) — 19274 bytes
- [BASS_CR_R3M13_CP1_PREPARATION_DIAGNOSTICS_20260922_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M13_CP1_PREPARATION_DIAGNOSTICS_20260922_v1.zip) — 26043 bytes
- [BASS_CR_R3M13_DUAL_BACKUP_RECEIPT_20260922_v1.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M13_DUAL_BACKUP_RECEIPT_20260922_v1.json) — 5500 bytes
- [BASS_CR_R3M13_PREPARATION_TRANSFER_20260922_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M13_PREPARATION_TRANSFER_20260922_v1.zip) — 2333455 bytes
- [BASS_CR_R3M14_PREFLIGHT_TRANSFER_20260922_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M14_PREFLIGHT_TRANSFER_20260922_v1.zip) — 16074 bytes
- [BASS_CR_R3M14_PREFLIGHT_TRANSFER_20260922_v2.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M14_PREFLIGHT_TRANSFER_20260922_v2.zip) — 20655 bytes
- [BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1.tar.zst) — 1465397891 bytes
- [BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1_ARCHIVE_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1_ARCHIVE_MANIFEST.json) — 19957 bytes
- [BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1_DRIVE_MULTIPART_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1_DRIVE_MULTIPART_MANIFEST.json) — 39744 bytes
- [BASS_CR_R3M15_A_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_A_20260922_v1.tar.zst) — 969313741 bytes
- [BASS_CR_R3M15_A_20260922_v1_DRIVE_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_A_20260922_v1_DRIVE_MANIFEST.json) — 20155 bytes
- [BASS_CR_R3M15_B_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_B_20260922_v1.tar.zst) — 1905765238 bytes
- [BASS_CR_R3M15_B_20260922_v1_DRIVE_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_B_20260922_v1_DRIVE_MANIFEST.json) — 46086 bytes
- [BASS_CR_R3M15_B_preparation_refinement_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_B_preparation_refinement_20260922_v1.tar.zst) — 969991056 bytes
- [BASS_CR_R3M15_B_preparation_refinement_20260922_v1_DRIVE_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_B_preparation_refinement_20260922_v1_DRIVE_MANIFEST.json) — 27294 bytes
- [BASS_CR_R3M15_C_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_C_20260922_v1.tar.zst) — 488561702 bytes
- [BASS_CR_R3M15_C_20260922_v1_DRIVE_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_C_20260922_v1_DRIVE_MANIFEST.json) — 12779 bytes
- [BASS_CR_R3M15_FINAL_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_FINAL_20260922_v1.tar.zst) — 179070 bytes
- [BASS_CR_R3M15_PREREGISTRATION_20260922_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M15_PREREGISTRATION_20260922_v1.tar.zst) — 65188 bytes
- [BASS_CR_R3M16_A1_20260923_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M16_A1_20260923_v1.tar.zst) — 970324374 bytes
- [BASS_CR_R3M16_A1_20260923_v1_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M16_A1_20260923_v1_MANIFEST.json) — 23861 bytes
- [BASS_CR_R3M16_B1_20260923_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M16_B1_20260923_v1.tar.zst) — 1907840011 bytes
- [BASS_CR_R3M16_B1_20260923_v1_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M16_B1_20260923_v1_MANIFEST.json) — 23863 bytes
- [BASS_CR_R3M17_READINESS_ecc8ecaddbea_20260923.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M17_READINESS_ecc8ecaddbea_20260923.zip) — 147477 bytes
- [BASS_CR_R3M18_B2_FINAL_AUDIT_20260923_v1.tar.zst](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M18_B2_FINAL_AUDIT_20260923_v1.tar.zst) — 938212186 bytes
- [BASS_CR_R3M18_B2_FINAL_AUDIT_20260923_v1_MANIFEST.json](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M18_B2_FINAL_AUDIT_20260923_v1_MANIFEST.json) — 5723 bytes
- [BASS_CR_R3M19_20260923_0b56f0ac_PATCH_AUDIT.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M19_20260923_0b56f0ac_PATCH_AUDIT.zip) — 619353 bytes
- [BASS_CR_R3M20_N1_20260923_6c2ddd7f_EVIDENCE.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M20_N1_20260923_6c2ddd7f_EVIDENCE.zip) — 127839 bytes
- [BASS_CR_R3M21_20260923_359b2bcc_EVIDENCE.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M21_20260923_359b2bcc_EVIDENCE.zip) — 18627 bytes
- [BASS_CR_R3M22_20260923_4b5488d8_EVIDENCE.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M22_20260923_4b5488d8_EVIDENCE.zip) — 47600 bytes
- [BASS_CR_R3M23_20260923_bb48456b_EVIDENCE.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M23_20260923_bb48456b_EVIDENCE.zip) — 36091 bytes
- [BASS_CR_R3M26_MODEL_PRODUCTION_CONVERGENCE_20260924_d7e8f3be.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M26_MODEL_PRODUCTION_CONVERGENCE_20260924_d7e8f3be.zip) — 274335 bytes
- [BASS_CR_R3M27_B3_RESULT_AUDIT_20260924_b96608e.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M27_B3_RESULT_AUDIT_20260924_b96608e.zip) — 55289 bytes
- [BASS_CR_R3M9_PAPER_BASED_INDEPENDENT_REIMPLEMENTATION_SPEC_20260921_v1.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M9_PAPER_BASED_INDEPENDENT_REIMPLEMENTATION_SPEC_20260921_v1.zip) — 18932 bytes
- [R3M28_SMALL_EVIDENCE_V2.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/R3M28_SMALL_EVIDENCE_V2.zip) — 62331 bytes
- [R3M29_SMALL_EVIDENCE.zip](/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/R3M29_SMALL_EVIDENCE.zip) — 36302 bytes

## Request to the external reviewer

Please independently audit the chronology, exact identities, run-result provenance, failure preservation, scientific status transitions, and backup claims. Compare the machine-readable inventory with the linked local records. Report factual discrepancies, missing evidence, unsupported status promotion, and any claim that exceeds its recorded scope. Separate code/test evidence, numerical evidence, scientific admission, remote publication, and restore verification. Do not rerun scientific work or modify this checkout. Return a concise but detailed audit with findings by severity and exact file links; conclude with one next canonical action.

## Fixed status and limits

- `production_admission = HOLD`; `all_bound = OPEN`; `b-grid = NO_GO`; `GLOBAL_TIME_ERROR = NOT_EVALUATED`.
- R3M27 time evidence is a noncertified estimate for fixed h=.20 selected spans only.
- R3M28 A3/B3 is a raw pair NO_GO; it is not a continuum spatial-error lower bound.
- R3M29 cell-average Coulomb is only a candidate for a short same-h validation.
- Dropbox upload records do not imply raw readback or restore. Use the status in each receipt.
- Purpose-specific numerical target is 1% total, .10% time, .30% space, with remaining allocations as registered in the linked roadmap. Model discrepancy remains separate.
- Model authority: [MODEL_CONTRACT.json](../../../docs/r3m26/MODEL_CONTRACT.json), [MODEL_FOUNDATION_KO.md](../../../docs/r3m26/MODEL_FOUNDATION_KO.md), [DAG.json](../../../docs/roadmap/DAG.json), and [ERROR_BUDGET.json](../../../docs/roadmap/ERROR_BUDGET.json).
