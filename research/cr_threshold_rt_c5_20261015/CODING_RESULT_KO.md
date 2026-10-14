# C5 실행형 연구: photon threshold-aware transport와 one-step H/He 원자 장부

2026-10-15 KST. **Scoped C5/C6/C7 coding result**, parent bass_cr PR64 exact head `26ac3b4eb6cbe792101c09ab48b3562dab8c5249`. 기존 `rei_bianchi` production·실행 중인 Codex 파일·AXBI scientific gate는 변경하지 않았다.

## 실제 구현

새 `src/threshold_rt.py`는 기존 frozen `MD14_Z002_FESC_BB50K_13P6_100_V1` (50,000 K, 13.6–100 eV)와 Verner HI/HeI/HeII 원자단면적에 결속한 **standalone Python prototype**이다. HeI=24.59 eV, HeII=54.42 eV에 각각 숫자 에너지가 같은 `chi^-`(target absorber inactive), `chi^+`(active) numerical states를 추가한다. Photon number/first energy moment를 보존하는 positive sparse two-neighbor transfer를 구현했으며 source sample 수 n=16에 49→51 states per direction만 필요하다.

실제 구현 경로: source injection via frozen Simpson-32 centroids → threshold-aware deposit → redshift and **below-13.6 boundary escrow + photon work** → frozen-neutral backward-Euler multi-absorber (species photo-events, binding and direct excess heat) → nuclei/charge stoichiometric ledger. 반복 three-step 경로에서도 모든 count/energy residual <~1e-11 unit tolerance. 샘플 관측은 count ~1.2e-16, energy ~6.3e-15 eV. `CohortTransport`는 불필요한 energy reprojection 없이 source-centroid energy를 따라가는 별도 양의 benchmark control이며 **많은 step에서 메모리 효율적인 production 대안이 아니다**.

관측값: 임의가 아니라 선언된 component 시험값 `(n_HI,n_HeI,n_HeII)=(1e-3,8e-5,2e-5) cm^-3`, `dt=10^9 s`를 사용하며, **실제 AXBI gas history에서 추출한 neut​​ral 상태가 아니다**. Reference는 같은 Verner fit/source S(E)와 backward-Euler step을 SciPy 연속 적분한 것이다.

| divisions/segment | initial HeI events baseline→tagged [%] | initial HeII [%] | 2%-redshift HeI [%] | 2%-redshift HeII [%] |
|--:|--:|--:|--:|--:|
|16|+10.2436→+0.0622|+38.5407→+0.1151|+8.6218→−2.5399|+46.3276→+1.9042|
|32|+5.0386→+0.0156|+17.8056→+0.0289|+4.3111→+4.3111|+20.9660→−10.6482|
|64|+2.4985→+0.0039|+8.5613→+0.0072|+1.9594→+0.8663|+9.0276→−4.7044|
|128|+1.2440→+0.0010|+4.1982→+0.0018|not measured|not measured|

`PRP != PR` constructive counterexample: one photon `E=25 eV`, redshift factor `r=.98` gives true physical `24.5 eV<chi_HeI` with correct HeI sigma=0, yet after **project→redshift→project** it retains sigma-effective `2.3282054176483962e-18 cm²` despite conserving count and first energy moment. Thus **one-sided tags repair frozen source but are NOT a complete moving spectral algorithm**. Important scientific finding, not a unit test failure repaired by tolerance changes.

## Execution and literature

- Local Python 3.13, numpy2.3.5/scipy1.17.0/pytest9.0.2; `PYTHONPATH=src pytest -q tests/test_threshold_rt.py`: **35 passed**, exit0. `src/benchmark.py` executed, 4 initial resolutions, 3 redshift resolutions, and three-step ledger cases. Relocated ZIP retest **35 passed**. Source code is in immutable ZIP, not only in prose.
- Actual Wolfram15.0.1: five algebraic residuals 0; actual hash-pinned xTensor1.3.0: five tensor residuals 0. Same-author CAS and Python independent-form evaluation; no external independent scientific review.
- Parent PR64 contained prior *actual native Rust component probe* matching original `AxbiSource`/Verner. New Python tagged transport **has NOT been compiled into Rust**. Do not claim native production execution or sign off full history.
- Mirocha et al. (2012), https://arxiv.org/abs/1204.1944: spectral discretization can change ionization/heating despite photon conservation. Baumschlager–Shen–Wadsley (2024), https://arxiv.org/abs/2310.16902: reaction-aware spectral representation near atomic edges. No numerical claim here imported from these papers.

## Immutable reproducible artifact

[Entire source/test/benchmark/CAS/plots/positive-negative controls](https://drive.google.com/file/d/131gI1H9zVvt-9SYhPPszTGbBzVq31zSo/view?usp=drivesdk) `BASS_CR_CODING_LOOP_20261015_SOURCE.zip`: **223,075 bytes**, 20 ZIP entries including 18 SHA256-manifest payloads. SHA256 `2c858d46471438e4107a1dd13faad8fbbc388a25976c0a0b48897ba7bbbc3673`. Local complete manifest and relocated tests confirmed.

Dropbox complete ID `id:BSpOijBcT10AAAAAAD7LtA`, path `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_CODING_LOOP_20261015_SOURCE.zip`, 223075 bytes. Provider remote assurance **R1 ACK/ID/name/size**, not full remote restore. Drive ID `131gI1H9zVvt-9SYhPPszTGbBzVq31zSo`. Cloud archive preserves full implementation/test; this Git item is the directly browsable handoff.

No original source, binary, AXBI DAG/STATE, running solver, report or user-owned archive overwritten. Existing BASS_CR Landau continuum coarse interval and unresolved fine constitutive-adjoint task unchanged.

## Next ready coding action

`CR_NEXT_COMPRESSED_THRESHOLD_SAFE_TRANSPORT`: design bounded-memory group/source representation that controls **photoionization and heat on every redshift step**, not just injection. First use the included `CohortTransport` as a reference and the 25→24.5eV fail as a regression. Owner requires separate versioned source ID/contract and matched trials before moving from sandbox to its AXBI experiment. Its AX11/AX12 pending status must not be changed solely on this supplier evidence.