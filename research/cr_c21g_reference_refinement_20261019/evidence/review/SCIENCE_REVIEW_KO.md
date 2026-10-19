# C21G 독립 과학·코드 검토

검토일: 2026-10-19 UTC. 검토자: reference_theory 독립 agent.

## 1. 판정과 범위

최종 판정은 `PASS_SCOPED_SCIENTIFIC_CODE_REVIEW`다. Photon/EOS 차의 수식, H/He 수지 재계산, reference-free order, 두 scale의 hybrid−FULLMID 계수는 검토한 구현에서 맞다. Empirical reference 변화량을 global error bound로 승격하지 않는 구분도 유지된다. 초기 검토에서 발견한 실행 gate와 log-completeness, benchmark의 binary64 비교 명칭, standalone payload 검증 연결은 한정된 수정 뒤 직접 확인하여 닫았다. 이 판정은 새 native 실행이나 native 정확도 인증의 완료가 아니다.

검토는 새 코드 읽기, 이미 생성된 산출물의 독립 산술 재계산, 기존 이론식과의 대조로 수행했다. 기존 C21F 56개 검증이나 native matrix를 다시 실행하지 않았다. 새 native reference와 n128/256 결과도 아직 없다. `REMOTE_QUOTA_INTAKE.json`의 실제 조회는 remote 호출 잔여량 0%와 연결 device 1개를 기록하며, 현재 NCP 자원 inventory는 `UNVERIFIED_CURRENT_NCP`다. 이를 NCP의 실제 CPU·메모리 가용량이 0이라는 뜻으로 읽지 않는다. 이 검토에서 remote campaign를 시작하지 않았다.

직접 읽은 파일:

- `unit/analyze_campaign.py`: reference-readiness, observed reference-choice 범위, refinement와 coefficient 산출.
- `unit/diagnostics.py`: strict domain, log-survivor, EOS, 수지, signed order, conditional interval.
- `unit/campaign_contract.py`: source/fixture pin, 단위 scale, tier, pilot budget, HOLD 범위.
- `unit/run_campaign.py`: operational readiness와 실행 영수증의 연결 부분.
- `unit/verify_analytic_reference.py`: 제조 IVP의 analytic 식과 benchmark 출력.
- `baseline_coefficient_probe/BASELINE_COEFFICIENT_DIAGNOSTIC.json`.
- `analytic_validation/ANALYTIC_REFERENCE_CHECK.json`의 첫 실행 기록.

## 2. 발견한 수정 항목

### S1. 8개 reference 실행완료와 native pilot 민감도를 함께 확인해야 함

초기 `run_campaign.py`는 native_source의 pilot status만으로 n128/256을 열었다. 따라서 common_ic의 reference job이 실패했어도 native_source 네 job이 성공하면 refinement를 시작할 수 있었다. 이 경우 최종 상태가 COMPLETE 계열로 기록된 뒤 마지막 failed-job 검사에서 실패 exit를 내는 모순도 가능했다.

계약에 맞는 조건은 다음과 같다.

```text
all eight reference jobs operationally COMPLETE
AND native_source pilot sensitivity is REF_READY
```

Common_ic의 수치 민감도 budget 초과는 native_source의 정련을 막지 않는다. Common_ic의 실행 실패·누락은 전체 reference 단계 미완료다. 이 둘을 나누는 helper와 분기 검증이 필요하다고 root에게 전달했고 runtime 검토 agent가 수정하기로 했다.

### S2. 일부 양의 cohort의 log가 없을 때 max-log 판정을 통과시키면 안 됨

`diagnostics.py`는 positive-weight log-unavailable pair 개수를 기록한다. 그러나 초기 analyzer의 `metrics()`는 이용 가능한 log 차의 max만 읽었다. 일부 cohort가 누락되어도 다른 cohort가 있으면 수치가 남아 readiness가 통과할 수 있었다.

정상 optical-depth reference는 모든 양의 cohort에 tau를 기록하므로 현재 정상 생산 경로에서는 이 결함이 드러나지 않는다. 그래도 손상·불완전 자료에서 READY가 나오는 것을 막아야 한다. `positive_weight_log_unavailable_pairs>0`이면 log metric을 unavailable로 판정하고 해당 resolution check를 실패시켜야 한다. 구조적 A=0 cohort는 이 조건에서 제외된다.

### S3. Analytic solution의 binary64 평가와 true error를 구별

첫 benchmark는 해석식 자체를 binary64로 계산하고 그 차를 `true_endpoint_errors_in_this_exact_problem`과 `True thermal endpoint error`라고 표시했다. 실제 수학적 해석식은 맞지만 4.44e-16처럼 unit-scale roundoff 부근의 값은 analytic evaluation의 반올림도 포함한다.

Root의 수정 방침에 동의한다. 필드는 `difference_from_binary64_analytic_evaluation`, 그림은 analytic solution과의 thermal difference로 표시하고 analytic evaluation precision을 명시한다. kappa=800에서 photon absolute difference가 floating 0인 것도 실제 photon 오차가 0이라는 뜻이 아니다. 양의 양쪽 survivor가 underflow한 것이고 log 차는 남는다.

이 수정에는 ODE 재실행이 필요하지 않다. 첫 실행 기록을 역사 자료로 보존하고, 같은 numeric output을 이용한 v2 metadata와 그림을 create-only 저장하면 된다. 원래 실행 시간과 raw identity는 유지한다.

### S4. Standalone analyzer의 provenance 검증 경로

초기 `completed_results()`는 COMPLETE receipt의 payload directory를 읽지만 payload SHA를 재검증하지 않았다. 현재 runner의 막 생성된 결과와 별개로, 나중에 백업으로 복원된 raw를 standalone analyzer에 넣을 때는 receipt와 파일이 여전히 일치하는지 확인해야 한다. 절대 원래 payload 경로만 있으면 다른 환경으로 복원할 때의 경로 연결도 필요하다. Root에게 전달했고 runtime/provenance 검토에 배정됐다. 이것은 수식 오류가 아니라 새 결과 intake의 신뢰성을 위한 항목이다.

## 3. 물리식·수지 검토

### Photon 좌표

양의 고정 A에서 두 tau가 모두 있으면 구현은 delta log를 tau_right−tau_left로 계산한다. 공통 log(A)를 먼저 상쇄하므로 맞다. Stable count 차의 부호도 log 차의 부호와 같고

\[
\operatorname{sign}(\delta\ell)e^{\max(\ell_L,\ell_R)}
\{-\operatorname{expm1}(-|\delta\ell|)\}
\]

를 사용하므로 left−right 방향이 유지된다. 직접 count 차와 stable 차, log 차와 underflow를 별도로 기록한다. 양의 weight인데 유한 log를 알 수 없는 0은 underflow로 인증하지 않는다.

Native pilot의 실제 count budget은 `max_i abs(deltaN_i)`다. 일반적인 total-photon bound인 `sum_i abs(deltaN_i)`와 다른 지표이므로 theory의 pilot 표를 실제 max 정의로 맞췄다. 일반 L1 집계량의 수학적 상계 유도는 별도로 유효하다.

### EOS

구현은 D=1+Y+x+Yy+2Yz와

\[
T_L-T_R=\frac{\delta w-w_R\delta D/D_R}{1.5k_BD_L}
\]

를 쓴다. 기존 EOS와 정확히 같은 실수 항등식이다. 직접 temperature 차와 stable 식의 차를 함께 저장한다. Fraction과 thermal 오차를 혼동하지 않으며 w_birth로 정규화하는 기존 gas norm도 유지한다.

### H/He·energy 수지

HeII stock 변화는 Y delta y, HeIII는 Y delta z다. Net event는 photo+ci−rr이며 dielectronic recombination은 HeII→HeI 채널에서 빠진다. 기대 stock 변화는 (net_H, net_HeI−net_HeII, net_HeII)로 구현되어 맞다. Y=0에서 He event를 명시적으로 거부하고 0/0을 피한다.

Binding 변화의 계수는 HII에 B_H, HeII에 Y B_HeI, HeIII에 Y(B_HeI+B_HeII)로 맞다. Photon/thermal/binding 변화, escape, −CMB, photon work, gas work, −source energy가 기존 outer/native ownership과 일치한다. Source number와 energy를 고정 birth fixture에서 별도로 재계산한다. 이 수지는 trajectory error bound로 해석하지 않는다.

### Tolerance scale

State 순서와 energy ledger offset 14–18, gas thermal offset M+3은 현행 reference와 일치한다. Energy scale은 초기 thermal·binding과 모든 고정 birth photon energy로 정해지며 output-adaptive scale이나 physical stock floor가 없다. 단위 1인 number ledger와 무차원 1인 tau/fraction을 같은 수치여도 다른 단위로 설명한다.

## 4. Reference-readiness와 차수의 의미

Tier 변화와 max-step 변화의 관측 차에서 empirical radius를 만들고 `global_error_bound=null`을 유지한다. 이는 주어진 계산 예산에서 다음 정련을 시작할 수 있는지 보는 조건이다. State의 정확도 인증, source/spectral convergence, native kernel 독립 검증을 대신하지 않는다.

L3와 L3M의 accepted-grid hash가 같으면 `MESH_CAP_INACTIVE`로 판정하는 구현이 맞다. 결과가 같은 것을 mesh 정련 확인으로 승격하지 않는다. 실제 grid가 달라도 독립 알고리즘이나 엄밀한 오차 enclosure가 되는 것은 아니다.

`signed_order()`는 같은 부호의 비영 error pair에만 유한 차수를 반환하고 crossing/zero를 unresolved로 남긴다. 이는 단순 abs-ratio보다 신중한 경험적 판정이다. 크기 기반 차수의 수학적 식 자체는 부호가 달라도 쓸 수 있지만 상쇄 구간의 asymptotic order 주장을 보류한다는 계약으로 읽으면 맞다.

`conditional_order_interval()`의 triangle bound는 mixed sign에서도 유효하다는 주석을 갖는다. 함수는 rho가 실제 reference 오차 상계라는 조건을 스스로 검증하지 않았고 binary64 식이 validated interval arithmetic이 아니라는 점을 명시한다. Empirical rho를 넣으면 sensitivity interval이며 보장된 confidence interval이 아니다.

여러 reference에서 얻은 유한 p의 min/max는 관측된 reference-choice 범위다. Analyzer는 unresolved reference 개수와 해석 제한을 함께 저장하므로 이를 통계적 신뢰구간이나 asymptotic order 증명으로 출력하지 않는다. 64/128/256 reference-free order도 roundoff·solver residual·비점근성의 영향을 받을 수 있다.

## 5. 기존 endpoint에 새 계수 진단을 적용한 결과

이것은 이미 게시된 baseline endpoint의 재사용이다. 새 native 실행이나 과거 matrix 재실행이 아니다. d_n=hybrid_n−FULLMID_n에 대해

\[
\widehat A_n=n(4d_{2n}-d_n),\qquad
\widehat B_n=2n^2(d_n-2d_{2n})
\]

는 구현과 맞다. d_n=A/n+B/n^2+C/n^3이면 정확히

\[
\widehat A_n-A=-C/(2n^2),\qquad
\widehat B_n-B=3C/(2n)
\]

이다. 이 점근 전개가 실제 데이터 구간에서 성립한다는 추가 전제는 남는다.

| Pair 시작 n | native_source thermal Ahat | native_source thermal Bhat | common_ic thermal Bhat |
|---:|---:|---:|---:|
| 8 | −7.654158066117134e-5 | −1.4562402725459833e-5 | −1.8175683180743363e-10 |
| 16 | −7.654582731220216e-5 | −1.4494456308966619e-5 | −2.53749021794647e-10 |
| 32 | −7.654775441068296e-5 | −1.4432789157581283e-5 | −6.293703336268663e-10 |

Native Ahat는 세 쌍에서 음수이고 전체 spread를 마지막 크기로 나눈 값은 약 8.065e-5다. 이것은 reference에 의존하지 않는 음의 leading coefficient 후보가 작은 범위에 있다는 관측이다. True A가 그 범위 안에 있거나 그 상대 정확도를 가졌다는 bound가 아니다.

특히 native Ahat의 인접 drift는 4.2466510308258876e-9와 1.9270984807917557e-9로 비가 2.2036502405840386이다. 이는 n^-2 잔여오차가 지배할 때 기대할 4배 축소를 확인한 자료가 아니다. 그 비의 log2 약 1.1399 역시 세 쌍의 경험적 진단값일 뿐 asymptotic theorem이 아니다. 새 n128/256이 필요한 이유가 남는다.

Common Bhat는 표처럼 크기가 커지고 안정하지 않다. 작은 second coefficient를 이 세 쌍에서 정확히 결정했다고 쓰면 안 된다. 원인을 특정 solver tolerance나 roundoff로 단정할 자료도 아직 없다. 현재 출력의 `crossing_prediction=NOT_FORMED`, `zero_crossing_forecast=null`은 적절하다. 이전 zero-crossing fit을 복원하거나 재사용하지 않는다.

## 6. 제조 analytic benchmark의 실제 확인 범위

첫 report는 2026-10-19T08:24:42 UTC부터 9개 case를 1.9097576049971394 s에 수행한 기록이다. Numpy 2.3.5, SciPy 1.17.0이다. Native microphysics를 사용하지 않는다.

모델은 dimensionless time에서 tau'=k, N=A exp(−tau), P'=kN, w'=QkN−mu w, L'=mu w다. Exact solution의 convolution과 k=mu의 resonant limit 분기가 맞다. Number N+P=A와 energy QN+w+L=QA+w0도 해당 제조 문제의 정확한 보존식이다. FLRW expansion, H/He absorber feedback, source birth, native chemistry는 포함하지 않는다.

- k=80, mu=0.3에서 L1/L2/L3/L3M 4개 case.
- k=800, mu=0.3에서 같은 4개 case. Reconstructed survivor underflow와 유한 log 보존을 실제로 확인했다.
- k=mu=0.3에서 L3 1개 case. Resonant analytic 분기를 확인했다.

첫 report에서 k=80의 L3 thermal 차는 +4.440892098500626e-16 eV/H이고 k=800에서는 −4.440892098500626e-16이다. 둘 다 binary64 analytic evaluation과의 차로 보고해야 한다. k=mu에서의 floating 0도 수학적 오차가 정확히 0이라는 인증이 아니다.

L3와 L3M은 k=80과 k=800 모두 실제 accepted-grid hash가 완전히 같다. 따라서 두 경우의 기록은 `MESH_CAP_INACTIVE`가 맞다. 모든 9개가 사전의 유한 비교 budget을 통과했지만 native reference 정확도나 mesh 독립 검증을 완료하지 않는다.

## 7. 최초 검토 입력의 지문

| 입력 | 최초 검토 SHA256 |
|---|---|
| analyze_campaign.py | d65a9d9924425105d1b18555e93bf5d39ff0742e6d74088da07a7a6854be1571 |
| diagnostics.py | a27eb840afaf657334f251db807f8631b7f6252bd3da63382c1b6d93060424bd |
| campaign_contract.py | bafa454aaa674208bee28215b34303466581470a9acdeeb3ddf0f99cddc09bc5 |
| BASELINE_COEFFICIENT_DIAGNOSTIC.json | 04427e3a64e4d2aa7f3b1b9d41dd24b949cbc1bd63d82442198f4ce08006932c |
| ANALYTIC_REFERENCE_CHECK.json 첫 기록 | 21d55fa5b6b7269ef39f99b1036ceb36877da897e4a7eae0ce0c41df53f9c572 |

수정 이후의 실행 manifest가 최종 코드 지문을 결정한다. 첫 기록의 숫자와 시간은 metadata 교정으로 새 ODE 실행이 이루어진 것처럼 바꾸지 않는다.

## 8. 게시·백업·DAG 상태

| 단계 | 과학 판정 | 전달 상태 |
|---|---|---|
| 새로운 자료 intake | Root의 현재 receipt 재사용 | Root 게시·백업 영수증 참조 |
| 수식·수지 독립 검토 | COMPLETE_SCOPED_REVIEW | 본 파일을 새 root checkpoint에 포함 |
| S1 실행 gate 수정 | CODE_REVIEW_CLOSED | can_refine와 실제 호출부 직접 확인 |
| S2 log completeness 수정 | CLOSED | 누락 positive-weight log는 READY 불가 |
| S3 binary64 명칭·layout 교정 | CLOSED | 첫 숫자 보존, v2 metadata와 v3 plot 직접 확인 |
| S4 provenance 연결 | CLOSED_SCOPED_INTEGRITY | 최종 helper·standalone 연결 직접 확인 |
| 새 analytic 제조 case | 9/9 finite checks PASS | Native 검증으로 승격하지 않음 |
| 새 native reference/128/256 | NOT_RUN | 자원·실행 영수증 필요 |
| Full48/source-age/spectral/angular/Case B/Bianchi/full EoR | HOLD | 기존 독립 검증 조건 유지 |

## 9. 최종 closure

### 직접 확인한 1차 closure

- S2 CLOSED: analyzer의 `metrics()`가 `positive_weight_log_unavailable_pairs`가 있을 때 log metric을 `None`으로 반환한다. Resolution check의 `is not None`과 연결되어 누락 cohort가 있으면 READY를 허용하지 않는다. 확인 코드 SHA256: `c11643ce8dd53a4eb091d42cd6fcb883f6e09c39e4b03a1ac83a727eb79358ea`.
- S3 SCIENTIFIC_METADATA_CLOSED: `analytic_validation_v2/ANALYTIC_REFERENCE_CHECK.json`을 직접 읽고 첫 report와 9개 case를 모두 비교했다. Field rename과 새 precision 설명을 제외한 모든 기존 값이 동일하다. V2 SHA256은 `0448e204e22ed884e2fd29bada51ff63767c99c32117e99455f004ae190b64ae`이고 기록된 original SHA가 실제 첫 report와 일치한다. 새 numeric/native 실행은 주장하지 않는다.
- Benchmark 출력 코드도 `difference_from_binary64_analytic_evaluation`과 binary64 precision 설명을 쓰도록 바뀌었다. 확인 SHA256: `1080d003d85541e39abf95d4236e02d51309ba0610d3df50906094ebf766cfa7`.
- V2 PNG를 실제 열어본 결과 의미와 coincident-point 주석은 맞지만 긴 왼쪽 ylabel의 단위 끝부분이 위쪽에서 잘린다. Root에게 두 줄 label로 저장값 재렌더를 요청했다. 이것은 새 수치 계산을 요구하지 않는 layout 수정이다.
- S1 CODE_REVIEW_CLOSED: 수정된 `can_refine()`는 aggregate reference execution COMPLETE와 native_source REF_READY를 모두 요구한다. 실제 실행부는 여기에 reference receipt 개수가 계획의 8개와 같고 모든 status가 COMPLETE라는 조건을 추가한다. Common_ic의 budget HOLD는 native_source의 budget 판정과 분리되어 있다. 초기의 잘못된 branch가 교정되었음을 직접 읽어 확인했다.
- Runtime reviewer의 최종 frozen runner SHA256은 `d844dec3be1cb397d48db319cd84a5f2314011db0cd0443d3d704d6252080275`다. 실제 파일과 `unit/tests/CAMPAIGN_REVIEW_GREEN.json`을 직접 읽어 14/14 orchestration 검증, exit0 기록을 확인했다. 이 검증의 native protocol 입력은 synthetic이며 새 native 실행으로 세지 않는다.
- S4 HELPER_REVIEWED_PENDING_ANALYZER_INTEGRATION: `verify_payload_record(receipt, payload_directory=None)`가 전체 payload file set·SHA, process exit/timeout, signature와 fixture/controls, worker closure, result shape/status, native owner/binary 및 point-log 개수까지 검증하는 것을 읽었다. Standalone analyzer의 호출 연결을 확인하면 이 항목을 닫을 수 있다. 이 시점의 closure는 최종 코드 전체의 승인 영수증이 아니다.

### 최종 closure와 파일 인계

최종 analyzer SHA256 `3e4cf60c6f4b11c2c8bcc3bd4ca6f5d1532f57e66f848d5d427f57eaa4f4d022`의 `completed_results(receipts, baseline_dir)`를 직접 읽었다. COMPLETE payload를 쓰기 전에 shared `verify_payload_record()`를 호출하고, 실제 baseline 파일의 manifest SHA, policy hash, frozen fixture hash 및 실행 manifest identity를 대조한다. Duplicate job ID와 서로 다른 native binary를 섞은 자료도 거부한다. 이 연결로 초기 S4의 검증 누락은 닫혔다. Payload 위치는 실제 receipt 경로를 기본으로 쓰며, 다른 저장 위치를 사용하는 경우 shared helper의 명시적 `payload_directory` 인수에 실제 확인된 경로를 제공해야 한다. 자동 경로 추측이나 자동 relocation을 완료했다고 주장하지 않는다.

`analytic_validation_v3/analytic_reference_diagnostics.png`를 실제 열어 왼쪽 label이 두 줄로 모두 보이고 단위도 잘리지 않는 것을 확인했다. Coincident finest-point 표시는 유지된다. 최종 PNG SHA256은 `04c73f0e75d1f1f9e07516d8bd3f8bffda670a2dcf9c2187ad8a7e8469645116`이다. V3는 저장된 numeric output의 layout 교정이며 9개 ODE를 새로 실행한 결과가 아니다. S3의 과학 명칭과 layout을 모두 닫는다.

이로써 이 검토에서 발견한 S1–S4의 해당 범위 수정과 확인은 종료한다. 재검토를 이유로 새로운 broad audit, 이전 native matrix, 이전 56개 검증을 반복하지 않았다. 이 문서와 theory 문서는 root의 최종 게시·백업 checkpoint에 포함할 수 있다. Native reference ladder, n128/256의 실행 결과 및 진정한 native global error bound는 `NOT_RUN`/`NOT_ESTABLISHED`로 남는다. 사용자 요청의 다음 이론·경량 코드·게시 단계와 이후 NCP 실행 단계를 구분한다.
