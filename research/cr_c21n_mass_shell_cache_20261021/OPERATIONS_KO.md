# C21N 공유 실행과 저장공간 admission

## 현재 상태와 적용 범위

| 구분 | 이 운영 구현의 현재 상태 |
|---|---|
| EXECUTION | `PASS_SCOPED`: 새 운영 경로의 focused checks. 새 과학 ODE 0, 현재 세션의 NCP 접속·실행 0. |
| PUBLICATION | 이 파일과 source/checks를 포함할 C21N content commit은 상위 closeout receipt가 확정한다. |
| BACKUP | 이 변경의 백업 여부는 별도 provider receipt를 따른다. 이전 C21LM ACK와 혼동하지 않는다. |
| DAG | 저장공간 guard·기존125 재실행 방지·cached builder worker 초기화는 구현·범위 검증. 새 과학 실행은 `NOT_RUN`. |

C21M의 sandbox26 + NCP98 + 재사용 중심1 = 125개 완료 결과를 재사용한다. 이전 NCP98 `NOT_RUN` 문구는 역사 기록이며, 이번 C21N 실행 여부와 별개다. 이번 운영 검사는 `test_storage_preflight.py`의 synthetic case3개만 처리한다. 실제 `builder`와 immutable prepared grid를 import하여 worker `READY`와 source identity를 검사하지만, test backend는 `build`, RHS, ODE 적분을 호출하지 않는다. 모든 synthetic manifest/receipt에 `OPERATIONAL_TEST_DOUBLE` 구분을 남긴다.

원 C21M `shared_resources.py`는 byte-identical 복사다. CPU affinity, cgroup v1/v2의 보이는 계층 quota·memory·cpuset, 실제 load, CPU55 제외, coordinator 비용, 협력 `flock` lease, 동적 신규 dispatch 축소를 유지한다. 해당 파일의 C21M docstring은 원본 보존에 따른 것이다. 기존 resource/science suite는 반복하지 않았다.

## 실행을 허용하는 입력

기본 grid는 없다. 명령줄에 `--grid`로 명시된 새 파일만 읽는다. Schema는 `C21N_GRID_V1`, `run_id`는 `c21n_`로 시작하는 최대80자 문자열이고, 각 case에는 고유한 `case_id`와 유한한 signed full Frobenius 좌표 `S0`, `Pm0`, `Pr0`가 필요하다. 같은 새 grid 안의 동일 좌표 중복도 거절한다. 실제 물리 가능 범위와 초기 분포 양성·정규화 검사는 원 계열 builder가 수행한다.

`completed_targets.json`은 실제 기존 grid26/98, 두 run manifest, 중심 reuse 기록 및 중심 원 manifest/raw/receipt, 125-case 분석의 `INPUT_SOURCES.json` 등 총9개 파일의 SHA256·크기에 결속한다. 원본 파일을 읽어 검증하며 수정하지 않는다. 새 입력이 기존125 중 하나와 각 좌표에서 모두 절대차 `≤2e-13`이면 `ALREADY_COMPLETED_PHYSICAL_TARGET`로 거절한다. 중심의 실제 작은 quadrature offset은 registry에 보존한다. 이 tolerance는 중복 실행 방지 기준이며, 서로 다른 계산의 byte identity나 전역 물리 오차 상계가 아니다.

원81 및 M26/98 grid를 자동 생성하거나 실행하는 경로는 없다. 기존 run directory를 새 source로 resume하지 않는다. 새로운 물리 문제나 source family를 연구할 경우에는 이 registry의 의미를 몰래 변경하지 않고 별도 input/source 계약을 만든다.

## 저장공간 검사

`storage_preflight.py`는 output path의 가장 가까운 기존 상위 디렉터리에서 `os.statvfs`를 읽는다. 새 run directory, `MANIFEST`, coordinator lock, CPU lease 생성 전에 검사한다. `--plan-only`에도 같은 검사가 적용된다. Disk preflight 자체는 경로를 생성하지 않는다.

사용 가능한 공간은 `f_bavail × f_frsize`이며 `f_frsize`가0일 때만 `f_bsize`로 대체한다. `f_bfree`에 포함될 수 있는 특권 예약 block을 실행 가능 용량으로 세지 않는다. Inode는 `f_favail`을 사용한다. Unknown block/inode 정보, read-only filesystem, 쓰기·탐색 불가 상위 경로, 관측 오류는 fail closed다.

| 예산 | Byte | Inode |
|---|---:|---:|
| 공유 filesystem에 남겨둘 reserve | 2GiB | 256 |
| coordinator의 manifest·event·summary·return | 64MiB | 32 |
| 아직 완료하지 않은 case당 raw·receipt | 8MiB | 8 |
| 생성할 상위 디렉터리 | 위 coordinator 여유에 포함 | 관측된 미생성 경로 수를 추가 |

40×101 FP64 state, 128개 scalar channel, 4×9×101 moment 배열의 합은 0.2MiB 미만이다. Case당8MiB는 NPZ/JSON overhead와 추가 여유를 포함한 보수적 계획 예산이다. 현재 case 하나는 directory와 `RESERVATION`, `STARTED`, `history.npz`, `RESULT`, `COMPLETE`의6개 inode를 쓰므로8개를 계상한다. Plot·배포 ZIP·추가 분석 공간은 이 raw 실행 예산에 포함되지 않는다.

이는 사용량 측정에 근거한 경량화 주장이나 filesystem 예약·할당량 강제가 아니다. 실제 사용자/project quota는 `statvfs`만으로 검증되지 않는다. 관측과 실제 쓰기 사이에 다른 작업이 공간을 쓸 수 있으므로, resource admission 대기 중과 새 case dispatch 전에도 검사한다. 검사 실패 시 더 배포하지 않고 기존 active case가 종료되도록 둔다. 이미 완료된 raw 및 실패·중단 흔적은 보존한다. 저장공간 회복 후 같은 manifest로 재개하면 미시작 case만 새로 시작한다. 사용자나 다른 owner의 파일을 자동 삭제하지 않는다.

## CPU·메모리와 작업 큐

`--workers`와 `C21N_WORKERS`의 절대 상한은62다. 실재64 logical CPUs를 모두 사용할 수 있더라도 CPU55를 제외하고 coordinator 한 CPU를 남기는 상한이다. 실제 affinity/cgroup/idle CPU/lease/memory/미시작 case 수가 더 작으면 worker 수를 줄인다. 명목64 CPU·128GB를 관측 자원으로 취급하지 않는다. 예를 들어 새 case가4개이면 science worker는 최대4개다.

Worker당1 thread, 보수적 메모리 계획은512MiB/worker + coordinator256MiB + `max(1GiB, observed memory limit/8)` reserve다. 원 예산의 64 FP64 momentum buffer와 저장 channel allowance를 유지한다. Prepared momentum의 불변 작은 배열은 이 여유 안에 있으나 실제 peak memory 절감이나64-core scaling은 측정하지 않았다.

각 worker에 큐1개·미처리 task 최대1개만 둔다. 완료된 worker에만 새 case를 배포한다. 다른 작업의 부하가 증가하면 신규 dispatch만 줄이며 다른 프로세스·lease를 중지하거나 변경하지 않는다. 종료 정리는 이 coordinator가 직접 생성한 `multiprocessing.Process` 객체에만 적용한다.

Legacy pyplot import 때문에 필요한 `MPLCONFIGDIR`는 매 attempt마다 private temporary directory로 만들고 실제 작은 파일 쓰기로 writable 여부를 확인한다. 종료 후 삭제하고 호출자의 환경변수 값을 복구한다. `C21N_TMPDIR` 또는 `TMPDIR`는 현재 host에서 쓰기 가능한 기존 디렉터리여야 한다. Plan은 영속 output/lease/cache를 만들지 않는다.

## Source와 resume 계약

Run manifest는 `builder.py`, `prepared_momentum.py`, `shared_runner.py`, `shared_resources.py`, `storage_preflight.py`, `completed_targets.json`의 digest, builder의 원 REI source/adapter identity, grid bytes, software version, storage 예산 및 site 선언을 결속한다. Worker도 같은 code hash와 새 builder identity를 확인한 뒤 `READY`를 보낸다. `execution_site=ncp`는 운영자 선언이며 실제 hostname·affinity는 따로 기록한다.

`--resume`은 manifest/source/grid/software가 완전히 같아야 한다. `COMPLETE.json`의 raw·result hash seal을 검사한다. `STARTED`가 있는 미완료 case, 실패 case, seal 없는 result는 자동 재실행하지 않는다. 원 파일을 지워 새 입력처럼 보이게 만들지 않는다. 새 attempt의 summary/event/return은 별도 이름으로 저장한다.

## NCP에서 사용할 명령

다음은 실행 위치별 경로와 최종 게시 content SHA만 채우면 된다. 이 문서는 현재 세션의 실행 완료를 주장하지 않는다. Grid 파일은 별도 검토된 explicit 새 입력을 사용한다.

```bash
export C21N_CONTENT_COMMIT='<published-tested-C21N-content-SHA>'
export C21N_PYTHON='/absolute/path/to/prepared/python'
export C21N_WORKERS=62
export C21N_LEASE_DIR='/tmp/bass_cpu_leases'
export C21N_TMPDIR='/absolute/path/to/writable/tmp'

bash /absolute/repo/research/cr_c21n_mass_shell_cache_20261021/ncp_run.sh \
  plan /absolute/repo /absolute/new_grid.json /absolute/new_create_only_run

bash /absolute/repo/research/cr_c21n_mass_shell_cache_20261021/ncp_run.sh \
  run /absolute/repo /absolute/new_grid.json /absolute/new_create_only_run
```

미시작 case가 남았을 때만 같은 content·grid·software로 위 명령의 `run`을 `resume`으로 바꾼다. 실행 스크립트는 `HEAD == C21N_CONTENT_COMMIT`을 요구하며 원 M production source, C21L adapter/vendor source 및 새 N dependencies의 clean 상태를 확인한다. 필요한 패키지는 `requirements-science.txt`의 NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8이다. 스크립트가 공유 환경에 패키지를 자동 설치하지 않는다.

저장공간만 확인하려면 다음 read-only probe를 사용할 수 있다.

```bash
python3 -B /absolute/repo/research/cr_c21n_mass_shell_cache_20261021/storage_preflight.py \
  --output /absolute/new_create_only_run --cases 4
```

## 수행한 focused 검증

`checks/ops_storage_v1/`은3개 그룹을 보존한다: available-block/inode/readonly/unavailable/unwritable negative fixtures와 metadata 무변경, hash-bound 기존125와 근접중심·구 schema 거절, 실제 cached builder를 import하는 fake worker3 case의 `READY` 및 disk 감소 후 미시작-only resume다. 첫 fake 결과의 byte를 그대로 보존했고 synthetic case는 총3개만 처리했다. 실제 NCP 검증은 아니다.

그 뒤 code review에서 resource-wait event의 disk 소비도 검사해야 함을 확인해 대기 분기에 검사3줄을 추가했다. `checks/ops_wait_guard_v2/`는 이 바뀐 분기만 별도로 검사했고, synthetic disk 감소 시 CPU lease·worker·`STARTED` 없이 `NOT_STARTED`와 실패 근거를 보존했다. 이 추가 검사의 fake case 실행은0이다. 첫3그룹의 원 tested source snapshot과 hash는 덮어쓰지 않았다. 최종 source에는 첫 검증과 이 좁은 후속 검증을 합쳐 적용하며, 첫 receipt를 최종 source에서 다시 실행한 것으로 표현하지 않는다.

`global_error_bound=null`을 유지한다. 새 운영 검증은 기존 preliminary collisionless non-tilted LRS 결과의 물리 범위를 확장하지 않는다.
