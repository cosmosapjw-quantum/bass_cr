# TP2A: reference와 candidate를 모두 검증하는 유한 적분 정책

기준 commit: `3499e9f73527dfb5e76299205b9e864e89ebf248`. 새 branch에서 이 sidecar의 판정 정책만 수정한다. 기존 branch, 실패 run, FEM basis, full-operator, native C++ 및 cross kernel 소스는 보존한다.

## 변경 근거

첨부된 사용자 결과에서 z=-4는 qualified reference48과 후보가 통과했다. z=-2의 reference는 56/64 비교를 통과했지만 후보 phase24의 raw 오차가 1.20945e-8로 1e-9 기준을 넘었다. connection 검사만으로는 부족하다.

별도 동일-basis 연구에서 같은 실패를 재현했다. phase32/budget24는 plain64와 최대 5.13e-15, phase24/budget12는 최대 4.79e-15 상대차로 일치했다. 같은 종방향 위상을 남기고 횡방향 성분을 제거한 대조에서도 기존 후보가 수렴한다. 기존 24rad 규칙이 횡방향 Bessel 의존성을 보증하지 않는다는 원인을 지지한다. `MATH_RESEARCH_KO.md`, `Z2_RESEARCH_FINDINGS.json` 참조.

## 새 고정 계약

- Geometry: -4,-2,0,2,4,6,8,10,12 a0. 이미 통과한 -4도 이전 원시 task를 가져오면 재적분하지 않고 판정만 재계산한다.
- Reference orders: 32,40,48,56,64. 연속 두 차수가 own connection/operator 및 raw cross 수렴을 통과한 높은 쪽만 기준으로 쓴다.
- Candidate orders: 24,32,40,48,56,64. 같은 phase budget24를 유지하며, qualified reference에 대한 raw 차이와 own connection/operator 검사를 모두 통과한 최초 후보를 쓴다.
- Screens: connection <=1e-6, raw cross relative <=1e-9, S/H Hermiticity <=1e-11, metric ratio >=1e-8. epsilon_z=1e-4a0, same-center order20, 18 channels는 유지한다.

최대 차수나 허용오차를 실행 중 변경하는 기능은 없다. 유한 ladder의 실패는 `REFERENCE_CONVERGENCE_UNRESOLVED`와 `CANDIDATE_CONVERGENCE_UNRESOLVED`로 분리한다. 통과하지 못한 낮은 candidate 기록도 `candidate_attempts`에 남는다. 처음 실패한 geometry 다음은 제출하지 않는다.

## 권장 실행: 이전 task의 명시적 재사용

기존 native build와 직전 canonical return을 사용한다. `--import-from`은 단순 `--resume-from`이 아니다. `IMPORT_GRANT.json`에 고정된 이전 report/ZIP SHA, commit, contract/context/source pins, basis, native binary, 각 task identity와 행렬 shape/hash/시간/full-cross 일치를 검사한 뒤 원시 NPZ bytes만 새 context로 연결한다. 이전 FAIL을 PASS로 바꾸지 않는다. 원본 파일은 읽기만 한다.

```bash
BASE=research/foundation_rebuild/tp2a_reference_qualified_20260926
BUILD_TP2A=runs/tp2a_native_build_20260926T043856Z
OLD_REFQ=runs/tp2a_reference_qualified_20260926T090750Z
OUT_REFQ="runs/tp2a_resolution_qualified_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" --workers 8 \
  --import-from "$OLD_REFQ" --out "$OUT_REFQ" \
  --expected-commit "$EXPECTED_SHA"
```

직전 반환 archive는 `OLD_REFQ` 옆의 `${OLD_REFQ}_RETURN.zip`이어야 한다. 현재 허용된 source report SHA는 `f4a758010ac773ee12d8b2a68e4b6fbe209c82301abe7f01ccdb75b2d78e127e`, archive SHA는 `f9eddd0fa19465d25806f1a75c1a4b44309d4627e8a5e46a7dbf9b8cc20bca9a`다. 누락 또는 불일치를 검사 우회로 해결하지 않는다.

예상 재사용은 이전 -4의 12 task와 -2의 18 task, 합계30개다. 실제 count가 다르면 IMPORT_RECEIPT와 해당 source를 확인한다. -4의 통과와 -2의 reference64 및 실패 후보24는 재적분 없이 사용하고, -2에서는 candidate32 세 시점부터 새 계산이 필요하다. 이전 raw source를 사용할 수 없는 경우 import를 생략한 fresh run은 가능하지만, 중복 계산을 피하려면 원시 source 복원부터 하는 것이 좋다.

## 진행상황, 중단 및 재개

실제 output 절대경로를 첫 줄에 출력하고 PROGRESS.jsonl에 task·reference·candidate 판정과 heartbeat를 남긴다. 다른 터미널에서 OUT 변수를 date로 새로 만들지 말고 첫 줄의 정확한 폴더를 사용한다.

같은 새 V2 실행이 중단되었을 때만 다음처럼 새 output으로 재개한다.

```bash
NEW_OUT="runs/tp2a_resolution_resume_$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$BASE/run_full_geometry_qualification.py" \
  --native-build "$BUILD_TP2A" --workers 8 \
  --resume-from "$OUT_REFQ" --out "$NEW_OUT" --expected-commit "$EXPECTED_SHA"
```

`--import-from`과 `--resume-from`은 함께 사용하지 않는다. 같은-context resume에는 완료된 task의 hash를 확인하며 불완전 NPZ는 재사용하지 않는다. 오류 상태에서도 만들어진 task는 보존한다.

## 반환

성공: `TP2A_RESOLUTION_QUALIFIED_FULL_GEOMETRY_PASS`.
Geometry별 `qualified_reference_order`, `qualified_candidate_order`, `candidate_attempts`, `reference_qualification`, `candidate_vs_reference`를 본다. `imported_tasks`, `restored_tasks`, `new_operator_evaluations`로 실제 재사용과 새 계산을 구분한다.

이 패키지의 코드·작은 실제 FEM spawn·checkpoint/import·저장된 18-channel z=-2 replay는 검증했다. 새 정책의 전체 9-geometry confirmatory는 아직 이 결과에 포함하지 않는다. 기존 18개는 변경된 판정/runtime에 관련된 회귀시험이며 역사적 TP1·GPU suite를 재실행하지 않는다. Runner가 필요한 sidecar 시험을 수행하므로 별도 사전 pytest는 불필요하다.

항상 capture_execution_allowed=false, production_admission=HOLD, all_bound=OPEN, b_grid=NO_GO, original_capture_gap_resolved=false다. 이산 geometry PASS는 연속 궤적 오차상한이나 basis completeness의 증명이 아니다.
