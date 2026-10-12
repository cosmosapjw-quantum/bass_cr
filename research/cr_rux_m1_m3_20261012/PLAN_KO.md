# BASS_CR 연구계획 재편 — 첨부 RUX DAG 반영

2026-10-12 · 현재 단위 `CR-RUX-M1-M3-REUSE-20261012`

## 연구 방향

**현재 사용할 수 있는 원자·침적·지연 응답을 정확한 범위에서 연결하여, 실제 소비자의 가열·이온화 오차를 먼저 판정한다.** 기존 M0 및 이차 응답과 native CR OFF 구현을 재사용한다. 원래 BASS_CR의 원자 산란·포획·지연 연구는 독립 경로로 유지하고, 응용의 CR OFF baseline과 모든 원자 정밀화 작업 사이에 자동 선행관계를 두지 않는다.

연구 상태와 전체 물리 실행 상태는 [NEXT_DAG.json](NEXT_DAG.json)과 [전역 overlay](REI_ATOMIC_REUSE_DAG_CR_OVERLAY_20261012.json)에 각각 명시되어 있다. 전역 노드의 현재 실행 소유자와 `PROPOSED_NOT_EXECUTED` 상태를 보존한다. 이번 CR 국소 완료가 전역 RUX00 또는 RUX03 전체의 완료를 뜻하지 않는다.

## 1. 즉시 이어갈 경량 연구

| 순위 | 작업 | 실제 출발 근거 | 완료 조건 |
|---|---|---|---|
| 1 | `M1_ELECTRON_SOURCE_BINDING` | PHYS01/02 injection·Rudd 계보, `Qe(W,t)=t A(W)`, 기존 M0와 native receiver | 실제 요청 하나의 spectrum·시간기저·초기 stock·bath·연산자·단위주입 정규화를 대조한 호환/비호환 표 |
| 병행 | `CR_PROCESS_RELEVANCE` | source가 있는 RUX02/RUX04 후보와 CR owner matrix | CR OFF의 제한된 baseline 또는 실제 필요한 hard-particle 과정 선택; 미상 source를 0으로 대체하지 않음 |
| 병행 | `M1_CONSUMER_ERROR_BUDGET` | 선택된 소비자의 실제 관측량 정의 | 절대/상대 tolerance, 양의 분모, `H0 q*/P_ref`, source 이력/곡률 또는 이차 잔차 bound 지정 |
| 다음 | `M2_PHYSICAL_CLOSURE_DECISION` | 위 binding 및 예산 + 이번 M2 결과 | 동일 domain에서 정확 이차 functional, 잔차 제어 이차 근사, 조건부 평균 지연 중 예산을 충족하는 방법 선택 |

산술 도구는 이미 구현·검사되었다. 다음 담당자는 먼저 현재 자료에 있는 source constructor와 electron source 정의를 읽고 정확한 변환표를 작성한다. 빈 field를 임의의 물리값으로 채우지 않는다. 입력 부족은 구체적인 field와 source 소유자까지 좁혀 기록한다. 기존 결과로 닫히는 질문에 새 G, 범용 adapter 또는 동일 suite 재실행을 붙이지 않는다.

이차 source이면 `P=H0 q*(a p+b R+c S)`를 먼저 사용한다. 일반 C2 source의 `P+=H0 p q(TR/p)`는 `H0 q* C+κ`가 지정된 가열 오차 예산 이하일 때 선택한다. 불연속 이력이나 evolving bath에 이 상계를 그대로 쓰지 않는다. 실제 `ΔTg`, `Δxe`, `Δτ`까지의 전파는 receiver 방정식에 연결해야 한다.

### binding 산출물의 필수 열

| 대상 | 반드시 구분할 내용 |
|---|---|
| Proton injection | proper/comoving, angle 적분 유무, `dK`, 전체 source 정규화 구간과 active collision 구간 |
| Electron birth | `W` 구간, 두 birth tag, `Qe(W,t)` 시간기저, Rudd 선택과 source lineage |
| M0 response | selected_record / birth_defined, `H0`, `p,R,S`, 고정 `T=10^10 s`, 고정 bath/operator |
| Native terminal packet | source/bath knot, heat·internal ionization·escape 채널, 실제 constructor 메타데이터 |
| Consumer | 실제 source history, 초기 stock, 시간좌표, heat 단위, observable denominator와 tolerance |

기본 금지 변환은 `terminal FS10 heating × M0 p`다. 동일 proton source 파일을 공유한다는 사실은 이 변환의 증명이 아니다. 기록된 `xi=0.1` terminal packet을 `xi=0.01` M0 kernel의 새 composition 결과로 해석하지 않는다.

## 2. 전역 RUX DAG의 선행조건

첨부 DAG의 `RUX00 → RUX02/RUX03 → RUX04` 출발 구조를 유지하되, source와 process owner가 준비되면 `RUX03_CR_SCREEN`에서 실제 필요한 CR 과정을 먼저 판정한다. 이 노드는 scenario freeze인 RUX04의 선행조건이다. CR을 켠 시나리오에는 `RUX13_BIND`를 RUX04/05/07 전에 요구한다. 그 후 FLRW와 Bianchi-I의 물리 구간 및 이력, tau/visibility, 실제 산출물 그림으로 진행한다.

`RUX13`의 matched-history 영향 비교는 baseline 이후에 남긴다. 이렇게 해야 source 관련성 판단과 정규화 연결은 일찍 수행하면서, CR 효과의 수치 비교에는 같은 조건의 실제 baseline을 사용할 수 있다.

| 선택한 물리 주장 | 최초 구간의 추가 선행조건 | RUX16 공개·승격의 추가 근거 |
|---|---|---|
| CR OFF scoped baseline | relevance에 OFF 범위와 owner 명시 | 실제 OFF 선택 이력 영수증과 기본 RUX11 산출물 |
| CR ON | RUX13_BIND | RUX13_BIND + RUX13 |
| HE precision | 해당 domain·provider의 실제 사용 조건 | RUX12 |
| HH process | 해당 process의 실제 사용 조건 | RUX14 |
| spatial topology | 공간 모형의 별도 물리·수치 조건 | RUX15 |

추가 확장의 선행조건은 **선택한 주장에만** 적용한다. CR OFF baseline에 CR 정밀화 완료를 자동 요구하지 않는다. 반대로 CR ON 또는 확장 물리를 포함한 결과가 해당 근거를 건너뛰고 release로 가도록 두지 않는다. `main_nodes`는 주요 노드의 집합이며 전부 직렬로 실행하라는 일정표나 실측 critical path가 아니다.

원 DAG의 S15는 point photon-stock 근거다. 이번에는 실제 source를 확인한 CRX01–05를 추가하여 primary photon bridge, native hard-particle snapshot, M0, current receiver, 새 M2 진단을 구분했다. S01–S17 전체 원격 payload나 물리 입력 archive가 이번에 모두 검증되었다고 주장하지 않는다. overlay의 `supplied_evidence_boundary`는 첨부 원 DAG가 기록한 당시 조사 범위를 그대로 보존한 값이다.

## 3. 원자 과정의 중복 계산을 피하는 계약

광흡수 사건은 광자수 감소, primary 이온 생성, binding energy 및 photoelectron excess energy에 한 번씩 대응한다. electron degradation을 켜면 photoelectron excess를 즉시 전부 열에도 더하지 않고, 선택 모형의 heat·secondary ionization·excitation·stock·escape로 분할한다. CR OFF라고 baseline primary 광가열이 꺼지는 것은 아니다.

Case A의 explicit recombination photons와 Case B OTS는 동일 재결합 광자 집단에 대해 선택한다. local HI absorption과 effective mean-free-path도 동일 흡수 사건을 중복 소유하지 않게 한다. 서로 다른 영역이나 absorber 집단을 명시적으로 나눈 항까지 전역 XOR로 금지하지 않는다. 단위 및 owner 상세는 [ATOM_OWNER_MATRIX.json](ATOM_OWNER_MATRIX.json)을 따른다.

## 4. 이미 완료한 작업의 재사용

M0 cached onset과 이차 응답은 원 파일을 그대로 읽는다. 이번 exact postprocess와 독립 reference 결과는 모두 저장되어 있다. native OFF 함수와 historical negative control의 동일성도 기록되어 있으므로 새 OFF wrapper를 만들지 않는다. 선택된 최신 receiver history가 실제 실행될 때 source 0 및 provider-call 0 영수증을 그 실행에 묶는다. 그 후속 영수증은 receiver 소유자의 작업이며 현재 BASS_CR 경량 연구를 막지 않는다.

기존 point/wide atomic 결과와 BASS_HE·HH의 scoped 성과는 각각의 claim ceiling을 유지한다. 원자율의 정확도, 열 가중 kernel의 수치오차, runtime 정상종료, physical EoR admission, 원격 backup 성공은 서로 다른 근거다.

## 5. 독립 CR 연구 및 NCP의 조건부 경로

`M4_TARGETED_CR_EXTENSION`은 다음 둘 중 하나가 구체화되면 활성화할 수 있다. 실제 소비자가 필요로 하지만 현재 결과에 없는 에너지·bath·채널·시간 범위가 확인되었거나, 원래 BASS_CR의 독립 원자·산란 질문이 명시적으로 선택된 경우다. 후자는 전체 REI 완료를 기다릴 필요가 없다. 필요한 출력, 기존 자료로 해결할 수 없는 이유, 최소 검증 및 비용 상한을 먼저 고정한다.

새 고비용 실행은 계산량이 실제로 원격 자원을 요구하고 source·resource·예산이 연결되었을 때만 dispatch한다. 준비된 H 패키지가 있다는 사실로 H를 자동 실행하지 않는다. 기존 F operator-binding 실패를 새 진단의 성공으로 복구 처리하지 않는다.

| 보존 대상 | 현재 상태 |
|---|---|
| H 전체9600 신규 실행 | DEFERRED_OPTIONAL |
| H 원 계약 | 최대 8 build, 76,800 column, 누적 900초, 자동 retry 0 |
| 실제 미수집 H 결과 | 실제 존재하는 경우에만 원 source·예약과 묶어 수집 |
| F 및 dependent G frontier | operator binding HOLD / BLOCKED |
| PHYS02_DELAY | OPEN |
| production_history | HOLD |
| atomic_G02 / all_bound / b_grid | UNRESOLVED / OPEN / NO_GO |

이번 단위에는 새 NCP 과학 작업이 없다. 이전 전체 H handoff ZIP의 이름·크기·SHA256·Drive/Dropbox ID는 [HANDOFF.json](HANDOFF.json)에 보존한다. 이번 경량 단위 ZIP은 현재 코드·입력·결과·검토를 포함하는 범위별 전달물이며, 이전 약 68 MB H payload 전체를 다시 담은 복원본으로 부르지 않는다.

## 6. 재개 순서와 종료 기준

먼저 `REPORT_KO.md`, `HANDOFF.json`, `review/DECISION.json`을 읽고 현재 scoped 완료와 남은 physical gate를 구분한다. 그 다음 M1 binding의 누락을 기존 source 파일로 좁힌다. 실제 source와 observable 예산이 묶이면 기존 exact 응답 또는 이번 상계로 충분성을 판정한다. 부족하면 그 부족의 원인에만 맞춘 M4 계약을 만든다.

이번 루프의 종료 기준은 새 M2 유도·구현·실행·독립 범위 판정과 실제 소비자 조사, 첨부 DAG의 조건부 의존성 재편, 재개 가능한 전달물이다. 전체 CR 연구나 전체 EoR 물리 문제가 해결되어야 이번 경량 루프를 닫는 구조로 만들지 않는다.
