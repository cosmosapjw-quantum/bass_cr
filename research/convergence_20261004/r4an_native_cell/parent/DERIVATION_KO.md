# R4AM: 원점 정칙화를 포함한 cross weak-K 검증 적분기

2026-10-03. 범위는 BASS_CR의 원자 데이터 생산이다. Bianchi 배경·수송·재이온화 동역학은 rei_bianchi가 담당한다. 이 단계는 R4AL의 다음 노드에 해당하는 유도와 참조 구현 및 fixture 검증이며 실제 원자 K 행렬 계산이나 작은 bridge 오차의 종결은 아니다.

## 1. 기준 함수와 weak operator

첫 인수에 반선형인 내적을 사용한다. T 핵은 정지하고 P 핵의 위치는 Rvec=(b,0,v_phys t)이다. 두 핵의 전하는 각각 +e이다. 전자 함수는

chi_T(x,t)=phi_T(x),
chi_P(x,t)=exp[i k x_z-i nu t] phi_P(x-Rvec),
k=m_e v_phys/hbar, nu=m_e v_phys^2/(2 hbar),
phi_alm=u_a(r)Y_lm/r.

여기서 Y_lm는 정규화 구면조화함수다. u는 저장된 연속 패널별 4차 다항식으로 원점과 외곽 끝점에서 0이다. 실제 비영 원점 slope와 내부 u' jump를 보존한다. 원 nodal eigensolve나 실제 원자기저의 완전성을 복원한 것이 아니다.

기준은 보존한 two_center.py의 H=1/2 gradient product + Coulomb potential, D=<chi_a,dot chi_b> 및 같은 candidate adapter다. source 경로와 해시는 inputs/legacy_sources/ARCHIVE_LOCATORS.txt 및 SOURCE_INPUT_LOCK.json에 있다. 이를 읽었지만 과거 계산이나 시험을 실행하지 않았다.

H_TP = integral [hbar^2/(2m_e) grad chi_T* dot grad chi_P + V chi_T* chi_P] dx,
D_TP = integral chi_T* dot chi_P dx,
K_TP = H_TP-i hbar D_TP,
V= -e^2/(4pi eps0) (1/r_T+1/r_P).

새 코드는 길이 a0, 에너지 Eh, 시간 ta=hbar/Eh의 무차원 수치값을 사용한다. 따라서 k의 수치값은 v, nu=v^2/2, kinetic 계수는 1/2이다. H와 K의 출력 단위는 Eh, D는 ta^-1, S는 무차원이다. 이 단위 및 두 charge=1을 실행계약에 고정하며 다른 단위·전하로 자동 일반화하지 않는다. 핵간 반발에너지 같은 새 scalar 항을 추가하지 않는다.

phase를 밖으로 빼고 f_T=phi_T*, f_P=phi_P라고 하면

h = (grad f_T dot grad f_P)/2 + (i v/2)(partial_z f_T) f_P -(1/r_T+1/r_P) f_T f_P,
d = -v f_T partial_z f_P - i nu f_T f_P,
kweak = h - i d.

-i d에는 +i v f_T partial_z f_P 및 -nu f_T f_P가 들어간다. 이를 단순히 H와 같은 것으로 두지 않는다. T 열은 정지하므로 D_PT=0, 정확한 모델에서 K_PT=H_TP^dagger다. 이는 모델 정의이며 저장된 raw 행렬을 대칭화하거나 평균내는 조작이 아니다. K 자체는 일반적으로 Hermitian이 아니므로 S의 sqrt(2) Frobenius 변환을 무조건 적용하지 않는다.

약한 gradient 형식을 직접 사용한다. 두 번 부분적분하여 strong Laplacian으로 바꾸거나 패널 경계의 surface 항을 버리지 않는다. H1 적합성과 약도함수의 정의는 원점 p 함수의 전역 매끄러움이나 H2 정칙성과 다르다.

## 2. 일반 shell-pair 영역

두 중심 거리 R=sqrt(b^2+z^2), r0=|x|, r1=|x-Rvec|를 쓴다. 한 shell pair의 영역은 radial 직사각형과 r0+r1>=R, |r0-r1|<=R의 교집합이다. 기존 affine-R polygon의 완전한 분할과 signed determinant 검사를 재사용한다. 이번에는 두 반경이 첫 패널에 들어가는 영역만 아래 원점 chart로 정확히 대체한다.

e=(b,0,z)/R, e1=(-z,0,b)/R, e2=(0,-1,0),
A=(r0^2-r1^2+R^2)/(2R), Q=rho^2,
x_T=A e+U e1+V e2, x_P=x_T-R e,
U=rho cos(phi), V=rho sin(phi).

reference triangle을 Duffy square로 옮겼을 때 signed Jacobian을 포함한 각도 평균 앞의 인자는 r0 r1 J_Duffy/(2R)다. 1/2는 각도 2pi와 두 함수의 1/(4pi) 정규화가 결합한 값이다.

sqrt(4pi) r^l Y_lm에 해당하는 solid harmonic은 s에서 1, p에서 c_m dot x다. c_0=(0,0,sqrt3), c_-1=(sqrt(3/2),-i sqrt(3/2),0), c_+1=(-sqrt(3/2),-i sqrt(3/2),0)이다. target의 켤레는 c_m의 상수 계수에만 취한다. 복소 analytic extension에 사용한 좌표까지 켤레화하면 holomorphy가 깨지므로 그렇게 하지 않는다.

q_l=u/r^(l+1), g_l=1 또는 c_m dot x일 때

sqrt(4pi) phi=q_l g_l,
sqrt(4pi) grad phi=q_l grad g_l + (q_l'/r)g_l x.

p gradient는 U,V에 대해 이차이므로 두 gradient의 곱은 사차다. 따라서 S용 이차 모멘트만으로 kinetic 항을 조립할 수 없다.

## 3. 사차까지의 entire 각도 모멘트

Phi_n(x)=sum_{j>=0} x^j/[j!(j+n)!], x=-k_eff^2 Q/4라 두자. 정수 Bessel 급수 또는 직접 원주 평균으로

<exp(i k_eff U)>=Phi_0(x),
<U^n exp(i k_eff U)> = i^(-n) d^n/dk_eff^n Phi_0(-k_eff^2 Q/4).

n<=4에서 이 도함수는 다음 유한 합이다.

M_n0 = i^(-n) n! sum_{j=0}^{floor(n/2)}
  Phi_(n-j)(x) (-k_eff Q/2)^(n-2j) (-Q/4)^j /[(n-2j)! j!].

V의 홀수 거듭제곱 평균은 0이고,
M_(a,2s)=sum_{j=0}^s (-1)^j binom(s,j) Q^(s-j) M_(a+2j,0).

이 식은 Q의 제곱근 branch를 사용하지 않는 entire 결합이다. collinear Q=0에서도 값이 정의된다. 전체 angular degree<=4만 지원하며 그 이상은 거절한다. 일반 higher-l backend를 구현했다는 뜻이 아니다.

복소 majorant에는 |Phi_n(x)|<=exp(2sqrt(|x|))/n!를 사용한다. (j+n)!>=n!j!와 sum y^j/(j!)^2=I0(2sqrt y)<=exp(2sqrt y), y>=0으로 유도된다. 여기 sqrt는 비음수 실수 modulus의 상계에만 쓰며 analytic integrand의 복소 sqrt(Q)가 아니다. 다른 phase 인자는 |exp(i theta)|<=exp(|Im theta|)로 감싼다. 모든 coefficient와 계산값은 방향성 반올림 구간이다.

실수 chart의 Q>=0은 실제 기하에서 증명한 경우에만 interval과 교집합을 취한다. 복소 majorant에서 음수·복소 Q를 0으로 투영하지 않는다. 실제 reference unit square 밖에서 value evaluation을 요청하면 거절한다.

## 4. 원점을 버리지 않는 radial-difference chart

첫 패널 끝을 a라 하자. R>2a이고 [R-a,R+a]가 상대 핵의 한 radial 패널 안에 들어가는 경우를 등록한다. 근접 핵 중심 반경 r=a u, 상대 반경 r_o=R+r eta, eta=2w-1, (u,w) in [0,1]^2를 사용한다.

T 원점 chart에서 mu=-eta+r(1-eta^2)/(2R), P 원점 chart에서는 mu=eta-r(1-eta^2)/(2R)다. n=mu e+U e1+V e2, U^2+V^2=1-mu^2로 둔다. 각각 x_T=r n 또는 x_T=R e+r n이다. 각도 평균 뒤의 체적 계수는 r^2 r_o/(2R) dr d eta이며 dr d eta=2a du dw다.

첫 패널에서 u(r)=c1 s+c2 s^2+c3 s^3+c4 s^4, s=r/a이므로

F(r)=u(r)/r=(c1+c2 s+c3 s^2+c4 s^3)/a

는 정확한 다항식이다. 원점 p 함수는 F(r)c dot n으로 방향의존 극한을 가질 수 있다. 그러나 원점 chart에서 필요한 scaled gradient는

s: r grad phi = r F'(r)n /sqrt(4pi),
p: r grad phi = [r F'(r)(c dot n)n + F(r){c-(c dot n)n}]/sqrt(4pi)

로 유한하다. 이것은 0/0을 작은 epsilon으로 바꾼 근사가 아니다.

두 원점 ball이 분리돼 있어 각 cross 적분에는 한쪽만 원점 gradient를 갖는다. kinetic 적분의 r^2와 1/r은 r로 결합한다. Coulomb의 local 1/r도 r로 결합하고 상대 핵의 분모는 r_o>=R-a>0이다. 예를 들어 T 원점에서 normalized harmonic 인자를 생략한 bracket은

H: (r/2)(r grad f_T) dot grad f_P + (i v r/2)(r partial_z f_T)f_P - (r+r^2/r_o)f_T f_P,
D: -v r^2 f_T partial_z f_P - i nu r^2 f_T f_P,
S: r^2 f_T f_P.

P 원점에서는 kinetic의 scaled gradient를 P 쪽에 두고 D의 병진항은 -v r f_T(r partial_z f_P)다. bracket 밖에는 r_o (2a)/(2R)만 남는다. phase에는 근접 핵 위치에 따라 상수 vz가 추가되며 실제 t_FP를 유지한다.

원점 r=0에서 이 weighted weak integrand는 유한하다. 원점 부피를 누락하지 않았고, 원점 slope나 p 함수를 smoothing하지 않았다. 이것은 angular/radial 적분 변수에서 정칙한 결합이라는 명제이지 원래 3차원 p orbital의 전역 C-infinity 명제가 아니다.

## 5. 실제 candidate의 완전한 cover

기존 큰 window z in [-2049/64,-2047/64] a0에서 R을 구간으로 계산했다. 실제 첫 edge a는 저장 FP64의 정확한 이진 유리수다. [R-a,R+a]는 remote panel 28에 엄격하게 포함된다. 원래 1,229개 삼각형 중 origin shell pair의 두 삼각형을 두 chart로 교체한다. 나머지 1,227개는 그대로다.

거리 평면에서 각각의 원점 영역 면적은 integral_0^a 2r dr=a^2다. 제거한 삼각형의 det/2 합이 R에 관한 다항식 계수별로 (a^2,0,0)과 같음을 검사했다. 따라서 전체는 일반 삼각형 1,227개+원점 chart 2개, 누락 영역 0이다. 이 검사는 실제 candidate의 기하만 평가했으며 S,H,D,K 행렬원소 적분은 0회다.

등록 조건을 만족하지 않는 더 작은 R, remote radial interface와의 교차, 미검증 polygon topology에는 현재 provider가 fail-closed한다. 이를 전체 궤도 지원으로 읽지 않는다.

## 6. S의 정칙성을 복사하지 않고 K를 직접 다룬 결과

고정 contact cell에서 각 non-origin triangle의 material 좌표는 R에 해석적이고 실제 반경 분모는 양수다. 원점 chart는 위 소거를 통해 local r 분모를 없앴으며 remote 분모만 남긴다. 모든 angular moment는 entire 결합이다. 각도·체적·위상·움직이는 경계항까지 포함한 각 유한 적분은 compact reference square 위의 해석적인 integrand가 된다. real domain에서 분모가 떨어져 있고 유한 cover이므로 각점 주변의 작은 복소 근방을 선택할 수 있다. 적분과 매개변수 미분은 그 근방의 균일 지배하에서 교환된다.

따라서 이 별도 유도는 등록된 열린 contact cell 안의 정확한 finite-candidate cross weak-K의 국소 real-analytic/C-infinity 성질을 준다. u' jump는 서로 다른 panel 함수로 영역을 분할해 처리했으며 volume-only 미분으로 지우지 않았다. 이 명제는 전역 C9, strong H2, 실제 물리 basis의 매끄러움과 다르다.

현재 코드는 **고정 실제 geometry에서의 u,w 복소 근방**만 평가한다. z 자체의 복소 근방 반경·도함수 numerical bound는 구현하지 않았다. 그러므로 이 존재 유도로 기존 S의 M9 수치를 K에 복사하거나 finite-window K variation/error를 수치 인증하지 않는다.

## 7. 실제 나머지가 있는 검증 cubature

f가 Bernstein 타원 E_rho에서 정칙이고 |f|<=M이면 Gauss-Legendre n점 나머지의 채택한 상계는

|I f-Q_n f| <= kappa_n(rho) M,
kappa_n=64/[15(rho-1)rho^(2n-1)], rho>1.

이 식은 FLINT acb_calc 공식 문서와 Johansson의 방법에 근거한다. FLINT native library를 이번 실행에 사용한 것은 아니다. 양의 Gauss weights의 합=2와
Iu Iw-Qu Qw=(Iu-Qu)Iw+Qu(Iw-Qw)
를 사용하여 mapped cell의 각 복소 행렬원소에

e=2 h_u h_w kappa_n (M_u+M_w)

를 더한다. M_u는 복소 u 타원과 실수 w 구간 전체에서의 상계이고 M_w는 반대다. 두 quadrature 차수의 차이를 e 대신 사용하지 않는다. 복소 분모가 0을 포함하면 계산을 거절하거나 미리 고정한 subdivision 한도 안에서 나눈다. unresolved cell을 0으로 처리하지 않는다.

계산 node는 scipy/mpmath가 후보만 제시하며 정확 유리수 Legendre 부호 변화와 서로소 bracket으로 확인한 기존 구현을 사용한다. node, weight, moment, phase, 적분 누적에는 Python 정수/2^256 방향성 반올림을 사용한다. 정확 Gauss rule과 구간 node/weight 평가의 관계에 따른 산술 포함성과 해석적 나머지를 구분한다. GPU/Fortran/GMP native hotloop를 새로 구현하거나 NCP 속도를 검증했다고 하지 않는다.

## 8. 실제 수행과 구현 한계

새 시험은 부적합 channel/degree/origin/pole/epoch/계약을 거절하고, 원점·일반 chart의 16개 s/p 각도 조합을 별도 Cartesian field/gradient의 4096점 원주합과 비교한다. 비교는 floating numerical check이며 그 근접도 자체를 검증 cubature 나머지로 사용하지 않는다.

별도 사전계약에서 u=r인 국소 제조함수, v=0, R=5a0를 사용했다. 이는 정규화된 물리 원자함수가 아니라 해석적 테스트 함수다. 두 원점 ball에서 정확히 S=a^3/3, H=K=-a^2/2-a^3/(3R), D=0이다. 정해진 일반 삼각형에서는 S=139/240, H=K=-7/20, D=0이다. n=32,rho=2의 실제 구간들이 이 값을 포함했고, 1e-16 목표 이내였다. 실제 원자 K matrix 평가나 전체 교차행렬의 정확도는 아직 계산하지 않았다.

source/run_reference.py는 같은 actual center geometry에서 한 행렬원소만 다루는 별도 미승인 실행 경로다. 현재 Python reference 구현은 정확성 기준이며 고성능 native 대체가 아니다. NCP에서 source/native 동등성 검토 없이 전체 81원소 또는 모든 shifted geometry로 확장하지 않는다. 시간/평가 budget에 걸리면 실패·부분 기록을 남기며 재시도하지 않는다. reference의 적은 fixture 실행시간을 전체 atomic run 소요시간으로 외삽하지 않는다.

## 9. 명확히 열려 있는 항목

실제 K의 좁은 cellwise enclosure, full cross 행렬 구성·검산, K(z)의 numerical uniform remainder, 같은 endpoint의 초기상태·selector/embedding 오차, 산란창·결합기저·b 적분·에너지표는 남아 있다. local real-analytic 유도와 fixture 성공은 이를 대신하지 않는다.

physical_bridge_upper=null, precise_K_cubature_error=null, full_stencil_total_upper=[null,null]. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO를 유지한다.

## 원전·구현 근거

- R4AL DERIVATION/NEXT_HANDOFF 및 original two_center.py/exact_cross.py: 현재 weak form/phase 규약. 원본 해시를 보존하며 계산 재실행 없음.
- NIST DLMF 10.9, https://dlmf.nist.gov/10.9 : 정수차 Bessel 각도 적분 항등식. 사차 도함수·origin chart·weak 결합은 본 작업의 직접 유도.
- FLINT acb_calc, https://flintlib.org/doc/acb_calc.html : 정칙성 조건부 Gaussian error theorem. 본 실행의 산술은 별도 Python integer interval 구현.
- Artacho–O'Regan, https://arxiv.org/abs/1608.05300 : 움직이는 비직교 기저 연결항의 일반 근거. 현재 finite-candidate proof나 numerical certificate를 논문으로부터 자동 상속하지 않음.

모든 방향성 반올림/새 코드는 proof-assistant 검증이 아니며 제삼자 인간 검토를 했다고 주장하지 않는다. fixture 검증, 실제기하 확인, 실제 원자 데이터 검증, runtime 및 게시 상태를 분리한다.
