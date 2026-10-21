# C21K 연구·구현·NCP 실행 준비 마감 보고서

**원 연구 마감 관측: 2026-10-20 UTC. 이 문서는 2026-10-21 scratch 소실 뒤의 복구·게시 마감본이다. K content `bab323983dad5206e162dbfdaefc167f2fabea45`와 PR `https://github.com/cosmosapjw-quantum/bass_cr/pull/89`는 실제 ACK로 결속했으며, 문서 head·최종 백업은 최종 외부 영수증을 따른다.**

완료된 I/J 위에 opacity 계수 재사용, K runner와 미실행 DAG를 추가했다. Epoch13·runner22·원 source plan1·saved replay3이 통과했다. 새 native/IVP는0이다. **일관된 가속은 NOT_ESTABLISHED, K live native는 NOT_RUN, native 성능과 NCP64 scaling은 NOT_EVALUATED**다. [E1–E4]

52개 논리 slots 중 기존 완료3개, 미실행 최대49개(H7+G12+I14+K16)다. 원 잔여·조건부21개와 새 비교 확장28개를 구분한다. 실제 실행은 현재 자원·신원·부모·G 판정에 따르며49는 제출·완료 횟수가 아니다. [D1]

## 복구 상태와 근거 가용성

정확 복구한 원 보고서17,942bytes/SHA256 `93084b00325a29ff1f99c154d271af1d0fefd114525b946d0e2fde080349f9fe`를 보존하고 이 문서만 별도 보수했다. K runtime3개와 NCP exact core8개(program3·tests3·backlog·control decision)는 원 최종 hash와 동일하다. Epoch·runner·실제 plan·최종 replay의 원 근거는 checkpoint2에서, NCP33 PASS·targeted1 PASS·staging3건 PASS·negative2 PASS의 실제 도구 반환은 대화 기록에서 복구했다. 이번 문서 보수에서 이를 재실행하지 않았다. [RC1]

기존34-payload NCP manifest SHA8f5f36…의 전체 bytes, 초기14 PASS·23 error/7 skips·24 fail·24 PASS raw, 원 `VALIDATION_HISTORY.json` 전체 bytes와 원 generated-UTC staging receipt는 미복구다. 초기 실패의 역사와 제한은 남기지만 해당 raw가 현재 존재한다고 주장하지 않는다. 원 독립 review JSON SHA dc521c…와 인계문 review JSON SHA c698c9…도 exact 미복구다. 후속 `planning/C21K_NCP_INDEPENDENT_REVIEW_RECOVERED_20261021.json`은 동일 source에 대한 **역사 PASS_SCOPED**를 복구한 기록이며 새 검토가 아니다. 새 공개 payload용 NCP manifest는 원 packet identity와 구분한다. [RC1,RC2]

## 1. 이어받은 권위와 원본 보존

| 역할 | 고정 값·상태 |
|---|---|
| C21G 실행 content | `e742d44f605c51c06615451774ba90af8f41f622` |
| C21H 실행 content | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` |
| C21I 실행 content | `fe6bbaec2de5032b938aed0713623b9618ba70e6` |
| 기존 native 반환 head | PR87 `d3eaf596e46be4f994723fb742237a7399c290ed` |
| C21J 진단·패킷 content | `55e6569a8f816e13babe4165f0fef3655f7299a3` |
| C21J 최종 문서 head / K 부모 | PR88 `fee0d6a3f1b6460a24a1ae60f50ee84971227e5b` |
| K content / 새 PR | `bab323983dad5206e162dbfdaefc167f2fabea45` / `https://github.com/cosmosapjw-quantum/bass_cr/pull/89` |
| K 후속 문서 head | 최종 외부 영수증 `publication.document_head` |

F 게시 완료·G 독립 계약·I 제조32+FD2/native0·J 진단 완료를 유지한다. I 제조 RHS423→372,74→71은 기존 근거이며 옛 suite/제조 실행을 반복하지 않았다.

PR87 완료3개는 H common_ic/VigilODE/base와 I vectorized base/FD다. 각823, 합2469 native 호출은 역사 실행이다. J의69 full-state hits·754 table queries는 saved replay다. [J1]

원 source/test/raw 변경0. 복구 전 실제 plan에서 closure34파일(기존24+고정 G4/baseline6)이 manifest와 일치했다. 원 archive의 job별 sidecar가 strict inventory를 막아 receipt+named payload116개만 create-only staging했다. 원 tar/sidecar3의 변경 없이 strict3건·negative2건 PASS였으며, 이번 복구는 그 도구 반환을 재사용했다. 새 native0이다. [E3,E6,RC1]

## 2. 연구 전과 마감 전의 새 결과 확인

초기21:14–21:15 UTC 뒤22:37:50.734–22:40:04.762에27개 조회가 성공했다. PR85–88·C21 refs15개는 동일했고 최근 updated PR20개와21:15:33 이후 검색에서 새 C21 반환0이었다. 네 PR은 open/draft/unmerged이며 이 범위의 K 의존성 변경0이다. [D2]

REI198 `2a8656af…` profile3, REI199 `4f136489…` tiny native4, HE78 `4977b6dd…`·WU125 `701cf85b…` 준비도 읽었다. 별도 owner 결과를 C21 완료·속도로 옮기지 않았다. [D2]

22:38:19–22:38:38 UTC 세 저장처 refresh에서 지정 dossier의 새 외부 후보0, 자체 checkpoint1개를 관측했다. Library는 cutoff 이후 폴더 재귀, Dropbox는 직접32항목·has_more=false, Drive는 직접64항목과 관련 하위1항목이다. 자체 checkpoint는 외부 반환이 아니다. 계정·NCP disk 전체 부재는 주장하지 않는다. 다른 대화 검색의 실제 unavailable 상태도 유지한다. [D3]

추가 bounded refresh는 2026-10-21 03:13:44 UTC에 완료했다. Bass_cr C21 branch13개·최신 PR88 fee0에서 새 C21 source/native 반환0, 의존성 변경0이었다. REI199 head964b2e3…의 time8/time16/time32 native3건과 HE81 head d6c1cf9…의 scoped canary 반환을 별도 실제 결과로 확인했다. 원 source/owner가 다른 결과이므로 C21 완료·K native 성능으로 옮기지 않았다. WU 새 NCP 반환은 그 GitHub/Dropbox 조회 범위에서 미확정이며, 다른 대화와 실제 NCP host는 이 조회 대상이 아니었다. Primary receipt/진단을 읽은 범위로서 전체 raw chain을 다시 admit한 결과는 아니다. [D4]

## 3. 이번 최적화의 이론적 내용

고정 fixture에서 원 opacity의 에너지와 계수는

\[
E_i(x)=q_i e^{-x},\qquad
K_{ij}(x)=s\,c\,n_{H,0}e^{-3x}\sigma_j(E_i(x))
\]

로 주어진다. 실제 key는 원 reference가 clamp한 뒤 전달한 binary64 epoch의 bytes다. fixture·원 source·상수·실행 환경이 고정되면 E,K는 gas·tau·passive ledger 값에 의존하지 않는다. 따라서 gas FD의 여러 상태가 같은 epoch를 사용하면 이 계수만 재사용할 수 있다. 반면 hazard의 neutral fraction과 photon population은 gas·tau에 의존하므로 전체 RHS나 native 응답을 epoch만으로 재사용할 수는 없다. [T1]

Cell LRU16은 성공한 유한 결과만 저장한다. `+0/-0`·인접 binary64를 구분하고 float/NumPy float64 외 타입을 거부한다. 불변 bytes와 독립 writable 반환을 분리하며 cell·fixture/source 변경 시 table을 재사용하지 않는다.

Miss 계산에서는 원 왼쪽 결합 곱 `((((s*c)*n)*exp(-3*x))*cross)`의 동일한 중간 결과만 분리한다. 곱셈을 재결합하거나 H 표현을 바꾸지 않는다. E 계산과 cross 호출 순서는 그대로다. 원 exp 계산 횟수는 opacity miss당 M9에서28→2, M81에서244→2가 되지만 cross는3M회로 같다. 최종 기본 실행의 H는 원함수를 유지한다. 수학적 실수식의 같음과 binary64 연산 tree의 같음을 구분했다. [T1]

원 opacity c_o, CSE miss c_f, key/guard/lookup c_k, hit 복사 c_h, miss 저장 c_s, setup C_0, Q=N_m+N_h에 대해

\[
\Delta T=N_hc_o+N_m(c_o-c_f)-Qc_k-N_hc_h-N_mc_s-C_0.
\]

Hit만으로 ΔT>0을 보장하지 않는다. 전체 job에는 protocol·native·solver·OS 비용도 있다. 기존 full-state cache가 없앤69회 뒤의 stream에서 epoch 비용을 센다.461 opacity hits는461회 native 절약이 아니다. [T1,E4]

독립 작업의 총 work W와 critical path L, 동일 CPU P개인 이상적 모델에서는 `C* ≥ max(W/P,L)`이다. 선행 관계 외 제약이 없는 work-conserving list 모델의 상한은 `C_list ≤ W/P+(1−1/P)L ≤ (2−1/P)C*`다. 메모리 admission·quota·공유 I/O·다른 CPU 속도 때문에 blocking이 생기는 실제 NCP scheduler에 이 근사비를 자동 부여하지 않는다.64코어라는 명칭만으로64배 가속을 추론하지 않는다. [T1,L1]

SciSpace2검색, Exa 원전, Wolfram context/evaluator2개를 사용했다. CAS는 IEEE 전체 인증이 아니다. Context 오류·재개와 미확보 HAL 원문을 보존했다. Michie는 abstract/metadata, Graham은 원 모델·proof 범위다. 강한 no-go·일반 memoization/scheduling의 신규성은 주장하지 않는다. [T2]

## 4. 실제 구현과 source admission

K runtime manifest는 `epoch_adapter.py`, `run_epoch_pilot.py`, `epoch_pilot_contract.py`의 정확한3파일만 포함한다. Manifest SHA256은 `f80955787df909c4709d5076bcb017d7995fbf33197f41f04b5e03bc934e4744`다. 최종 epoch SHA256은 `fc8009f7e185f7a257cbda0956317f4e7f358a8c548501c96e204aa7c94498bd`다. 원 NCP packet은 SHA `8f5f36f45e6ff89f4fb43912926d6706924e5266ec01c0ef60ae6bbaa9d7dca5`로 동결됐으나(34 payload,327621bytes) 그 manifest 전체 bytes는 현재 미복구다. 현재 `ncp/NCP_CODE_MANIFEST.json`은7606bytes/SHA256 `6784a3b04a09c354d63d9b5613b452efeaaeaab16b599b298ba4f59e7d425ce8`로서 RECOVERED_PACKET22 payload/192450bytes(self 제외)를 집계한다. 원 packet SHA를 재사용하지 않는다. Scheduler·builder·helper의 최종 source bytes는 각각 원 hash와 일치한다. [E0,E5,RC1]

원 I/H bytes를 private module에서 읽고 opacity import만 연결한다. 원 provider·exact admission/live guard·build 검사·CPU55·deadline·cleanup을 유지한다. 근사·clipping·fastmath·dtype 축소·허용오차·state/event 변경은 없다.

Native K admission은 checkout 밖의 H/I/K PUBLISHED receipts, detached K content, H→I→K ancestry, inherited committed bytes 및 K manifest를 확인한다. 원 I verifier가 요구하는 HEAD=fe6 조건은 원 I 실행에 그대로 남는다. K는 별도 검사를 하며 원 I receipt를 K content로 고쳐 쓰지 않는다. FD는 같은 K mode/source/publication을 확인한 뒤 원 H의 COMPLETE base·fixture·method·native/bridge·전체 payload 검사를 수행한다. 기존 I vectorized parent를 새 K FD 부모로 사용할 수 없다. [E2]

## 5. 완료한 검증과 정확한 범위

| 검증 | 실제 결과 | 해석 |
|---|---|---|
| 최종 epoch focused |13 methods PASS, unittest0.326초 | key·소유권·cell reset·source mutation·deadline, 원 threshold를 포함한126입력의 bit parity |
| 새 runner focused |22 methods PASS, unittest0.599초 | 실제 임시 Git과 explicit doubles의 출판·조상·source·FD·guard 검사 |
| 실제 원 source plan | exit0,0.421523초 | H/I/G/F/baseline34파일, doubles 없음; READY_EXECUTABLE_INPUTS_VERIFIED |
| 최종 saved replay |3경우 PASS_SCOPED, 실행1.252359초 | 각472 replies/40,432 binary64 값, FD nodes, physical fields 일치 |
| Scheduler/binder focused |33 methods PASS,1.351초 | 로컬 subprocess와 명시적 observer/build/publication doubles |
| Tracker gate 변경 확인 | targeted1 PASS,0.033초 | 33개 검증 뒤 강화한 child PID/start-ticks/RSS gate의 별도 검사 |
| 새 native/IVP |0 / 0 | 실제 native admission·미래 solver 경로 성공은 아직 미검증 |

13·22·33은 별도 집합이다. 33+targeted1을 최종 source의34-test suite 한 번으로 합치지 않는다. 수정 전후 source snapshots와 복구된 최종 raw를 재사용하며 초기 실패 raw의 미복구 범위는 RC1에 명시했다. 실제 source-only UNBOUND builder 준비는 역사 PASS이고 복구 중 같은 exact code의 템플릿 metadata 재생성이1회 있었다. 어느 것도 실행 가능 BOUND/native 결과는 아니다. Plan/replay·metadata 재생성은 test 수에 더하지 않는다. [E1–E5,RC1]

| 재생 stream / mode | table queries | opacity requests | miss | hit |
|---|---:|---:|---:|---:|
| I base / vectorized |823|859|329|530|
| I base / vectorized_exact |754|790|329|461|
| I FDhalf / vectorized_exact |754|790|329|461|

각3개 segment의 RPC·성공 terminal·native 응답표를 고정 J admission으로 읽고 입력 bytes 불변을 확인했다. 저장 accepted states로 physical summary를 재구성한 결과다. 새 trajectory 적분이나 미래 live process·deadline·solver 요청열의 실행 완료는 아니다. [E4]

## 6. 성능 판정과 역사 source 구분

비율은 원 I-exact saved-callback 시간 / 후보 saved-callback 시간이다.1보다 크면 그 표본에서 후보가 빠르다.

| 보존한 후보 | 당시 epoch SHA 앞자리 |7쌍 중앙값|범위|
|---|---|---:|---|
| 초기 opacity+H cache |3245d871…|0.9364664941|0.8827007446–1.1800605948|
| opacity CSE+cache, H 원함수 |db244c06…|1.0004085537|0.7356966366–1.1219821145|

두 범위가1을 가로지르며 일관된 saved-callback 가속은 NOT_ESTABLISHED다. 이후 typed-key·deadline guard가 추가된 **최종 fc8009f7 소스의 paired benchmark로 이 수치를 전이하지 않는다.** 역사 디렉터리 `epoch_final/`의 이름은 최신 source authority를 뜻하지 않는다. [T1,E4]

동시 campaign wall은 자원 경쟁을 포함하므로 통제된 native speedup benchmark가 아니다. Native 성능과 NCP64 scaling은 NOT_EVALUATED다.

## 7. 전체 미실행 작업과 DAG

| Lane | logical 전체 | 역사 완료 | 미실행 base/reference | 조건부 | 미실행 최대 |
|---|---:|---:|---:|---:|---:|
| H: fixture2×method2×base/FD |8|1|3|4|7|
| G: reference8+refinement4 |12|0|8|4|12|
| I: vectorized/exact×fixture2×method2×base/FD |16|2|7|7|14|
| K: 새 runtime의 같은2모드 행렬 |16|0|8|8|16|
| 합계 |52|3|26|23|49|

V3 inventory는 역사 잔여·조건부 H7+G12+J exact base1/조건부FD1=21과 이번 요청의 추가 I12+K16=28을 구분한다. 옛 J packet의 새 실행 허용은 base1뿐이었다. I instrumented baseline8은 H 중복이라 제외한다. [D1]

G는 원 campaign container1개 안에서 worker1로 reference8→원 native_source gate→조건부4를 실행한다. 기본 top-level pending은38=H7+I14+K16+G1이다. G exit0을12개 COMPLETE로 올리지 않는다. FD는 같은 lane/fixture/method/mode의 검증된 COMPLETE base가 hard parent다. H/I/K 비교 상대는 soft evidence라 독립 실행을 막지 않는다.

현재 문맥의 최소 controls는 다음 배타적 분기다. 원 완료3개는 변경하지 않는다. [D1]

| 검증된 현재 입력 | 추가 controls | 최대 새 attempts / top-level pending |
|---|---|---:|
| Known bytes·H FD 문맥 일치 |0|49 /38|
| 같은 bytes, H 경로 문맥 변경 |H base1|50 /39|
| 원 source/owner/build 통과, binary bytes 변경 |H base1+I vectorized base/FD2|52 /41|

Binary 변경 분기에 H path control을 또 더하지 않는다. 새 I FD는 새 I base에 의존한다. 기존3개는 역사 근거로 남고 다른 build의 현재 일치 근거로 재표시하지 않는다. Controls는 실행 전 변경 의존성을 위한 단일 시도이며 실패 retry가 아니다. Source/owner 변경은 BLOCKED다.

**실제 G/H/I 운영 checkout은 모두 detached fe6**, K는 별도 detached K content다. G e742/H40ea는 원 과학 provenance이며 이번 실행 HEAD와 구분한다. 각 checkout의 원 bytes·baseline·committed identity를 검증한다. Full48이나 미준비 matrix를 CPU 채우기용으로 추가하지 않는다.

## 8. 현재 NCP 상태와 실행 준비 경계

**NCP host·배정·binary 경로는 NOT_OBSERVED, 새 NCP native는 NOT_RUN이다.** 이전 read-only host 조회가 응답 없이 parent assistant에 의해 중단됐다는 역사 관측을 유지한다. 도구의 “aborted by user” 표시는 사용자가 직접 중단했다는 뜻이 아니며 remote completion은 UNKNOWN이다. 원 remote 조회 raw는 현재 복구물에 없고 이번에 새 remote probe를 수행하지 않았다. 이 공백을 서버 부재·native 실패·접속 성공으로 바꾸지 않는다. [RC1,RC2]

Scheduler는 CPU55를 제외한 실제 owner CPU 배정·affinity/cpuset·ancestor quota·RAM을 admit한다. Host fingerprint·UTC expiry·canonical allocation hash·shared CPU lease를 결속하고 coordinator CPU1/RAM도 계상한다. 메모리 reserve는 effective limit의12.5%와1GiB 중 큰 값이다. 광고64core/128GB를 현재 가용량으로 쓰지 않는다. Matching-context와 path-only control 분기의 최초 ready process는20, 검증된 새 binary의3-control 분기는21이다. 실제 RAM/quota·CPU/lease와 bound DAG가 동시성을 제한한다. 전체 batch 예시에는 선택 cap `maximum_concurrent_jobs`를 생략하여 고정1로 직렬화하지 않으며 실제 보수적 RSS budget을 결속한다.

Owned-process gate는 marker뿐 아니라 실제 tracker의 child PID·동일 start ticks·살아 있는 state·양의 RSS를 확인한다. 로컬 sandbox의 production 관측은 BLOCKED, NCP 통합은 미평가다. Probe 실패는 native0으로 중단한다. Bound matrix와 subprocess tests의 observer/admission doubles 범위를 유지한다. [E5]

원 H/I/K job300초·RHS/native200000·native timeout min(15초,남은예산)·worker1을 유지한다. G 내부는 job별300초, container3660초다. Campaign21600초와 owner expiry 중 먼저 끝나는 상한을 적용한다. Setup/guard도 원 budget을 소비한다. Plan·자원 관측·execute·resume를 구분하고 실패/시도 raw는 재시도하지 않는다.

Bridge717c…/receipt c846…는 실제 호환성이 확인되면 재사용하며, 필요 시 원 locked/jobs1 helper를 쓴다. Native owner6ea2…/known1e726… 또는 원 G가 검증한 owner/build_exit/input_sha256/owner_source.tar 경로를 admit한다. Native helper jobs2·wrapper tests는 bridge JSON receipt와 구분한다. 현재 artifact 존재는 추정하지 않는다. [B1]

## 9. 실행·게시·백업·DAG 상태

| 축 | 마감 상태와 권위 | 근거·남은 실제 실행 |
|---|---|---|
| 이론·epoch 구현 | SCOPED_COMPLETE | 최종 source identity 보존 |
| focused/실제 plan/저장 재생 | PASS_SCOPED | 각 실제 execution receipt |
| native exact/K 및 NCP49/50/52 | NOT_RUN | 실제 입력 분기·admission·terminal/raw |
| 성능 | 가속 NOT_ESTABLISHED; native NOT_EVALUATED | 같은 source/build/controls의 실제 비교 |
| Scheduler 검증·검토 |33+targeted1의 역사 PASS_SCOPED; 실제 tool raw 복구 | RC1의 byte identity·RC2의 RECOVERED_PRIOR_PASS_SCOPED를 결속; 새 검토 아님 |
| Git content/PR | 실제 게시 ACK: `bab323983dad5206e162dbfdaefc167f2fabea45` / `https://github.com/cosmosapjw-quantum/bass_cr/pull/89` 결속 | 실제 content SHA,부모fee0,ref/PR ACK; tree ACK와 구분 |
| 후속 문서 head | 최종 외부 영수증 publication.document_head | 실행 content와 구분 |
| 최종 묶음·세 저장처 | 최종 외부 영수증 backups.delivery / backups.document_closeout | 실제 bytes/SHA/provider ACK |
| DAG |52논리 slots의 준비·재사용·조건부 범위 확정 | 성공/실패/BLOCKED/REUSED를 실제 반환으로 갱신 |

게시 계보는 **C21J fee0 → K 실제 content → 후속 doc head**다. Content/PR은 실제 게시 ACK로 결속했으며 doc head·ZIP locator는 `C21K_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json`의 위 key로 읽는다. 미발급 commit·순환 archive hash를 만들지 않으며 checkpoint와 최종 delivery를 구분한다.

과거 실패·수정 전 source/timing·역사 NOT_PUBLISHED/PENDING을 유지하며 raw exact 복구 여부는 별도 기록한다. 공개 자료에는 LIVE_INVENTORY/process 원문·서명 URL·논문 전체·대량 abstract를 넣지 않고 허용된 자체 요약과 수학 결과를 사용한다. 실제 게시·백업 receipt는 별도다.

## 10. 과학 HOLD와 근거 목록

Full48, 전체 native/MD14 source matrix, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle/full-driver parity는 기존 HOLD다. Source-specific bit 동등성, 유한 trace 일치, balance 기록, NCP 프로세스 exit0은 각각 별도 주장이다. 어떤 것도 전역 ODE 오차 인증이나 과학 HOLD 해제를 자동으로 뜻하지 않는다. **`global_error_bound=null`**을 유지한다.

아래 근거는 고정 content의 동일 bytes와 경로에 결속된다.

- **J1**: C21J 최종 인계문과 PR87 고정 반환; PR88 head fee0 및 C21J publication closeout receipt.
- **E0**: `EXECUTION_MANIFEST.json`.
- **E1**: `evidence/verification/epoch_focused_final/EXECUTION_RECORD.json` 및 실제 stderr.
- **E2**: `evidence/runner_focused/attempt_01/EXECUTION_RECORD.json` 및 실제 stderr.
- **E3**: `evidence/runner_integration/actual_plan_01/EXECUTION_RECORD.json`, 그 plan의 source identity/receipt 및 `MATERIALIZATION_RECEIPT.json`. 별도 `CLOSURE_AFTER.json` 원 파일은 현재 미복구다.
- **E4**: `evidence/verification/epoch_replay_final/replay/REPLAY_REPORT.json`; 역사 timing은 `epoch_final`·`epoch_attempt_03`의 각각 source-bound report.
- **T1/T2**: `theory/C21K_EPOCH_CACHE_AND_DAG_THEORY_KO.md`, `C21K_EPOCH_INDEPENDENT_REVIEW.json`, `LITERATURE_LEDGER.json`, `R_LOOP_STATUS.json`, 허용된 Wolfram evaluator raw2개.
- **D1**: `ncp/BACKLOG_INVENTORY.json` V3, `ncp/DEPENDENCY_CONTROL_SCOPE_DECISION.json`, `planning/BACKLOG_REVIEW_V2_KO.md`.
- **D2**: `intake/refresh_2237/SUMMARY.json`과 query inventory의 당시27회 관측 요약.
- **D3**: `intake/EXTERNAL_FINAL_DELTA_REFRESH_PUBLIC.json`.
- **D4**: `intake/FINAL_EXTERNAL_REFRESH_20261021_SUMMARY.json`, `FINAL_EXTERNAL_REFRESH_20261021_PRIMARY_EXCERPTS.json`.
- **E6**: `ncp/validation/HISTORICAL_EVIDENCE_STAGING_TOOL_RESULT.json`, `HISTORICAL_EVIDENCE_NEGATIVE_TOOL_RESULT.json`과 대응 RAW.txt. 원 generated-UTC staging receipt는 미복구다.
- **E5**: 새 `ncp/NCP_CODE_MANIFEST.json`, `ncp/validation/SOURCE_VALIDATION_SNAPSHOTS.json`, `ATTEMPT_05_TOOL_RESULT.json`·`TRACKER_GATE_FOCUSED_TOOL_RESULT.json`과 대응 raw.
- **RC1**: `ncp/RECOVERY_RECEIPT_20261021.json`. 원 `VALIDATION_HISTORY.json` 전체 bytes와 remote 조회 raw는 미복구다.
- **RC2**: `planning/C21K_NCP_INDEPENDENT_REVIEW_RECOVERED_20261021.json`; 역사 PASS_SCOPED의 재구성 후속 기록이며 원 review JSON과 byte identity가 다르다.
- **B1**: `evidence/runner_integration/build_contract/`의 helper 추출·원 controls. 운영 checkout은 D1이 규정한다.
- **L1**: Graham, *Bounds for Certain Multiprocessing Anomalies* (1966), [DOI](https://doi.org/10.1002/j.1538-7305.1966.tb01709.x). 현재 적용의 가정·원전 읽기 범위는 T1/T2를 따른다.

## 게시 전송 형식

큰 JSON 전송의 무응답을 줄이기 위해 고정 source fetch 증거와 실행 불가 preview를 각각 `evidence/runner_integration/FETCHED_CONTENT.json.gz`, `ncp/CAMPAIGN_UNBOUND_TEMPLATE.json.gz`로 무손실 압축했다. 압축 해제 bytes와 원 SHA256의 일치를 확인했으며 원 JSON도 최종 delivery의 `original_publication_inputs/`에 보존한다. 상세 대조는 `administration/PUBLICATION_ENCODING.json`이다. 실행 코드·테스트·backlog/control pins는 변경되지 않았다. 실제 campaign은 원 builder가 새 BOUND JSON으로 생성하며 압축 preview를 실행하지 않는다. 현재 공개 content는116파일,964255bytes이고 최종 CONTENT_MANIFEST는19325bytes/SHA256 `dd7d9d3d79acbbbde88ee1994a175a31e1cf2369c5394e6233b50dbff300f4c6`다.
