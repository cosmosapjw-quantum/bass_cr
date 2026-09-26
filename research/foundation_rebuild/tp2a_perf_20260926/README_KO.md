# TP2A: CPU kernel acceleration and durable parallel geometry scan

기준: `a6be0e70db55bb60e493e102d04c64d67101da45`. 기존 파일을 수정하지 않는 sidecar다. 원래 FEM 기저, order24 거리 격자와 Bessel moments, weak-form H, 직접 D, complex128을 유지한다. s+p 전용이며 l>1을 조용히 삭제하지 않고 거절한다.

## 실측
동일 개발 호스트에서 18-channel, z=-12, order24 단일 스레드의 비프로파일링 측정:
- 원본 104.6403 s
- NumPy 중복 제거/벡터화 21.8633 s (4.79x)
- 선택적 C++ ring kernel 14.8152 s (7.06x vs original, 1.48x vs optimized NumPy)
- raw cross parity: 상대차 최대 약 9.3e-15; D_PT의 구조적 0도 유지.
- 3-process native 동일 snapshot 3개: 22.3436 s, 55.3095 CPU s; 직렬 결과와 배열 bytes 일치.
단일 측정의 관측값이지 모든 호스트의 보장 속도나 median benchmark가 아니다. 개발 호스트는 4 CPU quota, 4 GiB memory quota다. 로컬 5900X의 성능으로 오인하지 않는다.

## 무엇을 최적화했는가
원본 order10 profile에서 84% 정도가 basis_values에 있었다. radial 함수를 m/phi마다 다시 평가하고, 구면조화 다항식 dictionary와 powers, 좌표 norms, zero-ETF 지수함수를 반복 생성했다. 이를 거리 pair별 고유 radial 평가, 고정 s+p 다항식, 1024-pair batch, 연속 gradient 배열로 바꿨다. C++는 이 좁은 ring 평가만 담당한다. CDLL 호출은 GIL을 놓고, 외부 geometry 병렬화는 spawn processes라서 Python GIL을 공유하지 않는다. BLAS는 worker당 1 thread다. -ffast-math, 저정밀, 사후 symmetrization은 쓰지 않는다.

## 로컬 시작
공식 handoff의 exact commit으로 checkout한다. 기존 Python/NumPy/SciPy/pytest를 유지한다. 어떤 pip/apt 설치도 자동 실행하지 않는다.

```bash
BASE=research/foundation_rebuild/tp2a_perf_20260926
BUILD_TP2A="runs/tp2a_native_build_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/build_native.py" --out "$BUILD_TP2A"
```
컴파일러가 없으면 build는 명시적으로 실패한다. NumPy 경로는 C++ 없이 작동한다.

새 호스트 성능/동일성 검증:
```bash
OUT_PERF="runs/tp2a_benchmark_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/benchmark.py" --native-build "$BUILD_TP2A" --workers 8 --out "$OUT_PERF"
```
`benchmark.py`는 새 32 tests, 원본/NumPy/native 각 1회와 native 병렬 throughput을 비교한다. 동일 snapshot을 반복하는 것은 의도된 성능 실험이며 새 포획/단면적 계산이 아니다. 전체 TP2A scan은 이 명령에 들어 있지 않다.

## 현재 과학 gate
개발 TP2A는 -12,-10,-8에서 connection screen을 통과하고, -6에서 2.4019219676e-4 > 1e-6으로 중단했다. 원본 커널로 동일 세 시점을 계산했을 때 2.4019219670e-4였으며 cross 상대차 최대 약 7.1e-15였다. 최적화 회귀 오류가 아니라 기존 order24 연산자의 새 geometry/connection 실패다. epsilon, order, basis, threshold를 변경하지 않았다. 전체 13점 PASS라고 하지 않는다. 완료된 TP1을 무효화하거나 재실행하지 않는다.

따라서 지금은 위 benchmark만 로컬에서 실행하면 된다. -6 numerical blocker를 고치기 위해 같은 scan을 무작정 반복하지 않는다. 아래는 이후 명시적으로 scan을 재현할 때의 entrypoint다:
```bash
OUT_SCAN="runs/tp2a_scan_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_tp2a.py" --backend native --native-build "$BUILD_TP2A" --workers 8 --out "$OUT_SCAN"
```
`--workers`를 생략하면 실제 affinity/core/memory/cgroup 한도를 읽고 최대 8개를 선택한다. 요청 값이 안전 상한을 넘으면 조용히 바꾸지 않고 거절한다. NumPy-only는 `--backend numpy`를 사용하고 `--native-build`를 생략한다.

## 진행상황과 복구
실제 output 절대경로를 첫 줄에 출력한다. worker는 약 2초마다 처리한 radial pair 수를 보내고 coordinator는 5초 heartbeat를 기록한다. 다른 터미널에서는 **출력된 실제 경로**의 PROGRESS.jsonl을 읽는다. date로 OUT 변수를 새로 만들면 다른 경로가 된다.

각 완성된 S/H/D snapshot은 NPZ와 hash receipt를 원자적으로 저장한다. 같은 순간의 basis/trajectory/order/backend/native binary/source identity가 일치해야만 cache를 재사용한다. basis는 coordinator에서 한 번 구성한 coefficient payload를 모든 worker에 전달한다. 완료 시 RETURN_REPORT.json, MANIFEST.json, RETURN.zip을 만든다. 첫 오류 후 새 작업을 제출하지 않으며 in-flight 작업은 협력적으로 취소한다.

중단된 실행을 재개할 때만, 원본을 덮지 않고 새 output으로:
```bash
python3 "$BASE/run_tp2a.py" --backend native --native-build "$BUILD_TP2A" --workers 8 --resume-from "$OLD_SCAN" --out "$NEW_SCAN"
```
오래된 파일은 수정하지 않는다. source 또는 binary가 바뀌면 자동 cache migration을 하지 않는다. scientific FAIL은 resume로 해결되지 않는다.

## 검증 범위와 다음 작업
신규 32 tests에 원본 raw parity, 두 중심 모두 이동하는 D, channel permutation, batch 변경, invalid/disjoint geometry, native payload tamper, spawn/serial equality, cache salvage 및 standalone import를 포함했다. 기존 TP1 전체 전파나 GPU full run은 재실행하지 않았다. 정확한 근거는 VALIDATION_EVIDENCE.json과 전달 ZIP에 있다.

다음 과학 작업은 `FND_TP2A_ZMINUS6_CONNECTION_QUADRATURE_DIAGNOSIS`다. 원본과 최적화판이 함께 실패하는 -6의 적분/finite-difference 일관성을 조사해야 하며, 성능 문제와 혼동하거나 tolerance를 낮춰 통과시키면 안 된다.

항상 `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture_execution_allowed=false`다. 13개의 정적 표본이 성공해도 연속 궤적 오차상한 또는 capture 승인이 되지 않는다.
