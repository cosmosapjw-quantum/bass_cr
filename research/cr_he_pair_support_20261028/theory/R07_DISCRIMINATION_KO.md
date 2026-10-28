# R7 실제 판별 검증

Wolfram Language evaluator를 timeConstraint8초로 실제1회 호출했다. 입력 code와 도구 원문은 `evidence/R07_WOLFRAM.json`, `R07_WOLFRAM_RAW.json`에 보존했다. Provider CPU는 unmeasured/null이며 local40CPU-s에0으로 기록하거나 합산하지 않았다.

실제 출력은6개 polynomial identity residual 모두0, triangle fractional optimum `3/2`, asymmetric star optimum `1`,16개 Boolean cut-indicator 경우의 implication `true`, fixed-d residual-leg inequality의 동치 `true`, 전체 `PASS=true`였다. 총10개 판별 그룹이다.

Triangle은 정수 matching을 잘못 사용하는 구현을, star는 complete-graph bound를 모든 topology에 그대로 사용하는 구현을 구별한다. Cut Boolean 검사는 dual의1/2 factor와 endpoint 위치를 구별한다. Residual-leg 식은 diagonal two-leg convention을, charge/chemical 식은 correction 부호를 검산한다. 이것은 작은 판별 계산이며 일반 finite theorem의 유일한 증명이 아니다. General proof와 atomwise construction은 `THEOREM.md`에 있다.

Initial Wolfram context의 관련 없는 entity 응답은 채택하지 않았다. 이 R7 계산에서 source fit, original spectrum, RR, 물리 kernel 또는 full native25를 실행하지 않았다. 실제 source coefficient에 대한 알고리즘 실행은 C4 자원 admission 뒤 수행한다.
