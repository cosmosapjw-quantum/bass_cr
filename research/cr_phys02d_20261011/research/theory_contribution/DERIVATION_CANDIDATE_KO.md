# CR-PHYS02D 후보 유도 — 저장된 종단 가열량으로 얻는 유한구간 지연 정보

상태: **DERIVED; 해석적 toy 및 정확한 유한측도 반례 NUMERICALLY CHECKED.** 이 문서는 이론 기여자의 후보 유도이며 독립 최종 판정이 아니다. 기존 연구의 수송, 원자 계수, 원천과 bath를 변경하거나 재실행하지 않는다. 수치 입출력 계약과 판정 허용값의 최종 소유자는 root다.

## 1. 정의, 차원, 전제

선택한 전자 출생 스펙트럼과 기체 상태를 고정하고, 활성 전자의 **운동에너지 밀도** 벡터를 \(x(t)\in\mathbb R^n\), 고정된 에너지 분율 원천 벡터를 \(a\ge0\)라 둔다. \(x\)의 단위는 \(\mathrm{J\,m^{-3}}\), \(a\)는 무차원이다. 직접 cutoff에 주입되는 에너지는 활성 상태 밖의 별도 장부로 가므로 \(\boldsymbol1^Ta=1\)을 강제하지 않는다. 원천의 시간 진폭 \(q(t)\)는 \(\mathrm{J\,m^{-3}\,s^{-1}}\)이며,

\[
\dot x=Lx+a q(t),\qquad x(0)=0,\qquad P_H(t)=h^Tx(t),
\]

에서 \(L\)과 \(h\)의 단위는 각각 \(\mathrm{s^{-1}}\)다. \(L\)은 비대각 원소가 음이 아닌 Metzler 행렬이고 안정적(Hurwitz)이며, \(h\ge0\)는 Coulomb 열률 행이다. 현재 코드에서 원천의 heat 장부 성분은 0이므로 직접적인 \(d q(t)\) feedthrough는 없다. 그런 항을 나중에 추가하면 \(d\delta(\tau)\)를 열 커널에 명시적으로 포함해야 한다.

양의 semigroup와 Duhamel 식으로

\[
x(T)=\int_0^T e^{L\tau}a q(T-\tau)\,d\tau,
\quad
P_H(T)=\int_0^T K(\tau)q(T-\tau)\,d\tau,
\quad K(\tau)=h^Te^{L\tau}a\ge0.
\]

\(K\)는 단위 주입 에너지당 열 방출 응답이고 단위는 \(\mathrm{s^{-1}}\)다. 이온화로 전자 수는 늘어날 수 있으므로 이를 전자 한 개의 생존확률 또는 수명 분포로 부르지 않는다. 특정 출생 성분이 최종적으로 방출하는 **열에 가중한 에너지 지연**이다. 공간 수송·팽창·bath 변화·광자 재흡수는 이 식의 범위에 포함되지 않는다.

\(M=-L\)로 쓰면 \(M^{-1}\ge0\)인 nonsingular M-matrix이고,

\[
H_0=\int_0^\infty K(\tau)\,d\tau=h^TM^{-1}a>0,
\qquad \kappa(\tau)=K(\tau)/H_0
\]

는 각각 무차원 terminal heat yield와 정규화된 지연밀도다. 이 무한구간은 **같은 연산자를 무한히 유지한 수학적 기준**이다. 현재 원천·bath의 실제 물리적 유효기간이 \([0,T]\)인 경우 그 밖의 실제 우주론 이력을 증명하지 않는다. 이하의 유한구간 관측식은 \(K\)의 \([0,T]\) 부분과 이 조건부 기준 \(H_0\)를 사용한다.

부모 코드의 전체 \(G\)는 heat·binding·excitation·cutoff 등 누적 장부 때문에 0 고유값을 포함한다. 역행렬은 반드시 \(G_{\rm active}=G[:n,:n]\)에만 취한다. 에너지 오름차순에서 이 활성 블록은 위삼각이고, 양의 Coulomb 누출과 양의 흡수 장부가 안정성을 뒷받침한다. 이는 새 수치 검사가 아니라 읽은 구현의 구조이며, 새 결과를 사용할 때 해당 연산자 identity와 기존 실제 검증을 연결해야 한다.

## 2. 선형 ramp 원천에서 저장량 세 개가 주는 두 모멘트

기존과 동일한 \(q(t)=\alpha t\), \(0\le t\le T\), \(\alpha>0\)를 둔다. \(\alpha\)의 단위는 \(\mathrm{J\,m^{-3}\,s^{-2}}\)다. 누적 Coulomb 열을 \(Q_H(T)=\int_0^T P_H(t)dt\)라 정의하면 적분 순서 교환으로

\[
P_H(T)=\alpha\int_0^T(T-\tau)K(\tau)d\tau,
\qquad
Q_H(T)=\frac\alpha2\int_0^T(T-\tau)^2K(\tau)d\tau.
\]

따라서 즉시 terminal-yield 열률 비교값 \(P_{\rm inst}(T)=\alpha T H_0\)를 이용해

\[
\boxed{R=\frac{P_H(T)}{P_{\rm inst}(T)}},\qquad
\boxed{S=\frac{2Q_H(T)}{T P_{\rm inst}(T)}}
\]

를 **저장된 SI 스칼라만으로** 계산한다. \(Q_H\)의 단위는 \(\mathrm{J\,m^{-3}}\), 두 \(P\)는 \(\mathrm{J\,m^{-3}\,s^{-1}}\), \(T\)는 s이며 \(R,S\)는 무차원이다. \(S\)는 누적 열을 \(\frac12\alpha T^2H_0\)와 비교한 비율이다. 주입된 전체 선택 에너지에 대한 실제 열 분율과는 \(H_0\)만큼 다르다.

\(\tau\sim\kappa\), \(X=(1-\tau/T)_+\in[0,1]\)로 두면

\[
\boxed{R=\mathbb E[X],\qquad S=\mathbb E[X^2].}
\]

그러므로 이 모델이 만족해야 하는 필요조건은

\[
\boxed{0\le R\le1,\qquad R^2\le S\le R.}
\]

첫 부등식은 지지집합, \(S\ge R^2\)는 분산의 비음성, \(S\le R\)는 \(X^2\le X\)에서 따른다. \(\{R,S\}\)의 호환성만으로 원자 단면적·연산자·원천 구현 전체가 검증되는 것은 아니다. 이것은 고정된 선형 causal response와 저장량 사이의 새 의미론적 필요조건이다.

## 3. 관측시간에서 상한 고정한 지연의 평균과 분산

\[
D=\min(\tau,T)=T(1-X)
\]

라 두면

\[
\boxed{\mathbb E[D]=T(1-R)},
\quad
\boxed{\mathbb E[D^2]=T^2(1-2R+S)},
\quad
\boxed{\operatorname{Var}(D)=T^2(S-R^2)}.
\]

이들은 전체 지연밀도에서 \(\tau\ge T\)인 사건을 모두 \(T\)에 배정한 **capped moments**다. \(\tau<T\)인 열만 골라 재정규화한 조건부 평균과 다르다. \(R\ll1\)일 때 평균 \(D\)가 \(T\)에 가깝다는 사실은 많은 지연 가중치가 아직 유한구간에서 분리되지 않았음을 뜻하며, 실제 평균 지연이 \(T\) 정도라는 결론은 아니다.

순간 및 누적 즉시 침적 근사의 상대 부족분은 각각

\[
e_P=1-R=\mathbb E[D]/T,\qquad e_Q=1-S,
\]

이며 모멘트 호환성으로

\[
e_P\le e_Q\le2e_P-e_P^2
\]

가 성립한다. 상대오차의 분모는 즉시 침적 비교값이다. 실제 \(P_H\)를 분모로 삼으면 \(e_P/(1-e_P)\)가 된다.

## 4. 지금 열을 내는 원천의 나이와 구분

\(T\)에서 실제 열률에 기여하는 주입의 나이는 ramp 가중을 포함한

\[
\rho_T(\tau)=\frac{(T-\tau)K(\tau)}{P_H(T)/\alpha},\qquad 0\le\tau<T
\]

로 분포한다. 따라서

\[
\boxed{\bar\tau_{\rm heat,now}=T\left(1-\frac SR\right)
       =T-\frac{2Q_H(T)}{P_H(T)}}\quad (R>0).
\]

이 양은 **현재 발생하는 열의 원천 주입 나이**다. capped lag 평균 \(T(1-R)\), 모든 최종 열의 평균 지연 \(\mathbb E[\tau]\), 입자 수명과 각각 다르다. \(0\le\bar\tau_{\rm heat,now}\le T\)이고, 실제 현재 열의 출생 성분을 분리해 같은 식을 적용할 수 있다. 현재 직접 열 feedthrough가 없다는 전제도 유지한다.

두 출생 표지를 합칠 때 \(R,S\)는 \(H_{0,i}\), 곧 \(P_{{\rm inst},i}(T)\)에 따른 혼합이다:

\[
R_{\rm tot}=\frac{\sum_i P_{{\rm inst},i}R_i}{\sum_iP_{{\rm inst},i}},
\quad
S_{\rm tot}=\frac{\sum_i P_{{\rm inst},i}S_i}{\sum_iP_{{\rm inst},i}}.
\]

단순 평균이나 초기 주입 에너지 가중 평균으로 대체하지 않는다.

## 5. 유한구간 누적 heat-kernel 질량에 대한 직접 경계

\(F_{<}(T)=\Pr(\tau<T)=\Pr(X>0)\)라 쓰자. 현재의 유한 행렬 커널은 연속밀도이므로 경계 원자의 확률이 없고 \(<\)와 \(\le\)는 같다. 일반 측도 반례에서는 이를 구분한다. Cauchy–Schwarz를 적용하면

\[
R^2=\mathbb E[X\mathbf1_{X>0}]^2
\le\mathbb E[X^2]\Pr(X>0)=S F_{<}(T),
\]

즉

\[
\boxed{F_{<}(T)\ge R^2/S}\quad(S>0).
\]

이 경계는 두 모멘트만 아는 일반 비음 측도에서 sharp하다. \(X=S/R\)에 질량 \(R^2/S\), \(X=0\)에 나머지를 놓으면 등호다. \(F_{<}(T)\)는 일정한 에너지를 한 번 주입했을 때 최종 열 가중치 중 지연 \(T\) 안에 방출된 부분이다. ramp의 실제 누적 열/주입 에너지 비율로 해석하지 않는다.

더 짧은 \(uT\), \(0<u<1\)에서 \(c=1-u\), \(I(x)=\mathbf1_{x\ge c}\)로 두자. \([0,1]\)에서

\[
q_L(x)=\frac{x(x-c)}{1-c}\le I(x)
\le q_U(x)=\frac{x(1+c-x)}{c}
\]

이다. 왼쪽은 \(x<c\)에서 \(q_L\le0\)이고, \(x\ge c\)에서는 \(0\le q_L\le1\)이다. 오른쪽은 \(x<c\)에서 \(q_U\ge0\)이며 \(x\ge c\)에서는
\(q_U-1=(x-c)(1-x)/c\ge0\)이다. 적분하면

\[
\boxed{
\max\!\left(0,\frac{S-cR}{1-c}\right)
\le F(uT)\le
\min\!\left(1,\frac{(1+c)R-S}{c}\right)
}.
\]

특히 \(u=1/2\)에서는 \(\max(0,2S-R)\le F(T/2)\le\min(1,3R-2S)\)다. 이는 직접 증명한 quadratic dual 경계이며 전역 최적 경계라고 주장하지 않는다. \(u=1/4,1/2,3/4\)를 같은 공식으로 평가할 수 있다. 이론 부등식은 exact model에서 엄밀하지만, 수치 \(R,S\)를 대입한 출력값 자체가 discretization 오차를 인증한 구간은 아니다.

## 6. 두 모멘트가 정하지 못하는 양과 정확한 반례

엄격한 내부 영역 \(0<R<1,\ R^2<S<R\)를 생각하자. 위 sharp 경계를 실현하는 측도를 지연으로 쓰면

\[
p\,\delta_{T(1-S/R)}+(1-p)\,\delta_B,
\qquad p=R^2/S,\quad B\ge T
\]

다. \(B\)를 아무리 크게 바꾸어도 \(R,S\), 모든 capped moments와 현재 열의 원천 나이는 같다. 그러나

\[
\mathbb E[\tau]=T(1-R)+(1-p)(B-T)
\]

는 위로 제한되지 않는다. \(q>p\)인 충분히 높은 분위수도 \(B\)와 함께 임의로 커진다. 모든 분위수가 무제한이라는 뜻은 아니다. \(q\le p\)인 분위수는 \(F(T)\ge p\) 때문에 \(T\) 안에 존재한다.

반대로 같은 \(R,S\)를 갖고 모든 질량이 \(\tau<T\)에 있는 측도도 있다. \(X\)를

\[
a_*=(R-S)/(1-R),\quad 1,
\]

에 놓고 \(X=1\)의 질량을

\[
w_*=(S-R^2)/(1-2R+S)
\]

로 두면 두 모멘트가 정확히 일치하고 \(F(T)=1\), \(\mathbb E[\tau]=T(1-R)\)이다. 따라서 두 endpoint scalars만 주어졌을 때 가능한 평균 지연은 일반적으로

\[
\boxed{\mathbb E[\tau]\in[T(1-R),\infty)}
\]

이며 유일하지 않다. 이 정확한 허용구간은 일반 비음 지연측도에 대한 것이다. 유한 Hurwitz 행렬이 만드는 매끄러운 지수 커널에는 무한한 시간 꼬리가 있어 아래 경계의 달성 여부가 추가로 제한된다. 1-Lipschitz 변환과 독립 복사본을 쓴 분산 항등식 \(2\operatorname{Var}(Y)=\mathbb E[(Y-Y')^2]\)으로, 분산이 유한하면 \(\operatorname{Var}(\tau)\ge\operatorname{Var}(D)\)도 성립하지만 상계는 없다. 예외는 \(S=R^2\)의 결정론적 지연 등 퇴화 경계다. \(R=S=0\)이면 모든 질량이 \(\tau\ge T\)에 있고 실제 평균은 여전히 미결정이다.

이 불식별성은 **저장된 두 endpoint moments만으로 추론할 때**의 명제다. 정확한 \(L,a,h\) 전체를 알고 있으면 커널과 모멘트는 그 모델 안에서 정해진다. 원자 측도는 일반 positivity 정보만으로 무엇을 추론할 수 없는지 보여 주며, 현재의 매끄러운 커널 자체를 델타함수로 대체하자는 제안이 아니다.

매끄러운 양의 안정 시스템에서도 반례가 존재한다. 두 병렬 감쇠 모드를 쓰면

\[
\kappa(\tau)=w\lambda_f e^{-\lambda_f\tau}
 +(1-w)\lambda_s e^{-\lambda_s\tau},\quad 0<w<1,\ \lambda_f,\lambda_s>0.
\]

목표 \(R=1/8,S=1/10\)을 고정한 채 \(\lambda_sT=10^{-2},10^{-5},10^{-8}\) 각각에서 \(w,\lambda_fT\)를 90자리 계산으로 구했다. 두 모멘트는 \(10^{-60}\)보다 작은 절대잔차로 같지만 평균 지연 \(w/\lambda_f+(1-w)/\lambda_s\)은 다르며 첫째와 셋째의 비가 \(10^5\)보다 크다. 양의 지수혼합이므로 이는 finite, positive, stable 응답의 실제 수치 반례다. 해당 모형을 bass_cr 물리 데이터에 맞춘 것은 아니다.

## 7. 무한구간 모멘트가 있을 때의 즉시 침적 판별식

현재 endpoint-only 작업에서는 새 resolvent solve를 수행하지 않는다. 다음 별도 계산에서 얻을 수 있는 식은

\[
H_n=\int_0^\infty\tau^nK(\tau)d\tau=n!h^TM^{-(n+1)}a,
\quad \mu=H_1/H_0,\quad m_2=H_2/H_0.
\]

부분적분 \(\int_0^\infty\tau^ne^{-M\tau}d\tau=n!M^{-(n+1)}\)과 안정성으로 유도된다. 각각 \(H_n\)의 단위는 \(\mathrm{s^n}\)이고 \(\mu\)는 s다. ramp의 즉시 침적 오차는

\[
e_P(T)=\mathbb E[\min(\tau/T,1)]\le\min(1,\mu/T).
\]

따라서 즉시 비교값을 분모로 한 허용오차 \(\epsilon\)에 대해 \(T\ge\mu/\epsilon\)은 충분조건이다. 실제 열률을 분모로 요구하면 \(T\ge(1+\epsilon)\mu/\epsilon\)이 충분하다. 이는 같은 ramp와 고정 연산자 아래의 수학적 충분조건이고 일반적인 시간변화 원천·팽창하는 bath로 자동 이식할 수 없다. 현재 endpoint 두 값만으로 \(\mu\)의 유한 상계를 얻지 못하므로 이 조건을 검증할 수 없다.

## 8. 다음 NCP pulse 작업의 해석과 계산 형태

새 impulsive source에서는 \(x_{\rm pulse}(0)=a\), 이후 원천은 0이며 같은 활성 \(L\)로 전파한다. \(x_{\rm pulse}\)는 단위 주입에 대한 상태이고 \(\dot Q_{H,\rm pulse}=h^Tx_{\rm pulse}\)다. heat 장부는 0에서 시작한다. 전체 상태의 초기조건에는 원래 `source_vectors`의 직접 cutoff 장부와 내부 카운터 성분을 그대로 포함해야 에너지·수 장부가 보존된다. 이를 모두 0으로 버리거나 열로 바꾸지 않는다. 같은 저장 에너지 격자에서 두 원자 모형을 비교하는 pulse 두 번이 새로운 커널 정보를 주며, 이미 계산한 ramp를 재실행할 이유는 없다.

커널 적분 \(F(uT)=Q_{H,\rm pulse}(uT)/H_0\)는 pulse 누적 heat 장부를 직접 읽는 것이 좋다. 거의 같은 terminal yield 둘을 빼 \(1-F\)를 만드는 방식은 early-time \(F\ll1\)에서 소거오차가 커진다. \(K(uT)=h^Tx_{\rm pulse}(uT)\)는 양의 곱합이다. pulse로부터 \(R,S\)를 다시 얻을 필요가 있다면 양의 가중 \((1-u),(1-u)^2\)로 적분하거나 추가 누적 블록을 사용한다. 실제 pulse의 시간 적분 오차를 계량하지 않은 점별 표본으로 이를 인증했다고 하면 안 된다.

\(M^{-1}\)를 명시적으로 만들지 않는다. \(v_1=M^{-1}a\), \(v_2=M^{-1}v_1\), \(v_3=M^{-1}v_2\)를 순차 선형 solve로 구하면 \(H_0=h^Tv_1,H_1=h^Tv_2,H_2=2h^Tv_3\)다. 출생 스펙트럼이 많고 heat 행이 적으면 \(M^Tw_1=h\)부터 푸는 adjoint 방식이 유리할 수 있다. 실제 연산자의 삼각성, diagonal scaling, solve 잔차·양성 및 차원변환을 명시해야 한다. 이 비용·선택은 다음 실행 계약의 범위다.

기존 코드의 \(u=t/T_0\), \(G_A=T_0L\), \(g_H=T_0h\)를 쓰면

\[
H_n=n!T_0^n g_H^T(-G_A)^{-(n+1)}a.
\]

\(T_0\) 인자를 빠뜨리면 특히 평균과 분산의 단위가 틀린다. 현재 저장된 SI 관측량으로 계산하는 \(R,S\) 식에는 이런 내부 변환이 필요 없다.

기존 ramp 상태로부터 \(\int_0^T e^{-M\tau}a\,d\tau=Ta-Mx(T)/\alpha\)를 대수적으로 복원할 수는 있다. 그러나 빠른 모드에서는 큰 두 항의 차이로 작은 값을 얻으므로 새 pulse의 대체 인증으로 쓰지 않는다. \(P,Q_H\)로 직접 계산 가능한 capped moments와 현재 열의 원천 나이에 집중하는 것이 현재 단위의 수치적으로 명료한 경로다.

## 9. 정확한 pole oracle와 수치 경계

한 감쇠율 \(\lambda\)에서 \(\kappa=\lambda e^{-\lambda\tau}\), \(z=\lambda T\)이면

\[
R_1(z)=1-\frac{1-e^{-z}}z,\qquad
S_1(z)=1-\frac2z+\frac{2(1-e^{-z})}{z^2}.
\]

작은 \(z\)에서는 \(R_1=z/2-z^2/6+\cdots\), \(S_1=z/3-z^2/12+\cdots\)이므로 직접 뺄셈식보다 급수 또는 안정한 phi 함수가 필요하다. 큰 \(z\)에서는 \(R_1\to1,S_1\to1\), 지연은 즉시 근사에 접근한다.

두 직렬 단계 \(\lambda_1\ne\lambda_2\)이면

\[
\kappa_2(\tau)=\frac{\lambda_1\lambda_2}{\lambda_2-\lambda_1}
(e^{-\lambda_1\tau}-e^{-\lambda_2\tau}),
\]

\[
R_2=\frac{\lambda_2R_1(\lambda_1T)-\lambda_1R_1(\lambda_2T)}{\lambda_2-\lambda_1},
\quad S_2=\frac{\lambda_2S_1(\lambda_1T)-\lambda_1S_1(\lambda_2T)}{\lambda_2-\lambda_1}.
\]

평균은 \(1/\lambda_1+1/\lambda_2\), 두 번째 raw moment는 \(2(\lambda_1^{-2}+(\lambda_1\lambda_2)^{-1}+\lambda_2^{-2})\)다. 같은 감쇠율의 극한에서 \(\kappa_2=\lambda^2\tau e^{-\lambda\tau}\)이고

\[
R_2(z)=1-2/z+e^{-z}(1+2/z),
\quad S_2(z)=1-4/z+6/z^2-e^{-z}(2/z+6/z^2).
\]

이 경우 작은 \(z\)에서 \(R_2\sim z^2/6,S_2\sim z^2/12\)다. 서로 가까운 감쇠율에는 signed difference를 그대로 평가하지 않고 이 연속 극한 또는 divided-difference 전개를 사용해야 한다.

`endpoint_oracles.py`는 stdlib Fraction으로 원자 측도의 동일 모멘트를 정확히 검사하고 Decimal 90자리로 위 닫힌 식을 독립적인 적분 급수와 비교했다. 같은 감쇠율 극한, 양의 지수혼합 반례, CDF 경계도 확인했다. 실제 과학 연산자 생성과 수송은 각각 0회다. 실제 실행 결과는 `ORACLE_RESULT.json`이다.

## 10. 사전 수치 수용 조건 제안과 해석 제한

- 입력 \(T,P_H,P_{\rm inst},Q_H\)의 source/model/tag/grid identity, 단위와 provenance를 먼저 고정한다. 같은 이름의 다른 terminal closure나 다른 격자 결과를 섞지 않는다.
- \(T>0,P_{\rm inst}>0\), 유한값, \(P_H,Q_H\ge0\)를 검사하고 raw \(R,S,R-S,S-R^2\)를 보존한다. 음수 값을 숨기기 위한 clipping은 하지 않는다. roundoff 허용값은 root 계약에서 사전에 정한다.
- \(T(1-R)\), \(T(1-S/R)\), \(T^2(S-R^2)\)는 각각 \(R\simeq1\), \(S\simeq R\), \(S\simeq R^2\)에서 소거에 민감하다. conditioning 지표 \((1+R)/|1-R|\), \((R+S)/|R-S|\), \((S+R^2)/|S-R^2|\)를 함께 보고하거나 단위 시간으로 나눈 무차원량을 먼저 유지한다.
- 기존 4800·9600 격자 사이 새 진단의 변화는 유용한 empirical mesh check다. 이 차이를 rigorous enclosure 또는 물리적 오차막대로 바꾸지 않는다. 새 fourth grid는 이 유도에 필요하지 않다.
- source/bath가 시간에 따라 달라지거나 원천 스펙트럼이 변하면 고정 커널 convolution 자체가 바뀐다. 음의 source, 음의 kernel, 0이 아닌 초기 전자 상태에서도 위 단순 endpoint 식을 그대로 적용하지 않는다.
- 이번 결과는 `PHYS02_DELAY`의 정의와 판별력을 개선하지만, 전체 우주론적 지연 이력·원자 완전성·production history를 닫지 않는다. 해당 claim gate의 승격은 독립 최종 검토의 권한이다.

## 읽은 기준과 근거 상태

직접 읽은 기준은 Astra 연구 하네스 `PROJECT_INSTRUCTIONS.md`, PHYS02C `REPORT_KO.md`·`DERIVATION_KO.md`, PHYS02B `src/causal_cascade.py`의 source/generator/augmentation/terminal-yield/summarize 부분이다. 본 문서의 모멘트 정리와 경계는 위에 보인 직접 유도이며 새로운 문헌 검색 결과에 기대지 않는다. pole 예제는 해석식의 검산으로 한정한다. 아직 입수되지 않은 실제 9600 결과를 가정해 숫자를 생성하지 않았다.
