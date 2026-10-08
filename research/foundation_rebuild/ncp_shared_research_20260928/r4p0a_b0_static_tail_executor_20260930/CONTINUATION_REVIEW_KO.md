# B0 정적 꼬리 실행기: 후속 구현 검토

2026-09-30. 기준: 원 R4P0 f7b5eef → 새 실행기 923f77d (4 commits ahead). 후속 실행기를 재사용하며 과학 계산은 수행하지 않았다.

## 재현과 수정
추가 시험 첫 최종 RED: 11 failed / 8 passed. 수정 후 기존 64개와 신규 19개 합계 83 passed / 0 failed / 0 skipped.
- 정상 진입점은 원래 88회 예산을 생성한다. 그러나 내부 execute_plan과 worker initializer 자체는 다른 예산도 수용했다. 두 경계에서 maximum=88, parent_attempts=0, workers=1..8 및 seed 동일성을 검증하도록 보강했다. 기존 과학 실행이 88회를 넘었다는 주장은 아니다.
- 이전 canonical 파일 충돌을 계산 후 발견했다. 이제 새 dispatch/reservation 전에 중단하며 이전 바이트와 최초 실패를 보존한다.
- 새 JSON은 파일 fsync 뒤 부모 디렉터리 fsync도 수행한다. 파일시스템 전반의 전원장애 복구 인증이라는 주장은 하지 않는다.
- 상태 없는 샘플에 null 값과 함께 P_selected_status/Pdot_status=unavailable_without_state를 기록한다.
- RESOURCE_POLICY.json을 추가하고 로컬 승인 제안과 source pins에 SHA-256을 결합한다.

## 검증 경계
집중 시험에 ctypes native loader 및 실제 승인 소비 함수 차단 장치를 넣었다. 예외를 삼켜도 teardown 검사가 실패하도록 구성했다. HOME도 시험별 임시 디렉터리로 격리한다. 소비된 ID 시험의 파일은 합성 fixture이지 실제 승인 소비가 아니다. 합성 평가 16회는 네이티브 원자 연산자 16회가 아니다.

원 R4F/R4G worker_runtime, GlobalBudget, provider, EvaluationLedger 및 native source/library/BUILD와 B0 bank, 전달된 rate/plan 모듈은 변경하지 않았다. 변경은 이 정적 실행기 디렉터리에 한정한다. 기존 전체/장시간 과학 suite는 재실행하지 않았다.

## 남는 승인/과학 경계
독립 reviewer 검토는 아직 수행하지 않았다. NCP에서 focused review, 실제 CPU/cgroup/RAM/경로/기한을 새로 확인하고 prepare_authority.py로 UNAPPROVED live proposal을 만든 뒤 중단한다. 새 proposal SHA에 대한 사용자 승인이 있기 전 launcher를 실행하지 않는다. Portable template는 live NCP 승인 증거가 아니다.

capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO. 8개 operator-only 점은 연속 꼬리 적분, 무한대 capture 또는 basis completeness를 증명하지 않는다.
