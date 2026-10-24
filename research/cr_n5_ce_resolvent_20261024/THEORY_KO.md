# 에너지 확산 중 첫 H I 여기 사건 — 이론 연결

이 단원은 PR101의 최대 충돌율 상한을 실제 에너지 점유에 의존하는 첫 사건 확률로 구체화한다. Maxwell EE 확산, PHYS83 source-native H1 여기 단면적, C23D의 저장된 초기 가중치를 그대로 연결한다. 표준 Feynman–Kac/absorbing-chain 원리와 PR101 `theory/THEORY_REVIEW.md` §4의 기존 backward survival 유도를 재사용한다. 새로운 기여는 그 식의 채널별 유한-chain 수치 구현, 원 source 가중 평균 및 사건 에너지·시간 모멘트 연결이다.

## 경로 정의와 backward 방정식

q=chi k_B T, U=R k_B T의 유한 에너지 구간에서 q를 흡수 진입점, U를 반사 끝점으로 둔다. 원 PR59 Q는 열(column) population에 작용한다. q 상태를 제외한 A와 G=A^T를 정의하면, a=-G1은 q로 빠지는 진입율이다. 각 상태에서 조건부 Poisson mark h_s(E),h_p(E)를 놓고 h=h_s+h_p라 쓴다. 경로를 처음 mark 또는 q 진입에서 멈춘다.

작은 dt의 first-step 분해는 u_c=h_c dt+(1-h dt)(u_c+G u_c dt)+o(dt)를 준다. 따라서 K u_c=h_c, K=diag(h)-G이다. 흡수 확률은 K u_abs=a를 만족한다. 흡수 가능한 유한 양의 birth-death chain이므로 K의 역은 비음성이며 K1=h+a에서 세 결과의 확률 합이1이다. 이 성질은 유한 chain의 정확한 성질이다. continuum 수렴률이나 원자자료의 물리적 오차를 자동으로 제공하지 않는다.

기대 정지시간은 Kt=1이다. mark 직전 에너지의 비정규화 모멘트는 Kr_c=E h_c이다. Laplace 인자 exp(-s tau)를 붙이면 u_c(s)=(K+sI)^(-1)h_c이고, -∂_s u_c(0)=K^(-1)u_c이다. 따라서 Kv_c=u_c를 풀어 조건부 사건시간을 얻는다. 확률이0인 조건부 평균은 null이다.

한편 w=(-G)^(-1)h는 mark를 경로에 되먹이지 않은 누적 hazard의 기댓값이다. P(mark before entry)=E[1-exp(-integral h dt)]≤E[integral h dt]=w가 된다. 채널별 확률을 직접 풀어 희귀사건에서 1-u_abs의 소거오차를 피한다. PR101의 hmax·MFPT 값은 재계산하지 않고 보존된 비교자료로만 쓴다.

## source projection과 물리적 해석

원 W>q population만 q..U의 두 인접 grid node에 양의 선형 가중치로 보낸다. 이 투영은 수와 초기 운동에너지를 보존한다. q,10eV,Delta를 정확한 grid node로 포함해 원 W<10eV를 처음부터 CE가 가능한 상태로 올려 보내지 않는다. q node에 배정된 작은 질량은 유한 chain에서 즉시 첫 진입으로 해석하며 원 active denominator에서 빼지 않는다. 원 W≤q 전자는 이미 처음 진입한 상태이므로 pre-entry CE 확률0이다. 이 모델링 오차는 grid 비교 대상이다.

0<W<10eV는 초기 source 선택이다. 확산 중 전자는 Delta=10.20435eV 이상으로 올라갈 수 있으므로 CE 확률이0이라고 두지 않는다. h_c=n_1s sigma_c(E) v(E)는 개별 tag의 충돌 hazard다. ne k(T)의 thermal target rate와 바꾸어 쓰지 않는다. H2 분자, screened target, D/T isotope equality, PHYS84 population callback을 이 단원에 추가하지 않는다.

각 CE는 e(E)+H(1s)→e(E-Delta)+H(2l)이고, 전하·핵종·전자수는 그대로이며 Delta의 운동에너지가 원자 내부에너지로 옮겨간다. mark에서 계산을 멈추는 것은 관측량의 종료 조건이다. 실제 전자 소멸, Maxwellization, 영구적인 bath 편입 또는 최종 가열량을 뜻하지 않는다. EI·neutral elastic·CI·RR·DR·CX 및 고차 H excitation을 포함한 전체 first-event 경쟁률은 아직 null이다.

## 표준 결과 재사용과 독립 검산

SciSpace는 Hou–Deng의 reaction/diffusion Feynman–Kac 논문을 찾았고, arXiv1706.01512 원문 서지/초록에서 absorbing/reflecting first-passage scope를 확인했다. 이 문헌은 방법 배경이며 새로운 원자율 자료가 아니다. 첫 SciSpace 결과의 H2/Ar/screened-H 문헌은 종·조건이 달라 provider로 채택하지 않는다.

Wolfram의 두 transient state exact algebra를 독립 witness로 사용했다. 첫 상태의 q 진입율a, 상향율b, 두 번째의 하향율c와 mark율 lambda(x+y)에 대해

u_CE=lambda(x+y)(b,a+b)/(a c+(a+b)lambda(x+y)).

채널합+흡수=1, 직접해와 위 식의 일치, lambda→0 기울기, 단조증가, 오목성의5 checks가 모두 True이다. 전체 응답을 저장했고, PHYS85/86 owner가 예약한 외부 reference 작업은 수행하지 않았다. 수치실행의 독립 C9는 이 toy check와 별도로 원 matrix/source를 검토한다.
