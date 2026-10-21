# C21K 독립 backlog 확인 — 원 계약과 현재 확장을 분리

읽기 전용 추출이며 native/IVP/tests/remote 실행 및 원 source 수정은 0이다.

|구분|전체 logical slots|기존 실제 완료|미실행 기본/reference|미실행 조건부|미실행 최대|
|---|---:|---:|---:|---:|---:|
|H: fixture2 × method2 × base/FD|8|1|3|4|7|
|I: vectorized/exact × fixture2 × method2 × base/FD|16|2|7|7|14|
|G: fixture2 × L1/L2/L3/L3M + source refinement|12|0|8|4|12|
|K: 새 runtime의 vectorized/exact × fixture2 × method2 × base/FD|16|0|8|8|16|
|합계|52|3|26|23|49|

역사적으로 명시된 잔여·조건부 후속은 H7+G12+J exact base1/조건부FD1=21이다. **J의 옛 실행 packet은 최대 새 base1이었다.** 여기서 세는 exactFD1은 당시의 자동 제출 승인이 아니라 matching exact base 이후의 조건부 후속 가능성이다. 현재 사용자의 전체 미실행 실행 준비 요청에 따른 새 operational expansion은 추가 I 비교12+신규K16=28이며, 이를 과거 backlog로 부르지 않는다. I instrumented baseline의8 capability slots는 H-control 중복으로 기본 packet에서 제외한다.

기존 실제 완료는 H common_ic/VigilODE/base, I common_ic/VigilODE/vectorized/base, 같은 I vectorized/fd_half다. 각823, 합2469 historical native calls이며 새 호출이 아니다. 다른 I mode나 K 성공으로 승격하지 않는다.

G를 원 `run_campaign.py run` 하나로 감싸면 새 top-level 실행 node는38=H7+I14+K16+G1이다. G 내부12개의 scientific logical slots와 container1을 구분한다. G의8 reference는 원 순서와 worker1을 유지하고, 조건부4는 모든 reference 실행 완료 및 native_source reference-resolution gate 뒤에만 실행한다. G campaign exit0만으로12개 모두 완료했다고 표시하지 않는다.

FD의 hard parent는 같은 lane/fixture/backend/mode의 byte-verified COMPLETE base다. 원 H verifier는 input/native/bridge/source identity와 payload 전체를 비교한다. 현재 경로가 바뀌었다면 과거 COMPLETE raw를 복원한 것만으로 parent admission이 성립하지 않을 수 있다. 원 receipt를 고치거나 실패를 자동 재시도하지 않는다. 현재 사용자의 변경 의존성 검증 범위에서, 일치하는 base가 없으면 별도 조건부 준비 control을 새 경로에 한 번만 실행하도록 packet을 구성한다. 아래의 0/1/3 준비 분기를 따른다. K는 추가로 K runner identity와 같은 publication content를 요구한다.

H/I의 원 source는 fe6bbaec2de5032b938aed0713623b9618ba70e6에 있고 H content40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8는 실제 I 부모다. I runner는 정확한 detached I content를 요구한다. K runner는 별도 published K descendant의 detached checkout에서 H→I→K ancestry 및 inherited source bytes를 검증한다. 기존 문서 head를 native source로 대체하지 않는다.

모든49는 조건·현재 자원·source/build admission 전의 준비된 최대치다. CPU64를 채우기 위해 작업을 추가하지 않으며 CPU55, thread1, 원 tolerance/200000 cap/300s job deadline, create-only raw와 실패 보존을 유지한다. G의 job별300s를 원8+4 serial campaign 전체300s로 오해하지 않는다. 다른 repo의 과학 HOLD, Full48 및 미준비 물리 matrix는 이49 범위가 아니다. `global_error_bound=null`이다.

정확한52개 행, 완료3개 원 receipt hash, CLI argv template, output 경로 및 source/handoff hash는 `BACKLOG_INVENTORY_V3.json`과 `DEPENDENCY_CONTROL_SCOPE_DECISION_V2.json`을 따른다. 이는 실행 성공 영수증이 아니다.

## 별도 준비 control: 입력 변경에 따라 0, 1 또는 3

|현재 admission 결과|별도 준비 control|명목49를 포함한 새 raw attempt 최대|G를 하나로 감싼 새 coordinator node 최대|
|---|---:|---:|---:|
|같은 native/bridge bytes 및 일치하는 H FD parent context|0|49|38|
|같은 binary bytes, H FD parent 경로/context만 불일치|H common/V base 1|50|39|
|고정 source/owner 아래 유효 native 또는 bridge build의 bytes 변경|H common/V base + I common/V vectorized base + 같은 I FD = 3|52|41|

세 분기는 배타적이다. build 변경 분기에 path-only H base를 한 번 더 추가하지 않는다. 기존 완료3은 항상 역사 COMPLETE로 보존하고, build bytes가 바뀌면 현재 matching evidence로는 인정하지 않는다. 새 I control FD는 새 I vectorized base를 hard parent로 삼고 원 FD 검증을 그대로 통과해야 한다. 유효한 locked rebuild는 지원하되 source/owner pin이 바뀌는 경우는 BLOCKED다. 원 source/build 검증을 완화하거나 가짜 build receipt 파일 요건을 만들지 않는다.

H→I 및 I→K의 비교 자료 관계는 soft 관계다. 비교 자료가 없어도 원 계약상 독립적으로 가능한 실행을 막지 않으며, 완료 후 비교 가능성을 따로 판정한다. 같은 lane·fixture·backend·mode의 FD parent만 실행 hard dependency로 유지한다. 모든 준비 control은 명시적 이유, 별도 create-only 경로, 최대 한 번의 시도, 원 source/허용오차/budget을 유지한다. 실패·시간초과·중단 시 raw를 보존하고 자동 재시도하지 않는다.

이 표는 준비된 입력 분기의 상한이다. 현재 NCP 자원·실제 실행 성공·throughput 또는 native speedup을 확인했다는 뜻이 아니다. 실행·게시·백업·DAG 상태를 따로 기록하며 과학 HOLD와 `global_error_bound=null`을 유지한다.
