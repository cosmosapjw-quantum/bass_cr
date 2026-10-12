# 유한한 source 나이를 보존하는 가열 근사

`CR-RUX-M1-M3-REUSE-20261012` · 근거 상태: **derived**. 이 유도는 M0의 고정 kernel 계약을 이어받는다. 새로운 원자 모형, 시간전파, 실제 우주론 입력을 도입하지 않는다.

## 1. 정의와 가정

고정된 비음 causal heating kernel의 총 적분을 \(H_0>0\), 열 가중 지연 확률측도를 \(F\)라 둔다. 관측 시각 \(T=10^{10}\,\mathrm{s}\), source 이전 이력 \(q(t)=0\) for \(t<0\), 별도 초기 비열적 입자 stock 0을 유지한다. \(q(0)\)는 실제 초기값이며 0으로 강제하지 않는다. 가열률은

\[
\mathcal P(T)=H_0\int_{[0,T]}q(T-\tau)\,dF(\tau).
\]

\(H_0\)는 기존 단위주입 정규화이고 \(H_0q\)가 가열률 단위를 가진다. 이 연구는 임의 W, eV/s 또는 proper-volume 정규화를 추가하지 않는다. \(c,\hbar,k_B\)를 1로 놓은 것이 아니라 이 스칼라 응답 문제에는 등장하지 않는다. metric은 바뀌지 않는다.

기존 기록에서

\[
p=F([0,T]),\quad R=\int_{[0,T]}(1-\tau/T)\,dF,
\quad S=\int_{[0,T]}(1-\tau/T)^2\,dF
\]

를 재사용한다. 이는 사건 확률이나 전체 주입에너지의 열 분율이 아니라 열 가중 지연 모멘트다. \(p,R,S\)만으로 실제 kernel을 유일하게 복원하지 않는다.

## 2. 유한 나이의 첫 지연 보정

\(q\in C^2([0,T])\), \(M\ge\sup|q''|\)이면 끝점 Taylor 식으로

\[
\mathcal P_1(T)=H_0\{p q(T)-T(p-R)q'(T)\},
\]

\[
|\mathcal P-\mathcal P_1|
\le\frac{H_0MT^2}{2}(p-2R+S).
\tag{1}
\]

이는 기존 M0의 나머지 식을 재사용한다. 비음 \(q\)에서도 도함수 항 때문에 \(\mathcal P_1\)은 음수가 될 수 있다. 비음인 증가식 \(q/q_*=x^n\)에서는 \(\mathcal P_1/(H_0q_*)=p-n(p-R)<0\)가 가능하다. 현재 기록은 이미 \(n=3\)에서 이 부호 결함을 보인다. 실제 cubic 응답은 양수이나 그 정확한 값은 추가 모멘트 \(U_3\) 없이 평가하지 않는다. 이번 오차 비교 표는 기존 정확 응답이 있는 이차 이력만 사용한다.

전 지연 평균 \(\mu=\int\tau dF\)를 위 절단 모멘트 대신 넣으면 같은 식이 아니다. 현재 기록은 \(\mu>T\)이고, source의 zero prehistory 경계를 무시한 \(q(T)-\mu q'(T)\)를 이번 onset의 정확한 첫 보정으로 인정하지 않는다.

## 3. 양수성을 보존하는 조건부 평균 지연

\(p>0\)라 하자. \([0,T]\)에 제한하고 \(p\)로 나눈 측도를 사용하면

\[
\bar\tau_T=T\left(1-\frac Rp\right),\qquad
t_*=T-\bar\tau_T=T\frac Rp,
\]

\[
\mathrm{Var}_{<T}(\tau)=T^2\left(\frac Sp-\frac{R^2}{p^2}\right).
\]

따라서 한 번의 source 평가로 계산하는 근사는

\[
\boxed{\mathcal P_+(T)=H_0p\,q(t_*)}
\tag{2}
\]

이다. \(0\le R\le p\)에서 \(t_*\in[0,T]\)다. source가 비음이면 가열도 비음이며, 상수와 선형 source는 정확하다. 이것은 단일 시각 T의 응답 근사다. 모든 T에 같은 지연을 쓰는 진화 solver 또는 물리적 kernel의 재구성이 아니다.

\(q\)를 \(t_*\)에서 Taylor 전개하면 일차항의 적분은 \(\int_{[0,T]}(T-\tau-t_*)dF=0\)이다. 이차 나머지를 적분하여

\[
\boxed{|\mathcal P-\mathcal P_+|
\le\frac{H_0MT^2}{2}\left(S-\frac{R^2}{p}\right).}
\tag{3}
\]

\(S-R^2/p\ge0\)는 분산 비음성이다. (1)과 (3)의 계수 차이는

\[
\frac12\left[(p-2R+S)-\left(S-\frac{R^2}{p}\right)\right]
=\frac{(p-R)^2}{2p}\ge0.
\tag{4}
\]

그러므로 같은 C2 곡률 정보로 얻는 **절대오차 상계**는 조건부 평균 지연에서 항상 작거나 같다. 이것이 모든 개별 source에서 실제 오차도 더 작다는 뜻은 아니다. \(q\)가 convex이면 Jensen 부등식에 따라 \(\mathcal P\ge\mathcal P_+\), concave이면 부등호가 반대다. 이차식은 (3)의 곡률 상계를 등호로 달성한다. \(q\ge0\)가 필요한 경우 상수항을 충분히 더하면 동일 곡률과 등호를 유지할 수 있다.

차원은 \([M]=[q]/\mathrm{s}^2\), \([MT^2]=[q]\)이고 양변은 가열률이다. 새로운 온도·밀도·기하 가정을 넣지 않았다.

## 4. 근사 차수를 결정하는 오차 예산

명시적인 amplitude \(q_*>0\)와 \(\kappa=T^2 M/q_*\)를 사용한다. 현재 source \(q(T)=0\)인 종료 이력에서도 \(q_*\)를 초기값 또는 최대값으로 정의할 수 있다.

\[
\epsilon_+=\frac{|\mathcal P-\mathcal P_+|}{H_0q_*}
\le C_+\kappa,\quad C_+=\frac12\left(S-\frac{R^2}{p}\right),
\]

\[
\epsilon_1\le C_1\kappa,\quad C_1=\frac12(p-2R+S).
\]

가열률의 허용 절대오차 \(E_{\rm heat}>0\)가 소비자에게 있으면 \(H_0q_*C_+\kappa\le E_{\rm heat}\)가 충분조건이다. \(P_{\rm ref}>0\)에 대한 상대 예산 \(\eta\)라면 \(f_*=H_0q_*/P_{\rm ref}\)를 정의하고 \(f_* C_+\kappa\le\eta\)를 쓴다. **\(f_*\)는 실제 CR 가열분율이 아니라 지정한 reference에 대한 정규화 비율**이다. 결과 파일의 \(f_*\), \(\kappa\), \(\eta\) 격자는 민감도 진단용이고 실제 관측값이 아니다.

이 식이 작아도 source 근사, spectrum/bath 변화, 원자율·격자·원 기록의 forward error를 닫지 않는다. \(\Delta T_g,\Delta x_e,\Delta\tau\)에는 소비자 방정식의 별도 응답·오차전파가 필요하다. 따라서 이번 gate는 `FIXED_KERNEL_HEATING_CLOSURE_SUFFICIENT`일 뿐 EoR/production 승격이 아니다.

**이차 source에는 이미 저장된 M0의 세 모멘트 exact식을 우선 사용한다.** 이번 한 지연 근사는 일반 C2 이력에서 source 평가 한 번으로 충분한지 판단하는 선택지다. 이차 source에 불필요한 근사오차를 도입하도록 요구하지 않는다. 실제 이력을 이차식으로 근사할 수 있고 잔차 상한이 있으면 기존 \(H_0p\|q-q_{\rm quad}\|_\infty\)도 별도 선택지다.

\(p=0\)이면 \(R=S=0\)이고 실제 및 조건부 근사는0이다. \(p>0\)에서 \(R^2=pS\)이면 제한 측도는 한 지연에 집중되어 (2)가 모든 source에 정확하다. 순간 kernel에서는 \(p=R=S=1\), \(t_*=T\)이며 \(\mathcal P_+=H_0q(T)\)로 환원된다. 모든 열이 T 이후면 \(p=0\)이다. \(H_0=0\)은 가열0을 직접 처리해야 하며 확률측도를 정규화하지 않는다; 현재 cache는 \(H_0>0\) 범위다.

## 5. 기본 광흡수와 선택적 CR 지연의 사건 경계

이 절은 RUX03 소비 계약이며 새로운 수치 결과가 아니다. gas proper frame에서 \(N_E(\mathbf n)\)가 단위 proper volume·에너지·solid angle당 광자수이면, 흡수 사건밀도는

\[
\dot N_{{\rm abs},s}=n_s c\int dE\,d\Omega\,\sigma_s(E)N_E(\mathbf n).
\]

같은 사건이 광자 stock 감소와 primary 이온 생성에 한 번씩만 기여한다. 에너지는 종별 binding energy \(\chi_s\)와 photoelectron 주입 \(E-\chi_s\)로 나누며 fitted cross-section cutoff와 \(\chi_s\)를 서로 대체하지 않는다. electron degradation을 명시적으로 켜면 이 excess energy를 즉시 전부 thermal heat에도 더해 두 번 세면 안 된다. 열·secondary ionization·excitation·nonthermal stock·escape 등 선택 모델의 분할이 그 주입을 회계상 소진해야 한다. CR OFF와 baseline primary photoheating OFF는 같은 설정이 아니다.

Verner et al. (1996)의 원 자료는 ground-state photoionization cross section의 출처다: https://www.pa.uky.edu/~verner/photo.html . Furlanetto & Stoever (2010)는 빠른 전자의 에너지가 heating, H/He ionization, excitation으로 분할되고 전자에너지와 이온화 상태에 의존함을 계산한다: https://arxiv.org/abs/0910.4410 . 이 두 출처는 사건 구분의 문헌 근거이고, 여기서 재사용한 CR cache의 시간 kernel 또는 물리 정확도를 독립 인증하지 않는다.

Case A의 explicit recombination photons와 Case B OTS, local HI absorption과 같은 사건을 흡수하는 effective MFP는 중복 owner가 되지 않게 소비자 모델에서 선택한다. 서로 다른 영역·집단을 명시적으로 분해한 항까지 금지하는 전역 XOR로 확대하지 않는다. 이 주장의 실제 구현 상태는 M1/M3 intake 및 별도 owner registry를 따른다.
