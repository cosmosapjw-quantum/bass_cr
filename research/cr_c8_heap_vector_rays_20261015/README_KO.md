# BASS_CR C8: heap / NumPy batch / optional per-ray parallel optimization

Parent: `bass_cr` PR66 at `0a43dcbaf7691c04706800e3336c1fd5ceb056ce`.

**실행** (Python >=3.11, numpy, pytest):

```bash
python verify_package.py
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python src/opt_benchmark.py --repeats 5 > results/OPT_BENCHMARK_new.json
PYTHONPATH=src python src/parallel_benchmark.py > results/RAY_PARALLEL_BENCHMARK_new.json
```

원격/헤드리스 Linux의 `forkserver` 벤치마크는 *파일 경로에서* 실행해야 한다. `python - <<'PY'`와 같이 인터랙티브 stdin `__main__`에서 직접 multiprocessing을 시작하면 spawn/forkserver가 재수입할 파일 경로가 없으므로 실패한다. 이 원인·진단은 검증 중 실제 관측 후 `parallel_benchmark.py`로 수정했다.

설명 및 **정확한 scientific claim 범위**: `REPORT_KO.md`.

- Original source/test reference: `src/compressed_cohorts.py`, `src/threshold_rt.py`; 절대 변경하지 않음.
- Newly optimized implementation: `src/fast_compression.py` and `src/batch_observables.py`.
- Optional parallel/1+3 owner-safe adapter: `src/ray_parallel.py`, `src/ray_invariants.py`.
- Bench executable: `src/opt_benchmark.py`, `src/parallel_benchmark.py`.
- New tests under `tests/test_fast_compression.py`, `tests/test_batch_observables.py`, `tests/test_ray_parallel.py`, `tests/test_ray_invariants.py`. Previous 61 tests also preserved.
- Container source-independent physics examples and measured benchmark timing `results/*.json`, graphs `results/*.png`.

No existing REI AXBI checkpoint/campaign/source-model admission is changed. The signed Bianchi ray producer and the source angular Jacobian are **not implemented by this package** and must be supplied by the owner. The batch neutral gas is held fixed for a single step; full kinetic/chemical propagation remains separate.
