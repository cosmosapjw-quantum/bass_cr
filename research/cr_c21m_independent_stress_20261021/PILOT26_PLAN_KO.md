# C21M 26 신규 적분 + 1 기존 기준점 계획

## 실행 범위

`grid_pilot26.json`은 signed full Frobenius 좌표
`S0 = [-0.012, 0, 0.012]`, `Pm0 = Pr0 = [-0.0002, 0, 0.0002]`의
27점 중 중심을 제외한 26점을 명시한다. 초기 분포와 모든 40성분 방정식은
고정 REI 원 source를 사용하며 저장 시점은 101개다. Solver는 DOP853,
rtol `3e-11`, atol `3e-13`, 구간은 z=20에서 z=4다.

중심은 C21L `runs/pilot81/cases/s04_p04`의 완성된 원 trajectory를 재사용한다.
해당 파일을 복사·수정하거나 ODE를 다시 풀지 않는다. 실제 초기 signed 좌표는
`S0=0`, `Pm0=-2.111149637247e-19`, `Pr0=+2.1111496372470007e-19`이다.
이는 원 quadrature와 총응력 사상의 아주 작은 상쇄 offset이다. 그림의 요청 좌표
`(0,0,0)`와 실제 초기 좌표를 모두 저장한다. 새 builder가 정확히 같은 초기 상태를
생성했다고 주장하지 않는다. 기준점 원 source, input identity, raw와 receipt hash,
원 k와 runtime은 `REFERENCE_REUSE.json`에 고정돼 있다.

`GRID_DEDUP.json`은 C21L81, HH63, REI PR198 parent625, matter600,
mixed6의 실제 소스에 선언된 grid를 대조한다. PR198의 half-contraction 좌표는
모두 sqrt(2)를 곱해 비교한다. 중심 외 26점의 해당 범위 내 중복은 없다.
외부 전체 raw를 모두 다시 다운로드한 검토는 아니다. 다른 비공개 대화·접근할 수
없는 실행 반환·관측하지 못한 백업은 `UNAVAILABLE`이며 전역 부재를 뜻하지 않는다.
C15 warm source-on729와 그 BASS176/REC116 재사용 결과는 별도 물리 문제다.

## 실행과 분석 명령

이 디렉터리에서 실제 가용 자원과 협력 lease를 확인한 다음 실행한다.
아래 경로는 예시이며 이미 사용된 run 경로를 덮어쓰지 않는다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 shared_runner.py \
  --grid grid_pilot26.json --output runs/pilot26 \
  --workers 4 --execution-site sandbox --plan-only

PYTHONDONTWRITEBYTECODE=1 python3 shared_runner.py \
  --grid grid_pilot26.json --output runs/pilot26 \
  --workers 4 --execution-site sandbox

PYTHONDONTWRITEBYTECODE=1 python3 analyze_pilot.py \
  --run runs/pilot26 --output analysis_pilot27
```

NCP에서는 실제 host를 확인하고 `--execution-site ncp`를 사용한다. worker 수는
준비된 작업 수와 현재 quota·affinity·가용메모리·lease·CPU 부하에 제한된다.
운영 상세는 `SHARED_OPERATIONS_KO.md` 및 shared runner의 실제 옵션을 따른다.
실행 시작 후 builder·runner·resource 및 vendor source는 바꾸지 않는다.
완료 결과가 있는 run의 재개는 동일 manifest에서 아직 시작하지 않은 case만 허용한다.
완료점의 분석 재실행은 새로운 output 디렉터리로만 가능하다.

## 분석 산출물과 검증

`analyze_pilot.py`는 C21L `analyze_components.components`를 그대로 호출한다.
source bytes, run manifest, case reservation, completion seal, raw와 receipt의
SHA256를 검증하고 26개 신규 결과가 모두 완료됐을 때만 27점을 합친다.
운영 test double은 과학 결과로 받아들이지 않는다.

`components27.npz`는 signed 좌표, norm, gamma/nu 분리, 각 대각 tensor,
cancellation과 원 `Y[27,40,101]`, 네 복사 multipole 배열을 모두 보존한다.
CSV는 요청한 초기 좌표와 실제 초기·최종 좌표를 함께 제공한다. source pressure
`Pi_*_J_m3`는 tensor norm이 아니라 `pi_s=Delta p/3`이다. H의 단위가 초의
역수이므로 dimensionless full 좌표는 `sqrt(6)*(8*pi*G/c^2)*pi_s/H^2`다.

첫 그림은 각 S0 slice에서 최종 signed 총응력과 같은 S0의 zero-stress 기준점에
대한 최종 signed shear 차이를 보여준다. 3×3 셀은 각 실제 입력점이며 보간하지
않는다. 두 번째 그림은 S0=0의 두 opposing-stress trajectory에서 matter,
radiation, total의 signed 값, signed shear와 cancellation을 함께 보여준다.
이 그림들은 양의 norm과 signed 좌표를 명시적으로 구별한다.

`checks/pilot_preparation_checks.json`은 적분 없이 26개 초기 분포의 실제 builder
사상과 중심의 저장된 40×101 데이터·hash·물리 gate를 확인한 영수증이다.
해당 영수증만으로 새 26개의 적분 완료나 그림 검토를 주장하지 않는다.
실행 후 `PHYSICS_CHECKS.json`, `SUMMARY.json`, `OUTPUT_MANIFEST.json`이
그때의 실제 검사 범위와 원본 bytes의 불변을 기록한다.

`global_error_bound=null`. 본 계획은 preliminary collisionless non-tilted LRS
연구이며 일반 triaxial, full H/He/UV 재이온화 또는 완성된 CMB 예측을 뜻하지 않는다.
