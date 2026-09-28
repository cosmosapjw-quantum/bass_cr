# R4C single-rung temporal continuation handoff

상태: **IMPLEMENTATION_READY__NATIVE_NOT_EXECUTED**

목적은 기존 TP2D의 `TEMPORAL_REFINEMENT_UNRESOLVED`를 해결하기 위해, 이미 끝난 DOP853 reference·metric sentinels·N=24..384 candidate를 반복하지 않고 정확히 한 개의 더 미세한 candidate rung만 실행하는 것이다.

핵심 구현:
- exact prior RETURN ZIP SHA-256 및 CRC 확인 후 temporary extraction
- `SCIENCE_CONTEXT` hash/context id와 frozen claim ceiling 확인
- historical query store의 모든 JSON/NPZ pair에 대해 context/query/payload hash 및 `RUNTIME_QUERY_QUALIFIED` 확인
- pinned numerical dependencies 11개 byte SHA-256 확인
- reference state, metric sentinels, previous candidate를 재사용하고 재계산하지 않음
- 기존 qualified query store를 fresh output으로 restore한 뒤 새 rung의 필요한 time query만 evaluation
- frozen temporal screens를 그대로 적용
- query budget은 **한 run당** 유지. N=768은 worst-case 770 unique accesses, N=1536은 1538로 각각 frozen 2048 아래다. 따라서 N=768 실패 후 N=1536이 필요하면 같은 process에서 연속 실행하지 말고, N=768 RETURN ZIP을 새 resume source로 하는 별도 fresh run으로 실행한다.

현재 historical archive에 대한 N=384→768 **preflight-only**는 실제로 통과했다.
- source archive SHA-256 `630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
- source status `TEMPORAL_REFINEMENT_UNRESOLVED`
- context id `bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda`
- validated qualified query pairs: 1279
- max stored raw-cross relative difference: `9.991816484228157e-10` under frozen `1e-9`
- N=768 single-run upper bound: 770 < 2048
- old reference rerun: false
- old candidate rung rerun: false

Focused implementation validation:
- `py_compile`: PASS
- focused pytest: 2 passed
- CLI `--help`: PASS
- real archive preflight: PASS
- native science: **NOT RUN**

Execution guard:
`run_r4c_science.sh` refuses to run unless an explicit future authorization sets
`ALLOW_NEW_NATIVE_R4C=YES_I_AUTHORIZE_ONE_RUNG`.

N=768 이후 두 frozen distance screen이 모두 PASS하면 stop한다. refinement가 FAIL하면 N=1536은 별도 authorization + 별도 fresh output + N=768 RETURN archive exact SHA로만 연다. Threshold, basis, b, z-window, reference tolerance를 바꾸지 않는다. Capture/all-bound/b-grid는 열지 않는다.
