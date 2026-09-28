# 공유 NCP 자원 및 DAG 결정

## 직접 확인한 프로젝트 자료

| 프로젝트 | 확인한 원격 snapshot | 이번에 읽은 근거 | 현재 live PID 확인 |
|---|---|---|---|
| bass_cr F1-R2 | control 25ba5e6eb71285d22d06bb884e77b806bb40735a; executable f1d69165c6d1e799d9474db23166cb665880576f | R2 runner, 원 engine builder, 실행 handoff, 원 TP2D archive | 하지 않음 |
| BASS_HE | validation/ncp-c64g3-dr11h-20260928 / 37cde4c100b2b867dfc278e810f68d71f39e1d12 | RUN_PROFILE_DESIGN.json; 56-action contour DAG | 하지 않음; 설계값을 실제 allocation으로 취급하지 않음 |
| WU088_HH | codex/r31t-ncp-m3-production-screen / a49a704bf84fa86c34c16cd26a631dfabfbbc5ab, PR12 | M3A 성능 결과, BASS 동시 pool로 M3B 중단 기록 | 과거 동시 간섭은 문서화; 현재 live PID는 미확인 |

사용자가 말한 세 Codex 세션의 전체 PID↔repo 대응을 확인한 것은 아니다. 특히 Codex 대화/편집 세션이 활성이라는 사실과 세 scientific pool이 동시에 계산 중이라는 사실은 다르다.

## 중요한 새 관측

WU088_HH PR12는 B160 M3A에서 다음 median pairs/s를 보고한다: 64×1=1.2543, 32×2=1.2208, 60×1=1.1755, 32×1=0.9037. 64×1 두 batch의 실제 effective CPU parallelism은 56.48,54.56이며 throttling delta는 0이다. 이는 HH 해당 bounded workload에서의 결과이지 bass_cr evaluator의 성능 수치가 아니다.

M3B는 같은 VM/session cgroup에 BASS F1의 큰 pool이 들어왔기 때문에 throughput/cgroup 측정 오염으로 중단됐다. 이를 `RUNTIME_ENVIRONMENT_ERROR`로 보존했고 M3B profile ranking은 승인하지 않았다. 따라서 이번 연구에서 동시 실행 간섭은 단순 가정만이 아니다. 다만 지금 시점의 총 부하를 알려면 live inventory가 필요하다.

## D1. 즉시 운영 정책

현재 동결 CR R2는 affinity>=64와 workers60을 전제한다. 이를 18CPU taskset 안에 넣으면 host gate에서 실패한다. 실행 중인 코드/affinity/그랜트는 이번 연구에서 변경하지 않는다.

1. 새 대규모 workload의 시작을 한 명의 host coordinator가 조정한다.
2. 성능 순위 비교(calibration/benchmark)는 독점 측정 구간을 사용한다. 서로 같은 session cgroup의 CPU counter를 각자의 성능으로 계산하지 않는다.
3. CR의 현재 60-worker admission 구간과 HH의 M3B benchmark를 겹치지 않는다. 다른 두 Codex 세션은 문헌·코드·가벼운 검증 작업을 계속할 수 있다.
4. 이미 시작한 job을 임의 kill/SIGSTOP하지 않는다. 실제 PID/허가/remaining wall을 읽고 owner와 runner의 checkpoint/종료 경계에서만 조정한다. 기존 wall clock을 resource queue 이유로 몰래 재설정하지 않는다.
5. 결과의 수치 품질과 성능 측정 품질은 분리한다. 동시 실행으로 timing sample이 오염돼도 그 자체가 numerical parity FAIL은 아니다.

## D2. 다음 공유-runtime 설계

제안 기본값은 모든 scientific jobs 합계 56 CPU slots, 나머지8을 coordinator/OS/가벼운 agent 활동에 예약하는 것이다. 128GB 상품명 대신 visible ancestor cgroup와 OS의 실제 제한 bytes를 사용한다.

초기 RAM pool 예산은 min(96GiB,0.75×M_effective)다. 실제 MemAvailable와 계층별 memory.current/headroom이 더 작으면 낮춘다. 세 CPU-heavy job에 동일 우선순위라면 (18,18,20)과 각 약32GiB를 candidate grant로 둘 수 있다. 이는 최적 실측값도, 현재 실행에 적용한 설정도 아니다. 다음과 같이 실제 worker RSS에 따라 줄인다.

    W_i = min(CPU_grant_i / actual_threads_per_worker_i,
              floor((M_grant_i − M_controller_i)/(1.5 R_peak_i)),
              ready_tasks_i, validated_code_cap_i).

R_peak를 모르면 그 값이 0이라고 가정하지 않는다. 별도 승인된 작은 resource pilot 또는 신뢰 가능한 해당 task-class 측정이 필요하다. HH의 B192 peak를 CR의 h4 scratch에 이식하지 않는다.

공통 broker의 필수 경계:

- host identity/capacity와 job resource lease 분리.
- 원자적으로 모든 CPU+RAM grant를 예약하고, task boundary에서 유휴 토큰 반환.
- 세션이 죽었다는 이유만으로 즉시 grant를 회수하지 않고 자식 process/cgroup가 비었는지 확인.
- machine numerical-cache identity와 worker수/PID/wall budget을 분리.
- host-wide 누적 비용 원장 하나. 세 작업의 개별 금액 숫자는 VM 총비용을 자동으로 제어하지 않는다.
- 각 scientific job은 독립 cgroup/lease로 launch하고 PID descendants를 식별한다. CPU quota, memory.high/max는 governor 보조장치이며 OOM을 graceful checkpoint로 취급하지 않는다.
- 기존 deadline 안에서 stop-scheduling → persist → child reap/join → final receipt 순서. SIGKILL이면 finally가 실행된다는 보장은 없다.

각 code의 자기 메모리75% 예산을 세 번 허용하면225%가 된다. 서로 다른 repo의 launcher들이 보는 `/proc/meminfo`는 같은 자원이며, 독립적인 예산이 아니다.

## D3. 정확성과 재현성

CR: independent exact-time/resolution tasks 간에만 병렬화. Native 내부합산, q/h 선택 순서, dtype, error gate, basis identity를 유지한다.

HE: 서로 다른 contour/action을 병렬화할 수 있으나 동일 contour의 sheet/branch continuation 순서는 유지한다. design은64-sample에서32-panel을 파생하는 shortcut을 금지한다. 본 연구는 이를 우회하지 않는다.

HH: 이미 통과한 H0/foreign exactness를 재활용하되, x86 long-double padding bytes와 수치 값 동일성을 혼동하지 않는다. M3B ranking은 별도 exclusive sample로 닫는다. 과거 이미 통과한 M3A 전체를 반복할 필요는 없다.

## D4. 다음 CR 수정의 우선순위

A. resume numerical identity와 운영 receipt 분리: fresh output path만 바뀌어도 engine identity가 달라지는 현재 결함을 먼저 수정한다.
B. resource lease를 허용하도록 ≥64 host guard와 per-job worker grant를 분리한다. cgroup ancestor 제한을 읽는다.
C. metric tasks의 lazy prefix를 쓰되 representative full11 screens는 유지한다. historical branch가 유지될 때297→201.
D.27개 same-center node를 분리해 공통부분 추출. 현재594→54 same-center 호출.
E. exact planar symmetry를 근거로 even14를 별도 candidate로 승인. 기존 full18 evidence를 변경하지 않는다.
F. M4가 닫힌 동일 finite input에서는 CF4를 mandatory gate가 아닌 cost/accuracy challenger로 분리한다. 새로운 basis/time/impact point는 별도 평가 대상이다.

A/B/C/D가 먼저이며 E/F는 새 관측량·기저 scope를 명시한 후 수행한다. 증거를 재사용하는 것과 새로운 independent reference를 추가했다고 주장하는 것은 다르다.

## 남기는 gate와 줄이는 gate

단순 byte rehash/repackage/환경준비를 매번 새 과학 노드로 세지 않는다. Cache-only finite-span postprocessing은 propagation과 분리한다. 원래 full-basis, radial/angular convergence, asymptotic population, all-bound completeness, b integration의 물리적 조건은 생략하지 않는다.

필요한 proof/certificate가 오차 예산을 실제로 지배하면 expensive sweep을 축소할 수 있다. 현재 residual reconstruction 및 localized far-field tail certificate는 아직 구현/수치검증 전이다.

## ETA

이전 대화의18–35h / 중앙24–28h final audit ETA와 ±20%로 좁힐 수 있다는 예측은 신뢰 가능한 workload count 및 후반 convergence 증거가 없었다. 이를 현재의 검증된 ETA로 사용하지 않는다. 세션 간 자원 간섭까지 있으므로 measured task-class cost, DAG critical path, grant 일정, 아직 결정되지 않은 basis/b-grid 확장이 확정될 때 단계별 ETA를 다시 계산한다.
