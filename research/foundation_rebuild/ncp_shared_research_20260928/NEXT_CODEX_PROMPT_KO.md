# R3 continuation: cache-only reuse and metric audit

이 프롬프트는 bass_cr Codex 세션 하나에만 전달한다. 역할은 R3_POSTPASS_CACHE_REUSE_AND_METRIC_AUDIT다. 현재 세 세션은 사용자 보고상 유휴다. 시작 시 read-only process 확인은 수행하되 유휴 보고를 새 유료 계산 승인으로 해석하지 않는다.

Repository: cosmosapjw-quantum/bass_cr
Research/control branch: research/ncp-shared-r3-20260928
Required admitted evidence ancestor: 820b3e0a6da9f7a8c8ece8fcbd3afcf3fa9a6dc3
Historical R2 executable: f1d69165c6d1e799d9474db23166cb665880576f
Historical R2 tree: 5842046d6bf9d4865566dad28a3fec5b22235f41
Publication receipt와 현재 대화가 지정한 exact control HEAD/tree를 먼저 확인한다. 움직이는 branch name만으로 source identity를 정하지 않는다.

## 목표와 실행 경계

R2는 이미 F1_ENGINE_ADMISSION_PASS, 297/297 persisted, 1817.893839127999s다. F1을 다시 실행하지 않는다. 이번에 허용하는 것은 read-only inventory, 저장된 evidence/cache 검증, additive cache adapter 구현, synthetic 및 cache-only focused tests, 문서화, 별도 branch non-force push와 create-only 이중백업이다.

금지: 새 BASS native evaluator/공간적분, 새 engine compile, C++ scientific 실행, F0/F1/R2 재실행, cloud benchmark, 이전 3600s/4000KRW 승인 재사용, F2/F3 자동 실행, tolerance/대표점/기저/physical convention 변경, capture 또는 production 승격, 다른 repo 수정, main merge/force push, 원 checkout reset/clean/stash, 다른 세션 process kill/migrate, cgroup/systemd/mount/VM 변경.

## 1. 읽고 identity를 고정한다

현재 repo remote/HEAD/tree/status, 자기 PID+start identity와 descendants를 기록한다. 원 checkout은 변경하지 않고 별도 worktree 또는 사용자가 이미 만든 깨끗한 R3 worktree를 사용한다. 새 worktree와 R3 branch non-force push는 이 작업 범위에 포함된다. 기존 worktree 경로가 존재하면 삭제하지 말고 identity와 clean 상태를 확인한다.

읽을 파일:
- AGENTS.md; docs/READBACK_POLICY.md
- research/foundation_rebuild/ncp_shared_research_20260928/FOLLOWUP_RESEARCH_KO.md
- 같은 경로 MATHEMATICAL_SUPPLEMENT_KO.md; CURRENT_STATE.json; SOURCE_REGISTER_R3.json
- ncloud_c64g3_20260928/F0_DURABLE_CLOSURE.json
- ncloud_c64g3_20260928/execution_evidence/F1_R2/20260928T101921Z/{EVIDENCE_MANIFEST.json,RETURN_REPORT.json,PARTIAL_TASK_SUMMARY.json,ENGINE_IDENTITY.json,METRIC_CONNECTION_PARITY.json}
- ncloud_f1_r2_parallel_admission_20260928/runtime_r2/{task_plan.py,task_store.py,cache_evaluator.py}
- ncloud_f1_engine_admission_20260928/runtime/native/cloud_engine.py

과거 SOURCE_MANIFEST의 범위와 현재 control sidecar manifest를 혼동하지 않는다. 완료된 예전 18/32/48/30/16 test suite를 반복하지 않는다.

## 2. 완료된 R2 cache를 exact input으로 읽는다

Repo input:
research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1_R2/20260928T101921Z/OPERATOR_TASK_CACHE_20260928T101921Z.zip

Expected bytes: 3608658
Expected SHA256: 6f7929f553a10d7ee163af6831e46c86e4fcec2d0fc8b9f75aacd99110d318ef

ZIP path traversal/duplicate/CRC, TASK_CONTEXT, 297 receipt/payload pairs, payload SHA, dtype/shape/nonfinite, exact time/q/h를 검사한다. 예상 member 이름이나 개수 구조는 실제 archive에서 읽고 검증한다. manifest가 있는데 통째로 무시하지 않는다. cache-only 작업은 native callback이 호출되면 즉시 실패하는 sentinel을 사용한다. missing cache는 hard fail이며 계산 fallback이 아니다.

## 3. additive import bridge를 구현한다

신규 코드는 ncp_shared_research_20260928/runtime_r3/ 아래에 둔다. 원 F1/R2 scientific source와 기존 cache files는 수정하지 않는다.

- provenance identity: 원 receipt/context/taskID/source path를 그대로 보존한다.
- numerical identity: source/model/basis/trajectory/exact time/q/h/sector/dtype/ABI/numeric runtime/정책 및 승인된 binary identity를 명시적으로 묶는다.
- execution identity: output path, PID, worker count, budget, scheduling metadata는 별도 receipt다.
- 기존 engine identity를 in-place rewrite하지 않는다. 기존 key와 새 consumer 사이의 explicit IMPORT_BRIDGE.json을 만든다.
- output path만 다른 fresh output으로 array/receipt를 그대로 읽을 수 있는지 검증한다. 새 binary를 임의로 동등 판정하지 않는다.
- source, basis, parameter, binary, numeric runtime, policy가 바뀌는 negative test는 거절돼야 한다.

수치 array bytes를 바꾸지 않는 adapter가 acceptance다. 코드 수정 전에 focused negative tests를 먼저 두고, import/setup error가 아닌 의미 있는 assertion RED를 보존한 뒤 구현한다.

## 4. 저장 배열로만 actual-metric diagnostic을 만든다

기존 metric sentinel 다섯 개의 exact center/plus/minus와 각 selected q/h를 사용한다. Sdot_FD=[Splus-Sminus]/(2 eps_t), R=Sdot_FD-D-D†, S=C†C, W=C^-† R C^-1을 계산한다. Cholesky와 triangular solves를 사용하되 정의상 방향을 확인한다.

H의 Hermiticity를 별도 확인한다. 비Hermitian H이면 R_total에 (i/hbar)(H†-H)가 추가된다. 기존 atomic-unit convention과 physical-time 표현을 구분한다.

출력에는 raw Frobenius, 기존 relative metric, whitened Hermitian spectral norm, eps, S minimum eigenvalue/conditioning, finite-difference limitations를 남긴다. 기존 gate를 바꾸지 않는다. 보간된 reported dotS와 represented S(t)의 actual derivative를 같은 이름으로 덮어쓰지 않는다.

Wolfram/NumPy toy identity test는 definition audit다. NCP 전체 trajectory 증명으로 표현하지 않는다. 단일 eps/다섯 점으로 integral eta나 continuous supremum bound를 만들지 않는다. 불가한 항목은 NOT_CERTIFIED다.

## 5. 중요한 다음 물리 gate를 준비한다

F0 M4 same-input qualification과 R2 engine admission을 재활용한 finite-basis observable/pilot의 입력·출력 계약 초안을 작성한다. 실제 capture 계산은 열지 않는다. CF4나 전체 worker sweep를 무조건 prerequisite로 추가하지 않는다. radial/angular convergence, asymptotic extraction, all-bound, b-grid를 생략하지 않는다.

lazy metric prefix와 same-center factoring은 다음 새 operator workload의 후보로 유지한다. 이미 끝난297task를201task로 다시 계산해 성능을 주장하지 않는다. exact symmetry even14는 별도 scope/admission 전까지 적용하지 않는다.

## 6. 자원과 다른 repo

현재는 exclusive heavy epoch를 제안할 수 있지만 heavy launch는 하지 않는다. 세 repo에서 각각 나온 18/18/20,16/16/16,32/16/12는 proposal들이며 활성 배분이 아니다. 공유 broker 전체를 먼저 만드는 메타루프로 확장하지 않는다.

HH의 fixed pair histogram/actual metric negative result, HE의 trace-factorization/certificate identity 원칙만 가져온다. 다른 물리계의 행렬/에너지/상태를 CR에 import하지 않는다. HH M3B 재실행 및 HE source-identity repair는 해당 repo 담당자의 별도 작업이다.

## 7. 완료와 게시

이번에 추가한 focused tests와 cache-only checks만 실행한다. original suites 또는 native admission은 재실행하지 않는다. 모든 scientific native invocation=0이어야 한다.

산출물:
R3_RETURN.json, IMPORT_BRIDGE.json, CACHE_AUDIT.json, METRIC_DIAGNOSTICS.json,
NEXT_PHYSICS_GATE_DRAFT.md, 새 test receipts, 변경 manifest, sanitized host/inventory receipt.

자기 R3 branch에 non-force push하고 remote ref/tree 및 intended-path diff를 확인한다. 결과 ZIP은 기존 Drive/Dropbox 대상에 create-only로 저장한다. 둘 중 하나라도 실패하면 이중백업 완료라 하지 않는다. checkpoint는 R2 metadata/manifest cross-check, content/authority import는 필요한 R3 범위로 검증한다. provider ACK와 restore verification을 구분한다.

최종 상태:
R3_CACHE_REUSE_AND_METRIC_AUDIT_COMPLETE 또는 R3_BLOCKED.
원 F1_ENGINE_ADMISSION_PASS는 과거 evidence로 보존하며 새 production PASS로 바꾸지 않는다.

최종 반환: actual HEAD/tree, imported source identities, cache counts/hashes, new tests, new native evaluations=0, metric diagnostics scope, first blocker, exact next physics gate, remote publication receipt, 두 provider의 file IDs/size/hash/verification tier.
