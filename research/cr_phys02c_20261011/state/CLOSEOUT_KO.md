# CR-PHYS02C 실제 publication closeout

독립 최종 판정은 **PROMOTE_SCOPED**이며 root는 그 조건부 범위만 채택했다. 과학 commit은 `f34a0cc1484247caf252afde3d5fbe834640e9e4`, tree는 `72ccd199e1a2496dd345a7d44b8f8440dc0f00db`다. 별도 research branch와 [draft PR #28](https://github.com/cosmosapjw-quantum/bass_cr/pull/28)를 실제 생성했고 R1 exact ref/commit/tree/parent metadata readback이 일치했다. merge 또는 production 승인은 아니다.

## 실제 인계와 백업

완전 ZIP은 `CR_PHYS02C_20261011_f34a0cc1_HANDOFF.zip`, **3,251,044 bytes**, SHA256 `cd47c755730bd208d7b5360fb18e53351f63af481055994e5c8bcdb355b961fb`다. ZIP과 exact locator가 들어 있는 standalone NCP 시작 문서를 Drive와 Dropbox에 각각 create-only로 업로드했다. 실제 생성 파일은 총4개이며 ID·경로·이름·크기·parent/revision metadata를 R1 수준에서 확인했다. provider digest는 실제 metadata에 없었고, 전체 remote bytes를 재다운로드해 복원한 검사는 수행하지 않았다. 업로드 metadata 확인과 원격 byte 복원은 구별한다.

로컬에서는 immutable ZIP을 새 격리 디렉터리에 실제 추출하고 **235 payload hash/size**를 검증했다(전체 ZIP236 entries, self-excluded BUNDLE manifest 포함). 복원본 launcher `--plan` actual exit0 및 READY review/DAG/payload admission을 확인했다. 실제 수송은0회다. 이 로컬 cgroup 제한은8GiB이므로 NCP 최소12GiB working availability를 만족하지 못했고 resource admission은 HOLD였다. 이 상태를 NCP의 실제 용량이나 실행 결과로 해석하지 않는다.

다음 `CR-PHYS02C-NCP-MATCHED-THIRD-GRID`는 READY지만 **조건부 runtime admission**이다. NCP 실행은 **PREPARED_NOT_EXECUTED**이며 실제 capacity는 관측하지 않았다. 완전 다운로드 manifest 및 저장된 두 reference identity, cgroup ancestry, reserve/RAM, CPU/disk, numerical thread1 검사를 통과해야 한다. 동일 물리·FP64·허용값에서 순차2회 수송과3600s 제한을 유지한다.

## 불변 범위와 정확한 receipt

기존 scientific FILE_MANIFEST의104 listed 파일과 REVIEW_PACKET의95 listed 파일은 모두 변하지 않았다. 이 closeout은 뒤에 추가하는 receipt 파일만 기록하며, 원래 과학 snapshot을 재작성하지 않는다. 새7개 receipt/closeout 파일은 `../publication/RECEIPT_FILE_MANIFEST.json`에 개별 SHA256과 byte size로 기록하고 manifest 자신의 hash는 제외한다.

실제 근거는 `../publication/SCIENCE_COMMIT_RECEIPT.json`, `ARCHIVE_ASSEMBLY_RECEIPT.json`, `LOCAL_RESTORE_SMOKE_RECEIPT.json`, `DUAL_BACKUP_RECEIPT.json`, `CR_PHYS02C_20261011_NCP_START_KO.md`다. immutable ZIP에는 이후 dual-backup receipt 또는 receipt commit SHA를 소급해서 넣지 않는다. 이 addition-only receipt commit의 정확한 self identity는 Git이 commit 생성 시 결정하며, 생성 후 외부 final delivery receipt에서 기록한다. 자기 commit의 SHA를 미리 만들어 넣지 않는다.

PHYS02_DELAY **OPEN**, production_history **HOLD**, atomic_G02 **UNRESOLVED**, b_grid **NO_GO**, all_bound **OPEN**, R17B2B **NO_CERTIFIED_SOURCE_SHARPENING**은 유지한다. CCC target-energy identity, NIST Q lineage/CGI, 원자 완전성 및 production 이력은 이번 publication으로 닫히지 않는다. 모델 성능은 NOT_EVALUATED다.
