# Source-native original REI F05 H I resonance vs Thomson coefficient

This `bass_cr` research unit *consumes* original REI F05 H/He/thermal source data and computes **one precise original-physics material scattering input**, not an actual Lyα light curve or new 26-event IVP.

Original REI PR352 source: source-generated 46,080-cell accepted tick160 H/He electron + T and strictly **nonaccepted** preview tick161, original 27 source fields SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`. It is a private original-source consumer. The source file or archive is NEVER copied into this public Git branch.

Outputs: `REI_F05_HI_LYA_TO_THOMSON_46080.csv.gz` containing per-cell **derived ratio bounds only**, plus `RESULT.json` for total original-source H I neutral inventory, total saturated Lyα atomic scattering-area capacity and all free-electron Thomson area. Dimensions: σ in cm², N dimensionless atom/electron count, opacity ratio dimensionless. Not observed τ, not real Lyα photon budget, not true neutral 1s population. Ground-state-saturated, thermal-only line-centre model `g1=1, T_HI=Tgas`, source-independent nonthermal neutral cooling or microturbulence not modeled.

REI original 4 photoionizing photon-group model does not supply a separately source-matched 10.2 eV Lyα line photon occupation. This is a **conditional optical material contrast**, not a statement that actual source photons undergo Lyα resonance scattering.

Reproduce on an authorized machine with the same private source:
```bash
cd research/cr_rei_f05_lya_core_20261101
REI_F05_OWNER_PREVIEW=/path/to/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz bash REPRODUCE.sh
```
Python 3.12 standard library suffices for published code/tests. Local source readback and 15/15 normal +15/15 optimized tests. Independent same-author SciPy wofz numerical crosscheck performed outside repo; no distinct-author blind reviewer. Before claiming GHA CI, read real workflow status.

DAG: REI 28/88 reported, working 33/88, BASS-CR 0/3, all delta0; CR-OFF intact, Draft/HOLD, no merge, no force push, no production. Latest base BASS-CR PR158 `2ad9c6e1959afb92b876ecb82293040a579b0e81`.
