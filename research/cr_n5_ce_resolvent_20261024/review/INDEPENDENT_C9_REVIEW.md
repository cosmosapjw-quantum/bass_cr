# 독립 C9 최종 검토 — CE first-event resolvent

**판정: PASS_SCOPED_NATIVE_KNOT_FINITE_CHAIN. Blocking finding 0.**

Admitted gate는 `NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_FINITE_CHAIN`이다. 대상은 `GEOMETRIC_PLUS_NATIVE_CE_KNOTS_V1`의 실제 v3 결과이며, 전체 N4/N5의 완료 판정이 아니다. 원 point-grid v2의 18개 수렴 실패와 v1 원출력의 미복구 상태는 유지한다.

## 검토 대상과 독립성

Primary run: `n5_ce_resolvent_native_knot_primary_20261024_v3`. Input: `n5_ce_resolvent_native_knot_input_20261024_v3`. Native driver/CASE/manifest/R6 사전 게시: `21523c93583129763cc8b66f68091bd6e48e81ee` (root R1 통지). 실행된 snapshot과 최종 코드/입력의 정확한 byte identity, 18개 manifest 항목을 독립 확인했다. 이 중 과학 원입력은 14개이며 v2 engine/dispatcher는 변경되지 않았다.

Reviewer는 provider 원문 intake, R6 및 독립 검산을 담당했다. Production engine/driver 작성이나 primary 실행에는 기여하지 않았다. 독립 코드는 production/provider를 import하지 않고 저장된 binary64 bands, source arrays 및 원 CCC 표를 읽었다.

## 수치 gate

| 항목 | 관측 최대 또는 범위 | 동결 기준 |
|---|---:|---:|
| Generator scaled defect | 1.022691259e-16 | 2e-13 |
| Linear scaled residual | 9.465074789e-13 | 2e-12 |
| Partition absolute defect | 3.039690721e-11 | 2e-08 |
| Projection count relative error | 3.830880533e-16 | 2e-12 |
| Projection energy relative error | 3.145666838e-16 | 2e-12 |
| First-event energy relative residual | 1.102351892e-16 | 2e-14 |
| Probability range | 5.383172079e-11 … 0.9999999998535858 | [−2e−10, 1+2e−10] |
| max(uCE−w) | -3.519826259e-13 | ≤2e−10 |
| N2048/N1024 probability relative change | 0.000128109303628 | 0.005 |
| N2048/N1024 event-energy relative change | 1.51200364664e-05 | 0.01 |
| N2048/N1024 event-time relative change | 8.52292103661e-05 | 0.01 |
| R40/R80 probability relative change | 2.47269966623e-11 | 1e−5 |

8개 matrix-local gate, 24개 source projection/energy row, 36개 grid 비교 및 18개 boundary 비교가 모두 통과했다. 기존 11개 recovery-v2 controls는 재사용했고, native inclusion/source support/endpoints/dependency에 대한 변경 의존 단일 control만 추가 실행했다. 비교를 위한 tolerance 완화나 결과 clipping은 없다.

## 독립 exact-binary64 검산

Run `n5_c9_native_knot_binary64_20261024T074319028165Z_v1`에서 Decimal 80자리와 `Decimal.from_float`로 저장된 binary64 행렬·원자료를 정확히 올렸다. Finest R80의 두 chi, 세 source 및 2S/2P/sum을 확인했다. 4개 direct probability, 4개 energy, 4개 time, 6개 source-adjoint solve를 수행했다.

P_active 최대 상대차 5.982979214490492e-12, P_selected 5.982995241288738e-12, event energy 6.132895503893133e-12, event time **7.450640259390961e-12**이다. 최대값은 동결된 5e−10 기준 이하이다. Direct/adjoint 상대차 최대는 6.550180723e-76이다. 원 CCC 표와 native constants로 복원한 hazard 상대차는 최대 3.829166646e-16, source projection L1 상대차는 최대 6.585452505e-17이다.

8개 raw grid가 기존 point grid와 두 원 forward CE knot 배열의 정확한 합집합임을 확인했다. 같은 chi/N에서는 10eV 이하 grid와 source 배열이 bitwise 동일하다. 작은 cell의 최소 간격 9.4e−6eV에서 커진 조건화 오차도 위 독립 기준 안에 있었다. 원자료 Decimal reference arrays와 모든 실행/raw SHA256은 JSON에 수록했다.

## Finest R80/N2048의 전체 CE 결과

| chi | source z | P_active | P_selected | 평균 사건 입사에너지 (eV) | 평균 사건시간 (proper s) |
|---:|---:|---:|---:|---:|---:|
| 1.5 | 2.316 | 2.28426381167e-05 | 1.46424138727e-05 | 11.2588715619 | 594855.142768 |
| 1.5 | 2.479 | 2.26248968617e-05 | 1.45098546737e-05 | 11.2588715619 | 595320.576877 |
| 1.5 | 2.649 | 2.23878893156e-05 | 1.43693794965e-05 | 11.2588715619 | 595977.939777 |
| 3 | 2.316 | 3.47263185125e-05 | 1.45759766461e-05 | 11.2588822434 | 590986.258574 |
| 3 | 2.479 | 3.43617498045e-05 | 1.4443341811e-05 | 11.2588822434 | 591416.948538 |
| 3 | 2.649 | 3.39493970273e-05 | 1.43027477269e-05 | 11.2588822434 | 592034.61993 |

P_active의 분모는 원 W>q population이며 q-node로 투영된 질량도 포함한다. P_selected는 전체 원 0<W<10eV selected pulse population에 대한 확률이다. 원 W≤q는 이 first-before-entry 질문에 0을 기여한다. 이는 누락된 물리 rate를 0으로 놓는 것과 다르다.

Q는 column-population generator이고 G는 q node를 제거하되 경계로의 loss를 유지한 transpose이다. CE는 K=diag(h)−G의 양의 RHS 직접 solve로 구해 1−u_abs 소거를 피했다. Energy와 time은 각각 K r=E h, K v=u reward로 구했다. 두 채널 사건의 에너지는 Delta10.20435eV를 internal excitation으로 옮기는 첫 사건 ledger이며 후속 bath heating이나 radiative cascade는 계산하지 않았다.

초기 원자가 모두 10eV<Delta 아래에 있으므로 이 nearest-neighbor 사슬에서 성공한 경로는 동일한 첫 CE-active node를 통과한다. 따라서 고정 grid에서 조건부 사건 에너지와 채널 비율의 source 독립성은 구조상 자연스럽다. 사건시간에는 source별 접근시간이 더해져 source 의존성이 남는다. 기존 Markov 성질에 대한 설명이며 새로운 정리·실행으로 세지 않는다.

## 보존한 실패와 비용

v1은 local variable shadow로 1개 case 완료 뒤 중단되었고, workspace loss 뒤 정확한 코드/raw를 복구하지 못했다. 대화에 남은 실제 2Q/1complete/9RHS와 primary CPU0.279477s는 비용에 남기고 admission에서 제외했다. 원문 byte 검증을 한 것으로 재표현하지 않는다.

Recovery-v2는 12개 case/108RHS를 모두 저장했으나 chi1.5의 18개 확률 grid 비교가 0.5%를 넘었다(최대1.539762447%). Decimal arithmetic 검산 통과와 이 convergence 실패는 별개이다. 이 원결과는 FAILED_RETAINED로 남는다. v3은 동일 물리에 native source knots를 포함하는 별도 수치 표현으로 사전 동결·게시되었고, 이번 8개 case/72RHS/24source rows를 새로 산출했다. q-projection의 resolution 의존성도 있으므로 threshold spacing만을 실패의 유일한 원인으로 단정하지 않는다.

현재 과학 실행 누적은 v1 포함 22Q/21complete/189RHS이며, 정확한 raw가 남은 것은 v2+v3의20complete/180RHS이다. 누락된 v1의9RHS는 비용에서 제거하지 않는다. 새 ODE/source quadrature/thermal-rate quadrature/old historical campaign replay는0이다.

독립 검산 CPU는 v2 0.688471s + v3 0.799264s = **1.487735s**, 동결10s 이내다. v3 peak RSS 44972KiB, worker CPU1/coordinator CPU8, native thread1, RLIMIT_AS512MiB, worker lease 해제를 실제 기록했다. 이전 미측정 mechanical cost는 0으로 추정하지 않는다.

## 판정의 한계

지정된 T=10000K, thermal ne0.14cm−3, lnLambda20, 고정 stationary-heavy H1(1s) density0.9cm−3와 CE2S/2P만 조건부로 사용한다. Exposure10000proper s는 초기 pulse 정의이다. 첫 진입은 irreversible assimilation/Maxwellization이 아니며 killing은 관측 사건의 정지 규칙이다. 나머지 EI/neutral/CI/RR/DR/CX/HE 또는 nuclear hazard, excited target populations와 isotope transfer는 null로 남는다.

Finite-grid/boundary 비교와 exact-binary64 검산은 연속계·무한영역·원 source interpolation·물리모델의 인증된 전역 오차경계가 아니다. 전체 N4/N5는 PARTIAL/OPEN, N6/N7은 NOT_ACTIVATED이며 global_error_bound와 global_completion_percent는 null이다. 독립 C9의 과학 판정은 종료한다.

EXECUTION | 독립 C9 PASS, 원 v1 비용/미복구와 v2 실패 보존.

PUBLICATION | reviewer 게시0; root expected-SHA 최종 게시 담당.

BACKUP | reviewer 업로드0; root 백업 담당, 과거 UNKNOWN은 변경하지 않음.

DAG | 지정 CE resolvent child만 NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_FINITE_CHAIN; full N4/N5 PARTIAL, N6/N7 gated.
