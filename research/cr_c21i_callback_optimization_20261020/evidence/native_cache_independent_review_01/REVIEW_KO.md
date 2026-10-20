# C21I native exact-cache admission 독립 검토

현재 `native_cache_contract.py`와 원 `NativeMicro`, private C21H `BudgetedNativeMicro`, 최적화 callback의 성공 cache 삽입 경로를 직접 읽었다. 의도한 **새로 시작한, 검증된 source namespace의 runner** 범위에서 배포를 막을 구체적인 결함을 발견하지 않았다. 이 판정은 독립 source 검토와 기존 14개 focused stub 검사의 원시 기록을 재사용한 결과다. 이 검토에서 테스트·native·Rust·ODE를 새로 실행한 수는 모두 0이다.

검토 helper source SHA256은 `c94c506aacf9bf86765e6a58ced7d005ed50d8999f7f0dd6232df9159b7bd097`(21,580 bytes)이다. 검사 producer의 `native_cache_contract_03/RECEIPT.json`이 고정한 helper·tests·optimized adapter·원 source 8개를 현재 바이트와 다시 대조했고 모두 일치했다. `stderr.txt`의 실제 14개 test 이름과 `Ran 14 tests ... OK`를 읽었다. 원 01/02 실패 기록을 덮어쓰거나 전체 과학 검사를 새로 통과한 것으로 바꾸지 않는다.

## 확인한 계약

| 항목 | 실제 구현과 검토 결과 |
|---|---|
| import 순서 | helper는 표준 라이브러리만 import한다. private H runner의 NumPy 이전 worker 환경 설정을 유지할 수 있다. |
| provider 경로 | 원 source로부터 같은 interpreter에서 다시 compile한 class method code·default와 실제 class namespace를 대조한다. 원 NativeMicro 또는 private H BudgetedNativeMicro의 정확한 class 구조를 요구한다. 추가 subclass·instance method override·class descriptor 변경을 허용하지 않는다. |
| native 근거 | 고정 SHA의 C21G authority로 실제 전달받은 provenance를 재검증한다. command는 canonical binary 한 개이고 owner는 고정 commit이다. 실제 binary·wrapper·build 기록과 process receipt를 묶는다. |
| 운영 상태 | provider/native/process/stream/selector의 고정 identity, PID·command, closed/exit 상태, 형식이 맞는 monotone 실제 call count, 변경되지 않은 cap·deadline·fixture/source JSON을 확인한다. |
| 호출 상한 | `calls == max_calls`에서 N번째 실제 성공의 반환과 이미 저장된 정확 cache hit를 허용한다. 다음 miss는 원 NativeMicro의 `calls >= max_calls` 검사에서 실패한다. `calls > max_calls` 또는 감소는 guard에서 실패한다. cache hit를 새 native 호출로 세지 않는다. |
| 시간 예산 | Budgeted wrapper의 deadline을 binary64 비트로 고정하고 guard 앞뒤에서 확인한다. 원 wrapper는 남은 시간과 15초 중 작은 native timeout을 설정하며 실제 반환 뒤에도 검사한다. cache hit에도 helper와 optimized callback의 사전·사후 guard가 실행된다. |
| 성공한 값만 보존 | 원 callback이 결과 shape·finite 검사 및 반환 후 guard를 통과한 뒤에만 cache에 들어간다. provider 실패·nonfinite 결과는 저장되지 않는다. 반환은 copy이므로 caller의 수정으로 저장값이 바뀌지 않는다. |
| 파일 변화 | admission에서 SHA256을 읽고 각 guard는 path·device·inode·size·mtime/ctime ns·mode lease를 확인한다. 동일 내용의 파일 교체도 거부한다. 종료 직전 `full_hash=True`가 SHA를 다시 읽는다. |

순수성 근거는 기존 검토에서 회수한 고정 native owner 5개 source와 `native_point.rs::evaluate`의 매 요청 새 point state 구성이다. 해당 source들의 실제 Git blob identity는 `c21i_theory/raw/owner_purity/BYTE_IDENTITY.json`에 있다. helper에 기록한 owner/file blob들은 그 값과 일치한다. 별도 fixture의 과거 native 성능이나 과학 성공을 C21I로 옮긴 근거가 아니다.

## runner에서 지켜야 할 연결 조건

1. 실제 H 경로가 생성하고 handshake한 provider에 대해서만 admission을 호출한다. runner가 생성한 source·fixture identity mapping은 실제 전체 context를 담아야 한다. helper는 비어 있지 않은 임의 JSON을 스스로 전체 실행 manifest로 바꾸지 않는다.
2. 반환한 live guard를 `vectorized_exact` callback에 연결한다. 새 cell마다 callback/cache를 새로 만들며 fun·fixture·epoch/cell·birth·D·dynamic map이 바뀐 cache를 재사용하지 않는다.
3. `guard(full_hash=True)`를 성공 반환 **전이며 provider cleanup 전**에 호출한다. 정상 close 뒤에 closed guard를 호출하면 의도대로 실패하므로 순서를 지켜야 한다. 원 H driver의 source/native 전후 검사와 C21I 전체 runtime source 전후 검사를 유지한다.
4. bare NativeMicro를 직접 사용하는 경우의 한 job deadline은 바깥 `run_optimized_reference`가 보장해야 한다. helper 자체에서 deadline을 볼 수 있는 경로는 BudgetedNativeMicro다. helper가 새 deadline을 만들거나 기존 예산을 연장하지 않는다.
5. runner는 새 프로세스의 검증된 module 경로를 사용한다. class bytecode 검사와 현재 global binding의 고정은 arbitrary 사전 monkeypatch나 OS process attestation을 완전히 해결하는 장치가 아니다. 실제 constructor/handshake가 실행된 근거는 runner의 process raw·receipt에서 유지한다. tests의 StubProcess와 synthetic build 기록은 그 계약 검사를 위한 명시적 fixture다.

## 성능 및 호환성 범위

이 guard는 매 호출에 context JSON serialization, class/global identity 확인과 여러 파일의 metadata 조회를 수행한다. manufactured component benchmark의 가벼운 deadline guard보다 비용이 클 수 있다. 따라서 그 benchmark의 exact-cache 배속을 native admission 경로의 배속으로 재사용하지 않는다. 실제 동일 native owner·입력·binary·허용오차·worker 수의 runner에서 cache hit율과 전체 wall을 측정해야 한다.

`_code_identity`는 현재 Python 3.12.14의 code object field와 class namespace에서 검사됐다. NCP의 현재 Python 버전은 아직 이 검토로 확인하지 않았다. 원 source를 같은 interpreter에서 compile해 대조하는 구조이나, Python 3.10 이전의 `co_exceptiontable` 부재 또는 이후 interpreter의 자동 class metadata 차이까지 실제 실행했다고 주장하지 않는다. 현재 런타임을 먼저 확인하고 필요한 경우 이 작은 호환 경계를 별도 source 변경·focused 검사로 처리해야 한다.

## 독립 상태

| 축 | 상태 |
|---|---|
| 실행 | source 검토 및 기존 14/14 focused stub raw 재사용·8 source identity 대조 완료; 새 native/ODE/Rust/test 실행 0 |
| 게시 | root가 생성하는 실제 GitHub 영수증에 따름; 이 검토는 원격 쓰기 0 |
| 백업 | 새 독립 검토만 create-only 보존; 원격 ACK는 root delivery receipt에 따름 |
| DAG | native exact-cache admission은 의도한 fresh runner 범위의 source 검토 `PASS_SCOPED`; 실제 runner wiring·native 실행·성능은 별도 node |

`global_error_bound=null`을 유지한다. 이 admission은 수치 수렴, 전역 오차, native chemistry의 새로운 과학 통과를 선언하지 않는다.
