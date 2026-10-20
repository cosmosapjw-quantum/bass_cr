# C21H pilot 실행기 독립 검토

검토 시각: 2026-10-19 13:23 UTC. 판정: **PASS_SCOPED_SOURCE_REVIEW**.

이 판정은 새 실행기의 입력·실행·증거 계약에 대한 소스 검토다. C21H native 화학 실행, NCP 실행, 물리 수지 통과, 수치 수렴 또는 속도 채택을 뜻하지 않는다. 실제 컴파일·unit test·제조 실행의 결과는 해당 원시 로그와 영수증으로 별도 판정한다. 전역 오차 상계는 `null`이며 기존 C21G ladder와 확장 연구의 READY/HOLD는 이 검토로 승격하지 않는다.

## 1. 범위와 검토한 소스

담당자는 과학 소스를 수정하거나 native/NCP 실행을 시작하지 않았다. `run_pilot.py` 전체를 읽고, 연결되는 `optical_adapter.py`, 실제 `rust_bridge/build_bridge.sh`, 고정 C21G `campaign_contract.py`·`run_campaign.py`, 원본 `native_micro.py`의 관련 동작을 대조했다. 기존 수식 검토는 `SCIENCE_ADAPTER_REVIEW.md`를 재사용했다. 한 번의 검토와 확인된 결함의 교정 확인으로 범위를 닫았다.

| 검토 snapshot | bytes | SHA256 |
|---|---:|---|
| `run_pilot.py` | 15363 | `6f344f60d26a0ddb7bb205255cb767fdc230062bf60c56aae1ce58f5ef258f6c` |
| `optical_adapter.py` | 21058 | `53c8644b64f937fcca022c5307295d8666de8aee6c07244d139be139badcb387` |
| `rust_bridge/build_bridge.sh` | 3947 | `a870c9f60f241b18839398c44ebe4cfc3d95644b5c8209239a00a511581e497a` |

위 값은 검토한 바이트의 식별자다. 최종 실행 파일의 식별은 게시 `EXECUTION_MANIFEST.json`과 각 실행의 source identity가 담당한다. 이 문서를 작성할 때 최종 manifest는 아직 작성 전이므로 실제 `plan`의 manifest admission을 실행했다고 기록하지 않는다.

## 2. 확인된 결함과 교정

| ID | 최초 코드의 구체 결함 | 교정 확인 | 상태 |
|---|---|---|---|
| P1 | 빌드 writer는 `sources`의 basename→SHA를 출력했지만 reader는 `source_files`의 `rust_bridge/…`→`{bytes,sha256}`를 요구하여 실제 성공 빌드도 거절했다. | Writer가 Cargo.toml/Cargo.lock/src/main.rs 세 개를 reader와 같은 경로·구조로 기록한다. Binary SHA, VigilODE commit, Diffsol version, 성공 exit도 확인한다. | CLOSED |
| P2 | `fd_half`가 현재 native binary identity를 base와 비교하지 않아 서로 다른 native rebuild를 같은 FD 대조로 받아들일 수 있었다. | Native identity를 먼저 검증·기록하고 base receipt의 identity와 base `NATIVE_IDENTITY.json`을 모두 대조한 후 provider를 시작한다. | CLOSED |
| P3 | Smoke의 실제 fixture는 `manufactured_wiring_Y0`인데 base 검사는 아직 CLI의 native fixture 이름을 사용하여 smoke FD 후속 실행이 통과할 수 없었다. | 실제 command, fixture 이름, fixture digest를 먼저 확정한다. 이 세 값과 method를 parent와 비교하여 제조/native 혼합도 거절한다. | CLOSED |
| P4 | NumPy를 먼저 import한 뒤 현재 스레드만 CPU에 묶으면 먼저 생성된 BLAS 스레드가 다른 CPU에 남을 수 있었다. | NumPy/adapter import 전에 OPENBLAS/OMP/MKL/NUMEXPR/RAYON의 thread 수를 1로 설정·기록한다. NumPy가 이미 적재된 프로세스에서 native 실행은 거절한다. | CLOSED |
| P5 | RPC receive/wait의 deadline만으로는 Jacobian 안의 여러 native 평가가 각 15초씩 이어져 job 제한을 넘을 수 있었다. | `BudgetedNativeMicro`가 공통 job deadline을 매 원 provider 호출 전후 확인하고 그 호출의 timeout을 `min(15, remaining)`으로 설정한다. 생성자 handshake와 Rust 실행에도 남은 시간을 전달한다. 원본 provider 함수는 수정하지 않는다. | CLOSED |
| P6 | 빌드 종료 후의 source hash만으로는 빌드 도중 변경된 파일과 실제 compiler 입력을 구별할 수 없었다. | 새 target에 `SOURCE_BEFORE.json`을 create-only 기록하고 Cargo 이후 세 소스와 wrapper의 바이트를 다시 비교한다. Drift는 성공 Cargo exit과 구분하여 최종 비정상 exit 및 미승인 binary identity로 기록한다. | CLOSED |
| P7 | NativeMicro 생성자 안에서 프로세스를 시작한 뒤 handshake가 실패하면 `native_process_started=False`가 남았다. | 시도 전에 `native_launch_attempted=True`, `native_process_started=null`로 기록하고 생성자 성공 때만 True로 확정한다. Provider가 없으면 실제 시작 여부를 거짓으로 확정하지 않는다. | CLOSED |
| P8 | FD 실행 후 parent를 재검사했지만 반환 receipt hash를 처음 값과 비교하지 않아, 일관되게 갱신된 다른 parent 결과와 비교할 수 있었다. | Post-base의 경로·receipt identity를 최초 `base_job`과 비교하고 다르면 `FD_FOLLOWUP_BASE_DRIFT`로 실패한다. 통과한 경우에만 base result와 endpoint 비교를 저장한다. | CLOSED |

이 항목들은 소스 검토로 발견·교정한 결함이다. 각각에 대해 pre-fix 실행 테스트가 있었다고 주장하지 않으며 모든 검사를 red-first로 부르지 않는다. 실제 회귀 테스트 상태는 테스트 담당자의 별도 결과를 따른다.

## 3. 입력과 parent evidence 계약

C21G manifest 자체의 SHA는 실행기 상수 `7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`에 고정된다. 그 manifest에 따른 원 source, C21G runtime, fixture와 L0 baseline 바이트 검증을 재사용한다. C21H runtime은 별도 manifest의 상대 경로·bytes·SHA를 검사하며 절대 경로와 `..`를 거절한다. 실행 후 원 입력, 새 runtime, bridge와 native binary를 다시 대조한다.

`fd_half`의 parent는 COMPLETE인 base variant여야 한다. 입력 source identity, fixture, command, method, bridge identity, native identity가 같아야 하고 receipt를 제외한 전체 payload inventory가 일치해야 한다. Inventory는 심볼릭 링크를 거절하며 최상위 `JOB_RECEIPT.json`만 제외한다. Nested receipt도 payload에 들어간다. 기존 base 디렉터리에는 쓰지 않는다. 새로운 결과에 parent 영수증 SHA와 별도 `COMPARE_FD_HALF_TO_BASE.json`을 기록한다.

## 4. 실행 상태와 물리·수치 증거의 분리

Native 완료 시 `native_calls_attempted`와 원본 `rhs_evaluations`가 같아야 한다. 이 수에는 명시적인 가스·시간 차분을 위해 호출한 원 RHS도 포함된다. Rust RHS RPC 횟수, Jacobian RPC 횟수, 직접 분해 시도 또는 linear setup 수와 같은 정의로 취급하지 않는다. Adapter는 실제 backend counter를 보존하며 필요한 linear-work 키가 없으면 0으로 대체하지 않고 실패한다.

계산이 반환되면 원본 장부 결과를 저장하고 `recompute_balances`로 독립 수지를 재계산한다. Native endpoint는 고정 L0와 비교하되 C21G ladder 및 native 채택은 미완료로 표시한다. FD 후속 실행은 명시적 미분 간격 두 개만 절반으로 줄여 부모 결과와 별도로 비교한다. `execution=COMPLETE`는 이 실행·입력 계약을 완료했다는 뜻이며, 물리·수치 허용 기준이나 속도 우위를 자동 통과시키지 않는다.

예외와 cleanup 예외는 FAILED 영수증에 구분되어 남고, provider 호출 횟수·실제 종료 코드·환경 버전·실행 시간·payload SHA 목록을 수집한다. Adapter의 실패 경로도 derivative nodes, 원 RPC, 별도 process exit를 보존한다. 생성자 실패의 launch 상태와 실제 native 평가 여부는 서로 다른 필드다.

## 5. 자원·보존 범위

실행은 새로운 output 디렉터리만 생성하며 기존 디렉터리가 있으면 거절한다. 기존 campaign, dirty file, watcher, checkpoint를 정리·reset하는 경로가 없다. Native 실행은 현재 executor가 배정한 명시적 CPU를 요구하며 보호 CPU 55와 현재 affinity 밖의 CPU를 거절한다. 현재 inventory를 먼저 보존한다. Affinity membership 자체를 독점 자원 배정의 증거로 주장하지 않는다.

300초는 실행기에서 공유하는 평가/RPC deadline이다. 실제 receipt의 wall time에는 source 재검사, 비교·증거 쓰기 및 정리도 들어가므로 외부 OS의 hard kill 시각과 같다고 해석하지 않는다. Native 종료와 Rust 프로세스 정리의 grace 시간은 별도다. Provider 호출·RPC·원시 로그 크기에 추가 한도를 두고, Rust 종료 신호는 아직 실행 중인 해당 소유 프로세스 그룹에만 보낸다. 파일시스템 I/O 자체가 실패하면 완결 영수증이 없을 수 있으므로 영수증이 없는 디렉터리를 COMPLETE로 간주하지 않는다.

## 6. 부동소수점 clamp 교정의 제한 검토

Root가 실제 제조 연결 준비 중 발견한 `dx=1e-7` 사례에서 원래 `1e-9*(hi-lo)` inset은 해당 epoch의 ulp보다 작아 `L==lo`, `U==hi`로 표현될 수 있다. 기존 adapter의 `lo<L<U<hi` 검사는 이 유효한 원 RHS를 거절했다. 검사를 `lo<=L<U<=hi`로 바꾸는 제안을 독립 검토했고 최종 소스에서 확인했다.

이 교정은 원 clamp 산술과 cohort/event 경계를 그대로 유지한다. Endpoint를 `nextafter`로 바꾸거나 다른 epoch를 강제로 도입하지 않는다. 정확한 clamp corner의 partial-time 값 0은 기존 plateau-side convention이며 일반적인 양측 미분의 존재 주장이 아니다. 내부 FD 노드는 `(L,U)` 안의 서로 다른 표현 가능한 값이어야 하고 그런 노드가 없으면 명시적으로 실패한다. 이 내용은 `C21H_THEORY_KO.md`와 `NORM_FD_CONTRACT.json`에도 맞추었다.

위 발견사항에는 열린 소스 결함이 남아 있지 않다. 실제 native/C21G 비교와 달성 정확도, 최종 게시 manifest의 admission은 각 독립 단계에서 기록해야 한다.
