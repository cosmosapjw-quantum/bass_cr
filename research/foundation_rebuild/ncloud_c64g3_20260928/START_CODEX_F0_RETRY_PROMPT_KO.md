승인된 BASS NAVER Cloud c64-g3 F0 retry를 실행해줘.

Repository: cosmosapjw-quantum/bass_cr
Plan/data branch: research/fnd-ncloud-c64g3-codex-handoff-20260928
Minimum required input commit: 634f6fd3a2ff9b8dec94b104f693136b84accdab

현재 checkout과 사용자 수정은 그대로 보존하고 branch를 checkout하지 마.
branch를 fetch한 뒤 다음 문서를 git show로 읽어:
research/foundation_rebuild/ncloud_c64g3_20260928/F0_RETRY_HANDOFF_KO.md

그 문서가 현재 F0에 대한 authoritative handoff다.

중요한 수정:
- /data/bass는 F0의 필수조건이 아니다.
- 이미 준비된 /data/bass가 있으면 사용한다.
- 없으면 $HOME/.local/state/bass_f0 격리 workspace를 사용해 계속한다.
- local fallback은 cache-only F0에는 유효하지만 cloud throughput evidence가 아니다.
- disk format/mount/sudo로 /data를 만들려고 하지 마.
세 ZIP과 환경 lock은 모두 같은 GitHub branch의
research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/ 아래에 있으므로 Downloads/Dropbox/Drive를 다시 찾지 마.

핵심 범위:
- F0 cache-only M4 딱 한 번.
- exact archived operator cache만 사용.
- new spatial operator evaluations = 0.
- reference reintegration = false.
- fresh isolated venv는 F0_ENVIRONMENT_CONTRACT.json과 requirements-tested.txt의 exact pins로만 생성 가능.
- 원 TP2D TEMPORAL_REFINEMENT_UNRESOLVED를 바꾸지 마.
- 실패 후 patch/retry/F1/F2/F3/native compile/probe/CF4/DOP853로 자동 전환하지 마.
- current worktree reset/clean/stash/rebase/merge 금지.
- 결과는 RETURN_CONTRACT.json에 맞는 F0_RETURN_HANDOFF.json, 새 RETURN ZIP, HOST/environment receipts로 반환해.

항상 유지:
capture=false
production=HOLD
all_bound=OPEN
b_grid=NO_GO
original_capture_gap_resolved=false
continuous_global_supremum_bound=false
