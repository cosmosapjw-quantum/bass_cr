# C21M 공유 실행 운영 계약

`shared_runner.py`는 사용자가 제공하는 새로운 signed full-Frobenius 초기조건 목록만 실행한다. 원 C21L 81개 grid를 자동으로 만들거나 실행하는 경로가 없다. 물리 계산은 `builder.IndependentStressBuilder` 및 `builder.solve_case`에 위임하므로 원 40성분 RHS, FP64, quadrature, DOP853 `n=101, rtol=3e-11, atol=3e-13`은 builder의 고정 계약에 따른다.

입력 형식은 다음과 같다. `S0`, `Pm0`, `Pr0`는 모두 부호를 유지하는 full Frobenius 좌표이며, scalar norm은 이들의 절댓값이다.

```json
{
  "schema": "C21M_GRID_V1",
  "run_id": "new_independent_stress_run",
  "cases": [
    {"case_id": "radiation_only", "S0": 0.0, "Pm0": 0.0, "Pr0": 0.001}
  ]
}
```

`--plan-only`는 입력·source identity와 현재 affinity, 보이는 cgroup v1/v2 및 ancestor의 CPU quota·메모리 한도·여유를 읽고 계획을 stdout으로 내보낸다. output과 lease directory를 생성하지 않으며 과학 ODE를 적분하지 않는다. 원 source의 plotting import가 만드는 선택적 cache는 임시 `MPLCONFIGDIR` 안에 제한하고 종료 시 삭제하며 호출자의 환경값은 복원한다. 실제 실행은 별도 새 output에 `MANIFEST.json`을 만들고 Python·NumPy·SciPy 버전, source/builder/runner/resources SHA256, 입력 bytes 및 canonical case 목록을 결속한다. 각 worker는 준비 완료를 알리기 전에 자신의 builder source identity와 세 실행 파일의 SHA256을 coordinator manifest와 다시 대조한다. 불일치하면 case를 시작하지 않는다.

각 worker는 single-thread 환경에서 하나의 immutable 연산 template를 재사용한다. CPU55를 제외하고 coordinator도 CPU 1개·256 MiB 예산으로 계산한다. worker 예산은 512 MiB이며, 이는 2,592개 quadrature node의 FP64 buffer 64개와 101개 저장 시점의 scalar channel 128개에 Python·NumPy·SciPy 및 allocation 여유를 포함한 보수적 계획값이다. OS가 강제하는 per-process memory limit이나 측정된 최대 메모리 주장이 아니다. 각 worker의 실제 process high-water RSS와 반환 시 관측 thread 수를 receipt에 저장한다. 메모리 reserve는 관측된 전체 한도의 1/8과 1 GiB 중 큰 값이다.

공유 `cpu_N.lock`의 nonblocking `flock`을 존중하며, per-CPU 실제 부하와 가능한 cgroup CPU 사용량에서 이 실행의 process CPU 사용량을 뺀 값을 함께 관측한다. 외부 부하·quota·메모리 여유가 악화되면 새 dispatch를 줄이고 이미 실행한 case는 유지한다. cgroup v1의 cpuacct가 별도 mount인 경우 해당 CPU quota row에 usage가 없을 수 있으며, 이 경우 per-CPU 부하·quota 상한을 사용한다. cooperative lease는 동일한 directory를 사용하는 실행자 사이의 협조 계약이다. 관리되지 않은 다른 프로세스는 관측만 하며 변경·종료하지 않는다.

각 worker의 queue 크기는 1이고 coordinator는 worker당 최대 1개 in-flight case만 dispatch한다. worker 수는 가용 CPU·메모리와 남은 case 수로 제한한다. 초기 자원이 없거나 신규 부하가 증가한 경우 지정 wall budget 안에서 기다린다. budget 만료 후 새 dispatch는 중단하고 진행 중인 case에는 별도 drain grace를 준다. 이후 정리 대상은 이 coordinator가 생성한 process 객체뿐이다. 다른 owner의 프로세스와 파일은 건드리지 않는다.

## 재개

`--resume`은 manifest identity가 완전히 같은 경우만 허용한다. `COMPLETE.json`은 `RESULT.json`과 `history.npz`의 SHA256을 결속하며 둘을 모두 확인한다. 완료 raw는 다시 실행하지 않는다. reservation만 있고 `STARTED.json`이 없는 case만 미시작으로 재개한다. 시작 기록이 있으나 완료 seal이 없는 case는 `INTERRUPTED_NO_AUTORETRY` 또는 `INTERRUPTED_UNSEALED`로 보존한다. 실패 case도 자동 재시도하지 않는다. completed receipt나 raw가 달라지면 해당 재개의 promotion을 차단한다.

운영 test double 결과는 `operational_test_double=true` 및 `OPERATIONAL_TEST_DOUBLE_NO_SCIENCE`로 표시된다. `test_shared_operations.py`의 세 focused 그룹은 자원 계산·lease contention, resume/hash/create-only, 실제 spawned fake-worker queue·부하 축소·plan-only 무생성·완료 raw 무재실행을 점검한다. 이 검사는 과학 수치 검증이나 성능 벤치마크가 아니다.

## NCP

현재 대화에서 `/usr/bin/ssh`는 존재하지만 `/home/cosmosapjw/.ssh/ncp_key`가 없다. 키 내용은 읽지 않았다. 따라서 이 작업자의 NCP 접속·원격 resource probe·과학 실행은 `NOT_RUN`이다. 운영자가 해당 키를 가진 환경에서 접속한 후 명목 64 logical CPUs/128 GB와 실제 admission 결과를 구분한다.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

게시된 tested content commit의 별도 checkout에서 다음 shell을 사용한다. `C21M_CONTENT_COMMIT`, repo/grid/output의 실제 절대 경로는 최종 인계문에 결속한다. 이미 완료된 sandbox grid를 같은 science 재실행 목적으로 넣지 않으며, 미완료 또는 승인된 신규 grid를 사용한다.

```bash
export C21M_CONTENT_COMMIT=TESTED_PUBLISHED_CONTENT_SHA
bash research/cr_c21m_independent_stress_20261021/ncp_run.sh plan REPO_ABSOLUTE GRID_ABSOLUTE NEW_OUTPUT_ABSOLUTE
bash research/cr_c21m_independent_stress_20261021/ncp_run.sh run REPO_ABSOLUTE GRID_ABSOLUTE NEW_OUTPUT_ABSOLUTE
```

공유 lease directory가 현장 표준과 다르면 `C21M_LEASE_DIR`를 그 표준에 맞춘다. `C21M_WORKERS=64`는 상한 요청이며 64 workers 실행을 보장하지 않는다. 실제 new-task 수와 coordinator 비용으로 줄어든다. 모든 실행에서 `global_error_bound=null`을 유지한다.
