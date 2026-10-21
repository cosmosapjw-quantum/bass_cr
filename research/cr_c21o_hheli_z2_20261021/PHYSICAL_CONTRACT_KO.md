# C21O: z=20→2 조건부 H/He/Li–LRS pilot의 물리 계약

## 목표와 기존 결과의 보존

새 문제는 고정 REI `3b85dedce84d37b3e165da00685a8a984950aafe`의
non-tilted LRS Einstein–Vlasov/광자/무질량 neutrino 모멘트에 원시 원자
전하 반응과 전자밀도–Thomson 연결을 추가한다. C21L의 81개, C21M/N의
기존 독립응력 계산과 NCP 반환은 재실행하거나 provenance를 변경하지 않는다.
부모 문서 head는 `8dc5031b3323d4be42a7444843294200aa8887f2`다.

사용자는 이번에 물리 범위와 끝점을 확장하고 샌드박스 안에서 끝까지 실행하도록
명시했다. 따라서 과거 collisionless-only/HOLD는 과거 결과의 해석 범위로 보존하고,
새 source·새 입력·새 run ID에서 이 모델을 수행한다. 이전 DOP853 결과를 BDF
결과로 대체하지 않는다. 새 stiff charge system은 FP64 BDF와 analytic Jacobian,
`rtol=3e-11`, scaled-state `atol=3e-13`을 사용하며, FLRW Radau 비교를 별도 보존한다.

## 추적하는 물질과 반응

원자 charge states 20개에 자유 중성자 1개를 더해 21개 population을 추적한다.
자유전자는 대수적으로 계산하며 별도의 22번째 ODE가 아니다.

| 핵종 | 추적 전하 q | 초기 핵종 수 / H_ref | 상태 |
|---|---|---:|---|
| n | 0 | 0 | 명시된 후기 초기조건; beta adapter 존재 |
| H1 | 0,1 | 1 | 초기 이온분율 2e-4 |
| D | 0,1 | 2.5e-5 | 초기 이온분율 2e-4 |
| T | 0,1 | 0 | 명시된 후기 초기조건; beta adapter 존재 |
| He3 | 0,1,2 | 1e-5 | 초기 neutral |
| He4 | 0,1,2 | 0.082 | 초기 neutral |
| Li7 | 0,1,2,3 | 5e-10 | 초기 LiII |
| Li6 | 0,1,2,3 | 1e-14 | 초기 LiII |

이 수치는 재현 가능한 **illustrative prior**이며 BBN 계산이나 관측 적합 결과가 아니다.
z=15.9의 다른 초기조건 파일을 z=20으로 옮기지 않았다. 원소별 electronic rate를
isotope에 공유하는 명시적 근사를 사용하며 reduced-mass isotope shift를 풀지 않는다.
질량 밀도의 환산은 `mass ≈ A m_u`다. 정확한 isotope atomic mass, 결합질량 보정,
분자·음이온·Be7·Li8/9·다른 단명 핵종은 이 registry에 포함되지 않는다.

실제 동작하는 전자 반응은 인접 전하 상태 사이 ground-state valence
photoionization과 all-level spontaneous radiative recombination이다. 재결합 광자가
탈출하는 optically thin Case-A closure를 사용한다. H/He/Li의 원 Verner
photo/RR 계수와 R9 Python Provider를 byte 그대로 재사용한다. LiI는 2s valence
channel이며 64.39 eV 이상에서 원 PH1 outer-shell branch를 쓴다. Core/Auger,
CI, DR, charge exchange, secondary electron ionization, multilevel atoms는
`UNMODELED`다. 이를 0인 측정 반응률로 표현하지 않는다.

중성자 decay는 n→H⁺+e⁻, tritium은 T(q)→He3(q+1)+e⁻로 매핑한다.
선택한 역사적 상수는 mean neutron lifetime 877.75 s와 tritium half-life
12.33 Julian yr이다. 두 parent의 실제 초기량은 0이다. 비영 parent를 넣는
회귀 검사는 전하·핵자 보존 검사이며 decay heating의 cosmological 검증이 아니다.

## 실제로 입력하는 UV와 온도

광자 cohort 에너지는 10,20,40,60,100,150 eV다. 각 cohort의 방향 적분 number
flux는 `F_j=c n_gamma,j` [cm⁻² s⁻¹]이며 `Gamma_i=sum_j F_j sigma_i(E_j)`다.
등방 외부 UV를 가정한다. Soft/hard weights는 manifest에 수치 그대로 기록한다.

\[
f_s(z)=\frac{1+\tanh(8-z)}2,\qquad
f_h(z)=\frac{1+\tanh[(3.2-z)/0.35]}2,
\]
\[
T(z)=8[(1+z)/21]^2+10^4f_s(z)+5000f_h(z)\;{\rm K}.
\]

Soft 완전 on에서 HI의 광이온화율은 1e-13 s⁻¹, hard 완전 on은 추가
2e-14 s⁻¹이 되도록 정규화한다. 이 입력은 관측 UVB, stellar emissivity 또는
thermal-energy equation의 해가 아니다. 실제 온도는 원 RR fit의 3 K–1e9 K
범위 안에서 평가하며 floor나 보간을 적용하지 않는다.

이 UV support는 MeV photonuclear threshold보다 낮다. 따라서 선택된 photon
field로 첨부의 핵광분해 경로를 여는 rate는 threshold 때문에 0이다. 이 사실을
thermal fusion·핵충돌 반응망 전체가 구현됐다는 주장으로 확대하지 않는다.
전체 19개 반응의 활성 핵반응 모델은 별도의 rate·spectrum·energy 계약이 필요하다.

## 전하 반응망에서 LRS 모멘트까지

\(Y_i=n_i/n_{H,ref}\), \(Y=D x\), \(D=\mathrm{diag}(s_i)\)라 둔다.
Li처럼 작은 총량은 isotope scale을 분리해 O(1) fraction으로 적분한다.
이는 물리 abundance를 clipping하거나 normalization으로 보정하는 방법이 아니다.

\[
n_{H,ref}(a)=\frac{\Omega_b\rho_{c,0}}{m_u B_{ref}}a^{-3},\quad
B_{ref}=\sum_i A_iY_i(0),\quad n_e=n_{H,ref}\,q^TY.
\]

위 식에서 \(\rho_{c,0}\)는 질량밀도이며 코드의 J/m³ 값은 먼저 \(c^2\)로 나눈다.
코드 API의 number density는 proper cm⁻³다. 고정된 reference H 수는 beta로
생성되는 실제 H 총량과 구별된다. 핵자 보존은 \(A^TY\)로 검사한다.

\[
\frac{dx}{d\eta}=\frac{D^{-1}}{H}
\{(P+B)Y+n_{H,ref}(q^TY)RY\},\qquad \eta=\ln(a/a_0).
\]

\(P\)는 photo, \(R\)은 recombination coefficient, \(B\)는 beta operator다.
고정 H에서 정확한 원자 Jacobian은

\[
J_x=\frac{D^{-1}}H
\{P+B+n_eR+n_{H,ref}(RY)q^T\}D.
\]

마지막 rank-one 항은 모든 이온의 electron response를 포함한다.
Geometry에 대한 교차 미분에는 \(-x'\partial H/H\)가 추가된다.
전체 62-state Jacobian에는 photon opacity의 charge derivative도 포함된다.

원 40성분의 Thomson coefficient와 모멘트 방정식을 그대로 사용한다.
\(\Gamma_T=c\sigma_T n_e\)는 photon에만 작용하고 neutrino는 collisionless다.
Chemistry→electron→photon quadrupole→shear/energy→H→chemistry의 연결을 실제로
적분한다. Atomic gas의 anisotropic stress는 **등방 gas 가정**으로 0이고,
nonbaryonic massive Vlasov의 stress는 계속 동적으로 계산한다. Baryon rest mass는
기존 dust에 이미 포함돼 있으므로 다시 Einstein 밀도에 더하지 않는다.

## 정확한 stress 정규화

Orthonormal LRS tensors는
\[
\sigma_{\hat i\hat j}=\operatorname{diag}(-s,-s,2s),\quad
\pi^X_{\hat i\hat j}=\operatorname{diag}(-p_X,-p_X,2p_X),\quad
\Delta p_X=3p_X.
\]
그러므로 full Frobenius norm은 \(\sqrt6|s|\), \(\sqrt6|p_X|\)다.
Source half-contraction보다 \(\sqrt2\) 크다. SI pressure [J/m³]와 proper-time
\(H_t\) [s⁻¹]를 쓰는 코드에서는
\[
S_F=\sqrt6s/H_t,\quad
P_X=\sqrt6(8\pi G/c^2)p_X/H_t^2.
\]
이는 \(\kappa_E=8\pi G/c^4\), \(H_{geom}=H_t/c\)를 쓰는 정의와 같다.
Scalar norms는 \(\Sigma=|S_F|\), \(\Pi_X=|P_X|\)다.
\(P_r=P_\gamma+P_\nu\), \(P_{tot}=P_m+P_r\)를 먼저 더한 뒤 norm을 취한다.
두 sector norm을 직접 더하지 않는다. Tensor diagonals, signed amplitudes,
full/half norms, cancellation fraction을 raw에 모두 보존한다.

## Trace-energy 한계와 검증 약속

Gas thermal·ionization energy와 prescribed UV energy는 기존 Einstein source에
추가하지 않고 각각 계산해 기록한다. 순간 상태를 고정한 positive-energy 추가에 대해
\[
\epsilon=\frac{u_{th}+u_{ion}+u_{UV}}{3c^2H_t^2/(8\pi G)},\qquad
\frac{H_{added}-H}{H}=\sqrt{1+\epsilon}-1\le\epsilon/2
\]
를 진단한다. 이는 missing-reaction effect나 장시간 trajectory error의 상계가 아니다.
별도로 200 eV/baryon diagnostic도 보존한다. `global_error_bound=null`이다.

45개 격자는 signed S0 = -0.6,-0.3,0,0.3,0.6,
Pm0 = -5e-4,0,5e-4, Pr0 = -1.2e-3,0,1.2e-3이다.
각 A 변경에서 massive distribution과 energy normalization을 재생성한다.
출력 시간은 z20→2의 eta 균등 201개다. 별도 6개 계산은 FLRW Radau,
두 extreme L12, Thomson-off, 두 exact-initial-cancellation 사례다.
원 L8 결과를 L12로 덮어쓰지 않으며 둘의 차이를 직접 표시한다.

이 모델은 **선언된 반응 집합과 외부 입력 아래의 조건부 21-population LRS pilot**다.
모든 원시 핵반응·isotope chemistry·self-consistent stellar/UV/thermal feedback을
포함하는 최종 재이온화 예측은 이번 계산과 구분된 미완료 DAG다.
