# HeIII ground RR: shared competition, stable response and integrated return

## 1. 선택한 source와 수치 문제

He4III + e_fast(E) → He4II(1s) + γ 한 채널을 고정된 이전 H1+HeI
tagged-electron 사슬에 더한다. Native Verner HeII PI row는 I=54.42 eV,
Emax=50000 eV이며 g_bound=2, g_ion=1, d=2g_ion/g_bound=1이다.
입력은 원소 He의 전자 단면적을 He4에 조건부 귀속한 모형이다. 이전과 같은
stationary-heavy-target, zero-recoil, nonrelativistic scalar spontaneous ground
성분을 사용한다. Source와 문헌 위치는 intake/R2_SOURCE_QUALIFICATION_KO.md다.

에너지를 일관된 물리 단위로 넣으면

\[
\sigma_3(E)=\sigma_{\rm PI}(E+I)\frac{(E+I)^2}{d m_ec^2E},\qquad
\lambda_3(E)=n_{\rm HeIII}\sqrt{\frac{2E}{m_e}}\sigma_3(E).
\]

코드의 eV/cm 단위에서는 M=m_ec²/eV_J, v_cm_s=100√(2E_eV eV_J/m_e)다.
n_HeIII=.01 cm⁻³를 한 번 곱한다. Thermal ne=.14 cm⁻³는 이 hazard의
target가 아니다. E>0 및 E+I≤50000 eV를 확인하며 rate floor를 넣지 않는다.

K0는 PR106에 저장된 HeI 결과의 binary64 tridiagonal matrix를 **정확한
수치 피연산자**로 정의한 것이다. 과거 H1/HeI의 intended-real-sum은 별도
역사적 문제다. 새 D=diag(λ3)와 실수합 K1=K0+D가 이번 intended operator다.
Binary64 K1을 만들 때의 새 addition loss는 따로 측정한다. 모든 H1, HeI,
HeII, CE, first-entry와 bath reward가 같은 K1을 사용한다.

## 2. 양의 resolvent와 경쟁

가정: K0는 유한 차원의 nonsingular M-matrix이며 off-diagonal≤0이다.
각 λ3≥0이고 관측하는 reward/시간은 유한하다. K1도 nonsingular M-matrix다.
G0=K0⁻¹, G1=K1⁻¹는 entrywise 비음성이며 resolvent identity에서

\[
G_0-G_1=G_0DG_1=G_1DG_0\ge0.
\]

그러므로 비음성 기존 terminal reward b에 대해 h0=G0b, h1=G1b는
h1≤h0이고

\[
\delta h=h_1-h_0=-G_1Dh_0.
\]

CE probability, H1 capture probability, HeI capture probability 및 mean time
(b=1)에 각각 적용된다. Conditional energy/time은 두 moment의 비이므로
이 부등식만으로 그 비의 증가/감소를 단정하지 않는다.

M-matrix 조건은 이전 저장 사슬의 채택 범위다. 구현은 finite sign/pivot 및
새 solve residual을 점검한다. Roundoff가 있는 저장 행렬의 행합을 물리적
killing rate와 기호적으로 같다고 가정하지 않으며 아래 defect식을 쓴다.

## 3. 단일 추가 채널의 양쪽 bound

\[
p=G_1\lambda_3,\qquad w=G_0\lambda_3,\qquad\eta=\max_i w_i.
\]

G1≤G0에서 p≤w다. K1w=λ3+Dw이고, Dw≤ηλ3이므로
K1w≤(1+η)λ3다. G1≥0를 곱하면 w≤(1+η)p가 된다. 따라서

\[
\boxed{\frac{w}{1+\eta}\le p\le w.}
\]

비음성 initial measure μ를 곱해 source-weighted bound를 얻는다.
이전 K0에 이미 여러 채널이 있어도 새 D가 하나이므로 이 명제가 적용된다.
새로 여러 종의 D를 동시에 넣을 때 개별 종마다 같은 multiplicative lower
bound를 쓰는 주장은 이 증명에서 나오지 않는다. 과거 반례는 재사용한다.

또한 h0≥0이면

\[
0\le-\delta h=G_1Dh_0\le\|h_0\|_\infty p.
\]

따라서 새 capture 확률이 기존 비음성 reward 변화의 자연스러운 크기
척도다. 이 해석은 새 채널이 매우 드물어도 두 큰 수를 빼지 않고 유지된다.

## 4. 저장된 이전 해와 잔차의 정확한 관계

저장 열을 hhat0라 쓰고 r0=b−K0 hhat0로 둔다. 새로 계산할 안정 응답은
δhat=−G1 D hhat0라는 고정 RHS의 문제다. 직접 대수로

\[
h_1-\widehat h_0=G_1r_0+\widehat\delta h,
\]
\[
\widehat\delta h-\delta h^*=G_1DG_0r_0,
\qquad\delta h^*=-G_1DG_0b.
\]

첫 식은 직접 subtraction에 baseline residual이 섞이는 이유를 보인다.
두 번째 식은 안정 응답 자체가 이상적 이전 해의 변화와 다른 양을 준다.
따라서 δhat의 독립 own-column 검증과 과거 hhat0의 정확도를 구별한다.

선택적으로 양의 저장 시간 벡터 that0에 대해 m=min(K0 that0)>0가 확인되면
K0(that0/m)≥1이므로 G0·1≤that0/m이다. 비음성 행렬의 infinity norm을 써서

\[
\|G_0r_0\|_\infty\le
\frac{\|\widehat t_0\|_\infty}{m}\|r_0\|_\infty=:\epsilon_0,
\]
\[
|\widehat\delta h-\delta h^*|\le p\epsilon_0.
\]

이것은 유한 저장 문제의 정확한 수학적 추정이다. 수치 평가의 정밀도와
조건 m>0를 따로 확인해야 하며, 이 식만 적어 전역 물리 오차 인증을 주장하지
않는다. 이번 main observable는 이름에 stored-column response임을 명시한다.

## 5. 확률·시간·에너지 reward

각 terminal channel j의 hazard b_j에 대해 p_j=G1b_j다. 순간 kinetic reward가
b_j E이면 r_j=G1(b_j E)다. Finite killed-chain representation이 성립할 때

\[
p_j=\int_0^\infty e^{-K_1t}b_j\,dt,\quad
v_j=\int_0^\infty t e^{-K_1t}b_j\,dt=G_1p_j.
\]

Source μ에서 conditional capture energy는 μᵀr_j/(μᵀp_j), conditional time은
μᵀv_j/(μᵀp_j)다. 분모가 0이면 conditional quantity는 null이다.
Mean stopping time은 G1·1이다. 실제 physical18의 열은 0–5=first6, 6–7=H1 count/kinetic,
8–9=HeI count/kinetic, 10–11=새 HeIII capture count/kinetic, 12–17=bath6다.
따라서 6+2+2+2+6=18이며 새 λ3와 λ3E만 두 열로 삽입한다. Conditional5, stable4와 w1을 더해 28 RHS/case다.

이전 terminal sum b_old에 대해 저장 matrix의 closure defect를
ρ0=K0·1−b_old로 정의한다. 그러면 새 partition은 정확히

\[
G_1(b_{\rm old}+\lambda_3)-\boldsymbol1=-G_1\rho_0.
\]

따라서 이론의 exact ideal partition과 저장 연산자의 numerical partition을
구별하며 기존 maxabs≤2e−8 검사를 유지한다.

Energy-weighted total old RHS를 b_E,old, stored energy vector를 E라 하고
e_E=K0E−b_E,old로 정의한다. 새 capture의 전체 final reward는 λ3E이므로

\[
K_1E-(b_{E,old}+\lambda_3E)=e_E,
\]
\[
G_1(b_{E,old}+\lambda_3E)-E=-G_1e_E.
\]

개별 event의 signed energy는 −E (fast), −I (internal), E+I (retained photon)다.
Final stopped-energy sum에는 photon+internal=r이 들어간다. Fast removal −r은
그 final sum의 추가 reservoir가 아닌 event-transfer diagnostic이다.
H1/HeI/새 HeII는 각각 13.60/24.59/54.42 eV를 별도로 사용한다.

## 6. 저장 source의 적분 관측량

각 z의 원 pulse atoms는 W와 count density m을 가진다. PR104에 저장된
projection p와 active mask를 그대로 재사용한다. p[0]는 active source 중
바로 cutoff boundary에 놓인 질량이며 capture 시간은 0이다. μ=p[1:]로 두고
Nactive=sum(m[mask]), Nselected=sum(m)로 각각 정규화한다.

\[
N_3=\mu^Tp,\quad U_{e,3}=\mu^Tr,\quad
U_{\gamma,3}=U_{e,3}+I N_3,\quad U_{ion,3}=-I N_3.
\]

N3는 cm⁻³, U들은 eV cm⁻³다. SI로 N3×10⁶, U×10⁶ eV_J를 적용한다.
선택 source 전체 energy account에는 처음부터 inactive인 kinetic energy,
boundary energy Ecut(p[0]+μᵀp_entry), CE outgoing/internal, bath6 및 세 RR
channel의 photon/internal을 포함한다. Source 재투영·재적분은 하지 않는다.

이 값은 pulse 종료까지의 적분 결과다. Exposure와 time-history가 제공되지
않았으므로 source rate, event rate, effective seconds는 null이다. 평균
capture 시간이나 평균 stopping 시간을 exposure로 대신 쓰지 않는다.

## 7. integrated event와 native25 사상

선택 사건의 exact species column은 He4:2 −1, He4:1 +1, e:fast −1,
photon +1이다. Native heavy basis에서는 ν=e11−e12이며 A11=A12=4,
q11=1, q12=2다. N3^SI=10⁶ N3 [m⁻³], Ue,3^SI=10⁶ eV_J Ue,3 및 Uγ,3^SI=10⁶ eV_J Uγ,3 [J m⁻³]를 명시한다. 고정된 nb [m⁻³]를 공급할 때 a=N3^SI/nb로 놓으면

\[
\Delta Y=a\nu,\quad\Delta\zeta=-a,\quad
\Delta x_{e,th}=q^T\Delta Y-\Delta\zeta=0,
\]
\[
\Delta\chi_{th}=(\boldsymbol1+q)^T\Delta Y-\Delta\zeta=0.
\]

여기서 ζ는 total free electron의 nonthermal subset이다. 이를 charge-derived
electron count에 다시 더하지 않는다. Density를 제공하지 않으면 adapter는
density-space delta와 integrated energy만 반환하고 per-baryon projection은
null로 둔다. Frozen CR bath와 최신 PW19 donor의 nb,T를 합치지 않는다.

Native Z=(Y[21],ζ,w_nt,w_ext,logT)의 w_ext는 signed external photon transfer다.
기존 의미를 보존하는 integrated return은

\[
\Delta Z=(a\nu,-a,-U_{e,3}^{SI}/n_b,0,0)
\]

와 별도 retained-photon count N3^SI/nb 및 energy Uγ,3^SI/nb port다. Internal energy는
native ionization-energy vector와 ΔY가 이미 소유한다. 같은 binding energy를
별도 state에 또 넣지 않는다. Closed-box RR의 Δw_ext를 양수로 바꾸어 escape를
숨기지 않는다. 이 사건의 thermal source energy와 thermal count 변화는 0이다.
전체 heating/assimilation/cascade/feedback 상태는 기존 미완료 범위를 유지한다.

만일 후속 실제 rate R가 제공되면 r=R/nb이고 같은 column에 r를 곱한다.
Finite extent는 a=∫r dt다. 현재 integrated count를 Event.extent_m3_s에 직접
넣지 않는다. Conditional mean E=Ue/N3를 대표 event energy로 쓸 때 그것은
두 moment를 보존하는 표기이며 monoenergetic photon spectrum 주장이 아니다.

## 8. 검증 대상과 남은 구현

독립 이론 검토는 source/statistical factor, M-matrix 전제, single-hazard bound,
stored-residual identity, conditional moments, energy ownership 및 integrated/rate
구분을 확인한다. R7은 R4의 유리수 예제와 species/energy identity를 CAS로 검산한다.
C5–C9에서는 8개 case의 224 새 RHS, 24 source rows, grid/domain 비교,
두 finest case의 Decimal70 56 RHS와 독립 계수, integrated export를 실행한다.
Independent denominator는 각 열 자체 infinity norm이며 큰 time/energy 열로
작은 capture 확률의 오차를 가리지 않는다. Scientific global error bound는 null.

이 단위는 기존 식의 새로운 source-qualified consumer와 보존적 적분 반환을
구성한다. 새로운 불가능성 정리나 strong no-go를 제안하지 않는다.
