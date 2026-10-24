# N5 neutral elastic 독립 C9

## 판정과 독립성

검토자 판정은 **PASS_SCOPED_AFTER_REVIEWER_DIAGNOSTIC_DEFINITION_ALIGNMENT**다. 초기 진단 노름 분류 정정은 아래에 공개하며 최종 consumer 채택은 root의 실제 disposition에 맡긴다. 원 FAIL 결과와 실행 소스는 보존했다. 정정 뒤 미해결 과학 차단은 0이다.

선택은 chi1.5/3, R80, N2048 두 경우이며 실제 grid2480/active2479 nodes다. 각각 **14개 물리 RHS를 모두 독립 solve하여 총28개**다. u_s/u_p/u_entry/t/r_s/r_p 여섯, 독립 reference u_s/u_p를 RHS로 사용한 v_s/v_p 둘, EE/세 이온/Hneutral/Heneutral signed bath 여섯을 포함한다. t/v_s/v_p를 bound RHS로 대신하지 않았다.

생산 scientific module import0. 저장된 새 K의 binary64 값을 그대로 Decimal70으로 올려 별도 Thomas factorization을 사용했다. Raw MTCS 별도 parser, mp70 native PL 보간/단위/nu/D/mu/EE anchor 비율을 독립 확인했다. H/He 선택 edge 수는 첫 경우143/136, 둘째144/134다. 각 knot 주변과 전체 구간의 분산 표본을 포함한다.

Conductance에서 Q/K를 별도로 구성했다. diag(pi)K의 quadratic form은 양의 q-edge 항, 내부 edge 차이 제곱, 비음 CE killing 항의 합이므로 이 유한 chain에서 SPD와 동치다. 원 pi/grid/source projections/네 기존 bath RHS/CE RHS의 exact reuse도 확인했다. 기존 PR103 solve·old replay·source projection·source quadrature·새 ODE는 모두0이다.

## 실제 수치

| 검토량 | 관측 최대 | 적용 gate |
|---|---:|---:|
| 28개 해 norm-relative 차이 | 3.0616143171e-11 | 5e-10 |
| 실제 t 차이 | 3.0047443515e-12 | 5e-10 |
| v_s 차이 | 1.9132577897e-12 | 5e-10 |
| v_p 차이 | 5.3977545873e-13 | 5e-10 |
| Decimal reference backward residual | 8.78e-70 미만 | 1e-60 |
| MTCS D 상대차 | 1.80e-15 미만 | 5e-10 |
| MTCS mu 상대차 | 9.07e-13 미만 | 5e-10 |
| 새 conductance 상대차 | 2.33e-15 미만 | 5e-10 |
| Reference partition 절대차 | 4.88e-11 미만 | 2e-8 |
| Reference signed energy scaled residual | 4.39e-11 미만 | 2e-8 |

새 no-CE MFPT는 별도 tail-sum 식으로 확인했다. 기존 MFPT를 다시 풀지 않고 저장값으로 Told/(1+delta) <= Tnew <= Told를 확인했다. CE probability의 일반 단조성을 주장하지 않는다.

## 원 실패와 제한 정정

- v1: mpmath import 환경 실패, coefficient0/RHS0, workerCPU0.082568s. 보존된 PR103 mpmath1.3.0 wheel SHA256 a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c를 그대로 복사해 zip import했다. 설치/네트워크/이전 oracle 재실행0.
- v2: 28 RHS 완료, 원118checks 중114PASS와4diagnostic FAIL. 검토자가 두 binary64 reward 식의 차이를 cancelling signed net norm으로 나눈 값에 generator2e-13을 적용했다. 2.24–6.85e-13이었으며 원 RESULT와 코드/벡터/receipt는 변경하지 않았다.
- v3: 이전 완료 run을 가리키는 own stale lease 때문에 child 전에 거절. Exact run/terminal receipt/PID 부재를 확인해 그 lease만 정리했다. 잔존 원인은 NOT_ESTABLISHED, 다른 process/owner lease 변경0.
- v4: **완료28solve/MTCS 계수 평가를 반복하지 않고** 저장 네 reward series의 산술만 Decimal70으로 구성했다. Net 비교에는 동결 independent5e-10, -Q^T E의 absolute-term gross scale에는 동결 generator2e-13을 적용했다. 최대 net-relative4.4405866659e-13, gross-relative1.4259486130e-19로 모두PASS.

허용값·물리식·입력·생산 코드를 바꾼 것이 아니다. 서로 다른 노름 범주의 gate를 옮겨 적용한 reviewer 진단을 분리했다. 원 FAIL을 PASS로 덮어쓰지 않았다. 사전 patch 형식 오류1회도 file mutation/child0인 작성 도구 실패로 별도 기록했다.

## 비용·파일·범위

실제 attempts4, child3(환경실패1/28RHS1/4reward산술1). WorkerCPU합 **1.428695s**, coordinator0.011905434s, launchwall합1.507701851s. 실패 비용을 포함한 10CPU/40wall allowance를 초기화하지 않았다. WorkerCPU1/coordinatorCPU8/native1/AS512MiB; 실행 시 quota8/memory8GiB/affinity0–8/OOM0를 관측했다. Own lease는 마감 시 제거됐다.

Controls+primary1.069652s를 포함한 새 unit 누적2.498347s, 상속29.870022114s 포함 known lineage32.368369114s다. 외부 NCP/금전은 null 또는 UNOBSERVED다. 모든 attempt의 DISPATCH_RECEIPT.json에 top-level worker_cpu_s가 있다. Root 전달 subtree 안에는 네 receipt가 각각 한 번만 있다. 원 intake는 unit 밖이다.

Dense reference vectors와 raw MTCS는 private canonical에만 포함한다. 공개물은 집계 보고서와 코드다. C9_REPORT.json은 실제 paths/pins/metrics/failures를 모두 묶는다.

이것은 leading heavy-neutral 모형의 유한 두 chain 검증이다. Paired neutral-induced CE increment의 finite-grid 안정성은 CE continuum 오차 인증이 아니다. 일반 CE grid 차이가 작은 neutral signal과 비슷할 수 있다는 사실을 숨기지 않는다. 2R/r recoil 및 theta/(rE) 지표는 별개 근사 진단이며 global error certificate가 아니다.

MTCS를 event hazard/count로 읽지 않는다. First entry를 irreversible assimilation/Maxwellization으로 승격하지 않는다. Missing isotope/rate=null. N5 parent OPEN, N6/N7 비활성, 전체 thermal/UV/stars/nuclear 완료 아님. global_error_bound=null, global_completion_percent=null.

EXECUTION: scoped C9 완료, 실패 보존. PUBLICATION: root 소유. BACKUP: root 실제 receipt 필요. DAG: N5 neutral child 심사만.
