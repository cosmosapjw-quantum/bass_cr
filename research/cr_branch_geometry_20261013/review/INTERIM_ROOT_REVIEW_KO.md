# Root 후보 분과의 중간 독립 심사

- 단위: CR-THEORY-BRANCH-GEOMETRY-20261013.
- 상태: INTERIM_NO_BLOCKING_FINDING. 최종 승격 판정과 manifest 동결은 아직 하지 않았다.
- 역할: 후보 증명·코드·검산의 비저자. 외부 원전 조사를 맡았으나 후보 핵심 구성을 작성하지 않았다.
- 방법: 원문 유도, API 구현, 실행 check source, 실제 결과 JSON과 Wolfram raw를 읽었다. 실행 결과와 현재 source hash를 비교하고 Wolfram inline body와 별도 body의 일치를 확인했다.
- 과학 suite 재실행: 0. 이전 baseline 변경: 0.

## 1. 반응 후 원자 branch — RB.1–18

RB.4는 고정 prefix에서 원자 가중치, 기저 수, 기저 에너지의 변화가 모두 들어간 quotient derivative다. 기존의 기저 에너지 변화만 있는 특수식을 반응 경로 전체로 확장해 쓴 것이 아니다.

RB.5–6의 한 raw state scan은 명시된 chi >= 3/2, 양의 base count·energy, 비음 가중치, 고정된 정렬 support 아래 성립한다. Upper violation으로 원자를 추가하면 새 lower condition을 유지한다. Lower violation으로 제거하면 온도가 증가하지 않고 제거된 에너지는 새 upper side에 남는다. 각 방향에서 최대 M회 이동하므로 방향 전환 없는 종료 주장이 타당하다. 가중치 0인 항은 엄밀한 온도 변화 대신 등호를 허용하므로 증명과 코드에서 모순되지 않는다.

이 결과는 유한 endpoint 선택이며 경로 전체의 교차 수나 모든 EOS root의 유일성을 보장하지 않는다. 후보가 inherited index를 선택 입력으로 유지하고, C1 경로의 유한 교차 주장에는 transversality·separation 등이 추가로 필요하다고 제한한 점을 확인했다.

실제 단일 HI sharing contribution은 확률을 원 rate coefficient 안에 유지한다. 원 ghost와 첫 node의 분배 및 fast daughter를 함께 사용하며, 기저 electron count와 raw atom count가 중복되지 않는다. RB.15–17의 scalar extent fixed point 유일성과 cutoff branch의 유일성은 구별되어 있다. h(s)의 단위는 초이고, 표에 매우 큰 값이 나온 것은 구성한 낮은 밀도·선택 contribution의 step parameter다. 실제 cosmological elapsed time의 정확성으로 승격되지 않았다.

실행 기록은 5개 extent에서 동일 initial state와 동일 사건 열의 raw state를 사용한다. 네 invariant와 extent residual은 모든 기록에서 0이며, s=1/5의 복수 branch, s=1/4의 equality ownership과 양의 jump가 해당 check source의 실제 assert에 연결된다. 현재 관련 source 4개의 SHA256는 기록과 일치했다.

## 2. 공변 massive geometry — BG.1–14

Signature, physical momentum q, observer energy E=-c n.p, observer clock과 expansion tensor K의 단위가 서로 맞는다. 가속 normal에 대해 local observer clock을 전역 시간 gradient로 동일시하지 않았고, synchronous geodesic normal에서만 cosmological proper time으로 줄인다. K의 양의 팽창 부호와 ADM의 다른 부호 규약도 분리되어 있다.

Bianchi I의 P_i=a_i q_hat_i 보존은 대각 homogeneous metric의 spatial Killing symmetry에 한정된다. 일반 Bianchi 유형의 scalar work 식과 방향 transport를 혼동하지 않는다. Exact massive energy와 nonrelativistic source speed를 함께 사용할 때 원 source 모델의 적용 범위를 바꿨다고 주장하지 않은 점도 확인했다.

Packet count 보존과 proper-volume 밀도 희석은 BG.13–14에서 구분된다. 배경 work accumulator G는 kinetic energy의 signed 장부이며 국소 gravitational stress tensor로 해석하지 않는다. Cutoff 재분류와 thermal collision heat에 geometry work를 중복 합산하지 않는다. 기저 thermal fluid의 geometry work는 별도 closure 입력으로 남겨져 있다.

BG.11의 안정적 에너지 평가·kernel rebind·projection error의 실제 구현은 다른 author의 분과가 아직 준비 중이므로 여기서 구현 판정을 내리지 않았다.

## 3. Wolfram + xAct 원출력

공식 package의 세 SHA256와 실제 package/kernel version이 raw에 기록되어 있다. 출력은 MathLink -> False, 여덟 이름 붙은 tensor residual -> 0, AllZero -> True다. 시작·종료 기록의 script SHA256와 현재 script bytes가 일치하며, script에 inline된 body는 checks/xact_branch_geometry_body.wl와 일치했다.

이 확인은 규정한 normalization·spatial constraint·product rule의 tensor algebra에 대한 실제 실행 증거다. MassShellDecomposition 잔차는 momentum decomposition을 확인하며, 질량껍질 자체는 본문의 물리 가정과 결합된다. xAct가 Einstein equation이나 source kernel의 경험적 정확도까지 확인했다는 판정을 하지 않는다.

## 4. API와 남은 통합 범위

AtomicRaw와 함수들의 정확성은 주석·type annotation에서 명시한 Fraction 입력 계약 아래 판정했다. k_b와 chi 이외의 모든 state에 대한 runtime exact-type 강제가 구현된 것은 아니므로, 비정확형·비유한 입력까지 검증된 범용 API로 표현해서는 안 된다. 현재 실제 witness는 해당 Fraction 계약을 지킨다. 이는 현재 scoped 결과의 수정 요구가 아니다.

Coupled branch domain/error, geometry rebind·remap code, 새 scalar batch, 최종 CONTRACT/CLAIMS/DAG는 아직 이 중간 심사에 포함하지 않았다. 최종 과학 파일의 목록과 hash는 모든 분과 완료 후 별도로 결속한다.

## 5. Finding 지위

현재 root 분과에서 수정이 필요한 blocking 또는 nonblocking 수학 finding은 0건이다. 새 strong no-go는 0건이므로 NG1–NG7에 의한 금지 결론을 생성하지 않는다. 유한 sharp-cutoff 분류의 복수 root와 jump는 관측한 구성의 성질이며, 물리 문제 전체의 불가능성으로 확대하지 않는다.

