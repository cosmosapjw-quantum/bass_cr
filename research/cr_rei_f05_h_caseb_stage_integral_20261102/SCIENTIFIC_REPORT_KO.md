# BASS-CR → REI IGM | Original accepted H Case-B SDIRK source quadrature

Date 2026-11-02 KST. Original REI H/He 26-event / OTS, 46,080 material cells, REAL historically accepted intervals [0,64],[64,128],[128,160], proper microtick 4.87184874916828e9 seconds. Source-neutral parent BASS-CR PR164 exact HEAD `264ad0c1fd62f7ec799af14f273d9902a24ca6aa`. Original REI355 read-only SHA HEAD `70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00`. REC #195 source ZIP SHA `ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657`. Original kernel SHA `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. No REI/REC/BASS_HE worktree or source mutation.

## First actual original stage-rate H recombination integration

Original PDS event matrix is indexed `event.flux[cell,destination,source]`, with source-native `event.flux[:,0,1]` the **HII→HI Case-B recombination rate** and `event.flux[:,1,0]` the total source-native H-ionization rate (including original He-OTS H photoionization). 26-event recombination source is positive `N_HII × (Ne/V) × alpha_B,H(T)` [reactions s⁻¹]. We execute the original physical MPRK22(1)+Alexander SDIRK2 source for original full, two half-step maps, 3×3 original-certified steps, and use **the two half-step stage/final positive source fluxes**:
`Q_R = sum_{half h} h[(1-g)r_stage + g r_final], g=1-1/sqrt(2)`.
The interval is a **numerical source-stage quadrature range**, not a formal rigorous continuum-IVP event integral. Actual no phantom time steps, alternative rate fits, or synthetic photons. Only full-step diagnostic comparison, not a certified continuum truncation error.

| Original accepted source interval | Numerical H Case-B flux stage-quadrature [reactions] | Original H-ionizations quadrature [reactions] | PR164 conditional endpoint H recombination minimum |
|---|---|---|---|
| [0,64] | [1.0164433155051584e62,1.1065212641386639e62] | [1.6305795306557367e61,1.789221983329902e61] | 8.879746299967943e61 |
| [64,128] | [1.0163902747906035e62,1.1064677818668583e62] | [1.6654965468048833e61,1.8433360011930736e61] | 8.835204102163903e61 |
| [128,160] | [5.0820519050220345e61,5.532481951524329e61] | [8.537920316123963e60,9.505914814156858e60] | 4.381986121562681e61 |
| **Total** | **[2.5410387807979653e62,2.766237241157955e62]** | source sums separately in CSV | **2.209693652369452e62** |

Corresponding *gross H recombination binding-energy channel equivalent* is **[5.536185121860606e51,6.026827128244851e51] erg**, using original H χ=13.598434599702 eV and 1 eV=1.602176634e-12 erg. This is not thermal heating, net H/He binding change, direct 10.2-eV H Lyα photon luminosity, measured escaped line energy or a CR-on feedback.

## High-impact hostile-referee finding

The native two-half-step source quadrature of `ionization - recombination` is NOT exactly identical to the accepted MPRK positivity-corrected discrete state `ΔN_HII` **in every cell**. On original accepted interval 0→64, 45,744/46,080 cells' source flux quadrature `[∫I−∫R]` and original accepted HII endpoint-change intervals overlap; **336 do not**. Original positive source-signed gap of the 336 cells sums to 9.640425779725532e54 original HII counts, around 1.084858508048765e-7 of the total absolute original HII change and max local source-H-nuclei fraction 3.6925070450893135e-5. The *global integrated interval* does overlap. Other original accepted intervals [64,128], [128,160] overlap **all 46,080 cells**. 14 native ledgers include zero on the source maps; these are separately defined physical operator checks. This is a **discrete-map/source-quadrature equality caveat**, not a failed original MPRK gate and not evidence of a new global energy leak. Do not assert exact quantitative reaction events from these stage quadrature bounds without the scheme's event accumulation semantics. This finding was *kept*, not washed out by widening original physical tolerance.

Actual initial run with unpinned local NumPy2.4.2/pandas3.0.0 did not reproduce original accepted state bytes and STOPPED. Original owner source was not changed. A controlled replay with the existing REC195 original-matched isolated environment NumPy2.3.5/pandas2.2.3/SciPy1.17.0 regained exact original accepted state byte parity. Unchanged 9 maps and original full/half/two-half 14-ledger checks and no table events were verified. Optional system NumPy1 ABI warning printed during imports; source run exited 0. Original source-positive physical quantities are linked to exact pinned original time/site and parent H/He source geometry.

## Physics source and literature

Original source`event_uncertainty_operator.py` maps `_add(flux,0,1,r_hb)`; this is source-owned, not guessed from the observations. Original legacy BASS-CR #160 instantaneous Case-B rates, #164 endpoint necessary lower bound, and BASS_HE #151 actual He II Lyα original source are separate and must not be added to H gross energy. Hummer & Storey (1987), DOI 10.1093/mnras/224.3.801, Storey & Hummer (1995), DOI 10.1093/mnras/272.1.41, address Case-B line branching and its density/temperature limits. A source-integrated Case-B recombination event is not guaranteed to yield an escaped H Lyα photon (2s two-photon, resonant trapping, cascade/level population). No radiation occupation, Bianchi ray, CMB or optical depth computed here.

## Scope, validation and next action

Code `native_h_caseb.py` source-locks REI355 HEAD, REC195 full private source ZIP, 26-event kernel, exact three original primary REIADP1 endpoint SHAs, original proper time, full/half/half stage certification, 14 nuclear/photons/energy ledgers, original logT/HII gates 2e-4 and public width 2e-3, and exact accepted state arrays. Source-free output is ONE 3-row derived CSV + aggregate JSON. Full source raw array protected in original private provider; no original raw H/He state published.

Standalone source-free tests `test_native_h_caseb.py`: 9/9 normal and 9/9 Python -O on the pinned local source environment, including a synthetic sign/orientation check, positive stage weights, original source identity, conditional PR164 comparison, scheme nonoverlap diagnostic, no false photon/canonical admission. Native original source full code replay and byte readback are separately tested. A different-author independent referee or native subagent was not available: `NOT_RUN`; same-author hostile source mathematics and implementation reviewed.

**Canonical REI 28/88 (+0); working 33/88 (+0), physical-fast 4/7 (+0), BASS-CR extension 0/3 (+0).** Original accepted t160 only; t161 NOT_ACCEPTED. CR-OFF baseline unchanged. NO_MERGE/NO_FORCE_PUSH/NO_REI_MUTATION/PRODUCTION_HOLD. Exactly one source-owned bounded research unit; **STOP additional optional atomic / cooling / Ly-alpha atlases**. Next central path remains original REI versioned V2 3-lane [160,161] worker/runtime/source-clock with full 14-ledger and official ACCEPT/REJECT, then source-matched photon/geometry RUX02/RUX03.
