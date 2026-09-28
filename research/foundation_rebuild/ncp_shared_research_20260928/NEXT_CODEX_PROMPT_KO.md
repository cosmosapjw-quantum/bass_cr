# R3 code is implemented: cloud review/repair/run only

기존 R3 구현 지시는 완료되어 이 인계로 대체한다. 원 지시는 parent Git history에 보존된다.

사용자에게 전달된 implementation branch/HEAD/tree를 fetch하고 검증한 뒤 다음을 읽고 수행한다:

research/foundation_rebuild/ncp_shared_research_20260928/CLOUD_REVIEW_RUN_HANDOFF_KO.md

ChatGPT가 주요 코드와 신규 테스트를 구현/검증했다. Cloud Codex는 관련 diff의 집중 점검, 재현된 결함의 in-scope 수정, 준비된 single-process cache-only 실행과 결과 반환만 담당한다. 전체 코드 재작성 또는 완료된F0/F1/R2/native scientific run 재실행은 금지한다.

권한 범위, 입력 해시, 실제 구현 결과는 IMPLEMENTATION_RESULT_KO.md와 runtime_r3/INPUT_PINS.json에 있다. 기존 scientific source/threshold/model/basis는 변경하지 않는다. Source pins를 현재 파일에 맞추어 자동 수정하지 않는다.

capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO, continuous_global_supremum_bound=false.
