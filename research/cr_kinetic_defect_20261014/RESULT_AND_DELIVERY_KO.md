# Gaussian 형태 잔차의 kinetic 전파와 초기 온도 곡률

2026-10-14, Asia/Seoul. 선택 R5 `NT_CORE_TAIL_KINETIC_DEFECT_PROPAGATION`. 실제 부모 PR60 head `2c404479469cb0e1bf1dd073a50c1e2123809606`를 읽고 unchanged ref를 확인했다. 현재 상태는 **PARTIAL_CONTINUUM_FORWARD_CERTIFICATE**다. 정확한 radial kernel·초기 곡률·새 kinetic 수치 비교는 제공하지만, 전체 continuum finite-time 온도구간은 아직 null이다.

## 전체 재현 원본

- `BASS_CR_KINETIC_DEFECT_20261014_SOURCE.zip`: 4811067 bytes, 107 members/106 manifest payloads.
- SHA256 `3f601795158e533fdb65ed327488741d0f1dcb853e2551e30bbaf45283510599`.
- [전체 한국어 유도, 실제 코드·입력·kinetic 경로·검산·CAS·실패·DAG](https://drive.google.com/file/d/1bvpFtf0Du75UAimQQzGASRr6HkZYAPLr/view?usp=drivesdk).
- Drive ID `1bvpFtf0Du75UAimQQzGASRr6HkZYAPLr`, 기존 parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`: 실제 upload 및 metadata에서 ID/name/size/parent 일치.
- Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_KINETIC_DEFECT_20261014_SOURCE.zip`, ID `id:BSpOijBcT10AAAAAAD5csA`: completed, 같은4811067 bytes.
- 로컬106payload와 부모를 포함한6nested archives의 CRC·font 부재를 확인했고, 새 위치에 추출한 read-only verifier가 exit0을 반환했다. Remote verification은 R1 ACK/ID/name/size/parent이며 full-byte restore가 아니다.

이 Git 문서는 실질 유도와 재현 진입점이다. 실행된 전체 Python/Numba 코드와 실제 arrays는 ZIP에 있으며 Git에 모두 풀었다고 주장하지 않는다. 읽을 파일은 `REPORT_KO.md`, `CONTRACT.json`, `results/INITIAL_CURVATURE_INTERVAL.json`, `results/COMPARISON.csv`, `HANDOFF.json`이다.

## 1. 같은 continuum 초기분포와 scope

부모의 네 origin-labelled Maxwell-energy 초기분포를 유지한다. 수는 C/P/S/A=(1,1,.999,.001), 평균에너지는 원 source에서 보존한 값이며, theta=kBT/epsilon_eV는 약(.008712327653334758,19.96654127687456,.6628650249518994,.1161666666666667)eV다. 계산용 정확한 값은 dyadic energy/Fraction과 부모 K interval에 결속한다.

고정 proper V, 같은 양방향 Coulomb logarithm, 비상대론적·약결합 electron–electron Landau collision substep이다. 핵은 spectator이고 HI/HeI·외부주입·우주론 운반은 동시에 적분하지 않는다. Signature(-,+,+,+), proper seconds, W eV, F count/eV, cv=1380649/10681177560eV/K. K≈2.0738886541545980558e-10 eV^(3/2)/(s count).

Full Maxwell pivot plus signed correction의 소유권을 유지하지만 실제 해는 양의 labelled distributions로 진화시킨다. Pivot을 별도 bath로 더하지 않는다. 모든 reciprocal/tail-tail/nonlinear pair를 유지하며, 기존20kBT/FR source와 같은 물리해라고 부르지 않는다. 등방 IC와 등방 collision substep에서 radial reduction은 정확하다. 부모의 비등방 snapshot은 별도다.

## 2. 임의 radial 분포의 대칭 Landau 커널

고에너지 방향의 flux를 양수로 잡고, 원점 정칙성 및 무한대의 number/energy flux 소멸을 가정한다. F=sum F_a일 때

    S(W,E)=(2K/3)min(W,E)/sqrt(max(W,E))=S(E,W),
    D[F](W)=(2K/3)[W^(-1/2)integral_0^W E F(E)dE
                             +W integral_W^infinity F(E)/sqrt(E)dE],
    j_a=-D[F](F_a'-F_a/(2W))-K F_a/sqrt(W) integral_0^W F(E)dE,
    F_a,t=-partial_W j_a.

Maxwell 배경에 대입하면 부모 CP의 finite-temperature diffusion을 복원한다. s_a=partial_W log(F_a/sqrt(W))라 두면 동일식은

    j_a=-sum_b integral S(W,E)F_a(W)F_b(E)[s_a(W)-s_b(E)]dE.

E<W에서 S_E+S/(2E)=K/sqrt(W), E>W에서0이므로 부분적분이 두 표현의 동치를 준다. 실제 Wolfram으로 두 구간과 Maxwell 극한을 확인했다.

각 label count는 보존된다. Total energy의 미분 sum integral j_a는 (a,W)와(b,E)를 바꾸면 부호가 반대여서0이다. Labelled entropy H=sum integral F_a[log(F_a/sqrt(W))-1]는

    H'=-1/2 sum_ab integral integral S F_a F_b(s_a-s_b)^2<=0.

로그 안의 단위는 고정 reference amplitude로 제거하며 score와 결과는 변하지 않는다. Labelled entropy와 total-mixture entropy를 같은 함수로 두지 않는다. 이 식은 일반 Coulomb 문제의 모든 전역 정칙성 정리를 새로 증명한다는 주장이 아니다.

## 3. 형태 오차의 정확한 전파와 초기 온도계수

M_a(t)는 부모의 정확한 Gaussian moment path다. R_a=C_a(M)-M_a,t와 e_a=F_a-M_a를 두면

    e_a'=C(e_a,M)+C(M_a,e)+C(e_a,e)+R_a, e(0)=0.

수와 평균에너지 moment가 맞기 때문에 integral R_a=integral W R_a=0이지만 R 자체는0이 아니다. 따라서 delta U_a'(0)=0이다. 임의 배경B의 mean drift는

    a_B(W)=K[integral_W^infinity B(E)/sqrt(E)dE
                          -W^(-1/2)integral_0^W B(E)dE].

초기 Gaussian a_b와 I_ab=integral a_b R_a를 사용하면, smooth solution의 미분/적분 교환 아래

    delta U_a''(0)=sum_b(I_ab-I_ba),
    delta T_a(t)=t² delta U_a''(0)/(2cvN_a)+o(t²).

Reciprocal 항이 곡률의 total-energy 합도0으로 만든다. 반면 fixed q의 delta N_<q'(0)=sum integral_0^q R_a는 일반적으로0이 아니다. 온도만 보면 저에너지 분포오차의 선도항을 놓칠 수 있다.

### 전 에너지축 적분의 닫힌식

P_b(W)=erf(sqrt(bW))-2sqrt(bW)exp(-bW)/sqrt(pi), a,b,c>0에서

    L(a,c)=integral exp(-aW)P_c(W)dW=(c/(a+c))^(3/2)/a,
    Z(a,b,c)=integral W^(-1/2)exp(-aW)erf(sqrt(bW))erf(sqrt(cW))dW
            =2/sqrt(pi*a)atan sqrt[bc/(a(a+b+c))].

Z의 b,c 혼합미분은 양변 모두1/[2sqrt(pi*b*c)(a+b+c)^(3/2)]이고, 어느 인자든0에서 적분도0이다. s=a+b+c라 두면

    J=integral W^(-1/2)exp(-aW)P_b P_c dW
     =Z-2sqrt(bc)/sqrt(pi*s)[1/(a+b)+1/(a+c)]
                                  +2sqrt(bc)/(sqrt(pi)*s^(3/2)).

a=1/theta_a,b=1/theta_b,c=1/theta_c, c_ac=2KN_aN_c(theta_c/theta_a-1)/(sqrt(pi)theta_a^(3/2))에서

    integral a_b'j_ac
      =KN_b c_ac[-aJ-2b^(3/2)L(a+b,c)/sqrt(pi)
                        +2c^(3/2)L(a+c,b)/sqrt(pi)],
    I_ab=sum_c integral a_b'j_ac-theta_a' partial_theta_a Q_ab.

이렇게 모든 초기곡률을 사칙·sqrt·atan으로 평가한다.70자리 directed arithmetic과 positive half-angle/교대급수 remainder로 실제 입력에 대한 온도곡률 구간을 닫았다. 짧은 outward endpoints(K/s²):

    C [-1.538682052570294e-15,-1.538682052570291e-15]
    P [ 6.233938661956031e-18, 6.233938661956034e-18]
    S [ 1.504028654103486e-15, 1.504028654103489e-15]
    A [ 2.992348845895297e-14, 2.992348845895301e-14].

이는 초기 derivative interval이며 finite-time o(t²)를 포함하지 않는다.100000초에서 formal h² term은(-7.69341026e-6,3.11696933e-8,7.52014327e-6,1.49617442e-4)K다. 별도85자리 직접 integral 및 adjoint-integral 표현으로 대조했다. Fixed20theta_C0의 첫 count correction을 같은 시간으로 외삽하면+2.9836418e-5count이며 이것도 유한시간 상계가 아니다.

## 4. 실제 nonlinear kinetic 실행

x=W/theta_C0,s=Kt/theta_C0^(3/2)의 reflecting finite-band mesh를 사용한다. Cell density-of-states g_i=integral sqrt(x)dx, mean centre x_i, face z_i, gap ell_i를 사용하고 u_ai=n_ai/g_i, d_ai=(log u_a,i+1-log u_ai)/ell_i,

    m_ai=sqrt(z_i)LM(u_ai,u_a,i+1),
    J_ai=-sum_bj ell_j S(z_i,z_j)m_ai m_bj(d_ai-d_bj),
    n_ai'=J_a,i-1-J_ai.

Ideal logmean scheme에서 label mass, total energy, discrete Maxwell equilibrium이 정확히 보존되며

    H_h'=-1/2 sum_abij ell_i ell_j S_ij m_ai m_bj(d_ai-d_bj)^2<=0.

Zero cell에서 inward derivative가 비음수다. Prefix/suffix kernel 적용으로 RHS는 고정 label 수에서 O(N)이며 HPC 성능주장은 아니다. 시간적분은 stage-positive SSPRK2와 entropy acceptance다. 부동소수점 conservation과 시간오차는 따로 검사한다.

Initial discrete Maxwell의 inverse temperature를 조절해 각 원 count와 평균을 맞춘다. 이는 exact continuum cell masses가 아니며 projection difference를 기록했다. 초기 cell count에만1e-240 padding과 재정규화를 적용했다. 정규화 전 추가량은 label당Ncell*1e-240이하, L1 변화는 그2배 이하다. 이는 underflow 방지용 numerical representation으로, 진화 중 clipping은 없다.

같은 격자·같은 collision RHS를 Gaussian manifold로 투영한 새로운4moment control과 비교했다. 원 continuum moment producer는 반복하지 않았다.100000초 kinetic-minus-same-grid moment의 C/S/A 온도차와 fixed20theta_C0 count 차이:

|cells|delta TC K|delta TS K|delta TA K|delta Nbelow20|
|---:|---:|---:|---:|---:|
|128|-7.6558293e-6|7.4833363e-6|1.4920515e-4|2.9860192e-5|
|256|-7.6812982e-6|7.5084105e-6|1.4932453e-4|2.9842042e-5|
|512|-7.6876963e-6|7.5147135e-6|1.4935471e-4|2.9837077e-5|
|1024|-7.6890414e-6|7.5160411e-6|1.4935963e-4|2.9835944e-5|
|2048|-7.6897226e-6|7.5166100e-6|1.4936395e-4|2.9835633e-5|

P correction은약3e-8K로 매우 작고 subtraction roundoff에 민감하다.1024 약3.1402e-8,2048 약3.6413e-8이므로 그 고정밀 수렴을 주장하지 않는다. 표 전체는 finite-grid point calculations이지 continuum interval이 아니다.

2048grid absolute TCkin=101.3582325632548K, same-grid moment101.35824025297737K이다. 부모 continuum moment와의 spatial bias는 별도로 남는다. 가장 미세한 grid의 initial C projection L1은8.40830e-6count다. Same-grid pairing은 공통 편향을 분리하는 진단이지 continuum bias를 모두 인증하는 방법이 아니다.

2048grid의 final-mean-matched Maxwell에 대한 fourth-energy shape residual(C,P,S,A)은(-9.55973e-9,5.92754e-4,5.42571e-5,1.74781e-8)eV²다. 온도와 독립적인 형태 변화다.1024 CFL.4/.2의 deltaTC 차이는1.20e-10K, 모든 완료 경로는 양성이고 저장21시각의 최대 mass/energy drift는3.01981e-14count/6.73525e-13eV였다. Accepted entropy increment의 관찰최대는0이었다.

## 5. 아직 미완료인 전파 상계와 current

적절한 공간에서 ℒe=C(e,M)+C(M,e), -z'=ℒ*z,z(h)=psi를 두면

    <psi,e(h)>=integral<z,R>+integral sum_a<z_a,C(e_a,e)>.

실제 weighted kinetic stability/adjoint와 nonlinear remainder, finite-domain tail, initial/spatial/time/roundoff를 연결해야 finite-time continuum interval이 된다. Parent4moment L을 kinetic stability로 쓰지 않는다. 격자차이나 초기 t² 계수를 오차상계로 바꾸지 않는다.

이 Coulomb-only fixed-V symmetric source는 total free count3과 spatial current0을 보존한다. 따라서 동일 clock/volume의 Thomson current에는 내부 shape redistribution만으로 새 electron birth가 없다. General A=q.k,D=-u.k, cross-section-free column과 sigma exactly-once 계약을 유지한다. 원 ionizing/moving source의 관측량을 재발급하지 않는다.

## 6. 실제 검증, 문헌과 다음 실행

57개 새 formula/saved-result checks와13unit tests가 exit0을 반환했다. Actual cloud Wolfram15.0.1:16scalar zeros. Actual xTensor1.3.0:8tensor zeros, 공식 package hashes 일치.85자리 primitive/direct-integral 별도 경로,70자리 초기곡률 outward interval,5grid와1timecontrol을 포함한다. Same author plus separate CAS/arithmetic, external independent scientific review/native subagents NOT_RUN.

첫 missing-reciprocal 후보와 atan placeholder는 실제 assertion RED 후 동일시험 GREEN. 나머지는 tests-after다. JIT/time-budget 및 subnormal entropy/CFL 실패와 명시적 initial-padding repair를 보존했다. 추가 R60 domain 실행은 완료되지 않아 성공이나 domain convergence로 세지 않는다. Scalar 선행 draft와 실제 submitted script 전사를 구분하고 formal-symbol warning을 보존했다.

SciSpace/Exa에서 isotropic positive/conservative Landau 선행연구를 찾았고, Buet–Cordier DOI10.1137/S0036142997322102 및 Hirvijoki–Adams arXiv1611.07881의 primary abstract/metadata를 확인했다. 상세 미회수 정리를 현재 source certificate로 인용하지 않는다. 새로운 일반 수치기법 최초성을 주장하지 않는다.

HE49 full R4 at40659a752b9348fb7919cf5afcf42f310e05d064의 reference-bias/true-error 구분, HH66 full result atdb88ed7c4054094bcff62668bafc0fef927f559d의 norm/domain 제한을 구체적으로 재사용했다. REI117 상세PR head1865fcec018ba0d2478321c9c2fac39490669697의 abundance-history 목표와 미실행/optional tau를 보존했다. 다른 rate, inverse norm, warm data 또는 observer interval을 수입하지 않았다.

다음 SAME-node continuation은 `NT_KINETIC_CONTINUUM_TAIL_STABILITY`: 저장된 kinetic 경로의 continuum residual/tail 및 weighted propagator와 C(e,e) remainder를 결속한다. Old20kBT/FR, F/G/atomic/b-grid/globalREI와 CR/RCT/HH OFF는 그대로다. 전체 original source/cascade/native receiver/HPC, 외부심사, physical tau calibration, main merge 또는 permission change는 수행하지 않았다.
