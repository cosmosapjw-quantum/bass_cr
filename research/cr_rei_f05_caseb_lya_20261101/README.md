# Native original REI F05 Case-B H recombination → conditional Lyα source

BASS-CR source-physics contribution: 46,080 original F05 accepted-tick160 H/He source material cells at native volume, H+ Case-B recombination event rate, conditional recombination-cascade Lyα photon source and independent original HII two-half source increment crosswalk.

Original REI inputs are PRIVATE: 27-column original H/He/thermal/electron source and 30-column original original-26event HII increment CSV, neither copied into public Git; all byte-locked. The exact source owner is REI PR356 at `cc1929982948265f6d0b0f699353b3170ccd1792`, original tick160/131072 is the last OFFICIAL accepted tick, tick161 is a shadow candidate. Three shape lanes are one physical source.

The original rate is `α_B,H(T) N_HII N_e/Vproper` per second. The optional recombination cascade Lyα line yield uses the externally published Dijkstra/Cantalupo temperature fit and is **not** a native F05 2p/2s level-population result. Its intrinsic line photon generation is NOT observed escape, surface brightness, a Lyα occupation field, ionizing four-group source, Thomson optical depth, or actual Bianchi photon transport.

Output `ORIGINAL_REI_F05_CASEB_LYA_RECOMB_46080.csv.gz` has 46,080 source-derived records×14 fields (no private original input columns), `RESULT.json` physical summary, reproducible script, tests, exact SHA manifests and local source-free archive. No new physics source owner or production behavior is created.

Use on an authorized machine with matching original private source and pinned REI owner:
```bash
cd research/cr_rei_f05_caseb_lya_20261101
REI_F05_OWNER_REPO=/path/to/REI356_OWNER_ORIGINAL_CHECKOUT bash REPRODUCE.sh
```

Local 17/17 normal and 17/17 optimized tests and native 46k alphaB parity PASS; standalone Decimal60 5-cell crosscheck PASS; source-inclusive cold reproduction and restoration reported separately by receipts when actually executed. REI central 28/88, working 33/88, BASS-CR optional 0/3, all Δ0. CR-OFF protected; Draft/HOLD; no merge/force push.
