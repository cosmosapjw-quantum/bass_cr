# R4K N1536 A1 recovery research

Status: **R4K_A1_PARTIAL_SALVAGE_VERIFIED__RESOURCE_CENSUS_CAUSE_UNRESOLVED__RESUME_REPAIR_REQUIRED**

A1 partial return SHA256:
`82a8997ad57ad2a7dee70bce67bd0c5b2871df0ca4f23f04362bfb7f8e9b5b7e`

Size: 51,269,880 bytes.

Independently restored facts:
- manifest entries 4218, no size/SHA mismatch, ZIP CRC PASS;
- canonical query pairs 2063 = predecessor 2047 + 16 completed N1536 stage-8 useful queries;
- stage-8 completed 16/16 on 8 workers, wall 193.6389812209818 s, qps 0.08262799101251579, raw attempts 54, no task failure;
- stage-16 was rejected before dispatch by generic resource-census overlap;
- stage-32 was not started;
- selected 8-worker fill then hit the same pre-dispatch resource-census overlap;
- no N1536 candidate, temporal pair or cache-only replay was produced;
- A1 authorization consumed exactly once and supervisor reports group/descendant exit.

Root-cause classification: **RESOURCE_CENSUS_EVIDENCE_INSUFFICIENT**.

The current census constructs matching PID/cmdline data but discards that list when it raises the generic overlap error, so the partial evidence cannot establish whether the offender was a genuine external BASS job, a benign BASS helper, or a same-run teardown transient.

Required repair before fresh A2:
1. durable structured census with PID/PPID/PGID/SID/state/cmdline/affinity/cgroup/ownership relation;
2. classify same dedicated process-group members separately from external jobs;
3. bounded previous-worker teardown gate and `OWN_POOL_TEARDOWN_INCOMPLETE` classification;
4. exact A1 partial-archive validator and byte-preserving import of the 16 completed query pairs;
5. reuse A1 stage-8 measurement rather than recomputing it;
6. continue only stage16 -> stage32 -> missing fill;
7. seed lifetime raw budget with A1's 54 attempts:
   `GlobalBudget(parent_attempts=54, maximum=16896)`.

Wolfram-verified budget arithmetic:
- remaining midpoint queries 1520;
- remaining raw capacity 16842;
- strict remaining worst 16720;
- lifetime strict total 16774;
- lifetime cap margin 122;
- measured 8-worker-only fallback projection about 5.11 h by query throughput, about 4.97 h by raw-attempt throughput.

No native work was run in this R4K research loop.
