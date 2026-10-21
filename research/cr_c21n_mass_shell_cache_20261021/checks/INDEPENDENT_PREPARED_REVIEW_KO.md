# C21N 준비된 운동량 격자 독립 검토

**판정: `PASS_SCOPED`.** 현재 C21N 준비 계층은 고정된 PR147 물리 소스의 생성식과 원 C21M 초기조건 사상을 유지한다. 검토 범위에서 게시를 막는 결함은 발견하지 않았다. 이 판정은 생성자·초기조건·저장된 상태에서의 fields/RHS 평가에 대한 것이며, C21N으로 전체 ODE 경로를 새로 적분했다는 뜻은 아니다.

검토자: 독립 협업 agent `/root/external_results`. 구현자가 만든 수치 검산을 다시 실행하지 않고, 소스·차이·AST·SHA256을 독립 확인하고 실제 v2 영수증의 범위를 검토했다. 자세한 입력 결속과 제한은 [INDEPENDENT_PREPARED_REVIEW.json](INDEPENDENT_PREPARED_REVIEW.json)에 있다.

## 검토한 소스

| 대상 | SHA256 |
|---|---|
| C21N `prepared_momentum.py` | `a6230c3f814785d1301444fdf335254f12a9ee9e71e533cdcbf58aee3e000d0b` |
| C21N `builder.py` | `5009f638393888f90b1939fdfcb8d386aece2b8f194baa0a54860045756ce274` |
| 원 C21M `builder.py` | `7fb15e89403817812588e189c013d45d200864f0076351c7c84bf77667520f0f` |
| 고정 FV 생성자·물리 소스 | `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5` |
| 수정된 focused test | `6fb90c061ac4989c4d31a5a87096c1c0474a0e12341d333fa73e93917ac3229d` |

원 물리 source commit은 계속 `3b85dedce84d37b3e165da00685a8a984950aafe`다. C21L `SOURCE_MANIFEST.json`에 고정된 9개 vendor 파일의 크기와 SHA256이 모두 일치함을 별도로 확인했다. `IndependentStressBuilder`는 원 소스 검증을 수행한 뒤 template과 factory를 만든다.

## 부동소수점 순서와 초기 분포

공유되는 값은 Gauss 격자, compactified momentum, 각도 좌표, FD radial weight, 고정 질량의 초기 에너지처럼 (A)에 의존하지 않는 양이다. 다음 식의 곱셈과 나눗셈 순서가 원 생성자와 같다.

\[
W=1+A(3\mu^2-1)/2.
\]

특히 ((3\mu^2-1)/2)를 미리 만든 뒤 (A)를 곱하도록 재배치하지 않았다. 매 (A) 시도마다 `W`, packet weight, cell population, reference energy normalization, 전체 cell number와 최소 cell population을 새로 만든다. `reshape(...).sum(axis=(1,3))`, 에너지 정규화와 number sum의 reduction 순서도 원 생성자와 같다. 기존 분포를 둔 채 scalar `amplitude`만 바꾸는 방식은 없다.

`component_fields`, `_set_shear`, `solve_case`는 원 C21M과 AST가 같다. `build`는 운동량 객체를 만드는 한 호출을 factory 호출로 바꾼 것 외에는 AST가 같다. 따라서 signed full Frobenius 좌표, matter/radiation 분리, 공통 photon/neutrino 초기 (k), positivity·정규화·Hamiltonian 검사와 허용오차가 유지된다. 원 40성분 RHS와 DOP853 적분기를 계속 상속하며, `n=101`, `rtol=3e-11`, `atol=3e-13` 및 FP64 출력 조건도 같다.

## 불변성과 case 격리

factory 배열과 각 case의 분포는 immutable Python `bytes`를 backing으로 갖는다. 단순히 `writeable=False`를 지정하는 것보다 강한 조건이며, 보통의 ndarray API로 다시 쓰기 가능하게 바꿀 수 없다. configuration은 frozen dataclass, 배열 dictionary는 read-only mapping이다. `make()`와 `identity()`는 배열 identity·dtype·shape·strides·writeable 및 configuration을 다시 확인한다.

서로 다른 case가 공유하는 것은 격자 data다. 각 case는 독립 ndarray view와 새 packet/cell byte buffer를 받는다. 다음 (A) 시도는 앞선 case의 분포를 바꾸지 않는다. 이 보호 범위는 준비된 입력에 한정된다. 반환된 원 model 객체를 임의로 수정하거나 Python reflection으로 접근 제약을 우회하는 상황까지 방어한다고 주장하지 않는다. 독립 factory만 직접 쓰는 경우 vendor manifest 검증은 호출자의 책임이며, 이번에 검토한 production 진입점은 이를 확인하는 `IndependentStressBuilder`다.

## 실제 수치 검산을 수용한 범위

[prepared_momentum_v2.json](prepared_momentum_v2.json)은 네 그룹이 통과했음을 기록한다. 현재 구현·테스트 파일의 SHA256이 영수증의 identity와 일치한다.

| 검산 | 실제 범위와 비교 방식 |
|---|---|
| 원 생성자와 비교 | 질량·격자 3개 설정 × (A) 5개 = 15개. 배열 shape/dtype/bytes, 정규화·number의 FP64 bytes 비교 |
| 원 moment와 비교 | 위 15개 설정의 시간·왜곡 3개씩, 총 45개 moment 상태의 FP64 bytes 비교 |
| 초기조건 사상 | 기존 26개 + 실제 NCP 반환 98개 + 재사용 중심 1개 = 125개. mapping receipt는 dictionary equality, 초기 state는 FP64 bytes 비교 |
| 저장된 물리 상태 | 각 case의 index 0, 50, 100: 총 375개. fields의 수치 성분 22,125개와 RHS 성분 15,000개의 FP64 bytes 비교 |
| 격자 재사용·격리 | 공유 geometry, 별도 분포, 쓰기 가능 전환 거부, configuration 변경 거부, shape 변경 감지, 입력 domain 거부 |
| 반복 (A) 준비 | `leggauss`를 실패 sentinel로 바꾼 뒤 5개 (A) 시도 성공 |

초기조건 125개는 두 실제 run manifest와 원 중심 case에서 읽었고, 125개 physical target이 서로 다름을 독립적으로 확인했다. 수치 비교의 기준은 `optimized=False`인 원 C21M builder이므로 원 FV 생성자와 원 moment 식을 사용한다. 검산 동안 적분 진입점은 실패 sentinel로 교체되어 있다.

**mapping receipt의 dictionary equality를 모든 값의 byte equality로 확대하지 않는다.** 초기 state, fields, RHS에는 실제 byte 비교가 있다. 또한 375개 저장 상태의 일치는 전체 trajectory 재적분의 일치와 구분한다.

첫 v1 실패는 run manifest의 nesting을 잘못 읽어 `KeyError('contract')`가 난 harness 오류다. 실제 125개 loop에 진입하기 전의 실패이며, 원 실패 영수증과 실행된 test source가 보존되어 있다. 현재 test는 해당 경로를 `manifest['manifest']['grid']['cases']`로 바꾼 한 줄만 다르다. 이 수정으로 production builder나 factory를 바꾸지 않았다.

## 외부 방법의 정확한 기여

immutable bytes backing과 metadata/kernel identity guard의 원 참고 구현은 REI ACCEL01의 `cached_context.py`다.

- 원 구현 commit: `526870b3e36ad8354c58c761567b1b37829033b2`.
- 파일 SHA256: `f9508fa69f838f5c859334fd260c59825ce0a9ddf06c85fe596e49a6cbc1d282`.
- 동일 파일이 유지된 최신 확인 delivery: `98fcf3943fa54e089b0292d166c3a47becb5edb8`.

ACCEL01의 C15 물리 source나 `(x,b)` LRU moment 결과 cache를 PR147에 이식하지 않았다. 이번의 현지 기여는 원 PR147 생성자의 (A)와 무관한 준비를 재사용하면서, (A)에 의존하는 모든 물리 가중치와 정규화를 원 순서대로 다시 만드는 구현이다.

## 완료 상태와 제한

| 축 | 이 독립 검토의 상태 |
|---|---|
| `EXECUTION` | 소스·AST·hash 감사 완료. 수치 test 재실행 0, 신규 ODE 0, benchmark 0 |
| `PUBLICATION` | 검토 파일 생성 완료. push는 연구 coordinator가 수행 |
| `BACKUP` | 검토자가 provider 업로드를 수행하지 않음 |
| `DAG` | 준비된 생성자와 저장 상태의 fields/RHS 검토 `PASS_SCOPED`; 신규 C21N ODE `NOT_RUN` |

허용 domain 전체·모든 platform의 bitwise 일치를 증명한 것은 아니다. 속도 향상, 메모리 감소, 64-core scaling을 측정하거나 주장하지 않는다. 일반 triaxial 모델, full reionization·UV·stars·완성된 CMB 예측은 기존 범위 밖에 남는다. `global_error_bound=null`을 유지한다.
