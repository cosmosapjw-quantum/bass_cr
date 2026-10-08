# R4O temporal closeout / R4P0 tail & basis preparation

종료 상태: `R4P0_TAIL_AND_BASIS_PREFLIGHT_READY__NATIVE_AUTHORIZATION_PENDING`.

이 디렉터리는 preparation-only다. 새 operator, transport, basis 또는 reference 계산을 시작하는 launcher가 없다. 미래 실행 template에는 실제 authorization ID/CPU/RAM/deadline/wall/grace/cost가 없으며 USER_APPROVAL_REQUIRED다. 새 nonce를 소비하지 않는다.

## 입력과 결과

CONTRACT.json은 완료 A3 및 이전 N768 archive와 추출한 13개 입력 파일의 SHA/size를 고정한다. NPZ는 Git에 중복 저장하지 않으며 portable package에 원본 bytes로 넣는다. Package의 inputs/만으로 tests 및 CLI가 실행된다. 별도 PYTHONPATH나 원 worktree의 science 모듈이 필요 없다.

준비 CLI:

```bash
"$BASS_R4P0_PYTHON" -B prepare_closeout.py --inputs /exact/pinned/inputs --out /new/create-only/output
```

생성물:

- R4O_TEMPORAL_CLOSEOUT.json
- FINITE_SPAN_OBSERVABLE.json
- R4P0_TAIL_PREFLIGHT_CONTRACT.json
- B0_B3_BASIS_REGISTRY_CONTRACT.json
- FUTURE_NATIVE_TEMPLATES.json
- PREPARATION_RECEIPT.json

선택 observable의 현재 재현값: reference `0.009653432376161852`, N768 `0.009653417329471998`, N1536 `0.009653428615023815`. Reference의 R4O 표기와 1 ULP 차이가 있다. Observable order는 약 `2.00020498`; 확률 8 ULP envelope를 error ratio의 log2 interval에 전달하여 R4O의 근삿값을 대조한다. 실제 gate threshold는 그대로 유지한다.

고정 receipt의 비율로 얻은 temporal orders: p_ref `2.000008800630865`, p_self `2.000046457686088`. R4O에 기록된 근삿값과 최대 1.75e−12 차이를 원본 receipt와 함께 보존한다.

Tail plan은 signed z=±16/20/24/32 총 8 operator-only 표본이다. 계획 query_id는 PLAN_ONLY 식별자이며 qualified-provider cache ID가 아니다. 미래 실제 context/cache IDs는 별도 승인 실행기에서 byte identity와 함께 고정해야 한다. 최대 88 raw attempts는 11개 ordered ladder의 제안 상한이며 현재 승인/소비가 아니다.

B0/B1/B2/B3 symbolic channels=18/46/92/124. Positives는 positive_rank로 표기하고 실제 radial binding 시 energy/residual/sign/order를 검증한다. Registry nesting은 semantic nesting이다. B1–B3 실제 coefficient identity 및 full Gram은 미측정이고 higher-l backend blocker가 있다. B0 certificate를 상속하지 않는다.

## 재현과 배포

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  "$BASS_R4P0_PYTHON" -B -m pytest -q -p no:cacheprovider tests
"$BASS_R4P0_PYTHON" -B verify_preparation_package.py /path/to/preparation.zip
```

make_preparation_package.py는 clean exact commit만 허용한다. SOURCE_PINS.json, FUTURE_AUTHORIZATION_TEMPLATE.json, MANIFEST.json과 ZIP digest를 기계적으로 생성한다. verify_preparation_package.py는 CRC/전 파일 manifest 검사 후 새 빈 디렉터리에 추출하고 py_compile, full focused tests, preparation CLI를 수행한다. `PYTHONPATH`와 외부 fixture 환경변수를 제거한다. native/launch trap 테스트와 nonce 불생성을 확인한 실제 결과만 replay PASS로 기록한다.

capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false; continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
