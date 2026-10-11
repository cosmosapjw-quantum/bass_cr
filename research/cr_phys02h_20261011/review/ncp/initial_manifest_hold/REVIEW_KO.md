# PHYS02H 최초 NCP execution manifest 독립 HOLD

## 판정

**HOLD — NCP preparation 미승인.** 이 판정의 대상은 execution manifest `0a0281dccbbae4f53a167bdb0af421c2cf760f0ca0926c9be08f716887aab280`이며, scalar 및 local parallel의 기존 `PASS_SCOPED`는 유지한다. 원본 source, 실제 fixture 증거, 19개 direct pin은 일치하지만, 비정상 qualifier 종료와 손상된 metadata에서 전체 소유 process group 정리 및 실패 수집이라는 고정 계약을 충족하지 못한다.

검토자는 후보·허용조건·구현에 참여하지 않은 `/root/phys02h_decision_review`이다. 현재 실제 NCP 실행, 전체9600 생성, 과거 F/G 실행, 이전 테스트 재실행은0이다. 원본 qualifier/wrapper/tests/manifest를 이 디렉터리에 byte-identical하게 보존했다. 수정은 구현자에게만 맡기며, 이후 새 manifest 판정이 이 최초 실패 기록을 대체하지 않는다.

## Blocking findings

### NCP-H01 — qualifier가 먼저 종료되면 별도 lane group 정리를 생략

`run_and_collect.py:execute_and_collect`의 finally는 `process.poll() is None`인 경우에만 `PROCESS_EVENTS.jsonl`의 group을 정리한다. Qualifier가 SIGKILL/OOM 등으로 먼저 종료되면 그 별도 session의 lane/worker는 살아 있을 수 있는데, wrapper는 정리를 건너뛰고 collection으로 이동한다. 실제 source에서는 lane을 `start_new_session=True`로 실행하므로 qualifier process group의 소멸만으로 lane이 종료되지 않는다.

독립 mock fixture는 qualifier returncode=-9, 기록된 별도 lane group을 제공했다. 관측 결과는 killpg 호출0, collection 호출1이었다. 실제 OS 자식은 만들지 않았다. 수집 전에 qualifier의 생존 여부와 무관하게 모든 관측된 소유 group이 정리되는 경로가 필요하다.

### NCP-H02 — 손상된 START/READY/manifest가 raw failure collection을 중단

`collect`는 `START.json`, fallback `NCP_READY.json` 및 실행/입력 manifest를 `json.loads`로 직접 읽는다. Admission 실패의 원인이 손상된 READY나 manifest이거나, 중단으로 START가 잘린 경우 같은 오류가 수집 단계에서도 재발한다. 원시 실패 파일과 partial values가 있어도 archive를 만들지 못한다.

독립 fixture에서 START, READY, execution manifest, input manifest를 각각 `"{\n"`로 두고 작은 literal partial value 파일을 제공했다. 네 경우 모두 `JSONDecodeError`, archive 미생성을 확인했다. 손상된 metadata의 원시 bytes와 파싱 실패를 보존하면서 가능한 증거를 수집하고, 완전성 주장을 제한해야 한다. 잘못된 metadata를 유효한 source binding으로 채택해서는 안 된다.

### NCP-H03 — malformed PROCESS_EVENTS 한 줄이 후속 cleanup·terminal receipt·collection을 중단

Wrapper의 timeout finally에서 모든 event line을 무보호 `json.loads`로 해석한다. 한 줄이 잘리면 뒤에 있는 정상 소유 group 기록의 정리와 `WRAPPER_ACTUAL_EXIT.json`, collection이 모두 중단될 수 있다.

독립 fixture는 malformed 첫 줄 뒤에 정상 group 기록을 뒀다. Mock deadline 초과 경로에서 `JSONDecodeError`, 후속 group kill0, collection0, terminal wrapper receipt 미생성을 확인했다. 실제900초를 기다리거나 자식을 실행한 검사가 아니다. 개별 parsing 실패는 보존하면서 유효한 소유 기록의 정리와 terminal/failure 수집을 계속할 필요가 있다.

### NCP-H04 — comparator 소유 group의 영속 등록 누락

`qualify_parallel.py:execute`의 numerical lane spawn은 `PROCESS_EVENTS.jsonl`에 기록되지만, `--compare`의 새 session subprocess spawn은 그 영속 event에 기록되지 않는다. Root가 살아 있는 정상 finally에서는 메모리의 `children` 목록으로 정리되지만 root가 갑자기 종료되면 wrapper fallback에 comparator group 정보가 없다. 고정된 전체 소유 group 정리 조건에 맞도록 comparator도 같은 관측·정리 범위에 있어야 한다. 이 항목은 정적 source 검토 결과다.

### NCP-H05 — deadline 이후 root grace 동안 science group이 남을 수 있음

Watchdog timeout은 root에 TERM을 보낸 뒤 최대8초를 기다리고 나서야 영속 lane group의 fallback kill로 이동한다. Root가 cleanup을 수행할 수 없는 상태이면 lane generator는 이 grace 동안 계속될 수 있다. 과학 deadline과 종료 receipt/collection overhead를 구별하는 기존 계약에 맞추려면 소유 science group 정리가 deadline/failure 감지에 직접 연결되어야 한다. Receipt 수집을 위한 후속 시간은 허용되지만 그 시간을 새 과학 실행 여유로 사용하지 않는다. 이 항목도 정적 source 검토 결과다.

## 독립 재현과 증거

`INDEPENDENT_NONPHYSICAL_BOUNDARY_CHECK.py`는 보존된 초기 qualifier/wrapper를 로드하며 NumPy/SciPy/parallel_operator를 import하지 않는다. Popen과 신호 호출은 mock이고 collector 입력은 작은 literal 파일뿐이다. 새 OS child0, 새 물리 호출0, 생산 테스트 재실행0이었다.

- 실제 실행: 2026-10-11 09:12:30.119517–09:12:30.173534 UTC
- 실행1회, 내부 wall0.054009059초, 60초 상한, exit0
- 결과: `BLOCKING_FAILURE_BOUNDARIES_REPRODUCED`, 6개 fixture case
- Receipt SHA256: `e53d25e8255d62e4a8fbbce31f73c062cc503fff4b3c22679780f59c60a5e0ca`
- Script SHA256: `a81a1679e5513f9d84f9d826c910b551ee8042e7c76f448a9f3e7c646c96c8e2`
- Direct pin receipt SHA256: `ccfd16b530f31a18b177ca1d68b47851119e99169e7e68b7d02f8207a8aad1c4`

여기서 exit0은 reviewer fixture가 예상한 결함을 재현했다는 뜻이며 NCP 코드의 성공 판정이 아니다.

## 이번에 확인한 나머지 범위

고정 계약·두 resource amendment·source/READY의 review binding·동일 unit/manifest 요구·원래 버전 metadata와 child runtime 구분·누적8/76800 reservation·한900초 deadline·순차 phase/동시 model lane·정확 값 persistence·fresh parity와 historical fingerprint의 구분을 정적으로 읽었다. Resource 산식은 최종 wrapper1+root1+lane2+support2+worker58=64이고 메모리는 실제 가용량과 protected reserve로 판단한다. 최초 source와 변경된 fixture의 actual exit 및 ResourceWarning 보존도 확인했다.

이 확인을 실제 NCP 자원·동일성·성능 측정으로 승격하지 않는다. Source의19개 direct pin을 확인했으며 H549/F538 간접 manifest는 그 파일 identity와 code의 검증 경로를 읽었다. 이번 리뷰에서 모든 과거 의존 파일을 다시 해시하거나 복구하지 않았다.

보고서·START 지침의 전체 cleanup/실패 수집 약속은 위 결함과 충돌하므로 초기 packet으로 실행을 시작하면 안 된다. 원본과 최초 fixture를 유지한 채 관련 실패 경계만 고치고, 영향받는 nonphysical fixture 결과 및 새 실행 manifest에 대해 별도 제한 판정을 하면 된다. Scalar/local 계산을 재실행할 이유는 없다.
