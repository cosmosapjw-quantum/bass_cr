# BASS_CR C5: 보존형 spectrum-cohort compression (연구/검증용)

이 ZIP은 `rei_bianchi` production 소스가 아니다. 실제 `bass_cr`에 게시한 C5 소스 파일과 source-bound 비교/테스트를 포함한다.

Python 3.13, NumPy/SciPy/pytest가 있는 환경에서:

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python src/compression_benchmark.py > /tmp/compression_result.json
python verify_package.py
```

`src/threshold_rt.py`: frozen source와 Verner 원자율/비압축 코호트. `src/compressed_cohorts.py`: 48→32, 4-step 240→32 보존형 압축. `src/compression_benchmark.py`: 직접 결과 재생산. `src/benchmark.py`/`tests/test_threshold_rt.py`: 부모 C5 검증 입력/코드 (변경 없음).

전역 보장은 아니다. 오차 상계는 **같은 중성원자 상태와 BE dt**에서 `[r_min,1]`의 한 단계 흡수량/광가열에 대한 조건부 exact-real 수학식이며 floating outward 검증·결합 방정식 전파는 미완료다. `CompressionHold`는 손실을 숨기지 않는 정상 출력이다.

`REPORT_KO.md`와 `NEXT_DAG.json`을 먼저 읽어라. 원본 `rei_bianchi` 소스와 active Codex 세션을 바꾸지 않는다.

## v2 SOURCE07 C3 연동

원 frozen source 주입은 13.6–100eV이지만 독립 `CompressedCohortTransport`는 50keV까지 packet physical energy를 지원한다. `rei_bianchi`의 SOURCE07 q ray producer가 432.2293723204678eV packet을 내면, 그 source identity와 각도 Jacobian을 유지한 채 `(energy_eV,count_per_H)`로 입력 가능하다. `redshift(ratio)`는 owner가 제공한 실제 Bianchi characteristic ratio를 받는다. `max_cohorts`/absorption local budgets는 ray별·clock별로 검사해야 하며, 기존 AXBI fixed-q photon stage를 무단 교체하지 않는다.
