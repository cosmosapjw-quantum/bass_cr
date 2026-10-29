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

## 3. 계산 형태와 실제 물리 생성 데이터

관측 proper time 9점이 만드는 Δt=1.25×10^9 s인 8개 구간, photon energy 원래 범위에 맞춘 23개 1 eV bin, photon birth H/He, neutral target H I/He I. 736개 src×target×window×E 행 생성. 한 source target에 도달한 photon마다 HII 또는 HeII와 primary electron 하나씩 생성된다. 따라서 electron_birth=HII_birth+HeII_birth이고 no recombination reservoir update. 배출 photon energy E = target threshold I_a + primary electron excess E−I_a (not deposited thermal energy). Rate table은 **finite-window mean event number / proper time**, instantaneous owner photoionization rate가 아니다.

총 photon born `2.7294411246106446e-25` m^-3, original PR129 final first-abs bracket [6.5365599248361705e-27, 1.7193913666048540e-26] m^-3. Global latest/earliest witness interval sums exactly reproduce these parent endpoint numbers (binary64 rounding).

| proper window (Gs) | delta n_e lower (m^-3) | upper (m^-3) | primary e kinetic upper (J m^-3) |
|---|---:|---:|---:|
| 0.00–1.25 | 0.00000000e+00 | 1.06024887e-28 | 3.55483157e-47 |
| 1.25–2.50 | 0.00000000e+00 | 1.06024887e-28 | 3.55483157e-47 |
| 2.50–3.75 | 1.01021961e-28 | 7.79590840e-28 | 2.71106653e-46 |
| 3.75–5.00 | 9.86167064e-29 | 7.77056720e-28 | 2.70510255e-46 |
| 5.00–6.25 | 7.38481537e-28 | 2.46257585e-27 | 8.77491598e-46 |
| 6.25–7.50 | 7.21115889e-28 | 2.44428933e-27 | 8.72998443e-46 |
| 7.50–8.75 | 2.31434070e-27 | 5.50345581e-27 | 1.99871412e-45 |
| 8.75–10.00 | 2.26039684e-27 | 5.44667183e-27 | 1.98434453e-45 |

**중요한 비가산성 수치 반례:** 개별 window low 값들의 합 ≈ `6.233973637408e-27`, high 값들의 합 ≈ `1.762569015276e-26` m^-3인데, global final pointwise bracket [6.536559924836e-27, 1.719391366605e-26] m^-3와 다르다. Window-level extrema를 global integrated number와 혼동하면 물리적으로 존재하지 않는 광자 이력이 된다.

## 4. 소규모 feedback 규모 상한 (조건부)

**오직 photoionization-only closed box**에서 외부 중성종 변환, 추가 재결합, 다른 photon injection이 없으면 총 original photon birth Nγ보다 H I 또는 He I target 제거량이 클 수 없다. 따라서 n_a(t)≥n_a(0)−Nγ, opacity loss fraction ε_a≤Nγ/n_a(0). 원래 상태에서 ε_HI≤`1.96929374e-27`, ε_HeI≤`2.38856273e-26`. Positive σ로 κ(t)/κ0∈[1−ε,1] (ε=Nγ/min(n_a)), fixed E. 모든 광자 proper flight duration Δ에서 survival probability drift |Sdynamic−Sfrozen| ≤ ε/[e(1−ε)] ≈ `8.78703123e-27`. 이것은 아주 약한 **uniform diagnostic bound**, 실제 evolving plasma/opacity source evolution이나 photoelectron thermalization을 계산한 것이 아니다. e=exp(1)의 Euler number로 전자전하 e와 구분한다.

## 5. 실제 테스트 및 provenance

- 원본 PR129 ZIP SHA256, 40 member SHA/size, 41 ZIP entries CRC: 현재 turn 직접 PASS. 별도 원본 PR128 nested SHA도 검사하며 하위 PR125/PR127 원본은 부모 loader가 재검증.
- Python normal 13/13 PASS, Python -O 13/13 PASS, compileall PASS; corrupt-parent negative test 포함.
- MP80 (same-author independent formula): 128 original source atom-window endpoint/peak comparisons, max relative nonzero ~`0.00000000000000017537985097450073250237101274612426704421300568645791833464837569094068146882165`, not distinct-author review.
- Wolfram Language 1회: 구간 앞/뒤 미분 부호, T0 연결, 확률 차분 항등식 PASS.
- 실제 계산 736 스펙트럼 행/8 구간 총량/24 글로벌 witness. 원래 H-origin→HeI event=0, charged output stoichiometry, photon E=threshold+excess PASS.
- No new IVP. `NO_MERGE`, `AUTO_NEXT_NODE=false`.

## 6. 외부 문헌·근거 경계

- Verner et al. 1996, ApJ 465, 487, doi:10.1086/177435: original ground-state σ photoionization fits and author table https://www.pa.uky.edu/~verner/photo.html (actual source coefficients are frozen inherited bytes).
- Switzer & Hirata 2008, PRD 77, 083006, doi:10.1103/PhysRevD.77.083006: true cosmological He radiative transfer needs evolving neutral H I, scattering, line redistribution and background expansion. Our toy gas does not solve that.
- The microscopic first-ionization event law and time-window envelope above are directly derived here, not asserted as a novel primary-literature theorem.

## 7. DAG 및 다음 물리 관문

Central **28/88 delta0**; extension **0/3 delta0**; new physical data auxiliary **1/1 SCOPED_REVIEW_HOLD**. Distinct-author R06/C09 NOT_RUN; 18/20 local research stages scientifically eligible. physical K, exclusive He event kernel, real common-source evolving neutral inventory, angular radiative transfer, true thermal deposition, native25, L4 and production = HOLD. A central node cannot be promoted by inserting unrelated REI/BASS21 histories or by renaming rate envelopes. 

Candidate next scientifically meaningful node after independent reviewer gate: bind a genuinely shared proper-clock neutral history and absorption/emission photon source, then derive time-dependent opacity/radiation-event operator and compare with original BASS21 physical chemical event bookkeeping. Stop on mismatch, do not silently change source ownership.
