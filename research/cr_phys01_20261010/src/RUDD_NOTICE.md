# Rudd adapter provenance and license

`rudd.py` is distributed under **GNU GPL v3 only**, with `GPL-3.0.txt` in this directory. Its formula/parameter port is based on Mark R. Krumholz and contributors' CRIPTIC source, commit `e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92`, `Src/Losses/Ionization.H` (the upstream README specifies GPL version 3). This notice does not assign a new license to unrelated repository files.

The adapter adds a Python SI/eV interface, a selected 1–10 MeV proton support gate, differential secondary-electron production, and conservative interval moments. It fixes the upstream total-ionization expression's missing square: the integral of its differential kernel requires `F2*wmax**2`, whereas upstream uses `F2*wmax`. The stopping integral is unchanged. This discrepancy is preserved in `upstream_reported_total_cross_section_m2()` solely for an evidence comparison.

Atomic H uses the upstream Williams-limit coefficient choice. Neutral He uses the upstream Rudd empirical coefficients. H2 and He+ are outside this adapter's scope. This module neither asserts an experimentally certified accuracy over its selected interval nor provides all cosmic-ray energy-loss channels. Unmodeled primaries and unmatched secondaries must remain explicit energy reservoirs in the caller.
