# C21J 연구·게시·백업 마감 보고서

## 마감 상태와 읽는 순서

PR87의 실제 native 결과를 수용한 C21J trace 복원·callback replay 구현, focused 검증,
독립 검토, content 게시와 전체 연구 전달본의 세 저장처 백업이 완료됐다.
실제 native exact 실행은 NOT_RUN, exact 성능은 NOT_EVALUATED이며
global_error_bound=null이다. 이번 대화의 새 native chemistry 호출과 IVP 적분은 0이다.

| 역할 | 실제 고정값 |
|---|---|
| 실행 source | `fe6bbaec2de5032b938aed0713623b9618ba70e6` |
| 원 native 반환 head | `d3eaf596e46be4f994723fb742237a7399c290ed` |
| C21J content / draft PR88 | `55e6569a8f816e13babe4165f0fef3655f7299a3` |
| 전달 ZIP이 담은 D1 문서 head | `e04b19669b1542b4537448c764d1dc02ebc8b7b6` |
| 이 보고서를 담은 최종 D2 head | 최종 외부 `C21J_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json`의 실제 ref 관측을 읽는다 |

본문의 전달 ZIP은 이 보고서 이전 D1 snapshot이므로 그 SHA/저장처 ID를 여기서
비순환적으로 고정할 수 있다. 이 보고서와 D2 문서 delta를 담을 마지막 마감 ZIP의
SHA/ID, D2 자신의 commit SHA는 생성 뒤의 최종 권위 영수증에서 읽는다.
과거 snapshot의 PENDING과 NOT_RUN은 생성 시점의 사실로 보존했다.

## 완료한 전달 백업

- 파일: `BASS_CR_C21J_RESEARCH_DELIVERY_20261020T173607Z.zip`
- 크기/구성: 3495267 bytes, 135 members / 134 payload.
- SHA256: `b3f867d40f2f760e5f61168a1bec858d2c9a1dba646e7b56d015c569283a1ae8`
- Drive: `1VUN3oQO_U3VHB3n7PDcdmudhsKwt5QPj`
- Dropbox: `id:BSpOijBcT10AAAAAAD_aDQ`, rev `65e4ba52c16ad0af03d47`
- Library: `libfile_7f604c8e9d1081919c828e9a8fc97cd4`, file `file_000000005a88820ba56ff654e3927b65`

로컬 ZIP은 한 번의 전체 payload/CRC roundtrip으로 검증했다. Drive/Dropbox는
실제 upload ACK와 ID·크기 metadata에 따른 R1 확인이다. Library 전달 ZIP은 저장
뒤 두 번째 scratch 소실에서 실제 복구했으므로 그 목적에 한해 원 ZIP SHA와
134개 payload를 R3로 확인했다. 모든 원격 복사본을 내려받아 SHA를 확인한 것으로
표시하지 않는다. Catalog 갱신으로 거부된 첫 Drive 준비와 Library helper의
tools/list HTTP403은 실제 업로드 시작 전의 실패이며, 확인된 정상 경로에서 한 번씩
생성했다. 기존 파일을 덮어쓰지 않았다.

작업 환경은 두 번 소실됐다. 첫 번째에는 미리 보존한 content78 원 바이트로,
두 번째에는 이미 저장된 전달 ZIP으로 복구했다. 각 byte/hash 검증 결과는 별도
recovery receipt에 있으며, 이 복구를 이유로 옛 suite·제조·native·C21J 분석이나
replay를 반복하지 않았다. 최신 scoped metadata 확인에서는 PR85–88과 기존 실행
의존성이 유지됐다. 다른 대화 또는 NCP disk 전체의 결과 부재는 주장하지 않는다.

## 다음 한 행과 현재 한계

다음 준비 노드는 common_ic / vigilode-rodas5p / vectorized_exact / base 한 건이다.
구체적인 wrapper·env·원 CLI·입력/바이너리 pin·상한은
`NCP_C21J_FINAL_PROMPT_KO_20261020.md`와 content55e의 `ncp/` packet에 있다.
현재 NCP 자원 admission은 아직 관측하지 않았다. CPU55 보호, 실제 known native
SHA와 bridge build 검증, job1/worker1/300s/200000 cap 및 조건부 FD parent 계약을
지킨다. source24 복구 묶음은 full native checkout을 대신하지 않는다.

실행·과학 판정·성능·게시·백업·DAG를 분리한다. C21F 기존 게시 완료, G의 독립
reference 계약, 원 실패/raw/역사 NOT_PUBLISHED, 기존 과학 HOLD를 유지한다.

---

아래에는 content55e에서 확정한 전체 연구 본문을 그대로 이어 붙였다. 이후 문서
게시와 백업 상태는 위 마감 절과 최종 외부 권위 영수증이 추가한다.

# C21J 연구 보고서 — 새 native 반환의 수용, exact 요청 복원과 callback 재생

2026-10-20 UTC. 연구·코드 결과를 기록하는 본문이다. 실제 content commit,
후속 문서 head, draft PR, 저장처 ID 및 마감 시각은 별도의
`PUBLICATION_RECEIPT.json`과 최종 마감 영수증을 따른다. 본문에 인용한 과거
`NOT_RUN`, 실패 및 archive 제작 시점 `PENDING`은 해당 시점의 사실로 보존한다.

## 1. 이번에 완료한 일

**인계 이후 게시된 PR87의 실제 native 결과를 발견해 수용했고, 이를 입력으로
C21J의 trace 복원·exact callback 재생을 구현하고 집중 검증했다.** 이전 C21I는
이미 구현·검증·게시된 연구로 유지했다. 이 대화에서 native chemistry와 새 IVP
적분은 각각 0회이며, 기존 제조 32 jobs + FD 2 jobs 및 옛 physics suite는
재실행하지 않았다.

새로 확보한 직접 결과는 다음과 같다.

1. H base와 I vectorized base의 전체 28차원 endpoint, 모든 ledger와 endpoint
   진단량, 세 raw segment result 객체, accepted physical 상태 39개가 binary64
   단위로 같다. 39개에는 각 cell의 시작점 세 개가 포함된다.
2. 저장된 각 작업의 원 RHS 요청 823개를 복원했다. 현재 C21I exact 구현의
   full physical `(t,u)` cell LRU16에 해당하는 hit는 **69개**, miss는 **754개**다.
3. 원 callback 코드를 저장된 native 응답표에 연결한 네 재생 경우가 모두
   `PASS_SCOPED`다. 각 경우 472개 callback reply, 40,432개 binary64 수치값,
   실제 FD node 및 물리 summary 재구성이 일치했다. exact의 기록 조회는
   823→754로 줄었다.
4. 작은 native EVAL key의 100개 중복 중 추가 31개는 광학깊이가 달라 현재
   full-RHS cache의 hit로 세면 안 된다. 이를 구분하는 유도와 실제 인덱스를
   보존했다.
5. I vectorized의 한 번 기록된 job wall은 H보다 약 18.17597% 길었다. 이것은
   한 쌍의 관측이다. 전체 시간 가속은 `NOT_ESTABLISHED`, **실제 native exact
   실행은 `NOT_RUN`**, exact 성능은 `NOT_EVALUATED`다.

직접 근거는 `evidence/analysis_attempt_02/ANALYSIS.json`,
`evidence/replay_attempt_02/REPLAY_REPORT.json`,
`evidence/independent_review/REPLAY_REVIEW_V2.json`이다.

## 2. 권위 입력과 인계 이후의 변경

사용자가 지정한 전체 인계문, 최종 권위 영수증, 전체 보고서, NCP 인계문과
마감 ZIP을 materialize하고 주어진 전체 byte 수와 SHA256을 확인했다. 기존
scratch checkout 또는 Rust binary의 존재는 가정하지 않았다. 과학 프로그램은
GitHub의 고정 content에서 읽었고, 수신한 파일은 Git blob과 SHA256으로 연결했다.

| 단위 | 과학 실행 content | 관측 문서 head | 실제 상태 |
|---|---|---|---|
| C21H / PR85 | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | `0ec4c55102766c40c554ffc6141eb08fba741c79` | open / draft / 미병합 |
| C21I / PR86 | `fe6bbaec2de5032b938aed0713623b9618ba70e6` | `26ab505dac2bfcb0cfd3d049f22bc408f4c86241` | open / draft / 미병합 |
| 새 native 반환 / PR87 | 동일 C21I content | `d3eaf596e46be4f994723fb742237a7399c290ed` | open / draft / 미병합 |

PR87의 첫 evidence content는 `0f2d195aee3c08b372d020bcd6caba87db64a83c`다.
I 문서 head에서 PR87 head까지의 실제 비교는 4 commits ahead, 0 behind,
153개 추가 파일이며 모두 `research/cr_c21ghi_native_execution_20261020/`
아래다. 실행 source 변경은 없다. H content가 I content의 실제 부모라는 기존
관계도 유지한다. PR87의 문서 영수증 안 `observed_document_head`는 영수증 생성
직전 head를 가리키며, 현재 ref를 대신하지 않는다.

새 원본 archive는 아래와 같다.

```text
C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz
2568680 bytes
SHA256 2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3
Drive   1AlRBZ__ZoRYe7MwFE3QbMIvmOHGcKR1u
Dropbox id:BSpOijBcT10AAAAAAD_T4A
```

이번 intake에서 실제 Drive archive를 받아 전체 SHA256을 확인했다. 184개
tar member 중 일반 파일은 156개이고, package payload manifest의 155개
파일은 모두 길이/해시가 맞았다. manifest 자신은 자기 목록에서 제외된다.
포함된 bridge binary도 실제 bytes를 hash했다: 4,888,736 bytes,
`717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30`.
이것은 이전 scratch의 bridge SHA와 다른 새 NCP build다.

Native binary 본체는 archive에 없다. 따라서 native owner
`rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`와 SHA
`1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`는
반환 identity/receipt에서 확인한 값이며, 이 대화에서 그 binary를 다시 hash하거나
실행했다고 주장하지 않는다.

PR87 archive 제작 시점 manifest와 마지막 GitHub 문서 manifest는 서로 다른
snapshot이다. 영수증의 `github_payload_manifest_sha256=62283034…`는 초기
content의 149-entry manifest에 유효하다. 최신 head의 해당 manifest는
151 entries / SHA `4c412626…`, 최신 tree manifest는 152 entries /
SHA `a0a8541c…`다. 과거 영수증의 hash를 최신 파일로 소급 교체하지 않는다.

`evidence/intake/GITHUB_SUMMARY.json`과 `EXTERNAL_SUMMARY.json`은 조회 범위,
후속 관련 repo 결과, 실제 반환물 및 보존 한계를 설명한다. 다른 대화 조회는
Personal Context 서비스의 명시적 오류로 내용을 받지 못했다. 이를 다른 대화에
새 결과가 없다는 증거로 사용하지 않았다. Drive 지정 폴더 57개, Dropbox 지정
폴더 25개 및 Library의 범위 한정 최신 목록/제목 조회와 관련 PR·branch를
확인했다. 계정 전체 또는 NCP disk 전체의 결과 부재를 주장하지 않는다.

## 3. 새 native 실행이 채운 DAG 노드

이전 최종 인계 시각에는 native가 `NOT_RUN`이었다. PR87의 세 COMPLETE
작업은 그 이후 생성된 실제 근거다. 아래 행만 새롭게 충족된 노드로 반영한다.

| PR87 작업 | 실제 native 호출 | job wall (s) | accepted / rejected | 상태 |
|---|---:|---:|---:|---|
| H common_ic / VigilODE / base | 823 | 1.2116977100085933 | 36 / 16 | COMPLETE |
| I common_ic / VigilODE / vectorized / base | 823 | 1.4319355220068246 | 36 / 16 | COMPLETE |
| I common_ic / VigilODE / vectorized / fd_half | 823 | 1.434721386001911 | 36 / 16 | COMPLETE |

각 runner/native exit는 0이며, 저장된 native 응답은 823개 모두 OK다.
기존 실행 합계 2469 calls를 이 대화의 새 실행으로 세지 않는다. 각 작업의
RPC 계수는 RHS400 / Jacobian36 / partial_t36이고 direct factorization은 52다.

선택 입력은 `common_ic`, 범위는 `FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT`,
source 표기는 `PINNED_PR79_MD14_RATE_MANUFACTURED_3_ENERGY_GAS`다.
비광자 chemistry는 원 native provider를 사용했다. Y=0.08130135170951498,
M=9, Δln(a)=1e-4, full/integrated dimension=28/28이며, rtol=2e-11,
alpha=2e-14, max-step divisor=8을 유지했다. 기존 Y=0, Δln(a)=1e-7
제조 입력과 같은 fixture라고 취급하지 않는다.

Fixture의 canonical SHA는
`befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65`이고,
pretty-printed JSON bytes의 SHA는
`bcfb3d5a8b4d5c8153247712eb1c3d127c4410e2455f6106bf60720642d0f060`다.
두 hash는 서로 다른 serialization 계약을 가리킨다.

NCP build 기록의 첫 300 s timeout은 source/compiler 오류가 확인된 실패가
아니다. binary가 남지 않은 첫 시도와, Rust1.94.1로 locked release build를
완료한 별도 두 번째 시도를 모두 보존한다. 성공 compile에는 7m01s가 기록되어
있다. native 실행의 300 s 상한과 compile 소요시간을 혼동하지 않는다. source
호환 patch는 필요하지 않았다. 당시 CPU62 사용 및 CPU55 보호는 과거 admission
관측이며 현재 NCP 배정으로 재사용하지 않는다.

G의 8개 reference + 조건부 4개 계약, 나머지 H fixture/backend 노드, I exact
및 full native/source matrix는 이 세 행으로 완료되지 않는다. C21F 기존 게시
완료와 C21G의 독립 계약, 원 실패/raw/역사 NOT_PUBLISHED는 유지한다.

## 4. 실제 full RHS 요청열을 복원한 방법

독립변수 x=ln(a), 물리 적분 상태는 u=(τ,g,L)로 쓴다. τ는 M개의 광학깊이,
g는 네 gas 변수, L은 15개 누적 장부다. 원 RPC는 scaled z를 보내므로 먼저
원 고정 scale s와의 binary64 곱 u=z⊙s를 복원한다.

RHS RPC 400개만으로 native 호출수를 알 수 없다. Jacobian의 공통 base와
네 gas 열의 양쪽 FD node, 시간 편미분의 base와 양쪽 time node를 모두 넣어야
한다. clamp에 걸린 flat time branch에서는 원 RHS 호출이 없다. 실제 계수는

\[
N_F=400+(1+2\times4)\times36+3(36-3)=823.
\]

각 gas node는 저장된 offset에서 복원하고, 고정 source의 유효 stencil 탐색을
독립적으로 수행해 동일한 bits인지 대조했다. 작업당 288개 node offset은
dyadic rational 차분으로도 정확했다. 실제 두 time node와 flat 분기를
확인했고, 모든 복원 요청에 clamp·exp·density·`.17e` 직렬화를 적용한 native
EVAL 문자열 823개가 원 raw와 모두 일치했다.

C21I cache key는 cell instance별

\[
K=(\operatorname{bits}_{64}(t),\operatorname{bytes}_{64,LE}(u))
\]

다. clamp 전의 t, τ, gas, 모든 passive ledger와 signed zero를 보존한다.
각 cell에서 LRU16을 새로 시작한다.

| Cell | 전체 요청 | full-key hit | full-key miss | native-string hit |
|---|---:|---:|---:|---:|
| 0 | 272 | 23 | 249 | 36 |
| 1 | 279 | 23 | 256 | 28 |
| 2 | 272 | 23 | 249 | 36 |
| 합계 | 823 | **69** | **754** | **100** |

세 작업 모두 이 계수가 같다. 각 cell의 hit 23개는 RHS12 + partial_t base11다.
Gas/time probe의 hit는 0이다. full-key hit 비율은 69/823=8.3839611179%다.
원 JSONL과 손실 없이 압축한 새 복원 자료의 SHA는 `evidence/trace_requests/`의
manifest에 있다.

## 5. native key와 full key에 대한 새 판별 결과

고정 cell/scope에서 full key→native EVAL은 결정적 투영이다. LRU16에서 같은
key의 직전 접근 이후 등장한 서로 다른 key가 16개 미만이면 hit다. 투영은
그 종류 수를 늘리지 않으므로, 같은 baseline 요청열에서 full-key hit 인덱스는
native-key hit 인덱스에 포함된다. 이것은 유한 요청열의 조합적 명제이며,
두 cache를 실제로 중첩한 이후의 hit 수를 뜻하지 않는다.

추가 native-string hit 31개 중 27개는 τ와 passive ledger가 함께 다르고,
4개는 τ만 다르다. time/gas 차이 또는 clamp alias가 원인은 아니다. 고정
time/gas에서 active cohort의 생존량 N=A exp(−τ)이므로 τ→τ+δ이면 해당
photo rate와 heating, photon-work 장부 도함수가 변한다. δ=ln(2)는 그 cohort
생존량을 절반으로 만드는 구체적 사례다. native 비광자 입력은 그대로지만
full optical RHS는 같지 않다.

누적 ledger 값 L 자체는 이 RHS에 되먹임되지 않으며 15개 passive 열은
정확히 0이다. 따라서 추가 31개를 설명할 때 ledger 값 변화 자체를 원인으로
쓰지 않는다. photon-dependent ledger의 도함수가 τ에 의존한다는 것이 정확한
설명이다. 이번에는 보수적인 기존 full key를 축소하거나 native-level cache를
새로 구현하지 않았다.

## 6. callback 재생의 실행 경계와 결과

`replay_callbacks.py`는 원 NativeMicro의 response parser와 density/EOS 검사를
저장된 exact ASCII 응답표에 적용한다. NativeMicro constructor나 native
process를 호출하지 않는다. 중복 key의 상충 응답, 없는 key, 실패 응답은
거부한다. 원 reference가 만드는 RHS closure, H/I callback, bookkeeping을
실제로 계산하며, `subprocess.Popen`과 실제 `scipy.integrate.solve_ivp`는
금지한 상태로 수행한다.

| 저장된 입력 | 재생 callback | reply / binary64 값 | 기록표 조회 | 판정 |
|---|---|---:|---:|---|
| I vectorized base | 원 H | 472 / 40432 | 823 | PASS_SCOPED |
| I vectorized base | I vectorized | 472 / 40432 | 823 | PASS_SCOPED |
| I vectorized base | I vectorized_exact | 472 / 40432 | 754 | PASS_SCOPED |
| I vectorized fd_half | I vectorized_exact | 472 / 40432 | 754 | PASS_SCOPED |

저장된 accepted states를 원 driver에 공급해 종단 장부와 물리량을 재구성했다.
이 states를 새 solver가 적분했다고 표시하지 않는다. JSON 공백까지 같은 wire
bytes라는 주장도 하지 않는다. 비교한 것은 envelope의 유효성, 모든 수치
reply의 shape와 binary64 bytes, FD nodes와 물리 summary다.

같은 초기 solver 상태, 결정적 전이·query 선택, 같은 부동소수점 환경,
동일 numerical reply, 성공한 live admission과 외부 분기라는 전제 아래에는
귀납적으로 같은 adaptive numerical 경로를 얻는다. 이번 replay는 저장된
요청열의 numerical reply 전제를 직접 확인했다. 살아 있는 provider의 liveness,
deadline 및 새로운 환경에서의 실행 성공은 그 밖의 전제다. 따라서 native
exact 실행을 대신하지 않으며 참해에 대한 global error bound도 만들지 않는다.

## 7. 집중 검증과 독립 검토

새 진단에 한정해 다음 근거를 생성했다. 서로 다른 검사를 하나의 fresh
physics suite로 합산하지 않는다.

| 검증 그룹 | 실제 실행 | 의미 |
|---|---|---|
| Trace 구성·LRU·FD·축소 계약 | 새 9 tests PASS | signed zero, full key, cell reset, FD node 복원 등 |
| Replay 입력·RPC admission | 새 16 tests PASS | 고정 pin 권위, 완전 성공 stream, ID/shape/counter 등 |
| Archive manifest admission | 새 6 tests PASS | 고정 권위, payload 변조/미등재 거부, private payload 사전 거부 |
| 보완 후 trace 분석 | 세 저장 작업 PASS, exit0 | 69/823, native 문자열 대응, bitwise/FD 비교 |
| 보완 후 callback replay | 네 경우 PASS, exit0 | 앞 절의 numerical reply와 물리 재구성 |

독립 검토가 확인한 C9-J1은 임의 pin map이 권위를 다시 정의할 수 있던 문제,
C9-J2는 종료 없는 matched prefix나 실패 terminal을 수용하던 문제,
C9-J3는 analyzer가 자체 입력 receipt에만 raw 권위를 의존하던 문제다.
원본 pin SHA와 canonical SHA, 전체 성공 RPC 계약, 고정 package manifest를
추가하여 모두 검토한 최종 버전에서 닫았다. 신뢰된 원본으로 수행한 attempt01의
PASS를 소급 삭제하거나 바꾸지 않았다.

Archive privacy test 첫 시도는 manifest에 inventory가 한 개라는 test fixture
가정 때문에 실패했다. 실제 세 경로를 모두 검사하도록 test만 고쳤고, private
payload를 읽기 전에 거부하는 최종 6 tests가 통과했다. 첫 실패 기록을 보존했다.

최종 실행·검토된 프로그램 identity는 다음과 같다.

```text
replay_callbacks.py  20173 bytes
SHA256 7c855b9983c575042a18754687696a039bef31f5711c455f774b70c03bae52c1
analyze_native_trace.py  30150 bytes
SHA256 e2d8fff3acf4a867391de7247781d2ffe6d3a93ed0ba5c78b26876b911c00b9c
```

Current runtime에서는 Python3.12.14, NumPy2.3.5, SciPy1.17.0으로 재생을
수행했다. Rust/cargo는 실제 probe에서 없었고 C++ compile/run은 통과했다.
이는 현재 scratch 환경의 관측이다. NCP는 별도 환경이며 과거 NCP Python3.12.3,
Rust1.94.1 및 binary identity를 현재 자원 admission으로 대신하지 않는다.

## 8. 수치 민감도와 비용 해석

I FD-half의 전체 endpoint 최대 절대 차이는 thermal coordinate의
2.886579864025407e-15, 고정 scale로 나눈 최대 차이는
2.0285682709290226e-15다. 온도 변화는 −1.8189894035458565e-11 K다.
accepted grid는 달랐다. 이것은 FD 민감도의 작은 관측 차이이며, 참해에
대한 상한 또는 full native cosmological 수렴 판정은 아니다.

| 시간 범위 | H base (s) | I vectorized base (s) |
|---|---:|---:|
| outer process elapsed | 1.91 | 2.12 |
| job receipt wall | 1.2116977100085933 | 1.4319355220068246 |
| reference result wall | 0.8852872390125412 | 0.9776933779940009 |
| instrumented original RHS 합 | 미계측 | 0.581804697 |
| native logged interval 합 | 0.05604552090517245 | 0.05898441682802513 |
| full-key hit 69개에 해당하는 native interval | 0.004690387926530093 | 0.00497811014065519 |

Native log timer는 요청 write/flush와 응답 wait/read까지다. 이후 response
parse/validation, log flush, Python optical RHS 구성 등은 포함하지 않는다.
이 timer들은 포함관계이므로 독립 단계처럼 합산하지 않는다. native interval을
kernel-only chemistry 시간이라고 부르지도 않는다.

기록된 H–I wall 차이는 ΔT=0.2202378119982313 s다. hit 위치에서 생략할 수
있는 전체 원 RHS 비용을 C_j, 추가 cache 비용을 C_cache, 기타 시간 차이를
ΔT_other라 두면 해당 H wall보다 작아질 조건은

\[
\sum_{j\in\mathcal H_{full}} C_j
>0.2202378119982313+C_{cache}+\Delta T_{other}.
\]

Cache/기타 차이를 0으로 둔 단순 조건에서도 69 hit의 평균 비용은 3.19185235ms
초과여야 한다. 이는 전체 823개 original RHS의 평균 0.706931588ms보다
4.515080배 크며, hit 집합이 전체 original RHS 시간의 37.854251% 초과를
차지해야 한다는 것과 같다. per-request 전체 RHS 시간은 저장되지 않았으므로
이는 break-even 조건이지 성능 예측이 아니다.

실제 hit 위치의 native interval 합 4.97811ms만으로 exact의 전체 절감량을
계산하거나 불가능성을 증명할 수 없다. full RHS의 다른 Python/validation
비용도 생략될 수 있고 live cache guard 비용도 추가된다. 이번 결과는 적중
기회와 numerical 재사용 가능성을 좁혔으며, 실제 native exact 한 행이 다음
판별 실험이다. 전체 속도 향상 또는 하락의 일반적 확정은 하지 않는다.

## 9. SciSpace·Exa·Wolfram의 실제 사용

SciSpace에서 chemistry tabulation 원전을 탐색하고 Exa로 저자 소속 Cornell의
Pope(1997) 원 PDF와 Python3.12 공식 `functools` 문서를 읽었다. ISAT의 가까운
다른 입력에 대한 국소 근사와 현재 same-bit exact memoization의 계약을
구분했다. 검색 결과가 지지하지 않는 일반 성능 수치는 도입하지 않았다.

Wolfram에는 context 확인 후 우리 수식·단위·exact decimal rational 산술을
평가하도록 했다. τ 변화에 대한 광자 항등식, native 입력의 τ 독립성, 부호
refinement, opacity/time/thermal 단위와 실제 69-hit 비용 조건을 확인했다.
첫 부호 단순화가 `True`로 끝나지 않은 원 결과와 후속 Reduce/구체적 δ=ln2
검산을 함께 보존한다. 기존 Schur 이론 전체를 다시 계산하지 않았다.

직접 유도한 LRU/투영/adaptive 귀납과 optical key 반례는
`theory/NATIVE_TRACE_EXACT_CACHE_NOTE_KO.md`에 있다. 새로운 strong no-go를
성과로 주장하지 않는다. 문헌 사용 ledger에는 query·시각·URL·채택 이유·원
response SHA를 남겼고, 제공 파일에는 제3자 논문 전체를 복제하지 않았다.
우리 Wolfram evaluator code와 수학 결과는 별도 raw로 보존한다.

외부 원전:

- [Pope, Computationally efficient implementation of combustion chemistry using in situ adaptive tabulation, 1997](https://tcg.mae.cornell.edu/pubs/Pope_CTM_97.pdf)
- [Python 3.12 functools 공식 문서](https://docs.python.org/3.12/library/functools.html)

## 10. R1–R10 / C1–C10과 다음 실행

R1의 범위는 PR87 새 native 반환 이후의 첫 미충족 판별로 고정했다. R2는
기존 C21I 증거와 고정 source를 재사용하면서 다른 저장처/branch의 새 결과를
먼저 수용했다. R3에서 상태·수치·성능·전제를 구분했고, R4–R5는 full/native
key 사상과 LRU, optical 의존성, 조건부 adaptive 동일성을 구성적으로 유도했다.
R6는 독립 복원·원 callback replay·Wolfram, R7은 실제 hit 인덱스와 bit 비교로
판별했다. R8은 유한 범위 PASS 및 성능 미확립으로 판정했고, R9는 두 새
diagnostic과 focused tests로 연결했다. R10은 본 보고서·DAG·게시/백업 영수증·
다음 NCP 패킷으로 재개점을 고정한다. 상세 상태는 theory의 R loop 기록이다.

C1–C4는 baseline/수식-데이터 대응/수치규칙/실행 DAG를 정했고, C5는 새
분석기와 replayer를 구현했다. C6의 집중 검증과 C9의 독립 검토는 앞 절의
실제 실행으로 닫았다. C7–C8은 새 native 적분 없이 저장된 3 native 결과와
재생의 범위에서만 완료다. native exact의 live 실행과 성능은 별도 미충족 노드다.
C10의 게시·백업 성공은 최종 원격 영수증이 있을 때만 COMPLETE로 전환한다.

다음 NCP 작업은 같은 `common_ic / vigilode-rodas5p / vectorized_exact / base`
한 행이다. 현재 CPU/RAM/cgroup/할당·watcher·checkpoint를 읽기 전용으로 확인하고
CPU55를 보호한다. 유효한 반환 bridge를 실제 hash/receipt/runtime 확인 뒤
재사용하며, 실제 native binary는 고정 owner·SHA를 충족해야 한다. 실행 source는
detached C21I content이고 두 PUBLISHED H/I control receipts는 checkout 밖에 둔다.

동시 job1·worker1·fresh process·300s deadline·실제 RHS/native cap200000·
timeout=min(15s,remaining)을 유지한다. H/I 이미 완료한 base와 vectorized FD-half,
옛 제조 suite를 준비 단계로 반복하지 않는다. exact FD-half가 필요하면 먼저 같은
mode의 COMPLETE base가 있어야 한다. G reference ladder는 독립 계약대로 남긴다.
새 Schur/backend 통합이나 큰 physics 기능을 NCP에 맡기지 않는다.

`global_error_bound=null`이며 Full48, full native/MD14 source matrix,
source-age·spectral·angular 수렴, Case B, signed Bianchi, full EoR,
standalone full-driver parity HOLD를 유지한다. native 실행 완료, 수지 확인,
수치 수렴, 성능, 게시와 백업은 끝까지 서로 다른 축으로 기록한다.
