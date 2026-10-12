# 팽창하는 물질 셀의 충돌 시계와 에너지 잔차 추정

연구 단위: BASS_CR 다음 이론 루프, collision-clock 분과. 2026-10-12.

## 결과와 적용 위치

고정 배경에서 얻은 전자 cascade 생성자에 시간 의존성을 연결하는 두 가지 구성을 완성한다.

1. 모든 충돌 채널의 생성자와 출력률이 같은 양의 함수로 배율 조정될 때, 물리 부피 희석을 제거한 상태와 누적 충돌 시계로 기존 semigroup를 정확히 재사용한다.
2. 실제 PHYS02의 Coulomb logarithm이 밀도에 따라 변하는 경우에는 그 변화가 고정된 한 drift 행렬에 곱해지는 계수로 분리된다. 공통 배율에서 벗어나는 이 항, 추가 단열 에너지 drift, source의 진폭·모양 차이를 입력 에너지 예산으로 제어하는 Duhamel 추정을 구성한다.

각 정리는 아래의 유한 에너지 격자와 물질 셀 모델에 대한 직접 증명이다. 기존 PHYS02C/E 실행의 단위·source·행렬 정의를 재사용한다. 이번 기여는 실제 BASS_CR normalization, Coulomb prescription, source envelope, energy/number output의 명시적 연결이다.

## 1. 기존 BASS_CR 좌표와의 정확한 대응

재사용 원문은 복원된 CR-RUX-M1B-SOURCE-BINDING-20261012의 DERIVATION_KO.md §4와 원 causal_cascade.py다. 출처 경로와 SHA256은 SOURCE_READ_RECORD.json에 둔다.

원 기록은 무차원 시간 \(u=t/T_0\), \(T_0=10^{10}\,\mathrm{s}\)에서

\[
\frac{dz}{du}=G_u z+u b,\qquad z(0)=0
\tag{1.1}
\]

를 사용한다. 실제 active/energy 좌표에서의 에너지 밀도와 생성자는

\[
x_E=\epsilon_{\rm eV}U_*z_E,\qquad
G_{{\rm phys},EE}=\frac{(G_u)_{EE}}{T_0},\qquad
s_E(t)=q_{\rm phys}(t)b_E,\qquad
q_{\rm phys}(t)=q_*\frac{t}{T_0}.
\tag{1.2}
\]

여기서 energy source 벡터 \(b_E=(b_1+b_2)_E\)는 원 기록 그대로다. 각 birth 열은 같은 전체 선택 에너지 분모를 사용한다. 원 augmented 상태의 number 좌표는 \(n_N=U_*z_N\)로 바뀐다. 따라서 SI active energy를 입력으로 받는 number row와 direct number source는

\[
c_{{\rm phys},N}^T=\frac{(G_u)_{N,\rm act}}{T_0\epsilon_{\rm eV}},
\qquad s_N(t)=\frac{q_{\rm phys}(t)}{\epsilon_{\rm eV}}b_N.
\tag{1.2a}
\]

전체 mixed-unit 변환은 energy 좌표에 1, number 좌표에 \(1/\epsilon_{\rm eV}\)인 대각 행렬 \(D_{\rm SI}\)를 사용하여
\(Y_{\rm SI}=\epsilon_{\rm eV}U_*D_{\rm SI}z\),
\(G_{\rm phys}=D_{\rm SI}G_uD_{\rm SI}^{-1}/T_0\),
\(s_{\rm SI}=q_{\rm phys}D_{\rm SI}b\)로 쓸 수 있다.

실제 active 좌표는 각 cell의 **전자 에너지**다. 따라서 active energy functional은 \(w=(1,\ldots,1)^T\)이고, active number functional은 각 energy 단위를 일치시킨 후 \((1/W_1,\ldots,1/W_n)^T\)다. 물리적 SI 에너지 좌표에서는 \(W_j\)도 J로 넣는다. cutoff energy, cutoff number, ionization counts, low-cross diagnostics는 서로 다른 좌표다. 이하에서는 active block

\[
L_0=(G_u)_{\mathrm{act},\mathrm{act}}/T_0,\qquad
h_0^T=(G_u)_{\mathrm{heat},\mathrm{act}}/T_0
\tag{1.3}
\]

를 사용한다. 에너지 출력률 \(h_0\)의 성분 단위는 \(\mathrm{s^{-1}}\)다.

아래의 일반 \(w>0\) 표기는 다른 에너지 좌표에도 같은 증명을 쓰기 위한 것이다. 입자수 좌표 \(y_j\)를 쓰면 \(x_j=W_jy_j\), \(D=\operatorname{diag}W_j\), \(L_x=DL_yD^{-1}\), \(w_y=(W_j)\), \(w_x=\mathbf1\)의 정확한 대응이 있다.

## 2. 충돌 시계의 가정과 정리

고정 유한 구간 \(I=[t_i,T]\)에서 물질 셀의 상대 proper volume을 \(V(t)>0\), \(V(t_i)=1\)로 정한다. \(V\)는 절대연속이며

\[
\frac{\dot V}{V}=\Theta(t)
\tag{2.1}
\]

다. 시간은 선택한 기체 frame의 proper time이다. \(a(t)\)는 양의 공통 충돌률 배율로, 조각별 연속이고 이 구간에서 0보다 큰 하한을 갖는다고 둔다. 이 \(a\)는 우주론적 scale factor와 다른 함수다. \(s(t)\)는 적분 가능한 physical source vector이다. \(x(t)\)는 active energy density vector이고

\[
\dot x=\{a(t)L_0-\Theta(t)I\}x+s(t).
\tag{2.2}
\]

### 정리 CC1: 부피와 충돌 시계에 의한 정확한 재사용

\[
X(t)=V(t)x(t),\qquad
\tau(t)=\int_{t_i}^{t}a(v)\,dv
\tag{2.3}
\]

로 두면

\[
\boxed{
\frac{dX}{d\tau}=L_0X+J(\tau),\qquad
J(\tau)=\frac{V(t(\tau))}{a(t(\tau))}s(t(\tau)).
}
\tag{2.4}
\]

따라서 \(K(\sigma)=\exp(L_0\sigma)\)를 이용해

\[
\boxed{
x(t)=\frac1{V(t)}
\left[
K(\tau(t))x_i+
\int_{t_i}^{t}V(v)K\{\tau(t)-\tau(v)\}s(v)\,dv
\right].
}
\tag{2.5}
\]

초기 \(V(t_i)\)를 1로 정하지 않으면 첫 항의 \(x_i\)를 \(V(t_i)x_i\)로 바꾼다.

**증명.** 곱 미분을 수행하면

\[
\dot X=\dot Vx+V\dot x
=\Theta Vx+VaL_0x-V\Theta x+Vs
=aL_0X+Vs.
\]

\(d\tau=a\,dt\)로 나누어 (2.4)를 얻는다. 상수 행렬 \(L_0\)에 대해 variation of constants를 적용하고, source 적분에서 \(d\sigma=a(v)\,dv\)를 대입하면 (2.5)가 나온다. source의 \(1/a\)와 시간 적분의 \(a\)가 정확히 소거된다. 역대입은 (2.2)와 같은 초기값을 준다. \(\square\)

고정 source shape \(s(t)=bq(t)\)의 변환된 scalar source는 \(Vq/a\)다. 여러 저장 열 \(B=(b_1,\ldots,b_m)\)을 쓸 경우 \(s=Bq\)에 대해 각 \(q_j\)를 같은 방식으로 변환한다. source vector 자체가 시간에 따라 바뀌어도 (2.5)는 성립한다. 기존의 유한 source basis를 사용하려면 그 basis 밖의 차이를 §5의 \(\delta s\)로 유지한다.

### 정리 CC2: 물리적 heat rate와 누적 heat

reference heat row가 \(h_0\)이며 실제 collision heat row가 \(h(t)=a(t)h_0\)일 때,

\[
\boxed{
p_h(t)=a(t)h_0^Tx(t)
=\frac{a(t)}{V(t)}h_0^TX(\tau(t)).
}
\tag{2.6}
\]

물질 셀에 공급된 누적 heat를 초기 proper volume당 에너지로 나타내면

\[
\boxed{
\mathcal Q_h(t)
=\int_{t_i}^{t}V(v)p_h(v)\,dv
=\int_0^{\tau(t)}h_0^TX(\sigma)\,d\sigma.
}
\tag{2.7}
\]

정의 (2.7)는 열의 공급 장부이며, 해당 에너지를 최종 부피당으로 보고할 때는 \(\mathcal Q_h(t)/V(t)\)를 사용한다. 열적 상태의 압력 일은 receiver의 에너지식에 별도로 포함된다. 한편 각 시각의 proper-volume heat rate를 그대로 적분한 양은

\[
\int_{t_i}^{t}p_h(v)\,dv
=\int_0^{\tau(t)}
\frac{h_0^TX(\sigma)}{V(t(\sigma))}\,d\sigma.
\tag{2.8}
\]

식 (2.7)과 (2.8)는 서로 다른 부피 기준의 누적 정의다. 고정 부피에서는 일치한다.

\(s=bq\), \(x_i=0\)일 때 pulse heat kernel과 누적 kernel을

\[
k_h(\sigma)=h_0^TK(\sigma)b_{\rm act},\qquad
F_h(\sigma)=\int_0^\sigma k_h(\rho)\,d\rho
\tag{2.9}
\]

로 정의하면

\[
p_h(t)=\frac{a(t)}{V(t)}
\int_{t_i}^{t}V(v)q(v)
k_h\{\tau(t)-\tau(v)\}\,dv,
\tag{2.10}
\]

\[
\boxed{
\mathcal Q_h(t)=
\int_{t_i}^{t}V(v)q(v)
F_h\{\tau(t)-\tau(v)\}\,dv.
}
\tag{2.11}
\]

**증명.** (2.6)은 출력 정의와 \(x=X/V\)에서 바로 따른다. (2.7)은 \(a\,dt=d\tau\)를 적용한 결과다. (2.11)은 (2.5)를 (2.7)에 대입하여 적분 순서를 바꾸면 얻는다. 비음 source와 kernel에서는 Tonelli를, 일반 적분 가능한 source에서는 유한 구간의 절대적분 가능성을 사용한다. \(\square\)

source projection이 cutoff energy 같은 sink 좌표에 직접 넣는 성분 \(s_\ell(t)\)이 있으면 해당 누적 출력은

\[
\dot{\mathcal Q}_\ell
=a(t)\ell_0^TX+V(t)s_\ell(t)
\tag{2.12}
\]

로 계산한다. 원 source vector의 sink 성분도 유지한다. heat source 성분은 기존 PHYS02에서 0이다.

기존 \(H_0,R,S\)는 한 source family와 horizon에서 얻은 kernel 적분값이다. 새로운 \(V,a,q\)의 재사용 입력은 (2.9)의 kernel 또는 필요한 적분 모멘트다. 변환된 \(Vq/a\)가 원 ramp와 같은 family에 속하면 원 모멘트를 연결하고, 다른 시간 모양이면 (2.10)–(2.11)의 가중 적분을 평가한다.

## 3. 원 PHYS02 Coulomb 처방의 밀도 의존성을 고정 행렬로 분리

원 causal_cascade.py의 lines 200–212는 \(n_{e0}\)에서

\[
\begin{aligned}
v_j&=\sqrt{2W_j\epsilon_{\rm eV}/m_e},&
\omega_0&=\sqrt{\frac{n_{e0}e^2}{\epsilon_0m_e}},\\
L_{j,0}&=\min\!\left[
\log\!\frac{v_jW_j\epsilon_{\rm eV}}{\kappa\omega_0},
\log\!\frac{2W_j\epsilon_{\rm eV}}{\hbar\omega_0}+c_q
\right],\\
B_{j,0}&=\kappa_jL_{j,0},&
\kappa_j&=\frac{4\pi\kappa^2n_{e0}}{m_ev_j\epsilon_{\rm eV}},
\qquad
\kappa=\frac{e^2}{4\pi\epsilon_0}.
\end{aligned}
\tag{3.1}
\]

여기서 \(W_j\)는 eV 수치, \(B_{j,0}\)와 \(\kappa_j\)는 \(\mathrm{eV\,s^{-1}}\), \(c_q\)는 원 코드의 선택값 0 또는 \(-1/2\)다.

온도·조성·격자·원자 단면적·재분배 처방을 고정하고 모든 target density를 같은 \(d(t)>0\)로 배율 조정하는 이론적 확장을 정의한다. 따라서 \(n_e(t)=d(t)n_{e0}\), \(n_{\rm HI}(t)=d(t)n_{\rm HI,0}\), \(n_{\rm HeI}(t)=d(t)n_{\rm HeI,0}\)다. 원 코드의 \(\omega\)는 \(\sqrt d\,\omega_0\)로 변한다. 두 logarithm이 모두 \(-\tfrac12\log d\)만큼 이동하므로

\[
\boxed{
L_j(d)=L_{j,0}-\frac12\log d,\qquad
B_j(d)=d B_{j,0}-\frac{d\log d}{2}\kappa_j.
}
\tag{3.2}
\]

고전·양자 두 branch의 minimum 선택은 같은 양을 빼는 연산과 교환한다. 유효 구간은

\[
\boxed{
\min_j\left(L_{j,0}-\frac12\log d(t)\right)>0
\quad(t\in I)
}
\tag{3.3}
\]

로 정한다. 이 구간에서는 각 Coulomb stopping coefficient가 양수다.

원 drift의 한 column에서 이전 에너지를 \(W_{j-1}\)로 두되 첫 active node의 이전 값은 원 CUT \(=0.1\,\mathrm{eV}\)로 사용한다. \(\Delta W_j=W_j-W_{j-1}>0\)다. 원 project를 포함한 단위-rate energy transfer column을 \(D_j\)로 정의한다.

- active \(j\)의 diagonal은 \(-1\);
- 이전 active node 또는 cutoff energy의 기여는 \(W_{j-1}/W_j\);
- heat 기여는 \(\Delta W_j/W_j\);
- cutoff number와 low-cross diagnostic 성분은 원 project가 정한 별도 ledger 값.

그러면 원 drift coefficient는 \(B_{j,0}/\Delta W_j\)이고

\[
C_0=\sum_j\frac{\kappa_j}{\Delta W_j}D_j
\tag{3.4}
\]

라는 하나의 고정 행렬을 정의할 수 있다. 시간 단위는 physical second다. SI number 행에는 (1.2a)의 \(1/\epsilon_{\rm eV}\) 변환을 적용한다. atomic ionization/excitation rate는 고정 energy에서 target density에 선형이므로 원 lines 304–310의 rate들은 정확히 \(d\)배가 된다. 따라서 전체 energy/number ledger를 포함한 동일 처방의 생성자는

\[
\boxed{
G_{\rm phys}(d)
=d\,G_{\rm phys}(1)-\frac{d\log d}{2}C_0.
}
\tag{3.5}
\]

active block과 heat/cutoff energy/cutoff number의 모든 해당 행에서 같은 항등식이 성립한다. 기존 source vector \(b\)와 새 physical injection \(s(t)\)는 별도 입력이다. proton population과 target density가 함께 바뀔 때 생기는 birth 진폭·shape의 변화는 실제 source 정의에서 계산해 \(s(t)\)에 넣는다.

식 (3.5)는 \(dL_0\)를 충돌 시계로 사용하고 나머지를 명시적으로 추적하는 방법을 준다.

\[
\Delta_{\rm Coul}(t)
=-\frac{d(t)\log d(t)}2(C_0)_{\rm act}.
\tag{3.6}
\]

입력 배경에 따른 단열 kinetic-energy drift, 상대 species density 변화 또는 다른 rate shape 변화가 있으면 각 항을 \(\Delta\)에 더한다. 부피 희석 \(-\Theta I\)는 §2의 변수 변환으로 처리하고, kinetic energy의 이동은 이 \(\Delta\)에 들어간다. 두 작용은 원 energy cell에 미치는 효과가 다르다.

## 4. 양의 에너지 가중치와 시간 의존 전파의 추정

active 좌표에 대해 \(w_i>0\)를 고정하고

\[
\|z\|_w=\sum_iw_i|z_i|,\qquad
\|M\|_w=\max_j\frac{\sum_iw_i|M_{ij}|}{w_j}
\tag{4.1}
\]

로 정의한다. source 기록의 active energy 좌표에서는 \(w_i=1\)이다. number ledger나 진단용 교차 ledger를 zero energy weight로 붙이지 않고 active energy 공간에서 이 norm을 사용한다.

### 보조정리 CC3: Metzler 생성자의 공통 에너지 추정

\(A(t)\)가 Metzler, 즉 diagonal 밖의 성분이 비음이고,

\[
w^TA(t)\le\beta(t)w^T
\tag{4.2}
\]

가 column마다 성립한다고 하자. \(\beta\)는 적분 가능하다. 동차계의 propagator \(\Phi_A(t,v)\)는

\[
\boxed{
\|\Phi_A(t,v)\|_w
\le\exp\!\left(\int_v^t\beta(r)\,dr\right).
}
\tag{4.3}
\]

**증명.** \(\dot z=A z\)에서 각 성분의 절댓값에 대해 diagonal 항은 \(A_{ii}|z_i|\), off-diagonal 항은 \(A_{ij}|z_j|\)로 상계된다. 따라서 상부 미분 또는 거의 모든 시각의 미분에서

\[
\frac{d^+}{dt}\|z\|_w
\le w^TA|z|\le\beta\|z\|_w.
\]

적분형 Grönwall 추정이 (4.3)을 준다. 비음 초기값의 해는 비음으로 유지된다. 후자는 각 component가 0에 처음 도달했을 때 다른 component에서 오는 속도가 비음이라는 비교법, 또는 양의 작은-step 근사로 확인한다. \(\square\)

행렬 원소가 적분 가능하고 (4.2)가 거의 모든 시각에서 성립하면 같은 적분 증명을 적용한다. \(\beta\le0\)이면 에너지 norm이 수축한다.

## 5. 비가환 변화와 source mismatch에 대한 Duhamel 정리

같은 부피 함수 \(V\)를 사용하는 실제계와 reference를

\[
\begin{aligned}
\dot X&=A(t)X+S(t),&
A(t)&=a(t)L_0+\Delta(t),&
S(t)&=V(t)s(t),\\
\dot{\widehat X}&=a(t)L_0\widehat X+\widehat S(t),&&&
\widehat S(t)&=V(t)\widehat s(t)
\end{aligned}
\tag{5.1}
\]

로 둔다. \(\widehat X_i\ge0,\widehat S\ge0\), \(L_0\)가 Metzler이고 \(w^TL_0\le0\)라고 가정한다. 실제 \(A\)는 CC3의 가정을 만족한다. \(\Delta\)와 \(L_0\) 사이의 교환성은 요구하지 않는다.

source만으로 계산 가능한 reference energy envelope는

\[
\boxed{
\overline U(t)=w^T\widehat X_i+
\int_{t_i}^{t}w^T\widehat S(v)\,dv.
}
\tag{5.2}
\]

reference positivity와 passivity로 \(w^T\widehat X(t)\le\overline U(t)\)가 성립한다. 원 b의 active energy 합이 \(\eta_{\rm act}\)이면 \(\widehat s=b_{\rm act}q\)의 항은 \(\eta_{\rm act}Vq\)다. source의 직접 sink 에너지도 보수적 envelope에 포함하려면 원 energy functional의 실제 합을 사용한다.

### 정리 CC4: reference 궤적을 요구하지 않는 에너지 오차 상계

\[
\varepsilon(t)=\|\Delta(t)\|_w,\qquad
\eta(t)=V(t)\|s(t)-\widehat s(t)\|_w
\tag{5.3}
\]

를 두면

\[
\boxed{
\begin{aligned}
\|X(t)-\widehat X(t)\|_w
\le {}&
e^{\int_{t_i}^{t}\beta}\|X_i-\widehat X_i\|_w\\
&+\int_{t_i}^{t}
e^{\int_v^t\beta}
\{\varepsilon(v)\overline U(v)+\eta(v)\}\,dv.
\end{aligned}
}
\tag{5.4}
\]

proper-volume state의 오차는 우변을 \(V(t)\)로 나눈 값으로 제한된다.

**증명.** \(e=X-\widehat X\)에 대해

\[
\dot e=Ae+\Delta\widehat X+(S-\widehat S).
\]

따라서 정확한 Duhamel 항등식은

\[
e(t)=\Phi_A(t,t_i)e_i+
\int_{t_i}^{t}\Phi_A(t,v)
\{\Delta(v)\widehat X(v)+S(v)-\widehat S(v)\}\,dv.
\tag{5.5}
\]

CC3, 행렬 norm의 정의, \(w^T\widehat X\le\overline U\)를 차례로 적용하면 (5.4)를 얻는다. \(\square\)

source mismatch는 scalar 진폭과 energy shape로 따로 기록할 수 있다. \(s=qb,\widehat s=\widehat q\widehat b\), \(q,\widehat q\ge0\), \(b,\widehat b\ge0\), \(w^Tb=w^T\widehat b=1\)로 자기 source energy를 정규화한 경우

\[
\boxed{
\eta\le V\left[
|q-\widehat q|
+\min(q,\widehat q)\|b-\widehat b\|_w
\right].
}
\tag{5.6}
\]

\(\mu_i=w_ib_i\)는 energy probability vector이므로 두 번째 norm은 \(2\,{\rm TV}(\mu,\widehat\mu)\)다. 식 (5.6)은 \(m=\min(q,\widehat q)\)를 사용한
\(qb-\widehat q\widehat b=(q-m)b-(\widehat q-m)\widehat b+m(b-\widehat b)\)
에서 따른다. 원 저장 b를 임의로 다시 정규화하는 대신, 실제 \(\eta_j=w^Tb_j\)를 포함한 physical source 전체에 (5.3)을 직접 적용해도 된다.

한 에너지 구간의 source를 생략한 경우에는 그 source의 주입 에너지가 \(\eta\)에 직접 들어간다. 이로써 이전 루프의 선택 구간 밖 에너지 예산을 같은 식에 연결한다.

## 6. 누적 heat까지 포함하는 더 직접적인 에너지 추정

actual heat row를 \(h(t)^T\), reference를 \(a(t)h_0^T\)로 두고 source의 direct heat 성분을 각각 \(s_h,\widehat s_h\)로 둔다.

\[
Y=\binom{X}{\mathcal Q_h},\qquad
\mathcal A(t)=
\begin{pmatrix}A(t)&0\\h(t)^T&0\end{pmatrix},
\qquad
\mathcal S(t)=\binom{Vs}{Vs_h}.
\tag{6.1}
\]

열 공급 장부의 좌표 단위가 에너지이므로 양의 가중치는 \(\widetilde w=(w,1)\)이다. \(A\)가 Metzler, \(h\ge0\)이고

\[
w^TA+h^T\le0
\tag{6.2}
\]

이면 \(\widetilde w^T\mathcal A\le0\)다. active energy의 감소 중 heat 이외의 sink가 있으면 (6.2)는 부등식이고, 모두 포함하면 등식이다.

### 정리 CC5: state와 누적 heat를 동시에 제어하는 상계

reference도 같은 passivity를 만족한다고 하자. 행렬 차이를

\[
\mathcal D(t)=
\begin{pmatrix}
\Delta(t)&0\\
[h(t)-a(t)h_0]^T&0
\end{pmatrix}
\tag{6.3}
\]

로 두고, active 입력에서 증강 energy norm으로 가는 column norm을

\[
\widetilde\varepsilon(t)=
\max_j\frac{\sum_iw_i|\Delta_{ij}(t)|
+|h_j(t)-a(t)h_{0j}|}{w_j}
\tag{6.4}
\]

로 정의한다. 그러면

\[
\boxed{
\begin{aligned}
&\|X(t)-\widehat X(t)\|_w
+|\mathcal Q_h(t)-\widehat{\mathcal Q}_h(t)|\\
&\quad\le
\|Y_i-\widehat Y_i\|_{\widetilde w}\\
&\qquad+
\int_{t_i}^{t}
\left[\widetilde\varepsilon(v)\overline U(v)
+V(v)\{\|s-\widehat s\|_w+|s_h-\widehat s_h|\}\right]\,dv.
\end{aligned}
}
\tag{6.5}
\]

**증명.** 증강계의 propagator는 CC3에서 \(\beta=0\)인 수축이다. \(\mathcal D\widehat Y\)는 \(\widehat{\mathcal Q}_h\)에 의존하지 않고 active \(\widehat X\)에만 의존한다. CC4의 Duhamel 증명에서 이 항의 norm을 \(\widetilde\varepsilon\,\overline U\)로 제한하면 된다. \(\square\)

cutoff energy, binding energy, excitation energy 같은 서로 중복되지 않는 에너지 장부를 함께 붙이면 \(\widetilde w=(w,1,\ldots,1)\)와 각 ledger error의 절댓값 합으로 같은 증명이 성립한다. low-cross energy는 과거 crossing의 진단 장부이므로 전체 보존 에너지와 중복된다. 이 진단 좌표는 (6.2)의 에너지 합에서 분리한다.

number ledger의 출력 오차는 별도의 dual estimate를 사용한다. \(\dot{\mathcal N}=c(t)^TX+V s_N(t)\), \(\dot{\widehat{\mathcal N}}=a c_0^T\widehat X+V\widehat s_N\)라면

\[
|\delta\mathcal N(T)|
\le|\delta\mathcal N_i|+
\int_{t_i}^{T}
\left[
\|c(t)\|_{w,*}E_X(t)
+\|c(t)-a(t)c_0\|_{w,*}\overline U(t)
+V|s_N-\widehat s_N|
\right]dt,
\tag{6.6}
\]

\[
\|c\|_{w,*}=\max_j\frac{|c_j|}{w_j},
\tag{6.7}
\]

여기서 \(E_X(t)\)는 (5.4) 또는 (6.5)의 state error 상계다. cutoff number에는 에너지 norm의 0 weight 대신 필요한 number observable의 계수를 명시한다.

## 7. 반응 계수만으로 계산하는 상계와 충돌 시계 선택

고정 에너지 전달 행렬 \(B_k\)와 비음 반응률 \(r_k(t)\)에 대해

\[
A(t)=\sum_k r_k(t)B_k+A_{\rm add}(t),\qquad
L_0=\sum_k r_{k0}B_k
\tag{7.1}
\]

로 두자. energy output row도 반응별로 붙인 증강 행렬을 \(\widetilde B_k\)로 표기한다. 각 행렬은 Metzler이며 에너지 가중 column sum이 비양이라고 가정한다. 추가 항이 있을 때 실제 total \(A,h\)의 (6.2)도 확인한다. 그러면 실제의 양의 rate 조합은 passivity를 유지한다.

\[
\delta r_k(t)=r_k(t)-a(t)r_{k0},\qquad
\gamma_k=\|\widetilde B_k\|_{\widetilde w}
\tag{7.2}
\]

로 두면

\[
\boxed{
\widetilde\varepsilon(t)
\le\sum_k|\delta r_k(t)|\gamma_k
+\|\widetilde A_{\rm add}(t)\|_{\widetilde w}.
}
\tag{7.3}
\]

source와 rate history만으로 (6.5)의 적분을 평가할 수 있다. 필요한 norm은 고정 행렬의 column sum 한 번으로 계산된다.

한 반응의 diagonal loss가 \(-\lambda_{kj}\)이고 에너지 출력까지 합한 비음 off-diagonal column sum이 \(w_j\lambda_{kj}\) 이하이면

\[
\boxed{\gamma_k\le2\max_j\lambda_{kj}.}
\tag{7.4}
\]

이는 absolute column sum에서 diagonal loss와 outgoing energy를 더한 결과다. 해당 채널이 정확히 에너지를 보존하면 모든 실제 outgoing energy 장부를 포함한 nonzero column에서 등호가 성립한다.

### 실제 Coulomb 항의 certificate

식 (3.5)의 density clock \(a=d\)를 쓸 때

\[
\boxed{
\widetilde\varepsilon_{\rm Coul}(t)
=\frac{d(t)|\log d(t)|}{2}
\|\widetilde C_0\|_{\widetilde w}.
}
\tag{7.5}
\]

모든 실제 에너지 장부를 포함한 원 drift의 경우

\[
\|\widetilde C_0\|_{\widetilde w}
=2\max_j\frac{\kappa_j}{\Delta W_j}
\tag{7.6}
\]

이다. 이 expression은 원 격자의 이산 상태 norm에 대응한다. output별로 더 촘촘한 bounds가 필요하면 (5.5)의 실제 \(\Delta\widehat X\) 또는 backward output kernel을 사용해 column 최대값을 줄일 수 있다. 현재의 energy-budget 추정은 reference state trajectory를 입력으로 요구하지 않는다.

### 정리 CC6: 선택한 residual 상계를 최소화하는 scalar clock

\(r_{k0}>0\)인 채널에 대해

\[
\rho_k(t)=\frac{r_k(t)}{r_{k0}},\qquad
c_k=\gamma_k r_{k0}
\tag{7.7}
\]

로 둔다. 추가 항과 source를 고정하면 (7.3)의 clock 의존 부분은

\[
F_t(a)=\sum_k c_k|a-\rho_k(t)|
\tag{7.8}
\]

다. \(\sum_kc_k>0\)이면 \(F_t\)를 최소화하는 \(a\)는 \(\rho_k(t)\)의 weighted median이다. 즉 선택값의 양쪽에 엄격히 놓인 weight가 각각 전체의 절반을 넘지 않는 값이다. 허용 clock을 \(a_{\min}\le a\le a_{\max}\), \(a_{\min}>0\)로 정하면 weighted median \(m\)을 \(a_*=\min(a_{\max},\max(a_{\min},m))\)로 옮긴다. 모든 \(c_k=0\)이면 허용 clock을 임의로 선택해도 상계가 같다. 기준 rate가 0인 신규 채널은 \(|r_k|\gamma_k\)라는 clock 독립 잔차로 유지한다.

**증명.** \(F_t\)는 convex piecewise linear 함수다. \(a\)보다 작은 ratio의 weight 합에서 큰 ratio의 weight 합을 뺀 값이 subgradient이며, 같은 ratio의 weight는 양쪽 부호 사이의 구간을 채운다. \(0\in\partial F_t(a)\)가 weighted-median 조건과 동치다. 함수가 최소점 집합의 양쪽에서 각각 단조 감소·증가하므로 구간 제약에서는 위의 projection이 최소값을 준다. \(\square\)

reference energy envelope (5.2)는 \(a\)에 독립적이다. 따라서 이 pointwise 선택은 passivity에 기반한 (6.5)의 **명시한 계수 상계**의 적분도 최소화한다. 실제 observable error를 직접 최적화하려면 출력의 sensitivity를 추가 입력으로 사용한다.

## 8. 정확한 두 단계 cascade 판별 예제

고에너지 \(2E\)와 저에너지 \(E\)의 입자수 좌표 \(y=(y_1,y_2)^T\)를 사용한다. \(w=(2E,E)^T\), 입사 shape \(b=(1/(2E),0)^T\)다.

\[
L_0=\lambda
\begin{pmatrix}-1&0\\1&-1\end{pmatrix},
\qquad
h_0=\lambda E\binom11.
\tag{8.1}
\]

첫 반응은 \(2E\to E+E_{\rm heat}\), 두 번째는 \(E\to E_{\rm heat}\)다. \(w^TL_0+h_0^T=0\).

\[
V(t)=1+\frac{t}{t_*},\quad a(t)=V(t)^2,\quad
\Theta(t)=\frac1{t+t_*},\quad
q(t)=q_0V(t),\quad
\tau(t)=t+\frac{t^2}{t_*}+\frac{t^3}{3t_*^2},\quad t_i=0.
\tag{8.2}
\]

변환된 주입은 \(Vq/a=q_0\)로 일정하다. \(u=\lambda\tau\)라 하면 정확한 \(X=Vy\)는

\[
X_1=\frac{q_0}{2E\lambda}(1-e^{-u}),\qquad
X_2=\frac{q_0}{2E\lambda}\{1-(1+u)e^{-u}\}.
\tag{8.3}
\]

물리 heat rate, active energy, 누적 parcel heat는

\[
\boxed{
p_h(t)=q_0V(t)\left[1-\left(1+\frac u2\right)e^{-u}\right],
}
\tag{8.4}
\]

\[
w^TX=
\frac{q_0}{2\lambda}\{3-(3+u)e^{-u}\},
\qquad
\boxed{
\mathcal Q_h(t)
=q_0\tau(t)-\frac{q_0}{2\lambda}\{3-(3+u)e^{-u}\}.
}
\tag{8.5}
\]

직접 미분하면 \(\dot X=aL_0X+abq_0\), \(\dot{\mathcal Q}_h=Vp_h\), \(w^TX+\mathcal Q_h=q_0\tau\)가 각각 성립한다. \(\lambda=1/t_*\), \(T=t_*\)에서는

\[
p_h(T)=2q_0\left(1-\frac{13}6e^{-7/3}\right),\qquad
\mathcal Q_h(T)=q_0t_*\left(\frac56+\frac83e^{-7/3}\right).
\tag{8.6}
\]

source Jacobian을 빠뜨리면 변환된 source가 일정한 \(q_0\)와 달라져 (8.3)을 만족시키지 못한다. \(\tau(t)\) 대신 물리 \(t\)를 그대로 사용한 식은 \(u=7/3\)와 \(u=1\)을 구별하는 (8.6)에서 판별된다. physical heat의 \(a/V=V\) 인자를 생략하면 같은 시각의 rate가 2배 차이난다.

비가환 perturbation을 보기 위해

\[
B_1=\begin{pmatrix}-1&0\\1&0\end{pmatrix},
\qquad
B_2=\begin{pmatrix}0&0\\0&-1\end{pmatrix},
\qquad
[B_1,B_2]=\begin{pmatrix}0&0\\1&0\end{pmatrix}
\tag{8.7}
\]

로 둔다. \(r_1=a\lambda+\delta(t)\ge0,\ r_2=a\lambda\)인 실제계에서 heat rows는 각각 \((E,0),(0,E)\)다. 각 augmented column norm은 2이고 실제 energy balance는 모든 시각에 성립한다. 그러므로 동일 source와 초기값에서

\[
\|X-\widehat X\|_w+
|\mathcal Q_h-\widehat{\mathcal Q}_h|
\le2q_0\int_0^T|\delta(t)|\tau(t)\,dt.
\tag{8.8}
\]

\(|\delta|\le\delta_0\)이면

\[
\boxed{
\|X(T)-\widehat X(T)\|_w+
|\delta\mathcal Q_h(T)|
\le\delta_0q_0
\left(T^2+\frac{2T^3}{3t_*}+\frac{T^4}{6t_*^2}\right).
}
\tag{8.9}
\]

\(T=t_*\)에서 이 상계와 누적 source energy \(7q_0t_*/3\)의 비율은 \(\frac{11}{14}\delta_0t_*\)다. 비가환 반응률 변화도 지정한 source와 coefficient envelope만으로 직접 제한된다.

## 9. 구현에 넘길 최소 입력과 다음 연결

정리 CC1–CC2의 입력은 원 \(L_0,h_0,b_j\), \(V(t)\), \(a(t)\), physical source \(s(t)\), 초기 active stock이다. 사용할 energy/cutoff/number output row와 source의 직접 sink 성분도 함께 유지한다. 내부 시간의 단위 변환은 \(L_0=L_u/T_0\), \(h_0=h_u/T_0\)로 고정한다.

CC4–CC5의 추가 입력은 실제 rate coefficient 또는 \(\Delta(t)\), output row 차이, source mismatch energy, common energy-column inequality다. full reference trajectory를 사용하지 않는 certificate에는 (5.2)의 scalar input-energy envelope와 (7.3)의 coefficient bounds만 필요하다.

이번 루프의 실제 물리 연결은 다음 세 식이다.

\[
X_\tau=L_0X+\frac Va s,\qquad
G_{\rm phys}(d)=dG_{\rm phys}(1)-\frac{d\log d}{2}C_0,\qquad
|\delta\mathcal Q_h|+\|\delta X\|_w
\le\int\widetilde\varepsilon\,\overline U+\eta_{\rm energy}.
\]

thermal/nonthermal 상태변수의 에너지식과 moving cutoff 조건은 같은 루프의 별도 분과에서 결합한다. 여기서는 그 연결에 필요한 physical heat rate와 energy/number ledger를 분리해서 제공한다.

## 10. 검토와 실행 상태

- R1–R3: 유한 cascade, proper-time/material-volume convention, positive energy space, source 계보를 명시했다.
- R4–R5: 충돌 시계, 실제 Coulomb 한 행렬 보정, Duhamel energy/heat certificate, coefficient-optimal clock을 직접 구성·증명했다.
- R6: 역대입, 단위 대응, column energy balance를 유도문에서 확인했다. 별도 검토에서 SI number-row 변환, 제약 구간의 weighted median projection, source shape의 비음 조건을 명시하도록 보완했다.
- R7: 두 단계 cascade의 정확해, 비가환 반응 예제, 시간·부피·source Jacobian과 heat prefactor를 Wolfram Language로 1회 대수 검산하여 21/21 PASS를 얻었다. 실제 코드와 출력은 verify_analytic_case.wl, WOLFRAM_RAW_RESULT.json, ANALYTIC_CHECK_RESULT.json에 있다. Python의 SymPy import는 모듈 부재로 계산 전에 종료됐으며 이 환경 상태도 같은 결과 기록에 보존했다.
- R8–R10: 본 분과의 최종 판정은 독립 검토 후 통합 기록에 연결한다. 이번 분과에서 새 수송 실행, source quadrature, generator 생성, 과거 scientific suite, NCP 계산은 수행하지 않았다.


