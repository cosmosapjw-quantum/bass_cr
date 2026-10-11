# PHYS02H: 정확 모멘트 경계와 열별 병렬 생성

## 1. 대상과 근거 수준

대상은 기존 CR cascade의 유한 에너지 격자, 고정 bath, 열방출 커널이다. 기존 source·원자 입력·sharing quadrature·FP64 연산과 물리 판정은 유지한다. H는 (i) 저장된 십진 모멘트에 조건부인 정확 산술 인증과 (ii) 동일 생성식을 열별로 계산하는 구현의 검증을 분리한다. 실제 F 실패, 원래 CSC 값 부재, G frontier 차단은 이 두 결과만으로 해제되지 않는다.

시간은 초, E는 eV, G=T0 Q는 원래 코드의 무차원 생성행렬이다. T0=10^10 s, 1 yr=31557600 s를 정확 상수로 사용한다. 열확률은 dF=K(t)dt/H0이며 총 주입에너지의 확률로 바꾸지 않는다. 유한 고정 bath의 장시간 지속 자체는 여기서 정당화하지 않는다.

## 2. 기록이 정의하는 두 확률 표현

저장된 selected 레코드의 p,R,S,mu,m2를 정확한 십진 유리수로 읽는 표현을 S라 하자. 각 birth j의 기록을 정확하게 읽고 w_j=H0_j/sum H0_j로 혼합하는 표현을 B라 하자. 부동소수 계산에서 허용오차 안에 일치하는 두 레코드도 유리수로는 다른 제약이 될 수 있다. 따라서 S의 경계와 B의 경계를 교집합하여 하나의 exact-input 인증으로 쓰지 않는다.

S에서는 그 레코드의 전체 및 잔여 모멘트 경계를 결합한다. B에서는 birth별 분포의 혼합으로 전체 p,R,S,mu,m2를 다시 정의하고, 그 정의와 정확히 양립하는 전체·pooled residual·birth residual 경계를 결합한다. B는 독립적인 기록 기반 표현이며 기존 physical SSOT를 교체하지 않는다. 두 표현 사이의 모든 차이는 정확한 유리수와 표시용 십진값으로 남긴다.

## 3. 비어 있지 않은 모멘트 분포군

p=P(tau<=T), R=E[(1-tau/T)_+], S=E[(1-tau/T)_+^2], mu=E[tau], m2=E[tau^2]로 정의한다. 여기서는 실제 입력의 0<p<1, H0>0을 검사한다.

초기 부분의 U=(T-tau)/T | tau<=T는 [0,1]에 있다. a_e=R/p, b_e=S/p라 쓰면 필요한 조건은 0<=S<=R<=p 및 R^2<=p S이다. 비퇴화 경우 U의 두 원자 0, b_e/a_e와 가중치 1-a_e^2/b_e, a_e^2/b_e는 그 조건 아래 지지집합과 두 모멘트를 정확히 만족한다. U=0은 tau=T에 대응하며 초기 p에 포함된다. 이 유한 원자 증인은 분포군이 공집합이 아님을 증명할 뿐, 실제 유한율 cascade가 원자적이라는 주장이 아니다.

q=1-p와 X=tau-T | tau>T를 두면

    a=E[X]=[mu-T(1-R)]/q,
    b=E[X^2]=[m2-2T mu+T^2(1-S)]/q.

이는 전체 모멘트에서 초기 부분의 모멘트를 빼서 얻는다. 각각 s와 s^2 차원이다. q>0에서 a>0 및 v=b-a^2>=0을 검사한다. v=0이면 X=a의 한 원자가 증인이다. v>0이면 x0=a/2, x1=a+2v/a는 둘 다 양수이고, w1=(a-x0)/(x1-x0), w0=1-w1은 평균 a와 분산 v를 정확히 재현한다. 초기·잔여 증인을 p와 q로 결합하면 p,R,S,mu,m2를 모두 정확히 재구성할 수 있다. 음의 분산을 자르거나 초기/잔여 질량을 재정규화하지 않는다.

## 4. 생존확률 경계와 유리수 끝점

X>=0, a=E[X]>0, v=E[X^2]-a^2>0에서 이전 G의 일반 2모멘트 경계는

    L(x)=(a-x)^2/[v+(a-x)^2]  (0<=x<a), 그 밖에는0;
    U(x)=1 (x<=a), a/x (a<x<b/a), v/[v+(x-a)^2] (x>=b/a).

하한은 Cantelli를 왼쪽 사건에 적용하고, 상한은 비음수 지지집합의 Markov와 오른쪽 Cantelli를 결합한 결과다. 분기 b/a에서 두 상한은 a^2/b로 일치한다. v=0은 strict survival P(X>x)=1[x<a]로 별도 처리한다. T에서는 잔여 양의 지지집합에 의해 정확히 P(tau>T)=q를 사용한다.

각 모멘트 레코드의 전체 경계와 q L(t-T),q U(t-T), 그리고 B 표현의 sum w_j q_j L_j/U_j를 해당 표현 내부에서 결합한다. Q_f=inf{t:F(t)>=f}, epsilon=1-f라 하면

    L(t_lo)>epsilon  =>  F(t_lo)<f  =>  Q_f>t_lo,
    U(t_hi)<=epsilon =>  F(t_hi)>=f =>  Q_f<=t_hi.

따라서 아래 끝점은 strict, 위 끝점은 closed 조건이다. H는 정수 초 격자에서 정확 유리수 doubling/bisection을 수행하고, 마지막 조건을 분모가 양수인 정수 교차곱으로 다시 기록한다. 종료조건은 소수점 표시의 근접성이 아니라 위 부등식이다. 표에 쓰는 연 단위 소수는 표시이며 인증값은 정수 초와 유리수 여유다.

이 인증은 입력 십진수가 정의하는 비어 있지 않은 분포군에 대한 정리다. 저장 모멘트 자체의 물리 오차, 실제 생성행렬의 전방 오차, 격자 수렴, 커널의 phase-type 제약 또는 이론 근사 오차를 인증하지 않는다. G-R01의 원래 FP64 끝점은 그대로 보존된다.

## 5. 생성행렬의 열 분해

기존 Cascade._generator의 j번째 반복에서 변경되는 과학 배열은 로컬 col 하나다. E, atomic 데이터, stopping과 반응률은 읽기 전용이고, normalization_diagnostics는 계산 순서 기록을 append할 뿐 다음 열의 과학 계산에 피드백되지 않는다. 따라서 원래 연산식의 정확한 수학적 형태는

    G[:,j]=T0 C_j(E, atomic, fixed parameters),
    G[:,j]=0 for absorbing-ledger columns.

서로 다른 열 j의 C_j에는 재귀 의존성이 없다. 열 집합을 서로소 타일 I_r로 분할하여 각 열을 한 번씩 계산하고 원래 열 순서로 이어 붙이면 같은 행렬이다. 이는 선형성만을 가정한 일반 주장보다 강하며 현재 source의 읽기/쓰기 의존성으로 확인한다.

구현은 원래 함수의 AST에서 바깥 enumerate(self.E) iterator만 승인된 열 목록으로 제한한다. precompute, 열 내부 drift/ionization/excitation 순서, quadrature, np.sum/dot/bincount 입력과 연산을 유지한다. 각 열의 flatnonzero는 정렬된 고유 행 index를 주므로 같은 (i,j) 원소를 worker 사이에서 합할 필요가 없다. CSC data와 indices 구간을 열 순서로 복사하고 indptr를 정수 offset으로 구성한다. MPI/프로세스 순서에 따른 부동소수 reduction은 없다.

수학적 분해의 동일성이 서로 다른 런타임의 byte identity를 보장하지는 않는다. NumPy와 BLAS의 dispatch 및 연산 구현은 별도 출처다. 같은 source/input/runtime의 원본 직렬 행렬과 후보 행렬을 비교하여 data/indices/indptr, E, rates, diagnostic sequence의 실제 byte parity를 판정한다. source를 공유한 비교라는 의존성을 명시하고 독립 검토에서 AST 변경 범위와 조립 불변식을 확인한다.

## 6. 실행 장소와 다음 실제 계산

현재 assistant 환경에서 관측한 cgroup memory.max는8GiB, CPU quota는8 CPU다. 이곳에서 유리수 분석, 240상태 전체 행렬, 저장된9600격자의 선택16열을 실행한다. 기존 전체9600 원본 launcher는 최소 작업 메모리12GiB를 요구하므로 그 원본 전체 생성은 여기서 시작하지 않는다. 이 분류는 시간 이름표가 아니라 실제 메모리 admission에 따른다.

NCP에는 전체9600 같은 입력의 직렬/열별 병렬 쌍만 새 유한 계약으로 넘긴다. 병렬 모델2개와 coordinator/worker 모두를 실제 affinity·quota·RAM에 포함하며,64 CPU가 실제 허용되면 약30worker/model을 사용할 수 있다.128GB 표기를128GiB로 동일시하지 않고 바이트로 판정한다. 최소16GiB의 여유와 보수적인 직렬 lane 메모리12GiB씩을 확보한다. 원래 F 예약은 재사용하지 않는다.

두 모델 각각 원본2회·후보2회의 전체 qualification은8개 논리적 전체 생성에 해당한다. 각 worker의 부분 생성 호출과 평가한 열 수는 따로 기록한다. 새 pulse/resolvent/solve/expm은0이다. 후보의 전역 정확성은 NCP 실측 전에는 미평가이며,64-core 속도 향상도 예측 수치로 제시하지 않는다. 새로 만든 G는 원시 CSC 값까지 보존하고 현재 직렬 기준과 묶는다. 과거 G 해시와의 일치는 별도 정보이며 이전 E/F 상태의 자동 채택 조건으로 쓰지 않는다.

## 참고 원전

- Bertsimas & Popescu, SIAM J. Optim.15(3),780–804(2005), https://epubs.siam.org/doi/abs/10.1137/S1052623401399903 : 모멘트 확률경계의 일반 틀. 위 CR 잔여/혼합 유도는 이 작업의 직접 유도다.
- SciPy CSC representation, https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csc_matrix.html : 열별 data/indices/indptr와 canonical format 정의. 실행버전은 실제 receipt의1.17.0을 따르며 문서의 current-version 이름을 runtime pin으로 사용하지 않는다.
- NumPy SIMD runtime dispatch, https://numpy.org/doc/stable/reference/simd/index.html : 런타임 CPU별 kernel 선택. 과거 F 오류의 원인 확정 자료로 사용하지 않는다.
