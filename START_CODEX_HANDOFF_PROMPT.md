# START: BASS_CR local test operator

ROLE=LOCAL_CODEX_TEST_OPERATOR_ONLY
REPO=cosmosapjw-quantum/bass_cr
TARGET_REF=feat/fnd-r2-test-only-20260925
MODE=EXECUTE_FIXED_TESTS_AND_RETURN_EVIDENCE

기존 작업 checkout에서 `research/foundation_rebuild/LOCAL_CODEX_HANDOFF_KO.md`와 `VALIDATION_CONTRACT.json`을 읽고 그대로 실행한다. 전체 40자리 EXPECTED_SHA는 게시 완료 메시지에 제공된 값을 사용한다. git fetch 후 FETCH_HEAD 일치를 검사하고 non-destructive detached checkout을 사용한다. 사용자 변경과 충돌하면 reset/clean/stash하지 말고 identity/worktree blocker를 보고한다. 새 worktree를 만들지 않는다.

```sh
git fetch origin refs/heads/feat/fnd-r2-test-only-20260925
test "$(git rev-parse FETCH_HEAD)" = "$EXPECTED_SHA"
git switch --detach "$EXPECTED_SHA"
python3 research/foundation_rebuild/run_validation.py --profile local --expected-commit "$EXPECTED_SHA"
```

이미 과학 의존성이 설치된 interpreter는 그 절대경로로 대체할 수 있다. 의존성 부족은 ENVIRONMENT_BLOCKED로 반환하고 production 환경을 임의로 upgrade하지 않는다. 코드/알고리즘/허용오차/기저/하네스/모델 routing을 변경하거나 추가 연구를 시작하지 않는다. local LLM과 Keystone는 실행의 필수 dependency가 아니다.

실행기가 새 테스트와 고정 S/H/D 사례, 원 repository 회귀시험을 수행하고 단계별 stdout/stderr/receipt/manifest/RETURN ZIP을 만든다. 실패를 PASS로 만들려고 재시도, skip 추가, threshold 완화를 하지 않는다. 반환은 실제 HEAD, 단계별 passed/failed/skipped, 최초 blocker, 생성된 RETURN_REPORT.json 및 RETURN ZIP만으로 충분하다. PASS도 production HOLD / all-bound OPEN / b-grid NO_GO를 바꾸지 않는다.

기존 R3M10 시작 프롬프트의 역사적 버전은 base commit `8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f`의 이 경로에 남아 있다. 이번 세션에는 과거 구현자 역할을 상속하지 않는다.
