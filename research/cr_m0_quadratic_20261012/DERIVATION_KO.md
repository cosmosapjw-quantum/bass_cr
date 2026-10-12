# 고정 열화 kernel의 이차 주입 이력: 직접 유도 메모

2026-10-12 · M0 설계 보조 · 근거 상태 `derived`

이 문서는 새 후보의 설계 보조 유도이며 독립 승인 판정이 아니다. 실제 수치의 평가는 주 실행자의 별도 단일 후처리 결과를 따른다. 여기서는 과학 실행·새 kernel 구성·G·solve·NCP·옛 suite 실행을 하지 않았다.

## 1. 정의와 범위

기준은 기존 `PLAN_AND_RESULTS_KO.md`의 고정 bath·고정 주입 스펙트럼·선형 causal 응답이다. 모델을 \(m\in\{f,l\}\)로 쓰고 \(H_m>0\), \(F_m\)을 지연 \(\tau\ge0\) 위의 확률측도로 둔다. 밀도가 존재하면 \(dF_m=K_m(\tau)d\tau/H_m\)이고, 측도 표현은 지연의 원자도 허용한다.

\(T=10^{10}\,\mathrm{s}>0\), \(x=t/T\), 주입 전 이력 \(q(t)=0\) for \(t<0\), 주입 이외의 초기 particle perturbation 0을 유지한다. \(q\)는 \([0,T]\)의 양 끝을 포함해 정의한다. 특히 \(F_m(\{T\})\ne0\)이면 \(q(0)\)의 실제 값이 끝점 가열률에 들어가므로 초기점 값을 임의로 바꾸지 않는다.

\[
p_m=F_m([0,T]),\qquad R_m=\int(1-\tau/T)_+\,dF_m,
\qquad S_m=\int(1-\tau/T)_+^2\,dF_m.
\]

\(z=1-\tau/T\)를 \([0,T]\)에서 사용하면, 주입 이력 \(q(t)=q_* f(t/T)\)의 끝점 가열은

\[
\mathcal P_m(T)=H_mq_*\int_{[0,T]}f(z)\,dF_m.
\]

여기서 \(q_*>0\)는 명시적인 이력 amplitude다. 아래 비감소 클래스에서는 \(q_*=q(T)\), 종료 이력에서는 초기값 또는 peak amplitude다. 이 두 정규화를 섞지 않는다. \(p,R,S,f\)는 무차원이고, \(H_mq_*\)가 원 기록의 가열률 단위를 갖는다. 임의의 W나 eV/s를 추가하지 않는다.

모든 이차식 \(f(x)=\alpha+\beta x+\gamma x^2\)에 대해

\[
\boxed{\mathcal P_m(T)/(H_mq_*)=\alpha p_m+\beta R_m+\gamma S_m}
\]

는 선형성의 정확한 결과다. \(\tau=T\)에서는 상수항만 남고, \(\tau=0\)에서는 \(f(1)\)이 들어간다.

## 2. 정규화된 비음·비감소 이차식의 정확한 클래스

\[
f(x)=a(1-x)^2+2b x(1-x)+x^2,\qquad0\le x\le1.
\]

모든 차수 2 이하 실수 다항식 중 \(f(1)=1\)인 것은 유일하게 이 형식으로 표현된다. \(a=f(0)\), \(b=a+f'(0)/2\)다. 도함수는

\[
f'(x)=2[(b-a)(1-x)+(1-b)x].
\]

도함수가 일차식이므로 \([0,1]\)에서 비음일 필요충분조건은 \(b-a\ge0\), \(1-b\ge0\)다. 비감소 함수가 비음일 필요충분조건은 그 최소값인 \(a\ge0\)다. 따라서

\[
\boxed{f\ge0,\quad f'\ge0,\quad f(1)=1
\iff0\le a\le b\le1.}
\]

조건은 충분조건에 그치지 않고 이차식에서는 필요충분이다. 차수가 더 높으면 Bernstein control point의 순서가 동일하게 필요조건이라고 일반화하지 않는다.

세 꼭짓점 이력과 그 가중치는

\[
v_1(x)=1,\quad v_2(x)=2x-x^2,\quad v_3(x)=x^2,
\]
\[
\boxed{f=a v_1+(b-a)v_2+(1-b)v_3.}
\]

가중치는 비음이고 합이 1이다. 각 꼭짓점은 각각 \((a,b)=(1,1),(0,1),(0,0)\)이며 정확한 끝점 계수는

\[
C_{m,1}=p_m,\qquad C_{m,2}=2R_m-S_m,\qquad C_{m,3}=S_m.
\]

\(0\le z\le1\)에서 \(z^2\le2z-z^2\le1\)이므로

\[
0\le S_m\le 2R_m-S_m\le p_m\le1,
\qquad S_m\le \mathcal P_m(T)/(H_mq_*)\le p_m.
\]

즉 이 클래스의 순간 가열 예측 \(H_mq_*\)에 대한 결손은 \([1-p_m,1-S_m]\)에 든다. 이 정규화된 결손과 실제 가열률로 나눈 상대오차는 다르다.

### 두 모델의 비율 범위와 equality

\(h_{m,i}=H_mC_{m,i}\)로 놓자. \(h_{l,i}>0\)가 모든 꼭짓점에서 성립하면

\[
\frac{\mathcal P_f}{\mathcal P_l}
=\frac{\sum_i w_i h_{f,i}}{\sum_i w_i h_{l,i}}
=\sum_i\frac{w_i h_{l,i}}{\sum_jw_jh_{l,j}}
\frac{h_{f,i}}{h_{l,i}}.
\]

따라서 같은 \((a,b),q_*,T\)를 사용하는 두 모델의 비율은 세 꼭짓점 비율의 최소와 최대 사이에 있고, 양 끝은 실제 꼭짓점 이력으로 달성된다. 최소/최대 equality의 필요충분조건은 양의 source weight를 가진 모든 꼭짓점의 비율이 그 최소/최대와 같은 것이다. 극값 꼭짓점이 유일하면 해당 꼭짓점 이력이 유일한 equality source다. 여러 비율이 같으면 그 꼭짓점들의 convex hull도 equality다.

일반 kernel에서는 \(S_l>0\)면 위 분모 양성 조건이 충분하다. 어떤 \(h_{l,i}=0\)이면 해당 꼭짓점 비율을 만들 수 없으므로 같은 정리를 그대로 쓰지 않는다. \(q_*=q(T)=0\)까지 허용하면 비음·비감소 이력은 항등적 0이고 가열도 0이지만 정규화와 모델 비율은 \(0/0\)으로 정의되지 않는다.

## 3. 모든 비음 이차식으로의 확장

이 절에서는 비감소 또는 \(q(T)>0\) 조건을 요구하지 않는다. \(f\not\equiv0\), \(f(x)\ge0\) for \(x\in[0,1]\)인 모든 차수 2 이하 실수 다항식을 대상으로 한다. 특히 \(q(T)=0\)인 종료 source가 포함된다.

\[
f(x)=a(1-x)^2+2b x(1-x)+c x^2.
\]

끝점에서 \(a,c\ge0\)가 필요하다. 내부에서 \(u=x/(1-x)>0\)로 쓰면

\[
\frac{f(x)}{x(1-x)}=a/u+2b+cu.
\]

\(a,c>0\)이면 우변의 모든 \(u>0\)에 대한 inf는 \(2\sqrt{ac}+2b\)다. \(a=0\) 또는 \(c=0\)일 때도 나머지 항의 inf가 0이므로 같은 비음 조건을 얻는다. 따라서

\[
\boxed{f\ge0\text{ on }[0,1]\iff a,c\ge0,\quad b\ge-\sqrt{ac}.}
\]

다음 분해는 정확하다.

\[
\boxed{f(x)=[\sqrt a(1-x)-\sqrt c\,x]^2
+2(b+\sqrt{ac})x(1-x).}
\]

따라서 비음 이차식의 cone은 squared-linear source와 \(x(1-x)\) source로 생성된다. 모든 squared-linear source는 그 자체로 비음이므로, 생성 집합을 내부근의 square에만 제한하지 않아도 전체 cone과 같다.

\[
A_m=H_m\begin{pmatrix}p_m&R_m\\R_m&S_m\end{pmatrix},
\qquad B_m=H_m(R_m-S_m).
\]

\(\ell(x)=u+vx\)이면 끝점 가열 계수는 \((u,v)A_m(u,v)^\mathsf T\)다. \(x(1-x)\)의 계수는 \(B_m\)다. 양의 측도의 정의로 \(A_m\succeq0\), \(B_m\ge0\)이며,

\[
A_m\succ0\iff p_m>0\ \text{and}\ p_mS_m-R_m^2>0.
\]

이는 \([0,T]\) 안에서 \(z\)가 한 점에만 집중되지 않는 조건이다. \(B_m>0\)는 \(F_m((0,T))>0\)와 동치다.

이제 \(A_l\succ0\), \(B_l>0\)를 가정하자. \(A_f\)는 양의 준정부호만으로도 아래 정리가 성립한다. \(\lambda_-\le\lambda_+\)를 \((A_f,A_l)\)의 generalized eigenvalues라 하면 모든 nonzero squared-linear source에서

\[
\lambda_-\le\frac{w^\mathsf TA_fw}{w^\mathsf TA_lw}\le\lambda_+.
\]

이는 \(z=A_l^{1/2}w\)로 바꾸어 실대칭 \(A_l^{-1/2}A_fA_l^{-1/2}\)의 Rayleigh quotient로 표현하면 바로 증명된다. 각 경계는 대응하는 실수 eigenvector의 제곱 이력으로 달성된다.

일반 비음 이차식 \(f=\ell^2+\kappa x(1-x)\), \(\kappa\ge0\)에서는

\[
\frac{\mathcal P_f}{\mathcal P_l}
=\frac{h_l(\ell^2)}{h_l(\ell^2)+\kappa B_l}
\frac{h_f(\ell^2)}{h_l(\ell^2)}
+\frac{\kappa B_l}{h_l(\ell^2)+\kappa B_l}\frac{B_f}{B_l}.
\]

\(\ell\equiv0\) 또는 \(\kappa=0\)이면 해당 항은 직접 생략한다. 분모는 \(f\not\equiv0\)일 때 항상 양수다. 그 결과는

\[
\boxed{
\min\!\left(\lambda_-,\frac{B_f}{B_l}\right)
\le\frac{\mathcal P_f(T)}{\mathcal P_l(T)}
\le\max\!\left(\lambda_+,\frac{B_f}{B_l}\right).}
\]

이것은 충분한 외부 상한만이 아니라 정확한 전체 범위다. eigenvalue가 끝점이면 해당 squared-linear source, \(B_f/B_l\)가 끝점이면 \(x(1-x)\)가 equality를 만든다. 두 equality 이력의 비음 조합과 가열 분모 정규화를 사용하면 사이의 모든 비율도 달성된다.

일반 equality 조건은 선택된 유효 분해에서 양의 분모 weight를 가진 모든 성분의 비율이 같은 극값인 것이다. \(B_f/B_l\)가 eigenvalue 구간의 strict 내부이고 eigenvalue가 단순하면 극값은 대응 eigenvector의 square ray에서만 달성된다. 중복 eigenvalue나 동일한 \(B\) 비율에서는 equality 집합이 넓어진다.

중요한 범위 구분: 여기서 얻은 equality source가 \(q(T)=0\)일 수 있다. \(q(T)=q_0>0\)를 별도로 강제하는 다른 클래스에서는 일부 경계가 달성되지 않고 inf/sup로만 남을 수 있다. 앞 절의 비감소·끝점 정규화 클래스와 혼합해서 주장하지 않는다.

### 계산 형태와 exact 외향 bound

\(D_l=\det A_l>0\), \(D_f=\det A_f\),

\[
C=(A_f)_{00}(A_l)_{11}+(A_f)_{11}(A_l)_{00}
-2(A_f)_{01}(A_l)_{01}
\]

로 놓으면 \(\det(A_f-\lambda A_l)=D_l\lambda^2-C\lambda+D_f\)다. 따라서

\[
\lambda_\pm=\frac{C\pm\sqrt{C^2-4D_lD_f}}{2D_l}.
\]

\(A_f\succ0\)이면 작은 근은 \(2D_f/[C+\sqrt{C^2-4D_lD_f}]\)로 평가할 수 있다. 구현에서는 exact 기록값으로 분모와 determinant의 부호를 먼저 확인해야 한다. 표시용 근을 반올림한 값만으로 엄밀한 외향 bound를 주장하지 않는다.

유리수 \(L,U\)에 대해

\[
A_f-LA_l\succeq0,\quad UA_l-A_f\succeq0,
\quad B_f-LB_l\ge0,\quad UB_l-B_f\ge0
\]

를 exact arithmetic으로 확인하면 \([L,U]\)는 제곱근 반올림에 의존하지 않는 인증 구간이다. 대칭 2×2 matrix의 양의 준정부호는 두 대각 원소와 determinant가 모두 비음인지로 확인할 수 있다. 이 인증은 저장된 소수 기록의 계산에 대한 것이며 원자율·grid·실제 kernel의 오차를 새로 인증하지 않는다.

### 퇴화 경우

- \(B_l=0<B_f\): \(x(1-x)\)는 legacy 가열 0·fullBED 가열 양수이므로 그 자체의 비율은 미정의다. legacy 응답이 양수인 source를 작게 섞으면 비율이 무한히 커질 수 있다.
- \(B_l=B_f=0\): 해당 pure source는 \(0/0\)이다. 분모 양수 이력의 비율에서는 이 성분을 제거할 수 있다.
- \(A_l\) singular: legacy가 관측하지 못하는 squared-linear source가 생긴다. fullBED가 그 source에 양의 응답을 가지면 같은 무한대 문제가 발생한다. 두 모델의 공통 nullspace이면 실제 유효 부분공간으로 제한해 따로 분석해야 한다.
- \(p_l=0\): 모든 source에서 legacy의 시각 \(T\) 가열이 0이므로 유한한 모델 비율 전체 범위가 정의되지 않는다.

이번 기록이 strict 양성 조건을 만족하는지는 주 실행자의 exact 후처리에서 확인해야 한다. 여기는 수치 PASS를 선취하지 않는다.

## 4. source가 꺼진 뒤의 끝점 memory

초기 amplitude \(q_*\)로 시작하는 declining 이력

\[
q(t)=q_*(1-t/T)^2,\qquad 0\le t\le T
\]

과 이후의 0을 생각하면 \(q(T)=0\)이지만

\[
\boxed{\mathcal P_m(T)=H_mq_*(p_m-2R_m+S_m)
=H_mq_*\int_{[0,T]}(\tau/T)^2\,dF_m.}
\]

이 값은 비음이며 \(F_m((0,T])>0\)이면 양수다. \(\tau=0\)의 즉시 성분은 0, \(\tau=T\)의 지연 성분은 \(q(0)=q_*\)를 읽는다.

\[
q(t)=4q_*(t/T)(1-t/T),\qquad 0\le t\le T
\]

는 **포물선형 pulse**이며 삼각형 pulse가 아니다. \(q_*\)는 \(T/2\)에서의 peak다. 양 끝과 이후 source는 0이지만

\[
\boxed{\mathcal P_m(T)=4H_mq_*(R_m-S_m).}
\]

이 값은 \(F_m((0,T))>0\)이면 양수다. 두 경계 지연 \(\tau=0,T\)의 원자는 이 pulse의 끝점 가열에 기여하지 않는다. 진짜 piecewise-linear 삼각형 pulse에는 일반적으로 \(T/2\)에 대한 추가 절단 정보가 필요하다.

두 경우 모두 순간 가열 예측은 0이다. 실제 가열이 양수일 때 실제 가열 기준 상대 결손은 1로 정의할 수 있지만, 순간 예측으로 나눈 상대오차는 정의되지 않는다. 보고에서는 \(H_mq_*\)로 정규화한 절대 응답 또는 실제 단위 가열을 사용한다.

## 5. 누적 열량은 추가 모멘트를 요구한다

끝점 가열과 누적 열량은 다른 functional이다. \(U_{3,m}=\mathbb E[(1-\tau/T)_+^3]\)로 두면 Fubini 적분에서

\[
\int_0^T\mathcal P_m(t)\,dt
=H_mq_*T\left(\alpha R_m+\frac\beta2S_m+\frac\gamma3U_{3,m}\right).
\]

따라서 이차항이 실제로 남으면 \(p,R,S\)만으로 누적 열량을 정확히 결정할 수 없다. 상수와 선형 source의 누적량 \(H_mq_*TR_m\), \(H_mq_*TS_m/2\)는 기존 결과대로 닫힌다.

비결정성의 순수 수학적 예: \(z=0,1/3,2/3,1\)에 각각 weights \((1/6,1/2,0,1/3)\) 또는 \((1/3,0,1/2,1/6)\)를 주면 둘 다 \(p=1,R=1/2,S=7/18\)이지만 \(U_3\)는 각각 \(19/54\), \(17/54\)다. 이는 pRS만의 보편적 결정 공식을 배제하는 반례이며 CR cache의 실제 kernel을 적합하거나 대체한 것이 아니다.

## 6. 해석 한계와 적용 상태

모든 모델 비율은 같은 source amplitude·이력·시각·스펙트럼·bath·원 정규화 안의 fullBED/legacy 차이다. reference가 물리적 진실이라고 정하지 않았으므로 이 비율 범위를 모든 원자물리 오차의 상한으로 부르지 않는다. 임의 차수·비다항 source, 시간 변화 bath, 실제 cosmological history, 실제 CR의 전체 가열 비율에는 확장하지 않는다. 시간 의존 kernel 자체에 대해 endpoint functional를 새로 정의할 수는 있지만 현재 고정 kernel의 cached pRS를 그대로 이식할 근거가 되지는 않는다.

이 유도는 원 F operator binding HOLD, G frontier, H의 원래 예산·수치 정확도·실패·reservation을 바꾸지 않는다. `selected_record`와 `birth_defined`는 별도 source로 평가해야 하며 두 기록을 혼합한 kernel을 만들지 않는다.

적용한 절차: 호스트 모델 GPT-6 Astra에 대해 research harness v4.0.0의 START_HERE, PROJECT_INSTRUCTIONS, MODEL_ROUTING, phase 01, ultralight, 초기 state 템플릿을 실제로 읽었다. 초기 archive lookup에서 `state/RESEARCH_STATE.md` suffix가 원본과 templates 둘에 일치해 read command가 exit 1로 종료되었고, 정확한 entry 이름으로 state와 routing을 읽었다. 이는 읽기 경로의 구현 문제이며 과학 실행 실패가 아니다. 새 계산은 하지 않았고 본 메모는 root의 단일 milestone 산출물에 통합하도록 전달한다.
