# N5 새 구현과 제한된 수치 검증

## 계약과 구현

`FROZEN_CONTRACT.md`의 실행 전 revision 2와 root가 확정한 입력 30개를 소비했다. 이 구현의 범위는 rate 의미론, 기존 MFPT·열적 rate 표의 대수적 비교, 그리고 H1 ground-state CE의 조건부 첫 사건 추정이다. 기존 PHYS83 Maxwell 적분, reciprocity/population suite, PHYS84 source adapter, C23D ODE·MFPT 적분은 실행하지 않았다.

`n5_semantics.py`는 quantity kind, 종·전하·내부상태, frame·clock, 단위, 온도 exact match, 에너지·각도 support, isotope mapping, owner gate 및 null을 검사한다. 수치 0은 명시된 owner zero 근거가 있어야 채택한다. `run_diagnostic.py`는 기존 bath T·ne·lnLambda 및 frame·proper clock·closed-box identity를 확인한 뒤 기존 21-population registry와 저장된 6개 R80 평균을 읽는다. 기존 isotope quotient/보존 정리 또는 반응 network를 다시 구현하지 않았다.

PHYS83 원본 `MatchedCEChannel` constructor로 `energy_eV`, `W_eV_cm2`를 읽었다. constructor와 원본 vendor·네 source 파일은 입력 manifest와 provider 자체 hash 검사에 결속된다. 실행 중 Python entrypoint trace는 constructor 2회, pinned-blob load 2회, source table parse 4회, immutable-array construction 22회를 기록했다. `moments` 또는 `evaluate` 호출은 guard가 즉시 거절하도록 되어 있으며 실제 호출은 0회였다. 원 source code를 수정하지 않았다.

새 hazard는 `n_1s * 100 * sqrt(2 * eV_J / m_e) * W(E)/sqrt(E)`다. 추가 degeneracy 또는 factor 2를 넣지 않았다. 각각의 비음성 선형 W panel에서 clipped endpoint와 존재하는 `E=b/a`를 검사한다. 평가에는 `a*E+b` 대신 비음성 endpoint interpolation을 사용해 threshold 인근 상쇄를 피했다. 서로 다른 knot grid는 union을 취하며, 경로 전체 `[chi*theta, 80*theta]`를 검사한다. 저장된 값은 이 명시된 보간 모형의 수치적으로 평가한 supremum이며 physical/continuum certificate가 아니다.

독립 `decimal_reference.py`는 production arithmetic을 import하지 않는다. 80자리 Decimal endpoint oracle은 비음성 affine W에 대해 양의 interior stationary point가 minimum이라는 성질을 사용한다. 따라서 production의 일반 stationary 후보 탐색과 독립된 endpoint 경로로 최대값을 확인한다. 행별 rate-product, hcrit, first-event 산술에도 Decimal 참조를 저장했다.

## 실행 증거

새 고유 test method는 25개다. 첫 실행 `n5_semantics_tests_20261024t031814026z_v1`은 24 PASS, 1 FAIL이었다. 실패한 `test_hcrit_decimal`은 epsilon=0.999999에서 참조의 `Decimal(str(float))`가 binary64 입력과 다른 실수를 사용했기 때문이다. 약 `2.0815e-12` 차이는 `1-epsilon`에서 증폭된 입력 identity 차이였다. 참조를 `Decimal.from_float`로 바꿔 동일 binary64 입력을 80자리에서 평가했다. frozen science 모델과 production `log1p` 계산은 바뀌지 않았다.

변경 의존성인 `AlgebraTests.test_hcrit_decimal`만 `n5_hcrit_reference_check_20261024t031855920z_v2`에서 재검증하여 PASS했다. 나머지 24개는 변경되지 않은 의존성의 첫 실행 PASS를 재사용했다. 첫 실패의 로그·비용·source hash를 보존했고, 교정 전 reference/tests/dispatcher의 원본 bytes를 역패치한 뒤 당시 PRE_EXECUTION SHA256과 정확히 일치시켜 `repair_history/first_attempt_exact_source/`에 보존했다. 이 복원에는 코드를 실행하지 않았다.

과학 primary는 `n5_ce_envelope_primary_20261024t031906828z_v1` 한 번이다. hcrit 18행, frozen-target thermal-rate 비교 24행, 조건부 CE 첫 사건 추정 18행 및 별개의 envelope 6개가 생성되었다. `CE_PATH_ENDPOINT_SAMPLES.json`은 두 chi마다 경로에 포함된 union/clipped endpoint 431개의 2S·2P·sum hazard를 보존하므로 후속 그림은 이 값으로 그릴 수 있다.

| 실행 | 결과 | worker CPU s | peak RSS KiB |
|---|---|---:|---:|
| 첫 targeted test | 24 PASS / 1 reference-input FAIL | 0.065180 | 16,384 |
| 변경 의존성 재검증 | 1 PASS | 0.062708 | 15,744 |
| primary 대수 진단 | PASS_SCOPED | 0.323328 | 48,124 |

실행·실패를 포함한 새 worker CPU는 `0.451216 s`, coordinator CPU는 약 `0.008857562 s`다. 이전 measured lineage 부분합 `15.493261114 s`를 보존하여 현재 알려진 worker 부분합은 `15.944477114 s`다. 전역 예산·남은 예산·통화·측정되지 않은 비용은 null이다. 각 실행의 `PRE_EXECUTION.json`, `DISPATCH_RECEIPT.json`과 통합 `EXECUTION_LEDGER.json`이 authoritative한 실제 기록이다.

## 핵심 결과의 해석

`theta = 0.8617333262145178 eV`, R80 상단은 `68.93866609716143 eV`다. 초기 source의 `0<W<10 eV`와 전체 pre-entry path를 구분했다. CE source-native threshold는 `10.20435 eV`다.

| 선택 | 수치 envelope / proper s^-1 | 최대 에너지 eV |
|---|---:|---:|
| 2S | 7.897387991018573e-9 | 12.082 |
| 2P | 2.701914615623522e-8 | 68.93866609716143 |
| 2S+2P | 2.9189745001395196e-8 | 68.93866609716143 |

두 chi의 threshold가 CE gap 아래이므로 위 최대값은 공통이다. envelope의 80자리 참조 대비 최대 scaled relative 차이는 약 `1.494e-16`이었다. 2S+2P 조건부 active-population 첫 CE 확률 상한 추정은 6개 context에서 약 `0.00784377–0.00819922`, whole-selected 추정은 약 `0.00330455–0.00525580`이다. 이는 frozen EE 경로 위의 CE-only marked-process 결과다. 전체 non-EE 사건 확률, omitted process 확률, late-time heat, full stopping, permanent assimilation 및 physical/global certificate는 null로 유지한다. 이 구분은 `SCIENCE_INTERPRETATION.json`에도 저장했다.

`lambda_target = ne*q(T)`와 `lambda_target*m_active`는 각 고정 원자 target의 thermal-rate/EE-time 비교다. tagged-electron hazard 또는 실제 원자 population의 사건 수로 바꾸지 않았다. PHYS84 source callback은 실행되지 않았다.

## 자원·출력 계약

Dispatcher는 매번 현재 cgroup memory, clean inactive file cache, CPU affinity 및 관련 process 목록을 기록한다. `headroom + clean inactive file - 64 MiB >= 256 MiB`일 때만 새 child를 실행한다. coordinator CPU 8, worker CPU 0, native thread 1, address-space 512 MiB, CPU 30 s, wall 60 s를 사용했다. CPU 55는 이 호스트의 affinity에 없다. 외부 NCP lease는 UNOBSERVED로 유지하며 local lease는 `O_EXCL`로 획득·해제한다.

Run 디렉터리는 create-only이며 동일 ID는 거절한다. stdout/stderr, failure, source·input hash 및 비용을 보존한다. scientific output 파일을 수정하지 않았다. import 시 scientific work나 explicit output 쓰기가 없고 dispatcher의 `-B` 및 `PYTHONDONTWRITEBYTECODE=1`로 bytecode 쓰기도 막았다. JSON은 NaN을 허용하지 않는다.

## 단계 기록

| 단계 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|
| C2 계약 | revision2/30-input/source identity 결속 | parent 소유 | canonical bundle 대기 | N5 scoped child |
| C3 수치식 | hazard/Jensen·단위·domain 산술 구현 | parent 소유 | 대기 | C23D MFPT 재사용 |
| C4 알고리즘 | union panel·안정 interpolation·Decimal oracle | parent 소유 | 대기 | 전체 path coverage |
| C5 코드 | module/reference/run/dispatcher/tests 구현 | parent 소유 | 대기 | 새 provider campaign 없음 |
| C6 검증 | 24기존 PASS 재사용 + 수정1 PASS | parent 소유 | 실패 포함 보존 | reference 지적 닫힘 |
| C7 새 입력 | 30개 SHA256·정확 T·새 run ID | parent 소유 | pins 보존 | 원 MFPT·source identity 유지 |
| C8 결과 | primary 1회, 18/24/18행 | parent 소유 | canonical bundle 대기 | N5 부모 PARTIAL; N6/N7 OPEN |
| C9 | 별도 독립 reviewer에게 반환 | parent 소유 | 대기 | 독립 판정 대기 |
| C10 | parent 통합·게시·백업 | parent 소유 | 대기 | 전체 N5 완료 주장 없음 |

## 독립 C9의 selector 지적 교정

C9는 provider가 온도 또는 finite-window 제약을 선언했는데 caller가 해당 selector를 생략하면 adapter가 비교를 건너뛸 수 있음을 발견했다. 이는 구현의 admission 결함이다. `admit_rate`를 수정하여 thermal quantity에는 T를, tagged quantity에는 에너지 selector를 필수로 요구하며, provider의 T/incident 목록 또는 energy/outgoing/angle domain 선언에는 대응하는 명시적 request selector를 요구한다. 누락과 null은 모두 거절한다.

Primary 실행은 이미 정확한 T와 전체 identity를 명시했으므로 이 수정은 저장된 18/24/18행에 영향을 주지 않는다. 과학 primary를 재실행하지 않았다. primary에서 실행한 5개 source 파일은 `repair_history/primary_executed_source/`에 당시 SHA256과 동일한 bytes로 보존했다. 최종 전달 코드와 실행 코드의 구분은 `repair_history/C9_SELECTOR_REPAIR_RECEIPT.json`에 명시했다.

새 targeted regression `SemanticTests.test_required_selectors_c9`에는 온도·입사에너지·incoming/outgoing energy·angle selector의 누락/null 거절과 명시된 유효 request, tagged-energy 조건 및 기존 exact-T positive case를 포함했다. 두 번의 dispatch는 root의 완료된 plot v2 lease 잔여 파일 때문에 child 실행 전에 차단됐다. 타 소유 lease를 제거하지 않았으며 root가 terminal PASS 영수증과 대응하여 정리했다. 두 prelaunch 실패의 worker CPU는 0으로 보존한다. 첫 prelaunch 기록의 RSS 696 KiB는 실행된 worker가 없는 `RUSAGE_CHILDREN` snapshot이므로 worker RSS로 해석하지 않는다. 이후 dispatcher는 이 경우 RSS를 null로 기록한다.

실제 해제를 관측한 뒤 새 ID `n5_c9_selector_regression_20261024t032403142z_v3`에서 targeted regression이 PASS했다. 추가 worker CPU는 `0.057216 s`, peak RSS는 `15,744 KiB`다. 최종적으로 통과 근거가 있는 고유 test method는 26개이며 영향을 받지 않은 근거는 재사용했다.

**현재 비용 기준은 `EXECUTION_LEDGER_FINAL.json`이다.** 최초 reference 실패·성공, primary, 두 prelaunch 차단, selector regression을 모두 포함한 새 worker CPU는 `0.508432 s`, coordinator CPU는 약 `0.011562183 s`다. 기존 부분합과 합한 worker subtotal은 `16.001693114 s`다. root의 plot 및 독립 C9 비용은 이 파일에 포함하지 않으며 root가 별도로 합산한다. 전역 spend·remaining·currency는 null이다.

## 마지막 C9 API 교정과 최종 비용 기준

독립 검토는 공개 함수 `real`의 Decimal 지원에서 양수 또는 음수의 `Decimal('1e-1000')` 같은 nonzero 값이 float 변환 때 0이 되는 경우를 발견했다. Frozen JSON 입력과 primary 결과에는 영향을 주지 않는 일반 API 경계 문제다. `result == 0.0 and original value != 0`를 거절하는 좁은 guard를 추가했다. 음의 tiny Decimal도 부호가 사라지기 전에 nonzero coercion underflow로 거절한다. Exact signed zero와 표현 가능한 Decimal은 계속 허용한다.

새 단일 targeted method `AlgebraTests.test_decimal_coercion_underflow_c9`가 `n5_c9_decimal_coercion_20261024t032722392z_v1`에서 PASS했다. 양·음 tiny Decimal, product 경유, exact zero·signed zero·표현 가능한 Decimal·기존 float zero를 확인했다. 과학 primary와 기존 suite는 재실행하지 않았다. 독립 검토가 사용한 수정 전 `n5_semantics.py`의 SHA256 `c2892e334808d8deeffaf8b2e4f5a69795ca256813e63b08ded75fdb2880c7e4` bytes는 `repair_history/pre_decimal_coercion_fix_source/`에 보존했다. `C9_DECIMAL_COERCION_REPAIR_RECEIPT.json`은 원 primary/selector 교정 후/최종 전달 SHA를 구분한다.

**최종 비용 authority는 `EXECUTION_LEDGER_FINAL_V3.json`이다.** 앞선 FINAL 파일은 당시 상태의 기록으로 보존한다. 새 worker 총합은 `0.568941 s`, coordinator 총합은 약 `0.014389513 s`, 기존 lineage와 합친 worker 부분합은 `16.062202114 s`다. 실제 child는 test 4개·science 1개이며 prelaunch lease 차단 2개가 별도로 남는다. 통과 근거가 있는 고유 test method는 27개다. Parent의 plot·독립 C9 비용은 이 부분합에서 제외하며 전역 spend/remaining/currency는 null이다.
