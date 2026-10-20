# C21I runner C9 독립 검토 1회

## 판정과 범위

새 `run_optimized_pilot.py`의 변경 연결부를 한 번 독립 검토했다. 검토한 source는 SHA256 `1a3f4d9066bedc3a8d7466723e8f344fa451c0c6a85c48bf0efe03210d6d8a43`, I execution manifest는 `f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`이다. 이 범위에서 수정해야 할 구체적 결함을 발견하지 않았다. 판정은 **PASS_SCOPED**이며 다음 실행 gate는 같은 실제 bridge binary를 사용하는 제조 ODE 비교다.

검토자는 root가 작성한 runner를 검토했다. 검토자가 앞서 작성했던 adapter의 닫힌 방정식·vectorization·cache 구현을 다시 심사하거나 helper의 완료된 검증을 재실행하지 않았다. 현재 physmath-research-loop 1.3.0 C9의 부모가 제공한 실제 범위 정의를 사용했으며, 과거 완료 범위를 소급하여 1.3 검토로 표시하지 않았다.

## 실제 source 연결 확인

| 변경 표면 | 확인한 동작 | 사용한 근거 |
|---|---|---|
| H private import | H가 최초 NumPy 상태를 관측하고 worker 환경을 설정한 뒤 private optical adapter를 읽는다. 공개 `sys.modules['optical_adapter']`를 바꾸지 않는다. | 실제 `load_private_h`/원 H import 순서, 기존 fresh-process 계약 raw |
| source identity | 고정 H manifest와 8개 파일을 그대로 유지하고 별도 I 3개 source와 선택 mode를 `C21I_SOURCE_IDENTITY`에 추가한다. build receipt의 원 H 3개 Rust source 비교를 보존한다. | `own_source`, `verify_i_source`, 원 H build guard, 기존 drift/build-record 계약 |
| 게시 및 content checkout | native provider 생성 전에 supplied PUBLISHED H/I receipt, 실제 로컬 commit의 manifest/runtime 바이트, H-content ancestor, 실제 detached I-content HEAD를 확인한다. 진행 중 receipt 바이트가 달라지면 거절한다. | `NativeAuthority`, `verify_publications`, 원 H의 provider 생성 순서, 기존 synthetic Git 계약 |
| FD parent | 원 H의 base COMPLETE 및 fixture/method/input/native/bridge/source identity와 전체 payload 검사를 그대로 사용한다. I mode·source identity가 원 `own` 비교에 들어가므로 다른 mode 또는 I source의 parent를 거절한다. base raw는 원 guard가 실행 전후 확인한다. | 원 H `verified_base`와 I `own_source`; 기존 FD parent 계약 raw |
| native cache admission | `vectorized_exact` native에만 admission을 호출한다. 실제 source-defined private H `BudgetedNativeMicro` class는 새 runner의 private import 방식 및 bind 후에도 helper의 exact method/namespace 검사를 통과한다. | 아래 새 class integration probe; helper 전체 suite 재실행 없음 |
| 예산과 정리 | H가 전달한 남은 예산과 기존 provider의 절대 deadline 중 이른 값을 사용한다. admission 비용을 차감한 남은 값만 adapter에 전달한다. terminal full hash 및 source 재확인은 원 H provider cleanup보다 앞에 수행한다. 실패는 원 H의 traceback/FAILED receipt 및 cleanup 흐름을 따른다. | 실제 `run`/원 H `try-finally`; 기존 cleanup 계약과 아래 새 fake-clock probe |

게시 guard는 제공된 외부 receipt를 실제 로컬 content 바이트와 연결하는 검사다. runner가 외부 GitHub에 접속해 receipt의 provider ACK 또는 최신성을 새로 인증하는 기능은 없다. 실제 최신 게시 영수증을 선택하고 remote ACK를 확인하는 일은 게시·handoff 단계의 책임이다. 현재 H/I의 PUBLISHED 상태를 만들거나 우회하지 않았다.

## 검증 재사용과 새 경계 검사

`../optimized_pilot_01/RECEIPT.json`, `stderr.log`, 실제 `tests/test_optimized_pilot.py`를 읽었다. 기존 계약 12개의 PASS raw와 source 전후 identity가 현재 frozen source에 대응한다. 이 12개를 다시 실행하지 않았다. 이 검토에서 새로 실행한 것은 `probe_runner_boundaries.py`의 다음 네 integration probe다.

1. 실제 새 loader의 private H class를 helper `_ClassBinding`이 bind 전후 인정한다. 해당 private H module은 `sys.modules`에 등록되지 않은 상태다. NativeMicro 생성자는 호출하지 않았다.
2. fake time 100, 원 provider deadline 108, 호출자가 전달한 wall 10에서 admission이 3을 소모하면 optimizer stub에는 wall 5만 전달된다.
3. 같은 조건에서 admission이 9를 소모하면 optimizer stub 호출은 0이며 예산 초과로 실패한다. terminal guard 경로는 유지된다.
4. admission이 3을 소모하고 terminal full hash가 5를 더 소모하여 원 deadline 108에 도달하면 성공 반환을 거절한다.

네 probe는 모두 PASS_SCOPED였다. 실제 runtime source 3개, I manifest, 원 H runner의 SHA256/바이트는 실행 전후 같았다. 새 probe에 사용된 provider·publication authority·clock·optimizer는 명시적 test double이며 native process, Rust, ODE 실행은 모두 0이다. 기존 12 계약과 새 4 probe를 합쳐 과학 PASS나 전체 회귀 PASS로 표현하지 않는다.

## 완료 상태

| 항목 | 상태 |
|---|---|
| 검토 실행 | C9 한 번 완료, 기존 12개 scoped 근거 재사용, 추가 4개 integration probe PASS_SCOPED |
| 코드 수정 | 0; 원 H 및 I runtime source 변경 0 |
| GitHub 게시 | 이 검토의 remote write 0; 기존 게시 차단 상태를 변경하지 않음 |
| 보존 | 이 고유 evidence 디렉터리에 create-only 저장; 외부 백업 ACK는 root의 전체 전달 영수증에서 별도로 기록 |
| DAG | runner C9 범위 완료; 실제 같은 binary 제조 비교가 다음 실행 gate |

새 native 성능·chemistry 결과, 수치 수렴 또는 전역오차를 평가하지 않았다. `global_error_bound=null` 경계는 유지한다.
