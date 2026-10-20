# NCP 전체 최종 인계문 — C21I native exact 선택 한 행 / 2026-10-20

cosmosapjw-quantum/bass_cr 연구의 NCP 준비를 이어가줘. 이 문서와 C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json을 먼저 전부 읽고, 현재 자원과 실제 파일을 확인한 뒤 준비된 **common_ic / vigilode-rodas5p / vectorized_exact / base 한 행**을 진행해라. 이미 완료된 H base, I vectorized base, I vectorized FDhalf의 raw를 재사용한다. C21I 이론·최적화 구현·제조 검증을 새 미구현 작업으로 되돌리지 않는다.

**이 문서 작성 시 실제 native exact는 NOT_RUN, native exact performance는 NOT_EVALUATED, 현재 NCP 자원·실행 경로는 NOT_OBSERVED다.** C21J는 실제 원 native 반환에 대한 trace 복원과 네 callback replay를 완료했으며 새 native/ODE를 실행하지 않았다. 보호 CPU55, worker1/job1, 원 허용오차·300초/200000 상한, create-only 원본 보존, global_error_bound=null과 과학 HOLD를 유지한다.

## 1. 먼저 읽을 권위와 source를 구분한다

최종 외부 영수증 **C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json**에서 실제 최신 PR/ref 관측 시각과 D2 document head, 두 ZIP 및 provider별 ACK·검증 수준을 읽는다. D2 자신의 commit과 D2를 포함하는 CLOSEOUT ZIP의 SHA/ID를 이 본문에 순환 참조로 넣지 않았다. 아래 D1 head는 확정된 이전 문서 관측이며 현재 최종 head를 대체하지 않는다.

| 역할 | 실제 고정 값 |
|---|---|
| repo | cosmosapjw-quantum/bass_cr |
| **이번 live native 실행 source** | **fe6bbaec2de5032b938aed0713623b9618ba70e6** |
| H 실행 content | 40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8; I의 실제 부모 |
| H 게시 document head | 0ec4c55102766c40c554ffc6141eb08fba741c79 / draft PR85 |
| I 게시 document head | 26ab505dac2bfcb0cfd3d049f22bc408f4c86241 / draft PR86 |
| 기존 실제 native evidence 첫 content | 0f2d195aee3c08b372d020bcd6caba87db64a83c |
| 기존 native evidence 문서 head | d3eaf596e46be4f994723fb742237a7399c290ed / draft PR87 |
| **이번 분석·보고·패킷 게시 content** | **55e6569a8f816e13babe4165f0fef3655f7299a3** |
| C21J 게시 branch / PR | research/cr-c21j-native-trace-replay-20261020 / draft PR88 |
| C21J D1 document head | e04b19669b1542b4537448c764d1dc02ebc8b7b6 |
| 최신 D2 head와 이후 상태 | 최종 외부 권위 영수증과 실제 PR/ref를 읽을 것 |

C21J content의 실제 부모는 PR87 d3이다. 원 78개 content payload와 그 manifest는 고정됐고, D1은 README·DAG의 문서 변경 및 부가 문서10개를 추가했다. PR88은 D1의 실제 관측에서 open/draft/미병합이었다. Source55e는 이 진단·보고·실행 패킷을 게시한 commit이고, **native runner checkout HEAD는 fe6**이어야 한다.

먼저 현재 repo의 AGENTS.md, docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md, docs/HPC_ACCURACY_POLICY_KO.md, .codex/readback-policy.json을 읽는다. 고정 C21J 단위의 아래 파일을 함께 읽는다.

- ncp/NCP_C21J_EXACT_PILOT_KO.md
- ncp/PILOT_CONTRACT.json
- ncp/run_exact_once.sh
- ncp/STATIC_VALIDATION_RECEIPT.json과 원 validation raw
- ncp/AUTHORITY_DOCUMENT_IDENTITY_CORRECTION.json
- D1의 ncp/PUBLICATION_BINDING.json
- C21J_RESEARCH_REPORT_KO.md 및 evidence/analysis_attempt_02/ANALYSIS.json, evidence/replay_attempt_02/REPLAY_REPORT.json

고정 packet locator: https://github.com/cosmosapjw-quantum/bass_cr/blob/55e6569a8f816e13babe4165f0fef3655f7299a3/research/cr_c21j_native_trace_replay_20261020/ncp/NCP_C21J_EXACT_PILOT_KO.md

D1 publication binding locator: https://github.com/cosmosapjw-quantum/bass_cr/blob/e04b19669b1542b4537448c764d1dc02ebc8b7b6/research/cr_c21j_native_trace_replay_20261020/ncp/PUBLICATION_BINDING.json

원 packet의 작성 시각은13:39:37 UTC이고 PENDING_ROOT_PUBLICATION/null 필드는 그 당시 상태다. D1 PUBLICATION_BINDING은 실제 packet content55e/PR88을 결속한다. 원 패킷이나 원 validation raw를 뒤늦게 고쳐 당시 이미 게시됐던 것처럼 만들지 않는다. Native source나 one-job contract가 바뀐 것은 아니다.

이전 권위 문서는 NCP_C21HI_FINAL_PROMPT_KO_20261020.md와 다음 고정 문서다.

https://github.com/cosmosapjw-quantum/bass_cr/blob/26ab505dac2bfcb0cfd3d049f22bc408f4c86241/research/cr_orchestration_20261020/NCP_ORCHESTRATION_KO.md

이 문서의 정확한 Git bytes는19,254 bytes, SHA256 a2f9066f021659c2a2124425096d09e83df43ae72143646203d50be69427584b, Git blob5aeaf344fe88d21a5648d9a6c515ad083adc4646이다. 이전19,255-byte working copy에는 trailing LF 하나가 더 있었고 그 SHA1ab262e072995817d35d15a5ac400320e00a4aaeb51e6c191c50071fa0c1516a는 exact Git identity가 아니다. 원 static validation은 그 작업 사본 검사를 기록한다. Additive identity correction을 적용해 해석하고 runtime source나 과거 검증 raw는 보존한다.

## 2. 이번에 한 행을 선택한 이유와 이미 확보한 근거

실제 PR87에는 다음 세 작업이 COMPLETE로 반환돼 있다.

| 기존 작업 | actual native calls | job wall (s) |
|---|---:|---:|
| H common_ic / VigilODE / base | 823 | 1.2116977100085933 |
| I common_ic / VigilODE / vectorized / base | 823 | 1.4319355220068246 |
| I common_ic / VigilODE / vectorized / fd_half | 823 | 1.434721386001911 |

각 runner/native exit0이고823개 응답이 모두 OK다. Accepted36/rejected16/LU52, RPC rhs400/jac36/partial_t36이다. 합계2469는 기존 native 실행 횟수다. I 두 작업은 vectorized, cache_capacity0이었으므로 live exact가 실행됐다는 뜻이 아니다.

Common fixture는 FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT이며 source 표기는 PINNED_PR79_MD14_RATE_MANUFACTURED_3_ENERGY_GAS다. Nonphoto chemistry는 실제 native가 계산했다. M9, Y0.08130135170951498, dx1e-4, full/integrated28이며 완전한 native MD14/source12-cell 연구나 관측 checkpoint는 아니다.

C21J에서 H/I base의 전체28 endpoint·모든 ledger·endpoint diagnostics·세 raw segment result 객체·accepted physical records39개가 bitwise 같음을 확인했다.39개에는 cell 시작점3개가 포함된다. 전체 RHS 요청열은 다음 항등식으로도 닫혔다.

**823 = rhs400 + jac36 × (base1 + gas4 × 양쪽2) + (partial_t36 − flat branch3) × (base1 + time nodes2).**

Cell별 full physical (t,u) binary64 LRU16의 hit는 각각23, 전체69이며 miss754다. H base/I base/I FDhalf 세 저장 trace가 각각 같은 계수를 가진다. 작은7-input native EVAL key의100 hits는 다른 정책이다. 추가31쌍은 tau만 다른4쌍, tau+passive ledger가 다른27쌍이다. Native chemistry 입력이 같아도 전체 optical RHS·광자 의존 ledger 도함수는 달라질 수 있다. Passive ledger 값 자체를 RHS 인과 입력이라고 주장하지 않는다.

원 callback을 저장 native 응답표로 재생한 경우는 **I base에 H, I vectorized, I exact를 각각 적용한3개 + I FDhalf에 I exact를 적용한1개**, 총4개다. 각각472 replies/40432 binary64 values와 FD nodes·physical summary reconstruction이 PASS_SCOPED다. Nonexact는823table queries, exact는754table queries였다. Accepted states를 저장 trace에서 읽었으므로 새 trajectory integration은 아니다. 새 live native process/chemistry 및 ODE 호출은0이다.

실제 live exact에서는 cache hit에도 provider/process/deadline/context/file lease guard가 실행된다. Table replay는 이 현재 live guard와 native process가 성공한다는 증거가 아니며 replay timer는 실제 native benchmark가 아니다. **이번 한 행의 남은 질문은 원 exact admission/live guard 아래의 실제 calls·cache counters·전체 결과 동일성·시간 비용**이다.69/754를 새 actual counter의 이미 관측된 값으로 미리 기록하지 않는다.

## 3. 실행 직전 현재 결과와 자원 admission

이번 문서에서 현재 NCP 자원, 현재 CPU 배정, 현재 binary path, 현재 toolchain 존재는 관측하지 않았다. 실행자는 실제로 접근 가능한 환경을 읽고 현재 값을 새 admission 기록에 결속한다. 과거 scratch path나 오래된 NCP inventory를 현재 자원으로 사용하지 않는다.

1. 관련 repo/branch/PR 및 세 저장처의 최근 receipt·native 반환을 먼저 확인한다. 같은 source manifest, canonical fixture SHA, method, variant, optimization, native/bridge/build, controls의 COMPLETE raw와 terminal receipt가 있으면 REUSED로 처리한다. Matching job이 진행 중이면 복제 제출하지 않고 기존 작업을 추적한다. 다른 대화 접근이 실패하면 실제 오류와 조회 범위만 남긴다.
2. 현재 repo remote/HEAD/dirty/worktrees, campaign별 배정, CPU affinity, RAM/cgroup, disk 여유, process tree와 watcher/checkpoints를 읽는다. **CPU55를 제외한 실제 배정 CPU 하나**를 사용한다. Affinity mask에 들어 있다는 사실은 독점 배정 증거가 아니다. 과거 CPU62,64core/128GiB를 현재 가용량으로 사용하지 않는다.
3. 동시 native job1, Python/native/BLAS/OpenMP/MKL/NumExpr/Rayon worker1을 유지한다. NumPy import 전에 environment를 설정하고 새 Python process에서 시작한다.
4. 기존 dirty checkout을 reset/clean/stash/rebase하지 않고, 다른 job/watcher를 중단하거나 checkpoint를 덮어쓰지 않는다. 현재 상태를 보존한 별도 detached full checkout과 새 output/control 디렉터리를 사용한다.
5. 상세 LIVE_INVENTORY/process/context 원문은 비공개 원본으로 보존한다. 공개 결과는 허용된 scope 요약과 SHA로 남긴다. 접근·자원·artifact가 막혔다면 실제 ACCESS_UNAVAILABLE, RESOURCE_NOT_ADMITTED, ARTIFACT_MISSING 같은 구체 상태를 반환한다. 관측하지 않은 서버 전체나 NCP disk 전체의 부재를 주장하지 않는다.

C21J 게시 직전의 external metadata refresh는17:22:11–17:22:46 UTC, cutoff13:50 UTC였다. 해당 Library/Drive/Dropbox dossier 직접 조회 범위에서 새 candidate0, 새 archive download0이었다. 그 뒤 변경은 다시 확인한다. 당시 Personal Context는 SERVICE_ERROR: Personal context is unavailable for this conversation.으로 실패했으므로 다른 대화 전체 결과부재를 확인한 상태가 아니다.

## 4. 이번 DELIVERY 복구와 원 archive

### 4.1 C21J 전체 연구 DELIVERY

| 항목 | 실제 값 |
|---|---|
| 파일명 | BASS_CR_C21J_RESEARCH_DELIVERY_20261020T173607Z.zip |
| bytes | 3495267 |
| members / payload members | 135 / 134 |
| SHA256 | b3f867d40f2f760e5f61168a1bec858d2c9a1dba646e7b56d015c569283a1ae8 |
| Drive ID | 1VUN3oQO_U3VHB3n7PDcdmudhsKwt5QPj |
| Dropbox ID / rev | id:BSpOijBcT10AAAAAAD_aDQ / 65e4ba52c16ad0af03d47 |
| Library ID | libfile_7f604c8e9d1081919c828e9a8fc97cd4 |
| File ID | file_000000005a88820ba56ff654e3927b65 |

DELIVERY에는 D1 시점 단위, 고정 source24 closure, 원 native archive와 복구 authority가 들어 있다. 실제 경로·SHA는 archive manifest를 읽는다. 이는 **오프라인 callback replay의 복구 묶음**이며 live NCP 전체 실행 tree를24파일로 대체하는 계약이 아니다. 이 최종 NCP D2 본문은 DELIVERY보다 뒤에 작성됐으므로 해당 DELIVERY에 포함됐다고 표시하지 않는다.

D2 이후 작은 **BASS_CR_C21J_PUBLICATION_CLOSEOUT_20261020T*.zip**에는 문서 delta와 실제 D2 관측이 보존된다. 실제 최신 파일명·ID·SHA·D2head는 **C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json**을 현재 저장처에서 읽는다. 최종 외부 영수증이 둘 이상의 ZIP과 실제 최신 document head를 결속한다. 자기 자신의 head/ZIP SHA를 사전에 본문에 순환 참조하지 않는다.

Dossier는 Drive folder1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy, Library/Dropbox /BASS_DERIVATION_DOSSIERS_20260912/bass_cr다. 전체 compressed bytes·manifest·필요 payload identity를 확인한다. 같은 원 bytes를 복구했다는 이유로 과학 suite를 다시 돌리지 않는다. DELTA_MANIFEST는 base SHA가 맞는 문서에만 적용하고 source/test/raw를 재적용하지 않는다.

### 4.2 PR87 원 native 반환 archive

| 항목 | 확정 값 |
|---|---|
| 이름 | C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz |
| bytes / SHA256 | 2,568,680 / 2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3 |
| 구성 | 184 tar members,156 regular files,155 manifest payload entries |
| Drive | 1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u |
| Dropbox ID / rev | id:BSpOijBcT10AAAAAAD_T4A / 65e43db2185370af03d47 |
| Library / File ID | libfile_b26c9616e4748191ba98b19b1bea5d04 / file_00000000c0cc820b982a789de34a62ed |
| 내부 root | C21GHI_NATIVE_EXECUTION_20261020/ |
| payload manifest | PACKAGE_PAYLOAD_SHA256SUMS.txt;20,712 bytes |
| manifest SHA256 | 40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a |

초기 intake는 Drive 원 bytes와155payload SHA를 확인했다. 이후 Library에 실제 보존됐고 scratch 상실 후 복구에도 사용됐다. Dropbox metadata 확인을 Dropbox 원 bytes 다운로드로 표시하지 않는다. 현재 이미 같은 archive가 있으면 재다운로드하지 않는다.

이 archive에는 기존 세 job의 원 native/RPC/FD/result/raw와 controls, bridge build 실패/성공, 성공 bridge가 있다. **Known native executable은 들어 있지 않다.** Private LIVE_INVENTORY3개는 비공개 보존하고 공개 Git에 복사하지 않는다. Archive의 원 성공/실패 raw·역사 영수증을 수정하지 않는다.

## 5. full fe6 runtime과 외부 controls

새 isolated detached checkout의 HEAD는 fe6bbaec2de5032b938aed0713623b9618ba70e6이어야 한다. H/I는 같은 root repository에 있고 Hcontent의 Iancestor 관계와 manifests를 확인한다. C21J55e 또는 최신 doc head를 live source checkout으로 사용하지 않는다.

| 필요 항목 | 준비와 identity |
|---|---|
| F runtime | research/cr_c21e_event_native_20261018/의 원 runtime10개와 manifest |
| G runtime | research/cr_c21g_reference_refinement_20261019/의 원 runtime4개와 manifest |
| H runtime | research/cr_c21h_vigilode_bridge_20261019/의 원 runtime8개와 manifest |
| I runtime | research/cr_c21i_callback_optimization_20261020/의 원 runtime3개와 manifest |
| G baseline 입력 | common_ic와 native_source 각각 fixture.json/radau.json/SUMMARY.json, 총6개 |
| baseline root | F 단위의 evidence/C21F_NATIVE_NCP_20261018T1358Z |
| 외부 H/I controls | checkout 밖의 새 CONTROL에 H_PUBLICATION.json, I_PUBLICATION.json |
| 패킷 source | content55e의 ncp/ 파일과 D1의 additive binding/correction |

G의 입력 검사는 선택행이 common_ic여도 두 fixture의 baseline 여섯 파일을 요구한다. Native_source의 baseline을 빼서 admission을 실패하게 만든 뒤 검사를 우회하지 않는다. 전체 fe6 tree가 이 의존성을 보존한다.

H execution manifest SHA256은7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb이고 I manifest SHA256은f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec이다. 고정 I runner14,719 bytes의 SHA256은1a3f4d9066bedc3a8d7466723e8f344fa451c0c6a85c48bf0efe03210d6d8a43이다.

외부 PUBLISHED receipts는 현재 H/I 문서 영수증과 actual ref/manifest를 대조한다. 원 archive의 control/H_PUBLICATION.json SHA는57b81b524b83d7c05f82394b0fba1d4d57d99ed051b92d673fd9c081d702aed4, control/I_PUBLICATION.json SHA는28641242b36a8392e296fa7801212908296b9fd5fcf035574483e2399d2a2af2다. 원 content 안의 당시 pending receipt를 수정해 publication guard를 통과시키지 않는다. Manifest/receipt 내용을 새 source에 임의로 맞춰 쓰지 않는다.

정확한 Git bytes를 복구할 때 trailing LF를 덧붙이지 않는다. C21J INPUT_PINS의 source24/return60은 replay authority이고 bytesSHA ac339fc832ccc2e4b177034151a6adcf1510d82646b0c7e04d68bfc2be7aea90, canonicalSHA5c741dcaf415961d09bb4f1bf10c9dad600c0af3d0791e18750655b006957fea다. 이 작은 closure만 있으면 live runner 의존성이 모두 준비된다고 표시하지 않는다.

## 6. bridge는 유효 build를 먼저 재사용한다

원 archive의 binary/bass-cr-c21h-rust-bridge는4,888,736 bytes, SHA256 **717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30**이다. 성공 receipt build_success/BUILD_RECEIPT.json의 SHA256은 **c846c35621dd9a0aa3c5bbfb90e94da0f022e934cf2ea1342270d61eda4b5190**이다.

실제 복구 bytes·receipt/source-files identity, 현재 architecture/ELF loader·공유 library·실행 권한을 확인하면 **Rust 설치 없이 재사용할 수 있다**. 원 receipt 내부의 과거 build path는 보존하고 현재 binary path를 --bridge에, 원 receipt를 --bridge-build-receipt에 준다. 읽기 전용 host/loader 정보로 호환성을 확인하고 기존 bridge protocol/smoke/physics suite를 자동 반복하지 않는다.

현재 유효 bridge가 없거나 실제 호환 문제로 재사용할 수 없을 때만 고정 helper로 locked compile한다. CARGO/RUSTC는 현재 실제 executable이고 BRIDGE_BUILD는 새 절대 output 경로다. Compile budget은 native job의300초와 분리한다. 원 첫 build의 timeout300s/exit124와 두 번째 Rust1.94.1 locked build7분01초 성공은 모두 보존한다.

```bash
H="$WORKTREE/research/cr_c21h_vigilode_bridge_20261019"

taskset -c "$CPU" bash "$H/rust_bridge/build_bridge.sh" \
  --cargo "$CARGO" --rustc "$RUSTC" --target-dir "$BRIDGE_BUILD"
```

실제 helper는 cargo build --locked --release --jobs 1을 호출한다. VigilODE pin은8a8bd409b1d96c7b7421f496d229e119fd3d284e, Diffsol0.17.1, Cargo.lock SHA256 d30f7f6437b7704f845ba85f8206c94810fbd4ec1a48db9cba06b7b77604c892를 유지한다. 필요한 locked dependency가 cache에 실제 존재할 때만 --offline을 추가한다. 새 pin, backend 변경, 과거 sandbox linker workaround를 자동 적용하지 않는다.

구체적인 작은 호환 수정이 실제 필요하면 그 문제·source diff·변경 의존성만 여기에서 구현·focused 검증·push한 후 NCP에 전달한다. 큰 Schur/backend integration·새 기능 구현을 이 NCP 행의 시작 조건으로 맡기지 않는다.

## 7. native executable — 선택 행은 known SHA를 요구한다

Native owner는 cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4다. 선택 행이 요구하는 binary는5,003,448 bytes이며 SHA256은 **1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40**이다.

실제 현재 matching 파일을 먼저 확인한다. 없으면 원 PR82의 verified binary/build artifact와 현재 영수증을 찾아 복원한다. 과거 /root/C21F_NATIVE_RUN_20261018T1358Z/build/native_point를 현재 경로로 가정하지 않는다. 새 native return archive 안에 이 binary가 있다고 주장하지 않는다. 확인하지 않은 PR82 archive 이름·ID를 생성하지 않는다.

원 G authority에는 RECORDED_PINNED_OWNER_BUILD를 admit하는 일반 경로가 구현돼 있다. 이 경로는 build/native_point, owner_commit.txt, build_exit.txt, input_sha256.txt, owner_source.tar와 고정 native_point.rs를 대조한다. 그러나 **이번 한 행은 다른 SHA로 새로 만든 artifact를 자동 admit하지 않는다.** Known artifact를 복구할 수 없으면 그 실제 상태를 반환한다. 필요해진 별도 새 build는 source/build identity·영향 검증을 별도로 다룬다.

원 build_native.sh NEW_BUILD_DIRECTORY [EXISTING_OWNER_GIT_REPOSITORY]는 locked/offline owner build를 사용하지만 내부 CARGO_BUILD_JOBS=2다. Taskset 한 CPU가 compiler child 수를1로 바꿨다고 쓰지 않는다. 이를 이번 선택 행의 필수 준비나 자동 build 단계로 추가하지 않는다. Frozen helper를 편집해 원래 jobs1이었다고 표시하지 않는다.

## 8. 한 번만 실행할 명령과 실제 environment

아래 WORKTREE, CONTROL, CPU, NATIVE, BRIDGE, BRIDGE_RECEIPT, PYTHON, NEW_EXACT_JOB은 현재 NCP inventory·복구·배정 결과에서 실행자가 얻는 실제 값이다. 경로를 사용자에게 채우라고 되묻기 전에 실제 접근 가능한 환경에서 확인한다. NEW_EXACT_JOB은 아직 없는 절대 경로다.

다음 direct runner 호출과 다음 절의 wrapper는 **동일 행을 수행하는 두 진입 방식**이다. 실제 실행은 하나만 선택한다. Wrapper를 사용했다면 direct command를 또 실행하지 않는다. H/I baseline 새 실행, FD parent, mode sweep을 추가하지 않는다.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1

I="$WORKTREE/research/cr_c21i_callback_optimization_20261020"
G="$WORKTREE/research/cr_c21g_reference_refinement_20261019"
SOURCE="$WORKTREE/research/cr_c21e_event_native_20261018"
BASELINE="$SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"

"$PYTHON" "$I/run_optimized_pilot.py" native --optimization vectorized_exact \
  --publication-receipt "$CONTROL/I_PUBLICATION.json" \
  --c21h-publication-receipt "$CONTROL/H_PUBLICATION.json" \
  --source-dir "$SOURCE" --c21g-unit "$G" --baseline-dir "$BASELINE" \
  --bridge "$BRIDGE" --bridge-build-receipt "$BRIDGE_RECEIPT" \
  --native "$NATIVE" --cpu "$CPU" --fixture common_ic \
  --method vigilode-rodas5p --variant base --out "$NEW_EXACT_JOB"
```

### 준비된 얇은 wrapper

Content55e의 ncp/run_exact_once.sh는 위와 같은 인자 한 번을 실행하고 stdout/stderr/command/exit/time을 runner output 밖에 보존한다. 실제 현재 값으로 다음 environment를 결속한다.

| 환경 이름 | 실제 의미 |
|---|---|
| C21J_WORKTREE | detached full fe6 checkout 절대 경로 |
| C21J_CONTROL_DIR | 외부 H/I PUBLISHED controls 디렉터리 |
| C21J_NATIVE_BINARY | 확인된 known SHA native executable 절대 경로 |
| C21J_BRIDGE_BINARY | 현재 호환·SHA 확인한 bridge 절대 경로 |
| C21J_BRIDGE_BUILD_RECEIPT | 원 성공 build receipt 절대 경로 |
| C21J_PYTHON | 새 process를 실행할 실제 Python 절대 경로 |
| C21J_ALLOCATED_CPU | CPU55를 제외한 실제 배정 CPU 하나 |
| C21J_RUN_ROOT | 아직 없는 새 절대 결과 디렉터리 |
| C21J_TIME_BINARY | 선택 사항; 현재 실제 GNU time의 절대 경로 |

Wrapper 파일 자체는 C21J55e에서 읽은 별도 control 위치에서 사용하고 live worktree를55e로 바꾸지 않는다. **bash run_exact_once.sh를 한 번만 호출**한다. Wrapper가 새 RUN_ROOT를 만들고 원 runner가 그 아래 아직 없는 job/을 create-only로 만든다. GNU time binding이 없으면 GNU time/RSS 계측은 없다고 기록한다. Job receipt의 원 timing은 보존한다.

Wrapper는 prelaunch에서 known native SHA와 frozen I runner SHA를 확인한다. 별도 compiler, native probe, suite, ODE, 자동 retry, 다른 mode, FD follow-up을 호출하지 않는다. 그 단순 CPU affinity 확인은 실제 독점 campaign 배정을 대신하지 않는다. Publication/source/native/build/fixture/exact admission은 원 runner가 계속 검증한다. Wrapper log를 원 job/ 안에 뒤늦게 추가해 payload inventory를 바꾸지 않는다.

## 9. runner가 실제 강제하는 제한

| 항목 | 원 구현의 값·동작 |
|---|---|
| 원 source | detached HEADfe6; 같은 H/I repo와 committed runtime/manifest bytes |
| publication | 두 외부 PUBLISHED H/I controls와 source/manifest 대조 |
| common_ic canonical SHA | befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65 |
| fixture 원 JSON SHA | bcfb3d5a8b4d5c8153247712eb1c3d127c4410e2455f6106bf60720642d0f060 |
| 수치 controls | rtol2e-11, fixed-scale atol multiplier2e-14, max-step divisor8 |
| 계산 job deadline | 원 H epoch의300초 하나 |
| count limits | original RHS evaluations 최대200000, native actual calls 최대200000 |
| 개별 native timeout | min(15초, 원 job의 남은 예산) |
| exact cache | cell별 capacity16; full physical t/u binary64 bytes; signed zero 보존 |
| 성공값 처리 | 성공한 RHS만 cache, caller에는 copy, cell마다 reset |
| native provider admission | 원 NativeMicro/BudgetedNativeMicro class·code·binding, owner/build, actual process·streams·protocol |
| 불변 문맥 | fixture/source/context/configuration/deadline과 native count의 단조성 |
| callback live guard | cache hit에도 process/configuration/budget/context 및 metadata/path lease 검사 |
| full-byte SHA 검사 | admission과 terminal에서 수행 |

I exact setup과 guard도 원 H epoch의300초 예산을 소비한다. 계산 시작마다 새300초를 리셋하는 계약이 아니다. Native request timeout도 남은 예산보다 길게 설정하지 않는다. Callback마다 binary 전체 SHA를 다시 읽는 것으로 과장하지 않는다.

Native count가 cap에 도달해도 이미 저장된 성공 exact hit는 허용된다. Actual N+1 miss는 provider가 거부한다. 이 차이를 guard 결함이나 cap 우회로 잘못 분류하지 않는다. Count는 실제 provider 호출과 wrapper/table query를 구분한다.

--wall-s, --max-calls, --rtol, --workers 같은 인자는 이 CLI에 없다. 새 flag를 만들어 적용했다고 기록하지 않는다. Floor/clipping/fastmath/norm/tolerance/state/event 정의를 바꾸지 않는다. Generic purity 선언, replay stub, pending receipt 수정으로 live native admission을 우회하지 않는다. 환경과 runtime identity가 달라진다면 먼저 실제 차이를 기록하고 같은 실험의 단순 재사용으로 취급하지 않는다.

## 10. 결과가 생기면 읽을 순서

먼저 실제 JOB_RECEIPT.json, C21I_PUBLICATION_IDENTITY.json, INPUT_IDENTITY.json, H/I source identity, native owner/binary/process receipt, build receipt, fixture, native/RPC raw, 원 result와 payload hashes를 읽는다. Matching successful terminal이 없으면 성공 exit 문구만으로 COMPLETE를 선언하지 않는다. Partial/timeout/failed raw와 wrapper stdout/stderr/exit를 보존한다. 자동 retry로 앞 실패를 지우지 않는다.

### 실행과 전체 해의 동일성

실제 source content, doc publication evidence, native/bridge/build bytes, fixture/method/variant/optimization/controls와 새 hardware·toolchain·Python/NumPy·resource context를 반환한다. 기존 H/I는 원 native archive를 읽어 비교하며 재계산하지 않는다. 새 source/binary가 다르면 동일 identity 성능 실험으로 표시하지 않는다.

전체28 state, 모든 ledger, endpoint diagnostics와 accepted trace를 비교한다. 일부 endpoint만 같아 전체 equality를 선언하지 않는다. Bitwise 여부와 최대 fixed-scaled 차이, 실제 다른 성분·단위·accepted grid를 구분한다. Independent balance와 pinned L0 비교를 별도 판정한다. Balance closure나 endpoint agreement는 global ODE error bound가 아니다.

### 실제 cache와 native 비용

Original RHS requests/evaluations, hits/misses/evictions, native actual calls, rhs/Jacobian/partial_t RPC, accepted/rejected/LU/fallback, phase timers를 기록한다. 저장 trace의69/754는 비교 기준이며 새 actual counter는 실행 결과에서 읽는다. 같은 경로가 나올 충분조건이 충족됐는지 보고, 다르면 실제 새 요청열·admission·solver trace·환경 차이로 조사한다.

End-to-end process elapsed, job wall, reference wall, segment wall, instrumented RHS/key/hit, native logged interval의 이름과 scope를 그대로 쓴다. 포함관계인 timer를 더하지 않는다. Native interval을 순수 chemistry kernel 시간으로 부르지 않는다. Guard 전용 timer가 없다면 남는 시간을 순수 guard 비용이라고 명명하지 않는다.

H/I의 기존 wall 차이는0.2202378119982313초이며 I/H1.181759699782439다. I original RHS 합은0.581804697초, I native interval 합0.05898441682802513초다. Full-hit69개에 해당하는 native interval 합0.00497811014065519초와 작은 native-key100개의0.007200388237833977초는 별개다. 이 baseline 부분합은 실제 cache-on 절약 시간 측정이 아니다. 한 번의 새 exact job으로 일반적 speedup을 확정하지 않는다.

### 다음 FD 또는 다른 lane은 별도 조건이다

기존 I vectorized FDhalf는 COMPLETE로 재사용한다. Endpoint 최대 절대 차이2.886579864025407e-15, fixed-scaled2.0285682709290226e-15, 온도차−1.8189894035458565e-11K였고 accepted grid는 달랐다. 이 결과를 exact FDhalf가 이미 실행됐다는 증거로 사용하지 않는다.

새 exact base 이후 실제 FD 불확실성이 남을 때만 **matching COMPLETE exact-mode base**를 부모로 별도 exact FDhalf를 검토한다. 기존 vectorized base/FDhalf나 H base를 exact FD parent로 재지정하지 않는다. 이번 packet의 maximum_new_jobs는1이며 FD followup 자동 실행은 없다. G8+조건부4, 다른 H fixture/backend, I 전체 matrix, Schur/JVP production integration을 자동 제출하지 않는다.

## 11. 반환과 게시·백업·DAG

실제 다음 결과를 아래 축으로 각각 반환한다. Artifact/resource 접근이 막힌 상태는 준비 실패의 구체 원인을 적고, 수행하지 않은 native job을 NOT_RUN으로 남긴다. 출판 영수증이나 table replay PASS를 live execution receipt로 바꾸지 않는다.

| 상태 축 | 새 실행 전 상태 | 새 결과에서 필요한 근거 |
|---|---|---|
| 패킷 준비 | PREPARED_CONTRACT_ONLY, 실제 content55e 게시 | 고정 파일·binding·정적 확인 |
| 현재 자원 admission | NOT_OBSERVED | 실제 UTC·scope·allocation·CPU/RAM/cgroup/disk·process context |
| native exact 실행 | NOT_RUN | actual terminal receipt·exit·native/RPC/raw |
| 전체 해·수지 | 기존 scoped 동일성/기존 HOLD | 새 전체 state·ledger·trace·independent balance |
| native exact 성능 | NOT_EVALUATED; 일반 가속 NOT_ESTABLISHED | live guard가 동작한 actual counters/timers와 비교 한계 |
| 과학 전역 상한 | global_error_bound=null | 별도 과학 증명이 없는 한 그대로 유지 |
| 게시 | PR88의 분석/패킷 게시 완료, 최신 head는 외부 영수증 | 새 실행 evidence의 실제 create-only content/doc/PR 관측 |
| 백업 | 기존 DELIVERY/CLOSEOUT은 각 영수증 | 새 raw 묶음의 각 provider ACK·bytes/metadata 검증 수준 |
| DAG | 선택 exact base 준비 | 위 축의 실제 상태로 다음 node를 갱신 |

새 결과는 source/test/raw/receipt identity를 묶어 create-only branch/draft PR과 Drive·Dropbox·Library 백업으로 보존한다. 기존 객체를 덮어쓰거나 PR을 자동 merge하지 않는다. 원 실패·raw·역사 NOT_PUBLISHED와 기존 C21F 게시 완료를 유지한다. 상세 private LIVE_INVENTORY는 비공개 원본으로 보존하고 공개 tree에는 허용된 요약·SHA만 넣는다. 다른 사람에게 메시지를 보내는 행위는 별도 명시적 권한이 없는 한 수행하지 않는다.

C21G reference ladder는 독립 계약이다. 기존 C21I 제조32+FD2/native0과 RHS423→372,74→71의 근거를 재사용하고 전체 시간 가속 NOT_ESTABLISHED를 유지한다. C21J gate9+16+6 PASS 및 네 replay PASS를 전체 physics suite 완료로 확장하지 않는다. Original attempt01, V1 finding, privacy test 기대 교정 실패, 최초 build timeout과 후속 성공을 모두 원 identity로 보존한다.

Full48, 전체 native/MD14 source matrix, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle/full-driver parity의 과학 HOLD는 이 한 행으로 해제되지 않는다. 새 strong no-go나 global error bound를 만들지 않는다.

## 12. 원 권위 문서의 복구 locator

| 파일 | Library ID | File ID | bytes / SHA256 |
|---|---|---|---|
| NCP_C21HI_FINAL_PROMPT_KO_20261020.md | libfile_52d9b40c438081919f2041b780f379a9 | file_000000005ef481fa9a02dc0986387bd0 | 6,654 / 15d3473e2fcda275d5fca846d29c78a1d2eadf4b447713efda4443529acfa6bb |
| C21HI_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json | libfile_67a55a753db4819182ce4e20a2d62598 | file_00000000de1081fa9e70eba0ae026ecf | 24,858 / 688c514c852fc8cd856f169a57bd52b304ea56e37dae2d333c1365909f12812d |
| C21HI_NEXT_THREAD_PROMPT_KO_20261020.md | libfile_c3e5278a11208191ba7b0448d42f1004 | file_0000000094b881faa47407b2c05a1690 | 10,428 / 41d4b1dfec57d025f391143a049fd0a315737d550551fe3d3566dcd0ccc077b1 |
| C21HI_CLOSEOUT_REPORT_KO_20261020.md | libfile_750e99354434819196d8b33944ed15fd | file_00000000b3e081faab718551cfb172cd | 27,992 / 72ee19d6cef8ae200553bfa6c6e7c43a7c1001fef62748abab20965394d7068c |

원 C21HI 구현 ZIP은 BASS_CR_C21HI_OPTIMIZATION_DELIVERY_20261020T073122Z.zip,6,145,502 bytes,SHA2563c30312161d06e85ab42bea38105b9ede26f97303441a47c6ce2aaccc7d0c537,Drive1KlkxM5XII-v11hMCMGnjyEUnRaqKNpb1,Dropbox id:BSpOijBcT10AAAAAAD_SWg,Library libfile_7c60ff7673fc8191b3d7c98b4a33774e,File file_00000000a1348230861aa6214bffd565다.

원 문서 마감 ZIP은 BASS_CR_C21HI_PUBLICATION_CLOSEOUT_20261020T105959Z.zip,2,509,733 bytes,SHA256f2752a31ef99680aa42eabb21bbe5f8d83cc724de41ab3bfa053f9043eaeb9fb,Drive1O7wkkEauhxvbN16U1mkAxhwcIoMfyjol,Dropbox id:BSpOijBcT10AAAAAAD_SZg,Library libfile_cb771a719bf88191ab426e115103e48e,File file_00000000dbc481fab650a9cbaffcc416이다. DELTA_MANIFEST의 base SHA가 일치하는 문서에만 적용한다.

### 실제 원 source 근거

고정 I runner: https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/run_optimized_pilot.py

고정 H runner: https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21h_vigilode_bridge_20261019/run_pilot.py

Native exact guard: https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/native_cache_contract.py

G input/native authority: https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21g_reference_refinement_20261019/campaign_contract.py

현재 자원과 유효 artifact를 확인하고 준비된 한 행을 concrete하게 진행해라. 동일한 새 실행 결과가 이미 있으면 재사용하고, 수행한 실행·검증·게시·백업·DAG를 각각 실제 영수증으로 반환해라.
