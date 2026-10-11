# CR-PHYS02G: 열 방출 지연의 모멘트 경계와 frontier 분해

## 1. 범위와 증거 상태

이 문서는 CR-PHYS02G-MOMENT-ENVELOPES-AND-FRONTIER-STRATIFICATION의 후보 유도다. 정확한 확률측도와 정확한 첫 두 모멘트에 대한 부등식을 증명하고, 기존 E/F 스칼라와 앞으로 반환될 F adjoint 배열에 적용하는 방법을 고정한다. 이론 담당 Astra의 후보 기여이며 독립 승인 문서가 아니다.

선행 수치 출처는 실제 E pulse 반환 PR35와 그 입력을 사용한 F 스칼라 유도 PR36이다. 이 문서와 exact toy는 실제 9600-cell 계산, F 실행 또는 F 반환의 존재를 증명하지 않는다. 현재 F 실제 반환은 조회한 GitHub와 백업에서 관측되지 않았고, NCP 로컬 실행·예약·예산 소비 상태는 별도 확인 대상이다.

| 고정 계약 | SHA-256 |
|---|---|
| state/SCIENTIFIC_CONTRACT.json | 517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832 |
| state/VALIDATION_CONTRACT.json | 259d6964154cc190050761db092c9edd5499649867f822003db8afdfa42d9aba |
| ncp/NCP_EXECUTION_CONTRACT.json | 06a06f865bba44ce93cc3bcf905cf95440de0978e87ee76529d2f440c6065856 |

모멘트 문제에서 sharp라는 말은 주어진 제약 아래의 infimum/supremum을 뜻하며, 그 값의 달성은 별개다. 다항식으로 사건 지시함수를 지배하는 방식은 일반적인 모멘트 문제의 쌍대 표현이다.[1, Definition 2; §2] 아래의 조각별 식 전체, 엄격한 사건의 끝점 처리, 유한 지지 구성 및 CR 적용은 이 루프에서 직접 유도한다.

## 2. 첫 두 모멘트에 대한 생존 확률 경계

비음수 확률변수 \(X\)에 대하여

\[
a=\mathbb E X>0,\qquad b=\mathbb E X^2,\qquad v=b-a^2>0
\]

라 하자. 사건은 반드시 \(X>x\)이며 \(X\ge x\)가 아니다. 모든 \(x\ge0\)에서

\[
L(x;a,b)\le \Pr(X>x)\le U(x;a,b),
\]

\[
L(x;a,b)=
\begin{cases}
\dfrac{(a-x)^2}{v+(a-x)^2},&0\le x<a,\\[3pt]
0,&x\ge a,
\end{cases}
\]

\[
U(x;a,b)=
\begin{cases}
1,&0\le x\le a,\\[3pt]
\dfrac a x,&a<x<b/a,\\[3pt]
\dfrac{v}{v+(x-a)^2},&x\ge b/a.
\end{cases}
\]

이 각각은 정확한 \((a,b)\)를 갖는 **모든 비음수 확률분포** 위에서 sharp하다. 특정한 phase-type 분포, 하나의 고정 생성자, 서로 연결된 모든 frontier 상태, 양의 지지만을 갖는 조건부 측도, 또는 모든 시간의 경계가 한꺼번에 달성된다는 주장은 포함하지 않는다.

### 2.1 다항식 증명

\(0\le x<a\)에서 \(d=a-x\), \(c=a+v/d\)라 두자. 모든 실수 \(z\)에 대해

\[
1-\left(\frac{z-c}{c-x}\right)^2\le\mathbf1_{\{z>x\}}.
\]

\(z\le x\)이면 왼쪽이 0 이하이고, \(z>x\)이면 1 이하이기 때문이다. 기대값을 취하면

\[
\Pr(X>x)\ge 1-\frac{v+(a-c)^2}{(c-x)^2}
=\frac{d^2}{v+d^2}.
\]

\(x\ge a\)의 하한 0은 자명하다.

상한에는 세 majorant를 사용한다. 상수 1은 모든 문턱에서 유효하다. \(x>0\)일 때 비음수 지지에서 \(z/x\ge\mathbf1_{\{z>x\}}\)이므로 Markov 상한 \(a/x\)를 얻는다. \(x>a\)에서 \(d=x-a\), \(c=a-v/d\)라 두면

\[
\left(\frac{z-c}{x-c}\right)^2\ge\mathbf1_{\{z>x\}},
\qquad
\mathbb E\left(\frac{X-c}{x-c}\right)^2
=\frac{v}{v+d^2}.
\]

Markov 상한이 마지막 상한보다 작거나 같은 조건은

\[
\frac a x\le\frac v{v+(x-a)^2}
\iff x-a\le\frac va
\iff x\le\frac ba.
\]

따라서 세 상한의 작은 값을 취하면 위의 \(U\)가 된다. 두 비자명한 상한은 \(x=b/a\)에서 \(a^2/b\)로 연속적으로 만난다.

### 2.2 sharpness와 달성 여부

아래 구성은 단위가 일관된 임의의 정확한 \(a>0,v>0\)에 적용된다.

| 문턱 | 하한 | 상한 |
|---|---|---|
| \(0\le x<a\) | 달성됨 | 1이 달성됨 |
| \(a\le x<b/a\) | infimum 0, 달성되지 않음 | supremum, 달성되지 않음 |
| \(x\ge b/a\) | 0이 달성됨 | supremum, 달성되지 않음 |

**낮은 문턱의 하한.** \(d=a-x\)라 두고, \(x\)에 질량 \(v/(v+d^2)\), \(a+v/d\)에 질량 \(d^2/(v+d^2)\)를 둔다. 평균과 분산이 \(a,v\)이고, 문턱에 놓인 원자는 엄격한 사건에서 제외되므로 생존 확률이 정확히 \(L\)이다.

**낮은 문턱의 상한.** \(\ell=(a+x)/2>x\), \(u=a+v/(a-\ell)\)를 선택한다. \(\ell,u\)에 각각 \(v/[v+(a-\ell)^2]\), \((a-\ell)^2/[v+(a-\ell)^2]\)를 두면 두 점 모두 문턱 위에 있으므로 생존 확률은 1이다.

**\(a\le x<b/a\)의 상한.** \(x<y<b/a<z\)에 대하여 지지 \(\{0,y,z\}\)와

\[
p_y=\frac{az-b}{y(z-y)},\quad
p_z=\frac{b-ay}{z(z-y)},\quad
p_0=1-p_y-p_z
=\frac{(y-a)(z-a)+v}{yz}
\]

를 사용한다. 질량은 비음수이며 평균은 \(a\), 이차 모멘트는 \(b\)다. 양의 지지점들이 문턱 위에 있으므로

\[
\Pr(X>x)=p_y+p_z
=\frac a y-\frac{b-ay}{yz}\longrightarrow\frac a x.
\]

예컨대 \(y_n=x+(b/a-x)/(n+1)\), \(z_n=b/a+na\)로 접근할 수 있다. \(x=a\)에서 극한은 1이다. \(x>a\)에서는 엄격한 사건으로 Markov 등호를 달성할 수 없고, \(x=a\)에서 생존 확률 1은 평균 \(a\)와 양립하지 않는다.

**\(x\ge b/a\)의 상한.** \(u>x\), \(\ell=a-v/(u-a)\ge0\)에 대한 두 점 분포를 사용한다. \(u\)의 질량은 \(v/[v+(u-a)^2]\)이며, \(u\downarrow x\)에서 상한에 접근한다. 엄격한 사건 때문에 정확한 등호는 달성되지 않는다.

**중간 구간의 하한 0.** \(\varepsilon_n=a/(n+1)\), \(\ell_n=a-\varepsilon_n\), \(u_n=a+v/\varepsilon_n\)인 두 점 분포에서 높은 점의 질량은 \(\varepsilon_n^2/(v+\varepsilon_n^2)\to0\)이다. \(a\le x<b/a\)에서 하한 0은 달성될 수 없다. \(X\le x\)가 거의 확실하면 \(b\le xa\)여야 하는데 이 구간에서는 반대 부등식이 성립하기 때문이다.

**높은 구간의 하한 0.** \(\{0,b/a\}\)에 각각 \(1-a^2/b,a^2/b\)를 놓으면 \(x\ge b/a\)에서 생존 확률이 정확히 0이다.

### 2.3 퇴화와 부적합 입력

\(v=0\)이면 \(X=a\)가 거의 확실하므로 생존 확률은 \(\mathbf1_{\{x<a\}}\)다. 특히 \(x=a\)에서 0이다. \(a=b=0\)은 \(\delta_0\)로 정의된다. 비음수 변수에서 \(a=0,b>0\)은 불가능하며, \(b<a^2\), 음의 모멘트, 비유한 입력 역시 부적합이다.

물리적 조건부 잔여시간은 \(X>0\)이므로 양의 질량을 갖는 잔여시간 측도의 평균이 정확히 0일 수 없다. 일반 비음수 모멘트 도구의 \(\delta_0\) 처리를 물리 어댑터에 무조건 적용해서는 안 된다. 반올림 오차로 관측된 음수를 0으로 자르거나 임의의 작은 바닥값을 넣는 것도 허용하지 않는다.

## 3. E/F 스칼라에서 잔여시간 모멘트를 추출하는 항등식

열 방출의 정규화된 측도를

\[
dF(\tau)=\frac{K(\tau)\,d\tau}{H_0},\qquad
H_0=\int_0^\infty K(\tau)\,d\tau>0
\]

로 둔다. 이는 열량으로 가중한 방출 지연의 확률이다. 입자 수 생존율이나 단순한 활성 상태 점유율과 같지 않다.

기존 입력 \(T>0\), \(p=F(T)\), \(q=1-p\), \(\mu=\mathbb E\tau\), \(m_2=\mathbb E\tau^2\) 및

\[
R=\mathbb E(1-\tau/T)_+,\qquad
S=\mathbb E(1-\tau/T)_+^2
\]

를 사용하면

\[
\mathbb E(\tau-T)_+=\mu-T(1-R),
\]

\[
\mathbb E(\tau-T)_+^2=m_2-2T\mu+T^2(1-S).
\]

첫째 식은 \(\tau=\min(\tau,T)+(\tau-T)_+\), 둘째 식은 \((\tau-T)^2=(\tau-T)_+^2+(T-\tau)_+^2\)에서 따른다. 따라서 \(q>0\)일 때 \(X=(\tau-T)\mid\tau>T\)의 두 모멘트는

\[
a_T=\frac{\mu-T(1-R)}q,\qquad
b_T=\frac{m_2-2T\mu+T^2(1-S)}q.
\]

\(t>T\)에서 \(r=t-T\)에 대해

\[
qL(r;a_T,b_T)\le\Pr(\tau>t)\le qU(r;a_T,b_T).
\]

그러나 **\(t=T\)에서는 양쪽 값이 정확히 \(q\)**다. 조건부 변수는 \(X>0\)이므로 \(\Pr(X>0)=1\)이며, 일반 비음수 클래스의 \(L(0)=a_T^2/b_T\)로 알려진 값을 대체하면 안 된다. \(q=0\)일 때 잔여시간 조건부 모멘트는 UNDEFINED_ZERO_TAIL, \(t\ge T\)의 생존 확률은 0이다. 이 대수 항등식은 문턱 \(T\)에 원자가 있는 경우에도 성립한다.

## 4. 출생 성분의 구분과 교집합

출생 성분 \(j\)의 eventual heat가 \(H_{0j}\)이면 \(w_j=H_{0j}/\sum_jH_{0j}\)다. 따라서

\[
\Pr(\tau>t)=\sum_j w_j\Pr(\tau_j>t),
\]

\[
L_{\rm birth}(t)=\sum_jw_jq_jL(t-T;a_{Tj},b_{Tj}),\quad
U_{\rm birth}(t)=\sum_jw_jq_jU(t-T;a_{Tj},b_{Tj})
\]

가 유효하다. \(w_jq_j\)는 정규화하지 않은 전체 열의 꼬리 질량이다. 정규화된 꼬리 성분 가중치는 \(w_jq_j/q\)이며 두 종류를 혼동해서는 안 된다.

선택된 전체 분포의 무조건부 경계, pooled residual 경계, birth residual 경계를 별도로 보존하고

\[
L_*(t)=\max(L_{\rm total},L_{\rm pooled},L_{\rm birth}),\qquad
U_*(t)=\min(U_{\rm total},U_{\rm pooled},U_{\rm birth})
\]

를 취하면 교집합이다. \(t=T\)는 정확한 \(q\)를 사용한다. 성분 합과 선택된 스칼라의 수치 차이는 별도로 기록한다.

정확한 입력에서 성분의 질량과 첫 두 모멘트가 pooled 값과 일치하면, birth 경계는 pooled residual 경계보다 약해질 수 없다. 각 성분의 임의의 허용 분포를 섞은 분포는 pooled 두 모멘트 제약도 만족한다. 유한 개 성분에 대해 각 성분의 infimum/supremum을 동시에 임의로 가깝게 접근할 수 있으므로, 성분별 경계의 합은 더 작은 허용 집합에서의 극값이다. 이는 정확한 수학적 포함 관계이며, FP64 차이를 자르거나 부호를 바꾸는 근거가 아니다.

## 5. 양의 semigroup에서의 frontier 분해

\(A=-G_{\rm active}\)를 무차원 시간 \(u=t/T_0\)의 안정한 활성 블록, \(h\ge0\)를 heat 행의 전치 벡터라 하자. \(\exp(-Au)\ge0\), \(\Re\lambda(A)>0\), 비음수 초기 벡터 \(b_j\)를 가정한다. 전체 ledger의 모든 행을 무차원 확률 생성자로 해석하는 주장은 필요하지 않다.

상태 \(i\)에서 시작한 단위 활성 질량의 물리 시간 heat kernel은

\[
k_i(r)=\frac1{T_0}h^T\exp(-Ar/T_0)e_i,\qquad r\ge0
\]

다. 안정성과 양성에 의해 다음 적분은 유한하며 비음수다.

\[
q_0=A^{-T}h,\quad q_1=A^{-T}q_0,\quad q_2=A^{-T}q_1,
\]

\[
\int k_i(r)\,dr=q_{0i},\quad
\int r k_i(r)\,dr=T_0q_{1i},\quad
\int r^2 k_i(r)\,dr=2T_0^2q_{2i}.
\]

이는 \(\int_0^\infty r^k\exp(-Ar/T_0)\,dr/T_0=k!T_0^kA^{-(k+1)}\)로 직접 확인된다. \(q_{0i}>0\)일 때 heat 조건부 상태 잔여시간의 모멘트는

\[
a_i=T_0\frac{q_{1i}}{q_{0i}},\qquad
b_i=2T_0^2\frac{q_{2i}}{q_{0i}}.
\]

\(x_{Tj}=\exp(-AT/T_0)b_j\)라 두면 semigroup 성질로

\[
K_j(T+r)=\sum_i x_{T,ij}k_i(r).
\]

따라서 상태 조건부 생존 함수 \(S_i(r)\)에 대해

\[
\Pr(\tau_j>T+r)=\sum_i\alpha_{ij}S_i(r),\qquad
\alpha_{ij}=\frac{q_{0i}x_{T,ij}}{H_{0j}},\qquad
\sum_i\alpha_{ij}=q_j.
\]

선택된 전체 소스는

\[
\alpha_i=\frac{q_{0i}\sum_jx_{T,ij}}{\sum_jH_{0j}}
\]

를 사용한다. Frontier 경계는 \(\sum_i\alpha_iL/U(r;a_i,b_i)\)다. \(r=0\)은 정확한 전체 꼬리 질량이다. 유한한 rate kernel에는 0시각의 Dirac 원자가 없기 때문이다.

Frontier 가중치는 **현재 상태에 남아 있는 미래 열량** \(q_{0i}x_{T,ij}\)에 비례한다. F residence 분해의 \(q_{0i}w_{ij}\)나 bare population \(x_{T,ij}\)와 다른 양이다.

### 5.1 영 상태와 수치 적합성

\(q_{0i}=0\)이면 비음수 함수 \(k_i\)의 적분이 0이므로 \(k_i=0\)가 거의 모든 곳에서 성립하고 \(q_{1i}=q_{2i}=0\)이어야 한다. 이 상태는 heat weight가 0이며 조건부 나눗셈 없이 typed skip한다. \(q_0=0\)인데 고차 모멘트가 0이 아닌 입력은 모순이다.

입력, 가중치 및 상태 분산 \(b_i-a_i^2\)는 확률 표현과 양립해야 한다. 음수나 비유한 입력은 원래 값과 부호를 보존한 채 FRONTIER_MOMENT_NOT_PROBABILITY_COMPATIBLE로 처리한다. 기존 F의 작은 음수 허용 잔차가 새 확률 표현의 양성 증명이 되지는 않는다. 작은 \(q_0\)를 임의로 바닥값으로 대체하거나, 음의 분산을 0으로 자르거나, 모르는 오차 구간을 만들어 넓히지 않는다.

### 5.2 경계의 포함 관계와 한계

정확한 질량·모멘트 항등식 아래에서는

\[
L_{\rm frontier}\ge L_{\rm birth}\ge L_{\rm pooled},\qquad
U_{\rm frontier}\le U_{\rm birth}\le U_{\rm pooled}.
\]

증명은 4절과 같다. 상태별 제약은 각 출생 성분의 pooled 모멘트를 함의하고, 출생 성분의 제약은 전체 pooled 모멘트를 함의한다. 무조건부 전체 모멘트 경계와의 교집합도 유효하다.

상태들의 kernel은 실제로 동일한 \(G\)를 공유한다. 여기서는 공유 관계를 최적화 제약으로 완전히 이용하지 않으므로, frontier 합이나 최종 교집합이 물리 cascade 위에서 sharp하다고 주장하지 않는다. F의 저장된 \(q_0,q_1,q_2,x_T,b,E\) 배열이 있으면 새 \(G\), 선형 solve, pulse, expm 없이 계산할 수 있다. 실제 배열 검증과 새로운 독립 검토가 완료되기 전에는 PREPARED_NOT_EXECUTED다.

## 6. 누적 방출 분율과 시간 구간

\(0<f<1\)에 대해 generalized quantile을

\[
Q_f=\inf\{t\ge0:F(t)\ge f\},\qquad c=1-f
\]

로 정의한다. 생존 경계 \(L_*(t)\le1-F(t)\le U_*(t)\)에 대해

\[
t_{\rm lo}=\sup\big(\{t:L_*(t)>c\}\cup\{0\}\big),\qquad
t_{\rm hi}=\inf\{t:U_*(t)\le c\}
\]

이면 \(t_{\rm lo}\le Q_f\le t_{\rm hi}\)다. 저장할 하단 유한 근사점은 엄격한 \(L_*(t)>c\), 상단은 \(U_*(t)\le c\)를 유지해야 한다. \(L_*(t)=c\)만으로 하한을 주장하면 CDF의 plateau에서 잘못될 수 있다. \(f>p\)이면 알려진 \(F(T)=p\)에서 \(Q_f>T\)를 얻으므로 하단이 \(T\) 아래로 사라지지 않는다.

일반 단일 모멘트 경계의 해석적 역은

\[
q_{\rm lo}(f)=\max\left(0,a-\sqrt{\frac{v(1-f)}f}\right),
\]

\[
q_{\rm hi}(f)=
\begin{cases}
\dfrac a{1-f},&1-f\ge a^2/b,\\[3pt]
a+\sqrt{\dfrac{vf}{1-f}},&1-f<a^2/b.
\end{cases}
\]

퇴화 분포에서는 두 값이 \(a\)다. 잔여시간 단일 경계에는 \(c\mapsto c/q\)와 시간 \(T\)의 이동을 적용한다. 성분 합과 교집합의 역은 단조 경계의 양 끝을 유지하는 유한 bisection으로 평가할 수 있다. 이 값들은 모멘트 제약에 조건부인 구간 또는 충분한 horizon이며, 실제 CDF의 보간·외삽·최적 적합 지연시간이 아니다.

\(v>0\)이면 모든 유한 문턱에서 \(U>0\)다. 첫 두 모멘트로 \(f<1\)의 충분한 horizon은 얻을 수 있지만, 정확히 100% 열 방출을 보장하는 유한 시간은 얻을 수 없다. 하한이 0이라는 것도 실제 tail이 소멸했다는 뜻이 아니다.

## 7. 검산의 의미

exact_fraction_oracle.py는 한 분포당 8개 이하의 원자와 정확한 Fraction 연산으로 문턱 원자, 분산 0, sharpness 구성, 잔여시간 항등식, 출생 성분 및 frontier 모멘트 혼합 항등식을 확인한다. Frontier toy의 q 배열은 유한 지지 조건부 측도로부터 구성한 대수 fixture다. 실제 생성자에 대한 embeddability나 실제 F 배열을 증명하는 witness가 아니다. 전체 다항식 부등식과 semigroup 정당화는 본문의 해석적 증명에서 제공한다.

실행 기록은 EXACT_FRACTION_ORACLE.json, 원래 stdout/stderr 및 EXACT_FRACTION_ORACLE_RECEIPT.json에 남긴다. 실제 E/F 스칼라의 일회 계산과 Decimal80 비교는 다른 담당자의 별도 증거다. 정확한 Fraction 결과도 부동소수점 물리 입력의 forward error, 단면적 오차, 격자 오차 또는 장시간 bath 가정의 타당성에 대한 보증이 아니다.

## 참고 자료

1. D. Bertsimas and I. Popescu, *Optimal Inequalities in Probability Theory: A Convex Optimization Approach*, INSEAD working paper 2002/01/TM. [저자 기관 원문 PDF](https://flora.insead.edu/fichiersti_wp/inseadwp2002/2002-01.pdf). Definition 2(인쇄 2쪽): sharp bound와 supremum/달성의 구별. §2(인쇄 6–7쪽): 지시함수 다항식 majorant의 쌍대 표현. §3.2/Table 2(인쇄 15–16쪽): Markov 및 한쪽 이차 모멘트 경계. 출판판 DOI: [10.1137/S1052623401399903](https://doi.org/10.1137/S1052623401399903). 실제로 열람한 2002 작업 논문의 해당 절을 맥락 자료로 사용한다.
