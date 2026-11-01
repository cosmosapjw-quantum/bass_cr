# Original REI IGM F05 accepted tick160 46,080-node Cen92 versus SW91 H cooling

One source-native optional BASS-CR analysis stacked on frozen PR162, original source-owner F05 PR356 SHA locked. Compares the original-existing hydrogen collisional excitation cooling to Scholz & Walters (1991) optically-thin hydrogen cooling fit, as reproduced by Glover (2015). Both refer to energy removed from gas by H I electron-impact excitations, so they are **ALTERNATIVES**, not additive photon sources.

All 46,080 real original F05 accepted-tick160 cells have T within 2000–67000 K support. Native source volumes and proper microtick are actually consumed. Output is one derived-only 46k CSV with source model rate, signed power spread and first-order frozen delta lnT (not the original numerical defect or the actual tick161 solution). Model ratio ~+5.36% integrated; no acceptance of original tick161, no original REI mutation.

Primary files: `THEORY_AND_GATES.md`, `cooling_spread.py`, `test_cooling_spread.py`, `SCIENTIFIC_REPORT_KO.md`, `RESULT.json`, `REI_ORIGINAL_F05_CEN92_SW91_46080_DERIVED.csv.gz`, `HANDOFF_NEXT_THREAD_KO.txt`.

Run on the authorized original-source owner computer: `bash research/cr_rei_f05_sw91_vs_cen92_20261102/REPRODUCE.sh`. Original private F05 input is intentionally NOT in Git; a public-only clone cannot re-execute source-native data generation. Git includes source-free derived data, exact expected digests and tests. The original source-owner code, production branch, accepted history, adaptive policy, 14 ledgers and CR-OFF are never changed.

REI central 28/88, working 33/88, physical-fast 4/7, BASS-CR optional 0/3, all delta0, PRODUCTION HOLD. Stop more adjacent optional cooling surveys; prioritize source-owner native 26-event full/half/half and 14-ledger tick161 admission.

References: Scholz & Walters 1991 doi:10.1086/170587, Glover 2015 doi:10.1093/mnras/stv1781, Eqs.34–36.
