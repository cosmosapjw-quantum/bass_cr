# CR N5 독립 C9 검토 — 범위 한정 PASS

**판정: C9 PASS. 열린 blocking finding은 0개다.** 검토 중 발견한 admission 선택자 누락, coverage 원자료 상대경로, Decimal 변환 underflow 문제는 각각 수정 근거와 영향받은 단일 검증으로 닫았다. 남은 2개는 선택된 과학 입력에 영향을 주지 않는 문서 정합성 항목이다. 이 판정은 `CR_N5_PROVIDER_RATE_SEMANTICS_AND_CE_ENVELOPE`와 consumer `N5_C23D_HI_CE_FIRST_EVENT_FINITE_BAND_V1`에만 적용한다. 전체 N4는 PARTIAL/OPEN, 전체 N5는 PARTIAL이며 N6/N7은 실행하지 않았다.

검토자 `/root/provider_returns`는 앞서 공급자 원문을 읽고 정확한 bytes를 가져오는 역할만 수행했다. 이번 production 구현, coverage matrix 또는 이론 문서를 작성하지 않았다. 실제 primary run ID를 root와 구현 담당자에게서 받은 뒤 원 코드·입력·출력·실행 영수증을 직접 검토했다. 최종 JSON은 검토한 코드, frozen input30개, primary 산출물, 수정 이력과 독립 검산의 size/SHA256을 제공한다.

- Primary: `n5_ce_envelope_primary_20261024t031906828z_v1`.
- 독립 검산: `n5_independent_c9_binary64_20261024T032519789383Z_v1`.
- Frozen input manifest SHA256: `37f8c70705e128368c36247379858a8f245bcb6819aab3d977a2c6b0c7dc3016`.
- 최종 `n5_semantics.py` SHA256: `71d7d36f8ec0d02d7e42a27634803c698466b6456c8cf2c69ea7dd43d81c56f8`.
- 실행 당시 primary source5개는 `implementation/repair_history/primary_executed_source/`에 보존됐고 PRE_EXECUTION 해시와 모두 일치한다. 두 입력 guard를 보완한 최종 코드와 구별한다.

## 1. 과학적 의미와 적용 구간

검토한 두 rate는 서로 다른 관측량이다. 저장된 PHYS83 Maxwellian coefficient `q(T)`에 thermal electron density를 곱한 `n_e q(T)`는 고정 표적 하나의 사건률이다. 새 tagged-electron hazard는 표적 ground-H density에 에너지별 `sigma(E) v(E)`를 곱한다. 코드에서 밀도를 바꾸거나 원자료에 이미 들어 있는 degeneracy를 다시 곱하지 않았다.

| 항목 | 이번 수용 범위 | 남은 제한 |
|---|---|---|
| Thermal comparison | 정확한 T10000 K CSV 행4개 × MFPT6개 =24행 | tagged 전자 확률, evolved event count, heat는 null |
| Tagged CE | 고정 `n_H1_1s=0.9 cm^-3`, stationary heavy/unpolarized source-native W-PL | 새로 명시한 ground-state closure다. excited density는 미수신 |
| EE first entry | 저장된 C23D R80 active mean과 active fraction | irreversible assimilation/Maxwellization이 아님 |
| PHYS84 | NUMERICAL_ADMISSION_WAIT | adapter code 존재를 numerical admission으로 승격하지 않음 |
| HE94/HE-ANG | 입사20 eV, 출사3–6 eV,15–120° 조건부 DDCS window | full event normalization/joint-secondary law 미수신; HE-ANG pending |
| CI/RR/DR/CX/elastic/EI | coverage 및 기존 조건부 근거 결속 | 이번 tagged hazard/전체 경쟁확률/heat는 null |

초기 source의 `0<W<10 eV`와 first-entry 전 경로를 구별했다. 새 CE maximum은 `q=chi k_BT/eV`부터 `80 k_BT/eV=68.93866609716143 eV`까지 평가된다. 원 source threshold10.20435 eV 아래의 zero는 공급자가 정의한 문턱이다. 초기 전자가 문턱 아래라는 이유로 이후 EE 경로에서 CE를 제거하지 않았다. 반대로 finite data window 밖의 미수신 영역은 physical zero로 대체하지 않았다.

독립적으로 확인한 survival/Jensen 부등식은

\[
P_A=1-\mathbb E[e^{-\int_0^\tau h\,dt}]
\le 1-e^{-h_{\max}\mathbb E[\tau\mid A]}.
\]

고정 EE 경로 위의 조건부 Poisson mark와 전 경로에서의 uniform hazard envelope를 전제로 한다. 선택 source 전체에는 active fraction을 곱한다. 원 pulse 전체, 다른 반응으로 바뀐 coupled path, 반복 CE 횟수, 에너지 deposition fraction으로 넓히지 않는다. 저장 MFPT가 검증된 upper enclosure로 공급되지 않았으므로 대입한 숫자는 조건부 모델의 수치 상한 추정이다. 방향성 반올림을 갖춘 확률 certificate나 우주론 전체의 error bound를 주장할 수 없다.

## 2. 독립 수치 검산

Production 코드는 각 W-PL panel의 endpoint와 가능한 stationary candidate를 평가한다. 독립 검산은 비음수 affine `W(E)=aE+b`에 대해 `W(E)/sqrt(E)`가 양의 내부 maximum을 갖지 않는다는 해석적 성질을 사용했다. 미분은 `(aE-b)/(2E^(3/2))`이고, 양의 admissible stationary point는 minimum이다. 따라서 union knots와 잘린 path endpoints를 직접 평가하면 충분하다.

`SOURCE_ARRAYS_REUSED.json`의 저장 배열, density, 상수와 scalar inputs를 `Decimal.from_float`로 정확한 binary64 입력값에 대응시켰다. 80자리 Decimal barycentric interpolation/square root를 사용했으며 production maximum 함수나 provider constructor를 호출하지 않았다. 여섯 경우마다431개 endpoint를 확인했다.

| 선택 | 두 chi에서 공통 hmax [proper s^-1] | 최대 지점 [eV] | 독립 binary64 기준 상대차 |
|---|---:|---:|---:|
| 2S | 7.897387991018573e-9 | 12.082 | 2.352e-17 |
| 2P | 2.701914615623522e-8 | 68.93866609716143 | 6.479e-17 |
| 2S+2P | 2.9189745001395196e-8 | 68.93866609716143 | 6.025e-17 |

합 채널의 maximum은 같은 에너지에서 합친 hazard를 최대화한 값이다. 서로 다른 위치에 있는 두 개별 maximum을 단순히 더하지 않았다.

추가로 저장된18 hcrit,18 CE first-event,24 thermal-product 행을 독립 닫힌식과 대조했다. Hcrit/CE 최대 상대차는 `1.85266860375458e-16`, thermal-product 최대 상대차는 `1.41832190629349e-16`로 frozen tolerance `5e-14` 이하다. 여섯 context의 평균과 active fraction은 기존 C23D R80 행과 정확히 같고,24 thermal 행의 q 문자열도 원 CSV의 정확한 T10000 행과 같았다. 생성된 input manifest30개와 primary 실행 source5개를 별도 SHA로 검증했다.

이 검산은 저장 binary64 입력에서 계산의 수치 일치를 확인한다. 원 CCC 자료의 empirical uncertainty, interpolation의 물리적 오차, finite-mass correction, 생략한 level, MFPT의 continuum 또는 무한영역 오차를 측정하지 않았다. `global_error_bound`와 `global_completion_percent`는 null이다.

## 3. 발견 사항과 해결 근거

### R1. 필수 선택자 생략 admission

원 `admit_rate`는 request에 T/incident/domain 필드가 있을 때만 검사했다. 독립 synthetic witness에서 thermal T를 제거하면 잘못 승인됐다. 최종 guard는 thermal T, 공급자가 선언한 T/incident/window, tagged energy 선택자를 필수로 요구한다. `n5_c9_selector_regression_20261024t032403142z_v3`의 영향받은 한 test method가 누락/null negative controls와 올바른 selector positive controls를 통과했다. 독립 witness도 원 코드는 true, 수정 코드는 false, 명시한 T는 true임을 확인했다.

실제 primary run은 T를 명시했으므로 숫자에 영향이 없다. 이 수정 때문에 primary 과학 계산을 다시 실행하지 않았다.

### R2. coverage source의 상대경로

기존 C23C의 `sources/...` 경로를 새 unit 기준으로 읽으면 파일이 없어 provenance가 불명확했다. PHYS81은 현재 local registry와 curve payload identity, PHYS82는 정확한 owner contract, HE37은 재사용한 C23C secondary provider entry로 해석 위치를 고쳤다. 원 상대경로는 archival metadata로 보존했다. HE37 raw owner를 이번에 다시 읽었다고 주장하지 않았다.

수정된 matrix SHA256은 `fc85f9395e0826c5b4dde116fdea00fa3645a6cc330788c37a569f5a3f996887`이다. `source_local_sha256`가 있는 모든 공급자 항목의 local bytes를 검증했다.21 populations ×8 channels의 상태를 직접 읽었고, 모든 `rate_value`는 null을 유지한다. 조건부 elemental PI/RR 모델, C23E D43K, finite source, 부적용 process와 미수신 process를 구별했다. isotope quotient는 모든 admitted bath state에서의 generator/energy observable 조건을 유지한다.

### R3. Decimal 입력 변환 underflow

독립 검산 당시 `product(Decimal('1e-1000'),1.0)`는 float 변환에서 먼저0이 되어 기존 product underflow 검사를 우회했다. 이는 frozen JSON/binary64 입력에는 영향이 없지만 함수가 Decimal을 허용한다는 계약과 어긋났다. 원 witness의 코드 `c2892e...`는 `repair_history/pre_decimal_coercion_fix_source/`에 그대로 남겼다.

최종 코드는 float 결과가0인데 원 입력이0이 아니면 `NONZERO_COERCION_UNDERFLOW`로 거절한다. `n5_c9_decimal_coercion_20261024t032722392z_v1`의 단일 test method에서 양/음 tiny Decimal 거절, 양/음 exact zero 및 representable 값 허용을 확인했다. reviewer는 최종 두 줄 guard diff, test 결과와 pre-execution source hash를 한 번 대조했다. CE 최대값과 닫힌식은 변경되지 않았으므로 기존 독립 검산을 재사용했다.

## 4. 최초 검증 실패와 수정 이력

최초 새 suite `n5_semantics_tests_20261024t031814026z_v1`은25개 중24 PASS,1 FAIL이었다. 실패를 전부 PASS로 덮어쓰지 않았다. `epsilon`이1에 가까운 사례에서 `Decimal(str(float))`는 production `log1p`에 실제로 들어간 binary64와 약간 다른 입력을 나타내므로 `2.0815086e-12`의 상대차가 발생했다.

`reference_hazard_limit`만 실제 float 입력을 `Decimal.from_float`로 옮기도록 수정했다. `n5_hcrit_reference_check_20261024t031855920z_v2`에서 영향받은 test 하나를 통과했고, 이전24개 검증은 재사용했다. 현재 producer의 product/envelope/first-event reference는 여전히 `Decimal(str)`를 쓴다. 그것은 저장된 근접 decimal representation과의 agreement이며 certified arithmetic bound가 아니다. 이번 독립 from-float 검산이 이 구별을 명확히 한다.

전체 suite를 반복 실행하지 않았다. 최종 evidence는 원24 PASS, corrected hcrit1, 새 selector1, 새 Decimal coercion1로27개의 서로 다른 method에 대한 근거다. 두 selector launch 시도는 root-owned plot lease 때문에 child를 시작하지 못했고 각각 실패 영수증을 보존했다. 해당 worker CPU는0이며 첫 영수증의 RUSAGE RSS값은 실제 worker RSS가 아님을 별도 정정했다.

## 5. 남은 비차단 문서 항목

| ID | 증거 | 현재 판정과 후속 정리 |
|---|---|---|
| N2 | frozen revision2는 NumPy/SciPy pinned import와512MiB를 허용하지만 뒤의 이전 문장은256MiB/no heavy libraries라고 적혀 있음 | 명시적인 revision2가 우선하고 실제 PRE_EXECUTION도512MiB다. 다음 계약에서 문장을 통합하되 frozen 원본은 보존 |
| N3 | 이론 negative list는 epsilon<=0을 거절한다고 쓰지만 API/tests는 epsilon0의 정확한 zero limit을 허용 | 선택 epsilon은.01,.1,.5라 결과 영향 없음. 다음 계약에서 zero-limit 확장을 명시하거나 API를 일치시킴 |

## 6. 자원, 비용과 종료 범위

Producer의 최종 비용 기준은 `implementation/EXECUTION_LEDGER_FINAL_V3.json`이다.7 attempts 중 실제 children5개(test4, primary science1), prelaunch lease rejection2개다. Worker CPU는0.568941 s, coordinator CPU는0.014389513 s다. 최초 실패 및 수정 검증 비용을 포함한다.

독립 C9 worker는 CPU0, native thread1,128MiB address-space/5 CPU s/30 wall s 한도에서 실제0.074879 CPU s, RSS13544 KiB를 사용했다. 별도 coordinator CPU는0.001256838 s였다. 해당 실행은 current resource snapshot 및 exclusive local lease를 기록했고 정상 해제했다. CPU8 coordinator를 보호했으며 이 host에서 보이지 않는 CPU55/NCP 자원을 임의로 사용하지 않았다. Parent plot 비용은 별도이며, inherited known lineage15.493261114 worker CPU s를 초기화하지 않는다. 전체금액, remaining, 미측정 intake/reasoning/report 비용은 여전히 unknown/null이다.

이번 reviewer 실행의 새 ODE, provider constructor, provider rate evaluation, quadrature, old science replay는 모두0이다. Primary는 source array 복원에 기존 constructor2회를 사용했고 provider moments/evaluate를 호출하지 않았다. PHYS84 numerical source나 HE window moments를 다시 계산하지 않았다.

**EXECUTION:** C9 scoped PASS, 열린 blocking0. **PUBLICATION:** parent의 expected-SHA 게시 단계. **BACKUP:** parent의 실제-byte R3 단계. **DAG:** 이 N5 child만 수용 가능; 전체 N5 PARTIAL, N6/N7 OPEN. 이 검토는 publication 또는 backup 완료를 대신하지 않는다.
