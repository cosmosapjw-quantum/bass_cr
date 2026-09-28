# R4C temporal-closure preregistration draft

상태: **DRAFT_NOT_EXECUTION_AUTHORIZATION**

목표는 frozen TP2D temporal screens를 변경하지 않고 기존 N=384 ladder를 이어서 full-window finite-basis transport를 닫는 것이다.

고정 screen:
- candidate-to-reference phase-aligned metric distance <= 1e-6
- consecutive-refinement phase-aligned metric distance <= 1e-6
- candidate metric-norm drift <= 1e-8

Observed N doubling에서 state metric error order는 ~2다. 최신 pair를 기준으로 N=768 예상값은 reference ~6.585723e-07, refinement ~1.975989e-06; N=1536은 각각 ~1.646261e-07, ~4.939462e-07. 이 예측은 gate가 아니라 scheduling heuristic이다.

실행 순서가 승인되면:
1. 정확히 동일 source/model/basis/trajectory/time window/operator qualification policy를 유지한다.
2. N=768만 먼저 실행한다. 새 native operator query가 필요한 경우 그 수와 cache hit/miss를 별도 ledger로 보존한다.
3. reference distance와 N384→N768 refinement distance를 frozen screen으로 판정한다.
4. 둘 다 PASS면 즉시 종료한다.
5. refinement만 FAIL하고 observed order가 기존 ~2차 거동과 양립하면 N=1536 한 단계만 실행한다.
6. order collapse, operator qualification failure, resource identity drift가 나오면 확장하지 않고 blocker로 종료한다.
7. temporal closure가 되어도 capture_execution_allowed를 자동 true로 바꾸지 않는다. 다음 all-bound/asymptotic/capture gate를 별도로 연다.

금지: threshold 완화, reference solver tolerance 변경, 새 basis/b/z-window로 몰래 전환, 기존 R2 재실행, b-grid/cross-section 실행.
