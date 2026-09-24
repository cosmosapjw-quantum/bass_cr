# Codex handoff — R3M26 이후 모델 기반 수렴

다음 내용을 로컬 Codex에 전달한다. 현재 문서가 포함된 원격 R3M26 최종 commit을 exact authority로 기록하고 시작한다. 기존 R3M25 authority는 `90d6cbad25e4bc49e9563f8721fdc408761b31c7`이며 R3M26의 receipt-only commit은 수치 소스를 바꾸지 않는다.

## 목표와 권한

GPT6용 physmath-research-loop의 theory→coding 흐름을 적용하되 R3M26에서 완료한 이론·외부 조사·국소 reference를 반복하지 말라. 현재 선택한 물리 모형을 수치적으로 정확히 구현하는 것이 production 기준이다. 특정 논문/그림/private raw 일치는 prerequisite가 아니다. numerical total1%, 시간.10%, 공간.30% 및 나머지 배분은 유지한다. 모델 discrepancy는 별도다.

현재 production HOLD, all-bound OPEN, b-grid NO_GO다. 정확히 하나의 다음 node는 `N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT`다. 이 handoff의 실행 범위는 B3용 외부 실행 계약·조정기 작성/검증, 정확한 B3 preparation 한 번, witnessed full collision B3 **한 건**, 사전 등록 분석과 결과 반환이다. B4/finer h/representation/b-grid/physical-rate/main merge/force push는 자동 실행하지 않는다. 이미 승인된 준비·가역 수정·검증에는 다시 확인을 요구하지 않는다. 선택적 로컬 모델이 없으면 이를 장애로 만들지 말고 Codex-only로 진행한다.

## 고정 입력과 검토 순서

1. `docs/r3m26/SCIENTIFIC_CONTRACT.md`, `MODEL_CONTRACT.json`, `MODEL_FOUNDATION_KO.md`, `NUMERICAL_STRATEGY_KO.md`, `PERFORMANCE_AND_CODE_REVIEW_KO.md`, `docs/roadmap/{DAG,ERROR_BUDGET}.json`을 읽는다.
2. user branch/worktree/untracked를 보존하고 새 전용 branch에서 시작한다. main을 바꾸지 않는다. R3M26 전체 diff와 final receipt, 시험 로그를 확인한다.
3. frozen `cr_repro` digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`다. canonical B initial.npy SHA는 `ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa`다.
4. frozen forecast는 `results/R3M26/temporal/B3_FROZEN_FORECAST.json`, 파일 SHA `5eb9920d10ed467df7bc512cbbf983ee1ce95d2df94a15d21aa8e6940ebf743e`, payload SHA `be693bbae3a90420b25f441431ee0f63b2dd8131fd1c2017c81c847e83a4c64e`다. 그대로 사용한다. B3 관측 뒤 예측/임계값/모형을 재등록하거나 바꾸지 않는다. 로컬 BLAS의 마지막 bit 차이 때문에 forecast를 다시 만들 필요도 없다.
5. B2 작은 raw result는 `results/R3M20_N1/intake/collision/result.json`, SHA `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`다. local raw arrays는 사용자 data root에서 기존 receipt로 확인한다. cloud archive raw readback/restore가 완료됐다고 가정하지 않는다.

## B3 실행 전 계약을 구체화

B3 config는 frozen B1/B2 family에서 **requested real dt만 .00625**로 바꾼다. 100 keV/u, b=2, h=.20, grid350×300×600, CAP/source/initial/projection/imaginary-time 설정을 유지한다. nstep7172, actual dt `.00624946176119497`, 공통 horizon `44.821139751290325` au다. chunk128씩57회, 마지막4 steps다.

기존 `scripts/r3m18_b2_execute.py` 및 `r3m17_preflight.py`는 B2 전용으로3586/29와 정확한 B2 argv를 검사한다. 단순히 B3 config를 넘겨 실행하지 말라. 외부 coordinator/preflight를 새 R3M27 파일로 작성하여 expected config·canonical executable argv·source·science interpreter·resource budget·checkpoint frontier를 B3에 맞게 한 곳에서 생성/검증한다. 기존 B2 검증이나 frozen numerical source를 완화하지 않는다. `r3m17_checkpoint_guard.py`의 검증된 immutable generation 방식을 재사용한다. 정상 resume, 이미 완료된 writer의 publish-only, 예상 frontier 이탈, argv/config 변조를 작은 fixture로 검증한다.

현재 R3M14 witness는 preparation receipt의 **전체 canonical config**와 collision config가 같아야 한다. 따라서 B2 receipt에서 dt를 바꾼 가짜 preparation을 만들거나 receipt hash 재사용으로 통과시키지 않는다. 기존 `scripts/r3m13_initial_state_pair.py prepare`로 exact B3 config preparation을 생성하고 canonical initial.npy SHA가 같은지 확인한다. inherited collision의 내부 preparation은 기존 witness 경로대로 실행되어 같은 initial array를 검증해야 한다. 이는 새 preparation 또는 propagator 설계를 연구하는 작업이 아니다. 기존 helper가 수행하는 내부 준비 작업량도 runtime에 기록한다.

실행 전에 별도 CONTRACT.json과 hash manifest에 config, scripts, forecast, environment, output root,57-generation disk budget, CPU/RAM/GPU resource ceilings, checkpoint retention, timeout·retry 정책을 기록한다. SHA가 포함된 구체 계약을 만든 뒤 실행한다. source/config/initial/runtime mismatch나 resource preflight 실패면 collision을 시작하지 않고 정확한 blocker를 반환한다. 내부 검증을 단지 boolean만 바꾸어 통과시키지 않는다.

## CPU·RAM·GPU 운용

실제 기준은 Ryzen5900X12c/24t, 약96GiB RAM, RTX309024GB이며 실행 시 inventory를 다시 기록한다. science interpreter는 `/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python`이고 기존 Python3.12.3/NumPy2.5.3/SciPy1.18.1/CuPy14.2/CUDA12090 환경을 확인한다. 패키지를 조용히 업그레이드하지 않는다.

한 GPU propagation만 실행한다. 최소 free GPU2GiB와 실제 사용량/peak를 관측하고, R3M25에서 검증한 필요 배열만 GPU에 두는 원칙을 적용한다. full CF4 replacement/float32/다중 동시 GPU collision/63M CPU fallback을 하지 않는다. CPU는 hash·작은 분석·I/O를 제한된 worker로 수행하며 BLAS/OpenMP 중첩을 막는다. CPU FFT4-worker 후보는 검증된 작은 reference workload에 한정한다. RAM은 필요한 host buffers와 filesystem cache에 사용하되 미완료 checkpoint를 다음 chunk가 덮어쓰지 못하도록 publish/fsync/hash 완료 순서를 보존한다. 비동기 저장은 새로 검증하지 않았다면 도입하지 않는다.

57개 state 배열만 약57.46GB(decimal)다. 실제 preparation/checkpoint duplicate/temp/기존 dataset 여유를 더한 disk 예산을 계약에 계산한다. checkpoint 배열은 로컬에 보존한다. 주요 비용을 preparation, GPU propagation, Gram analysis, D2H, checkpoint/hash/I/O로 나누어 기록한다. microbenchmark가 전체 collision 속도라고 주장하지 않는다.

## 실행·판정

준비와 local tests/preflight가 통과하면 B3 한 건을 순차 실행한다. 각 chunk 다음에는 immutable generation을 검증해 게시한 후 다음 chunk로 진행한다. 최초 실패 원문을 보존하고 자동 재시도하지 않는다. crash 뒤 재개가 필요하면 기존 completed frontier를 검증하고 같은 step을 중복 실행하지 않는다. 과학적 수렴 실패는 runtime failure와 구분한다.

완료 뒤 실제 result와 witness에 다음 분석기를 실행한다. 아래 `$B3_ROOT`는 계약에 고정한 새 출력 경로다.

```bash
"$SCIENCE_PYTHON" scripts/r3m26_temporal.py evaluate \
  --result "$B3_ROOT/collision/result.json" \
  --witness "$B3_ROOT/collision/r3m14_initial_binding.json" \
  --forecast results/R3M26/temporal/B3_FROZEN_FORECAST.json \
  --out "$B3_ROOT/B3_TEMPORAL_EVALUATION.json"
```

raw result·v2 witness 외에 coordinator 계약/config/환경/final checkpoint/준비 receipt 연결도 감사한다. 분석기만으로 endpoint 배열을 독립 재계산했다고 주장하지 않는다.

사전 기준은 세 cumulative channels 모두에서 fine increments 동일 부호·수축, `|B3−B2|/|B3|≤.001`, `U_time/|B3|≤.001`이다. `U_time=2 max(E_model,D_hold)`: 네 P∞ 후보의 B3 잔여와 세 frozen forecast의 held-out residual을 사용한다. actual dt를 사용하며 roundoff 미해결/0 denominator를 PASS로 바꾸지 않는다. p clean range 및 LOO는 diagnostic이다. safety factor2는 설계값이고 confidence probability/엄밀상한이 아니다. 관측 B3를 central로 보존한다.

- PASS: `TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS`, certified=false. 같은 local-reference 작업을 다시 열지 말고 **spatial+h_dt budget**을 다음 canonical node로 구체화한다. production/all-bound/b-grid는 자동 GO가 아니다.
- 일관된 예측 속 근소한 초과: 실제 값과 budget gap을 제시하고 후속 계약에서 최대 한 refinement의 예상비용/판별력을 평가한다. 여기서 B4를 실행하지 않는다.
- 부호·예측·모형 envelope 불일치: blind refinement 대신 same-H algorithm/representation/time-dependence 원인을 겨냥한 한 분기로 좁힌다. 별개의 local certification을 무한히 추가하지 않는다.

`r3m26_budget.py` ledger는 각 관측량의 preparation/spatial/time/boundary, 이후 high-n/b 적분을 해당 범위에 맞게 받는다. 실측 pair나 local PASS를 `VALIDATED_ESTIMATE`로 자동 표기하지 않는다. estimate validation flags와 references는 실제 full-component evidence를 가리켜야 한다. 다른 b/energy/units/all-bound 관측량과 섞지 않는다. h_dt를 한 번 포함하고 누락 오차는 null/OPEN으로 남긴다.

## 반환·종료

한국어 보고서, 실제 scalar 결과와 B0–B3 표, four-point/LOO/held-out 분석, typed ledger, runtime/failure/checkpoint 기록, 독립 결과검토, exactHEAD/remoteR1, 작은 final-state/result+audit 이중 backup receipt를 반환한다. 기존 큰 backup을 반복 업로드하지 않는다. raw readback/restore를 하지 않았다면 각각 NOT_RUN/RESTORE_NOT_TESTED다. main merge/force push는 하지 않는다.

DAG와 계획은 실제 완료 상태로 함께 갱신하고 다음 canonical node를 하나만 남긴다. 시간차원이 닫히면 공간→준비/경계→all-bound→b적분→50/225확장 순으로 종합해 종료한다. 모든 대안 알고리즘을 구현하거나 추가 논문을 찾아야만 종료되는 조건을 새로 만들지 않는다.
