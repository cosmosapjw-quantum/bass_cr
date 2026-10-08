# F1 native admission bounded execution plan

상태: **READY_FOR_USER_RUN_AUTHORIZATION, NOT AUTHORIZED YET**

구현 commit/tree:

```text
8236887dd8869de57522d5c87a48972f287969fe
d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae
```

F1은 performance benchmark가 아니라 15 representative archived query와 5 metric sentinels의
새 native engine parity admission이다.

## Expected workload

- representative queries: 15
- 각 query: frozen 11-resolution ladder 전체 screen
- representative raw evaluations: 165
- metric sentinel: z=-12,-6,0,6,12의 center ± epsilon, 총 15 exact-time provider queries
- sentinel provider는 first qualified adjacent pair에서 멈춘다.
- 실제 raw-evaluation 총수는 sentinel selection에 따라 달라진다.
- worker pool 사용 안 함; F1은 serial admission.
- BLAS/OpenMP thread는 1 유지 권장.

Historical TP2D는 4,442 raw attempts에 약 44,625 s가 걸렸지만, F1 query mix는 full-ladder
h=4까지 의도적으로 포함하므로 단순 평균으로 runtime을 보장하지 않는다.

## Proposed wall budget

권고 `max_wall_seconds = 7200` (2 h).

이 값은 실행 성공을 보장하는 예측이 아니라 fail-closed 상한이다.
runner는 각 expensive operation 사이에 remaining budget을 검사한다.
한 native call이 진행 중일 때는 budget을 조금 초과할 수 있다.

## Cost gate

RUN_AUTHORIZATION은 다음 중 하나가 필요하다.

1. `spending_limit_krw` 명시, 또는
2. 이미 과금 승인을 받은 기존 host라면 `prepaid_host_approved=true`.

현재 문서는 비용 권한을 만들지 않는다.

NCP 공식 요금표의 High CPU-g3 64 vCPU / 128 GiB 항목은 시간당 3,192원(VAT 별도)으로
표시된다. 실제 계정/리전/디스크/IP/네트워크 과금은 콘솔이 authoritative하다.

2시간 wall budget을 승인할 때는 server-rate 이외의 부대비용 여유까지 포함한 cost cap을
사용자가 직접 선택한다.

## Execution conditions

실제 실행 전에:

- remote branch contains exact implementation commit/tree.
- F0_DURABLE_CLOSURE passes.
- source manifest passes.
- TP2D archive identity passes.
- approved host/workspace has enough free disk.
- exact pinned Python numerical environment is available.
- RUN_AUTHORIZATION matches exact implementation commit/tree.
- output path is fresh/create-only.

실행 중 threshold, representative set, compiler flags, ladder를 변경하지 않는다.

## Outputs

성공:
`F1_ENGINE_ADMISSION_PASS`

실패는 contract의 distinct status를 그대로 반환한다.

필수 evidence:
- ENGINE_BUILD.json
- ENGINE_IDENTITY.json
- ENGINE_ADMISSION.json
- REPRESENTATIVE_PARITY.json
- METRIC_CONNECTION_PARITY.json
- PROGRESS.jsonl
- RETURN_REPORT.json
- FOCUSED_TESTS.log

실행 후 NCP evidence publication policy를 사용해
`execution_evidence/F1/<run_id>/`에 sanitized evidence를 push한다.

## Stop boundary

F1 완료 후 F2를 자동 실행하지 않는다.
F2 16/32/48/60-worker calibration은 별도 authorization이다.
