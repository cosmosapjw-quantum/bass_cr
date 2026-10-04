# 저비용 LLM/Codex 운영 규약

1. `CODEX_ROUTING.json`에서 현재 repo 하나를 선택한다. 원 저장소 AGENTS.md와 해당 `CODEX_START_KO.md`를 읽는다. `legacy_sources/AGENTS.md`는 보존 원문이지 현재 packet의 새로운 작업 지시가 아니다.
2. repository root에서 `python3 docs/atomic_reionization_handoff_20261004_v1/tools/task_packet.py next --thread rei_bianchi`를 실행한다. 마지막 repo 인자는 실제 repo명으로 바꾼다. zip을 scratch에서 읽을 때는 packet root 아래 `python3 tools/task_packet.py ...`를 사용한다.
3. READY 카드 하나만 처리한다. `details`에 구체 경로·검증·acceptance가 있다. WAITING이면 unmet dependency를 반환하고 중복 물리 실행이나 원자 legacy 탐색을 시작하지 않는다. `PR_PLAN.json`은 아직 열리지 않은 구현 작업의 분해다.
4. source snapshot과 현재 HEAD의 차이를 확인한다. packet 게시 문서의 차이만 있으면 기존 science 결과를 무효화하거나 reset하지 않는다. 실제 API/물리 코드가 바뀐 경우 관련 입력만 갱신한다.
5. 작업마다 `common/RETURN_CONTRACT.schema.json` 형식의 JSON 하나와 필요한 증거 파일을 만든다. `commands`에는 실제 실행만, 실패도 exit_code와 evidence_path를 포함한다. 예정된 명령을 실행된 것처럼 넣지 않는다.
6. 산출물·acceptance를 확인한 뒤 후속 실행 상태 사본의 completed_task_ids에 해당 ID를 추가한다. 전역 상태는 조정 담당이 다른 repo의 반환 증거와 함께 갱신한다. 원래 `EXECUTION_STATE.json`은 게시 당시 상태다. 결정 노드는 이유/범위가 기록된 뒤만 activated_decisions에 넣는다.
7. `python3 .../tools/task_packet.py legacy --thread bass_cr`는 재호출 계약을 출력할 뿐 자동 실행하지 않는다. parked task는 `show CR-L1` 등으로 조회하고 실제 필요한 선행조건을 명시한 뒤 수행한다.

반환 최소 예시(미실행 계획이므로 상태 blocked):

```json
{"task_id":"REI-F00","state":"blocked","input_identity":{"source_commit":"use_observed_exact_commit"},"changed_paths":[],"commands":[],"artifacts":[],"claim":{"basis":"No runtime executed","ceiling":"planning only"},"next_task":null,"blocker":{"kind":"input","reason":"Replace this illustrative return with observed evidence"}}
```

LLM은 branch/SHA/단위/반응 ID/온도 정의를 추측하지 않는다. `TASK_CARDS.jsonl`은 한 줄당 독립 카드이며, 전체 PROGRAM/원문 묶음을 매번 프롬프트에 넣지 않는다. 필수 문헌/계수 원문은 각 `read_first`, source registry, common external reference의 정확한 파일만 읽는다. Grackle 배포 일부를 standalone library로 빌드하지 않는다.

검증 도구 `verify_packet.py`는 게시 초기 상태의 DAG·선택기·manifest를 검사한다. 과학 런타임이나 갱신된 실행 상태의 admission을 대신하지 않는다. 모든 repo의 파일을 가진 전체 ZIP에서만 전역 `build_program.py`를 재생성한다.
