# BASS_CR 다음 이론 루프: branch와 geometry

## 시작점과 완료 기준

연구 단위는 **CR-THEORY-BRANCH-GEOMETRY-20261013**이다. 직전 KC1–KC7의 채택 결과, source SHA256, 원 출력과 branch `research/cr-kernel-cutoff-20261013`의 실제 HEAD `c450b00108dc05885a25d0d9c042cdcfe41bd659`를 이어받았다. 새로운 물리 history를 추정해 넣지 않고, DAG의 READY 두 노드가 요구한 실제 구성 문제를 진행했다.

선택한 노드는 `CR_THEORY_COUPLED_BRANCH_SOLVER`와 `CR_THEORY_GEOMETRY_KERNEL_REBIND`다. 전자는 실제 source rate를 사용한 branch domain·self-map·endpoint/error certificate 및 반응으로 raw atom이 변하는 교차를 요구한다. 후자는 실제 moved-parent event, geometry/cutoff 장부의 비중복, 명시한 표현 오차를 요구한다.

## 이번에 진행한 연결

1. **실제 coupled branch:** 원 HI sharing contribution과 별도 stopping edge를 사용한다. Trial neutral과 thermal electron density가 실제 rate에 들어가며 두 extent의 축약식에서 명시적인 box를 잡는다. Cutoff가 같은 두 grid node 사이에 남는다는 부등식과 수축 상계로 endpoint를 닫는다.
2. **반응 교차:** immutable raw event path에서 base count/energy와 생성 atom weight를 동시에 바꾼다. Prefix scan의 유한 종료를 증명하고, 실제 생성된 첫 node가 편입되는 extent를 정확히 구성한다. 동일 inventory의 복수 root를 확인해 inherited branch 선택 의미를 명시한다.
3. **질량 있는 geometry:** normal observer energy와 geodesic에서 massive work law를 유도한다. Bianchi I의 정확한 momentum transport를 구현하고, 원 source의 새 parent energy와 rate·sharing·daughter·lower trace를 함께 다시 결속한다.
4. **표현 오차:** count와 첫 energy moment가 보존되는 양의 energy projection을 정의한다. Lipschitz/C2 weak bound와 실제 HeI scalar rate의 within-cell bound를 구한다. Angular momentum/stress, threshold와 전체 branching-operator 미분은 별도 의무로 남긴다.

## 검증과 채택

이전 scientific suite는 다시 실행하지 않는다. 새 세 reference 프로그램, 실제 Wolfram scalar 24개와 부등식 4개, 실제 xAct tensor 8개를 기록한다. 각 결과는 실행한 source/input identity와 결속하고 독립 reviewer가 수식·domain·원 출력을 읽는다. Conditional derivation, finite-input exactness, FP64 관찰 오차, 물리/time error를 구별한다.

문서·코드·원 출력과 DAG를 동일 연구 단위에 보존한다. LaTeX/PDF와 source ZIP을 만들고, 이전에 승인된 additive research draft PR 및 Dropbox/Google Drive 이중 백업으로 인계한다. 물리 실행·global authority와 publication 상태를 합치지 않는다.

## 다음 DAG 순서

현재 구성 뒤 첫 의무는 full sharing families 및 stopping이 branch-dependent density를 통해 함께 변하는 adjacent-branch continuation이다. 병렬로 geometry–collision composition의 local splitting error를 유도한다. Angular moment remap은 raw angular packets를 유지한 상태에서 선택할 수 있는 별도 표현 연구다. 기존 selected scenario/observable/receiver application 노드와 전역 과학 gate는 그대로 남긴다.

기존 근거·정책이 이 작은 이론 구성의 선행조건을 막는 경우는 없었다. 새 blanket 승인·재검사 규칙을 추가하지 않았다. Network stream interruption으로 author agent를 저장된 파일에서 이어서 실행한 일은 환경 복구이며, scientific state를 초기화하거나 기존 통과 suite를 반복할 이유로 사용하지 않았다.
