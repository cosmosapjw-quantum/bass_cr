# BASS-CR PHYS14 | NIST 1s→2p versus Shah H ionization competing first electron event

Same original 6400 H/He RR photons and source proper-time birth bins from the byte-pinned PHYS13 full SOURCE archive. Single immutable parent archive `sources/PR138_ORIGINAL_SOURCE.zip` is supplied inside the complete PHYS14 ZIP, **not** committed to Git as binary. Self-contained script requires Python 3, numpy, scipy (for blind referee) and matplotlib (two scientific plots generated with plot_science.py). Run `bash REPRODUCE.sh` on a clean extracted full source ZIP to regenerate numerical CSV/JSON and validate SHA. Original Shah/Kim/Bray user PDFs are not redistributed. This model is conditional/restricted two-channel first inelastic and does not solve stopping, electron motion or gas/radiation background.

Main numerical source: `phys14_compete.py`; data: `nist_h_2p_cross_sections.csv`; tests `test_phys14.py`, independent method `blind_referee.py`; outputs `results/*.csv`, `results/RESULT.json` and two PNG figures. Study source and limitations in `THEORY_KO.md`, `LITERATURE.md` and `REPORT_KO.md`.

Central DAG 28/88, extension 0/3, scoped PHYS14 auxiliary 1/1 REVIEW_HOLD. R06/C09 distinct-author NOT_RUN; no merge, force push, auto-next, or production.
