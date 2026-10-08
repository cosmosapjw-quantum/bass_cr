# R4AL: 전체 18채널 Gram의 연속 양성 및 H1 weak 연산자 norm tube

2026-10-03. 원자 데이터 전용. 기존 R4AK는 공진쌍 Gram만 닫았으며 전체 18채널 하한은 null이었다. 이번에는 R4AF의 인증된 중심 cross S와 R4AB의 정확 radial G,T를 재사용하여 전체 18채널의 기존 두 window에서 양성을 증명한다. 새 cross/radial 적분, M9 및 옛 R8 계산은 없다. 원 radial eigensolve 복원, 실제 원자모델 완전성 또는 작은 bridge 오차를 주장하지 않는다.

## 1. 대상, 규약, 근거

내적은 첫 인수에 반선형이다. finite compact candidate는 5 radial modes, 각 40개 패널의 degree-4 연속 다항식 u_a와 정규화된 Y_lm이다. l=(0,0,0,1,1), 각 l에 모든 m을 유지하므로 한 중심 9개, 전체 18개다. phi_alm=u_a(r)Y_lm/r, u_a(0)=u_a(64a0)=0이며 밖은 0이다. 내부 u' jump를 제거하지 않는다.

길이 a0, 시간 ta=hbar/Eh, 에너지 Eh를 계산 단위로 명시한다. 물리적 hbar, m_e, Coulomb coupling을 없앤 것이 아니다. 아래 SI 병진위상은

chi_P(x,t)=exp[i k x_z-i nu t] phi_P(x-b e_x-v_phys t e_z),
k=m_e v_phys/hbar, nu=m_e v_phys^2/(2hbar).

원자단위의 수치값은 b=2, z=vt, v=4521571391451241/2251799813685248=2.00798106651023, k=v, nu=v²/2다. 입력 float는 exact binary rational로 읽는다. 기본 metric(-,+,+,+)는 국소 비상대론 전자 weak 적분에 사용되지 않는다.

S=F†F, F=[F_T,F_P]이고 S=[[G,C],[C†,G]]이다. 이 Hermitian block structure는 정확한 inner product의 정의다. 옛 저장 raw TP/PT를 서로 평균하거나 덮어쓰지 않는다. 기존 C0의 certified interval은 z0=-32, 저장 actual t_FP=-15.936405244903225의 함수다. positive Gram의 norm 상계에는 공통 epoch phase가 영향을 주지 않지만, constant-reference matrix를 만들 때는 actual/ideal epoch를 따로 처리한다.

G와 T의 정본은 inputs/BASS_CR_R4AB_GRAM_EXACT.json이다. 그 J 필드는 radial derivative matrix이지 integral u²/r²가 아니다. 이를 혼동하지 않는다. 본 계산은 미확보된 u²/r² moment를 재계산하지 않고 Hardy 상계로 처리한다. R4AF S_ENCLOSURE의 hash/seal/geometry/result와 candidate identity, npz hash를 검증했다. 상세 경로는 evidence/INTAKE.json에 있다.

## 2. H1의 충분조건과 radial Hardy 상계

연속 finite polynomial u, 양 끝 zero trace는 u의 zero extension이 H1임을 보장한다. 정규화 구면조화함수에 대해

||phi_alm||² = g_a = integral |u_a|² dr,
||grad phi_alm||² = T_a + l(l+1) I_a,
T_a=integral |u_a'|² dr, I_a=integral |u_a|²/r² dr.

radial gradient의 cross term은 끝점 [u²/r]=0을 사용해 상쇄한다. r=0에서는 u=O(r), 따라서 u²/r -> 0이다. first derivative jump가 있어도 일차 weak derivative 계산에는 surface delta가 추가되지 않는다. 이차 strong derivative를 쓴다는 뜻은 아니다.

1차원 부분적분은 I_a=2 Re integral u_a* u_a'/r dr를 주므로 I_a <= 2 sqrt(I_a T_a), 따라서

I_a <= 4 T_a,
Q_a := ||grad phi_alm||² <= [1+4l(l+1)]T_a.

p orbital의 u'(0)를 0으로 바꾸지 않는다. p angular function이 원점에서 방향의존 극한을 가져도 ||grad phi||²의 위 상계는 유한하다. 이것만으로 H2/H9를 선언하지 않는다.

모든 m을 포함한 각 radial multiplet의 derivative tensor trace는 회전 불변이다. 따라서 그 z-z 성분은 trace의 1/3이다. 전체 한 중심에 대해

N = sum_a (2l_a+1)g_a,
Q = sum_a (2l_a+1)[1+4l_a(l_a+1)]T_a,
sum_channels ||partial_z phi||² <= Q/3.

이 식은 각 p_m의 gradient가 개별적으로 등방적이라는 주장이 아니다. full multiplet이 없는 입력에는 적용하지 않는다. code는 현재 (0,0,0,1,1) layout만 받는다. Y의 정규화와 parity, addition theorem은 NIST DLMF14.30.E7/E8/E9를 참조한다. multiplet derivative trace와 radial Hardy 적용은 위에서 직접 유도했다.

## 3. S의 전역 H1 Lipschitz 상계

ideal z parameter의 projectile column은

partial_z chi_P = exp[i v x_z-i v z/2](-partial_z phi_P-i v phi_P/2).

동일 l,m의 parity로 <phi,partial_z phi>=0이다. 모든 column의 제곱 norm을 합하면

beta = Q/3 + (v²/4)N

이 z derivative Hilbert-Schmidt norm 제곱의 상계다. SI에서는 Q/3+k²N/4이다. target synthesis norm은 ||F_T||²=||G||<=g_plus다. 따라서

||C_z||_2 <= sqrt(g_plus beta) =: L_C,
||S(z)-S(w)||_2 = ||C(z)-C(w)||_2 <= L_C |z-w|.

여기 full block [[0,A],[A†,0]]의 operator norm은 ||A||_2이고 2||A||가 아니다. Frobenius norm은 sqrt(2)||A||_F라는 별개의 항등식이다. operator norm과 Frobenius norm을 혼용하지 않는다.

위 도함수와 Lipschitz 명제는 H1 translation 정리에서 직접 따른다. smooth compact functions에는 fundamental theorem of calculus와 Minkowski를 적용하고, H1 density로 닫는다. 이 결과는 shell contact가 있는 곳에서도 유효하다. C9에 필요한 contact-cell 가정을 사용하지 않는다. 그러나 이 사실로 기존 M9 bound의 domain을 확대하지는 않는다.

## 4. full18 Gram의 양의 하한

같은 angular labels에만 radial G_ab를 배치해 한 중심 9x9 G를 정확하게 조립한다. 원 offdiagonal과 대각 norm을 그대로 유지한다. exact Gershgorin으로 g_minus I <= G <= g_plus I를 얻는다.

R4AF의 각 복소 rectangle에서 최대 절댓값의 제곱합을 정수 제곱근으로 위쪽 반올림해 c0 >= ||C(z0)||_F >= ||C(z0)||_2를 얻는다. 실제 t_FP와 ideal t=z/v 차이는 C 전체의 공통 unit-modulus phase이므로 c0는 그대로 사용 가능하다.

|z-z0|<=H에서 c(H)=c0+H L_C, 그리고

s_minus(H)=g_minus-c(H),
s_plus(H)=g_plus+c(H)

이면 s_minus I <= S(z) <= s_plus I다. s_minus>0일 때만 positivity와 cond2<=s_plus/s_minus를 반환한다. 단순한 한 점의 eigenvalue를 uniform lower bound로 쓰지 않는다.

기존 window H=1/64: s_minus>=0.944949461133, s_plus<=1.055050538867,
H=1/128: s_minus>=0.971145650753, s_plus<=1.028854349247.

표시는 바깥쪽 반올림이고 정본은 CERTIFICATE.json의 exact rationals다. 한 중심 g_minus≈0.9999999999999878, g_plus≈0.9999999999999977, c0≈0.0026581596268377573, Q≈6.514166959605371, L_C≈3.3531122713574666/a0이다.

이 범위는 현재 두 window뿐이다. 전체 |z|>=12, 다른 b/E/basis에 적용했다고 하지 않는다. 기존 R4AK pair bound와 비교되는 새로운 full18 bound이며 두 대상을 바꿔 쓰지 않는다.

## 5. actual epoch와 constant S tube

actual t_FP sample의 위상 offset delta=(v z0-v²t_FP)/2이다. ideal C=e^(-i delta) C_actual. q=1-i delta-delta²/2, eta=|delta|³/6이면 real delta에 대해 |e^(-i delta)-q|<=eta다. 적분 Taylor remainder의 모든 실수축 도함수의 modulus가 1이라는 사실을 사용한다.

R4AF rectangle midpoint M과 full-X Frobenius radius eps0를 사용해

||X_ideal(z0)-X(qM)||_2 <= eps0+eta||X(M)||_F=:eps_anchor.

G를 양 대각 block에 넣고 qM을 offdiagonal로 넣은 exact-rational matrix S_ref에 대해

||S(z)-S_ref||_2 <= eps_anchor+H L_C=:eps_S(H).

eps_S≈0.052392379239960415 및0.026196189619980208이다. 이는 구간 전체에 대한 0차 reference error이며, 기존 R4AF point radius를 악화시킨 새 point 적분이 아니다. 현재 coarse variation tube를 미분식의 tiny per-sample error로 대입하지 않는다.

## 6. 전체 weak H,D,K,Sdot의 uniform norm tube

complete real radial channels에서 <phi,partial_z phi>=0이므로, 원자단위의 전 프레임 gradient trace와 time derivative trace는

A = 2Q+v²N,
B_t = v² beta

로 감쌀 수 있다. 따라서 ||grad F||²<=A, ||Fdot||²<=B_t, ||F||²=||S||<=s_plus.

3D Hardy ||psi/|x-R_A|||<=2||grad psi||를 각 Coulomb 핵에 적용한다. SI weak form은

h(psi,psi)=hbar²/(2m_e)||grad psi||² - sum_A kappa_A integral |psi|²/|x-R_A| dx.

따라서

||H|| <= hbar²/(2m_e) A + 2 sum_A |kappa_A| sqrt(s_plus A),
||D|| <= sqrt(s_plus B_t),
||K|| <= ||H||+hbar||D||,
||Sdot|| <= v L_C.

마지막 식은 same-centre Gram이 상수여서 cross block만 미분되는 구조를 사용한다. code는 두 charge1과 명시된 a0/Eh/ta 규약에 한정돼 H<=A/2+4sqrt(s_plus A)를 계산한다.

H=1/64에서 H<=53.511150176794Eh, D<=6.915830495559/ta,
K<=60.426980672353Eh, Sdot<=6.732985954769/ta.
H=1/128에서 K<=59.980131124719Eh다.

이는 정확 finite candidate weak operator의 **absolute norm bounds**다. K_ref=0, Sdot_ref=0의 uniform remainder로 사용할 수 있으나, 기존 저장 H/D의 실제 오차가60이라는 뜻은 아니다. 오래된 H/D를 검사·재평가하지 않았다. K의 실제 변화나 상쇄를 활용하지 않았으므로 작은 bridge 목표를 인증하지 못한다.

이 정확 H1 모델에서는 Sdot=D+D†이고 H=H†이므로 Gamma=Sdot+(i/hbar)(K†-K)=0이다. 이는 수학 모델의 항등식이다. 옛 numerical assembly의 Gamma를 강제0으로 바꾸거나 Hermitian projection을 하지 않는다. R4AK의 범용 remainder provider가 독립 큰 eps_K와eps_Sdot를 더하면 이 상관관계를 잃을 수 있으므로 자동 엄밀승인하지 않는다.

## 7. 종료와 남은 것

닫힌 항: 같은 실제 finite candidate/두 기존window의 full18 Gram positivity, 0차 S-error tube, 전체 weak H/D/K와Sdot의 uniform 크기 상계, source/epoch/unit의 명시적 결합. 이는 실제 입력에서 계산한 새로운 exact bounds다.

열린 항: K의 정밀 spatial enclosure와 좁은 uniform variation/remainder; 실제 Sdot의 날카로운 interval; 같은 endpoint 초기상태; finite-window/basis/bridge/capture/cross-section. physical_bridge_upper와두stencil total은 null이다. 거친 zero-reference K bound를 작은 실제 bridge 오차로 포장하지 않는다.

다음 로컬: R4AM_WEAK_K_CONTACT_CELL_PROVIDER_AND_REMAINDER. weak gradient·Coulomb·ETF integrand와 원점/접합부를 포함하는 검증 적분기를 설계·구현하고 필요한 최소 native query를 별도 계약한다. 최초crosscap0. 이것은 여기서 남아 있는 실제 원자 연구다.

외부: 기존 R4AH_m64. 이 계산은 완료된 R4AF point/M9를 재실행하지 않고, 실제 shifted sample을 얻기 위해 이미 전달한코드를NCP에서 실행하는 것. 여기서 동일 memory preflight를 다시 수행하지 않는다.

## 출처와 신뢰 범위

[PROJECT] R4AK DERIVATION/NEXT_DAG, R4AB exactG/T, R4AF qualified C enclosure and metadata. 해시와원archive경로는evidence/INTAKE.json.
[PRIMARY_ANGULAR] https://dlmf.nist.gov/14.30, normalization/parity/addition identities only.
[PRIMARY_MOVING] https://arxiv.org/abs/1608.05300, evolving nonorthogonal basis connection의일반근거. 이번uniformbounds는직접유도이며그논문의미확인certificate를상속하지않음.

정수/Fraction 산술, 43개 신규시험, 다른구성의211개읽기전용조건은implementation evidence다. 증명보조기/제삼자인간검토/실제물리sourcevalidation과다르다.
