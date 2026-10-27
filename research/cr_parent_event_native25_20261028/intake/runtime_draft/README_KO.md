# 새 parent-event 단위의 실행 계약 초안

이 디렉터리는 `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`의 C4 준비를 위한 **미실행 소스 초안**이다. 실행·import·compile·과학 계산·worker 시작은 수행하지 않았다. 문서 작성, 원문 읽기, diff 및 파일 해시 같은 metadata 작업의 CPU는 실측하지 않았으며 `0`으로 기록하지 않는다. 실제 C4 입장, 코드 설치, worker 실행, 단계 게시 권한은 root에 있다. 이 초안을 읽었다는 사실로 어느 R/C 단계를 완료 처리하지 않는다.

## 근거와 변경 범위

- R1 실제 게시: PR111, `fbc039ff5c357571cbbf2ff61d96fde8b3ce8594`; root의 dual R2 완료 통지를 확인했다.
- R1 계약: `research/cr_parent_event_native25_20261028/CONTRACT.json`, SHA256 `01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162`.
- 고정 input manifest: `inputs/INPUT_MANIFEST.json`, 17 files, SHA256 `2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3`.
- 실제 R02 preflight: SHA256 `604fdaf185ab0f5b0aa6bd7568e8736f7aa5924dbd0f568ddc02c8585a1fb520`; 17 pins 및 이전 source/backup receipt 점검 `PASS`, local/remote expected match를 읽었다. 이후 단계의 fresh preflight를 대체하지 않는다.
- 읽은 정책: `bass_cr/AGENTS.md`, SHA256 `bf1b921550473363df97f75bbbfc2e839120990f89a330b35da66867695f17b5`.
- 복사 원본: PR110 `research/cr_low_birth_causal_rr_20261027/implementation/run_bounded.py`, SHA256 `629d14ab8dd93fe0b23fb6394038f061f4a3fc0642922d110788d67922e05d9f`. 원본과 과거 비용·실패·archive는 수정하지 않았다.
- 이번 authoring 중 local HEAD `8ac0a56475e06c02e3e3e3a11417ef893fdcb4ce`를 읽었다. R1 뒤 root의 단계 게시가 진행 중인 관찰이며, 이 초안의 게시 또는 단계 완료 증거가 아니다.

수정은 새 단위 identity, 동일 단위 비용 결속, 알려진 PID 관찰, 새 C4 메모리 입장에 한정한다. source/물리 연산자·임계치·RR 결과를 import하거나 재실행하지 않는다. 현 단위 하나만 수행하고 다음 단위 자동 시작은 금지한다.

## 독립 예산

새 budget ID는 `CR_PARENT_EVENT_20261028_NEW40`이며 cap은 **40 CPU s**이다. 과거 PR107/PR109/PR110 또는 병렬 프로젝트의 미사용 예산은 가져오지 않는다.

| 역할 | 고유 run ID 초안 | worker CPU s | coordinator 및 영수증 tail CPU s | 선택 RLIMIT_AS |
|---|---|---:|---:|---:|
| 변경 preparation worker | `prepare_v1` | 3 | 2.05 | 256 MiB |
| controls | `controls_v1` | 3 | 2.05 | 256 MiB |
| primary | `primary_v1` | 4 | 2.05 | 256 MiB |
| independent reference | `independent_v1` | 6 | 2.05 | 256 MiB |
| saved-result plot | `plot_saved_v1` | 6 | 2.05 | 256 MiB |

각 coordinator 2.05 안에는 처음부터 0.05의 보수적 영수증 tail이 들어간다. 다섯 worker 22 + coordinator 10.25 + **입장·실패 preparation reserve 4 = 36.25**, 미할당 contingency는 3.75이다. 4초 preparation reserve는 실제 C4 host/proc 관찰과 실패 입장 비용을 위한 별도 항목이며 3초의 변경 preparation worker와 구분한다. 예약은 실측값이 아니다. cap 40은 전체 실제 charge를 대상으로 하고, 예약 초과 또는 실패도 지우지 않는다.

별도 필드는 순수 `measured_preparation_CPU_s`, `worker_cpu_s`, `coordinator_cpu_through_receipt_s`와 보수적 `conservative_tail_CPU_s`/`receipt_tail_reserve_s`이다. 전체 charge는 이 성분의 합이다. 과거 ledger의 charged preparation baseline을 순수 measured로 오해하게 만들었던 결합 필드는 새 ledger에서 사용하지 않는다.

## C4를 채우는 순서와 필수 실제 자료

1. 독립 정적 검토 뒤 root가 새 unit의 `implementation/run_bounded.py`로 설치한다. 이 `runtime_draft` 위치에서 실행하는 것은 허용되지 않는다. `--help`, import, compile도 이 작성 작업에서는 하지 않았다.
2. root가 fresh policy/HEAD/병렬 owner/source·backup receipt를 다시 읽고, 실제 host/cgroup과 알려진 PID 관찰을 수행한다. `C04_HOST_ADMISSION_TEMPLATE.json`은 그 결과를 담을 스키마이며 현재 `NOT_OBSERVED`이다. host receipt는 `status=completed`, `memory_gate=PASS`와 아래 PID probe의 실제 `PASS`를 요구한다.
3. 성공·실패를 포함한 모든 같은 단위 preparation receipt를 **create-only**로 남긴다. 각 receipt는 실제 측정값과 보수적 tail을 분리하고 `terminal_debit=true`, `cpu_accounting_complete=true`를 갖는다. 해결되지 않은 no-ACK는 임의의 0 비용으로 넣을 수 없다.
4. `C04_PREPARATION_LEDGER_TEMPLATE.json`의 각 행에 실제 unit-local path/bytes/SHA256 및 세 비용 성분을 넣는다. host receipt 자체도 반드시 이 ledger에 포함한다. `fsum` 비용 합계는 budget baseline과 `1e-12` 이내로 같아야 한다. preparation 총 charge는 4 이하이다.
5. 실제 production/reference 코드가 확정되면 `implementation/*.py`와 `review/*.py` 전체를 `C04_CODE_MANIFEST_TEMPLATE.json` 형식으로 bytes/SHA256 고정한다. 실행기는 snapshot을 만들 때도 frozen hash와 같음을 검사한다.
6. 실제 host/preparation/code manifest SHA256, 현재 AGENTS SHA256, 실제 cgroup path 및 `/proc/self/cgroup` 원문 SHA256을 `EXECUTION_BUDGET_TEMPLATE.json`에 넣고 검토한다. 그 뒤에만 `FROZEN_C4_ADMITTED`를 설정한다. null이나 status 문자열만 바꾼 template은 입장을 통과하지 못한다.

첫 worker 이후에는 preparation baseline과 순수 measured/tail 성분을 바꿀 수 없다. 그 뒤 발생하는 추가 입장 비용은 독립된 실제 attempt debit과 owner reconciliation으로 보존해야 한다. 실패한 run ID는 preworker에서 멈췄어도 재사용하지 않는다. 새 v2 등은 실제 잔여 charge와 고유 allocation을 반영한 명시적 검토 대상이다.

### 새 메모리 정책

초안 정책은 `RAW_HEADROOM_ONLY_V1`이며 이전 단위의 file-LRU 50% credit을 **자동 수입하지 않는다**. 읽은 실제 관찰값으로 다음을 검사한다.

`available = min(host MemAvailable, max(0, cgroup limit − current))`

cgroup limit이 `max`이면 host 관찰값을 사용한다. selected worker 256 MiB + host reserve 1 GiB = **1,342,177,280 bytes**가 필요하다. frozen worker upper cap 512 MiB는 유지하지만 실제 다섯 allocation의 RLIMIT_AS는 정확히 256 MiB이다. signed raw headroom, limit/current, file/shmem/active/inactive/mapped/dirty/writeback/unevictable counters를 영수증에 보존하며 reclaim credit은 0이다.

root는 기록한 cgroup path가 실제 process에 적용되는 제한을 나타내는지, 더 엄격한 descendant limit이 있는지 확인해야 한다. 실행기는 C4에 고정된 membership SHA가 그대로인지와 fresh counters를 최초 입장 및 launch 직전에 다시 검사한다. host/cgroup 관찰은 비원자적이며 메모리 보장 또는 outward lower-bound certificate가 아니다. OS 설정 변경이나 RAM pressure 조작은 없다. 새 credit 정책이 필요하면 별도 근거·검토·버전이 필요하다.

### 알려진 PID와 owned cleanup

C4 host receipt의 `owned_PID_observation_probe`는 실제 `known_Popen_PID`, kernel `start_ticks`, `live_PID_observed=true`, `child_cleanup_complete=true`, 측정 CPU를 요구한다. 이 probe 비용은 preparation ledger에 포함한다. probe의 `CPU_s`는 이미 receipt 총 preparation 측정에 포함된 부분값으로서 다시 더하지 않는다.

본 worker에서는 `Popen.pid`를 직접 census seed로 넣고 시작 직후 `/proc/<pid>/stat`의 parent/group/session/start identity를 확인한다. 살아 있지만 관찰할 수 없는 root worker, 바뀐 start identity 또는 탈출한 group은 실패이다. group kill은 unreaped Popen root가 있는 동안에만 수행하고, 그 밖에는 발견·검증한 owned PID/start pairs와 subreaper에 실제 귀속된 descendants만 정리한다. unrelated process를 이름으로 찾거나 종료하지 않는다.

## C4 이후에만 사용할 CLI 형태

아래는 **prospective example**이며 아직 production 파일명이 확정되었다는 뜻이 아니다. 실행하지 않았다.

```bash
python research/cr_parent_event_native25_20261028/implementation/run_bounded.py \
  --run-id prepare_v1 --cpu-reserve 3 --memory-limit-bytes 268435456 -- \
  python implementation/prepare.py --out runs/prepare_v1
```

root가 실제 코드 파일명과 manifest를 확정한 뒤 일치하는 명령을 사용한다. interpreter는 현재 실행기와 같은 Python이어야 하고 script는 고정 manifest 안에 있어야 한다. `--out`은 정확히 한 번이며 `runs/<run_id>`와 같아야 한다. worker는 `CR_BOUNDED_UNIT`, `CR_BOUNDED_OUTDIR`, `CR_BOUNDED_ATTEMPT_ID`와 실제 reservation을 검증하는 guard를 별도로 가진다.

## 회계·실패 보존과 한계

실행기 진입 즉시 고유 invocation lease를 create-only로 만들고, argparse/lock/admission/outdir/snapshot/worker 실패에도 독립 terminal debit을 남긴다. ledger lock을 얻지 못해도 standalone debit 경로는 사용한다. 같은 attempt의 normal receipt와 후속 cumulative amendment는 **최대 charge 한 번**만 집계한다. terminal debit이 없는 lease/reservation, malformed receipt, 불완전 child CPU 정리는 다음 입장을 닫고 owner reconciliation을 요구한다. stale lease를 지우거나 no-ACK를 0으로 리셋하지 않는다.

coordinator 초기 비용이 이미 예약을 썼다면 worker를 시작하지 않는다. 실행 중 owned PID polling, worker/group cleanup, RUSAGE_CHILDREN 및 RUSAGE_SELF debit을 유지한다. polling은 비원자적 추정이고 RLIMIT_CPU는 process별 제한이다. 따라서 총 descendant CPU가 cap을 절대 넘을 수 없다는 kernel hard-proof는 주장하지 않는다. 실제 reservation 초과, tail 확대 또는 실패가 있으면 비용과 실패를 그대로 기록한다. 정적 초안의 PID 수선은 아직 실제 실행 검증을 받지 않았다.

작성 중 한 차례 source-range 불일치는 적용 전 중단되었고, 한 차례 exec transport 단절은 readback으로 미적용을 확인한 뒤 metadata patch만 재시도했다. worker 또는 과학 실행 실패로 바꾸어 기록하지 않으며, 이 metadata 작업 CPU도 미측정이다.

기존 PR110의 C4 resource refusal, controls v1 oracle failure, plot v1 실패와 24.692011/40 charge(순수 measured 14.616973, tail 10.075038000000001)는 원본 기록으로 보존한다. 그 미사용분을 새 예산에 이월하지 않는다. 이 초안은 중앙 28/88과 이번 CR 효과 0, global completion/error/budget currency null을 바꾸지 않는다.

## 기존 intake의 한 문장 의미 정정

이전 consumer feasibility 초안의 “actual w_ext=0인 scoped projection”은 total actual 외부 일을 뜻하지 않는다. 현재 frozen R1이 우선한다: **actual total `w_ext`와 CR donor/proton debit은 null**, retained-photon의 `w_ext` 기여는 0, scoped RR projection 또는 명시적 conditional fixture의 0은 그 좁은 계약값이다. 과거 게시 파일을 고치지 않고 이 구분을 prospective 작업에 적용한다.
