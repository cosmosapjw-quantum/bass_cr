F1-R2 parallel native admission implementation을 시작해줘.

Repository:
cosmosapjw-quantum/bass_cr

Branch:
research/fnd-ncloud-f1-r2-parallel-admission-20260928

현재 source checkout은 변경하지 말고 별도 detached worktree에서만 구현해.
이번 세션은 R2 code/test/push까지만 승인한다. 실제 NCP scientific run은 금지한다.

authoritative handoff:
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/R2_CODEX_HANDOFF_KO.md

핵심 목적:
기존 F1 scientific reducer/threshold/query set을 그대로 유지하고,
expensive operator evaluation만 exact-task process pool로 병렬화한다.

Known server:
64 vCPU
128 GB RAM
Intel Xeon Gold 5220
CB1 100 GB

기존 timeout:
run_id 20260928T064313Z
exit 124
7200 s
scientific status NOT_REPORTED
마지막 phase engine_loaded
htop에서 expensive phase가 사실상 1 vCPU만 사용

R2 preferred workers:
60
(64 affinity - 4 reserved)

대표 parity:
15 queries × 11 resolutions = 165 independent expensive tasks.

metric sentinels:
기존 5 z × center/±epsilon exact times의 full ladder를 precompute하고,
exact task identity로 중복 제거해.

반드시:
- spawn process pool
- each worker BLAS/OpenMP threads=1
- worker initializer에서 engine/basis/evaluator 1회 load
- parent only durable task-store writer
- each completed task 즉시 hash-valid NPZ+JSON persist
- exact-context resume to fresh output
- no fuzzy time reuse
- cache miss has NO native fallback
- existing pinned run_admission()을 cache evaluator 위에서 재사용
- serial-vs-parallel synthetic equivalence tests
- timeout/interrupt partial result preservation

구현 위치:
research/foundation_rebuild/ncloud_f1_r2_parallel_admission_20260928/runtime_r2/

기존 scientific source 파일은 수정하지 마.

old authorization은 R2에서 반드시 거절해.
새 R2 authorization schema/firewall만 구현하고 실제 authorization 파일은 만들지 마.

R2-new tests만 실행해.
TP2D 18 / TP2E 32 / old F1 48 tests는 재실행하지 마.

허용:
worktree 생성
R2 focused tests
py_compile
CLI --help
bounded commits
R2 branch non-force push

금지:
actual R2 native science run
F1_ENGINE_ADMISSION_PASS 주장
RUN_AUTHORIZATION 생성
threshold 변경
representative set 변경
frozen ladder 변경
F2/F3
main merge
force push
reset/clean

완료 상태:
F1_R2_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN
또는
F1_R2_IMPLEMENTATION_BLOCKED

R2_RETURN_CONTRACT.json에 맞춰 최종 evidence를 반환하고,
remote HEAD/tree 및 새 파일 경로를 전부 출력해.
