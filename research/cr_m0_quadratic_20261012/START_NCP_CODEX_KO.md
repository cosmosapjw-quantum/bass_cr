# NCP handoff — M0 이차 주입 응답 완료

현재 branch는 `research/cr-m0-quadratic-response-20261012`, 기준 commit은 `ae2d246d7e9037e000b00cd89991beb6f837f2ee`다. root AGENTS와 이 디렉터리의 `README_KO.md`, `HANDOFF.json`, `NEXT_DAG.json`를 읽는다. 기존 사용자 작업에 reset/clean/stash 또는 일괄 덮어쓰기를 하지 않는다.

**이번 M0는 여기서 완료했으며, NCP에 새로 실행할 작업이 없다.** 저장된 pRS의 이차 이력 응답, exact 2×2 PSD 경계, 그림을 위해 NCP job·runner·pilot·benchmark·재검산을 만들지 않는다. 이전 M0 evaluator, 이번 evaluator와 과거 suite도 완료 확인을 이유로 반복 실행하지 않는다.

아직 시작하지 않은 H 전체9600 qualification은 보류다. 실제로 존재하는 미수집 H run이 있다면 그 source의 원래 `--collect` 절차만 이어받는다. 기존 수집·부재 확인 기록은 재사용하고, 이번 M0를 이유로 같은 NCP 부재 확인을 반복하지 않는다. 미게시 현지 상태를 확인하지 못한 곳에서는 UNKNOWN을 유지한다. 새 폴더나 unit 이름으로 원래 reservation·소모 예산을 초기화하지 않는다.

원 H의 8build/76800열/900초/retry0과 원 numerical/resource/runtime 계약은 그대로다. F/G 및 나머지 physical gate를 유지한다. 새로운 2×2 유리수 부등식은 원 F raw CSC의 복구나 full9600 성능 측정이 아니다.

다음 연구는 ChatGPT에서 M1 실제 consumer 이력·스펙트럼·bath/domain·관측량·오차 예산을 연결하고 M2 이차 근사의 잔차와 응답 오차를 평가한다. CR-off receiver 상태는 해당 저장소에서 실제 증거와 연결한다. 모든 비음 이차 source 안의 모델 차이를 일반 cosmological source나 물리 입력 정확도로 승격하지 않는다.

새 NCP 실행은 구체적인 CR 과학 질문 또는 선택된 성능 연구, 캐시·경량 방법의 부족, 필요한 출력, 비용·병렬 독립성, source·누적 예산·종료조건을 한 activation 기록으로 정한 뒤에만 한다. 다른 workload에 원 H worker 수·예산을 자동 적용하지 않는다.

완전 전달 ZIP에는 이번 결과·직접 유도·첫 그림 실패와 복구 기록·독립 검토, 그리고 원 계획 조정 완전 ZIP을 byte 그대로 포함한다. 추가 첨부가 필요하지 않다. 최상위 최신 START가 내부에 보존된 과거 H 자동 실행 안내보다 우선한다. 새 ZIP의 실제 Git commit·Drive/Dropbox ID·크기·SHA256은 외부 START와 전달 영수증을 따른다. 같은 bytes를 이미 보유했으면 재사용하며 실제 source 복구가 필요한 경우에만 안전한 manifest와 새 디렉터리를 사용한다.
