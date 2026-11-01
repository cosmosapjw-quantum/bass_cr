# BASS-CR original REI F05 | full 46k-cell Cen92 vs Scholz–Walters91 cooling physics

Date 2026-11-02 KST. One **new source-owned full-support closure sensitivity** on ORIGINAL accepted F05 tick160/131072, frozen source read-only. Project `cosmosapjw-quantum/bass_cr`; immutable parent Draft PR162 exact HEAD `7c6c0c4a9d025dc72a80de6bddf2865cb68690b4`. Original REI source owner PR356 exact HEAD `cc1929982948265f6d0b0f699353b3170ccd1792`. Source-free new files only. CR-OFF original unaffected, production HOLD, no merge, force-push, changing thermal code, numerical tolerance, or new native IVP.

## Verified physics and primary evidence

The original F05 reduced 26-event H/He/thermal RHS includes the Cen92 H excitation cooling `n_e n_HI Λ_Cen`, coefficient SHA256 locked `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36`. Scholz & Walters (1991), doi:10.1086/170587, independently derive electron-impact H cooling rates, optically thin, fit valid over 2000–1e8 K. Exact published comparison/coefficients are Glover (2015), doi:10.1093/mnras/stv1781, equations (34)-(36). Literature labels Cen expression as *Ly-alpha cooling*; the prior BASS-CR #162 positive 2p-vs-legacy remainder is a model difference, NOT an identified measurement of 2s or higher level. No atomic 2p emission source is added or altered here.

**Original physical input:** real 46,080-cell private `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz`, SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`, extracted *accepted tick160 columns* N_H/N_He/N_e/x_HII/Tgas and native read-only original proper cell volumes through existing SHA-locked `native_caseb_lya.native()`. Source temperature full interval **2096.669755618253–66261.76097099554 K**, inside BOTH fits with no extrapolation. Native original microtick `4871848749.16828` s. Source NUMERICAL interval widths are not atom-model error estimates.

The two-model source energy rate is `Q_C=NH(1−xHII)*Ne/V*Lambda_Cen(T)` versus `Q_SW=NH(1−xHII)*Ne/V*Lambda_SW(T)`. Thermal energy `U=(3/2)k_B T*(NH+NHe+Ne)`, model-only frozen local response `δlnT=−dt*(Q_SW−Q_C)/U`. This treats original cells as an ideal shared-temperature monatomic bath; it is not a new trajectory, photon escape, Ly-alpha occupation, energy-conserving recombination/Compton ledger update or actual output spectrum.

### New original-source physical results

| Observable/diagnostic | Source-verified result |
|---|---:|
| Original cells, no source-domain exclusion | 46080/46080 |
| Cen92 original H excitation cooling sum | 3.228248858135368e39 erg/s |
| SW91 alternate H cooling sum | 3.4012753342571914e39 erg/s |
| Signed model difference (SW minus Cen) | +1.730264761218236e38 erg/s |
| Signed integrated model ratio minus one | +0.05359762636817389 (5.359762636817389%) |
| One frozen original proper tick energy difference | 8.429588212670994e47 erg |
| Local SW/Cen ratio min..max (midpoints) | 0.9341831051087838..1.6257210112925125 |
| Source cells SW > Cen; SW < Cen | 36000; 10080 |
| Sign-uncertain interval cells | 42 (not 42 independent simulations) |
| Largest abs frozen first-order delta lnT, midpoint | 7.306574024911232e-6 |
| Largest abs upper enclosure of first-order delta lnT | 7.82200519956613e-6 |
| Number of cells abs midpoint delta lnT >2e-4 | 0/46080 |
| Number of cells abs midpoint delta lnT >2e-6 | 1116/46080 |
| Number of cells midpoint model response greater than original tick161 PREVIEW midpoint thermal change | 6/46080 |
| Same comparison robust across source intervals | 0/46080 |

All cells use original accepted tick160 data, not an invented temperature or background. **The original candidate tick161 remains NOT ACCEPTED.** The historical V1 shared-parent independent-endpoint numerical gate `2.1245050576368385e-4 > 2e-4` is still FAIL; source-scoped V2 `5.387144148931529e-6` is a *different discrete comparison* that cannot authorize V1's failed historical record. The physical frozen two-model response `~7e-6` is not either numerical error estimator. The relative cooling rate 5.36% is not a total IGM heating/age/CMB observable uncertainty.

### Implementation and verification

`cooling_spread.py` consumes exact private input and owner source in READ-ONLY mode, validates SHA + source shape, source count, native proper volume, units/signs, original clock, source native code identity, analytical monotonicity and signed interval enclosure; writes ONE `REI_ORIGINAL_F05_CEN92_SW91_46080_DERIVED.csv.gz` with **derived-only physical model power/response** (no raw T, NH, NHe, Ne, V, xHII or preview delta), plus `RESULT.json`. Numerical result records are from 46,080 original cells, not 3 copies. Numerical stability tests establish original coefficient positivity/interval overlap with one-sided conservative arithmetic; no MPFR-directed-rounding global theorem claimed.

`test_cooling_spread.py` executes **13/13 normal**, **13/13 python -O**, including Wolfram five temperature reference ratios, independent 60-digit Decimal evaluation of log-polynomial rates, analytic derivative-domain extrema, source SHA negative check, 46k source/order/range and nonpromotion, signed interval, power/moment sums, and 46k cold deterministic readback. Repo's existing NumPy2.4.2/Pandas optional NumPy1 extensions may log ABI stderr diagnostics, but actual new source and tests exit 0. Hostile self-review found critical claim separation: modeled cooling source difference cannot close a discrete numerical admission criterion and source intervals cannot be promoted to atomic error bars. Distinct-author referee NOT_RUN; native subagent NOT_RUN; GitHub CI status only if independently checked.

Original private source never committed. The source-free dataset/report/standalone code+tests are published on an independent Draft PR only if final commit/push receipt confirms. Cite exact future HEAD, backup hash and provider status from real output, never from planned values.

## PhysMath R/C execution receipt and authoritative DAG

R1/R2/R3 objective/source/reuse and closure domain; R4/R5 constructed two source-matched cooling/response equations and interval form; R6 cross-model sign counterexample, atomic-uncertainty claim and formal monotonicity; R7 Wolfram source ratio plus 46k direct diagnostic; R8 explicit supported/nonauthoritative separation; R9 compute contract; R10 theory checkpoint `e918fe7962ed3e1d84dab15c78749b9411af0510`, pushed with cold-restored source-free theory backup SHA256 `b09a6fc7ac7376c5bd01feb621b426e2e0c8e1fe13292202ee90959e20759c57`.

C1/C2 actual frozen F05 source/baseline; C3 monotone envelope and signed power projection; C4 isolated branch and small bounded 46k original single dataset; C5 new source-locked generator; C6 13/13 normal and -O tests; C7 original H/He source and thermal/energy dimensional check; C8 deterministic gzip/JSON original re-execution and local checksum; C9 once-per-unit same-author skeptical audit of sign, interval, astrophysical use and leakage; C10 final source-free archive, Draft GitHub PR and copyable handoff are to be reported from actual receipts.

Central REI **28/88 (+0)**, working REI **33/88 (+0)**, physical-fast **4/7 (+0)**, BASS-CR extension **0/3 (+0)**. All are historical/reported DAG counts, NOT 46,080 extra completed nodes.

### Stop and positive next step

**STOP the repeated optional atomic closure fit comparisons after this single full-domain result.** It establishes the physical source's full-range sensitivity and pinpoints that two literature-based rate choices do not by themselves fix or invalidate the original [160,161] numerical gate. Original REI source owner must do versioned full 26-event photon/HHe/OTS/thermal source-clock and 14-ledger stage integration, original first64 replay and V2 worker admission; independent RUX02/RUX03 source-equal photon transport and geometry remain relevant. This BASS-CR track can only supply one nonduplicated physical consumer, cannot promote the 88-node central DAG itself.
