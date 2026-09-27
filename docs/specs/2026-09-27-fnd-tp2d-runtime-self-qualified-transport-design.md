# FND TP2D Runtime Self-Qualified Full-Window Transport Design

## Goal

TP2C의 13-point static full18 geometry PASS를 전파 계산으로 연결하되, 정적 node 사이의 operator interpolation을 도입하지 않는다. Full-window transport가 실제 요청하는 모든 고유 time에서 analytic backend를 직접 resolution-qualify한 뒤에만 `S,H,D`를 제공한다.

## Architecture

`qualified_provider.py`는 physics-agnostic finite-resolution gate다. 각 exact binary64 time에서 ordered ladder를 평가하고, 두 인접 독립 resolution의 raw cross 차이와 각 full operator의 Hermiticity/metric screen을 검사한다. 성공 snapshot과 모든 attempted cross payload는 즉시 durable query receipt로 저장한다.

`analytic_adapter.py`는 기존 `assemble(...)`에 `phase_budget=None`, `sector='full'`을 강제하여 TP2B candidate semantics가 runtime production candidate로 새어들지 않게 한다.

`transport_policy.py`는 `Sdot=D+D†` sentinel과 temporal pair gate를 소유한다. `run_tp2d.py`는 TP1 DOP853 reference와 Cholesky metric-frame candidate를 이 provider 위에서 실행하고 create-only return package를 만든다.

## Scientific claims

성공 시 `all_runtime_operator_queries_qualified=true`와 `full_window_transport_qualified=true`만 새로 승인한다. 실제 solver가 질의하지 않은 모든 실수 time에 대한 uniform/global bound는 없으므로 `continuous_trajectory_error_bound=false`, `continuous_global_supremum_bound=false`를 유지한다. Capture, all-bound, b-grid, production은 열지 않는다.

## Failure semantics

Identity/input mismatch, new-test failure, runtime operator ladder exhaustion, query budget exhaustion, metric-connection failure, reference-transport failure, temporal-refinement exhaustion, runtime/environment failure를 서로 다른 status로 보존한다. 실패 후 threshold, basis, solver tolerance, ladder를 자동 변경하지 않는다.
