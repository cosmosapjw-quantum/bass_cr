# Memory admission validation

The cache correction is frozen at `resource_profile.py` SHA256 `0759465ca5f01967e7df6afdf897f0a068c4812163f80df5f44a5291d369d17f`. This record persists already observed results; writing it reran no test, census, native call or physical calculation. Exact commands, counts, source hashes and counter values are in [MEMORY_ADMISSION_VALIDATION.json](MEMORY_ADMISSION_VALIDATION.json).

The focused cache suite passed **9 tests**, the affected resource suite passed **5**, and the affected execution CLI suite passed **8**: **22 passed, zero skipped**. Initial TDD failed before the two new helpers existed. Final coverage includes invalid/missing accounting, all cache exclusions, protected and descendant cases, concurrent changes in usage/cache counters, over-limit repayment, tighter ancestor caps, and host MemAvailable.

The observed local 8 GiB cgroup had 375,595,008 bytes of raw headroom and 3,730,847,744 bytes of eligible half-cache credit, giving 4,106,442,752 bytes of estimated availability. The unchanged reserve was 1 GiB; CPU quota remained eight despite nine visible affinity CPUs. These are a recorded pre-pilot census sample, not a new live reading or a peak-RSS measurement.

For a verified leaf cgroup, the policy credits half of the nonnegative difference between the smaller current/file/file-LRU count and the sum of mapped, dirty, writeback, shared-memory, unevictable and protected bytes. Overlapping exclusions intentionally underestimate credit. Anonymous, swap and slab memory receive no allowance. Two cache observations and bracketing usage reads keep the smaller credit and larger charge. Missing counters disable credit; missing usage gives zero availability for that finite cap. The final estimate remains below host MemAvailable and every finite ancestor constraint. No cgroup is modified or forced to reclaim, and the existing `max(1 GiB, available/8)` reserve is unchanged.

The [Linux cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-interface-files) defines these counters and protections. The [procfs documentation](https://docs.kernel.org/filesystems/proc.html#meminfo) explains that available memory can include reclaimable cache. The one-half allowance is an explicit conservative project policy, not a kernel-defined cgroup MemAvailable formula or allocation guarantee.

This validates resource estimation and launch admission only. It contains no physical pilot result, MPI acceptance, scientific accuracy claim or NCP scaling measurement.
