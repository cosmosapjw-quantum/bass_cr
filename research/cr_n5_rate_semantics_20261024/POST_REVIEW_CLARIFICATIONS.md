# C9 이후 문서 해석의 명시

독립 C9의 과학·코드 판정은 `PASS_WITH_NONBLOCKING_FINDINGS`, 열린 blocking0이다.
원 frozen contract, 이론 문서와 reviewer 판정은 당시 근거로 보존한다.
남은 두 문서 항목은 다음과 같이 해석한다. 코드·수치 결과·입력은 바꾸지 않는다.

1. **실행 메모리와 import.** 사전 frozen revision2가 초안의 256 MiB/no-heavy-libraries 문장을 대체한다. 실제 허용은 512 MiB address space와 pinned PHYS83 constructor를 import하기 위한 NumPy/SciPy다. 실제 PRE_EXECUTION과 peak RSS가 이를 기록한다. provider `moments`/`evaluate` 또는 새 구적의 허가는 포함하지 않는다.
2. **ε=0 API 극한.** 과학 입력은 ε∈{0.01,0.1,0.5}로 고정됐다. 배송 API는 수학적으로 연속인 ε=0에서 hcrit=0을 추가로 허용하며 해당 exact-zero control은 이미 검증했다. 일반 API domain은 0≤ε<1, m>0이다. 이론의 negative-test 목록 중 ε≤0 거절 문구는 이 API의 zero-limit 확장을 포함하지 않은 문서 표현으로 해석한다. 음의 ε 및 ε≥1은 거절한다.

선택된 과학 계산의 tolerance, physical closure, primary 결과 및 원 independent numerical check는 그대로 유지한다. 추가 과학·검산 실행은 0이다.

EXECUTION: documentation clarification only | PUBLICATION: included in scoped payload | BACKUP: included in canonical payload | DAG: no gate change
