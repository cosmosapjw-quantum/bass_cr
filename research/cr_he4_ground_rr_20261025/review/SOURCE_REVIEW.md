# Independent source and theory review: He4 ground RR consumer

Reviewer task: `he4_source_audit`. Observed 2026-10-25. This is a read-only source/theory review; no scientific suite, thermal quadrature, finite-chain solve, source regeneration, old primary, or publication was executed. Mechanical SHA and Git-blob identity checks were performed. No final implementation approval is implied before the implementation is available for review.

## 1. Authority actually inspected

The fixed CR handoff is commit `8d0a5c375589fbddadc2bb90c8117311c80bad09`, path `research/program_expansion_20261025/HANDOFF_KO.md`. The local expansion checkout was observed at this SHA. Root `AGENTS.md` was read. Existing H1 RR authority is PR105 Documents `b1aed87852d4f8994494c2ae41a913afd390eccd`, Science `bdfd34499153575305871bd68a139e2878f5f49f`.

Root confirmed that the central TASK_ASSIGNMENT selects only **He4+ ground -> He4 neutral ground singlet** for the new named unit. The He4++ -> He4+ entry below is independently verified candidate metadata, not an executed second channel. The selected unit reuses the existing H1-RR baseline. The independent source audit retrieved the actual REI151 code, frozen contract, and theory at `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`:

- `research/microphysics_r9_20261015/unit8_remaining_bridges_20261016/code/li_thermal_rates.py`, Git blob `815a3f9ca3d8ecad995c80814948632907390762`.
- `.../spec/LI_THERMAL_CONTRACT.json`, Git blob `7fb86947fe81496b84e32008c477d3fde52916b2`.
- `.../spec/LI_THERMAL_THEORY.md`, Git blob `93f6ab5903dbc1d33864d990c37d25c9c7560046`.

These sources explicitly bind HeI `chi_eV=24.59,saha_d=4` and HeII `chi_eV=54.42,saha_d=1`. The module creates historical quadrature nodes at import; it was read, never imported. Existing thermal validation is reusable within its original assumptions. Its separately failed BDF kinetics reference remains HOLD and does not erase the rate-block evidence.

C23B source was independently read at the inherited CR pin. Mechanical checks of the local bytes give:

| Object | Bytes | SHA256 | Git blob |
|---|---:|---|---|
| `spectral_photo_source.py` | 10712 | `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d` | `e7d474d5145cb264102206e0403b0aa5916c3140` |
| `verner_photo.dat` | 17760 | `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389` | `754b5ce11cbe662f96394430beeafe3f102f339c` |
| `source_providers/CONTRACT.json` | 3056 | `d589523758493c1f2f2aedec29d09a6a2c2cb8548cdba1a0f8996cd4ab221fe1` | `e40e4093ea56c2427cf3a79bd5d29ed6d2edad2e` |

The table's locally available preserved location is `research/cr_c23e_d43_source_binding_20261024/implementation/reuse/c23b/data/verner_photo.dat`. Its exact bytes match the H1 input manifest; no new fit was constructed.

## 2. Source-native channels and consumer mapping

| Recombination channel | PI product label | Source `(Z,N)` | Native I [eV] | Electronic g_bound / g_ion | d=2 g_ion/g_bound | Capturing density [cm^-3] |
|---|---|---|---:|---|---:|---:|
| conditional He4+ + e -> He4 ground singlet + photon | HeI | (2,2) | 24.59 | 1 / 2 | 4 | 0.02 |
| conditional He4++ + e -> He4+ ground 1s + photon | HeII | (2,1) | 54.42 | 2 / 1 | 1 | 0.01 |

All of the HeII target density is assigned to ground 1s in the selected frozen model. This level-population assignment should be explicit. The neutral ground product is the singlet; triplet and excited products require their own source channels. The bare target has no bound electronic level.

The exact photo-fit parameter tuple is `(I_eV,Emax_eV,E0_eV,sigma0_Mb,ya,P,yw,y0,y1)`:

```
HeI  = (24.59,50000,13.61,949.2,1.469,3.188,2.039,0.4434,2.136)
HeII = (54.42,50000,1.720,13690,32.88,2.963,0,0,0)
```

Do not replace these fitted thresholds with spectroscopic or reduced-mass energies while preserving the fitted coefficients. C23B's contract states that elemental labels do not establish isotope-resolved physical input. The He4 mapping is a declared conditional application, not an empirical He3/He4 equality result. Nuclear spin factors cancel between consistently counted states of the same isotope.

For E>0 in the stationary-heavy-target convention, epsilon=E+I and

\[
\sigma_{\rm RR,c}(E)=\sigma_{\rm PI,c}(E+I_c)
 \frac{(E+I_c)^2}{d_c(m_ec^2)_{\rm eV}E},\qquad
\lambda_c(E)=n_{{\rm capturing\ ion},c}\,100\sqrt{\frac{2 E\,{\rm eV_J}}{m_e}}\,
\sigma_{\rm RR,c}(E).
\]

Cross sections are cm^2, speed is cm/s, density is cm^-3, and the result is s^-1. The target factor is 0.02 or 0.01, never the thermal electron density 0.14. A bulk chemistry rate would have a distinct electron-density factor; it must not be inserted into a tagged-electron hazard.

Photon support is `I<=epsilon<=50000 eV`; the strict RR lower domain is E>0. Thus the source-specific kinetic maxima are 49975.41 and 49945.58 eV. Numerical/model validity still follows the selected nonrelativistic heavy-target approximation; the source fit's maximum alone is not a new physical accuracy certificate. The saved R80 grid is far below these maxima, but its actual E array must be checked without regenerating it. E=0 is outside the differential interface; no artificial rate floor is justified.

Use the preserved CR electron mass `9.1093837015e-31 kg`. REI151 used `9.1093837139e-31 kg`. At identical source and thermal constants, inherited thermal moments map by `(m_REI/m_CR)^(3/2)`; this is a numerical-convention mapping, not an isotope or finite-mass correction.

## 3. Physical interpretation of the HeI source

The author's [Verner photoionization collection](https://www.pa.uky.edu/~verner/photo.html) identifies ground-state smooth nonrelativistic fits. [Verner et al. 1996](https://arxiv.org/pdf/astro-ph/9601009), section 2, identifies the HeI input as the absolute Samson et al. 1994 measurements and section 3 discusses smoothing across resonances. The inherited adapter preserves that fitted model.

[Verner and Ferland](https://arxiv.org/pdf/astro-ph/9509083), section 2, explicitly use updated Verner fits for ground-level recombination. Therefore the inherited smooth-fit ground-RR interpretation has direct literature support. The same source distinguishes the state/channel information required for Milne inversion from total TOPbase PI data. [Nahar 2000](https://www.astronomy.ohio-state.edu/nahar.1/papers/nasa-atdtxray-snn.pdf), section 4, explains that the inverse relation uses PI resolved to the initial recombining ionic state.

Consequently, label this consumer as the **REI151/C23B adopted smooth ground-channel model**, with source residual-state resolution a conditional model assumption. The fit's ground initial atom label does not independently certify exact residual-HeII state resolution at every energy where additional channels open. This qualification does not require changing the fixed grid, discarding valid earlier results, or blocking a conditional consumer. A future physical state-resolved extension needs its own provider and admission. No quantitative correction for the unresolved branch was derived here.

## 4. Selected stopping map and future multi-channel bound

For the selected new channel, let K_H be the saved baseline including H1 RR and set `lambda_He=lambda_HeI`. HeI capture competes with existing H1 RR, q-entry and CE in one operator. A future separately admitted HeII capture would change this to `lambda_He=lambda_HeI+lambda_HeII`; the two-channel statements in this section address that future extension. Define

\[
K_{new}=K_H+\operatorname{diag}(\lambda_{He}),\qquad
p_c=K_{new}^{-1}\lambda_c.
\]

Summing separately killed H1 and He probabilities would not represent this common first-event process. After the first capture the tagged electron is stopped; its result does not evolve a subsequent He++->He+->He sequence or composition feedback.

The inherited positive rare-event inequality transfers to the **total added He hazard**. With `w=K_H^-1 lambda_He`, `eta=max(w)` and `p=K_new^-1 lambda_He`,

\[
\frac{w}{1+\eta}\le p\le w.
\]

For an individual channel use `w_c=K_H^-1 lambda_c`. The justified identity is

\[
0\le w_c-p_c
=K_{new}^{-1}\operatorname{diag}(\lambda_{He})w_c
\le \max(w_c)\,p.
\]

For a future extension adding multiple new hazards at once, the same multiplicative lower bound `w_c/(1+eta)<=p_c` is not generally valid for each species separately. Exact counterexample: `K0=[[1,-1],[0,1]]`, `lambda_c=(0,1)`, `lambda_other=(1,0)`. Then `Knew=[[2,-1],[0,2]]`, `w_tot=(2,1)`, `eta=2`, `w_c=(1,1)`, and `p_c=(1/4,1/2)`. At the first state, 1/4<1/3. This is a valid two-state transient serial chain. The counterexample is direct rational algebra, not a numerical replay or new no-go theorem. For the currently selected single added HeI channel, the inherited multiplicative bound applies directly.

## 5. Energy and population acceptance

For capture in channel c at kinetic E, the signed event changes are

\[
\Delta U_{fast}=-E,\qquad
\Delta U_{internal}=-I_c,\qquad
\Delta U_{photon}=E+I_c,\qquad
\Delta U_{recoil}=0
\]

under the explicitly fixed zero-recoil model. Each channel conserves energy. Charge conservation follows from removing one free electron and reducing the ionic charge by one; isotope nuclei are unchanged. A finite-mass extension requires consistent relative-frame cross sections, source thresholds, target motion, and momentum/recoil partition together.

Per-channel integrated rewards must retain distinct thresholds:

`R_photon,c = R_kinetic,c + I_c P_c`; `R_internal,c = -I_c P_c`.

Do not substitute one threshold for the sum of He captures, add the diagnostic kinetic-removal column again to deposited energy, or treat retained RR photons as heat. A scalar RR coefficient supplies no angular law. Photon momentum/direction, moving-target recoil, cascade, reabsorption and actual thermal assimilation remain separately bound interfaces.

Useful new adapter controls: positive finite E; exact source identity and all coefficients; density absence/null rejection distinct from explicit zero; correct charge/product orientation; d4 versus d1; wrong-ne mutation; source maximum and unsupported species rejection; finite outputs at the allowed support; exact event stoichiometry and sign ledger; common-operator channel sum; total-only rare bound; no reuse of an individual-channel lower bound disproved above.

## 6. Provider freshness and ownership snapshot

The latest six open PRs by update were queried in each provider repository. This bounded survey found these current heads:

| Repository | Expansion PR and SHA | Active source owner PR and SHA |
|---|---|---|
| WU088_HH | PR149 `34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad` | PR148 `2912a315aa39e7293000b7b2b8c7cc7a706fea9e` |
| rec_bianchi | PR138 `5dd414982c5c9ada97dfdfcc0b77cf83af86d66e` | PR137 `ea89c97abeb7a663a813f00e9aadddaf0b32a6a9` |
| BASS_HE | PR102 `c456b05e0f1c53faa3ae36720826f43e57c06a91` | PR101 `28a26f4db951ab9085180e2ecc5d600d981a1f71` |

The actual pinned expansion handoffs were read. No separate new active He-RR consumer appeared in this bounded query; no global absence is asserted. WU supplies species/reaction identities, elementary channels and nuclear branches; REC supplies level populations, spectra and radiation history; HE supplies differential collision/thermalization. CR consumes qualified payloads and owns external nonthermal distribution, injection/cascade/stopping. The seven-isotope initial view is extensible.

HE101 remains scoped 19/20 with C8 export OPEN, PASS/FAIL/FAIL and reserve0; no physical full joint event supplier is inferred. WU PHYS91 has B1 OPEN and exhausted primary/reference/Wolfram budget. REC PB01 is scoped complete while H5 physical epsilon and H6 trace remain open. None of these historical allowances transfer to this CR unit.

## 7. Review disposition

Source/formula contract: suitable for a named conditional smooth-fit He4 ground spontaneous RR consumer, subject to the explicit mapping and common-operator requirements above. Implementation and new numerical results require their own independent review. Existing H1/C23E results, N4/N5 PARTIAL_OPEN, N6/N7 predecessor gates, historical UNKNOWN_NO_ACK, prior failed attempts and cumulative budget must remain as recorded. Global physical completion and error bound remain null. The source review itself has no new scientific-run debit.
