승인된 F1 NCP native admission을 딱 한 번 실행하고 결과를 GitHub에 게시해줘.

Repository: cosmosapjw-quantum/bass_cr
Control branch: research/fnd-ncloud-f1-engine-admission-20260928

Frozen implementation:
commit = 8236887dd8869de57522d5c87a48972f287969fe
tree = d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae

Owner authorization:
max_wall_seconds = 7200
spending_limit_krw = 8000
F1 native admission = approved

Approved existing storage:
NCP default CB1 100 GB /dev/vda
observed root filesystem /dev/vda2 ext4 mounted at /
F1 workspace = /root/.local/state/bass_f1
별도 /data volume을 만들지 마.

먼저 control branch를 fetch하고 아래 authoritative handoff를 읽어 그대로 실행해:
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_NCP_RUN_HANDOFF_KO.md

중요:
- scientific runner는 반드시 frozen implementation commit/tree의 detached worktree에서 실행해.
- RUN_AUTHORIZATION_20260928.json은 최신 control branch에서 외부 파일로 materialize해.
- current main checkout은 변경하지 마.
- F1은 serial, BLAS/OpenMP=1.
- 실행은 정확히 1회.
- 실패하면 자동 retry/patch/tolerance 변경 금지.
- PASS/FAIL 모두 execution_evidence/F1/<run_id>/에 sanitized evidence를 non-force push해.
- evidence publish 후 F2/F3를 시작하지 마.

완료 시 F1_NCP_RUN_PUBLISHED 블록과 게시된 GitHub 경로를 반환해.