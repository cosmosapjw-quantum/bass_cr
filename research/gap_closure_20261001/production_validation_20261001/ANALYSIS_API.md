# Fresh static analysis API

`fresh_context_analysis.py` performs offline saved-matrix analysis only. Physical producers and source/native/input loading remain in R4U. Historical cache context IDs are never admitted into a fresh Fortran cache.

- `analyze_g02(lane_manifest_paths, output_path)`: validates the exact72-time union, fresh common Fortran context, completed supervisor/queue/cache receipts, all qualified query pairs, exact full/raw block binding, and per-lane full11-level caps. It calls unchanged `static_validation.compare_ladder` for eight centers. The returned status is a diagnostic; `physical_G02_closed` remains false.
- `freeze_g03_predictions(output_path)`: create-only frozen model record, intended before physics and bound by the parent run contract. Also supports the already-created root record schema `BASS_CR_G03_OFFLINE_MODELS_V1` with exact CSV/analyzer byte pins and purpose `FROZEN_BEFORE_ANY_R4V_PHYSICAL_CALL`.
- `analyze_g03(manifest_path, frozen_predictions_path, output_dir)`: validates predeclared model equality/source hashes and exactly two completed signed48 cache pairs, then calls unchanged saved-matrix rate analyzer and frozen model scorer. Historical baseline provenance is separate from the fresh Fortran context. Partial analysis output after a numerical failure is not success; completion is marked only by G03_RESULT.json.

CLI examples (paths absolute):

```sh
python -I fresh_context_analysis.py g02 --manifests LANE0.json LANE1.json LANE2.json LANE3.json --output G02_RESULT.json
python -I fresh_context_analysis.py freeze-g03 --output FROZEN_G03.json
python -I fresh_context_analysis.py g03 --manifest G03_PLAN.json --frozen FROZEN_G03.json --output NEW_G03_ANALYSIS_DIR
```

Call under OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1. Output paths are create-only. All cache identity validation precedes output creation. The adapter does not independently certify time ordering of a supplied freeze file: the parent run contract must bind its exact SHA before the physical run. Thirteen focused synthetic tests passed; no physical/native evaluator was constructed in these tests.
