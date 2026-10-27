# R7 수치 설계와 고정 판별 입력

## 구성

비선형 fine/coarse 방정식을 production 경로에서 직접 적분하는 대신, 증명된 오차 비교계의 endpoint와 블록 내부 상계를 계산한다. 질량작용 사건 열은 정확한 정수, 계수와 interval endpoints는 Fraction이다. H/D/charge 불변량을 원 R4 열과 결속한다. 원천 모델의 TIQM/SQM은 대안이며 합산하지 않는다.

비교행렬 B는 a,b,c>=0, d는 실수인 2x2 Metzler 행렬이다. g>=0를 붙인 3x3 augmented matrix를 사용해 exp(BH)와 강제항 적분을 동시에 감싼다. 양의 shift 뒤의 행렬·각 급수 항을 위 방향으로 계산하며, 공통 유도노름에 따른 geometric tail을 더한다. 꼬리 경계에는 실제 반올림된 비음수 행렬의 노름을 사용한다. exp(-shift*H)의 위쪽 값은 양의 exponential 다항식 하한의 역수로 얻는다. 코드가 사용하는 모든 방향은 구현 문서에 명시한다.

지수와 강제항 적분을 얻은 뒤 초기 잔차 성분에만 (1-rho)를 뺀다. d<0인 경우 endpoint 값은 블록 전체 supremum이 될 수 없으므로, whole-block 상계는 d를 max(d,0)로 바꾼 협조계로 별도 계산한다. 특정 내부 시각의 query에는 원 B를 사용한다. B=0 및 B^2=0의 singular 경우는 역행렬 없이 처리한다.

## 판별 입력

verification/PRIMARY_INPUT.json에는 5개 affine control과 4개 HD 공유 저장고 control을 고정한다. HD control은 반응 없는 2상태, 비선형 2상태, coarse 형성계수 차이를 명시한 2상태, 그리고 저장된 R6 native9state 생성자 구간의 midpoint를 재사용하는 경우다. 각 HD control은 3블록 및 블록 내 0,1/4,1/2,3/4,1 위치의 인증 상계를 저장한다. 별도 reference는 33/65개 시각에서 실제 fine/coarse ODE를 독립 구현하여 비교한다.

9상태 입력의 rho와 H는 R6 저장 결과에서 재사용한다. 원 생성자 구간은 그대로이며 새 반응 파라미터·branch·밀도·lift는 명시한 수학 fixture다. 실제 물리 consumer를 구성했다고 판정하지 않는다. 새 rational lift의 K*pi 잔차 상계를 primary에서 직접 확인한다.

## 비용과 수용 기준

새 R7 primary/reference는 각각 1회, CPU cap60초다. CAS는 새로운 대수 항등식에 1회, time limit30초를 사용한다. 과거 R6/PHYS91 잔여0은 유지된다. Primary는 exact controls, 보존량, 입력 거부, positivity, interval/Jacobian 방향을 확인한다. Reference는 생산 코어를 import하지 않고 SciPy expm과 별도 nonlinear RHS를 사용한다. 독립 수치 허용오차는 reference input에 고정하며 일반 증명의 지위와 구별한다.

최종 출력은 exact rational/dyadic 값을 저장한다. 과도하게 긴 중간 Fraction을 줄이기 위한 양의 방향 반올림은 tail과 함께 인증되며, 표시용 binary64로 생산 상계를 대체하지 않는다.
