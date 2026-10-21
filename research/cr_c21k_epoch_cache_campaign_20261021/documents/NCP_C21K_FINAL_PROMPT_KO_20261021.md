# NCP 최종 실행 인계문 — C21K epoch cache와 전체 미실행 DAG

이 본문을 NCP 담당 대화에 통째로 전달한다. 대상 저장소는 `cosmosapjw-quantum/bass_cr`이며 새 단위는 `research/cr_c21k_epoch_cache_campaign_20261021`이다. 이미 구현·검토된 패킷을 복구하고, 현재 자원과 입력을 결속한 뒤, 준비된 유한 DAG를 한 번의 coordinator로 실행하는 것이 목적이다. 큰 Schur/backend 통합이나 새 최적화 기능을 NCP에서 새로 설계하지 않는다.

**작성 시 실제 C21K NCP 실행은 NOT_RUN, 현재 NCP host·64core/128GB 배정은 NOT_OBSERVED, native 성능은 NOT_EVALUATED, 일관된 전체 시간 가속은 NOT_ESTABLISHED다.** 현재 대화에는 실행 가능한 NCP 접속·배정 정보가 결속되지 않았다. 온라인 장치 metadata만 확인된 read-only 원격 조회는 host 결과를 받지 못한 채 중단됐다. 이것을 NCP 접속 성공·서버 부재·native 실패로 해석하지 않는다. 실제 NCP에서 아래 admission을 새로 수행해야 한다.

## 복구 범위와 현재 근거 신원

2026-10-21 scratch pruning과 function store 소실 뒤, 이 문서는 정확 복구된 원 인계문에서 별도 작성한 문서 보수본이다. 원 초안45,254 bytes/SHA256 `f04f66a6f8d124f305740d62505d610a300cbcaaa49b13b9ee178876726f38cd`는 그대로 보존했다. 이번 보수에서 새 연구·검토 cycle·test·staging helper·native·IVP 실행은0이다.

- K runtime3개는 checkpoint에서, NCP program3개·tests3개·backlog·control decision 합8개는 기록에서 원 hash와 동일하게 복구했다. `ncp/RECOVERY_RECEIPT_20261021.json`이 NCP exact core와 그 외 재구성 파일을 구분한다. 과학 source와 실행 계약은 바뀌지 않았다.
- Epoch13·runner22·실제 원 source plan·최종 replay3의 원 근거는 checkpoint2에서 복구했다. NCP33 PASS·별도 targeted1 PASS·원 staging3건 PASS·negative2 PASS의 도구 반환은 대화 기록에서 복구했고 재실행하지 않았다. `ncp/validation/SOURCE_VALIDATION_SNAPSHOTS.json`과 실제 복구된 tool-result/raw가 적용 범위를 명시한다.
- 기존34-payload NCP manifest(5936bytes/SHA256 `8f5f36f45e6ff89f4fb43912926d6706924e5266ec01c0ef60ae6bbaa9d7dca5`), 초기14 PASS·23 error/7 skips·24 fail·24 PASS의 원 raw, 원 `VALIDATION_HISTORY.json` 전체 bytes, 원 staging receipt의 정확 UTC는 복구되지 않았다. 이 결과의 역사 요약과 현재 raw의 존재를 혼동하지 않는다. 현재 공개 payload에는 별도 새 `ncp/NCP_CODE_MANIFEST.json`을 사용하며 원34-payload 전체가 복구됐다고 주장하지 않는다.
- 원 독립 review JSON SHA `dc521c2c3f90a58048e9d8a9049ae998b74313e064d2f68715cd9d422f3b9c1d` 및 원 인계문 review JSON SHA `c698c94bea3667390680ce39fab21a9eb4381b1a75c17f96fca26c1a3f1bdc32`도 exact bytes 미복구다. `planning/C21K_NCP_INDEPENDENT_REVIEW_RECOVERED_20261021.json`은 원 source identity에 적용되는 **역사 PASS_SCOPED**를 복구한 후속 기록이며 새 검토가 아니다.

아래 표에 실제 content commit, branch와 draft PR ACK를 결속했다. Git tree 생성 ACK는 commit/ref/PR 게시 ACK가 아니다. Document head와 최종 백업은 실제 최종 외부 영수증에서 읽는다.

## 0. 실제 게시 locator

아래 source/PR 항목은 실제 게시 ACK로 확정했다. Doc head와 archive locator는 순환 hash를 만들지 않고 최종 외부 권위 `C21K_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json`에서 읽는다. NCP 실행자는 임의 SHA·PR 번호·provider ID를 만들지 않는다.

| 항목 | 최종 값 |
|---|---|
| K 실행 content commit | `bab323983dad5206e162dbfdaefc167f2fabea45` |
| K 후속 document head | 최종 외부 영수증 `publication.document_head` |
| K branch / draft PR URL | `research/cr-c21k-epoch-cache-campaign-20261021 / https://github.com/cosmosapjw-quantum/bass_cr/pull/89` |
| K PUBLISHED receipt | 해당 document head의 `research/cr_c21k_epoch_cache_campaign_20261021/PUBLICATION_RECEIPT.json` 원 Git bytes |
| 최종 DELIVERY ZIP·bytes·SHA·provider IDs | 최종 외부 영수증 `backups.delivery` |
| 후속 document-closeout ZIP·bytes·SHA·provider IDs | 최종 외부 영수증 `backups.document_closeout` |
| NCP code manifest | `ncp/NCP_CODE_MANIFEST.json`:7606bytes, SHA256 `6784a3b04a09c354d63d9b5613b452efeaaeaab16b599b298ba4f59e7d425ce8`; RECOVERED_PACKET22 payload/192450bytes, self 제외 |
| focused 실행·수정 전후 source | `ncp/RECOVERY_RECEIPT_20261021.json`, `ncp/validation/SOURCE_VALIDATION_SNAPSHOTS.json`, 복구된 실제 tool-result/raw |
| 역사 독립 검토 결론 | `planning/C21K_NCP_INDEPENDENT_REVIEW_RECOVERED_20261021.json`: RECOVERED_PRIOR_PASS_SCOPED |

부모 계보는 **C21J `fee0d6a3f1b6460a24a1ae60f50ee84971227e5b` → 실제 K content → 후속 document head**다. 과학 프로그램을 실행할 때 후속 document head를 K content 대신 checkout하지 않는다. K source는 새 content에 고정되고 PUBLISHED receipt는 그 뒤 문서 commit에서 외부 control로 읽는다. 과거 content 안의 PENDING receipt를 수정해서 통과시키지 않는다.

## 1. 먼저 새 반환을 확인하고 완료한 일을 보존한다

실행 준비 전에 현재 Git refs/PR·관련 대화·세 저장처 dossier의 이 패킷 이후 C21 관련 반환을 확인한다. 새 결과가 있으면 고정 content의 실제 receipt/raw를 읽어 완료된 동일 신원 노드를 재사용한다. Metadata 또는 PR 제목만으로 새 native 결과를 인정하지 않는다. 검색 범위·관측 UTC·limit와 source/document 구분을 남긴다.

이 연구의 GitHub refresh는 2026-10-20 22:37:50–22:40:04 UTC에 PR85–88와 bass_cr C21 관련 ref15개를 관측했고 기존 refs와 원 source 변경이 없었다. 관련 REI/HE/WU 반환은 별도 owner·범위로 분류했으며 CR DAG의 실행 의존성을 바꾸지 않았다. 세 저장처 refresh 22:38:19–22:38:38 UTC는 자체 checkpoint를 제외한 새 관련 candidate0이었다. 이는 해당 조회 범위의 결론이며 다른 대화 전체나 NCP disk 전체의 부재 확인은 아니다.

추가 bounded refresh는 2026-10-21 03:13:44 UTC에 완료했다. `intake/FINAL_EXTERNAL_REFRESH_20261021_SUMMARY.json`에 따르면 bass_cr C21 branch13개와 최신 PR88 `fee0d6a3f1b6460a24a1ae60f50ee84971227e5b`에서 새 C21 source/native 반환0, 의존성 변경0이었다. REI199의 실제 time8/time16/time32 native3건과 HE81의 scoped canary 반환은 새 외부 결과로 읽었으나 별도 owner·source 결과다. C21 노드 완료·native owner 교체·K 가속 근거로 옮기지 않는다. 이 조회는 다른 대화나 실제 NCP host를 관측하지 않았고 WU 새 NCP 반환도 해당 GitHub/Dropbox 조회 범위에서 확정하지 못했다. 전체 raw chain을 새로 재검증한 결과도 아니다.

C21F 게시 완료, C21G 독립 실행 계약, 원 실패·raw·역사 NOT_PUBLISHED를 그대로 보존한다. 원 H/I/F/G source·tests·허용오차·fixture·state/event 정의를 수정하지 않는다. 기존 제조32jobs+FD2jobs 또는 C21I 전체 suite를 재실행하지 않는다. C21J 저장 trace 분석/replay와 C21K 가벼운 검증도 이미 완료한 근거다. 변경된 의존성에 필요한 준비만 수행한다.

## 2. source provenance와 실제 운영 checkout

| 대상 | 원 과학 content / authority | 이번 실제 실행 위치 |
|---|---|---|
| G 원 독립 campaign | `e742d44f605c51c06615451774ba90af8f41f622` | detached **fe6** checkout에 상속된 동일 원 G/F bytes |
| H 원 bridge runner | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | detached **fe6** checkout에 상속된 동일 원 H bytes |
| I 원 최적화 runner | `fe6bbaec2de5032b938aed0713623b9618ba70e6` | detached **fe6** checkout |
| K 새 epoch runner·coordinator | 최종 K content | 별도의 detached **K content** full checkout |
| H 문서 receipt | `0ec4c55102766c40c554ffc6141eb08fba741c79` | 두 checkout 밖의 원 H_PUBLICATION.json |
| I 문서 receipt | `26ab505dac2bfcb0cfd3d049f22bc408f4c86241` | 두 checkout 밖의 원 I_PUBLICATION.json |
| K 문서 receipt | 최종 K document head | 두 checkout 밖의 실제 K_PUBLICATION.json |

G/H의 원 과학 content를 이번 전체 coordinator의 실행 HEAD라고 적지 않는다. **이번 binder는 G/H/I 운영 tree가 detached fe6이고 K 운영 tree가 detached K content인지 검사한다.** K job의 원 I/H/F/G 모듈·baseline은 K checkout 안에서 모두 읽는다. K에서 별도 fe6 worktree의 I 경로를 끼워 넣지 않는다. I job은 반대로 fe6 안의 같은 원 tree를 쓴다.

Full checkout에는 F runtime10, G runtime4, H runtime8, I runtime3, 해당 manifests와 `common_ic`/`native_source` 각각의 baseline3개, 총 baseline6개가 필요하다. C21J replay용 source24·return60의 부분 복구만으로 live tree를 대신하지 않는다. 두 fixture baseline은 한 fixture만 실행하더라도 원 admission에 필요하다.

고정 manifest SHA256:

- G: `7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`
- H: `7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb`
- I: `f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`

K runtime manifest의 정확한 집합은 `run_epoch_pilot.py`, `epoch_adapter.py`, `epoch_pilot_contract.py` 세 파일이다. Coordinator·backlog는 별도의 published campaign source로 검증한다. 복구된 scheduler SHA256 `495f469faf432cba3764781e545d5711b7ba4f652c778b3aaa57589c64f04928`, builder SHA256 `8f2a8cd2b3aa50d7f5991d0ae69fb9f4a171cf4010cb5d08619e722f3f5fa543`는 원 최종 source와 동일하다. 현재 NCP payload는 새 `ncp/NCP_CODE_MANIFEST.json`이 기록한22개/192450bytes(self 제외)이며 manifest7606bytes의 SHA는 머리 표를 따른다. 원34-payload/327,621bytes manifest의 전체 bytes 복구 여부와 runtime byte identity는 별개다. 원 I publication 함수나 원 receipt를 위조해 K HEAD를 I HEAD라고 표시하지 않는다.

## 3. 실행 수: logical52, 역사 완료3, pending 최대49

| Lane | logical slots | 역사 COMPLETE | 미실행 최대 | 관계 |
|---|---:|---:|---:|---|
| H |8|1|7|2 fixtures ×2 methods ×base/FDhalf |
| G |12|0|12|reference8, 원 gate 뒤 history4 |
| I |16|2|14|2 fixtures ×2 methods ×2 modes ×base/FDhalf |
| K |16|0|16|I의 두 modes에 새 epoch 최적화를 적용 |
| 합계 |52|3|49|nominal base/reference26 + conditional23 |

Methods는 `vigilode_rodas5p`, `diffsol_bdf`, modes는 `vectorized`, `vectorized_exact`다. K baseline mode를 새로 만들지 않는다. 원 H와 중복되는 I instrumented baseline8개도 이 matrix에 더하지 않는다.

역사 잔여·조건부 **21**은 H7+G12+기존 J exact base1/조건부 FD1이다. 과거 J 패킷은 한 번의 exact base만 선택했고 FD까지 자동 승인된 것으로 소급 해석하지 않는다. 이번 사용자의 전체 미실행 준비 요청에 따른 새 운영 확장은 **28=추가 I12+K16**이다. 원 J 패킷을 수정하지 않고 현재 별도 campaign에서 이를 명시했다.

G는 원 `run_campaign.py run` 하나를 top-level process로 실행한다. 내부 worker1과 reference8→조건부4를 그대로 유지하므로 기본 top-level pending process는 **38=H7+I14+K16+G container1**이다. Logical49와 process38을 혼동하지 않는다. G reference8 모두 실행 COMPLETE이고 원 native_source 민감도 gate까지 통과한 경우만 history4가 열린다. G exit0이나 reference8 완료를 history4 완료로 올리지 않는다.

FD는 같은 lane·fixture·method·mode의 검증된 COMPLETE base가 hard parent다. K FD에 원 I vectorized base를 넘길 수 없다. H/I/K 비교 상대는 soft evidence 관계이며 그것만으로 독립 job 실행을 불필요하게 직렬화하지 않는다.

### 준비된 현재 문맥 control: 0/1/3 중 한 분기만

| 실제 admission 결과 | 새 controls | 최대 새 raw attempts / top-level pending |
|---|---:|---:|
| Known native·bridge bytes와 원 H FD 문맥까지 일치 |0|49 /38|
| Binary bytes는 같고 H의 manifest/native/bridge 절대 경로 문맥만 달라짐 |H base1|50 /39|
| Binary bytes가 다르지만 원 source·owner·locked build provenance가 검증됨 |H base1 + I vectorized base1 + 그 FDhalf1|52 /41|
| Source·owner pin 변경 또는 build provenance 실패 |admit 안 함|BLOCKED|

Binary 변경 분기는 path 변경 H base를 이미 포함한다. 네 번째 control을 추가하지 않는다. 원 완료3개는 계속 역사 COMPLETE로 보존하고, 다른 build에 대한 현재 일치 근거로 재표시하지 않는다. 현재 새 I FD control은 현재 새 I base에 의존한다. Path 이동만으로 이미 완료한 I pair를 반복하지 않는다.

이 controls는 실행 전 확인된 변경 의존성의 최소 비교 근거이며 실패 후 retry가 아니다. Binder가 `context_repair_jobs`, `science_jobs_accounting`, `maximum_raw_attempt_units`에 선택을 기록한다. 각각 새 create-only 출력에 한 번만 시도한다. 원 receipt path를 편집하거나 과거 경로를 가짜로 꾸며 control을 없애지 않는다.

## 4. 원 archive와 저장처 복구

최종 K DELIVERY의 실제 locator는 머리 표와 최종 권위 영수증을 따른다. Document delta는 DELTA_MANIFEST의 base SHA가 일치하는 문서에만 적용한다. 원 source/test/raw를 문서 delta로 재적용하지 않는다.

기존 실제 native 근거는 다음 **원 archive**다.

| 항목 | 값 |
|---|---|
| 이름 | `C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz` |
| bytes / SHA256 |2,568,680 / `2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3`|
| Drive ID |`1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u`|
| Dropbox ID / rev |`id:BSpOijBcT10AAAAAAD_T4A` / `65e43db2185370af03d47`|
| Library / File ID |`libfile_b26c9616e4748191ba98b19b1bea5d04` / `file_00000000c0cc820b982a789de34a62ed`|
| 내부 root |`C21GHI_NATIVE_EXECUTION_20261020/`|
| 구성 |184 tar members,156 regular files,155 manifest payload entries|
| payload manifest |`PACKAGE_PAYLOAD_SHA256SUMS.txt`,20,712 bytes|
| manifest SHA256 |`40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a`|

이미 같은 bytes가 현재 있으면 재다운로드하지 않는다. 새 복구는 압축 파일 SHA와 manifest를 확인하고 private 새 경로에 풀어야 한다. 원 archive에는 세 job 전체 payload, controls, bridge 실패·성공 raw와 성공 bridge가 있다. **Known native executable은 들어 있지 않다.** 부분 replay payload로 `verify_external`의 전체 payload inventory 검사를 대신하지 않는다.

**원 archive를 그대로 푼 evidence directory를 SITE에 직접 연결하지 않는다.** 각 job에는 receipt의 payload 목록 밖에 `runner_exit_code.txt` sidecar1개가 있어 원 strict 전체 inventory 검사가 거부한다. 원 archive·sidecar를 삭제·수정하지 않고 §7의 고정 helper로 receipt와 그 named payload만 별도 admission root에 byte copy한다. `native_return_evidence`는 그 **새 root 자체**이며 다음 원 directory 이름을 그대로 포함한다.

- `H_common_ic_vigilode_rodas5p_base`
- `I_common_ic_vigilode_vectorized_base`
- `I_common_ic_vigilode_vectorized_fd_half`

공개 Git에 archive 전체, private LIVE_INVENTORY3개, process 환경 원문, 서명 download URL을 복사하지 않는다. 공개 결과는 허용된 요약·SHA이고 원본은 비공개 보존한다. 저장처 dossier는 Drive folder `1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy`, Library/Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/bass_cr`다.

## 5. 현재 경로를 정하고 isolated full checkout을 준비한다

아래 절대 경로는 **현재 host에서 실제 값을 선택하는 입력**이다. `/ABS/...` 경로를 그대로 실행하지 않는다. 아래 content commit과 PR은 실제 게시 값이다. Checkout·control·campaign·build 출력은 서로 구분하고 기존 폴더를 reset/clean하거나 덮어쓰지 않는다. 기존 repository를 재사용한다면 remote와 actual objects·worktrees를 먼저 읽는다. 신규라면 다음처럼 전체 history가 있는 repository를 별도 경로에 확보한다.

```bash
C21K_REPO='/ABS/new_or_verified_bass_cr_repository'
C21K_I_CHECKOUT='/ABS/new_detached_fe6_checkout'
C21K_K_CHECKOUT='/ABS/new_detached_K_content_checkout'
C21K_CONTROL='/ABS/new_outside_control_directory'
C21K_CONTENT='bab323983dad5206e162dbfdaefc167f2fabea45'
C21K_CLOSEOUT='/ABS/actual/C21K_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json'
C21K_DOC_HEAD="$(python3 - "$C21K_CLOSEOUT" <<'PY_HEAD'
import json, re, sys
with open(sys.argv[1]) as stream:
    value = json.load(stream)['publication']['document_head']
if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{40}', value) is None:
    raise SystemExit('Actual final document head is required')
print(value)
PY_HEAD
)"
C21K_I_CONTENT='fe6bbaec2de5032b938aed0713623b9618ba70e6'
C21K_UNIT_REL='research/cr_c21k_epoch_cache_campaign_20261021'
```

Repository가 없을 때만:

```bash
git clone --no-checkout https://github.com/cosmosapjw-quantum/bass_cr.git "$C21K_REPO"
```

최종 commit 값이 실제 40hex이고 remote publication과 대조된 뒤:

```bash
git -C "$C21K_REPO" fetch origin "$C21K_CONTENT" "$C21K_DOC_HEAD" "$C21K_I_CONTENT" \
  0ec4c55102766c40c554ffc6141eb08fba741c79 \
  26ab505dac2bfcb0cfd3d049f22bc408f4c86241
git -C "$C21K_REPO" worktree add --detach "$C21K_I_CHECKOUT" "$C21K_I_CONTENT"
git -C "$C21K_REPO" worktree add --detach "$C21K_K_CHECKOUT" "$C21K_CONTENT"
git -C "$C21K_REPO" merge-base --is-ancestor \
  40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8 "$C21K_I_CONTENT"
git -C "$C21K_REPO" merge-base --is-ancestor "$C21K_I_CONTENT" "$C21K_CONTENT"
```

Shallow clone 때문에 원 H/I ancestry나 고정 blobs를 못 읽으면 필요한 history를 먼저 확보한다. Ancestry 검사를 삭제하지 않는다. 공개 source를 다운로드한 파일 모음만으로 실제 detached Git publication admission을 대신하지 않는다.

외부 control은 정확한 Git bytes로 create-only 복사한다. 아래 예시의 K receipt는 최종 doc head의 실제 `PUBLICATION_RECEIPT.json` 경로를 따른다. Root가 별도 locator를 명시했다면 그 실제 경로를 사용한다.

```bash
mkdir "$C21K_CONTROL"
(
  set -e
  set -o noclobber
  git -C "$C21K_REPO" show \
    '0ec4c55102766c40c554ffc6141eb08fba741c79:research/cr_c21h_vigilode_bridge_20261019/PUBLICATION_RECEIPT.json' \
    > "$C21K_CONTROL/H_PUBLICATION.json"
  git -C "$C21K_REPO" show \
    '26ab505dac2bfcb0cfd3d049f22bc408f4c86241:research/cr_c21i_callback_optimization_20261020/PUBLICATION_RECEIPT.json' \
    > "$C21K_CONTROL/I_PUBLICATION.json"
  git -C "$C21K_REPO" show \
    "$C21K_DOC_HEAD:$C21K_UNIT_REL/PUBLICATION_RECEIPT.json" \
    > "$C21K_CONTROL/K_PUBLICATION.json"
)
```

H control SHA는 `57b81b524b83d7c05f82394b0fba1d4d57d99ed051b92d673fd9c081d702aed4`, I control SHA는 `28641242b36a8392e296fa7801212908296b9fd5fcf035574483e2399d2a2af2`다. 원 bytes에 trailing LF를 임의로 더하지 않는다. H/I/K controls 모두 **두 checkout 밖**에 있어야 한다. G의 별도 receipt는 `C21G_PUBLICATION_RECEIPT_V1`, status `PUBLISHED_OPEN_DRAFT_PR`이고 unit 필드가 없으므로 H/I 모양으로 바꾸지 않는다. 이번 SITE schema에는 G publication receipt 인자가 없다.

## 6. 현재 runtime과 유효 binary를 먼저 확인한다

실제 Python executable을 절대 real path로 정하고 버전·NumPy·SciPy·platform·loader를 관측한다. 검증에 쓴 로컬 환경은 Python3.12.14/NumPy2.3.5/SciPy1.17.0이었지만 이것이 현재 NCP 설치 상태라는 뜻은 아니다. Runtime 차이는 기록하고 근거 없이 전체 환경을 upgrade하지 않는다. Runner를 NumPy가 이미 import된 notebook process 안에서 호출하지 않는다. Scheduler가 새 Python child process를 시작한다.

```bash
C21K_PYTHON='/ABS/actual/resolved/python3'
C21K_NCP="$C21K_K_CHECKOUT/$C21K_UNIT_REL/ncp"
C21K_H="$C21K_I_CHECKOUT/research/cr_c21h_vigilode_bridge_20261019"
C21K_F="$C21K_I_CHECKOUT/research/cr_c21e_event_native_20261018"
C21K_NATIVE_RETURN='/ABS/private/C21GHI_NATIVE_EXECUTION_20261020'
C21K_NATIVE_ARCHIVE='/ABS/private/C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz'
C21K_HISTORICAL_EVIDENCE='/ABS/new_historical_evidence_admission_root'
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export RAYON_NUM_THREADS=1 OMP_NESTED=FALSE OMP_MAX_ACTIVE_LEVELS=1
```

`HOME`, `CODEX_HOME` 같은 공용 환경변수를 작업 경로로 바꾸지 않는다. 아래 build를 실제 수행하기 **전에 §8의 현재 자원 관측과 owner 배정·공유 CPU 예약**을 확보한다. Build는 필요한 artifact가 없거나 호환되지 않을 때만 수행하고 compiler RSS도 그 준비 배정에 계상한다. 원 science/smoke suite의 자동 재실행을 준비 단계에 붙이지 않는다.

### 6.1 Bridge 재사용 또는 원 locked helper

Known bridge는 4,888,736 bytes, SHA256 `717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30`다. 원 archive의 `binary/bass-cr-c21h-rust-bridge`와 `build_success/BUILD_RECEIPT.json`을 사용한다. 원 성공 receipt SHA는 `c846c35621dd9a0aa3c5bbfb90e94da0f022e934cf2ea1342270d61eda4b5190`다.

현재 bytes·실행 권한·ELF architecture/loader/shared-library 호환성과 원 receipt의 source identity가 유효하면 Rust 설치 없이 이 artifact를 재사용한다. Receipt의 과거 binary path를 편집하지 않고 현재 파일 경로를 SITE에 준다.

새 build가 필요하면 실제 배정 CPU55 이외의 build CPU, 현재 cargo/rustc executable과 아직 없는 절대 target 경로를 정한다. 성공 toolchain의 역사 관측은 Rust1.94.1이다. Helper 자체는 버전을 강제하지 않으므로 현재 선택한 두 executable의 version을 먼저 확인한다. Build는 campaign의 원 300초 job budget과 별도이며 owner allocation 안에서 제한된 준비 작업으로 계상한다.

```bash
C21K_BUILD_CPU='ACTUAL_ALLOCATED_CPU_EXCLUDING_55'
C21K_LEASE_DIR='/ABS/actual_shared_owner_cpu_lease_directory'
[[ "$C21K_BUILD_CPU" =~ ^[0-9]+$ && "$C21K_BUILD_CPU" != 55 ]] || {
  echo 'An actually allocated build CPU excluding 55 is required' >&2
  exit 2
}
C21K_CARGO='/ABS/verified/cargo'
C21K_RUSTC='/ABS/verified/rustc'
C21K_BRIDGE_BUILD='/ABS/new_bridge_build_directory'
flock -n "$C21K_LEASE_DIR/cpu_${C21K_BUILD_CPU}.lock" \
  taskset -c "$C21K_BUILD_CPU" bash "$C21K_H/rust_bridge/build_bridge.sh" \
  --cargo "$C21K_CARGO" --rustc "$C21K_RUSTC" \
  --target-dir "$C21K_BRIDGE_BUILD"
```

C21K_LEASE_DIR는 §8에서 합의된 실제 shared directory이며 준비돼 있어야 한다. 위 flock이 예약을 얻지 못하면 build를 시작하지 않는다. 현재 locked dependencies cache가 실제 준비된 경우에만 `--offline`을 더한다. 원 helper는 `cargo build --locked --release --jobs 1`을 사용하며 VigilODE `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, Diffsol0.17.1, Cargo.lock SHA `d30f7f6437b7704f845ba85f8206c94810fbd4ec1a48db9cba06b7b77604c892`를 유지한다. 원 helper 이름은 **build_bridge.sh**다.

출력 `BUILD_RECEIPT.json`, versions, SOURCE_BEFORE, stdout/stderr와 성공 binary를 모두 보존한다. Exit0, 원 source_files identity, source_files_unchanged, binary hash를 확인한다. 예전 timeout300초/exit124와 뒤 성공421초 기록은 역사 raw로 남긴다. 새로운 source pin이나 과거 linker workaround를 자동 적용하지 않는다.

### 6.2 Native 재사용 또는 원 owner build

Known native는 5,003,448 bytes, SHA256 `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`, 원 owner는 `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`다. PR82의 실제 검증 artifact·receipt 또는 현재 matching 파일을 확인해 재사용한다. 옛 `/root/.../native_point`가 현재 있다고 가정하지 않는다. PR87 archive에서 이 binary를 찾았다고 만들지 않는다.

Known artifact를 재사용할 수 없고 현재 locked toolchain/cache가 준비돼 있으면 **원 F helper**를 사용한다.

```bash
C21K_NATIVE_BUILD='/ABS/new_native_build_directory'
C21K_BUILD_CPU='ACTUAL_ALLOCATED_CPU_EXCLUDING_55'
C21K_LEASE_DIR='/ABS/actual_shared_owner_cpu_lease_directory'
[[ "$C21K_BUILD_CPU" =~ ^[0-9]+$ && "$C21K_BUILD_CPU" != 55 ]] || {
  echo 'An actually allocated build CPU excluding 55 is required' >&2
  exit 2
}
C21K_OWNER_REPO='/ABS/verified_existing_rei_bianchi_git_repository'
flock -n "$C21K_LEASE_DIR/cpu_${C21K_BUILD_CPU}.lock" \
  taskset -c "$C21K_BUILD_CPU" bash "$C21K_F/build_native.sh" \
  "$C21K_NATIVE_BUILD" "$C21K_OWNER_REPO"
```

두 번째 인자는 선택 사항이다. 없으면 원 helper가 별도 bare repo에서 정확한 owner commit을 fetch한다. Helper는 dirty owner worktree가 아닌 그 commit의 `git archive`를 export한다. `$HOME/.cargo/bin`을 PATH 앞에 추가하므로 실제 선택되는 Rust1.94.1 cargo/rustc를 확인한다. 내부 `CARGO_BUILD_JOBS=2`와 `cargo build --offline --locked --release --lib`를 그대로 유지한다. 한 CPU taskset을 걸었다고 compiler child 수가1로 바뀌었다고 쓰지 않는다. 준비 CPU·RAM 배정 안에서 실행한다.

이 helper는 원 wrapper를 `rustc --edition=2021 -O`로 컴파일하고 wrapper test binary를 만들어 `--test-threads=1`로 검사한다. 이것은 새 build의 원 절차이며 기존 물리 suite 재실행과 구분한다. Cache가 없으면 offline/locked 조건을 삭제하지 말고 부족한 artifact를 명시해 준비한다. 실패 build directory를 재활용하거나 로그를 지우지 않는다.

G의 원 native admission에 필요한 파일은 `native_point`, `owner_commit.txt`, `build_exit.txt`의 `exit_code=0`, `input_sha256.txt`, `owner_source.tar`다. Binary는 해당 build root의 `native_point`여야 하고 wrapper·archive·binary hashes가 맞아야 한다. **원 helper는 NATIVE_BUILD_RECEIPT.json 또는 native BUILD_RECEIPT.json을 만들지 않는다.** Bridge receipt와 혼동하지 않는다.

새 binary SHA가 known SHA와 다르더라도 이 고정 owner/source build provenance가 통과하면 이번 K campaign은 §3의 3-control 분기로 admit한다. 이는 원 J의 known-SHA 단일 행 wrapper를 수정한 것이 아니다. Source/owner/fixture/tolerance가 달라지면 이 분기로도 admit하지 않는다. 동일 source라는 이유로 byte-reproducible build 또는 동일 성능을 추정하지 않는다.

## 7. 역사 evidence를 보존한 admission root와 SITE를 결속한다

먼저 새 helper를 사용한다. 입력은 §4의 **known full compressed tar**이고 출력은 아직 없는 절대 directory다. Extracted 부분 폴더나 다시 압축한 다른 tar를 입력으로 쓰지 않는다.

```bash
(
  set -o noclobber
  "$C21K_PYTHON" "$C21K_NCP/prepare_historical_evidence.py" \
    --archive "$C21K_NATIVE_ARCHIVE" --out "$C21K_HISTORICAL_EVIDENCE" \
    > "$C21K_CONTROL/HISTORICAL_STAGING.stdout" \
    2> "$C21K_CONTROL/HISTORICAL_STAGING.stderr"
)
```

Helper는 압축 archive2568680bytes/SHA2722e479…와 V3 backlog SHA3a329a1d… 및 원3 receipt pins를 확인한다. Tar의 모든 path·중복·link/special member를 검사하며 임의 extractall을 쓰지 않는다. H36/I38/I39 named payload, 총113개와 receipt3개를 byte 그대로 복사한다. 각 원 job에서 stage에 넣지 않는 추가 파일은 정확히 runner_exit_code.txt 하나뿐이고 다른 예상 밖 파일은 거부한다. **원 sidecar3개는 archive 안에 그대로 남고 identity가 새 receipt에 기록된다.** 원 receipt 재작성이나 strict verifier 완화는 없다.

출력 root 바로 아래 원명3 directories와 `STAGING_RECEIPT.json`이 생긴다. 후자는 세 job directory 밖에 둔다. 복구 전 실제 로컬 staging1회에서116 files/5,216,823 bytes를 복사하고 unchanged `scheduler.verify_external`3건이 PASS했다. Existing-output·one-byte archive tamper negative2도 PASS(0.009초)였다. 해당 tool-result/raw만 기록에서 복구했으며 이번 복구에서 helper를 재실행하거나 원 generated-UTC staging receipt를 재생성하지 않았다. 이 검증은 archive/data admission이며 새 native/IVP0이다. 실제 FD-parent context·현재 source/build/owner admission과 별개이고 0/1/3 controls 분기를 제거하지 않는다.

기존 stage가 있으면 같은 bytes/receipt를 확인해 재사용하고 원 output을 덮어쓰지 않는다. 실패했다면 원 archive와 실패 로그를 보존하며 gate를 반환한다. Source가 검증한 known archive에 sidecar를 수동 삭제한 새 tar를 만들지 않는다.

현재 `make_campaign.py`의 SITE 입력은 다음 key들을 가진 JSON object다. 별도 SITE schema 문자열은 요구하지 않는다. **필수10개는 모두 존재하는 절대 경로**여야 하며 builder는 real path로 정규화한다.

| Key | 정확한 의미 |
|---|---|
| `python` | 실제 Python executable |
| `i_checkout` | full detached fe6 checkout |
| `k_checkout` | full detached 실제 K content checkout |
| `bridge_binary` | 현재 재사용/검증된 bridge executable |
| `bridge_build_receipt` | 그 bridge의 원 성공 BUILD_RECEIPT.json |
| `native_binary` | 현재 검증된 native_point |
| `h_publication_receipt` | checkout 밖 원 H PUBLISHED receipt |
| `i_publication_receipt` | checkout 밖 원 I PUBLISHED receipt |
| `k_publication_receipt` | checkout 밖 실제 K PUBLISHED receipt |
| `native_return_evidence` | prepare_historical_evidence.py가 만든 새 admission root 자체 |
| `native_build_dir` | 선택: 다른 SHA의 검증된 native build root. 이 경우 필수 |
| `g_reuse_directories` | 선택: 원 G가 실제 검증할 이전 G campaign directories 배열 |

G reuse를 쓰지 않으면 빈 배열 또는 key 생략이다. H/I의 개별 job directory를 G campaign reuse로 넣지 않는다. 신규 native build root가 없을 때 빈 가짜 build directory를 만들지 않는다.

변수에는 §6에서 실제 확인한 경로를 넣는다. 다음은 shell 문자열을 JSON으로 안전하게 전달하는 생성 예시다. `C21K_NATIVE_BUILD`는 known binary 재사용에 build directory가 없으면 빈 문자열로 둔다.

```bash
C21K_BRIDGE='/ABS/actual/bridge_binary'
C21K_BRIDGE_RECEIPT='/ABS/actual/bridge_BUILD_RECEIPT.json'
C21K_NATIVE='/ABS/actual/native_point'
C21K_NATIVE_BUILD="${C21K_NATIVE_BUILD-}"
C21K_SITE="$C21K_CONTROL/SITE_BINDINGS.json"
C21K_MANIFEST="$C21K_CONTROL/CAMPAIGN.json"
"$C21K_PYTHON" - "$C21K_SITE" "$C21K_PYTHON" \
  "$C21K_I_CHECKOUT" "$C21K_K_CHECKOUT" \
  "$C21K_BRIDGE" "$C21K_BRIDGE_RECEIPT" "$C21K_NATIVE" \
  "$C21K_CONTROL/H_PUBLICATION.json" "$C21K_CONTROL/I_PUBLICATION.json" \
  "$C21K_CONTROL/K_PUBLICATION.json" "$C21K_HISTORICAL_EVIDENCE" \
  "$C21K_NATIVE_BUILD" <<'PY_SITE'
import json, sys
from pathlib import Path
keys = ['python', 'i_checkout', 'k_checkout', 'bridge_binary',
        'bridge_build_receipt', 'native_binary', 'h_publication_receipt',
        'i_publication_receipt', 'k_publication_receipt', 'native_return_evidence']
site = dict(zip(keys, sys.argv[2:12]))
if sys.argv[12]:
    site['native_build_dir'] = sys.argv[12]
site['g_reuse_directories'] = []
with Path(sys.argv[1]).open('x') as stream:
    json.dump(site, stream, indent=2)
    stream.write('\n')
PY_SITE
"$C21K_PYTHON" "$C21K_NCP/make_campaign.py" \
  --bindings "$C21K_SITE" --out "$C21K_MANIFEST"
```

**새 build를 선택했다면 C21K_NATIVE_BUILD에 검증된 build root가 남아 있어야 한다. 위 default는 이미 지정한 값을 보존한다.** Binder는 원 G native/build admission, 원 H bridge receipt, H/I/K PUBLISHED ancestry·committed blobs, source closure, 역사3개 전체 payload를 확인한다. 성공 상태는 `BOUND`다. `UNBOUND_NOT_EXECUTABLE`은 `--bindings` 없는 템플릿이며 실행용이 아니다.

`BLOCKED_INPUT_ADMISSION` receipt가 생겼다면 그 실패를 보존한다. 원 source·receipt를 수정하지 말고 실제 누락된 artifact/경로만 해결한 뒤 다른 새 control/manifest filename에 다시 결속한다. 기존 CAMPAIGN.json을 수동 편집하거나 output을 덮어쓰지 않는다. Binding이 선택한 0/1/3 controls와 최대49/50/52를 실제 JSON에서 확인한다.

## 8. 현재 owner allocation과 resource admission

64core/128GB는 활용하려는 서버 사양이며 현재 독점 가용량이 아니다. 현재 host의 affinity, effective cpuset, 보이는 cgroup v2 모든 ancestor의 CPU quota·memory limit/current와 MemAvailable을 읽는다. CPU55는 언제나 제외한다. Affinity에 있다는 사실만으로 그 CPU의 독점 배정을 주장하지 않는다.

```bash
(
  set -o noclobber
  "$C21K_PYTHON" "$C21K_NCP/scheduler.py" --inspect-resources \
    > "$C21K_CONTROL/RESOURCE_SNAPSHOT.json"
)
```

이 명령은 과학 runtime을 import하지 않고 자원을 관측한다. 반복 관측은 새 filename에 저장한다. `--inspect-resources`만으로 owner 권한·공유 lease·process 관측 capability가 검증된 것은 아니다.

실제 NCP owner가 현재 배정에 대해 다음 `OWNER_ALLOCATION.json`을 작성한다. 아래는 **채우기 전 비실행 템플릿**이다. Empty CPU list,0 budget, REPLACE 값으로는 admission이 실패한다. 실제 host fingerprint는 방금 snapshot에서, expiry는 실제 배정의 UTC 만료 시각에서 얻는다.

```json
{
  "schema": "C21K_OWNER_ALLOCATION_V1",
  "owner_allocation_id": "REPLACE_WITH_ACTUAL_OWNER_ALLOCATION_ID",
  "host_fingerprint_sha256": "REPLACE_WITH_CURRENT_SNAPSHOT_64HEX",
  "expires_at_utc": "REPLACE_WITH_ACTUAL_FUTURE_UTC_ISO8601",
  "cpu_ids": [],
  "per_job_rss_budget_bytes": 0,
  "coordinator_rss_budget_bytes": 0,
  "lease_directory": "/ABS/actual_shared_owner_cpu_lease_directory"
}
```

필수는 schema, owner_allocation_id, matching host fingerprint, timezone 있는 미래 expiry, 중복 없는 정수 cpu_ids, 양의 정수 job/coordinator RSS budgets, 실제 shared lease directory다. 전체 batch 예시는 선택 항목 `maximum_concurrent_jobs`를 생략했다. 실제 owner가 별도 동시성 cap을 요구할 때만 양의 정수로 추가한다. 값1은 과학 worker를 직렬화하므로 전체 자원 활용 기본값으로 넣지 않는다. 이 항목을 생략해도 실제 CPU/quota/RAM, lease와 DAG 준비 상태의 제한은 모두 적용된다. RSS budgets의0은 측정값이 아니라 미입력 표식이며 실제 현재 자원의 보수적 배정 값으로 채운다. Hash를 임의 문자열로 넣는 field는 없다. Coordinator가 canonical allocation SHA256을 계산하여 ADMISSION에 기록한다. 원 allocation JSON도 함께 반환한다. Hash는 입력 신원이며 그 자체가 host owner의 권한 증명은 아니다.

Lease directory는 같은 host에서 겹치는 배정을 조정하는 모든 관련 coordinator가 공유하는 실제 경로여야 한다. Campaign별 새 private lease directory를 만들어 충돌 회피 검사를 무력화하지 않는다. 기존 lock을 삭제하거나 CPU55를 allocation에 넣어 우회하지 않는다.

동시 job 수는 allocated CPUs∩현재 affinity/cpuset에서 CPU55를 뺀 수, quota의 floor, available RAM 및 지정 cap으로 제한된다. Coordinator 전용 CPU1개와 그 RAM을 별도 계상한다. 메모리 reserve는 `max(1GiB, effective memory limit의12.5%)`다. 실제128GiB라면16GiB지만 광고값128GB를 자동 변환해 실제 limit으로 쓰지 않는다. Active job마다 보수적인 전체 RSS budget을 예약하고 새 launch 직전 capacity와 input hashes를 재확인한다. 64core라는 이유로63jobs를 강제하지 않는다. 같은 문맥 또는 path-only control 분기의 초기 ready process는20개이고, 검증된 새 binary의3-control 분기는21개다. 실제 bound manifest의 ready 집합과 capacity가 권위이며64개의 새 jobs를 만들지 않는다.

원 H/I/K job worker1·thread1과 G 내부 worker1을 유지하면서 **서로 독립인 job 사이**에서 CPU를 사용한다. Linux cgroup v2나 subreaper 등 필요한 관측 capability가 없으면 해당 상태를 반환한다. 별도 새 backend를 NCP에서 구현해 우회하지 않는다.

## 9. plan, 한 번의 execute, 정확한 resume

먼저 최종 manifest의 입력 신원과 DAG를 plan으로 확인한다.

```bash
(
  set -o noclobber
  "$C21K_PYTHON" "$C21K_NCP/scheduler.py" --manifest "$C21K_MANIFEST" \
    > "$C21K_CONTROL/SCHEDULER_PLAN.json"
)
```

Plan 성공은 `PREPARED_NOT_RUN`이다. 실제 source-only UNBOUND builder 준비는 이미 PASS지만 그것이 site-bound source/build/publication admission을 실행한 것은 아니다. Native/IVP는0이며 실제 owner allocation과 live process cleanup admission까지 실행한 것도 아니다. K 원 runner의 실제 source plan PASS와 coordinator bound plan PASS도 서로 다른 영수증이다.

실제 allocation JSON이 준비되고 plan의 49/50/52 분기가 맞으면 새 절대 output을 지정해 coordinator를 한 번 시작한다. Output directory는 **미리 만들지 않는다**. Scheduler가 create-only 생성한다. 예시 log 경로도 아직 없는 파일이어야 한다.

```bash
C21K_ALLOCATION="$C21K_CONTROL/OWNER_ALLOCATION.json"
C21K_RUN_OUT='/ABS/new_unique_C21K_campaign_output'
(
  set -o noclobber
  if "$C21K_PYTHON" "$C21K_NCP/scheduler.py" \
    --manifest "$C21K_MANIFEST" \
    --allocation "$C21K_ALLOCATION" \
    --out "$C21K_RUN_OUT" --execute \
    > "$C21K_CONTROL/EXECUTE.stdout" \
    2> "$C21K_CONTROL/EXECUTE.stderr"; then
    C21K_EXECUTE_EXIT=0
  else
    C21K_EXECUTE_EXIT=$?
  fi
  printf '%s\n' "$C21K_EXECUTE_EXIT" > "$C21K_CONTROL/EXECUTE.exit_code"
  exit "$C21K_EXECUTE_EXIT"
)
```

실행 직전에 coordinator는 Linux child subreaper를 활성화하고, 자기 소유 marker가 있는 짧은 Python child를 만든다. `/proc/<pid>/environ`의 marker뿐 아니라 실제 `owned_processes()`가 그 child PID를 찾는지, 전후 start ticks가 일치하는지, 살아 있는 state와 양의 정수 RSS를 관측하는지까지 검사한다. 이 **process 관측 사전검사는 native/science probe가 아니다**. 현재 ChatGPT sandbox에서는 이 관측이 차단되는 경로가 확인됐으며 실제 NCP에서는 아직 관측하지 않았다. `OWNED_PROCESS_OBSERVATION_UNAVAILABLE`, marker 실패 또는 `OWNED_PROCESS_TRACKER_NOT_VERIFIED` 등 실제 tracker 검증 실패면 native job0으로 중단한다. 실패를 감추거나 항상 성공하는 stub으로 바꾸지 않는다.

정상 launch 뒤에는 owner marker와 PID start ticks로 자기 child/descendants를 추적하고 RSS·deadline을 관측한다. Timeout/interrupt에는 자기 프로세스만 정리한다. 타인 process를 pid 이름만 보고 종료하지 않는다. 상세 environ 값은 저장하지 않는다. Run stderr와 CAMPAIGN_RETURN을 함께 읽어 단순 CLI exit를 과학 성공으로 해석하지 않는다.

중단 후 **동일 manifest, 동일 output**의 아직 미시도 노드만 이어갈 때:

```bash
(
  set -o noclobber
  if "$C21K_PYTHON" "$C21K_NCP/scheduler.py" \
    --manifest "$C21K_MANIFEST" \
    --allocation "$C21K_ALLOCATION" \
    --out "$C21K_RUN_OUT" --execute --resume \
    > "$C21K_CONTROL/RESUME_01.stdout" \
    2> "$C21K_CONTROL/RESUME_01.stderr"; then
    C21K_RESUME_EXIT=0
  else
    C21K_RESUME_EXIT=$?
  fi
  printf '%s\n' "$C21K_RESUME_EXIT" > "$C21K_CONTROL/RESUME_01.exit_code"
  exit "$C21K_RESUME_EXIT"
)
```

`--resume`만 붙이고 `--execute`를 빼면 실제 실행 없이 plan이다. Resume는 manifest digest·job signature·complete payload 전체 신원을 확인한다. 이미 output이 있는 FAILED/TIMED_OUT/INTERRUPTED 또는 원 시도 노드를 자동 재시도하지 않는다. 불완전한 job directory는 INTERRUPTED로 남긴다. 실패 뒤 새 output 전체를 만들어 같은 matrix를 다시 시작하는 것도 자동 retry로 사용하지 않는다. 미시도 노드를 이어갈 때도 현재 만료 전의 유효 allocation이 필요하다. 새 allocation이 정당하게 발급되면 새 JSON과 hash를 보존한다.

실행 후 최초 실패·거부 원인을 보존한다. 사용자가 허용한 작은 경로·실제 toolchain·build 호환 수정은 NCP에서 수행하고 diff·focused 확인·변경 전후 source/build identity를 남길 수 있다. Pinned runtime bytes를 바꿔야 한다면 기존 admission을 우회하거나 원 receipt를 고치지 않고 새 검증과 실제 published identity를 결속해야 한다. 큰 Schur/backend 통합·새 기능 설계는 별도 연구로 돌린다. 작은 준비 수정을 이유로 불필요하게 전체 작업을 중단하거나 옛 suite를 반복하지 않는다.

## 10. deadline·과학 판정과 성능 판정

원 H/I/K 각 job은 원 H epoch의300초, original RHS/native200000 cap, 개별 native timeout `min(15초, 남은 예산)`를 유지한다. Source setup·exact admission·live guard도 그 예산을 소비한다. K setup마다 새300초를 만들지 않는다. Coordinator 외부 job timeout도300초이며 원 내부 budget을 늘려 주지 않는다. G는 내부 job별300초 계약이고 G container 외부 상한은3660초다. Campaign horizon은21600초와 owner allocation 만료 중 먼저 도달하는 시점이다. 현재 source가 기록한 상한을 원 실패를 성공으로 만들기 위해 늘리지 않는다.

새 K cache는 cell scope의 opacity 계산을 실제 epoch binary64 key로 재사용하는 exact 경로다. Signed zero·소유 배열·원 연산 순서와 원 native-cache/live provider 검사를 유지한다. 전체 RHS를 epoch 하나로 합치거나 근사·clipping·float32·fastmath를 도입하지 않는다.

이미 완료한 근거는 epoch focused13 methods, runner focused22 methods, 실제 원 source closure plan1회, 저장 native trace3cases replay다. Replay 각 case의472 replies/40432 binary64 values, FD nodes와 저장 state 기반 physical summary가 일치했다. 이것은 새 native trajectory solve가 아니다. 새 native/IVP0이었다. Scheduler/binder는 수정 전 source의33 methods PASS(1.351초) 뒤 actual tracker preflight gate를 강화하고 그 변경에 대한 targeted1 method PASS(0.033초)를 따로 기록했다. 이를 최종 source의34개 전체 suite 한 번으로 합치지 않는다. Subprocess 실행·affinity·signal 등은 실제 로컬 process로 확인했지만 ownership/start-tick 관측은 명시적 doubles를 썼고, bound matrix의 build/publication admission도 분기 연결용 doubles다. 실제 NCP marker observer 통합·live native admission은 미평가다. 정확한 수정 전후 source hashes와 현재 복구된 raw는 `ncp/RECOVERY_RECEIPT_20261021.json` 및 `ncp/validation/SOURCE_VALIDATION_SNAPSHOTS.json`을 따른다. 역사 검토 결론은 `planning/C21K_NCP_INDEPENDENT_REVIEW_RECOVERED_20261021.json`이며, 미복구 초기 raw나 원 검토 JSON이 현존한다고 간주하지 않는다.

역사 timing은 source3245d871…에서 paired median0.9364664941, source db244c06…에서1.0004085537이었다. 두 범위가1을 가로지른다. 이후 typed-key/deadline 경계가 바뀐 최종 epoch source `fc8009f7e185f7a257cbda0956317f4e7f358a8c548501c96e204aa7c94498bd`에 이 timing을 전이하지 않는다. Cache miss 감소나 synthetic/replay 시간으로 native·NCP64 속도 향상을 선언하지 않는다.

새 실제 반환에서는 동일 fixture/method/mode의 matched pair에 대해 source/build/runtime/host/affinity/CPU lease·thread environment·timers를 함께 비교한다. 다른 host의 과거 wall time은 matched current performance가 아니다. Coordinator 동시 실행의 CPU 경쟁·launch/setup·I/O·검사 overhead와 순수 solver/native 시간을 구분한다. Historical3개와 새 controls의 비교 가능성도 구분한다. 이번 유한 cohort만으로 안정적 통계적 가속이나 임의 workload 일반화가 성립한다고 쓰지 않는다.

`COMPLETE`는 검증된 receipt와 payload의 실행 상태다. 물리 residual·positivity·photon ledger·trace/FD 민감도·reference 오차·BDF 비교 판정은 별도로 수행한다. G `SCOPED_HOLD`, 미실행 conditional, 비교 evidence unavailable을 실패0 또는 전체 PASS로 합치지 않는다. `global_error_bound=null`과 기존 science HOLD를 유지한다.

## 11. 반환할 실제 파일과 상태

과학 실행, 게시, 백업, DAG 상태를 별도 field로 보고한다. Coordinator가 초기 반환에 기록하는 `publication=NOT_PUBLISHED`, `backup=NOT_BACKED_UP`는 실행 당시의 사실이며 뒤 게시 성공으로 덮어쓰지 않는다. 후속 publication/backup 영수증을 additive하게 만든다.

필수 반환 묶음은 다음과 같다.

1. 실제 source/content/doc refs, runtime·NCP manifests와 hashes, H/I/K 외부 PUBLISHED receipts, SITE_BINDINGS, 원 CAMPAIGN.json 및 canonical digest. 원 compressed archive identity와 새 STAGING_RECEIPT, 보존한 sidecar identities, admission-copy116파일을 구분한다.
2. 현재 owner allocation 원 JSON·canonical SHA, resource snapshot과 모든 ADMISSION records, 관측 시각·host fingerprint·CPU55 제외·coordinator/worker CPU·quota/RAM/capacity·lease 범위. 민감한 상세 host/process 목록은 private에 보존한다.
3. 실제 native/bridge bytes·SHA·현재 path와 build provenance, 재사용/새 compile 구분, 버전·locked dependency·helper stdout/stderr·원 실패 기록. 새 compile의 native wrapper tests와 과학 jobs를 별도 계수한다.
4. CAMPAIGN_IDENTITY, 모든 CAMPAIGN_RETURN, 각 jobs/<id>/RESERVATION·COORDINATOR_RECEIPT·stdout/stderr·payload의 원 JOB_RECEIPT/RPC/native/result/FD/physical-summary. 실패·timeout·interrupted partial raw도 포함한다.
5. 원 완료3 재사용/역사만 상태, 추가 controls0/1/3의 관측 이유, 실제 시도 수, 조건 미충족 BLOCKED/NOT_RUN/SCOPED_HOLD, 새 native calls·per-job timers/RSS·cleanup unresolved 수와 남은 DAG.
6. 기존 H/I/K lane 비교와 FD sensitivity, G 내부 reference8·history4의 실제 각각 결과, 실행과 과학 HOLD·성능 판정의 구분.

복구 가능한 archive를 새 이름으로 create-only 만들고 member/byte/SHA manifest를 남긴다. Drive·Dropbox·Library의 실제 upload/readback 결과와 ID/rev/bytes/SHA를 각각 기록한다. 수행하지 못한 저장처를 성공으로 표시하지 않는다. 원 archive와 새 derived 결과를 구분하고 원 raw bytes를 재포맷하지 않는다. 공개 draft PR은 허용된 source·요약·새 근거만 사용하고 private 원본은 공개 tree에서 제외한다. 자동 merge하지 않는다. 다른 사람에게 외부 메시지를 보내는 것은 별도 명시적 권한이 있는 경우만 수행한다.

접근·자원·artifact·소유 process 관측이 막히면 실패를 보존하고 가능한 행정 작업까지 완료한 뒤 실제 gate와 남은 일을 보고한다. 오래된 scratch repo/Rust binary가 현재 있다고 가정하거나 관측되지 않은 NCP 전체 부재를 주장하지 않는다. 새 실행이 없으면 정확히 **NCP NOT_OBSERVED 또는 gate별 BLOCKED, native NOT_RUN, performance NOT_EVALUATED**로 반환한다.

## 12. 이 인계문의 직접 계약 근거

실행 API와 gate는 최종 K content의 `ncp/make_campaign.py`, `ncp/scheduler.py`, `ncp/BACKLOG_INVENTORY.json`, `ncp/DEPENDENCY_CONTROL_SCOPE_DECISION.json`, `ncp/prepare_historical_evidence.py`, `epoch_pilot_contract.py`, `run_epoch_pilot.py`를 따른다. 과거 `FD_CONTEXT_REPAIR_ADDENDUM.json`은 path-only 분기 역사이며 뒤 0/1/3 scope decision을 대체하는 최신 전체 계약이 아니다.

원 helper와 admission은 고정 fe6 content의 다음 파일에서 읽는다.

- [원 H build helper](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21h_vigilode_bridge_20261019/rust_bridge/build_bridge.sh)
- [원 F owner build helper](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21e_event_native_20261018/build_native.sh)
- [원 G source/native authority](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21g_reference_refinement_20261019/campaign_contract.py)
- [원 H runner](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21h_vigilode_bridge_20261019/run_pilot.py)
- [원 I runner](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/run_optimized_pilot.py)

복구된 helper SHA256은 `6822cb69e2b70a5fe808ed8e167e57b501752f6eb2a0b5e2969678fb2c215163`(8985bytes)이며 원 최종 bytes와 동일하다. 원 `HISTORICAL_EVIDENCE_STAGING_RECEIPT.json`의 역사 identity는3036bytes/SHA256 `7474f1e216ea6616a589fabbf17e151d2f1ffd1bc9ed9f566c479af987f654dc`지만 exact receipt bytes는 현재 미복구다. 현재 복구된 실제 도구 반환은 `ncp/validation/HISTORICAL_EVIDENCE_STAGING_TOOL_RESULT.json`, `HISTORICAL_EVIDENCE_NEGATIVE_TOOL_RESULT.json`과 각각의 RAW.txt다. 새 NCP에서 helper를 실행하면 현재 UTC/경로의 별도 새 STAGING_RECEIPT를 보존하며 옛 identity로 표시하지 않는다.

이 문서는 준비된 실행 계약의 인계와 근거 보존 범위의 문서 보수다. 원 H/I/F/G source·test·raw 변경0, 이번 복구 준비본 작성 중 compile/native/IVP/physics suite/test/검토 cycle 실행0이다.

## 게시 전송 형식

큰 JSON 전송의 무응답을 줄이기 위해 고정 source fetch 증거와 실행 불가 preview를 각각 `evidence/runner_integration/FETCHED_CONTENT.json.gz`, `ncp/CAMPAIGN_UNBOUND_TEMPLATE.json.gz`로 무손실 압축했다. 압축 해제 bytes와 원 SHA256의 일치를 확인했으며 원 JSON도 최종 delivery의 `original_publication_inputs/`에 보존한다. 상세 대조는 `administration/PUBLICATION_ENCODING.json`이다. 실행 코드·테스트·backlog/control pins는 변경되지 않았다. 실제 campaign은 원 builder가 새 BOUND JSON으로 생성하며 압축 preview를 실행하지 않는다. 현재 공개 content는116파일,964255bytes이고 최종 CONTENT_MANIFEST는19325bytes/SHA256 `dd7d9d3d79acbbbde88ee1994a175a31e1cf2369c5394e6233b50dbff300f4c6`다.
