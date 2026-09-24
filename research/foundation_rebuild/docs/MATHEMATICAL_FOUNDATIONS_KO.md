# 수학적 토대: continuum 문제와 이산 알고리즘의 분리

이 문서에서 수치 식은 원자 단위(a0,Eh,t_a)를 사용한다. 단위가 있는 식에는 ħ,m_e를 쓴다. 모든 실제 실험은3D/방사형 단일 원자 또는 작은 유한 기저 benchmark이며 production 충돌이 아니다.

## 1. 물리모형에서 유지할 것
고정 target와 prescribed straight-line projectile에서 H(t)=p²/(2m_e)-κ/r-κ/|r-Rp(t)|, Rp=(b,0,vt), κ=e²/(4πε0). 전자수1, target infinite mass, nuclear backreaction 없음. +κ/R(t)는 주어진 궤적 아래 전자 공간의 항등연산자에 곱해지는 scalar라 추가/제거가 global phase만 바꾼다. density와 fixed projector probability는 불변이다. 따라서 이 항 누락을3% h-grid 차이의 원인으로 간주할 수 없다.

이동 projectile 고유함수는 Φn^P(r,t)=exp[i m_e v z/ħ-i m_e v²t/(2ħ)]exp[-i Ent/ħ]φn(r-Rp(t)). 표본화 전에 이 continuum 식은 상수속도 단일 중심 TDSE를 만족한다. finite-band truncation에서는 multiplication by exp(i m_e vz/ħ)이 band를 이동시키므로 연속 boost invariance를 자동 보장하지 않는다. 핵 이동에 대한 coordinate-translation covariance는 별도 invariant다. keV/u의 질량은 m_u로 속도를 변환하며 proton laboratory kinetic energy와 구분한다. 이는 R3M9에서 이미 수정한 사항이다.

## 2. Coulomb과 splitting의 domain 문제
T=-(ħ²/2m_e)∆, 매끄러운 V에 대해 test function f에 직접 미분하면
[T,V]f=-(ħ²/2m_e)[(∆V)f+2∇V·∇f],
[V,[T,V]]f=(ħ²/m_e)|∇V|²f.
Coulomb 원점 밖에서는 |∇V|²=κ²/r⁴. 정확한 hydrogen1s에서 이 형식적 multiplier의 기대값은 원자 단위로
I(ε)=4∫_ε^∞ exp(-2r)/r² dr=4exp(-2ε)/ε-8Γ(0,2ε),
lim εI(ε)=4.
따라서1s에 대해 이 commutator form은 유한하지 않다. continuum Schrödinger H의 적절한 domain/자기수반성과 모순되지 않는다. 유한행렬에서 Strang의 잘 정의된 수렴도 부정하지 않는다. 다만 매끄러운 V에 대한 commutator norm 충분조건을 h에 균일한 bound로 그대로 옮길 수 없으며, 기존 fixed-h 시간 evidence를 새 공간표현에 자동 이전할 수 없다. 이 사실을 mandatory global certificate라는 영구 blocker로 바꾸지 않는다.

## 3. 준비 solver가 실제로 최소화하는 대상
Sτ=exp(-τV/2)exp(-τT)exp(-τV/2). normalize(Sτψ)를 반복하면 수렴 시 Sτ의 지배 고유벡터다. [T,V]≠0이면 Sτ≠exp(-τH)이므로 H 고유벡터와 달라질 수 있다. Baker-Campbell-Hausdorff에 따라 finite matrix에서 logSτ=-τH+O(τ³). iteration count만 늘리면 finite-τ bias가 남는다. 새 코드의 preconditioned eigensolve는 Hψ=Eψ를 직접 풀며 (T+1/2)^-1은 iteration preconditioner일 뿐 Hamiltonian 변경이 아니다.

상태 error로 residual을 전환하려면 고유 branch와 분리 gap이 필요하다. normalized ψ, r=(H-E)ψ이고 다른 spectrum과 E의 거리가 γ>0라면 해당 isolated eigenvector의 직교 complement 크기는 <=||r||/γ. 최적 global phase를 맞춘 state distance는 <=sqrt(2)||r||/γ라는 충분조건이 있다. 정확한 hydrogen gap을 다른 finite-grid H의 gap으로 몰래 대체하지 않는다.

같은 H,W>=0,CAP 및 같은 orthogonal Q에서 상태 차이 δ가 전파 후에도 지배된다면 |P-Ptilde|<=2sqrt(Ptilde)δ+δ². 다른 box/h/projector에 무조건 적용할 수 없다. 특히 이번 다른 box의 split-state distance를 기존 B3 capture 예산에 입장시키지 않았다.

## 4. 무엇을 평균하는가
Cubic kernel Kh=h^-3 1_{[-h/2,h/2]^3}, Vbar=Kh*V라 두면 Fourier에서는 Vbarhat(q)=Vhat(q)∏α sinc(qαh/2). Wolfram 적분으로 이 factor를 확인했다. 이는 potential 단독의 체적평균이며 ∫φi* V φj와 일반적으로 같지 않다. constant-cell basis에서의 mass-lumped potential과 Fourier basis의 Galerkin matrix는 서로 다른 연산자다. Cell averaging은 h→0의 같은 continuum model을 겨냥할 수 있지만 finite h에서 자동으로 variational 또는 고차 정확도인 것은 아니다. ∆Vbar=4πZKh이라는 smearing 해석도 가능하나, 이것만으로 모든 cell-average discretization을 physical-model 변경이라고 분류하지 않는다.

## 5. 비앨리어싱 Fourier-Galerkin
주기 box Ω의 plane wave |k>=Ω^-1/2 exp(ik·r). Vkl=Ω^-1∫Ω V(r)exp[-i(k-l)·r]dr. 미리 고정된 주기 potential의 rigid translation에는 Vkl(R)=Vhat(k-l)exp[-i(k-l)·R]. D_R=diag exp(-ik·R)이므로 H_R=D_RH0D_R†. 이 항등식은 임의의 연속 R와 고정 Fourier cutoff에서 성립한다. Collocation은 Fourier index difference를 순환적으로 식별하는 alias를 포함하고, cell 평균은 모든 alias를 없애지 않는다.

진단용 구면 cutoff V=-1/r(r<Rc),0(r>=Rc),Rc<L/2에 대해
Vhat(q)=-4π[1-cos(qRc)]/(L³q²), q≠0,
Vhat(0)=-2πRc²/L³.
코드는 cancellation을 피하도록 -2πRc²/L³ sinc²(qRc/2)를 사용한다. 이 factor는 Coulomb kernel의 정확한 Fourier transform이지 cell-average sinc filter와 다르다.

Toeplitz의 i-j는 [-(N-1),N-1]. M>=2N-1 길이의 circulant에 이 차분을 embedding하고 coefficient를 zero-pad하면 필요한 N개 출력에서 exact Toeplitz product가 된다. modulo-N convolution으로 대체하면 다른 H가 된다. 현재 CPU 구현은 arbitrary moving center를 D_R로 옮기며 dense assembly로 검증했다.

## 6. 이동 potential의 exact finite-basis 시간 기준
D(t)=exp(-ivKzt), H(t)=D(t)H0D†(t). c(t)=D(t)a(t)로 놓으면 i da/dt=(H0-vKz)a. 따라서 U(t,0)=D(t)exp[-i(H0-vKz)t]. 시간 의존 lab-frame exponential midpoint를 이 exact expression과 비교할 수 있다. -vKz를 빠뜨려도 잘못된 H0가 Hermitian이라 norm은 보존된다. 단위 복원 시 vKz는 v pz이며 Schrödinger exponential에는1/ħ가 들어간다.

## 7. 움직이는 비직교 기저
Ψ=B(t)c, S=B†B, H=B†HphysB, D=B†dotB일 때 iħS dotc=(H-iħD)c. dotS=D+D†는 norm consistency의 필요 identity이나 D의 anti-Hermitian 부분을 정하지 못한다. D→D+A, A†=-A는 같은 dotS를 주면서 실제 계수 역학을 바꾼다. 따라서 Sdot와 generator의 anti-Hermiticity만 확인해서는 충분하지 않다. 직접 B†dotB 또는 독립 exact transport benchmark가 필요하다. 기존 R3M17 metric tests는 유지할 가치가 있으며 이를 삭제할 이유는 없다.

## 8. Radical radial weak form과 한계
각 l에서 u=rR_l, u(0)=u(Rmax)=0. H_ij=(1/2)∫Bi'Bj' dr+∫[l(l+1)/(2r²)-1/r]BiBj dr, M_ij=∫BiBj dr. endpoint basis를 제거하고 원점을 포함하는 첫 element를 고차 다항식으로 표현한다. Gauss 내부 node에서 적분하는 것은 soft core를 넣는 것이 아니다. generalized Hermitian eigenproblem으로 exact hydrogen E_n=-1/(2n²), mass orthogonality, residual, virial 및 domain/mesh/quadrature를 따로 검증했다.

두 중심 충돌에서는 spherical symmetry가 사라지므로 이1D 비용을3D 충돌 비용과 비교해서는 안 된다. Cross-center integrals, angular coupling, moving D, pseudocontinuum과 common observable가 추가로 필요하다.

## 9. All-bound와 유한 separation
각 고정 n의 bound projection과 n→∞의 all-bound는 다르다. hydrogen orbital extent는 n²a0 scale이고 이웃 shell gap은 Eh(2n+1)/(2n²(n+1)²)로0에 모인다. 먼 핵의 uniform Coulomb term은 phase지만 다음 dipole perturbation은 energy scale Eh n²/(R/a0)²를 가진다. 이웃 n-shell gap과의 비는 대략 n^5/(R/a0)²로 증가한다. 이는 scale estimate이며 n<=3의 오차한계가 아니다. Degenerate n 내부의 Stark mixing은 같은 n 총 projection과 구별해야 한다. 그러므로 fixed Rmax/tf에서 nmax만 무한히 늘리는 것은 균일한 completeness 증명이 아니다. 이번 R64의 n5 spectrum 실패가 그 구조를 수치적으로 보여준다.

## 해석 상태
1–9의 명시적 유도는 derived, 각 작은 matrix/atom 결과는 numerically checked 또는 implementation-verified. 원래3% capture gap의 지배 원인 분해, continuum capture convergence, all-bound completion은 unresolved다.

## 10. FFT라고 해서 Coulomb cusp가 지수 수렴하는 것은 아니다
정규화한1s ψ(r)=(πa0³)^-1/2 exp(-r/a0). Fourier convention (2π)^-3/2이면 φ(k)=(2sqrt(2)/π)a0^(3/2)/(1+a0²k²)²다. 따라서 진폭은 k^-4. 무한공간에서 구면 cutoff K 밖의 kinetic 기여는
T_tail/Eh=(16/π)∫_{Ka0}^∞ u⁴/(1+u²)^4 du ~16/[3π(Ka0)³],
확률 tail은 ~32/[5π(Ka0)^5]. 각각의 prefactor와 전체 radial integral π/32를 Wolfram으로 검산했다. 이것은 cusp에 의한 algebraic ultraviolet tail이며 cubic finite Fourier eigenvalue 오차의 엄밀 bound나 capture probability 오차가 아니다. 특히 cubic cutoff와 spherical cutoff를 동일시하지 않는다. 물리적 Schrödinger 해에서 Tψ와 Vψ가 원점 근처에서 상쇄되므로 potential 셀 평균만 정밀하게 만드는 것으로 이 joint cusp 구조가 자동 보존되지 않는다.
