# BASS_CR C10: source-conditioned threshold-split H/He spectral reaction supplier

이 폴더는 q-reference fixed-grid SOURCE07 C5의 원래 photon number/first-energy moment를 바꾸지 않고, **known fresh MD14 BB50K source**에 한정해 Verner HI/HeI/HeII threshold split positive GL quadrature로 frozen-neutral source-level photoevent/heat를 비교한다.

## 실행

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=src pytest -q tests
PYTHONPATH=src python src/benchmark_subcells.py --repeats 3 --rays 8 32 128 --workers 1 2 4 > results/MATCHED_SOURCE_BENCHMARK.json
python verify_package.py
```

물리 입력: original Simpson32-native48 fractions, 50,000K blackbody, q grid geometric `[13.6,433]eV`, nE64/128/256/512/1024; proper neutral HI/HeI/HeII `(0.0017575700008892194,0.0001429214010766023,0)` cm⁻³, dt1e10 seconds. Source photons/H `4.298036114764196e-8`. Binding energies and fit thresholds distinct. Signed `q_ref` requires owner-generated physical energy R and J applied once externally. No source/owner history edits.

`src/threshold_rt.py` is **unchanged frozen source dependency** from prior PR68 ancestry, included for relocation. New sources: `src/source_subcells.py` + `src/benchmark_subcells.py`; tests `tests/test_source_subcells.py`. It runs offline using numpy/scipy/pytest. Shape reconstruction invalid for arbitrary hardened unknown spectrum; new source variant only.

Read `REPORT_KO.md`, `docs/THEORY_KO.md`, `NEXT_DAG.json`, `results/MATCHED_SOURCE_BENCHMARK.json`.
