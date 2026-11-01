# `bass_cr` CR→REI | low-energy p+H resonant exchange on original BASS193

Scope: BASS-CR-owned optional **ion-neutral CX event-rate** on the exact same BASS193 source/clock as the preceding CR-OFF Thomson receiver PR #153. **No mutation of REI or BASS geometry**; no new EoR IVP; actual primary-source rates are literature-fit, not original Schultz numeric dataset.

To reproduce the archived **192 physically conditioned model rows**, retain original upstream private file `REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip` (SHA-256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52`). This source ZIP is **not** embedded in public repo archive.

```bash
python -m pip install numpy scipy matplotlib
REI_SOURCE_ZIP=/absolute/path/REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip bash REPRODUCE.sh
```

Result: `results/BASS193_H_HPLUS_CX_SOURCE_CONDITIONAL_192.csv`, `results/RESULT.json`, four PNG+SVG plots. Original input byte hashes, 192 proper-time source clock, HII electron/neutral original density, analytic Maxwell log-velocity integral and physical zero-chemistry invariants are verified in `test_cx_screen.py`.

Literature fit: Titova, Izmodenov, Korolkov (2025), PASA Appendix A Eq.(A4), cross sections originally computed by Schultz et al. (2016), DOI `10.1088/0953-4075/49/8/084004`. The distinguishable charge exchange/elastic separation is less reliable at `g≲3 km/s`; fit computed only for 3--200 km/s, and full Maxwellian integration is printed as an **unadmitted extrapolation diagnostic**.

This repo is the *owner of optional p+H atomic/transport corrections*, `rei_bianchi` owns the actual H/He IGM evolving source and central 88-node DAG, and `bass` owns Bianchi geometry. No automatic CR adapter or merging into REI. See `SCIENTIFIC_REPORT_KO.md` and `REI_CONSUMER_CONTRACT.json`.
