# C21G 실행기 독립 코드 심사와 집중 검증

## 결과와 범위

`run_campaign.py`의 완료 인정·재사용·입력 고정·실패 보존 경로를 심사하고 수정했다. 최종 실행기 SHA256은 `d844dec3be1cb397d48db319cd84a5f2314011db0cd0443d3d704d6252080275`이며, 해당 바이트의 집중 검사 14개가 모두 통과했다. 이 검사는 기존 C21F의 56개 검사나 이전 native matrix를 재실행한 것이 아니다. NativeMicro·Rust·Grackle·NCP의 과학 실행을 시작하지 않았다.

이 문서와 `CAMPAIGN_REVIEW_RED.json`, `CAMPAIGN_REVIEW_GREEN.json`, 각 대응 로그는 이번 심사의 근거다. 게시·백업·DAG 전역 상태는 상위 C21G 인계 영수증에서 갱신한다. 이 하위 심사가 독립적으로 게시 완료나 native 과학 검증 완료를 선언하지 않는다.

## 닫은 문제

| 문제 | 수정과 남은 의미 |
|---|---|
| 빈 파일 목록을 가진 COMPLETE 영수증이 재사용됨 | result·worker 영수증과 실행 종류별 필수 파일을 요구하며, 실제 전체 payload 파일 집합의 크기·SHA256이 manifest와 일치해야 한다. |
| 다시 해시한 잘못된 worker/result metadata가 통과함 | job signature, 전체 fixture digest, runtime, microphysics 종류, worker status·종료코드, 요청한 reference controls 또는 history mode·subdivisions, 실제 호출 수를 함께 검증한다. |
| Native 원시 로그 일부가 빠져도 완료로 보일 수 있음 | native process owner·binary SHA·timeout·호출 상한과 worker exit0을 확인한다. 원시 JSONL 행 수·provider 실제 호출 수·결과의 RHS 호출 수가 일치해야 한다. 프로토콜의 물리 의미는 고정된 원본 NativeMicro가 실행 중 검사한다. |
| 최초 확인 이후 소스가 바뀔 수 있음 | 고정 입력 기록의 manifest·policy·C21F runtime·baseline·C21G runtime·실제 runner 파일·native binary 바이트를 부모 job 전후와 worker import 전·실행 후에 확인한다. 변경을 발견하면 COMPLETE로 인정하지 않는다. |
| 실행기 시작 실패나 결과 파싱 실패 때 job 상태가 사라짐 | job별 terminal FAILED 영수증과 실패 원인을 새 경로에 보존한다. 종료된 worker가 남긴 부분 payload도 보존한다. |
| 프로세스 leader가 먼저 종료되면 TERM을 무시하는 자식이 남을 수 있음 | `start_new_session=True`로 만든 이 job의 process group에 TERM 후 KILL을 반드시 보낸다. leader 종료만으로 group 종료를 추정하지 않는다. 다른 group을 대상으로 하는 정리 명령은 없다. |
| common fixture 실행 자체가 실패해도 native refinement가 열릴 수 있음 | `can_refine()`는 기준해 평가의 execution_status COMPLETE와 native_source pilot READY를 모두 요구한다. main은 8개 reference 영수증의 COMPLETE도 확인한다. common fixture의 수치 budget HOLD는 실행 실패와 별도로 취급한다. |
| 전체 process argv가 공개 inventory에 저장됨 | `ps` 열을 `args`에서 `comm`으로 바꾸어 임의 프로세스의 전체 인자를 기록하지 않는다. CPU 할당 여부는 운영자가 현재 다른 campaign를 읽고 판단한다. |
| import로 기존 source checkout에 bytecode가 쓰임 | local import 전에 `sys.dont_write_bytecode=True`를 설정한다. child에는 기존 `PYTHONDONTWRITEBYTECODE=1`도 유지한다. |

## 공용 검증 인터페이스

```python
verify_payload_record(receipt, payload_directory=None) -> result
can_refine(reference_assessment) -> bool
```

첫 함수는 완료 payload를 검증하고 파싱한 result를 반환한다. 잘못된 스키마·누락 파일·불일치에는 `ValueError`를 낸다. 두 번째 인자는 사용자가 실제로 복원한 경로를 호출자가 확인한 경우에만 전달한다. 경로를 자동 추측하거나 다운로드를 수행하지 않는다. 상대 파일 manifest의 절대경로·상위 이동과 symlink를 거부한다.

이 검증은 영수증의 내부 일관성을 확인한다. 독립 분석 호출자는 분석 대상 fixture와 고정 input manifest라는 외부 기준에도 영수증을 연결해야 한다. `run_job`은 이미 최초 입력 기록의 fixture SHA 및 동일한 예상 signature로 이 연결을 수행한다. 물리 수지·수치 비교 budget·수렴 차수는 이 완료 검증 뒤 별도로 평가한다.

## 실행 근거와 red-first 범위

실제로 실행한 공통 unittest argv는 다음과 같다. 정확한 Python 경로·cwd·UTC·exit code는 각 JSON 영수증에 들어 있다.

```text
python3 -B -m unittest discover -s /workspace/scratch/4d2e4c44b70c/c21g_work/unit/tests -p test_campaign.py -v
```

| 기록 | UTC 시작 | 결과 | 시간 | SHA256 |
|---|---|---|---|---|
| RED | 2026-10-19T08:32:50.556999+00:00 | exit1, 10 methods, failures10·errors1; failures는 subtest도 포함 | unittest0.604s, process0.724388s | runner `d6188f56af3883b594f44d26c0923fe07a0e31f5fd8b83a8740782dbdf44e16e`; tests `b73228aa998a5bace1e74649ff00fc7c387a4b7f7e06ee579739d7c4897c4214` |
| GREEN | 2026-10-19T08:50:54.140968+00:00 | exit0, 14/14 PASS | unittest0.664s, process0.778734s | runner `d844dec3be1cb397d48db319cd84a5f2314011db0cd0443d3d704d6252080275`; tests `8530af8b1b14903b262617c56c349b5afdcf7c2def69511b94b27ae2ac22d0bd` |

RED에서 실제 실패한 경로는 빈 완료 payload, 실패 프로세스의 완료 인정, launch 실패 영수증 누락, gate helper 부재, worker 또는 tolerance metadata 불일치, job 시작 전 소스 확인 부재, 미목록 파일·경로 탈출이다. create-only 기본 동작과 단순 바이트 변조 검사는 처음부터 통과했다. 최종 14개 전체를 red-first라고 부르지 않는다.

RED 이후 추가한 네 검사는 source/runner 실제 바이트 변경, worker 이후 변경과 부분 보존, malformed receipt의 ValueError 계약, synthetic native metadata·로그 수 불일치다. 이 네 검사는 별도의 RED 기록을 주장하지 않는다. 전체 fixture를 signature에 포함하는 변경 때문에 테스트 fixture 형식도 보강했다.

timeout 검사의 최초 `/proc` 단독 판별은 샌드박스의 실제 OS 상태와 맞지 않았다. 직접 관측한 `os.getpgid`와 child heartbeat는 TERM 이후 자식의 지속 실행, KILL 이후 정지를 구분했으며 `/proc/stat` 행은 정지 뒤에도 S를 보였다. 최종 검사는 알려진 child에 대한 실제 OS 조회를 우선하고 정상 Linux zombie 상태도 종료로 인정한다. 같은 검사에서 별도의 임시 process group이 계속 살아 있음을 확인했다. 따라서 timeout 검사의 최초 PASS를 이전 구현의 올바른 동작 근거로 사용하지 않는다.

## 로그 공개 전 확인

최초 RED의 unittest.mock 실패 출력 한 줄에 inherited environment가 포함되었다. 해당 인자 dump 한 줄을 제거했고, RED JSON에 제거 사유·원래 로그 SHA·보존한 실패 수와 traceback 위치를 기록했다. 기존 오류의 과학·기능 증거를 삭제하지 않았으며, 현재 RED 로그가 최초 stderr와 바이트 동일하다고 주장하지 않는다. 이후 테스트는 mock 호출 횟수만 비교하여 환경 인자 dump를 만들지 않는다.

`CAMPAIGN_LOG_PRIVACY_AUDIT.json`은 RED/GREEN 네 파일을 현재 credential 값과 일반 credential 할당 패턴으로 검사한 결과와 각 파일 SHA를 기록한다. credential 값이나 변수명은 audit에 출력하지 않았다.

## 다음 연결 단계

상위 작업자는 고정 manifest를 만든 뒤 새 작은 manufactured fixture의 reference·FULLMID·MIDPHOTO_ENDMICRO 세 job으로 실제 parent/worker 연결을 확인할 수 있다. 그 결과도 native 물리 검증과 분리한다. NCP 실제 pilot은 현재 자원·다른 campaign·dirty files·watcher·checkpoint를 확인하고 명시적으로 할당된 CPU에서 새 출력 경로로 수행한다. 원래의 독립 검증 HOLD는 유지한다.
