# Prospective implementation output schema

Unit `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`. Authoring is not execution approval.
All command-line programs require a frozen C4 budget through `run_bounded.py`.
The runner owns unique run directories and writes immutable CPU receipts.

## Preparation

`prepare.py --out runs/prepare_v1` reads the exact retained PR109 JSON at the
repo-relative path in `inputs/INPUT_MANIFEST.json`, validates the single
`direct_0p1_10` record, and hashes both retained Verner provider files without
importing either. It writes `PREPARED.npz` and `PREPARATION.json` create-only.
The NPZ is the changed coefficient input for production, not a recovered old G.
The JSON includes original payload/source identities, subset raw-byte hashes,
literal constants/density recipes and represented float.hex values, coefficient
hashes, uniformization rate, and a finite maximum Poisson cutoff. No source
coefficient is renormalized.

## Production arrays

`primary.py --prepared runs/prepare_v1 --out runs/primary_v1` writes
`ARRAYS.npz` and `RESULT.json`. Every numeric array is float64 unless explicitly
noted. Prefix order is T/4,T/2,3T/4,T; bin order is [0,T/4],(T/4,T/2],
(T/2,3T/4],(3T/4,T]. Native birth support remains [.1,10] eV throughout.

| NPZ key | Shape | Meaning |
|---|---|---|
| E_eV | (3200,) | Exact saved active energies |
| A_m3_s2 | (3200,) | Exact saved ramp source coefficients |
| b_eV_s | (3200,) | New fixed-2022 Coulomb stopping coefficients |
| drift_s_inv | (3200,) | b divided by the saved current-to-previous energy gap |
| lambda_H_s_inv, lambda_He_s_inv | (3200,) each | Competing ground RR hazards |
| times_s | (4,) | Known-history observation endpoints |
| n_prefix_m3 | (4,3200) | Active cohort number-density states |
| O_prefix_m3_s | (4,3200) | Actual integrals of those states from0 to endpoint |
| O_bins_m3_s | (4,3200) | Actual occupancy in each observation bin |
| capture_H_prefix_m3, capture_He_prefix_m3 | (4,3200) each | lambda times prefix occupancy |
| capture_H_bins_m3, capture_He_bins_m3 | (4,3200) each | lambda times bin occupancy |
| photon_H_energy_eV, photon_He_energy_eV | (3200,) each | Current capture energy plus the channel threshold |
| endpoint_H_rate_m3_s, endpoint_He_rate_m3_s | (4,3200) each | lambda times endpoint active state |

The direct-cutoff source coefficient is recorded in PREPARATION and RESULT;
it is never silently appended as an active state.

## Summary rows

RESULT contains `schema`, `unit`, `input`, `coefficient_identity`, `constants`,
`inventory`, `context`, `prefixes`, `observation_bins`, `tails`,
`numerical_acceptance`, `artifacts` and explicit physical scope limitations.
`prefixes` and `observation_bins` each contain four rows with:

- `interval_s`, `injected_number_m3`, `injected_energy_eV_m3`;
- `active_number_m3`, `active_energy_eV_m3` for cumulative prefixes, and
  `active_number_change_m3`, `active_energy_change_eV_m3` for bins;
- `occupancy_total_m3_s`, `cutoff_direct_number_m3`,
  `cutoff_drift_number_m3`, `cutoff_number_m3`, `cutoff_energy_eV_m3`,
  `coulomb_energy_eV_m3`;
- `channels.H` and `channels.He`, each with `capture_number_m3`,
  `capture_kinetic_eV_m3`, `retained_photon_number_m3`,
  `retained_photon_energy_eV_m3`, `binding_energy_change_eV_m3`, and prefix-only
  `endpoint_rate_m3_s` / `endpoint_kinetic_rate_eV_m3_s`;
- `rr_native25` as a25-entry integrated event vector; `full_source_native25`
  is null, and `physical_heating_completed` is false;
- count/kinetic/total energy residuals normalized by that row's input;
- disjoint-bin `return_claims`, while cumulative prefixes are nonadditive
  diagnostics and do not claim events.

All extensive worldtube totals are null because proper volume is absent.
Retained photons form a separate discrete port whose per-atom bin count is in
ARRAYS; no arbitrary photon spectrum or continuous time history is inferred.
The endpoint at T is the known-history left limit.

## Independent reader agreement

The independently authored reference reads the original source JSON and literal
provider constants directly. It does not import production model, solver or
port functions. It may use the exact arrays above for comparison after building
its own coefficients. Channel capture, kinetic and retained photon totals are
compared at relative1e-9. State/occupancy, source identity and represented-law
coefficient checks are separate from those rare-event comparisons. The exact
finite operator comparison does not certify continuous-energy physical error.
