# N1536 adaptive successor implementation handoff

상태: N1536_ADAPTIVE_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING.
이 커밋은 비 native 실행기 준비다. N1536 operator, parity, pilot, replay는 실행하지 않았다.

## 불변 입력과 구현 경계

- 완료된 A2 ZIP SHA256: dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3.
- 이전 실행 commit/tree: 11100b35f78ec26100ea732971bb4ce0f9925719 / 05976e386c0a39591247d69c32c8cb28fa3f2a97.
- 원 context: bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda.
- 원 native source/library/BUILD hash는 successor.py에 고정하고, 각 worker는 기존 worker_runtime.initialize_worker에서 dlopen 전에 재검사한다.
- 새 N1536 경로는 run_n1536_science.sh → supervise_n1536.py → run_n1536.py다. R4F N768 실행기는 변경하지 않았다.

완료 A2 ZIP의 manifest 모든 구성원 SHA256/size/CRC와 2047 query pair의 identity, payload, ordered qualification을 확인한 후에만 재사용한다. N1536 planner는 원 run_candidate 순서의 binary64 연산으로 required 1538개, exact inherited 2개, missing 1536개, eventual union 3583개를 구성한다. active query count 1538은 frozen per-run cap 2048 이하다.

Pilot 8/16/32는 missing ID를 결정론적으로 층화하여 8/16/32개 배정한다. 56개 모두 유용한 scientific query이며 성공 pair는 canonical cache에 create-only 게시한다. 모든 stage가 성공하면 1480개가 fill에 남는다. stage throughput에는 pool 시작·종료 시간을 포함한다. 건강한 stage 중 실제 queries/sec 최대를 선택하고 동률은 적은 worker를 선택한다. 상위 stage의 시작 전 자원 거부 시 그 stage와 이후 pilot ID를 누락 작업으로 되돌리고 하위 건강한 stage로 fill한다. 계산 중 worker 또는 operator 실패는 global budget을 취소하고 부분 증거를 보존하며 중단한다.

각 stage 전에 affinity, cgroup CPU quota, /proc/meminfo와 cgroup RAM, 다른 BASS 프로세스의 CPU 중복을 검사한다. worker는 spawn이며 각 1 GiB 주소 공간과 1 numerical thread를 유지한다. global raw reservation은 기존 durable GlobalBudget을 공유한다. 새 rung useful 최대는 1536×11=16896 raw이며 별도 parity 22 raw는 이 구현의 자동 실행 범위에 포함하지 않았다.

필수 1538 pair가 모두 검증된 후에만 원래 initial state에서 run_candidate(...,1536)를 strict cache-only provider로 수행한다. native operator call이 0이 아니면 차단한다. candidate와 pair 증거를 먼저 저장한 다음 frozen temporal screens, reference norm, operator qualification, triangle consistency를 분류한다. N1536의 dual distance PASS는 유효한 결과다. production은 계속 HOLD다.

## 비 native 검증

준비 worktree에서 실행:

1. /root/.local/state/bass_f0/env/tp2e_f0_20260928T045058Z/bin/python -B -m pytest -q -p no:cacheprovider research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/tests research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/tests → 60 passed, 0 failed, 0 skipped.
2. 실제 A2 ZIP에 대해 successor.validate_predecessor와 plan_n1536/required_missing 비 native preflight → canonical pairs 2047, required 1538, inherited exact hits 2, missing 1536, union 3583.
3. serial.verify_pinned_dependencies() → 19/19 SHA 일치. check_native_build on frozen F1 engine → source 90913155c0cfa80962d1cb00bb1b7ec0443170917c25913ac5e359979738ab30, library 966146f0ca713251f8b73999b4d89595cf1820a8c2d36f5c6290387b70c68035, BUILD 180a74d3acf2588d3b8c7944effe4709a4fd4f6241cb4df736cd8f0c94430af1, native_loaded_by_check=false.
4. launcher→parser identity trap은 잘못된 commit을 주입하여 native load 및 nonce 소비 전에 거부됨을 확인한다. 이것은 synthetic test이며 native parity가 아니다.

## 후속 승인

make_preparation_package.py는 clean exact commit에서 실제 predecessor ZIP과 frozen native BUILD를 검증한 뒤 SOURCE_PINS.json, query plan, useful pilot plan, SHA 및 미래 승인 템플릿을 기계적으로 생성한다. 템플릿의 CPU 목록, fresh authorization ID, deadline/wall, grace, cost는 사용자 승인 전까지 placeholder다. 이 준비 단계는 native 권한을 부여하지 않는다.

추후 승인 없이 launcher를 실행하지 않는다. 새 승인에는 exact commit/tree, 입력 ZIP/query-plan/pilot-plan hash, 8/16/32 stage와 최대32, CPU/RAM, global raw cap, wall/deadline, cost, 필요 시 별도 parity scope가 들어가야 한다.

N3072, 새 nonce/retry, threshold 변경, reference 재실행, capture, all-bound, b-grid는 범위 밖이다.
