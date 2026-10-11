# PHYS02G 최종 읽기 전용 handoff 준비의 독립 판정

## 판정

**PASS_SCOPED_READ_ONLY_PREPARATION.** 다음 NCP 작업은 보존된 실제 F 실패와 연산자 provenance의 읽기 전용 조사다. **F는 HOLD_OPERATOR_BINDING_UNRESOLVED, G frontier는 BLOCKED_BY_F_OPERATOR_BINDING_HOLD**를 유지한다. 이 판정은 새 F 계산, G frontier 후처리 또는 저장 G의 채택을 승인하지 않는다.

심사자는 /root/phys02g_final_handoff_review이며 후보 선택·과학 및 수용 계약 설계·구현·생산자 검산에 참여하지 않은 새 독립 Astra 역할이다. 현재 developer label은 GPT-6 Astra Pro이고 exact router alias는 MODEL_UNRESOLVED다. backend identity를 독립 인증한 것으로 기록하지 않는다.

판정 JSON: FINAL_READONLY_HANDOFF_DECISION.json, 18115 bytes, SHA256 ba4d6e012a2522cce97c9c9acf9f9976c380d0cba0f4a60aaa306998a8a0b1e2.
진단 계약: NCP_READONLY_DIAGNOSTIC_CONTRACT.json, 5,357 bytes, SHA256 eebca369dbb01b6ad678e110866f919bdd07c7692850330df55f3deab99df0ba.

## 실제 실패와 현재 상태

직접 읽은 ACTUAL_EXIT, G_COMPLETION, 원시 stderr, 예약 및 wrapper sidecar는 fullBED G 1회 예약·완료 후 exact operator identity에서 중단됐음을 보여 준다. source의 순서는 G 생성 → 완료 기록 → exact parity → 구조 검사 → resolvent 예약 → solve다. 실제 중단 위치는 parity이며 resolvent·solve·pulse·expm은 모두 0이다. execute/collect/wrapper의 실제 exit는 1/0/1이다. collection의 성공은 실패 증거를 수집했다는 뜻이며 과학 실행 성공이 아니다.

G data의 기준 SHA는 6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd, 현재 SHA는 8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa다. 공개된 이 실행의 G 1회는 이미 소모됐다. 명목상 남은 상한을 새로운 실행권이나 retry로 재사용하지 않는다. 전역의 모든 실행 이력을 이번 자료가 완전히 조사했다는 주장도 하지 않는다.

coordinator 107.954172934초와 wrapper 109.790418950초는 중첩 시간이다. 합산하거나 앞의 시간을 constructor 단독 측정으로 부르지 않는다. runtime 기록의 SkylakeX/Haswell dispatch 차이는 실제 관측한 provenance 차이이며 원인·오차 크기·roundoff-only를 입증하지 않는다.

## 조건부 resolvent 설명

통합 문서의 두 역행렬 항등식은 정확하다. 가역인 A와 B=A+ΔA, 같은 heat row h를 가정하면

B⁻¹−A⁻¹ = −B⁻¹ΔA A⁻¹,

q_B−q_A = −B⁻ᵀΔAᵀq_A

가 성립한다. 이는 원래 pulse와 새 resolvent의 동일 연산자 연결이 왜 필요한지를 설명하는 조건부 대수식이다. **전체 G의 data hash 차이는 변한 값의 위치가 active A, heat h, 다른 ledger 중 어디인지 알려 주지 않는다.** 실제 active ΔA가 0이 아닌지, h가 같은지, 두 semigroup이 물리적으로 다른지 또는 오차가 얼마인지도 이 해시만으로 결론 낼 수 없다. 현재 판정은 그 연결이 고정 계약대로 확립되지 않았다는 HOLD다.

## 다음 NCP에 허용된 범위

진단 명령의 전체 창은 180초다. 양쪽 원래 CSC 값이 이미 보존돼 있고 각각 reference와 failed-current의 정확한 data/indices/indptr identity 및 provenance에 연결되는 경우에만 그 창 안에서 저장 배열 비교를 최대 1회, 최대 90초 수행할 수 있다. 블록은 262,144 entries 이하이며 구조를 먼저 비교한다. signed 차이와 zero/sign/nonfinite 구분을 보존한다. 해석 없는 fingerprint에서 오차 크기를 만들어 내지 않는다.

한쪽이라도 원래 값이 없으면 MISSING_PERSISTED_OPERATOR_VALUES와 정확한 조회 범위를 남긴다. 현재 전달된 실패 반환에는 양쪽 값 대신 fingerprint만 있다는 기존 R3/인벤토리 범위를 유지한다. 명시된 원래 실행·cache 위치에 이미 있는 값을 조사할 수 있지만, hash가 맞는 기존 cache도 provenance와 별도 채택 계약이 확립되기 전에는 후보다.

새 G 생성·resolvent·solve·pulse·expm·F retry·G frontier는 모두 0이다. reference SHA 교체, tolerance 완화, source 변경, dispatch 강제, 설치·library 교체도 0이다. 파일 전달·create-only 복원과 source integrity 확인 시간은 계약대로 별도 기록한다. 읽기 전용 조사나 작은 차이의 관측만으로 물리 계산을 재개하지 않는다. 새 F/G 실행에는 채택할 연산자/source, 허용 기준과 누적 남은 예산이 고정된 별도 유한 과학 계약 및 독립 판정이 필요하다.

## 복원과 전달 증명의 범위

P01의 SHA는 실제 TO04 영수증과 일치한다. TO04는 G core 141개 entry의 새 디렉터리 복원과 F-family 인자 없는 stdlib plan 1회만 기록한다. exit 0, PREPARED_SOURCE_ADMITTED, WAITING_FOR_F_ACTUAL_RETURN가 확인됐다. NCP runtime, 현재 실패 family의 실제 admission, 성공 F family 경로 또는 실제 frontier 실행은 확인하지 않았다. 준비 당시 WAITING을 현재 F HOLD보다 우선하지 않는다.

원래 F tar의 R3는 정확한 archive와 실제 return 복원을 기록하지만 PR37 Git 대비는 **41/47 일치, publication 파일 4개 없음, staging 파일 2개 다름**이다. 이 차이를 숨기거나 원본을 덮어쓰지 않았다. 별도로 만든 GIT_PUBLICATION_SNAPSHOT_RECEIPT는 PR37 head a490ab7af8e7b1b4db9a604293867df8e6d035dd의 **47/47 exact Git blob**을 기록한다. 원래 tar와 staging 버전은 보존된다. 두 source의 분리된 identity를 최종 outer envelope에 유지해야 한다. 새 snapshot의 완전성이 원래 tar를 소급해 47/47 Git snapshot으로 바꾸지는 않는다.

또한 실패 return의 frozen_payload는 F source FILE_MANIFEST만 포함한다. 그 반환만으로 원래 F bundle root 전체의 membership이 검증됐다고 확대하지 않는다. 별도로 검증된 G core 안의 완전한 이전 F 준비 ZIP과 현재 실패 archive 및 별도 Git snapshot을 함께 전달하는 구성은 이 제한을 지킨다. 이 심사자는 R3와 snapshot 영수증을 읽었으며 전체 archive 재복원·전량 Git 대조·옛 F suite를 반복하지 않았다.

## G의 기존 과학 결과와 남은 전달 확인

G science commit 0ad3be0fec018fbd638063ffd4bf4d0cf2ef8525 및 기존 독립 판정 SHA256 9dd9c623fdd881667b6692ea8c3c9fbac08d545ba821fe33f66c2dbd38322002를 유지한다. 저장 모멘트의 유도된 부등식과 점검된 FP64 평가라는 기존 상한을 새 F 성공으로 확대하지 않는다. frontier는 미실행이다.

G-R01도 유지한다. 10개 FP64 working endpoint 조건은 통과했지만 exact decimal-token 해석에서는 8개 구간에서 약 10⁻¹⁷ 확률 여유의 부호 차이가 있었다. 원시 끝점은 인증된 exact-input 수치 포괄구간·forward-error 구간·물리 불확실성 구간이 아니다.

이번 준비 범위의 blocker는 없다. 최종 outer archive의 실제 membership/hash 및 외부 START의 backup identity는 후속 사실 게시 확인으로 남겨 둔다. 아직 정해지지 않은 ID나 업로드 성공을 이 판정으로 선인증하지 않는다. 다음 외부 START에는 현재 읽기 전용 계약과 F/G HOLD가 내부의 오래된 실행 분기보다 먼저 적용돼야 한다.

이번 심사에서 source import·물리 생성·solve·pulse·expm·저장 배열 수치 비교·suite·plan·복원·원격 변경은 모두 0이다. 최종 판정문과 JSON 두 개 및 최초 작성본 두 개를 보존했다. 실제 읽은 파일 및 archive member의 bytes/SHA256과 의미상 읽기 범위는 JSON에 기록했다.

## 제한된 문장 수정의 최종 binding

첫 판정 작성 직후 owner가 conditional resolvent 문장만 명확히 했다. 변경된 단락을 직접 다시 읽었고 전체 G hash의 불일치가 active A 또는 heat row의 변화 위치나 semigroup 비동등성을 입증하지 않는다는 한계가 본문에 명시됐음을 확인했다. 최종 LATE_F_INTEGRATION_KO.md는 6,555 bytes, SHA256 c7a0b3d058384cb0bef05a93f4f2dc6a6ffd420b6f95938c07379dcbb4ffb90b다. 이전 판정 두 파일은 initial_final_review에 그대로 보존했다. 새로운 수치 계산·suite·G core 변경 없이 이 prose revision만 최종 판정에 반영했다.
