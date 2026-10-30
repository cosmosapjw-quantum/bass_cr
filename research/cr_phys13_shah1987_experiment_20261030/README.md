# BASS-CR PHYS13 | original measured Shah1987 H electron-impact / source-conditional bridge

Original: PHYS12 **complete** SOURCE ZIP (SHA-256 locked). This package contains its original complete ZIP, source-authoritative 6400 H/He RR photon energies, 26 hand-transcribed original *measured* Shah et al. 1987 cross sections (Table 1 p3508, 14.6–21.4 eV), original reported ± 67%-level point errors and separate 6.8% correlated normalization uncertainty.

The new 6599 source-conditioned data rows cover measured knots, original photon atoms, time channels, 27 original birth-policy/epoch witnesses and source energy bins. Kim1992 is a *fit* not the original measurement. Values for electron E<14.6 eV are **not measured** and are not assumed physically zero; our 0 in a source-coverage integration is only a bookkeeping omission. Mean free path, local collision envelope and second-event capacity are conditional thought experiments. No physical stopping, full K, global He double-event, photon+neutral common evolution, production, merge or central DAG promotion.

## Reproduce

Run `bash REPRODUCE.sh` in the unzipped package directory; exact parent SOURCE ZIP is included in `sources/PR137_ORIGINAL_SOURCE.zip`. Source original 3 PDF files are **not redistributed** in this ZIP: use their recorded SHA-256 in `SOURCE_IDENTITY.json` to verify the user-provided inputs, including visible Table 1. The manually transcribed 26-row CSV is the executable numeric input.

For interpretation read `THEORY_KO.md`, `REPORT_KO.md`, `BLIND_REFEREE_EVIDENCE.json`, and `results/RESULT.json`. R/C files are retrospective notes, **not** 20 independent experiments. Distinct-author R06/C09 NOT_RUN.
