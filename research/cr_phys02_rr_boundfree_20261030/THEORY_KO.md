# CR_PHYS02_RR_BOUNDFREE_ENVELOPE_V1 | 이론 R1–R10 | 2026-10-30

## 1. 질문과 고정 입력

PR125(`acf34ccb4229c002d9ad80a06a6d88cefb66d2fd`)의 PR110-source-derived, 100 K·proper seconds·고정 proper-volume density H I/He I ground RR 광자 원자별 `capture_{H,He}_bins_m3[4,3200]` 및 `photon_{H,He}_eV[3200]`을 보존한다. 원천 전자에너지나 H/He 결합에너지를 재생성·변경하지 않는다. 입자별 포착 수밀도는 각 시간구간의 *누적이 아닌 증분*이다.

- Frozen source ZIP SHA256 `8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e` (원래 PR110 ZIP은 동봉되어 byte identity 별도 보존).
- Photon atomwise NPZ SHA256 `e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f`.
- Photon summary JSON SHA256 `4a8cafd27bb78086842fc213fec6cc1f61dae0e62d3939c23be6df00fe32a538`.
- 범위: 외부 광장·원격 광자·He exclusive double-event 수용이 아니라 이미 태어난 H/He ground-RR 광자의 *지정된 가상 고정 흡수 매질*에서의 일차 상호작용 진단이다.

## 2. 원전 물리 데이터 (R2)

Verner, Ferland, Korista & Yakovlev (1996), ApJ 465, 487, DOI `10.1086/177435`, 저자 제공 `photo.dat`, Z=1,N=1(H I) 및 Z=2,N=2(He I) 두 줄의 1996 원전 계수를 `source/VERNER1996_HI_HEI_TABLE1.dat`에 전사했다. arXiv:astro-ph/9601009v2 p.4 Eq.(1), 확인된 부호는 **(x-1)^2**이다. v2의 정오표식과 혼동할 수 있는 (y-1)^2는 채택하지 않는다. FIT는 측정치 자체가 아니라 논문이 관측/계산 자료에 맞춘 물리 단면적 근사다. He I fitting은 Samson et al. (1994)의 절대 광이온화 측정에 기초한다. 유효 범위 각 `Eth <= E <= Emax=5e4 eV`; 현재 photon 최대 34.59 eV는 그 내부에 있다.

## 3. 정의/차원 (R3)

Photon energy E [eV], raw Verner fit parameters (Eth,Emax,E0,sigma0,ya,P,yw,y0,y1). Define

```
x = E/E0 - y0,
Y = sqrt(x*x + y1*y1),
F = ((x-1)**2 + yw**2) * Y**(0.5*P-5.5) * (1+sqrt(Y/ya))**(-P),
sigma(E) = 1e-22 m^2 * sigma0[Mb] * F  if Eth<=E<=Emax, else 0.
```

SI unit `1 Mb = 1e-18 cm^2 = 1e-22 m^2`. For the frozen PR110 inventory `n_H=140 m^-3`, `n_HII=1.4 m^-3`, `n_He=1085/94 m^-3`, `n_HeII=(1085/94)*0.01 m^-3`, `n_HeIII=0`, set `n_HI=n_H-n_HII=138.6 m^-3`, `n_HeI=n_He-n_HeII-n_HeIII`. Use *one frozen gas rest frame*, photon energies conserved in this model; no cosmological redshift or transfer to a boosted observer. Let `alpha_HI(E)=n_HI sigma_HI(E)`, `alpha_HeI(E)=n_HeI sigma_HeI(E)` [m^-1], `alpha=alpha_HI+alpha_HeI`.

## 4. 구성적 물리 단서 및 두 대안 (R4)

A. **Opacity-only**: atomwise absorption coefficient, target branching ratios and mfp `1/alpha`; entirely local and does not assume a transport distance. B. **Frozen ballistic finite-horizon envelope**: conditional extra model assumes stationary homogeneous neutral gas, straight-line light at physical c, only FIRST photoionization absorption, no scattering/expansion/cascade, observation at original source final proper time T=1e10 s. Do not invent birth-time distribution within any original time bin. New reported data include A and B with labels; B does not purport to be a native Bianchi cosmological transport solution.

## 5. 정확한 bin endpoint envelope (R5, derived)

For source channel q∈{H,He}, interval j with t∈[t_j,t_{j+1}] and nonnegative per-atom emitted count density `w_{qji}` in m^-3, set `s(t)=c(T-t)`, `tau_i(t)=alpha(E_{qi}) s(t)` and `r_a(E)=alpha_a/alpha` (when alpha>0; otherwise zero). Probability of first absorption by target a is `P_a(E,t)=r_a(E)[1-exp(-tau_i(t))]`. Its derivative w.r.t. t is `-c alpha_a exp(-alpha c(T-t)) <= 0`. Therefore

```
A^-_{qja} = sum_i w_qji r_a(E_qi) [1 - exp(-alpha(E_qi)c(T-t_{j+1}))]
A^+_{qja} = sum_i w_qji r_a(E_qi) [1 - exp(-alpha(E_qi)c(T-t_j))]
```

satisfy `A^-_{qja} <= A_{qja}(T) <= A^+_{qja}` for ANY nonnegative within-bin emission-time measure with the frozen counts. This is sharp at bin endpoints for the *particular channel-target sum* if the emission times for its atoms may be freely concentrated at either endpoint. The bounds should not be read as one simultaneously realizable full multichannel absorption configuration with different extremizing times; global all-lower/all-upper are consistent endpoint schedules (all atoms in each bin emitted at end/start respectively). Use numerically stable `-expm1(-tau)`. With `E>=Eth_a`, the first-absorption energy bookkeeping is exactly

```
U_abs = sum_{qji,a} E_qi * A_{qjia} * eV_to_J
U_ion = sum_{qji,a} Eth_a * A_{qjia} * eV_to_J
U_excess = sum_{qji,a} (E_qi-Eth_a) * A_{qjia} * eV_to_J
U_abs = U_ion + U_excess.
```

`U_excess` is **initial photoelectron kinetic-energy availability**, NOT actual deposited heat. Re-emitted recombination photons and secondary electron escape are not counted. `N_surv(T)=sum_i w_i exp(-tau_i(t))` lies between `N_emit - sum_a A^+_a` and `N_emit - sum_a A^-_a`, respecting the same endpoint choices. Heating/cascade/channel ownership beyond the first event remain unbound.

## 6. Adversarial limits (R6/C9 distinct-author NOT_RUN)

- If target densities are not stationary, cross sections are not applicable to gas rest frame, or E redshifts then endpoint path integrals use a time-dependent alpha and **these numerical B bounds do not apply**; they cannot be relabelled cosmological absorption probabilities.
- A source time-bin mean or center is not an observed emission time; use endpoint inequalities only.
- The PR125 threshold energies 13.60/24.59 eV are model labels that coincide with the Verner table's printed Eth; do not silently swap in more precise NIST thresholds.
- Source-count depletion of neutrals is negligible under this fixed source, but freezing densities is still an explicit model assumption, not a coupled solution.
- At E<24.59eV, sigma_HeI=0, so H-channel photons must have zero HeI-target absorption; at E<54.42eV, no HeII-target absorption via the present channels.
- R6/C9 is not completed by parent re-reading its own proof/code; default independent review remains HOLD.

## 7. Stage R7 onward / claim gate

An independently evaluated Wolfram formula/limits and Python negative cases support the finite model; the general endpoint inequality follows from monotonicity. `derived` = the endpoint theorem and energy ledger; `literature-supported` = Verner fitted photoionization cross sections; `numerically-checked` = source-driven concrete arrays after execution. Output is a conditional photoabsorption **envelope** with no physical cosmic optical depth, true absorbed-photon count, net species histories, deposited heating or production L4 claim.

The existing central DAG `28/88` and extension `0/3` must not change merely because a scoped sibling has new data. New scientific product counts as an independent auxiliary 1/1 upon concrete output/test/readback. Existing PR125 and PR126 remain Draft/review HOLD, PR118 resource fail, aggregate CPU certification NOT_CERTIFIED, true exclusive He kernel/K/clock/owner/stopping unbound. The next physical coupled owner may separately decide whether this data can be imported as a conditional response, not as a completed Bianchi transfer node.
