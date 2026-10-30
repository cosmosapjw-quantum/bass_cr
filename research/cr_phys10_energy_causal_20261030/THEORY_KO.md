# BASS-CR PHYS10 | 원본 RR 첫 광흡수 초기 광전자 운동에너지의 인과적 응답

**물리적 주장 범위:** 원본 PR134 SOURCE ZIP SHA256 `e77bb3b9f7a91f608841b39e0b9679703c7d1f4d50f929c7fb7f030dac175243`, PR134 immutable HEAD `9a79c8b618fae288aee3a6bebdb2b8a5afba9c67`. 중첩 PR133, PR132 및 원본 H/He spectrum을 변경하지 않는다. 현재 데이터는 100 K, 고정 중성 배경의 조건부 첫 광이온화 모델이다. **열침적, secondary ionization, full chemistry Jacobian, cosmological radiative transfer, He exclusive double ionization, physical K가 아니다.**

## 1. 출처와 컨벤션

- Metric signature `(-,+,+,+)`; proper time seconds `t`, `c=299792458 m/s`, original `n_HI=138.6 m^-3`, `n_HeI=11.427127659574467 m^-3`, `k_B`는 100K 원본 source의 상태 변수이며 새 열진화 방정식에 들어가지 않는다.
- Photon energy E in eV, conversion `1 eV=1.602176634e-19 J`. Thresholds follow original PHYS07/PHYS09 owner: `I_HI=13.60 eV`, `I_HeI=24.59 eV`. Source has 3200 H-origin, 3200 He-origin atoms and 4 birth bins; each photon atom has nonnegative weight `w_{ij}` [photon/m^3].
- `k_a(E)=c*n_a*sigma_a(E)`, `[k_a]=s^-1`, total k=k_HI+k_HeI. Cross sections and thresholds are the **unchanged original code's** Verner et al. (1996) fits. Reference: Verner, Ferland, Korista & Yakovlev, ApJ 465, 487, DOI 10.1086/177435, https://arxiv.org/abs/astro-ph/9601009.
- No spatial ray/geometry is inferred; fixed proper-second optical hazard is not an expanding-universe path.

## 2. 기존 PHYS09의 미분과 PHYS10 에너지 관측량

하나의 광자가 출생 시각 `s`에 에너지 `E`를 갖는다고 하자. `T>s`에서 최초 target a에 흡수될 확률은 `P_a(T|s,E)= k_a/k [1-exp(-k(T-s))]`, k=0 또는 T<=s 이면 P=0이다.

가상 로그-중성밀도 변분 `δ ln n_b(t)=λ 1_[u,v](t)`에 대하여 `L=max(s,u)`, `U=min(T,v)`, `Δ=U-L`와 `A=[exp(-k(L-s))-exp(-k(U-s))]/k`를 정의한다. `U<=L`이면 G=0; 그 외에는

`G_ab^[u,v](E,T|s) = δ_ab k_b A - (k_a k_b/k) [A-Δ exp(-k(T-s))]`.

이는 frozen-**baseline**에 대한 causal functional derivative이며 실제 `n_a(t)` evolution을 가정하지 않는다. k→0 극한은 원래 적분형에서 정의한다. `Σ_a G_ab = k_b Δ exp[-k(T-s)] >= 0`, off-diagonal `G_ab<=0`.

흡수 하나가 내놓는 **초기 광전자 운동에너지** `ε_a(E)=max(E-I_a,0)` eV를 정의한다. (실제 흡수가 있는 지원영역에서 E>=I_a.) 원본 photon j의 중첩으로

`N_a(T)=Σ_{i,j} w_ij P_a(T|s_j,E_i)  [m^-3]`,

`Q_a(T)=e_J Σ_{i,j} w_ij ε_a(E_i) P_a(T|s_j,E_i) [J m^-3]`,

`B_a(T)=e_J I_a N_a(T) [J m^-3]`,

`F_a(T)=e_J Σ_{i,j} w_ij E_i P_a(T|s_j,E_i) [J m^-3]`.

`e_J=1.602176634e-19 J/eV`이며 **event-by-event** `F_a=B_a+Q_a`.

새 PHYS10의 핵심 생성량은

`H_ab^[u,v](T)=e_J Σ_{i,j} w_ij ε_a(E_i) G_ab^[u,v](E_i,T|s_j) [J m^-3]`

및 `∂B_a/∂ln n_b=e_J I_a ΣwG_ab`; `∂F_a=∂B_a+H_ab`. 이는 단순한 absorption-number response가 아니라 spectrum-weighted primary-electron-energy response이다.

조건부 평균 `\bar ε_a(T)=Q_a/(e_J N_a)` [eV]는 N_a>0일 때 정의한다. 에너지 응답 H를 eV 단위 `H^(eV)`로 쓰면

`∂\bar ε_a/∂ln n_b=(H^(eV)_ab - \bar ε_a G_ab^summed)/N_a` [eV],

여기서 시간창 8개 전체 합을 사용한다. Birth-bin 시각은 earliest/midpoint/latest라는 **각각의 허용 witness schedule**로만 선택한다. 평균의 global extremum 주장은 하지 않는다.

## 3. 경계, 보존식 및 검증 계약

- H-origin photon `E<=23.6 eV < 24.59 eV`이므로 H-origin → He I 첫 광이온화 count/energy는 0.
- 9 observation epochs×3 birth schedules×2 birth origins×2 target×2 perturb-owner×8 windows=1728 causal energy rows; 27 time-ledger rows; 108 time-channel energy rows; final 368 1-eV energy-bin response rows.
- For every target and time: `F-B-Q=0` (within binary64 roundoff). For every response: `∂F-∂B-∂Q=0`. Number response is exactly the PHYS09 original (all 1728 row values).
- Conditional first-electron kinetic energy is *not* gas heating or energy deposition: collision/ionization stopping, opacity feedback, transport, electron-energy cap K and secondaries are unmodeled.
- Independent-author theory R06 and code C09 **NOT_RUN**. One author has checked alternative direct piecewise-hazard FD; this cannot be represented as a different author.

## 4. Convergence / limits

As T→s from above, `P_a,Q_a,B_a,F_a`→0. If `k_b=0`, `G_ab=0`; if no neutral is present at any energy, all first-ionization rates vanish. At times after the observation T, G_ab window=0. The `k→0` integral expression prevents 0/0 in the physical implementation. Energy dimension is eV/m³ before SI conversion and J/m³ after, not a dimensionless heating coefficient.

## 5. Reuse/provenance

All physics inputs originate from the nested original PR134 ZIP and its PHYS09 code's `original_source` loader, which in turn validates nested original PHYS08 and PHYS07 owner identities. No REI BASS193 state/clock is mixed. The exact 1996 Verner source justifies the *existing* opacity fitting family; it does not independently validate an invented new radiation bath. This unit is new scoped physical auxiliary data 1/1 REVIEW_HOLD, with central DAG 28/88 and extension 0/3 unchanged.
