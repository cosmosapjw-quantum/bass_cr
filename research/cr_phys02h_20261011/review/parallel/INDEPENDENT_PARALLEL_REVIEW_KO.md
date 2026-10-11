# PHYS02H 열별 병렬 생성의 local 독립 판정

## 판정

**PASS_SCOPED.** 고정 source의 열 계산을 분리하고 원래 순서의 CSC 저장을 조립하는 후보는, 실제 수행된 240상태 전체 행렬 및 저장된 9600격자의 선택 16열 범위에서 채택할 수 있다. 두 모델·두 반복의 16개 reference-candidate 쌍은 저장된 원시 값까지 정확하게 일치한다. source를 공유하는 이 비교는 계산 분해·조립의 구현 검증이며 독립적인 물리 oracle은 아니다.

이 판정은 별도 exact scalar 판정을 대체하지 않으며, 전체9600 연산자·NCP 실행·NCP64 성능을 승인하지 않는다. 변경 중인 NCP launcher는 읽거나 판정하지 않았다. 다음 NCP preparation은 별도의 고정 execution manifest와 aggregate resource contract에 대한 독립 판정에 연결해야 한다.

검토자 `/root/phys02h_decision_review`는 후보·허용조건·구현·생산 테스트 작성에 참여하지 않았다. 원본 및 후보 source를 읽고 stdlib만 사용하는 별도 읽기 전용 검사를 1회 수행했다. 생산 모듈 import, generator, pilot, 물리 공식 계산, 기존 테스트 재실행은 하지 않았다. canonical Astra v4.0.0 흐름을 유지하되 호스트 라벨과 실제 backend attestation은 구분한다.

## 고정 증거

| 항목 | SHA256 |
|---|---|
| Scientific contract | `a49b1fa88c86d46c4e37cdb7ba37fbd44e5fa05511febc3a3089ab5ed5331dc4` |
| Parent `causal_cascade.py` | `d87a9cc122125b2d37b47f261f57eab698baa59e07a6b21723860f39313c7b72` |
| `src/parallel_operator.py` | `3a7e89f158339712a2c1109b2599d3062fff21a1ab99fadf4f906f5375e3bfbd` |
| `scripts/run_parallel_pilot.py` | `b431a553880c27777ea0afbe60658bcd0cb1a7a5ddc7cfbf1a0bfd66c6a88454` |
| `tests/test_parallel_operator.py` | `549d35d6f8b70d4e1e9ba90b1c1071646646435b8103a7341b9fbeb9beca3ef0` |
| `evidence/parallel/PILOT_PLAN.json` | `069398cddac9ac4ac4dc7a9f67fc0fdcebb47fe794418623b2c536770706220c` |
| `evidence/parallel/pilot/RESULT.json` | `7546b4b8e04adae6f2d033c562ce7c3cfbf52a23ba54b0c655881276e19ada5a` |
| Independent payload checker | `32084ffff7d9e868b1c057a1cde86a9b26a0f1e14b414e4a4f84b2e899a74ff1` |
| Independent payload receipt | `4c5e3d414f857c35222f36ffe326f0212ad8508243b7ba1a8e7d764b1431752f` |
| Independent input inventory | `ed0d76abfc9231a7e32680c18abb8ab140db5d6bc133af6f178c101640ca596f` |

정확한 byte 수와 각 원시 NPY·sidecar·reservation의 identity는 `INDEPENDENT_INPUT_INVENTORY.json`에 보존했다. 기존 fullBED atomic 및 saved-grid adapter의 source도 frozen scientific contract의 지정 identity와 일치했다. 여기서 새로 읽은 것은 local 고정 입력과 실제 저장 payload이다. 원격 복구나 과거 대형 suite의 재검증을 수행한 것으로 보고하지 않는다.

## 열 독립성과 산술 순서

원본 `Cascade._generator`는 전체 E에서 speed·stopping·ionization·excitation rates를 먼저 계산한다. 그 뒤 각 j에서 새로운 dense `col`을 만들고, drift, species 순서의 ionization, 입력 channel 순서의 excitation을 누적한다. 외부 열의 계산 값은 읽지 않는다. `project`는 E와 고정 ledger 위치만 읽고 새 배열을 반환한다. `_sharing`의 변경 가능한 상태는 `normalization_diagnostics.append`이며 후속 열의 과학 값에 피드백되지 않는다. Gauss cache는 같은 order의 노드·가중치의 재사용이고 이 source는 그 배열을 제자리 변경하지 않는다.

따라서 현재 고정 source에서는 각 열이 `G[:,j]=T0 C_j(E, atomic, fixed parameters)`로 분리된다. 단순한 행렬 선형성에 의존한 가정이 아니라 실제 source의 읽기·쓰기 의존성으로 확인한 결과다. shell의 E, n, size, ledger mapping, atomic object, sharing_order=4, quantum_constant=0, mesh, 빈 diagnostic list가 원래 초기화와 연결된다. 저장 E는 immutable bytes를 backing으로 갖고 새 열별 구현은 과거 SavedGridCascade method identity를 사칭하지 않는다.

후보 AST는 함수 이름, 추가 `columns` 인자, 유일한 바깥 `enumerate(self.E)` iterator만 바꾼다. 독립 검사는 원본 source를 별도로 parse해 이 세 변경을 직접 구성했고, 되돌리면 원본 AST가 정확히 복원됨을 확인했다. 독립 계산한 hash는 실제 모든 worker의 저장된 proof와 일치했다.

- Original AST: `4ecb18cfe02877ff343f3a35f238ef1462b1b21e45b11c0e03356587c43c8761`
- Restricted AST: `bbc4b497f9f3b7ccef179162854bb2592e1effed38962f6c33324deebf61b669`

전체 precomputation, 열 내부 누적 순서, quadrature, `sum/dot/bincount` 입력, `np.asarray(values)*T_END`, sparse return은 유지된다. 원래 module globals에서 compile하며, low/fullBED의 서로 다른 atomic 구현도 원래 checked source를 사용한다. 이는 서로 다른 CPU dispatch 사이의 byte identity에 대한 정리가 아니다. 실제 실행한 동일 runtime 쌍에서 별도로 byte parity를 확인했다.

요청 열은 정렬되고 중복이 없어야 한다. 각 tile은 정렬된 요청 목록의 연속 부분이며 tile 전체를 이어 붙이면 요청 목록과 정확히 같아야 한다. 완료 순서와 무관하게 첫 열 위치로 tile을 정렬한다. 각 원래 열의 `flatnonzero`는 정렬된 고유 row index를 만들므로 동일 (i,j)에 대한 worker 간 부동소수 합산은 필요 없다. Gather는 CSC column slice를 원래 열 순서로 복사하고, data/indices를 concatenate하며 정수 indptr만 구성한다. Ledger 열과 선택되지 않은 열은 비어 있다. 생성자 호출 후 CSC 저장이 전달한 배열과 정확히 같은지도 검사한다.

Diagnostics도 tile의 열 순서대로 이어 붙인다. 독립 검사에서는 각 열의 저장된 ion rate가 0인지 여부와 species 순서를 이용해 실제 diagnostic의 `(species, energy)` 순서를 재구성했다. 전체 diagnostic 목록과 각 rate 배열의 raw bytes가 reference와 일치했다.

## 실제 payload 대조

읽기 전용 검사는 2026-10-11 09:01:57.813073–09:01:58.519571 UTC, **1회, 내부 wall 0.706529319초, exit 0**이었다. 60초 상한을 사용했으며 NPY header를 stdlib로 parse하고 원시 payload를 직접 비교했다. NumPy/SciPy 또는 생산 모듈을 import하지 않았다.

| 독립 검사 | 실제 결과 |
|---|---:|
| 저장된 실제 payload | 24 |
| NPY 파일의 dtype·shape·file/raw hash 대조 | 216 |
| 동일 입력 reference-candidate 쌍 | 16 |
| 두 반복의 reference 쌍 | 4 |
| 원시 배열 쌍의 직접 비교 | 180 |
| 저장된 열 occurrence | 3,968 |
| Diagnostic record | 4,592 |
| 저장된 partial worker AST proof | 44 |

모든 NPY의 비pickle 형식, C-order, little-endian FP64 또는 int32, 선언 크기 및 hash를 확인했다. 원시 음의 G 값을 보존하고 유한성·CSC 포인터 범위·정렬된 고유 row index·비선택 열의 공백을 대조했다. 작은 행렬은 251×251이고 240개 계산 열을 포함한다. 선택 행렬의 저장 shape는 9611×9611이지만 계산한 열은 고정된16개뿐이다. shape만으로 전체9600 생성이라고 해석하지 않는다.

선택 열은 0,3199,3200,3227,3228,3636,3637,4164,4165,4478,4479,6473,6474,8613,8614,9599이다. 원시 E hash는 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`이며, 끝점·split·여섯 anchor의 이웃이라는 고정 선택 규칙을 저장 E에서 다시 읽어 확인했다. E를 재생성하거나 generator를 실행하지 않았다.

## 실행 횟수와 성능의 의미

생산 pilot의 실제 외부 wall은 **66.284735842초**, 내부 wall은 **65.195421020초**, exit는0이다. 두 wall은 중첩되어 합산하지 않는다. 총 24개 논리적 생성은 작은 격자16개와 선택열8개로 나뉜다. 실제 generator invocation은 **52회 = 원본 작은 전체4 + 직렬 선택열4 + spawned partial44**이다. 이 수는 성공한 pilot에 대한 정확한 count다.

별도 targeted tests의 실제 4개 통과·약2.038648초 기록도 읽었다. 테스트는 serial restricted2회와 성공 partial4회를 포함한다. 주입된 오류는 해당 child의 generator 진입 전 발생했고, 취소된 sibling의 generator 진입은0 또는1회로 관측되지 않았다. 이 불확실한 테스트 횟수를 pilot의52에 섞거나 exact total로 만들지 않는다. 원본 테스트·pilot·과학 실행은 이번 검토에서 재실행하지 않았다.

작은 workload의 실제 end-to-end 결과는 후보가 직렬보다 느리다. 예를 들어 small fullBED의 두 반복 평균은 직렬 약1.065초, 4worker 후보 약3.049초이고, 선택16열은 각각 약0.527초와4.809초다. Spawn·fresh import·입출력과 gather 비용이 포함된 측정이며 local speedup을 주장할 근거가 없다. 64 CPU 또는 전체9600의 성능으로 외삽하지 않는다. 열 독립성은 병렬 실행 가능성을 제공하지만 동일한 열 수의 tile이 동일한 계산 비용을 갖는다는 보장은 없다. 전체 격자의 실제 load balance와 속도는 다음 별도 NCP qualification에서 판단해야 한다.

## 자원·실패·출처의 제한

저장된 admission은 cgroup quota8 CPU, memory.max8GiB, affinity inventory9 CPU를 구분한다. 계산 worker는 최대4개이고 coordinator1개를 더하며, 최소2GiB reserve와 당시 memory.current를 포함한 메모리 admission 부등식이 실제 각 후보에서 충족됐다. 현재 작은 메모리 호스트에서 전체9600 호출을 시작하기 전에 거부하는 guard도 읽었고 targeted test 통과 증거가 있다.

기록된 fresh-worker 및 coordinator lifetime peakRSS의 최댓값은 각각132059136 bytes, 약125.941MiB이다. 이 값은 getrusage의 프로세스 lifetime 최대값이며 per-build delta나 동시 전체 RSS가 아니다. `multiprocessing.resource_tracker` 같은 support process의 RSS는 이 telemetry에 포함되지 않는다. 같은 시각이 아닌 peak를 합산해 전체 메모리를 만들지 않는다. 원래 local quota에는 계산 worker·coordinator 이외의 CPU 여유가 있으나, 이 관측이 향후 두 lane·root·support를 갖는 NCP aggregate admission을 대체하지 않는다.

후보의 source에는 thread 환경1 설정과 worker 안의 `threadpool_limits(1)`이 있다. 저장된 runtime은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, OpenBLAS0.3.30/SkylakeX 및 thread1을 기록한다. 이는 이전 F 반환의 런타임과 동일하다는 근거가 아니다. 이번 두 모델의 실제 local parity만으로 과거 F 실패의 원인·정밀도·equivalence를 판단하지 않는다.

원시 양쪽 payload는 parity 이전에 저장되므로 이후 실패 시에도 값을 비교할 수 있게 되어 있다. 성공 payload의 source/runtime/assembly identity, 원시 CSC, 에너지, 각 rate, 순서 있는 diagnostics, create-only reservation을 유지한다. 주입 오류의 targeted cleanup 테스트는 소유한 multiprocessing 계산 child의 정리를 확인하며, 모든 가능한 OS descendant·OOM·호스트 중단 상황에 대한 인증으로 확대하지 않는다.

이번 local scope에서 차단할 결함은 발견하지 않았다. `F HOLD_OPERATOR_BINDING_UNRESOLVED`, `G frontier BLOCKED_BY_F_OPERATOR_BINDING_HOLD`와 기존 물리 gate는 유지한다. 이 local PASS의 다음 연결점은 고정된 NCP execution manifest의 독립 preparation 판정이며, 실제 NCP 실행이나 과거 operator의 채택은 아니다.
