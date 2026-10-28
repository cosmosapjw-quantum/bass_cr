# R8 — 주장별 채택과 열린 물리 입력

단위는 CR_PHYS02_HE_EVENT_UNION_V1이다. 이 단계는 완결된 유도와 재사용 가능한 근거를 주장별로 판정한다. 이 문서 작성 시 새로운 numerical runtime admission은 아직 없다. R7의 실제 symbolic identity 결과와 원 응답은 root가 별도 단계 기록에 결속한다.

중앙 기준은 실제 관찰 22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes / 17 edges다. 이번 CR의 중앙 집계 효과는 0이며 각 단계의 실제 게시 시점 preflight를 우선한다. Local theory 진척을 중앙 physical completion으로 더하지 않는다.

## 주장별 판정

| 주장 | 판정 | 근거와 적용 범위 | 후속 행동 |
|---|---|---|---|
| μ=S+2π₁D의 유한 원자 사건 표현 | DERIVED_SCOPED | 대칭 D의 총질량은 double 사건 수이며 각 사건은 electron leg 두 개를 갖는다. [R5 전체 유도](../theory/THEORY_KO.md) | Exact event representation의 계산 계약으로 사용 |
| Disjoint birth partitions의 parent union 보정 | DERIVED_SCOPED | C=2Σᵢ<ⱼD(Aᵢ×Aⱼ), species correction=(+C,0,−C), ionic charge correction=−2C | Atomwise·species·charge 검증의 기준식으로 사용 |
| 0≤C≤min(N/2,N−maxᵢnᵢ) | DERIVED_SCOPED | 고정 finite atomic marginal과 nonnegative single/double measure family. N=0 및 dominant block의 모든 경우 포함 | 같은 family의 exact bound로 사용 |
| 양 endpoint와 전체 중간 interval의 달성 | DERIVED_SCOPED | All-single, half-shift 및 convex mixture의 직접 구성. [R4 예](R04_RESULT_KO.md) | Witness generator의 검증 목표로 사용 |
| C와 전체 double count의 구별 | DERIVED_SCOPED | Diagonal-double은 C=0이면서 전체 double count=N/2일 수 있다 | C를 d_U로 대체하는 구현을 거절 |
| 같은 marginal에서 C의 비유일성 | DERIVED_SCOPED_WHEN_CMAX_POSITIVE | C_max>0이면 두 endpoint witness가 서로 다른 C를 준다. C_max=0의 퇴화 경우를 구분한다 | 조건부 family의 식별 한계를 명시 |
| Same-state per-baryon species와 chemical 보정 | CONDITIONAL_DERIVED_SCOPED | explicit n_b=8750/47m⁻³와 고정 recipient binding convention에 한정 | Missing n_b의 native fields는 null, 다른 nonnull n_b는 거절 |
| q=tA의 finite proper-history scaling | REUSED_INPUT_AND_DERIVED_SCOPED | Proper [0,10¹⁰]s 안에서 F[a,b]=(b²−a²)/2. 구간 밖은 unknown | 정상화와 clock을 다시 곱하지 않고 실제 구간만 사용 |
| 저장 source와 attribution의 identity | REUSED_ACTUAL_BYTES | [입력 manifest](../inputs/INPUT_MANIFEST.json), source/closeout 복구 영수증의 정확한 bytes | 실제 pinned NPZ를 읽는 제한 실행으로 결속 |
| 새 코드의 static 준비 | READY_FOR_RESERVED_REFERENCE_RUN | [R6 독립 관찰](R06_INDEPENDENT_STATIC_OBSERVATION.json), F01–F03 static closed/runtime pending | 예약된 primary·controls·independent 실행 |
| 새 numerical/runtime accuracy | PENDING_ACTUAL_EXECUTION | 문서 작성 및 static AST 확인은 수치 실행 증거가 아니다 | 실제 raw results, attempt 비용과 실패를 보존해 판정 |
| 실제 exclusive He 분포와 actual C_cross | INPUT_UNSUPPLIED_NULL | 현재 source는 inclusive electron marginal이다. Witness를 실제 joint distribution으로 식별할 입력이 없다 | actual_exclusive_event_measure=null, actual_C_cross=null 유지 |
| Actual full-source physical native25 및 EOS/T | INPUT_UNSUPPLIED_NULL | Partner response, donor work, 실제 bath/EOS 등 필요한 입력이 없다 | actual_full_native25=null, actual_T=null, full physical activation=false 유지 |
| 광범위한 novelty 또는 strong no-go | NOT_CLAIMED | 문헌 최초성·전체 물리 문제의 불가능성을 판정하지 않는다 | 기존 구성과 제한된 새 결과만 사용 |

## 실제 값과 witness 값을 구분한다

저장 NPZ를 정확히 읽어 만든 marginal은 실제 입력이다. 그 marginal에 맞추어 구성한 all-single·diagonal·half-shift 사건들은 조건부 mathematical witnesses다. 각각의 witness에서 계산한 D, C, species increment와 native component는 해당 witness의 값으로 표시한다. 이를 actual exclusive D 또는 actual C_cross로 옮기지 않는다. 실제 joint 분포는 null이며 null을 영측도나 C=0으로 대체하지 않는다.

He source-ion 포트의 exact correction은 완결된 수학이다. Full-source physical native25의 미완료는 그 보정을 무효화하지 않는다. 해당 partial return을 같은 상태의 조건부 소비자에 사용하면서 물리적으로 미공급인 성분을 분리해 유지한다.

## 계속 진행할 작업

고정된 finite-atomic theorem과 계산 계약을 채택하고, 준비된 구현이 그 계약을 따르는지 실제 bounded 실행으로 판별한다. 입력 bytes 불일치, event claim 누락, mixed state/frame/clock, support 확장, 잘못된 n_b와 시간 중복은 거절할 대상이다. R7의 한정 CAS 검산은 정확히 평가된 항등식만 뒷받침하며 실제 source 또는 물리 입력을 생성하지 않는다.

이 단계의 문서 작성은 과학 실행이나 원격 게시를 수행하지 않았다. 단계 Git·dual backup의 완료는 root의 실제 단계 영수증으로 판정한다. Metadata/provider/publication CPU는 unmeasured이며 0으로 주장하지 않는다.
