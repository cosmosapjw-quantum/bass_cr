# CR_N4 현재 ref·정책·중앙 DAG 조사 — 2026-10-24 KST

## 결론

현재 bass_cr PR98 head는 `910a9a92e4bf5a9d77b6ff60365d94559f54cbbd`, 중앙 `research/orchestration-sandbox-20261022` head는 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`다. 중앙 head는 사용자가 지정한 고정 인계 commit과 같다. C23C 완료 이후 관련 ref drift는 관측되지 않았다. 이번 작업은 읽기 전용 intake이며 과학 계산·ODE·원격 mutation을 수행하지 않았다.

중앙의 N4는 아직 `plan_status=PROPOSED`, 원 저자 계약은 `status=OPEN`, `execution=NOT_RUN`인 과거 계획 snapshot이다. 이를 갱신할 때 원 계약과 예산을 바꾸지 않고 wrapper에 현재 완료 근거를 연결하는 기존 패턴이 있다. `HE-X1`은 원 `current_unit_selected` 계약을 보존한 채 `plan_status=COMPLETE_SCOPED`와 `observed_completion`을 둔다. N4에도 동일한 구조를 사용할 수 있다.

## 실제 조사 범위

- bass_cr REST heads 176개. 현재 관련 ref는 PR98 C23C, PR96 C21O/C23B, PR97 orchestration CR이다.
- Open PR metadata 97개를 `per_page=100` 한 page에서 수집했다. 가장 최근 갱신은 PR98의 2026-10-23 15:40:00 UTC다.
- 선택 원문 11개, 295,661 bytes의 실제 Git blob SHA1와 size를 모두 대조해 PASS_SCOPED를 얻었다. 파일별 SHA256도 `SOURCE_IDENTITY_VERIFICATION.json`에 있다.
- 다른 대화 전체는 UNAVAILABLE, 외부 host의 현재 process·lease는 UNOBSERVED다. 모든 branch 본문을 읽었다고 주장하지 않는다.

## 적용되는 정책

bass_cr root AGENTS는 완료된 source·입력·전제의 검증 재사용과 변경된 의존성의 targeted 검증을 요구한다. 통상 additive push는 provider ACK, expected commit, exact ref의 실제 `git ls-remote`로 R1을 확인하고 멈춘다. 복원·권위 변경·명시적 byte 검증은 해당 산출물 R3 대상이다. 새로운 실행에는 실제 affinity/cgroup/RAM, coordinator 여유와 thread 제한을 적용하며 누적 raw-attempt 예산을 복제하거나 초기화하지 않는다.

중앙 rei_bianchi root AGENTS는 과학 재현·복원에 필요한 최소 identity를 유지하되 불필요한 보안·증거층 확장을 금지한다. Byte mismatch와 semantic/scientific validity를 구분하며, 근거가 유지된 검토를 재귀적으로 반복하지 않는다. 코드 구현이 필요한 경우 frozen contract 아래 lower-tier 실행과 독립 Astra 결정을 분리한다.

하위 정책 검색은 비잘림 Git tree로 수행했다. 중앙 `research/`, `orchestration_longterm_20261023/`, `assembly/`에 추가 AGENTS가 없다. Recursive 98 entries 중 발견한 두 AGENTS는 `atomic/sources/` 안의 donor 사본이다. bass_cr `research/` 및 C23C root에도 추가 AGENTS가 없고, recursive 352 entries의 `intake/policy/AGENTS.md`는 보존 사본이다. 제안된 N4 addon과 중앙 assembly 수정에는 각 저장소 root 정책이 적용된다.

## 최소 변경안

1. bass_cr PR98에 named C23C frozen-five-label caloric consumer의 `N4_ADMISSION.json`과 입력·유효영역·에너지 소유권 대응을 추가한다. 기존 C23C 과학 결과와 독립 C9를 참조하고 source를 다시 실행하지 않는다.
2. 중앙 `assembly/DAG.json`의 `CR_N4_C23B_CUTOFF_BINDING` wrapper만 scoped completion으로 갱신하고, 외부 C/D/E commit·입력 identity·검토·백업 위치를 `observed_completion`에 연결한다.
3. 고정 인계의 원 저자 계약 block은 그대로 두고 앞부분에 현재 완료와 다음 별도 stopping 노드 안내를 추가할 수 있다. `PR_PLANS_KO.md`에서는 해당 N4 상태 row만 대응시킨다.
4. 40개 저자 계약, 7개 embedded authority, 17개 integration edge, 나머지 39개 wrapper, 기존 HE-X1 완료와 모든 누적 예산을 보존한다. `CR_N4_STOPPING_KERNEL`과 `CR_N5_ATOMIC_ISOTOPE_COVERAGE`는 별도 OPEN이다.

`assemble.py` 전체 재생성은 피해야 한다. 현재 `assemble()`은 wrapper 상태를 PROPOSED/OWNER_*로 재계산하므로 HE-X1의 후속 COMPLETE_SCOPED overlay를 소실시킬 수 있다. 현 DAG의 지정 wrapper만 패치하고 변경 범위의 동등성을 확인하면 충분하다.

Atomic source의 cutoff 등호 처리는 대응표에 명시해야 한다. C23C의 equality-to-thermal 계약에 따라 active measure는 `(Kc,infinity)`, thermal measure는 `[0,Kc]`다. 원 인계의 적분 하한 표기가 원자의 경계 질량을 다른 쪽으로 옮기게 해석되지 않도록 한다.

## 예산과 push 경계

동결 N4 budget의 `inherited_spend`, `remaining`, `currency`는 모두 null이다. Unknown을 0으로 바꾸지 않는다. C23C의 이미 측정한 worker 비용은 복원된 원 receipt로 재사용하며 이 intake에서 재측정하지 않는다. 새 heavy launch·science·ODE는 0이다.

관측된 expected SHA는 bass_cr `910a9a92e4bf5a9d77b6ff60365d94559f54cbbd`, 중앙 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`다. Root는 각 실제 push 직전 변경 여부를 확인하고, ref가 이동했으면 새 변경을 읽어 보존한 뒤 최소 diff를 재기반해야 한다. Force push의 근거는 없다.

## 네 축

EXECUTION: READ_ONLY_INTAKE_COMPLETE_SCOPED. PUBLICATION: 이 작업의 원격 mutation 0, root 담당. BACKUP: 이 작업의 원격 mutation 0, root의 산출물별 receipt가 관리한다. DAG: N4 완료 근거의 wrapper 연결 경로 확인; stopping과 empirical full21 coverage는 OPEN.
