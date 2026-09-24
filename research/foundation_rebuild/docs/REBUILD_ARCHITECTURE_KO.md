# Surgical / radical rebuild 설계와 선택

## 1. 선택된 방향
물리모형의 전자수, Coulomb source, straight-line trajectory, 에너지 좌표는 유지한다. 재구축의 대상은 이산 representation–H–preparation–propagator–observable의 결합이다. 기존 frozen FFT/Strang 엔진과 R3M10–29 증거는 regression archive로 보존한다. 단순 cell-average patch를 주 production 전략으로 선택하지 않는다.

바로 재사용 가능한 surgical 결과는 true-H residual-stopped 준비 solver다. Fourier-Galerkin Coulomb 연산자는 단일 원자와 제한된 domain의 독립 기준으로 사용한다. Global3D box에 naive Toeplitz padding을 그대로 배포하지 않는다.

독립 scientific rebuild prototype의 우선 경로는 two-center cusp-adapted radial Galerkin이다. 이는 기존 AOCC 코드에 radial Gaussian 개수만 더하는 변경이 아니다. Full angular channels와 symmetric pseudocontinuum, 직접 D matrix, common observable가 함께 필요하다. 아직 해당 충돌 엔진을 완성/승인한 것은 아니며, 아래 시험에서 실패하면 실패한 cross-integral/representation을 특정하고 기존 h/dt 반복으로 되돌아가지 않는다.

## 2. Surgical S1: H-consistent preparation
현재 구현된 CPU 커널: ground_state_preconditioned(). Input은 immutable H_h action, grid mass norm, initial guess, residual tolerance와 max iterations. Output은 E, normalized state, true-H residual, iteration history 및 branch evidence. Preconditioner (T_h+1/2)^-1은 반복에만 사용한다. 기존 split state는 initial guess로 사용할 수 있으나 H eigenstate로 재표기하지 않는다.

Production extension은 CuPy/PETSc 등 backend로 action/preconditioner만 이식하고, state identity는 수치 결과와 새 receipt를 만든다. 과거 preparation bytes와 같은 이름으로 덮어쓰지 않는다. H operator digest, mass convention, dtype, boundary, kinetic dispersion을 receipt에 포함한다. residual alone은 state branch와 continuum preparation을 보증하지 않는다. 원래 B3의 시간 추정과 새 초기상태의 시간 추정은 별도 scope다.

## 3. Surgical S2: 실제 P_h V P_h
이산 kinetic K_h와 같은 기저에서 Coulomb matrix/action을 조립한다. 이번 exact cutoff Fourier transform은 검증 oracle이며 production long-range potential에 Rc=7을 무단 적용하지 않는다. 가능한 구현은 (a) actual finite-box matrix quadrature와 nonalias convolution, (b) singularity extraction + local atomic correction in the same variational space, (c) atom-patch enrichment + global interstitial representation이다.

필수 invariants: complex Hermiticity, weighted adjoint, dense-small/action parity, independently integrated Coulomb entries, static spectrum and subcell-phase dependence, nonalias Fourier differences, boundary consistency. Solver identity에는 basis and mass as well as V/T를 포함한다. 서로 다른 H의 두 numerical endpoints 차이를 temporal error로 이름 붙이지 않는다.

현재 Python embedded action은 cubic diagnostic이다. B3 anisotropic grid 전용 backend는 아직 없다. N=(350,300,600)의 padding=(700,600,1200)에서 complex128 배열 하나7.51GiB, 세 개22.53GiB. in-place/recompute/localization/distributed memory 등 구체적인 buffer plan과 actual peak/work-precision 없이24GiB GPU에 들어간다고 주장하지 않는다. 반대로 모든 변형이 불가능하다는 주장도 하지 않는다.

## 4. Radical R1: Two-center radial Galerkin의 수학적 인터페이스
Basis functions는 중심 A∈{T,P}, radial index j, l,m으로 분리한다. 각 중심의 atomic radial eigenfunctions/pseudostates를 공통 hp-FEM 또는 B-spline weak form에서 얻고 R_jl(r)Y_lm를 사용한다. 이동 중심에는 exp(i v·r-i v²t/2) ETF를 넣는다. n<=4 bound tests라면 최소 l<=3,m=-l..l을 포함한다. 이것은 초기 시험 범위이며 all-bound completeness 선언이 아니다.

데이터 타입:
- ModelSpec: electron_count=1, point nuclear charges, mass convention, trajectory, units. 물리모형 digest.
- BasisSpec: centers, radial knots/elements, polynomial order, lmax, retained negative states, positive-pseudostate window, quadrature rules. 기저 digest.
- OperatorSnapshot: S,H,D,W,time 및 각 독립 quadrature/adjoint error. D=B†dotB의 직접 미분값을 보관한다.
- State: coefficients, time, basis identity, weighted norm. 다른 representation의 state를 자동 reinterpret하지 않는다.
- ObservableSpec: physical center, Galilean convention, selected physical channel span, Gram matrix, final separation, units. n<=3 / all-bound / cross section을 별도 type으로 둔다.
- RunResult: 모든 위 identity, tolerances, first failure, scalar outputs, admitted scope, completed command receipts.

행렬:
S_ab=<χa|χb>, H_ab=<χa|T+VT+VP|χb>, D_ab=<χa|dotχb>.
i S cdot=(H-iD-iW)c, dotS=D+D†. W=B†Wphysical B positive semidefinite이면 norm derivative=-2c†Wc. 

무조건 symmetrization한 G로 unitary하게 만드는 것만으로 D를 검증하지 않는다. 직접 finite-difference basis derivative와 independent integral을 비교하며, metric identity/Cholesky derivative는 추가검사다. epsilon ladder에서 truncation/roundoff를 분리한다. rank loss를 eigenvalue floor나 숨은 channel 삭제로 덮지 않는다.

## 5. Cross-center quadrature의 bounded 첫 작업
다음 새 proposed node: FND_R2_TWO_CENTER_OPERATOR_PARITY_AND_BOUND_SPECTRUM.
첫 핵심 작업은 full collision이 아니라 작은 lmax=0→1→2→3의 S,H,D block을 독립적으로 조립하는 것이다. 두 중심의 separation과 boost를 분리해 측정한다.

(a) v=0,1s pair의 overlap은 exp(-R)(1+R+R²/3)와 비교한다. 이 공식은 boosted overlap의 정답이 아니므로 v≠0에서는 독립 quadrature가 필요하다.
(b) 각 isolated center spectrum n<=4와 m degeneracy, radial quadrature 및 domain refinement를 검증한다.
(c) physical H=0의 moving-basis 재표현과 이번 translating Coulomb exact finite-basis case를 수행하여 D의 anti-Hermitian 부분을 검사한다.
(d) target/projectile 중심을 바꾸거나 공통 rigid displacement를 준 경우의 equality를 확인한다. boundary가 같이 이동하는 경우와 box에 대해 움직이는 경우를 분리한다.
(e) 작은 frozen H에서는 dense exponential을 oracle로, 시간 의존 case에서는 독립 adaptive ODE를 보조로 사용한다. local time error만으로 전체 collision을 승인하지 않는다.

Positive-energy pseudostates는 양 중심에서 대칭적인 포함/확장 경로를 둔다. 예를 들어 Emax ladder2,4,8Eh를 사전에 선택할 수 있지만 이 수치들은 연구용 초기 후보이며 충분성이나 최종 budget을 뜻하지 않는다. basis growth와 continuum coupling을 nmax tail 하나로 대체하지 않는다.

## 6. Rydberg completeness와 asymptotic extraction
P_nmax는 selected projectile span의 Gram-corrected probability. 외부 핵의 finite-R field, outgoing propagation time, radial support, CAP와 nmax를 함께 바꾼 envelope가 필요하다. 고정 n-shell 내부의 unitary rotation은 총 shell probability를 바꾸지 않지만 다른 shell/continuum과의 mixing은 별도다. all-bound tail을 region probability의 차이 또는 마지막 shell increment로 자동 계산하지 않는다. 두 중심의 negative-state populations를 finite separation에서 그냥 더하지 말고 Gram/overlap identity를 기록한다.

Cross section은 2π∫bPcap(b)db. 먼저 same typed single-b observable의 내부 수치검증을 닫고, b quadrature와 b-tail 및 다른 energy는 분리한다. 새1% target을 덜 엄격하게 바꾸지 않으며 empirical envelope와 optional rigorous bound를 구분한다.

## 7. 다른 radical 경로의 위치
R2 atom-patch + interstitial plane waves: cusp를 국소 hp/B-spline patch에 맡기고 smooth part를 Fourier로 처리한다. 최근 IGA-PW/SIPG 연구는 static periodic full-potential 문제에서 근거를 제공하지만 moving two-center collision 구현·mesh velocity·connection·interface stability는 여기서 증명되지 않았다. 적분기/patch 비용이 two-center basis보다 유리한 경우의 대안이다.

R3 separable Coulomb weak integration: 1/r=(2/sqrtπ)∫_0^∞exp(-s²r²)ds를 사용하면 rectangular-box Fourier matrix entries가 세1D 적분의 곱으로 표현된다. Gaussian approximation을 pointwise soft potential로 넣는 것이 아니라 weak matrix integral의 quadrature로 사용한다. rank/large-s tail/finite-box errors와 시간에 따른 low-rank growth를 검증해야 하며 현재 구현하지 않았다.

현재 선택은 R1의 bounded cross-center prototype이다. 한두 static energies를 맞추도록 onsite Coulomb 상수를 튜닝하거나, trial ensemble에서 가장 잘 맞는 값을 생산 중심값으로 뽑는 경로는 제외한다.

## 8. 종료 조건
이번 분기에서 원래3% capture gap은 unresolved로 남는다. 종료된 것은 (1) 준비 고정점의 구조적 원인 판별, (2) cell-average-only 가정의 검토, (3) operator-consistent static improvement와 exact transport benchmark 구현, (4) radical 경로의 구체적 선택이다. 다음 결과가 cross-center kernel을 통과하면 그때 작은 공통 capture run으로 전진하며, 또다른 provenance-only 감사로 미루지 않는다.
