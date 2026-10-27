# 재사용할 수 있는 한정 결과와 계산 사상

## 고정 모델의 부분적 source 식별

고정 source revision 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b의 같은 kinematic domain 안에서 f0(I,W)=(1+W/I)^−3, f1(I,W)=(W/I)f0(I,W)라 하자. H 기저 gH=(7/3)f0(IH,W)+f1(IH,W), He 기저 gHe0=f0(IHe,W), gHe1=f1(IHe,W)를 사용한다. 각 recovery band의 저장 에너지 모멘트 b_i와 M_ij=∫ Wg_j(W)dW가 주어지면, 비특이 M에 대해 theta=M^−1 b가 이 세 기저 모형 안에서 유일하다. 이 유일성은 원 실행의 저장하지 않은 FP64 계수 바이트 복구를 의미하지 않는다.

실제 계산은 R=diag(1/b_i), c_j=1/max_i|(RM)_ij|, B=RM diag(c), Bz=1, theta=diag(c)z로 한다. 고정 rcond·sensitivity·양의 envelope와 미사용 band 검사를 모두 통과해야 식별 계수를 채택한다. 원 Q8 projector P가 선형이므로 P(AH+AHe)=P(AH)+P(AHe)이고, 새 기저별 attribution을 원 저장 atom에 직접 대조할 수 있다. 원 source atom은 비교의 기준으로 남긴다.

식별 구간은 [0,1000] eV이지만 실제 소비할 birth partition은 [0.1,10] eV뿐이다. 각 cell의 Q8와 barycentric 사상, 3200 active nodes 및 별도 cutoff ghost를 그대로 사용한다. 원 source의 proper factor729·중성 target factor·angle integration은 다시 곱하지 않는다.

## 유한 proper-time 및 부모 사건

같은 gas-rest frame·고정 proper m³에서 q_j(t)=t A_j, 0≤t≤T=10^10 s가 실제 공급돼 있다. 유한 구간 [a,b]의 새 탄생 적분은 J_j(a,b)=((b−a)(b+a)/2) A_j이다. 여기서 N은 m^−3, E는 eV m^−3이며 전체 worldtube의 절대 입자수와 에너지는 별도 proper volume 없이 정의하지 않는다.

선택 He 전자 수 NHe와 s+p+2d=NHe, s,p,d≥0가 주어지면 source 종 변화는 (−NHe+d, NHe−p−2d, p+d)다. 이는 선택 marginal과 양립하는 필요 조건을 나타낸다. p는 선택 support 밖 partner 전자 수이므로 전체 전하 생성은 NHe+p이고, 실제 partner의 운동·열·radiation 응답은 별도 입력이다. 따라서 여기서 구성한 family는 실제 exclusive branching을 대신하지 않는다.

원 저장 RR capture CH,CHe를 서로 다른 target 사건으로 합성하면 ΔHII=JH−CH, ΔHeII=NHe−p−2d−CHe, ΔHeIII=p+d가 된다. 같은 100 K·조건부 H1/He4 inventory와 explicit nb=8750/47 m^−3에서 각 density 변화와 p,d 계수를 nb로 한 번 나눈다. baseline, delta, 희귀 capture 항을 각각 저장하여 baseline의 ulp보다 작은 증분을 잃지 않는다.

## 에너지와 retained photon

L0=Uinj+IHsrc JH+I1src NHe는 canonical kinetic source와 모델로 식별한 electron-equivalent binding functional이다. recipient 결합에너지 변화는 IH*(JH−CH)+I1*(NHe−CHe)+I2*p+(I2−I1)*d다. source/RR/native 상수의 차이는 별도 literal sidecar이며, 실제 I2src·partner energy·residual excitation·proton depletion은 아직 null이다. p,d의 branch chemical lift나 literal residual을 heat 또는 w_ext로 옮기지 않는다.

원 discrete retained photon의 count 및 energy atom은 별도 port에 그대로 연결한다. 이 포트는 photon moments로 spectrum/history를 역생성하지 않으며 deposition과 physical heating을 선언하지 않는다.

## 명시적 caloric fixture

p=d=0, monatomic translational EOS, frozen response를 명시한 fixture에서 cv=3kB/2라 하자. bin 시작의 Ua=Uth0+Qprefix(a), Da=npart0+Nthermal,prefix(a)에 대해 δ_ab=(qDa−Ua n)/(Ua(Da+n)), ΔlogT=log1p(δ_ab)다. retention은 q=QC eVJ,n=0이고, assimilation은 q=(QC+Ucut)eVJ,n=Ncut이다. 이전 prefix의 작은 baseline 증분을 두 부분 또는 고정밀도로 보존한다. 이 계산은 재결합 hazard를 다시 계산하거나 실제 coupled thermal history를 닫지 않는다.

정의·원전 비교·유도는 [THEORY_KO.md](THEORY_KO.md), 실제 심사는 [R6](review/R6_INDEPENDENT.json), 22개 대수 검산은 [R7](symbolic/RESULT_V1.json)에 있다. 숫자 구현의 입력·출력·정밀도·허용치는 [COMPUTATIONAL_CONTRACT.json](COMPUTATIONAL_CONTRACT.json)과 그에 결속된 원 spec에 고정했다. 수치 실행·PASS는 이 문서 작성 시점에 미수행이다.

현재 범위: 한 단위만 종료. 중앙 **28/88**, 집계 효과 0. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4false, global completion/error/budget/currency null.
