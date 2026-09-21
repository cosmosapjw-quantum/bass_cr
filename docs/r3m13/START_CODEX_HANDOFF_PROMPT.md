# BASS CR R3M13 -> local Codex start

Owner: CR. This is the preparation-control continuation of R3M12, not a new
Nichols source-code request. Authors' code/data remain unavailable and are not
prerequisites.

## Identity and preservation
Start from `02546302a3d6958ea9fa97488a670672e07be178` or a verified descendant
containing these R3M13 additions. Use the published R3M13 branch in a separate
worktree. Do not modify main, old evidence, old source snapshots or old manifests.
Read docs/r3m13/REPORT_KO.md and the pinned R3M12 return README first.
Numerical source digest must remain:
`581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`.
The new utility is deliberately outside cr_repro/*.py so old seals remain valid.
Do not copy it into that package.

## Tests and tiny replay
Use the existing project virtual environment, Python/NumPy and optional CuPy.
Record exact environment versions. Run:
```bash
python -m pytest -q -p no:cacheprovider tests/test_r3m13_initial_pair.py tests/test_r3m11.py tests/test_r3m11_jobs.py
python scripts/r3m13_initial_state_pair.py --help
```
The research environment ran these as 46 PASS. This is not a full-suite or GPU
claim. Repair failures with preserved RED evidence; do not change tolerance to
obtain PASS. Before using a different numerical source, reconcile its physics.

## Production preparation-only pair
Choose a fresh OUTPUT_ROOT under the local large disk. Execute sequentially:
```bash
export OUT=/mnt/sn850x2t/bass_cr_r3m13_preparation_20260922
mkdir -p "$OUT"
python scripts/r3m13_initial_state_pair.py prepare \
  --config configs/r3m13/tdl_dx025_imag025_T30.json \
  --out "$OUT/initial025" >"$OUT/initial025.stdout" 2>"$OUT/initial025.stderr"
python scripts/r3m13_initial_state_pair.py prepare \
  --config configs/r3m13/tdl_dx025_imag0125_T30.json \
  --out "$OUT/initial0125" >"$OUT/initial0125.stdout" 2>"$OUT/initial0125.stderr"
python scripts/r3m13_initial_state_pair.py compare \
  --first "$OUT/initial025" --second "$OUT/initial0125" \
  --reference-probability 0.00775827737938 \
  --relative-screen 0.01 --out "$OUT/pair.json" \
  >"$OUT/pair.stdout" 2>"$OUT/pair.stderr"
```
Use a fresh output path if it already exists. Do not delete failed receipts.
Preparation currently restarts from scratch after an interruption. Completed
initial.npy and receipts are immutable; compare uses mmap and bounded workspace.
Only initial states and target-only single-step diagnostics are produced here.
Neither helper nor compare starts a collision run.

The reference scalar is the archived R3M12 value, but the CLI does not by itself
prove its association to newly recreated initial bytes and identical K/Q.
`reference_anchor_verified=false` and `roundoff_certified=false` are intentional.
A floating screen is not a permission to skip the following physics task.

## Exact next R3M12-requested collision
Run only the new production preparation at dx=.25, real dt=.05, fixed CAP:
```bash
python -m cr_repro.r3m11 run \
  --config configs/r3m13/tdl_dx025_imag0125_T30.json \
  --out "$OUT/collision0125" --max-steps 128 \
  >"$OUT/collision0125.chunk001.stdout" 2>"$OUT/collision0125.chunk001.stderr"
```
Repeat in bounded chunks with new log filenames until completion. The inherited
runner repeats preparation at the first chunk; this release does not inject
saved initial arrays into that runner or alter checkpoint identity. Verify its
initial energy/residual against preparation receipts. Preserve config/source
hashes and seals at each completed chunk.
Do not launch a full b-grid, 50/225-keV run, fresh AOCC expansion, physical rate
or production central selection.

Compare new final `analysis.gram_audit.P_span_nmax` against R3M12
`tdl_refined_dx025` = .00775827737938 using the original reference denominator.
Read full result JSON rather than rounded README values for the final report.
List H residual, no-CAP target ray defect, finite-span probability, region
probability, initial-state ray distance, and source/config identities separately.
Do not label finite-span complement continuum, or a one-pair pass asymptotic
convergence. If the preparation control still fails, stop with NO_GO and
preserve the result; do not add finer spatial jobs automatically.

## Backup and publication
R3M12 archive remains separately pending on Google Drive:
name BASS_CR_R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921_v1.tar.gz
bytes 1231876036
sha256 3be00617f99387ffec406de5fa47000c5d2b8f56a9e9767f4fdcb1b6bc790fa6
Read provenance/r3m12_delivery/DUAL_BACKUP_RECEIPT.json and the existing
Drive multipart manifest before any retry. Preserve its original chunk plan.
Use only existing authorized Drive/Dropbox connections. An unavailable Drive
credential is a backup blocker, not a reason to label a local synced directory
an online backup. No need to reupload an already verified Dropbox original.
Do not infer zero search hits mean object absence.

For new R3M13 output, create immutable manifest and detached receipt; upload
to the established BASS_DERIVATION_DOSSIERS_20260912 folder in both providers.
Record actual upload success, object IDs, sizes, and raw readback/hash checks.
Do not write dual_backup_complete=true unless both provider claims are verified.
Commit small reports/configs/failure ledgers to a dedicated branch in bass_cr.
Large initial/final arrays stay in archived backup, with pointer/hash in Git.
No force push, main merge or rewriting historical tests.

## Return node
`R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN`.
Return a Korean summary, machine-readable decision, source/config/array hashes,
preparation and collision receipts, one-pair comparison table, backup receipts
and current GitHub SHA. Global b-grid status remains NO_GO unless a later,
separate complete convergence review explicitly changes it.
