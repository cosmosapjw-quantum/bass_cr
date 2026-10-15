# 실행 방법: BASS_CR C9/R5 Verner curvature and source-local cohort budgets

- 전제: Python >=3.12, numpy, scipy, mpmath, pytest. 원 `rei_bianchi` 또는 Codex 환경은 수정하지 않는다.
- `PYTHONPATH=src python -m pytest -q tests`
- `PYTHONPATH=src python src/curvature_benchmark.py --repeats 9 > results/CURVATURE_BENCHMARK.json`
- `PYTHONPATH=src python src/curvature_scaling.py --rays 32 --repeats 3 > results/PARALLEL_SCALING.json`
- `python verify_package.py`는 artifact SHA와 CRC 검사만 수행, scientific solver 미실행.

관심 클래스는 `CurvatureHeapCompressedCohortTransport`(빠른 float 상계)와 `DirectedCurvatureHeap`(85자리 dyadic/source bound 상향 계산). 기본 source `frozen_source(16)`의 cutoffs와 물리적 binding을 혼동하지 않도록 owner χ를 별도 지정할 수 있다. 각 허용 병합은 같은 광선·같은 source-age·같은 clock에만 사용해야 한다. Source Jacobian·Bianchi ray·아래의 CI/RCT/HH 물리 입력을 이 패키지가 대체하지 않는다.

- `src/curvature_bounds.py`: 2차 Peano/Jensen algebra, fit second derivatives, per-species event/heat bounds.
- `src/directed_curvature.py`: positive real expressions Decimal85 directed evaluation, cache, upward pair budget.
- `src/fast_compression.py`: 기존 heap의 `_pair_bounds` / `_accum` 확장지점, 디폴트 의미 유지.
- `src/curvature_benchmark.py`, `src/curvature_scaling.py`: 검증용 benchmark producers.
- `tests/test_curvature_bounds.py`: mpmath independent derivatives, physical-binding/fit distinction, 22 admitted vs 20 held, local per-ratio comparisons.

`REPORT_KO.md`, `NEXT_DAG.json` and `integration/REI_SOURCE07_C5_HANDOFF_KO.md`를 읽고 모델 scope/권한을 확인한다.
