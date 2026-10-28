# C9 예비 정적 검토 — 실제 실행 결과 수신 전

## 현재 판정

**PRELIMINARY_STATIC_REVIEW_COMPLETE / NO_BLOCKING_STATIC_FINDING.**

실제 production energy_sum.py를 원문으로 읽고, 정리의 핵심 연산·증명 certificate·native adapter의 호출 경로를 검토했다. 읽은 구현에서 정리의 결과나 원래 source/consumer 범위를 깨는 blocking defect를 찾지 못했다.

이는 최종 C9 판정이 아니다. 실제 측정된 primary/independent 결과·로그·영수증·실행 source identity를 아직 읽지 않았으며, runtime 검사는 not_run 상태이다. 최종 C9는 C6/C7 산출물에 대한 별도 결과 검토 후 작성한다. 검토자가 과학 코드, NPZ 로더, CAS, test, compilation을 실행하지 않았다.

## 검토 순서와 독립성

독립 reference와 독립 saved-result worker의 authoring을 먼저 끝내고 아래 SHA로 동결한 뒤 production 원문을 처음 읽었다.

| 파일 | 동결·검토 SHA256 |
|---|---|
| reference/generic_dual.py | 58ede1228866a8ca29cce838b7fbfb473c872ea9ef20ec0faf69066df276983b |
| reference/REFERENCE_CONTRACT.md | f58ccd6afdec93d0f947cd905813206299f27740ade0f0e8007c907ff0f46bf5 |
| implementation/independent.py | 99280c5ee8f795b9712db8a3cfffd68f857b9e230d8158e865c43c6965c43744 |
| implementation/energy_sum.py | 6cacfa7ba046ea21740beb91b9fd20797f8c06fa43ea525f0c9a555e933d981a |
| 재사용 event_union.py | 6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d |

기준 unit path는 research/cr_he_energy_sum_20261028이다. reference authoring 중 production의 greedy·deficit helper를 읽거나 호출하지 않았다. reference는 직접 만든 graph의 half-integral dual 전수 열거와 explicit certificate 검사를 제공한다. 이후 production을 읽은 사실은 본 예비 검토부터 기록하며, 동결된 reference/worker 파일을 그에 맞추어 수정하지 않았다.

## 1. 일반 core의 정리 대응

### Exact 입력과 정의역

validate_atoms는 유한 list/tuple 안의 typed Atom, 고유하고 비어 있지 않은 key, 비음수 exact energy·mass, 비음수 정수 partition을 요구한다. exact는 plain int 또는 Fraction만 허용하고 bool·float·str을 거부한다. 이는 README의 core API와 일치한다.

독립 saved-result reader가 Fraction 문자열을 허용하는 것은 저장 형식에서 exact 값을 복원하기 위한 별도 경로다. Production serializer는 Fraction을 문자열로 쓰고, production core가 그 문자열을 자동 입력 변환하지 않는다는 점이 문서화되어 있다. 비교 runner가 먼저 Fraction으로 복원하면 두 계약이 연결된다.

일반 core는 empty input과 E=0을 허용한다. Native adapter는 원래 byte-pinned source validator를 거쳐 원래 cutoff·상한10eV·four partitions를 유지한다.

### Deficit sweep

solve는 양의 질량 atoms를 2E<=K의 low와 2E>K의 high로 분리한다. high는 energy 내림차순으로 정렬한 뒤 groupby로 완전한 동일-energy level을 묶는다. Low prefix pointer는 K-energy의 닫힌 경계를 사용한다. 따라서 같은 energy level의 일부만 tail deficit에 반영하는 문제가 없다.

Maximum positive deficit만 갱신하고, 여러 level이 같은 maximum을 주면 먼저 발견한 threshold를 유지한다. 어느 complete threshold도 dual certificate를 구성할 수 있으므로 이 선택은 유효하다. Zero-weight levels를 deficit 산정에서 생략해도 질량 식은 불변이며, 최종 dual은 zero-weight atoms까지 포함한다.

### Sparse witness와 모든 target

Match는 가장 높은 high와 가장 낮은 남은 low부터 처리한다. 적격 low가 없으면 해당 high를 잔여 single로 남기고 다음 high로 진행한다. 각 positive assignment에서 최소 하나의 residual이0이 되며 low pointer가 앞으로만 움직인다.

남은 low는 coefficient/2의 diagonal, 남은 high는 single로 구성한다. 각 diagonal을 두 marginal legs로 세므로 theorem의 marginal 등식과 맞는다. Requested target이 optimum과 다를 때는 doubles만 target/dmax로 축소하고 atom별 남은 질량을 singles로 채운다.

dmax=0이면 허용 target도0이어서 target==dmax branch를 타며 division에 도달하지 않는다. add와 chosen-event construction은0 coefficient를 생략한다.

## 2. Production certificate 검증

verify는 solver를 다시 호출하지 않고 다음 실제 데이터를 검사한다.

- 재계산한 atom digest와 N·low_mass·high_mass.
- target interval, delta=N-2dmax, maximum positive deficit에 대한 threshold witness.
- 전체 atom key를 정확히 한 번 덮는 half-integral dual.
- 실제 maximum·selected events의 양의 coefficient, 고유 ID, known legs, pair cap, exact atom marginal.
- Maximum double mass = declared dmax = weighted dual objective.
- Target double mass 및 single mass N-2target.
- At most n_positive maximum events와 at most2n_positive target events.

Threshold가 high라는 검사가 있으므로 tail energy>=threshold 합에는 low가 끼지 않는다. 조건부 cap의 equality와 모든 loop는 exact Fraction 비교로 처리된다.

### Group-minimum dual 검사

Production dual 값은0,1/2,1로 제한된다. 어떤 두 dual-value group의 합이1 미만이면, 그 두 group에 허용 edge가 존재하는지 여부는 각 group의 최소 energy 두 개의 합으로 정확히 결정된다. 같은 group에서는 최소-energy atom을 자기 자신과 짝지을 수 있어 loop 조건을 검사한다. 따라서 group minima 방식은 모든 허용 edge·loop 제약을 포함하고, zero-weight vertices도 검사 대상이다.

동결된 reference의 native checker는 다른 경로를 사용한다. Energy 정렬 후 각 atom의 전체 allowed-neighbor prefix에서 최소 explicit dual 값을 찾아 모든 제약을 검증한다. 이 경로는 dual이 half-integral 또는 특정 threshold 형태라는 가정을 하지 않는다. 두 구현 모두 graph 전체에 대한 논리적 coverage를 제공하며 sampled pair 검사가 아니다.

실제 source와 모든 saved witness에 대한 두 경로의 runtime 일치는 C6/C7 결과에서 확인해야 한다.

## 3. Native adapter와 once-only 반환

_native_module은 재사용 event_union.py의 SHA를 확인한 뒤 처음 import하고, 그 실제 module을 cache한다. Native source는 이 module의 원래 NPZ byte-verified loader를 통해서만 attestation을 얻는다.

_native_atoms는 이전 source validator, provenance kind,3201 atoms, 원래 atom-content digest를 확인한다. 새 atom_content_id의 tuple 구성과 Fraction serialization은 원래 event_union.py와 일치한다. 따라서 같은 pinned atom sequence의 digest를 비교하는 경로다.

bind_cap은 exact K와 명시적 nonempty assumption, canonical source SHA, NPZ SHA, atom digest, 같은 state, predecessor SHA와 actual-physical-K null을 함께 digest로 묶는다. validate_cap은 전체 expected dictionary와 비교하므로 변경·누락·추가 필드가 검출된다.

consume_native는 다음 순서로 처리한다.

1. Source/cap identity와 solution cap digest·K를 확인한다.
2. 일반 certificate를 verify한다.
3. nb가8750/47인지를 검사한다.
4. 원래 proper window와 explicit binding을 확인한다.
5. 모든 four partitions의 원래 claims를 만들어 original consumer를 한 번 호출한다.
6. 성공 후 해당 window의 inventory intersection을 반환한다.

실제 proper factor W는 original consumer가 적용하고, wrapper가 event coefficient에 별도 W를 곱하지 않는다. 새 source normalization, RR, retained photon, EOS/transport 계산을 호출하는 경로는 없다.

원래 neutral inventory gate가 성공 반환 전에 실행된다. 반환하는 lower endpoint는 max(0,N-Hneutral/W)이며 그 조건을 우회하지 않는다. Native wrapper가 full four-partition claims를 요구하므로 p=0 species·chemical 범위가 보장된다. Original API의 partial selection은 보존된다.

## 4. R6 findings의 구현 반영

| R6 finding | 실제 반영 지점 | 예비 상태 |
|---|---|---|
| F01 algebraic interval과 inventory | original consumer 호출 후 native_inventory_double_interval 반환 | 정적 반영 확인 |
| F02 p=0 범위 | full four-partition claims 강제; original partial API 유지 | 정적 반영 확인 |
| F03 stored cutoff 대 decimal cap | core exact int/Fraction, 2E<=K와 pair sum<=K | 정적 반영 확인; boundary 실행 대기 |
| F04 C와 d 구별 | cross_C_scope=CHOSEN_WITNESS_ONLY_NOT_MAX_C | 정적 반영 확인 |
| F05 general/native 정의역 분리 | 일반 Atom 검증과 attested native adapter 분리 | 정적 반영 확인 |
| F06 dmax=0·zero events | zero optimum division 회피, zero event 생략 | 정적 반영 확인; runtime 대기 |

현재 정적 검토에서 새로운 수학적 수정 요청은 없다.

## 5. Independent worker와 bounded runner 연결

implementation/independent.py는 positional OUTDIR을 받아 OUTDIR/RESULT.json을 create-only로 쓴다. optional --input으로 saved primary certificate path를 바꿀 수 있으며 기본 input은 runs/primary_v1/PRIMARY_CERTIFICATES.json이다. run_bounded.py가 사용하는 positional 호출 형식과 일치한다.

Worker는 saved primary JSON의 unit,48 small cases의 reference IDs·순서·energy/weight/K,9 native cases 및3201 native atoms를 검사한다. Generic oracle dmax, maximum certificate, chosen target certificate를 별도 groups로 기록한다. 모든 scalar는 exact하게 복원하며 production import나 NPZ load를 하지 않는다.

Max events와 selected events가 구조·값까지 같고 target=dmax이면, 같은 atom/K/dual/event 인자에서 얻은 maximum certificate를 명시적 identity reuse로 target group에 연결한다. 나머지 target은 reference를 실제 호출하도록 되어 있다. 동일한 검사를 반복하지 않는 이유와 참조 group이 RESULT에 남는다.

정상 inventory에서 explicit group 수는 global4 + small48×4 + native9×3 =223이다. 이 수는 reference 내부의 모든 require 문 개수를 뜻하지 않는다. fresh/reused/failed/not_run을 구별한다. PASS 조건은 모든 cases 처리, 실패0, not_run0이다.

run_bounded.py의 원문은 단일 worker·single native threads·CPU/address-space/wall 제한, 실행 source snapshot과 전후 identity 비교, 실패 attempt의 charge 보존, measured coordinator+worker CPU 및 conservative tail을 기록한다. Aggregate preventive hard-cap proof는 false라고 명시되어 있다. 실제 예산·성공 여부는 실행 영수증을 읽은 뒤 평가한다.

## 6. 최종 C9에서 확인할 남은 실제 근거

다음은 미실행 작업을 예비 static PASS로 대체하지 않기 위한 결과 연결점이다.

1. Measured primary·controls·independent runs의 exit code, RESULT status, stdout/stderr, source unchanged 및 실행 source SHA.
2. 48 small oracle comparisons와 manual anchors, 특히 stored cutoff 두 cap의 구별.
3. Native9 saved cases 전체의 exact marginal·pair support·dual optimum과 K3 half-target의 별도 verification.
4. Malformed scalar·삭제 event·wrong pair·forged dual·source/state/window/nb/replay negative controls의 실제 결과.
5. Native proper-window/partition composition·inventory rejection·physical nulls의 실제 반환.
6. 해당 새 unit budget의 실제 누적 측정·tail·실패 기록과 remaining status.

이 목록의 실제 근거를 읽기 전에는 C9를 complete 또는 implementation-verified로 표시하지 않는다. Metadata/provider CPU는 unmeasured/null이며 검토자가 새 scientific execution이나 다른 owner budget을 사용하지 않았다.

