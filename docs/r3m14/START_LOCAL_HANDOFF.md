# BASS CR R3M14 local execution handoff, v2

Work unit: `R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN`.

Start from a verified descendant of `d04124e8a1b83f29fd26baa13f11cd68a8f33c15` containing the R3M14 v2 witness. Do not modify `main`, archived evidence, `cr_repro/*.py`, old checkpoint seals, or old backup manifests. Required `cr_repro` source digest: `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`.

Read `docs/r3m14/PREFLIGHT_KO.md`, `docs/r3m13/REPORT_KO.md`, and the R3M12 return README first.

## 0. Environment and tests

Record exact OS, Python, NumPy, SciPy, CuPy/CUDA/driver and GPU identity. Run at minimum:

```bash
python -m pytest -q -p no:cacheprovider \
  tests/test_r3m14_collision_initial_witness.py \
  tests/test_r3m13_initial_pair.py \
  tests/test_r3m11.py tests/test_r3m11_jobs.py
python scripts/r3m14_collision_initial_witness.py --help
```

Do not relax tolerances to obtain PASS. A dependency/import failure is an environment blocker, not a physics failure. Preserve logs. Before production, verify that `scripts/r3m13_initial_state_pair.py` is the canonical helper and that its recorded preparation receipts carry its exact `script_sha256`.

## 1. Production preparation pair

Use a fresh large-disk root:

```bash
export OUT=/mnt/sn850x2t/bass_cr_r3m14_20260922
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

Record both full receipts, `initial.npy` SHA-256 values, production phase-aligned `d`, `d_star`, stationary residuals, energies, no-CAP one-step ray defects and CAP survival norms. The archived probability remains only a scenario anchor until the collision result and all identities are bound.

## 2. Bind the actual collision initial state

Start the `.0125 x 2400` collision through the v2 wrapper, not the raw runner:

```bash
python scripts/r3m14_collision_initial_witness.py \
  --config configs/r3m13/tdl_dx025_imag0125_T30.json \
  --prepared "$OUT/initial0125" \
  --out "$OUT/collision0125" --max-steps 128 \
  >"$OUT/collision0125.chunk001.stdout" \
  2>"$OUT/collision0125.chunk001.stderr"
```

The wrapper first reuses the canonical R3M13 `load_prepared()` validation, then additionally requires canonical-JSON config identity, exact R3M13 helper-script SHA, preparation normalization, and preparation/runtime equality for the fields R3M13 records (`python`, `numpy`, `backend`). It computes a typed digest over dtype, shape and numerical bytes of the state actually returned by inherited `relaxed_initial()`.

Before the first real-time step, require `r3m14_initial_binding.json` with:

- `schema=BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V2`;
- `status=PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED`;
- `array_digest_match=true`, `norm_match=true`, `environment_match=true`;
- canonical `cr_repro` source digest;
- canonical R3M13 helper SHA;
- prepared receipt/file/array hashes;
- v2 instrumentation SHA and enriched config hash;
- runtime environment record.

Any mismatch is `STOP_PROVENANCE_FAIL` and must occur before `state.json` is created. The wrapper must not substitute, normalize, cast, or inject the saved preparation. It returns the inherited `psi` object unchanged.

## 3. Resume bounded chunks

Repeat the same wrapper command with fresh log names and identical config/prepared/out paths. On resume, v2 requires the prior PASS binding plus unchanged source digest, R3M13 helper SHA, instrumentation SHA, prepared receipt/file/array hashes, enriched config hash, and full recorded collision runtime environment before delegating to the inherited sealed-restart validator.

Never delete a RED checkpoint or binding receipt. Never resume an unsealed/source-mismatched checkpoint. After completion require `result.json`, final sealed `state.npy/state.json`, `r3m14_initial_binding.json`, and `r3m14_witness_run_receipt.json`.

## 4. Decision gate

Compare final `analysis.gram_audit.P_span_nmax` against R3M12 same-grid reference `0.00775827737938`, using that value as denominator.

Report separately the production pair `d`, trace distance and conditional interval; each preparation's Hamiltonian residual and target-only ray defect; actual internal-initial binding; final finite-span probability; `P_region`, norm, Gram condition/eigenvalues and gap diagnostics; relative same-grid change; source/config/state/seal/helper/instrumentation hashes; exact runtime environment; chunk/restart history.

Gate semantics:

1. binding/provenance mismatch -> `STOP_PROVENANCE_FAIL`, no propagation;
2. production `d>d_star` -> preparation-pair `NO_GO`;
3. final same-grid finite-span change >1% -> preparation-control `NO_GO`;
4. pair and collision screens <=1% -> only `PREPARATION_CONTROL_PASS_SCOPED`.

A scoped PASS does not overturn inherited spatial `NO_GO` (`dx=.3125 -> .25` changed 2.289941%), does not authorize a b-grid, and does not turn finite `n<=3` span into all-bound or continuum probability.

## 5. Backup and return

Create an immutable R3M14 production archive and manifest. Upload create-only to the established BASS dossier destinations in both providers. Record actual IDs, sizes, and provider readback/hash evidence. Set dual-backup complete only after both provider claims are independently verified. Keep the older R3M12 Drive multipart 1/19 issue separate.

Commit only small code/report/receipt pointers to a dedicated branch. Large arrays remain in the dual archive. No force push or `main` merge.

Return a Korean report and machine-readable decision. After a scoped preparation PASS the next node is only `R3M15_SPATIAL_REFINEMENT_DECISION_GATE`; do not automatically launch `dx=.20`.
