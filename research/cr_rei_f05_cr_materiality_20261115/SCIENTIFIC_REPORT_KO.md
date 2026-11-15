# BASS-CR → REI F05 | CR ionization-heating materiality threshold

**2026-11-15. Original 46,080 H/He/OTS cells × 4 accepted physical source epochs, 184,320 input records.** This is a source-matched *conditional activation criterion*, not CR-ON cosmological time evolution, an injected cosmic-ray spectrum, new RUX11/RUX13 admission, or an observed CMB quantity. Immutable BASS-CR parent PR166 `f990ed8cb66ba5687ef83fceb2699f43a2a8d964`; original REI PR367 source, read-only. Original REI V1 last officially accepted tick160/131072; V2 161–163 separate research-only. Central REI 28/88, working 33/88, Physical Fast 4/7, BASS-CR extension 0/3, all Δ0, CR=OFF and production HOLD.

## Provenance and exact source execution

- Original REI367 source-full ZIP SHA256 `d6d27a7d50a6e106739f1e45e95c41b8218bccba329cd2ce9220bef2ce2543a1`, original 184320-row source 20-field gzip member SHA256 `5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913`.
- WU088_HH R57 original augmented 27-field gzip SHA256 `d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e`, its source nine-event rate science JSON SHA256 `f2adab1ce52992f3da0096ce79acb68d3c65c57f304ab8628e2156d17ffd4cde`.
- Original sealed 26-event kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. Proper microtick `4.87184874916828e9` seconds.
- Source generator actually matches all original **20 columns as exact text on all 184,320 rows** (REI367 versus WU R57), checks 46k-node order, original proper clocks, H nuclei, HII positive cone, dNe stoichiometry, original total gas Udot and logarithmic temperature identity. Independent stdlib-only auditor re-read the same original 184,320 records and recomputed aggregate HII/heat/He-OTS source physics **PASS**. No original 184k-row source data in public Git.

## Constructive physical source results

Native original HII source `S_H=sum(dot N_HII)<0`, native Case-B `R_H=sum HII_CASE_B`, original direct H-ionizing event count `I_H,dir=sum HI_ION`; total HII creation `I_H,tot=R_H+S_H`, including original He-OTS ionization `I_H,OTS=I_H,tot-I_H,dir`. **The original nine-event direct HI_ION alone is not total H ionization.**

For neutral H atoms `A=sum N_HI>0`, a *hypothetical homogeneous effective CR H ionization hazard* `zeta_CR` [s^-1 per neutral H] and an *independently unspecified* heat yield `epsilon_heat` [erg/extra ion] give `delta dot N_HII=zeta_CR A` and `delta dot U=zeta_CR A epsilon_heat`. No physical CR source model is assumed or run. The source-point zero-net thresholds are `zeta_chem=-S_H/A`, the **2D heat materiality frontier** `zeta_CR epsilon_heat=-Udot/A` and at chemical threshold `epsilon_star=(-Udot)/(-S_H)`. HII binding `chi_H=13.598434599702 eV` and U heat are NOT the same energy term.

| Original tick | ζ_chem [s^-1] | ε_star [eV / effective extra ion] | Original He-OTS fraction of H formation | Neutral H atoms |
|---|---:|---:|---:|---:|
| 0 | 6.221590792959104e-13 | 9.406515542672588 | 0.8509734214398823 | 4.584453555493304e62 |
| 64 | 5.208749780227057e-13 | 11.237129866295321 | 0.7901381422967598 | 5.472699025181773e62 |
| 128 | 4.452012894008359e-13 | 13.009966715799045 | 0.7431472043190351 | 6.357538560213226e62 |
| 160 | 4.14761070259447e-13 | 13.853704950859028 | 0.7234572698332826 | 6.797721760048333e62 |

Total original H nuclei constant `5.523438018661132e66`, HII signed source `[-2.852259403160577,-2.850591984466439,-2.8303843644224617,-2.8194303525235783]e50` particles/s, total native Udot `[-4.298611455576868,-5.132167868879903,-5.89972808414696,-6.258030833149542]e39` erg/s. Source total H-ionizing hazard is `[1.198266613488094e-13,1.0064208586334021e-13,8.980868286889175e-14,8.561241269714769e-14]` s^-1, far above direct `[1.785735736109496e-14,2.112093510240958e-14,2.3067611271300017e-14,2.3675490343428965e-14]` s^-1 because He-OTS coupling is real source physics.

Native source gas internal energy `U=3 k_B T (N_H+N_He+N_e)/2`, so **extra ionization creates an electron**: `delta dot lnT=zeta_CR N_HI (epsilon_heat/U-1/Npart)` locally. Its zero-temperature-response local value is `epsilon_T=3 k_B T/2` per ion; neutral-weighted original values are `[1.9154613163863703,1.9820130088974464,2.0279294031884283,2.0456232986847414]` eV, local source range ≈0.271–8.566 eV. No additional extra electron work term can be added to the original total-U source.

## Independent hostile review, failures and limitations

The first consumer audit demanded original `native_thermal_rhs==Udot_thermochemical` byte equality and failed. This was **too strict**: the original scientific source has 68,427/184,320 float64-distinct but numerically consistent rows, maximum **relative** gap `7.057954912685918e-16`, consistent with original REI367 floating-point residual. A test now checks numerical agreement `≤1e-15`, while explicitly publishing original epoch differing row counts `[16992,16930,17212,17293]`. This repair changes no scientific source, solver or original gate. Source-only unit normal and Python -O **11/11 each PASS**; separate same-author independent stdlib-only audit recomputed 184,320/184,320 original source physical rows PASS. It is not a different-author blind referee or native delegated subagent: **NOT_RUN**.

No actual CR injection particle spectrum, cosmic-ray transport, local secondary electron yield, helium CR response, feedback propagation, CR pressure or escaped photons. These are snapshot GLOBAL threshold frontiers, not a statement that all 46k local cells change HII sign or a full continuous physically accepted REI trajectory. Literature: Leite et al. 2017 DOI `10.1093/mnras/stx805`; Furlanetto & Stoever 2010, `Secondary ionization and heating by fast electrons`; Sazonov & Sunyaev 2015, `Preheating of the Universe by cosmic rays from primordial supernovae`. Their CR spectra/heat fractions are NOT imposed as source data.

**Admission:** source-native numerically checked CR materiality frontier, not CR-ON physics admitted. REI central 28/88 (+0), working 33/88 (+0), Fast 4/7 (+0), BASS-CR 0/3 (+0). RUX11 materiality/error budget and RUX13 named source identity absent; original V1 production tick160. Original source/main/REI owner/CR=OFF left unchanged, no merge, force push or CR-ON. **STOP** further optional atomic/CX/cooling/opacity tables and artificial CR scenarios; next real owner task is source-equal RUX11/RUX13 or REI F05 validated continuum/history.
