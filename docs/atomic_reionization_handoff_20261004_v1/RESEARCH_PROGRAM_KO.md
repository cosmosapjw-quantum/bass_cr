# 네 스레드를 닫는 실행 연구계획

## 채택 결론

기본 목표는 새 원자 계산의 완결이 아니라 명시한 원자 provider/domain에서 유효한 첫 reionization 결과다. 기존 원자물리의 HOLD/OPEN 상태를 보존하면서 응용용 완료 조건을 별도로 만든다. 수치 인증·보존법칙·소스 동일성은 생략하지 않는다. 이미 있는 소비자 API와 공개 계수를 연결하고, 필요한 차이가 실제 관측량에 영향을 줄 때만 정밀 확장을 호출한다.

원자 provider와 우주론 executor를 분리한다. HH/He는 작은 계수·도함수·domain·소스 family 패킷을 내고 rei_bianchi가 한 번의 paired campaign(REI-F09)을 실행한다. HH-F3/HE-F3는 그 동일 결과를 수락한다. 초기 CR-off baseline은 CR-on 연구와 HH/He의 선택 확장 때문에 막히지 않는다. 실행 이후 원자 효과가 사전 예산을 넘거나 정의역 밖이면 해당 provider만 확장한다.

## 현재 코드에서 확인한 출발점

| 스레드 | 실제 상태 | 이번에 먼저 할 일 | 보존할 한계 |
|---|---|---|---|
| rei_bianchi | Rust 일곱 고정입력 kernel과 shared-parent primitive | 완전한 H/He 사건·열 map, nonlinear certificate, 적응 적분, 기하 adapter 구현 | 이전 [160,161] 구간의 실패를 새 homogeneous 모델의 성공으로 덮지 않음 |
| bass_cr | R4AO 한 origin_P 실제 finite cell, 전체 grid 아님 | CR-off source=0, provider calls=0를 실제 receiver에 연결 | G02 unresolved, production HOLD, capture false, all-bound OPEN |
| WU088_HH | FD2 네 callback·네 saved-ball 비교, 새 적분 0 | 외부 HH source family와 consumer seam | 24/289 accepted, 265 unbounded, epsilon_C/R 미정 |
| BASS_HE | B5C2 전자점 8·독립 endpoint 5·고유 검사 59는 기존 기록 | 이미 있는 B3 GM25 constant API와 KF96 대안을 명시 | scientific PROMOTE HOLD, Eq55 NOT_RUN, physical source false |

이 표의 과거 runtime 수치는 저장소 기록을 읽은 것이며 이번에 원래 큰 계산을 재실행한 결과가 아니다. 현재 commit은 각 `REPO_SNAPSHOT.json`에 고정되어 있다.

## 채팅에서 완료한 선행 작업

- 원자 수·전하·자유전자 stoichiometry, 광이온화 threshold/열 배분, proper/comoving 회계, 온도식의 입자수 변화항과 팽창항의 소유권을 유도하고 유한 검산했다.
- H 상수율 oracle 및 H/He synthetic controlled fixture를 구체화했다. fixture는 구현 검증용이고 물리 EoR history가 아니다.
- nonlinear implicit-map 인증에서 필요한 residual, inverse Jacobian, uniform Hessian, sparse remainder와 독립 checker 조건을 유도했다. point AD를 구간 enclosure로 오인하지 않게 했다.
- Grackle 3.4.1 선택 원문과 license를 보존하고 Verner H/He fit parameter·공식·단위·domain을 잠갔다. 소스 파일 일부는 참조용이며 완전한 Grackle build가 아니다.
- HH 반응의 source convention에 추가 1/2가 없음을 고정했다. Grackle k57의 저온 tiny branch와 고온 공식 사이의 불연속, derivative domain을 명시했다.
- He의 기존 B3 GM25/W82 계수 1.70e-13 cm3/s와 KF96 대안의 충돌을 문헌과 실제 코드에서 확인했다. 하나의 임의 평균으로 숨기지 않는다. He RCT scalar rate만으로 photon/heat spectrum을 정할 수 없다는 계약도 고정했다.
- 네 저장소의 원래 plan/DAG/gates/API를 byte 보존하고 source commit/path/hash로 연결했다. He T4의 원래 16-node DAG는 백업을 실제 복원해 회수했다.

완료하지 않은 선행 항목은 물리 오차 envelope, He 에너지 분배, 실제 소비자 인증 및 물리 시나리오 admission이다. 코드를 실행해야 판정되는 사항을 채팅에서 완료로 적지 않았다.

## Fastest track: 작업 순서와 PR 단위

| 단계 | 소유자/노드 | 구체 산출물 | 다음으로 넘어갈 조건 |
|---|---|---|---|
| 모델 계약 | REI-F00, HE-F1 병렬 | source/closure lock, 기존 He API의 명시 source family | 암묵적 opacity·case·domain 없음 |
| provider+oracle | REI-F01/F02 | coefficient adapter·동차 opacity·해석 H step | 외부 원문 일치, 보존/극한/domain 검사 |
| 결합 map | REI-F03; 이후 CR-F0 | species·열·광자 회계, controlled fixture, CR 무호출 증거 | rejected candidate write=0, 회계 잔차 평가 |
| 인증 | REI-F04→F05 | uniform remainder와 첫 전체 canonical interval | 엄밀 local error <2e-4, public width <2e-3; tolerance 완화 없음 |
| 기하·물리 입력 | REI-F06/F07 | Bianchi/FLRW adapter와 science scenario lock | 정의역·source·IC·관측량·허용 예산 선등록 |
| 첫 물리 결과 | REI-F08 | 동일 원자 realization의 paired histories | 전체 applicable domain의 수치 gate, claim 명시 |
| 원자 감도 | HH-F1/F2, HE-F2→REI-F09→HH-F3/HE-F3 | 단일 campaign 결과와 각 provider 수락 판정 | 사전 정의한 관측량 예산; 초과 시 한정 확장 |
| 응용 종결 | HH-F4 및 각 return | 적용 범위와 재개 조건을 갖춘 완료 기록 | 기존 원자 인증의 HOLD를 보존한 scoped application closure |

PR_PLAN.json의 구현 PR들은 이후 작업 단위다. 이번 게시 PR과 실제 구현을 완료한 PR은 구분한다. 선택한 기존 연구 branch의 PR에는 누적 이력이 포함되므로 이번 packet commit만 별도로 검토할 수 있게 링크를 제공한다. HH PR33과 He PR17은 기존 draft를 유지한다.

## Mid/long-term lane: 언제든 호출 가능

`LEGACY_LANE.json`은 원래 시작점, 미해결 gate, 원문 사본, 백업 locator와 재개 조건을 보유한다. 다음 중 하나가 구체적으로 선언되면 필요한 하위 lane을 활성화한다: (1) 새 관측량/에너지/온도 domain, (2) source family 차이가 과학 예산을 초과, (3) 현재 provider에 없는 spectrum·angular·excitation·capture 정보, (4) 사용자 요청에 따른 원래 정밀 연구 자체의 재개.

F09 완료는 legacy 재개의 일반 선행조건이 아니다. 예를 들어 F07에서 recombination/secondary 입력이 물리 시나리오에 필수라고 판정되면 필요한 확장만 즉시 호출할 수 있다. 기존 원자 문제 전체를 baseline의 공통 선행조건으로 다시 연결하지 않는다.

| lane | 보존한 다음 연구 방향 | 빠른 경로와의 접점 |
|---|---|---|
| CR legacy | R4AP weak-K single-entry cover/error allocation와 후속 bound/capture | 새 CR-on spectrum 또는 현재 외부 CX domain 부족 시 adapter를 교체 |
| HH legacy | C0/C1/B22 및 FD2 이후 실제 continuum·remainder 인증 | 동일 provider 계약을 만족하는 새율/오차 certificate가 도착하면 sensitivity만 재평가 |
| He legacy | B5C3 이후 small-R/join, T4 원 DAG, coherent/continuum 확장 | scalar B3를 energy-resolved moments로 확장할 때 동일 회계 계약 사용 |
| rei extension | REC/secondary, 정밀도·기하·모델 확장 | 선택 scenario에 필요한 부분만 dependency를 선언해 활성화 |

## 실패 처리와 작업 종료

환경 오류와 수치 불수락, 물리 모델 한계, 문헌 소스 충돌을 별도로 반환한다. 환경 실패를 과학 실패로, 유한 검산을 전역 인증으로 승격하지 않는다. 실패한 step/state와 엄밀 임계값은 남긴다. domain 밖에서 clamp·silent extrapolation·임의 smoothing을 도입하지 않는다.

각 작업은 지정 입력 hash, 실제 명령/exit code, 산출물, claim ceiling, 다음 노드를 반환해야 한다. 완성되지 않은 runtime를 `EXECUTION_STATE.json`에 completed로 넣지 않는다. 일정은 실행 gate로 관리하며 측정되지 않은 소요일을 약속하지 않는다.
