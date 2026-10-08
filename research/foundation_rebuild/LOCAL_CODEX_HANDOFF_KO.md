# START: BASS_CR fixed validation only

ROLE=LOCAL_CODEX_TEST_OPERATOR_ONLY
REPO=cosmosapjw-quantum/bass_cr
TARGET_REF=feat/fnd-r2-test-only-20260925
MODE=NO_NEW_CODING_NO_RESEARCH_REDESIGN
SOURCE_AUTHORITY=research/foundation_rebuild/SOURCE_MANIFEST.json
EXECUTION_CONTRACT=research/foundation_rebuild/VALIDATION_CONTRACT.json

기존 CP3의 `LOCAL_CODEX_TWO_CENTER_FOUNDATION_IMPLEMENTER` 역할은 이 인계로 대체된다. 두 중심 S/H/D의 bounded 코드와 테스트는 이미 제공되어 있다. 테스트를 위해 추가 구현, 논문 조사, 계획 문서 재작성, 하네스/모델 설정 변경을 시작하지 않는다.

## Intake

기존 bass_cr checkout에서 수행한다. 새 worktree/clone, git clean, reset --hard, 자동 stash, force push는 하지 않는다. 사용자 변경은 보존한다. 전달 메시지의 전체 40자리 EXPECTED_SHA를 사용하여 target ref를 fetch하고 FETCH_HEAD 일치를 확인한다. 불일치하면 branch를 임의로 추정하지 말고 identity blocker를 보고한다. `git switch --detach EXPECTED_SHA`가 사용자 변경과 충돌하면 중단하고 원본을 유지한다.

```sh
git fetch origin refs/heads/feat/fnd-r2-test-only-20260925
test "$(git rev-parse FETCH_HEAD)" = "$EXPECTED_SHA"
git switch --detach "$EXPECTED_SHA"
python3 research/foundation_rebuild/run_validation.py --profile local --expected-commit "$EXPECTED_SHA"
```

과학 패키지가 설치된 별도 interpreter가 이미 있으면 python3 대신 그 절대경로를 사용한다. 기본 후보는 기존 `/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python`이다. 기존 환경을 최신 버전으로 업그레이드하지 않는다. 의존성 부족은 코드 결함과 구분하여 ENVIRONMENT_BLOCKED로 반환한다. 새 환경을 쓸 때에만 `requirements-validation.txt`를 사용하며, source나 threshold를 바꾸지 않는다.

## 실행

실행기는 자동으로 새로운 runs/fnd_validation/<UTC>_<id>를 만든다. Source manifest와 frozen cr_repro digest를 확인하고 다음 고정 단계만 실행한다.
1. CP3 + R2 + validator regression tests.
2. 고정된 두 중심 analytic/FEM/ETF operator cases와 atomic spectrum/pseudostate bank.
3. 원 repository tests를 별도 subprocess로 실행한다.

로컬 LLM, Keystone, Codex worker 재분배는 runtime dependency가 아니다. source/test/허용오차/기저/격자 설정을 수정하지 않는다. 실패를 통과시키기 위한 retry·fallback·skip 추가를 하지 않는다. 실패하면 최초 stdout/stderr, receipt, 체크포인트와 RETURN_REPORT.json을 그대로 반환한다. TIMEOUT/INTERRUPTED는 수치 NO_GO와 구분한다. GPU skip을 GPU PASS라 부르지 않는다.

## 반환

실행기가 출력한 RETURN ZIP 및 RETURN_REPORT.json 경로, 실제 HEAD, 단계별 test/failure/error/skip 수, operator-case 측정값, 최초 blocker만 보고한다. PASS라도 원래 capture gap 해소나 production 승인을 선언하지 않는다. source 변경이나 다음 capture 연구를 시작하지 않는다. 이번 세션의 목적은 제공된 구현의 로컬 재현 시험이다.

## 남은 과학 범위

General radial-FEM cross-center convergence, high-n/continuum completeness, CAP/finite-time, original A3/B3 discrepancy, all-bound and b-grid는 별도 연구로 남는다. 이를 여기서 해결하기 위한 코딩을 local Codex에 떠넘기지 않는다. 논문/private raw의 완전 일치나 rigorous global certificate를 새 선행조건으로 넣지 않는다.
