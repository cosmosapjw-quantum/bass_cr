# F1 Intel/native engine admission 구현 계획

> 대상: Codex 구현 루프. 실제 과학 admission run은 이 계획의 마지막 별도 gate 전까지 금지한다.

## 목표

F0에서 archive-only M4가 N96에서 자격을 얻은 뒤, 다음 단계는 c64-g3/Intel 계열 호스트에서
새로 빌드한 analytic moment engine이 historical engine과 같은 numerical object를 계산하는지
독립적으로 승인하는 것이다.

F1은 성능 benchmark가 아니다. worker pool, 16/32/48/60 scaling, CF4, DOP853, capture를
시작하지 않는다. 새 engine이 source/basis/policy/parity gate를 통과한 이후에만 F2를 열 수 있다.

## Frozen inputs

- scientific source commit:
  `c954d68fdc86527453765a563b3a025351163ed9`
- TP2D full archive:
  SHA-256 `630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
- moment source:
  `moment_kernel.cpp`, SHA-256
  `90913155c0cfa80962d1cb00bb1b7ec0443170917c25913ac5e359979738ab30`
- historical library:
  SHA-256 `966146f0ca713251f8b73999b4d89595cf1820a8c2d36f5c6290387b70c68035`
- exact basis: TP2D archive의 `BASIS.json/BASIS.npz`; 재계산 금지.
- frozen runtime ladder와 screens: `F1_CONTRACT.json`.
- parity sample: `F1_REPRESENTATIVE_QUERIES.json`.

대표 query 15개는 archive 전체 1,279 queries에서 실제 selected q/h class 7종의
negative/positive edge query와 exact t=0을 선택했다. 임의 새 time을 만들지 않는다.

## 구현 위치

모든 신규 runtime code는 이 sidecar 아래에 둔다.

```text
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/
  runtime/
    native/
      cloud_engine.py
      engine_admission.py
      archive_evidence.py
    run_f1_engine_admission.py
    tests/
      test_cloud_engine.py
      test_archive_evidence.py
      test_engine_admission.py
      test_runner_contract.py
```

기존 TP2A/TP2D source 파일은 수정하지 않는다. 필요한 기존 함수를 import해 재사용한다.

## Phase A: F0 artifact import

F0 성공은 현재 사용자 보고 evidence로 기록돼 있다. F1 구현 전후 어느 시점이든
실제 F0 host artifacts를 `F0_ARTIFACT_IMPORT_CONTRACT.json`에 따라
F1 branch의

```text
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/
```

에 import한다.

필수:
- RETURN_REPORT.json
- RETURN ZIP
- F0_RETURN_HANDOFF.json
- ENVIRONMENT_RECEIPT.json
- HOST_F0 receipt

RETURN report/archive의 SHA와 size는 이미 고정돼 있다. 다른 파일은 실제 bytes에서 SHA를 계산해
receipt에 기록한다. 없으면 합성하지 않는다. F0 import 실패는 **F1 code 구현 자체를 막지는 않지만**
실제 F1 scientific execution은 막는다.

## Task 1: archive evidence reader

RED tests:
- TP2D archive hash tamper 거절.
- BASIS.json 또는 BASIS.npz byte tamper 거절.
- representative query JSON/NPZ hash mismatch 거절.
- query receipt의 time_hex/query_id/selected resolution mismatch 거절.
- zip-slip / duplicate member / missing member 거절.
- allow_pickle=False 외의 NPZ load 경로가 생기면 실패.

GREEN implementation:
- archive를 extraction 없이 우선 직접 읽는다.
- exact basis payload를 create-only temp/staging에 materialize하는 helper만 제공한다.
- archived query NPZ에서 `selected__S,H,D`와 모든 historical attempted
  `qXX_hY__{S,H,D}_{tp,pt}`를 읽는다.
- representative contract에 없는 query를 자동 대체하지 않는다.

## Task 2: cloud engine builder

RED tests:
- source SHA mismatch.
- forbidden compiler flag.
- extra `-march/-mtune/-Ofast/-ffast-math/-flto`.
- compiler subprocess nonzero.
- output library missing/zero bytes.
- current platform mismatch/engine receipt tamper.
- historical BUILD.json overwrite 시도.

GREEN implementation:
- source는 frozen checkout의 exact `moment_kernel.cpp`.
- required flags는 historical build와 동일:
  `-std=c++17 -O3 -fPIC -shared -ffp-contract=off -Wall -Wextra -Werror`.
- compiler path/version, full argv, source SHA, library SHA, platform.machine/system,
  CPU model/flags, libc, Python/NumPy/SciPy, BLAS를 `ENGINE_BUILD.json`에 저장한다.
- 별도 `ENGINE_IDENTITY.json`을 canonical JSON digest로 만든다.
- historical library SHA와 새 library SHA는 같을 필요가 없다.
- historical BUILD receipt나 GRANT를 수정하지 않는다.
- output은 create-only.

Unit tests에서는 실제 BASS 15-point scientific run을 하지 않는다.
compiler seam은 작은 synthetic C/C++ fixture 또는 subprocess mock으로 검증할 수 있다.

## Task 3: engine adapter

새 build directory를 기존 `MomentKernel` contract와 연결한다.

- compatibility `BUILD.json`은 새 library의 source/library SHA와 current machine/system을 담되,
  historical receipt와 별도 파일이다.
- 기존 `MomentKernel`의 source-hash check를 우회하거나 monkeypatch하지 않는다.
- `analytic_adapter.AnalyticEvaluator`와 `assemble(... phase_budget=None, sector='full')` semantics를 유지한다.
- exact TP2D basis bytes로 channels/trajectory를 만든다.
- `atomic_bank`를 다시 계산해 같은 basis라고 간주하지 않는다.

## Task 4: parity engine

각 15 representative query에서:

1. historical JSON/NPZ hash를 contract와 대조.
2. frozen resolution ladder를 새 engine으로 처음부터 순서대로 평가.
3. historical과 같은 selected q/h가 나와야 한다.
   다르면 즉시 `POLICY_SELECTION_DRIFT`.
4. historical이 실제 평가했던 모든 resolution의 raw cross arrays
   `S_tp,S_pt,H_tp,H_pt,D_tp,D_pt`를 비교.
5. selected full `S,H,D`를 비교.
6. `np.allclose(rtol=1e-11, atol=1e-12)`와 relative Frobenius를 모두 기록.
7. Hermiticity/metric/raw-convergence screen을 새 결과 자체에 다시 적용.

D의 양 방향은 서로 독립적인 raw arrays로 비교한다. S/H reverse conjugacy가 코드에서
derived라는 이유로 D 방향 비교를 생략하지 않는다.

## Task 5: metric-connection sentinel

z/a0 = -12,-6,0,6,12에서 historical TP2D 정의와 동일한 epsilon_z=1e-4를 사용한다.

- 새 engine으로 centered S derivative를 계산.
- direct `D+D†`와 비교.
- residual <=1e-6만 science gate다.
- historical residual과의 tight allclose를 요구하지 않는다. 차분 cancellation을 parity gate로 쓰지 않는다.
- 계산에 사용된 exact time_hex와 selected q/h를 모두 기록한다.

## Task 6: runner와 failure semantics

`run_f1_engine_admission.py`는 create-only output을 사용한다.

실행 순서:
1. self/source/contract verify
2. F0 durable evidence verify
3. TP2D archive/basis/representative verify
4. F1-new tests
5. engine build
6. representative parity
7. metric sentinel
8. final report/package

failure statuses는 `F1_CONTRACT.json` 값을 그대로 사용한다.

특히:
- compile failure != parity failure
- q/h selection drift != matrix parity failure
- runtime/environment failure != scientific numerical failure
- tests failure 후 science execution 금지

## Task 7: tests와 구현 완료 판정

Codex 구현 세션에서 허용되는 완료 상태:

```text
F1_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN
F1_IMPLEMENTATION_COMPLETE_F0_IMPORT_PENDING
F1_IMPLEMENTATION_BLOCKED
```

실제 `F1_ENGINE_ADMISSION_PASS`는 이번 구현 세션의 허용 상태가 아니다.

구현 완료 조건:
- 신규 focused tests PASS, failures/errors/skips=0.
- py_compile PASS.
- CLI `--help` import-safe.
- synthetic/tamper tests PASS.
- existing source files modified 0.
- branch diff가 F1 sidecar + imported F0 evidence만 포함.
- source manifest 갱신.
- local commit + remote push + R1 ref/tree verification.

기존 TP2D 18 tests나 TP2E 32 tests를 구현 완료용으로 반복 실행하지 않는다.
source semantics를 변경하지 않았으므로 중복 검증을 피한다.

## 실제 F1 execution gate

구현 이후 별도 승인 없이는 native admission을 실행하지 않는다.

필요 입력:
- F0 artifact import complete.
- 실제 c64-g3 또는 명시적으로 승인된 x86_64 admission host.
- `max_wall_seconds`.
- `spending_limit_krw` 또는 이미 과금 승인된 host라는 명시.
- disk/workspace 준비 상태.
- frozen F1 implementation commit/tree.

실행 전 contract 값을 수정하지 않는다. 예산 부족이면 workload를 자동 축소하지 않고
`F1_EXECUTION_BUDGET_BLOCKED`로 반환한다.

## Claim ceiling

F1 성공도 다음을 열지 않는다.

```text
capture_execution_allowed = false
production_admission = HOLD
all_bound = OPEN
b_grid = NO_GO
original_capture_gap_resolved = false
continuous_global_supremum_bound = false
```

F1의 성공 의미는 오직 **새 native engine이 frozen representative evidence에서 historical
engine/policy와 승인된 수치 parity를 보였다**는 것이다.
