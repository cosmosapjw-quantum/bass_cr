# Codex handoff: F1 Intel/native engine admission implementation

Role: **BASS_NCLOUD_F1_IMPLEMENTER**.

이번 세션의 목표는 **F1 admission code를 구현하고 테스트·push하는 것**이다.
실제 15-point BASS native admission scientific run은 실행하지 않는다.

## 0. branch와 current worktree 보존

Repository: `cosmosapjw-quantum/bass_cr`

Implementation branch:
`research/fnd-ncloud-f1-engine-admission-20260928`

Minimum plan commit:
`d42bf11e2bac8dbffa449c64229e81de6bb00d44`

현재 사용자의 main checkout을 그대로 보존한다.

```bash
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" status --short
git -C "$REPO" rev-parse HEAD
git -C "$REPO" rev-parse 'HEAD^{tree}'
git -C "$REPO" branch --show-current || true

F1_BRANCH='research/fnd-ncloud-f1-engine-admission-20260928'
git -C "$REPO" fetch origin "refs/heads/$F1_BRANCH:refs/remotes/origin/$F1_BRANCH"
F1_REF="refs/remotes/origin/$F1_BRANCH"

git -C "$REPO" merge-base --is-ancestor 'd42bf11e2bac8dbffa449c64229e81de6bb00d44' "$F1_REF" || {
  echo F1_PLAN_COMMIT_MISSING
  exit 3
}
```

이번 F1 구현에 한해 별도 detached worktree 생성은 명시적으로 허용한다.

```bash
F1_WORKTREE="${BASS_F1_WORKTREE:-$HOME/.local/state/bass_codex/f1_engine_admission_20260928}"
test ! -e "$F1_WORKTREE" || {
  echo "F1_WORKTREE_ALREADY_EXISTS: $F1_WORKTREE"
  exit 3
}
mkdir -p "$(dirname "$F1_WORKTREE")"
git -C "$REPO" worktree add --detach "$F1_WORKTREE" "$F1_REF"
cd "$F1_WORKTREE"
```

기존 checkout에서 reset/clean/stash/rebase/branch switch를 하지 않는다.
F1 worktree도 사용자 파일을 자동 삭제하지 않는다.

## 1. authoritative 문서

다음 순서로 읽는다.

```text
AGENTS.md
docs/READBACK_POLICY.md
research/foundation_rebuild/ncloud_c64g3_20260928/AGENTS.md
research/foundation_rebuild/ncloud_c64g3_20260928/F0_DURABLE_CLOSURE.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/EVIDENCE_MANIFEST.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/RETURN_REPORT.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/F0_RETURN_HANDOFF.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_CONTRACT.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_REPRESENTATIVE_QUERIES.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/SOURCE_PINS.json
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_IMPLEMENTATION_PLAN_KO.md
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_RETURN_CONTRACT.json
```

충돌 시 F1_CONTRACT와 이 handoff가 F1 구현 범위에 대해 우선한다.
scientific source semantics와 historical evidence는 변경하지 않는다.

## 2. Phase A: durable F0 evidence verify

F0 artifacts는 이미 이 branch에 게시되어 있다. host path에서 다시 import하거나 동일 파일을
중복 commit하지 않는다.

Authoritative evidence:

```text
research/foundation_rebuild/ncloud_c64g3_20260928/F0_DURABLE_CLOSURE.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/EVIDENCE_MANIFEST.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/RETURN_REPORT.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/F0_RETURN_HANDOFF.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/ENVIRONMENT_RECEIPT.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/HOST_F0_20260928T045058Z.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/SANITIZATION.json
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/tp2e_cache_20260928T045058Z_RETURN.zip
```

검사:

- `F0_DURABLE_CLOSURE.status == F0_DURABLE_CLOSED`.
- scientific status는 `TP2E_CACHE_ONLY_M4_COMPARISON_PASS`.
- handoff status는 `STOP_F0_COMPLETE`.
- fresh tests 32/32, failure/error/skip 0.
- historical N384 replay metric distance `2.713539056469168e-16 <= 1e-10`.
- M4 selected N96.
- new spatial operator evaluations = 0.
- reference_reintegrated = false.
- original TP2D `TEMPORAL_REFINEMENT_UNRESOLVED` 보존.
- claim ceiling unchanged.

publication tier는 R1이며 RETURN ZIP remote full-redownload restore verification은 수행하지 않았다.
이를 `RESTORE_VERIFIED`로 승격하지 않는다.

이 검사가 실패하면 `F1_IMPLEMENTATION_BLOCKED`로 중단한다. F0를 재실행하거나
host path에서 다른 evidence를 자동 탐색하지 않는다.

## 3. TDD 구현

구현 위치는 오직:

```text
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/runtime/
```

신규 파일:

```text
runtime/native/archive_evidence.py
runtime/native/cloud_engine.py
runtime/native/engine_admission.py
runtime/run_f1_engine_admission.py
runtime/tests/test_archive_evidence.py
runtime/tests/test_cloud_engine.py
runtime/tests/test_engine_admission.py
runtime/tests/test_runner_contract.py
```

### RED 먼저

최소한 다음 failure를 focused tests로 먼저 만든다.

- archive SHA mismatch
- zip duplicate/path traversal/missing BASIS/query
- BASIS byte tamper
- representative query JSON/NPZ hash mismatch
- query time/resolution drift
- source SHA mismatch
- forbidden compiler flag
- compiler nonzero/missing library
- engine identity receipt tamper
- policy selection drift
- raw cross parity fail
- full S/H/D parity fail
- metric connection fail
- run authorization missing/invalid
- output path collision
- failure before scientific execution does not claim admission PASS

테스트 import/setup error를 RED로 세지 않는다. 의미 있는 assertion failure를 확인하고
RED receipt를 남긴 다음 최소 구현으로 GREEN을 만든다.

## 4. archive_evidence.py

요구사항:

- full TP2D archive SHA/size를 F1_CONTRACT와 비교.
- zip-slip/duplicate members 거절.
- BASIS JSON/NPZ를 exact bytes로 검증하고 `allow_pickle=False`.
- `F1_REPRESENTATIVE_QUERIES.json`의 15 query만 exact hash로 읽는다.
- historical query NPZ에서:
  - `selected__S,H,D`
  - 모든 historical attempted `qXX_hY__S_tp/S_pt/H_tp/H_pt/D_tp/D_pt`
  를 제공한다.
- nearby-time/fuzzy identity/fallback query 금지.
- basis를 atomic_bank로 재계산하지 않는다.

## 5. cloud_engine.py

builder는 dependency injection 가능한 subprocess seam을 가져야 한다.

실제 scientific build가 나중에 실행될 때 frozen command는:

```text
g++ -std=c++17 -O3 -fPIC -shared -ffp-contract=off
    -Wall -Wextra -Werror
    moment_kernel.cpp -o libmoments.so
```

추가 `-march/-mtune/-ffast-math/-Ofast/-flto` 금지.

기록:
- compiler path/version
- argv
- source SHA
- library SHA
- machine/system
- CPU model/flags
- libc
- Python/NumPy/SciPy
- BLAS
- canonical engine identity

historical BUILD.json/GRANT/library를 덮어쓰지 않는다.
new engine의 library SHA가 historical library SHA와 같아야 하는 것은 아니다.

unit tests는 fake compiler/subprocess seam을 사용해도 된다.
이번 구현 세션에서 실제 15-query BASS admission을 실행하지 않는다.

## 6. engine_admission.py

나중의 scientific runner가 사용하는 library API를 구현한다.

각 representative query에서:

1. frozen full ladder 순서로 새 engine evaluator 실행.
2. historical selected q/h와 정확히 같아야 함.
3. 다르면 `POLICY_SELECTION_DRIFT`.
4. historical이 평가한 모든 resolution raw arrays 비교.
5. selected full S/H/D 비교.
6. `np.allclose(rtol=1e-11, atol=1e-12)`.
7. relative Frobenius와 max absolute difference 기록.
8. Hermiticity, metric ratio, raw convergence screen 재검사.

metric sentinels:
z/a0 = -12,-6,0,6,12
epsilon_z = 1e-4
new residual <=1e-6.

historical metric residual과 tight allclose는 요구하지 않는다.

## 7. runner authorization firewall

`run_f1_engine_admission.py`는 실제 native science 실행 전에
외부 `RUN_AUTHORIZATION.json`을 요구하도록 구현한다.

authorization에 최소:

```json
{
  "schema": "BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1",
  "implementation_commit": "<exact later commit>",
  "implementation_tree": "<exact later tree>",
  "native_admission_allowed": true,
  "max_wall_seconds": "<positive integer>",
  "spending_limit_krw": "<nonnegative number or null>",
  "prepaid_host_approved": "<boolean>"
}
```

중 하나의 비용 조건은 명시돼야 한다:
- spending_limit_krw가 non-null, 또는
- prepaid_host_approved=true.

authorization이 없으면 build/evaluation 전에
`F1_EXECUTION_NOT_AUTHORIZED`로 종료해야 한다.

**이번 구현 세션에서는 authorization 파일을 만들지 않는다.**

## 8. 구현 검증

새 F1 tests만 실행한다. 기존 TP2D 18 tests, TP2E 32 tests, 장시간 science를 반복하지 않는다.

필수:
- new focused tests failures/errors/skips = 0
- `python -m py_compile` PASS
- runner `--help` PASS
- no real F1 scientific execution
- existing scientific source modified 0
- source manifest 작성
- generated files의 secrets scan
- final worktree status에 의도한 파일만 존재

실제 compiler를 요구하지 않는 synthetic tests로 구현을 검증한다.
호스트에 compiler가 없다는 이유만으로 implementation test를 skip하지 않도록 seam을 설계한다.

## 9. commit/push

구현이 GREEN이면 commit을 bounded unit으로 나눈다. 예:

```text
data(ncloud): import verified F0 result artifacts
test(f1): add engine admission contract tests
feat(f1): add archive evidence and engine builder
feat(f1): add parity admission engine and gated runner
docs(f1): close implementation handoff
```

detached worktree에서 push:

```bash
git push origin HEAD:refs/heads/research/fnd-ncloud-f1-engine-admission-20260928
```

force push 금지.

R1 verify:
- remote ref SHA == local final commit
- remote tree == local tree
- base `609508ea...` descendant
- changed paths가 F1 sidecar와 f0_evidence에 한정
- no deletions/modifications of historical scientific source.

## 10. 종료

`F1_RETURN_CONTRACT.json`에 맞춘 summary를 출력한다.

정상 구현 완료 + durable F0 evidence verification 완료:

```text
F1_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN
```

durable F0 evidence verification 또는 implementation blocker:

```text
F1_IMPLEMENTATION_BLOCKED
```

**F1_ENGINE_ADMISSION_PASS라고 쓰지 않는다.**

F1 scientific execution, F2, F3는 시작하지 않는다.

항상 유지:
`capture=false`,
`production=HOLD`,
`all_bound=OPEN`,
`b_grid=NO_GO`,
`original_capture_gap_resolved=false`,
`continuous_global_supremum_bound=false`.
