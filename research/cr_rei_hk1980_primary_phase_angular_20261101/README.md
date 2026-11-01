# Original HK1980 two-energy proton+H angular quantum scattering (BASS-CR→REI)
**Source-authentic research output, not production.** This branch preserves the original unfinished local HK worktree and reuses its verified source reconstruction, then produces a NEW 3,072-row (2 genuine energies × 2 charge-labelled elastic/CX channels × 768 positive Gauss–Legendre angles) source-derived DCS grid, with exact moment crosswalk. No empirical rate fitting, no interpolated invented phase, no REI IGM IVP.

Scientific source: Hunter & Kuriyan (1980), DOI 10.1016/0092-640X(80)90006-6, 674 manual primary phase cells from private WU088 R12 source archive SHA256 562aba864fa55119e8454f4484ae3b09433df990ab589a3b9725544a8b6a5913. DO NOT publish the private ZIP, handwritten original phase arrays, publisher scans or source-reconstruction credentials. Output is a finite-L calculated derivative of archival printed phases, not a publisher-authenticated full quantum dataset.

## Outputs
- `HK1980_PRIMARY_JOINT_4_ROWS.csv`: four **charge-labelled** original phase moment rows (copied byte-exact from protected local precursor; new worktree original immutable).
- `HK1980_VS_SCHULTZ2016_DCS_SIX_ANGLES.csv`: six distinct-source sparse sample comparisons, NOT source equivalence.
- `HK1980_SOURCE_DCS_2E_2CHANNELS_768ANGLES.csv.gz`: new original-phase-derived 3072-row angle-resolved DCS; includes nuclear/charged CM angle, proper jacobians, and total/MT/viscosity contributions.
- `ANGULAR_SCIENCE_RESULT.json`, `RESULT.json`: numerical outputs with all caveats, identities, units and hashes.
- `THEORY_AND_GATES.md`, `SCIENTIFIC_REPORT_KO.md`, `STAGE_EVIDENCE.md`, `HANDOFF_NEXT_THREAD_KO.md`: reusable theory, source, test, and stop decisions.

## Reproduce (authorized private source only)
```bash
cd research/cr_rei_hk1980_primary_phase_angular_20261101
HK1980_SOURCE_ZIP=/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip bash REPRODUCE.sh
```
Python 3.12+, numpy; source ZIP read-only. Local **26/26 regular**, **26/26 Python -O** PASS, 768-vs-1024 angular check and independent Legendre finite-L sum; GitHub CI NOT_VERIFIED. Avoid inferring spin-averaged proton transport, Maxwellian REI rate, actual Bianchi tilt or CMB observables. REI central 28/88, working 33/88, CR extension 0/3, delta0. Draft HOLD, NO_MERGE, NO_FORCE_PUSH, NO_REI_MUTATION.
