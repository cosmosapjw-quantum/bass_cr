# R4AJ 실행 계획

현재 입력: R4AI REVISED_WORKFRONT의 LOCAL_BRIDGE_SELECTOR_AND_PHASE_GAP_DISCRIMINATOR.
새 범위: 저장된 candidate/channel과 기존 rank-5 reference를 비교하고, rank-1 1s 목적의 phase-gap 가능성 및 resonant cluster 대안을 유도·구현·경량 검증한다.

1. R4AI 직전 답변을 한국어로 완역한다. 역사적 수치 결과를 다시 실행한 것으로 말하지 않는다.
2. R4AB 저장 intrinsic matrix와 R4AG 채널 metadata를 exact identity로 읽는다. 원자 적분은 하지 않는다.
3. 저장 행렬쌍 자체에 대한 유리수 min-max/gap 및 1s selector residual bound를 만든다. 물리적 연속 행렬로 승격하지 않는다.
4. rank mismatch, 두 중심 퇴화와 잘못된 kinetic gap 경로를 판별한다. 측정 P1s와 propagation cluster Ppair를 분리한다.
5. resonant block을 보존한 Sylvester primitive와 propagator 오차의 조건부 합성식을 구현한다. 미확립 입력은 null/거절한다.
6. 새 코드 단위시험, 별도 정확 대수와 작은 synthetic dynamics 검산만 한다. 원자 native/shifted/M9/기존R8/기존suite/메모리prepare 호출은 모두0.
7. DBv21을 보존하고 append-only v22 연구 evidence를 만든다. 두 외부 작업(R4AH와 이론 입력)의 의존성을 갱신한다.
8. 동일 branch exact-base용 create-only patch, 문서, 재현 ZIP을 검증하고 Drive/Dropbox 백업을 시도한다.

경량 자원 상한: 개별 새 검산 command wall60초, 배열차원18 이하, native 원자루프 금지. 성공 주장 전에 실제 exit와 결과를 확인한다.
물리 gate: G02 UNRESOLVED, production HOLD, capture false, all_bound OPEN, b_grid NO_GO.
