# C03 — exact 표현, 오차 경계, sparse 구성과 독립 oracle

단위: `CR_PHYS02_HE_EVENT_UNION_V1`. 상태: 수치 표현·알고리즘 계약을 문서화함. 이 시점에서 scientific runtime은 NOT_RUN이고, 아래 검사는 구현된 계획이다.

## Fraction.from_float의 정확성과 물리 오차

`load_pinned_source`는 SHA256이 고정된 NPZ의 두 float64 배열을 읽는다. 각 저장된 binary64 E_j와 A_j를 `Fraction.from_float(float(x))`로 옮기므로, 이미 저장된 binary64 값의 유리수 표현은 정확하다. 새로운 Decimal string 반올림이나 float reduction으로 값을 바꾸지 않는다. 이후 marginal, finite proper-time factor, event union, species·charge·chemical correction은 Fraction 연산으로 계산한다.

이 exactness는 원래 연속 source physics가 오차 0이라는 뜻이 아니다. 선행 model-identified attribution은 자체 입력·원래 허용 기준을 갖는다. 계약의 inherited atom tolerance 2e-11은 이전 identity로 재사용하며 새 fitting·projection을 실행하거나 더 작은 source-model error를 주장하지 않는다. 이번 새 exact 결과는 그 고정된 저장 marginal에 대한 대수적 결과다. `primary.py`의 source_model_error는 inherited accepted attribution tolerance를 남기고 새 certified source uncertainty interval을 제공하지 않는다.

특히 cutoff는 decimal rational 1/10로 재정의하지 않고 `Fraction.from_float(.1)`로 고정한다. 별도 ghost row가 그 exact 저장 경계에 있다. active partition의 1,3,10 eV 경계는 정확한 정수이고, ghost를 active bin으로 재표기하거나 native energy support 밖으로 확장하면 거절한다. zero는 exact zero이고, 작은 양수를 cutoff tolerance로 지우지 않는다.

`CONTRACT.json`의 독립 report relative tolerance 1e-12는 완화하지 않는다. 현재 `independent.py`는 직렬화된 rational 값 자체에 exact equality를 사용하므로 이 단계의 acceptance는 해당 허용치보다 엄격하다. 그림의 float 변환과 표기 자릿수는 표시용이며 산술 acceptance나 원본 RESULT를 바꾸지 않는다.

## Sparse half-shift 구성의 비용과 퇴화 경우

양의 coefficient를 가진 atoms를 partition 순서와 원래 atom 순서로 안정 정렬한다. 누적 mass coordinates 0=x_0<...<x_K=N에서 x와 x+N/2를 짝지어 [0,N/2)를 적분한다. 원래 경계와 N/2만큼 이동한 경계를 모아 exact breakpoints를 만들고, 인접 breakpoint마다 unordered two-leg event 하나를 저장한다. 같은 partition의 연속 block 배치가 dominant-bin 경우에도 sharp cross envelope를 달성하게 한다.

저장량은 atoms, cumulative edges, breakpoints 및 sparse events 모두 O(K)이다. K×K 행렬을 생성하지 않는다. 구현은 atom 정렬과 breakpoint 정렬을 수행하므로 일반 비교 연산 수는 O(K log K)이고, 정렬 후 두 index sweep은 O(K)이다. 이를 전체 CPU가 O(K)라고 기록하지 않는다. Fraction의 분자·분모 bit length에 따른 산술 비용도 별도이며, 이 문서는 runtime/RSS를 측정한 benchmark가 아니다. sparse segment 수는 O(K), 보수적으로 2K 이하의 규모다.

| 경우 | 실제 코드 경로와 불변량 |
|---|---|
| N=0 | 양의 atom 목록이 비면 빈 event list; sharp bound 0 |
| 일부 atom 또는 bin의 mass=0 | zero-weight atoms를 cumulative edges에서 제외; 원 marginal의 exact 0은 유지 |
| 한 bin만 양수 | double event는 가능하지만 cross C=0 |
| max(n_i)=N/2 | exact breakpoint 비교; epsilon 분기로 어느 쪽에 임의 배정하지 않음 |
| max(n_i)>N/2 | minority mass N-max(n_i)가 cross bound; 나머지 double은 within-bin에 남음 |
| 같은 atom 두 leg | event weight를 두 번 marginal에 더함; event count는 한 번만 셈 |
| 겹치는 이동 경계 | set과 exact 비교로 동일 breakpoint 제거; 0 길이 event를 만들지 않음 |

sharp envelope의 C와 total d를 구분한다. diagonal-double witness의 d=N/2, C=0이 이 구분을 드러낸다. half-shift witness도 total d=N/2이며 C는 min(N/2,N-max(n_i))이다. 이 family의 sharpness는 실제 scattering kernel의 realizability나 통계적 confidence interval을 뜻하지 않는다.

## 실행될 controls와 독립 reference

`controls.py`는 작은 exact fixture만 사용한다. balanced/dominant/exact-half/zero/single-positive-bin, 두 leg factor, 잘못된 nb, 겹치는 proper windows, support·state·frame·isotope, source digest·canonical label forgery, claim completeness, conflicting IDs, negative/nonfinite, finite inventory 등의 수용·거절 사유를 확인하도록 구현되어 있다. fixture는 `ALGEBRAIC_FIXTURE`이고 canonical source나 실제 exclusive measure가 아니다. 계획된 check를 아직 PASS 수로 세지 않는다.

독립 reference `independent.py`는 production `event_union`을 import하지 않는다. 실제 pinned NPZ를 별도로 읽어 exact atom digest를 계산하고, primary의 공개 half-shift witness를 데이터로 읽는다. 각 사건에서 HeI→HeII 또는 HeI→HeIII 전이를 직접 합산해 union과 partition 별 species·charge·chemical 차이를 비교한다. 3201 atom별 marginal과 대칭 D의 2-leg normalization을 별도로 확인한다.

sharp bound의 작은 독립 oracle은 4개 bin의 모든 n_i in {0,1,2}, 총 81 경우에서 6개 cross edge의 multiplicity를 exhaustive dynamic programming으로 탐색한다. capacity는 2n_i, event mass 단위는 1/2이며 unused capacity는 single event로 남긴다. optimum 탐색에 proposed min-formula를 쓰지 않고, 구한 optimum과 그 식을 나중에 비교한다. 이 half-unit 표현은 총 N이 홀수일 때 가능한 반정수 optimum을 integer-only oracle이 놓치지 않게 한다. degree feasibility와 실제 edge assignment도 저장한다.

81개 유한 사례는 일반 정리의 대체 증명이 아니다. 일반 sharpness는 R6의 별도 exact 구성에 의존한다. 새 실행 결과는 이후 `runs/*/RESULT.json`과 `RECEIPT.json`으로 판정하고, 원 실패와 수정은 개별 identity로 남긴다.

근거: `../implementation/event_union.py`, `../implementation/controls.py`, `../implementation/independent.py`, `../CONTRACT.json`, `R06_RESULT_KO.md`, `R06_INDEPENDENT_STATIC_OBSERVATION.json`. 중앙 참고 baseline 28/88; 이 문서의 중앙 집계 효과 0.
