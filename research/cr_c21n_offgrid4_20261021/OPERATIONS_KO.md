# offgrid4 실제 실행과 재실행 방지

## 실제 완료된 실행

2026-10-21 13:10:16 UTC에 시작한 run은 샌드박스 host
`af4832b34a81`에서 새 4개 case를 완료했다.
Run identity는
`f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023`다.
실행 source는 C21N content
`5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`의 격리 checkout이며,
이 후속 분석·문서 branch를 실행 source로 소급 표기하지 않는다.

실제 호출은 다음과 같다. **이는 완료된 과거 실행 기록이므로 다시 실행하지 않는다.**

```bash
python -B \
  /workspace/scratch/10765dc22dcf/c21n_offgrid_exec_20261021T1306Z/research/cr_c21n_mass_shell_cache_20261021/shared_runner.py \
  --grid /workspace/scratch/10765dc22dcf/c21n_offgrid_exec_20261021T1306Z/research/cr_c21n_mass_shell_cache_20261021/prepared_offgrid4/grid_offgrid4.json \
  --output /workspace/scratch/10765dc22dcf/c21n_offgrid4_sandbox_20261021T1306Z \
  --workers 4 --execution-site sandbox \
  --timeout-seconds 300 --active-grace-seconds 60 \
  --lease-dir /tmp/bass_cpu_leases
```

원 run directory의 28개 파일을 `raw_offgrid4/`로 복사하고 전체 bytes를 대조했다.
`EXECUTION_RECEIPT.json`과 case별 `COMPLETE.json`은 raw·RESULT hash를 결속한다.
새 과학 ODE는 4회, 기존 81/125 재적분은 0회다. 원 uncached solver로 같은
4개를 다시 적분하는 paired replay는 수행하지 않았다.

## 자원과 시간의 해석

실행 시 affinity는 CPU0–8, 보이는 cgroup quota는 8 CPU, memory limit는
8 GiB였다. Coordinator는 CPU0, science worker는 CPU1–4에 고정됐다.
CPU55는 정책상 제외되며 이 샌드박스의 가용 affinity에 포함되지 않았다.
다른 owner의 process·파일·lease는 변경하지 않았다.

각 numerical library의 thread 환경변수는 1이다. Worker가 반환할 때 관측한
프로세스 thread 수는 각각 2였으며, 이는 numerical thread1 정책과 구분한다.
Python multiprocessing Queue의 관리 thread를 포함할 수 있으므로
"프로세스 전체가 단일 thread"라고 보고하지 않는다.

실제 coordinator 영수증의 wall time은 3.26130703400122초다.
이 시간과 case별 nfev·solver wall·process RSS는 실행 provenance이며
벤치마크·speedup·memory improvement·64-core scaling의 증거로 쓰지 않는다.
Python3.12.14, NumPy2.3.5, SciPy1.17.0 환경을 별도 기록했다.

새 plan 단계의 storage 관측은 available24,362,303,488bytes/inode2,028,464였다.
4case 요구 예산은 2,248,146,944bytes와321inode였다. 이는 저장공간 예약이
아니며 사용자·프로젝트 quota의 독립 확인도 아니다. 실제 실행 직전 및
dispatch 전 관측값은 `raw_offgrid4/STORAGE_*`와 `EVENTS_*`를 따른다.

Worker512MiB·coordinator256MiB·최소1GiB reserve는 기존 보수적 운영 예산이다.
완료 raw의 실제 process high-water RSS는 해당 한 실행의 관측값이며
보편적인 memory bound가 아니다.

## 완료 입력 registry

`COMPLETED_INPUTS_129.json`은 기존125 registry와 새4개의 manifest·raw·seal에
결속된다. 129개는 125 정규격자에4개 opposing-stress 점을 추가한 집합이며,
129개 정규 3차원 격자가 아니다. 원 C21N의125 registry는 변경하지 않았다.

새 `completed_input_guard.py`는 이름이 바뀌어도 세 signed 좌표가 축별
2e-13 이내로 일치하면 완료 입력을 거부한다. Solver를 import하거나 실행하지
않는다. 다른 입력을 통과시켜도 physical validity나 새 science 승인을 제공하지 않는다.

새 guard는 역사적 N runner에 자동 주입되지 않는다. 향후 명시적으로 승인된
새 grid를 실행할 때 **새 guard를 먼저 호출하고 성공한 경우에만** 고정 N
launcher를 호출해야 한다. 현재 offgrid4 grid의 기대 결과는
`REFUSE_COMPLETED_INPUTS`, exit2다. `--resume` 역시 이번 네 입력을 다시
실행하기 위한 우회 경로가 아니다.

## NCP 상태

현재 샌드박스에는 지정된 `/home/cosmosapjw/.ssh/ncp_key`가 없다.
따라서 이번 후속4의 NCP 실제 실행은 `NOT_RUN`, live host/resource 확인은
`UNAVAILABLE`다. 앞서 수용한 NCP98의 완료 기록은 그대로 유지한다.
동일4개를 NCP에서 다시 실행할 과학적 필요는 현재 없다.

향후 승인된 새 입력이 생기면 NCP의64 logical CPU/128GB라는 명목 사양 대신
affinity, cgroup quota·cpuset, free RAM, load, 기존 lease, disk/inode를 새로
확인한다. 사용자가 보고한 과거 root filesystem 고갈은 현재 관측이 아니므로
실제 `df`/statvfs 결과로 판단한다. CPU55와 coordinator 비용을 유지하고
case수·유휴CPU·quota·memory 중 가장 작은 허용량에 맞춰 worker를 배정한다.
다른 세션이 있다는 이유만으로 전체 중단하거나 다른 owner의 자원을 강제로
회수하지 않는다.
