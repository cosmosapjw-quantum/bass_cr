# BASS CR R3M14 local execution handoff

Work unit: `R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN`.

Start from a verified descendant of `d04124e8a1b83f29fd26baa13f11cd68a8f33c15` that contains this R3M14 preflight sidecar. Do not modify `main`, archived evidence, `cr_repro/*.py`, old checkpoint seals, or old backup manifests. Required `cr_repro` source digest: `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`.

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

Do not relax tolerances to obtain PASS. Dependency/import failure is an environment blocker, not a physics failure. Preserve logs.

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

Record full receipts, both initial `.npy` SHA-256 values, production phase-aligned `d`, `d_star`, stationary residuals, energies, no-CAP one-step ray defects and CAP survival norms. The archived probability remains a scenario anchor until collision and identities are bound.

## 2. Byte-bind the actual collision initial state

Start the `.0125 x 2400` collision through the preflight wrapper so the state actually returned by inherited `relaxed_initial()` is hashed before the first real-time step and matched against `$OUT/initial0125/initial.npy`.

```bash
python scripts/r3m14_collision_initial_witness.py \
  --config configs/r3m13/tdl_dx025_imag0125_T30.json \
  --prepared "$OUT/initial0125" \
  --out "$OUT/collision0125" --max-steps 128 \
  >"$OUT/collision0125.chunk001.stdout" \
  2>"$OUT/collision0125.chunk001.stderr"
```

Before propagation, require `r3m14_initial_binding.json` with `status=PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED`, `array_digest_match=true`, `backend_match=true`, canonical source digest, prepared receipt/file/array hashes, instrumentation SHA and enriched config hash. Any mismatch must abort before `state.json` exists.

The wrapper observes and returns the original `psi` object. It must not substitute, normalize, cast or inject the saved preparation into the numerical runner.

## 3. Resume bounded chunks

Repeat the same command with fresh log names and identical config/prepared/out paths. The wrapper must verify the original binding receipt before delegating to R3M11 restart validation. Never delete a RED checkpoint or binding receipt. Never resume from an unsealed or source-mismatched checkpoint.

After completion require `result.json`, final sealed `state.npy/state.json`, R3M14 binding receipt and witness-run receipt. Read full precision from JSON.

## 4. Decision table

Compare final `analysis.gram_audit.P_span_nmax` against R3M12 same-grid reference `0.00775827737938` using that value as denominator.

Report separately: production initial-pair `d`, trace distance and conditional interval; each preparation's Hamiltonian residual and target-only no-CAP ray defect; internal-initial binding status/hash; final `P_span_nmax`; `P_region`, finite-grid norm, Gram condition/eigenvalues and gap diagnostics; relative `P_span` change; source/config/state/seal/instrumentation hashes and exact environment.

Gates:
1. binding mismatch -> `STOP_PROVENANCE_FAIL` before propagation;
2. production `d>d_star` -> preparation pair `NO_GO`;
3. final same-grid finite-span change >1% -> preparation control `NO_GO`;
4. if both screens are <=1%, report only `PREPARATION_CONTROL_PASS_SCOPED`.

Even a scoped PASS does not overturn inherited spatial `NO_GO` (`dx=.3125 -> .25` changed 2.289941%), does not authorize a b-grid, and does not make finite `n<=3` span an all-bound or continuum observable.

## 5. Backup and return

Create an immutable R3M14 archive plus manifest. Upload create-only to established BASS dossier destinations in both providers. Record actual IDs, sizes and provider readback/hash evidence. Do not set dual-backup complete until both provider claims are verified. Keep older R3M12 Drive multipart 1/19 issue separate.

Commit only small code/report/receipt pointers to a dedicated branch. Large arrays stay in the dual archive. No force push or main merge.

Return a Korean report and machine-readable decision. Next node after scoped preparation PASS is only `R3M15_SPATIAL_REFINEMENT_DECISION_GATE`; do not launch `dx=.20` automatically.
