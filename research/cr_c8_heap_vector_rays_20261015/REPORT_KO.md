# BASS_CR C8 실측 최적화 및 방향별 보존형 photon cohort 지원

2026-10-15 KST. 실제 **코드 수정·실행**을 포함한 `physmath-research-loop`의 현재 coding 연구 노드. 이전 `bass_cr` PR #66 (`0a43dcbaf7691c04706800e3336c1fd5ceb056ce`)의 `compressed_cohorts.py` 등 전부 **원본 그대로** 재사용한다. 이 연구는 원 source/물리 모델을 교체하지 않는 단일 단계 경량 최적화/검증이며, 실제 우주 재이온화 이력/상대론적 Boltzmann transport의 신규 전면 계산이 아니다.

## 1. 과학 모델 및 부호/단위

- Metric `(-,+,+,+)`, normal-tetrad null photon `p^a=(E/c)(u^a+e^a)`, `u·u=-1`, `e·e=1`, `u·e=0`, `c=29979245800 cm/s`.
- Original MD14/50,000 K frozen source is `13.6..100 eV`; independently produced SOURCE07 Bianchi photon labels can reach `432.2293723204678 eV`; Verner atomic fit applies to `E<=50000 eV`.
- Source Jacobian, ray direction k_i, birth epoch, proper time, R·J and quadrature weights are owned by `rei_bianchi` SOURCE07. **Our code does not reapply them**. Cohorts are per-H photon counts and current physical eV, proper neutral densities per cm³, timestep proper s.
- Source model/baryon/helium normalizations, 13.60/24.59/54.42 eV Verner cutoffs, and binding-energy ledgers stay separate. Existing CR/RCT/HH OFF under primary REI goal.

## 2. Next-neighbor heap: identical greedy selection, asymptotically cheaper

Parent reference `CompressedCohortTransport.compress` enumerates all adjacent pairs whenever it merges. A decreasing cohort count from N to cap K requires ∑_(m=K+1)^N(m−1)=O(N²) pair evaluation, each evaluating all three frozen absorber-specific rate/heat bounds. For a given adjacent pair, its cost/score depends only on its current energies/counts and *fixed* neutrals, dt, forecast ratio and budgets. Remaining available budget only decreases, so a currently inadmissible unchanged pair cannot become admissible later. One merge invalidates only the pair itself and immediate left/right neighbors.

New `HeapCompressedCohortTransport` maintains doubly linked cohorts and lazy generation-checked heap candidates; updates at most two new adjacent scores per accepted merge. Complexity for this greedy rule is O(N log N) heap work, retaining the same initial-order tie break. Unlike naive global spectrum clustering, it changes **only computation order**, not the local physical criterion. **All tested numerical outputs, cohort placements, count/energy moments and spent budget certificates exactly agree with the old scan** (including 48→32, 96→48, 240→32, 384→192, equal-energy and seeded random controls, stringent HOLD cases and four-step repeated injection). 

Measured *median* wall times, matched input/cap and same floating scientific output, Python 3.13, 5 timer repetitions, container Linux (not user Ryzen hardware):

| Cohorts | Old scan [ms] | New heap [ms] | Ratio |
|---|---:|---:|---:|
| 48→32 | 3.568 | 0.512 | **6.96×** |
| 96→48 | 18.620 | 1.176 | **15.84×** |
| 240→32 | 159.790 | 4.425 | **36.11×** |
| 384→192 | 299.874 | 6.415 | **46.74×** |

Per-label `last_certificate` reset semantics and `CompressionHold` unchanged; in a failed trial, no mutation occurs. No matched-accuracy claim for a full cosmological solver is implied.

## 3. Vectorized multi-ray photoionization/heat

New `batch_frozen_be_readout` applies the same Verner formula and one-step BE `(N_i/(1+Σ_k dt c n_k σ_k)) dt c n_k σ_k` across ragged independent angular rays using a single NumPy SoA-style input packing. Each ray retains **its own** proper neutral density, dt, current physical E, redshift factor, and final species readouts; no source weight/Jacobian is multiplied again. Redshifts crossing 13.6 eV are correctly zeroed in the absorber and heat, while >50keV energies are rejected. Independent scalar reference: maximum species event/heat relative differences 3.7×10⁻¹⁶ in the measured batches.

| Independent rays (48 source packets each) | Scalar [ms] | NumPy [ms] | Ratio |
|---|---:|---:|---:|
| 8 | 0.691 | 0.224 | **3.08×** |
| 64 | 5.624 | 1.122 | **5.01×** |
| 256 | 26.747 | 6.040 | **4.43×** |

Parallel process execution is **implemented and measured**, not assumed faster. The separate `ray_parallel.compress_rays` uses a safe `forkserver` process context, deterministic ray ordering and atomic ensemble return. Under this 5-CPU sandbox, at 8 rays cold workers **slow** the call from about 0.00396 s (one process) to 0.01746/0.01608 s (2/4 processes); at 64 rays a 4-worker process pool returned 0.02655 s vs 0.03003 s for one process (1.13×). This includes process startup, IPC and per-call pool teardown. `opt_benchmark.py` also compares one/two-process species readouts: at 256 rays two-process was 1.71× faster than scalar but significantly slower than the NumPy readout. Do not recommend unconditional parallelism for short ray workloads; in large native Rust C3, use that owner's own measured parallel/SoA path.

## 4. NEW physics safety: Bianchi direction/source-age cannot be merged

For cohorts sharing the same normal-tetrad direction `e^a`,

`Ebar=(n1 E1+n2 E2)/(n1+n2)` implies `(n1+n2)Ebar=n1E1+n2E2`.

Hence the photon four-momentum `Σ n p^a=(Σ nE/c)(u^a+e^a)` is preserved. But merging photons with **different** directions `e1,e2` into one ray carrying `e1`, even if energy is preserved, produces a spatial momentum defect `ΔP^a=(n2 E2/c)(e1^a−e2^a)`. Scalar mean-energy preservation alone is insufficient for Bianchi angular transport.

New `RayLane(ray_id,source_epoch_s,clock_s,direction,cohorts)` and `compress_bianchi_ray_lanes` enforce independent ray/source-age/proper-time owner keys, unit direction, transactional failure and normal-frame photon number/energy/spatial-momentum equality (floating physical moment check). This is a **safe interface to SOURCE07 packets**; it is not an implementation of their actual photon tetrad/metric or an optical/Ricci/Thomson closure.

A new second-order functional observation follows from the same moment identity: for smooth response `g(E)` within one threshold-safe interval,

`|n1 g(E1)+n2 g(E2)−(n1+n2)g(Ebar)| ≤ 1/2 ||g''||∞ [n1 n2/(n1+n2)] (E2−E1)²`.

This could sharpen parent’s first-derivative budget. A certified `g''` enclosure has **not** yet been implemented or used to admit more merges. Do not import this improved asymptotic error as a current code certificate.

## 5. Cross-repo current work and no duplication

Actual `rei_bianchi` PR117/working HEAD `0c9fd151b6e0aef9ee2414ed672364afa4a3dce1`, 2026-10-15 ~08:27 KST, includes `SOURCE07 C3` Rust native Bianchi photon event-splitting, serial/2/4-thread and SoA optimized readouts. Its independent Ryzen5900X 24576-packet, eight-slice release microbenchmark reports FLRW 1→4 workers 2.43×, axisym 2.71×, AoS→SoA 5.77×, **for that owner-specific code**. Do not claim these numbers as bass_cr speedups. The C4 next contract explicitly flags bounded per-ray memory and angular momentum ownership; this research supplies a Python *error-budgeted* compressor and operator-level tests complementary to the native C3. AX07 conditional ZERO complete, AX08 signed family partial, AX11/AX12 pending in last observed STATE. No user Codex launched or used by this run; owner repo was read only.

`BASS_HE` current PR58 is the **warm HM12/FT03** P01 second-cell interval and full 2904 photon error carry: do not transfer numeric bounds into cold MD14 source. `WU088_HH` PR73 remains a different screened-Coulomb Fredholm/radial problem. No foreign rate, stability or numeric coefficient imported.

Literature context: Mirocha et al. 2012 arXiv:1204.1944 and Baumschlager et al. 2024 DOI 10.1051/0004-6361/202348164 emphasize matching **species-specific ionization and heating** under evolving SEDs, not merely scalar photon moments. Here the physical scope is local frozen-neutral BE and accepted forecast tube, not a calibrated full H/He reionization history.

## 6. Execution, limits and handoff

`PYTHONPATH=src python -m pytest -q tests`: **92/92 PASS** (61 inherited + 31 new), including randomized strict heap parity; opposite-direction/epoch controls; multi-process isolation and strict rollback. Container benchmarks are in `results/OPT_BENCHMARK.json` and `results/RAY_PARALLEL_BENCHMARK.json`, measurements raw in JSON. Existing tests check conservation of number, kinetic energy and per-species BE event/heat readouts. Actual Wolfram15.0.1 exact mean-energy/greedy complexity identities and actual xTensor1.3.0 normal-tetrad null/momentum tests returned zero residuals with official package hashes. First Wolfram overly long symbolic call failed syntax; corrected targeted call passed. External independent review/native subagents not available (`native_subagent: NOT_RUN`). No CUDA/C++/Rust producer, HPC, full source/chemistry or exact outward float full-history theorem is claimed.

**Next READY:** (A) realistic source-epoch/angle/proper-time short-interval coupling with SOURCE07 owner outputs, while preserving `k_i`, redshift and source Jacobian ownership; (B) higher-order response bounds to reduce loose one-step slope-based budgets, plus a separately versioned new source/config experiment; (C) independent bass_cr Landau continuum fine constitutive/adjoint is unchanged PENDING. If any source identity or physics changes, require an explicit new model ID and matched source/IC/clock before accepting output. This code is supplementary experimental science, not owner AXBI DAG readiness or physical EoR claim.
