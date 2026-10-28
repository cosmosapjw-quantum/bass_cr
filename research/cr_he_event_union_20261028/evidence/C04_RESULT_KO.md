# C04 — 새 단위 bounded 실행 계약과 아직 실행되지 않은 상태

단위: `CR_PHYS02_HE_EVENT_UNION_V1`. 문서 작성 시 runtime 상태는 **NOT_RUN**이다. 이 문서 작업에서는 scientific worker, probe, plotting을 실행하지 않았고 `BUDGET.json`을 수정하지 않았다. 실제 C4 probe 및 후속 실행은 root의 frozen `implementation/run_bounded.py`가 순차 수행한다. 실행 후 추가되는 실제 receipt와 측정값이 이 사전 계획보다 우선하며, NOT_RUN 기록은 사전 시점의 상태로 보존한다.

## 별도 40 CPU-s와 planned reservations

새 cap은 40 CPU-s다. preparation/probe, worker, coordinator, 실패한 attempt, plotting 및 conservative tail을 같은 새 단위에 charge한다. 선행 PR111 및 그 이전·타 owner의 미사용 예산을 받지 않는다. 문서 작성 중 읽은 `BUDGET.json`에는 cap=40, charge=0, measured=0, tails=0, attempts=[], `OPEN_NO_SCIENCE_LAUNCHED`가 있었다. 이는 아직 launch가 없다는 ledger 관찰이며, 문서 작성·provider·게시 CPU가 0이라는 주장은 아니다.

| planned attempt | mode | reservation CPU-s | worker RLIMIT_CPU hard seconds |
|---|---|---:|---:|
| preparation / runtime probe | probe | 2 | 1 |
| saved-source primary | primary | 8 | 7 |
| exact fixture controls | controls | 4 | 3 |
| independent reference | independent | 6 | 5 |
| PNG+SVG scientific plot | plot | 12 | 11 |
| 계획 reservation 합계 | 순차 실행 | 32 | worker별 독립 limit |

위 합계와 cap의 차이 8 CPU-s는 아직 지출하지 않은 계획상 headroom이다. 실제 비용이나 확정된 transferable 잔여가 아니다. 최소 복구가 필요하면 그때의 실제 누적 charge와 별도 reservation으로 같은 40 CPU-s 안에서 결정한다. 실패 run을 지우거나 동일 output directory에서 덮어써 성공으로 만들지 않는다. 이번 단위 완료 후 자동 다음 과학 단위는 OFF다.

## Frozen runner의 실제 동작

runner는 `CR_UNIT_ROOT`로 단위를 고정하고, 새 `runs/<run_id>` 디렉터리를 create-only로 만든다. nonblocking file lock과 기존 RESERVED attempt 부재를 확인한 뒤 `charge + reservation <= 40` 조건을 검사한다. 실행 전 실제 reservation을 기록하고 canonical implementation 여섯 파일의 bytes·SHA를 `SOURCE_MANIFEST.json`과 `EXECUTED_SOURCE/`에 보존한다. worker는 canonical path에서 실행하고 종료 후 원본 source identity가 바뀌지 않았는지 확인한다.

native thread 환경변수 OPENBLAS_NUM_THREADS, OMP_NUM_THREADS, MKL_NUM_THREADS, NUMEXPR_NUM_THREADS, BLIS_NUM_THREADS는 모두 1이다. worker RLIMIT_AS는 536870912 bytes, 즉 512 MiB다. 이는 프로세스 가상 주소공간 limit이며 동일한 RSS 값이나 512 MiB 전체 host memory reservation을 주장하지 않는다. child RLIMIT_CPU는 floor(reservation−0.5) seconds이고 soft/hard 값이 동일하다. native BLAS 중첩 병렬과 새 병렬 worker fan-out을 사용하지 않는다.

`CR_BOUNDED_OUTDIR`, 단위별 `MPLCONFIGDIR`, `PYTHONDONTWRITEBYTECODE=1`을 전달한다. 한 번의 worker는 별도 owned process group에서 실행한다. wall timeout 50 s가 발생하면 그 process group만 SIGKILL하고 stdout/stderr 및 실패 상태를 수집한다. 이 timeout은 CPU reservation을 대체하지 않는다.

parent의 RUSAGE_SELF와 완료된 child의 RUSAGE_CHILDREN user+system CPU를 합산하고 microsecond 단위로 올림한 뒤 attempt마다 0.05 CPU-s tail을 더한다. receipt에는 worker/coordinator 측정, tail·rounding tail, charge, wall time, exit code, failure, source_unchanged, scientific_status 및 maximum worker RSS가 남는다. 실패·timeout·limit 초과도 charge한다. 실행 후 source가 바뀌거나 측정 charge가 reservation을 초과하거나 accepted scientific status가 아니면 PASS가 아니다.

coordinator의 후반 serialization과 전체 host 활동에 대한 엄밀한 aggregate preventive hard-cap 증명은 제공하지 않는다. runner는 `preventive_aggregate_hard_cap_proof=false`를 유지한다. publication/metadata/provider CPU와 remote CAS CPU는 unmeasured null이며 0으로 승격하지 않는다.

## C4와 후속 actual evidence 우선순위

현 단계에서 Python/numpy import, 512 MiB 수용, 실제 wall/RSS/CPU 또는 plotting 성공을 주장하지 않는다. root가 계획된 probe를 실행한 뒤 해당 `RESERVATION.json`, `COMMAND.json`, `RECEIPT.json`, stdout/stderr와 ledger를 C4 evidence에 추가한다. 이후 primary/controls/independent/plot의 actual RESULT·receipt가 각 단계 runtime 결과의 근거다. `PASS_SCOPED` plot status는 생성 코드가 정상 완료했을 때만 결과 파일에 나타난다.

PR110의 memory refusal·reclaim·EROFS·실패 control·plot_v1 비용 및 v2 복구, PR109/PR107의 memory·stale lease·고유 recovery, PR111의 preparation/worker 실패는 선행 영수증에 그대로 남는다. 이번 fresh reservation이 그 실패를 취소하지 않는다.

근거: `../CONTRACT.json`, 읽기 전용 `../BUDGET.json`, `../implementation/run_bounded.py`, `../inputs/PREDECESSOR_FINAL_RECEIPT.json`. 참고 중앙 baseline 28/88, 이 계획의 중앙 집계 효과 0. 각 실제 stage의 게시·이중 백업·최신 중앙 값은 stage receipt로 별도 기록한다.
