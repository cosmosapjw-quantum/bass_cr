# PHYS02G NCP local Codex 시작 지침

## 지금 수행할 작업

**`CR-PHYS02G-NCP-OPERATOR-PROVENANCE-INTAKE`를 읽기 전용으로 진행한다.** 현재 F는 `HOLD_OPERATOR_BINDING_UNRESOLVED`, G actual frontier는 `BLOCKED_BY_F_OPERATOR_BINDING_HOLD`다. 저장 모멘트 분석의 G 준비 판정은 PASS_SCOPED로 보존한다.

이번 전달은 **추가 첨부 없는 단일 완전 ZIP**이다. G core·기존 완전 F 준비본·실제 E 자료·두 canonical Astra v4.0.0 하네스와, 게시 중 새로 도착한 실제 F 실패 원본·현재 Git snapshot·새 읽기 전용 계약·독립 심사를 함께 담았다. 실제 F를 다시 시작하거나 실패를 성공으로 바꾸지 않는다.

## 정확한 백업과 소스

| 항목 | 실제 값 |
| --- | --- |
| 전체 전달 ZIP | CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip |
| 전체 크기 | 58470931 bytes |
| 전체 SHA256 | 2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707 |
| outer manifest schema | cr-phys02g-late-f-hold-envelope.v1 |
| outer manifest SHA256 | 1ec3c042a86008a59f4867a179980b5e3f59783c6b8d372d99c6b453566c4e18 |
| outer payload / 전체 entry | 79 / 80 |
| Drive ID | 1TrNu23r3VfhvPGjesqATWFpthvhVjTcB |
| Drive 폴더 | 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI |
| Drive 열기 | https://drive.google.com/file/d/1TrNu23r3VfhvPGjesqATWFpthvhVjTcB/view?usp=drivesdk |
| Dropbox ID | id:BSpOijBcT10AAAAAAD4I9A |
| Dropbox 경로 | /BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip |
| Dropbox namespace path | ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip |
| Dropbox revision | 65d8b6ea41a810af03d47 |
| G science commit | 0ad3be0fec018fbd638063ffd4bf4d0cf2ef8525 |
| G science tree | b4ba1be466d5d62ab7572076387113d2277948ff |
| G 게시 branch | research/cr-phys02g-moment-frontier-20261011 |
| G draft PR | https://github.com/cosmosapjw-quantum/bass_cr/pull/38 |
| 실제 F 반환 PR / head | 37 / a490ab7af8e7b1b4db9a604293867df8e6d035dd |
| G core FILE_MANIFEST SHA256 | 5bc6cfed11a1e29271347f039168f10d4339dd21a0c0874e156e3a6c77dac727 |
| G 준비 독립 판정 SHA256 | 9dd9c623fdd881667b6692ea8c3c9fbac08d545ba821fe33f66c2dbd38322002 |
| 새 읽기 전용 계약 SHA256 | eebca369dbb01b6ad678e110866f919bdd07c7692850330df55f3deab99df0ba |
| 새 독립 판정 SHA256 | ba4d6e012a2522cce97c9c9acf9f9976c380d0cba0f4a60aaa306998a8a0b1e2 |
| 새 독립 판정 | PASS_SCOPED_READ_ONLY_PREPARATION |

두 provider는 업로드 성공, 정확한 ID·이름·크기·폴더/경로와 제공된 revision을 확인했다. Metadata tool은 provider checksum을 제공하지 않았다. 위 전체 SHA256은 완성 로컬 ZIP의 실제 값이다. 이 R1 결과를 새 원격 ZIP의 raw byte 복원이나 수신자 실행 확인으로 부르지 않는다.

## 1. 한 파일로 복구

기존 승인된 Drive/Dropbox 연결 또는 실제 확인된 rclone remote를 사용해 위 정확한 백업 하나를 가져온다. remote alias·계정·파일 위치를 추측하지 않는다. 이미 같은 전체 크기·SHA256 파일이 있으면 재다운로드하지 않는다.

전체 ZIP 크기·SHA256을 먼저 대조한다. 새 빈 root에 복구하며 절대경로·parent traversal·중복 entry·symlink·비정규 member를 거부한다. outer `BUNDLE_MANIFEST.json`에서 열거한 payload와 manifest 자신 하나가 정확한 전체 집합이어야 하고, 모든 bytes·SHA256이 일치해야 한다. 기존 dirty checkout·source·run·return 위에 덮어쓰지 않는다.

먼저 다음 파일을 읽는다.

- README_CURRENT_NCP_KO.md
- late_f/CURRENT_NEXT_ACTION.json
- late_f/LATE_F_INTEGRATION_KO.md
- late_f/NCP_READONLY_DIAGNOSTIC_CONTRACT.json
- late_f/FINAL_READONLY_HANDOFF_DECISION.json
- late_f/INDEPENDENT_LATE_RETURN_ASSESSMENT.json
- late_f/R3_RESTORE_RECEIPT.json
- late_f/SOURCE_SNAPSHOT_RECONCILIATION.json

각 internal contract/review hash를 위 값 및 outer manifest와 대조한다. CURRENT_NEXT_ACTION은 실제 준비 판정의 hash를 연결한다.

내장 G core는 `payload/CR_PHYS02G_20261011_0ad3be0f_HANDOFF.zip`, 27,795,932 bytes, SHA256 `21c60d3d3f7193f2e957f17f2b610a306d0d85eaed08c90a52c0da8c5a1e602b`다. 필요할 때 별도의 빈 G source root에 복구하고 inner manifest `cr-phys02g-self-contained-bundle.v1`, core FILE_MANIFEST와 SCIENCE_COMMIT_RECEIPT를 검증한다. 그 안에 기존 F 완전본 ZIP과 실제 E/canonical 의존 자료가 있다.

새 실제 F 원본은 `payload/CR_PHYS02F_LOCAL_OPERATOR_BINDING_HOLD_REMOTE_20261011T0700Z.tar.gz`, 30,522,967 bytes, SHA256 `0b6d54f5811f4f8ee651a79e734c9dddf37a722133bd51acad3fcf16c110a4e5`다. 별도의 빈 root에서 tar의 일반 파일·디렉터리만 허용하고 symlink·hardlink·중복·traversal을 거부한다. 원본 F/return family, 외부 sidecar와 내부 numerical ZIP을 정확히 검증한다. Numerical ZIP SHA256은 `f64b263fd8dd99121d3114a66a2a70616b383cbd5ce0823acd45f9893babdd8d`다.

현재 PR37의 정확한 47-file source snapshot은 late_f/git_publication_snapshot/ 아래에 별도로 있다. 원본 tar와 현재 snapshot의 차이는 정상화하지 않는다. 원래 tar는 41개 Git blob이 일치하고 4개 publication 파일이 없으며 2개 staged 요약이 달랐다. 새 snapshot은 47/47 exact Git blob으로 연결된다. 원본과 publication 시점의 자료를 구분하여 보존한다. 관련 없는 tar metadata 프로젝트 내용으로 작업 범위를 넓히지 않는다.

## 2. 이미 소비된 F 실패를 기준으로 시작

F actual은 2026-10-11 06:41:06–06:42:54 UTC에 fullBED G 예약/완료 1/1 뒤 exact operator parity에서 실패했다. Resolvent·solve·pulse·expm은 0, execute/collect/wrapper exit은 1/0/1이다. Coordinator 107.954172934초와 wrapper 109.790418950초는 중첩이며 합산하지 않는다.

기준 G.data SHA는 `6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd`, 실패한 current SHA는 `8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa`다. Shape 9611×9611, nnz 36,193,027, energy·indices·indptr·method bindings는 일치했다. 전체 G의 hash 차이만으로 active matrix 또는 heat row 중 어느 부분이 변했는지는 알 수 없다.

과거 G 내부 START의 “F actual not observed”, WAITING 및 “미예약이면 최초 실행”은 이전 후보 고정 시점의 기록이다. 이번 실제 실패에 그 최초 실행 분기를 적용하지 않는다. F reset, legacy 후속 실행, nominal 잔여 allowance 소비, 새 G 재구축 또는 G frontier --execute를 하지 않는다.

## 3. 읽기 전용 진단 계약 실행

진단 명령 창은 **180초**다. source 복구·전송·무결성 검증 시간은 별도 기록한다. 원래 E/F runtime과 기존 호스트의 실제 library/build/CPU-dispatch provenance를 읽고 경로·버전·관련 파일 hash를 남긴다. 필요한 비밀이 아닌 runtime 변수만 확인한다. BLAS dispatch를 강제하거나 환경·패키지·소스를 바꾸지 않는다. 관측된 SkylakeX/Haswell 차이를 원인이나 오차 크기로 단정하지 않는다.

현재 반환에는 두 원래 CSC 값이 없다. 기존 기록에서 확인된 NCP run/cache 위치의 보존 파일만 조사한다. 같은 reference fingerprint의 E cache가 있어도 출처가 연결되지 않으면 새 입력 후보일 뿐이며 채택하지 않는다.

**양쪽 원래 저장 CSC가 모두 존재하고 각각 exact raw identity가 연결될 때만**, 전체 180초 안에서 저장 배열 비교를 최대 **1회·90초** 수행한다. Block은 최대 262,144 entry다. 먼저 structure를 대조하고 차이 개수·첫 좌표·최대 절대 차이·zero-aware 상대 차이·finite same-sign ULP를 기록한다. Zero·sign·nonfinite는 따로 분류하고 signed 차이를 유지한다. 비교 코드를 실행했다면 코드 identity와 실제 command·UTC·wall·exit·stdout/stderr도 보존한다.

한쪽이라도 없으면 `MISSING_PERSISTED_OPERATOR_VALUES`와 실제 조사 범위를 반환한다. Hash만으로 numerical difference를 만들어내지 않는다. Clipping, 임의 floor, 허용오차 변경, 기준 SHA 교체는 없다.

이번 과제의 **G·resolvent·solve·pulse·expm·F retry·G frontier 실행은 전부 0**이다. 새 물리 실행은 실제 입력·허용기준·누적 예산이 명시된 별도 유한 계약과 독립 심사를 필요로 한다. 읽기 전용 진단의 성공만으로 현재 F/G HOLD를 해제하지 않는다.

## 4. 독립 판정과 완전한 반환

프로젝트에 채택된 canonical Astra v4.0.0 흐름과 역할 분리를 보존한다. 후보·계약·물리 해석은 Astra, 고정 계약의 기계적 구현은 lower worker, 최종 판정은 후보·허용조건·구현에 참여하지 않은 independent Astra다. 모델 label과 backend 관측을 구별하고 Pro 접미사로 exact alias를 만들지 않는다.

기존 G-R01을 유지한다. FP64에서는 10개 horizon 끝점 조건이 통과했지만 exact decimal-token 비교에서는 8개 구간의 적어도 한 끝점 부호가 약 1e-17 확률 여유에서 달랐다. Raw 구간을 directed-rounding exact-input 인증, forward-error 또는 물리 불확실성 구간으로 보고하지 않는다.

PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다.

반환에는 현재 완전 전달본 또는 그 정확한 원본 payload, 실제 F family 전체, 이번 진단의 원시 증거·코드·source/runtime identity·실제 종료와 새 독립 판정을 함께 담는다. Source pointer만으로 완전 반환을 대신하지 않는다.

Git 반환 전에 위 G branch의 실제 최신 head가 science commit의 descendant이며 후속 변경이 publication 범위인지 확인한다. 그 head에서 새 additive return branch와 draft PR을 만든다. merge·force push·history overwrite는 없다. 기존 Drive/Dropbox 폴더에 완전한 outer return과 짧은 시작 파일을 고유 이름으로 저장한다. R1 업로드 확인과 실제 source 복구 R3를 구분한다.

최종 보고에는 실제 읽기 전용 조사 범위, 두 CSC 값의 존재·부재 및 identity, 원인/오차에 대해 알 수 있는 범위, 실행·비실행과 actual exit, 유지 HOLD, 새 PR/head/tree와 두 백업의 정확한 ID·크기·SHA256을 담는다. 사용자에게 기존 파일을 다시 첨부하도록 요구하지 않는다.
