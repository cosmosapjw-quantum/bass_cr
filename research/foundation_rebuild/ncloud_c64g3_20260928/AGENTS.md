# Scoped instructions: ncloud_c64g3_20260928

상위 AGENTS.md와 docs/READBACK_POLICY.md를 함께 적용한다.
이 파일은 전체 저장소의 기존 과학/권한 정책을 바꾸지 않는다.

## Authority and scope

- ARTIFACTS.json의 archive hash와 실행 시 전달된 exact plan commit을 사용한다.
- 원 source commit c954d68fdc86527453765a563b3a025351163ed9와 plan commit은 서로 다르다.
  source checkout이 그대로여도 git show PLAN_COMMIT:path로 계획을 읽을 수 있다.
- 승인된 재설계의 처음 실행은 F0 only. Codex의 이번 역할은 고정 패키지 실행과 evidence 반환이다.
- F1–F3 파일/CLI는 proposed다. 구현돼 있거나 cloud admission을 통과했다고 주장하지 않는다.
- budget null, worker RSS 미측정, engine 미승인 상태에서는 native launch를 금지한다.

## Preserve and stop

- 원 결과·source·basis·library·GRANT·context/qid는 불변이다.
- reset --hard, git clean, 자동 stash/rebase/merge, 자동 새 worktree, .codex/ staging을 하지 않는다.
- 실행 중인 checkout은 전환하지 않는다. 사용자 수정과 untracked 파일을 보존한다.
- F0 실패를 자동 수정·재시도하지 않는다. 시험 count 감소, skip 추가, tolerance 완화,
  가까운 time 대체, 새 reference solve, fallback spatial evaluation을 금지한다.
- VM 생성/정지/반납, disk format, credential 열람·게시, 무단 install/upgrade를 하지 않는다.
- source code를 바꾸지 않고 생긴 반환 receipt는 승인된 output 경로에 create-only로 기록한다.
  이 F0 handoff만으로 결과의 GitHub push 또는 provider upload 권한을 새로 부여하지 않는다.

## Evidence and claims

- F0는 공간적분 0회, reference reintegration=false, worker 1, BLAS/OpenMP 1.
- 변경 없는 기존 장시간 suite를 재실행하지 않는다. 새 환경 첫 admission에서는
  원 TP2E entrypoint의 해당 suite를 한 번 실행하며, 임의로 재실행하거나 우회하지 않는다.
- user-provided, derived, executed, provider-acknowledged를 분리한다.
- 기본 원격 검증은 R1 selective metadata다. 원본 archive admission과 충돌·복구는 별도 content 검증이다.
  UPLOAD_VERIFIED와 RESTORE_VERIFIED를 혼동하지 않는다.
- capture_execution_allowed=false; production_admission=HOLD; all_bound=OPEN;
  b_grid=NO_GO; original_capture_gap_resolved=false; continuous_global_supremum_bound=false.
