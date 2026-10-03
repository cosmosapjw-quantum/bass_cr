# R4AJ: selected-1s 선택자와 공진 부분공간의 bridge 판별

2026-10-03. 이 문서의 새 결과는 선택자 의미·저장 행렬의 정확 산술·조건부 유한차원 bridge 판별이다. 실제 연속 원자 operator, 산란궤도 또는 재이온화 source의 승인을 뜻하지 않는다. R4AI와 원래 G01–G13의 claim ceiling을 유지한다.

## 1. 서로 다른 선택자는 서로 다른 관측량이다

회수한 candidate metadata는 5개 radial mode, 한 중심 9개 s+p 채널이다. 원 배열은 target 9개, projectile 9개의 순서다. `principal_n=1,l=m=0`을 만족하는 projectile 채널은 full index 9이고, 음의 energy label을 가진 projectile 채널은 9,10,12,13,14다. 에너지 label은 고유값 enclosure가 아니며, 이 검색을 통해 production selector를 설치하지 않는다.

과거 reference의 projectile 음의 에너지 부분공간은 rank 5, 이번 측정 목적의 projectile 1s는 rank 1이다. 공통 Hilbert 공간에 놓인 두 유한 rank 직교 projector P,Q에서 rank P<rank Q이면 Ran Q∩Ker P에 단위벡터 x가 존재한다. 따라서 (P−Q)x=−x이고 ||P−Q||≥1이다. 직교 projector 차이의 norm은 1 이하이므로

\[
\boxed{\|P_{1s}-P_{\rm negative}\|_2=1.}
\]

이 명제는 각각의 projector가 어떻게 회전했는지와 무관하다. 같은 reference의 같은 상태라는 전제도 관측량의 rank 차이를 지우지 못한다. 과거 rank-5 selector mapping의 작은 certificate를 rank-1 관측량에 복사할 수 없다. 같은 rank끼리라면 이 정보만으로 거리를 정할 수 없으므로 코드가 `None`을 반환한다.

## 2. 저장된 한 중심 (H0,S)에서의 정확한 gap 판별

입력은 R4AB의 `INTRINSIC.npz`에 저장된 실수 대칭 9×9 S,H0다. 각 binary64 수를 정확한 이진 유리수로 해석한다. 새 적분이나 예전 시험을 하지 않았다. 이 단계의 수학적 대상은 **저장된 유한 행렬쌍**이다. 저장값과 연속 candidate 적분 사이 오차는 포함하지 않는다.

다음 충분조건을 정확 유리수로 검사했다.

\[
S\succeq s_* I>0,\qquad
\mu=H_{00}/S_{00}\le\alpha=-499/1000\ E_h,
\]
\[
(H_0-\beta S)|_{x_0=0}\succeq0,\qquad\beta=-126/1000\ E_h.
\]

S의 양의 Gershgorin 하한과 제한행렬의 양의 diagonal-dominance 여유를 사용했다. Courant–Fischer 정리에 따라 λ1≤μ≤α, λ2≥β이므로

\[
\boxed{\lambda_2-\lambda_1\ge373/1000\ E_h.}
\]

λ2 하한에서 x0=0은 codimension-one 부분공간이다. S-직교 보완이라고 가정할 필요는 없다. 정확 LDL 분해를 이용한 다른 구성의 검토도 각각 양의 pivot을 확인했다.

기저 vector e0와 저장행렬의 고유 ground projector 사이의 사상 오차도 구별한다. q=S^(1/2)e0/√S00, y=(H0−μS)e0이면

\[
\|(S^{-1/2}H_0S^{-1/2}-\mu)q\|^2
=\frac{y^\dagger S^{-1}y}{S_{00}}
\le\frac{\|y\|_2^2}{s_*S_{00}}=:r_*^2.
\]

rest spectrum≥β>μ이므로

\[
\|P_q-P_{\rm ground}\|_2
\le\frac{r_*}{\beta-\mu}
\le4.488\times10^{-15}.
\]

마지막 표시는 위쪽 반올림이며 exact bound는 RESULT.json의 유리수다. 이 작은 값은 rank-1 label에서 같은 저장행렬 rank-1 ground로의 오차다. 위 rank-5 대 rank-1의 거리 1과 모순되지 않는다. 원자 operator·quadrature·physical basis 오차가 포함됐다고 읽으면 안 된다.

## 3. 두 중심 공진은 한 중심 gap과 별개다

동일한 두 isolated internal-energy operator의 직합을 reference로 놓으면 ground eigenvalue가 정확히 두 번 나타난다. 따라서 projectile ground 한 상태와 full complement 사이의 reference gap은 0이다. 같은 원자 내부의 1s–나머지 gap이 양수라는 사실로 target 1s를 제거할 수 없다.

반면 두 ground를 함께 retained cluster로 묶으면 이 **직합 reference**의 pair-to-rest gap은 적어도 373/1000 Eh다. 이 판별은 finite-separation interacting Hamiltonian의 gap이 정확히 0이라는 주장이 아니다. 해당 gap은 coupling, diagonal perturbation, whitening/embedding, frame 연결항을 통제해야 별도로 계산할 수 있다.

설계 결정은 `dynamic cluster={T1s,P1s}`와 `measurement=P1s`를 분리하는 것이다. 두 상태를 함께 진화시키되 측정량을 cluster 전체 population으로 바꾸지 않는다. 현재 선택자는 raw 1s span이고, isolated spectral pair로의 mapping도 입력 모델마다 증명해야 한다.

중심이 겹쳐 기저가 비직교이면 두 rank-1 projector를 더한 것이 pair projector가 아니다. S>0이고 coefficient selector J_R를 쓰는 경우 orthonormal 좌표에서

\[
P_R=M J_R(J_R^\dagger S J_R)^{-1}J_R^\dagger M^\dagger,
\qquad M^\dagger M=S.
\]

코드의 작은 행렬 참조 구현은 Cholesky S=LL†, M=L†를 사용한다. 잘못된 S를 Hermitian으로 투영하거나 종속 selector를 몰래 정규화하지 않는다. 이 floating 함수는 projector diagnostic이지 interval certificate가 아니다.

## 4. ETF의 큰 위상을 임의의 gap으로 사용하면 안 된다

현재 식 iħSċ=(H−iħD)c에 대해 d=Mc, M†M=S로 바꾸면

\[
i\hbar\dot d=h d,
\quad h=M^{-\dagger}(H-i\hbar D)M^{-1}
+i\hbar\dot M M^{-1}.
\]

Γ=Ṡ−D−D†+(i/ħ)(H†−H)이면

\[
h-h^\dagger=-i\hbar M^{-\dagger}\Gamma M^{-1}.
\]

따라서 unitary block theorem에는 Γ=0인 정확 reference가 필요하며 실제 수치 Γ는 별도 metric/state 오차로 남긴다. h를 강제 Hermitian화하지 않는다. 추가 unitary frame W에서는 h가 W†hW−iħW†Wdot으로 변하므로 빠른 carrier 위상을 넣어 생긴 대각 energy를 물리 phase-gap이라고 읽을 수 없다.

기존 conforming same-center 식에서
H=H0+V+(iħ/2)[(v·A)†−v·A]+m_e v²S/2,
D=−v·A−i m_e v²S/(2ħ)이므로
H−iħD=H0+V+(iħ/2)[(v·A)†+v·A]다. 정확 A가 skew일 때 boost의 겉보기 m_e v²/2 energy는 소거된다. 현재 수치 A의 결함은 이 항등식의 정확 만족으로 덮어쓰지 않는다. 이 계산은 phase-amplitude 분해에서 connection과 진폭 도함수를 누락하면 가짜 비공진성 판정이 생긴다는 이유를 보여준다.

## 5. 공진을 유지한 조건부 block-action 상계

가정은 고정 orthonormal chart에 있는 C1 Hermitian 유한행렬, Γ=0, 모든 frame connection이 포함된 generator다. retained R과 complement Q에 대해

\[
h=\begin{pmatrix}H_R&B^\dagger\\B&H_Q\end{pmatrix},
\quad h_{\rm bd}=\operatorname{diag}(H_R,H_Q).
\]

R 내부의 T1s/P1s coupling을 H_R에서 제거하지 않는다. 전 구간 길이 T에 대해 두 block의 spectrum이 순서대로 분리돼

\[
\inf\operatorname{spec}H_Q-\sup\operatorname{spec}H_R\ge\gamma>0
\]

이며 B0≥sup||B||, B1≥sup||Bdot||, L≥sup(||Hdot_Q−cdot I||+||Hdot_R−cdot I||)가 실제 연속 상계라고 가정한다. interlaced spectra의 pairwise gap만으로 이 operator-norm 상수를 적용하지 않는다.

Sylvester 식 H_Q X−XH_R=B는 순서 gap 아래 semigroup 적분으로 풀리며

\[
\|X\|\le B_0/\gamma,
\quad \|\dot X\|\le B_1/\gamma+L B_0/\gamma^2.
\]

공통 scalar c는 식에서 정확히 소거된다. reference propagator U_Q,U_R에 대해

\[
\frac{d}{dt}(U_Q^\dagger XU_R)
=U_Q^\dagger(\dot X+iB/\hbar)U_R.
\]

따라서 임의 prefix interval의 interaction-picture coupling primitive는

\[
\left\|\int U_Q^\dagger B U_R\,dt/\hbar\right\|
\le\mathcal A:=\frac{2B_0}{\gamma}
+T\left(\frac{B_1}{\gamma}+\frac{LB_0}{\gamma^2}\right).
\]

V_I=U_bd†(h−h_bd)U_bd/ħ, F(t)=∫V_I라 하고 interaction propagator U_I를 사용하면
∫V_I U_I=F U_I−∫F Udot_I다. Udot_I=−i V_I U_I와 unitary norm을 이용해

\[
\boxed{\|U-U_{\rm bd}\|
\le\min\{2,\; TB_0/\hbar,\;\mathcal A(1+TB_0/\hbar)\}.}
\]

T=0에서는 정확히0이다. B0/gamma와 A, TB0/ħ 모두 무차원이다. B1 단위는 energy/time, L도 energy/time이다. 이 식은 진폭뿐 아니라 도함수·phase/gap 조건이 필요한 이유를 명시한다. Burgarth 등의 integral-action 논문은 이 접근의 문헌 근거지만, 위 특수화는 여기서 유도했다. 그 논문을 현 원자 입력의 수치 인증으로 취급하지 않는다.

**이 상계는 제거공간과의 동역학 차이이지 retained 공진공간 내부의 실제 1s transfer를 제한하지 않는다.** 정규화된 공통 초기상태와 공통 projector의 population 차이는 2||U−Ubd|| 이하이나, reference의 P1s 변화는 따로 더해야 한다.

고정 2상태 측정기저에서 internal offdiagonal κ(t)를 포함한 H_R에 대해 ||i[H_R,P1s]||=|κ|이므로

\[
|P_{1s}^{\rm bd}(b)-P_{1s}^{\rm bd}(a)|
\le\min\{1,\hbar^{-1}\int_a^b|\kappa(t)|dt\}.
\]

끝점에서 P1s=0이라고 가정하지 않는다. measurement가 움직이면 그 도함수 또는 고정화 frame connection이 추가된다. 처음부터 Q 성분이 있는 상태의 embedding도 별도로 통제해야 한다.

## 6. 독립 반례성 fixture와 실제 판정

새 합성 3×3 예제에서 H_R=[[0,1/4],[1/4,0]] Eh, H_Q=2 Eh, B=(1/1000,0)Eh, T=6ta, ħ=Eh ta를 쓴다. 외부 gap은7/4 Eh이다. exact bound는 ||U−Ubd||≤503/437500≈0.0011497143이다. 실제 floating difference는 약0.00075059944, 70자리 독립 계산의 P1s는0.9949959261779935...이다.

즉 제거공간의 영향이 작아도 retained pair 내부 transfer가 거의1일 수 있다. 이 새로운 fixture는 누출 오차를 전체 bridge 오차로 잘못 읽는 것을 막는 판별 예다. 실제 원자값이라고 사용하지 않는다.

실제 BASS bridge에 필요한 gamma(t), B/Bdot/L, internal κ/그 적분, 초기상태, 연속 S/H/D/whitening 오차, selector/embedding 차이는 이번에 확보하지 않았다. 따라서 physical bridge upper는 null이며 옛 504.54 raw bound와5e-6 per-side 목표를 변경하지 않는다. 한 점의 stored spectral gap으로 그 구간을 닫지 않는다.

## 7. 종료와 다음 작업

이 노드는 rank 불일치와 reference 공진을 판별하고, exact 저장행렬 gap 및 조건부 block-bound 코드를 완성했다. 다음 local node는 `LOCAL_RESONANT_PAIR_WEAK_BRIDGE_ENVELOPE`다. 동일한 candidate의 weak-H/frame 연결을 포함한 pair 내부 κ와 Q 결합을 연속 interval 형태로 공급하는 경로를 설계·구현한다. actual gap이 부족하면 retained cluster를 필요한 만큼만 확대하는 별도 계약이 필요하다. 무조건 모든 bound state 출력으로 목적을 바꾸지 않는다.

외부 node는 여전히 R4AH m64다. 이번 결과 때문에 m64·나머지 shifted·M9·기존 중심점·old R8을 다시 계산하지 않는다. source table·재이온화율·capture 또는 global operator 승격도 없다.

## 출처와 신뢰 범위

- 프로젝트 원문: 입력에 보존한 REFERENCE_SELECTOR_REPAIR.md, CONTINUOUS_MAJORANT_ROUTE_A.md, PROJECTOR_RATE_THEOREM.md, REGULARITY_AND_DYNAMICS_TRANSFER.md와 R4AI 계약.
- GitHub exact ref 0d7bdbe76dc35d38668d750e6312919cecb09144의 gapped_tail_followup_20261001/GAPPED_TAIL_THEOREM.md는 ‘전체 두 중심 gap을 사용할 수 없음, disjoint support 후 projectile block만 적용’을 명시한다. remote 내용은 읽었고 새 원자 계산은 하지 않았다.
- Artacho–O’Regan, Quantum mechanics in an evolving Hilbert space, arXiv:1608.05300v2, Phys. Rev. B95,115155(2017). 이번 조회는 abstract/identity이며 moving-basis 일반 근거다.
- Burgarth et al., One bound to rule them all: from Adiabatic to Zeno, arXiv:2111.08961v2, Quantum6,737(2022). 이번 조회는 abstract/identity이며 integral-action 접근의 일반 근거다.
- 위 새 수식의 증명은 이 문서에 직접 제시했으며 문헌의 미확인 세부 정리를 복사한 것으로 주장하지 않는다. Fraction 정확 계산과 새 fixture 시험은 proof assistant나 실제 원자계의 검증을 대신하지 않는다.
