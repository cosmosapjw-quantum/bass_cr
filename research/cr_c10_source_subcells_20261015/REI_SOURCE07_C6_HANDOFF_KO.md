# SOURCE07 C6: bass_cr source-subcell supplier (review only)

Current owner source: rei_bianchi e9c52f14e6ce50bb3b3924cda4ba34472caa28b4, rust/rei_microphysics/src/axbi_q_grid.rs and research/source07_c5_fixedq_20261015/NEXT_C6.json. Its old 49/51-node checkpoints, source IDs, AX08/AX11/AX12 and chemistry are unchanged.

New independently executable implementation: research/cr_c10_source_subcells_20261015/src/source_subcells.py with original 50kK MD14 native48 Simpson-32 fractions, positive Gauss-Legendre 8 source-native and reference-q cell intersections, species Verner threshold 13.60/24.59/54.42eV, binding 13.598434599702/24.587389011/54.41776eV, and frozen-neutral exponential absorption rather than parent backward Euler. q-normal geometry R=Ephysical/Eref, owner angular J and birth epoch are inputs only, not calculated or applied twice here.

Matched z20 proper gas HI 0.0017575700008892194, HeI 0.0001429214010766023, HeII 0 cm^-3, dt 1e10s, emitted 4.298036114764196e-8/H: Python nE256 centroid reproduces native Rust total absorption 3.12053792820337006e-8/H to ~2.25e-22 and total heat 1.45995781352239345e-7eV/H to ~2.04e-21. Subcell HeI matches independent owner continuum reference 1.4281834584030507e-9/H at relative ~9.4e-12; native centroid error -1.21148%. Across q N_E64/128/256/512/1024, subcell stays near 1e-11 while centroid crosses from -1.21% to +0.408%. Real user Ubuntu pytest 47 PASS; frozen-neutral cached scalar 473.44ms vs NumPy batched 4.317ms for 128 independent states, matched formula.

Git-scoped command (ancestor threshold_rt dependency kept unchanged):
PYTHONPATH=research/cr_c10_source_subcells_20261015/src:research/cr_c5_budgeted_cohorts_20261015/src python3 -m pytest -q research/cr_c10_source_subcells_20261015/tests

Owner C6 next: in an isolated same-source/IC/clock short component compare physical q ray R, original R*J applied ONCE, all five signed q backgrounds, source H/He events and binding/heat against original C5 centroid and independent native/SciPy continuum; test energy reference Emax433eV and actual radiation evolved q-grid at a new versioned source identity. Fresh source conditional shape cannot be silently reused after arbitrary absorption or redshift: arbitrary spectra with same count and first energy moment can have different HeI/HeII rates across an ionization edge. No whole-cosmological-history admission is issued.

ZIP BASS_CR_SOURCE_SUBCELL_C10_20261015_SOURCE.zip, 169515 bytes SHA256 322b49381b8b8790bb063a604a3150d47285f0b114389e6544460d595f2fbb48, Drive 17jjXTamLb-0lcEhQopxYp8H4Nacca6-5, Dropbox id:BSpOijBcT10AAAAAAD7oug. No local Codex, native subagent NOT_RUN, no owner repo edits.
