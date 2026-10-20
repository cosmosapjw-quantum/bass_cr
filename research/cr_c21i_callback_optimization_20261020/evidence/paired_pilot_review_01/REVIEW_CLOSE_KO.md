# Paired pilot 독립 검토 및 실패 기록 경계 교정

## 판정

새 `benchmarks/paired_pilot.py`의 독립 C9 source 검토에서 발견한 실패 기록·owned cleanup·operational false-PASS 경계를 한 번의 bounded C5/C6 수정 작업으로 교정했다. 실제 science runner 32개 job은 이 검토에서 실행하지 않았다. 현재 harness는 root의 실제 same-binary 비교로 넘어갈 수 있다.

고정 source는 `c77b17ef2f4790511ffe930509fcf012ed3575dbe0c3f1e245168199525f1055`(28,879 bytes)이다. 이 시점 이후 검토자는 runtime source를 수정하지 않는다.

## 원 finding과 최소 교정

| ID | 관측한 원 source 문제 | 교정 |
|---|---|---|
| PP1 | `subprocess.run(timeout=330)`의 TimeoutExpired/OSError, 또는 `collect()` 예외가 실행된 attempt의 행 저장보다 먼저 발생했다. 시작한 실행과 경과시간이 `attempted_rows`·총비용에서 빠질 수 있었다. | Launch 전 create-only ATTEMPT, launch/timeout/cleanup의 PROCESS_RECEIPT, 수집 실패와 OBSERVATION을 보존한다. Timeout·harness 오류로 중단해도 이미 시작한 행과 비용이 summary에 남는다. |
| PP2 | 외부 timeout이 Python만 종료하면 원 H가 `start_new_session=True`로 만든 Rust segment는 다른 process group에 있었다. | Popen root도 새 session으로 생성하며 관측한 parent/starttime chain만 추적한다. 동일 PID namespace의 정확한 local PID와 `/proc` PID를 구별하고 pidfd로 TERM/KILL한다. 원 H solver source는 수정하지 않았다. |
| PP3 | COMPLETE receipt를 읽으면 nonzero Python exit, native 실행 flag, segment process exit 오류를 summary에서 강제하지 않았다. 계획 행 수·중복도 별도 gate가 없었다. | Exit 0·manufactured-only flag·완전한 accepted trace·각 segment exit 0·cleanup 완료를 운영 gate에 연결했다. 계획한 round/method/mode cardinality와 uniqueness가 맞아야 통과한다. |
| PP4 | `finally`의 source identity 확인이 실패하면 앞선 예외·최종 receipt·비용 기록을 가릴 수 있었다. | SOURCE_AFTER_FAILURE를 별도 저장하고 SUMMARY·HARNESS_RECEIPT·payload manifest를 기록한다. Source 변경은 accepted=false다. |

원 수정 전 source와 finding은 `paired_pilot_before_review_fix.py`, `FINDINGS.json`으로 보존했다. 원 source의 결함을 source 검토에서 특정한 기록이며, 원 32개 physics job을 red-first 실행한 기록은 아니다.

## 실제 focused 검증과 환경 교정

첫 `paired_pilot_failure_01`은 새 8개 harness contract 중 7개가 통과하고 실제 detached-child timeout 계약이 실패했다. 출력과 source가 그대로 보존됐다. 현 환경에서는 `os.getpid()`의 local PID와 `/proc/self/stat`의 visible PID가 다르며 `NSpid`가 두 번호를 제공한다. 최초 `/proc/{Popen.pid}` 조회는 다른 namespace의 번호를 잘못 사용하여 owned 목록이 비었고, `cleanup.complete=false`가 기록됐다.

두 번째 scoped 수정에서는 namespace mapping을 도입했지만 이 환경에 `/proc/<pid>/task/.../children` 파일이 없다는 추가 관측이 드러났다. 해당 실패도 `paired_pilot_failure_02`에 보존했다. 파일이 있는 환경은 직접 children 경로를 사용하며, 현재 환경은 `/proc/*/stat`의 parent 링크를 **poll 한 번당 한 번** 읽는 fallback을 사용하도록 고쳤다. 후보를 채택할 때 같은 PID namespace, NSpid, 실제 parent와 parent 시작 시각을 다시 확인한다. 다른 campaign의 프로세스를 목록에 넣거나 신호하지 않는다.

최종 `paired_pilot_failure_03`의 영향받은 세 계약은 실제 **3/3 PASS**다.

- 짧은 성공 Python stub의 시작/종료 receipt와 실제 owned root identity를 보존했다.
- 동일 PID에 다른 시작 시각을 제시한 경우 신호를 보내지 않았다.
- Timeout 때 TERM을 무시하는 실제 Python launcher와 별도 session의 Python child를 정리했다. 별도로 시작한 독립 control process는 계속 살아 있었고 신호 대상에 포함되지 않았다.

첫 실행에서 통과한 영향 없는 다섯 계약(launch 실패 비용, receipt가 덮지 못하는 운영 실패, cardinality/중복/empty 실패, collection/timeout attempt 보존, terminal identity 실패 보존)을 재사용한다. 따라서 **8개 고유 계약의 scoped PASS**이며, 최종 source에서 전체 8개를 한 번에 다시 실행했다고 표시하지 않는다. 실제 subprocess는 명시적인 Python stub/control뿐이다. Native chemistry·Rust binary·ODE·과거 science suite 실행은 각각 0이다.

## 실제 paired 실행의 조건

기존 계획인 2 methods × 4 modes × 첫 관측 1회와 후속 3회, 총 32개 job을 유지한다. Mode는 변경 없는 원 H, I instrumentation baseline, vectorized, vectorized_exact다. 입력은 기존 H smoke Y=0, M=9, dx=1e-7, full 28/integrated 26이고 rtol=2e-11, alpha=2e-14, cell divisor 8을 유지한다.

외부 timeout은 H의 300초 job 예산에 30초 여유를 둔 330초다. Timeout·launch/collection/cleanup 등 harness 실패에서는 해당 attempt를 기록한 뒤 후속 실행을 중단하며, 실행하지 않은 계획 key를 summary에 남긴다. 실행되지 않은 job의 비용을 만들어 넣지 않는다. 정상 science failure의 실제 receipt/raw도 통과로 바꾸지 않는다.

`--cpu 2 --monitor-cpu 3`을 지원한다. 두 CPU는 **parent affinity를 좁히기 전** 최초 허용 set에서 검사한다. 이후 monitor만 CPU 3에 묶고 각 child는 CPU 2에 명시적으로 묶는다. CPU 55는 두 옵션에서 거부한다. Membership은 독점 할당 증거가 아니다. Monitor의 ownership polling과 cleanup은 `process_wall_s`에 포함된다. H의 job 및 reference 시간은 별도로 비교한다.

첫 관측은 이미 빌드·실행한 binary의 fresh process이고 OS cache를 비우지 않는다. 후속 관측도 fresh Python 및 Rust segment process이며 mode 순서를 회전한다. 이를 제어된 cold/warm benchmark로 부르지 않는다.

## 과학·수치 비교 범위

같은 method·round의 원 H 결과와 후보 결과에서 fixture/input/bridge identity, 모든 최종 gas·photons·ledger·수지·optical depth·log survivor·underflow·최소 tau·tolerance contract를 비교한다. 모든 accepted time/state/config, 실제 FD node와 순서, 독립 재계산 수지, Rust work counter와 기록된 Python/NumPy/SciPy/thread 환경도 비교한다. 부동소수는 signed zero를 포함한 binary64 구조로 대조한다.

이 byte-level numerical criterion은 수학적 전역 오차 증명이 아니라 같은 코드 경로를 가속한 이번 callback 변경의 재현성 기준이다. Runtime source/input의 byte identity와 물리값/accepted trace의 numerical identity를 별도 필드로 보존한다. 허용오차를 완화하거나 실패를 clipping·fallback으로 감추지 않는다.

RPC log의 `logged_bytes`는 실제 파일 크기다. Rust에서 받은 JSON 메시지의 원 wire serialization은 H가 보존하지 않으므로 그 메시지의 크기는 Python 재직렬화 추정치로 표시한다. 원 wire byte 측정으로 승격하지 않는다.

## 같은 새 bridge의 현재 확인

`CURRENT_BRIDGE_AND_SOURCE_CHECK.json`은 binary 파일을 실제 읽고 H8/I3 및 상속 F10 manifest identity를 확인한 결과다.

- Binary: `/workspace/scratch/da42c813ee8c/builds/c21h_bridge_baseline_03/release/bass-cr-c21h-rust-bridge`, 4,660,352 bytes, SHA256 `202f4d93b94602f6649f427237afd6513b8fd933ae828cbd7a3cc1e90f7af934`.
- Build receipt: 2,928 bytes, SHA256 `800291c2e51424dd01afdef5f64672343fb167b9dd97a38f8c7b1210b0584c73`.
- 그 receipt는 VigilODE pin `8a8bd409...`, Diffsol 0.17.1, Rust 1.94.1 및 실제 canonical Cargo.lock compile을 기록한다. 이 검토는 재컴파일하지 않았다.
- 현재 I manifest는 `f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`이며 runner/helper/optimizer 3개 runtime을 묶는다. Benchmark source는 자신의 실행 identity에 별도로 들어간다.

## Skill context 및 독립 상태

Root가 전달한 현재 physmath-research-loop 1.3.0의 실제 `SKILL.md`, `references/CODING_LOOP.md`, `references/POLICY_INTEGRATION.md`를 읽었다. C9와 발견된 실제 결함의 bounded C5/C6, 최소 교정·focused 검증·원 실패 보존·유한 검토·해결 후 transition을 적용했다. 읽은 파일의 SHA와 실제 scope는 FINDINGS에 기록했다. 이전에 완료된 C21I 이론·component 결과에 이 skill context를 소급 표시하지 않는다.

| 축 | 상태 |
|---|---|
| 실행 | 독립 source 검토 및 bounded harness repair 완료. 8 고유 scoped 계약; 마지막 영향 검사 3/3 PASS. 실제 paired 32 jobs는 root 실행으로 넘김. |
| 게시 | 이 검토는 GitHub mutation 0. Root의 실제 content/ref/PR receipt를 따른다. |
| 백업 | 수정 전 source, 실패 01/02, 수정 03 및 review를 create-only 보존. 원격 ACK는 root delivery receipt를 따른다. |
| DAG | Paired harness readiness `PASS_SCOPED`; same-binary trajectory/물리/성능 결론은 실제 32 job 결과를 기다린다. |

`global_error_bound=null`을 유지한다.
