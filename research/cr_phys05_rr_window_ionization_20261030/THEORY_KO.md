# CR_PHYS05 | 실제 PR129 H/He RR 광자 기반 시간구간 이온·전자 탄생 장부

**증거 상태:** source byte VERIFIED; 이론 직접 유도 DERIVED; normal/-O Python 13/13 PASS; MP80 128 samples NUMERICALLY_CHECKED; native R06/C09 NOT_RUN; physical owner HOLD. 작성 2026-10-30.

## 1. 원본·연구 경계

기준 PR129 HEAD `76fac9178442ae5dc02b270d741b3ee1dcfa79b2`, 원본 SOURCE SHA256 `09b9c10bc50a3f00b6bba334e23565e867324f2112ee7906a543b3d2899bd64b` (6,067,061 bytes). 불변 PR125 original photon atomwise weights(3200 H + 3200 He photon energies; 4 source birth bins)와 PR127 Verner H I/He I neutral photoionization coefficients 및 PR129 original-source-bound observer 9 clocks 사용. 원래 H I 138.6 m^-3, He I 11.427127659574467 m^-3의 homogeneous 100 K, stationary neutral target, s∈[0,10^10] proper seconds. Source time-bin 안에는 개별 photon 탄생시간의 분포가 주어지지 않는다. 임의의 midpoint emissivity를 관측된 것으로 구성하지 않는다. No expansion/redshift/scattering/re-emission/ionizing feedback.

이 연구는 전자 하나를 방출하는 첫 광이온화 H I→H II+e 또는 He I→He II+e의 사건만 다룬다. PR129 single-photon event measure의 시간구간 버전으로, 실제 REI17/BASS21 동일 bath/rate가 아니라 별도 frozen-gas conditional data이다.

## 2. 수학적 이론: 직접 유도

σ_a(E)≥0 [m²], n_a≥0 [m^-3], κ(E)=c∑n_aσ_a [s^-1], β_a=n_aσ_a/∑n_bσ_b. 총 첫흡수 확률 F(s,T)=0 (s>T), 1−exp[−κ(T−s)] (s≤T). Window W_a=β_a[F(s,T1)−F(s,T0)] for T1>T0. 다음 piecewise 형태가 된다:

- s≤T0: β_a exp[−κ(T0−s)](1−exp[−κ(T1−T0)])
- T0<s≤T1: β_a(1−exp[−κ(T1−s)])
- s>T1: 0.

첫 구간의 dW_a/ds=+β_aκ exp[−κ(T0−s)](1−exp[−κΔ])≥0. 둘째 구간 dW_a/ds=−β_aκ exp[−κ(T1−s)]≤0. s=T0에서 함수는 연속이며 최대이다. 고정 원래 발생구간 [l,r]에서 **sharp** envelope는 W_a^max=W_a(clip(T0,l,r)), W_a^min=min(W_a(l),W_a(r)). W_a의 부호없는 공통 시간핵으로 인해 target별 minima/maxima는 동일 원자 시간 witness로 달성 가능하다. 원본 atom-wise w_{jic}≥0이므로 각 atom/시각 window의 source measure에 곱해서 합산해도 해당 window에서 sharp이다. 

**하지만 서로 다른 window의 극값은 단일 전역 emission-time history로 동시에 달성된다는 보장이 없다.** 따라서 ∑window W^max를 최종 누적 흡수 상한으로 사용해서는 안 된다. 별도의 earliest/latest/midpoint global-history witnesses로 직접 통합한 endpoint만 PR129 final과 비교한다. α=0에서도 W=0로 연장 가능하지만 locked source는 α>0이다.


## Limits
Bounds conditional on free within-bin birth times and stationary neutral opacity; no global common extrema of all windows.
