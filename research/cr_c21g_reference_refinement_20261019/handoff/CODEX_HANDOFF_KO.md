# C21G 실행 인계 — 그대로 복사하여 사용

```text
ROLE=C21G_BOUNDED_NATIVE_EXECUTOR
REPOSITORY=cosmosapjw-quantum/bass_cr
BRANCH=research/cr-c21g-reference-refinement-20261019
UNIT=research/cr_c21g_reference_refinement_20261019
PARENT_ASSESSMENT=d780c2c53f869c914add1d5492312d0bc507f976
PARENT_PR=https://github.com/cosmosapjw-quantum/bass_cr/pull/83
NATIVE_OWNER=cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4
EXPECTED_REUSED_BINARY_SHA256=1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40
NEW_NATIVE_STATUS=NOT_RUN

목표:
이미 구현된 C21G reference ladder 8개와 조건부 native_source 시간 정련
4개를 실제로 실행하고, 새 raw만 게시·이중백업하여 연구 스레드로 반환한다.
큰 기능 개발은 ChatGPT 쪽에서 완료했다. NCP에는 실제 환경 확인,
필요한 최소 호환 수정 또는 compile, bounded 실행만 남긴다.

0. 현재 상태를 먼저 읽어라.
실제 GitHub HEAD·새 PR·백업에서 이 인계 이후 결과가 있는지 확인한다.
이 문서 작성 시점의 NOT_RUN을 최신 상태로 가정하지 않는다.
PUBLICATION_RECEIPT.json에서 실제 실행 commit을 읽고
EXECUTION_MANIFEST.json, README_KO.md, DAG_C21G.json,
REPRODUCE.md, theory/THEORY_REFERENCE_ERROR_KO.md를 읽는다.
소스·fixture·baseline·새 실행기 SHA를 맞춘다. 현재 실행 commit을
C21F의 f8359232...로 기록하지 않는다. 후자는 원 baseline 실행이다.

1. 실제 환경과 다른 campaign를 보존하라.
현재 checkout·dirty files·branch·HEAD·watcher·checkpoint·running jobs를
읽기 전용으로 확인한다. 현재 NCP CPU/RAM과 campaign별 할당도 확인한다.
ChatGPT의 remote_calls_left_pct=0 기록은 그때의 접근 상태일 뿐이다.
사용자가 파일을 내려받거나 수동 명령을 먼저 실행하도록 요구하지 않는다.
실제 확인한 repo 경로와 credential/연결 경로를 사용한다.
기존 dirty checkout을 reset/clean/stash/rebase하지 않는다.
필요하면 별도 worktree/checkout에서 고정된 C21G 실행 commit을 사용한다.
다른 campaign·watcher·checkpoint를 중단하거나 수정하지 않는다.
이 작업에 CPU 하나를 명시적으로 할당하되 보호 CPU 55를 제외한다.
Affinity 안에 있다는 사실만으로 독점 가용성을 가정하지 않는다.

2. 원 native binary를 우선 재사용하라.
기존 native 실행 receipt와 실제 파일에서 위 SHA의 binary를 찾는다.
그 SHA와 필요한 최소 시작 호환 점검이 맞으면 compile/tests를 반복하지 않는다.
없거나 실행 불가능할 때만 현재 source의 build_native.sh로 pinned owner를
빌드하고 build_dir의 owner/input/binary/build-exit 증거를 보존한다.
새 binary는 run CLI의 --build-dir로 실제 검증 폴더를 전달한다.
원래 56개 suite·기존 8/16/32/64 행렬·기존 native point 전체 감사를
자동으로 반복하지 않는다. C21F 과거 패치/APPLY_C21F_FULL.py를 재적용하지 않는다.

3. 실행기 입력을 실제 경로로 정하라.
C21G_UNIT=<확인한 checkout>/research/cr_c21g_reference_refinement_20261019
C21G_SOURCE=<확인한 checkout>/research/cr_c21e_event_native_20261018
C21G_BASELINE=$C21G_SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z
C21G_NATIVE=<실제 검증한 binary>
C21G_CPU=<실제 할당한 CPU, 55 제외>
C21G_PLAN_OUT=<아직 존재하지 않는 create-only plan 출력 경로>
C21G_OUT=<아직 존재하지 않는 create-only 새 출력 경로>
위 꺾쇠 항목은 예시 placeholder이며 임의 NCP 절대 경로로 채우지 않는다.
프로그램은 GitHub에서 직접 읽는다. 원 baseline의 fixture/radau/SUMMARY는
현재 repo의 고정 evidence에서 재사용한다.

4. 실행 없는 plan을 먼저 만들고 입력 identity를 확인하라.
python3 "$C21G_UNIT/run_campaign.py" plan \
  --source-dir "$C21G_SOURCE" --baseline-dir "$C21G_BASELINE" \
  --out "$C21G_PLAN_OUT"

필요한 시작 검증은 새 환경 호환성에 관한 최소 검사만 수행한다.
이미 유지된 sandbox 검사와 analytic 9 cases를 관성적으로 반복하지 않는다.

5. 새 bounded campaign를 실행하라.
python3 "$C21G_UNIT/run_campaign.py" run \
  --source-dir "$C21G_SOURCE" --baseline-dir "$C21G_BASELINE" \
  --native "$C21G_NATIVE" --cpu "$C21G_CPU" --out "$C21G_OUT"

Reference: common_ic/native_source 각각 L1,L2,L3,L3M, 합계 8개.
History: native_source FULLMID와 MIDPHOTO_ENDMICRO 각각 n128,n256, 합계 4개.
L0 reference와 기존 n8/16/32/64는 재사용한다.
Reference 8개가 모두 operational COMPLETE이며 native_source의 사전
pilot sensitivity가 READY일 때만 history를 연다. Common_ic budget
초과는 독립 판정이고, common_ic 실행 실패/누락은 reference 단계 미완료다.
사전 tier·scale·예산·source를 바꾸어 같은 job의 PASS를 만들지 않는다.
한 worker, 한 CPU, job wall 300초, native/RHS 200000 호출 예산을 지킨다.

6. 실패·중단은 보존하고 완료분만 재사용하라.
재시도는 새 출력 경로와 --reuse "$C21G_PREVIOUS_OUT"을 사용한다.
이 옵션은 서명·payload SHA를 검증한 완료 C21G job만 재사용한다.
기존 출력 폴더에서 resume하거나 raw를 덮어쓰지 않는다.
구현/환경/입력/실행 budget 실패와 물리·수치 판정을 구별한다.
작은 호환 수정이 필요하면 변경 source SHA와 영향을 남기고 관련 검사만 한다.

7. 반환·게시·백업을 완료하라.
RETURN_TO_CHATGPT.json, INPUT_IDENTITY.json, NATIVE_IDENTITY.json,
LIVE_INVENTORY.json, PLAN.json, job receipt, worker receipt,
stdout/stderr, native process raw, result/accepted-grid, 실패 자료를 보존한다.
새 raw만 create-only로 GitHub에 게시하고 Drive+Dropbox에 이중백업한다.
실제 commit·provider ID·size·checksum과 실시한 readback 수준을 기록한다.
DAG에서 source implementation, native execution, physics ledger,
reference sensitivity, signed/order assessment, publication, backup을 분리한다.

연구 스레드로 복사할 반환 본문에는 다음을 포함한다.
- 실제 repo/branch/실행 commit/최종 문서 receipt head와 source 변화 구분
- 8 reference 및 조건부 4 history 각각의 완료/실패/재사용 상태
- source/fixture/raw SHA, native owner/binary/build identity, 실제 runtime
- budget, solver counters, accepted-grid 변화, underflow/log 보존
- 물리 수지와 reference 민감도/차수를 구별한 판정
- 게시·백업 실제 ID 및 완료 여부, 현재 DAG와 다음 READY node

global_error_bound=null을 유지한다. Empirical radius는 인증된 오차
상계가 아니고, 0 차이는 정확한 IVP 오차 0의 증거가 아니다.
L3/L3M actual grid가 같으면 MESH_CAP_INACTIVE다.
Full48/source-age/spectral/angular/Case B/signed Bianchi/full EoR 및
standalone Grackle driver parity는 독립 검증 전까지 HOLD다.
```
