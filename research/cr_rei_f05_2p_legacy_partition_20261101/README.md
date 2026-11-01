# REI-F05 original H-excitation cooling: 2p contribution versus legacy operator

This is ONE original-source optional BASS-CR physical science unit stacked on original PR161. It does not add any new thermal source to REI, mutate original F05 code, or approve tick161. Frozen accepted parent tick 160/131072, private original source SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d.

Original legacy H I excitation cooling ne*nHI*Lambda_old ALREADY includes H excitation; separately estimated PR161 H(1s→2p) energy sink must not be added to it. The 12,528-row original-snapshot output partitions the empirical legacy energy sink into an explicitly 2p component and an **unassigned remainder**, under Te=Tgas and f1s=1 within the published 5000–20000 K collision-strength table. The remainder cannot be assigned specific atomic channels on existing evidence.

Run on the original authorized source host: `bash research/cr_rei_f05_2p_legacy_partition_20261101/REPRODUCE.sh`. It runs 16 original-source tests twice (regular and python -O), generates a clean deterministic gzip CSV and result JSON, checks source and exact output hashes, and validates this scoped manifest. Public Git clone is NOT source-complete without original private source owner. See `THEORY.md`, `SCIENTIFIC_REPORT_KO.md`, `RESULT.json`, `HANDOFF_NEXT_THREAD_KO.md`.

NO_REI_MUTATION; NO_MERGE; NO_FORCE_PUSH; PRODUCTION HOLD; CR-OFF unchanged. Central DAG 28/88, working 33/88, BASS-CR 0/3, all Δ0.
