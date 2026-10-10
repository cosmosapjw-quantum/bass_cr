# CR-PHYS02D 동일 9600 격자 펄스 실행 준비

현재 물리 실행 상태는 **PREPARED_NOT_EXECUTED**이다. 로컬 검증은 최대 2개 활성 상태의 해석적 toy와 표준 라이브러리 운영 검증에 한정된다.

## 명령

새 단위 디렉터리에서 실행한다.

```bash
python ncp/launch_pulse.py --plan
python ncp/launch_pulse.py --execute --run-dir evidence/runs/PULSE_새로운식별자
python ncp/launch_pulse.py --collect --run-dir evidence/runs/실제실행디렉터리 --out evidence/returns
```

`--plan`은 NumPy/SciPy를 import하지 않는다. 두 계약, 입력 파일, 전이 의존성 manifest, 동결 FILE_MANIFEST 또는 BUNDLE_MANIFEST, DAG READY와 독립 PASS_SCOPED 심사 해시를 확인한다. 아직 심사나 동결 payload가 없거나 자원이 부족하면 HOLD가 정상이다. 실행은 위 예시처럼 명시한 새 디렉터리 또는 `--run-dir` 생략으로 생성되는 기본 디렉터리 중 하나만 선택한다. `--execute`의 기본 디렉터리 이름은 UTC와 UUID로 생성되며 기존 디렉터리를 덮어쓰지 않는다. 직접 `--worker`를 실행해서 coordinator를 우회할 수 없다.

## 실행 경계

실제 수치 환경은 Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0 및 실제 수치 threadpool 1개 thread를 요구한다. 전역 설치는 허가되지 않았다. 반환된 `ops.py`는 원본 그대로이며 매 operator build 전에 자원을 확인한다. 가장 제한적인 보이는 메모리에서 max(12.5%, 1 GiB)를 예약한 뒤 작업 가능 메모리 12 GiB 이상, 여유 디스크 8 GiB 이상, 유효 CPU 1 이상이 필요하다.

fullBED 다음 legacy 순서로 정확히 Cascade(3200,6400)를 구성한다. 최대 operator build 2회, pulse expm_multiply 2회, 총 coordinator wall budget 3600초이며 자동 재시도는 없다. 각 모델은 두 birth 열을 한 번에 17개 u=i/16 시각에서 계산한다. 저장된 NPZ의 source_vectors 전체를 초기 상태로 사용하며 direct cutoff와 internal counter를 보존한다. 저장된 시간은 정확히 [0,1e10]이고 에너지 격자는 array_equal이어야 한다. 열원 heat 초기 행은 정확히 0이어야 한다. 이전 ramp 실행과 네 번째 격자는 허가되지 않았다.

## 입력 및 산출물

필수 고정 입력은 state/SCIENTIFIC_CONTRACT.json, ncp/NCP_EXECUTION_CONTRACT.json, inputs/INPUT_IDENTITIES.json, inputs/DEPENDENCY_PAYLOAD_MANIFEST.json이다. FILE_MANIFEST 또는 BUNDLE_MANIFEST가 실제 파일을 검증하고, state/NEXT_DAG.json의 해당 task가 READY이며 review/INDEPENDENT_DECISION.json의 해시와 독립성 및 코드 심사 범위가 일치해야 한다.

실제 실행 디렉터리는 PLAN_AND_ADMISSION.json, RESERVATION.json, RUNTIME.json, 모델별 RESOURCE_BEFORE_BUILD, BUILD/PULSE 예약, stdout.log, stderr.log, PULSE_fullBED_9600.npz 및 PULSE_legacy_9600.npz, RESULT_<model>.json, 성공 시 NUMERICAL_RESULT.json, ACTUAL_EXIT.json을 포함한다. 실패 시 도달한 파일만 존재하며 삭제하거나 성공으로 간주하지 않는다. create-only 반환 ZIP은 실제 run, 새 단위 src/ncp/state/inputs/review, toy/운영 첫 실패 evidence, manifest로 고정한 전이 의존성 및 운영 adapter를 포함한다. RETURN_MANIFEST.json은 반환된 모든 payload 파일의 byte 수와 SHA256을 기록한다.

## 해석 한계

CDF는 원래 주입 전자의 eventual heat 에너지를 기준으로 한 pulse 누적분율이다. 현재 ramp heat의 ancestry age, 유한창 clipped moments, 무한시간 frozen-operator moments는 서로 다른 양이다. 무한시간 moments는 고정 수학 연산자의 연장에 조건부인 결과이며 우주적 시간 역사 예측이 아니다. 저장 ramp의 J1/J2와 일치하는지는 동일 연산자의 대수적 점검이지 독립 물리 검증이 아니다. 9600에서의 새 pulse는 pulse mesh convergence, production 승인, 전체 PHYS02_DELAY 해결, CCC identity 해결 또는 NCP64 scaling을 뜻하지 않는다. 실제 반환 파일과 독립 Astra 심사 없이 실제 물리 PASS를 선언할 수 없다.

반환 ZIP의 source_unit/은 연구 단위의 REPORT, START, theory, endpoint evidence, tests와 심사 파일을 포함한다. RESTORE_LAYOUT.json 및 README_RESTORE.txt 지시에 따라 dependency_payload/을 저장소 root에, source_unit/을 research/cr_phys02d_20261011에 overlay한다. 실제 run은 별도 새 위치에 보존한다. 복원 후 manifest 및 심사 해시를 다시 확인한다.
