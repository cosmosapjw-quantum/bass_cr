# R4 표현 선택과 판별 예제

선택한 변수는 edge별 unordered event 질량이다. Bin별 scalar 상한만 적용하면 어떤 두 bin이 서로 pairing할 수 있는지 잃는다. 반대로 atom3201개를 처음부터 조밀한 pair matrix로 최적화하면 약천만 pair 변수가 생기지만, 이 단위의 graph 가정은 bin rectangle 전체를 허용한다. 따라서 네-bin fractional matching에서 optimum을 얻고, 필요한 질량만 sparse atom coupling으로 올리는 구조를 채택한다.

## 왜 정수 matching이 아닌가

세 bin의 질량이 `(1,1,1)`이고 세 edge가 모두 허용되면 각 edge에 `1/2`를 놓아 총 cross event 질량 `3/2`를 얻는다. Electron leg는 각 bin에서1씩 소비한다. 정수 matching은 한 edge밖에 고를 수 없어1을 반환한다. 사건측도의 질량은 실수이므로 후자는 연구 대상의 feasible set이 아니다. 네 번째 zero bin을 붙여 실제 네-bin interface의 판별 fixture로 사용한다.

## Graph 제약을 구별하는 작은 구성

질량 `(1,2,4,8)`을 사용한다. 모든 수는 조건부 대수 fixture의 질량이다.

| Graph | primal 구성 | 상한 증명서 | rho |
|---|---|---|---:|
| empty | 모든 x=0 | y=(0,0,0,0) |0|
| bin0 중심 star | x01=1, 나머지0 | y=(1,0,0,0) |1|
| bin3 중심 star | x03=1,x13=2,x23=4 | y=(1,1,1,0) |7|
| triangle012, bin3 isolated | x02=1,x12=2,x01=0 | y=(1,1,0,0) |3|
| path01-12-23 | x01=1,x23=4,x12=0 | y=(1,0,1,0) |5|
| complete | 위 bin3 star 구성 | y=(1,1,1,0) |7|

각 행은 primal degree와 dual edge inequality를 직접 확인할 수 있다. 동일 marginal에서도 explicit graph에 따라 상한이 달라지므로, graph를 단순한 주석으로 저장하는 구현은 판별된다. Complete graph는 기존 `min(N/2,N-max n_i)=min(15/2,7)=7`과 맞는다.

## 선택 알고리즘과 독립 경로

Production은 각 bin의 left/right 복사본을 만든 대칭 이분 network에서 Edmonds–Karp 방식의 exact rational maximum flow를 사용한다. 흐름을 대칭화하여 unordered edge witness를 얻고, residual min cut으로 half-integral dual을 얻는다. Primal/dual equality는 solver 내부 상태와 별개로 다시 검사한다.

Independent reference는 네-bin half-integral dual 후보 `{0,1/2,1}^4`의81개 중 feasible candidate의 objective 최솟값을 직접 열거한다. 이 reference는 production의 augmenting path, residual cut 또는 flow construction을 호출하지 않는다. 64 graph와81 integer-capacity vectors를 대상으로 비교하여 topology/degeneracy를 모두 구별한다. 정확한 source coefficient에 대한64 graph 비교도 별도다. 이 실행은 C4 자원 admission 뒤 수행한다.

모든 feasible C는 optimum assignment를 `C/rho`로 scale하여 만든다. 원래 bin atom 큐에서 edge가 요구하는 두 submeasure를 같은 질량만큼 떼어 sparse transport로 결합한다. 남는 전자질량으로 fixed d의 diagonal portion을 채운다. 이 연결을 R5에서 증명한다.
