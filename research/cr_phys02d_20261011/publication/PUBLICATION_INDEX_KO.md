# CR-PHYS02D 실제 publication 영수증

Science PR: [https://github.com/cosmosapjw-quantum/bass_cr/pull/32](https://github.com/cosmosapjw-quantum/bass_cr/pull/32) (PR #32). 실제 science commit은 `6ed83ff61aff24fe51ff0370736f70e0e52893f8`, tree는 `0c481f344a18bb7fc67444ffcce880f4d04bd581`이다. 직접 science base는 PR #31 commit `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31`, tree `ae9c5ea98edd724423bfa8cb79db976908d1c123`이다. 이 receipt-only 후속 자료는 실제 science commit을 부모로 하며, 이 후속 commit 자신의 미래 ID는 여기 기록하지 않는다.

## Immutable handoff ZIP

- 이름: `CR_PHYS02D_20261011_6ed83ff6_HANDOFF.zip`
- 크기: 4903951 bytes
- SHA256: `100e0cf1fec443067b74aed9f8d508f1daae1d117bf9005f57ebcd68e1cf2673`
- Entry 수: 360; 로컬에서 CRC 및 모든 payload bytes/SHA256 검증 완료.
- Drive ZIP ID: `1H3Gn3xb7InyPuXCQKxQtQ1_m02e2OnIW`; [실제 Drive ZIP](https://drive.google.com/file/d/1H3Gn3xb7InyPuXCQKxQtQ1_m02e2OnIW/view?usp=drivesdk)
- Drive folder: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox ZIP ID: `id:BSpOijBcT10AAAAAAD36cQ`; rev `65d8467123fdc0af03d47`
- Dropbox path: `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_20261011_6ed83ff6_HANDOFF.zip`
- Dropbox provider path: `ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_20261011_6ed83ff6_HANDOFF.zip`

Immutable ZIP을 수정하지 않았다. 후속 upload/restore 영수증은 ZIP 밖에 보존한다. ZIP은 dependency-complete repository-layout overlay이며 전체 역사 checkout이 아니다. Mandatory inherited 259 files는 base Git에 대해 고정되어 있다. Sibling-only PHYS02C 후기 receipts의 provenance는 sibling commit `eecb9bdceb40ff8dbb84feba969d1eec6555970f`이며 base ancestor로 주장하지 않는다.

## 실제 backup ID가 들어간 standalone 시작 문서

[로컬 repository 시작 문서](NCP_START_WITH_BACKUP_IDS_KO.md)는 실제 업로드한 standalone `CR_PHYS02D_20261011_6ed83ff6_NCP_START_KO.md`와 바이트가 동일하다.

- 크기: 17801 bytes
- SHA256: `da066f54a1c5e8b630c8f87bbae607954161affb95f79b0b2fb1ad15ce492197`
- [실제 Drive 시작 문서](https://drive.google.com/file/d/1EE11a-gepxjyDELoo8syXZj2k9WY3Lxo/view?usp=drivesdk); ID `1EE11a-gepxjyDELoo8syXZj2k9WY3Lxo`
- Dropbox 시작 문서 ID: `id:BSpOijBcT10AAAAAAD36kw`; rev `65d84714cb8b90af03d47`
- Dropbox path: `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_20261011_6ed83ff6_NCP_START_KO.md`
- Dropbox provider path: `ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_20261011_6ed83ff6_NCP_START_KO.md`

두 목적지에서 ZIP 및 standalone 총 4개 실제 upload가 완료되었으며 실제 metadata readback이 일치했다. 추가 사용자 첨부 없이 시작할 수 있는 exact-ID 전달본이다. 기존 인증된 backup access는 필요하며, 접근 불가 시 scoped blocker를 보고한다.

## Readback 및 실제 실행 범위

원격 검증은 **R1_METADATA**다. 원격 provider checksum은 connector response에서 제공되지 않았다. 원격 다운로드 후 bytes/hash/restore는 수행하지 않았다. 기록한 ZIP SHA256 및 Dropbox content hash는 로컬 expected identity이며 원격 byte readback을 의미하지 않는다.

로컬 immutable archive는 별도 새 디렉터리에 full-byte restore했고, stdlib `--plan` actual exit 0을 확인했다. 전체 manifest payload 359 entries 및 inherited dependency 259 entries가 검증되었으며 `admission_status=READY`다. 이 호스트의 resource probe는 `HOLD`, `admitted=false`였다. 보이는 cgroup 메모리 상한 8 GiB이고 reserve 후 working memory가 필요 12 GiB보다 작았다. Plan 환경 Python 3.12.14는 실제 physics pinned Python 3.12.3 실행 환경 검증을 대체하지 않는다.

물리 G build **0회**, pulse **0회**이며 NCP는 **PREPARED_NOT_EXECUTED**다. Science review 범위는 endpoint와 execution preparation의 `PASS_SCOPED`이며 actual pulse physics PASS를 주장하지 않는다. 실제 수치 return 후 다음 독립 Astra 심사가 필요하다. 기존 scientific gates를 유지한다.

## 영수증과 검토

- [실제 science receipt](SCIENCE_COMMIT_RECEIPT.json)
- [Archive assembly receipt](ARCHIVE_ASSEMBLY_RECEIPT.json)
- [두 backup 실제 receipts](DUAL_BACKUP_RECEIPT.json)
- [로컬 restore/plan receipt](LOCAL_RESTORE_SMOKE_RECEIPT.json)
- [Restore extract stdout](RESTORE_EXTRACT.stdout.json), [stderr](RESTORE_EXTRACT.stderr.log)
- [Restore plan stdout](RESTORE_PLAN.stdout.json), [stderr](RESTORE_PLAN.stderr.log)
- [실제 publication binding](PUBLICATION_BINDING.json)
- [외부 시작 지시문 review record](EXTERNAL_INSTRUCTION_REVIEW_RECORD.json)
- [새 publication 파일 manifest](PUBLICATION_FILE_MANIFEST.json)

`PUBLICATION_FILE_MANIFEST.json`은 이번 신규 publication 파일만 고정하며 자기 자신은 hash cycle을 피하도록 제외한다. 기존 `READBACK_PLAN.json`과 원본 frozen science 88 files는 변경하지 않았다.
