# C21M 독립 초기응력 builder 계약

## 완료한 구현과 범위

`builder.py`는 고정 REI PR147 source `3b85dedce84d37b3e165da00685a8a984950aafe`의 원 40성분 `CanonicalFVSpecies`에 signed full-Frobenius 초기좌표 `(S0,Pm0,Pr0)`를 결속한다. 원 `rhs`, `integrate`, DOP853, FP64, 24×12 Gauss3, L8, rtol=3e-11, atol=3e-13, z20→4와 101개 저장 시점을 유지한다. 초기조건 검증만으로 ODE trajectory 정확도를 선언하지 않는다. 새 실행은 외부 runner가 별도 run ID와 manifest를 부여한다.

source의 압력 변수 `Pi_X_J_m3`는 `p_X=(P_parallel-P_perp)/3`다. 동일 직교 normal frame에서 `pi_X=diag(-p_X,-p_X,2p_X)`, `sigma=diag(-s,-s,2s)`이므로 full norm은 각각 `sqrt(6)*abs(p_X)`, `sqrt(6)*abs(s)`다. proper-time H,s는 s^-1이므로 `K_t=8*pi*G/c^2=c^2*kappa_E`를 사용한다. `kappa_E*|pi|/(H/c)^2`와 같은 무차원량이다. half-contraction 값은 full 값을 sqrt(2)로 나눈 값이다.

## 분포에서 초기조건으로

원 massive 분포는 radial Fermi–Dirac weight와 `W_m=1+A_m P2(mu)`의 곱이다. `P2`의 구간은 [-1/2,1]이므로 `A_m∈[-1,2]`에서 비음수다. source는 각 A마다 packets, cell populations 및 reference energy normalization을 함께 생성한다. builder도 매 root trial마다 원 `CanonicalMomentumFV(30,A,24,12,gauss_order=3)` 생성자를 호출한다. 기존 분포에 amplitude scalar만 바꾸는 경로는 없다.

고정 A에서 초기 무전단 Friedmann 값 `Hbase`를 원 `fields`에서 계산한다. 실제 signed target `S0=sqrt(6)*s/H`로부터

\[
q=\frac{s}{H_{ref}}=\frac{S_0 H_{base}}{H_{ref}\sqrt{6-S_0^2}},\qquad
\Sigma_{ref}^{source}=\frac{\sqrt3|q|}{\sqrt{1+q^2}}
\]

를 사용한다. 이는 source 매개변수와 실제 초기 invariant를 구분하며, quadrature normalization의 부동소수점 편차도 실제 H에 반영한다. 허용 shear는 `|S0|<sqrt(6)`이다.

이때 원 pressure moment를 평가하여 `Pm(A)`를 얻고, 실제 A=-1 및 A=2의 signed bounds로 target을 검사한다. 범위 안에서는 brentq로 A를 결정한다. exact zero matter target은 A=0의 기존 tiny quadrature stress가 2e-13 이내일 때 원 isotropic 분포 A=0을 유지하고 실제 offset을 출력한다. raw stress를 잘라 0으로 만들지 않는다.

복사는 기본 입력 family에서 `k_gamma=k_nu=k`다. 두 species가 원 상태와 출력에 별도로 존재한다. 초기 monopoles는 1, quadrupoles는 k/5이며 원 source가 허용한 `|k|<=0.5`를 유지한다. k=0 및 0.5의 원 moment에서 radiation slope를 계산하여 Pr target에 대응시킨다. gamma와 neutrino 사이에 별도 자유도를 새로 추가하지 않았다.

총응력은 `p_tot=p_m+p_gamma+p_nu`를 만든 뒤 norm을 취한다. cancellation fraction은 `1-|p_tot|/(|p_m|+|p_r|)`이며 분모가 정확히 0이면 undefined로 저장한다. source에 없는 UV와 baryonic anisotropic stress는 각각 ABSENT_FROM_MODEL 및 UNMODELED로 표시한다. isotropic dust는 실제 모형 내 PRESENT_ISOTROPIC이다.

## 정확도 보존형 재사용

worker마다 원 energy/number/Thomson 행렬을 한번 준비한 뒤 readonly로 공유하고, 각 case는 새 momentum weight와 mutable source object를 소유한다. moment의 중복 표현 재사용은 C21L `ExactReuseMomentum`을 그대로 사용한다. A별 grid 생성 cache를 새로 구현했다고 주장하지 않는다. 원 `CanonicalMomentumFV`와 5개 A 및 3개 moment 상태의 bitwise 동등성, 원40성분 RHS와 3개 초기조건×3개 상태의 bitwise 동등성을 focused 검증했다. 실제 speedup/메모리 절감/64-core scaling은 측정하지 않았다.

## 실제 검증

`PYTHONDONTWRITEBYTECODE=1 python3 test_builder.py`의 6개 test group이 통과했다. FLRW/radiation-only/matter-only/opposing/mixed 초기축, positivity·에너지 normalization·Hamiltonian·보존량, source-domain endpoint와 불가능 target의 명시적 거부, direct tensor norm 및 SI 시간 변환, 공유 template 불변성을 포함한다. 초기 tests에서 원 integrator를 호출하면 실패하도록 막았으므로 ODE 적분은 0회다. 실제 receipt는 `checks/builder_checks.json`, stdout/stderr는 `builder_checks.log`에 있다. `global_error_bound=null`이다.

## 외부 결과 수용과 중복 제외

`EXTERNAL_UPTAKE.json`은 직접 확인한 source bytes·실행 영수증·선별 raw endpoint와 기존 독립 검토의 재사용을 구별한다. PR198의 606개 collisionless trajectories는 이미 실행됐다. PR213/BASS176의 729개 warm source-on cases는 같은 실행의 mirror이며 한번만 센다. REC116은 그 729개의 후처리, HH127은 A_m=0의 63개 control과 sector 후처리다. HE82는 확인 시점에 contract checkpoint이므로 proposed28 실행 완료로 수용하지 않는다. 기존의 원81을 포함하여 완료된 물리 입력은 새 sweep에서 제외한다.
