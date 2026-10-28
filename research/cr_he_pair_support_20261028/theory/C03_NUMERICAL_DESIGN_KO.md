# C3 exact numerical design

이번 문제는 이미 고정된 finite atomic source를 대상으로 한다. 새 연속 적분·grid extrapolation·kernel closure를 만들지 않는다. Stored binary64 coefficient를 정확한 유리수로 올린 뒤 graph 최적화와 atom splitting을 모두 Fraction 연산으로 수행한다. 이 선택은 algebraic residual을 없애지만 물리 input error를 없애지 않는다.

Production network는10vertices(s,4left,4right,t), 최대8terminal+12cross forward arcs다. BFS shortest augmenting paths의 Edmonds–Karp 순서를 고정한다. N>0의 middle capacity2N과 N=0의 explicit branch로 infinity를 float로 표현하지 않는다. Residual reachability에서 half-integral cover를 만들고 solver와 분리된 checker가 primal/dual equality를 확인한다.

Atom lift는 최대3201개의 원래 atom queue를 순회한다. Pair mass를 min(residual-left,residual-right,remaining-edge)만큼 배정하므로 양수성과 exact marginal을 보존한다. Diagonal residual은 사용한 leg의 절반을 event mass로 기록한다. 조밀한3201²pair table은 만들지 않는다. Deterministic ordering은 동일한 input의 witness 재현성을 제공한다.

독립 reference는 production의 residual network를 재사용하지 않는다. 81개 doubled-dual tuples의 feasible cover만 열거한다. Integer fixtures는 정수 dot products, source는 exact Fraction sums를 사용한다. 모든64graph와degenerate capacities를 확인하며 중복 broad suite를 반복하지 않는다.

수치 근거는 exact certificate, exact atom marginals, exact scale/window 관계, serialization roundtrip 및 L1 capacity sensitivity다. Plot에는 저장 결과를 presentation float로만 바꾼다. Null physical error와 conditional graph status를 figure에도 표시한다. Source spectrum·support·temperature·history의 불확실성을 임의의 numerical tolerance로 대체하지 않는다.
