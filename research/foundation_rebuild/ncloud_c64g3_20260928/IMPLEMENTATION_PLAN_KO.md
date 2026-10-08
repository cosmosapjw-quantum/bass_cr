# BASS c64-g3 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 TP2D evidence를 재사용하고 새 공간적분만 c64-g3의 독립 시간점 pool로 옮긴다.

**Architecture:** F0 cache-only M4를 먼저 실행한다. 추가 시점이 필요할 때에만
새 Intel engine admission(F1), 자원·task pool calibration(F2), 고정-grid CF4(F3)를 연다.
전체 설계 승인과 각 단계의 구현 완료·실행 승인·과학 PASS는 별개다.

**Tech Stack:** 기존 Python/NumPy/SciPy 및 C++ analytic moments, spawn processes,
POSIX SSD task store, Git provenance. MPI/Kubernetes/multi-VM/GPU는 추가하지 않는다.

## Global Constraints

원 설계의 SSOT는 ARTIFACTS.json에 고정된
BASS_NCLOUD_C64G3_REDESIGN_20260928.zip의 REDESIGN_KO.md,
MIGRATION_RUNBOOK_KO.md, IMPLEMENTATION_PLAN_KO.md다.
이 문서는 그 F0–F3 구조를 저장소 경로·인계 역할에 매핑한 실행계획이다.
동일 과학 정의를 새로 유도하거나 원 문서의 권고를 실제 cloud 측정으로 승격하지 않는다.
불일치는 자동 조정하지 않고 SPEC_CONFLICT로 보존한다.

Frozen scientific gates:
- F0 historical N384 replay metric distance <=1e-10.
- candidate/reference distance <=1e-6; adjacent refinement <=1e-6; norm drift <=1e-8.
- runtime raw cross convergence <=1e-9.
- new-engine parity: rtol=1e-11, atol=1e-12; q/h drift => POLICY_SELECTION_DRIFT.
- 원 source/basis/GRANT/library identity와 원 TEMPORAL_REFINEMENT_UNRESOLVED를 보존한다.
- no nearby-time substitution, no automatic threshold/ladder/method changes.
- capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO,
  original_capture_gap_resolved=false, continuous_global_supremum_bound=false.

## 현재 역할과 권한

이번 Codex start handoff는 F0 고정 실행·검사·반환만 활성화한다.
F1–F3의 설계는 승인됐지만 이 커밋에 runtime 구현이 없고,
Codex가 F0 실패를 계기로 자동 코딩·수리·native launch로 전환하지 않는다.
이후 구현용 인계는 아래 파일·테스트·판정 계약을 사용한다.
main merge, force push, 사용자 변경 정리, cloud 자원 생성/삭제는 어느 단계에도 포함하지 않는다.

## 현재 상태

| 단계 | 준비된 것 | 아직 확인되지 않은 것 |
|---|---|---|
| F0 | 원 패키지의 cloud_preflight.py, run_cache.sh, TP2E cache-only entrypoint | 실제 host/input admission, 실제 BASS M4 |
| F1 | 아래 build/admission 명세 | 새 Intel adapter와 실제 parity |
| F2 | 아래 pool/calibration 명세 | 구현, RSS, 실제 16/32/48/60 scaling |
| F3 | 아래 CF4 명세 | native runner, 실제 temporal qualification |

## F0. 원본 이식과 cache-only 비교

**Observed files in approved archives:** cloud_preflight.py, run_cache.sh,
TP2E run_cached_m4.py, tp2e_archive.py, tp2e_core.py, GRANT.json.
Git 문서만 받은 상태에서 이 파일들이 checkout 안에 있다고 가정하지 않는다.

**Consumes:** 원 TP2D 전체 RETURN ZIP, 원 설계 ZIP(원 TP2E ZIP 포함),
실제 작업 호스트 및 승인된 Python 환경. **Produces:** HOST receipt,
원 entrypoint의 RETURN_REPORT/MANIFEST/RETURN ZIP, environment receipt.

- [ ] 실행 workspace의 branch/HEAD/tree/status와 active project process를 읽기만 해서 기록한다.
      계획은 startup의 exact PLAN_COMMIT에서 읽는다. source checkout과 계획 commit을 혼동하지 않는다.
- [ ] ARTIFACTS.json의 hash로 입력을 검증하고 archive member path를 확인한다.
      기존 code/env/output에 덮어쓰지 않고 새 전용 경로를 사용한다.
- [ ] 원 Python minor와 NumPy/SciPy의 기록을 확인한다. 없다면 이미 승인된 venv와의 차이를
      명시하고, 검증할 환경이 준비되지 않은 경우 ENVIRONMENT_BLOCKED로 중단한다.
      이 인계에서는 설치·업그레이드로 자동 수리하지 않는다.
- [ ] 원 cloud_preflight.py로 HOST/input receipt를 만든다.
      RSS 미측정에 따른 safe_worker_ceiling=null은 F0의 실패 사유가 아니지만 native scaling은 막는다.
- [ ] 원 run_cache.sh를 통해 run_cached_m4.py를 한 번 실행한다.
      worker/BLAS=1, 새로운 공간적분=0, reference 재적분=false.
      새로운 CPU/OS/BLAS 환경의 첫 admission은 원 TP2E suite를 그대로 한 번 실행한다.
- [ ] 성공/실패 모두 원 RETURN status와 first_failure를 그대로 반환한다.
      성공하면 같은 질문에 대한 추가 native run 없이 STOP_F0_COMPLETE.
      실패면 STOP_F0_BLOCKED 또는 STOP_F0_SCIENTIFIC_UNRESOLVED. 자동 재시도하지 않는다.

실제 명령과 return 요약은 CODEX_HANDOFF_KO.md에 있다. output 충돌은 rc=3 또는
원 argparse error이며, 원 파일을 지우지 않는다. 상태를 문서의 예상값으로 바꾸지 않는다.

## F1. 새 Intel native build와 engine admission

**Proposed files, not present:** runtime/native/cloud_engine.py,
runtime/native/engine_admission.py, runtime/tests/test_engine_admission.py.

**Interface:** engine_admission(source_root, historical_archive, new_build_dir,
frozen_policy, out_dir) -> ENGINE_ADMISSION.json 및 ENGINE_IDENTITY.json.

- [ ] source tamper, basis 내용·순서 변조, 누락 build receipt를 거절하는 focused test를 먼저 작성한다.
      로컬 고정 fixture에서 의미 있는 assertion RED를 보존하고 import/setup 실패와 구분한다.
- [ ] pinned C++ source와 원 BASIS coefficient bytes를 사용한다. atomic_bank를 다시 풀어
      같은 기저라고 가정하지 않는다. 기존 GRANT의 library SHA를 새 빌드로 바꾸지 않는다.
- [ ] 첫 build lane은 승인 설계의 generic x86-64/fast-math 금지 권고를 build contract에 고정한다.
      compiler argv/version, source closure, lib SHA, CPU/ISA/libc, Python/numeric/BLAS를 기록한다.
- [ ] frozen representative 중앙·양쪽 tail·q/h 전이 points에서 독립 ladder를 수행한다.
      원 selected S/H/D와 rtol=1e-11, atol=1e-12; 양방향 D, Hermiticity, metric positivity,
      기존 connection sentinel을 검사한다. q/h 변경은 POLICY_SELECTION_DRIFT다.
- [ ] 같은 focused tests의 GREEN과 실제 cross-platform 실행 여부를 분리해 기록한다.
      과거 provider의 library check를 no-op으로 만들지 않는다.

Compile/runtime failure, input identity failure, numerical parity failure를 다른 status로 남긴다.
실제 representative point 집합과 runtime budget은 실행 전 evidence-bound contract로 고정한다.

## F2. exact-time pool과 calibration

**Proposed files:** runtime/native/task_plan.py, runtime/native/worker_pool.py,
runtime/native/task_store.py, runtime/calibrate_cloud.py, runtime/tests/test_cloud_pool.py.

**Interface:** qualify_times(times_hex, engine_admission, basis_payload, policy,
resource_plan, run_budget, out_dir) -> TASK_MANIFEST.json.

- [ ] serial/spawn parity와 out-of-order completion 후 chronological replay를 검증하는 RED를 작성한다.
- [ ] spawn을 명시한다. 하나의 worker가 한 시간의 전체 finite ladder를 순서대로 평가한다.
      worker별 같은 시간의 TT/PP memo만 허용하며 native 합산순서는 바꾸지 않는다.
- [ ] data identity와 resource/log identity를 분리한다. 원 context/qid를 재작성하지 않고
      archive SHA, old qid, selected array SHA, new consumer를 import receipt로 연결한다.
- [ ] parent가 유일한 manifest writer다. task의 planned/submitted/running/computed/
      persisted/validated/failed를 구분하고 저장 전 완료 ACK를 금지한다.
- [ ] 실제 affinity/quota/cgroup/memory를 읽는다. worker RSS가 없거나 cgroup이 불명확하면
      scaling을 자동 승인하지 않는다. 중앙 고비용 pilot의 RSS를 사용한다.
      M_budget=min(96GiB,0.75*M_eff,max(0,A_eff-8GiB)),
      W_memory=floor(max(0,M_budget-4GiB)/(1.5*R_peak)).
      W_safe=min(CPU allowance,W_memory,remaining tasks). c64에서는 CPU 4개를 제어 여유로 둔다.
- [ ] 동일 192개 distinct exact-time task를 cold store에서 비교한다.
      자원 gate를 통과한 16/32/48/60 profile만 측정하고 좋은 두 후보를 반복한다.
      최고 median throughput 97% 이내이면 작은 worker를 고르는 권고를 calibration contract에 고정한다.
- [ ] wall/p50/p95, raw evals, RSS, CPU user/system/steal, iowait, ctx switches,
      fsync 비용과 q/h/parity를 기록한다. warm hit나 중복 task는 throughput에서 분리한다.
- [ ] worker exception, SIGINT, disk-full, fsync failure, partial/tampered cache,
      deadline과 in-flight grace를 focused failure injection으로 검증한다.
      real Git fixture 또는 완전히 격리된 Git seam을 사용한다. fake head를 real ancestry에 보내지 않는다.

budget null이면 native launch를 허용하지 않는다. deadline 이후 in-flight/grace 비용도 기록하며
zero-overshoot를 보장하지 않는다. scheduler 코드가 아직 없으므로 실행 명령을 발명하지 않는다.

## F3. 고차 temporal 실험과 partial-result 보고

**Proposed files:** runtime/run_cloud_transport.py, runtime/native/transport_reducer.py,
runtime/native/return_report.py, runtime/tests/test_cloud_transport.py.

**Consumes:** F1 admission, F2 resource profile, historical reference import grant,
prospectively frozen CF4(two Gauss nodes) 및 [24,48,96,192], explicit wall/cost budget.

- [ ] 비가환 시간의존 exact solution에서 4차 수렴과 exponential 순서 negative control의 RED를 작성한다.
- [ ] 각 단계의 실제 Gauss time을 한 번 계산해 hex로 고정한다. 2N time tasks와 endpoints/diagnostics를
      직접 qualification한다. N24의 48개 Gauss tasks를 60개 worker보다 적다고 오류로 보지 않는다.
- [ ] 모든 required operator가 준비되면 기존 metric-frame G 정의로 시간순 전파한다.
      adaptive DOP853 미래 stage를 사전 분배하거나 최종 state들을 임의 평균하지 않는다.
- [ ] historical reference는 imported_reference=true와 historical engine identity를 기록한다.
      새 reference solve 또는 연속 구간 uniform bound라고 표현하지 않는다.
- [ ] candidate/reference<=1e-6, adjacent<=1e-6, norm<=1e-8을 모두 요구한다.
      ladder 소진은 TEMPORAL_REFINEMENT_UNRESOLVED로 종료한다. threshold/method 변경은 없다.
- [ ] 실패해도 완료 reference, candidate/pair, task ledger, resource/cost를 RETURN_REPORT에 남긴다.
      requested/returned/persisted/qualified count를 나누고 missing은 NOT_EVALUATED로 표현한다.
- [ ] 신규 focused tests, import-safe subprocess CLI, cold-start 실패 주입을 검증한 뒤에만
      새 runtime CLI와 별도 실행 인계를 게시한다. 합성 PASS와 실제 cloud scientific PASS는 분리한다.

## 미해결 실행 입력과 종료 조건

SSH target, 실제 VM 준비 상태, 작업 볼륨, numeric environment provenance,
max_wall_seconds, spending_limit_krw, 원 TP2D 전체 ZIP의 현 호스트 접근성은 자동으로 채우지 않는다.
VM/설치/유료 benchmark 권한이 없으면 실행하지 않고 정확한 blocker를 반환한다.
Code/design 준비가 끝났다는 이유로 cloud 자원 생성·provider upload·main merge를 수행하지 않는다.

계획·인계 문서 게시에는 ordinary R1 selective remote identity verification을 사용한다.
원 archive restore/admission은 별도 content 검증이다. 문서만 변경된 이 커밋은
원 15/32/18 tests나 장시간 science의 신규 PASS를 주장하지 않는다.
