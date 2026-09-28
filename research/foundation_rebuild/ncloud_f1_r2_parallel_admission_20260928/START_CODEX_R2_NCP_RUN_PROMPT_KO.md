승인된 F1-R2 60-worker NCP admission을 정확히 한 번 실행하고 결과를 GitHub에 게시해줘.

Repository: cosmosapjw-quantum/bass_cr
Control branch: research/fnd-ncloud-f1-r2-parallel-admission-20260928

Frozen R2 implementation:
commit = f1d69165c6d1e799d9474db23166cb665880576f
tree = 5842046d6bf9d4865566dad28a3fec5b22235f41

Owner authorization:
max_wall_seconds = 3600
spending_limit_krw = 4000
native_admission_allowed = true

Known host:
64 vCPU
128 GB RAM
CB1 100 GB /dev/vda
preferred workers = 60

control branch를 fetch한 뒤 아래 authoritative handoff를 읽고 그대로 실행해:
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_NCP_RUN_HANDOFF_KO.md

중요:
- scientific runner는 반드시 frozen R2 implementation commit/tree의 detached worktree에서 실행해.
- RUN_AUTHORIZATION_20260928_R2.json은 최신 control branch에서 외부 파일로 materialize해.
- /root/.local/state/bass_f1_r2 workspace를 사용해.
- 별도 /data volume을 만들지 마.
- external timeout으로 죽이지 마. runner의 3600s durable timeout을 사용해.
- precompute 동안 15초마다 child process count/CPU/RSS/MemAvailable/resource progress를 RESOURCE_SAMPLES.tsv에 기록해.
- 정상 precompute에서는 workers=60이고 수십 개 worker가 활성화되어야 해.
- timeout/interrupt에도 operator_tasks와 PARTIAL_TASK_SUMMARY/RETURN_REPORT를 보존해.
- operator task cache를 ZIP으로 묶어 evidence에 포함해.
- 실행은 정확히 1회. 자동 retry/resume 금지.
- PASS/FAIL 모두 execution_evidence/F1_R2/<run_id>/에 non-force push해.
- evidence 게시 후 F2/F3를 시작하지 마.

완료 시 F1_R2_NCP_RUN_PUBLISHED 블록과 게시 경로를 반환해.