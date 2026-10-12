# 온도·조성 피드백 분과 독립 심사

연구 단위: CR-THEORY-FEEDBACK-20261013. 검토자: /root/feedback_literature_review.
판정: **FP1–FP7 ACCEPTED_CONDITIONAL_DERIVATION**. 수학적 차단 지적: **0개**.
실제 Wolfram/xAct 실행과 기하학 분과는 최종 통합 판정에 연결한다.

## 1. 검토 범위와 독립 방법

FEEDBACK_THEOREMS_KO.md 전체, FEEDBACK_ASSUMPTIONS.json 및 FEEDBACK_ERROR_MAP.json을 읽었다.
후보 생성·검산 설계와 분리된 검토로, 불변집합의 유계성, 소모율 적분에 의한 domain 유지,
분수 차의 직접 분해, contraction residual의 역삼각부등식, 선형 경로 재구성의 미분 잔차,
정확한 한 사건 예제의 대입과 도함수를 확인했다.
이번 심사에서 과학 계산을 새 실행한 횟수는 0이며 작성자·root 실행 근거는 원출력으로 별도 확인한다.

## 2. 존재와 정의역

원자핵 수가 원자·이온 성분을 제한하고, 양의 active bin energy 및 U·R의 비음성이
active count와 에너지 성분을 제한한다. 전하 보존에서 N_e+Σ_jA_j가 ionic charge와 Q_0로
결정되므로 N_e도 유계다. 따라서 제시한 닫힌 선형 불변집합 K_0는 compact convex이며,
추가 자유 reservoir에는 별도 유한 상계가 필요하다는 조건이 문서에 있다.

열적 수 상한 N_max=N_nuc+N_H+2N_He−Q_0와 하한 N_min=N_nuc는
동일한 전하·핵수 장부에서 따라온다. 온도 부등식은 affine N에 대한 선형 부등식이므로
K의 convexity가 유지된다. 초기 U_n>0에서 h*C_U≤U_n 조건은 갱신 U≥U_n/2를 주고,
N≤N_max 및 U≤E_total을 함께 사용하면 T_floor와 T_ceiling이 유지된다.
연속 self-map의 존재 정리 적용 조건이 모두 채워져 있다.

T=0에서 특이한 rate는 양의 온도 domain에 한정되며, T=0을 포함하는 경우에는
연속 확장을 가정한다. 밀도 log의 경우에도 양의 밀도·양의 logarithm 구간 및 실제로 사용한
미분 상계를 coefficient domain으로 유지한다. 현재 정리는 그 선언한 domain에 대한 결과다.

## 3. 유일성, 잔차, 계수 오차

상태의 서로 다른 물리 단위는 고정 양의 척도 a_i를 가진 infinity norm으로 처리한다.
온도 차를 U_z/(c_vN_z)−U_w/(c_vN_w)로 직접 통분하면 FP.19의 L_T가 나온다.
Fraction과 density의 상계도 양의 고정 원자핵 수·부피 조건에서 맞다.

Extent 차에는 두 효과가 있다. numerator의 차이는 h*L_r/m_r,
분모의 차이는 h²*F_r*D_r/m_r² 이하이다. S의 각 출력 행에 절댓값을 적용하면
FP.24의 q가 전체 map의 Lipschitz 상수다. q<1이면 K의 완비성 및 self-map으로
유일성과 임의의 feasible 초기 iterate에서의 Picard 수렴이 성립한다.
FP.27은 h*A+h²*B=q_target의 양의 근을 cancellation이 적은 형태로 쓴 식이다.

Fixed-point residual bound는 거리≤q*거리+residual에서 직접 얻어진다.
새 iterate에는 q를 한 번 더 곱하는 사후 오차 계수도 맞다.
동일 support·초기 state·S의 두 rate family를 비교한 FP.30은 같은 분수 차 상계이며,
FP.31의 세 오차는 map perturbation, 실제 측정 residual, 평가 오차로 대응한다.
EOS의 직접 차 공식은 FP.29 및 FP.42의 온도 계수를 준다.

## 4. 실제 ODE와의 연결

질량작용 polynomial의 상태 도함수와 V의 시간 도함수는 제시한 차원과 지수를 갖는다.
실제 경로는 quasipositivity, 같은 불변량 및 물리적 소비율 상계로 K에 남는다.
첫 이탈 시각 전에 U≥U_n−s*C_U_physical를 적분하는 논증에서,
h*C_U_physical≤U_n/2가 해당 시간 구간의 온도 floor를 보장한다.

Frozen donor와 capacity step의 consistency는 초기 propensity 일치 조건을 사용한다.
ξ≤hF에서 endpoint 이동 O(h)를 얻고, coefficient 변화 및 capacity denominator를
각각 O(h²)로 제한한다. 실제 Euler remainder의 Lipschitz 적분과 합쳐 FP.36–FP.37이 나온다.
초기에 없는 donor를 사용하는 반응은 물리적 rate의 vanishing·Lipschitz 조건 아래에서
그 step의 추가 extent가 O(h²)이므로 support 고정과 일차 local consistency가 양립한다.
경계에 가까운 초기 상태 전체에 대한 균일 상계에는 추가 cancellation 또는 양의 하한이
필요하다는 정확한 조건도 유지되어 있다.

## 5. Physical endpoint defect의 적분

선형 경로 η(s)=y_n+s(z−y_n)/h는 convex K에 남는다.
미분 잔차에 endpoint vector field를 더하고 빼면
D_end+(h−s)[L_G*||z−y_n||/h+L_G,t]라는 상계가 나온다.
Gronwall 적분에서 가중치 exp[L_G(h−s)]와 (h−s)를 각각 적분하면

$$
A=(e^{Lh}-1)/L,
\qquad
B=((Lh-1)e^{Lh}+1)/L^2
$$

이고 L→0에서 h와 h²/2다. 이 결과는 FP.40–FP.41과 일치한다.
B의 작은 인수 전개 1/2+x/3+x²/8+x³/30도 적분의 Taylor 전개와 같다.
해당 endpoint defect는 실제 G를 사용하므로 iteration 미완료와 시간 이산화의 차이를
같은 재구성 잔차에 포함한다. 별도의 approximate G 평가가 남으면 그 오차를 더한다는
계약이 기계 기록에 명시돼 있다.

## 6. 정확한 비선형 예제

FP7의 y_n=(1,1,1,0,1), s=(−1,−1,1,2,3)은 원자핵 수 2,
전하 0, 에너지 6E_0를 보존한다. θ=(1+3x)/(2+2x)와 χ_H=(1+x)/2를
계수에 넣으면 F=(3+5x)/2다. ψ'_η=(5η/2)/(1+2ηF)^2의 최대는
x=0에서 얻고, η에 대한 전체 최대는 η=1/3의 5/24다.
따라서 선언한 scalar 구간에서 모든 유한 η≥0의 수렴 증명이 닫힌다.
η=4/17의 x*=1/4, θ*=7/10, q=170/841은 직접 대입으로 일치한다.
실제 donor를 사용한 ODE rate는 κ_0F(x)(1−x)^2이므로
해당 endpoint의 extent defect는 −17κ_0/128이다.
이 사례의 discrete endpoint, 실제 physical defect, 원소·전하·에너지가 서로 일관된다.

## 7. 최소 문서 교정

FP-R1 — CLOSED: §1의 사건 명세 참조가 실제 파일
EVENT_STEP_DERIVATION_KO.md로 교정된 것을 확인했다. 문서 경로의 교정이며 수식은 유지된다.
함께 정리된 Coulomb 계수 예시의 0<n_lo≤n≤n_hi<C² 조건은 본문·가정·오차 사상에
동일하게 반영되어 밀도와 logarithm의 양의 정의역을 명시한다.

| 검토 파일 | bytes | SHA-256 |
|---|---:|---|
| derivations/FEEDBACK_THEOREMS_KO.md | 25402 | 0cbf68003f3ddfd1c5b0db75999d43592a5857a6749a96f4a16ef5558521f8f6 |
| derivations/FEEDBACK_ASSUMPTIONS.json | 10799 | 4e28ceef7c2132621d7ea68cca49620e1bb5fdcead21eb0cb64980e70861f423 |
| derivations/FEEDBACK_ERROR_MAP.json | 4408 | 834ad9671b57a4fcd4fd857e0842a4cb5631e3a70ace50a670da5e0c785d5486 |

