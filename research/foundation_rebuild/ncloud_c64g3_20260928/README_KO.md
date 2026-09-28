# NAVER Cloud c64-g3: 승인 계획, 복구된 입력, Codex F0 retry

상태: **F0_RETRY_READY_REPO_CONTAINED_INPUTS_NATIVE_IMPLEMENTATION_PENDING**.

초기 F0 handoff는 설계 ZIP, TP2D 전체 RETURN ZIP, 승인 환경을 외부에서 찾지 못해
`STOP_F0_BLOCKED`로 종료됐다. 그 run은 그대로 보존한다. 이후 사용자가 전체 TP2D RETURN ZIP을
직접 제공했고, byte/hash/ZIP/내부 manifest를 검증한 뒤 필요한 세 ZIP과 환경 provenance를
이 branch에 게시했다.

## 이번에 사용할 문서

1. 저장소 루트 `AGENTS.md`, `docs/READBACK_POLICY.md`.
2. 이 디렉터리의 `AGENTS.md`, `ARTIFACTS.json`, `STATUS.json`.
3. **`F0_RETRY_HANDOFF_KO.md`**: 현재 Codex retry 지시. 이것이 최초
   `CODEX_HANDOFF_KO.md`보다 F0 입력 위치와 환경 admission에 대해 우선한다.
4. `IMPLEMENTATION_PLAN_KO.md`: F0-F3 장기 계획.
5. `DUAL_BACKUP_AUDIT.json`: Dropbox/Google Drive 조사와 복구 기록.

## GitHub에 포함된 F0 입력

`artifacts/`에 다음 exact bytes가 들어 있다.

- `tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip`
  - SHA-256 `630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
  - 31,849,212 bytes, 1,279 runtime query pairs.
- `BASS_NCLOUD_C64G3_REDESIGN_20260928.zip`
  - SHA-256 `2c0600f742490ab89b63ff7810f8655a7cd9f43631669db13d08abf4b2c6a1df`.
- `BASS_TP2E_RESEARCH_20260928.zip`
  - SHA-256 `0f7af63b234b8ae527ac1c1ba42c28a9cf89b39f79da329d2b73d8aa2896c7b0`.
- `requirements-tested.txt`, `HISTORICAL_ANALYTIC_BUILD.json`,
  `F0_ENVIRONMENT_CONTRACT.json`, `TP2D_RETURN_AUDIT.json`.

따라서 F0 retry를 위해 Downloads, Dropbox, Google Drive에서 추가 파일을 찾지 않는다.
현재 source checkout을 바꾸지 않고 `git show <plan-ref>:<path>`로 별도 staging에
materialize할 수 있다.

## 범위

F0는 cache-only M4 한 번뿐이다. 새 spatial operator 평가와 새 DOP853 solve는 0회다.
F0 실패 후 자동 patch/retry/native compile/F1-F3로 전환하지 않는다.
F1-F3는 여전히 구현·비용 승인 전이다.

항상 유지:
`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`,
`original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`.
원 TP2D `TEMPORAL_REFINEMENT_UNRESOLVED`는 변경하지 않는다.
