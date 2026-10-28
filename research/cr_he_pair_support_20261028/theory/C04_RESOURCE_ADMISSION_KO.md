# C4 실행 DAG와 자원 admission

Frozen new budget는40CPU-s다. Unit root `BUDGET.json`에 모든 actual attempt를 append하며 coordinator/worker CPU와 보수적 tail을 합산한다. 과거 PR112 잔여35.289821 또는 다른 owner 예산은 이전하지 않는다. Metadata/provider/publication/remoteCAS CPU는 unmeasured/null로 별도다.

실행 순서는 `probe -> primary/controls -> independent -> plot -> C9 -> science closure`이며 science workers는 serial이다. Root만 bounded runner를 실행한다. Production author와 independent oracle author는 별도 파일을 작성했고 과학 import/실행을 하지 않았다. Independent C9 reviewer는 production 작성자가 아니다.

초기 reservation 계획은 probe2,primary12,controls6,independent14,plot6 CPU-s다. 각각을 시작할 때 `current actual cumulative charge + requested reservation <=40`을 확인한다. 개별 reservation의 미사용분은 같은 열린 단위의 잔여에 남지만 closed prior unit 예산은 사용할 수 없다. 실제 실패가 있으면 그 비용과 로그를 남기고 구체적 원인·수정 후 남은 예산 안에서만 별도 run ID로 재시도한다. 이미 PASS인 unchanged suite를 재실행하지 않는다.

각 worker는1native thread,512MiB address-space limit,50s wall limit과 reservation보다 작은 integer RLIMIT_CPU를 적용한다. 소유 process group만 timeout 시 종료한다. Source snapshot과 command/environment/input manifests를 함께 저장한다. measuredCPU에 microsecond rounding과0.05CPU-s tail을 더해 debit한다. 이는 측정 기반 보수적 accounting이며 preventive aggregate hard-cap의 완전한 증명이라고 주장하지 않는다.

Probe는 실제 Python/NumPy import와 version/RSS를 확인하는2CPU-s reservation이다. 이후 small4-bin exact optimization, 3201-atom sparse witnesses,5184+64independent comparisons, 저장 결과 plot으로 범위를 제한한다. 새로운 HPC/NCP job, dense pair-matrix, source fit·RR suite는 필요하지 않다.

Exact command template:

```bash
python3 implementation/run_bounded.py probe_v1 probe 2
python3 implementation/run_bounded.py primary_v1 primary 12
python3 implementation/run_bounded.py controls_v1 controls 6
python3 implementation/run_bounded.py independent_v1 independent 14
python3 implementation/run_bounded.py plot_v1 plot 6
```

실제 exit/status/cost와 어떤 명령이 실행됐는지는 runs의 RECEIPT/COMMAND/RESULT와 BUDGET이 권위다. 이 admission 문서만으로 예정 명령을 실행 완료로 세지 않는다. 종료 후 science_closed=true,추가 allowance0,잔여NONTRANSFERABLE,automatic_next_node=false를 고정한다.
