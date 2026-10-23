# C22D 최종 독립 검토

## 판정

**PASS_SCOPED — 과학 수용을 막는 지적 0개.** 선언한 finite-source H1 CI 모형의 새 계산 4개에 대해 저장 시점, solver가 수락한 시점, 같은 입력의 BDF–Radau 비교를 수용한다. 이 판정은 전체 thermochemical/radiative closure, 연속 시간 오차 상계, 실제 원자율 전체 범위의 정확도 인증을 뜻하지 않는다. `global_error_bound=null`을 유지한다.

검토자는 모델·rate provider·runner·analyzer를 구현한 agent와 별개다. 추가 정적 검토자에게 에너지·전하·상태 투영·signed stress의 원코드를 별도로 제공했다. 두 검토 모두 연구 RHS나 rate provider를 실행하지 않았고 ODE 재실행은 0이다. 새 독립 검산은 저장된 배열의 합·차·norm·hash만 계산했다.

| 축 | 검토 종료 상태 |
|---|---|
| EXECUTION | 저장 배열 독립 검산 및 정적 검토 COMPLETE_SCOPED; ODE/RHS/provider 0 |
| PUBLICATION | 검토 산출물 로컬 생성; 최종 commit/외부 게시 ACK는 parent가 별도 관리 |
| BACKUP | 검토 결과를 최종 패키지에 포함하도록 인계; 별도 provider 저장 완료를 주장하지 않음 |
| DAG | C22D finite-source 수용 검토 완료; 다음 line-energy/radiative closure 계약으로 연결 |

## 검토 대상과 identity

대상은 `research/cr_c22d_cold_ci_20261022`이다. runtime 42개 파일의 SHA256/크기를 `evidence/SOURCE_FREEZE.json`에 대조했고 모두 일치했다.

- Runtime source identity: `2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72`.
- 수치 분석 실행본: `analysis_v1/analyzer_executed_v1.py`, 45,148 bytes, SHA256 `3391cfd378e76c31c4f3509c395f80ded2b8a6eef7b0487bb7591facffadde5e`.
- 분석 manifest의 기존 28개 산출물은 검토 시 모두 일치했다.
- 이후 `analyze.py`의 figure-only 수정은 별도 renderer identity다. 기존 수치 실행본을 그 수정본으로 소급 대체하지 않는다.

독립 검산 코드 `review_saved_arrays.py`는 NumPy와 표준 라이브러리만 import한다. 실제 실행은 CPU4, native thread 1, wall 1.321 s였고 CPU55를 사용하지 않았다. `SAVED_ARRAY_REVIEW.json`은 298개 source·artifact·array·비교 검사를 기록하며 실패는 0이다. 이 수는 연구 성과의 척도가 아니라 검토 범위를 식별하는 기록이다.

## 보존량과 배열의 독립 검산

원 raw의 저장점 804개와 수락점 8,047개를 읽었다. 각 accepted summary의 `eta`와 78행 full-state 배열이 원 raw의 accepted 배열과 정확히 일치하는지 확인했다. atomic label에서 charge와 isotope grouping을 독립 구성하고 `math.fsum`으로 다음을 계산했다.

1. 원자 population 합과 charge-weighted electron 수에서 핵종별 보존량, 전하 및 입자 수를 계산했다.
2. 열·binding·resident UV·escaped RR·gas work·UV work·Compton bath·escaped n2의 여덟 항을 합했다.
3. 남은 UV photon과 누적 PI event로 photon 장부를 계산했다.
4. 현재 particle 수와 thermal energy에서 온도를 재구성했다.
5. signed radiation 합을 취한 뒤 norm을 계산하고 cancellation 분모와 defined mask를 별도 확인했다.

| 실행 | saved | accepted | accepted 에너지 최대 상대 잔차, 독립 `fsum` |
|---|---:|---:|---:|
| BDF registry control LRS, CI OFF | 201 | 1,618 | 1.2695932e−11 |
| BDF CI LRS | 201 | 1,618 | 1.2697340e−11 |
| BDF CI FLRW | 201 | 1,616 | 1.4458887e−11 |
| Radau CI LRS | 201 | 3,195 | 1.8771477e−15 |

사전 에너지 기준은 1e−8이다. saved와 accepted를 합친 독립 핵종 잔차 최대는 2.2204461e−14, 전하 2.4066036e−15, photon 1.6098234e−15였다. 입자 수로 재구성한 온도와 저장 온도의 상대 차이는 최대 6.6613381e−16이었다. 원 summary와 `fsum` 합산 순서가 달라 마지막 binary64 rounding 수준의 값 차이는 있을 수 있으며 양쪽 모두 동일한 사전 gate를 통과한다.

21개 atomic population, 78 full state, 75 solver state가 유지됐다. `n`, `T_0`, `T_1`은 선언된 exact-zero inventory이며 이 세 좌표만 solver에서 제외됐다. missing species를 임의로 0 채움으로 대체한 근거는 없다. 작은 음수 UV 값은 원자료에 유지되며 clipping하지 않았다.

## 사전 등록한 아홉 지표의 방법 비교

BDF와 더 엄격한 Radau의 저장 `eta` 201개는 정확히 같았다. interpolation을 사용하지 않고 원 배열에서 차이를 다시 계산해 `STRICT_REFERENCE.json`과 배열 파일에 대조했다. 허용치 2e−7은 바뀌지 않았다.

| 지표 | 최대 정규화 차이 |
|---|---:|
| 온도 | 9.4306293e−9 |
| 전자 밀도 | 6.1515982e−9 |
| Thomson optical depth | 1.7911294e−9 |
| full Frobenius shear norm | 8.7878746e−9 |
| full Frobenius radiation norm | 3.3519421e−9 |
| H1 이온화 분율 | 6.1507388e−9 |
| Compton bath 누적 에너지 | 3.9830897e−10 |
| n2 누적 escaping energy | 2.9218151e−8 |
| H1 CI 누적 사건 수 | 6.3569845e−8 |

온도 등 여섯 지표에는 `max(abs(reference),1e−8*reference_peak,1e−30)`를, 누적 bath/n2/CI에는 uniform reference-peak scale을 사용했다. 수용은 두 solver가 이 유한 sample에서 일치한다는 범위다.

## 에너지·전하 식과 코드 대응

`model.py:H1IonizationModel.rhs`의 반응률은

\[
r=\frac{n_e X_{\mathrm{H1},0}q_{\mathrm{core}}(T)}{H}.
\]

CI는 H1 ground와 ion에 각각 −r, +r를 더하고 U에 −χr, CI counter에 +r를 더한다. 정규화된 atomic 좌표에는 각 isotope scale로 나눈 값을 사용한다. 새 CI counter 자체를 escaping energy에 합하는 경로는 없다. binding 증가 +χr가 열손실 −χr와 상쇄한다.

상속된 C22A 온도는 `T=2U/(3 kB N)` 및 `N=sum(X_atomic)+X_e`로 계산된다. CI에 따른 `N′=r`가 온도에 자동 반영되어

\[
T'_{\rm CI}=-\frac{2\chi/(3k_B)+T}{N}r
\]

가 된다. 별도의 온도 교정항을 다시 더하지 않는다. 누적 `χ*C_CI`는 CI가 thermal에서 binding으로 전달한 사건 에너지이며, 모든 PI/RR가 함께 작용한 전체 binding 순변화와 구분한다.

새 registry는 H1/D/T binding, PI heating, RR export, CI loss에 χ=13.6058 eV를 공유한다. HI PH2 단면적의 에너지 축·계수는 그대로 두고 낮은 support를 새 문턱에서 자른다. 원 RR number/capture fit은 유지되며 Milne/LTE consistency는 OPEN이다. 13.6058 eV의 지위는 CCC source convention 정렬이며, 정밀한 실제 H1 threshold 보정으로 해석하지 않는다.

H1-only CI는 H1과 D의 공통 이온화 분율 subspace에 서로 다른 미분을 주므로 이전의 그 특정 quotient를 유지하지 않는다. 모든 isotope quotient의 불가능성에 대한 주장은 채택하지 않았다.

## CI 효과와 registry 효과의 분리

`MATCHED_EFFECTS.json`의 모든 최종 차이와 최대 절대 차이는 원 raw 산술과 일치했다. CI ON/OFF는 같은 새 registry와 공통 초기조건을 사용한다. registry-only 비교는 새 registry의 CI OFF와 기존 C22C LRS를 비교하며 공통 입력과 선언된 solver 설정을 유지한다.

같은 새 registry에서 CI ON은 최종 온도를 0.0017459670 K, 전자 밀도를 4.5243650e−12 cm−3 낮추고, Thomson depth를 3.1421143e−8 높였다. 최종 H1 CI 누적 사건 수는 7.37974053e−6/Href다. 별도로 old C22C에서 새 registry CI OFF로의 최종 온도 차이는 −0.0117199645 K이므로 이 둘을 CI 효과 하나로 합치면 안 된다.

**전단의 작은 출력 차이는 이번 자료에서 분해되지 않는다.** CI ON−OFF의 `Sigma_F` 최대 차이 1.8312615e−11은 CI ON의 BDF−Radau 최대 차이 1.6534545e−10보다 작다. 최종 차이에서도 같은 문제가 있다. 이번 scoped acceptance에 추가 ODE는 필요 없으며, 전단에 대한 CI 효과의 정밀 측정 주장을 후속 의무로 남긴다. 다른 지표의 모델 차이가 곧 물리적 오차 상계가 되는 것도 아니다.

최종 전자 수가 CI ON에서 감소하는 사실은 사건 장부로 직접 설명된다. 두 coupled 경로의 ON−OFF 최종 차이는 다음과 같다.

\[
\Delta C_{PI}=1.9317881\times10^{-14},\quad
C_{CI}=7.37974053\times10^{-6},\quad
\Delta C_{RR}=8.25804404\times10^{-6}.
\]

따라서 `ΔXe=ΔC_PI+C_CI−ΔC_RR=−8.78303490052e−7/Href`이다. 원 `ne/nHref` 차이와 3.45e−18만 다르다. 이는 두 coupled 해의 누적 장부 비교이며, 전체 경로를 다른 물리 과정으로 따로 재적분한 결과는 아니다. 수치는 `FINAL_CHARGE_DIFFERENCE.json`에 저장했다.

## 조건부 진단의 범위

Ground-only Saha inverse 진단에서 실제 ne를 사용한 `ne*K3/alpha_RR` 최대값은 약 2.07344e−21이다. 이 값은 채택된 finite source의 ground inverse이며 전체 준위 inverse network·omitted-process bound는 OPEN이다.

First-gap p=1.127과 PL p=1은 같은 채택 경로에서 비교했다. accepted LRS mesh의 두 사다리꼴 functional 비율 변화는 −1.9246696e−5이다. 같은 PL 사다리꼴 적분 자체와 ODE CI counter의 상대 차이는 +1.1534592e−4이므로 전자를 정밀한 event-counter 변화로 바꾸어 제시하지 않는다. 격자와 경로가 고정된 functional sensitivity로 보존한다. 원자료의 physical tail, interpolation, secondary thermalization, higher-level radiation, full closure는 별도 의무다.

## 실제 그림 검토와 기록 교정

`analysis_v1/figures_v2`의 PNG 4개를 직접 열어 보았다. matched effect와 registry 변화의 별도 패널, signed stress와 scalar norm의 별도 패널, 아홉 지표의 기준선, conditional diagnostic의 scope 표시를 확인했다. 시간/η축은 0 이상으로 표시되고 v1에서 보고된 음수 padding 및 label 겹침이 해소됐다. 읽을 수 없는 잘림이나 겹침은 관측하지 않았다. PDF는 PNG와 같은 렌더 작업의 보존 파일이며 본 검토에서 별도의 PDF rasterization은 하지 않았다.

Frozen `SUMMARY.json`의 `failure_scope.all_gate_failures_preserved=false`는 분석 gate 실패가 0개라는 상황을 표현하는 데 모호하다. 본 검토는 이를 다음처럼 명확히 기록한다: **analysis gate failure count=0; 기존 light-check 실패는 별도 원본과 진단에 보존됨.** 원 v1 JSON의 bytes는 바꾸지 않는다. `evidence/LIGHT_CHECK_ACCEPTANCE.json`과 독립 preflight review에는 원 34/36 PASS, invalid predicate 두 개, exact binary64 addition proof 및 replacement 이유가 보존되어 있다. tolerance를 느슨하게 해서 과거 실패를 PASS로 바꾼 기록은 없다.

표시 수정의 `RENDER_COMPLETE.json`은 accepted summary 재계산 0, provider/RHS/ODE 0을 기록한다. 수치 분석 완료본과 v1 그림을 보존하고 figure-only 산출물로 교정했다. inaccessible conversations는 UNAVAILABLE, 원 nuclear network PNG는 NOT_RECOVERED_NOT_READ, VigilODE P02 C6FAIL과 외부127 JSON/재적분 이력은 유지한다.

## 다음 단계에 넘기는 조건

C22D는 채택한 dilute, single-Maxwellian, non-tilted LRS finite-source 문제의 수용을 완료했다. 원자율의 실제 coverage 계약, finite-mass/isotope energy convention, line trapping/reabsorption, 2s mixing·cascade·spectrum, secondary electron thermalization, DR/CX/free-free 등 누락된 에너지 교환은 다음 연구 단위에서 다룬다. full nuclear high-energy와 general triaxial/tilted/polarized CMB는 HOLD다. 최종 게시·백업 상태는 parent가 실제 commit/provider ACK/byte readback 근거로 별도 확정한다.
