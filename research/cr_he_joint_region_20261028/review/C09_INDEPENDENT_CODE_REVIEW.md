# C09 — 독립 코드·과학 수용 검토

**판정: 명시한 API 표현 규약과 실행 범위에서 PASS; 현재 native 연구 수용을 막는 결함 0.** 기준 출판은 C8 `527840221887e9777031f2a6f281d48cb1ac42ef`다. 검토자는 core 구현 작성자가 아니며, `joint_region.py`, `cpp_backend.py`, `integer_flow.cpp`, `worker.py`, `THEOREM.md`, controls RESULT/CASES, native SUMMARY, independent RESULT, C08_REPRODUCIBILITY를 읽었다. Bin validator와 oracle/checker의 범위·집계 정의도 필요한 부분을 읽었다. 별도 비작성자에게 C++ seam만 정적으로 교차검토시켰다.

이번 C9에서는 코드 실행·import·컴파일·solver·NPZ 배열 로딩·원격 게시를 하지 않았다. 저장된 실행 근거의 검토이며 새 재실행 PASS가 아니다. 원본 코드나 다른 파일을 변경하지 않았다.

## 1. 발견사항과 최소 조치

| 대상 / 증거 | 영향 | 최소 조치와 상태 |
|---|---|---|
| **일반 integer bin과 direct API 범위 차이.** CONTRACT/R03는 integer labels를 허용하지만 `joint_region._input`이 재사용하는 `cross_flow.validate_atoms`는 `type(partition) is int` 및 `partition>=0`를 요구한다. | 음수 label의 수학적으로 유효한 fixture를 direct API가 그대로 받는다는 주장은 틀리다. Native labels 0..3 및 저장된 결과에는 영향이 없다. | 아래 canonical-label convention을 공개 API 문서에도 명시한다. **표현 규약으로 수용 가능한 차이이며 native blocker 아님.** 기존 frozen contract/theorem을 조용히 축소하지 않는다. |
| **Residual 교환의 실행 coverage.** controls CASES의 강제 교환은 `residual_augmentations=1`, `maximum_residual_path_edges=1`이다. | reverse HL edge를 포함한 긴 경로 및 제거 LL edge의 다른 끝 q가 내부 path low인 경우가 실제 실행되었다고 주장할 수 없다. | 이 한계를 보존한다. 해당 분기의 정적 수학·코드 대조는 일치하고 native는 특수 분기를 사용한다. **수용에 필요한 추가 실행 요구 없음.** |
| **실행 전 binary pin의 시점.** C8 문서는 controls/native의 별도 prelaunch executable-hash 필드가 없었으며 C8 이후 추가되었다고 명시한다. | 과거 실행에서 하지 않은 검사를 소급하여 PASS로 표현할 수 없다. | 현재 C8의 구분을 유지한다. 새 independent primal/consumer 검증은 generator binary 자체를 신뢰할 필요 없이 결과를 검사한다. **이미 적절히 공개됨.** |

**API canonical-label convention.** 일반 수학 fixture의 유한 distinct integer labels를 정렬하여 `0,...,k-1`에 일대일 대응시키고 그 map을 보존하면 된다. 이 변환은 bin equality/inequality, HL domain, `(d,C)`, atom keys·energies·masses 및 event marginals를 보존한다. **현재 API는 이 변환을 자동 수행하지 않는다.** 필요한 caller가 입력 전에 수행해야 하며, direct API의 허용 표현은 nonnegative integer labels다. Identity-pinned native input의 labels 0..3 또는 atom digest를 이 이유로 재명명해서는 안 된다.

## 2. 정리에서 구현으로의 대조

`domain_report`는 positive-mass atom에 한하여 bin별 low/high 최소 에너지를 비교한다. 같은 bin의 허용 HL pair가 존재할 필요충분조건이 두 최소 에너지 합 `<=K`이므로 전수 edge materialization 없이도 predicate 전체를 검사한다. Zero-mass endpoint 무시는 정리의 정량화와 일치하며, equality는 low/allowed 쪽에 포함된다.

`metrics`는 모든 atom의 marginal을 직접 합산한다. Diagonal tuple의 같은 key를 두 번 누적하고, pair energy support와 `s+2d=N`, `HH=0`, low/high leg identities를 exact하게 검사한다. Cross는 unequal birth-bin labels만으로 정한다. `_fill_low_diagonals`는 실제 low singleton residual을 절반 coefficient의 diagonal로 바꾸므로 두-leg 규약이 유지된다.

`assemble`의 분기 `X=0`, `X=M`, `X=D`, `M=0`, 일반 residual repair는 정리의 구성과 일치한다. 다섯 vertex 모두 최종 `metrics`를 통과해야 하며, B/F/G의 HL=M도 별도 확인한다. D/X의 logical inequalities와 primal을 검사하는 것만으로 global upper optimum을 새로 증명하지는 않는다. 이 함수의 **caller-certified D/X** 전제는 docstring에 명시되어 있고, native worker는 hash-pinned PR114/115 입력 및 정확한 cap key로 그 전제를 연결한다. 일반 `solve`는 별도 fresh primal/dual 경로다.

`_repair_high_low`는 positive HL adjacency, forward residual과 positive reverse flow를 사용한다. Multi-source BFS에서 source high와 endpoint low만 전체 HL occupancy가 변한다. Endpoint single이 남아 있으면 certified X와 모순이므로 거절한다. LL-cross edge를 제거하는 경우 epsilon은 path residual·두 endpoint 여유·제거 edge mass·목표 M까지의 잔여 이하이며, 시작 high single을 줄이고 다른 low q의 single을 늘린다. q가 내부 path low여도 그 vertex의 HL 순변화는 0이다. 기존 LL edge는 제거만 하므로 최초 LL 목록을 재사용해도 새 edge를 놓치지 않는다. 각 단계 후 complete marginal, C=X 및 HL의 엄격한 증가를 재검사한다.

`mix_at`은 O/A/B/F/G의 완전한 measure를 섞고 동일 unordered tuple의 coefficient를 더한다. Zero/동일 vertex를 먼저 처리하고 `M=0`, `X=M`, `X=D`, `upper_d=C`의 영분모를 회피한다. 마지막에 target `(d,C)`와 원래 N/L 및 전체 marginal을 다시 검사한다. Float/bool target은 exact scalar로 수용하지 않는다. Acceptance에 부동소수점 tolerance가 들어가는 경로를 발견하지 못했다.

## 3. C++ 결과를 수용하는 exact 경계

Python/C++ 양쪽은 capacity·bound를 `2^126` 미만의 비음수 정수로 제한한다. C++ decimal parser는 곱셈·덧셈 전에 overflow를 검사한다. 각 forward/reverse residual pair의 합이 초기 capacity를 보존하고 total flow가 bound 이하이므로 signed `__int128` 연산 범위가 유지된다. Edge-count 제한은 paired edge index도 보호한다. 반복 DFS의 backtrack은 부모 vertex가 남는 경우에만 `vertices.back()`을 읽는다.

Wrapper는 반환된 모든 edge의 capacity bound, source/sink net flow, 모든 내부 node의 conservation을 Python 정수로 검사한다. 재구성 residual에서 sink 비도달과 cut=value도 확인한다. 따라서 C++가 잘못된 flow를 출력하거나 bound에서 조기 종료해 maximum에 못 미치면 수용하지 않는다. **모든 검사를 통과한 뒤에만** 원래 Python network의 forward/reverse residual을 갱신한다. `finally`가 실패 시에도 class-method patch를 복원한다.

단일 thread·동기 호출, 외부 bounded runner의 process 시간/메모리 제한 및 executable identity는 caller 전제다. `_PATCH_ACTIVE`를 thread lock으로, wrapper 자체를 timeout/hash enforcing runner로 주장하면 안 된다. 현재 docstring은 이 경계를 명시한다. 본 연구에서의 과학적 수용 오류를 발견하지 못했다.

## 4. 실제 근거가 지지하는 범위

| 저장된 근거 | 확인한 실제 범위 |
|---|---|
| controls RESULT/CASES | **117/117 assertions**, 독립 incidence oracle **12 fixtures**, **479 candidate bases**. `bases_checked`에는 singular/infeasible 후보도 포함되므로 479개의 서로 다른 검증 graph나 성공 vertex라는 뜻이 아니다. |
| controls corruption/range branches | Forced residual exchange, 64-bit보다 큰 exact capacity, `2^126` range 거절, 잘못된 zero-flow backend 거절, 실패 후 patch 복원이 기록되어 있다. |
| native SUMMARY | Accepted caps: `0`, exact decimal `1/5`, twice stored binary ghost, `2`, `6`, `20`. 별도 `1,3,10`은 구체적 forbidden pair를 갖는 domain rejection이다. |
| native construction | K2는 X=M으로 기존 B를 사용, K6는 X=D이며 **새 C++ cross max-flow primal**을 실행, K20은 M=0으로 saved G를 사용한다. `native_scalar_optimizer_replays=0`을 “새 solver 실행 0회”로 바꾸어 읽으면 안 된다. |
| native/independent RESULT | **20 witnesses/consumer calls**, 원본 **3201 atoms=3200 active+1 ghost**, **64020 atom-marginal checks**, 78155 event records, 29039 pair-support checks. Distinct vertices가 겹치면 aliases로 결합하며 nontrivial 네 cap에는 interior witness도 있다. |
| independent RESULT | Raw NPZ identity와 primal/consumer mapping의 exact 확인이며, `global_D_X_optimality=REUSED_PRIOR_CERTIFICATE_PROOF_NOT_RECOMPUTED`, solver calls 0, production imports 0으로 범위를 명시한다. |

Independent result의 1020 scalar·2020 vector-component·300 physical-gate checks와 원 consumer의 same-state binding을 함께 읽었다. 모든 native source를 선택하여 p=0인 반환이며, W와 nb를 각 한 번 적용한다. 실제 K/exclusive kernel, outside partner, donor work, EOS/T, 절대 부피, full physical native25가 해결되었다는 근거는 없고 `physical_activation=false`를 유지한다. Partial-mask 일반화를 새 native 검증 성과로 주장하지 않는다.

C8의 local charged ledger는 **23.448655/40 CPU-s**이며 실패한 build_v1 watchdog 시도와 controller diagnostics가 포함되어 있다. build_v2 회복을 최초 성공처럼 덮어쓰지 않았고, remote R7 CPU와 metadata/provider 시간을 local science 합계의 0으로 흡수하지 않는다. Plot은 saved exact SUMMARY를 읽고 display 좌표에서만 float를 사용한다. K6 flow의 독립 timing 또는 universal speedup은 측정하지 않았다.

## 5. 수용 결정

저장된 scoped native 결과와 constructive implementation을 수용한다. 직접 API의 nonnegative-label 표현 규약과 긴 residual-path 미실행 범위를 분명히 공개하면 현재 연구의 추가 실행을 요구할 구체적 결함은 없다. General rational theorem의 증명, finite controls, native witness 검증은 서로 다른 근거이며 어느 하나를 전체 입력의 실행 검증으로 확대하지 않는다. 이 C9 범위의 검토를 종료한다.
