# C22D 최신 refs·외부 결과·원격 게시 조사

관측: 2026-10-22 14:42:48–14:52:06 UTC (23:42:48–23:52:06 KST).
역할: read-only intake. 과학 코드 실행, 외부 쓰기, 업로드, 원시 궤적 다운로드, ODE 재실행은 모두 0이다.

## 1. 최신 refs와 권위

GitHub REST `/git/matching-refs/heads/` 실제 응답은 7개 저장소 합계 **1271 heads**다.
이는 Git wire advertisement 수가 아니다. 직전 C22C의 06:34 UTC REST snapshot
1259개 대비 **+12 added / 3 changed / 0 removed**다. 이전 1246→1255(+9)
및 이후 조사 이력은 별도의 시간층으로 보존한다.

| 저장소 | 직전 | 이번 | 추가 | 변경 | 삭제 |
|---|---:|---:|---:|---:|---:|
| bass_cr | 173 | 175 | 2 | 0 | 0 |
| rei_bianchi | 262 | 263 | 1 | 1 | 0 |
| bass | 265 | 266 | 1 | 0 | 0 |
| BASS_HE | 91 | 92 | 1 | 0 | 0 |
| WU088_HH | 143 | 145 | 2 | 0 | 0 |
| rec_bianchi | 138 | 141 | 3 | 1 | 0 |
| vigilode | 187 | 189 | 2 | 1 | 0 |

전체 exact refs/SHA는 `API_LIVE_REFS.json`, 변화는 `LIVE_REF_DELTA.json`에 있다.
기준 파일 SHA256은 `0ee500305bb0c3547702f401d21369d9980f7aa33a6f5d4886c8c67674801eda`다.

[PR96](https://github.com/cosmosapjw-quantum/bass_cr/pull/96)과
`research/cr-c21o-hheli-z2-sandbox-20261021`의 실제 head는 여전히
**R `a5e12c5f3e6d323e211d65fefad34060ec07eff0`**이며 open/draft/unmerged다.
Science C, historical D, recovery R 및 C21O execution identity는 기존 권위층 그대로 보존한다.
C22C local commit `286d459f101eaeea0bebfda28bb0a8cfb4ceccf5`가 이 branch에
게시되었다는 ACK는 관측되지 않았다.

새 BASS_CR 원격 결과는 다음 세 층을 섞지 않아야 한다.

| 층 | 실제 원격 상태 | 의미 |
|---|---|---|
| durable evidence | `5750489be6ad80b4e142f5712c656c33ae07f097`, R의 직접 자식, README 한 파일 추가 | C22C archive/local commit/tree를 가리키는 문서 게시 |
| PR97 diagnostic | `15fd250ab91574bd4f3348e91d739a15a6ed6005`, R의 직접 자식, [PR97](https://github.com/cosmosapjw-quantum/bass_cr/pull/97) open draft | recovered C22A/B와 별도 `cr_c22c_excitation_diagnostic`; ODE 0인 저장 경로 진단 |
| 현재 local C22C science | `286d459f101eaeea0bebfda28bb0a8cfb4ceccf5`, tree `10d2b4d63ddf3642beb9ac80e2515a7677829545` | `cr_c22c_h1_excitation`의 4개 새 coupled trajectory; 위 diagnostic과 다른 연구 단위 |

durable branch는 [원문 README](https://github.com/cosmosapjw-quantum/bass_cr/blob/5750489be6ad80b4e142f5712c656c33ae07f097/research/cr_c22c_durable_evidence_20261022/README.md)
자체가 full C22C source publication을 주장하지 않는다. 그 branch를 head-filter로 조회한
PR 목록은 빈 배열이었다. README 제목의 “Draft PR”만으로 PR 생성 ACK를 추정하지 않는다.

14:50 UTC repo metadata의 permissions는 admin/maintain/push/triage/pull 모두 true다.
이는 read-only 권한 metadata이며 Git 쓰기 성공 증거가 아니다. 과거 create_blob의
UNKNOWN_NO_ACK를 permission denied나 성공으로 재해석할 수 없다.

## 2. 선택 text의 실제 검증 범위

새 의존성과 관련된 text **15개, 113097 bytes**를 선택했다. 모든 파일에서

1. pinned commit의 directory metadata상 path/size/Git blob SHA를 확인했다.
2. contents endpoint와 git/blobs endpoint의 decoded UTF-8 bytes를 대조했다.
3. 실제 byte length를 포함하는 Git blob SHA1을 계산해 원격 SHA와 일치시켰다.
4. 저장 bytes의 SHA256을 기록했다.

**15/15 PASS**이며 최종 binding은 `SELECTED_TEXT_BINDINGS_V2.json`이다.
V1은 최초 metadata 가시성 한계를 보존한 기록이고 V2는 모든15개의 independent
directory size 확인을 보충한다. 첫15회 contents 응답을 raw JSON/base64로 잘못
가정한 로컬 parser 오류는 교정했다. 이는 원격 fetch 실패나 과학 실행 실패가 아니다.
외부 결과의 수치값은 아래에서 **OWNER_REPORTED**로 취급한다. 원시 NPZ·ODE·전체
campaign 검증 또는 전체 source 코드 검토를 했다는 뜻이 아니다.

## 3. C22D 물리·최적화에 유용한 새 외부 정보

### REC omitted budget: CI 에너지·입자수와 source domain

[REPORT](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/04c0b10c1f1ec38d57c751369c553b638979e453/research/rec_thermal_omitted_budget_20261022/REPORT_KO.md)
및 frozen contract는 HG97 H I/He I/He II CI source accuracy domain을
**1e4–1e9 K**, H I/He II CE를 **5e3–5e5 K**로 명시한다.
저온 계수의 기본값은 지원 거절이며, continuation은 별도 요청과 mask가 있는
고정 경로 후처리다. 계수 부재를 물리적 0으로 대신하지 않는다.

CI event rate가 `r_i = ne C_i Yi`일 때 운동에너지 소스
`Qkin = -nb Σχi ri`와 binding 소스 `Qbind = +nb Σχi ri`가 상쇄된다.
CI 자체에 radiative escape를 붙이지 않는다. 입자수 증가를 포함한 직접 온도
강제항은 `δ(dlnT/dx) = -Σri[1 + 2χi/(3kBT)]/(Hη)`다.
새 전자 항의 누락은 별도 물리 오류다.

OWNER_REPORTED fixed-path 결과는 REC thermal8의 872개 저장 상태에서 actual-U
hot Compton 약 −2.576~−2.592 eV/baryon, H I CE 약 −0.00132,
CI kinetic 약 −2.06e-5 eV/baryon이다. 이는 다른 ensemble의 source priority이며
C21O/C22C 에너지 budget에 합칠 수 없다. 새로운 ODE는 해당 외부 단위에서도0회로
보고한다. actual-U hot term, 별도 Planck reference, UV recoil/thermal term을 분리한다.
다음 최대8개 full63 Compton-coupled IVP는 계획이며 완료 결과가 아니다.
He I CE/metastable와 Li CI/CE는 미공급 상태다.

### HH1 D energy adapter: 하나의 potential과 chain rule

[HH1 theory/result](https://github.com/cosmosapjw-quantum/WU088_HH/blob/6c3b12554288893d5d7e221d77be943324285ceb/research/hh1_d_energy_adapter_20261022/HH1_THEORY_AND_RESULT.md)
는 `I_D = I_H + 43 k_B K`인 선언된 rounded model의 PI/RR event ledger를
제공한다. PI는 binding +I_D, gas +(E−I_D), radiation −E, electron +1이며,
RR은 binding −I_D, gas −e_capture, radiation +(I_D+e_capture), electron −1이다.
온도식은 `dT/dt = -2HT + 2q/(3kBN) - T(dxe/dt)/N`이다.

C99 O(1) adapter와 exact-input rational oracle의 유한 검사 PASS가 owner 보고되어
있으나 D threshold/cross-section/RR moment의 일관된 physical provider admission은
아직 없다. H threshold와 D threshold 사이 광자를 D 이온화에 재사용하면 안 된다.
Low-T CI source node는 NEXT_OPEN이다. 이 adapter의 대수·비용과 solver speedup은
구별해야 한다. `hh-phys80-sandbox-reduction` 새 ref는 이전 HH79와 같은 SHA이므로
branch 이름만으로 새 과학 결과를 추가 집계하지 않는다.

### REI sandbox: 구조 단순화와 실제 timing의 차이

[REI report](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/2f9ebff30c7505e425179862819f212ddbd07542/research/rei_coupled_isotope_sandbox_20261022/REPORT_KO.md)
의 OWNER_REPORTED 결과는 기본156개 검사와 별도2개 source-onset 검사다.
21 populations를 보존한 charge-block 공유와 electron-feedback rank-one Jacobian을
구현했다. 고정 T/UV/nB와 물리 영역에서 rank-one denominator d≥1을 유도하지만,
전체 condition number나 핵·열 결합 Jacobian의 보증은 아니다.

동일한 국소 작업을 비교한 실제 owner microbenchmark는 prepared RHS **3.78배**,
64-state vectorized RHS **36.25배**를 보고한다. 반대로 Python 공유block+rank-one
선형계는 dense21보다 **3.39배 느려서 dense가 기본**이다. 계수 객체는 T/스펙트럼이
바뀌면 다시 준비해야 한다. 이 수치는 현재 C22D 환경의 측정치도 전체 궤적 speedup도
아니며, compact62→33 대수 축약의 speedup으로 재라벨할 수 없다.

새 nuclear onset은 제조 rate와 제조 energy ledger의 검사이며 실제 nuclear
rate/Q 정확도나 전체 결합 network 완료가 아니다. `n/T=0` 상태의 생성 방향을
보존하는 absolute abundance 표현과 missing/structural-zero/underflow 구별은
C22D에서도 유용한 인터페이스 계약이다.

### REC RR moment: derivative fit와 독립 energy moment 구분

[thermal moments report](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/892aad5c3e9fb0b2abd021154b62a42c39277125/research/rec_thermal_moments_20261022/REPORT_KO.md)
는 temperature-independent kernel 및 Maxwellian 조건에서
`L_RR = kBT(3α/2 + dα/dlnT)`를 유도한다. 그러나 empirical α의 값 오차만으로
미분 오차가 제한되지는 않는다. Primary는 parent number rate를 유지한
`kBT α_parent f_Mao2017` hybrid이며 derivative 식은 별도 민감도 모델이다.
Source lock은 Mao, Kaastra & Badnell (2017), DOI10.1051/0004-6361/201629708,
CDS J/A+A/599/A10의 calc/pars table을 지정한다. 이번에는 그 원표 bytes를
다시 다운로드하거나 native coefficient에 채택하지 않았다.

### 별도 C22C diagnostic과 현재 C22C science

PR97의 별도 diagnostic은 SW91 fit의 2000K 이상 구간에서 old C22B 201표본 중
71표본/70인접구간, elapsed duration2.15755%를 사용해
0.0489597873 eV/Href 조건부 excitation loss를 보고한다.
새 ODE/RHS0이며 C22C local의4개 coupled trajectory를 대체하지 않는다.
SW91 polynomial boundary의 원래 작은 jump를 smoothing하지 않았고,
domain 밖은 unavailable이다. 이 값은 전체 궤적 적분·오차상한·source
negligibility 증거가 아니다.

## 4. 외부 미완료·실패 이력의 보존

- REI220/BASS180 compact33 mirror, 125grid+2cancel+2full62oracle,
  최초127 JSON 실패·재적분 이력과 representative raw4의 PASS_SCOPED 범위는
  이전 검증대로 보존한다. 이번 intake는 raw0이며127 전체 재감사로 승격하지 않는다.
- REI219 live PR은 open draft unmerged이며 head
  `6a12f3865d9ea427c1391c41caed8bb7cb7ec00d`다. 현재 owner body는 DD 및
  conditional18-family 단위와 delivery C10 완료를 보고하지만
  COUPLED_ISOTOPE_NATIVE_PRODUCTION은 HOLD_DEPENDENCIES다.
  이전 incomplete campaign 기록과 새 scoped owner claim을 별도로 둔다.
- HE85 live PR은 open draft unmerged이며 head
  `16a424b7290f484c57e97c8ed74f81e6d2043782`다. 현재 owner body는
  392nominal+2L24 scoped pilot delivery를 보고한다. 잃은 원래 NPZ 때문에
  394 scientific identities를 recovery rerun했다는 사실도 명시한다.
  이는 원래 bytes 복원이 아니다. 이번에는 raw를 확인하지 않았으므로
  OWNER_REPORTED로만 기록하며 과거 unfinished/recovery 기록을 지우지 않는다.
  Full thermal/nuclear admission과 동일시하지 않는다.
- VigilODE P02 C6FAIL을 유지한다. 새 production-review provenance receipt는
  historical reference availability FAIL(14 unresolved identifiers,
  53 failing citations/27 unchanged files)을 명시한다. 새 review subset의
 53 citations PASS와 전체 저장소의 FAIL을 분리한다. 이는 evidence availability
  결함이지 이 text 조사에서 새로 판정한 numerical failure가 아니다.
- 접근할 수 없는 이전 대화 원문은 **UNAVAILABLE**이다. 사용자 handoff 및
  접근 가능한 저장소 문서를 대화 원문의 재독으로 표현하지 않는다.
- 원 핵반응 network PNG는 **NOT_RECOVERED_NOT_READ**다.

## 5. 백업·게시의 다음 최소 경로

기존 C22C authority63194bytes SHA256
`fb7a965396735a23e5967d1d5846f1b853b2829551df508c7583a007bb33ffa8` 및
terminal receipt55086bytes SHA256
`e32f254ff2703b27f9c378ab65291eb64400968a14a2f0e847bcca72540694df`의 실제
Library+Dropbox R3 완료를 parent authority에서 재사용한다. 이 child가 새
download/upload/Drive 검사를 했다는 뜻은 아니다. C21O 원 recovery ZIP의
Library size/SHA/CRC PASS, Dropbox ACK+ID+size/byte-readback NOT_RUN이라는
별도 원래 상태도 소급 변경하지 않는다. Drive 보존 확인은 계속 OPEN이다.

원격 durable README는 C22C archive114019304bytes SHA256
`b8e3448a8cdba0f0b8512dc241098a1829400c37064917048d8438788655c3fb` 및
Git bundle41491791bytes SHA256
`cbccac84b68d1c58261eef931ae01bce7543ec15892dc1203d2d5da5135a1f79`를
참조한다. 원격 문서 자체는 source publication ACK를 대신하지 않는다.

최소 게시 경로는 검증된 archive/bundle을 기존 R base object가 있는 격리 checkout에
import하고 exact local commit/tree를 확인한 뒤, 실제 source/data/figure가 있는
별도 branch를 create-only로 게시해 응답과 원격 tree를 확인하는 것이다.
현재 R/PR96 또는 다른 agent의 PR97을 덮어쓸 필요가 없다. 실행 완료 계산을 복원
목적으로 재적분할 필요도 없다. exact original commit 전송과 connector가 만든
equivalent-tree commit을 사용하는 경우를 분리해 기록해야 한다.

## 6. 네 축

| 축 | 이 intake의 실제 상태 |
|---|---|
| EXECUTION | READ_ONLY_INTAKE_COMPLETE_SCOPED; text15 integrity PASS; external raw0/code0/ODE0; 원래51개 NCP 재실행0 |
| PUBLICATION | targetR/PR96 unchanged; 별도 one-doc5750489 및 PR97 diagnostic 확인; full local286d 게시ACK 없음; write0 |
| BACKUP | 이전 actual C22C Library+Dropbox R3 증거 재사용; 새백업0; Drive OPEN; triple backup 완료 주장 없음 |
| DAG | 최신의존성 intake COMPLETE_SCOPED; C22D rate-domain/energy ownership/optimization 계약에 위정보 전달; full physics HOLD와 global_error_bound=null 유지 |

과학 채택 여부, C22D 새 입력·run ID, 실제 자원·lease 및 worker1thread 계약은 parent의
해당 연구 단계에서 결정한다. 이 intake가 외부값을 자동 채택하거나 어느 science gate를
해제하지 않는다.

