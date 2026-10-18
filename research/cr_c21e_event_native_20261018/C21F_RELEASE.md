# C21F recovered release: publication retry, 2026-10-18

This release publishes the final recovered C21F source, not a new research run. It is based on immutable C21E PR80 `82c71000fccf0e353534080efbbf4eff7f31ac4c`; original native owner remains `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`. No NCP job, checkpoint, upstream owner or existing branch is edited.

## Important reconciliation

Current inspection found a historical partial C21F branch `research/cr-c21f-optical-depth-reference-20261018` at `7905762c63dcdd40f107ff33e3d19ca26c33bca1` and intermediate R5/C5-C6 cloud files. Therefore the preceding blanket statement that no C21F publication/backup existed was too broad. Those objects are preserved. They are not the final recovered 56-test source. This new branch is `research/cr-c21f-recovered-release-20261018` and publishes the final archive's executable bytes without merging the earlier partial variant.

## Exact source and scope

Four core files fix the external private-API call, provide the cumulative-optical-depth continuous Radau reference, remove absent-He fixed unknowns, and add 12 tests. The optional study runner and measured summary are included. Source files are byte-identical to the final recovered archive. This is the same science as the previous completed C21F unit; no new native Rust or Grackle run occurred here.

Fresh publication-stage check: 56/56 pytest, exit 0, 11.85 s, plus Python compileall and both shell syntax checks. Earlier red/green evidence, full accepted-step results and all 102 payloads are retained in the immutable archive. Source code is directly runnable from this branch; do not apply the previous embedded patch on top.

Default Radau coordinates are `optical-depth`; `--reference-coordinates population` remains explicit. The new reference reconstructs N=N_birth exp(-tau), retains log-survivors/underflow counters and does not clip internal gas variables or switch methods after failure. Same scalar tolerances in the two coordinates do not mean identical physical error criteria. Manufactured nonphoto rates and fixed GL2 three-energy source results are not native Grackle/source-age/spectral/global EoR certification. Native compiler and actual native runs remain NOT_RUN.

## Verified immutable archive

`BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip`, 394429 bytes, 102 payloads.
SHA256 `4bd711063c1d8d4e7724da693f8e021fd6742f5a1edfda3cbecd12f0956ed768`.

- Google Drive: https://drive.google.com/file/d/1jeaxLIO24gJDyhLvTUvAMTBcX0HogL3O/view
- Dropbox: `/bass_cr/C21/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip`, file ID `id:BSpOijBcT10AAAAAAD_Mug`.
- ChatGPT Library: `/BASS_DERIVATION_DOSSIERS_20260912/bass_cr/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip`.

All three copies were actually downloaded and checked: full archive SHA, ZIP CRC, and 102/102 file SHA/size pairs match. The archive is immutable and retains historical pre-publication handoffs/receipts; current `C21F_RELEASE.md` and newly published handoffs supersede their publication status, not their science. The original C21E README, DAG and manifest are historical for C21E.

## Next action

Use the new published Codex/NCP handoff. Checkout the execution commit specified there in an isolated worktree, run existing `run_ncp.sh NEW_OUTPUT ALLOCATED_CPU [EXISTING_OWNER_REPO]`. Native compiler/API compatibility may still require a small observed repair, not new algorithm implementation. Do not use historical CPU55 without checking ownership. Source48, source-age/spectral/angular convergence, Case-B, signed Bianchi and full EoR remain HOLD.
