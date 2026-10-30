# BASS-CR PHYS11 | source-kinematic upper capacity of H I secondary ionization

**Result type:** derived + numerically checked + implementation verified, under source-frame cold-target energy-only necessary conditions. Not a measured secondary count and not full radiative transport. Main proof and scope: `THEORY_KO.md`.

## Original source, no splice

Immutable PR135 SOURCE ZIP SHA `faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033` (6,736,766 bytes) includes original PHYS09 SOURCE and earlier original H/He owner. No BASS/REI state was imported. Original Emax H 23.6eV, He 34.59eV; original H threshold 13.60eV, He threshold 24.59eV. Maximum e after first absorption 20.99eV.

The original 3200 He-origin photon energy atoms have **2389** energies E>=27.20 eV. Only this set, **first absorbed by H I**, can make an energetic H I secondary ionization. A second secondary H or any secondary He is not supported. Direct He double photon event has E<79.0078eV. These are conditional zero statements for one unaccelerated source primary, no external energy or thermal target boost, not universal He collision claims.

## Actual computed 1e10-second results

| birth witness | first photoionizations m^-3 | secondary H event capacity upper m^-3 | capacity/first | max secondary H binding J m^-3 |
|:---|---:|---:|---:|---:|
| earliest | 1.719391366604854e-26 | 1.288631258608997e-28 | 0.007494694248427891 | 2.807876253644071e-46 |
| midpoint | 1.1927886964448523e-26 | 8.829465000830514e-29 | 0.007402371457029261 | 1.9239053020469957e-46 |
| latest | 6.53655992483617e-27 | 4.747213123182091e-29 | 0.007262555805760585 | 1.0343988561909493e-46 |

Total initial electron kinetic energy earliest 6.236750696526702e-45 J m^-3, eligible subset 3.304397844783822e-46 J m^-3, and under a **counterfactual all-eligible-ionize-H** budget: 2.807876253644071e-46 J m^-3 binding + 4.965215911397516e-47 J m^-3 remaining kinetic. This is not a predicted gas heating or deposition amount. The equality is an energy bookkeeping identity only.

## Numerical data and verification

- 12,800 support-per-original-energy-and-target rows; 108 time-channel; 27 total; 1,728 linear causal window response; 184 energy-bin rows; total 14,847 rows.
- `python -m unittest -v test_phys11` 16/16 PASS, `python -O -m unittest -v test_phys11` 16/16 PASS, negative byte SHA rejection PASS.
- Adversarial same-model separate algorithm `blind_style_audit.py`: direct P_H event integration at original hazard and independent positive/negative finite density-log window perturbation; first counts match exactly, nontrivial causal relative errors `1.6475e-9` and `1.6614e-9`, max `1.6614e-9`.
- Source original first-event count all 108/108 time/channel records agrees with PHYS10 output to required precision. Energy ledger `Q_eligible = B_cap + Q_leftover_if_all_cap_realized` holds near double precision.
- Wolfram independent symbolic/numerical inequality confirms `epsilon_max=20.99eV<24.59eV`, `<2×13.60eV`, source max 34.59eV `<24.59+54.4177655282eV`.

## Referee findings and HOLD

- Actual physical kernel `K` needs electron-impact energy-dependent differential H ionization cross sections and proper electron path distribution with stopping, medium and clock. The upper-capacity number does not estimate occurrence probability.
- Current source 100K gas is frozen; strict zeros require neglect of external work and energetic target thermal tails in the initial-event budget. Cosmic rays, extra hard photons, He+ and heating/non-ionizing excitations lie outside the scope.
- No exact source-owner shared evolving H/He neutral history, radiation bath, cosmological directional geometry; no full chemistry/observable, no cosmological τ or heat.
- R06/C09 distinct author NOT_RUN; native subagent NOT_RUN. Scoped aux 1/1 conditional HOLD; Central DAG 28/88 +0, Extension 0/3 +0.
- Parent PR133 (11/43), PR134 and PR135 are immutable; no merge/force-push, do not repair historic host Git safety barrier by circumvention.

Primary source/provenance bibliography: `LITERATURE.md`.
