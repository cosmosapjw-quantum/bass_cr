# C12: 물리적 방출률 가중 age 및 H/He-광자 국소 결합 연구

## Source, 정의, 단위 및 범위

Owner: rei_bianchi branch codex/rux-science-delivery-20261014,
commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315. C11에서 고정한
owner Spectrum/Scenario/Verner 소스 세 파일의 SHA-256을 그대로 검사한다.
서명 (-,+,+,+), 에너지 eV, proper time s, 기체 밀도 cm^-3, Hubble s^-1,
광자수 및 반응량은 original H nucleus당 수치다.

Owner가 명시한 source 함수 kappa(a)는 시간당 H당 photon emission이다.
dt=d ln(a)/H(a,q)이므로, source-age measure는

    dN_emit/H = kappa(a)/H(a,q) d ln(a).

a=1/21 에서 a=1/5까지 적분하며, 양의 Gauss-Legendre age 가중치를
생성한다. Owner의 MD14-parameterized source-rate 함수이다.
직접 관측한 개별 source들의 연속 방출 이력이라는 주장은 하지 않는다.
방출 E_star=13.6..100 eV의 photon은 owner의 source-age/direction
ratio로 E_received=R(a,q,mu)E_star를 부여받는다. Angular 적분은 owner와
같은 12-point Gauss, source energy는 threshold-split 16-point Gauss다.
전체 기하학적 source R*J transport Jacobian은 여기서 별도로 적용하지
않으며 owner의 수송 계산을 대체하지 않는다.

## 보존형 photon-chemistry 결합

광자 packet k의 점유수를 I_k (photons/original H), 입사 물리 에너지를 E_k라 둔다.
HI/HeI/HeII species j에 대해 sigma_j(E_k)는 cm^2, n_j는 proper cm^-3이고

    tau_kj = c dt n_j sigma_j(E_k)
    dot I_k = - c I_k sum_j n_j sigma_j(E_k).

동결 gas 구간의 정확한 photon loss는
    Delta A_kj = I_k (1-exp(-sum_j tau_kj)) tau_kj/(sum_j tau_kj)
이며 tau 합이 0인 경우 극한값 0을 쓴다.
각 packet에서 sum_j Delta A_kj <= I_k 이고 모두 비음수다.

y=nHe/nH, xHI,xHeI,xHeII,xHeIII는 nuclei별 분율이다.
    dot xHI = -dot A_HI
    xHII = 1-xHI
    dot xHeI  = -dot A_HeI/y
    dot xHeII = (dot A_HeI-dot A_HeII)/y
    dot xHeIII = dot A_HeII/y.

전자는 x_e=1-xHI + y (xHeII+2 xHeIII), 기체 열에너지는
    U_th/H = (3/2) k_B T_g (1+y+x_e).
흡수 광자 열원은 종별 photoelectron 에너지 E_k-I_j를 곱한다.
총 광자 손실 에너지 = 결합 에너지 저장 + 기체 열 증가이다.
Wolfram은 hydrogen nuclei, helium nuclei, electrical charge conservation을
3개 ionization stoichiometry column에 대해 정확히 0이라고 검산했다.

## Time integrator and spectral reference

Frozen opacity는 매 단계 시작 gas로 exact photon exponential을 적용하므로
국소 coupled ODE에 대한 1차 정확도다.
Midpoint는 폐기할 half-step photon predictor로 mid gas를 평가하고
원본 photon에서 full exponential absorption을 다시 평가한다.
각 discrete full step의 photons/thermal/binding 에너지 보존은 정확하며,
실제 8/16/32/64/128 step과 별도 DOP853 동시계 ODE의 비교에서
frozen order ~1, midpoint order ~2가 측정됐다.

Age 16/32/64 Gauss에 대해 owner의 별도 source QUADPACK 적분을 비교했다.
Emitted-energy는 3개 source epoch q=+.01에서 SciPy QUADPACK으로 독립
적분하며 각도 Gauss 규칙은 공통이다. 이 교차검사만으로 angular
연속적분 또는 실제 thermal source physics의 에러를 증명하지 않는다.

## Positive source-age compression: constructive SVD nullspace

Age response matrix A의 각 열은 1(normalization)과 1 또는 3개
training gas의 8반응 모멘트로 만든다. Owner emission weights w0>=0으로
A w0 = b가 자명하게 feasible하다. Near-dependent 행 때문에 HiGHS가
가끔 false infeasible을 보고하므로 tolerance를 늘리는 대신 SVD null
direction v를 구해 w->w+lambda v를 수행하고, 비음수 경계에서 가중치
한 개씩을 정확히 0으로 만든다. 매 단계 전체 모멘트 잔차를 보존하도록
구성하되 마지막 원래 A에 대한 relative training error를 측정하며,
1e-10 숫자 구현 tolerance 초과 시 ERROR를 낸다. 세 signed q에서
SVD 축약 1-state 8 ages, 3-state 13 ages를 얻었다. Floating precision
근사이므로 모든 실수 source-history에 대한 정확한 정리로 승격하지 않는다.
이 알고리즘은 유한 모멘트 positive-measure 축약의 기존 원리 적용이다.

Zero-weight age의 photon packets를 실제 배열에서 제거해 packet 배열
memory와 반복 reaction tensor 비용을 줄인다. Source가 알려진 덕분에
가능하며, 현재 source의 모르는 hardened child moment를 발명하지 않는다.

## Scalar Bianchi angular parity

Owner의 axisymmetric photon energy ratio는
R/R_iso=sqrt(exp(2 beta)(1-mu^2)+exp(-4 beta)mu^2).
Wolfram 결과 d(R/R_iso)/dbeta|_0 = 1-3mu^2 및 이의 mu 평균 0.
등방 초기 source, 각평균의 scalar response, 미분가능성 범위에서
tracefree anisotropy linear term이 소거된다. 방향 관측량이나
일반 source 비등방에도 이 결론을 자동 확장하지 않는다.

## Scientific limitations / gates

이 연구는 과거 광자가 z=4까지 UNATTENUATED로 도달했다고 놓는
분리된 국소 photon reservoir surrogate다. 따라서 xHI(z=4)=0.7 등
초깃값은 controlled COUNTERFACTUAL이지 관측적 inference가 아니다.
재결합, helium recombination cascade, secondary ionization,
source emission after start, prior opacity, cooling, expansion temperature
work, actual anisotropic photon transport는 포함하지 않는다.
H(z=4)~1.38e-17 s^-1에서 8e10 s의 Hdt~1.1e-6으로, 이 효과의
관측오차는 C12의 작은 수치 compression difference보다 클 수 있다.
SOURCE07 C8 / AX08 / AX11 / AX12 원래 admission은 HOLD다.

Primary references:
Friedrich et al. (2012) MNRAS 421 2232-2250,
doi:10.1111/j.1365-2966.2012.20449.x (H/He photon-conserving
multifrequency and stronger T-step restrictions).
Baumschlager, Shen & Wadsley (2024) A&A, Spectral reconstruction for
radiation hydrodynamic simulations of galaxy evolution (HeII thresholds).
Vikas et al. (2013), Radiation transport modeling using extended
quadrature method of moments (positivity/realizability motivation only).
