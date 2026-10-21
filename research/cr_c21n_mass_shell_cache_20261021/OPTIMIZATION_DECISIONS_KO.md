# C21N 최적화 결정

## 구현한 경계

`PreparedMomentumFactory`는 worker의 builder마다 한 번 가우스 노드·compactified radial 좌표·angular 좌표·Fermi–Dirac radial weight·초기 energy를 준비한다. 실제 trial마다 `W(A)`, packet numbers, cell populations, reference energy normalization, total number, minimum cell을 다시 생성한다. 원 source의 `CanonicalMomentumFV` 또는 이미 검증된 `ExactReuseMomentum` 객체에 이 자료를 연결하고 원 moment/RHS/integrator를 그대로 호출한다.

정확한 부동소수점 평가 순서를 보존하기 위해 `(3*mu*mu-1)`을 저장한다. 이를 미리 `/2`한 P2로 바꾸면 원 `A*numerator/2`의 순서와 달라질 수 있다. 모든 sum 축과 순서도 원 constructor와 같다. 이 변경은 수식의 근사나 solver 변경이 아니다.

불변 자료는 `tobytes` 후 `frombuffer`로 연결한다. 단순 writeable flag를 다시 켜는 수정을 거절하며, dataclass configuration과 array shape/dtype/strides/writeable metadata를 사용 전에 확인한다. 서로 다른 A의 packet/cell arrays는 공유하지 않는다. 이 방어는 일반적인 우발적 변경에 대한 것으로 hostile native-memory 변조에 대한 보안 경계는 아니다.

## 실제 검증 범위

`checks/prepared_momentum_v2.json`: 15 constructor configurations, 45 moment states에서 bytes 일치. 기존125 target의 mapping receipt 값이 같고 초기 state bytes가 같다. 시작·중간·끝 375개 저장 상태에서 fields 22,125 FP64 값과 RHS 15,000 FP64 값이 bytes 일치한다. 원 ODE integrate entry는 검증 중 금지했다. 초기 v1의 manifest key 오류는 하네스 오류이며, 실패 영수증과 당시 테스트 source를 보존했다.

반복 A trial 이후 quadrature 함수를 호출하면 실패하게 한 검증 5개가 통과했다. 이는 반복 생성 연산이 제거됐다는 구조적 검증이다. elapsed speedup, peak RSS 절감, 전체 sweep 시간 개선을 뜻하지 않는다. 이러한 성능 값은 `UNMEASURED`다.

## 이미 있는 경로와 재사용한 외부 근거

C21L의 Legendre/moment 행렬 재사용과 동일 moment 공통항 재사용, C21M의 독립 case multiprocessing·bounded dispatch·create-only raw·공유 lease는 유지한다. REI ACCEL01의 bytes backing 및 metadata guard 설계를 source에 결속해 재사용했다. C15의 `(x,b)` LRU 결과 캐시와 다른 물리 solver는 가져오지 않았다. 자세한 출처는 `EXTERNAL_REUSE.json`에 있다.

HH75는 같은 finite-L8 radiation matrix의 exact exponential과 shear-memory 분석을 제공한다. 이미 완료된 연구를 다시 구현하지 않았고, 이번 국소 mass-shell derivative의 물리적 비교 자료로만 수용했다. Reduced state solver로 전환하면 adaptive error norm까지 바뀌므로 현재의 40상태 bitwise 동등성 범위에서 도입하지 않았다. VigilODE의 FV kernel도 다른 prescribed geometry/Thomson 범위이므로 교체하지 않았다.

## 추가한 운영 제약

새 C21N 입력 schema/run ID와 source에 결속한 completed125 registry를 사용한다. 완료된 좌표와 각 축의 차이가 모두 `<=2e-13`이면 거절한다. 별도 측정 목적의 재실행 우회 옵션은 없다. 원 distribution·tolerance·출력은 그대로다.

출력 파일시스템의 `f_bavail`과 `f_favail`을 run/lease 생성 전에 확인하고, 실행 중에도 새 dispatch 전에 다시 확인한다. 관측값은 예약이나 quota 보증이 아니며 외부 disk 소모가 생기면 진행 중인 case를 보존하면서 새 dispatch를 중단한다. CPU55, coordinator 비용, 1 numeric thread, 동적 CPU quota/RAM/load/lease 제약은 C21M 코드 그대로다.

원 RHS의 return array를 공유 mutable buffer로 재사용하는 최적화는 넣지 않았다. SciPy integrator가 받은 값을 보유할 수 있으므로 이를 하려면 별도의 생명주기 검토가 필요하다. Mixed precision, fastmath, solver/tolerance 변경, GPU 이전, 대규모 성능 캠페인은 이번 범위 밖이다.
