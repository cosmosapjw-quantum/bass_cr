# R4C hostile re-audit: code repair and N768 handoff

## 판정

Original d0293b9988d25758728120ceee3be7c7abcaa786: EXECUTION_ADMISSION_NO_GO.
Repair code 4c2c0be5171c74a52b4a6e96b04c33fa00c62481, tree 2e1a3175a7d20cf9c0218fb15f07f72d4afcb425: NON_NATIVE_CHECKS_PASSED__LIVE_ENVIRONMENT_AND_USER_AUTHORIZATION_PENDING.

완전 blind 독립 심사는 아니다. 이 대화에는 이전 결론이 노출돼 있다. CodeRabbit나 별도 독립 reviewer 실행을 주장하지 않는다. 기존 PASS를 증거로 대체하지 않고 원본 code에 실패 주입을 수행했다. 실제 native build/load/evaluation, DOP853/old rungs 재실행, N768 과학 계산은 모두 0회다.

## 재현한 실패와 수정

1. 승인 토큰 없는 Python run_cli가 execute_science stub까지 도달했다. 수정 후 exit 2, science 경계 미도달.
2. 동일 generic token으로 shell이 N768->N1536을 Python stub에 전달했다. 수정 후 shell exit 64, Python 미호출. 양 진입점 모두 N384->N768로 고정했다.
3. cr_repro/constants.py의 격리 복사본 변경이 11개 pin을 통과했다. 기존 TP2D dependency pins와 합쳐 19개로 확장하고 상수 변경을 차단했다. 기존 수치 소스는 변경하지 않았다.
4. frozen contract와 native library를 대조하기 전에 MomentKernel 생성자에 도달했다. 실제 source/library/BUILD digest와 architecture를 dlopen 전에 확인하도록 수정했다. 생성자 probe는 stub이며 실제 .so 로드가 아니다.
5. 추출된 source의 metric NaN, reference norm NaN, candidate dt=123이 각각 허용됐다. strict JSON/유한성/shape/basis/dt/query identity 검사로 세 실패를 차단했다. 이는 원 exact-hash ZIP이 손상됐다는 뜻이 아니다.
6. 기존 승인 token에는 새 wall budget과 durable one-shot 소비가 없었다. 명시적 새 wall budget, account-local exclusive authorization ID, timeout supervisor, raw attempt-before-call ledger를 추가했다. 실패한 raw call도 카운트한다.

원본 safety assertion 7개 실패, 수정본 동일 assertion 0개 실패. 추가 JSON exponent overflow 및 bytecode-write RED도 보존 후 수정. 최종 focused suite 31 passed in 1.31s, failures/errors/skips=0. bash -n, diff --check, actual historical archive preflight 통과. 테스트한 6개 변경 파일 Git blob SHA가 remote 6/6 일치한다.

검증은 ae225119 복원 source에 같은 repair bytes를 얹은 격리 clone에서 수행했다. local test commit e37cf607b8c7b1d223604cf20876d8c84d6d0978과 remote code commit은 서로 다르다. d029까지의 additive evidence/docs와 기존 수치 의존성은 대조했지만 전체 원격 tree의 NCP native execution을 한 것은 아니다. 실제 .so/ABI는 live NCP admission 대상이다.

## 수치 결과와 ceiling

기존 state/S_f 후처리로 N384 reference distance 2.6345608772779628e-6, 기존 receipt와 차이 2.606320378701482e-18을 확인했다. N768 실제 time arithmetic은 770 unique accesses, 기존 cache hit 2, 새 query time 768이다. 성공 시 store union 2047. frozen per-run query budget 2048 유지. 최대 11개 resolution으로 wrapper cap 8470 raw attempts, 두 검증된 hit를 고려한 새 raw-call 상한 8448. 시간·과금 추정이 아니다.

2차 heuristic에서 N768 d_ref 약 6.5864e-7, d_self 약 1.9762e-6이다. 후자는 frozen 1e-6을 넘으므로 한 rung 후 UNRESOLVED 가능성을 승인자가 알아야 한다. 수렴 예측은 gate가 아니다. 동일 18-channel/100 keV/u/b=2 a0/z=-12~+12 a0만 다룬다. algebraic skew 및 norm 보존은 실제 overlap derivative나 continuous bound를 증명하지 않는다.

capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO, original_capture_gap_resolved=false, continuous_global_supremum_bound=false, continuous_trajectory_error_bound=false.

## Codex handoff

역할 CLOUD_REVIEW_REPAIR_EXECUTOR. 주요 구현을 다시 작성하지 않는다. 먼저 AGENTS.md, repaired/original source와 frozen 계약을 읽고 자기 initial findings를 기록한 뒤 이 보고서와 대조한다. 추가 결함이 있으면 focused repair/tests를 수행하되 실행 code identity가 바뀌면 승인을 다시 바인딩한다. main merge/force/reset/clean/자동 stash/rebase/사용자 변경 삭제 금지.

별도 clean worktree에서 아래 EXECUTION_COMMIT을 사용한다. branch에 뒤따른 docs/receipt HEAD를 자동 실행하지 않는다.

EXECUTION_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481
EXECUTION_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425
SIDE=research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation
RESUME_BYTES=31849212
EXPECTED_RESUME_SHA256=630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35
CONTEXT=bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda
NATIVE_SOURCE_SHA256=90913155c0cfa80962d1cb00bb1b7ec0443170917c25913ac5e359979738ab30
NATIVE_LIBRARY_SHA256=966146f0ca713251f8b73999b4d89595cf1820a8c2d36f5c6290387b70c68035

준비된 Python>=3.11, NumPy2.3.5, SciPy1.17.0 및 기존 frozen BUILD.json/libmoments.so의 실제 경로를 확인한다. 자동 build/upgrade/대체 backend 금지. 로딩 전 digest/architecture를 확인하고 host ABI/동적 의존성 확인 한계를 기록한다. Python은 -I -B, 네 thread limit은 모두 1. 출력과 테스트 로그는 worktree 밖이다. 추적된 bytecode/cache를 자동 제거하지 않는다.

```bash
"$BASS_R4C_PYTHON" -I -B -m pytest -p no:cacheprovider "$SIDE/tests" -q \
  --junitxml="$RECEIPTS/focused.xml"
bash -n "$SIDE/run_r4c_preflight.sh" "$SIDE/run_r4c_science.sh"
# input/Python/expected commit variables를 먼저 export한다.
bash "$SIDE/run_r4c_preflight.sh" "$PREFLIGHT_OUT"
```

현재 NATIVE_AUTHORIZATION=PENDING_USER_APPROVAL. 이 문서 자체는 science 승인이 아니다. 사용자가 exact N384->N768 한 attempt와 새 R4C_AUTHORIZATION_ID, R4C_MAX_WALL_SECONDS, 60초 종료 grace, 새 cost scope를 승인해야 한다. 비용 상한이 필요하면 외부에서 적용 가능한 통제를 확인하며 코드가 KRW를 강제한다고 주장하지 않는다. 이전 3600초/4000원 승인은 소비됐다. 승인값을 임의로 만들지 않는다.

승인과 live admission이 모두 닫힌 경우만 실행한다:
```bash
export EXPECTED_COMMIT=4c2c0be5171c74a52b4a6e96b04c33fa00c62481
export EXPECTED_TREE=2e1a3175a7d20cf9c0218fb15f07f72d4afcb425
export EXPECTED_RESUME_SHA256=630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35
export PREVIOUS_NSTEP=384 NEXT_NSTEP=768
export ALLOW_NEW_NATIVE_R4C=YES_I_AUTHORIZE_ONE_RUNG
bash "$SIDE/run_r4c_science.sh" "$OUT"
```

실제 발견한 RESUME_ARCHIVE/ANALYTIC_BUILD/BASS_R4C_PYTHON, 승인된 R4C_AUTHORIZATION_ID/R4C_MAX_WALL_SECONDS는 위 명령 전 export해야 한다. nonce는 ~/.local/state/bass_r4c/authorizations/<ID>.json에서 exclusive 소비된다. 실패 후 삭제/재발급/다른 account-HOME-host로 우회 금지. Python 직접 호출로 shell timeout을 건너뛰지 않는다.

d_ref<=1e-6, d_self<=1e-6, reference 및 previous/current norm drift<=1e-8, operator qualification을 함께 판정한다. exit 0을 PASS로 취급하지 않는다. UNRESOLVED도 정상 연구 반환이다. 어떤 결과에도 N1536 자동 확장 금지. DOP853, N<=384, F0/F1/R2, capture/all-bound/b-grid/benchmark 재실행 금지.

첫 실패/partial data/raw attempt ledger를 보존하고 physics/numerical/implementation/environment/authorization/runtime를 분리한다. SIGKILL/OOM이면 final ZIP을 보장하지 못한다. 존재하지 않는 candidate/receipt를 생성하여 채우지 않는다. interrupted-candidate 일반 resume는 미구현이다.

review/host/approval/command-exit receipts, PREFLIGHT, EXECUTION_ADMISSION, AUTHORIZATION_CONSUMED, NATIVE_PRELOAD_CHECK, RAW_EVALUATION_LEDGER, CANDIDATE_N768, TEMPORAL_PAIR_N384_N768, PROVIDER_AUDIT, RETURN_REPORT, MANIFEST 및 실제 query payload를 반환한다. 작은 evidence만 별도 branch로 non-force 게시하고 원 NPZ는 Git에 중복 저장하지 않는다. portable ZIP과 SHA/size를 create-only 이중백업한다.

Drive folder: 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Dropbox folder: /bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS

provider credential 부재 시 우회하지 말고 실제 ZIP bytes를 ChatGPT로 전달한다. /root 경로만 반환한 것은 전송 완료가 아니다. selective R1 검증과 RESTORE_VERIFIED를 구분한다. 최종 ceiling을 유지하고 한 rung에서 종료한다.
