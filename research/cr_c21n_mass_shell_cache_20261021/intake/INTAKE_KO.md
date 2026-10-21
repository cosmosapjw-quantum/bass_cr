# C21N 최신 외부 결과 수용

**준비된 NCP 98개는 다른 실행에서 이미 완료됐다. C21N은 이 결과를 다시 적분하지 않는다.**
실제 [PR92 HEAD](https://github.com/cosmosapjw-quantum/bass_cr/commit/645a7f1a960be10e10574a819d7fb35a4511d9fa)의
원 source·격자·manifest와 다운로드한 98개 case 영수증을 대조했다. 원 raw의 canonical
identity는 일관되지만 일부 문서의 identity 표기, CSV의 줄바꿈 bytes, archive 파일 수에는
불일치가 있다. 원 파일을 바꾸지 않고 [추가 정정 기록](NCP98_CORRECTION_RECORD.json)에
올바른 값과 수용 범위를 고정했다.

| 상태축 | 이번 intake에서 확인한 상태 |
|---|---|
| EXECUTION | 읽기 전용 수용 감사 완료. 신규 ODE·benchmark 0. 외부 NCP98은 완료 반환 수용. |
| PUBLICATION | PR90·91·92와 관련 외부 refs를 실제 조회. 이 intake 파일은 C21N의 추가 게시 자료이며 이 agent는 push하지 않음. |
| BACKUP | 새 NCP98 archive를 backup 담당 agent가 1회 다운로드하고 전체 SHA256·archive manifest·raw seal을 검증. 새 upload 0. |
| DAG | 기존 27 + 반환 98 = 125점 완료 자료를 사용. 새 초기응력 sweep를 자동 제출하지 않음. 일반 triaxial·full reionization·CMB·전역 오차 상계는 HOLD. |

## 1. 조사 범위와 실제 refs

동일한 7개 저장소의 광고된 branch heads를 이전 1,224개와 비교했다. 현재 1,232개이며
신규 8개, 변경 5개, 삭제 0개다. [LIVE_REF_DELTA.json](LIVE_REF_DELTA.json)은 이전
inventory의 SHA256과 각 변경 전후 SHA를 보존한다. 모든 branch의 모든 파일이나 공개되지
않은 대화를 읽었다는 뜻은 아니다. 노출되지 않은 대화·private host 반환은 `UNAVAILABLE`이다.

| 권위 대상 | 확인한 HEAD | 의미 |
|---|---|---|
| BASS_CR PR90 | `e954467132eef864a0fb86ba5de44f90f76b08e0` | C21L 성분 분석의 문서 마감 |
| BASS_CR PR91 | `b78a943e5d7ae341bbfe84f742a06a4ac36d0e43` | C21M 신규26 + 재사용 중심1 |
| BASS_CR PR92 | `645a7f1a960be10e10574a819d7fb35a4511d9fa` | 완료된 NCP98와 결합125 반환 |
| HH128 | `92f5ab9dba531ebe05909dcb77d3740d2c68c580` | shear memory와 유한 L8의 8→3 표현 |
| HH129 | `b76fd4b5d0dfe4850ebde66a8a10f78402d36c00` | 과거 standalone 구현·배송 회수 보충 |
| HH76 새 branch | `f61f23aee6ee70d0710fae2e98fae0f93f2394bb` | time transport 계약 4파일; 새 결과는 아직 없음 |
| REI214 / BASS177 | `98fcf3943fa54e089b0292d166c3a47becb5edb8` / `4f19e6eaf50e8458d59d27ff47f03e9d8c8b22ca` | 같은 ACCEL01의 두 게시처 |
| REC117 | `e79fca7b53aba2e99ea94fe2b4e498056da117be` | 외부 z20→2 이력 소비 계약 |
| HE82 | `048a73de4246f609b1bc14854ea5c48757cb82fd` | 기존 checkpoint보다 추가된 코드·완료 보고 |
| VigilODE 후속 branch | `5fd6e459a3f67cee90e002821b9b4b740c47475b` | 별도 FV oracle·Schur·remap 연구 |

전체 입력·solver·build·runtime·검증 범위와 재실행 방지 판단은
[C21N_EXTERNAL_INTAKE.json](C21N_EXTERNAL_INTAKE.json)에 있다. 실제 읽은 응답의 hash는
[READ_SOURCE_MANIFEST.json](READ_SOURCE_MANIFEST.json)에 기록했다.

## 2. NCP98 수용과 정정

PR92는 C21M 문서 HEAD의 직계 후속으로 3 commits ahead, 0 behind다. 전체 Git tree diff는
추가 511개와 변경 1개다. 변경된 기존 파일은 `analyze_campaign.py`이며 그림 패널 크기와
셀 라벨 font size만 달라졌다. 원 builder·RHS·runner·vendor 및 기존 26개 raw는 바뀌지 않았다.

고정 입력은 `grid_ncp_refinement98.json`의 SHA256
`768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04`와 정확히 같다.
물리 source는 REI `3b85dedce84d37b3e165da00685a8a984950aafe`, 실행 source는
C21M content `659c94312eb9c12ebb987de934459c12a63d67b0`다. Python 3.12.3,
NumPy 2.3.5, SciPy 1.17.0, FP64, 원40상태·101저장점·DOP853
`rtol=3e-11`, `atol=3e-13`를 기록한 반환이다.

실제 raw canonical run identity는 다음이다.

```text
7f89b12adbeee64a70832e633ae563584bc2a68f6ac433dc56f759a1946eb718
```

Canonical JSON을 직접 SHA256으로 계산한 값이 MANIFEST, RETURN 및 98개 COMPLETE·RESULT·
RESERVATION·STARTED에 모두 일치한다. 98개 case target은 준비된 격자와 정확히 같고,
원 source·manifest·vendor hash 비교 15건도 일치했다. 이 15건은 중복 builder 검사를
포함하므로 서로 다른 파일은 14개다. [source/identity 검토](NCP98_SOURCE_IDENTITY_REVIEW.json).

보존할 불일치는 세 가지다.

1. 원 보고서·실행 영수증·독립 검토·인계문은 identity의 뒤쪽을
   `...ac2a60139b98efacb01c05a`로 잘못 적었다. 해당 문서는 불변 보존하고 raw의 올바른
   identity에 이번 수용을 결속한다.
2. `endpoints_campaign.csv` 실제 파일은 LF 126개, 100,645 bytes다. 원 output manifest는
   CRLF 표현의 100,771 bytes를 기록한다. 메모리에서 줄바꿈만 바꾸면 기대 SHA256과
   정확히 일치한다. 숫자나 원 파일을 변경하지 않았으며 **원 manifest 7개 모두 bytes
   일치라는 주장은 수용하지 않는다**. 실제 결과는 6/7이다.
   [bytes 감사](NCP98_OUTPUT_MANIFEST_BYTE_AUDIT.json).
3. 원 backup receipt의 `payload_files=614`는 회수한 archive에서 재현되지 않는다.
   실제 regular files는 509개이며, SHA256SUMS 1개와 그 manifest의 payload 508개다.

새 archive SHA256은 `e9baa6bab57790d29a0dfb06747a3304f0449a48e7dfc2d14c6630849f9c1d0a`,
크기는 17,911,591 bytes다. 이번에는 Dropbox 사본을 실제 다운로드했다. 원 문서에 기록된
Drive ACK·다운로드 검증은 그 문서의 과거 증거이며, 이 intake가 Drive 재다운로드까지
수행했다고 확대하지 않는다.

NCP site는 실행자가 선언했고 hostname `s1a0e5abed09`가 별도로 기록됐다. worker CPU는
61개, coordinator CPU0, 보호 CPU55는 사용하지 않았다. 기록된 wrapper wall 13.18초와
RETURN 내부 wall 10.298729851초는 서로 다른 범위의 단일 실행 기록이다. 속도 개선율이나
64-core scaling 측정으로 해석하지 않는다. 현재 시점 NCP 가용 자원은 새로 관측하지 않았다.

## 3. 외부 방법의 재사용 판단

[HH128 원 보고서](https://github.com/cosmosapjw-quantum/WU088_HH/blob/92f5ab9dba531ebe05909dcb77d3740d2c68c580/research/hh_phys75_sector_memory_20261021/REPORT_KO.md)는
기존 1,231개 long collisionless 이력과 별도 HH63에서 signed matter/radiation의 shear 기여를
적분했다. 이는 같은 coupled trajectory의 경로별 기여이며 종을 제거한 인과 실험이 아니다.
유한 L8의 constant matrix를 이용한 `E=exp[(b-bi)M]Ei`도 구현했지만, adaptive error norm이
8상태와 3상태에서 달라진다. 3개 신규 입력의 paired control 6개는 이미 완료됐으므로
다시 실행하지 않는다. C21N의 원40상태 solver를 이 표현으로 대체하지 않았다.

[ACCEL01 원 구현](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/526870b3e36ad8354c58c761567b1b37829033b2/research/rei_sigma_pi_acceleration_20261021/cached_context.py)은
C15 모델별 exact binary64 `(x,b)` LRU와 bytes-backed 불변 배열 및 metadata guard를 쓴다.
이 파일은 implementation pin과 최신 delivery pin에서 byte-identical이고, 공개된 검증 및
실제 smoke snapshot의 source hash도 같다. 반면 worker의 실행 snapshot과 후속 validator
source는 다르므로 둘의 실행 증거를 합치지 않는다. C21N이 고려하는 **A와 무관한
CanonicalMomentumFV 격자 생성 자료의 재사용**은 이 C15 state-value cache와 다른 수명이다.
불변 backing·정확한 identity guard를 참고하되 물리 owner를 바꾸지 않는다.

해당 원문 3개는 [PRIMARY_SOURCE_SNAPSHOTS.json](PRIMARY_SOURCE_SNAPSHOTS.json)에 결속했고
각 Git blob SHA를 확인했다. `primary/`의 파일은 읽기 전용 참고 사본이며 이 intake에서
실행하거나 production import에 연결하지 않았다.

[REC117 계약](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e79fca7b53aba2e99ea94fe2b4e498056da117be/research/rec_rei_trajectory_reuse_20261021/CONTRACT_KO.md)은
외부에서 완료됐다고 보고된 237개 z20→2 중 175개 nominal grid를 소비한다. 현재 원격에는
계약·source-lock 4파일만 있고 새 raw는 다른 scratch snapshot의 hash로만 연결돼 있다.
이번 대화에서 원본 source·실행·raw는 `UNAVAILABLE`이다. C21M125와 nominal 초기좌표는
3개 겹치지만 종단 z와 저장시간 격자가 다르므로 동일 전체 trajectory라고 판정하지 않는다.

[HE82 보고서](https://github.com/cosmosapjw-quantum/BASS_HE/blob/048a73de4246f609b1bc14854ea5c48757cb82fd/research/he29_rei_pilot_20261021/RESEARCH_KO.md)는
28개 원 계산과 독립 성분 12개를 합한 40개 완료를 보고한다. 새12개의 입력은 C21M125와
겹치지 않는다. 그러나 보고서가 가리킨 `data/source_identity.json`과
`data/reviewed_source_manifest.json`은 관측 HEAD에서 실제 404였다. 완료 보고와 구현
근거는 수용하되, 회수하지 않은 raw를 독립 검증한 것으로 만들지 않는다.

VigilODE의 새 FV oracle은 prescribed geometry와 unpolarized elastic Thomson의 별도
first-order 모델이다. 공개된 12개 formula checks는 그 범위의 검산이며 C21M collisionless
40상태 적분의 대체 검증이 아니다. Live BASS/REI port와 production은 계속 HOLD다.

## 4. C21N의 유용한 다음 단위

완료된 125점과 원40상태 이력을 재사용하면서, A에 독립적인 canonical grid·moment 준비의
불변 재사용을 구현하고 A에 따른 weight·cell population·정규화는 정확히 다시 만든다.
별도의 이론 목표는 초기 signed matter/radiation 상쇄가 풀리는 국소 mass-shell 응답이다.
이는 HH75의 경로 적분 attribution, HH76의 all-node 시간 수송, REC117의 z2 consumer와
구별되는 기여다. 새 source의 변경 의존성만 focused 검산하며, 원 ODE·FP64·quadrature·
reduction 순서·허용오차를 보존한다. `global_error_bound=null`을 유지한다.
