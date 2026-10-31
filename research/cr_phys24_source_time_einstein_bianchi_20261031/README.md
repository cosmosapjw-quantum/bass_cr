# BASS-CR PHYS24 | original PHYS15 source clock × conditional Einstein dust Bianchi-I Lyα Stokes and first HI interaction

Date 2026-10-31 KST. This is **a new numerical physical-model dataset**, not code optimization or a new canonical DAG closure. Exactly sourced: PHYS15 original 27-row cumulative 2p clock and unchanged 2066-event total, PHYS22 global conditional E1 χ. Conditionally constructed: time-bin angle independence, within-bin emission age, three exact but externally specified Einstein–Bianchi dust geometries, recoil-free line shape, first HI interaction as a loss term. No original CR source-owned ray, shared Einstein–Boltzmann cosmology or physical RII was inferred.

## Original input authority
- Parent `cosmosapjw-quantum/bass_cr` immutable Draft PR147 `fac9a25d53468502b3807da2034e4bfa99325c8f`, PHYS23 complementary evidence PR148 `36eedc32f081567a9f345bffdfd9feafeff727c5` and PR149 `92980340065c2c1c32bcd97c4d860ba8ea5cbfa4` (all live verified 2026-10-31).
- Immutable original 2066-event blob SHA1 `d7034188ca5a02dc37db24aaf8f7d550624567bd` directly read back by GitHub at PR147 HEAD in this run.
- PHYS15 ZIP SHA256 `48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316`; PHYS23 ZIP SHA256 `22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111`; both restored and hashed locally in this session, PHYS23 archive 44/44 CRC.
- Exact original PHYS15 and PHYS22 subset bytes included in `input/`, hash checked in `phys24.py`. Original PHYS15 nested source ZIP and PHYS23 full ZIP are **not included again** in this PHYS24 package; restore by SHA from existing Library/Drive references.

## New science
- PHYS15 2 original birth policies ×8 source time increments =16 time interval injection data rows, inherited 5 PHYS22 E1 scenarios ×2 Bray upper anchors, 3 exact Einstein dust Bianchi-I backgrounds (one isotropic, one axisymmetric, one triaxial), 3 within-time-bin clock closures (start/mid/end).
- `results/SOURCE_TIME_INTERVAL_INJECTION.csv` (16); `EINSTEIN_BIANCHI_DUST_BACKGROUND.csv` (123); `TIME_RESOLVED_SKY_STOKES.csv` (207360); `TIME_RESOLVED_SPECTRA_FIRST_HI.csv` (105300); `INTERVAL_EMISSION_SPECTRAL_WITNESS.csv` (74844); `DIAGNOSTICS.csv` (180). **Total 387823 rows** across different data grains (not 387823 distinct independent physical events).
- Four real scientific PNG figures produced from these CSVs in `figures/`. See `THEORY_KO.md` for assumptions and exact equations, `BLIND_REFEREE_FINDINGS.md` for falsifiable limitations.

## Offline reproduction

Use Python3 with `numpy`, `scipy`, `matplotlib`. From this folder:

```bash
python phys24.py                          # full CSV, deterministic checked sources
python -m unittest test_phys24.py -q     # 18 physics, numerical, source/identity tests
python -O -m unittest test_phys24.py -q  # 18 tests with optimized Python interpreter
python plot_science.py                  # 4 PNG science figures
```

The full CSV reproduction is a heavy repeat; preserved original CSVs already ship. `results/RESULT.json` contains source and output hashes. If source ZIPs are provided separately, their original SHA256 can be compared to retained values. `RUN_CONTRACT.json` freezes pre-execution hypotheses and stop conditions. `VALIDATION.json` gives actual command outcomes. Never infer a native CI result from local tests.

## Scope and DAG
`SOURCE_COMPATIBLE_EINSTEIN_IVP=UNBOUND`; `PHYSICAL_K=UNBOUND`; `ORIGINAL_RAY_DIRECTION=UNBOUND`; `PHYS22_CHI_TIME_CORRELATION=UNBOUND`; `RII_DETAILED_BALANCE=NOT_RUN`; `FINE_HYPERFINE_2P_RHO=UNBOUND`; `GLOBAL_HE_EXCLUSIVE=UNBOUND`. This is an explicit `CONSTRUCTED_CONDITIONAL_REVIEW_HOLD` auxiliary. `CENTRAL_DAG=28/88 Δ0; EXTENSION_DAG=0/3 Δ0`, `PRODUCTION=NATIVE25=L4=HOLD`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`. Distinct-author R06/C09 and native subagent `NOT_RUN`.
