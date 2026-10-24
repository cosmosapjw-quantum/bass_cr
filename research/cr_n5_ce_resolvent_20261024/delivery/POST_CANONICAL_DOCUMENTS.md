# Canonical freeze와 후속 문서의 결속

Canonical ZIP은 2026-10-24T08:02:40Z에 Science S896800b4511f323ad3f0b5372b4912fb4770ea98 및 central M1c664c1546a077feade7f4bb6896073d1f47267a9를 포함해 고정했다. 250payload/251members의 검증 범위가 그 시점의 파일 집합이다.

그 뒤 발생한 원격 R3 영수증, Drive60.002s no-ACK/정확한조회0, 최종 Documents D와 central M2는 frozen ZIP의 기존 bytes를 바꾸지 않는다. D의 새 delivery 문서는 Git 고정 commit으로 게시하고, terminal authority에 정확한 D/M2 SHA와 문서 payload를 함께 저장한다. Terminal JSON 자체는 별도의 Library/Dropbox 실제-byte R3로 전달한다. 그 파일의 자체 ID/해시는 외부 terminal receipt로 결속하며 자기 해시를 자기 내용에 넣지 않는다.

복원 순서는 canonical ZIP의 manifest 검증 → D 문서/정확한 post-canonical payload → terminal authority의 S/D/M1/M2와 backup identity 확인이다. 보존된 v1 비용/실행 수와 NOT_RECOVERED 상태, v2 grid FAIL, 과거 Drive UNKNOWN은 그대로 유지한다. 이 순서는 새 과학 실행이나 기존 suite replay를 요구하지 않는다.
