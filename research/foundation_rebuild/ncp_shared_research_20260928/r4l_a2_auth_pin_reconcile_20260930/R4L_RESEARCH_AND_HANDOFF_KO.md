# R4L A2 authorization-pin reconciliation

Status: `A2_AUTHORIZATION_PROPOSAL_PIN_DRIFT__READ_ONLY_RECONCILIATION_REQUIRED`.

The final A2 resume package is `N1536_A2_RESUME_1f18e87_237846c79ecd_20260930.zip`, bytes `148359853`, SHA256 `237846c79ecdf6ed79f9ba1e68a98b4f5e3682bcb35009d88a06838d70e36472`. The Google Drive split backup was independently materialized and concatenated; both part hashes, the joined source SHA, ZIP CRC and manifest all pass.

Byte-backed authority pins inside the final package:
- source pins: `3ff0179fbe117586f6e2d737ff383397df495052084f575f1d4a541eed23708e`
- proposed N1536 query plan: `30b6a07769de454e419e07596ecf90fe797fde43da079abd1beeaa6c441d7314`
- useful pilot plan: `a6ae00971235e6b4955603eb081969376479324abe84413b37ba7c24e309e349`
- A1 salvage manifest: `483cbba45051d6cfe166ecada08670870d51291326cdfc9ff0668f715a6b682d`
- resume plan: `8a47946285b9da39bcce14756a7260aa20dc341c5e925b1b11b535973ebbfe99`
- pilot continuation plan: `e4fceb1427fa497eb413d21d68e4862197d350eb064ecdc6be0914c361bd8663`
- future authorization template: `c29bd9590d5e2d1336ec7f6544c5c475df548241d14bc567f44f236621ff7974`

The latest NCP/Codex human-readable summary reported the old pre-resume query-plan and source-pins hashes (`ec893...`, `985693...`). It is not yet known whether only the summary text is stale or the saved live authorization proposal JSON is stale. Native A2 must not start until the saved proposal is compared byte-for-byte to the final package values.

Required next action is read-only only:
1. sha256sum the final package authority files;
2. jq the saved live authorization proposal fields;
3. if proposal is correct, return `SUMMARY_TEXT_STALE__PROPOSAL_VALID`;
4. if proposal is stale, create a new create-only proposal JSON mechanically from the final template without changing code/commit/tree;
5. re-run a read-only CPU/RAM/external-BASS census;
6. keep the existing deadline `2026-09-30T10:29:46.685717Z` unless the user explicitly requests a new wall window;
7. confirm fresh A2 ID `R4G-N1536-ADAPTIVE-RESUME-20260930-A2` remains unused;
8. do not consume authorization or start native science.

A1 salvage contract remains: 16 stage-8 queries reused, A1 raw attempts 54, lifetime raw cap 16896, strict lifetime worst 16774, margin 122. No parity. CPU candidate remains ordered 0-31 only if the fresh census still passes.

No source mutation or native science is authorized by this research note.
