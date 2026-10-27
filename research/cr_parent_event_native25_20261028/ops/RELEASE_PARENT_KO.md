# PR111 / parent-event 단위의 봉인·인계 helper

대상은 `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`, `research/cr_parent_event_native25_20261028` 하나다. `release_parent.py`는 파일 포장과 명시적 R3 읽기만 담당한다. 과학 모듈 import, scientific replay, 원천 재계산, Git 쓰기, 업로드, Library 작업, 다음 단위 실행을 하지 않는다. **현재 작성·정적 판독만 했으며 helper 실행, ZIP 생성, GET, 업로드는 하지 않았다.** 작성 작업의 metadata CPU는 미측정이다. 이 문서는 C09/S, C10/D, 중앙 M 또는 과학 PASS 수를 미리 확정하지 않는다.

## 적용 근거와 기존 코드

- `bass_cr/AGENTS.md`: SHA256 `bf1b921550473363df97f75bbbfc2e839120990f89a330b35da66867695f17b5`.
- `bass_cr/docs/READBACK_POLICY.md`: SHA256 `8d30839c0a99732754b82f3d0eeef195770b928a9dde8bafe1c17dff4b20afdc`.
- 참조한 `next_ops/build_closeout.py`: SHA256 `7d30566e088fb33cba40e95ffe3c0d8543dc371e2ab46fffa580d1291e34d699`.
- 참조한 `next_ops/raw_r3.py`: SHA256 `3cfb032a616cc5a3d71cb5c60416511fc7e757cba55c3489887636aacf7a4e7c`.
- 참조한 `next_ops/git_r3.py`: SHA256 `911a35eda26344011a2a49d459004c8ed206ff83650e5c0f79d0f24dffa49e6f`.

기존 helper를 import하거나 수정하지 않았다. create-only ZIP, member SHA/CRC, 실제 원본 GET 구조를 현재 unit용 표준 라이브러리 코드로 옮겼다. 문서가 가리키는 `.codex/readback-policy.json`은 조사한 local/HEAD에 없었다. 현재 실제 AGENTS·READBACK_POLICY와 사용자의 canonical release/R3 명시적 지시를 따른다. 이 helper를 실제 실행하기 전에 root가 최신 정책·HEAD·owner 변화와 게시 영수증을 확인한다.

## 모든 명령의 공통 계약

각 명령은 **아직 존재하지 않는 절대경로 `--attempt-dir`**를 요구한다. 이 디렉터리는 current unit 밖이어야 한다. 모든 산출물은 create-only이며, 입력 파일과 기존 archive를 덮어쓰지 않는다. `START.json`을 먼저 만들고, 성공 또는 포착된 실패에 `TERMINAL.json`을 쓴다. START만 남으면 `UNKNOWN_NO_ACK`다. 실패 ZIP·부분 다운로드·개별 provider receipt를 삭제하지 않으며 자동 재시도하지 않는다. argparse 실패나 이미 존재하는 attempt namespace 거절은 새 attempt 안에 기록할 수 없으므로 호출자의 process receipt에 남겨야 한다.

입력 파일은 absolute path, regular file, non-symlink여야 한다. archive path는 relative POSIX path여야 하며 `..`, 빈 component, absolute path, backslash, colon, control character, `MANIFEST.json` 충돌을 거절한다. case-fold duplicate와 file/directory prefix 충돌도 거절한다. 로컬 바이트는 inode·size·mtime_ns를 읽기 전후 대조한다. JSON duplicate key와 NaN/Infinity도 거절한다.

캐시·private 이름은 단위 inventory에서 제외하고 그 경로와 이유를 SOURCE plan/manifest에 기록한다. 이미 Git에 게시된 private/cache 경로는 조용히 누락하지 않고 거절한다. 실제 signed transport URL 내용은 입력/포장 경로에서 거절한다. provider 원본 URL response는 명시적인 private R3 입력으로만 읽으며 URL·token·HTTP 오류 body를 stdout이나 공개 receipt에 쓰지 않는다. 이 규칙은 비밀정보 탐지의 완전성 보증이 아니므로 root가 explicit extras/closeout 목록을 검토한다.

## 1. C09 실제 S에서 SOURCE plan

다음 명령은 **C09가 실제 게시되고 dual R2가 끝난 뒤**, C10 전에만 사용한다. 아래 `ACTUAL_*`는 명령 설명용 표식이며 helper는 실제 40/64자리 값과 실제 파일만 수용한다. 경로는 모두 절대경로로 전달한다.

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py source-plan \
  --repo-root /workspace/scratch/865c84d871b7/bass_cr \
  --S ACTUAL_S_40HEX \
  --state /workspace/scratch/865c84d871b7/parent_ops/pub_state.json \
  --c09-receipt /workspace/scratch/865c84d871b7/bass_cr/research/cr_parent_event_native25_20261028/publication/C09_RECEIPT.json \
  --published-paths /workspace/scratch/865c84d871b7/parent_ops/published_paths.json \
  --attempt-dir /workspace/scratch/865c84d871b7/parent_release_source/source_plan_v1
```

필요하면 `--extras /absolute/EXTRAS.json`을 덧붙인다. extras는 다음 exact-key 객체의 **명시적 ordered list**다.

```json
[
  {
    "local_path": "/absolute/current/public/receipt.json",
    "archive_path": "release_metadata/receipt.json"
  }
]
```

plan은 다음 실제 증거를 요구한다.

1. repo·branch가 현재 unit과 일치하고, R01–R10/C01–C09의 정확한 19단계 parent chain·ref ACK·non-force·양 provider ACK/ID/size/R2가 있다. C09 receipt와 state의 마지막 row는 동일해야 한다.
2. local Git HEAD가 S이고 C09 tree가 실제 local S tree와 같다. 없는 object를 자동 fetch하지 않는다.
3. Git S tree의 **모든 current-unit 파일** 및 `published_paths`의 실제 파일을 immutable Git blob으로 읽는다. 로컬에 같은 게시 경로가 있다면 S 바이트와 같아야 한다.
4. current unit 전체의 non-cache/non-private 파일을 포함한다. 따라서 모든 현재 `runs/`, 실패한 attempt, debit·lease·snapshot, resource/preworker 기록과 post-C09 receipt도 존재하는 그대로 들어간다. 경로가 같고 게시 바이트와 다른 파일은 source를 임의로 덮지 않고 거절한다.
5. R1 `INPUT_MANIFEST.json`의 정확한 17 source payload를 bytes/SHA로 대조해 포함한다. 고정 manifest SHA는 `2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3`, CONTRACT SHA는 `01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162`다. 이 값이 바뀌면 이 helper의 현재 계약이 맞지 않으므로 root가 새 actual identity를 먼저 심사해야 한다.
6. `pub_state.json`의 S 시점 사본과 실제 helper 소스를 각각 `release_metadata/PUBLICATION_STATE_AT_S.json`, `release_ops/release_parent.py`로 추가한다. workspace 전체나 이전 units 전체를 glob하지 않는다.

`SOURCE_PLAN.json`은 실제 origin, size, SHA256, CRC32, S Git blob identity와 exclusions를 기록한다. **경로가 S에 존재한다는 사실만으로 Git-published라 하지 않는다.** archived bytes의 Git blob hash까지 S와 같을 때만 `git_published_at_S`다. 이로써 이전 Git에 이미 존재하는 17 payload도 정확하게 분류하며, archive-only NPZ/JSON을 raw Git에 존재한다고 주장하지 않는다.

plan 작성만으로 ZIP을 만들지 않는다. root는 plan의 actual paths/exclusions 및 실패 기록의 포함 여부를 검토하고 실제 plan SHA를 다음 명령에 넣는다.

## 2. Canonical SOURCE를 한 번 봉인

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py source-build \
  --plan /workspace/scratch/865c84d871b7/parent_release_source/source_plan_v1/SOURCE_PLAN.json \
  --plan-sha256 ACTUAL_PLAN_SHA256 \
  --attempt-dir /workspace/scratch/865c84d871b7/parent_release_source/source_build_v1
```

생성 이름은 정확히 `BASS_CR_PARENT_EVENT_SOURCE_20261028_{S12}.zip`이다. `ZipFile(mode='x')`를 사용하고, fixed ZIP metadata와 원문 바이트를 보존한다. `MANIFEST.json`은 `schema`, `kind`, `identity`, `files:[{path,bytes,sha256,crc32,...}]`, `git_published_paths`, `archive_only_paths`, 17 source paths를 가진다. 이전 `raw_r3.py`의 files/path/bytes/SHA/optional CRC 구조와 호환되지만 현재 unit의 실제 검증에는 이 helper의 explicit R3 명령을 사용한다.

build 전후에 controls pins, local HEAD, unit inventory, 모든 로컬 snapshot/bytes, 17 payload와 실제 Git 분류를 다시 대조한다. plan 이후 새 run·실패 receipt가 생기거나 frozen 파일이 바뀌면 실패한다. 이런 파일을 자동으로 빼지 않는다. 모든 member의 bytes/SHA/CRC, manifest SHA 및 `testzip()`을 읽어 확인한 뒤에만 `ARCHIVE_RECEIPT.json`을 쓴다. receipt의 `.archive`를 기존 root-owned `dualBackup(key, archive)`에 넘길 수 있다.

동일 S를 새 attempt namespace에서 재포장하는 것도 막기 위해 repo의 parent에 다음 create-only claim을 만든다.

```text
parent_release_source/seal_registry/{S}/CLAIM.json
parent_release_source/seal_registry/{S}/SEALED.json
```

claim 뒤 실패·중단되면 claim과 부분 산출물을 보존한다. 이 helper는 claim을 지우거나 stale이라고 간주하거나 자동 재시도하지 않는다. root가 actual bytes/receipts를 조사해 기존 archive의 회수 가능성을 판단해야 한다. 성공한 SOURCE를 이후 C10·중앙·Library·final receipt 때문에 재작성하지 않는다.

## 3. 실제 양 provider full GET R3

먼저 root가 기존 `parent_ops/dual_backup.js`로 actual 업로드와 size/ID/R2 receipt를 만든다. helper는 업로드하지 않는다. 이어 root가 각 provider의 원본 download link를 실제 취득하고, 원문 response는 private 파일에 보관한다. 공개 acquisition 기록은 다음 구조를 사용한다. 아래 값은 스키마 설명용이며 실제 tool request·raw response pin으로 채운다.

```json
{
  "schema": "CR_PARENT_EVENT_ORIGINAL_LINK_ACQUISITION_V1",
  "unit": "CR_PHYS02_PARENT_EVENT_NATIVE25_V1",
  "archive_sha256": "ACTUAL_ARCHIVE_SHA256",
  "providers": [
    {
      "provider": "Dropbox",
      "id": "ACTUAL_DROPBOX_ID",
      "original_file": true,
      "actual_request": {"entries": ["ACTUAL_DROPBOX_ID"]},
      "raw_response": {"path": "/absolute/SOURCE_Dropbox_raw_private.json", "bytes": 123, "sha256": "ACTUAL_RAW_RESPONSE_SHA256"},
      "url_pointer": "/entries/0/download_url",
      "id_pointer": "/entries/0/id"
    },
    {
      "provider": "Drive",
      "id": "ACTUAL_DRIVE_ID",
      "original_file": true,
      "actual_request": {"url": "https://drive.google.com/file/d/ACTUAL_DRIVE_ID/view", "download_raw_file": true, "include_base64": false},
      "raw_response": {"path": "/absolute/SOURCE_Drive_raw_private.json", "bytes": 456, "sha256": "ACTUAL_RAW_RESPONSE_SHA256"},
      "url_pointer": "/file_uri/download_url",
      "id_pointer": null
    }
  ]
}
```

`123/456`은 예시이며 실제 file size를 넣어야 한다. 원문 tool response의 구조가 다르면 JSON pointer를 **실제 구조에 맞게** 지정한다. Dropbox는 raw response ID까지 필수 대조하며, 실제 request에서 사용한 유효한 `expiration_in_sec`도 허용한다. Drive response에 원본 ID가 있으면 `id_pointer`를 지정하고, 없으면 actual request의 canonical file URL에 들어 있는 ID·원문 response SHA·업로드 ID에 결속한다. Drive connector의 실제 인자는 `url`이며 `download_raw_file=true/include_base64=false`를 요구하고 export MIME 변경은 허용하지 않는다. raw response의 임시 download URL 자체를 이 공개 acquisition JSON에 복사하지 않는다. 이 provenance record는 root가 실제 취득 호출에서 작성하는 증거이며 helper가 그 호출을 소급 수행했다고 주장하지 않는다.

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py provider-r3 \
  --archive-receipt /absolute/source_build_v1/ARCHIVE_RECEIPT.json \
  --backup-receipt /workspace/scratch/865c84d871b7/parent_ops/SOURCE_backup_pending.json \
  --acquisition /absolute/SOURCE_LINK_ACQUISITION.json \
  --attempt-dir /workspace/scratch/865c84d871b7/parent_release_source/source_R3_v1
```

두 provider는 각각 전체 GET를 수행한다. HTTP 200, Range/partial response 없음, unmodified body, 정확한 archive size/SHA, manifest membership/order, 모든 payload bytes/SHA/CRC 및 ZIP CRC를 확인한다. 실제 원본 다운로드를 별도 파일로 보존한다. provider 하나가 실패해도 다른 provider의 실제 결과와 개별 receipt를 남긴다. combined `DUAL_R3.json`은 둘 다 PASS일 때만 `both_original_full_GET_and_all_members_PASS=true`다. 한 번의 연결 timeout은 55초이며 자동 재시도는 없다. R2 receipt나 로컬 archive 검사만으로 R3를 표시하지 않는다.

## 4. 실제 Git S 공개 경로의 selective R3

root가 실제 대상 경로의 unique JSON array를 준비한다. 이 목록은 sealed SOURCE의 `git_published_paths` 부분집합이어야 한다. archive-only 대상은 네트워크 호출 전에 거절한다.

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py git-r3 \
  --source-receipt /absolute/source_build_v1/ARCHIVE_RECEIPT.json \
  --paths /absolute/S_GIT_R3_PATHS.json \
  --attempt-dir /workspace/scratch/865c84d871b7/parent_release_source/S_GIT_R3_v1
```

공개 raw Git endpoint에서 immutable S 경로를 GET하고, sealed SOURCE가 보유한 실제 S blob의 bytes/SHA256/Git blob SHA1과 대조한다. C10 이후 달라질 수 있는 working-tree 파일을 oracle로 쓰지 않는다. 모든 대상의 실제 receipt를 따로 남기며 선택되지 않은 경로까지 읽었다고 주장하지 않는다. D/M의 별도 Git readback은 root의 actual 해당 commit helper/절차로 수행한다.

## 5. D/M 이후의 별도 CLOSEOUT

identity JSON은 아래 **exact keys**만 허용한다.

```json
{
  "schema": "CR_PARENT_EVENT_CLOSEOUT_IDENTITY_V1",
  "unit": "CR_PHYS02_PARENT_EVENT_NATIVE25_V1",
  "S": "ACTUAL_S_40HEX",
  "D": "ACTUAL_D_40HEX",
  "M": "ACTUAL_M_40HEX"
}
```

`CLOSEOUT_INPUTS.json`은 extras와 같은 `{local_path:absolute,archive_path:safe_relative}`의 **명시적 ordered list**다. 디렉터리를 glob하지 않는다. 아래 mandatory role 파일이 모두 목록에 실제로 있어야 한다. stage별 actual receipts/UNKNOWN records/최종 예산·review/source R3·최종 owner observation 등 추가 자료도 root가 명시해서 넣는다. 이미 SOURCE에 있는 scientific runs를 다시 계산하거나 SOURCE를 중첩하여 재포장하지 않는다.

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py closeout \
  --identity /absolute/CLOSEOUT_IDENTITY.json \
  --inputs /absolute/CLOSEOUT_INPUTS.json \
  --state /workspace/scratch/865c84d871b7/parent_ops/pub_state.json \
  --source-receipt /absolute/source_build_v1/ARCHIVE_RECEIPT.json \
  --source-r3 /absolute/source_R3_v1/DUAL_R3.json \
  --central-receipt /absolute/CENTRAL_PUBLICATION_RECEIPT.json \
  --central-git-r3 /absolute/M_GIT_R3.json \
  --central-return /absolute/ACTUAL_PUBLISHED_OWNER_RETURN.json \
  --handoff /absolute/HANDOFF_CLOSEOUT_PREIMAGE_KO.md \
  --report /workspace/scratch/865c84d871b7/bass_cr/research/cr_parent_event_native25_20261028/REPORT_KO.md \
  --attempt-dir /workspace/scratch/865c84d871b7/parent_release_closeout/closeout_build_v1
```

실제 C09=S/C10=D parent chain, 20단계 양 R2, SOURCE identity/실제 dual R3, 중앙 S/D/M/ref ACK/non-force/CR effect0 및 88 nodes/17 edges를 확인한다. 중앙 완료 수는 실제 receipt에서 읽고 status 문자열을 세지 않는다. 중앙 receipt는 이전 publisher와 같은 `science_commit_S`, `documents_commit_D`, `commit_M`, `actual_remote_ref`, `expected_parent`, `nodes`, `integration_edges`, `original_central_completed`, `original_central_total`, `count_effect`, `reviewed_identity`, `paths` 필드를 요구한다. `reviewed_identity.unit/S/D`가 현재 단위에 결속되어야 한다. 중앙 raw R3는 actual M의 정확한 DAG+owner-return 두 경로여야 하고, 제공한 owner-return 바이트가 그 실제 M blob과 같아야 한다.

과학 PASS 수·CPU 값은 helper에 하드코딩하지 않는다. actual report/ledger/review를 그대로 보존한다. 이전 27/88과 foreign B3h 기여, 현재 중앙 count, CR0, PR236 별도 count 등 상세 의미는 root의 실제 중앙 receipt/owner-return/report에 담긴다. helper는 다른 프로젝트의 숫자를 합산하지 않는다.

생성 이름은 `BASS_CR_PARENT_EVENT_CLOSEOUT_20261028_{D12}_{M12}.zip`이다. SOURCE ZIP은 read-only로 확인하며 그 자체를 CLOSEOUT payload로 넣는 것도 거절한다. CLOSEOUT에는 SOURCE bytes/SHA/provider identity와 actual receipt가 들어간다. CLOSEOUT 자신의 미래 bytes/SHA/provider IDs/Library/R3는 manifest에서 null이다. 실제 후속 archive receipt와 final handoff가 이를 제공하며, 그 때문에 SOURCE/CLOSEOUT을 다시 만들지 않는다.

CLOSEOUT도 동일 `provider-r3` 명령으로 actual 양 provider R3를 수행할 수 있다. `verify-local` 명령은 로컬 파일 재검사만 수행하고 provider R3가 아님을 명시한다.

```bash
python3 /workspace/scratch/865c84d871b7/parent_ops/release_parent.py verify-local \
  --archive-receipt /absolute/ARCHIVE_RECEIPT.json \
  --attempt-dir /absolute/local_verify_v1
```

## 제한과 root의 마지막 확인

- 현재 코드는 작성·정적 판독 단계다. 실행·compile·archive build·GET 검증을 완료했다고 하지 않는다. 실제 C-stage 비용·성공 여부는 별도 runner/ledger의 사실이며 metadata helper의 `scientific_execution=false`와 혼동하지 않는다.
- SOURCE claim 이후 중단된 archive는 자동 재빌드하지 않는다. root가 남은 bytes/receipt/claim을 판독해 복구를 결정한다. 기존 실패와 UNKNOWN은 모든 경우 그대로 보존한다.
- 파일 snapshot 대조는 병렬 변경을 탐지하는 조건이지 전역 filesystem transaction이 아니다. root는 C09 이후 source freeze를 유지하고 plan/build 사이 새 과학/metadata 기록을 만들지 않는다. 변경이 필요하면 봉인 전에 새 actual plan으로 정리한다.
- 이 helper는 제공된 actual provider acquisition/게시 receipt가 사실인지 외부에서 다시 인증하는 업로드 도구가 아니다. 실제 GET payload의 SHA/bytes/CRC는 직접 확인한다. provider raw URL provenance는 root가 취득한 원문 response pin과 actual request 기록에 결속한다.
- private 파일 이름 및 transport-content guard는 제한된 오염 방지 장치다. root가 extras/explicit CLOSEOUT 목록을 읽고 확인한다. private full-chat 검색 불가·Drive partial inventory 한계를 이 helper로 확장하거나 지우지 않는다.
- 새로운 과학 예산은 현재 단위의 별도 40 CPU-s ledger를 따른다. helper는 과거 잔여를 이월하거나 metadata CPU를 0이라고 기록하지 않는다. 업로드·Library 보존·stage 완료·최종 중앙 게시·다음 단위 승인 판단은 root 소관이다.
