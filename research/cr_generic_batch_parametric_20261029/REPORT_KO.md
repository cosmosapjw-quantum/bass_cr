# BASS-CR: exact parametric multi-budget SSP 2026-10-29

## 범위 및 SOURCE

Unit `CR_GENERIC_BATCH_PARAMETRIC_V1`, parent Draft PR122 HEAD `f152e28fd4e9a727b23e068603c0359c5e0d1303`. Original atom array NPZ (233050 bytes) SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. This work uses the same conditional K=3 eV numerical source and does **not** infer a physical exclusive He kernel, its physical K, clock, rates, donor/partner energy or stopping. No main/parent/foreign repo writes.

## 최신 repo 상태와 의존성 (실제 2026-10-29 조회)

- `bass_cr` PR122 still newest at frozen head, parent PR121, Draft. `BASS` PR245–247: Bianchi-I CE1 angular/time source certificates, not CR event kernel.
- `BASS_HE` PR108: deuteron correlated daughter ledger, not this He event marginal. `rec_bianchi` PR156: printed HD frequency/energy callsite, different source.
- `rei_bianchi` PR264: frozen electron UVB local jet, not physical CR rate. `WU088_HH` PR159–160: HD thermochemical Q and cross-model source, not a He event kernel. `vigilode` PR107–109: ODE original residual/lognorm, method inspiration only.
- Previous bass_cr R/C 18/20 reviewer distinction remains; no genuinely distinct-author reviewer was available in the current tool inventory.

## 새 이론 (derived)

One exact residual path traversal covers sorted query budgets. On a minimum-cost-flow segment with positive marginal integer k, M(c)=m0+(c-C0)/k, dual lambda=1/k. At zero-cost and saturated regions the code uses special paths/mincut. Each query has its exact primal including negative reverse residual arcs and original-graph dual prices; independent Python `Fraction` recomputes capacities, budget and primal-dual gap and enumerates every admissible original HL edge. Proof and regimes in `THEORY_KO.md`; this is not a new general MCF algorithm.

## 실제 코딩 및 수치

- New `potentials_batch.cpp` C++20 i128, query-indexed streaming witnesses, one traversal for up to 128 budgets; `batch_bridge.py` exact normalization and full original-edge dual proof. Original PR122 files and NPZ protected.
- 6/6 Python normal tests, 6/6 Python -O, 75 seeded exact full-event LP comparisons; independent Wolfram 18-edge/7 budget values 7/7 exact; 7-budget UBSan 0 overflow reports; `REPRODUCE.sh` exit0.
- Original 3201 atoms, 3 budgets, each 102831 HL dual constraints and zero exact gap. End-to-end batch wall 16.337883s, Python-process CPU 15.174366s, peak child RSS 114696 KB. Existing parent 3-budget rational results exactly matched.
- 120 synthetic atoms / 5 bins / 8 budgets / 3 paired trials, same machine, compiler and exact certificate checks: batch median 0.049091s, repeated parent median 0.182901s, ratio of medians 3.7258. Batch last 84 augmentations vs 610 sum repeated. This ratio is **not** original-3201 or physical-production speedup.
- Parent 3201 complete repeated-workload retest timed out with no valid final log. No exact source-scale matched ratio inferred.

## 오류·반례 및 수정

1. First Python batch parser treated `LOW` as unexpected: explicit protocol field contract amended, then unit/LP tests passed. Implementation defect, not theory.
2. Original PR122 repeated native benchmark did not produce a complete output before timeout: comparison blocked; preserved, not transformed into numerical failure.
3. A budget-query ceiling of 128 and signed-i128 scaling/overflow checks were added; output memory is O(Q times witness size), no blanket scalability claim.
4. Negative residual reverse arcs and exact-kink budgets tested; terminal maximum-flow λ=0 dual checked.

## Claim gate / physical boundary

Canonical 28/88, extension 0/3, prior auxiliary references retained, this new auxiliary exact-batch 1/1 **SCOPED WITH R6/C9 HOLD**, workflow 18/20 (R6,C9 genuinely distinct author NOT_RUN). Physical K, exclusive He kernel, event rate normalization/clock, donor+partner energy ownership, stopping, native25, L4, production all HOLD. Existing PR118 CPU resource FAIL and noncertified aggregate CPU budget remain.

## Next recommended action

A separately authored R6/C9 hostile review of batch interpolation, negative residual cycle, dual construction and fractional endpoint, then parent-native 3201 exact matched benchmark under bounded resource allocation. Independently pursue exclusive He event source and physical owner binding. No merge before claim gates.

## Literature

- Király & Kovács, *Efficient implementations of minimum-cost flow algorithms* (2012), https://arxiv.org/abs/1207.6381.
- Kovács, *Minimum-cost flow algorithms: an experimental evaluation* (2015), https://doi.org/10.1080/10556788.2014.895828.
- Switzer & Hirata, *Primordial helium recombination II* (2008), https://arxiv.org/abs/astro-ph/0702144. Physics-source candidate, not an admitted exclusive pair-event source.

Remote publication/backup receipts are detached, generated only after actual provider responses.
