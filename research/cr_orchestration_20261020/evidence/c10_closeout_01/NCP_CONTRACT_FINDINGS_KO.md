# C10 NCP orchestration 계약 대조 — 문서 마감

## 범위와 판정

정확 readback의 `cr_orchestration_20261020/NCP_ORCHESTRATION_KO.md`를 그대로 읽고, 같은 readback의 unchanged I `run_optimized_pilot.py`, H/I `CODEX_HANDOFF_KO.md`, H/I publication receipts에 연결했다. 이 작업은 publisher 문서 호환성 확인이며 새 C9 검토나 구현/시험 루프가 아니다. Runtime·tests·raw 변경 0, solver/test 실행 0, networking/GitHub mutation 0이다.

**새 orchestration의 H/I 실행 CLI, 외부 receipt, detached content checkout, ancestry, FD parent 연결에서 알려진 receipt 형식 문제 이외의 추가 구체 실행 불일치를 발견하지 못했다.** G runner 자체나 새로운 native 동작을 검증했다는 판정은 아니다.

## F1 — 기존 H handoff와 새 receipt의 PR 형식 불일치 (parent가 이미 수정 예정)

- 실제 readback H receipt는 `pull_request: 85`와 별도 `pull_request_url`을 가진다.
- H handoff의 `C21H_PR_URL` 명령은 `publication["pull_request"]["url"]`을 직접 읽는다.
- 따라서 이 H 인계 경로는 정수에 대한 indexing에서 멈춘다. I receipt도 현재 정수86이지만 I runtime `_publication`은 PR 필드를 소비하지 않는다.
- 최소 수정: H/I 문서 receipt에서 `pull_request`를 `{"number":85또는86,"url":현재실제PR_URL}` 객체로 맞춘다. 실제 URL은 현재 receipt의 `pull_request_url`에 이미 있다. 기존 별도 URL/번호 필드 보존 여부는 publisher 판단이다.
- `content_commit`, execution manifest, runtime은 그대로 유지한다. 새 native/test 실행이 필요한 수정이 아니다.

## F2 — 기존 handoff의 현재 상태 문장이 게시 완료와 모순 (표현 교정)

- H `handoff/CODEX_HANDOFF_KO.md`의 첫 blockquote는 아직 “현재 게시 중단”과 commit/branch/PR 미생성을 현재 상태로 쓴다.
- I `CODEX_HANDOFF_KO.md`의 “현재 상태와 역할”은 아직 H/I remote content commit·PR이 확인되지 않았다고 쓴다.
- 같은 readback의 최신 receipts는 H `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`/PR85, I `fe6bbaec2de5032b938aed0713623b9618ba70e6`/PR86을 `PUBLISHED`로 기록한다. 새 orchestration도 이를 명확히 설명한다.
- 최소 수정: 첫 현재 상태만 실제 게시 정보로 갱신하고 기존 거절 내용은 “역사 기록”으로 보존한다. 원 과학 ZIP, 원 실패/raw, immutable content commit은 수정하지 않는다.
- 이 문장 문제는 새 orchestration의 실행 인자를 바꾸지 않는다. 현재 receipt를 우선한다는 새 orchestration 규칙으로 실행 경로는 이미 정해져 있으므로 별도 실행 gate를 추가하지 않는다.

## 확인한 실행 연결

- orchestration은 H/I 최신 문서 head에서 receipts를 먼저 읽어 content checkout 밖 `CONTROL`에 보존한다.
- 같은 repo에서 H content ancestor I content를 확인하고 I content로 detached worktree를 만든다. 이는 I `verify_publications`의 same-checkout, ancestor 및 `HEAD == I_content`/detached 조건과 맞는다.
- I native/base와 FD 명령은 `--publication-receipt` 및 `--c21h-publication-receipt`를 둘 다 전달한다. I private authority는 실제 committed H8/I3 runtime+manifest와 receipt를 검사한다.
- H/I CLI의 `--source-dir`, `--c21g-unit`, `--baseline-dir`, `--bridge`, `--bridge-build-receipt`, `--native`, 선택 `--build-dir`, `--cpu`, `--fixture`, `--method`, `--variant`, `--base-job`, `--out` 연결은 기존 H/I 인계와 같다.
- I first row의 `vectorized/common_ic/vigilode-rodas5p/base`와 같은 mode/context FD 연결은 현재 source identity/verified_base 계약과 맞는다. H base를 I FD 부모로 쓰지 않는 설명도 맞는다.
- Locked build와 현재 환경에서만 필요한 linker workaround의 설명은 기존 H/I handoff 범위와 같다. 새로운 NCP 환경에서 build 성공이나 자원 가용성을 확인한 것으로 확대하지 않는다.

## 문서 마감 후 남는 경계

Parent가 receipt 객체와 현재 상태/DAG 문서를 최소 수정하여 실제 doc commit ACK를 기록하면 이 C10 문서 호환성 범위는 닫힌다. 추가 recursive review나 기존 tests 재실행을 요구하지 않는다. 실제 live 자원 확인, locked compile 또는 유효 build 재사용, 필요한 작은 환경 호환 수정, bounded native 실행은 기존 실행 인계에 남는다. Native chemistry와 과학 수렴/성능/global bound는 게시 완료에서 추론하지 않는다.

## 읽은 파일 identity

아래는 이 문서의 읽기 대상 바이트를 식별하며 새 검증 suite의 결과가 아니다.

- `cr_orchestration_20261020/NCP_ORCHESTRATION_KO.md`: 19254 bytes, SHA256 `a2f9066f021659c2a2124425096d09e83df43ae72143646203d50be69427584b`.
- `cr_c21i_callback_optimization_20261020/run_optimized_pilot.py`: 14719 bytes, SHA256 `1a3f4d9066bedc3a8d7466723e8f344fa451c0c6a85c48bf0efe03210d6d8a43`.
- `cr_c21h_vigilode_bridge_20261019/handoff/CODEX_HANDOFF_KO.md`: 25153 bytes, SHA256 `3d73d43590725fccff40d09828727e4e1ffcd4f614204ecbe9e3aee46b281235`.
- `cr_c21i_callback_optimization_20261020/CODEX_HANDOFF_KO.md`: 11856 bytes, SHA256 `d9172159d0aaac317b36574fda2765f5f299188dc2fafd8ac107ff47ff699f90`.
- `cr_c21h_vigilode_bridge_20261019/PUBLICATION_RECEIPT.json`: 825 bytes, SHA256 `499c39fd5c92b155f897ea8e38981b4be8d5af0990c7ea41bd4fba488e5335b4`.
- `cr_c21i_callback_optimization_20261020/PUBLICATION_RECEIPT.json`: 837 bytes, SHA256 `5580f3c8bf049a789e492be4a94f7d1bb3261213ab669ada7e8eb30a6b02a71d`.
