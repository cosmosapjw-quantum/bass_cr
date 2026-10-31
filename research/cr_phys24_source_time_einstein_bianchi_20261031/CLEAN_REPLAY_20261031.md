# PHYS24 clean-room local replay, separate from the PHYS23 parent

- Project: cosmosapjw-quantum/bass_cr.
- Parent PR #149 commit: 92980340065c2c1c32bcd97c4d860ba8ea5cbfa4. Immutable PHYS22 PR #147 commit fac9a25d53468502b3807da2034e4bfa99325c8f; sibling PHYS23 raw-archive PR #148 commit 36eedc32f081567a9f345bffdfd9feafeff727c5.
- Independent isolated working directory: `/mnt/data/phys24_clean_replay_20261031` in the computation runtime (not an external author or native subagent).
- Executed sequence: `python phys24.py`; `python -m unittest test_phys24.py -q`; `python -O -m unittest test_phys24.py -q`; `python plot_science.py`. Every command exit code 0.
- Both unittest invocations passed 18/18. Source-input hash guards were active.
- All six newly generated scientific CSV files matched the frozen package **byte-exact**. All four regenerated PNG figures matched **byte-exact**.
- 387,823 mixed-grain rows: 16 injection bins, 123 background rows, 207360 sky Stokes, 105300 frequency/first-interaction rows, 74844 pulse witnesses, 180 diagnostics.
- Source PHYS15 ZIP SHA-256 `48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316`; source PHYS23 ZIP SHA-256 `22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111`; original 2066-event blob `d7034188ca5a02dc37db24aaf8f7d550624567bd`.
- PHYS24 full source/data/figures archive: `BASS_CR_PHYS24_SOURCE_TIME_EINSTEIN_BIANCHI_20261031_FULL.zip`, 11,365,887 bytes, SHA-256 `906556e9c4f1e2f926736a26175e8a5689a1cdf91071957fd10d8a9ac2c13f9f`.
- Google Drive ZIP: https://drive.google.com/file/d/1ya7yrT8OAFwWwOsziRdwLEZ6P5HKcXXv/view ; Library ZIP: `/BASS/bass_cr/CR_PHYS24_SOURCE_TIME_EINSTEIN_BIANCHI_20261031/BASS_CR_PHYS24_SOURCE_TIME_EINSTEIN_BIANCHI_20261031_FULL.zip`. Both restored and matched the original archive by SHA-256 and byte comparison.
- The large CSV data and four figures are in the external archive, not in this code-facing Git PR. `python3 phys24.py` reconstructs six CSVs exactly, then tests run.
- Exact Einstein-dust Bianchi I is **conditional** and NOT demonstrated to be the original CR source's Einstein IVP. Emission-bin time, source angular correlation, physical RII, recoil and global He exclusivity remain unbound.
- Same-author local checks only. `R06_DISTINCT_AUTHOR=C09_DISTINCT_AUTHOR=NATIVE_SUBAGENT=NOT_RUN`; `GITHUB_NATIVE_CI=NOT_VERIFIED`; `CENTRAL_DAG=28/88`, `EXTENSION_DAG=0/3`, `PHYS24_AUX=1/1_REVIEW_HOLD`. No merge, force-push or production claim.
- Runtime: CPython 3.13.5; NumPy 2.3.5; SciPy 1.17.0; Matplotlib 3.10.8.
