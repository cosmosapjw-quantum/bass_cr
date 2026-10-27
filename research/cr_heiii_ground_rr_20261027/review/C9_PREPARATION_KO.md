# C9 독립 검산기 준비

상태: **PREPARED / SCIENTIFIC_NOT_RUN**. 이 준비 작업에서 C9 PASS를 주장하지 않는다. 파일 작성과 `py_compile`만 수행했다. 실제 실행은 C7/C8 산출물이 준비된 후 root의 C9 dispatcher에 속한다.

## 파일과 독립성

`c9_independent.py`는 생산·provider 모듈을 import하지 않는다. NumPy는 NPZ 자료를 읽고 저장된 binary64 결과의 배열을 다루는 데 사용한다. 기준해는 별도로 작성한 scalar Decimal70 tridiagonal LU와 전진/후진 대입으로 계산하도록 구현했다. 새 reference 코어를 먼저 작성한 뒤, 새 production export/config/dispatch의 실제 schema를 정적으로 읽어 이름과 경로를 맞췄다.

원 source row, 이전 HeI FROZEN 계약, PR104/PR106 필드와 R6에서 읽은 native25 원자료가 기준이다. 기존 H1/HeI solve, generator, source projection 및 quadrature를 재생하는 코드가 없다. K0에서 새 w RHS 하나를 푸는 것은 이번 새 진단에 해당한다.

## 고정된 수치 검산

- 두 finest case `chi1.5_R80_N2048`, `chi3_R80_N2048`를 검사하며 실제 n은 배열 길이에서 읽는다.
- 각 case는 18 physical + 5 conditional + 4 stored-column response + 1 w로 28개, 총 **56 RHS**다.
- K1은 `Decimal.from_float(stored_HeI_Kdiag) + Decimal.from_float(new_lambda)`로 만든다. rounded K1을 Decimal로 바꾸어 대체하지 않는다.
- 기존 16개 physical RHS는 immutable binary64 값을 재사용한다. 새 λE 및 stable λ×stored-column 곱은 Decimal에서 만들고, conditional RHS는 독립 기준 probability를 사용한다.
- 각 해 열 자체의 infinity norm으로 **5e−10**을 적용한다. 큰 time/energy 열을 공통 분모로 쓰지 않는다.
- 사전 고정 sample indices는 각 n에 대해 `{0,n//4,n//2,3n//4,n−1}`다. native HeII 표를 직접 읽어 독립 Decimal 식으로 PI/RR/speed/hazard를 계산하고 **5e−13**을 적용한다.
- 저장 matrix/RHS/alias 일치, positive pivots, independent rare bound, stable signs 및 componentwise backward residual도 검증하도록 구현했다. 수치 실행 결과는 아직 없다.

## source와 integrated export

두 finest case × 세 z의 **6개 actual source row**를 저장된 source projection에서 직접 적분한다. 실제 24개 export의 case/z 집합, ID uniqueness와 공통 frame도 확인한다. SI count와 energy, seven signed reservoirs, 원자/fast-electron/photon stoichiometry, source qualification pins, conditional mean의 moment 해석, rate/exposure/history의 null 및 heating 미승격을 검사한다.

Actual exports의 `native25`와 photon per-baryon 값은 root 결정대로 null을 요구한다. Nonzero projection은 C6가 저장할 `NATIVE25_POSITIVE_NB_CONTROL.json`의 실제 event로 별도 대조한다. 사전에 고정된 control 입력은 count=1.25 cm⁻³, kinetic=2.5 eV cm⁻³, nb=2.5×10⁶ m⁻³이다. 이 값으로 ΔY11=a, ΔY12=−a, Δζ=−a, Δw_nt=−Ue/nb와 나머지 zero rows, 별도 retained-photon port를 독립 계산한다. PW19 donor nb/T는 소비하지 않는다.

`CONTROL_RESULTS.json`에서는 `integrated_duplicate_event_id_rejected`와 `integrated_cross_frame_rejected`의 실제 C6 판정을 읽는다. Producer를 import하여 controls를 다시 실행하지 않는다. 통합 event energy의 기존 더 엄격한 **2e−13**도 유지한다.

## 실제 실행 인터페이스

Root dispatcher는 다음 인자를 checker에 전달한다.

```text
--unit-dir <research/cr_heiii_ground_rr_20261027>
--primary-dir <unit/runs/cr_heiii_rr_primary_20261027_v1>
--controls-dir <unit/runs/cr_heiii_rr_controls_20261027_v1>
--out-dir <new C9 attempt directory>
```

예상 출력은 `C9_INDEPENDENT_RESULT.json`과 두 개의 `*_DECIMAL70.csv`다. CSV는 각 reference의 28열 전체를 보존하며 private numeric evidence로 취급한다. 결과 JSON은 own-column 비교, selected coefficients, source rows, input/output identity, 실제 CPU와 실패를 보존한다. Output files는 create-only다.

외부 dispatcher의 독립 예약은 10 CPU-s, AS512 MiB, native thread1이다. Checker에는 9.8 CPU-s의 내부 중단 조건도 있지만 **완주 시간은 아직 측정하지 않았다**. 무조건 통과하도록 예산을 확대하거나 실패를 삭제하는 경로가 없다. 실패 시 가능한 partial reference와 error receipt를 남기고, 실제 시도 비용은 dispatcher가 별도로 기록한다.

이 검산기의 성공 판정 이름은 `PASS_SCOPED_INDEPENDENT_REFERENCE`이며, 전체 C9의 과학 채택은 실제 production diff·C6/C7/C8/C9 출력에 대한 마지막 독립 판단 뒤에만 가능하다. N6/N7, 기존 예산·UNKNOWN_NO_ACK, isotope mapping과 caloric/heating 구분을 바꾸지 않는다.

## 적용한 skill

`c38/physmath-research-loop` 1.3.0, `CODING_LOOP.md` C9 정의와 기존에 읽은 `POLICY_INTEGRATION.md`를 적용했다. 선택 단계는 C9 reference/checker 준비이며, 새 numerical suite나 CAS는 0이다. 추가 reviewer를 생성하지 않았다. Source/schema의 정적 대조와 문법 컴파일은 실제 수치 검산의 대체물이 아니다.

