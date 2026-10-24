# 07:21 UTC workspace-loss recovery and next execution

The files used at 05:00 UTC were absent when three agents checked the workspace at 07:21 UTC. The cause is UNOBSERVED. S0 commit `ad3634c029dcff722602dc139fb726142935f88c`, tree `4ef8b8ea98318325caf1e7f4df2741cab37e4956`, Draft PR102 survives. Its eleven exact files have been restored from the surviving API/tree cache. The reviewed contract SHA remains `44b43c42eff4b67a9d3c8ed4d49e53f3cb91c9c29b2413cca2a1761632215d2b`.

## Observed v1 execution, preserved separately from bytes

- `n5_resolvent_tests_20261024t050030z_v1`: observed worker return10/10 PASS; CPU0.239278s; peak RSS49072KiB.
- `n5_ce_resolvent_primary_20261024_v1`: observed FAILED due local variable shadowing; CPU0.279477s; wall0.318127s; peak RSS54012KiB.
- Actual v1 work: two Q matrices built, one complete case, nine completed RHS, three source projections. New ODE/source/rate quadrature/historical replay0.
- v1 executed code, CASE, full dispatch receipt and NPZ/raw files were not in S0. At this authorization they are NOT_RECOVERED. The agent/tool conversation preserves observed outcome/cost, not a byte-level replacement for lost artifacts. Do not create fake originals or describe a new calculation as recovered v1 raw. v1 is excluded from scientific admission.
- Known bounded worker subtotal from the inherited19.209296114s plus the two observed v1 children is19.728051114s. External/tool/mechanical unmeasured costs remain null or separately observed, never reset to zero.

## Minimal continuation decision

Failure1 is an implementation variable-shadowing defect; failure2 is an environment/artifact-availability incident. Neither supplies a physical no-go result. The previous requirement to possess exact failed-v1 bytes before any new work would permanently block a scientifically independent new unit although authoritative physical inputs survive. Root authorizes a new clearly identified recovery execution from those immutable inputs, without promoting v1.

The frozen physics, grids, thresholds, equations and numerical tolerances are unchanged. Restore PR59/PHYS83/C23D inputs from exact Git commits or their verified backups, not by rerunning providers or old science. If old implementation bytes cannot be recovered, reconstruct a new implementation identity with the `case_record` name repair. It is not an exact reconstruction claim. Create a new input `n5_ce_resolvent_recovery_input_20261024_v2` and run `n5_ce_resolvent_recovery_primary_20261024_v2`. Do not fabricate an original CASE_V1 file.

Before launch publish the prepared code, input manifest and CASE at a new immutable S1 commit. The new source/environment warrants the small frozen controls again plus one two-iteration CASE-preservation regression; it does not warrant any completed historical science suite. Tests≤10CPU s/30wall, primary≤30CPU s/60wall, AS512MiB, fresh actual resource/lease, one native thread, workerCPU0/coordinatorCPU8 when actually available. Retain all new raw output and measure cost. Root may proceed directly from passing controls to the same twelve physical matrix cases. New v2 admission depends on actual raw results and independent C9.

If v2 succeeds, total current-session physical work is14 Q builds,13 completed cases,117 RHS; only12 cases/108RHS from v2 are admitted. One case is repeated relative to the failed current v1 attempt, explicitly charged. These are anticipated counts until actual execution confirms them. Historical science replay remains0.

Survey tool caches are being restored independently. Re-serialized transport envelopes are labeled as such; exact underlying source bytes are verified where original hashes exist. Missing metadata/raw is recorded rather than invented. New freshness at07:23 already identifies PHYS86 owner progress; obtain its actual return and preserve PHYS84/full-stopping gates.

EXECUTION: v1 failed and raw unavailable; new prepared recovery authorized, not yet run.

PUBLICATION: S0 R1 PASS; S1 code/input snapshot required before new launch.

BACKUP: no S0 ACK at incident time; recovered preparation checkpoint being saved. Prior N5/C23D immutable R3 receipts remain historical evidence.

DAG: new CE child in progress; full N4/N5 PARTIAL/OPEN; N6/N7 gated; global_error_bound=null and global_completion_percent=null.
