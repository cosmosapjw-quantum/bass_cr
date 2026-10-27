# R2 근거 재사용 지도 — 새 부모 사건 단위

상태: root의 R2 게시에 사용할 intake용 지도. 이 파일 자체로 R2 완료나 계산 실행을 선언하지 않는다.
단위 CR_PHYS02_PARENT_EVENT_NATIVE25_V1, 선행 PR110 CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1.
선행 S2eed7ef835c55ee17e4ce96e0eda7fe8d82dc47c / D616b166fa0108ca35defece3f8c9d99fc79895cb / M42cc3a909688d670200ba09c500e2ca83a94fa10.
최소 실제 파일은 INPUT_SOURCE_MANIFEST.json의17개 record로 결속한다. manifest는 source 파일을 복사하거나 생성하지 않는다.

## 동일 identity/scope에서 재사용

| 근거 | 재사용 내용 | 유지할 범위 |
|---|---|---|
| PR109 canonical source JSON, SHA8fca44… | 실제 direct_0p1_10의3200 active+1 cutoff atom, q=tA, [0,1e10]proper time, family/birth partition | aggregateA/E bytes 불변. 원 parent target label은 저장되지 않음. |
| PHYS02A/B/Rudd/injection source와 actual9600 lineage | actual1–4MeV source recipe, neutral .99 factors, proper729의 once-only 소유, source basis, common W support, original projection | source constants를 새 RR상수로 치환하지 않음. 기존 source/G 재실행0. |
| 저장된 PHYS02A6개 band moments | 3개 recovery anchors/3개 미사용 holdout | 새 계수는 MODEL_IDENTIFIED. 저장 coefficient raw bytes를 발견했다고 하지 않음. |
| 저장 PHYS02C coverage/actual9600 receipt | source construction의 grid-independent identity, common endpoint2154.927725029828eV, 기존 scale | grid-independent는 source constructor에 한함. 전체G bytes는 없으며 복원하지 않음. |
| PR110 primary RESULT SHAae8452… / ARRAYS SHA2c3624… | four prefixes/four bins, active/cutoff/Coulomb/H·He RR/retained photon, exact finite-history response | total cohort response 그대로. target-parent origin별 response를 새로 전파한 결과가 아님. |
| PR11046 accepted control obligations,112 primary flags,517 independent comparisons | 이전3200-state response의 검증 | 새 source attribution/native25 composition의 검증으로 자동 계산하지 않음. |
| PR110 conditional H1/He4 inventory | totalnH140,nHe1085/94,ne2849/1880,nb8750/47,T100K | 이전PR109 nbnull불변. REC/HE/WU/PW19/별도REI state 미수입. |
| 실제 native25 source d91de629… 및 REI storage835707… | coordinate order, charge-minus-fast 의미, chemical basis, hidden-energy 표현의 선례 | 기존foreign state/nb/history/thermal/photo/RR kernel을 실행하거나 활성화하지 않음. |
| 이전 publication/R3/C9/실패 영수증 | provenance와 scope-trust chain | 원 실패·UNKNOWN_NO_ACK·resource/plot/oracle 비용·all-attempt-PASS=false 유지. |

## 변경 의존성만 새로 다룰 부분

1. 알려진3 basis와 저장 moments에서 target attribution coefficients를 식별하고, conditioning/positive-domain/unused-anchor/actual atom checks를 수행한다.
2. target density와 proper factors가 포함된 원 aggregate에 추가 density·729·4π·clock을 다시 곱하지 않도록 새 입력/소유권을 검증한다.
3. 실제 H parent extent와 He inclusive yield를 구별한다. s,p,d family 및 선택 밖 partner/잔류 excitation ports를 새로 유도하고 native25 partial response로 사상한다.
4. source H13.605693122994, RR13.60, recipient chemical I*의 차이를 explicit sidecar로 보존한다.
5. default cutoff retention과 명시적으로 선택한 conditional caloric assimilation을 구현한다. actual partner/branch/donor point가 없으면 full physical native25 point를 null로 유지한다.
6. 새 두 부분 baseline+increment 표현과 event dedup/finite-window controls, 별도 저자의 계산·review를 수행한다. 완료된3200-state propagation/기존 검토를 재실행하지 않는다.

## 오래된 숫자나 표현을 재사용할 때의 주의

PHYS02A의 primary_causal_turn_on에 있는 H/He all-W 누적 수는 low-selected 양이 아니다.
He의 기존 'primary ionization' label은 지금 읽은 inclusive electron-production source의 모형 functional로 해석해야 한다.
그 label만으로 독점 HeI→HeII 사건을 확정하거나 all-W 누적값을 low parent count에 대입하지 않는다.
기존 바이트와 당시 판정은 그대로 보존하고, 새 semantic qualification을 별도 기록한다.

PR110 cutoff의 E=.1 direct atom은 low projection ghost다. 실제 W<.1 source를 계산한 것으로 바꾸지 않는다.
PR110 Coulomb·cutoff energy는 새 consumer의 EOS를 명시하기 전에는 full physical-heating 결과가 아니다.
같은100K 숫자를 가진 legacy all-electrons-thermal FS10 packet은 fast-electron native25 상태와 같지 않다.
새 conditional temperature endpoint를 계산하더라도 원 frozen100K hazards나 시간응답을 소급 수정하지 않는다.

## 예산·gate 및 검토 독립성

선행 단위 charged24.692011/40, 순수측정14.616973, tails10.075038, 잔여15.307989는 NONTRANSFERABLE이다.
새40 CPU-s는 preparation/worker/coordinator/tails/실패를 포함한 별도 한도다.
C4 이전 과학 실행·CAS·old replay0이며 root가 새 actual host admission/manifest/실행승인을 관리한다.
본 작성자는 선행PR110 theory/reference 저자이고 새 이론/입력식별 제안자다. 본 작성자 자신의 증명·reference가 독립검토를 대체하지 않는다.
source_qualification의 R6 및 별도 production 결과 검토와 역할을 구분한다.

현재 중앙 관찰28/88,88nodes/17edges,이번CR effect0.
N4/N5 PARTIAL_OPEN,N6/N7 PREDECESSOR_GATED,L4=false.
개인 대화 전체 검색 UNAVAILABLE, Drive complete inventory NOT_ESTABLISHED.

