# R5 — 저장된 HeIII finite operator의 인과적 RR clock 응답

**단위:** CR_RR_CAUSAL_ERLANG_CLOCK_V1  
**상태:** 구성적 유도 완료, R6 독립 검토 전. 이 문서는 새 solver 실행 또는 수치 PASS를 주장하지 않는다.  
**대상 경로:** `bass_cr/research/cr_rr_causal_clock_20261027`.

## 1. Authority와 정확한 문제

R5 시작 시 2026-10-27 06:07:40 UTC에 `research/cr-heiii-ground-rr-20261027` ref와 root AGENTS를 다시 읽었다. HEAD는 D `ec463db0c7e5c7fb5070796071c926caa4db6445`로 유지되었고, AGENTS SHA256은 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`이다. `survey_repos/FINAL_REF_REFRESH.json` 및 `CURRENT_FRONTIER_KO.md`의 병렬 변경도 읽었다. WU는 `e9276ea2ba8af2d73197a6852931fcafbf39ddf5`, REC synthesis는 `f9d2e979939949a9da8c4bcd04d7d83390bd3724`까지 전진했으나, source 회수·이론 인계 delta이며 현재 CR bath와 맞는 실제 주입 이력을 새로 제공하지 않는다.

본 단위의 \(K\)는 이전 HeIII NPZ에 저장된 binary64 `K_diag/K_lower/K_upper`의 각 비트열이 표현하는 **정확한 실수**로 이루어진 finite 행렬이다. 저장되기 전의 \(K_{\rm HeI}+\operatorname{diag}\lambda_{\rm HeII}\) 실수 합, 새로 생성한 hazard, continuum operator를 뜻하지 않는다. 이전 diagonal-addition loss는 이 정의로 없어지는 물리 오차가 아니며 기존 evidence로 남는다. [이전 engine](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/implementation/engine.py)

동일 NPZ `rhs_physical18`의 zero-based 열 6/7, 8/9, 10/11을 각각 HII→HI, HeII→HeI, HeIII→HeII의 count/kinetic reward로 채택한다. 각각 저장된 실수 입력이다. kinetic 열은 원래 \(\lambda E\) 형성의 반올림을 포함한다. 새 exact product로 바꾸고 이전 all-time solution을 같은 문제의 해처럼 사용할 수 없다. 기존 `solution_physical18`, `p_H1/r_H1`, `p_HeI/r_HeI`, `p_HeII/r_HeII`는 **수치 근사해**로 재사용한다.

\(w\)는 같은 case의 저장된 source projection에서 `projection[1:]`이며, `projection[0]` 경계 mass는 원 pulse ledger에 별도로 유지한다. 이 mass의 RR reward는 0이다. source를 다시 투영하거나 정규화하지 않는다. 세 z source는 대안이며 시계열이 아니다. 과거 실제 \(Q_e=tA\) source는 다른 100 K bath의 결과이고 현재 10,000 K bath로 이전하지 않는다. [현재 scope와 source 근거](../source_frontier/SOURCE_FEASIBILITY_KO.md)

명시적으로 선택한 proper-time 관측 horizon \(T\)에 대해 저장된 pulse의 응답을 계산한다. \(T\)는 source exposure를 추정한 값이 아니다. arbitrary source history, \(n_b\), physical stopping rate, native instantaneous RHS는 이 정리로 생성되지 않는다.

## 2. 가정과 양의 semigroup

\(K\in\mathbb R^{n\times n}\)는 finite tridiagonal Z-matrix, 즉 두 off-diagonal이 0 이하인 행렬이며 nonsingular M-matrix라고 가정한다. \(w,r\in\mathbb R_{\ge0}^n\)이다. 시간 단위는 proper second이고 \(K\)는 \(s^{-1}\) 단위를 갖는다.

M-matrix의 충분한 실용 certificate는 어떤 \(h>0\), \(\beta>0\)가 있어

\[
Kh\ge\beta h                                                     \tag{1}
\]

가 성분별로 성립하는 것이다. \(D=\operatorname{diag}h\)로 scaling하면 \(D^{-1}KD\)의 각 행에서 diagonal과 off-diagonal 절댓값 합의 차가 \(\beta\) 이상이다. Gershgorin 원판이 \(\Re z\ge\beta>0\)에 들어가므로 \(K\)는 stable하다. 또한 \(-K\)가 Metzler이므로 \(S(t)=e^{-Kt}\ge0\). 충분히 큰 \(c\)에 대해 \(cI-K\ge0\)를 택하면 \(S(t)=e^{-ct}e^{(cI-K)t}\)의 급수에서도 양수성이 직접 보인다.

\(f=Kh-\beta h\ge0\)라 놓으면

\[
 e^{-\beta t}h-S(t)h
 =\int_0^t S(t-s)e^{-\beta s}f\,ds\ge0.                            \tag{2}
\]

따라서 weighted norm \(\|x\|_h=\max_i|x_i|/h_i\)에서

\[
 \|S(t)\|_h\le e^{-\beta t},\qquad
 K^{-1}=\int_0^\infty S(t)\,dt\ge0.                               \tag{3}
\]

역으로 nonsingular M-matrix이면 \(h=K^{-1}{\bf1}>0\)를 선택해 \(\beta=\min_i1/h_i>0\)를 얻을 수 있다. 실제 코드는 이론적으로 존재하는 witness를 새로 구했다고 가정하지 않고, 저장된 positive time vector 등 후보 \(h\)에 대해 (1)을 검증해야 한다.

### Tridiagonal 대안

diagonal \(d_i\), lower \(\ell_i\le0\), upper \(u_i\le0\)에 대해

\[
 p_1=d_1,\qquad p_i=d_i-\ell_{i-1}u_{i-1}/p_{i-1}
\]

가 모두 엄밀히 양수이면 Thomas factorization \(K=LU\)에서 \(L^{-1},U^{-1}\ge0\), 따라서 \(K^{-1}\ge0\)다. 이 판정은 exact 또는 rigorous enclosure로 pivot 부호를 확인했을 때의 결과다. 이전 binary64 pivot의 양수 관측만으로 새 rigorous certificate를 선언하지 않는다. 아래의 정량 오차에는 여전히 witness와 양의 \(\beta\), 또는 동등하게 검토된 inverse bound가 필요하다.

어느 유도에도 \(K{\bf1}\ge0\), 행합 확률 보존, \(P_r\le1\)을 가정하지 않는다. \(w\) 자체가 count density이고 reward도 energy를 포함하므로 무차원 확률 상한 1을 일반적으로 사용할 수 없다.

## 3. Finite-age reward 정리

\[
 k_r(t)=w^\top S(t)r,\qquad
 F_r(T)=\int_0^T k_r(t)\,dt,\qquad
 P_r=w^\top K^{-1}r.                                             \tag{4}
\]

(2)–(3)에 의해 \(k_r(t)\ge0\)이고 적분 가능하다. 그러므로 \(F_r\)는 연속 미분 가능하며 단조 증가하고,

\[
 F_r(0)=0,\qquad 0\le F_r(T)\le P_r,\qquad
 \lim_{T\to\infty}F_r(T)=P_r.                                     \tag{5}
\]

이는 finite nonnegative reward measure의 성질이다. row-substochasticity가 확인되지 않았을 때에도 성립한다. 개별 해의 물리 확률 또는 전체 입자 보존을 주장하려면 그 별도 조건을 확인해야 한다.

\(C_w=w^\top h\)라 하면 유용한 보조 bounds는

\[
 k_r(t)\le C_w\|r\|_h e^{-\beta t},\quad
 P_r\le C_w\|r\|_h/\beta,\quad
 P_r-F_r(T)\le C_w\|r\|_h e^{-\beta T}/\beta.                       \tag{6}
\]

\(r=0\) 또는 \(w=0\)이면 모든 reward가 정확히 0이다. \(T=0\)은 별도의 정확한 endpoint로 처리하며 무한한 \(\gamma\)를 수치적으로 만들지 않는다.

## 4. Erlang-clock의 정확한 resolvent 표현

\(H\sim{\rm Erlang}(m,\gamma)\), \(m\in\mathbb N_{\ge1}\), \(\gamma>0\)를 보조 관측 clock으로 둔다. 실제 source history 또는 입자별 물리 clock을 추가한다는 의미가 아니다. Survival function은

\[
 \Pr(H>t)=e^{-\gamma t}\sum_{j=0}^{m-1}\frac{(\gamma t)^j}{j!}.
\]

비음성에 따른 Tonelli 정리로

\[
\begin{aligned}
 A_m(\gamma)
 &=\mathbb E F_r(H)
 =\int_0^\infty k_r(t)\Pr(H>t)\,dt\\
 &=\sum_{j=0}^{m-1}
   \gamma^j w^\top(K+\gamma I)^{-(j+1)}r .                         \tag{7}
\end{aligned}
\]

마지막 행은 \(\int_0^\infty t^j e^{-Bt}\,dt=j!B^{-(j+1)}\), \(B=K+\gamma I\)에서 온다. \(j=0\)은 stable semigroup 적분이며, 일반 \(j\)는 integration by parts와 귀납법으로 얻는다. 경계항은 (2)의 exponential decay로 사라진다.

계산은

\[
 z_0=B^{-1}r,\quad z_j=\gamma B^{-1}z_{j-1},\quad
 A_m=\sum_{j=0}^{m-1}w^\top z_j                                  \tag{8}
\]

로 수행할 수 있다. \(B^{-1}\ge0\)이므로 exact \(z_j\)와 모든 합의 항이 음이 아니다. 같은 \(B\) factorization을 여러 reward RHS와 source contraction에 재사용한다. 작은 rare reward를 \(P_r\)에서 근접한 값을 빼는 방식으로 계산할 필요가 없다. dense inverse 또는 과거 전체 time campaign이 필요하다는 결론도 나오지 않는다.

## 5. Clock tail과 deterministic horizon의 enclosure

\(0<T<\infty\), \(0<\delta<1\)에 대해

\[
 \gamma_-=\frac{m(1+\delta)}T,\qquad
 \gamma_+=\frac{m(1-\delta)}T                                    \tag{9}
\]

로 정한다. 아래첨자 \(-\)는 평균이 작은 clock, \(+\)는 평균이 큰 clock이다.

\[
 \mathbb EH_-=\frac{T}{1+\delta}<T,\qquad
 \mathbb EH_+=\frac{T}{1-\delta}>T.
\]

### 5.1 Chernoff tail의 유도

\(X=\gamma H\sim{\rm Gamma}(m,1)\)이고 \(\mathbb E e^{sX}=(1-s)^{-m}\), \(s<1\)다. \(a=\gamma T/m>1\)일 때 \(s=1-1/a>0\)를 Chernoff 상한에 넣으면

\[
 \Pr(H>T)\le\exp\{m(\log a+1-a)\}.                                \tag{10}
\]

\(0<a<1\)에서는 같은 \(s=1-1/a<0\)로 lower tail에 Markov inequality를 적용해

\[
 \Pr(H<T)\le\exp\{m(\log a+1-a)\}.                                \tag{11}
\]

따라서 (9)가 정확히 성립할 때

\[
 Q_-=\exp\{m[\log(1+\delta)-\delta]\},\qquad
 Q_+=\exp\{m[\log(1-\delta)+\delta]\}.                              \tag{12}
\]

\(0<\delta<1\)이면 \(0<Q_\pm<1\). \(\gamma\)를 binary64로 반올림한 값을 정확한 입력으로 채택한 경우에는 실제 \(a=\gamma T/m\)를 사용한다. ideal \(\delta\)와 rounded \(\gamma\)를 혼용하지 않는다.

### 5.2 Monotonicity만 사용하는 bracket

\(A_-=\mathbb E F_r(H_-)\), \(A_+=\mathbb E F_r(H_+)\)라 하자. \(F_r\)가 단조 증가하고 \(0\le F_r\le P_r\)이므로

\[
 A_-\le(1-q_-)F_r(T)+q_-P_r,\quad q_-=\Pr(H_->T),
\]
\[
 A_+\ge(1-q_+)F_r(T),\quad q_+=\Pr(H_+<T).
\]

어떤 \(Q_\pm\ge q_\pm\), \(Q_\pm<1\)도 사용할 수 있다. 첫 식의 오른쪽은 \(q_-\)를 늘리면 증가하고, 둘째 식의 유효한 하한은 \(q_+\)를 늘리면 감소한다. 따라서

\[
 \boxed{\;
 \max\!\left(0,\frac{A_- -P_rQ_-}{1-Q_-}\right)
 \le F_r(T)\le
 \min\!\left(P_r,\frac{A_+}{1-Q_+}\right).\;}                       \tag{13}
\]

이 정리는 Erlang 근사가 \(F_r(T)\)와 가깝다는 경험적 가정 없이 성립한다. 폭이 넓으면 넓은 enclosure를 반환해야 하며, 그것을 임의로 좁히지 않는다.

### 5.3 극한과 수렴 조건

고정 \(m,\delta\)에서 \(H_\pm=T X_\pm\)이며 \(X_\pm>0\)는 \(T\)와 무관하다. bounded convergence로 \(T\downarrow0\)이면 \(A_\pm\to0\), \(T\to\infty\)이면 \(A_\pm\to P_r\). (13)의 양 끝도 각각 0과 \(P_r\)로 수렴한다. 이는 exact arithmetic 결과이며 실제 solver certificate 폭의 수렴을 자동 보증하지 않는다.

**고정 \(\delta>0\)에서 \(m\)만 늘리면 bracket은 일반적으로 \(F_r(T)\)로 닫히지 않는다.** clock은 각각 \(T/(1+\delta)\), \(T/(1-\delta)\)로 집중한다. 이 경우 bracket의 극한은 그 두 시간의 reward다.

고정 \(T>0\)에 대해

\[
 \delta_m\to0,\qquad m\delta_m^2\to\infty                          \tag{14}
\]

를 함께 요구하면 clock 평균은 \(T\)로, 분산은 0으로 수렴한다. 또한

\[
 \log(1+\delta)-\delta\le-\frac{\delta^2}{2(1+\delta)},\qquad
 \log(1-\delta)+\delta\le-\frac{\delta^2}{2}
\]

이므로 \(Q_\pm\to0\). 연속이고 bounded인 \(F_r\)에 대해 \(A_\pm\to F_r(T)\), 이어서 (13)의 양 끝이 \(F_r(T)\)로 수렴한다. 예로 \(m>1\)에서 \(\delta_m=m^{-1/4}\)가 조건을 만족한다. 이는 수렴 정리의 예이며 실제 production order 선택이나 추가 run 권한이 아니다.

## 6. Floating-point shifted solves의 검증 가능한 오차

해석적 bracket과 solve 오차는 별도다. 다음 정리는 **잔차가 실제로 rigorously bounded 되었을 때** 적용된다.

\(B=K+\gamma I\), \(\alpha=\beta+\gamma\)라 하자. (1)에 의해 \(Bh\ge\alpha h\)이고,

\[
 B^{-1}h\le h/\alpha,\qquad
 \|B^{-1}\|_h\le1/\alpha .                                       \tag{15}
\]

증명은 \(B(h/\alpha)\ge h\)에 양의 \(B^{-1}\)를 곱하면 된다. 따라서 근사해 \(\widehat x\)의 정확한 잔차 \(\rho=b-B\widehat x\)에 대해

\[
 |x-\widehat x|
 \le B^{-1}|\rho|
 \le \frac{\|\rho\|_h}{\alpha}h.                                 \tag{16}
\]

### 6.1 Recurrence 전체의 누적 오차

실제 저장한 \(\widehat z_j\)에 대해

\[
 \rho_0=r-B\widehat z_0,\qquad
 \rho_j=\gamma\widehat z_{j-1}-B\widehat z_j \quad(j\ge1)
\]

이며 \(\|\rho_j\|_h\le\eta_j\)를 확보했다고 하자. exact error \(e_j=z_j-\widehat z_j\)는

\[
 e_0=B^{-1}\rho_0,\qquad
 e_j=B^{-1}(\gamma e_{j-1}+\rho_j)
\]

를 만족한다. 따라서

\[
 \epsilon_0=\eta_0/\alpha,\qquad
 \epsilon_j=(\gamma\epsilon_{j-1}+\eta_j)/\alpha
 \quad\Longrightarrow\quad |e_j|\le\epsilon_jh .                  \tag{17}
\]

이는 앞 단계 오차를 누락하지 않는 양의 scalar recurrence다. \(\gamma/\alpha<1\)이며, 선택적으로

\[
 \epsilon_j\le
 \frac1\alpha\sum_{k=0}^j
       \left(\frac\gamma\alpha\right)^{j-k}\eta_k
\]

로도 표현할 수 있다. 마지막 solve의 잔차 하나만을 \(A_m\) 전체 오차로 쓰는 것은 허용되지 않는다.

\(\widehat A\)의 dot product와 summation 오차가

\[
 \left|\widehat A-\sum_{j=0}^{m-1}w^\top\widehat z_j\right|
 \le d_{\rm sum}
\]

로 bounded 되어 있으면

\[
 |A_m-\widehat A|
 \le E_A:=C_w\sum_{j=0}^{m-1}\epsilon_j+d_{\rm sum}.                \tag{18}
\]

\(C_w,\eta_j,\epsilon_j,d_{\rm sum}\)의 수치 상한 역시 upward rounding 또는 exact arithmetic으로 확보해야 한다. scalar \(\widehat A\)의 nominal 계산값만 맞는 것으로는 충분하지 않다.

### 6.2 재사용 all-time solution의 certificate

새로 all-time solve를 반복할 필요는 없다. 저장된 근사해 \(\widehat x_\infty\)에 대해

\[
 \rho_\infty=r-K\widehat x_\infty,\qquad
 \eta_\infty\ge\|\rho_\infty\|_h
\]

를 검증하고 \(\widehat P\)의 dot-product error가 \(d_\infty\) 이하이면

\[
 |P_r-\widehat P|
 \le E_P:=C_w\,\eta_\infty/\beta+d_\infty.                         \tag{19}
\]

따라서 \(P^L=\max(0,\widehat P-E_P)\), \(P^U=\widehat P+E_P\)를 outward rounding으로 만들 수 있다. 필요하면 (6)의 독립 상한과 교차할 수 있다. 기존 값이 저장돼 있다는 사실만으로 \(P_r\)가 exact라는 의미는 아니다.

### 6.3 수치 enclosure를 최종 bracket으로 전달

\(A_-^L\le A_-\), \(A_+\le A_+^U\), \(P_r\le P^U\), \(q_\pm\le q_\pm^U<1\)가 검증되면 안전한 endpoint는

\[
 L=\max\!\left(0,\frac{A_-^L-P^Uq_-^U}{1-q_-^U}\right),\qquad
 U=\min\!\left(P^U,\frac{A_+^U}{1-q_+^U}\right).                   \tag{20}
\]

lower는 아래로, upper는 위로 반올림한다. \(A_m\)의 비음성과 \(A_m\le P_r\)를 교차해 certificate를 개선할 수 있다. 서로 모순되는 interval이나 \(L>U\)는 실패로 보고해야 한다.

여기서의 exact shift는 saved \(K\)의 정확한 실수 값에 **선언한 정확한 \(\gamma\)**를 더한 것이다. factorization이 rounded \(\widehat B\)를 사용해도 되지만, 잔차를 \(\widehat B\)가 아닌 \(B\)에 대해 계산해야 한다. RHS의 \(\gamma\widehat z_{j-1}\) 형성 반올림도 그 잔차 안에 포함한다.

통상 floating residual, high-precision agreement 또는 \(\log/\exp\)의 nominal 값은 자동 rigorous bound가 아니다. exact rational evaluation, 검토된 rounding-error inequality 또는 outward interval evaluation이 필요하다. tail이 underflow해 0이 되었다고 \(q=0\)을 선언할 수 없다. 이 조건이 충족되지 않으면 해석적 정리는 유지하되 floating certificate는 unresolved로 기록한다.

## 7. 시간 bin, count·energy·photon 및 부호

같은 \(K,w,r\)에서 \(0\le T_1<T_2\)라 하자.

\[
 \Delta_r=F_r(T_2)-F_r(T_1)\ge0.
\]

각 endpoint가 \([L_i,U_i]\)로 포함되면

\[
 \boxed{\quad
 \max(0,L_2-U_1)\le\Delta_r
 \le\min(P^U,U_2-L_1).\quad}                                     \tag{21}
\]

증명은 두 endpoint inequality의 차와 \(0\le\Delta_r\le P_r\)다. 이론상 upper는 음이 될 수 없으며, 실제 negative upper 또는 lower>upper는 certificate 불일치다. 0으로 덮어 통과시키지 않는다. \(T_1=0\)에는 정확한 \([0,0]\), \(T_2=\infty\)에는 all-time certificate를 사용한다.

각 channel에서 \(N=\Delta_{\rm count}\), \(E=\Delta_{\rm kinetic}\), 기존 threshold \(I\ge0\)를 공통 기저로 사용한다.

| 반환 항 | 동일 기저에 대한 식 | interval |
|---|---|---|
| RR event count | \(N\) | \([N_L,N_U]\) |
| 제거되는 fast-electron kinetic energy | \(-E\) | \([-E_U,-E_L]\) |
| internal-energy 변화 | \(-IN\) | \([-IN_U,-IN_L]\) |
| retained-photon energy | \(E+IN\) | \([E_L+IN_L,E_U+IN_U]\) |

동일한 \(N,E\)에 대해

\[
 -E-IN+(E+IN)=0                                                   \tag{22}
\]

가 정확히 성립한다. 각 interval의 끝점을 독립적으로 임의 선택한 조합이 모두 보존한다는 뜻은 아니다. exporter는 공통 \(N,E\)와 linear map을 유지해 correlation을 보존한다. species event mapping도 동일 \(N\)으로 parent ion −\(N\), daughter ion +\(N\), electron −\(N\)를 적용한다. isotope/threshold는 기존 source-qualified 공급자를 그대로 사용한다.

SI 변환은 한 번만 수행한다.

\[
 N[{\rm m}^{-3}]=10^6N[{\rm cm}^{-3}],\quad
 E[{\rm J\,m}^{-3}]=
 (10^6\times1.602176634\times10^{-19})E[{\rm eV\,cm}^{-3}].          \tag{23}
\]

eV의 SI 정의와 최종 수치 반올림을 구분한다. \(T_2<\infty\)이고 폭이 양수일 때 \(\Delta_r/(T_2-T_1)\)는 **선언한 pulse·time bin의 조건부 평균 반환률**이다. 실제 연속 injection rate, exposure 또는 pointwise instantaneous RHS로 이름을 바꾸지 않는다.

retained photon은 이 event ledger의 photon reservoir다. photon transport, cascade, escape, stopping, 물리 heating 완료를 뜻하지 않는다.

## 8. 실제 외부 source가 공급될 때의 convolution

일반 nonnegative locally integrable source \(b(t)\)가 실제로 주어지면, proper-volume population column은

\[
 n'(t)=-K^\top n(t)+b(t),\qquad
 n(t)=e^{-K^\top t}n_0+
 \int_0^t e^{-K^\top(t-s)}b(s)\,ds.                               \tag{24}
\]

backward reward에서 쓰는 \(K\)와 forward population의 \(K^\top\)를 혼동하지 않는다. \(f_r(u)=\int_0^u e^{-K\tau}r\,d\tau\)라 하면 Tonelli/Fubini와 variation of constants에 의해

\[
 Y_r(T)=n_0^\top f_r(T)+
 \int_0^T b(s)^\top f_r(T-s)\,ds.                                 \tag{25}
\]

finite nonnegative vector measure \(B(ds)\)도 Stieltjes integral로 처리할 수 있으며, 실제 pulse는 이 일반화의 시간 atom이다. RR에는 \(f_r(0)=0\)이므로 \(T\)에서 주입한 source는 그 순간까지 누적 RR에 기여하지 않는다.

zero initial population과 고정 source shape \(b(t)=wq(t)\), \(q(t)\ge0\), 단위 \(s^{-1}\)이면

\[
 Y_r(T)=\int_0^T q(s)F_r(T-s)\,ds.                                \tag{26}
\]

세 scalar saved-pulse kernels는 각각의 shape 또는 명시적 shape 선형결합에 대한 arbitrary **시간 profile**을 연결한다. arbitrary energy-time source \(b_i(t)\) 전체를 이미 계산한 것은 아니다. 그 경우 vector kernel \(f_r\), source-energy mapping, 실제 history와 적분 오차를 별도로 제공해야 한다.

현재 source history, clock Jacobian, donor/recipient normalization은 없으므로 (25)–(26)의 실제 physical 숫자를 생성하지 않는다. 서로 다른 z snapshot으로 시간 차를 추론하지 않는다. 과거 실제 \(Q_e=tA\) 100 K 결과를 같은 bath의 증거로 사용하는 것도 허용되지 않는다.

## 9. 코딩 연구 루프의 명시적 의무

기계 계약 [FORMULA_CONTRACT.json](FORMULA_CONTRACT.json)에 식, 부호, 단위, exact input 기준 및 certificate 의무를 정리했다. C 단계에서는 먼저 선택 case·horizon·\(m,\delta\)·비용·attempt를 동결해야 한다. 이 R5 문서는 새 실행 예산을 정하지 않는다.

필수 판정은 exact stored input identity, Z/sign/shape, M-matrix witness 또는 엄밀 pivot, 실제 shift와 tail의 일치, recurrence 이전 오차 전파, all-time upper bound, q의 상향 bound, scalar accumulation 및 최종 outward rounding이다. analytic exact-K 결과와 numerical certificate와 물리/model/grid 오차를 별도 필드로 둔다. sparse shifted solve의 실제 성능과 certificate 폭은 실행 후의 증거로만 판정한다.

기존 source·H1/HeI/HeIII RR·C23E·M0/M1/M2 결과를 재사용한다. 과거 UNKNOWN_NO_ACK와 예산, N6/N7 predecessor gate, global physical completion/error null, isotope mapping 및 provider 유효 범위는 유지한다. 본 정리로 DAG 완료 수 또는 physical heating 완료를 바꾸지 않는다.

## 10. 기존 근거와 문헌의 역할

현재 exact K·reward·source pin의 근거는 이전 [동결 계약](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/FROZEN_CONTRACT.md)과 engine, 저장 NPZ다. 일반 source convolution 및 quadratic/curvature closure는 [M0](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_m0_quadratic_20261012/README_KO.md)와 [M1–M3](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_rux_m1_m3_20261012/REPORT_KO.md)의 기존 근거를 재사용한다.

R1/R2에서 실제로 읽은 primary 문헌은 Bladt et al. (2002)의 [CTMC reward transform](https://www-id.imag.fr/Laboratoire/Membres/Sbeity_Ihab/Sure-Paths/publi_general/BMNS-MAM4.pdf), de Souza e Silva et al. (2013)의 [Erlang random-time sparse/banded transient method](https://pubsonline.informs.org/doi/abs/10.1287/ijoc.1120.0537), Bladt et al. (2019)의 [inhomogeneous Markov reward matrix formulation](https://arxiv.org/abs/1905.04605)이다. 정확한 열람 범위는 source evidence에 남아 있다. 반복 검색은 수행하지 않았다.

이 문헌은 방법의 일반 맥락을 제공한다. 식 (1)–(26), 현재 stored \(K\)에 대한 결속과 certificate 의무는 이 문서에서 직접 유도했다. 문헌이 현재 CR source 또는 물리 heating을 인증했다는 주장이나 방법의 신규성 주장은 하지 않는다.

