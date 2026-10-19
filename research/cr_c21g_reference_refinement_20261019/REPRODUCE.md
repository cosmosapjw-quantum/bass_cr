# C21G 재현·실행 안내

## 1. 고정 입력과 작업 위치

저장소는 `cosmosapjw-quantum/bass_cr`, 부모 평가는 PR83 `d780c2c53f869c914add1d5492312d0bc507f976`이다. 새 단위 경로는 `research/cr_c21g_reference_refinement_20261019/`다. 게시 이전의 임시 상태를 실행 commit으로 사용하지 말고, 최종 `PUBLICATION_RECEIPT.json`의 실제 실행 commit과 `EXECUTION_MANIFEST.json`을 읽는다. 검증된 실행 manifest SHA256은 `7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`다.

아래 변수는 확인한 checkout 안에서 정한다. NCP 절대 경로를 가정하지 않는다.

```bash
c21g_repo=$(git rev-parse --show-toplevel)
c21g_unit="$c21g_repo/research/cr_c21g_reference_refinement_20261019"
c21g_source="$c21g_repo/research/cr_c21e_event_native_20261018"
c21g_baseline="$c21g_source/evidence/C21F_NATIVE_NCP_20261018T1358Z"
```

실행기는 기본적으로 위의 원게시 evidence 경로를 읽는다. 별도 복원본은 `--baseline-dir`로 명시할 수 있지만 manifest의 바이트·SHA·fixture digest를 통과해야 한다. 새 자료 배포에 과거 23 MB text나 native archive 전체를 중복해서 넣을 필요는 없다. 기존 raw는 PR82의 GitHub 경로를 참조하고, 새 자료만 create-only 보존한다.

## 2. 실행 없는 plan

`--out`은 아직 존재하지 않는 경로여야 한다. 이 명령은 native process를 시작하지 않는다.

```bash
python3 "$c21g_unit/run_campaign.py" plan \
  --source-dir "$c21g_source" \
  --baseline-dir "$c21g_baseline" \
  --out "$c21g_new_plan_dir"
```

성공하면 `INPUT_IDENTITY.json`과 `PLAN.json`이 생긴다. Plan에는 새 reference 8개와 조건부 history 4개가 있고 기존 L0/8/16/32/64 job은 없다. Manifest mismatch가 있으면 실제 source·fixture 의존성을 해결한 뒤 새 출력 경로에서 다시 plan한다.

## 3. 경량 검증 재현

유지된 코드의 검증 근거는 재사용한다. 이번 sandbox 결과는 reference patch 9 + diagnostics 9 + runner 14 + analysis binding 3개 PASS, analytic 9 cases PASS, smoke 3 jobs PASS다. 아래 명령은 이 단위를 변경했거나 관련 회귀를 확인할 때의 경량 재현 경로다. 원래 56개 suite와 기존 native 행렬은 이 경로에 포함하지 않는다.

```bash
python3 -B -m unittest discover -s "$c21g_unit/tests" -v
C21F_SOURCE_DIR="$c21g_source/src" python3 -B -m unittest discover \
  -s "$c21g_unit/evidence/tests/reference_patch" \
  -p test_reference_patch.py -v
python3 -B "$c21g_unit/run_campaign.py" smoke \
  --source-dir "$c21g_source" \
  --baseline-dir "$c21g_baseline" \
  --out "$c21g_new_smoke_dir"
python3 -B "$c21g_unit/verify_analytic_reference.py" \
  --out "$c21g_new_analytic_dir"
```

`unit/tests`의 세 파일은 `test_campaign.py`, `test_diagnostics.py`, `test_analysis_binding.py`다. Reference patch의 별도 9개 검사는 `evidence/tests/reference_patch/`에 있으며 같은 폴더의 `ORIGINAL_SCALAR_SMOKE.json`을 읽는다. 이 검사의 기본 source 경로는 개발 당시 staging 위치이므로, 다른 checkout에서는 위처럼 **`C21F_SOURCE_DIR`을 실제 `src` 경로로 설정**한다.

`smoke`는 작은 Y=0 제조 fixture의 reference L1·FULLMID 4·hybrid 4 세 job이다. 실제 sandbox wall 4.494274969001708초에 모두 완료했다. Native Grackle 검증으로 표기하지 않는다. `verify_analytic_reference.py`의 아홉 제조 문제에는 source birth·H/He feedback·FLRW geometry가 없으며 기존 실행 wall은 1.9097576049971394초였다. 재현 실행을 새로 한다면 그 실행 여부와 wall time을 새로운 영수증으로 기록한다.

## 4. Native 실행 전 실제 확인

현재 사용 가능한 CPU·RAM·process·기존 campaign와 native binary 위치를 실제로 확인한다. 현재 원격 도구 quota가 0이었던 과거 receipt는 앞으로의 자원 상태를 대신하지 않는다. CPU affinity membership 자체도 독점 자원 할당의 증거가 아니다.

한 CPU를 이 작업에 할당하고 **CPU 55를 제외**한다. dirty 파일·watcher·다른 checkpoint가 있는 checkout은 보존하고 필요한 경우 새 worktree/checkout에서 고정 실행 commit을 사용한다. 임의 reset·clean·stash·rebase·기존 campaign 종료·원게시 패치 재적용은 하지 않는다.

기존 검증 native binary의 SHA256이 아래와 같으면 재사용한다.

```text
1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40
```

해당 binary를 실제로 찾지 못했거나 실행 불가능한 경우에만 기존 `build_native.sh`로 pinned owner를 빌드하고, 실제 빌드 폴더를 `--build-dir`로 전달한다. Runner는 `owner_commit.txt`, `build_exit.txt`, `input_sha256.txt`, owner source archive와 wrapper/binary SHA를 검증한다. CPU·binary 변수를 예상값으로 채우지 않는다.

필요한 최소 시작 호환 점검을 통과한 후에만 아래를 실행한다. 전체 native build/test를 관성적으로 반복하지 않는다.

```bash
python3 "$c21g_unit/run_campaign.py" run \
  --source-dir "$c21g_source" \
  --baseline-dir "$c21g_baseline" \
  --native "$c21g_verified_native" \
  --cpu "$c21g_allocated_cpu" \
  --out "$c21g_new_native_dir"
```

새로 빌드한 binary라면 `--build-dir "$c21g_verified_build_dir"`을 추가한다. Reference만 실행할 때는 `--references-only`를 추가한다. 기본 경로는 새 reference를 먼저 계산하고, 전체 reference 실행 완료와 native_source 민감도 조건이 충족된 경우에만 네 history를 진행한다.

## 5. 중단과 완료 job 재사용

각 시도는 새 출력 폴더를 사용한다. 실패한 폴더를 지우거나 그 안에서 기존 job을 덮어쓰지 않는다. Source/fixture/runtime/binary/tier signature와 payload hash를 검증한 **완료 C21G job**만 다음 시도에서 재사용한다.

```bash
python3 "$c21g_unit/run_campaign.py" run \
  --source-dir "$c21g_source" \
  --baseline-dir "$c21g_baseline" \
  --native "$c21g_verified_native" \
  --cpu "$c21g_allocated_cpu" \
  --reuse "$c21g_previous_attempt_dir" \
  --out "$c21g_new_attempt_dir"
```

기존 C21F 결과는 baseline 입력이며 `--reuse` 대상 C21G job으로 위장하지 않는다. 입력·환경·예산 오류를 물리 실패로 합치지 않고 `FAILURE.json`, stdout/stderr와 partial payload를 보존한다. 고정 budget 실패 후 source·tolerance·예산을 몰래 바꾸어 같은 job으로 통과시키지 않는다.

## 6. 결과 분석과 반환

Runner의 분석 결과를 재사용한다. 별도 복원본에 대한 standalone 분석은 실제 receipt와 payload의 연결 및 SHA를 확인한 뒤 실행한다.

```bash
python3 "$c21g_unit/analyze_campaign.py" \
  --baseline-dir "$c21g_baseline" \
  --run-dir "$c21g_completed_or_partial_run_dir" \
  --out "$c21g_new_analysis_dir"
```

실행기는 `REFERENCE_ASSESSMENT.json`, `REFINEMENT_ASSESSMENT.json`, `RETURN_TO_CHATGPT.json`을 기록한다. 완료 exit, physical ledger, reference 민감도, signed component order, reference-free order, 최대 norm의 active component, underflow/log 기록을 분리해서 읽는다. `L3M` cap을 바꿔도 actual grid가 같으면 `MESH_CAP_INACTIVE`다. Empirical radius나 reference-choice min/max를 인증된 오차 상계나 신뢰구간으로 해석하지 않는다.

새 실행의 raw·source/fixture/runtime identity·모든 process receipt·실패 자료를 create-only로 게시하고 Drive+Dropbox에 이중백업한다. 실제 provider ID·size·checksum/readback 수준을 영수증에 적은 뒤 DAG를 갱신한다. 기존 raw archive와 과거 단계 기록을 대체하지 않는다.
