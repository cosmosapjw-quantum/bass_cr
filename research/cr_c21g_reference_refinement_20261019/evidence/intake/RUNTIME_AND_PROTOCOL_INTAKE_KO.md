# C21F 후속 연구: 샌드박스와 첨부 규약 취득

관측 구간: 2026-10-19 07:55:54–07:58:31 UTC (16:55:54–16:58:31 KST).
담당 범위는 도구 가용성 및 첨부 규약의 적용 범위 확인이다. 이 취득 단계에서는 과학 계산이나 native 실행을 수행하지 않았다.

## 1. 현재 샌드박스 실행 상태

| 항목 | 새로 관측한 상태 | 적용 범위 |
|---|---|---|
| Python | 3.12.14, stdlib 산술 probe PASS | 경량 검증·분석 구현 가능 |
| NumPy | 2.3.5, import PASS | 배열·FP64 후처리 가능 |
| SciPy | 1.17.0, import PASS | 필요한 경량 수치 probe 가능 |
| Matplotlib | 3.10.8, import PASS | 실제 수치 기반 plot 생성 가능 |
| SymPy | PACKAGE_MISSING | 로컬 심볼릭 경로는 현재 미제공 |
| pytest | PACKAGE_MISSING | 새 표준 라이브러리 unittest 경로 사용 가능 |
| g++ | 13.3.0, 작은 C++17 FP64 프로그램 compile/run exit 0 | CPP_PASS는 실행 환경 smoke 근거 |
| gcc | 13.3.0, version command exit 0 | C 프로그램 compile/run은 별도 미수행 |
| bash·git | 5.2.21·2.51.1, version command exit 0 | 구문 검사·로컬 저장소 연산 가능 |
| rustc·cargo | NOT_ON_PATH | 현재 Rust 실행 성공을 추정하지 않음 |
| WolframKernel·wolframscript | NOT_ON_PATH | 원격 Wolfram plugin은 별도 실행 경로 |

`RUNTIME_PROBE.json`에 실제 version·exit·출력을 보존했다. C++ probe는 두 double의 정확한 덧셈 및 `sizeof(double)==8`을 검사했다. 이는 물리 모델, IEEE 연산 전체, native bridge 검증의 근거가 아니다.

## 2. 현재 원격 자원 확인 범위

Desktop Commander의 `who_am_i`를 이번 취득에서 한 번 새로 호출했다. 요청은 성공했고 `remote_calls_left_pct=0`, `device_count=1`을 반환했다. 개인 식별 필드를 제외한 결과를 `REMOTE_QUOTA_INTAKE.json`에 보존했다.

현재 NCP CPU·RAM·다른 campaign·dirty files·watcher·checkpoint는 이번 단일 account-level 조회로 확인할 수 없다. 따라서 이 상태는 **UNVERIFIED_CURRENT_NCP**다. 원격 job 시작, 프로세스 중단, 파일 변경은 각각 0건이다. 과거 실행 로그의 자원 수치는 현재 가용 자원에 대입하지 않는다.

## 3. 첨부 규약의 적용 범위

첨부 파일은 사용자가 제공한 현재 scratch 경로에서 직접 읽었다. `ATTACHMENT_PROTOCOL_INTAKE.json`에 읽기 범위·크기·SHA256을 보존했다.

| 파일 | 읽기 범위 | C21F 후속 작업에 적용하는 내용 |
|---|---|---|
| 04 Adaptive CMB Code Development Protocol | 전체 | 물리·코드·관측량 계약과 실제 code path를 복원한 뒤 최소 수정. PHYS-MATH → PHYS-MATH-CODE 순서의 감사. plot 직접 확인. |
| 05 DAG-Governed Research Executor | 전체 | 선행 근거를 재사용하고 DAG상 가능한 다음 단위를 실행. 새 결과의 수치표·plot·감사·다음 의무를 연결. |
| 07 Figure Residual Error Pass | 전체 | 의미·겹침·잘림·축소 가독성의 최종 점검. 89–90 mm 또는 180–183 mm 출력 폭을 의도에 맞게 명시. |
| 08 Figure Hostile Audit | 전체 | figure 주장·축·단위·정규화·panel 비교가 실제 데이터와 맞는지 먼저 감사하고 최소 수정. |
| 01 Low-ell Bianchi audit | 첫 135줄 | 원문이 감사 대상을 htt/bass로 명시한다. C21F에는 실행 상태·물리 검증·문서 주장 구별이라는 공통 원칙만 참고한다. |
| 03 Rust environment | 전체 | 경로 선언 확인. 선언된 prefix는 현재 존재하지 않는다. |
| 09 bootstrap | 전체 | 과거 Bianchi 복원 절차와 예상 520 Python / 44 Rust 검사라는 역사적 목적 확인. |

### 현재 요청과의 조정

- CMB의 gauge/LoS/Bessel/Thomson/11-family 규칙은 해당 code path를 다루는 경우에 적용한다. C21F fixed-fixture H/He time-integration을 Bianchi/CMB 검증으로 확장하지 않는다.
- 05의 한 단계 선택 규칙은 **각 의존 단계의 순차 완료**로 적용한다. 사용자가 이번에 요청한 가능한 구현·가벼운 검증·게시·백업 전체를 한 단위에서 임의 종료하는 규칙으로 사용하지 않는다.
- 04의 unresolved baseline에서 release packaging을 미루라는 문구는 물리적 검증·production release 승격을 제한한다. 이번 사용자 지시는 각 단계의 연구 증거와 미완료 의무까지 게시·백업하도록 명시하므로, 연구 checkpoint의 create-only 보존은 계속한다.
- 그림 preset의 `/web: off`, `/cites: none`은 그림만을 읽는 해당 감사 형식이다. 사용자가 명시한 문헌 도구 사용이나 연구 주장에 필요한 출처 표기를 막지 않는다.
- 현재 developer의 병렬 작업 지시 및 사용자 승인 범위가 일반 첨부 규약의 기본 전략보다 우선한다.

## 4. 첨부 Rust·bootstrap의 취급

첨부 Rust archive는 실제 존재하며 192,287,020 bytes다. 읽기 전용으로 앞쪽 directory header 1,445개를 확인한 뒤 첫 일반 파일을 읽기 전에 멈췄다. `cargo`, `rustc`, `rust-std-x86_64-unknown-linux-gnu`, rustfmt·clippy·LLVM·documentation 관련 component directory가 관측되었다. archive 전체 CRC·signature·payload 검증이나 설치는 수행하지 않았다. 기록은 `RUST_ARCHIVE_INTAKE.json`에 있다.

`03-rust_1_94_1_env.sh`가 선언한 `/mnt/data/rust-1.94.1-prefix`는 현재 존재하지 않는다. 해당 shell 파일을 source하지 않았다.

`09-bootstrap.sh`는 network pip/maturin 설치, `audit/__init__.py` 변경, 별도 `_rustcore` 빌드 및 wheel 강제 설치, 과거 전체 회귀 검사를 포함한다. C21F 후속 reference·refinement의 의존 계약과 다르므로 실행하지 않았다. 필요한 경우에만 C21F manifest의 실제 의존성에 맞춘 별도 최소 절차를 만든다.

## 5. 다음 실행에 전달하는 최소 계약

1. Root가 최신 백업·GitHub 원시 receipt 취득을 완료한 뒤 source·fixture·reference·raw identity를 고정한다.
2. 현재 구현 수정·경량 검사·자료 형식·분석·plot·실행 runner를 샌드박스에서 완성한다. 새 검사 결과와 재사용한 과거 검사를 구별한다.
3. Native 실제 계산을 요구하는 항목에는 고정 owner/source, 입력 hash, 정밀도·허용오차, 출력·실패 schema를 전달한다.
4. NCP 실행자는 실제 시작 직전 현재 자원과 campaign·dirty files·watcher·checkpoint를 읽고 보존한다. 현재 inventory가 확보되지 않은 상태에서 과거 자원 수치를 사용해 launch하지 않는다.
5. 기존 matrix를 입력으로 재사용하고, 새로 필요한 reference tolerance 또는 fine refinement만 create-only output에 기록한다. 구체적인 run 목록은 최신 DAG와 root의 새 연구 결과가 정한다.
6. Compile·실행 exit, 수지 검사, 수치 수렴, claim 범위, 게시·백업 상태를 별도 필드로 남긴다. NCP에 새 기능 설계나 처음부터의 큰 구현을 떠넘기지 않는다.

## 상태

- 첨부 규약 취득: COMPLETE_SCOPED.
- 샌드박스 가용성 probe: COMPLETE.
- NCP 현재 자원 취득: UNVERIFIED_CURRENT_NCP; 현재 provider 잔여 호출량 0% 관측.
- 새 과학 실행: 이 담당 취득 범위에서는 NOT_RUN.
- 파일 게시·백업: 상위 연구 단위의 create-only publication/backup에 결합 예정. 이 문서 자체는 provider 성공 영수증을 주장하지 않는다.
