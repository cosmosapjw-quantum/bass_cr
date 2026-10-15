# C14: 재결합 전자밀도 중점화와 stiff photon-source 적분

## 출처와 연구 범위

기준 Git: bass_cr C13 eef456cd3f72b4d8c699e6454e04ed405099b436.
읽기 전용 기준: rei_bianchi 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
Owner source emission/age/scenario의 SHA를 프로그램에서 검사한다.
실제 owner igm_rates.rs의 HII/HeII/HeIII Case-A recombination
수치식을 유지한다. 기본 signature (-,+,+,+). Proper time s,
gas density cm^-3, photon number per original H, cross-section cm^2.

C13에서 source_scale=0인 상황에도 global first-order integration error가
발생했다. Source-scale>0과 매우 높은 opacity에서는 별개로 midpoint
photon birth가 실제 잔존 광자수를 거의 잃는 반례가 나왔다.
본 연구는 독립적인 두 numerical subproblem만 다룬다.

## H/He 재결합의 전자 feedback

HII fraction h=1-xHI, helium fractions he1,he2,he3와
y=nHe/nH에 대하여 electron abundance/H는

    xe = h+y*(he2+2he3).

T, proper nH,nHe 및 owner alpha(T)를 고정한 reaction substep에서
원래 C13은 ne=nH*xe(start)를 Markov rate에 고정했다.
Hydrogen only라면 이때 실제 nonlinear ODE는

    dh/dt=-alphaH*nH*h^2.

Wolfram에서 검산한 exact solution은
    h_exact(t)=h0/[1+alphaH*nH*h0*t].
기존 frozen-electron exponential approximation은
    h_old=h0 exp[-alphaH*nH*h0*t].
Wolfram Taylor:
    h_old-h_exact=-(alphaH*nH)^2*h0^3*t^2/2+O(t^3).
즉 local second order error 때문에 global first-order error가 생긴다.

새 알고리즘은 HII, HeII, HeIII 원래 Markov exponential을
유지하고 electronic rate를 다음 scalar implicit positivity
condition에서 계산한다.

    xe_mid=(xe_start+xe_end(xe_mid))/2.

순수 재결합과 positive initial state에서 xe_end는 xe_mid의
단조감소 함수이므로 고정점 root는 0..xe_start에 유일하다.
Brentq bracket solver를 사용한다. Numeric solver tolerance만
원래 정확성에 적합하도록 적용하며 물리 acceptance를 바꾸지 않는다.
H and He nucleus counts, charge neutrality, positive fractions,
and recombination photon escape/thermal ledgers are retained.
HeIII recombination count sign y*(he3_start-he3_end)>=0는 구현 중
한 번 실수로 반대로 작성되었으나 독립 positivity test에서 확인하고
수정했다. 어떤 이벤트의 음수량도 관용적으로 clipping하여
문제를 덮지 않았다.

Tested actual owner fluid with source=0, initial T=4000 and 9000 K,
a=.1..11, nsteps=8,16,32,64,128, independent DOP853:
old observed p approximately1.000..1.008;
midpoint observed p approximately1.999..2.000.
At T0=4000 n=8 old abs xHI error2.2630e-6, new1.2840e-8;
at n=128 old1.4061e-7, new5.0157e-11.

## Constant local source and opacity: positive Duhamel

A photon packet k has constant proper emission S_k >=0 in photons/H/s,
constant absorption lambda_k = sum_j lambda_kj >=0, dt>0.
Exact frozen-gas photon equation

    dot Nk = Sk-lambda_k*Nk

has time-integrated solution

    N1=N0 exp(-tau)+S_k*dt*phi(-tau),
    tau=lambda_k*dt,
    phi(-tau)=[1-exp(-tau)]/tau and phi(0)=1.

This comes from the exact Duhamel integral of uniform emission
inside a proper time interval, and Wolfram returned
integral=S*(1-exp[-lambda dt])/lambda with zero-opacity limit Sdt.
Taylor small-tau is 1-tau/2+tau²/6-tau³/24+... .
A dedicated stable function uses expm1 and small-tau series.

Species absorption is (N0+Sdt-N1)*(lambda_j/lambda_total);
for zero lambda, no species event occurs.
All event counts and photon survivors are nonnegative. Full packet
number ledger N0+Sdt=N1+sum_j absorbed_j is checked.

C13 midpoint-born approximation for a constant emitting cell instead has
    N1_mid=N0 exp(-tau)+Sdt exp(-tau/2).
If tau is very large, all newborn photons disappear artificially,
although real continuous emission maintains steady stock S/lambda.
This error does not require nonconservation of photon count.

At owner a~0.105 using proper HI/HeI/HeII and Verner cross sections,
E=13.61eV has per-step tau about 2308 for nsteps32 and about 72
for nsteps1024 across a=.1→.11. A manufactured constant source
total=.05 photons/H across five representative physical energies
gives exact 13.61eV stock 1.35382051398e-7/H. Midpoint-injected
source underestimates this surviving stock by ~100% throughout the
32–1024 step range. The Duhamel computation matches its independent
analytic constant-coefficient solution at roundoff.

This is a DIFFERENT subproblem from time-dependent gas opacity,
cosmological source hardening, photon direction/age R*J changes, and
the real rei_bianchi photon transport. Do NOT insert it as a naive
unconditional replacement of the actual SOURCE07 runtime.

## What remains unresolved

The pure RR 2nd order gate is checked, but the full C13 source+opacity+
temperature gas response still shows first-order-like convergence
even with midpoint ne, including a weak source case with T always
below the Rust 5500K RR coefficient branch. Thus that branch switch
cannot alone explain the remaining effect. Large optical depth,
birth-point placement and dynamic absorber time-centering need a true
coupled radiation/chemistry reference before physical admission.

Selected source papers:
Zingale et al. 2021, Practical Effects of Integrating Temperature
with Strang Split Reactions, https://arxiv.org/abs/2103.13193 .
Southworth et al. 2024, IMEX Runge Kutta radiation hydrodynamics I,
DOI 10.1016/j.jcp.2024.113339.
Friedrich et al. 2012, H/He C2-Ray radiation transport,
DOI 10.1111/j.1365-2966.2012.20449.x.
