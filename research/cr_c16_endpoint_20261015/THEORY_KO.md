# C16: 양의 시간가변 photon source–opacity 적분과 이온화 문턱 event splitting

## 1. 보호된 물리적 범위

C15 parent Git identity ad1441a97cd0c755cd8bdac8ede80900906764a8.
읽기 전용 rei_bianchi source HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
Owner Scenario/Spectrum/C8/Verner 입력은 C11 SHA-256 검사로 고정한다.
c=29979245800 cm/s, proper time s, physical photon E in eV,
species proper n in cm^-3, photons per original hydrogen nucleus.
Bianchi-I background metric signature (-,+,+,+). 테스트 q=-0.01,0,0.01.

이번 단계의 authoritative 계산은 **기체 ion fraction을 고정**하고
proper number density nH(a)∝a^-3, photon E(a) Bianchi-I redshift와
analytic owner Scenario.rate(a)만 바꾸는 국소 time-dependent
photoabsorption/source 문제다. 공간별 SOURCE07 flux, frame R*J,
원래 H/He thermal recombination feedback은 여기서 계산하지 않는다.

## 2. 연속식과 exact local affine-source/affine-opacity formal solution

각 고정 에너지/방향 channel k에서 photons per original H의 ODE:

    dN/dt = S(t) - lambda(t) N(t),
    lambda(t)=sum_{j in HI,HeI,HeII} c n_j(t) sigma_j[E(t)].

한 proper interval h에서 species rates가 각각 affine,
lambda_j(t)=lambda_{j,0}+(lambda_{j,1}-lambda_{j,0})t/h,
source S(t)=S0+(S1-S0)t/h라고 정의한다.
t=0..h에서 old photon exact optical depth는

    tau_total=h*(lambda0+lambda1)/2.

변수 u=(h-t)/h는 photon generation endpoint에서 거꾸로 잰
시간 분율이므로, born source contribution은 정확히

    N_source = h ∫_0^1 [S1+(S0-S1)u]
       exp{-h[lambda1*u+(lambda0-lambda1)*u^2/2]} du.

N_end=N0 exp(-tau_total)+N_source.
S0,S1,lambda0,lambda1>=0라면 N_end>=0이 보장된다.
전체 species photon lost count= N0+h(S0+S1)/2-N_end>=0.
시간가변 species 별 branching integral은 또 다른 적분이므로
현재 코드의 양의 opacity fraction 할당은 number-preserving
APPROXIMATION, exact species kinetics가 아니다.

## 3. Fast endpoint weighted exponential formula

Known constant-lambda source survival weights:
phi1=(1-exp(-tau))/tau,
phi2=(tau-1+exp(-tau))/tau^2.
S0 and S1 survivor coefficients are phi1-phi2 and phi2.

Mean backward emission age in a constant-opacity survival measure:
w(tau)=1/tau-1/[exp(tau)-1].
Wolfram CAS derived for tau>0 and expanded:
w(tau)=1/2-tau/12+tau^3/720-tau^5/30240+...
and w(tau)~1/tau for tau>>1.
Therefore the positive effective species opacities may be chosen as

    lambda_eff,j=lambda1,j +w(tau_total)(lambda0,j-lambda1,j).

With tau_eff=h sum_j lambda_eff,j, the old photons decay using
the EXACT affine total optical depth tau_total, and the source
uses h[S0(phi1(tau_eff)-phi2(tau_eff))+S1 phi2(tau_eff)].
For smooth data and h→0 this is second-order locally, with
endpoint weighting becoming dominant at large opacity, *provided*
the opacity/source endpoints are themselves consistent smooth values.

This FAST method is not uniformly high accuracy when lambda1=0
and lambda0 is very large (the true source boundary layer width
then scales as 1/sqrt(lambda0)). A deliberate test preserves this
counterexample rather than calling endpoint-weighted exact.

## 4. Positive optical-quadrature reference

Use x=s*u with s=max(1,h lambda1,sqrt(h lambda0)).
The exact affine source integral becomes an exponential-weighted
quadrature over x∈[0,s]:

 N_source=h/s ∫_0^s [S1+(S0-S1)x/s]
 exp{-h[lambda1*x/s+(lambda0-lambda1)x^2/(2s^2)]} dx.

For high opacity, positive 64-point Gauss quadrature is evaluated
only over x∈[0,min(s,80)] after verifying the neglected tail
is exponentially small on tested finite domains. This is
NUMERICALLY CHECKED rather than a universal interval-certified
bound at arbitrary positive lambda. Stable expm1 and series handle
small optical depths. Matched independent SciPy adaptive integrals
at lambda endpoints [0,0], [2000,0], [0,2000],
[2000,1000], [1e5,1e5] etc. agree to ~2e-11 relative
or better within tested domains.

Total photon absorption is allocated positively using the
old rate midpoint fraction for existing photons, and
endpoint-weighted rate fraction for the newborn loss. This
guarantees overall number conservation and nonnegative species
events but is not an exact species-wise time-variable opacity integral.

## 5. New owner Verner threshold-crossing result

The actual Verner fits set sigma(E<th_j)=0, and at the physical
threshold energies chi=[13.60,24.59,54.42]eV the cross-section can
jump from zero to a positive number. A naive smooth affine opacity
over a temporal cell that STRADDLES chi fails in the strongest
source/opacity settings.

Manufactured independent ray-channel benchmark:
- Owner Scenario.rate(a), H(a,q), proper density nH(a)∝a^-3,
  He/H number y, fixed gas fractions (.9,.85,.15), and actual
  Verner HI/HeI/HeII functions.
- Five photon energy labels at a0=.1: E=[14,20,32,70,90]eV,
  mu_birth=[-1,-.5,0,.5,1]. Photon energy E(a) follows
  the exact owner Bianchi-I direction ratio from the anchor.
- Emission at each epoch fills the five fixed ray channels.
  This is a manufactured source-channel convention, NOT
  full SOURCE07 age-resolved source energy redistribution.
- Independent SciPy Radau in continuous log a for this identical
  defined model (rtol3e-11, atol1e-15).

The 14 eV channel crosses the HI 13.6 eV threshold at
a_cross=.1*(14/13.6)=.10294117647058823 for q=0.
For q≠0 use Brent root of E(a)-chi=0 with physical Bianchi ratio.
Insert every detected threshold crossing as a temporal subinterval
edge, evaluate lambda_j from the INSIDE one-sided limits.
Crucially iterate over ALL newly split intervals; initial code
mistakenly still iterated the original n and omitted the final
time interval, producing a misleading first-order result.
The code was corrected and the invariant was regression-tested.

Actual q0 maximum relative photon-survivor error vs independent
Radau with 64-point optical quadrature:

 base time intervals   unsplit     threshold partitioned
 8                     8.6987e-2   4.4329e-5
 16                    8.9697e-3   1.1677e-5
 32                    9.3880e-3   2.9210e-6
 64                    9.6808e-3   7.32e-7
 128                   1.989e-4    1.84e-7
 256                   3.443e-4    4.6e-8

The threshold-aware 2nd-order convergence ratio holds for q=-.01,0,+.01.
This establishes accuracy for the DEFINED frozen-ion-fraction,
source-channel Bianchi-I ODE, not a complete REI EoR history.

## 6. Optimization boundaries

For 4096 actual-owner physical photon energies, two vectorized
algorithms cost different amounts and have different accuracy.
C16 FAST endpoint vs positive optical quadrature measured
approximately 0.819ms vs 10.93ms (3-trial medians).
The worst packet-level difference may be >100% near a species
threshold, hence a faster method must not be selected purely on
runtime. Both preserve the same photon ledger.
3 independent signed-q Radau+threshold experiments via
OS spawn 3-process scheduling measured 1.47s median vs 3.06s
for one process, with exactly the same emitted numerical outputs.
No claim on CMB observables, full Grackle/Rust solver or GPU speed.
No local Codex used; native subagent NOT_RUN.

## 7. Unresolved physical integration

- True owner SOURCE07 R*J current-frame radiative intensity and
  age-resolved spatial ray support, photon birth energy channels.
- Full photoionization species-wise time-variable branching
  and temperature-dependent H/He recombination OTS/thermal cooling.
- Branch-threshold root robustness for arbitrary changing angular
  tetrads, rapid negative shear and multimodal spectra.
- Independent physical EoR ionization/time histories and error budget.
Production/AX08/AX11/AX12 scientific admission HOLD.

Literature:
Mellema et al. 2006, C2-Ray photon conserving optical depth
https://arxiv.org/abs/astro-ph/0508416 .
Friedrich et al. 2012 helium C2-Ray DOI
10.1111/j.1365-2966.2012.20449.x .
Norman et al. 2015 fully coupled reionization DOI
10.1088/0067-0049/216/1/16 .
Zingale et al. 2021 time-integrated temperature with reactions
https://arxiv.org/abs/2103.13193 .
