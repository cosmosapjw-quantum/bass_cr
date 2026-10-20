# C21J 전체 새 대화 인계문 — 2026-10-20

$physmath-research-loop, SciSpace, Exa, Wolfram을 사용해 cosmosapjw-quantum/bass_cr 연구를 이 상태에서 이어가줘. 이 문서는 실제 전체 인계문이다. 먼저 이 문서와 최종 외부 권위 영수증 C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json을 전부 읽고, 아래 고정 연구 보고서·NCP 패킷·원 native 반환을 연결해라. 옛 scratch checkout, Rust compiler, bridge 또는 native executable이 현재 있다고 가정하지 마라. 파일은 현재 저장처에서 ID·파일명을 확인해 복구하고, 프로그램은 GitHub의 고정 content에서 읽을 수 있다.

**현재 연구 결론:** C21I 구현·기존 제조 검증은 완료 상태다. 그 뒤 PR87에서 실제 H base, I vectorized base, I vectorized FDhalf 세 native 실행이 반환됐다. C21J는 이 실제 raw를 재사용해 전체 RHS 요청열과 exact cache 기회를 복원하고, 원 callback을 저장된 native 응답표에 연결한 네 경우를 실제로 재생했다. 세 저장 trace 각각 full-key LRU16의 hit는 69, miss는 754이며 네 callback replay는 PASS_SCOPED다. **실제 native exact 실행은 아직 NOT_RUN, 그 성능은 NOT_EVALUATED다.** 다음 준비된 NCP 행은 common_ic / vigilode-rodas5p / vectorized_exact / base 하나다. global_error_bound=null과 기존 과학 HOLD를 유지한다.

## 1. 먼저 읽을 실제 권위와 현재 상태를 판정하는 순서

1. 현재 관련 dossier에서 **C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json**을 찾고 전체를 읽어라. 최종 D2 document head, 최종 PR/ref 관측 시각·상태, DELIVERY ZIP 및 PUBLICATION_CLOSEOUT ZIP의 실제 ID·SHA256·provider ACK·검증 수준은 이 외부 영수증의 값으로 판정한다. 저장처에 ROOT_DELIVERY_METADATA.json이 있으면 그 실제 값도 대조한다. 이 본문에 자기 자신의 commit이나 자기 자신을 포함하는 ZIP의 SHA를 억지로 넣지 않았다.
2. GitHub의 PR88 및 branch를 실제로 다시 읽고 영수증 이후 변경을 구분한다. 문서 commit을 native 실행 source로 사용하지 않는다. Source/test/raw 변경이 없다면 기존 실행·focused 검증을 재사용한다.
3. C21J 고정 content 55e6569a8f816e13babe4165f0fef3655f7299a3 아래 research/cr_c21j_native_trace_replay_20261020/의 **C21J_RESEARCH_REPORT_KO.md**, **theory/NATIVE_TRACE_EXACT_CACHE_NOTE_KO.md**, **INPUT_PINS.json**, **evidence/analysis_attempt_02/ANALYSIS.json**, **evidence/replay_attempt_02/REPLAY_REPORT.json**을 읽는다. 현재 README·DAG·게시 기록은 D1 이후의 문서 상태도 함께 읽는다.
4. NCP로 이어갈 때는 이 인계와 함께 **NCP_C21J_FINAL_PROMPT_KO_20261020.md**, 고정 단위의 **ncp/NCP_C21J_EXACT_PILOT_KO.md**, **ncp/PILOT_CONTRACT.json**, **ncp/run_exact_once.sh**를 읽는다. D1의 **ncp/PUBLICATION_BINDING.json**이 packet content 55e와 실제 실행 source fe6을 분리해 결속한다.
5. 이전 C21HI 전체 인계문·마감 보고서·권위 영수증은 아래 복구 표에서 읽는다. 이전 원문과 원 실패·성공 raw의 역사적 상태를 덮어쓰지 않는다.

고정 보고서: https://github.com/cosmosapjw-quantum/bass_cr/blob/55e6569a8f816e13babe4165f0fef3655f7299a3/research/cr_c21j_native_trace_replay_20261020/C21J_RESEARCH_REPORT_KO.md

고정 이론: https://github.com/cosmosapjw-quantum/bass_cr/blob/55e6569a8f816e13babe4165f0fef3655f7299a3/research/cr_c21j_native_trace_replay_20261020/theory/NATIVE_TRACE_EXACT_CACHE_NOTE_KO.md

## 2. 실행 content, 게시 문서 head, 실제 DAG

| 단위·역할 | 고정 content 또는 실제 실행 source | 별도로 보존할 문서 head·게시 |
|---|---|---|
| C21H 실행 | 40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8 | 0ec4c55102766c40c554ffc6141eb08fba741c79 / draft PR85 |
| C21I 실행 | fe6bbaec2de5032b938aed0713623b9618ba70e6 | 26ab505dac2bfcb0cfd3d049f22bc408f4c86241 / draft PR86 |
| PR87 실제 native 반환 | 첫 evidence content 0f2d195aee3c08b372d020bcd6caba87db64a83c; 실행 source는 위 fe6 | d3eaf596e46be4f994723fb742237a7399c290ed / draft PR87 |
| C21J 새 진단·이론·검증·NCP 패킷 | 55e6569a8f816e13babe4165f0fef3655f7299a3 | draft PR88, branch research/cr-c21j-native-trace-replay-20261020 |
| C21J D1 문서 | 위 content에 대한 문서 변경 | e04b19669b1542b4537448c764d1dc02ebc8b7b6 |
| C21J 최종 D2 문서 | 이 전체 인계·DELIVERY 복구 정보 등 | 최종 외부 권위 영수증의 실제 document head를 읽을 것 |

H content는 I content의 **실제 부모**다. PR87은 I 게시 이후의 반환 evidence를 추가했고 원 H/I 과학 source를 바꾸지 않았다. C21J content의 실제 부모는 PR87 head d3eaf596e46be4f994723fb742237a7399c290ed다. C21J packet의 게시 source와 NCP가 실행할 C21I source는 서로 역할이 다르다.

C21J content 게시 관측은 2026-10-20 17:28:02 UTC였고 PR88은 open/draft/미병합이었다. 실제 Git Data API provider ACK 및 metadata로 원 78개 payload의 경로·mode·bytes·Git blob SHA와 ref를 대조했다. 원 payload는 1,441,337 bytes이며 content manifest SHA256은 df59a03ad0ee85b0216c0c123c9709db083e6b87eb3cce8e616de771784eb8c1이다. 이 검증 수준을 shell ls-remote나 모든 provider의 원바이트 재다운로드라고 표현하지 않는다.

D1까지 PR88은 두 commit, 단위 안 총 88 files다. 원 78개 중 README·DAG만 문서로 갱신하고 부가 문서 10개를 추가했다. DELTA_MANIFEST_D1.json은 수정 대상의 base SHA와 새 SHA를 별도로 묶는다. **base SHA가 맞는 문서에만 delta를 적용하고, 추가 파일은 없는 곳에 create-only로 만든다. 원 H/I source/test/native raw나 역사 영수증을 재적용하지 않는다.** 최종 D2의 변경 범위도 실제 최종 영수증과 delta manifest에서 확인한다. PR을 자동 merge하거나 force push하지 않는다.

## 3. 이번 DELIVERY 및 최종 마감 파일의 복구

### 3.1 D1 상태의 전체 연구 DELIVERY ZIP

| 항목 | 실제 값 |
|---|---|
| 파일명 | BASS_CR_C21J_RESEARCH_DELIVERY_20261020T173607Z.zip |
| bytes | 3495267 |
| 전체 members / payload members | 135 / 134 |
| SHA256 | b3f867d40f2f760e5f61168a1bec858d2c9a1dba646e7b56d015c569283a1ae8 |
| Drive ID | 1VUN3oQO_U3VHB3n7PDcdmudhsKwt5QPj |
| Dropbox ID / rev | id:BSpOijBcT10AAAAAAD_aDQ / 65e4ba52c16ad0af03d47 |
| Library ID | libfile_7f604c8e9d1081919c828e9a8fc97cd4 |
| File ID | file_000000005a88820ba56ff654e3927b65 |

이 DELIVERY는 D1 시점의 C21J 단위, replay에 필요한 고정 source 24개, 원 native 반환 archive, 복구·권위 자료를 묶는다. 실제 member 경로와 각각의 SHA는 ZIP manifest 및 동반 영수증을 따른다. **이 D2 인계문은 그보다 나중에 작성·게시되므로 위 DELIVERY ZIP 안에 있다고 주장하지 않는다.**

ZIP은 새 위치에 복구하고 전체 압축 bytes SHA, manifest, 필요한 payload SHA를 확인한다. 원 archive가 이미 일치하는 bytes로 복구돼 있으면 같은 archive를 다시 다운로드하거나 기존 과학 suite를 반복할 이유가 없다. 검증 수준은 각 저장처 ACK·metadata·실제 byte readback을 구분해 최종 외부 영수증에서 읽는다. Create-only 백업을 유지하고 기존 객체를 덮어쓰지 않는다.

### 3.2 D2 이후 작은 PUBLICATION_CLOSEOUT ZIP과 최종 권위 영수증

최종 마감 ZIP의 파일명 locator는 **BASS_CR_C21J_PUBLICATION_CLOSEOUT_20261020T*.zip**이다. 이 ZIP은 D2의 문서 delta와 실제 D2 게시 관측을 보존한다. 실제 파일명·bytes·SHA·세 저장처 ID는 **C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json**을 읽어서 얻는다.

순서는 content55e → D1 → 전체 DELIVERY 및 세 provider ACK → D2 전체 인계 → 작은 PUBLICATION_CLOSEOUT 및 세 provider ACK → 최종 외부 권위 영수증이다. D2 본문이 자기 head나 자기 자신을 포함하는 closeout ZIP의 SHA/ID를 사전에 아는 순환 구조를 만들지 않는다. Archive-time PENDING, 하위 agent의 마감 전 PENDING, 현재 완료 상태는 각각 기록된 시점에 속한다. 최종 완료 판정은 나중 영수증의 실제 관측으로 연결한다.

주요 dossier 범위는 Drive folder 1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy와 Library/Dropbox의 /BASS_DERIVATION_DOSSIERS_20260912/bass_cr이다. 이름 검색 후 실제 ID·SHA를 대조한다.

## 4. 원 native 반환 archive와 실행 파일 복구

### 4.1 원 archive — 이번 C21J의 실제 입력

| 항목 | 확정 값 |
|---|---|
| 파일 | C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz |
| bytes | 2,568,680 |
| SHA256 | 2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3 |
| tar 구성 | 184 members, 156 regular files, 155 payload entries; manifest 자기 항목 제외 |
| Drive ID | 1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u |
| Dropbox ID / rev | id:BSpOijBcT10AAAAAAD_T4A / 65e43db2185370af03d47 |
| Library ID | libfile_b26c9616e4748191ba98b19b1bea5d04 |
| File ID | file_00000000c0cc820b982a789de34a62ed |
| 압축 내부 root | C21GHI_NATIVE_EXECUTION_20261020/ |
| payload manifest | PACKAGE_PAYLOAD_SHA256SUMS.txt; 20,712 bytes |
| payload manifest SHA256 | 40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a |

초기 intake에서 Drive의 원 압축 bytes 전체 SHA와 payload 155개를 실제로 확인했다. 원 반환은 이후 Library에도 실제 보존됐고 scratch 상실 뒤 같은 원 bytes로 복원됐다. Dropbox의 metadata 확인을 원 bytes 재다운로드 검증으로 확대하지 않는다.

이 archive에는 세 job의 native JSONL, RPC stream, 실제 FD nodes, 원 result/receipt, build 실패·성공 기록, H/I publication controls와 성공 bridge가 있다. **native executable 자체는 없다.** 세 개의 private LIVE_INVENTORY process/context 원문도 들어 있다. 그 원문은 비공개 원본 보존에 포함되고 공개 Git tree에는 복사하지 않는다. C21J 진단은 이 세 항목을 읽기 전에 거부한다. 공개 문헌 ledger와 제3자 원전도 별도 취급한다.

### 4.2 bridge 및 native identity

| 역할 | 실제 고정 identity |
|---|---|
| archive bridge | binary/bass-cr-c21h-rust-bridge; 4,888,736 bytes |
| bridge SHA256 | 717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30 |
| 성공 build receipt | build_success/BUILD_RECEIPT.json |
| build receipt SHA256 | c846c35621dd9a0aa3c5bbfb90e94da0f022e934cf2ea1342270d61eda4b5190 |
| H control SHA256 | control/H_PUBLICATION.json; 57b81b524b83d7c05f82394b0fba1d4d57d99ed051b92d673fd9c081d702aed4 |
| I control SHA256 | control/I_PUBLICATION.json; 28641242b36a8392e296fa7801212908296b9fd5fcf035574483e2399d2a2af2 |
| native owner | cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4 |
| 선택 exact 행의 known native | 5,003,448 bytes |
| known native SHA256 | 1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40 |

현재 host의 loader·공유 library·권한과 binary bytes가 맞으면 bridge는 Rust를 새로 설치하지 않고 재사용할 수 있다. Receipt 내부의 과거 build 경로를 현재 경로로 편집하지 말고 실제 현재 binary 경로를 CLI에 별도로 준다. Known native의 과거 /root/C21F_NATIVE_RUN_20261018T1358Z/build/native_point는 탐색 locator이며 현재 존재를 뜻하지 않는다. 없으면 실제 PR82 binary/build artifact와 영수증을 찾아 복원한다. 확인하지 않은 artifact ID를 만들지 않는다. 선택된 한 행은 다른 SHA의 새 native build를 자동 admit하지 않는다.

## 5. 고정 source 24개와 scratch 상실 뒤의 재개

원 C21J INPUT_PINS.json은 정확한 bytes SHA256 **ac339fc832ccc2e4b177034151a6adcf1510d82646b0c7e04d68bfc2be7aea90**, canonical SHA256 **5c741dcaf415961d09bb4f1bf10c9dad600c0af3d0791e18750655b006957fea**로 고정됐다. source_files 24개는 fe6 content에, return_files 60개는 d3 반환과 원 archive에 연결된다. 임의로 새 pin map을 공급해 입력 권위를 바꾸는 경로는 허용하지 않는다.

DELIVERY의 source closure를 빈 tree의 원 상대 경로에 그대로 복원하거나 GitHub fe6의 정확한 content를 읽어 같은 경로에 materialize한다. 개별 bytes·SHA를 INPUT_PINS와 대조하고 LF를 덧붙이거나 serializer로 다시 써서 원본 identity를 바꾸지 않는다. 단위 자체도 content55e의 bytes 또는 D1의 명시적 문서 delta로 복구한다. 고정 source 24개는 **오프라인 callback replay의 closure**다. NCP live runner는 더 넓은 F/G/H/I runtime·manifest와 G baseline 여섯 파일이 필요하므로 full fe6 detached checkout을 사용한다.

현재 C21J 진단 source의 고정 값은 다음과 같다.

| 파일 | bytes | SHA256 |
|---|---:|---|
| replay_callbacks.py | 20,173 | 7c855b9983c575042a18754687696a039bef31f5711c455f774b70c03bae52c1 |
| analyze_native_trace.py | 30,150 | e2d8fff3acf4a867391de7247781d2ffe6d3a93ed0ba5c78b26876b911c00b9c |

분석·replay에는 Rust가 필요 없다. 실제 replay 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0이었다. 현재 실행 환경은 별도로 관측해야 한다. 2026-10-20 이 대화 중 scratch가 상실됐고, root는 보존된 원 78 payload의 full bytes와 index로 정확히 복구했다. 모든 SHA256·Git blob identity를 확인했으며 **그 복구 때문에 analysis, focused tests, IVP, native를 새로 돌리지 않았다.** SCRATCH_RECOVERY_RECEIPT.json과 AUTHORITY_RECOVERY_RECEIPT.json이 그 범위를 기록한다. 과거 scratch의 compiler 부재나 존재를 현재 환경에 이식하지 않는다.

입력 또는 진단의 변경된 의존성이 생긴 경우에만 README의 create-only analyzer/replay 명령과 관련 focused gate를 실행한다. 같은 bytes를 복구했다는 이유만으로 옛 전체 suite를 반복하지 않는다.

## 6. C21I에서 이미 완료된 구현과 기존 제조 근거

C21I에는 vectorized reduced Jacobian과 preallocation, full physical (t,u) binary64 key의 cell LRU16 exact cache, source/class/process/configuration/binary/deadline/cap purity 계약, 게시 receipt와 detached content 검증, mode에 맞는 FD parent guard가 구현돼 있다. 기본 mode는 vectorized이고 vectorized_exact는 명시적으로 선택한다. 이것을 새 미구현 기능으로 되돌리지 않는다.

이전 실제 제조 32 jobs + FD2 jobs의 native chemistry 호출은 0이었다. Y=0, M=9, dx=1e-7, full28/integrated26 제조 입력에서 exact는 VigilODE RHS 423→372, Diffsol 74→71로 줄였다. 일관된 end-to-end 전체 시간 가속은 NOT_ESTABLISHED다. Kernel warm 수치 4.82–11.19배는 native trajectory speedup이 아니다.

독립 Rust Schur/JVP prototype과 제조 검증은 완료돼 있으나 H production backend에 통합된 상태로 표시하지 않는다. 큰 Schur/backend 통합이나 새 기능의 설계·구현을 NCP에 처음부터 떠넘기지 않는다. 실제 추가 코드가 필요해지면 여기서 구현·변경 의존성의 focused 검증·push를 마친 뒤 작고 구체적인 bounded 실행만 전달한다.

C21F 게시 완료 상태, C21G PR84의 독립 reference 계약, 원 실패·raw·역사 NOT_PUBLISHED를 유지한다. H/I 세 native 반환은 C21G의 G8 + 조건부4를 완료한 증거가 아니다. 다른 backend·fixture·source matrix와 full native 연구 완료로 확장하지 않는다.

## 7. 새로 수신한 PR87의 실제 native 실행 — 재실행하지 말고 사용

선택 fixture는 common_ic이며 FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT다. Source 표기는 PINNED_PR79_MD14_RATE_MANUFACTURED_3_ENERGY_GAS이고 nonphoto chemistry는 실제 Rust native provider가 계산했다. Y=0.08130135170951498, M=9, dx=1e-4, full/integrated state=28, rtol=2e-11, alpha=2e-14, max-step divisor=8이다. 이 fixture를 완전한 실제 MD14/source12-cell matrix나 관측 checkpoint로 재분류하지 않는다.

Canonical fixture SHA256은 befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65이고 원 fixture JSON bytes SHA256은 bcfb3d5a8b4d5c8153247712eb1c3d127c4410e2455f6106bf60720642d0f060이다.

| 반환된 실제 job | native calls | job wall (s) | 상태 |
|---|---:|---:|---|
| H common_ic / vigilode-rodas5p / base | 823 | 1.2116977100085933 | COMPLETE |
| I common_ic / vigilode-rodas5p / vectorized / base | 823 | 1.4319355220068246 | COMPLETE |
| I common_ic / vigilode-rodas5p / vectorized / fd_half | 823 | 1.434721386001911 | COMPLETE |

각 job은 runner/native exit0, native 응답 823개 모두 OK, accepted36/rejected16, LU52, RPC rhs400/jac36/partial_t36이다. 기존 합계 **2,469 native calls**를 C21J의 새 실행으로 세지 않는다. 반환된 I는 **cache_capacity=0의 vectorized mode**였으므로 exact live 성능의 영수증이 아니다.

NCP의 첫 bridge compile은 timeout300s/exit124로 끝났고, 다음 locked Rust1.94.1 compile은 약7분01초 뒤 성공했다. 첫 timeout이 source 불일치나 compile 오류를 입증한 것은 아니다. 그 반환에는 추가 source 호환 patch가 필요하지 않았다. 성공 build만 남기고 실패 raw를 지우지 않는다. 과거 CPU62는 역사적 실행 자원이며 현재 배정으로 사용하지 않는다. CPU55는 보호한다.

## 8. C21J가 실제로 새로 계산한 것

### 8.1 원 요청열과 full key

각 RPC rhs 요청 외에 Jacobian의 base·양쪽 gas FD nodes와 partial_t의 base·time nodes를 원 연산 순서로 복원했다. Jacobian 36개는 base1 + gas4개 양쪽8회, partial_t36개 중 cell 경계의 flat branch3개는 RHS0회, 나머지33개는 base+time2회다.

**823 = 400 + 36 × (1 + 2 × 4) + (36 − 3) × 3.**

Gas node offset 288개와 실제 time nodes를 저장된 값과 고정 source에서 독립적으로 대조했다. 복원된 각각의 요청에 원 clamp·exp·density·.17e 직렬화를 적용한 native EVAL 문자열 823개가 actual raw와 모두 맞았다.

Full key는 cell에 묶인 **clamp 이전 t의 bits + 전체 physical u의 little-endian binary64 bytes**다. 모든 tau·gas·ledger와 signed zero를 보존한다. Fixture/source/cell/scales/provider 불변 문맥이 함께 고정된다.

| cell | 원 RHS requests | full-key LRU16 hits | misses | 작은 native-key hits |
|---|---:|---:|---:|---:|
| 0 | 272 | 23 | 249 | 36 |
| 1 | 279 | 23 | 256 | 28 |
| 2 | 272 | 23 | 249 | 36 |
| 합계 | 823 | **69** | **754** | **100** |

세 저장 job에서 각각 이 계수다. Cell별 23 hits는 rhs12 + partial_t base11이며 gas/time probe hit는0이다. 재사용률 69/823=8.3839611179%는 이 유한 요청열의 결과다.

7-input native key의 100 hits를 full RHS cache의 100 hits로 바꾸면 안 된다. 추가31쌍은 tau만 다른4쌍, tau와 passive ledger가 함께 다른27쌍이다. Native chemistry 입력은 tau를 포함하지 않아도 전체 optical RHS와 광자 의존 장부의 도함수는 tau에 의존한다. Passive ledger의 값 자체를 RHS의 인과 입력이라고 잘못 설명하지 않는다. 현재 full key는 ledger 값도 보수적으로 포함한다. 이 분석이 작은 key로 full RHS를 재사용하는 새 기능을 구현했다는 뜻은 아니다.

### 8.2 실제 네 callback replay

| 저장 입력 | 실제 계산한 callback | 비교 reply / binary64 값 | 저장 응답표 queries | 판정 |
|---|---|---:|---:|---|
| I vectorized base | 원 H | 472 / 40,432 | 823 | PASS_SCOPED |
| I vectorized base | I vectorized | 472 / 40,432 | 823 | PASS_SCOPED |
| I vectorized base | I vectorized_exact | 472 / 40,432 | 754 | PASS_SCOPED |
| I vectorized fd_half | I vectorized_exact | 472 / 40,432 | 754 | PASS_SCOPED |

원 RHS 및 callback 함수가 실제로 계산했고 native 부분만 일치하는 저장 응답표로 제공했다. 원 rhs/Jacobian/partial_t reply를 정답으로 그대로 반환한 방식이 아니다. Native 응답 중복 conflict0, job당 unique native request723이다. 필요한 key가 없거나 응답이 충돌하면 실패한다. 보간, approximate key, native fallback, 새 forward ODE로 빈칸을 채우지 않는다.

**754는 이 replay의 table query 수다. 새 live native 호출 수가 아니다.** Accepted states는 저장 trace에서 소비해 물리 summary를 재구성했으며 새 solver로 다시 적분하지 않았다. Wire envelope와 수치 shape·bits를 검증했지만 JSON 공백까지 byte-identical serialization이라고 주장하지 않는다. C21J의 새 native process/chemistry 실행0, 새 IVP integration0, 옛 제조/suite 재실행0이다.

H base와 I vectorized base의 전체28 endpoint, 모든 ledger와 endpoint diagnostic, 세 raw segment result 객체, accepted physical records39개가 bitwise 같았다. 39개에는 각 cell 시작점3개가 포함된다. 이 동일성은 해당 저장 결과에 대해 확보했다.

### 8.3 현재 gate와 실패 이력

현재 유효 결과는 analysis_attempt_02와 replay_attempt_02다. 최초 attempt01의 PASS도 그 입력과 source 버전의 기록으로 보존한다. 독립 review V1의 finding은 reusable gate 계약에 관한 것이었다. Arbitrary pin map의 권위 재정의(C9-J1), terminal 없는/실패 RPC 수용(C9-J2), 자체 선언 raw identity만 믿는 analyzer admission(C9-J3)을 보완했다. V2에서 세 finding이 CLOSED다.

Trace 복원 계약9 tests, replay admission16 tests, archive admission6 tests는 각각 실제 PASS다. Changed gate가 들어간 analysis/replay attempt02도 exit0/PASS다. 이를 새 전체 physics suite라고 부르지 않는다. 최초 privacy test가 LIVE_INVENTORY가 하나라고 가정한 실패는 실제 세 항목 모두를 사전에 거절하는지 검사하도록 테스트 기대를 수정했다. 이 원 test-development 실패와 V1 raw를 보존하고 성공 이력으로 덮어쓰지 않는다.

Analyzer는 고정 payload manifest SHA와 읽는 모든 raw 파일 SHA를 대조한다. Replay는 INPUT_PINS의 정확한 bytes와 canonical identity, source24/return60의 완전한 고정 집합 및 hello/config/request/reply/terminal/EOF 성공 stream을 확인한다. 원 성공 trace의 일부분을 완전한 실행처럼 admit하지 않는다.

## 9. 성능, FD 및 이론에서 확보한 범위

### 시간은 포함 범위를 유지해 읽는다

| 기록된 범위 | H base (s) | I vectorized base (s) |
|---|---:|---:|
| job receipt wall | 1.2116977100085933 | 1.4319355220068246 |
| instrumented original RHS 합 | 미계측 | 0.581804697 |
| native request logged interval 합 | 0.05604552090517245 | 0.05898441682802513 |
| full-key69 hit 인덱스의 native interval 합 | 0.004690387926530093 | 0.00497811014065519 |
| 작은 native-key100 hit 인덱스의 native interval 합 | 0.006793982960516587 | 0.007200388237833977 |

이 한 sequential pair의 I/H job wall 비는 1.181759699782439이며 I가 약18.176% 길었다. 반복·환경 통제를 갖춘 일반적 성능 결론은 아니다. Native log interval은 request write/flush + response wait/read이며 뒤의 parse/validation/log flush와 Python optical RHS를 포함하지 않는다. 순수 chemistry kernel 시간으로 부르지 않고 중첩 timer를 서로 독립인 비용처럼 더하지 않는다.

기존 C21I 비용식을 재사용해, 같은 수치 trace에서 hit j의 제거 가능한 전체 원 RHS 비용을 C_j, 추가 cache 비용을 C_cache, 다른 단계·환경의 차이를 ΔT_other로 놓으면:

T_exact = T_I − Σ_hit C_j + C_cache + ΔT_other.

이 한 H 기록보다 빨라질 조건은 Σ_hit C_j > 0.2202378119982313 s + C_cache + ΔT_other다. Cache·기타 차이를0으로 둔 단순 조건에서도 69 hit의 평균 전체 RHS 비용은3.19185235ms를 넘어야 한다. 전체823 RHS 평균0.706931588ms의4.515080배이며, hit 집합이 전체 RHS 시간의37.854251%를 넘어야 한다는 조건이다. Per-request 전체 RHS timer가 없어 실제 절약량을 추정하지 못한다. I의69개 native interval4.978ms는 I wall의 약0.347649%이고, 100-key7.200ms와 별개다. 이 숫자로 exact 불가능이나 strong no-go를 주장하지 않는다.

### FD와 전역 오차

기존 I vectorized base와 FDhalf의 최대 endpoint 절대 차이는2.886579864025407e-15(thermal), 최대 fixed-scaled 차이는2.0285682709290226e-15, 온도 차이는−1.8189894035458565e-11 K였다. Accepted grid는 달랐다. 이 한 FD 민감도와 callback equality는 전역 trajectory 오차 상한이 아니다. **global_error_bound=null**을 유지한다.

### 이론·문헌·CAS 루프

새 이론은 finite LRU reuse-distance 불변식, full-hit가 같은 baseline의 native-key hit에 포함되는 조건, 광학깊이를 바꾼 구체적 투영 반례, 완전 callback 재현 조건, 조건부 adaptive 동일성, 새69-hit 비용 조건이다. 이전 일반 Schur/cache 유도는 반복하지 않았다.

Adaptive 경로 동일성은 같은 IVP/source·FP 연산·native 응답·초기 solver state와 deterministic solver, 전체 callback reply의 bitwise equality, 한쪽에만 작동하는 deadline/process 실패가 없다는 조건 아래 귀납적으로 말할 수 있다. 이번 table replay는 실제 native process의 liveness·file lease·deadline·binary guard를 다시 수행한 증거가 아니다. 이 조건을 제거한 미래 경로나 live 성능을 주장하지 않는다.

SciSpace로 Pope의 원 ISAT 논문을 식별했고 Exa로 원저자 Cornell PDF와 Python3.12 공식 functools 문서를 실제로 읽었다. ISAT의 가까운 조성에서 국소 근사·오차 통제를 쓰는 retrieval과 여기의 literal full-key exact memoization을 필요한 범위에서 구분했다. 그 논문의 speedup이나 error bound를 이 시스템에 가져오지 않았다.

- 원전: https://tcg.mae.cornell.edu/pubs/Pope_CTM_97.pdf
- DOI: https://doi.org/10.1080/713665229
- 공식 문서: https://docs.python.org/3.12/library/functools.html

Wolfram 자연어 context 후 evaluator3회로 새 광자 항등식·부호 refinement·단위·69-hit exact-rational 산술을 검산했다. 첫 부호 simplification이 True로 닫히지 않은 결과와 후속 Reduce/δ=ln2 검산을 함께 보존했다. 새 strong no-go는 채택하지 않았다. theory/R_LOOP_STATUS.json, SOURCE_IDENTITY.json, LITERATURE_LEDGER.json, 허용된 우리 수식·CAS raw를 재사용한다. 제3자 PDF 전체나 논문 abstract 대량 raw는 공개 Git/제공 ZIP에 포함하지 않는다. 원 NCP 과학 raw를 보존하는 의무와 제3자 원문을 재배포하는 행위는 별개다.

## 10. 재개 전에 새 결과부터 확인 — 실제 마지막 관측의 한계

마지막 게시 전 외부 refresh는 **2026-10-20 17:22:11–17:22:46 UTC**, cutoff13:50 UTC를 사용한 metadata-only 확인이었다. Library의 관련 dossier 직접 modified filter는0개이고 next_cursor=null이었다. 별도의 첫20개 unfiltered positive-control page는 전체 inventory 완료로 세지 않았다. Drive 관련 folder 직접57개 응답은 최신11:23:04였고 tool에 continuation field가 없었다. Dropbox 관련 dossier 직접25개는 has_more=false, 최신11:23:12였다. 해당 범위의 새 candidate0, 새 archive 다운로드0이었다.

이 결과는 계정 전체, 모든 하위 folder, NCP disk 전체, 다른 대화 전체의 결과 부재를 뜻하지 않는다. Personal Context 실제 조회는 “SERVICE_ERROR: Personal context is unavailable for this conversation.”으로 실패했다. 이를 다른 대화에 관련 결과가 없다는 증거로 바꾸지 않는다. GitHub의 마지막 관련 branch/PR 조회 범위·결과는 publication/GITHUB_FINAL_DELTA_REFRESH_PUBLIC.json과 최종 외부 영수증에서 읽는다.

다음 대화에서는 그 관측 이후 관련 branch/repo/dossier/다른 대화에 더 새 결과가 있는지 좁은 범위부터 다시 확인한다. 동일 source·fixture·binary·method·mode·controls·terminal raw가 확인되면 재사용한다. 실제 matching job이 진행 중이면 중복 제출하지 않는다. 새로운 source 변경이 있으면 문서 변경과 분리하고 변경된 의존성만 검증한다.

## 11. 남은 NCP 작업 — 준비된 exact base 한 행

준비된 계약은 common_ic / vigilode-rodas5p / vectorized_exact / base, 최대 새 job1, worker1, 자동 retry0, 자동 FD follow-up0, 자동 G campaign0이다. 실제 NCP resources·경로·current binary는 이번 C21J에서 **NOT_OBSERVED**다. 실행자는 현재 접근 가능한 자원을 실제로 읽고 CPU55를 제외한 배정 CPU 하나, RAM/cgroup/disk와 기존 process/watcher/checkpoint를 확인한다. Affinity는 독점 배정 증거가 아니다.

실행 source는 detached full repo **fe6bbaec2de5032b938aed0713623b9618ba70e6**이며 H/I의 외부 PUBLISHED controls는 checkout 밖에 둔다. C21J55e는 분석·패킷의 source다. H/I runner나 원 pending receipt를 바꿔 admission을 통과시키지 않는다. G의 baseline 검사 때문에 common_ic와 native_source의 fixture.json/radau.json/SUMMARY.json, 총6개가 필요하다. Replay용24-file closure만으로 native 전체 checkout을 대신하지 않는다.

유효 bridge가 있으면 성공 receipt와 SHA·host 호환성을 확인해 재사용한다. 필요할 때만 고정 helper의 locked build를 별도 compile budget으로 수행한다. Known native SHA가 없으면 원 artifact 복구를 먼저 한다. 선택 행에 임의의 새로운 native build를 섞지 않는다. 구체적인 추가 호환 수정이 실제로 필요해지면 여기서 구현·focused 검증·push 후 NCP로 전달한다.

원 runner의300s deadline, RHS/native 각200000 cap, 요청 timeout=min(15s, 남은 원 예산)을 유지한다. Exact setup/guard도 같은 H deadline을 소비한다. Callback hit에도 live guard가 있고 admission/terminal에는 full SHA가 있다. 모든 callback마다 binary 전체 hash를 다시 읽는다고 설명하지 않는다. Calls가 cap에 도달해도 이미 성공한 exact hit는 가능하며 N+1 miss는 provider가 거부한다. 원 tolerance·norm·floor·clipping·fastmath·event·state 정의를 바꾸지 않는다.

실행 명령과 실제 environment binding은 **NCP_C21J_FINAL_PROMPT_KO_20261020.md** 및 고정 ncp/run_exact_once.sh에 있다. Shell wrapper는 stdout/stderr/exit/time을 runner job/ 밖에 create-only로 보존하고 한 번만 호출한다. Runtime source/native/build/fixture/control identity, terminal receipt, 전체 state·ledger·accepted trace·independent balance·cache/native/RPC counters를 반환한다. 69/754는 저장 trace에 대한 결과이므로 새 live counter와 별도로 비교한다.

후속 FD는 새로운 불확실성이 실제로 남을 때 matching COMPLETE **exact-mode base**를 부모로 별도로 검토한다. 기존 I vectorized base/FDhalf나 H base를 exact FD parent로 재지정하지 않는다. G8+조건부4, 다른 fixture/backend/source matrix, Schur production integration을 자동 실행하지 않는다.

## 12. 상태 축과 재사용 원칙

| 축 | 이 인계에서 유지할 실제 상태 |
|---|---|
| C21I 이론·구현·focused·제조 | 완료, 기존 증거 재사용 |
| PR87 actual native | H base/I vectorized base/I vectorized FDhalf COMPLETE; 기존2469 calls |
| C21J finite-trace 계산·네 replay | 완료/PASS_SCOPED; 새 native0·새 IVP0 |
| C21J focused gate | 9 +16 +6의 각 scoped PASS; V2 finding3개 CLOSED |
| actual native exact | NOT_RUN |
| actual native exact 성능 | NOT_EVALUATED; 일반 가속 NOT_ESTABLISHED |
| 과학 | 기존 HOLD; global_error_bound=null |
| 게시 | PR88 content55e와 D1 확정; 최종 D2 head/PR 상태는 외부 권위 영수증의 실제 관측 |
| 백업 | DELIVERY와 최종 CLOSEOUT의 provider별 ACK·bytes/metadata 검증을 외부 영수증에서 각각 읽음 |
| DAG | I 고정 source + PR87 원 native raw → C21J 요청열·LRU·callback replay 완료 → NCP exact base 준비 |

R1–R10은 새 finite-trace 단위의 실제 유도·문헌·검산·판정으로 완료된 근거를 재사용하고, C1–C10은 이번 코드·focused gate·실제 게시 영수증과 연결한다. 문서/백업 마감이 남았던 시점의 하위 PENDING을 현재 연구 미구현으로 되돌리지 않는다. 새 의존성이 바뀌지 않으면 determinant/Schur 유도, 옛 chemistry suite, 제조 matrix를 다시 수행하지 않는다.

과학 HOLD는 Full48, 전체 native/MD14 source matrix, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle/full-driver parity에 유지된다. 수지 일치·FD 민감도·bitwise callback equality·실행 성공·성능·게시·백업을 서로 독립으로 기록한다. 원 실패/raw/역사 NOT_PUBLISHED, C21F 기존 게시, C21G 독립 계약, 보호 CPU55, create-only 백업을 보존한다.

## 13. 이전 C21HI 권위 자료의 정확한 locator

| 문서 | Library ID | File ID | bytes / SHA256 |
|---|---|---|---|
| C21HI_NEXT_THREAD_PROMPT_KO_20261020.md | libfile_c3e5278a11208191ba7b0448d42f1004 | file_0000000094b881faa47407b2c05a1690 | 10,428 / 41d4b1dfec57d025f391143a049fd0a315737d550551fe3d3566dcd0ccc077b1 |
| C21HI_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json | libfile_67a55a753db4819182ce4e20a2d62598 | file_00000000de1081fa9e70eba0ae026ecf | 24,858 / 688c514c852fc8cd856f169a57bd52b304ea56e37dae2d333c1365909f12812d |
| C21HI_CLOSEOUT_REPORT_KO_20261020.md | libfile_750e99354434819196d8b33944ed15fd | file_00000000b3e081faab718551cfb172cd | 27,992 / 72ee19d6cef8ae200553bfa6c6e7c43a7c1001fef62748abab20965394d7068c |
| NCP_C21HI_FINAL_PROMPT_KO_20261020.md | libfile_52d9b40c438081919f2041b780f379a9 | file_000000005ef481fa9a02dc0986387bd0 | 6,654 / 15d3473e2fcda275d5fca846d29c78a1d2eadf4b447713efda4443529acfa6bb |

원 구현·제조검증 ZIP은 BASS_CR_C21HI_OPTIMIZATION_DELIVERY_20261020T073122Z.zip, 6,145,502 bytes, 1,691 members/1,690 payload, SHA256 3c30312161d06e85ab42bea38105b9ede26f97303441a47c6ce2aaccc7d0c537이다. Drive1KlkxM5XII-v11hMCMGnjyEUnRaqKNpb1, Dropbox id:BSpOijBcT10AAAAAAD_SWg, Library libfile_7c60ff7673fc8191b3d7c98b4a33774e, File file_00000000a1348230861aa6214bffd565이다.

이전 문서 마감 ZIP은 BASS_CR_C21HI_PUBLICATION_CLOSEOUT_20261020T105959Z.zip, 2,509,733 bytes, 91 members/90 payload, SHA256 f2752a31ef99680aa42eabb21bbe5f8d83cc724de41ab3bfa053f9043eaeb9fb다. Drive1O7wkkEauhxvbN16U1mkAxhwcIoMfyjol, Dropbox id:BSpOijBcT10AAAAAAD_SZg, Library libfile_cb771a719bf88191ab426e115103e48e, File file_00000000dbc481fab650a9cbaffcc416이다. 이 ZIP도 DELTA_MANIFEST의 base SHA가 맞는 문서에만 적용한다.

### 권위 문서의 한 바이트 교정

NCP_ORCHESTRATION_KO.md의 26ab 고정 Git 원문은19,254 bytes, SHA256 a2f9066f021659c2a2124425096d09e83df43ae72143646203d50be69427584b, Git blob5aeaf344fe88d21a5648d9a6c515ad083adc4646이다. 이전 local working copy19,255 bytes에는 trailing LF 하나가 더 있었다. 그 copy의 SHA1ab262e072995817d35d15a5ac400320e00a4aaeb51e6c191c50071fa0c1516a를 exact Git bytes SHA로 사용하지 않는다.

고정 패킷의 STATIC_VALIDATION_RECEIPT와 원 validation raw는 당시 working copy 검사를 기록하므로 그대로 보존한다. ncp/AUTHORITY_DOCUMENT_IDENTITY_CORRECTION.json이 위 정확한 Git identity를 additive하게 교정한다. Runtime source는 바뀌지 않았고 이 교정 때문에 원 runner나 과학 tests를 반복하지 않았다.

## 14. replay source closure 24개 — 파일명 확인용

다음 목록의 source는 모두 fe6bbaec2de5032b938aed0713623b9618ba70e6에서 가져온다. 개별 정확한 bytes·SHA는 고정 INPUT_PINS.json과 DELIVERY manifest가 권위다. 이 목록은 live NCP 전체 runtime을 대체하지 않는다.

1. research/cr_c21h_vigilode_bridge_20261019/EXECUTION_MANIFEST.json — 2,490 bytes; SHA256 7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb
2. research/cr_c21h_vigilode_bridge_20261019/optical_adapter.py — 21,058 bytes; SHA256 53c8644b64f937fcca022c5307295d8666de8aee6c07244d139be139badcb387
3. research/cr_c21h_vigilode_bridge_20261019/run_pilot.py — 15,363 bytes; SHA256 6f344f60d26a0ddb7bb205255cb767fdc230062bf60c56aae1ce58f5ef258f6c
4. research/cr_c21h_vigilode_bridge_20261019/requirements.txt — 97 bytes; SHA256 5658b6455896d47a13f0b03a99a5d59828882435d7a919ebc0909e549c100565
5. research/cr_c21h_vigilode_bridge_20261019/rust_bridge/Cargo.toml — 865 bytes; SHA256 96c388f8b5d92b11a255afd550e7e13284a7b3083e533474f1d57d16715bcc6b
6. research/cr_c21h_vigilode_bridge_20261019/rust_bridge/Cargo.lock — 42,739 bytes; SHA256 d30f7f6437b7704f845ba85f8206c94810fbd4ec1a48db9cba06b7b77604c892
7. research/cr_c21h_vigilode_bridge_20261019/rust_bridge/src/main.rs — 31,673 bytes; SHA256 19728487a6ad3e34058b52bccdae99c2026cd110c82b3f937e3c731f2931ea89
8. research/cr_c21h_vigilode_bridge_20261019/rust_bridge/build_bridge.sh — 3,947 bytes; SHA256 a870c9f60f241b18839398c44ebe4cfc3d95644b5c8209239a00a511581e497a
9. research/cr_c21h_vigilode_bridge_20261019/rust_bridge/test_bridge_protocol.py — 10,553 bytes; SHA256 8b4cbb0424c8a6a167ad25265d8490d90cc069af8ededb6e4d2309ea21446354
10. research/cr_c21i_callback_optimization_20261020/EXECUTION_MANIFEST.json — 831 bytes; SHA256 f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec
11. research/cr_c21i_callback_optimization_20261020/run_optimized_pilot.py — 14,719 bytes; SHA256 1a3f4d9066bedc3a8d7466723e8f344fa451c0c6a85c48bf0efe03210d6d8a43
12. research/cr_c21i_callback_optimization_20261020/optimized_adapter.py — 20,343 bytes; SHA256 bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e
13. research/cr_c21i_callback_optimization_20261020/native_cache_contract.py — 21,580 bytes; SHA256 c94c506aacf9bf86765e6a58ced7d005ed50d8999f7f0dd6232df9159b7bd097
14. research/cr_c21g_reference_refinement_20261019/EXECUTION_MANIFEST.json — 4,009 bytes; SHA256 7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed
15. research/cr_c21e_event_native_20261018/src/event_coupler.py — 10,655 bytes; SHA256 24386145f4337b2e01a32219a56ec2446080e4aa4a679a8f956a3eb7ff2ab819
16. research/cr_c21e_event_native_20261018/src/native_micro.py — 5,109 bytes; SHA256 ce27acea344604c08159e08d6e703f66a85d51f0729b4e30aa2248a3337ecc27
17. research/cr_c21e_event_native_20261018/src/reference_tau.py — 11,653 bytes; SHA256 714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0
18. research/cr_c21e_event_native_20261018/src/run_experiment.py — 20,173 bytes; SHA256 71fb34d6ae5ca843868a2b666a0e7f93ee330c5bedc6c7191220e8060f4869fc
19. research/cr_c21e_event_native_20261018/vendor/pr79/c21d_trilane.py — 13,498 bytes; SHA256 22d4c355353721cd0dff00a401f15a18b9d6fdfda8dc0bdfaab753a3c1c044c0
20. research/cr_c21e_event_native_20261018/vendor/pr79/exposure_contract.py — 9,115 bytes; SHA256 b30cefb2fdce72f813f70fc42a29f2dc67516e73c18f4907737341fcf8ec9407
21. research/cr_c21e_event_native_20261018/vendor/pr79/radau_exposure_oracle.py — 7,132 bytes; SHA256 23895d81e50791135c689db5b6a180fcb23e05ef8cb76e271c65b189cf3fe428
22. research/cr_c21e_event_native_20261018/native/native_point.rs — 8,305 bytes; SHA256 3812cf4fec625fdec32e47d737bec8e0306cc538372c5a2cf801d2b0cf590e2d
23. research/cr_c21e_event_native_20261018/build_native.sh — 2,582 bytes; SHA256 917ca6620ff5d9ad85cb1a783b3ebbc3b87db7dd58f11c7b500bd1dce35dcf82
24. research/cr_c21e_event_native_20261018/run_ncp.sh — 3,563 bytes; SHA256 b451bf1a2400920d9b2861eed7f65e718342df1afd0f1c15a7a8a8d127b3b22b

새 연구를 시작하기 전에 최신 반환을 읽고, 같은 근거는 재사용하고, 바뀐 의존성만 검증해라. 다음 native 행의 실제 결과가 생기기 전에는 exact live 실행·성능이나 global error bound를 완료로 표시하지 마라.
