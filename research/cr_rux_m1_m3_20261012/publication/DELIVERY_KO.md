# 게시 및 전달 확인 — CR-RUX-M1-M3-REUSE-20261012

검토된 과학 source commit은 `dfdef60b4967466f2dccabbba6bbdad9ad7cd068`, tree는 `391a83d5f1c784728c09b4656c0e594375657f6f`다. [Draft PR44](https://github.com/cosmosapjw-quantum/bass_cr/pull/44)는 PR43의 M0 이차 응답 branch를 기반으로 한다. 이 파일을 포함한 후속 commit은 게시·백업 영수증만 추가한다. 유도·계산 코드·원자 입력·M2 결과 및 독립 검토 후보는 바꾸지 않는다.

## 현재 전달본

- 파일: `BASS_CR_RUX_M1_M3_20261012_dfdef60b.zip`
- 크기: 965,246 bytes
- SHA256: `0ebad6b122c83b08b713e2863971037d8873947ab34836d9c2337a022a221a05`
- 내용: 현재 연구의 코드·선택 source·입력·결과·검토와 재개 문서, 총 142 archive member
- [Google Drive](https://drive.google.com/file/d/1l7m8wO1zTyVOEIt5Mo7obyjnYsQG4Niv/view)
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_RUX_M1_M3_20261012_dfdef60b.zip`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4Rig`

로컬에서는 archive CRC와 각 member의 SHA256·크기·경로를 확인했다. Drive와 Dropbox에서는 성공 응답·원격 ID·대상 경로·965,246-byte 크기를 확인했다. 제공된 metadata에 원격 checksum이 반환되지 않았으므로 그 값이 비교되었다고 주장하지 않는다. 기본 R1 선택 검증을 적용했고 원격 파일 본문을 다시 내려받지 않았다. 이 상태는 raw-byte restore 검증과 구분한다.

현재 ZIP은 이 경량 연구 단위의 전달본이다. 이전 약 68 MB PHYS02H 전체 payload는 현재 HANDOFF.json의 기존 ID와 SHA를 따른다. 이 ZIP의 백업 영수증은 사후 publication commit에 저장하여 자체 archive hash와 순환 참조하지 않는다.

## 게시 과정

초기 일반 HTTPS git push는 자격증명 부재로 exit 128이었다. 연결된 GitHub 기능으로 blob·tree·commit·branch를 생성하고, 원격 tree가 검토한 로컬 tree와 정확히 같음을 확인했다. GitHub의 commit 메타데이터로 인해 미게시 로컬 commit과 원격 commit SHA는 다르지만 source tree는 같다. 미게시 로컬 commit은 `local/cr-rux-review-20261012`에 보존했다. 생성된 branch의 원격 head도 확인했고 source branch를 그 commit으로 채택했다.

이 과정은 게시 경로의 문제였으며 과학 계산을 다시 실행하지 않았다. 상세 기록은 GITHUB_CLI_PUSH_FAILURE.json, GITHUB_SCIENCE_PUBLICATION.json, DELIVERY_WORKFLOW_NOTES.json에 있다. main은 merge하지 않았고 다른 저장소는 변경하지 않았다.

다음 경량 작업은 M1_ELECTRON_SOURCE_BINDING과 실제 소비자의 observable budget 연결이다. 새 NCP 과학 job은 0이며 기존 M0·M2 및 과거 OFF 검사를 반복하지 않는다.
