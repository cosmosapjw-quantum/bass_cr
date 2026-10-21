# bass_cr C21K 다음 대화 전체 인계문

이 문서를 다음 대화의 실제 작업 지시와 함께 읽는다. `$physmath-research-loop`, SciSpace, Exa, Wolfram을 사용하여 `cosmosapjw-quantum/bass_cr` 연구를 이어간다. 완료한 C21I/J/K 구현을 미구현으로 되돌리지 않는다. 먼저 이후의 실제 실행 반환을 확인하고, 변경된 의존성만 검증한다. 마지막 저장·게시의 권위는 함께 제공되는 **C21K_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json**이다.

## 1. 즉시 읽을 실제 파일과 Git identity

- `C21K_CLOSEOUT_REPORT_KO_20261021.md`: 연구·구현·검증·복구·게시 보고서.
- `NCP_C21K_FINAL_PROMPT_KO_20261021.md`: 전체 NCP 준비·실행·반환 명령과 계약.
- `C21K_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json`: 실제 content, document head, PR, delivery/closeout ZIP의 크기·SHA·세 저장처 ACK.
- K 실행 content: `bab323983dad5206e162dbfdaefc167f2fabea45`.
- K branch: `research/cr-c21k-epoch-cache-campaign-20261021`.
- K draft PR: `https://github.com/cosmosapjw-quantum/bass_cr/pull/89`.
- K unit: `research/cr_c21k_epoch_cache_campaign_20261021`.
- 최종 document head는 외부 권위 영수증의 `publication.document_head`에서 읽는다. 실행 source는 위 content에 고정한다. 문서 commit을 실행 content로 바꾸지 않는다.
- K `PUBLICATION_RECEIPT.json`은 실제 document head에서 읽어 checkout 밖에 둔다. 원 H/I receipt도 원 Git bytes로 checkout 밖에 둔다. PENDING 과거 문서를 고쳐 gate를 통과시키지 않는다.

현재 PR/ref는 다시 읽는다. 이후 변경이 문서인지 실행 source인지 구분한다. 파일이 없으면 Library의 실제 filename/ID를 확인하거나 세 저장처 ZIP을 복구하고 SHA를 대조한다. 옛 scratch repository, function store, native binary, bridge, Rust 설치가 현재 존재한다고 가정하지 않는다.

## 2. 기존 권위와 실제 업데이트

원 사용자 인계의 C21H/ I 게시 완료는 유지한다.

| 단위 | 실행 content 또는 근거 | 당시 document head |
|---|---|---|
| G | `e742d44f605c51c06615451774ba90af8f41f622` | 원 independent campaign 계약 유지 |
| H | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | `0ec4c55102766c40c554ffc6141eb08fba741c79` |
| I | `fe6bbaec2de5032b938aed0713623b9618ba70e6` | `26ab505dac2bfcb0cfd3d049f22bc408f4c86241` |
| 실제 native 반환 PR87 | 원 3 jobs/2469 native calls | `d3eaf596e46be4f994723fb742237a7399c290ed` |
| J | `55e6569a8f816e13babe4165f0fef3655f7299a3` | `fee0d6a3f1b6460a24a1ae60f50ee84971227e5b` |
| K | `bab323983dad5206e162dbfdaefc167f2fabea45` | 최종 영수증에서 읽음 |

H content는 I content의 실제 부모이고 I→J→K ancestry를 보존했다. PR85–88은 관측 범위에서 open/draft/unmerged였다. 새 대화에서 상태를 재조회한다.

초기 C21HI 인계의 native NOT_RUN은 당시 상태다. 이후 확인한 PR87 실제 완료 3건은 H common_ic/VigilODE/base, I common_ic/VigilODE/vectorized/base와 fd_half이다. 각823 native calls, 총2469다. 원 raw와 원 source identity를 가진 실제 실행이며, common fixture의 3-energy gas-manufactured 구조에서 nonphoto chemistry를 native로 호출했다. Full native MD14/전체 물리 driver가 검증됐다는 뜻은 아니다. 이번 K 작업의 새 native calls와 새 IVP solves는 각각0이었다.

마지막 외부 재조회는 `intake/FINAL_EXTERNAL_REFRESH_20261021_SUMMARY.json` 및 실제 primary excerpts를 읽는다. 2026-10-21 03:13:44 UTC 종료 관측에서는 bass_cr 새 반환이 없었다. 별도 REI PR199의 time8/16/32 actual 3건과 HE PR81의 packed canary는 새로 확인했으나 owner/binary/source가 달라 C21 완료 node나 성능 근거로 승계하지 않았다. WU PHYS73의 새 반환은 제한된 GitHub/Dropbox 범위에서 확인하지 못했다. 다른 대화 전체 검색은 실행 당시 unavailable이었고, 이후 제공된 대화 기억은 primary artifact의 대체물이 아니다. 전역적으로 다른 결과가 없다고 단정하지 않는다.

## 3. 완료한 K 이론·코드

원 private reference와 I adapter의 opacity binding에 한정해 epoch coefficient 재사용을 구현했다. 같은 event cell, 불변 fixture, source/globals, binary64 epoch에서 E와 K가 state에 의존하지 않음을 유도했다. Signed zero와 인접 binary64를 구분하는 strict float/np.float64 key, LRU16, finite-success-only, immutable bytes-backed 저장과 독립 writable 반환 배열을 쓴다. Hazard와 population은 state-dependent이며 epoch-only full-RHS cache를 만들지 않는다. 원 exact full-state/native guard는 별도다.

Opacity miss의 공통 scalar 계산을 원 왼쪽 결합 순서로 hoist했다. M9에서 exp 연산식28→2, M81에서244→2이며 cross-section3M은 그대로다. H는 원함수다. Approximation, tolerance relaxation, clipping, fastmath, 새 물리 또는 Schur/backend 통합은 없다.

`epoch_pilot_contract.py`와 `run_epoch_pilot.py`는 K 실행 identity, H→I→K ancestry, exact3 runtime, 원 H budget/build/CPU55/cleanup과 FD matching을 결속한다. NCP scheduler/binder와 원 archive의 exact historical admission staging helper도 여기에서 구현·focused 검증했다. NCP에 새 backend 설계나 campaign 구현을 넘기지 않는다.

| 파일 | 최종 SHA256 |
|---|---|
| epoch_adapter.py | `fc8009f7e185f7a257cbda0956317f4e7f358a8c548501c96e204aa7c94498bd` |
| run_epoch_pilot.py | `138ef2ed530c304c756cd75326fe8082ca6edf696ce86807cf2405fdd8f69038` |
| epoch_pilot_contract.py | `725f53c626610659ec8ede83845c998ca36f351bc6a96c2f9e4c5f580d157cc5` |
| EXECUTION_MANIFEST.json | `f80955787df909c4709d5076bcb017d7995fbf33197f41f04b5e03bc934e4744` |
| ncp/scheduler.py | `495f469faf432cba3764781e545d5711b7ba4f652c778b3aaa57589c64f04928` |
| ncp/make_campaign.py | `8f2a8cd2b3aa50d7f5991d0ae69fb9f4a171cf4010cb5d08619e722f3f5fa543` |
| ncp/prepare_historical_evidence.py | `6822cb69e2b70a5fe808ed8e167e57b501752f6eb2a0b5e2969678fb2c215163` |
| ncp/BACKLOG_INVENTORY.json | `3a329a1d593403a4c4d78f8f99eee3b9b521cece02734470738501791669c1eb` |
| ncp/DEPENDENCY_CONTROL_SCOPE_DECISION.json | `ee5718beee31ca9b91f00dd7a50e1e27f652b91d2be6182813d2e2832fe0f8e8` |

## 4. 실제 검증과 주장 경계

- 최종 epoch focused13 tests PASS. 실제 FIT threshold13.60/24.59/54.42를 포함한126 입력 조합에서 binary64 bit parity.
- Runner focused22 tests PASS: 실제 임시 Git과 명시적 doubles. 실제 고정 H/I/G/F34파일로 plan1회도 READY_EXECUTABLE_INPUTS_VERIFIED, doubles 없음.
- 저장 callback trace3경우: 각472 replies/40432 binary64 values, FD nodes와 저장 state 기반 physical summary bits 일치. 이는 저장 accepted states를 소비한 replay이고 새 적분이 아니다.
- I vectorized trace: provider823, opacity859 requests/329 misses/530 hits.
- I exact 및 FD-half trace: provider754, opacity790 requests/329 misses/461 hits. 원 full-RHS에서 이미 제거한69회와 opacity hit를 중복 합산하지 않는다.
- Scheduler/binder 수정 전33 tests PASS1.351s, 이후 tracker gate 변경 targeted1 PASS0.033s. 최종 source의34-test 전체 suite를 한 번 실행했다고 합치지 않는다.
- 실제 historical staging3 jobs/113 payload+3 receipts strict PASS; 별도 negative2 tests PASS. 원 archive sidecar를 삭제하지 않고 exact receipt-named admission copy만 create-only 생성했다.
- Process/affinity/signals/setsid는 실제 로컬 subprocess로 확인했지만 sandbox의 `/proc` 제약 때문에 ownership/start-tick 관측에는 explicit doubles를 썼다. 실제 NCP observer 및 실제 bound published-checkout/native build 통합은 미관측이다.
- 두 역사 source의 paired replay timing median은0.9364664941 및1.0004085537이며 두 범위가1을 가로지른다. 최종 fc8009 source의 timing으로 옮기지 않는다.

**일관된 callback 또는 전체 시간 가속 NOT_ESTABLISHED. K native 실행 NOT_RUN, native performance/NCP64 scaling NOT_EVALUATED. `global_error_bound=null`.**

Wolfram의 operation-tree SameQ는 IEEE 실수 연산의 전체 증명이 아니며 실제 bit 검증을 별도로 한다. 이상적 DAG 하한 max(W/P,L), list bound W/P+(1−1/P)L는 그 가정 아래의 정리다. 실제 RAM/quota/공유 I/O 환경에 무조건 성능 경계로 옮기지 않는다. 새 strong no-go는 채택하지 않았다.

## 5. NCP에서 실행할 유한 전체 행렬

52 logical slots=H8+G12+I16+K16. 역사 완료3개의 bytes와 context가 맞으면 pending49=H7+G12+I14+K16. 이는 이전 명시 잔여21와 이번 사용자가 확장한28(I추가12+K16)의 합이다. 중복 I baseline audit8은 제외한다.

원 G는 내부 single-worker independent container 한 개다: reference8개 후 원 native_source gate가 허용할 때 history4개. 따라서49 scientific jobs는38 top-level pending processes다. Matching context의 initial ready20이다. H→I/I→K 비교는 soft evidence이고, 같은 lane/mode의 matching base→FD 및 원 G 내부 gate만 hard dependency다.

| 실제 input 분기 | 추가 controls | 최대 새 attempt |
|---|---:|---:|
| 역사 native/bridge bytes와 H FD context 일치 | 0 | 49 |
| 같은 bytes, canonical H FD native/bridge/manifest path context 다름 | H base1 | 50 |
| 같은 원 source/owner/build pins의 유효 새 native 또는 bridge bytes | H base+I vectorized base+그 FD, 3 | 52 |

1과3을 더하지 않는다. 다른 source/owner pins는 admission BLOCKED다. 원 완료 근거는 역사로 보존하며 새 build와 matching reuse라고 표시하지 않는다. 실패·중단·timeout은 자동 retry하지 않는다. 동일 manifest의 COMPLETE payload만 검증해 resume 재사용한다.

실제64 CPU/128GB 배정은 host·owner allocation·affinity·cgroupv2 quota/RAM을 읽어 확인한다. CPU55를 제외하고 coordinator CPU/RAM을 따로 계상한다. 각 scientific worker1CPU/BLAS·OMP1 thread; 실제 독립 ready jobs만 동시 실행한다. 명칭64 CPU를64 physical cores 또는64배 가속으로 쓰지 않는다. RAM reserve는max(1GiB,12.5%); 실제128GiB면16GiB다. Per-job RSS budget은 현재 binary의 관측 또는 보수적 근거로 정한다. 예시 JSON의 null은 실행값이 아니다.

## 6. NCP 준비 순서 — 전체 명령은 NCP 인계문 사용

1. 실제 새 반환부터 확인해 완료를 재사용한다. Host owner allocation과 기존 작업을 확인하고 타 작업/CPU55를 건드리지 않는다.
2. 전체 history가 있는 Git에서 detached I=`fe6...`와 detached K=`bab323983dad5206e162dbfdaefc167f2fabea45` 두 checkout을 만든다. 원 G/H/I는 I checkout에서 실행하고 K는 K checkout에서 상속 H/I/G/F bytes를 검증한다. G e742/H40ea provenance와 실제 실행 checkout fe6는 구분한다.
3. 원 H/I 및 실제 K PUBLISHED receipts를 두 checkout 밖에 둔다. K receipt는 최종 document head에서 정확한 Git bytes로 읽는다.
4. 현재 유효 native/bridge binary를 재사용하거나 원 locked build를 수행한다. Native knownSHA=`1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`; 원 owner=`6ea2b1b4b3875c9163cafc45efe720afded43fc4`. Rebuilt native는 원 G가 owner_commit/build_exit/input_sha256/owner_source.tar/wrapper로 검증한다. 없는 NATIVE_BUILD_RECEIPT.json을 발명하지 않는다. Bridge의 원 H receipt와 VigilODE`8a8bd409b1d96c7b7421f496d229e119fd3d284e`/Diffsol0.17.1/Cargo.lock pins를 따른다.
5. Original native archive를 아래 identity로 복구한다. `prepare_historical_evidence.py --archive ORIGINAL --out NEW_ADMISSION_ROOT`로 named payload+receipt만 별도 복사한다. 원 tar에는 wrapper sidecar가 있어 직접 extracted job dirs를 binder에 넣으면 exact payload 검사를 실패한다. 원 tar/sidecar/receipt/raw는 변경하지 않는다.
6. 실제 absolute path로 SITE_BINDINGS를 채우고 `make_campaign.py --bindings SITE --out NEW_CAMPAIGN`을 실행한다. UNBOUND template는 실행하지 않는다. `scheduler.py --inspect-resources`와 현재 OWNER_ALLOCATION을 결속한다.
7. Plan 뒤 `scheduler.py --manifest ... --allocation ... --out UNIQUE_NEW_OUT --execute`. 같은 manifest/output의 재개만 `--resume`. Scientific job300s, G container3660s, 전체21600s, 원 native/RHS200000 및 percall15s 한도를 유지한다.
8. Allocation→coordinator lease/pin→실제 `/proc` ownership/starttick/RSS capability probe가 순서대로 통과해야 science가 시작된다. 실제 환경 호환 문제는 구체적인 작은 수정만 하고 변경 의존성을 focused 검증한다. 큰 backend나 새 기능을 여기서 시작하지 않는다.
9. Raw stdout/stderr, 실패, source/native/build/publication identity, DAG 상태, 자원과 elapsed를 create-only로 반환한다. `SCOPED_HOLD`를 모든 job COMPLETE로 올리지 않는다. 실행·게시·세 저장처 백업·DAG 상태를 각각 표시한다.

원 native archive:

```text
C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz
2568680 bytes
SHA256 2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3
Library libfile_b26c9616e4748191ba98b19b1bea5d04
File file_00000000c0cc820b982a789de34a62ed
Drive 1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u
Dropbox id:BSpOijBcT10AAAAAAD_T4A
```

## 7. 중단·복구의 정확한 상태

게시 직전128파일 tree 생성 요청은 반환 ACK 없이 중단됐다. Commit/ref/PR 요청은 그 전에 하지 않았다. 그 사이 자동 작업공간 정리로 scratch와 function stores가 사라졌다. 사용자 삭제로 해석하지 않는다.

Checkpoint2를 원 ZIP SHA와79 payload hash로 복구했고, final epoch/runner/theory/replay raw는 그대로다. NCP source3+tests3+계획2는 실제 대화의 원 생성/출력으로 조립하여 모두 원 SHA와 정확히 일치했다. NCP 전체 인계문45254bytes, 보고서17942bytes도 원 SHA로 복구했다. 따라서 실제 실행 source/pins 변경은0이고 옛 과학 suite를 반복하지 않았다.

원 NCP34-payload manifest, 초기14/23-error/24-failure/24-pass full raw, 원 STAGING_RECEIPT의 동적 시각, 원 C9 review JSON 및 handoff review JSON 등의 일부 보조 bytes는 복구하지 못했다. 원 identity와 역사 실패·NOT_PUBLISHED는 `administration/RECOVERY_INVENTORY_20261021.json`, `ncp/RECOVERY_RECEIPT_20261021.json`, `planning/RECOVERY_MANIFEST.json`에서 보존했다. 새 manifest/복구 review 문서를 원 bytes라고 주장하지 않는다. 최종33+targeted1·staging·negative tool-return은 전사 복구 provenance를 명시했다. 원 검토의 PASS_SCOPED는 검토한 동일 source hash에만 연결하고 새 검토를 했다고 쓰지 않는다.

복구본 checkpoint도 세 저장처 ACK를 받았다:

```text
BASS_CR_C21K_RECOVERED_IMPLEMENTATION_CHECKPOINT_20261021T031046Z.zip
366865 bytes / 121 members / 120 payload
SHA256 9bfd9ca6f49d9501e85ee566d67a5607446063572949df5ed0ce78e4ecd757f0
Library libfile_8dfceb069f108191a439669bb16df6e0
File file_00000000e294820ba1eb74d2652053b5
Drive 1K8lDFZ1bSFU-lpUaX9BwURKZlzSDiEkm
Dropbox id:BSpOijBcT10AAAAAAD_eVA
```

이는 최종 Git content/문서 마감본과 구분되는 중간 복구 checkpoint다. 최종 ZIP 두 개의 실제 identity와 provider ACK는 최종 외부 영수증 `backups.delivery`, `backups.document_closeout`에서 읽는다. Delta는 그 manifest의 base SHA가 맞는 문서에만 적용한다. 원 과학 source/test/raw를 재적용하거나 실패 이력을 새 성공으로 덮어쓰지 않는다.

## 8. 다음 작업 경계

새 NCP 반환이 있으면 먼저 원 source/fixture/build/publication/완료 receipt와 전체 payload를 확인하고 DAG의 해당 node만 전환한다. 새 반환이 없으면 이 완료된 연구를 반복하지 말고 준비된 NCP 실행을 현재 배정에 결속하는 것이 다음 작업이다. 이 대화 환경에서 가능한 구체적 코드 수정은 구현·focused 검증·push까지 완료한다. C21F 게시 완료, C21G 독립 실행 계약, 보호 CPU55, create-only 백업, FP64, 원 실패/raw/역사 NOT_PUBLISHED, 기존 모든 과학 HOLD와 `global_error_bound=null`을 유지한다.

실행 성공, 게시 성공, 백업 성공, 과학적 승인과 속도 향상 주장은 서로 다른 근거로 판정한다. 실제 ACK 없는 저장·게시를 완료로 쓰지 않는다. 새 강한 no-go나 전역 오차 경계를 선언하지 않는다. 필요한 최종 산출물은 실제 결과, 변경 이유, source-matched 검증, 갱신된 DAG, 세 저장처의 실제 영수증, 다음 대화용 인계문이다.

### 최종 게시 인코딩

큰 증거 JSON과 UNBOUND preview는 원 SHA를 유지하는 무손실 gzip으로 Git에 게시한다. `administration/PUBLICATION_ENCODING.json`의 decoded SHA와 최종 delivery `original_publication_inputs/`의 원 JSON을 대조할 수 있다. 실행 코드·tests·backlog/control pins는 그대로다. 새 NCP manifest는7606bytes/SHA256 `6784a3b04a09c354d63d9b5613b452efeaaeaab16b599b298ba4f59e7d425ce8`,22payload/192450bytes다. 최종 content116파일,964255bytes; CONTENT_MANIFEST19325bytes/SHA256 `dd7d9d3d79acbbbde88ee1994a175a31e1cf2369c5394e6233b50dbff300f4c6`. 이전 uncompressed115파일 freeze는 역사 시도로 보존하며 최종 manifest와 혼동하지 않는다.
