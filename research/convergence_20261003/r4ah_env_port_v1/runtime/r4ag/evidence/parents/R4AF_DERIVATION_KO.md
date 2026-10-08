# R4AF: 복소 타원 상계와 tensor Gauss에 의한 cross-S 검증 적분

2026-10-03 KST. 대상은 저장된 유한 s+p candidate의 한 실제 geometry이며, 물리적 radial basis 완전성이나 산란 확률을 인증하지 않는다. 이전 R4AE의 M9와 Peano 항은 원 identity로 보존하고 계산하지 않았다.

## 1. 정확히 같은 수학적 함수

SI에서 C_ab=∫φ_Ta(x)* exp[i m_e v_phys x_z/ħ − i m_e v_phys² t/(2ħ)] φ_Pb(x−b e_x−z e_z)d³x다. φ=u(r)Y_lm/r, l=0,1. 좌표는 a0, 에너지는 E_h, 시간은 t_a=ħ/E_h, 속도는 a0/t_a로 환산하며 C와 S는 무차원이다. 저장 FP64 입력은 정확한 이진 유리수로 읽는다. 현재 b=2, z=−32, v=2.00798106651023이며 t는 GEOMETRY.json의 실제 FP64 epoch를 그대로 쓴다. z/v의 이상적 epoch로 교체하지 않는다. 원점·outer edge에서 u=0인 40패널 degree4 함수,5 radial modes,9 ordered channels/center를 유지한다.

기존 shell-pair polygon의 affine-R vertex와 signed Duffy Jacobian을 그대로 사용한다. R=√(b²+z²)만 real outward interval로 읽는다. 한 삼각형에서 r0,r1은 reference square의 u,w에 대한 다항식이다. 원점 p모드에는 첫 패널 u/r의 정확한 다항식 소거를 사용하며, 원점 slope를0으로 바꾸지 않는다. 다른 패널에는 r0,r1 분모가 남으므로 복소 연장에서 pole 회피를 명시적으로 검사한다.

Q=[(r0+r1+R)(r0+r1−R)(R+r0−r1)(R−r0+r1)]/(4R²), k=vb/R, x=−k²Q/4. Φ_n(x)=Σ_j x^j/[j!(j+n)!]는 entire다. B0=Φ0, T1=(kQ/2)Φ1, T2=(k²Q²/4)Φ2로 parent의 네 각도 moment를 그대로 구성한다. 남은 적분함수는

F_ab(u,w)=exp[i vz(r0²−r1²)/(2R²)+i δ_epoch] J_Duffy/(2R) [u_a(r0)/r0^l_a][u_b(r1)/r1^l_b] A_ab,
δ_epoch=vz/2−v²t_FP/2.

복소 u,w로 연장할 때 target harmonic의 켤레는 상수 계수에만 적용한다. 복소 변수 자체를 켤레화하면 정칙성이 깨지므로 금지한다. Q나 sqrt(Q)의 branch를 새로 만들지 않고 entire 결합을 유지한다. 연속 수학적 함수와 물리 의미의 동등성이 확인되므로, 기존 이상적-epoch M9는 후속 이상적 stencil에 그대로 쓸 수 있다. 이번 actual-epoch point를 shifted stencil 또는 이상적 epoch와 같다고 취급하지 않는다.

## 2. 원전의 일차원 Gaussian 타원 상계

공식 FLINT acb_calc 문서의 Local integration algorithms는 다음 상계를 제시한다. f가 초점 ±1, parameter ρ>1인 Bernstein 타원 안에서 정칙이고 |f|≤M이면,

|I[f]−Q_n[f]|≤κ_n(ρ) M,
κ_n(ρ)=64/[15(ρ−1)ρ^(2n−1)].

이 명제와 arbitrary-precision Gaussian/complex-bound 전략은 문헌 근거다. 본 코드가 FLINT를 실행하거나 그 구현 검증을 계승했다는 뜻은 아니다. 현재 FLINT 설치를 확보하지 못해 별도 정수 구간 구현을 사용했다.

우리 reference box의 반폭을 h_u,h_w라 하자. M_u는 u의 복소 타원과 w의 실수 구간의 곱에서 |F|를 지배하며, M_w는 반대다. 두 변수를 동시에 복소화한 큰 polydisc가 필요하지 않다. 정확한 선형 functional 항등식

I_u I_w−Q_u Q_w=(I_u−Q_u) I_w+Q_u(I_w−Q_w)

및 Gaussian weight의 양성·총합2를 쓰면 각 복소 행렬원소에 대해

|∫_B F−Q_u Q_w F|≤e_ab,
e_ab=2 h_u h_w κ_n(ρ)(M_u,ab+M_w,ab)

를 얻는다. 이것은 본 작업에서 사용한 tensor 오차 합성이다. 고차 rule 두 개의 차이를 상계로 사용하지 않는다.

각 복소원소의 실수·허수에 각각 [−e_ab,e_ab]를 더하면 안전한 복소 직사각형 구간이다. X=[[0,C],[C†,0]]의 Frobenius 반경에는 2√Σ e_ab²≤2Σ e_ab를 사용할 수 있다. 이 L1 majorant로 각 패널의 Gaussian 차수를 실행 전에 선택하고, 최종 수치는 더 날카로운 squared Frobenius 합으로 평가한다.

## 3. 계산 가능한 M_u,M_w와 pole 검사

ρ=2를 사전 고정했다. 정규화 타원은 실수 반축5/4, 허수 반축3/4인 직사각형 안에 있다. reference box마다 이를 정확한 유리수로 사상한 complex rectangular interval에서 모든 polynomial/rational factor를 감싼다. sqrt(R²)는 point parameter의 real interval이며 복소 변수를 따라 sqrt를 계산하지 않는다. 원점에서 소거되지 않는 r 분모의 복소 직사각형에0이 포함되면 그 패널은 승인하지 않는다.

복소 Φ의 majorant는 다음 elementary series 비교로 직접 얻는다. a=|x|≥0에서
Σ a^j/[j!(j+n)!]≤(1/n!)Σ a^j/(j!)²≤exp(2√a)/n!.

첫 부등식은 (j+n)!≥n!j!, 둘째는 (2j)!≤4^j(j!)²와 exp 급수의 짝수항에 의해 성립한다. 이 상계는 양의 유한 a 전체에 유효하므로 real-axis oscillatory cancellation을 complex bound에 잘못 사용하지 않는다. |exp(iθ)|≤exp(|Imθ|)도 함께 사용한다.

exp의 양의 상계는 argument를1/2 이하로 나눈 뒤80항 Taylor와 기하급수 remainder, 반복제곱으로 계산한다. exponent cap1024를 넘거나 pole을 배제하지 못하면 fail-closed이며 자의적으로 무한값을 잘라내지 않는다. 각각의 remainder bound는 계수 비교에 근거하고, libm exp의 반올림을 가정하지 않는다.

## 4. Gauss node·weight와 실제 산술

SciPy/mpmath의 근은 오직 bracket 제안값이다. 각 n에 대해220-bit dyadic bracket n개에서 정확 유리수 Legendre 부호 변화를 검사하고, bracket의 서로소성과 (−1,1) 포함을 확인한다. degree n이므로 모든 근이 포괄된다. 근 구간을256-bit dyadic interval로 포함시킨 뒤

w_i=2/[(1−x_i²)(P_n'(x_i))²],
P_n'=n(xP_n−P_(n−1))/(x²−1)

로 weight를 감싼다. 모든 weight가 양수이고 총합 구간이2를 포함해야 한다. proposal library는 최종 certificate의 root 위치 권위가 아니다.

native evaluator는 GMP mpz 정수 endpoint/2^256을 쓴다. +와−는 정확하고, ×와÷는 floor/ceil, sqrt는 integer sqrt로 방향성 반올림한다. π는 parent의 Machin 급수 포함구간을 입력으로 받는다. sin/cos64항, Φ96항은 실제 Gauss 실수 노드의 domain에서 explicit tail bound를 더한다. 모든 weighted sum은 정수 구간으로 계산하므로 병렬 합산이 비결정적인 FP reduction으로 바뀌지 않는다. 3개 disjoint cell partition의 최종 합도 exact integer endpoint 합이다.

최종 C_mid의 mathematical dyadic midpoint와 FP64로 저장한 convenience midpoint는 서로 다른 값이다. 후자는 별도 exact-binary distance로 다시 감싸 자신의 반경을 부여한다. 기존 저장 S의 TP와 PT는 각각 별도로 비교하며, 원래 raw 행렬을 adjoint projection으로 수정하지 않는다.

## 5. 오차의 의미와 유효범위

최종 point 구간에는 Gaussian analytic remainder, uncertain nodes/weights, geometry/phase/radial/초월함수 반올림과 누적 산술이 포함된다. 물리 radial truncation, source-model discrepancy, time-propagation, other geometry 또는 전체 trajectory 오차는 포함하지 않는다. 정확한 full-cross18x18 norm과 9x9 C norm의 √2를 혼동하지 않는다.

R4AE의 M9 bound와 같은 물리함수를 평가한다는 algebraic equivalence가 있으나, 새 point 계산은 actual epoch이며 M9는 ideal epoch다. 후속 stencil 합성에서 parent의 epoch 사상 항은 여전히 필요하다. 중심 z0 한 점의 성공을 여덟 shifted sample의 성공으로 복사하지 않는다. 전체 stencil total_upper는 미확보 항이 있는 동안 null이다.

구현 검증, 수학적 유도, 정수산술 신뢰 기반은 proof-assistant 형식 인증과 구별한다. independent reviewer는 exact Legendre polynomial 부호, 저장 M에 대한 Gaussian 부등식, 모든 native cell endpoint 합, Frobenius 제곱부등식을 다른 구성으로 확인한다. 같은 세션의 별도 산술이며, complex magnitude를 다른 물리 적분기로 재계산하거나 별도 인간 검토한 것은 아니다.

## 원전과 provenance

[EXT_GAUSS] FLINT 공식 acb_calc 문서, Local integration algorithms, 2026-10-03 KST 확인. https://flintlib.org/doc/acb_calc.html . 위 κ_n과 holomorphy 조건만 사용했다.
[EXT_PETRAS] F. Johansson, Numerical integration in arbitrary-precision ball arithmetic, arXiv:1802.07942v1 (2018). https://arxiv.org/abs/1802.07942 . complex magnitude로 Gaussian 오차를 통제하는 방법 맥락이며 현 candidate의 certificate가 아니다.
[PROJECT_R4AE] parent DERIVATION, result, pinned WINDOW_JET, candidate/geometry/S input. M9는 재계산하지 않았다.
