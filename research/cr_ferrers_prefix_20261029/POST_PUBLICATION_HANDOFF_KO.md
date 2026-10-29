# BASS-CR PR124 publication closeout and continuation (2026-10-29)

PROJECT=cosmosapjw-quantum/bass_cr
UNIT=CR_FERRERS_PREFIX_EXACT_V1
PR=https://github.com/cosmosapjw-quantum/bass_cr/pull/124
BRANCH=research/cr-ferrers-interval-compression-20261029
HEAD_BEFORE_POST_PUBLICATION_RECEIPTS=bf5ee426167f70cd09d8527a701a0588c6c9e0d3
BASE_PR=123
BASE_HEAD=9f520c5e4042cb15bbd55da14ef946d6d9960d97

## Source authority and restoration

- Original 3,201-atom NPZ: SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`.
- Frozen SOURCE ZIP: 1145041 bytes, SHA256 `f8048f8f19836b45d77682fefc2cfa520553c9d75fe4b1c06be01fbd56e4fbb0`.
- SOURCE [Google Drive](https://drive.google.com/file/d/1s7GaBh7axN4s2ZXSTXe-Eyf1hUOkRmNd/view): actual original download + whole hash, member 52/52 and ZIP CRC PASS.
- Stage [Google Drive folder](https://drive.google.com/drive/folders/1E7zd5EICcT77R2TXHw5sfVimxOuNrVpT): 20 file IDs/names/sizes confirmed. Individual stage original byte hashes NOT_RUN.
- GitHub PR124 published 16 core + 20 staged files. Prior turn all 36 Git blob SHA readback matched local originals; current turn 5 representative source/review-file blobs rechecked and HEAD unchanged.
- GitHub combined CI statuses had zero entries; cannot infer CI PASS.
- Original Dropbox binary ZIP double-backup NOT_VERIFIED. Do not count Dropbox Paper or Library as Dropbox original binary restore.

## Scope and checked result

In the finite fractional matching with edge support E_h+E_l<=K and bin-only cost chi=1_(b_h!=b_l), each high sees an energy-ordered low prefix within each birth bin. A directed segment-tree with 0-cost internal arcs and bin-entry cost chi preserves all feasible (m,C) pairs; therefore C_min(m), M(c) and d_max(c) in the stated model are preserved. The high-labeled flow decomposition and original-graph primal-dual gaps are checked by exact Python Fraction consumer.

The original source 102831 logical HL edges becomes 4307 compressed forward arcs and 1358 network vertices, with 2295 disconnected high vertices pruned. Exact original 3201 3-budget M/d and dual gaps are preserved. A separately synthetic 3201 5-bin recoloring passes 3/3 exact original dual checks. Earlier Wolfram 7/7 and UBSan 6/6 are predecessor evidence; **fresh current-turn clean restore** ran `bash REPRODUCE.sh`, producing a checked g++20 build and 6/6 normal + 6/6 python -O unit tests with exit0.

Three earlier same-host pairs show original median 18.844991s vs compressed median 16.471989s, ratio 1.144063. This is the measured original 3201 fixture with n=3, not an algorithmic bound or physical production performance.

## DAG/claim contract

CENTRAL_DAG=28/88 delta0
EXTENSION_DAG=0/3 first PARTIAL
NEW_AUXILIARY=1/1 scoped implementation verified, review HOLD
WORKFLOW=18/20; R06 and C09 genuinely distinct-author NOT_RUN
AGGREGATE_CPU_HARDCAP=NOT_CERTIFIED
HISTORICAL_PR118_RESOURCE_FAIL=PRESERVED

The physical exclusive He event kernel, physical K, source clock/normalization, donor/partner energy owner and stopping are unbound. Physical native25/L4/production HOLD. Do not infer physical rates from mathematical marginal capacities.

## Next minimal actions

1. Confirm the final detached delivery head (see separately uploaded HEAD_LOCKED_HANDOFF_KO.md), PR124 still DRAFT, and source hash above. Read research/cr_ferrers_prefix_20261029/{THEORY_FERRERS_KO.md,REPORT_KO.md,RESULTS.json,DAG_DELTA.json,STAGE_LEDGER.json,HANDOFF_KO.md,POST_PUBLICATION_RECEIPTS.json}.
2. Get genuine distinct-author R06 mathematical hostile review and C09 code/ownership review. Only then change 18/20.
3. If another scoped science node is authorized, profile exact original-edge certificate evaluation and witness decompression; optimize this actual bottleneck before more generic checks. Preserve fixed-C region distinct from C<=c frontier.
4. In parallel pursue actual source-qualified exclusive He kernel and physical K/clock/energy owner. No physical native25/L4/production until source binding.
5. No main merge, parent branch mutation, changed-source reattribution or hidden CPU charge. Preserve original ZIP, immutable source and test bytes.

This is a **post-publication** handoff. Git stage records were retrospective and 20/20 posted, not real-time scientific-phase backups. Source ZIP remains immutable.
