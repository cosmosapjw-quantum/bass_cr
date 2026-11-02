# REI F05 original MPRK H Case-B effective discrete transfers

One bounded original-source BASS-CR science unit stacked on immutable PR165. The original MPRK22(1) chemistry corrector uses `Fbar[e0,e1] * corrector_population / predictor_population`, NOT the Alexander-SDIRK thermal stage event quadrature of prior PR165. This code reconstructs original HII→HI Case-B donor-weighted effective transfer over original accepted 0→64, 64→128, 128→160 material.

**Real computed result** (46,080 original source cells each interval): MPRK total original accepted recombination transfer count `[2.6513808511756977e62,2.651394861400402e62]`. All 138,240 interval-cell net HII source transfer intervals overlap actual original accepted REIADP1 population changes, including the PR165 previously reported 336 mismatch cells at 0→64. This is a **discrete PDS transfer budget**, NOT an exact continuum chemical integral, independent particle emission, H Ly-alpha flux, accepted t161, CMB or production change.

Results: `ORIGINAL_F05_MPRK_H_EFFECTIVE_TRANSFER_3_INTERVALS.csv` (3 derived rows only), `SCIENCE_RESULT.json`, `SCIENTIFIC_REPORT_KO.md`, `THEORY.md`, `test_mprk_effective_h.py`. No private original REI/REC source input is committed.

Run on authorized original source machine with unchanged source and pinned original REC195 runtime:
`bash research/cr_rei_f05_mprk_effective_h_20261102/REPRODUCE.sh`.

Central REI 28/88 Δ0; working 33/88 Δ0; Physical Fast 4/7 Δ0; BASS-CR extension 0/3 Δ0. CR=OFF intact, production HOLD, no merge/force push/source mutation.

Cold extracted source-free tar replay requires the immutable parent PR165 `research/cr_rei_f05_h_caseb_stage_integral_20261102/native_h_caseb.py` as an adjacent sibling (a read-only symlink is sufficient), plus the authorized private REI and REC195 inputs. Its original parent source code SHA256 is `7d73a3ecd47966abdbb254941581b66e92f1914799c05162985243b7d4a91075` and is explicitly checked. The archive is source-free, not a self-contained copy of private source data or all ancestor modules.
