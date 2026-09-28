# R3: idle-host closeout and cross-repository research

## Scope and evidence

This is a research/continuation document, not a new paid-run authorization. The owner reports bass_cr, BASS_HE and WU088_HH idle. No live NCP process census was performed here. Existing outputs, code, permissions, thresholds and consumed authorizations are unchanged.

The interrupted publication already exists on bass_cr branch research/ncp-shared-r3-20260928 at 93c0604f591b063f2087019d0c19e909261067de. The original 64,092-byte research packet has SHA256 09c4986027d9f08389245c763378cfd9f4baad6174374f05a3f8aca46de81a20 and was already uploaded to both providers. Its current metadata was confirmed without creating duplicate copies.

## 1. The next node changed: R2 has passed

The actual R2 result is published at bass_cr commit 820b3e0a6da9f7a8c8ece8fcbd3afcf3fa9a6dc3, tree 3cf2a99680001b9da550343136417812429190ca. Run 20260928T101921Z reports F1_ENGINE_ADMISSION_PASS, exit 0, 1817.893839127999 seconds. All 297 planned tasks were persisted, with 60 workers and no failed tasks. The publisher recorded 121 resource samples, up to 61 child processes, maximum sum of child ps %CPU 5987.4, and minimum MemAvailable 121914019840 bytes.

The ps statistic is a process-lifetime average, not a precise interval utilization measure. This run overlapped the HH interruption interval, so it is valid numerical-admission evidence subject to its original checks, not a clean isolated-throughput benchmark or a measured 60x speedup. The original serial timeout has no completed comparable wall time.

Five direct metric sentinels report a maximum relative residual 2.3253812582402828e-9 against their 1e-6 gate. Their finite differences do not certify a continuous time supremum or an integrated trajectory-error bound.

Decision: do not repeat F0, the completed R2 admission, or the old test suites for publication. The 3600-second/4000-KRW exactly-once authorization has been consumed by the recorded run. Idle status is not another run allowance.

## 2. What transfers from WU088_HH

Read source: research/r31u-shared-ncp-theory-20260928 at ff3db87dfbadd5f1eed89b413e5b785baf63a429; research/r31u_shared_host/{RESULT.json,RESEARCH_AND_DESIGN_KO.md}.

The HH research reports a small algebraic metric gap (5.12384790334138e-15) but a large actual-derivative defect (0.248069740331951) and whitened spectral residual 0.6007169417167524 per atomic time in its own interpolation experiment. Its simple Hermite candidate was not admitted: mixed O and D errors were approximately 0.494 and 0.570. These are HH results, not bass_cr measurements.

The transferable theorem is H-independent: with S positive, H Hermitian and the actual derivative of the represented S(t), the generator's norm defect depends on dot S-D-D†. A cheap overlap/connection audit can reject a bad interpolation before an expensive H evaluation. It cannot certify full H accuracy or omit the separate H gate.

Do not repair bass_cr by replacing an independently computed derivative with D+D† or by symmetrizing raw sources. For the next cache-only node, compute the whitened residual using the existing independent three-point snapshots and report sampling/finite-difference limitations. This is a structural diagnostic, not a continuous bound.

The HH report also identifies unequal benchmark histograms: max(24,2P) tasks over 12 cyclic pairs depend on P. Its proposed 132-task fixed histogram is a reasonable design for future finalist comparison, not grounds to rerun every completed M3A configuration. Preserve HH's valid exactness and CPU-engagement evidence while keeping M3B throughput ranking pending.

## 3. What transfers from BASS_HE

Read source: research/shared-c64-crossrepo-20260928 at 8ed9a455bada777bc63f29fa5f6064b0eff2065a; research/shared_c64/20260928/R1.

HE's conditional common-contour method factors an expensive spectral trace from cheap impact-parameter weights. Its publication reports 14 independently computed traces, 56 weighted actions and 28 panel pairs. A single sandbox trial of a representative case gave 3.83926x; it is not an NCP or bass_cr speedup. Global homotopy, physical promotion and continuum admission remain unproved/unadmitted.

Transfer only the dependency-factorization principle. In bass_cr, same-center blocks at fixed time/basis/trajectory/same_order do not depend on cross quadrature q,h, so factoring those blocks is appropriate. Do not transfer HE energy sheets, complex-contour actions, matrices or numerical values to CR. CR impact parameter changes geometry/ETFs and is not merely a postprocessing weight without a separate proof.

Independent 32/64-panel paths must remain independent. Reweighted actions sharing one spectral trace share its uncertainty; similarly, many consumers of one CR operator cache do not create many independent numerical validations.

## 4. Additional derivation completed here

The supplement derives the moving-metric identity, the additional term for a non-Hermitian H, and a Duhamel bound for replacing a generator by its skew-Hermitian part. A Wolfram exact noncommuting 2x2 check and eight local algebra/numerical probes were completed. No native BASS evaluation, cloud run or production test was performed.

The first Wolfram trial differentiated Conjugate[t] before imposing real time and did not reduce to zero. It is retained as a symbolic-domain/setup failure, then corrected by simplifying S under real-time assumptions before differentiation. The corrected exact difference is the zero matrix. Neither result is a runtime or scientific-production claim.

The new controlled projection bound is conditional on an actual time integral. Discrete sentinel maxima cannot supply that integral. This prevents a norm-preserving integrator from being mistaken for a fidelity certificate.

## 5. Resource decision while all sessions are idle

For now choose exclusive heavy epochs, not another generic scheduler implementation. One host coordinator admits the next expensive workload; the other sessions may edit/read/run lightweight checks. Before every launch verify descendants and actual resource availability. No current process is killed, migrated, resized or resumed by this document.

The earlier proposals CR:18/HE:18/HH:20 plus control8, HE:16/16/16, and HH:32/HE:16/CR:12 plus control4 are different candidates, not three compatible deployed grants. Do not silently combine them. A future shared allocator must count CPU and memory once at host level, enforce ancestor headroom, bind ownership to PID start identity, and avoid reclaiming a lease while children remain alive.

An exclusive run may use the already validated pool size only within a new applicable authorization. Eight control slots or 56 pool slots are not retroactive modifications to the successful 60-worker R2 contract. No performance claim is made for a new partition.

## 6. Revised minimal continuation

Next bounded node: R3_POSTPASS_CACHE_REUSE_AND_METRIC_AUDIT.

1. Read the successful R2 and F0 evidence from exact Git snapshots. Do not recreate historical results.
2. Validate the 297-task cache payload and receipts, then add an import bridge that preserves old identities while separating numerical context from output-path/PID/worker operational metadata. The previous output-path identity defect remains relevant to future reuse, but does not invalidate the completed R2 run.
3. Demonstrate fresh-output reuse with no rebuild, no native fallback, no tolerance changes and unchanged arrays. Reject basis, parameter, source, ABI, dtype, numeric-runtime or policy drift. A different engine is not equivalent merely because path fields were removed.
4. Using only stored operator samples, compute raw/whitened metric diagnostics at the available sentinel triples; preserve actual derivative versus reported derivative labels. Record unidentifiable continuous bounds as NOT_CERTIFIED.
5. Prepare the next finite-basis observable/transport contract. Keep capture=false and production HOLD until the specific next gate is authorized and satisfied.

Lazy metric tasks (297 to 201 under the observed prefix choices) and same-center factoring (594 to 54 subcalls) are future-work candidates, not reasons to repeat this passed admission. F2 optimization and a CF4 challenger are not automatically mathematical prerequisites for a finite-input M4 diagnostic. Radial/angular convergence, asymptotic extraction, all-bound completeness and b integration remain separate required physics obligations.

## Status

Research completed within the requested scope. Review type: OWNER_SELF_REVIEW; no independent decision reviewer was invoked. Cloud deployment/performance improvement: NOT_EXECUTED_NOT_MEASURED. No new active run authorization. Numerical claim ceilings unchanged. The old 18-35h final-audit ETA remains withdrawn.
