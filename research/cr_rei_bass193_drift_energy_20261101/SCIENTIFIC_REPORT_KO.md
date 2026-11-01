# BASS-CR → REI Bianchi IGM | BASS193 drift-energy budget, 2026-11-01

## Exact source and numeric result
Original IGM owner: `cosmosapjw-quantum/rei_bianchi` PR311 (193 BASS epochs, 192 proper intervals); full private source ZIP SHA256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52` is PREVIOUSLY REPORTED ONLY, not reopened in this run. Public verified parent: `bass_cr` PR155 original source-conditioned derived CSV, sha256 `f47f1379503dba93f1583a8cb2b2cdb61fa856f9e0e485140d62fce329600f03`, Git blob `62290340fd338e1105e44739823d2ff267377f52`; unchanged predecessor PR156 SHA `e60089662d88b49cb107b87c6ce7c18489f56a2e`.

Selected small drift `epsilon=|u_i-u_H|/a=0.1` with `a^2=2 k_B T/mu`. Local source snapshots only, fixed densities T and no external driving. 192 newly generated source-snapshot energy records, NOT 192 independent astrophysical realizations, no time-evolved Bianchi source.

**Measured from input source**:
- max conditional H-only `DeltaTmax/T = 0.003320163267191843` = 0.3320163%, at interval 66, `z_low=9.64915850365812`.
- peak source `T=112.0515169647264 K`, `x_HII=0.4686409762107297`, `DeltaTmax = 0.37202933065940824 K`, `energy capacity=4.808851088377388e-05 eV/H`.
- median source `DeltaTmax/T = 1.433351150776421e-06`, min `2.9431143293311135e-08`; 162/192 ratios are below `1e-4`.
- exact unequal-mass algebraic overall maximum for `epsilon=0.1`: `0.0033333333984776692`, nearly equal-mass `epsilon²/3=0.0033333333333333335`.
- A7 3–200 km/s **model-conditional** local frozen-source `nu_rel * dt` ranges from `37.94446998006225` to `312.3760520429921`. Each separately initialized bin gives `1-exp(-2 nu dt)>=0.99` in this limited model. This is neither measured REI tilt nor self-consistent thermal evolution, nor an additive 192-bin heat history.

The energy ceiling is independent of angular cross sections, whereas the *time-scale* column depends on the published Titova et al. (2025) A7 fit, which has known fit discontinuity and source-support limitations. DO NOT interpret conditional near-complete damping as a confirmed real IGM thermal rise. No full 2016 CX DCS, 2023 elastic DCS or cold-proton spin-symmetrized joint kinetic operator has been acquired; official UGA direct retrieval timed out. No new exact input beyond prior paper source data; no invented angular DCS.

## Equations and physical dimensions
`rho_red=(rho_i rho_H)/(rho_i+rho_H)`; `Edr=0.5 rho_red U²`; `E_H=1.5(n_i+n_H)k_B T`; `DeltaTmax/T=Edr/E_H`; `Edr/nH_total` is provided in eV/H. With `U=epsilon a`, `DeltaTmax/T=(2/3)(mi+mn)ni nn/[(mi ni+mn nn)(ni+nn)]epsilon²`. Equal masses give `(4/3)x(1-x)epsilon² <= epsilon²/3`. Units: energy density erg/cm³, temperatures Kelvin, energies eV per hydrogen nucleus, proper time seconds. Source `T_saved_K` is one temperature snapshot for both species, not two independently evolved temperatures.

For *separately initialized constant-coefficient collision-only* bin, use `dU/dt=-nu_rel U` and `Edr(t)=Edr(0) exp(-2nu_rel dt)` with `nu_rel=gamma(1/rho_i+1/rho_H)`; the conversion fraction is `-expm1(-2 nu_rel dt)`. This does not model Hubble drag, Bianchi shear, ionization mass loading, external forcing, or continuous source evolution. H-only heat-capacity ceiling is an upper ceiling if other species share the heat, but is NOT a global IGM heating bound under sustained drift generation.

## Executed validation and hostile review
- `python3 -m unittest -v test_reservoir`: 16/16 PASS, normal (Python 3.12.3); `python3 -O -m unittest -v test_reservoir`: 16/16 PASS.
- Source 192 rows validated by the byte-locked SHA256, ordered clock, positive units, `nHII/(nHII+nHI) = x_HII_end`, parent gamma/nurel identities, tampering rejection; byte-identical output in two clean temporary runs.
- Independently re-evaluated all 192 algebraic capacity values in Decimal precision=55 directly from original public CSV (without importing reservoir.py): largest absolute Decimal vs CSV float difference `1.4890918747408599e-18`, max at interval 66.
- Wolfram CAS simplifies the arbitrary-mass formula, equal-mass `(4/3)x(1-x)epsilon²`, and the `epsilon²/3` maximum.
- Same-author adversarial audit: source is a **single frozen astrophysical trajectory**, so multiplying independent per-bin energy capacity values cannot establish a time-integrated REI history. Susceptibility to external Bianchi shear and ionization-driven velocity injection is UNRESOLVED; no probability or CMB optical depth is predicted. Root prior fit A7 has known discontinuity and low-speed support gap. None of these are silently repaired or certified.

## Research result, DAG and drift watchdog
Direct physical result: strong collision-only damping can coexist with a low available drift-heating energy reservoir. This screens misleading inference from earlier PR155 `nu/H_eff` alone and provides a hydrogen-energy budget interface for REI owner review, **not a new REI thermal source**.
REI canonical 28/88 REPORTED (delta0); REI working 33/88 REPORTED (delta0); BASS-CR extension 0/3 (delta0). Production HOLD, CR-OFF baseline unaffected, no merge, force push or REI mutation. Real central next work remains REI F05 original source-owned [160,161], RUX02/RUX03, not another optional A7/fit/192-row extension. Repeated optional projects risk drift; this unit is final bounded energy-budget triage pending true source/tilt acquisition. No immediate follow-on optional PR from this calculation.

Source literature: Schultz et al., J. Phys. B 49 084004 (2016), https://doi.org/10.1088/0953-4075/49/8/084004; Glassgold, Krstic & Schultz, ApJ 621 808 (2005), https://doi.org/10.1086/427686; UGA data portal https://sites.physast.uga.edu/amdbs/elastic/index-h%2B%2Bh-2023.html . CR transport rates are not adopted directly from these publications without original full tables.
