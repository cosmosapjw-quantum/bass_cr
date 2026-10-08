# R4X 연속 기저 연구 재현 안내

이번 단계는 G02의 shared-endpoint 기저 표현, 기저 진단, strict FP64 Fortran/OpenMP radial 평가기, 제한된 정적 S/H/D 비교를 다룬다. 원래 입력기저와 기존 production provider는 변경하지 않는다. G02 전체 미분 게이트·전파·capture를 통과했다고 해석하지 않는다. 기저 표현의 정확한 정의와 API는 `BASIS_API_KO.md`, 정적 adapter와 실행 예산은 `OPERATOR_API.md`, 실제 판정은 각 결과 JSON과 최종 보고서를 따른다.

## 패키지 구성과 복구

바깥 패키지의 `base/BASS_CR_R4W_G02_RESEARCH_PACKAGE_20261001_v1.zip`은 변경하지 않은 R4W 패키지다. 크기는 26,227,037 bytes, SHA256은 `eb3332f61be633f38e22bf6294f1e5537e6be25d960e7f708fd9794af46d69f5`다. 이 안의 `base/BASS_CR_R4V_RESEARCH_PACKAGE_20261001_v1.zip`은 SHA256 `dd7a5df422cc6b75a928d6583546ef5578de1e0fd5e7d669e0ae06253a1d69f3`인 이전 패키지다. 입력기저·원래 native 빌드·72개 operator cache·R4U 이전 근거가 중첩된 base에 들어 있다. 각 패키지의 manifest를 따라 실제 파일 위치를 복원하며, ZIP의 폴더명을 실행 경로라고 가정하지 않는다.

바깥 `source/`는 새 연구 모듈과 AGENTS.md 추가 안내, `runs_r4x/`는 실제 후보·빌드·진단·정적 실행·독립 검토, `reports/`는 보고서와 DBv10이다. `MANIFEST.json`의 파일별 hash를 복구 기준으로 사용한다. 초기 시도와 수정 근거는 이름에 INITIAL이 붙은 로그 및 해당 검토 기록에 남아 있다. 완료된 결과를 읽는 데 재실행은 필요하지 않다.

경로·컴파일러·native binary·source·resource가 바뀐 환경은 새 실행 문맥이다. 이전 절대경로를 바꾼 것만으로 과거 identity나 승인이 유지되지 않는다. native 라이브러리는 복구 절차로 파일과 의존성을 검증하거나 현재 환경에서 별도 빌드한다. 새 manifest를 만들고 현재 source/input/native/resource를 다시 묶는다. 저장된 후보와 빌드는 source SHA까지 묶으므로 코드 변경 후 그대로 재사용할 수 없다.

## 후보와 비물리 진단의 재현

아래 명령은 워크스페이스 최상위에서 실행한다. 이미 완료된 `runs_r4x/candidate_v1`, `native_v1`, `static_v1`을 덮어쓰지 않는다. `replay_r4x_01`은 예시이며, 이미 존재하면 별도의 새 이름을 선택한다. 원본 입력 두 파일은 아래 byte SHA와 일치해야 한다.

```bash
R4X_MOD=recovered_r4u/source/research/gap_closure_20261001/g02_continuous_basis_20261002
R4X_REPLAY=replay_r4x_01
python "$R4X_MOD/build_candidate.py" \
  --original-npz recovered_r4u/runtime_inputs/BASIS.npz \
  --original-metadata recovered_r4u/runtime_inputs/BASIS.json \
  --expected-npz-sha256 889001a751cd3cae93ad217336587f5fc58db11c0a496843ecc7e7bbd93f83ec \
  --expected-metadata-sha256 3cf2359dd9802e84f9ec4dc45f3585e0aa9712de38a3fb0a077300d257150131 \
  --out "$R4X_REPLAY/candidate_v1" \
  --native-out "$R4X_REPLAY/native_v1" --compiler gfortran
python "$R4X_MOD/basis_diagnostics.py" \
  --candidate "$R4X_REPLAY/candidate_v1" \
  --inputs recovered_r4u/runtime_inputs \
  --output "$R4X_REPLAY/BASIS_DIAGNOSTICS.json"
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_DYNAMIC=FALSE \
  OMP_PROC_BIND=FALSE OMP_MAX_ACTIVE_LEVELS=1 \
  python "$R4X_MOD/validate_evaluator.py" \
  --candidate "$R4X_REPLAY/candidate_v1" \
  --native-manifest "$R4X_REPLAY/native_v1/NATIVE_BUILD.json" \
  --out "$R4X_REPLAY/EVALUATOR_VALIDATION.json"
```

실제 R4X에서는 각각 `runs_r4x/candidate_v1`, `runs_r4x/native_v1`, `runs_r4x/BASIS_DIAGNOSTICS.json`, `runs_r4x/EVALUATOR_VALIDATION.json`을 사용했다. 당시 compiler entrypoint와 실제 frontend, 명령, 버전 및 SHA는 `native_v1/NATIVE_BUILD.json`에 기록되어 있다. 위 `gfortran`은 현재 환경의 검증된 compiler로 지정해야 한다. 동일한 컴파일러 이름이 동일한 binary를 뜻하지 않는다.

추가된 단위 검사는 기저 10개와 adapter 9개, 총 19개다. 변경된 모듈을 다시 검증해야 할 때만 아래 두 파일을 대상으로 실행한다. 과거 R4U/R4V/R4W 전체 검사 반복은 필요하지 않다. adapter의 synthetic worker·native 검사는 실제 물리 호출이나 실행 예산 소비가 아니다.

```bash
python -m unittest discover -s "$R4X_MOD" -p 'test_basis_representation.py' -v
python -m unittest discover -s "$R4X_MOD" -p 'test_operator_adapter.py' -v
```

평가기 실측은 100만 반지름, 한 radial mode의 제한된 benchmark다. 이번 호스트는 8 CPU quota/8 GiB였으며 Python 대비 end-to-end 최고 속도비는 4 threads에서 약 2.479배였다. 1/2/4/8 threads 모두 비교 대상 출력은 bitwise 일치했다. 이 수치는 전체 S/H/D 또는 trajectory 속도비, MPI 실행, NCP64 scaling이 아니다. prelocated 측정에도 ctypes·검증·할당 비용이 포함된다. 조건이 다른 환경의 속도는 다시 측정한다.

## 정적 연산자 실행의 재현

실제 정적 실행은 `runs_r4x/static_v1/MANIFEST.json`으로 고정했다. 해당 manifest SHA256은 `fdf0e87470c809de2fa65795e8aaa193db338052d1f6e6aaa839a894b04ebe2c`, 내부 manifest ID는 `df25e7a7da88628227665ab4209b6f8f7a398d7af20aa081d332eb6d2152db34`다. 이 두 값은 당시 실행을 식별하며 새 출력 경로의 재현에 재사용하지 않는다.

다음 `prepare`는 native를 로드하거나 물리 연산자를 실행하지 않는다. 복구·검증된 원래 strict C++ moment build와 별도 후보를 입력으로 받아 새 manifest를 만든다. native build가 다른 위치에 있으면 검증된 현재 경로를 지정한다.

```bash
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 \
  OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 \
  python "$R4X_MOD/run_static_comparison.py" prepare \
  --inputs recovered_r4u/runtime_inputs \
  --candidate "$R4X_REPLAY/candidate_v1" \
  --build recovered_r4u/native_build_portable \
  --out "$R4X_REPLAY/static_v1" --workers 4
```

새 `MANIFEST.json`의 source/input/native pins, 호출 계획, CPU/RAM admission과 예산을 확인한 뒤 **해당 prepare가 출력한 SHA256**을 아래 자리표시자에 넣어 실행한다. 명령 자체를 재현 근거 없이 자동 재실행하지 않는다.

```bash
env OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 \
  OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 \
  python "$R4X_MOD/run_static_comparison.py" run \
  --out "$R4X_REPLAY/static_v1" \
  --manifest-sha256 NEW_SHA256_FROM_PREPARE
```

계획은 원본/후보 × z=−32/0 × cross order=32/40의 정확히 8회 raw cross 호출이며, b=2와 same-center order=20을 고정한다. 최대 4개 single-thread worker와 별도 coordinator CPU를 사용한다. 후보의 이 정적 실행 radial 평가는 Python FP64다. 별도 Fortran benchmark를 이 정적 실행의 사용 backend로 해석하지 않는다.

각 attempt는 시작 전에 durable reservation을 소비한다. 시작한 출력 디렉터리는 재실행할 수 없으며, timeout·실패·중단 후 소모한 reservation을 재시도하지 않는다. 내부 `worker` 명령을 직접 실행하지 않는다. 완료된 `SUMMARY.json`과 각 raw/full 산출물을 우선 읽는다. 추가 연구가 필요하면 실패 원인을 검토하고 별도 계약·새 출력 디렉터리·새 manifest·새 예산으로 진행한다. 과거 호출 cap을 자동으로 갱신하거나 기존 실패를 지우지 않는다.

DBv10의 최신 상태는 `current_research_gap_status`에서 읽고 DBv9의 이전 effective view는 `current_research_gap_status_v9`에서 읽는다. 기존 42개 표와 3,290개 행은 유지한다. 추가된 `basis_research_evidence`와 `basis_research_status`는 이번 근거와 G02 국소 진척만 기록한다. 정적 진단 성공도 cross-block FD·전체 G02·production을 닫지 않는다. production HOLD, capture=false, all_bound OPEN, b-grid NO_GO를 유지한다.

실제 8개 정적 계산에 사용한 coordinator source는 `runs_r4x/source_at_run/run_static_comparison.py`에 보존했다. 완료 후 프로세스 시작 실패 시 예약 횟수의 보고 오류를 수정했고 최종 adapter 테스트9개를 실행했다. `POST_RUN_REPAIR_RECEIPT.json`이 전후 identity를 구별한다. 기존 manifest는 수정 후 runner와 일치하지 않으므로 기존 완료 작업을 재개하지 말고 재실행이 필요하면 새로운 출력과 manifest를 생성한다.
