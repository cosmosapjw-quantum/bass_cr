# Local Codex handoff — B2 하나로 full-collision 시간 수렴률 확인

ROLE=LOCAL_CODEX_RESEARCH_IMPLEMENTER
PROJECT=BASS/CR_CHARGE_EXCHANGE
REPOSITORY=https://github.com/cosmosapjw-quantum/bass_cr
INPUT_BRANCH=cr/r3m17-production-readiness-20260923
BASE_SCIENTIFIC_HEAD=7844bc0d8122070b267ee77c75cb2c9447435155
WORK_UNIT=N1_TDL_B_DT0125_SINGLE_COLLISION_TEMPORAL_RESOLUTION
DELIVERY=REPOSITORY_NATIVE
NEW_FULL_COLLISION_BUDGET=1 (B2 only)
MAIN_MERGE=NO; FORCE_PUSH=NO; FINER_H=NO; SOFT_CORE=NO
BGRID=NO; ENERGIES_50_225=NO; PHYSICAL_RATE=NO; AOCC_LARGE_TRAJECTORY=NO

## 0. 입력과 권한

사용자가 이 연구·수정·후속 handoff를 요청했다. 이미 승인된 bounded B2를 수행하되
추가 collision 수를 늘리거나 physics/source/tolerance를 바꾸지 않는다. Git에서 코드를
취득한다. ZIP 다운로드 요구는 하지 않는다. GPT6 research/coding v4.0.0 규칙을 적용한다.

입력 branch의 현재 remote exact HEAD를 먼저 기록하고 `docs/r3m17/DELIVERY_RECEIPT.json`의
source/checkpoint identity와 비교한다. 이후 더 새로운 B2 결과가 있으면 같은 physics,
source, initial identity인지 한 번 확인한다. 이미 완료된 compatible B2를 재실행하지 않는다.
기존 저장소/사용자 변경은 보존한다. 새 worktree를 자동 생성하지 말고 현재 프로젝트 정책을
읽는다. 전용 `cr/` 후속 branch에 작업하고 main은 변경하지 않는다.

읽기 순서:
1. docs/r3m17/SCIENTIFIC_CONTRACT.md, REPORT_KO.md, FINAL_DECISION.json
2. docs/r3m17/NUMERICAL_AUDIT.md, LITERATURE_REVIEW_KO.md, EXTERNAL_CODE_REVIEW.md
3. results/R3M17/INDEPENDENT_REVIEW.json, GRID_TIME_GEOMETRY.json
4. docs/roadmap/DAG.json, ERROR_BUDGET.json
5. configs/r3m17/B2.json, scripts/r3m17_preflight.py, r3m17_temporal.py, r3m17_checkpoint_guard.py
6. scripts/r3m13_initial_state_pair.py, r3m14_collision_initial_witness.py, r3m16_coordinator.py

## 1. 불변조건과 실행 전 검사

numerical source digest:
581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b

B2는 `configs/r3m16/B1.json`에서 requested real dt만 .025→.0125로 바꾼 정확한 config다.
E=100keV/u, b=2a0, h=.20a0; τ=.00625×4800, box/start/stop/CAP/정규화/채널은 그대로다.
actual dt는 runner가 계산하며 .01249892352238994, nstep=3586이 예상값이다.
ceil(nstep/128)=29 chunks; 마지막은2 steps다. 이전15-chunk 상한을 재사용하면 안 된다.

scientific interpreter:
/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python
production runtime: Python3.12.3, NumPy2.5.3, SciPy1.18.1, CuPy14.2.0,
CUDA runtime12090, driverAPI13020, driver595.84, RTX3090 24GB.
실제 identity를 다시 기록한다. 무조건 upgrade·다른 Python·대형 CPU fallback을 하지 않는다.
GPU runtime이 다르면 compatible으로 추정하지 말고 정확한 차이와 binding 영향을 반환한다.
현재 web CPU 검증 환경은 Python3.12.14/NumPy2.3.5/SciPy1.17.0이며 생산환경 검증이 아니다.

관련 기존 R3M11–R3M16 시험과 `tests/test_r3m17_*.py`를 실제 local 환경에서 실행한다.
명령은 repo root, PYTHONPATH에 repo root, BLAS/OMP threads=1, 기존 CUDA 라이브러리
환경을 재사용한다. historical PASS 수를 새 실행 수로 재사용하지 않는다.

`r3m17_preflight.py --config configs/r3m17/B2.json --job-root <B2_ROOT> --out <new-plan.json>`
은 **계획만** 생성한다. 로컬 경로의 command plan을 새로 생성한다. Git에 저장된 web
preflight의 absolute scratch 경로를 실행하지 않는다.

R3M15 resource probe를 canonical interpreter로 먼저 실행한다. 현재 GPU 점유/FFT workspace,
최소1.5GiB headroom을 포함하는 기존 monitor를 재사용한다. probe/command timeout과
OOM은 structural/runtime failure다. 무단 CPU fallback 또는 새 collision retry를 하지 않는다.

Checkpoint 보존은 별도 디스크를 요구한다. 29 generation×1,008,000,128bytes≈29.232GB
(27.225GiB)에 live/temp/prepared/final 및 archive 여유를 더한다. B2 실행 전에 최소40GiB
자유공간을 체크하고 예상 archive가 이를 넘으면 실제 산정량으로 늘린다. same-filesystem
hardlink만 허용하며 부족하면 RESOURCE_BLOCKED를 반환한다.

## 2. 초기상태와 B2 하나 실행

기본 새 root 예:
/mnt/sn850x2t/bass_cr_r3m17_20260923/B2
이 경로가 이미 있으면 overwrite하지 않고 기존 receipt를 읽어 completed/partial/failed를
분류한다. completed면 재실행 금지; partial은 동일 sealed trajectory의 continuation만 허용.

fresh B2 preparation receipt를 원 R3M13 helper로 만든다. 기존 receipt의 dt를 고쳐서 쓰지 않는다.
`initial.npy`는 B0/B1과 정확히 동일해야 한다:
SHA256=ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa

일치하지 않으면 충돌 전에 중지한다. 바이트 불일치를 ray tolerance로 대체하지 않는다.
R3M14 v2 witness가 실제 내부 initial을 다시 확인해야 하며 수동 state 주입/receipt 완화 금지.
준비 결과와 그 실행 환경을 immutable하게 남긴다.

충돌은 기존 v2 CLI만 사용한다:
`<SCIENCE_PYTHON> scripts/r3m14_collision_initial_witness.py --config configs/r3m17/B2.json --prepared <B2_ROOT>/preparation --out <B2_ROOT>/collision --max-steps 128`

단일 owner가 GPU를 순차 실행한다. 기존 command supervision과 MLflow outer tracing을
재사용하거나 같은 경계의 작은 coordinator를 작성한다. 각 command의 argv/cwd/env digest,
exit/timeout, stdout와 stderr를 별도 create-only 파일로 보존한다. CUDA/메모리 실패를
단순 scientific NO_GO로 바꾸지 않는다.

각 successful chunk가 종료되고 writer가 없을 때, 다음 chunk 전에:
`<SCIENCE_PYTHON> scripts/r3m17_checkpoint_guard.py snapshot --run <active-collision> --out <B2_ROOT>/generations/g<done> --config configs/r3m17/B2.json`

`generations` parent는 미리 만들되 `g<done>`은 반드시 fresh여야 한다. production에서
`--allow-unwitnessed` 사용 금지. guard 성공과 v2 receipt의 done/seal 일치 후에만 다음 chunk.
recovery generation을 만들기 전에는 다음 command를 시작하지 않는다.

중단되어 active checkpoint가 손상되면 증거를 보존한다. 마지막 published generation을
`r3m17_checkpoint_guard.py restore --generation <generation> --out <fresh-recovered-collision> --config ...`
로 별도 경로에 복원한 후 같은 initial/source/runtime의 v2 CLI로 계속한다. 이는 동일 B2의
sealed continuation이며 새 초기상태 collision이 아니다. 손상 경로에 덮어쓰지 않는다.
복구가 불가능하면 중지한다. 완료된 B2를 처음부터 다시 실행하지 않는다.

## 3. 분석: pair PASS와 잔여오차를 분리

최종 result/nstep/v2/seal/support/Gram diagnostics를 보존한다. P1/P2/P3, P_region,
norm, initial H residual, CAP-layer support 및 raw channel norms를 기록한다.

새 analyzer를 사용한다:
`<SCIENCE_PYTHON> scripts/r3m17_temporal.py --b2-run <active-collision> --b2-prepared <B2_ROOT>/preparation --out <new-B_TEMPORAL_ANALYSIS.json>`

이 도구는 actual dt, complete config/source/backend, frozen initial SHA, v2 binding,
checkpoint/receipt를 확인한 뒤 signed 차수와 conditional Richardson 값을 반환한다.
zero/작은 관측량의 상대오차를 자동 PASS로 처리하지 않는다. 필요 absolute tolerance는
새 과학계약으로 사전 등록하며 현재 상대예산을 조용히 바꾸지 않는다.

허용 결론:
- STRUCTURAL_OR_RUNTIME_BLOCKED: invalid/source/binding/resource/recovery defect를 특정.
- TIME_REFINEMENT_STILL_OPEN: 채널별 시간차분·차수·조건부 estimate가 충분하지 않음.
- EMPIRICAL_TEMPORAL_CANDIDATE_REQUIRES_CROSSCHECK: P1/P2/P3 모두 사전 기준에
  부합한 최초 temporal candidate. certified error 또는 전체 budget CLOSED가 아님.

target-only p≈2나 두 점의 작은 차이로 representation 변경을 승인하지 않는다.
B2만 있으므로 h=.25의 A2가 없고 dt=.0125 spatial gap은 NOT_MEASURED다.
B2−A1을 spatial gap으로 계산하지 않는다. 예측 파일은 HYPOTHETICAL이며 B2 결과로 복사하지 않는다.

이 노드에서는 추가 full collision, finer h, soft core, 새 propagator, AOCC trajectory를
실행하지 않는다. 수렴이 안 되면 측정된 이유에 맞춘 다음 한 노드를 **제안하고 종료**한다.
범용 '다음 연구루프' 이름으로 계산을 추가하지 않는다.

## 4. 다음 설계의 선택 원칙

순수 temporal 비용이 blocker면 current H_h의 full-H exponential / nonautonomous reference를
작은 고정 h 문제에서 먼저 비교한다. CUDA 큰 격자 Krylov basis를 무제한 할당하지 않는다.
전진 CAP에는 non-Hermitian-capable exponential action이 필요하고 Hermitian Lanczos를
그대로 사용하지 않는다. CFET 내부 exponential을 다시 저차 T/V split으로 대체해 고차라고
부르지 않는다. representation replacement는 별도 설계·독립 spatial 검증이 있어야 한다.

시간 candidate가 생겨도 moving-isolated-atom null, 동일 dt h 비교, grid-phase translation,
CAP/box 및 start/stop 검사를 남긴다. A/B차가 반드시 줄어야 한다는 사후 조건을 넣지 않는다.
spatial error와 temporal error의 상쇄가 풀리면 h-gap이 커질 수도 있다.
AOCC smoke metric PASS는 basis/channel validation과 분리한다.

## 5. 증거·백업·반환

작은 코드/config/results/report/manifest는 Git의 전용 `cr/` branch로 commit/push.
큰 initial/final 배열과 필요한 recovery 자료는 기존 디스크에 보존하고 완료된 단계의
기존 create-only 이중백업 절차를 쓴다:
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/
Google Drive parent 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI

기존 authorized connection만 사용하고 credential blocker를 그대로 반환한다. 단순 local
sync/Git push를 dual backup이라고 하지 않는다. SELECTIVE READBACK: ACK/objectID/
size/checksum과 manifest identity로 닫힌 단계는 같은 bytes를 다시 내려받지 않는다.
UPLOAD_VERIFIED와 RESTORE_VERIFIED를 구분한다. checkpoint guard의 LOCAL restore 시험은
remote backup 복원 증거가 아니다. 과거 R3M15/R3M16 전송을 반복하지 않는다.

최종 반환:
1. branch와 exact HEAD, remote-ref verification tier.
2. 보고서·판정·receipt의 commit permalink.
3. B0/B1/B2 P1/P2/P3, actual dt, signed changes, p, conditional estimates, norm/CAP.
4. full collision=정확히1 또는 blocked/이미완료로0; tiny diagnostic과 별도 계수.
5. 실제 test count/log, 환경 차이, 모든 최초 실패와 recovery 경로.
6. backup provider ACK/ID/size/checksum/verification tier; 미실행 restore 명시.
7. 실제 결과에 따른 정확히 하나의 다음 canonical node. Production/N1/all-bound/b-grid는
   해당 전체 exit criteria가 없는 한 OPEN/HOLD를 유지한다.
