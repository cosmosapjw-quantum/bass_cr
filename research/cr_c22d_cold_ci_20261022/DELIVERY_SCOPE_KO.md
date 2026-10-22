# C22D 배송·게시 범위와 복원 계약

## 세 가지 identity

1. **실제 실행 source:** `evidence/SOURCE_FREEZE.json`의42파일, aggregate SHA256 `2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72`. 과학 실행 전 local commit은26068749f0d738b46fd428907d81f40eeadbe1c8이다.
2. **전체 로컬 연구 commit/bundle:** 새 D의 코드·raw·분석·그림·review·후속 read-only 진단을 포함하는 최종 commit은 외부 final authority에 기록한다. bundle은 C22C local parent286d459f101eaeea0bebfda28bb0a8cfb4ceccf5를 prerequisite로 갖는 D delta다. base가 없는 완전한 Git 저장소라고 부르지 않는다.
3. **GitHub 게시:** R=a5e12c5f3e6d323e211d65fefad34060ec07eff0 위에 source closure22개를 게시한 commit은9496f159a0387713d9135398e1f1a3b3e4dcbee0이다. 그 뒤 선택한 결과·유도·수용 문서를 같은 authority branch와 Draft PR96에 추가한다. 최종 remote commit/tree와 파일 수·범위는 실제 ACK/readback receipt로 확정한다. 로컬 전체 data commit과 원격 text commit을 같은 identity라고 쓰지 않는다.

이전 create_tree 요청은25초 안에 응답이 없어 UNKNOWN_NO_ACK였으나, 동일 요청의 deterministic Git tree SHA를 로컬에서 계산하고 원격 GET으로 실제 일치를 확인했다. 그 뒤 commit과 expected-SHA를 가진 fast-forward ref update를 수행했고 branch readback에서9496f159를 확인했다. 무응답 원 기록은 보존한다.

## 최종 패키지의 의도

새 D 결과, 동결된 runtime dependency closure, 실제 비교에 사용한 이전 C22C BDF 데이터, source/analysis/review/line-admission 근거와 D delta bundle을 하나의 scoped ZIP으로 제공한다. 변경하지 않은 모든 과거 campaign과 전체 Git history를 다시 복제하지 않는다. 이전 C22C 배송본과 authority의 정확한 SHA·보존 식별자를 parent dependency로 함께 제공한다. 과거 C21O327파일 복원이나15개 byte-identical 분석 출력의 의미도 그대로 유지한다.

ZIP 내부 manifest는 모든 payload의 상대 경로·크기·SHA256를 담는다. ZIP 자신의 SHA는 외부 final authority에 둔다. provider 영수증은 ZIP 고정 후 바깥에 기록하여 archive가 자기 SHA 또는 미래 영수증을 포함하는 순환을 만들지 않는다. 복원 도우미는 신뢰한 외부 SHA를 확인한 메모리 bytes 자체에서 ZIP을 읽고, CRC·path·중복·payload hash를 확인한 뒤 새 디렉터리에만 쓴다. 복원 과정의 ODE 실행은0이다.

## 확인된 체크포인트와 남은 보존 상태

- `BASS_CR_C22D_NEW_EXECUTION_20261023T022658KST.zip`: 5,798,208 bytes, SHA256 `b0e9407913c0711f6ef6a1ac967d35e456e7c8536731c156e333509be2960688`.
- Library: `libfile_bcc86f7db2a08191ba0da9771eeeb35b`, 실제 재다운로드 bytes·크기·SHA·139-member ZIP CRC PASS.
- Dropbox: `id:BSpOijBcT10AAAAAAD_jCg`, 실제 재다운로드 bytes·크기·SHA·139-member ZIP CRC PASS.
- source-only admission ZIP의 Dropbox는 completed ACK `id:BSpOijBcT10AAAAAAD_i9A`; 그 ZIP의 Library 무응답은 UNKNOWN으로 보존한다.
- Drive admission upload는 중단될 때까지 ACK가 없었고 remote 생성·취소 모두 미확정이다. 검색0건만으로 부재를 단정하지 않는다. Drive 원 main UNKNOWN_NO_ACK, 원 document NOT_RUN, C21O recovery ZIP NOT_ATTEMPTED의 역사도 유지한다. 삼중 백업 완료로 쓰지 않는다.

실행 체크포인트의 첫 prepared 저장 도우미는 API 도구 탐색 단계의 network 오류로 write 시작 전에 실패했다. 네트워크 권한을 요청한 같은 도우미 명령은 auto-review가 `/root/.codex` 보호 경로 실행을 이유로 거절했다. 그 명령을 반복하거나 helper를 옮겨 우회하지 않았다. 새 단일 소파일에 제공되는 직접 저장 기능으로 체크포인트를 저장했고 실제 readback을 확인했다. 이 두 환경·정책 사건과 성공한 별도 저장을 구별한다. 최종 파일의 실제 상태는 final authority와 terminal transport receipt를 따른다.

## 원 상태 보존

C21O original45stress+6controls,327파일 복원과15분석 출력 일치, restore helper의 verified-memory ZIP 수정은 재사용한다. 외부 compact33/62 oracle, 다른 RR/DR·UV/T·tolerance, owner-reported recovery rerun을 C22D source/ensemble과 합치지 않는다. 접근 불가 대화 UNAVAILABLE, 원 핵반응 PNG NOT_RECOVERED_NOT_READ, full nuclear/general geometry HOLD, `global_error_bound=null`을 유지한다.
