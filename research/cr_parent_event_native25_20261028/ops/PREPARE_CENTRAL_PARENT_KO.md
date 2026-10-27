# Parent-event 중앙 반환 생성기: 실행 전 입력 계약

대상 단위는 `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`, 경로는 `research/cr_parent_event_native25_20261028`이다. 이 문서와 `prepare_central_parent.py`는 **아직 실행하지 않은 metadata helper source**다. 실제 최종 S/D, 중앙 후보, 과학 승인, 게시 성공 또는 R3를 여기서 미리 선언하지 않는다.

작성자 `/root/theory_review`는 이번 이론·독립 수치 reference 작성자이자 이 metadata builder 작성자다. Production `parent_event.py`·`controls.py`의 작성자는 아니다. 이 builder 및 실제 생성 후보의 독립 검토는 다른 검토자가 수행해야 한다. 이 파일 작성 과정에서는 Python 실행·import·compile·과학 계산·Git·네트워크·백업 작업이 없었다.

## 1. 정확히 무엇을 생성하는가

실제 완료 입력을 모두 검증한 뒤 새 directory에 다음 두 파일만 만든다.

| Candidate 상대 경로 | 허용 변경 |
|---|---|
| `DAG.json` | 기존 `CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE` 노드에 `owner_return_parent_event_native25_20261028` 링크 하나 추가 |
| `returns/CR_PARENT_EVENT_NATIVE25_20261028.json` | 실제 최종 S/D, source R3, 과학·검토·예산·게시 증거에서 새 scoped owner return 생성 |

후보 밖에 `CENTRAL_BUILD_PROOF.json`을 별도로 만든다. 원 DAG와 central checkout, 기존 return, 원 unit 파일을 수정하지 않는다. 기존 CR 노드의 `current_status`·`contract`·dependency도 변경하지 않는다. 기존 proper injection·low-birth·HeIII return 및 B3h를 포함한 나머지 owner metadata는 그대로 보존한다.

링크를 지운 후보 전체가 원 DAG와 exact-number canonical JSON으로 같아야 한다. 또 나머지 87 nodes, 17 integration edges, node 외의 모든 top metadata, N4/N5/N6/N7 및 B3h node와 기존 CR return fields를 별도로 hash한다. `Decimal` JSON parsing으로 과거 숫자를 binary64로 다시 반올림하지 않는다. 이 canonical form은 로컬 보존 증명용이며 RFC 8785 구현을 주장하지 않는다. 원 raw DAG hash는 별도로 유지한다.

집계는 현재 `28/88`, 역사적 `27/88`, 이번 효과 `0`이다. 역사적 27→28은 이전 외부 B3h 완료에 따른 변화다. 현재 qualified owner return의 실제 count를 확인하고 status 문자열을 세지 않는다. PR236의 미병합 32/88은 더하지 않는다. 새 scoped child `1/1` 및 R/C `20/20`은 각각 실제 입력 검증 후에만 쓴다. N4/N5 `PARTIAL_OPEN`, N6/N7 `PREDECESSOR_GATED`, L4 false와 global completion/error/budget/currency null을 유지한다.

## 2. Root 입력 manifest

최종 실제 입력이 준비된 뒤 root가 `CR_PARENT_EVENT_CENTRAL_BUILD_INPUT_V1` JSON을 만든다. 미정 값을 채운 예시 JSON이나 template candidate는 제공하지 않는다. Top fields는 다음과 같다.

- `schema`: 위 schema.
- `unit`: `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`.
- `identities`: 정확히 `S`, `D`, `central_parent`, `central_base_tree` 네 개의 실제 lowercase 40-hex ID. S는 실제 C09, D는 실제 C10 stage commit이어야 한다. 중앙 M은 후보 생성 전에 알 수 없으므로 생성 return의 `central_commit_M`은 null이다.
- `files`: 아래 표의 역할을 모두 포함한다. 각 pin은 `path`(absolute, regular, nonsymlink), `bytes`(positive integer), `sha256`(actual lowercase 64-hex)다. `controls`만 이 pin들의 비어 있지 않은 배열이다. 다른 role은 pin 하나다.

| `files` role | 실제 입력 및 결속 |
|---|---|
| `dag` | 최신 root가 실제 읽은 중앙 raw DAG |
| `central_baseline` | 현재 root baseline: `head`, `tree`, `DAG_sha256`, `completed=28`, `total=88`, `source_baseline` actual pin |
| `publication_state` | 실제 `parent_ops/pub_state.json`의 완료 snapshot; 정확한 R01–R10/C01–C10 20-stage chain |
| `contract` | frozen `CONTRACT.json`, SHA `01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162` |
| `input_manifest` | frozen 17-file manifest, SHA `2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3` |
| `report` | 최종 실제 report bytes; unit ID를 포함하며 root admission에 exact pin |
| `budget` | 실제 `BUDGET_CLOSEOUT.json` |
| `execution_budget` | 실제 이번 unit `EXECUTION_BUDGET.json` |
| `execution_ledger` | 실제 마지막 `evidence/EXECUTION_LEDGER.json` |
| `preparation_ledger` | execution budget이 hash로 결속한 실제 `evidence/C04_PREPARATION_LEDGER.json` |
| `primary` | 최종 실제 채택한 primary `RESULT.json`; run 이름을 하드코딩하지 않음 |
| `controls` | 실제 채택한 current-unit control `RESULT.json` pin 배열. 기존 50 controls와 targeted v2를 각각 포함할 수 있으며 재실행하지 않음 |
| `reference` | 실제 independent `RESULT.json` 또는 아래 검증된 `ACCEPTED_REFERENCE.json`; 이 exact primary의 path/bytes/SHA를 검사했어야 함 |
| `C9` | 아래 concrete C9 wrapper |
| `admission` | 아래 actual final root admission |
| `source_archive` | `CR_PARENT_EVENT_ARCHIVE_RECEIPT_V1`, `kind=SOURCE`인 실제 봉인 source receipt |
| `source_R3` | `CR_PARENT_EVENT_DUAL_RAW_R3_V1` actual dual original full-GET receipt |

`central_baseline.source_baseline`은 root의 실제 중앙 qualification file을 가리킨다. Qualification은 unit, `verdict=QUALIFIED_CENTRAL_BASELINE_NO_CR_PHYSICS_CHANGE`, `blocking_findings=[]`, `central_head/tree`, `dag_sha256`, current count 28/88, nodes 88/edges 17 및 actual `authoritative_return`·`count_authority`를 포함해야 한다. 기존 R07 qualification schema의 실제 field 계약을 재사용한다. 최신 HEAD가 바뀌면 해당 실제 HEAD·DAG·count authority를 새로 읽고 qualified file을 공급해야 한다. 이 builder는 remote HEAD를 조회하지 않으며 오래된 baseline을 최신이라고 선언하지 않는다.

Count authority의 actual raw bytes도 pin 검증 후 읽는다. 해당 return의 scoped observation이 actual DAG observation과 같아야 하고 top-level 및 observation의 explicit count 모두 28/88이어야 한다. 원 b99 baseline 파일은 새 중앙 변경이 생겨도 자동 덮어쓰지 않는다.

## 3. C9·root admission·예산 계약

Root와 합의한 C9 wrapper:

- `schema=CR_PARENT_EVENT_C09_INDEPENDENT_REVIEW_V1`, `unit`은 이번 단위.
- `decision=PASS_SCOPED_PARTIAL_RETURN`, `blocking_findings=0`.
- `reviewed_files=[{path,bytes,sha256}, ...]`: 실제 primary, reference, 모든 채택 control result의 exact pins를 최소한 포함한다. Reference가 composite이면 원 FAILED reference RESULT와 새 targeted recovery RESULT 두 개의 pins도 필요하다. 실제 독립 심사 본문은 별도 substantive review로 보존한다.

최종 `ADMISSION.json`:

- `schema=CR_PARENT_EVENT_FINAL_ADMISSION_V1`, `unit`, 실제 `S`.
- `decision=ADMITTED_SCOPED_PARTIAL_RETURN`, `automatic_next_node=false`, `L4=false`, `global_physical_completion=null`, `physical_heating_complete=false`.
- `reviewed_files=[{role,path,bytes,sha256}, ...]`가 `report`, `budget`, `primary`, `controls`, `reference`, `C9`, `source_R3`의 실제 bytes를 모두 결속한다. 여러 control files는 각각 `role=controls`로 넣되 absolute path는 중복하지 않는다.
- Admission은 C10 게시 전, 실제 D가 생기기 전에 만들 수 있다. D는 실제 최종 20-stage receipt에서 확인한다. Report가 admission 자체 hash를 포함하는 circular identity는 요구하지 않는다.

`BUDGET_CLOSEOUT.json`:

- `schema=CR_PARENT_EVENT_BUDGET_CLOSEOUT_V1`, `unit`, `cap_s=40`.
- `charged_cpu_s`, `measured_cpu_s`, `conservative_tail_cpu_s`는 실제 ledger와 일치한다.
- `all_runtime_attempts_pass`는 실제 실패 상태와 같아야 한다. 알려진 실패가 있으므로 최종적으로 false를 유지한다.
- `old_science_replays=0`, `global_budget_remaining=null`, `closed=true`.

Builder는 다음 metadata arithmetic만 한다. Scientific sums, fit, source quadrature, RR propagation을 다시 계산하지 않는다.

1. Preparation `all_cumulative_records`의 실제 receipt bytes를 읽어 unit/attempt/status/measured/tail/charged를 비교하고, 각 attempt의 maximum cumulative debit 하나만 선택한다. 원 실패 및 amendment를 합산 중복하지 않는다.
2. 이번 unit의 `evidence/ATTEMPT_DEBITS/*.json`을 읽어 terminal·accounting complete 여부를 확인한다. 각 attempt의 실제 maximum cumulative debit과 canonical ledger row를 대조한다.
3. 이번 unit의 `runs/*/RESERVATION.json`에 terminal ACK가 빠진 attempt가 있으면 거절한다. 과거 다른 unit의 `UNKNOWN_NO_ACK` 또는 budget은 옮겨 오지 않는다.
4. Preparation + worker + coordinator의 pure measured CPU와 conservative tail을 따로 합산한다. charged ≤40, remaining=40−charged, no-transfer/global-null를 검사한다. JSON float 기록 합산용 absolute allowance `1e-10 CPU-s`는 과학 tolerance를 바꾸는 값이 아니다.
5. 과거·병렬 예산을 포함하지 않으며 remaining은 다음 단위에 자동 이월하지 않는다. `/proc` polling을 hard preventive aggregate cap proof로 승격하지 않는다.

현재 runner ledger의 실제 schemas를 사용한다. 보존된 실패 이름·예산 합계는 최종 파일에서 읽으며 source에 임의 숫자를 박아 넣지 않는다. Final report나 C9의 문장 의미를 자동 증명하는 도구는 아니다. Root의 actual admission과 다른 검토자의 최종 candidate review가 필요하다.

## 4. 과학 결과의 반영 한계

실제 primary scoped status, actual current controls, independently authored reference의 모든 실행 check를 확인한다. Independent result의 primary pin이 이번 manifest의 primary와 같아야 한다. Worker primary의 역사적 `independent_reference=PENDING` 문자열은 바꾸지 않고, 별도의 실제 final reference result를 함께 기록한다.

원 source record SHA `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf` 및 17-file manifest가 그대로여야 한다. Actual selected low birth `.1–10 eV`, same conditional 100 K inventory, `nb=8750/47`, proper history `[0,1e10] s`, proper gas frame과 volume mode를 확인한다. 식별된 coefficient를 원래 저장돼 있던 coefficient bytes로 표현하지 않는다.

실제 반환에는 target totals·coefficient/conditioning의 실제 저장값 및 exact evidence pins가 들어간다. H는 식별된 source 기여이고 He는 `s+p+2d=N_selected_He` 제약을 갖는 affine bookkeeping이다. 실제 s/p/d, 밖의 partner energy/history/pool/response, residual HeII state, proton work, full9600/full physical native25는 계속 null이다. 기본 cutoff는 retained component이며 caloric assimilation은 명시적 conditional fixture다. Binding convention residual과 retained photon은 각각 별도 포트다. 이 결과를 physical heating·foreign consumer activation·global physical completion으로 바꾸지 않는다.

Actual control evaluation 수는 supplied accepted control RESULT들에서 더하며 오래된 unit의 517/112/46 등은 새 count에 더하지 않는다. 실패한 runtime attempt는 control/science acceptance와 별도로 execution history에 남는다.

실제 C08 첫 reference는 3,450 중 3,446 PASS·4 oracle FAIL이었다. 이후 네 exact-half scalar만 복구한 `CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1`의 실제 생성물을 `files.reference`로 공급할 수 있다. Builder는 그 composite의 원 FAILED RESULT·실제 새 네-check RESULT·원 FAILED receipt·executed code를 다시 pin 대조한다. 원 3,446 PASS rows의 동일성, 정확히 네 ID만 교체, 원 네 failures의 보존을 metadata로 확인하며 수식을 재실행하지 않는다. Accepted 3,450 unique와 3,454 actual evaluations, 3,446 reuse와 4 new를 별도 기록한다. 합성 파일을 3,450개 full rerun이라고 표현하지 않는다. 새 복구가 실제 PASS하지 않았으면 composite 경로는 통과하지 않는다.

## 5. Source R3 재사용과 게시

Source archive receipt는 실제 S, `kind=SOURCE`, 정확한 archive name/bytes/SHA/members/payloads/manifest hash, sealed/no-rebuild를 결속해야 한다. Source identity의 D/M null 및 19/20은 당시 source 봉인 관찰로 보존하고, 완성된 workflow의 실제 20/20과 혼동하지 않는다.

R3 receipt의 Dropbox/Drive 각각은 actual HTTP200/full GET, HEAD·Range 아님, original file download, 전체 bytes/SHA 및 모든 payload hash/CRC PASS여야 한다. R3가 실제 archive receipt의 bytes/hash를 결속하는지도 검사한다. 이 builder는 백업을 재다운로드하거나 ZIP을 재생성하지 않는다. Source receipt와 payload classification은 기존 release helper의 actual validation 결과를 재사용하며 archive-only 파일을 새 raw-Git evidence라고 주장하지 않는다.

실제 입력이 모두 생긴 뒤 root가 사용할 CLI 형태:

```text
python parent_ops/prepare_central_parent.py \
  --input <absolute actual final build-input JSON> \
  --input-sha256 <actual SHA256 of that JSON> \
  --output-dir <new absolute parent_release_closeout/.../central_candidate directory> \
  --proof-file <new absolute parent_release_closeout/.../CENTRAL_BUILD_PROOF.json>
```

Angle-bracket 항목은 설명이며 실행값이 아니다. Source-only 작성 단계에는 이 명령을 실행하지 않는다. Output directory와 proof는 `parent_release_closeout` 아래에만 허용하고 서로 별도이며 create-only다. 모든 입력 검증이 먼저 끝나야 출력이 생긴다. 중단된 partial output은 지우거나 덮어쓰지 않고 보존한다. 성공 proof는 새 file hashes, 실제 입력 pins, 전체 DAG 보존검사와 `PENDING_DIFFERENT_REVIEWER`를 담는다.

Root의 후속 publisher는 다음을 실제 수행해야 한다.

1. Current remote HEAD/tree, 해당 새 return의 실제 부재, 최신 AGENTS/owner 변경을 다시 확인한다.
2. 다른 검토자가 실제 두 candidate와 proof를 읽어 수락하고 root가 exact pins로 채택한다.
3. 실제 base tree에 이 두 path만 적용한다. 이 작은 candidate directory로 전체 tree를 교체하지 않는다.
4. `expected_sha=current reviewed parent`, `force=false`로 게시한다. 다른 owner가 HEAD를 바꿨으면 이전 candidate/review/receipt를 보존하고 새 실제 base에 다시 결속한다.
5. 성공 후 actual M을 별도 receipt에 기록하고 실제 두 Git blob full readback/R3를 확인한다.

새 science node, scientific rerun, 자동 다음 unit은 이 helper의 기능에 없다. 개인 대화 전체 검색 unavailable, Drive partial inventory, 각 provider의 별도 scope·budget·UNKNOWN 기록도 그대로다.
