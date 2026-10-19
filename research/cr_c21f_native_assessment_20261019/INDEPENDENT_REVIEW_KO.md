# C21F 신규 native 실행의 독립 수치·물리 검토

검토일: 2026-10-19. 검토 대상은 PR82의 기존 NCP 원자료와 C21F 실행 소스다.
원래 C21F 구현·복구·게시를 재실행하거나 수정하지 않았다.

## 1. 결론과 근거 상태

**두 고정 fixture에서 native 비광이온화 H/He RHS를 호출한 실행이 완료되었고, FULLMID의 시간 2차 수렴과 BE의 시간 1차 수렴을 지지하는 새 원자료가 있다.**
native-source fixture에서 MIDPHOTO_ENDMICRO에 나타난 2보다 큰 유한 해상도 차수는 thermal 오차의 부호 상쇄와 최대오차 성분 전환으로 설명된다. 같은 해상도의 MIDPHOTO_ENDMICRO−FULLMID 차이에는 이미 1차 성분이 직접 보인다.

- **implementation-verified / executed:** 공개 PreparedAbsorption.evaluate 경로의 bridge가 실제 컴파일되었고 Rust bridge 검사 3개와 native 행렬 2개가 완료되었다. 이 검토에서는 저장된 build·실행 로그를 읽었으며 새 Rust 실행을 하지 않았다.
- **numerically checked:** 원래 두 행렬의 SUMMARY, fixture, Radau를 직접 읽어 signed component error와 두 방법의 차이를 다시 계산했다. 두 fixture 각각의 byte hash 및 content digest를 확인했다. 기존 56개 검사 및 native 행렬은 반복하지 않았다.
- **derived:** 아래 전제에서 frozen reaction substep의 MIDPHOTO_ENDMICRO−FULLMID 차이는
  \[
  \delta g=\frac{h^2}{2}D_gM(g_0)\,[P_g(N_0,g_0)+M(g_0)]+O(h^3)
  \]
  이다. 이 leading defect는 일반적인 고정구간 오차에 1차 항을 만든다.
- **unresolved:** native Radau 기준해의 상태 오차 상한과 tolerance 민감도는 이번 두 reference만으로 정량적으로 확정되지 않는다. 특히 common-IC FULLMID의 약 \(10^{-12}\) 차이에 대해 reference 오차와 roundoff·비선형 해법 오차를 분리하는 후속 검사가 필요하다.
- **채택 범위:** 고정 GL2 birth, 고정 스펙트럼과 opacity, 지정 초기조건, 짧은 FLRW 구간에서의 native event coupling 및 시간 정련. Full48, source-age, spectral, angular, Case B, Bianchi, full EoR는 기존 HOLD를 유지한다.

이 결과는 해당 방법의 일관성·오차 진단이다. 새 불가능성 정리나 신규성 주장을 도입하지 않는다.

## 2. 읽은 자료와 identity

| 항목 | 확인한 identity |
|---|---|
| 실행 소스 | bass_cr@f8359232df8d0dd4fe91fcdabeb6701eb06089ba |
| PR81 문서·영수증 기준 | 249d9b29b0adc5a8cf615a9999065aff26ff6900 |
| 신규 실행 원자료 | PR82@c4a502e0c931a201edfa3c7046f7a91230c2278f |
| 원자료 디렉터리 | research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z/ |
| native owner | rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4 |
| 실행 binary SHA256 | 1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40 |
| common_ic fixture canonical SHA256 | befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65 |
| common_ic fixture.json raw-byte SHA256 | bcfb3d5a8b4d5c8153247712eb1c3d127c4410e2455f6106bf60720642d0f060 |
| native_source fixture canonical SHA256 | c562971cf0fcab251fc96b7634f5e7aefab87377652a98be3ba4256a23a9d781 |
| native_source fixture.json raw-byte SHA256 | fb33c66c9d26009ceb4d593b221481c0743320e4c657365971910b8294ef986e |

독립 검토자가 직접 GitHub에서 취득한 SUMMARY.json, fixture.json, radau.json 각 2개, 총 6개에 대해 Git blob SHA를 재계산하여 일치시켰다. fixture의 canonical JSON SHA256도 SUMMARY와 Radau의 fixture_sha256과 각각 일치했다. 이 검토의 현재 Python 실행 probe는 PYTHON_PASS, Python 3.12.14였다.

실행 경로의 주요 소스는 [event_coupler.py][S1], [run_experiment.py][S2], [reference_tau.py][S3], [native_point.rs][S4]다. native_micro.py도 읽어 native handshake, 실제 binary SHA 기록, EOS·밀도 대응, photo 및 expansion 입력의 0 검사, microphysical 수지 검사를 확인했다. 이 문서의 source reading은 kernel·연속식·이산화의 대응에 대한 검토이며, upstream rate fit 전부의 새로운 문헌 검증을 뜻하지 않는다.

## 3. 두 실행의 물리·수치 범위

두 fixture는 \(a_0=0.09\), \(\Delta\ln a=10^{-4}\),
\[
g_0=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w)
=(0.2,0.15,0.01,1.4229641197648433\ {\rm eV/H})
\]
를 사용한다. \(T_0=8500\ {\rm K}\), \(Y=n_{\rm He}/n_{\rm H}=0.08130135170951498\)이다.

| fixture | photo opacity | spectrum·birth | native 부분 |
|---|---:|---|---|
| common_ic | 원 cross section의 0.001배 | 3개의 초기 cohort와 2회 GL2 birth의 각 3개 에너지, 총 9 cohorts | 원 native 비광이온화 H/He RHS |
| native_source | 원 opacity 1배 | 3개 초기 cohort와 원 MD14 12-cell centroid spectrum의 2회 GL2 birth, 총 27 cohorts | 같은 native RHS와 native source export |

두 fixture는 spectrum과 opacity가 함께 다르다. 두 출력의 차이를 단일 source 변경의 효과로 분해하지 않는다. native source 실행도 전체 48-source나 source-age 정련을 포함하지 않는다. 초기 photon inventory는 \(0.032/{\rm H}\), 새 GL2 birth는 약 \(5.98038736618\times10^{-5}/{\rm H}\)로 고정되어 있다.

native_source reference의 최대 누적 광학깊이는 \(81.3554849707788\), 최저 양의 최종 cohort는 \(6.514631281313118\times10^{-38}/{\rm H}\)다. common_ic의 최대 광학깊이는 \(0.08366082770907855\)다. 두 reference에서 underflowed_positive_cohorts는 0이며, min_internal_optical_depth와 min_accepted_optical_depth는 0이다. 이 수치는 이번 finite fixture에서 관측한 결과다.[S5][S6]

## 4. 연속식과 구현의 대응

\(x=\ln a\), proper time \(t\), \(dt/dx=H^{-1}\)를 사용한다.
cohort \(i\)의 물리 에너지는 \(E_i(x)=q_i e^{-x}\)이며,
\[
k_{ij}(x)=s_\kappa\,c\,n_{{\rm H},0}e^{-3x}\sigma_j(E_i),\qquad
\alpha(g)=\bigl(1-x_{\rm HII},\;Y(1-x_{\rm HeII}-x_{\rm HeIII}),\;Yx_{\rm HeII}\bigr).
\]
여기서 \(s_\kappa\)는 fixture의 opacity_scale이다. \(k\alpha\)는 초당 반응률, \(c\)는 실제 광속이고 자연단위계를 도입하지 않았다.

active cohort에 대해
\[
\lambda_i=\sum_j k_{ij}\alpha_j,\qquad
\frac{dN_i}{dx}=-\frac{\lambda_i}{H}N_i,\qquad
\frac{d\tau_i}{dx}=\frac{\lambda_i}{H},\qquad
N_i=A_i e^{-\tau_i}.
\]
\(A_i\)는 birth 때 주어진 photon amount이다. \(\tau_i\)는 무차원이며, inactive cohort는 구조적 0이다. \(\tau\) 변환은 동일 연속식의 좌표 변환이다.

species event rate \(S_j=\sum_iN_i k_{ij}\alpha_j\)에 대해
\[
\frac{dg_{\rm frac}}{dx}
=\frac{\mathcal A_Y(S)+M_{\rm frac}(g)}{H},\qquad
\frac{dw}{dx}
=\frac{\sum_{ij}N_i k_{ij}\alpha_j(E_i-B_j)+M_w(g)}{H}-2w,
\]
\[
\mathcal A_Y(S)=\left(S_{\rm H},\frac{S_{\rm HeI}-S_{\rm HeII}}Y,
\frac{S_{\rm HeII}}Y\right),\qquad Y>0.
\]
사용한 두 fixture는 \(Y>0\)이다. \(Y=0\)에서는 별도의 구조적 0 처리와 고정 unknown 제거가 이미 C21F에 있다.

native_point.rs의 igm_point_rhs 호출은 photo input와 native Hubble input을 0으로 준다. expansion은 run_history의 geometry 연산과 reference의 \(-2w\) 항이 소유한다. native_micro.py는 native가 반환한 photo 및 expansion 항이 0인지 검사한다. 따라서 이번 경로에는 확인된 소스 수준에서 expansion이나 photo의 중복 소유가 없다.[S1][S2][S3][S4]

### 수지와 정확도의 구별

단위는 fraction, photon/H, eV/H를 구별한다. 소스·redshift work·gas expansion work·escaped cooling·CMB 교환·binding energy를 포함한 ledger로 물리 수지를 검사했다.

| 관측량 | common_ic 12 histories 최대 절댓값 | native_source 12 histories 최대 절댓값 |
|---|---:|---:|
| photon number defect /H | \(6.288372600415926\times10^{-17}\) | \(2.0816681711721685\times10^{-17}\) |
| energy defect eV/H | \(3.7015972698031113\times10^{-13}\) | \(9.602868596603111\times10^{-14}\) |
| species ledger defect | \(1.3587872146891833\times10^{-14}\) | \(2.4591439995447217\times10^{-14}\) |

reference의 number/energy defect는 common_ic에서 \(-8.456776945386935\times10^{-18}/{\rm H}\), \(-2.759159003704048\times10^{-16}\ {\rm eV/H}\), native_source에서 \(8.060913048169027\times10^{-14}/{\rm H}\), \(-1.3574138490210323\times10^{-12}\ {\rm eV/H}\)다.[S5][S6][S7][S8]

이 수지는 solver가 실제로 검사하는 bookkeeping identity의 잔차다. 같은 invariant를 유지하는 두 다른 궤적도 존재할 수 있으므로 수지 잔차를 state error의 상한으로 쓰지 않았다. 시간 오차는 별도로 reference와 정련을 통해 평가한다.

## 5. 새 원자료가 보여 주는 시간 수렴

정규화는
\[
\epsilon_n=\max\left(
|\delta x_{\rm HII}|,\;|\delta x_{\rm HeII}|,\;|\delta x_{\rm HeIII}|,
\frac{|\delta w|}{w_0}
\right)
\]
이고, \(n\)은 각 event interval의 subdivision 수이다.

| fixture·방법 | \(\epsilon_{64}\) | \(8\to16,\;16\to32,\;32\to64\) 관측 차수 |
|---|---:|---|
| common_ic BE | \(3.1801391550678737\times10^{-7}\) | 0.997572, 0.998784, 0.999391 |
| common_ic FULLMID | \(9.779259503009374\times10^{-13}\) | 1.995165, 1.992416, 1.961803 |
| common_ic MIDPHOTO_ENDMICRO | \(5.296865612112254\times10^{-9}\) | 0.999008, 0.999510, 0.999777 |
| native_source BE | \(1.836918575224062\times10^{-4}\) | 1.025830, 1.015109, 1.008191 |
| native_source FULLMID | \(7.674564930555562\times10^{-7}\) | 1.896310, 1.970812, 1.992460 |
| native_source MIDPHOTO_ENDMICRO | \(2.881076631155999\times10^{-7}\) | 2.136570, 2.652475, 2.241934 |

FULLMID는 두 fixture에서 기대되는 2차 정련 경향을 보인다. native_source의 마지막 FULLMID thermal 오차는 \(1.092063053098613\times10^{-6}\ {\rm eV/H}\), temperature 오차는 \(0.006360917011988931\ {\rm K}\)다.

native_source에서 hybrid가 \(n=64\)의 최대오차 기준으로 더 작게 보이는 원인은 다음 signed 분석으로 해소된다.

### Signed cancellation과 최대오차 성분 전환

\(e_w^{\rm H}=w_{\rm MIDPHOTO\_ENDMICRO}-w_{\rm Radau}\),
\(d_w=w_{\rm MIDPHOTO\_ENDMICRO}-w_{\rm FULLMID}\)로 정의한다.

| \(n\) | \(e_w^{\rm H}\) eV/H | \(d_w\) eV/H | \(n\,d_w\) eV/H | hybrid 최대오차 성분 |
|---:|---:|---:|---:|---|
| 8 | \(+5.361474715859238\times10^{-5}\) | \(-9.795235125231727\times10^{-6}\) | \(-7.836188100185382\times10^{-5}\) | thermal |
| 16 | \(+1.21930600605058\times10^{-5}\) | \(-4.840733176969536\times10^{-6}\) | \(-7.745173083151258\times10^{-5}\) | thermal |
| 32 | \(+1.9392700445486355\times10^{-6}\) | \(-2.406211845995543\times10^{-6}\) | \(-7.699877907185737\times10^{-5}\) | thermal |
| 64 | \(-1.0751923973373323\times10^{-7}\) | \(-1.1995822928323463\times10^{-6}\) | \(-7.677326674127016\times10^{-5}\) | HeII |

\(d_w\)의 reference-free 관측 차수는
\[
1.0168545489,\quad1.0084619097,\quad1.0042315331
\]
이다. 여기서는 Radau reference 자체가 차분에서 완전히 소거된다.
\(n\,d_w\)가 약한 변화만 보이고, FULLMID의 양의 \(O(n^{-2})\) thermal 오차와 hybrid의 음의 \(O(n^{-1})\) 성분이 상쇄된다. \(n=64\)에서는 thermal 오차가 부호를 바꾸며, norm의 지배 성분도 HeII로 바뀐다.

common_ic에서도 같은 차분의 차수는
\[
1.0000339665,\quad1.0000237107,\quad1.0000294051
\]
이다. 따라서 이 진단은 native_source의 특정 norm만 보고 내린 추측보다 강하다. 두 fixture의 signed 결과와 실제 method 차이를 함께 사용한다.[S7][S8]

## 6. Frozen reaction substep의 local defect 유도

### 전제와 표기

한 smooth reaction cell에서 geometry·clock·cross section을 substep의 midpoint 값으로 고정한다. proper step 길이를 \(h>0\), 초기 상태를 \(z_0=(N_0,g_0)\)로 쓴다.

\[
\dot z=F(z)=P(z)+\widehat M(z),\qquad
\widehat M(N,g)=(0,M(g)).
\]
\(P=(P_N,P_g)\)는 photo 반응이고, \(P_N=-\Lambda(g)N\),
\(\Lambda={\rm diag}(\lambda_i)\)이다.
\(G_g=P_g+M\)로 둔다.

전제는 해당 solution과 implicit stage가 smooth physical domain 안에 있고, \(P,M\)에 필요한 도함수가 존재·유계이며, 비선형 방정식을 local truncation 비교에 필요한 정밀도로 풀었다는 것이다. state의 성분별 단위가 다르지만 \(D_gM\)는 해당 물리적 성분 사이의 Jacobian으로 해석하므로 아래 식은 성분별로 차원이 맞는다.

### Photo update의 2차 전개

두 방법 모두 \(\bar g=(g_0+g_1)/2\)에서 photo absorber를 계산한다.
photo event의 합은
\[
N_{1,i}=N_{0,i}\exp[-h\lambda_i(\bar g)],
\]
\[
Q_j=\sum_iN_{0,i}
\frac{k_{ij}\alpha_j(\bar g)}{\lambda_i(\bar g)}
\left[1-\exp(-h\lambda_i(\bar g))\right]
\]
로 주어진다. \(\lambda_i=0\)에서는 연속 극한으로 처리한다. 이 사건량을 stoichiometry와 heat weights에 적용하여 gas photo increment를 얻는다.

두 방법 모두 일관성으로
\[
g_1-g_0=hG_g(z_0)+O(h^2),\qquad
\bar g-g_0=\frac h2G_g(z_0)+O(h^2)
\]
를 만족한다. 따라서 exponential을 전개하면
\[
\Delta z_{\rm photo}
=hP(z_0)+\frac{h^2}{2}D P(z_0)F(z_0)+O(h^3).
\]
이때 \(DP\,F\)의 \(N\)-미분 항은 exponential depletion의
\(-\lambda h^2/2\) 항에서, \(g\)-미분 항은 midpoint absorber 변화에서 각각 발생한다. photo RHS를 gas midpoint에서 평가했다는 말만으로 이 전개를 대체하지 않고, depletion와 gas feedback을 둘 다 포함한 것이다.

### Midpoint micro와 endpoint micro의 차이

FULLMID는
\[
hM(\bar g)=hM(g_0)
+\frac{h^2}{2}D_gM(g_0)G_g(z_0)+O(h^3)
\]
를 사용한다. 따라서
\[
z_{1,\rm FULL}=z_0+hF(z_0)
+\frac{h^2}{2}DF(z_0)F(z_0)+O(h^3),
\]
즉 frozen autonomous reaction ODE의 2차 Taylor 항과 일치한다.

MIDPHOTO_ENDMICRO는
\[
hM(g_1)=hM(g_0)
+h^2D_gM(g_0)G_g(z_0)+O(h^3)
\]
를 사용한다. 두 implicit 해의 차이가 photo midpoint에도 되먹임되지만, 이미 \(\delta g_1=O(h^2)\)이므로 그 추가 차이는 \(h\,D_gP\,\delta g_1/2=O(h^3)\)이다. 따라서 같은 초기값·같은 frozen coefficients에서
\[
g_{1,\rm HYB}-g_{1,\rm FULL}
=\frac{h^2}{2}D_gM(g_0)\,[P_g(z_0)+M(g_0)]+O(h^3).
\]
차이의 leading 항은 gas에 나타난다. photon에 대한 feedback은 이 한 step 비교에서는 \(O(h^3)\)부터 들어간다.

부호는 HYB−FULL로 정했다. 위 식 자체는 항상 양수 또는 음수라는 뜻을 갖지 않는다. 저장된 native trajectory에서 thermal 성분은 음으로 관측되었다.

### Geometry와 event boundary까지의 적용 범위

run_history는 각 interval의 midpoint 전후에 geometry half-step을 적용하고,
proper \(h=\int dx/H(x)\)를 GL4로 구하며,
opacity와 native epoch를 midpoint에서 평가한다. smooth cell에서는 이 symmetric geometry 배치와 midpoint time 평가의 leading local defect는 \(O(h^3)\)다. 따라서 위 hybrid의 \(O(h^2)\) micro defect를 제거하지 않는다.

breakpoints는 source birth와 fit cutoff의 crossing을 분리한다. jump를 가로지르는 단일 smooth Taylor 전개는 사용하지 않는다. source birth를 정확한 event boundary에 두고 각 smooth interval을 정련할 때, 유한한 event 수와 해당 interval별 bounded stability를 전제로 local \(O(h^3)\)는 global \(O(h^2)\), 일반적인 nonzero local \(O(h^2)\) leading term은 global \(O(h)\)를 준다.

보다 정확히 hybrid의 fixed-interval leading global error는 variational propagator로 운반된
\[
\frac12\sum_j h_j^2
\Phi(T,t_j)\,
\begin{pmatrix}
0\\ D_gM(g(t_j))\,G_g(z(t_j))
\end{pmatrix}
\]
의 leading 항으로 표현된다. 각 interval의 subdivision 수를 \(n\)배 늘리는 family에서는 이 합이 통상 \(O(n^{-1})\)다. 계수의 퇴화·상쇄, 특정 observable에서의 소거, 특수한 rate field에서는 leading 항이 사라질 수 있다. 그러므로 유한한 4개 해상도에서 읽은 norm 차수로 모든 조건의 차수를 확정하지 않는다.

이번 derived 식과 두 fixture의 reference-free difference는 서로 일치한다. 안정성이 나빠지는 별도 stiffness 극한까지 균일한 차수나 오차 상수를 주장하지 않는다.

## 7. 남은 reference 정확도 의무와 최소 후속 작업

기존 optical-depth Radau는 rtol \(2\times10^{-10}\), atol \(2\times10^{-13}\)를 사용했다. \(\tau\)와 \(N\)에서 같은 scalar tolerance는 같은 physical-error criterion을 뜻하지 않는다. 이 tolerance 숫자를 그대로 global state error 상한으로 해석하지 않았다.

고정된 birth amount \(A\)에서 두 optical-depth 값의 차이를 \(\delta\tau\)라 하면
\[
|\widetilde N-N|
=N|e^{-\delta\tau}-1|
\le N e^{|\delta\tau|}|\delta\tau|,
\qquad \delta\log N=-\delta\tau.
\]
따라서 후속 tolerance 비교는 재구성된 photon/H의 절대 차이와 log-survivor 차이를 함께 기록할 수 있다. 이는 두 상태 사이의 정확한 변환식이며, solver가 지정 tolerance 이하의 global \(\delta\tau\)를 보장한다는 추가 명제는 포함하지 않는다.

common_ic FULLMID의 reference-free thermal self-convergence는
\[
1.9960867828,\quad2.0028395023
\]
이고, \(n=32,64\)에 2차 Richardson를 가정한 최종 thermal error estimate는
\(1.3430738003232061\times10^{-12}\ {\rm eV/H}\)다.
해당 extrapolate와 Radau의 차이는
\(4.8405723873656825\times10^{-14}\ {\rm eV/H}\)다.
이는 작은 reference discrepancy와 양립하지만, 두 해상도의 truncation remainder도 포함하므로 엄밀한 reference-error enclosure로 채택하지 않는다.

native_source에서 같은 self-convergence는
\(1.8698841941,\;1.9634716090\), Richardson estimate는
\(1.0844729458151885\times10^{-6}\ {\rm eV/H}\), extrapolate−Radau는
\(7.590107431454385\times10^{-9}\ {\rm eV/H}\)다. 아직 finite-step higher-order remainder와 reference 오차를 분리해야 한다.

가장 작은 승인 범위의 후속 작업은 이미 저장된 원자료를 사용한 signed·reference-free 분석을 현재 상태/DAG에 반영하는 것이다. 이는 본 검토에서 수행했다. 새 numerical execution을 진행할 때는 원 fixture와 source를 그대로 유지하면서:

1. 기존 native binary 또는 exact source로부터의 동일 owner build를 사용해 **reference만** rtol/atol ladder로 비교하고, common physical state·photon·ledger 차이를 기록한다.
2. native_source hybrid의 cancellation 이후를 관측할 필요가 있으면 \(n=128,256\)의 **새** resolution만 실행한다. 기존 \(8,16,32,64\)는 재실행하지 않는다.
3. 새 결과마다 fixture/source/binary/raw identity, solver return status, 수지, reference 민감도, observed convergence를 별도로 기록한다.

reference-control 검증은 세밀한 오차 수치의 신뢰도를 높이는 작업이다. 이미 관측된 native completion이나 scoped ledger closure를 다시 미실행 상태로 되돌리지 않는다.

## 8. 현재 판정

PR82의 실행 evidence를 채택하여 C21F native compilation과 두 고정 fixture 실행을 completed로 갱신하는 것이 타당하다. 코드 수준에서 새 수정이 필요한 관측 실패는 이번 범위에서 찾지 못했다. MIDPHOTO_ENDMICRO는 comparator로 유지하고, FULLMID의 fixed-fixture 시간 2차 성질을 후속 기준으로 삼는다.

이번 검토의 completed는 source reading, immutable raw 재계산, signed cancellation 진단 및 local-defect 유도까지다. backup byte inventory와 remote PR 게시 상태의 최종 확정은 별도의 provenance 검토에서 실제 영수증에 연결한다.

[S1]: https://github.com/cosmosapjw-quantum/bass_cr/blob/f8359232df8d0dd4fe91fcdabeb6701eb06089ba/research/cr_c21e_event_native_20261018/src/event_coupler.py
[S2]: https://github.com/cosmosapjw-quantum/bass_cr/blob/f8359232df8d0dd4fe91fcdabeb6701eb06089ba/research/cr_c21e_event_native_20261018/src/run_experiment.py
[S3]: https://github.com/cosmosapjw-quantum/bass_cr/blob/f8359232df8d0dd4fe91fcdabeb6701eb06089ba/research/cr_c21e_event_native_20261018/src/reference_tau.py
[S4]: https://github.com/cosmosapjw-quantum/bass_cr/blob/f8359232df8d0dd4fe91fcdabeb6701eb06089ba/research/cr_c21e_event_native_20261018/native/native_point.rs
[S5]: https://github.com/cosmosapjw-quantum/bass_cr/blob/c4a502e0c931a201edfa3c7046f7a91230c2278f/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z/common_ic/radau.json
[S6]: https://github.com/cosmosapjw-quantum/bass_cr/blob/c4a502e0c931a201edfa3c7046f7a91230c2278f/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z/native_source/radau.json
[S7]: https://github.com/cosmosapjw-quantum/bass_cr/blob/c4a502e0c931a201edfa3c7046f7a91230c2278f/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z/common_ic/SUMMARY.json
[S8]: https://github.com/cosmosapjw-quantum/bass_cr/blob/c4a502e0c931a201edfa3c7046f7a91230c2278f/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z/native_source/SUMMARY.json

## 9. CROSS_REVIEW — 새 후처리 코드와 저장 결과

**판정: PASS_SCOPED.** 범위는 신규 후처리의 핵심 수치식, identity 및 해석 gate, 기록된 결과와의 일치다. 아래 동결본의 코드를 실제로 읽고 파일 SHA256를 재계산했다. 원래 56 tests와 native 행렬을 재실행하지 않았다.

| 검토 대상 | SHA256 |
|---|---|
| analyze_native_evidence.py v3 | b07aa7ca28d03e6cfc785df11d2a004ff3b0517eb86624842b4aa9a43cd7a075 |
| results_v3/ASSESSMENT.json | 8e92cebc44a4edff8b2f9c21963ffc2e5312d89054a64f6c5285f0f148793725 |
| audit_native_points.py | e4dce851e5a48c33988bc01b355753673c7e0f7df3ea4b860832aac511cd9f20 |
| native_point_audit_run01/POINT_AUDIT.json | 7bc9ab669daa63644e237fc3d7eadda4b57bf971ba761ec09b373c4f525160cc |
| validation_v3/VALIDATION_RECEIPT.json | 45d0f0f5e43fc49596fe8a9d31f81509de03d20a368a61470869e9111d097340 |

검토한 v3 결과는 24 histories, 2 references, 2160 accepted steps를 포함한다. 선택한 input 126개 중 원 실행 manifest 항목과 비교한 raw input은 108개다. manifest의 전체 168 payload를 이 analyzer 하나가 모두 검증했다고 해석하지 않는다. 별도 point audit는 26개 파일의 27140 requests/responses를 검사했고, 26개 파일 모두 result/reference의 native call counter와 일치한다. 두 후처리의 확인 범위가 서로 다르므로 단순 합계를 새 과학 실행 수로 사용하지 않는다.

### 재구성 가능한 잔차와 에너지 수지의 범위

v3는 reaction 초기 열 scale을
\[
x_{\rm mid}=0.5(x_{\rm lo}+x_{\rm hi}),\qquad
w_{\rm reaction,0}=w_{\rm prev}\exp[-2(x_{\rm mid}-x_{\rm lo})]
\]
로 복원한다. 이는 terminal gas가 아니라 첫 geometry half-step 직후의 \(w\)이고, 원 실행 코드의 midpoint 반올림 순서까지 따른다.

검토자는 2160개 row의 **저장 residual vector**에 대해 이 normalization을 별도로 계산했다. 모든 row가 원래 \(\mathrm{nonlinear\_tol}=2\times10^{-13}\)를 그대로 만족하며, 최대값은 \(2.3592410188651465\times10^{-14}\)다. 원래 equation residual의 모든 항을 row만으로 다시 계산했다는 주장은 하지 않는다. row에 없는 native micro ledger를 만들어내지 않았다.

이전 후처리의 nonlinear_tol*(1+1e-12)는 원 tolerance를 그대로 사용하는 비교로 교정했다. exp[-(hi-lo)]는 수학적으로 동등하지만, 실행 반올림 순서의 추적성을 위해 위 midpoint 식으로 교정했다. 이 수정으로 변한 normalized residual의 최대 차이는 \(3.1554436208840472\times10^{-30}\)였고 모든 원자료 판정은 유지되었다. 원 solver의 tolerance와 과학 소스에는 변경이 없다.

accepted-step 자료로 확인한 것은 시간 grid, terminal gas domain, aggregate photon domain, 저장 residual norm, photon-number stock의 변화 및 누적 photo event와 원자료 대응이다. 각 row의 full nonphoto energy ledger와 per-cohort photon vector가 없으므로 다음 제한은 코드와 결과에 그대로 명시되어 있다.

- individual_step_energy_reconstruction: UNAVAILABLE_FROM_ACCEPTED_LOG.
- per_cohort_accepted_step_domain: NOT_RECORDED.
- internal_trial_state_domain: NOT_ASSESSED_FROM_ACCEPTED_STEPS.

최종 total-H·binding·thermal·radiation ledger의 독립 재합산은 그 실제 기록 범위에서 수행되었다. 저장된 per-step energy_defect의 최대값이 result와 같다는 검사는 원래 개별 step의 energy budget을 완전히 재구성한 검사와 구별된다.

### Point audit의 원 acceptance 보존

NativeMicro/MicroRates의 원 수치와 scalar 비교 의미를 직접 대조했다. density/EOS/fraction 비교는 \(a_{\rm tol}+r_{\rm tol}|{\rm expected}|\), binding의 math.isclose는 최대값 규칙, energy identity는 원래 fsum 기반 budget을 사용한다. arbitrary tolerance 완화가 없다.

검토자는 보고된 최대 budget 위치 중 density, EOS, HeII stoichiometry, binding, energy의 5개 원시 행을 각각 다시 읽고 독립 계산했다. 보고된 위치·절대 잔차·budget·비율이 모두 정확히 일치했다. 최대 budget 사용 비율은 해당 항목 순서로
\(5.206382385659353\times10^{-3}\),
\(1.9420017787462884\times10^{-3}\),
\(1.808290719244188\times10^{-5}\),
\(2.8889308935296\times10^{-5}\),
\(1.0015319766980056\times10^{-5}\)다.

binary hash는 process metadata·manifest·build receipt의 대응으로 취급하고, binary bytes의 독립 재취득과 구별한 제한도 확인했다. 모든 pointwise 수지 검사와 별도로, atomic rate의 외부 자료 정확도 및 reference global error의 calibration 의무를 유지한다.

### 부적합한 crossing fit의 처리

native_source의 4개 해상도 전체에 \(A/n+B/n^2\)를 맞춘 hybrid−Radau fit은 \(n=64\)에서 양의 thermal 오차 \(+1.6500191923414488\times10^{-7}\)를 예측한다. 실제 값은 \(-1.0751923973373323\times10^{-7}\ {\rm eV/H}\)다. fit의 형식적 crossing \(n=77.71675693227098\)도 관측 부호전환 구간 \([32,64]\) 밖이다.

따라서 이 fit은 **INADEQUATE_FOR_CROSSING_PREDICTION**으로 처리했다. v3의 fitted_sign_mismatch_levels는 [64], observed_sign_change_brackets는 [[32,64]], certified_crossing_prediction은 null이다. 모든 미실행 grid의 fit 값은 NOT_ADMISSIBLE_AS_PREDICTION으로 표시한다. 이 값들은 부적합성을 기록한 진단이며 다음 해상도의 과학 결과·crossing 근거로 사용하지 않는다.

실제로 채택한 cancellation 근거는 부호가 보존된 raw endpoint, max-error 성분 전환, reference를 소거한 \(d_n\), 제6절의 local defect 유도다. Richardson 또는 reference-free difference를 reference accuracy floor의 증명으로 사용하는 gate는 없다.

### 실제 검증 로그와 종료

validation_v3의 정확한 argv·exit code·stdout/stderr를 읽었다. 신규 analyzer 검사 5개는 PASS, exit 0이며, 후처리 실행은 exit 0이다. 시험 대상은 source/digest 구분, 누락·오염 evidence 거절, SUMMARY와 underlying result 대응, signed cancellation 해석, create-only output 보존이다. 이들은 이전 56개 과학·프로토콜 검사와 별개의 새 후처리 검사다.

교정 후 동결 코드·결과의 SHA256, 원 residual gate, crossing 부적합 판정, 모든 미실행 extrapolation의 제한을 별도 짧은 Python 검사로 확인했다. 새 지적이 해결된 뒤 추가 광범위 검사를 반복하지 않고 이 교차검토를 종료했다.
