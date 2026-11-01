# BASS-CR → REI Bianchi IGM | 원본 BASS193의 저에너지 H⁺+H(1s) 공명 전하교환 용량

**연구 판정:** `SOURCE_CONDITIONAL_LOW_ENERGY_CX_EVENT_RATE_NUMERICALLY_CHECKED`, REI 중앙 DAG **28/88 (+0)**, REI working **33/88 (보고치)**, BASS-CR extension **0/3 (+0)**. 물리적 해석 범위는 **원본 BASS193의 frozen proper-time/ionization/temperature 이력에 대한 총 전하교환 사건률**이다. 새 REI EoR 진화, 실제 Bianchi finite tilt, 운동량·열 수송, 새로운 관측량 또는 canonical 노드 수용이 아니다.

## 1. 원본 입력 및 재사용

* Original BASS193: `cosmosapjw-quantum/rei_bianchi` PR #311 (HEAD `63052797e382b438ef375e8389f539118a7e2a0c`), 보존된 REI_F4_CCC... ZIP SHA256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52`. CSV 네 개의 개별 SHA256 검증과 193-epoch/192-interval clock match. ZIP 원본을 수정하지 않음.
* 같은 원본 전자 상태의 CR-OFF Thomson consumer는 `bass_cr` PR #153 (HEAD `ac2ed86c8b59fe7c7b5e78b0716c6c4d4677072e`)에 존재. 이 결과는 그 consumer에 **추가되는 선택적 CR rate capacity**이며 원래 CR-OFF 기준 계산의 선행조건이 아니다.
* 원래 독립 `bass_cr` R3M10은 100 keV/u 단일 b의 NO_GO. 이 고에너지/미수렴 결과를 eV IGM에 외삽하지 않음.

**Published physical input to the CX approximation:** Titova, Izmodenov, Korolkov (2025), *PASA*, “Effects of angular scattering and H+p, H+H collisions...”, Appendix A Eq. (A4), fitted to Schultz et al. (2016), *J. Phys. B* 49 084004, DOI `10.1088/0953-4075/49/8/084004`. Formula as published:

\[
\sigma_{cx}^{fit}(g) = \big[A-B\ln(g/[1\,\mathrm{cm\,s^{-1}}])\big]^2,
\quad A=1.87618291\,10^{-7}\,\mathrm{cm},\ B=8.28949260\,10^{-9}\,\mathrm{cm}.
\]

Original Schultz et al (2016) computes integral/differential quantum cross sections at `10^-4`--`10^4 eV` center-of-mass. Distinguishable-particle separation becomes less secure at slow relative speeds; the 2025 paper compares errors ~5% at 2 km/s and describes better validity above 3 km/s. **We neither acquired nor checked the underlying 1301-point numerical raw table**; a published fit is a literature-supported input, not direct primary tabulated-data replication. Analysis deliberately uses `3 <= g <= 200 km/s`, reports the fit-weighted missing low-speed fraction separately, and **does not infer a complete rate** in cold bins.

## 2. From microscopic charge exchange to REI-compatible physical state

Resonant channel: `H+(p)+H(1s) -> H(1s)+H+(p)`. If both distribution functions are Maxwellian at the **same** original `T_BASS_saved_K`, zero mean relative drift,
\[
\mu = m_pm_H/(m_p+m_H),\quad a(T)=\sqrt{2k_BT/\mu},
\]
\[
k_{cx}^{[g_-,g_+]}(T)=\frac{4}{\sqrt\pi a^3}\int_{g_-}^{g_+}g^3e^{-g^2/a^2}\sigma_{cx}^{fit}(g)\,dg.
\]

Here `g_-=3e5 cm/s`, `g_+=2e7 cm/s`. The upper choice negligibly affects the thermal tail for the original 100--12000 K source; the lower cutoff is essential for fit/quantum-distinguishability interpretation. This **uses the BASS gas scalar T as a kinetic closure**: the actual proton and neutral velocity distributions, relative drift and angular differential CX scattering have *not* been source-matched.

As an analytic numerical cross-check, integrating the **unbounded fit** (clearly nonauthoritative outside domain) over the entire Maxwell distribution yields
\[
\langle\sigma g\rangle_{\mathrm{all\ fit}} = \frac{2a}{\sqrt\pi}\left[
\big(A-B\{\ln(a/[1\,\mathrm{cm\,s^{-1}}])+\tfrac12(1-\gamma_E)\}\big)^2
+\frac{B^2}{4}\big(\tfrac{\pi^2}{6}-1\big)
\right].
\]
The coded integral, after fixing `quad`'s **absolute tolerance** for \(k\sim10^{-9}\,\mathrm{cm^3/s}\), matches this independent closed form at 100--12000 K within relative `3e-10`. The **all-fit** value is shown only to expose unsupported speed weight; it is **not an admitted full physical rate**.

The BASS193 source densities are exact source definitions:
\[
n_H(z_j)=10^{-6}n_b(z_j)[n_{H,ref}/n_b]_j\quad[\mathrm{cm}^{-3}],\;
 n_{p,j}=n_{H,j}x_{HII,j},\;
 n_{HI,j}=n_{H,j}(1-x_{HII,j}).
\]
\[
\nu_{cx,HI}=n_p k_{cx},\quad\nu_{cx,p}=n_{HI}k_{cx},\quad
\Gamma^{cx}_{events/H}=n_Hx_{HI}x_{HII}k_{cx}.
\]
`Gamma_events/H * Delta t` is **frozen-at-interval-end exposure**, NOT \(\int n_Hx_{HI}x_{HII}k\,dt\), NOT a realization of collision counts, and is not summed as a physical integrated history. For an expansion-clock diagnostic, \(H_{\mathrm{eff},j}=\ln[(1+z_{high})/(1+z_{low})]/\Delta t_j\); the ratio \(\nu_{cx,HI}/H_{\mathrm{eff}}\) is **not an inferred momentum drag rate**.

## 3. Measured-from-source numerical facts (model, not observations)

* Exact frozen BASS193 source: **192 rows**, `T_BASS_saved_K` approximately **100--12000 K**.
* **109/192** intervals have at least 95% of the **all-velocity fitted model rate weight** inside `3--200 km/s`. Ten are 50--95%; **73** have less than 50%, i.e. cold-source missing-speed sensitivity dominates. These percentages are model-integral coverage, **not** cross-section uncertainty or guaranteed physical accuracy.
* Max **frozen-end event exposure** `6.462852166958264 per H` at interval #69, `z_low=9.33024529994081`, `T=126.9327356246 K`, `xHII=0.6688092406`, but model speed-window coverage is only about **33.98%**. **Do not claim** the physical total collision exposure is 6.46; the cold-regime cross section and actual within-bin trajectories are not established.
* Within the 109 model >=95%-covered bins, max frozen-end exposure ≈**0.51635565274867 per H** at `z_low=7.963732801243164`. This is still a model conditional capacity, not a realized number.
* Max \(\nu_{cx,HI}/H_{eff}\approx2.75595\times10^4\) in hot, highly ionized snapshots: a neutral-encounter timescale diagnostic only.
* Original REI and BASS scalars are not new CR thermal feedback. The original optical-depth CR-OFF baseline in PR #153 is still an independent source input.

### Chemistry/energy/transport claim boundaries

For the **resonant ground-state label exchange** reaction, event stoichiometry has exactly zero change in total `H I`, `H II`, electrons and H binding energy:
\[
(\dot n_{HI},\dot n_{HII},\dot n_e,\dot u_{binding})_{cx,\mathrm{direct}}=(0,0,0,0).
\]
Thus there is **no direct** reionization chemistry or Thomson electron-depth source. This does **not** imply zero momentum or kinetic-energy exchange if proton and neutral distributions/tilts differ. A correct Bianchi 1+3 momentum/heat source requires an angular differential CX kernel (and elastic p+H) with actual species distributions. **The total-event cross section must not be substituted for the momentum-transfer cross section**. In equilibrium with identical Maxwell distributions the reversible collision operator vanishes, but the saved single gas T is only a closure, not proof of that state.

## 4. Blind-referee findings and implementation status

1. **BLOCK_NOW / actually repaired:** SciPy `quad` default absolute tolerance ~1.5e-8 is above the requested ∼1e-9 cm³/s rate and produced false low-precision answers. Fixed with `epsabs=1e-25`, relative `2e-11`; independent analytic all-fit vs direct quadrature test guards against regression.
2. **BLOCK_NOW / correctly scoped:** Published 2025 **total** charge-exchange fit is an approximation and below 3 km/s species distinction becomes problematic. Do not invent low-T full rate or silently extend Lindsay--Stebbings 5 keV threshold to eV IGM.
3. **BLOCK_NOW / correctly scoped:** BASS193 `T_BASS_saved` and `xHII` are source-owned, but no independent proton/neutral distribution, differential scattering kernel, actual Bianchi tilt or native REI production IVP has been supplied. The result cannot become `RUX13` completed or `C0/C1A` momentum source on these facts.
4. **REAL REI mission:** Unlike previous PHYS22--25 Lyα conditional expansions, this research explicitly maps the collision process to the *specific* REI ion/neutral state, identifies zero chemistry and the missing finite-tilt kinetic source contract. Do not automatically launch PHYS26 new atomic scattering cascades.
5. **VALIDATION STATUS:** Python unit tests and independent source clock/chemistry crosswalk are actual checks; no native subagents or distinct-author referee used. GitHub CI / external byte-restoration require their own results.

The smallest next source-backed BASS-CR physics unit is to obtain **original angular differential p+H resonant-CX and p+H elastic data at the IGM velocity range**, then construct \(\sigma_{mt}(g)=2\pi\int (1-\cos\chi)\, d\sigma/d\Omega\,\sin\chi\,d\chi\) and the actual two-fluid exchange operator on a **BASS-owned finite-tilt matched source state**. Only when REI source/clock and BASS geometry match should this become an optional REI owner `RUX13` sensitivity, not a forced CR-ON baseline.

**REI central 28/88 (reported) Δ0; Working 33/88; BASS-CR extension 0/3 Δ0.** `PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false.`
