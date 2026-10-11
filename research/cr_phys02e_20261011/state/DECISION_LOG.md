# PHYS02E 결정 기록

1. 사용자 2026-10-11 09:46:56 KST 연구 루프 계속·NCP 인계 요청으로 현재 PR33 원본 반환을 읽었다. 기존 백업 업로드·추가 첨부 없는 전달 권한은 유지된다.
2. 이전 성공한 준비 판정이 실제 launcher 실패를 덮지 않도록 PR33 독립 HOLD를 출발점으로 채택했다. 원래 실패 예약은 소모되었다.
3. 다음 질문을 저장 E의 semantic admission으로 닫았다. 원인을 특정 CPU/libm으로 단정하거나 allclose 허용을 추가하지 않았다.
4. Astra가 고정 계약·정확 입력·허용오차·2G/2pulse/3600s 새 NCP 범위를 정의했다. 코드 및 소규모 시험·문서·발행 준비는 정책에 따라 lower-tier 요청으로 분담했다. 실제 backend identity는 독립 확인되지 않았다.
5. 이론 기여자는 후보 도출, 구현자는 자기 범위 테스트, source intake만 맡았던 별도 Astra는 독립 검토를 수행한다. root가 그 판정 hash를 받아 DAG를 결속한다.
6. 실제 시험은 두 배치 모두 exit0, 실패/repair0. 새 물리 G/pulse0. 이후 코드는 독립 검토와 최종 restore gate만 통과하면 발행한다.
7. 새 ZIP/시작문서는 create-only로 두 기존 백업에 추가하고, 실제 ID·SHA와 science commit을 외부 receipt로 결속한다. 자기 archive hash/업로드 ID를 같은 archive에 넣는 순환을 만들지 않는다.
