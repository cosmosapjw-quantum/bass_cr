# 독립 R6: H1/He4 neutral elastic 유한온도 에너지 교환

판정: **PASS_SCOPED_THEORY_AND_FROZEN_CONTRACT**, blocking finding0. 검토시각2026-10-24 21:37:49 UTC. 생산 구현과 과학 실행에 참여하지 않았고 수치 C9는 아직 수행하지 않았다.

## 독립 유도

전자질량m, 중성질량M, 상대속도g=v-u, 질량중심속도V=(mv+Mu)/(m+M), 감소질량mu_red=mM/(m+M)로 둔다. 탄성충돌에서 |g'|=|g|이므로 deltaE=mu_red V·(g'-g). MTCS 정의로 각도를 적분하면 a_E=-n mu_red <g sigma_m(g) V·g>이다.

beta=m/(m+M), s²=k_BTn/M라 두면 V=beta g+u. Gaussian Stein identity는 <u·g f(g)>=-s²<3f+gf'>를 주므로 a_E=n mu_red[s²<3f+gf'>-beta<g²f>]. f=g sigma_m(E), E=mg²/2에서 gf'=f[1+2E sigma'/sigma]. 고정v의 leading expansion을 취하고 J를eV로 바꾸면 mu=2(m/M)nu_m[theta(2+E sigma'/sigma)-E]이다. 이는 F0 convention을 p=sqrt(E)F0로 바꿔 얻은 D=2(m/M)theta E nu_m와 mu=D'+D(1/(2E)-1/theta)에 일치한다.

Maxwell p∝sqrt(E)exp(-E/theta)는 J=-D[p'-(1/(2E)-1/theta)p]=0을 만족한다. 같은온도·정지bath에서는기존pi를유지한conductance합성이가능하다.

## 유효범위와 생략항

정지표적의 정확한 event energy change는 -[2mM/(m+M)²]E(1-cosχ)다. Leading drift의coldlimit는이식의O(m/M)항이다. Second angularmoment sigma2=∫(1-cosχ)²dσ는0<=sigma2<=2sigma_m를만족하여 D_recoil/D_thermal≈E/(rtheta) sigma2/sigma_m<=2E/(rtheta)를준다. 따라서 theta/(rE)와2E/(rtheta)를별도진단량으로보고해야한다. 계약은이구분을이미포함하며두값을전역물리오차상계로채택하지않는다.

연속piecewise-linear sigma는양의연속D와구간별mu를준다. flux식에서D'항이상쇄되므로각knot에서fluxmatching을갖는weak문제가명확하다. derivative의우측구간선택은진단규약이며주연산자는D로직접구성한다. 표적속도전개의계수정칙성·급격한단면적변화는별도모형의존성이다.

## 이산 보존과진단

각edge의c/pi 양방향rate는columnsum0와detailedbalance를동시에준다. Column-forwardQ에대한backward는Q^T이므로Knew=Kold-Qneutral,active^T가맞다. a_b=-Q_b^T E를동일K로적분하면K E=h_CE E+Σa_b+q a_entry에서전체stoppedenergy장부가닫힌다. CEincomingenergy를outgoingkinetic+internalgap으로나누어열을중복계산하지않는다.

No-CE흡수first-entry의T_i=Σ_{k<i}(Σ_{j>k}pi_j)/c_k는각항이양수다. c_old<=c_new<=(1+delta)c_old이므로Told/(1+delta)<=Tnew<=Told. 이는동일pi/q/U의no-CE문제에한정된다.

14physicalRHS=6확률/시간/incomingenergy+2conditionaltime+6bathrewards. 후속C9는시간t/v_s/v_p까지포함해야하며이번R6가그수치검증을대신하지않는다.

## 종료

수학적blocking지적은없다. 고정된경량controls→8case/112RHS→동일계약의독립C9로진행할수있다. Globalphysicalerror는null, fullN4/N5는PARTIAL/OPEN, N6/N7은gated다. 구체15checks와identity는THEORY_R6.json에기록했다.
