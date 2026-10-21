# C21N NCP 실행 인계: 이미 준비된 새로운 4개 초기조건

## 1. 바로 전달할 Codex 요청

```text
cosmosapjw-quantum/bass_cr의 C21N을 이어서 처리해줘.
먼저 PR93 및 후속 branch/실행 반환/백업에 offgrid4 결과가 새로 왔는지 확인해.
이미 완료된 C21L81, C21M26, NCP98, combined125는 재실행하지 마.

권위 물리 source는 REI 3b85dedce84d37b3e165da00685a8a984950aafe이다.
실행할 C21N content는 5ecb8a6c4961302b7066b06278e72ecd2d77f8c9이고
문서 branch HEAD와 source content를 구분해. 격리 checkout에서 아래 명령을 써.
prepared_offgrid4/grid_offgrid4.json의 새 opposing-stress 4개는 초기조건 및
원 builder 대비 초기 state/RHS 동등성까지 검증됐으나 과학 ODE는 NOT_RUN이다.
새로운 결과가 없다면 이 4개만 create-only directory에서 실제 실행해.

현재 affinity/cgroup quota/RAM/load/disk/inode/협력 lease를 새로 확인하고,
CPU55를 보호하며 coordinator 비용과 각 worker의 numeric thread1을 포함해.
다른 세션이 있다는 이유로 전체 중단하지 말고 실제 유휴 자원에 맞춰 배정해.
다른 owner의 process/output/lease는 변경하지 마. 새 case가4개이므로
62-worker 상한을 설정해도 science worker는 최대4개다.

원 FP64, 40상태, DOP853, rtol3e-11/atol3e-13, 101저장점,
z20→4, 기존 source 및 분포 정규화를 유지해. 상세 benchmark나 기존 검증
전체를 다시 실행할 필요는 없어. 환경 수정이 필요하면 원 content와
변경 source를 분리하고 새 hash를 기록해.

완료 raw/manifest/COMPLETE/RESULT/RETURN와 실제 host·software·resource·시간을
회수하고 source/input identity를 확인한 뒤 성분별 후처리 및 기존125와의
비교를 수행해. 실제 수행한 범위만 PASS_SCOPED로 보고하고 새 run ID를 유지해.
매 단계 EXECUTION | PUBLICATION | BACKUP | DAG를 분리해 기록하고
새 content/document 게시와 create-only backup을 마쳐줘.
global_error_bound=null; triaxial/full reionization/CMB는 HOLD다.
```

## 2. 고정 입력과 과학 범위

| 항목 | 고정 값 |
|---|---|
| PR | https://github.com/cosmosapjw-quantum/bass_cr/pull/93 |
| Branch | `research/cr-c21n-mass-shell-cache-20261021` |
| 실행 content | `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9` |
| 원 물리 source | `3b85dedce84d37b3e165da00685a8a984950aafe` |
| Run ID | `c21n_offgrid4_opposing_z20_z4_20261021` |
| Grid SHA256 | `2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5` |
| 좌표 | signed full Frobenius `(S0,Pm0,Pr0)` |
| 입력 | `S0=0`, `Pm0=±7.5e-5,±1.75e-4`, `Pr0=-Pm0` |
| 상태 | 초기 physical certificates + sandbox plan 완료; 새 과학 ODE `NOT_RUN` |

현재 source는 Python이다. 새 C/C++ 컴파일은 필요하지 않다. 기존 C21M의 실제
NCP98 실행 환경은 Python3.12.3/NumPy2.3.5/SciPy1.17.0이었고, 이번 샌드박스
검증은 Python3.12.14였다. Matplotlib pin은3.10.8이다. 새 NCP의 관측 환경은
별도로 기록한다. 과거 host 기록은 현재 접근이나 자원 가용성의 증명이 아니다.

## 3. NCP shell 명령

아래는 NCP에 접속한 상태에서 실행한다. 기본 작업 경로는 **새로 제안하는
연구 전용 경로**이며 현재 host에 존재한다고 확인한 경로가 아니다. 기존 준비된
Python 환경이 있으면 실행 전에 `C21N_PYTHON`을 그 절대 경로로 지정한다.
그렇지 않으면 새 전용 venv를 만들고 고정 requirements를 설치한다.
현장 공유 lease 경로가 다르면 `C21N_LEASE_DIR`를 기존 경로에 맞춘다.

```bash
set -euo pipefail
set -o noclobber

export C21N_CONTENT_COMMIT='5ecb8a6c4961302b7066b06278e72ecd2d77f8c9'
task_branch='research/cr-c21n-mass-shell-cache-20261021'
task_work_root="${C21N_WORK_ROOT:-/root/bass_cr_c21n_runs}"
mkdir -p "$task_work_root"
task_repo="$(mktemp -d "$task_work_root/checkout_XXXXXXXX")"

git clone --filter=blob:none --single-branch --branch "$task_branch" --no-checkout \
  https://github.com/cosmosapjw-quantum/bass_cr.git "$task_repo"
git -C "$task_repo" sparse-checkout init --cone
git -C "$task_repo" sparse-checkout set \
  research/cr_c21l_rei_pilot_20261021 \
  research/cr_c21m_independent_stress_20261021 \
  research/cr_c21n_mass_shell_cache_20261021
git -C "$task_repo" checkout --detach "$C21N_CONTENT_COMMIT"
test "$(git -C "$task_repo" rev-parse HEAD)" = "$C21N_CONTENT_COMMIT"

task_unit="$task_repo/research/cr_c21n_mass_shell_cache_20261021"
if [[ -z "${C21N_PYTHON:-}" ]]; then
  task_venv="$task_work_root/venv_$(basename "$task_repo")"
  "${C21N_BASE_PYTHON:-python3.12}" -m venv "$task_venv"
  export C21N_PYTHON="$task_venv/bin/python"
  "$C21N_PYTHON" -m pip install -r "$task_unit/requirements-science.txt"
fi
"$C21N_PYTHON" -c 'import sys,numpy,scipy,matplotlib; print(sys.version); print(numpy.__version__,scipy.__version__,matplotlib.__version__); assert (numpy.__version__,scipy.__version__,matplotlib.__version__)==("2.3.5","1.17.0","3.10.8")'

task_grid="$task_unit/prepared_offgrid4/grid_offgrid4.json"
printf '%s  %s\n' \
  '2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5' \
  "$task_grid" | sha256sum --check

export C21N_WORKERS=62
export C21N_LEASE_DIR="${C21N_LEASE_DIR:-/tmp/bass_cpu_leases}"
export C21N_TMPDIR="${C21N_TMPDIR:-/tmp}"
export C21N_TIMEOUT_SECONDS=3600
export C21N_ACTIVE_GRACE_SECONDS=300
task_tag="$(date -u +%Y%m%dT%H%M%SZ)_$$"
task_output="$task_work_root/runs/offgrid4_$task_tag"
test ! -e "$task_output"

bash "$task_unit/ncp_run.sh" plan "$task_repo" "$task_grid" "$task_output"
bash "$task_unit/ncp_run.sh" run  "$task_repo" "$task_grid" "$task_output"
```

`plan`은 run output이나 CPU lease를 만들지 않는다. `run`도 실행 직전에
자원과 저장공간을 다시 확인한다. 실제 `execution_site=ncp`는 operator 선언이며
관측 hostname와 raw 완료 증거를 함께 읽어야 한다. Shell 변수들은 후속 수집에
사용하므로 같은 session을 유지하거나 별도 실행 메모에 실제 경로를 기록한다.

### 재개

같은 `task_repo`, `task_grid`, `task_output`, Python 환경을 복원한 뒤:

```bash
bash "$task_unit/ncp_run.sh" resume "$task_repo" "$task_grid" "$task_output"
```

이는 미시작 case에만 적용한다. `STARTED`/실패/미봉인 결과를 자동 재실행하지
않는다. 기존 완료 seal/raw를 검증하고 보존한다. 어떤 경로도 임의로 삭제해
새 run처럼 보이게 만들지 않는다.

## 4. 실행 자원 계약

- 명목64 logical CPU/128GB를 실측값으로 쓰지 않는다. CPU affinity, 보이는
  cgroup quota·cpuset·memory, 실제 RAM/load, 기존 `flock` lease를 관측한다.
- CPU55를 제외하고 coordinator CPU1개를 비용에 포함한다. 요청 상한62,
  이 입력은 남은 case수에 따라 최대4science workers다. 각 numeric library는1thread다.
- 메모리 계획은 worker512MiB, coordinator256MiB,
  reserve `max(1GiB, observed memory limit/8)`이다. 측정된 peak나 OS강제제한은 아니다.
- 저장공간은 available blocks/inodes 기준이며4case에서 최소
  2,248,146,944bytes와 `320+새 경로 생성 inode수`를 요구한다.
  이는 conservative allowance다. 이후 plot/배송ZIP은 이 예산 밖에 있다.
  사용자·프로젝트 quota는 `statvfs`만으로 보증되지 않으므로 별도 현장 제한이
  있으면 확인한다. Preflight가 실제 용량을 예약하지 않는다.
- 부하 증가나 저장공간 감소 시 신규 dispatch를 줄이거나 멈추고 완료 raw를
  보존한다. 다른 owner의 process·lease·output을 변경하지 않는다.

## 5. 결과 회수와 다음 분석

`MANIFEST.json`, attempt별 `RESOURCES_*.json`/`STORAGE_*.json`/`EVENTS_*.jsonl`,
`RETURN_*.json`/`SUMMARY_*.json`, 각 case의
`RESERVATION`/`STARTED`/`RESULT`/`COMPLETE` 및 raw 파일을 함께 보존한다.
grid/source/software에 결속한 실제 run identity는 실행 환경에서 생성한 값을
사용한다. 샌드박스 `plan` identity를 NCP identity로 복사하지 않는다.

새 결과가 도착하면 먼저 original C21N content와 source hash,4개 좌표와101×40
trajectory, positivity/normalization/Hamiltonian 및 component signs를 확인한다.
성분 합을 먼저 만들고 norm을 취하며 photon/존재하는 neutrino를 분리 보존한다.
저장 trajectory를 대상으로 초기 mass-shell 계수와 signed shear를 비교한다.
현재 quadratic jet는 첫 저장점에서도 최대2.12% 차이가 있었으므로1% 또는
전 구간 근사로 채택하지 않는다. 자세한 benchmark를 새로 시작하지 않는다.

이4개와 기존125를 합친129개는 불규칙한 확장 ensemble이다. 3차원 정규격자나
새125개 sweep로 부르지 않는다. raw/receipt를 새 content로 게시하고 해당
content의 후처리·문서·DAG·백업을 별도로 마감한다.

## 6. 보존해야 할 범위

물리적 과학 범위는 preliminary non-tilted collisionless LRS Bianchi I다.
`global_error_bound=null`, general triaxial/full reionization/CMB는 HOLD다.
Speedup·메모리 절감·64-core scaling은 측정하지 않았다. 기존125의 단일 NCP
실행 시간을 C21N 최적화의 성능 자료로 사용하지 않는다.
