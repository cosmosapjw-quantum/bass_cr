# Codex: 원자물리 데이터 전용 계승

## 가장 먼저 적용할 경계

현재 작업의 목적은 원자 충돌/선택상태 포획 데이터 완성이다. Bianchi 물리와 재이온화 동역학은 rei_bianchi의 소유다. 이곳에서 해당 모델·배경·수송·x_e/열 진화를 구현하거나 테스트하지 않는다. 과거 패키지에 보존된 Bianchi-I 참조코드는 역사 자료이며 다음 실행 목록이 아니다. 최신 계획은 ATOMIC_ONLY_DAG.json, 과학 수치 근거는 불변 R4AJ v1의 FINAL_STATE/RESULT이다.

## 다운로드 및 바이트 확인

같은 세트의 전체 v2 ZIP/통합 v2 patch/manifest를 사용한다. R4AI 단독, R4AI+R4AJ v1, 통합 v2 patch를 중복 적용하지 않는다. Dropbox 인증 연결 또는 사용자 동기화 폴더로 받으며 credential을 로그에 남기지 않는다. 최종 시작 prompt의 실제 ID와 SHA를 사용한다. 인증 없는 ID만으로 다운로드가 가능하다고 가정하지 않는다. 원 R4AJ v1과 R4AI가 전체 v2 package 안에 들어 있다.

전체ZIP을 새 디렉터리에 풀고 `python verify_package.py .`로 payload를 확인한다. 이것은 과학실행이 아니다. `base/R4AJ_v1.zip`의 원 FINAL_STATE/REPORT는 이번 범위지시 이전 기록이며, scope 문서가 앞으로의 소유권·계획을 덮어쓴다. 과거 기록을 수정하지 않는다.

## Git

대상 branch는 research/r4q-gap-closure-20261001, expected HEAD는 0d7bdbe76dc35d38668d750e6312919cecb09144다. 실제 원격/로컬 HEAD와 clean 상태를 다시 읽는다. 다른 작업이나 동일 경로가 있으면 멈추고 diff를 검토한다. 새 branch, main merge, force push를 하지 않는다.

`python tools/apply_checked_patch.py --repo /absolute/bass_cr --patch publication/COMBINED_ATOMIC_ONLY.patch --manifest publication/PATCH_MANIFEST.json`

위 helper는 기존 바이트동일 파일이며 지정된 r4ai_local_pre_codex/ 및 r4aj_selector_bridge/ 아래의 새 경로만 허용한다. 한 번 적용한 뒤 worktree/index와 manifest를 확인하고 같은 branch에서 commit/non-force push한다. 이 패키지는 Git objects를 가진 bundle이 아니라 실제 적용 검증한 binary patch다. 옛 R4AD 안전성차단 mutation과 R4AA379를 가져오지 않는다.

## 원자 연구와 실행

로컬 다음은 LOCAL_RESONANT_PAIR_WEAK_BRIDGE_ENVELOPE다. 측정 P1s와 retained T1s/P1s는 구별한다. 저장 행렬 gap이나 합성 3x3 시험을 실제 bridge/capture/source 인증으로 사용하지 않는다. weak generator의 공진 내부항, 제거공간 coupling/도함수, 움직이는 frame connection을 동일 convention으로 결합한다.

외부 첫 실행은 R4AH m64 하나다. base/R4AJ_v1.zip -> parent/R4AI.zip -> legacy_runtime의 R4AH/R4AG를 새 작업폴더로 풀고 해당 기존 handoff의 source/input/native/resource one-shot 절차를 따른다. 원 코드를 재구현하지 않는다. 실제 메모리/CPU 관측을 기록하고 승인 조건을 낮추지 않는다. m64 실제 반환 수락 전 remaining9를 시작하지 않는다. 별도 batch를 만든 뒤 승인하고, 같은 native 조건에서 원 merge_returns.py로 m64를 재계산하지 않고 수집한다.

## 반환

실제 수행한 stage의 source/native/input/frame/unit/domain/attempt/output/resource, 실패 및 중단, node enclosure와 seal, 검토 결과, 변경 코드와 manifest를 반환한다. shifted/stencil/physical bridge가 없으면 null이다. 현재 G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO다. 두 provider의 실제ACK/ID/size가 있을 때에만 이중백업완료이며 R1 UPLOAD_VERIFIED와 실제 download RESTORE_VERIFIED를 구별한다.
