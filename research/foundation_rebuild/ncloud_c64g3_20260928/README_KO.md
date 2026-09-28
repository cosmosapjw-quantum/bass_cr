# NAVER Cloud c64-g3: 승인된 계획과 Codex F0 인계

상태: **PLAN_APPROVED_F0_HANDOFF_READY_NATIVE_IMPLEMENTATION_PENDING**.
이 커밋은 계획·인계 문서만 추가한다. 기존 물리 코드, 원 TP2D 실패 결과,
원 TP2E 패키지, 기존 AGENTS.md와 readback policy는 수정하지 않는다.

## 읽는 순서

1. 저장소 루트 AGENTS.md 및 docs/READBACK_POLICY.md.
2. 이 디렉터리의 AGENTS.md, ARTIFACTS.json, STATUS.json.
3. IMPLEMENTATION_PLAN_KO.md: 승인된 전체 F0–F3 계획과 현재 실행 경계.
4. CODEX_HANDOFF_KO.md: 이번 첫 Codex 실행 지시.
5. 원 설계 ZIP의 REDESIGN_KO.md, MIGRATION_RUNBOOK_KO.md,
   IMPLEMENTATION_PLAN_KO.md. ZIP identity는 ARTIFACTS.json이 고정한다.

원 설계 ZIP과 TP2E ZIP은 이 Git 커밋에 포함하지 않았다. 이미 제공한 파일을
로컬 Downloads 또는 /data/bass/inputs에서 찾아 hash를 확인한다.
원 TP2D 전체 RETURN ZIP도 별도 입력이다. 요약 JSON은 실행 입력의 대체물이 아니다.

## 이번 인계의 범위

Codex는 우선 F0의 고정 패키지 실행·로그 반환 담당이다. source 자동 수정,
테스트를 통과시키기 위한 patch, dependency 자동 업그레이드, 실패 재시도,
새 native 계산과 F1–F3 구현을 이번 F0 인계에서 수행하지 않는다.
F1–F3는 계획에 명세됐지만 아직 존재하는 실행기로 취급하지 않는다.

cache-only M4 비교가 통과하면 그 결과를 반환하고 종료한다.
실패하면 first blocker와 완성된 부분 결과를 보존하고 종료한다.
원 TP2D TEMPORAL_REFINEMENT_UNRESOLVED를 PASS로 덮지 않는다.

cloud VM 생성·SSH target·환경설치·과금 budget은 계획 승인만으로 만들어지지 않는다.
기존에 준비·승인된 호스트와 환경에서만 실행한다. main merge/force push,
기존 worktree 정리, credentials 게시, 서버·볼륨 삭제를 금지한다.
