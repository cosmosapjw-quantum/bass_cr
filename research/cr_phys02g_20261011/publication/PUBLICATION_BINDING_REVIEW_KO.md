# PHYS02G 최종 게시 binding 독립 판정

**PASS_SCOPED_PUBLICATION_BINDING.** 외부 START의 현재 지시는 읽기 전용 연산자 provenance intake로 한정돼 있다. F는 HOLD_OPERATOR_BINDING_UNRESOLVED, G frontier는 BLOCKED_BY_F_OPERATOR_BINDING_HOLD를 유지한다.

판정 JSON: PUBLICATION_BINDING_DECISION.json, 10369 bytes, SHA256 29c2b95254023817f19617367af08725a164d4b120800bf27a6e141e58a05ff7.

## 확인한 연결

- 외부 START는 10,621 bytes, SHA256 54af74dde0dbaa69a1a65173f1fdc533a8d100d0ec633c69e40c863de582e44c다. 전체 진단 창 180초 안에서 양쪽 원래 저장 CSC의 exact identity가 연결됐을 때만 최대 1회·90초 비교를 허용한다. 미보존 값은 MISSING_PERSISTED_OPERATOR_VALUES로 남기고 새로운 물리 실행을 열지 않는다.
- 알려진 F 소모 G 1회 및 execute/collect/wrapper exit 1/0/1을 보존한다. 이전 내부 START의 최초 실행 분기, 명목 잔여 allowance, retry 및 legacy 후속 실행을 적용하지 않는다고 명시한다.
- Outer ZIP은 58,470,931 bytes, SHA256 2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707이다. 이번에는 전체 ZIP을 다시 hash하지 않았다. 기존 assembly 영수증과 local stat, 외부 START가 일치했다.
- 실제 outer manifest 22,457 bytes의 SHA256 1ec3c042a86008a59f4867a179980b5e3f59783c6b8d372d99c6b453566c4e18을 직접 확인했다. 79 payload와 manifest 자신 하나가 실제 80 entries의 정확한 집합이며 중복은 없다. 별도 PR37 snapshot payload는 47개다.
- 실제 내장 README, CURRENT_NEXT_ACTION, 진단 계약, 최종 독립 판정, 수정 integration 5개를 읽어 manifest 및 현재 로컬 bytes와 일치함을 확인했다. 계약 eebca369…와 판정 ba4d6e01… 연결이 정확하다.
- G core ZIP 27,795,932 bytes와 실제 실패 F tar 30,522,967 bytes의 manifest·header·START identity가 일치한다. Outer/inner schema와 복원 root를 구분한다. 이번 검토에서 두 내장 archive payload는 다시 읽거나 복구하지 않았다.

## 백업·Git과 주장 범위

Drive ID는 1TrNu23r3VfhvPGjesqATWFpthvhVjTcB, parent는 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI다. Dropbox ID는 id:BSpOijBcT10AAAAAAD4I9A, revision은 65d8b6ea41a810af03d47이다. 두 provider의 기록된 크기는 모두 58,470,931 bytes이며 정확한 경로·파일명이 START와 일치한다. 이 검토는 root의 실제 R1 영수증과 시작 파일을 대조했다. Provider를 다시 조회하지 않았다. Provider checksum 미제공을 명시하며 로컬 SHA를 원격 checksum이나 새 outer의 R3 복원 증명으로 바꾸지 않는다.

외부 START는 science commit 0ad3be0fec018fbd638063ffd4bf4d0cf2ef8525와 게시 branch/PR38을 고정하고, 아직 없는 publication C2 head를 자체 참조하지 않는다. 수신자가 실제 최신 head의 C1 후손 관계와 publication 범위 후속 변경을 확인한 뒤 새 additive return branch/draft PR을 만들도록 지시한다.

현재 원본 F tar의 41/47 Git 일치·publication 4개 없음·staging 2개 차이와 별도 47/47 PR37 snapshot의 출처를 구분한다. G-R01 끝점 제한과 상속 gate도 유지한다. 저장 값 탐색이나 작은 수치 차이 관측만으로 F/G HOLD를 해제하지 않는다.

## 완료와 남은 게시 동작

외부 START의 내용·정확한 백업 식별자·계약/판정 연결에는 blocker가 없다. **검토한 START를 그대로 업로드하고 publication metadata를 기록할 수 있다.** START 자체의 provider ID 및 C2 실제 head는 이번 검토 시점에 아직 생성되지 않았으며 root가 게시 후 사실대로 기록해야 한다. 이 판정은 미래 ID나 업로드·commit 성공을 선인증하지 않는다.

이번 후속 검토는 manifest/membership 1회 및 지정 text payload 5개 확인으로 끝냈다. 전체 ZIP rehash·remote readback·R3·core plan·수치 비교·suite·물리 실행·source/START 수정은 모두 0이다. 이 두 판정 파일은 이미 올라간 outer ZIP 밖에 새로 작성했다.
