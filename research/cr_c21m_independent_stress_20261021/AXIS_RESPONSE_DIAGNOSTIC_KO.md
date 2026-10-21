# 완료한 collisionless pilot의 축 응답 사후 진단

REC PR116의 anchored additive 방법을 C21M의 실제 완료한 27점에 적용했다.
외부 warm729의 정확도를 가져오는 대신, 현재 collisionless z20→4, full40-state,
full Frobenius 데이터의 저장된 101개 시점 전체에서 직접 비교했다.

\[
\widehat F(S,m,r)=F(S,m,0)+F(S,0,r)-F(S,0,0).
\]

각 S0에서 물질축과 복사축 및 공통 기준점을 사용하면 세 S0 slice 전체에서
support는 15점이다. 나머지 12개 혼합점은 예측식에 넣지 않고 검산에만 사용했다.
네 signed 관측량 S, Pm, Pr, Ptot를 각각 재구성했다. 계수를 적합하지 않았다.
총응력의 독립적 재구성과 재구성한 두 성분의 합 사이의 최대 차이는
`8.131516293641283e-20`으로, 이 별도의 부동소수점 closure 잔차도 보존했다.

| signed 관측량 | 전체 저장 시점 최대 절대잔차 | 최종값 최대 절대잔차 | 최종 support scale로 나눈 최대잔차 |
|---|---:|---:|---:|
| S | 1.2601685821147374e-9 | 1.2594991629505392e-9 | 8.863047512291639e-7 |
| Pm | 1.1647880056851224e-9 | 6.541676293117283e-10 | 5.2070622676396835e-5 |
| Pr | 1.4831875142125306e-9 | 1.3007594153199398e-9 | 2.0538024620937846e-5 |
| Ptot | 2.5829708926876404e-9 | 1.954927044633362e-9 | 3.0333813463251443e-5 |

잔차의 부호는 actual minus prediction이다. support scale은 혼합점의 값을
사용하지 않고, 15개 support의 해당 관측량 절댓값 최대로 정의한다. 전체 시점과
최종 시점의 scale을 구분한다. 큰 초기 shear 배경이 정규화 분모를 지배할 수
있으므로 각 축 응답에서 같은 S0의 기준점 값을 뺀 increment scale도 함께 저장한다.
S의 최종 최대잔차를 이 increment scale로 나누면 `2.596106524902794e-5`다.

0 부근의 상대오차를 작은 임의 floor로 가리지 않았다. 예를 들어
`s1_m0_r2`의 최초 Ptot는 `-4.2184816721217536e-20`, 재구성은
`-2.710505431213762e-19`, 절대잔차는 `2.2886572640015867e-19`이므로
pointwise 상대잔차가 `5.425310436042429`다. 이는 초기 반대 stress의 거의
완전한 상쇄에서 나타난다. 실제 값이 정확히 0인 S의 네 초기 표본에는 상대값을
정의하지 않고 mask를 보존하며, 절대잔차는 모두 남긴다. 표본을 제거하거나
물리적 0으로 clipping하지 않는다.

REC116의 `math.fsum` 합산과 80자리 Decimal의 stored-binary64 residual 검사를
trajectory 배열에 맞게 적용했다. 이 보조 검사는 계산된 mixed interaction과
재구성 산술의 rounding 차이를 살펴보는 유한 정밀도 검사다. 정확한 유리수
연산이 아니며, 수학적으로 0인 stored-float interaction에도 매우 작은 비영
잔차가 남을 수 있다. 독립 검토에서 이 한계를 확인하여 v2의 명칭을 바로잡았다.
ODE 해의 오차를 증명하지 않는다.

최종 채택 경로 `axis_response_diagnostic_results_v2/`에는 12×101×4의 actual·prediction·residual·
80자리 stored-float interaction·정규화 값·정의 여부를 담은 NPZ, 전체 trajectory와
endpoint CSV, 원 raw/source binding, summary 및 output hash가 있다.
원 27개는 신규 26 적분과 기존 C21L 중심 1개 재사용으로 구성되며 실제 중심의
아주 작은 초기 matter/radiation offset도 그대로 사용했다.

초기 v1 산출물 `axis_response_diagnostic_results/`와 그 실행 소스
`executed_axis_response_diagnostic_v1.py`는 역사적 증거로 보존한다. v2는 명칭과
유한 정밀도 설명을 정정한 후처리이며, 원 과학 적분을 다시 하지 않았다.

이번 작업의 새 ODE와 benchmark 실행은 각각 0이다. 작은 진폭의 이 유한 격자에서
축 응답이 거의 가산적이라는 사후 근거를 얻었지만, mixed interaction은 0이 아니며
matter/radiation은 여전히 중력적으로 결합한다. 다른 진폭·다른 source·저장되지 않은
시점·연속 domain·미래 125점으로 정확도를 확대하지 않는다. 원 exact 결과를
대체하지 않았고 production surrogate를 승인하지 않았다. `global_error_bound=null`.
