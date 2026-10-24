# 실행 전 구현 계약의 구체화

Root의 첫 static code-path 읽기에서 확인했고 S0 게시 및 어떤 테스트/primary 실행보다 먼저 적용한다. 원 FROZEN_CONTRACT의 물리 입력, 식, 허용오차와 R6 analytic 판정은 바뀌지 않는다.

1. `validate_case`의 truthy units/frame 검사만으로는 잘못된 단위·frame 문자열을 거부하지 못한다. 고정 CASE의 정확한 unit mapping/frame/clock을 비교하고 실제 잘못된 문자열 control을 추가한다. immutable CASE SHA 검사는 계속 유지한다.
2. MFPT Poisson의 수용 기준 `2e-12`는 다른 선형계와 같은 backward scaled residual이다: `abs((-G)T-1)/(abs(G)abs(T)+1)`. q의 T0=0을 포함한다. 가까운 native knots에서 cumulative T의 차분을 다시 뺀 flux residual은 별도 진단으로 남길 수 있으나, 조건이 다른 flux-scale ratio를 이 frozen operator residual로 표시하지 않는다. 원 기준은 동일하고 아직 측정된 FAIL/PASS가 없다.
3. 저장된 EE matrix의 delta-scoped column/balance 비교에는 저장된 Q 배열을 사용한다. 기존 EE generator를 재구성하는 반복 과학 검사는 필요하지 않다. 새 이온의 conductance, Q와 합성 Q만 구축한다.
4. 초기 pulse power에 exposure를 다시 곱한 별도 frozen-drift heat 필드는 요청된 관측량에 포함하지 않는다. Exposure는 source rate를 초기 population으로 바꾸는 데 한 번 사용한다. 저장하는 순간 bath power와 source-rate-weighted moment의 서로 다른 단위를 유지한다. 그림용 새400개 EE curve 평가와1200개 ion curve 평가는 별도 횟수로 기록한다.

PREPARED_V2는 실제 실행 전 준비 identity로 보존하며 수정된 PREPARED_V3를 실행 source로 동결한다. 해당 source에 대한 focused controls와 독립 C9를 수행한다. 이 변경으로 원 PR102 실패·비용·입력은 달라지지 않는다.

추가 검증 계수 적분은 C6에서 theta_t/theta_b 세 비율의 normalized Maxwell mean을 supplied analytic formula와 비교하는 oracle이다. 실제 시작한3 coefficient-validation quadratures(각각3 interval 분할)를 별도 계수한다. Source quadrature와 physical thermal-rate provider quadrature는0이다. 실제 결과/횟수는 run receipt가 authority다.
