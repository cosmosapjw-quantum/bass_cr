# FND full S/H/D 통합: 검증된 cross 재사용

기준 commit: `f472e8f379d0e08f4e4a834f04040e3089c4f3f3`.
작업 단위: `FND_FULL_OPERATOR_INTEGRATION_FROM_VALIDATED_CROSS_V1`.

## 새 구현

`full_operator.py`는 TT/PP를 각 중심의 전체 구에서 계산하고, 변경하지 않은 `reaudit_20260925/repair/aligned_cross.py`의 TP/PT와 결합한다. 다른 중심 Coulomb은 유한 각운동량 공간에 대한 정확한 multipole projection으로 적분하며 radial mesh를 핵간 거리 R에서 추가로 나눈다. Coulomb softening, eigenvalue 대입, 모드 삭제, 사후 Hermitian symmetrization을 사용하지 않는다.

`H_cc-iD_cc=H0_cc+Vother_cc`의 ETF 상쇄, 독립 구면 직접 적분, 내부/외부 Coulomb scalar oracle, p multipoles, 직접 기저 시간미분, 작은 full S의 시간차분, support 및 provenance negative controls를 새로 검사했다. 내부 단위는 a0, Eh, ta다. `D`는 Hermitian 행렬이 아니다.

저장된 order24 cross를 재사용할 때 kernel hash, matrix hash, geometry/time 및 모든 ordered channel identities를 확인한다. 기저 identity가 다르면 에너지가 비슷해도 자동으로 재결합하지 않는다. 기본 경로는 기존 cross ladder를 재실행하지 않는다.

## 수행된 검증과 한계

개발 환경의 새 시험: **23 passed / 0 failed / 0 skipped**. 기존 34/84/492개 suite는 반복하지 않았다. 실제 18x18, 100 keV/u, b=2 a0, z=-12 a0의 full static snapshot을 저장된 cross로 구성했다. TT/PP quadrature order12->20의 full S/H/D 차이는 약 1.89e-16 / 2.34e-16 / 1.93e-16이다. 최소/최대 metric eigenvalue는 약 0.99506914 / 1.00493086, ratio는 0.99018667이다. 정확한 출력은 `VALIDATION_EVIDENCE.json`과 전달 ZIP에 있다.

개발 검증은 복원된 원본 dependency layout에서 실행했다. repository CI를 새로 실행했다고 주장하지 않는다. Source pins와 로컬 반환물로 repository 실행을 재현한다. 작은 basis의 full metric 시간차분 검사는 통과했지만 큰 18-channel 전 궤적 수렴이나 capture propagation까지 검증한 것은 아니다.

`production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture_execution_allowed=false`를 유지한다. GPU full run은 시작하지 않는다.

## 로컬 실행

기존 repo root에서 이미 성공한 order24 출력 디렉터리를 입력한다. 새 코딩이나 parameter tuning은 하지 않는다. Python/NumPy/SciPy/pytest는 앞 단계 환경을 그대로 사용한다. 설치·업그레이드를 자동으로 하지 않는다.

```bash
BASE="research/foundation_rebuild/full_operator_20260926"
# OUT24는 직전 성공한 run_cross_probe --order 24의 실제 출력 폴더다.
# 셸을 재시작했다면 그 실제 경로를 다시 넣는다. 임의의 latest 결과를 고르지 않는다.
CROSS24="$OUT24"
test -f "$CROSS24/RESULT.json" && test -f "$CROSS24/matrices.npz" || exit 1
OUT_FULL="runs/fnd_full_operator_$(date -u +%Y%m%dT%H%M%SZ)"
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 "$BASE/run_validation.py" --cross-dir "$CROSS24" --out "$OUT_FULL"
```

공식 인계문에 제공된 정확한 새 commit을 `--expected-commit`으로 추가할 수 있다. 실행기는 source pins, 기존 cross identity, 신규 23개 시험, 새 TT/PP 및 full matrix를 확인하고 `RETURN_REPORT.json`, NPZ, 단계 receipt, manifest, 반환 ZIP을 생성한다. 이미 존재하는 출력 경로는 덮어쓰지 않는다. 실패하면 첫 오류와 로그를 보존하며 자동 재시도하지 않는다.

성공 상태: `FULL_STATIC_OPERATOR_VALIDATION_PASS`. 이는 **위 고정 snapshot과 신규 시험**의 성공이지 전 궤적이나 capture PASS가 아니다. 단순 source-layout 또는 input identity 오류는 `IDENTITY_OR_INPUT_BLOCKED`, 의존성 import 실패는 `ENVIRONMENT_BLOCKED`, 수치 screen 실패는 `NUMERICAL_SCREEN_FAILED`로 분리한다.

결과 조회:
```bash
jq '{status,scope,steps,full_static,capture_execution_allowed,production_admission,all_bound,b_grid}' "$OUT_FULL/RETURN_REPORT.json"
```

다음은 이 구현을 사용하는 한정된 시간 의존 operator/transport pilot이다. full collision, b-grid, all-bound와 원래 GPU의 3% 차이를 이번 정적 결과만으로 승인하지 않는다. 이미 통과한 z=-12 cross ladder는 변경된 입력이나 검증 실패가 없는 한 다시 돌리지 않는다.
