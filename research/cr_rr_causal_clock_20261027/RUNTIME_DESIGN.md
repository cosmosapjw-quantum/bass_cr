# CR clock bounded dispatcher — candidate design

## 현재 상태

dispatch.py는 새 CR_RR_CAUSAL_ERLANG_CLOCK_V1의 로컬 실행 하네스 후보다. 기존 HeIII dispatcher 전체와 현재 RESEARCH_CONTRACT, EXECUTION_PLAN, PREPARATION_RECEIPT를 실제 읽고 새 단위에 필요한 부분을 분리했다.

**AST 구문 검사만 수행했다.** 이 후보 모듈을 import하거나 dispatch/worker/self-test/solver를 실행하지 않았다. 새 연구 unit 또는 원격 저장소를 수정하지 않았다. 소스 복사, native 빌드, C5 게시와 실제 실행 권한 결속은 root가 수행한다.

기존 파일의 단순 상수 치환은 하지 않았다. old R6 decision 문자열과 primary actual_primary_RHS=224 gate, old run ID, old 30 CPU초 및 source 경로를 제거하고 root가 동결한 새 plan/pins/worker argv에 결속했다.

## CLI

현재 root의 EXECUTION_PLAN에 동결된 필드와 맞춘 인터페이스다.

    python -B implementation/dispatch.py \
      --unit /absolute/path/to/cr_rr_causal_clock_20261027 \
      --mode controls \
      --run-id cr_clock_controls_20261027_v1 \
      --config /absolute/path/to/cr_rr_causal_clock_20261027/EXECUTION_PLAN.json \
      --pins /absolute/path/to/cr_rr_causal_clock_20261027/SOURCE_PINS.json

mode는 controls, primary, independent, plot 중 하나다. 새로운 run ID는 경로 문자가 없는 고유 ID여야 한다. 같은 실행 디렉터리는 다시 열거나 덮어쓰지 않는다. 재시도는 retained 실패를 보존한 별도 ID와 남은 동일 stage 예산으로만 가능하다.

C9는 같은 config와 별도의 SOURCE_PINS_C9.json을 사용할 수 있다. 해당 pins에 REFERENCE_PLAN.json, qualification 및 primary output을 실제 unit-relative 파일로 포함한다. 원본 pins를 업데이트했다는 이유로 과거 attempt의 source identity를 바꾸지 않는다.

## 필수 EXECUTION_PLAN 구조

    {
      "schema": "CR_CLOCK_EXECUTION_PLAN_V1",
      "unit_id": "CR_RR_CAUSAL_ERLANG_CLOCK_V1",
      "resources": {
        "total_cpu_s": 60,
        "stage_cpu_s": {
          "controls": 5,
          "primary": 30,
          "independent": 15,
          "plot": 5
        },
        "coordinator_cpu_s": 2,
        "r7_unused_reservation_s": 3,
        "wall_s": 60,
        "RLIMIT_AS_bytes": 536870912,
        "memory_reserve_bytes": 1073741824,
        "native_threads": 1,
        "cpus": {
          "coordinator": 0,
          "worker": 1,
          "independent": 2,
          "plot": 3
        }
      },
      "mode_argv": {
        "controls": [
          "implementation/controls.py",
          "--unit", "{unit}", "--output", "{output}",
          "--run-id", "{run_id}", "--config", "{config}", "--pins", "{pins}"
        ],
        "primary": [
          "implementation/primary_runner.py",
          "--unit", "{unit}", "--output", "{output}",
          "--run-id", "{run_id}", "--config", "{config}", "--pins", "{pins}"
        ],
        "independent": [
          "implementation/reference_runner.py",
          "--unit", "{unit}", "--output", "{output}",
          "--run-id", "{run_id}", "--config", "{config}", "--pins", "{pins}"
        ],
        "plot": [
          "implementation/plot_saved.py",
          "--unit", "{unit}", "--output", "{output}",
          "--run-id", "{run_id}", "--config", "{config}", "--pins", "{pins}"
        ]
      }
    }

위 0/1/2/3은 현재 root의 실제 C4 admission에 따른 역할 배치다. dispatcher는 매 실행의 actual affinity와 대조한다. 별도 환경에서 이 숫자가 가용하다고 가정하지 않는다. 네 역할 CPU는 서로 달라야 하고 cgroup CPU quota는 동시 coordinator+worker에 해당하는 2 CPU 이상이어야 한다. 한 번에 실제 실행되는 worker는 하나다.

total/stage/coordinator/R7/native/AS/wall 값은 새 계약과 정확히 같아야 한다. memory reserve는 최소 1 GiB이며 더 작은 값은 거부한다. R7의 3초는 unused reservation으로 계속 보유하고 다른 mode에 이전하지 않는다.

## SOURCE_PINS

    {
      "schema": "CR_CLOCK_SOURCE_PINS_V1",
      "unit_id": "CR_RR_CAUSAL_ERLANG_CLOCK_V1",
      "config_sha256": "<exact SHA256 of EXECUTION_PLAN.json>",
      "files": [
        {
          "path": "implementation/dispatch.py",
          "bytes": "<integer>",
          "sha256": "<64 lowercase hex>",
          "role": "code"
        }
      ],
      "preparation_receipt": {
        "path": "PREPARATION_RECEIPT.json",
        "bytes": "<integer>",
        "sha256": "<64 lowercase hex>"
      }
    }

필수 원칙:

- files의 role은 code, input, contract, previous_result이다.
- 모든 path는 해당 unit 내부의 정규 relative path이며 symlink/경로 탈출을 허용하지 않는다.
- 실제 bytes와 SHA256을 모두 대조한다. code에는 launcher 자신도 포함한다.
- mode entrypoint는 명시적으로 code로 pin된 .py여야 한다.
- code에 .so/.c/.h도 넣을 수 있다. 모든 code 파일은 원래 relative layout대로 EXECUTED_SOURCE에 복사한다.
- 따라서 implementation/libclock_kernel.so는 EXECUTED_SOURCE/implementation/libclock_kernel.so에 존재한다.
- native library는 실제 pin된 바이트를 그대로 복사한다. dispatcher가 컴파일하거나 native qualification을 새로 선언하지 않는다.
- configs/pins의 hash 순환을 만들지 않는다. pins가 config SHA를 소유하고, actual pins SHA는 PRE_EXECUTION과 source authority가 기록한다.

PREPARATION_RECEIPT의 필수 항목은 다음과 같다.

    {
      "no_prior_local_science_before_first_worker": true,
      "prior_local_science_attempt_count": 0,
      "metadata_code_preparation_cpu_s": null,
      "missing_prior_local_science_attempts": false
    }

이는 첫 worker 이전의 역사적 attestation이다. 이후 attempt가 없다는 뜻으로 재사용하지 않는다. 이후 실행은 runs의 실제 receipt로 누적한다. metadata/code preparation의 미측정 CPU를 0으로 대체하지 않으며, publication/remote Wolfram의 비용과 새 scientific worker+coordinator 예산을 구별한다.

## 실행 snapshot과 argv

각 실행은 unit/runs/RUN_ID를 create-only로 만들고 implementation/.cr_clock_task_lease를 create-only로 획득한다. lease에는 실제 PID·run ID·nonce가 있으며, 정확한 소유자가 확인된 경우만 해제한다.

source copy layout:

    runs/RUN_ID/
      RESOURCE_ADMISSION.json
      EXECUTED_SOURCE/
        implementation/...
        <pinned contract relative paths>
        _admission/
          EXECUTION_PLAN.json
          SOURCE_PINS.json
          PREPARATION_RECEIPT.json
      PRE_EXECUTION.json
      stdout.txt
      stderr.txt
      payload/                         # worker가 직접 생성
      DISPATCH_RECEIPT.json

placeholder 의미:

| Token | 실제 값 |
|---|---|
| {unit} | 원래 새 unit의 absolute path |
| {output} | create-only run root |
| {run_id} | 현재 고유 run ID |
| {snapshot} | 현재 run의 EXECUTED_SOURCE |
| {config} | snapshot/_admission/EXECUTION_PLAN.json |
| {pins} | snapshot/_admission/SOURCE_PINS.json |

첫 script는 항상 EXECUTED_SOURCE의 복사본을 현재 Python -B로 실행한다. shell을 사용하지 않는다. PYTHONPATH를 제거하며 user site를 사용하지 않는다. import는 frozen implementation 경로를 기준으로 구성해야 한다.

input 및 previous_result는 원래 unit의 고정 파일을 사전·사후 hash로 확인한다. worker도 실제 load 시 pin을 확인해야 한다. 이것을 입력 복사본에서 실행했다고 주장하지 않으며, pre/post hash만으로 순간적인 변경 후 복원을 수학적으로 배제한다고 주장하지 않는다. root는 해당 input을 immutable로 관리한다.

{output}는 run root이므로 root worker가 payload를 exist_ok=False로 생성할 수 있다. reference wrapper의 runpy는 같은 worker 프로세스 안에서 실행되므로 CPU를 별도 child로 중복 계산하지 않는다.

## CPU·wall·thread 제어

workers + 이 launcher coordinator의 새 로컬 비용만 60초 envelope에 속한다.

- stage별 worker 비용: controls5, primary30, independent15, plot5.
- coordinator 누적2.
- R7 unused3은 예약 상태로 남는다.
- 이전 direct attempt의 worker/coordinator 측정 비용을 모두 포함한다. 실패·timeout도 차감한다.
- runs 바로 아래 디렉터리에 receipt가 없거나 비용이 bool/음수/NaN/inf/unknown이면 UNKNOWN_PRIOR_ATTEMPT_BUDGET으로 차단한다.
- nested control fixture의 receipt를 별도 실제 dispatch로 중복 계산하지 않는다.
- historical H1/C23E/HeI/HeIII/REI/WU/HE 예산을 새 60초로 이전하지 않는다.

실제 남은 stage/global 예약의 정수 하향값을 worker RLIMIT_CPU로 설정한다. worker에 전달하는 환경 변수는 다음과 같다.

    CR_CLOCK_WORKER_CPU_CAP_S=<actual admitted remaining integer seconds>

OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/BLIS thread 환경은 모두 1이다. OMP_DYNAMIC=FALSE, OMP_NESTED=FALSE, OMP_MAX_ACTIVE_LEVELS=1이다. worker RLIMIT_AS는 512 MiB, core dump는 금지한다.

dispatcher는 약 20 ms 간격으로 자기 child의 CPU와 wall/coordinator budget을 관찰한다. worker limit 약 0.05초 전, coordinator limit 약 0.02초 전, wall limit 약 0.5초 전에 중단 경계를 둔다. RLIMIT_CPU는 별도 kernel hard guard다. 실제 측정이 cap을 넘으면 실패로 보존하며 제한을 늘리지 않는다.

계측은 actual RUSAGE_CHILDREN delta와 fresh coordinator process_time이다. coordinator 비용은 source verification·snapshot·polling·종료·최종 prior accounting·lease cleanup 뒤에 샘플링한다. 마지막 receipt serialization/write 및 print는 그 샘플 뒤에 있으므로 receipt에 측정 경계를 명시한다. 이 범위 밖 CPU를 측정된 0이라고 보고하지 않는다.

fresh CLI 한 번이 coordinator 한 번이다. 다른 작업을 먼저 실행한 persistent Python에서 run()을 호출하면 process_time의 의미가 달라지므로 사용하지 않는다.

## 보수적 RAM admission

현재 root의 C4 관찰은 8 GiB cgroup에서 memory.current가 높지만 큰 inactive file cache가 있는 경우였다. 단순 memory.max-current만을 free RAM으로 해석하지 않는다. 동시에 active cache나 slab을 자유롭게 회수할 수 있다고 가정하지도 않는다.

매 실행 전에 실제 /sys/fs/cgroup/memory.stat, memory.max, memory.current, memory.events, cpu.max, actual affinity, /proc/meminfo 및 coordinator RSS/VmSize를 읽는다.

    clean = max(0, inactive_file - file_dirty - file_writeback - shmem)
    hypothetical_current = max(0, memory.current - clean)
    group_available = max(0, memory.max - hypothetical_current)
    available = min(host MemAvailable, group_available)
    after_reserve = available - memory_reserve_bytes
    admit iff after_reserve >= 512 MiB

raw memory.stat 전체와 공식·실제 숫자를 RESOURCE_ADMISSION에 저장한다. active_file 및 slab_reclaimable은 관찰값으로만 남고 가용량에 더하지 않는다. 이는 cache reclaimability estimate이며 raw free memory 또는 무오류 보증이 아니다. cache dropping, unrelated process kill, system-wide tuning은 하지 않는다.

## 실패·unknown·소유권 경계

- fresh run directory가 만들어진 뒤의 config/pin/admission/worker 실패는 actual coordinator/worker 측정치와 함께 receipt로 남긴다.
- 같은 run path를 새 receipt로 덮어쓰지 않는다. 안전하지 않거나 중복인 path는 refusal을 stderr로 반환한다.
- metadata refusal을 성공한 scientific run 또는 0 CPU라고 바꾸지 않는다.
- child는 start_new_session으로 이 launcher가 만든 새 process group에 들어간다.
- failure/timeout에서는 그 소유 group만 TERM/KILL한다. unrelated PID/group을 종료하지 않는다.
- owned group의 reaping/accounting이 불명확하면 worker CPU를 null로 남기고 UNKNOWN_OWNED_CHILD_ACCOUNTING으로 표시한다. lease를 보존하여 새로운 dispatch가 비용을 0으로 간주하지 못하게 한다.
- 마지막 prior ledger 재조회에서 unknown이 발견돼도 runtime PASS를 반환하지 않는다.
- 실패 payload·stdout·stderr·PRE_EXECUTION과 원 비용을 삭제하지 않는다.

PASS는 프로세스 실행·runtime 상태의 의미다. 과학적 정확성, source qualification, independent review, N6/N7, 게시·백업·DAG는 자동 승격하지 않는다. DISPATCH_RECEIPT에도 각각의 소유 경계를 별도 필드로 남긴다.

## Root의 다음 단계

1. 이 파일을 unit/implementation/dispatch.py로 복사한다.
2. ROOT의 실제 C5 code/native binary와 selected15 same-byte inputs를 배치한다.
3. EXECUTION_PLAN, PREPARATION_RECEIPT, 코드·입력·계약의 실제 hash/size로 SOURCE_PINS를 생성한다.
4. 코드·계약·runtime 독립 검토 및 node preflight 후 source를 게시한다.
5. 실제 worker 실행은 root가 새 고유 run ID로 수행한다.

이 후보 작성 과정에서는 위 1–5를 실행하지 않았다.

