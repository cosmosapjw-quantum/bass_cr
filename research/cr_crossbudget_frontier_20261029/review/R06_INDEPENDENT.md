# 독립 이론 검토

Reviewer: 별도 agent `/root/frontier_theory_review`. Primary와 독립적인 정적 유도이며 인간저자 심사로 표현하지 않는다. Source bdc7bf6f4e9cc94d68c32e1752c62de5f809b0bf, 계산 실행0.

HL 총량 m, LL 총량 q로 m+2q<=L 및 m<=M(c). 그러므로 d<= (L+M(c))/2. 유한 LP의 feasible 영점과 유한 용량으로 최적해가 존재한다. 최적 HL의 각 low 잔여 r_l을 diagonal r_l/2에 배정하면 cross 비용0으로 상계를 달성한다. dual atom 가격과 cross multiplier 식이 정확하다. M은 c에 대해 증가·오목·구간별 선형이다.

K4 네 원자의 세 HL edges에서 x+y<=1,x+z<=1,y+z<=c. m<=1+min(y,z)<=1+c/2. x=1-c/2,y=z=c/2는 0<=c<=2에서 feasible하다. 제시한 dual p_H0=p_L0=lambda=1/2도 모든 edge를 지지한다. c>=2는 total mass4에 의해 d<=2이며 달성된다. c1에서 dmax7/4, 기존 outer bound2의 엄격한 차1/4는 맞다.

2E=K는 low, high-high는 strict inequality로 배제된다. 빈 집합/zero mass/no HL에도 정리는 성립한다. w,c,d 단위 m^-3 s^-2, 가격 무차원, W d 단위 m^-3. 화학 bookkeeping은 eV m^-3이며 J 변환이 필요하다.

Findings: no-edge low_diagonal 누락; Atom 타입검사 순서; 직접 테스트 runner의 독립 class 발견 누락. 정리에서 c>=0와 rational-c certificate 조건을 명시하고 과거 CAS/환경 claim을 새 실행 로그와 연결할 것. Full-event LP는 독립 formulation이지만 같은 backend이므로 독립 solver라 표현하지 않을 것.

판정: derived + independent proof review. C<=c 상부 frontier 정리. 새 보편 no-go/문헌 신규성 주장은 채택하지 않는다. API findings는 C5/C6에서 닫는다.
