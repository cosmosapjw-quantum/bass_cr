# 별도 agent 코드 검토, original source

Reviewer `/root/frontier_code_review`; source bdc7bf6f4e9cc94d68c32e1752c62de5f809b0bf. 정적 검토, 실행0.

1. frontier.py68-71: solve([Atom.parse('low',0,3,0)],4,0)의 값3/2는 맞지만 low_diagonal 누락. 모든 경로에 공통 완전 witness를 반환할 것.
2. frontier.py61-62: solve([object()],4,0)에서 a.key가 타입검사보다 먼저여서 AttributeError. 타입검사를 먼저 수행.
3. frontier.py101: valid atom key lambda가 multiplier와 충돌. dual_prices/budget_multiplier 별도 필드.
4. test_frontier.py39: unittest.main을 맨 끝으로 이동해 독립 formulation class를 직접 실행에서도 수집.
5. assert 검사는 python -O에서 제거됨. fail-closed certificate 검증은 명시적 예외, primal 비음성 검사를 포함해야 함.
6. max_atoms/max_edges caller override의 상한을 검증하거나 default-only guard로 문서를 교정.

Full-event LP oracle는 독립 formulation이지만 같은 SymPy backend다. 새로운 구현에서 빈입력/zero mass/no-edge, invalid Atom, lambda atom, schema consistency와 runner 발견을 판별 검증할 것. Original scalar logic 수용 가능; API/certificate 수정 후 재검토 필요.
