# BASS c64-g3: 승인 계획과 Codex 시작점

Repository-side plan: [IMPLEMENTATION_PLAN_KO.md](../../research/foundation_rebuild/ncloud_c64g3_20260928/IMPLEMENTATION_PLAN_KO.md).
첫 실행 지시: [CODEX_HANDOFF_KO.md](../../research/foundation_rebuild/ncloud_c64g3_20260928/CODEX_HANDOFF_KO.md).
입력 pin과 상태: [ARTIFACTS.json](../../research/foundation_rebuild/ncloud_c64g3_20260928/ARTIFACTS.json),
[STATUS.json](../../research/foundation_rebuild/ncloud_c64g3_20260928/STATUS.json).

승인된 순서: F0 cache-only M4 → 필요 시 F1 new-engine admission → F2 calibration → F3 CF4.
현재 Codex handoff는 준비된 F0만 실행한다. F1–F3는 미구현이며 비용 상한도 미지정이다.
이 commit은 문서 추가만 수행하며 기존 source/result/native engine/main은 바꾸지 않는다.
원 설계와 실행 package ZIP은 외부 입력으로 유지하고 ARTIFACTS.json의 SHA로 검증한다.
